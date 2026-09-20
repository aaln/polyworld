"""Local live report for the second coaching study."""
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import html
from pathlib import Path
import sys
import json

ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT/'tmp/gota-ir/richard-transition-20260920'


def render():
    active=STUDY/'fresh-hit' if (STUDY/'fresh-hit/plan.json').exists() else STUDY/'cadence'
    names=('coached_baseline','transition_freshhit','transition_armor_freshhit') if active.name=='fresh-hit' else ('coached_baseline','transition_cadence','transition_armor_cadence')
    cells=[]
    for name in names:
        for color in ('red','blue'):
            d=active/'hosted'/name/color
            if name=='coached_baseline':d=STUDY/'cadence/hosted'/name/color
            if (d/'arm-result.json').exists():
                v=json.loads((d/'arm-result.json').read_text())
                value=f"{v['wins']} wins · {v['losses']} losses · {v['draws']} draws";status='Fully audited'
            elif (d/'quarantine.json').exists():value='Runtime/evidence review required';status='Quarantined'
            elif (d/'server-progress.json').exists():
                v=json.loads((d/'server-progress.json').read_text());value=f"{v['verified']}/{v['expected']} audited";status='Running'
            elif (d/'batch/created.json').exists():value='40 requested';status='Running'
            else:value='Awaiting complete local gate';status='Not requested'
            cells.append(f'<tr><td>{name} · {color}</td><td>{value}</td><td>{status}</td></tr>')
    rows=[]
    banner='The coached episode is the previous formation4800_budget variant. That source scored0/40 on red and40/40 on blue. The new combined controllers require fresh evidence; no league replacement has been made.'
    if (STUDY/'results.json').exists():
        result=json.loads((STUDY/'results.json').read_text())
        passed=result['conditional_promotion']['user_conditional_promotion_gate_passed']
        banner='Complete:400hosted games and108local games, all audited. The Alex/Jordan promotion condition '+('passed; deployment status is recorded separately.' if passed else 'failed; the league policy remains unchanged.')+' Richard and color-specific results are shown below.'
    for name in names:
        rs=[json.loads(p.read_text()) for p in (active/'local'/name).glob('*/result.json')]
        valid=[r for r in rs if r['valid']]
        rows.append(f"<tr><td>{name}</td><td>{len(rs)}/12</td><td>{sum(r['win'] for r in valid)} wins; {sum(r['deaths'] for r in valid)} deaths</td><td>{len(rs)-len(valid)} invalid</td></tr>")
    promotion=''
    if (STUDY/'promotion-check/authorization-and-gate.json').exists():
        p=STUDY/'promotion-check';details=[]
        if (p/'selection.json').exists():
            selected=json.loads((p/'selection.json').read_text())['name']
            for rival in ('alex','jordan'):
                for color in ('red','blue'):
                    d=p/'hosted'/selected/rival/color
                    if (d/'arm-result.json').exists():
                        v=json.loads((d/'arm-result.json').read_text());outcome=f"{v['wins']} wins · {v['losses']} losses · {v['draws']} draws"
                    elif (d/'batch/created.json').exists():outcome='40 requested; full audit pending'
                    else:outcome='Queued'
                    details.append(f'<tr><td>{rival.title()} · {color}</td><td>{outcome}</td></tr>')
            promotion=f'<p>Selected unchanged candidate: {html.escape(selected)}.</p><table><tr><th>Opponent / color</th><th>Outcome</th></tr>'+''.join(details)+'</table>'
        else:promotion='<p>Selection waits for the complete Richard comparison. No further policy code edits are planned.</p>'
        promotion='<h2>User-authorized promotion check</h2><p>The user authorized pushing the policy if it beats Alex and Jordan, accepting unresolved Richard performance. Gate: at least30/40 wins on each color against both Alex g002:v1 and Jordan:v268, with all160games fully audited. The original Richard gate remains separately reported.</p>'+promotion
        if (p/'result.json').exists():
            passed=json.loads((p/'result.json').read_text())['user_conditional_promotion_gate_passed']
            promotion+='<p><strong>Alex/Jordan promotion gate: '+('passed' if passed else 'failed')+'.</strong></p>'
    page='''<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="20"><title>Red transition and Ranger response</title><style>
body{font:16px/1.6 system-ui;background:#f2f5f4;color:#18302b;margin:0}main{max-width:1100px;margin:auto;padding:40px}h1{font-size:32px}h2{font-size:22px;margin-top:32px}.note{background:#fff2d2;border-left:4px solid #c69526;padding:18px}table{border-collapse:collapse;background:white;width:100%}th,td{text-align:left;padding:12px;border-bottom:1px solid #dce3df}th{background:#dcebe5}a{color:#096b56}.small{font-size:14px;color:#567068}</style></head><body><main>
<h1>Red: leave defense, scout, and contest the Ranger</h1>
<p>Coaching session 2026-09-20t19-10-35-082z64deb6 · exact Richard v135</p>
<div class="note">'''+html.escape(banner)+'''</div>
<p>The exact replay confirms long remembered returns: 197 of 286 sampled emergency decisions had no fresh alarm. In 110, no enemy hero was visible. The core was still undamaged in those samples. The Ranger finished at level 10 with five equipment items; our Death Knight finished level 4 with one.</p>
<p>The new bundle couples finite defense, observed-clear release, a bounded Crossbowman scout and shared Ranger targeting even with fewer than four healthy defenders. A second version buys HP equipment earlier. All numeric thresholds are authored interpretations of the coaching.</p>
<p>The first two versions each won 5/12 locally against the baseline’s 7/12 and were preserved without upload. Exact Ranger reconstruction then found 62 of 75 late hit intervals were nine ticks; all 62 included movement within two ticks after the preceding hit. The revised focus controller adds verified-hit recovery, evaluated as part of the complete bundle. A boundary test then caught stale hit memory at focus entry; the final controller requires consecutive decisions. The intermediate cadence versions were uploaded as inert versions, but no candidate games were requested for them. All earlier local results are preserved.</p>
<p>Ranger finished with 123 attack and 330,000 range in engine units; our Crossbowman had 155 attack and 390,000 range. Damage per hit alone does not explain the loss. Baseline games are reused from their original request receipts; they are counted once.</p>
<h2>Native local comparison</h2><table><tr><th>Policy</th><th>Completed</th><th>Valid outcomes</th><th>Runtime</th></tr>'''+''.join(rows)+'''</table>
<h2>Richard v135 · fresh pinned 5v5 comparison</h2><table><tr><th>Policy / color</th><th>Fort outcomes</th><th>Validation</th></tr>'''+''.join(cells)+'''</table>
<p>Original Richard target gate: at least30 wins from40 on each color, plus eight combined wins over the contemporaneous coached baseline. This criterion is reported independently of the later user-authorized Alex/Jordan promotion check. Invalid games are excluded; draws score zero. Generated seeds differ between arms, and repeated trajectories are correlated.</p>
<p><a href="https://softmax.com/observatory/v2?tab=experience-requests&amp;detail=episode-request:ereq_b3f6d7ee-c7da-41b3-8ecc-70b9a790208a">Coached episode</a></p>
'''+promotion+f'<p class="small">Updated {datetime.now(timezone.utc).isoformat()} · refreshes every 20 seconds.</p></main></body></html>'
    (STUDY/'report.html').write_text(page);return page.encode()


if __name__=='__main__':
    if '--serve' in sys.argv:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                data=render();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(data)
            def log_message(self,*args):pass
        ThreadingHTTPServer(('127.0.0.1',8843),Handler).serve_forever()
    else:render()
