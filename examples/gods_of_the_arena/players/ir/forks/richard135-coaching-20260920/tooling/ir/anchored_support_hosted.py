"""Qualified support signals: serial complete cohorts, no automatic promotion."""
import time
import counterpush_hosted as runner
from anchored_support import STUDY
from bounded_caster_support import STUDY as PREDECESSOR
from policy_ir import digest, read, write
from ranger_guard_queue import alive


if __name__ == '__main__':
    pid=read(PREDECESSOR/'hosted-process.json')['pid']
    write(STUDY/'queue-state.json',{'stage':'waiting_for_predecessor','pid':pid,'directory':str(PREDECESSOR)})
    while alive(pid): time.sleep(15)
    prior=PREDECESSOR/'hosted-comparison.json'
    if not prior.exists(): raise RuntimeError('Predecessor stopped without verdict')
    verdict=read(prior); winner=verdict.get('selected') or verdict.get('upstream_selected')
    if winner:
        write(STUDY/'hosted-comparison.json',{'selected':None,'stage':'not_run','reason':'Predecessor passed full suite; avoid unnecessary XP.',
            'predecessor':str(prior),'upstream_selected':winner,'promotion_performed':False})
        raise SystemExit(0)
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']): raise RuntimeError('Local evaluation stopped without verdict')
        time.sleep(15)
    candidates=read(STUDY/'local/comparison.json')['qualified'][:3]
    if candidates:
        while not (STUDY/'activation-proof.json').exists():
            state=STUDY/'activation-process.json'
            if state.exists() and not alive(read(state)['pid']): raise RuntimeError('Activation job stopped without verdict')
            time.sleep(15)
        proof=read(STUDY/'activation-proof.json')
        if not proof['passed']: raise RuntimeError('No verified activation')
        for name in candidates:
            source=STUDY/'local/candidates'/name/'policy.bas'
            rows=[r for r in proof['rows'] if r['name']==name]
            if not rows or not any(sum(r['proof']['expanded_assist_decisions']) for r in rows): raise RuntimeError('Candidate never activated: '+name)
            for row in rows:
                if row['source_sha256']!=digest(source.read_bytes()): raise RuntimeError('Source differs from activation proof')
                if not row['proof']['all_state_hashes_equal'] or not row['proof']['all_actions_consumed']: raise RuntimeError('Incomplete replay')
                if not all(e['class_id'] in (7,8) and e['slot'] in (2,3) for e in row['events']): raise RuntimeError('Wrong role activated')
    runner.STUDY=STUDY; runner.PREFIX='aaron-gota-ir-coordinated-support'; runner.MAX_CANDIDATES=3
    runner.CHANGE='Qualify idle red caster support by standing friendly defense anchor and/or actual DeathKnight attack commitment; preserve recall, rally, existing targets and blue behavior.'
    runner.RICHARD_RED_FLOOR=30; runner.RED_KITE_FLOOR=24
    runner.DESIGN=('Context-qualified red Lich7/Warlock8 coordination, parent corrected bound_idle22. '
        'Three independent anchor/frontline/both variants. Native source-bound full-game activation '
        'required before upload. Richard78 forty/color requires30red/38blue, Jordan186 requires38/color, '
        'g002, redkite27 requires24red, vanguard, black, then mixed200. Frozen comparison pool; new '
        'versions need follow-up. Full runtime/equipment/replay audits. Reused controls are not new '
        'games. Correlated fixed-lineup evidence is directional. Stop first full-suite winner. No automatic promotion.')
    runner.main()
