"""Inferred opponent IR in the primary seven-layer Python dictionary layout.

Generated from frozen observer evidence; no private opponent code or VM commands.
Use opponent_ir.validate / predict; this is not a BASIC or rollout policy.
"""

MODEL = {'schema': 'gota-semantic-opponent/1',
 'id': 'jordan_v268_observer_model',
 'situation': {'grounded': {'observation': 'Single owned hero slot 0/5, exact predecision host-visible '
                                           'snapshots. Predictor uses tick t-1; inferred motif begins at t '
                                           'and must last at least 6 ticks (0.25s at 24 Hz).',
                            'structure_alive': 'For structures, objectAlive means exposed; positive HP '
                                               'means standing. A zero visible target means none OR '
                                               'hidden.',
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
                                           'mask_3_low_1': 'nearby=our hero + our creep; no nearby exposed '
                                                           'structure; visible HP ≤100',
                                           'mask_4_low_0': 'nearby=our exposed structure; no nearby '
                                                           'hero/creep; visible HP >100',
                                           'mask_4_low_1': 'nearby=our exposed structure; no nearby '
                                                           'hero/creep; visible HP ≤100',
                                           'mask_5_low_0': 'nearby=our hero + our exposed structure; no '
                                                           'nearby creep; visible HP >100',
                                           'mask_5_low_1': 'nearby=our hero + our exposed structure; no '
                                                           'nearby creep; visible HP ≤100',
                                           'mask_6_low_0': 'nearby=our creep + our exposed structure; no '
                                                           'nearby hero; visible HP >100',
                                           'mask_7_low_0': 'nearby=our hero + our creep + our exposed '
                                                           'structure; visible HP >100',
                                           'mask_7_low_1': 'nearby=our hero + our creep + our exposed '
                                                           'structure; visible HP ≤100'},
                            'glossary_extensions': {'target_hero': 'Visible target identifies a living '
                                                                   'hostile hero; pursuit/retained target, '
                                                                   'not proof of an attack or kill.',
                                                    'target_creep': 'Visible target identifies a living '
                                                                    'hostile footman; pursuit/retained '
                                                                    'target, not proof of farming or last '
                                                                    'hits.',
                                                    'target_structure': 'Visible target identifies a '
                                                                        'positive-HP exposed hostile '
                                                                        'tower, barracks or god; not proof '
                                                                        'of damage.',
                                                    'advance': 'Without a valid visible target, velocity '
                                                               'points toward our god (radial cosine '
                                                               '>0.35). Relative geometry, not inferred '
                                                               'destination.',
                                                    'withdraw': 'Without a valid visible target, velocity '
                                                                'points away from our god (radial cosine '
                                                                '<-0.35). Not proof of retreat to safety.',
                                                    'lateral': 'Without a valid visible target, velocity '
                                                               'is neither advancing nor withdrawing by '
                                                               'the radial thresholds.',
                                                    'hold': 'Without a valid visible target, speed <1000 '
                                                            'world units/tick. Can include turning, '
                                                            'collision or hidden target; voluntary waiting '
                                                            'unproven.'}},
               'notes': 'All motifs are [inferred-skill]. Original attack is defense_cadence; it is not '
                        'equivalent to a visible target. Concurrent movement qualifiers are retained '
                        'inside targeting motifs. This describes observed behavior, not Jordan source '
                        'rules.'},
 'belief': {'grounded': {'level': 'individual',
                         'opponent_version': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                         'our_policy': {'id': 'gota_relh154_legacy',
                                        'schema': 'gota-semantic-policy/1',
                                        'canonical_sha256': '8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37',
                                        'basic_sha256': 'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'},
                         'memory': 'No private opponent memory inferred. Individual estimates are frozen; '
                                   'no persistent in-episode updates are asserted.',
                         'uncertainty': 'Partial visibility, correlated trajectories, estimated '
                                        'affordances, and retrospective event boundaries. Absence from '
                                        'view is not absence from game.',
                         'predictor': {'contexts': {'mask_1_low_0': {'target_hero': 387,
                                                                     'advance': 24,
                                                                     'hold': 184,
                                                                     'withdraw': 37},
                                                    'mask_1_low_1': {'target_hero': 14,
                                                                     'hold': 1,
                                                                     'lateral': 3,
                                                                     'advance': 2},
                                                    'mask_2_low_0': {'target_creep': 518,
                                                                     'advance': 6,
                                                                     'hold': 26,
                                                                     'withdraw': 5},
                                                    'mask_2_low_1': {'target_creep': 2},
                                                    'mask_3_low_0': {'target_hero': 219,
                                                                     'hold': 146,
                                                                     'withdraw': 64,
                                                                     'target_creep': 118,
                                                                     'advance': 6},
                                                    'mask_3_low_1': {'target_hero': 17,
                                                                     'hold': 20,
                                                                     'withdraw': 32,
                                                                     'advance': 5,
                                                                     'target_creep': 1},
                                                    'mask_4_low_0': {'target_structure': 18,
                                                                     'advance': 17,
                                                                     'hold': 18,
                                                                     'lateral': 1},
                                                    'mask_4_low_1': {'lateral': 2, 'hold': 11},
                                                    'mask_5_low_0': {'target_hero': 649,
                                                                     'target_structure': 228,
                                                                     'hold': 313,
                                                                     'withdraw': 72,
                                                                     'advance': 68,
                                                                     'lateral': 27},
                                                    'mask_5_low_1': {'hold': 31,
                                                                     'withdraw': 22,
                                                                     'target_hero': 24,
                                                                     'target_structure': 3,
                                                                     'lateral': 1,
                                                                     'advance': 1},
                                                    'mask_6_low_0': {'target_creep': 201,
                                                                     'hold': 31,
                                                                     'target_structure': 14,
                                                                     'withdraw': 16,
                                                                     'advance': 5},
                                                    'mask_7_low_0': {'target_creep': 136,
                                                                     'target_hero': 360,
                                                                     'target_structure': 37,
                                                                     'hold': 93,
                                                                     'withdraw': 30,
                                                                     'lateral': 6,
                                                                     'advance': 15},
                                                    'mask_7_low_1': {'target_structure': 4,
                                                                     'target_hero': 1,
                                                                     'withdraw': 5,
                                                                     'lateral': 2,
                                                                     'advance': 1,
                                                                     'hold': 1}},
                                       'global': {'target_creep': 976,
                                                  'target_hero': 1671,
                                                  'target_structure': 304,
                                                  'hold': 875,
                                                  'withdraw': 283,
                                                  'advance': 150,
                                                  'lateral': 42},
                                       'smoothing': 'Laplace +1 over estimated available skills; context '
                                                    'backs off globally if n<8'},
                         'skills': {'target_hero': {'n': 1690,
                                                    'episodes': 11,
                                                    'ticks': 34151,
                                                    'initiation_contexts': {'mask_7_low_0': 361,
                                                                            'mask_5_low_0': 661,
                                                                            'mask_1_low_0': 391,
                                                                            'mask_3_low_0': 221,
                                                                            'mask_3_low_1': 17,
                                                                            'mask_7_low_1': 1,
                                                                            'mask_1_low_1': 14,
                                                                            'mask_5_low_1': 24},
                                                    'termination': {'visibility_lost_or_not_alive': 244,
                                                                    'visible_target_change': 1379,
                                                                    'observer_dead': 67},
                                                    'left_censored': 19,
                                                    'median_duration_ticks': 14.0,
                                                    'outcome_hp_change_median': 0.0,
                                                    'concurrent_movement_ticks': {'hold': 26187,
                                                                                  'advance': 6780,
                                                                                  'lateral': 638,
                                                                                  'withdraw': 546},
                                                    'prediction': {'actual_n': 615,
                                                                   'predicted_n': 1185,
                                                                   'recall': 0.991869918699187,
                                                                   'precision': 0.5147679324894515},
                                                    'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t780'},
                                    'target_creep': {'n': 1148,
                                                     'episodes': 11,
                                                     'ticks': 14598,
                                                     'initiation_contexts': {'mask_7_low_0': 138,
                                                                             'mask_2_low_0': 657,
                                                                             'mask_3_low_0': 128,
                                                                             'mask_6_low_0': 220,
                                                                             'mask_2_low_1': 2,
                                                                             'mask_3_low_1': 1,
                                                                             'mask_4_low_0': 1,
                                                                             'mask_5_low_0': 1},
                                                     'termination': {'visible_target_change': 944,
                                                                     'visibility_lost_or_not_alive': 204},
                                                     'left_censored': 170,
                                                     'median_duration_ticks': 11.0,
                                                     'outcome_hp_change_median': 0.0,
                                                     'concurrent_movement_ticks': {'advance': 4597,
                                                                                   'hold': 9170,
                                                                                   'lateral': 370,
                                                                                   'withdraw': 461},
                                                     'prediction': {'actual_n': 288,
                                                                    'predicted_n': 239,
                                                                    'recall': 0.7569444444444444,
                                                                    'precision': 0.9121338912133892},
                                                     'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t750'},
                                    'target_structure': {'n': 560,
                                                         'episodes': 11,
                                                         'ticks': 32372,
                                                         'initiation_contexts': {'mask_6_low_0': 59,
                                                                                 'mask_7_low_0': 84,
                                                                                 'mask_5_low_0': 304,
                                                                                 'mask_4_low_0': 105,
                                                                                 'mask_7_low_1': 4,
                                                                                 'mask_5_low_1': 3,
                                                                                 'mask_3_low_0': 1},
                                                         'termination': {'visible_target_change': 516,
                                                                         'visibility_lost_or_not_alive': 38,
                                                                         'observer_dead': 2,
                                                                         'episode_end': 4},
                                                         'left_censored': 255,
                                                         'median_duration_ticks': 44.0,
                                                         'outcome_hp_change_median': 0.0,
                                                         'concurrent_movement_ticks': {'advance': 4789,
                                                                                       'hold': 26484,
                                                                                       'lateral': 993,
                                                                                       'withdraw': 106},
                                                         'prediction': {'actual_n': 128,
                                                                        'predicted_n': 10,
                                                                        'recall': 0.0546875,
                                                                        'precision': 0.7},
                                                         'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t737'},
                                    'advance': {'n': 422,
                                                'episodes': 11,
                                                'ticks': 9020,
                                                'initiation_contexts': {'mask_1_low_0': 151,
                                                                        'mask_3_low_0': 51,
                                                                        'mask_2_low_0': 15,
                                                                        'mask_7_low_0': 22,
                                                                        'mask_5_low_0': 105,
                                                                        'mask_1_low_1': 6,
                                                                        'mask_3_low_1': 5,
                                                                        'mask_4_low_0': 60,
                                                                        'mask_6_low_0': 5,
                                                                        'mask_5_low_1': 1,
                                                                        'mask_7_low_1': 1},
                                                'termination': {'visible_target_change': 275,
                                                                'movement_character_change': 95,
                                                                'visibility_lost_or_not_alive': 51,
                                                                'observer_dead': 1},
                                                'left_censored': 268,
                                                'median_duration_ticks': 19.0,
                                                'outcome_hp_change_median': 0.0,
                                                'concurrent_movement_ticks': {'advance': 9020},
                                                'prediction': {'actual_n': 60,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t3309'},
                                    'withdraw': {'n': 291,
                                                 'episodes': 11,
                                                 'ticks': 5735,
                                                 'initiation_contexts': {'mask_3_low_0': 71,
                                                                         'mask_3_low_1': 33,
                                                                         'mask_7_low_0': 30,
                                                                         'mask_5_low_0': 72,
                                                                         'mask_5_low_1': 22,
                                                                         'mask_2_low_0': 5,
                                                                         'mask_6_low_0': 16,
                                                                         'mask_1_low_0': 37,
                                                                         'mask_7_low_1': 5},
                                                 'termination': {'visible_target_change': 169,
                                                                 'visibility_lost_or_not_alive': 31,
                                                                 'movement_character_change': 91},
                                                 'left_censored': 7,
                                                 'median_duration_ticks': 8,
                                                 'outcome_hp_change_median': 0,
                                                 'concurrent_movement_ticks': {'withdraw': 5735},
                                                 'prediction': {'actual_n': 77,
                                                                'predicted_n': 14,
                                                                'recall': 0.05194805194805195,
                                                                'precision': 0.2857142857142857},
                                                 'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t1794'},
                                    'lateral': {'n': 50,
                                                'episodes': 11,
                                                'ticks': 642,
                                                'initiation_contexts': {'mask_3_low_0': 4,
                                                                        'mask_7_low_0': 6,
                                                                        'mask_5_low_0': 27,
                                                                        'mask_4_low_1': 4,
                                                                        'mask_6_low_0': 2,
                                                                        'mask_7_low_1': 2,
                                                                        'mask_1_low_1': 3,
                                                                        'mask_5_low_1': 1,
                                                                        'mask_4_low_0': 1},
                                                'termination': {'visible_target_change': 17,
                                                                'movement_character_change': 27,
                                                                'visibility_lost_or_not_alive': 6},
                                                'left_censored': 8,
                                                'median_duration_ticks': 9.5,
                                                'outcome_hp_change_median': 0.0,
                                                'concurrent_movement_ticks': {'lateral': 642},
                                                'prediction': {'actual_n': 12,
                                                               'predicted_n': 0,
                                                               'recall': 0.0,
                                                               'precision': None},
                                                'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t2820'},
                                    'hold': {'n': 879,
                                             'episodes': 11,
                                             'ticks': 8101,
                                             'initiation_contexts': {'mask_7_low_0': 93,
                                                                     'mask_3_low_0': 146,
                                                                     'mask_3_low_1': 20,
                                                                     'mask_1_low_0': 184,
                                                                     'mask_5_low_0': 314,
                                                                     'mask_5_low_1': 31,
                                                                     'mask_2_low_0': 26,
                                                                     'mask_6_low_0': 31,
                                                                     'mask_4_low_1': 11,
                                                                     'mask_4_low_0': 21,
                                                                     'mask_1_low_1': 1,
                                                                     'mask_7_low_1': 1},
                                             'termination': {'movement_character_change': 687,
                                                             'visible_target_change': 155,
                                                             'visibility_lost_or_not_alive': 37},
                                             'left_censored': 4,
                                             'median_duration_ticks': 8,
                                             'outcome_hp_change_median': 0,
                                             'concurrent_movement_ticks': {'hold': 8101},
                                             'prediction': {'actual_n': 286,
                                                            'predicted_n': 18,
                                                            'recall': 0.01048951048951049,
                                                            'precision': 0.16666666666666666},
                                             'example': 'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t1703'}},
                         'validation': {'n': 1466,
                                        'correct': 842,
                                        'accuracy': 0.5743519781718963,
                                        'population_correct': 690,
                                        'population_accuracy': 0.47066848567530695,
                                        'persistence_accuracy': 0.1684856753069577,
                                        'uniform_expected_accuracy': 0.17301695575911127,
                                        'cluster_uncertainty': {'clusters': 3,
                                                                'lift_95pct': [0.08189655172413793,
                                                                               0.11607142857142858],
                                                                'method': '2000 bootstrap resamples of '
                                                                          'distinct full observer '
                                                                          'trajectories; descriptive with '
                                                                          'few clusters'},
                                        'novel_trajectories': {'n': 794,
                                                               'correct': 474,
                                                               'accuracy': 0.5969773299748111,
                                                               'population_correct': 400,
                                                               'population_accuracy': 0.5037783375314862,
                                                               'persistence_accuracy': 0.1952141057934509,
                                                               'uniform_expected_accuracy': 0.1738694974211347},
                                        'novel_episode_ids': ['ereq_20fc56c5-3ea4-4945-89ff-4d32587a9dec',
                                                              'ereq_fa77ce60-00ed-448b-8bf0-30528c340b82'],
                                        'robustness_baselines': {'class': {'correct': 752,
                                                                           'n': 1466,
                                                                           'accuracy': 0.5129604365620737,
                                                                           'by_context': {'mask_5_low_1': {'correct': 3,
                                                                                                           'n': 16},
                                                                                          'mask_7_low_1': {'correct': 0,
                                                                                                           'n': 4},
                                                                                          'mask_5_low_0': {'correct': 252,
                                                                                                           'n': 537},
                                                                                          'mask_1_low_1': {'correct': 5,
                                                                                                           'n': 5},
                                                                                          'mask_3_low_1': {'correct': 0,
                                                                                                           'n': 10},
                                                                                          'mask_4_low_0': {'correct': 7,
                                                                                                           'n': 10},
                                                                                          'mask_1_low_0': {'correct': 135,
                                                                                                           'n': 240},
                                                                                          'mask_3_low_0': {'correct': 34,
                                                                                                           'n': 165},
                                                                                          'mask_6_low_0': {'correct': 68,
                                                                                                           'n': 82},
                                                                                          'mask_7_low_0': {'correct': 98,
                                                                                                           'n': 238},
                                                                                          'mask_4_low_1': {'correct': 0,
                                                                                                           'n': 2},
                                                                                          'mask_2_low_0': {'correct': 150,
                                                                                                           'n': 157}}},
                                                                 'side': {'correct': 692,
                                                                          'n': 1466,
                                                                          'accuracy': 0.47203274215552526,
                                                                          'by_context': {'mask_5_low_1': {'correct': 5,
                                                                                                          'n': 16},
                                                                                         'mask_7_low_1': {'correct': 0,
                                                                                                          'n': 4},
                                                                                         'mask_5_low_0': {'correct': 252,
                                                                                                          'n': 537},
                                                                                         'mask_1_low_1': {'correct': 5,
                                                                                                          'n': 5},
                                                                                         'mask_3_low_1': {'correct': 0,
                                                                                                          'n': 10},
                                                                                         'mask_4_low_0': {'correct': 7,
                                                                                                          'n': 10},
                                                                                         'mask_1_low_0': {'correct': 135,
                                                                                                          'n': 240},
                                                                                         'mask_3_low_0': {'correct': 34,
                                                                                                          'n': 165},
                                                                                         'mask_6_low_0': {'correct': 68,
                                                                                                          'n': 82},
                                                                                         'mask_7_low_0': {'correct': 36,
                                                                                                          'n': 238},
                                                                                         'mask_4_low_1': {'correct': 0,
                                                                                                          'n': 2},
                                                                                         'mask_2_low_0': {'correct': 150,
                                                                                                          'n': 157}}}},
                                        'by_episode': {'ereq_20fc56c5-3ea4-4945-89ff-4d32587a9dec': {'n': 330,
                                                                                                     'correct': 178,
                                                                                                     'accuracy': 0.5393939393939394,
                                                                                                     'population_correct': 142,
                                                                                                     'population_accuracy': 0.4303030303030303,
                                                                                                     'persistence_accuracy': 0.14242424242424243,
                                                                                                     'uniform_expected_accuracy': 0.17204906204906203},
                                                       'ereq_fa77ce60-00ed-448b-8bf0-30528c340b82': {'n': 464,
                                                                                                     'correct': 296,
                                                                                                     'accuracy': 0.6379310344827587,
                                                                                                     'population_correct': 258,
                                                                                                     'population_accuracy': 0.5560344827586207,
                                                                                                     'persistence_accuracy': 0.23275862068965517,
                                                                                                     'uniform_expected_accuracy': 0.17516420361247947},
                                                       'ereq_033c22c8-e976-4b7c-b05d-65b2e0ce6064': {'n': 336,
                                                                                                     'correct': 184,
                                                                                                     'accuracy': 0.5476190476190477,
                                                                                                     'population_correct': 145,
                                                                                                     'population_accuracy': 0.43154761904761907,
                                                                                                     'persistence_accuracy': 0.13690476190476192,
                                                                                                     'uniform_expected_accuracy': 0.1720096371882086},
                                                       'ereq_09fd9a45-9a05-4188-ae85-8a0db7690b69': {'n': 336,
                                                                                                     'correct': 184,
                                                                                                     'accuracy': 0.5476190476190477,
                                                                                                     'population_correct': 145,
                                                                                                     'population_accuracy': 0.43154761904761907,
                                                                                                     'persistence_accuracy': 0.13690476190476192,
                                                                                                     'uniform_expected_accuracy': 0.1720096371882086}},
                                        'by_observer_side': {'0': {'n': 464,
                                                                   'correct': 296,
                                                                   'accuracy': 0.6379310344827587,
                                                                   'population_correct': 258,
                                                                   'population_accuracy': 0.5560344827586207,
                                                                   'persistence_accuracy': 0.23275862068965517,
                                                                   'uniform_expected_accuracy': 0.17516420361247947},
                                                             '5': {'n': 1002,
                                                                   'correct': 546,
                                                                   'accuracy': 0.5449101796407185,
                                                                   'population_correct': 432,
                                                                   'population_accuracy': 0.4311377245508982,
                                                                   'persistence_accuracy': 0.13872255489021956,
                                                                   'uniform_expected_accuracy': 0.17202262142381905}}},
                         'proxy': {'usable': False,
                                   'rollouts': 0,
                                   'divergence': None,
                                   'reason': 'No executable skill controller or rollout validation. '
                                             'Boundary-conditional prediction alone cannot qualify a '
                                             'proxy.',
                                   'proposed_gate': {'skill_frequency_total_variation_max': 0.1,
                                                     'position_histogram_total_variation_max': 0.15,
                                                     'win_rate_absolute_gap_max': 0.1,
                                                     'note': 'Proposed future gate on novel seeds, both '
                                                             'sides; not tested or a certification.'}},
                         'observability': {'episodes': 20,
                                           'ticks': 203672,
                                           'living_opponent_ticks': 907699,
                                           'visible_living_opponent_ticks': 200988,
                                           'fraction': 0.22142582508078118,
                                           'all_scheduled_hero_tick_fraction': 0.197364389803213,
                                           'observer_dead_fraction': 0.14696669154326564,
                                           'residual_fraction': 0.07120325591577607,
                                           'segments': 8919,
                                           'eligible': 7601,
                                           'exclusions': {'left_censored': 1307,
                                                          'selected_skill_not_established_by_prior_affordances': 11}}},
            'claims': {'Jordan268_I_O03': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                    'structure; visible HP >100 THEY PREFER target_hero '
                                                    'OVER advance FOR hero_pressure (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O03',
                                                         'when': 'mask_1_low_0',
                                                         'skill': 'target_hero',
                                                         'over': 'advance',
                                                         'n': 629,
                                                         'chosen_count': 384,
                                                         'rate': 0.6104928457869634,
                                                         'context_n': 632,
                                                         'confidence': 0.6101426307448494,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 450,
                                                                       'chosen_count': 341,
                                                                       'rate': 0.7577777777777778},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h100.t7392',
                                                         'predictions': {'n': 240,
                                                                         'correct': 135,
                                                                         'accuracy': 0.5625,
                                                                         'population_correct': 135,
                                                                         'population_accuracy': 0.5625,
                                                                         'persistence_accuracy': 0.10416666666666667,
                                                                         'uniform_expected_accuracy': 0.20020833333333335},
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
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t986',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t2884',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t2896'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O04': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                    'structure; visible HP ≤100 THEY PREFER target_hero '
                                                    'OVER hold FOR hero_pressure (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O04',
                                                         'when': 'mask_1_low_1',
                                                         'skill': 'target_hero',
                                                         'over': 'hold',
                                                         'n': 20,
                                                         'chosen_count': 14,
                                                         'rate': 0.7,
                                                         'context_n': 20,
                                                         'confidence': 0.6818181818181818,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 49,
                                                                       'chosen_count': 17,
                                                                       'rate': 0.3469387755102041},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h103.t6822',
                                                         'predictions': {'n': 5,
                                                                         'correct': 5,
                                                                         'accuracy': 1.0,
                                                                         'population_correct': 5,
                                                                         'population_accuracy': 1.0,
                                                                         'persistence_accuracy': 0.2,
                                                                         'uniform_expected_accuracy': 0.2},
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
                                                         'supporting_episodes': 9,
                                                         'examples': ['ereq_3a830277-104c-47df-b45f-475f84adcbba.h103.t1826',
                                                                      'ereq_3a830277-104c-47df-b45f-475f84adcbba.h102.t1876',
                                                                      'ereq_c2933955-7e74-446e-944b-ef5c0ecdde47.h103.t1833'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O05': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                    'structure; visible HP >100 THEY PREFER target_creep '
                                                    'OVER advance FOR creep_contact (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O05',
                                                         'when': 'mask_2_low_0',
                                                         'skill': 'target_creep',
                                                         'over': 'advance',
                                                         'n': 555,
                                                         'chosen_count': 518,
                                                         'rate': 0.9333333333333333,
                                                         'context_n': 555,
                                                         'confidence': 0.9317773788150808,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 1091,
                                                                       'chosen_count': 1083,
                                                                       'rate': 0.9926672777268561},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h104.t6944',
                                                         'predictions': {'n': 157,
                                                                         'correct': 150,
                                                                         'accuracy': 0.9554140127388535,
                                                                         'population_correct': 150,
                                                                         'population_accuracy': 0.9554140127388535,
                                                                         'persistence_accuracy': 0.7261146496815286,
                                                                         'uniform_expected_accuracy': 0.20031847133757963},
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
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t1088',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t1096',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t1119'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O06': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                    'structure; visible HP ≤100 THEY PREFER target_creep '
                                                    'OVER withdraw FOR creep_contact (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O06',
                                                         'when': 'mask_2_low_1',
                                                         'skill': 'target_creep',
                                                         'over': 'withdraw',
                                                         'n': 2,
                                                         'chosen_count': 2,
                                                         'rate': 1.0,
                                                         'context_n': 2,
                                                         'confidence': 0.75,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 17,
                                                                       'chosen_count': 17,
                                                                       'rate': 1.0},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_c2933955-7e74-446e-944b-ef5c0ecdde47.h100.t3382',
                                                         'predictions': {'n': 0,
                                                                         'correct': 0,
                                                                         'accuracy': None,
                                                                         'population_correct': 0,
                                                                         'population_accuracy': None,
                                                                         'persistence_accuracy': None,
                                                                         'uniform_expected_accuracy': None},
                                                         'prediction_interval': {'clusters': 0,
                                                                                 'lift_95pct': None,
                                                                                 'note': 'Too few distinct '
                                                                                         'observable '
                                                                                         'trajectories'},
                                                         'supporting_episodes': 1,
                                                         'examples': ['ereq_c2933955-7e74-446e-944b-ef5c0ecdde47.h100.t3372',
                                                                      'ereq_c2933955-7e74-446e-944b-ef5c0ecdde47.h100.t3382'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O07': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                    'structure; visible HP >100 THEY PREFER target_hero '
                                                    'OVER target_creep FOR hero_pressure (hypothesis).',
                                           'status': 'supported',
                                           'evidence': [{'id': 'Jordan268_I_O07',
                                                         'when': 'mask_3_low_0',
                                                         'skill': 'target_hero',
                                                         'over': 'target_creep',
                                                         'n': 553,
                                                         'chosen_count': 219,
                                                         'rate': 0.3960216998191682,
                                                         'context_n': 553,
                                                         'confidence': 0.3963963963963964,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 1524,
                                                                       'chosen_count': 502,
                                                                       'rate': 0.3293963254593176},
                                                         'status': 'supported',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h100.t7382',
                                                         'predictions': {'n': 165,
                                                                         'correct': 63,
                                                                         'accuracy': 0.38181818181818183,
                                                                         'population_correct': 34,
                                                                         'population_accuracy': 0.20606060606060606,
                                                                         'persistence_accuracy': 0.16363636363636364,
                                                                         'uniform_expected_accuracy': 0.16787878787878788},
                                                         'prediction_interval': {'clusters': 3,
                                                                                 'lift_95pct': [0.04,
                                                                                                0.28888888888888886],
                                                                                 'method': '2000 bootstrap '
                                                                                           'resamples of '
                                                                                           'distinct full '
                                                                                           'observer '
                                                                                           'trajectories; '
                                                                                           'descriptive '
                                                                                           'with few '
                                                                                           'clusters'},
                                                         'supporting_episodes': 11,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t1763',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t1767',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t1767'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O08': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                    'structure; visible HP ≤100 THEY PREFER withdraw OVER '
                                                    'target_creep FOR preservation (hypothesis).',
                                           'status': 'supported',
                                           'evidence': [{'id': 'Jordan268_I_O08',
                                                         'when': 'mask_3_low_1',
                                                         'skill': 'withdraw',
                                                         'over': 'target_creep',
                                                         'n': 75,
                                                         'chosen_count': 32,
                                                         'rate': 0.4266666666666667,
                                                         'context_n': 75,
                                                         'confidence': 0.42857142857142855,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 69,
                                                                       'chosen_count': 2,
                                                                       'rate': 0.028985507246376812},
                                                         'status': 'supported',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_e3bf4a52-1935-4b75-b94f-6029e4147b3f.h105.t6337',
                                                         'predictions': {'n': 10,
                                                                         'correct': 4,
                                                                         'accuracy': 0.4,
                                                                         'population_correct': 0,
                                                                         'population_accuracy': 0.0,
                                                                         'persistence_accuracy': 0.0,
                                                                         'uniform_expected_accuracy': 0.16666666666666666},
                                                         'prediction_interval': {'clusters': 1,
                                                                                 'lift_95pct': None,
                                                                                 'note': 'Too few distinct '
                                                                                         'observable '
                                                                                         'trajectories'},
                                                         'supporting_episodes': 9,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t1792',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t1955',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t1964'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O09': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                    'hero/creep; visible HP >100 THEY PREFER '
                                                    'target_structure OVER hold FOR structure_pressure '
                                                    '(hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O09',
                                                         'when': 'mask_4_low_0',
                                                         'skill': 'target_structure',
                                                         'over': 'hold',
                                                         'n': 54,
                                                         'chosen_count': 18,
                                                         'rate': 0.3333333333333333,
                                                         'context_n': 54,
                                                         'confidence': 0.3392857142857143,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 184,
                                                                       'chosen_count': 137,
                                                                       'rate': 0.7445652173913043},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h101.t7732',
                                                         'predictions': {'n': 10,
                                                                         'correct': 7,
                                                                         'accuracy': 0.7,
                                                                         'population_correct': 7,
                                                                         'population_accuracy': 0.7,
                                                                         'persistence_accuracy': 0.0,
                                                                         'uniform_expected_accuracy': 0.2},
                                                         'prediction_interval': {'clusters': 1,
                                                                                 'lift_95pct': None,
                                                                                 'note': 'Too few distinct '
                                                                                         'observable '
                                                                                         'trajectories'},
                                                         'supporting_episodes': 8,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t9022',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h108.t9027',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t9269'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O10': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                    'hero/creep; visible HP ≤100 THEY PREFER hold OVER '
                                                    'lateral FOR unresolved (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O10',
                                                         'when': 'mask_4_low_1',
                                                         'skill': 'hold',
                                                         'over': 'lateral',
                                                         'n': 13,
                                                         'chosen_count': 11,
                                                         'rate': 0.8461538461538461,
                                                         'context_n': 13,
                                                         'confidence': 0.8,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 0,
                                                                       'chosen_count': 0,
                                                                       'rate': None},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h102.t8087',
                                                         'predictions': {'n': 2,
                                                                         'correct': 1,
                                                                         'accuracy': 0.5,
                                                                         'population_correct': 0,
                                                                         'population_accuracy': 0.0,
                                                                         'persistence_accuracy': 0.0,
                                                                         'uniform_expected_accuracy': 0.2},
                                                         'prediction_interval': {'clusters': 1,
                                                                                 'lift_95pct': None,
                                                                                 'note': 'Too few distinct '
                                                                                         'observable '
                                                                                         'trajectories'},
                                                         'supporting_episodes': 5,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t7952',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t7978',
                                                                      'ereq_975636fd-c5ad-487c-b47a-dbc39dfbb70e.h102.t8069'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O11': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                    'nearby creep; visible HP >100 THEY PREFER target_hero '
                                                    'OVER target_structure FOR hero_pressure (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O11',
                                                         'when': 'mask_5_low_0',
                                                         'skill': 'target_hero',
                                                         'over': 'target_structure',
                                                         'n': 1357,
                                                         'chosen_count': 649,
                                                         'rate': 0.4782608695652174,
                                                         'context_n': 1357,
                                                         'confidence': 0.4782928623988227,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 338,
                                                                       'chosen_count': 263,
                                                                       'rate': 0.7781065088757396},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h101.t8817',
                                                         'predictions': {'n': 537,
                                                                         'correct': 252,
                                                                         'accuracy': 0.4692737430167598,
                                                                         'population_correct': 252,
                                                                         'population_accuracy': 0.4692737430167598,
                                                                         'persistence_accuracy': 0.048417132216014895,
                                                                         'uniform_expected_accuracy': 0.16685288640595902},
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
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t901',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t901',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t910'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O12': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                    'nearby creep; visible HP ≤100 THEY PREFER hold OVER '
                                                    'target_hero FOR unresolved (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O12',
                                                         'when': 'mask_5_low_1',
                                                         'skill': 'hold',
                                                         'over': 'target_hero',
                                                         'n': 82,
                                                         'chosen_count': 31,
                                                         'rate': 0.3780487804878049,
                                                         'context_n': 82,
                                                         'confidence': 0.38095238095238093,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 26,
                                                                       'chosen_count': 3,
                                                                       'rate': 0.11538461538461539},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h104.t8627',
                                                         'predictions': {'n': 16,
                                                                         'correct': 2,
                                                                         'accuracy': 0.125,
                                                                         'population_correct': 3,
                                                                         'population_accuracy': 0.1875,
                                                                         'persistence_accuracy': 0.0,
                                                                         'uniform_expected_accuracy': 0.16666666666666666},
                                                         'prediction_interval': {'clusters': 3,
                                                                                 'lift_95pct': [-0.25, 0.0],
                                                                                 'method': '2000 bootstrap '
                                                                                           'resamples of '
                                                                                           'distinct full '
                                                                                           'observer '
                                                                                           'trajectories; '
                                                                                           'descriptive '
                                                                                           'with few '
                                                                                           'clusters'},
                                                         'supporting_episodes': 11,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h106.t4230',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t5651',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h105.t5658'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O13': {'claim': 'WHEN nearby=our creep + our exposed structure; no '
                                                    'nearby hero; visible HP >100 THEY PREFER target_creep '
                                                    'OVER target_structure FOR creep_contact (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O13',
                                                         'when': 'mask_6_low_0',
                                                         'skill': 'target_creep',
                                                         'over': 'target_structure',
                                                         'n': 267,
                                                         'chosen_count': 201,
                                                         'rate': 0.7528089887640449,
                                                         'context_n': 267,
                                                         'confidence': 0.7509293680297398,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 556,
                                                                       'chosen_count': 435,
                                                                       'rate': 0.7823741007194245},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h103.t8224',
                                                         'predictions': {'n': 82,
                                                                         'correct': 68,
                                                                         'accuracy': 0.8292682926829268,
                                                                         'population_correct': 68,
                                                                         'population_accuracy': 0.8292682926829268,
                                                                         'persistence_accuracy': 0.24390243902439024,
                                                                         'uniform_expected_accuracy': 0.17642276422764228},
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
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t6314',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t6342',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t6374'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O15': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                    'structure; visible HP >100 THEY PREFER target_hero '
                                                    'OVER target_creep FOR hero_pressure (hypothesis).',
                                           'status': 'supported',
                                           'evidence': [{'id': 'Jordan268_I_O15',
                                                         'when': 'mask_7_low_0',
                                                         'skill': 'target_hero',
                                                         'over': 'target_creep',
                                                         'n': 677,
                                                         'chosen_count': 360,
                                                         'rate': 0.5317577548005908,
                                                         'context_n': 677,
                                                         'confidence': 0.5316642120765832,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 287,
                                                                       'chosen_count': 81,
                                                                       'rate': 0.28222996515679444},
                                                         'status': 'supported',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_66edaa67-cd21-4285-b307-138a47fdfa0b.h103.t8648',
                                                         'predictions': {'n': 238,
                                                                         'correct': 155,
                                                                         'accuracy': 0.6512605042016807,
                                                                         'population_correct': 36,
                                                                         'population_accuracy': 0.15126050420168066,
                                                                         'persistence_accuracy': 0.14285714285714285,
                                                                         'uniform_expected_accuracy': 0.14315726290516206},
                                                         'prediction_interval': {'clusters': 3,
                                                                                 'lift_95pct': [0.1111111111111111,
                                                                                                0.6440677966101694],
                                                                                 'method': '2000 bootstrap '
                                                                                           'resamples of '
                                                                                           'distinct full '
                                                                                           'observer '
                                                                                           'trajectories; '
                                                                                           'descriptive '
                                                                                           'with few '
                                                                                           'clusters'},
                                                         'supporting_episodes': 11,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t750',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t756',
                                                                      'ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h109.t770'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]},
                       'Jordan268_I_O16': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                    'structure; visible HP ≤100 THEY PREFER withdraw OVER '
                                                    'target_creep FOR preservation (hypothesis).',
                                           'status': 'requires_review',
                                           'evidence': [{'id': 'Jordan268_I_O16',
                                                         'when': 'mask_7_low_1',
                                                         'skill': 'withdraw',
                                                         'over': 'target_creep',
                                                         'n': 14,
                                                         'chosen_count': 5,
                                                         'rate': 0.35714285714285715,
                                                         'context_n': 14,
                                                         'confidence': 0.375,
                                                         'confidence_meaning': 'Laplace-smoothed observed '
                                                                               'selection probability, not '
                                                                               'probability of hidden '
                                                                               'intent; correlated '
                                                                               'segments',
                                                         'base_rate': {'source': '21-episode population '
                                                                                 'prior, same context and '
                                                                                 'paired affordances',
                                                                       'n': 32,
                                                                       'chosen_count': 2,
                                                                       'rate': 0.0625},
                                                         'status': 'provisional',
                                                         'level': 'individual',
                                                         'opponent': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
                                                         'last_observed': 'ereq_e3bf4a52-1935-4b75-b94f-6029e4147b3f.h107.t1625',
                                                         'predictions': {'n': 4,
                                                                         'correct': 0,
                                                                         'accuracy': 0.0,
                                                                         'population_correct': 0,
                                                                         'population_accuracy': 0.0,
                                                                         'persistence_accuracy': 0.0,
                                                                         'uniform_expected_accuracy': 0.14285714285714285},
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
                                                         'supporting_episodes': 8,
                                                         'examples': ['ereq_354100a3-f8be-435e-bde3-d7be87494b0f.h107.t1625',
                                                                      'ereq_3a830277-104c-47df-b45f-475f84adcbba.h104.t850',
                                                                      'ereq_3a830277-104c-47df-b45f-475f84adcbba.h101.t6406'],
                                                         'unresolved_constraints': 'Enemy '
                                                                                   'cooldowns/private '
                                                                                   'memory and full route '
                                                                                   'execution unavailable. '
                                                                                   'Hold can be '
                                                                                   'turning/collision; '
                                                                                   'always provisional.',
                                                         'counterstrategy_status': 'proposed_test_only; no '
                                                                                   'exploitation attempt '
                                                                                   'or validated rollout '
                                                                                   'proxy'}]}}},
 'goal': {'hero_pressure': {'preference': 'Hypothesis: hero contact outranks creep contact in the counted '
                                          'contexts. No inference of kill intent or willingness to '
                                          'sacrifice structures.',
                            'provenance': 'interpretation'},
          'creep_contact': {'preference': 'Hypothesis: maintain creep contact. XP, gold and last-hit '
                                          'optimization are not observed.',
                            'provenance': 'interpretation'},
          'structure_pressure': {'preference': 'Hypothesis: pressure exposed structures. Target selection '
                                               'is weaker evidence than realized damage.',
                                 'provenance': 'interpretation'},
          'territory_pressure': {'preference': 'Hypothesis: gain proximity to our god. Intended route/end '
                                               'point remains unknown.',
                                 'provenance': 'interpretation'},
          'preservation': {'preference': 'Hypothesis: create distance at low absolute HP; geometry alone '
                                         'does not establish safety-seeking.',
                           'provenance': 'interpretation'},
          'reposition': {'preference': 'Hypothesis: lateral relocation; tactical purpose unresolved.',
                         'provenance': 'interpretation'},
          'unresolved': {'preference': 'Goal unknown: stationary motion alone does not establish voluntary '
                                       'holding.',
                         'provenance': 'unknown'}},
 'skill': {'target_hero': {'operator': 'observed_target_hero', 'parameters': {'minimum_segment_ticks': 6}},
           'target_creep': {'operator': 'observed_target_creep',
                            'parameters': {'minimum_segment_ticks': 6}},
           'target_structure': {'operator': 'observed_target_structure',
                                'parameters': {'minimum_segment_ticks': 6}},
           'advance': {'operator': 'observed_advance', 'parameters': {'minimum_segment_ticks': 6}},
           'withdraw': {'operator': 'observed_withdraw', 'parameters': {'minimum_segment_ticks': 6}},
           'lateral': {'operator': 'observed_lateral', 'parameters': {'minimum_segment_ticks': 6}},
           'hold': {'operator': 'observed_hold', 'parameters': {'minimum_segment_ticks': 6}}},
 'strategy': [{'id': 'Jordan268_I_O03',
               'when': 'mask_1_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Jordan268_I_O04',
               'when': 'mask_1_low_1',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Jordan268_I_O05',
               'when': 'mask_2_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Jordan268_I_O06',
               'when': 'mask_2_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Jordan268_I_O07',
               'when': 'mask_3_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Jordan268_I_O08',
               'when': 'mask_3_low_1',
               'skill': 'withdraw',
               'for': ['preservation']},
              {'id': 'Jordan268_I_O09',
               'when': 'mask_4_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'Jordan268_I_O10', 'when': 'mask_4_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Jordan268_I_O11',
               'when': 'mask_5_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Jordan268_I_O12', 'when': 'mask_5_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Jordan268_I_O13',
               'when': 'mask_6_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Jordan268_I_O15',
               'when': 'mask_7_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Jordan268_I_O16',
               'when': 'mask_7_low_1',
               'skill': 'withdraw',
               'for': ['preservation']}],
 'execution': {'binding': 'gota-observer-model/1', 'game_version': '2026.9.16.5', 'language': 'Python'},
 'update': {'revision': 1,
            'parent': None,
            'change': {'origin': 'observable_replay_inference',
                       'level': 'individual',
                       'parameters': {'minimum_segment_ticks': 6,
                                      'opportunity_radius_tiles': 12,
                                      'low_hp_absolute': 100,
                                      'motion_min_world_units': 1000,
                                      'radial_cosine_threshold': 0.35,
                                      'local_route_check_tiles': 2},
                       'frozen_model_sha256': '343465db0de3f03344ba832e2df29005b2178405bb993f7c778fb3948a3f44ef',
                       'semantics': 'Rule records share primary id/when/skill/for layout; they express '
                                    'forecasts, not an inferred execution order or a claim that only one '
                                    'source rule fires. predictor distribution governs context backoff and '
                                    'unavailable-skill masking.'},
            'needs_review': ['Unvalidated rollout proxy',
                             'No exploitation experiment',
                             'Unknown abilities and cooldowns',
                             'Class/side/phase confounding',
                             '22% visibility and few distinct heldout trajectories'],
            'evidence': [{'artifact': 'docs/opponents/jordan-v268/evidence.json',
                          'guide': 'guide-opponent-model-ir.md',
                          'model_level': 'individual'}]}}
