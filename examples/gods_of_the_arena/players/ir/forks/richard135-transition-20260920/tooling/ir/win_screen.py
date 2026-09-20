"""Fresh win-first study; the previous duration-sensitive screen remains failed."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import shutil
from economy_screen import run
from policy_ir import HERE,bundle,digest,read,write,refresh_grounding,compile_policy
from release_workspace import RUN,SOURCE,VERSION,verify
STUDY=RUN/'win-first-study'
VARIANTS={'bounded':'Bound mobile pursuit to12tiles; preserve wave navigation and class combat, with the explicit dense-object recovery fallback.',
          'lanes':'Bound mobile pursuit plus public-map2/1/2lane navigation and the same explicit dense-object recovery fallback.'}
RULE=('Fresh study after complete failed360-game macro screen. Win priority follows latest user request: autoresearch the game and improve the gameplay for optimally winning. '
      'Old lane40/40 vsLich25/40 and274vs289deaths selected a hypothesis, not promotion. Faster games made prior deaths/alive-minute and totalXP gates reject. '
      'Now freeze40newpairedlocalgames/arm, two unchangedcandidates andcurrentLich. Need>=2morewins than current, meanhero deaths/game<=110%current, equipment everygame, allVM/replayvalidity; XP/min and deaths/alive-minute diagnostic, notselection. '
      'Atmost2advance to fresh100episode mixed-roster discovery againstcurrentLich; require>=5pp gain andsameguard. Then independent400candidatevs400current confirmation with>=5pp andone-sidedFisherp<.025, noadverseclassp<.005 andsamedeaths/gameguard. '
      '100sampledcurrentfieldgames>=50wins/allgear/fullvalidity beforepromotion. Directnamedrival40games/color probes describe twofixedlineups perrival; repeatedidenticaltrajectories are not independentgeneralization. '
      'Keep allpreviousfailedverdicts; nooutcomepooling, droppedseeds, interimtuning oroptionalstopping.')

def prepare():
    verify();d=STUDY/'local';d.mkdir(parents=True,exist_ok=True)
    if (d/'plan.json').exists():return d
    for n in ['episode','audit']:shutil.copy2(RUN/'r3/build'/n,d/n)
    for n in ['default.bas','config.json']:shutil.copy2(RUN/'local'/n,d/n)
    parent=RUN/'r3-study/reconciled/lich_nearest/policy.ir.json';sources={'current':str(RUN/'r3-study/reconciled/lich_nearest/policy.bas')}
    evidence=RUN/'macro-study/local/screen-result.json'
    for n in VARIANTS:
        before=read(RUN/'macro-study/local/candidates'/n/'policy.ir.json');p=deepcopy(before)
        p['goal']['G_fort']['preference']='Maximize binaryfortwins. Complete games efficiently; XP pergame is not a substitute forwinning.'
        p['goal']['G_survival']['preference']='Limit totalhero deaths percompletedgame relative to currentpolicy; report death intensity peralive-minute separately because game duration changes.'
        p['belief']['claims']['B_macro']={'claim':RULE,'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
        p['update']={'revision':before['update']['revision']+1,'parent':digest(before),'change':'New independent win-first hypothesis; executable unchanged.','needs_review':['belief/B_macro','goal/G_fort','goal/G_survival'],'evidence':p['belief']['claims']['B_macro']['evidence']}
        refresh_grounding(p);assert compile_policy(p)==compile_policy(before)
        bundle(p,d/'candidates'/n);sources[n]=str(d/'candidates'/n/'policy.bas')
    tools=d/'frozen-instruments';tools.mkdir()
    for p in HERE.glob('*.py'):
        if not p.name.startswith('test_'):shutil.copy2(p,tools/p.name)
    inputs=[d/n for n in ['episode','audit','config.json']]+[Path(p) for p in sources.values()]
    old=read(RUN/'local/plan.json')
    write(d/'plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),'family':'release','game_version':VERSION,'game_source':SOURCE,
       'variants':VARIANTS,'sources':sources,'inputs':{str(p):digest(p.read_bytes()) for p in inputs},
       'instruments':{p.name:digest(p.read_bytes()) for p in tools.glob('*.py')},'cases':[dict(c,seed=732000+i) for i,c in enumerate(old['cases'])],
       'win_thresholds':{'current':2},'survival_control':'current','selection_mode':'win_first','rule':RULE,
       'current_version':'3b5d11e5-cd80-4783-afae-0aa2ef1e4505','reuse':'Nooutcomesreused;120newlocalgames withfreshseeds732000..039.'})
    return d
if __name__=='__main__':
    d=prepare();run(d,8,'release')
    logs=list((d/'screen').glob('*/*/stdout.log'))
    if len(logs)!=120 or any('BASIC error:' in p.read_text() for p in logs):raise ValueError('Missing logs or invalidlocalVM')
    write(d/'vm-validity.json',{'games':120,'all_local_vm_logs_valid':True})
