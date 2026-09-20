"""Fresh g002 red confirmation plus existing champion preservation checks."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from g002_watch import STUDY,PARENT,RIVAL
from policy_ir import read,write
import middle_rush_parallel_checks as hosted


def main():
    discovery=read(STUDY/'discovery-result.json')
    assert discovery['qualified'], 'No discovery qualifier; do not spend confirmation XP'
    name=discovery['qualified'][0]
    version=read(STUDY/'hosted'/name/'uploaded-version.json')
    hosted.ROOT=STUDY/'confirmation';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Prospectivelydeclared red watch/advance confirmation.40episodes perarm exactrosters. FreshREDg002>=30; preserve40REDrelh154Jordan254macro4; black16 baseline0; BLUEg002relh15440each plus sixfullgameBLUEparities. Full audits; no automatic promotion.'
    hosted.VERSIONS[name]={'id':version['id'],'name':version['name']+':v'+str(version['version'])}
    previous=PARENT.parent
    targets=[('g002','gota-g002:v1',RIVAL,'red'),('g002','gota-g002:v1',RIVAL,'blue')]
    for key,sub in [('relh154','confirmation/relh154/legacy/blue'),('black16','confirmation/black16/legacy/blue'),('macro4','confirmation/macro4/legacy/blue'),('jordan254','batches/jordan254/legacy/blue')]:
        path=previous/sub/'plan.json'
        if not path.exists():
            choices=[p for p in previous.glob('confirmation/*/legacy/blue/plan.json') if key.replace('16','').replace('4','') in read(p)['rival_key']]
            assert len(choices)==1,(key,path,choices)
            path=choices[0]
        p=read(path)
        targets.append((key,p['rival'],p['rival_version'],'red'))
        if key=='relh154':targets.append((key,p['rival'],p['rival_version'],'blue'))
    roots=[hosted.prepare(k,label,name,color,rival)[0] for k,label,rival,color in targets]
    results={}
    with ThreadPoolExecutor(4) as pool:
        for f in as_completed([pool.submit(hosted.run_arm,p) for p in roots]):
            k,r=f.result();results[k]=r;write(STUDY/'confirmation-progress.json',results)
    passed=all(r['wins'] >= (30 if k=='g002/'+name+'/red' else 0 if k=='black16/'+name+'/red' else 40) for k,r in results.items())
    write(STUDY/'confirmation-result.json',{'selected':name,'all_outcome_gates_passed':passed,'arms':results,'promotion_performed':False,'mechanism_review_required':True})
    print('CONFIRM',passed,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__':main()
