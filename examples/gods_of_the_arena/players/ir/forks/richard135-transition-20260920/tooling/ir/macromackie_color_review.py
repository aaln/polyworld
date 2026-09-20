"""Summarize frozen color cohorts and source-verified recall/visibility traces.

Run after the retained color selection's native replays have been reconstructed.
Uses recorded observations only; does not give the policy access to hidden heroes.
"""
from collections import Counter
from pathlib import Path
import json

from binding import CONTRACTS
from economy_feedback import record
from policy_ir import digest, read, write
from release_workspace import RUN

ROOT = RUN / 'coached-lanes/r5-macromackie-v4'
ANCHOR = RUN / 'coached-lanes/r5-anchored-support/hosted/anchor/tournament-portfolio/policy'
CONTROL = RUN / 'coached-lanes/r5-jordan-lineup/candidate'


def rows(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def trace(path):
    first = {}
    window = []
    summary = None
    for r in rows(path):
        if r['type'] == 'summary':
            summary = r
        elif r['type'] == 'decision':
            m = r['memory']
            if m['defActive'] and r['slot'] not in first:
                first[r['slot']] = {'tick': r['tick'], 'seconds': r['tick'] / 24,
                                    'visible_group': m['defCount'], 'anchor': m['defAnchor']}
            if r['slot'] == 5 and 1248 <= r['tick'] <= 1260:
                window.append({'tick': r['tick'], 'visible_group': m['defCount'],
                               'defense_active': m['defActive']})
    assert summary and summary['all_state_hashes_equal'] and summary['all_actions_consumed']
    return {'first_recall': first, 'brief_visibility_window': window, 'proof': summary}


def main():
    g, h = read(CONTROL / 'policy.ir.json'), read(ANCHOR / 'policy.ir.json')
    assert g['strategy'] == h['strategy'] and g['execution'] == h['execution']
    different = [k for k in g['skill'] if g['skill'][k] != h['skill'][k]]
    assert different == ['observe']
    sources = []
    for parent in (g, h):
        skill = parent['skill']['observe']
        text = CONTRACTS[skill['operator']].source(skill['parameters'])
        assert text.startswith('if selfTeam = 0 then\n')
        sources.append(text.split('\nelse\n', 1)[1])
    assert sources[0] == sources[1]
    comparison = read(ROOT / 'comparison.json')
    cohorts = {}
    for name, result in comparison['results'].items():
        cohorts[name] = {'colors': result['colors']}
        for color in ('red', 'blue'):
            subset = [r for r in result['rows'] if r['color'] == color]
            signatures = Counter((r['win'], r['ticks'], r['deaths'], r['rival_deaths']) for r in subset)
            cohorts[name][color + '_outcome_signatures'] = [
                {'win': k[0], 'ticks': k[1], 'owned_deaths': k[2],
                 'rival_deaths': k[3], 'games': count} for k, count in sorted(signatures.items())]
    cases = []
    for case in read(ROOT / 'color-dense-selection.json')['cases']:
        directory = ROOT / 'hosted/anchor/macromackie_v4/blue/artifacts' / case['episode']
        decoded = list(rows(directory / 'decoded.jsonl'))
        proof = decoded[-1]
        assert proof['type'] == 'summary' and proof['hash_mismatches'] == 0
        structures, visibility, previous = [], [], None
        for frame in (r for r in decoded if r['type'] == 'frame'):
            alive = {b['id'] for b in frame['buildings'] if b['hp'] > 0}
            if previous is not None and previous - alive:
                structures.append({'destroyed_by_sample_tick': frame['tick'], 'ids': sorted(previous - alive)})
            previous = alive
            if frame['tick'] in (960, 1200, 1440, 1560):
                h5 = next(x for x in frame['heroes'] if x['slot'] == 5)
                visibility.append({'post_tick': frame['tick'], 'enemy_hero_ids': [
                    x['id'] for x in h5['visible_post_tick'] if x['kind'] == 2 and x['team'] == 0 and x['hp'] > 0]})
        cases.append(case | trace(directory / 'decisions-blue-dense.jsonl') |
                     {'structures': structures, 'sampled_visibility': visibility})
    red = trace(ROOT / 'artifacts/ereq_fb88f791-70be-4104-8e4f-86f0650b7eeb/decisions-red-dense.jsonl')
    claim = (
        'Macromackie v4 fixed 5v5 two-player comparison: anchor red19/40 blue9/40; '
        'blue_repair red40/40 blue8/40. Both policies have exactly identical lowered blue '
        'observer source, other skills and strategy. All63blue losses end2728/2740ticks '
        'with4owned deaths and0rival deaths. Full reconstruction of selected blue losses '
        'of both durations shows all5first recall at1558(64.92s), versus1252(52.17s) '
        'in the median blue win. At1252–1255 the win sees4clustered enemies and '
        'the losses see3; the four-visible-hero threshold delays their recall. '
        'In actual Gredleaguewin the reconstructed DK recalls846(35.25s). '
        'Blue opens3/2on side lanes, leaving long return travel while middle is pushed. '
        'This supports a brittle visibility-gated rush response, not intrinsic color '
        'balance or universal causal attribution. Different seeds and few repeated '
        'trajectories; no independent-trial significance. Hypothesis for testing: '
        'accumulate recent visible lane pressure and observed structure damage, '
        'account for return travel time, and commit until arrival or threat resolution. '
        'Do not infer hidden enemies or simply make all defense permanent. No new '
        'gameplay or league selection is validated by this diagnostic feedback.')
    result = {'cohorts': cohorts, 'blue_observer_sha256': digest(sources[0]),
              'other_skills_strategy_execution_identical': True, 'blue_cases': cases,
              'red_league_comparison': red, 'claim': claim,
              'source_hashes': {'anchor': digest((ANCHOR / 'policy.bas').read_bytes()),
                                'blue_repair': digest((CONTROL / 'policy.bas').read_bytes())}}
    write(ROOT / 'color-analysis.json', result)
    report = '''# Why the red/blue gap against macromackie v4

| Our policy | Red wins | Blue wins |
|---|---:|---:|
| coordinated-support-anchor | 19/40 | 9/40 |
| perimeter-blue_repair | 40/40 | 8/40 |

The largest verified blue failure is late recognition of the opening middle rush.
Our opening splits all five heroes across the side lanes. Group recall requires
four currently visible enemy heroes clustered near a friendly structure. Actual
five-hero pressure can expose only one to three heroes through fog of war.

Two source-verified blue losses, covering both observed loss-duration classes,
first recall all five heroes at tick1558 (64.92s). A selected blue win recalls at
tick1252 (52.17s). At ticks1252–1255, that win sees four clustered enemies while
the losses see three. A brief visibility threshold crossing changes return timing.
This is a repeatable decision mechanism, not proof that changing the threshold
alone would improve every opponent matchup.

In the median blue loss, middle outer/inner/gate towers are gone by sampled ticks
1200/1560/1920 (50/65/80s). Base guards are gone by2400/2640 (100/110s), and the
god dies at2728 (113.67s). Defenders arrive piecemeal after a long return journey.
All63blue losses in the160game comparison end at2728 or2740, with four owned
hero deaths and no enemy hero deaths. These are fast base collapses rather than
the prolonged post-defense waiting seen in the original red loss.

The selected actual blue_repair red league win recalls its DeathKnight at846
(35.25s), nearly30seconds before the selected blue losses. Both colors have
different hero rosters, and our observer/navigation explicitly branch on color.
This comparison cannot separate innate hero/map balance from policy interaction.

Both policy versions share exactly identical compiled blue observer source,
other skills, strategy and execution. Their9/40versus8/40blue results therefore
do not show a blue-code improvement; their red branches are what differ.

Next hypothesis: recognize sustained observed lane pressure and structure damage
without requiring four enemies visible simultaneously; include defender travel
time and keep a return commitment until arrival or threat resolution. Validate
against multiple opponents before changing the approved diverse league pair.

Evidence: color-analysis.json, color-dense-selection.json, retained full replay
and decision traces, comparison.json. All reconstructed commands and hashes match.
Selection: median-duration anchor blue win/loss, another loss from the other
duration class, and the previously selected actual G red league win. Different
seeds; repeated trajectories; directional evidence, not independent trials.
Policy code and league selections remain unchanged.
'''
    (ROOT / 'COLOR_ANALYSIS.md').write_text(report)
    feedback = ROOT / 'color-feedback'
    if not feedback.exists():
        record(ROOT / 'diagnostic-feedback/policy.ir.json', ANCHOR / 'policy.bas',
               claim, ROOT / 'color-analysis.json', feedback)
    print(json.dumps({'blue_parity': True, 'cases': len(cases),
                      'report': str(ROOT / 'COLOR_ANALYSIS.md'), 'feedback': str(feedback)}))


if __name__ == '__main__':
    main()
