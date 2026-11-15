"""Results of `.get(...)`, `.pop_back()` and `.pop_front()` compared with `null` in first-party GDScript.

Usage: python null_compare.py CORPUS_DIR
    CORPUS_DIR: fetched with fetch.py at the repository root (first-party rules and groups from there)

Token-based (gdcorpus tokenizer), with no type resolution, so `.get(k)` also counts `Object.get` and typed
dictionaries. A call counts when `==` or `!=` and `null` follow its closing parenthesis. `get` is split by its
number of arguments: `get(k, default)` gives the value itself. Every use is listed with its repository group.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

KINDS = ("get/1", "get/2", "pop_back", "pop_front")
OPEN, CLOSE = "([{", ")]}"


def closing(ts, i):
    depth, commas = 0, 0
    for j in range(i, len(ts)):
        v = ts[j].v if ts[j].k == "OP" else None
        if v and v in OPEN:
            depth += 1
        elif v and v in CLOSE:
            depth -= 1
            if depth == 0:
                return j, commas
        elif v == "," and depth == 1:
            commas += 1
    return None, 0


def compared_with_null(ts, j):
    if j + 3 >= len(ts):
        return False
    a, b, c = ts[j + 1], ts[j + 2], ts[j + 3]
    adjacent = a.k == b.k == "OP" and a.line == b.line and a.col + 1 == b.col
    return adjacent and a.v in "=!" and b.v == "=" and c.k == "ID" and c.v == "null"


def kind(ts, i):
    t = ts[i]
    if t.v not in ("get", "pop_back", "pop_front") or i == 0 or ts[i - 1].v != "." or i + 1 >= len(ts) or ts[i + 1].v != "(":
        return None
    j, commas = closing(ts, i + 1)
    if j is None or not compared_with_null(ts, j):
        return None
    if t.v != "get":
        return t.v
    return "get/1" if commas == 0 else "get/2"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    counts = collections.defaultdict(collections.Counter)
    files = collections.defaultdict(set)
    found = []
    for name, _, _, group in G.REPOS:
        repo = G.Repo(sys.argv[1], name, group)
        for f, info in G.script_infos(repo).items():
            if not info["first_party"]:
                continue
            ts = [t for t in G.tokenize(repo.read(f)) if t.k != "NL"]
            for i, t in enumerate(ts):
                k = kind(ts, i) if t.k == "ID" else None
                if k:
                    counts[k][group] += 1
                    files[k].add(f"{name}/{f}")
                    found.append(f"{name}/{f}:{t.line} ({group}): {k}")
    for k in KINDS:
        by_group = ", ".join(f"{g} {n}" for g, n in sorted(counts[k].items()))
        print(f"{k:10} {sum(counts[k].values()):4} in {len(files[k]):3} files  {by_group}")
    for row in found:
        print(row)


if __name__ == "__main__":
    main()
