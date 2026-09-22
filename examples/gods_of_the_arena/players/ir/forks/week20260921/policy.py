"""Validated new-week policy with explicitly bounded claims."""

POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_week20260921_lane',
 'situation': {'grounded': {'observation': 'Bassy Q16.16 decimals for fractional action coordinates, integer '
                                           'snapshot tiles and IDs; six inventory slots; shared public hero '
                                           'draft.',
                            'structure_alive': 'For structures objectAlive means exposed; positive HP means '
                                               'standing.',
                            'predicates': {'always': 'Unconditional lifecycle phase',
                                           'active': 'Alive, battle started, decision due, not channeling or '
                                                     'stunned'}},
               'notes': 'Public draft choices and visible enemy objects only. Current tower aggro and nearby '
                        'waves are facts, unseen opponents unknown. Shared XP rewards productive lanes; '
                        'stronger towers require creep cover.'},
 'belief': {'grounded': {'memory': ['crossed',
                                    'enemyX',
                                    'enemyY',
                                    'homeX',
                                    'homeY',
                                    'hurtTick',
                                    'initialized',
                                    'lane',
                                    'moveTick',
                                    'nextThink',
                                    'previousHits',
                                    'previousHp',
                                    'retreat',
                                    'scanOffset',
                                    'spawnX',
                                    'spawnY'],
                         'lifetime': 'BASIC globals start at zero per episode and persist across decisions '
                                     'and respawns. The lifecycle binding explicitly resets initialization '
                                     'and retreat state after death.',
                         'uncertainty': 'Unseen enemies are unknown. Visible targets may be masked. Only the '
                                        'draft roster, allied positions and visible opponents inform live '
                                        'choices.'},
            'claims': {'NewWeekBundle': {'claim': 'Passed the fixed-opponent hosted score gate versus the '
                                                  'exact compatibility incumbent; scope and correlation '
                                                  'limits are recorded in evidence/review.json.',
                                         'status': 'supported',
                                         'evidence': [{'artifact': 'evidence/hosted-result.json'},
                                                      {'artifact': 'evidence/review.json'}]},
                       'HostContract': {'claim': 'All ten classes on both colors pass 126 actual-VM '
                                                 'mechanism/stress checks; complete source parses and '
                                                 'round-trips, and two hosted replays match all state '
                                                 'hashes, XP and the new score formula.',
                                        'status': 'supported',
                                        'evidence': [{'artifact': 'evidence/scenarios-extra.json'},
                                                     {'artifact': 'evidence/build-proof.json'},
                                                     {'artifact': 'evidence/extra-build-proof.json'},
                                                     {'artifact': 'evidence/calibration.json'}]},
                       'MixedTeamScore': {'claim': 'The new bundle improves clean mixed-team mean score over '
                                                   'the compatibility incumbent on each color and by at '
                                                   'least 20% overall. Observed gate: unqualified: '
                                                   'insufficient clean games. Two exact rosters and middle '
                                                   'draft seats cannot establish universal league '
                                                   'superiority.',
                                          'status': 'requires_review',
                                          'evidence': [{'artifact': 'evidence/field-plan.json'},
                                                       {'artifact': 'evidence/field-result.json'},
                                                       {'artifact': 'evidence/field-review.json'}]}}},
 'goal': {'Win': {'preference': 'Destroy the opposing god while preserving ours.', 'provenance': 'authored'},
          'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert '
                                 'gold into durable combat strength.',
                   'provenance': 'authored'},
          'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to '
                                    'productive play.',
                      'provenance': 'authored'},
          'Score': {'preference': 'Maximize the new live league score max(0, lifetime XP - 200 * elapsed '
                                  'world ticks / 1440); fort outcomes are a separate diagnostic.',
                    'provenance': 'authored'}},
 'skill': {'draft': {'operator': 'week_draft', 'parameters': {'think_ticks': 6}},
           'lifecycle': {'operator': 'week_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'week_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'week_economy', 'parameters': {}},
           'recover': {'operator': 'week_recover', 'parameters': {'retreat_hp': 24}},
           'tower_safety': {'operator': 'week_tower_safety', 'parameters': {'tower_hp': 65}},
           'combat': {'operator': 'week_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'week_advance', 'parameters': {}}},
 'strategy': [{'id': 'R_draft',
               'when': 'always',
               'skill': 'draft',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_lifecycle',
               'when': 'always',
               'skill': 'lifecycle',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_observe',
               'when': 'active',
               'skill': 'observe',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_economy',
               'when': 'active',
               'skill': 'economy',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_recover',
               'when': 'active',
               'skill': 'recover',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_tower_safety',
               'when': 'active',
               'skill': 'tower_safety',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_combat',
               'when': 'active',
               'skill': 'combat',
               'for': ['Win', 'Grow', 'Survive', 'Score']},
              {'id': 'R_advance',
               'when': 'active',
               'skill': 'advance',
               'for': ['Win', 'Grow', 'Survive', 'Score']}],
 'execution': {'binding': 'gota-bassy/2026-09-21', 'game_version': '2026.9.21.5', 'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': '693742d706be66b68adcf8a67e31855cf6ffbc5a5c2db28b7a666c6d27f45874',
            'change': {'origin': 'Completed new-week hosted comparison and native validation; executable '
                                 'preserved exactly'},
            'needs_review': ['mixed-team-score-generalization', 'current-leader-comparison'],
            'evidence': [{'artifact': 'evidence/hosted-result.json'},
                         {'artifact': 'evidence/experiment.md'}]}}
