# Druid lane recovery: local admission

This is the practiced snapshot before the fresh 400-game later-draft comparison.
It is not yet a deployment or competitive result. The broader all-class policy
failed its gate and remains preserved in `lane-recovery20260923-hosted`.

Only Druid receives the lane-healing, bounded cooldown wait and useful-shopping
rule. Other heroes retain blue-center's commands. All 582 local checks pass.
Eight fresh main native matches are compared with eight preserved deterministic
local controls; eight non-Druid command streams and terminal states are equal.
Four additional full matches explicitly exercise Ranger and Crossbowman under
both source variants and are exactly equal. No hosted controls are reused.

- [Semantic IR](druid-lane/policy.ir.json) and [generated BASIC](druid-lane/policy.bas).
- [Local results](druid-lane/evidence/local-summary.json), [non-Druid equivalence](druid-lane/evidence/non-druid-equivalence.json), and [ranged equivalence](druid-lane/evidence/ranged-equivalence.json).
- [Frozen hosted plan](druid-lane/evidence/hosted-plan.json) and [capture hashes](druid-lane/evidence/session-input-manifest.json).

Run `python druid-lane/verify.py`. The portable converter supports `compile` and
`extract` and regenerates the exact tested source. Original captures are unchanged.
Source `29f6d7e6`; locally reviewed IR `5af7815f`; binding
`gota-bassy/druid-lane-recovery-2026-09-23-r1`; engine `2026.9.22.3`.
See the [current experiment](../../../../../../games/gods_of_the_arena/experiments/2026-09-23-druid-lane-recovery.md)
for the complete decision rule and later outcome.
