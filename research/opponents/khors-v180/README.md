# Khors v180: observed behavior on the neutral-camp release

28 appearances, eight hero classes, both sides, in 36 league games selected before outcomes. All replay state hashes, XP and integer scores reconcile. All 28 khors VMs are clean; only 5 games have all ten VMs clean. Other-player failures remain explicitly marked. No source, JEV, heldout forecast, executable proxy or causal transfer claim.

The strongest tendencies are conditional hero priority (801/816 commands; 27 eligible games), neutral harvesting without nearby hero/wave targets (1,243/1,307; 28 games), and estimated creep finishes (2,685/3,571; 28 games). Clean-game counterparts for the first two are 75/78 and 296/305. Episode-cluster uncertainty and per-game denominators are in[the IR](opponent.ir.json).

v180 does attack buildings: 1,125/9,914 explicit attack commands address towers, barracks or gods. The old universal building-avoidance hypothesis is false for this version. 51 commands addressed returning neutrals. These are submitted commands, not proof of damage.

Mean score is 2,511.43; mean XP 4,926.11 is composed of 2,180.36 hero, 1,667.93 lane-creep, 595.68 neutral and 482.14 structure/other. These are descriptive sampled outcomes, affected by class, roster and other-policy failures. Do not compare them causally with our differently drafted heroes or with a leaderboard average.

| Hero | Games | Mean score | Mean neutral XP |
|---|---:|---:|---:|
| Crossbowman | 8 | 4525 | 503 |
| DeathKnight | 5 | 164 | 235 |
| DemonHunter | 1 | 1450 | 1342 |
| DruidWarden | 6 | 2008 | 581 |
| Lich | 2 | 5425 | 2174 |
| Ranger | 3 | 2666 | 464 |
| VanguardKnight | 2 | 0 | 303 |
| Warlock | 1 | 957 | 306 |

Neutral income alone is insufficient: Vanguard still scored zero in both appearances and DeathKnight averaged 164 over five. The goal for our repair remains net individual score, with neutral kills/XP as mechanism checks.

The [7,581-point Lich game](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_26895ca1-ea7d-4152-bbd7-c9d31a77fc35) had 69 neutral kills and 4,109 neutral XP, alongside 3,508 creep and 3,300 hero XP. It also had an unrelated VM failure. Conversely, [this Crossbowman game](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_307914d5-94f6-4db1-bf58-2d2d67bf2166) recorded 11 neutral kills but only 30 neutral XP. We must verify eligibility and actual reward receipts, not optimize a kill counter alone.

Resource use is substantial: 250 health potions and 151 portal scrolls across 28 games. Mean spending 1,885 includes 414 in buybacks; it is not all healing. Purchase and portal events are retained per episode.

[Counter hypotheses](counter-hypotheses.ir.json) separate the tested weak-neutral candidate from untested hero-priority and XP-radius ideas. The candidate failed the score gate; see [the completed comparison](../../RESULTS.md). [Evidence rows](evidence/actor-rows.json) link every claim to an episode, class, command denominator and exact source hash. [Artifact index](evidence/artifact-index.json) locates immutable full replays and public frames. The collection/behavior instruments are preserved from the research archive; the fresh workspace does not import archived gameplay.

Run `python research/observations.py` then `python research/publish_opponent.py` from the workspace to reproduce summaries from captured inputs. Inference remains at motif granularity: exact threshold, memory, action ordering, target identity prediction and reactive intervention behavior are unidentified.
