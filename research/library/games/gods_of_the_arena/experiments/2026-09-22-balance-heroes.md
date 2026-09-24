# Symmetry and hero balance: new evidence required

Status: completed; all four coordinated alternatives rejected by the frozen replacement gate. Previous experiments and captured inputs remain immutable.

Question: on published 2026.9.22.2 / ffcedcd, does a team-relative policy preferring
Crossbowman, Warlock, Arcanist or Ranger improve current per-hero integer XP score
over the exact deployed b82c3799 source? The creator reports Ranger HP/level 38→19,
Crossbowman base damage 46→69, and Warlock Dread Totem 58→87. Confirmed in source.

The old engine's performance and hero rankings do not transfer. Current engine
freezes shared observations and resolves simultaneous movement/hits/deaths,
removes faction draft bonuses and absolute-order tie breaks. Our old global
quarter-tile recovery step, integer lane goals and directional fallbacks were
not rotation equivariant. Convert all spatial reasoning into team coordinates.
Retain the old executable as a separate fresh hosted control.

Check closed_levers.md: older win gates and old-recovery findings are historical.
The rejected attention/equipment variants are not being retried. The shared
normal 400/cycle and 1600/day ledger still applies; 1120 were reserved before this
new question. No old engine accepted state is overwritten.

Cheapest adequate instruments: source contract audit, real-host mirrored
decisions, all-hero micropractice, and complete responsive native episodes with
exact replay reconstruction. These establish legality/mechanics, not competitive
strength. Rebuild and calibrate the auditor against a hosted current-engine replay.

Then freeze exact current healthy opponent versions, identical nine-player mixed
rosters, and subject first pick on each color. Compare five arms (deployed control,
mirrored Ranger, Crossbowman, Warlock, Arcanist), 40 games/arm/color = 400 games.
Sequential batches, full ten-VM validity, all replay hashes, XP and official integer
scores. Use one subject seat, never five copies as a proxy for mixed league play.
Keep all original replay/spec/status inputs. Record realized picks and fallbacks,
death/XP/hit/item/portal diagnostics and repeated command streams.

If the hypothesis is true, at least one new executable improves mean subject score
by ≥10% overall and preserves ≥95% of control score on each color. If no executable
meets both, retain control and reject/inconclusive rather than change the threshold.
Require every compared game valid. Positive score where control is zero must also
be strict. Select the highest aggregate score among qualifying candidates.

Adversarial critique: these are controller-plus-draft interventions, not isolated
causal hero rankings; enemy/team draft responses are part of the policy effect.
First-pick results do not establish late-draft performance. Random seeds cannot be
perfectly paired in hosted requests; freeze all other settings and versions. A
small/duplicate trajectory population limits uncertainty and generalization. Four
choices increase selection optimism: report all choices, and qualify any selection
as a bounded roster result rather than claim universal superiority or #1.

Raw study: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-balance-20260922`.
Reference: current20260922 pair and deployment receipts, preserved on branch
gota/week-20260921 at 192ce2d. No old result receives a new game label.

## Completed results

All 400 games completed with zero invalid VMs, exact source hashes and full replay/XP/integer-score agreement. Each cell has 40 distinct command streams.

| Controller | Red score | Blue score | Mean | Gate |
|---|---:|---:|---:|---|
| Deployed control | 2337.400 | 2701.975 | 2519.688 | reference |
| Mirrored Ranger | 2229.075 | 1715.950 | 1972.512 | fail |
| Mirrored Crossbowman | 2626.250 | 2382.325 | 2504.288 | fail |
| Mirrored Warlock | 1238.450 | 722.875 | 980.663 | fail |
| Mirrored Arcanist | 1540.425 | 1264.675 | 1402.550 | fail |

The control remains the selected reference for this experiment. Mirrored motion passes geometric tests but is not retained as a gameplay improvement. Crossbowman's red gain cannot offset its blue regression under the frozen rule. This does not establish a universal hero ranking: the intervention combines draft and spatial behavior, with different responses from the other nine policies.

A separate prospective follow-up isolates Crossbowman priority while preserving every deployed post-draft contract. Its 80 games use the remaining daily allowance in a separate cycle after this 400-game cycle closes. Controls are reused explicitly, not relabeled as fresh concurrent observations. See `2026-09-22-crossbow-draft-isolation.md`.
