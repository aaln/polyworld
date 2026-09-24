# Release62 lane and neutral-camp experiment

Engine: `2c8db6ebe1dc785ce1eea87496505d1244ee4c44` in the isolated sibling
`polyworld-gota-neutral62-20260923`; game2026.9.23.4, replay62/format6/outer2.
Research files live on the fork's `gota/lane-recovery-20260923` branch. Do not
use that branch's older engine files to decode these captures.

`camp_binding.py` extends the reviewed lane-occupancy semantic binding. `build.py`
creates the original seven-layer IR, Python dictionary, generated BASIC and
compile/extract converter. It refuses to overwrite captured inputs. The local
pull-cancellation prototype is preserved under `prototype-pull-cancel/` in the
raw study directory; r62b is the tested source.

Raw root: `polyworld/tmp/gota-lane-neutral62-20260923` (sibling of this research
worktree). The portable reviewed pair contains sanitized evidence and hashes;
the raw root retains captures and receipts. Do not publish signed upload URLs.

Build `episode.nim`, `practice.nim`, `telemetry.nim` and `source_probe.nim` after
copying them into the exact engine's `examples/gods_of_the_arena/tools/`, using
valid underscore-only module filenames. Compile from that engine root with
Nim2.2.10, `-d:headless -d:release -d:replayEvents`, and the verified dependency
root recorded in `runtime-provenance.json`. Binary names are `episode`,
`practice`, `telemetry`, `source-probe`. Preserve checksums in the raw study.
The upstream `tests/test_gota_camps.nim` suite validates the new mechanics.

`native.py` runs12complete games: one fixed seed, two colors and two seats,
for the parent, lane-only and combined candidate. Nine reference VMs respond.
This is a runtime/mechanism screen, not a league performance estimate.

`hosted.py --prepare` validates the live manifest/schema, freezes the exact
roster and score-only method, and uploads inert versions. `hosted.py` uses
shared request journals, limits and idempotency receipts; it streams complete
audits. Requests contain10ordinary baseline games or40responsive counterfactual
pairs. The two treatments share all40baseline seeds. No league membership writes.

The original cohort failed all10first-batch games because Jordan411 did not
compile. Its immutable preparation is in `invalid-jordan411/`, and the original
receipt path remains in `hosted/` for budget reconciliation. Replacement controls
use `hosted-f5/` and a new baseline version; the prospective amendment replaces
Jordan with BeWellBot. Failed games remain budgeted and are not score results.

`dashboard.py` serves read-only live progress at `http://localhost:8796`.
`statistics_report.py` can run while harvesting to decode complete replays; once
all pairs exist it audits120games and computes stratified paired score intervals,
XP-source attribution, time budgets and recipient counts. Two baseline contrasts
use97.5%intervals; the camp-versus-lane contrast is exploratory. Primary outcome
is individual score, with no separate win/death/nonzero gates.

`probe.py` reconstructs all40combined-policy command streams through their full
episodes, checking every world hash and recording neutral selections/pull state.
Other recorded actions are used only for retrospective fidelity, not as responsive
counterfactual opponents. `readback.py` saves league/version drift without writes.
After audits, `finalize.py` annotates the IR without changing tested BASIC and
saves the portable pair/report. Never relabel a discovery cohort as confirmation.

Resume the existing experiment, receipts and budget ledger. Do not rerun
preparation against changed versions or generate new IDs to bypass a failed
request. The original and replacement rosters are separate evidence scopes.
