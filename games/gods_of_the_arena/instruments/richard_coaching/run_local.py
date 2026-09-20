"""Execute every frozen combined-policy/control local case with full audits."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
from prepare import ROOT, STUDY, read, write, digest


def main():
    plan=read(STUDY/'plan.json')
    assert read(STUDY/'vm-proof.json')['passed']
    for path,expected in plan['inputs_sha256'].items():
        assert digest(Path(path).read_bytes())==expected,path
    # Reuse the existing complete native outcome/runtime/replay auditor. Its
    # `prepare` import resolves to this study, without editing that instrument.
    spec=importlib.util.spec_from_file_location('coached_native_runner',
        ROOT/'games/gods_of_the_arena/instruments/support_repairs/run_local.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    assert runner.STUDY==STUDY
    write(STUDY/'local-runtime-provenance.json',{'started_at':datetime.now(timezone.utc).isoformat(),
        'episode_sha256':digest((runner.BIN/'episode').read_bytes()),
        'auditor_sha256':digest((runner.BIN/'audit-hosted').read_bytes()),
        'runner_sha256':digest(Path(spec.origin).read_bytes())})
    items=[(name,case,plan) for case in plan['cases'] for name in plan['sources']]
    with ThreadPoolExecutor(2) as pool:
        rows=list(pool.map(runner.run,items))
    write(STUDY/'local-results.json',{'rows':rows,'complete':len(rows)==len(items),
                                     'scope':plan['scope']})


if __name__=='__main__':main()
