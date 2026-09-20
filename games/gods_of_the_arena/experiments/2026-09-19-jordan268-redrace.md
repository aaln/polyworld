---
id: 2026-09-19-jordan268-redrace
policy: aaron-gota-ir-jordan268-counter
baseline: aaron-gota-ir-j268-counterrace-0920:v1
candidate: redrace
status: confirmed
hypothesis: "Apply nearby-only defense recall to red to preserve the three heroes already advancing on the other lane."
decision_rule: "Four fresh red games versus exact Jordan268; advance at >=3/4 wins against the frozen counterrace red14/40. Require blue command parity. Frozen finalist needs >=30/40 fresh wins each color."
evals: ["xreq_8b67b844-c477-493c-9fc7-00574651b810", "xreq_e44410f4-5dd2-4ff9-9dc9-f7ba436eb35a", "xreq_f216ad2f-904d-4999-a879-c4646d23ceab"]
---

# Hypothesis

The observed Jordan IR favors hero contact in O15 mixed opportunities. Red confirmation produced14/40 wins with the initial waveclear lever. In audited loss ereq_4e76d241-52c8-4151-958d-9c35e768c8f2, three heroes approach the opposite lane then recall; sampled active-defense decisions without a target are53/79 for DeathKnight,59/78 for Lich,57/80 for Warlock. The whole policy replay matches55,779 owned commands. Preserve this distant group's offensive pressure, analogous to the separately screened blue counterrace.

# Design and critique

Checked closed_levers.md and the completed red confirmation. Do not repeat opening assembly. Branch from frozen counterrace, modifying only red remote recall eligibility: beyond28tiles of the friendly god, clear group defense before ordinary target selection. All blue code, target-kind priority, attack, route and item decisions remain as in the parent. Nearby red heroes retain original defense. Use a named full-source native operator and prove full blue command parity on the earlier blue win. No new candidate test until the current blue confirmation drains and is fully audited.

Four-game directional screen, full ten-seat fixed lineup against exact Jordan268, same published .5 release and map/config. Compare to disclosed earlier14/40 red cohort; generated seeds are not matched. Sampled decisions are correlated, not independent examples; no bound N floor exists. Main counterarguments: red's three offensive classes may race poorly, or nearby-only defense may protect the god too late. A blue win mechanism is not automatically transferable across classes. More attacks is not success without a fort win.

# Predictions and decision rule

If true: distant red heroes continue attacking instead of crossing the map and earn at least3/4 wins (directional gate). If false/backwards: they fail to threaten the enemy god and earn at most1/4;2/4 inconclusive. Only advance at3/4 or4/4, then freeze the same artifact for40fresh games/color and require at least30/40 each to meet the original scoped criterion. Do not pool older screens or parent confirmations with that finalist. Audit all10VMs, complete replay state hashes/actions, roster, build, scores and totalXP. No league promotion.

# Result

Screen red4/4 wins, all four replay/VM/roster/score/XP audits passed. Blue replay parity passed16,024 commands on the parent win; local2,400tick runtime smoke passed allten VMs. Advancement gate passes. Freeze exact BASIC be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73 for fresh40games/color confirmation.

# Verdict

Confirmed against the preregistered narrow criterion: fresh red40/40 and blue40/40 wins for the same frozen BASIC/version. All80complete state-hash/action replay,10VM, roster/build/config, score and totalXP audits passed. Screens were excluded from confirmation. Repeated trajectory signatures prevent treating these as80independent maps. The deliverable is the isolated native Python IR/JSON/BASIC bundle and owned experimental version00cd9483-0309-4613-bf61-89f3f4a33d01. No league promotion. The original primary remains the rollback source53f15b12-2198-41d1-bb99-df4bdb1ff7fd.

Confirmation interim: red40/40 wins; all40full replay/VM/roster/score/XP audits passed. Fresh blue confirmation follows; do not count the parent blue cohort as this finalist’s confirmation.

Final result: both confirmation arms complete. Red40/40, blue40/40. Same tested source SHA be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73. Selected before these arms; no policy changes during confirmation.
