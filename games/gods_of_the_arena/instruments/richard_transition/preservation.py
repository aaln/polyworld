"""Recorded all-command blue parity and pre-transition red boundaries."""
import json
import subprocess
from fresh_hit import STUDY,NAMES,read,write,digest
from study import case,run,PARENT,CAMPAIGN


def main():
    binary=CAMPAIGN/'cycles/20260919T101825Z-880d3c/replay-command-stream'
    proof=read(binary.parent/'command-stream-calibration/proof.json')
    assert proof['passed'] and proof['binary_sha256']==digest(binary.read_bytes())
    rows=read(STUDY/'local-results.json')['rows'];cases=[]
    for seed in sorted({r['seed'] for r in rows if r['side']==1}):
        entries=[]
        for name in NAMES:
            folder=STUDY/'local'/name/str(seed)
            result=read(folder/'result.json');audit=read(folder/'audit.json')
            assert result['valid'] and audit['hash_mismatches']==0
            output=subprocess.run([str(binary),str(folder/'replay.bin')],capture_output=True,check=True)
            info=json.loads(output.stderr)
            assert info['ticks']==audit['ticks'] and info['actions_consumed']==audit['recorded_actions']
            entries.append({'name':name,'all10_command_sha256':digest(output.stdout),
                'audit_sha256':digest((folder/'audit.json').read_bytes())})
        assert len({e['all10_command_sha256'] for e in entries})==1
        assert len({e['audit_sha256'] for e in entries})==1
        cases.append({'seed':seed,'exact_commands_and_audit_equal':True,'entries':entries})
    boundaries=[]
    for slot in range(5):
        c=case(slot=slot,tick=4799)
        old=run(PARENT/'policy.bas',[c],memory=[])[0]
        new=run(STUDY/'candidates/transition_freshhit/policy.bas',[c],memory=[])[0]
        assert old['actions']==new['actions']
        boundaries.append({'slot':slot,'tick':4799,'actions_equal':True})
    write(STUDY/'preservation-proof.json',{'passed':True,'blue_paired_cases':cases,'red_prephase':boundaries,
        'scope':'All10 canonical commands and full audits equal for all6paired blue local cases of each final candidate. Red unmodified-equipment source also matches prephase scenarios; armor intentionally changes red purchasing before phase. No claim of universal equivalence from sampled cases.'})
    print('PRESERVATION PASSED',flush=True)


if __name__=='__main__':main()
