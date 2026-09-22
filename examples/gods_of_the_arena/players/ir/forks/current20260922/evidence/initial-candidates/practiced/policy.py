"""Semantic policy; compile through the versioned microplay binding."""

POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_targets20260922_practiced',
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
                        'stronger towers require creep cover. Current target identities are evaluation '
                        'metadata, never live policy inputs. Creep XP requires same floor and six-tile '
                        'proximity; Crossbowman attack range exceeds it.'},
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
                                    'restock',
                                    'resumeTarget',
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
                                                       {'artifact': 'evidence/field-review.json'}]},
                       'Microplay': {'claim': 'Practiced timing, XP position, equipment and portal skills '
                                              'improve the current relh/Jordan/Richard matchups.',
                                     'status': 'untested',
                                     'evidence': []}}},
 'goal': {'Win': {'preference': 'Destroy the opposing god while preserving ours.', 'provenance': 'authored'},
          'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert '
                                 'gold into durable combat strength.',
                   'provenance': 'authored'},
          'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to '
                                    'productive play.',
                      'provenance': 'authored'},
          'Score': {'preference': 'Maximize the new live league score max(0, lifetime XP - 200 * elapsed '
                                  'world ticks / 1440); fort outcomes are a separate diagnostic.',
                    'provenance': 'authored'},
          'Practice': {'preference': 'Secure feasible last hits and shared XP, buy useful permanent power, '
                                     'and use safe portals for urgent defense or productive recovery.',
                       'provenance': 'authored'}},
 'skill': {'draft': {'operator': 'micro_draft', 'parameters': {'think_ticks': 6}},
           'timing': {'operator': 'micro_timing', 'parameters': {}},
           'lifecycle': {'operator': 'micro_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'micro_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'micro_economy', 'parameters': {'shop_gold': 500}},
           'home_portal': {'operator': 'micro_home_portal', 'parameters': {}},
           'recover': {'operator': 'micro_recover', 'parameters': {'retreat_hp': 24}},
           'tower_safety': {'operator': 'micro_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'micro_xp_close', 'parameters': {}},
           'combat': {'operator': 'micro_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'micro_advance', 'parameters': {}}},
 'strategy': [{'id': 'R_draft',
               'when': 'always',
               'skill': 'draft',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_timing',
               'when': 'always',
               'skill': 'timing',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_lifecycle',
               'when': 'always',
               'skill': 'lifecycle',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_observe',
               'when': 'active',
               'skill': 'observe',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_economy',
               'when': 'active',
               'skill': 'economy',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_home_portal',
               'when': 'active',
               'skill': 'home_portal',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_recover',
               'when': 'active',
               'skill': 'recover',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_tower_safety',
               'when': 'active',
               'skill': 'tower_safety',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_xp_close',
               'when': 'active',
               'skill': 'xp_close',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_combat',
               'when': 'active',
               'skill': 'combat',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']},
              {'id': 'R_advance',
               'when': 'active',
               'skill': 'advance',
               'for': ['Win', 'Grow', 'Survive', 'Score', 'Practice']}],
 'execution': {'binding': 'gota-bassy/microplay-2026-09-22-r2',
               'game_version': '2026.9.21.5',
               'language': 'BASIC'},
 'update': {'revision': 3,
            'parent': '50cb7d95aa753aa7a56479281e7c6325d8b48df7dc2ec54e10249e325328fdbf',
            'change': {'origin': 'User requested semantic IR and practice on last hits, XP, gear and '
                                 'defensive portals',
                       'variant': 'potions'},
            'needs_review': ['belief/Microplay'],
            'evidence': [{'artifact': 'games/gods_of_the_arena/experiments/2026-09-21-targets-microplay.md'}]}}
