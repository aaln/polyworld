"""Read-only local progress view over preserved study files; no credentials."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

STUDY = Path(__file__).resolve().parents[5] / 'polyworld/tmp/gota-score-20260922'
PAGE = '''<!doctype html><meta charset="utf-8"><title>GOTA individual score comparison</title>
<style>body{font:16px system-ui;margin:40px;max-width:1000px;background:#f6f7fb;color:#15243b}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #ddd}h1{font-size:26px}.note{color:#526277}</style>
<h1>GOTA — XP opportunity policy comparison</h1><p class="note">2026.9.22.3 · 40 games per source and color · XP score is primary</p>
<div id="view">Loading…</div><p class="note">Completed games become evidence after source, runtime, replay and score checks. Partial scores are provisional.</p>
<script>async function update(){let r=await fetch('/data');let rows=await r.json();let s='<table><tr><th>Policy</th><th>Color</th><th>Games complete</th><th>Audited</th><th>Mean score</th><th>Invalid</th></tr>';for(let x of rows)s+=`<tr><td>${x.name}</td><td>${x.side?'Blue':'Red'}</td><td>${x.done}/40</td><td>${x.audited}/40</td><td>${x.score===null?'—':x.score.toFixed(1)}</td><td>${x.invalid}</td></tr>`;document.getElementById('view').innerHTML=s+'</table>'}update();setInterval(update,5000)</script>'''


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def data():
    result = []
    for name in ('baseline', 'candidate'):
        for side in (0, 1):
            p = STUDY / 'hosted' / name / str(side)
            eps = read(p / 'episodes.json') or []
            rows = [read(q) for q in (p / 'artifacts').glob('*/result.json')]
            result.append({'name': name, 'side': side,
                'done': sum(e['status'] in ('completed', 'failed', 'cancelled', 'error') for e in eps),
                'audited': len(rows), 'invalid': sum(not r['valid'] for r in rows),
                'score': sum(r.get('score', 0) for r in rows) / len(rows) if rows else None})
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
    ThreadingHTTPServer(('127.0.0.1', 8852), Handler).serve_forever()
