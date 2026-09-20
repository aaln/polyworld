# Current competitive contract — 2026-09-15

Final campaign readback: **2026.9.15.3**, source
**e1279894d10a7684f303e7a9f1ea2f84c1d14253**, prepared runtime
`tmp/gota-ir/runtime-2026.9.15.3`. The balance changes below remain live. The new
combat observations are now published: `selfAttacksLanded`, `selfAttackCooldown`,
range/damage/speed and visible object targets/velocities. Hit count persists
across respawns. An idle attack cooldown includes its full windup, so waiting
for it to becomezero is not an attack-readiness strategy. The hit-counter edge
is the reliable event for a post-shot retreat; initialize it on first observation
and after decision gaps.

Walking clears attack intent and suppresses automatic target-based offensive
spells. Automatic healing/support/passives still run. The experimental spell
operator tries one charged ready offensive cast after accepted movement and
skips Druid friendly-healing slots. Cast acceptance, basic hits, XP and fort
wins are distinct measures. No kiting candidate met the combined qualification
gates. Canonical v2 BASIC stays byte-identical. Final snapshot shows v2rank3
at1585.103MMR: `tmp/gota-ir/kiting-campaign-20260915/final-league/`.

## Historical snapshot at23:13UTC

At23:13UTC the published game is **2026.9.15.2**, source
**a6112c5d92c1efc86b7b30235c408106bc497242**, runtime
`tmp/gota-ir/runtime-2026.9.15.2`. It contains tower HP900/1200/1800,
damage18/24/30, Warlock restoration24 and Death Knight healing30.
The new `selfAttackCooldown`, `selfAttacksLanded` and object target/velocity
observations in local HEAD are **not published in this release**. Kiting must
use only the older observation surface for league compatibility. Moving clears
attack intent and resets a swing; a normal hit occurs after45% of its class
attack duration. The maximum current windup is16ticks (Crossbowman). A stationary
tile timer is only a proxy; validate actual hits before attributing kiting.
Fresh leaderboard: selected v2 ranks2 at1603.066MMR, red-kite:v13 ranks1
at1657.776. Snapshot: `tmp/gota-ir/kiting-20260915/meta/`.

## Historical contract and experiments before23:13UTC


Published game **2026.9.15.1**, source **5422fb0c4b230ca7bfa57a69e450a369da2dabe9**. The local main branch contains later collision/creep fixes and must not substitute for this release in evaluation. Prepared runtime: `tmp/gota-ir/runtime-2026.9.15.1`. [Source/replay evidence](upgrade-20260915-mechanics.json).

The league snapshot places current v2 third at 1582.9917 MMR and red-kite:v13 first at 1656.3347. These are dated observations; promotion needs fresh roster and game readback.

| Concern | Current contract | Policy implication |
| --- | --- | --- |
| Terminal score | Destroy the enemy fort; every winning teammate gets 1; game-limit timeout gives all 0 | Keep legitimate timeouts in win-rate denominators |
| Map | Competition map preset seed 54, 116 tiles; match seed separately randomizes the simulation | Pin full map preset; derive new waypoints from current geometry when changing movement |
| BASIC self data | Decision-start snapshots; item/object queries are live | Count accepted spending or let host reject stale-budget attempts |
| Basic attacks | Free repeated class-specific attacks; every equipped damage bonus applies for every class | Early damage gear can change last hits and growth; no class lock on item purchase |
| Spells | castTarget(slot,id), castPoint(slot,x,y), abilityCharges/Cooldown/Recharge(slot) | Explicit and automatic bot casts share live resources; do not assume explicit calls disable automatic casting |
| Poison | Uses engine attack target and now checks ordinary range/visibility/exposure | Old unrestricted-poison experiments are historical, not current affordances |
| Equipment | Six slots, no selling, no duplicate gear; HP/mana gear adds current as well as max resource | Five planned equipment items can preserve one permanent consumable slot; consumables still compete for it |
| Terrain | terrainKind/Walkable/Height/WaterDepth with explicit At variants and layer constants | Static terrain is available through fog; hidden enemies are not |
| Walking | Clears attack intent before pathfinding, even if destination fails | Failed commands need not be atomic |
| Replay | New format, explicit spell actions and richer metrics | Use current source reader; the old six-action audit array is obsolete |
| Hosted seed | Results/replay carry effective per-episode seed; game-config artifact can retain nominal seed | Check effective seeds before calling arms matched |

Three public hosted replays reproduced every tick hash using the pinned local runtime. In those tapes, the leader's Berserker, Arcanist and Ranger used an ordered dagger/longsword/armor/axe/spellbook build and healing stock. Our heroes often bought cheaper class-specific gear, and the leader issued substantially more movement commands. This motivates isolated equipment and movement hypotheses; it does not identify the leader's hidden intentions or prove either mechanism causes the ranking.

The new ordered-loadout experiment edits only E2 of exact v2. Its complete named operator and five item parameters are represented in the IR. Generated BASIC can be lifted back to the same IR; an accepted symbolic parameter change invalidates related beliefs for review. Execution parity and observed purchase effects are separate from fort-win evidence.

The pre-existing `layered` wave-local targeting draft is still an untested alternative. Historical September 10 reports remain unchanged and do not establish performance on this release.

## Creator announcement received during this campaign

The user supplied a newer balance announcement: outer/inner/gate HP
900/1200/1800; damage 18/24/30; Warlock Aether Siphon restores 24 mana;
Death Knight Sanguine Chalice heals 30. At the latest read, both the league
manifest and the complete public Coworld version list still designate 2026.9.15.1,
whose source has tower HP 1200/2400/4800, damage 28/56/112, restore 22 and heal 28.
The announcement is therefore a prospective simulation input, not a claim about
the current hosted executable. See `tmp/gota-ir/balance-20260915/runtime.json`
and its exact four-change patch. Additional future release changes are unknown.

Clearing any one complete lane exposes the fort. Compared with the pinned source,
the announced HP values reduce that lane's total tower HP from 8400 to 3900.
This motivates exploiting supported structure opportunities. Existing automatic
bot casting already uses both buffed passives when useful, including while moving.
Adding explicit casts would not be needed merely to receive these buffs.

The equipment screen finished 14/40 versus v2 12/40 and default 10/40, missing its
v2 gain gate. It is not promoted. The current experiment changes only R1 of exact
v2: prefer a nearby exposed fort/tower with a living allied footman nearby and
HP at least 60%. This is distinct from the previously rejected unconditional
structure weighting. All three thresholds belong to the semantic operator and
can be reverse-edited from BASIC with belief invalidation. See
[supported-siege experiment](experiments/2026-09-15-supported-siege.md).


## Glory metric verified September15

`tools/tournaments.nim::gameValues` defines Score as lifetime XP minus100 per
simulated minute, and Glory as that value multiplied by the binary fort-win
score. At24ticks/second: `glory = win * (total_xp -100*ticks/1440)`. Fractional
minutes and negative winning values are retained. Losses and timeouts receive
zero Glory. Average all appearances; for a policy controlling multiple heroes,
average its hero scores within each game first. Missing lifetime XP is invalid
evidence, not a zero. The hosted results in all80 current XP games include ten
`total_xp` values, which the new full-replay XP inspector verifies.

The live league snapshot still uses binary team wins through Elo; Glory is a
separate tournament/evaluation objective. Keep fort-win qualification primary.
Time-efficient last hits are plausible shared improvements: footmen award25XP,
towers100XP, heroes150XP to the finishing hero. Those rewards offset15,60,90seconds
of the penalty respectively, conditional on winning. These are accounting
identities, not a claim that chasing a target is worth the time or risk.

The BASIC host exposes selfLevel and worldTick, but not lifetime XP or final
outcome. Do not invent a `selfGlory` observation. Goals and evidence can represent
Glory while executable decisions use the legal HP, distance, kind, inventory and
movement observations. `G_glory` is now linked to current R1/R2/R4/E2 without
changing the frozen candidate's BASIC. `glory_metrics.py` matches the game's own
Nim scorer on300fixtures; `glory_feedback.py` verifies all lifetime-XP records and
adds retrospective paired diagnostics after primary XP validation. See
[metric contract](glory-contract-20260915.json).
