"""Extract per-class API member names (methods, properties, signals, constants) and the parent class from a Godot
checkout's class reference XML (doc/classes, modules/*/doc_classes, platform/*/doc_classes). Read-only on the checkout.

Usage: python build_api.py GODOT_DIR API_JSON   -> writes API_JSON (records the engine commit; the survey used 469659e)
"""
import json
import os
import subprocess
import sys
from engine_reference import load

EXPECTED = "469659e0617345149cd1eaec2e643d61d130aa6a"
if len(sys.argv) != 3:
    sys.exit(__doc__)
root, out = sys.argv[1], sys.argv[2]
classes = {name: {"inherits": cls["inherits"], **{key: sorted(cls[key]) for key in
            ("methods", "members", "signals", "constants")}} for name, cls in load(root).items()}
commit = os.environ.get("GODOT_REVISION") or subprocess.run(
    ["git", "-c", "safe.directory=" + os.path.abspath(root), "-C", root, "rev-parse", "HEAD"],
    capture_output=True, text=True).stdout.strip()
if commit != EXPECTED:
    print(f"warning: {root} is at {commit or 'unknown commit'}, the survey used {EXPECTED}", file=sys.stderr)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump({"godot_commit": commit, "classes": classes}, fh, indent=0, sort_keys=True)
print(f"{len(classes)} classes from {commit}")
