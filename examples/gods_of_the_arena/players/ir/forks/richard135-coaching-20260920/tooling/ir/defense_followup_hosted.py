"""Serialize follow-up defense experiments and stop after a full-suite winner."""
import argparse
import time
from pathlib import Path

import counterpush_hosted as runner
from policy_ir import digest, read, write
from ranger_guard_queue import alive
from release_workspace import RUN


def main(study, predecessor, prefix):
    pid=read(predecessor/'hosted-process.json')['pid']
    write(study/'queue-state.json',{'stage':'waiting_for_predecessor','directory':str(predecessor),'pid':pid})
    while alive(pid):time.sleep(15)
    prior=predecessor/'hosted-comparison.json'
    if not prior.exists():raise RuntimeError('Predecessor stopped without final verdict; reconcile first')
    verdict=read(prior)
    winner=verdict.get('selected') or verdict.get('upstream_selected')
    if winner:
        write(study/'hosted-comparison.json',{'selected':None,'stage':'not_run',
            'reason':'Predecessor passed the full suite; avoid unnecessary follow-up XP.',
            'predecessor':str(prior),'upstream_selected':winner,'promotion_performed':False})
        return
    while not (study/'local/comparison.json').exists():
        if not alive(read(study/'local-process.json')['pid']):
            raise RuntimeError('Local evaluation stopped without verdict')
        time.sleep(15)
    candidates=read(study/'local/comparison.json')['qualified'][:2]
    for name in candidates:
        proof_path=study/'activation-proof.json'
        if not proof_path.exists():raise RuntimeError('Native activation proof required before upload')
        proofs=read(proof_path)
        proof=proofs.get('candidates',{}).get(name,proofs)
        source=study/'local/candidates'/name/'policy.bas'
        if not proof['passed'] or proof['source_sha256']!=digest(source.read_bytes()):
            raise RuntimeError('Missing activation for this exact source')
        for row in proof['rows']:
            p=row['proof']
            if not p['all_state_hashes_equal'] or not p['all_actions_consumed']:
                raise RuntimeError('Incomplete activation replay')
            if any(p['unsupported_hold_decisions'][1:]):
                raise RuntimeError('Wait rule activated on an unintended slot')
        if not any(sum(r['proof']['unsupported_hold_decisions']) for r in proof['rows']):
            raise RuntimeError('Wait rule never activated in recorded games')
    runner.STUDY=study
    runner.PREFIX=prefix
    runner.CHANGE='Coordinated caster assistance and source-bound DeathKnight readiness; preserve recall, rally, pressure roles and blue behavior.'
    runner.RICHARD_RED_FLOOR=30
    runner.RED_KITE_FLOOR=24
    runner.DESIGN=('Coached coordinated defense: existing recall/rally, caster public-intent support '
        'and source-bound DeathKnight readiness. Local parent is corrected bound_idle caster '
        'policy. Full actual activation required before upload. Richard78 requires30red/38blue '
        'in40/color, then Jordan186 requires38/color, g002,redkite27 requires24red,vanguard,black '
        'and mixed200. Frozen historical pool for comparison; newer versions need follow-up. '
        'Complete replay/runtime/equipment audits; correlated fixed-lineup evidence is '
        'directional. Reused controls are not new games. No automatic promotion.')
    runner.main()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('study',type=Path);p.add_argument('predecessor',type=Path);p.add_argument('prefix')
    a=p.parse_args();main(a.study,a.predecessor,a.prefix)
