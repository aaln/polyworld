import copy
import json
from pathlib import Path
import tempfile
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

import researcher as r


class ResearcherTests(unittest.TestCase):
    def matrix(self):
        arms, results = [], {}
        def add(kind, role, color, group, wins=32):
            key = '/'.join((kind, group, role, color))
            arms.append(dict(key=key, kind=kind, role=role, color=color, comparison=group))
            results[key] = dict(games=40, wins=wins)
        for col in ('red', 'blue'):
            add('self', 'candidate', col, 'parent', 24)
            for role in ('candidate', 'parent'):
                for i in range(5): add('field', role, col, str(i))
                for i in range(2): add('archive', role, col, str(i))
                for i in range(3): add('mixed', role, col, str(i))
        return {'arms': arms}, results

    def test_color_regression_cannot_hide_in_total(self):
        p, results = self.matrix()
        self.assertTrue(r.judge(p, results)['passed'])
        results['self/parent/candidate/red']['wins'] = 23
        results['self/parent/candidate/blue']['wins'] = 40
        self.assertFalse(r.judge(p, results)['passed'])

    def test_draws_and_field_regressions_reject(self):
        p, results = self.matrix()
        results['self/parent/candidate/red']['wins'] = 0
        self.assertFalse(r.judge(p, results)['passed'])
        p, results = self.matrix()
        results['field/0/candidate/blue']['wins'] = 31
        self.assertFalse(r.judge(p, results)['passed'])

    def test_missing_mixed_color_is_rejected(self):
        p, results = self.matrix()
        p['arms'] = [a for a in p['arms'] if not (a['kind'] == 'mixed' and a['color'] == 'red')]
        self.assertFalse(r.judge(p, results)['passed'])

    def test_pending_games_cannot_qualify(self):
        p, results = self.matrix()
        results['self/parent/candidate/red'] = dict(games=39, wins=39)
        self.assertFalse(r.judge(p, results)['passed'])

    def test_budget_retry_is_idempotent_and_body_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r.write(root/'config.json', dict(tooling=tmp, target={'coworld_id':'test'},
                    game_config={}, daily_episode_limit=80, cycle_episode_limit=40))
            body = dict(idempotency_key='one', num_episodes=40, target={'coworld_id':'test'}, game_config_overrides={})
            one = r.reserve(root, body, root/'xp', 'cycle1')
            self.assertEqual(one, r.reserve(root, body, root/'xp', 'cycle2'))
            self.assertEqual(len(r.read(root/'xp-ledger.json')), 1)
            with self.assertRaises(ValueError): r.reserve(root, body | {'notes':'changed'}, root/'xp', 'cycle1')
            with self.assertRaises(ValueError): r.reserve(root, body | {'idempotency_key':'two'}, root/'two', 'cycle1')
            r.reserve(root, body | {'idempotency_key':'two'}, root/'two', 'cycle2')
            with self.assertRaises(ValueError): r.reserve(root, body | {'idempotency_key':'three'}, root/'three', 'cycle3')

    def test_lock_prevents_second_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            with r.lock(Path(tmp)/'lock'):
                with self.assertRaises(BlockingIOError):
                    with r.lock(Path(tmp)/'lock', blocking=False): pass

    def test_one_day_budget_override_expires_without_changing_other_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r.write(root/'config.json', dict(tooling=tmp, daily_episode_limit=10000,
                cycle_episode_limit=400, max_parallel_xp=3,
                daily_episode_limit_override={'utc_day':'2026-09-20', 'normal_limit':1600}))
            with patch.object(r, 'now', return_value='2026-09-20T23:59:59Z'):
                self.assertEqual(r.config(root)['daily_episode_limit'], 10000)
            with patch.object(r, 'now', return_value='2026-09-21T00:00:00Z'):
                current = r.config(root)
                self.assertEqual(current['daily_episode_limit'], 1600)
                self.assertEqual(current['cycle_episode_limit'], 400)
                self.assertEqual(current['max_parallel_xp'], 3)

    def test_redacted_remote_hash_requires_exact_existing_version(self):
        api = MagicMock()
        api.get.return_value.json.return_value = {'player_file_content_hash':None}
        api.post.return_value.json.return_value = {'existing_policy_version':{'id':'expected'}, 'upload_url':None}
        proof = r.verify_remote_source(api, {'content_hash':'abc'}, 'expected')
        self.assertEqual(proof['source_sha256'], 'abc')
        api.post.return_value.json.return_value = {'existing_policy_version':None, 'upload_url':'not-printed'}
        with self.assertRaises(ValueError): r.verify_remote_source(api, {'content_hash':'abc'}, 'expected')
        api.post.return_value.json.return_value = {'existing_policy_version':{'id':'different'}, 'upload_url':None}
        with self.assertRaises(ValueError): r.verify_remote_source(api, {'content_hash':'abc'}, 'expected')

    def test_snapshot_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'policy.bas').write_text('original')
            r.write(p/'snapshot.json', {'files': {'policy.bas': r.sha(p/'policy.bas')}})
            r.verify_snapshot(p)
            (p/'policy.bas').write_text('edited')
            with self.assertRaises(ValueError): r.verify_snapshot(p)

    def test_atomic_write_survives_interruption_before_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'state.json'
            r.write(p, {'accepted': 'old'})
            with patch.object(r.os, 'replace', side_effect=OSError('interrupted')):
                with self.assertRaises(OSError): r.write(p, {'accepted':'new'})
            self.assertEqual(r.read(p)['accepted'], 'old')

    def test_supervisor_bounds_a_stalled_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake = root/'fake-codex'
            fake.write_text('#!' + sys.executable + '\nimport time\ntime.sleep(60)\n')
            fake.chmod(0o755)
            (root/'PROMPT.md').write_text('test')
            r.write(root/'config.json', dict(tooling=tmp, codex=str(fake), workspace=tmp,
                    dependencies=tmp, cycle_timeout_seconds=0.05, between_cycles_seconds=1,
                    daily_episode_limit=80))
            sleep = time.sleep
            with patch.object(r.time, 'sleep', side_effect=lambda _: sleep(0.01)):
                r.run(root, once=True)
            completed = list((root/'cycles').glob('*/exit.json'))
            self.assertEqual(len(completed), 1)
            self.assertLess(r.read(completed[0])['returncode'], 0)
            self.assertEqual(r.read(root/'service.json')['state'], 'between_cycles')


if __name__ == '__main__': unittest.main()
