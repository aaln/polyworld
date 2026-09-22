"""Conditional later-draft mixed-roster guardrail, unchanged practiced bytes."""
import healthy_field as f

h = f.h
FIRST = f.OUT
OUT = h.STUDY / 'middle-field'


def prepare(c):
    h.CYCLE = 'interactive-current-draft-field-20260922'
    path = OUT / 'plan.json'
    if path.exists():
        return h.read(path)
    h.live(c)
    members = f.preflight(c)
    cfg = {k: v for k, v in h.read(h.STUDY / 'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed', 'players', 'tokens')}
    arms = []
    for label, version in [('candidate', f.CANDIDATE), ('control', h.INCUMBENT)]:
        for side in (0, 1):
            subject = side * 5 + 2
            pool = iter(m['policy_version']['id'] for m in members)
            roster = [version if i == subject else next(pool) for i in range(10)]
            background = h.research.fingerprint([None if i == subject else v for i, v in enumerate(roster)])
            arm = {'name': label, 'target': 'mixed-third-pick', 'opponent': background,
                   'side': side, 'version': version, 'own_slots': [subject],
                   'roster': roster, 'games': 40}
            body = {'idempotency_key': 'gota-current-middle-field0922-' + label + '-' + str(side) + '-' + background[:8],
                    'target': {'coworld_id': h.GAME, 'variant_id': 'competition'},
                    'game_config_overrides': cfg, 'num_episodes': 40,
                    'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(roster)],
                    'notes': 'Conditional mixed-team later-draft guardrail. Exact practiced/control versions and matched rosters, one third-pick subject, both colors. XP score gate; all ten VMs/full replay audit. No automatic league selection.'}
            folder = OUT / label / str(side)
            h.freeze(folder / 'arm.json', arm)
            h.freeze(folder / 'request.json', body)
            arms.append(arm)
    plan = {'game_version': h.VERSION, 'engine_commit': h.COMMIT, 'cycle': h.CYCLE,
            'games': 160, 'arms': arms, 'candidate_source_sha256': f.current_score.CONTRACT['reference_source_sha256'],
            'evaluator_sha256': h.sha((f.panel.HERE / 'current_score.py').read_bytes()),
            'conditional_on': 'healthy-field/result.json complete and research_improved; unchanged candidate bytes',
            'rule': 'All40games/cell clean and replay/score audited. Own-score preservation >=95% control each color and strict aggregate gain >=10%. Fort outcomes diagnostic. This later-draft guardrail does not guarantee every draft seat or every roster.',
            'budget': 'Same current-draft-field cycle:160first-pick+160third-pick=320, below400; shared daily journal unchanged.'}
    h.freeze(path, plan)
    return plan


if __name__ == '__main__':
    with h.client() as c:
        plan = prepare(c)
    result_path = FIRST / 'result.json'
    if not result_path.exists():
        print('Later-draft guardrail frozen; awaiting complete first-pick comparison.')
    else:
        assert h.read(result_path)['research_improved'], 'No conditional guardrail spend after failed comparison'
        f.OUT = OUT
        f.run(plan, initial_queue=1)
