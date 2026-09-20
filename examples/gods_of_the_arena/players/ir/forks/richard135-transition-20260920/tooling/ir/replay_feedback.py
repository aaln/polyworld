"""Attach replay findings to the retained v2 IR without inventing policy behavior."""
from copy import deepcopy
from pathlib import Path
import sys
from policy_ir import HERE, ROOT, bundle, compile_policy, digest, read, refresh_grounding, write


def main():
    output = Path(sys.argv[1])
    path = HERE / 'waveguard_xp.evaluated.ir.json'
    parent = read(path)
    policy = deepcopy(parent)
    original = (HERE / 'waveguard_xp.evaluated.bas').read_text()
    findings_path = HERE / 'replay-findings-20260915.json'
    evidence = {'artifact':str(findings_path.relative_to(ROOT)), 'sha256':digest(findings_path.read_bytes())}
    findings = read(findings_path)
    short = findings['arms']['spell_short']['retreat_segments']
    policy['belief']['claims']['B_replay_turn_cost'] = {
        'claim':f"Published .3 replay diagnosis: among {short['segments']} complete ten-tick hit-adjacent walk segments, median turning-only ticks={short['median_turn_only_ticks']}, median moving ticks={short['median_moved_ticks']}. Only {short['separation_gain_gt_quarter_tile']}/{short['living_tracked_enemy_at_end']} segments gained >0.25 tiles against the same initially nearest visible enemy still alive at the end. These correlated command-derived observations show a motion failure, not competitive superiority of a replacement.",
        'status':'supported', 'evidence':[evidence]}
    policy['belief']['claims']['B_replay_tower_trap'] = {
        'claim':'Two of forty v2 cases have >30-second no-movement/no-hit/no-active-offense stalls, with the first path waypoint inside friendly-tower collision clearance. The Arcanist stalls 344.7 seconds. At its verified tick1200 checkpoint, 24 nearby walk destinations fail; a diagnostic-only engine waypoint change produces4.60 tiles displacement. Accepted movement and terrainWalkable do not prove successful navigation. Target switches are not evidence of progress.',
        'status':'supported', 'evidence':[evidence]}
    policy['belief']['claims']['B_replay_late_escape'] = {
        'claim':'Across134 v2 deaths, the median final-six-second window contains one second of half-second samples below35%HP;18 deaths have no such sample. This supports investigating earlier escape decisions. It is a sampled opportunity measure, not proof of avoidable deaths or a validated threshold.',
        'status':'supported', 'evidence':[evidence]}
    policy['belief']['claims']['B_motion_feedback_hypothesis'] = {
        'claim':'Persistent retreat destinations and measured separation, with turn cost, enemy closing speed, safe re-engagement and earlier multi-attacker risk checks, may improve survival without losing fort wins. Preventive tower-clearance routing may avoid collision traps. These proposed behaviors are NOT implemented in the retained v2 executable and require fresh local and hosted validation.',
        'status':'untested', 'evidence':[evidence]}
    policy['update'] = {
        'revision':parent['update']['revision']+1, 'parent':digest(parent),
        'change':'Replay-grounded beliefs and next hypotheses from160 complete tapes on40 reused cases. Retain byte-identical league v2; no candidate or league promotion.',
        'needs_review':sorted(set(parent['update']['needs_review'] + ['belief/B_motion_feedback_hypothesis', 'goal/G_survival'])),
        'evidence':parent['update']['evidence']+[evidence],
    }
    refresh_grounding(policy)
    if compile_policy(policy) != original:
        raise ValueError('Diagnostic feedback must preserve the selected executable exactly')
    bundle(policy, output)
    write(output/'parent.ir.json', parent)
    write(output/'runtime-provenance.json', {
        'version':findings['game_version'], 'source':findings['published_source'],
        'replay_evidence':evidence,
        'note':'Replay decoding used the isolated published checkout and binaries hashed in the evidence. Root working-tree game changes were not used as evaluation mechanics.'})
    write(path, policy)
    print(f"IR revision {policy['update']['revision']}; retained BASIC {digest(original.encode())}")


if __name__ == '__main__':
    main()
