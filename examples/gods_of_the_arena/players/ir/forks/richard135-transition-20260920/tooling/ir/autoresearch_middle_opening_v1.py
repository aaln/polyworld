"""Versioned early public middle-lane coverage; inherited combat takes priority."""
from dataclasses import replace
from binding import CONTRACTS

def register():
    parent=CONTRACTS['lineup_perimeter_route']
    route='''if selfTeam = 0 and selfClass = param_middle_class and worldTick <= param_middle_until and defActive = 0 then
  moId = 0
  moX = 105
  moY = 10
  moI = 0
  while moI < objectCount() and moI < 64
    if objectKind(moI) = 3 then
      moI = 64
    else
      if objectTeam(moI) = selfTeam and objectKind(moI) = 4 and objectHp(moI) > 0 then
        moCandidate = objectId(moI)
        if moCandidate >= 16 and moCandidate <= 18 then
          if moId = 0 or moCandidate < moId then
            moId = moCandidate
            moX = objectX(moI) + 4
            moY = objectY(moI) - 4
          end if
        end if
      end if
      moI = moI + 1
    end if
  wend
  moveAccepted = walkTo(moX, moY)
else
'''
    source=route+'\n'.join('  '+line for line in parent.template.splitlines())+'\nend if'
    new=replace(parent,template=source,parameters=parent.parameters|{'middle_class':(8,5,9),'middle_until':(1800,240,2400)},
        meaning=parent.meaning+' Superseding early red fallback for the configured class: through middle_until, when strategy has no combat candidate, no accepted motion and no active defense, walk four map tiles inward of the first standing friendly middle tower16,17,18. Positive HP, including protected structures, defines standing. If none stands use own core coordinate105,10. This public fixed-map lane assignment uses no rival identity, seed or future state. All other classes, blue decisions, combat, active defense and later fallback retain the parent rules. No claim that this coverage improves wins until reacting tests pass.')
    key='lineup_middle_opening_v1'
    if key in CONTRACTS and CONTRACTS[key]!=new:raise ValueError('Conflicting middle opening binding')
    CONTRACTS[key]=new

register()
