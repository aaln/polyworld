"""Versioned active-defense scope for constant-work dense recovery."""
from dataclasses import replace

def guarded_dense(parent):
    old='  if bestId <> 0 and selfClass <> param_plain_class then'
    assert parent.template.count(old)==1
    return replace(parent,template=parent.template.replace(old,'  if defActive and bestId <> 0 and selfClass <> param_plain_class then',1),
        meaning=parent.meaning+' Superseding dense eligibility: require current defActive from '
        'this decision\'s observer. When defense is inactive, keep the original attack fallback '
        'even after a new hit; no dense movement occurs. This preserves ordinary-push commands '
        'before defense begins. Inside active defense retain the same observed-hit, consecutive '
        'tick, class, terrain and failed-movement guards. Sparse controller unchanged. Scope '
        'does not establish that recall will fire or that defense recovery improves fort wins.')
