"""Public-observation response to a partially visible rush; no opponent labels."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess

from economy_feedback import record
from league_threat_review import run_native
from policy_ir import compile_policy, digest, extract, read, refresh_grounding, write
from ranger_guard_hosted import freeze
from release_workspace import RUN
from rush_defense_eval import evaluate
from red_pressure_hosted import prepare_head, result
from rush_hosted import upload
from win_hosted import live
from hero_binding import class_id
import test_policy_ir as f
from test_rush_unblock import UnblockTests
from test_rush_defense import scene

STUDY = RUN / 'coached-lanes/r5-macromackie-visible-rush'
PREVIOUS = RUN / 'coached-lanes/r5-macromackie-v4'
PARENT = RUN / 'coached-lanes/r5-jordan-lineup/candidate'
RECORD = Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-17-macromackie-visible-rush.md')
SEED = 815000
UPLOAD_PREFIX = 'aaron-gota-ir-visible-rush'
DESIGN = ('Visible-rush hypothesis: only blue_group4->3 from deployed blue_repair. '
          'No label/version read in game; identify observed clustered enemy heroes near '
          'standing friendly structures. Local12 perarm with red fullgame parity, native '
          'VM and fullaudit checks. Hosted40red40blue exactmacromackie-gota:v4. '
          'Targetedpass blue>=32 red>=38; no automatic promotion or broadfield claim.')


def make(name):
    parent = read(PARENT / 'policy.ir.json')
    if name == 'deployed':
        return parent
    if name != 'blue_three':
        raise ValueError(name)
    p = deepcopy(parent)
    p['id'] = 'gota_visible_rush_blue_three'
    p['skill']['observe']['parameters']['blue_group'] = 3
    p['goal']['G_defense']['preference'] += (
        ' On blue, three currently visible living enemy heroes clustered near a standing '
        'friendly structure are sufficient evidence to initiate existing defensive recall. '
        'Fog can hide the remainder of a five-hero push. Do not require an opponent name '
        'or infer that unseen enemies are present. Preserve existing bounded response, '
        'quiet release, class spacing and all red behavior.')
    evidence = PREVIOUS / 'color-analysis.json'
    p['belief']['claims']['B_visible_rush'] = {
        'status': 'untested', 'claim': DESIGN + ' Prediction: earlier blue recall reduces '
        'opening base collapses. Counter-risk: unnecessary defense against smaller groups.',
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Respond to three visible clustered blue-side attackers.')
    refresh_grounding(p)
    return p


def native_checks():
    class VM(UnblockTests):
        factory = staticmethod(make)
    VM.setUpClass()
    vm = VM()
    rows = []
    for name in ('deployed', 'blue_three'):
        p = make(name)
        assert extract(compile_policy(p), p) == p
        for team in (0, 1):
            for slot in range(5):
                for count in (0, 2, 3, 4):
                    case = scene(team, count=count, worldTick=100)
                    case['self'].update(selfId=100 + team * 5 + slot,
                                        selfClass=class_id(team, slot))
                    for i, enemy in enumerate(case['objects'][4:]):
                        enemy.update(objectId=100 + (1-team)*5+i,
                                     objectClass=class_id(1-team, i))
                    r = vm.play(name, [case], ('defActive', 'defCount'))[0]
                    expect = count >= (3 if team == 1 and name == 'blue_three' else 4)
                    assert bool(r['memory']['defActive']) == expect, (name, team, slot, count, r)
                    rows.append(r)
                    if count == 3 and team == 1:
                        case['objects'][3]['objectHp'] = 0
                        assert vm.play(name, [case], ('defActive',))[0]['memory']['defActive'] == 0
        for slot in range(5):
            for density in (40, 160, 240):
                case = scene(1, count=3, worldTick=100)
                case['self'].update(selfId=105+slot, selfClass=class_id(1, slot))
                for i, enemy in enumerate(case['objects'][4:]):
                    enemy.update(objectId=100+i, objectClass=class_id(0, i))
                case['objects'] += [f.obj(3000+i, kind=3, team=i%2, x=i%116, y=i*7%116)
                                    for i in range(density-len(case['objects']))]
                rows += vm.play(name, [case], ('defActive',))
    assert max(r['instructions'] for r in rows) <= 20000
    assert max(r['work'] for r in rows) <= 50000
    write(STUDY / 'vm-proof.json', {'passed': True, 'decisions': len(rows),
          'max_instructions': max(r['instructions'] for r in rows),
          'max_fixture_work': max(r['work'] for r in rows),
          'scope': 'Actual roster classes/IDs, group2/3/4 and absent standing anchor; dense scenes.'})


def main():
    STUDY.mkdir(parents=True, exist_ok=True)
    captured_record = STUDY / 'preregistered-experiment.md'
    if not captured_record.exists():
        captured_record.write_bytes(RECORD.read_bytes())
    freeze(STUDY / 'prospective.json', {'design': DESIGN, 'record_sha256': digest(captured_record.read_bytes()),
           'local_cases': 12, 'seed': SEED, 'hosted_cases': 80, 'blue_floor': 32, 'red_floor': 38})
    native_checks()
    opponents = {'default': RUN / 'r5/default.bas',
                 'current': Path(__file__).parent / 'win_bounded_0916.r5.evaluated.bas',
                 'center_proxy': RUN / 'coached-lanes/r5-convoy/screen/candidates/center/policy.bas'}
    evaluate('local', ['deployed', 'blue_three'], 12, SEED, make, STUDY,
             RUN / 'r5/fast/audit-local', opponents_override=opponents)
    local = read(STUDY / 'local/result.json')
    a, b = local['metrics']['blue_three'], local['metrics']['deployed']
    proofs = []
    for row in local['rows']:
        if row['name'] == 'blue_three' and row['color'] == 0:
            root = STUDY / 'local/games'
            proof = json.loads(subprocess.check_output([str(RUN / 'r5/compare-gameplay'),
                str(root/'blue_three'/str(row['seed'])/'replay.bin'),
                str(root/'deployed'/str(row['seed'])/'replay.bin')], text=True))
            proofs.append(proof)
    parity = len(proofs) == 6 and all(all(p[k] for k in
        ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in proofs)
    checks = {'all_gear': a['all_gear'], 'red_parity': parity, 'wins': a['wins'] >= b['wins'],
              'per_opponent': all(a['opponents'][k] >= b['opponents'][k] for k in b['opponents'])}
    write(STUDY / 'local/qualification.json', {'passed': all(checks.values()),
          'checks': checks, 'red_parity_proofs': proofs, 'candidate': a, 'control': b})
    if not all(checks.values()):
        write(STUDY/'result.json', {'passed': False, 'stage': 'local', 'checks': checks})
        return
    candidate = STUDY / 'local/candidates/blue_three'
    feedback = STUDY / 'local/qualified-feedback'
    if not feedback.exists():
        record(candidate/'policy.ir.json', candidate/'policy.bas',
               'Native actual-class thresholds/denseVM and local12 cases passed relative '
               'qualification; all6red fullgames exactly unchanged. Hostedpending. '+DESIGN,
               STUDY/'local/qualification.json', feedback)
    live()
    root, version = upload('blue_three', STUDY, UPLOAD_PREFIX, DESIGN,
        feedback_override=feedback, validation_note='Native mechanism/local runtime and redparity passed; hosted unvalidated inert candidate.')
    head = root / 'macromackie-v4'
    prepare_head(head, version, PREVIOUS/'reference', 'earlier observed rush response', DESIGN)
    r = result(head)
    passed = r['colors']['blue']['win'] >= 32 and r['colors']['red']['win'] >= 38
    report = {'passed': passed, 'candidate': r,
              'control': read(PREVIOUS/'comparison.json')['results']['blue_repair'],
              'version': version, 'promotion_performed': False,
              'scope': 'Frozen exactmatchup directional evidence; fullaudit verified. Native mechanism '
                       'and localredparity checked. Reconstruct hosted recall before final targetedverdict.'}
    write(STUDY/'result.json', report)
    if not (root/'evaluated-feedback').exists():
        record(feedback/'policy.ir.json', feedback/'policy.bas',
               f'Complete80macromackie-v4:{r["colors"]}; outcome gate passed={passed}. '
               'No broadfield validation or league promotion.', STUDY/'result.json', root/'evaluated-feedback')
    print('HOSTED COMPLETE', r['colors'], 'outcome gate', passed, flush=True)


if __name__ == '__main__':
    main()
