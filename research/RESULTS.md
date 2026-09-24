# Current-engine recovery comparison

180 hosted games: 60 current-policy controls and two responsive 60-pair comparisons. All ten side/seat positions, frozen rosters and seeds. Each request had at most 60 games. Full replay hashes, all ten VM statuses, XP and integer score accounting were audited.

| Policy | Mean score | Positive-score games | Mean among positive games | Paired gain and adjusted 97.5% interval |
|---|---:|---:|---:|---|
| Deployed | 1527.0 | 54/60 | 1696.7 | Reference |
| previous | 1616.0 | 41/60 | 2364.8 | +88.9 [-245.6, +405.1] |
| weak-neutral | 1397.6 | 48/60 | 1747.0 | -129.4 [-318.2, +41.6] |

The intervals resample whole matched games within side/seat strata and adjust for two baseline contrasts. Hero slices below are exploratory. Conditional positive-score means select different outcomes and must be read alongside the overall mean. The legacy helper additionally reports a >=500-point productivity threshold; this is a diagnostic, not the promotion objective.

## Neutral income by hero

| Hero | Games per arm | Deployed / candidate neutral XP | Deployed / candidate neutral kills | Candidate score change |
|---|---:|---:|---:|---:|
| Vanguard | 2 | 0.0 / 0.0 | 0.0 / 0.0 | +0.0 |
| Ranger | 6 | 707.8 / 707.8 | 12.2 / 12.2 | +0.0 |
| Arcanist | 9 | 173.3 / 137.0 | 4.1 / 4.2 | -186.2 |
| Druid | 20 | 379.9 / 329.7 | 6.0 / 6.1 | -342.4 |
| Death Knight | 11 | 519.6 / 788.7 | 8.4 / 14.0 | -54.9 |
| Crossbowman | 6 | 641.8 / 641.8 | 11.7 / 11.7 | +0.0 |
| Lich | 4 | 135.2 / 510.5 | 3.0 / 12.8 | +343.5 |
| Berserker | 2 | 277.0 / 67.0 | 4.0 / 1.5 | -6.5 |

Warlock and Demon Hunter were absent from this natural-draft panel; no hosted efficacy claim applies to them. All ten classes did secure neutral kills in the controlled camp encounters. The candidate and deployed policy each earned 400 total neutral XP there; the previous policy earned 970. The candidate did not improve this local mechanism test. The 12 native full games also favored deployed source in total score (9,942 versus 9,177 candidate and 8,164 previous); these are runtime/mechanism checks, not hosted outcome evidence.

The complete own-source reconstructions of three poor league games matched every command and state hash. The Vanguard saw an eligible camp on only 15 of 1,553 active decisions and selected it every time. That is an opportunity/routing hypothesis, not proof that a camp route will improve score. Druid and Arcanist observations also show retreat, health and competing-target restrictions.

## Decision and continuation

The fresh workspace and all three references are preserved. No automatic rollback or league promotion follows from this study. Any advancing candidate requires an independent fresh confirmation under the frozen rule. The next repair should test bounded camp access and income per travel/death time, while protecting the deployed policy’s productive-game rate. Do not select a hero-specific hybrid on this sample and call the same sample confirmation.

[Current research contract](CURRENT_CONTRACT.md) · [Full statistics](results/statistics.json) · [Khors v180 observations](opponents/khors-v180/README.md) · [Frozen plan](results/hosted-plan.json)

Raw captures remain at `/Users/aaln/experiments/softmax/polyworld/tmp/gota-weak-neutral62-20260924`. Historical workspace and session inputs remain intact.
