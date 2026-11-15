"""Numeric repository incidence for the extraction, without committing source excerpts.

Usage: python summarize.py EXTRACTION_DIR
"""
import collections
import json
import os
import sys


def main():
    with open(os.path.join(sys.argv[1], 'awaits.json'), encoding='utf-8') as fh:
        records = json.load(fh)
    repos = collections.defaultdict(collections.Counter)
    for rec in records:
        if rec['category'] == 'vendored':
            continue
        c = repos[rec['repo']]
        c['awaits'] += 1
        if rec['kind'] != 'signal':
            continue
        c['signal_awaits'] += 1
        c['used_signal_results'] += bool(rec['used'])
        if rec.get('arity') == 0 and rec['used']:
            c['used_zero_results'] += 1
        if (rec.get('arity') or 0) >= 2:
            c['multi_signal_awaits'] += 1
            c['used_multi_results'] += bool(rec['used'])
            if rec['used'] and rec.get('how') in ('receiver self', 'receiver typed'):
                c['typed_multi_results'] += 1
    all_counts = collections.Counter()
    for c in repos.values():
        all_counts.update(c)
    print(json.dumps({'repos': repos, 'all': all_counts}, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
