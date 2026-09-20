"""Validate source identity, audit accounting, references and frozen artifacts."""
import gzip
import hashlib
import json
from pathlib import Path
import re

from source_audit import ROOT, OUT, RUN, SOURCE_SHA, read, sha, write


def main():
    provenance = read(OUT / 'provenance.ir.json')
    assert sha(OUT / 'v135.bas') == SOURCE_SHA == provenance['source_sha256']
    for path, expected in provenance['original_frozen_artifacts_verified_unchanged'].items():
        assert sha(ROOT / path) == expected, path
    runtime = read(OUT / 'runtime-audit.ir.json')
    assert len(runtime['rows']) == runtime['episodes'] == 20
    for field in ['ticks', 'commands_matched', 'decisions']:
        assert sum(row[field] for row in runtime['rows']) == runtime[field], field
    assert all(r['all_state_hashes_equal'] and r['all_actions_consumed'] and r['source_sha256'] == SOURCE_SHA for r in runtime['rows'])
    assert runtime['probe_source_sha256'] == sha(Path(__file__).with_name('source_audit_probe.nim'))
    assert all(r['probe_sha256'] == sha(RUN / 'source-probe') for r in runtime['rows'])
    fixtures = read(OUT / 'discriminating-fixtures.ir.json')
    assert fixtures['source_sha256'] == SOURCE_SHA and fixtures['all_assertions_passed']
    assert fixtures['vm_source_sha256'] == sha(Path(__file__).with_name('source_fixture_vm.nim'))
    assert fixtures['vm_binary_sha256'] == sha(RUN / 'fixture-vm')
    assert len(fixtures['fixtures']) == fixtures['scenes'] == 12
    assert sum(len(f['actual']) for f in fixtures['fixtures']) == fixtures['executed_decisions'] == 21
    model = read(OUT / 'source-model.ir.json')
    assert set(['situation','belief','goal','skill','strategy','execution','update']) <= model.keys()
    assert not model['execution']['compilable'] and not model['execution']['validation']['proxy_usable']
    ids = {r['id'] for r in model['strategy']}
    assert len(ids) == 10
    fixture_ids = {f['id'] for f in fixtures['fixtures']}
    for skill in model['skill'].values():
        assert set(skill['fixture_ids']) <= fixture_ids
        assert 1 <= skill['source_lines'][0] <= skill['source_lines'][1] <= 666
    comparison = read(OUT / 'comparison.ir.json')
    assert len(comparison['claim_comparisons']) == 9
    counters = read(OUT / 'counter-hypotheses.ir.json')
    for row in comparison['claim_comparisons'] + counters['strategy']:
        assert set(row['source_mechanisms']) <= ids
    assert all(not r['original_status_changed'] for r in comparison['claim_comparisons'])
    economy = read(OUT / 'economy-audit.ir.json')
    assert economy['binary_sha256'] == sha(RUN / 'economy/economy-probe')
    assert len(economy['rows']) == 20
    verified_accounts = 0
    for row in economy['rows']:
        raw = ROOT / row['raw_receipt']
        assert sha(raw) == row['raw_sha256']
        with gzip.open(raw, 'rt') as f:
            receipt = json.load(f)
        assert receipt['all_state_hashes_equal'] and receipt['all_actions_consumed']
        assert receipt['identity']['binary_sha256'] == economy['binary_sha256']
        for hero in row['heroes']:
            rewards = [r for r in receipt['rewards'] if r['hero'] == hero['id']]
            purchases = [r for r in receipt['purchases'] if r['hero'] == hero['id']]
            assert purchases == hero['accepted_purchases']
            assert hero['initial']['total_xp'] + sum(r['xp'] for r in rewards) == hero['final']['total_xp']
            assert hero['initial']['gold'] + sum(r['gold'] for r in rewards) - sum(p['cost'] for p in purchases) == hero['final']['gold']
            xp, level = hero['final']['total_xp'], 1
            while level < 20 and xp >= 100 + 75*(level-1):
                xp -= 100 + 75*(level-1)
                level += 1
            assert (level, xp) == (hero['final']['level'], hero['final']['xp'])
            verified_accounts += 1
    assert verified_accounts == 200
    markdown = [OUT / p for p in ['README.md','counter-policy-guide.md','ranger-economy.md']]
    markdown += [ROOT / 'docs/guides/guide-opponent-model-ir.md', Path(__file__).with_name('README.md')]
    links = 0
    for path in markdown:
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            target = link.split('#')[0]
            assert (path.parent / target).exists(), (path, target)
            links += 1
    artifacts = {str(p.relative_to(ROOT)): sha(p) for p in OUT.iterdir() if p.is_file() and p.name != 'verification.json'}
    artifacts['docs/guides/guide-opponent-model-ir.md'] = sha(ROOT / 'docs/guides/guide-opponent-model-ir.md')
    instruments = ['source_audit_probe.nim','source_audit.py','source_fixture_vm.nim','source_audit_fixtures.py',
                  'economy_probe.nim','build_economy_probe.py','economy_audit.py','publish_source_audit.py',
                  'verify_source_audit.py','guide.py','test_guide.py','prepare_pair.py','build.py','publish_target.py','README.md']
    write(OUT / 'verification.json', {'schema':'gota-source-audit-verification/1','passed':True,
        'frozen_artifacts_unchanged':len(provenance['original_frozen_artifacts_verified_unchanged']),
        'replay_episodes':20,'commands_matched':runtime['commands_matched'],'fixture_scenes':12,
        'economy_accounts_reconciled':verified_accounts,'local_document_links_checked':links,
        'artifacts':artifacts,'instrumentation':{str(Path(__file__).with_name(n).relative_to(ROOT)):sha(Path(__file__).with_name(n)) for n in instruments}})
    print(f'PASS: 21 frozen artifacts, 20 exact-source games, 12 fixtures, {verified_accounts} economy accounts, {links} local links.')


if __name__ == '__main__':
    main()
