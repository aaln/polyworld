"""Visible combat opportunities; scoring estimates do not guarantee a last hit."""


def opportunity_contract(contract):
    return contract('''
        bestId = 0
        bestDistance = 2147483647
        oBestScore = 2147483647
        oNearest = 0
        oNearestDistance = 2147483647
        oRange = selfAttackRange / 60000
        if oRange < 1 then
          oRange = 1
        end if
        oIndex = 0
        while oIndex < objectCount()
          oId = objectId(oIndex)
          if objectAlive(oIndex) and objectTeam(oIndex) <> selfTeam then
            oDx = objectX(oIndex) - selfX
            oDy = objectY(oIndex) - selfY
            oDistance = oDx * oDx + oDy * oDy
            oHp = objectHp(oIndex)
            oKind = objectKind(oIndex)
            if oDistance < oNearestDistance then
              oNearest = oId
              oNearestDistance = oDistance
            end if
            oScore = oDistance * 100 + oHp * param_hp_weight
            if oKind = 3 and selfLevel < param_farm_until_level and oDistance <= 64 then
              oScore = oScore - 10000
            end if
            oAttackRange = oRange
            if oKind = 1 then
              oAttackRange = 4
            end if
            if oDistance <= oAttackRange * oAttackRange then
              if param_in_range = 1 then
                oScore = oScore - 20000
              end if
              if param_kill_bonus = 1 and oHp <= selfAttackDamage and (oKind = 2 or oKind = 3) then
                oScore = oScore - 100000
                if oKind = 2 then
                  oScore = oScore - 100000
                end if
              end if
              if oKind = 1 then
                oScore = oScore - param_objective_bonus * 2
              end if
              if oKind = 4 then
                oScore = oScore - param_objective_bonus
              end if
            end if
            if oScore < oBestScore then
              oBestScore = oScore
              bestId = oId
              bestDistance = oDistance
            end if
          end if
          oIndex = oIndex + 1
        wend
        if bestId <> 0 and bestId <> oNearest then
          opportunitySelections = opportunitySelections + 1
        end if
    ''', {'hp_weight': (0, 0, 20), 'farm_until_level': (0, 0, 5),
          'in_range': (1, 0, 1), 'kill_bonus': (1, 0, 1), 'objective_bonus': (0, 0, 50000)},
        [], ['candidate'], [],
        'Rank visible attackable enemies by squared tile distance*100 plus HP weight. '
        'Optionally prefer creeps within eight tiles before the configured level. '
        'Within approximate current basic range, prioritize in-range targets, then targets whose '
        'observed HP is no greater than own basic damage, with an extra hero-kill bonus. '
        'An optional in-range objective bonus prioritizes exposed forts/towers. Fort range uses four tiles. '
        'Return actual squared distance separately from ranking score. Integer tile range, HP and basic damage '
        'do not guarantee a last hit: mitigation, spell effects, movement and allied damage are unresolved. '
        'Enumeration order breaks ties. No hidden information or predicted enemy actions.',
        ['opportunitySelections'])
