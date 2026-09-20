"""Blue nearest-two critical admission with an explicitly bounded extra duty."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_middle_transit_v4

ADMISSION = '''responseEligible = 0
if defAnchor <> 0 and defFrontD <= param_response_radius * param_response_radius and defCount >= param_response_group then
  responseDx = selfX - defAnchorX
  responseDy = selfY - defAnchorY
  responseOwnD = responseDx * responseDx + responseDy * responseDy
  responseRank = 0
  responseIndex = 0
  while responseIndex < objectCount() and responseIndex < 64
    responseKind = objectKind(responseIndex)
    if responseKind = 3 then
      responseIndex = 64
    else
      if responseKind = 2 and objectTeam(responseIndex) = selfTeam and objectAlive(responseIndex) and objectHp(responseIndex) > 0 then
        responseDx = objectX(responseIndex) - defAnchorX
        responseDy = objectY(responseIndex) - defAnchorY
        responseD = responseDx * responseDx + responseDy * responseDy
        if responseD < responseOwnD or (responseD = responseOwnD and objectId(responseIndex) < selfId) then
          responseRank = responseRank + 1
        end if
      end if
    end if
    responseIndex = responseIndex + 1
  wend
  if responseRank < param_response_members then
    responseEligible = 1
  end if
end if'''

def scoped(parent):
    red,blue=parent.template.split('\nelse\n',1)
    token='  defLastTick = worldTick'
    assert blue.count(token)==1
    blue=blue.replace(token,'''  if worldTick <= defLastTick then
    responseUntil = 0
    responseMode = 0
  end if
  if responseMode and worldTick >= responseUntil then
    defUntil = 0
    responseMode = 0
  end if
'''+token)
    token='    if defAnchor <> 0 and ('
    assert blue.count(token)==1
    blue=blue.replace(token,'\n'.join('    '+s for s in ADMISSION.splitlines())+'\n'+token+'responseEligible or ')
    token='      defUntil = worldTick + defHoldTicks'
    assert blue.count(token)==1
    blue=blue.replace(token,token+'''
      if responseEligible then
        responseUntil = worldTick + param_response_hold
        responseMode = 1
      end if
      if responseMode and defUntil > responseUntil then
        defUntil = responseUntil
      end if''')
    token='if defDx * defDx + defDy * defDy > param_recall_radius * param_recall_radius then'
    assert blue.count(token)==1
    blue=blue.replace(token,token[:-5]+' and worldTick >= responseUntil then')
    return replace(parent,template=red+'\nelse\n'+blue,
      parameters=parent.parameters|{'response_radius':(60,20,80),'response_group':(2,2,4),'response_members':(2,1,5),'response_hold':(240,120,1200)},
      memory=parent.memory+('responseUntil','responseMode'),
      meaning=parent.meaning+' Blue-only bounded critical response: a visible living enemy '
      'cluster near the friendly god and a standing friendly anchor admits the nearest '
      'response_members living friendly heroes, ranked by squared anchor distance and '
      'public ID ties. Fresh eligibility starts/renews a response_hold deadline that '
      'permits remote recall and caps the inherited long sentry defense deadline. '
      'Expiry clears only this remembered added duty before ordinary alarm processing, '
      'so stale continuation cannot extend it. Ordinary local group defense can start '
      'again; missing observations never assert enemy death. Existing commitments can '
      'briefly overlap newly admitted responders after ranks change; admission, not '
      'simultaneous population, is capped. Red executable statements are unchanged. '
      'No rival identity, hidden state, engine or runtime limit changes.')

name='lineup_scoped_core_response_v1'
value=scoped(CONTRACTS['lineup_deployed_cached_v4'])
if name in CONTRACTS and CONTRACTS[name]!=value:raise ValueError('Conflicting response V1 contract')
CONTRACTS[name]=value
