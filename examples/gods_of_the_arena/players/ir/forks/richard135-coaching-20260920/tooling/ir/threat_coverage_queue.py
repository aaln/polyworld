"""Serial coordinated threat probes after the already running pressure study."""
import time
from policy_ir import read, write, digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure import STUDY as PRESSURE
from threat_coverage import STUDY
from threat_coverage_hosted import prepare, run


def main():
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']): raise RuntimeError('Local coverage study stopped without verdict')
        time.sleep(15)
    choices = read(STUDY/'local/comparison.json')['qualified'].copy()
    if 'both_coverage' in choices:
        choices.remove('both_coverage'); choices.insert(0,'both_coverage')
    choices = choices[:2]
    if not choices:
        print('No coverage local qualifier; no hosted requests.',flush=True); return
    while alive(read(PRESSURE/'hosted-process.json')['pid']): time.sleep(15)
    if not (PRESSURE/'hosted-comparison.json').exists(): raise RuntimeError('Pressure study stopped without reconciled completion')
    guard = PRESSURE/'promotion-guardrail'
    if (guard/'process.json').exists():
        while alive(read(guard/'process.json')['pid']): time.sleep(15)
        if not (guard/'result.json').exists() and not (guard/'not-run.json').exists():
            raise RuntimeError('Pressure field guardrail stopped without reconciled result')
    g002 = PRESSURE/'g002-guardrail'
    if (g002/'process.json').exists():
        while alive(read(g002/'process.json')['pid']): time.sleep(15)
        if not (g002/'result.json').exists() and not (g002/'not-run.json').exists():
            raise RuntimeError('Pressure gota-g002 guardrail stopped without reconciled result')
    from core_pressure import STUDY as CORE
    if (CORE/'hosted-process.json').exists():
        while alive(read(CORE/'hosted-process.json')['pid']): time.sleep(15)
        if not (CORE/'hosted-comparison.json').exists():
            raise RuntimeError('Core pressure queue stopped without reconciled result')
    freeze(STUDY/'hosted-selection.json',{'choices':choices,
        'local_sha256':digest((STUDY/'local/comparison.json').read_bytes()),
        'plan_sha256':digest((STUDY/'hosted-prospective-plan.json').read_bytes()),
        'rule':'Stop after first candidate passes targeted and preservation gates; second only if first fails a pre-broad gate. No automatic deployment.'})
    prepare(choices[0])
    with drained_wide(STUDY):
        reports = {}; selected = None
        for name in choices:
            write(STUDY/'queue-state.json',{'stage':'hosted_coverage','candidate':name})
            r = run(name); row = {'targeted_passed':r['passed'],'checks':r['checks'],'gains':r['gains']}
            p = STUDY/'hosted'/name/'preservation-result.json'
            if p.exists(): row['preservation_passed'] = read(p)['passed']
            reports[name] = row
            if r['passed'] and row.get('preservation_passed'):
                selected = name; break
        write(STUDY/'hosted-comparison.json',{'selected':selected,'results':reports,
            'scope':'Targeted actual league threat/mixed response and preservation only. Broad field remains necessary.'})


if __name__ == '__main__': main()
