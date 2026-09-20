"""Counted observer-only opponent model in the primary seven-layer Python IR.
No private source; not an executable or validated rollout proxy.
"""

MODEL = {'schema': 'gota-semantic-opponent/1',
 'id': 'alex_g002_v1_individual_observer_model',
 'situation': {'grounded': {'observation': 'One real own slot0/5 at its predecision moment. Motif at t must '
                                           'persist 6 ticks; predictors use only t-1.',
                            'predicates': {'mask_2_low_0': 'nearby=our creep; no nearby hero/exposed '
                                                           'structure; visible HP >100',
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
                         'opponent_version': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                         'opponent_label': 'gota-g002:v1',
                         'our_policy': {'directory': '/Users/aaln/experiments/softmax/polyworld/examples/gods_of_the_arena/players/ir/forks/jordan268',
                                        'id': 'gota_jordan268_redrace',
                                        'basic_sha256': 'be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73',
                                        'ir_file_sha256': 'dbb2dbe273e02c047afcf674af4a73117abab278a6af362238879ee77ae2ddb2',
                                        'versions': ['00cd9483-0309-4613-bf61-89f3f4a33d01',
                                                     '4cdbbf36-3d70-4ea3-8aed-c92ee0e024be']},
                         'predictor': {'contexts': {'mask_2_low_0': {'target_creep': 139},
                                                    'mask_3_low_0': {'target_hero': 12},
                                                    'mask_4_low_0': {'target_structure': 126,
                                                                     'advance': 72,
                                                                     'hold': 18,
                                                                     'lateral': 6,
                                                                     'withdraw': 12},
                                                    'mask_5_low_0': {'target_structure': 25,
                                                                     'hold': 6,
                                                                     'target_hero': 2},
                                                    'mask_6_low_0': {'target_structure': 117,
                                                                     'target_creep': 294,
                                                                     'hold': 6,
                                                                     'withdraw': 6},
                                                    'mask_7_low_0': {'target_hero': 50,
                                                                     'target_structure': 19}},
                                       'global': {'target_creep': 433,
                                                  'target_structure': 287,
                                                  'advance': 72,
                                                  'hold': 30,
                                                  'target_hero': 64,
                                                  'lateral': 6,
                                                  'withdraw': 18},
                                       'smoothing': 'Laplace +1 over estimated available skills; context '
                                                    'backs off globally if n<8'},
                         'skills': {'target_hero': {'n': 68,
                                                    'episodes': 6,
                                                    'ticks': 2521,
                                                    'initiation_contexts': {'mask_6_low_0': 4,
                                                                            'mask_7_low_0': 50,
                                                                            'mask_3_low_0': 12,
                                                                            'mask_5_low_0': 2},
                                                    'termination': {'visible_target_change': 56,
                                                                    'visibility_lost_or_not_alive': 12},
                                                    'left_censored': 0,
                                                    'median_duration_ticks': 36.0,
                                                    'outcome_hp_change_median': 0.0,
                                                    'concurrent_movement_ticks': {'hold': 992,
                                                                                  'advance': 1529},
                                                    'prediction': {'actual_n': 11,
                                                                   'predicted_n': 16,
                                                                   'recall': 1.0,
                                                                   'precision': 0.6875},
                                                    'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h101.t2485'},
                                    'target_creep': {'n': 561,
                                                     'episodes': 12,
                                                     'ticks': 7129,
                                                     'initiation_contexts': {'mask_2_low_0': 265,
                                                                             'mask_6_low_0': 294,
                                                                             'mask_4_low_0': 2},
                                                     'termination': {'visible_target_change': 442,
                                                                     'visibility_lost_or_not_alive': 119},
                                                     'left_censored': 126,
                                                     'median_duration_ticks': 9,
                                                     'outcome_hp_change_median': 0,
                                                     'concurrent_movement_ticks': {'advance': 2181,
                                                                                   'hold': 3909,
                                                                                   'withdraw': 1000,
                                                                                   'lateral': 39},
                                                     'prediction': {'actual_n': 148,
                                                                    'predicted_n': 184,
                                                                    'recall': 1.0,
                                                                    'precision': 0.8043478260869565},
                                                     'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t689'},
                                    'target_structure': {'n': 473,
                                                         'episodes': 12,
                                                         'ticks': 58455,
                                                         'initiation_contexts': {'mask_6_low_0': 261,
                                                                                 'mask_4_low_0': 168,
                                                                                 'mask_7_low_0': 19,
                                                                                 'mask_5_low_0': 25},
                                                         'termination': {'visible_target_change': 335,
                                                                         'visibility_lost_or_not_alive': 84,
                                                                         'episode_end': 54},
                                                         'left_censored': 186,
                                                         'median_duration_ticks': 97,
                                                         'outcome_hp_change_median': 0,
                                                         'concurrent_movement_ticks': {'advance': 9905,
                                                                                       'hold': 47652,
                                                                                       'lateral': 686,
                                                                                       'withdraw': 212},
                                                         'prediction': {'actual_n': 86,
                                                                        'predicted_n': 87,
                                                                        'recall': 0.5930232558139535,
                                                                        'precision': 0.5862068965517241},
                                                         'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t957'},
                                    'advance': {'n': 72,
                                                'episodes': 12,
                                                'ticks': 2855,
                                                'initiation_contexts': {'mask_4_low_0': 72},
                                                'termination': {'movement_character_change': 60,
                                                                'visible_target_change': 12},
                                                'left_censored': 0,
                                                'median_duration_ticks': 49.0,
                                                'outcome_hp_change_median': 0.0,
                                                'concurrent_movement_ticks': {'advance': 2855},
                                                'prediction': {'actual_n': 24,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2253'},
                                    'withdraw': {'n': 18,
                                                 'episodes': 12,
                                                 'ticks': 371,
                                                 'initiation_contexts': {'mask_4_low_0': 12,
                                                                         'mask_6_low_0': 6},
                                                 'termination': {'visible_target_change': 18},
                                                 'left_censored': 0,
                                                 'median_duration_ticks': 16.0,
                                                 'outcome_hp_change_median': 0.0,
                                                 'concurrent_movement_ticks': {'withdraw': 371},
                                                 'prediction': {'actual_n': 7,
                                                                'predicted_n': 0,
                                                                'recall': 0.0,
                                                                'precision': None},
                                                 'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2864'},
                                    'lateral': {'n': 6,
                                                'episodes': 6,
                                                'ticks': 108,
                                                'initiation_contexts': {'mask_4_low_0': 6},
                                                'termination': {'movement_character_change': 6},
                                                'left_censored': 0,
                                                'median_duration_ticks': 18.0,
                                                'outcome_hp_change_median': 0.0,
                                                'concurrent_movement_ticks': {'lateral': 108},
                                                'prediction': {'actual_n': 1,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2846'},
                                    'hold': {'n': 30,
                                             'episodes': 12,
                                             'ticks': 369,
                                             'initiation_contexts': {'mask_4_low_0': 18,
                                                                     'mask_5_low_0': 6,
                                                                     'mask_6_low_0': 6},
                                             'termination': {'movement_character_change': 24,
                                                             'visible_target_change': 6},
                                             'left_censored': 0,
                                             'median_duration_ticks': 9.0,
                                             'outcome_hp_change_median': 0.0,
                                             'concurrent_movement_ticks': {'hold': 369},
                                             'prediction': {'actual_n': 10,
                                                            'predicted_n': 0,
                                                            'recall': 0.0,
                                                            'precision': None},
                                             'example': 'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2280'}},
                         'validation': {'n': 287,
                                        'correct': 210,
                                        'accuracy': 0.7317073170731707,
                                        'population_correct': 195,
                                        'population_accuracy': 0.6794425087108014,
                                        'persistence_accuracy': 0.4808362369337979,
                                        'uniform_expected_accuracy': 0.1796747967479675,
                                        'cluster_uncertainty': {'clusters': 3,
                                                                'lift_95pct': [0.0, 0.1875],
                                                                'method': '2000 bootstrap resamples of '
                                                                          'distinct full observer '
                                                                          'trajectories; descriptive with '
                                                                          'few clusters'},
                                        'novel_trajectories': {'n': 0,
                                                               'correct': 0,
                                                               'accuracy': None,
                                                               'population_correct': 0,
                                                               'population_accuracy': None,
                                                               'persistence_accuracy': None,
                                                               'uniform_expected_accuracy': None},
                                        'novel_episode_ids': [],
                                        'robustness_baselines': {'class': {'correct': 190,
                                                                           'n': 287,
                                                                           'accuracy': 0.662020905923345,
                                                                           'by_context': {'mask_2_low_0': {'correct': 40,
                                                                                                           'n': 40},
                                                                                          'mask_7_low_0': {'correct': 2,
                                                                                                           'n': 14},
                                                                                          'mask_4_low_0': {'correct': 40,
                                                                                                           'n': 81},
                                                                                          'mask_6_low_0': {'correct': 108,
                                                                                                           'n': 144},
                                                                                          'mask_3_low_0': {'correct': 0,
                                                                                                           'n': 2},
                                                                                          'mask_5_low_0': {'correct': 0,
                                                                                                           'n': 6}}},
                                                                 'side': {'correct': 200,
                                                                          'n': 287,
                                                                          'accuracy': 0.6968641114982579,
                                                                          'by_context': {'mask_2_low_0': {'correct': 40,
                                                                                                          'n': 40},
                                                                                         'mask_7_low_0': {'correct': 5,
                                                                                                          'n': 14},
                                                                                         'mask_4_low_0': {'correct': 47,
                                                                                                          'n': 81},
                                                                                         'mask_6_low_0': {'correct': 108,
                                                                                                          'n': 144},
                                                                                         'mask_3_low_0': {'correct': 0,
                                                                                                          'n': 2},
                                                                                         'mask_5_low_0': {'correct': 0,
                                                                                                          'n': 6}}}},
                                        'by_episode': {'ereq_4f7e1a91-1c8c-4491-a68b-2542cc199310': {'n': 80,
                                                                                                     'correct': 54,
                                                                                                     'accuracy': 0.675,
                                                                                                     'population_correct': 39,
                                                                                                     'population_accuracy': 0.4875,
                                                                                                     'persistence_accuracy': 0.25,
                                                                                                     'uniform_expected_accuracy': 0.17583333333333334},
                                                       'ereq_35302c57-b5cf-42aa-ad0c-b99ab2859a25': {'n': 70,
                                                                                                     'correct': 52,
                                                                                                     'accuracy': 0.7428571428571429,
                                                                                                     'population_correct': 52,
                                                                                                     'population_accuracy': 0.7428571428571429,
                                                                                                     'persistence_accuracy': 0.5857142857142857,
                                                                                                     'uniform_expected_accuracy': 0.18047619047619046},
                                                       'ereq_50eb06e1-c98a-4d16-bf07-fe5d6ce4f80c': {'n': 67,
                                                                                                     'correct': 52,
                                                                                                     'accuracy': 0.7761194029850746,
                                                                                                     'population_correct': 52,
                                                                                                     'population_accuracy': 0.7761194029850746,
                                                                                                     'persistence_accuracy': 0.5373134328358209,
                                                                                                     'uniform_expected_accuracy': 0.1825870646766169},
                                                       'ereq_5af9a53a-af97-4cfe-9fb2-e997497424cb': {'n': 70,
                                                                                                     'correct': 52,
                                                                                                     'accuracy': 0.7428571428571429,
                                                                                                     'population_correct': 52,
                                                                                                     'population_accuracy': 0.7428571428571429,
                                                                                                     'persistence_accuracy': 0.5857142857142857,
                                                                                                     'uniform_expected_accuracy': 0.18047619047619046}},
                                        'by_observer_side': {'0': {'n': 207,
                                                                   'correct': 156,
                                                                   'accuracy': 0.7536231884057971,
                                                                   'population_correct': 156,
                                                                   'population_accuracy': 0.7536231884057971,
                                                                   'persistence_accuracy': 0.5700483091787439,
                                                                   'uniform_expected_accuracy': 0.18115942028985507},
                                                             '5': {'n': 80,
                                                                   'correct': 54,
                                                                   'accuracy': 0.675,
                                                                   'population_correct': 39,
                                                                   'population_accuracy': 0.4875,
                                                                   'persistence_accuracy': 0.25,
                                                                   'uniform_expected_accuracy': 0.17583333333333334}}},
                         'observability': {'episodes': 20,
                                           'ticks': 56547,
                                           'living_opponent_ticks': 278829,
                                           'visible_living_opponent_ticks': 122795,
                                           'fraction': 0.44039536777021043,
                                           'all_scheduled_hero_tick_fraction': 0.4343112808813907,
                                           'observer_dead_fraction': 0.0,
                                           'residual_fraction': 0.030261818477951057,
                                           'segments': 2039,
                                           'eligible': 1500,
                                           'exclusions': {'left_censored': 530,
                                                          'selected_skill_not_established_by_prior_affordances': 9}},
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
            'claims': {'AlexG002v1_I_O05': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER hold FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'AlexG002v1_I_O05',
                                                          'when': 'mask_2_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'hold',
                                                          'n': 139,
                                                          'chosen_count': 139,
                                                          'rate': 1.0,
                                                          'context_n': 139,
                                                          'confidence': 0.9929078014184397,
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
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h100.t1336',
                                                          'predictions': {'n': 40,
                                                                          'correct': 40,
                                                                          'accuracy': 1.0,
                                                                          'population_correct': 40,
                                                                          'population_accuracy': 1.0,
                                                                          'persistence_accuracy': 0.7,
                                                                          'uniform_expected_accuracy': 0.2},
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
                                                          'supporting_episodes': 12,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t718',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t737',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t1307'],
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
                       'AlexG002v1_I_O07': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                     'structure; visible HP >100 THEY PREFER target_hero '
                                                     'OVER target_creep FOR hero_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'AlexG002v1_I_O07',
                                                          'when': 'mask_3_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'target_creep',
                                                          'n': 12,
                                                          'chosen_count': 12,
                                                          'rate': 1.0,
                                                          'context_n': 12,
                                                          'confidence': 0.9285714285714286,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 1028,
                                                                        'chosen_count': 137,
                                                                        'rate': 0.13326848249027237},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h104.t2823',
                                                          'predictions': {'n': 2,
                                                                          'correct': 2,
                                                                          'accuracy': 1.0,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 1.0,
                                                                          'uniform_expected_accuracy': 0.16666666666666666},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 6,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t2814',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t2824',
                                                                       'ereq_ab17782d-44c9-4a10-9b8c-c7764afc88c4.h104.t2814'],
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
                       'AlexG002v1_I_O09': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                     'hero/creep; visible HP >100 THEY PREFER '
                                                     'target_structure OVER hold FOR structure_pressure '
                                                     '(goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'AlexG002v1_I_O09',
                                                          'when': 'mask_4_low_0',
                                                          'skill': 'target_structure',
                                                          'over': 'hold',
                                                          'n': 234,
                                                          'chosen_count': 126,
                                                          'rate': 0.5384615384615384,
                                                          'context_n': 234,
                                                          'confidence': 0.538135593220339,
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
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h100.t2864',
                                                          'predictions': {'n': 81,
                                                                          'correct': 47,
                                                                          'accuracy': 0.5802469135802469,
                                                                          'population_correct': 47,
                                                                          'population_accuracy': 0.5802469135802469,
                                                                          'persistence_accuracy': 0.19753086419753085,
                                                                          'uniform_expected_accuracy': 0.19999999999999998},
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
                                                          'supporting_episodes': 12,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2013',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h103.t2013',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t2253'],
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
                       'AlexG002v1_I_O11': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                     'nearby creep; visible HP >100 THEY PREFER '
                                                     'target_structure OVER target_hero FOR '
                                                     'structure_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'AlexG002v1_I_O11',
                                                          'when': 'mask_5_low_0',
                                                          'skill': 'target_structure',
                                                          'over': 'target_hero',
                                                          'n': 33,
                                                          'chosen_count': 25,
                                                          'rate': 0.7575757575757576,
                                                          'context_n': 33,
                                                          'confidence': 0.7428571428571429,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 122,
                                                                        'chosen_count': 33,
                                                                        'rate': 0.27049180327868855},
                                                          'status': 'supported',
                                                          'level': 'individual',
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h103.t3116',
                                                          'predictions': {'n': 6,
                                                                          'correct': 4,
                                                                          'accuracy': 0.6666666666666666,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.3333333333333333,
                                                                          'uniform_expected_accuracy': 0.16666666666666666},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 6,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h103.t2837',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h101.t3089',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h102.t3089'],
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
                       'AlexG002v1_I_O13': {'claim': 'WHEN nearby=our creep + our exposed structure; no '
                                                     'nearby hero; visible HP >100 THEY PREFER target_creep '
                                                     'OVER target_structure FOR creep_contact (goal '
                                                     'hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'AlexG002v1_I_O13',
                                                          'when': 'mask_6_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'target_structure',
                                                          'n': 423,
                                                          'chosen_count': 294,
                                                          'rate': 0.6950354609929078,
                                                          'context_n': 423,
                                                          'confidence': 0.6941176470588235,
                                                          'confidence_meaning': 'Laplace-smoothed observed '
                                                                                'selection probability, not '
                                                                                'probability of hidden '
                                                                                'intent; correlated segments',
                                                          'base_rate': {'source': '14-trajectory population '
                                                                                  'prior, same context and '
                                                                                  'paired affordances',
                                                                        'n': 371,
                                                                        'chosen_count': 270,
                                                                        'rate': 0.7277628032345014},
                                                          'status': 'provisional',
                                                          'level': 'individual',
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h100.t3089',
                                                          'predictions': {'n': 144,
                                                                          'correct': 108,
                                                                          'accuracy': 0.75,
                                                                          'population_correct': 108,
                                                                          'population_accuracy': 0.75,
                                                                          'persistence_accuracy': 0.625,
                                                                          'uniform_expected_accuracy': 0.16689814814814813},
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
                                                          'supporting_episodes': 12,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h100.t995',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h102.t995',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h103.t995'],
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
                       'AlexG002v1_I_O15': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                     'structure; visible HP >100 THEY PREFER target_hero '
                                                     'OVER target_creep FOR hero_pressure (goal hypothesis).',
                                            'status': 'supported',
                                            'evidence': [{'id': 'AlexG002v1_I_O15',
                                                          'when': 'mask_7_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'target_creep',
                                                          'n': 69,
                                                          'chosen_count': 50,
                                                          'rate': 0.7246376811594203,
                                                          'context_n': 69,
                                                          'confidence': 0.7183098591549296,
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
                                                          'opponent': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                                                          'last_observed': 'ereq_a74b5621-ccf6-4c05-8735-d6cb37e2ecad.h101.t2837',
                                                          'predictions': {'n': 14,
                                                                          'correct': 9,
                                                                          'accuracy': 0.6428571428571429,
                                                                          'population_correct': 0,
                                                                          'population_accuracy': 0.0,
                                                                          'persistence_accuracy': 0.0,
                                                                          'uniform_expected_accuracy': 0.14285714285714285},
                                                          'prediction_interval': {'clusters': 1,
                                                                                  'lift_95pct': None,
                                                                                  'note': 'Too few distinct '
                                                                                          'observable '
                                                                                          'trajectories'},
                                                          'supporting_episodes': 6,
                                                          'examples': ['ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h102.t2485',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h103.t2485',
                                                                       'ereq_4e73477b-e9b3-457b-b02c-91b7f08ae002.h104.t2485'],
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
                            'supporting_preferences': ['AlexG002v1_I_O07', 'AlexG002v1_I_O15'],
                            'paired_context_starts': 81,
                            'global_ordering_validated': False},
          'creep_contact': {'preference': 'Hypothesis: maintain creep contact. XP, gold and last-hit '
                                          'optimization are not observed.',
                            'provenance': 'interpretation',
                            'supporting_preferences': ['AlexG002v1_I_O05', 'AlexG002v1_I_O13'],
                            'paired_context_starts': 562,
                            'global_ordering_validated': False},
          'structure_pressure': {'preference': 'Hypothesis: pressure exposed structures. Target selection is '
                                               'weaker evidence than realized damage.',
                                 'provenance': 'interpretation',
                                 'supporting_preferences': ['AlexG002v1_I_O09', 'AlexG002v1_I_O11'],
                                 'paired_context_starts': 267,
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
                         'supporting_preferences': [],
                         'paired_context_starts': 0,
                         'global_ordering_validated': False}},
 'skill': {'target_hero': {'operator': 'observed_target_hero', 'parameters': {'minimum_segment_ticks': 6}},
           'target_creep': {'operator': 'observed_target_creep', 'parameters': {'minimum_segment_ticks': 6}},
           'target_structure': {'operator': 'observed_target_structure',
                                'parameters': {'minimum_segment_ticks': 6}},
           'advance': {'operator': 'observed_advance', 'parameters': {'minimum_segment_ticks': 6}},
           'withdraw': {'operator': 'observed_withdraw', 'parameters': {'minimum_segment_ticks': 6}},
           'lateral': {'operator': 'observed_lateral', 'parameters': {'minimum_segment_ticks': 6}},
           'hold': {'operator': 'observed_hold', 'parameters': {'minimum_segment_ticks': 6}}},
 'strategy': [{'id': 'AlexG002v1_I_O05',
               'when': 'mask_2_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'AlexG002v1_I_O07',
               'when': 'mask_3_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'AlexG002v1_I_O09',
               'when': 'mask_4_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'AlexG002v1_I_O11',
               'when': 'mask_5_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'AlexG002v1_I_O13',
               'when': 'mask_6_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'AlexG002v1_I_O15',
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
                       'model_freeze_sha256': '36aa6e70e3c81948d04b353c2f855002a436dc6e2f2579bf398f055c35c71476',
                       'purpose': 'Primary-format forecast model; no automatic strategy adoption'},
            'needs_review': ['Unvalidated live rollout proxy',
                             'Untested counterstrategies',
                             'Exact-repeat heldout leakage risk',
                             'Class/side/phase confounding',
                             'No hidden belief or ability inference'],
            'evidence': [{'artifact': 'docs/opponents/alex-g002-v1/evidence.json',
                          'model_level': 'individual',
                          'episode_count': 20}]}}

PROPOSED_RULES = [{'id': 'AlexG002v1_I_C01',
  'status': 'proposed_test_only',
  'adopted': False,
  'rule': {'id': 'AlexG002v1_I_C01',
           'when': 'visible_core_pressure_and_distant_defenders',
           'skill': 'observe',
           'for': ['G_defense']},
  'predicate_proposal': 'Visible living enemy pair near a standing friendly defense anchor and own god; keep '
                        'spatial and time-to-return evidence, never opponent label or hidden state.',
  'mechanism': 'Allow a bounded critical-defense commitment to override the 28-tile distant-recall '
               'cancellation; evaluate earlier warning distance and assigned responder travel.',
  'opponent_preference_ids': ['AlexG002v1_I_O11', 'AlexG002v1_I_O15'],
  'macro_evidence': {'n': 12,
                     'pair_within24': {'observed_pair_episodes': 12,
                                       'zero_friendly_within28': 12,
                                       'all_five_friendly_alive_and_distant': 12},
                     'scope': 'Descriptive training observations; not heldout macro validation'},
  'existing_intervention': 'No controlled current-policy-versus-Alex intervention has yet validated this '
                           'proposed repair.',
  'test': 'Fresh pinned Richard135 AND Alexg002 candidate/control 40 per color, >=30/40 each target/color; '
          'retain Jordan268 >=38/40 each and original field guard. Full source, VM and replay audits. Draws '
          'count zero.'},
 {'id': 'AlexG002v1_I_C02',
  'status': 'diagnostic_proposal',
  'adopted': False,
  'rule': {'id': 'AlexG002v1_I_C02',
           'when': 'local_defense_fails_after_response',
           'skill': 'attack',
           'for': ['G_defense', 'G_survival']},
  'predicate_proposal': 'Observed response occurred but the core still fell; require a trace of actual '
                        'defender arrival and target choice.',
  'mechanism': 'Test interception at the threatened inner structure, before the god becomes the active '
               'target. Visible late god burn leaves very little travel time; a defender who only chases '
               'heroes can still allow structure pressure.',
  'evidence': 'own-decision-analysis.json plus macro-observations.json; diagnostic inference, not an adopted '
              'opponent preference.',
  'test': 'Record arrival time, enemy structure-target duration, friendly survival and actual fort wins. Use '
          'real reacting opponent; the observational model is not a rollout controller.'}]
