"""Select a fresh win-first winner over the currently selected Lich versions."""
import argparse
from policy_ir import read,digest,compile_policy,extract
from release_deploy_pair import main as deploy
from release_deploy import AARON
from release_hosted import OPTIMIZER
from win_hosted import CURRENT
from win_screen import STUDY
PRIORS={OPTIMIZER:CURRENT,AARON:'7321f8ff-f9d7-46fe-828c-3168bc21af1a'}

def readiness(study):
    root=study/'hosted-confirmation';plan=read(root/'plan.json');r=read(root/'result.json');name=plan['candidate']
    disc=study/'hosted-discovery';version=read(disc/name/'uploaded-version.json');meta=read(disc/name/'upload-request.json')
    field=read(study/'field/result.json');fp=read(study/'field/plan.json')
    if plan['sample_size']!=400 or plan['current_version']!=CURRENT or not r['passed'] or r['selected']!=name:raise ValueError('No qualifying fresh confirmation')
    if any(r['arms'][n]['games']!=400 for n in ['current',name]) or not all(r['comparisons'][name]['checks'].values()):raise ValueError('Incomplete or failed confirmation guards')
    if not field['passed'] or field['games']!=100 or field['wins']<50 or field['equipment_games']!=100 or field['version']!=version['id'] or field['candidate']!=name:raise ValueError('Field gate failed')
    if fp['confirmation_sha256']!=digest((root/'result.json').read_bytes()) or plan['discovery_sha256']!=digest((disc/'result.json').read_bytes()) or set(fp['excluded_players'])!={AARON,OPTIMIZER}:raise ValueError('Evidence provenance changed')
    p=read(root/name/'feedback/policy.ir.json');source=(study/'local/candidates'/name/'policy.bas').read_text()
    if compile_policy(p)!=source or extract(source,p)!=p or digest(source.encode())!=meta['content_hash'] or meta['player_id']!=OPTIMIZER:raise ValueError('Policy/IR/player binding mismatch')
    reconciled=study/'reconciled'/name
    final=read(reconciled/'policy.ir.json');proof=read(reconciled/'reconciliation.json')
    expected={'policy_version':version['id'],'ir_sha256':digest(final),'basic_sha256':meta['content_hash'],
        'confirmation_sha256':digest((root/'result.json').read_bytes()),'field_sha256':digest((study/'field/result.json').read_bytes()),'compile_and_reverse_extract_exact':True}
    if any(proof.get(k)!=v for k,v in expected.items()) or compile_policy(final)!=source or extract(source,final)!=final:raise ValueError('Final IR evidence reconciliation is missing or changed')
    if any(final['belief']['claims'][key]['status']!='supported' for key in ['B_candidate','B_macro','B_release_evaluation']):raise ValueError('Current measured beliefs remain unresolved')
    return plan,version,meta

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');a=parser.parse_args()
    deploy(STUDY,a.apply,readiness_fn=readiness,prior_versions=PRIORS)
