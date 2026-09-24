# Explicit sustain and cautious melee farming on replay60

The frozen source changes Vanguard/DeathKnight recovery and close-threat spacing, plus Arcanist/Warlock mana restoration. These four classes unlock their resource ability from level2 and avoid redundant same-decision lethal creep casts. Other classes retain their behavior. Broad melee variants were rejected in local exploration; see evidence/local-exploration.json.

Run `python verify.py`. Recompile with `python convert.py compile --out /new/path`; extract with `python convert.py extract --source policy.bas --out /new/path`. Evidence in `evidence/trial-report.json` controls competitive qualification. Captured inputs and initial IR remain unchanged in the raw study.
