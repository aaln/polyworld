"""Verify published Python predictions and primary-IR belief compatibility."""
import copy,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
LOCAL=ROOT/'examples/gods_of_the_arena/players/ir'
sys.path.insert(0,str(LOCAL));import opponent_ir
OUT=ROOT/'docs/opponents/jordan-v268'
model=opponent_ir.load(LOCAL/'opponents/jordan_v268.py');prior=opponent_ir.load(LOCAL/'opponents/population_20260919.py')
with gzip.open(OUT/'heldout-predictions.jsonl.gz','rt') as f:predictions={r['observation']:r for r in map(json.loads,f)}
matched=0
with gzip.open(OUT/'observations.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if r['id'] not in predictions:continue
  p=opponent_ir.predict(model,r['situation'],r['affordances']);expected=predictions[r['id']]
  assert p['skill']==expected['prediction'] and p['probabilities']==expected['probabilities'];matched+=1
assert matched==len(predictions)
# Import the actual pinned primary compiler/binding, not the older working tree binding.
clean=ROOT.parent/'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0,str(clean));import policy_ir
parent=policy_ir.read(OUT/'observer-policy.ir.json');baseline=policy_ir.compile_policy(parent)
candidate=copy.deepcopy(parent);candidate['belief']['claims'].update(opponent_ir.belief_patch(model));policy_ir.validate(candidate)
assert policy_ir.compile_policy(candidate)==baseline
assert hashlib.sha256(baseline.encode()).hexdigest()=='b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'
assert tuple(opponent_ir.LAYERS)==tuple(policy_ir.LAYERS)
assert set(model)==set(parent)
assert all(set(r)=={'id','when','skill','for'} for r in model['strategy'])
# The action compiler must reject the observational model, preventing accidental use as a proxy.
try:policy_ir.compile_policy(model)
except ValueError:rejected=True
else:raise AssertionError('Observation model accepted as executable policy')
receipt={'schema':'gota-opponent-python-compatibility/1','seven_layer_layout_matches_primary':True,'strategy_rule_layout_matches_primary':True,
 'all_heldout_predictions_reproduced':matched,'belief_patch_passes_primary_validator':True,'belief_patch_preserves_exact_primary_basic':True,
 'primary_basic_sha256':hashlib.sha256(baseline.encode()).hexdigest(),'action_compiler_rejects_observation_model':rejected,
 'live_primary_policy_modified':False,'proxy_usable':False}
(OUT/'python-compatibility.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
