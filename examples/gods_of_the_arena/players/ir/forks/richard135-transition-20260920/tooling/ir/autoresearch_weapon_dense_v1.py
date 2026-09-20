"""Versioned published physical attack-style scope for dense post-hit recovery."""
from dataclasses import replace

def weapon_dense(parent):
    old='    if param_dense_all_classes = 1 or selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then'
    new='    if selfClass = 1 or selfClass = 6 or (param_weapon_melee = 1 and (selfClass = 0 or selfClass = 4 or selfClass = 5)) then'
    assert parent.template.count(old)==1
    parameters=dict(parent.parameters);parameters.pop('dense_all_classes');parameters['weapon_melee']=(0,0,1)
    return replace(parent,template=parent.template.replace(old,new,1),parameters=parameters,
        meaning=parent.meaning+' Superseding class eligibility: only published RangedAttack '
        'classes Ranger1/Crossbow6, optionally also MeleeAttack Vanguard0/DemonHunter4/'
        'DeathKnight5. Berserker9 remains excluded by inherited plain_class. MagicAttack '
        'classes Arcanist2/Druid3/Lich7/Warlock8 retain the exact parent dense attack '
        'fallback, regardless of hit changes. This is an explicit gameplay-class scope, '
        'not an assertion that weapon heroes lack spells or that one class is universally '
        'superior. Sparse recovery, targeting, movement geometry, gear and alarms unchanged.')
