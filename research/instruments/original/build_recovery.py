"""Freeze the user's lane-sharing hypothesis as a convertible semantic pair."""
import json
import pprint
import re
import shutil
import recovery_binding as b

RAW = b.ROOT.parent / 'polyworld/tmp/gota-weak-neutral62-20260924'
COMMIT = '2c8db6ebe1dc785ce1eea87496505d1244ee4c44'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'weak-neutral'
    assert not out.exists(), 'Preserve captured inputs'
    request = {
        'user':'Fix low league scores; test that weak heroes kill neutrals for income. Skip Jev. Preserve khors180 observational analysis.',
        'engine':COMMIT,'objective':'Expected individual floor(max(0, XP - 200 * elapsed minutes)).',
        'hypothesis':'Weak heroes lose income while preferring distant units or structure pressure to nearby camps. Bounded direct neutral combat, safer tier requirements and no speculative weak-hero wave pulls may improve score.',
        'scope':'Coordinated targeting/guard/navigation changes; carry behavior preserved. Test against deployed source and prior champion with fresh responsive counterfactuals, diverse natural draft contexts. No efficacy claim from old narrow pilot.',
        'evidence':'gota-khors180-observations-20260924; current36leaguegames; heterogeneous hero draws and two unrelated failing opponents preclude naive causal rollback.',
    }
    write(RAW / 'request.json', request)
    p = json.loads((b.PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_weak_neutral20260924'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.4')
    p['skill'] = {k: {'operator': 'weakneutral_' + k, 'parameters': p['skill'][k]['parameters'] if k in p['skill'] else spec.defaults()} for k, spec in specs.items()}
    rules = {r['skill']: r for r in p['strategy']}
    p['strategy'] = [dict(rules[k], **{'for': ['Score']}) if k in rules else {'id': 'R_' + k, 'when': 'active', 'skill': k, 'for': ['Score']} for k in specs]
    p['situation']['notes'] += ' Weak neutral-farming revision: bounded direct income before distant chase; no private XP available. ' + ' Release62 adds neutral kind6/faction2, visible camp/leader/returning fields and public static camp geometry. Returning mobs are immune. Camp life/respawn knowledge remains visibility-limited. Lane XP sharing remains15percent last-hit reserve plus85percent nearby share; neutral recipients must be on the last-hitting unit team.'
    p['belief']['claims'] = {
        'WeakNeutralIncome': {'status':'requires_review','claim':'Weak heroes directly attack tier-eligible nearby neutrals instead of speculative pulls or distant target pursuit; measure neutral XP and net score together.','evidence':[{'artifact':'evidence/practice-comparison.json'}]},
        'WeakHeroScore': {'status':'requires_review','claim':'Current deployed source is the baseline; compare rollback and weak-neutral candidate on identical fresh roster/seed/slot controls. New neutral kills must translate into higher score.','evidence':[{'artifact':'evidence/statistics.json'}]},
    }
    p['goal']['Score']['preference'] = 'Maximize expected individual floor(max(0, XP - 200 * elapsed minutes)). Lane occupancy, survival, team victory and game duration have value only through this score. Compare marginal expected XP against travel/death downtime and time penalty.'
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': request['user'], 'deployment_qualified': False}, 'needs_review': ['belief/WeakNeutralIncome', 'belief/WeakHeroScore'], 'evidence': [{'artifact': 'evidence/request.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]: write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(b.PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/khors18020260924').mkdir()
    shutil.copy2(b.HERE / 'recovery_binding.py', out / 'tooling/khors18020260924/recovery_binding.py')
    converter = (b.PARENT / 'convert.py').read_text().replace('tooling/neutralfarm20260923','tooling/khors18020260924').replace('camp_binding','recovery_binding')
    (out / 'convert.py').write_text(converter)
    write(out / 'evidence/request.json', request)
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((b.PARENT / 'policy.bas').read_bytes()), 'engine_commit': COMMIT, 'game_version': '2026.9.23.4', 'hosted_complete': False, 'deployment_qualified': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((b.PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__': main()
