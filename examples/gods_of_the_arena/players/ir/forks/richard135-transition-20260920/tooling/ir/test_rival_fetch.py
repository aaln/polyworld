from pathlib import Path
import tempfile
import unittest

import httpx

from hosted_wave import fetch


class RepeatedSubjectTests(unittest.TestCase):
    def test_team_fetch_preserves_each_own_slots_private_log(self):
        seen = []
        def handler(request):
            seen.append(request.url.path)
            return httpx.Response(200, content=b'test fixture', request=request)
        episode = {'id': 'fixture', 'status': 'completed', 'policy_version_ids': ['ours']*5 + ['rival']*5}
        with tempfile.TemporaryDirectory() as temp, httpx.Client(base_url='https://fixture.test', transport=httpx.MockTransport(handler)) as c:
            root = Path(temp)
            fetch(c, episode, root, 'ours', allow_repeated_subject=True)
            self.assertEqual(len(list((root/'fixture').glob('own-policy-slot-*.log'))), 5)
            self.assertTrue((root/'fixture/.done').exists())
            self.assertEqual([s for s in range(10) if any(p.endswith('/policy-logs/'+str(s)) for p in seen)], list(range(5)))

    def test_default_single_subject_study_still_rejects_duplicates(self):
        episode = {'id': 'fixture', 'status': 'completed', 'policy_version_ids': ['ours']*5 + ['rival']*5}
        with tempfile.TemporaryDirectory() as temp, httpx.Client(base_url='https://fixture.test', transport=httpx.MockTransport(lambda r:httpx.Response(200,content=b'fixture',request=r))) as c:
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                fetch(c, episode, Path(temp), 'ours')
            self.assertFalse((Path(temp)/'fixture/.done').exists())


if __name__ == '__main__':
    unittest.main()
