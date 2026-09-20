"""Fresh exactrelh confirmation plus previously required blue preservation."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from relh154_scoped import STUDY,OLD
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze


def main():
    discovery=read(STUDY/'hosted-result.json');name=discovery['selected'];assert name in ('legacy','scoped')
    assert name in read(STUDY/'local/qualification.json')['qualified']
    review=read(STUDY/'hosted'/name/'review/decisions.json')['cases']
    assert review and all(r['win'] and r['proof']['all_state_hashes_equal'] and r['proof']['all_actions_consumed'] for r in review)
    assert all(max(v['tick'] for v in r['first_recalls'].values())<3222 for r in review)
    refs={}
    for key in ('relh154',):
        p=read(STUDY/'batches'/key/name/'blue/plan.json');refs[key]={'label':p['rival'],'id':p['rival_version']}
    for key in ('g002','black16','macro4'):
        p=read(OLD/'guards/batches'/key/'pair150/blue/plan.json');refs[key]={'label':p['rival'],'id':p['rival_version']}
    hosted.ROOT=STUDY/'confirmation';hosted.ROOT.mkdir(exist_ok=True)
    freeze(hosted.ROOT/'selection.json',{'candidate':name,'targets':refs,'source_sha256':digest((STUDY/'local/candidates'/name/'policy.bas').read_bytes()),
        'rule':'Fresh40relhRED40relhBLUE and40BLUEeachg002black16macro4 mustallwin. Discovery40JordanBLUE alreadyrequired40/40. Allruntime/replay/gearchecks. REDsourceunchanged plus6fullparities.',
        'discovery':digest((STUDY/'hosted-result.json').read_bytes()),'review':digest((STUDY/'hosted'/name/'review/decisions.json').read_bytes())})
    hosted.DESIGN='Fresh relh154 scoped-recall confirmation plus requiredpreservation:40red40blue exactrelh,40BLUEeachg002black16macro4. Must40/40allarms. Sourcefrozen; nointerimtuning.'
    v=read(STUDY/'hosted'/name/'uploaded-version.json');hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
    arms=[]
    for key,t in refs.items():
        for color in (('red','blue') if key=='relh154' else ('blue',)):
            arms.append(hosted.prepare(key,t['label'],name,color,t['id'])[0])
    results={}
    with ThreadPoolExecutor(4) as pool:
        for future in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            k,r=future.result();results[k]=r;write(hosted.ROOT/'progress.json',{'arms':results})
    passed=all(r['wins']==40 and r['all_full_audits_passed'] for r in results.values())
    write(hosted.ROOT/'result.json',{'name':name,'passed':passed,'arms':results,'promotion_performed':False})
    print('CONFIRMATION',name,passed,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__':main()
