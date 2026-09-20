---
{
  "id": "2026-09-10-structure-pressure",
  "policy": "GOTA semantic IR",
  "baseline": "local Duelist SHA256 7247acb6fe63d5f0eb40dd21efe8e27263af06705bb7161faba362cc3d0e13f3",
  "candidate": "local gota_duelist_structures",
  "status": "inconclusive",
  "hypothesis": "Hero preference can divert attention from nearby exposed objectives. Equal structure priority may convert pressure into fort wins, but can increase tower exposure.",
  "decision_rule": "Discovery: >=4 additional wins/60 over matched Duelist and observed mechanism. Highest qualified win count, fixed tie order, receives ONE frozen confirmation. Confirmation: 120 independent seed/seat pairs, 12/class; gain >=5 points vs Duelist and >=10 points vs default baseline, exact paired p<0.025 for both; no Bonferroni-flagged adverse metric/class in either 55-test sweep. Local evidence only.",
  "evals": [
    "local:tmp/gota-ir/hypothesis-study-20260910/discovery/parent",
    "local:tmp/gota-ir/hypothesis-study-20260910/discovery/structures"
  ]
}
---

# Set exposed-structure distance weight to 1, equal to heroes, while footmen retain weight 4.

## Context

Derived from the current `duelist.ir.json` and completed campaign. The local `closed_levers.md` and optimizer-seed root register were checked. This is a separate mechanism, not a retry of poison removal or another hero-weight sweep. The live read-only snapshot still reports game 2026.9.10.3. No hosted performance claim is made.

Code location: `binding.py`, observe / R1. Every other behavior is identical to the frozen Duelist parent; goals and claims are updated to describe the one change.

## Predictions — pre-registered

- If TRUE: The fraction of decisions aimed at exposed towers/forts increases; fort wins improve if current hero pursuit diverts useful siege pressure. Melee tower exposure is the principal risk.
- If FALSE: Structure targeting does not increase, or earlier tower focus increases deaths and reduces wins.

## Design

First inspect existing evidence and verify the binding in controlled real-VM scenarios. Then run 60 complete games per arm on discovery seeds 61000–61005, covering all ten classes separately among nine default policies. All three variants compare to the same fresh Duelist arm. Discovery is exploratory: six seed clusters do not establish significance.

Only a candidate with at least four additional wins and observed activation qualifies. The highest qualifying win count wins; ties use recovery, structures, single_heal order. Freeze this winner before 120 wholly new seeds 62000–62119, with one candidate seat per seed and 12 cases per class. Run matched Duelist and all-default baseline controls on those exact cases. Distinct seeds make the paired exact sign/McNemar test independent; there is no ten-seat pseudoreplication in confirmation. The required gains are 0.05 versus Duelist and 0.10 versus default baseline, p<0.025 each. Both must pass. Check wins, timeouts, death rate per decision, final gear, and final level for adverse changes overall and by class, using 0.05/55 per comparison. Class n=12 has low power; absence of a flag is not proof of class safety.

Adversarial critique: Additional structure attacks can indicate suicidal tower exposure rather than productive siege. Structure exposure remains mandatory. Inspect deaths and class splits alongside target-kind counts; post-tick classification can miss an object that died and was removed. The design isolates this one change against Duelist; a direct comparison to the default alone would confound it with existing Duelist changes. A weak effect may remain unresolved at 120 independent seeds; do not extend N or loosen the rule after looking. Historical validation seeds are excluded. All VM failures invalidate candidate eligibility; interrupted artifacts are preserved and resume checks hashes. Eight local workers; no concurrent hosted batches.

## Result

Completed 60 games per arm on six discovery seed clusters, all ten classes separately. Candidate 25/60 versus matched Duelist 35/60; delta -16.67 percentage points. No incomplete or VM-failed games were scored. All source, replay and trace hashes passed audit.

Predeclared activation proxy: `{"candidate_rate": 0.0728352161579232, "control_rate": 0.0446383256050015, "observed": true}`.

Structure-target share increased from 4.46% to 7.28%, so the intended preference was used. Wins fell by ten. This configuration is rejected by the discovery rule; six seed clusters are insufficient for a broad claim about structure pressure.

Per-class wins, deaths and equipment are preserved in [the report](../hypotheses-20260910-report.html) and [audited JSON](../hypotheses-20260910-result.json), SHA-256 `f82da4a2f319abf45c0c6184733fe0f639dd32d98b876d828824a86745e0405e`. The evaluated [IR](../hypotheses/structures.ir.json) generates [BASIC](../hypotheses/structures.bas) byte-for-byte identical to the tested source. Twenty-eight tests passed, including real-VM mechanics and both representation directions.

## Verdict

**Inconclusive for competitive superiority; this configuration did not qualify.** The predeclared discovery rule required four additional wins plus the activation condition; it was not met. No fresh-seed confirmation, additional XP, or league promotion was run. The unexecuted confirmation seeds remain unobserved. Retain the unchanged Duelist parent as the local reference. Do not conflate rejection of this setting with a proof that its broader mechanism can never work.
