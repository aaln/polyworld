"""Replay61: suppress silenced casts without suppressing legal action channels."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0, str(HERE.parent / 'druidlane20260923'))
import druid_binding as parent

ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/control-legality-2026-09-23-r61'
BASE_FACTS = deepcopy(ir.temporal_facts('2026.9.23.3'))


def configure():
    specs = dict(parent.configure())
    facts = deepcopy(BASE_FACTS)
    facts.update(
        abilities='Replay61: every ability requires an explicit cast and learned rank. No automatic spell fallback. Basic acquisition remains automatic when not walking.',
        balance='Ranger HP growth29; Crossbowman base damage58; Chalice heal45; Gale Slash65. Rank1 BlazingBlade72, DreadTotem70, GolemSeed68, BoneMarionette53.',
        controls='Public selfStunTicks/selfSilenceTicks/selfRootTicks and visible objectStunTicks/objectSilenceTicks/objectRootTicks are remaining ticks in the frozen decision frame. Zero unseen status is not evidence about a hidden hero.',
        control_legality='Stun blocks movement, basic attacks, spells and item use. Ability leveling has separate gates. Root blocks movement but allows attacks, spells and items. Silence blocks spells but permits movement, basic attacks and items. Stun/root interrupt an active portal; silence does not.',
        control_durations='At24ticks/sec: Vanguard R stun24; Warlock E silence48; Druid R root48; Lich E root24. Fixed duration across learned ranks; hostile impact affects heroes and creeps, not structures. Timers refresh to the later expiry, not additive duration.',
    )
    ir.temporal_facts = lambda version: deepcopy(facts)
    for key, old in list(specs.items()):
        specs[key] = replace(old, meaning=old.meaning.replace('Auto-spells remain enabled.', 'All spells require explicit casts.'))
    old = specs['combat']
    marker = 'if abilityLevel(slot) > 0 and abilityCooldown(slot) = 0 then'
    assert old.template.count(marker) == 1
    specs['combat'] = replace(old, template=old.template.replace(marker, 'if selfSilenceTicks = 0 and abilityLevel(slot) > 0 and abilityCooldown(slot) = 0 then'),
        meaning=old.meaning + ' Skip only the spell channel while silenced. Attack selection and legal post-hit movement continue; rooted basic attacks and spells remain available. Reduced ability damage is read from the live host, never an obsolete hard-coded kill threshold.')
    old = specs['lane_recovery']
    marker = 'if laneSlot >= 0 then'
    assert old.template.count(marker) == 1
    specs['lane_recovery'] = replace(old, template=old.template.replace(marker, 'if laneSlot >= 0 and selfSilenceTicks = 0 then'),
        meaning=old.meaning + ' During silence, wait within the existing bounded safe recovery window without issuing a rejected heal; resume casting after expiry. Keep root-compatible healing, potion use, danger and shopping priorities unchanged.')
    host.VERSION = ir.VERSION = VERSION
    host.GAME_VERSIONS = ir.GAME_VERSIONS = ('2026.9.23.3',)
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'control61_' + key: value for key, value in specs.items()})
    return specs
