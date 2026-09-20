# richard-gods-of-the-arena:v135 — individual opponent IR

Python: [richard_v135.py](../../../examples/gods_of_the_arena/players/ir/opponents/richard_v135.py). The same seven layers and `id / when / skill / for` records as our primary IR; observable forecasting binding, not opponent source code.

**Main finding:** Richard maintains structure pressure while contesting heroes. In the creep-and-structure context, the model predicts structure targeting on 140/226 heldout starts, versus 83/226 correct for the population predictor. Our blue defense fails against a visible two-hero core attack; red also loses combat.

## Identity, evidence and visibility

Exact version `7c370daf-3c5f-42f8-870b-54b79c495a44`; individual model. Current own BASIC `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. 20 target games, 16 training / 4 chronological heldout; outcomes were ignored during selection. Date range 2026-09-20T11:17:15.211091Z–2026-09-20T14:53:15.084906Z. Opponent wins 20/20 in this observational sample.
Training has 11 distinct complete observer streams; heldout has 3. Visibility: 110,180/600,830 living opponent hero-ticks (18.3%). Observer dead fraction 14.6%; unsegmented residual 10.0% of visible hero-ticks.
The observer is one actual owned hero instance, slot 0 or 5. No pooled teammate viewpoints. Targets outside its object list are masked; unseen is unknown, not dead. Every original replay tick/hash and action consumption is verified; game logs report 10/10 VMs active in all 34 target and population episodes.

## Inferred skills

| Motif | Starts in distinct training | Ticks | Median duration |
|---|---:|---:|---:|
| target_hero | 893 | 15472 | 12 |
| target_creep | 1052 | 13725 | 11.0 |
| target_structure | 978 | 15261 | 10.0 |
| advance | 132 | 9410 | 52.0 |
| withdraw | 14 | 406 | 29.0 |
| lateral | 15 | 1162 | 104 |
| hold | 32 | 611 | 8.0 |

Every motif has counted initiation contexts, termination reasons and concurrent movement in evidence.json. Target means visible pursuit/retained target, not necessarily an attack. Advance/withdraw are radial geometry relative to our god; hold can be turning/collision. Six-tick minimum segments; spells/private cooldowns are outside the inferred skill set.

## Preferences and prediction records

Each confidence is the smoothed paired-affordance selection frequency, not certainty about intent. Both named alternatives must be locally estimated available at t−1. `supported` means relative forecast lift in this sample; it does not establish an exploitable weakness. Sparse or non-improving statements remain provisional.

| ID | Situation | Prefer → over | Chosen/n | Confidence | Population base rate (n) | Heldout correct/n; baseline | Status |
|---|---|---|---:|---:|---|---|---|
| Richard135_I_O03 | nearby=our hero; no nearby creep/exposed structure; visible HP >100 | target_hero → hold | 357/357 | 0.997 | 26.4% (307) | 128/128; 0/128 | supported |
| Richard135_I_O04 | nearby=our hero; no nearby creep/exposed structure; visible HP ≤100 | target_hero → hold | 8/8 | 0.900 | 0.0% (61) | 3/3; 0/3 | supported |
| Richard135_I_O15 | nearby=our hero + our creep + our exposed structure; visible HP >100 | target_hero → target_creep | 14/22 | 0.625 | 33.3% (84) | 4/6; 0/6 | supported |
| Richard135_I_O13 | nearby=our creep + our exposed structure; no nearby hero; visible HP >100 | target_structure → target_creep | 338/583 | 0.579 | 16.2% (371) | 140/226; 83/226 | supported |
| Richard135_I_O09 | nearby=our exposed structure; no nearby hero/creep; visible HP >100 | target_structure → hold | 564/578 | 0.974 | 56.8% (222) | 201/207; 201/207 | provisional |
| Richard135_I_O06 | nearby=our creep; no nearby hero/exposed structure; visible HP ≤100 | hold → target_creep | 7/7 | 0.889 | 0.0% (3) | 0/3; 0/3 | provisional |
| Richard135_I_O11 | nearby=our hero + our exposed structure; no nearby creep; visible HP >100 | target_hero → target_structure | 67/82 | 0.810 | 41.0% (122) | 17/21; 17/21 | provisional |
| Richard135_I_O05 | nearby=our creep; no nearby hero/exposed structure; visible HP >100 | target_creep → hold | 270/334 | 0.807 | 97.9% (334) | 80/106; 80/106 | provisional |
| Richard135_I_O07 | nearby=our hero + our creep; no nearby exposed structure; visible HP >100 | target_creep → hold | 339/653 | 0.519 | 54.7% (1028) | 121/223; 121/223 | provisional |

Full records in the Python belief layer include model level, exact opponent identity, last observed episode/tick, supporting episode count, prediction intervals and evidence examples. Confidence-sorted supported/provisional rows above are retained together so failed hypotheses remain inspectable.

## Goals and beliefs — hypotheses

Conditional structure pressure over creep contact is supported by Richard135_I_O13. Hero contact over holding is supported by O03; hero versus structure O11 adds no lift over population and remains provisional. These contexts do not establish a universal goal order.
Goals are interpretations linked to preference IDs and counts in MODEL.goal. No second-order opponent beliefs are inferred: distinguishable tests n=0, confidence unestimated, predictions 0.

## Adaptation, constraints and deception

Same-context training choices are split by episode midpoint, chronological halves and whether our visible units target the opponent; all counts are in evidence.json/adaptation. These descriptive shifts do not isolate causal adaptation from class, position or game phase. Causal adaptation established=False. Deception tests 0; no deception claim.
Excluded starts: {"left_censored": 820, "selected_skill_not_established_by_prior_affordances": 54}. Ineligible affordances and left-censored first appearances never enter preference counts. No hidden cooldown or gold inference.

## Heldout validation

| Predictor | Correct / eligible | Accuracy |
|---|---:|---:|
| Individual IR | 694/923 | 75.2% |
| Context population | 502/923 | 54.4% |
| Population + class | 461/923 | 49.9% |
| Population + side | 597/923 | 64.7% |
| Previous motif persists | — | 15.7% |

Novel-stream heldout: 322/422, 76.3%; population 50.2%. Exact observer-stream novelty is not statistical independence. Cluster uncertainty: `{"clusters": 3, "lift_95pct": [0.09375, 0.26066350710900477], "method": "2000 bootstrap resamples of distinct full observer trajectories; descriptive with few clusters"}`.
Richard has some novel heldout observer streams, but only three heldout trajectory clusters total; transfer beyond these lineups remains unproven.
No proxy controller was executed: rollouts 0, divergence unmeasured, usable=False. Motif prediction is conditioned on retrospectively identified boundaries; it predicts neither skill onset timing nor action arguments.

## Our policy failure and proposed counters

In 7/7 distinct training streams where the first god damage is visible, no living friendly hero is within 28 tiles. Representative blue replay: at t5760 all five decisions have defCount=2, defActive=0 and defUntil=0; first observed god damage is t5778. Critical60’s existing 4/4 blue screen is encouraging but red remains 0/4, and neither Alex nor Jordan preservation is established.
The exact deployed BASIC reconstructed all own commands and state hashes in representative red and blue games. See own-decision-analysis.json; memories are actual 120-tick samples and are never interpolated. Macro counts are descriptive training analysis added after fit; they did not enter the heldout predictor.

- `Richard135_I_C01` (proposed_test_only): Allow a bounded critical-defense commitment to override the 28-tile distant-recall cancellation; evaluate earlier warning distance and assigned responder travel. Test: Fresh pinned Richard135 AND Alexg002 candidate/control 40 per color, >=30/40 each target/color; retain Jordan268 >=38/40 each and original field guard. Full source, VM and replay audits. Draws count zero.
- `Richard135_I_C02` (diagnostic_proposal): Repair red combat/economy after timely response. Test support and wave participation; the existing red equipment-only screen 0/4 already refutes sufficiency of that tested variant. Test: Record arrival time, enemy structure-target duration, friendly survival and actual fort wins. Use real reacting opponent; the observational model is not a rollout controller.

These are reviewable primary-strategy proposals in PROPOSED_RULES, not adopted live-policy changes. Richard, Alex and Jordan gates must pass together.

## Unglossed and provenance

Observer-relative advance, absolute low HP, estimated opponent affordances, visible target versus actual attack, and concurrent target/motion remain explicit local glossary extensions. They occur on every annotated sustained start and do not silently change the primary policy glossary.
Sources: study-plan.json, model-freeze.json, evidence.json, macro-observations.json, own-decision-analysis.json, observer-policy.ir.json, population.ir.md, full annotated observations.jsonl.gz and heldout-predictions.jsonl.gz. Every observation includes episode/tick, visibility, alternatives, selected motif and visible outcome. Exact guide snapshot and artifact hashes are preserved.

| Split | Created UTC | Observer slot | Episode |
|---|---|---:|---|
| train | 2026-09-20T11:17:15.211091Z | 0 | [ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686) |
| train | 2026-09-20T11:29:15.149454Z | 0 | [ereq_e257144c-f78b-42b2-a1c2-91f72688e149](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_e257144c-f78b-42b2-a1c2-91f72688e149) |
| train | 2026-09-20T11:29:15.338071Z | 5 | [ereq_e766eb57-1ad0-4546-80a5-bdd686a83c94](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_e766eb57-1ad0-4546-80a5-bdd686a83c94) |
| train | 2026-09-20T11:41:15.017582Z | 5 | [ereq_63a9c85f-e010-4dfc-ab10-132d7851a6b3](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_63a9c85f-e010-4dfc-ab10-132d7851a6b3) |
| train | 2026-09-20T11:41:15.216882Z | 5 | [ereq_a722338b-035d-490f-afff-c84c6d068a2f](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_a722338b-035d-490f-afff-c84c6d068a2f) |
| train | 2026-09-20T12:05:15.072102Z | 5 | [ereq_63b9dc35-3a06-4cb0-bec9-2714e5a8497e](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_63b9dc35-3a06-4cb0-bec9-2714e5a8497e) |
| train | 2026-09-20T12:05:15.761285Z | 0 | [ereq_9b1e762c-67f5-4615-8da9-360c3f88e3c5](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_9b1e762c-67f5-4615-8da9-360c3f88e3c5) |
| train | 2026-09-20T12:17:14.949496Z | 5 | [ereq_a1d89da2-92f0-4f99-8c7a-f6d2f78f2456](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_a1d89da2-92f0-4f99-8c7a-f6d2f78f2456) |
| train | 2026-09-20T12:29:15.013560Z | 5 | [ereq_98733159-21b5-4368-9438-c9a06f44afe5](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_98733159-21b5-4368-9438-c9a06f44afe5) |
| train | 2026-09-20T12:41:14.925813Z | 5 | [ereq_a8957880-c86e-4554-b5eb-5b42f212a6d9](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_a8957880-c86e-4554-b5eb-5b42f212a6d9) |
| train | 2026-09-20T12:53:15.373471Z | 0 | [ereq_0f8bc91a-ca6c-4790-bde9-53c5a33a8f0e](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_0f8bc91a-ca6c-4790-bde9-53c5a33a8f0e) |
| train | 2026-09-20T13:29:15.609882Z | 0 | [ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2) |
| train | 2026-09-20T13:29:15.824610Z | 5 | [ereq_369b0b03-2176-448d-9301-387763b3fe94](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_369b0b03-2176-448d-9301-387763b3fe94) |
| train | 2026-09-20T13:41:15.362427Z | 5 | [ereq_7b4ed477-df6b-467c-ac97-d39250e5fd45](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_7b4ed477-df6b-467c-ac97-d39250e5fd45) |
| train | 2026-09-20T13:41:15.589268Z | 5 | [ereq_7e7e399d-85f5-4da6-a037-73b974e73c4c](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_7e7e399d-85f5-4da6-a037-73b974e73c4c) |
| train | 2026-09-20T14:17:15.351923Z | 5 | [ereq_f5415108-acba-4219-b116-0606afd7b3c9](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_f5415108-acba-4219-b116-0606afd7b3c9) |
| heldout | 2026-09-20T14:41:14.995080Z | 5 | [ereq_38c2dfb5-a988-4ac1-81ef-2226fa9b205a](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_38c2dfb5-a988-4ac1-81ef-2226fa9b205a) |
| heldout | 2026-09-20T14:41:15.062300Z | 5 | [ereq_74cd8109-1bf0-4eed-b095-0345eb0a774c](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_74cd8109-1bf0-4eed-b095-0345eb0a774c) |
| heldout | 2026-09-20T14:53:14.920013Z | 0 | [ereq_5cb288d2-608c-4ad5-aec9-22c5eedfaed0](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_5cb288d2-608c-4ad5-aec9-22c5eedfaed0) |
| heldout | 2026-09-20T14:53:15.084906Z | 5 | [ereq_c2cfaf27-ac5d-4efb-8f2c-e929db3432d9](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_c2cfaf27-ac5d-4efb-8f2c-e929db3432d9) |
