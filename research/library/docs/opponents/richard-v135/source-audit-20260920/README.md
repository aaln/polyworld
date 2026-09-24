# Richard v135: observation IR versus exact source

The observation IR captured useful coarse preferences, especially structure pressure, but it did not recover Richard's controller. The source combines a cached neural mode with ordered targeting, movement, inventory, defense and hit-recovery rules. This audit preserves the original IR and its 75.2% heldout motif accuracy; it adds a separately identified source model and discriminating tests.

For policy development, start with the [counter-policy guide](counter-policy-guide.md). For future inference studies, use the [revised guide](../../../guides/guide-opponent-model-ir.md).

The follow-up [Ranger economy audit](ranger-economy.md) reconstructs accepted purchases, kill rewards and level transitions across all 20 games. It reconciles all 200 hero XP/gold/level accounts and measures Ranger's repeated nine-tick basic-hit cadence.

## Exact identity

The supplied [commit](https://github.com/Metta-AI/co-gas/commit/93bd2aa1d79549960e88ea0f63ccf3a73273f198) changes `docs/gota-policy-handoff.md` (the requested diff anchor) and a candidate manifest. Its v135 source is `players/users/relh/co-gas/polyworld-basic/gods_of_the_arena_neural_siege_counter.bas`. The directory owner does not identify the hosted policy owner.

- Hosted Richard UUID: `7c370daf-3c5f-42f8-870b-54b79c495a44`.
- [Exact BASIC snapshot](v135.bas): SHA-256 `f48bb0057aeaf2ff939035324340183e34f8f9544e03226edfe62e78faad5a30`.
- [Candidate manifest](candidate.yaml) binds the UUID/hash and original source commit `fcdc915074115e772469c50daa61dc06b3ef8975`.
- Source at that original commit and the supplied commit is byte-identical.
- Game: `2026.9.16.5`, commit `f2ab9598d8f8001b6beae3e66404e341770c803f`.

This is not `gods_of_the_arena_relh_weak_gate_finish_v135.bas`. Fetching the referenced commit did not change the co-gas checkout. [Provenance](provenance.ir.json) records source custody and frozen-artifact hashes.

## What was verified

All five Richard VMs were replaced with the exact source on each of the original 20 target games; our five heroes replayed their recorded commands. Every Richard command and every full world-state hash matched through termination: **132,344 world ticks, 601,050 living policy decisions, 915,098 commands**. This verifies source equivalence on the original trajectories, not new competitive performance. [Complete receipts](runtime-audit.ir.json).

Twelve source-informed synthetic scenes, comprising 21 VM decisions, all passed in the pinned BASIC VM without changing weights or injecting private globals. The host accepts commands as specified by each fixture; these tests establish decision semantics, not physically reachable trajectories or successful attacks. [Requests and results](discriminating-fixtures.ir.json).

| Measured source behavior | Decisions/events in the 20 games |
|---|---:|
| Combat mode 0 / 2 / 6 | 318,972 / 219,316 / 62,762 |
| Objective equipment mode | 601,050 (all measured decisions) |
| Neural recomputations | 150,308 |
| Multiple recorded commands in one decision | 296,238 |
| Home-reservation guard true | 21,686 |
| Movement after a new landed hit | 6,266 |
| v135 tower-siege retaliation guard true | **0** |

Counts overlap; a later command can override an earlier command. The corpus does not exercise every source branch. In particular, the defining v135 change could not have been identified from positive examples in these games. All observed equipment modes being objective mode does not prove that every future state selects it.

## Compare the inferred and actual policies

The old predictor uses only an opportunity mask (hero/creep/exposed structure within 12 integer tiles) and absolute HP≤100. It predicts a category at retrospectively identified starts lasting at least six ticks. Richer features were recorded but were not predictor inputs. Only 18.3% of living opponent hero-ticks were visible from our selected single hero.

| Original inference | What the source establishes | Consequence |
|---|---|---|
| O13: structure over creep in their shared context, 140/226 heldout | Modes 2/8 prefer the nearest exposed **god or tower** within squared distance 300; barracks are excluded from this selector | Compatible aggregate tendency; split structure kinds and preserve mode/override uncertainty |
| O03/O04: hero over hold when only a hero is nearby | Generic nearest-enemy attack plus mode-dependent hero selection can produce this | Useful forecast; not proof of an unconditional hero preference or suicidal low-HP intent |
| O15/O11: hero targeting with structures nearby | Mode, objective kind, distance, self-directed attack and home defense all matter | “Hero nearby” is insufficient to recover why hero wins |
| O05/O07: creep targeting in mixed contexts | Generic nearest enemy and direct home-attacker priority can select creeps | Does not establish farming, last-hit optimization or a fixed creep preference |
| O09: structure targeting when alone | Compatible with objective selection or generic nearest selection | No individual lift over the population prior; retain provisional status |
| O06: low-HP hold, 0/3 heldout correct | No absolute-HP-100 hold branch; source uses HP percentage for neural input and consumables | No support for a voluntary low-HP holding mechanism; original failed forecast remains recorded |
| Concurrent movement qualifier | Several locomotion/attack requests can occur in one decision; final hit-recovery movement is a one-decision pulse | Keep action order and high-frequency events, not only sustained motifs |
| Grouping / split pressure visible in trajectories | Per-hero departure latch after ≥3 allies gather; dynamically nearest home defender, with possible distance ties | Geometry-dependent coordination exists; permanent roles or communication were not established |

[Claim-by-claim IR](comparison.ir.json) retains all nine preference IDs and their original status. These findings do not turn coarse heldout predictions into command-level errors; the evaluation targets differ.

## Actual execution structure

Source line references below refer to the frozen 666-line [BASIC](v135.bas). The [source semantic IR](source-model.ir.json) represents the seven layers with a dedicated non-compilable source-audit binding.

1. **Observation scan, lines 1–126:** nearest generic enemy, nearest god/tower, nearest hero, lowest-HP in-range hero targeting self, ally centroid/spread and rally count. Construct 25 clamped features including HP/mana percentage, class, geometry, phase and ability charges.
2. **Neural selection, 127–293:** 25→16 ReLU→18 linear scores; cached argmax recomputed every four living VM decisions. Outputs encode nine combat modes and two equipment modes. Targets are still rescanned every decision: this is not four ticks of blindness.
3. **Departure and base controller, 295–352:** persist a per-hero departure latch when a route-using hero is at the opening rally with at least three allies; deadlines remain at ticks 3500 and 4500. Mode 8 prefers objective, then hero, then generic enemy; other modes initially attack the nearest generic enemy or walk toward (64,64).
4. **Spell/economy, 354–516:** Lich midpoint ring attempt when the nearest hero targets self at 5<distance≤7; heal use below 60% HP and purchase below 50%. Objective equipment checks dagger→sword→armor→axe→book across classes. The normal equipment branch differs. Attempts and successful effects are separate.
5. **Mode overrides, 517–564:** retreat, objective-first attack/route, targeted cast, or ally-centroid movement according to combat mode.
6. **v135 siege correction, 566–570:** modes 2/8, nearest objective specifically a tower at squared distance≤300, and a visible enemy hero targeting this Richard hero within its own basic range: attack the lowest-HP eligible attacker. A god does not satisfy the tower guard.
7. **Home reservation, 572–659:** if ≤1 standing guard remains within 10 tiles of home, or a guard has ≤390 HP while self is within 30 tiles, reserve a hero with no strictly closer living ally. Equal distances can elect several. Within 20 tiles, attack a direct home attacker before a hero before another nearby unit; otherwise return home. A one-basic-hit enemy-fort finish in range suppresses recall.
8. **Hit recovery, 661–666:** after `selfAttacksLanded` increases, issue `walkTo(selfX,selfY)` last. This is a post-hit request, not evidence of voluntary idling or premature windup cancellation.

## Discriminating outcomes

- Fixed geometry, same neural combat mode 2: a nearby hero targeting another ally leaves the tower as terminal attack target; changing only its target to self switches Richard to that hero. Moving it outside range or changing the objective to a god prevents the switch. A second eligible attacker with lower HP wins.
- Same old creep+structure context and same combat mode: a tower is attacked; replacing it with a barracks causes route movement after the generic initial attack. The old model forecasts `target_structure` for both.
- Eight nearly identical observations produce countdowns `4,3,2,1,4,3,2,1`. A landed-hit counter sequence `0,1,1` produces terminal attack, self-position walk, attack.
- A creep directly targeting Richard's home outranks a nearby hero in home defense. Adding a strictly closer ally removes the tested hero's reservation.

These are source-informed counterexamples to the coarse context identifying a controller. They are not a new accuracy estimate or proof that a counter wins. The original 694/923 versus population 502/923 result and three heldout stream clusters remain unchanged.

## Reproduce and use

The instrument [README](../../../../games/gods_of_the_arena/instruments/opponent_ir/README.md) gives compilation and execution commands for `source_audit_probe.nim`, `source_audit.py`, `source_fixture_vm.nim` and `source_audit_fixtures.py`. Probes compile in the pinned clean game checkout, not the modified working engine. Source and binary hashes are retained in receipts.

Observed Richard maximum: 14,255 instructions and 23,076 work units per decision in these games, under the pinned 20,000 / 50,000 limits. This is a sample maximum, not a global bound. Our earlier cohort policy's cutoffs were real and belong to a different source; the [counter guide](counter-policy-guide.md) links those failures.

The audit used existing replays and local VM fixtures, spending no XP and changing no deployed policy. The source-informed IR is a documented mechanism model; it has not been compiled back into an equivalent executable. The original observation model remains `proxy.usable=false`.
