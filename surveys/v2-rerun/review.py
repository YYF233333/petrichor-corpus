"""Draw fixed, bounded samples of the count premises that changed on v2.

    CORPUS_MANIFEST=corpus/v2.json python surveys/v2-rerun/review.py
    python surveys/v2-rerun/review.py --dump ITEM [START [END]]

The JSON stores locations and later human verdicts, never full corpus files.
"""
import collections
import csv
import json
import os
from pathlib import Path
import random
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'corpus-counts'))
sys.path.insert(0, str(HERE.parent / 'cross-branch-duplication'))
import counts as C
import gdcorpus as G

SEED = 20261115
OUTPUT = HERE / 'reviews.json'


def group_site(row):
    member = row['members'].split(';')[0]
    match = re.match(r'(.+?\.gd).*?:(\d+)-', member)
    if match is None:
        raise ValueError(member)
    return f"{row['repo']}/{match[1]}:{match[2]} {row['gid']}"


def draw(populations):
    manifest = json.loads((ROOT / 'corpus/v2.json').read_text(encoding='utf-8'))
    metadata = {r['name']: r for r in manifest['repos']}
    result = {}
    for key, population in populations.items():
        population = sorted(set(population))
        chosen = random.Random(SEED).sample(population, min(50, len(population)))
        records = []
        for site in chosen:
            match = re.match(r'([^/]+)/(.+?):(\d+)', site)
            if not match:
                raise ValueError(site)
            name, path, line = match.groups()
            repo = metadata[name]
            records.append({'site': site, 'repo': name, 'file': path, 'line': int(line),
                            'url': repo['url'].removesuffix('.git') + '/blob/' + repo['commit'] + '/' + path + '#L' + line,
                            'authorship': repo['authorship'], 'verdict': None, 'note': ''})
        result[key] = {'population': len(population), 'seed': SEED, 'sample': records}
    return result


def main():
    if sys.argv[1:2] == ['--dump']:
        data = json.loads(OUTPUT.read_text(encoding='utf-8'))
        start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        end = int(sys.argv[4]) if len(sys.argv) > 4 else start + 10
        for i, rec in enumerate(data[sys.argv[2]]['sample'][start:end], start):
            print(f'\n=== {i} {rec["site"]}')
            lines = (ROOT / 'corpus/v2' / rec['repo'] / rec['file']).read_text(encoding='utf-8', errors='replace').splitlines()
            for j in range(max(0, rec['line'] - 7), min(len(lines), rec['line'] + 19)):
                print(f'{j+1:5} {lines[j]}')
        return
    metrics = json.loads((ROOT / 'surveys/corpus-counts/results-v2/metrics.json').read_text(encoding='utf-8'))
    populations = {key: metrics['sites'].get(key, []) for key in
                   ('_get or _set', 'pop_at', 'free() on self', 'set_script on self',
                    '.free() in an _on_ method', 'a keyword of this language as a name',
                    '### block above a declaration', 'string with a line break')}
    populations.update(lambda_capture_direct=[], lambda_default=[])
    for name, _, _, group in G.REPOS:
        repo = G.Repo(ROOT / 'corpus/v2', name, group)
        for path in repo.files:
            if not path.endswith('.gd') or not repo.first_party(path):
                continue
            ts = [t for t in G.tokenize(repo.read(path)) if t.k != 'NL']
            method = ('', 0, 0, 0)
            for i, t in enumerate(ts):
                if t.k == 'ID' and t.v == 'func' and (
                        i == 0 or ts[i - 1].line != t.line or ts[i - 1].v == 'static' or ts[i - 1].k == 'AN'):
                    if i + 1 < len(ts) and ts[i + 1].k == 'ID':
                        method = (ts[i + 1].v, *C.func_body(ts, i), i)
                elif t.k == 'ID' and t.v == 'func' and ts[i - 1].v in C.LAMBDA_PREV:
                    counter = collections.Counter()
                    s, e = C.func_body(ts, i)
                    C.lambda_captures(ts, i, s, e, method, counter, ('', []))
                    site = f'{name}/{path}:{t.line}'
                    if counter['lambda_capture_assign']:
                        populations['lambda_capture_direct'].append(site)
                    if counter['lambda_default']:
                        populations['lambda_default'].append(site)
    result = draw(populations)
    with open(ROOT / 'work/rerun/v2/await-signal-results/awaits.json', encoding='utf-8') as fh:
        awaits = json.load(fh)
    result.update(draw({'used_multi_signals': [r['key'] for r in awaits if r['category'] != 'vendored'
                       and r['kind'] == 'signal' and r['used'] and (r.get('arity') or 0) >= 2]}))
    with open(ROOT / 'work/rerun/v2/property-accessors/properties.json', encoding='utf-8') as fh:
        properties = json.load(fh)
    result.update(draw({'nontrivial_getters': [p['id'] for p in properties if p['scope'] == 'first-party'
                       and p['getter'] and not p['getter'].get('trivial')]}))
    base = ROOT / 'surveys/corpus-counts/results-v2'
    strings = (base / 'string_index.txt').read_text(encoding='utf-8')
    weak = (base / 'weak_refs.txt').read_text(encoding='utf-8')
    result.update(draw({'string_index_candidates': re.findall(r'^([^/ ]+/.+?:\d+) \(', strings, re.M),
                        'weakref_calls': re.findall(r'^([^/ ]+/.+?:\d+) \([^)]*\): weakref\(', weak, re.M)}))
    with open(ROOT / 'surveys/scene-structures/results-v2/uses.csv', encoding='utf-8') as fh:
        uses = list(csv.DictReader(fh))
    result.update(draw({'scene_type_conflicts': [f"{r['repo']}/{r['script']}:{r['line']} {r['kind']}:{r['path']}"
                       for r in uses if r['status'].startswith('differs')]}))
    with open(ROOT / 'surveys/cross-branch-duplication/results-v2/groups_exact.csv', encoding='utf-8') as fh:
        groups = list(csv.DictReader(fh))
    result.update(draw({'game_clone_groups': [group_site(r)
                       for r in groups if r['group'] == 'games']}))
    if '--check' in sys.argv:
        previous = json.loads(OUTPUT.read_text(encoding='utf-8'))
        for key, value in result.items():
            assert value['population'] == previous[key]['population'], key
            assert [r['site'] for r in value['sample']] == [r['site'] for r in previous[key]['sample']], key
            assert all(r['verdict'] for r in previous[key]['sample']), key
        print('all sample locations, seeds and verdict coverage verified')
        return
    if OUTPUT.exists():
        raise RuntimeError('Review data already exists; preserve its verdicts.')
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print({key: (value['population'], len(value['sample'])) for key, value in result.items()})


if __name__ == '__main__':
    main()
