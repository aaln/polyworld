# Agent entry points

For GotA policy research, monitoring, coaching or league upgrades, first read
[the Devin autoresearch guide](docs/guides/devin-gota-autoresearch.md).
It identifies the portable runtime, current handoff, semantic IR conventions,
research evidence, single-writer transfer and promotion gates.

Use `aaln/polyworld` as the research fork. Preserve existing work and failed
experiments. Main includes gameplay changes that differ from the published
league engine; use the pinned research worktree for comparative policy tests.
Do not launch the archived Mac/Codex supervisor inside a Devin research session.

After the September 22 upstream sync, main uses the upstream gameplay and replay
format unchanged. Custom human controls remain on
`archive/gota-human-controls-20260922`; do not reintroduce them into the current
engine through old coaching or IR rules. The latest individual-score policy
research is on `gota/score-20260922`; read that branch's
`docs/guides/guide-gota-current-release.md` and
`games/gods_of_the_arena/current.json` before new policy work. The September 20
handoff in this branch is historical. See `docs/upstream-sync-20260922.md`.
