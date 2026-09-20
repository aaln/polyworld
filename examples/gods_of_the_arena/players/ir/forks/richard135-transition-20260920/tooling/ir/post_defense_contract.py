"""Separate destination refresh, productive defense and post-defense release."""
from dataclasses import replace
from hero_binding import CLASS_ID


def post_defense(parent):
    source = parent.template
    start = source.index('    defThreatX = defFrontX\n')
    end = source.index('    defenseRefreshes = defenseRefreshes + 1', start)
    rally = source[start:end]
    # Reuse exactly the parent geometry, independently of lease renewal.
    rally = '\n'.join(line[2:] if line.startswith('  ') else line for line in rally.splitlines())
    marker = 'if worldTick < defUntil then\n'
    assert source.count(marker) == 1
    setup = '''pdVisibleThreat = 0
pdReleased = 0
if worldTick <= pdLastTick then
  pdLastProductive = worldTick
end if
pdLastTick = worldTick
if param_refresh_rally and defSentry = 0 and defFront <> 0 and defAnchor <> 0 and worldTick < defUntil then
RALLY
end if
'''.replace('RALLY', rally)
    source = source.replace(marker, setup + marker, 1)
    marker = 'if (defKind = 2 or defKind = 3) and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then\n'
    assert source.count(marker) == 1
    source = source.replace(marker, marker + '''    if pdVisibleThreat = 0 then
      pdDx = objectX(defI) - defHomeX
      pdDy = objectY(defI) - defHomeY
      pdRadius = param_creep_home_tiles
      if defKind = 2 then
        pdRadius = param_hero_home_tiles
      end if
      if pdDx * pdDx + pdDy * pdDy <= pdRadius * pdRadius then
        pdVisibleThreat = 1
      end if
    end if
''', 1)
    source += f'''
if defActive = 0 or bestId <> 0 or pdVisibleThreat then
  pdLastProductive = worldTick
end if
pdQuietTicks = param_quiet_ticks
if selfClass = {CLASS_ID['DeathKnight']} then
  pdQuietTicks = param_tank_quiet_ticks
end if
if param_release_enabled and defActive and bestId = 0 and pdVisibleThreat = 0 then
  if worldTick - pdLastProductive >= pdQuietTicks then
    defUntil = 0
    defActive = 0
    pdReleased = 1
  end if
end if
'''
    return replace(parent, template=source, parameters=parent.parameters | {
        'refresh_rally': (1, 0, 1), 'release_enabled': (1, 0, 1),
        'quiet_ticks': (240, 120, 1440), 'tank_quiet_ticks': (1080, 120, 2880),
        'hero_home_tiles': (24, 12, 32), 'creep_home_tiles': (16, 8, 24)},
        memory=tuple(dict.fromkeys(parent.memory + ('pdLastTick', 'pdLastProductive'))),
        meaning=parent.meaning +
        ' Post-defense transition supersedes indefinite no-target sentry waiting. '
        'During an already-active attacker recall, optionally refresh the destination '
        'from the current visible standing anchor without extending its commitment. '
        'Use the existing active mobile-enemy scan to detect living visible enemy '
        'heroes within hero_home_tiles of the friendly god, or creeps within '
        'creep_home_tiles. Actual selected combat targets or those visible base '
        'threats reset the quiet clock. No-target rally walking never resets it. '
        'After quiet_ticks, clear active defense so ordinary lane pressure resumes; '
        'actual red DeathKnight global class5 uses tank_quiet_ticks for rear cover. '
        'A fresh observed group can recall heroes again. No assumption that hidden '
        'enemies are dead, no opponent identity lookup, no change to the blue branch. '
        'Distinct class rally destinations are supplied by the paired navigation '
        'skill; accepted walking and release do not by themselves prove movement '
        'or a win. Validate both on complete games.')


def arrived_post_defense(parent):
    """Quiet means idle after arrival, not travelling to a threatened tower."""
    marker='pdVisibleThreat = 0\n'
    assert parent.template.count(marker)==1
    source=parent.template.replace(marker,marker+'''if defFront <> 0 and defCount >= defGroupSize and defAnchor <> 0 then
  pdVisibleThreat = 1
end if
''',1)
    marker='if defActive = 0 or bestId <> 0 or pdVisibleThreat then\n'
    assert source.count(marker)==1
    source=source.replace(marker,'''pdRallyDx = selfX - defPointX
pdRallyDy = selfY - defPointY
pdAtRally = pdRallyDx * pdRallyDx + pdRallyDy * pdRallyDy <= param_arrival_tiles * param_arrival_tiles
if defActive = 0 or bestId <> 0 or pdVisibleThreat or pdAtRally = 0 then
''',1)
    return replace(parent,template=source,parameters=parent.parameters | {
        'arrival_tiles':(6,4,10),'hero_home_tiles':(24,12,48)},
        meaning=parent.meaning+' Arrival-qualified quiet supersedes the earlier timeout: '
        'count quiet only while physically within arrival_tiles of the common rally. '
        'Travel toward a defensive assignment resets the quiet clock, preventing a '
        'hero crossing from another lane from timing out before reaching the defense. '
        'A currently visible group with a standing threatened friendly anchor also '
        'counts as pressure, even outside the home radius. Stale defCount is ignored '
        'unless defFront is currently nonzero. Larger declared home radius may protect '
        'against approaching survivors. This remains an observed-threat heuristic; '
        'unseen opponents are not assumed dead.')
