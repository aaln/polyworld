"""Fresh-baseline paired pilot; journal every episode and leave league unchanged."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time
import httpx
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / 'weakhero20260923'))
import weak_hosted as previous
h, panel = previous.h, previous.panel
import counterfactual_journal

RAW = ROOT.parent / 'polyworld/tmp/gota-control-tactics61-20260923'
h.STUDY = panel.STUDY = RAW
h.CYCLE = 'interactive-control-tactics61-20260923'
h.GAME = 'cow_9ff2e22a-c7e3-4500-ae49-62f42970d699'
h.COMMIT = 'e42c4822f44e04726b09bb4ffe853152c7a18207'
h.VERSION = '2026.9.23.3'
BASE = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas'
CANDIDATE = RAW / 'control-tactics/policy.bas'


def upload(c, label, path, name, schema):
    data = path.read_bytes()
    out = RAW / 'uploads' / label
    body = {'name': name, 'content_hash': h.sha(data), 'size_bytes': len(data),
            'player_id': h.PLAYER, 'attributes': {}, 'tags': {'game': 'gods_of_the_arena'}}
    h.freeze(out / 'request.json', body)
    jsonschema.validate(body, schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out / 'version.json').exists():
        response = c.post('/stats/policies/files/upload', json=body)
        if response.status_code == 409:
            response = c.post('/stats/policies/files/complete', json=body)
            response.raise_for_status(); version = response.json()
        else:
            response.raise_for_status(); payload = response.json()
            version = payload.get('existing_policy_version')
            if version is None:
                response = httpx.put(payload['upload_url'], content=data,
                                    headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                response.raise_for_status()
                response = c.post('/stats/policies/files/complete', json=body)
                response.raise_for_status(); version = response.json()
        h.write(out / 'version.json', version)
    version = h.read(out / 'version.json')
    metadata = h.get(c, '/stats/policy-versions/' + version['id'])
    assert metadata['name'] == name
    h.write(out / 'metadata.json', metadata)
    log = ROOT / 'games/gods_of_the_arena/players/controltactics20260923/VERSION_LOG.md'
    text = log.read_text() if log.exists() else '# Control tactics research versions\n'
    if version['id'] not in text:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(text + '\n- ' + datetime.now(timezone.utc).isoformat() + ': ' + name + ':v' + str(version['version']) +
            ' (`' + version['id'] + '`), source `' + h.sha(data) + '`. ' +
            ('Exact incumbent clone, fresh current-release baseline history.' if label == 'baseline' else
             'Coordinated hero control targeting/timing before retreat, healing reserve and E unlock guard.') +
            ' BASIC file policy, engine61; local checks passed, hosted unvalidated; inert, no league selection.\n')
    return version['id']


def prepare():
    assert h.read(RAW / 'native-comparison.json')['passed']
    assert h.read(RAW / 'practice-comparison.json')['passed']
    with h.client() as c:
        game = h.live(c)
        h.freeze(RAW / 'canonical-game.json', game)
        schema = h.get(c, '/openapi.json'); h.freeze(RAW / 'openapi-preparation.json', schema)
        memberships = h.get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&active_only=true&limit=1000')
        h.freeze(RAW / 'memberships-preparation.json', memberships)
        field = {m['player']['name']: m['policy_version'] for m in memberships}
        versions = {'baseline': upload(c, 'baseline', BASE, 'wisp-cedar-61c2', schema),
                    'candidate': upload(c, 'candidate', CANDIDATE, 'morrow-ibis-61c2', schema)}
        config = {k: v for k, v in game['manifest']['variants'][0]['game_config'].items() if k not in ('players', 'tokens', 'seed')}
        allies = [field[n]['id'] for n in ['relh', 'Alex Smith', 'macromackie', 'Scott Smith']]
        enemies = [field[n]['id'] for n in ['Andre von Auto', 'richard', 'Jordan', 'Andre von Houck', 'daveey']]
        arms = []
        for side in [0, 1]:
            for ordinal in [0, 3]:
                team = list(allies); team.insert(ordinal, versions['baseline'])
                roster = team + enemies if side == 0 else enemies + team
                arm = {'side': side, 'ordinal': ordinal, 'slot': side*5+ordinal, 'roster': roster,
                       'cell': f'side{side}-seat{ordinal}', 'games': 20}
                body = {'idempotency_key': 'gota-cc61c2-baseline-' + arm['cell'],
                    'target': {'coworld_id': h.GAME, 'variant_id': 'competition'},
                    'game_config_overrides': config, 'num_episodes': 20,
                    'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(roster)],
                    'notes': 'Frozen baseline for paired counterfactual control-tactics pilot; no league selection.'}
                folder = RAW / 'hosted' / arm['cell']
                h.freeze(folder / 'request.json', body)
                h.create(c, body, folder / 'batch', dry_run=True)
                arms.append(arm)
        h.freeze(RAW / 'hosted-plan.json', {'game': h.VERSION, 'engine': h.COMMIT,
            'versions': versions, 'source_hashes': {'baseline': h.sha(BASE.read_bytes()), 'candidate': h.sha(CANDIDATE.read_bytes())},
            'field': {n: field[n] for n in ['relh','Alex Smith','macromackie','Scott Smith','Andre von Auto','richard','Jordan','Andre von Houck','daveey']},
            'arms': arms, 'pairs': 80, 'new_games': 160,
            'selection': 'Exactly these80new baseline episodes; fresh unique baseline version has no other history. Counterfactual source experience_request, n80. All seeds/rosters/configs/slots reused with responsive policies.',
            'rung': 'Directional paired pilot; no established game-specific paired-sample N floor. No deployment from this pilot alone.',
            'rule': 'All80pairs valid, all10VMs and full replays/XP verified. Report paired mean delta/95percent bootstrap CI, both colors, draft contexts, class, nonzero and productive rates. Advance only if CI lower>=0, mean>0, eachcolor>=95percent baseline and neither nonzero nor productive frequency decreases. No posthoc cohort removal; any failed validity yields unqualified.'})
        print(json.dumps({'prepared': True, 'new_games': 160, 'versions': versions}), flush=True)


def collect(c, ident, roster, slot, source_hash):
    out = RAW / 'artifacts' / ident
    if (out / 'audit-result.json').exists(): return h.read(out / 'audit-result.json')
    out.mkdir(parents=True, exist_ok=True)
    full = h.get(c, '/v2/episode-requests/' + ident)
    h.write(out / 'episode.json', full)
    assert full['coworld_id'] == h.GAME and full['coworld_version'] == h.VERSION
    assert full['policy_version_ids'] == roster
    for kind, name in [('results','results.json'),('replay','replay.bin'),('player-status','player-status.json'),('spec','spec.json')]:
        if (out / name).exists(): continue
        response = c.get('/v2/episode-requests/' + ident + '/artifacts/' + kind)
        response.raise_for_status(); data = response.content
        if kind == 'replay' and data.startswith(b'\x1f\x8b'): data = gzip.decompress(data)
        (out / name).write_bytes(data)
    if not (out / 'audit.json').exists():
        proc = subprocess.run([str(RAW / 'bin/episode'), '--replay', str(out/'replay.bin')], capture_output=True, text=True, timeout=900)
        (out/'audit.log').write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr[-1200:]
        h.write(out/'audit.json', json.loads(proc.stdout.splitlines()[-1]))
    audit, actual, status, spec = [h.read(out/n) for n in ['audit.json','results.json','player-status.json','spec.json']]
    assert audit['hash_mismatches'] == 0 and audit['ticks'] == actual['ticks']
    assert [v['xp'] for v in audit['heroes']] == actual['total_xp']
    assert [max(0,v['xp']*1440-200*audit['ticks'])//1440 for v in audit['heroes']] == actual['scores']
    assert spec['players'][slot]['content_hash'] == source_hash
    assert len(spec['players']) == len(status['players']) == 10
    assert sorted(p['slot'] for p in status['players']) == list(range(10))
    failed = [p['slot'] for p in status['players'] if p.get('exit_code') != 0]
    row = {'episode': ident, 'valid': not failed, 'failed_slots': failed, 'slot': slot,
           'score': actual['scores'][slot], 'hero': audit['heroes'][slot], 'ticks': audit['ticks'],
           'seed': actual['seed'], 'all_hashes_equal': True, 'replay_sha256': h.sha((out/'replay.bin').read_bytes()),
           'content_hashes': [p['content_hash'] for p in spec['players']]}
    h.write(out / 'audit-result.json', row)
    return row


def run():
    plan = h.read(RAW/'hosted-plan.json')
    assert plan['source_hashes']['candidate'] == h.sha(CANDIDATE.read_bytes())
    with h.client() as c:
        pool = ThreadPoolExecutor(4)
        baseline = []
        for arm in plan['arms']:
            folder = RAW/'hosted'/arm['cell']
            ident = panel.reserve(c, h.read(folder/'request.json'), folder/'batch')
            if isinstance(ident, dict): ident = ident['id']
            print(json.dumps({'baseline_request': ident, 'cell': arm['cell']}), flush=True)
            seen = {}
            while len(seen) < arm['games']:
                eps = h.episodes(c, ident)
                h.write(folder/'episodes.json', eps)
                ready = [e for e in eps if e['status'] in ('completed','failed','cancelled','error') and e['id'] not in seen]
                for e in ready: assert e['status'] == 'completed', e
                for e, row in zip(ready, pool.map(lambda e: collect(c,e['id'],arm['roster'],arm['slot'],plan['source_hashes']['baseline']), ready)):
                    seen[e['id']] = row | {'cell': arm['cell'], 'roster': arm['roster']}
                h.write(folder/'result.json', list(seen.values()))
                if len(seen) < arm['games']: time.sleep(10)
            baseline.extend(seen.values())
        assert len(baseline) == 80 and all(r['valid'] for r in baseline), 'Invalid baseline; do not create candidate games'
        ready = {'baseline_version': plan['versions']['baseline'], 'coworld_id': h.GAME,
                 'complete': True, 'episode_ids': [r['episode'] for r in baseline]}
        body = {'candidate_policy_version_id': plan['versions']['candidate'],
                'baseline_policy_version_id': plan['versions']['baseline'], 'source': 'experience_request',
                'n': 80, 'idempotency_key': 'gota-cc61c2-counterfactual-b3f0c124'}
        evaluation = counterfactual_journal.create(c,h,body,RAW/'counterfactual',h.read(RAW/'openapi-preparation.json'),ready)
        print(json.dumps({'counterfactual_eval': evaluation['id']}), flush=True)
        indexed = {r['episode']:r for r in baseline}; seen = {}
        while True:
            evaluation = h.get(c,'/v2/counterfactual-evals/'+evaluation['id'])
            h.write(RAW/'counterfactual/status.json',evaluation)
            pairs = evaluation.get('pairs', [])
            pending = [p for p in pairs if p['candidate_episode_request_id'] and p['candidate_episode_request_id'] not in seen and p['candidate_score'] is not None]
            def audit_candidate(pair):
                base = indexed[pair['baseline_episode_request_id']]
                roster = list(base['roster']); roster[base['slot']] = plan['versions']['candidate']
                return collect(c,pair['candidate_episode_request_id'],roster,base['slot'],plan['source_hashes']['candidate'])
            for pair, result in zip(pending, pool.map(audit_candidate, pending)):
                ident = pair['candidate_episode_request_id']
                base = indexed[pair['baseline_episode_request_id']]
                assert pair['coworld_id'] == h.GAME and pair['seed'] == base['seed'] and pair['probe_slot'] == base['slot']
                roster = list(base['roster']); roster[base['slot']] = plan['versions']['candidate']
                assert pair['opponent_policy_version_ids'] == [v for i,v in enumerate(roster) if i != base['slot']]
                for i,(x,y) in enumerate(zip(base['content_hashes'], result['content_hashes'])):
                    if i != base['slot']: assert x == y
                assert pair['baseline_score'] == base['score'] and pair['candidate_score'] == result['score']
                seen[ident] = {'pair': pair, 'baseline': base, 'candidate': result}
            h.write(RAW/'paired-results.json',{'complete':len(seen)==80,'pairs':list(seen.values())})
            print(json.dumps({'paired_audited': len(seen), 'status': evaluation['status']}), flush=True)
            if evaluation['status'] in ('completed','failed','cancelled','skipped'):
                assert evaluation['status'] == 'completed' and len(seen) == 80, evaluation['status']
                break
            time.sleep(10)
        pool.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--prepare',action='store_true')
    args = parser.parse_args()
    if args.prepare: prepare()
    else: run()
