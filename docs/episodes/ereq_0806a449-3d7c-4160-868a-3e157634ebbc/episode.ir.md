# Reconstructed episode IR — ereq_0806a449-3d7c-4160-868a-3e157634ebbc

## 1. Episode header

**Status:** reconstructed; fidelity is reconstruction-to-IR; decision quality is candidates only. Revised guide section 11 applies.

**Episode:** `f7ede3be-c505-4f11-a973-7dedca5a7e11`; request `ereq_0806a449-3d7c-4160-868a-3e157634ebbc`; round `round_8020fd06-cf4b-4d54-90ba-a9ffdf376b00`. [Observatory](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_0806a449-3d7c-4160-868a-3e157634ebbc).

**Environment:** Gods of the Arena / Competition, `2026.9.16.5`, source `f2ab9598d8f8001b6beae3e66404e341770c803f`.

**Policy:** `aaron-gota-ir-relh154-legacy-0916:v1`; version `53f15b12-2198-41d1-bb99-df4bdb1ff7fd`; policy ID `df3daddb-adce-4bf3-81ce-f66af73c1101`.

**IR:** `gota_relh154_legacy`, canonical SHA256 `8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37`; file-byte SHA256 `7030610727902f3fb7ae74325261a791dd98c5db3404574cfc5122014c11ac42`.

**BASIC:** SHA256 `b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9`; [frozen executable](policy.bas); [frozen IR](policy.ir.json).

**Perspective:** slot 0, DeathKnight, Red, hero 100. Slots 1–4 are independent instances of the same version (Crossbowman, Lich, Warlock, Berserker). Their internal states are not shared with slot 0. All five owned instances are covered by command/state equivalence; the detailed account and fidelity counts cover slot 0.

**Opponents:** slots 5–9, `gota-g002:v1`, version `a30542cb-54de-4109-92e6-bcabca7db4d8`, policy ID `763b0cd0-e203-49c7-953a-5cda2252f4c9`.

**Seed:** effective `1354549052` from results/replay; requested seed `2026` is not the effective seed; map seed `54`.

**Outcome:** Red loss, Blue win; scores `[0, 0, 0, 0, 0, 1, 1, 1, 1, 1]`. Duration 13,557 ticks = 09:24.88 at 24 Hz.

**Segmentation:** 43 decision points from 12,261 living decisions. A point begins when the locomotion owner, matched rule set, or fused R1 defense choice changes, or when the host resumes decisions after a death. Repeated target IDs, rally-coordinate updates, inventory use and attack ticks are execution details while those choices persist. Six death gaps are recorded as span terminations; no policy decisions are invented during them.

**Observation timing:** Situation uses the visibility-filtered object list immediately before this hero's VM runs and the VM's host snapshot. Predicate truth is recorded at its rule's evaluation phase, since E0 changes the inventory facts used by E2. End-of-tick omniscient frames are kept separately for retrospective quality filtering.

**Reconstruction caveat:** the original logs contain only start/completion messages. The reconstruction reproduces every owned command and every state hash in this episode. Its beliefs and rule evaluations are its own; output-equivalent but internally different original behavior is invisible. Trace prints add no globals; an uninstrumented run also matches every captured observation, all 227 globals before/after each subject decision, and all captured state projections.

**Common rule and parameter contract**

Rules run in this order. Every matching rule fires. R2/R4 share locomotion, with only one writer on each observed tick; purchases compose sequentially. There is no global one-rule winner or runtime ordering of abstract goals. Parameter sets below are frozen and referenced by every Selected line.

- `R0`: `always` → `count`; goals `G_base`.

- `R1`: `always` → `observe`; goals `G_base`, `G_defense`.

- `R2`: `always` → `attack`; goals `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`.

- `E0`: `always` → `consume`; goals `G_capacity`, `G_survival`.

- `E1`: `always` → `sustain`; goals `G_capacity`, `G_survival`.

- `E2`: `inventory_has_empty` → `equipment`; goals `G_capacity`, `G_glory`.

- `R4`: `no_candidate_no_motion` → `fallback`; goals `G_wave`, `G_defense`.

<details><summary>Exact skill operators and static parameters</summary>

```json

{
  "count": {
    "operator": "count_decision",
    "parameters": {}
  },
  "observe": {
    "operator": "lineup_paired_legacy",
    "parameters": {
      "redbranch_edge_tiles": 2,
      "redbranch_fort_tiles": 4,
      "redbranch_unit_weight": 1,
      "redbranch_building_weight": 1,
      "redbranch_plain_class": 9,
      "redbranch_extra_class": 7,
      "redbranch_pursuit_tiles": 12,
      "redbranch_group_size": 4,
      "redbranch_home_tiles": 100,
      "redbranch_tower_tiles": 14,
      "redbranch_cluster_tiles": 12,
      "redbranch_hold_ticks": 1440,
      "redbranch_behind_tiles": 4,
      "redbranch_intercept_tiles": 10,
      "redbranch_creep_first": 0,
      "redbranch_hp_weight": 1,
      "redbranch_continue_home": 48,
      "redbranch_gather_heroes": 0,
      "redbranch_blue_group": 4,
      "redbranch_blue_hold": 1200,
      "redbranch_blue_continue": 24,
      "redbranch_red_sentry": 3,
      "redbranch_blue_sentry": 3,
      "redbranch_sentry_hold": 7200,
      "edge_tiles": 2,
      "fort_tiles": 4,
      "unit_weight": 1,
      "building_weight": 1,
      "plain_class": 9,
      "extra_class": 7,
      "pursuit_tiles": 12,
      "group_size": 4,
      "home_tiles": 100,
      "tower_tiles": 14,
      "cluster_tiles": 12,
      "hold_ticks": 1440,
      "behind_tiles": 4,
      "intercept_tiles": 10,
      "creep_first": 0,
      "hp_weight": 1,
      "continue_home": 48,
      "gather_heroes": 0,
      "blue_group": 4,
      "blue_hold": 1200,
      "blue_continue": 24,
      "red_sentry": 3,
      "blue_sentry": 3,
      "sentry_hold": 7200,
      "core_response_tiles": 24,
      "core_radius": 14,
      "backdoor_tiles": 24,
      "backdoor_hold": 480,
      "near_response": 28,
      "response_stagger": 96,
      "isolated_max": 1,
      "perimeter_team": 2,
      "perimeter_tiles": 24,
      "response_reach": 32,
      "release_mode": 1,
      "idle_ticks": 480,
      "middle_group": 3,
      "middle_opening_ticks": 1800,
      "pair_damage": 150,
      "pair_opening": 3600
    }
  },
  "attack": {
    "operator": "defense_cadence",
    "parameters": {
      "normal": 1,
      "targeted": 0,
      "risk_hp": 0,
      "min_ticks": 12,
      "max_ticks": 64,
      "gain_tiles": 2,
      "step_tiles": 3,
      "threat_tiles": 7,
      "support": 1,
      "spells": 1,
      "recovery_ticks": 1,
      "all_classes": 1,
      "plain_class": 9,
      "motion_object_limit": 80,
      "defense_motion_limit": 40
    }
  },
  "consume": {
    "operator": "consume_inventory",
    "parameters": {
      "heal_denominator": 5,
      "heal_numerator": 3,
      "mana_denominator": 5,
      "mana_numerator": 2
    }
  },
  "sustain": {
    "operator": "buy_sustain_only",
    "parameters": {}
  },
  "equipment": {
    "operator": "selective_loadout",
    "parameters": {
      "first_item": 11,
      "second_item": 13,
      "third_item": 18,
      "fourth_item": 19,
      "fifth_item": 16,
      "red_loadout": 0
    }
  },
  "fallback": {
    "operator": "lineup_perimeter_route",
    "parameters": {
      "redbranch_fallback_x": 64,
      "redbranch_fallback_y": 64,
      "redbranch_offset_tiles": 0,
      "redbranch_stall_decisions": 48,
      "offset_tiles": 0,
      "stall_decisions": 48,
      "fallback_x": 64,
      "fallback_y": 64,
      "rally_spacing": 2,
      "forward_rally": 0
    }
  }
}

```

</details>

## 2. Arc

The DeathKnight followed the opening wave route while no attack candidate was selected. At 00:34.92, four living visible enemy heroes near an allied tower caused `observe` to activate defense and `fallback` to send it toward a defensive rally. Across later combats and respawns it alternated between attacking selected nearby targets and returning to defensive rally points, retaining its sentry commitment. The episode ended at 09:24.88 with Red's god destroyed and Blue winning.

## 3. Decision points

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp01

**Header —** tick 1, 00:00.04; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 350/350, tile (111, 4); living visible enemy heroes: none. `defActive=0`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; ordinary target selection [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=0`, `defHoldTicks=7200`, rally `(0,0)`, remembered threat `(0,0)`. `defCount=0` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=0`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+6 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(0,0)`. Start-tick commands: `3(7,0), 3(5,0), 3(11,0), 3(13,0), 3(6,0), 3(9,0), 1(111,25)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 1–837 (34.88 seconds of living execution), terminated by channel choice changed at tick 838. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 350→400, tile (111, 4)→(106, 82), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 11→11. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02

**Header —** tick 838, 00:34.92; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (106, 82); living visible enemy heroes: 106 at (62,48), HP 238, 107 at (62,48), HP 190, 108 at (62,48), HP 250, 109 at (63,46), HP 220. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=8038`, `defHoldTicks=7200`, rally `(68,39)`, remembered threat `(63,46)`. `defCount=4` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(68,39)`. Start-tick commands: `1(68,39)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 838–1470 (26.38 seconds of living execution), terminated by channel choice changed at tick 1471. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 66 ticks, first at tick 1200.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (106, 82)→(80, 43), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 11→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp03

**Header —** tick 1471, 01:01.29; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (80, 42); living visible enemy heroes: 105 at (79,30), HP 330, 106 at (76,31), HP 276, 107 at (76,30), HP 166, 108 at (77,30), HP 168, 109 at (78,29), HP 262. `defActive=1`, `defSentry=1`, `bestId=1068`. Selected target is a visible footman at (76,33), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=8647`, `defHoldTicks=7200`, rally `(85,26)`, remembered threat `(79,32)`. `defCount=5` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1068`. Start-tick commands: `2(1068,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 1471–1475 (0.21 seconds of living execution), terminated by channel choice changed at tick 1476. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (80, 42)→(80, 42), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp04

**Header —** tick 1476, 01:01.50; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (80, 42); living visible enemy heroes: 105 at (79,30), HP 330, 106 at (76,31), HP 276, 107 at (76,30), HP 166, 108 at (77,29), HP 168, 109 at (78,28), HP 262. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=8647`, `defHoldTicks=7200`, rally `(85,26)`, remembered threat `(79,32)`. `defCount=5` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(85,26)`. Start-tick commands: `1(85,26)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 1476–1482 (0.29 seconds of living execution), terminated by channel choice changed at tick 1483. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (80, 42)→(80, 42), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp05

**Header —** tick 1483, 01:01.79; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (80, 41); living visible enemy heroes: 105 at (78,29), HP 330, 106 at (76,30), HP 276, 107 at (76,29), HP 166, 108 at (77,28), HP 168, 109 at (78,27), HP 262. `defActive=1`, `defSentry=1`, `bestId=1060`. Selected target is a visible footman at (75,33), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=8647`, `defHoldTicks=7200`, rally `(85,26)`, remembered threat `(79,32)`. `defCount=5` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1060`. Start-tick commands: `2(1060,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 1483–1582 (4.17 seconds of living execution), terminated by host decision gap; next invocation at tick 1799 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 400→0, tile (80, 41)→(77, 33), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp06

**Header —** tick 1799, 01:14.96; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (111, 4); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed]; defense memory persists across a decision gap [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=8647`, `defHoldTicks=7200`, rally `(85,26)`, remembered threat `(79,32)`. `defCount=5` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(85,26)`. Start-tick commands: `1(85,26)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 1799–2132 (13.92 seconds of living execution), terminated by channel choice changed at tick 2133. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 8 ticks, first at tick 2002.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (111, 4)→(100, 15), successful basic-hit counter 0→0; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp07

**Header —** tick 2133, 01:28.88; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (100, 15); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=1098`. Selected target is a visible footman at (93,22), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=9242`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(86,25)`. `defCount=5` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1098`. Start-tick commands: `2(1098,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 2133–2299 (6.96 seconds of living execution), terminated by host decision gap; next invocation at tick 2516 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 48 ticks, first at tick 2171.

**Consequence —** Between the first and last policy snapshots: self HP 400→0, tile (100, 15)→(90, 21), successful basic-hit counter 0→1; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp08

**Header —** tick 2516, 01:44.83; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (111, 4); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed]; defense memory persists across a decision gap [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=9499`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(89,22)`. `defCount=2` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(100,15)`. Start-tick commands: `1(100,15)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 2516–3475 (40.00 seconds of living execution), terminated by channel choice changed at tick 3476. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 117 ticks, first at tick 3359.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (111, 4)→(100, 15), successful basic-hit counter 1→1; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp09

**Header —** tick 3476, 02:24.83; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (100, 15); living visible enemy heroes: 109 at (92,21), HP 316. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (92,21), HP 316. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=10676`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(92,21)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 3476–3688 (8.88 seconds of living execution), terminated by host decision gap; next invocation at tick 3905 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 196 ticks, first at tick 3476.

**Consequence —** Between the first and last policy snapshots: self HP 400→0, tile (100, 15)→(90, 21), successful basic-hit counter 1→4; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp10

**Header —** tick 3905, 02:42.71; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (111, 4); living visible enemy heroes: 105 at (93,20), HP 258, 107 at (90,21), HP 246, 108 at (91,20), HP 350. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense memory persists across a decision gap [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=11105`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(93,20)`. `defCount=3` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(100,15)`. Start-tick commands: `1(100,15)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 3905–4053 (6.21 seconds of living execution), terminated by channel choice changed at tick 4054. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 149 ticks, first at tick 3905.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (111, 4)→(102, 14), successful basic-hit counter 4→4; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp11

**Header —** tick 4054, 02:48.92; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (101, 14); living visible enemy heroes: 105 at (93,20), HP 241, 107 at (90,21), HP 246, 108 at (91,20), HP 394. `defActive=1`, `defSentry=1`, `bestId=105`. Selected target is a visible hero at (93,20), HP 241. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=11254`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(93,20)`. `defCount=3` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=105`. Start-tick commands: `2(105,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 4054–4308 (10.62 seconds of living execution), terminated by channel choice changed at tick 4309. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 255 ticks, first at tick 4054.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (101, 14)→(92, 20), successful basic-hit counter 4→9; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp12

**Header —** tick 4309, 02:59.54; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (92, 20); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=11508`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(91,21)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(100,15)`. Start-tick commands: `1(100,15)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 4309–4650 (14.25 seconds of living execution), terminated by channel choice changed at tick 4651. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 38 ticks, first at tick 4572.

**Consequence —** Between the first and last policy snapshots: self HP 400→400, tile (92, 20)→(100, 15), successful basic-hit counter 9→9; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp13

**Header —** tick 4651, 03:13.79; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 400/400, tile (100, 15); living visible enemy heroes: 109 at (92,21), HP 328. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (92,21), HP 328. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=11851`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(92,21)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 4651–4800 (6.25 seconds of living execution), terminated by channel choice changed at tick 4801. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 150 ticks, first at tick 4651.

**Consequence —** Between the first and last policy snapshots: self HP 400→154, tile (100, 15)→(92, 22), successful basic-hit counter 9→10; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp14

**Header —** tick 4801, 03:20.04; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 154/462, tile (92, 22); living visible enemy heroes: 107 at (8,88), HP 310, 108 at (8,87), HP 394. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=12000`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(91,23)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(100,15)`. Start-tick commands: `1(100,15)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 4801–6090 (53.75 seconds of living execution), terminated by channel choice changed at tick 6091. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 53 ticks, first at tick 5402.

**Consequence —** Between the first and last policy snapshots: self HP 154→406, tile (92, 22)→(100, 15), successful basic-hit counter 10→10; own visible god HP 400→400, own standing towers 9→9. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp15

**Header —** tick 6091, 04:13.79; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 406/462, tile (100, 15); living visible enemy heroes: 106 at (90,23), HP 314, 107 at (90,22), HP 310, 108 at (91,21), HP 442. `defActive=1`, `defSentry=1`, `bestId=1384`. Selected target is a visible footman at (92,21), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=13291`, `defHoldTicks=7200`, rally `(100,15)`, remembered threat `(91,21)`. `defCount=3` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1384`. Start-tick commands: `2(1384,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 6091–6335 (10.21 seconds of living execution), terminated by channel choice changed at tick 6336. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 240 ticks, first at tick 6091.

**Consequence —** Between the first and last policy snapshots: self HP 406→110, tile (100, 15)→(94, 19), successful basic-hit counter 10→15; own visible god HP 400→400, own standing towers 9→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp16

**Header —** tick 6336, 04:24.00; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 110/524, tile (94, 19); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=13535`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(93,20)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 6336–6919 (24.33 seconds of living execution), terminated by channel choice changed at tick 6920. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 43 ticks, first at tick 6877.

**Consequence —** Between the first and last policy snapshots: self HP 110→218, tile (94, 19)→(103, 9), successful basic-hit counter 15→15; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp17

**Header —** tick 6920, 04:48.33; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 218/524, tile (103, 9); living visible enemy heroes: 105 at (94,19), HP 510, 107 at (8,84), HP 285, 108 at (8,83), HP 490, 109 at (96,16), HP 364. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (96,16), HP 364. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=14120`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(96,16)`. `defCount=2` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 6920–7004 (3.54 seconds of living execution), terminated by host decision gap; next invocation at tick 7221 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 85 ticks, first at tick 6920.

**Consequence —** Between the first and last policy snapshots: self HP 218→0, tile (103, 9)→(100, 11), successful basic-hit counter 15→16; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp18

**Header —** tick 7221, 05:00.88; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 524/524, tile (111, 4); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed]; defense memory persists across a decision gap [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=14204`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(99,12)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 7221–8254 (43.08 seconds of living execution), terminated by channel choice changed at tick 8255. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 241 ticks, first at tick 7891.

**Consequence —** Between the first and last policy snapshots: self HP 524→524, tile (111, 4)→(103, 9), successful basic-hit counter 16→16; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp19

**Header —** tick 8255, 05:43.96; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 524/524, tile (103, 9); living visible enemy heroes: 109 at (95,15), HP 264. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (95,15), HP 264. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=15455`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(95,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 8255–8553 (12.46 seconds of living execution), terminated by host decision gap; next invocation at tick 8770 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 299 ticks, first at tick 8255.

**Consequence —** Between the first and last policy snapshots: self HP 524→0, tile (103, 9)→(97, 14), successful basic-hit counter 16→24; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp20

**Header —** tick 8770, 06:05.42; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 524/524, tile (111, 4); living visible enemy heroes: 108 at (91,21), HP 490. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense memory persists across a decision gap [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=15753`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(97,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 8770–8889 (5.00 seconds of living execution), terminated by channel choice changed at tick 8890. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 100 ticks, first at tick 8778.

**Consequence —** Between the first and last policy snapshots: self HP 524→524, tile (111, 4)→(103, 9), successful basic-hit counter 24→24; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp21

**Header —** tick 8890, 06:10.42; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 524/524, tile (103, 9); living visible enemy heroes: 108 at (96,16), HP 432. `defActive=1`, `defSentry=1`, `bestId=108`. Selected target is a visible hero at (96,16), HP 432. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16090`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(96,16)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=108`. Start-tick commands: `2(108,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 8890–9003 (4.75 seconds of living execution), terminated by channel choice changed at tick 9004. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 74 ticks, first at tick 8890.

**Consequence —** Between the first and last policy snapshots: self HP 524→586, tile (103, 9)→(98, 14), successful basic-hit counter 24→24; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp22

**Header —** tick 9004, 06:15.17; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (98, 14); living visible enemy heroes: 105 at (8,96), HP 419. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16163`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(98,14)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 9004–9484 (20.04 seconds of living execution), terminated by channel choice changed at tick 9485. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 206 ticks, first at tick 9220.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (98, 14)→(103, 9), successful basic-hit counter 24→24; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp23

**Header —** tick 9485, 06:35.21; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (103, 9); living visible enemy heroes: 105 at (10,92), HP 194, 107 at (8,95), HP 370, 109 at (95,15), HP 400. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (95,15), HP 400. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16685`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(95,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 9485–9583 (4.12 seconds of living execution), terminated by channel choice changed at tick 9584. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 99 ticks, first at tick 9485.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (103, 9)→(100, 11), successful basic-hit counter 24→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp24

**Header —** tick 9584, 06:39.33; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (100, 11); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16783`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(100,11)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 9584–9881 (12.42 seconds of living execution), terminated by channel choice changed at tick 9882. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (100, 11)→(103, 9), successful basic-hit counter 26→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp25

**Header —** tick 9882, 06:51.75; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (103, 9); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=1653`. Selected target is a visible footman at (96,16), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16783`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(100,11)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1653`. Start-tick commands: `2(1653,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 9882–9949 (2.83 seconds of living execution), terminated by channel choice changed at tick 9950. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (103, 9)→(97, 13), successful basic-hit counter 26→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp26

**Header —** tick 9950, 06:54.58; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (97, 13); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16783`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(100,11)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 9950–10361 (17.17 seconds of living execution), terminated by channel choice changed at tick 10362. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (97, 13)→(103, 9), successful basic-hit counter 26→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp27

**Header —** tick 10362, 07:11.75; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (103, 9); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=1677`. Selected target is a visible footman at (96,16), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16783`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(100,11)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1677`. Start-tick commands: `2(1677,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 10362–10439 (3.25 seconds of living execution), terminated by channel choice changed at tick 10440. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (103, 9)→(97, 14), successful basic-hit counter 26→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp28

**Header —** tick 10440, 07:15.00; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (97, 14); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=16783`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(100,11)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 10440–10838 (16.62 seconds of living execution), terminated by channel choice changed at tick 10839. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 23 ticks, first at tick 10816.

**Consequence —** Between the first and last policy snapshots: self HP 586→586, tile (97, 14)→(103, 9), successful basic-hit counter 26→26; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp29

**Header —** tick 10839, 07:31.62; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 586/586, tile (103, 9); living visible enemy heroes: 109 at (96,16), HP 400. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (96,16), HP 400. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18039`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(96,16)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 10839–11049 (8.79 seconds of living execution), terminated by host decision gap; next invocation at tick 11266 after a replay-verified death/respawn gap. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 171 ticks, first at tick 10839.

**Consequence —** Between the first and last policy snapshots: self HP 586→0, tile (103, 9)→(94, 17), successful basic-hit counter 26→29; own visible god HP 400→400, own standing towers 8→8. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp30

**Header —** tick 11266, 07:49.42; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 646/646, tile (111, 4); living visible enemy heroes: 106 at (96,15), HP 450, 107 at (96,14), HP 28, 108 at (97,14), HP 364. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense memory persists across a decision gap [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18466`, `defHoldTicks=7200`, rally `(103,9)`, remembered threat `(97,14)`. `defCount=3` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(103,9)`. Start-tick commands: `1(103,9)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 11266–11357 (3.83 seconds of living execution), terminated by channel choice changed at tick 11358. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 92 ticks, first at tick 11266.

**Consequence —** Between the first and last policy snapshots: self HP 646→646, tile (111, 4)→(107, 10), successful basic-hit counter 29→29; own visible god HP 400→400, own standing towers 8→7. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp31

**Header —** tick 11358, 07:53.25; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 646/646, tile (107, 10); living visible enemy heroes: 106 at (97,15), HP 492, 108 at (98,14), HP 262. `defActive=1`, `defSentry=1`, `bestId=108`. Selected target is a visible hero at (98,14), HP 262. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18558`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(98,14)`. `defCount=2` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=108`. Start-tick commands: `2(108,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 11358–11635 (11.58 seconds of living execution), terminated by channel choice changed at tick 11636. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 278 ticks, first at tick 11358.

**Consequence —** Between the first and last policy snapshots: self HP 646→646, tile (107, 10)→(100, 14), successful basic-hit counter 29→35; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp32

**Header —** tick 11636, 08:04.83; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (100, 14); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18835`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(99,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 1+2 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(106,12)`. Start-tick commands: `3(3,0), 3(5,0), 3(6,0), 1(106,12)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 11636–11807 (7.17 seconds of living execution), terminated by channel choice changed at tick 11808. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (100, 14)→(106, 12), successful basic-hit counter 36→36; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp33

**Header —** tick 11808, 08:12.00; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (106, 12); living visible enemy heroes: 108 at (7,96), HP 538. `defActive=1`, `defSentry=1`, `bestId=1749`. Selected target is a visible footman at (99,19), HP 60. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18835`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(99,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=1749`. Start-tick commands: `2(1749,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 11808–11885 (3.25 seconds of living execution), terminated by channel choice changed at tick 11886. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (106, 12)→(101, 18), successful basic-hit counter 36→36; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp34

**Header —** tick 11886, 08:15.25; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (101, 18); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=18835`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(99,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(106,12)`. Start-tick commands: `1(106,12)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 11886–12251 (15.25 seconds of living execution), terminated by channel choice changed at tick 12252. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 23 ticks, first at tick 12229.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (101, 18)→(106, 12), successful basic-hit counter 36→36; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp35

**Header —** tick 12252, 08:30.50; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (106, 12); living visible enemy heroes: 109 at (98,17), HP 400. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (98,17), HP 400. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=19452`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(98,17)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 12252–12356 (4.38 seconds of living execution), terminated by channel choice changed at tick 12357. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 45 ticks, first at tick 12252.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (106, 12)→(101, 18), successful basic-hit counter 36→36; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp36

**Header —** tick 12357, 08:34.88; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (101, 18); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=19496`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(103,16)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(106,12)`. Start-tick commands: `1(106,12)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 12357–12707 (14.62 seconds of living execution), terminated by channel choice changed at tick 12708. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 66 ticks, first at tick 12642.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (101, 18)→(108, 14), successful basic-hit counter 36→36; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp37

**Header —** tick 12708, 08:49.50; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (108, 14); living visible enemy heroes: 105 at (94,14), HP 570, 107 at (98,14), HP 370. `defActive=1`, `defSentry=1`, `bestId=107`. Selected target is a visible hero at (98,14), HP 370. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=19908`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(98,14)`. `defCount=2` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=107`. Start-tick commands: `2(107,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 12708–12843 (5.67 seconds of living execution), terminated by channel choice changed at tick 12844. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 71 ticks, first at tick 12708.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (108, 14)→(100, 17), successful basic-hit counter 36→37; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp38

**Header —** tick 12844, 08:55.17; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (100, 17); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=19978`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(102,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(106,12)`. Start-tick commands: `1(106,12)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 12844–13148 (12.71 seconds of living execution), terminated by channel choice changed at tick 13149. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 26 ticks, first at tick 13123.

**Consequence —** Between the first and last policy snapshots: self HP 708→708, tile (100, 17)→(106, 12), successful basic-hit counter 37→37; own visible god HP 400→400, own standing towers 7→7. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp39

**Header —** tick 13149, 09:07.88; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 708/708, tile (106, 12); living visible enemy heroes: 106 at (97,18), HP 558, 108 at (98,17), HP 586. `defActive=1`, `defSentry=1`, `bestId=108`. Selected target is a visible hero at (98,17), HP 586. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; self tile equals rally tile [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=20349`, `defHoldTicks=7200`, rally `(106,12)`, remembered threat `(98,17)`. `defCount=2` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=108`. Start-tick commands: `2(108,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 13149–13217 (2.88 seconds of living execution), terminated by channel choice changed at tick 13218. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 69 ticks, first at tick 13149.

**Consequence —** Between the first and last policy snapshots: self HP 708→770, tile (106, 12)→(101, 16), successful basic-hit counter 37→37; own visible god HP 400→400, own standing towers 7→6. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp40

**Header —** tick 13218, 09:10.75; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`; these are the source guards, not mutually exclusive options. Self HP 840/840, tile (101, 16); living visible enemy heroes: 106 at (100,17), HP 498. `defActive=1`, `defSentry=1`, `bestId=106`. Selected target is a visible hero at (100,17), HP 498. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=20418`, `defHoldTicks=7200`, rally `(109,14)`, remembered threat `(100,17)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (did not match), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=106`. Start-tick commands: `2(106,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 13218–13252 (1.46 seconds of living execution), terminated by channel choice changed at tick 13253. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 35 ticks, first at tick 13218.

**Consequence —** Between the first and last policy snapshots: self HP 840→840, tile (101, 16)→(101, 15), successful basic-hit counter 37→38; own visible god HP 400→352, own standing towers 6→6. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp41

**Header —** tick 13253, 09:12.21; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 840/840, tile (101, 15); living visible enemy heroes: 106 at (102,14), HP 380. `defActive=1`, `defSentry=1`, `bestId=106`. Selected target is a visible hero at (102,14), HP 380. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=20453`, `defHoldTicks=7200`, rally `(109,14)`, remembered threat `(102,14)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=106`. Start-tick commands: `2(106,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 13253–13334 (3.42 seconds of living execution), terminated by channel choice changed at tick 13335. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 24 ticks, first at tick 13253.

**Consequence —** Between the first and last policy snapshots: self HP 840→840, tile (101, 15)→(100, 16), successful basic-hit counter 38→40; own visible god HP 267→134, own standing towers 6→6. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp42

**Header —** tick 13335, 09:15.62; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`, `no_candidate_no_motion`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`; these are the source guards, not mutually exclusive options. Self HP 840/840, tile (100, 16); living visible enemy heroes: none. `defActive=1`, `defSentry=1`, `bestId=0`. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; no living enemy hero in current visibility [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=20476`, `defHoldTicks=7200`, rally `(109,14)`, remembered threat `(102,14)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R4` cites `G_wave`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2` → `R4`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 0 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 matched. **Locomotion winner: R4.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `fallback` uses the emitted walk destination below; defense rally is `(109,14)`. Start-tick commands: `1(109,14)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 13335–13529 (8.12 seconds of living execution), terminated by channel choice changed at tick 13530. The policy issued movement orders while no target was selected with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 42 ticks, first at tick 13488.

**Consequence —** Between the first and last policy snapshots: self HP 840→840, tile (100, 16)→(108, 14), successful basic-hit counter 40→40; own visible god HP 134→134, own standing towers 6→6. `no_candidate_no_motion` is true throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp43

**Header —** tick 13530, 09:23.75; slot 0. No environment-defined phase is recorded.

**Situation —** True glossary predicates: `always`, `inventory_has_empty`. Affordances: `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`; these are the source guards, not mutually exclusive options. Self HP 840/840, tile (108, 14); living visible enemy heroes: 109 at (99,15), HP 400. `defActive=1`, `defSentry=1`, `bestId=109`. Selected target is a visible hero at (99,15), HP 400. Distinctions: sentry assignment [unglossed]; visible living enemy count [unglossed]; selected target [unglossed]; own structure condition [unglossed]; defense commitment active [unglossed]; defense deadline [unglossed]; defense rally point [unglossed]; defense intercept eligibility [unglossed]; combat motion budget gate exceeded [unglossed]; defense renewal from fewer than four nearby heroes [unglossed].

**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: `defUntil=20730`, `defHoldTicks=7200`, rally `(109,14)`, remembered threat `(99,15)`. `defCount=1` is scratch state and may be stale when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.

**Goal in force —** Locomotion rule `R2` cites `G_fort`, `G_cadence`, `G_survival`, `G_glory`, `G_defense`. R1 continues to cite `G_base`, `G_defense`; the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.

**Arbitration —** Actual ordered firing: `R0` → `R1` → `R2` → `E0` → `E1` → `E2`. Bookkeeping: R0. Recognition/target/defense: R1 (`defActive=1`). Combat: R2 emitted 1 commands. Consumption: E0 emitted 0. Purchases: E1 then E2 (matched), 0+0 attempts. Fallback R4 did not match. **Locomotion winner: R2.** Rule predicates were checked against executed fire markers at their evaluation phases.

**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. Locomotion skill `attack` uses target `bestId=109`. Start-tick commands: `2(109,0)` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). A command is an invocation; purchase acceptance is not inferred from an attempt.

**Execution span —** ticks 13530–13557 (1.17 seconds of living execution), terminated by episode ended. The policy issued target attacks with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace. During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred on 28 ticks, first at tick 13530.

**Consequence —** Between the first and last policy snapshots: self HP 840→840, tile (108, 14)→(106, 14), successful basic-hit counter 40→40; own visible god HP 134→34, own standing towers 6→6. `no_candidate_no_motion` is false throughout this span. These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.

## 4. Judgment I — Fidelity (reconstructed)

**Consistent 43; inconsistent 0; unresolvable 0**, for the reconstructed primary-perspective decision points. Every one of 85,827 rule evaluations across 12,261 living ticks also matches the IR guard. No inconsistency list entries. Each channel's fired rules and command ranges were checked; ordered purchase actions are retained individually.

Per channel (bookkeeping, target/defense, combat/locomotion, inventory consumption, ordered purchases): 43 consistent, 0 inconsistent, 0 unresolvable decision points each. These are repeated views of the same 43 points, not 215 independent decisions. There are zero ticks with both R2 and R4 writing locomotion.

The IR compiles byte-for-byte to the deployed source and reverse-extracts to the same executable contract. The instrumented reconstruction reproduces 67,929 commands from all five owned heroes and all 13,557 state hashes, consuming all 128,895 recorded actions. The uninstrumented/instrumented comparison also preserves all captured observations and globals. These checks establish reconstructed executable fidelity. **Original internal fidelity is unresolvable** because original rule evaluations were not logged. No independent claim about the truth of authored goals, inferred intent, or original private internal state follows.

## 5. Judgment II — Decision quality (reconstructed; candidates only)

No win-probability series is supplied. The retrospective proxy is `(own god HP − enemy god HP)/100 + sum(own tower HP/maxHP) − sum(enemy tower HP/maxHP)`, with HP floored at zero. Each god contributes up to four tower-equivalent units; barracks are excluded. For each decision span, compare the state immediately before its first tick with its last post-tick state; rank the five largest decreases. This is an explicit material heuristic, not a win probability or a causal estimate. Longer spans have more exposure, and other heroes cause much of the change.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.q01

**dp:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`; ticks 838–1470.

**Actual:** `fallback` via `R4`; episode score 0; proxy change -1.8821.

**Initiation conditions satisfied:** `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`, `fallback`. All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.

**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, so the successful replay reconstruction is not counterfactual evidence.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.q02

**dp:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp43`; ticks 13530–13557.

**Actual:** `attack` via `R2`; episode score 0; proxy change -1.3400.

**Initiation conditions satisfied:** `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`. All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.

**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, so the successful replay reconstruction is not counterfactual evidence.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.q03

**dp:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp40`; ticks 13218–13252.

**Actual:** `attack` via `R2`; episode score 0; proxy change -1.3300.

**Initiation conditions satisfied:** `count`, `observe`, `attack`, `consume`, `sustain`. All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.

**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, so the successful replay reconstruction is not counterfactual evidence.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.q04

**dp:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp41`; ticks 13253–13334.

**Actual:** `attack` via `R2`; episode score 0; proxy change -1.2746.

**Initiation conditions satisfied:** `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`. All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.

**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, so the successful replay reconstruction is not counterfactual evidence.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.q05

**dp:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp31`; ticks 11358–11635.

**Actual:** `attack` via `R2`; episode score 0; proxy change -0.6541.

**Initiation conditions satisfied:** `count`, `observe`, `attack`, `consume`, `sustain`, `equipment`. All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.

**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, so the successful replay reconstruction is not counterfactual evidence.

No confidence-above-0.6 falsification candidates can be selected: runtime confidence is absent. There are no fidelity inconsistencies to add. No frozen-world trials were used.

## 6. Judgment III — Diagnosis (reconstructed; proposed evidence updates)

There are no rollout-backed decision-quality findings and no fidelity inconsistencies. Therefore none is routed as a demonstrated strategy, belief, skill-interface, or execution failure. The following are structural findings, glossary gaps, and measured-behavior proposals permitted by revised section 11; they remain proposals and do not edit the policy.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f01

**Kind / layer:** structural / strategy / embedder contract.

**IR blocks:** `strategy`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp01`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`.

**Observation:** Rules execute sequentially. R1 writes target/defense state, R2 controls combat, E0 consumes inventory, E1 and E2 both attempt purchases, R4 conditionally writes movement. R2/R4 share the locomotion output but only one writes it on each observed tick: no cross-rule overwrite occurred here. Purchases have cumulative effects on shared resources, not a single winner.

**Proposed update:** Represent rule order, read/write channels, guard evaluation phase, cumulative purchase effects and emitted-command provenance explicitly. Preserve the current execution order in the embedder.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f02

**Kind / layer:** structural / 1 and 5 fused.

**IR blocks:** `skill.observe`, `strategy.R1`, `goal.G_defense`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp18`.

**Observation:** observe/lineup_paired_legacy detects the visible rush, commits to defense, refreshes its deadline and chooses a target. These strategy choices are embedded in the observer.

**Proposed update:** In a future behavior-preserving lift, give recognition, commitment initiation, commitment renewal and defensive target selection separate named predicates/rules. Do not replace the algorithm during the lift.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f03

**Kind / layer:** ontology_gap / 1 — situation.

**IR blocks:** `situation.grounded.predicates`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp01`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp03`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp04`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp05`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp06`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp07`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp08`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp09`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp10`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp11`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp12`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp13`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp14`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp15`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp16`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp17`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp18`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp19`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp20`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp21`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp22`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp23`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp24`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp25`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp26`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp27`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp28`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp29`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp30`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp31`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp32`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp33`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp34`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp35`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp36`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp37`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp38`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp39`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp40`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp41`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp42`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp43`.

**Observation:** The deployed glossary has only always, inventory_has_empty and no_candidate_no_motion. It cannot name the defense, sentry, renewal and intercept distinctions exercised here.

**Proposed update:** Review the exact unglossed list as a proposed glossary extension, then add grounding and boundary fixtures for accepted terms.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f04

**Kind / layer:** measured_behavior_no_quality_verdict / not yet causally routed.

**IR blocks:** `belief.B_persistent_defense`, `belief.B_stale_rally`, `skill.observe`, `skill.fallback`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp18`.

**Observation:** The subject initiates defense at tick 838 and never records defActive=0 on a later living decision. A below-threshold visible group can refresh an existing sentry commitment. At tick 8150, one living observed enemy at (94,19) renews the deadline to 15350; the subject at (103,9) has no eligible target inside the ten-tile intercept radius and emits walkTo(103,9).

**Proposed update:** Attach this as a scoped activation example and a candidate for renewal/release research. It establishes intentional no-target rallying, not avoidable loss, successful defense, or collision failure.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f05

**Kind / layer:** evidence_gap / research tooling.

**IR blocks:** `belief.grounded`, `execution`, `update`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp02`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp43`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp40`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp41`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp31`.

**Observation:** Original policy logs have no rule trace; reconstructed globals contain commitments, not probabilistic enemy-intent estimates. Live opposing policies and forceable alternative-skill interfaces are absent.

**Proposed update:** Capture native rule events and decision-time observations during future episodes. Define branchable skill interfaces and recover validated live opponents before decision-quality verdicts. Keep absent confidence values null.

### ereq_0806a449-3d7c-4160-868a-3e157634ebbc.f06

**Kind / layer:** measured_execution_gate_no_quality_verdict / not yet causally routed.

**IR blocks:** `skill.attack.parameters.defense_motion_limit`, `skill.attack`, `belief.B_cadence_mechanism`, `goal.G_cadence`.

**Evidence:** `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp03`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp05`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp07`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp09`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp11`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp13`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp15`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp17`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp19`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp21`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp23`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp25`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp27`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp29`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp31`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp33`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp35`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp37`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp39`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp40`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp41`, `ereq_0806a449-3d7c-4160-868a-3e157634ebbc.dp43`.

**Observation:** All 2900 subject decisions with a selected target exceed the defensive motion limit of 40 observed objects. The source therefore takes its attack-only budget branch. motionActive remains zero throughout all 12261 living decisions; the cadence skill's presence is not evidence it activated here.

**Proposed update:** Record this activation limit separately from cadence efficacy. Investigate a cheaper combat observation set or budget-safe implementation before testing a different limit; preserve VM bounds and compare responding-policy outcomes before judging improvement.

## 7. Unglossed terms

These exact phrases are proposed vocabulary, not newly installed predicates. Their decision-point references are complete for the distinctions annotated above.

- **sentry assignment** — defSentry after R1; class-selected role, not a belief about a teammate's intent. Evidence: `dp01`, `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **visible living enemy count** — Count current observation objects with enemy team, kind=2, alive=true and hp>0. Never substitute defCount when defFront=0. Evidence: `dp01`, `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **selected target** — bestId after R1, including zero for no candidate; join nonzero IDs only to the current visible object list. Evidence: `dp01`, `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **own structure condition** — HP and standing status (hp>0) of allied kinds 1 and 4 in the current observation. Standing is distinct from objectAlive/exposure. Evidence: `dp01`, `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **ordinary target selection** — R1's defActive=0 branch, which performs ordinary bounded target selection. Evidence: `dp01`.

- **no living enemy hero in current visibility** — No current observed enemy kind=2 object has alive=true and hp>0. This says nothing about enemies outside visibility or enemy footmen. Evidence: `dp01`, `dp06`, `dp07`, `dp08`, `dp12`, `dp16`, `dp18`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp32`, `dp34`, `dp36`, `dp38`, `dp42`.

- **defense commitment active** — defActive=1 after R1, from worldTick<defUntil; commitment may outlive the visible group that initiated it. Evidence: `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **defense deadline** — Persistent defUntil and its remaining ticks, max(0,defUntil-worldTick). This is a commitment expiry, not a forecast or confidence. Evidence: `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **defense rally point** — Persisted defPointX/defPointY selected by R1; actual R4 walk destination may differ if terrain fallback runs. Evidence: `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **defense intercept eligibility** — Visible living enemy hero/footman within squared distance 100 of self, and within squared distance 400 of the remembered threat or squared distance 9 of self. R1 then ranks eligible candidates. Evidence: `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **combat motion budget gate exceeded** — objectCount()>defMotionLimit at R2; on this subject's active defense branch the limit is 40. This selects attack-only execution before cadence calculations. Evidence: `dp02`, `dp03`, `dp04`, `dp05`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp24`, `dp25`, `dp26`, `dp27`, `dp28`, `dp29`, `dp30`, `dp31`, `dp32`, `dp33`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **defense renewal from fewer than four nearby heroes** — A current nonzero defFront and defAnchor, defCount<defGroupSize, and an increase from pre-decision defUntil to the new deadline. Record the exact renewal tick; never backdate it to the span's start. Evidence: `dp02`, `dp06`, `dp07`, `dp08`, `dp09`, `dp10`, `dp11`, `dp12`, `dp13`, `dp14`, `dp15`, `dp16`, `dp17`, `dp18`, `dp19`, `dp20`, `dp21`, `dp22`, `dp23`, `dp28`, `dp29`, `dp30`, `dp31`, `dp34`, `dp35`, `dp36`, `dp37`, `dp38`, `dp39`, `dp40`, `dp41`, `dp42`, `dp43`.

- **defense memory persists across a decision gap** — At the first invocation after a missing-tick interval, R1 still yields defActive=1; verify the interval's death/respawn cause separately. Evidence: `dp06`, `dp08`, `dp10`, `dp18`, `dp20`, `dp30`.

- **self tile equals rally tile** — Host integer selfX/selfY equals defPointX/defPointY. This does not prove exact physical arrival, unobstructed movement, or tactical safety. Evidence: `dp07`, `dp09`, `dp13`, `dp15`, `dp17`, `dp19`, `dp21`, `dp23`, `dp25`, `dp27`, `dp29`, `dp33`, `dp35`, `dp39`.

## 8. Provenance

- Revised guide: `guide-episode-semantic-ir (1).md`, SHA256 `425b55d6a0d55b3ad4d18ad74bc355cf92bf5905e8d3b008b41447fdbaf2103e`; [frozen copy](guide-episode-semantic-ir-v2.md).

- Policy IR canonical hash `8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37`; byte hash `7030610727902f3fb7ae74325261a791dd98c5db3404574cfc5122014c11ac42`. These hash conventions are distinct.

- Simulator source `f2ab9598d8f8001b6beae3e66404e341770c803f`, release `2026.9.16.5`; original engine files were clean. Added probe instrumentation is [preserved here](replay_semantic_episode_probe.nim).

- Seed used for both reconstruction runs: `1354549052`. Counterfactual seeds: none. Other agents' recorded actions were used solely to reproduce the actual trajectory.

- Rule instrumentation: eval/fire/exit markers at the original top-level rule regions; no added globals; [instrumentation equivalence](instrumentation-equivalence.json), [IR/source parity](policy-parity.json).

- Full per-tick state is recoverable from the source-matched replay; the exported ground-truth JSONL is a projection, not a simulator checkpoint. The document uses full-state information only in labeled assessment/provenance, except public episode outcome and host termination facts.

- All raw artifacts and SHA256 hashes: [provenance.json](provenance.json). All 43 structured blocks, exact start/end observations, rule events, and trace line references: [episode.ir.json](episode.ir.json).

- Native viewer playback was not used. The existing five-frame schematic of the coached interval was inspected before measurement. No game-specific replay-inspection binding was found; repository-native tooling supplied the observations and replay checks.

- No behavioral edits, evidence attachment, hosted games, uploads or league changes were performed.
