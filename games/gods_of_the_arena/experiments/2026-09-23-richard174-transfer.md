# Richard v174 guarded siege transfer — frozen before hosted submission

2026-09-23 UTC. User requested source-informed semantic IR and useful transfers from ../co-gas, with opaque uploaded names. This is one combined candidate, not separate component attribution.

Candidate BASIC SHA256: f7873bb2ec9ef14eb118639568144cadc75ad9a67f6b202a25a802890c85f143 (guarded-siege r2).
Baseline BASIC SHA256: 29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36, deployed Aaron 0c766ec9-131f-45d1-a207-ad75aea9ccc5 and Coach d75ff766-e78f-4aa5-b656-55eb29248208.
Engine 2026.9.22.3 / replay58 / 1b70894436b7ffdcd0d421b6b32c2415c9c8bfde. No gameplay edits.

Hypothesis: opportunistic tower pressure under allied cover, together with retaliation against an in-range hero attacking us during siege, increases individual score. The coordinated change retains last hits, selected hero fights, god targets and current recovery/portal priorities. The tower must already target someone else, be exposed and within ten observation cells; we need allied creep cover, at least65% health, no tower aggro and no local numerical disadvantage. Readiness uses existing public observations. No opponent identity or private runtime state.

Evidence: exact Richard source matches 82,818 commands and every replay state hash across four Warlock games. Its structure-first mode occurs on45,490 of71,954 living decisions. A broader diagnostic guard finds109 own decisions selecting a nonlethal creep while a covered nearby tower exists. Neither establishes causal score value. The candidate passed662 local checks and16 complete native games, both colors and draft positions, with exact Richard opposing it. Portable compile/extract reproduce identical source and IR.

Design: 400 fresh hosted games,50 per source/context, eight requests. Four contexts: red lead ordinal0, blue lead0, red late3, blue late3. Natural draft; later roster has two identical fixed baseline teammates. Principal opposing versions remain khors114, Richard174 and Jordan411; relh161 is a fixed teammate. All source bytes, rosters and configuration freeze in trial/plan.json before spend. Three requests maximum active. No old competitive controls, extensions, class filtering or retuning after results.

Qualification: zero source/VM/full-state-replay/XP/integer-score failures in all400 games; pooled mean individual score at least10% above fresh baseline; each of four context means at least95% of its control; strictly positive lower95% bound of10,000 context-stratified independent whole-game bootstrap relative gains. Current game and six principal champions must remain stable. Report hero classes, distinct command streams, XP by source, kills, deaths, minutes, level, last hits and score comparisons against each rival. Native results measure runtime, not league strength. No universal ranking or single-component causality claim.

Mechanism subset: first four lexically sorted episode IDs per source/context (32 total), independent of outcomes. Reconstruct subject VM commands from actual hosted tapes; compare source and full state hashes; report pressure choices, target outcomes and runtime. This subset is descriptive and cannot override the400-game gate.

Budget: user authorized10,000 additional games for September23 UTC; effective cap11,600. Before this study2,320 reserved, after2,720, leaving8,880. Shared ledger and paused legacy worker preserved. Qualified source may be deployed to both authorized players under bespoke opaque names; no privacy flag exists. Rejected source is archived with reviewed IR while current validated source stays deployed.

## Completed broad-source result

The coordinated source increased pooled mean individual score from **1,654.575 to1,779.945 (+7.58%)**, but failed the frozen10% threshold, the positive95% gain-bound requirement (interval **−8.65% to+27.05%**) and red later-draft preservation. It is **not deployed**. Both champions retain validated Druid lane recovery.

| Context | Baseline | Candidate | Change |
| --- | ---: | ---: | ---: |
| Red first pick | 2,945.18 | 3,040.86 | +3.25% |
| Blue first pick | 2,969.76 | 3,113.68 | +4.85% |
| Red later draft | 120.30 | 56.36 | −53.15% |
| Blue later draft | 583.06 | 908.88 | +55.88% |

All400 games pass ten-source/VM/full-replay/XP/integer-score audits. Each cell contains50games. The candidate blue-first cell has48distinct command streams; the other seven have50. Field versions were stable. All662 local checks and16native matches pass. The32-game mechanism subset reconstructs every subject command and world hash:149 covered-tower selections yield44 submitted tower attacks; two attacker selections yield two submitted attacks. Those are not landed-hit or causal score counts. Later-draft samples contain Druids; early samples differ in class mix.

The favorable blue-later result combines more heroXP (+138), creepXP (+458.74) and buildingXP (+38) with longer games (+1.177minutes, costing235.43points), plus god and clamp/rounding changes. Its gap against Richard improved, but its gap against khors worsened from−1,244.28 to−2,079.18. Higher personal points alone do not ensure league progress. No class or color slice qualifies the broad source.

[Reviewed portable IR/policy](../../../examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted/guarded-siege/) keeps the tested BASIC unchanged while recording failed qualification in its beliefs. [Full report](../../../examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted/evidence/report.json), [score/XP figure](../../../examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted/evidence/score-breakdown.png), [prospective plan](../../../examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted/evidence/plan.json) and [artifact index](../../../examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted/evidence/artifact-index.json) preserve all results. Run `python guarded-siege/verify.py`; use its `convert.py` for compile/extract.

Source SHA256: `f7873bb2ec9ef14eb118639568144cadc75ad9a67f6b202a25a802890c85f143`.
Reviewed IR SHA256: `841b52731c7e39476727bb26a448cf5b6b5775ffa5a8aa6af4eff2feeb93f4bb`.

A separate blue-Druid-only source is a new hypothesis requiring fresh controls and unchanged red/other-class commands. The eight-game baseline home-navigation diagnostic found zero redundant home-navigation commands; it does not justify importing Richard's nearest-defender rule now. Original inputs and failed instrumentation versions are preserved.
