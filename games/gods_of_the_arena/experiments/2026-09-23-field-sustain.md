# Field sustain and interruptible health retreats

Status: running; source frozen after local admission.

Session: `/Users/aaln/Documents/Policy Loops/sessions/2026-09-23t02-52-57-098ze03810`.
Read notes, session metadata, synthesis, linked frames and the game implementation.
All51captured files, including video/audio/empty input IR and policy, are copied
unchanged to `polyworld/tmp/gota-field-sustain-20260923/captured-session` with a
SHA256 manifest. The supplied follow-up URL identifies the league, not the episode.
Keep the recording unbound until a matching replay/source is verified. Playback
is scrubbed; Gemini's exact390HP and elapsed-time assertions are not accepted.

## Mechanism and coordinated intervention

Current policy latches retreat until fountain arrival with90%HP/80%mana.
Its explicit self-healing is behind combat, which walking retreat preempts.
Druid HealingBloom/KindredWisps use a fixed area and12tick impact; moving too far
can miss one's own heal. Low health is evidence to reconsider recovery, not a
permanent obligation to reach spawn.

Edit semantic IR and versioned contracts together: current threat/resource
appraisal; strongest learned, ready, charged, affordable self-heal below75%HP;
bounded18tick pending-heal state; one-cell-per-axis cover step toward an allied
homeward creep/tower or homeward shelter; early health-retreat release at75%HP
and20%mana. Clear the persistent base path and movement throttle before normal
combat/advance can run in the same decision. Preserve restock, portal ownership,
keep replenishment, and visible danger overrides. Never wait for a cooldown.
No opponent identity or replay truth is a runtime input. The full bundle is
evaluated together; no claim that each individual edit is separately beneficial.

Parent is validated blue-centerc02f8cb6, now deployed to both players. The
completed400-game blue study stays frozen. Check closed_levers: no unchanged
repeat of old targeting, elixir, mirrored movement or crossbow-only failures.

If useful, accepted healing and prompt route interruption reduce unnecessary
base travel and increase XP-minus-time score. If harmful, mana depletion,
premature re-entry or deaths outweigh saved travel. Mechanism correctness or
more time outside base alone does not qualify score improvement.

## Design and critique

Use actual-engine fixtures first: Druid safe healing and danger/mana/charges/
cooldown/root/restock cases, all-class healed-in-transit interruption, inherited
portals/buyback/broad runtime checks, portable compile/extract, twelve complete
native games. Native outcomes are runtime evidence, not rival-policy strength.
Initial r1 treated its own healing warning as hostile; preserve its failed
fixture and source. r2 excludes own caster warnings while unknown casters remain
unsafe. No hosted data were used to choose this correction.

240fresh games,40/source/context, six requests. Contexts: blue lead ranged
guardrail, red later-draft, blue later-draft. For the latter, subject is public
team ordinal3; two fixed blue-center references occupy allied ordinals0/2,
relh161 ordinal1, JuliaB5 ordinal4. This encourages the unchanged public draft
fallback to Druid after ranged/mage choices, without rewriting either subject's
draft or pretending a forced-class proxy is production. Report actual classes;
require at least10Druid games per source pooled across late contexts for a
coaching-specific competitive verdict. The duplicated fixed teammate source is
explicit; this is a controlled roster, not a random field or universal ranking.

Khors114,Jordan411,Richard174 remain opposing in every context. Whole teams
rotate together. Exact versions/sources/configuration are frozen before spending.
Prior fresh controls are not reused. No mid-run retuning, seed pairing claim,
sample extension or changed threshold after results. Small40-game cells can
leave moderate effects inconclusive; that means retain the parent.

## Prospective acceptance

Require all ten source/VM exits, full replay hashes, XP source reconciliation
and integer scores to pass in all240games. Aggregate equal-context mean score
must improve>=10%, each of the three cells retain>=95%control, and the lower95%
context-stratified independent whole-game bootstrap aggregate gain exceed0.
Pooled later-draft mean must improve; candidate blue-lead mean own-minus-khors114
must remain positive. Require the Druid exposure floor above. Report score,
hero/creep/building/god XP, deaths, duration, class slices and rival gaps.
First4lexical episode UUIDs per cell receive complete healing/field/keep effect
inspection (24games), diagnostic only. Show all duplicates and failures.

Game and principal champions(ours,khors,Richard,Jordan,relh) must remain stable;
background changes are disclosed. A qualified exact source can replace both
authorized champions; otherwise retain blue-center and preserve the complete
coaching pair/results with unsupported score claims marked accordingly.

Budget: normal September23UTC1600,1360already reserved,240remaining. One new
cycle `interactive-field-sustain-20260923`, six40-game requests, maximum3active.
Do not renew the expired September22override or reset the journal. Legacy worker
remains paused. Existing user authorization covers evaluation and validated
deployment to both players; no messages to others.

Raw evidence: `polyworld/tmp/gota-field-sustain-20260923`.

## Local admission

Source3807330d, initial IR7731f1a4, bindingr2. All558checks pass:68sustain,100opening,180buyback,84portal,126broad;12complete native games pass full replay/XP/runtime verification. Max15678instructions/23247work. Portable compile/extract exact. Wrong initial inherited-harness invocation and corrected output are separately preserved; no failed comparison was discarded.
