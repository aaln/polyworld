# Hosted microplay verification — 2026-09-20

The enhanced policy was inactive in this hosted study; field improvement is not verified.

120 XP games used nine frozen other players, with each subject policy occupying all ten seats four times. Every complete replay, subject command sequence, and hosted VM status passed.

| Arm | Games | Target changes | Basic hits | Self deaths | Other ally deaths | Crowded decisions |
|---|---:|---:|---:|---:|---:|---:|
| parent | 40 | 0 | 5328 | 110 | 658 | 87.0% |
| finish | 40 | 0 | 5305 | 93 | 606 | 89.3% |
| combined | 40 | 0 | 5410 | 122 | 676 | 87.3% |

Cohorts use different seeds. Counts and exposure rates are descriptive; wins are not the objective.

The48-object budget gate skipped 87.3% of combined-policy decisions. Its remaining 4,542 unit-target decisions produced 15 finishing/assistance candidates. Crowding is one blocker; the other reach/target/ally guards also limit opportunities.

- Combined → parent, same-tape counterfactuals: `{'identical_full_trajectory_with_other_players_commands': 40}`.
- Combined → finish, same-tape counterfactuals: `{'identical_full_trajectory_with_other_players_commands': 40}`.

Counterfactual reconstruction reruns the complete alternate subject VM while replaying the other nine players. It checks every command and state hash, and stops at the first different command. Identical full trajectories establish behavioral equivalence in those games; a divergence alone does not prove benefit.

Both alternatives matched every command and world state in all40combined-arm games. The enhanced policy therefore produced no individual or cooperative gameplay change on those trajectories. Differences between the three hosted cohorts cannot be treated as causal evidence for the enhancements.

Evidence: [semantic research IR](research.ir.json), [prospective plan](plan.ir.json), [decision events](decisions.ir.jsonl.gz), and [manifest](manifest.json). The `evaluated/` policies contain evidence updates with exactly unchanged BASIC. Raw replays and official status receipts are retained under `tmp/gota-ir/microplay-xp-20260920/`, indexed and hashed in the research IR.

- [parent XP request](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_24e952d0-6688-497b-9bb6-f07af93a575f)
- [finish XP request](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_e0a72803-305c-4e88-aabc-5501628a6023)
- [combined XP request](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_203a298f-8fab-4a34-b9b0-36fee81940a9)

Next experiment: redesign the opportunity/VM-budget gate as a separate IR fork, then repeat the frozen-player ablation. Additional unchanged-policy batches are not warranted by these results.

No league champion was changed. The shared daily allowance was raised from 1,600 to 100,000 by explicit user instruction; this experiment reserved 120 episodes.
