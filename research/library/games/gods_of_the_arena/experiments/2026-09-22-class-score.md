# Preserve fallback heroes while improving Crossbowman points

Status: completed and rejected after 160 fresh hosted games. Both deployed
portal champions remain unchanged. No conditional confirmation was launched.

| Source | Red mean score | Blue mean score | Overall |
| --- | ---: | ---: | ---: |
| Fresh deployed control | 2857.025 | 2695.400 | 2776.2125 |
| Crossbow-only | 1944.475 | 3255.625 | 2600.0500 |

Aggregate change **−6.35%**, red **−31.94%**, blue **+20.78%**; the 95%
whole-game bootstrap gain interval is **[−23.50%, +14.66%]**. All 160 games
passed source, all-VM, full-replay, XP and integer-score audits; each cell has
40 distinct command streams. The game and champion versions stayed unchanged.
The frozen aggregate/each-color conditions failed. The favorable blue slice
does not qualify a color-dependent replacement. Sixteen additional typed-effect
replay audits are diagnostic and do not change this decision.

Local admission passed 160 actual-tick conformance scenes, 84 portal and 126
broader checks, 20 complete native games and eight exact native trajectory
comparisons. These correctly established branch behavior; they did not predict
competitive improvement. Initial IR/source and all raw captures are preserved.

The preceding adaptive-score study completed400games. Its broad spell-pressure
controller gained13.92% in a first-pick screen but lost4.20% on an independent
later-draft roster, including a13.35%red regression. It is rejected. The new
hypothesis is deliberately class-conditional, motivated by Crossbowman's
higher mean scores and the broad source's lack of reliable Ranger/fallback
improvement. Those inspected slices do not validate the new complete policy.

Source **513f8a2c**, semantic IR **2e767191**, binding
`gota-bassy/class-score-2026-09-22-r1` branches on public `selfClass`:

- Crossbowman retains the screened independent public hero spell attempt with
  real-host fallback, plus hero attack priority480.
- Every other class retains the deployed portal controller's combat template
  and hero priority80. The extra observation cache changes no old variables.
  Draft, lifecycle, items, structure targeting, timing, movement, safety and
  portals remain unchanged for all classes.

Actual-tick conformance compares **all commands and every world-state hash**
for160scenes: eight conditions, ten classes, both colors,96ticks each. The
candidate must match broad spell-pressure for Crossbowman and the deployed
source for all nine others. It also needs84portal/126broader host checks,
portable compile/extract, full native replay/XP audits, and native trajectory
comparisons. These validate branches/runtime, not rival-policy superiority.

Prospective hosted design, fixed before new spending:

1. **160fresh games:** control/candidate,40percolor, first team seat. Exact
   Richard167,khors114 and Jordan411 oppose both; relh161 is a teammate. No
   reused control results from the inspected400-game study.
2. Only after a complete passing screen, **160independent games** swap relh161
   and Nancy's team assignments. Keep the first team seat so the edited class
   remains available. This is a changed-roster confirmation, not the broad
   study's later-draft test. Branch preservation has its own conformance and
   native checks; do not imply improvement for unchanged fallback classes.
3. Each stage requires zero invalid/source/VM/replay/XP/integer audit failures,
   at least10%aggregate mean improvement and95%eachcolor. Report whole-game
   bootstrap intervals, draft-class mixture, duplicate streams and paired
   khors/Richard score gaps. Do not revise thresholds after outcomes arrive.
4. Deploy only exact bytes passing both stages while the tested field remains
   current. Otherwise retain both original portal champions. A fixed-roster
   gain is not a universal ranking guarantee.

Maximum320new hosted games in a separate shared-journal cycle. Existing dated
Sep22UTC allowance10000 is authorized; normal1600later, cycle400 and parallel3
remain. Preserve all preceding captures, failed sources and pending receipts.
Raw root: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-class-score-20260922`.
The `class_hosted.py` wrapper uses a distinct idempotency prefix and cycle;
old baselines cannot silently satisfy fresh requests. `class_report.py` and
`class_effects.py` reuse the current exact-engine audit logic with new outputs.
