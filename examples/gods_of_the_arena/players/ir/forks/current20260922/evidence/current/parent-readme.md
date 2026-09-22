# Practiced microplay policy

Primary semantic IR: `policy.py`; generated executable: `policy.bas`. Version **aaron-gota-micro0922:v1**, UUID `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7`. Engine **2026.9.21.5** / `f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. Inert research version; no league or formal accepted-state change.

Adds a one-physics-tick post-hit movement/reacquisition skill, feasible last-hit priority, Crossbowman XP proximity before stale movement throttles, four damage/HP items with potion and portal reserves, purposeful restocking, lane-directed return portals and bounded emergency defenders. Uses public observations and draft choices; no policy-ID oracle.

Practice on each color: Ranger attacks **20→39** in 360 ticks; contested-wave last-hit gold **210→240**, with shared XP **300→285**; boundary Crossbowman XP **0→15**; Ranger shop damage **47→61** with unchanged 320 HP; defensive channels complete and release, safe-base controls do not portal. The XP regression remains visible. The current host has no sell/upgrade action, so equipment improvement means purchase choice and order.

Four responsive native parent matches won; all state hashes replay exactly. All 126 runtime fixtures pass, maximum 13,428 instructions / 20,377 work. The first fixture had no suitable sparse XP waypoint; its corrected ground-tile setup and the old same-tick command assertion are preserved separately. Neither instrument failure is counted as a policy runtime failure.

Hosted panel: **480 games**, 40 per policy/target/color. Targets relh v161, Jordan v306 and Richard v153, with exact UUIDs in the plans. Fort qualification: **False**; absolute rival-score qualification: **False**.

| Opponent | Color | Baseline W/L/D | Practiced W/L/D | Practiced / rival score | Score change | Distinct streams |
|---|---|---|---|---:|---:|---:|
| relh | red | 0/40/0 | 33/7/0 | 322.44 / 381.16 | +284.79 | 18 |
| relh | blue | 3/37/0 | 29/0/11 | 411.02 / 310.23 | +255.19 | 18 |
| jordan | red | 9/0/31 | 40/0/0 | 781.65 / 436.60 | +341.31 | 15 |
| jordan | blue | 1/0/39 | 40/0/0 | 591.43 / 278.61 | +174.22 | 18 |
| richard | red | 0/40/0 | 29/11/0 | 327.99 / 436.26 | +288.56 | 19 |
| richard | blue | 2/38/0 | 34/0/6 | 484.70 / 237.28 | +350.97 | 17 |

Score is per-hero `max(0, XP - 200 * world ticks / 1440)`, including draft time. Uniform teams, fixed map and repeated streams limit generalization; the generated seeds are not a paired or independent statistical sample. Winning forts alone does not establish leaderboard superiority. Baseline discovery closed before the revised timing/XP hypothesis was frozen; two 240-game cycles shared the existing 400/cycle, 1600/day budget.

Offline verification: `python3 verify.py`. Regenerate an edited Python IR with `python3 convert.py compile --policy policy.py --out /tmp/new-micro-pair`; lift BASIC edits with `python3 convert.py extract --source edited.bas --out /tmp/lifted-micro-pair`. Changed executable bytes invalidate prior belief claims automatically. Versioned compiler and all candidate pairs are preserved under `tooling/` and `evidence/`. Raw inputs/replays remain at `tmp/gota-targets-20260922`; earlier coaching captures and baseline bundles are untouched.
