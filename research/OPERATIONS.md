# Operating the fresh workspace

Start at [START_HERE.md](../START_HERE.md). The frozen 180-game study is complete. Its scripts and IDs reproduce that study; create a new experiment directory, cycle, plan and upload names for new work. Do not rerun `hosted.py prepare/run`, `native.py` or the statistics publisher over captured outputs.

## Offline integrity and conversion

Run from the workspace root:

```sh
/Users/aaln/experiments/softmax/metta/.venv/bin/python research/verify_workspace.py
```

This checks every migrated reference, all three portable policy compilers/extractors, the ordered controller index and unchanged pinned game files. It loads the current API/statistics adapters with network connections and old-workspace reads blocked. It reads shared budget configuration but creates no games. Add `--origins` to compare original references and all four coaching sessions, including media. Add `--out /new/path/report.json` to save a new report without overwriting evidence.

[environment.json](environment.json) records local Python/Nim/dependency locations and exact dependency commits. The code and conversion tooling are in this workspace. Python packages, dependency cache, saved-user credentials and large captured replay/media files remain external. This is a ready local worktree, not a hermetic distributable environment. Recreate dependencies from `coworld/dependencies.lock` on another machine; do not copy credentials into Git.

## Build and replay

```sh
python research/build_tools.py episode
research/.build/episode --replay /absolute/path/to/captured/replay.bin
```

Build output and caches go to ignored `research/.build/`, preserving captured binaries. Override `--nim`, `--deps` (or `POLYWORLD_DEPS`) and `--out` as needed. The helper uses `headless`, `release` and `replayEvents` with the checked-in engine. A replay checks every state hash and consumes every recorded action; it does not rerun opponent VMs. Combine replay validity with captured player-status files when assessing hosted runtime health.

Other build targets are `telemetry`, `own-probe`, `camp-income`, `practice`, or `all`:

| Tool | Invocation after building | Purpose |
|---|---|---|
| telemetry | `research/.build/telemetry --replay /path/replay.bin` | Reward receipts and per-hero mechanisms |
| own-probe | `AUDIT_POLICY=/path/policy.bas AUDIT_SLOT=0 research/.build/own-probe --replay /path/replay.bin` | Reconstruct one exact source's decisions; require matching source identity |
| practice | `AUDIT_POLICY=/path/policy.bas research/.build/practice` | Weak-neutral guard fixtures |
| camp-income | `AUDIT_POLICY=/path/policy.bas research/.build/camp-income` | Fixed local camp encounters across classes/colors |

The last two are artificial behavioral fixtures; their scores are not league estimates. Keep their output in a new experiment folder. Full current native tests must run responsive VMs and independently replay recordings, following the preserved `native.py` study design.

## API access and shared ownership

`research/hosted.py` loads the frozen implementation modules under `research/vendor/`, then supplies the current workspace, engine, shared campaign and study. `research/recovery_statistics.py` does the same for statistics. Vendored modules are import-only; their historical CLI entry points and default globals are not current campaign commands.

Load a wrapper with a unique `importlib.util.spec_from_file_location` name. Do not `import hosted` after the transitive legacy imports have populated generic module names. The wrapper's `h.client()` uses the existing saved-user client; `h.live(client)` reads the live game. Verify its release/configuration before planning any new hosted comparison. A pinned local engine does not establish that the live service is unchanged.

The shared campaign is `../gota-autoresearch`. Read `active-research.json`, `ownership.json`, `PAUSED` and the shared ledgers. Acquire the existing `runner.lock` ownership before becoming a campaign writer; respect `xp-create.lock`, `budget.lock` and the existing counterfactual reservation/recovery workflow. Preserve request hashes and receipts, and recover uncertain submissions before creating replacements. Use the existing `league-deployment.lock` for authorized league writes with exact version IDs and readback. Do not restart the paused legacy worker; its engine/configuration fields are historical.

Limits remain **100,000 games/day**, **400/cycle**, **3 active requests**, and **at most 100 games/variations per request**. Freeze responsive counterfactuals, source/IR digests and a numerical score decision rule before results. The current frozen study's wrapper sets `CYCLE` and `RAW` to completed evidence: reuse implementation through a new wrapper, not those identifiers.

## Captures and historical material

- Current 180-game captures: path recorded as `raw_study` in `environment.json`; published summaries are under `research/results/`.
- Khors v180 captures: `../polyworld/tmp/gota-khors180-observations-20260924`; the portable observation model and artifact index are under `research/opponents/khors-v180/`.
- Four coaching sessions: byte-copied notes, synthesis and text under `research/coaching_inputs/`; media remains at hash-indexed original paths.
- Sixteen historical IR/BASIC pairs and opponent/coaching lessons: `research/library/manifest.json`. These are reference snapshots, not complete alternate campaigns.
- `migrate_context.py` and `build_context_index.py` document migration provenance. They are capture utilities, not routine setup commands. Preserve existing manifests; use a new versioned destination for later captures.

The old research workspace and dirty main workspace remain untouched. The existing three policy sources were not changed by this migration, and no hosted games or league deployments were initiated.
