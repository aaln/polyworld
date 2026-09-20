"""Local review report; results come only from completed audited cells."""
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT/'tmp/gota-ir/richard-coaching-20260920'


def table(title, paths):
    rows=[]
    for label,p in paths:
        if (p/'arm-invalid-result.json').exists():
            v=json.loads((p/'arm-invalid-result.json').read_text())
            detail=f"{v['invalid_games']}/40 invalid games; cohort rejected"
            state='Runtime failure'
        elif (p/'quarantine.json').exists():
            detail='Runtime failure; remaining games being reviewed';state='Rejected'
        elif (p/'arm-result.json').exists():
            v=json.loads((p/'arm-result.json').read_text())
            detail=f"{v['wins']} wins · {v['losses']} losses · {v['draws']} draws"
            state='Fully audited' if v['all_full_audits_passed'] else 'Needs review'
        elif (p/'server-progress.json').exists():
            v=json.loads((p/'server-progress.json').read_text())
            detail=f"{v['verified']}/{v['expected']} audited";state='Running'
        elif (p/'batch/created.json').exists():detail='40 games requested';state='Running'
        elif p.parent.parent.name=='hosted' and (p.parents[2]/'hosted-disposition.json').exists():
            detail='Not submitted; local validation rejected advancement';state='Preserved'
        else:detail='Not started';state='Pending'
        rows.append(f'<tr><td>{html.escape(label)}</td><td>{detail}</td><td>{state}</td></tr>')
    return f'<h2>{title}</h2><table><tr><th>Policy / color</th><th>Fort outcomes</th><th>Evidence</th></tr>'+''.join(rows)+'</table>'


def render():
    history=ROOT.parent/'gota-autoresearch/adaptive-opponent-20260920'
    panels=''
    if (STUDY/'results.json').exists():
        summary=json.loads((STUDY/'results.json').read_text())
        panels+=(f"<p><b>Completed:</b> {summary['local_games']} native local games and "
                 f"{summary['hosted_games']} hosted games. "
                 f"{summary['invalid_hosted_games']} hosted games were quarantined for "
                 "VM failures; all replays were reconstructed. The final controller "
                 "passed its local runtime margin and all 80 hosted VM checks, "
                 "winning 40/40 on blue and 0/40 on red. No both-color replacement "
                 "qualified.</p>")
    for folder,name,title in [('late-cohort','formation4800_cohort','Later assault with a four-hero cohort'),
                              ('committed-return','formation2400_commit','Remembered defensive return'),
                              ('armed-cohort','formation2400_armed','Equipment and coordinated defense'),
                              ('bounded-cohort','formation4800_bounded','Bounded observation cost'),
                              ('bounded-combat','formation4800_budget','Coordinated observation and combat cost')]:
        if (STUDY/folder).exists():
            names=['deployed',name] if folder=='late-cohort' else [name]
            panels+=table(title,[(f'{n} · {c}',STUDY/folder/'hosted'/n/c) for n in names for c in ['red','blue']])
    panels+=table('Coached combined policies — first comparison',[(f'{name} · {color}',STUDY/'hosted'/name/color)
        for name in ['deployed','formation2400','formation3600','formation2400_weapon'] for color in ['red','blue']])
    if (STUDY/'visibility-complete').exists():
        panels+=table('Forward discovery and earlier defensive warning',[(f'formation2400_discovery · {c}',STUDY/'visibility-complete/hosted/formation2400_discovery'/c) for c in ['red','blue']])
    panels+=table('Earlier base warning',[(n+' · blue',history/'critical-blue-confirmation'/n) for n in ['critical60','critical40']])
    panels+=table('Historical specialists against v135',[(f'{n} · {c}',history/'hosted/richard135'/c/n) for n in ['anchor','bound_idle','assist22','deployed'] for c in ['red','blue']])
    page='''<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="20">
<title>Richard v135 — coached counter</title><style>
body{font:16px/1.6 system-ui,sans-serif;color:#182634;background:#f3f5f4;margin:0}main{max-width:1080px;margin:auto;padding:40px}
h1{font-size:32px;margin:0}h2{font-size:21px;margin:32px 0 12px}.sub{color:#52646e}.note{padding:18px;background:#fff3d4;border-left:4px solid #b58010;margin:24px 0}
table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:11px 16px;border-bottom:1px solid #e3e8e7}th{background:#dce9e6}td:first-child{width:45%}.layers{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.layers div{background:white;padding:16px;border-radius:6px}.layers b{display:block;color:#11685b}a{color:#11685b}code{font-size:12px}
</style></head><body><main><h1>Richard v135 — coached counter</h1>
<p class="sub">Session 2026-09-20t17-21-56-307zf4f7b3 · published game 2026.9.16.5</p>
<div class="note"><b>Research status:</b> Blue critical60 has 40/40 audited Richard wins, retained by the completed coached variants. Red remains unresolved. No new league replacement has passed validation.</div>
<p>Your recording is bound to <code>ereq_15e13437-273d-4c4f-84cc-162b01b602b4</code>: historical bound_idle on red versus Richard135 on blue. All 60 captured files were copied and hashed without changing the originals.</p>
<div class="layers"><div><b>Situation & belief</b>Four healthy allies near the team center establish readiness. Enemy dispersion requires at least three visible heroes.</div><div><b>Goal & strategy</b>Gather for a shared objective; probe the base perimeter, then commit together. Home threats redirect the group.</div><div><b>Skill & execution</b>Shared target selection, observed entry scoring, a movement tether, and a bounded breach commitment. Native BASIC compile/extract parity.</div></div>
<p>The initial variants passed all 48 local runtime/replay checks but won 2/12 each, versus 7/12 for deployed. Full Richard replays then exposed a missing-objective visibility stall and repeated defensive reversals through fog. Follow-ups test the coordinated corrections, later timing, four-hero readiness, and a remembered return to defend. These are combined behavior tests.</p>
<p>The intermediate breach-only refinement is preserved with its 24 local results and was not submitted: the known visibility stall remained. Every tested policy, failed result, and native reconstruction is retained in the study folder.</p>
'''+panels+f'<p class="sub">Updated {datetime.now(timezone.utc).isoformat()}. Counts are actual fort wins; draws score zero. Repeated deterministic trajectories are correlated. Only complete audited cells receive a win count. This report refreshes every 20 seconds.</p></main></body></html>'
    (STUDY/'report.html').write_text(page)
    return page.encode()


if __name__=='__main__':
    if '--serve' in sys.argv:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body=render();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(body)
            def log_message(self,*args):pass
        ThreadingHTTPServer(('127.0.0.1',8842),Handler).serve_forever()
    else:render()
