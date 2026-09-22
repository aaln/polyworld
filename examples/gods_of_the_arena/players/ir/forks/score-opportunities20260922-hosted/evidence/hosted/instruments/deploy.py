"""Deploy only the qualified exact follow-up bytes to the two authorized players."""
import json
import subprocess
import sys
import time
import httpx
import jsonschema
from hosted_score import h, ROOT, STUDY

LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
PLAYERS = {'aaron': h.PLAYER, 'coach': 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'}
PRIOR = {'aaron': 'b65ccf7b-d7a1-4681-b57f-a55f5ace43c7', 'coach': '088c0fed-b536-4777-9f7a-14abee21e5b8'}
PAIR = ROOT / 'examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922-hosted'
OUT = STUDY / 'deployment'
NOTE = ''  # Filled exclusively from the completed audited report.



def members(c):
    return h.get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')


def upload_coach(c, source, schema):
    out = OUT / 'coach'
    meta = {'name': 'aaron-gota-score0922-coach', 'content_hash': h.sha(source),
            'size_bytes': len(source), 'player_id': PLAYERS['coach'], 'attributes': {},
            'tags': {'game': 'gods_of_the_arena', 'game_version': h.VERSION,
                     'engine_commit': h.COMMIT, 'validation': NOTE}}
    h.freeze(out / 'upload-request.json', meta)
    jsonschema.validate(meta, schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out / 'uploaded-version.json').exists():
        r = c.post('/stats/policies/files/upload', json=meta)
        if r.status_code == 409:
            r = c.post('/stats/policies/files/complete', json=meta)
            r.raise_for_status()
            version = r.json()
        else:
            r.raise_for_status()
            payload = r.json()
            version = payload.get('existing_policy_version')
            if version is None:
                r = httpx.put(payload['upload_url'], content=source,
                              headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                r.raise_for_status()
                r = c.post('/stats/policies/files/complete', json=meta)
                r.raise_for_status()
                version = r.json()
        h.write(out / 'uploaded-version.json', version)
    return h.read(out / 'uploaded-version.json')


def select(c, label, version, schema):
    player = PLAYERS[label]
    out = OUT / label / 'selection'
    body = {'league_id': LEAGUE, 'policy_version_id': version['id'], 'player_id': player,
            'auto_champion': 'always', 'notes': NOTE}
    h.freeze(out / 'request.json', body)
    definition = schema['paths']['/v2/league-submissions']['post']['requestBody']['content']['application/json']['schema']
    jsonschema.validate(body, definition, resolver=jsonschema.RefResolver.from_schema(schema))
    query = f'/v2/league-submissions?league_id={LEAGUE}&player_id={player}&policy_version_id={version["id"]}&limit=100'
    submissions = h.get(c, query)
    prior = [s for s in submissions if s.get('auto_champion') == 'always' and s['status'] not in ('failed','rejected','cancelled')]
    assert len(prior) <= 1, 'Reconcile ambiguous submission state'
    if prior:
        h.write(out / 'created.json', prior[0])
    elif not (out / 'created.json').exists():
        assert not (out / 'create-attempt.json').exists(), 'Uncertain create: reconcile its exact version before retrying'
        h.write(out / 'create-attempt.json', {'at': h.research.now(), 'body_sha256': h.research.fingerprint(body)})
        r = c.post('/v2/league-submissions', json=body)
        h.write(out / 'response.json', {'status': r.status_code, 'body': r.text})
        r.raise_for_status()
        h.write(out / 'created.json', r.json())
    for _ in range(120):
        rows = members(c)
        h.write(out / 'readback.json', rows)
        matching = [r for r in rows if r['player']['id']==player and r['policy_version']['id']==version['id'] and r['end_time'] is None]
        assert len(matching) <= 1
        if matching:
            row = matching[0]
            assert row['status'] not in ('disqualified','rejected','retired'), 'Qualification failed; preserve prior champion and reconcile'
            if row['is_champion'] and row['status']=='competing' and row['substatus']=='active':
                print('Verified',label,version['id'],row['id'],flush=True)
                return row
        time.sleep(5)
    raise RuntimeError('Existing submission pending; resume exact receipts, do not resubmit')


def main():
    global NOTE
    report = h.read(STUDY / 'hosted/report.json')
    assert report['complete'] and report['score_gate_passed']
    NOTE = (f"Individual XP opportunity policy on{h.VERSION}. Fresh160-game A/B gain{report['aggregate_gain_percent']:.3f}%; colors{report['per_color_gain_percent']};95% interval{report['gain_ci95_percent']}. All ten sources/VMs, full replay/XP/integer score audited. Fixed first-pick mixed roster, no rank guarantee. Prior explicit deployment authorization for Aaron and Coach.")
    with h.research.lock(h.CAMPAIGN / 'runner.lock', blocking=False), h.research.lock(h.CAMPAIGN / 'league-deployment.lock', blocking=False), h.client() as c:
        h.live(c)
        assert h.read(h.CAMPAIGN / 'service.json')['state']=='paused'
        result = h.read(STUDY / 'hosted/result.json')
        assert result['complete'] and result['passed']
        manifest = h.read(PAIR / 'manifest.json')
        source = (PAIR / 'policy.bas').read_bytes()
        assert h.sha(source)==manifest['source_sha256'] and manifest['score_gate_passed']
        p = subprocess.run([sys.executable,str(PAIR / 'verify.py')],capture_output=True,text=True,check=True)
        h.write(OUT / 'conversion-proof.json', {'returncode':p.returncode,'stdout':p.stdout})
        schema = h.get(c,'/openapi.json')
        before = members(c)
        h.write(OUT / 'latest-memberships.json', before)
        if not (OUT / 'before.json').exists():
            for label,player in PLAYERS.items():
                current = [r for r in before if r['player']['id']==player and r['is_champion'] and r['end_time'] is None]
                assert len(current)==1 and current[0]['policy_version']['id']==PRIOR[label], 'Concurrent champion change: re-evaluate before replacing it'
            h.freeze(OUT / 'before.json', before)
            h.freeze(OUT / 'decision.json', {'at':h.research.now(),'source_sha256':h.sha(source),
                'authorization':'Prior explicit latest-league deployment to both Aaron and Coach; no new approval required',
                'engine':h.COMMIT,'game_version':h.VERSION,'evidence':'160-game fresh-control score A/B against khors114/Jordan411/Richard167; full report preserved',
                'score':result['score'],'control_score':result['control_score'],'uplift_percent':(result['score']/result['control_score']-1)*100,
                'rollback_versions':PRIOR,'rollback_source_sha256':'db71abb37180a06a432ac71c3c5d6802be2ba2c1b2d782b151336beacd8b1520',
                'rollback_source':'examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted/policy.bas',
                'limits':report['evidence_scope']})
        versions = {'aaron':h.read(STUDY / 'upload/version.json'),
                    'coach':upload_coach(c,source,schema)}
        log = ROOT / 'games/gods_of_the_arena/players/score20260922/VERSION_LOG.md'
        log.parent.mkdir(parents=True, exist_ok=True)
        text = log.read_text() if log.exists() else '# Individual score policy versions\n'
        if versions['coach']['id'] not in text:
            log.write_text(text + f"\n- {h.research.now()}: Coach `{versions['coach']['id']}`, `{versions['coach']['name']}:v{versions['coach']['version']}`, source `{h.sha(source)}`. Byte-identical qualified executable; separate player binding, no independent evidence. Inert until automatic placement is verified.\n")
        chosen = {}
        for label in ('coach','aaron'):
            chosen[label] = select(c,label,versions[label],schema)
        rows = members(c)
        for label,selected in chosen.items():
            row = next(r for r in rows if r['id']==selected['id'])
            assert row['is_champion'] and row['status']=='competing' and row['substatus']=='active'
        h.write(OUT / 'verified.json', {'at':h.research.now(),'source_sha256':h.sha(source),'selected':chosen,'versions':versions,'memberships':rows})
        log.write_text(log.read_text() + f"\n- {h.research.now()}: Both players verified active, competing champions on `{h.sha(source)}`. Receipt: `tmp/gota-score-20260922/deployment/verified.json`.\n")


if __name__ == '__main__':
    main()
