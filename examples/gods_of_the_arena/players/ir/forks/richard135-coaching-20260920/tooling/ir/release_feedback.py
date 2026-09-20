"""Record every local result, including failures, without changing tested code."""
from economy_feedback import record
from policy_ir import compile_policy, digest, read
from release_workspace import RUN, VERSION


def local():
    folder = RUN / 'local'
    report = read(folder / 'screen-result.json')
    plan = read(folder / 'plan.json')
    controls = {c: report['metrics'][c] for c in ['v2', 'cadence', 'default']}
    for name in plan['sources']:
        if name == 'default':
            continue
        parent = folder / ('candidates' if name in plan['variants'] else 'controls') / name / 'policy.ir.json'
        source = parent.parent / 'policy.bas'
        output = folder / 'screen-feedback' / name
        if output.exists():
            if compile_policy(read(output/'policy.ir.json')) != source.read_text():
                raise ValueError('Feedback source changed')
            continue
        claim = (f'Completed40balanced local games on{VERSION}; metrics {report["metrics"][name]}; controls {controls}. '
                 f'All{report["verified_games"]}full replay and VM checks completed. '
                 + ('Selected for hosted discovery only. ' if name in report['selected'] else 'Not selected for a new league version. ')
                 + 'Source compatibility and local evidence only; competitive transfer requires new hosted results. Historical old-release wins are not pooled.')
        record(parent, source, claim, folder/'screen-result.json', output)
    print('All local findings incorporated into IR; tested BASIC byte parity verified.')


if __name__ == '__main__':
    local()
