"""Offline migration checks: provenance, exact conversion, and isolated imports."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(*args):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origins', action='store_true', help='Also hash original files, including media')
    parser.add_argument('--out', type=Path, help='New JSON report; refuses to overwrite')
    args = parser.parse_args()
    if args.out:
        assert not args.out.exists(), args.out
    manifest = read(ROOT / 'research/manifest.json')
    report = {'offline': True, 'engine_commit': manifest['engine_commit'], 'checks': {}}
    checks = report['checks']
    original_count = 0
    for name in ['library', 'vendor']:
        data = read(ROOT / 'research' / name / 'manifest.json')
        for local, row in data['files'].items():
            path = ROOT / local
            assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], local
            if args.origins:
                assert sha(Path(row['origin'])) == row['sha256'], row['origin']
                original_count += 1
        checks[name + '_byte_exact_files'] = len(data['files'])
        for row in data.get('pairs', {}).values():
            assert sha(ROOT / row['path'] / 'policy.bas') == row['source_sha256']
            assert row['current_promotion_qualified'] is False
        if 'pairs' in data:
            checks['historical_pairs'] = len(data['pairs'])
        if args.origins:
            for row in data.get('indexed_only', []):
                assert sha(Path(row['origin'])) == row['sha256']
                original_count += 1
    sessions = read(ROOT / 'research/coaching_inputs/manifest.json')['sessions']
    copied = indexed = 0
    for session in sessions.values():
        for row in session['files']:
            indexed += 1
            if row['local']:
                assert sha(ROOT / row['local']) == row['sha256'], row['local']
                copied += 1
            if args.origins:
                assert sha(Path(row['origin'])) == row['sha256'], row['origin']
                original_count += 1
    checks.update(coaching_sessions=len(sessions), coaching_copies=copied,
                  coaching_inputs_indexed=indexed, originals_verified=original_count)
    checks['portable_pairs'] = {}
    with tempfile.TemporaryDirectory(prefix='gota-context-verify-') as temp:
        for name, row in manifest['policies'].items():
            pair = ROOT / 'research/policies' / name
            assert sha(pair / 'policy.bas') == row['source_sha256'], name
            verified = json.loads(run(pair / 'verify.py').strip().splitlines()[-1])
            assert verified['verified']
            for mode in ['compile', 'extract']:
                out = Path(temp) / (name + '-' + mode)
                command = [pair / 'convert.py', mode, '--out', out]
                if mode == 'extract':
                    command.extend(['--source', pair / 'policy.bas'])
                run(*command)
                assert (out / 'policy.bas').read_bytes() == (pair / 'policy.bas').read_bytes()
                for filename in ['policy.ir.json', 'extracted.ir.json', 'semantics.json']:
                    assert read(out / filename) == read(pair / filename), (name, mode, filename)
            checks['portable_pairs'][name] = {'source_sha256': row['source_sha256'],
                                              'compile_and_extract_equal': True}
    index = read(ROOT / 'research/knowledge/controller.ir.json')
    pair = ROOT / 'research/policies/deployed'
    policy = read(pair / 'policy.ir.json')
    semantics = read(pair / 'semantics.json')
    source = (pair / 'policy.bas').read_text()
    assert index['strategy'] == policy['strategy']
    for rule in index['strategy']:
        item = index['skill'][rule['skill']]
        match = re.search(r"^' @rule " + re.escape(rule['id']) + r"\n(.*?)(?=\n\x27 @rule |\Z)", source, re.M | re.S)
        assert match and source[:match.start()].count('\n') + 1 == item['executable']['line']
        assert hashlib.sha256(match.group(1).encode()).hexdigest() == item['executable']['region_sha256']
        assert item['binding'] == policy['skill'][rule['skill']]
        assert item['grounded_contract'] == semantics['skills'][rule['skill']]
    checks['ordered_controller_rules'] = len(index['strategy'])
    layers = {'situation', 'belief', 'goal', 'skill', 'strategy', 'execution', 'update'}
    assert layers <= index.keys()
    assert layers <= read(ROOT / 'research/knowledge/hypotheses.ir.json').keys()
    for path in ['START_HERE.md', 'research/OPERATIONS.md', 'research/IR_WORKFLOW.md']:
        assert (ROOT / path).is_file(), path
    # A fresh subprocess catches accidental old-workspace imports and network calls.
    code = r'''
import importlib.util, json, pathlib, sys
root = pathlib.Path.cwd()
archive = json.loads((root/'research/manifest.json').read_text())['archive']
def guard(event, args):
    if event.startswith('socket.connect'):
        raise RuntimeError('Network use in offline import verification')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        name = str(pathlib.Path(args[0]).resolve())
        if name == archive or name.startswith(archive + '/'):
            raise RuntimeError('Old workspace dependency: ' + name)
sys.addaudithook(guard)
for name in ['hosted', 'recovery_statistics']:
    spec = importlib.util.spec_from_file_location('verify_migration_' + name, root/'research'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if name == 'hosted':
        assert module.h.ROOT == root and module.h.ENGINE == root
        config = module.shared_budget_config(module.h.CAMPAIGN)
        assert config['daily_episode_limit'] == 100000
print('offline imports passed')
'''
    assert 'offline imports passed' in run('-c', code)
    checks['imports_without_archive_or_network'] = True
    engine_files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only',
                      manifest['engine_commit'], 'examples/gods_of_the_arena'], cwd=ROOT, text=True).splitlines()
    for path in engine_files:
        expected = subprocess.check_output(['git', 'show', manifest['engine_commit'] + ':' + path], cwd=ROOT)
        assert (ROOT / path).read_bytes() == expected, 'Modified pinned engine file: ' + path
    checks['unchanged_engine_files'] = len(engine_files)
    report['passed'] = True
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
