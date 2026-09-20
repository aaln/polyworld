"""Explicit20-minute g002 red priority; complete targeted cohorts, no broad claim."""
from datetime import datetime,timezone,timedelta
from pathlib import Path
import time
from economy_feedback import record
from g002_coordination import STUDY as M
from g002_arrival import STUDY as N
from g002_activation import activated
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure_hosted import prepare_head,result
from rush_hosted import upload
from threat_coverage_hosted import control
from release_workspace import RUN
from win_hosted import live
ROOT=RUN/'coached-lanes/r5-g002-deadline'
DESIGN=('User explicitly prioritizes beating g002 on red within20minutes. '
        'Complete40red40blue per locally qualified candidate; at least32red/38blue '
        'plus full runtime/replay/equipment audits and exact localblue behavior. '
        'Compare deployedG24red40blue and Hanchor4red40blue, reusednotnew. '
        'This is a deadline-limited targeted selection, not a passed broad-field suite. '
        'Keep prior full-suite gates and failed studies intact. No interim source changes.')


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    if not (ROOT/'plan.json').exists():
        freeze(ROOT/'plan.json',{'started_at':datetime.now(timezone.utc).isoformat(),'deadline':(datetime.now(timezone.utc)+timedelta(minutes=19)).isoformat(),
            'authorization':'User: beatingg002red highestpriority, only20minutes beforecompetitionends. Earlier: deployimprovedpolicytobothplayerswhenready.',
            'candidates':[{'study':str(M),'name':'rally'},{'study':str(N),'name':'arrive20'}],
            'gates':{'red_wins':32,'blue_wins':38,'local_qualification':True,'native_activation':True,'runtime_equipment_replays':True},
            'selection':'Highest redwins, then totalwins, then fewer deaths; only completed80game cohorts eligible. Broad validation explicitly omitted undernewdeadlinepriority.',
            'maximum_games':160,'design':DESIGN})
    plan=read(ROOT/'plan.json');live();reports={}
    for case in plan['candidates']:
        study=Path(case['study']);name=case['name']
        for needed,proc in [('local/comparison.json','local-process.json'),('activation-proof.json','activation-process.json')]:
            while not (study/needed).exists():
                if not alive(read(study/proc)['pid']):raise RuntimeError('Validation workerstopped: '+needed)
                time.sleep(5)
        if name not in read(study/'local/comparison.json')['qualified']:
            reports[name]={'eligible':False,'reason':'Failed localqualification'};continue
        proof=read(study/'activation-proof.json');source=study/'local/candidates'/name/'policy.bas'
        if not proof['passed'] or not read(study/'vm-stress.json')['passed']:raise ValueError('Missing VM/nativeproof')
        if not any(r['name']==name and activated(r) and r['source_sha256']==digest(source.read_bytes()) for r in proof['rows']):raise ValueError('Sourceactivationnotproved')
        root,version=upload(name,study,'aaron-gota-ir-post-defense',
            'Refresh recalled attacker destinations without extending defense, separate actual-role rally destinations, and resume lane pressure after declared quiet interval while guarding visible near-base threats; preserve blue.',
            feedback_override=study/'activation-feedback'/name,
            validation_note='Local comparison, blue gameplay parity, focused VM tests and full native behavior activation passed. Hosted g002 and field unvalidated; inert experiment.')
        head=root/'deadline-g002';prepare_head(head,version,control('gota-g002:v1'),'Deadline priority g002 red; '+name,DESIGN)
        write(ROOT/'active.json',case|{'version':version,'head':str(head)})
        a=result(head);passed=a['colors']['red']['win']>=32 and a['colors']['blue']['win']>=38
        report={'study':str(study),'name':name,'version':version,'result':a,'eligible':passed,'source_sha256':digest(source.read_bytes()),'head':str(head),'scope':DESIGN}
        reports[name]=report;write(ROOT/'progress.json',{'results':reports})
        if not (root/'deadline-feedback').exists():
            src=study/'activation-feedback'/name
            record(src/'policy.ir.json',src/'policy.bas',f'Deadline target complete80games g002: {a["colors"]}; targetedeligibility{passed}. Broad-field,Richard/Jordan and mixed10-player coverage remain unverified for thissource. Priorstudygatesunchanged.',head/'result.json',root/'deadline-feedback')
        print(name,a['colors'],'eligible',passed,flush=True)
    eligible=[r for r in reports.values() if r.get('eligible')]
    eligible.sort(key=lambda r:(-r['result']['colors']['red']['win'],-r['result']['wins'],sum(x['deaths'] for x in r['result']['rows'])))
    write(ROOT/'result.json',{'selected':eligible[0]['name'] if eligible else None,'results':reports,'plan_sha256':digest((ROOT/'plan.json').read_bytes()),'promotion_performed':False})

if __name__=='__main__':main()
