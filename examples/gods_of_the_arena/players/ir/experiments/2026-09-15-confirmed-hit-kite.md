# Confirmed-hit kiting from exact league v2
Status: running

Release2026.9.15.3 became live during the older timed-kite screen. Its manifest
pins e1279894d10a7684f303e7a9f1ea2f84c1d14253 and exposes a lifetime successful
basic-hit counter, preserved across respawns, plus ticks to next hit. This is
new mechanistic evidence for a distinct implementation before reading any
outcomes of the earlier screen. The prior screen remains separately recorded.

Parent is exact aaron-gota-ir-waveguard-r4:v2, SHA
c23c618705b74ec3154ba7614cdda6fd7bdc84e71ea55c3b0ef171438f0a91c3.
Only R2 combat execution changes; target selection, item buying, inventory use
and no-target allied-wave movement are preserved. Ordinary kiting uses an
observed counter increment, never an assumed elapsed windup. Ranged heroes
retreat10ticks from a mobile target within3tiles; all classes can escape when
HP falls below35% while losing HP near a threat. Failed movement restores an
attack order. Missing targets and gaps reset event memory.

Hypothesis: retreat during basic-attack recovery to reduce enemy contact while
preserving our successful shots, growth, and fort wins. TRUE: fewer deaths,
retained hit output/wins, every normal retreat following a successful hit.
FALSE: retreat sacrifices useful attacks or positioning, or survivors fail to
convert into fort wins. A confirmed hit need not be a kill or meaningful damage
against every defense; XP and outcomes remain separate metrics.

Cheapest adequate instrument: exact-source functional fixtures, then full local
matched games against defaults; old-release tapes cannot isolate the new API.
Fresh independent seeds721000–721039, four cases perclass, three arms(v2,
candidate,default) with one tested hero and nine defaults. Freeze seed/slot,
full engine config, source, binaries, policies and instruments before launch.

Directional screen gates: at least as many fort wins as both references;
deaths <=85% of v2 and basic hits >=80%; displacement in >=12/40 cases;
100% normal retreats preceded by a replay-observed hit within1tick. Complete
all120 games and tick/action audits before reading the result. No corrected
adverse flag in33 overall/class checks for win, timeout and death rate per
reference. Keep all failures and retry exact inputs. No retuning/stopping on
partial outcomes. A failed gate is retained.

Critique: ten classes differ in range, speed and windup; report every class,
and do not count the ten teammates as independent games. Raw deaths/hits vary
with game length; report rates and keep fort-win guardrails. Army movement and
terrain can obstruct a retreat; accepted movement alone does not establish
actual displacement. Small40-case screens can miss moderate effects. This
screen alone does not qualify promotion; a passing candidate needs fresh
confirmation and batched hosted comparisons with frozen incumbent versions.

No hosted candidate has been uploaded or promoted by this record.

Completed all120 games and replay checks. Candidate12/40 wins vs v2 22/40 and
default18/40; deaths125 vs134; hits2153 vs2321. All153 normal retreats had a real
hit within1tick. Mechanics work; performance gate failed. No promotion.

Two separately frozen component probes now reuse these40 cases explicitly as
adaptive discovery: no_escape changes only critical_percent35→0; targeted
changes only which enemy qualifies as a retreat threat, requiring observed
objectTarget=selfId. All other thresholds, economy, targeting and no-target
movement stay unchanged. Both use the same screen gates (wins>=v2/default,
deaths<=85%v2,hits>=80%,actual movement>=12games,100%valid normal hit events).
No partial-outcome tuning. Any selected improvement requires fresh validation;
these reused outcomes cannot serve as independent confirmation. Maximum two
component probes in this discovery pass; preserve both results, including
failures. Rosters are nine defaults plus the subject; all full tapes verified.
