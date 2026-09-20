"""Deploy the exact reviewed adaptive fork to the two authorized league players."""
import argparse
import fcntl
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from games.gods_of_the_arena.instruments.richard_coaching import deploy_half as shared

OUT = ROOT/'tmp/gota-ir/formation-adaptive-deployment-20260920'
PAIR = ROOT/'examples/gods_of_the_arena/players/ir/forks/formation-adaptive-20260920'
SOURCE = 'c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4'
AUTH = 'deploy the policy to latest on league'
NOTE = ('Explicit user selection after reviewing the adaptive formation3600 fork. '
        'Discovery400 and unchanged confirmation240 fully audited: each stage Alex40/40each color, '
        'Jordan40/40each, Richardblue40/40/red0W40L. Fresh formation Alex/Jordan controls0/160. '
        'Repeated trajectories are correlated. Richard red and broad-field gates remain unqualified; '
        'the user-approved deployment does not advance formal research acceptance. '
        'Same tested source for Aaron and Coach under the existing two-player scope.')
RIVALS = {'ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83': '7c370daf-3c5f-42f8-870b-54b79c495a44',
          'ply_4e9a2db0-dbc2-4283-b4cc-3ce79e9f8d40': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
          'ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2'}
PRIOR = {'aaron': '2c025f1e-a6f9-46ca-bab1-32dfaef6e9de',
         'coach': 'b9eb629e-a429-45eb-9e7b-559095f78552'}
read, write, now, sha = shared.read, shared.write, shared.now, shared.digest


def append_once(marker, text):
    if marker not in shared.LOG.read_text():
        with shared.LOG.open('a') as log:
            log.write('\n\n'+marker+'\n\n'+text+'\n')


def main(apply):
    OUT.mkdir(parents=True, exist_ok=True)
    shared.OUT = OUT  # Reuse the receipt-safe upload helper in this process only.
    with (shared.CAMPAIGN/'league-deployment.lock').open('a+') as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        source = (PAIR/'policy.bas').read_bytes()
        assert sha(source) == SOURCE
        proof = subprocess.run([sys.executable, str(PAIR/'verify.py')], check=True, capture_output=True, text=True)
        import json
        write(OUT/'conversion-proof.json', json.loads(proof.stdout))
        evidence = {}
        for stage, filename in [('discovery','hosted-result.json'),('confirmation','confirmation-result.json')]:
            result = read(PAIR/'evidence'/filename)
            assert result['complete'] and result['passed'] and all(result['gate'].values())
            for key, cell in result['cells'].items():
                assert cell['games'] == 40 and cell['all_full_audits_passed'] and cell['structured_ten_vm_exits']
                expected = 40 if '/candidate/' in key and key != 'richard/candidate/red' else 0
                assert cell['wins'] == expected
            evidence[stage] = {'sha256': sha((PAIR/'evidence'/filename).read_bytes()),
                              'artifact': str(PAIR/'evidence'/filename), 'games': result['games'],
                              'gate': result['gate'], 'cells': {k:{x:v[x] for x in ('wins','losses','draws')}
                                                               for k,v in result['cells'].items()}}
        with shared.client() as c:
            game = shared.get(c, '/v2/coworlds/cow_126f2fcb-80a0-4b6e-8166-eb6163576db5')
            assert game['version'] == '2026.9.16.5'
            assert '/tree/f2ab9598d8f8001b6beae3e66404e341770c803f/' in game['manifest']['game']['runnable']['source_url']
            all_champions = shared.get(c, f'/v2/league-policy-memberships?league_id={shared.LEAGUE}&champions_only=true&limit=100')
            assert len(all_champions)<100
            by_player = {row['player']['id']:row for row in all_champions}
            for player, expected in RIVALS.items():
                assert by_player[player]['policy_version']['id'] == expected, 'Target version changed'
            schema = shared.get(c, '/openapi.json')
            write(OUT/'live-schema.json', schema)
            write(OUT/'game-at-apply.json', game)
            write(OUT/'all-champions-before.json', all_champions)
            current = shared.owned_champions(c)
            before_path = OUT/'champions-before.json'
            if not before_path.exists():
                assert all(current[p]['policy_version']['id']==PRIOR[label] for label,p in shared.PLAYERS.items())
                write(before_path, current)
            before = read(before_path)
            for label, player in shared.PLAYERS.items():
                allowed = {before[player]['policy_version']['id']}
                receipt = OUT/label/'uploaded-version.json'
                if receipt.exists():
                    allowed.add(read(receipt)['id'])
                assert current[player]['policy_version']['id'] in allowed, 'Concurrent champion change'
            write(OUT/'rollback.json', {p:{'policy_version':r['policy_version'], 'membership':r['id'],
                  'source_sha256':'e9eac314c36c06be53af969b54be0eb42a9ee329b0c6d1874eebda489d645e4a',
                  'action':f"POST /v2/league-policy-memberships/{r['id']}/champion", 'body':{},
                  'trigger':'Confirmed runtime invalidity or qualification rejection; ordinary red Richard losses are known, not a surprise rollback trigger.',
                  'expected_time':'One authenticated selection and readback; no rebuild.'} for p,r in before.items()})
            preflight = {'checked_at':now(), 'ready':True, 'authorization_verbatim':AUTH,
                         'two_player_scope':'Existing explicit user authorization to deploy to both Aaron and Coach',
                         'source_sha256':SOURCE, 'pair':str(PAIR), 'evidence':evidence,
                         'scope':NOTE, 'standard_field_qualified':False, 'formal_research_acceptance_advanced':False}
            write(OUT/'preflight.json', preflight)
            if not apply:
                print('Read-only deployment preflight passed for both players.', flush=True)
                return
            versions = {}
            for label, player in shared.PLAYERS.items():
                metadata = read(PAIR/'upload-request.json')
                if label == 'coach':
                    metadata.update(name=metadata['name']+'-coach', player_id=player,
                                    tags=metadata['tags'] | {'validation':NOTE, 'authorization':AUTH,
                                    'semantic_ir_sha256':sha((PAIR/'policy.ir.json').read_bytes())})
                version = shared.upload(c, label, metadata, source, schema)
                if label == 'aaron':
                    assert version['id'] == read(PAIR/'uploaded-version.json')['id'], 'Tested source identity changed'
                versions[player] = version
                append_once('## Adaptive deployment registration '+version['id'],
                            f"- {version['name']}:v{version['version']}; {label}; {now()}.\n"
                            f'- BASIC {SOURCE}; byte-identical tested source.\n'
                            '- Validation: validated for the user-approved bounded deployment; 640 hosted games audited.\n'
                            '- '+NOTE)
            decision = preflight | {'recorded_at':now(), 'league':shared.LEAGUE, 'versions':versions,
                                    'rollback':read(OUT/'rollback.json')}
            if not (OUT/'decision.json').exists():
                write(OUT/'decision.json', decision)
            append_once('## Adaptive league submission decision 2026-09-20',
                        '- User: '+AUTH+'\n- '+NOTE+'\n- Decision and rollback: `'+str(OUT/'decision.json')+'`.')
            for label, player in shared.PLAYERS.items():
                current = shared.owned_champions(c)
                for p,row in current.items():
                    assert row['policy_version']['id'] in {before[p]['policy_version']['id'],versions[p]['id']}
                version = versions[player]
                if current[player]['policy_version']['id'] != version['id']:
                    body = {'league_id':shared.LEAGUE,'policy_version_id':version['id'],'player_id':player,
                            'auto_champion':'never','notes':NOTE}
                    operation = schema['paths']['/v2/league-submissions']['post']
                    body_schema = operation['requestBody']['content']['application/json']['schema']
                    shared.jsonschema.validate(body, body_schema, resolver=shared.jsonschema.RefResolver.from_schema(schema))
                    print('SUBMITTING',label,version['id'],flush=True)
                    shared.select(c, player, version, OUT/label/'league', NOTE)
                for attempt in range(120):
                    rows = shared.get(c, f'/v2/league-policy-memberships?league_id={shared.LEAGUE}&mine=true&limit=100')
                    write(OUT/label/'qualification-readback.json', rows)
                    matches = [r for r in rows if r['player']['id']==player and r['policy_version']['id']==version['id']]
                    assert len(matches)==1
                    row = matches[0]
                    if row['status'] in {'disqualified','retired','rejected'}:
                        raise ValueError('Qualification failed; use saved rollback and reconcile exact membership')
                    if row['status']=='competing' and row['substatus']=='active' and row['is_champion']:
                        print('VERIFIED',label,version['id'],row['id'],flush=True)
                        break
                    time.sleep(5)
                else:
                    raise ValueError('Qualification remains pending; resume exact existing submission')
            final = shared.owned_champions(c)
            assert all(final[p]['policy_version']['id']==v['id'] for p,v in versions.items())
            write(OUT/'deployment-verified.json', {'verified_at':now(),'league':shared.LEAGUE,
                  'players':final,'versions':versions,'source_sha256':SOURCE,
                  'state':'both_competing_active_champions','scope':NOTE})
            append_once('## Adaptive deployment verified 2026-09-20',
                        '- Both players active, competing and champion at '+now()+'.\n- Receipt: `'+str(OUT/'deployment-verified.json')+'`.')
            print('Both players deployed and verified.',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    main(parser.parse_args().apply)
