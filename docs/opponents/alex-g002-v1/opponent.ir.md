# gota-g002:v1 — individual opponent IR

Python: [alex_g002_v1.py](../../../examples/gods_of_the_arena/players/ir/opponents/alex_g002_v1.py). The same seven layers and `id / when / skill / for` records as our primary IR; observable forecasting binding, not opponent source code.

**Main finding:** Alex produces a fast core attack that our counterrace policy sees but declines to answer. In all 12 distinct training streams, the first visible enemy pair within 24 tiles of our god arrives while all five friendly heroes are alive farther than 28 tiles away. This is a counted defensive failure, not proof of Alex’s hidden intent.

## Identity, evidence and visibility

Exact version `a30542cb-54de-4109-92e6-bcabca7db4d8`; individual model. Current own BASIC `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. 20 target games, 16 training / 4 chronological heldout; outcomes were ignored during selection. Date range 2026-09-20T10:05:15.574199Z–2026-09-20T15:05:15.005282Z. Opponent wins 20/20 in this observational sample.
Training has 12 distinct complete observer streams; heldout has 3. Visibility: 122,795/278,829 living opponent hero-ticks (44.0%). Observer dead fraction 0.0%; unsegmented residual 3.0% of visible hero-ticks.
The observer is one actual owned hero instance, slot 0 or 5. No pooled teammate viewpoints. Targets outside its object list are masked; unseen is unknown, not dead. Every original replay tick/hash and action consumption is verified; game logs report 10/10 VMs active in all 34 target and population episodes.

## Inferred skills

| Motif | Starts in distinct training | Ticks | Median duration |
|---|---:|---:|---:|
| target_hero | 68 | 2521 | 36.0 |
| target_creep | 561 | 7129 | 9 |
| target_structure | 473 | 58455 | 97 |
| advance | 72 | 2855 | 49.0 |
| withdraw | 18 | 371 | 16.0 |
| lateral | 6 | 108 | 18.0 |
| hold | 30 | 369 | 9.0 |

Every motif has counted initiation contexts, termination reasons and concurrent movement in evidence.json. Target means visible pursuit/retained target, not necessarily an attack. Advance/withdraw are radial geometry relative to our god; hold can be turning/collision. Six-tick minimum segments; spells/private cooldowns are outside the inferred skill set.

## Preferences and prediction records

Each confidence is the smoothed paired-affordance selection frequency, not certainty about intent. Both named alternatives must be locally estimated available at t−1. `supported` means relative forecast lift in this sample; it does not establish an exploitable weakness. Sparse or non-improving statements remain provisional.

| ID | Situation | Prefer → over | Chosen/n | Confidence | Population base rate (n) | Heldout correct/n; baseline | Status |
|---|---|---|---:|---:|---|---|---|
| AlexG002v1_I_O07 | nearby=our hero + our creep; no nearby exposed structure; visible HP >100 | target_hero → target_creep | 12/12 | 0.929 | 13.3% (1028) | 2/2; 0/2 | supported |
| AlexG002v1_I_O11 | nearby=our hero + our exposed structure; no nearby creep; visible HP >100 | target_structure → target_hero | 25/33 | 0.743 | 27.0% (122) | 4/6; 0/6 | supported |
| AlexG002v1_I_O15 | nearby=our hero + our creep + our exposed structure; visible HP >100 | target_hero → target_creep | 50/69 | 0.718 | 33.3% (84) | 9/14; 0/14 | supported |
| AlexG002v1_I_O05 | nearby=our creep; no nearby hero/exposed structure; visible HP >100 | target_creep → hold | 139/139 | 0.993 | 97.9% (334) | 40/40; 40/40 | provisional |
| AlexG002v1_I_O13 | nearby=our creep + our exposed structure; no nearby hero; visible HP >100 | target_creep → target_structure | 294/423 | 0.694 | 72.8% (371) | 108/144; 108/144 | provisional |
| AlexG002v1_I_O09 | nearby=our exposed structure; no nearby hero/creep; visible HP >100 | target_structure → hold | 126/234 | 0.538 | 56.8% (222) | 47/81; 47/81 | provisional |

Full records in the Python belief layer include model level, exact opponent identity, last observed episode/tick, supporting episode count, prediction intervals and evidence examples. Confidence-sorted supported/provisional rows above are retained together so failed hypotheses remain inspectable.

## Goals and beliefs — hypotheses

Conditional structure contact over hero contact is suggested by AlexG002v1_I_O11 (25/33 training; 4/6 heldout), with very little heldout evidence. O15 favors hero contact when all three target categories are nearby (50/69 training; 9/14 heldout). O13’s creep preference is no more predictive than population. No universal structure-first or hero-ignoring rule is inferred.
Goals are interpretations linked to preference IDs and counts in MODEL.goal. No second-order opponent beliefs are inferred: distinguishable tests n=0, confidence unestimated, predictions 0.

## Adaptation, constraints and deception

Same-context training choices are split by episode midpoint, chronological halves and whether our visible units target the opponent; all counts are in evidence.json/adaptation. These descriptive shifts do not isolate causal adaptation from class, position or game phase. Causal adaptation established=False. Deception tests 0; no deception claim.
Excluded starts: {"left_censored": 530, "selected_skill_not_established_by_prior_affordances": 9}. Ineligible affordances and left-censored first appearances never enter preference counts. No hidden cooldown or gold inference.

## Heldout validation

| Predictor | Correct / eligible | Accuracy |
|---|---:|---:|
| Individual IR | 210/287 | 73.2% |
| Context population | 195/287 | 67.9% |
| Population + class | 190/287 | 66.2% |
| Population + side | 200/287 | 69.7% |
| Previous motif persists | — | 48.1% |

Novel-stream heldout: 0/0, unscored; population unscored. Exact observer-stream novelty is not statistical independence. Cluster uncertainty: `{"clusters": 3, "lift_95pct": [0.0, 0.1875], "method": "2000 bootstrap resamples of distinct full observer trajectories; descriptive with few clusters"}`.
**Every Alex heldout stream exactly matches a training stream.** The small lift is descriptive replay prediction, not evidence of generalization to a new trajectory; the cluster interval includes zero. No Alex tendency qualifies as a validated exploit.
No proxy controller was executed: rollouts 0, divergence unmeasured, usable=False. Motif prediction is conditioned on retrospectively identified boundaries; it predicts neither skill onset timing nor action arguments.

## Our policy failure and proposed counters

Representative red replay: at t2520 all five agents record defCount=5 and defAnchor=1, yet defActive=0/defUntil=0 and continue attacking remote structures. First god damage is t2533; defeat t2583. On blue, t3000 samples also show defCount=4 and canceled defense; first god damage t3108, defeat t3126. The 28-tile remote-recall cancellation is an actionable own-policy decision problem, not a failure to observe the push.
The exact deployed BASIC reconstructed all own commands and state hashes in representative red and blue games. See own-decision-analysis.json; memories are actual 120-tick samples and are never interpolated. Macro counts are descriptive training analysis added after fit; they did not enter the heldout predictor.

- `AlexG002v1_I_C01` (proposed_test_only): Allow a bounded critical-defense commitment to override the 28-tile distant-recall cancellation; evaluate earlier warning distance and assigned responder travel. Test: Fresh pinned Richard135 AND Alexg002 candidate/control 40 per color, >=30/40 each target/color; retain Jordan268 >=38/40 each and original field guard. Full source, VM and replay audits. Draws count zero.
- `AlexG002v1_I_C02` (diagnostic_proposal): Test interception at the threatened inner structure, before the god becomes the active target. Visible late god burn leaves very little travel time; a defender who only chases heroes can still allow structure pressure. Test: Record arrival time, enemy structure-target duration, friendly survival and actual fort wins. Use real reacting opponent; the observational model is not a rollout controller.

These are reviewable primary-strategy proposals in PROPOSED_RULES, not adopted live-policy changes. Richard, Alex and Jordan gates must pass together.

## Unglossed and provenance

Observer-relative advance, absolute low HP, estimated opponent affordances, visible target versus actual attack, and concurrent target/motion remain explicit local glossary extensions. They occur on every annotated sustained start and do not silently change the primary policy glossary.
Sources: study-plan.json, model-freeze.json, evidence.json, macro-observations.json, own-decision-analysis.json, observer-policy.ir.json, population.ir.md, full annotated observations.jsonl.gz and heldout-predictions.jsonl.gz. Every observation includes episode/tick, visibility, alternatives, selected motif and visible outcome. Exact guide snapshot and artifact hashes are preserved.

| Split | Created UTC | Observer slot | Episode |
|---|---|---:|---|
| train | 2026-09-20T10:05:15.574199Z | 5 | [ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002) |
| train | 2026-09-20T10:17:15.134651Z | 0 | [ereq_d79c3904-1962-4bf9-baef-246cccbe6c17](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_d79c3904-1962-4bf9-baef-246cccbe6c17) |
| train | 2026-09-20T10:29:15.630594Z | 5 | [ereq_ab17782d-44c9-4a10-9b8c-c7764afc88c4](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_ab17782d-44c9-4a10-9b8c-c7764afc88c4) |
| train | 2026-09-20T10:41:15.216854Z | 0 | [ereq_87ba2957-57de-4aac-8867-1cf86b06d5f4](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_87ba2957-57de-4aac-8867-1cf86b06d5f4) |
| train | 2026-09-20T11:17:15.291515Z | 5 | [ereq_0e7a53dc-0e61-471f-a885-c5c0e4862099](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_0e7a53dc-0e61-471f-a885-c5c0e4862099) |
| train | 2026-09-20T11:41:14.904074Z | 5 | [ereq_05233fc8-db19-44c1-984a-69fdc33bba46](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_05233fc8-db19-44c1-984a-69fdc33bba46) |
| train | 2026-09-20T11:41:15.125976Z | 0 | [ereq_b2234f67-1d36-4c31-825b-09551474a6f0](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_b2234f67-1d36-4c31-825b-09551474a6f0) |
| train | 2026-09-20T11:53:15.766504Z | 0 | [ereq_0dfea382-21eb-4746-ab1d-f9dca400692f](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_0dfea382-21eb-4746-ab1d-f9dca400692f) |
| train | 2026-09-20T12:05:15.124480Z | 5 | [ereq_e15c0bbb-478e-4ac3-9658-5972654f596e](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_e15c0bbb-478e-4ac3-9658-5972654f596e) |
| train | 2026-09-20T12:29:14.882228Z | 0 | [ereq_8419afa2-fbf1-48f2-9083-0c120c9c530c](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_8419afa2-fbf1-48f2-9083-0c120c9c530c) |
| train | 2026-09-20T12:41:15.077515Z | 5 | [ereq_f1f1e89b-2626-4767-810a-de580832917b](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_f1f1e89b-2626-4767-810a-de580832917b) |
| train | 2026-09-20T12:53:15.209024Z | 0 | [ereq_1db2a887-6854-45d4-accc-e3f0d32d3fc3](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_1db2a887-6854-45d4-accc-e3f0d32d3fc3) |
| train | 2026-09-20T12:53:15.242709Z | 0 | [ereq_38049079-023c-40e5-8a1c-6881ce343817](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_38049079-023c-40e5-8a1c-6881ce343817) |
| train | 2026-09-20T13:29:15.648947Z | 5 | [ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad) |
| train | 2026-09-20T13:29:15.728461Z | 0 | [ereq_3e335c98-b3b2-4a5f-971e-f91cadf9f80b](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_3e335c98-b3b2-4a5f-971e-f91cadf9f80b) |
| train | 2026-09-20T13:53:15.131568Z | 5 | [ereq_68bd647e-fbbb-435d-a6f2-6e3a3bd9d9b8](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_68bd647e-fbbb-435d-a6f2-6e3a3bd9d9b8) |
| heldout | 2026-09-20T14:05:15.141042Z | 5 | [ereq_4f7e1a91-1c8c-4491-a68b-2542cc199310](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_4f7e1a91-1c8c-4491-a68b-2542cc199310) |
| heldout | 2026-09-20T14:05:15.184283Z | 0 | [ereq_35302c57-b5cf-42aa-ad0c-b99ab2859a25](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_35302c57-b5cf-42aa-ad0c-b99ab2859a25) |
| heldout | 2026-09-20T14:41:14.974145Z | 0 | [ereq_50eb06e1-c98a-4d16-bf07-fe5d6ce4f80c](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_50eb06e1-c98a-4d16-bf07-fe5d6ce4f80c) |
| heldout | 2026-09-20T15:05:15.005282Z | 0 | [ereq_5af9a53a-af97-4cfe-9fb2-e997497424cb](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_5af9a53a-af97-4cfe-9fb2-e997497424cb) |
