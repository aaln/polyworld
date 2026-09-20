"""Causal, abstaining opponent identification from observed early equipment.

This is a research instrument, not a winning controller. Labels are training
metadata only; the predictor receives visible class and inventory records.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import math

UNKNOWN = 'unknown'
HORIZONS = (480, 960, 1440, 1920, 2400)


def signature(hero):
    return (hero['class'], tuple(sorted(item for item in hero['items'] if item != 'NoItem')))


def fit(records):
    """One first-visible inventory per hero; one contribution per episode/key."""
    counts = defaultdict(Counter)
    class_counts = defaultdict(Counter)
    for record in records:
        label = record['label']
        observed = record['first_inventory']
        for cls in {h['class'] for h in observed}:
            class_counts[cls][label] += 1
        for key in {signature(h) for h in observed}:
            counts[key][label] += 1
    rules = {}
    labels = sorted({r['label'] for r in records})
    for key, evidence in counts.items():
        scores = {label: evidence[label] / max(1, class_counts[key[0]][label]) for label in labels}
        ranking = sorted(scores, key=lambda label: (-scores[label], label))
        best = ranking[0]
        second = scores[ranking[1]] if len(ranking) > 1 else 0
        # Require actual supporting trajectories, a substantial gap, and avoid
        # interpreting absent comparison-class data as discrimination.
        complete_comparisons = all(class_counts[key[0]][label] >= 2 for label in labels if label != UNKNOWN)
        eligible = (best != UNKNOWN and evidence[best] >= 2 and complete_comparisons
                    and scores[best] >= 0.5 and scores[best] >= 4 * second)
        rules[key] = {'label': best if eligible else UNKNOWN,
                      'eligible': eligible, 'evidence': dict(evidence),
                      'class_totals': dict(class_counts[key[0]]), 'scores': scores}
    return rules


def predict(first_inventory, rules, tick):
    """Two distinct heroes must agree; repeated frames add no votes."""
    votes = Counter()
    evidence = []
    for hero in first_inventory:
        if hero['tick'] > tick:
            continue
        rule = rules.get(signature(hero))
        if rule and rule['eligible']:
            votes[rule['label']] += 1
            evidence.append({'hero': hero['id'], 'class': hero['class'],
                             'seen_at': hero['tick'], 'label': rule['label']})
    ranked = votes.most_common()
    chosen = ranked[0][0] if ranked and ranked[0][1] >= 2 and len(ranked) == 1 else UNKNOWN
    return {'label': chosen, 'votes': dict(votes), 'evidence': evidence}


@dataclass
class ThreatMemory:
    """Independent of identity: current structure pressure may demand defense."""
    last_tick: int = -1
    last_structure_contact: int = -100000
    mode_until: int = 0
    previous_hp: dict = field(default_factory=dict)

    def step(self, view, our_team):
        tick = view['tick']
        if tick < self.last_tick:
            raise ValueError('Observations must be chronological')
        self.last_tick = tick
        if not view['available']:
            return {'mode': 'unobserved', 'reason': 'observer unavailable'}
        objects = {o[0]: o for o in view['objects']}
        structures = {i: o for i, o in objects.items() if o[1] in (1, 4) and o[2] == our_team and o[6] > 0}
        enemies = [o for o in objects.values() if o[1] == 2 and o[2] != our_team and o[7] and o[6] > 0]
        targets = [o for o in enemies if o[8] in structures]
        # A target ID is observed intent, not attributed damage. Both are kept
        # distinct; missing observations never fabricate damage or enemy death.
        damage = [i for i, o in structures.items() if i in self.previous_hp and o[6] < self.previous_hp[i][1]
                  and tick - self.previous_hp[i][0] <= 24]
        self.previous_hp = {i: (tick, o[6]) for i, o in structures.items()}
        home = next((o for o in structures.values() if o[1] == 1), None)
        near = [] if home is None else [o for o in enemies if (o[4]-home[4])**2+(o[5]-home[5])**2 <= 60**2]
        if targets or damage:
            self.last_structure_contact = tick
        # Diagnostic proposal only. Actual responder selection, travel and
        # release must be evaluated in reacting games before adoption.
        if len(near) >= 2 and tick - self.last_structure_contact <= 240:
            self.mode_until = tick + 240
        return {'mode': 'bounded_defense' if tick < self.mode_until else 'ordinary',
                'visible_structure_targeters': [o[0] for o in targets],
                'observed_structure_damage': damage,
                'visible_near_home': [o[0] for o in near],
                'mode_until': self.mode_until}
