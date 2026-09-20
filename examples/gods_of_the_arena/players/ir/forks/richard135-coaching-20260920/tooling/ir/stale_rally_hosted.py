"""Early rival preservation gate for the frozen combined replay repair."""
from concurrent.futures import ThreadPoolExecutor

from economy_feedback import record
from jordan254_followup import STUDY as CONTROL
from policy_ir import digest,read,write
from ranger_guard_hosted import freeze
from rush_hosted import upload
from stale_rally_repair import STUDY,prepare
import middle_rush_parallel_checks as hosted


def main():
    prepare()
    result=read(STUDY/'replay-seed/result.json')
    assert result['original_loss_reproduced'] and result['arms']['retire_core']['red_win']==1
    assert result['arms']['warning100']['red_win']==0
    root=STUDY/'hosted-preservation';root.mkdir(exist_ok=True)
    targets={'jordan254':{'label':'Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v254',
                         'id':'92958fa7-74b2-4a3e-b0d7-e885e68e32d3'},
             'macro4':{'label':'macromackie-gota:v4','id':'1a78a3f9-8112-4c2c-831a-f0ffee8dbacc'}}
    freeze(root/'prospective.json',{'candidate':'retire_core','first_stage_targets':targets,
        'episodes':40,'color':'red','current_baseline_wins':{'jordan254':40,'macro4':40},
        'rule':'Each must retain40/40 current-warning100 red wins with all full audits. If either fails, stop further promotion qualification and retain the already promoted warning100. No interim source changes.',
        'if_pass':'Complete remaining8 color/rival arms from all5rivals before considering promotion, as in the original repair prospective record.',
        'evidence':str(STUDY/'replay-seed/result.json'),'control':str(CONTROL/'final-result.json'),
        'scope':'Directional fixed-lineup evidence with reused exact current-source controls; no independent-trial significance or mixed-team claim.'})
    src=STUDY/'candidates/retire_core';feedback=STUDY/'local-feedback'
    if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas',
        'Actual reported loss fully reproduced with action/hash/setup/seed equality. Combined retirement+core alarm wins this single localcounterfactual, warning100loses. Retirement alone stillloses. Five native transition/bluebranch/denseVM tests pass. Competitive effect untested.',
        STUDY/'replay-seed/result.json',feedback)
    _,version=upload('retire_core',STUDY,'aaron-gota-ir-liveanchor','Retire destroyed own anchors and detect visible core creeps.',
        feedback_override=feedback,candidate_override=src,
        validation_note='Exact reported local loss reproduced; combinedrepair wins one counterfactual. VM/IR tests pass. Rival preservation untested; inert upload, no league selection.')
    hosted.ROOT=root/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Frozen stale-anchor+creep repair:40red per exactJordan254/macromackie4. Must retain current40/40 each. Complete full replay/runtime/equipment/roster/release audits. No source tuning or automatic league change.'
    hosted.VERSIONS['candidate']={'id':version['id'],'name':version['name']+':v'+str(version['version'])}
    plans=[]
    for key,target in targets.items():
        p,_=hosted.prepare(key,target['label'],'candidate','red',target['id']);plans.append(p)
    with ThreadPoolExecutor(2) as pool:arms=dict(pool.map(hosted.run_arm,plans))
    passed=all(a['games']==40 and a['wins']==40 and a['all_full_audits_passed'] for a in arms.values())
    write(root/'result.json',{'passed':passed,'arms':arms,'promoted':False,
                            'source_sha256':digest((src/'policy.bas').read_bytes()),
                            'decision':'Continue remaining guard arms' if passed else 'Reject promotion; preserve warning100 champions'})
    print('REPAIR FIRST GUARDS',passed,{k:v['wins'] for k,v in arms.items()},flush=True)


if __name__=='__main__':main()
