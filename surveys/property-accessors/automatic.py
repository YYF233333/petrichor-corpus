"""Report mechanical accessor counts without borrowing v1's manual labels.

Usage: python automatic.py EXTRACTION_DIR
The field-use split is a syntactic indicator, not a b/c classification.
"""
import collections
import json
import os
import re
import sys


def counts(props):
    result = collections.Counter(properties=len(props))
    for p in props:
        g, s = p['getter'], p['setter']
        result['getters'] += bool(g)
        result['setters'] += bool(s)
        result['exported'] += bool(p['export'])
        if g:
            result['trivial_getters'] += bool(g.get('trivial'))
            if not g.get('trivial'):
                result['nontrivial_field_getters'] += bool(g.get('uses_field'))
                result['nontrivial_other_getters'] += not g.get('uses_field')
        if s:
            result['await_setters'] += any(re.search(r'\bawait\b', stmt) for stmt in s.get('stmts', []))
            result['await_ready_setters'] += any(re.search(r'\bawait\s+(?:self\.)?ready\b', stmt)
                                                 for stmt in s.get('stmts', []))
            if p['export'] and s.get('touches'):
                result['exported_setters_with_touches'] += 1
                result['exported_setters_with_guard_syntax'] += bool(s.get('guards'))
    return dict(result)


def main():
    root = sys.argv[1]
    with open(os.path.join(root, 'properties.json'), encoding='utf-8') as fh:
        props = json.load(fh)
    with open(os.path.join(root, 'corpus.json'), encoding='utf-8') as fh:
        corpus = json.load(fh)
    fp = [p for p in props if p['scope'] == 'first-party']
    data = {'method': 'automatic; no manual getter, setter or guard verdicts',
            'all': counts(fp), 'repos': {name: counts([p for p in fp if p['repo'] == name]) for name in corpus}}
    data['all']['lines'] = sum(c['first-party']['lines'] for c in corpus.values())
    for name in corpus:
        data['repos'][name]['lines'] = corpus[name]['first-party']['lines']
    print(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
