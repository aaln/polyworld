---
id: 2026-09-19-jordan268-waveclear
policy: aaron-gota-ir-jordan268-counter
baseline: aaron-gota-ir-relh154-legacy-0916:v1
candidate: waveclear
status: inconclusive
hypothesis: "Jordan's observed hero-over-creep targeting leaves creep cover as a manipulable resource. Prioritizing visible enemy creeps during our existing defense may expose Jordan heroes to structures and improve the fort race."
decision_rule: "First screen 4 fresh games/color/arm. Advance if candidate gains at least 2 wins on one color without losing wins on the other. To call both Jordan fixed lineups beaten, a frozen selected fork must then win at least 30/40 fresh confirmation games on each color with complete replay/runtime audits. No league promotion."
evals: ["xreq_6950d368-2698-4942-a0b0-9fd2f51fbb2d", "xreq_0a9d974b-bf50-4ce0-b4c1-699f20063851", "xreq_1e741215-de41-48b9-b9fe-82078f042ad7", "xreq_13dec805-73b2-4cc8-b74b-17ff92857c7a"]
---

# Hypothesis

Opponent IR `Jordan268_I_O15` predicts hero targets in 155/238 heldout opportunities where heroes, creeps and exposed structures coexist; the class-conditioned field baseline scores 98/238. This is a targeting tendency, not an already-tested exploit.

Change only the defense target-kind preference: `observe.parameters.creep_first` and `redbranch_creep_first`, 0→1. These are the same semantic lever in the two team branches of `lineup_paired_legacy`. Keep alarms, role assignments, timing, movement, purchases and attack cadence unchanged.

# Design and critique

- Checked for `closed_levers.md`: no GOTA file exists. Historical `clear_wave`/`wave14` studies concerned earlier baselines and Jordan versions; they are not v268 evidence. Preserve this distinction.
- Current league game remains `2026.9.16.5`, commit `f2ab9598d8f8001b6beae3e66404e341770c803f`.
- Full ten-seat rosters: five copies of one owned policy versus five exact Jordan v268 copies (`207ffaf9-0d1e-4d92-a15d-4352f1bddec2`), both colors, current league map/config. Compare to exact parent `53f15b12-2198-41d1-bb99-df4bdb1ff7fd`.
- Bulk requests generate independent seed cohorts. They are roster-matched, not seed-matched A/B. Repeated fixed-lineup trajectories limit statistical independence. No game-specific evaluation floor binding exists; report directional, scoped outcomes, not broad league significance.
- Construct validity: observe actual own target-kind changes and tower/hero outcomes. More creep selections alone does not establish better wins.
- Main counterargument: ignoring a dangerous Jordan hero could lose defenders faster, or Jordan may not rely on creep shielding. That would refute this direction even if wave clearing activates.
- Adverse runtime/VM results invalidate competitive evidence; do not drop them or count them as successful gameplay. Preserve failed artifacts and diagnose.

# Predictions and decision rule

If true: defense chooses creeps when both kinds are available, followed by fewer surviving hostile creeps near our structures and higher fort-win count.
If false/backwards: the preference activates but fort wins stay zero or defenders/structures die sooner. Stop this lever after the screen; preserve the failed fork and use the replay to design a different single-lever experiment.

First screen: four fresh parent and candidate games per color; no tuning before all four arms finish. Advance with ≥2 additional wins on either color and no color regression. A selected fork must pass a new 40-per-color confirmation at ≥30 wins/color to claim the tested Jordan lineups beaten. Promotion into the main policy is outside this fork experiment.

# Result

Screen: parent red 0/4, blue 0/4; waveclear red 3/4, blue 0/4. All sixteen replay/VM/roster audits passed. Three red wins include two identical-length trajectories. The screen advancement gate passes, but this does not meet the both-color confirmation gate. Exact replayed own VM decisions show more creep targets (18/48 active nonzero targets in a red win, versus 1/51 in a parent red loss; correlated samples, different trajectories).

# Verdict

Inconclusive for beating both lineups. Preserve the red candidate and investigate blue opening assembly as a separate lever before spending on confirmation. The waveclear mechanism activates; its causal effect is not established by this small screen. No promotion.

Follow-up evidence: the identical red executable branch in counterrace confirmed14/40; waveclear alone was insufficient under the study threshold. Nearby-only recall was subsequently tested as separate blue and red levers. See the counterrace and redrace records.
