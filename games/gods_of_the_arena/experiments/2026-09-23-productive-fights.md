---
id: 2026-09-23-productive-fights
policy: productive-fights
baseline: druid-lane 29f6d7e6
candidate: 26dfc350d3bae7d4efd223f81c40a39e1ed56f7f2700fef8b2bce259df6d81c0
status: inconclusive
hypothesis: Guarded attacks on enemy heroes already within basic reach convert productive combat time into more XP than continuing nonlethal creep or lengthy structure attacks.
decision_rule: Fresh 400-game comparison; aggregate mean score gain at least 10%, positive lower 95% gain bound, every context at least 95% of baseline, nonzero mean at least 5% higher, nonzero frequency no lower, and score-at-least-500 frequency strictly higher. All audits pass; fixed exact field versions.
evals: ["tmp/gota-productive20260923/diagnosis.json"]
---

# Hypothesis

Increase score during productive games, the nonzero average, and the frequency of productive games. Score is floor(max(0, lifetime XP - 200 * elapsed minutes)), including drafting. More XP or longer games alone does not qualify an improvement.

Our observed controller gives a healthy creep a larger target bonus than a healthy enemy hero. We will diagnose opportunities to attack a hero already in basic reach while healthy and not locally outnumbered, preserving creep last hits, recovery, tower safety and near-dead god finishes. The proposed change caches visible eligible heroes and applies one guarded target override, without chasing beyond the measured reach or changing draft, economy, portal, healing or attack-recovery timing.

# Design and critique

Read closed_levers.md before design. Prior all-purpose target scoring, spell-pressure, broad lane recovery and guarded tower siege did not qualify. This is a distinct close-range hero-engagement rule; those failed bundles are not imported.

First diagnose eight existing own-source replays: four productive appearances selected lexically within color and four previously audited low cases. Full authentic-source command/state matching is required. This retrospective diagnosis can show an opportunity but cannot show a beneficial counterfactual.

Local checks will cover positive activation, lethal creep preservation, distant/invisible heroes, low HP, local disadvantage, tower aggro, retreat, portal channel, god finish and VM budgets across colors/classes. Native complete games test runtime and responsiveness only. Compile and extraction must reproduce the new semantic IR/BASIC pair.

If those checks support the mechanism, freeze one candidate and 400 new hosted games, 50 per source/context across red/blue first and later draft positions. One subject per game, identical fixed background rosters across arms, naturally available classes and current exact rival UUIDs. No reused competitive controls or post-hoc class filtering. The fresh field has Richard195 and khors114; use exact resolved versions, not the older Richard174 cohort.

Confounds: draft/class and roster differ between contexts; report each. Nonzero mean is conditioned on a post-treatment outcome, so it cannot alone establish better within-game play. Overall mean, nonzero frequency and >=500 frequency are evaluated together. Do not filter zeroes or invalid games to pass the gate. Seeds are independently assigned by host, not paired; bootstrap independent whole games within context. Sample size may leave the result inconclusive; report intervals without extending the cohort after outcomes.

# Predictions and decision rule

If true: the rule submits additional in-range hero attacks, hero XP rises enough to outweigh forgone creep/structure XP and extra time/deaths, aggregate score rises, and productive frequency does not fall. If false: those attacks do not activate, yield no extra hero XP, or increase time/death/creep opportunity costs enough to miss the score rule.

Productive game is prospectively defined as score >=500, preserving the prior audit's threshold. Nonzero means score >0. Report means of all scores, positive scores and >=500 scores; their frequencies; median and lower tail; XP sources, kills/deaths, class, match time and unclamped XP-minus-time margin. Primary qualification is the exact frontmatter rule with 10,000 context-stratified whole-game bootstrap draws. Conditional means and frequencies are also bootstrapped, with uncertainty reported. Exact source/VM/full-state/XP/integer-score audits are required for every purchased game; duplicate streams are disclosed. Freeze a mechanism subset by lexical episode ID before its detailed decoding.

No component-specific causal claim: observation cache and target override implement the same behavior. Current champions remain unless the complete fresh comparison qualifies; opaque policy names are used for inert uploads.

# Result

Eight existing own-source appearances match every command and state hash. The broad public-object guard finds zero opportunities in four productive appearances and five in the four low cases. This does not support spending a fresh400game cohort on this narrow rule. Candidate generated, but neither locally qualified nor hosted. The proposed fixture initially failed compilation due to a building enum name; its build log is preserved. No gameplay conclusions rely on it.

# Verdict

Inconclusive for score effect; deferred before hosted spending because the mechanism is absent in the selected productive sample. Preserve the exact source and diagnostic selection. Next distinct hypothesis: productive outbound portal use, documented separately.
