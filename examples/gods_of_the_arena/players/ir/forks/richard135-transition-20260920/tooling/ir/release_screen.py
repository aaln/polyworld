"""Frozen new-release screen, using independently rebuilt clean instruments."""
from datetime import datetime, timezone
import random
import shutil

from economy_screen import run
from policy_ir import HERE, bundle, digest, read, write
from release_candidates import VARIANTS, make, rebase
from release_workspace import RUN, SOURCE, VERSION, verify


def prepare():
    verify()
    directory = RUN / 'local'
    directory.mkdir(exist_ok=True)
    if (directory / 'plan.json').exists():
        return directory
    for name in ['episode', 'audit']:
        shutil.copy2(RUN / 'build' / name, directory / name)
    coworld = read(RUN / 'live-before/coworld.json')
    config = next(v['game_config'] for v in coworld['manifest']['variants'] if v['id'] == 'competition')
    write(directory / 'config.json', config)
    shutil.copy2(HERE.parent / 'base.bas', directory / 'default.bas')
    sources = {'default': directory / 'default.bas'}
    for name, file in [('v2', 'waveguard_xp.evaluated.ir.json'), ('cadence', 'cadence_all.evaluated.ir.json')]:
        bundle(rebase(file), directory / 'controls' / name)
        sources[name] = directory / 'controls' / name / 'policy.bas'
    for name in VARIANTS:
        bundle(make(name), directory / 'candidates' / name)
        sources[name] = directory / 'candidates' / name / 'policy.bas'
    instruments = [p for p in HERE.glob('*.py') if not p.name.startswith('test_')]
    frozen = directory / 'frozen-instruments'
    frozen.mkdir()
    for p in instruments:
        shutil.copy2(p, frozen / p.name)
    inputs = [directory / n for n in ['episode', 'audit', 'config.json']] + list(sources.values())
    slots = list(range(10)) * 4
    random.Random(2026091603).shuffle(slots)
    write(directory / 'plan.json', {
        'created_at': datetime.now(timezone.utc).isoformat(), 'family': 'release',
        'game_version': VERSION, 'game_source': SOURCE, 'variants': VARIANTS,
        'sources': {n: str(p) for n, p in sources.items()},
        'inputs': {str(p): digest(p.read_bytes()) for p in inputs},
        'instruments': {p.name: digest(p.read_bytes()) for p in instruments},
        'cases': [{'seed': 730000 + i, 'slot': s} for i, s in enumerate(slots)],
        'selection_controls': ['v2', 'default', 'cadence'], 'survival_control': 'cadence',
        'rule': 'Complete280 full local games and audits. Each candidate needs>=2 more wins than each of cadence, waveguard and default; deaths/alive-minute<=110%cadence, XP>=80%cadence, gear every game, no invalid VM or unconfirmed-hit recovery. Rank by wins, lower death rate, XP, name; at most two advance. Local selection only. New100-episode fixed-incumbent batches for both deployed controls regardless of candidate selection. If qualifiers exist, complete same100/candidate before ranking. Candidate needs>=5pp over both controls plus survival/XP/gear guards for fresh400/arm confirmation. Confirmation requires>=5pp and one-sided Fisher p<.025 against each control, no adverse-class p<.005, same survival/XP/gear guards; all games/audits, no optional stopping. Then100 random-current-champion field games requiring>=50wins and all gear/VM checks. No new league selection without those gates.',
        'stop_rule': 'No old-release outcome pooling, no dropped seeds or optional stopping. Preserve failures; resume identical inputs only.'})
    return directory


if __name__ == '__main__':
    run(prepare(), 8, 'release')
