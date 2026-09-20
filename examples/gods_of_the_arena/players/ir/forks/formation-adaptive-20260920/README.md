# Adaptive formation3600 fork

This frozen IR/policy pair uses public enemy equipment to choose previously tested response components. It passed the precommitted discovery and fresh confirmation thresholds against Alex g002v1 and Jordan v268 while preserving the bounded Richard v135 aggregate win threshold. All 640 hosted games were fully audited; the executable was unchanged between stages. League memberships and formal research acceptance were not changed.

Two distinct simultaneously visible living enemies with exact boots+elixir, boots-only, or dagger-only inventories select the respective response. Conflicting recognized profiles abstain. Observation is sampled every 24 ticks through tick 1800; a selected profile persists for the episode. Other policies can share these inventories: this is behavioral adaptation, not reliable player identification.

Blue selects the historical Alex remote alarm and hero-first priority, Jordan local counterpressure, or formation3600 critical defense for dagger/unknown. Red combines early caster transit and low-HP tower handoff with late formation only for dagger/unknown. The coordinated package is supported; individual causal contributions were not isolated.

| Stage | Opponent / policy / our color | W | L | D | Distinct complete streams |
|---|---|---:|---:|---:|---:|
| discovery | alex/candidate/red | 40 | 0 | 0 | 7 |
| discovery | alex/candidate/blue | 40 | 0 | 0 | 9 |
| discovery | alex/formation/red | 0 | 40 | 0 | 9 |
| discovery | alex/formation/blue | 0 | 40 | 0 | 8 |
| discovery | jordan/candidate/red | 40 | 0 | 0 | 2 |
| discovery | jordan/candidate/blue | 40 | 0 | 0 | 2 |
| discovery | jordan/formation/red | 0 | 40 | 0 | 8 |
| discovery | jordan/formation/blue | 0 | 40 | 0 | 9 |
| discovery | richard/candidate/red | 0 | 40 | 0 | 1 |
| discovery | richard/candidate/blue | 40 | 0 | 0 | 5 |
| confirmation | alex/candidate/red | 40 | 0 | 0 | 7 |
| confirmation | alex/candidate/blue | 40 | 0 | 0 | 10 |
| confirmation | jordan/candidate/red | 40 | 0 | 0 | 2 |
| confirmation | jordan/candidate/blue | 40 | 0 | 0 | 2 |
| confirmation | richard/candidate/red | 0 | 40 | 0 | 1 |
| confirmation | richard/candidate/blue | 40 | 0 | 0 | 5 |

Draws count zero. There were no invalid games. Generated seeds were not paired. Repeated streams are correlated and distinct streams do not automatically establish independent trials. The Richard control is the earlier formation3600 cohort (blue 40W, red 0W/14L/26D), not a fresh Richard A/B. The fork does not establish Richard red improvement or broad-field/mixed-team generalization. Discovery and confirmation remain separate in all evidence.

`policy.py` is primary; JSON and BASIC are generated from the seven-layer IR. Validated beliefs were reflected back without changing BASIC. `compiler.zip` freezes the loaded compiler and required pinned-engine data; `contracts.json` freezes the exact instantiated binding contracts. Reproduce offline with:

```sh
python3 verify.py
```

`evidence/` contains frozen plans, all per-episode outcomes and replay hashes, complete trajectory counts, representative source reconstructions, the four original reference pairs and failed native-admission history. `requests.json` supplies retrieval IDs. Source reconstruction matches every owned command and every replay state hash, but is retrospective rather than a counterfactual opponent rollout. Raw replays and VM statuses remain in the private study path in `validation.json`. All 130 files from the two original coaching captures retain their original hashes; failed candidates were preserved.
