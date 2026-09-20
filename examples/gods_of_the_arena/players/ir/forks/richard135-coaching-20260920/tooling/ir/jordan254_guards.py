"""Frozen selected-warning preservation checks against three exact incumbents."""
from concurrent.futures import ThreadPoolExecutor,as_completed

from economy_feedback import record
from jordan254_followup import STUDY
from macromackie_middle_rush import STUDY as PREVIOUS
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze

ROOT=STUDY/'guards'


def main():
    ROOT.mkdir(exist_ok=True)
    assert read(STUDY/'hosted-result.json')['outcome_qualified']==['warning100']
    assert 'warning100' in read(STUDY/'local/qualification.json')['qualified']
    old=read(PREVIOUS/'parallel-nonregression/result.json')['arms']
    macro=read(PREVIOUS/'review-result.json')['candidate']['colors']
    refs={
       'g002':(read(PREVIOUS/'parallel-nonregression/g002/resolved-target.json'),{c:old['g002/candidate/'+c]['wins'] for c in ['red','blue']}),
       'black16':(read(PREVIOUS/'parallel-nonregression/black16/resolved-target.json'),{c:old['black16/candidate/'+c]['wins'] for c in ['red','blue']}),
       'macro4':({'label':'macromackie-gota:v4','id':'1a78a3f9-8112-4c2c-831a-f0ffee8dbacc'},{c:macro[c]['win'] for c in ['red','blue']})}
    freeze(ROOT/'prospective.json',{'selected':'warning100','episodes_per_color':40,'targets':refs,
          'gate':'Match or exceed exactdeployed control wins on eachcolor/rival. All runtime/replay/roster/version/gear audits. Existing controls reused once, not freshpairedseeds; directional only.',
          'control_evidence':[str(PREVIOUS/'parallel-nonregression/result.json'),str(PREVIOUS/'review-result.json')],
          'candidate_evidence':digest((STUDY/'hosted-result.json').read_bytes()),'no_automatic_promotion':True})
    hosted.ROOT=ROOT/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Selected Jordan254 warning100: preserve exactg002v1 black16 macromackie4,40percolor allfullaudits. Prior exactdeployed controls explicitlyreused; source frozen; noautopromotion.'
    v=read(STUDY/'hosted/warning100/uploaded-version.json')
    hosted.VERSIONS['candidate']={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
    arms=[]
    for color in ['red','blue']:
        for key,(target,_) in refs.items():
            p,_=hosted.prepare(key,target['label'],'candidate',color,target['id']);arms.append(p)
    results={}
    with ThreadPoolExecutor(3) as pool:
        futures=[pool.submit(hosted.run_arm,p) for p in arms]
        for future in as_completed(futures):
            k,r=future.result();results[k]=r;write(ROOT/'progress.json',{'arms':results})
    checks={k:{c:results[k+'/candidate/'+c]['wins']>=control[c] for c in ['red','blue']} for k,(_,control) in refs.items()}
    result={'passed':all(all(v.values()) for v in checks.values()),'checks':checks,'arms':results,
            'controls':{k:v[1] for k,v in refs.items()},'promotion_performed':False}
    write(ROOT/'result.json',result)
    f=STUDY/'hosted/warning100/evaluated-feedback'
    if not (ROOT/'feedback').exists():record(f/'policy.ir.json',f/'policy.bas',
        'Selectedwarning100 preservation240games: '+str({k:v['wins'] for k,v in results.items()})+
        f'; checks{checks}. Exact prior deployed controls reused, no independenttrial claim. No automaticpromotion.',ROOT/'result.json',ROOT/'feedback')
    print('GUARDS',result['passed'],checks,{k:v['wins'] for k,v in results.items()},flush=True)


if __name__=='__main__':main()
