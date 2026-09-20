---
id: 2026-09-20-richard-alex-opponent-ir
policy: Aaron and Coach deployed Jordan268 counter
baseline: conditional population motif predictor
candidate: exact Richard135 and Alex gota-g002-v1 observable motif models
status: confirmed
hypothesis: Opponent-specific visible target and movement preferences predict heldout choices better than a context-conditioned field prior.
decision_rule: At least8 paired-affordance training starts and strictly higher chronological heldout accuracy than population for a supported preference; otherwise provisional. No rollout or winning-policy claim.
evals:
  - kind: existing_episode_reanalysis
    artifact: docs/opponents/richard-v135/evidence.json
  - kind: existing_episode_reanalysis
    artifact: docs/opponents/alex-g002-v1/evidence.json
---

# Observer-grounded Richard135 and Alexg002 IR

User asks an IR analysis to beat exact richard-gods-of-the-arena:v135 and Alex Smith gota-g002:v1. Read-only existing league episodes; no new XP or changes to deployed source. Frozen latest60round metadata, outcome-independent latest20games per exact target, 16training/4chronologicalholdout, 14earlier population games spanning8other versions. One real hero observer(slot0/5), exact currently deployed IR/BASIC and game2026.9.16.5. Source f2ab9598d8f8001b6beae3e66404e341770c803f. Opponent private commands used only to reconstruct audited replay, never predictor features.

## Design and critique

Reuse the frozen Jordan observer semantics and seven motifs. Features come from prior tick and estimated alternate affordances, never current selected action or hidden state. Minimum6ticks sustained motif; first appearances and unestablished choices excluded. Deduplicate training by full observable stream. Holdout is opened only after fit freeze. Compare context population, class-conditioned, side-conditioned and persistence baselines; report coverage, exact repeat trajectories, residual and uncertainty. Relative counts do not identify private goals or executable rules; opposing-team adaptation and deception are unproven. Parameterized evaluator preserves previous study code.

If opponent preferences help, prediction lift appears on the chronological holdout; if no lift, demote statements. Even positive lift does not validate a live proxy or competitive counter. Counterstrategy stays proposed until real-reacting rival tests pass existing frozen competitive gates. Mixed classes, few unique full trajectories and selection among visible situations constrain transfer. Latest holdout does not prove future-version transfer. Match outcomes are observational context, not controlled intervention evidence.

## Result

Completed using existing episodes only; no XP requests were created. Both targets won 20/20 selected games against the exact deployed executable. All replay state hashes, episode rosters and 10 active VMs per episode were verified. The native observer exposes one real policy instance's predecision view, with no teammate pooling or private opponent VM features.

Richard: 694/923 heldout choices correct (75.2%), versus population 502/923 (54.4%); side-conditioned baseline 64.7%. Novel observer streams score 322/422 (76.3%) versus 50.2% population. Visible coverage is 18.3% of living opponent ticks. Structure-over-creep preference O13 has 338/583 paired training starts and 140/226 correct heldout predictions, versus 83/226 for population.

Alex: 210/287 (73.2%), versus population 195/287 (67.9%); side-conditioned baseline 69.7%. Visible coverage is 44.0%. All heldout streams exactly repeat training streams; novel-trajectory generalization is untested and the descriptive three-cluster lift interval includes zero. Contextual preferences O07/O11/O15 meet the pre-registered count and relative-lift rule, but their heldout counts are small and correlated. No universal structure-first priority is established.

Post-fit descriptive analysis, excluded from predictive features: in all 12 distinct Alex training streams, all five friendly heroes are alive beyond 28 tiles when the first visible enemy pair reaches within 24 tiles of our god. At t2520 in the representative red game, all five own VMs record defCount=5 but defActive=0 and continue attacking remote structures. First god damage occurs at t2533, defeat at t2583. Richard blue similarly has defCount=2 and inactive defense at t5760, first god damage at t5778 and defeat at t5803. Richard red includes a late response that still loses, so recall alone is not established as sufficient.

The exact deployed source reproduced 93,288 own commands across the four representative games. Both Python models pass primary seven-layer layout checks; all 1,210 archived heldout forecasts reproduce exactly. Merging both belief patches into a copy of primary IR preserves BASIC SHA be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73. Eight observer/semantic unit checks pass. Model manifests and compatibility receipts are archived with each report.

## Verdict

Confirmed **only under the pre-registered relative prediction rule**: both models contain preferences meeting n>=8 and strictly positive chronological heldout lift. This is an observational forecast result, not a competitive policy result. Richard's novel-stream subset adds evidence within this lineup; Alex's transfer to a novel trajectory remains inconclusive. Three heldout clusters per target are insufficient for strong population inference. No proxy was executed (rollouts=0; usable=False).

Deliver the primary-format Python models and proposed counter rules to the existing single autoresearcher. The leading experiment is a bounded critical-defense commitment that can override the 28-tile recall cancellation, with earlier interception and a separate red combat diagnosis. The existing Richard Critical60 screen is blue 4/4 but red 0/4; it is not an accepted joint counter. Require prospective Richard/Alex/Jordan and broad-field gates for one final executable. No live policy changed; no rollback is needed for this read-only analysis. A policy that beats all targets remains unresolved.
