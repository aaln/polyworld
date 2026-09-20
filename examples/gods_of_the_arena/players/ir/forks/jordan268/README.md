`gota_jordan268_redrace` forks the primary `gota_relh154_legacy` in the same seven-layer Python representation. [policy.py](policy.py) exposes a plain `POLICY` dictionary. [policy.ir.json](policy.ir.json), [policy.bas](policy.bas), and [semantics.json](semantics.json) preserve its executable behavior and explicit skill meanings.

The frozen fork meets the precommitted criterion of at least30/40 fresh wins on each color. Selected version: `aaron-gota-ir-j268-redrace-0920:v1` (`00cd9483-0309-4613-bf61-89f3f4a33d01`). Promotion verified at 2026-09-20T05:43:03.140815+00:00: active, competing champion for Aaron’s Co-play Coach in Gods of the Arena. See [promotion receipt and rollback](promotion.json). Aaron’s player was upgraded to `aaron-gota-ir-j268-redrace-0920-aaron:v1` at 2026-09-20T06:15:03.297298+00:00, verified active, competing champion with identical BASIC. See [Aaron’s promotion receipt and rollback](promotion-aaron.json).

The response was guided by [Jordan v268’s observed opponent IR](../../../../../../docs/opponents/jordan-v268/opponent.ir.md), particularly O15’s tendency to target heroes when heroes, creeps and structures coexist. Actual evaluation used the real hosted Jordan version `207ffaf9-0d1e-4d92-a15d-4352f1bddec2`, not an inferred proxy.

The fork clears creep waves during existing defense and keeps distant heroes on their ordinary offensive path instead of recalling them across the map. Beyond28tiles from the friendly god, the final redrace variant clears defense before selecting ordinary targets; nearby heroes retain the primary defense. Attack, movement, inventory and purchase rules still execute in their original order, including multiple commands per decision. The binding adds an explicit semantic operation, with no hidden opponent-state input.

The important experimental correction was that red’s initial3/4 waveclear screen fell to14/40 in confirmation. Opening assembly also failed0/4. Nearby-only recall then confirmed40/40 on blue in the immediate parent. Redrace extends that eligibility rule to red and preserves the blue executable branch. Those results are recorded separately below.

| Candidate | Stage | Color | Wins | Distinct audit signatures | Request |
|---|---|---|---:|---:|---|
| counterrace | confirmation | blue | 40/40 | 2 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_6fa757ed-544d-4385-8346-f2b0c4c3a080) |
| counterrace | confirmation | red | 14/40 | 9 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_080027bd-c1bf-4a7c-9486-466c938ebb1a) |
| redrace | confirmation | blue | 40/40 | 2 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_f216ad2f-904d-4999-a879-c4646d23ceab) |
| redrace | confirmation | red | 40/40 | 1 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_e44410f4-5dd2-4ff9-9dc9-f7ba436eb35a) |
| assembly | screen | blue | 0/4 | 4 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_13be54fc-1dcc-4dc3-96b7-c5132dfeda78) |
| counterrace | screen | blue | 4/4 | 1 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_f7ed5006-3c88-4511-8a68-949ecf2e28ba) |
| parent | screen | blue | 0/4 | 3 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_0a9d974b-bf50-4ce0-b4c1-699f20063851) |
| parent | screen | red | 0/4 | 3 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_6950d368-2698-4942-a0b0-9fd2f51fbb2d) |
| redrace | screen | red | 4/4 | 1 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_8b67b844-c477-493c-9fc7-00574651b810) |
| waveclear | screen | blue | 0/4 | 3 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_13dec805-73b2-4cc8-b74b-17ff92857c7a) |
| waveclear | screen | red | 3/4 | 3 | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:xreq_1e741215-de41-48b9-b9fe-82078f042ad7) |

All completed arms passed full replay state-hash and action-consumption checks, all10VM validity, pinned rosters/build/config, score and totalXP agreement. [evaluation.json](evaluation.json) contains aggregate results; [evidence-index.json](evidence-index.json) contains every completed episode and artifact hashes. The campaign has audited 188 episodes and 1,050,707 game ticks so far.

Scope: fixed five-versus-five lineups on published GOTA2026.9.16.5. Generated seeds were not matched A/B. Audit signatures exclude RNG state and include sampled frames, events and full hero summaries; they can repeat across seeds and are not counts of independent trajectories. The winning screens repeat one such signature per color. These results do not establish broad league performance or causal necessity of every retained component.

Verify the standalone bundle with Python3.10+ and its standard library:

```sh
python3 examples/gods_of_the_arena/players/ir/forks/jordan268/verify.py
```

The verifier unpacks the original native compiler snapshot into a temporary directory and checks Python→JSON→BASIC plus full-source reverse extraction. [manifest.json](manifest.json) pins all compiler files, source mechanics, the additive [contracts.py](contracts.py), and tested BASIC SHA256 `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. The original primary policy remains available in the observer snapshot; no primary source was overwritten.

For the coach/autoresearcher: retain the failed assembly and insufficient waveclear results, distinguish opponent-prediction evidence from response validation, and use fresh confirmation after selection. A useful next experiment is an ablation of creep priority under nearby-only recall; its necessity has not been isolated. Broader rosters and Jordan versions require separate tests. No such extra experiments or promotion are implied by this result.

Reproducible research files remain in `games/gods_of_the_arena/instruments/jordan268_counter`, preregistered records in `games/gods_of_the_arena/experiments`, and raw hosted artifacts in `tmp/gota-ir/jordan268-counter-20260920`. Every request is also listed in the evidence index.
