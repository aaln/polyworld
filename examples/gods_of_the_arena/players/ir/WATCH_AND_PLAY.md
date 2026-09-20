# Watch the policy and play a hero

The native viewer is built at `tmp/gota-ir/gota-viewer`. Run the launchers below from the repository root, or double-click their `.command` files in Finder. They start paused; press **Space** to begin.

The current targeting candidate has a separate recording and a viewer built against the published `.3` replay format:

```sh
./tmp/gota-ir/review/watch-duelist.command
```

Select the first Red hero, **Death Knight**. It uses the moderate hero-priority candidate; all nine other heroes use the default baseline. This is the first discovery-seed/seat recording (seed 41000), lasting 8:15.33 and ending in a Red win. The candidate died three times and ended with four equipment items. Its complete 112,804-action tape independently reproduced every state hash. This individual recording illustrates behavior; the separate held-out campaign determines whether the candidate improves win rate.

```sh
# Watch the selected wave-following policy lose on seed 2026.
./tmp/gota-ir/review/watch-policy.command

# Watch the original baseline win on the same seed.
./tmp/gota-ir/review/watch-baseline.command

# Control the same hero yourself; nine baseline bots fill the other seats.
./tmp/gota-ir/review/play-human.command
```

## What to watch

In the policy recording, **Red's second hero, the Crossbowman**, uses the selected offset-0 wave-following policy. Every other seat runs the baseline. Click its portrait in the top panel to select and follow it. Selecting a hero also shows that team's fog of war.

The policy match lasts **11:07.33**, ending in a Blue win. The all-baseline comparison ends at **9:24.50** with a Red win. This is one useful counterexample, not proof of a general failure mechanism.

Use Space to pause/resume, the transport bar to select 1×/2×/4×/16× playback, and its timeline to seek. Watch whether following a footman leads to useful pressure, and whether the hero then leaves that wave when an enemy appears. R4 only governs movement when no attackable enemy is observed; visible-target combat remains the original nearest-enemy policy.

Send a timestamp, selected hero and what you wanted it to do. The `.trace.jsonl` beside each replay records sparse actual rule decisions; its clock is ticks at 24 ticks/second. The public replay contains actual commands and world outcomes, not the policy's authored intentions.

Files under `tmp/gota-ir/review/`:

- `waveguard-loss.replay`, `.trace.jsonl`, `.result.json`
- `baseline.replay`, `.trace.jsonl`, `.result.json`

## Human controls

The human launcher assigns you **seat 2**, Red's Crossbowman, on seed 2026.

| Action | Control |
| --- | --- |
| Move your hero | Right-click walkable ground |
| Attack/chase an enemy | Right-click the enemy; left-clicking an enemy also issues attack |
| Select/focus a hero | Click the hero or its top-panel portrait |
| Pan camera | Arrow keys, middle-button drag, or click/drag on the minimap |
| Zoom | Mouse wheel/trackpad scroll |
| Open/close shop | Click the **INVENTORY / SHOP** title at bottom right |
| Buy | Click an item in the shop; you can buy anywhere if affordable |
| Use an item | Click its inventory slot; **F/G** use the first/second slots |
| Pause/resume | **Space** |

Combat abilities activate automatically. The visible Q/W/E/R labels do not provide manual spell casting in this build. Arrow keys move the camera; this is a click-to-command game rather than direct WASD movement.

Destroy enemy towers in lane order (outer → inner → gate), then the exposed fort. A fort victory determines the score. You respawn after dying. Human matches are saved as `tmp/gota-ir/review/human-<timestamp>-<pid>.replay` when you close the game window normally.

## Rebuild the viewer in this workspace

The older vendored Silky/Windy copies could not compile the current UI. The prepared `viewer-deps` directory uses the repository's pinned Silky and Windy revisions and links the other existing local dependencies. Original dependency checkouts were left intact.

```sh
POLYWORLD_DEPS="$PWD/tmp/gota-ir/viewer-deps" nim c --hints:off \
  -o:tmp/gota-ir/gota-viewer examples/gods_of_the_arena/gota.nim
```

Native launches must run from the repository root so the renderer can find `../polyworld_data`; the supplied launchers do this automatically.
