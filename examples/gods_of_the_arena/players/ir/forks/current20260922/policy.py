"""Current-release semantic policy and evidence; exact tested BASIC retained."""

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
                        'proximity; Crossbowman attack range exceeds it. Draft availability is shared across '
                        'both teams. Prefer an available ranged hero; never assume Ranger remains available '
                        'in a late pick. The supplied old-compat replay does not identify the current '
                        'policy.'},
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
            'claims': {'PracticeMechanics': {'claim': 'Controlled both-color engine drills: Ranger 20 to 39 '
                                                      'basic hits/360 ticks; contested-wave gold 210 to 240 '
                                                      'but XP 300 to 285; Crossbowman boundary XP 0 to 15; '
                                                      'Ranger shop damage 47 to 61 at the same 320 HP with '
                                                      'potion and portal slots; threatened-base portal '
                                                      'channels complete and defense releases, while '
                                                      'safe-base controls do not portal. These establish '
                                                      'bounded mechanisms, not general match strength.',
                                             'status': 'supported',
                                             'evidence': [{'artifact': 'evidence/practice-baseline.json'},
                                                          {'artifact': 'evidence/practice-practiced.json'}]},
                       'HostContract': {'claim': '126 actual-host fixtures pass across all classes/colors, '
                                                 'including dense waves, upgrades, shopping, channels, '
                                                 'buyback and defense release. Four responsive native games '
                                                 'won against the parent with exact replay parity. Hosted VM '
                                                 'and score validity is reported per game.',
                                        'status': 'supported',
                                        'evidence': [{'artifact': 'evidence/practiced-scenarios-r2.json'},
                                                     {'artifact': 'evidence/practiced-local-result.json'},
                                                     {'artifact': 'evidence/practiced/result.json'}]},
                       'TargetScoreImprovement': {'claim': 'Mean per-hero XP score exceeds the lane:v1 '
                                                           'baseline in every pinned target/color cell. '
                                                           'Forts, absolute rival score and correlated '
                                                           'trajectories are separate measurements.',
                                                  'status': 'supported',
                                                  'evidence': [{'artifact': 'evidence/review.json'}]},
                       'CurrentContract': {'claim': 'The current decimal-aware binding and XP-score metric '
                                                    'govern new experiments. Historical integer assumptions, '
                                                    'opponent versions and fort-win qualification gates are '
                                                    'not active constraints.',
                                           'status': 'supported',
                                           'evidence': [{'artifact': 'evidence/current/contract.json'},
                                                        {'artifact': 'evidence/current/guide.md'}]},
                       'DraftOpening': {'claim': 'Real-host public opening fixtures select Ranger at tick13 '
                                                 'after enemy Crossbowman; if enemy takes Ranger, select '
                                                 'Arcanist at tick13. This prevents the observed compat '
                                                 'Vanguard choice when these ranged options are available, '
                                                 'without promising any class from every draft seat.',
                                        'status': 'supported',
                                        'evidence': [{'artifact': 'evidence/current/draft-practice.json'}]},
                       'ObservedCompatFailure': {'claim': 'Supplied replay: Coach compat explicitly chose '
                                                          'Vanguard while Ranger was available, earned209XP '
                                                          'and died5times; relh Ranger earned2685XP with no '
                                                          'deaths. Three Coach teammates had VM failures. '
                                                          'Outcome/draft are verified; internal policy '
                                                          'beliefs and causal class superiority are not '
                                                          'established.',
                                                 'status': 'supported',
                                                 'evidence': [{'artifact': 'evidence/current/user-episode/analysis.json'}]},
                       'MixedScoreImprovement': {'claim': 'Exact practiced source versus live compatibility '
                                                          'policy in two frozen healthy-preflight mixed '
                                                          'rosters,40games per version/color. Current-score '
                                                          'gate passed: True. Results are scoped to these '
                                                          'rosters and first-pick seats.',
                                                 'status': 'supported',
                                                 'evidence': [{'artifact': 'evidence/current/field/plan.json'},
                                                              {'artifact': 'evidence/current/field/result.json'},
                                                              {'artifact': 'evidence/current/field/review.json'}]},
                       'LaterDraftScore': {'claim': 'Unchanged executable tested from third-pick seats on '
                                                    'both colors, 40 games per version/color. Current-score '
                                                    'gate passed: True. This verifies a later draft context, '
                                                    'not every possible hero or roster.',
                                           'status': 'supported',
                                           'evidence': [{'artifact': 'evidence/current/middle-field/plan.json'},
                                                        {'artifact': 'evidence/current/middle-field/result.json'},
                                                        {'artifact': 'evidence/current/middle-field/review.json'}]},
                       'ObservedMixedTargetScores': {'claim': 'Retrospective opposing-player score readout: '
                                                              'own mean exceeds relh161 in all four frozen '
                                                              'mixed lineup/color cells, and '
                                                              'Jordan317/Richard153 in both red cells. '
                                                              'Jordan/Richard are allies in the blue cells '
                                                              'and provide no blue-side counter evidence. '
                                                              'Opponent identity is audit metadata, not an '
                                                              'input to the executable.',
                                                     'status': 'supported',
                                                     'evidence': [{'artifact': 'evidence/current/field-target-scores.json'}]},
                       'RefinementRejection': {'claim': 'Scarce-gold armor reserves and faster observation '
                                                        'improve some practice measures but fail matched '
                                                        'responsive native comparison. Retain the original '
                                                        'practiced BASIC, rather than assuming individual '
                                                        'drill gains improve full matches.',
                                               'status': 'supported',
                                               'evidence': [{'artifact': 'evidence/current/attention-confirm-decision.json'},
                                                            {'artifact': 'evidence/current/reserve-control-result.json'}]},
                       'Generalization': {'claim': 'No universal class-strength, every-draft-position, '
                                                   'current-target-every-color score superiority or '
                                                   'number-one league rank claim. Completed uniform target '
                                                   'panel uses Jordan306; mixed follow-up uses Jordan317. '
                                                   'Jordan356 appeared during the follow-up and is untested. '
                                                   'Further current responsive validation is required.',
                                          'status': 'requires_review',
                                          'evidence': [{'artifact': 'evidence/current/experiment.md'},
                                                       {'artifact': 'evidence/current/target-drift.json'},
                                                       {'artifact': 'evidence/review.json'}]}}},
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
 'update': {'revision': 5,
            'parent': 'e5b0e077b0b6166d2a3e9a416dca513d2ac03201326842208d2b37b769b7fb24',
            'change': {'origin': 'User requested current-game IR isolation and analysis of relh Ranger '
                                 'versus compat Vanguard; preserve strongest executable and reflect audited '
                                 'draft/field evidence',
                       'episode': 'ereq_cd49a7f0-5410-4506-9c2d-c8c275d9c749'},
            'needs_review': ['belief/Generalization'],
            'evidence': [{'artifact': 'evidence/current/experiment.md'}]}}
