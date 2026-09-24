# XP-per-work harvesting candidate

This separate replay61 fork implements the user's score-only direction with
integer target-opportunity ranking. It preserves current control legality and
ranks visible attackable targets by reward divided by ceil(HP/basic damage) plus
travel tiles beyond reach. Rewards are hero150, structure100, exposed god500,
and creep15 as an upper bound before sharing. Current-target preference is5%.

It has no team-win utility. Survival, purchases and returning to lane remain
mechanisms for score. This prototype changes target selection; it does not
pretend to estimate full future opportunity cost. Obstacle paths, spells,
competing last hitters and shared XP still need calibration.

Eight complete responsive candidate games plus eight byte-exact reused controls
pass all ten VM limits, full replay hash/command/XP/score checks. Score totals are
**19,367 → 19,376 (+0.05%)**, with red gains and blue losses. This is not evidence
of a competitive improvement. No hosted games, uploads or league writes use this
candidate. Saved for refinement; do not promote it from these eight comparisons.

The reviewed semantic annotations compile/extract to the exact tested BASIC.
`evidence/native-comparison.json` contains every pair and replay digest;
`evidence/objective.json` records the user steering. Captured initial IR and full
replays remain in `polyworld/tmp/gota-harvest-value61-20260923`.
See `docs/guides/guide-gota-score-analysis.md` for the statistical method.

Run `python verify.py`, or use `convert.py compile --out <new-directory>` and
`convert.py extract --source policy.bas --out <new-directory>`.
