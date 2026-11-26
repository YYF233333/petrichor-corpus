"""Derive the committed results of the tool-migration survey from the reports of measure.py.

    python summarize.py CORPUS REPORTS COMMIT [--out DIR] [GAME ...]

CORPUS is the corpus clone the reports were measured on, read for first-party lines. REPORTS is
the work directory of measure.py, holding GAME.txt. COMMIT is the Petrichor commit of the build.
Writes summary.tsv, fixes.tsv, templates.tsv, causes.tsv and errors-GAME.tsv to DIR (default
results/ beside this script).

An error's template is its message with names, types, paths and numbers replaced. Its cause
comes from the template; for a slot left without a type, from the report's hint at that slot.
"""
import argparse
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

GAMES = ["Starter-Kit-FPS", "deck_builder_tutorial", "tanks-of-freedom-ii"]
DIAGNOSTIC = re.compile(r"^(?P<path>[^:]+\.pet):(?P<line>\d+):(?P<col>\d+): (?P<kind>error|hint): (?P<msg>.*)$")
MIGRATED = re.compile(r"^(?P<gd>\S+\.gd) → ")
FIX = re.compile(r"^(?P<n>\d+) × (?P<fix>.+)$")
SUMMARY = re.compile(r"^petrichor migrate: (?P<scripts>\d+) script\(s\), (?P<added>\d+) added, (?P<left_out>\d+) left out, "
                     r"(?P<types>\d+) type\(s\), (?P<withdrawn>\d+) withdrawn, (?P<fixes>\d+) fix\(es\), "
                     r"(?P<paths>\d+) path\(s\) renamed, (?P<errors>\d+) error\(s\)")
LEFT = re.compile(r'^"(?P<name>\w+)" is left without a type: .*?(?P<why> has no name here| does not check)\.(?P<none> Nothing flows into it\.)?')
SLOT = re.compile(r'^(?:Parameter "(?P<p>\w+)" needs a type\.|"(?P<v>\w+)" needs a type( or an initial value|: None does not say)'
                  r'|"(?P<f>\w+)\(\)" returns void\. Declare its return type|An empty (array|dictionary) needs a declared type)')
WORDS = {"A", "An", "As", "Base", "Cannot", "Convert", "Declare", "Function", "Narrow", "Not", "Parameter", "The", "There", "This", "To"}
KEPT = {"Variant", "None", "Object"}

# (cause, pattern on the message), first match wins. Slot errors are settled by their hints first.
CAUSES = [
    ("missing-resource", r"^There is no resource at |does not fit its type: expected \w+, found Resource\.$"),
    ("cascade", r"has errors \(|^This call returns void and has no value\.$"),
    ("no-class-name", r"^The type of \S+ is not known here"),
    ("object-none", r"^The value may be None \(Object\?\)"),
    ("unwrap", r"^The value may be None \("),
    ("setter-await", r"^await requires an async function and cannot appear in an initializer\.$"),
    ("setter-parameter", r"^As the setter of \"\w+\", \w+\(\) takes one argument of type \S+\? and returns nothing\.$"),
    ("signature", r"^Function \"emit\(\)\" takes|passes \d+ argument\(s\)|^Cannot pass a value of type (Texture\?|String) as (Card|bool)\.$"),
    ("downcast", r"^The elements are (?!Variant\b)\S+, which the loop variable|^Cannot (assign|pass) a value of type (Resource|Texture|Node)\??"
                 r" as |passes (?!Variant\b)\w+ as argument \d+, which func\("),
    ("implicit-null", r"needs an initial value\.$|the resource has no value for \"\w+\", which must be assigned"
                      r"|^instantiate\(\) needs \w+ = \.\.\., (a member|an export) of"),
    ("null-literal", r"^Cannot (assign|pass) a value of type None as "),
    ("variant", r"\bVariant\b"),
    ("missing-member", r"^\w+ has no (property|method) \""),
    ("conversion", r"Convert explicitly with"),
    ("exported-scene", r"^An exported scene is written PackedScene"),
    ("rule", r"^This match over|^An index must be|requires int operands|^is tests classes|is never None\.$|^Not all paths of"
             r"|^None does not say which \S+ the (elements|values) are|which have no common type|does not fit its type: Array\["
             r"|^Cannot (assign|return) a value of type \w+ as \w+\.$|^Function \"new\(\)\" not found"
             r"|^A signal is connected to a function value|the root has no node at|^An empty (array|dictionary) needs a declared type"),
]


def template(msg):
    msg = re.sub(r"\(res://[^)]*\)", "(<path>)", msg)
    msg = re.sub(r"res://\S+?(?=[:.,]?(\s|$))", "<path>", msg)
    msg = re.sub(r"^Base script <path>", "Base script <decl>", msg)
    msg = re.sub(r"\S+ has errors \(", "<decl> has errors (", msg)
    msg = re.sub(r"The type of \S+ is not known here", "The type of <member> is not known here", msg)
    msg = re.sub(r"instantiate\(\) needs \w+ =", "instantiate() needs <member> =", msg)
    msg = re.sub(r"(connected to |; |, )\w+\(\)( takes|, which)", r"\1<f>()\2", msg)
    msg = re.sub(r'(the value stored for "[^"]*" of )\S+', r"\1<node>", msg)
    msg = re.sub(r"for example -> \S+?\.$", "for example -> T.", msg)
    msg = re.sub(r'\$?"[^"]*"', "<name>", msg)
    msg = re.sub(r"`[^`]*`", "`E`", msg)
    msg = re.sub(r"\b(line|lines) \d+(, \d+)*", r"\1 #", msg)
    msg = re.sub(r"\b\d+\b", "#", msg)
    msg = re.sub(r"\b(int|float|bool)\b", "T", msg)

    def name(m):
        return m[0] if m[1] in WORDS or (m[1] in KEPT and not m[2]) else "T"
    msg = re.sub(r"\b([A-Z][A-Za-z0-9_]*)((?:\.[A-Z][A-Za-z0-9_]*)*(?:\[(?:[^\[\]]|\[[^\]]*\])*\])?\??)", name, msg)
    return re.sub(r"\bT(, T)*( and T)?\b", "T", msg)


def cause(e, hints, source):
    """A slot's error takes the reason of its hint: the hint on its line naming it, else one naming it in its
    file, else one naming it anywhere (a return in an override). An empty literal is named by its assignment."""
    msg, path, line = e["msg"], e["path"], e["line"]
    slot = SLOT.match(msg)
    if slot:
        named = slot["p"] or slot["v"] or slot["f"]
        if named is None:
            target = re.search(r"(\w+)\s*(?::[^=]*)?=\s*$", source[:int(e["col"]) - 1])
            named = target and target[1]
        for where in ((path, line), path, None):
            found = {why for (p, l, n), why in hints.items() if n == named and (where is None or where in ((p, l), p))}
            if len(found) == 1:
                return found.pop()
            if found:
                break
    if re.search(r":\s*Packed\w+Array\s*=\s*\[\]", source) and msg.startswith("An empty array"):
        return "conversion"
    for name, pattern in CAUSES:
        if re.search(pattern, msg):
            return name
    return "other"


def read(report):
    errors, hints, fixes, migrated, summary = [], {}, [], [], None
    with open(report, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            d = DIAGNOSTIC.match(line)
            if d and d["kind"] == "error":
                errors.append(d)
            elif d:
                left = LEFT.match(d["msg"])
                if left:
                    why = "no-class-name" if left["why"] == " has no name here" else "slot-no-inflow" if left["none"] else "slot-unchecked"
                    hints[d["path"], d["line"], left["name"]] = why
            elif MIGRATED.match(line):
                migrated.append(MIGRATED.match(line)["gd"])
            elif FIX.match(line):
                fixes.append((int(FIX.match(line)["n"]), FIX.match(line)["fix"]))
            elif SUMMARY.match(line):
                summary = line
    return errors, hints, fixes, migrated, summary


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        out = csv.writer(fh, delimiter="\t", lineterminator="\n")
        out.writerow(header)
        out.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("reports")
    ap.add_argument("commit")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("games", nargs="*", default=GAMES)
    args = ap.parse_intermixed_args()
    os.makedirs(args.out, exist_ok=True)
    summary_rows, fix_rows, template_rows, cause_counts = [], [], [], collections.Counter()
    for game in args.games:
        errors, hints, fixes, migrated, summary = read(os.path.join(args.reports, game + ".txt"))
        if summary is None:
            sys.exit(f"{game}: no summary line in the report")
        s = SUMMARY.match(summary)
        if int(s["errors"]) != len(errors):
            sys.exit(f"{game}: the summary counts {s['errors']} errors, the report lists {len(errors)}")
        repo = G.Repo(args.corpus, game, G.REPO_METADATA[game]["group"])
        lines = sum(repo.read(f).count("\n") + 1 for f in migrated if repo.first_party(f))
        rows, by_template = [], collections.defaultdict(list)
        for e in errors:
            # The lines that the tool adds, as constants that name classes, may put the line past the end.
            source = (repo.read(e["path"][:-len(".pet")] + ".gd").split("\n")[int(e["line"]) - 1:] + [""])[0]
            t, c = template(e["msg"]), cause(e, hints, source)
            rows.append((e["path"], e["line"], c, t))
            by_template[c, t].append(e)
            cause_counts[game, c] += 1
        missing = sum(1 for r in rows if r[2] == "missing-resource")
        summary_rows.append((game, args.commit, s["scripts"], s["left_out"], s["types"], s["withdrawn"], s["fixes"], s["errors"],
                             missing, lines, f"{100 * len(errors) / lines:.1f}", f"{100 * (len(errors) - missing) / lines:.1f}", summary))
        fix_rows += [(game, n, fix) for n, fix in fixes]
        for (c, t), es in sorted(by_template.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            template_rows.append((game, c, len(es), len({e["path"] for e in es}), f"{es[0]['path']}:{es[0]['line']}", t))
        write(os.path.join(args.out, f"errors-{game}.tsv"), ["file", "line", "cause", "template"], rows)
    write(os.path.join(args.out, "summary.tsv"),
          ["game", "petrichor", "scripts", "left_out", "types", "withdrawn", "fixes", "errors", "missing_resource",
           "lines", "errors_per_100_lines", "without_missing_resource", "report"], summary_rows)
    write(os.path.join(args.out, "fixes.tsv"), ["game", "count", "fix"], fix_rows)
    write(os.path.join(args.out, "templates.tsv"), ["game", "cause", "errors", "files", "first", "template"], template_rows)
    causes = sorted({c for _, c in cause_counts}, key=lambda c: (-sum(cause_counts[g, c] for g in args.games), c))
    write(os.path.join(args.out, "causes.tsv"), ["cause"] + args.games,
          [[c] + [cause_counts[g, c] for g in args.games] for c in causes])
    for row in summary_rows:
        print("\t".join(str(v) for v in row[:12]))


if __name__ == "__main__":
    main()
