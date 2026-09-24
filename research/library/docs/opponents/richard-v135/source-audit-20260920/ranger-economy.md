# Richard v135: items, leveling and the Ranger

Richard's Ranger combines generic damage equipment with fast post-hit recovery. He does not have a Ranger-specific leveling routine. The engine grants XP and gold to the hero delivering the kill, and levels that hero automatically. In our archived matchup his Ranger starts slowly, then gains most of his final XP from killing our heroes.

These findings combine the exact v135 BASIC with a logging-only overlay of game `2026.9.16.5`. All 20 original games again matched every replay state hash and consumed every action. XP, gold and level arithmetic reconciled for **all 200 hero-game accounts**. [Machine-readable audit](economy-audit.ir.json), [source model](source-model.ir.json).

## Purchases: ordered attempts with real affordability checks

The source has two equipment branches, chosen with the neural mode. **All 601,050 audited Richard decisions selected `objectiveBuild=1`.** That branch applies the same checks to every class, including Ranger (class 1) and Crossbowman (class 6):

| Check order | Item / ID | Cost | Pinned effect |
|---|---|---:|---|
| 1 | Crimson Dagger / 11 | 110 | +8 basic damage |
| 2 | Sunsteel Longsword / 13 | 150 | +10 basic damage |
| 3 | Knight Armor / 16 | 160 | +120 maximum HP |
| 4 | Battle Axe / 18 | 180 | +14 basic damage |
| 5 | Arcane Spellbook / 20 | 190 | +12 basic damage, +30 maximum mana |

The “armor” item increases health; it does not reduce incoming damage. Increasing maximum HP also increases current HP by the same amount in the pinned engine. Equipment names do not restrict class eligibility: the spellbook adds basic damage to Ranger too. Five items give +44 damage, +120 HP and +30 mana, leaving one of six slots for a consumable.

This is a sequence of `if` checks, not a guaranteed one-item-per-turn plan or a rule to save for the next item. The policy tests missing items and predecision `selfGold`; the host checks current gold and inventory at each request. At initial 150 gold, Ranger buys the 110-gold dagger first; a same-turn sword request cannot spend the original 150 again. Multiple purchases can succeed when funds and slots permit. Health purchases happen before equipment and can delay it.

The unused-in-this-corpus normal branch has class-specific choices: Ranger and Crossbowman try Ranger Boots, Ranger Bow and Rune Crossbow. Reading that source branch alone would give the wrong description of the observed v135 build. No Richard hero bought those three items, a mana potion or a poison potion in these 20 games. Across all Richard heroes, **1,410 accepted purchases** came from 2,116 recorded buy requests; attempts must not be counted as inventory acquisitions.

Source: [v135.bas](v135.bas), lines 361–516. Game definitions: pinned `content.nim` item table and `sim.nim` `purchaseReason`, `applyBuyItem`, `refreshHeroStats`. Buying requires a living hero, money and inventory capacity; it does not require returning to a shop. Equipment duplicates are rejected; consumables can stack subject to capacity.

## Healing competes with equipment for income

The inventory scan uses carried healing items below **60%** HP. Below **50%** HP with no heal item observed, the policy attempts a Vitality Elixir (50 gold, 90 heal), then an Ironroot Ration (30 gold, 40 heal). Both attempts can be accepted when there is enough money and space; the scan's `hasHeal` value does not update after the first purchase. Newly purchased items are normally encountered by the next decision's scan.

This explains bursts of potion spending during fights. In the representative Ranger trajectory, the sword is delayed until tick 3824; there were accepted healing purchases at 1413, 1868 and 2981 first. Late in the game, repeated elixir purchases turn accumulated kill gold into survival. A counter that merely chips the Ranger may allow this loop to continue. Whether concentrated pressure or forcing consumable expenditure improves our outcome needs a responsive experiment.

## Leveling: rewards, not skill-point allocation

| Killing blow on | XP to the killing hero | Gold to that hero |
|---|---:|---:|
| Creep | 25 | 15 |
| Enemy hero | 150 | 100 |
| Building, including barracks | 100 | 75 |

Basic attacks and damaging spells can earn these rewards. The pinned code assigns them to the damage-dealing hero on the lethal transition; it does not distribute nearby shared XP or assist XP. There is no passive income in these reconciled accounts. The XP needed to advance from level `L` is `100 + 75*(L-1)`, up to level 20. Total XP thresholds are level 2: 100, level 3: 275, level 4: 525, level 5: 850, level 6: 1250, level 7: 1725, level 8: 2275, level 9: 2900, level 10: 3600.

V135 reads `selfLevel` into a neural input. It never explicitly issues a level-up, buys a level, allocates skill points, or reads total XP. Better leveling therefore comes through access to rewarding targets, successful damage and survival, not an unseen leveling command. The source does not prove an intentional last-hit optimization algorithm.

Ranger starts at 200 HP, 25 basic damage and 110 mana; each level adds 38 HP, 6 damage and 8 mana. His base basic range is 330,000 world units (5.5 tiles), and nominal attack period is 18 ticks. At level 10 with the five-item build: maximum HP is 662 and basic damage is **123 = 25 + 9×6 + 44**. Equipment and levels both matter.

## Ranger's actual progression against our archived red control

Richard has Ranger only on his blue roster in these uniform-team games. Six of the 20 games place him there; all six have an identical published Ranger trace. Treat this as **one repeated Ranger trajectory**, not six independent successes. Other actors create four distinct complete economy streams among those games.

Representative episode: `ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686`, Ranger actor 106, terminal tick 8517. IDs describe this replay only, not a policy predicate.

| Tick | Verified event/state |
|---:|---|
| 1 | Dagger purchased from initial 150 gold; basic damage becomes 33 |
| 1000 | Still level 1, 0 XP, 40 gold |
| 1384 | First reward |
| 1876 | Level 2 |
| 2000 | 100 XP from four creep kills; level 2 |
| 3000 | 150 XP from six creep kills; level 2 |
| 3809 | Level 3 |
| 3824 | Sword purchased for 150 from 160 gold |
| 4000 | 400 XP: ten creeps and one hero; level 3 |
| 5044 / 5097 | Levels 4 / 5 |
| 5056 | Knight Armor purchased from exactly 160 gold |
| 5718 / 5719 | Level 6, then Battle Axe purchased |
| 6419 / 6558 | Level 7, then Arcane Spellbook purchased |
| 7689 / 7978 / 8313 | Levels 8 / 9 / 10 |
| 8517 | 4025 XP, level 10, 640 gold, 123 basic damage; two deaths total |

Final rewards reconcile exactly: **47 creeps ×25 + 17 heroes ×150 + 3 buildings ×100 = 4025 XP**. Hero kills provide 2550/4025, or 63.4%, of the total. This is a later combat snowball, not evidence of excellent early farm. In the same trajectory our Death Knight finishes level 2 with eight deaths and 12 basic hits; our Crossbowman reaches level 7. Avoid feeding repeated isolated deaths while measuring whether we can convert the Ranger's early weakness into useful pressure.

## His Ranger is already using the attack-recovery improvement

At source lines 661–666, a new confirmed basic hit triggers `walkTo(selfX,selfY)` after the ordinary commands. On the following decision ordinary attacks can resume. The pinned no-target movement branch resets swing state; this avoids waiting out the full normal recovery without canceling the preceding windup.

The replay measures this directly: Ranger hits hero 100 at **1393, 1402, 1411, 1420, 1429**—nine ticks apart—and then hero 103 at 1438, 1447, 1456. Of 62 intervals between consecutive hero-target basic hits on the same target, 58 are nine ticks. This histogram is not conditioned on continuous in-range eligibility, and long gaps include disengagement. It nevertheless shows that the “18-tick Ranger” assumption substantially understates his realized close-contact damage rate.

The source author's earlier handoff independently describes the v123 introduction of this technique: an isolated Ranger probe changed 18-tick to nine-tick intervals, followed by hosted comparisons. Those historical results concern a predecessor and different matchups; our exact-v135 ledger is the direct evidence here. Historical notes also report that an opening-farm patch regressed later outcomes and that axe-before-armor had no measured farm benefit in its bounded probe. Do not repeat either as an established solution. [Pinned historical excerpt](ranger-history-excerpt.md).

## Implications for the counter session and future IR

Add candidate `Richard135_C05` from [counter-hypotheses.ir.json](counter-hypotheses.ir.json): measure whether coordinated early pressure and preventing repeat hero deaths can delay Ranger's sword/levels without sacrificing our own XP or home. Track accepted purchases, per-target kill rewards, level milestones, post-hit cadence, potion spending and both teams' damage/deaths. Compare against the same responsive opponent; a lower Ranger level at one early checkpoint is insufficient if he catches up and wins.

Separate an economy fix from a cadence fix. Matching the item names alone cannot establish equal DPS: levels, range uptime, attack recovery, spell effects and the ability to spend kill gold on healing all differ. Any recovery change to our policy must preserve spell/defense precedence and validate actual hit intervals; blindly issuing movement every tick can prevent attacks.

For future observation IR, record item appearance and level changes as their own events with visibility censoring. When only public inventory is visible, an item first seen is not an exact purchase timestamp. Likewise, a level change identifies a threshold crossing, not the unobserved source of XP. Keep actual accepted purchases and reward attribution in a separately labeled truth/source audit such as this one.
