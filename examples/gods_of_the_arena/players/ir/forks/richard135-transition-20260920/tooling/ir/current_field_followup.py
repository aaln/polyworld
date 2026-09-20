"""Refresh changed champions after a frozen-suite winner; never select a champion."""
import argparse
from pathlib import Path
from coached_league_live import arm_plan, AARON, OPTIMIZER
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create, get
from jordan_lineup_guardrails import mixed_part, pin_auditor
from jordan_lineup_wide import ROOT as WIDE, WINNER, mixed_summary
from policy_ir import read,write,digest,compile_policy,extract
from prepare_campaign_xp import LEAGUE
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result as head_result
from release_deploy import champions
from win_hosted import live

GATES={'maximum_color_win_loss':2,'minimum_aggregate_head_gain':0,
       'minimum_allied_wins':112,'maximum_allied_loss':4,'maximum_roster_loss':4,
       'maximum_class_fraction_loss':.2,'no_added_opposed_draws':True,
       'all_equipment_runtime_replays':True}
DESIGN=('Current-version follow-up after all frozen-suite gates pass. Exact pinned '
        'rosters for control/candidate, changed rivals80perarm40/color, fresh200mixed '
        'perarm with bothowned players160allied40opposed. Serial full arms, complete '
        'runtime/replay/equipment audits. Directional fixed-lineup empirical guardrails, '
        'no validated independent-trial N floor or significance claim. No promotion.')


def updated_rosters(prior,pool):
    rivals={r['player']['id']:{'id':r['policy_version']['id'],'label':r['policy_version']['label'],
        'player_id':r['player']['id']} for r in pool if r['player']['id'] not in {AARON,OPTIMIZER}
        and r['status']=='competing' and r['substatus']=='active'}
    if set(rivals)!={r['player_id'] for r in prior['rivals']}:
        raise ValueError('Player pool changed; explicitly redesign complete mixed coverage')
    changed=[rivals[r['player_id']] for r in prior['rivals'] if rivals[r['player_id']]['id']!=r['id']]
    lineups=[{'partner_slot':p['partner_slot'],'other_players':[rivals[r['player_id']] for r in p['other_players']]}
             for p in prior['lineups']]
    if {r['id'] for p in lineups for r in p['other_players']}!={r['id'] for r in rivals.values()}:
        raise ValueError('Mixed roster misses a current rival')
    return changed,lineups


def prepare(study,name):
    root=study/'hosted'/name; out=root/'current-field';out.mkdir(exist_ok=True)
    original=read(root/'final-result.json')
    if not original['passed'] or original['stage']!='field': raise ValueError('All original gates must pass first')
    game=live();prior=read(WIDE/'plan.json');version=read(root/'uploaded-version.json')
    buddy=read(root/'deployment-pair/aaron-upload/uploaded-version.json')
    policy=read(root/'final-feedback/policy.ir.json');source=(root/'final-feedback/policy.bas').read_text()
    if compile_policy(policy)!=source or extract(source,policy)!=policy: raise ValueError('IR/source drift')
    if digest(source.encode())!=read(root/'upload-request.json')['content_hash']: raise ValueError('Untested source')
    with client() as c:
        own=champions(c)
        if {r['player']['id']:r['policy_version']['id'] for r in own}!={OPTIMIZER:prior['candidate_versions'][0],AARON:prior['candidate_versions'][1]}:
            raise ValueError('Deployed controls changed')
        pool=get(c,f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&limit=100')
    if (out/'plan.json').exists():
        plan=read(out/'plan.json')
        if game['version']!=plan['game_version'] or game['manifest']['game']['runnable']['source_url']!=plan['game_source']: raise ValueError('Game release changed')
        if (plan['candidate_versions']!=[version['id'],buddy['id']] or plan['control_versions']!=prior['candidate_versions']
                or plan['source_sha256']!=digest(source.encode())
                or plan['original_result_sha256']!=digest((root/'final-result.json').read_bytes())):
            raise ValueError('Frozen candidate or qualification evidence changed')
        return out,plan
    changed,lineups=updated_rosters(prior,pool)
    write(out/'champions.json',pool)
    plan={k:prior[k] for k in ('target','game_version','game_source','config')}
    plan.update(control_versions=prior['candidate_versions'],candidate_versions=[version['id'],buddy['id']],
        name=name,changed_rivals=changed,lineups=lineups,gates=GATES,design=DESIGN,
        original_result_sha256=digest((root/'final-result.json').read_bytes()),
        snapshot_sha256=digest((out/'champions.json').read_bytes()),source_sha256=digest(source.encode()))
    freeze(out/'plan.json',plan)
    return out,plan


def run(study,name):
    out,p=prepare(study,name);root=out.parent;heads={};checks={};gain=0;g=p['gates']
    # Entire comparison rule is frozen before any new request is created.
    template=read(WINNER/'jordan/plan.json')
    for rival in p['changed_rivals']:
        key='rival_'+rival['id'].split('-')[0]
        reference=out/'references'/key;reference.mkdir(parents=True,exist_ok=True)
        freeze(reference/'plan.json',template|{'rival':rival['label'],'rival_version':rival['id'],'rival_key':key})
        h={}
        for arm in ('control','candidate'):
            folder=out/'heads'/key/arm
            prepare_head(folder,{'id':p[arm+'_versions'][0],'name':arm+' current-field '+name},reference,arm+' '+rival['label'],DESIGN)
            h[arm]=head_result(folder)
        heads[key]=h
        for color in ('red','blue'):
            checks[key+'_'+color]=h['candidate']['colors'][color]['win']>=h['control']['colors'][color]['win']-g['maximum_color_win_loss']
        gain+=h['candidate']['wins']-h['control']['wins']
        write(out/'head-progress.json',{'heads':heads,'checks':checks,'gain':gain})
    checks['aggregate_head_gain']=gain>=g['minimum_aggregate_head_gain']
    arms={}
    if all(checks.values()):
        seeds=set()
        for arm in ('control','candidate'):
            rows=[]
            for i in range(2):
                folder=out/'mixed'/arm/f'part-{i}';folder.mkdir(parents=True,exist_ok=True)
                plan=arm_plan(p,arm,i);freeze(folder/'plan.json',plan);pin_auditor(folder)
                with client() as c:create(c,batch_body(plan,100),folder/'batch',dry_run=True)
                audit=folder/'audit-progress.json'
                if not audit.exists() or read(audit).get('verified')!=100: run_queue([folder])
                for row in mixed_part(folder):
                    if row['seed'] in seeds: raise ValueError('Repeated mixed seed')
                    seeds.add(row['seed']);row['roster_index']=i;rows.append(row)
            arms[arm]=mixed_summary(rows)
        a,b=arms['candidate'],arms['control']
        checks.update(allied=a['allied_wins']>=b['allied_wins']-g['maximum_allied_loss'],absolute=a['allied_wins']>=g['minimum_allied_wins'],
            rosters=all(a['rosters'][str(i)]>=b['rosters'][str(i)]-g['maximum_roster_loss'] for i in range(2)),
            classes=a['classes'].keys()==b['classes'].keys() and all(v['games']==b['classes'][c]['games'] and
                v['wins']>=b['classes'][c]['wins']-g['maximum_class_fraction_loss']*v['games'] for c,v in a['classes'].items()),
            opposed_draws=a['opposed_draws']<=b['opposed_draws'],equipment=a['both_gear']==b['both_gear']==200)
    result={'heads':heads,'arms':arms,'checks':checks,'passed':all(checks.values()),
        'plan_sha256':digest((out/'plan.json').read_bytes()),'promotion_performed':False,'scope':DESIGN}
    write(out/'result.json',result)
    if not (out/'feedback').exists():record(root/'final-feedback/policy.ir.json',root/'final-feedback/policy.bas',
        f'Fresh pinned current-version field checks: {checks}. All completed full arm audits retained; no champion selection.',
        out/'result.json',out/'feedback')
    print('Current field',checks,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path);p.add_argument('name')
    p.add_argument('--run',action='store_true',help='Launch the authorized validation batches; never promotes')
    a=p.parse_args();run(a.study,a.name) if a.run else prepare(a.study,a.name)
