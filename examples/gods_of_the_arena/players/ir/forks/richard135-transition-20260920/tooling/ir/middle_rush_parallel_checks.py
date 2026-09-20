"""Parallel, batched nonregression checks explicitly requested by the user.

Avoid duplicate controls: candidate red is exactly G red; H and G blue are
exactly identical. Measure changed blue versus G and candidate red versus H.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import subprocess
import sys
import time

from binding import CONTRACTS
from economy_feedback import record
from hosted_wave import client, create, episodes
from hosted_wave_audit import verify as audit
from jordan_lineup_guardrails import pin_auditor
from macromackie_middle_rush import STUDY
from policy_ir import HERE, digest, read, write
from ranger_guard_hosted import freeze
from release_workspace import RUN
from win_hosted import live

ROOT = STUDY/'parallel-nonregression'
VERSIONS = {
    'candidate': {'id':'d94c63e8-4aa5-4a71-8ec5-78549f3958c6','name':'aaron-gota-ir-middle-rush-blue_three-0916:v1'},
    'blue_control': {'id':'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a','name':'aaron-gota-ir-perimeter-blue_repair-0916-aaron:v1'},
    'red_control': {'id':'9cedf3ff-c7ce-4cff-897f-d48b44e049ad','name':'aaron-gota-ir-coordinated-support-anchor-0916:v1'}}
DESIGN = ('User-authorized parallel40episode batches. Exact g002v1 andblack-kitev16 '
          'candidate40/color; shared blue Gcontrol40 and red Hcontrol40 per rival. '
          'Candidate red has identical lowered execution to G; H/Gblue identical. '
          'Avoid counting duplicate implementations as extra evidence. Eachcolor '
          'candidate must match or exceed measured relevant control wins. Exact '
          'rosters/config/release, all runtime/replay/equipment checks. Different '
          'generated seeds and correlated trajectories, no formal significance. '
          'Also Gblue40 vs relh154 to diagnose new candidate0/40blue. No source tuning.')


def branch_proof():
    folders = {'g':RUN/'coached-lanes/r5-jordan-lineup/candidate',
               'h':RUN/'coached-lanes/r5-anchored-support/hosted/anchor/tournament-portfolio/policy',
               'new':STUDY/'local/candidates/blue_three'}
    policies = {n:read(p/'policy.ir.json') for n,p in folders.items()}
    observer = {}
    for n,p in policies.items():
        skill=p['skill']['observe']
        observer[n]=CONTRACTS[skill['operator']].source(skill['parameters']).split('\nelse\n',1)
        assert p['strategy']==policies['g']['strategy'] and p['execution']==policies['g']['execution']
        assert all(s==policies['g']['skill'][k] for k,s in p['skill'].items() if k!='observe')
    assert observer['new'][0]==observer['g'][0]
    assert observer['h'][1]==observer['g'][1]
    return {'candidate_red_equals_g':True,'h_blue_equals_g':True,
            'source_hashes':{n:digest((p/'policy.bas').read_bytes()) for n,p in folders.items()},
            'local_red_fullgame_parity':str(STUDY/'local/qualification.json')}


def prepare(key,label,arm,color,rival_id=None):
    root=ROOT/key/arm/color
    root.mkdir(parents=True,exist_ok=True)
    ref=read(STUDY/'hosted/blue_three/macromackie-v4/plan.json')
    own=VERSIONS[arm]
    slots=list(range(5)) if color=='red' else list(range(5,10))
    selector=rival_id or label
    body={'idempotency_key':'gota-middle-parallel-'+digest({'root':str(ROOT),'key':key,'arm':arm,'color':color})[:20],
          'target':ref['target'],'game_config_overrides':ref['config'],'num_episodes':40,
          'roster':[{'slot':s,'player':{'policy_ref':own['id'] if s in slots else selector}} for s in range(10)],
          'notes':DESIGN+' '+arm+' '+color+' versus '+label}
    with client() as c:
        create(c,body,root/'batch',dry_run=True)
        if rival_id is None:
            request=create(c,body,root/'batch')
            eps=read(root/'batch/created.json').get('episodes') or episodes(c,request)
            rivals={p['policy_version_id']:p for e in eps for p in e['participants'] if p['position'] not in slots}
            assert len(rivals)==1
            rival_id,rival=next(iter(rivals.items()))
            name,version=label.rsplit(':v',1)
            assert rival['policy_name']==name and rival['version']==int(version)
            freeze(ROOT/key/'resolved-target.json',{'label':label,'id':rival_id,'player_id':rival['player_id'],'player_name':rival['player_name']})
    p={k:ref[k] for k in ('target','game_version','game_source','config','episodes_per_color','interpretation')}
    p.update(policy_version=own['id'],policy_label=own['name'],rival=label,rival_version=rival_id,
             rival_key=key,color=color,arm=arm,own_slots=slots,
             roster=[own['id'] if s in slots else rival_id for s in range(10)],design=DESIGN)
    freeze(root/'plan.json',p)
    pin_auditor(root)
    return root,rival_id


def summarize(root):
    plan=read(root/'plan.json')
    assert read(root/'collection.json')['episodes']==40
    folders=sorted(p.parent for p in (root/'artifacts').glob('*/.done'))
    assert len(folders)==40
    rows=[];seeds=set()
    binary=root/'audit';sha=digest(binary.read_bytes())
    for folder in folders:
        audit(folder,binary,sha)
        ep,r,a=[read(folder/n) for n in ('episode.json','results.json','audit.json')]
        config={k:v for k,v in ep['game_config'].items() if k not in ('seed','players','tokens')}
        assert ep['policy_version_ids']==plan['roster'] and config==plan['config']
        assert ep['coworld_version']==plan['game_version'] and ep['coworld_id']==plan['target']['coworld_id']
        assert r['seed'] not in seeds;seeds.add(r['seed'])
        assert [h['total_xp'] for h in a['heroes']]==r['total_xp']
        own={r['scores'][s] for s in plan['own_slots']}
        other={r['scores'][s] for s in range(10) if s not in plan['own_slots']}
        assert len(own)==len(other)==1 and own|other<={0,1}
        win,loss=next(iter(own)),next(iter(other));assert win+loss<=1
        gear=sum(a['heroes'][s]['first_gear_tick']>=0 for s in plan['own_slots']);assert gear==5
        rows.append({'episode':ep['id'],'seed':r['seed'],'win':win,'loss':loss,'draw':int(not win and not loss),
                     'ticks':r['ticks'],'gear_heroes':gear,'replay_sha256':a['replay_sha256']})
    output={'games':40,'wins':sum(r['win'] for r in rows),'losses':sum(r['loss'] for r in rows),
            'draws':sum(r['draw'] for r in rows),'all_full_audits_passed':True,'rows':rows}
    write(root/'arm-result.json',output)
    print('DONE',plan['rival'],plan['arm'],plan['color'],output['wins'],flush=True)
    return str(root.relative_to(ROOT)),output


def run_arm(root):
    if (root/'arm-result.json').exists():return summarize(root)
    live();jobs=[]
    try:
        with client() as c:
            request=create(c,read(root/'batch/request.json'),root/'batch')
            for script,args,name in [('rival_matchups.py',[str(root),'harvest'],'harvest.log'),
                                     ('watch_hosted_audit.py',[str(root),'--workers','2'],'audit.log')]:
                log=(root/name).open('a')
                jobs.append((subprocess.Popen([sys.executable,str(HERE/script),*args],stdout=log,stderr=log),log))
            while True:
                entries=episodes(c,request);counts=dict(Counter(e['status'] for e in entries))
                write(root/'server-progress.json',{'request':request,'statuses':counts,'checked_at':datetime.now(timezone.utc).isoformat()})
                if any(s in counts for s in ('failed','cancelled','error')):raise ValueError('Failed episode retained')
                if any(p.poll() not in (None,0) for p,_ in jobs):raise ValueError('Collector failed')
                if counts=={'completed':40}:break
                time.sleep(15)
        if any(p.wait()!=0 for p,_ in jobs):raise ValueError('Collector failed')
        return summarize(root)
    finally:
        for p,log in jobs:
            if p.poll() is None:p.terminate();p.wait()
            log.close()


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    freeze(ROOT/'prospective.json',{'design':DESIGN,'authorization':'User: replace for both champions after no regression vs g002v1 andblackkitev16; requests may run in parallel.',
           'branch_proof':branch_proof(),'maximum_new_episodes':360,'workers':3,'versions':VERSIONS,
           'gate':'candidateblue>=Gblue and candidatered>=Hred on eachrival; red G identical bysource andsixfullgames. Priorrelh/Jordan guard failures also block promotion.'})
    arms=[]
    for key,label in [('g002','gota-g002:v1'),('black16','black-kite:v16')]:
        first,rid=prepare(key,label,'candidate','red');arms.append(first)
        for arm,color in [('candidate','blue'),('blue_control','blue'),('red_control','red')]:
            p,_=prepare(key,label,arm,color,rid);arms.append(p)
    relh=read(STUDY/'tournament-guards/relh154/resolved-target.json')
    p,_=prepare('relh154','relh-gods-of-the-arena:v154','blue_control','blue',relh['id']);arms.insert(0,p)
    results={}
    with ThreadPoolExecutor(3) as pool:
        pending=[pool.submit(run_arm,p) for p in arms]
        for future in as_completed(pending):
            key,value=future.result();results[key]=value
            write(ROOT/'progress.json',{'arms':results})
    checks={}
    for key in ('g002','black16'):
        checks[key]={'blue':results[key+'/candidate/blue']['wins']>=results[key+'/blue_control/blue']['wins'],
                     'red':results[key+'/candidate/red']['wins']>=results[key+'/red_control/red']['wins']}
    passed=all(all(v.values()) for v in checks.values())
    write(ROOT/'result.json',{'passed':passed,'checks':checks,'arms':results,'promotion_performed':False,'scope':DESIGN})
    source=STUDY/'hosted/blue_three/reviewed-feedback'
    if not (ROOT/'evaluated-feedback').exists():
        record(source/'policy.ir.json',source/'policy.bas',
               'User-requested parallel nonregression comparison: '+str({k:v['wins'] for k,v in results.items()})+
               f'. Checks{checks}; passed={passed}. Priorrelh/Jordan failures remain separate gates; no promotion.',
               ROOT/'result.json',ROOT/'evaluated-feedback')
    print('FINAL',passed,checks,flush=True)


if __name__=='__main__':main()
