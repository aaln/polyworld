POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_harvest_value20260923',
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
                                           'active_druid': 'Current public hero class is Druid and its '
                                                           'normal decision is active; all other classes '
                                                           'skip lane recovery entirely.',
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
                        'interrupts; a bot cannot cancel a channel by walking. Respawn grows with deaths, '
                        'not hero level. Public remaining respawn and buybackPrice, gold and own unique core '
                        'items support an earlier post-core buyback rule. No opponent identity or hidden '
                        'information features. Public blue team, team ordinal zero and ranged class define a '
                        'central opening route. No opponent identity or hidden position is an input. Lane '
                        'recovery checks public current healing resources and affordable missing core items. '
                        'A learned charged affordable heal within8seconds, a successfully used potion or '
                        'pending accepted heal supports a bounded12second safe hold. No passive field HP '
                        'regeneration is assumed. Release61 adds distinct stun, silence and root states. '
                        'Silence is not a global inactive state; root is not a spell or item prohibition. '
                        'Enemy status timers are visible-only evidence. Current host abilityDamage supplies '
                        'the reduced damage thresholds. Harvest work proxy is integer basic-hit count plus '
                        'travel tiles beyond reach. Creep reward15 is an upper bound before sharing, not '
                        'marginal last-hit XP. Only public visible current objects are eligible.'},
 'belief': {'grounded': {'memory': ['crossed',
                                    'enemyX',
                                    'enemyY',
                                    'homeX',
                                    'homeY',
                                    'hurtTick',
                                    'initialized',
                                    'lane',
                                    'laneHealUntil',
                                    'laneUntil',
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
            'claims': {'RewardWorkRanking': {'status': 'requires_review',
                                             'claim': 'The integer XP/work target ranking runs correctly but '
                                                      'has no demonstrated score gain: eight matched native '
                                                      'comparisons total19367to19376, red gains and blue '
                                                      'losses. Preserve the fork for refinement, not '
                                                      'deployment.',
                                             'evidence': [{'artifact': 'evidence/native-comparison.json'}]},
                       'ProxyLimitations': {'status': 'supported',
                                            'claim': 'Chebyshev travel ignores obstacles; attacks/work '
                                                     'ignores spell burst, shared XP, competing last hitters '
                                                     'and enemy reactions. Prospective paired score test '
                                                     'required.',
                                            'evidence': [{'artifact': 'README.md'}]}}},
 'goal': {'Win': {'preference': 'No independent victory incentive. Enemy-god destruction supplies500 own XP '
                                'and avoids later elapsed-time cost. Keep the baseline structure targeting '
                                'in this experiment; do not idle merely to lengthen games.',
                  'provenance': 'authored'},
          'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert '
                                 'gold into durable combat strength.',
                   'provenance': 'authored'},
          'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to '
                                    'productive play. Exploit legal defensive actions during root or '
                                    'silence; preserve productive basic attacks and item recovery.',
                      'provenance': 'authored'},
          'Score': {'preference': 'Maximize expected individual floor(max(0,lifetime XP-200*elapsed '
                                  'minutes)), including draft. No team-win, survival, death-count, '
                                  'productive-frequency or nonzero-mean hard constraint. These are '
                                  'diagnostic mechanisms, not separate objectives. Accept more deaths or '
                                  'losses if score improves. Terminal god500 personal XP remains an economic '
                                  'reward.',
                    'provenance': 'authored'},
          'Practice': {'preference': 'Secure feasible last hits and shared XP, buy useful permanent power, '
                                     'and use safe portals for urgent defense or productive recovery.',
                       'provenance': 'authored'},
          'survive_and_replenish': {'preference': 'Druid only: stay near the current lane while useful '
                                                  'healing can safely recover a health-only retreat. Return '
                                                  'for an affordable missing core item, absent healing or '
                                                  'danger. Resume farming at60%HP/20%mana; hold at '
                                                  'most12seconds.',
                                    'provenance': 'interpretation'}},
 'skill': {'portal_state': {'operator': 'harvest61_portal_state', 'parameters': {}},
           'draft': {'operator': 'harvest61_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'harvest61_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'harvest61_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'harvest61_timing', 'parameters': {}},
           'lifecycle': {'operator': 'harvest61_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'harvest61_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'harvest61_economy', 'parameters': {'shop_gold': 500}},
           'portal_context': {'operator': 'harvest61_portal_context', 'parameters': {}},
           'lane_recovery': {'operator': 'harvest61_lane_recovery', 'parameters': {}},
           'replenish': {'operator': 'harvest61_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'harvest61_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'harvest61_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'harvest61_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'harvest61_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'harvest61_xp_close', 'parameters': {}},
           'combat': {'operator': 'harvest61_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'harvest61_advance', 'parameters': {}}},
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
              {'id': 'R_lane_recovery',
               'when': 'active_druid',
               'skill': 'lane_recovery',
               'for': ['Score', 'survive_and_replenish']},
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
 'execution': {'binding': 'gota-bassy/harvest-value-2026-09-23-r61a',
               'game_version': '2026.9.23.3',
               'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': 'a68694a4627682f1a7e1380a0cc011067e66185b8ff3cb149daf695217452bf2',
            'change': {'origin': 'User: stop optimizing game wins; prepare XP harvesting at all costs. Use '
                                 'discrete math and statistical aggregation.',
                       'deployment_qualified': False},
            'needs_review': ['belief/RewardWorkRanking'],
            'evidence': [{'artifact': 'evidence/native-comparison.json'}, {'artifact': 'README.md'}]}}
