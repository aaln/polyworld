"""Retrospective participant scores: never call an allied target an opponent."""
from panel import h


def main():
    targets = {m['player']['name']: m['policy_version']['id']
               for m in h.read(h.STUDY / 'healthy-field/memberships.json')
               if m['player']['name'] in ('relh', 'Jordan', 'richard')}
    rows = []
    for stage in ('healthy-field', 'middle-field'):
        for side in (0, 1):
            folder = h.STUDY / stage / 'candidate' / str(side)
            arm, cell = h.read(folder / 'arm.json'), h.read(folder / 'result.json')
            rivals = []
            for name, version in targets.items():
                slot = arm['roster'].index(version)
                if slot // 5 == side:
                    continue
                scores = [h.read(folder / 'artifacts' / r['episode'] / 'results.json')['scores'][slot] for r in cell['rows']]
                rivals.append({'name': name, 'version': version, 'slot': slot,
                               'mean_score': sum(scores) / len(scores)})
            rows.append({'stage': stage, 'side': side, 'own_score': cell['own_score'],
                         'opposing_targets': rivals})
    h.write(h.STUDY / 'field-target-scores.json', {
        'scope': 'Retrospective exact opposing participant scores in fixed mixed rosters; allies excluded, not uniform head-to-head tests.',
        'rows': rows})


if __name__ == '__main__':
    main()
