"""Rerun the surveys whose inputs are pinned and public, and compare their output with the committed results.

    python reproduce.py [survey ...]

Needs corpus v1 (python fetch.py) and inputs/extension_api-4-7.json (see README.md).
Writes to work/reproduce/ and exits non-zero when any output differs from its committed result.
Line endings are not compared.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "work", "reproduce")
CORPUS = "corpus/v1"
API = "inputs/extension_api-4-7.json"
GODOT = os.environ.get("GODOT_REFERENCE", "inputs/godot-docs")

# survey: [(script and arguments, stdout file or None, [(produced file, committed file)])]
# Paths are relative to the repository root; {out} is the survey's directory under work/reproduce/.
STEPS = {
    "by-name-access": [
        ("by-name-access/names.py", [CORPUS, API], "names.txt", [("names.txt", "by-name-access/results/names.txt"), ("by_name_access.json", "by-name-access/results/by_name_access.json")]),
    ],
    "constant-expressions": [
        ("constant-expressions/constants.py", [CORPUS, API], "constants.txt", [("constants.txt", "constant-expressions/results/constants.txt")]),
    ],
    "corpus-counts": [
        ("corpus-counts/counts.py", [CORPUS, "--metrics", "{out}/metrics.json"], "counts.txt", [("counts.txt", "corpus-counts/results/counts.txt"), ("metrics.json", "corpus-counts/results/metrics.json")]),
        ("paper-migration-2/autoload_self.py", [CORPUS], "autoload_self.txt", [("autoload_self.txt", "corpus-counts/results/autoload_self.txt")]),
        ("corpus-counts/inner_classes.py", [CORPUS, API, "--samples", "0"], "inner_classes.txt", [("inner_classes.txt", "corpus-counts/results/inner_classes.txt")]),
        ("corpus-counts/layout.py", [CORPUS], "layout.txt", [("layout.txt", "corpus-counts/results/layout.txt"), ("layout.json", "corpus-counts/results/layout.json")]),
        ("corpus-counts/ancestor_assignments.py", [CORPUS], "ancestor_assignments.txt", [("ancestor_assignments.txt", "corpus-counts/results/ancestor_assignments.txt")]),
        ("corpus-counts/init_params.py", [CORPUS, API], "init_params.txt", [("init_params.txt", "corpus-counts/results/init_params.txt"), ("init_params.json", "corpus-counts/results/init_params.json")]),
        ("corpus-counts/class_level_access.py", [CORPUS, API], "class_level_access.txt", [("class_level_access.txt", "corpus-counts/results/class_level_access.txt")]),
        ("corpus-counts/preload_cycles.py", [CORPUS], "preload_cycles.txt", [("preload_cycles.txt", "corpus-counts/results/preload_cycles.txt")]),
        ("corpus-counts/string_index.py", [CORPUS], "string_index.txt", [("string_index.txt", "corpus-counts/results/string_index.txt")]),
        ("corpus-counts/null_failures.py", [CORPUS], "null_failures.txt", [("null_failures.txt", "corpus-counts/results/null_failures.txt")]),
        ("corpus-counts/weak_refs.py", [CORPUS], "weak_refs.txt", [("weak_refs.txt", "corpus-counts/results/weak_refs.txt")]),
        ("corpus-counts/autoload_types.py", [CORPUS], "autoload_types.txt", [("autoload_types.txt", "corpus-counts/results/autoload_types.txt")]),
        ("corpus-counts/engine_objects.py", [CORPUS, API], "engine_objects.txt", [("engine_objects.txt", "corpus-counts/results/engine_objects.txt"), ("engine_objects.json", "corpus-counts/results/engine_objects.json")]),
    ],
    "member-visibility": [
        ("cross-branch-duplication/build_api.py", [GODOT, "{out}/api.json"], None, []),
        ("member-visibility/vis.py", [CORPUS, "{out}/api.json"], "vis.txt", [("vis.txt", "member-visibility/results/vis.txt")]),
    ],
    "cross-branch-duplication": [
        ("cross-branch-duplication/build_api.py", [GODOT, "{out}/api.json"], None, []),
        ("cross-branch-duplication/dup.py", ["--corpus", CORPUS, "--api", "{out}/api.json", "--out", "{out}"], None,
         [("summary.json", "cross-branch-duplication/out/summary.json"), ("workarounds.json", "cross-branch-duplication/out/workarounds.json")]),
        ("cross-branch-duplication/components.py", ["--corpus", CORPUS, "--api", "{out}/api.json", "--out", "{out}"], None,
         [("components.csv", "cross-branch-duplication/out/components.csv"), ("components_summary.json", "cross-branch-duplication/out/components_summary.json")]),
        ("cross-branch-duplication/report.py", ["{out}"], None, [("report.txt", "cross-branch-duplication/out/report.txt")]),
        ("cross-branch-duplication/dup.py", ["--corpus", CORPUS, "--api", "{out}/api.json", "--out", "{out}/k3", "--k", "3"], None, []),
        ("cross-branch-duplication/report.py", ["{out}/k3"], None, [("k3/report.txt", "cross-branch-duplication/out_k3/report.txt")]),
        ("cross-branch-duplication/dup.py", ["--corpus", CORPUS, "--api", "{out}/api.json", "--out", "{out}/k8", "--k", "8"], None, []),
        ("cross-branch-duplication/report.py", ["{out}/k8"], None, [("k8/report.txt", "cross-branch-duplication/out_k8/report.txt")]),
        ("cross-branch-duplication/ring_check.py", ["--corpus", CORPUS, "--api", "{out}/api.json", "{out}", "{out}/k3", "{out}/k8"], "ring_check.txt",
         [("ring_check.txt", "cross-branch-duplication/out/ring_check.txt")]),
    ],
    "await-signal-results": [
        ("await-signal-results/extract.py", [CORPUS, GODOT, "{out}"], "report.txt", [("report.txt", "await-signal-results/results/report.txt")]),
    ],
    "property-accessors": [
        ("property-accessors/extract.py", [CORPUS, "{out}"], "extraction.txt", [("extraction.txt", "property-accessors/results/extraction.txt")]),
        ("property-accessors/count.py", ["{out}"], "report.txt", [("report.txt", "property-accessors/results/report.txt")]),
    ],
    "implementation-coverage": [
        ("implementation-coverage/coverage.py", [CORPUS, API], "coverage.txt", [("coverage.txt", "implementation-coverage/results/coverage.txt")]),
        ("implementation-coverage/remaining.py", [CORPUS, API], "remaining.txt", [("remaining.txt", "implementation-coverage/results/remaining.txt")]),
        ("implementation-coverage/remaining2.py", [CORPUS, API], "remaining2.txt", [("remaining2.txt", "implementation-coverage/results/remaining2.txt")]),
        ("implementation-coverage/gdscript_builtins.py", [CORPUS], "gdscript_builtins.txt", [("gdscript_builtins.txt", "implementation-coverage/results/gdscript_builtins.txt")]),
        ("implementation-coverage/remaining3.py", [CORPUS, API], "remaining3.txt", [("remaining3.txt", "implementation-coverage/results/remaining3.txt")]),
    ],
    "pitfalls": [
        ("pitfalls/build.py", ["{out}"], None, [("catalog.tsv", "pitfalls/catalog.tsv"), ("catalog.md", "pitfalls/catalog.md")]),
    ],
    "scene-structures": [
        ("scene-structures/analyze.py", [CORPUS, "{out}"], None, [("repos.json", "scene-structures/results/repos.json")]),
        ("scene-structures/report.py", [CORPUS, "{out}"], None, [("report.txt", "scene-structures/results/report.txt"), ("multi_games.txt", "scene-structures/results/multi_games.txt")]),
        ("scene-structures/summarize.py", ["{out}"], None, [("summary.txt", "scene-structures/results/summary.txt")]),
    ],
}


def read(path):
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def main():
    want = sys.argv[1:] or list(STEPS)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0",
               CORPUS_MANIFEST=os.path.join(ROOT, "corpus", "v1.json"))
    env.pop("CORPUS_AUTHORSHIP", None)
    env.pop("CORPUS_INCLUDE_REFERENCE", None)
    failed = []
    for survey in want:
        out = os.path.join(OUT, survey)
        env["SURVEY_METRICS_DIR"] = out
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for script, args, stdout, compare in STEPS[survey]:
            cmd = [sys.executable, os.path.join("surveys", script)] + [a.replace("{out}", out) for a in args]
            print("+", " ".join(cmd), flush=True)
            with open(os.path.join(out, stdout) if stdout else os.devnull, "wb") as fh:
                r = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh)
            if r.returncode:
                failed.append(f"{script}: exit {r.returncode}")
                continue
            for produced, committed in compare:
                if not os.path.isfile(os.path.join(ROOT, "surveys", committed)):
                    failed.append(f"{committed}: missing committed result")
                elif read(os.path.join(out, produced)) != read(os.path.join(ROOT, "surveys", committed)):
                    failed.append(f"{committed}: differs from {os.path.relpath(os.path.join(out, produced), ROOT)}")
    for f in failed:
        print("DIFFERS", f)
    print("all identical" if not failed else f"{len(failed)} differ")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
