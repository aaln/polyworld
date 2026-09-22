# Guide: infer an opponent policy from observations

Revision 2 — 2026-09-20. This is the maintained guide for new studies. Existing studies keep their original guide, model, split and evidence hashes. The revision follows the [Richard v135 source audit](../opponents/richard-v135/source-audit-20260920/README.md).

An opponent IR should predict behavior at a declared level of detail and preserve what remains unidentified. A model that forecasts “targets a structure” can be useful without knowing which structure, why, when a command occurs, or what the opponent will do after our intervention. Give each of those capabilities its own evidence and validation status.

## 1. Bind identity and freeze the question

Record opponent owner/name, policy-version UUID, game/build commit, map/configuration, our exact policy hash, roster/classes, side, dates and observation authority. A version label alone is insufficient: Richard v135 and a relh file named `...v135.bas` are different policies. If source becomes available, record repository commit, path, byte hash and the manifest mapping that hash to the hosted UUID.

Before reading heldout behavior, freeze the episode-selection rule, chronological split, population baseline, feature definitions, segmentation, prediction target, metrics, rejection conditions and guide snapshot. Retain failed hypotheses. Exact repeated observer streams must be grouped, and novelty across train/heldout must be reported. Generated seed labels do not establish independent trajectories.

State the intended use: descriptive observation, forecast, mechanism hypothesis, executable proxy, or tested counter. These are separate validation levels. Source access changes the study into a source-informed study; it does not retroactively improve the observation-only score.

## 2. Preserve three kinds of evidence

| Evidence | Permitted use | Required boundary |
|---|---|---|
| Our actual predecision observation | Fit an observation-only model and construct executable own-policy predicates | Preserve observer slot, timestamp, visibility and history; do not pool teammates unless their runtime can do so |
| Replay truth / opponent commands / private memory | Score observability or explicitly declared retrospective audits | Never silently expose these as observation-only features |
| Later source reveal | Verify identity, recover mechanisms, design discriminating experiments | Separate artifact and status; old freeze and old heldout result remain unchanged |

Our view and the opponent's view differ. “Visible to us” does not establish “visible to them,” and “not in our view” means unknown. Distinguish standing structures from exposed structures: on GOTA .5, structure `objectAlive` means exposed, while positive HP establishes standing. Target ID zero can mean no target or a masked target.

Every observation needs episode/tick/actor, visibility, lagged features, alternatives and why they were affordable/available, chosen observable event, subsequent visible outcome, censoring and evidence references. Affordances are estimates unless the host contract establishes them. Preserve object kinds and target IDs even when a first model groups them.

## 3. Represent behavior on several time scales

Maintain an event stream as well as sustained segments. Record target changes, motion changes, visible hits, casts, item changes, deaths/reappearances and response delays at the finest observable resolution. A six-tick segment threshold can describe sustained behavior while erasing one-decision hit recovery and four-decision mode changes. Inspect residual and short events; do not discard them as noise by default.

Specify each clock: world tick, living policy decision, ability charge/cooldown, attack windup/recovery, and longer commitment. Identify persistent state as a hypothesis with update/reset rules. Compare identical current observations with different observable histories to test whether memory is needed. Death, lost visibility and respawn censor histories; do not invent a reset.

Separate channels: navigation, attack intent, spell attempt, inventory/economy, and coordination can coexist. A visible target is neither a newly issued attack nor a landed hit. No movement can mean turning, collision, attack timing or a command to the current position. A requested cast/buy is distinct from acceptance and resulting effect.

Treat inventory and levels as event streams too. A newly visible item establishes acquisition before first sighting, not an exact purchase tick; a level change establishes a threshold crossing, not which hidden kill supplied XP. In a source/truth audit, reconcile accepted purchases, actual gold debits, kill-reward attribution and level thresholds. Separate income, item-selection policy, nominal class stats and measured attack cadence before explaining a combat advantage.

## 4. Use the seven semantic layers without inventing an execution graph

| Layer | Observation-derived content |
|---|---|
| `situation` | Measured features, units, timestamps, missingness, perspective and estimated affordances |
| `belief` | Counted claims, alternatives, uncertainty, identity and validation scope |
| `goal` | Hypothesized purpose linked to claims; “unknown” is valid |
| `skill` | Observable operators with initiation/termination and simultaneous channels |
| `strategy` | Conditional preferences; candidate priority edges only when discriminated |
| `execution` | Observation/forecast binding, supported output granularity, cadence assumptions, proxy eligibility |
| `update` | Parent freeze, evidence additions, rejected hypotheses, source-reveal status and new tests |

Keep the established `id / when / skill / for` rule shape and stable IDs. A list of preferences is not automatically an ordered controller. Put extension fields behind a schema/binding discriminator; do not feed inferred models to the BASIC compiler as known policy code.

For each mechanism hypothesis, also retain a record like this:

```json
{
  "id": "OPP_M001",
  "claim": "An attack on the sieging hero changes its target",
  "status": "proposed",
  "observed_from": "our_slot_0_predecision_view",
  "when": {"objective_kind": "tower", "attacker_target": "opponent_actor"},
  "skill": "retarget_attacker",
  "for": ["self_preservation_hypothesis"],
  "alternatives": ["nearest_enemy", "lowest_hp_enemy", "fixed_siege_commitment"],
  "priority": {"overrides": [], "overridden_by": [], "identified": false},
  "state": {"required_history": "unknown", "reset": "unknown"},
  "evidence": {"eligible_opportunities": 0, "choices": 0, "episodes": 0, "distinct_streams": 0},
  "discriminator": "Hold geometry fixed; vary whom the nearby hero targets",
  "prediction_record": {"n": 0, "metric": "target_id_and_latency"},
  "proxy_usable": false
}
```

When guards overlap, test which action wins. An ordered base controller, learned mode, scripted correction, defense override and hit-recovery movement can all execute in one decision. Preserve the ordered command bundle and host acceptance in source audits. Do not infer the final world effect from the last command of an unrelated channel.

## 5. Test alternatives and feature sufficiency

Start with a population prior and simple individual model. Report which recorded features actually enter the predictor. Class, side, phase, relative HP, range, exact structure kind, threat target, ally geometry and recent hits may explain apparent preferences. Do not assume their relevance; compare richer candidates on development data and reserve a new holdout for changed models.

Use paired discriminators: vary one condition while keeping relevant geometry/history fixed. Examples include attacker targets self versus ally, tower versus god versus barracks, in-range versus just out-of-range, nearest defender versus a closer teammate, and post-hit versus no-hit. Test competing explanations and boundary cases, not only confirming examples.

For coordination, distinguish shared geometry from communication, roster role from dynamic election, and common destination from synchronized commitment. Test teammate availability, distance ties, death, displacement and staggered arrival. For individual play, measure accepted spells, hit timing, damage taken per engagement, survival and target selection. A win total alone cannot identify which skill improved.

If multiple mechanisms produce the same observations, retain an equivalence set. “Not identifiable in this sample” is a useful result. Require eligible opportunities before treating missing behavior as negative evidence. A source branch may exist and never fire against our policy.

## 6. Score the capability you actually built

Report separately:

1. Coverage: visible living actor-ticks, observer-dead fraction, censored starts, residual events, episodes/classes/sides/phases and distinct streams. For a tested mechanism, report eligible opportunities and the guard/action/accepted-effect funnel.
2. Forecast: target category, target ID, action arguments, onset time, duration and termination as separate metrics. If scored only at retrospectively known segment starts, say so prominently; it is not an online event-timing predictor.
3. Calibration and baselines: same-context population, class/side/phase alternatives and persistence. A smoothed choice frequency is not a posterior probability that an inferred rule or goal is correct.
4. Generalization: chronological holdout, trajectory novelty, per-class/side results and uncertainty grouped by independent units available. Hundreds of events from three streams are not hundreds of independent demonstrations.
5. Mechanism: intervention response, boundary behavior, suppressors, precedence and history dependence. Keep this separate from heldout motif accuracy.

Predeclare minimum opportunity/coverage requirements for the intended use. Avoid a universal “n events means identified” rule. Failed forecasts and unknown contexts remain visible, and confidence decays or resets across policy versions.

## 7. Validate a proxy before using it for counterfactuals

Marginal occupancy, path shape or motif accuracy alone cannot qualify an executable proxy. Require heldout agreement on action timing, target identity, argument values, concurrent channels, memory effects and response to interventions relevant to the proposed counter. Compare conditional and closed-loop behavior; report divergence with its horizon and state coverage.

Use a ladder of evidence:

1. Source replay reconstruction, when source exists: identical commands and state hashes on the original tape establish exact behavior on that path.
2. Synthetic VM fixtures: establish command/guard semantics under supplied observations. Scripted acceptance does not establish game reachability or combat efficacy.
3. Short interventions with the actual opponent responding: establish local causal effects; other frozen actors limit the claim.
4. Full games with both teams responding: establish matchup effects under pinned rosters/configurations.
5. Fresh XP comparisons against the exact hosted opponent and preservation opponents: establish the candidate's deployment claim, with both colors and runtime validity audited.

A tape of future opponent commands is invalid once our action changes their observations. If authentic source is available and bound to the hosted UUID, prefer running that source over a coarse proxy. Its availability does not validate a separately authored semantic reimplementation. Keep `proxy.usable=false` until that implementation's own contract passes.

For candidate counters, preregister source hashes, one attributable change, expected mechanism, primary outcome, validity checks and rejection rule. Quarantine VM cutoffs as invalid execution, separately from losses. Profile complete episodes and dense scenes with margin below the actual instruction/work limits; a runtime-safe counter is part of the tested artifact.

## 8. When source is revealed, audit rather than rewrite history

Freeze and hash the original model, guide, predictions and evidence. Verify the supplied source's owner/UUID/hash/commit against an authoritative manifest and, where possible, reconstruct original command streams. Publish a separate source model and a claim-by-claim comparison with these outcomes: compatible at the original granularity; overbroad if treated as a mechanism; omitted mechanism; contradicted by a discriminator; or untested/unidentified. Preserve the old forecast status alongside the new audit assessment.

Count source branch activation on the old corpus, including later suppression. New source-informed fixtures and richer features require new evidence; the old holdout has now been inspected. Document which conclusions come from source text, private runtime state, synthetic tests, or public observation. A source comment is a hypothesis about purpose, not proof of that purpose's effectiveness.

Richard v135 is the worked example: the old model scored 694/923 sustained starts (75.2%) versus 502/923 for the population prior. Exact source replay later matched 915,098 commands across all 20 games. Yet the version's tower-siege retaliation branch fired zero times in those games. Synthetic tests showed target changes that the coarse `hero/creep/structure + absolute HP` context cannot distinguish. Both results are true: useful forecasting at its declared resolution, and insufficient identification for a counterfactual controller.

The Ranger follow-up supplied a second lesson: source contains a Ranger-specific equipment branch, but all audited decisions selected the generic objective build. Accepted-purchase logs, rather than source branch names, establish what was bought. Six Ranger games repeated one published Ranger trace: nine-tick basic-hit intervals and later hero-kill income explain observed strength more precisely than either the nominal 18-tick class cadence or “he farms well.” Their causal contribution to a new counter still requires responsive experiments.

## 9. Deliver artifacts another session can use

Publish the model in machine-readable IR, a concise interpretation, raw evidence references, split/freeze/guide hashes, prediction records, rejected alternatives, limitations and next discriminators. For a source audit, add pinned source, provenance, execution order, activation receipts, claim comparison and reproducible probes. For a counter handoff, add tested successes/failures, exact candidate hashes, public predicates, expected mechanism metrics, field-preservation gates and proposed experiments with explicit status.

Keep historical artifacts immutable. New guide versions affect new studies. Never silently republish a frozen report with a revised guide or source-informed model.
