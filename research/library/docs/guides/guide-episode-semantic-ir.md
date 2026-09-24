# Guide: Producing a Semantic IR of an Episode

*For an autoresearcher agent. This guide tells you how to take a recorded game episode and produce a semantic account of it from a policy's perspective, in the same medium and vocabulary as the policy's own IR. The output is evidence: it is what the research loop reads to find where a policy went wrong and which layer to edit.*

---

## 1. What you are producing

An **episode IR** is a text document that narrates one episode as a sequence of **decision points**, each described in the policy's own terms: what it recognized, what it believed, what it wanted, which rules fired, which skill it chose, what happened. It is written in the vocabulary of the policy IR (its glossary, skills, and rules) so that every finding can attach to a specific IR block.

It is not a replay summary. It is not a commentary on what should have happened. It is the episode as the policy experienced it, followed by separately labeled judgments grounded in measurement.

Two rules govern everything below:

- **Record what the policy could see, not what was true.** The policy's beliefs are recorded as it held them. Ground truth is recorded separately and only where it is used to score a belief after the fact.
- **Narration is yours; judgment is not.** You write the account. Fidelity is checked mechanically, decision quality is measured by counterfactual rollout, and diagnosis follows a routing table. You propose what looks interesting; you do not declare what was right.

---

## 2. Inputs you need

Before starting, confirm you have all of these. If any is missing, stop and report.

1. **The policy IR** at the version that played the episode — glossary, skills, rules, goals. Record its version hash.
2. **The trace** — per-tick log containing the observable state the policy had access to, the policy's internal variables (belief estimates, skill-internal state), the active skill, the rules evaluated and which fired, and the action emitted. If the trace lacks rule-evaluation records, the fidelity judgment (Section 6) cannot be made; say so.
3. **Ground truth** — the full game state per tick, including what the policy could not observe. Used only for scoring beliefs and for counterfactual rollouts.
4. **Outcome data** — the episode result, and if the environment provides it, a per-tick or per-event win-probability estimate. If there is none, you will derive a coarse one (Section 7).
5. **A seeded simulator** that can be branched from any tick with the other agents' policies held fixed. Required for decision-quality judgments; without it, Section 7 produces candidates only, never verdicts.

---

## 3. Segment the episode into decision points

A decision point is any tick where the strategy layer made a choice. Concretely, one of:

- A skill was selected (including re-selection of the same skill after another terminated)
- A skill terminated, whether by its own termination condition or by preemption
- A rule with a different priority than the previously winning rule took over
- The policy's goal in force changed (rare; always record)

Ticks where the active skill simply continued executing are not decision points. They belong to the execution span of the preceding decision point.

Expect 20–80 decision points for a typical episode. Fewer than 10 means your segmentation is too coarse or the policy has too few skills to be interesting; more than 150 means you are recording execution as decisions. Report the count.

Assign each decision point a stable ID: `<episode_id>.dp<NN>`.

---

## 4. Annotate each decision point

For each decision point, write one block with these sections. Use the policy IR's exact predicate names, skill names, and rule IDs. Where the trace contains something the glossary has no word for, write it in plain language and tag it `[unglossed]` — these tags are findings.

**Header** — ID, tick, game clock, phase of the episode if the environment defines phases.

**Situation** — the predicates from the glossary that were true at this tick, per the trace. List all that were true, not only those the winning rule used. Affordances: which skills' initiation conditions were satisfied.

**Belief** — the policy's estimates of unobserved state and of other agents, with confidence, as recorded in the trace. Do not correct them here.

**Goal in force** — which goal the winning rule cites, and any goal-ordering the policy applied.

**Arbitration** — every rule whose conditions matched, in priority order, with the winner marked. If the trace shows a rule matched but the policy did not act as that rule prescribes, mark it `[fidelity?]` and continue; Section 6 resolves it.

**Selected** — the skill chosen, with the parameters it was given.

**Execution span** — the tick range the skill ran, how it terminated (own condition / preempted by which rule / episode ended), and a one-line plain-language description of what execution did.

**Consequence** — what changed in the observable state as a result, in the glossary's terms. Which beliefs were confirmed or falsified during this span, scored against ground truth (this is the one place ground truth enters the narration, and only to grade a belief the policy stated).

Write the block as structured prose under labeled lines, not as a table. It must read as an account, and a person who plays the game should be able to follow it without the trace.

---

## 5. Assemble the narrative

Order the blocks chronologically. Before the first block, add:

- **Episode header** — episode ID, environment and version, policy ID and IR version hash, teammates and opponents with their policy IDs, seed, outcome, duration.
- **Arc** — three to five sentences describing the shape of the episode in plain language: how it opened, where it turned, how it ended. This is the only free narrative in the document and it should make no judgments.

After the last block, add the judgment sections below. Keep them separate from the narration; a reader must be able to tell where the account ends and the assessment begins.

---

## 6. Judgment I — Fidelity

*Did the policy do what its IR says it does?*

For every decision point, check mechanically: given the recorded situation and beliefs, does the IR's arbitration rule (priority, specificity, recency, as the IR specifies) select the rule and skill the trace shows? Three outcomes:

- **Consistent** — the IR predicts what happened.
- **Inconsistent** — a different rule should have won, or the winning rule prescribes a different skill. Record which. This is an embedding fault surfacing in play; it may not appear in the enumerated table because the live situation was one the table did not cover.
- **Unresolvable** — the trace does not record enough to decide. Record what is missing.

Report the counts and list every inconsistency with its decision point ID. Do not interpret them here. Fidelity findings route to the embedder, not to the IR.

---

## 7. Judgment II — Decision quality

*Given what the policy believed and wanted, was the chosen skill the best available?*

This is the expensive judgment. You do not perform it at every decision point. Select candidates in this order, cheapest filter first:

1. **Outcome attribution.** Using win-probability data (or a coarse proxy you derive: material, position, objective control — state what you used), find the decision points immediately preceding the largest swings against the policy. Take the top N (default 5).
2. **Falsified beliefs.** Decision points where a belief with confidence above 0.6 was subsequently shown wrong, and the winning rule conditioned on that belief.
3. **Fidelity inconsistencies** from Section 6, since the policy did something other than what it should have — worth knowing whether the deviation helped or hurt.

For each candidate, run **counterfactual rollouts**: branch the seeded simulator at the decision point, force each *alternative skill whose initiation condition was satisfied* (from the Affordances line), and roll forward with all other agents' policies fixed and reacting. Use enough seeds per branch to report an interval (default 20). Compare the branch outcomes to the actual.

Record for each candidate:

```
dp: <id>
actual: <skill> → outcome metric <value>
alternatives:
  <skill_A> → <value> ± <ci> (n=<seeds>)
  <skill_B> → <value> ± <ci> (n=<seeds>)
verdict: actual was [best | within interval of best | dominated by <skill>]
```

A verdict of "dominated" means a decision-quality finding. A verdict of "best" at a decision point that preceded a large negative swing is *also* a finding: the loss was not caused by a choice, so look at perception or execution.

Never issue a verdict without rollouts. If the simulator is unavailable, the section lists candidates with the reason each was selected and stops.

---

## 8. Judgment III — Diagnosis

*For every finding, which layer does it implicate?*

Take each decision-quality finding and each fidelity inconsistency and route it:

| What you observed | Layer implicated |
|---|---|
| Right situation, right belief, dominated skill choice | 5 — strategy: the rule preferred the wrong skill here |
| Right situation, wrong belief, choice was best given the belief | 2 — belief: the inference was miscalibrated |
| A predicate that would have distinguished this case does not exist in the glossary | 1 — situation: ontology gap; write the missing predicate in plain language |
| Situation was correctly recognized but no rule matched, and the fallthrough behavior was poor | 5 — strategy: coverage gap |
| Right skill selected, poor result from execution | 6 — execution: the skill's internals underperformed; do not propose an IR edit |
| Skill did not terminate when its interface says it should | 4 — skill: interface fault |
| Policy consistently pursued something no goal names | 3 — goal: flag for human review; do not propose an edit |
| IR predicted a different rule than fired | Embedding fault — route to the embedder, not to any layer |

Each routed finding becomes a **proposed evidence update**: which IR block (rule, skill, predicate, goal) it bears on, what it says about that block, and the decision point IDs supporting it. Write these as proposals. They are attached to the IR by the research loop after review, not by you.

---

## 9. Output format

One markdown document per episode, in this order:

1. Episode header
2. Arc
3. Decision-point blocks (chronological)
4. Judgment I — Fidelity (counts, inconsistency list)
5. Judgment II — Decision quality (candidates, rollouts, verdicts)
6. Judgment III — Diagnosis (routed findings, proposed evidence updates)
7. Unglossed terms — every `[unglossed]` tag collected, deduplicated, with the decision points where each appeared
8. Provenance — IR version, trace source, simulator version, seeds used, this guide's version

Every block and every finding has a stable ID. Nothing in sections 1–3 asserts what should have happened. Nothing in sections 4–6 is asserted without the mechanical check, the rollout, or the routing table that grounds it.

---

## 10. Across episodes

A single episode IR is a data point. The research loop reads many. To make that possible:

- Use identical block structure across episodes so findings can be aggregated by rule ID, skill, predicate, and layer.
- When the same rule is dominated at decision points across several episodes under similar situations, say so in that episode's diagnosis by referencing the prior episode IDs — but do not aggregate here; the loop does that.
- Unglossed terms that recur across episodes are the strongest signal for ontology growth. Keep the tags exact so they can be counted.

---

## 11. When the policy does not fit the model

The sections above assume a policy where one rule wins per tick and selects one skill, a glossary that covers the situations the policy distinguishes, a trace with internal state, and a simulator with live opponents. Real policies violate these. Each violation is a finding, not a blocker; here is how to proceed.

**Several rules act per tick.** Determine from the trace whether the rules write to disjoint outputs or overwrite one another.

- *Disjoint* (one rule drives movement, another targeting, another release): the policy has N control channels, each with its own one-winner arbitration. A decision point is a tick where any channel's winner changes. The Arbitration block gets one line per channel. Fidelity (Section 6) is checked per channel.
- *Overlapping* (later rules overwrite earlier ones): execution order is the priority — last writer wins. Record the order as the arbitration rule and check fidelity against it.

In both cases, record which structure the policy has as a structural finding in Section 8. The IR's strategy layer must model the same structure, and the embedder needs to know it.

**The glossary is too thin.** If the policy visibly distinguishes situations the glossary cannot name, do not stop and do not substitute. Tag every such distinction `[unglossed]` and describe it in plain language. On a first pass over a policy with a thin glossary, the collected unglossed list (Section 9, item 7) is the primary output — it is the glossary extension, with evidence. Proceed with the rest of the document as far as the vocabulary allows.

**Situation and strategy are entangled in the code.** If the routine that computes predicates also makes decisions (observation code that decides to defend, patrol, or release), layers 1 and 5 are fused in the implementation. Record this as a structural finding. For annotation purposes, treat the decision the fused routine makes as a strategy-layer choice and the inputs it used as unglossed predicates. The lift should split them; you should not.

**The trace is a reconstruction.** If the original policy logged too little and a reconstruction is used in its place, the reconstruction must be shown behaviorally equivalent — matching emitted commands and state hashes over the full episode set — and the document must be labeled *reconstructed* in the header and in every judgment section. State the caveat explicitly: the reconstruction reproduces the original's outputs, so its internal variables (beliefs, rule evaluations) are the reconstruction's own. Fidelity judgments compare reconstruction to IR, not original to IR. Behavior that is output-equivalent but internally different is invisible to this document.

**No live opponent policies for counterfactuals.** Section 7 already stops at candidates. Two partial unblocks, in order of preference:

1. If reconstructions of the *opponent* policies exist and meet the same equivalence bar, they qualify as live policies for rollouts.
2. Short-horizon frozen-world rollouts — opponents replay their recorded actions — may be used as a weak triage estimate only where the horizon is short enough that opponent reaction is negligible. Label every such result `frozen-world, horizon=<ticks>`. It ranks candidates; it is never a verdict.

---

## 12. Things that will go wrong

- **Hindsight leaking into narration.** The commonest failure. If a Belief line says "believed the hook was ready (it was not)," you have leaked. The parenthetical belongs in Consequence, as a belief score, not in Belief.
- **Judging by reading.** You will see a decision point and know what you would have done. That is a candidate for Section 7, not a verdict. Write it as a candidate with its reason.
- **Recording ticks as decisions.** If two consecutive blocks have the same skill, same rule, and no termination between them, they are one decision point.
- **Counterfactuals against a frozen world.** Replaying the other agents' recorded actions instead of running their policies produces branches where opponents don't react. State explicitly that other agents' policies were live.
- **Silent glossary substitution.** If the trace shows a condition the glossary doesn't name, do not pick the nearest glossary term. Tag it unglossed. Nearest-term substitution hides exactly the ontology gaps this document exists to find.
- **Summarizing long spans.** A skill that ran for 400 ticks gets one execution-span line. Do not expand it into a narrative; if something notable happened mid-span that didn't produce a decision point, it is either a missing decision point (check segmentation) or an execution detail (record in one clause).
