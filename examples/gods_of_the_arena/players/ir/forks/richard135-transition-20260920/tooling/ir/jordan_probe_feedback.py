"""Preserve the completed Jordan probe and its evidence-only IR revision."""
from copy import deepcopy
from datetime import datetime, timezone
import markdown

from policy_ir import HERE, bundle, compile_policy, digest, extract, read, refresh_grounding, write
from release_workspace import ROOT, RUN


def main():
    root = RUN / 'jordan-v148-probe'
    result = read(root / 'result.json')['rivals']['jordan']
    diversity = read(root / 'command-diversity.json')['arms']['jordan']
    if result['games'] != 80 or not result['all_full_audits_passed']:
        raise ValueError('Incomplete probe')
    cases = {color: read(root / 'review' / (color + '-view.json')) for color in ['red', 'blue']}
    summaries = {color: read(root / 'review' / (color + '-summary.json')) for color in cases}
    own_metrics = {}
    for color in cases:
        rows = [r for r in result['rows'] if r['color'] == color]
        own_metrics[color] = {
            'games': len(rows), 'wins': sum(r['win'] for r in rows),
            'durations_ticks': sorted({r['ticks'] for r in rows}),
            'team_deaths_per_game': sorted({r['deaths'] for r in rows}),
            'rival_team_deaths_per_game': sorted({r['rival_deaths'] for r in rows}),
            'all_five_heroes_bought_gear': sum(r['gear_heroes'] == 5 for r in rows),
            'replay': 'https://softmax.com/observatory/v2?tab=episode-requests&detail=episode-request:' + cases[color]['row']['episode']}
    findings = {
        'result_sha256': digest((root / 'result.json').read_bytes()),
        'command_diversity_sha256': digest((root / 'command-diversity.json').read_bytes()),
        'metrics': own_metrics, 'distinct_full_command_tapes': diversity['distinct_full_command_tapes'],
        'observations': [
            'Our current bounded policy loses all 80 games, 40 per color; all replay, VM, roster, source, score and XP checks pass. All five heroes buy equipment in every game.',
            'All 40 red games end at tick2517 (104.875s): seven own team deaths versus one Jordan death. Crossbowman dies three times and Berserker four times in the reviewed red replay.',
            'All 40 blue games end at tick2684 (111.833s): two own team deaths versus one Jordan death.',
            'Both reviewed lineups issue zero enemy-fort attack commands and leave the enemy fort at400HP. Jordan issues425 fort attack commands as blue and710 as red; these are requests, not damage counts.',
            'With us red, both sides clear a complete lane. Jordan destroys our gate by95s and our fort at104.875s; our push destroys their gate by100s, then targets exposed barracks.',
            'With us blue, we destroy outer and inner towers in two lanes but no gate before losing. Jordan clears its chosen lane and attacks our fort.',
            'Exact command comparison finds one full command tape per color. Repeated seeds are not evidence of80 different tactical situations.'
        ],
        'mechanic': {'claim': 'A fort becomes vulnerable when any lane has no standing towers; barracks destruction is not required.',
                     'source': str(ROOT / 'examples/gods_of_the_arena/sim.nim'), 'line': 686,
                     'source_sha256': digest((ROOT / 'examples/gods_of_the_arena/sim.nim').read_bytes())},
        'hypotheses': [
            'After confirming a cleared lane, transition to the exposed fort instead of nearby barracks; measure travel cost and immediate threat before committing.',
            'Maintain a shared lane objective until its gate is down; compare against current opportunistic nearest-target switching.',
            'Test regrouping or retreat for isolated Crossbowman/Berserker against the opposing push; survival alone cannot compensate for losing the fort race.'
        ],
        'limitations': 'Direct five-copy teams on the published competition map; not mixed-team ladder contribution. Replay positions are ground truth sampled every5s. Policy logs contain only start/completion, so perceived state and internal reasoning cannot be reconstructed. Suggested fixes are unimplemented and untested.'}
    write(root / 'findings.json', findings)
    parent = read(HERE / 'win_bounded_0916.evaluated.ir.json')
    basic = (HERE / 'win_bounded_0916.evaluated.bas').read_text()
    if compile_policy(parent) != basic:
        raise ValueError('Parent parity failed')
    refs = [{'artifact': str(root / name), 'sha256': digest((root / name).read_bytes())}
            for name in ['result.json', 'command-diversity.json', 'findings.json']]
    policy = deepcopy(parent)
    policy['belief']['claims']['B_jordan_v148'] = {
        'claim': 'Published2026.9.16.3 direct five-copy team probe: current bounded policy lost0-80 to exact Jordan v148,40losses/color. All80 full audits and equipment checks passed. Two distinct command tapes, one/color; this supports a fixed-lineup weakness, not an80-independent-strategy estimate or a mixed-league win-rate claim.',
        'status': 'supported', 'evidence': refs}
    policy['belief']['claims']['B_jordan_finish_hypotheses'] = {
        'claim': 'Untested: prioritize the exposed fort after clearing a lane, maintain lane commitment through the gate, and prevent isolated Crossbowman/Berserker feeding. These changes may address the observed objective-race and survival gaps but are not implemented in this executable and require fresh local and hosted comparisons.',
        'status': 'untested', 'evidence': refs}
    policy['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                        'change': 'Jordan v148 counterexample added; exact deployed symbolic policy preserved.',
                        'needs_review': list(dict.fromkeys(parent['update']['needs_review'] + ['belief/B_jordan_finish_hypotheses'])),
                        'evidence': parent['update']['evidence'] + refs}
    refresh_grounding(policy)
    if compile_policy(policy) != basic or extract(basic, policy) != policy:
        raise ValueError('Probe feedback broke IR/symbolic parity')
    dest = root / 'feedback'
    if dest.exists():
        if read(dest / 'policy.ir.json') != policy:
            raise ValueError('Frozen feedback differs')
    else:
        bundle(policy, dest)
    write(root / 'feedback-parity.json', {'basic_sha256': digest(basic.encode()), 'parent_ir_sha256': digest(parent),
        'feedback_ir_sha256': digest(policy), 'compile_unchanged': True, 'reverse_extract_equal': True,
        'deployed_policy_changed': False})
    red_link, blue_link = (own_metrics[c]['replay'] for c in ['red', 'blue'])
    report = f'''# Jordan v148 probe — current policy loses 0–80

Tested `aaron-gota-ir-win-bounded-0916:v1` against exact
`Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v148` on published2026.9.16.3.
Aaron's two deployed policies have identical BASIC, so this measures their shared behavior.

| Our side | Wins | Losses | Draws | Duration | Our/Jordan hero deaths |
|---|---:|---:|---:|---:|---:|
| Red | 0 | 40 | 0 | 104.875 seconds | 7 / 1 per game |
| Blue | 0 | 40 | 0 | 111.833 seconds | 2 / 1 per game |

Two serial40-episode experience requests; all80 games fully audited. All heroes bought items.
No VM failures, dropped games, replay divergence, policy tuning or deployment changes.
One distinct full command sequence per color: these are two repeated fixed tactical lineups,
not80 distinct strategic tests. This does not estimate mixed-team ladder win rate.

## What the replays show

Jordan wins the fort race on both sides. Our red push clears the gate, then targets
barracks while Jordan finishes our fort. Our blue team clears outer/inner towers in
two lanes without finishing either gate. Neither reviewed lineup attacks Jordan's fort;
it retains400HP. Our red Crossbowman dies3times and Berserker4times.

The engine makes a fort vulnerable after one lane's towers are destroyed; barracks
are optional. Next hypotheses: direct fort finishing, lane commitment through the
gate, and safer grouping for exposed heroes. These remain untested.

[Watch our red loss]({red_link}) — gate-to-fort conversion and repeated hero deaths.
[Watch our blue loss]({blue_link}) — split objectives leave both gates standing.

![Recorded replay positions](review/sides-review.png)

Views above show verified sampled positions, not native3D playback. Policy logs only
contain start/completion, so this is ground-truth behavior analysis, not a reconstruction
of the policy's private reasoning.

## IR feedback

`feedback/policy.ir.json` records this counterexample and the untested hypotheses.
Compilation is byte-identical to the deployed BASIC; reverse extraction exactly
recovers the new IR. The frozen deployed IR and league selections are unchanged.

Evidence: `result.json`, `command-diversity.json`, `findings.json`, `feedback-parity.json`.
XP red: `xreq_31bf0249-e03a-468d-9132-5c7f229d96fd`.
XP blue: `xreq_d5e08e30-1c1b-40e7-a0ff-39121c2fdc5c`.
'''
    (root / 'REPORT.md').write_text(report)
    body = '<!doctype html><meta charset="utf-8"><title>Jordan v148 probe</title><style>body{max-width:1050px;margin:40px auto;font:17px/1.55 system-ui;padding:0 20px}pre{white-space:pre-wrap}img{width:100%}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:8px 14px}code{overflow-wrap:anywhere}</style>'
    body += markdown.markdown(report, extensions=['tables'])
    (root / 'REPORT.html').write_text(body)
    state = read(RUN / 'active-state.json')
    state.update(stage='jordan_v148_probe_complete', updated_at=datetime.now(timezone.utc).isoformat(),
                 all_eval_jobs_complete=True, active_controller_session=None, new_hosted_campaign=4700)
    state['latest_probe'].update(result='0wins,80losses,0draws', distinct_full_command_tapes=2,
        report=str(root / 'REPORT.html'), feedback_ir_sha256=digest(policy), all_audits_passed=True)
    state['remaining_research'] = 'Jordan v148 beats bounded on both fixed team lineups. Test fort finishing, lane commitment, and isolated hero survival. See latest probe feedback; fixes unimplemented.'
    write(RUN / 'active-state.json', state)
    context = HERE / 'WORKING_CONTEXT.md'
    old = context.read_text()
    marker = '# Latest requested test — Jordan v148 completed'
    note = f'''{marker}

Current bounded policy lost0/80:40losses/red and40losses/blue, no draws.
All80 full replay/VM/source/roster/score/XP audits passed; all5heroes bought items.
Exact command diversity2(one/color): fixed-lineup counterexample, not80different tactics.
Durations2517ticks/red and2684ticks/blue. Own team deaths7/red and2/blue vsJordan1each.
Jordan version93bd214c-9b77-4e88-b174-b3cdcf3f8da8. Study {root}.
Report REPORT.md/REPORT.html there; findings.json and review/sides-review.png.
Feedback IR there adds scoped counterexample and untested fort-finish/lane/survival hypotheses;
compile/reverse parity passes with unchanged deployed BASIC. Canonical deployedIR remainsbelow.
No league selections changed. No XP jobs running. New dashboard http://localhost:8800.
Campaign total880local+4700hosted. Do not rerun these completed80games.
Original completed deployment context follows (its4620hosted count predates this probe).

'''
    if not old.startswith(marker):
        context.write_text(note + old)
    print({'games': 80, 'wins': result['wins'], 'losses': result['losses'], 'feedback_ir_sha256': digest(policy), 'report': str(root / 'REPORT.md')})


if __name__ == '__main__':
    main()
