"""Use observed local battle outcomes to end red defensive commitment."""
from dataclasses import replace


def victory_counterpush(parent):
    source=parent.template.replace('defFront = 0\n',
        'vcFriends = 0\nvcDead = 0\nvcEnemies = 0\ndefFront = 0\n',1)
    token='  if objectKind(defI) = 2 then\n'
    assert source.count(token)==1
    source=source.replace(token,token+'''    vcDx = objectX(defI) - selfX
    vcDy = objectY(defI) - selfY
    vcD = vcDx * vcDx + vcDy * vcDy
    if vcD <= 576 then
      if objectTeam(defI) = selfTeam then
        if vcD <= 196 and objectHp(defI) > 0 and objectAlive(defI) then
          vcFriends = vcFriends + 1
        end if
      else
        if objectHp(defI) <= 0 then
          vcDead = vcDead + 1
        else
          if objectAlive(defI) then
            vcEnemies = vcEnemies + 1
          end if
        end if
      end if
    end if
''',1)
    token='if worldTick < defUntil then\n'
    assert source.count(token)==1
    source=source.replace(token,'''vcRelease = 0
if worldTick < defUntil and vcDead >= 2 and vcFriends >= param_victory_allies and vcEnemies = 0 then
  if param_leave_tank = 0 or selfClass <> 0 then
    vcRelease = 1
    defUntil = 0
  end if
end if
'''+token,1)
    return replace(parent,template=source,parameters=parent.parameters|{
        'victory_allies':(4,3,5),'leave_tank':(0,0,1)},meaning=parent.meaning+
        ' Observed local victory transition: in the existing bounded public hero scan count '
        'living allies within14tiles, dead enemy heroes within24tiles, and living enemy '
        'heroes within24tiles. End a current defense commitment only if at least2 actual '
        'visible enemy corpses, victory_allies surviving allies, and no living nearby enemy '
        'hero are observed together. Select the normal wave objective immediately. '
        'leave_tank1 retains DeathKnight as rear guard; others may counterpush. Preserve '
        'original commitment and recall rules whenever this concrete victory condition '
        'is absent. Missing enemies are never counted as dead. Creeps still use ordinary '
        'targeting. This does not guarantee an unseen enemy cannot backdoor.')
