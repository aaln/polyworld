"""Frozen current-champion validation; keep the already-running guardrails intact."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time

from coached_league_live import AARON, OPTIMIZER, arm_plan
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create
from jordan_lineup import STUDY
from jordan_lineup_guardrails import ROOT as EARLY, mixed_part, pin_auditor
from policy_ir import digest, read, write
from rush_sentries import STUDY as BASE
from win_hosted import live

ROOT = STUDY / 'wide-validation'
WINNER = STUDY / 'hosted/blue_repair'
AUTHORIZATION = ('aaron-gota-ir-perimeter-blue_repair-0916:v1 seems to be beating jordan now. '
                 'so we can run xp requests against the wide pool of 5v5 10 players and '
                 '5v5 2 players. if it does well, promote it to both players in league')


def frozen(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and read(path) != value:
        raise ValueError('Frozen evidence changed: ' + str(path))
    if not path.exists():
        write(path, value)


def prepare():
    game = live()
    if (ROOT / 'plan.json').exists():
        plan = read(ROOT / 'plan.json')
        if game['version'] != plan['game_version'] or game['manifest']['game']['runnable']['source_url'] != plan['game_source']:
            raise ValueError('Published release changed')
        return plan
    prior = read(EARLY / 'plan.json')
    all_rows = read(STUDY / 'wide-field-champions.json')
    rivals = [{'id': r['policy_version']['id'], 'label': r['policy_version']['label'], 'player_id': r['player']['id']}
              for r in all_rows if r['status'] == 'competing' and r['substatus'] == 'active'
              and r['player']['id'] not in {OPTIMIZER, AARON}]
    if len(rivals) != 13 or len({r['player_id'] for r in rivals}) != 13:
        raise ValueError('Expected the reviewed thirteen distinct current opposing champions')
    current = {r['player_id']: r for r in rivals}
    lineups = [{'partner_slot': p['partner_slot'], 'other_players': [current[r['player_id']] for r in p['other_players']]}
               for p in prior['lineups']]
    if {r['id'] for p in lineups for r in p['other_players']} != {r['id'] for r in rivals}:
        raise ValueError('Mixed roster pool does not cover all thirteen current champions')
    old_paths = {read(Path(p) / 'plan.json')['rival_version']: p for p in read(BASE / 'league-sweep/plan.json')['head_paths']}
    existing = {read(Path(p) / 'plan.json')['rival_version']: p for p in read(EARLY / 'schedule.json')['heads']}
    existing[read(WINNER / 'jordan/plan.json')['rival_version']] = str(WINNER / 'jordan')
    plan = {k: prior[k] for k in ('target', 'game_version', 'game_source', 'config', 'control_versions', 'candidate_versions')}
    plan.update(authorization=AUTHORIZATION, lineups=lineups, rivals=rivals,
                snapshot_sha256=digest((STUDY / 'wide-field-champions.json').read_bytes()),
                basic_sha256=digest((STUDY / 'candidate/policy.bas').read_bytes()),
                gates={'maximum_head_color_loss': 4, 'maximum_head_total_loss': 8,
                       'minimum_aggregate_head_gain': 16, 'maximum_allied_loss': 8,
                       'minimum_allied_wins': 112, 'maximum_roster_loss': 8,
                       'maximum_class_fraction_loss': .30, 'no_added_opposed_draws': True},
                design='Thirteen pinned current opposing champions,80 games each,40 per color. '
                'Reuse candidate Jordan80 and khors80 already requested; complete all remaining880. '
                'For four changed opponent versions run fresh deployed80 controls; reuse exact-source '
                'controls for unchanged rivals. Fresh matched ten-player200 per arm with both owned '
                'players and all thirteen rivals across two fixed rosters,160allied+40opposed per arm. '
                'Both owned registrations change together. Retain earlier Richard69/mixed guardrail '
                'as an additional veto, never overwrite it. No tuning. Repeated command trajectories '
                'limit independence: empirical rollout guardrails, not a league rank or formal '
                'independent-trial significance claim. User-authorized promotion only after every gate.',
                created_at=datetime.fromtimestamp((STUDY / 'wide-field-champions.json').stat().st_mtime, timezone.utc).isoformat())
    template = read(WINNER / 'jordan/plan.json')
    schedule = []
    for rival in rivals:
        key = 'rival_' + rival['id'].split('-')[0]
        paths = {}
        for arm in ('control', 'candidate'):
            reuse = old_paths if arm == 'control' else existing
            if rival['id'] in reuse:
                paths[arm] = reuse[rival['id']]
                continue
            folder = ROOT / 'heads' / key / arm
            p = {k: plan[k] for k in ('target', 'game_version', 'game_source', 'config')}
            p.update(policy_version=plan[arm + '_versions'][0], policy_label=arm,
                     rival=rival['label'], rival_version=rival['id'], rival_key=key,
                     episodes_per_color=40, interpretation=template['interpretation'], design=plan['design'])
            frozen(folder / 'plan.json', p)
            for color in ('red', 'blue'):
                out = folder / key / color
                slots = list(range(5)) if color == 'red' else list(range(5, 10))
                roster = [p['policy_version'] if s in slots else rival['id'] for s in range(10)]
                ap = p | {'color': color, 'own_slots': slots, 'roster': roster}
                frozen(out / 'plan.json', ap)
                pin_auditor(out)
                body = {'idempotency_key': 'gota-lineup-wide-' + digest(ap)[:20], 'target': p['target'],
                        'game_config_overrides': p['config'], 'num_episodes': 40,
                        'roster': [{'slot': s, 'player': {'policy_ref': ref}} for s, ref in enumerate(roster)],
                        'notes': plan['design'] + ' ' + rival['label'] + ' ' + arm + ' ' + color}
                with client() as c:
                    create(c, body, out / 'batch', dry_run=True)
            paths[arm] = str(folder)
        schedule.append({'rival': rival, **paths})
    plan['heads'] = schedule
    plan['additional_new_games'] = 1600
    plan['candidate_current_head_games'] = 1040
    plan['fresh_mixed_games_per_arm'] = 200
    for i in range(2):
        for arm in ('control', 'candidate'):
            out = ROOT / 'mixed' / arm / f'part-{i}'
            p = arm_plan(plan, arm, i)
            frozen(out / 'plan.json', p)
            pin_auditor(out)
            with client() as c:
                create(c, batch_body(p, 100), out / 'batch', dry_run=True)
    frozen(ROOT / 'plan.json', plan)
    return plan


def mixed_summary(rows):
    allied = [r for r in rows if r['allied']]
    opposed = [r for r in rows if not r['allied']]
    if len(allied) != 160 or len(opposed) != 40:
        raise ValueError('Incorrect allied/opposed coverage')
    return {'games': 200, 'allied_wins': sum(r['win'] for r in allied),
            'opposed_draws': sum(not r['win'] and not r['partner_win'] for r in opposed),
            'both_gear': sum(r['first_gear_tick'] >= 0 and r['partner_gear'] for r in rows),
            'rosters': {str(i): sum(r['win'] for r in allied if r['roster_index'] == i) for i in range(2)},
            'classes': {c: {'games': len(cr := [r for r in allied if r['class'] == c]), 'wins': sum(r['win'] for r in cr)}
                        for c in {r['class'] for r in rows}}, 'rows': rows}


def metric_checks(plan, arms, heads, early_passed, jordan_passed):
    a, b, g = arms['candidate'], arms['control'], plan['gates']
    checks = {'prior_guardrails': early_passed, 'jordan': jordan_passed,
              'allied': a['allied_wins'] >= b['allied_wins'] - g['maximum_allied_loss'],
              'absolute': a['allied_wins'] >= g['minimum_allied_wins'],
              'rosters': all(a['rosters'][str(i)] >= b['rosters'][str(i)] - g['maximum_roster_loss'] for i in range(2)),
              'classes': a['classes'].keys() == b['classes'].keys() and all(
                  v['games'] >= 10 and v['games'] == b['classes'][c]['games'] and
                  v['wins'] >= b['classes'][c]['wins'] - g['maximum_class_fraction_loss'] * v['games']
                  for c, v in a['classes'].items()),
              'opposed_draws': a['opposed_draws'] <= b['opposed_draws'],
              'equipment': a['both_gear'] == b['both_gear'] == 200}
    gain = 0
    for key, h in heads.items():
        x, y = h['candidate'], h['control']
        gain += x['wins'] - y['wins']
        checks[key] = (x['wins'] >= y['wins'] - g['maximum_head_total_loss'] and
                       all(x['colors'][c]['win'] >= y['colors'][c]['win'] - g['maximum_head_color_loss'] for c in ('red', 'blue')))
    checks['aggregate_head_gain'] = gain >= g['minimum_aggregate_head_gain']
    return checks


def report():
    plan = read(ROOT / 'plan.json')
    heads, evidence, seeds = {}, {}, set()
    for row in plan['heads']:
        h = {}
        for arm in ('control', 'candidate'):
            path = Path(row[arm]); p = read(path / 'plan.json')
            for k in ('target', 'game_version', 'game_source', 'config'):
                if p[k] != plan[k]:
                    raise ValueError('Reused source/config differs')
            if p['rival_version'] != row['rival']['id'] or p['policy_version'] != plan[arm + '_versions'][0]:
                raise ValueError('Wrong exact policy version in comparison')
            x = read(path / 'result.json')['rivals'][p['rival_key']]
            if x['games'] != 80 or not x['all_full_audits_passed'] or not all(r['gear_heroes'] == 5 for r in x['rows']):
                raise ValueError('Incomplete or unaudited head evidence')
            for r in x['rows']:
                if r['seed'] in seeds: raise ValueError('Repeated comparison seed')
                seeds.add(r['seed'])
            evidence[str(path / 'result.json')] = digest((path / 'result.json').read_bytes())
            inventory(path)
            h[arm] = x
        heads[row['rival']['id']] = h
    arms = {}
    for arm in ('control', 'candidate'):
        rows = []
        for i in range(2):
            folder = ROOT / 'mixed' / arm / f'part-{i}'
            if read(folder / 'plan.json') != arm_plan(plan, arm, i):
                raise ValueError('Frozen mixed arm changed')
            for r in mixed_part(folder):
                if r['seed'] in seeds: raise ValueError('Repeated mixed seed')
                seeds.add(r['seed']); r['roster_index'] = i; rows.append(r)
        arms[arm] = mixed_summary(rows)
    checks = metric_checks(plan, arms, heads, read(EARLY / 'result.json')['passed'], read(WINNER / 'jordan-result.json')['passed'])
    evidence[str(EARLY / 'result.json')] = digest((EARLY / 'result.json').read_bytes())
    for p in (WINNER / 'replay-review/result.json', WINNER / 'jordan-result.json'):
        evidence[str(p)] = digest(p.read_bytes())
    result = {'heads': heads, 'arms': arms, 'checks': checks, 'passed': all(checks.values()),
              'head_wins': {arm: sum(h[arm]['wins'] for h in heads.values()) for arm in arms},
              'games_per_head_arm': 1040, 'games_per_mixed_arm': 200,
              'plan_sha256': digest((ROOT / 'plan.json').read_bytes()), 'evidence_sha256': evidence,
              'scope': plan['design']}
    write(ROOT / 'result.json', result)
    if not (ROOT / 'feedback').exists():
        src = EARLY / 'feedback'
        record(src / 'policy.ir.json', src / 'policy.bas',
               f'Frozen current field validation: head wins {result["head_wins"]}/1040 each; '
               f'mixed allied candidate {arms["candidate"]["allied_wins"]}/160, deployed {arms["control"]["allied_wins"]}/160. '
               f'Checks {checks}. Fully audited; empirical guardrails with correlated trajectories, not a rank claim.',
               ROOT / 'result.json', ROOT / 'feedback')
    lines = ['# Current field validation', '', f'Promotion gates passed: {result["passed"]}.', '',
             '| Opponent | Candidate red / blue | Deployed red / blue |', '|---|---:|---:|']
    for h in heads.values():
        a, b = h['candidate'], h['control']
        lines.append(f'| {a["label"]} | {a["colors"]["red"]["win"]} / {a["colors"]["blue"]["win"]} | {b["colors"]["red"]["win"]} / {b["colors"]["blue"]["win"]} |')
    lines += ['', f'Allied mixed wins: {arms["candidate"]["allied_wins"]}/160 versus {arms["control"]["allied_wins"]}/160.',
              '', plan['design'], '', 'The optimizer lab has no validated eval-design N floor. These are scoped empirical guardrails; no formal significance claim.']
    (ROOT / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    print('Wide verdict:', result['head_wins'], {a: x['allied_wins'] for a, x in arms.items()}, checks, flush=True)
    return result


def run(promote=False):
    plan = prepare()
    # Another controller owns both earlier guardrails and the original sweep.
    # Wait for both to finish; never create concurrent remote batches.
    while not (EARLY / 'result.json').exists() or not (BASE / 'league-sweep/completed.json').exists():
        write(ROOT / 'queue-state.json', {'stage': 'waiting_for_existing_suites'})
        time.sleep(15)
    ordered = sorted(plan['heads'], key=lambda r: (not str(ROOT) in r['control'], r['rival']['label']))
    for i in range(2):
        for arm in ('control', 'candidate'):
            out = ROOT / 'mixed' / arm / f'part-{i}'
            write(ROOT / 'queue-state.json', {'stage': 'mixed', 'arm': arm, 'roster': i})
            if not (out / 'audit-progress.json').exists() or read(out / 'audit-progress.json')['verified'] != 100:
                live(); run_queue([out])
        # Begin direct matchups promptly between mixed roster pairs.
        for row in ordered[i::2]:
            for arm in ('control', 'candidate'):
                out = Path(row[arm])
                write(ROOT / 'queue-state.json', {'stage': 'heads', 'arm': arm, 'rival': row['rival']['label']})
                if not (out / 'result.json').exists(): run_prepared(out)
                inventory(out)
    result = report()
    write(ROOT / 'queue-state.json', {'stage': 'completed', 'passed': result['passed']})
    requested = STUDY / 'deployment-requested/deployment-verified.json'
    if requested.exists():
        receipt = read(requested)
        final = ROOT / 'postdeployment-feedback'
        if not final.exists():
            record(ROOT / 'feedback/policy.ir.json', ROOT / 'feedback/policy.bas',
                   'The user explicitly promoted the exact tested pair before this broad evaluation '
                   'finished. Keep its original result and gates unchanged; this is post-deployment '
                   'evidence, not a retrospective claim that deployment passed those gates. '
                   f'Complete broad checks passed: {result["passed"]}.', requested, final)
        from policy_ir import HERE
        active = read(HERE / 'active_policy.json')
        if {r['player']: r['version'] for r in active['players']} == receipt['versions']:
            if digest((final / 'policy.bas').read_bytes()) != receipt['source_sha256']:
                raise ValueError('Post-deployment feedback changed the tested policy')
            active.update(policy=str(final / 'policy.bas'), semantic_ir=str(final / 'policy.ir.json'),
                          latest_evaluation=str(ROOT / 'result.json'))
            write(HERE / 'active_policy.json', active)
        write(ROOT / 'queue-state.json', {'stage': 'postdeployment_evaluation_complete', 'passed': result['passed'],
              'user_requested_deployment': str(requested), 'league_selection_changed_by_evaluation': False})
        print('Broad evidence complete; prior user-requested deployment retained. No automatic rollback.', flush=True)
    elif promote and result['passed']:
        from jordan_lineup_promote import main
        main(apply=True)
        write(ROOT / 'queue-state.json', {'stage': 'promoted_both_players', 'passed': True})
    elif promote:
        print('Promotion withheld: a frozen validation gate failed. Exact candidate and all results retained.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'report'])
    parser.add_argument('--promote-if-passed', action='store_true')
    args = parser.parse_args()
    if args.command == 'run': run(args.promote_if_passed)
    else: globals()[args.command]()
