# Blue central route against khors v114

Status: local admission passed; hosted comparison being prepared. User requests better blue play against Andre's khors114.
Parent is the newly deployed core-buyback policy67fdcd5d, reviewed IRc1a5839b.
Active game2026.9.22.3/replay58/engine1b708944 is freshly verified unchanged;
khors114 andRichard174 remain current. Prior failures and captures are preserved.

## Diagnosis and intervention

Reanalysis of all200 prior candidate games separates class and color. On blue,
our Ranger averages15.33 hero kills versus khors23.92, while creep XP is
2362.96 versus1958.06. Our Crossbowman averages17.35 versus20.92 kills and
2987.71 versus2407.75 creep XP. Khors leads hero XP within both class slices.
These are retrospective associations, not matched class interventions.

The four blue replays selected prospectively for the previous study's effects
show our hero still level1 after one minute on the northwest outer lane; khors
is level2/3 near center. Minute-position plots connect sparse samples, not
exact paths. The generated advance rule routes ordinal0 toward(mapWidth/10,
mapHeight/10) on both teams until crossing, while the center offers a different
set of early encounters. This suggests an opportunity-access issue rather than
simply increasing target priority. Prior broad targeting and coordinated
mirroring bundles failed; do not import those changes.

Change R_advance: blue team ordinal0 on Ranger or Crossbowman uses the
center waypoint before crossing. Existing combat, defense, retreat, recovery,
buyback and portal actions keep priority. After crossing, advance normally.
Coordinate R_base_recovery_intent for the same blue lead ranged context: when
newly critical in the keep, force immediate thinking and release the movement
throttle before local recovery. The route-only r1 escaped the keep on a persisted
advance command and then used a scroll in2/84portal fixtures. Preserve that
failed local source; the coupled r2 must pass all84.
All red, other ordinal and other class behavior is unchanged. No opponent UUID,
hidden position or reconstructed replay state enters the live controller.

If useful, the actual host issues the central opening command only in those
two contexts, early contact/hero XP rises, and final individual XP-minus-time
score improves. If harmful, shared XP dilution, fighting stronger opponents,
extra deaths or lost creep farming outweigh new opportunities. A shorter route
or faster first kill without final score improvement does not qualify.

## Prospective decision

Practice100 opening contexts(ten classes,two colors,five ordinals) for both
sources; inherited180buyback,84portal and126broad cases; eight complete native
matches(two sources,two colors,two seeds). Verify exact red native trajectories
are unchanged and portable IR compile/extract equality. Native wins only test
runtime; rivals are not available as executable source.

Run one preselected sourcec02f8cb6 versus fresh deployed-source controls:
400games,100/source/color, exact mixed roster and whole-team rotation, subject
in first team seat, khors114/Richard174/Jordan411 opposing both colors, relh161
and JuliaB5 teammates. No old controls, no retuning, no mid-cohort substitution.
Zero all-ten-source/VM/full replay hashes/XP/integer-score audit failures required.

Advance only if all hold: aggregate mean score>=110%control; each color>=95%
control; lower95% side-stratified independent whole-game bootstrap aggregate
gain>0; lower95% blue-only independent whole-game bootstrap gain>0; candidate
blue mean own-minus-khors114>0. Report rival difference confidence intervals and
outscore proportions separately; a positive mean does not prove certain
superiority. No #1 or later-draft claim. Same game and principal champions must
remain unchanged(ours,khors,Richard,Jordan,relh); report background changes.
All thresholds are frozen before hosted data. No added samples to rescue a miss.

Budget:400new games in one cycle interactive-blue-center-20260923. Shared
September23UTC ledger starts960/1600, leaving640; after this trial1360/1600.
Parallel3,batch100. The legacy worker stays paused. Completed source/IR/results
are saved and only a qualified exact source may replace both authorized players.

## Design critique

Routing changes the encountered population and teammate XP sharing; those are
parts of the intervention, not reasons to ignore an unfavorable result.
Within-class summaries are descriptive because draft order and other hero
assignments vary with seeds. Red executable equivalence does not justify
reusing old red controls; use fresh concurrent arms.100games/cell can resolve
large effects but may leave modest gains inconclusive. Preserve duplicate
streams and use independent whole-game resampling, not fictitious paired seeds.
Fixed first-team seat intentionally exposes this public ordinal0 rule; other
ordinals must remain unchanged in local checks. There is no claim that a
later-draft policy improved. First4lexical episode UUIDs per completed cell
receive detailed effect/route analysis; this subset is diagnostic, not a holdout.

Raw inputs:polyworld/tmp/gota-blue-khors-20260923. Preserve original parent
trial, source, local IR and portal coaching session2026-09-22t16-43-56-076z862811.

## Local admission result

Final r2 sourcec02f8cb6, initial IRf82ba63e.100opening,180buyback,84portal and
126broad checks pass(490 total); all8complete native games pass source/runtime,
replay and XP checks. Both red native seeds produce identical full command
streams and terminal states. Maximum14954instructions/22020work. Portable
compile/extract reproduces the exact source and semantic IR.

Initial r1 route-only source5273b04c failed2keep20portal cases and remains
preserved under initial-r1 with its own native results. The shared test harness
initially queried read-only mapWidth as a mutable BASIC global; both sources
failed that query. Using the host's mapTiles accessor repairs the fixture without
changing policy bytes. Native scores are mixed and are not rival evidence.
