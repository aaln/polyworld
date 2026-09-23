"""Freeze a new IR-first pair, retaining all captured parent inputs."""
import json
import pprint
import re
import shutil
import weak_binding as b

ROOT, HERE, PARENT = b.ROOT, b.HERE, b.PARENT
RAW = ROOT.parent / 'polyworld/tmp/gota-weakhero60-20260923'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'explicit-sustain'
    assert not out.exists(), 'Preserve frozen pairs'
    p = json.loads((PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_explicit_sustain20260923'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.2')
    old = {r['skill']: r for r in p['strategy']}
    p['skill'] = {k: {'operator': 'weak_' + k, 'parameters': v.defaults()} for k, v in specs.items()}
    p['strategy'] = [old[k] if k in old else {'id': 'R_' + k, 'when': 'active_resource_hero', 'skill': k, 'for': ['Score', 'survive_and_replenish']} for k in specs]
    next(r for r in p['strategy'] if r['skill'] == 'lane_recovery')['when'] = 'active_lane_healer'
    next(r for r in p['strategy'] if r['skill'] == 'melee_spacing')['when'] = 'active_melee'
    p['goal']['survive_and_replenish']['preference'] = 'Explicit useful self recovery before unnecessary home travel; retain dangerous escapes, useful shopping, portal channels and bounded safe recovery. Improve low-scoring melee income without sacrificing carry performance.'
    p['situation']['notes'] += ' Release60 removes automatic spells. Missing HP/mana, learned ability rank, cooldown, charge, public threats and shopping opportunities jointly determine recovery. Resource spells unlock from level2 after the normal level1 primary. Nearby hero pressure and local relative level-power trigger short melee disengagements instead of long chases or unconditional home trips.'
    p['belief']['claims'] = {
        'HistoricalWeakHeroes': {'status': 'supported', 'claim': 'Earlier replay59 cohort had100carry appearances averaging3311.42 versus100melee averaging118.23. This identifies a research priority, not current-release performance or a causal class comparison.', 'evidence': [{'artifact': 'evidence/prior-evidence.json'}]},
        'ExplicitSustainMechanism': {'status': 'requires_review', 'claim': 'Unlock and cast useful healing/restoration before target-dependent stop paths; recover safely in lane with bounded holds while retaining danger/shop/channel priorities.', 'evidence': [{'artifact': 'evidence/practice.json'}]},
        'CompetitiveGain': {'status': 'requires_review', 'claim': 'Requires fresh replay60 baseline/candidate comparison on both colors and draft contexts. Earlier auto-casting results cannot qualify this source.', 'evidence': [{'artifact': 'evidence/trial-report.json'}]},
    }
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': 'User requests improved low-scoring heroes; explicit60 contract audit exposes no-target healing and omitted restoration. Coordinated early unlock, explicit sustain and bounded melee recovery.'}, 'needs_review': ['belief/ExplicitSustainMechanism', 'belief/CompetitiveGain'], 'evidence': [{'artifact': 'evidence/request.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/weakhero20260923').mkdir()
    shutil.copy2(HERE / 'weak_binding.py', out / 'tooling/weakhero20260923/weak_binding.py')
    converter = (PARENT / 'convert.py').read_text().replace('tooling/druidlane20260923', 'tooling/weakhero20260923').replace('import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir', 'import weak_binding\nweak_binding.configure()\nir = weak_binding.ir')
    (out / 'convert.py').write_text(converter)
    write(out / 'evidence/request.json', json.loads((RAW / 'request.json').read_text()))
    write(out / 'evidence/prior-evidence.json', {'reports': ['docs/opponents/relh-v169/source-audit-20260923/README.md', 'games/gods_of_the_arena/release-audits/2026-09-23-explicit-abilities/README.md']})
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((PARENT / 'policy.bas').read_bytes()), 'engine_commit': 'fd315c8fa30f8923c7a7709a577c40ac071b1c2a', 'game_version': '2026.9.23.2', 'hosted_complete': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
