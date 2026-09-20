"""Pre-registered blue side-siege recall study versus exact relh154."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from binding import CONTRACTS
from economy_feedback import record
from policy_ir import read,write,digest,refresh_grounding,compile_policy,extract
from ranger_guard_hosted import freeze
from release_workspace import RUN
from rush_defense_eval import evaluate
from rush_hosted import upload
import middle_rush_parallel_checks as hosted

STUDY=RUN/'coached-lanes/r5-relh154'
PARENT=RUN/'coached-lanes/r5-jordan254/warning-followup/final-feedback'
VARIANTS=('deployed','wide100','pair50','pair150')
LABEL='relh-gods-of-the-arena:v154'
RIVAL='99ff8b49-8bb6-4ee2-9204-ff24a8efda4e'
RECORD=Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-18-relh154-blue-warning.md')


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name=='deployed':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='gota_relh154_'+name
    observer=p['skill']['observe'];observer['parameters']['home_tiles']=100
    if name.startswith('pair'):
        observer['operator']='lineup_paired_siege'
        for key,spec in CONTRACTS[observer['operator']].parameters.items():
            observer['parameters'].setdefault(key,spec[0])
        observer['parameters'].update(pair_damage=int(name[4:]),pair_opening=3600,arrival_tiles=18)
        if name=='pair150':observer['parameters']['blue_hold']=1440
    p['goal']['G_defense']['preference']+=' Blue: include standing outer side-lane towers within100tiles of home in visible pressure detection.'
    if name.startswith('pair'):
        p['goal']['G_defense']['preference']+=(' During first3600ticks, a pair of visible living enemy heroes near an observed damaged standing side-lane tower can initiate recall. '+name[4:]+'HP must be missing. Travel farther than18tiles from the defensive objective is not quiet arrival; ordinary hold deadlines still apply. Red behavior remains exactly the deployed branch.')
    p['belief']['claims']['B_relh_warning']={'status':'untested','claim':'Observed relh154 blue losses recall most heroes at3222 after all three attacked-side towers fall; test earlier evidence-gated warning, not opponent identity or hidden knowledge.',
       'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Blue side-siege warning: '+name)
    refresh_grounding(p);return p


def local(seed=819000):
    opponents={'default':RUN/'r5/default.bas','current':Path(__file__).parent/'win_bounded_0916.r5.evaluated.bas',
               'center_proxy':RUN/'coached-lanes/r5-convoy/screen/candidates/center/policy.bas'}
    assert read(STUDY/'vm-proof.json')['passed']
    evaluate('local',list(VARIANTS),12,seed,make,STUDY,RUN/'r5/fast/audit-local',opponents_override=opponents)
    result=read(STUDY/'local/result.json');metrics=result['metrics'];qualified=[];checks={}
    for name in VARIANTS[1:]:
        proofs=[]
        for row in result['rows']:
            if row['name']==name and row['color']==0:
                d=STUDY/'local/games'
                proof=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(d/name/str(row['seed'])/'replay.bin'),str(d/'deployed'/str(row['seed'])/'replay.bin')],text=True))
                proofs.append(proof)
        parity=len(proofs)==6 and all(all(r[k] for k in ('all_actions_equal','all_state_hashes_equal','same_seed','setup_equal','config_equal')) for r in proofs)
        write(STUDY/'local'/('red-parity-'+name+'.json'),{'passed':parity,'proofs':proofs})
        m=metrics[name];b=metrics['deployed']
        checks[name]={'red_parity':parity,'all_gear':m['all_gear'],'wins':m['wins']>=b['wins'],
                      'colors':all(m['colors'][c]>=b['colors'][c] for c in ('0','1'))}
        if all(checks[name].values()):qualified.append(name)
    write(STUDY/'local/qualification.json',{'qualified':qualified,'checks':checks,'metrics':metrics})
    print('LOCAL',qualified,{n:(m['wins'],m['deaths']) for n,m in metrics.items()},flush=True)


def remote():
    qualification=read(STUDY/'local/qualification.json');names=qualification['qualified']
    hosted.ROOT=STUDY/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Frozen exactrelh154 blue side-siege warning study.40blueepisodes perqualifiedarm, allfullaudits.>=38permitsfresh40red40blue confirmation;40/40both required. Noautomaticpromotion.'
    arms=[]
    for name in names:
        src=STUDY/'local/candidates'/name;feedback=STUDY/'qualified-feedback'/name
        if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas',
            'Local12case runtime/gear/redparity and native detector checks passed. Hosted unvalidated. '+str(qualification['metrics'][name]),
            STUDY/'local/qualification.json',feedback)
        root,v=upload(name,STUDY,'aaron-gota-ir-relh154','Earlier blue observed side-siege warning.',feedback_override=feedback)
        hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        path,_=hosted.prepare('relh154',LABEL,name,'blue',RIVAL);arms.append(path)
    results={}
    with ThreadPoolExecutor(3) as pool:
        for future in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            key,r=future.result();results[key]=r;write(STUDY/'progress.json',{'arms':results})
    passed=[n for n in names if results['relh154/'+n+'/blue']['wins']>=38]
    write(STUDY/'hosted-result.json',{'outcome_qualified':passed,'arms':results,'mechanism_review_pending':True,'promotion_performed':False})
    print('HOSTED',passed,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__':local() if sys.argv[1]=='local' else remote()
