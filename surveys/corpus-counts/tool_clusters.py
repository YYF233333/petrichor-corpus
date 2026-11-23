"""Scripts that `@tool` keeps from migrating: the first-party files with the annotation, and the first-party scripts
in one inheritance tree with such a file.

Usage: python tool_clusters.py CORPUS_DIR
    CORPUS_DIR: fetched with fetch.py at the repository root

A file has `@tool` when its tokens hold the annotation, as counts.py counts it. Two scripts are in one tree when one
extends the other, by path or by class_name, directly or through other first-party scripts. Petrichor supports
inheritance across languages in neither direction (spec §11.2). So while `@tool` is a compile error (spec §2.3), the
whole tree stays GDScript (spec §13.4). Class-level access between the files is not counted.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = []
    for name, _, _, group in G.REPOS:
        repo = G.Repo(sys.argv[1], name, group)
        infos = G.script_infos(repo)
        own = {f for f, s in infos.items() if s["first_party"]}
        tool = {f for f in own if any(t.k == "AN" and t.v == "@tool" for t in G.tokenize(repo.read(f)))}
        tree = collections.defaultdict(set)
        for f in own:
            base = infos[f]["base_script"]
            if base in own:
                tree[f].add(base)
                tree[base].add(f)
        kept, todo = set(tool), sorted(tool)
        while todo:
            for other in sorted(tree[todo.pop()]):
                if other not in kept:
                    kept.add(other)
                    todo.append(other)
        rows.append((group, name, len(own), len(tool), len(kept)))
    for group, name, files, tool, kept in sorted(rows):
        print(f"{group:7} {name:28} scripts {files:4}  @tool {tool:3}  with their trees {kept:3}  {100 * kept / files:5.1f}%")
    for group in sorted({r[0] for r in rows}):
        files, tool, kept = (sum(r[i] for r in rows if r[0] == group) for i in (2, 3, 4))
        print(f"{group:7} total: scripts {files}  @tool {tool}  with their trees {kept}  {100 * kept / files:.1f}%")
    files, tool, kept = (sum(r[i] for r in rows) for i in (2, 3, 4))
    print(f"all     total: scripts {files}  @tool {tool}  with their trees {kept}  {100 * kept / files:.1f}%")


if __name__ == "__main__":
    main()
