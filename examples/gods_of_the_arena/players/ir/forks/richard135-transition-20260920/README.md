# Richard coaching and conditional promotion check

Reviewed session `2026-09-20t19-10-35-082z64deb6` and reconstructed the exact user episode. All 70 captured files remain unchanged.

Completed 108 local games and 400 hosted games: 240 against Richard v135 and 160 against Alex g002:v1 / Jordan v268. All hosted games passed full replay and all-ten-VM checks. Generated seeds are not paired across hosted arms, and repeated command trajectories are correlated.

| Richard v135 | Red | Blue |
|---|---:|---:|
| Coached baseline | 0/40 | 40/40 |
| transition_freshhit | 0/40 | 40/40 |
| transition_armor_freshhit | 0/40 | 40/40 |

The original both-color Richard gate failed for both final variants. The user subsequently authorized promotion if the unchanged policy beats Alex and Jordan; this is a separate gate, not a relabeling of Richard failure.

Selected unchanged source: `aaron-gota-ir-richard135-transition-freshhit-0920:v1`, `transition_freshhit`.

| Conditional promotion test | Wins | Losses | Draws |
|---|---:|---:|---:|
| transition_freshhit/alex/red | 2 | 24 | 14 |
| transition_freshhit/alex/blue | 0 | 40 | 0 |
| transition_freshhit/jordan/red | 0 | 40 | 0 |
| transition_freshhit/jordan/blue | 0 | 40 | 0 |

Conditional promotion gate: **failed**. Deployment, if eligible, is recorded separately under `promotion-check/deployment`.

The implementation couples finite defense memory, observed-clear offense, a bounded Crossbowman scout, shared Ranger focus, synchronized legal strikes, and fresh-hit movement recovery; an alternative buys armor earlier. Scenario proofs establish command behavior, not combat success. The native engine supplies no gap-closing stun for the chosen strikes.

The original replay has 197/286 sampled emergency decisions without a fresh alarm. The Ranger finishes level 10 with five items; our Death Knight is level 4 with one. Ranger late hit intervals were often nine ticks with post-hit movement. Our Crossbowman had higher nominal damage and range, so raw attack stats alone do not explain the wipe.

The new variants lost earlier on red. Smaller end-game stat gaps or fewer raw deaths therefore do not establish improved scaling or survival. See the full-cohort progression comparison.

Saved primary IR/BASIC pairs: `evaluated/` and `coached-baseline/`. `reproduce.py` verifies every pair using the captured repo conversion; `reproduction-proof.json` was generated from `/tmp`. Failed and superseded versions remain archived.

Study and raw audits: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-transition-20260920`. Session/evidence hashes: `session-references.json`, `captured-inputs.json`, `additional-validation.json`. Layer mapping: `semantic-coaching-map.json`.
