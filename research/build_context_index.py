"""Index preserved coaching and the exact executable semantic layers."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    sessions = {
        '2026-09-20t17-21-56-307zf4f7b3': 'Richard135 formation/perimeter: pre-new-week historical coaching only.',
        '2026-09-20t19-10-35-082z64deb6': 'Offensive transition, scouting and ranged-carry defense: old-engine hypotheses.',
        '2026-09-22t16-43-56-076z862811': 'Portal recovery: distinct home/outbound purposes, keep guard and channel lock; inherited in current controller.',
        '2026-09-23t02-52-57-098ze03810': 'Field sustain: broader attempts failed; a later Druid-only transfer succeeded on its original engine.'}
    source_root = Path('/Users/aaln/Documents/Policy Loops/sessions')
    captures = {}
    for ident, scope in sessions.items():
        folder = source_root / ident
        assert (folder / 'notes.md').exists() and (folder / 'session.json').exists()
        rows = []
        for p in sorted(folder.rglob('*')):
            if not p.is_file(): continue
            relative = p.relative_to(folder)
            local = None
            if p.suffix in ['.md', '.json', '.txt']:
                dest = ROOT / 'research/coaching_inputs' / ident / relative
                if dest.exists(): assert sha(dest) == sha(p), dest
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dest)
                local = str(dest.relative_to(ROOT))
            rows.append({'relative': str(relative), 'origin': str(p), 'local': local,
                         'bytes': p.stat().st_size, 'sha256': sha(p)})
        captures[ident] = {'scope': scope, 'files': rows,
                          'review': 'Gemini synthesis is proposed coaching, not executable truth or a score qualification.'}
    write(ROOT / 'research/coaching_inputs/manifest.json', {'sessions': captures,
          'media_policy': 'Original videos, audio and images remain at their source paths with hashes; notes, input IR/policy, transcripts and synthesis are byte-copied. Empty inputs remain empty.'})

    pair = ROOT / 'research/policies/deployed'
    p = read(pair / 'policy.ir.json')
    semantics = read(pair / 'semantics.json')
    source = (pair / 'policy.bas').read_text()
    skills = {}
    for rule in p['strategy']:
        match = re.search(r"^' @rule " + re.escape(rule['id']) + r'\n(.*?)(?=\n\x27 @rule |\Z)', source, re.M | re.S)
        assert match, rule['id']
        skills[rule['skill']] = {
            'rule': rule['id'], 'when': rule['when'], 'goals': rule['for'],
            'executable': {'path': 'research/policies/deployed/policy.bas',
                           'line': source[:match.start()].count('\n') + 1,
                           'region_sha256': hashlib.sha256(match.group(1).encode()).hexdigest()},
            'ir': {'path': 'research/policies/deployed/policy.ir.json',
                   'pointer': '/skill/' + rule['skill']},
            'binding': p['skill'][rule['skill']],
            'grounded_contract': semantics['skills'][rule['skill']],
            'efficacy': 'Inherited bundle behavior; no isolated current-release causal effect asserted.'}
    write(ROOT / 'research/knowledge/controller.ir.json', {
        'schema': 'gota-context-index/1', 'id': 'deployed_controller_current62',
        'situation': {'engine_commit': read(ROOT / 'research/manifest.json')['engine_commit'],
                      'game_version': p['execution']['game_version'],
                      'public_inputs_only': True, 'controller_source_sha256': sha(pair / 'policy.bas')},
        'belief': {'incumbent': 'Retained after completed 180-game comparison; not independently proved optimal.',
                   'compiler_memory_annotations_are_partial': True,
                   'additional_persistent_state_visible_in_source': {
                       'lane_selection': ['laneDecisionStarted', 'laneDecisionStart', 'laneAssigned', 'laneStored', 'laneChanged'],
                       'neutral_pull': ['nPullStage', 'nPullCamp', 'nPullMob', 'nPullUntil', 'nPullReady', 'nLastSeen'],
                       'note': 'These globals persist between decisions; lifecycle explicitly clears nPullStage on death. One-time lane assignment survives respawn. Read full source for all state.'}},
        'goal': {'Score': 'Expected floor(max(0, XP - 200 * elapsed_minutes)); individual score only.'},
        'skill': skills, 'strategy': p['strategy'],
        'execution': {'kind': 'navigation_index_not_a_second_executable_policy',
                      'authoritative_pair': 'research/policies/deployed',
                      'workflow': 'research/IR_WORKFLOW.md',
                      'order_matters': 'Later commands can replace earlier intent; active/stopped, retreat and portal locks arbitrate channels.'},
        'update': {'revision': 1, 'origin': 'User requested fresh context and useful IR-to-policy migration.',
                   'evidence': ['research/RESULTS.md', 'research/results/statistics.json'],
                   'executable_changed': False}})
    print(json.dumps({'sessions': len(captures), 'captured_files_indexed': sum(len(x['files']) for x in captures.values()),
                      'executable_skills_indexed': len(skills)}))


if __name__ == '__main__': main()
