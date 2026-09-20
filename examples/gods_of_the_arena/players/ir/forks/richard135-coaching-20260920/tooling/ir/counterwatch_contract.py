"""Separate offensive activity from remembered defensive responsibility."""
from dataclasses import replace


def counterwatch(parent):
    source=parent.template
    source=source.replace('defLastTick = worldTick\n',
        'if worldTick <= cwLastTick then\n  cwPush = 0\nend if\ncwLastTick = worldTick\ndefLastTick = worldTick\n',1)
    token='    vcRelease = 1\n    defUntil = 0'
    assert source.count(token)==1
    source=source.replace(token,'    vcRelease = 1\n    cwPush = 1',1)
    token='if worldTick < defUntil then\n'
    assert source.count(token)==1
    source=source.replace(token,'''if cwPush and defFront <> 0 and defAnchor <> 0 then
  if defFrontTarget = defAnchor or defFrontD <= 576 or defCount >= 3 then
    cwPush = 0
    defUntil = worldTick + defHoldTicks
  end if
end if
if worldTick < defUntil and cwPush = 0 then
''',1)
    return replace(parent,template=source,memory=tuple(dict.fromkeys(parent.memory+('cwPush','cwLastTick'))),
        meaning=parent.meaning+' Replace forgetting defense with a persistent counterattack '
        'mode. An observed local victory enables ordinary wave offense while retaining the '
        'existing defense clock and threat detector. While counterattacking, a visible '
        'enemy near a standing friendly anchor recalls this hero if it targets that anchor, '
        'is within24tiles of our god, or belongs to a group of at least3. Renew the original '
        'role-specific commitment on that observed pressure, including when the old clock '
        'has expired. A new episode clears counterattack memory. This separates monitoring '
        'from passive rally duty. It is not new knowledge of hidden enemies or creep-only '
        'attacks. Missing enemies still do not count as a local victory.')
