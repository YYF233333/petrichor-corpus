"""Parameters with a default value, by how their type is written: `name := default`, which GDScript infers from the
default, `name: T = default`, and `name = default` without a type.

Usage: python param_defaults.py CORPUS_DIR
    CORPUS_DIR: fetched with fetch.py at the repository root

Token-based (gdcorpus tokenizer), over first-party files. A parameter list is the parentheses that follow `func` and
an optional name, so lambdas count too. Parameters are split at the commas of that list's own level, and a parameter
has a default when an `=` stands at that level.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

OPEN, CLOSE = "([{", ")]}"


def parameters(ts):
    """Each parameter of each `func` as (tokens, is_lambda)."""
    for i, t in enumerate(ts):
        if t.k != "ID" or t.v != "func":
            continue
        j = i + 1
        named = j < len(ts) and ts[j].k == "ID"
        if named:
            j += 1
        if j >= len(ts) or ts[j].v != "(":
            continue
        depth, start = 0, j + 1
        for k in range(j, len(ts)):
            v = ts[k].v
            if ts[k].k == "OP" and v in OPEN:
                depth += 1
            elif ts[k].k == "OP" and v in CLOSE:
                depth -= 1
                if depth == 0:
                    if k > start:
                        yield ts[start:k], not named
                    break
            elif ts[k].k == "OP" and v == "," and depth == 1:
                if k > start:
                    yield ts[start:k], not named
                start = k + 1


def kind(param):
    """How a parameter with a default writes its type, or None without a default."""
    depth = 0
    for n, t in enumerate(param):
        if t.k != "OP":
            continue
        if t.v in OPEN:
            depth += 1
        elif t.v in CLOSE:
            depth -= 1
        elif depth == 0 and t.v == ":=":
            return "inferred"
        elif depth == 0 and t.v == "=":
            if n and param[n - 1].k == "OP" and param[n - 1].v == ":":
                return "inferred"
            return "typed" if any(p.k == "OP" and p.v == ":" for p in param[:n]) else "untyped"
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    total = collections.Counter()
    files = collections.Counter()
    by_repo = collections.defaultdict(collections.Counter)
    sites = []
    for name, _, _, group in G.REPOS:
        repo = G.Repo(sys.argv[1], name, group)
        for f in repo.files:
            if not f.endswith(".gd") or not repo.first_party(f):
                continue
            ts = [t for t in G.tokenize(repo.read(f)) if t.k != "NL"]
            seen = set()
            for param, is_lambda in parameters(ts):
                total["parameters"] += 1
                k = kind(param)
                if k is None:
                    continue
                total[k] += 1
                total[k + "_lambda"] += is_lambda
                seen.add(k)
                if k == "inferred":
                    by_repo[(group, name)]["uses"] += 1
                    sites.append(f"{name}/{f}:{param[0].line} ({group})")
            for k in seen:
                files[k] += 1
            if "inferred" in seen:
                by_repo[(group, name)]["files"] += 1
    print(f"parameters                 {total['parameters']:6}")
    for k, label in (("inferred", "name := default"), ("typed", "name: T = default"), ("untyped", "name = default")):
        print(f"{label:26} {total[k]:6}  files {files[k]:4}  in lambdas {total[k + '_lambda']}")
    for (group, name), c in sorted(by_repo.items()):
        print(f"  {group:7} {name:28} uses {c['uses']:4}  files {c['files']:4}")
    for s in sorted(sites):
        print(s)


if __name__ == "__main__":
    main()
