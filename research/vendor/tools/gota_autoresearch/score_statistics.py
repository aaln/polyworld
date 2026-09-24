"""Exact score accounting and paired, context-stratified research summaries.

Whole games are the sampling units. Hero/time-window rows within a game are
descriptive, never independent replicates. No automatic policy promotion.
"""
from collections import defaultdict
from math import comb, sqrt
import random
from statistics import mean


def accounting(xp, ticks):
    """All terms use denominator 1440; no floating-point score rounding."""
    margin = 1440 * xp - 200 * ticks
    clamp = max(0, -margin)
    rounding = max(0, margin) % 1440
    score = (margin + clamp - rounding) // 1440
    return dict(xp=xp, ticks=ticks, score=score, margin_numerator=margin,
                clamp_numerator=clamp, rounding_numerator=rounding)


def decomposition(before, after):
    a, b = [accounting(r['hero']['xp'], r['ticks']) for r in (before, after)]
    assert a['score'] == before['score'] and b['score'] == after['score']
    terms = dict(xp=1440*(b['xp']-a['xp']), elapsed_time=-200*(b['ticks']-a['ticks']),
                 zero_floor=b['clamp_numerator']-a['clamp_numerator'],
                 integer_rounding=a['rounding_numerator']-b['rounding_numerator'])
    assert sum(terms.values()) == 1440*(b['score']-a['score'])
    return {k: v/1440 for k,v in terms.items()}


def wilson(successes, total, z=1.959963984540054):
    if not total: return None
    p = successes / total
    d = 1 + z*z/total
    c = (p + z*z/(2*total)) / d
    h = z*sqrt(p*(1-p)/total + z*z/(4*total*total))/d
    return [max(0,c-h), min(1,c+h)]


def outcomes(scores):
    n = len(scores)
    positive = [x for x in scores if x > 0]
    productive = [x for x in scores if x >= 500]
    low = [x for x in scores if 0 < x < 500]
    out = dict(n=n, mean=mean(scores), nonzero_mean=mean(positive) if positive else None,
               nonzero_rate=len(positive)/n, productive_mean=mean(productive) if productive else None,
               productive_rate=len(productive)/n, zero_games=n-len(positive),
               productive_games=len(productive),
               nonzero_wilson95=wilson(len(positive),n), productive_wilson95=wilson(len(productive),n))
    # Exact mixture: zeros + small-positive outcomes + productive outcomes.
    out['mean_contribution'] = {'small_positive':sum(low)/n, 'productive':sum(productive)/n}
    assert abs(sum(out['mean_contribution'].values()) - out['mean']) < 1e-9
    return out


def paired_summary(rows, draws=10000, seed=9236102):
    """Fixed context mix; resample matched episode pairs within each context."""
    if not rows: return None
    groups = defaultdict(list)
    for r in rows: groups[r['baseline']['cell']].append(r)
    before, after = [[r[k]['score'] for r in rows] for k in ('baseline','candidate')]
    deltas = [b-a for a,b in zip(before,after)]
    rng = random.Random(seed)
    estimates = []
    for _ in range(draws):
        total = 0
        for group in groups.values():
            total += sum((p['candidate']['score']-p['baseline']['score'])
                         for p in rng.choices(group,k=len(group)))
        estimates.append(total / len(rows))
    estimates.sort()
    better, worse = sum(x>0 for x in deltas), sum(x<0 for x in deltas)
    discordant = better+worse
    # Diagnostic sign test, excludes ties, not an extra promotion gate.
    sign_p = min(1,2*sum(comb(discordant,k) for k in range(min(better,worse)+1))/2**discordant) if discordant else 1
    terms = [decomposition(r['baseline'],r['candidate']) for r in rows]
    return dict(n=len(rows), baseline=outcomes(before), candidate=outcomes(after),
                mean_delta=mean(deltas), delta95=[estimates[int(draws*.025)],estimates[int(draws*.975)-1]],
                wins=better, ties=len(rows)-discordant, losses=worse, exact_sign_p=sign_p,
                rescued_nonzero=sum(a==0 and b>0 for a,b in zip(before,after)),
                lost_nonzero=sum(a>0 and b==0 for a,b in zip(before,after)),
                mean_score_decomposition={k:mean(t[k] for t in terms) for k in terms[0]},
                uncertainty='Paired whole-game percentile bootstrap, stratified by frozen side/seat. Conditional means use different outcome-selected subsets. Hero/context slices descriptive; no multiplicity-adjusted efficacy claim.')
