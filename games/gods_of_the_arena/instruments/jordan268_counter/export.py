"""Export a reviewable native Python IR and its exact compiler snapshot."""
import argparse
import ast
from copy import deepcopy
import pprint
import shutil
from pathlib import Path
import zipfile

from campaign import CLEAN, ROOT, STUDY, digest, read, write
from policy_ir import compile_policy, extract, refresh_grounding, grounded, executable, differences
from report import summarize


def export(name):
    summary = summarize()
    source = STUDY / 'candidates' / name
    policy = deepcopy(read(source / 'policy.ir.json'))
    original_basic = (source / 'policy.bas').read_text()
    output = ROOT / 'examples/gods_of_the_arena/players/ir/forks/jordan268'
    output.mkdir(parents=True, exist_ok=True)
    write(output / 'evaluation.json', summary)
    shutil.copyfile(STUDY / 'evidence-index.json', output / 'evidence-index.json')
    shutil.copyfile(STUDY / 'candidate-verification.json', output / 'verification.json')
    lineage = []
    for candidate in ('waveclear', 'assembly', 'counterrace', 'redrace'):
        candidate_folder = STUDY / 'candidates' / candidate
        if not (candidate_folder / 'uploaded-version.json').exists():
            continue
        child = read(candidate_folder / 'policy.ir.json')
        parent_name = child['update']['change'].get('parent_candidate')
        parent = read(STUDY / 'candidates' / parent_name / 'policy.ir.json') if parent_name else read(
            ROOT / 'docs/opponents/jordan-v268/observer-policy.ir.json')
        lineage.append({'candidate': candidate, 'id': child['id'], 'parent_candidate': parent_name or 'primary',
                        'source_ir_sha256': digest(child), 'parent_ir_sha256': digest(parent),
                        'basic_sha256': digest((candidate_folder / 'policy.bas').read_bytes()),
                        'uploaded_version': read(candidate_folder / 'uploaded-version.json')['id'],
                        'change': child['update']['change'],
                        'executable_diff': differences(executable(parent), executable(child))})
    write(output / 'lineage.json', lineage)
    records = output / 'research-records'
    records.mkdir(exist_ok=True)
    for record in (ROOT / 'games/gods_of_the_arena/experiments').glob('*-jordan268-*.md'):
        shutil.copyfile(record, records / record.name)
    evidence = {'artifact': 'evaluation.json', 'sha256': digest((output / 'evaluation.json').read_bytes())}
    own = [a for a in summary['arms'] if a['name'] == name]
    results = '; '.join(f"{a['stage']} {a['color']} {a['wins']}/{a['n']}" for a in own)
    confirmed = {a['color']: a for a in own if a['stage'] == 'confirmation'}
    passed = set(confirmed) == {'red', 'blue'} and all(a['n'] == 40 and a['wins'] >= 30 for a in confirmed.values())
    policy['belief']['claims']['Jordan268_fork_evaluation'] = {
        'claim': f'Exact real Jordan v268, fixed five-versus-five on release.5: {results}. '
        + ('Meets the precommitted scoped 30/40-per-color criterion. ' if passed else
           'Does not meet the precommitted both-color confirmation criterion. ')
        + 'Generated seeds, repeated trajectory signatures and a narrow roster limit generalization; '
        'the opponent IR is a behavioral guide, not an executable Jordan proxy.',
        'status': 'supported' if passed else 'requires_review', 'evidence': [evidence]}
    blue_parent = [a for a in summary['arms'] if a['name'] == 'counterrace'
                   and a['stage'] == 'confirmation' and a['color'] == 'blue']
    if blue_parent and 'Jordan268_counterpressure' in policy['belief']['claims']:
        arm = blue_parent[0]
        policy['belief']['claims']['Jordan268_counterpressure'].update(
            claim=f"Nearby-only blue recall in the counterrace parent confirmed {arm['wins']}/{arm['n']} "
            "wins against exact Jordan268; the waveclear blue screen was0/4. This supports "
            "the counterpressure response in the fixed lineup, with repeated trajectory "
            "signatures and unmatched cohorts. It does not establish Jordan's private intent.",
            status='supported', evidence=[evidence])
    if 'Jordan268_I_O15' in policy['belief']['claims']:
        policy['belief']['claims']['Jordan268_I_O15'].update(
            claim='The observed Jordan268 O15 hero-over-creep tendency motivated the fork. '
            'Waveclear alone screened red3/4 and blue0/4; its red branch later confirmed14/40. '
            'The benefit of retaining waveclear inside the final recall policy has not been '
            'isolated by an ablation. Keep opponent prediction support separate from '
            'counter-strategy causality.', status='requires_review')
    if 'Jordan268_red_counterpressure' in policy['belief']['claims'] and passed:
        policy['belief']['claims']['Jordan268_red_counterpressure'].update(
            claim=f"Nearby-only recall on red and blue confirmed {confirmed['red']['wins']}/40 red "
            f"and {confirmed['blue']['wins']}/40 blue wins against exact Jordan268. The immediate "
            "parent confirmed14/40 red and40/40 blue. Supports the response on these fixed "
            "lineups; replay signatures repeat and cohorts were not seed-matched.",
            status='supported', evidence=[evidence])
    policy['update'].update(revision=policy['update']['revision'] + 1,
                            parent=digest(read(source / 'policy.ir.json')),
                            change={'origin': 'audited hosted feedback', 'candidate': name,
                                    'both_color_criterion_passed': passed})
    if passed:
        policy['update']['needs_review'] = [path for path in policy['update']['needs_review']
                                           if path != 'belief/Jordan268_red_counterpressure']
    if 'belief/Jordan268_I_O15' not in policy['update']['needs_review']:
        policy['update']['needs_review'].append('belief/Jordan268_I_O15')
    policy['update']['evidence'].append(evidence)
    refresh_grounding(policy)
    assert compile_policy(policy) == original_basic
    assert extract(original_basic, policy) == policy
    write(output / 'policy.ir.json', policy)
    write(output / 'semantics.json', grounded(policy))
    (output / 'policy.py').write_text('"""Primary-format executable IR fork; see evaluation.json for its measured scope."""\n\nPOLICY = '
                                   + pprint.pformat(policy, width=110, sort_dicts=False) + '\n')
    (output / 'policy.bas').write_text(original_basic)
    shutil.copyfile(Path(__file__).with_name('contracts.py'), output / 'contracts.py')
    # Keep the exact native compiler self-contained without copying an unrelated checkout.
    pending, modules = ['policy_ir'], {}
    while pending:
        module = pending.pop()
        path = CLEAN / (module + '.py')
        if module in modules or not path.exists():
            continue
        modules[module] = path
        for node in ast.walk(ast.parse(path.read_text())):
            imports = ([a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import)
                       else [node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            pending.extend(m for m in imports if m not in modules and (CLEAN / (m + '.py')).exists())
    game_prefix = 'examples/gods_of_the_arena/'
    archived = {game_prefix + 'players/ir/' + module + '.py': path for module, path in modules.items()}
    archived.update({game_prefix + name: CLEAN.parents[1] / name for name in ('content.nim', 'bots.nim', 'sim.nim')})
    archived[game_prefix + 'players/base.bas'] = CLEAN.parent / 'base.bas'
    with zipfile.ZipFile(output / 'compiler.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for archive_name, path in sorted(archived.items()):
            info = zipfile.ZipInfo(archive_name, date_time=(2026, 9, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    manifest = {'game_version': '2026.9.16.5', 'game_commit': 'f2ab9598d8f8001b6beae3e66404e341770c803f',
                'compiler_origin': str(CLEAN),
                'compiler_files': {m: digest(p.read_bytes()) for m, p in sorted(archived.items())},
                'compiler_zip_sha256': digest((output / 'compiler.zip').read_bytes()),
                'contracts_sha256': digest((output / 'contracts.py').read_bytes()),
                'basic_sha256': digest(original_basic.encode()), 'policy_ir_sha256': digest(policy),
                'tested_source_ir_sha256': digest(read(source / 'policy.ir.json')),
                'uploaded_version': read(source / 'uploaded-version.json')['id'],
                'selected_candidate': name, 'both_color_criterion_passed': passed}
    manifest['evidence_sha256'] = {file: digest((output / file).read_bytes()) for file in
                                  ('evaluation.json', 'evidence-index.json', 'verification.json',
                                   'lineage.json', 'semantics.json')}
    manifest['evidence_sha256'].update({str(p.relative_to(output)): digest(p.read_bytes())
                                       for p in records.glob('*.md')})
    version = read(source / 'uploaded-version.json')
    deployment_text = 'This is an uploaded fork; it has not been promoted into the league.'
    promotion_path = STUDY / 'promotion/promotion-verified.json'
    if promotion_path.exists():
        promotion = read(promotion_path)
        if promotion['policy_version']['id'] == version['id']:
            assert promotion['basic_sha256'] == manifest['basic_sha256']
            receipt = {'decision': read(STUDY / 'promotion/decision.json'), 'verification': promotion}
            write(output / 'promotion.json', receipt)
            manifest['promotion'] = {'artifact': 'promotion.json',
                'sha256': digest((output / 'promotion.json').read_bytes()),
                'verified_at': promotion['verified_at'], 'state': promotion['state']}
            deployment_text = (f"Promotion verified at {promotion['verified_at']}: active, competing champion "
                               "for Aaron’s Co-play Coach in Gods of the Arena. "
                               "See [promotion receipt and rollback](promotion.json).")
    aaron_promotion_path = STUDY / 'promotion-aaron/promotion-verified.json'
    if aaron_promotion_path.exists():
        promotion = read(aaron_promotion_path)
        if promotion['source_policy_version_id'] == version['id']:
            assert promotion['basic_sha256'] == manifest['basic_sha256']
            receipt = {'decision': read(STUDY / 'promotion-aaron/decision.json'), 'verification': promotion}
            write(output / 'promotion-aaron.json', receipt)
            manifest['promotion_aaron'] = {'artifact': 'promotion-aaron.json',
                'sha256': digest((output / 'promotion-aaron.json').read_bytes()),
                'policy_version_id': promotion['policy_version']['id'],
                'verified_at': promotion['verified_at'], 'state': promotion['state']}
            deployment_text += (f" Aaron’s player was upgraded to `{promotion['policy_version']['label']}` "
                f"at {promotion['verified_at']}, verified active, competing champion with identical BASIC. "
                "See [Aaron’s promotion receipt and rollback](promotion-aaron.json).")
    write(output / 'manifest.json', manifest)
    results_table = '\n'.join(
        f"| {a['name']} | {a['stage']} | {a['color']} | {a['wins']}/{a['n']} | "
        f"{a['distinct_audit_signatures']} | [XP](https://softmax.com/observatory/v2?tab=overview&detail=experience-request:{a['request']}) |"
        for a in summary['arms'])
    pending = [r for r in summary['pending'] if r['name'] == name]
    status = ('The frozen fork meets the precommitted criterion of at least30/40 fresh wins '
              'on each color.' if passed else 'The fork has not met the precommitted criterion '
              'of at least30/40 fresh wins on each color. Pending arms: ' +
              ', '.join(f"{r['stage']} {r['color']} ({r['n']})" for r in pending) + '.')
    (output / 'README.md').write_text(f'''`{policy['id']}` forks the primary `gota_relh154_legacy` in the same seven-layer Python representation. [policy.py](policy.py) exposes a plain `POLICY` dictionary. [policy.ir.json](policy.ir.json), [policy.bas](policy.bas), and [semantics.json](semantics.json) preserve its executable behavior and explicit skill meanings.

{status} Selected version: `{version['name']}:v{version['version']}` (`{version['id']}`). {deployment_text}

The response was guided by [Jordan v268’s observed opponent IR](../../../../../../docs/opponents/jordan-v268/opponent.ir.md), particularly O15’s tendency to target heroes when heroes, creeps and structures coexist. Actual evaluation used the real hosted Jordan version `207ffaf9-0d1e-4d92-a15d-4352f1bddec2`, not an inferred proxy.

The fork clears creep waves during existing defense and keeps distant heroes on their ordinary offensive path instead of recalling them across the map. Beyond28tiles from the friendly god, the final redrace variant clears defense before selecting ordinary targets; nearby heroes retain the primary defense. Attack, movement, inventory and purchase rules still execute in their original order, including multiple commands per decision. The binding adds an explicit semantic operation, with no hidden opponent-state input.

The important experimental correction was that red’s initial3/4 waveclear screen fell to14/40 in confirmation. Opening assembly also failed0/4. Nearby-only recall then confirmed40/40 on blue in the immediate parent. Redrace extends that eligibility rule to red and preserves the blue executable branch. Those results are recorded separately below.

| Candidate | Stage | Color | Wins | Distinct audit signatures | Request |
|---|---|---|---:|---:|---|
{results_table}

All completed arms passed full replay state-hash and action-consumption checks, all10VM validity, pinned rosters/build/config, score and totalXP agreement. [evaluation.json](evaluation.json) contains aggregate results; [evidence-index.json](evidence-index.json) contains every completed episode and artifact hashes. The campaign has audited {summary['audited_episodes']} episodes and {summary['audited_ticks']:,} game ticks so far.

Scope: fixed five-versus-five lineups on published GOTA2026.9.16.5. Generated seeds were not matched A/B. Audit signatures exclude RNG state and include sampled frames, events and full hero summaries; they can repeat across seeds and are not counts of independent trajectories. The winning screens repeat one such signature per color. These results do not establish broad league performance or causal necessity of every retained component.

Verify the standalone bundle with Python3.10+ and its standard library:

```sh
python3 examples/gods_of_the_arena/players/ir/forks/jordan268/verify.py
```

The verifier unpacks the original native compiler snapshot into a temporary directory and checks Python→JSON→BASIC plus full-source reverse extraction. [manifest.json](manifest.json) pins all compiler files, source mechanics, the additive [contracts.py](contracts.py), and tested BASIC SHA256 `{manifest['basic_sha256']}`. The original primary policy remains available in the observer snapshot; no primary source was overwritten.

For the coach/autoresearcher: retain the failed assembly and insufficient waveclear results, distinguish opponent-prediction evidence from response validation, and use fresh confirmation after selection. A useful next experiment is an ablation of creep priority under nearby-only recall; its necessity has not been isolated. Broader rosters and Jordan versions require separate tests. No such extra experiments or promotion are implied by this result.

Reproducible research files remain in `games/gods_of_the_arena/instruments/jordan268_counter`, preregistered records in `games/gods_of_the_arena/experiments`, and raw hosted artifacts in `tmp/gota-ir/jordan268-counter-20260920`. Every request is also listed in the evidence index.
''')
    (output / 'verify.py').write_text('''"""Verify and recompile this frozen fork using its native compiler snapshot."""
import hashlib,json,runpy,sys,zipfile,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((HERE/'compiler.zip').read_bytes())==manifest['compiler_zip_sha256']
assert sha((HERE/'contracts.py').read_bytes())==manifest['contracts_sha256']
for name,expected in manifest['evidence_sha256'].items():assert sha((HERE/name).read_bytes())==expected
with zipfile.ZipFile(HERE/'compiler.zip') as z:
 assert set(z.namelist())==set(manifest['compiler_files'])
 for name,expected in manifest['compiler_files'].items():assert sha(z.read(name))==expected
 workspace=tempfile.TemporaryDirectory(prefix='j268-native-ir-')
 z.extractall(workspace.name)
sys.path.insert(0,str(Path(workspace.name)/'examples/gods_of_the_arena/players/ir'))
import contracts
from policy_ir import compile_policy,extract,digest
policy=runpy.run_path(str(HERE/'policy.py'))['POLICY']
for ref in policy['belief']['claims']['Jordan268_fork_evaluation']['evidence']:
 assert sha((HERE/ref['artifact']).read_bytes())==ref['sha256']
assert policy==json.loads((HERE/'policy.ir.json').read_text())
source=compile_policy(policy)
assert source==(HERE/'policy.bas').read_text()
assert digest(policy)==manifest['policy_ir_sha256']
assert sha(source.encode())==manifest['basic_sha256']
assert extract(source,policy)==policy
print(json.dumps({'verified':True,'candidate':manifest['selected_candidate'],'basic_sha256':manifest['basic_sha256'],'uploaded_version':manifest['uploaded_version']}))
''')
    print('EXPORTED', output, 'criterion_passed', passed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    export(parser.parse_args().name)
