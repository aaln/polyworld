# Fresh GotA research context

This is the working entry point for a new conversation. Read this file and `research/RESULTS.md`; open the indexed references only when needed.

## Task and authority

Improve **expected individual score**, `floor(max(0, lifetime XP - 200 * elapsed_minutes))`, including draft time. Report positive-score frequency and positive-score mean to explain the overall average. Team wins, fewer deaths and neutral kills are diagnostics, not separate optimization targets. Longer games help only when added XP exceeds the added time cost.

The workspace pins upstream **2026.9.23.4**, commit `2c8db6ebe1dc785ce1eea87496505d1244ee4c44`, replay **62**, with neutral camps, explicit spells and crowd control. Before new hosted work, verify the live game against this pin. A newer engine needs a separate release audit and fresh controls. Read [current mechanics](research/knowledge/MECHANICS.md); the checked-in engine is authoritative.

## Where we stand

| Reference | Source prefix | Role |
|---|---|---|
| [deployed](research/policies/deployed) | `2fbd789b` | Retained incumbent; default parent for a new hypothesis |
| [previous](research/policies/previous) | `29f6d7e6` | Previous high-scoring policy, preserved for isolated transfers |
| [weak-neutral](research/policies/weak-neutral) | `c2321ead` | Tested candidate that did not pass the score gate |

The completed **180-game current-engine study** used 60 controls and two responsive 60-pair comparisons across every side/team seat. Deployed mean **1,527**, previous **1,616**, weak-neutral **1,398**. Previous-minus-deployed adjusted 97.5% interval **[-246, +405]**; weak-neutral **[-318, +42]**. Neither challenger qualified. Zero-score counts were **6, 19, 12** respectively. All ten VMs, replay hashes, XP and score accounting passed. No automatic rollback is supported.

Last verified league champions (2026-09-24 03:09 UTC; re-read before changing):

- Aaron: `quartz-marten-62e4:v1`, version `3ddff6be-799c-4cb7-a592-6c73471b456e`.
- Aaron's Co-play Coach: `linen-kestrel-62f5:v1`, version `c1dbd6b2-b73a-450d-80a5-4e67bdc4fb84`.
- Both have source `2fbd789b`. League `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`.

The working tree started clean from the engine commit. The previous workspace and original coaching inputs are preserved. Historical qualification flags apply to their original studies; `research/manifest.json` records current qualification.

## Useful knowledge, loaded on demand

- [IR ↔ policy workflow](research/IR_WORKFLOW.md): exact compilation, extraction, binding edits and evidence review.
- [Controller skill index](research/knowledge/controller.ir.json): all 21 rules in execution order, source lines, region hashes, semantic contracts, parameters and additional persistent state.
- [Knowledge map and transfer lessons](research/knowledge/README.md): historical policy pairs, opponent models, successful components, rejected bundles and pending ideas.
- [Hero-specific findings](research/knowledge/HERO_NOTES.md): observed class coverage, neutral income, score and concrete weaknesses.
- [Hypotheses](research/knowledge/hypotheses.ir.json): unvalidated next interventions with falsifiers.
- [Khors v180](research/opponents/khors-v180/README.md): 28 version-bound appearances; descriptive motifs, not an executable opponent proxy.
- [Coaching input index](research/coaching_inputs/manifest.json): four original sessions, copied notes/synthesis/input text and hashed media locations.

The `research/library/` tree is a **frozen historical reference library**. It contains 16 additional IR/BASIC snapshots, Richard v174 and relh v169 source models, older khors models, coaching reviews and experiments. It is not another set of current instructions. Old opponent identities, automatic spell casting and match-win gates do not govern new work.

## Best next question

Why do low-income heroes miss productive opportunities? A zero-score Vanguard source reconstruction selected camps whenever it saw an eligible one, but had only **15 such decisions out of 1,553**. In the hosted study both Vanguard games earned zero neutral XP. Nearby target selection alone did not solve camp access. Test bounded safe routes with travel cost and abandon rules, preserving lane XP opportunities.

Treat hero transfers separately: the candidate increased Death Knight neutral XP but reduced score; Lich improved in only four exploratory games. Arcanist has a separate verified shopping/mana-restoration issue. A class-specific fork selected from these results needs fresh confirmation; the selection sample cannot confirm itself.

## Run and experiment discipline

Use `/Users/aaln/experiments/softmax/metta/.venv/bin/python` for the existing environment. Run `python research/verify_workspace.py` first. [Environment and tool commands](research/OPERATIONS.md) provide build, replay and API entry points. Policy conversion and current API/statistics imports work without the old workspace. Original full replay/media captures and the local dependency cache stay at the locations in the manifests.

Each future XP request has **at most 100 games/variations** and uses responsive paired counterfactuals with identical seed, roster, slot and engine/configuration. The permanent shared allowance is **100,000/day**, with the existing **400/cycle** and **3 active requests** limits. Use the shared journal and ownership files at `../gota-autoresearch`; preserve their history. Its legacy worker remains paused. Credentials are loaded by the existing saved-user client; do not copy secrets into the repository.

Freeze source/IR, selection, opponents and numerical decision rule before outcomes. Audit every actor, full replay hashes, XP receipts and integer score. Invalid games prevent qualification; do not turn runtime failures into zero scores or filter outcomes to pass. Confirm promising changes on fresh contexts. No universal verdict-size floor or guarantee of future score preservation has been established.

The user prefers opaque upload names. These are bespoke names, not a privacy guarantee. Earlier league/GitHub publication authorization and unsigned-commit authorization are recorded; publish only concrete reviewed results within that scope. This migration itself changes no policy, league membership, game rules or hosted budget usage.

## Suggested opening prompt for a new conversation

> Read START_HERE.md and research/RESULTS.md. Continue individual-score research from the retained deployed policy, using the previous policy as a transfer reference. Investigate low-income heroes' camp access and XP eligibility. Edit through semantic IR, test coordinated changes with current-engine responsive controls, retain only supported improvements, and preserve all evidence. Load historical references only when relevant.
