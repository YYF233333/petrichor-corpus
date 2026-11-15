"""Rerun automated surveys on a new corpus, keeping v1 and hand labels intact.

    python rerun.py v2 [survey ...] [--human-only]

Raw extractions stay under work/rerun/. Only derived results go to results-v2/
(results-v2-human/ for the human subset). Existing differing results are refused.
Saved .txt reports strip trailing ASCII spaces and tabs; numeric content stays intact.
GODOT_REFERENCE selects the pinned class-reference directory, as in reproduce.py.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import reproduce as R
from fetch import head

ROOT = Path(__file__).resolve().parent
ALL_STEPS = dict(R.STEPS)
ALL_STEPS['paper-migration'] = [
    ('paper-migration/stats.py', [R.CORPUS + '/Starter-Kit-FPS', R.CORPUS + '/Ring'], 'stats.txt',
     [('stats.txt', 'paper-migration/results/stats.txt')]),
    ('paper-migration/idioms.py', [R.CORPUS], 'idioms.txt', [('idioms.txt', 'paper-migration/results/idioms.txt')]),
]
ALL_STEPS['paper-migration-2'] = [
    ('paper-migration-2/stats.py', [R.CORPUS + '/Starter-Kit-FPS', R.CORPUS + '/Ring'], 'stats.txt',
     [('stats.txt', 'paper-migration-2/results/stats.txt')]),
]
ALL_STEPS['v2-rerun'] = [
    ('v2-rerun/audit.py', [R.CORPUS], 'sampling.json', [('sampling.json', 'v2-rerun/results/sampling.json')]),
]


def steps(survey):
    result = []
    for script, args, stdout, compare in ALL_STEPS[survey]:
        compare = list(compare)
        if script.endswith('/ring_check.py'):
            continue  # Ring is a reference, outside the headline corpus.
        if script == 'property-accessors/count.py':
            continue
        args = list(args)
        if script == 'corpus-counts/counts.py' and '--metrics' not in args:
            args += ['--metrics', '{out}/metrics.json']
            compare = compare + [('metrics.json', 'corpus-counts/results/metrics.json')]
        if script == 'cross-branch-duplication/report.py':
            args += ['--labels', '{out}/no-v1-labels.csv']
        result.append((script, args, stdout, compare))
    if survey == 'scene-structures':
        result[-1][3].extend((f, 'scene-structures/results/' + f) for f in ('scripts.csv', 'uses.csv', 'contexts.csv'))
    if survey == 'cross-branch-duplication':
        result[-1][3].append(('groups_exact.csv', 'cross-branch-duplication/out/groups_exact.csv'))
    return result


def publish(pairs, suffix):
    destinations = {}
    for src, committed in pairs:
        if Path(src).suffix == '.txt':
            # Formatting belongs to the new-version runner, not the v1 comparator.
            data = Path(src).read_bytes().replace(b'\r\n', b'\n')
            Path(src).write_bytes(b'\n'.join(line.rstrip(b' \t') for line in data.split(b'\n')))
        original = Path(committed)
        # out_k3 and out_k8 become subdirectories of the new results directory.
        part = original.parts[1]
        relative = Path('k' + part.split('_k')[1]) / original.name if part.startswith('out_k') else Path(original.name)
        dest = ROOT / 'surveys' / original.parts[0] / ('results-' + suffix) / relative
        if dest in destinations:
            raise ValueError(f'duplicate result destination: {dest}')
        destinations[dest] = src
    # Check everything before creating any new result files.
    for dest, src in destinations.items():
        if dest.exists() and R.read(dest) != R.read(src):
            raise RuntimeError(f'{dest} differs; investigate before updating it. New output: {src}')
    for dest, src in destinations.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(Path(src).read_bytes())


def run(version, manifest, corpus, want, human=False, save=True):
    data = json.loads(Path(manifest).read_text(encoding='utf-8'))
    if data.get('version') == 1:
        raise ValueError('Use reproduce.py for v1; this runner never replaces v1 results.')
    missing = [r['name'] for r in data['repos'] if head(os.path.join(corpus, r['name'])) != r['commit']]
    if missing:
        raise RuntimeError(f'{len(missing)} missing or unpinned clones; run python fetch.py {version}. '
                           f'First: {", ".join(missing[:5])}')
    suffix = version + ('-human' if human else '')
    base = ROOT / 'work' / 'rerun' / suffix
    base.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CORPUS_MANIFEST=str(Path(manifest).resolve()), PYTHONIOENCODING='utf-8', PYTHONHASHSEED='0')
    env.pop('CORPUS_INCLUDE_REFERENCE', None)
    env.pop('CORPUS_AUTHORSHIP', None)
    if human:
        env['CORPUS_AUTHORSHIP'] = 'human'
    pairs = []
    for survey in want:
        out = base / survey
        out.mkdir(exist_ok=True)
        env["SURVEY_METRICS_DIR"] = str(out)
        for script, args, stdout, compare in steps(survey):
            cmd = [sys.executable, str(ROOT / 'surveys' / script)] + [
                a.replace('{out}', str(out)).replace(R.CORPUS, str(corpus)) for a in args]
            print('+', ' '.join(cmd), flush=True)
            with open(out / stdout if stdout else os.devnull, 'wb') as fh:
                subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh, check=True)
            pairs.extend((out / produced, committed) for produced, committed in compare)
    if save:
        publish(pairs, suffix)
    return base


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('surveys', nargs='*')
    ap.add_argument('--human-only', action='store_true')
    args = ap.parse_args()
    if any(s not in ALL_STEPS for s in args.surveys):
        ap.error('unknown survey; choose from: ' + ', '.join(ALL_STEPS))
    run(args.version, ROOT / 'corpus' / (args.version + '.json'), ROOT / 'corpus' / args.version,
        args.surveys or list(ALL_STEPS), args.human_only)


if __name__ == '__main__':
    main()
