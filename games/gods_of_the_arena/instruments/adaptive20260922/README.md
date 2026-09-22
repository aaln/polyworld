# Adaptive individual-score research

Use the current-release guide and `current.json` first. This instrument pins
2026.9.22.3 / 1b708944 / replay58; it does not trust the engine files in the
research checkout. The dedicated engine worktree and inherited binary hashes
are recorded in `runtime-provenance.json`. Policy inputs remain public.

- `adaptive_binding.py` extends the frozen deployed portal binding. `build.py`
  emits two new portable IR/BASIC pairs and checks reverse extraction.
- `practice.nim` uses actual game ticks for44 spell cases across both colors,
  including real damaging hits, rejected-cast fallback, allies, recovery,
  portal ownership and mana restoration. Existing84 portal and126 broader
  fixtures run separately. `native.py` checks12 full ten-VM native matches;
  their scores are diagnostics, not evidence against hosted rivals.
- `adaptive_hosted.py --prepare` freezes the240game screen and inert uploads.
  Running without `--prepare` resumes exact receipts under the shared runner
  lock and journal. Never reset reservations. Maximum3active requests;
 40games/cell. `report.py --watch` decodes and verifies every game.
- Only a qualifying screen selects a source. Then prepare
  `adaptive_hosted.py --stage confirmation --candidate NAME --prepare`, run
  with `--stage confirmation`, and run `report.py --stage confirmation --watch`.
  This160game fresh control/candidate comparison changes teammates and subject
  draft position. It uses the exact selected source, not a new combined policy.
- `effects.py --watch` (optionally `--stage confirmation`) decodes four lexical
  episodes per cell for actual damage and field-time diagnostics. Selection is
  fixed before effect inspection and is separate from the full score gate.
- `field.py --out NEW_DIRECTORY --before PRIOR/snapshot.json` reads current
  game, champions and standings and reports changed versions. Each output is
  immutable. An existing snapshot is reused explicitly on preparation resume;
  use a new directory for a new capture. The archived worker stays paused.
- `diagnosis.py` publishes the80-game previous-control retrospective evidence
  and non-executable Richard167/khors114 semantic models. A model is not exact
  source; neither has validated forecasts or proxy qualification.
- `publish.py` saves reviewed IR/source pairs, results, complete request lists,
  artifact hashes and original-input references. Competitive failures remain
  visible. `verify.py` in each saved pair checks its complete manifest and
  exact compile/extract round-trip. Recompiled edits invalidate prior claims.
- `dashboard.py` serves read-only screen progress on localhost8853. It holds
  no credentials and does not create requests or change policies.

All Python API helpers share the established credential client and journal.
The `/stats/policy-versions` metadata endpoint is owner-scoped; do not interpret
its404 for a rival as retirement or attempt privileged bypass. Exact public
membership IDs, episode specs/content hashes and dry-run roster resolution
identify competitors. Raw artifacts live outside tracked source under
`polyworld/tmp/gota-adaptive-score-20260922`; preserve them.

The prospective score gate is>=10%aggregate mean gain with>=95%eachcolor and
zero invalid/audit failures. Report uncertainty, duplicate streams, realized
classes, within-game rival score gaps and XP/time decomposition. No fort-win
requirement. A selected source is not a universal ranking guarantee, and new
opponent versions invalidate any claim of having tested those newer versions.
The user authorized10000hosted games for September22 UTC; ordinary1600later.
Cycle400/parallel3limits and single-writer rules remain.
