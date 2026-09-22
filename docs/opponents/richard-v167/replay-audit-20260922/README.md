# Richard v167 and khors v114 on the current XP-score game

This is a **retrospective descriptive audit**, not recovered opponent source or
an executable proxy. All 80 games are the deployed portal policy's clean
controls from the completed score-opportunity study, on **2026.9.22.3 /
1b708944 / replay58**. All ten VM exits, source hashes, full replay state
hashes, event XP totals and integer scores reconcile. The earlier khors study
used a different release and matches containing failed other VMs; preserve it
under its original limitations.

Richard's exact `e811221e-c419-4f7b-9629-01f8722ab9f7` (**v167**) drafts
**Warlock in 73/80 games**, Vanguard in three and Berserker in four. This
availability-dependent sample does not reveal draft ordering. Richard v135's
Ranger source model is historical and must not guide current hero assumptions.

Andre von Auto's exact khors:v114 is
`145c01e0-0cbf-4e1e-8120-11b437175b91`. It uses Ranger or Crossbowman in all 80.
The following means pool both colors, 40 per policy color:

| Policy | Hero kills | Creep last hits | Spell releases | Hero XP | Creep XP |
|---|---:|---:|---:|---:|---:|
| Our deployed portal policy | 13.41 | 195.41 | 106.56 | 2011.88 | 2754.68 |
| khors:v114 | 20.01 | 153.20 | 96.35 | 3001.88 | 2057.46 |
| Richard:v167 | 10.18 | 122.30 | 100.84 | 1526.25 | 2100.35 |

Our creep income is already higher. Khors earns more hero XP with fewer casts,
so rejected attempts and cast count alone are poor optimization targets.
Survival, mana, gold conversion and field time matter through **realized XP**
and the **200 points per minute** time cost. The score is
`max(0, XP*1440 - 200*ticks)//1440`; a longer game is valuable only when its
extra XP offsets that cost. Enemy-god destruction contributes 500 XP per
teammate and remains part of the comparison.

The deeper sample was selected before detailed inspection: the first four
lexically sorted episode UUIDs per control color, eight complete replays.
Minute position frames are replay truth, not the policy's observations.
In that sample, our basic attacks deal substantial structure damage while
khors' basic structure damage is zero. This suggests a target-allocation
hypothesis; it does not identify khors' controller ordering or prove that
ignoring structures improves our score. Richard's Dread Totem is not the
largest measured spell-damage source; Moth Hex deals more total damage in
this sample. A totem-only counter would therefore be premature.

The [adaptive-score experiment](../../../../games/gods_of_the_arena/experiments/2026-09-22-adaptive-score.md)
freezes two public-observation counter candidates. One separates spell targets
from basic attacks; the other also raises hero basic-target priority. Neither
uses player names, policy UUIDs, hidden positions or future opponent actions.
Competitive evidence comes from the exact hosted rivals responding to each
candidate. The rejected f6a0dace policy and its blue hero-XP regression remain
preserved; these candidates do not reintroduce its ten-tile chase restriction
or power-ratio rejection.

[economy-summary.json](economy-summary.json) contains both-color aggregates,
all eight detailed typed-effect summaries, fixed selection and scope.
[richard_v167.ir.json](richard_v167.ir.json) and
[khors_v114.ir.json](khors_v114.ir.json) keep all seven semantic layers with
unidentified priorities and `proxy_usable=false`. Reproduce using
`games/gods_of_the_arena/instruments/adaptive20260922/diagnosis.py`.
Raw inputs, full replays and plotted position frames remain in
`/Users/aaln/experiments/softmax/polyworld/tmp/gota-adaptive-score-20260922`.
