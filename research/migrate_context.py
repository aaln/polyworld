"""Copy selected, version-scoped knowledge without changing captured inputs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(json.loads((ROOT / 'research/manifest.json').read_text())['archive'])
LIBRARY = ROOT / 'research/library'
VENDOR = ROOT / 'research/vendor'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def copy(relative, target, records):
    source = ARCHIVE / relative
    dest = target / relative
    if dest.exists():
        assert sha(source) == sha(dest), dest
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    records[str(dest.relative_to(ROOT))] = {
        'origin': str(source), 'sha256': sha(source), 'bytes': source.stat().st_size,
        'scope': 'Frozen historical reference; original release and result apply.'}


def main():
    assert not (LIBRARY / 'manifest.json').exists(), 'Migration already captured; preserve it'
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ARCHIVE).decode().split('\0')
    bundles = [
        'docs/opponents/relh-v169/source-audit-20260923/',
        'docs/opponents/richard-v174/source-audit-20260923/',
        'docs/opponents/khors-v114/score-audit-20260923/',
        'docs/opponents/khors-v179/score-audit-20260923/',
        'docs/opponents/richard-v135/source-audit-20260920/',
        'docs/coaching/',
        'games/gods_of_the_arena/release-audits/',
    ]
    selected = {f for f in tracked if any(f.startswith(p) for p in bundles)}
    selected.update(f for f in tracked if f.startswith('games/gods_of_the_arena/experiments/2026-09-2')
                    and f.endswith('.md') and '/2026-09-20-' not in f)
    selected.update('docs/guides/' + f for f in
                    ['guide-opponent-model-ir.md', 'guide-episode-semantic-ir.md',
                     'guide-gota-score-analysis.md'])
    # The long former "current release" guide mixes many dated checkpoints.
    # Preserve a reference hash, not another competing current entry point.
    roots = ARCHIVE / 'examples/gods_of_the_arena/players/ir/forks'
    pairs = {
        'crossbow-draft': 'balance-draft20260922',
        'core-buyback': 'core-buyback20260923/core-buyback',
        'combat-elixir': 'combat-elixir20260923/combat-elixir',
        'portal-recovery': 'portal-coaching20260922-hosted',
        'blue-opening': 'blue-center20260923-hosted/blue-center',
        'all-class-sustain': 'field-sustain20260923-hosted/field-sustain',
        'all-class-lane-recovery': 'lane-recovery20260923-hosted/lane-recovery',
        'richard-siege-transfer': 'richard17420260923-hosted/guarded-siege',
        'blue-druid-siege': 'blue-druid-siege20260923-hosted/blue-druid-siege',
        'avoid-buildings': 'unit-farming20260923-hosted/unit-farming',
        'selective-building-finishes': 'selective-finish20260923-hosted/selective-finish',
        'explicit-sustain': 'weakhero20260923-hosted/explicit-sustain',
        'control-legality': 'control20260923-local/control-legality',
        'control-tactics': 'controltactics20260923-hosted/control-tactics',
        'lane-occupancy': 'lanefarm20260923-hosted/lane-occupancy',
        'harvest-value': 'harvest-value20260923-local/harvest-value',
    }
    pair_records = {}
    for key, relative in pairs.items():
        path = roots / relative
        assert (path / 'policy.ir.json').exists() and (path / 'policy.bas').exists(), key
        names = ['policy.ir.json', 'policy.bas', 'policy.py', 'extracted.ir.json',
                 'semantics.json', 'manifest.json', 'README.md']
        for name in names:
            if (path / name).exists(): selected.add(str((path / name).relative_to(ARCHIVE)))
        # Carry results and session bindings, not every duplicate historical runner.
        for pattern in ['*review*.json', '*statistic*.json', '*summary*.json', '*manifest*.json',
                        '*session*.json', '*request*.json']:
            for p in (path / 'evidence').glob(pattern):
                if p.is_file(): selected.add(str(p.relative_to(ARCHIVE)))
        m = json.loads((path / 'manifest.json').read_text()) if (path / 'manifest.json').exists() else {}
        ir = json.loads((path / 'policy.ir.json').read_text())
        pair_records[key] = {
            'path': str((LIBRARY / path.relative_to(ARCHIVE)).relative_to(ROOT)),
            'source_sha256': sha(path / 'policy.bas'),
            'original_binding': ir['execution']['binding'],
            'original_game_version': ir['execution']['game_version'],
            'original_qualification': m.get('deployment_qualified'),
            'current_promotion_qualified': False,
            'conversion': 'Historical snapshot. Port its hypothesis into an active portable pair; original tooling remains at origin.',
        }
    records = {}
    for relative in sorted(selected): copy(relative, LIBRARY, records)

    # Capture the complete local import graph used by current API/audit wrappers.
    modules = []
    for name in ['hosted', 'recovery_statistics']:
        spec = importlib.util.spec_from_file_location('migration_source_' + name,
                    ROOT / 'research' / (name + '.py'))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        modules.append(mod)
    queue = modules + list(sys.modules.values())
    seen, dependencies = set(), set()
    while queue:
        mod = queue.pop()
        if not isinstance(mod, types.ModuleType) or id(mod) in seen: continue
        seen.add(id(mod))
        filename = getattr(mod, '__file__', None)
        if not filename: continue
        path = Path(filename).resolve()
        if path.is_relative_to(ARCHIVE): dependencies.add(path.relative_to(ARCHIVE))
        if path.is_relative_to(ARCHIVE) or path.is_relative_to(ROOT):
            queue.extend(v for v in vars(mod).values() if isinstance(v, types.ModuleType))
    vendor_records = {}
    for relative in sorted(dependencies): copy(relative, VENDOR, vendor_records)
    write(VENDOR / 'manifest.json', {'files': vendor_records,
          'usage': 'Import-only implementation dependencies. Current wrappers supply engine, campaign, sources and study. Do not run historical entry points.'})
    legacy = [ARCHIVE / 'docs/guides/guide-gota-current-release.md',
              ARCHIVE / 'docs/opponents/jordan-v268/observer-policy.ir.json',
              ARCHIVE / 'docs/opponents/alex-g002-v1/observer-policy.ir.json']
    write(LIBRARY / 'manifest.json', {'files': records, 'pairs': pair_records,
          'indexed_only': [{'origin': str(p), 'sha256': sha(p),
                           'reason': 'Obsolete release or overlapping chronological handoff; retrieve only for an explicitly version-scoped question.'}
                          for p in legacy],
          'archive_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ARCHIVE).decode().strip(),
          'policy': 'All copied bytes match captured origin. Historical promotion flags are not current-engine qualifications.'})
    print(json.dumps({'reference_files': len(records), 'historical_pairs': len(pairs),
                      'vendored_modules': len(vendor_records)}))


if __name__ == '__main__': main()
