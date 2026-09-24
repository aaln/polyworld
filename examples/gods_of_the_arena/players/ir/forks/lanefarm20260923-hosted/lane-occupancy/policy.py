POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_lane_occupancy20260923',
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
                        'the reduced damage thresholds. Release61 adds distinct stun, silence and root '
                        'states. Silence is not a global inactive state; root is not a spell or item '
                        'prohibition. Enemy status timers are visible-only evidence. Current host '
                        'abilityDamage supplies the reduced damage thresholds. Control61tactics uses '
                        'currently visible heroes, appropriate remaining-control timers and exact host cast '
                        'validation. No opponent identity or private XP is used. Public allied positions '
                        'identify estimated lane commitment via positive angular projection from home onto '
                        'the three existing waypoints. Alive allies within12tiles of home are uncommitted. '
                        'Shared-XP eligibility depends on actual six-tile range and navigation layer; '
                        'estimated lane counts do not assert eligibility.'},
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
            'claims': {'LaneIntent': {'status': 'supported',
                                      'claim': '120actual host decision fixtures verify one opening choice, '
                                               'safety/unknown/tie guards, expiry, respawn persistence and '
                                               'blue routing. All80hosted opening sources reconstruct exact '
                                               'commands and state hashes; 20 change lanes. The counts '
                                               'estimate allied commitment, not guaranteed future solo XP.',
                                      'evidence': [{'artifact': 'evidence/practice-comparison.json'},
                                                   {'artifact': 'evidence/source-audit.json'}]},
                       'ScoreGain': {'status': 'supported',
                                     'claim': '80matched responsive hosted comparisons on the full reused '
                                              'control cohort: individual score 2493.625to2771.450; '
                                              'delta+277.825, paired95%interval[113.675, 461.75]. Score-only '
                                              'pilot advancement=True. No independent confirmation or '
                                              'deployment qualification; isolation alone is not an '
                                              'improvement.',
                                     'evidence': [{'artifact': 'evidence/statistics.json'}]}}},
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
          'Score': {'preference': 'Maximize expected individual floor(max(0, XP - 200 * elapsed minutes)). '
                                  'Lane occupancy, survival, team victory and game duration have value only '
                                  'through this score. Compare marginal expected XP against travel/death '
                                  'downtime and time penalty.',
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
 'skill': {'portal_state': {'operator': 'lanefarm_portal_state', 'parameters': {}},
           'draft': {'operator': 'lanefarm_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'lanefarm_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'lanefarm_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'lanefarm_timing', 'parameters': {}},
           'lifecycle': {'operator': 'lanefarm_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'lanefarm_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'lanefarm_economy', 'parameters': {'shop_gold': 500}},
           'control_hero': {'operator': 'lanefarm_control_hero', 'parameters': {}},
           'portal_context': {'operator': 'lanefarm_portal_context', 'parameters': {}},
           'choose_lane': {'operator': 'lanefarm_choose_lane', 'parameters': {}},
           'lane_recovery': {'operator': 'lanefarm_lane_recovery', 'parameters': {}},
           'replenish': {'operator': 'lanefarm_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'lanefarm_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'lanefarm_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'lanefarm_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'lanefarm_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'lanefarm_xp_close', 'parameters': {}},
           'combat': {'operator': 'lanefarm_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'lanefarm_advance', 'parameters': {}}},
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
              {'id': 'R_control_hero', 'when': 'active', 'skill': 'control_hero', 'for': ['Score']},
              {'id': 'R_portal_context', 'when': 'active', 'skill': 'portal_context', 'for': ['Score']},
              {'id': 'R_choose_lane', 'when': 'active', 'skill': 'choose_lane', 'for': ['Score']},
              {'id': 'R_lane_recovery', 'when': 'active_druid', 'skill': 'lane_recovery', 'for': ['Score']},
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
 'execution': {'binding': 'gota-bassy/lane-occupancy-2026-09-23-r61a',
               'game_version': '2026.9.23.3',
               'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': 'b47d9adbcda7a65eb2a8056d7778f17cfbd3a3fedd4fce573dc2daab85416daf',
            'change': {'origin': 'Reviewed user lane-sharing coaching against the full80pair counterfactual '
                                 'cohort. Test source unchanged. Score is the only optimization gate.',
                       'deployment_qualified': False},
            'needs_review': [],
            'evidence': [{'artifact': 'evidence/request.json'},
                         {'artifact': 'evidence/statistics.json'},
                         {'artifact': 'evidence/source-audit.json'},
                         {'artifact': 'evidence/native-comparison.json'},
                         {'artifact': 'evidence/practice-comparison.json'}]}}
