# Confirmed-hit component: no_escape
Status: inconclusive

Setting critical_percent to0 removes emergency attack interruptions. If emergency movement caused lost pressure, wins/hits should recover while confirmed-hit timing remains valid.

Parent controller: confirmed_hit_kite, release2026.9.15.3. Exactv2 remains the
competitive reference. Only the named component changes. Previous controller
won12/40 versus v2 22/40; the broad controller failed. Closed levers reviewed.

Freeze before run:40 seed/seat cases from721000–721039 reused explicitly as
adaptive discovery; each new candidate runs against nine defaults. Reuse only
exactly matched, fully audited v2/default controls. Compare component outcomes
also against the previous controller's40 matching cases. This is not independent
confirmation. No partial stopping or retuning. Full40 new replay checks required.

FALSE prediction: pressure/wins do not recover, or survival worsens. Screen
qualifies only if wins>=22(v2) and18(default), deaths<=.85*134, basic hits>=.8*2321,
actual displacement in>=12 cases and every normal retreat follows a hit within
one tick. Apply the existing33 corrected regression checks. Any selected candidate
needs fresh independent confirmation and hosted fixed-incumbent N-episode batches.

Critique: observed target IDs are intent rather than certain future damage;
emergency removal may preserve attacks while allowing avoidable deaths. These
are post-failure exploratory interventions, so selection and reuse can overfit.
Report both probes; do not substitute reused cases for future confirmation.

Artifacts: tmp/gota-ir/kiting-ablations-20260915/no_escape/.

Result: 20/40wins vs priorcontroller12,v222; deaths136vsv2134, hits2403vsv22321. Screenpassed=False. No promotion.
