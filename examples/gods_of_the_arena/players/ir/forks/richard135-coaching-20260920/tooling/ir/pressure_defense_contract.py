"""Separate attacker recall retention from the three long-lived sentries."""
from dataclasses import replace


def pressure_observer(parent):
    token = 'defActive = 0\n'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, '''if defSentry = 0 then
  defHoldTicks = param_pressure_hold
  defContinueHome = param_pressure_continue
end if
defActive = 0
''', 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'pressure_hold': (480, 120, 1440), 'pressure_continue': (0, 0, 48)},
        meaning=parent.meaning + ' Non-sentry attackers use pressure_hold for group recall '
        'retention and pressure_continue for survivor refresh. Zero continuation disables '
        'refresh by an isolated survivor except exactly at home; a fresh observed group still '
        'recalls every role. The three sentries retain their original continuation and long '
        'commitment. This prevents a single recurring survivor from indefinitely refreshing '
        'both attackers, while retaining the sentry defense. It does not assert three '
        'defenders are sufficient in every matchup. Purchases and blue behavior are unchanged '
        'when composed as the red branch of lineup_pressure_observe.')
