# Actual-engine micropractice

These controlled drills run policy VMs against the exact published engine,
2026.9.21.5 / f776d5e. Both colors are tested. Cadence uses stationary targets
and normalized HP/mana; contested last hits use stationary opposing creeps
with an allied creep and varied initial swing phase. These are mechanical
experiments, not estimates of league win probability.

## Attack recovery

The baseline issues walk and attack in one decision. The new skill waits one
physics tick before reacquiring, allowing the engine to clear the old swing.
It acts only after an observed hit, and respects death, retreat, root, stun
and portal channels. All rows use 360 ticks; both colors have identical counts.

| Hero | Baseline hits | Practiced hits | Baseline interval | Practiced interval |
|---|---:|---:|---:|---:|
| Vanguard Knight | 15 | 32 | [24] | [11] |
| Ranger | 20 | 39 | [18] | [9] |
| Arcanist | 12 | 25 | [30] | [14] |
| Druid Warden | 14 | 29 | [26] | [12] |
| Demon Hunter | 22 | 44 | [16] | [8] |
| Death Knight | 13 | 27 | [28] | [13] |
| Crossbowman | 10 | 20 | [36] | [17] |
| Lich | 11 | 23 | [32] | [15] |
| Warlock | 13 | 27 | [28] | [13] |
| Berserker | 18 | 35 | [20] | [10] |

## Last hits and XP

In each 24-creep contested drill, last-hit gold rises **210 to 240** (14 to
16 kills), but shared XP falls **300 to 285**. Faster attack cycling is useful;
it does not alone maximize time in XP range. All trials run the same duration.
This regression is retained in the results.

A Crossbowman can attack from 6.5 tiles, beyond the six-tile same-floor XP
radius. In the 6.25-tile boundary drill, both policies earn 15 gold, but the
baseline earns zero XP. The new proximity rule steps inward before stale
navigation throttles can defer it, earning all 15 XP. This fixture does not
establish behavior across different terrain floors.

## Equipment and portals

At 1000 shop gold, Ranger's baseline inventory is dagger, potion, armor, axe,
boots and portal: damage 47, HP 320, 320 unspent gold. The selected variant
replaces boots with a crossbow: damage 61, HP 320, 240 unspent gold. The rejected
five-gear alternative reaches 71 damage and 120 unspent gold, but sacrifices
the potion slot and was less consistent on the native XP screen. The engine
has no sell or equipment-upgrade action. Purchase priority and slots matter.

Both colors complete emergency-home portal channels when a visible hero
threatens the keep, while safe-base controls do not portal. The threat is
removed afterward and the policy issues offensive movement again. Existing
runtime fixtures also check that channels/cooldowns are respected. Real matches
can still interrupt a channel after a new threat arrives.

Retrospective typed-event samples in `events-review.json` verify actual purchases,
creep versus hero XP, and portal completion. Some low-income heroes still buy
consumables before they can afford armor; reserving permanent-equipment gold is
a candidate for a future separately frozen experiment, not a tested cure here.

## Validation and limitations

The selected source b82c3799 passes 126 host/runtime checks, uses at most 13,428
instructions and 20,377 work in the dense fixtures, and wins four native matches
against the responsive parent. Repeated trajectories limit those four matches.
The independent hosted target panel is reported separately in `review.json`.
All initial candidate sources, failed instrument logs and the prior binding
remain preserved. Practice findings are reflected in the final semantic IR;
no old policy or coaching capture is overwritten.
