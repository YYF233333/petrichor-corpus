"""Read the pinned class reference, including derived module metadata in sparse CI.

GODOT_REVISION reads Git objects without changing a local checkout. Regenerate the
module supplement with: python engine_reference.py GODOT_DIR REVISION OUTPUT
"""
import glob
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

COMMIT = "469659e0617345149cd1eaec2e643d61d130aa6a"
SUPPLEMENT = os.path.join(os.path.dirname(__file__), "module-reference.json")


def parse(text):
    root = ET.fromstring(text)
    if root.tag != "class":
        return None, None
    cls = {"inherits": root.get("inherits"), "signals": {}, "methods": {}, "members": {}, "constants": []}
    for sig in root.findall("signals/signal"):
        cls["signals"][sig.get("name")] = len(sig.findall("param"))
    for method in root.findall("methods/method"):
        ret = method.find("return")
        cls["methods"][method.get("name")] = ret.get("type") if ret is not None else "void"
    for member in root.findall("members/member"):
        cls["members"][member.get("name")] = member.get("type")
    for constant in root.findall("constants/constant"):
        cls["constants"].append(constant.get("name"))
        if constant.get("enum"):
            cls["constants"].append(constant.get("enum"))
    cls["constants"] = sorted(set(cls["constants"]))
    return root.get("name"), cls


def git_classes(directory, revision, modules_only=False):
    # The exception is process-local; no Git configuration is written.
    cmd = ["git", "-c", "safe.directory=" + os.path.abspath(directory), "-C", directory]
    paths = subprocess.check_output(cmd + ["ls-tree", "-r", "--name-only", revision], text=True).splitlines()
    paths = [p for p in paths if p.endswith(".xml") and
             ((not modules_only and p.startswith("doc/classes/")) or
              (p.startswith(("modules/", "platform/")) and "/doc_classes/" in p))]
    query = "".join(f"{revision}:{p}\n" for p in paths).encode()
    data = subprocess.check_output(cmd + ["cat-file", "--batch"], input=query)
    classes, offset = {}, 0
    for path in paths:
        end = data.index(b"\n", offset)
        size = int(data[offset:end].split()[-1])
        name, cls = parse(data[end + 1:end + 1 + size])
        offset = end + size + 2
        if name:
            classes[name] = cls
    return classes


def load(directory):
    revision = os.environ.get("GODOT_REVISION")
    if revision:
        return git_classes(directory, revision)
    paths = glob.glob(os.path.join(directory, "doc", "classes", "*.xml"))
    extra = glob.glob(os.path.join(directory, "modules", "*", "doc_classes", "*.xml"))
    extra += glob.glob(os.path.join(directory, "platform", "*", "doc_classes", "*.xml"))
    if not paths:
        raise FileNotFoundError(f"missing class reference: {directory}/doc/classes")
    classes = {}
    if not extra:
        with open(SUPPLEMENT, encoding="utf-8") as fh:
            supplement = json.load(fh)
        assert supplement["godot_commit"] == COMMIT
        classes.update(supplement["classes"])
    for path in sorted(paths + extra):
        with open(path, encoding="utf-8") as fh:
            name, cls = parse(fh.read())
        if name:
            classes[name] = cls
    return classes


if __name__ == "__main__":
    directory, revision, output = sys.argv[1:]
    classes = git_classes(directory, revision, modules_only=True)
    with open(output, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"godot_commit": revision, "classes": classes}, fh, indent=1, sort_keys=True)
        fh.write("\n")
