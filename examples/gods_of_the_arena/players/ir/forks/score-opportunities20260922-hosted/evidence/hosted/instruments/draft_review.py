"""Secondary draft-mix decomposition; never changes the frozen promotion rule."""
from pathlib import Path
import json
import statistics

ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-score-20260922'
OUT=STUDY/'hosted'


def main():
    report=json.loads((OUT/'report.json').read_text());assert report['complete']
    verdict=json.loads((OUT/'result.json').read_text())
    cells=[]
    for cell in verdict['cells']:
        groups=[]
        for cls in sorted({r['class'] for r in cell['rows']}):
            rows=[r for r in cell['rows'] if r['class']==cls]
            groups.append({'class':cls,'games':len(rows),**{k:statistics.mean(r[k] for r in rows) for k in ['score','xp','deaths','level','ticks']}})
        cells.append({'name':cell['name'],'side':cell['side'],'by_class':groups})
    standardized=[]
    for side in [0,1]:
        base=next(c for c in cells if c['name']=='baseline' and c['side']==side)
        candidate=next(c for c in cells if c['name']=='candidate' and c['side']==side)
        b={r['class']:r for r in base['by_class']};n={r['class']:r for r in candidate['by_class']}
        if set(b)!=set(n):
            standardized.append({'side':side,'available':False,'reason':'Class overlap incomplete'})
            continue
        weights={k:(b[k]['games']+n[k]['games'])/80 for k in b}
        before=sum(weights[k]*b[k]['score'] for k in b)
        after=sum(weights[k]*n[k]['score'] for k in n)
        standardized.append({'side':side,'available':True,'weights':weights,'baseline_score':before,'candidate_score':after,'gain_percent':(after/before-1)*100,'within_class_gain_percent':{k:(n[k]['score']/b[k]['score']-1)*100 if b[k]['score'] else None for k in b}})
    result={'cells':cells,'standardized':standardized,'scope':'Secondary descriptive standardization to each side pooled class frequency. Class choice depends on seeded draft order/availability; small conditional cells and other composition differences prevent causal attribution. This analysis does not replace the preregistered unadjusted mean-score gate.'}
    (OUT/'draft-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
