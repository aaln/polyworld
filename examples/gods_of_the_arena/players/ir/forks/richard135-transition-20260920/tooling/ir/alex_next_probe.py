"""User-requested named rival tests through the documented XP label selector."""
from datetime import datetime,timezone
import httpx
from economy_feedback import record
from hosted_wave import client,create,episodes
from jordan_lineup_guardrails import pin_auditor
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head,result
from release_workspace import RUN
from threat_coverage_hosted import control
from win_hosted import live

STUDY=RUN/'coached-lanes/r5-alex-next'
ALEX='ply_4e9a2db0-dbc2-4283-b4cc-3ce79e9f8d40'
H=RUN/'coached-lanes/r5-anchored-support'
G=RUN/'coached-lanes/r5-jordan-lineup'
DESIGN=('Explicit user-requested test of Alex Smith named new policy. Exact name:vN '
        'resolved by normal XP roster selector, then verify participant owner and UUID. '
        'Five identical policies per team,40episodes/color, complete80 per own source. '
        'Sources anchorH and deployedG remain frozen. No source tuning or promotion. '
        'Full runtime/replay/equipment audit. Directional fixed-lineup evidence.')


def resolve_and_run(label):
    key=label.replace(':','-');root=STUDY/key/'anchor';root.mkdir(parents=True,exist_ok=True)
    version=read(H/'hosted/anchor/uploaded-version.json')
    ref=read(control('gota-g002:v1')/'plan.json')
    folder=root/'rival_named/red';folder.mkdir(parents=True,exist_ok=True)
    body={'idempotency_key':'gota-alex-named-'+digest({'label':label,'source':version['id'],'study':str(STUDY)})[:20],
          'target':ref['target'],'game_config_overrides':ref['config'],'num_episodes':40,
          'roster':[{'slot':s,'player':{'policy_ref':version['id'] if s<5 else label}} for s in range(10)],
          'notes':DESIGN+' Anchor on red against '+label}
    with client() as c:
        create(c,body,folder/'batch',dry_run=True)
        try:xreq=create(c,body,folder/'batch')
        except httpx.HTTPStatusError as e:
            write(root/'unavailable.json',{'label':label,'status':e.response.status_code,'detail':e.response.json(),'time':datetime.now(timezone.utc).isoformat(),'created':False})
            if e.response.status_code not in (400,403,404):raise
            print(label,'unavailable',e.response.status_code,e.response.json(),flush=True);return None
        receipt=read(folder/'batch/created.json')
        eps=receipt.get('episodes') or episodes(c,xreq)
    if not eps:raise ValueError('Created request has no resolved episodes')
    rivals={p['policy_version_id']:p for e in eps for p in e['participants'] if p['position']>=5}
    if len(rivals)!=1:raise ValueError('Named opponent ambiguous')
    rid,rival=next(iter(rivals.items()));name,ver=label.rsplit(':v',1)
    if rival['policy_name']!=name or rival['version']!=int(ver) or rival['player_id']!=ALEX:
        write(root/'unexpected-roster.json',rival);raise ValueError('User-named rival does not match Alex; inspect retained request')
    for e in eps:
        if e['policy_version_ids']!=[version['id']]*5+[rid]*5:raise ValueError('Unexpected resolved roster')
    freeze(STUDY/key/'resolved-target.json',{'label':label,'id':rid,'player_id':rival['player_id'],'player_name':rival['player_name'],'resolved_from_xreq':xreq,'selector':'Documented XP policy_ref exact label; no private policy source requested.'})
    print('RESOLVED',label,rid,rival['player_name'],xreq,flush=True)
    plan={k:ref[k] for k in ('target','game_version','game_source','config','episodes_per_color','interpretation')}
    plan.update(policy_version=version['id'],policy_label=version['name']+':v'+str(version['version']),
                rival=label,rival_version=rid,rival_key='rival_named',design=DESIGN)
    freeze(root/'plan.json',plan)
    for color in ('red','blue'):
        f=root/'rival_named'/color;f.mkdir(parents=True,exist_ok=True)
        slots=list(range(5)) if color=='red' else list(range(5,10))
        roster=[version['id'] if s in slots else rid for s in range(10)]
        freeze(f/'plan.json',plan|{'color':color,'own_slots':slots,'roster':roster});pin_auditor(f)
        if color=='blue':
            b={'idempotency_key':body['idempotency_key']+'-blue','target':plan['target'],'game_config_overrides':plan['config'],
               'num_episodes':40,'roster':[{'slot':s,'player':{'policy_ref':v}} for s,v in enumerate(roster)],'notes':DESIGN+' Anchor on blue against '+label}
            with client() as c:create(c,b,f/'batch',dry_run=True)
    anchor=result(root)
    gversion={'id':'b61bfdfb-f82f-4c6b-a504-5c040ed82a68','name':'aaron-gota-ir-perimeter-blue_repair-0916:v1'}
    grows=STUDY/key/'deployed';prepare_head(grows,gversion,root,'Deployed versus new '+label,DESIGN)
    deployed=result(grows)
    report={'target':rival,'anchor':anchor,'deployed':deployed,'promotion_performed':False,'scope':DESIGN}
    write(STUDY/key/'result.json',report)
    source=H/'hosted/anchor/final-feedback'
    if not (root/'feedback').exists():
        record(source/'policy.ir.json',source/'policy.bas',f'User-requested new opponent {label}: anchor {anchor["colors"]}, deployed {deployed["colors"]}. Earlier g002 red failure remains; no promotion from this diagnostic.',STUDY/key/'result.json',root/'feedback')
    return report


def main():
    STUDY.mkdir(parents=True,exist_ok=True)
    freeze(STUDY/'prospective-plan.json',{'rivals':['gota-me:v166','gota-g003:v1'],
        'own_sources':{'anchor':'9cedf3ff-c7ce-4cff-897f-d48b44e049ad','deployed':'b61bfdfb-f82f-4c6b-a504-5c040ed82a68'},
        'games_per_source_per_available_rival':80,'maximum_new_games':320,'design':DESIGN,
        'unavailable':'Record normal API rejection and skip; do not search private source or guess UUID.'})
    live();reports={}
    for label in ('gota-me:v166','gota-g003:v1'):
        reports[label]=resolve_and_run(label);write(STUDY/'progress.json',{'results':reports})
    write(STUDY/'result.json',{'results':reports,'promotion_performed':False})

if __name__=='__main__':main()
