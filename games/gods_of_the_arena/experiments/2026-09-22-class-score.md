# Preserve fallback heroes while improving Crossbowman points

Status: local validation of a new full-policy candidate; no hosted games yet.

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
