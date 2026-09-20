"""Publish source-reveal IR while proving the observation-only freeze is intact."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from source_audit import ROOT, OUT, SOURCE_SHA, VERSION, read, write, sha

COMMIT = '93bd2aa1d79549960e88ea0f63ccf3a73273f198'
ORIGINAL = 'fcdc915074115e772469c50daa61dc06b3ef8975'
REPO = ROOT.parent / 'co-gas'
SOURCE = 'players/users/relh/co-gas/polyworld-basic/gods_of_the_arena_neural_siege_counter.bas'
GAME = ROOT.parent / 'polyworld-gota-clean-20260916-r5'


def git_bytes(commit, path):
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=REPO)


def main():
    assert sha(OUT / 'v135.bas') == SOURCE_SHA
    assert git_bytes(COMMIT, SOURCE) == git_bytes(ORIGINAL, SOURCE) == (OUT / 'v135.bas').read_bytes()
    assert git_bytes(COMMIT, 'experiments/candidates/gods-of-the-arena-neural-siege-counter-20260920.yaml') == (OUT / 'candidate.yaml').read_bytes()
    old = OUT.parent
    manifest = read(old / 'artifact-manifest.json')
    frozen = {}
    for name, expected in manifest['published_files'].items():
        assert sha(old / name) == expected, name
        frozen[str((old / name).relative_to(ROOT))] = expected
    for name, expected in manifest['python_models'].items():
        assert sha(ROOT / name) == expected, name
        frozen[name] = expected
    frozen[str((old / 'artifact-manifest.json').relative_to(ROOT))] = sha(old / 'artifact-manifest.json')
    source_provenance = {
        'schema': 'gota-source-reveal-provenance/1', 'opponent_uuid': VERSION,
        'opponent_name': 'richard-gods-of-the-arena', 'opponent_version': 135,
        'repository': str(REPO), 'repository_url': 'https://github.com/Metta-AI/co-gas',
        'requested_commit': COMMIT, 'original_source_commit': ORIGINAL,
        'source_path': SOURCE, 'source_sha256': SOURCE_SHA,
        'requested_diff_path': 'docs/gota-policy-handoff.md',
        'requested_diff_path_sha256': hashlib.sha256(b'docs/gota-policy-handoff.md').hexdigest(),
        'candidate_manifest_path': 'experiments/candidates/gods-of-the-arena-neural-siege-counter-20260920.yaml',
        'candidate_manifest_sha256': sha(OUT / 'candidate.yaml'),
        'source_identical_at_both_commits': True,
        'game_commit': 'f2ab9598d8f8001b6beae3e66404e341770c803f', 'game_version': '2026.9.16.5',
        'game_source_sha256': {name: sha(GAME / 'examples/gods_of_the_arena' / name) for name in ['sim.nim', 'content.nim', 'bots.nim']},
        'original_frozen_artifacts_verified_unchanged': frozen,
        'scope': 'Post-source-reveal audit. Original fit/holdout and guide remain unchanged. New probes are not blind observations.'}
    write(OUT / 'provenance.ir.json', source_provenance)
    history = git_bytes(COMMIT, 'docs/gota-policy-handoff.md').decode()
    start, end = history.index('### Red Kite combat deficit:'), history.index('### Siege-primary diagnostic:')
    (OUT / 'ranger-history-excerpt.md').write_text(
        '# Historical Ranger research, pinned source excerpt\n\n'
        f'Extracted verbatim from `docs/gota-policy-handoff.md` at co-gas commit `{COMMIT}`. '
        'These are the source author’s reports about predecessors v115/v122/v123 and other matchups, not new v135 experiment results. '
        'The current audit independently measures v135 purchases, rewards and hit cadence.\n\n' + history[start:end])

    runtime = read(OUT / 'runtime-audit.ir.json')
    fixtures = read(OUT / 'discriminating-fixtures.ir.json')
    economy = read(OUT / 'economy-audit.ir.json')
    assert runtime['episodes'] == economy['episodes'] == 20
    assert fixtures['all_assertions_passed'] and fixtures['scenes'] == 12
    counts = runtime['counts']

    def node(i, lines, skill, when, effects, goals, observed=None, tests=()):
        return {'id': f'Richard135_M{i:02}', 'source_lines': lines, 'skill': skill,
                'when': when, 'effects': effects, 'for': goals,
                'evidence_status': 'source_verified',
                'runtime_count': observed, 'fixture_ids': list(tests)}

    nodes = [
        node(1, [1, 126], 'scan_and_encode', 'every living decision',
             {'nearest_generic': 'living/exposed hostile any kind; strict distance tie',
              'nearest_objective_kinds': [1, 4], 'nearest_hero_kind': 2,
              'siege_threat': 'lowest HP visible hero targeting self within self basic range',
              'ally_geometry': ['centroid', 'maximum squared self distance', 'opening rally count'],
              'features': {'count': 25, 'clamp': [-100, 100], 'inputs': ['self HP percent', 'self mana percent', 'max ally squared distance / 100', 'level * 5', 'ally and nearest enemy offsets mirrored on blue', 'nearest enemy HP / 10', 'nearest enemy kind * 25', 'worldTick / 288', 'four ability charges * 25', 'ten class indicators * 100']}},
             ['perception'], runtime['decisions']),
        node(2, [127, 293], 'select_cached_neural_mode', 'decrement countdown; recompute iff <= 0',
             {'network': {'inputs': 25, 'hidden_relu': 16, 'outputs': 18, 'selection': 'argmax with strict > updates'},
              'clock': {'unit': 'living VM decisions', 'period': 4, 'reset_value': 4},
              'decode': {'combat': 'decision mod 9', 'equipment': 'int(decision >= 9)'},
              'weights': {'artifact': 'v135.bas', 'sha256': SOURCE_SHA}},
             ['mode_selection_unknown_objective'], counts['neural_recompute'], ['neural_four_decision_clock']),
        node(3, [295, 309], 'latch_group_departure',
             'tick < 3500 AND routeFallback AND allies_within_rally_radius4 >= 3 AND self_within_rally_radius4',
             {'groupDeparture': 1, 'reset': 'no explicit source reset',
              'routeFallback': '(combat==2 OR (combat==8 AND bestId==0)) AND no objective at squared distance<=300 AND no hero at squared distance<=700',
              'rally': {'red': [71, 12], 'blue': [45, 104]}}, ['coordinated_departure_hypothesis']),
        node(4, [311, 352], 'base_attack_or_route', 'every living decision',
             {'mode8': ['nearest objective if distance2<=300', 'nearest hero if distance2<=700', 'nearest generic enemy', 'route'],
              'other_modes': ['nearest generic enemy', 'walkTo(64,64)'],
              'route': {'before_3500_unlatched': {'red': [71,12], 'blue': [45,104]},
                        'before_4500_otherwise': {'red': [9,33], 'blue': [107,83]},
                        'later': {'red': [11,106], 'blue': [105,10]}}}, ['contact_hypothesis', 'objective_pressure_hypothesis']),
        node(5, [354, 359], 'lich_midpoint_ring', 'class==7 AND nearest hero targets self AND 25<hero_distance2<=49',
             {'request': 'castPoint(3, midpoint(self,nearestHero))', 'success': 'host-dependent; no explicit charge guard'},
             ['intercept_hypothesis'], counts.get('command_kind_13', 0)),
        node(6, [361, 516], 'consume_and_purchase', 'every living decision; equipment requires observed empty slot',
             {'heal_use_below_hp_fraction': 0.6, 'heal_buy_below_hp_fraction': 0.5,
              'heal_purchase_attempt_order': [{'item':2,'cost':50}, {'item':1,'cost':30}],
              'objective_equipment': [{'item':11,'cost':110}, {'item':13,'cost':150}, {'item':16,'cost':160}, {'item':18,'cost':180}, {'item':20,'cost':190}],
              'objective_equipment_class_filter': None,
              'normal_ranged_classes': [1,6], 'normal_ranged_gear': [8,14,19],
              'normal_melee_classes': [0,4,5,9], 'normal_magic_classes': [2,3,7,8],
              'normal_only': ['mana potion use/purchase', 'poison use/purchase', 'class-specific equipment'],
              'affordability': 'source data is a predecision snapshot; each host call checks live gold/capacity',
              'ordering': 'multiple independent if checks; no guaranteed one-purchase limit or savings plan'},
             ['survival_hypothesis', 'damage_growth_hypothesis'], counts['command_kind_3']),
        node(7, [517, 564], 'apply_mode_override', 'combat in 1..7',
             {'1': 'walk home corner', '2': 'objective<=300 then hero<=700 else route; no generic-enemy fallback here',
              '3..6': 'castTarget(combat-3, bestId else selfId)', '7': 'walk ally centroid'},
             ['mode_selection_unknown_objective'], None, ['structure_context_tower', 'structure_context_barracks']),
        node(8, [566, 570], 'answer_siege_attacker',
             'combat in {2,8} AND objectiveKind==4 AND objectiveDistance2<=300 AND siegeThreatId!=0',
             {'request': 'attackTarget(siegeThreatId)', 'priority': 'after mode override, before home defense/recovery'},
             ['self_preservation_hypothesis'], counts.get('siege_counter_guard_true',0),
             ['siege_quiet','siege_attacker_targets_self','siege_attacker_targets_other_ally','siege_attacker_outside_range','siege_god_is_not_tower','siege_lowest_hp_eligible_attacker']),
        node(9, [572, 659], 'reserve_home_defender',
             'home observed standing AND (guards<=1 OR (guardHP<=390 AND selfHomeDistance2<=900)) AND no strictly closer living ally AND NOT in-range one-hit enemy-fort finish',
             {'guard_radius2':100, 'intruder_radius2':400, 'attack_if_self_home_distance2_at_most':400,
              'target_order':['direct fort attacker (hero or creep)', 'nearest enemy hero', 'nearest enemy hero or creep'],
              'otherwise':'walkTo(home)', 'ties':'multiple equal-distance candidates may reserve',
              'priority':'overrides siege/mode locomotion; can be followed by recovery walk'},
             ['home_preservation_hypothesis'], counts['home_reservation_guard_true'],
             ['home_direct_creep_over_hero','home_closer_ally_removes_self_reservation']),
        node(10, [661, 666], 'end_post_hit_recovery', 'initialized AND selfAttacksLanded > previous landed hits',
             {'request':'walkTo(selfX,selfY)', 'update':'save hit count; initialized=1',
              'priority':'last locomotion command', 'effect_scope':'after confirmed hit; not an unconditional per-tick movement'},
             ['attack_cadence_hypothesis'], counts['hit_recovery_walk'], ['one_decision_hit_recovery_pulse'])]
    goals = {g: {'provenance': 'purpose hypothesis; source/runtime establish operations, not optimality'} for n in nodes for g in n['for']}
    source_model = {
        'schema':'gota-source-policy-audit/1', 'id':'richard_v135_source_reveal_20260920',
        'situation': {'grounded': {'version': VERSION, 'perspective':'each Richard VM host-visible observation',
            'coordinates':'integer map tiles; squared distances; world scale 60000 per tile',
            'object_kinds':{'god':1,'hero':2,'creep':3,'tower':4,'barracks':5},
            'structures':'objectAlive means exposed; positive HP means standing',
            'range_comparison':'distance2*3600 <= (selfAttackRange/1000)^2',
            'observability':'source audit sees private VM memory retrospectively; own deployed policy cannot read it'}},
        'belief': {'grounded': {'evidence_regime':'source_revealed', 'source_sha256':SOURCE_SHA,
            'original_observation_model_unchanged':True, 'learned_modes_observed':{'0':counts['combat_0'],'2':counts['combat_2'],'6':counts['combat_6']},
            'equipment_modes_observed':{'1':counts['build_1']}, 'unexercised_defining_patch': 'Richard135_M08'},
            'claims': {n['id']:{'claim':n['skill'], 'status':'source_verified', 'evidence':[{'lines':n['source_lines'],'runtime_count':n['runtime_count'],'fixture_ids':n['fixture_ids']}]} for n in nodes}},
        'goal': goals,
        'skill': {n['skill']: {k:v for k,v in n.items() if k not in ['for','when']} for n in nodes},
        'strategy': [{k:n[k] for k in ['id','when','skill','for']} | {'source_order':i} for i,n in enumerate(nodes)],
        'execution': {'binding':'gota-source-audit-description/1', 'compilable':False,
            'semantic_reimplementation_validated':False, 'authentic_source':'v135.bas',
            'command_composition':'ordered requests across locomotion, spells and inventory; host applies acceptance live',
            'control_edges':[{'earlier':a,'later':b,'meaning':'later locomotion request can supersede earlier attack/movement'} for a,b in [('Richard135_M04','Richard135_M07'),('Richard135_M07','Richard135_M08'),('Richard135_M08','Richard135_M09'),('Richard135_M09','Richard135_M10')]],
            'persistent_state':['decision','neuralActionCountdown','groupDeparture','recoveryInitialized','recoveryLastHit'],
            'xp_mechanics':{'source':'pinned simulator, not opponent command', 'kill_rewards':{'creep':[25,15],'hero':[150,100],'building':[100,75]},
                'reward_pair_units':['xp','gold'],'level_threshold':'100+75*(current_level-1)','max_level':20,'explicit_level_up_command':False},
            'validation':{'exact_replay_commands':runtime['commands_matched'],'games':20,'fixtures':12,'fixture_decisions':21,
                'new_counter_policy_games':0,'proxy_usable':False}},
        'update': {'revision':1,'parent':'richard_v135_observer_model', 'relation':'separate source audit; original model not revised',
            'evidence':['provenance.ir.json','runtime-audit.ir.json','discriminating-fixtures.ir.json','economy-audit.ir.json'],
            'limitations':['same-corpus reconstruction is not fresh prediction','guard counts can be suppressed by later commands','synthetic host acceptance is not combat efficacy','semantic description is not compiled equivalent source']}}
    write(OUT / 'source-model.ir.json', source_model)

    sys.path.insert(0, str(ROOT / 'examples/gods_of_the_arena/players/ir'))
    import opponent_ir
    model = opponent_ir.load(ROOT / 'examples/gods_of_the_arena/players/ir/opponents/richard_v135.py')
    assessments = {
        'O03': ('compatible_coarse_forecast', ['M04','M07','M09'], 'Nearest target and mode/defense selection can explain contact; not a global hero preference.'),
        'O04': ('compatible_sparse_forecast', ['M02','M06','M07'], 'Absolute HP<=100 is not the source health threshold; 3 heldout events do not identify low-HP intent.'),
        'O15': ('coarse_context_mechanistically_insufficient', ['M07','M08','M09'], 'Paired mask-7 scenes keep old context fixed but change terminal target with attacker target.'),
        'O13': ('compatible_but_structure_kind_overbroad', ['M01','M07'], 'Tower/god objective selection excludes barracks; mask-6 tower and barracks fixtures diverge.'),
        'O09': ('compatible_without_individual_lift', ['M04','M07'], 'Both generic and objective selection can produce the behavior; preserve provisional status.'),
        'O06': ('unsupported_holding_mechanism', ['M02','M06','M10'], '0/3 heldout; no absolute-HP-100 hold rule. Source does not prove voluntary holding.'),
        'O11': ('coarse_context_mechanistically_insufficient', ['M07','M08','M09'], 'Hero-versus-structure priority depends on missing guards and mode; no lift over population.'),
        'O05': ('compatible_without_goal_identification', ['M04','M07'], 'Generic nearest-creep contact does not identify farming or last-hit optimization.'),
        'O07': ('compatible_without_goal_identification', ['M04','M09'], 'Generic nearest selection or direct fort-attacker priority can select a creep; no global preference.')}
    comparisons=[]
    for rule in model['strategy']:
        pref=model['belief']['claims'][rule['id']]['evidence'][0]
        assessment,mechanisms,why=assessments[rule['id'].split('_')[-1]]
        comparisons.append({'id':rule['id'],'original_rule':rule,'original_preference':pref,
            'audit_status':assessment,'source_mechanisms':['Richard135_'+m for m in mechanisms],
            'reason':why,'original_status_changed':False})
    write(OUT / 'comparison.ir.json', {'schema':'gota-opponent-source-comparison/1',
        'observation_model_sha256':sha(ROOT / 'examples/gods_of_the_arena/players/ir/opponents/richard_v135.py'),
        'source_sha256':SOURCE_SHA,'claim_comparisons':comparisons,
        'original_forecast':{'individual':[694,923],'population':[502,923],'target':'motif at retrospectively known >=6-tick starts','heldout_stream_clusters':3},
        'new_discriminators':'discriminating-fixtures.ir.json','source_runtime':'runtime-audit.ir.json',
        'identified_omissions':['four-decision neural mode cache','ordered multi-command composition','structure-kind distinction','tower-only self-attacker correction','group departure latch','nearest home defender with ties','post-hit recovery','accepted purchases and automatic kill-reward leveling'],
        'main_limit':'Coarse observable forecast remains useful; mechanism and counterfactual fidelity were not established.'})

    candidates = [
        ('C01','preserve_blue_and_repair_red_engagement',['M04','M09'], 'blue_prior_validated_red_repair_proposed',
         'Friendly defense commitment or unsupported red engagement observed',
         'Preserve validated blue critical defense; test one bounded red entry/support change',
         ['contributing allies','damage conversion','avoidable deaths','defender arrival','per-color wins'],
         'Same deaths delayed, defense stall, or regression to blue/field'),
        ('C02','coordinated_tower_siege_attractor',['M08'], 'opponent_branch_fixture_verified_counter_proposed',
         'Visible Richard hero sieging exposed friendly tower; own healthy actor can attack within Richard range',
         'One healthy actor attracts retaliation with allied damage support',
         ['guard opportunities','observed retargets','tower damage prevented','attractor deaths','per-color wins'],
         'Rare activation, attacker killed faster, or no tower/match benefit'),
        ('C03','home_defender_diversion',['M09'], 'opponent_branch_fixture_verified_counter_proposed',
         'Public Richard home-guard loss/critical state and visible intruder opportunity',
         'Compare timed second-angle pressure during an observed nearest-defender return',
         ['defender allocation','return time','fort damage','own core exposure','wins'],
         'Diversion consolidates defense or costs more resources than it gains'),
        ('C04','measure_before_timing_exploitation',['M02','M05','M10'], 'diagnostic_only',
         'Visible hit/cast/approach events in a losing engagement',
         'Measure cadence and ring impacts before changing approach or recovery',
         ['hit intervals','range uptime','accepted spell effects','damage taken','survival'],
         'No actual exploitable window or movement cancels own windups'),
        ('C05','prevent_ranger_hero_kill_snowball',['M06','M10'], 'source_and_replay_diagnosis_counter_proposed',
         'Visible early Ranger with limited equipment and a supported engagement opportunity',
         'Test bounded coordinated pressure and fewer repeated isolated hero deaths',
         ['accepted purchases','kill-reward sources','level milestones','potion spending','actual basic cadence','own XP','terminal wins'],
         'Early XP gain disappears, own farm/core sacrificed, or Ranger catches up and wins')]
    write(OUT / 'counter-hypotheses.ir.json', {'schema':'gota-source-informed-counter-hypotheses/1',
        'opponent_uuid':VERSION,'source_sha256':SOURCE_SHA,'created_from':'source_model_and_archived_counter_results',
        'execution':{'binding':'proposals-only','compilable':False,'deployed':False,'new_xp_requests':0,'all_new_counter_effects_require_responsive_tests':True},
        'strategy':[{'id':'Richard135_'+i,'when':when,'skill':skill,'for':['improve_individual_and_team_play','win_both_colors'],
            'status':status,'source_mechanisms':['Richard135_'+m for m in ms],'intervention':action,
            'metrics':metrics,'reject_if':reject,'observability':'own-policy public host fields and permitted memory; no private Richard mode input'}
            for i,skill,ms,status,when,action,metrics,reject in candidates],
        'prior_evidence':{'blue_component':{'wins':40,'games':40,'source_sha256':'d157d54aef9dc47f9d1a75a4f7216a76a3b63bb89688232b8ab6640a6b2f7140'},
            'red_combined_final':{'wins':0,'games':40,'losses':39,'draws':1},
            'cohort_invalid_red_games':40,'bounded_candidate_instruction_gate_failure':19105},
        'validation_plan':{'local':'exact authentic Richard source with all ten VMs responding',
            'hosted':'fresh candidate/control XP, exact UUID, both colors; preserve already frozen session gates',
            'historical_gate':{'richard_min_wins_per_40_each_color':30,'combined_win_gain':8,'jordan_min_wins_per_40_each_color':38,
                'field_opponents':['relh154','g002v1','black-kite16','macro4','red-kite34','vanguard1'],'field_screen_per_color':8},
            'runtime':{'max_instructions':20000,'max_work':50000,'historical_local_instruction_margin_gate':19000},
            'independence':'report distinct trajectories; repeated fixed-roster games are not independent trials'},
        'evidence':['counter-policy-guide.md','ranger-economy.md','economy-audit.ir.json','discriminating-fixtures.ir.json']})
    rangers=[(r,h) for r in economy['rows'] for h in r['heroes'] if h['class']=='Ranger' and h['policy']=='richard_v135']
    signatures={hashlib.sha256(json.dumps(h,sort_keys=True).encode()).hexdigest() for r,h in rangers}
    h=rangers[0][1]
    write(OUT / 'ranger-economy-summary.ir.json', {'schema':'gota-source-ranger-economy/1',
        'class_id':1,'games':len(rangers),'distinct_published_ranger_traces':len(signatures),
        'representative_episode':rangers[0][0]['episode'], 'source_model_mechanisms':['Richard135_M06','Richard135_M10'],
        'first_reward_tick':h['first_reward_tick'],'accepted_first_item_ticks':h['first_item_ticks'],
        'level_transitions':[{'tick':t['tick'],'level':t['hero']['level']} for t in h['level_changes']],
        'xp_by_source':{k:v*{'creep':25,'hero':150,'building':100}[k] for k,v in h['reward_counts'].items()},
        'reward_counts':h['reward_counts'],'final':h['final'],'deaths':h['deaths'],
        'hero_basic_interval_histogram':h['same_target_hero_hit_interval_counts'],
        'interval_scope':'Consecutive hero-target basic hits on same target; not continuously in-range opportunity counts',
        'richard_accepted_purchase_counts':dict(Counter(p['item'] for r in economy['rows'] for hero in r['heroes'] if hero['policy']=='richard_v135' for p in hero['accepted_purchases'])),
        'interpretation':'One repeated Ranger trace: delayed initial income, later hero-kill XP majority, observed nine-tick cadence. No counter-policy experiment yet.'})
    print(f'Published source IR, {len(comparisons)} comparisons, {len(candidates)} counter hypotheses; verified {len(frozen)} frozen artifacts unchanged.')


if __name__ == '__main__':
    main()
