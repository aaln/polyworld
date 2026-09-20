"""Revalidate saved own structure independently of current enemy visibility."""
from dataclasses import replace


def live_anchor(parent):
    source = parent.template
    reset = '  defUntil = 0\nend if'
    assert source.count(reset) == 1
    source = source.replace(reset,'  defUntil = 0\n  liveAnchorId = 0\nend if',1)
    source = source.replace('defFront = 0\n','liveAnchorSeen = 0\ndefFront = 0\n',1)
    scan = 'while defI < objectCount() and defI < 64\n'
    assert source.count(scan) == 3
    source = source.replace(scan,scan+'''  if liveAnchorId <> 0 then
    if objectId(defI) = liveAnchorId and objectTeam(defI) = selfTeam and objectHp(defI) > 0 then
      liveAnchorSeen = 1
    end if
  end if
''',1)
    source = source.replace('if defFront <> 0 then\n','''liveAnchorRetired = 0
if liveAnchorId <> 0 and liveAnchorSeen = 0 then
  defUntil = 0
  liveAnchorId = 0
  liveAnchorRetired = 1
end if
if defFront <> 0 then
''',1)
    refresh = '    defUntil = worldTick + defHoldTicks'
    assert source.count(refresh) == 1
    source = source.replace(refresh,'    liveAnchorId = defAnchor\n'+refresh,1)
    return replace(parent,template=source,memory=parent.memory+('liveAnchorId',),
        meaning=parent.meaning+' Revalidate the saved friendly anchor ID on every decision, '
        'including decisions without visible enemy heroes and the first decision after respawn. '
        'On this pinned release all standing friendly structures appear before creeps in the '
        'first64 objects. An absent or nonpositive-HP saved own anchor cancels its duty before '
        'fresh-group detection. A fresh group may select a different standing anchor in the '
        'same decision. Enemy disappearance alone never cancels duty. No quiet timer or '
        'standing-anchor behavior changes. Do not use objectAlive for protected structures.')


def reachable_core(parent,rolling_core):
    result=rolling_core(parent)
    return replace(result,parameters=result.parameters|{'creep_response':(40,16,64)},
        meaning=result.meaning+' This version permits response from40tiles, covering the '
        'observed stale inner-tower rally32tiles from the god. The radius is a response '
        'distance, not visibility; only observed living enemy creeps can trigger it.')
