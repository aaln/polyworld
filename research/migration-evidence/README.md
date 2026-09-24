# Fresh-context migration verification

The new entry point is [START_HERE.md](../../START_HERE.md). This migration adds knowledge and runnable conversion/audit dependencies while preserving all three current policy sources and the pinned game.

[Offline verification](verification.json) passed:

- Three portable policy verifiers and byte-identical compile/extract round trips.
- 350 byte-exact historical references, including 16 IR/BASIC snapshots.
- 25 frozen import dependencies; current wrappers load with old-workspace reads and network connections blocked.
- Four coaching sessions: 64 copied text/JSON files and 214 indexed original inputs, including media.
- 592 original-file hashes checked; 21 controller rules mapped in exact execution order.
- All 68 existing pinned game files unchanged.

[Replay calibration](replay-calibration.json) passed after rebuilding the episode tool with Nim 2.2.10 and the current engine: an existing 4,566-tick capture produced exactly the stored audit output, including every hero row, XP/score and zero state-hash mismatches. All 26 dependency checkout commits match `environment.json`.

Authored documentation links resolve locally. Migrated JSON was checked for populated credential fields; none were found. Frozen copied sources retain original whitespace and embedded historical paths; their hash equality takes precedence over formatting cleanup. Large replay/media captures, dependencies and credentials remain external as documented in [operations](../OPERATIONS.md).

No new hosted games, policy changes, league writes or gameplay changes were made. The 180-game result remains the current evidence: neither challenger qualified, and the deployed source remains the reference. Starting a fresh conversation can reduce stale assumptions; this migration is not evidence of improved gameplay scores.
