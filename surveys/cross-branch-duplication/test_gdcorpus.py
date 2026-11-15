"""Checks for the manifest rules that can silently bias every survey."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import gdcorpus as G

ROOT = Path(__file__).resolve().parents[2]


class ManifestRules(unittest.TestCase):
    def setUp(self):
        (ROOT / 'work').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'work')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'sample'
        self.repo.mkdir()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def test_excludes_and_own_addons(self):
        for f in ('main.gd', 'generated/file.gd', 'auto.gd', 'addons/own/a.gd', 'addons/vendor/b.gd'):
            self.write(f, 'var x = 1\n')
        metadata = {'sample': {'exclude': ['generated/**', 'auto.gd'], 'first_party_addons': ['own']}}
        with patch.object(G, 'REPO_METADATA', metadata):
            repo = G.Repo(self.root, 'sample', 'game')
        self.assertTrue(repo.first_party('main.gd'))
        self.assertTrue(repo.first_party('addons/own/a.gd'))
        for path in ('generated/file.gd', 'auto.gd', 'addons/vendor/b.gd'):
            self.assertFalse(repo.first_party(path))

    def test_cap_samples_whole_files_and_keeps_resolution_inputs(self):
        self.write('huge.gd', 'var x = 1\n' * 11)
        for i in range(8):
            self.write(f'{i}.gd', 'var x = 1\n' * 3)
        data = {'line_cap': 10, 'line_cap_seed': 20261115}
        with patch.object(G, 'MANIFEST_DATA', data):
            a = G.Repo(self.root, 'sample', 'game')
            b = G.Repo(self.root, 'sample', 'game')
        self.assertEqual(a._sample, b._sample)
        self.assertEqual(len(a._sample), 3)
        self.assertNotIn('huge.gd', a._sample)
        self.assertIn('huge.gd', a.files)
        self.assertTrue(a.source_first_party('huge.gd'))
        self.assertLessEqual(sum(len(a.read(f).splitlines()) for f in a._sample), 10)

    def test_v1_has_no_sampling(self):
        self.write('main.gd', 'var x = 1\n' * 21000)
        with patch.object(G, 'MANIFEST_DATA', {'version': 1}):
            repo = G.Repo(self.root, 'sample', 'game')
        self.assertIsNone(repo._sample)
        self.assertTrue(repo.first_party('main.gd'))

    def test_reference_and_human_filters(self):
        manifest = self.root / 'manifest.json'
        repos = [{'name': n, 'url': 'https://example.test/' + n, 'commit': 'a' * 40, 'group': 'game',
                  'weight': weight, 'authorship': author}
                 for n, weight, author in [('human', 'normal', 'human'), ('mixed', 'normal', 'mixed'),
                                            ('Ring', 'reference', 'human')]]
        manifest.write_text(json.dumps({'repos': repos}), encoding='utf-8')
        cmd = [sys.executable, '-c', 'import gdcorpus; print([r[0] for r in gdcorpus.REPOS])']
        env = dict(os.environ, CORPUS_MANIFEST=str(manifest))
        env.pop('CORPUS_INCLUDE_REFERENCE', None)
        env.pop('CORPUS_AUTHORSHIP', None)
        cwd = Path(__file__).parent
        self.assertEqual(subprocess.check_output(cmd, cwd=cwd, env=env, text=True).strip(), "['human', 'mixed']")
        env['CORPUS_AUTHORSHIP'] = 'human'
        self.assertEqual(subprocess.check_output(cmd, cwd=cwd, env=env, text=True).strip(), "['human']")


if __name__ == '__main__':
    unittest.main()
