Gods of the Arena — human play

Run `./examples/gods_of_the_arena/gota` from the repository root. Choose a hero
and press Enter; the other nine seats use bundled bots. Practice opponents
make decisions more slowly and cast only their primary ability. Standard uses
their full abilities. The guide is optional.

On macOS, `python3 examples/gods_of_the_arena/install_desktop.py` installs
**Gods of the Arena.app** on the Desktop with the game logo. Double-click it to
play; it uses this checkout's assets and picks up subsequent native builds.

| Input | Action |
| --- | --- |
| Right-click | Move or attack |
| Left-click | Inspect; confirm an armed spell or attack-move |
| Q / W / E / R | Cast the four abilities at the cursor |
| A, then left-click | Attack-move |
| S | Stop moving and attacking |
| F1 | Recenter and resume following your hero |
| L | Toggle the automatic follow camera |
| Hold C and move pointer | Pan; arrows, middle-drag and minimap also work |
| V | Ask one healthy teammate for assistance at the cursor |
| Alt+V / Shift+V / Ctrl+V | Attack / defend / retreat call |
| Alt+left-click | Assistance call |
| Esc | Cancel targeting; otherwise pause and open controls |
| Space | Pause/resume |
| F6 | Replay inspection / return to live |
| B, F / G | Existing shop and item controls |

The camera follows automatically until you pan. It returns to your hero on
respawn. Your health, mana and ability bar stay visible when inspecting someone
else. Hover an ability for its effect, target rules, costs, cooldown and charge
recharge. A failed attempt explains why it failed and never fires later.

Esc → Controls offers quickcast, aim-and-confirm, and assisted casting at the
inspected/combat target. Self abilities fire immediately in every mode. Clicking
a non-self ability in quickcast mode enters aim-and-confirm so it can be aimed
away from the HUD. Right-click or Esc cancels aiming without issuing movement.
Combat sounds are optional and initially off.

Heroes move as soon as you redirect them, turning while they walk. Base movement
speed is 75% above the original tuning (40% faster than the first movement update),
and living heroes and creeps walk around occupied units. Right-clicking the ground
marks your destination with the expanding green circular pulse used in Pudge Wars.
Friendly health bars stay green and enemy bars stay red, including at low health.
The roster and hero panels use a compact layout with full-size text, leaving more
of the arena visible when zoomed in.

WASD controls use 1–4 for abilities, Q for attack-move and X for stop. The mouse
key preset enables A/D/S as left/right/middle mouse, with Z attack-move and X
stop. Custom bindings can be loaded with `--keys PATH`, using entries such as
`spell1 = KeyQ`, `stop = KeyX`, `center = KeyF1`, or `ping = KeyV`.
Changing a preset resets custom bindings to that preset.

Examples:

```sh
./examples/gods_of_the_arena/gota --player:7 --difficulty standard
./examples/gods_of_the_arena/gota --controls wasd --cast normal
./examples/gods_of_the_arena/gota --record match.replay
```

Matches end with victory, defeat, or a time-limit draw, plus personal stats and
rematch/hero selection. Recorded rematches use `match-2.replay`, etc. F6 lets you
review recent play with commands disabled; Return to live resumes at the latest
recorded tick. Team calls expire after five seconds; bundled bots respond, and
custom policies can opt in through the `allyPing*` host data.

Build with `nim c examples/gods_of_the_arena/gota.nim`, or add `-d:emscripten`
for the browser build. Use the dependencies pinned in `coworld/dependencies.lock`
(including OpenAL for optional sounds); `POLYWORLD_DEPS` selects a dependency
directory and `SILKY_PATH` can override an older sibling Silky checkout. Serve
`examples/gods_of_the_arena/emscripten` over HTTP and open `gota.html`.

Human input and flow regressions are in `tests/test_gota_human.nim` and
`tests/test_gota_playflow.nim`. `tests/test_gota_movement.nim` covers rapid redirects,
immediate reversals, unit avoidance, arrival, and historical movement speeds.
Existing spell, attack, replay, simulation and map
preset tests cover combat and deterministic playback. Shopping behavior is unchanged.
