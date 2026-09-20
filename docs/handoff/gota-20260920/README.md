# September 20 research handoff archive

Start with [the operational guide](../../guides/devin-gota-autoresearch.md).

This is a point-in-time export, not a live campaign directory. `progress.json`
and `LEAGUE_STATUS.json` carry their original timestamps. The source worker
continued running during export; obtain its latest checkpoint and ledger during
ownership transfer. `config.json` records historical paths/dated budget authority;
`remote.py init` generates a separate portable observer configuration.

- `accepted-0000-b2693715459d/`: immutable formal ancestor and compiler/evidence.
- `active-fork/`: selected primary policy sources, frozen plans and result summaries
  from the current worker fork, including unsuccessful experiments. Per-game
  artifacts, repeated compiler captures and binaries are not copied here.
- `support-repairs/`: the isolated support repair candidates, feedback and reports.
- `FOCUS.md`, `CHECKPOINT.md` and related JSON: historical priorities and evidence.
- `conditional-promotion-gate.json`: a narrow study-specific authorization, not a
  general exception to the joint-target research gates.

Original absolute paths remain in historical evidence so its identity is honest.
Use episode/request IDs and hashes to retrieve remote artifacts or transfer private
raw data. Missing raw inputs mean an audit is not yet reproduced on the new host.
The old XP ledger and live locks must be transferred privately, not reset from
this source archive. No token, credential store or signed upload URL is included.

The repository sync also preserves first-party local game/UI/test changes and
research documents. Reinstallable dependency checkouts, Python caches, generated
application builds and the raw `duels/` replay archive remain local/ignored.
