"""Finite Richard-only diagnostic of two already registered defense policies."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_richard as v

STUDY = v.STUDY / 'critical-blue-confirmation'


def main():
    with v.r.lock(STUDY / 'runner.lock', blocking=False):
        plan = v.r.read(STUDY / 'plan.json')
        frozen = v.r.read(STUDY / 'plan.sha256.json')['sha256']
        assert v.r.sha(STUDY / 'plan.json') == frozen
        assert len(plan['arms']) == 2 and sum(a['games'] for a in plan['arms']) == 80
        assert all(a['rival_version'] == '7c370daf-3c5f-42f8-870b-54b79c495a44'
                   and a['color'] == 'blue' for a in plan['arms'])
        v.live()
        proofs = []
        with v.client() as api:
            for arm in plan['arms']:
                source = Path(arm['source'])
                metadata = v.r.read(source / 'upload-request.json')
                assert v.r.sha(source / 'policy.bas') == metadata['content_hash']
                proofs.append(v.r.verify_remote_source(api, metadata, arm['policy_version']))
        v.r.write(STUDY / 'source-identity.json', proofs)
        os.environ['GOTA_RESEARCH_CYCLE'] = v.CYCLE
        v.r.write(STUDY / 'owner.json', {'pid': os.getpid(), 'cycle': v.CYCLE,
            'authorized_games': 80, 'combined_finite_cycle_games': 400,
            'purpose': 'Diagnostic only; frozen historical320 remains unchanged.'})
        for arm in plan['arms']:
            directory = Path(arm['directory'])
            if (directory / 'arm-result.json').exists():
                continue
            assert v.r.sha(STUDY / 'plan.json') == frozen
            while not (directory / 'batch/created.json').exists():
                try:
                    v.r.xp_create(v.ROOT, directory / 'request.json', directory / 'batch')
                except ValueError as exc:
                    if 'Three XP batches already active' not in str(exc):
                        raise
                    time.sleep(30)
            ident = v.r.read(directory / 'batch/created.json')['id']
            print(json.dumps({'arm': arm['key'], 'request': ident}), flush=True)
            with (directory / 'harvest.log').open('a') as log:
                subprocess.run([v.PYTHON, str(v.COLLECTOR), str(directory)],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
            result = v.r.read(directory / 'arm-result.json')
            print(json.dumps({'arm': arm['key'], **{k:x for k,x in result.items() if k != 'rows'}}), flush=True)
        cells = [{'key': a['key'], **{k:x for k,x in v.r.read(Path(a['directory']) / 'arm-result.json').items()
                                     if k != 'rows'}} for a in plan['arms']]
        v.r.write(STUDY / 'result.json', {'complete': True, 'cells': cells,
            'promotion_eligible': False, 'interpretation': plan['decision_rule']})


if __name__ == '__main__':
    main()
