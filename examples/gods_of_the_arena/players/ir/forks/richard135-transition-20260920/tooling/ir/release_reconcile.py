"""Scope inherited evidence, then preserve exact evaluated BASIC through feedback."""
from copy import deepcopy
from pathlib import Path

from policy_ir import bundle, compile_policy, digest, extract, read, refresh_grounding, write

ARCHIVE = Path('/Users/aaln/experiments/softmax/polyworld')


def reconcile(parent_path, source_path, evidence_paths, claim, output, resolved_reviews=()):
    parent = read(parent_path)
    source = source_path.read_text()
    assert compile_policy(parent) == source
    policy = deepcopy(parent)
    if policy['execution']['game_version'] == '2026.9.16.3':
        policy['situation']['notes'] = ('Published2026.9.16.3, source7365e4e9390e97bbc8b7722b41a2ae88ae008c2b; clean tracked engine and24locked dependencies. Simulation source closure matches .2; older evidence retains its original release. Sixcreeps/lane/480ticks, current building collision and live host stats.')
    resolved, unresolved = [], []
    for name, belief in policy['belief']['claims'].items():
        if name in {'B_release', 'B_candidate'}:
            continue
        if belief['claim'].startswith('Inherited historical observation'):
            continue
        belief['claim'] = ('Inherited historical observation about the earlier policy/version or '
                           'experiment named below; this is not a measurement of the new release candidate. '
                           + belief['claim'])
        for evidence in belief['evidence']:
            path = Path(evidence['artifact'])
            if path.is_absolute():
                continue
            original = ARCHIVE / path
            if original.is_file() and digest(original.read_bytes()) == evidence.get('sha256'):
                evidence['artifact'] = str(original)
                resolved.append(str(original))
            else:
                # Keep the original identifier/hash; never fabricate a replacement.
                unresolved.append(evidence)
    evidence = [{'artifact': str(Path(p).resolve()), 'sha256': digest(Path(p).read_bytes())}
                for p in evidence_paths]
    policy['belief']['claims']['B_release_evaluation'] = {
        'claim': claim, 'status': 'supported', 'evidence': evidence}
    if 'belief/B_candidate' in resolved_reviews:
        policy['belief']['claims']['B_candidate'] = {'claim': claim, 'status': 'supported', 'evidence': evidence}
    policy['goal']['G_capacity']['preference'] = (
        'Preserve HP/mana support and class equipment purchases; retain gold for persistent combat strength.')
    if 'G_glory' in policy['goal']:
        policy['goal']['G_glory']['preference'] = (
            'Track the current local tournament diagnostic win*(lifetime XP -200*simulated minutes) '
            'separately from historical100-rate records. The Softmax league objective remains binary '
            'fort wins; survival qualification remains a deployment guard.')
    if policy['skill']['observe']['operator'] in ('building_enemy', 'class_building', 'class_building_two'):
        policy['goal']['G_base']['provenance'] = 'authored'
        if policy['skill']['observe']['operator'] == 'class_building':
            policy['goal']['G_base']['preference'] += ' Berserker instead uses baseline nearest-center selection.'
    policy['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                        'change': 'Scope historical evidence and reconcile latest-release observations/goals; preserve exact tested behavior.',
                        'needs_review': [r for r in parent['update']['needs_review'] if r not in resolved_reviews], 'evidence': evidence}
    refresh_grounding(policy)
    assert compile_policy(policy) == source and extract(source, policy) == policy
    bundle(policy, output)
    write(output/'parent.ir.json', parent)
    write(output/'historical-reference-resolution.json', {
        'resolved_verified_paths': resolved, 'unresolved_preserved_references': unresolved,
        'meaning': 'Only the new evidence list is used for the current release verdict. Historical missing references are preserved, not silently replaced.'})
    return policy
