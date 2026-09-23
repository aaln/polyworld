import contextlib
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import counterfactual_journal as journal


@pytest.fixture
def fixture(tmp_path):
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    def read(path): return json.loads(path.read_text())
    def freeze(path, data):
        if path.exists(): assert read(path) == data
        else: write(path, data)
    cfg = {'daily_episode_limit': 100000, 'cycle_episode_limit': 400, 'max_parallel_xp': 3}
    h = SimpleNamespace(CAMPAIGN=tmp_path, STUDY=tmp_path, CYCLE='test', GAME='current',
        VERSION='v', COMMIT='commit', read=read, write=write, freeze=freeze, live=lambda c: None)
    h.research = SimpleNamespace(config=lambda p: cfg, lock=lambda p: contextlib.nullcontext(),
        now=lambda: '2026-09-23T00:00:00Z', write=write,
        fingerprint=lambda b: hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest())
    write(tmp_path / 'xp-ledger.json', {}); write(tmp_path / 'service.json', {'state': 'paused'})
    body = {'candidate_policy_version_id': 'candidate', 'baseline_policy_version_id': 'baseline',
            'source': 'experience_request', 'n': 5, 'idempotency_key': 'stable-key'}
    ready = {'baseline_version': 'baseline', 'coworld_id': 'current', 'complete': True,
             'episode_ids': ['episode'+str(i) for i in range(5)]}
    schema = {'components': {'schemas': {'CreateCounterfactualEvalBody': {'type': 'object'}}}}
    calls = []
    def post(url, json):
        assert h.read(tmp_path / 'xp-ledger.json')['stable-key']['episodes'] == 5
        calls.append(json.copy())
        return SimpleNamespace(status_code=200, raise_for_status=lambda: None,
                               json=lambda: {'id': 'cf-test', 'idempotency_key': json['idempotency_key']})
    client = SimpleNamespace(post=post)
    return h, cfg, body, ready, schema, client, calls


@pytest.mark.parametrize('n', [0, 101, None, True, 5.0])
def test_bad_count_never_reserves_or_posts(fixture, n):
    h, cfg, body, ready, schema, client, calls = fixture
    body['n'] = n
    with pytest.raises(AssertionError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
    assert not calls and h.read(h.CAMPAIGN/'xp-ledger.json') == {}


def test_timeout_retry_preserves_key_and_single_reservation(fixture):
    h, cfg, body, ready, schema, client, calls = fixture
    original = client.post
    def timeout(url, json): original(url, json); raise TimeoutError()
    with patch.object(journal, 'active_requests', return_value=0):
        client.post = timeout
        with pytest.raises(TimeoutError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
        client.post = original
        journal.create(client, h, body, h.STUDY/'out', schema, ready)
        journal.create(client, h, body, h.STUDY/'out', schema, ready)
    assert calls == [body, body]
    assert sum(e['episodes'] for e in h.read(h.CAMPAIGN/'xp-ledger.json').values()) == 5


def test_budget_and_concurrency_fail_before_post(fixture):
    h, cfg, body, ready, schema, client, calls = fixture
    with patch.object(journal, 'active_requests', return_value=3):
        with pytest.raises(AssertionError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
    cfg['cycle_episode_limit'] = 4
    with patch.object(journal, 'active_requests', return_value=0):
        with pytest.raises(AssertionError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
    assert not calls and h.read(h.CAMPAIGN/'xp-ledger.json') == {}


def test_old_release_or_duplicate_pool_is_rejected(fixture):
    h, cfg, body, ready, schema, client, calls = fixture
    ready['coworld_id'] = 'old'
    with pytest.raises(AssertionError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
    ready['coworld_id'] = 'current'; ready['episode_ids'][1] = ready['episode_ids'][0]
    with pytest.raises(AssertionError): journal.create(client, h, body, h.STUDY/'out', schema, ready)
    assert not calls


def test_resume_accepts_reordered_same_pool_but_rejects_replacement(fixture):
    h, cfg, body, ready, schema, client, calls = fixture
    out=h.STUDY/'out'
    with patch.object(journal,'active_requests',return_value=0):
        journal.create(client,h,body,out,schema,ready)
        frozen=h.read(out/'baseline-pool.json')
        ready['episode_ids'].reverse()
        journal.create(client,h,body,out,schema,ready)
        assert h.read(out/'baseline-pool.json')==frozen and len(calls)==1
        ready['episode_ids'][0]='replacement'
        with pytest.raises(AssertionError):journal.create(client,h,body,out,schema,ready)
    assert len(calls)==1
