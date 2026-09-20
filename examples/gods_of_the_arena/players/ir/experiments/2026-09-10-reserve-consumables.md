---
{
  "id": "2026-09-10-reserve-consumables",
  "policy": "GOTA semantic IR",
  "baseline": "Duelist SHA256 7247acb6fe63d5f0eb40dd21efe8e27263af06705bb7161faba362cc3d0e13f3",
  "candidate": "gota_duelist_reserve_consumables cap=4",
  "status": "inconclusive",
  "hypothesis": "Permanent equipment fills all slots and blocks healing. Capping gear at four preserves consumable capacity and may increase wins at the cost of permanent stats.",
  "decision_rule": "Discovery >=4 added wins/60 over Duelist and parent gear>4 in >=3 classes, candidate never>4. Only then 120 independent fresh seeds (12/class), gain>=.05 vs Duelist and >=.10 vs default baseline with exact paired p<.025 for both. No adverse flag in 44 comparisons (win, timeout, death rate, level x overall+10 classes), alpha .05/44. Equipment reduction is an intended reported tradeoff. Hosted comparison still required before promotion.",
  "evals": [
    "local:tmp/gota-ir/reserve-study-20260910/discovery/parent",
    "local:tmp/gota-ir/reserve-study-20260910/discovery/candidate"
  ]
}
---

# Reserve two consumable slots

## Context

Existing audited seed 61000, Warlock slot 3, had six permanent items and 5,964 rejected healing purchases. This identifies a capacity failure, not its frequency or win impact. Closed levers checked: this is distinct from the failed single-heal branch. The live league still uses published game 2026.9.10.3. User explicitly authorizes league promotion when ready, following local validation then hosted XP.

## Predictions — pre-registered

- If TRUE: the cap prevents permanent equipment from occupying the last two slots, full-inventory healing rejection decreases, and retained sustain offsets lost stats to increase wins.
- If FALSE: capacity is rarely limiting, other consumables still block healing, or losing gear stats offsets access; wins fail the gain thresholds or regress.

## Design

One behavior changes: equipment cap four in E2; all targeting, sustain, consumption, gear ordering and fallback match Duelist. Real-VM tests cover within-decision cap, rejected purchases, reverse extraction and unaffected sustain. Audit accepted purchases, not attempt counts, by replaying every discovery tape against every original state hash.

Discovery uses seeds 63000–63005, every class separately, 60 games/arm among nine defaults. These are six seed clusters, not 60 independent trials. Audit all 120 games. If qualified, freeze this exact candidate for seeds 64000–64119, one shuffled, balanced seat per independent seed, plus matched parent and default controls: 360 confirmation games. Gates are in frontmatter and machine-readable plan. N=120 is an arbitrary conservative floor, may miss modest gains; no optional stopping or threshold changes. No additional candidate or reused historical validation seeds.

Adversarial critique: source evidence is one late-game Warlock, so class coverage is required before confirmation. Fewer healing rejections can result from a shorter game or less gold, so accepted counts and durations accompany them and do not substitute for wins. Two consumable slots are not guaranteed healing plus mana: dual healing types can still compete for space. Ending equipment and levels depend on duration. The cap intentionally lowers equipment count; this metric is reported rather than a blocking regression. Four other metrics undergo a Bonferroni sweep overall/by class; class n=12 has low power. Crashes invalidate eligibility and interrupted artifacts are preserved. Local results cannot establish field superiority.

## Result

Completed 60 games per arm, six seed clusters, all ten classes. Cap four won **27/60** versus Duelist **24/60** (+5 percentage points). Eight classes had parent games reaching more than four equipment items. No candidate exceeded four. The discovery rule required four additional wins; the observed gain was three, so confirmation was not run. Seeds 64000–64119 remain unobserved.

All 120 replay audits matched every state hash: 1,550,667 ticks and 14,159,036 recorded actions. No VM-failed or incomplete games were scored. All 30 tests passed; maximum observed work/instructions were 5,088/2,897, within 50,000/20,000.

Actual healing purchases rejected for lack of space fell **55,580 → 99**. Accepted healing purchases rose **588 → 884**; healing spend rose **23,060 → 34,920 gold**. Equipment purchases fell **231 → 198** as intended. Candidate decisions were 702,807 versus 692,142 (+1.54%), so the rejection decrease is not explained by a shorter aggregate game duration. These observations support the capacity mechanism; they do not establish a win advantage.

Class wins (parent → candidate, n=6 each): Vanguard 0→0, Ranger 2→3, Arcanist 0→1, Druid 1→1, Demon Hunter 1→1, Death Knight 4→4, Crossbowman 4→4, Lich 4→4, Warlock 3→5, Berserker 5→4. Death totals and gear per class are in the report. Class comparisons are exploratory and cannot select a production class-specific rule from six seeds.

[Full report](../reserve-20260910-report.html), [paired data](../reserve-20260910-result.json), [verification](../reserve-20260910-verification.json). The updated [IR](../hypotheses/reserve.ir.json) retains the tested [BASIC](../hypotheses/reserve.bas) byte for byte. `B_reserve_capacity` records the supported mechanism; `B_reserve` keeps competitive benefit under review.

## Verdict

**Inconclusive for competitive superiority; capacity mechanism observed.** This configuration did not meet the predeclared discovery gate. No confirmation, hosted XP, upload, or league promotion occurred. Do not loosen the threshold or treat the three added wins as confirmed strength. The active league champion remains `aaron-gota-ir-waveguard-r4:v1`, verified live during this study. The user's authorization to promote a validated replacement remains recorded.
