---
id: 2026-09-23-productive-return
policy: productive-return
baseline: druid-lane 29f6d7e6
candidate: 41ae39f6922ca6c248b6357ae5c6741a05127b290872f9d3a4708252943546fb
status: inconclusive
hypothesis: Spending one ready outbound scroll and aligning its destination with the active lane reduces travel and increases productive XP after elapsed-time cost.
decision_rule: Fresh 400-game comparison; aggregate mean score gain at least 10%, positive lower 95% gain bound, every context at least 95% of baseline, nonzero mean at least 5% higher, nonzero frequency no lower, and score-at-least-500 frequency strictly higher. All audits pass; fixed exact field versions.
evals: ["tmp/gota-productive-return59-20260923/local-summary.json", "tmp/gota-productive-return59-20260923/native-result.json"]
---

# Hypothesis

Increase score during productive games, the nonzero average, and the frequency of productive games. Score is floor(max(0, lifetime XP - 200 * elapsed minutes)), including drafting. More XP or longer games alone does not qualify an improvement.

Our current source requires two scrolls for outbound travel. It also chooses blue first-carry portal anchors using the outer-lane waypoint while its validated walking route uses the center. Change those together: one ready scroll is sufficient after recovery, and the friendly-tower anchor follows the actual lane waypoint. Preserve cooldown/channel lock, threat checks, distance >20 cells, recall, economy, draft, target selection, healing and combat timing.

## Release migration before hosted spending

During preparation, the league moved from 2026.9.22.3/replay58 to **2026.9.23.1/replay59**, published commit **d6827a4bd3a55a46cf86f88e921f147137709c64**, coworld `cow_32f7afc6-78f6-49d5-990b-5b3c3619662c`. The first candidate1513e2f9 passed582local checks and16native games on the old release but used no hosted games. Its inputs, tools and evidence remain in `tmp/gota-productive20260923`. The new study is `tmp/gota-productive-return59-20260923` with a separate engine worktree, decoder calibration, current-source semantic binding and fresh controls.

Current patch: Ranger HP growth19→29; Crossbowman damage69→58; Gale Slash52→65; Sanguine Chalice36→45. Score formula and relevant portal/host logic are unchanged. The IR records the changes; old competitive evidence does not qualify this engine. The same prospective metrics below apply; no outcome-driven threshold change.

# Design and critique

Read closed_levers.md before design. Prior all-purpose target scoring, spell-pressure, broad lane recovery and guarded tower siege did not qualify. The preceding close-hero diagnostic found no opportunities in four productive examples and was deferred without hosted spending. This is a distinct mobility hypothesis; none of those failed bundles is imported.

First diagnose the same eight preserved own-source replays for safe single-scroll outbound opportunities, requiring exact command/state matches. Replay-only findings are not treatment comparisons.

Local checks cover actual accepted single-scroll channels, aligned blue anchors, two-scroll compatibility, cooldown, insufficient HP, threats, no scroll, near-home destinations, no anchor, healing and recall. Full native games test runtime and responsive interactions. Compile and extraction must reproduce the semantic IR/BASIC pair.

If those checks support the mechanism, freeze one candidate and 400 new hosted games, 50 per source/context across red/blue first and later draft positions. One subject per game, identical fixed background rosters across arms, naturally available classes and current exact rival UUIDs. No reused competitive controls or post-hoc class filtering. The initial fresh field had Richard195 and khors179; use exact resolved versions, not the older Richard174 cohort.

Confounds: draft/class and roster differ between contexts; report each. Nonzero mean is conditioned on a post-treatment outcome, so it cannot alone establish better within-game play. Overall mean, nonzero frequency and >=500 frequency are evaluated together. Do not filter zeroes or invalid games to pass the gate. Seeds are independently assigned by host, not paired; bootstrap independent whole games within context. Sample size may leave the result inconclusive; report intervals without extending the cohort after outcomes.

# Predictions and decision rule

If true: single-scroll outbound channels activate, travel to productive farming shrinks, and extra XP exceeds the time cost and any lost-recall penalty. Aggregate/nonzero scores and productive frequency rise. If false: channels do not activate, deliver the hero to unproductive or unsafe positions, or loss of a ready recall creates enough deaths or downtime to miss the score rule.

Productive game is prospectively defined as score >=500, preserving the prior audit's threshold. Nonzero means score >0. Report means of all scores, positive scores and >=500 scores; their frequencies; median and lower tail; XP sources, kills/deaths, class, match time and unclamped XP-minus-time margin. Primary qualification is the exact frontmatter rule with 10,000 context-stratified whole-game bootstrap draws. Conditional means and frequencies are also bootstrapped, with uncertainty reported. Exact source/VM/full-state/XP/integer-score audits are required for every purchased game; duplicate streams are disclosed. Freeze a mechanism subset by lexical episode ID before its detailed decoding.

No component-specific causal claim: lane-aligned anchor selection and single-scroll use implement the same outbound behavior. Current champions remain unless the complete fresh comparison qualifies; opaque policy names are used for inert uploads.

# Result

Replay59 preparation passed582candidate checks,84baseline checks and16complete native games. No hosted requests or uploads were created. Rival policy-list endpoints returnedHTTP500 for three background players; later existing full replay artifacts provided current-engine source proofs. User supplied a new khors179 high-score episode and prioritized avoiding building attacks before this candidate was launched.

# Verdict

Deferred without a competitive verdict. Preserve source41ae39f6 and its portable IR/conversion/evidence in tmp/gota-productive-return59-20260923. Unit-farming is a separate fork of the same incumbent, without these portal changes.
