# Current Gods of the Arena policy work

Read `games/gods_of_the_arena/current.json`. The active engine is
**2026.9.22.2 / ffcedcd866c4d31924361ed4baff2b7a6d3aba67**, published coworld
`cow_2dd9158a-e22e-4000-9b2b-b060fffa7a9a`. Verify the live league's source,
version and configuration before new hosted work. The research branch preserves
older engine files and studies; build the exact pinned engine through
`games/gods_of_the_arena/instruments/balance20260922/bootstrap.py`.

## Current contract

- BASIC supports decimals and fractional action coordinates. Public position
  observations are global integer cells with complementary team border rules.
  Mirrored movement, navigation, vision, targeting and seeded last-hit ties are
  implemented in the host. Both bundled reference policies use team coordinates;
  that is a controller design, not a restriction on legal global-coordinate bots.
- One shared object/warning frame is frozen for the decision phase. Accepted own
  inventory and ability operations update immediately. Movement plans use the
  same starting state, then move together; collected damage resolves before
  deaths and rewards. Mutual kills and simultaneous fort draws are legal.
- Faction draft bonuses are gone. Ranger HP growth is **19**, Crossbowman base
  damage **69**, and Warlock Dread Totem damage **87**. Read actual stats, ability
  ranks, costs and ranges from the host; do not import an old hero stat table.
- Explicit draft picks and skill-point spending remain required. Keep the public
  availability fallback and ten-second pick deadline. Abilities start locked.
- Shopping requires the friendly keep. Inventory has six slots; consumables
  stack. There is no sell/equipment-upgrade operation. Portals channel for three
  seconds with a 60-second cooldown. Spawn recovery is fast; buyback exists.
- Towers retain updated HP/damage; barracks waves have three melee and one caster.
  Creep XP requires same-floor proximity within six tiles. An eligible last
  hitter receives the 15% reserve; the remainder is shared. Crossbowman attacks
  reach beyond this XP radius, so its practiced farming step remains relevant.
- Fresh actual-engine practice still finds a full movement tick after a landed
  hit shortens Ranger recovery to nine ticks. Same-decision walk+attack is not
  equivalent. This mechanic does not establish a hero's competitive strength.
- Primary league score is integer
  `max(0, lifetime_xp * 1440 - 200 * world_ticks) // 1440`, including draft time.
  Fort outcomes are separate diagnostics. Standings average scores, not win Elo.

## Current IR and completed evidence

The `balance20260922` bundle preserves the complete 400-game screen and all five
IR/BASIC pairs. Every cell has 40 clean games, exact source/VM/replay/XP/integer
score checks and 40 distinct command streams. All four coordinated mirrored
alternatives failed the prospective replacement gate. Geometric symmetry alone
was not retained as a gameplay improvement; blue score regressed.

The selected reference is **`balance-draft20260922`**, source **7631fa32**, binding
`gota-bassy/balance-draft-2026-09-22-r1`. It changes only draft priority to
Crossbowman and retains the deployed post-draft controller. If Crossbowman is
unavailable, it uses the existing public ranged-first fallback. A separate
80-game follow-up scored **2888.975 red / 3273.5 blue**, versus the reused exact
current-engine control's **2337.4 / 2701.975**: **+22.3%** overall, passing both
frozen conditions. All 480 games were valid and fully audited.

This is a fixed first-pick-roster result, not independent confirmation or a
universal hero ranking. The follow-up reuses earlier controls explicitly.
It outscored opposing relh on both colors and Jordan411/Richard153 on red;
Jordan and Richard were teammates in the blue roster, so no opposing blue claim
follows. Check newer opponent versions separately. The source-preserving
current-engine control remains in `balance20260922/control` as rollback.

Do not force team-relative movement merely because it passes mirrored-action
tests, and do not treat the retained global-coordinate behavior as permanently
required. A future controller can change either approach with current evidence.

Use IR as the editing medium. Change current host bindings and policy components
as needed; old tactical rules, opponent v135 identities, old integer-only
compilers and old win gates do not constrain new research. Preserve historical
studies under their original engine and decision rules. Never relabel an old
outcome as a new-engine result, or feed hidden replay truth/policy UUIDs into the
live controller. Failed alternatives remain available with their evidence.

## Evaluation and operations

Freeze exact executable bytes, IR, engine/configuration, opponent UUIDs, seats
and prospective decisions. Use mixed teams and one subject seat for claims about
this league. Compare matched side/roster controls. Default advancement requires
zero invalid games/audit failures, strict aggregate score improvement of at
least 10%, and each cell retaining at least 95% of control. Rival score
superiority, late-draft strength and #1 rank are separate claims. A reused
control cohort must be labeled explicitly; it is not fresh concurrent evidence.

Shared journal limits remain 400 new games/cycle, 1600/UTC day, at most three
active requests, 40–200 games/request. Do not reset a ledger or change limits to
make an experiment pass. Runtime, ownership and evidence safeguards remain even
when historical tactical IR is obsolete. Read the campaign FOCUS/ownership
record before taking the writer; the prior worker is paused during interactive
work. The user's root checkout moved to upstream main and the old LaunchAgent
script path is absent: do not blindly restart an obsolete or missing runner.

Current live registrations are Aaron `0dc85085-cb5b-4de6-8d50-e8fd043d0b5f`
and Coach `35c85505-1977-4bad-b4ea-f1473aaa79dc`, both **7631fa32**, verified
competing/active/champion after normal `auto_champion=always` placement. The
[deployment receipts](../../examples/gods_of_the_arena/players/ir/forks/balance-draft20260922-deployment/README.md)
preserve source hashes, readback and rollback identities. Placement does not
establish later league-round performance. Resolve live versions before new work.
Manual champion selection previously returned HTTP500; normal placement worked.
Do not retire a live champion before its replacement is verified.
