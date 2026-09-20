# Earlier confirmed-hit kiting, without emergency interruptions
Status: inconclusive

Source reason: ranged attack ranges are4–6.5tiles, while the preceding candidate
only retreats once a threat is within3tiles. Crossbow's16tick windup can allow a
melee pursuer to close from6.5tiles to about5tiles before its first shot. Waiting
for3tiles can discard the first safe retreat opportunity. This is a mechanical
hypothesis, not a proven explanation of the earlier results.

The component probes showed emergency interruptions lost useful pressure:
fullcontroller12/40, no_escape20/40, targeted-with-emergency16/40, v2 22/40.
No variant qualified. Preserve those results. The next2x2 discovery matrix holds
critical_percent=0 and retreat_ticks=10 fixed, varies threat_tiles3vs5 and
observed-aggro filtering offvs on. Each factor contrast changes only one thing;
interactions remain explicit. The existing no_escape(all,3) cell is reused
without rerunning. Three new cells: early_all(all,5), targeted_only(aggro,3),
early_targeted(aggro,5). No tuning or partial stopping after launch.

TRUE: earlier post-hit movement preserves range, improves survival and retains
attacks/wins; actual-aggro filtering may prevent needless movement. FALSE:
moving too early loses firing opportunities or objective presence, reducing
wins or hit output. Filtering may react too late to an approaching threat.

All cells use the same inspected40 independent seed/seat cases721000–721039,
nine default companions/opponents, pinned published2026.9.15.3 and exact v2.
This is explicitly adaptive discovery, NOT independent confirmation. Thresholds
stay fixed: wins>=22v2/18default, deaths<=85%v2, hits>=80%v2, displacement>=12cases,
100%normal retreats after actual hit within1tick, no corrected regression flag.
Complete all120 new games and replay checks before choosing a cell. If multiple
pass, rank by wins then lower deaths per game minute; no class-specific selection.
Any selected cell requires fresh, preregistered confirmation and hosted N-episode
batches with fixed incumbent versions. A failure is retained, not renamed success.

Critique: reused seeds and several candidate cells invite overfitting; strict
fresh confirmation is mandatory. Aggregate survival can mask class regressions;
report all classes. Raw hit counts vary with match duration; report hit rate as
well, preserving the original gate. Accepted movement is not actual displacement.

Completed every new game and tape. {'early_all': {'wins': 17, 'deaths': 124, 'hits': 2255, 'passed': False}, 'targeted_only': {'wins': 20, 'deaths': 137, 'hits': 2451, 'passed': False}, 'early_targeted': {'wins': 19, 'deaths': 141, 'hits': 2596, 'passed': False}}
Selected for fresh confirmation: None. No league change.
