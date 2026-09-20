"""Red outer-lane warning hypotheses; retain the exact deployed blue branch."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from binding import CONTRACTS
from economy_feedback import record
from hero_binding import class_id
from jordan254_research import STUDY as BASE, PARENT, LABEL
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest,refresh_grounding,compile_policy,extract
from ranger_guard_hosted import freeze
from release_workspace import RUN
from rush_defense_eval import evaluate
from rush_hosted import upload
from test_rush_defense import scene
from test_rush_unblock import UnblockTests
import test_policy_ir as f

STUDY=BASE/'outer-warning'
RECORD=Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-18-jordan254-outer-warning.md')
VARIANTS={'deployed':{},'warning100':{'redbranch_home_tiles':100},
          'reach14':{'redbranch_home_tiles':100,'redbranch_intercept_tiles':14},
          'wave14':{'redbranch_home_tiles':100,'redbranch_intercept_tiles':14,'redbranch_creep_first':1}}


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name=='deployed':return parent
    p=deepcopy(parent);p['id']='gota_jordan254_'+name
    p['skill']['observe']['parameters'].update(VARIANTS[name])
    p['goal']['G_defense']['preference']+=' On red, detect observed enemy groups near outer side-lane towers up to100tiles from home; require existing group and standing-anchor evidence. This is shared visible pressure, not hidden enemy prediction.'
    if name!='warning100':p['goal']['G_defense']['preference']+=' Defenders may select mobile enemies within14tiles instead of10, retaining the existing threat-location bounds.'
    if name=='wave14':p['goal']['G_defense']['preference']+=' During active defense prefer enemy creeps to remove siege support before enemy heroes.'
    evidence=BASE/'baseline-review/decisions.json'
    p['belief']['claims']['B_outer_warning']={'status':'untested','claim':RECORD.read_text(),
       'evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Jordan254 outer-lane warning: '+name)
    refresh_grounding(p);return p


def local():
    STUDY.mkdir(exist_ok=True)
    freeze(STUDY/'prospective.json',{'record_sha256':digest(RECORD.read_bytes()),'variants':VARIANTS,'local_count':12,'seed':816000,
        'qualification':'allgear;full6blueparity;default4/4;wins>=parent-1;nativeVM;IRparity',
        'hosted':'40red40blue perqualifier; target32red38blue plusactualearlierrecall; noautopromotion'})
    class VM(UnblockTests):factory=staticmethod(make)
    VM.setUpClass();vm=VM();rows=[]
    for name in VARIANTS:
        p=make(name);assert extract(compile_policy(p),p)==p
        q=p['skill']['observe'];b=make('deployed')['skill']['observe']
        assert CONTRACTS[q['operator']].source(q['parameters']).split('\nelse\n',1)[1]==CONTRACTS[b['operator']].source(b['parameters']).split('\nelse\n',1)[1]
        for slot in range(5):
            case=scene(0,count=4,worldTick=960)
            case['self'].update(selfId=100+slot,selfClass=class_id(0,slot),selfX=102,selfY=98)
            case['objects'][2].update(objectId=10,objectX=23,objectY=12)
            for i,e in enumerate(case['objects'][4:]):e.update(objectX=18+i%2,objectY=13,objectClass=class_id(1,i),objectTarget=10)
            row=vm.play(name,[case],('defActive','defCount','defAnchor'))[0];rows.append(row)
            assert bool(row['memory']['defActive'])==(name!='deployed')
            for kind in ('small_group','dead_anchor','dense'):
                c=deepcopy(case)
                if kind=='small_group':c['objects']=c['objects'][:-1]
                if kind=='dead_anchor':c['objects'][2]['objectHp']=0
                if kind=='dense':c['objects'] += [f.obj(3000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
                rr=vm.play(name,[c],('defActive',))[0];rows.append(rr)
                if kind!='dense':assert rr['memory']['defActive']==0
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})
    opponents={'default':RUN/'r5/default.bas','current':Path(__file__).parent/'win_bounded_0916.r5.evaluated.bas',
               'center_proxy':RUN/'coached-lanes/r5-convoy/screen/candidates/center/policy.bas'}
    evaluate('local',list(VARIANTS),12,816000,make,STUDY,RUN/'r5/fast/audit-local',opponents_override=opponents)
    result=read(STUDY/'local/result.json');metrics=result['metrics'];qualified=[];checks={}
    for name in list(VARIANTS)[1:]:
        proofs=[]
        for row in result['rows']:
            if row['name']==name and row['color']==1:
                d=STUDY/'local/games'
                proof=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(d/name/str(row['seed'])/'replay.bin'),str(d/'deployed'/str(row['seed'])/'replay.bin')],text=True))
                proofs.append(proof)
        parity=len(proofs)==6 and all(all(r[k] for k in ('all_actions_equal','all_state_hashes_equal','same_seed','setup_equal','config_equal')) for r in proofs)
        write(STUDY/'local'/('blue-parity-'+name+'.json'),{'passed':parity,'proofs':proofs})
        m=metrics[name];checks[name]={'blue_parity':parity,'all_gear':m['all_gear'],'default':m['opponents']['default']==4,'wins':m['wins']>=metrics['deployed']['wins']-1}
        if all(checks[name].values()):qualified.append(name)
    write(STUDY/'local/qualification.json',{'qualified':qualified,'checks':checks,'metrics':metrics})
    print('LOCAL',qualified,{n:(m['wins'],m['deaths']) for n,m in metrics.items()},flush=True)


def remote():
    qualification=read(STUDY/'local/qualification.json');names=qualification['qualified']
    hosted.ROOT=STUDY/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Frozen red outer-warning study against exactJordan254;40episodes percolor, fullaudits. Earlier recall and>=32red38blue required. Noautomaticpromotion.'
    target=read(BASE/'baseline/jordan254/resolved-target.json');arms=[]
    for name in names:
        src=STUDY/'local/candidates'/name;feedback=STUDY/'qualified-feedback'/name
        if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas',
            'Local12case runtime/gear/blueparity and native detector checks passed. Hosted unvalidated. '+str(qualification['metrics'][name]),
            STUDY/'local/qualification.json',feedback)
        root,v=upload(name,STUDY,'aaron-gota-ir-j254','Red outer-lane warning and optional reach/creep defense.',feedback_override=feedback)
        hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        for color in ('red','blue'):
            path,_=hosted.prepare('jordan254',LABEL,name,color,target['id']);arms.append(path)
    results={}
    with ThreadPoolExecutor(3) as pool:
        for key,r in pool.map(hosted.run_arm,arms):
            results[key]=r;write(STUDY/'progress.json',{'arms':results})
    passed=[n for n in names if results['jordan254/'+n+'/red']['wins']>=32 and results['jordan254/'+n+'/blue']['wins']>=38]
    write(STUDY/'hosted-result.json',{'outcome_qualified':passed,'arms':results,'mechanism_review_pending':True,'promotion_performed':False})
    for n in names:
        src=STUDY/'qualified-feedback'/n;out=STUDY/'hosted'/n/'evaluated-feedback'
        if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
             'ExactJordan25440percolor: '+str({c:results['jordan254/'+n+'/'+c]['wins'] for c in ('red','blue')})+
             f'; outcomequalified={n in passed}. Nativehostedmechanism/broadguards pending; nopromotion.',STUDY/'hosted-result.json',out)
    print('HOSTED',passed,{k:r['wins'] for k,r in results.items()},flush=True)


if __name__=='__main__':
    local() if sys.argv[1]=='local' else remote()
