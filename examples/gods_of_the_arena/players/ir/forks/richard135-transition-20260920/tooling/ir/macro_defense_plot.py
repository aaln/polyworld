"""Plot decoded full-replay ground truth alongside reconstructed owned decisions."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import numpy as np


def main(folder, output):
    frames={r['tick']:r for l in (folder/'decoded.jsonl').open()
            if (r:=json.loads(l)).get('type')=='frame'}
    decisions={(r['tick'],r['slot']):r for l in (folder/'decisions-team-0.jsonl').open()
               if (r:=json.loads(l)).get('type')=='decision'}
    ticks=sorted(t for t in frames if t%120==0)
    states=np.zeros((5,len(ticks)),dtype=int)
    for j,t in enumerate(ticks):
        for slot in range(5):
            if frames[t]['heroes'][slot]['hp']<=0:states[slot,j]=0
            elif (r:=decisions.get((t,slot))) is None:states[slot,j]=4
            elif not r['memory']['defActive']:states[slot,j]=1
            elif r['memory']['bestId']:states[slot,j]=2
            else:states[slot,j]=3
    colors=['#d9dce3','#3f927e','#dc983c','#ad4753','#9999bb']
    fig,(ax,ay)=plt.subplots(2,1,figsize=(13,6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    ax.imshow(states,aspect='auto',interpolation='nearest',origin='upper',
              extent=[ticks[0]-60,ticks[-1]+60,4.5,-.5],
              cmap=ListedColormap(colors),norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5,4.5],5))
    ax.set_yticks(range(5),['Death Knight','Crossbowman','Lich','Warlock','Berserker'])
    ax.set_title('Richard v78 league loss: four heroes repeatedly defend without a target',loc='left',pad=36)
    ax.legend(handles=[Patch(color=c,label=l) for c,l in zip(colors[:4],['Dead','Ordinary lane/combat policy','Defense with target','Defense without target'])],
              ncol=4,loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,fontsize=9)
    for team,color,label in [(0,'#ad4753','Our red towers'),(1,'#417bb7',"Richard’s blue towers")]:
        counts=[sum(b['kind']=='TowerBuilding' and b['team']==team and b['hp']>0 for b in frames[t]['buildings']) for t in ticks]
        ay.step(ticks,counts,where='mid',color=color,label=label,linewidth=2)
    for a in (ax,ay):
        a.axvline(8750,color='#292f3b',linestyle='--',linewidth=1)
        a.spines[['top','right']].set_visible(False)
    ay.set_ylabel('Standing towers');ay.set_xlabel('Replay tick (24 ticks per second)')
    ay.legend(frameon=False,loc='lower left');ay.set_ylim(0,12)
    ay.grid(axis='y',alpha=.2)
    fig.text(.01,.01,'Five-second snapshots. “Without target” is reconstructed policy state, not proof of a collision or an exact measure of idle time.',fontsize=9,color='#555')
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(output,dpi=160);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();main(a.folder,a.output)
