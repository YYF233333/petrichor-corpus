"""Fetch a corpus version: shallow, blobless, sparse clones pinned to the commits in its manifest.

    python fetch.py [VERSION] [name ...]

VERSION defaults to v1. Reads corpus/VERSION.json and clones into corpus/VERSION/<name>.
Re-running skips the clones already at their commit. Python 3 stdlib only; needs git on PATH.
"""
import json
import argparse
import concurrent.futures
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def head(d):
    if not os.path.isdir(os.path.join(d, ".git")):
        return None
    try:
        with open(os.path.join(d, ".git", "HEAD"), encoding="ascii") as fh:
            detached = fh.read().strip()
        if len(detached) == 40 and all(c in "0123456789abcdef" for c in detached):
            return detached
    except OSError:
        pass
    r = subprocess.run(["git", "-c", "safe.directory=" + os.path.abspath(d), "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and os.path.isdir(os.path.join(d, ".git")) else None


def fetch(dest, url, sha, sparse):
    if head(dest) == sha:
        print(f"{os.path.basename(dest)}: already at {sha}")
        return
    os.makedirs(dest, exist_ok=True)

    def git(*args):
        print("+ git", " ".join(args), flush=True)
        subprocess.run(["git", "-c", "safe.directory=" + os.path.abspath(dest), *args], cwd=dest, check=True)

    git("init", "-q")
    subprocess.run(["git", "-c", "safe.directory=" + os.path.abspath(dest), "remote", "remove", "origin"], cwd=dest, capture_output=True)
    git("remote", "add", "origin", url)
    git("config", "core.longpaths", "true")
    git("sparse-checkout", "set", "--no-cone", *sparse)
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", sha)
    git("checkout", "-q", "--detach", sha)
    assert head(dest) == sha, dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", default="v1")
    parser.add_argument("names", nargs="*")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    version, want = args.version, set(args.names)
    with open(os.path.join(ROOT, "corpus", version + ".json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(fetch, os.path.join(ROOT, "corpus", version, r["name"]),
                               r["url"], r["commit"], manifest["sparse"])
                   for r in manifest["repos"] if not want or r["name"] in want]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
