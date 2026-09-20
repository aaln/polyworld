import unittest
from unittest.mock import patch

import httpx

from hosted_wave import ResilientClient


class RetryTests(unittest.TestCase):
    def exercise(self, method, url, body=None):
        calls = []
        def handle(request):
            calls.append(request)
            if len(calls) == 1:
                raise httpx.ConnectError('temporary DNS failure', request=request)
            return httpx.Response(200, json={'ok': True})
        with ResilientClient(base_url='https://example.invalid', transport=httpx.MockTransport(handle)) as c:
            with patch('hosted_wave.time.sleep'):
                response = c.request(method, url, json=body)
        return len(calls), response.status_code

    def test_reads_retry(self):
        self.assertEqual(self.exercise('GET', '/episodes'), (2, 200))

    def test_only_idempotent_experience_posts_retry(self):
        self.assertEqual(self.exercise('POST', '/v2/experience-requests', {'idempotency_key': 'fixed-key'}), (2, 200))
        with self.assertRaises(httpx.ConnectError):
            self.exercise('POST', '/v2/experience-requests', {})
        with self.assertRaises(httpx.ConnectError):
            self.exercise('POST', '/v2/league-submissions', {'idempotency_key': 'not-supported'})

    def test_delayed_core_artifact_retries_until_published(self):
        calls = []
        def handle(request):
            calls.append(request)
            return httpx.Response(404 if len(calls) < 3 else 200, content=b'logs')
        with ResilientClient(base_url='https://example.invalid', transport=httpx.MockTransport(handle)) as c:
            with patch('hosted_wave.time.sleep'):
                response = c.get('/v2/episode-requests/ereq_test/artifacts/logs')
        self.assertEqual((len(calls), response.status_code), (3, 200))

    def test_permanently_missing_artifact_remains_an_error(self):
        calls = []
        def handle(request):
            calls.append(request)
            return httpx.Response(404)
        with ResilientClient(base_url='https://example.invalid', transport=httpx.MockTransport(handle)) as c:
            with patch('hosted_wave.time.sleep'):
                response = c.get('/v2/episode-requests/ereq_test/artifacts/replay')
        self.assertEqual(len(calls), 6)
        with self.assertRaises(httpx.HTTPStatusError):
            response.raise_for_status()

    def test_optional_policy_logs_and_unrelated404_do_not_retry(self):
        for path in ['/v2/missing', '/v2/episode-requests/ereq_test/version/policy-logs/0']:
            calls = []
            def handle(request):
                calls.append(request)
                return httpx.Response(404)
            with ResilientClient(base_url='https://example.invalid', transport=httpx.MockTransport(handle)) as c:
                with patch('hosted_wave.time.sleep'):
                    response = c.get(path)
            self.assertEqual((len(calls), response.status_code), (1, 404))


if __name__ == '__main__': unittest.main()
