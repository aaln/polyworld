POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_adaptive_spell_targeting',
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
                        'interrupts; a bot cannot cancel a channel by walking. Independent public spell '
                        'target; optional higher hero basic-target priority; no hidden player identity or '
                        'lifetime-XP input. Own lifetime XP is not exposed by this host BASIC API.'},
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
            'claims': {'OpportunityMechanism': {'claim': 'All44 actual-engine spell fixtures pass: '
                                                         'independent nearby public hero casts produce real '
                                                         'hero damage while basics select a finishing creep; '
                                                         'out-of-range and allied alternatives fall back '
                                                         'legally; useful mana restoration works. '
                                                         'Recovery/channel fixtures remain protected. This '
                                                         'does not establish competitive value.',
                                                'status': 'supported',
                                                'evidence': [{'artifact': 'evidence/practice.json'}]},
                       'PortalPreserved': {'claim': 'All84 inherited portal fixtures and126 broader '
                                                    'all-class host checks pass on the frozen current '
                                                    'engine.',
                                           'status': 'supported',
                                           'evidence': [{'artifact': 'evidence/portals.json'},
                                                        {'artifact': 'evidence/scenarios.json'}]},
                       'CompetitiveGain': {'claim': 'Screen passed: 10.059% aggregate, '
                                                    'colors[8.198026259003166, 11.714278402838808],95% '
                                                    'interval[-7.494543532380737, 31.08764436396203]. No '
                                                    'independent confirmation for this source; no '
                                                    'replacement qualification. Exact-version fixed-roster '
                                                    'scope, no universal rank guarantee or per-component '
                                                    'causal claim.',
                                           'status': 'requires_review',
                                           'evidence': [{'artifact': 'evidence/screen-report.json'}]},
                       'FieldDrift': {'status': 'supported',
                                      'claim': 'Opponent-version and game snapshots are evaluation metadata; '
                                               'newer entries can change optimal behavior. No opponent UUID '
                                               'or hidden replay state enters the live source. A changed '
                                               'field requires a new comparison, preserving pinned results.',
                                      'evidence': [{'artifact': 'evidence/field-changes.json'}]}}},
 'goal': {'Win': {'preference': 'No independent victory incentive. Enemy-god destruction supplies500 own XP '
                                'and avoids later elapsed-time cost. Keep the baseline structure targeting '
                                'in this experiment; do not idle merely to lengthen games.',
                  'provenance': 'authored'},
          'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert '
                                 'gold into durable combat strength.',
                   'provenance': 'authored'},
          'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to '
                                    'productive play.',
                      'provenance': 'authored'},
          'Score': {'preference': 'Sole objective: maximize final individual max(0, lifetime XP*1440 '
                                  '-200*world_ticks)//1440. Hero kill150XP, shared creep pool15XP, '
                                  'building100XP, enemy god destruction500XP for every teammate. Prefer '
                                  'productive kills and farming; elapsed time always costs200/minute. '
                                  'Survival, items and portals matter only through their contribution to '
                                  'this objective.',
                    'provenance': 'authored'},
          'Practice': {'preference': 'Secure feasible last hits and shared XP, buy useful permanent power, '
                                     'and use safe portals for urgent defense or productive recovery.',
                       'provenance': 'authored'},
          'survive_and_replenish': {'preference': 'At critical field health, disengage and channel safely '
                                                  'home before more farming; restore HP/mana at spawn and '
                                                  'return productively with a reserved scroll.',
                                    'provenance': 'interpretation'}},
 'skill': {'portal_state': {'operator': 'adaptive_portal_state', 'parameters': {}},
           'draft': {'operator': 'adaptive_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'adaptive_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'adaptive_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'adaptive_timing', 'parameters': {}},
           'lifecycle': {'operator': 'adaptive_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'adaptive_observe',
                       'parameters': {'scan_limit': 96, 'hero_priority_bonus': 80}},
           'economy': {'operator': 'adaptive_economy', 'parameters': {'shop_gold': 500}},
           'portal_context': {'operator': 'adaptive_portal_context', 'parameters': {}},
           'replenish': {'operator': 'adaptive_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'adaptive_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'adaptive_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'adaptive_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'adaptive_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'adaptive_xp_close', 'parameters': {}},
           'combat': {'operator': 'adaptive_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'adaptive_advance', 'parameters': {}}},
 'strategy': [{'id': 'R_portal_state', 'when': 'always', 'skill': 'portal_state', 'for': ['Score']},
              {'id': 'R_draft', 'when': 'always', 'skill': 'draft', 'for': ['Score']},
              {'id': 'R_recovery_intent',
               'when': 'low_health_in_field',
               'skill': 'recovery_intent',
               'for': ['Score']},
              {'id': 'R_base_recovery_intent',
               'when': 'low_health_in_base',
               'skill': 'base_recovery_intent',
               'for': ['Score']},
              {'id': 'R_timing', 'when': 'always', 'skill': 'timing', 'for': ['Score']},
              {'id': 'R_lifecycle', 'when': 'always', 'skill': 'lifecycle', 'for': ['Score']},
              {'id': 'R_observe', 'when': 'active', 'skill': 'observe', 'for': ['Score']},
              {'id': 'R_economy', 'when': 'active', 'skill': 'economy', 'for': ['Score']},
              {'id': 'R_portal_context', 'when': 'active', 'skill': 'portal_context', 'for': ['Score']},
              {'id': 'R_replenish', 'when': 'in_base', 'skill': 'replenish', 'for': ['Score']},
              {'id': 'R_channel_town_scroll',
               'when': 'town_scroll_ready',
               'skill': 'channel_town_scroll',
               'for': ['Score']},
              {'id': 'R_walk_to_base',
               'when': 'recovery_remaining',
               'skill': 'walk_to_base',
               'for': ['Score']},
              {'id': 'R_home_portal', 'when': 'active', 'skill': 'home_portal', 'for': ['Score']},
              {'id': 'R_tower_safety', 'when': 'active', 'skill': 'tower_safety', 'for': ['Score']},
              {'id': 'R_xp_close', 'when': 'active', 'skill': 'xp_close', 'for': ['Score']},
              {'id': 'R_combat', 'when': 'active', 'skill': 'combat', 'for': ['Score']},
              {'id': 'R_advance', 'when': 'active', 'skill': 'advance', 'for': ['Score']}],
 'execution': {'binding': 'gota-bassy/adaptive-score-2026-09-22-r1',
               'game_version': '2026.9.22.3',
               'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': '47710194b0cd7c1cc0558ec0fa10bfca0e34c0abc9c1fa9c2cba77463f612a28',
            'change': {'origin': 'Current-engine practice and completed hosted outcomes reflected into IR; '
                                 'executable bytes unchanged',
                       'screen_passed': True,
                       'confirmation_passed': False},
            'needs_review': ['belief/CompetitiveGain'],
            'evidence': [{'artifact': 'evidence/screen-report.json'}]}}
