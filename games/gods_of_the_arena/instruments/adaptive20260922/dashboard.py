"""Read-only local progress view over preserved study files; no credentials."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

STUDY = Path(__file__).resolve().parents[5] / 'polyworld/tmp/gota-adaptive-score-20260922'
PAGE = '''<!doctype html><meta charset="utf-8"><title>GOTA individual score comparison</title>
<style>body{font:16px system-ui;margin:40px;max-width:1000px;background:#f6f7fb;color:#15243b}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #ddd}h1{font-size:26px}.note{color:#526277}</style>
<h1>GOTA — adaptive score comparison</h1><p class="note">2026.9.22.3 · Fresh controls in both colors · XP score is primary</p>
<div id="view">Loading…</div><p class="note">Completed games become evidence after source, runtime, replay and score checks. Partial scores are provisional.</p>
<script>async function update(){let r=await fetch('/data');let rows=await r.json();let s='<table><tr><th>Policy</th><th>Color</th><th>Games complete</th><th>Audited</th><th>Mean score</th><th>Invalid</th></tr>';for(let x of rows)s+=`<tr><td>${x.name}</td><td>${x.side?'Blue':'Red'}</td><td>${x.done}/${x.total}</td><td>${x.audited}/${x.total}</td><td>${x.score===null?'—':x.score.toFixed(1)}</td><td>${x.invalid}</td></tr>`;document.getElementById('view').innerHTML=s+'</table>'}update();setInterval(update,5000)</script>'''


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def data():
    result = []
    followup=STUDY.with_name('gota-class-score-20260922')
    study=followup if (followup/'screen/plan.json').exists() else STUDY
    stage='confirmation' if (study/'confirmation/plan.json').exists() else 'screen'
    finish=STUDY.with_name('gota-finish-score-20260922')
    if (finish/'trial/plan.json').exists():study,stage=finish,'trial'
    refresh=STUDY.with_name('gota-finish-refresh-20260922')
    if (refresh/'refresh/plan.json').exists():study,stage=refresh,'refresh'
    elixir=STUDY.with_name('gota-combat-elixir-20260923')
    if (elixir/'trial/plan.json').exists():study,stage=elixir,'trial'
    plan=read(study/stage/'plan.json')
    for arm in plan['arms']:
        name,side=arm['name'],arm['side']
        p=study/stage/name/str(side)
        eps=read(p/'episodes.json') or []
        rows=[read(q) for q in (p/'artifacts').glob('*/result.json')]
        result.append({'name':study.name.replace('gota-','')+' / '+stage+' / '+name,'side':side,'total':arm['games'],
            'done':sum(e['status'] in ('completed','failed','cancelled','error') for e in eps),
            'audited':len(rows),'invalid':sum(not r['valid'] for r in rows),
            'score':sum(r.get('score',0) for r in rows)/len(rows) if rows else None})
    return result


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(data()).encode() if self.path == '/data' else PAGE.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json' if self.path == '/data' else 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8853), Handler).serve_forever()
