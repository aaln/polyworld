"""Explicit engine and shared-budget pin; no inherited old-game acceptance."""
from pathlib import Path
import sys
from build import ROOT, STUDY, ENGINE, VERSION, COMMIT
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'targets20260922'))
import panel
h = panel.h
h.STUDY = panel.STUDY = STUDY
h.ENGINE = ENGINE
h.GAME = 'cow_2dd9158a-e22e-4000-9b2b-b060fffa7a9a'
h.COMMIT, h.VERSION = COMMIT, VERSION
h.CYCLE = 'interactive-balance-heroes-20260922'
h.INCUMBENT = 'f3f8baab-d02a-4f7f-8fc9-e1f050f967a7'


def capture():
    with h.client() as c:
        h.live(c)
        h.freeze(STUDY / 'openapi.json', h.get(c, '/openapi.json'))


if __name__ == '__main__':
    capture()
