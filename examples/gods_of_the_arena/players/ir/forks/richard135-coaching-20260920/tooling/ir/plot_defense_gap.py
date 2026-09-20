"""Plot the replay-confirmed decision dead zone; no inferred enemy positions."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from jordan_root import STUDY

def main():
    frame=next(r for l in (STUDY/'replay.jsonl').open() if (r:=json.loads(l))['type']=='frame' and r['tick']==16440)
    god=next(b for b in frame['buildings'] if b['id']==2)
    fig,ax=plt.subplots(figsize=(7,6),layout='constrained')
    ax.set_facecolor('#f4f7fb')
    ax.add_patch(Circle((6,101),10,fill=False,color='#2672c7',lw=2,label='Old interception: 10 tiles from Arcanist'))
    ax.add_patch(Circle(god['position'],18,fill=False,color='#29915d',lw=2,ls='--',label='Candidate: 18 tiles from protected god'))
    ax.scatter(*god['position'],marker='*',s=280,color='#286840',label='Own god: 85 HP')
    for h in frame['heroes'][5:]:
        ax.scatter(*h['position'],s=70,color='#2672c7')
    enemy=next(o for o in frame['heroes'][7]['visible_post_tick'] if o['id']==103)
    ax.scatter(*enemy['position'],marker='s',s=100,color='#c53535',label='Visible Warlock')
    ax.annotate('Four heroes reject\nthis visible target',enemy['position'],xytext=(22,91),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.annotate('Repeated rally (6,101)',(6,101),xytext=(-3,113),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.set(xlim=(-7,34),ylim=(120,78),xlabel='Map x (tiles)',ylabel='Map y (tiles)',title='The target filter leaves an uncovered approach\nTick 16,440: 73 ticks before the god falls')
    ax.set_aspect('equal');ax.legend(loc='upper right',fontsize=8)
    fig.savefig(STUDY/'defense-gap.png',dpi=160)
    plt.close(fig)
if __name__=='__main__':main()
