# GOTA repair results

Updated 2026-09-20T17:22:40.912431+00:00. Exact Richard v135 and Alex g002:v1 remain the targets; Jordan preservation is mandatory.

**No tested repair in this ledger qualifies as the combined solution.** The red caster-transit component improved local play and beat the accepted ancestor 40/40 on both colors, but lost every one of its 40 Richard135 red games. Broad defensive recall hurt general play. Standalone caster support was inactive in the fresh gameplay screen despite passing activation fixtures.

| Repair | Measured result and decision |
|---|---|
| [40-tile critical recall](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-counter-20260920/hosted/screen/critical40/red/result.json) | Small Richard screen: red 0/4, blue 2/4. Insufficient; no promotion. |
| [60-tile critical recall](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-counter-20260920/hosted/screen/critical60/red/result.json) | Richard blue 4/4, red 0/4; local 1/12 versus deployed 6/12, deaths 329 versus 61. Reject this broad variant. |
| [Red weapon-first equipment](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-counter-20260920/hosted/screen/weapon/red/result.json) | Richard red 0/4. No gain in this screen; no promotion. |
| [Static middle Warlock plus critical recall](/Users/aaln/experiments/softmax/gota-autoresearch/forks/fork_20260920_045449_29b23b/richard_middle_cached_v2/screen/result.json) | 1/12 local wins versus 6/12 deployed, deaths 310 versus 61. Reject the exact combination. |
| [One-time red caster transit](/Users/aaln/experiments/softmax/gota-autoresearch/forks/fork_20260920_045449_29b23b/middle_transit_v4/hosted-discovery/parent-red/result.json) | Local 30/32 versus 16/32; hosted accepted-ancestor 40/40 both colors, Richard135 red 0/40. Useful local component; insufficient target repair. |
| [Transit plus 240-tick blue response](/Users/aaln/experiments/softmax/gota-autoresearch/forks/fork_20260920_045449_29b23b/scoped_core_response_v3/screen/result.json) | 9/16 versus transit 15/16; blue 1/8 versus 7/8 and deaths 193 versus deployed 103. Reject. |
| [Transit plus 720-tick blue response](/Users/aaln/experiments/softmax/gota-autoresearch/forks/fork_20260920_045449_29b23b/scoped_core_response_v3/screen/result.json) | 9/16 versus transit 15/16; blue 1/8 versus 7/8 and deaths 261 versus deployed 103. Reject. |
| [Restore anchored idle caster support](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/support-repairs-20260920/REPORT.md) | 3/6, matching deployed; every game command identical. No expanded support in all three red games. Reject standalone restoration. |
| [Restore unanchored idle caster support](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/support-repairs-20260920/REPORT.md) | 3/6, matching deployed; every game command identical. No expanded support in all three red games. Reject standalone restoration. |

## What the tests establish

- Moving red casters through the middle changes behavior and improves the measured owned-reference matchups. It does not yet solve Richard135.
- Increasing recall broadly can turn a favorable target screen into a large field regression. Both response duration variants dropped from the transit control’s 7/8 blue wins to 1/8.
- Restoring an assistance rule behind existing defense/idle gates can add code without changing gameplay. Both fresh support variants reproduced every canonical command in all six cases, with zero expanded support in six complete red source reconstructions.
- The historical anchor reference improved the new local sample from 3/6 to 4/6 but raised deaths from 25 to 39, above the frozen limit of 30. Its known exact-Alex red weakness remains.

## Evidence and interpretation

The isolated interactive study ran 24 new complete native games, real-VM activation/negative/dense-class checks and complete source reconstructions for all six repaired red games. Those reconstructions matched 108,938 own commands and every state hash. The supervised researcher separately completed and audited 120 hosted component-discovery games. This ledger recomputes result totals and checks the linked replay/VM receipts; original plans, failures and source identities remain intact.

[Detailed support experiment](/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/support-repairs-20260920/REPORT.md) · [Machine-readable ledger](ledger.json) · [Opponent IR analysis](/Users/aaln/experiments/softmax/polyworld/docs/opponents/richard-alex-20260920/analysis.md)

These local screens and repeated fixed-lineup trajectories are not independent league trials. Fresh current-control comparisons, Richard/Alex/Jordan on both colors and broad-field checks remain required for one final executable. The current live policies are unchanged by the interactive study.

The next useful tests must alter actual response timing, allocation or the interaction with transit. The existing supervised worker owns those followups and all hosted requests. Rerun `tools/gota_autoresearch/repair_ledger.py` after audited results change; it never creates requests or changes policies.
