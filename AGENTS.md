# Agent entry points

For GotA policy research, monitoring, coaching or league upgrades, first read
[the current-release guide](docs/guides/guide-gota-current-release.md) and
`games/gods_of_the_arena/current.json`. They define the active engine, IR and
XP-score metric. Then read [the autoresearch history and operational
guide](docs/guides/devin-gota-autoresearch.md) for ownership, budgets and evidence.
Its historical win-only gates and old IR do not constrain new experiments on
the current release. Preserve frozen prior experiments and their original rules.

Use `aaln/polyworld` as the research fork. Preserve existing work and failed
experiments. Verify main against the published manifest; the research branch
can retain older engine files. Build the current JSON's exact engine commit in
an isolated worktree for comparative tests, even when main presently matches it.
Do not launch the archived Mac/Codex supervisor inside a Devin research session.
