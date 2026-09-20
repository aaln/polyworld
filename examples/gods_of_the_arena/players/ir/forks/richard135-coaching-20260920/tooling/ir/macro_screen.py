"""Frozen fresh local macro screen on the current game release."""
from datetime import datetime,timezone
from pathlib import Path
import shutil
from economy_screen import run
from macro_candidates import VARIANTS,make
from policy_ir import HERE,bundle,digest,read,write
from release_workspace import RUN,SOURCE,VERSION,verify
STUDY=RUN/'macro-study'
def prepare():
    verify();d=STUDY/'local';d.mkdir(parents=True,exist_ok=True)
    if (d/'plan.json').exists():return d
    for n in ['episode','audit']:shutil.copy2(RUN/'r3/build'/n,d/n)
    for n in ['config.json','default.bas']:shutil.copy2(RUN/'local'/n,d/n)
    (d/'screen').mkdir(exist_ok=True)
    old=read(RUN/'local/plan.json');sources={}
    for n in ['v2','cadence','default']:
        sources[n]=old['sources'][n]
    sources['lich_nearest']=str(RUN/'lich-followup/local/candidates/lich_nearest/policy.bas')
    for n in ['budget_control',*VARIANTS]:
        bundle(make(n),d/'candidates'/n);sources[n]=str(d/'candidates'/n/'policy.bas')
    tools=d/'frozen-instruments';tools.mkdir()
    for p in HERE.glob('*.py'):
        if not p.name.startswith('test_'):shutil.copy2(p,tools/p.name)
    inputs=[d/n for n in ['episode','audit','config.json']]+[Path(p) for p in sources.values()]
    write(d/'plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),'family':'release',
       'game_version':VERSION,'game_source':SOURCE,'variants':VARIANTS,'sources':sources,
       'inputs':{str(p):digest(p.read_bytes()) for p in inputs},'instruments':{p.name:digest(p.read_bytes()) for p in tools.glob('*.py')},
       'cases':[dict(c,seed=731000+i) for i,c in enumerate(old['cases'])],'win_thresholds':{'v2':2,'default':2,'cadence':0,'lich_nearest':-2,'budget_control':0},'survival_control':'cadence',
       'reuse':'No outcomes reused:360freshlocalgames,40perarm, new seeds731000..731039.',
       'diagnosis':{'artifact':str(RUN/'r3/macro-survey/result.json'),'sha256':digest((RUN/'r3/macro-survey/result.json').read_bytes())},
       'rule':'Complete all360newlocalgames (4variants and5controls). Directional selection only, at most2macro variants by wins/deathrate/XP. >=v2+2/default+2/cadence/budgetcontrol, within2wins of Lichparent; death<=110%cadence, XP>=80%cadence, gear everygame and allVM/replaychecks. New hosted named-rival probes and mixed-roster confirmation required before promotion. No interim tuning/stopping.'})
    return d
if __name__=='__main__':run(prepare(),6,'release')
