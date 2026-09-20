"""Correct the red Warlock's offensive spell eligibility during retreat."""
from dataclasses import replace


def warlock_cadence(parent):
    old='if selfClass <> 3 or mSpell = 3 then'
    assert parent.template.count(old)==1
    source=parent.template.replace(old,'if selfClass <> 3 or selfTeam = 0 or mSpell = 3 then',1)
    return replace(parent,template=source,meaning=parent.meaning+
        ' On pinned release .5, red class3 is Warlock, whose slots1and2 are offensive '
        'MothHex and DreadTotem; it is not the blue Druid(class8). Permit those two '
        'charged/off-cooldown spells during accepted retreat movement, retaining descending '
        'slot priority, live host mana/range checks, and automatic support casting. '
        'Every other class, blue behavior, movement and equipment remain unchanged. '
        'This corrects an inherited class mapping assumption without rewriting old contracts.')
