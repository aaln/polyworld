"""Full actual-draft Druid coverage; fixed teammate2 leaves support available."""
from concurrent.futures import ThreadPoolExecutor
import native,json
S=native.STUDY
cases=[(n,context,side,3,seed) for n in ['baseline','blue-druid-siege'] for context,side in [('red-druid',0),('blue-druid',1)] for seed in [923082,923083]]
plan={'cases':cases,'source_sha256':native.sha(S/'blue-druid-siege/policy.bas'),'reference_sha256':native.sha(S/'reference-defer-druid.bas'),'scope':'Extra local actual-draft Druid coverage: teammate2 uses Druid-deferred native reference; team0 remains deployed baseline. Richard174 remains opposing. Not league performance.'}
native.write(S/'druid-native-plan.json',plan)
with ThreadPoolExecutor(2) as pool:rows=list(pool.map(native.run,cases))
assert all(r['valid'] and r['hero']['class']==3 for r in rows),rows
native.write(S/'druid-native-result.json',{'passed':True,'rows':rows,'scope':plan['scope']})
print(json.dumps({'passed':True,'games':len(rows)}))
