# Burst kiting from exact league v2
Status: inconclusive

Parent: aaron-gota-ir-waveguard-r4:v2, 6d0ff780-652f-47a8-82b3-336cb7a10a56,
BASIC c23c618705b74ec3154ba7614cdda6fd7bdc84e71ea55c3b0ef171438f0a91c3.
Published game 2026.9.15.2, source a6112c5. Closed levers checked: earlier
stationary pursuit exclusion almost never activated; this tests distinct timed
combat execution. Buying, targeting and wave following retain v2 behavior.

Hypothesis: ranged heroes spending a short interval backing away after a firing
burst, and all heroes escaping briefly when critically injured, reduce deaths
while preserving fort wins and attack output. This is one combat controller;
component attribution will require later ablation if the complete controller works.

The current league lacks the newly committed hit/cooldown API. Eighteen
stationary tile decisions on one target infer a firing opportunity, never assert
a hit. Full replay instrumentation observes actual basic-hit events separately.
TRUE: fewer deaths, retained attacks/wins, and hits preceding retreats. FALSE:
retreat cancels windup, no useful displacement, or survival costs attack/win output.

Frozen screen: 40 independent fresh seeds719000–719039, four cases per class,
one tested hero plus nine default heroes. All three arms use identical slots,
seeds, config, engine. Require candidate wins >= v2 and default, deaths <=85%
of v2, actual hits >=80%, displacement in >=12 cases, and >=90% normal bursts
preceded by an actual hit within18 ticks. Full120 replay audits before aggregate;
all invalids preserved and exact-input retried. Corrected33 regression checks
across wins, timeouts and death rate overall/each class. Screen is directional.

Critique: floor-tile stationarity can hide sub-tile motion; actual-hit gate checks
this. Walking resets attack windup; hit/output gate catches this. Other units can
cause movement and changing match length confounds raw deaths/hits; report
per-decision rates too, and use win guardrails. Small per-class counts cannot
establish specialization. Exact older public mechanics are isolated from dirty
human-play work and unpublished APIs. No local screen alone qualifies promotion.
A successful screen needs preregistered fresh confirmation and batched hosted XP.

Evals: tmp/gota-ir/kiting-20260915/plan.json (local screen,120 complete games).

Completed all120 games and full replay checks. {"passed": false, "gates": {"parent": {"gain_wins": -5, "passed": false}, "baseline": {"gain_wins": 0, "passed": true}, "survival": {"death_ratio": 1.1794871794871795, "hit_ratio": 0.9477958236658933, "passed": false}}, "activation": {"games": 27, "classes": [0, 1, 2, 3, 4, 5, 7, 8, 9], "verified_bursts": 70, "unverified_bursts": 7, "landed_before_retreat_fraction": 0.9090909090909091}}
The timed candidate did not qualify for league replacement. The newly published hit-counter release motivates the separately preregistered confirmed-hit candidate on fresh seeds; old outcomes are not pooled. Two duplicate audit processes hit their wall-clock limits; both exact tapes passed their other audits and all frozen inputs/checks were revalidated with preserved original instruments.
