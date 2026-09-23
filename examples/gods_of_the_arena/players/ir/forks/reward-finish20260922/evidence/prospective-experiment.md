# Prefer immediately reachable high-XP finishes

Status: prospective held-out trial, not a validated replacement.

Source `e6bb1eba81233cd5b1757e678b33817ea26e9db283b1ea56f4cf70d2e6e1d4b3`
is generated from the portal controller through binding
`gota-bassy/reward-finish-2026-09-22-r1`. Only observation target utility changes.
The parent's lethal-creep bonus can outrank a reachable one-hit hero. The new
rule favors enemy god (500 XP), hero (150 XP), or exposed structure (100 XP)
finishes over the 15 XP creep pool when observed HP is no greater than basic
damage and public integer distance is within floor(attack range). The range
check is conservative but cannot guarantee contact or kill credit against
moving enemies and simultaneous attackers.

Healthy/two-hit/distant heroes retain parent priorities. Parent safety,
recovery, portals, draft, items, movement and combat templates are preserved.
This excludes the broader spell-pressure edits rejected in the preceding 400
and 160-game studies. It is a new narrow whole-policy hypothesis, not a claim
that a component of those failed bundles was independently effective.

Actual-engine admission requires 140 target/reward fixtures across ten classes
and both colors, 84 portal and 126 broad cases, eight complete responsive native
games, and portable compile/extract equality. The artificial fixture initially
moved a building without its host footprint; that failed capture is preserved.
The corrected fixture uses the real building cell. Native games test runtime,
not performance against unavailable opponent sources.

Frozen before new hosted spending:

- One preselected candidate versus fresh deployed controls, **100 games per
  source/color, 400 total**. No screening or inspected-result control reuse.
- Exact Richard167, khors114 and Jordan411 oppose both colors. Whole teams
  rotate together, one subject in the first team seat; relh161 is a teammate.
- Primary score is `max(0, XP*1440 - 200*ticks)//1440`, including draft.
  Require **at least 10% aggregate gain, each color at least 95% of control,
  and a positive lower 95% bootstrap aggregate-gain bound**. All 400 games must
  pass exact ten-source, all-VM, full-replay, XP and integer-score audits.
- Independent whole-game sampling stratified by color; report draft classes,
  duplicate streams, XP/time decomposition and paired rival score gaps.
  The first four lexical episode IDs per cell supply effect diagnostics only.
- No deployment if the frozen gate fails or the game/champion field changes.
  A passing first-seat fixed-roster result does not establish fallback draft
  superiority, universal rank or future protection against new policies.

Use one shared-journal cycle `interactive-reward-finish-20260922`, maximum 400;
three requests active at most, four batches of 100. The dated September 22 UTC
10,000 allowance is already authorized; normal later-day cap remains 1,600.
Keep all prior captures and failed policies. Raw evidence:
`/Users/aaln/experiments/softmax/polyworld/tmp/gota-finish-score-20260922`.
