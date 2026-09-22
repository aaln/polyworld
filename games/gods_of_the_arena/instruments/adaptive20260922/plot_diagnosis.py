"""Read-only minute frames from exact replays; no inferred live observations."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT.parent/'polyworld/tmp/gota-adaptive-score-20260922'
plan=json.loads((RAW/'diagnosis-plan.json').read_text())
for side in (0,1):
    row=next(r for r in plan['episodes'] if r['side']==side)
    data=json.loads((RAW/'diagnosis'/row['episode']/'audit.json').read_text())
    frames=[data['frames'][min(m-1,len(data['frames'])-1)] for m in (1,4,8,12)]
    fig,axes=plt.subplots(1,4,figsize=(17,4.9),layout='constrained')
    names={side*5:'Aaron',(1-side)*5:'khors114',(1-side)*5+2:'Richard167'}
    for ax,f in zip(axes,frames):
        for kind,marker,size in [('buildings','s',13),('creeps','.',8)]:
            for team in (0,1):
                points=[p for p in f[kind] if p['team']==team]
                ax.scatter([p['x']/60000 for p in points],[p['z']/60000 for p in points],s=size,marker=marker,c=['#be4b41','#3973bc'][team],alpha=.35)
        for h in f['heroes']:
            if h['hp']<=0:continue
            slot=h['slot'];x=h['x']/60000;y=h['z']/60000
            ax.scatter(x,y,c=['#c13d37','#246dd0'][slot//5],s=48 if slot in names else 15,edgecolors='black' if slot in names else 'none')
            if slot in names:ax.annotate(names[slot]+f"\nL{h['level']} {round(100*h['hp']/h['max_hp'])}%",(x,y),xytext=(3,4),textcoords='offset points',fontsize=7)
        ax.set(xlim=(-59,59),ylim=(-59,59),title=f"{f['tick']/1440:g} min",aspect='equal',xlabel='world x / tile')
        ax.grid(alpha=.13)
    fig.suptitle(f"Aaron {'red' if side==0 else 'blue'} · {row['episode']}\nPost-tick full-truth frames; buildings=squares, creeps=dots. Not a live policy view.",fontsize=10)
    fig.savefig(RAW/f'diagnosis-side{side}.png',dpi=160)
    plt.close(fig)
