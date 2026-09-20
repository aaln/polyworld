"""Build a self-contained schematic viewer from hash-verified diagnostics.

Usage: python replay_viewer.py OUTPUT.html DIAGNOSTIC.jsonl [...]
This renders recorded simulation coordinates, visible objects and native paths;
it does not synthesize game footage or interpolate unobserved states.
"""
import json
from pathlib import Path
import sys
from replay_review import read_tape

PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>GOTA replay diagnosis</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;background:#111720;color:#e4eaf4;font:16px system-ui;max-width:1250px;margin:auto;padding:24px}
h1{font-size:27px;margin:0 0 8px}p{color:#acb9c9;line-height:1.5}button,select{font:inherit;background:#253349;color:#fff;border:1px solid #53627a;border-radius:6px;padding:8px}
canvas{width:100%;background:#101920;border:1px solid #465365;border-radius:10px}main{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-top:18px}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}input{flex:1;min-width:220px}pre{white-space:pre-wrap;line-height:1.5;font:14px ui-monospace}strong{color:white}.note{background:#202d3e;padding:14px;border-radius:8px}@media(max-width:800px){main{display:block}}
</style><h1>Where the policy loses movement</h1>
<p>Published game 2026.9.15.3 · complete action tapes verified against every state hash.<br>
Schematic replay: real coordinates and navigation paths, rather than the native 3D renderer.</p>
<div class="controls"><select id="case"></select><button id="play">Play</button>
<select id="speed"><option value="1">1×</option><option value="0.25">¼×</option><option value="8">8×</option></select>
<button id="zoom">Show whole map</button></div>
<main><div><canvas id="map" width="800" height="720"></canvas>
<div class="controls"><input aria-label="Replay time" id="time" type="range" min="0" value="0"><span id="clock"></span></div>
<p>White ring: our hero · gold: attack target · green: engine path<br>Blue/red: teams · gray: blocked ground. Objects shown are visible to our team.</p></div>
<aside><div class="note" id="why"></div><pre id="detail"></pre><p>Controls change only this view. These are existing games, not new evaluations. The two kiting variants were not promoted.</p></aside></main>
<script>
const cases=DATA;
const notes={
'arcanist-v2':'v2, seed 721023. Watch 00:29–06:15: the hero is pinned beside its own tower while its attack targets change. The first waypoint sits inside the tower’s collision clearance.',
'crossbow-short':'Short-retreat variant, seed 721028. At 08:33.63, a ten-tick retreat starts. Watch how little the hero moves while the approaching Demon Hunter closes the gap.',
'lich-long':'Long-retreat variant, seed 721018. At 14:09.46, even a 32-tick retreat fails to create space; the hero loses health. Longer duration alone does not choose a safe route.'};
let choice=0,idx=0,playing=false,whole=false,acc=0,last=0;
const q=id=>document.getElementById(id),ctx=q('map').getContext('2d');
cases.forEach((c,i)=>q('case').add(new Option(c.name+' · '+c.header.class,i)));
function select(){choice=+q('case').value;idx=cases[choice].name==='arcanist-v2'?Math.max(0,cases[choice].frames.findIndex(f=>f.tick>=2400)):0;playing=false;q('play').textContent='Play';q('time').max=cases[choice].frames.length-1;draw()}
function draw(){const c=cases[choice],f=c.frames[idx],h=f.hero;const p=h.position;const r=whole?58:10,cx=whole?58:p[0],cy=whole?58:p[1];const sc=700/(r*2),ox=50-(cx-r)*sc,oy=10-(cy-r)*sc;
const xy=p=>[ox+p[0]*sc,oy+p[1]*sc];ctx.clearRect(0,0,800,720);
c.header.terrain.forEach((row,y)=>{[...row].forEach((ch,x)=>{if(x<cx-r-1||x>cx+r||y<cy-r-1||y>cy+r)return;ctx.fillStyle=ch==='.'?'#18322e':'#3b3d46';ctx.fillRect(ox+x*sc,oy+y*sc,sc+.4,sc+.4)})});
function line(a,b,color,width=2){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(...xy(a));ctx.lineTo(...xy(b));ctx.stroke()}
let prev=p;for(const wp of f.path){line(prev,wp,'#a5df95');prev=wp}
const target=f.objects.find(o=>o[0]===h.target);if(target)line(p,target[3],'#ffce61');
for(const o of f.objects){if(o[4]<=0)continue;const pos=xy(o[3]);let radius=({1:.65,2:.28,3:.2,4:.55}[o[1]])*sc;ctx.fillStyle=o[2]===0?'#ec827f':'#78bdff';ctx.beginPath();ctx.arc(...pos,Math.max(2,radius),0,Math.PI*2);ctx.fill();if(!whole){ctx.fillStyle='#e4eaf4';ctx.font='12px system-ui';ctx.fillText(o[0]+' '+o[4]+'hp',pos[0]+7,pos[1]-7)}}
const pos=xy(p);ctx.strokeStyle='white';ctx.lineWidth=3;ctx.beginPath();ctx.arc(...pos,Math.max(7,.4*sc),0,Math.PI*2);ctx.stroke();
q('time').value=idx;let sec=f.tick/24;q('clock').textContent=Math.floor(sec/60).toString().padStart(2,'0')+':'+(sec%60).toFixed(2).padStart(5,'0')+' · tick '+f.tick;
q('why').textContent=notes[c.name]||c.name;
q('detail').textContent=`HP             ${h.hp} / ${h.max_hp}\nMana           ${f.mana}\nLifetime XP    ${f.xp}\nBasic hits     ${h.hit_count}\nLast command   ${{1:'walk',2:'attack'}[h.action]||h.action}\nTarget         ${h.target}\nTarget distance ${h.target_distance.toFixed(2)} tiles\nPosition       ${p.map(x=>x.toFixed(3)).join(', ')}\nPath waypoint  ${f.path_index} / ${f.path_length}\nEnemies ≤6 tiles ${h.enemy_near}\nAllies ≤6 tiles  ${h.ally_near}\nTargeting us   ${h.attackers.map(a=>a.id).join(', ')||'none'}\n\nItems\n${f.inventory.filter(x=>x!=='NoItem').join('\n')}\n\nFull replay\n${c.summary.ticks} ticks, ${c.summary.hash_mismatches} hash mismatches`;
}
q('case').onchange=select;q('time').oninput=()=>{idx=+q('time').value;draw()};q('zoom').onclick=()=>{whole=!whole;q('zoom').textContent=whole?'Follow hero':'Show whole map';draw()};q('play').onclick=()=>{playing=!playing;q('play').textContent=playing?'Pause':'Play'};
function loop(now){if(playing){acc+=(now-last)/1000*(+q('speed').value)*24;const fs=cases[choice].frames;while(idx<fs.length-1&&acc>=fs[idx+1].tick-fs[idx].tick){acc-=fs[idx+1].tick-fs[idx].tick;idx++;draw()}if(idx===fs.length-1){playing=false;q('play').textContent='Play'}}else acc=0;last=now;requestAnimationFrame(loop)}select();requestAnimationFrame(loop);
</script></html>'''


def main():
    out, *paths = map(Path, sys.argv[1:])
    cases = []
    for path in paths:
        h, frames, s = read_tape(path)
        if not frames:
            raise ValueError("Viewer requires sampled frames")
        cases.append({'name': path.stem, 'header': h, 'frames': frames, 'summary': s})
    data = json.dumps(cases, separators=(',', ':')).replace('</', '<\\/')
    out.write_text(PAGE.replace('DATA', data, 1))
    print(out)


if __name__ == '__main__':
    main()
