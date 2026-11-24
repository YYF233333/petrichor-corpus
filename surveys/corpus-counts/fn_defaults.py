"""Functions with default parameters used as values that the caller may call with fewer arguments:
method values connected to a signal, and `f.bind(...)`.

Usage: python fn_defaults.py CORPUS_DIR EXTENSION_API_JSON
    CORPUS_DIR: fetched with fetch.py at the repository root
    EXTENSION_API_JSON: inputs/extension_api-4-7.json

Token-based (gdcorpus tokenizer), over first-party files. A function is resolved by name: in the same file, then in
the repository when all functions of that name have the same parameter counts. A signal's argument count is known by
name the same way, from the repository's `signal` declarations or from the engine's signals.

- A connection is `sig.connect(m)` or `connect("sig", m)`, where `m` is a name, `self.m`, `x.m` or
  `Callable(x, "m")`.
- A bind is `m.bind(...)` or `Callable(x, "m").bind(...)`. Its caller's argument count k is known when it is the
  handler of such a connection. The engine passes the bound arguments after the caller's (Godot ed1daf0
  `core/variant/callable_bind.cpp:141-150`), so with t parameters and n bound values the caller fills the defaults
  when k = t - n.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

OPEN, CLOSE = "([{", ")]}"


def close_of(ts, j):
    depth = 0
    for k in range(j, len(ts)):
        if ts[k].k == "OP" and ts[k].v in OPEN:
            depth += 1
        elif ts[k].k == "OP" and ts[k].v in CLOSE:
            depth -= 1
            if depth == 0:
                return k
    return None


def open_of(ts, k):
    depth = 0
    for j in range(k, -1, -1):
        if ts[j].k == "OP" and ts[j].v in CLOSE:
            depth += 1
        elif ts[j].k == "OP" and ts[j].v in OPEN:
            depth -= 1
            if depth == 0:
                return j
    return None


def args_of(ts, j):
    """The top-level arguments of the parenthesis at j, as token lists."""
    end = close_of(ts, j)
    if end is None:
        return None
    out, start, depth = [], j + 1, 0
    for k in range(j + 1, end):
        t = ts[k]
        if t.k == "OP" and t.v in OPEN:
            depth += 1
        elif t.k == "OP" and t.v in CLOSE:
            depth -= 1
        elif t.k == "OP" and t.v == "," and depth == 0:
            out.append(ts[start:k])
            start = k + 1
    if end > start:
        out.append(ts[start:end])
    return out


def has_default(param):
    depth = 0
    for t in param:
        if t.k != "OP":
            continue
        if t.v in OPEN:
            depth += 1
        elif t.v in CLOSE:
            depth -= 1
        elif t.v == "=" and depth == 0:
            return True
    return False


def declarations(ts):
    """Named functions as name -> {(total, required)}, and signals as name -> {argument count}."""
    funcs, signals = collections.defaultdict(set), collections.defaultdict(set)
    for i, t in enumerate(ts):
        if t.k != "ID" or t.v not in ("func", "signal") or i + 1 >= len(ts) or ts[i + 1].k != "ID":
            continue
        name = ts[i + 1].v
        params = args_of(ts, i + 2) if i + 2 < len(ts) and ts[i + 2].v == "(" else None
        if t.v == "signal":
            signals[name].add(len(params or []))
        elif params is not None:
            funcs[name].add((len(params), sum(1 for p in params if not has_default(p))))
    return funcs, signals


def method_of(arg):
    """The method a handler argument names, for a name, `a.b.m` or `Callable(x, "m")`."""
    if len(arg) >= 4 and arg[0].v == "Callable" and arg[1].v == "(":
        inner = args_of(arg, 1)
        if close_of(arg, 1) == len(arg) - 1 and inner and len(inner) == 2 and len(inner[1]) == 1 and inner[1][0].k == "STR":
            return inner[1][0].v
        return None
    if len(arg) % 2 == 0:
        return None
    for i, t in enumerate(arg):
        if (i % 2 == 0 and t.k != "ID") or (i % 2 == 1 and not (t.k == "OP" and t.v == ".")):
            return None
    return arg[-1].v


def bound_method(arg):
    """For a handler argument `<method>.bind(...)`, the method and the number of bound values."""
    if len(arg) < 4 or arg[-1].v != ")":
        return None, None
    paren = open_of(arg, len(arg) - 1)
    if paren is None or paren < 3 or arg[paren - 1].v != "bind" or arg[paren - 2].v != ".":
        return None, None
    return method_of(arg[:paren - 2]), len(args_of(arg, paren) or [])


def main():
    corpus, api_path = sys.argv[1], sys.argv[2]
    engine_signals = collections.defaultdict(set)
    with open(api_path, encoding="utf-8") as fh:
        for c in json.load(fh)["classes"]:
            for s in c.get("signals", []):
                engine_signals[s["name"]].add(len(s.get("arguments", [])))
    c = collections.Counter()
    sites = collections.defaultdict(list)
    for name, _, _, group in G.REPOS:
        repo = G.Repo(corpus, name, group)
        files = [f for f in repo.files if f.endswith(".gd") and repo.first_party(f)]
        toks = {f: [t for t in G.tokenize(repo.read(f)) if t.k != "NL"] for f in files}
        decl = {f: declarations(ts) for f, ts in toks.items()}
        repo_funcs, repo_signals = collections.defaultdict(set), collections.defaultdict(set)
        for fs, ss in decl.values():
            for k, v in fs.items():
                repo_funcs[k] |= v
            for k, v in ss.items():
                repo_signals[k] |= v

        def resolve(f, method):
            sigs = decl[f][0].get(method) or repo_funcs.get(method)
            return next(iter(sigs)) if sigs and len(sigs) == 1 else None

        for f, ts in toks.items():
            for p in range(1, len(ts)):
                if ts[p].v != "(" or ts[p - 1].v != "connect":
                    continue
                args = args_of(ts, p)
                if not args:
                    continue
                if len(args[0]) == 1 and args[0][0].k == "STR" and len(args) >= 2:
                    signal, handler = args[0][0].v, args[1]
                elif p >= 3 and ts[p - 2].v == "." and ts[p - 3].k == "ID":
                    signal, handler = ts[p - 3].v, args[0]
                else:
                    continue
                known = repo_signals.get(signal) or engine_signals.get(signal)
                arity = next(iter(known)) if known and len(known) == 1 else None
                method, n = bound_method(handler)
                kind = "bind" if method else "method value"
                if not method:
                    method, n = method_of(handler), 0
                if not method:
                    continue
                c[f"{kind}: connections"] += 1
                sig = resolve(f, method)
                if not sig:
                    c[f"{kind}: function not resolved"] += 1
                    continue
                total, required = sig
                if total == required or n >= total:
                    c[f"{kind}: no default left to the caller"] += 1
                    continue
                c[f"{kind}: defaults the caller may leave"] += 1
                site = f"{group} {name}/{f}:{ts[p].line} {method}(t={total}, r={required})" + (f".bind(n={n})" if n else "") + f" <- {signal}"
                if arity is None:
                    c[f"{kind}:   signal's count unknown"] += 1
                    continue
                site += f"({arity})"
                if arity + n == total:
                    c[f"{kind}:   caller fills the defaults"] += 1
                    sites[f"{kind}, fills"].append(site)
                elif required <= arity + n < total:
                    c[f"{kind}:   caller leaves defaults"] += 1
                    sites[f"{kind}, leaves"].append(site)
                else:
                    c[f"{kind}:   count outside the range"] += 1
                    sites[f"{kind}, outside"].append(site)
    for kind in ("method value", "bind"):
        for k in ("connections", "function not resolved", "no default left to the caller", "defaults the caller may leave",
                  "  caller fills the defaults", "  caller leaves defaults", "  count outside the range", "  signal's count unknown"):
            print(f"{kind + ': ' + k:50} {c[kind + ': ' + k]:5}")
    for k in ("method value, leaves", "bind, leaves", "bind, fills"):
        print(f"\n== {k}")
        for s in sites[k]:
            print(s)


if __name__ == "__main__":
    main()
