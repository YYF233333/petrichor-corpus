"""Fetch a corpus version: shallow, blobless, sparse clones pinned to the commits in its manifest.

    python fetch.py [VERSION] [name ...]

VERSION defaults to v1. Reads corpus/VERSION.json and clones into corpus/VERSION/<name>.
Re-running skips the clones already at their commit. Python 3 stdlib only; needs git on PATH.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def head(d):
    r = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and os.path.isdir(os.path.join(d, ".git")) else None


def fetch(dest, url, sha, sparse):
    if head(dest) == sha:
        print(f"{os.path.basename(dest)}: already at {sha}")
        return
    os.makedirs(dest, exist_ok=True)

    def git(*args):
        print("+ git", " ".join(args), flush=True)
        subprocess.run(["git", *args], cwd=dest, check=True)

    git("init", "-q")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=dest, capture_output=True)
    git("remote", "add", "origin", url)
    git("config", "core.longpaths", "true")
    git("sparse-checkout", "set", "--no-cone", *sparse)
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", sha)
    git("checkout", "-q", "--detach", sha)
    assert head(dest) == sha, dest


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    want = set(sys.argv[2:])
    with open(os.path.join(ROOT, "corpus", version + ".json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    for r in manifest["repos"]:
        if not want or r["name"] in want:
            fetch(os.path.join(ROOT, "corpus", version, r["name"]), r["url"], r["commit"], manifest["sparse"])


if __name__ == "__main__":
    main()
