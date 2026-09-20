"""Prospective hosted gates for the locally selected item/macro combination.

The earlier lane-study gate cannot beat an 80/80 control. This separate study
requires preservation of that team matchup and improvement across three new
fixed mixed rosters. Repeated episodes are not counted as independent tactics.
"""
import argparse
from collections import Counter
from math import comb
import random
import shutil
from pathlib import Path

from campaign_hosted_compare import cohort
from coached_hosted_r5 import prepare as prepare_team
from coached_loadout import STUDY
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create
from policy_ir import read, write, digest
from release_hosted import summarize
from release_workspace import RUN
from win_hosted import live

OWNED = {'ply_594ec24d-d7f3-4370-a000-468354ec41c9',
         'ply_630a768f-d623-44b2-80fa-36968d6fa75a'}
CONTROL = '810d3860-af35-4fed-9364-a4e4bd8b0c2b'
CHANGE = 'Ordered damage equipment for sustained structure damage; exact selected macro preserved in IR'


def freeze():
    game = live()
    path = STUDY / 'hosted-plan.json'
    if path.exists():
        plan = read(path)
        if game['id'] != plan['target']['coworld_id']:
            raise ValueError('Live game changed')
        return plan
    result = read(STUDY / 'local/result.json')
    if not result['selected'] or any(m['games'] != 40 for m in result['metrics'].values()):
        raise ValueError('Complete local forty-case qualification required')
    candidate = result['selected'][0]
    champions = read(STUDY / 'champions-before-hosted.json')
    available = sorted([{'id': r['policy_version']['id'], 'label': r['policy_version']['label'],
                         'player_id': r['player']['id']} for r in champions
                        if r['player']['id'] not in OWNED and r['status'] == 'competing'
                        and r['substatus'] == 'active'], key=lambda r: r['label'])
    if len(available) < 9:
        raise ValueError('Need nine distinct current incumbents')
    rng = random.Random(7560916)
    rosters = [rng.sample(available, 9) for _ in range(3)]
    baseline = read(RUN / 'coached-lanes/r5-convoy/hosted/current/plan.json')
    plan = {k: baseline[k] for k in ['target', 'game_version', 'game_source', 'config', 'rival', 'rival_version']}
    plan.update(candidate=candidate, control_version=CONTROL, rosters=rosters,
                local_result_sha256=digest((STUDY / 'local/result.json').read_bytes()),
                gates={'team_wins': 80, 'minimum_mixed_win_gain': .05,
                       'minimum_improved_rosters': 2, 'context_sign_p_max': .05,
                       'maximum_death_rate_ratio': 1.1, 'maximum_class_win_regression': .30,
                       'minimum_field_wins': 70},
                design='Complete80candidate games,40/color, vs exactJordan175; preserve prior80/80 '
                       'on the same source. If passed, three fresh fixed-roster100episode requests '
                       'perarm (600games), identical pinned rosters and role rotations, independent '
                       'server seeds. Compare30roster/role contexts using per-context win fractions '
                       'and a one-sided sign statistic, not an episode-level significance claim. '
                       'Require>=5pp pooledgain,>=2/3rosters improve, signp<.05, deaths/alivemin '
                       '<=1.1control, no classregression>30pp, allgear/fullVM/replays/sourcevalid. '
                       'Then100sampledfieldgames>=70wins. No tuning between arms. Contexts share '
                       'incumbents; all inference remains scoped to this design. No promotion '
                       'before every gate passes.')
    if game['id'] != plan['target']['coworld_id']:
        raise ValueError('Current source differs from baseline evidence')
    write(path, plan)
    write(STUDY / 'rival.json', {'label': plan['rival'], 'id': plan['rival_version']})
    return plan


def team():
    plan = freeze()
    folder = prepare_team(plan['candidate'], STUDY, 'aaron-gota-ir-loadout', CHANGE)
    run_prepared(folder)
    inventory(folder)
    result = read(folder / 'result.json')['rivals']['jordan']
    passed = result['wins'] == plan['gates']['team_wins'] and all(r['gear_heroes'] == 5 for r in result['rows'])
    write(STUDY / 'team-gate.json', {'passed': passed, 'wins': result['wins'], 'games': 80,
                                    'evidence': str(folder / 'result.json'),
                                    'interpretation': 'Fixed team nonregression only; mixed A/B still required.'})
    feedback = folder / 'team-feedback'
    if not feedback.exists():
        parent = STUDY / 'local/feedback' / plan['candidate']
        record(parent / 'policy.ir.json', parent / 'policy.bas',
               f'ExactJordan175 team probe on {plan["game_version"]}: {result["wins"]}/80 wins; '
               f'nonregression gate passed={passed}. FulltenVMs/replays verified. Fixedlineups '
               'are not independent strategies; require mixedroster A/B and field beforepromotion.',
               folder / 'result.json', feedback)
    print('Team nonregression:', passed, flush=True)


def mixed():
    plan = freeze()
    if not read(STUDY / 'team-gate.json')['passed']:
        raise ValueError('Team gate failed; candidate is not eligible')
    version = read(STUDY / 'hosted' / plan['candidate'] / 'uploaded-version.json')['id']
    root = STUDY / 'hosted-confirmation'
    root.mkdir(exist_ok=True)
    write(root / 'plan.json', plan)
    folders = []
    for i, opponents in enumerate(plan['rosters']):
        for arm, subject in [('control', CONTROL), ('candidate', version)]:
            out = root / arm / f'part-{i}'
            out.mkdir(parents=True, exist_ok=True)
            arm_plan = {k: plan[k] for k in ['target', 'game_version', 'game_source', 'config']}
            arm_plan.update(opponents=opponents, policy_version=subject,
                            run_id=f'loadout-r5-{digest(plan)[:16]}-{arm}-{i}', notes=plan['design'])
            if (out / 'plan.json').exists() and read(out / 'plan.json') != arm_plan:
                raise ValueError('Frozen arm changed')
            write(out / 'plan.json', arm_plan)
            shutil.copy2(RUN / 'r5/audit', out / 'audit')
            with client() as c:
                create(c, batch_body(arm_plan, 100), out / 'batch', dry_run=True)
            folders.append(out)
    # Finish all server games, artifacts and audits for an arm before the next.
    for out in folders:
        live()
        run_queue([out])
    compare()


def compare():
    plan = freeze()
    root = STUDY / 'hosted-confirmation'
    parts = {arm: [cohort(root / arm / f'part-{i}', 2) for i in range(3)]
             for arm in ['control', 'candidate']}
    seeds = set()
    for arm, cohorts in parts.items():
        for i, part in enumerate(cohorts):
            arm_plan = read(root / arm / f'part-{i}/plan.json')
            if arm_plan['opponents'] != plan['rosters'][i]:
                raise ValueError('Mismatched pinned roster')
            for row in part['rows']:
                if row['seed'] in seeds:
                    raise ValueError('Reused effective seed across arms')
                seeds.add(row['seed'])
                row['roster_index'] = i
    arms = {arm: summarize(cohorts) for arm, cohorts in parts.items()}
    control, candidate = arms['control'], arms['candidate']
    contexts = []
    for i in range(3):
        for slot in range(10):
            scores = {arm: [r['win'] for r in parts[arm][i]['rows'] if r['slot'] == slot] for arm in arms}
            if any(len(v) != 10 for v in scores.values()):
                raise ValueError('Incomplete role context')
            delta = (sum(scores['candidate']) - sum(scores['control'])) / 10
            contexts.append({'roster': i, 'slot': slot, 'delta': delta})
    plus = sum(r['delta'] > 0 for r in contexts)
    minus = sum(r['delta'] < 0 for r in contexts)
    p = sum(comb(plus + minus, x) for x in range(plus, plus + minus + 1)) / 2 ** (plus + minus)
    gains = [(parts['candidate'][i]['wins'] - parts['control'][i]['wins']) / 100 for i in range(3)]
    gates = plan['gates']
    checks = {'pooled_win_gain': (candidate['wins'] - control['wins']) / 300 >= gates['minimum_mixed_win_gain'],
              'roster_breadth': sum(g > 0 for g in gains) >= gates['minimum_improved_rosters'],
              'context_sign': p < gates['context_sign_p_max'],
              'survival': candidate['death_rate'] <= control['death_rate'] * gates['maximum_death_rate_ratio'],
              'equipment': candidate['equipment_games'] == 300,
              'classes': all((c['wins'] - control['class_wins'][name]['wins']) / c['games'] >=
                             -gates['maximum_class_win_regression'] for name, c in candidate['class_wins'].items())}
    result = {'arms': arms, 'contexts': contexts, 'roster_gains': gains, 'context_sign_p': p,
              'checks': checks, 'passed': all(checks.values()), 'design': plan['design'],
              'field_guardrail': 'Not run yet; required before deployment.'}
    write(root / 'result.json', result)
    inventory(root)
    parent = STUDY / 'hosted' / plan['candidate'] / 'team-feedback'
    output = root / 'feedback'
    if not output.exists():
        record(parent / 'policy.ir.json', parent / 'policy.bas',
               f'Fresh mixedroster comparison: candidate {candidate["wins"]}/300 vscontrol '
               f'{control["wins"]}/300. Thirty roster/role contexts, signp={p}, roster gains={gains}. '
               f'Checks {checks}; everyfullreplay/VM/source/roster verified. Fixedroster contexts '
               'shareincumbents; do not infer broad independent significance. Field remainsrequired.',
               root / 'result.json', output)
    print({k: v for k, v in result.items() if k not in {'arms', 'contexts'}}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['freeze', 'team', 'mixed', 'compare'])
    parser.add_argument('--study', type=Path, default=STUDY)
    args = parser.parse_args()
    STUDY = args.study.resolve()
    globals()[args.command]()
