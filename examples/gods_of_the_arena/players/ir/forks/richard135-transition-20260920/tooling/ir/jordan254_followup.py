"""Separate direct-rival diagnostic and fresh relative local comparison.

The first screen's default4/4 gate failed for all candidates (and its baseline
was3/4). Preserve that verdict. These frozen sources require new evidence;
no threshold in the earlier experiment is rewritten.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys

from economy_feedback import record
from jordan254_research import LABEL,STUDY as BASE
from jordan254_warning import STUDY as PRIOR
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze
from release_workspace import RUN
from rush_defense_eval import evaluate
from rush_hosted import upload

STUDY=BASE/'warning-followup'
NAMES=['warning100','reach14']


def make(name):
    return read(PRIOR/'local/candidates'/name/'policy.ir.json')


def prepare():
    STUDY.mkdir(exist_ok=True)
    freeze(STUDY/'prospective.json',{'hypothesis':'Earlier observed outer pressure response may prevent the lost lane and return journey.',
      'prior_failed_screen':str(PRIOR/'local/qualification.json'),'prior_screen_passed':False,
      'source_hashes':{n:digest((PRIOR/'local/candidates'/n/'policy.bas').read_bytes()) for n in ['deployed',*NAMES]},
      'selection':'warning100 minimalchange and reach14 lowerlocaldeaths169vs176; wave14excluded227deaths. Selected before any candidateJordan results.',
      'fresh_local':{'cases_per_arm':60,'seed':817000,'rule':'allruntime/gear;30bluefullgameparity;wins/colors/opponents>=deployed. Local proof only, not competitive verdict.'},
      'hosted':{'cases_per_color':40,'candidates':NAMES,'rule':'>=32red38blue and actual earlierrecall. This is new followup; earlier failedscreen retained.'},
      'promotion':'No automaticpromotion. Freshlocal and hostedmechanism gates plus40/color g002v1 black16 macromackie4 comparison todeployed required.'})


def local():
    prepare()
    old=read(PRIOR/'local/plan.json')
    evaluate('local',['deployed',*NAMES],60,817000,make,STUDY,RUN/'r5/fast/audit-local',opponents_override=old['opponents'])
    result=read(STUDY/'local/result.json');m=result['metrics'];checks={}
    for n in NAMES:
        proofs=[]
        for row in result['rows']:
            if row['name']==n and row['color']==1:
                d=STUDY/'local/games'
                proofs.append(json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(d/n/str(row['seed'])/'replay.bin'),str(d/'deployed'/str(row['seed'])/'replay.bin')],text=True)))
        parity=len(proofs)==30 and all(all(r[k] for k in ['all_actions_equal','all_state_hashes_equal','same_seed','setup_equal','config_equal']) for r in proofs)
        write(STUDY/'local'/('blue-parity-'+n+'.json'),{'passed':parity,'proofs':proofs})
        checks[n]={'blue_parity':parity,'all_gear':m[n]['all_gear'],'wins':m[n]['wins']>=m['deployed']['wins'],
                   'colors':all(m[n]['colors'][c]>=m['deployed']['colors'][c] for c in ['0','1']),
                   'opponents':all(m[n]['opponents'][o]>=m['deployed']['opponents'][o] for o in m[n]['opponents'])}
    write(STUDY/'local/qualification.json',{'qualified':[n for n,c in checks.items() if all(c.values())],'checks':checks,'metrics':m,'prior_screen_still_failed':True})
    print('LOCAL',{n:(v['wins'],v['deaths']) for n,v in m.items()},checks,flush=True)


def remote():
    prepare()
    hosted.ROOT=STUDY/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Frozen directJordan254 diagnostic after initialscreen absolute-default gatefailed; freshrelative-local comparisonseparate.40percolor fullaudits. Noautomaticpromotion.'
    target=read(BASE/'baseline/jordan254/resolved-target.json');arms=[]
    for n in NAMES:
        src=PRIOR/'local/candidates'/n;feedback=STUDY/'diagnostic-feedback'/n
        if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas',
            'Originalscreen default4/4 gateFAILED (candidate3/4 baseline3/4); all11/12,bluefullparity andnativeVM pass. New directrivaldiagnostic; freshrelative60cases pending. No promotion fromthis alone.',
            STUDY/'prospective.json',feedback)
        root,v=upload(n,STUDY,'aaron-gota-ir-j254','Earlier red outer-lane threat coverage.',feedback_override=feedback,candidate_override=src,
                      validation_note='Originalscreen default gatefailed, retained; native runtime/IR/blueparitypassed. Separatehosted diagnostic andfreshlocal pending. Inertupload.')
        hosted.VERSIONS[n]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        for color in ('red','blue'):
            p,_=hosted.prepare('jordan254',LABEL,n,color,target['id']);arms.append(p)
    results={}
    with ThreadPoolExecutor(4) as pool:
        futures=[pool.submit(hosted.run_arm,p) for p in arms]
        for future in as_completed(futures):
            k,r=future.result();results[k]=r;write(STUDY/'progress.json',{'arms':results})
    passed=[n for n in NAMES if results['jordan254/'+n+'/red']['wins']>=32 and results['jordan254/'+n+'/blue']['wins']>=38]
    write(STUDY/'hosted-result.json',{'outcome_qualified':passed,'arms':results,'mechanism_review_pending':True,'promotion_performed':False,'prior_screen_still_failed':True})
    for n in NAMES:
        f=STUDY/'diagnostic-feedback'/n;out=STUDY/'hosted'/n/'evaluated-feedback'
        if not out.exists():record(f/'policy.ir.json',f/'policy.bas',
            'Jordan254 full40/color diagnostic: '+str({c:results['jordan254/'+n+'/'+c]['wins'] for c in ['red','blue']})+
            f'. Outcomequalified={n in passed}; originalscreen failed; freshlocal/actualmechanism/broadguards separate. No promotion.',STUDY/'hosted-result.json',out)
    print('HOSTED',passed,{k:v['wins'] for k,v in results.items()},flush=True)


if __name__=='__main__':
    local() if sys.argv[1]=='local' else remote()
