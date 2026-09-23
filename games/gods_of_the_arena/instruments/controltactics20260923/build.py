"""Create a fresh semantic IR/policy pair through the versioned converter."""
import json
import pprint
import re
import shutil
import tactics_binding as b
RAW = b.ROOT.parent / 'polyworld/tmp/gota-control-tactics61-20260923'
COMMIT = 'e42c4822f44e04726b09bb4ffe853152c7a18207'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'control-tactics'
    assert not out.exists(), 'Preserve captured pairs'
    p = json.loads((b.PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_control_tactics20260923'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.3')
    # Retain calibrated parameters, order and predicates; only rebind implementations.
    p['skill'] = {key: {'operator':'cctactics_'+key, 'parameters':p['skill'][key]['parameters'] if key in p['skill'] else spec.defaults()} for key,spec in specs.items()}
    rules={r['skill']:r for r in p['strategy']}
    p['strategy']=[rules[k] if k in rules else {'id':'R_'+k,'when':'active','skill':k,'for':['Score','Survive']} for k in specs]
    p['situation']['notes'] += ' Release61 adds distinct stun, silence and root states. Silence is not a global inactive state; root is not a spell or item prohibition. Enemy status timers are visible-only evidence. Current host abilityDamage supplies the reduced damage thresholds.'
    p['situation']['notes'] += ' Control61tactics uses currently visible heroes, appropriate remaining-control timers and exact host cast validation. No opponent identity or private XP is used.'
    p['belief']['claims'] = {
        'ControlMechanism': {'status':'requires_review','claim':'Earlier E unlock, hero-specific control before retreat, overlap timing, and imminent healing mana preserve productive actions while enabling useful stun/silence/root impacts.','evidence':[{'artifact':'evidence/practice-comparison.json'}]},
        'CompetitiveGain': {'status':'requires_review','claim':'New executable has no inherited score qualification. Require matched current-engine responsive controls; a better control count alone cannot qualify.','evidence':[{'artifact':'evidence/native-comparison.json'}]},
    }
    p['goal']['Score']['preference'] += ' Count avoided death and hero control only through resulting XP-minus-time; preserve farming and do not assume more control cannot regress scores.'
    p['update'] = {'revision':1,'parent':parent_digest,'change':{'origin':'User requests effective stun/silence use and score preservation. Coordinated early E unlock, control target selection/timing before retreat, and generic control arbitration.','deployment_qualified':False},'needs_review':['belief/ControlMechanism','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/request.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(b.PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/controltactics20260923').mkdir()
    shutil.copy2(b.HERE / 'tactics_binding.py', out / 'tooling/controltactics20260923/tactics_binding.py')
    converter = (b.PARENT / 'convert.py').read_text().replace('crowd-control legality','crowd-control tactics').replace('tooling/control20260923','tooling/controltactics20260923').replace('import control_binding\ncontrol_binding.configure()\nir = control_binding.ir','import tactics_binding\ntactics_binding.configure()\nir = tactics_binding.ir')
    (out / 'convert.py').write_text(converter)
    for name in ['request.json']:
        write(out / 'evidence' / name, json.loads((RAW / name).read_text()))
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((b.PARENT / 'policy.bas').read_bytes()), 'engine_commit': COMMIT, 'game_version': '2026.9.23.3', 'hosted_complete': False, 'deployment_qualified': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((b.PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
