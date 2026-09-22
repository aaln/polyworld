# Microplay practice and target comparison

Published engine: **2026.9.21.5**, commit
`f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. Uses the exact runtime and
dependency checkout from `../week20260921`, with a separate private study
at `tmp/gota-targets-20260922`. The prior IR and captured inputs are immutable.

## Conversion and practice

`micro.py` preserves the first attempted timing, five-equipment and potion
variants. `practiced.py` is the corrected versioned binding: a full physics tick
between movement and attack reacquisition, plus XP proximity before navigation
throttles. Both use the repository seven-layer compiler and require exact
Python/JSON/BASIC round trips. Do not hand-edit a tested BASIC file and retain
its old IR identity.

```sh
python3 games/gods_of_the_arena/instruments/targets20260922/practiced.py NEW_NAME --mode potions
```

The finalized `ir/forks/microplay20260922` bundle includes a standalone
`convert.py` and `verify.py`. Its converter rejects unknown BASIC edits and
marks beliefs for review when executable bytes change.

Copy `practice.nim`, `scenarios.nim`, and `events.nim` into the pinned engine's
`examples/gods_of_the_arena/tools/` directory. Build with Nim 2.2.10,
`-d:headless -d:release`, the pinned `POLYWORLD_DEPS`, and for `events.nim` also
`-d:replayEvents`. The first two accept the absolute source path in `WEEK_POLICY`.
The event auditor accepts `--replay /absolute/path/replay.bin` and verifies
every state hash, action consumption and XP-event reconciliation.

The 126 scenario checks cover all classes/colors and runtime stress. Practice
adds actual-tick attack cadence, contested last-hit gold/shared XP, the
Crossbowman XP boundary, equipment allocation, and positive/negative defensive
portal channels. `PRACTICE_TRACE=1` emits bounded diagnostic state to stderr.
These controlled drills are not competitive proxies.

## Hosted evidence

`preflight.py` checks exact target-version VM health in existing games.
`panel.py` freezes all slots and exact target UUIDs, runs 40 games per cell,
streams artifacts, checks all ten VMs and fully resimulates replays.
`confirm.py` admits the corrected source only after completed baseline,
practice and native evidence, uploads an inert version, logs it, and starts the
six-cell target panel. It does not select league memberships.

Both completed research cycles share the existing global XP journal, creation
lock, 400-per-cycle / 1600-per-UTC-day normal limits and paused-writer check.
Do not run a writer while the background researcher owns the campaign; do not
rerun a failed unchanged source with new keys or reset the budget journal.
The archived September 20 allowance has expired.

`review.py` reports fort outcomes, per-hero XP score, growth, draft classes,
and distinct complete command streams. `inspect_events.py` selects one
median-score replay per observed outcome per cell for retrospective diagnosis.
`finalize.py` preserves the evidence and reflects validation back into IR while
asserting the evaluated BASIC remains byte-identical. Generated seeds and
different command streams are not independent statistical samples.

Final results and limitations are in
`../../experiments/2026-09-21-targets-microplay.md` and the saved policy bundle.

## Current-score follow-up

`current.json` and `guide-gota-current-release.md` route new work to the current
contract. `current_attention.py` starts from that pair and invalidates changed
behavior claims. `current_score.py` compares exact current engine/opponent/color
cells using XP score; its tests prevent old win-only acceptance from leaking
into the new path. Preserve completed `panel.py` results and their frozen gates.

`economy_practice.nim` checks scarce-gold purchases; `draft_practice.nim` tests
the user's public opening on the real host. `focus_episode.nim` emits typed
events and bounded post-tick public observations for the supplied episode's
slots4/5. Those observations are not an internal decision/intent trace.

`healthy_field.py` performs roster VM preflight and a160-game fixed mixed-team
first-pick A/B against live compat. `guardrail_field.py` conditionally runs the
unchanged pair from third-pick seats for another160games in the same budget
cycle. `review_healthy_field.py` audits growth, correlation and representative
typed events. `finalize_current.py` preserves a separate current semantic pair
with unchanged validated BASIC; `deploy_current.py` requires both score gates,
exact source/ownership and the existing two-player authorization, saves rollback
receipts, and verifies active competing champions. It has a read-only default.
