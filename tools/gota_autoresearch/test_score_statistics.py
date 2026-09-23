import pytest
from score_statistics import accounting, decomposition, outcomes, paired_summary, wilson


def row(xp, ticks, cell='red'):
    return dict(hero={'xp':xp},ticks=ticks,score=accounting(xp,ticks)['score'],cell=cell)


def test_score_boundary_and_fractional_minutes():
    assert accounting(1400,7*1440)['score']==0
    assert accounting(1401,7*1440)['score']==1
    assert accounting(1401,7*1440+1)['score']==0
    assert accounting(0,1)['score']==0


def test_accounting_clamp_time_and_rounding_identity():
    for a,b in [(row(0,600),row(50,600)),(row(1000,600),row(1200,1440)),
                (row(1000,600),row(0,1440)),(row(1401,10080),row(1401,10081))]:
        d=decomposition(a,b)
        assert sum(d.values())==pytest.approx(b['score']-a['score'])


def test_rare_productive_games_not_confused_with_average():
    result=outcomes([0]*9+[1000])
    assert result['mean']==100 and result['nonzero_mean']==1000
    assert result['productive_rate']==.1
    assert sum(result['mean_contribution'].values())==100


def test_pairing_keeps_covariance_and_ties():
    pairs=[{'baseline':row(x,720), 'candidate':row(x+10,720)} for x in [200,10000]]
    s=paired_summary(pairs,draws=100)
    assert s['delta95']==[10,10] and s['wins']==2
    ties=[{'baseline':row(0,720),'candidate':row(50,720)}]
    s=paired_summary(ties,draws=100)
    assert s['ties']==1 and s['exact_sign_p']==1
    assert s['mean_score_decomposition']['xp']==50
    assert s['mean_score_decomposition']['zero_floor']==-50


def test_zero_samples_and_wilson_uncertainty():
    assert paired_summary([]) is None and wilson(0,0) is None
    assert wilson(0,10)[1] > .25
    assert wilson(10,10)[0] < .75
