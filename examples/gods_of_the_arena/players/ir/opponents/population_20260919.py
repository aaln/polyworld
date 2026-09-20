"""Inferred opponent IR in the primary seven-layer Python dictionary layout.

Generated from frozen observer evidence; no private opponent code or VM commands.
Use opponent_ir.validate / predict; this is not a BASIC or rollout policy.
"""

MODEL = {'schema': 'gota-semantic-opponent/1',
 'id': 'gota_field_20260919_observer_prior',
 'situation': {'grounded': {'observation': 'Single owned hero slot 0/5, exact predecision host-visible '
                                           'snapshots. Predictor uses tick t-1; inferred motif begins at t '
                                           'and must last at least 6 ticks (0.25s at 24 Hz).',
                            'structure_alive': 'For structures, objectAlive means exposed; positive HP '
                                               'means standing. A zero visible target means none OR '
                                               'hidden.',
                            'predicates': {'mask_0_low_0': 'nearby=none; no nearby hero/creep/exposed '
                                                           'structure; visible HP >100',
                                           'mask_1_low_0': 'nearby=our hero; no nearby creep/exposed '
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
                                           'mask_5_low_0': 'nearby=our hero + our exposed structure; no '
                                                           'nearby creep; visible HP >100',
                                           'mask_5_low_1': 'nearby=our hero + our exposed structure; no '
                                                           'nearby creep; visible HP ≤100',
                                           'mask_6_low_0': 'nearby=our creep + our exposed structure; no '
                                                           'nearby hero; visible HP >100',
                                           'mask_6_low_1': 'nearby=our creep + our exposed structure; no '
                                                           'nearby hero; visible HP ≤100',
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
 'belief': {'grounded': {'level': 'population',
                         'opponent_version': 'sampled_field_20260919',
                         'our_policy': {'id': 'gota_relh154_legacy',
                                        'schema': 'gota-semantic-policy/1',
                                        'canonical_sha256': '8e4eb95f2cd8a9dd2702a5b4e13a7ceb541db803e04c70cea11b33bf5839ce37',
                                        'basic_sha256': 'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'},
                         'memory': 'No private opponent memory inferred. Individual estimates are frozen; '
                                   'no persistent in-episode updates are asserted.',
                         'uncertainty': 'Partial visibility, correlated trajectories, estimated '
                                        'affordances, and retrospective event boundaries. Absence from '
                                        'view is not absence from game.',
                         'predictor': {'contexts': {'mask_0_low_0': {'advance': 4},
                                                    'mask_1_low_0': {'advance': 51,
                                                                     'target_hero': 345,
                                                                     'withdraw': 10,
                                                                     'lateral': 19,
                                                                     'hold': 31},
                                                    'mask_1_low_1': {'lateral': 7,
                                                                     'target_hero': 17,
                                                                     'hold': 12,
                                                                     'withdraw': 10,
                                                                     'advance': 3},
                                                    'mask_2_low_0': {'target_creep': 1107,
                                                                     'hold': 3,
                                                                     'advance': 5},
                                                    'mask_2_low_1': {'target_creep': 17},
                                                    'mask_3_low_0': {'target_creep': 970,
                                                                     'target_hero': 502,
                                                                     'hold': 13,
                                                                     'withdraw': 9,
                                                                     'lateral': 6,
                                                                     'advance': 24},
                                                    'mask_3_low_1': {'target_creep': 35,
                                                                     'target_hero': 21,
                                                                     'withdraw': 2,
                                                                     'hold': 4,
                                                                     'advance': 7},
                                                    'mask_4_low_0': {'target_structure': 137,
                                                                     'hold': 31,
                                                                     'withdraw': 6,
                                                                     'advance': 8,
                                                                     'lateral': 2},
                                                    'mask_5_low_0': {'target_structure': 42,
                                                                     'target_hero': 263,
                                                                     'hold': 19,
                                                                     'withdraw': 6,
                                                                     'lateral': 1,
                                                                     'advance': 7},
                                                    'mask_5_low_1': {'advance': 4,
                                                                     'hold': 3,
                                                                     'target_hero': 9,
                                                                     'target_structure': 2,
                                                                     'withdraw': 8},
                                                    'mask_6_low_0': {'target_structure': 104,
                                                                     'target_creep': 435,
                                                                     'hold': 10,
                                                                     'withdraw': 4,
                                                                     'advance': 3},
                                                    'mask_6_low_1': {'target_creep': 1},
                                                    'mask_7_low_0': {'target_creep': 171,
                                                                     'target_hero': 81,
                                                                     'target_structure': 21,
                                                                     'hold': 6,
                                                                     'advance': 3,
                                                                     'withdraw': 2,
                                                                     'lateral': 3},
                                                    'mask_7_low_1': {'target_hero': 9,
                                                                     'hold': 6,
                                                                     'advance': 3,
                                                                     'target_creep': 13,
                                                                     'lateral': 1,
                                                                     'withdraw': 2}},
                                       'global': {'target_creep': 2749,
                                                  'target_hero': 1247,
                                                  'target_structure': 306,
                                                  'advance': 122,
                                                  'hold': 138,
                                                  'withdraw': 59,
                                                  'lateral': 39},
                                       'smoothing': 'Laplace +1 over estimated available skills; context '
                                                    'backs off globally if n<8'},
                         'skills': {'target_hero': {'n': 1648,
                                                    'episodes': 21,
                                                    'ticks': 75219,
                                                    'initiation_contexts': {'mask_7_low_0': 82,
                                                                            'mask_5_low_0': 280,
                                                                            'mask_1_low_0': 570,
                                                                            'mask_3_low_0': 648,
                                                                            'mask_3_low_1': 21,
                                                                            'mask_1_low_1': 19,
                                                                            'mask_7_low_1': 9,
                                                                            'mask_4_low_0': 7,
                                                                            'mask_5_low_1': 9,
                                                                            'mask_0_low_0': 1,
                                                                            'mask_6_low_1': 1,
                                                                            'mask_2_low_0': 1},
                                                    'termination': {'visible_target_change': 775,
                                                                    'visibility_lost_or_not_alive': 789,
                                                                    'episode_end': 12,
                                                                    'observer_dead': 72},
                                                    'left_censored': 396,
                                                    'prediction': {'n': 0, 'accuracy': None},
                                                    'confidence': 'Motif definition only; population '
                                                                  'prediction unvalidated'},
                                    'target_creep': {'n': 3593,
                                                     'episodes': 21,
                                                     'ticks': 48509,
                                                     'initiation_contexts': {'mask_7_low_0': 181,
                                                                             'mask_3_low_0': 1135,
                                                                             'mask_3_low_1': 37,
                                                                             'mask_2_low_0': 1628,
                                                                             'mask_2_low_1': 27,
                                                                             'mask_5_low_0': 14,
                                                                             'mask_4_low_0': 37,
                                                                             'mask_6_low_0': 516,
                                                                             'mask_7_low_1': 14,
                                                                             'mask_4_low_1': 1,
                                                                             'mask_0_low_0': 2,
                                                                             'mask_6_low_1': 1},
                                                     'termination': {'visible_target_change': 2929,
                                                                     'visibility_lost_or_not_alive': 660,
                                                                     'observer_dead': 4},
                                                     'left_censored': 793,
                                                     'prediction': {'n': 0, 'accuracy': None},
                                                     'confidence': 'Motif definition only; population '
                                                                   'prediction unvalidated'},
                                    'target_structure': {'n': 587,
                                                         'episodes': 21,
                                                         'ticks': 47224,
                                                         'initiation_contexts': {'mask_5_low_0': 85,
                                                                                 'mask_6_low_0': 159,
                                                                                 'mask_7_low_0': 27,
                                                                                 'mask_4_low_0': 292,
                                                                                 'mask_0_low_0': 12,
                                                                                 'mask_5_low_1': 2,
                                                                                 'mask_1_low_0': 6,
                                                                                 'mask_2_low_0': 3,
                                                                                 'mask_6_low_1': 1},
                                                         'termination': {'visibility_lost_or_not_alive': 155,
                                                                         'visible_target_change': 410,
                                                                         'episode_end': 15,
                                                                         'observer_dead': 7},
                                                         'left_censored': 273,
                                                         'prediction': {'n': 0, 'accuracy': None},
                                                         'confidence': 'Motif definition only; population '
                                                                       'prediction unvalidated'},
                                    'advance': {'n': 362,
                                                'episodes': 17,
                                                'ticks': 8994,
                                                'initiation_contexts': {'mask_1_low_0': 122,
                                                                        'mask_3_low_1': 8,
                                                                        'mask_3_low_0': 66,
                                                                        'mask_4_low_0': 55,
                                                                        'mask_5_low_1': 4,
                                                                        'mask_7_low_1': 3,
                                                                        'mask_0_low_0': 41,
                                                                        'mask_5_low_0': 16,
                                                                        'mask_2_low_0': 28,
                                                                        'mask_7_low_0': 8,
                                                                        'mask_6_low_0': 4,
                                                                        'mask_1_low_1': 6,
                                                                        'mask_4_low_1': 1},
                                                'termination': {'visible_target_change': 211,
                                                                'movement_character_change': 57,
                                                                'visibility_lost_or_not_alive': 90,
                                                                'episode_end': 3,
                                                                'observer_dead': 1},
                                                'left_censored': 237,
                                                'prediction': {'n': 0, 'accuracy': None},
                                                'confidence': 'Motif definition only; population '
                                                              'prediction unvalidated'},
                                    'withdraw': {'n': 88,
                                                 'episodes': 9,
                                                 'ticks': 2476,
                                                 'initiation_contexts': {'mask_3_low_0': 16,
                                                                         'mask_1_low_0': 19,
                                                                         'mask_3_low_1': 2,
                                                                         'mask_4_low_0': 6,
                                                                         'mask_6_low_0': 4,
                                                                         'mask_5_low_0': 6,
                                                                         'mask_5_low_1': 8,
                                                                         'mask_1_low_1': 19,
                                                                         'mask_7_low_0': 5,
                                                                         'mask_7_low_1': 2,
                                                                         'mask_2_low_0': 1},
                                                 'termination': {'visibility_lost_or_not_alive': 22,
                                                                 'visible_target_change': 26,
                                                                 'movement_character_change': 39,
                                                                 'episode_end': 1},
                                                 'left_censored': 11,
                                                 'prediction': {'n': 0, 'accuracy': None},
                                                 'confidence': 'Motif definition only; population '
                                                               'prediction unvalidated'},
                                    'lateral': {'n': 68,
                                                'episodes': 11,
                                                'ticks': 1554,
                                                'initiation_contexts': {'mask_3_low_0': 17,
                                                                        'mask_1_low_0': 34,
                                                                        'mask_1_low_1': 7,
                                                                        'mask_0_low_0': 1,
                                                                        'mask_7_low_1': 1,
                                                                        'mask_7_low_0': 3,
                                                                        'mask_5_low_0': 1,
                                                                        'mask_2_low_0': 2,
                                                                        'mask_4_low_0': 2},
                                                'termination': {'visible_target_change': 33,
                                                                'movement_character_change': 23,
                                                                'visibility_lost_or_not_alive': 12},
                                                'left_censored': 29,
                                                'prediction': {'n': 0, 'accuracy': None},
                                                'confidence': 'Motif definition only; population '
                                                              'prediction unvalidated'},
                                    'hold': {'n': 143,
                                             'episodes': 14,
                                             'ticks': 2462,
                                             'initiation_contexts': {'mask_3_low_0': 15,
                                                                     'mask_1_low_0': 33,
                                                                     'mask_1_low_1': 12,
                                                                     'mask_4_low_0': 32,
                                                                     'mask_7_low_1': 6,
                                                                     'mask_5_low_1': 3,
                                                                     'mask_6_low_0': 10,
                                                                     'mask_5_low_0': 19,
                                                                     'mask_7_low_0': 6,
                                                                     'mask_2_low_0': 3,
                                                                     'mask_3_low_1': 4},
                                             'termination': {'movement_character_change': 103,
                                                             'visible_target_change': 19,
                                                             'visibility_lost_or_not_alive': 20,
                                                             'episode_end': 1},
                                             'left_censored': 5,
                                             'prediction': {'n': 0, 'accuracy': None},
                                             'confidence': 'Motif definition only; population prediction '
                                                           'unvalidated'}},
                         'validation': {'population_generalization': 'not independently validated',
                                        'baseline_on_jordan': 0.47066848567530695},
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
                         'observability': {'episodes': 21,
                                           'ticks': 241566,
                                           'living_opponent_ticks': 1076818,
                                           'visible_living_opponent_ticks': 198677,
                                           'fraction': 0.18450378801245892,
                                           'all_scheduled_hero_tick_fraction': 0.1644908637804989,
                                           'observer_dead_fraction': 0.06274889678183188,
                                           'residual_fraction': 0.06160250054107924,
                                           'segments': 6489,
                                           'eligible': 4660,
                                           'exclusions': {'left_censored': 1744,
                                                          'selected_skill_not_established_by_prior_affordances': 85}}},
            'claims': {'GotaField20260919_P_O01': {'claim': 'WHEN nearby=none; no nearby '
                                                            'hero/creep/exposed structure; visible HP >100 '
                                                            'THEY PREFER advance OVER withdraw FOR '
                                                            'territory_pressure (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O01',
                                                                 'when': 'mask_0_low_0',
                                                                 'skill': 'advance',
                                                                 'over': 'withdraw',
                                                                 'n': 4,
                                                                 'chosen_count': 4,
                                                                 'confidence': 0.8333333333333334,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.25,
                                                                               'n': 4},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_5cf577c7-ee4b-462b-9d96-9b4add399e42.h106.t4473',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O03': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                            'structure; visible HP >100 THEY PREFER '
                                                            'target_hero OVER advance FOR hero_pressure '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O03',
                                                                 'when': 'mask_1_low_0',
                                                                 'skill': 'target_hero',
                                                                 'over': 'advance',
                                                                 'n': 450,
                                                                 'chosen_count': 341,
                                                                 'confidence': 0.7566371681415929,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.2018888888888889,
                                                                               'n': 450},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h106.t3205',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O04': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                            'structure; visible HP ≤100 THEY PREFER '
                                                            'target_hero OVER hold FOR hero_pressure '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O04',
                                                                 'when': 'mask_1_low_1',
                                                                 'skill': 'target_hero',
                                                                 'over': 'hold',
                                                                 'n': 49,
                                                                 'chosen_count': 17,
                                                                 'confidence': 0.35294117647058826,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.20408163265306123,
                                                                               'n': 49},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h108.t1170',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O05': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                            'structure; visible HP >100 THEY PREFER '
                                                            'target_creep OVER advance FOR creep_contact '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O05',
                                                                 'when': 'mask_2_low_0',
                                                                 'skill': 'target_creep',
                                                                 'over': 'advance',
                                                                 'n': 1091,
                                                                 'chosen_count': 1083,
                                                                 'confidence': 0.9917657822506862,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.20114573785517875,
                                                                               'n': 1091},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h107.t2533',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O06': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                            'structure; visible HP ≤100 THEY PREFER '
                                                            'target_creep OVER withdraw FOR creep_contact '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O06',
                                                                 'when': 'mask_2_low_1',
                                                                 'skill': 'target_creep',
                                                                 'over': 'withdraw',
                                                                 'n': 17,
                                                                 'chosen_count': 17,
                                                                 'confidence': 0.9473684210526315,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.2,
                                                                               'n': 17},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_ed937886-1075-4c52-a876-1ec765195df3.h107.t3100',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O07': {'claim': 'WHEN nearby=our hero + our creep; no nearby '
                                                            'exposed structure; visible HP >100 THEY '
                                                            'PREFER target_creep OVER target_hero FOR '
                                                            'creep_contact (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O07',
                                                                 'when': 'mask_3_low_0',
                                                                 'skill': 'target_creep',
                                                                 'over': 'target_hero',
                                                                 'n': 1524,
                                                                 'chosen_count': 970,
                                                                 'confidence': 0.6363040629095675,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.16917104111986,
                                                                               'n': 1524},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h105.t3142',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O08': {'claim': 'WHEN nearby=our hero + our creep; no nearby '
                                                            'exposed structure; visible HP ≤100 THEY '
                                                            'PREFER target_creep OVER target_hero FOR '
                                                            'creep_contact (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O08',
                                                                 'when': 'mask_3_low_1',
                                                                 'skill': 'target_creep',
                                                                 'over': 'target_hero',
                                                                 'n': 69,
                                                                 'chosen_count': 35,
                                                                 'confidence': 0.5070422535211268,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.16666666666666666,
                                                                               'n': 69},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h109.t2068',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O09': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                            'hero/creep; visible HP >100 THEY PREFER '
                                                            'target_structure OVER hold FOR '
                                                            'structure_pressure (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O09',
                                                                 'when': 'mask_4_low_0',
                                                                 'skill': 'target_structure',
                                                                 'over': 'hold',
                                                                 'n': 184,
                                                                 'chosen_count': 137,
                                                                 'confidence': 0.7419354838709677,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.2,
                                                                               'n': 184},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h105.t4768',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O11': {'claim': 'WHEN nearby=our hero + our exposed structure; '
                                                            'no nearby creep; visible HP >100 THEY PREFER '
                                                            'target_hero OVER target_structure FOR '
                                                            'hero_pressure (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O11',
                                                                 'when': 'mask_5_low_0',
                                                                 'skill': 'target_hero',
                                                                 'over': 'target_structure',
                                                                 'n': 338,
                                                                 'chosen_count': 263,
                                                                 'confidence': 0.7764705882352941,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.1675542406311637,
                                                                               'n': 338},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h106.t928',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O12': {'claim': 'WHEN nearby=our hero + our exposed structure; '
                                                            'no nearby creep; visible HP ≤100 THEY PREFER '
                                                            'target_hero OVER withdraw FOR hero_pressure '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O12',
                                                                 'when': 'mask_5_low_1',
                                                                 'skill': 'target_hero',
                                                                 'over': 'withdraw',
                                                                 'n': 26,
                                                                 'chosen_count': 9,
                                                                 'confidence': 0.35714285714285715,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.16666666666666666,
                                                                               'n': 26},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_7c5d2590-7451-44be-91c0-0fa466ac7a15.h108.t10496',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O13': {'claim': 'WHEN nearby=our creep + our exposed '
                                                            'structure; no nearby hero; visible HP >100 '
                                                            'THEY PREFER target_creep OVER '
                                                            'target_structure FOR creep_contact '
                                                            '(hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O13',
                                                                 'when': 'mask_6_low_0',
                                                                 'skill': 'target_creep',
                                                                 'over': 'target_structure',
                                                                 'n': 556,
                                                                 'chosen_count': 435,
                                                                 'confidence': 0.7813620071684588,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.16819544364508393,
                                                                               'n': 556},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h107.t3475',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O14': {'claim': 'WHEN nearby=our creep + our exposed '
                                                            'structure; no nearby hero; visible HP ≤100 '
                                                            'THEY PREFER target_creep OVER withdraw FOR '
                                                            'creep_contact (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O14',
                                                                 'when': 'mask_6_low_1',
                                                                 'skill': 'target_creep',
                                                                 'over': 'withdraw',
                                                                 'n': 1,
                                                                 'chosen_count': 1,
                                                                 'confidence': 0.6666666666666666,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.16666666666666666,
                                                                               'n': 1},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_ed937886-1075-4c52-a876-1ec765195df3.h107.t9782',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O15': {'claim': 'WHEN nearby=our hero + our creep + our '
                                                            'exposed structure; visible HP >100 THEY '
                                                            'PREFER target_creep OVER target_hero FOR '
                                                            'creep_contact (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O15',
                                                                 'when': 'mask_7_low_0',
                                                                 'skill': 'target_creep',
                                                                 'over': 'target_hero',
                                                                 'n': 287,
                                                                 'chosen_count': 171,
                                                                 'confidence': 0.5951557093425606,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.14405176704828274,
                                                                               'n': 287},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_4d3260d2-64fe-4bd4-9d37-1dc9105778bf.h105.t1379',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]},
                       'GotaField20260919_P_O16': {'claim': 'WHEN nearby=our hero + our creep + our '
                                                            'exposed structure; visible HP ≤100 THEY '
                                                            'PREFER target_creep OVER target_hero FOR '
                                                            'creep_contact (hypothesis).',
                                                   'status': 'requires_review',
                                                   'evidence': [{'id': 'GotaField20260919_P_O16',
                                                                 'when': 'mask_7_low_1',
                                                                 'skill': 'target_creep',
                                                                 'over': 'target_hero',
                                                                 'n': 34,
                                                                 'chosen_count': 13,
                                                                 'confidence': 0.3888888888888889,
                                                                 'confidence_meaning': 'Laplace-smoothed '
                                                                                       'descriptive '
                                                                                       'frequency; '
                                                                                       'population '
                                                                                       'generalization '
                                                                                       'untested',
                                                                 'base_rate': {'source': 'Uniform over '
                                                                                         'available skills '
                                                                                         'in '
                                                                                         'paired-affordance '
                                                                                         'observations; '
                                                                                         'population '
                                                                                         'holdout absent',
                                                                               'rate': 0.14635854341736695,
                                                                               'n': 34},
                                                                 'status': 'provisional',
                                                                 'level': 'population',
                                                                 'opponent': 'sampled_field_20260919',
                                                                 'last_observed': 'ereq_ed937886-1075-4c52-a876-1ec765195df3.h108.t11293',
                                                                 'predictions': {'n': 0,
                                                                                 'correct': 0,
                                                                                 'accuracy': None,
                                                                                 'population_accuracy': None},
                                                                 'counterstrategy_status': 'prior_only'}]}}},
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
 'strategy': [{'id': 'GotaField20260919_P_O01',
               'when': 'mask_0_low_0',
               'skill': 'advance',
               'for': ['territory_pressure']},
              {'id': 'GotaField20260919_P_O03',
               'when': 'mask_1_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'GotaField20260919_P_O04',
               'when': 'mask_1_low_1',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'GotaField20260919_P_O05',
               'when': 'mask_2_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O06',
               'when': 'mask_2_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O07',
               'when': 'mask_3_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O08',
               'when': 'mask_3_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O09',
               'when': 'mask_4_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'GotaField20260919_P_O11',
               'when': 'mask_5_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'GotaField20260919_P_O12',
               'when': 'mask_5_low_1',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'GotaField20260919_P_O13',
               'when': 'mask_6_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O14',
               'when': 'mask_6_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O15',
               'when': 'mask_7_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'GotaField20260919_P_O16',
               'when': 'mask_7_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']}],
 'execution': {'binding': 'gota-observer-model/1', 'game_version': '2026.9.16.5', 'language': 'Python'},
 'update': {'revision': 1,
            'parent': None,
            'change': {'origin': 'observable_replay_inference',
                       'level': 'population',
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
                          'model_level': 'population'}]}}
