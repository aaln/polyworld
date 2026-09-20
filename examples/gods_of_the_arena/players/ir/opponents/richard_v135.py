"""Counted observer-only opponent model in the primary seven-layer Python IR.
No private source; not an executable or validated rollout proxy.
"""

MODEL = {'schema': 'gota-semantic-opponent/1',
 'id': 'richard_v135_individual_observer_model',
 'situation': {'grounded': {'observation': 'One real own slot0/5 at its predecision moment. Motif at t must '
                                           'persist 6 ticks; predictors use only t-1.',
                            'predicates': {'mask_1_low_0': 'nearby=our hero; no nearby creep/exposed '
                                                           'structure; visible HP >100',
                                           'mask_1_low_1': 'nearby=our hero; no nearby creep/exposed '
                                                           'structure; visible HP ≤100',
                                           'mask_2_low_0': 'nearby=our creep; no nearby hero/exposed '
                                                           'structure; visible HP >100',
                                           'mask_2_low_1': 'nearby=our creep; no nearby hero/exposed '
                                                           'structure; visible HP ≤100',
                                           'mask_3_low_0': 'nearby=our hero + our creep; no nearby exposed '
                                                           'structure; visible HP >100',
                                           'mask_4_low_0': 'nearby=our exposed structure; no nearby '
                                                           'hero/creep; visible HP >100',
                                           'mask_5_low_0': 'nearby=our hero + our exposed structure; no '
                                                           'nearby creep; visible HP >100',
                                           'mask_6_low_0': 'nearby=our creep + our exposed structure; no '
                                                           'nearby hero; visible HP >100',
                                           'mask_7_low_0': 'nearby=our hero + our creep + our exposed '
                                                           'structure; visible HP >100'},
                            'glossary_extensions': {'target_hero': 'Visible target identifies a living '
                                                                   'hostile hero; pursuit/retained target, '
                                                                   'not proof of an attack or kill.',
                                                    'target_creep': 'Visible target identifies a living '
                                                                    'hostile footman; pursuit/retained '
                                                                    'target, not proof of farming or last '
                                                                    'hits.',
                                                    'target_structure': 'Visible target identifies a '
                                                                        'positive-HP exposed hostile tower, '
                                                                        'barracks or god; not proof of '
                                                                        'damage.',
                                                    'advance': 'Without a valid visible target, velocity '
                                                               'points toward our god (radial cosine >0.35). '
                                                               'Relative geometry, not inferred destination.',
                                                    'withdraw': 'Without a valid visible target, velocity '
                                                                'points away from our god (radial cosine '
                                                                '<-0.35). Not proof of retreat to safety.',
                                                    'lateral': 'Without a valid visible target, velocity is '
                                                               'neither advancing nor withdrawing by the '
                                                               'radial thresholds.',
                                                    'hold': 'Without a valid visible target, speed <1000 '
                                                            'world units/tick. Can include turning, '
                                                            'collision or hidden target; voluntary waiting '
                                                            'unproven.'},
                            'structure_semantics': 'For structures alive means exposed; HP>0 means standing. '
                                                   'Target0 means none OR hidden.'},
               'notes': 'Forecast visible motifs; do not infer executable opponent source rules, rule order, '
                        'or a single-rule-per-tick policy. Movement remains a simultaneous qualifier.'},
 'belief': {'grounded': {'level': 'individual',
                         'opponent_version': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                         'opponent_label': 'richard-gods-of-the-arena:v135',
                         'our_policy': {'directory': '/Users/aaln/experiments/softmax/polyworld/examples/gods_of_the_arena/players/ir/forks/jordan268',
                                        'id': 'gota_jordan268_redrace',
                                        'basic_sha256': 'be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73',
                                        'ir_file_sha256': 'dbb2dbe273e02c047afcf674af4a73117abab278a6af362238879ee77ae2ddb2',
                                        'versions': ['00cd9483-0309-4613-bf61-89f3f4a33d01',
                                                     '4cdbbf36-3d70-4ea3-8aed-c92ee0e024be']},
                         'predictor': {'contexts': {'mask_1_low_0': {'target_hero': 357},
                                                    'mask_1_low_1': {'target_hero': 8},
                                                    'mask_2_low_0': {'target_creep': 270,
                                                                     'lateral': 8,
                                                                     'hold': 21,
                                                                     'withdraw': 14,
                                                                     'advance': 21},
                                                    'mask_2_low_1': {'hold': 7},
                                                    'mask_3_low_0': {'target_creep': 339, 'target_hero': 314},
                                                    'mask_4_low_0': {'target_structure': 564, 'advance': 14},
                                                    'mask_5_low_0': {'target_hero': 67,
                                                                     'target_structure': 15},
                                                    'mask_6_low_0': {'target_creep': 238,
                                                                     'target_structure': 338,
                                                                     'advance': 7},
                                                    'mask_7_low_0': {'target_hero': 14,
                                                                     'hold': 4,
                                                                     'advance': 4}},
                                       'global': {'target_creep': 847,
                                                  'target_structure': 917,
                                                  'target_hero': 760,
                                                  'lateral': 8,
                                                  'hold': 32,
                                                  'advance': 46,
                                                  'withdraw': 14},
                                       'smoothing': 'Laplace +1 over estimated available skills; context '
                                                    'backs off globally if n<8'},
                         'skills': {'target_hero': {'n': 893,
                                                    'episodes': 11,
                                                    'ticks': 15472,
                                                    'initiation_contexts': {'mask_3_low_0': 392,
                                                                            'mask_1_low_0': 388,
                                                                            'mask_1_low_1': 12,
                                                                            'mask_2_low_0': 12,
                                                                            'mask_5_low_0': 73,
                                                                            'mask_7_low_0': 16},
                                                    'termination': {'visible_target_change': 813,
                                                                    'visibility_lost_or_not_alive': 52,
                                                                    'observer_dead': 28},
                                                    'left_censored': 121,
                                                    'median_duration_ticks': 12,
                                                    'outcome_hp_change_median': 0,
                                                    'concurrent_movement_ticks': {'advance': 5645,
                                                                                  'lateral': 791,
                                                                                  'hold': 8702,
                                                                                  'withdraw': 334},
                                                    'prediction': {'actual_n': 254,
                                                                   'predicted_n': 158,
                                                                   'recall': 0.5984251968503937,
                                                                   'precision': 0.9620253164556962},
                                                    'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1364'},
                                    'target_creep': {'n': 1052,
                                                     'episodes': 11,
                                                     'ticks': 13725,
                                                     'initiation_contexts': {'mask_2_low_0': 391,
                                                                             'mask_6_low_0': 267,
                                                                             'mask_3_low_0': 392,
                                                                             'mask_2_low_1': 2},
                                                     'termination': {'visible_target_change': 916,
                                                                     'visibility_lost_or_not_alive': 136},
                                                     'left_censored': 205,
                                                     'median_duration_ticks': 11.0,
                                                     'outcome_hp_change_median': 0.0,
                                                     'concurrent_movement_ticks': {'advance': 5223,
                                                                                   'hold': 6719,
                                                                                   'lateral': 918,
                                                                                   'withdraw': 865},
                                                     'prediction': {'actual_n': 284,
                                                                    'predicted_n': 332,
                                                                    'recall': 0.7077464788732394,
                                                                    'precision': 0.6054216867469879},
                                                     'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t624'},
                                    'target_structure': {'n': 978,
                                                         'episodes': 11,
                                                         'ticks': 15261,
                                                         'initiation_contexts': {'mask_6_low_0': 338,
                                                                                 'mask_4_low_0': 602,
                                                                                 'mask_5_low_0': 27,
                                                                                 'mask_2_low_0': 11},
                                                         'termination': {'visible_target_change': 891,
                                                                         'visibility_lost_or_not_alive': 69,
                                                                         'observer_dead': 4,
                                                                         'episode_end': 14},
                                                         'left_censored': 50,
                                                         'median_duration_ticks': 10.0,
                                                         'outcome_hp_change_median': 0.0,
                                                         'concurrent_movement_ticks': {'hold': 10271,
                                                                                       'advance': 4321,
                                                                                       'lateral': 474,
                                                                                       'withdraw': 195},
                                                         'prediction': {'actual_n': 345,
                                                                        'predicted_n': 433,
                                                                        'recall': 0.9884057971014493,
                                                                        'precision': 0.7875288683602771},
                                                         'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1039'},
                                    'advance': {'n': 132,
                                                'episodes': 11,
                                                'ticks': 9410,
                                                'initiation_contexts': {'mask_2_low_0': 100,
                                                                        'mask_7_low_0': 4,
                                                                        'mask_6_low_0': 14,
                                                                        'mask_4_low_0': 14},
                                                'termination': {'movement_character_change': 29,
                                                                'visible_target_change': 77,
                                                                'visibility_lost_or_not_alive': 26},
                                                'left_censored': 78,
                                                'median_duration_ticks': 52.0,
                                                'outcome_hp_change_median': 0.0,
                                                'concurrent_movement_ticks': {'advance': 9410},
                                                'prediction': {'actual_n': 19,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h105.t4561'},
                                    'withdraw': {'n': 14,
                                                 'episodes': 7,
                                                 'ticks': 406,
                                                 'initiation_contexts': {'mask_2_low_0': 14},
                                                 'termination': {'visibility_lost_or_not_alive': 14},
                                                 'left_censored': 0,
                                                 'median_duration_ticks': 29.0,
                                                 'outcome_hp_change_median': 0.0,
                                                 'concurrent_movement_ticks': {'withdraw': 406},
                                                 'prediction': {'actual_n': 6,
                                                                'predicted_n': 0,
                                                                'recall': 0.0,
                                                                'precision': None},
                                                 'example': 'ereq_e766eb57-1ad0-4546-80a5-bdd686a83c94.h103.t1660'},
                                    'lateral': {'n': 15,
                                                'episodes': 11,
                                                'ticks': 1162,
                                                'initiation_contexts': {'mask_2_low_0': 15},
                                                'termination': {'movement_character_change': 8,
                                                                'observer_dead': 7},
                                                'left_censored': 7,
                                                'median_duration_ticks': 104,
                                                'outcome_hp_change_median': 0,
                                                'concurrent_movement_ticks': {'lateral': 1162},
                                                'prediction': {'actual_n': 2,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h105.t4653'},
                                    'hold': {'n': 32,
                                             'episodes': 11,
                                             'ticks': 611,
                                             'initiation_contexts': {'mask_7_low_0': 4,
                                                                     'mask_2_low_0': 21,
                                                                     'mask_2_low_1': 7},
                                             'termination': {'movement_character_change': 25,
                                                             'visibility_lost_or_not_alive': 7},
                                             'left_censored': 0,
                                             'median_duration_ticks': 8.0,
                                             'outcome_hp_change_median': 0.0,
                                             'concurrent_movement_ticks': {'hold': 611},
                                             'prediction': {'actual_n': 13,
                                                            'predicted_n': 0,
                                                            'recall': 0.0,
                                                            'precision': None},
                                             'example': 'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t7862'}},
                         'validation': {'n': 923,
                                        'correct': 694,
                                        'accuracy': 0.7518959913326111,
                                        'population_correct': 502,
                                        'population_accuracy': 0.5438786565547129,
                                        'persistence_accuracy': 0.1570964247020585,
                                        'uniform_expected_accuracy': 0.18545374812980447,
                                        'cluster_uncertainty': {'clusters': 3,
                                                                'lift_95pct': [0.09375, 0.26066350710900477],
                                                                'method': '2000 bootstrap resamples of '
                                                                          'distinct full observer '
                                                                          'trajectories; descriptive with '
                                                                          'few clusters'},
                                        'novel_trajectories': {'n': 422,
                                                               'correct': 322,
                                                               'accuracy': 0.7630331753554502,
                                                               'population_correct': 212,
                                                               'population_accuracy': 0.5023696682464455,
                                                               'persistence_accuracy': 0.14691943127962084,
                                                               'uniform_expected_accuracy': 0.18428120063191153},
                                        'novel_episode_ids': ['ereq_74cd8109-1bf0-4eed-b095-0345eb0a774c',
                                                              'ereq_c2cfaf27-ac5d-4efb-8f2c-e929db3432d9'],
                                        'robustness_baselines': {'class': {'correct': 461,
                                                                           'n': 923,
                                                                           'accuracy': 0.49945828819068255,
                                                                           'by_context': {'mask_2_low_1': {'correct': 0,
                                                                                                           'n': 3},
                                                                                          'mask_6_low_0': {'correct': 83,
                                                                                                           'n': 226},
                                                                                          'mask_7_low_0': {'correct': 0,
                                                                                                           'n': 6},
                                                                                          'mask_5_low_0': {'correct': 15,
                                                                                                           'n': 21},
                                                                                          'mask_4_low_0': {'correct': 137,
                                                                                                           'n': 207},
                                                                                          'mask_2_low_0': {'correct': 80,
                                                                                                           'n': 106},
                                                                                          'mask_1_low_0': {'correct': 19,
                                                                                                           'n': 128},
                                                                                          'mask_1_low_1': {'correct': 0,
                                                                                                           'n': 3},
                                                                                          'mask_3_low_0': {'correct': 127,
                                                                                                           'n': 223}}},
                                                                 'side': {'correct': 597,
                                                                          'n': 923,
                                                                          'accuracy': 0.6468039003250271,
                                                                          'by_context': {'mask_2_low_1': {'correct': 0,
                                                                                                          'n': 3},
                                                                                         'mask_6_low_0': {'correct': 83,
                                                                                                          'n': 226},
                                                                                         'mask_7_low_0': {'correct': 0,
                                                                                                          'n': 6},
                                                                                         'mask_5_low_0': {'correct': 17,
                                                                                                          'n': 21},
                                                                                         'mask_4_low_0': {'correct': 201,
                                                                                                          'n': 207},
                                                                                         'mask_2_low_0': {'correct': 80,
                                                                                                          'n': 106},
                                                                                         'mask_1_low_0': {'correct': 95,
                                                                                                          'n': 128},
                                                                                         'mask_1_low_1': {'correct': 0,
                                                                                                          'n': 3},
                                                                                         'mask_3_low_0': {'correct': 121,
                                                                                                          'n': 223}}}},
                                        'by_episode': {'ereq_38c2dfb5-a988-4ac1-81ef-2226fa9b205a': {'n': 213,
                                                                                                     'correct': 164,
                                                                                                     'accuracy': 0.7699530516431925,
                                                                                                     'population_correct': 109,
                                                                                                     'population_accuracy': 0.5117370892018779,
                                                                                                     'persistence_accuracy': 0.1596244131455399,
                                                                                                     'uniform_expected_accuracy': 0.18427230046948356},
                                                       'ereq_74cd8109-1bf0-4eed-b095-0345eb0a774c': {'n': 211,
                                                                                                     'correct': 161,
                                                                                                     'accuracy': 0.7630331753554502,
                                                                                                     'population_correct': 106,
                                                                                                     'population_accuracy': 0.5023696682464455,
                                                                                                     'persistence_accuracy': 0.14691943127962084,
                                                                                                     'uniform_expected_accuracy': 0.18428120063191153},
                                                       'ereq_5cb288d2-608c-4ad5-aec9-22c5eedfaed0': {'n': 288,
                                                                                                     'correct': 208,
                                                                                                     'accuracy': 0.7222222222222222,
                                                                                                     'population_correct': 181,
                                                                                                     'population_accuracy': 0.6284722222222222,
                                                                                                     'persistence_accuracy': 0.1701388888888889,
                                                                                                     'uniform_expected_accuracy': 0.18804563492063492},
                                                       'ereq_c2cfaf27-ac5d-4efb-8f2c-e929db3432d9': {'n': 211,
                                                                                                     'correct': 161,
                                                                                                     'accuracy': 0.7630331753554502,
                                                                                                     'population_correct': 106,
                                                                                                     'population_accuracy': 0.5023696682464455,
                                                                                                     'persistence_accuracy': 0.14691943127962084,
                                                                                                     'uniform_expected_accuracy': 0.18428120063191153}},
                                        'by_observer_side': {'0': {'n': 288,
                                                                   'correct': 208,
                                                                   'accuracy': 0.7222222222222222,
                                                                   'population_correct': 181,
                                                                   'population_accuracy': 0.6284722222222222,
                                                                   'persistence_accuracy': 0.1701388888888889,
                                                                   'uniform_expected_accuracy': 0.18804563492063492},
                                                             '5': {'n': 635,
                                                                   'correct': 486,
                                                                   'accuracy': 0.7653543307086614,
                                                                   'population_correct': 321,
                                                                   'population_accuracy': 0.5055118110236221,
                                                                   'persistence_accuracy': 0.15118110236220472,
                                                                   'uniform_expected_accuracy': 0.18427821522309712}}},
                         'observability': {'episodes': 20,
                                           'ticks': 132344,
                                           'living_opponent_ticks': 600830,
                                           'visible_living_opponent_ticks': 110180,
                                           'fraction': 0.1833796581395736,
                                           'all_scheduled_hero_tick_fraction': 0.16650547059179108,
                                           'observer_dead_fraction': 0.1463005500816055,
                                           'residual_fraction': 0.10024505354873843,
                                           'segments': 5552,
                                           'eligible': 4678,
                                           'exclusions': {'left_censored': 820,
                                                          'selected_skill_not_established_by_prior_affordances': 54}},
                         'proxy': {'usable': False,
                                   'rollouts': 0,
                                   'divergence': None,
                                   'reason': 'No executable skill controller or rollout validation. '
                                             'Boundary-conditional prediction alone cannot qualify a proxy.',
                                   'proposed_gate': {'skill_frequency_total_variation_max': 0.1,
                                                     'position_histogram_total_variation_max': 0.15,
                                                     'win_rate_absolute_gap_max': 0.1,
                                                     'note': 'Proposed future gate on novel seeds, both '
                                                             'sides; not tested or a certification.'}},
                         'second_order_beliefs': {'n': 0,
                                                  'confidence': None,
                                                  'predictions': 0,
                                                  'inferred': False},
                         'uncertainty': 'Partial visibility, estimated affordances, correlated trajectories '
                                        'and retrospective boundaries; absence is not death. Source memory, '
                                        'private cooldowns and hidden observations are unavailable.'},
            'claims': {'Richard135_I_O03': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                     'structure; visible HP >100 THEY PREFER target_hero '
                                                     'OVER hold FOR hero_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'Richard135_I_O03',
                                                          'when': 'mask_1_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'hold',
                                                          'n': 357,
                                                          'chosen_count': 357,
                                                          'rate': 1.0,
                                                          'context_n': 357,
                                                          'confidence': 0.9972144846796658,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 307,
                                                                        'chosen_count': 81,
                                                                        'rate': 0.26384364820846906},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h105.t7070',
                                                          'predictions': {'n': 128,
                                                                          'correct': 128,
                                                                          'accuracy': 1.0,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.0625,
                                                                          'uniform_expected_accuracy': 0.20716145833333335},
                                                          'prediction_interval': {'clusters': 3,
                                                                                  'lift_95pct': [1.0, 1.0],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 11,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1386',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1395',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1404'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O04': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                     'structure; visible HP ≤100 THEY PREFER target_hero '
                                                     'OVER hold FOR hero_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'Richard135_I_O04',
                                                          'when': 'mask_1_low_1',
                                                          'skill': 'target_hero',
                                                          'over': 'hold',
                                                          'n': 8,
                                                          'chosen_count': 8,
                                                          'rate': 1.0,
                                                          'context_n': 8,
                                                          'confidence': 0.9,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 61,
                                                                        'chosen_count': 0,
                                                                        'rate': 0.0},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h108.t4815',
                                                          'predictions': {'n': 3,
                                                                          'correct': 3,
                                                                          'accuracy': 1.0,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.0,
                                                                          'uniform_expected_accuracy': 0.20000000000000004},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 4,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1422',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h108.t4815',
                                                                       'ereq_e257144c-f78b-42b2-a1c2-91f72688e149.h106.t1414'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O05': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER hold FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_I_O05',
                                                          'when': 'mask_2_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'hold',
                                                          'n': 334,
                                                          'chosen_count': 270,
                                                          'rate': 0.8083832335329342,
                                                          'context_n': 334,
                                                          'confidence': 0.8065476190476191,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 334,
                                                                        'chosen_count': 327,
                                                                        'rate': 0.9790419161676647},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h109.t6728',
                                                          'predictions': {'n': 106,
                                                                          'correct': 80,
                                                                          'accuracy': 0.7547169811320755,
                                                                          'population_correct': 80,
                                                                          'population_accuracy': 0.7547169811320755,
                                                                          'persistence_accuracy': 0.3490566037735849,
                                                                          'uniform_expected_accuracy': 0.20754716981132076},
                                                          'prediction_interval': {'clusters': 3,
                                                                                  'lift_95pct': [0.0, 0.0],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 11,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t624',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t637',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t657'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O06': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                     'structure; visible HP ≤100 THEY PREFER hold OVER '
                                                     'target_creep FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_I_O06',
                                                          'when': 'mask_2_low_1',
                                                          'skill': 'hold',
                                                          'over': 'target_creep',
                                                          'n': 7,
                                                          'chosen_count': 7,
                                                          'rate': 1.0,
                                                          'context_n': 7,
                                                          'confidence': 0.8888888888888888,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 3,
                                                                        'chosen_count': 0,
                                                                        'rate': 0.0},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a8957880-c86e-4554-b5eb-5b42f212a6d9.h102.t2888',
                                                          'predictions': {'n': 3,
                                                                          'correct': 0,
                                                                          'accuracy': 0.0,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.0,
                                                                          'uniform_expected_accuracy': 0.20000000000000004},
                                                          'prediction_interval': {'clusters': 2,
                                                                                  'lift_95pct': [0.0, 0.0],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 7,
                                                          'examples': ['ereq_e766eb57-1ad0-4546-80a5-bdd686a83c94.h102.t2888',
                                                                       'ereq_63a9c85f-e010-4dfc-ab10-132d7851a6b3.h102.t2888',
                                                                       'ereq_a722338b-035d-490f-afff-c84c6d068a2f.h102.t2888'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O07': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER hold FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_I_O07',
                                                          'when': 'mask_3_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'hold',
                                                          'n': 653,
                                                          'chosen_count': 339,
                                                          'rate': 0.5191424196018377,
                                                          'context_n': 653,
                                                          'confidence': 0.5190839694656488,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 1028,
                                                                        'chosen_count': 562,
                                                                        'rate': 0.546692607003891},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h107.t7046',
                                                          'predictions': {'n': 223,
                                                                          'correct': 121,
                                                                          'accuracy': 0.5426008968609866,
                                                                          'population_correct': 121,
                                                                          'population_accuracy': 0.5426008968609866,
                                                                          'persistence_accuracy': 0.2825112107623318,
                                                                          'uniform_expected_accuracy': 0.16973094170403588},
                                                          'prediction_interval': {'clusters': 3,
                                                                                  'lift_95pct': [0.0, 0.0],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 11,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t1373',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h108.t2233',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h108.t2245'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O09': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                     'hero/creep; visible HP >100 THEY PREFER '
                                                     'target_structure OVER hold FOR structure_pressure '
                                                     '(goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_I_O09',
                                                          'when': 'mask_4_low_0',
                                                          'skill': 'target_structure',
                                                          'over': 'hold',
                                                          'n': 578,
                                                          'chosen_count': 564,
                                                          'rate': 0.9757785467128027,
                                                          'context_n': 578,
                                                          'confidence': 0.9741379310344828,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 222,
                                                                        'chosen_count': 126,
                                                                        'rate': 0.5675675675675675},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h107.t8244',
                                                          'predictions': {'n': 207,
                                                                          'correct': 201,
                                                                          'accuracy': 0.9710144927536232,
                                                                          'population_correct': 201,
                                                                          'population_accuracy': 0.9710144927536232,
                                                                          'persistence_accuracy': 0.014492753623188406,
                                                                          'uniform_expected_accuracy': 0.2002415458937198},
                                                          'prediction_interval': {'clusters': 3,
                                                                                  'lift_95pct': [0.0, 0.0],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 11,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1048',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1056',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1064'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O11': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                     'nearby creep; visible HP >100 THEY PREFER target_hero '
                                                     'OVER target_structure FOR hero_pressure (goal '
                                                     'hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_I_O11',
                                                          'when': 'mask_5_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'target_structure',
                                                          'n': 82,
                                                          'chosen_count': 67,
                                                          'rate': 0.8170731707317073,
                                                          'context_n': 82,
                                                          'confidence': 0.8095238095238095,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 122,
                                                                        'chosen_count': 50,
                                                                        'rate': 0.4098360655737705},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h107.t8308',
                                                          'predictions': {'n': 21,
                                                                          'correct': 17,
                                                                          'accuracy': 0.8095238095238095,
                                                                          'population_correct': 17,
                                                                          'population_accuracy': 0.8095238095238095,
                                                                          'persistence_accuracy': 0.047619047619047616,
                                                                          'uniform_expected_accuracy': 0.16825396825396824},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 4,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t7521',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h108.t7521',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h107.t7543'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O13': {'claim': 'WHEN nearby=our creep + our exposed structure; no '
                                                     'nearby hero; visible HP >100 THEY PREFER '
                                                     'target_structure OVER target_creep FOR '
                                                     'structure_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'Richard135_I_O13',
                                                          'when': 'mask_6_low_0',
                                                          'skill': 'target_structure',
                                                          'over': 'target_creep',
                                                          'n': 583,
                                                          'chosen_count': 338,
                                                          'rate': 0.5797598627787307,
                                                          'context_n': 583,
                                                          'confidence': 0.5794871794871795,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 371,
                                                                        'chosen_count': 60,
                                                                        'rate': 0.16172506738544473},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h106.t8227',
                                                          'predictions': {'n': 226,
                                                                          'correct': 140,
                                                                          'accuracy': 0.6194690265486725,
                                                                          'population_correct': 83,
                                                                          'population_accuracy': 0.3672566371681416,
                                                                          'persistence_accuracy': 0.14601769911504425,
                                                                          'uniform_expected_accuracy': 0.16710914454277287},
                                                          'prediction_interval': {'clusters': 3,
                                                                                  'lift_95pct': [-0.3939393939393939,
                                                                                                 0.36923076923076925],
                                                                                  'method': '2000 bootstrap '
                                                                                            'resamples of '
                                                                                            'distinct full '
                                                                                            'observer '
                                                                                            'trajectories; '
                                                                                            'descriptive '
                                                                                            'with few '
                                                                                            'clusters'},
                                                          'supporting_episodes': 11,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t976',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1001',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h109.t1008'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]},
                       'Richard135_I_O15': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                     'structure; visible HP >100 THEY PREFER target_hero '
                                                     'OVER target_creep FOR hero_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'Richard135_I_O15',
                                                          'when': 'mask_7_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'target_creep',
                                                          'n': 22,
                                                          'chosen_count': 14,
                                                          'rate': 0.6363636363636364,
                                                          'context_n': 22,
                                                          'confidence': 0.625,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 84,
                                                                        'chosen_count': 28,
                                                                        'rate': 0.3333333333333333},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                                                          'last_observed': 'ereq_a9613a4f-0d0f-493a-a9c3-785cff47b7d2.h106.t7868',
                                                          'predictions': {'n': 6,
                                                                          'correct': 4,
                                                                          'accuracy': 0.6666666666666666,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.0,
                                                                          'uniform_expected_accuracy': 0.14285714285714285},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 4,
                                                          'examples': ['ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h107.t7777',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t7789',
                                                                       'ereq_5d8a6d43-f7c2-41d5-bc07-cf02cf763686.h106.t7798'],
                                                          'unresolved_constraints': 'Enemy cooldowns/private '
                                                                                    'memory and full route '
                                                                                    'execution unavailable. '
                                                                                    'Hold can be '
                                                                                    'turning/collision; '
                                                                                    'always provisional.',
                                                          'counterstrategy_status': 'proposed_test_only; no '
                                                                                    'exploitation attempt or '
                                                                                    'validated rollout '
                                                                                    'proxy'}]}}},
 'goal': {'hero_pressure': {'preference': 'Hypothesis: maintain visible hero contact in the counted '
                                          'contexts; no inference of kill intent or global priority.',
                            'provenance': 'interpretation',
                            'supporting_preferences': ['Richard135_I_O03',
                                                       'Richard135_I_O04',
                                                       'Richard135_I_O11',
                                                       'Richard135_I_O15'],
                            'paired_context_starts': 469,
                            'global_ordering_validated': False},
          'creep_contact': {'preference': 'Hypothesis: maintain creep contact. XP, gold and last-hit '
                                          'optimization are not observed.',
                            'provenance': 'interpretation',
                            'supporting_preferences': ['Richard135_I_O05', 'Richard135_I_O07'],
                            'paired_context_starts': 987,
                            'global_ordering_validated': False},
          'structure_pressure': {'preference': 'Hypothesis: pressure exposed structures. Target selection is '
                                               'weaker evidence than realized damage.',
                                 'provenance': 'interpretation',
                                 'supporting_preferences': ['Richard135_I_O09', 'Richard135_I_O13'],
                                 'paired_context_starts': 1161,
                                 'global_ordering_validated': False},
          'territory_pressure': {'preference': 'Hypothesis: gain proximity to our god. Intended route/end '
                                               'point remains unknown.',
                                 'provenance': 'interpretation',
                                 'supporting_preferences': [],
                                 'paired_context_starts': 0,
                                 'global_ordering_validated': False},
          'preservation': {'preference': 'Hypothesis: create distance at low absolute HP; geometry alone '
                                         'does not establish safety-seeking.',
                           'provenance': 'interpretation',
                           'supporting_preferences': [],
                           'paired_context_starts': 0,
                           'global_ordering_validated': False},
          'reposition': {'preference': 'Hypothesis: lateral relocation; tactical purpose unresolved.',
                         'provenance': 'interpretation',
                         'supporting_preferences': [],
                         'paired_context_starts': 0,
                         'global_ordering_validated': False},
          'unresolved': {'preference': 'Goal unknown: stationary motion alone does not establish voluntary '
                                       'holding.',
                         'provenance': 'interpretation',
                         'supporting_preferences': ['Richard135_I_O06'],
                         'paired_context_starts': 7,
                         'global_ordering_validated': False}},
 'skill': {'target_hero': {'operator': 'observed_target_hero', 'parameters': {'minimum_segment_ticks': 6}},
           'target_creep': {'operator': 'observed_target_creep', 'parameters': {'minimum_segment_ticks': 6}},
           'target_structure': {'operator': 'observed_target_structure',
                                'parameters': {'minimum_segment_ticks': 6}},
           'advance': {'operator': 'observed_advance', 'parameters': {'minimum_segment_ticks': 6}},
           'withdraw': {'operator': 'observed_withdraw', 'parameters': {'minimum_segment_ticks': 6}},
           'lateral': {'operator': 'observed_lateral', 'parameters': {'minimum_segment_ticks': 6}},
           'hold': {'operator': 'observed_hold', 'parameters': {'minimum_segment_ticks': 6}}},
 'strategy': [{'id': 'Richard135_I_O03',
               'when': 'mask_1_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Richard135_I_O04',
               'when': 'mask_1_low_1',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Richard135_I_O05',
               'when': 'mask_2_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_I_O06', 'when': 'mask_2_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_I_O07',
               'when': 'mask_3_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_I_O09',
               'when': 'mask_4_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'Richard135_I_O11',
               'when': 'mask_5_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Richard135_I_O13',
               'when': 'mask_6_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'Richard135_I_O15',
               'when': 'mask_7_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']}],
 'execution': {'binding': 'gota-observer-model/1', 'game_version': '2026.9.16.5', 'language': 'Python'},
 'update': {'revision': 1,
            'parent': None,
            'change': {'origin': 'observable_replay_inference',
                       'parameters': {'minimum_segment_ticks': 6,
                                      'opportunity_radius_tiles': 12,
                                      'low_hp_absolute': 100,
                                      'motion_min_world_units': 1000,
                                      'radial_cosine_threshold': 0.35,
                                      'local_route_check_tiles': 2},
                       'model_freeze_sha256': 'ec816aa512b666ffe2365198465a68485cb173072122cc298d3cdb3efd1ce93d',
                       'purpose': 'Primary-format forecast model; no automatic strategy adoption'},
            'needs_review': ['Unvalidated live rollout proxy',
                             'Untested counterstrategies',
                             'Exact-repeat heldout leakage risk',
                             'Class/side/phase confounding',
                             'No hidden belief or ability inference'],
            'evidence': [{'artifact': 'docs/opponents/richard-v135/evidence.json',
                          'model_level': 'individual',
                          'episode_count': 20}]}}

PROPOSED_RULES = [{'id': 'Richard135_I_C01',
  'status': 'proposed_test_only',
  'adopted': False,
  'rule': {'id': 'Richard135_I_C01',
           'when': 'visible_core_pressure_and_distant_defenders',
           'skill': 'observe',
           'for': ['G_defense']},
  'predicate_proposal': 'Visible living enemy pair near a standing friendly defense anchor and own god; keep '
                        'spatial and time-to-return evidence, never opponent label or hidden state.',
  'mechanism': 'Allow a bounded critical-defense commitment to override the 28-tile distant-recall '
               'cancellation; evaluate earlier warning distance and assigned responder travel.',
  'opponent_preference_ids': ['Richard135_I_O13'],
  'macro_evidence': {'n': 11,
                     'pair_within24': {'observed_pair_episodes': 11,
                                       'zero_friendly_within28': 7,
                                       'all_five_friendly_alive_and_distant': 7},
                     'scope': 'Descriptive training observations; not heldout macro validation'},
  'existing_intervention': 'Critical60 blue 4W0L, Critical40 blue 2W2L; both red 0W4L. Directional screens '
                           'only.',
  'test': 'Fresh pinned Richard135 AND Alexg002 candidate/control 40 per color, >=30/40 each target/color; '
          'retain Jordan268 >=38/40 each and original field guard. Full source, VM and replay audits. Draws '
          'count zero.'},
 {'id': 'Richard135_I_C02',
  'status': 'diagnostic_proposal',
  'adopted': False,
  'rule': {'id': 'Richard135_I_C02',
           'when': 'local_defense_fails_after_response',
           'skill': 'attack',
           'for': ['G_defense', 'G_survival']},
  'predicate_proposal': 'Observed response occurred but the core still fell; require a trace of actual '
                        'defender arrival and target choice.',
  'mechanism': 'Repair red combat/economy after timely response. Test support and wave participation; the '
               'existing red equipment-only screen 0/4 already refutes sufficiency of that tested variant.',
  'evidence': 'own-decision-analysis.json plus macro-observations.json; diagnostic inference, not an adopted '
              'opponent preference.',
  'test': 'Record arrival time, enemy structure-target duration, friendly survival and actual fort wins. Use '
          'real reacting opponent; the observational model is not a rollout controller.'}]
