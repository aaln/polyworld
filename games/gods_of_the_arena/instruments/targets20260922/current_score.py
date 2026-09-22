"""Current-release score decisions, independent of historical win-only gates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CONTRACT = json.loads((ROOT / 'games/gods_of_the_arena/current.json').read_text())


def require_current(policy):
    assert policy['execution']['game_version'] == CONTRACT['game_version'], 'Historical game IR is not a current candidate'
    assert policy['execution']['binding'] == CONTRACT['binding'], 'Register and validate a new current binding explicitly'


def compare(cells, controls, minimum_games=40):
    """Requires exact target/side keys; caller audits XP and all ten VMs first."""
    old = {(c['target'], c['opponent'], c['side']): c for c in controls}
    assert len(old) == len(controls) == len(cells), 'Matched current controls required'
    own_total = parent_total = 0.0
    valid = preserved = beats = True
    for c in cells:
        b = old[c['target'], c['opponent'], c['side']]
        assert c['game_version'] == b['game_version'] == CONTRACT['game_version']
        assert c['engine_commit'] == b['engine_commit'] == CONTRACT['engine_commit']
        valid &= c['games'] >= minimum_games and b['games'] >= minimum_games
        valid &= c['invalid'] == b['invalid'] == 0
        valid &= c['all_hashes_equal'] and b['all_hashes_equal']
        preserved &= c['own_score'] >= .95 * b['own_score']
        beats &= c['own_score'] > c['opponent_score']
        own_total += c['own_score']
        parent_total += b['own_score']
    return {'research_improved': bool(valid and preserved and own_total > parent_total and own_total >= 1.10 * parent_total),
            'beats_each_target_color_by_score': bool(valid and beats),
            'valid': bool(valid), 'per_cell_preserved': bool(preserved),
            'own_score_sum': own_total, 'parent_score_sum': parent_total,
            'fort_outcomes_gate_progress': False}
