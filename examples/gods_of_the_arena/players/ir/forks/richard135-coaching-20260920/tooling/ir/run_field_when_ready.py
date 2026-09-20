"""Wait for the complete frozen confirmation, then run its preregistered field gate."""
from pathlib import Path
import subprocess
import sys
import time
from policy_ir import HERE,read
study=Path(sys.argv[1]);confirmation=study/'hosted-confirmation/result.json'
while not confirmation.exists():
    try:
        import os
        os.kill(int(sys.argv[2]),0)
    except ProcessLookupError:
        raise RuntimeError('Confirmation controller ended without a verdict; inspect its retained artifacts')
    time.sleep(5)
if not read(confirmation)['passed']:
    print('Confirmation failed; no field request launched.',flush=True)
    sys.exit(0)
subprocess.run([sys.executable,str(HERE/'release_field.py'),str(study),'launch'],check=True)
with (study/'field/harvest.log').open('w') as harvest, (study/'field/audit.log').open('w') as audit:
    jobs=[subprocess.Popen([sys.executable,str(HERE/'release_field.py'),str(study),'harvest'],stdout=harvest,stderr=subprocess.STDOUT),
          subprocess.Popen([sys.executable,str(HERE/'watch_hosted_audit.py'),str(study/'field'),'--workers','2'],stdout=audit,stderr=subprocess.STDOUT)]
    status=[j.wait() for j in jobs]
    if any(status):raise RuntimeError(f'Field collectors failed: {status}')
subprocess.run([sys.executable,str(HERE/'release_field.py'),str(study),'report'],check=True)
print('Field gate complete; no league mutation.',flush=True)
