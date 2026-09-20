"""Test existing support mechanisms against g002 before more source changes."""
from economy_feedback import record
from g002_review import STUDY, H
from policy_ir import read, write, digest
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result
from release_workspace import RUN, verify
from threat_coverage_hosted import control
from win_hosted import live

DESIGN = ('User-prioritized gota-g002:v1 diagnosis. Exact pinned teams,40episodes per color, '
          'all80 completed and fully audited. Two existing locally verified sources: '
          'caster support without the anchor restriction, then reachable tank readiness. '
          'Reuse the completed deployed and anchored controls without counting them as new. '
          'Other previously failed/pending opponent gates remain unchanged. '
          'Directional fixed-lineup evidence; no automatic promotion.')


def main():
    verify(); live()
    cases = [
        ('caster_idle', RUN / 'coached-lanes/r5-caster-binding-repair', 'bound_idle'),
        ('ready12', RUN / 'coached-lanes/r5-reachable-support', 'ready12')]
    inputs = []
    for name, study, candidate in cases:
        source = study / 'local/candidates' / candidate / 'policy.bas'
        root = study / 'hosted' / candidate
        version = read(root / 'uploaded-version.json')
        metadata = read(root / 'upload-request.json')
        if metadata['content_hash'] != digest(source.read_bytes()):
            raise ValueError('Already-uploaded source differs')
        if candidate not in read(study / 'local/comparison.json')['qualified']:
            raise ValueError('Missing local qualification')
        inputs.append({'name': name, 'study': str(study), 'candidate': candidate,
                       'version': version['id'], 'source_sha256': digest(source.read_bytes())})
    freeze(STUDY / 'diagnostic-plan.json', {'cases': inputs, 'design': DESIGN,
        'control': str(control('gota-g002:v1')), 'anchor_control': str(H / 'hosted/anchor/g002'),
        'new_games': 160, 'purpose': 'Separate the g002 effect of anchoring from tank readiness; no selection or promotion from this diagnostic alone.'})
    reports = {}
    for (name, study, candidate), expected in zip(cases, inputs):
        root = STUDY / 'existing-probes' / name
        version = read(study / 'hosted' / candidate / 'uploaded-version.json')
        prepare_head(root, version, control('gota-g002:v1'), 'g002 mechanism ' + name, DESIGN)
        reports[name] = result(root)
        write(STUDY / 'diagnostic-progress.json', {'results': reports})
        src = study / 'local/comparison-feedback' / candidate
        if not (root / 'feedback').exists():
            record(src / 'policy.ir.json', src / 'policy.bas',
                f'Complete gota-g002 diagnostic: {reports[name]["colors"]}; all runtime/replay/equipment audits. '
                'Earlier failed or incomplete competitor gates remain unchanged. No promotion.',
                root / 'result.json', root / 'feedback')
        print(name, reports[name]['colors'], flush=True)
    write(STUDY / 'diagnostic-result.json', {'results': reports, 'promotion_performed': False, 'scope': DESIGN})


if __name__ == '__main__':
    main()
