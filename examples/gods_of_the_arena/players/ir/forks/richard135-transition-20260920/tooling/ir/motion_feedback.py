"""Feed complete campaign evidence into candidate IRs without changing behavior."""
from copy import deepcopy
from pathlib import Path
import sys

from policy_ir import ROOT, bundle, compile_policy, digest, read, refresh_grounding, write


def feedback(directory, stage):
    path = directory / (stage + '-result.json')
    report = read(path)
    evidence = {'artifact': str(path.resolve().relative_to(ROOT)),
                'sha256': digest(path.read_bytes())}
    for name, metrics in report['metrics'].items():
        source = directory / 'candidates' / name
        if not source.exists():
            continue
        parent_path = source / 'policy.ir.json'
        if stage == 'confirmation':
            parent_path = directory / 'screen-feedback' / name / 'policy.ir.json'
        parent = read(parent_path)
        policy = deepcopy(parent)
        basic = (source / 'policy.bas').read_text()
        control = report['metrics']['v2']
        default = report['metrics']['default']
        claim = (f"Complete {stage} on published 2026.9.15.3: {metrics['wins']}/{metrics['games']} "
                 f"fort wins versus v2 {control['wins']} and default {default['wins']}; "
                 f"deaths per alive minute {metrics['death_rate']:.6f} versus v2 {control['death_rate']:.6f}; "
                 f"lifetime XP {metrics['xp']} versus v2 {control['xp']}. "
                 f"All {report['verified_games']} full replay state sequences verified. ")
        if stage == 'screen':
            claim += ('Selected for untouched confirmation. ' if name == report['selected'] else
                      'Did not advance under the frozen selection rule. ')
            claim += 'Adaptive multi-candidate discovery does not establish competitive superiority.'
        else:
            claim += ('Passed both fresh local win gates and survival/XP guardrails. Hosted confirmation pending.'
                      if report['passed'] else 'Failed the fresh local qualification rule; no promotion.')
        policy['belief']['claims']['B_candidate'] = {
            'claim': claim, 'status': 'requires_review', 'evidence': [evidence]}
        policy['belief']['claims']['B_motion_execution'] = {
            'claim': (f"{metrics['normal_retreats']} normal retreats followed verified basic hits; "
                      f"{metrics['unverified_retreats']} lacked that prerequisite. "
                      f"{metrics['moved_kite_ticks']} retreat ticks produced actual displacement; "
                      f"{metrics['motion_completions']} ended on the public separation/disappeared-threat condition. "
                      f"Explicit offensive casts during retreats: {metrics['spells']}. "
                      'These mechanism counts are correlated within episodes and are not independent win evidence.'),
            'status': 'supported', 'evidence': [evidence]}
        policy['update'] = {
            'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
            'change': f'{stage} feedback; exact evaluated behavior retained.',
            'needs_review': ['belief/B_candidate', 'goal/G_fort', 'goal/G_survival'],
            'evidence': parent['update']['evidence'] + [evidence]}
        refresh_grounding(policy)
        if compile_policy(policy) != basic:
            raise ValueError('Evidence feedback changed evaluated behavior')
        output = directory / (stage + '-feedback') / name
        bundle(policy, output)
        write(output / 'parent.ir.json', parent)
        print(name, digest(basic.encode()))


if __name__ == '__main__':
    feedback(Path(sys.argv[1]), sys.argv[2])
