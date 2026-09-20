"""Version-pinned Jordan254 baseline and frozen candidate comparisons."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import middle_rush_parallel_checks as hosted
from economy_feedback import record
from policy_ir import HERE, read, write, digest, compile_policy, extract
from ranger_guard_hosted import freeze
from release_workspace import RUN
from win_hosted import live

STUDY = RUN/'coached-lanes/r5-jordan254'
LABEL = 'Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v254'
PARENT = RUN/'coached-lanes/r5-macromackie-middle-rush/deployment-pair/policy'


def baseline():
    live(); STUDY.mkdir(exist_ok=True)
    source=(PARENT/'policy.bas').read_bytes();policy=read(PARENT/'policy.ir.json')
    assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
    active=read(HERE/'active_policy.json')
    assert {r['version'] for r in active['players']}=={
        'd94c63e8-4aa5-4a71-8ec5-78549f3958c6','95e39723-64cc-45b5-b66a-4440e12fb4b3'}
    freeze(STUDY/'baseline-prospective.json',{'question':'How does the exact deployed policy fare against exact Jordan254 by color?',
        'episodes_per_color':40,'source_sha256':digest(source),'parent_ir':str(PARENT/'policy.ir.json'),
        'selection':'Median duration win and loss per color when present, before reconstruction.',
        'scope':'Directional fixed-lineup 5v5 two-player baseline; no statistical independence claim. User permits parallel batch requests.'})
    hosted.ROOT=STUDY/'baseline'
    hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Jordan254 baseline: deployed exact middle-rush;40episodes percolor; all runtime/roster/release/replay/equipment checks; no source changes.'
    red,rid=hosted.prepare('jordan254',LABEL,'candidate','red')
    target=read(hosted.ROOT/'jordan254/resolved-target.json')
    assert target['player_id']=='ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb'
    blue,_=hosted.prepare('jordan254',LABEL,'candidate','blue',rid)
    with ThreadPoolExecutor(2) as pool:
        rows=dict(pool.map(hosted.run_arm,[red,blue]))
    output={'label':LABEL,'rival':rid,'source_sha256':digest(source),'arms':rows,'promotion_performed':False}
    write(STUDY/'baseline-result.json',output)
    if not (STUDY/'baseline-feedback').exists():
        record(PARENT/'policy.ir.json',PARENT/'policy.bas',
               'Jordan254 deployed baseline,40percolor: '+str({k:v['wins'] for k,v in rows.items()})+
               '. Complete audits; directional fixed-lineup evidence. No gameplay change.',
               STUDY/'baseline-result.json',STUDY/'baseline-feedback')
    print('BASELINE',{k:v['wins'] for k,v in rows.items()},flush=True)


if __name__=='__main__':
    baseline()
