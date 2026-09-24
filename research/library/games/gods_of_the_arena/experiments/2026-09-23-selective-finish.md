---
id: 2026-09-23-selective-finish
policy: selective-finish
baseline: druid-lane 29f6d7e6
candidate: 08987348157268b5aaf02b9c173942f2cde5866deba3064df64a15dee3db7b93
status: refuted
hypothesis: Restrict structure attacks to nearby short finishes while retaining recurring unit XP, improving score after elapsed-time cost.
decision_rule: Fresh400 games,50 per source/context; overall mean at least10% higher with positive lower95% bootstrap gain, each context at least95% of control, nonzero mean at least5% higher, nonzero frequency no lower, productive(score>=500) frequency strictly higher, all audits pass and current field stable.
evals: ["xreq_fd7c75c2-d10d-4bca-a73a-7af320529d1f", "xreq_d0fcef54-e1c6-463c-afb6-c57d0f2cc3a5", "xreq_e2b7e581-13ab-42f4-997a-515c9c0afc35", "xreq_e00f76a8-c012-40f9-afc6-7f5c22525523", "xreq_bcbbe23d-2004-4235-ac2d-9f01335b4acb", "xreq_55a6b050-5e2e-4484-964d-6da314980e20", "xreq_52164281-dacb-404b-b378-d62e2829ff0d", "xreq_9d329dd5-df82-4c25-8bc5-c2bc95c9c24d"]
---

# Hypothesis

User coaching on September23: damage alone earns no building XP; take low-health buildings we can plausibly destroy instead of prolonged sieges. Buildings award100XP to the last-hitting hero, and enemy-god destruction awards500XP per teammate. Destroying a barracks also removes a recurring creep source. Preserve captured inputs and the previous unit-farming trial unchanged.

This hypothesis is designed after seeing the first completed unit-farming cells, which did not preserve their control means. Its400-game trial is still finishing. No observations from that trial count as fresh control evidence for this new candidate, and its thresholds are unchanged.

# Design and critique

Closed levers reviewed. Neither ignoring buildings outright nor the earlier guarded siege bundle is a demonstrated improvement. This candidate forks the exact deployed Druid controller, changes target eligibility and short-finish priority together, and retains draft, economy, portals, healing, navigation and tower safety.

Enemy heroes and creeps remain eligible. An exposed living tower or god becomes eligible only within the existing public basic-reach estimate and at most two current basic hits of HP. Barracks require one hit because killing them removes future waves. Give an eligible one-hit tower/barracks a300point targeting bonus; a two-hit tower gets no added bonus. Retain existing lethal-hero, lethal-creep and god priorities. Public integer positions and reach are approximations; actual damage, death and XP acceptance must be practiced. No spell-damage forecasts or hidden enemy information. Current source applies basic damage to structures without armor mitigation, but simultaneous competing kills can still deny last-hit credit.

Mechanism checks must cover both colors/all classes, high HP rejection, two-hit tower acceptance, one-hit barracks acceptance, two-hit barracks rejection, distant/locked targets, mixed units, recovery and actual building death with100XP credit. Complete native games prove runtime only. Regenerate from semantic IR and verify compile/extract equality before hosted spending.

If local validation passes, use400fresh hosted games on published replay59,50 per source/context across red/blue lead/later draft. One subject and identical fixed rival versions/background roster across arms, natural draft, independent random seeds. Re-resolve all rivals before freeze; do not reuse prior control games. Decompose every game's ten source/VM identities, full replay hashes, XP and exact integer score. Report class mixtures and duplicate streams without outcome-driven filters.

Risks: a short last hit can still cost more future creep XP than its100reward, building priorities may steal better unit kills, approximated reach can induce travel, and current navigation may still advance into unproductive areas. Longer games can reduce score even with moreXP. This exact bundle can fail; the design does not assume the coaching hypothesis is true.

# Predictions and decision rule

If true: deliberate building commands concentrate on short finishes, hero/creep opportunities persist, and all frozen aggregate, per-context and productivity gates pass. If false: eligible finishes rarely activate, deny future XP, cause more deaths/travel, or fail the score criteria.

Use10000 whole-game bootstrap resamples stratified by context, with independent arm resampling. Nonzero mean is conditional on treatment outcome; require its increase jointly with preserved nonzero rate and higher productive rate. No extensions or threshold changes after outcomes. All400games remain in the result, including failures. Preregister the first four lexical episode IDs per arm for a32-game full command/effects diagnostic subset. A narrower class variant would require a new source and a separately frozen test.

# Result

All 400 fresh games passed ten-source/VM, full-replay, XP and integer-score audits. Every arm contains 50 distinct command streams; the game and principal champions stayed unchanged. All 802 candidate checks, 84 baseline checks and 16 complete native games passed. The policy/IR conversion is exact; worst fixture 17,930 instructions / 25,048 work. No gameplay edits or gate changes during the trial.

| Context | Baseline | Selective finishes | Change |
|---|---:|---:|---:|
| Red lead | 2,554.22 | 2,140.04 | −16.22% |
| Blue lead | 3,394.62 | 3,790.90 | +11.67% |
| Red later draft | 10.06 | 44.22 | +339.56% from a very low baseline |
| Blue later draft | 202.30 | 74.10 | −63.37% |

Overall mean **1,540.30 → 1,512.315 (−1.82%)**, 95% gain interval **[−16.53%, +14.35%]**. This interval does not establish the population direction. Nonzero mean increases 2,484.35 → 2,800.58, while nonzero frequency drops 62% → 54%. Productive-game mean increases 2,877.67 → 3,351.92, but productive frequency falls 53% → 44.5%. Zero games rise 76 → 92 of 200. The conditional averages do not rescue the failed joint rule.

In the preregistered 32-game subset, building-target commands fall 1,924 → 3, while unit-target commands fall 4,240 → 4,095. All three candidate structure commands satisfy the pre-tick cutoff: two one-hit towers and one two-hit tower. There are no over-two-hit commands or two-hit barracks commands. Local 220 target/kill fixtures establish actual100building/500god XP; hosted short-finishing activation is sparse. Merely excluding prolonged sieges does not create additional productive target opportunities. This diagnostic subset is not an independent competitive sample.

A DNS lookup failed during a read-only episode-list request after six experience requests were already recorded. The collector resumed those exact receipts and created only the two remaining planned arms. `collector-interruption.json` preserves the incident; all eight requests completed, with no duplicate spending, missing text logs, exclusions or replacement games.

# Verdict

**Refuted as a qualified replacement under the frozen joint rule; retain source29f6d7e6 on both players.** Aggregate gain, positive confidence bound, red-lead and blue-later preservation, nonzero frequency and productive frequency fail. The estimate is uncertain, so this is not proof that every selective-building strategy is harmful. Do not deploy a favorable blue/class slice or rerun unchanged. Preserve the reviewed semantic IR/BASIC pair and raw captures. Any coordinated opportunity/routing or class-scoped alternative needs a distinct source, measured activation and a separate prospective test.

Pair: `examples/gods_of_the_arena/players/ir/forks/selective-finish20260923-hosted`.
Raw evidence: `polyworld/tmp/gota-selective-finish59-20260923`; report and preregistered effects are under `trial/`.
