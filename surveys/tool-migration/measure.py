"""Migrate copies of corpus games with Petrichor's `pet migrate --dry-run` and save the reports.

    python measure.py GODOT PETRICHOR CORPUS [--work DIR] [GAME ...]

GODOT is a Godot 4.7 editor binary. PETRICHOR is a Petrichor build laid out as its addon:
`petrichor.gdextension` beside `bin/` with the editor library and `pet`. In the Petrichor
repository that is `tests/engine/project`; in a release it is `addons/petrichor`. CORPUS is a
corpus clone such as `corpus/v1`, which is only read.

Each game is copied to WORK/GAME (default work/tool-migration), given the addon and imported
once with Godot. A later run reuses the imported copy and replaces only the addon's files. The
report of each game goes to WORK/GAME.txt; summarize.py derives the committed results from it.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMES = ["Starter-Kit-FPS", "deck_builder_tutorial", "tanks-of-freedom-ii"]
PET = {"win32": "pet.windows.x86_64.exe", "linux": "pet.linux.x86_64", "darwin": "pet.macos.universal"}[sys.platform]
DEBUG_FILES = (".pdb", ".exp", ".lib")


def install(build, addon):
    (addon / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy(build / "petrichor.gdextension", addon)
    for f in (build / "bin").iterdir():
        if f.is_file() and not f.name.endswith(DEBUG_FILES):
            shutil.copy(f, addon / "bin" / f.name)


def prepare(godot, build, corpus, work, game):
    copy = work / game
    fresh = not copy.exists()
    if fresh:
        shutil.copytree(corpus / game, copy, ignore=shutil.ignore_patterns(".git"))
    install(build, copy / "addons" / "petrichor")
    if fresh:
        subprocess.run([godot, "--headless", "--import", "--path", str(copy)], capture_output=True, timeout=1800)
    return copy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("godot")
    ap.add_argument("petrichor", type=Path)
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--work", type=Path, default=ROOT / "work" / "tool-migration")
    ap.add_argument("games", nargs="*", default=GAMES)
    args = ap.parse_intermixed_args()
    godot = str(Path(shutil.which(args.godot) or args.godot).resolve())
    args.work.mkdir(parents=True, exist_ok=True)
    for game in args.games:
        copy = prepare(godot, args.petrichor.resolve(), args.corpus.resolve(), args.work.resolve(), game)
        start = time.monotonic()
        ran = subprocess.run([copy / "addons" / "petrichor" / "bin" / PET, "migrate", "--dry-run", "--godot", godot],
                             capture_output=True, timeout=3600, cwd=copy)
        out = (ran.stdout + ran.stderr).decode("utf-8", "replace").replace("\r\n", "\n")
        (args.work / f"{game}.txt").write_text(out, encoding="utf-8", newline="\n")
        lines = out.rstrip().splitlines()
        print(game, f"{time.monotonic() - start:.0f} s", f"exit {ran.returncode}", lines[-1] if lines else "", flush=True)


if __name__ == "__main__":
    main()
