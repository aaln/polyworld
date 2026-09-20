"""Select the tested anti-rush executable for both existing league players."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time

from economy_feedback import record
from hosted_wave import client, get
from policy_ir import HERE, compile_policy, digest, extract, read, write
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live

PRIORS = {OPTIMIZER: '810d3860-af35-4fed-9364-a4e4bd8b0c2b',
          AARON: 'fa0cab2a-708f-40e0-b6b8-1e44ffeea124'}


def readiness(study, name):
    verify()
    hosted, mixed = study/'hosted'/name, study/'paired-guardrail'
    local, rush, gate, pair_plan, pair, field_plan, field = [read(p) for p in [
        study/'local/result.json', hosted/'result.json', hosted/'gate.json',
        mixed/'plan.json', mixed/'result.json', mixed/'field/plan.json', mixed/'field/result.json']]
    version = read(hosted/'uploaded-version.json')
    clone = read(mixed/'deployment-pair/aaron-upload/uploaded-version.json')
    versions = {OPTIMIZER: version, AARON: clone}
    if (name not in local['selected'] or local['metrics'][name]['games'] < 60 or rush['games'] != 240
            or not gate['passed'] or not pair['passed'] or not field['passed']
            or any(pair['arms'][arm]['games'] != 200 for arm in ['control','candidate'])
            or field['games'] != 100 or field['allied_games'] != 80 or field['both_equipment_games'] != 100):
        raise ValueError('Complete qualifying local, rush, mixed and field evidence is required')
    if (gate['candidate_result_sha256'] != digest((hosted/'result.json').read_bytes())
            or (pair_plan['rush_gate_sha256'] != digest((hosted/'gate.json').read_bytes())
                and not (pair_plan.get('exploratory') and pair_plan['rush_gate_sha256'] is None))
            or field_plan['comparison_sha256'] != digest((mixed/'result.json').read_bytes())
            or pair_plan['candidate_versions'] != [version['id'],clone['id']]
            or field_plan['policy_version'] != version['id'] or field_plan['partner_version'] != clone['id']):
        raise ValueError('Evidence or evaluated player bindings changed')
    source = (study/'local/candidates'/name/'policy.bas').read_bytes()
    if pair_plan['basic_sha256'] != digest(source):
        raise ValueError('Mixed guardrail used a different executable')
    for player, folder in [(OPTIMIZER,hosted),(AARON,mixed/'deployment-pair/aaron-upload')]:
        metadata = read(folder/'upload-request.json')
        if metadata['player_id'] != player or metadata['content_hash'] != digest(source):
            raise ValueError('Uploaded executable or owner changed')
    feedback = mixed/'field/feedback'
    if not feedback.exists():
        record(mixed/'feedback/policy.ir.json',mixed/'feedback/policy.bas',
               f'After passing the exact-rival240game and matched mixed400game checks, '
               f'completed100sampled league games: allied{field["allied_wins"]}/80; '
               f'bothplayers bought equipment in100/100. Sampled field guardrail passed; '
               'this does not establish rank1 or a formal independent-trial significance claim.',
               mixed/'field/result.json',feedback)
    policy = read(feedback/'policy.ir.json')
    if compile_policy(policy).encode() != source or extract(source.decode(),policy) != policy:
        raise ValueError('Final measured IR and evaluated executable differ')
    game = live()
    if (game['id'] != pair_plan['target']['coworld_id'] or game['version'] != pair_plan['game_version']
            or game['manifest']['game']['runnable']['source_url'] != pair_plan['game_source']):
        raise ValueError('Live game changed since evaluation')
    return versions, source, policy, feedback, pair_plan


def main(study, name, apply=False):
    versions, source, policy, feedback, plan = readiness(study,name)
    ids = {p:v['id'] for p,v in versions.items()}
    out = study/'deployment';out.mkdir(exist_ok=True)
    note = ('User authorized both existing player updates. Exact executable passed60freshlocalcases, '
            '240named-rivalgames,400matchedmixedgameswithbothplayers,100sampledpairedfieldgames. '
            'Fullreplay/tenVM/equipment/source checks and semanticIR roundtrip retained. '+str(study))
    with client() as c:
        before = check_champions(champions(c),ids,PRIORS)
        for p,v in versions.items():
            verify_owned(c,v,p)
            remote = get(c,'/stats/policy-versions/'+v['id'])
            if remote.get('player_file_content_hash') not in (None,digest(source)):
                raise ValueError('Remote source differs from evaluated source')
        write(out/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),
            'authorization':'User: deploy the policies and then keep autoresearching',
            'before':list(before.values()),'versions':ids,'basic_sha256':digest(source),
            'semantic_ir_sha256':digest(policy),'evidence':{str(p):digest(p.read_bytes()) for p in [
                study/'hosted'/name/'result.json',study/'paired-guardrail/result.json',
                study/'paired-guardrail/field/result.json']},'ready':True})
        if not apply:
            print('Ready for the two existing players; no selections changed.',flush=True)
            return
        tags={'semantic_ir_sha256':digest(policy),'symbolic_policy_sha256':digest(source),
              'ir_revision':str(policy['update']['revision']),'game_version':plan['game_version'],
              'validation':note,'feedback_parity':'Exact compile and reverse extraction, unchanged tested BASIC.'}
        for player,v in versions.items():
            remote=get(c,'/stats/policy-versions/'+v['id'])
            response=c.put('/stats/policy-versions/'+v['id']+'/tags',json=(remote.get('tags') or {})|tags)
            response.raise_for_status()
            saved_tags=get(c,'/stats/policy-versions/'+v['id'])['tags']
            if any(saved_tags.get(k)!=value for k,value in tags.items()):
                raise ValueError('Final evidence tags did not persist')
            current=check_champions(champions(c),ids,PRIORS)
            if current[player]['policy_version']['id'] != v['id']:
                select(c,player,v,out/('optimizer' if player==OPTIMIZER else 'aaron'),note)
            for _ in range(12):
                current=check_champions(champions(c),ids,PRIORS)
                if current[player]['policy_version']['id']==v['id']:break
                time.sleep(5)
            else:raise ValueError('Selection pending; resume exact receipts')
        after=check_champions(champions(c),ids,PRIORS)
        if any(after[p]['policy_version']['id']!=v for p,v in ids.items()):
            raise ValueError('Both selections did not verify')
        receipt={'verified_at':datetime.now(timezone.utc).isoformat(),'owned_active_ladder_players':2,
                 'players':list(after.values()),'versions':ids,'source_sha256':digest(source),
                 'semantic_ir_sha256':digest(policy),'ir_policy_pair':str(feedback)}
        write(out/'deployment-verified.json',receipt)
        write(HERE/'active_policy.json',{'players':[{'player':p,'version':v['id'],
              'label':f'{v["name"]}:v{v["version"]}'} for p,v in versions.items()],
              'policy':str(feedback/'policy.bas'),'semantic_ir':str(feedback/'policy.ir.json'),
              'deployment_receipt':str(out/'deployment-verified.json')})
    print('Both existing league players selected and active; exactly two owned champions verified.',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path);parser.add_argument('name')
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();main(args.study.resolve(),args.name,args.apply)
