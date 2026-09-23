"""Exact own-source replay for four declared contrasting low-score cases."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-khors114-audit-20260923';PLAN=json.loads((RAW/'own-source-plan.json').read_text())
assert hashlib.sha256(Path(PLAN['source']).read_bytes()).hexdigest()==PLAN['source_sha256']
def one(case):
    out=RAW/'own-source-audits'/case['episode'];out.mkdir(parents=True,exist_ok=True)
    if (out/'audit.json').exists():return json.loads((out/'audit.json').read_text())
    p=subprocess.run([str(RAW/'own-source-probe'),'--replay',str(RAW/'league-artifacts'/case['episode']/'replay.bin')],env=dict(os.environ,AUDIT_SLOTS=str(case['slot']),AUDIT_POLICY=PLAN['source'],AUDIT_KIND='ours'),capture_output=True,text=True,timeout=900)
    (out/'stdout.log').write_text(p.stdout);(out/'stderr.log').write_text(p.stderr);assert p.returncode==0,p.stderr[-1500:]
    d=json.loads(p.stdout.splitlines()[-1]);assert d['all_state_hashes_equal'] and d['all_actions_consumed'];(out/'audit.json').write_text(json.dumps(d,indent=2)+'\n');return d
with ThreadPoolExecutor(2) as pool:rows=list(pool.map(one,PLAN['cases']))
assert all(r['all_state_hashes_equal'] and r['all_actions_consumed'] for r in rows)
(RAW/'own-source-summary.json').write_text(json.dumps({'plan':PLAN,'rows':rows,'selected_kind_warning':'bestKind persists when bestId=0; kind counts are diagnostic VM values, not a valid target histogram. Use no-selected-target and submitted commands separately.'},indent=2)+'\n')
print(json.dumps({'verified_games':len(rows),'matched_commands':sum(r['commands_matched'] for r in rows)}))
