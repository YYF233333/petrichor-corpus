"""Migrate copies of corpus projects with Petrichor's `pet migrate`, then convert them back with
`pet migrate --reverse`, and save both reports.

    python measure.py GODOT PETRICHOR CORPUS [--work DIR] [--jobs N] [PROJECT ...]

GODOT, PETRICHOR and CORPUS are those of tool-migration/measure.py, whose preparation this reuses.
A PROJECT is the directory of a project.godot under CORPUS, such as Starter-Kit-FPS or
godot-demo-projects/2d/platformer; by default each Godot 4 project of the manifest.

Each project is copied to WORK/imported/PROJECT (default work/round-trip), given the addon and
imported once. Each run copies that to WORK/run/PROJECT, migrates it, converts it back, and writes
the reports to WORK/run/PROJECT.forward.txt and .reverse.txt. summarize.py compares the copy with
the corpus.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tool-migration"))
sys.path.insert(0, str(HERE.parent / "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402
from measure import PET, ROOT, prepare  # noqa: E402


def projects(corpus):
    """The directories of the Godot 4 projects of the manifest's repositories, as CORPUS paths."""
    found = []
    for name, _url, _commit, group in G.REPOS:
        repo = G.Repo(str(corpus), name, group)
        for root in sorted(repo.roots):
            settings = (root + "/" if root else "") + "project.godot"
            if settings in repo.fileset and re.search(r"(?m)^config_version\s*=\s*5\s*$", repo.read(settings)):
                found.append(name + ("/" + root if root else ""))
    return found


def pet(copy, godot, *args):
    ran = subprocess.run([copy / "addons" / "petrichor" / "bin" / PET, "migrate", "--allow-dirty", *args, "--godot", godot],
                         capture_output=True, timeout=3600, cwd=copy)
    return ran.returncode, (ran.stdout + ran.stderr).decode("utf-8", "replace").replace("\r\n", "\n")


def measure(godot, build, corpus, work, project):
    imported = prepare(godot, build, corpus, work / "imported", project)
    copy = work / "run" / project
    if copy.exists():
        shutil.rmtree(copy)
    shutil.copytree(imported, copy)
    start = time.monotonic()
    lines = []
    for step, args in (("forward", ()), ("reverse", ("--reverse",))):
        code, out = pet(copy, godot, *args)
        Path(f"{copy}.{step}.txt").write_text(out, encoding="utf-8", newline="\n")
        tail = out.rstrip().splitlines()
        lines.append(f"{step} exit {code}: {tail[-1] if tail else ''}")
    return f"{project}\t{time.monotonic() - start:.0f} s\t" + "\t".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("godot")
    ap.add_argument("petrichor", type=Path)
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--work", type=Path, default=ROOT / "work" / "round-trip")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("projects", nargs="*")
    args = ap.parse_intermixed_args()
    godot = str(Path(shutil.which(args.godot) or args.godot).resolve())
    work = args.work.resolve()
    todo = args.projects or projects(args.corpus)
    with ThreadPoolExecutor(args.jobs) as pool:
        for line in pool.map(lambda p: measure(godot, args.petrichor.resolve(), args.corpus.resolve(), work, p), todo):
            print(line, flush=True)


if __name__ == "__main__":
    main()
