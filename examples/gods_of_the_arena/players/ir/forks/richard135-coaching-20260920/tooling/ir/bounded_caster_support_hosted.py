"""Require actual, source-bound activation before hosted caster evaluation."""
import time

import counterpush_hosted as runner
from bounded_caster_support import STUDY
from supported_defense import STUDY as PREDECESSOR
from policy_ir import digest, read, write
from ranger_guard_queue import alive


if __name__ == '__main__':
    pid=read(PREDECESSOR/'hosted-process.json')['pid']
    write(STUDY/'queue-state.json',{'stage':'waiting_for_predecessor','pid':pid,'directory':str(PREDECESSOR)})
    while alive(pid):time.sleep(15)
    prior=PREDECESSOR/'hosted-comparison.json'
    if not prior.exists():raise RuntimeError('Predecessor stopped without verdict')
    verdict=read(prior)
    winner=verdict.get('selected') or verdict.get('upstream_selected')
    if winner:
        write(STUDY/'hosted-comparison.json',{'selected':None,'stage':'not_run','reason':'Predecessor passed full suite; avoid unnecessary XP.','predecessor':str(prior),'upstream_selected':winner,'promotion_performed':False})
        raise SystemExit(0)
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
    runner.PREFIX = 'aaron-gota-ir-caster-reach'
    runner.CHANGE = ('Bound red Lich7/Warlock8 support to16/18tiles, preserve existing caster targets; '
                     'preserve noncaster targeting, recall and rally, and the blue branch.')
    runner.RICHARD_RED_FLOOR = 30
    runner.RED_KITE_FLOOR = 24
    runner.DESIGN = ('Shorter caster support, parent corrected bound_idle22. Native full-game '
        'activation on global classes7/8 required before upload. No waiting rule in these candidates. Exact Richard78,40/color '
        'requires30red/38blue, then Jordan186 requires38/color, g002, redkite27 requires24red, '
        'vanguard, black, and mixed200. Frozen historical pool for comparison; newer league '
        'versions require separate follow-up. All complete replay/runtime/equipment and '
        'command diversity checks. Reused controls are not new games. Correlated fixed-lineup '
        'evidence is directional. No automatic promotion.')
    runner.main()
