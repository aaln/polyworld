Gods of the Arena: human playability review, inspired by Pudge Wars

Reviewed September 14, 2026. GotA checkout: `d03d2d1`; Pudge Wars checkout:
`debc196` in `/Users/aaln/experiments/softmax/polyworld-pudge-wars`. The latter
also has an existing local edit to `players/base.bas`; teammate observations
below describe that working tree. This document records the original review.
The subsequent implementation covers controls, command feedback, owned HUD,
camera follow, ability previews/tooltips, guided bot matches, combat feedback,
respawn/results/rematch, and team calls. Shopping was explicitly excluded by
the user. See [human play instructions](../examples/gods_of_the_arena/human_play.md).

The most valuable transfer from Pudge Wars is its explicit conversation with
the player: what you control, what your next click does, why an action failed,
and how to get back into the fight. GotA already has much of the underlying
gameplay. Its main gaps are in exposing that gameplay consistently.

I compiled both current native clients and inspected their opening screens at
1440×900. The control findings come from tracing the input, UI, and simulation
code, supplemented by the existing GotA spell tests, which passed. This is a code and rendered
UI review, not a completed human match or a measured usability study. The
screenshots are local artifacts: [GotA opening screen](../tmp/gota-playability/gota-start.png)
and [Pudge Wars opening screen](../tmp/gota-playability/pudge-start.png).

Existing strengths matter here: GotA already has movement click markers,
accurate mesh picking, a minimap, health bars with delayed damage trails,
selection and occlusion outlines, manual abilities, cooldown numbers, charge
counts, spell telegraphs, and a shop with item descriptions and rejection
reasons. These should be extended. Pudge's older `human_play.md` and
`playing_with_friends.md` are not reliable descriptions of every current
binding: its implementation now uses WASD movement and X to stop.

| Priority | Improvement for GotA | Pudge Wars precedent | Expected benefit |
| --- | --- | --- | --- |
| First | Consistent cast, attack, inspect, and cancel controls | Explicit targeting states; LMB confirms, RMB/Esc cancels; quickcast option | Fewer accidental attacks and ambiguous clicks |
| First | Explain every rejected command | Immediate block reasons plus simulation result feedback | Players can distinguish unavailable actions from broken inputs |
| First | Keep the owned hero's controls visible and provide camera follow/recenter | Owned/inspected distinction, F1 center, L follow, camera grab | Less time recovering the hero or the correct command panel |
| First | Ability tooltips and previews before casting | Ability descriptions, readiness labels, range/aim overlays | Players can learn and aim without external documentation |
| Next | A guided first match and readable objectives | Stock bots, seat selection, difficulty presets, clear arena objective | A playable entry point without command-line setup or MOBA knowledge |
| Next | Faster shopping during combat | Contextual shop and hotkey purchases | Less time obscuring the battlefield |
| Next | Personal combat feedback, respawn, result, and rematch flow | Damage/heal numbers, combat sounds, respawn countdown, end screen | Clearer consequences and a reason to play another match |
| Later | Team pings, cooperative bots, takeover, hosted play | Pings consumed by bots, seat handoff, lobbies, reconnect | Human-agent team play and easier play with friends |

**1. Make control intent explicit.** GotA currently has three spell behaviors:
self abilities fire on key press; other abilities may immediately use the
selected object or the hero's existing attack target; remaining ranged/area
abilities arm for a later right-click. Clicking an ability icon always arms it,
including self abilities. Left-clicking an enemy both selects it and orders a
basic attack. Thus the keyboard and HUD versions of the same ability can have
different interactions, and an inspection click can start a chase.

Use one targeting state shared by keys and HUD buttons. The recommended mouse
preset is RMB for move/attack, LMB for inspection or confirmation of an armed
action, RMB/Esc to cancel targeting, and Q/W/E/R for abilities. Self abilities
should activate consistently from either key or icon. Offer quickcast at the
cursor as a setting. If casting at the existing combat target remains useful,
make it an explicit assist option with a visible target rather than an implicit
consequence of the last selection.

Wire attack-move and stop into that preset. `attackMoveArmed` is initialized and
cleared but never set true in the current graphics code, so the existing
attack-move path is unreachable through those controls. There is also a hidden
binding constraint: shared `inputs.nim` maps A/D/S to left/right/middle mouse
buttons. A conventional A attack-move or S stop cannot simply be added on top.
Move those aliases behind a named accessibility/control preset, and make the
displayed bindings come from the same map used for input.

Pudge's current WASD steering is worth a separate optional preset, especially
for players who prefer direct movement. It requires alternative spell bindings
because W already belongs to GotA's four-ability row. It also needs release,
focus-loss, menu, and targeting behavior defined together. Preserve the mouse
preset while evaluating this option; copying Pudge's keys verbatim would create
conflicts.

Sources: [GotA controls](../examples/gods_of_the_arena/controls.nim),
`activatePlayerAbility`; [GotA graphics](../examples/gods_of_the_arena/graphics.nim),
`updatePlayerSpells`, `updateWorldSelection`, `updatePlayerOrder`;
[mouse aliases](../src/polyworld/inputs.nim). Pudge equivalents:
`human.nim:handleHumanInput`, `beginHookCommand`, `cancelAim`, and `keybinds.nim`.

**2. Answer failed actions.** GotA's command queue already receives a boolean
from every simulation operation, but only purchases produce a UI receipt.
The armed-spell path silently returns when the hero is dead, lacks mana or
charges, or is on cooldown. Targeted casts outside range are rejected by the
simulation, while ground casts are clamped to range. Without an explanation or
preview, those distinct outcomes are hard to understand.

Show a brief reason near the ability row: “Need 20 more mana,” “Ready in 2.1s,”
“No charges — next in 4s,” “Target out of range,” or “Respawning.” Give attack
orders a target acknowledgment as well as the existing move marker. Keep
same-frame input acknowledgment separate from authoritative acceptance: a click
marker means the input was received, not that pathfinding necessarily succeeded.

Generalize the purchase-receipt mechanism to command results. Prefer rejection
reasons computed by the same validators that apply commands, so UI rules cannot
drift from gameplay. Preview validation can improve immediacy; the final command
still uses the normal deterministic path. Do not add queues that unexpectedly
fire spells seconds after a failed attempt.

Sources: [command application and receipts](../examples/gods_of_the_arena/controls.nim),
`flushPlayerCommands`; [simulation](../examples/gods_of_the_arena/sim.nim),
`castAbility`, `applyUseItem`, `purchaseReason`. Pudge equivalents:
`human.nim:hookBlockReason`, `rejectReason`, `drainIntentResults`, `humanErrorLine`.
Pudge has some generic failures too; adopt the mechanism and improve specificity.

**3. Keep the hero and its controls available.** GotA's main detail panel follows
the inspected selection. Inspecting an enemy replaces the hero's abilities with
that enemy's details, while Q/W/E/R still operate the owned hero. The inventory
already remains tied to the owned hero. Pin the hero's health, mana, abilities,
and consumables during play, and show inspected targets in a smaller secondary
panel. Remove actionable hotkey labels from read-only enemy details.

Add F1 to select/recenter the owned hero and a visible follow toggle. In current
player mode, portrait clicks start a finite camera ease; ordinary movement does
not continuously follow the hero. Retain arrow/minimap/MMB pan and fullscreen
edge scrolling. Pudge's hold-a-key camera grab is useful for trackpads; implement
it through the binding map. Recenter on respawn, with a clear option to return
to following after manual panning.

The opening GotA capture also shows overlapping ally labels at spawn and camera
space beyond the map edge. Make the local hero's “YOU” marker persist independently
of selection, de-emphasize overlapping ally labels, and frame the hero with its
exit route visible. Both captured HUDs have small text, so use Pudge as a behavior
reference rather than assuming its exact sizing is ideal.

Sources: [GotA HUD](../examples/gods_of_the_arena/ui.nim), `detailId`,
`inventoryHero`, `drawHeroPortrait`; [GotA camera](../examples/gods_of_the_arena/graphics.nim),
`playerMode`, `playerHeroFrame`, `updateCamera`;
[camera easing](../src/polyworld/rtscameras.nim), `advanceCameraEase`.
Pudge equivalents: `human.nim:isOwnedInspect`, `syncInspectToHero`,
`handleHumanInput`; `graphics.nim:updateCamera` and `emitCombatFeedback`.

**4. Teach abilities at the point of use.** GotA displays icons, charges,
cooldowns, and recharge progress, but its ability wells do not explain the
ability name, effect, target rules, mana cost, or range. Those details already
exist in `AbilitySpec`. Generate tooltips from those values and add one short
tactical explanation per ability. Readiness must include mana and charges, not
just the cooldown sweep. Explain what a charge is and when the next one returns.

While targeting, display the actual reachable area and impact footprint,
including rings, cones, lines, and self-centered effects. Preview range
clamping and invalid targets. GotA already draws authoritative spell footprints
after a cast begins; reuse that geometry before confirmation rather than drawing
a decorative approximation that disagrees with the hit test.

The first ability slot is internally named `PassiveAbility`, but human heroes
use manual spells and Q activates that slot too. Player-facing explanations
should describe what actually happens. A clearly labeled optional assist mode
can help new players, but should not silently change who decides when to spend
mana or charges.

Sources: [ability definitions](../examples/gods_of_the_arena/content.nim),
`AbilitySpec`, `HeroSpecs`; [spell rendering](../examples/gods_of_the_arena/spelleffects.nim),
`footprintSettings`, `drawSpells`; [human seat setup](../examples/gods_of_the_arena/bots.nim),
`loadBots`; `sim.nim:tryCombatAbilities`. Pudge equivalents:
`ui.nim:drawHudTooltip`, `drawBottomUnit`; `human.nim:drawHumanOverlays`.

**5. Give the first match a clear beginning and objective.** GotA's normal
entry point requires a human slot and exactly nine supplied bots. Pudge can
fill stock bots and exposes seats and difficulty presets. Add “Play vs bots,”
a hero card with role and four readable abilities, and a practice difficulty.
Crossbowman or Ranger is a reasonable starting candidate to evaluate; hero
selection should respect the current team/class roster rules.

Start practice with the player ready at spawn, then teach a short sequence:
move out, follow a friendly wave, attack an enemy, cast once, and buy a useful
item. Present one prompt at a time and allow skipping. Mark a suggested lane
and the next attackable objective. Explain tower protection in place: “Destroy
the outer tower first,” then “Destroy the inner tower,” then the gate and fort.
Keep the next objective distinct from the current attack target. The UI should
use known map information and team visibility for enemy state.

Pudge difficulty is implemented with decision intervals and hook aim noise.
GotA's bots also benefit from automatic combat abilities, so merely reducing
their BASIC decision frequency would not slow every automated combat action.
Use explicit practice policies/assistance settings and evaluate challenge in
actual matches before choosing defaults.

Sources: [GotA setup](../examples/gods_of_the_arena/game.nim), `usage`,
`parseGameOptions`; `sim.nim:towerExposed`, `fortExposed`, `tryCombatAbilities`.
Pudge equivalents: `game.nim:findStockBot`, `applyDifficulty`; `ui.nim:drawNetLobby`.
The guided sequence and lane objective guidance are new GotA proposals, not
claims that Pudge has a complete tutorial.

**6. Make shopping compatible with fighting.** GotA has a useful, data-driven
catalog and specific purchase reasons. However, opening it covers almost the
entire battlefield while the battle continues. Present a compact recommended
set first: sustain, damage, and durability/movement, with a full-catalog toggle.
Show affordability and before/after effects. Keep warnings and the hero's vitals
visible. For solo practice, optionally pause on shop-open; this must be explicit
and must not become a global pause in future multiplayer.

Expose all six inventory slots with clear use/equipped states. Currently F/G
operate physical slots 0/1, while all six can be clicked; an early equipment
purchase can occupy a hotkey slot even though equipment is passive. Either bind
all slots visibly or provide stable active-consumable bindings. Teach that
equipment applies immediately and that buying is allowed anywhere. Do not copy
Pudge's stand-on-the-shop-pad rule into GotA.

Sources: [shop](../examples/gods_of_the_arena/shops.nim), `drawShop`;
`graphics.nim:onButtonPress`; `ui.nim` inventory handling;
`sim.nim:purchaseReason`, `applyUseItem`. Pudge equivalents:
`ui.nim:drawShopPanel`, `drawInventoryPanel`, `carriedShopItems`.

**7. Make combat outcomes and the next match legible.** Extend GotA's existing
health trails and spell effects with restrained personal damage/heal numbers,
hit confirmation, a low-health signal, and a short kill/objective feed. Pudge
already derives combat feedback from tick changes and limits sound to the player
and current camera. That is a useful starting point for controlling noise in
GotA's larger battles. Its audio is opt-in/muted by default; HUD error buzzes
and a full announcer are not implemented precedents.

Add “Respawn in N seconds,” the known killer/cause where available, and a camera
return when the hero revives. GotA already simulates death and respawn, but does
not provide Pudge's explicit player countdown. Base the countdown on current
death state, including the death-animation interval, rather than a duplicated
eight-second label.

At match end, present victory/defeat/draw with personal contribution and
“Play again.” A time limit must not invent a fort victory. GotA already has a
stats overlay; reuse it. Its transport is initialized with repeating enabled,
and the transport seeks to the beginning at the end. Set a deliberate end state
for human play rather than falling directly into replay behavior. Keep replay
inspection accessible, with controls gated and transient inputs cleared while
viewing history.

Sources: `graphics.nim:drawWorldUnitBars`, `advanceRenderedSimulation`, transport
initialization; `sim.nim:updateHero`; [transport](../src/polyworld/player.nim),
`shouldTick`. Pudge equivalents: `graphics.nim:emitCombatFeedback`,
`ui.nim:drawEndScreen`, respawn presentation, `audio.nim`.

**8. Make the four teammates usable.** Add team pings for attack, defend,
retreat, and assist, followed by a small visible acknowledgment when a bot
accepts. Start with one responder for an assist call, expiration, and survival
taking priority. Pudge implements a three-second ping and one available bot
responder, and its baseline avoids disrupting intentional human movement during
rescues. In GotA, use that principle for lane assignments, tower pushes, and
support behavior. Visible acknowledgments would be an improvement beyond the
current Pudge behavior, which logs them diagnostically.

Seat takeover/autopilot and friend lobbies are useful later. GotA currently
skips loading a VM for the human seat, so a takeover toggle needs a fallback
policy and recorded controller transitions. Hosted sessions additionally need
seat ownership and reconnect handling. These are larger changes than improving
the local control loop.

Pudge sources: `teammates.nim:teamPingResponder`, `needsRescue`;
`players/base.bas` teamwork block; `human.nim:handleSeatSwap`; `hosting.nim`,
`netclient.nim`, `HOSTED_PLAY_SESSION.md`.

The first implementation should combine items 1–4 with the respawn countdown:
a player can keep their hero in view, inspect safely, understand an ability,
aim or cancel it, and receive an explanation if it fails. Keep existing map,
balance, and spell geometry while evaluating that change. Follow with the
guided match, compact shop, and match-end flow, then team coordination and
hosted play. Networking, new abilities, and a map redesign are unnecessary
dependencies for the first pass.

Implementation can stay centered on `controls.nim`, `graphics.nim`, `ui.nim`,
and `shops.nim`, reusing `AbilitySpec` and spell footprints. Pudge's
`commandcard.nim`, `bottomhud.nim`, and `sounds.nim` are useful reference modules
but are absent from this GotA checkout. Port only the needed interfaces;
the complete Pudge controller also contains networking, cheats, and game-specific
placement behavior. New stop/controller/ping simulation actions need replay
support. Presentation-only feedback and previews should remain outside the
authoritative simulation.

Evaluate the first pass with concrete tasks: a new player can move and cast
without opening documentation; an invalid cast explains itself; inspecting an
enemy does not attack it; manual panning can be undone with one key; a dead
player knows when and where they return. Check the same interactions at
1440×900 and 1920×1080 using a mouse and a trackpad. Track time to first
successful move/cast/purchase, accidental orders, and unexplained failed inputs
before and after; these are proposed measurements, not measured improvements.
For implementation validation, exercise each input route through the same
command handler, verify replay hashes for human actions, and check that aiming,
errors, pings, and sounds do not expose hidden enemy information.

Build note: the default GotA native build encountered an older sibling Silky
without `drawRoundedImage`. The screenshot build succeeded using the existing
`tmp/gota-ir/viewer-deps/silky/src` checkout through `SILKY_PATH`. No dependency
files were modified. Both screenshot executables are temporary artifacts.
