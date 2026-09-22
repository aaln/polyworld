# New-week policy versions

## aaron-gota-week0921-lane:v1

- Version `9fc7f72e-0489-48f5-a5d3-c53fca44cff4`, source SHA256 `ad3f1d5ca719491cc3e34a76a0bcdf7434aed45b4fb1a707a65ecdcf65f030f9`.
- Registered 2026-09-22T04:17:22.604001+00:00. Engine 2026.9.21.5 / f776d5e55d439706a8d49878d17d7ba1f6a1f7ce.
- New coordinated draft/lane/skill/economy/recovery policy. Native validation complete; hosted quality unvalidated. Inert upload; no champion selection.

## aaron-gota-week0921-baseline:v1

- Version `6559c395-82f9-4fa4-8f7e-6f3481d9f169`, source SHA256 `eeabcd4c5f5ff1f3719525fe17af1ca28cb027c4cf12a575c1bd99d9eef0773f`.
- Registered 2026-09-22T04:17:23.358301+00:00. Engine 2026.9.21.5 / f776d5e55d439706a8d49878d17d7ba1f6a1f7ce.
- Byte-exact upstream baseline for a fixed opponent. Native validation complete; hosted quality unvalidated. Inert upload; no champion selection.

## Final validation — 2026-09-22 UTC

- Candidate executable remains byte-identical to the registration above. All 160 candidate hosted games completed with no subject VM failure.
- Uniform comparison passed: candidate mean score red 553.4651 / blue 584.7613 versus compatibility control 26.0933 / 90.3153, 40 games per cell. Candidate fort outcomes: 74 wins, 6 draws; blue win frequency regressed relative to the control.
- Mixed-team holdout: all 160 games audited, but other-policy failures left zero clean games. Gate unqualified; all-game candidate scores 389.6118 / 930.8632 versus control 0 / 173.7701 are tainted diagnostics.
- 126 actual-host scenarios, six compiler checks, complete native matches and exact hosted replay audits passed. Saved IR feedback changes no executable bytes.
- Policy/IR and full bounded results: `examples/gods_of_the_arena/players/ir/forks/week20260921`. No league or formal acceptance changes.
