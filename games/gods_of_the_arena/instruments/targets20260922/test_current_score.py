"""Protect against accidental reuse of binary-win or old-release acceptance."""
import unittest
import current_score as s


def cell(score, rival=10, **kw):
    return dict(target='rival', opponent='exact-uuid', side=0, games=40, invalid=0,
                all_hashes_equal=True, game_version=s.CONTRACT['game_version'],
                engine_commit=s.CONTRACT['engine_commit'], own_score=score,
                opponent_score=rival, **kw)


class CurrentScore(unittest.TestCase):
    def test_draws_do_not_block_xp_progress(self):
        result = s.compare([cell(120, draws=40, wins=0)], [cell(100, wins=40)])
        self.assertTrue(result['research_improved'])

    def test_fort_wins_do_not_hide_score_regression(self):
        self.assertFalse(s.compare([cell(80, wins=40)], [cell(100, wins=0)])['research_improved'])

    def test_old_release_is_not_a_current_control(self):
        control = cell(100); control['game_version'] = '2026.9.16.5'
        with self.assertRaises(AssertionError): s.compare([cell(120)], [control])

    def test_changed_opponent_needs_new_control(self):
        control = cell(100); control['opponent'] = 'old-version'
        with self.assertRaises(KeyError): s.compare([cell(120)], [control])

    def test_invalid_games_cannot_qualify(self):
        candidate = cell(120); candidate['invalid'] = 1
        self.assertFalse(s.compare([candidate], [cell(100)])['research_improved'])

    def test_improvement_and_target_superiority_are_separate(self):
        result = s.compare([cell(120, rival=150)], [cell(100)])
        self.assertTrue(result['research_improved'])
        self.assertFalse(result['beats_each_target_color_by_score'])


if __name__ == '__main__': unittest.main()
