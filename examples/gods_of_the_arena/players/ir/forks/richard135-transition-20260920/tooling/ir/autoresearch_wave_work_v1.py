"""Equivalent wave escort selection with fewer temporary branches."""
from dataclasses import replace
import re


def compact_wave(parent):
    pattern = r'(?m)^( *)choose = 0\n\1if id = escortId then\n\1  choose = 1\n\1  retained = 1\n\1end if\n\1if retained = 0 then\n\1  if distance < chosenDistance or \(distance = chosenDistance and id < chosenId\) then\n\1    choose = 1\n\1  end if\n\1end if\n\1if choose then'
    assert len(re.findall(pattern, parent.template)) == 2
    source = re.sub(pattern, lambda m: m[1] + 'if id = escortId or (retained = 0 and (distance < chosenDistance or (distance = chosenDistance and id < chosenId))) then\n' + m[1] + '  if id = escortId then\n' + m[1] + '    retained = 1\n' + m[1] + '  end if', parent.template)
    return replace(parent, template=source, meaning=parent.meaning +
        ' The wave selection uses a combined predicate instead of a temporary '
        'choose flag. Retained escort, nearest-distance and smallest-ID tie '
        'semantics are identical. This is a policy binding implementation '
        'optimization, not a new claim of strategic superiority or an increased '
        'VM limit. Verify commands and every replay state before any use.')
