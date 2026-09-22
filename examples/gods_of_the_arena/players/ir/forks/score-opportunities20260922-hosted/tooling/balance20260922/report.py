"""Decompose every arm, realized draft, opponent score and score uncertainty."""
from collections import Counter
import json
import random
from environment import h, STUDY

NAMES = ['Vanguard', 'Ranger', 'Arcanist', 'Druid', 'Demon Hunter',
         'Death Knight', 'Crossbowman', 'Lich', 'Warlock', 'Berserker']


def main():
    plan = h.read(STUDY / 'hosted/plan.json')
    result = h.read(STUDY / 'hosted/result.json')
    assert result['complete'] and len(result['cells']) == 10
    cells, targets = [], []
    versions = {m['player']['name'].lower(): m['policy_version']['id'] for m in h.read(STUDY / 'memberships.json')}
    for arm, cell in zip(plan['arms'], result['cells']):
        assert (arm['name'], arm['side']) == (cell['name'], cell['side'])
        rows = cell['rows']
        assert len(rows) == cell['games'] == 40
        assert cell['invalid'] == sum(not r['valid'] for r in rows)
        assert cell['score'] == sum(r.get('score', 0) for r in rows) / 40
        by_pick = []
        for hero in sorted({r['class'] for r in rows if 'class' in r}):
            chosen = [r for r in rows if r.get('class') == hero]
            by_pick.append({'hero': NAMES[hero], 'games': len(chosen),
                            'score': sum(r['score'] for r in chosen) / len(chosen),
                            'deaths': sum(r['deaths'] for r in chosen) / len(chosen)})
        summary = {k: v for k, v in cell.items() if k != 'rows'}
        summary.update(picks=by_pick, hits=sum(r.get('hits', 0) for r in rows) / 40,
                       level=sum(r.get('level', 0) for r in rows) / 40,
                       wins=sum(r.get('win', 0) for r in rows), losses=sum(r.get('loss', 0) for r in rows),
                       draws=sum(r.get('draw', 0) for r in rows))
        cells.append(summary)
        for target in ('relh', 'jordan', 'richard'):
            slots = [i for i, v in enumerate(arm['roster']) if v == versions[target] and i // 5 != arm['side']]
            if slots:
                targets.append({'policy': arm['name'], 'side': arm['side'], 'target': target,
                    'version': versions[target], 'own_score': cell['score'],
                    'rival_score': sum(sum(r['scores'][i] for i in slots) / len(slots) for r in rows if 'scores' in r) / 40})
    rng = random.Random(20260922)
    comparisons = []
    for comparison in result['comparisons']:
        name = comparison['name']
        arms = [c for c in result['cells'] if c['name'] == name]
        controls = result['cells'][:2]
        clean = all(c['invalid'] == 0 for c in arms + controls)
        assert comparison['passed'] == (clean and
            all(c['score'] >= .95*b['score'] for c,b in zip(arms,controls)) and
            sum(c['score'] for c in arms) > sum(c['score'] for c in controls) and
            sum(c['score'] for c in arms) >= 1.1*sum(c['score'] for c in controls))
        deltas = []
        if clean:
            # Whole-game bootstrap, stratified by side. Descriptive interval;
            # neither an independent confirmation nor multiplicity correction.
            for _ in range(5000):
                means = []
                for group in (arms, controls):
                    means.append(sum(sum(rng.choice(c['rows'])['score'] for _ in range(40)) / 40 for c in group) / 2)
                deltas.append(means[0] - means[1])
            deltas.sort()
        comparisons.append({**comparison, 'score_difference_95_bootstrap': [deltas[124], deltas[4874]] if deltas else None,
                            'uplift_percent': 100*(comparison['score']/comparison['control_score']-1) if comparison['control_score'] else None})
    review = {'complete': True, 'selected': result['selected'], 'cells': cells,
              'comparisons': comparisons, 'opposing_target_scores': targets,
              'uncertainty': 'Whole-game, side-stratified percentile bootstrap; fixed rosters and four-way selection limit generalization. Realized-pick splits are descriptive, not causal hero effects.',
              'scope': '2026.9.22.2; 40 games per cell, one first-pick subject seat. Blue roster opposes relh; Jordan/Richard are allies there. No universal hero ranking, late-draft or #1 claim.'}
    h.write(STUDY / 'review.json', review)
    print(json.dumps({k: v for k, v in review.items() if k != 'opposing_target_scores'}, indent=2))


if __name__ == '__main__':
    main()
