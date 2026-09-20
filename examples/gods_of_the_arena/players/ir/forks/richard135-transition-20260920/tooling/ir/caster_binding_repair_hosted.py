"""Require actual, source-bound activation before hosted caster evaluation."""
import time

import counterpush_hosted as runner
from caster_binding_repair import STUDY
from policy_ir import digest, read
from ranger_guard_queue import alive


if __name__ == '__main__':
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):
            raise RuntimeError('Local evaluation stopped without a verdict')
        time.sleep(15)
    candidates = read(STUDY/'local/comparison.json')['qualified'][:2]
    proof = read(STUDY/'activation-proof.json')
    if not proof['passed']:
        raise RuntimeError('No verified full-game activation for the corrected binding')
    for name in candidates:
        source = STUDY/'local/candidates'/name/'policy.bas'
        rows = [r for r in proof['rows'] if r['name'] == name]
        if not rows or not any(sum(r['proof']['expanded_assist_decisions']) for r in rows):
            raise RuntimeError('Candidate was not exercised in full games: ' + name)
        for row in rows:
            if row['source_sha256'] != digest(source.read_bytes()):
                raise RuntimeError('Activation evidence is for different source')
            if not row['proof']['all_state_hashes_equal'] or not row['proof']['all_actions_consumed']:
                raise RuntimeError('Incomplete activation replay')
            if not all(e['class_id'] in (7, 8) and e['slot'] in (2, 3) for e in row['events']):
                raise RuntimeError('Wrong hero class activated')
    runner.STUDY = STUDY
    runner.PREFIX = 'aaron-gota-ir-caster-bound'
    runner.CHANGE = ('Source-bound red Lich7/Warlock8 support nearby allied attack intent; '
                     'preserve noncaster targeting, recall and rally, and the blue branch.')
    runner.RICHARD_RED_FLOOR = 30
    runner.RED_KITE_FLOOR = 24
    runner.DESIGN = ('Corrected caster coordination, parent pressure20. Native full-game '
        'activation on global classes7/8 required before upload. Exact Richard78,40/color '
        'requires30red/38blue, then Jordan186 requires38/color, g002, redkite27 requires24red, '
        'vanguard, black, and mixed200. Frozen historical pool for comparison; newer league '
        'versions require separate follow-up. All complete replay/runtime/equipment and '
        'command diversity checks. Reused controls are not new games. Correlated fixed-lineup '
        'evidence is directional. No automatic promotion.')
    runner.main()
