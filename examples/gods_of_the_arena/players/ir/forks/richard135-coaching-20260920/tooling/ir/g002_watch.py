"""Replay-guided red watch/advance experiment, with exact deployed blue behavior."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import subprocess
import sys
from binding import CONTRACTS
from policy_ir import read, write, digest, refresh_grounding, compile_policy, extract
from release_workspace import RUN
from rush_defense_eval import evaluate
from economy_feedback import record
from rush_hosted import upload
import middle_rush_parallel_checks as hosted

STUDY = RUN/'coached-lanes/r5-g002-red-objective'
PARENT = RUN/'coached-lanes/r5-relh154/scoped-followup/final-feedback'
VARIANTS = ('deployed', 'watch20', 'watch30')
RIVAL = 'a30542cb-54de-4109-92e6-bcabca7db4d8'
CONTROL = '53f15b12-2198-41d1-bb99-df4bdb1ff7fd'


def make(name):
    parent = read(PARENT/'policy.ir.json')
    if name == 'deployed': return parent
    assert name in VARIANTS
    p = deepcopy(parent); p['id'] = 'gota_red_'+name
    for key, skill in p['skill'].items():
        if key == 'observe':
            skill['operator'] = 'lineup_watch_defense'
            defaults = CONTRACTS[skill['operator']].parameters
            skill['parameters'] = {k: skill['parameters'].get(k,v[0]) for k,v in defaults.items()}
            skill['parameters']['redbranch_watch_quiet'] = 24*int(name[5:])
        if skill['operator'] == 'lineup_perimeter_route':
            skill['operator'] = 'lineup_counterpush_route'
            defaults = CONTRACTS[skill['operator']].parameters
            skill['parameters'] = {k: skill['parameters'].get(k,v[0]) for k,v in defaults.items()}
    p['goal']['G_defense']['preference'] += (' Red: defensive memory need not force stationary waiting. '
        'After '+name[5:]+' seconds of quiet after arrival, push while retaining the original threat lease. '
        'A newly observed survivor near a friendly structure can immediately recall the team. '
        'Defend a perimeter around the threatened structure, transfer destroyed anchors to home, '
        'and use distinct class rally destinations. Blue remains the exact deployed branch.')
    p['belief']['claims']['B_red_watch'] = {'status':'untested',
        'claim':'The reported four-hero clump issues identical accepted rally orders without targets; '
        'test bounded physical waiting while preserving the single-survivor recall memory, unlike rejected unconditional retirement.',
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Red watch and advance: '+name)
    refresh_grounding(p); return p


def local(seed=819200):
    assert read(STUDY/'vm-proof.json')['passed']
    opponents={'default':RUN/'r5/default.bas','current':Path(__file__).parent/'win_bounded_0916.r5.evaluated.bas',
               'center_proxy':RUN/'coached-lanes/r5-convoy/screen/candidates/center/policy.bas'}
    evaluate('local',list(VARIANTS),12,seed,make,STUDY,RUN/'r5/fast/audit-local',opponents_override=opponents)
    r=read(STUDY/'local/result.json'); metrics=r['metrics']; checks={}; qualified=[]
    for name in VARIANTS[1:]:
        proofs=[]
        for row in r['rows']:
            if row['name']==name and row['color']==1:
                d=STUDY/'local/games'
                proofs.append(json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(d/name/str(row['seed'])/'replay.bin'),str(d/'deployed'/str(row['seed'])/'replay.bin')],text=True)))
        parity=len(proofs)==6 and all(all(p[k] for k in ('all_actions_equal','all_state_hashes_equal','same_seed','setup_equal','config_equal')) for p in proofs)
        write(STUDY/'local'/('blue-parity-'+name+'.json'),{'passed':parity,'proofs':proofs})
        m=metrics[name]; b=metrics['deployed']
        checks[name]={'blue_parity':parity,'gear':m['all_gear'],'wins':m['wins']>=b['wins'],
                      'colors':all(m['colors'][c]>=b['colors'][c] for c in ('0','1'))}
        if all(checks[name].values()): qualified.append(name)
    write(STUDY/'local/qualification.json',{'qualified':qualified,'checks':checks,'metrics':metrics})
    print('LOCAL',qualified,{n:(m['wins'],m['deaths']) for n,m in metrics.items()},flush=True)


def remote():
    q=read(STUDY/'local/qualification.json');names=q['qualified']
    hosted.ROOT=STUDY/'discovery';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Red watch/advance prospective discovery.40episodes perarm exactg002v1, frozen release andlineup. All fullaudits. Freshdeployedcontrol. Candidate must add>=8wins and reach>=30/40 before fresh confirmation and preservation; no promotion from discovery.'
    hosted.VERSIONS['deployed']={'id':CONTROL,'name':'aaron-gota-ir-relh154-legacy-0916:v1'}
    arms=[hosted.prepare('g002','gota-g002:v1','deployed','red',RIVAL)[0]]
    for name in names:
        src=STUDY/'local/candidates'/name;feedback=STUDY/'qualified-feedback'/name
        if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas','Native mechanism tests and local12/color parity qualified; hosted unvalidated.',STUDY/'local/qualification.json',feedback)
        _,v=upload(name,STUDY,'aaron-gota-ir-redwatch','Retain threat memory while releasing quiet red defenders.',feedback_override=feedback)
        hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        arms.append(hosted.prepare('g002','gota-g002:v1',name,'red',RIVAL)[0])
    results={}
    with ThreadPoolExecutor(3) as pool:
        for f in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            k,r=f.result();results[k]=r;write(STUDY/'discovery-progress.json',results)
    b=results['g002/deployed/red']['wins']
    candidates=[n for n in names if results['g002/'+n+'/red']['wins']>=max(30,b+8)]
    candidates.sort(key=lambda n:(-results['g002/'+n+'/red']['wins'],n))
    write(STUDY/'discovery-result.json',{'qualified':candidates,'arms':results,'promotion_performed':False})
    print('DISCOVERY',candidates,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__': local() if sys.argv[1]=='local' else remote()
