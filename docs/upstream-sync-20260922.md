# September 22 upstream synchronization

The fork's main branch merges upstream `Metta-AI/polyworld` main at
**5563868e066f82ba5180c03cd89ec8da5388e652**. This includes the September 21
mechanics update, symmetry fixes, hero balance changes, and 500 XP per teammate
when the enemy god is destroyed. The last upstream commit records deployment;
its runtime is identical to **1b70894436b7ffdcd0d421b6b32c2415c9c8bfde**.

The user explicitly chose upstream gameplay unchanged and preservation of the
custom human controls in an archive branch. The entire pre-sync fork main,
**38ea61ceb477b665a05ff29ed3e1a81e9a9aec0a**, remains at
[`archive/gota-human-controls-20260922`](https://github.com/aaln/polyworld/tree/archive/gota-human-controls-20260922).
That snapshot includes custom controls, spell previews, audio, stop/ping replay
actions, the desktop launcher, tests, and their original documentation. Old
human-play documentation elsewhere in this fork describes that archive.

Eight merge conflicts arose in bots, controls, the game documentation, graphics,
replays, simulation, UI, and movement tests. Upstream files and current build
configuration are retained byte for byte, including explicit ability leveling,
portal/draft/buyback actions, replay version 58, and simultaneous mirrored
simulation. Custom-control-only modules and tests are removed from active main
and preserved in the archive. The merged gitignore keeps research exclusions.
All 2,868 fork-only research files present on pre-sync main retain their Git
blob identities; captured inputs and historical results are not rewritten.

The latest policy work remains on
[`gota/score-20260922`](https://github.com/aaln/polyworld/tree/gota/score-20260922),
including commit **0aa5a218f0e8694036de754c7bbf8db9367f89ed** and the completed
160-game study. Its pinned-engine evidence does not change when main syncs.
No research branch or league champion is changed by this synchronization.

## Validation

- Full upstream suite: `nim r tests/tests.nim` passed, using Nim 2.2.10 and
  dependencies from the current lockfile. Private character-asset checks are
  skipped by the upstream suite unless `-d:gotaAssets` is supplied.
- Headless GotA build: `nim c -d:headless examples/gods_of_the_arena/gota.nim`
  passed in the resolved merge checkout.
- Focused integer-score, god-reward, and simultaneous-movement tests passed
  against the exact upstream runtime before conflict resolution.
- All 536 upstream tracked files other than `.gitignore` match upstream blobs.
  All 2,868 fork-only research files match the previous main blobs.
- Merge conflicts are resolved and the diff passes whitespace checks.

The full suite uses the normal compile mode: its CLI tests intentionally
exercise graphical `--player` arguments. An initial invocation with
`-d:headless` stopped at that CLI guard; the corrected standard invocation
completed successfully. No gameplay code was changed to accommodate tests.

Local logs and preservation proof are under
`polyworld/tmp/upstream-sync-20260922`; policy worktrees and game-budget records
are unchanged. The user's local upstream-tracking `main` also fast-forwards to
5563868, preserving its untracked research inputs.
