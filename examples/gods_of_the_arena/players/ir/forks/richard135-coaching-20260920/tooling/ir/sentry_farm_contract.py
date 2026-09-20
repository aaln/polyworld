"""Use quiet guard duty to clear a bounded, visible nearby creep wave."""
from dataclasses import replace


def farm_observer(parent):
    start='''farmId = 0
farmScore = 2147483647
farmEnabled = 0
if defSentry and coreRespond and (defFront = 0 or defFrontD > param_farm_safe * param_farm_safe) then
  farmEnabled = 1
end if
'''
    scan='''if farmEnabled and defKind = 3 and defI < param_farm_scan then
  if coreD <= param_farm_home * param_farm_home and defD <= param_farm_reach * param_farm_reach then
    farmValue = coreD * 10 + objectHp(defI)
    if farmValue < farmScore then
      farmScore = farmValue
      farmId = objectId(defI)
    end if
  end if
end if
'''
    token='      defD = defDx * defDx + defDy * defDy\n      defGx = objectX(defI) - defThreatX'
    assert parent.template.count(token)==1
    source=parent.template.replace('if defActive then\n',start+'if defActive then\n',1)
    source=source.replace(token,'      defD = defDx * defDx + defDy * defDy\n'+
                          '\n'.join('      '+line for line in scan.splitlines())+
                          '\n      defGx = objectX(defI) - defThreatX',1)
    source+='''
if defActive and coreId = 0 and bestId = 0 and farmId <> 0 then
  bestId = farmId
  bestDistance = farmScore
end if
'''
    return replace(parent,template=source,parameters=parent.parameters | {
        'farm_home':(32,16,40),'farm_safe':(40,24,64),'farm_reach':(32,16,40),'farm_scan':(64,48,80)},
        meaning=parent.meaning+' During an already active defense, a sentry within the core '
        'response radius may target a visible living enemy creep within farm_home of home and '
        'farm_reach of itself, only when no visible enemy hero lies within farm_safe of home. '
        'Reuse core/self distances from the existing scan; consider only the first farm_scan '
        'objects to preserve runtime capacity. Prefer creeps nearer home, then lowerHP. '
        'This fallback never overrides a core threat or an ordinary combat target and does '
        'not release defensive duty or infer unseen enemies are absent. It aims to earn '
        'last-hit XP/gold during quiet guard duty; it cannot guarantee safety or rewards.')
