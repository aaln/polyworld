"""Serialize with the diagnostic; preserve local and hosted qualification gates."""
import time
import counterpush_hosted as runner
from caster_assist import STUDY
from ally_assist import STUDY as DIAGNOSTIC
from policy_ir import read, write
from ranger_guard_queue import alive

if __name__ == '__main__':
    pid = read(DIAGNOSTIC/'guard-process.json')['pid']
    write(STUDY/'queue-state.json', {'stage': 'waiting_for_existing_guard', 'pid': pid})
    while alive(pid): time.sleep(15)
    if not (DIAGNOSTIC/'guard-result.json').exists():
        raise RuntimeError('Existing guard stopped without complete results; reconcile first')
    runner.STUDY = STUDY
    runner.PREFIX = 'aaron-gota-ir-caster-assist'
    runner.CHANGE = 'Healthy Lich/Warlock support public allied attack intent; preserve noncaster behavior, recall and rally; exact blue branch.'
    runner.RICHARD_RED_FLOOR = 30
    runner.RED_KITE_FLOOR = 24
    runner.DESIGN = ('Caster-only coordinated defense, parent pressure20. Paired40/color '
        'versus exactRichard78 requires30red/38blue, then Jordan/g002/redkite24red/vanguard/black '
        'and mixed200. Full runtime/replay/equipment/command diversity checks. Reused controls '
        'are not new games; fixed-lineup correlated evidence is directional. No automatic promotion.')
    runner.main()
