"""Richard-specific diagnostic; retains the failed local promotion gate."""
from ally_assist import STUDY
from policy_ir import read, write, digest
from economy_feedback import record
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result as head_result
from threat_coverage_hosted import control
from rush_hosted import upload
from win_hosted import live


if __name__ == '__main__':
    local = read(STUDY/'local/comparison.json')
    assert local['qualified'] == []
    name = 'assist22'
    assert read(STUDY/'vm-stress.json')['passed']
    design = ('Diagnostic only: assist22 local56/60 vs deployedG54/60 and pressure20parent58/60; '
        'two extra convoy losses failed local promotion qualification. Choose the lower-death '
        'assistance variant to test the coached Richard78 matchup directly, without erasing '
        'that failure or promoting. Forty episodes/color, exact pinned rosters and current '
        'game, complete full replay/runtime/equipment/diversity audits. Require30red/38blue '
        'only as a matchup signal. Repeated trajectories are correlated directional evidence.')
    freeze(STUDY/'diagnostic-prospective.json', {
        'design': design, 'variant': name, 'episodes': 80, 'promotion_eligible': False,
        'failed_local_gate_sha256': digest((STUDY/'local/comparison.json').read_bytes()),
        'candidate_sha256': digest((STUDY/'local/candidates'/name/'policy.bas').read_bytes())})
    live()
    root, version = upload(name, STUDY, 'aaron-gota-ir-ally-assist',
        'Support public allied attack intent within existing defense; no recall/rally change.',
        feedback_override=STUDY/'local/comparison-feedback'/name,
        validation_note='Local56/60 versus deployed54, parent58; two convoy regressions FAILED promotion gate. Richard diagnostic only; inert.')
    ref = control('richard-gods-of-the-arena:v78')
    prepare_head(root/'diagnostic-richard', version, ref, 'Richard78 assistance diagnostic', design)
    a = head_result(root/'diagnostic-richard'); b = head_result(ref)
    result = {'candidate': a, 'control': b, 'signal': {
        'red30': a['colors']['red']['win'] >= 30, 'blue38': a['colors']['blue']['win'] >= 38},
        'promotion_eligible': False, 'failed_local_gate_retained': True,
        'new_games': 80, 'reused_control_games': 80, 'design': design}
    write(STUDY/'diagnostic-result.json', result)
    if not (STUDY/'diagnostic-feedback').exists():
        record(STUDY/'local/comparison-feedback'/name/'policy.ir.json', STUDY/'local/candidates'/name/'policy.bas',
            f'Actual Richard78 diagnostic: {a["colors"]}, deployedG {b["colors"]}. '
            'Prior local convoy regression remains failed; this test does not authorize promotion.',
            STUDY/'diagnostic-result.json', STUDY/'diagnostic-feedback')
    print('Richard assistance diagnostic', a['colors'], result['signal'], flush=True)
