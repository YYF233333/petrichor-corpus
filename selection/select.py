"""Select survey corpus v2: about 200 Godot 4 repositories, by the rule in selection.md.

    python -I selection/select.py

(-I keeps this file from shadowing the standard `select` module.) Every GitHub response is cached under
selection/cache/, so a rerun reproduces the same selection offline once selection/labels.tsv is complete.
Delete selection/cache/ to select again from the live GitHub state (HEADs move).
Needs `gh auth login` when cache is cold; uses only read-only GitHub API calls. Python 3.11 stdlib only.
Writes corpus/v2.json and selection/candidates.tsv, and prints the statistics for selection/selection.md.
"""
import argparse
import collections
import concurrent.futures as cf
import csv
import datetime
import fnmatch
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "cache")
V1_PATH = os.path.join(ROOT, "corpus", "v1.json")
V2_PATH = os.path.join(ROOT, "corpus", "v2.json")
LABELS_PATH = os.path.join(HERE, "labels.tsv")
CANDIDATES_PATH = os.path.join(HERE, "candidates.tsv")

# ---------------------------------------------------------------------------------------------
# The rule

STAR_SLICES = [(1000, None), (300, 999), (150, 299), (80, 149), (50, 79), (35, 49), (25, 29), (20, 24)]
BYTES_PER_LINE = 34.4  # first-party .gd bytes per line, measured on corpus v1 (10,020,320 B / 291,043 lines)
MIN_STARS = 20
MIN_LINES = 100
DUP_SHARE = 0.5  # dropped when this share of its first-party .gd bytes is byte-identical to a higher-ranked kept repo
TOTAL_TARGET = 200
GAME_MIN_SHARE = 0.60
HUMAN_MIN_SHARE = 0.50
LINE_CAP = 20000
LINE_CAP_SEED = 20261115

# Non-game groups get star-ranked within their remaining slots; these caps only apply if needed
# (we inspect the pool first; see pick_200).
KNOWN_TEST_ADDONS = {"gdunit4", "gut", "wat"}

with open(V1_PATH, encoding="utf-8") as _fh:
    V1_DATA = json.load(_fh)


def gh_full_from_url(url):
    return url.rstrip("/").removesuffix(".git").split("github.com/", 1)[1]


V1_REPOS = [
    {
        "v1_name": r["name"],
        "full": gh_full_from_url(r["url"]),
        "url": r["url"],
        "commit": r["commit"],
        "group": "demo" if r["group"] == "demos" else r["group"],
        "weight": "reference" if r["name"] == "Ring" else "normal",
    }
    for r in V1_DATA["repos"]
]

# ---------------------------------------------------------------------------------------------
# GitHub access with a response cache

_token = None
_lock = threading.Lock()


def token():
    global _token
    with _lock:
        if _token is None:
            _token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    return _token


def http(method, url, body=None):
    for attempt in range(8):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bearer " + token())
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "corpus-select")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                ra = e.headers.get("retry-after")
                rem = e.headers.get("x-ratelimit-remaining")
                reset = e.headers.get("x-ratelimit-reset")
                wait = int(ra) if ra else (int(reset) - time.time() + 3 if rem == "0" and reset else 60)
                print(f"  rate limited ({e.code}), waiting {int(wait)} s", flush=True)
                time.sleep(max(5, min(wait, 1800)))
                continue
            if e.code in (404, 409, 410, 451):
                return {"_error": e.code}
            if e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  {e}, retrying", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up on {url}")


def cached(kind, key, fn):
    p = os.path.join(CACHE, kind, hashlib.sha1(key.encode()).hexdigest()[:24] + ".json.gz")
    if os.path.exists(p):
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    v = fn()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p + ".tmp", "wt", encoding="utf-8") as fh:
        json.dump(v, fh)
    os.replace(p + ".tmp", p)
    return v


def graphql(query):
    r = http("POST", "https://api.github.com/graphql", {"query": query})
    if not r.get("data"):
        raise RuntimeError(json.dumps(r)[:500])
    return r["data"]


def pmap(fn, xs, workers=8):
    with cf.ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, xs))


# ---------------------------------------------------------------------------------------------
# Candidates: search, repository metadata, trees, blobs, authorship evidence


def _search_slice(s_lo, s_hi, d_lo=None, d_hi=None, found=None):
    if found is None:
        found = {}
    sq = f"stars:{s_lo}..{s_hi}" if s_hi else f"stars:>={s_lo}"
    dq = f" created:{d_lo}..{d_hi}" if d_lo and d_hi else ""
    q = f"language:GDScript fork:false {sq}{dq}"
    url1 = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": 100, "page": 1}
    )
    r1 = cached("search", url1, lambda u=url1: (time.sleep(2.2), http("GET", u))[1])
    tc = r1["total_count"]
    if tc > 950 or r1.get("incomplete_results"):
        if d_lo is None:
            _search_slice(s_lo, s_hi, "2014-01-01", "2026-11-16", found)
            return found
        t0 = datetime.date.fromisoformat(d_lo)
        t1 = datetime.date.fromisoformat(d_hi)
        if t0 < t1:
            mid = t0 + datetime.timedelta(days=(t1 - t0).days // 2)
            _search_slice(s_lo, s_hi, d_lo, mid.isoformat(), found)
            _search_slice(s_lo, s_hi, (mid + datetime.timedelta(days=1)).isoformat(), d_hi, found)
            return found
        if s_hi is not None and s_lo < s_hi:
            smid = (s_lo + s_hi) // 2
            _search_slice(s_lo, smid, d_lo, d_hi, found)
            _search_slice(smid + 1, s_hi, d_lo, d_hi, found)
            return found
        raise RuntimeError(f"cannot split {q}: {tc}")
    for it in r1["items"]:
        found.setdefault(it["full_name"].lower(), it["full_name"])
    page = 2
    while (page - 1) * 100 < tc and page <= 10:
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {"q": q, "sort": "stars", "order": "desc", "per_page": 100, "page": page}
        )
        r = cached("search", url, lambda u=url: (time.sleep(2.2), http("GET", u))[1])
        for it in r["items"]:
            found.setdefault(it["full_name"].lower(), it["full_name"])
        if len(r["items"]) < 100:
            break
        page += 1
    return found


def search():
    found = {}
    for lo, hi in STAR_SLICES:
        _search_slice(lo, hi, found=found)
    return found


META = """nameWithOwner url isFork isArchived isTemplate isMirror stargazerCount pushedAt createdAt description
repositoryTopics(first: 30) { nodes { topic { name } } }
templateRepository { nameWithOwner } parent { nameWithOwner } licenseInfo { spdxId }
owner { login ... on User { name } ... on Organization { name } }
defaultBranchRef { name target { ... on Commit { oid tree { oid } } } }"""


def metadata(names):
    names = sorted(names, key=str.lower)
    out = {}
    batches = [names[i:i + 40] for i in range(0, len(names), 40)]

    def one(batch):
        parts = []
        for i, n in enumerate(batch):
            o, r = n.split("/")
            parts.append(f'r{i}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) {{ {META} }}')
        q = "query { " + "\n".join(parts) + " }"
        return batch, cached("meta", q, lambda q=q: graphql(q))

    for batch, data in pmap(one, batches, 4):
        for i, n in enumerate(batch):
            out[n.lower()] = data.get(f"r{i}")
    return out


def v1_tree_oids(items):
    """Map v1 repo nameWithOwner -> tree oid at its pinned v1 commit."""
    out = {}
    parts = []
    for i, (full, sha) in enumerate(items):
        o, r = full.split("/")
        parts.append(f'r{i}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) {{ object(oid: {json.dumps(sha)}) {{ ... on Commit {{ oid tree {{ oid }} }} }} }}')
    q = "query { " + "\n".join(parts) + " }"
    data = cached("v1tree", q, lambda q=q: graphql(q))
    for i, (full, _sha) in enumerate(items):
        obj = (data.get(f"r{i}") or {}).get("object") or {}
        out[full.lower()] = (obj.get("tree") or {}).get("oid")
    return out


KEEP_EXT = (".gd", ".tscn", ".scn", ".cs", "/project.godot", "/plugin.cfg")


def keep(path):
    return ("/" + path).endswith(KEEP_EXT)


def tree(full, sha):
    def fetch(sha, prefix):
        r = http("GET", f"https://api.github.com/repos/{full}/git/trees/{sha}?recursive=1")
        if "_error" in r:
            return None
        if not r["truncated"]:
            return [[prefix + e["path"], e["size"], e["sha"]] for e in r["tree"] if e["type"] == "blob" and keep(e["path"])]
        r = http("GET", f"https://api.github.com/repos/{full}/git/trees/{sha}")
        out = []
        for e in r["tree"]:
            if e["type"] == "blob" and keep(e["path"]):
                out.append([prefix + e["path"], e["size"], e["sha"]])
            elif e["type"] == "tree":
                out += fetch(e["sha"], prefix + e["path"] + "/") or []
        return out

    return cached("tree", f"{full}@{sha}", lambda: {"entries": fetch(sha, "")})["entries"]


def blobs(wanted):
    """{blob sha: text} for (repo full name, blob sha) pairs; cached by sha (content-addressed)."""
    texts, todo = {}, []
    for full, sha in sorted(set(wanted)):
        p = os.path.join(CACHE, "blob", sha + ".json.gz")
        if sha in texts:
            continue
        if os.path.exists(p):
            with gzip.open(p, "rt", encoding="utf-8") as fh:
                texts[sha] = json.load(fh)
        else:
            todo.append((full, sha))
    seen = set()
    todo = [x for x in todo if not (x[1] in seen or seen.add(x[1]))]
    batches = [todo[i:i + 80] for i in range(0, len(todo), 80)]

    def one(batch):
        by_repo = collections.defaultdict(list)
        for full, sha in batch:
            by_repo[full].append(sha)
        parts = []
        for i, (full, shas) in enumerate(by_repo.items()):
            o, r = full.split("/")
            objs = " ".join(f'b{sha}: object(oid: "{sha}") {{ ... on Blob {{ text }} }}' for sha in shas)
            parts.append(f'r{i}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) {{ {objs} }}')
        data = graphql("query { " + "\n".join(parts) + " }")
        res = {}
        for i, (full, shas) in enumerate(by_repo.items()):
            node = data.get(f"r{i}") or {}
            for sha in shas:
                res[sha] = (node.get("b" + sha) or {}).get("text")
        for sha, t in res.items():
            p = os.path.join(CACHE, "blob", sha + ".json.gz")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with gzip.open(p + ".tmp", "wt", encoding="utf-8") as fh:
                json.dump(t, fh)
            os.replace(p + ".tmp", p)
        return res

    for res in pmap(one, batches, 4):
        texts.update(res)
    return texts


AGENT_TRAILER_RE = re.compile(
    r"^\s*Co-Authored-By:\s*(.+)$", re.I | re.M
)
AGENT_SIG_RE = re.compile(
    r"\b(claude|anthropic|copilot|cursor|codex|openai|gemini|devin|windsurf|aider|cline|roo|sweep|amazon\s*q|qodo|junie|opencode|antigravity|noreply@anthropic\.com)\b",
    re.I,
)


def fetch_evidence(items):
    """Fetch authorship evidence and README for [(full, commit_sha)] pairs; cached per repo@sha."""
    out = {}
    todo = []
    for full, sha in items:
        key = f"{full}@{sha}"
        p = os.path.join(CACHE, "evidence", hashlib.sha1(key.encode()).hexdigest()[:24] + ".json.gz")
        if os.path.exists(p):
            with gzip.open(p, "rt", encoding="utf-8") as fh:
                out[full.lower()] = json.load(fh)
        else:
            todo.append((full, sha))

    batches = [todo[i:i + 15] for i in range(0, len(todo), 15)]

    def one(batch):
        parts = []
        for i, (full, sha) in enumerate(batch):
            o, r = full.split("/")
            parts.append(
                f'r{i}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) {{ '
                f'c: object(oid: {json.dumps(sha)}) {{ ... on Commit {{ '
                f'h: history(first: 100) {{ totalCount nodes {{ committedDate message }} }} '
                f'pre: history(until: "2025-01-01T00:00:00Z") {{ totalCount }} }} }} '
                f'root: object(expression: {json.dumps(sha + ":")}) {{ ... on Tree {{ entries {{ name type }} }} }} '
                f'cursor: object(expression: {json.dumps(sha + ":.cursor")}) {{ ... on Tree {{ entries {{ name }} }} }} '
                f'copilot: object(expression: {json.dumps(sha + ":.github/copilot-instructions.md")}) {{ ... on Blob {{ byteSize }} }} '
                f'readme: object(expression: {json.dumps(sha + ":README.md")}) {{ ... on Blob {{ text }} }} '
                f'}}'
            )
        data = graphql("query { " + "\n".join(parts) + " }")
        # Check if any repo has a non-"README.md" readme in root entries
        alt_readmes = []
        parsed = {}
        for i, (full, sha) in enumerate(batch):
            node = data.get(f"r{i}") or {}
            c = node.get("c") or {}
            h = c.get("h") or {}
            nodes = h.get("nodes") or []
            total_commits = h.get("totalCount") or 0
            pre2025 = (c.get("pre") or {}).get("totalCount") or 0
            weeks = set()
            co_agents = []
            for cm in nodes:
                dt = (cm.get("committedDate") or "")[:10]
                if dt:
                    iso = datetime.date.fromisoformat(dt).isocalendar()
                    weeks.add((iso.year, iso.week))
                msg = cm.get("message") or ""
                for m in AGENT_TRAILER_RE.finditer(msg):
                    who = m.group(1).strip()
                    if AGENT_SIG_RE.search(who):
                        co_agents.append(who)
            root_entries = (node.get("root") or {}).get("entries") or []
            root_names = {e["name"].lower(): e["name"] for e in root_entries}
            agent_files = []
            for af in ("claude.md", "agents.md", "gemini.md", ".cursorrules", ".windsurfrules"):
                if af in root_names:
                    agent_files.append(root_names[af])
            if (node.get("cursor") or {}).get("entries"):
                agent_files.append(".cursor/")
            if node.get("copilot"):
                agent_files.append(".github/copilot-instructions.md")
            readme_text = (node.get("readme") or {}).get("text")
            if readme_text is None:
                alt = next(
                    (e["name"] for e in root_entries if e["type"] == "blob" and re.match(r"^readme(\.|$)", e["name"], re.I) and e["name"] != "README.md"),
                    None,
                )
                if alt:
                    alt_readmes.append((full, sha, alt))
            parsed[full] = {
                "total_commits": total_commits,
                "pre2025_commits": pre2025,
                "pre2025_share": round(pre2025 / total_commits, 3) if total_commits else 0.0,
                "latest_count": len(nodes),
                "active_weeks": len(weeks),
                "commits_per_active_week": round(len(nodes) / len(weeks), 2) if weeks else 0.0,
                "latest_commit_date": (nodes[0].get("committedDate") or "")[:10] if nodes else "",
                "earliest_100_date": (nodes[-1].get("committedDate") or "")[:10] if nodes else "",
                "agent_files": agent_files,
                "co_authored_count": len(co_agents),
                "co_authored_sample": sorted(set(co_agents))[:5],
                "readme": readme_text or "",
            }
        if alt_readmes:
            aparts = []
            for j, (full, sha, alt) in enumerate(alt_readmes):
                o, r = full.split("/")
                aparts.append(f'a{j}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) {{ rm: object(expression: {json.dumps(sha + ":" + alt)}) {{ ... on Blob {{ text }} }} }}')
            adata = graphql("query { " + "\n".join(aparts) + " }")
            for j, (full, _sha, _alt) in enumerate(alt_readmes):
                t = ((adata.get(f"a{j}") or {}).get("rm") or {}).get("text")
                if t:
                    parsed[full]["readme"] = t
        for full, sha in batch:
            key = f"{full}@{sha}"
            p = os.path.join(CACHE, "evidence", hashlib.sha1(key.encode()).hexdigest()[:24] + ".json.gz")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with gzip.open(p + ".tmp", "wt", encoding="utf-8") as fh:
                json.dump(parsed[full], fh)
            os.replace(p + ".tmp", p)
        return parsed

    for res in pmap(one, batches, 4):
        for full, ev in res.items():
            out[full.lower()] = ev
    return out


# ---------------------------------------------------------------------------------------------
# Analysis of one repository


def strip_gd_comments_strings(src):
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "#":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if c in ('"', "'"):
            q = src[i:i + 3] if src[i:i + 3] in ('"""', "'''") else c
            i += len(q)
            out.append('""')
            while i < n:
                if src[i] == "\\" and len(q) == 1:
                    i += 2
                    continue
                if src[i:i + len(q)] == q:
                    i += len(q)
                    break
                if src[i] == "\n" and len(q) == 1:
                    break
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


GD3_RE = re.compile(
    r"(?m)(?:^\s*(?:onready\s+var|export(?:\s*\([^)]*\))?\s+var|(?:remote|master|puppet|remotesync|mastersync|puppetsync)\s+(?:func|var))\b|^\s*tool\s*$|(?<!\.)\byield\s*\()"
)
GD4_RE = re.compile(
    r"(?:@(?:export(?:_\w+)?|onready|tool|rpc|icon|warning_ignore|static_unload)\b|\bawait\b|\bsuper\s*\(|\bsuper\.\w+)"
)


def check_gd4_syntax(gd_texts):
    """Return (has_gd4, has_gd3) over stripped GDScript sources."""
    has4, has3 = False, False
    for t in gd_texts:
        if not t:
            continue
        s = strip_gd_comments_strings(t)
        if GD3_RE.search(s):
            has3 = True
        if GD4_RE.search(s):
            has4 = True
    return has4, has3


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


CONFIG_RE = re.compile(r"^\s*config_version\s*=\s*(\d+)", re.M)
TEST_RE = re.compile(r"(?:^|/)(?:tests?|testing|unit|specs?|test_project)/|(?:^|/)test_[^/]*\.gd$|_tests?\.gd$", re.I)
AUTHOR_RE = re.compile(r'^\s*author\s*=\s*"([^"]*)"', re.M)
PLUGIN_CFG_RE = re.compile(r"(?:^|/)addons/[^/]+/plugin\.cfg$|^plugin\.cfg$")


def is_excluded(path, excludes):
    for pat in excludes:
        pat = pat.strip()
        if not pat:
            continue
        if pat.endswith("/") and (path.startswith(pat) or ("/" + pat) in ("/" + path)):
            return True
        if fnmatch.fnmatch(path, pat) or path == pat:
            return True
    return False


def first_party_addons(m, entries, texts, has_pg=True):
    """addons/<name>/ directories written by the repository's owner."""
    repo, login = norm(m["nameWithOwner"].split("/")[1]), norm(m["owner"]["login"])
    oname = norm(m["owner"].get("name"))
    stripped = re.sub(r"^(godot|gd)|(godot|gd|plugin|addon)?4?$", "", repo) or repo
    names, cfg_names, authors = set(), set(), {}
    for path, size, sha in entries:
        mm = re.search(r"(?:^|/)addons/([^/]+)/", path)
        if mm:
            names.add(mm.group(1))
            if re.search(r"(?:^|/)addons/[^/]+/plugin\.cfg$", path):
                cfg_names.add(mm.group(1))
                a = AUTHOR_RE.search(texts.get(sha) or "")
                if a:
                    authors.setdefault(mm.group(1), set()).add(norm(a.group(1)))
    fp = set()
    for n in names:
        a = norm(n)
        by_name = (len(a) >= 3 and (a == repo or a == stripped)) or (
            len(a) >= 4 and (a in repo or stripped in a or (len(login) >= 4 and login in a))
        )
        by_author = any(x and ((len(login) >= 3 and login in x) or (len(oname) >= 4 and (oname in x or x in oname))) for x in authors.get(n, ()))
        if by_name or by_author:
            fp.add(n)
    if not has_pg and not fp and cfg_names:
        fp = {n for n in cfg_names if norm(n) not in KNOWN_TEST_ADDONS}
    return fp


def analyze(m, entries, texts, excludes=()):
    roots = {}
    for path, size, sha in entries:
        if path == "project.godot" or path.endswith("/project.godot"):
            mm = CONFIG_RE.search(texts.get(sha) or "")
            roots[os.path.dirname(path)] = int(mm.group(1)) if mm else 0
    has_pg = bool(roots)
    v5 = sorted(r for r, v in roots.items() if v == 5)
    fp_addons = first_party_addons(m, entries, texts, has_pg=has_pg)
    ordered = sorted(roots, key=len, reverse=True)
    has_plugin_cfg = any(PLUGIN_CFG_RE.search(p) for p, _, _ in entries)
    a = dict(
        has_pg=has_pg,
        has_plugin_cfg=has_plugin_cfg,
        projects_v5=len(v5),
        projects_other=len(roots) - len(v5),
        fp_addons=sorted(fp_addons),
        gd_files=0,
        gd_bytes=0,
        gd_addon_bytes=0,
        test_bytes=0,
        vendored_bytes=0,
        other_engine_bytes=0,
        excluded_bytes=0,
        scenes=0,
        cs_bytes=0,
        blobs=[],
        fp_gd_paths=[],
    )
    for path, size, sha in entries:
        if any(seg.startswith(".") for seg in path.split("/")[:-1]):
            continue
        root = next((r for r in ordered if r == "" or path.startswith(r + "/")), None)
        if path.endswith((".tscn", ".scn")):
            a["scenes"] += root is not None and roots[root] == 5
            continue
        if path.endswith(".cs"):
            a["cs_bytes"] += size
            continue
        if not path.endswith(".gd"):
            continue
        if root is not None and roots[root] != 5:
            a["other_engine_bytes"] += size
            continue
        sub = path[len(root) + 1:] if root else path
        parts = sub.split("/")
        if "addons" in parts[:-2]:
            name = parts[parts.index("addons") + 1]
            if name not in fp_addons:
                a["vendored_bytes"] += size
                continue
        if excludes and is_excluded(path, excludes):
            a["excluded_bytes"] += size
            continue
        if TEST_RE.search(path):
            a["test_bytes"] += size
        elif "addons" in parts[:-2]:
            a["gd_addon_bytes"] += size
        a["gd_files"] += 1
        a["gd_bytes"] += size
        a["blobs"].append((sha, size))
        a["fp_gd_paths"].append((path, size, sha))
    a["est_lines"] = round(a["gd_bytes"] / BYTES_PER_LINE)
    return a


PLUGIN_RE = re.compile(r"\b(plugin|addon|add-on|library|sdk)\b", re.I)
DEMO_RE = re.compile(r"\b(demos|examples|samples|showcase|snippets|recipes)\b", re.I)
TOOL_RE = re.compile(r"\b(editor|tool|toolkit|app|application|software|utility|launcher|viewer|visuali[sz]er|daw|ide|player)\b", re.I)
GAME_RE = re.compile(r"\bgames?\b", re.I)


def group_of(m, a):
    full = m["nameWithOwner"]
    if not a["has_pg"] and a["has_plugin_cfg"]:
        return "plugin"
    if a["gd_addon_bytes"] and a["gd_addon_bytes"] >= 0.5 * max(1, a["gd_bytes"] - a["test_bytes"]):
        return "plugin"
    text = full.split("/")[1].replace("-", " ").replace("_", " ") + " " + (m.get("description") or "")
    if PLUGIN_RE.search(text):
        return "plugin"
    if a["projects_v5"] >= 3 or DEMO_RE.search(text):
        return "demo"
    if TOOL_RE.search(text) and not GAME_RE.search(text):
        return "tool"
    return "game"


def load_labels():
    labels = {}
    if not os.path.exists(LABELS_PATH):
        return labels
    with open(LABELS_PATH, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            labels[r["name"].lower()] = {
                "name": r["name"],
                "group": r["group"].strip(),
                "complete": r["complete"].strip().lower(),
                "authorship": r["authorship"].strip().lower(),
                "generated": [x.strip() for x in r["generated"].split(";") if x.strip()],
                "reason": r["reason"].strip(),
            }
    return labels


# ---------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-judge", action="store_true", help="Write work/to_judge.jsonl for candidates needing review")
    args = ap.parse_args()

    labels = load_labels()
    found = search()
    for v1 in V1_REPOS:
        found.setdefault(v1["full"].lower(), v1["full"])
    print(f"search: {len(found)} repositories", flush=True)
    meta = metadata(found.values())

    # Resolve v1 repositories by current nameWithOwner
    v1_by_key = {}
    for v1 in V1_REPOS:
        m = meta.get(v1["full"].lower())
        key = m["nameWithOwner"].lower() if m else v1["full"].lower()
        v1_by_key[key] = v1

    v1_trees = v1_tree_oids([(meta[v1["full"].lower()]["nameWithOwner"], v1["commit"]) for v1 in V1_REPOS if meta.get(v1["full"].lower())])

    rows = {}
    for key, name in found.items():
        m = meta.get(key)
        key = m["nameWithOwner"].lower() if m else key
        v1 = v1_by_key.get(key)
        rows[key] = {
            "name": m["nameWithOwner"] if m else name,
            "m": m,
            "v1": v1,
            "commit": v1["commit"] if v1 else (((m or {}).get("defaultBranchRef") or {}).get("target") or {}).get("oid", ""),
            "tree_oid": v1_trees.get(key) if v1 else ((((m or {}).get("defaultBranchRef") or {}).get("target") or {}).get("tree") or {}).get("oid"),
            "drop": None if m else "not found",
        }

    def pre(row):
        m = row["m"]
        if row["drop"] or row["v1"]:
            return
        if m["isFork"] or m["parent"]:
            row["drop"] = "fork"
        elif m["isMirror"]:
            row["drop"] = "mirror"
        elif m["templateRepository"]:
            row["drop"] = "from template " + m["templateRepository"]["nameWithOwner"]
        elif not m["defaultBranchRef"] or not m["defaultBranchRef"]["target"]:
            row["drop"] = "empty"

    for row in rows.values():
        pre(row)
    live = [r for r in rows.values() if not r["drop"]]

    done = [0]

    def get_tree_logged(row):
        row["entries"] = tree(row["m"]["nameWithOwner"], row["tree_oid"]) if row["tree_oid"] else None
        done[0] += 1
        if done[0] % 400 == 0:
            print(f"  trees {done[0]}/{len(live)}", flush=True)

    pmap(get_tree_logged, live, 8)
    print("trees done", flush=True)

    want_cfg = []
    for row in live:
        ents = row["entries"]
        if ents is None:
            row["drop"] = "no tree"
            continue
        has_pg = any(p == "project.godot" or p.endswith("/project.godot") for p, _, _ in ents)
        has_pc = any(PLUGIN_CFG_RE.search(p) for p, _, _ in ents)
        if not has_pg and not has_pc and not row["v1"]:
            row["drop"] = "no project.godot or plugin.cfg"
            continue
        full = row["m"]["nameWithOwner"]
        for p, s, sha in ents:
            if p == "project.godot" or p.endswith("/project.godot") or p.endswith("/plugin.cfg") or p == "plugin.cfg":
                want_cfg.append((full, sha))

    texts = blobs(want_cfg)
    print(f"config blobs: {len(texts)}", flush=True)

    # First pass analyze + identify plugin-only repos needing GDScript syntax check
    plugin_gd_want = []
    for key, row in rows.items():
        if row["drop"]:
            continue
        lab = labels.get(key)
        excludes = lab["generated"] if lab else ()
        row["a"] = a = analyze(row["m"], row["entries"], texts, excludes=excludes)
        row["group"] = lab["group"] if lab else group_of(row["m"], a)
        if row["v1"]:
            continue
        if a["has_pg"]:
            if not a["projects_v5"]:
                row["drop"] = "no Godot 4 project (config_version=5)"
                continue
        else:
            if row["m"]["stargazerCount"] < MIN_STARS:
                row["drop"] = f"under {MIN_STARS} stars"
                continue
            if a["est_lines"] < MIN_LINES:
                row["drop"] = f"under {MIN_LINES} first-party lines"
                continue
            for _p, _s, sha in a["fp_gd_paths"]:
                plugin_gd_want.append((row["m"]["nameWithOwner"], sha))
            continue
        if a["est_lines"] < MIN_LINES:
            row["drop"] = f"under {MIN_LINES} first-party lines"
        elif row["m"]["stargazerCount"] < MIN_STARS:
            row["drop"] = f"under {MIN_STARS} stars"

    if plugin_gd_want:
        gd_texts = blobs(plugin_gd_want)
        print(f"plugin gd blobs: {len(gd_texts)}", flush=True)
        for row in rows.values():
            if row["drop"] or row["v1"] or row["a"]["has_pg"]:
                continue
            srcs = [gd_texts.get(sha) for _p, _s, sha in row["a"]["fp_gd_paths"]]
            has4, has3 = check_gd4_syntax(srcs)
            row["gd4_syntax"] = (has4, has3)
            if has3:
                row["drop"] = "Godot 3 syntax in plugin"
            elif not has4:
                row["drop"] = "no Godot 4 syntax markers in plugin"

    # near-duplicates: walk by stars; drop a repo when DUP_SHARE of its first-party bytes are identical
    # blobs of a repo kept before it (v1 repos are never dropped, though they register their blobs)
    ranked = sorted(
        (r for r in rows.values() if not r["drop"]),
        key=lambda r: (-r["m"]["stargazerCount"], r["m"]["createdAt"]),
    )
    owner_of = collections.defaultdict(list)
    for row in ranked:
        shared = collections.Counter()
        for sha, size in set(map(tuple, row["a"]["blobs"])):
            for other in owner_of.get(sha, ()):
                shared[other] += size
        hit = next((o for o, b in shared.most_common() if row["a"]["gd_bytes"] and b >= DUP_SHARE * row["a"]["gd_bytes"]), None)
        if hit and not row["v1"]:
            row["drop"] = "near-duplicate of " + hit
            continue
        for sha, size in set(map(tuple, row["a"]["blobs"])):
            owner_of[sha].append(row["m"]["nameWithOwner"])

    remaining = [r for r in ranked if not r["drop"]]
    print(f"remaining candidates after rules 1-4: {len(remaining)}", flush=True)

    # Fetch authorship evidence + README for all remaining candidates
    ev = fetch_evidence([(r["m"]["nameWithOwner"], r["commit"]) for r in remaining])
    for r in remaining:
        r["ev"] = ev.get(r["m"]["nameWithOwner"].lower(), {})

    if args.dump_judge:
        dump_for_judging(remaining)
        return

    # Apply labels & completeness
    missing = [r["m"]["nameWithOwner"] for r in remaining if r["m"]["nameWithOwner"].lower() not in labels]
    if missing:
        print(f"WARNING: {len(missing)} remaining candidates missing from labels.tsv (run --dump-judge)", flush=True)
        for r in remaining:
            if r["m"]["nameWithOwner"].lower() not in labels:
                r["drop"] = "unlabelled"
    for r in remaining:
        lab = labels.get(r["m"]["nameWithOwner"].lower())
        if not lab:
            continue
        r["label"] = lab
        r["group"] = lab["group"]
        r["authorship"] = lab["authorship"]
        if lab["complete"] == "no" and not r["v1"]:
            r["drop"] = "incomplete"

    eligible = [r for r in remaining if not r["drop"]]
    pick_200(eligible)
    write(rows, eligible)


def sample_gd_paths(a, k=3):
    """Pick up to k representative non-test first-party .gd paths."""
    paths = [x for x in a["fp_gd_paths"] if not TEST_RE.search(x[0])]
    if not paths:
        paths = list(a["fp_gd_paths"])
    # Prefer medium-sized files (400B..12000B) across distinct dirs
    paths.sort(key=lambda x: (0 if 400 <= x[1] <= 12000 else 1, -min(x[1], 12000), x[0]))
    picked, seen_dirs = [], set()
    for p, s, sha in paths:
        d = os.path.dirname(p)
        if d not in seen_dirs:
            picked.append((p, s, sha))
            seen_dirs.add(d)
            if len(picked) == k:
                return picked
    for p, s, sha in paths:
        if (p, s, sha) not in picked:
            picked.append((p, s, sha))
            if len(picked) == k:
                return picked
    return picked


def dump_for_judging(remaining):
    want = []
    samples = {}
    for r in remaining:
        full = r["m"]["nameWithOwner"]
        pts = sample_gd_paths(r["a"], 3)
        samples[full] = pts
        for _p, _s, sha in pts:
            want.append((full, sha))
    gd_texts = blobs(want)
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    out_path = os.path.join(ROOT, "work", "to_judge.jsonl")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        for r in remaining:
            m, a, ev = r["m"], r["a"], r["ev"]
            full = m["nameWithOwner"]
            rec = {
                "name": full,
                "url": m["url"],
                "v1": r["v1"]["v1_name"] if r["v1"] else "",
                "v1_group": r["v1"]["group"] if r["v1"] else "",
                "stars": m["stargazerCount"],
                "created": m["createdAt"][:10],
                "pushed": m["pushedAt"][:10],
                "license": lic(m),
                "description": m.get("description") or "",
                "heuristic_group": r["group"],
                "has_pg": a["has_pg"],
                "projects_v5": a["projects_v5"],
                "gd_files": a["gd_files"],
                "est_lines": a["est_lines"],
                "test_share": round(a["test_bytes"] / a["gd_bytes"], 2) if a["gd_bytes"] else 0,
                "addon_share": round(a["gd_addon_bytes"] / a["gd_bytes"], 2) if a["gd_bytes"] else 0,
                "scenes": a["scenes"],
                "cs_bytes": a["cs_bytes"],
                "evidence": {k: v for k, v in ev.items() if k != "readme"},
                "readme_excerpt": (ev.get("readme") or "")[:2500],
                "gd_paths_sample": [p for p, _, _ in a["fp_gd_paths"][:40]],
                "gd_samples": [
                    {"path": p, "bytes": s, "text": (gd_texts.get(sha) or "")[:3000]}
                    for p, s, sha in samples[full]
                ],
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(remaining)} candidates to {out_path}", flush=True)


def pick_200(eligible):
    """Select TOTAL_TARGET repos enforcing v1 retention, >=60% games, >=50% human repos and >=50% human capped lines."""
    selected = []
    rest = []
    for r in eligible:
        if r["v1"]:
            r["selected"] = True
            r["weight"] = r["v1"]["weight"]
            selected.append(r)
        else:
            r["weight"] = "normal"
            rest.append(r)

    rest.sort(key=lambda r: (-r["m"]["stargazerCount"], r["m"]["createdAt"]))

    ref_total = sum(r["weight"] == "reference" for r in selected)
    ref_games = sum(r["weight"] == "reference" and r["group"] == "game" for r in selected)
    normal_target = TOTAL_TARGET - ref_total
    min_games = max(
        math_ceil(TOTAL_TARGET * GAME_MIN_SHARE),
        math_ceil(normal_target * GAME_MIN_SHARE) + ref_games,
    )
    games_need = max(0, min_games - sum(r["group"] == "game" for r in selected))
    game_pool = [r for r in rest if r["group"] == "game"]
    other_pool = [r for r in rest if r["group"] != "game"]

    chosen = list(selected)
    for r in game_pool[:games_need]:
        r["selected"] = True
        chosen.append(r)
    rem_pool = sorted(game_pool[games_need:] + other_pool, key=lambda r: (-r["m"]["stargazerCount"], r["m"]["createdAt"]))
    for r in rem_pool:
        if len(chosen) >= TOTAL_TARGET:
            r["drop"] = "over quota"
            continue
        r["selected"] = True
        chosen.append(r)

    # Ensure >=50% human repos and >=50% human capped lines
    def human_ok(ch):
        norm_ch = [x for x in ch if x["weight"] == "normal"]
        for subset in (ch, norm_ch):
            if sum(x.get("authorship") == "human" for x in subset) < HUMAN_MIN_SHARE * len(subset):
                return False
            tot_cap = sum(min(x["a"]["est_lines"], LINE_CAP) for x in subset)
            hum_cap = sum(min(x["a"]["est_lines"], LINE_CAP) for x in subset if x.get("authorship") == "human")
            if hum_cap < HUMAN_MIN_SHARE * tot_cap:
                return False
        return True

    assert human_ok(chosen), "human quota not met; add swap logic if needed"


def math_ceil(x):
    n = int(x)
    return n if x == n else n + 1


def lic(m):
    return (m.get("licenseInfo") or {}).get("spdxId") or "none"


def lic_json(m):
    s = (m.get("licenseInfo") or {}).get("spdxId")
    return None if not s or s == "NOASSERTION" else s


def write(rows, eligible):
    cols = [
        "name", "url", "stars", "pushed", "created", "license", "archived", "is_template", "group",
        "authorship", "complete", "projects_v5", "projects_other", "gd_files", "est_lines", "gd_bytes",
        "test_share", "addon_share", "vendored_bytes", "godot3_bytes", "cs_bytes", "scenes", "commit",
        "v1", "weight", "status", "description",
    ]
    out = []
    for key, row in sorted(rows.items(), key=lambda kv: -((kv[1]["m"] or {}).get("stargazerCount") or 0)):
        m, a = row["m"] or {}, row.get("a") or {}
        lab = row.get("label") or {}
        out.append([
            row["name"], m.get("url", ""), m.get("stargazerCount", ""), (m.get("pushedAt") or "")[:10],
            (m.get("createdAt") or "")[:10], lic(m) if m else "", m.get("isArchived", ""), m.get("isTemplate", ""),
            row.get("group", ""), row.get("authorship", ""), lab.get("complete", ""),
            a.get("projects_v5", ""), a.get("projects_other", ""), a.get("gd_files", ""), a.get("est_lines", ""),
            a.get("gd_bytes", ""), f'{a["test_bytes"] / a["gd_bytes"]:.2f}' if a.get("gd_bytes") else "",
            f'{a["gd_addon_bytes"] / a["gd_bytes"]:.2f}' if a.get("gd_bytes") else "", a.get("vendored_bytes", ""),
            a.get("other_engine_bytes", ""), a.get("cs_bytes", ""), a.get("scenes", ""), row.get("commit", ""),
            "v1" if row["v1"] else "", row.get("weight", ""),
            "selected" if row.get("selected") else "dropped: " + (row["drop"] or "?"),
            re.sub(r"\s+", " ", m.get("description") or "")[:160],
        ])
    with open(CANDIDATES_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in out:
            fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")

    sel = [r for r in rows.values() if r.get("selected")]
    sel.sort(key=lambda r: (["game", "plugin", "tool", "demo"].index(r["group"]), -r["m"]["stargazerCount"], r["m"]["createdAt"]))
    names = collections.Counter(r["m"]["nameWithOwner"].split("/")[-1].lower() for r in sel)
    manifest = {
        "version": 2,
        "line_cap": LINE_CAP,
        "line_cap_seed": LINE_CAP_SEED,
        "sparse": V1_DATA["sparse"],
        "repos": [
            {
                "name": (r["m"]["nameWithOwner"].replace("/", "__")
                         if names[r["m"]["nameWithOwner"].split("/")[-1].lower()] > 1
                         else r["m"]["nameWithOwner"].split("/")[-1]),
                "url": r["m"]["url"] + ".git",
                "commit": r["commit"],
                "group": r["group"],
                "license": lic_json(r["m"]),
                "stars": r["m"]["stargazerCount"],
                "created": r["m"]["createdAt"][:10],
                "authorship": r.get("authorship", ""),
                "weight": r["weight"],
                "exclude": (r.get("label") or {}).get("generated", []),
                "first_party_addons": r["a"]["fp_addons"],
            }
            for r in sel
        ],
    }
    with open(V2_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    stats(rows, sel)


def stats(rows, sel):
    drops = collections.Counter(re.sub(r" (of|from template) .*|\(\d+\)", "", r["drop"]) for r in rows.values() if r["drop"])
    print("\ncandidates", len(rows), "selected", len(sel))
    for k, v in drops.most_common():
        print(f"  {v:5}  {k}")
    judged = [r for r in rows.values() if r.get("label")]
    print(f"\njudged: {len(judged)}, complete=no: {sum(r['label']['complete'] == 'no' for r in judged)}, "
          f"plugin-only (no project.godot): judged={sum(not r['a']['has_pg'] for r in judged)}, "
          f"selected={sum(not r['a']['has_pg'] for r in sel)}")

    for label, sub in [("ALL 200", sel), ("NORMAL 199 (excl. Ring)", [r for r in sel if r["weight"] == "normal"])]:
        total_raw = sum(r["a"]["est_lines"] for r in sub)
        total_cap = sum(min(r["a"]["est_lines"], LINE_CAP) for r in sub)
        print(f"\n=== {label} (n={len(sub)}) === raw={total_raw} capped={total_cap}")
        for g in ["game", "plugin", "tool", "demo"]:
            gs = [r for r in sub if r["group"] == g]
            if gs:
                ls = sorted((r["a"]["est_lines"] for r in gs), reverse=True)
                non_v1 = [r for r in gs if not r["v1"]]
                print(f"  {g:7} {len(gs):4} repos ({len(gs)/len(sub):.1%}) {sum(ls):8} raw {sum(min(x, LINE_CAP) for x in ls):8} capped  "
                      f"min_stars_all={min(r['m']['stargazerCount'] for r in gs)} "
                      f"min_stars_new={min(r['m']['stargazerCount'] for r in non_v1) if non_v1 else '-'}")
        for au in ["human", "mixed", "agent"]:
            aus = [r for r in sub if r.get("authorship") == au]
            r_lines = sum(r["a"]["est_lines"] for r in aus)
            c_lines = sum(min(r["a"]["est_lines"], LINE_CAP) for r in aus)
            print(f"  auth {au:7} {len(aus):4} repos ({len(aus)/len(sub):.1%}) raw={r_lines:8} ({r_lines/total_raw:.1%}) "
                  f"capped={c_lines:8} ({c_lines/total_cap:.1%})")
        capped = sorted(sub, key=lambda r: (-min(r["a"]["est_lines"], LINE_CAP), -r["a"]["est_lines"]))
        top5_cap = sum(min(r["a"]["est_lines"], LINE_CAP) for r in capped[:5])
        print(f"  top 5 capped share: {top5_cap}/{total_cap} = {top5_cap/total_cap:.2%}")
        raw_s = sorted(sub, key=lambda r: -r["a"]["est_lines"])
        top5_raw = sum(r["a"]["est_lines"] for r in raw_s[:5])
        print(f"  top 5 raw share: {top5_raw}/{total_raw} = {top5_raw/total_raw:.2%}")

    print("\nLargest 8 by raw est_lines:")
    total_raw = sum(r["a"]["est_lines"] for r in sel)
    total_cap = sum(min(r["a"]["est_lines"], LINE_CAP) for r in sel)
    for r in sorted(sel, key=lambda r: -r["a"]["est_lines"])[:8]:
        raw = r["a"]["est_lines"]
        cap = min(raw, LINE_CAP)
        print(f"  {r['m']['nameWithOwner']:42} {r['group']:6} {r['authorship']:5} raw={raw:7} ({raw/total_raw:.1%}) cap={cap:6} ({cap/total_cap:.2%})")

    qs = sorted((r["a"]["est_lines"] for r in sel), reverse=True)
    n = len(qs)
    print("\nquantiles (raw lines):", {p: qs[min(n - 1, int(n * (1 - p)))] for p in (0.1, 0.25, 0.5, 0.75, 0.9)})
    lics = collections.Counter(lic(r["m"]) for r in sel)
    print("licenses:", lics.most_common())
    print("license=null (none+NOASSERTION):", sum(lic_json(r["m"]) is None for r in sel))
    print(f"test share of selected raw lines: {sum(r['a']['test_bytes'] for r in sel) / sum(r['a']['gd_bytes'] for r in sel):.1%}")
    print(f"excluded (generated) lines skipped in selected: {sum(r['a']['excluded_bytes'] for r in sel) / BYTES_PER_LINE:.0f}")
    cnt = collections.Counter()
    sizes = {}
    for r in sel:
        for sha, size in set(map(tuple, r["a"]["blobs"])):
            cnt[sha] += 1
            sizes[sha] = size
    dup = sum(sizes[s] * (c - 1) for s, c in cnt.items() if c > 1)
    print(f"bytes in blobs repeated across selected repos: {dup / BYTES_PER_LINE:.0f} lines ({dup / sum(r['a']['gd_bytes'] for r in sel):.2%})")


if __name__ == "__main__":
    main()
