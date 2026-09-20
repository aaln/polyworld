# Richard v135 coaching study — September 20, 2026

No coached variant established a Richard135 win advantage on both colors. The validated blue component wins 40/40; red remains unresolved.

Completed 800 hosted games: 760 passed full replay/all-ten-VM validation; 40 were quarantined for an owned VM instruction-limit failure. All purchased replays were preserved and reconstructed. Invalid games are neither wins nor losses.

Completed 216 native local games. The final combined controller passed its 19,000-instruction gate with 2,018 instructions of measured headroom. Local opponents diagnose behavior and regressions; they are not executable proxies for Richard.

No league policy was changed by this study. The original baseline remains in [retained-baseline](retained-baseline/). The separately verified improvement is saved in [validated-blue-component](validated-blue-component/). Every tested combined IR/BASIC pair, including failures, is under [evaluated](evaluated/).

| Combined policy | Richard: our red | Richard: our blue | Local wins / control |
|---|---:|---:|---:|
| [formation2400](evaluated/formation2400/validation.json) | 0/40 (40 losses, 0 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 7/12 |
| [formation3600](evaluated/formation3600/validation.json) | 0/40 (14 losses, 26 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 7/12 |
| [formation2400_weapon](evaluated/formation2400_weapon/validation.json) | 0/40 (40 losses, 0 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 7/12 |
| [formation2400_breach](evaluated/formation2400_breach/validation.json) | Not submitted | Not submitted | 2/12 vs 7/12 |
| [formation2400_discovery](evaluated/formation2400_discovery/validation.json) | 0/40 (40 losses, 0 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 8/12 |
| [formation4800_cohort](evaluated/formation4800_cohort/validation.json) | 40/40 invalid; rejected | 40/40 (0 losses, 0 draws) | 3/12 vs 7/12 |
| [formation2400_commit](evaluated/formation2400_commit/validation.json) | 0/40 (34 losses, 6 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 8/12 |
| [formation2400_armed](evaluated/formation2400_armed/validation.json) | 0/40 (40 losses, 0 draws) | 40/40 (0 losses, 0 draws) | 2/12 vs 8/12 |
| [formation4800_bounded](evaluated/formation4800_bounded/validation.json) | Not submitted | Not submitted | 3/12 vs 8/12 |
| [formation4800_budget](evaluated/formation4800_budget/validation.json) | 0/40 (39 losses, 1 draws) | 40/40 (0 losses, 0 draws) | 4/12 vs 8/12 |

The deployed control scored 0/40 on each color in both contemporaneous comparison windows. The prospective gate required at least 30/40 wins on **each** color and at least 8 more combined wins than control. Field and survival requirements were retained. Draws score zero.

These are uniform five-versus-five policy matches on release 2026.9.16.5, map 116/seed 54 configuration, against exact `richard-gods-of-the-arena:v135` (`7c370daf-3c5f-42f8-870b-54b79c495a44`). Different seeds often repeat command trajectories; complete command-stream diversity is recorded for every valid cell. Do not treat 40 games as 40 independent trials. No claim of leaderboard #1 or broad field strength follows.

## What the coaching changed

The seven-layer IR now represents an authored late-game transition, four/five-hero readiness, observed enemy dispersion, shared target selection, perimeter entry scoring, synchronized breaches, and a movement tether. The complete bundle was evaluated together. Later revisions added forward discovery when the next objective is unseen, a four-member cohort resistant to a distant fifth ally, remembered home pressure through fog, and ordered equipment across classes.

Perimeter circling is implemented as repeated selection among three exterior approach points. This is an authored approximation of the coaching, not a guarantee of continuous orbiting or avoidance of every tower attack zone. A bounded probe timer can authorize a breach; the replay results determine whether that decision helps.

The first group controller gathered heroes but stopped after an objective disappeared from vision. Native replay reconstruction identified that default-goal stall. A subsequent replay showed nine sampled transitions into or out of defense: lost visibility repeatedly reversed the returning group. A 1,200-tick remembered return corrected that decision mechanism; in its diagnostic game, Richard’s Demon Hunter died six times, but our team still lost. This supports the mechanism observation, not a winning-policy claim.

The delayed cohort exceeded the BASIC instruction limit in all 40 red hosted games. Exact native replay reproduced the first inspected failure at tick 5,274 after 24,936 matching owned commands and every prior state hash. All 40 games were quarantined. A bounded observer then failed the stricter local margin at 19,105 instructions, so it was never uploaded. Coordinating observation and combat budgets reduced the final local maximum to 17,982 without relaxing the gate.

## Why specialization matters

Three historical specialists that beat an older Richard version each went 0/40 on both colors against v135 in the separate 320-game verification. Their older success did not transfer. The current Jordan-tuned recall can cancel a distant return to defend; the earlier, persistent critical warning has a verified blue benefit against Richard135. Red has different classes and routes, and these group-assault changes did not demonstrate the same transfer.

The policy reacts to public observations and remembered sightings. It does not read opponent policy IDs or hidden positions. General player identification and broad leaderboard qualification remain outside this Richard-focused study’s validated results.

## Preserved inputs and reproduction

All 60 captured session files were copied and hash-verified unchanged. The recording was bound to audited episode `ereq_15e13437-273d-4c4f-84cc-162b01b602b4`, historical bound_idle red versus Richard135 blue. The session contained no attached policy; the comparison baseline was explicitly bound to the deployed `be6affd3…` source.

- [Session references](session-references.json)
- [Complete result index](results.json)
- [Captured coaching inputs](session-inputs/)
- [Semantic coaching implementation map](semantic-coaching-map.json)
- [Captured conversion tooling manifest](tooling-manifest.json)
- Raw evidence, replays, native proofs, and frozen plans: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-coaching-20260920`

Each evaluated directory contains primary `policy.py`, semantic `policy.ir.json`, regenerated `policy.bas`, extracted IR, semantics, manifest, and validation. Outcome feedback changed the IR beliefs and evidence; every evaluated BASIC remains byte-identical to its tested source.

To verify every saved pair with the captured repo conversion, from any directory:

```sh
python3 "/Users/aaln/experiments/softmax/polyworld/examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/reproduce.py"
```

This verifies conversion and source parity. The recorded live results are evidence files, not a promise of identical performance against future opponent versions.
