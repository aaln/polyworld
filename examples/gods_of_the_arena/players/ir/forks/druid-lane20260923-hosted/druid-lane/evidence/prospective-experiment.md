# Druid lane recovery with unchanged other heroes

Status: local development; no hosted games submitted.

The all-class lane-recovery source `2878f3e9` failed its frozen 320-game gate:
aggregate −5.26%, blue lead −12.15%, both later-draft contexts approximately +25%.
The exploratory Druid means rose on both colors while blue Ranger fell sharply.
These observations motivate a new source and test; they do not qualify a selected
slice of the failed policy. Preserve the original report and closed-lever entry.

## New hypothesis and scope

Apply the practiced lane-recovery rule only to the observed Druid class. Retain
deployed blue-center `c02f8cb6` commands for all other heroes. Druid stays at a
safe current position while useful healing works, can await a short cooldown,
resumes at 60% HP/20% mana, and returns for affordable missing core gear or when
healing is unavailable, danger appears, or the 12-second hold expires.
The complete Druid rule includes potion tracking and shopping; individual edits
need not be independently useful. No opponent identity is a runtime input.

If useful, Druid-heavy natural later-draft play earns more individual points
without disturbing the strong deployed ranged controller. If harmful, the
previous later-draft improvement disappears under fresh seeds or causes a
color regression. Do not claim that the earlier class slices establish causality.

## Local admission and preserved scope

Run the 92 recovery cases with Druid behavior enabled and other classes expected
to retain the baseline. Repeat inherited opening, portal, buyback and broad
runtime checks. Verify exact IR/BASIC round trips. Run complete native games
using the previous fixed local seeds/configuration; compare complete command
streams and terminal states against the preserved baseline whenever the subject
is not Druid. These local controls may be reused for deterministic equivalence,
never as competitive hosted controls. Runtime evidence must include the actual
maximum instruction/work costs.

## Fresh competitive test

One new preselected source, **400 fresh games**, 100 per source per color. Subject
has public team ordinal 3 in the same disclosed natural later-draft roster:
two fixed blue-center reference teammates, relh:v161 and Julia B5; khors:v114,
Richard:v174 and Jordan:v411 oppose it. Both subjects retain their production
draft. Require at least 20 Druid episodes per source across both colors.

Require zero source/VM/full-replay/XP/integer-score failures, at least 10% pooled
later-draft mean score gain, each color at least 95% of its fresh control, and a
positive lower 95% color-stratified independent whole-game bootstrap gain. Engine
and principal champions must remain stable. The non-Druid behavior equivalence
checks are also mandatory for promotion. This is a new scoped comparison of a
different executable, not a change to the failed four-context acceptance rule.
No old hosted controls, sample extension, favorable class filtering or threshold
adjustment after results. All actual classes and duplicate command streams are
reported. First four lexical episode IDs per source/color receive a full recovery
and shopping audit, descriptive only.

Critique: rare high scores and naturally different class mixes make later-draft
means noisy. Increasing to 100 games per cell may still leave moderate effects
inconclusive; retain blue-center then. Scope is these natural later-draft rosters
plus mechanically unchanged non-Druid play, not permanent leaderboard supremacy.

The user authorized 10,000 additional September 23 UTC games. After the preceding
study, 1,920 of 11,600 are reserved; this separate 400-game cycle brings it to
2,320. Four requests of 100, maximum three active. Legacy worker stays paused.
Preserve captured session `2026-09-23t02-52-57-098ze03810` and all prior outcomes.

Raw evidence: `polyworld/tmp/gota-druid-lane-20260923`.
