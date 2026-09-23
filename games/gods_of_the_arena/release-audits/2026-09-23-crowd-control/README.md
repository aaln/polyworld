# Crowd control: verified mechanics and policy adaptation

The new patch is live as **2026.9.23.3 / replay61**, engine
[`e42c482`](https://github.com/Metta-AI/polyworld/commit/e42c4822f44e04726b09bb4ffe853152c7a18207).
The score remains `floor(max(0, lifetime XP - 200 * elapsed minutes))`.
Our tested compatibility fork removes illegal casts during silence, but **does
not establish a score improvement**. Both deployed champions remain `29f6d7e6`.

| Ability | Rank1 damage before → now | Control | Duration at every learned rank |
| --- | ---: | --- | ---: |
| Vanguard R, Blazing Blade | 90 → 72 | Stun | 24ticks / 1second |
| Warlock E, Dread Totem | 87 → 70 | Silence | 48ticks / 2seconds |
| Druid R, Golem Seed | 85 → 68 | Root | 48ticks / 2seconds |
| Lich E, Bone Marionette | 66 → 53 | Root | 24ticks / 1second |

Effects apply on hostile ability impact to heroes and creeps, not buildings.
Damage scales by rank; control duration does not. Refreshes keep the later
expiry instead of adding durations. Existing delayed footprints and cast travel
matter: an in-range order is not a guaranteed hit.

| Own status | Move | Basic attack | Spell | Item | Active portal |
| --- | --- | --- | --- | --- | --- |
| Stun | Blocked | Blocked | Blocked | Blocked | Interrupted |
| Root | Blocked | Allowed | Allowed | Allowed | Interrupted |
| Silence | Allowed | Allowed | Blocked | Allowed | Continues |

“Allowed” still requires normal range, resources and other host guards.
Ability leveling has separate gates; stun is not a prohibition on every host API.
The public APIs expose `selfSilenceTicks` and visible-object stun/silence/root
ticks alongside existing self stun/root ticks. They use the shared frozen
observation frame and do not reveal hidden heroes. No ability-control metadata
function exists: use this pinned hero/slot table for strategic control selection.
The incumbent already queries live `abilityDamage` for creep kill thresholds.

## Implemented and verified

The [reviewed semantic IR and BASIC pair](../../../../examples/gods_of_the_arena/players/ir/forks/control20260923-local/README.md)
uses a new release61 binding. Combat and Druid lane healing skip the spell channel
while silenced; attacks, items and movement retain their existing rules.
Healing resumes after silence expires. Root-compatible casting remains legal.
All other strategy order and calibrated parameters remain unchanged.

The binding also removes obsolete automatic-spell and old balance assumptions.
Every ability still needs an explicit cast after the previous patch. It accepts
only the new game version, keeping archived engines and frozen IR intact.

- Four upstream suites pass: controls, portals, spells and base policy.
  They cover real ability impacts, fixed durations at every rank, action legality,
  control refresh/death, fog filtering, frozen observations and replay seeking.
  [Outputs](tests/), [build/dependency proof](checks.json).
- **104 matched fixtures / 208 executions**, all ten classes on both colors in
  combat, plus Druid recovery, potion and channel cases. Each runs120actual ticks.
  The candidate removes **388 rejected silenced casts**. Every other command,
  including timing/arguments, and every recorded gameplay sample is identical.
  [Comparison](practice-comparison.json).
- Rooted heroes still cast; silenced heroes still attack and move. Druid potions
  work during silence/root, and lane healing resumes after silence. Portal tests
  preserve the distinction between silence and movement-disabling controls.
- **Eight complete native games / four paired counterfactuals** use matched seed,
  roster, subject slot and published configuration, with nine responsive upstream
  VMs. All80hero score calculations and full replay hashes pass. All ten terminal
  hero gameplay summaries match within every pair; subject score deltas are
  **0,0,0,0**. [Native comparison](native-comparison.json).

Fixtures use deliberately exposed visibility and an inert hostile body for
combat isolation; recovery cases use natural vision. Injected control windows
last48ticks; upstream tests separately verify each actual ability's duration.
An initial potion fixture used an elixir the incumbent does not select. It is
preserved, then corrected to its actual HealthPotion with heal spells on cooldown.
Only the corrected fixtures support the potion finding.

Gameplay sample equality excludes the diagnostic `lastActionError`, which changes
when rejected calls are omitted. We do not claim identical full state hashes
between policies. Each recorded match separately reproduces its own exact hashes.
Local match subjects naturally draft Crossbowman, Warlock and Berserker; the
all-class mechanism coverage comes from fixtures. These are not current-rival
score measurements or a statistically qualified replacement.

## Next score hypotheses

The [seven-layer semantic coaching IR](mechanics-and-coaching.ir.json) separates
verified mechanics from proposed tactics:

1. **Productive defense while rooted:** permit a reachable basic attack, useful
   heal or defensive spell when a retreat cannot move. Never interpret root or
   silence as harmlessness; enemy basics/spells may remain available.
2. **Control timing for hero finishes and escapes:** aim area casts using visible
   held time, cast delay and target reach. Avoid unnecessary overlap unless the
   damage secures a kill or immediate control prevents death. Silence should
   target dangerous casters, not automatically outrank a physical carry.
3. **Preserve XP income:** keep enough resources for control when a hero threat is
   present, while allowing efficient creep last hits. Measure actual accepted
   impacts, hero kills, creep XP, deaths, lane downtime and final score together.

The previous weak-hero bundle reduced deaths but reduced XP income and failed its
score gate. This patch does not make that unchanged source qualified. The Arcanist
shopping/resource problem also remains a separate hypothesis.

No hosted games, uploads or league writes occurred. [Readback](live-readback.json)
confirms both incumbent champions active on the new release. Future hosted work
requires **at most100variations per request, paired responsive counterfactuals**,
and the shared journaled budget adapter. Skipping rejected casts alone does not
justify spending a score trial; combine only independently motivated tactical
changes in a separately frozen candidate. The permanent daily cap remains100,000.

## Reproduction and preserved evidence

The isolated checkout and26exact dependencies are recorded in `checks.json`.
[`instruments/control20260923`](../../instruments/control20260923/) contains build,
conversion, status practice, paired full-match, comparison and publication tools.
The policy pair's `verify.py` checks portable hashes and exact Python/JSON/BASIC
round trips. [Input manifest](input-manifest.json) retains original creator notes,
published manifest, initial IR, fixture correction history, raw command/gameplay
traces and all eight complete replays without publishing signed artifact URLs.
