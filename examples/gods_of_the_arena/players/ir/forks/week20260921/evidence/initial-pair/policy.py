"""New-week semantic policy; generated BASIC is derived from these skills."""

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
                                     'and respawns. join_wave revalidates an escort by observed living ID '
                                     'whenever selected.',
                         'uncertainty': 'Unseen enemies are unknown. Visible targets may be masked. Only the '
                                        'draft roster, allied positions and visible opponents inform live '
                                        'choices.'},
            'claims': {'NewWeekBundle': {'claim': 'Coordinated draft, explicit upgrades, productive lanes, '
                                                  'permanent gear, finite defense and recovery should '
                                                  'improve new-week outcomes. Hypothesis for the bundle, not '
                                                  'component causality.',
                                         'status': 'untested',
                                         'evidence': []}}},
 'goal': {'Win': {'preference': 'Destroy the opposing god while preserving ours.', 'provenance': 'authored'},
          'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert '
                                 'gold into durable combat strength.',
                   'provenance': 'authored'},
          'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to '
                                    'productive play.',
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
 'strategy': [{'id': 'R_draft', 'when': 'always', 'skill': 'draft', 'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_lifecycle',
               'when': 'always',
               'skill': 'lifecycle',
               'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_observe', 'when': 'active', 'skill': 'observe', 'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_economy', 'when': 'active', 'skill': 'economy', 'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_recover', 'when': 'active', 'skill': 'recover', 'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_tower_safety',
               'when': 'active',
               'skill': 'tower_safety',
               'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_combat', 'when': 'active', 'skill': 'combat', 'for': ['Win', 'Grow', 'Survive']},
              {'id': 'R_advance', 'when': 'active', 'skill': 'advance', 'for': ['Win', 'Grow', 'Survive']}],
 'execution': {'binding': 'gota-bassy/2026-09-21', 'game_version': '2026.9.21.5', 'language': 'BASIC'},
 'update': {'revision': 1,
            'parent': 'c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4',
            'change': {'origin': 'User requested new-week policy; clean Bassy binding replaces previous '
                                 'engine assumptions',
                       'upstream': 'f776d5e55d439706a8d49878d17d7ba1f6a1f7ce'},
            'needs_review': ['belief/NewWeekBundle'],
            'evidence': [{'artifact': 'games/gods_of_the_arena/experiments/2026-09-21-week-policy.md'}]}}
