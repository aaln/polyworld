import json,subprocess
from pathlib import Path
from g002_retention import STUDY,VARIANTS,make
from rush_defense_eval import evaluate
from ranger_guard_hosted import freeze
from policy_ir import read,write,digest,compile_policy,extract
from release_workspace import RUN
from league_threat_review import run_native
from economy_feedback import record
from red_pressure_hosted import prepare_head,result
from rush_hosted import upload
from threat_coverage_hosted import control
from win_hosted import live
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case

DESIGN='Final deadline experiment directly fromdeployedG; shorten red sentryhold300to60seconds, optionally survivorrenewal48to24tiles. No combat/support/rally change. Twelve localgamesperarm versuscontrols, exact6bluegameparity, nativeallactions/hash and denseVM. Choose single localwinner bywins thenfewestdeaths; complete40red40blue exactg002. Require32red38blue. Broaderfield unvalidated. Priorfailedstudies remainfailed.'

def main():
    freeze(STUDY/'prospective.json',{'design':DESIGN,'variants':VARIANTS,'seed':814000,'count':12,'red_floor':32,'blue_floor':38})
    f.RealVmTests.setUpClass.__func__(f.RealVmTests)
    class V(u.UnblockTests):
        factory=staticmethod(make)
        vm=f.RealVmTests.vm
    vm=V();rows=[]
    for name in VARIANTS[1:]:
        p=make(name);assert extract(compile_policy(p),p)==p
        for slot in range(5):
            for density in (40,160,240):
                d=defense_case(slot,count=4)
                d['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(d['objects']))]
                rows+=vm.play(name,[d],('defUntil','defActive'))
        for slot in (0,2,3):
            d=defense_case(slot,count=4)
            q=defense_case(slot,count=0);q['self']['worldTick']=1540
            z=vm.play(name,[d,q],('defUntil','defActive'))
            assert z[0]['memory']['defUntil']==1540 and z[1]['memory']['defActive']==0
            assert vm.play('deployed',[d,q],('defActive',))[-1]['memory']['defActive']==1
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),'scope':'Actualredroles dense40/160/240; sentry expires1540 after100trigger while deployedretainsdefense.'})
    evaluate('local',VARIANTS,12,814000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics'];b=m['deployed'];qualified=[]
    for name in VARIANTS[1:]:
        proofs=[]
        for row in r['rows']:
            if row['name']==name and row['color']==1:
                root=STUDY/'local/games';proofs.append(json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(root/name/str(row['seed'])/'replay.bin'),str(root/'deployed'/str(row['seed'])/'replay.bin')],text=True)))
        blue=len(proofs)==6 and all(all(p[k] for k in ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in proofs)
        write(STUDY/'local'/('blue-parity-'+name+'.json'),{'passed':blue,'rows':proofs})
        a=m[name]
        if a['all_gear'] and a['wins']>=b['wins'] and all(a['colors'][c]>=b['colors'][c] for c in b['colors']) and all(a['opponents'][o]>=b['opponents'][o] for o in b['opponents']) and blue:qualified.append(name)
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n))
    write(STUDY/'local/comparison.json',{'qualified':qualified,'selected':qualified[0] if qualified else None,'metrics':m,'scope':DESIGN})
    if not qualified:write(STUDY/'deadline-result.json',{'selected':None,'results':{},'reason':'No localqualifier'});return
    name=qualified[0];src=STUDY/'local/candidates'/name
    case=next(x for x in r['rows'] if x['name']==name and x['color']==0)
    out=STUDY/'activation';out.mkdir(exist_ok=True)
    proof=run_native('replay-slots-probe',STUDY/'local/games'/name/str(case['seed'])/'replay.bin',out/'decisions.jsonl',{'PROBE_POLICY':str(src/'policy.bas'),'PROBE_SLOTS':'0,1,2,3,4'})
    passed=proof['all_actions_consumed'] and proof['all_state_hashes_equal']
    write(STUDY/'activation-proof.json',{'passed':passed,'rows':[{'name':name,'source_sha256':digest((src/'policy.bas').read_bytes()),'proof':proof}],'scope':'Full source replay; actual expiration specifically proven in nativeVM fixtures. No newrelease/spread operator enabled.'})
    if not passed:raise ValueError('Nativefailure')
    feedback=STUDY/'activation-feedback'/name
    record(src/'policy.ir.json',src/'policy.bas','Deadline local12gamesperarm andfullnative replay passed. Behavioral expiration proven bynativeVM. Hostedg002pending; widerfield untested.',STUDY/'activation-proof.json',feedback)
    live();root,v=upload(name,STUDY,'aaron-gota-ir-retention',DESIGN,feedback_override=feedback,validation_note='Deadline local12perarm controls/blueparity/fullnativeVM/replay passed. Hostedunvalidated inertcandidate.')
    head=root/'deadline-g002';prepare_head(head,v,control('gota-g002:v1'),'Deadline direct deployedretention versusg002',DESIGN)
    a=result(head);passed=a['colors']['red']['win']>=32 and a['colors']['blue']['win']>=38
    record(feedback/'policy.ir.json',feedback/'policy.bas',f'Completeg00280:{a["colors"]}; targetedeligibility{passed}; widerfielduntested.',head/'result.json',root/'deadline-feedback')
    item={'study':str(STUDY),'name':name,'version':v,'result':a,'eligible':passed,'source_sha256':digest((src/'policy.bas').read_bytes()),'head':str(head),'scope':DESIGN}
    write(STUDY/'deadline-result.json',{'selected':name if passed else None,'results':{name:item},'promotion_performed':False})
    print('FINAL',name,a['colors'],passed,flush=True)
if __name__=='__main__':main()
