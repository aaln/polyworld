# Recovered Alex-winning policy — September 20, 2026

The previous `aaron-gota-ir-relh154-legacy-0916:v1` repeatedly beat the exact current Alex `gota-g002:v1` UUID. In the highlighted September 19 comparison it won **70/80: red30/40, blue40/40**. All 6 recovered blue cohorts won40/40. Red was less reliable: 19–30 wins per40 across the recovered cohorts. This is a historical result, not a fresh retest.

Exact policy version: `53f15b12-2198-41d1-bb99-df4bdb1ff7fd`. BASIC SHA256: `b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9`. Opponent: `a30542cb-54de-4109-92e6-bcabca7db4d8`. Engine:2026.9.16.5. The recovered primary `policy.py`, JSON IR and BASIC preserve the old behavior; compile/extract parity is recorded. Original evidence and captured coaching inputs remain unchanged.

The executable difference from the later deployed Jordan counter is confined to **the observer/defense decision**. Attack, spell/equipment and navigation skill definitions match. This narrows the investigation to when those unchanged skills are used; it does not independently prove which recall change caused every loss.

- **Early middle warning on blue:** during the first75seconds, three visible clustered enemies near a standing middle tower can trigger recall instead of waiting for four.
- **Damaged side-tower warning on blue:** during the first150seconds, a visible pair near a standing side tower with150HP missing triggers ordinary recall. This is current damage, not a measured damage rate.
- **Defend the threatened objective:** remember the protected structure; consider visible enemies within24tiles of it and32tiles of the acting hero. The role and commitment clocks retain defense. Non-sentries with no actionable target for20seconds can release; fog is never treated as proof of safety.
- **What the Jordan counter changed:** it cancels defense beyond28tiles from the friendly god; blue also clears solo backdoor commitment. This preserves distant offense, but removes the old remote return behavior.
- **What the Richard counter then added:** a two-enemy, anchored near-core alarm within60tiles can override that cancellation for50seconds. This broader rule is different from restoring the old objective-specific alarms. Our latest inherited blue won40/40 against Richard but0/40 against Alex.

The historical median-duration blue win was reconstructed from its exact source: **24,618 owned commands and all5,880 state hashes match**. The fresh early-middle alarm occurred on 5 hero slots, across 1025 decisions. This establishes that the early defense behavior was used in an actual win; it is not an ablation proving that rule alone won the game.

| Historical cohort | Our color | Wins | Losses | Draws | Distinct full command streams |
|---|---|---:|---:|---:|---:|
| scoped-followup | blue | 40 | 0 | 0 | not counted |
| target_geometry | red | 29 | 11 | 0 | 9 |
| target_geometry | blue | 40 | 0 | 0 | 4 |
| urgent-jordan-20260919 | red | 28 | 12 | 0 | not counted |
| role_raid | red | 28 | 12 | 0 | not counted |
| role_raid | blue | 40 | 0 | 0 | not counted |
| nearby_raid | red | 19 | 21 | 0 | not counted |
| nearby_raid | blue | 40 | 0 | 0 | not counted |
| weapon_dense | red | 28 | 12 | 0 | 9 |
| weapon_dense | blue | 40 | 0 | 0 | 4 |
| readiness | red | 30 | 10 | 0 | 8 |
| readiness | blue | 40 | 0 | 0 | 4 |

Stored native replay audits, row counts and replay hashes were rechecked for these cohorts. The highlighted80games have all ten successful structured VM exits and player-status hashes rechecked. The older legacy confirmation has archived headless-log validation but no structured player-status files; the manifest keeps that distinction. Seeds and repeated trajectories are correlated; do not interpret the rows as independent Bernoulli trials or select the best red cohort as a guaranteed87.5%future win rate. The broader record explains the remembered near-perfect blue results.

A separate September20 experiment, `tower_handoff_v2` (`17db3a9d-b5eb-4f5a-b5aa-10654e9555bd`), recovered **Alex red40/40**, while **Alex blue0/40**. It also won40/40 each color against Jordan and0/40 each color against Richard. Its red behavior couples caster transit/support with a low-HP tower disengagement requiring a nearby live allied creep, and preserves attacks on nearly finished towers. A reviewed Alex red win contains three actual tower-target changes. The complete package, not tower disengagement alone, owns that win count. It was rejected for joint target advancement and remains unpromoted.

Two discriminating follow-ups are supported by this research, not yet validated:

1. Restore the historical blue observer as an exact reference, then test objective-triggered recall versus the28-tile cancellation and the broad Richard exception with other skills fixed. Predicted effect: recover early middle defense and Alex blue wins; Jordan and Richard must be checked because the timing tradeoff may return.
2. Test the newer red caster/tower-handoff component with the historical blue observer in a separately versioned IR combination. Predicted effect: preserve the red Alex result while recovering blue; mixing individually successful color components is not proof the combined executable will win. The worker's separate critical-blue fusion is a different hypothesis and is left untouched.

No policy was pushed. The latest unchanged coaching candidate failed the user-authorized Alex/Jordan check: Alex red2W24L14D, blue0W40L; Jordan0W40L on each color. Its evaluated IR/BASIC pair and all400hosted/108local results are saved in the sibling `richard135-transition-20260920` bundle. The live incumbent was retained.

Evidence manifest: `findings.json`; exact skill changes: `legacy-to-jordan-skills.json`, `jordan-to-critical-skills.json`, `critical-to-current-skills.json`. Raw historical research: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/alex-history-20260920`. No new hosted games were purchased for this historical investigation.
