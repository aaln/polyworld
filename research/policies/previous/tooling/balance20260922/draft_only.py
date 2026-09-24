"""Follow-up discriminator: Crossbowman draft without spatial-controller changes."""
from dataclasses import replace
import json
import pprint
import build

BINDING = 'gota-bassy/balance-draft-2026-09-22-r1'


def configure():
    build.configure_control()
    specs = build.practiced.specs('potions')
    draft = specs['draft']
    draft = replace(draft, template=draft.template.replace('        p = 0',
        '        if c = Crossbowman then\n          score = score + 300\n        end if\n        p = 0'),
        meaning='Prefer available Crossbowman after the damage buff; retain the exact public ranged-first fallback and every post-draft controller rule.')
    assert 'if c = Crossbowman then\n          score = score + 300' in draft.template
    specs['draft'] = draft
    build.binding.VERSION = build.ir.VERSION = BINDING
    build.binding.CONTRACTS.clear()
    build.binding.CONTRACTS.update({'draftonly_' + name: spec for name, spec in specs.items()})
    return specs


def main():
    p = json.loads((build.PARENT / 'policy.ir.json').read_text())
    parent = build.ir.digest(p)
    specs = configure()
    p['id'] = 'gota_balance20260922_crossbow_draft'
    p['execution'].update(binding=BINDING, game_version=build.VERSION)
    p['skill'] = {name: {'operator': 'draftonly_' + name, 'parameters': spec.defaults()} for name, spec in specs.items()}
    p['strategy'] = [{'id': 'R_' + name, 'when': 'always' if name in ('draft', 'timing', 'lifecycle') else 'active',
                     'skill': name, 'for': ['Grow', 'Survive', 'Score', 'Practice']} for name in specs]
    p['belief']['claims'] = {'DraftIsolation': {'claim': 'Prioritizing Crossbowman alone improves patched-engine score while preserving the productive blue movement behavior of the deployed controller.', 'status': 'untested', 'evidence': []}}
    p['situation']['notes'] = 'Current shared-frame host; public draft availability only. Keep original global-coordinate controller as a tested component. The preceding mirrored alternatives regressed on blue; hero strength and geometry must not be conflated.'
    p['update'] = {'revision': 1, 'parent': parent,
        'change': {'origin': 'Follow-up discriminator after mirrored Ranger and Crossbowman fail blue score preservation; isolate Crossbowman draft priority'},
        'needs_review': ['belief/DraftIsolation'], 'evidence': [{'artifact': 'games/gods_of_the_arena/experiments/2026-09-22-crossbow-draft-isolation.md'}]}
    build.ir.refresh_grounding(p)
    source = build.ir.compile_policy(p)
    assert build.ir.extract(source, p) == p
    # Prove that every non-draft contract is the unchanged deployed controller.
    old = build.practiced.specs('potions')
    assert all(specs[k] == old[k] for k in old if k != 'draft')
    out = build.STUDY / 'candidates/crossbow_draft'
    assert not out.exists()
    out.mkdir(parents=True)
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', build.ir.grounded(p))]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    (out / 'manifest.json').write_text(json.dumps({'source_sha256': build.ir.digest(source.encode()),
        'ir_sha256': build.ir.digest(p), 'binding': BINDING, 'game_version': build.VERSION,
        'engine_commit': build.COMMIT, 'exact_roundtrip': True, 'postdraft_contracts_unchanged': True,
        'validation': 'untested'}, indent=2) + '\n')
    print(build.ir.digest(source.encode()))


if __name__ == '__main__':
    main()
