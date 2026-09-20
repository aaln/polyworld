"""Build a focused review artifact from completed rush-defense evidence."""
from datetime import datetime, timezone
from policy_ir import read
from rush_defense import STUDY
from release_workspace import RUN, VERSION, SOURCE


def main():
    lines = ['# GotA rush-defense research', '', f'Updated {datetime.now(timezone.utc).isoformat()}. '
             f'Locked game {VERSION}, source `{SOURCE}`.', '',
             'The deployed bounded policy split its heroes into two outer lanes while khors pushed '
             'five heroes through the middle. In the user-supplied replay, all five attackers were '
             'visible by40seconds; our god died at125.33seconds, with no hero deaths on either team. '
             'Red-kite repeated the middle push; gota-g001 used an outer lane and first fought our '
             'advancing heroes. Shared visibility of that outer rush was partial.', '',
             f'[User replay breakdown]({RUN}/coached-lanes/khors-defense/rush-breakdown.png).', '',
             'The new semantic IR detects four visible enemy heroes near a standing friendly tower '
             'or god, suspends the split push, and rallies behind that structure. It continues '
             'defending surviving deep invaders through bounded gaps in vision. Red and blue have '
             'separately tested commitment durations. Item purchases remain enabled. Normal combat '
             'remains unchanged outside defense; its scan budget is reduced during defense. The '
             'BASIC is generated from versioned semantic contracts and reverse-extracts to the same IR.', '',
             '## Local evidence', '']
    local = STUDY/'local/result.json'
    if local.exists():
        r=read(local)
        lines += ['| Policy | Wins /60 | Default /20 | Deployed /20 | Middle-rush proxy /20 | Hero deaths |',
                  '|---|---:|---:|---:|---:|---:|']
        for name,m in r['metrics'].items():
            o=m['opponents']
            lines.append(f'| {name} | {m["wins"]} | {o["default"]} | {o["current"]} | {o["center_proxy"]} | {m["deaths"]} |')
        lines += ['', 'All180games passed full replay/VM audits; every controlled hero bought gear. '
                  'The proxy is our own earlier five-hero push, not private rival code. Repeated '
                  'seeds test six fixed opponent/color contexts and do not establish broad significance. '
                  'The candidate wins more but incurs more hero deaths; survival remains a tradeoff.', '',
                  f'[Results]({local}); [evaluated IR]({STUDY}/local/context-feedback/blue_memory/policy.ir.json); '
                  f'[generated BASIC]({STUDY}/local/candidates/blue_memory/policy.bas).', '',
                  'An additional replay run exposed defense variables and matched every result and '
                  'replay byte from the normal evaluator. It showed all five heroes receiving the '
                  'same rally point by the40second sample. '
                  f'[Behavior evidence]({STUDY}/instrument-check/behavior-review.json).', '']
    lines += ['## Exact live opponents', '', '| Arm | Rival | Red wins /40 | Blue wins /40 |', '|---|---|---:|---:|']
    for arm in ['current','blue_memory']:
        for key in ['khors','red_kite','gota_g001']:
            path=STUDY/'hosted'/arm/'matchups'/key/'result.json'
            if path.exists():
                r=read(path)['rivals'][key]
                lines.append(f'| {arm} | {r["label"]} | {r["colors"]["red"]["win"]} | {r["colors"]["blue"]["win"]} |')
            else:
                lines.append(f'| {arm} | {key} | Pending full audit | Pending full audit |')
    lines += ['', 'Each cell is one40episode request with all ten seats pinned. Every rival/color '
              'and its full audit must finish before the complete candidate verdict. Exact command '
              'diversity is reported separately; repeated deterministic tapes are not independent tactics.', '',
              '## Deployment status', '',
              'Both league players still select the bounded policy. The defense upload is experimental. '
              'Promotion requires the frozen rush gate, a fresh paired-player mixed-roster guardrail, '
              'and a sampled field check. No champion selection follows from the local result alone.', '',
              'The earlier gear-only800game experiment is rejected: allied wins110/160 versus93/160, '
              'but the class and opposed-draw gates failed. Its known failure is included in the '
              'new defense IR; it is not inherited as mixed-team validation.', '',
              'Failed candidates remain preserved: the first screen had22VM overruns and20complete '
              'games; the next two42game screens failed tactical gates. A36game lineup screen '
              'selected the candidate before the fresh180game validation. No captured coaching '
              'inputs or original workspace changes were overwritten.']
    (STUDY/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(STUDY/'REPORT.md')


if __name__ == '__main__':
    main()
