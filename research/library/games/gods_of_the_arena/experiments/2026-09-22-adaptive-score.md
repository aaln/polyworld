# Score resilience against Richard167 and khors114

Status: completed400games; broad candidate rejected after independent confirmation.

User direction: keep optimizing individual points as competitors change, with
Richard167 and Andre von Auto's khors114 as explicit targets. The live snapshot
still uses 2026.9.22.3 / 1b708944, with Aaron first and Andre second. This is a
point-in-time standing, not evidence of durable superiority. The public player
statistics page has not refreshed since 19:58 UTC and describes older replay
versions; do not use it as a current-version counter-policy verdict.

Parent is the deployed portal source db71abb3. Closed levers were checked:
the f6a0dace opportunity bundle lost 9.65% score overall and 22.64% on blue.
Preserve its rejection. This study investigates actual spell damage and combat
uptime while retaining the parent's basic-target and recovery decisions.

Before proposing executable changes, reanalyze the 80 valid baseline games in
the completed score study. They contain the exact Richard167 and khors114
responding against the deployed policy, with no failed VMs and current-engine
source/replay/XP checks. Their comparison is retrospective and roster-bound.
Read the first four episode IDs in lexical order per color for detailed typed
events and position timelines, selected without outcome filtering. Aggregate
the existing economy evidence over all 80. Opponent source ordering remains
unknown; descriptive IR is not an executable opponent proxy.

Measure hero/creep/building/god XP, realized basic/ability damage by victim kind,
accepted spells, ability-specific damage, gold conversion, living field time,
and score decomposition. Rejected attempts alone are not an improvement target.
Keep observations, hidden replay truth, and inferred decision rules separate.
Only public current observations may enter our policy.

Hypothesis under investigation: sharing one target between basic attacks and
every spell wastes damaging abilities when another visible, reachable hero or
creep is a better spell opportunity. A separate bounded spell-target selector
may increase realized hero damage and kill XP without the farming/chasing
regression of f6a0dace. Alternative: splitting fire lowers kill credit or spends
mana on unproductive harassment; fewer rejections alone would not support it.

Before hosted spending, freeze final IR/source, current game and opponent
versions, full roster/seat assignments, host fixture results and decision rules.
Default score advancement is at least 10% aggregate gain with each color at
least 95% of fresh control and zero invalid/audit failures. If multiple
candidates are screened, require a separate fresh confirmation roster before
deployment. Claims about beating each rival need their own paired score gaps.
Small fixed-roster samples cannot establish universal ranking.

Field changes invalidate assumptions: capture current champions and score
snapshot at preparation and completion, bind exact versions within an A/B,
and start a new comparison if a material release or roster change occurs.
Never replace an opponent version midway through a comparison. September22
UTC cap 10000 is already authorized; preserve the shared ledger and cycle400,
parallel3 and 40–200 batch limits. No approval is needed for this allowance.

## Frozen comparison and local evidence

Two separate portable semantic IR/BASIC pairs start from db71abb3:

- spell-targeting: source352b5d93, IR47710194. Nearest visible living enemy hero
  is retained during the existing bounded observation scan. Damaging abilities
  attempt this target independently, falling back to the basic target only
  when the real host rejects the cast. Useful mana restoration is enabled.
- spell-pressure: source5b693e5c, IRbc5c83f9. The same spell behavior plus
  hero basic-target bonus80→480, preserving finishing-creep priority,18-tile
  target search, timing, structure scoring, recovery, portal and tower guards.

Each passes44 meaningful actual-tick spell fixtures,84 portal fixtures and126
all-class host checks. The deployed control passes32/44 new spell expectations;
its missing independent spell targeting and mana restoration are expected
mechanism differences, not invalid executions. Both candidates and control
complete12 native games with full replay/XP/integer-score and VM-limit checks.
Native scores are mixed and blue declines; these games do not estimate strength
against the named hosted competitors. No improvement is inferred from them.

Before spending, freeze240games: fresh control plus both candidates,40percolor,
identical pinned mixed teams within color. Richard167,khors114 and Jordan411
oppose each color. relh161 is a teammate. Screen selection requires10%aggregate
mean improvement and95%eachcolor, zero invalid/audit failures, and chooses the
highest qualifying aggregate. An independently drawn160-game confirmation uses
a different allied/background assignment and the third team seat before any
deployment. The selected exact bytes must pass the same rule there. No passing
screen means no confirmation/deployment. Maximum study spending400games.

Controls use independent random seeds; all comparisons report stratified
whole-game bootstrap intervals, class distributions and duplicate streams.
All ten source hashes, VM exits, full replay hashes, XP components and integer
scores are checked. Rival score differences are paired within each game and
reported separately. Fixed rosters cannot establish enduring #1 rank.

The read-only `field.py` instrument captures game, current champions and
standings at preparation and completion and reports changed versions. New
release or roster evidence starts a new comparison; pinned versions never
change within an A/B. No obsolete background worker is resumed.

## Completed screen

All240games are valid with40distinct command streams per cell. Both candidates
pass the frozen point-estimate rule. Spell-targeting gains10.06% (red8.20%,
blue11.71%); spell-pressure gains13.92% (red19.16%, blue9.26%) and is selected.
Its95%aggregate bootstrap interval is[-4.07%,35.05%], so independent confirmation
matters. khors114 is outscored53/80 versus control41/80; Richard16765/80 versus
57/80; Jordan41170/80 versus68/80. Paired score intervals remain in the report;
khors red includeszero. These are score comparisons, not team-win percentages.

The selected source gains408.75heroXP/redgame and446.25heroXP/bluegame. Red
creepXP rises42.28; blue falls29.30. Additional time costs106.66/red and198.22/blue
points before integer rounding/clamping. Longer games pay only through greater
XP. Basic/ability damage diagnostics from the24 mechanically selected replays
remain descriptive; class/scene mixture differs. No component causality claim.

Current champions and game stayed unchanged across the screen. At22:44UTC
Aaron remained#1 and Andre#2; this standing predates any new deployment.
Confirmation keeps exact source5b693e5c and switches two background players
and the subject's seat. The public draft availability fallback remains active.

Screen limitation: the selected variant's Crossbowman means rise on both
colors, while Ranger is nearly flat on red and lower on blue. Candidate
cohorts also contain more Crossbowman picks. Descriptive standardization to
control class frequencies reduces the selected gain to about8.1%; it does not
identify causal class effects or replace the frozen aggregate gate. This is
an additional reason for the independently prepared later-draft confirmation.
Do not splice a class-conditional controller from these results without testing
the resulting complete policy.

## Independent confirmation and decision

All160confirmation games pass source/VM/full-replay/XP/integer-score audits,
with40distinct streams in each cell. The later-draft roster produces Arcanist,
Lich, Druid and Death Knight instead of the screen's two ranged carries.
Mean score1161.76→1112.93, **−4.20%**, red−13.35%, blue+6.54%;95%gain interval
[-26.43%,24.22%]. The frozen rule fails. **No broad variant is deployed.**
Both original portal champions remain the reference. The screen's higher
Crossbow scores do not validate the broad controller on fallback heroes.

A separate [class-aware experiment](2026-09-22-class-score.md) now narrows the
intervention to Crossbowman and preserves original action paths for the other
nine classes. Its complete source needs fresh controls and independent
confirmation. Old400game results and the two local initial IR pairs remain
unchanged; this is a new hypothesis, not a splice automatically declared valid.
