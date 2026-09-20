"""Prospective check against the newly observed round-378 league threat."""
import time
from economy_feedback import record
from policy_ir import read, write, digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure import STUDY
from red_pressure_hosted import prepare_head, result as head_result
from threat_coverage_hosted import control
from win_hosted import live

ROOT = STUDY / 'g002-guardrail'


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    plan = {'candidate': 'pressure20', 'rival': 'gota-g002:v1',
        'observed_loss': 'ereq_dfb9857e-35f2-4bcf-8d9f-00db7b69eb3e',
        'new_candidate_games': 80, 'reused_deployed_games': 80,
        'gates': {'minimum_red_wins': 24, 'maximum_color_loss': 2},
        'scope': 'New threat discovered during monitoring. Complete 40 episodes per color, '
                 'full VM/replay/equipment checks. Reuse exact already-planned deployed wide '
                 'control. Additional promotion requirement; original field gates unchanged. '
                 'Fixed-lineup empirical evidence, not independent-trial significance.'}
    freeze(ROOT / 'prospective-plan.json', plan)
    guard = STUDY / 'promotion-guardrail'
    while alive(read(guard / 'process.json')['pid']):
        time.sleep(15)
    if not (guard / 'result.json').exists():
        raise RuntimeError('Pressure field guardrail stopped without reconciled result')
    prior = read(guard / 'result.json')
    if not prior['passed']:
        write(ROOT / 'not-run.json', {'reason': 'Pressure field guardrail failed; candidate ineligible.',
                                    'checks': prior['checks']})
        return
    root = STUDY / 'hosted' / plan['candidate']
    ref = control(plan['rival']); before = read(ref / 'plan.json'); game = live()
    if game['version'] != before['game_version'] or game['manifest']['game']['runnable']['source_url'] != before['game_source']:
        raise ValueError('Published release changed')
    prepare_head(ROOT / 'candidate', read(root / 'uploaded-version.json'), ref,
                 'Round378 gota-g002 threat guardrail', plan['scope'])
    with drained_wide(ROOT):
        b, a = head_result(ref), head_result(ROOT / 'candidate')
        checks = {'red_absolute': a['colors']['red']['win'] >= plan['gates']['minimum_red_wins']}
        for color in ('red', 'blue'):
            checks[color] = a['colors'][color]['win'] >= b['colors'][color]['win'] - plan['gates']['maximum_color_loss']
        report = {'candidate': a, 'control': b, 'checks': checks, 'passed': all(checks.values()),
                  'plan_sha256': digest((ROOT / 'prospective-plan.json').read_bytes()),
                  'scope': plan['scope']}
        write(ROOT / 'result.json', report)
        feedback = guard / 'feedback'
        if not (ROOT / 'feedback').exists():
            record(feedback / 'policy.ir.json', feedback / 'policy.bas',
                   f'New league threat gota-g002: pressure {a["wins"]}/80 versus deployed {b["wins"]}/80; '
                   f'checks {checks}. Other frozen promotion gates remain required.',
                   ROOT / 'result.json', ROOT / 'feedback')
        print('Pressure gota-g002', a['colors'], b['colors'], checks, flush=True)


if __name__ == '__main__':
    main()
