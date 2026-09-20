"""Publish native Python IR dictionaries and their counted Markdown/evidence views."""
import argparse,datetime,gzip,hashlib,json,pprint,shutil,sys
from collections import Counter
from pathlib import Path
from semantics import PARAMETERS,SKILLS,context
from guide import publish_guide
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'examples/gods_of_the_arena/players/ir'))
from opponent_ir import validate

DESCRIPTIONS={
 'target_hero':'Visible target identifies a living hostile hero; pursuit/retained target, not proof of an attack or kill.',
 'target_creep':'Visible target identifies a living hostile footman; pursuit/retained target, not proof of farming or last hits.',
 'target_structure':'Visible target identifies a positive-HP exposed hostile tower, barracks or god; not proof of damage.',
 'advance':'Without a valid visible target, velocity points toward our god (radial cosine >0.35). Relative geometry, not inferred destination.',
 'withdraw':'Without a valid visible target, velocity points away from our god (radial cosine <-0.35). Not proof of retreat to safety.',
 'lateral':'Without a valid visible target, velocity is neither advancing nor withdrawing by the radial thresholds.',
 'hold':'Without a valid visible target, speed <1000 world units/tick. Can include turning, collision or hidden target; voluntary waiting unproven.'}
GOAL_BY_SKILL={'target_hero':'hero_pressure','target_creep':'creep_contact','target_structure':'structure_pressure','advance':'territory_pressure','withdraw':'preservation','lateral':'reposition','hold':'unresolved'}
GOALS={
 'hero_pressure':'Hypothesis: hero contact outranks creep contact in the counted contexts. No inference of kill intent or willingness to sacrifice structures.',
 'creep_contact':'Hypothesis: maintain creep contact. XP, gold and last-hit optimization are not observed.',
 'structure_pressure':'Hypothesis: pressure exposed structures. Target selection is weaker evidence than realized damage.',
 'territory_pressure':'Hypothesis: gain proximity to our god. Intended route/end point remains unknown.',
 'preservation':'Hypothesis: create distance at low absolute HP; geometry alone does not establish safety-seeking.',
 'reposition':'Hypothesis: lateral relocation; tactical purpose unresolved.',
 'unresolved':'Goal unknown: stationary motion alone does not establish voluntary holding.'}

def pct(x):return 'unscored' if x is None else f'{100*x:.1f}%'
def when(key):
 _,mask,_,low=key.split('_');mask=int(mask)
 present=[name for bit,name in [(1,'our hero'),(2,'our creep'),(4,'our exposed structure')] if mask&bit]
 absent=[name for bit,name in [(1,'hero'),(2,'creep'),(4,'exposed structure')] if not mask&bit]
 exclusions=('; no nearby '+ '/'.join(absent)) if absent else ''
 return f"nearby={' + '.join(present) or 'none'}{exclusions}; visible HP {'≤' if low=='1' else '>'}100"

def make_model(report,plan,level,population_observations=None):
 individual=level=='individual';pred=report['models']['train' if individual else 'population'];prefix='Jordan268_I' if individual else 'GotaField20260919_P'
 claims={};rules=[];predicates={}
 if individual:preferences=report['preferences']
 else:
  preferences=[]
  for key,counts in pred['contexts'].items():
   chosen=max(counts,key=lambda s:(counts[s],s));context_rows=[r for r in population_observations if r['preference_eligible'] and context(r['situation'])==key]
   available=Counter(skill for r in context_rows for skill in r['affordances'] if skill!=chosen)
   other=max(available,key=lambda skill:(counts.get(skill,0),available[skill],skill))
   pairs=[r for r in context_rows if chosen in r['affordances'] and other in r['affordances']];n=len(pairs);selected_count=sum(r['selected']==chosen for r in pairs)
   dates={r['id']:r['created_at'] for r in plan['episodes']};last=max(context_rows,key=lambda r:(dates[r['episode']],r['tick']))['id'];mask=int(key.split('_')[1]);low=int(key.split('_')[-1])
   preferences.append({'id':f'{prefix}_O{2*mask+low+1:02d}','when':key,'skill':chosen,'over':other,'n':n,'chosen_count':selected_count,'confidence':(selected_count+1)/(n+2),'confidence_meaning':'Laplace-smoothed descriptive frequency; population generalization untested',
    'base_rate':{'source':'Uniform over available skills in paired-affordance observations; population holdout absent','rate':sum(1/len(r['affordances']) for r in pairs)/n if n else None,'n':n},'status':'provisional','level':level,'opponent':'sampled_field_20260919','last_observed':last,
    'predictions':{'n':0,'correct':0,'accuracy':None,'population_accuracy':None},'counterstrategy_status':'prior_only'})
 for pref in preferences:
  pid=pref['id'];key=pref['when'];predicates[key]=when(key)
  claims[pid]={'claim':f"WHEN {when(key)} THEY PREFER {pref['skill']} OVER {pref['over']} FOR {GOAL_BY_SKILL[pref['skill']]} (hypothesis).",
   'status':'supported' if pref['status']=='supported' else 'requires_review','evidence':[pref]}
  rules.append({'id':pid,'when':key,'skill':pref['skill'],'for':[GOAL_BY_SKILL[pref['skill']]]})
 model={'schema':'gota-semantic-opponent/1','id':'jordan_v268_observer_model' if individual else 'gota_field_20260919_observer_prior',
  'situation':{'grounded':{'observation':'Single owned hero slot 0/5, exact predecision host-visible snapshots. Predictor uses tick t-1; inferred motif begins at t and must last at least 6 ticks (0.25s at 24 Hz).',
    'structure_alive':'For structures, objectAlive means exposed; positive HP means standing. A zero visible target means none OR hidden.',
    'predicates':predicates,'glossary_extensions':DESCRIPTIONS},'notes':'All motifs are [inferred-skill]. Original attack is defense_cadence; it is not equivalent to a visible target. Concurrent movement qualifiers are retained inside targeting motifs. This describes observed behavior, not Jordan source rules.'},
  'belief':{'grounded':{'level':level,'opponent_version':plan['target_version'] if individual else 'sampled_field_20260919',
    'our_policy':{'id':'gota_relh154_legacy','schema':'gota-semantic-policy/1','canonical_sha256':'8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37','basic_sha256':'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'},
    'memory':'No private opponent memory inferred. Individual estimates are frozen; no persistent in-episode updates are asserted.',
    'uncertainty':'Partial visibility, correlated trajectories, estimated affordances, and retrospective event boundaries. Absence from view is not absence from game.',
    'predictor':pred,'skills':report['skills'] if individual else report['population_skills'],'validation':report['heldout'] if individual else {'population_generalization':'not independently validated','baseline_on_jordan':report['heldout']['population_accuracy']},
    'proxy':report['proxy'],'observability':report['observability']['all_jordan' if individual else 'population']},'claims':claims},
  'goal':{key:{'preference':text,'provenance':'interpretation' if key!='unresolved' else 'unknown'} for key,text in GOALS.items()},
  'skill':{s:{'operator':'observed_'+s,'parameters':{'minimum_segment_ticks':6}} for s in SKILLS},
  'strategy':rules,'execution':{'binding':'gota-observer-model/1','game_version':'2026.9.16.5','language':'Python'},
  'update':{'revision':1,'parent':None,'change':{'origin':'observable_replay_inference','level':level,'parameters':PARAMETERS,'frozen_model_sha256':report['model_freeze_sha256'],
    'semantics':'Rule records share primary id/when/skill/for layout; they express forecasts, not an inferred execution order or a claim that only one source rule fires. predictor distribution governs context backoff and unavailable-skill masking.'},
   'needs_review':['Unvalidated rollout proxy','No exploitation experiment','Unknown abilities and cooldowns','Class/side/phase confounding','22% visibility and few distinct heldout trajectories'],
   'evidence':[{'artifact':'docs/opponents/jordan-v268/evidence.json','guide':'guide-opponent-model-ir.md','model_level':level}]}}
 return validate(model)

def write_python(path,model):
 path.write_text('"""Inferred opponent IR in the primary seven-layer Python dictionary layout.\n\nGenerated from frozen observer evidence; no private opponent code or VM commands.\nUse opponent_ir.validate / predict; this is not a BASIC or rollout policy.\n"""\n\nMODEL = '+pprint.pformat(model,width=108,sort_dicts=False)+'\n')

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory.resolve();report=json.loads((d/'evaluation.json').read_text());plan=json.loads((d/'study-plan.json').read_text());out=ROOT/'docs/opponents/jordan-v268';out.mkdir(parents=True,exist_ok=True);modeldir=ROOT/'examples/gods_of_the_arena/players/ir/opponents';modeldir.mkdir(exist_ok=True)
 population_observations=[]
 for row in plan['episodes']:
  if row['split']=='population':
   with gzip.open(d/'artifacts'/row['id']/'observations.jsonl.gz','rt') as f:population_observations.extend(json.loads(line) for line in f)
 population_skills={}
 for skill in SKILLS:
  rows=[r for r in population_observations if r['selected']==skill]
  population_skills[skill]={'n':len(rows),'episodes':len({r['episode'] for r in rows}),'ticks':sum(r['duration_ticks'] for r in rows),'initiation_contexts':dict(Counter(context(r['situation']) for r in rows)),'termination':dict(Counter(r['termination'] for r in rows)),'left_censored':sum(r['predictor_tick'] is None for r in rows),'prediction':{'n':0,'accuracy':None},'confidence':'Motif definition only; population prediction unvalidated'}
 report['population_skills']=population_skills
 model=make_model(report,plan,'individual');population=make_model(report,plan,'population',population_observations);write_python(modeldir/'jordan_v268.py',model);write_python(modeldir/'population_20260919.py',population)
 (out/'evidence.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(d/'study-plan.json',out/'study-plan.json');shutil.copy2(d/'model-freeze.json',out/'model-freeze.json');shutil.copy2(d/'heldout-predictions.jsonl.gz',out/'heldout-predictions.jsonl.gz')
 publish_guide(d, out)
 for name,source in [('observer-policy.ir.json',ROOT/'docs/episodes/ereq_0806a449-3d7c-4160-868a-3e157634ebbc/policy.ir.json'),('observer-policy.bas',ROOT/'docs/episodes/ereq_0806a449-3d7c-4160-868a-3e157634ebbc/policy.bas')]:shutil.copy2(source,out/name)
 allobs=[];popobs=[]
 for row in plan['episodes']:
  with gzip.open(d/'artifacts'/row['id']/'observations.jsonl.gz','rt') as f:rows=[json.loads(l) for l in f]
  (popobs if row['split']=='population' else allobs).extend(rows)
 for name,rows in [('observations.jsonl.gz',allobs),('population-observations.jsonl.gz',popobs)]:
  with gzip.open(out/name,'wt') as f:
   for row in rows:f.write(json.dumps(row,separators=(',',':'))+'\n')
 examples=[]
 for pref in report['preferences']:
  if pref['status']=='supported':examples.extend([r for r in allobs if r['id']==pref['examples'][0]])
 (out/'example-observations.json').write_text(json.dumps(examples,indent=2)+'\n')
 v=report['observability']['all_jordan'];h=report['heldout'];dt=report['observability']['distinct_train'];ho=report['observability']['heldout'];supported=[p for p in report['preferences'] if p['status']=='supported'];provisional=[p for p in report['preferences'] if p['status']!='supported']
 lines=['# Jordan v268 — individual opponent IR','',
  f"Native Python artifact: [`jordan_v268.py`](../../../examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py). Same seven-layer dictionaries and `id / when / skill / for` rule records as the primary IR; inference binding `gota-observer-model/1`. No executable equivalence to Jordan is claimed.",'',
  f"**Initial result:** {pct(h['accuracy'])} heldout motif-choice accuracy versus {pct(h['population_accuracy'])} population and {pct(h['robustness_baselines']['class']['accuracy'])} class-conditioned population. Three preferences clear the stated heldout baseline gate. No strategy edit or proxy is qualified for adoption.",'',
  '![Heldout validation](validation.png)','', '## 1. Header','',
  '- **Identity:** `Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v268`; version UUID `207ffaf9-0d1e-4d92-a15d-4352f1bddec2`. Individual model; no pooling across Jordan versions.',
  '- **Snapshot:** rank 1 in the fetched league leaderboard, MMR 1802.17. League `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; completed rounds 483–502.',
  '- **Episodes:** 20 Jordan games, 2026-09-19 17:17:58 to 2026-09-20 03:27:04 UTC (September 19 local). All 20 were Jordan wins. Outcomes did not select the sample.',
  '- **Split:** earliest 16 training / latest 4 heldout, frozen before behavior inspection. Training reduces to 11 distinct visible trajectories. Heldout has 3 distinct trajectories; two episodes exactly repeat a training trajectory. The remaining two episodes are new observable trajectories, not evidence of broad seed diversity.',
  '- **Observer:** one real owned policy instance, slot 0 or 5. Both owned deployments use `gota_relh154_legacy`, `gota-semantic-policy/1`; [frozen policy](observer-policy.ir.json). Canonical SHA `8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37`.',
  f"- **Visibility:** {v['visible_living_opponent_ticks']:,}/{v['living_opponent_ticks']:,} living opponent hero-ticks visible ({pct(v['fraction'])}); {pct(v['all_scheduled_hero_tick_fraction'])} of all five scheduled hero-ticks. Observer dead on {pct(v['observer_dead_fraction'])} of ticks. No enemy trajectories are filled through these gaps.",'',
  '## 2. Skills','',
  'All seven are `[inferred-skill]` motifs, not recovered source functions. The existing `attack` skill executes `defense_cadence`, so it is deliberately not equated with an observed target. Targeting and movement can coexist: primary motif records a visible target first and retains a concurrent movement histogram. These categories do not assert single-rule execution.',
  '', '| Skill | Definition | Distinct-train starts | Median ticks | Heldout recall |','|---|---|---:|---:|---:|']
 for skill,s in report['skills'].items():lines.append(f"| `{skill}` | {DESCRIPTIONS[skill]} | {s['n']} | {s['median_duration_ticks']} | {pct(s['prediction']['recall'])} |")
 lines+=['',f"Residual: {pct(v['residual_fraction'])} of visible opponent hero-ticks lie in runs shorter than 6 ticks; {pct(dt['residual_fraction'])} on distinct training trajectories. Hidden ticks are outside this denominator. Sustained motions are fully classified, so a low residual does not establish causal completeness.",'',
  'Initiation and termination profiles below use all sustained starts in distinct training trajectories, including explicitly left-censored first appearances. Preference counts exclude those appearances. Counts and per-skill prediction precision/recall are in [evidence.json](evidence.json).','']
 for skill,s in report['skills'].items():
  common=Counter(s['initiation_contexts']).most_common(2);lines.append(f"- `{skill}`: initiation "+'; '.join(f"`{key}` n={n}" for key,n in common)+f"; left-censored n={s['left_censored']}. Termination "+', '.join(f"{key} n={n}" for key,n in s['termination'].items())+'.')
 lines+=['','## 3. Preferences','',
  'Nearby means ≤12 integer tiles in the **previous** visible snapshot. HP≤100 is an absolute visible threshold, not percent health. Hostile means hostile to Jordan. Target opportunity requires positive HP and exposed/alive status; movement alternatives check two terrain points. These are observable affordance estimates, not proof of Jordan sight, dynamic route success, or private cooldown readiness.',
  '', 'Every n below counts distinct-training motif starts where both named alternatives were estimated available. Confidence is a Laplace-smoothed selection rate, **not** certainty about source code or intent. Base rate is the same-context, same-affordance population frequency. Heldout predicts from t−1; the new target/motion at t is never a feature. Source rules and ability choices remain unknown.', '', '### Supported relative predictions','']
 def pref_block(p):
  pr=p['predictions'];b=p['base_rate'];n=p['n'];goal=GOAL_BY_SKILL[p['skill']]
  return ['```text',f"{p['id']}  [{p['status']}]",f"WHEN {when(p['when'])}",f"THEY PREFER {p['skill']} OVER {p['over']}",f"FOR {goal} [hypothesis]",f"CONFIDENCE {p['confidence']:.3f}  n={n}  CHOSEN {p['chosen_count']}/{n}  EPISODES {p['supporting_episodes']}",f"BASE RATE {pct(b['rate'])} (population n={b['n']})",f"LEVEL individual  OPPONENT Jordan:v268",f"LAST OBSERVED {p['last_observed']} (training evidence)",f"PREDICTIONS {pr['correct']}/{pr['n']} ({pct(pr['accuracy'])}); population {pr['population_correct']}/{pr['n']} ({pct(pr['population_accuracy'])})",'```','']
 for p in sorted(supported,key=lambda p:p['confidence'],reverse=True):lines+=pref_block(p)
 lines+=['`O15` also beats the class-conditioned population baseline: 155/238 versus 98/238. `O07` is a weaker 63/165 versus 34/165. `O08` has only ten heldout cases and geometrically defined withdrawal; treat it as low confidence despite clearing the nominal gate. These forecasts do not establish that a counter-strategy succeeds.','', '### Provisional','', 'n<8, no heldout cases, failure to beat baseline, or ambiguous stationary motion prevents promotion. Common behavior shared with the field can be predictable without being an individual advantage.','']
 for p in sorted(provisional,key=lambda p:p['confidence'],reverse=True):lines+=pref_block(p)
 lines+=['## 4. Goals — hypotheses','',
  '- `Jordan268_I_G01`: **hero contact > creep contact**, only in O07/O15 contexts. Support: O07 n=553 and O15 n=677 distinct-training opportunities; heldout 63/165 and 155/238. Confidence inherits those probabilities (0.396 and 0.532); this is a target-choice ordering, not a claim of kill intent or global priority.',
  '- `Jordan268_I_G02`: **distance creation may outrank creep contact when HP≤100**, O08 n=75, confidence 0.429, heldout 4/10. Preservation is an interpretation; moving away from our god does not prove reaching safety.',
  '- No observed preference establishes an ordering among winning, XP, equipment, team sacrifice or deception. Corresponding goal confidence is unestimated (n=0, predictions=0); no narrative is supplied.','',
  '## 5. Beliefs (theirs)','',
  '`Jordan268_I_B01`: second-order opponent belief model withheld. n=0 distinguishable belief tests; confidence unestimated; predictions=0. Visible targets and inventory do not expose private memory, intended skill cooldowns or beliefs about our capabilities.','',
  '## 6. Adaptation, constraints and deception','',
  'The same preference contexts were split at each episode midpoint and chronologically across distinct training episodes. Counts below are descriptive; class, combat stage, position and remaining structures can still confound them. No causal reaction-to-us claim is supported.','',
  '| Preference | Early → late within episode | Earlier → later episodes | Our visible units target Jordan → do not |','|---|---|---|---|']
 for item in report['adaptation']:
  if item['preference'] not in {p['id'] for p in supported}:continue
  fmt=lambda k:f"{item[k]['selected']}/{item[k]['n']} ({pct(item[k]['rate'])})"
  lines.append(f"| {item['preference']} | {fmt('within_early')} → {fmt('within_late')} | {fmt('chronological_early')} → {fmt('chronological_late')} | {fmt('our_pressure_present')} → {fmt('our_pressure_absent')} |")
 lines+=['',
  '`Jordan268_I_A01`: hero-target rates rise later within these games but do not show a corresponding increase across chronological episodes. Count/prediction support is O07/O15 above; confidence in **causal adaptation** is unestimated. An in-episode coach should retain recent conditional counts without overwriting the frozen individual prior. No in-episode policy was installed.',
  '',f"Constraints: {v['exclusions']['left_censored']} sustained starts are left-censored; {v['exclusions']['selected_skill_not_established_by_prior_affordances']} lack the selected pre-tick affordance. Both groups are excluded from preferences. Stationary motifs remain ambiguous; spell/cooldown-dependent choices and purchase intentions are outside this model.",
  '', '`Jordan268_I_D01`: no deception claim. Exploitation attempts n=0, confidence unestimated, prediction record=0. Hidden behavior was not inspected to manufacture a contrast. Test a proposed response against the exact real policy before interpreting a tendency as exploitable.','',
  '## 7. Validation','',
  f"All 41 original replays consumed every action and matched every recorded state hash: {sum(json.loads((d/'artifacts'/r['id']/'observer-validation.json').read_text())['ticks'] for r in plan['episodes']):,} verified ticks. This validates reconstruction; it does not validate inferred motives.",
  '',f"Heldout: {ho['segments']} sustained starts; {ho['eligible']} eligible predictions; {ho['exclusions']['left_censored']} first-appearance starts and {ho['exclusions']['selected_skill_not_established_by_prior_affordances']} missing-affordance starts excluded. This is **choice prediction conditional on retrospective boundaries**, not prediction of boundary timing or every game tick.",'',
  '| Predictor | Correct / eligible | Accuracy |','|---|---:|---:|',f"| Jordan individual | {h['correct']}/{h['n']} | {pct(h['accuracy'])} |",f"| Population, same situation | {h['population_correct']}/{h['n']} | {pct(h['population_accuracy'])} |",f"| Population + visible class | {h['robustness_baselines']['class']['correct']}/{h['n']} | {pct(h['robustness_baselines']['class']['accuracy'])} |",f"| Population + observer side | {h['robustness_baselines']['side']['correct']}/{h['n']} | {pct(h['robustness_baselines']['side']['accuracy'])} |",f"| Previous motif persists | — | {pct(h['persistence_accuracy'])} |",f"| Uniform available motifs | expected | {pct(h['uniform_expected_accuracy'])} |",'',
  f"On the two heldout trajectories not exactly present in training: {h['novel_trajectories']['correct']}/{h['novel_trajectories']['n']} ({pct(h['novel_trajectories']['accuracy'])}) versus population {h['novel_trajectories']['population_correct']}/{h['novel_trajectories']['n']} ({pct(h['novel_trajectories']['population_accuracy'])}). Differences between these trajectories may be small; exact-hash novelty is not statistical independence.",
  '', 'A descriptive bootstrap over the three distinct heldout trajectories gives +8.2 to +11.6 percentage points versus the context population baseline. Three clusters are too few to establish broad league generalization. Per-episode and per-side results, statement records and raw predictions are preserved.',
  '', '**Proxy:** unusable; 0 rollouts, divergence unmeasured. The Python IR is a functioning motif predictor, not an action controller. A future proxy must implement generic skills, predict onset timing, and test heldout starts before counterfactual use. Proposed gates: skill-frequency TV≤0.10, spatial-bin TV≤0.15, absolute win-rate gap≤0.10 on a larger novel-seed, both-side suite; none has been tested.','',
  '## 8. Unglossed','',
  '| Proposed term | Why it is needed | Observation reference |','|---|---|---|']
 for term,explain in [('estimated_opponent_affordances','Separate visible opportunities from proven opponent execution capability.'),('visible_target_not_attack','Preserve a retained/chased target without inventing damage.'),('concurrent_target_and_motion','Retain simultaneous targeting and movement; do not imply one source rule per tick.'),('absolute_low_hp','Use exposed absolute HP; enemy max HP is not a host field.'),('observer_relative_advance','Radial movement relative to our known god, not a guessed opponent destination.')]:lines.append(f"| `[unglossed] {term}` | {explain} | `{examples[0]['id']}` |")
 lines+=['', 'These tags occur on every annotated sustained start (Jordan n=8,919); their definitions are measurement conventions, not hidden-policy hypotheses. Extensions remain local to this opponent binding, not silently adopted primary predicates.','',
  '## 9. Counter-strategy candidates and coach handoff','',
  'All candidates below are **proposed experiments**. Exploitation tests n=0; no win-benefit confidence is assigned. No source rule or league policy was changed.','',
  '```text',
  'Jordan268_I_C01  WHEN O15 context AND a visible Jordan hero targets our defender',
  'PROPOSE preserve paired defense assignment while a separately assigned unit continues structure pressure',
  'OUR SKILLS observe / attack / fallback; edit would target R1 assignment and R4 routing',
  'EVIDENCE O15: 155/238 heldout vs class-conditioned population 98/238',
  'TEST exact Jordan v268, matched fresh seeds, both sides; track structure damage, wins, defender deaths',
  'STATUS proposed_only; bait/deception risk untested; not eligible for adoption',
  '',
  'Jordan268_I_C02  WHEN O07 context AND a creep wave and hero are both viable targets',
  'PROPOSE test a defender separation that preserves wave progress while absorbing hero targeting',
  'OUR SKILLS observe / attack / fallback; preserve teammate attribution in the observation',
  'EVIDENCE O07: 63/165 heldout; weaker prediction, so run as a diagnostic arm',
  'STATUS proposed_only; exploitation tests=0',
  '```','',
  'Coach improvements: preserve exact opponent-version identity; make affordability/visibility a required field; keep skill onset and execution outcome separate; reject rules supported only by repeated trajectories; require a heldout baseline lift before adding a belief; retain provisional and disconfirmed statements rather than erasing them. Autoresearcher should first run C01 against the real policy, not this unqualified proxy.','',
  '## 10. Provenance and reproduction','',
  '- Guide snapshot: [guide-opponent-model-ir.md](guide-opponent-model-ir.md); SHA-256 in manifest.',
  '- [Frozen selection](study-plan.json), [model freeze](model-freeze.json), [counted evaluation](evidence.json), [every Jordan motif start](observations.jsonl.gz), [heldout forecasts](heldout-predictions.jsonl.gz), [readable example blocks](example-observations.json).',
  '- [Python compatibility proof](python-compatibility.json): all 1,466 frozen forecasts reproduced; proposed belief entries pass the primary validator and leave its exact compiled BASIC unchanged. The executable compiler rejects the observational model, preventing accidental use as a rollout controller.',
  '- [Reusable instrument](../../../games/gods_of_the_arena/instruments/opponent_ir/README.md); exact game `2026.9.16.5`, source `f2ab9598d8f8001b6beae3e66404e341770c803f`. Host target visibility filtering replicated; hidden commands used only to reconstruct the simulator. Training trace contains no hidden target, enemy cooldown, enemy max HP, gold, route intent or VM state.',
  '- Population prior: [population.ir.md](population.ir.md), 21 earlier games selected by opponent version and side without using scores. Field composition is documented below; this is a sampled prior, not the entire league.',
  '- Raw tapes, predecision views and hash proofs remain under `tmp/gota-ir/opponent-jordan-v268-20260919/artifacts/`. Downloaded via authenticated GETs only; no uploads, XP creation, or champion changes.',
  '- Schematic inspection preceded statistical extraction. The replay-inspection game binding was missing; the native version-matched decoder supplied exact view reconstruction and all-tick hash checks.',
  '', '| Split | Created UTC | Observer slot | Episode |','|---|---|---:|---|']
 for row in plan['episodes']:
  if row['split']=='population':continue
  url='https://softmax.com/observatory/v2?tab=overview&detail=episode-request:'+row['id'];lines.append(f"| {row['split']} | {row['created_at']} | {row['observer_slot']} | [{row['id']}]({url}) |")
 (out/'opponent.ir.md').write_text('\n'.join(lines)+'\n')
 # Population report keeps its lack of independent population validation explicit.
 pv=report['observability']['population'];poprows=[r for r in plan['episodes'] if r['split']=='population'];pops=Counter(r['opponent_label'] for r in poprows)
 pl=['# Sampled field — population opponent IR','',
  'Native Python prior: [`population_20260919.py`](../../../examples/gods_of_the_arena/players/ir/opponents/population_20260919.py). This prior supports the Jordan comparison; it is not a validated league-wide strategy.','',
  '## 1. Header','',f"Level population. {len(poprows)} games, {len(pops)} policy versions, all before Jordan heldout cutoff. One earliest eligible episode per opponent-version × our observer side. Our policy is the same frozen relh154 IR. {pv['visible_living_opponent_ticks']:,}/{pv['living_opponent_ticks']:,} living opponent hero-ticks visible ({pct(pv['fraction'])}). Exact IDs and dates: [study-plan.json](study-plan.json).",'',
  '## 2. Skills','',f"Same seven observation motifs, definitions and local estimated affordances as the individual model. {pv['segments']} sustained starts, {pv['eligible']} eligible choices; residual {pct(pv['residual_fraction'])}. Population segmentation is recorded per episode; complete blocks are [population-observations.jsonl.gz](population-observations.jsonl.gz).",'',
  '## 3. Preferences','', 'The Python prior retains count-backed context distributions with stable `GotaField20260919_P_Oxx` IDs. They are provisional: no independent population validation split was reserved. The comparison baseline is Laplace-smoothed context frequency, masked by available motifs; contexts with n<8 back off globally.','',
  '| Context | Most frequent motif | Selected / n |','|---|---|---:|']
 for key,counts in report['models']['population']['contexts'].items():
  selected=max(counts,key=lambda s:(counts[s],s));pl.append(f"| `{key}` | `{selected}` | {counts[selected]}/{sum(counts.values())} |")
 pl+=['','## 4. Goals — hypotheses','', 'No population goal ordering is accepted. Contact/pressure labels inherit descriptive motif names only; goal validation n=0, confidence unestimated.','',
  '## 5. Beliefs (theirs)','', 'No second-order beliefs inferred; distinguishable tests n=0, predictions=0, confidence unestimated.','',
  '## 6. Adaptation and deception','', 'Different player versions and sides must not be read as adaptation by one agent. No population deception or causal adaptation claim; tests n=0.','',
  '## 7. Validation','',f"As a frozen baseline on Jordan heldout choices: {h['population_correct']}/{h['n']} ({pct(h['population_accuracy'])}); this is not a population-generalization test. All 21 tapes pass every original state hash. No proxy rollouts (n=0); usable=False; divergence unmeasured.",'',
  '## 8. Unglossed','', 'Uses the same five observer-binding extensions documented in the individual IR; no primary-glossary changes. Tagged blocks n=6,489.','',
  '## 9. Counter-strategy candidates','', 'None: this is a comparison prior without an independently validated exploit. Candidate tests=0.','',
  '## 10. Provenance','', 'Same pinned game, host view, own policy, guide and instrument as [individual IR](opponent.ir.md). Selection preceded behavior inspection and ignored outcomes. Policy-version composition:','']
 for label,count in pops.items():pl.append(f'- `{label}`: {count} episode(s).')
 pl+=['','Episode IDs, creation dates, observation slots and versions are in the frozen study plan.']
 (out/'population.ir.md').write_text('\n'.join(pl)+'\n')
 # Preserve raw artifact hashes without credential-bearing URLs.
 manifest={'schema':'gota-opponent-artifacts/1','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'game_commit':'f2ab9598d8f8001b6beae3e66404e341770c803f','evidence_root':str(d),'artifacts':{}}
 paths=[d/'eligible.json',d/'champions.json',d/'rounds.json',d/'leaderboard.json',d/'study-plan.json',d/'model-freeze.json',d/'observer-probe',Path(__file__).parent/'README.md']+list(out.glob('*'))+list(modeldir.glob('*268.py'))+[modeldir/'population_20260919.py',ROOT/'examples/gods_of_the_arena/players/ir/opponent_ir.py']+list(Path(__file__).parent.glob('*.py'))+[Path(__file__).parent/'replay_observer.nim']
 for row in plan['episodes']:
  folder=d/'artifacts'/row['id'];paths.extend(folder/name for name in ['replay.bin','results.json','observer.jsonl.gz','observer-validation.json','observations.jsonl.gz','segmentation.json'])
 for path in paths:
  if path.is_file() and path.name!='artifact-manifest.json':manifest['artifacts'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 (out/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Built',modeldir/'jordan_v268.py','and',out/'opponent.ir.md')
if __name__=='__main__':main()
