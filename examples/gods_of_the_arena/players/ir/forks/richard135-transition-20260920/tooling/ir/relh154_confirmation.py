"""Fresh confirmation of a frozen relh154 candidate, forty games per side."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import sys
import json
import re
from relh154_research import STUDY,LABEL,RIVAL,RECORD
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze


def main(name):
    preliminary=read(STUDY/'hosted-result.json')
    assert name in preliminary['outcome_qualified']
    assert name in read(STUDY/'local/qualification.json')['qualified']
    review=read(STUDY/'hosted'/name/'review/decisions.json')['cases']
    wins=[r for r in review if r['color']=='blue' and r['win']]
    assert wins and all(r['proof']['all_state_hashes_equal'] and r['proof']['all_actions_consumed'] for r in review)
    assert all(len(r['first_recalls'])==5 and max(v['tick'] for v in r['first_recalls'].values())<3222 for r in wins)
    hosted.ROOT=STUDY/'confirmation';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Fresh heldout40episodes/color exactrelh154; frozen candidate after local and40blue discovery. Target40/40both, fullaudits. Source remains unchanged; no tuning during runs.'
    version=read(STUDY/'hosted'/name/'uploaded-version.json')
    hosted.VERSIONS[name]={'id':version['id'],'name':version['name']+':v'+str(version['version'])}
    freeze(hosted.ROOT/'selection.json',{'name':name,'source_sha256':digest((STUDY/'local/candidates'/name/'policy.bas').read_bytes()),
           'prior_result_sha256':digest((STUDY/'hosted-result.json').read_bytes()),'review_sha256':digest((STUDY/'hosted'/name/'review/decisions.json').read_bytes()),
           'rule':'Original prospective gate:40/40red and40/40blue, allfullaudits. No broadfield or tenplayerclaim.'})
    arms=[hosted.prepare('relh154',LABEL,name,color,RIVAL)[0] for color in ('red','blue')]
    results={}
    with ThreadPoolExecutor(2) as pool:
        for future in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            k,r=future.result();results[k]=r;write(hosted.ROOT/'progress.json',{'arms':results})
    passed=all(r['wins']==40 and r['all_full_audits_passed'] for r in results.values())
    write(hosted.ROOT/'result.json',{'name':name,'passed':passed,'arms':results,'promotion_performed':False})
    ids=[read(p)['id'] for root in (STUDY/'batches',STUDY/'confirmation') for p in root.glob('relh154/*/*/batch/created.json')]
    s=re.sub(r'^evals:.*$','evals: '+json.dumps(ids),RECORD.read_text(),flags=re.M);RECORD.write_text(s)
    print('CONFIRMATION',name,passed,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__':main(sys.argv[1])
