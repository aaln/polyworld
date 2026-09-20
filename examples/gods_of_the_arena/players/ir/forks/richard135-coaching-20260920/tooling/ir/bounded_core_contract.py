"""Versioned bound for the active red mobile-target scan."""
from dataclasses import replace


def bounded_targets(parent):
    token='  while defI < objectCount()\n'
    assert parent.template.count(token)==1
    source=parent.template.replace(token,'  while defI < objectCount() and defI < param_defense_target_scan\n',1)
    return replace(parent,template=source,parameters=parent.parameters | {'defense_target_scan':(96,64,128)},
        meaning=parent.meaning+' Bound the active defensive mobile-target scan to the first '
        'defense_target_scan visible objects. On the pinned source, all structures and ten '
        'heroes occur before creeps, within the first48objects. Thus every visible hero is '
        'considered; later creeps may be omitted. The bound reserves instruction capacity '
        'for target priority, recovery, purchases and navigation in dense late-game waves. '
        'Ordinary inactive offense and the separate blue branch remain unchanged.')
