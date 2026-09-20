"""Explicit class-lineup scope for ordered equipment, with a baseline fallback."""


def selective(contract, ordered, baseline):
    indent = lambda source: '\n'.join('  ' + line for line in source.splitlines())
    return contract(
        'if selfTeam = 1 or (param_red_loadout = 1 and selfClass <> 7 and selfClass <> 8) then\n'
        + indent(ordered.template) + '\nelse\n' + indent(baseline.template) + '\nend if',
        ordered.parameters | {'red_loadout': (0, 0, 1)},
        sorted(set(ordered.reads) | set(baseline.reads)),
        sorted(set(ordered.writes) | set(baseline.writes)),
        sorted(set(ordered.actions) | set(baseline.actions)),
        'Blue team (classes Vanguard, Ranger, Arcanist, Druid Warden, Demon Hunter) uses '
        'the explicit ordered equipment progression. If red_loadout=1, red Death Knight, '
        'Crossbowman and Berserker also use it. Other red heroes retain the exact baseline '
        'equipment logic. This is a declared lineup-specific hypothesis, not a guarantee '
        'of superiority. Ordered branch: ' + ordered.meaning + ' Baseline branch: ' + baseline.meaning,
        sorted(set(ordered.memory) | set(baseline.memory)))
