"""Verify and recompile this frozen fork using its native compiler snapshot."""
import hashlib,json,runpy,sys,zipfile,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((HERE/'compiler.zip').read_bytes())==manifest['compiler_zip_sha256']
assert sha((HERE/'contracts.py').read_bytes())==manifest['contracts_sha256']
for name,expected in manifest['evidence_sha256'].items():assert sha((HERE/name).read_bytes())==expected
with zipfile.ZipFile(HERE/'compiler.zip') as z:
 assert set(z.namelist())==set(manifest['compiler_files'])
 for name,expected in manifest['compiler_files'].items():assert sha(z.read(name))==expected
 workspace=tempfile.TemporaryDirectory(prefix='j268-native-ir-')
 z.extractall(workspace.name)
sys.path.insert(0,str(Path(workspace.name)/'examples/gods_of_the_arena/players/ir'))
import contracts
from policy_ir import compile_policy,extract,digest
policy=runpy.run_path(str(HERE/'policy.py'))['POLICY']
for ref in policy['belief']['claims']['Jordan268_fork_evaluation']['evidence']:
 assert sha((HERE/ref['artifact']).read_bytes())==ref['sha256']
assert policy==json.loads((HERE/'policy.ir.json').read_text())
source=compile_policy(policy)
assert source==(HERE/'policy.bas').read_text()
assert digest(policy)==manifest['policy_ir_sha256']
assert sha(source.encode())==manifest['basic_sha256']
assert extract(source,policy)==policy
print(json.dumps({'verified':True,'candidate':manifest['selected_candidate'],'basic_sha256':manifest['basic_sha256'],'uploaded_version':manifest['uploaded_version']}))
