# Multiple replay-driven hypotheses, before competitive execution

The user explicitly authorizes testing many improvements and combinations at
once and submitting a better replacement for `aaron-gota-ir-waveguard-r4:v2`.
This campaign supersedes the experiment skill's one-hypothesis-at-a-time
workflow preference. It retains frozen inputs, complete outcomes and fresh
confirmation after candidate selection.

## Hypotheses and cells

The replay diagnosis found that short retreats spend most of their time turning,
that target switches do not resolve a friendly-tower waypoint trap, and that
critical-HP warnings are often brief. The resulting ten IR-compiled cells are:

1. Stable-destination retreat with separation feedback, any nearby threat.
2. The same restricted to observed attackers.
3. The first without explicit offensive spell attempts during movement.
4. Earlier damage/attacker escape without normal post-hit kiting.
5. Observed-attacker kiting plus earlier escape.
6. Preventive tower-clearance detours.
7. Ranger/Crossbow starting dagger instead of starting boots.
8. Any-threat kiting plus the starting weapon.
9. Tower detours plus the starting weapon.
10. Observed-attacker kiting, earlier escape, tower detours and starting weapon.

All candidates retain legal item purchasing. Equipment changes affect only
Ranger/Crossbow initial gear; other purchases and consumables remain the parent
behavior. IR contracts describe actual rule order, state, observations and
actions. Generated BASIC and reverse extraction must match before execution.

## Critique and differing predictions

- **Motion:** If the controller helps, movement/separation completion activates
  and survival improves without losing fort wins. If retreat merely abandons
  damage or objectives, wins or XP fall. A successful walk command alone does
  not count as competitive evidence.
- **Pressure:** Earlier escape may prevent deaths, or unnecessarily surrender
  fights. Compare the isolated pressure cell and its combination with kiting.
- **Tower clearance:** Preventive detours may avoid path traps, or oscillate
  and waste travel. Activation must be measured, and no engine-only waypoint
  intervention is allowed in a policy or evaluated game.
- **Weapon:** Added basic damage may improve last hits, or lost starting speed
  may worsen survival. Its interaction with kiting is explicitly tested.
- **Confounds:** One subject and nine default policies per game; all ten classes
  and both teams balanced. Match seed/seat/config across arms. Controls are the
  exact selected v2 and exact published default. Use published e127989 mechanics,
  not dirty root game sources. Event counts are not independent samples.
- **Selection:** Ten candidates increase selection noise. The screen ranks them;
  it cannot establish superiority. Only one fixed winner receives fresh
  confirmation. Underpowered or failed outcomes remain failures/inconclusive.

## Frozen decision rules

Authoritative counts, seeds, sources and rules are in
`tmp/gota-ir/motion-campaign-20260915/plan.json`, created before its first game.

- Screen:40 fresh balanced cases, seeds723000–723039, twelve arms total.
  Finish all480 games and complete replay audits. Shortlist candidates gaining
  at least2 wins over each control, with death rate per alive minute no more
  than110% of v2 and lifetime XP at least80%. Require actual mechanism activation
  and no post-hit retreat triggered without a verified hit. Choose by wins,
  then lower death rate, then XP, then name. This is discovery only.
- Confirmation:240 untouched cases, seeds724000–724239, one selected candidate
  and the two controls. Require>=5 percentage-point gain and exact paired
  one-sided p<.025 against EACH control, survival/XP guardrails, and no adverse
  class win flag at .05/10. No changing the candidate mid-confirmation.
- Hosted:only a local qualifier advances. Freeze current game and nine incumbent
  policy versions. One100-episode request per arm, independent platform seeds,
  rotated seats. Require>=10pp win gain and one-sided Fisher exact p<.05 versus
  v2, complete artifact inspection and survival review. Use a separate40-episode
  field guardrail before champion replacement. The previously missing hosted
  sample floor is replaced by this campaign-specific fixed design; it resolves
  only effects large enough for that sample and threshold.
- No optional stopping, omitted seeds, changed thresholds, or uninspected XP.
  Invalid runs are preserved and block advancement until exact-input recovery.
  Budget limits or compiler failures are implementation failures, not game losses.

The previous fixed10/32-tick kiting failures and the older radius-only/loadout
results remain recorded. None is reclassified as successful by this campaign.
