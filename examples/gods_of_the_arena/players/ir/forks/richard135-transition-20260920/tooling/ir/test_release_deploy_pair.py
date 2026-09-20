from copy import deepcopy
import unittest

from release_deploy_pair import AARON, CONTROL, DIVISION, OPTIMIZER, PRIOR_OPTIMIZER, check_champions


class PairedDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'player': {'id': p}, 'policy_version': {'id': v}, 'division': {'id': DIVISION},
            'status': 'competing', 'substatus': 'active', 'is_champion': True}
            for p, v in [(AARON, CONTROL), (OPTIMIZER, PRIOR_OPTIMIZER)]]
        self.versions = {AARON: 'aaron-copy', OPTIMIZER: 'optimizer-tested'}

    def test_initial_partial_and_final_states_are_resumable(self):
        check_champions(self.rows, self.versions)
        for row in reversed(self.rows):
            row['policy_version']['id'] = self.versions[row['player']['id']]
            check_champions(self.rows, self.versions)

    def test_successor_study_requires_exact_current_pair(self):
        priors = {AARON: 'current-aaron', OPTIMIZER: 'current-optimizer'}
        for row in self.rows:
            row['policy_version']['id'] = priors[row['player']['id']]
        with self.assertRaises(ValueError):
            check_champions(self.rows, self.versions)
        check_champions(self.rows, self.versions, priors)
        self.rows[0]['policy_version']['id'] = CONTROL
        with self.assertRaises(ValueError):
            check_champions(self.rows, self.versions, priors)
        with self.assertRaises(ValueError):
            check_champions(self.rows, self.versions, {AARON: 'current-aaron'})

    def test_cannot_assign_the_other_players_version(self):
        self.rows[0]['policy_version']['id'] = self.versions[OPTIMIZER]
        with self.assertRaises(ValueError):
            check_champions(self.rows, self.versions)

    def test_extra_or_missing_player_is_rejected(self):
        for rows in [self.rows[:1], self.rows + [deepcopy(self.rows[0])]]:
            with self.assertRaises(ValueError):
                check_champions(rows, self.versions)

    def test_wrong_division_or_inactive_champion_is_rejected(self):
        for key, value in [('status', 'retired'), ('is_champion', False), ('division', {'id': 'wrong'})]:
            rows = deepcopy(self.rows)
            rows[0][key] = value
            with self.assertRaises(ValueError):
                check_champions(rows, self.versions)


if __name__ == '__main__':
    unittest.main()
