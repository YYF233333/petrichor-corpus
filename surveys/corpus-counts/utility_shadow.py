"""Methods named like a utility function, and direct calls of that name, in first-party GDScript.

Usage: python utility_shadow.py CORPUS_DIR EXTENSION_API_JSON
    CORPUS_DIR: fetched with fetch.py at the repository root (first-party rules and groups from there)
    EXTENSION_API_JSON: thirdparty/godot-cpp/gdextension/extension_api-4-7.json (utility functions, engine classes)

GDScript resolves a direct call `name(...)` to its own or the engine's utility function before any member (Godot
ed1daf0 modules/gdscript/gdscript_analyzer.cpp:3451, 3502; members from 3568). A call counts when a method of that
name is declared by the calling class, a base script, an outer class (static methods only) or an engine base class.
GDScript's own utilities are those of modules/gdscript/gdscript_utility_functions.cpp:570-592.

Token-based (gdcorpus tokenizer), with no type inference: "fits" compares the argument count only. Base scripts are
resolved through every .gd file of the repository. A "wrapper" call is inside the method of the same name. Every
first-party file counts; with a line-capped manifest, the files of the sample are counted again on their own.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

# name -> (min args, max args or None)
GDSCRIPT = {
    "convert": (2, 2), "type_exists": (1, 1), "char": (1, 1), "ord": (1, 1), "range": (1, 3),
    "load": (1, 1), "inst_to_dict": (1, 1), "dict_to_inst": (1, 1), "Color8": (3, 4),
    "print_debug": (0, None), "print_stack": (0, 0), "get_stack": (0, 0), "len": (1, 1),
    "is_instance_of": (2, 2),
}
# The analyzer checks no count for vararg engine utilities. These are their run-time minimums; the print family
# takes 0 (core/variant/variant_utility.cpp).
VARARG_MIN = {"max": 2, "min": 2, "str": 1, "push_error": 1, "push_warning": 1}
ARITY = {}  # name -> (kind, min args, max args or None)
NATIVE_METHODS = collections.defaultdict(dict)  # engine class -> {utility name: method}
OPEN, CLOSE = "([{", ")]}"


def load_api(path):
    with open(path, encoding="utf-8") as fh:
        api = json.load(fh)
    for f in api["utility_functions"]:
        n = len(f.get("arguments", []))
        ARITY[f["name"]] = ("engine", VARARG_MIN.get(f["name"], 0), None) if f["is_vararg"] else ("engine", n, n)
    for name, (lo, hi) in GDSCRIPT.items():
        ARITY[name] = ("gdscript", lo, hi)
    for c in api["classes"]:
        G.NATIVE_PARENT[c["name"]] = c.get("inherits")
        for m in c.get("methods", []):
            if m["name"] in ARITY:
                NATIVE_METHODS[c["name"]][m["name"]] = m


def native_owner(native, name):
    while native:
        if name in NATIVE_METHODS.get(native, {}):
            return native
        native = G.NATIVE_PARENT.get(native)
    return None


def matching(ts, i):
    """Index of the bracket closing the one at i."""
    depth = 0
    for j in range(i, len(ts)):
        t = ts[j]
        if t.k == "OP" and t.v in OPEN:
            depth += 1
        elif t.k == "OP" and t.v in CLOSE:
            depth -= 1
            if depth == 0:
                return j
    return len(ts) - 1


def split_args(ts, i, j):
    """Top-level comma-separated pieces between the brackets at i and j."""
    pieces, cur, depth = [], [], 0
    for t in ts[i + 1:j]:
        if t.k == "NL":
            continue
        if t.k == "OP" and t.v in OPEN:
            depth += 1
        elif t.k == "OP" and t.v in CLOSE:
            depth -= 1
        if depth == 0 and t.k == "OP" and t.v == ",":
            pieces.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        pieces.append(cur)
    return pieces


def params(ts, i, j):
    """(required, total, rest) of a parameter list."""
    req = total = 0
    rest = False
    for p in split_args(ts, i, j):
        if len(p) >= 3 and all(t.k == "OP" and t.v == "." for t in p[:3]):
            rest = True
            continue
        total += 1
        if not any(t.k == "OP" and t.v == "=" for t in p):
            req += 1
    return req, total, rest


class Cls:
    def __init__(self, file, path, extends, outer):
        self.file, self.path, self.extends, self.outer = file, path, extends, outer
        self.methods = {}  # utility name -> {"line", "req", "total", "rest", "static"}
        self.calls = []  # (name, line, argument count, enclosing method name)
        self.inner = {}  # simple name -> Cls

    @property
    def label(self):
        return self.path or "<top>"


def parse(rel, src):
    """The file's top-level class and its inner classes."""
    ts = G.tokenize(src)
    top = Cls(rel, "", None, None)
    scopes = [("class", -1, top)]
    depth = 0
    n = len(ts)
    for i, t in enumerate(ts):
        if t.k == "OP" and t.v in OPEN:
            depth += 1
        elif t.k == "OP" and t.v in CLOSE:
            depth = max(0, depth - 1)
        if t.k != "NL" and t.first and depth == 0 and not (t.k == "OP" and t.v in CLOSE):
            while len(scopes) > 1 and t.col <= scopes[-1][1]:
                scopes.pop()
            k = i
            while k < n and ts[k].k == "AN":
                k += 1
                if k < n and ts[k].k == "OP" and ts[k].v == "(" and ts[k].line == ts[k - 1].line:
                    k = matching(ts, k) + 1
            cls = next(s[2] for s in reversed(scopes) if s[0] == "class")
            inside_func = scopes[-1][0] == "func"
            if k + 1 < n and ts[k].k == "ID" and ts[k].v == "class" and ts[k + 1].k == "ID" and not inside_func:
                ext = None
                m = k + 2
                while m < n and ts[m].k != "NL" and not (ts[m].k == "OP" and ts[m].v == ":"):
                    if ts[m].k == "ID" and ts[m].v == "extends" and m + 1 < n:
                        if ts[m + 1].k == "STR":
                            ext = ("path", ts[m + 1].v)
                        elif ts[m + 1].k == "ID":
                            nm, q = ts[m + 1].v, m + 2
                            while q + 1 < n and ts[q].k == "OP" and ts[q].v == "." and ts[q + 1].k == "ID":
                                nm += "." + ts[q + 1].v
                                q += 2
                            ext = ("name", nm)
                    m += 1
                name = ts[k + 1].v
                c = Cls(rel, (cls.path + "." if cls.path else "") + name, ext, cls)
                cls.inner[name] = c
                scopes.append(("class", t.col, c))
            else:
                is_static = k < n and ts[k].k == "ID" and ts[k].v == "static"
                f = k + 1 if is_static else k
                if (f + 2 < n and ts[f].k == "ID" and ts[f].v == "func" and ts[f + 1].k == "ID"
                        and ts[f + 2].k == "OP" and ts[f + 2].v == "(" and not inside_func):
                    name = ts[f + 1].v
                    if name in ARITY:
                        req, total, rest = params(ts, f + 2, matching(ts, f + 2))
                        cls.methods.setdefault(name, {"line": ts[f + 1].line, "req": req, "total": total,
                                                      "rest": rest, "static": is_static})
                    scopes.append(("func", t.col, name))
        if t.k == "ID" and t.v in ARITY and i + 1 < n and ts[i + 1].k == "OP" and ts[i + 1].v == "(":
            prev = ts[i - 1] if i > 0 else None
            if not (prev and ((prev.k == "OP" and prev.v == ".") or (prev.k == "ID" and prev.v == "func"))):
                cls = next(s[2] for s in reversed(scopes) if s[0] == "class")
                fn = next((s[2] for s in reversed(scopes) if s[0] == "func"), None)
                cls.calls.append((t.v, t.line, len(split_args(ts, i + 1, matching(ts, i + 1))), fn))
    classes = []

    def collect(c):
        classes.append(c)
        for x in c.inner.values():
            collect(x)

    collect(top)
    return classes


def fits(argc, lo, hi):
    return argc >= lo and (hi is None or argc <= hi)


def scan_repo(name, group, out):
    """Append one row per declaration and per counted call to out["decls"] and out["calls"]."""
    R = G.Repo(sys.argv[1], name, group)
    parsed = {rel: parse(rel, R.read(rel)) for rel in R.files if rel.endswith(".gd")}
    infos = G.script_infos(R)
    by_class_name = {(R.project_of(rel).root, info["class_name"]): rel
                     for rel, info in infos.items() if info["class_name"]}

    def top_of(rel):
        return parsed[rel][0] if rel in parsed else None

    def find_inner(c, nm):
        """An inner class named by a bare or dotted name, seen from class c."""
        parts = nm.split(".")
        x = c
        while x is not None:
            y = x.inner.get(parts[0])
            if y is not None:
                for p in parts[1:]:
                    y = y.inner.get(p)
                    if y is None:
                        break
                if y is not None:
                    return y
            x = x.outer
        y = top_of(by_class_name.get((R.project_of(c.file).root, parts[0])))
        for p in parts[1:]:
            y = y.inner.get(p) if y else None
        return y

    def base_of(c):
        """(base script class or None, engine base class name or None)."""
        if c.path == "":
            info = infos.get(c.file, {})
            if info.get("base_script"):
                return top_of(info["base_script"]), None
            if info.get("extends") is None:
                return None, "RefCounted"
            return None, info.get("native_direct")
        if c.extends is None:
            return None, "RefCounted"
        kind, v = c.extends
        if kind == "path":
            rel = R.project_of(c.file).to_rel(v, c.file)
            if rel and rel.startswith("uid://"):
                rel = R.uid.get(rel)
            return top_of(rel), None
        y = find_inner(c, v)
        if y is not None:
            return y, None
        return None, v if v in G.NATIVE_PARENT else None

    def ancestors(c):
        """(base script classes, nearest first; engine base class name or None)."""
        seen, out_, cur = set(), [], c
        while True:
            b, native = base_of(cur)
            if b is None:
                return out_, native
            if (b.file, b.path) in seen or b is c:
                return out_, None
            seen.add((b.file, b.path))
            out_.append(b)
            cur = b

    def declaration(c, anc, native, cname):
        """(source, where, declaration) of the method a direct call of cname would find, or None."""
        if cname in c.methods:
            d = c.methods[cname]
            return "own", f"{c.label}:{d['line']}", d
        for a in anc:
            if cname in a.methods:
                d = a.methods[cname]
                return "script_base", f"{a.file} {a.label}:{d['line']}", d
        o = c.outer
        while o is not None:
            d = o.methods.get(cname)
            if d is not None and d["static"]:
                return "outer_static", f"{o.label}:{d['line']}", d
            o = o.outer
        owner = native_owner(native, cname)
        if owner is None:
            return None
        m = NATIVE_METHODS[owner][cname]
        args = m.get("arguments", [])
        d = {"req": sum(1 for a in args if "default_value" not in a), "total": len(args),
             "rest": m.get("is_vararg", False)}
        return "native_base", f"{owner} (via {native})", d

    for rel, classes in parsed.items():
        if not R.source_first_party(rel):
            continue
        out["files"].append((name, rel, R.first_party(rel)))
        for c in classes:
            anc, native = ancestors(c)
            for cname in c.methods:
                out["decls"].append({"repo": name, "file": rel, "name": cname, "sampled": R.first_party(rel)})
            for cname, line, argc, fn in c.calls:
                found = declaration(c, anc, native, cname)
                if found is None:
                    continue
                source, where, d = found
                kind, lo, hi = ARITY[cname]
                fu = fits(argc, lo, hi)
                fo = argc >= d["req"] and (d["rest"] or argc <= d["total"])
                out["calls"].append({
                    "repo": name, "group": group, "file": rel, "sampled": R.first_party(rel), "name": cname,
                    "kind": kind, "source": source, "where": where, "line": line,
                    "arity": "both" if fu and fo else "utility_only" if fu else "own_only" if fo else "neither",
                    "wrapper": "wrapper" if fn == cname else "other"})


def report(title, out, keep):
    files = [f for f in out["files"] if keep(f[2])]
    print(f"== {title}: {len(files)} .gd files in {len(G.REPOS)} repositories")
    file_sets = collections.defaultdict(set)
    sites = collections.Counter()
    for d in out["decls"]:
        if keep(d["sampled"]):
            for metric in ("decl", "decl_" + ARITY[d["name"]][0]):
                file_sets[metric].add((d["repo"], d["file"]))
    for r in out["calls"]:
        if keep(r["sampled"]):
            s = r["source"]
            for metric in (s, f"{s}_{r['kind']}", f"{s}_{r['arity']}", f"{s}_{r['wrapper']}",
                           f"{s}_{r['kind']}_{r['arity']}"):
                file_sets["call_" + metric].add((r["repo"], r["file"]))
                sites["call_" + metric] += 1
    for metric in sorted(file_sets):
        projects = len({repo for repo, _ in file_sets[metric]})
        text = f"  {metric}: {len(file_sets[metric])} files, {projects} projects"
        print(text + (f", {sites[metric]} sites" if metric.startswith("call") else ""))
    names = collections.Counter(d["name"] for d in out["decls"] if keep(d["sampled"]))
    print("  declared names: " + ", ".join(f"{k} {v}" for k, v in names.most_common()))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    load_api(sys.argv[2])
    out = {"files": [], "decls": [], "calls": []}
    for name, _, _, group in G.REPOS:
        scan_repo(name, group, out)
    report("first-party", out, lambda sampled: True)
    cap = G.MANIFEST_DATA.get("line_cap")
    if cap is not None:
        report(f"first-party, sampled to {cap} lines per repository", out, lambda sampled: sampled)
    print("== calls, by file" + ("; * marks a file outside the sample" if cap is not None else ""))
    places = collections.defaultdict(list)
    for r in out["calls"]:
        key = (r["repo"], r["file"], r["group"], r["sampled"], r["name"], r["source"], r["where"], r["kind"],
               r["arity"], r["wrapper"])
        places[key].append(r["line"])
    for (repo, rel, group, sampled, cname, source, where, kind, arity, wrapper), lines in sorted(places.items()):
        mark = "" if sampled or cap is None else " *"
        print(f"  {repo}/{rel} ({group}){mark} {cname}: {source} {where}, {kind}, {arity}, {wrapper}; "
              f"lines {', '.join(map(str, lines))}")


if __name__ == "__main__":
    main()
