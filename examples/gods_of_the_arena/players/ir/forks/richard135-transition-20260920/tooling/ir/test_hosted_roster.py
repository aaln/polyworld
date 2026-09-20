import unittest

from campaign_hosted_compare import verify_rotated_roster


class RosterAssignmentTests(unittest.TestCase):
    def test_every_class_keeps_the_pinned_teammate_assignment(self):
        expected = ['subject', *[f'opponent-{i}' for i in range(9)]]
        for shift in range(10):
            actual = expected[-shift:] + expected[:-shift] if shift else expected
            verify_rotated_roster(actual, expected, 'subject')

    def test_same_members_and_subject_seat_with_swapped_teams_is_rejected(self):
        expected = ['subject', *[f'opponent-{i}' for i in range(9)]]
        actual = expected.copy()
        actual[1], actual[6] = actual[6], actual[1]
        with self.assertRaisesRegex(ValueError, 'Opponent order'):
            verify_rotated_roster(actual, expected, 'subject')

    def test_missing_or_duplicate_policy_is_rejected(self):
        expected = ['subject', *[f'opponent-{i}' for i in range(9)]]
        actual = expected.copy()
        actual[1] = actual[2]
        with self.assertRaisesRegex(ValueError, 'membership'):
            verify_rotated_roster(actual, expected, 'subject')


if __name__ == '__main__':
    unittest.main()
