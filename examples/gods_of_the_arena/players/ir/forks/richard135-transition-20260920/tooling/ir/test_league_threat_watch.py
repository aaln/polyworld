import unittest
from league_threat_watch import AARON, OPTIMIZER, classify


def episode(red_owner=OPTIMIZER, blue_owner='rival', red_score=0, blue_score=1):
    return {'id': 'example', 'status': 'completed', 'participants': [
        {'position': s, 'player_id': red_owner if s < 5 else blue_owner,
         'policy_version_id': 'red-v1' if s < 5 else 'blue-v1',
         'policy_name': 'red' if s < 5 else 'blue', 'version': 1} for s in range(10)],
        'participant_scores': [{'position': s, 'score': red_score if s < 5 else blue_score} for s in range(10)]}


class ThreatClassification(unittest.TestCase):
    versions = {OPTIMIZER: ['red-v1'], AARON: ['blue-v1']}

    def test_five_copies_are_one_loss(self):
        rows = classify(episode(), self.versions)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['outcome'], 'loss')
        self.assertTrue(rows[0]['needs_replay_review'])

    def test_timeout_is_not_a_defeat(self):
        row = classify(episode(blue_score=0), self.versions)[0]
        self.assertEqual(row['outcome'], 'draw')
        self.assertFalse(row['needs_replay_review'])

    def test_self_play_does_not_invent_an_external_threat(self):
        rows = classify(episode(blue_owner=AARON), self.versions)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['self_duel'] for r in rows))
        self.assertFalse(any(r['needs_replay_review'] for r in rows))

    def test_superseded_policy_is_not_attributed_to_new_policy(self):
        self.assertEqual(classify(episode(), {OPTIMIZER: ['new-v2'], AARON: ['new-v2-copy']}), [])

    def test_two_winning_teams_is_invalid(self):
        with self.assertRaises(ValueError): classify(episode(red_score=1), self.versions)


if __name__ == '__main__': unittest.main()
