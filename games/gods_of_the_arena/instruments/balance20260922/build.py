"""Symmetry-aware semantic binding and explicit hero-preference experiments."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import json
import pprint
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUDY = ROOT.parent / 'polyworld/tmp/gota-balance-20260922'
ENGINE = ROOT.parent / 'polyworld-gota-engine-20260922'
VERSION = '2026.9.22.2'
COMMIT = 'ffcedcd866c4d31924361ed4baff2b7a6d3aba67'
BINDING = 'gota-bassy/balance-2026-09-22-r1'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/current20260922'
sys.path.insert(0, str(HERE.parent / 'targets20260922'))
import practiced
ir, binding = practiced.ir, practiced.binding


def orient(template):
    """All rounding/offset choices occur in the red-oriented team frame."""
    template = re.sub(r'\bselfX\b', 'myX', template)
    template = re.sub(r'\bselfY\b', 'myY', template)
    for name, origin in [('objectX', 'originX'), ('objectY', 'originY')]:
        template = re.sub(r'\b' + name + r'\(([^()]*)\)',
                          lambda m: '(' + origin + ' + facingSign * ' + m[0] + ')', template)
    lines = []
    for line in template.splitlines():
        for name, first in [('walkTo', 0), ('attackMove', 0), ('useItemAt', 1)]:
            start = line.find(name + '(')
            if start < 0:
                continue
            opening = start + len(name)
            depth, args, begin, end = 1, [], opening + 1, opening + 1
            while depth:
                char = line[end]
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if (char == ',' and depth == 1) or depth == 0:
                    args.append(line[begin:end].strip())
                    begin = end + 1
                end += 1
            assert len(args) == first + 2, line
            for index, origin in [(first, 'originX'), (first + 1, 'originY')]:
                args[index] = origin + ' + facingSign * (' + args[index] + ')'
            line = line[:opening+1] + ', '.join(args) + line[end-1:]
        lines.append(line)
    return '\n'.join(lines)


def configure():
    specs = practiced.configure('potions')
    old_facts = ir.temporal_facts('2026.9.21.5')
    old_facts.update(
        queries='One frozen public object and warning frame per decision phase; own command results, inventory and ability costs update immediately.',
        coordinates='Global integer observed cells use complementary red/blue tile boundaries. Policy converts into team coordinates before rounding, then reverses action coordinates.',
        phases='Shared starting actor state, simultaneous movement, collected damage then deaths/rewards; mutual kills and fort draws are legal.',
        rewards='Creep XP within six tiles on same floor. Seed/tick/team-relative geometry and spawn determine simultaneous last hitter; no absolute ID advantage.',
        scores='Integer max(0, lifetime_xp * 1440 - 200 * world_ticks) div 1440; win outcome separate.',
        balance='Ranger HP/level 19; Crossbowman base damage 69; Warlock Dread Totem base damage 87; no faction draft bonuses.')
    ir.temporal_facts = lambda version: deepcopy(old_facts)
    binding.VERSION = ir.VERSION = BINDING
    binding.GAME_VERSIONS = ir.GAME_VERSIONS = (VERSION,)
    frame = binding.contract('''
facingSign = 1
originX = 0
originY = 0
if selfTeam = 1 then
  facingSign = -1
  originX = mapWidth - 1
  originY = mapHeight - 1
end if
myX = originX + facingSign * selfX
myY = originY + facingSign * selfY
''', {}, (), (), (), 'Reflect all public coordinates into the same team frame before integer division and movement offsets.')
    specs = {'frame': frame, **{k: replace(v, template=orient(v.template),
        meaning=v.meaning + ' Spatial reasoning uses team coordinates.') for k, v in specs.items()}}
    draft = specs['draft']
    draft = replace(draft, template=draft.template.replace('        p = 0',
        '        if c = param_preferred_hero then\n          score = score + 300\n        end if\n        p = 0'),
        parameters={**draft.parameters, 'preferred_hero': (1, 0, 9)},
        meaning='Immediately choose the experimental preferred hero if available; otherwise use ranged-first public role-aware fallback. This preference is a hypothesis, not a hero tier claim.')
    assert 'param_preferred_hero' in draft.template
    specs['draft'] = draft
    binding.CONTRACTS.clear()
    binding.CONTRACTS.update({'balance_' + k: v for k, v in specs.items()})
    return specs


def build(name, hero):
    p = json.loads((PARENT / 'policy.ir.json').read_text())
    parent = ir.digest(p)
    specs = configure()
    p['id'] = 'gota_balance20260922_' + name
    p['skill'] = {k: {'operator': 'balance_' + k, 'parameters': v.defaults()} for k, v in specs.items()}
    p['skill']['draft']['parameters']['preferred_hero'] = hero
    p['strategy'] = [{'id': 'R_' + k, 'when': 'always' if k in ('frame', 'draft', 'timing', 'lifecycle') else 'active',
        'skill': k, 'for': ['Grow', 'Survive', 'Score', 'Practice']} for k in specs]
    p['execution'].update(binding=BINDING, game_version=VERSION)
    p['belief']['claims'] = {'PatchedHeroChoice': {'claim': 'Team-relative mechanics and the preferred hero improve XP score under the symmetry and hero balance patch.', 'status': 'untested', 'evidence': []}}
    p['situation']['notes'] = 'Public current observations only. Match-side reflection precedes rounding and spatial tie-breaks. The hero preference is experimental; old Ranger results are historical. Opponent version IDs are evaluator metadata only.'
    p['update'] = {'revision': 1, 'parent': parent, 'change': {'origin': 'User requested symmetry audit and tests of Crossbowman/Warlock after Ranger HP nerf', 'engine': COMMIT},
        'needs_review': ['belief/PatchedHeroChoice'], 'evidence': [{'artifact': 'games/gods_of_the_arena/experiments/2026-09-22-balance-heroes.md'}]}
    ir.refresh_grounding(p)
    source = ir.compile_policy(p)
    assert ir.extract(source, p) == p
    out = STUDY / 'candidates' / name
    assert not out.exists(), 'Preserve captured inputs'
    out.mkdir(parents=True)
    for filename, obj in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
        (out / filename).write_text(json.dumps(obj, indent=2) + '\n')
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    (out / 'manifest.json').write_text(json.dumps({'game_version': VERSION, 'engine_commit': COMMIT,
        'source_sha256': ir.digest(source.encode()), 'ir_sha256': ir.digest(p), 'binding': BINDING, 'preferred_hero': hero,
        'exact_roundtrip': True, 'validation': 'unvalidated'}, indent=2) + '\n')
    print(name, ir.digest(source.encode()))


def configure_control():
    """Port contract facts while retaining every byte of the deployed control."""
    configure()
    facts = ir.temporal_facts(VERSION)
    practiced.configure('potions')
    binding.GAME_VERSIONS = ir.GAME_VERSIONS = (VERSION,)
    facts['coordinates'] = ('This retained control reasons in global observed tiles. It remains legal on the patched host, '
                            'but lane rounding and quarter-tile offsets are not rotation equivariant. Mirroring is a separately evaluated intervention.')
    ir.temporal_facts = lambda version: deepcopy(facts)


if __name__ == '__main__':
    for name, hero in [('ranger', 1), ('crossbow', 6), ('warlock', 8), ('arcanist', 2)]:
        build(name, hero)
