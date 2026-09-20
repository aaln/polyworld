"""Stage hosted comparisons only after the prospective full local qualification."""
import counterpush_hosted as runner
from ally_assist import STUDY

if __name__ == '__main__':
    runner.STUDY = STUDY
    runner.PREFIX = 'aaron-gota-ir-ally-assist'
    runner.CHANGE = ('Coached public allied target assistance within existing defensive mode, no new '
                     'recall or rally; pressure20 parent and unchanged blue branch.')
    runner.RICHARD_RED_FLOOR = 30
    runner.RED_KITE_FLOOR = 24
    runner.DESIGN = ('Paired fixed rosters on both colors versus Richard78: require at least '
        '30/40 red wins (pressure20 parent measured27, G11) and38/40 blue. Then preserve '
        'Jordan/g002/redkite/vanguard/black and mixed200. All full replays/runtime/equipment '
        'inspected. Reused controls are not new games; repeated trajectories are correlated, '
        'so results remain directional fixed-lineup evidence. No automatic champion change.')
    runner.main()
