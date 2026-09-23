POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_blue_druid_siege20260923',
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
                        'regeneration is assumed. Public exposed tower, allied wave cover and self-targeted '
                        'in-range enemy hero predicates support guarded siege pressure. All other current '
                        'host facts and Druid lane recovery remain.'},
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
            'claims': {'CoachingInterpretation': {'status': 'supported',
                                                  'claim': 'The verified recorded Druid kept walking home '
                                                           'after healing. The previous broader '
                                                           'field-sustain bundle failed its240game score '
                                                           'gate. The all-class lane-recovery study also '
                                                           'failed overall while later-draft means improved; '
                                                           'that is a hypothesis for a new Druid-only '
                                                           'source, not evidence of qualification.',
                                                  'evidence': [{'artifact': 'evidence/coaching-review.json'}]},
                       'RecoveryMechanism': {'status': 'supported',
                                             'claim': 'The inherited Druid recovery component is '
                                                      'byte-for-byte unchanged. Its92 actual-tick recovery '
                                                      'cases pass on this complete new source; the previous '
                                                      'Druid-only hosted result belongs to the parent pair. '
                                                      'The coordinated siege skill is restricted to blue '
                                                      'Druids. Ten unaffected full-match pairs, including '
                                                      'red Druids, retain exact command tapes and terminal '
                                                      'world state; these are tested contexts, not an '
                                                      'exhaustive all-state proof.',
                                             'evidence': [{'artifact': 'evidence/recovery.json'},
                                                          {'artifact': 'evidence/parent-reviewed.ir.json'},
                                                          {'artifact': 'evidence/equivalence.json'}]},
                       'CompetitiveGain': {'status': 'contradicted',
                                           'claim': 'The frozen400-game qualification rule was met: False. '
                                                    'Pooled mean score change -0.077%,95%gain interval '
                                                    '[-17.426862383440934, 21.1011960589901],context changes '
                                                    '[-0.07682245707286706]. Relative score-gap preservation '
                                                    "False,Druid exposure {'baseline': 176, "
                                                    "'blue-druid-siege': 168}. This result applies to one "
                                                    'complete scoped source and a fixed blue later-draft '
                                                    'roster. Rejection is failure to qualify, not proof of '
                                                    'population harm. It establishes neither a universal '
                                                    'ranking nor single-component causality.',
                                           'evidence': [{'artifact': 'evidence/trial-report.json'}]},
                       'RichardSourceTransfer': {'status': 'supported',
                                                 'claim': 'Richard source identity and ordering are verified '
                                                          'over82818commands in4Warlock games. Our broader '
                                                          'retrospective diagnosis finds109 guarded tower '
                                                          'opportunities. Scope and target selection pass80 '
                                                          'actual-host scenes on four classes and both '
                                                          'colors, together with582 inherited checks and24 '
                                                          'complete native matches, including active blue '
                                                          'Druids and10 unaffected command/world-equivalent '
                                                          'pairs. Source identity, runtime and intended '
                                                          'guarded choices are supported; competitive value '
                                                          'of the coordinated transfer remains unvalidated. '
                                                          'Hosted mechanism audit reconstructs all commands '
                                                          'and state hashes in16prospectively selected '
                                                          'games; candidate totals '
                                                          "{'selected_covered_tower': 114, "
                                                          "'submitted_attack_covered_tower': 77, "
                                                          "'selected_siege_attacker': 0, "
                                                          "'submitted_attack_siege_attacker': 0}. Selections "
                                                          'and submitted attacks do not establish landed '
                                                          'damage or causal gain. Competitive qualification '
                                                          'is recorded separately.',
                                                 'evidence': [{'artifact': 'evidence/opponent/richard_v174.source.ir.json'},
                                                              {'artifact': 'evidence/own-diagnosis.json'},
                                                              {'artifact': 'evidence/practice.json'},
                                                              {'artifact': 'evidence/local-summary.json'},
                                                              {'artifact': 'evidence/effects-summary.json'}]}}},
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
          'survive_and_replenish': {'preference': 'Druid only: stay near the current lane while useful '
                                                  'healing can safely recover a health-only retreat. Return '
                                                  'for an affordable missing core item, absent healing or '
                                                  'danger. Resume farming at60%HP/20%mana; hold at '
                                                  'most12seconds.',
                                    'provenance': 'interpretation'}},
 'skill': {'portal_state': {'operator': 'siege_portal_state', 'parameters': {}},
           'draft': {'operator': 'siege_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'siege_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'siege_base_recovery_intent', 'parameters': {}},
           'timing': {'operator': 'siege_timing', 'parameters': {}},
           'lifecycle': {'operator': 'siege_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'siege_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'siege_economy', 'parameters': {'shop_gold': 500}},
           'portal_context': {'operator': 'siege_portal_context', 'parameters': {}},
           'lane_recovery': {'operator': 'siege_lane_recovery', 'parameters': {}},
           'replenish': {'operator': 'siege_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'siege_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'siege_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'siege_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'siege_tower_safety', 'parameters': {'tower_hp': 65}},
           'guarded_siege': {'operator': 'siege_guarded_siege', 'parameters': {}},
           'xp_close': {'operator': 'siege_xp_close', 'parameters': {}},
           'combat': {'operator': 'siege_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'siege_advance', 'parameters': {}}},
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
              {'id': 'R_guarded_siege', 'when': 'active', 'skill': 'guarded_siege', 'for': ['Score']},
              {'id': 'R_xp_close', 'when': 'active', 'skill': 'xp_close', 'for': ['Score']},
              {'id': 'R_combat', 'when': 'active', 'skill': 'combat', 'for': ['Score']},
              {'id': 'R_advance', 'when': 'active', 'skill': 'advance', 'for': ['Score']}],
 'execution': {'binding': 'gota-bassy/blue-druid-siege-2026-09-23-r2',
               'game_version': '2026.9.22.3',
               'language': 'BASIC'},
 'update': {'revision': 3,
            'parent': '66cabc92e1f0894a4c2679063dfed14e87a0a57c1ffd37a7eb26d29939b1db3c',
            'change': {'origin': 'Full hosted result and mechanism evidence reflected into semantic IR; '
                                 'tested BASIC unchanged.',
                       'deployment_qualified': False},
            'needs_review': [],
            'evidence': [{'artifact': 'evidence/trial-report.json'},
                         {'artifact': 'evidence/effects-summary.json'}]}}
