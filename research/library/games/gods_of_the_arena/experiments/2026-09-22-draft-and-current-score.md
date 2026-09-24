# Current-release draft and score follow-up

User steering: continue micropractice, prevent obsolete IR from constraining the
new game, and investigate relh's Ranger versus our frequently dying Vanguard.
Episode: [ereq_cd49a7f0](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_cd49a7f0-5410-4506-9c2d-c8c275d9c749).

Active engine: **2026.9.21.5 / f776d5e55d439706a8d49878d17d7ba1f6a1f7ce**.
Current reference: `microplay20260922`, BASIC SHA256
`b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098`.
Raw inputs and every failed experiment remain in `tmp/gota-targets-20260922`.
The earlier 480-game target panel and its original fort/score gates stay frozen.

## Exact episode findings

The game used **Coach compat:v1**, UUID `7dcba95c-6966-4a86-b033-7ffcafa8991f`,
not the new practiced policy. The complete replay reproduces every state hash,
the final XP and the official per-hero scores. Typed events show:

| Measurement | relh v161 | Coach compat:v1 |
|---|---:|---:|
| Hero | Ranger | Vanguard |
| Draft tick | 1237 | 13 |
| Final level | 8 | 2 |
| Deaths | 0 | 5 |
| Lifetime XP | 2685 | 209 |
| Hero-kill XP | 1350 | 0 |
| Creep XP | 735 | 209 |
| Structure XP | 600 | 0 |
| Basic hits | 377 | 19 |
| Official score | 1698.19 | 0 |

At tick 13, only the first opponent's Crossbowman had been selected. Ranger was
available, but Coach explicitly chose Vanguard. relh selected Ranger much later.
relh bought only Ranger Boots in this episode; an expensive weapon progression
does not explain this particular XP lead. Coach bought dagger, then sword, then
mana potion, and never armor. Its deaths came from Lich twice, a creep once and
relh twice. relh dealt 891 damage to Coach; creeps dealt 518, Lich 503 and the
Crossbowman 92. A melee exposure problem is a hypothesis; hidden policy beliefs
were not captured and are not inferred as fact from post-tick public views.

Three Coach teammates (slots 6, 7 and 8) had BASIC VM failures. This game is
useful diagnostic evidence, but cannot establish a clean counter-policy win
rate or a causal comparison of hero classes.

## Actual-host draft practice

`draft_practice.nim` recreates only the known public opening: first red pick is
Crossbowman, then the subject's legal blue turn. All subsequent draft choices
come from the tested BASIC; future replay actions are not replayed as opponents.
The retained practiced policy selects **Ranger at tick 13**. If the first enemy
takes Ranger instead, it selects **Arcanist at tick 13**. Both checks pass with
1,738 instructions / 3,960 work. This proves the draft action, not a full-game
counterfactual outcome. Hero availability is global; Ranger cannot be guaranteed
from every later draft position.

## Further micropractice and rejected refinements

Armor reserve works in scarce-gold drills: melee heroes acquire armor by the
third shop visit rather than repeatedly spending their gold on consumables.
However, both the all-class and melee-only reserve variants failed their
matched-color native comparisons. Their sources and results are preserved.

A three-tick observation loop improves the contested-wave drill from 285 to
315 XP at unchanged 240 last-hit gold. Fresh two-seed, both-color responsive
confirmation fails: candidate mean score red **433.38** versus parent **591.66**,
blue **679.13** versus **553.11**; aggregate ratio **0.9718**. Every VM/replay is
valid, but red regresses 26.8%. Reject it; do not upload or spend hosted games
on it. Keep the original six-tick practiced executable unchanged.

## Prospective mixed-team comparison

This asks a new question: does the retained practiced bundle improve the
deployed compatibility policy's score in healthy mixed teams?

- One Aaron subject seat, first pick on red and blue; nine distinct other
  players, exact versions frozen before games. Current Jordan is v317, not the
  completed target panel's v306. relh remains v161 and Richard v153.
- Candidate `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7` versus live Aaron control
  `c2785cd4-433b-46d1-a454-dd29147383ec`. The Coach compatibility copy is a
  separate, fixed participant in both arms.
- Preflight each exact roster version using at least three recent completed
  games per color, inspecting that participant's VM status. This is runtime
  screening, not strength-based selection.
- 40 games per arm/color, **160 total**, existing shared ledger and ordinary
  limits. Hold all other roster slots fixed within each color. Audit all ten
  VMs, every state hash, final XP and official scores.
- Current-score gate: all games clean; candidate score at least 95% of control
  on each color and a strict aggregate increase of at least 10%. Fort outcomes
  are diagnostic. Superiority to the opposing team's mean score is a separate
  claim. No automatic league selection.

`healthy_field.py` uses `current_score.py`, independently of the historical
win-only acceptance controller. Six evaluator tests verify that XP gain with
draws can advance, fort wins with XP regression cannot, old engines or changed
opponents cannot serve as controls, and invalid games prevent advancement.
Two fixed first-pick rosters cannot establish strength at every draft position,
against every current policy, or a number-one leaderboard rank.

All160 first-pick games are complete and clean; every replay/XP/score audit
passes. The current-score gate passes on both colors.

| Policy / color | Score | XP | Deaths | Level | W/L/D |
|---|---:|---:|---:|---:|---|
| Practiced red | 4081.61 | 7159.20 | 3.95 | 13.45 | 24/11/5 |
| Compat red | 0 | 362.68 | 3.83 | 2.62 | 0/40/0 |
| Practiced blue | 2511.85 | 4525.32 | 2.62 | 10.53 | 39/0/1 |
| Compat blue | 0 | 1162.47 | 8.85 | 4.92 | 29/3/8 |

The practiced policy selected Ranger in all80 subject games. Blue compat chose
Vanguard in all40; red compat ended with Crossbowman14/DeathKnight26. Absolute
red deaths did not decrease; improved red growth/score must not be described as
a red death reduction. The four cells have40/40/37/40 distinct complete command
streams, which does not establish statistical independence.

Nine retrospective median-score replays, stratified by observed outcome, have
additional typed-event audits. Candidate hero XP includes substantial creep,
hero and structure rewards; all five selected candidate replays buy all four
planned permanent items and complete4–10portals. The selected controls complete
none. This confirms skill activation in those examples, not isolated causality
or a representative estimate from the retrospective subset. Spell out-of-range
rejections remain a concrete future improvement target.

## Conditional later-draft guardrail

Before collecting its results, freeze `middle-field/plan.json`: unchanged
candidate/control bytes, same nine healthy-preflight participants, subject in
the third team pick on both colors. Forty games per arm/color,160additional,
within the same320-game cycle total and shared daily cap. This tests a broader
draft context where Ranger may already be taken. Use the same current XP-score
preservation/improvement rule; no fort-win gate. The first-pick comparison
passed, so the conditional guardrail ran. Any deployment uses the
user's existing explicit latest-league/two-player authorization, with a separate
decision and rollback record after both comparisons finish.

All160 third-pick games are complete and clean, with exact replay/XP/score
agreement. The guardrail passes.

| Policy / color | Score | XP | Deaths | Level | W/L/D |
|---|---:|---:|---:|---:|---|
| Practiced red | 1719.68 | 4541.60 | 6.00 | 10.55 | 12/26/2 |
| Compat red | 0 | 867.75 | 4.30 | 4.33 | 0/39/1 |
| Practiced blue | 1938.65 | 4808.95 | 4.43 | 10.95 | 38/0/2 |
| Compat blue | 581.30 | 3425.08 | 8.68 | 9.03 | 26/0/14 |

Third-pick candidate drafts: red Arcanist35/Druid3/Lich2; blue Arcanist33/Lich7.
Thus its gains are not restricted to obtaining Ranger. Absolute red deaths rise
despite much higher score and growth; do not claim universally fewer deaths.

Retrospective exact opponent scores, with allies excluded: candidate exceeds
relh161's mean in all four tested cells (relh297.15/604.74 at first pick and
398.55/1162.11 at third pick). Candidate also exceeds Jordan317 and Richard153
in both red cells, where those players are opponents. They are allies in the
blue cells, which provide no corresponding blue-side counter evidence.

One actual episode runnable per arm verifies the exact player-file content hash;
every episode separately verifies roster UUIDs. Both old compatibility
registrations share file hash `983a3343`; stats metadata had null file hashes,
so the identity proof uses actual episode specs. All eight arm runnables match
the expected source. The original screenshot and raw API/replay inputs remain
preserved locally.

Fresh league readback found **Jordan356** (`a4be5384-ca46-4e96-9a14-cc4932a45903`)
after the frozen study. It is **untested**. relh161 and Richard153 are unchanged.
This limits current-opponent claims without changing the completed A/B verdict.

## Deployment

At **2026-09-22 08:38 UTC**, both players were verified as active, competing
champions with the tested source: Aaron `aaron-gota-micro0922:v1`
(`f3f8baab-d02a-4f7f-8fc9-e1f050f967a7`), Coach
`aaron-gota-micro0922-coach:v1` (`15b325b4-e9f3-487f-bd95-a059f92d20e2`).
The IR/policy pair is in `ir/forks/current20260922`; the separate deployment
decision, exact memberships, error recovery and rollback references are in
`ir/forks/current20260922-deployment`.

Manual champion selection returned HTTP500 twice without changing the old
champion. Documented automatic selection during normal placement succeeded.
Only the unselected failed-attempt membership was retired; the API records that
as disqualified/inactive, which is not a policy runtime failure. The old
compatibility registrations and all captured inputs remain preserved.
