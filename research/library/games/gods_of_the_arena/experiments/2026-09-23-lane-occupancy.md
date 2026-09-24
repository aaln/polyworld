# Less-crowded opening lane / engine61

User coaching: choose a lane that other players are not going to, to increase
individual XP-minus-time score. The implemented hypothesis concerns **allied**
competition for creep XP; enemies may supply hero-kill opportunities.

Mean individual score **2493.62 → 2771.45**,
paired delta **+277.82**, 95% paired bootstrap interval
**[+113.67, +461.75]**.
Score-only pilot advancement: **True**. This is a directional
study on a reused cohort, without an established verdict-size floor or independent
confirmation. No league deployment. All80pairs are retained; no game-win gate.

## Mechanism and coordinated implementation

At engine `e42c4822f44e04726b09bb4ffe853152c7a18207`, each creep supplies15XP
within six tiles on its navigation layer. An eligible last hitter reserves15%;
the remaining85% is shared. A sole eligible hero receives15XP; with two heroes,
the last hitter averages8.625 and the other6.375, including fractional carry.
Gold last-hit rewards are separate. These theoretical shares do not guarantee
that a lane choice reaches or kills more creeps.

During12–35seconds after first activation, the policy classifies allied heroes
at least12tiles from home by their angular direction toward the three existing
lane waypoints. All allied positions are public. With at leasttwo committed
allies, it chooses a strictly less crowded lane if healthy and away from current
targets/threats. Occupancy ties retain the current route; shorter waypoint travel
breaks ties between better alternatives. It commits once, persists the choice
through respawns, invalidates a stale portal anchor, and lets an explicit choice
override the first-seat blue ranged center route. It does not estimate wave size,
future enemy pressure, navigation travel time, or joint teammate coordination.

Changed executable components: lifecycle, observation, advance, plus choose_lane.
Draft, economy, combat, crowd control, recovery and all other skill bodies match
the control-tactics parent. All strategy goal references use individual Score.
An initial Q16.16 overflow prototype was preserved and repaired before upload.

## Validation and experiment

120host decision executions pass, including unknown/near-home allies, balanced
lanes, low HP, nearby enemy, opening expiry, persistent assignment and blue
override. Eight new complete native games match eight preserved parent controls:
total score20818→18845, three lower and five equal. This is negative reference-bot
evidence, not omitted or used to redefine the hosted cohort.

Hosted: all80prior control-tactics candidate games serve as baseline;80new
counterfactual games replace only our policy. Exact seed, resolved roster, probe
slot, game configuration, manifest and nine responsive sources are paired.
Every game has ten valid VMs, exact full replay hashes, XP and integer scores.
All80opening source reconstructions match commands and world-state hashes;
**20/80 actually change lane**.

Baseline `morrow-ibis-61c2:v1` (`f063e236-4f9b-4f52-a57c-e41b29d14caf`),
candidate `sable-oriole-61d3:v1` (`4d55ef4d-cfa2-485d-a048-a81c35b8acd3`).
Counterfactual evaluation `cfeval_1d51ee96-53df-47a7-b1c6-77d0929aa235`;
experience request `xreq_62c0d9f3-0d08-4f64-975f-dec4edd65e2c`.
Both league champions retain the previously deployed source29f6d7e6.

## Descriptive mechanism metrics

| Per-game mean | Parent | Lane candidate |
|---|---:|---:|
| Total XP | 5761.99 | 6044.70 |
| Creep XP | 3243.24 | 3567.20 |
| Hero XP | 2021.25 | 1882.50 |
| Structure/other XP | 497.50 | 595.00 |
| Solo-recipient creep XP | 2959.69 | 3285.75 |
| Hero kills | 13.47 | 12.55 |
| Deaths | 7.61 | 7.11 |
| Game minutes | 16.56 | 16.58 |

Solo-recipient XP is counted from actual positive XP recipients for each creep
death, not lane geometry. Counts1–5 reconcile exactly to all creep XP, and all
XP sources reconcile to integer scores. Hero/side/seat breakdowns, survival,
nonzero frequency and conditional means are diagnostics; they do not change the
frozen score-only rule. Attribution is descriptive, not an isolated component
effect; route, travel, support and combat exposure change together.

| Hero class ID | Pairs | Parent score | Candidate score | Delta |
|---|---:|---:|---:|---:|
| 1 | 18 | 3262.06 | 3510.44 | +248.39 |
| 3 | 40 | 1556.00 | 1556.00 | +0.00 |
| 6 | 22 | 3569.68 | 4376.73 | +807.05 |

All20changed games are blue first-seat ranged heroes moving from the center
route to lane2; the other60full command streams and scores remain identical.
That context improves3763.65→4874.95 (+29.53%). Overall creep XP rises323.96
while hero XP falls138.75; solo-recipient creep XP rises326.06. Most baseline
creep XP was already solo-recipient (91.26% versus92.11% candidate), so this is
mainly more solo farming opportunities, not proof that splitting the same wave
was the dominant loss. Fewer hero kills did not prevent a higher individual score.

After the study, the league changed to2026.9.23.4/replay62, commit2c8db6e,
adding neutral camps. This61result does not qualify current-release deployment.
A separate current-release comparison will test lane-only and guarded camp
farming while preserving every source and result in this cohort.

Raw inputs, original IR, replay tapes and upload receipts remain in
`polyworld/tmp/gota-lane-occupancy61-20260923`. Reused baselines link to the
untouched preceding control study. The portable pair contains every pair ID,
file hashes, frozen method, results and source audit. Reviewed IR annotations
regenerate byte-identical tested BASIC; run `python verify.py` or the included
compile/extract converter. No inferred live XP or private opponent state is used.

Portable pair: `examples/gods_of_the_arena/players/ir/forks/lanefarm20260923-hosted/lane-occupancy`.
