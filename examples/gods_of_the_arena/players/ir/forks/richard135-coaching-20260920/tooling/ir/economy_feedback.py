"""Close the local evidence -> IR -> identical BASIC -> extracted IR loop."""
from copy import deepcopy
from pathlib import Path
import sys

from policy_ir import ROOT, bundle, compile_policy, digest, extract, read, refresh_grounding, write


def record(parent_path, source_path, claim, evidence_path, output):
    parent = read(parent_path)
    source = source_path.read_text()
    if compile_policy(parent) != source:
        raise ValueError('Parent IR does not represent the tested BASIC')
    evidence = {'artifact': str(evidence_path.resolve().relative_to(ROOT) if evidence_path.resolve().is_relative_to(ROOT) else evidence_path.resolve()),
                'sha256': digest(evidence_path.read_bytes())}
    policy = deepcopy(parent)
    policy['belief']['claims']['B_candidate'] = {
        'claim': claim, 'status': 'requires_review', 'evidence': [evidence]}
    policy['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                        'change': 'Complete measured feedback; exact tested behavior retained.',
                        'needs_review': ['belief/B_candidate', 'goal/G_fort', 'goal/G_survival'],
                        'evidence': parent['update']['evidence'] + [evidence]}
    refresh_grounding(policy)
    if compile_policy(policy) != source or extract(source, policy) != policy:
        raise ValueError('Evidence broke IR/symbolic parity')
    bundle(policy, output)
    write(output / 'parent.ir.json', parent)


def local(directory):
    path = directory / 'screen-result.json'
    report = read(path)
    rows = read(directory / 'screen-rows.json')
    for name in read(directory / 'plan.json')['variants']:
        m = report['metrics'][name]
        controls = ', '.join(f"{c} {report['metrics'][c]['wins']}/40" for c in ['v2', 'default', 'motion'])
        classes = {str(cls): {'games': len(rr := [r for r in rows if r['name'] == name and r['class'] == cls]),
                             'wins': sum(r['score'] for r in rr)} for cls in range(10)}
        claim = (f"Frozen40-case local discovery on published2026.9.15.3: {m['wins']}/40 fort wins versus {controls}. "
                 f"Death rate {m['death_rate']:.6f}/alive-minute; lifetime XP {m['xp']}; "
                 f"equipment in {m['gear_games']}/40 games; planned loadout purchases {m['loadout_purchases']}; "
                 f"actual moving kite ticks {m['moved_kite_ticks']}; unverified post-hit retreats {m['unverified_retreats']}. "
                 f"Class breakdown (small descriptive groups): {classes}. All {report['verified_games']} replay sequences verified. "
                 + ('Selected for hosted discovery. ' if name in report['selected'] else 'Did not qualify for hosted discovery. ')
                 + 'Selection among multiple candidates does not establish competitive superiority; hosted held-out confirmation is required.')
        folder = directory / 'candidates' / name
        record(folder / 'policy.ir.json', folder / 'policy.bas', claim, path, directory / 'screen-feedback' / name)
    print('All candidate IR beliefs updated; every evaluated BASIC remained byte-identical and reverse-extracted exactly.')


if __name__ == '__main__':
    local(Path(sys.argv[1]).resolve())
