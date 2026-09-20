"""An old audit failure must not terminate later artifact collectors."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from hosted_queue import run


class QueueRecoveryTests(unittest.TestCase):
    def test_all_children_drain_before_reporting_an_earlier_failure(self):
        waited = []
        children = []
        for index in range(4):
            def wait(index=index):
                waited.append(index)
                return 1 if index == 1 else 0
            children.append(Mock(wait=Mock(side_effect=wait)))
        with tempfile.TemporaryDirectory() as temp:
            folders = [Path(temp) / name for name in ['control', 'candidate']]
            for folder in folders:
                folder.mkdir()
            with (patch('hosted_queue.client'), patch('hosted_queue.read', return_value={}),
                  patch('hosted_queue.batch_body', return_value={}),
                  patch('hosted_queue.create', return_value='request'),
                  patch('hosted_queue.episodes', return_value=[{'status': 'completed'}] * 100),
                  patch('hosted_queue.subprocess.Popen', side_effect=children)):
                with self.assertRaisesRegex(ValueError, 'recover before interpreting'):
                    run(folders)
        self.assertEqual(waited, [0, 1, 2, 3])


if __name__ == '__main__':
    unittest.main()
