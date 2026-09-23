"""Create a fresh semantic IR/policy pair through the versioned converter."""
import json
import pprint
import re
import shutil
import control_binding as b
from check import RAW, COMMIT


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'control-legality'
    assert not out.exists(), 'Preserve captured pairs'
    p = json.loads((b.PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_control_legality20260923'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.3')
    # Retain calibrated parameters, order and predicates; only rebind implementations.
    for key, skill in p['skill'].items():
        assert key in specs
        skill['operator'] = 'control61_' + key
    p['situation']['notes'] += ' Release61 adds distinct stun, silence and root states. Silence is not a global inactive state; root is not a spell or item prohibition. Enemy status timers are visible-only evidence. Current host abilityDamage supplies the reduced damage thresholds.'
    p['belief']['claims'] = {
        'ControlContract': {'status': 'supported', 'claim': 'Exact published61 source and upstream actual-tick tests distinguish legal actions and interruptions for stun, silence and root.', 'evidence': [{'artifact': 'evidence/checks.json'}]},
        'SilenceLegality': {'status': 'requires_review', 'claim': 'Combat and Druid recovery skip silenced casts while retaining legal channels and resuming after expiry; test both colors and every class.', 'evidence': [{'artifact': 'evidence/practice-comparison.json'}]},
        'CompetitiveGain': {'status': 'requires_review', 'claim': 'No score gain established. Removing rejected casts may only save VM work. Local runtime equivalence does not qualify league deployment; any hosted test requires <=100 variations and paired responsive counterfactuals on this exact release.', 'evidence': []},
    }
    p['goal']['Survive']['preference'] += ' Exploit legal defensive actions during root or silence; preserve productive basic attacks and item recovery.'
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': 'Creator crowd-control patch; refresh stale auto-casting/balance facts and silence guards in two coordinated skills.', 'deployment_qualified': False}, 'needs_review': ['belief/SilenceLegality', 'belief/CompetitiveGain'], 'evidence': [{'artifact': 'evidence/release.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(b.PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/control20260923').mkdir()
    shutil.copy2(b.HERE / 'control_binding.py', out / 'tooling/control20260923/control_binding.py')
    converter = (b.PARENT / 'convert.py').read_text().replace('draft-only current-game', 'crowd-control legality').replace('tooling/druidlane20260923', 'tooling/control20260923').replace('import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir', 'import control_binding\ncontrol_binding.configure()\nir = control_binding.ir')
    (out / 'convert.py').write_text(converter)
    for name in ['release.json', 'checks.json']:
        write(out / 'evidence' / name, json.loads((RAW / name).read_text()))
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((b.PARENT / 'policy.bas').read_bytes()), 'engine_commit': COMMIT, 'game_version': '2026.9.23.3', 'hosted_complete': False, 'deployment_qualified': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((b.PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
