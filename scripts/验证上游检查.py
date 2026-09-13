"""上游检查的离线回归：真实来源记录 + 隔离副本 + GitHub 响应夹具。"""

import contextlib
import copy
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('upstream_check', Path(__file__).with_name('检查上游技能.py'))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class UpstreamCheckTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((check.PLUGIN_ROOT / '上游来源.json').read_text(encoding='utf-8'))
        self.tree = {'truncated': False, 'tree': [
            {'path': entry['upstreamPath'], 'type': 'blob', 'mode': '100644', 'sha': entry['gitBlobSha1']}
            for entry in self.lock['files']
        ]}

    def fetch(self, url):
        if '/commits/' in url:
            return {'sha': 'a' * 40}
        self.assertIn('/git/trees/' + 'a' * 40, url)
        return self.tree

    def test_local_snapshot_and_single(self):
        check.validate_local(check.PLUGIN_ROOT, self.lock)

    def test_unrelated_commit_is_not_an_update(self):
        self.tree['tree'].append({'path': 'README.md', 'type': 'blob', 'mode': '100644', 'sha': 'b' * 40})
        result = check.check_upstream(self.lock, 'main', self.fetch)
        self.assertEqual(result['status'], 'up_to_date')
        self.assertEqual(result['changes'], [])

    def test_entry_and_rule_changes(self):
        for index in (0, 1):
            with self.subTest(index=index):
                original = self.tree['tree'][index]['sha']
                self.tree['tree'][index]['sha'] = 'b' * 40
                result = check.check_upstream(self.lock, 'main', self.fetch)
                self.assertEqual(result['changes'], [{'path': self.lock['files'][index]['upstreamPath'], 'status': 'modified'}])
                self.tree['tree'][index]['sha'] = original

    def test_added_reference_removed_entry_and_license_change(self):
        removed = self.tree['tree'].pop(0)['path']
        added = 'skills/productivity/grilling/references/new.md'
        self.tree['tree'].append({'path': added, 'type': 'blob', 'mode': '100644', 'sha': 'b' * 40})
        next(entry for entry in self.tree['tree'] if entry['path'] == 'LICENSE')['sha'] = 'c' * 40
        changes = check.check_upstream(self.lock, 'main', self.fetch)['changes']
        self.assertEqual({(entry['path'], entry['status']) for entry in changes}, {(removed, 'removed'), (added, 'added'), ('LICENSE', 'modified')})

    def test_truncated_tree_fails(self):
        self.tree['truncated'] = True
        with self.assertRaisesRegex(ValueError, '不完整'):
            check.check_upstream(self.lock, 'main', self.fetch)

    def test_upstream_symlink_requires_review(self):
        self.tree['tree'][0]['mode'] = '120000'
        with self.assertRaisesRegex(ValueError, '文件类型'):
            check.check_upstream(self.lock, 'main', self.fetch)

    def test_corrupt_snapshot_and_single_fail(self):
        for relative in (self.lock['files'][0]['localPath'], self.lock['single']['localPath']):
            with self.subTest(path=relative), tempfile.TemporaryDirectory(prefix='Hexgen-GrillCheck-') as directory:
                isolated = Path(directory) / 'plugin'
                shutil.copytree(check.PLUGIN_ROOT, isolated)
                with (isolated / relative).open('ab') as stream:
                    stream.write(b'changed')
                with self.assertRaisesRegex(ValueError, '改变|不一致'):
                    check.validate_local(isolated, self.lock)

    def test_missing_snapshot_record_fails(self):
        self.lock['files'].pop(0)
        with self.assertRaisesRegex(ValueError, '缺少'):
            check.validate_local(check.PLUGIN_ROOT, self.lock)

    def test_path_escape_fails(self):
        changed = copy.deepcopy(self.lock)
        changed['files'][0]['localPath'] = '../outside.md'
        with self.assertRaisesRegex(ValueError, '非法'):
            check.validate_local(check.PLUGIN_ROOT, changed)

    def test_cli_network_failure_is_error(self):
        output = io.StringIO()
        with patch.object(check, 'check_upstream', side_effect=OSError('network unavailable')), contextlib.redirect_stdout(output):
            result = check.main(['--json'])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'error')

    def test_cli_changed_exit_code(self):
        output = io.StringIO()
        with patch.object(check, 'check_upstream', return_value={'status': 'update_available', 'changes': []}), contextlib.redirect_stdout(output):
            result = check.main(['--json'])
        self.assertEqual(result, 2)

    def test_offline_does_not_access_network(self):
        with patch.object(check, 'check_upstream') as network, contextlib.redirect_stdout(io.StringIO()):
            result = check.main(['--offline', '--json'])
        self.assertEqual(result, 0)
        network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
