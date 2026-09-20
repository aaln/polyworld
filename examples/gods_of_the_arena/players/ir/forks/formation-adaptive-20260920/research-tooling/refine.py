"""Verify the exact-command runtime repair across every original local case."""
from concurrent.futures import ThreadPoolExecutor
import subprocess
from local import ROOT,STUDY,read,write,digest,local


def main():
    name='profile_pruned';source=STUDY/'candidates'/name/'policy.bas'
    plan=read(STUDY/'local-plan.json')
    prospective={'candidate':name,'source_sha256':digest(source.read_bytes()),'cases':plan['cases'],
      'repair':'Move actor-distance calculation inside the existing enemy-hero/creep branch that alone consumes it. No scan cutoff, threshold or policy behavior change.',
      'prior_failures':'profile_switch and profile_fold both19210 on first red Richard; first stage16games completed and remainsfailed. Deployed control19349 is valid belowhard20000, not a new margin-admitted candidate.',
      'gate':'All8complete games fully audited, own five VMs <=19000instructions/50000work, otherVMs belowhard20000; all ten complete command streams exactly match original profile_switch. Blue Richard retains exact formation behavior. Original hosted numerical gates unchanged.'}
    path=STUDY/'pruned-plan.json'
    if path.exists():assert read(path)==prospective
    else:write(path,prospective)
    stream=ROOT.parent/'gota-autoresearch/cycles/20260919T101825Z-880d3c/replay-command-stream'
    def one(case):
        out=STUDY/'pruned-local'/str(case['seed'])
        row=local.match(name,case,source,plan['opponents'][case['opponent']],out)
        if not row['valid']:return row
        actual=__import__('json').loads((out/'stdout.log').read_text().splitlines()[-1])
        row['own_max_instructions']=max(h['max_instructions'] for h in actual['heroes'][case['side']*5:case['side']*5+5])
        hashes=[]
        for tape in [out/'replay.bin',STUDY/'local/profile_switch'/str(case['seed'])/'replay.bin']:
            p=subprocess.run([str(stream),str(tape)],capture_output=True,check=True);hashes.append(digest(p.stdout))
        row.update(command_streams=hashes,exact_original_commands=hashes[0]==hashes[1])
        write(out/'equivalence.json',row);return row
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(one,plan['cases']))
    passed=all(r['valid'] and r['gear_heroes']==5 and r['own_max_instructions']<=19000 and r['exact_original_commands'] for r in rows)
    verdict={'passed':passed,'candidate':name,'source_sha256':digest(source.read_bytes()),'games':len(rows),'rows':rows}
    write(STUDY/'pruned-verdict.json',verdict)
    if passed:
        assert read(STUDY/'vm-proof-profile_pruned.json')['passed']
        write(STUDY/'hosted-admission.json',{'passed':True,'candidate':name,'source_sha256':digest(source.read_bytes()),
          'native_proof':str(STUDY/'vm-proof-profile_pruned.json'),'complete_game_proof':str(STUDY/'pruned-verdict.json'),
          'max_own_instructions':max(r['own_max_instructions'] for r in rows),'blue_richard_parity':str(STUDY/'local-verdict.json')})
    print('Runtime repair',passed,[(r['seed'],r.get('own_max_instructions'),r.get('exact_original_commands')) for r in rows],flush=True)


if __name__=='__main__':main()
