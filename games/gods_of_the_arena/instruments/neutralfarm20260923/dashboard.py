"""Read-only release62 experiment progress from the streaming harvester."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

RAW = Path(__file__).resolve().parents[5]/'polyworld/tmp/gota-lane-neutral62-20260923'
PAGE = '''<!doctype html><meta charset="utf-8"><title>GotA lane and camp study</title>
<style>body{font:17px system-ui;max-width:1000px;margin:40px;background:#f5f7fa;color:#172637}td,th{padding:12px;border-bottom:1px solid #bbb;text-align:left}table{border-collapse:collapse;width:100%}</style>
<h1>Lane selection and neutral farming</h1><p>Release62 · Matched responsive games · Individual score</p>
<div id="data"></div><p>Partial results are provisional. The original10-game Jordan411 batch failed compilation and is preserved separately.</p>
<script>async function refresh(){let rows=await(await fetch('/data')).json();let t='<table><tr><th>Arm</th><th>Audited games</th><th>Mean score</th><th>State</th></tr>';for(let r of rows)t+=`<tr><td>${r.arm}</td><td>${r.n}/40</td><td>${r.mean===null?'—':r.mean.toFixed(1)}</td><td>${r.status}</td></tr>`;document.getElementById('data').innerHTML=t+'</table>';}refresh();setInterval(refresh,5000);</script>'''


def read(path, default):
    try:return json.loads(path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):return default


def data():
    base = [r for p in (RAW/'hosted-f5').glob('*/result.json') for r in read(p,[])]
    rows = [('baseline',base,'complete' if len(base)==40 else 'collecting')]
    for arm in ['lane-only','lane-neutral']:
        d=read(RAW/'counterfactual'/arm/'paired-results.json',{})
        status=read(RAW/'counterfactual'/arm/'status.json',{}).get('status','not started')
        rows.append((arm,[r['candidate'] for r in d.get('pairs',[])],status))
    return [dict(arm=arm,n=len(v),mean=sum(r['score'] for r in v)/len(v) if v else None,status=status) for arm,v,status in rows]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body=json.dumps(data()).encode() if self.path=='/data' else PAGE.encode()
        self.send_response(200);self.send_header('Content-Type','application/json' if self.path=='/data' else 'text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass


if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8796),Handler).serve_forever()
