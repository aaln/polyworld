# Reproducing this episode account

Start with [the coach handoff](coach-and-autoresearcher.md) or [the full episode IR](episode.ir.md).
The report generator is specific to this episode and rejects other request IDs; its prose is not a generic narrator.
The native probe can capture other exact-source policies, but those require their own provenance and interpretation.

The frozen BASIC is the deployed source. `policy.instrumented.bas` adds only `print "IR:..."` markers at rule evaluation,
entry and exit. Removing those marker lines recovers `policy.bas` byte for byte. No globals were added.
The probe captures marker events and command offsets, then verifies all five owned heroes' commands against the tape
and checks the complete post-tick state hash sequence. It reproduces opponents using their recorded actions solely for
reconstruction, so this executable must not be used to claim counterfactual decision quality.

The original and instrumented runs also produced identical decision-time observations, 227 globals before and after
every primary-hero decision, commands, and projected ground-truth frames. Those comparisons and the exact source hashes
are preserved in [instrumentation-equivalence.json](instrumentation-equivalence.json),
[policy-parity.json](policy-parity.json), and [provenance.json](provenance.json).

From `/Users/aaln/experiments/softmax/polyworld`, regenerate the Markdown and JSON from the saved native trace:

```sh
python3 tools/episode_semantic_ir.py \
  --evidence tmp/gota-ir/semantic-episode-20260918 \
  --episode-artifacts /Users/aaln/experiments/softmax/gota-research-20260916/coached-lanes/r5-coach-split-0918/user-episode/ereq_0806a449-3d7c-4160-868a-3e157634ebbc \
  --output docs/episodes/ereq_0806a449-3d7c-4160-868a-3e157634ebbc

../metta/.venv/bin/python tools/plot_episode_semantic_ir.py \
  docs/episodes/ereq_0806a449-3d7c-4160-868a-3e157634ebbc
```

To rerun native reconstruction, use the clean source checkout at
`/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r5`, commit
`f2ab9598d8f8001b6beae3e66404e341770c803f`. The installed probe is
`examples/gods_of_the_arena/players/ir/replay_semantic_episode_probe.nim`; its frozen copy is in this directory.
Do not compile against the original workspace's modified game files.

```sh
POLYWORLD_DEPS=/Users/aaln/experiments/softmax/gota-research-20260916/deps \
nim c -d:headless --hints:off \
  -o:tmp/gota-ir/semantic-episode-20260918/replay-semantic-recheck \
  /Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir/replay_semantic_episode_probe.nim

PROBE_SLOTS=0,1,2,3,4 \
PROBE_SUBJECT=0 \
PROBE_GLOBAL_NAMES=/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/semantic-episode-20260918/global-names.txt \
PROBE_POLICY=/Users/aaln/experiments/softmax/polyworld/docs/episodes/ereq_0806a449-3d7c-4160-868a-3e157634ebbc/policy.instrumented.bas \
tmp/gota-ir/semantic-episode-20260918/replay-semantic-recheck \
  --replay /Users/aaln/experiments/softmax/gota-research-20260916/coached-lanes/r5-coach-split-0918/user-episode/ereq_0806a449-3d7c-4160-868a-3e157634ebbc/replay.bin \
  > tmp/gota-ir/semantic-episode-20260918/reconstructed-recheck.jsonl
```

Expected native summary: 13,557 ticks, 67,929 owned commands matched, 61,089 owned decisions across five heroes,
all state hashes equal, all actions consumed. The detailed primary perspective has 12,261 invocations and
85,827 rule evaluations. Full per-tick game state is reconstructable from the replay; the JSONL ground-truth
projection alone is not a branch checkpoint and omits state such as opponents' private VM memory.

`validation.json` records coverage, reference integrity and fault-injection checks. No live-opponent rollouts,
hosted evaluations, policy edits or evidence attachments are part of this conversion.
