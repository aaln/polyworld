"""Snapshot the maintained guide for new studies; preserve historical guides."""
import hashlib
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
CANONICAL = ROOT / 'docs/guides/guide-opponent-model-ir.md'
NAME = 'guide-opponent-model-ir.md'


def freeze_guide(study, canonical=CANONICAL):
    study.mkdir(parents=True, exist_ok=True)
    snapshot = study / NAME
    if not snapshot.exists():
        shutil.copy2(canonical, snapshot)
    return {'artifact': NAME, 'sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest()}


def publish_guide(study, output, canonical=CANONICAL):
    snapshot, published = study / NAME, output / NAME
    # Older studies already published their original guide but did not retain a
    # raw-study copy. Do not retroactively associate them with today's guide.
    if published.exists():
        if snapshot.exists() and snapshot.read_bytes() != published.read_bytes():
            raise ValueError('Refusing to replace a published guide with a different study snapshot')
        return
    if not snapshot.exists():
        if (study / 'model-freeze.json').exists():
            raise ValueError('Frozen study has no guide snapshot; restore the historical guide before publishing')
        freeze_guide(study, canonical)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot, published)
