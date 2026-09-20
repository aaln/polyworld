"""Advance completed local macro qualifiers to new100-game mixed-roster discovery."""
from datetime import datetime,timezone
from pathlib import Path
import shutil
import subprocess
from economy_feedback import record
from hosted_queue import run
from hosted_wave import client,get
from macro_screen import STUDY
from policy_ir import HERE,read,write,digest
from release_hosted import upload,compare
from release_workspace import RUN,SOURCE,VERSION,verify

def main():
    verify();local=STUDY/'local';screen=read(local/'screen-result.json')
    if screen['verified_games']!=360:raise ValueError('Complete all local arms first')
    logs=list((local/'screen').glob('*/*/stdout.log'))
    if len(logs)!=360 or any('BASIC error:' in p.read_text() for p in logs):raise ValueError('Local VM failure or missing log')
    if not screen['selected']:
        print('No macro candidate qualified; no upload or XP launched.');return
    prior=RUN/'r3-study/hosted-confirmation'
    if not (prior/'result.json').exists():raise ValueError('Complete the earlier frozen confirmation before any adaptive hosted study')
    previous=read(prior/'plan.json')
    for n in screen['selected']:
        out=local/'screen-feedback'/n
        if not out.exists():record(local/'candidates'/n/'policy.ir.json',local/'candidates'/n/'policy.bas',
            f'Fresh40-game local screen among4macro hypotheses; {screen["metrics"][n]}. All360games, localVMlogs and fullreplay audits verified. Adaptive selection only; no hosted competitive claim.',local/'screen-result.json',out)
    hosted=STUDY/'hosted-discovery';hosted.mkdir(exist_ok=True)
    if not (hosted/'plan.json').exists():
        plan={k:previous[k] for k in ['target','game_version','game_source','config','opponents']}
        plan['controls']=read(RUN/'r3-study/hosted-discovery/plan.json')['controls']
        plan.update(created_at=datetime.now(timezone.utc).isoformat(),episodes_per_arm=100,
          local_plan_sha256=digest((local/'plan.json').read_bytes()),discovery_reject_adverse_classes=True,
          confirmation_rule='Selection requires>=5pp over both deployedcontrols, no adverse class p<.005, survival<=110%cadence, XP>=80%cadence, allgear/VM/fullreplayvalidity. Complete both selected100episodearms before interpretation. Reused current3controls only for adaptive selection. Independent held-out400/arm confirmation and100sampledfieldgames required before promotion. Named-rival probes assess bothcolors separately; fixed-roster repeats are not distincttacticalscenarios.',
          excluded_discovery_results=[str(RUN/'hosted-discovery/result.json'),str(RUN/'class-followup/hosted-discovery/result.json'),str(RUN/'class-followup/hosted-confirmation/result.json'),str(RUN/'lich-followup/hosted-discovery/result.json'),str(prior/'result.json')],
          excluded_rival_results=[str(RUN/'lich-followup/rival-matchups/result.json')],
          reused_controls='Reuse exactly completed part0ofeachdeployedcontrol from current3confirmation:100/arm. These200outcomes and allprioroutcomes excluded from new confirmation. No reusedoutcome counts as newgame.')
        write(hosted/'plan.json',plan)
        for n in ['v2','cadence']:(hosted/n).symlink_to(prior/n/'part-0',target_is_directory=True)
    with client() as c:
        league=get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28');game=get(c,'/v2/coworlds/'+league['game']['coworld_id'])
        if game['version']!=VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:raise ValueError('Live release changed')
    upload(STUDY)
    run([hosted/n for n in screen['selected']])
    compare(STUDY)
if __name__=='__main__':main()
