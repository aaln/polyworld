# gota_base_v0 — source-derived semantic policy

Status: source-derived explanation. The executable semantic artifact is now [base.ir.json](base.ir.json), with a versioned BASIC binding and reverse extractor. [base.generated.bas](base.generated.bas) is generated from that IR. This Markdown is explanatory prose, not the compiler input.
Source: [../base.bas](../base.bas), SHA-256 `6af2a79e0c7815b41a00e824de897b1ab2a2f3057798c6c5395778e59d734ae9`.
Domain binding: Gods of the Arena `2026.9.10.1`, source-compatible with `2026.9.9.4`; see [README.md](README.md).

## 1. Situation

The world contains heroes, footmen, towers and forts, identified by stable object IDs. Only the current visibility-filtered enumeration can supply enemy facts. Distances are squared Euclidean distances between integer map-tile observations, not path lengths.

An eligible enemy has a different team and `objectAlive(index) != 0`. For units this means living; for structures it includes exposure prerequisites. A protected structure with positive HP is standing but is not eligible. Inventory contains six slots of equipment or consumable stacks.

## 2. Belief

There is no opponent model, remembered enemy location or uncertainty estimate. `decisions` persists and increments but does not influence behavior. Target selection is recomputed every decision. An unseen enemy does not participate in that selection; the program does not assert that it is dead.

The policy also creates within-decision summaries: nearest eligible enemy and inventory presence flags. These are procedural summaries, not probabilistic beliefs.

## 3. Goal

The game awards team fort victories. This program's local preferences are proximity-based combat, consumable spending and class-dependent equipment purchasing. “Apply pressure” and “sustain combat” are interpretations of those preferences; the source does not establish an original author rationale or a global optimization objective.

It has no explicit preference for completing a lane, following footmen, retreating, focusing a teammate's target or preserving a purchase reserve.

## 4. Skill

Each skill runs once per decision and then returns. The engine retains navigation/attack orders and executes movement, basic attacks and automatic abilities between decisions.

**observe_nearest_enemy.** Scan object indices in increasing enumeration order. Among eligible enemies minimize `(objectX-selfX)^2 + (objectY-selfY)^2`. Replace the candidate only on a strictly smaller distance, preserving the first enumerated candidate on ties. Return its ID, or zero.

**attack_nearest.** When a candidate exists, call `attackTarget(candidate)`. Ignore the return value. Do not impose another range limit or remember a target commitment. The engine handles normal pursuit and attack eligibility.

**scan_inventory_and_consume.** Clear `hasHeal`, `hasMana`, `hasPoison`, `hasGear`, `emptySlot`; then visit slots 0–5. Read the current item ID for each slot. Set presence flags before attempting consumption: IDs 1/2 are healing, 3 mana, 4 poison, IDs >4 equipment, and 0 empty. For each slot independently:

- Use healing at strictly below 60% of the decision's starting HP maximum.
- Use mana potion at strictly below 40% of the decision's starting mana maximum.
- Use poison whenever the selected candidate ID is nonzero.

Ignore use return values. Do not refresh self HP/mana snapshots or revise a presence flag when a stack becomes empty. Multiple slots can be consumed in one decision. `emptySlot` reflects the scan at each slot's visit; an item consumed there does not retroactively make it empty in this summary.

**buy_consumables.** In the following order, independently attempt:

1. Below 50% HP and `hasHeal=0`: elixir (2) if starting gold ≥50, then ration (1) if starting gold ≥30. Both conditions can run.
2. Positive maximum mana, below 50% mana and `hasMana=0`: mana potion (3) if starting gold ≥45.
3. Candidate exists and `hasPoison=0`: poison (4) if starting gold ≥40.

Do not decrement the program's gold snapshot or refresh flags after purchases. The engine checks the actual balance and inventory on every attempt, so a later attempt may fail.

**buy_equipment.** Run only if `emptySlot != 0` from the earlier scan. Evaluate the following class group and attempt its purchases from left to right. All thresholds refer to starting gold. The first purchase in each class group additionally requires `hasGear=0`.

| Class IDs | Initial purchase, only without gear | Remaining ordered attempts |
| --- | --- | --- |
| Melee: 0, 4, 5, 9 | Gauntlets 7 at ≥70 | Helmet 5 at ≥80; dagger 11 at ≥110; sword 13 at ≥150; axe 18 at ≥180 |
| Ranged: 1, 6 | Boots 8 at ≥100 | Bow 14 at ≥150; crossbow 19 at ≥180 |
| Magic: 2, 3, 7, 8 | Wand 12 at ≥140 | Ring 10 at ≥120; staff 17 at ≥170; spellbook 20 at ≥190 |

After the class group, attempt buckler (6) at ≥90 and amulet (9) at ≥120. No budget refresh, no duplicate-equipment check in the program, no return-value checks. The engine rejects invalid attempts. This is an ordered attempt list, not a promised final equipment build.

**walk_to_center.** If there was no selected candidate, request `walkTo(64,64)` and ignore the return value. There is no lane or teammate selection and no explicit collision avoidance beyond engine pathfinding.

## 5. Strategy

This descriptive strategy corresponds to the ordered rules in `base.ir.json`:

```text
POLICY gota_base_v0
ON EACH HOST DECISION
  DO increment_decisions
  DO observe_nearest_enemy
  WHEN candidate_exists DO attack_nearest
  DO scan_inventory_and_consume
  DO buy_consumables
  WHEN earlier_inventory_scan_found_empty_slot DO buy_equipment
  WHEN no_candidate DO walk_to_center
  FINISH
```

The full contracts above are necessary to preserve behavior. Changing tie breaking, refreshing a budget or replacing two purchase attempts with an `else` changes this policy even if the prose summary sounds the same.

## 6. Execution

The original executable is `base.bas`; `base.generated.bas` is regenerated from the semantic IR. Both use only the four exported BASIC actions, the documented observations and bounded persistent memory. Normal attack range, pathfinding and automatic ability selection remain engine behavior; their presence is not evidence of an explicit skill in this program.

The baseline's poison use follows the engine's direct item-damage path, including its different checks from normal combat. A faithful baseline reconstruction must preserve the calls and ordering; a change to restrict poison is a separate policy revision.

## 7. Update

The BASIC program does not learn internally. The external research loop produces new artifacts and feeds episode evidence back into the belief/update layers. Source → IR → BASIC command-trace equivalence is established for this baseline, including a complete action/state tape. Each behavior change still needs named scenario expectations and complete games. Inferred rationale remains separately attributed during reverse extraction. See [README.md](README.md) for the completed experiment and its limits.
