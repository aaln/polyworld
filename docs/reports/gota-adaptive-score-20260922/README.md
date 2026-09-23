# Adapting individual-score policy to Richard v167 and khors v114

Current work targets the actual September 22 game: 2026.9.22.3, replay 58,
engine 1b708944. Richard v167 and Andre von Auto’s khors v114 oppose our
subject in both colors. The original portal source db71abb3 remains deployed. At the latest captured
48th round, Andre ranks first at 1690.99 and Aaron second at 1670.80; this
context is time-sensitive and does not replace controlled testing.

The [opponent audit](../../opponents/richard-v167/replay-audit-20260922/README.md)
reconstructs all 80 earlier control games. Richard drafts Warlock in 73/80;
khors uses Ranger or Crossbowman. Khors averages 20.01 hero kills to our 13.41,
while we collect more creep XP. More spell attempts or more hero priority do
not automatically close that gap: realized rewards, lost farming and time
must be measured together. No opponent source was recovered; the semantic
models are descriptive and cannot serve as executable proxies.

The [inventory audit](inventory-review.json) rules out a simple final-gear
explanation for khors's advantage. In all 80 games, both policies finish with
Crimson Dagger, Knight Armor, Battle Axe and Rune Crossbow. Our final gold
averages 1,738 versus khors's 1,162 and Richard's 594. Six inventory slots,
unique equipment and no selling prevent simply adding more damage equipment
once the four-item core plus portal/potion slots are occupied. Richard instead
uses varied caster equipment. Buyback attempts average 1.775 / 2.013 / 4.525
for us / khors / Richard; these counts include attempts, so they do not measure
successful respawns or prove a better buyback rule. Future gold-conversion
tests must account for slot opportunity cost and time recovered in the field.

| Experiment | Fresh hosted games | Aggregate score change | Red / blue | Decision |
| --- | ---: | ---: | --- | --- |
| Separate spell targets | 80 candidate + 80 shared screen controls | +10.06% | +8.20% / +11.71% | Not selected; unconfirmed |
| Spell targets + broad hero priority | 80 candidate + same 80 screen controls | +13.92% | +19.16% / +9.26% | Screen selected |
| Same source, independent later-draft roster | 160 | −4.20% | −13.35% / +6.54% | Rejected |
| Crossbow-only intervention | 160 | −6.35% | −31.94% / +20.78% | Rejected |
| Reward-ordered immediate finishes | 400 | +12.44% | +22.29% / +4.01% | Score gate passed; field changed |
| Same source with refreshed Julia teammate | 160 | Pending | Pending | Independent confirmation running |

The initial two candidates share one explicitly reported 80-game control;
that screen totals 240 games. Adding its 160-game independent confirmation
makes the first study 400. The separate class study adds 160. No control from
those inspected results is reused by the 400-game finishing trial.

The broad source’s failure on later-draft heroes motivated a class-specific
hypothesis. Its fresh trial then lost red farming and hero XP despite the blue
gain. These outcomes reject the complete policies; they do not establish which
individual edit caused the difference. Local branch-equivalence and runtime
checks passed even where competitive scores regressed.

The narrow finishing candidate passes its 400-game score conditions (+12.44%,
95% interval [+0.084%, +26.409%]), but Julia changed champions during the trial.
The original all-field stability rule prevents deployment from that test alone.
A separately frozen 160-game comparison refreshes Julia and requires the game
and principal champions to stay unchanged; other background updates are
disclosed. The first failed preparation is preserved, with no games created.

The candidate changes only observed target utility: prefer
one-hit reachable heroes, exposed structures or the enemy god to a dying creep.
It passes 140 actual-engine target/reward scenarios, 84 portal cases, 126 broad
checks and eight full native games. Its original prospective 400-game trial required a
10% aggregate gain, at least 95% of control on both colors and a positive lower
95% bootstrap gain bound. Practice outcomes cannot substitute for either hosted comparison.

[All first-study IR/source pairs](../../../examples/gods_of_the_arena/players/ir/forks/adaptive-score20260922/README.md)
and the [Crossbow-only pair](../../../examples/gods_of_the_arena/players/ir/forks/class-score20260922/README.md)
preserve initial inputs, reviewed beliefs, complete requests and source hashes.
The [finishing protocol](../../../games/gods_of_the_arena/experiments/2026-09-22-reward-finish.md)
was frozen before its hosted spending. Scores use lifetime XP less 200 points
per minute, clamped at zero; extending a game only helps if added XP offsets
that time cost. Hero, creep, building, god and time contributions are reported
separately.

Changing opponents require new evidence. The read-only
[field watcher](../../../games/gods_of_the_arena/instruments/adaptive20260922/field_watch.py)
records exact champion versions and prioritizes changed champions, then current
leaders. It includes new entrants before their first ranked round. Its output
is a research queue, not a live policy input, forecast or automatic deployment.
The paused legacy worker must not resume its obsolete game configuration.
