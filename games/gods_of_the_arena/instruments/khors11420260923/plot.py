"""Export descriptive score-tail and hero-class figures; no causal estimates."""
from pathlib import Path
from collections import defaultdict
import json,statistics,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'docs/opponents/khors-v114/score-audit-20260923';rows=json.loads((OUT/'evidence/actor-rows.json').read_text());own=[r for r in rows if r['policy']!='khors'];rival=[r for r in rows if r['policy']=='khors']
fig,(ax,bx)=plt.subplots(1,2,figsize=(13,5.9),gridspec_kw={'width_ratios':[.8,1.45]})
colors=['#327b93','#a85c31']
for i,(label,rs) in enumerate([('Ours (75)',own),('khors (39)',rival)]):
    vals=[100*sum(r['score']==0 for r in rs)/len(rs),100*sum(r['score']<500 for r in rs)/len(rs)]
    bars=ax.bar([-.17+i*.34,.83+i*.34],vals,width=.32,label=label,color=colors[i]);ax.bar_label(bars,fmt='%.1f%%',padding=4,fontsize=9)
ax.set_xticks([0,1],['Zero points','Below 500']);ax.set_ylim(0,38);ax.set_ylabel('Share of appearances (%)');ax.set_title('The low tail is similar overall');ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.10));ax.spines[['top','right']].set_visible(False)
classes=['Crossbowman','Ranger','Arcanist','Lich','DruidWarden','DeathKnight','Warlock','DemonHunter','VanguardKnight','Berserker']
labels=[]
for i,cl in enumerate(classes):
    rs=[r for r in own if r['class']==cl];labels.append(cl.replace('Warden','').replace('Knight',' Knight')+f'  ({sum(r["score"]==0 for r in rs)}/{len(rs)} zero)')
    value=statistics.mean(r['score'] for r in rs);bx.barh(i,value,color=colors[0]);bx.text(value+40,i,f'{value:,.0f}',va='center',fontsize=9)
bx.set_yticks(range(len(classes)),labels);bx.invert_yaxis();bx.set_xlim(0,3800);bx.set_xlabel('Our mean individual score');bx.set_title('Our fallback heroes concentrate the zeroes');bx.spines[['top','right']].set_visible(False)
fig.suptitle('Khors v114 audit · 72 league games · current replay58',fontsize=15)
fig.text(.04,.018,'Descriptive, not randomized: 75 own and 39 khors appearances share games. 63/72 games have other-player VM failures.\nDraft availability and rosters differ; small hero-class samples. All subject VMs clean.',fontsize=9,color='#56616f')
fig.tight_layout(rect=[0,.10,1,.93]);fig.savefig(OUT/'score-tail.png',dpi=170);fig.savefig(OUT/'score-tail.svg');plt.close(fig)
p=OUT/'score-tail.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='package-manifest.json' and '__pycache__' not in p.parts}
(OUT/'package-manifest.json').write_text(json.dumps({'schema':'gota-evidence-bundle/1','files':files},indent=2)+'\n')
