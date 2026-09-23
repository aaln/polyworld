POLICY = {'schema': 'gota-semantic-policy/1',
 'id': 'gota_field_sustain20260923',
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
                                           'recovered_in_field': 'Current safe field health>=75% and '
                                                                 'mana>=20%, no equipment restock; cancel a '
                                                                 'stale health retreat before reaching '
                                                                 'fountain.',
                                           'can_sustain_in_lane': 'A self-heal was accepted within the '
                                                                  'bounded18tick impact window and current '
                                                                  'visible threats/warnings permit a short '
                                                                  'covered sustain step. Learned rank, '
                                                                  'charge, cooldown and mana were checked '
                                                                  'before acceptance; no speculative '
                                                                  'cooldown waiting.',
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
                        'central opening route. No opponent identity or hidden position is an input. '
                        'Coaching session2026-09-23t02-52-57-098ze03810 concerns Druid recovery. '
                        'Source/episode subsequently matched and verified in coaching-episode-binding; '
                        'original capture was unbound; visual facts and unverified Gemini details separated '
                        'in coaching-review. Learned ready affordable self-heal, bounded accepted-cast '
                        'window and current public threat guards ground can_sustain_in_lane. All hero '
                        'classes use live ability observations.'},
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
                                    'spawnY',
                                    'sustainUntil'],
                         'lifetime': 'BASIC globals start at zero per episode and persist across decisions '
                                     'and respawns. The lifecycle binding explicitly resets initialization '
                                     'and retreat state after death.',
                         'uncertainty': 'Unseen enemies are unknown. Visible targets may be masked. Only the '
                                        'draft roster, allied positions and visible opponents inform live '
                                        'choices.'},
            'claims': {'CoachingInterpretation': {'status': 'supported',
                                                  'claim': 'Coaching recording matched league '
                                                           'episode4a6d182f-c2da-4f9d-a9cc-92c4e7cd57b2/requestereq_7ad01f93-5ee5-4eca-ba01-a9b7ee9ea658 '
                                                           'by22358total ticks, roster, slot4redDruid and '
                                                           'HUD sequence. Actual '
                                                           'source67fdcd5d/core-buyback; all replay hashes '
                                                           'match and own VM exits0. Automatic self-heals '
                                                           'reach248/298HP at tick4273 and full298 at4441; '
                                                           'still walks to spawn until about5364 (45.46s '
                                                           'after75%recovery), resumes advance about5382. No '
                                                           'new XP245 from4200through6498. Other '
                                                           'VMs1/2/7fail, so this is mechanistic evidence '
                                                           'only. Candidate is evaluated on separate '
                                                           'all-ten-VM-clean fresh games; cannot claim the '
                                                           'extra healing component alone improves score.',
                                                  'evidence': [{'artifact': 'evidence/coaching-episode-binding.json'},
                                                               {'artifact': 'evidence/coaching-review.json'}]},
                       'RecoveryMechanism': {'status': 'supported',
                                             'claim': 'All68actual-tick sustain/recovery '
                                                      'fixtures,100opening,180buyback,84portal and126broad '
                                                      'checks pass;12complete native games pass. Druid '
                                                      'heals162HP in the controlled scene and leaves '
                                                      'health-only retreat; recovered heroes across ten '
                                                      'classes replace the base path and advance in the same '
                                                      'tick. Threat,resource,restock and active-channel '
                                                      'guards preserved. Initialr1 mistook own healing '
                                                      'warnings for threats and is preserved as a local '
                                                      'failure.',
                                             'evidence': [{'artifact': 'evidence/practice.json'},
                                                          {'artifact': 'evidence/local-summary.json'}]},
                       'CompetitiveGain': {'status': 'contradicted',
                                           'claim': '240fresh games: '
                                                    'aggregate-10.728%,contexts[-8.870330448416041, '
                                                    '-68.52420652332896, '
                                                    '-5.8253837586557555],95%gainCI[-30.32570881245068, '
                                                    "13.16792307235708],Druid exposures{'baseline': 61, "
                                                    "'field-sustain': 70}. Original "
                                                    'score/context/exposure/stability qualification:False. '
                                                    'Blue lead and two ordinal3 mixed-roster contexts; '
                                                    'latter have two fixed reference teammates. No permanent '
                                                    'rank or isolated-component causal claim.',
                                           'evidence': [{'artifact': 'evidence/trial-report.json'}]}}},
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
          'survive_and_replenish': {'preference': 'Maximize productive map uptime: use an accepted '
                                                  'affordable self-heal while withdrawing; take a short safe '
                                                  'field sustain step, resume at75%HP/20%mana without a '
                                                  'fountain detour. Preserve urgent threat escape, necessary '
                                                  'shopping and committed portal channels.',
                                    'provenance': 'interpretation'}},
 'skill': {'portal_state': {'operator': 'sustain_portal_state', 'parameters': {}},
           'draft': {'operator': 'sustain_draft', 'parameters': {'think_ticks': 6}},
           'recovery_intent': {'operator': 'sustain_recovery_intent', 'parameters': {}},
           'base_recovery_intent': {'operator': 'sustain_base_recovery_intent', 'parameters': {}},
           'recovery_refresh': {'operator': 'sustain_recovery_refresh', 'parameters': {}},
           'timing': {'operator': 'sustain_timing', 'parameters': {}},
           'lifecycle': {'operator': 'sustain_lifecycle',
                         'parameters': {'buyback_seconds': 25, 'buyback_reserve': 200}},
           'observe': {'operator': 'sustain_observe', 'parameters': {'scan_limit': 96}},
           'economy': {'operator': 'sustain_economy', 'parameters': {'shop_gold': 500}},
           'portal_context': {'operator': 'sustain_portal_context', 'parameters': {}},
           'field_appraisal': {'operator': 'sustain_field_appraisal', 'parameters': {}},
           'retreat_release': {'operator': 'sustain_retreat_release', 'parameters': {}},
           'field_sustain_and_push': {'operator': 'sustain_field_sustain_and_push', 'parameters': {}},
           'replenish': {'operator': 'sustain_replenish', 'parameters': {}},
           'channel_town_scroll': {'operator': 'sustain_channel_town_scroll', 'parameters': {}},
           'walk_to_base': {'operator': 'sustain_walk_to_base', 'parameters': {}},
           'home_portal': {'operator': 'sustain_home_portal', 'parameters': {}},
           'tower_safety': {'operator': 'sustain_tower_safety', 'parameters': {'tower_hp': 65}},
           'xp_close': {'operator': 'sustain_xp_close', 'parameters': {}},
           'combat': {'operator': 'sustain_combat', 'parameters': {'reset_recovery': 1}},
           'advance': {'operator': 'sustain_advance', 'parameters': {}}},
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
              {'id': 'R_recovery_refresh',
               'when': 'always',
               'skill': 'recovery_refresh',
               'for': ['Score', 'survive_and_replenish']},
              {'id': 'R_timing', 'when': 'always', 'skill': 'timing', 'for': ['Score']},
              {'id': 'R_lifecycle', 'when': 'always', 'skill': 'lifecycle', 'for': ['Score']},
              {'id': 'R_observe', 'when': 'active', 'skill': 'observe', 'for': ['Score']},
              {'id': 'R_economy', 'when': 'active', 'skill': 'economy', 'for': ['Score']},
              {'id': 'R_portal_context', 'when': 'active', 'skill': 'portal_context', 'for': ['Score']},
              {'id': 'R_field_appraisal',
               'when': 'active',
               'skill': 'field_appraisal',
               'for': ['Score', 'survive_and_replenish']},
              {'id': 'R_retreat_release',
               'when': 'recovered_in_field',
               'skill': 'retreat_release',
               'for': ['Score', 'survive_and_replenish']},
              {'id': 'R_field_sustain_and_push',
               'when': 'can_sustain_in_lane',
               'skill': 'field_sustain_and_push',
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
 'execution': {'binding': 'gota-bassy/field-sustain-2026-09-23-r2',
               'game_version': '2026.9.22.3',
               'language': 'BASIC'},
 'update': {'revision': 2,
            'parent': '7731f1a43fd9c98187dd585a947d7195760ac463335990de1207480a02529e14',
            'change': {'origin': 'Completed coaching/source/local/hosted evidence reflected into semantic '
                                 'IR; tested executable bytes unchanged.',
                       'deployment_qualified': False},
            'needs_review': [],
            'evidence': [{'artifact': 'evidence/trial-report.json'},
                         {'artifact': 'evidence/session-input-manifest.json'}]}}
