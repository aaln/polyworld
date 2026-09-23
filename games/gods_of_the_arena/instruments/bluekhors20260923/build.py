"""Create a new source/IR pair and preserve the deployed parent."""
import json, pprint, shutil, re
from pathlib import Path
import blue_binding as b

ROOT, HERE, PARENT = b.ROOT, b.HERE, b.PARENT
STUDY = ROOT.parent / 'polyworld/tmp/gota-blue-khors-20260923'
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')

def main():
    out = STUDY / 'blue-center'
    assert not out.exists(), 'Preserve original candidate snapshots'
    p = json.loads((PARENT / 'policy.ir.json').read_text())
    ir = b.ir
    parent_digest = ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_blue_center20260923'
    p['execution']['binding'] = b.VERSION
    p['situation']['notes'] += ' Public blue team, team ordinal zero and ranged class define a central opening route. No opponent identity or hidden position is an input.'
    p['skill'] = {key: {'operator': 'bluecenter_' + key, 'parameters': value.defaults()} for key, value in specs.items()}
    p['belief']['claims'] = {
        'RouteMechanism': {'status': 'requires_review', 'claim': 'The first blue ranged hero advances toward center when no combat/recovery/defense rule preempts. All other classes, ordinals and red behavior remain unchanged.', 'evidence': [{'artifact': 'evidence/practice.json'}]},
        'InheritedMechanics': {'status': 'requires_review', 'claim': 'Current buyback, portal recovery and combat mechanisms remain valid on the exact engine.', 'evidence': [{'artifact': 'evidence/local-summary.json'}]},
        'CompetitiveGain': {'status': 'requires_review', 'claim': 'A fresh 400-game comparison improves blue individual score and closes the khors114 score gap while passing aggregate and red-preservation gates. Earlier central contact alone is not success.', 'evidence': [{'artifact': 'evidence/trial-report.json'}]}
    }
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': 'User requests blue improvement against khors114. Prior 100 blue games lose hero-kill XP despite higher creep XP; all four prospectively sampled blue openings remain level1 at one minute while khors is level2/3.'}, 'needs_review': ['belief/' + k for k in p['belief']['claims']], 'evidence': [{'artifact': 'evidence/experiment.md'}]}
    ir.refresh_grounding(p)
    source = ir.compile_policy(p)
    assert ir.extract(source, p) == p
    out.mkdir(parents=True)
    for n, v in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]: write(out/n, v)
    (out/'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out/'policy.bas').write_text(source)
    shutil.copytree(PARENT/'tooling', out/'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out/'tooling/bluekhors20260923').mkdir()
    shutil.copy2(HERE/'blue_binding.py', out/'tooling/bluekhors20260923/blue_binding.py')
    converter = (PARENT/'convert.py').read_text().replace('tooling/adaptive20260922', 'tooling/bluekhors20260923').replace('import buyback_binding\nbuyback_binding.configure()\nir = buyback_binding.ir', 'import blue_binding\nblue_binding.configure()\nir = blue_binding.ir')
    (out/'convert.py').write_text(converter)
    write(out/'manifest.json', {'source_sha256': ir.digest(source.encode()), 'ir_sha256': ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': ir.digest((PARENT/'policy.bas').read_bytes()), 'engine_commit': '1b70894436b7ffdcd0d421b6b32c2415c9c8bfde', 'game_version': '2026.9.22.3', 'hosted_complete': False, 'score_gate_passed': None})
    split = lambda s: dict(zip(re.split(r"' @rule (R_\w+)\n", s)[1::2], re.split(r"' @rule (R_\w+)\n", s)[2::2]))
    old, new = split((PARENT/'policy.bas').read_text()), split(source)
    changed = [k for k in old if old[k] != new[k]]
    assert changed == ['R_base_recovery_intent', 'R_advance'], changed
    write(STUDY/'skill-difference.json', {'changed_rules': changed, 'other_rule_bodies_identical': True})
    print((out/'manifest.json').read_text())

if __name__ == '__main__': main()
