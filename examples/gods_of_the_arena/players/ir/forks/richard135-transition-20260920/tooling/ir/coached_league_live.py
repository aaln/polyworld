"""Matched league simulations with both owned players, allied or opposed."""
import argparse
from math import comb
import random
import shutil

from campaign_hosted_compare import cohort
from command_diversity import inventory
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create, get
from policy_ir import read, write, digest
from release_deploy_pair import clone_for_aaron
from release_hosted import summarize, OPTIMIZER
from release_workspace import RUN
from win_hosted import live

ROOT = RUN / 'coached-lanes/r5-live-league'
PARENT = RUN / 'coached-lanes/r5-asymmetric'
AARON = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'
CONTROL = ['810d3860-af35-4fed-9364-a4e4bd8b0c2b', 'fa0cab2a-708f-40e0-b6b8-1e44ffeea124']


def prepare():
    game = live()
    ROOT.mkdir(exist_ok=True)
    if (ROOT / 'plan.json').exists():
        plan = read(ROOT / 'plan.json')
        if game['id'] != plan['target']['coworld_id']:
            raise ValueError('Live game changed')
        return plan
    if not read(PARENT / 'team-gate.json')['passed']:
        raise ValueError('Candidate has not passed eighty-game Jordan check')
    parent = read(PARENT / 'hosted-plan.json')
    candidate = read(PARENT / 'hosted/blue_damage/uploaded-version.json')
    metadata = read(PARENT / 'hosted/blue_damage/upload-request.json')
    source = (PARENT / 'local/candidates/blue_damage/policy.bas').read_bytes()
    with client() as c:
        champions = get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
        write(ROOT / 'champions.json', champions)
        clone = clone_for_aaron(c, ROOT, metadata, source,
                               'Inert experimental clone for both-player league simulation; '
                               'locally qualified and80/80vsJordan175, mixed-team unvalidated. '
                               'No champion selection.')
    available = sorted([{'id': r['policy_version']['id'], 'label': r['policy_version']['label'],
                         'player_id': r['player']['id']} for r in champions
                        if r['player']['id'] not in {OPTIMIZER, AARON} and r['status'] == 'competing'
                        and r['substatus'] == 'active'], key=lambda r: r['label'])
    if len(available) < 8:
        raise ValueError('Need eight other distinct players')
    random.Random(7570916).shuffle(available)
    lineups = []
    for i, partner_slot in enumerate([1, 1, 5, 5]):
        opponents = [available[(j + i*3) % len(available)] for j in range(8)]
        lineups.append({'partner_slot': partner_slot, 'other_players': opponents})
    plan = {k: parent[k] for k in ['target', 'game_version', 'game_source', 'config']}
    plan.update(control_versions=CONTROL, candidate_versions=[candidate['id'], clone['id']],
                candidate_labels=[f'{v["name"]}:v{v["version"]}' for v in [candidate, clone]],
                lineups=lineups, parent_team_gate_sha256=digest((PARENT / 'team-gate.json').read_bytes()),
                basic_sha256=digest(source),
                authorization='User: test assortment of other players including both owned players, together or opposed, to simulate the league.',
                design='Four matched pinned-roster100episode requests/arm (800games total). '
                       'Two owned player versions plus eight other distinct league players in everygame. '
                       'Both owned versions change together in the candidatearm. Two adjacent-own '
                       'rosters yield160allied+40opposed games/arm; two opposite-own rosters add '
                       '200opposed. Balanced role rotation, fresh serverseeds, alltenVM/replay/config '
                       'audits. Primary comparison:160alliedgames/arm across16roster-role contexts. '
                       'Opposed games are separate diagnostics: combined owned winrate cannot improve '
                       'when one must lose. Do not count two teammates as two independent wins. '
                       'No tuning between arms; field guardrail required before deployment.',
                gates={'minimum_allied_gain': .05, 'minimum_improved_allied_rosters': 2,
                       'context_sign_p_max': .05, 'maximum_pair_death_rate_ratio': 1.1,
                       'maximum_class_regression': .30, 'minimum_field_allied_win_rate': .70})
    write(ROOT / 'plan.json', plan)
    write(PARENT / 'mixed-plan-superseded.json', {
        'reason': plan['authorization'], 'original_plan_retained': str(PARENT / 'hosted-plan.json'),
        'original_mixed_requests_launched': 0, 'new_study': str(ROOT)})
    return plan


def arm_plan(plan, arm, i):
    versions = plan[arm + '_versions']
    lineup = plan['lineups'][i]
    refs = [None] * 10
    refs[0] = {'id': versions[0], 'player_id': OPTIMIZER}
    refs[lineup['partner_slot']] = {'id': versions[1], 'player_id': AARON}
    others = iter(lineup['other_players'])
    for slot in range(10):
        if refs[slot] is None:
            refs[slot] = next(others)
    result = {k: plan[k] for k in ['target', 'game_version', 'game_source', 'config']}
    result.update(policy_version=versions[0], partner_version=versions[1],
                  opponents=refs[1:], run_id=f'livepair-r5-{digest(plan)[:16]}-{arm}-{i}',
                  notes=plan['design'])
    return result


def run():
    plan = prepare()
    folders = []
    for i in range(4):
        for arm in ['control', 'candidate']:
            out = ROOT / arm / f'part-{i}'
            out.mkdir(parents=True, exist_ok=True)
            expected = arm_plan(plan, arm, i)
            if (out / 'plan.json').exists() and read(out / 'plan.json') != expected:
                raise ValueError('Frozen matched roster changed')
            write(out / 'plan.json', expected)
            shutil.copy2(RUN / 'r5/audit', out / 'audit')
            with client() as c:
                create(c, batch_body(expected, 100), out / 'batch', dry_run=True)
            folders.append(out)
    for out in folders:
        live()
        if ((out / 'collection.json').exists() and (out / 'audit-progress.json').exists()
                and read(out / 'collection.json')['episodes'] == 100
                and read(out / 'audit-progress.json')['verified'] == 100
                and len(list((out / 'artifacts').glob('*/.done'))) == 100
                and len(list((out / 'artifacts').glob('*/audit.json'))) == 100):
            # The final report rechecks every cached artifact and hash. A resumed
            # run need not restart completed collection/audit worker processes.
            print('Retained completed arm:', out.relative_to(ROOT), flush=True)
            continue
        run_queue([out])
    report()


def report():
    plan = prepare()
    parts = {arm: [] for arm in ['control', 'candidate']}
    seen = set()
    for arm in parts:
        for i in range(4):
            out = ROOT / arm / f'part-{i}'
            if read(out / 'plan.json') != arm_plan(plan, arm, i):
                raise ValueError('Comparison arm differs from frozen design')
            part = cohort(out, 2)
            for row in part['rows']:
                if row['seed'] in seen:
                    raise ValueError('Effective seed reused across arms')
                seen.add(row['seed'])
                artifacts = out / 'artifacts' / row['episode']
                ep, audit = read(artifacts / 'episode.json'), read(artifacts / 'audit.json')
                expected_owners = {v['id']: v['player_id'] for v in arm_plan(plan, arm, i)['opponents']}
                expected_owners[plan[arm + '_versions'][0]] = OPTIMIZER
                if {p['position']: p['player_id'] for p in ep['participants']} != {
                        slot: expected_owners[version] for slot, version in enumerate(ep['policy_version_ids'])}:
                    raise ValueError('Actual player ownership differs from the two-player league design')
                partner = ep['policy_version_ids'].index(plan[arm + '_versions'][1])
                own = audit['heroes'][row['slot']]
                buddy = audit['heroes'][partner]
                allied = partner // 5 == row['slot'] // 5
                if (allied and own['score'] != buddy['score']) or (not allied and own['score'] + buddy['score'] > 1):
                    raise ValueError('Invalid team scores')
                row.update(roster_index=i, partner_slot=partner, allied=allied,
                           partner_class=buddy['class'], partner_win=buddy['score'],
                           partner_deaths=buddy['deaths'], partner_alive_ticks=buddy['alive_ticks'],
                           partner_gear=buddy['first_gear_tick'] >= 0)
            parts[arm].append(part)
    arms = {}
    for arm, cohorts in parts.items():
        total = summarize(cohorts)
        rows = total['rows']
        allied = [r for r in rows if r['allied']]
        opposed = [r for r in rows if not r['allied']]
        if len(allied) != 160 or len(opposed) != 240:
            raise ValueError('Unexpected allied/opposed coverage')
        total.update(allied_games=160, allied_wins=sum(r['win'] for r in allied),
                     opposed_games=240, opposed_optimizer_wins=sum(r['win'] for r in opposed),
                     opposed_aaron_wins=sum(r['partner_win'] for r in opposed),
                     opposed_draws=sum(not r['win'] and not r['partner_win'] for r in opposed),
                     both_bought_equipment=sum(r['first_gear_tick'] >= 0 and r['partner_gear'] for r in rows),
                     pair_death_rate=sum(r['deaths'] + r['partner_deaths'] for r in rows) * 1440 /
                                     sum(r['alive_ticks'] + r['partner_alive_ticks'] for r in rows))
        arms[arm] = total
    contexts = []
    gains = []
    for i in range(2):
        counts = {arm: sum(r['win'] for r in parts[arm][i]['rows'] if r['allied']) for arm in arms}
        gains.append((counts['candidate'] - counts['control']) / 80)
        for slot in range(10):
            rr = {arm: [r for r in parts[arm][i]['rows'] if r['slot'] == slot and r['allied']] for arm in arms}
            if not rr['control']:
                continue
            if any(len(v) != 10 for v in rr.values()):
                raise ValueError('Incomplete allied role context')
            contexts.append({'roster': i, 'slot': slot,
                             'delta': (sum(r['win'] for r in rr['candidate']) - sum(r['win'] for r in rr['control'])) / 10})
    positive = sum(c['delta'] > 0 for c in contexts)
    negative = sum(c['delta'] < 0 for c in contexts)
    sign_p = sum(comb(positive + negative, j) for j in range(positive, positive + negative + 1)) / 2 ** (positive + negative)
    a, b, gates = arms['candidate'], arms['control'], plan['gates']
    checks = {'allied_gain': (a['allied_wins'] - b['allied_wins']) / 160 >= gates['minimum_allied_gain'],
              'allied_roster_breadth': sum(g > 0 for g in gains) >= gates['minimum_improved_allied_rosters'],
              'allied_context_sign': sign_p < gates['context_sign_p_max'],
              'survival': a['pair_death_rate'] <= b['pair_death_rate'] * gates['maximum_pair_death_rate_ratio'],
              'equipment': a['both_bought_equipment'] == 400,
              'classes': all((v['wins'] - b['class_wins'][name]['wins']) / v['games'] >= -gates['maximum_class_regression']
                             for name, v in a['class_wins'].items()),
              'opposed_draws': a['opposed_draws'] <= b['opposed_draws']}
    result = {'arms': arms, 'allied_contexts': contexts, 'allied_roster_gains': gains,
              'allied_context_sign_p': sign_p, 'checks': checks, 'passed': all(checks.values()),
              'design': plan['design'], 'interpretation': 'Fixed league simulation; contexts share '
              'incumbents and episodes may repeat command tapes. Sign statistic is scoped to tested '
              'roster-role contexts, not broad independent strategies. Opposed combined wins are '
              'not evidence of improvement. Field guardrail still required.'}
    write(ROOT / 'result.json', result)
    inventory(ROOT)
    if not (ROOT / 'feedback').exists():
        parent = PARENT / 'hosted/blue_damage/team-feedback'
        record(parent / 'policy.ir.json', parent / 'policy.bas',
               f'Both-owned-player league simulation800games. Allied candidate {a["allied_wins"]}/160 '
               f'versus current {b["allied_wins"]}/160; per-roster gains {gains}; context signp={sign_p}. '
               f'Checks {checks}; opposed games evaluated separately. {result["interpretation"]}',
               ROOT / 'result.json', ROOT / 'feedback')
    print({k: v for k, v in result.items() if k not in {'arms', 'allied_contexts'}}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'report'])
    args = parser.parse_args()
    globals()[args.command]()
