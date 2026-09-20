"""Class repair local checks; explicitly reuse completed paired control tapes."""
from datetime import datetime,timezone
import shutil

from class_release_candidates import make,VARIANTS
from economy_screen import run
from policy_ir import HERE,bundle,read,write,digest
from release_workspace import RUN,VERSION,SOURCE,verify

STUDY=RUN/'class-followup'

def prepare():
    verify()
    d=STUDY/'local';d.mkdir(parents=True,exist_ok=True)
    if (d/'plan.json').exists(): return d
    prior=RUN/'local';old=read(prior/'plan.json')
    for n in ['episode','audit','config.json','default.bas']: shutil.copy2(prior/n,d/n)
    sources={n:old['sources'][n] for n in ['v2','cadence','default','footprint']}
    (d/'screen').mkdir()
    for name in sources:
        (d/'screen'/name).symlink_to(prior/'screen'/name,target_is_directory=True)
    for name in VARIANTS:
        bundle(make(name),d/'candidates'/name)
        sources[name]=str(d/'candidates'/name/'policy.bas')
    frozen=d/'frozen-instruments';frozen.mkdir()
    for p in HERE.glob('*.py'):
        if not p.name.startswith('test_'): shutil.copy2(p,frozen/p.name)
    inputs=[d/n for n in ['episode','audit','config.json']]+[__import__('pathlib').Path(p) for p in sources.values()]
    write(d/'plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),'family':'release',
        'game_version':VERSION,'game_source':SOURCE,'variants':VARIANTS,'sources':sources,
        'inputs':{str(p):digest(p.read_bytes()) for p in inputs},
        'instruments':{p.name:digest(p.read_bytes()) for p in frozen.glob('*.py')},'cases':old['cases'],
        'win_thresholds':{'v2':2,'default':2,'cadence':0,'footprint':-2},'survival_control':'cadence',
        'reuse':'160completed control games reused by symlink, unchanged seeds/config/source/binaries;80newgames. Local debugging only, not independent strength evidence.',
        'rule':'Class-specific repair: other nine classes must preserve parent action traces; Berserker base variant must reproduce waveguard actions in real-VM fixtures. Complete40matched local games per new variant, compare frozen original controls. Need>=v2+2/default+2/cadence, within2wins of footprint; death<=110%cadence, XP>=80%cadence, all gear/VM/replay guards. At most two advance. Then100hosted games per qualifier versus the SAME frozen nine opponents. Reuse completed discovery controls for selection only; no new significance claim. Select>=5pp over both deployed controls, no adverse-class flag p<.005, survival/XP/gear guards. Best wins/survival/XP/name advances to fresh400games/arm, excluding ALL earlier seeds and outcomes. Confirmation>=5pp,p<.025 each, no class flag, same guards;100sampled field before promotion. No tuning/stopping mid-stage.',
        'stop_rule':'Original footprint qualified initial selection but400confirmation not launched. Defer it to investigate observed Berserker regression; do not relabel its discovery as a confirmation or pool adaptive data into final tests.'})
    return d

if __name__=='__main__': run(prepare(),8,'release')
