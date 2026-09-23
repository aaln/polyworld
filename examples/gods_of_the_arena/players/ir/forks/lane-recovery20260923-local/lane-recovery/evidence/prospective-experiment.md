# Lane healing with useful shopping returns

Status: local development; no hosted games submitted.

The user reports repeated unnecessary base trips and requests a simpler policy:
stay in lane to heal, except when returning also buys useful items. Start from
deployed blue-center `c02f8cb6`, not the rejected field-sustain `3807330d`.
Read `closed_levers.md`; the prior coordinated bundle failed its 240-game score
gate. The original coaching captures and that result remain immutable.

## Hypothesis and change

For a health-only retreat outside the keep, stay at a safe nearby position while
an available heal or potion works. Resume normal play at 60% HP and 20% mana.
Allow at most 12 seconds per retreat episode; consider affordable learned heals
whose cooldown is at most 8 seconds, track accepted heal impacts and active
potions, and cast only a useful ready heal. Stop the old base path immediately.
If a missing core item is affordable and an inventory slot is available, preserve
the return and shop. Threats, unavailable healing, exhausted waiting time and
resource deficits retain the existing escape. Existing keep recovery and active
portal channels keep ownership. No changed draft, targeting, route or buyback.

This changes the recovery destination and commitment. Unlike the rejected
bundle, it holds position through a useful bounded cooldown instead of stepping
toward home and abandoning field healing after an 18-tick impact window. It
does not add a formation anchor or force extra healing outside a retreat.
Health does not passively regenerate in lane; a no-heal hero must not wait there
forever. Public observations alone determine actions.

If useful, safe lane healing shortens base travel and restores XP collection
without excessive deaths or wasted mana. If harmful, staying stationary, delayed
shopping, resource depletion or premature re-entry reduce individual score.

## Checks before spending

Use actual engine ticks to test both colors, Druid cooldown recovery, active
potions, no mana/charges/heal, danger and incoming warnings, roots, affordable
and unaffordable purchases, full inventory, already recovered heroes, a bounded
timeout, and active channels. Verify regenerated BASIC and extracted semantic IR
are identical. Run inherited opening, portal, buyback and broad scenarios plus
complete native games. Native results establish runtime/mechanism only.

## Prospective hosted comparison

Freeze one final source and fresh deployed-parent controls. 320 games: 40 per
source in red lead, blue lead, red later-draft and blue later-draft contexts.
Khors:v114, Richard:v174 and Jordan:v411 oppose each subject. Later contexts use
the prior disclosed roster with two fixed reference teammates, subject ordinal
3, to exercise natural Druid fallback without changing production draft code.
Check live champions and the engine before preparation and submission; a changed
field needs a new frozen plan. No control reuse, sample extension or retuning
after competitive results. Minimum 10 Druid games per source pooled later-draft.

Require all ten source/VM/full-replay/XP/integer audits to pass, at least 10%
aggregate mean score improvement, each context at least 95% of control, a
positive lower 95% context-stratified whole-game bootstrap gain, improved pooled
later-draft score and positive blue-lead mean score gap over khors:v114. Report
all class mixes, score, XP sources, deaths and duration. The first four lexical
episode IDs per cell get a recovery/travel audit, descriptive only.

Critique: different natural draft mixes can dominate a small cell; report them
without selecting favorable slices. Fixed teammates and roster constrain scope.
Fort wins and reduced travel alone cannot qualify promotion. Forty games per
cell may leave moderate gains inconclusive; retain the parent in that case.

The normal September 23 UTC hosted allowance is already fully reserved at
1,600. Build, practice and prepare the concrete comparison first. Do not submit
until additional games are authorized or the budget resets. Legacy worker stays
paused; journal every eventual request and preserve its idempotency key.

Raw evidence: `polyworld/tmp/gota-lane-recovery-20260923`.
