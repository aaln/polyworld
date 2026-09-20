---
{
  "id": "2026-09-10-hp-investment",
  "policy": "Reconciled GOTA semantic IR",
  "baseline": "Duelist 7247acb6fe63d5f0eb40dd21efe8e27263af06705bb7161faba362cc3d0e13f3 and default baseline",
  "candidate": "gota_duelist_hp_investment",
  "status": "inconclusive",
  "hypothesis": "When injured without healing stock, buying missing HP equipment before consumables converts gold into immediate HP and permanent capacity, improving fort wins; it can also displace consumables and class weapons.",
  "decision_rule": "One frozen candidate, 120 fresh independent seed/seat cases, 12/class. Win gain >=.05 vs Duelist and >=.10 vs default, one-sided paired exact p<.025 for BOTH. At least 30 games with an accepted emergency investment spanning >=3 classes. No adverse Bonferroni flag in the existing 55-metric/group sweep for either reference. No failed VMs or replay state mismatches. Hosted confirmation required before league promotion.",
  "evals": [
    "local:tmp/gota-ir/hp-investment-study-20260910/validation/parent",
    "local:tmp/gota-ir/hp-investment-study-20260910/validation/candidate",
    "local:tmp/gota-ir/hp-investment-study-20260910/validation/baseline"
  ]
}
---

# Emergency HP equipment before consumables

## Context

The independent IR review verified that an 80-gold helmet adds 50 maximum HP and immediately adds 50 current HP. Current selfHp/selfGold remain decision-start snapshots. The reconciled Duelist IR now records this fact in B_equipment_resources. Its starting BASIC remains unchanged. This is a new spending-order mechanism, distinct from the rejected four-equipment cap and single-heal configurations; both local and optimizer-seed closed-lever registers were checked.

## Predictions — pre-registered

- If TRUE: the early investment phase makes accepted purchases across several classes, provides immediate HP, and turns that resource gain into at least the required fort-win gains without material class regressions.
- If FALSE: gold/slots are too scarce for activation, reduced healing stock or delayed class weapons offset the HP, or wins fail the predeclared thresholds. More equipment alone is not evidence of stronger play.

## Design

Change only sustain skill E1. Below half starting HP, with hasHeal=0 from the existing inventory scan, inspect live inventory for an empty slot and missing helmet/buckler/amulet. Try those in cost order (80/90/120 gold), stopping this early investment phase after one successful purchase. Then execute the unchanged sustain-only routine and later normal equipment rules. This does not cap equipment, refresh self snapshots or inventory flags, change healing thresholds, or change targeting. Counters record accepted early investments and their catalog HP bonus; complete replay audits independently count real purchases/spending and validate every state hash.

Use the reconciled Duelist parent and all-default control. Each arm plays seeds 67000–67119, one fixed shuffled seat per seed, balanced 12/class, among nine default policies. All arms use the same seed/seat cases and pinned published runtime. This directly evaluates ONE source-grounded candidate; there is no preliminary selection sweep or outcome-conditioned validation entry. The two one-sided exact paired tests require p<.025 and the effect thresholds in frontmatter. The existing regression sweep covers win, timeout, deaths per decision, ending gear and level overall and in ten classes (55 comparisons per reference at .05/55). Class n=12 has low power and ending inventory/levels depend on game duration.

N=120 is a stated-arbitrary conservative local floor; modest improvements may remain unresolved. No early aggregate inspection, optional stopping, threshold changes, additional candidates or extension of N. All 360 games must finish and all tapes are audited before verdict. Source, runtime and instrument hashes are frozen in plan.json. Any VM failure or inconsistent replay blocks eligibility. Eight local workers. The user authorizes evaluations and already authorized a league update when ready; local-first then hosted comparison remains the sequence.

Adversarial critique: earlier gear is not free healing. Permanent slots and gold compete with potions and weapons; the cap experiment showed this tradeoff matters. Starting selfGold is stale after the investment, so subsequent attempts may fail correctly; the real host must enforce the budget. A healthy snapshot or existing heal blocks the new phase even if consumption just removed the last heal, preserving the isolated variable. Runtime counters observe accepted investments, not attempted purchases. A positive result would validate the whole changed policy in baseline-filled local rosters, not prove every explanatory belief or superiority over live rivals.

## Result

Completed all 360 games and all 360 replay state/purchase audits before inspecting aggregates. Candidate won **57/120 (47.5%)**, Duelist **62/120 (51.7%)**, default **55/120 (45.8%)**. Paired gain was **−4.17 percentage points versus Duelist** (17 positive, 22 negative pairs; one-sided exact p=0.831608) and **+1.67 points versus default** (28 positive, 26 negative pairs; p=0.445962). Both predeclared superiority gates failed. No adverse comparison crossed the conservative regression threshold; this does not prove absence of harm. Tick-limit timeouts increased from 5 parent / 4 default to 11 candidate, and are included as zero scores.

The mechanism activated in **89/120 games across all ten classes**: **113 accepted early investments**, granting **6,320 current HP** as well as maximum HP. Every event matched a real replay purchase and its exact HP increase. The first activating case in fixed seed order was 67001, Ranger slot 6: helmet at tick 4620 raised HP 158→208 for 80 gold; buckler at tick 5584 raised HP 141→201 for 90 gold. This case was not chosen by outcome.

The spending/capacity tradeoff is visible. Relative to Duelist, accepted healing purchases fell **1,208→701**, while equipment purchases rose **476→536** and healing rejections for lack of space rose **47,499→122,862**. Accepted healing per 1,000 candidate decisions fell **0.801→0.473** and no-space rejections rose **31.501→82.912**. Totals and rates are descriptive and affected by episode duration/state; these comparisons do not isolate the cause of the win difference.

Two initial candidate attempts (seeds 67039/67046, slots 3/4) hit the 180-second local wall-clock limit under heavy machine load; neither other arm had interrupted attempts. Both original cases completed on exact-input retry. Preserved complete partial-trace lines exactly match the retry prefixes (1,979 / 837 lines). No case was dropped, replaced or selectively rerun. See `tmp/gota-ir/hp-investment-study-20260910/interruption.json`. These infrastructure interruptions are distinct from the in-game tick-limit timeouts counted above.

All 36 tests passed. All 45,769,818 replay actions across 4,975,673 ticks were consumed with matching states. Source/trace hashes and IR↔BASIC parity passed. The new tracing instrument also reproduced the original baseline tape byte-for-byte before the comparison. Runtime work/instruction maxima remained below the VM budgets. Local published-source correspondence is not identity with the hosted container.

Evidence: [complete result](../hp-investment-20260910-result.json), [verification](../hp-investment-20260910-verification.json), [readable report](../hp-investment-20260910-report.html), [evaluated IR](../hypotheses/hp_investment.ir.json), [exact BASIC](../hypotheses/hp_investment.bas). Frozen pre-evaluation, evaluated and audited-review bundles are under `tmp/gota-ir/hp-investment-study-20260910/`. All seeds 67000–67119 are now observed.

## Verdict

**Local superiority unconfirmed; do not promote this setting.** The intended HP effect is supported, but it did not meet either win gate. Feed observed activation, spending and failed superiority evidence into separate IR beliefs while preserving the exact tested BASIC (SHA256 `9d7e638440b81b2c4601a325f37f5593f9b206198aa04d054318012eaefd7196`). A failed gate does not refute every possible use of HP equipment. Reopening needs new evidence for a distinct gold/slot-aware prerequisite, not another unchanged retry. No hosted XP, upload or league mutation followed this evaluation; the live readback shows the existing v2 champion.
