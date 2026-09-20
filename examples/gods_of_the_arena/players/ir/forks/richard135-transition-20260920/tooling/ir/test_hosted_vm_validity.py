from pathlib import Path
import tempfile
import unittest

from hosted_wave_audit import verify_vm_validity
from policy_ir import write


class VMValidityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        (self.folder / 'game.log').write_text('Pod logs were not captured: unavailable pod\n')
        self.status = {'schema_version': '1', 'players': [
            {'slot': slot, 'state': 'exited', 'exit_code': 0, 'reason': 'Completed'} for slot in range(10)]}

    def test_structured_status_recovers_capture_failure(self):
        write(self.folder / 'player-status.json', self.status)
        verify_vm_validity(self.folder)
        self.assertTrue((self.folder / 'vm-validity.json').exists())

    def test_failed_vm_cannot_pass(self):
        self.status['players'][4].update(exit_code=1, reason='BASIC VM disabled')
        write(self.folder / 'player-status.json', self.status)
        with self.assertRaisesRegex(ValueError, 'ten successful'):
            verify_vm_validity(self.folder)

    def test_duplicate_or_missing_seat_cannot_pass(self):
        self.status['players'][9]['slot'] = 8
        write(self.folder / 'player-status.json', self.status)
        with self.assertRaisesRegex(ValueError, 'ten successful'):
            verify_vm_validity(self.folder)

    def test_completed_api_without_status_is_insufficient(self):
        write(self.folder / 'episode.json', {'status': 'completed', 'error': None})
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)

    def test_structured_success_cannot_override_explicit_vm_failure(self):
        (self.folder / 'game.log').write_text('scripts: 9/10 active, 1000 decisions\n')
        write(self.folder / 'player-status.json', self.status)
        with self.assertRaisesRegex(ValueError, 'disabled'):
            verify_vm_validity(self.folder)

    def test_unexplained_log_truncation_is_not_a_capture_marker(self):
        (self.folder / 'game.log').write_text('unexplained incomplete output')
        write(self.folder / 'player-status.json', self.status)
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)

    def test_game_container_transport_failure_requires_structured_status(self):
        (self.folder / 'game.log').write_text("===== container: game =====\nb'unable to retrieve container logs for containerd://" + 'a'*64 + "'\n")
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)
        write(self.folder / 'player-status.json', self.status)
        verify_vm_validity(self.folder)

    def test_other_container_failure_does_not_hide_incomplete_game_logs(self):
        (self.folder / 'game.log').write_text("===== container: worker =====\nb'unable to retrieve container logs for containerd://" + 'a'*64 + "'\n===== container: game =====\nincomplete game log\n")
        write(self.folder / 'player-status.json', self.status)
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)


    def missing_log(self):
        (self.folder / 'game.log').unlink()
        write(self.folder / 'episode.json', {'id': 'ereq_exact'})
        write(self.folder / 'game-log-response.json', {
            'episode_id': 'ereq_exact', 'status_code': 404,
            'path': '/v2/episode-requests/ereq_exact/artifacts/logs',
            'body': {'detail': 'No logs found for job missing-job'}})
        write(self.folder / 'player-status.json', self.status)

    def test_official_missing_log_response_uses_actual_status_without_fake_log(self):
        self.missing_log()
        verify_vm_validity(self.folder)
        self.assertFalse((self.folder / 'game.log').exists())

    def test_unproven_log_absence_cannot_pass(self):
        self.missing_log()
        (self.folder / 'game-log-response.json').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)

    def test_another_episodes_missing_log_does_not_authorize_fallback(self):
        self.missing_log()
        write(self.folder / 'episode.json', {'id': 'ereq_different'})
        with self.assertRaisesRegex(ValueError, 'missing'):
            verify_vm_validity(self.folder)


if __name__ == '__main__':
    unittest.main()
