"""Adaptive class discovery reuses old controls only for selection, never verdict."""
from datetime import datetime,timezone
import shutil

from economy_feedback import record
from hosted_queue import run
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest
from release_hosted import upload,compare
from release_workspace import RUN,VERSION,SOURCE,verify
from class_release_screen import STUDY


def prepare():
    verify()
    from class_release_parity import check
    check()
    local=STUDY/'local';screen=read(local/'screen-result.json');frozen=read(local/'plan.json')
    if screen['verified_games'] != 240: raise ValueError('80new+160reused local checks must complete')
    root=STUDY/'hosted-discovery';root.mkdir(exist_ok=True)
    for name in frozen['variants']:
        out=local/'screen-feedback'/name
        if not out.exists():
            record(local/'candidates'/name/'policy.ir.json',local/'candidates'/name/'policy.bas',
                   f'Class follow-up on{VERSION}: completed40local games; metrics {screen["metrics"][name]}. '
                   'Controls explicitly reused; no independent competitive claim. '
                   +('Selected for100game hosted discovery.' if name in screen['selected'] else 'Local gates failed.'),
                   local/'screen-result.json',out)
    if not (root/'plan.json').exists():
        plan=read(RUN/'hosted-discovery/plan.json')
        plan.update(created_at=datetime.now(timezone.utc).isoformat(),
            local_plan_sha256=digest((local/'plan.json').read_bytes()),
            confirmation_rule=frozen['rule'], discovery_reject_adverse_classes=True,
            excluded_discovery_results=[str(RUN/'hosted-discovery/result.json')],
            reused_controls='Completed v2/cadence100each from original release discovery; adaptive selection only, no new games or confirmation evidence.')
        write(root/'plan.json',plan)
        for name in ['v2','cadence']:
            (root/name).symlink_to(RUN/'hosted-discovery'/name,target_is_directory=True)
        tools=STUDY/'frozen-hosted-tools';tools.mkdir()
        for p in HERE.glob('*.py'):
            if not p.name.startswith('test_'): shutil.copy2(p,tools/p.name)
        write(tools/'manifest.json',{p.name:digest(p.read_bytes()) for p in tools.glob('*.py')})
    return screen['selected']


if __name__=='__main__':
    selected=prepare()
    with client() as c:
        league=get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        game=get(c,'/v2/coworlds/'+league['game']['coworld_id'])
        if game['version']!=VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:
            raise ValueError('Live release changed')
    upload(STUDY)
    run([STUDY/'hosted-discovery'/name for name in selected])
    compare(STUDY)
