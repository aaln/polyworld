MODEL = {'schema': 'semantic-coaching-hypotheses/1',
 'id': 'crowd_control_release61_20260923',
 'situation': {'game_version': '2026.9.23.3',
               'engine_commit': 'e42c4822f44e04726b09bb4ffe853152c7a18207',
               'replay_version': 61,
               'baseline_source_sha256': '29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36',
               'public_predicates': {'silenced': 'selfSilenceTicks>0; spell channel illegal, other legal '
                                                 'channels remain available',
                                     'rooted': 'selfRootTicks>0; movement and active portal interrupted, '
                                               'reachable attacks/spells/items remain possible',
                                     'stunned': 'selfStunTicks>0; active actions blocked',
                                     'target_held_through_impact': 'Visible target '
                                                                   'max(objectStunTicks,objectRootTicks) '
                                                                   'covers cast delay plus required travel; '
                                                                   'proposal must account for shape/range '
                                                                   'and current target motion',
                                     'target_can_retaliate': 'A rooted target may attack/cast; a silenced '
                                                             'target may still attack/move; do not zero its '
                                                             'threat',
                                     'reachable_income': 'Currently visible legal creep last hit or '
                                                         'plausible hero finish with public reach, current '
                                                         'damage and resource observations; hidden XP is not '
                                                         'available to BASIC'},
               'control_abilities': [{'class': 0,
                                      'slot': 3,
                                      'name': 'BlazingBlade',
                                      'damage': 72,
                                      'effect': 'stun',
                                      'ticks': 24},
                                     {'class': 8,
                                      'slot': 2,
                                      'name': 'DreadTotem',
                                      'damage': 70,
                                      'effect': 'silence',
                                      'ticks': 48},
                                     {'class': 3,
                                      'slot': 3,
                                      'name': 'GolemSeed',
                                      'damage': 68,
                                      'effect': 'root',
                                      'ticks': 48},
                                     {'class': 7,
                                      'slot': 2,
                                      'name': 'BoneMarionette',
                                      'damage': 53,
                                      'effect': 'root',
                                      'ticks': 24}],
               'contract': 'Rank1 damages shown; duration fixed across learned ranks. Hostile impacts affect '
                           'heroes/creeps, not structures. Timer refresh takes later expiry. Frozen '
                           'visible-object frame; no hidden status inference. Every spell is explicit. Score '
                           'and previous balance rollback otherwise unchanged.'},
 'belief': {'contract': {'status': 'source_and_runtime_verified',
                         'evidence': ['checks.json',
                                      'tests/test_gota_controls-run.log',
                                      'tests/test_gota_portals-run.log']},
            'cast_legality': {'status': 'locally_verified',
                              'claim': '104 matched fixtures remove388silenced rejections with other '
                                       'commands and gameplay samples unchanged; tested BASIC303eeddb.',
                              'evidence': ['practice-comparison.json']},
            'score_gain': {'status': 'not_established',
                           'claim': 'Four local responsive paired score deltas0. Reduced command rejection '
                                    'alone does not establish XP income or competitive gain.',
                           'evidence': ['native-comparison.json']},
            'retreat_while_rooted': {'status': 'source_observed_counter_hypothesis_untested',
                                     'claim': 'Existing walk_to_base can set stopped even when selfRootTicks '
                                              'prevents the walk; a defensive attack or useful spell may '
                                              'still be legal. Needs reachable opportunity and death-risk '
                                              'fixtures before changing arbitration.'},
            'stale_evidence': {'status': 'historical_scope_preserved',
                               'claim': 'Earlier auto-cast and damage assumptions cannot qualify current '
                                        'policies. Preserve old sources and null results; previous survival '
                                        'bundle reduced deaths but also income.'}},
 'goal': {'score': 'Maximize floor(max(0,XP-200*elapsed_minutes)), productive frequency, nonzero mean and '
                   'unconditional mean; duration alone is not reward.',
          'control': 'Convert control windows into achievable hero finishes, escape survival and lane time '
                     'while preserving creep income.'},
 'skill': {'SilenceAwareChannels': {'status': 'implemented_locally_verified_not_deployed',
                                    'binding': 'gota-bassy/control-legality-2026-09-23-r61',
                                    'operation': 'Guard combat and Druid recovery cast calls only; allow '
                                                 'normal independent attacks/items/movement; resume after '
                                                 'silence expires.'},
           'RootedDefensiveIncome': {'status': 'proposed',
                                     'initiation': 'Rooted, retreat owns movement, legal reachable hostile '
                                                   'or useful ready self-heal; not stunned/silenced for '
                                                   'spells.',
                                     'operation': 'Use immediate productive or protective action while '
                                                  'immobilized; reassess at expiry without cancelling urgent '
                                                  'escape. Do not chase or cast merely because rooted.'},
           'TimeControlForImpact': {'status': 'proposed',
                                    'initiation': 'Visible worthwhile hero target, legal shape/range, '
                                                  'learned affordable ability, public control clock.',
                                    'operation': 'Lead moving targets appropriately; stop motion prediction '
                                                 'only if immobilization covers impact. Chain near expiry '
                                                 'unless immediate damage/disable is needed. Distinguish '
                                                 'silence from immobilization.'},
           'ControlResourceBudget': {'status': 'proposed',
                                     'initiation': 'Threat or income opportunity under current mana/charges.',
                                     'operation': 'Value likely hero kill or avoided death against creep '
                                                  'last hits and lane time. Reserve response resources when '
                                                  'threatened; permit cost-effective wave casts and avoid '
                                                  'blanket hero-only rules.'}},
 'strategy': [{'id': 'CC61_SILENCE', 'when': 'silenced', 'skill': 'SilenceAwareChannels', 'for': ['score']},
              {'id': 'CC61_ROOT_DEFENSE',
               'when': 'rooted and retreat owns movement and useful legal immediate action exists',
               'skill': 'RootedDefensiveIncome',
               'for': ['score', 'control']},
              {'id': 'CC61_IMPACT_TIMING',
               'when': 'visible hero opportunity and legal affordable control ability',
               'skill': 'TimeControlForImpact',
               'for': ['score', 'control']},
              {'id': 'CC61_RESOURCES',
               'when': 'hero threat competes with creep-income cast',
               'skill': 'ControlResourceBudget',
               'for': ['score']}],
 'execution': {'executable': False,
               'binding': None,
               'deployed': False,
               'implemented_subset': 'Only SilenceAwareChannels is executable in the linked primary policy '
                                     'pair. Remaining tactics are hypotheses, not claimed behavior.',
               'primary_pair': 'examples/gods_of_the_arena/players/ir/forks/control20260923-local/control-legality',
               'arbitration': 'Preserve draft/death/stun and active portal locks; legality is per action '
                              'channel. No live ground-truth XP or hidden enemy identity.'},
 'update': {'revision': 1,
            'origin': 'User creator note and continue request; exact published source/runtime audit.',
            'preserve': ['Original creator note and live manifests',
                         'Initial compiled IR and corrected fixture history',
                         'All prior studies and deployed source'],
            'next_tests': ['Rooted-retreat reachable attack/heal fixtures across sides and low-scoring '
                           'classes, including no useful target, silence, stun and danger negatives',
                           'Impact timing and control chaining with moving/rooted targets; actual damage, '
                           'control duration and kill credit',
                           'Separately frozen current-engine responsive paired score test;<=100variations '
                           'per request through journaled budget adapter'],
            'metrics': ['own final score',
                        'productive frequency score>=500',
                        'nonzero mean and frequency',
                        'hero kills and creep XP/minute',
                        'deaths/minute and lane downtime',
                        'accepted spell effects and control overlap',
                        'VM errors and budget'],
            'falsifier': 'Reject a score-changing bundle that reduces deaths or rejected orders but lowers '
                         'XP-minus-time or productive frequency; local guard cleanup alone has no '
                         'competitive gain.',
            'qualification': 'No hosted games and no league writes. Prior ordinary random-seed studies '
                             'remain historical; new requests require matched responsive counterfactuals.'}}
