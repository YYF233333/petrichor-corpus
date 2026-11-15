"""Record exactly which files meet the manifest's ownership and sampling rules."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cross-branch-duplication'))
import gdcorpus as G


def main():
    records = []
    for name, url, commit, group in G.REPOS:
        repo = G.Repo(sys.argv[1], name, group)
        files = [f for f in repo.files if f.endswith('.gd') and repo.source_first_party(f)]
        lengths = {f: len(repo.read(f).splitlines()) for f in files}
        selected = [f for f in files if repo.first_party(f)]
        record = {'repo': name, 'url': url, 'commit': commit, 'group': group,
                  'authorship': repo.metadata.get('authorship'),
                  'eligible_files': len(files), 'eligible_lines': sum(lengths.values()),
                  'selected_files': len(selected), 'selected_lines': sum(lengths[f] for f in selected),
                  'files': selected}
        if G.MANIFEST_DATA.get('line_cap') is not None:
            assert record['selected_lines'] <= G.MANIFEST_DATA['line_cap'], name
            record['oversized_files'] = [f for f in files if lengths[f] > G.MANIFEST_DATA['line_cap']]
        records.append(record)
    print(json.dumps({'line_cap': G.MANIFEST_DATA.get('line_cap'),
                      'seed': G.MANIFEST_DATA.get('line_cap_seed'), 'repos': records}, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
