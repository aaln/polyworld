"""Assess the Richard80/80 winner against actual league threats, preserving failures."""
from ally_assist import STUDY
from policy_ir import read, write, digest
from economy_feedback import record
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result as head_result
from threat_coverage_hosted import control
from jordan_lineup_wide import WINNER
import core_pressure_hosted as field_runner
from win_hosted import live


if __name__ == '__main__':
    diagnostic = read(STUDY/'diagnostic-result.json')
    assert diagnostic['candidate']['wins'] == 80
    assert not diagnostic['promotion_eligible']
    assert read(STUDY/'local/comparison.json')['qualified'] == []
    design = ('Follow-up assessment of assist22 after Richard80/80. Preserve failed local '
        'convoy gate:56/60 versus pressureparent58, deployed54. Local proxy regression is '
        'unresolved, not relabeled a pass. Test actual league threats and mixed field to '
        'assess the tradeoff against deployedG. Require redkite24red and no more than2color '
        'wins lost versusG, Jordan38/color, black losses at mostG+2, and existing mixed200 '
        'guards. Forty/color complete perhead. Directional fixed-lineup evidence; no '
        'automatic promotion, final tradeoff review required even if hosted checks pass.')
    plan = {'design': design, 'order': ['red-kite', 'g002', 'jordan', 'vanguard', 'black-kite', 'field200'],
        'maximum_new_games': 600, 'reused_richard_games': 80, 'local_gate_failed': True,
        'automatic_promotion': False, 'diagnostic_sha256': digest((STUDY/'diagnostic-result.json').read_bytes())}
    freeze(STUDY/'guard-prospective.json', plan)
    live()
    root = STUDY/'hosted/assist22'; version = read(root/'uploaded-version.json')
    checks = {}; heads = {}; field = None
    refs = [('red-kite', control('red-kite:v27')), ('g002', control('gota-g002:v1')),
            ('jordan', WINNER/'jordan'), ('vanguard', control('gota-vanguard-rally-hold:v1')),
            ('black-kite', control('black-kite:v13'))]
    for stage, ref in refs:
        prepare_head(root/'preservation'/stage, version, ref, stage+' assistance preservation', design)
        a = head_result(root/'preservation'/stage); b = head_result(ref)
        heads[stage] = {'candidate': a, 'control': b}
        for color in ('red', 'blue'):
            floor = 38 if stage == 'jordan' else b['colors'][color]['win']-2
            checks[stage+'_'+color] = a['colors'][color]['win'] >= floor
        if stage == 'red-kite': checks['red_kite_absolute'] = a['colors']['red']['win'] >= 24
        if stage == 'black-kite': checks['black_losses'] = a['losses'] <= b['losses']+2
        write(STUDY/'guard-progress.json', {'stage': stage, 'heads': heads, 'checks': checks})
        if not all(checks.values()): break
    if all(checks.values()):
        stage = 'field'; field_runner.STUDY = STUDY; field_runner.DESIGN = design
        field = field_runner.field(root, 'assist22')
        checks.update({'field_'+k: v for k,v in field['checks'].items()})
    result = {'stage': stage, 'heads': heads, 'field': field, 'checks': checks,
        'hosted_guards_passed': all(checks.values()), 'prior_local_failure_retained': True,
        'promotion_performed': False, 'requires_final_tradeoff_review': True,
        'plan_sha256': digest((STUDY/'guard-prospective.json').read_bytes())}
    write(STUDY/'guard-result.json', result)
    if not (STUDY/'guard-feedback').exists():
        record(STUDY/'diagnostic-feedback/policy.ir.json', STUDY/'local/candidates/assist22/policy.bas',
            f'Actual league preservation completed through {stage}: checks {checks}. '
            'Richard80/80 retained; prior local convoy regression remains. No promotion performed.',
            STUDY/'guard-result.json', STUDY/'guard-feedback')
    print('Assistance guards', stage, checks, flush=True)
