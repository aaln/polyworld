"""Close the frozen warning study without changing evaluated executable bytes."""
from copy import deepcopy
from pathlib import Path

from jordan254_followup import STUDY
from jordan254_research import STUDY as BASE
from policy_ir import bundle, compile_policy, digest, extract, read, write

NOTE = (
    'Validated targeted Jordan254 improvement on published 2026.9.16.5: warning100 '
    'RED40/40 BLUE40/40 versus deployed RED0/40 BLUE40/40. Native median red replay '
    'reconstructs every owned command and state hash; all five heroes first recall '
    'at894 versus1480, 24.42 seconds earlier. Fresh60 local cases58/60 match deployed58/60, '
    'all30 blue full-game action/hash parities pass. Preservation40/color: g002v1 '
    'RED22 BLUE40 versus deployed21/40; black-kitev16 RED0 BLUE40 versus0/40; '
    'macromackie4 RED40 BLUE40 versus40/40; relh154 RED40 BLUE0 versus40/0. '
    'All400 selected-candidate hosted games passed complete runtime/replay/roster/version/equipment '
    'audits. Rival controls reused from the exact prior executable, different generated seeds; '
    'correlated fixed-lineup trajectories, no independent-trial significance or ten-player '
    'qualification. Initial absolute default gate FAILED and remains failed; this is the '
    'separate prospectively declared followup. Reach14 rejected at28/40 red below32 floor. '
    'Known weaknesses persist: black-kite red, relh blue, and stale red defensive rally '
    'orders after anchor destruction (user episode77d700dd). Warning100 changes early '
    'red threat coverage only and is not a fix for that separate stale-order bug.'
)


def finalize():
    local = read(STUDY/'local/qualification.json')
    hosted = read(STUDY/'hosted-result.json')
    guards = read(STUDY/'guards/result.json')
    relh = read(STUDY/'relh-preservation/result.json')
    assert 'warning100' in local['qualified']
    assert hosted['outcome_qualified'] == ['warning100'] and guards['passed'] and relh['passed']
    arms = {**hosted['arms'], **guards['arms'], **relh['arms']}
    assert all(r['games'] == 40 and r['all_full_audits_passed'] for r in arms.values())
    reviewed = read(STUDY/'hosted/warning100/review/decisions.json')['cases']
    baseline = read(BASE/'baseline-review/decisions.json')['cases']
    new_red = next(c for c in reviewed if c['color'] == 'red')
    old_red = next(c for c in baseline if c['name'] == 'red loss')
    assert all(c['proof']['all_state_hashes_equal'] and c['proof']['all_actions_consumed'] for c in reviewed)
    new_ticks = {s:r['tick'] for s,r in new_red['first_recalls'].items()}
    old_ticks = {s:r['tick'] for s,r in old_red['first_recalls'].items()}
    assert len(new_ticks) == len(old_ticks) == 5
    assert set(new_ticks.values()) == {894} and set(old_ticks.values()) == {1480}
    evidence_paths = ['prospective.json','local/qualification.json','hosted-result.json',
                      'hosted/warning100/review/decisions.json','guards/result.json',
                      'relh-preservation/result.json']
    evidence = [{'artifact':str(STUDY/p),'sha256':digest((STUDY/p).read_bytes())} for p in evidence_paths]
    result = {'confirmed':'warning100','rejected':'reach14','scope':NOTE,
              'earlier_recall_ticks':1480-894,'candidate_first_recalls':new_ticks,
              'baseline_first_recalls':old_ticks,'evidence':evidence,
              'candidate_source_sha256':'6b14024bd2614b5dcbfa33e94b0b11360956b81a3d44419aaf4b44cf29d5d51a',
              'prior_screen_still_failed':True,'stale_anchor_bug_fixed':False}
    write(STUDY/'final-result.json',result)
    parent = read(STUDY/'guards/feedback/policy.ir.json')
    source = (STUDY/'guards/feedback/policy.bas').read_text()
    assert digest(source.encode()) == result['candidate_source_sha256']
    policy = deepcopy(parent)
    policy['belief']['claims']['B_candidate'] = {'status':'supported','claim':NOTE,'evidence':evidence}
    policy['belief']['claims']['B_outer_warning'] = {'status':'supported',
        'claim':'Observed outer-lane pressure now triggers red recall 586ticks earlier in the reconstructed representative Jordan254 win; 40red/40blue wins in the fixed-lineup study. Scope and limitations in B_candidate.',
        'evidence':evidence}
    policy['belief']['claims']['B_stale_rally'] = {'status':'supported',
        'claim':'In user episode77d700dd red DK/Lich/Warlock continue walking to73,11 after protected tower11 is destroyed. Their defUntil17672 outlasts the13872tick loss. This candidate does not repair stale rally expiry.',
        'evidence':[{'artifact':str(BASE/'user-stall-77d700dd/owned-proof.json'),
                     'sha256':digest((BASE/'user-stall-77d700dd/owned-proof.json').read_bytes())}]}
    policy['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
        change='Validated warning100 feedback, requested preservation checks, and explicit unresolved stale-rally limitation.',
        needs_review=[x for x in parent['update']['needs_review'] if x != 'belief/B_candidate'],
        evidence=parent['update']['evidence']+evidence)
    assert compile_policy(policy) == source and extract(source,policy) == policy
    out = STUDY/'final-feedback'
    if out.exists(): assert read(out/'policy.ir.json') == policy
    else: bundle(policy,out)
    report = '# Jordan254 warning100 — completed evaluation\n\n'+NOTE+'\n\n'
    report += '| Opponent | Prior red | New red | Prior blue | New blue |\n|---|---:|---:|---:|---:|\n'
    for label,pr,nr,pb,nb in [('Jordan254',0,40,40,40),('g002v1',21,22,40,40),('black-kitev16',0,0,40,40),('macromackie4',40,40,40,40),('relh154',40,40,0,0)]:
        report += f'| {label} | {pr}/40 | {nr}/40 | {pb}/40 | {nb}/40 |\n'
    report += '\nThe one additional g002 win is not evidence of a meaningful improvement. All checks use five heroes controlled by each of two policies.\n'
    report += '\nCandidate IR/BASIC: `final-feedback/`. Source SHA: `'+result['candidate_source_sha256']+'`. Evidence: `final-result.json`.\n'
    (STUDY/'REPORT.md').write_text(report)
    exp = Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-18-jordan254-warning-followup.md')
    text = exp.read_text().replace('status: running','status: confirmed')
    text = text.split('## Result\n',1)[0]+'## Result\n\n'+NOTE+'\n\n## Verdict\n\nConfirmed for warning100 against the specified target and preservation rule. Reach14 fails its hosted red floor. Original failed screen remains failed.\n\nEvidence: '+str(STUDY/'final-result.json')+'\n'
    exp.write_text(text)
    print('Confirmed warning100; all requested preservation checks passed; exact IR/BASIC parity retained.')


if __name__ == '__main__': finalize()
