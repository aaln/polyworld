"""Versioned final equipment-slot reservation, using current public inventory."""
from dataclasses import replace
from textwrap import dedent


def last_slot_axe(parent):
    prefix = dedent('''
        axeGear = 0
        axeOwned = 0
        axeSword = 0
        axeSlot = 0
        while axeSlot < 6
          axeItem = itemId(axeSlot)
          if axeItem > 4 then
            axeGear = axeGear + 1
          end if
          if axeItem = 18 then
            axeOwned = 1
          end if
          if axeItem = 13 then
            axeSword = 1
          end if
          axeSlot = axeSlot + 1
        wend
        if (selfClass = 0 or selfClass = 4 or selfClass = 5 or selfClass = 9) and axeGear = 5 and axeOwned = 0 and axeSword = 0 then
          if selfGold >= 180 then
            buyItem(18)
          end if
        else
    ''').strip()
    template = prefix + '\n' + '\n'.join('  '+line for line in parent.template.splitlines()) + '\nend if'
    return replace(parent, template=template,
        writes=tuple(sorted(set(parent.writes) | {'axeGear','axeOwned','axeSword','axeSlot','axeItem'})),
        meaning=parent.meaning+' Superseding final-slot rule: physical melee classes '
        'Vanguard0, DemonHunter4, DeathKnight5, Berserker9 with exactly five owned '
        'equipment and neither sword13 nor axe18 reserve the remaining slot for '
        'BattleAxe18 at180gold. Earlier sustain still has priority. Otherwise the '
        'entire inherited equipment branch executes unchanged. Only public own '
        'inventory/class/gold; no temporal, seed, opponent or hidden-state gate. '
        'This tests a30gold delay for4more basic damage, not assured superiority.')
