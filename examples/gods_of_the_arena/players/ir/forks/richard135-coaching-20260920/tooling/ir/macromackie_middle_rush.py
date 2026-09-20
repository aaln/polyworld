"""Run the same frozen gate with a separately registered middle-only observer."""
from copy import deepcopy
from pathlib import Path

import macromackie_visible_rush as pipeline
from policy_ir import digest, read, refresh_grounding, write
from hero_binding import class_id
from test_rush_defense import scene
from test_rush_unblock import UnblockTests

STUDY = pipeline.RUN / 'coached-lanes/r5-macromackie-middle-rush'
DESIGN = ('Early middle rush: on blue during first1800ticks, three visible clustered '
          'enemy heroes at standing friendly middle towers19/20/21 initiate recall. '
          'Other locations/times use parent four threshold. No opponent labels. '
          'Fresh local12/arm, actual-class VM/dense/IR checks and redparity before '
          'complete40red40blue versus exactmacromackie-v4. Targeted32blue38red, '
          'source-verified earlyrecall required. No automatic promotion.')


def make(name):
    parent = read(pipeline.PARENT / 'policy.ir.json')
    if name == 'deployed':
        return parent
    if name != 'blue_three':
        raise ValueError(name)
    p = deepcopy(parent)
    p['id'] = 'gota_middle_rush_blue_three'
    skill = p['skill']['observe']
    skill['operator'] = 'lineup_middle_rush'
    skill['parameters'].update(middle_group=3, middle_opening_ticks=1800)
    p['goal']['G_defense']['preference'] += (
        ' During the first75seconds on blue, three visible clustered enemy heroes '
        'near a standing friendly middle-lane tower signal a possible concentrated '
        'rush and initiate existing recall. Side lanes and later play retain the '
        'four-hero trigger. Preserve red execution and existing defensive lifetimes. '
        'Observe strategy from gameplay; opponent identity is unavailable.')
    evidence = pipeline.PREVIOUS / 'color-analysis.json'
    p['belief']['claims']['B_early_middle_rush'] = {'status': 'untested', 'claim': DESIGN,
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())},
                     {'artifact': str(pipeline.RUN/'coached-lanes/r5-macromackie-visible-rush/local/qualification.json'),
                      'sha256': digest((pipeline.RUN/'coached-lanes/r5-macromackie-visible-rush/local/qualification.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Earlier blue recall specifically for observed early middle pressure.')
    refresh_grounding(p)
    return p


def scoped_checks():
    original_checks()
    class VM(UnblockTests):
        factory = staticmethod(make)
    VM.setUpClass()
    vm = VM()
    rows = []
    for slot in range(5):
        for tower in (19, 20, 21, 13, 25):
            for tick in (1800, 1801):
                case = scene(1, count=3, worldTick=tick)
                case['self'].update(selfId=105+slot, selfClass=class_id(1, slot))
                case['objects'][3]['objectId'] = tower
                for i, enemy in enumerate(case['objects'][4:]):
                    enemy.update(objectId=100+i, objectClass=class_id(0, i), objectTarget=tower)
                r = vm.play('blue_three', [case], ('defActive',))[0]
                assert bool(r['memory']['defActive']) == (tower in (19,20,21) and tick <= 1800)
                rows.append(r)
    write(STUDY/'scope-proof.json', {'passed': True, 'decisions': len(rows),
          'scope': 'All5actualblueclasses; middle19/20/21 versusotherlanes13/25; exact1800inclusive boundary.'})


if __name__ == '__main__':
    original_checks = pipeline.native_checks
    pipeline.STUDY = STUDY
    pipeline.DESIGN = DESIGN
    pipeline.SEED = 815100
    pipeline.UPLOAD_PREFIX = 'aaron-gota-ir-middle-rush'
    pipeline.RECORD = Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-17-macromackie-middle-rush.md')
    pipeline.make = make
    pipeline.native_checks = scoped_checks
    pipeline.main()
