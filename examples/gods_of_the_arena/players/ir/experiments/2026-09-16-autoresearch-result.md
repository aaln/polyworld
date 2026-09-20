# Autoresearch result: cadence policy deployed

`aaron-gota-ir-cadence-all-0916:v1` is now the active champion for **Aaron's
Optimizer** in Gods of the Arena. Aaron's waveguard entry is also active;
exactly two owned ladder players were verified. No first-place claim is made.

## Independent confirmation

The selected candidate completed 400 fresh games per policy against the same
nine pinned incumbents, with balanced hero rotation and independent seeds.
Discovery games were excluded. All 1,200 complete replays and VM outcomes passed.

| Policy | Wins /400 | Deaths per minute alive | Mean Glory |
|---|---:|---:|---:|
| Cadence candidate |215 (53.75%)|0.3980|989.37|
| Waveguard-r4:v2 |175 (43.75%)|0.6540|389.51|
| Motion-weapon:v2 |176 (44.00%)|0.4892|365.32|

The win gains were 10.00 and9.75 percentage points, with one-sided Fisher
p-values 0.002886 and0.003579. Both preset significance gates passed; there were
no adverse class flags. Equipment was purchased in all 400 candidate games.
Death rate was 39% lower than waveguard and 19% lower than motion. These are
cohort results, not a guarantee of a particular leaderboard rank.

## Transfer to current champions

A separate 100-game request sampled current champion lineups, excluding both
owned players: **58 wins**, equipment in 100/100, all replay and VM checks passed.
It covered 13 opponent versions and 59 different opponent sets. Mean Glory was
924.69. This passed the predeclared field guardrail; it is a transfer screen,
not another A/B. Request: `xreq_98443e6b-3124-4449-84ba-4af4e06aa594`.

## What changed

After a confirmed basic hit, the policy issues one brief legal movement decision
and resumes attacking, shortening recovery. It retains wave routing and item
buying. In 300 completed discovery replays, basic hits per minute alive rose to
21.28 from 12.58 for motion and 12.78 for waveguard; dominant hit intervals
shortened for every hero class. Most brief movement only turns the hero, so it
is not claimed to provide safe escape movement. Friendly-tower navigation stalls
remain a future improvement target.

The IR now explicitly distinguishes attack cadence from escape intentions.
Measured beliefs, goal references, confirmation, field results and deployment
were merged into revision 22. Compiling and reverse-extracting retain exact
parity with the uploaded BASIC. See `../cadence_all.evaluated.ir.json` and
`../cadence_all.evaluated.bas`.

## Research scope and reproducibility

Two iterations screened 16 candidate configurations across 880 local games,
followed by 2,100 new hosted games. Failed farming, center movement and four-tick
retreat variants remain recorded; none was promoted. Separately, 1,200 previously
played motion-policy games were recovered and audited, not counted as new data
or pooled with this study.

100 full-suite tests and 4 additional roster/queue regression checks passed. One
hosted pod log was unavailable; the original capture marker remains, with the
game's official ten-seat successful VM status as equivalent proof. No episodes
were dropped or replaced. All full action tapes were replayed successfully.

Game: 2026.9.15.3, source e1279894d10a7684f303e7a9f1ea2f84c1d14253.
Policy ID: `c5711f9d-6248-4843-ae39-bc13a4911b79`.
BASIC SHA256: `d44442652129be56516e6ef675bd338d05a0a7863e2372958d2da8fece348c8e`.
Optimizer membership: `lpm_365995fe-5793-4098-959a-c211f850b8c0`.
Evidence root: `tmp/gota-ir/autoresearch-20260916/cadence-cycle`:
`completed.json`, `hosted-confirmation/result.json`, `field/result.json`,
`deployment/deployment-verified.json`, and `deployed-feedback/`.
