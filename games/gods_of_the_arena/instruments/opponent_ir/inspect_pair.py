"""Render discovery-only visible replay frames before counting opponent motifs."""
import gzip
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[4]
fig,axes=plt.subplots(2,5,figsize=(17,7.5))
for row,slug in enumerate(['richard-v135','alex-g002-v1']):
    study=ROOT/'tmp/gota-ir'/('opponent-'+slug+'-20260920')
    plan=json.loads((study/'study-plan.json').read_text())
    meta=next(r for r in plan['episodes'] if r['split']=='train')
    folder=study/'artifacts'/meta['id']
    ticks=json.loads((folder/'observer-validation.json').read_text())['ticks']
    selected=[max(1,int(ticks*f)) for f in (.15,.35,.55,.75,.95)]
    frames={}
    with gzip.open(folder/'observer.jsonl.gz','rt') as stream:
        for line in stream:
            frame=json.loads(line)
            if frame['type']=='header':terrain=frame['terrain']
            if frame.get('tick') in selected:frames[frame['tick']]=frame
    for col,tick in enumerate(selected):
        ax=axes[row,col];f=frames[tick];objects={o[0]:o for o in f['objects']};team=meta['observer_slot']//5
        ax.imshow([[1 if c=='#' else 0 for c in line] for line in terrain],origin='lower',cmap='Greys',alpha=.17,extent=(0,116,0,116))
        for o in objects.values():
            if o[6]<=0:continue
            color='#277da8' if o[2]==team else '#d17b21'
            if o[1]==2:
                ax.scatter(o[4],o[5],color=color,s=30,zorder=4)
                ax.text(o[4]+1,o[5]+1,str(o[0]),fontsize=6,color=color)
                if o[8] in objects and o[2]!=team:
                    t=objects[o[8]];ax.annotate('',(t[4],t[5]),(o[4],o[5]),arrowprops={'arrowstyle':'->','lw':.7,'color':color},zorder=3)
            elif o[1] in (1,4,5):
                ax.scatter(o[4],o[5],color=color,marker='*' if o[1]==1 else 's',s=65 if o[1]==1 else 12,alpha=.7)
        ax.set(xlim=(0,116),ylim=(116,0));ax.set_aspect('equal');ax.set_title(f'{slug} · t={tick}',fontsize=10)
        if col==0:ax.set_ylabel('Own '+('red' if team==0 else 'blue')+' · observer '+str(meta['observer_slot']))
        if not f['available']:ax.text(58,58,'Observer unavailable',ha='center',fontsize=9)
fig.suptitle('Visible replay frames · discovery games only',x=.04,ha='left',fontsize=17)
fig.text(.04,.025,'Blue: our team. Orange: opponent. Arrows: visible opponent target. Hidden objects are omitted; a missing hero is not assumed dead.',fontsize=10)
fig.tight_layout(rect=(0,.06,1,.94))
out=ROOT/'tmp/gota-ir/opponent-pair-20260920/discovery-frames.png';fig.savefig(out,dpi=150)
print(out)
