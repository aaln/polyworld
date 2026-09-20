import unittest
from league_watch import OWN, RIVALS, head_to_head

class ScoreIdentityTests(unittest.TestCase):
    def episode(self, side=0):
        own, rival = OWN['Aaron'], RIVALS['Richard']
        teams = [(own, 'current-own'), (rival, 'current-rival')]
        if side: teams.reverse()
        return {'id': 'episode', 'status': 'completed',
            'participants': [{'position': i, 'player_id': teams[i//5][0], 'policy_version_id': teams[i//5][1]} for i in range(10)],
            'participant_scores': [{'position': i, 'score': int(i//5 == side)} for i in range(10)]}

    def setUp(self):
        self.champions = {OWN['Aaron']: {'version': 'current-own'}, RIVALS['Richard']: {'version': 'current-rival'}}

    def test_both_colors_and_duplicate_episode(self):
        for side, color in [(0, 'red'), (1, 'blue')]:
            ep = self.episode(side)
            counts, evidence = head_to_head([ep, ep], self.champions)
            self.assertEqual(counts, {'Aaron/Richard/'+color: {'wins': 1, 'losses': 0, 'draws': 0}})
            self.assertEqual(len(evidence), 1)

    def test_historical_mixed_incomplete_and_invalid_are_excluded(self):
        for change in ('old', 'mixed', 'pending', 'missing', 'both-win'):
            ep = self.episode()
            if change == 'old':
                for p in ep['participants'][:5]: p['policy_version_id'] = 'old-own'
            if change == 'mixed': ep['participants'][0]['player_id'] = OWN['Coach']
            if change == 'pending': ep['status'] = 'running'
            if change == 'missing': ep['participant_scores'].pop()
            if change == 'both-win':
                for p in ep['participant_scores']: p['score'] = 1
            self.assertEqual(head_to_head([ep], self.champions), ({}, []), change)

    def test_draw_is_not_win(self):
        ep = self.episode()
        for p in ep['participant_scores']: p['score'] = 0
        counts, _ = head_to_head([ep], self.champions)
        self.assertEqual(counts['Aaron/Richard/red'], {'wins': 0, 'losses': 0, 'draws': 1})

if __name__ == '__main__': unittest.main()
