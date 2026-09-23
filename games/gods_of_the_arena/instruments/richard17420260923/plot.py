"""Standalone score and exact XP/time decomposition; descriptive, not causal."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[4];STUDY=ROOT.parent/'polyworld/tmp/gota-richard174-source-20260923'
p=argparse.ArgumentParser();p.add_argument('--stage',default='trial');a=p.parse_args();out=STUDY/a.stage
r=json.loads((out/'report.json').read_text());names=list(dict.fromkeys(c['name'] for c in r['cells']));cells={(c['name'],c['cell']):c for c in r['cells']}
fig,axes=plt.subplots(1,2,figsize=(13,5.6),gridspec_kw={'width_ratios':[1,1.2]});ax,bx=axes
colors=['#63758b','#267d91','#bb6b28'];width=.23
for i,n in enumerate(names):
 y=[cells[n,s]['means']['score'] for s in ['red-lead','blue-lead','red-late','blue-late']];ci=[cells[n,s]['score_ci95'] for s in ['red-lead','blue-lead','red-late','blue-late']]
 x=np.array([0,1,2,3])+(i-(len(names)-1)/2)*width
 bars=ax.bar(x,y,width,label=n,color=colors[i]);ax.errorbar(x,y,yerr=[[y[j]-ci[j][0] for j in range(4)],[ci[j][1]-y[j] for j in range(4)]],fmt='none',color='#293644',capsize=3)
 ax.bar_label(bars,fmt='%.0f',padding=3,fontsize=9)
ax.set_xticks([0,1,2,3],['Red lead','Blue lead','Red late','Blue late']);ax.set_ylabel('Mean individual points');ax.set_title('Score by context · 50 games per bar');ax.legend(fontsize=8);ax.spines[['top','right']].set_visible(False)
components=['hero_xp','creep_xp','building_xp','god_xp','time','clamp/round'];palette=['#9e4937','#438363','#a89246','#786794','#687e97','#a8a8a8']
labels=[];rows=[]
for n in names[1:]:
 for side in ['red-lead','blue-lead','red-late','blue-late']:
  old,new=cells['baseline',side]['means'],cells[n,side]['means']
  d=[new[k]-old[k] for k in components[:4]]+[-200*(new['minutes']-old['minutes'])]
  d.append(new['score']-old['score']-sum(d));rows.append(d);labels.append(side)
x=np.arange(len(rows));positive=np.zeros(len(rows));negative=np.zeros(len(rows))
for j,k in enumerate(components):
 v=np.array([row[j] for row in rows]);bottom=np.where(v>=0,positive,negative)
 bx.barh(x,v,left=bottom,label=k,color=palette[j],height=.63);positive+=np.maximum(v,0);negative+=np.minimum(v,0)
bx.set_yticks(x,labels,fontsize=9);bx.invert_yaxis();bx.axvline(0,color='#344',linewidth=.7);bx.set_xlabel('Mean point change versus same-context control');bx.set_title('XP gains less extra time cost');bx.spines[['top','right']].set_visible(False);bx.set_ylim(len(rows)-.4,-1.1);bx.legend(fontsize=8,ncols=3,loc='upper left')
fig.suptitle('GOTA guarded siege transfer · '+a.stage+' · 2026.9.22.3',fontsize=15)
fig.text(.06,.02,'Left: 95% whole-game bootstrap intervals. Right: exact mean score decomposition, including zero-clamp/rounding residual.\nFixed mixed rosters; later draft includes two fixed reference teammates. Effects are descriptive. One preselected candidate; 400 fresh held-out games.',fontsize=9,color='#52606d')
fig.tight_layout(rect=[0,.10,1,.94]);fig.savefig(out/'score-breakdown.png',dpi=170);fig.savefig(out/'score-breakdown.svg');plt.close(fig)
print(out/'score-breakdown.png')
