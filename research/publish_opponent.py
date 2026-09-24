"""Build a non-executable seven-layer model without inventing controller guards."""
from pathlib import Path
from collections import Counter
import hashlib,json,random,shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/opponents/khors-v180'
read=lambda p:json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def ratio(rows,den,num):
    eligible=[r for r in rows if r['counts'].get(den,0)>0]
    n=sum(r['counts'].get(den,0) for r in rows);k=sum(r['counts'].get(num,0) for r in rows)
    rng=random.Random(924180);values=[]
    for _ in range(5000):
        draw=rng.choices(eligible,k=len(eligible))
        values.append(sum(r['counts'].get(num,0) for r in draw)/sum(r['counts'][den] for r in draw))
    values.sort()
    return {'opportunities':n,'choices':k,'fraction':k/n,'eligible_episodes':len(eligible),
            'choice_episodes':sum(r['counts'].get(num,0)>0 for r in eligible),
            'episode_cluster_bootstrap95':[values[124],values[4874]],'unit':'Recorded explicit attack command, conditional on listed exported public affordances; not every game tick.'}

def main():
    s=read(OUT/'evidence/summary.json');rows=read(OUT/'evidence/actor-rows.json');kh=[r for r in rows if r['player']=='Andre von Auto']
    claims=[]
    def claim(ident,text,den,num,alternatives):
        record={'id':ident,'claim':text,'status':'observed_conditional_tendency','evidence':ratio(kh,den,num),
                'clean_game_evidence':ratio([r for r in kh if r['all_vm_clean']],den,num),
                'alternatives':alternatives,'source':'evidence/actor-rows.json','priority_identified':False,
                'state':{'required_history':'unknown','reset':'unknown'},'proxy_usable':False}
        claims.append(record);return record
    claim('K180_HERO_OVER_CREEP','Strong hero-target preference when both a hero and a lane creep are within nominal basic range (+0.25tile measurement tolerance).','both_hero_creep_in_basic_range','both_choose_2',['Nearest/lowest-HP hero scoring','Current-target persistence','Hero-specific target logic','Opportunity selection differs from deliberate pursuit'])
    claim('K180_NEUTRAL_DOWNTIME','Usually attacks a visible neutral within10tiles when no enemy hero is within10tiles and no enemy lane creep within6tiles.','neutral_without_nearby_hero_wave','neutral_opportunity_choose_6',['Generic nearest-target selection','Explicit downtime farming','Lane route intersects camps','Farm-health guard or existing aggro'])
    claim('K180_LAST_HIT','Often selects a lane creep whose observed HP fits one nominal basic attack while it is in range. This is an estimated last-hit opportunity, not guaranteed damage or last-hit credit.','one_basic_creep_available','choose_finishable_creep',['Lowest absolute HP','Explicit kill threshold','Attack cooldown timing','Competing hero priority'])
    counts=s['khors']['commands'];building=sum(counts.get('attack_'+str(k),0) for k in [1,4,5])
    claims += [{'id':'K180_BUILDINGS','status':'observed_rejection_of_universal_claim','claim':f'{building}/{counts["command_2"]} explicit attack commands address buildings/gods; never attacks buildings is false for v180. This does not identify which HP threshold or priority causes a siege.',
                'evidence':['evidence/summary.json','evidence/actor-rows.json'],'proxy_usable':False},
               {'id':'K180_WEAK_MELEE','status':'observed_context_limited','claim':'Neutral farming is not sufficient for weak melee productivity: two Vanguard games score0 and five DeathKnight games average163.8 despite neutral kills. These tiny, confounded class slices are not causal kit comparisons.',
                'evidence':['evidence/summary.json'],'proxy_usable':False},
               {'id':'K180_RESOURCES','status':'observed_effects','claim':'250health potions and151portal scrolls consumed across28appearances. Mean gold spent1885.36 includes414.29buybackgold; high spending is not all healing. Exact shopping trigger and portal direction rule remain unidentified.',
                'evidence':['evidence/summary.json','evidence/actor-rows.json'],'proxy_usable':False},
               {'id':'K180_NEUTRAL_CREDIT','status':'observed_counterexample_to_kill_equals_xp','claim':'One Crossbowman game has11neutral kills but only30neutral XP. Killing a neutral does not establish that the killer received its full reward. Current mechanics require alive/in-range eligibility and shareXP. Individual missing receipts need event-level distance/alive checks.',
                'evidence':[{'episode':'ereq_307914d5-94f6-4db1-bf58-2d2d67bf2166','slot':0,'artifact':'evidence/actor-rows.json'}],'proxy_usable':False}]
    ir={'schema':'gota-opponent-descriptive-ir/3','id':'khors_v180_current62_observations_20260924',
        'situation':{'identity':{'name':'khors:v180','owner':'Andre von Auto','player_id':'ply_3d22435e-30a2-4f2a-b037-a5c249583788','policy_version_id':'564e4650-5efb-4b66-b9d4-a49070e1e68e','source_sha256_from_specs':s['source_sha256'],'source_available':False},
            'game':{'version':'2026.9.23.4','engine_commit':'2c8db6ebe1dc785ce1eea87496505d1244ee4c44','replay':62},
            'authority':{'features':'Each actor own legal predecision visibility-filtered public objects, exported within18tiles, plus own public stats. Not the opponent source or internal state.','labels':'Recorded submitted commands; accepted effects/XP/score separately reconstructed from full replay truth.','clock':'World tick at frozen decision callback; only explicit attack commands enter conditional choice denominators.','limits':'Farther-than18tile targets are unknown in this export; action arguments do not prove acceptance. Returning neutrals remain explicit exceptions.'},
            'predicates':{'hero_and_creep_in_basic_reach':'Both visible alive enemy categories within nominal hero basic range+0.25tile','neutral_downtime':'Visible nonreturning neutral<=10tiles; no visible enemy hero<=10 and no enemy lane creep<=6','estimated_creep_finish':'Visible alive creep in nominal reach and HP<=public basic damage','structure_opportunity':'Exposed alive enemy structure/god visible<=9tiles'},
            'coverage':{'episodes_scanned':36,'khors_appearances':28,'distinct_whole_game_command_streams':s['khors_distinct_full_game_streams'],'all_vm_clean_khors_games':s['khors_clean_games']['n'],'classes':{k:v['n'] for k,v in s['khors_classes'].items()},'no_new_hosted_games_for_model':True}},
        'belief':{'claims':claims,'global_limits':['Only5khors games have all ten VMs clean; other-player failures change opportunity distributions. Khors itself is clean in all28.','No heldout forecasting test or mechanistic intervention. Thousands of commands are clustered within28games.','Observed current62 behavior must not overwrite v114/v179 historical IR.','No calibration claim for latent goals or exact thresholds. No JEV used.']},
        'goal':{'individual_income':{'status':'analyst_hypothesis','description':'Repeated hero kills and creep/neutral income consistent with XP accumulation; internal objective weights unknown.'},'survival_and_return':{'status':'analyst_hypothesis','description':'Consumables, portals and buybacks maintain presence; optimal thresholds not identified.'}},
        'skill':{'hero_focus':{'initiation':'Observed attack choices when heroes and creeps coexist in reach','operator':'prefer_hero_target_motif','termination':'Unknown; target changes retained in evidence','channels':['attack intent','spells and movement may coexist']},
            'creep_finish':{'initiation':'Estimated basic-finish creep available','operator':'select_finishable_creep_motif','termination':'Target dies, changes or exits visibility; controller rule unidentified'},
            'neutral_income':{'initiation':'Observed downtime predicate','operator':'direct_neutral_attack_motif','termination':'New units, threat, returning mob or camp death; exact precedence unknown'},
            'resource_cycle':{'initiation':'Accepted item/portal/buyback events','operator':'replenish_and_return_motif','termination':'Observed portal completion/interruption or next field action; trigger thresholds unknown'}},
        'strategy':[{'id':'K180_S_HERO','when':'hero_and_creep_in_basic_reach','skill':'hero_focus','for':['individual_income'],'status':'conditional_preference_observed','claim':'K180_HERO_OVER_CREEP'},
            {'id':'K180_S_CREEP','when':'estimated_creep_finish','skill':'creep_finish','for':['individual_income'],'status':'conditional_preference_observed','claim':'K180_LAST_HIT'},
            {'id':'K180_S_NEUTRAL','when':'neutral_downtime','skill':'neutral_income','for':['individual_income'],'status':'conditional_preference_observed','claim':'K180_NEUTRAL_DOWNTIME'},
            {'id':'K180_S_RESOURCE','when':'Unknown resource thresholds','skill':'resource_cycle','for':['survival_and_return'],'status':'effects_observed_trigger_unidentified','claim':'K180_RESOURCES'}],
        'execution':{'kind':'descriptive_non_executable','compiler_eligible':False,'proxy_usable':False,'forecast_validated':False,'controller_order_identified':False,'latent_memory_identified':False,'may_supply_hidden_features_to_live_policy':False},
        'update':{'revision':1,'parent':'Separate version-specific replacement for using khors114/v179 assumptions onv180; old models unchanged.',
            'evidence':['evidence/plan.json','evidence/summary.json','evidence/actor-rows.json','evidence/artifact-index.json'],
            'next_tests':['Actual responsive neutral-income trial with both carry and weak-hero draft contexts','Matched hero-versus-creep target priority with kill likelihood, travel and enemy control guards','Verify XP eligibility radius and alive state on neutral kills with little XP','Hold geometry/history fixed to discriminate nearest-target scoring from explicit priority','Chronological holdout needed before any predictive or executable proxy claim']}}
    write(OUT/'opponent.ir.json',ir)
    hypotheses={'schema':'gota-counter-hypotheses/1','opponent':'opponent.ir.json','goal':'Expected individual XP-minus-time score','hypotheses':[
        {'id':'OWN_WEAK_NEUTRAL','status':'under_responsive_test','change':'Direct nearby neutral combat for weak heroes, level-tier/HP/nearby-wave guards, no speculative weak-hero pulls','source_sha256':'c2321ead3ea8c3cab828c0c128662db355cebf67fde440711a50321c00ac0a7a','metric':'Paired individual score plus actual neutral kills and XP','falsifier':'More camp kills but lower score or no neutral XP increase','experiment':'../../hosted.py'},
        {'id':'OWN_HERO_FINISH_PRIORITY','status':'proposed_not_tested','change':'Prefer reachable, plausible hero finishes while retaining imminent creep last hits; do not copy unconditional aggression','metric':'Hero XP gained minus lane/neutral XP and extra downtime','falsifier':'More pursuit/deaths or less total score'},
        {'id':'OWN_CREDIT_RADIUS','status':'proposed_not_tested','change':'Keep weak hero alive within6tiles when a pulled neutral dies; measure recipients rather than kill counters','metric':'Neutral XP per kill/opportunity and net score','falsifier':'Neutral kills without own receipts; travel/survival cost exceeds income'}]}
    results_path=ROOT/'research/results/statistics.json'
    if results_path.exists():
        tested=read(results_path)['contrasts']['weak-neutral']
        h=hypotheses['hypotheses'][0]
        h.update(status='tested_did_not_pass_score_gate' if not tested['pilot_advance'] else 'awaiting_independent_confirmation',
                 result={'paired_games':tested['overall']['n'],
                         'mean_score_delta':tested['overall']['mean_delta'],
                         'adjusted_975_interval':tested['overall']['delta975'],
                         'baseline_neutral_kills':tested['neutral_mechanism']['baseline']['neutral_kills'],
                         'candidate_neutral_kills':tested['neutral_mechanism']['candidate']['neutral_kills'],
                         'interpretation':'Neutral kills alone are not an efficacy metric. Class-specific findings are exploratory; no rollout.'},
                 results='../../RESULTS.md')
    write(OUT/'counter-hypotheses.ir.json',hypotheses)
    archive=Path(read(ROOT/'research/manifest.json')['archive'])
    shutil.copy2(archive/'docs/guides/guide-opponent-model-ir.md',OUT/'guide-snapshot.md')
    rows_text='\n'.join('| '+k+' | '+str(v['n'])+' | '+str(round(v['mean_score']))+' | '+str(round(v['mean_xp_sources']['neutral']))+' |' for k,v in s['khors_classes'].items())
    report=f'''# Khors v180: observed behavior on the neutral-camp release

28 appearances, eight hero classes, both sides, in36leaguegames selected before outcomes. All replay state hashes, XP and integer scores reconcile. All28khors VMs are clean; only5games have all ten VMs clean. Other-player failures remain explicitly marked. No source, JEV, heldout forecast, executable proxy or causal transfer claim.

The strongest tendencies are conditional hero priority (801/816commands;27eligible games), neutral harvesting without nearby hero/wave targets (1243/1307;28games), and estimated creep finishes (2685/3571;28games). Clean-game counterparts for the first two are75/78 and296/305. Episode-cluster uncertainty and per-game denominators are in[the IR](opponent.ir.json).

v180does attack buildings:1125/9914explicit attack commands address towers, barracks or gods. The old universal building-avoidance hypothesis is false for this version.51commands addressed returning neutrals. These are submitted commands, not proof of damage.

Mean score is2511.43; meanXP4926.11 is composed of2180.36hero,1667.93lane-creep,595.68neutral and482.14structure/other. These are descriptive sampled outcomes, affected by class, roster and other-policy failures. Do not compare them causally with our differently drafted heroes or with a leaderboard average.

| Hero | Games | Mean score | Mean neutral XP |
|---|---:|---:|---:|
{rows_text}

Neutral income alone is insufficient: Vanguard still scored zero in both appearances and DeathKnight averaged164over five. The goal for our repair remains net individual score, with neutral kills/XP as mechanism checks.

The[7581-point Lich game](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_26895ca1-ea7d-4152-bbd7-c9d31a77fc35) had69neutral kills and4109neutral XP, alongside3508creep and3300hero XP. It also had an unrelated VM failure. Conversely,[this Crossbowman game](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_307914d5-94f6-4db1-bf58-2d2d67bf2166) recorded11neutral kills but only30neutral XP. We must verify eligibility and actual reward receipts, not optimize a kill counter alone.

Resource use is substantial:250health potions and151portal scrolls across28games. Mean spending1885includes414in buybacks; it is not all healing. Purchase and portal events are retained per episode.

[Counter hypotheses](counter-hypotheses.ir.json) separate the weak-neutral candidate now under test from untested hero-priority and XP-radius ideas. [Evidence rows](evidence/actor-rows.json) link every claim to an episode, class, command denominator and exact source hash. [Artifact index](evidence/artifact-index.json) locates immutable full replays and public frames. The collection/behavior instruments are preserved from the research archive; the fresh workspace does not import archived gameplay.

Run `python research/observations.py` then `python research/publish_opponent.py` from the workspace to reproduce summaries from captured inputs. Inference remains at motif granularity: exact threshold, memory, action ordering, target identity prediction and reactive intervention behavior are unidentified.
'''
    (OUT/'README.md').write_text(report)
    manifest={'files':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json'},'raw_root':str(ROOT.parent/'polyworld/tmp/gota-khors180-observations-20260924')}
    write(OUT/'manifest.json',manifest)

if __name__=='__main__':main()
