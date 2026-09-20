"""Derive fixture hero IDs from the pinned engine, never from team-slot numbers."""
import re
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[2]/'content.nim'
_source = CONTENT.read_text()
_enum = re.search(r'HeroClass\* = enum\n(.*?)\n  HeroAttackStyle', _source, re.S).group(1)
NAMES = re.findall(r'^\s*(\w+),?\s*$', _enum, re.M)
CLASS_ID = {name: i for i, name in enumerate(NAMES)}
TEAM_CLASSES = {}
for team, color in [(0, 'Red'), (1, 'Blue')]:
    body = re.search(color+r'HeroClasses\*: array\[HeroClassesPerTeam, HeroClass\] = \[(.*?)\]', _source, re.S).group(1)
    TEAM_CLASSES[team] = re.findall(r'^\s*(\w+),?\s*$', body, re.M)
if len(NAMES) != 10 or any(len(v) != 5 for v in TEAM_CLASSES.values()):
    raise ValueError('Unexpected pinned hero schema')


def class_id(team, slot):
    return CLASS_ID[TEAM_CLASSES[team][slot]]


def class_ids(team):
    return [class_id(team, slot) for slot in range(5)]
