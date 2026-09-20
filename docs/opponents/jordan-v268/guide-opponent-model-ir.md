# Guide: Producing a Semantic IR of an Opponent

*For an autoresearcher agent. This guide tells you how to build a semantic model of another agent — an opponent, or any agent whose policy you cannot read — from its observable behavior, in the same medium and grammar as our own policy IR. The output lives in our policy's belief layer, drives counter-strategy, and can be embedded into a proxy policy that stands in for the opponent in counterfactual rollouts.*

---

## 1. What you are producing

An **opponent IR** is a text document describing how another agent plays, in the vocabulary of situations, skills, preferences, and goals — the same grammar as a policy IR. The critical difference: a policy IR is *lifted* from code and trace, with provenance you can point at. An opponent IR is *inferred* from behavior alone, under partial observability, from an adversary who may be adapting or deceiving. So every statement in it is a hypothesis with a confidence, an observation count, and a prediction record. There is no statement without evidence, and no evidence without a count.

The test of an opponent IR is not whether it reads well. It is whether it **predicts**: given a situation the opponent is in, does the model say what the opponent will do, and is it right more often than a baseline? Everything below is in service of that.

Three rules:

- **Observe from where you stood.** You saw the opponent only when and where your own policy could observe. Every observation is tagged with what was visible. Never fill in what you did not see.
- **Preference is relative to affordance.** An opponent who retreated when retreat was the only option has shown you nothing about preference. Record what they chose *against what they could have chosen*.
- **Infer, don't narrate.** You will find it easy to write a story about why the opponent did something. Write the tendency and its count; leave the story out, or label it a hypothesis with what would test it.

---

## 2. Inputs you need

1. **Our policy IR and glossary** at the version that played. The opponent model is written in this vocabulary first, extended where it fails.
2. **Episode traces or episode IRs** for every episode involving the opponent, with our observable state per tick. Episode IRs (from the episode guide) are preferred: they already segment time and name situations.
3. **Ground truth** per tick where available. Used *only* to score our own observability (what fraction of the opponent's actions we could see) and, in Section 8, to score predictions. Never used as if the model had access to it.
4. **Opponent identity.** Whether the same opponent (policy version, or human account) appears across episodes. Without identity you can only build a population model (Section 3).
5. **A seeded simulator** if you intend to validate by embedding the model into a proxy and rolling out (Section 8). Optional but strongly preferred.

---

## 3. Three levels of model

Decide which you are building before starting; the procedure is the same but the evidence bar and the use differ.

**Population model** — how opponents in this environment tend to play, across many opponents. Coarse, high-count, slow to change. Used as the prior for a new opponent, and as the baseline every individual model must beat.

**Individual model** — how *this* opponent plays, across episodes. Requires identity. Starts as the population model and diverges as evidence accumulates. This is where exploitable tendencies live.

**In-episode model** — what this opponent is doing *right now*, in this episode. Starts from the individual model and updates on the current episode's observations. Captures adaptation and the current plan. Short-lived; discarded or folded back at episode end.

A statement in an opponent IR carries which level it belongs to. Population statements are cheap to trust; in-episode statements are cheap to discard. The model is wrong when a level is misapplied — treating one episode's behavior as a standing tendency, or ignoring visible adaptation because the individual model says otherwise.

---

## 4. Segment the opponent's behavior into skills

You cannot see the opponent's skill boundaries; you infer them from motifs in their trajectory.

1. **Extract the opponent's observable trajectory** per episode: position, actions, targets, ability use, and any state you could see, tick by tick, with a visibility flag per tick.
2. **Segment into motifs.** Boundaries occur where the opponent's behavior changes character: direction reversals, target changes, ability use, transitions between advancing and holding. Cluster the resulting segments by their shape and outcome until you have a small set of recurring behaviors.
3. **Name each motif as a skill**, using our glossary's skill names when the behavior matches one of ours, and a new name tagged `[inferred-skill]` when it does not. Give each an observed **initiation profile** (what tended to be true when it started) and **termination profile** (what tended to be true when it stopped), with counts.
4. **Record what you could not segment.** Stretches where the behavior fits no motif are residual; report their fraction. A high residual means the opponent has structure you have not found, or the visibility was too poor to see it.

Expect 5–12 skills. If you find 30, you are naming execution variation as skills; if you find 2, your segmentation is too coarse to be predictive.

---

## 5. Annotate situations from the observer's perspective

For each opponent skill selection (each motif start), write a block:

**Header** — episode ID, tick, opponent ID, model level this observation informs.

**Visibility** — what we could observe of the opponent and their surroundings at this tick. If the trace has an observability flag, use it; otherwise state the assumption.

**Situation (as we saw it)** — our glossary's predicates that were true at this tick, from our observable state. Also the predicates about the *opponent's* state we could observe (their cooldowns if visible, their health, their position relative to allies).

**Affordances (theirs)** — which of the opponent's inferred skills were available to them at this moment, as best we can tell. This is required: without it, the selection tells you nothing about preference.

**Selected** — the skill they chose.

**Outcome for them** — what it produced, from their side. Needed to infer goals (Section 6).

**Unglossed** — any distinction that seems to have mattered to their choice that our glossary cannot name. Tag `[unglossed]` and describe.

You do not need every opponent action annotated. You need every *skill selection* annotated, because that is the unit of preference.

---

## 6. Infer preferences and goals

**Preferences.** For each situation cluster (group of annotated blocks with the same or similar predicate set), tabulate the opponent's skill choices against affordances. A preference statement is warranted when one skill is chosen over an available alternative at a rate that a baseline (population model, or uniform over affordances) would not produce. Write it in IR grammar with evidence:

```
O-07  WHEN self.hook_on_cooldown ∧ enemy.in_range      [situation from OUR observation]
      THEY PREFER advance_and_bait OVER hold
      FOR pressure                                       [inferred goal, hypothesis]
      CONFIDENCE 0.78   n=41   BASE RATE 0.35 (population)
      LEVEL individual   OPPONENT bot:pudge_rl_v2
      LAST OBSERVED ep1147.dp23   PREDICTIONS 31/38 correct on held-out
```

Every field is required. A preference with n < 8 is written but marked `provisional` and excluded from counter-strategy until it earns its count.

**Goals.** Infer from what the opponent's choices systematically trade off. If they repeatedly accept damage to secure position, position outranks preservation for them. Write goals as an ordering with the preference IDs that support it, and mark the whole goal section as hypothesis — goals are the least observable layer, and the easiest to overfit a story onto.

**Beliefs (theirs), optionally.** If the opponent's behavior is best explained by a wrong belief about *us* — they bait as if our hook is ready when it is not — record it as a belief-layer statement about them, with the observations that support it. This is a second-order model and it is where exploitation is richest and inference is weakest. Hold it to a higher count.

---

## 7. Detect adaptation, constraint, and deception

Three things masquerade as preference and must be separated out:

**Constraint.** They did X because nothing else was available, or because their own state forced it (low health, cooldowns). The affordance line handles most of this; where it doesn't, note the constraint and exclude the observation from preference counts.

**Adaptation.** The opponent changes in response to us. Detect by splitting observations into early and late within an episode, and across episodes chronologically, and testing whether the preference rate moved. A preference that holds early and disappears late is an adaptation finding: record both states and what of ours preceded the change. Weight recent observations more heavily in the in-episode model; do not let them overwrite the individual model without a count.

**Deception.** In environments where an agent can profit from being mismodeled — feints, baits, information games — the opponent may act to shape your model. Signs: a strong, cheap-to-observe tendency that, when exploited, turns out to be a trap; behavior that is consistent when we are watching and different when we are not (check against ground truth where you have it). Record suspected deception as a hypothesis with the exploitation attempt that would test it. Never build a counter-strategy on a tendency you have not tested against.

---

## 8. Validate

An opponent model earns trust only by prediction. Two tests, run in order:

**Held-out prediction.** Hold out at least 20% of episodes (chronologically last, so you also test drift). For each opponent skill selection in the held-out set, predict from the model — given the situation as we saw it and their affordances, what does the model say they choose? Report accuracy overall, per preference statement, and against the population baseline. A statement that does not beat baseline on held-out data is demoted to `provisional` regardless of its in-sample count.

**Proxy rollout.** Embed the opponent IR into a proxy policy — a simple controller that selects skills according to the model's preferences and executes them with generic skill implementations. Run the proxy in the seeded simulator against our policy in the held-out episodes' starting conditions. Compare the proxy's trajectory statistics (skill frequencies, position distributions, outcomes) to the real opponent's. Where the proxy diverges, the model is missing something; where it matches, the proxy qualifies as a **live opponent policy for counterfactual rollouts** — which is what the episode guide needs and could not get. Report the divergence and the threshold at which you consider the proxy usable.

A model that passes held-out prediction but not proxy rollout usually has correct preferences and wrong skill boundaries or initiation profiles. A model that passes neither should be rebuilt from Section 4.

---

## 9. Output format

One markdown document per opponent per model level (population, individual), with the in-episode model appended to the episode IR rather than stored separately.

1. **Header** — opponent ID, level, episode set (IDs, count, date range), our policy IR version, visibility summary (fraction of opponent ticks observable)
2. **Skills** — inferred skill list with initiation and termination profiles and counts; residual fraction
3. **Preferences** — every statement in the format of Section 6, sorted by confidence; provisional statements in a separate list
4. **Goals** — inferred ordering with supporting preference IDs; marked hypothesis
5. **Beliefs (theirs)** — second-order statements if any, with counts
6. **Adaptation and deception findings** — from Section 7
7. **Validation** — held-out accuracy overall and per statement; proxy rollout divergence; whether the proxy is usable
8. **Unglossed** — collected tags, deduplicated, with observation references
9. **Counter-strategy candidates** — for each tested preference with high confidence, the situation in which it is exploitable and the skill of ours that exploits it, written as a *proposed* rule for our strategy layer, not an adopted one
10. **Provenance** — episode sources, glossary version, this guide's version, date

Every statement has a stable ID (`O-NN` prefixed by opponent and level) so that our policy IR's belief-layer predicates (`enemy.tends_to_bait`) and strategy rules can cite it.

---

## 10. How this feeds the loop

- **Belief layer.** Each tested preference becomes a candidate predicate for our glossary — `enemy.tends_to_bait` — with the opponent IR statement as its definition and its confidence as the belief's prior. Our policy's belief layer then updates it in-episode.
- **Strategy layer.** Counter-strategy candidates enter the research loop as proposed edits with evidence attached. They go through the loop's normal protocol; the opponent model does not write rules directly.
- **Episode guide.** A validated proxy unblocks counterfactual rollouts. Record the proxy's divergence in every rollout that uses it, so verdicts inherit the proxy's uncertainty.
- **Population prior.** Individual models fold back into the population model on a schedule, weighted by count. The population model is what a new opponent gets on first contact.

---

## 11. Things that will go wrong

- **Story instead of statistic.** "They're aggressive" is not a statement. "Prefer advance over hold when our hook is down, 0.78, n=41, base 0.35" is. If you cannot write the second form, you do not have a finding.
- **Preference without affordance.** The single commonest error. Always ask what else they could have done.
- **Observing only when alive.** You see the opponent when your agent is near and alive. Their behavior when you are dead or far is unobserved, not absent. Report visibility fraction and do not generalize past it.
- **Teammate attribution.** In team games, the opponent's choice may respond to *our teammate*, not to us. Include teammate state in the situation block.
- **Overwriting the individual model with one episode.** A human who tried something new once is not a new player. In-episode observations update the in-episode model; they reach the individual model only through the count.
- **Building counter-strategy on an untested tendency.** A tendency that has never been exploited may be a bait. Test by exploitation in the simulator first, in play second, and record what happened.
- **Anthropomorphizing bots and mechanizing humans.** A scripted bot's "tendency" is a rule with noise; a human's rule is a tendency with reasons. The evidence format is the same; the confidence you assign to persistence should not be.
- **Ground truth leaking into the model.** If a preference is conditioned on something we could not observe, we cannot act on it. Ground truth scores the model; it never enters the model.
