# Current Gods of the Arena policy work

Read `games/gods_of_the_arena/current.json` first. It routes current work to
engine **2026.9.21.5 / f776d5e** and the tested **current20260922** IR/compiler
pair (unchanged microplay executable, updated current evidence). Verify the live
league's coworld and source before new hosted work.
This guide supersedes historical runtime and advancement instructions for new
experiments on this release. User instruction: old IR that no longer applies
must not constrain progress on the updated game.

## Current contract

- BASIC supports decimals and fractional action coordinates. Snapshot tile
  coordinates and IDs remain integers. Use the current decimal-aware compiler.
- Draft all heroes explicitly within the ten-second pick deadline. Public
  draft choices are available; an old fixed-character roster assumption is not.
- Spend skill points explicitly. Passive automatic leveling does not unlock
  abilities. Check legal ranks, cooldowns, charges and mana.
- Shopping requires the friendly keep; spawn recovery is fast. Inventory has
  six slots, consumables stack, and the host has no sell or equipment-upgrade
  operation. Plan purchases and reserves through actual supported actions.
- Portals have a three-second channel and 60-second cooldown. Buyback is
  supported and respawn is capped. Preserve channel and legal-action guards.
- Waves contain three melee creeps and a caster per barracks; towers have the
  updated health/damage. Use current engine values, not old tactical constants.
- Creep XP requires same-floor proximity within six tiles. The 15% last-hitter
  reserve is conditional on eligibility; the remaining 85% is shared nearby.
  Crossbowman range exceeds the XP radius.
- Same-decision walk+attack does not reset the new swing. A full physics tick
  of movement before reacquisition does, as current practice demonstrates.

## IR and evidence boundaries

Use the seven-layer representation as an editing medium, with the current
binding and host contract. Old strategy content, inferred v135 controller
ordering, historical opponent IDs, integer-only tooling, and old parameter
constraints are optional historical hypotheses. They are not defaults or
mandatory constraints. Reintroduce one only with a current executable mechanism
and current evidence. The current builder must start from the current pair,
not the old formal accepted snapshot.

Preserve historical files and frozen results. Do not migrate an old supported
claim merely by changing its game-version label. Current executable changes
invalidate prior behavioral claims until tested. Never feed hidden replay
truth or policy identity into the action policy.

## New experiment decisions

The primary league metric is mean per-hero
`max(0, lifetime XP - 200 * world ticks / 1440)`, including draft time.
Fort wins/losses/draws remain useful diagnostics. Old 60%-win acceptance,
30/40 or 38/40 fort thresholds, historical rival panels and binary-score
assumptions do **not** gate a newly preregistered current-score experiment.
The completed microplay panel retains its originally frozen gates; this update
does not relabel its results.

Freeze exact candidate/control bytes, engine/configuration, current target
UUIDs, sides and score rules before collecting their results. Compare native
variants against same-color parent controls: candidate red versus parent blue
alone can confuse policy effect with draft/color advantage. For the next
attention experiment, research advancement requires zero invalid games/audit
failures, at least 10% aggregate own-score gain, and no per-cell decrease beyond
5% versus its matched current parent. Beating each target in XP score is a
separate claim requiring own mean above that rival in every target/color cell.
Mixed-team strength and rank need their own evidence. No automatic deployment
follows from changing the research metric.

Runtime validity, exact replay/XP/score checks, correlated-trajectory reporting,
single-writer ownership and shared budgets continue to apply. Those safeguards
are independent of obsolete tactical IR. The current `targets20260922` tools
already run through the shared journal without the legacy win-only acceptance
path. The old controller's formal accepted state remains historical; port its
score gate before using it to judge current-release progress.

For ongoing operations, read the latest campaign `FOCUS.md`/ownership record.
The previous researcher may be paused while an interactive experiment owns
the writer. Do not duplicate its requests or change its in-progress files.

The current pair adds the user episode audit, real-host ranged-draft checks,
rejected refinements and 320 clean mixed-team A/B/guardrail games. Both current
score gates pass; no historical win gate was relabeled. The faster attention
variant was rejected for a red score regression, so the source remains b82c3799.
Fresh Jordan356 is untested; frozen mixed results used317. Read the separate
deployment receipts for which registrations are live, rather than inferring
league selection from an evidence bundle.

Verified live at 08:38 UTC September22: Aaron `aaron-gota-micro0922:v1`
(`f3f8baab-d02a-4f7f-8fc9-e1f050f967a7`) and Coach
`aaron-gota-micro0922-coach:v1` (`15b325b4-e9f3-487f-bd95-a059f92d20e2`).
Both use b82c3799 and are active competing champions. Full deployment evidence:
`examples/gods_of_the_arena/players/ir/forks/current20260922-deployment`.
Use these as live controls for new experiments; never overwrite a frozen plan.
The direct champion endpoint returned500; documented automatic champion
selection during normal placement succeeded. Do not misread the intentional
retirement of the unselected first attempt as a policy-quality disqualification.
