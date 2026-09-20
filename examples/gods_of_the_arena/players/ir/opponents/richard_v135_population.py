"""Counted observer-only opponent model in the primary seven-layer Python IR.
No private source; not an executable or validated rollout proxy.
"""

MODEL = {'schema': 'gota-semantic-opponent/1',
 'id': 'richard_v135_population_observer_model',
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
 'belief': {'grounded': {'level': 'population',
                         'opponent_version': 'sampled_field_20260920',
                         'opponent_label': 'Eight earlier field versions',
                         'our_policy': {'directory': '/Users/aaln/experiments/softmax/polyworld/examples/gods_of_the_arena/players/ir/forks/jordan268',
                                        'id': 'gota_jordan268_redrace',
                                        'basic_sha256': 'be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73',
                                        'ir_file_sha256': 'dbb2dbe273e02c047afcf674af4a73117abab278a6af362238879ee77ae2ddb2',
                                        'versions': ['00cd9483-0309-4613-bf61-89f3f4a33d01',
                                                     '4cdbbf36-3d70-4ea3-8aed-c92ee0e024be']},
                         'predictor': {'contexts': {'mask_1_low_0': {'target_hero': 81,
                                                                     'advance': 62,
                                                                     'hold': 111,
                                                                     'withdraw': 29,
                                                                     'lateral': 24},
                                                    'mask_1_low_1': {'withdraw': 20,
                                                                     'hold': 34,
                                                                     'advance': 5,
                                                                     'lateral': 2},
                                                    'mask_2_low_0': {'target_creep': 327,
                                                                     'advance': 2,
                                                                     'hold': 4,
                                                                     'withdraw': 1},
                                                    'mask_2_low_1': {'target_creep': 2, 'withdraw': 1},
                                                    'mask_3_low_0': {'target_creep': 562,
                                                                     'target_hero': 137,
                                                                     'hold': 193,
                                                                     'withdraw': 61,
                                                                     'advance': 26,
                                                                     'lateral': 49},
                                                    'mask_3_low_1': {'target_creep': 15,
                                                                     'target_hero': 5,
                                                                     'hold': 30,
                                                                     'advance': 10,
                                                                     'lateral': 1,
                                                                     'withdraw': 7},
                                                    'mask_4_low_0': {'target_structure': 126,
                                                                     'advance': 26,
                                                                     'hold': 62,
                                                                     'withdraw': 7,
                                                                     'lateral': 1},
                                                    'mask_4_low_1': {'target_structure': 5,
                                                                     'withdraw': 3,
                                                                     'hold': 33,
                                                                     'advance': 1},
                                                    'mask_5_low_0': {'target_structure': 33,
                                                                     'target_hero': 50,
                                                                     'hold': 31,
                                                                     'advance': 3,
                                                                     'withdraw': 2,
                                                                     'lateral': 3},
                                                    'mask_5_low_1': {'target_structure': 1,
                                                                     'target_hero': 2,
                                                                     'hold': 5,
                                                                     'withdraw': 1},
                                                    'mask_6_low_0': {'target_creep': 270,
                                                                     'target_structure': 60,
                                                                     'lateral': 4,
                                                                     'hold': 19,
                                                                     'advance': 12,
                                                                     'withdraw': 6},
                                                    'mask_6_low_1': {'target_creep': 6,
                                                                     'target_structure': 4,
                                                                     'hold': 4},
                                                    'mask_7_low_0': {'target_structure': 15,
                                                                     'target_hero': 28,
                                                                     'target_creep': 29,
                                                                     'hold': 6,
                                                                     'advance': 1,
                                                                     'withdraw': 3,
                                                                     'lateral': 2},
                                                    'mask_7_low_1': {'target_structure': 3,
                                                                     'target_creep': 4,
                                                                     'target_hero': 4,
                                                                     'hold': 3,
                                                                     'withdraw': 2}},
                                       'global': {'target_creep': 1215,
                                                  'target_hero': 307,
                                                  'target_structure': 247,
                                                  'hold': 535,
                                                  'withdraw': 143,
                                                  'advance': 148,
                                                  'lateral': 86},
                                       'smoothing': 'Laplace +1 over estimated available skills; context '
                                                    'backs off globally if n<8'},
                         'skills': {'scope': 'same seven observable motifs; counted rows in '
                                             'population-observations.jsonl.gz'},
                         'validation': {'n': 0, 'population_generalization': 'not independently tested'},
                         'observability': {'episodes': 14,
                                           'ticks': 60331,
                                           'living_opponent_ticks': 276614,
                                           'visible_living_opponent_ticks': 93560,
                                           'fraction': 0.33823306123334324,
                                           'all_scheduled_hero_tick_fraction': 0.31015564137839585,
                                           'observer_dead_fraction': 0.04654323647875885,
                                           'residual_fraction': 0.07752244548952544,
                                           'segments': 3262,
                                           'eligible': 2681,
                                           'exclusions': {'left_censored': 514,
                                                          'selected_skill_not_established_by_prior_affordances': 67}},
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
            'claims': {'Richard135_P_O03': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                     'structure; visible HP >100 THEY PREFER hold OVER '
                                                     'target_hero FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O03',
                                                          'when': 'mask_1_low_0',
                                                          'skill': 'hold',
                                                          'over': 'target_hero',
                                                          'n': 307,
                                                          'chosen_count': 111,
                                                          'confidence': 0.36245954692556637,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 307,
                                                                        'rate': 0.20244299674267102},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h100.t2751',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O04': {'claim': 'WHEN nearby=our hero; no nearby creep/exposed '
                                                     'structure; visible HP ≤100 THEY PREFER hold OVER '
                                                     'withdraw FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O04',
                                                          'when': 'mask_1_low_1',
                                                          'skill': 'hold',
                                                          'over': 'withdraw',
                                                          'n': 60,
                                                          'chosen_count': 33,
                                                          'confidence': 0.5483870967741935,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 60,
                                                                        'rate': 0.20083333333333334},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_566b97ad-41e2-4d53-820b-f7f929266fc3.h106.t6797',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O05': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER hold FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O05',
                                                          'when': 'mask_2_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'hold',
                                                          'n': 334,
                                                          'chosen_count': 327,
                                                          'confidence': 0.9761904761904762,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 334,
                                                                        'rate': 0.20404191616766468},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h102.t2626',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O06': {'claim': 'WHEN nearby=our creep; no nearby hero/exposed '
                                                     'structure; visible HP ≤100 THEY PREFER target_creep '
                                                     'OVER withdraw FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O06',
                                                          'when': 'mask_2_low_1',
                                                          'skill': 'target_creep',
                                                          'over': 'withdraw',
                                                          'n': 3,
                                                          'chosen_count': 2,
                                                          'confidence': 0.6,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 3,
                                                                        'rate': 0.20000000000000004},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h104.t1542',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O07': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER hold FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O07',
                                                          'when': 'mask_3_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'hold',
                                                          'n': 1028,
                                                          'chosen_count': 562,
                                                          'confidence': 0.5466019417475728,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 1028,
                                                                        'rate': 0.16783398184176393},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h100.t3035',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O08': {'claim': 'WHEN nearby=our hero + our creep; no nearby exposed '
                                                     'structure; visible HP ≤100 THEY PREFER hold OVER '
                                                     'target_creep FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O08',
                                                          'when': 'mask_3_low_1',
                                                          'skill': 'hold',
                                                          'over': 'target_creep',
                                                          'n': 68,
                                                          'chosen_count': 30,
                                                          'confidence': 0.44285714285714284,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 68,
                                                                        'rate': 0.16715686274509803},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_566b97ad-41e2-4d53-820b-f7f929266fc3.h106.t5210',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O09': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                     'hero/creep; visible HP >100 THEY PREFER '
                                                     'target_structure OVER hold FOR structure_pressure '
                                                     '(goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O09',
                                                          'when': 'mask_4_low_0',
                                                          'skill': 'target_structure',
                                                          'over': 'hold',
                                                          'n': 222,
                                                          'chosen_count': 126,
                                                          'confidence': 0.5669642857142857,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 222,
                                                                        'rate': 0.20225225225225227},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h102.t3027',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O10': {'claim': 'WHEN nearby=our exposed structure; no nearby '
                                                     'hero/creep; visible HP ≤100 THEY PREFER hold OVER '
                                                     'target_structure FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O10',
                                                          'when': 'mask_4_low_1',
                                                          'skill': 'hold',
                                                          'over': 'target_structure',
                                                          'n': 42,
                                                          'chosen_count': 33,
                                                          'confidence': 0.7727272727272727,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 42,
                                                                        'rate': 0.2},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_79f848e2-41f8-4b95-a8b8-63f91142989b.h104.t2824',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O11': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                     'nearby creep; visible HP >100 THEY PREFER target_hero '
                                                     'OVER target_structure FOR hero_pressure (goal '
                                                     'hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O11',
                                                          'when': 'mask_5_low_0',
                                                          'skill': 'target_hero',
                                                          'over': 'target_structure',
                                                          'n': 122,
                                                          'chosen_count': 50,
                                                          'confidence': 0.4112903225806452,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 122,
                                                                        'rate': 0.16775956284153004},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h103.t2392',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O12': {'claim': 'WHEN nearby=our hero + our exposed structure; no '
                                                     'nearby creep; visible HP ≤100 THEY PREFER hold OVER '
                                                     'target_hero FOR unresolved (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O12',
                                                          'when': 'mask_5_low_1',
                                                          'skill': 'hold',
                                                          'over': 'target_hero',
                                                          'n': 9,
                                                          'chosen_count': 5,
                                                          'confidence': 0.5454545454545454,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 9,
                                                                        'rate': 0.16666666666666666},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_566b97ad-41e2-4d53-820b-f7f929266fc3.h105.t1557',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O13': {'claim': 'WHEN nearby=our creep + our exposed structure; no '
                                                     'nearby hero; visible HP >100 THEY PREFER target_creep '
                                                     'OVER target_structure FOR creep_contact (goal '
                                                     'hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O13',
                                                          'when': 'mask_6_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'target_structure',
                                                          'n': 371,
                                                          'chosen_count': 270,
                                                          'confidence': 0.7265415549597856,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 371,
                                                                        'rate': 0.16927223719676548},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h102.t2990',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O14': {'claim': 'WHEN nearby=our creep + our exposed structure; no '
                                                     'nearby hero; visible HP ≤100 THEY PREFER target_creep '
                                                     'OVER target_structure FOR creep_contact (goal '
                                                     'hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O14',
                                                          'when': 'mask_6_low_1',
                                                          'skill': 'target_creep',
                                                          'over': 'target_structure',
                                                          'n': 14,
                                                          'chosen_count': 6,
                                                          'confidence': 0.4375,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 14,
                                                                        'rate': 0.16666666666666666},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_79f848e2-41f8-4b95-a8b8-63f91142989b.h104.t2900',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O15': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                     'structure; visible HP >100 THEY PREFER target_creep '
                                                     'OVER target_hero FOR creep_contact (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O15',
                                                          'when': 'mask_7_low_0',
                                                          'skill': 'target_creep',
                                                          'over': 'target_hero',
                                                          'n': 84,
                                                          'chosen_count': 29,
                                                          'confidence': 0.3488372093023256,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 84,
                                                                        'rate': 0.14467120181405896},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_566b97ad-41e2-4d53-820b-f7f929266fc3.h108.t5810',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]},
                       'Richard135_P_O16': {'claim': 'WHEN nearby=our hero + our creep + our exposed '
                                                     'structure; visible HP ≤100 THEY PREFER target_hero '
                                                     'OVER target_creep FOR hero_pressure (goal hypothesis).',
                                            'status': 'requires_review',
                                            'evidence': [{'id': 'Richard135_P_O16',
                                                          'when': 'mask_7_low_1',
                                                          'skill': 'target_hero',
                                                          'over': 'target_creep',
                                                          'n': 16,
                                                          'chosen_count': 4,
                                                          'confidence': 0.2777777777777778,
                                                          'confidence_meaning': 'Smoothed observed '
                                                                                'frequency; not intent '
                                                                                'certainty; correlated '
                                                                                'starts.',
                                                          'base_rate': {'source': 'Uniform over paired '
                                                                                  'available motifs; '
                                                                                  'population generalization '
                                                                                  'not independently tested',
                                                                        'n': 16,
                                                                        'rate': 0.14583333333333331},
                                                          'level': 'population',
                                                          'opponent': 'sampled_current_policy_field_20260920',
                                                          'status': 'provisional',
                                                          'last_observed': 'ereq_afa63af7-0c73-4d67-8da4-5b280ec295eb.h103.t2401',
                                                          'predictions': {'n': 0,
                                                                          'correct': 0,
                                                                          'accuracy': None,
                                                                          'population_accuracy': None}}]}}},
 'goal': {'hero_pressure': {'preference': 'Hypothesis: maintain visible hero contact in the counted '
                                          'contexts; no inference of kill intent or global priority.',
                            'provenance': 'interpretation',
                            'supporting_preferences': ['Richard135_P_O11', 'Richard135_P_O16'],
                            'paired_context_starts': 138,
                            'global_ordering_validated': False},
          'creep_contact': {'preference': 'Hypothesis: maintain creep contact. XP, gold and last-hit '
                                          'optimization are not observed.',
                            'provenance': 'interpretation',
                            'supporting_preferences': ['Richard135_P_O05',
                                                       'Richard135_P_O06',
                                                       'Richard135_P_O07',
                                                       'Richard135_P_O13',
                                                       'Richard135_P_O14',
                                                       'Richard135_P_O15'],
                            'paired_context_starts': 1834,
                            'global_ordering_validated': False},
          'structure_pressure': {'preference': 'Hypothesis: pressure exposed structures. Target selection is '
                                               'weaker evidence than realized damage.',
                                 'provenance': 'interpretation',
                                 'supporting_preferences': ['Richard135_P_O09'],
                                 'paired_context_starts': 222,
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
                         'supporting_preferences': ['Richard135_P_O03',
                                                    'Richard135_P_O04',
                                                    'Richard135_P_O08',
                                                    'Richard135_P_O10',
                                                    'Richard135_P_O12'],
                         'paired_context_starts': 486,
                         'global_ordering_validated': False}},
 'skill': {'target_hero': {'operator': 'observed_target_hero', 'parameters': {'minimum_segment_ticks': 6}},
           'target_creep': {'operator': 'observed_target_creep', 'parameters': {'minimum_segment_ticks': 6}},
           'target_structure': {'operator': 'observed_target_structure',
                                'parameters': {'minimum_segment_ticks': 6}},
           'advance': {'operator': 'observed_advance', 'parameters': {'minimum_segment_ticks': 6}},
           'withdraw': {'operator': 'observed_withdraw', 'parameters': {'minimum_segment_ticks': 6}},
           'lateral': {'operator': 'observed_lateral', 'parameters': {'minimum_segment_ticks': 6}},
           'hold': {'operator': 'observed_hold', 'parameters': {'minimum_segment_ticks': 6}}},
 'strategy': [{'id': 'Richard135_P_O03', 'when': 'mask_1_low_0', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_P_O04', 'when': 'mask_1_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_P_O05',
               'when': 'mask_2_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O06',
               'when': 'mask_2_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O07',
               'when': 'mask_3_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O08', 'when': 'mask_3_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_P_O09',
               'when': 'mask_4_low_0',
               'skill': 'target_structure',
               'for': ['structure_pressure']},
              {'id': 'Richard135_P_O10', 'when': 'mask_4_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_P_O11',
               'when': 'mask_5_low_0',
               'skill': 'target_hero',
               'for': ['hero_pressure']},
              {'id': 'Richard135_P_O12', 'when': 'mask_5_low_1', 'skill': 'hold', 'for': ['unresolved']},
              {'id': 'Richard135_P_O13',
               'when': 'mask_6_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O14',
               'when': 'mask_6_low_1',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O15',
               'when': 'mask_7_low_0',
               'skill': 'target_creep',
               'for': ['creep_contact']},
              {'id': 'Richard135_P_O16',
               'when': 'mask_7_low_1',
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
                          'model_level': 'population',
                          'episode_count': 14}]}}
