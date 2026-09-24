POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_weak_neutral20260924',
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
               'notes': 'Current authority is game 2026.9.23.4, engine '
                        '2c8db6ebe1dc785ce1eea87496505d1244ee4c44. Drafting, skill spending, decimal '
                        'actions, own-keep shopping, portals, explicit casts, crowd control and neutral '
                        'camps are current mechanics. Only public observations are controller inputs. Unseen '
                        'camp occupancy and respawn remain unknown. Neutral XP requires eligible living '
                        'recipients within six tiles on the same navigation layer; kills alone do not '
                        'establish XP income. The exact executable is unchanged from the frozen experiment. '
                        'Historical prose is preserved in evidence/frozen-input.ir.json. Frozen bindings '
                        'reproduce inherited behavior; their history is not evidence of present score '
                        'efficacy. The neutral rule excludes Ranger and Crossbowman; weak-hero class is a '
                        'policy grouping, not a claim that every such hero is intrinsically weak.'},
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
            'claims': {'WeakNeutralMechanism': {'status': 'supported',
                                                'claim': 'The 160 constructed host fixtures passed. In '
                                                         'controlled level-4 tier-1 encounters on both '
                                                         'sides, all ten hero classes secured at least one '
                                                         'neutral kill. This establishes bounded mechanical '
                                                         'capability, not league score improvement or '
                                                         'successful camp routing.',
                                                'evidence': [{'artifact': 'evidence/practice-comparison.json'},
                                                             {'artifact': 'evidence/camp-income.json'}]},
                       'WeakHeroScore': {'status': 'requires_review',
                                         'claim': 'The 60 matched current-release games gave mean score '
                                                  'delta -129.45, with adjusted 97.5% paired interval '
                                                  '[-318.25, 41.65]. Neutral targeting has not been '
                                                  'independently confirmed as a score repair. Use actual '
                                                  'class-specific neutral XP receipts and scores; do not '
                                                  'infer benefit from kills alone.',
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
 'skill': {'portal_state': {'operator': 'weakneutral_portal_state', 'parameters': {}},
           'draft': {'operator': 'weakneutral_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'weakneutral_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'weakneutral_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'weakneutral_timing', 'parameters': {}},
           'lifecycle': {'operator': 'weakneutral_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'weakneutral_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'weakneutral_economy', 'parameters': {'shop_gold': 500}},
           'control_hero': {'operator': 'weakneutral_control_hero', 'parameters': {}},
           'portal_context': {'operator': 'weakneutral_portal_context', 'parameters': {}},
           'choose_lane': {'operator': 'weakneutral_choose_lane', 'parameters': {}},
           'lane_recovery': {'operator': 'weakneutral_lane_recovery', 'parameters': {}},
           'replenish': {'operator': 'weakneutral_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'weakneutral_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'weakneutral_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'weakneutral_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'weakneutral_tower_safety', 'parameters': {'tower_hp': 65}},
           'neutral_farm': {'operator': 'weakneutral_neutral_farm', 'parameters': {}},
           'xp_close': {'operator': 'weakneutral_xp_close', 'parameters': {}},
           'combat': {'operator': 'weakneutral_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'weakneutral_advance', 'parameters': {}}},
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
              {'id': 'R_neutral_farm', 'when': 'active', 'skill': 'neutral_farm', 'for': ['Score']},
              {'id': 'R_xp_close', 'when': 'active', 'skill': 'xp_close', 'for': ['Score']},
              {'id': 'R_combat', 'when': 'active', 'skill': 'combat', 'for': ['Score']},
              {'id': 'R_advance', 'when': 'active', 'skill': 'advance', 'for': ['Score']}],
 'execution': {'binding': 'gota-bassy/weak-neutral-income-2026-09-24-r1',
               'game_version': '2026.9.23.4',
               'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': 'a5aa41cb72fc7e90bc2ea507981b3b0594a3be23690113de3aae336569236aba',
            'change': {'origin': 'Current-engine reset and completed matched comparison',
                       'executable_changed': False,
                       'deployment_qualified': False},
            'needs_review': ['belief/WeakHeroScore'],
            'evidence': [{'artifact': 'evidence/request.json'},
                         {'artifact': 'evidence/frozen-input.ir.json'},
                         {'artifact': 'evidence/statistics.json'},
                         {'artifact': 'evidence/practice-comparison.json'},
                         {'artifact': 'evidence/native-comparison.json'},
                         {'artifact': 'evidence/camp-income.json'}]}}
