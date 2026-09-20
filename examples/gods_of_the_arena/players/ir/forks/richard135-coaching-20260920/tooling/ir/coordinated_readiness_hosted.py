"""Wait for earlier complete verdicts, then test the combined decision."""
import time
import counterpush_hosted as runner
from coordinated_readiness import STUDY
from reachable_support import STUDY as PREDECESSOR
from policy_ir import digest,read,write
from ranger_guard_queue import alive


if __name__=='__main__':
    pid=read(PREDECESSOR/'hosted-process.json')['pid']
    write(STUDY/'queue-state.json',{'stage':'waiting_for_predecessor','pid':pid,'directory':str(PREDECESSOR)})
    while alive(pid):time.sleep(15)
    prior=PREDECESSOR/'hosted-comparison.json'
    if not prior.exists():raise RuntimeError('Earlier study has no final verdict')
    v=read(prior);winner=v.get('selected') or v.get('upstream_selected')
    if winner:
        write(STUDY/'hosted-comparison.json',{'selected':None,'stage':'not_run','upstream_selected':winner,
            'predecessor':str(prior),'reason':'Prior full-suite winner; avoid unnecessary XP.','promotion_performed':False})
        raise SystemExit(0)
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('Local study stopped without verdict')
        time.sleep(15)
    names=read(STUDY/'local/comparison.json')['qualified'][:3]
    if names:
        while not (STUDY/'activation-proof.json').exists():
            if not alive(read(STUDY/'activation-process.json')['pid']):raise RuntimeError('Activation stopped without proof')
            time.sleep(15)
        proof=read(STUDY/'activation-proof.json')
        if not proof['passed']:raise RuntimeError('Missing activation')
        for name in names:
            source=STUDY/'local/candidates'/name/'policy.bas'
            rr=[r for r in proof['rows'] if r['name']==name]
            if not rr or not any(sum(r['proof']['expanded_assist_decisions']) for r in rr) or not any(r['proof']['unsupported_hold_decisions'][0] for r in rr):raise RuntimeError('Both mechanisms required')
            for r in rr:
                if r['source_sha256']!=digest(source.read_bytes()) or not r['proof']['all_state_hashes_equal'] or not r['proof']['all_actions_consumed']:raise RuntimeError('Source or replay mismatch')
    runner.STUDY=STUDY;runner.PREFIX='aaron-gota-ir-team-readiness';runner.MAX_CANDIDATES=3
    runner.CHANGE='Combine frontline initiate-or-hold readiness with context-qualified caster support; retain emergency defense, recall/rally, attacking roles and blue behavior.'
    runner.RICHARD_RED_FLOOR=30;runner.RED_KITE_FLOOR=24
    runner.DESIGN=('Combined coordinated defense, native actual DK5 wait and caster7/8 support activation '
        'required before upload. Parent corrected bound_idle22. Test components together. Richard78 '
        'forty/color requires30red/38blue, then Jordan186 requires38/color, g002, redkite27 absolute24red, '
        'vanguard, black and mixed200. Current changed league versions require separate follow-up. '
        'Full replay/runtime/equipment audits. Directional correlated fixed-lineup evidence; no automatic promotion.')
    runner.main()
