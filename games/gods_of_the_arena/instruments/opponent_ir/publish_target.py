"""Publish counted target models in primary Python IR, with honest predictive limits."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import pprint
import shutil
from guide import publish_guide
import sys

from semantics import PARAMETERS, SKILLS, context
from build import DESCRIPTIONS, GOAL_BY_SKILL, GOALS, pct, when

ROOT=Path(__file__).resolve().parents[4]
LOCAL=ROOT/'examples/gods_of_the_arena/players/ir'
sys.path.insert(0,str(LOCAL))
import opponent_ir

def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def model(report,plan,level,population_rows):
    individual=level=='individual';predictor=report['models']['train' if individual else 'population']
    prefix=plan['preference_prefix'] if individual else plan['preference_prefix'].replace('_I','_P')
    prefs=deepcopy(report['preferences']) if individual else []
    if not individual:
        for key,counts in predictor['contexts'].items():
            selected=max(counts,key=lambda x:(counts[x],x))
            rs=[r for r in population_rows if r['preference_eligible'] and context(r['situation'])==key]
            options=Counter(x for r in rs for x in r['affordances'] if x!=selected)
            other=max(options,key=lambda x:(counts.get(x,0),options[x],x))
            paired=[r for r in rs if selected in r['affordances'] and other in r['affordances']]
            n=len(paired);chosen=sum(r['selected']==selected for r in paired)
            dates={r['id']:r['created_at'] for r in plan['episodes']}
            prefs.append({'id':f"{prefix}_O{int(key.split('_')[1])*2+int(key.split('_')[-1])+1:02d}",
                'when':key,'skill':selected,'over':other,'n':n,'chosen_count':chosen,'confidence':(chosen+1)/(n+2),
                'confidence_meaning':'Smoothed observed frequency; not intent certainty; correlated starts.',
                'base_rate':{'source':'Uniform over paired available motifs; population generalization not independently tested',
                    'n':n,'rate':sum(1/len(r['affordances']) for r in paired)/n if n else None},
                'level':'population','opponent':'sampled_current_policy_field_20260920','status':'provisional',
                'last_observed':max(rs,key=lambda r:(dates[r['episode']],r['tick']))['id'],
                'predictions':{'n':0,'correct':0,'accuracy':None,'population_accuracy':None}})
    claims={};rules=[]
    for pref in prefs:
        claims[pref['id']]={'claim':f"WHEN {when(pref['when'])} THEY PREFER {pref['skill']} OVER {pref['over']} FOR {GOAL_BY_SKILL[pref['skill']]} (goal hypothesis).",
            'status':'supported' if pref['status']=='supported' else 'requires_review','evidence':[pref]}
        rules.append({'id':pref['id'],'when':pref['when'],'skill':pref['skill'],'for':[GOAL_BY_SKILL[pref['skill']]]})
    goals={}
    for key,text in GOALS.items():
        if key=='hero_pressure':text='Hypothesis: maintain visible hero contact in the counted contexts; no inference of kill intent or global priority.'
        support=[p for p in prefs if GOAL_BY_SKILL[p['skill']]==key]
        goals[key]={'preference':text,'provenance':'interpretation','supporting_preferences':[p['id'] for p in support],
            'paired_context_starts':sum(p['n'] for p in support),'global_ordering_validated':False}
    result={'schema':opponent_ir.SCHEMA,'id':plan['target_slug'].replace('-','_')+'_'+level+'_observer_model',
        'situation':{'grounded':{'observation':'One real own slot0/5 at its predecision moment. Motif at t must persist 6 ticks; predictors use only t-1.',
            'predicates':{p['when']:when(p['when']) for p in prefs},'glossary_extensions':DESCRIPTIONS,
            'structure_semantics':'For structures alive means exposed; HP>0 means standing. Target0 means none OR hidden.'},
            'notes':'Forecast visible motifs; do not infer executable opponent source rules, rule order, or a single-rule-per-tick policy. Movement remains a simultaneous qualifier.'},
        'belief':{'grounded':{'level':level,'opponent_version':plan['target_version'] if individual else 'sampled_field_20260920',
            'opponent_label':plan['target_label'] if individual else 'Eight earlier field versions',
            'our_policy':plan['our_policy'],'predictor':predictor,
            'skills':report['skills'] if individual else {'scope':'same seven observable motifs; counted rows in population-observations.jsonl.gz'},
            'validation':report['heldout'] if individual else {'n':0,'population_generalization':'not independently tested'},
            'observability':report['observability']['all_target' if individual else 'population'],
            'proxy':report['proxy'],'second_order_beliefs':{'n':0,'confidence':None,'predictions':0,'inferred':False},
            'uncertainty':'Partial visibility, estimated affordances, correlated trajectories and retrospective boundaries; absence is not death. Source memory, private cooldowns and hidden observations are unavailable.'},'claims':claims},
        'goal':goals,'skill':{s:{'operator':'observed_'+s,'parameters':{'minimum_segment_ticks':6}} for s in SKILLS},
        'strategy':rules,'execution':{'binding':'gota-observer-model/1','game_version':'2026.9.16.5','language':'Python'},
        'update':{'revision':1,'parent':None,'change':{'origin':'observable_replay_inference','parameters':PARAMETERS,
            'model_freeze_sha256':report['model_freeze_sha256'],'purpose':'Primary-format forecast model; no automatic strategy adoption'},
            'needs_review':['Unvalidated live rollout proxy','Untested counterstrategies','Exact-repeat heldout leakage risk','Class/side/phase confounding','No hidden belief or ability inference'],
            'evidence':[{'artifact':f"docs/opponents/{plan['target_slug']}/evidence.json",'model_level':level,'episode_count':report['observability']['all_target' if individual else 'population']['episodes']}]}}
    return opponent_ir.validate(result)

def proposals(plan,report,macro):
    prefix=plan['preference_prefix'];richard=plan['target_slug']=='richard-v135'
    return [{'id':prefix+'_C01','status':'proposed_test_only','adopted':False,
        'rule':{'id':prefix+'_C01','when':'visible_core_pressure_and_distant_defenders','skill':'observe','for':['G_defense']},
        'predicate_proposal':'Visible living enemy pair near a standing friendly defense anchor and own god; keep spatial and time-to-return evidence, never opponent label or hidden state.',
        'mechanism':'Allow a bounded critical-defense commitment to override the 28-tile distant-recall cancellation; evaluate earlier warning distance and assigned responder travel.',
        'opponent_preference_ids':[prefix+'_O13'] if richard else [prefix+'_O11',prefix+'_O15'],
        'macro_evidence':{'n':macro['n'],'pair_within24':macro['radius24'],'scope':'Descriptive training observations; not heldout macro validation'},
        'existing_intervention':('Critical60 blue 4W0L, Critical40 blue 2W2L; both red 0W4L. Directional screens only.' if richard else 'No controlled current-policy-versus-Alex intervention has yet validated this proposed repair.'),
        'test':'Fresh pinned Richard135 AND Alexg002 candidate/control 40 per color, >=30/40 each target/color; retain Jordan268 >=38/40 each and original field guard. Full source, VM and replay audits. Draws count zero.'},
      {'id':prefix+'_C02','status':'diagnostic_proposal','adopted':False,
        'rule':{'id':prefix+'_C02','when':'local_defense_fails_after_response','skill':'attack','for':['G_defense','G_survival']},
        'predicate_proposal':'Observed response occurred but the core still fell; require a trace of actual defender arrival and target choice.',
        'mechanism':('Repair red combat/economy after timely response. Test support and wave participation; the existing red equipment-only screen 0/4 already refutes sufficiency of that tested variant.' if richard else
            'Test interception at the threatened inner structure, before the god becomes the active target. Visible late god burn leaves very little travel time; a defender who only chases heroes can still allow structure pressure.'),
        'evidence':'own-decision-analysis.json plus macro-observations.json; diagnostic inference, not an adopted opponent preference.',
        'test':'Record arrival time, enemy structure-target duration, friendly survival and actual fort wins. Use real reacting opponent; the observational model is not a rollout controller.'}]

def publish(d):
    report=read(d/'evaluation.json');plan=read(d/'study-plan.json');macro=read(d/'macro-observations.json')
    out=ROOT/'docs/opponents'/plan['target_slug'];out.mkdir(parents=True,exist_ok=True)
    basename='richard_v135' if plan['target_slug']=='richard-v135' else 'alex_g002_v1'
    rows={};population=[]
    for r in plan['episodes']:
        with gzip.open(d/'artifacts'/r['id']/'observations.jsonl.gz','rt') as f:rows[r['id']]=[json.loads(l) for l in f]
    for i in report['population_episode_ids']:population.extend(rows[i])
    individual=model(report,plan,'individual',population);prior=model(report,plan,'population',population)
    proposed=proposals(plan,report,macro)
    modeldir=LOCAL/'opponents'
    for name,value in [(basename,individual),(basename+'_population',prior)]:
        text='"""Counted observer-only opponent model in the primary seven-layer Python IR.\nNo private source; not an executable or validated rollout proxy.\n"""\n\nMODEL = '+pprint.pformat(value,width=110,sort_dicts=False)+'\n'
        if name==basename:text+='\nPROPOSED_RULES = '+pprint.pformat(proposed,width=110,sort_dicts=False)+'\n'
        (modeldir/(name+'.py')).write_text(text)
    for source,dest in [('evaluation.json','evidence.json'),('study-plan.json','study-plan.json'),('model-freeze.json','model-freeze.json'),
        ('macro-observations.json','macro-observations.json'),('own-decision-analysis.json','own-decision-analysis.json'),('runtime-checks.json','runtime-checks.json'),
        ('probe-provenance.json','probe-provenance.json'),('observer-policy.bas','observer-policy.bas'),('observer-policy.ir.json','observer-policy.ir.json'),
        ('heldout-predictions.jsonl.gz','heldout-predictions.jsonl.gz')]:shutil.copy2(d/source,out/dest)
    publish_guide(d, out)
    with gzip.open(out/'observations.jsonl.gz','wt') as f:
        for r in plan['episodes']:
            if r['split']!='population':
                for item in rows[r['id']]:f.write(json.dumps(item)+'\n')
    with gzip.open(out/'population-observations.jsonl.gz','wt') as f:
        for item in population:f.write(json.dumps(item)+'\n')
    write(out/'counterstrategy-proposals.json',proposed)
    write(out/'example-observations.json',[x for r in plan['episodes'] if r['split']=='train' for x in rows[r['id']] if x['preference_eligible']][:8])
    h=report['heldout'];v=report['observability']['all_target'];targetrows=[r for r in plan['episodes'] if r['split']!='population']
    richard=basename=='richard_v135'
    lines=[f"# {plan['target_label']} — individual opponent IR",'',
        f"Python: [{basename}.py](../../../examples/gods_of_the_arena/players/ir/opponents/{basename}.py). The same seven layers and `id / when / skill / for` records as our primary IR; observable forecasting binding, not opponent source code.",'',
        ('**Main finding:** Richard maintains structure pressure while contesting heroes. In the creep-and-structure context, the model predicts structure targeting on 140/226 heldout starts, versus 83/226 correct for the population predictor. Our blue defense fails against a visible two-hero core attack; red also loses combat.' if richard else
         '**Main finding:** Alex produces a fast core attack that our counterrace policy sees but declines to answer. In all 12 distinct training streams, the first visible enemy pair within 24 tiles of our god arrives while all five friendly heroes are alive farther than 28 tiles away. This is a counted defensive failure, not proof of Alex’s hidden intent.'),'',
        '## Identity, evidence and visibility','',
        f"Exact version `{plan['target_version']}`; individual model. Current own BASIC `{plan['our_policy']['basic_sha256']}`. 20 target games, 16 training / 4 chronological heldout; outcomes were ignored during selection. Date range {targetrows[0]['created_at']}–{targetrows[-1]['created_at']}. Opponent wins 20/20 in this observational sample.",
        f"Training has {report['unique_training_trajectories']} distinct complete observer streams; heldout has {report['unique_heldout_trajectories']}. Visibility: {v['visible_living_opponent_ticks']:,}/{v['living_opponent_ticks']:,} living opponent hero-ticks ({pct(v['fraction'])}). Observer dead fraction {pct(v['observer_dead_fraction'])}; unsegmented residual {pct(v['residual_fraction'])} of visible hero-ticks.",
        'The observer is one actual owned hero instance, slot 0 or 5. No pooled teammate viewpoints. Targets outside its object list are masked; unseen is unknown, not dead. Every original replay tick/hash and action consumption is verified; game logs report 10/10 VMs active in all 34 target and population episodes.','',
        '## Inferred skills','', '| Motif | Starts in distinct training | Ticks | Median duration |','|---|---:|---:|---:|']
    for skill,stats in report['skills'].items():lines.append(f"| {skill} | {stats['n']} | {stats['ticks']} | {stats['median_duration_ticks']} |")
    lines+=['', 'Every motif has counted initiation contexts, termination reasons and concurrent movement in evidence.json. Target means visible pursuit/retained target, not necessarily an attack. Advance/withdraw are radial geometry relative to our god; hold can be turning/collision. Six-tick minimum segments; spells/private cooldowns are outside the inferred skill set.','',
        '## Preferences and prediction records','',
        'Each confidence is the smoothed paired-affordance selection frequency, not certainty about intent. Both named alternatives must be locally estimated available at t−1. `supported` means relative forecast lift in this sample; it does not establish an exploitable weakness. Sparse or non-improving statements remain provisional.','',
        '| ID | Situation | Prefer → over | Chosen/n | Confidence | Population base rate (n) | Heldout correct/n; baseline | Status |',
        '|---|---|---|---:|---:|---|---|---|']
    for p in sorted(report['preferences'],key=lambda p:(p['status']!='supported',-p['confidence'])):
        q=p['predictions'];b=p['base_rate'];lines.append(f"| {p['id']} | {when(p['when'])} | {p['skill']} → {p['over']} | {p['chosen_count']}/{p['n']} | {p['confidence']:.3f} | {pct(b['rate'])} ({b['n']}) | {q['correct']}/{q['n']}; {q['population_correct']}/{q['n']} | {p['status']} |")
    lines+=['','Full records in the Python belief layer include model level, exact opponent identity, last observed episode/tick, supporting episode count, prediction intervals and evidence examples. Confidence-sorted supported/provisional rows above are retained together so failed hypotheses remain inspectable.','',
        '## Goals and beliefs — hypotheses','',
        ('Conditional structure pressure over creep contact is supported by Richard135_I_O13. Hero contact over holding is supported by O03; hero versus structure O11 adds no lift over population and remains provisional. These contexts do not establish a universal goal order.' if richard else
         'Conditional structure contact over hero contact is suggested by AlexG002v1_I_O11 (25/33 training; 4/6 heldout), with very little heldout evidence. O15 favors hero contact when all three target categories are nearby (50/69 training; 9/14 heldout). O13’s creep preference is no more predictive than population. No universal structure-first or hero-ignoring rule is inferred.'),
        'Goals are interpretations linked to preference IDs and counts in MODEL.goal. No second-order opponent beliefs are inferred: distinguishable tests n=0, confidence unestimated, predictions 0.','',
        '## Adaptation, constraints and deception','',
        'Same-context training choices are split by episode midpoint, chronological halves and whether our visible units target the opponent; all counts are in evidence.json/adaptation. These descriptive shifts do not isolate causal adaptation from class, position or game phase. Causal adaptation established=False. Deception tests 0; no deception claim.',
        f"Excluded starts: {json.dumps(v['exclusions'])}. Ineligible affordances and left-censored first appearances never enter preference counts. No hidden cooldown or gold inference.",'',
        '## Heldout validation','', '| Predictor | Correct / eligible | Accuracy |','|---|---:|---:|',
        f"| Individual IR | {h['correct']}/{h['n']} | {pct(h['accuracy'])} |",
        f"| Context population | {h['population_correct']}/{h['n']} | {pct(h['population_accuracy'])} |"]
    for label in ('class','side'):
        b=h['robustness_baselines'][label];lines.append(f"| Population + {label} | {b['correct']}/{b['n']} | {pct(b['accuracy'])} |")
    lines += [f"| Previous motif persists | — | {pct(h['persistence_accuracy'])} |",'',
        f"Novel-stream heldout: {h['novel_trajectories']['correct']}/{h['novel_trajectories']['n']}, {pct(h['novel_trajectories']['accuracy'])}; population {pct(h['novel_trajectories']['population_accuracy'])}. Exact observer-stream novelty is not statistical independence. Cluster uncertainty: `{json.dumps(h['cluster_uncertainty'])}`.",
        ('Richard has some novel heldout observer streams, but only three heldout trajectory clusters total; transfer beyond these lineups remains unproven.' if richard else
         '**Every Alex heldout stream exactly matches a training stream.** The small lift is descriptive replay prediction, not evidence of generalization to a new trajectory; the cluster interval includes zero. No Alex tendency qualifies as a validated exploit.'),
        'No proxy controller was executed: rollouts 0, divergence unmeasured, usable=False. Motif prediction is conditioned on retrospectively identified boundaries; it predicts neither skill onset timing nor action arguments.','',
        '## Our policy failure and proposed counters','',
        ('In 7/7 distinct training streams where the first god damage is visible, no living friendly hero is within 28 tiles. Representative blue replay: at t5760 all five decisions have defCount=2, defActive=0 and defUntil=0; first observed god damage is t5778. Critical60’s existing 4/4 blue screen is encouraging but red remains 0/4, and neither Alex nor Jordan preservation is established.' if richard else
         'Representative red replay: at t2520 all five agents record defCount=5 and defAnchor=1, yet defActive=0/defUntil=0 and continue attacking remote structures. First god damage is t2533; defeat t2583. On blue, t3000 samples also show defCount=4 and canceled defense; first god damage t3108, defeat t3126. The 28-tile remote-recall cancellation is an actionable own-policy decision problem, not a failure to observe the push.'),
        'The exact deployed BASIC reconstructed all own commands and state hashes in representative red and blue games. See own-decision-analysis.json; memories are actual 120-tick samples and are never interpolated. Macro counts are descriptive training analysis added after fit; they did not enter the heldout predictor.','']
    for p in proposed:lines += [f"- `{p['id']}` ({p['status']}): {p['mechanism']} Test: {p['test']}"]
    lines += ['', 'These are reviewable primary-strategy proposals in PROPOSED_RULES, not adopted live-policy changes. Richard, Alex and Jordan gates must pass together.','',
        '## Unglossed and provenance','',
        'Observer-relative advance, absolute low HP, estimated opponent affordances, visible target versus actual attack, and concurrent target/motion remain explicit local glossary extensions. They occur on every annotated sustained start and do not silently change the primary policy glossary.',
        'Sources: study-plan.json, model-freeze.json, evidence.json, macro-observations.json, own-decision-analysis.json, observer-policy.ir.json, population.ir.md, full annotated observations.jsonl.gz and heldout-predictions.jsonl.gz. Every observation includes episode/tick, visibility, alternatives, selected motif and visible outcome. Exact guide snapshot and artifact hashes are preserved.','',
        '| Split | Created UTC | Observer slot | Episode |','|---|---|---:|---|']
    for r in targetrows:lines.append(f"| {r['split']} | {r['created_at']} | {r['observer_slot']} | [{r['id']}](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:{r['id']}) |")
    (out/'opponent.ir.md').write_text('\n'.join(lines)+'\n')
    pop=report['observability']['population']
    (out/'population.ir.md').write_text(f"# Current-policy field prior for {plan['target_label']}\n\nPython: [{basename}_population.py](../../../examples/gods_of_the_arena/players/ir/opponents/{basename}_population.py).\n\n14 earlier games from 8 other versions, same own executable and single-instance view. Both target versions and owned opponents excluded. Counts are deduplicated by exact observer stream; selected IDs and dates are in study-plan.json. Visible living hero-ticks: {pop['visible_living_opponent_ticks']}/{pop['living_opponent_ticks']} ({pct(pop['fraction'])}); residual {pct(pop['residual_fraction'])}.\n\nSeven motifs use the individual report’s exact initiation/termination semantics. Conditional preference counts and all primary-style belief entries are in the Python prior. Every preference is provisional: independent population validation n=0. Goals are linked interpretations, no global ordering; second-order beliefs 0, causal adaptation/deception tests 0. No counterstrategy or executable proxy is adopted; rollouts 0, divergence unknown, usable=False. The five glossary extensions and observability constraints are shared with the individual IR. Full population annotation blocks are in population-observations.jsonl.gz.\n\nAs the fixed baseline on this opponent’s heldout choices it scores {h['population_correct']}/{h['n']} ({pct(h['population_accuracy'])}); this is not population-wide generalization. Source/version, runtime proofs and exact guide are shared with the individual study.\n")
    print('PUBLISHED',out/'opponent.ir.md',flush=True)

if __name__=='__main__':publish(Path(sys.argv[1]).resolve())
