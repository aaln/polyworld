"""A league update must not bypass evidence, executable or player boundaries."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from release_deploy import AARON, CONTROL, DIVISION, PRIOR_OPTIMIZER, OPTIMIZER, owned_champions, readiness
from policy_ir import HERE, compile_policy, digest, read, write


class DeploymentBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.policy = read(HERE / 'base.ir.json')
        self.source = compile_policy(self.policy)
        files = {
            'hosted-discovery/result.json': {'selected': 'test'},
            'hosted-discovery/test/uploaded-version.json': {'id': 'candidate'},
            'hosted-discovery/test/upload-request.json': {'content_hash': digest(self.source.encode()), 'player_id': OPTIMIZER},
            'hosted-confirmation/result.json': {'passed': True, 'selected': 'test',
                'arms': {n: {'games': 400} for n in ['v2', 'cadence', 'test']}},
            'hosted-confirmation/test/feedback/policy.ir.json': self.policy,
            'field/result.json': {'passed': True, 'version': 'candidate', 'candidate': 'test',
                'games': 100, 'wins': 60, 'equipment_games': 100},
        }
        for name, value in files.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            write(self.root / name, value)
        write(self.root / 'hosted-confirmation/plan.json', {'candidate': 'test', 'sample_size': 400,
              'discovery_sha256': digest((self.root / 'hosted-discovery/result.json').read_bytes())})
        write(self.root / 'field/plan.json', {'excluded_players': [AARON, OPTIMIZER],
              'confirmation_sha256': digest((self.root / 'hosted-confirmation/result.json').read_bytes())})
        source_path = self.root / 'local/candidates/test/policy.bas'
        source_path.parent.mkdir(parents=True)
        source_path.write_text(self.source)

    def change(self, path, updates):
        write(self.root / path, read(self.root / path) | updates)

    def test_complete_consistent_evidence_is_eligible(self):
        self.assertEqual(readiness(self.root)[1]['id'], 'candidate')

    def test_field_failure_cannot_be_overridden_by_confirmation(self):
        self.change('field/result.json', {'passed': False, 'wins': 49})
        with self.assertRaisesRegex(ValueError, 'both pass'):
            readiness(self.root)

    def test_missing_games_are_not_a_finished_confirmation(self):
        self.change('hosted-confirmation/result.json', {'arms': {n: {'games': 399} for n in ['v2', 'cadence', 'test']}})
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            readiness(self.root)

    def test_replaced_evidence_breaks_field_binding(self):
        self.change('hosted-confirmation/result.json', {'different_evidence': True})
        with self.assertRaisesRegex(ValueError, 'provenance'):
            readiness(self.root)

    def test_post_evaluation_code_edit_cannot_deploy(self):
        path = self.root / 'local/candidates/test/policy.bas'
        path.write_text(self.source + '\nbuyItem(20)\n')
        with self.assertRaisesRegex(ValueError, 'IR, executable'):
            readiness(self.root)

    def test_a_different_player_cannot_receive_optimizer_upload(self):
        self.change('hosted-discovery/test/upload-request.json', {'player_id': AARON})
        with self.assertRaisesRegex(ValueError, 'player binding'):
            readiness(self.root)

    def test_deployment_preserves_two_players_and_aarons_policy(self):
        rows = [{'player': {'id': player}, 'policy_version': {'id': version},
                 'division': {'id': DIVISION}, 'status': 'competing',
                 'substatus': 'active', 'is_champion': True}
                for player, version in [(AARON, CONTROL), (OPTIMIZER, PRIOR_OPTIMIZER)]]
        self.assertEqual(len(owned_champions(rows, 'candidate')), 2)
        changed = deepcopy(rows)
        changed[0]['policy_version']['id'] = 'unexpected'
        with self.assertRaisesRegex(ValueError, 'changed outside'):
            owned_champions(changed, 'candidate')
        with self.assertRaisesRegex(ValueError, 'exactly the two'):
            owned_champions(rows + [deepcopy(rows[0])], 'candidate')


if __name__ == '__main__':
    unittest.main()
