# Current priority: beat Richard and Jordan, attain and retain league #1

Latest user instructions, 2026-09-20:

> ensure this policy can also beat richard's policy
> aaron-gota-ir-j268-redrace-0920:v1
> reactive coach's membership instead of a-aron
> we must beat richard and jordan and be the #1 on the leaderboard. ensure we have a policy that can do so. Keep checking every 3 hours to ensure we are/get/have a winning policy that can do so

This supersedes older Jordan-only priority and stale deployment prose. Continue
autonomous IR research, fresh evaluation and evidence-supported upgrades for
Aaron and Coach. The user has authorized improving their live policies; do not
ask for the same authorization again. Do not deploy an unvalidated candidate or
relax existing frozen gates. Do not re-enter a-aron: the account has a two-player
league limit. Preserve Coach and Aaron as the active pair.

Read LEAGUE_STATUS.json and LEAGUE_STATUS.md at startup and before every new
experiment. A separate read-only LaunchAgent refreshes these every10,800seconds.
Its reports identify current exact champion UUIDs, ranks and completed league
losses from the latest12rounds. These observations require replay auditing before
causal claims. An old version's wins do not prove a win against a new opponent.
If the report is older than three hours while the machine is awake, run:
`/Users/aaln/experiments/softmax/metta/.venv/bin/python /Users/aaln/experiments/softmax/polyworld/tools/gota_autoresearch/league_watch.py`

At07:25UTC Aaron was #1, Richard #2, Jordan #3, Coach #4. Ranking and matchup
success are separate measurements: the deployed executable just lost0W40L on
each color against exact Richard135. Do not call the combined objective achieved
because an old accumulated ranking is #1. Preserve the rank with general play
and repair the exact matchup. Continue checks after success as opponents evolve.

## Exact deployed primary IR

Both players currently use the same Jordan-counter executable:
`be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`.

- Coach player ply_594ec24d-d7f3-4370-a000-468354ec41c9;
  policy00cd9483-0309-4613-bf61-89f3f4a33d01,
  aaron-gota-ir-j268-redrace-0920:v1;
  restored membership lpm_3954a540-f536-4ef3-98a4-44847647711a.
- Aaron player ply_630a768f-d623-44b2-80fa-36968d6fa75a;
  policy4cdbbf36-3d70-4ea3-8aed-c92ee0e024be,
  aaron-gota-ir-j268-redrace-0920-aaron:v1.
- Richard135:7c370daf-3c5f-42f8-870b-54b79c495a44.
- Jordan268:207ffaf9-0d1e-4d92-a15d-4352f1bddec2.

Source bundle:
`/Users/aaln/experiments/softmax/polyworld/examples/gods_of_the_arena/players/ir/forks/jordan268`.
Use its policy.py / policy.ir.json as a lineage-preserving research branch when
repairing the deployed policy. Its fresh Jordan268 confirmation was40/40red and
40/40blue with full audits, repeated fixed-lineup trajectories. Compiler bindings
are in the bundle/compiler archive and
`polyworld/games/gods_of_the_arena/instruments/jordan268_counter/contracts.py`.
Import the versioned contracts before compile/extract. Never edit old bindings.
Campaign formal accepted snapshot0000-b269 remains unchanged; a separate deployed
branch is not automatic acceptance by the broader researcher.accept gates.
Any candidate developed from the accepted branch must also outperform/preserve
this currently deployed branch; beating only the older weak parent is insufficient.

## Active interactive Richard study: resume, do not duplicate

Study `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/richard-counter-20260920`.
Code `polyworld/games/gods_of_the_arena/instruments/richard_counter`.
Record `polyworld/games/gods_of_the_arena/experiments/2026-09-20-richard135-counter.md`.
Read HANDOFF.md in the study for current executor ownership before acting.
Existing baseline: parent red40/40losses, blue40/40losses, all fully audited.
Two critical-defense candidates and one red-equipment candidate are uploaded
inertly. Existing requests, uploaded versions and results are in the study's
requests.json and candidates/; use stored receipts, not new duplicate XP.
The interactive controller is serial. Do not run another collector on a live
arm. Once handed off, reuse completed artifacts and continue the exact experiment.

Mechanism: Jordan counter cancels distant recall. Richard's split two-hero
near-core attacks bypass its4-enemy alarm while our heroes remain far away.
Critical40/60 allow1200ticks remote recall for an anchored near-core pair.
Red additionally loses early frontliners and XP; weapon tests the existing
red_loadout progression independently. These are hypotheses, not proven repairs.
Fresh tests must retain the deployed policy's Jordan wins on both colors.

Frozen target-specific gate: Richard135 >=30/40 actual wins EACH color and
>=8aggregate wins gained vs fresh deployed control; Jordan268 >=38/40 EACH;
six pinned field rivals (relh154,g002v1,black-kite16,macro4,red-kite34,vanguard1)
candidate/control8percolor, no more than2lost wins per rival/color and no
aggregate regression; enlarge ambiguous field arms before deciding. Small
four-game discovery screens cannot qualify a promotion. All10VMs, full replay
hashes/actions, source/IR parity, game/config/roster and score/XP checks required.
If either rival upgrades, freeze new exact UUID arms prospectively, retain old
results and test current champions too. Never weaken an existing gate after seeing
its result. Broad campaign acceptance retains all its original stricter gates.

Only after fresh confirmation and field preservation: produce feedback in native
seven-layer Python IR, compile/extract parity and immutable source/evidence
snapshot; register player-specific bytes, document the exact decision, update
the intended Aaron/Coach champion(s), monitor qualification, and verify the
active pair. Preserve prior receipts and an exact rollback version. The latest
user authorization covers these validated upgrades. Report the actual achieved
win counts and live rank, including failures and limits. No guaranteed future wins.

The three-hour monitor does not launch competing researchers or buy XP. The
existing single supervised worker handles research and retries. Keep all original
episode budgets and frozen gates. Finish pending local work safely and use its
findings, but prioritize unresolved Richard losses and preserving Jordan gains
over another Jordan-only or self-play-only study. Read this file before the next
expensive request. Keep an exact checkpoint so a cycle ending cannot lose work.
