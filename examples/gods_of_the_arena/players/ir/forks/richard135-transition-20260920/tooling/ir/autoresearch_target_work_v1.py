"""Equivalent omission of the target-validation scan when no target exists."""
from dataclasses import replace


def target_work(parent):
    old = 'while macroIndex < objectCount()'
    assert parent.template.count(old) == 2
    return replace(parent, template=parent.template.replace(old, 'while bestId <> 0 and macroIndex < objectCount()'),
        meaning=parent.meaning + ' The pursuit-validation scan stops when bestId '
        'is zero: object IDs are positive, so zero cannot match. The original '
        'scan can only clear an existing bestId, never create one. This retains '
        'target/action semantics while avoiding pointless full scans. Changed '
        'macroIndex scratch is reinitialized before each scan and is not a belief.')
