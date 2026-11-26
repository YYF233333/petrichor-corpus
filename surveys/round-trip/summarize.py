"""Compare each file that measure.py migrated and converted back with its original.

    python summarize.py CORPUS WORK COMMIT [--out DIR]

CORPUS is the corpus clone the copies were made from. WORK is the work directory of measure.py.
COMMIT is the Petrichor commit of the build. Writes summary.tsv, refused.tsv, rules.tsv and
files.tsv to DIR (default results/ beside this script).

A file converted back is identical to its original, differs only by the known rewrites of
Petrichor's architecture §6.6, or differs otherwise. Each other difference is a hunk of a line diff
taken after the known rewrites, named by the first rule of RULES that its tokens meet.
"""
import argparse
import collections
import csv
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cross-branch-duplication"))
import gdcorpus as G  # noqa: E402

FORWARD = re.compile(r"^(?P<gd>\S+\.gd) → (?P<pet>\S+\.pet)")
BACK = re.compile(r"^(?P<pet>\S+\.pet) → (?P<gd>\S+\.gd)")
LEFT = re.compile(r"^(?P<pet>\S+\.pet): left out: (?P<why>.*)$")
DIAGNOSTIC = re.compile(r"^(?P<path>[^:]+\.pet):(?:\d+:){0,2} error: (?P<msg>.*)$")


def autoloads(settings):
    section = re.search(r"(?ms)^\[autoload\]$(.*?)(?=^\[|\Z)", settings)
    return re.findall(r'(?m)^(\w+)="\*', section.group(1)) if section else []


# The rewrites that a migration converted back keeps by design (architecture §6.6), each applied to
# both texts, or to the original as the migration wrote it.
def known(original, back, names):
    for quote in ('"""', "'''"):
        original, back = original.replace(quote, quote[0]), back.replace(quote, quote[0])
    for name in names:
        original = re.sub(r'\$(["\']?)/root/' + name + r'\1(?!\w)', name, original)
        original = re.sub(r'(?<![\w.])get_node\((["\'])/root/' + name + r'\1\)', name, original)

    def lines(text):
        text = re.sub(r"(?m)^[ \t]*_[ \t]*:[ \t]*pass[ \t]*\r?\n", "", text)
        text = re.sub(r"(?m)^[ \t]*return(?:[ \t]+null)?[ \t]*\r?\n", "", text)
        return re.sub(r"\breturn null\b", "return", text)
    return lines(original), lines(back)


def toks(text):
    return [(t.k, t.v, t.pre) for t in G.tokenize(text) if t.k != "NL"]


def words(tokens):
    return " ".join(str(v) if k != "STR" else repr(v) for k, v, _ in tokens)


# Each rule: a name, and a pattern on a change of a hunk's token diff, written "removed => added",
# each side the tokens' texts joined by spaces (`!=` is two tokens). A hunk is named by the rules
# its changes meet, parentheses aside; a change that meets none makes it "other".
TYPE = r"[A-Za-z_]\w*( \. \w+)*( \[ [\w. ,\[\]]* \])?"
RULES = [
    ("type-written", rf"^ => ((: |- > )?{TYPE}|\[ {TYPE} \])$"),
    ("type-changed", rf"^{TYPE} => {TYPE}$"),
    ("truth-test", r"^ => (\) )?(! =|= =) (null|0|0\.0|''|\w+ \( \))$|^not => $|^ => not$|^ => (not )?is_instance_valid \($"
                   r"|^ => \. (is_empty|is_null) \( \)$|^(= =|! =) null => \)$"),
    ("cast", rf"^ => (\) )?as {TYPE}( \))?$"),
    ("cast-dropped", rf"^as {TYPE} => $"),
    ("typed-array-as", r"^\(? ?\S+ as Array \[ [\w.]+ \] \)? => \S+$|^as Array \[ [\w.]+ \] \)? => $"),
    ("conversion", r"^ => (\( )?(int|float|Packed\w+Array)( \()?$|^(\d+) => \4\.0$"),
    ("method-or-signal-itself", r"^'\w+' ,? => $|^ => \w+ \.$|^emit_signal => \w+ \. emit$|^call_deferred \( '\w+' => \w+ \. call_deferred \($"),
    ("by-name", r"=> \S+ \. (call|set) \( '\w+'"),
    ("preload-constant", r"^ => (const \w+ = preload \( '[^']*' \) ?)+$"),
]
PARENTHESES = re.compile(r"^ => [()]$|^[()] => $")
# The rules among the known rewrites of architecture §6.6 at the commit measured, beside those
# known() applies: typed-array-as from 49b6da7, cast and preload-constant from 7921875, the others
# added by this survey.
KNOWN = {"type-written", "type-changed", "truth-test", "conversion", "method-or-signal-itself", "typed-array-as", "cast", "preload-constant"}


def changes(a, b):
    ta, tb = toks(a), toks(b)
    ops = difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes()
    return [words(ta[i1:i2]) + " => " + words(tb[j1:j2]) for tag, i1, i2, j1, j2 in ops if tag != "equal"]


def rule(a, b):
    found = changes(a, b)
    if not found:
        return "spacing"
    names = set()
    for change in found:
        if PARENTHESES.match(change):
            continue
        name = next((name for name, pattern in RULES if re.search(pattern, change)), "other")
        if name == "other":
            return name
        names.add(name)
    return "+".join(sorted(names)) or "parentheses"


def hunks(original, back):
    a, b = original.splitlines(keepends=True), back.splitlines(keepends=True)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            yield "".join(a[i1:i2]), "".join(b[j1:j2])


def example(a, b):
    shown = ["- " + line for line in a.splitlines()] + ["+ " + line for line in b.splitlines()]
    return " | ".join(s.replace("\t", "    ").strip() for s in shown[:5])


def refusal(why, messages):
    if why.startswith("in the inheritance tree of"):
        return "inheritance tree of a file that stays"
    if why.startswith("it uses "):
        return "class-level access to a file that stays"
    if not messages:
        return why
    first = messages[0]
    if first.startswith("It has compile errors"):
        return "compile errors"
    return re.sub(r"\b\d+\b", "#", re.sub(r"here \S+\.$", "here T.", re.sub(r"of \S+ where", "of T where", first)))


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        out = csv.writer(fh, delimiter="\t", lineterminator="\n")
        out.writerow(header)
        out.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("work")
    ap.add_argument("commit")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    run = os.path.join(args.work, "run")
    projects = sorted(os.path.relpath(os.path.join(d, f), run).replace("\\", "/")[:-len(".reverse.txt")]
                      for d, _, fs in os.walk(run) for f in fs if f.endswith(".reverse.txt"))
    summary, file_rows, refused, by_rule = [], [], collections.Counter(), collections.defaultdict(list)
    for project in projects:
        forward = read(os.path.join(run, project + ".forward.txt")).splitlines()
        reverse = read(os.path.join(run, project + ".reverse.txt")).splitlines()
        migrated = [m["gd"] for m in map(FORWARD.match, forward) if m]
        back = {m["gd"] for m in map(BACK.match, reverse) if m}
        left = {m["pet"]: m["why"] for m in map(LEFT.match, reverse) if m}
        messages = collections.defaultdict(list)
        for m in filter(None, map(DIAGNOSTIC.match, reverse)):
            messages[m["path"]].append(m["msg"])
        names = autoloads(read(os.path.join(args.corpus, project, "project.godot")))
        counts = collections.Counter()
        for gd in migrated:
            pet = gd[:-3] + ".pet"
            if gd not in back:
                reason = refusal(left.get(pet, "not converted"), messages.get(pet, []))
                refused[reason] += 1
                counts["refused"] += 1
                continue
            original = read(os.path.join(args.corpus, project, gd))
            converted = read(os.path.join(run, project, gd))
            if original == converted:
                kind = "identical"
            else:
                a, b = known(original, converted, names)
                found = [(rule(x, y), x, y) for x, y in hunks(a, b)]
                kind = "known" if all(set(name.split("+")) <= KNOWN for name, _, _ in found) else "other"
                for name, x, y in found:
                    by_rule[name].append((project + "/" + gd, x, y))
            counts[kind] += 1
            file_rows.append((project + "/" + gd, kind))
        summary.append((project, args.commit, len(migrated), len(back), counts["identical"], counts["known"], counts["other"], counts["refused"]))
    total = [sum(row[i] for row in summary) for i in range(2, 8)]
    write(os.path.join(args.out, "summary.tsv"), ["project", "petrichor", "migrated", "converted_back", "identical", "known_only", "other", "refused"],
          summary + [("total", args.commit, *total)])
    write(os.path.join(args.out, "refused.tsv"), ["reason", "files"], sorted(refused.items(), key=lambda kv: (-kv[1], kv[0])))
    write(os.path.join(args.out, "rules.tsv"), ["rule", "known", "hunks", "files", "first", "example"],
          [(name, "yes" if set(name.split("+")) <= KNOWN else "no", len(found), len({f for f, _, _ in found}), found[0][0], example(found[0][1], found[0][2]))
           for name, found in sorted(by_rule.items(), key=lambda kv: (-len(kv[1]), kv[0]))])
    write(os.path.join(args.out, "files.tsv"), ["file", "result"], file_rows)
    print("migrated", total[0], "converted back", total[1], "identical", total[2], "known only", total[3], "other", total[4], "refused", total[5])


if __name__ == "__main__":
    main()
