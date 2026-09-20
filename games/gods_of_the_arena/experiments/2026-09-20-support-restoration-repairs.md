---
id: 2026-09-20-support-restoration-repairs
policy: current Aaron and Coach Jordan268 counter
baseline: exact deployed be6affd3 source
candidate: anchored idle caster support and unanchored idle caster support
status: refuted
hypothesis: Restoring visible ally-committed red caster assistance improves defensive combat without the broad recall regression.
decision_rule: Locally retain every deployed winning case, gain at least one red win, preserve gear and native budgets, and keep total deaths at most max(1.15 times deployed deaths, deployed deaths plus 5); observe actual support activation. Passing nominates fresh hosted tests only.
evals:
  - kind: native_local_regression_screen
    artifact: tmp/gota-ir/support-repairs-20260920/local-results.json
  - kind: complete_source_reconstruction
    artifact: tmp/gota-ir/support-repairs-20260920/verdict.json
---

# Hypothesis

The historical anchored-support policy beat Richard78 on both colors but fails against the exact current Alex policy on red. Its corrected class-7/8 idle-caster assistance is absent from the current deployed observer. Reintroduce only this assistance into the current 28-tile recall policy, keeping offensive counterpressure, blue source, movement, equipment and all existing target selection intact. Compare anchored assistance (standing friendly defensive structure required) against unanchored assistance, both requiring a healthy nearby ally publicly targeting the observed threat. No hidden state or opponent labels.

# Design and critique

Closed levers and the historical specialist review were checked. The supervised researcher owns caster transit, scoped blue response and all hosted collection; this interactive session owns this separate support-restoration directory. No duplicate collectors or agents. Current game release and native bindings remain pinned to 2026.9.16.5.

Four sources: deployed control, anchored restoration, unanchored restoration, exact historical anchor reference. Run each against default, deployed and historical anchor on both colors: 24 complete native games with the same six fixed cases. The reference differs in its observer and is descriptive context; compare each repair to the deployed control to attribute the restoration. All classes are present. Validate blue/noncaster inactivity and actual caster support in the real VM first; source/IR round trips must match. Every complete game requires native runtime budgets, full replay hashes/actions, scores and equipment checks. Failures are preserved, never counted as losses or silently omitted.

This is a local mechanism/regression screen. Opponents are owned programs, not Richard or Alex; gains cannot establish competitive transfer. Few deterministic cases are correlated. A restoration may be inactive because the current recall policy clears defense first; that outcome is informative, not evidence of an effective repair. Broader recall already caused severe local regressions and is not combined into this first attribution test.

# Predictions and decision rule

If the hypothesis holds, assistance produces a visible attack order in an idle-caster opportunity; at least one red fort loss becomes a win while retaining all deployed winning cases, all equipment, VM limits and the survival bound in frontmatter. If it is insufficient, activation is absent in full games, wins do not improve, or previously winning games/survival regress. Anchored versus unanchored identifies whether structure qualification changes the outcome. Count any draw as zero wins. No post-result threshold changes.

After a complete passing screen, nominate a frozen candidate for fresh hosted Richard135 and Alex g002 red comparisons against the exact deployed control; preserve the worker's numerical gates and require Jordan and both-color field checks before promotion. An initial failure ends advancement of that exact variant. Preserve every result and exact source hash in the repair ledger.

# Result

All 24 native games completed and passed replay hashes/actions, scores, VM budgets and equipment checks. Deployed, anchored restoration and unanchored restoration each won 3/6: red 0/3, blue 3/3, with 25 deaths. The historical reference won 4/6 but had 39 deaths, above the prospective limit max(1.15*25,25+5)=30; it was descriptive and not eligible to advance.

Both repaired sources pass real-VM activation, negative cases and dense fixtures for all actual class IDs (maximum 15,909 instructions and 24,491 fixture work). In full games, every canonical command from all ten heroes matches deployed in all six cases for both repairs. One raw replay differed in serialization, so command equality was checked using the calibrated canonical encoder rather than inferred from raw file hashes.

All six repaired red games were reconstructed using the exact BASIC source: 108,938 owned commands and every state hash matched; zero expanded-range assistance decisions occurred. Assistance can activate in the controlled fixture but does not change these game trajectories. This distinguishes inactive gameplay intervention from an implementation or VM failure.

The report, frozen plan, source bundles, command comparison and complete audits are under tmp/gota-ir/support-repairs-20260920. Feedback for each candidate is recorded in primary Python IR under feedback/{anchored,unanchored}; both retain byte-identical BASIC and compile/extract parity. No hosted XP or live policy changes were made by this isolated experiment.

# Verdict

Refuted in the pre-registered **local screen**: neither standalone restoration adds a red win or demonstrates expanded assistance during these full games. Both fail advancement. This is not a competitive verdict against Richard/Alex and does not refute a separately attributed combination with transit or timely response. The next mechanism must alter actual availability or response timing rather than repeatedly adding support behind inactive defense/idle-target gates. Exact failures enter closed_levers.md and the shared repair ledger; no rollback is needed because the sources were never deployed.
