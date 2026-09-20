"""Explicit, approximate building-edge targeting for the 2026.9.16.2 host."""


def building_contract(contract):
    return contract('''
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectHp(index) > 0 and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            if dx < 0 then
              dx = -dx
            end if
            if dy < 0 then
              dy = -dy
            end if
            buildingInset = 0
            buildingWeight = param_unit_weight
            if objectKind(index) = 4 or objectKind(index) = 5 then
              buildingInset = param_edge_tiles
              buildingWeight = param_building_weight
            end if
            if objectKind(index) = 1 then
              buildingInset = param_fort_tiles
              buildingWeight = param_building_weight
            end if
            dx = dx - buildingInset
            dy = dy - buildingInset
            if dx < 0 then
              dx = 0
            end if
            if dy < 0 then
              dy = 0
            end if
            distance = (dx * dx + dy * dy) * buildingWeight
            if distance < bestDistance then
              bestDistance = distance
              bestId = id
            end if
          end if
          index = index + 1
        wend
    ''', {'edge_tiles': (2, 0, 3), 'fort_tiles': (4, 0, 5),
          'unit_weight': (1, 1, 8), 'building_weight': (1, 1, 8)},
       [], ['candidate'], [],
       'Select visible exposed living enemies by squared distance to an approximate axis-aligned '
       'building edge, times the declared kind weight. Kinds4 and5 are towers and barracks; kind1 '
       'is the fort. Inset distances are a heuristic, not the engine footprint or a reachability '
       'test. Keep engine exposure and attackTarget pathfinding; never walk to a building center. '
       'Lower building weight prioritizes siege but can neglect dangerous units. Enumeration order breaks ties.')
