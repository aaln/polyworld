"""Versioned public selected-target guard on dense post-hit recovery geometry."""
from dataclasses import replace


def target_geometry(parent):
    old = '        if mTryX <> selfX or mTryY <> selfY then'
    assert parent.template.count(old) == 1
    check = '''        mTracked = 0
        mIndex = 0
        while mIndex < objectCount()
          if objectId(mIndex) = bestId then
            mTracked = 1
            mKind = objectKind(mIndex)
            if mKind = 2 or mKind = 3 then
              mDx = objectX(mIndex) - selfX
              mDy = objectY(mIndex) - selfY
              mD = (mTryX - selfX) * mDx + (mTryY - selfY) * mDy
              if mD > 0 then
                mTryX = selfX
                mTryY = selfY
                if param_reverse_toward = 1 then
                  if mDx > 0 then
                    mTryX = selfX - 1
                  end if
                  if mDx < 0 then
                    mTryX = selfX + 1
                  end if
                  if mDy > 0 then
                    mTryY = selfY - 1
                  end if
                  if mDy < 0 then
                    mTryY = selfY + 1
                  end if
                end if
              end if
            end if
            mIndex = objectCount()
          end if
          mIndex = mIndex + 1
        wend
        if mTracked = 0 then
          mTryX = selfX
          mTryY = selfY
        end if
'''
    return replace(parent, template=parent.template.replace(old, check+old, 1),
        parameters=parent.parameters | {'reverse_toward': (0, 0, 1)},
        meaning=parent.meaning+' Before a new dense recovery step, locate the '
        'currently selected object in the current visibility-filtered view. '
        'For a selected hero or creep, compute the dot product of the intended '
        'homeward tile step with its current self-relative position. If positive, '
        'reverse_toward0 suppresses the step and retains the original attack; '
        'reverse_toward1 instead takes a one-tile step on each nonzero axis away '
        'from that selected target. Original terrain and command-acceptance '
        'guards apply. Zero/negative dot and structures retain the homeward step. '
        'Missing selected objects suppress movement. Scratch variables reset '
        'within every eligible decision; no target is remembered through fog. '
        'No extra persistent memory, target ranking, alarm, equipment or sparse '
        'recovery changes. Selected targets need not be the incoming threat; '
        'tile geometry is not proof of displacement, safety or winning.')
