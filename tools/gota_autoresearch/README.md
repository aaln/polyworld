# GotA continuous autoresearch

For the portable Devin handoff, start with
[the operational guide](../../docs/guides/devin-gota-autoresearch.md) and
[ready-to-paste mission](../../docs/guides/devin-gota-prompt.md).
The Mac campaign notes below preserve historical setup and acceptance rules;
the current deployment authority and champion identities must be refreshed.

## Current league objective (September20,2026)

The user now requests an IR policy that beats Richard and Jordan and attains and
retains #1. Aaron and Coach are the requested active players; a-aron is retired.
Read FOCUS.md and LEAGUE_STATUS.json for live identities, evidence and priorities.
The user authorized evidence-supported upgrades of this pair. Target-specific
promotion still requires fresh Richard/Jordan confirmation, field preservation,
all replay/runtime/IR checks and a recorded decision. Formal broad research
acceptance retains the original gates below; neither is implied by a high rank.

A second **read-only** LaunchAgent, `com.aaron.gota-league-watch`, now checks the
leaderboard, active champions, opponent versions and latest12rounds every10,800
seconds. It writes `LEAGUE_STATUS.md`, `LEAGUE_STATUS.json`, and timestamped raw
receipts under `league-watch/`. The single existing autoresearch worker reads
these at startup and before each experiment. No competing research daemon was
created. The monitor does not buy XP or alter memberships. Both services require
this Mac to be awake, logged in and online; missed sleeping-time checks are not
claimed as completed checks. Retrying after access failure keeps prior timestamps
visible rather than claiming a fresh success.

Monitor source: `polyworld/tools/gota_autoresearch/league_watch.py`.
Schedule: `~/Library/LaunchAgents/com.aaron.gota-league-watch.plist`.
Latest restoration proof: `polyworld/tmp/gota-ir/restore-coach-20260920/verified.json`.
Live-branch Richard research: `polyworld/tmp/gota-ir/richard-counter-20260920`.

The worker repeatedly builds semantic IR policies from the last accepted policy.
New hypotheses start as forks. Only the acceptance command advances the incumbent;
it saves a read-only IR/BASIC/compiler/evidence snapshot and creates the next fork.
Generation zero is the existing deployed `relh154-legacy` policy, not a newly proven
self-play improvement. The original dirty game checkout is preserved.

The macOS user LaunchAgent runs continuously while this Mac is awake and the user
is logged in. It starts on login, restarts failures, and retries every 10,800 seconds
if stopped. A filesystem lock prevents overlapping research workers. Agent cycles
have a 160-minute ceiling, checkpoints, separate JSONL logs, and failure backoff.
Sleeping/offline time cannot run games or agents; work resumes after availability.

Campaign directory: `/Users/aaln/experiments/softmax/gota-autoresearch`.

## Acceptance

- Hosted fort wins against the immediate parent: at least **60% on red and 60% on
  blue**, at least 40 games per side; draws score zero.
- Fresh parent/candidate comparisons against at least five field rivals and two
  historical own policies, both colors: no observed win-rate regression per rival
  and side. Add current league threats prospectively.
- At least **200 mixed ten-player games per policy**, at least five paired rosters,
  80 per side and two subject classes per side. Actual player IDs must be distinct.
- Local gameplay/mechanism qualification first, then a frozen held-out matrix;
  all replay, runtime, roster, game version, equipment and IR/compiler checks pass.

These are empirical acceptance thresholds. Repeated deterministic trajectories are
correlated; no confidence or guaranteed universal superiority is implied. Local
mechanism tests cannot replace hosted generalization. The service advances the
research incumbent. Latest user-authorized live upgrades follow the separate
FOCUS.md target/field gate and verified Aaron/Coach membership workflow.

Budgets: 400 new hosted episodes per agent cycle, 1,600 per UTC day, at most three
concurrent requests. A request contains 40–200 games. Studies can span cycles/days;
requests are journaled and retried with the same idempotency key. The worker keeps
doing useful local/replay analysis when hosted allowance is exhausted. Settings
are in `config.json`; the research agent must not relax them to pass an experiment.

## Inspect, pause, resume

```sh
PY=/Users/aaln/experiments/softmax/metta/.venv/bin/python
CTL=/Users/aaln/experiments/softmax/polyworld/tools/gota_autoresearch/researcher.py
"$PY" "$CTL" status
"$PY" "$CTL" pause
"$PY" "$CTL" resume
```

`pause` stops the current agent within ten seconds (plus up to thirty seconds for
graceful shutdown). Already submitted remote XP continues and remains harvestable.
`state.json` names the accepted snapshot and current fork; `progress.json` and
`CHECKPOINT.md` explain current work; `cycles/*/events.jsonl` and `last-message.md`
record each agent run. `xp-ledger.json` records spending and request locations.

To remove the schedule while preserving all work:

```sh
launchctl bootout "gui/$(id -u)" ~/Library/LaunchAgents/com.aaron.gota-autoresearch.plist
```

## Candidate and holdout workflow

`fork 'hypothesis'` copies the current accepted IR into a new editable bundle and
records its parent. Edit that IR, use versioned binding contracts, regenerate BASIC,
test locally, upload inertly, and create a JSON prospective plan with these keys:

```json
{
  "parent_snapshot": "0000-<source-hash>",
  "fork": "/absolute/path/to/fork",
  "candidate_dir": "/absolute/path/to/tested/bundle",
  "upload_receipt": "/absolute/path/to/uploaded-version.json",
  "upload_metadata": "/absolute/path/to/upload-request.json",
  "local_evidence": ["/absolute/path/to/local/qualification.json"],
  "mechanism_report": "/absolute/path/to/mechanism.md",
  "discovery_episodes": [],
  "arms": [
    {
      "key": "self/candidate/red",
      "kind": "self",
      "role": "candidate",
      "comparison": "immediate-parent",
      "color": "red",
      "directory": "/absolute/path/to/new/holdout/arm",
      "own_slots": [0, 1, 2, 3, 4],
      "roster": ["candidateUUID", "candidateUUID", "candidateUUID", "candidateUUID", "candidateUUID", "parentUUID", "parentUUID", "parentUUID", "parentUUID", "parentUUID"]
    }
  ]
}
```

The example shows one arm only; `freeze` requires the complete matrix. Kinds are
`self`, `archive`, `field`, and `mixed`. Role is `candidate` or `parent`. Field and
archive comparisons each need both roles on both colors. Mixed comparisons need
two arms with the same single subject slot, teammates, and opponents; substitute
only the tested version. Choose enough mixed rosters to satisfy color/class gates.
Every arm directory must be new with no previously started request or artifacts.

Run `freeze draft.json`, then create each actual request through
`xp-create request.json arm/batch`. The exact UUID roster, target and game config
must match the frozen matrix. This journals allowance before the POST. Existing
harvesters can resume the stored `created.json`; never use a helper that creates
extra requests outside this ledger. For each arm save complete episodes under
`arm/artifacts/<episode-id>/` with `episode.json`, `results.json`, `replay.bin`,
VM validity evidence, and `.done`. Audit with the campaign's pinned auditor.

When complete, `accept fork/holdout-plan.json` independently re-audits every game,
writes the gate result, adds measured feedback into IR without altering tested
BASIC, snapshots, and forks. Failing results stay in the experiment record.
Never manually change `state.json` to promote an unqualified policy.
