from pathlib import Path
import tempfile
import unittest

from guide import freeze_guide, publish_guide, NAME


class GuideCustodyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.canonical = self.root / 'current.md'
        self.canonical.write_text('revision two')
        self.study, self.out = self.root / 'study', self.root / 'published'

    def test_new_study_freezes_before_guide_changes(self):
        receipt = freeze_guide(self.study, self.canonical)
        self.canonical.write_text('revision three')
        self.assertEqual(freeze_guide(self.study, self.canonical), receipt)
        publish_guide(self.study, self.out, self.canonical)
        self.assertEqual((self.out / NAME).read_text(), 'revision two')

    def test_legacy_published_snapshot_is_immutable(self):
        self.out.mkdir()
        (self.out / NAME).write_text('historical guide')
        publish_guide(self.study, self.out, self.canonical)
        self.assertEqual((self.out / NAME).read_text(), 'historical guide')
        self.assertFalse(self.study.exists())

    def test_conflicting_snapshot_is_rejected(self):
        freeze_guide(self.study, self.canonical)
        self.out.mkdir()
        (self.out / NAME).write_text('historical guide')
        with self.assertRaises(ValueError):
            publish_guide(self.study, self.out, self.canonical)
        self.assertEqual((self.out / NAME).read_text(), 'historical guide')

    def test_frozen_study_cannot_acquire_new_guide_at_publication(self):
        self.study.mkdir()
        (self.study / 'model-freeze.json').write_text('{}')
        with self.assertRaises(ValueError):
            publish_guide(self.study, self.out, self.canonical)
        self.assertFalse((self.study / NAME).exists())


if __name__ == '__main__':
    unittest.main()
