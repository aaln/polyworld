from datetime import datetime,timezone
from pathlib import Path
from coached_candidates import STUDY, VARIANTS, make
from policy_ir import HERE,bundle,digest,read,write
from release_workspace import RUN,SOURCE,VERSION,verify
from rush_local import run


def prepare(study=STUDY, variants=VARIANTS, factory=make, seed=742000):
    verify();root=study/'local';root.mkdir(parents=True,exist_ok=True)
    if (root/'plan.json').exists():return read(root/'plan.json'),root
    sources={'current':str(HERE/'win_bounded_0916.evaluated.bas')}
    for name in variants:
        bundle(factory(name),root/'candidates'/name);sources[name]=str(root/'candidates'/name/'policy.bas')
    write(root/'config.json',read(RUN/'local/config.json'))
    paths=[RUN/'r3/build/episode',RUN/'r3/build/audit',root/'config.json',RUN/'local/default.bas']
    paths += [HERE/n for n in ['coached_contract.py','coached_candidates.py','coached_combat.py','coached_local.py','rush_local.py','binding.py','policy_ir.py']]
    plan={'created_at':datetime.now(timezone.utc).isoformat(),'source':SOURCE,'version':VERSION,'variants':variants,
          'sources':sources,'source_sha256':{n:digest(Path(p).read_bytes()) for n,p in sources.items()},
          'input_sha256':{str(p):digest(p.read_bytes()) for p in paths},
          'cases':[{'seed':seed+i,'color':i%2,'opponent':'default' if i%4<2 else 'current'} for i in range(40)],
          'rule':'Combinedcoachingchanges;200freshlocalgames/fullaudits. Fourvariants plusunchangedbaseline; fivecopies/team. Samequalification/ranking as precedingrush:>=18/20vsdefault,>=10/20vsbounded,allgear/VMvalid. Top2enter exactJordan80each; bettercandidate needs mixedroster andfieldguardrails beforedeployment. Fixedlineups directional, no broadstatisticalclaim.',
          'capture_manifest_sha256':digest((STUDY/'capture-manifest.json').read_bytes())}
    write(root/'plan.json',plan);return plan,root


if __name__=='__main__':
    plan,root=prepare();run(plan,root)
