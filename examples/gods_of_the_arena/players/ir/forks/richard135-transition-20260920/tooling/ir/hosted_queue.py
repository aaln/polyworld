"""Run frozen 100-game arms serially; harvest and audit concurrently per arm."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time

from hosted_batch import batch_body
from hosted_wave import client, create, episodes
from policy_ir import HERE, read, write


def run(folders):
    jobs = []
    with client() as c:
        for folder in folders:
            plan = read(folder / 'plan.json')
            request = create(c, batch_body(plan, 100), folder / 'batch')
            print(f'{folder.name}: {request}', flush=True)
            for script, args, log in [
                    ('hosted_batch.py', [str(folder), 'harvest', '--watch'], 'harvest.log'),
                    ('watch_hosted_audit.py', [str(folder), '--workers', '2'], 'audit.log')]:
                stream = (folder / log).open('a')
                proc = subprocess.Popen([sys.executable, str(HERE / script), *args], stdout=stream, stderr=stream)
                jobs.append((proc, stream, folder, script))
            while True:
                rows = episodes(c, request)
                statuses = dict(Counter(ep['status'] for ep in rows))
                write(folder / 'server-progress.json', {'request': request, 'statuses': statuses,
                                                       'checked_at': datetime.now(timezone.utc).isoformat()})
                if any(ep['status'] in {'failed', 'cancelled', 'error'} for ep in rows):
                    raise ValueError('Retain failed game and recover the exact request: ' + request)
                if len(rows) == 100 and statuses == {'completed': 100}:
                    print(f'{folder.name}: 100 games finished; artifacts and audits streaming', flush=True)
                    break
                time.sleep(15)
    failures = []
    for proc, stream, folder, script in jobs:
        code = proc.wait()
        stream.close()
        if code:
            failures.append(f'{script} failed for {folder}')
    # Let later collectors finish even if an earlier audit needed recovery.
    # Exiting the parent early can terminate still-running child collectors.
    if failures:
        raise ValueError('; '.join(failures) + '; recover before interpreting results')
    print('Every requested game, artifact and full replay audit completed.', flush=True)


if __name__ == '__main__':
    run([Path(path).resolve() for path in sys.argv[1:]])
