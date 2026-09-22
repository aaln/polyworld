POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_portal_coaching20260922',
 'situation': {'grounded': {'observation': 'Bassy Q16.16 decimals for fractional action coordinates, integer '
                                           'snapshot tiles and IDs; six inventory slots; shared public hero '
                                           'draft.',
                            'structure_alive': 'For structures objectAlive means exposed; positive HP means '
                                               'standing.',
                            'predicates': {'always': 'Unconditional lifecycle phase',
                                           'low_health_in_field': 'Below 30% health outside the friendly '
                                                                  'keep/spawn, alive and not '
                                                                  'channeling/stunned. Recovery takes '
                                                                  'priority over farming and attack '
                                                                  'reacquisition.',
                                           'low_health_in_base': 'Critical health inside own keep/spawn '
                                                                 'commits to walking and replenishment '
                                                                 'without a home portal.',
                                           'active': 'Alive, battle started, decision due, not channeling or '
                                                     'stunned',
                                           'in_base': 'Host canShop identifies own keep or spawn; home '
                                                      'recalls are disallowed here while useful outbound '
                                                      'channels remain legal.',
                                           'town_scroll_ready': 'Committed field recovery with an actual '
                                                                'ready scroll; safe channel checks must '
                                                                'still pass.',
                                           'recovery_remaining': 'Recovery owns the decision and no '
                                                                 'successful channel/replenishment action '
                                                                 'has claimed it.'}},
               'notes': 'Coached home recall differs from outbound tower travel. in_base=canShop, '
                        'fountain=inOwnSpawn. Public hero/creep separation and warnings gate a field '
                        'channel. Global geometry and Crossbow draft are retained; current engine rejects '
                        'ordinary commands during channels. Actual stun/root, anchor loss or death '
                        'interrupts; a bot cannot cancel a channel by walking.'},
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
                                    'portalBusy',
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
            'claims': {'PortalPattern': {'claim': 'All16 preselected baseline diagnostic games contain a '
                                                  'home-directed portal starting inside the keep; useful '
                                                  'outward portals also occur. The supplied episode confirms '
                                                  'it for both owned slots, but contains a failed rival VM '
                                                  'and is mechanism evidence only.',
                                         'status': 'supported',
                                         'evidence': [{'artifact': 'evidence/diagnosis-result.json'}]},
                       'CoachingFidelity': {'claim': 'Coordinated priorities, live scroll '
                                                     'readiness/reserves, field safety and in-base walking '
                                                     'realize the coaching on both colors.',
                                            'status': 'untested',
                                            'evidence': []},
                       'CompetitiveGain': {'claim': 'The combined portal controller improves current league '
                                                    'XP score without a color regression. Native practice '
                                                    'alone cannot establish this.',
                                           'status': 'untested',
                                           'evidence': []}}},
 'goal': {'Win': {'preference': 'Objective pressure supports XP production; fort outcomes are diagnostic, '
                                'while current league XP score is primary.',
                  'provenance': 'authored'},
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
                       'provenance': 'authored'},
          'survive_and_replenish': {'preference': 'At critical field health, disengage and channel safely '
                                                  'home before more farming; restore HP/mana at spawn and '
                                                  'return productively with a reserved scroll.',
                                    'provenance': 'interpretation'}},
 'skill': {'portal_state': {'operator': 'portal_portal_state', 'parameters': {}},
           'draft': {'operator': 'portal_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'portal_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'portal_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'portal_timing', 'parameters': {}},
           'lifecycle': {'operator': 'portal_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'portal_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'portal_economy', 'parameters': {'shop_gold': 500}},
           'portal_context': {'operator': 'portal_portal_context', 'parameters': {}},
           'replenish': {'operator': 'portal_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'portal_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'portal_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'portal_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'portal_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'portal_xp_close', 'parameters': {}},
           'combat': {'operator': 'portal_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'portal_advance', 'parameters': {}}},
 'strategy': [{'id': 'R_portal_state',
               'when': 'always',
               'skill': 'portal_state',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_draft',
               'when': 'always',
               'skill': 'draft',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_recovery_intent',
               'when': 'low_health_in_field',
               'skill': 'recovery_intent',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_base_recovery_intent',
               'when': 'low_health_in_base',
               'skill': 'base_recovery_intent',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_timing',
               'when': 'always',
               'skill': 'timing',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_lifecycle',
               'when': 'always',
               'skill': 'lifecycle',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_observe',
               'when': 'active',
               'skill': 'observe',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_economy',
               'when': 'active',
               'skill': 'economy',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_portal_context',
               'when': 'active',
               'skill': 'portal_context',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_replenish',
               'when': 'in_base',
               'skill': 'replenish',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_channel_town_scroll',
               'when': 'town_scroll_ready',
               'skill': 'channel_town_scroll',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_walk_to_base',
               'when': 'recovery_remaining',
               'skill': 'walk_to_base',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_home_portal',
               'when': 'active',
               'skill': 'home_portal',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_tower_safety',
               'when': 'active',
               'skill': 'tower_safety',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_xp_close',
               'when': 'active',
               'skill': 'xp_close',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_combat',
               'when': 'active',
               'skill': 'combat',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']},
              {'id': 'R_advance',
               'when': 'active',
               'skill': 'advance',
               'for': ['Grow', 'Survive', 'Score', 'Practice', 'survive_and_replenish']}],
 'execution': {'binding': 'gota-bassy/portals-2026-09-22-r2',
               'game_version': '2026.9.22.2',
               'language': 'BASIC'},
 'update': {'revision': 1,
            'parent': 'd811adf6984493daa316ddf203e259b9ec51d50048b23bf502949ab2620213e4',
            'change': {'origin': 'Session2026-09-22t16-43-56-076z862811; coordinated field recall and scroll '
                                 'economy',
                       'episode': 'ereq_2d958e27-210e-461d-b6af-b2e26dfa3a81'},
            'needs_review': ['belief/CoachingFidelity', 'belief/CompetitiveGain'],
            'evidence': [{'artifact': 'evidence/coaching/notes.md'},
                         {'artifact': 'evidence/coaching/synthesis.json'}]}}
