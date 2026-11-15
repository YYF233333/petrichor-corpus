"""Repository incidence for three existing token predicates, without scene work.

Usage: python incidence.py CORPUS EXTENSION_API
Matches remaining.py, remaining2.py and names.py; comparison checks the totals.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, '..', 'cross-branch-duplication'))
sys.path.insert(0, os.path.join(HERE, '..', 'by-name-access'))
import gdcorpus as G
import names as N


def main():
    corpus, api_path = sys.argv[1:]
    with open(api_path, encoding='utf-8') as fh:
        api = json.load(fh)
    globals_ = {c['name'] for c in api.get('global_constants', [])}
    for enum in api.get('global_enums', []):
        globals_.update(v['name'] for v in enum.get('values', []))
    constants = set()
    for cls in api['classes']:
        constants.update(c['name'] for c in cls.get('constants', []) or [])
        for enum in cls.get('enums', []) or []:
            constants.update(v['name'] for v in enum.get('values', []))
    constants -= globals_
    result = {}
    for name, _, _, group in G.REPOS:
        repo = G.Repo(corpus, name, group)
        counter = collections.Counter()
        for path in repo.files:
            if not path.endswith('.gd') or not repo.first_party(path):
                continue
            ts = [t for t in G.tokenize(repo.read(path)) if t.k != 'NL']
            declared = {ts[i+1].v for i in range(len(ts)-1) if ts[i].k == 'ID'
                        and ts[i].v in ('var', 'const', 'func', 'signal', 'enum', 'class') and ts[i+1].k == 'ID'}
            bare = iterator = 0
            for i, t in enumerate(ts):
                prev = ts[i-1] if i else None
                nxt = ts[i+1] if i+1 < len(ts) else None
                if t.k == 'ID' and t.v in constants and t.v not in declared and not (prev and prev.v == '.'):
                    bare += 1
                if t.k == 'ID' and t.v == 'func' and (prev is None or prev.line != t.line or prev.v == 'static' or prev.k == 'AN'):
                    iterator += bool(nxt and nxt.v == '_iter_init')
                if t.k != 'ID' or not nxt or nxt.k != 'OP' or nxt.v != '(' or (prev and prev.k == 'ID' and prev.v == 'func'):
                    continue
                specs = N.POSITIONS.get(t.v, [])
                if not specs:
                    continue
                args, _ = N.call_args(ts, i+1)
                recv = N.receiver(ts, i)
                for index, kind, target, role in specs:
                    if index >= len(args) or len(args[index]) != 1 or args[index][0].k != 'STR' or target is None:
                        continue
                    arg = args[target] if isinstance(target, int) and target < len(args) else []
                    on_self = recv in ('none', 'self') if target == 'recv' else len(arg) == 1 and arg[0].k == 'ID' and arg[0].v == 'self'
                    counter['self_code_names'] += bool(on_self)
            counter['bare_files'] += bool(bare)
            counter['bare_uses'] += bare
            counter['iterator_files'] += bool(iterator)
            counter['iterator_defs'] += iterator
        result[name] = counter
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
