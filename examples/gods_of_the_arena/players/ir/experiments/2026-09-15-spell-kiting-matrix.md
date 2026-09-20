# Spell continuity while kiting
Status: inconclusive

Source-derived mechanism: applyWalkTo clears attackObjectId. updateHero then
has no strike target, so tryCombatAbilities cannot cast offensive abilities
while walking. Healing/support/passives can still work. Source is the exact
published e127989 sim.nim (tryCastAbility/tryCombatAbilities/applyWalkTo).
This proves the interaction exists; it does not prove it caused previous losses.

A longer retreat might gain real separation, but it also spends more time with
no automatic offensive spell target. Test a2x2 duration/casting matrix with
threat radius5, critical_percent0 and unfiltered threats fixed. Existing
bare10tick cell(early_all) failed17/40wins/deaths124. Three new cells:
spell_short(explicit casts,10ticks), long_bare(no explicit casts,32ticks),
spell_long(explicit casts,32ticks). Each factor contrast changes one variable.
All cells are frozen before any new outcomes; no partial tuning/stopping.

On an accepted retreat walk, spell cells try one successful offensive cast in
slot3,2,1 priority, checking charges/cooldown and letting the host validate
live mana/range/target. Druid friendly-healing slots1/2 are skipped. A failed
walk restores normal attack and issues no explicit casts. Automatic passives
and support remain enabled. Inventory and purchases remain unchanged. Explicit
resource timing can differ from automatic casts; this is not claimed to be
bitwise equivalent to automatic casting during standing attacks.

TRUE: accepted casts occur during actual retreats, offensive growth is retained,
and a longer safe firing cycle reduces deaths without losing wins. FALSE:
casts rarely activate, movement still loses pressure, or mana is spent poorly.

Adaptive discovery only: same40 inspected balanced cases721000–721039 and exact
v2/default references. New instrumentation adds only an accepted-cast counter;
rerun both40-case references once and verify identical ticks/winners/state hashes
against the preceding instrument before reusing them across cells. Full tapes
must all verify. All runtime failures are retained and block aggregation until
exact-input recovery.

Preregistered gates: wins>=v2/default; deaths<=85%v2; lifetime XP>=80%v2;
actual retreat displacement in>=12cases; every normal retreat follows a real
hit within1tick; no corrected adverse regression flag. Spell-enabled cells also
need>=10accepted explicit casts across>=5games. Here XP replaces the older raw
basic-hit floor because the intervention deliberately restores spell damage;
report BOTH hit counts/rates and XP, and do not reclassify any earlier failure.
XP measures finishing blows rather than all damage; fort wins remain mandatory.
Fresh confirmation is required before any strength claim or league replacement.
If multiple cells pass, choose more wins, then lower deaths per game minute.

Critique: several adaptive probes can overfit this cohort; fresh cases must
confirm the chosen candidate. Longer retreats can reduce raw counts by changing
match duration; report per-minute rates. Successful casts need not hit moving
enemies; full outcomes and lifetime XP matter. This matrix adds no human or
unpublished observations and uses the published3 combat surface only.

Completed all cells and tape checks. {'spell_short': {'wins': 17, 'deaths': 115, 'casts': 39, 'passed': False}, 'long_bare': {'wins': 23, 'deaths': 135, 'casts': 0, 'passed': False}, 'spell_long': {'wins': 20, 'deaths': 138, 'casts': 84, 'passed': False}}
Selected for fresh confirmation: None. No league change from this discovery matrix.
