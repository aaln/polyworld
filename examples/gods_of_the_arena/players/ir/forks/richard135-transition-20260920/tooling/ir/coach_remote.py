"""Forty-game batches for locally qualified coaching variants; no promotion."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from coach_assembled import STUDY
from g002_watch import CONTROL, RIVAL, PARENT
from policy_ir import read, write
from economy_feedback import record
from rush_hosted import upload
import middle_rush_parallel_checks as hosted
from pathlib import Path

RECORD=Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-18-coached-assembled-center.md')


def log_requests():
    ids=[read(p)['id'] for p in STUDY.glob('**/batch/created.json')]
    s=RECORD.read_text();s=re.sub(r'^evals:.*$', 'evals: '+json.dumps(sorted(ids)),s,flags=re.M)
    RECORD.write_text(s)


def run(roots, output):
    results={}
    with ThreadPoolExecutor(3) as pool:
        for f in as_completed([pool.submit(hosted.run_arm,p) for p in roots]):
            k,r=f.result();results[k]=r;write(STUDY/(output+'-progress.json'),results);log_requests()
    return results


def discovery():
    names=read(STUDY/'local/qualification.json')['qualified']
    assert names, 'No local qualifier'
    hosted.ROOT=STUDY/'discovery';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Coaching session0918: assembly-qualified two-support rear guard and three centerattackers. Forty games/arm RED exactg002 with fresh deployedcontrol. No interim tuning; require >=30wins and+8 before fresh confirmation. Fixedlineup correlated seeds; full audits.'
    hosted.VERSIONS['deployed']={'id':CONTROL,'name':'aaron-gota-ir-relh154-legacy-0916:v1'}
    roots=[hosted.prepare('g002','gota-g002:v1','deployed','red',RIVAL)[0]]
    for name in names:
        src=STUDY/'local/candidates'/name;feedback=STUDY/'qualified-feedback'/name
        if not feedback.exists():
            record(src/'policy.ir.json',src/'policy.bas','Native VM tests and the prespecified local aggregate/color gate passed, with six complete BLUE gameplay parities. Inspect opponent-level tradeoffs in qualification.json; hosted unvalidated.',STUDY/'local/qualification.json',feedback)
        _,v=upload(name,STUDY,'aaron-gota-ir-coach','Coached assembly-qualified two-guard three-center push.',feedback_override=feedback)
        hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        roots.append(hosted.prepare('g002','gota-g002:v1',name,'red',RIVAL)[0])
    results=run(roots,'discovery')
    base=results['g002/deployed/red']['wins']
    qualified=[n for n in names if results['g002/'+n+'/red']['wins']>=max(30,base+8)]
    qualified.sort(key=lambda n:(-results['g002/'+n+'/red']['wins'],n))
    write(STUDY/'discovery-result.json',{'qualified':qualified,'arms':results,'promotion_performed':False})
    print('DISCOVERY',qualified,{k:r['wins'] for k,r in results.items()},flush=True)


def confirmation():
    discovery=read(STUDY/'discovery-result.json');assert discovery['qualified']
    name=discovery['qualified'][0];v=read(STUDY/'hosted'/name/'uploaded-version.json')
    hosted.ROOT=STUDY/'confirmation';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Coached split fresh confirmation and regression guard.40games/arm: REDg002>=30and8more thanfreshbaseline; REDrelh154Jordan254macro4 all40wins; black16no declinevs0. BLUEg002relh all40wins. Full audit and mechanism review before any champion promotion.'
    hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
    hosted.VERSIONS['deployed']={'id':CONTROL,'name':'aaron-gota-ir-relh154-legacy-0916:v1'}
    targets=[('g002','gota-g002:v1',RIVAL,'red'),('g002','gota-g002:v1',RIVAL,'blue')]
    for key,sub in [('relh154','confirmation/relh154/legacy/blue'),('black16','confirmation/black16/legacy/blue'),('macro4','confirmation/macro4/legacy/blue'),('jordan254','batches/jordan254/legacy/blue')]:
        p=read(PARENT.parent/sub/'plan.json')
        targets.append((key,p['rival'],p['rival_version'],'red'))
        if key=='relh154':targets.append((key,p['rival'],p['rival_version'],'blue'))
    roots=[hosted.prepare(k,label,name,color,rid)[0] for k,label,rid,color in targets]
    roots.append(hosted.prepare('g002','gota-g002:v1','deployed','red',RIVAL)[0])
    results=run(roots,'confirmation')
    base=results['g002/deployed/red']['wins']
    passed=all(r['wins']>=(max(30,base+8) if k=='g002/'+name+'/red' else 0 if k.startswith('black16/') else 40)
               for k,r in results.items() if '/deployed/' not in k)
    write(STUDY/'confirmation-result.json',{'selected':name,'all_outcome_gates_passed':passed,'arms':results,'promotion_performed':False,'mechanism_review_required':True})
    print('CONFIRM',passed,{k:r['wins'] for k,r in results.items()},flush=True)


if __name__=='__main__': discovery() if sys.argv[1]=='discovery' else confirmation()
