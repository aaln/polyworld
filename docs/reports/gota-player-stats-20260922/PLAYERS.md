# Players

`GOTA/players/` compares recent league behavior, with one column per player.
`GOTA/standings/` remains the last completed tournament. Refreshing Players
never launches games or changes tournament results.

## Refresh

Requirements: Python with `httpx`, the authenticated `softmax` CLI, Git, Nim,
a sibling `polyworld` checkout, and its Nim dependencies. Existing wiki
requirements already include `httpx`.

From the repository root:

```sh
python tools/update_players.py --hours 8
nim r -o:/tmp/polyworld-buff-style tools/style_pages.nim
python tools/test_players.py
```

Use `--softmax /path/to/softmax` if the CLI is outside `PATH`. Set
`--polyworld /path/to/polyworld` and `--dependencies /path/to/dependencies`
when the checkouts are elsewhere. `POLYWORLD_DEPS` also selects dependencies.
The dependency directory contains the packages named in
`polyworld/coworld/dependencies.lock`.

`--end 2026-09-22T17:45:00Z` fixes the cutoff for a reproducible snapshot.
The default cutoff is the current UTC time. Windows longer than eight hours
are rejected. Episode creation time determines inclusion: start inclusive,
end exclusive. Only completed league rounds are considered, and all episode
pages are read. Rounds crossing the cutoff are filtered per episode.

The collector downloads public replay artifacts and public seat statistics.
It reconstructs every replay with the matching engine and verifies every
recorded hash. The copied extractor is adapted from
`andre_von_auto/games/gods-of-the-arena/tools/gota_stats.nim`. Unlike that
report's collator, this updater groups by league player ID, not policy family.
Different policy versions remain visible in the selected player's details.
Current league players with no recent games remain visible with empty values.
Former participants in the window and built-in opponents are also included.

`tools/players/engines.json` maps replay versions to source commits. New
versions require an explicit matching engine entry. The updater builds the
same extractor against isolated checkouts in `.cache/players/engines/`.
A compile check runs before each build. Failed downloads, attribution errors,
unsupported versions and replay hash mismatches stop publication. The previous
snapshot stays intact. Unfinished or unavailable episodes are counted in the
published coverage note rather than treated as losses or zero-valued games.

Raw replays, cached API metadata, extractor binaries, build logs and engine
checkouts stay under ignored `.cache/players/`. Only aggregate `data.json`
is published. Repeated runs reuse downloads and verified rows, keyed by the
extractor source and engine commit. To release old replay disk space, remove
the corresponding directories under `.cache/players/episodes/`. Remove engine
checkouts with `git -C ../polyworld worktree remove <checkout>`.

## Interpretation

Values are arithmetic means of hero-game statistics, not ratios pooled over
all ticks. Accepted order counts exclude engine rejections. Total and repeated
order counts include rejected commands. Rejection-reason counts absent from a
verified game are zero. Missing CPU telemetry is unknown and excluded from its
metric's denominator. Attack-target shares omit games with no accepted target
orders. Cell tooltips expose the number of contributing hero-games.

The extractor fixes two details from the example: tick zero is not counted as
an extra alive tick, and movement uses full-precision coordinates with death,
respawn and completed portal jumps excluded. Tower proximity refers to original
tower locations, including destroyed towers. Time-alive measurements include
the drafting phase. Low-health walks are a proxy, not confirmed retreats.
League score is taken from recorded platform rewards to preserve each engine's
scoring rules. Mixed engine versions are reported in snapshot coverage.

League is the first category, with score, win/loss and average glory. The browser
sorts player columns by their mean recorded score in the snapshot, highest first,
with equal scores ordered by name and missing scores last. Win/loss shows win,
loss and draw percentages of the column's games, with counts in the tooltip.
Glory is computed per game:
the recorded score for a winner, otherwise zero. Its average includes losses
and draws; a missing winning score is excluded. The current per-game formula is
`max(0, floor(total XP - 200 * game minutes))`; earlier games keep their recorded
precision. Drafting follows score, then direct control, rejections, indirect
economy statistics and downstream results. Small bars compare magnitudes within
each row; a larger value does not imply better play. Selection persists locally in
the browser. No analytics or player tracking requests are sent.

The snapshot also includes full aggregates for every observed policy-version ID
under each player's `policyVersions`. Each version has its own sample counts,
game record, engine coverage and first/last game timestamps. Versions with the
same number from different policies remain separate. Version aggregates use the
same per-game calculations and missing-data rules as the combined column.

Select a player and choose a policy version to change that column. The dropdown
lists the versions played within this snapshot, newest played first. It does
not fetch newer games. All versions is the default. Version choices are kept
while switching players, until page reload; the column header marks a filtered
version. Changing a version re-sorts columns by the displayed score and updates
comparison bars while preserving the player highlight and vertical position.

## Publish

Review the snapshot window and coverage, then commit the aggregate, page assets,
and tool changes. Push `main` to deploy through the existing GitHub Pages setup.
The page is a dated snapshot; loading it does not initiate replay collection.
