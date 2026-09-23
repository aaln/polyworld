# Relh169 source and draft audit

This is read-only research instrumentation. It creates no XP requests, uploads or
league memberships and does not edit an executable policy.

Run with the repository's Python environment from the research checkout:

```sh
python3 games/gods_of_the_arena/instruments/relh16920260923/build.py
python3 games/gods_of_the_arena/instruments/relh16920260923/audit.py
python3 games/gods_of_the_arena/instruments/relh16920260923/publish.py
python3 games/gods_of_the_arena/instruments/relh16920260923/seal.py
python3 docs/opponents/relh-v169/source-audit-20260923/verify.py --inputs
```

`build.py` verifies the isolated replay59 engine and locked dependency revisions,
then builds two native probes. Paths are the recorded local research layout;
adapt paths explicitly on another machine while preserving original provenance.
It requires the existing Nim2.2.10 toolchain and replay59 dependency checkout.

`source_probe.nim` executes authentic relh source from draft through termination,
compares every submitted command and every full-world hash, and records private
controller activation for retrospective interpretation. Other players use the
captured command tape. It never continues after a changed command and is not a
counterfactual evaluator. This extends the already used Richard source probe.

`drafts.nim` replays only the draft prefix, checking hashes and collecting public
availability/composition immediately before each draft command. `audit.py`
reconstructs the exported Q16.16 head and the own baseline heuristic, checks all
400 actual subject picks, then evaluates the relh head on our200states. Only the
choice is hypothetical; it does not assign a hypothetical game score.

The frozen `tmp/gota-relh169-audit-20260923/plan.json` selects all200baseline
controls from unit-farming59 and the first2lexical UUIDs per context for8full
source reconstructions. Resource and economy audits from those same immutable
games are reused with content hashes and XP/score checks. No cherry-picked
high-score episode and no fresh-control claim.

`audit.py` caches probe JSON. To re-execute native reconstructions, preserve the
old `episodes/` directory under a new name before rerunning; never overwrite the
frozen inputs. `publish.py` packages exact source, documentation captures,
semantic IR and proposed transfers. `seal.py` hashes the portable artifacts.
`verify.py --inputs` also hashes original replay/spec/resource files; its default
mode validates the portable report without requiring local replay files.

Full outcome data are descriptive. A policy transfer must use a separately
frozen IR conversion and controlled current-engine experiment, with existing
failed Richard174 transfers retained.
