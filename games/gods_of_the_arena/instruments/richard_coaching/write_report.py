"""Publish the completed local evidence package and precise research disposition."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from prepare import ROOT, STUDY, CAMPAIGN, read, write, digest
from finalize import DEST
import report


def outcome(v):
    if v is None:return 'Not submitted'
    if v.get('invalid_games'):return f"{v['invalid_games']}/40 invalid; rejected"
    return f"{v['wins']}/{v['games']} ({v['losses']} losses, {v['draws']} draws)"


def main():
    result=read(DEST/'results.json');assert result['complete']
    qualified=result['Richard_qualified']
    headline=('A coached candidate cleared the Richard135 both-color discovery gate; '
              'independent confirmation and field qualification remain.' if qualified else
              'No coached variant established a Richard135 win advantage on both colors. '
              'The validated blue component wins 40/40; red remains unresolved.')
    lines=['# Richard v135 coaching study — September 20, 2026','',headline,'',
        f"Completed {result['hosted_games']} hosted games: {result['hosted_games']-result['invalid_hosted_games']} passed full replay/all-ten-VM validation; {result['invalid_hosted_games']} were quarantined for an owned VM instruction-limit failure. All purchased replays were preserved and reconstructed. Invalid games are neither wins nor losses.",
        '',f"Completed {result['local_games']} native local games. The final combined controller passed its 19,000-instruction gate with 2,018 instructions of measured headroom. Local opponents diagnose behavior and regressions; they are not executable proxies for Richard.",
        '', 'No league policy was changed by this study. The original baseline remains in [retained-baseline](retained-baseline/). The separately verified improvement is saved in [validated-blue-component](validated-blue-component/). Every tested combined IR/BASIC pair, including failures, is under [evaluated](evaluated/).',
        '', '| Combined policy | Richard: our red | Richard: our blue | Local wins / control |',
        '|---|---:|---:|---:|']
    for r in result['candidates']:
        h=r['Richard'];red=outcome(h['red']) if h else 'Not submitted';blue=outcome(h['blue']) if h else 'Not submitted'
        lines.append(f"| [{r['name']}](evaluated/{r['name']}/validation.json) | {red} | {blue} | {r['local']['wins']}/12 vs {r['local_control']['wins']}/12 |")
    lines += ['', 'The deployed control scored 0/40 on each color in both contemporaneous comparison windows. The prospective gate required at least 30/40 wins on **each** color and at least 8 more combined wins than control. Field and survival requirements were retained. Draws score zero.',
        '', 'These are uniform five-versus-five policy matches on release 2026.9.16.5, map 116/seed 54 configuration, against exact `richard-gods-of-the-arena:v135` (`7c370daf-3c5f-42f8-870b-54b79c495a44`). Different seeds often repeat command trajectories; complete command-stream diversity is recorded for every valid cell. Do not treat 40 games as 40 independent trials. No claim of leaderboard #1 or broad field strength follows.',
        '', '## What the coaching changed', '',
        'The seven-layer IR now represents an authored late-game transition, four/five-hero readiness, observed enemy dispersion, shared target selection, perimeter entry scoring, synchronized breaches, and a movement tether. The complete bundle was evaluated together. Later revisions added forward discovery when the next objective is unseen, a four-member cohort resistant to a distant fifth ally, remembered home pressure through fog, and ordered equipment across classes.',
        '', 'Perimeter circling is implemented as repeated selection among three exterior approach points. This is an authored approximation of the coaching, not a guarantee of continuous orbiting or avoidance of every tower attack zone. A bounded probe timer can authorize a breach; the replay results determine whether that decision helps.',
        '', 'The first group controller gathered heroes but stopped after an objective disappeared from vision. Native replay reconstruction identified that default-goal stall. A subsequent replay showed nine sampled transitions into or out of defense: lost visibility repeatedly reversed the returning group. A 1,200-tick remembered return corrected that decision mechanism; in its diagnostic game, Richard’s Demon Hunter died six times, but our team still lost. This supports the mechanism observation, not a winning-policy claim.',
        '', 'The delayed cohort exceeded the BASIC instruction limit in all 40 red hosted games. Exact native replay reproduced the first inspected failure at tick 5,274 after 24,936 matching owned commands and every prior state hash. All 40 games were quarantined. A bounded observer then failed the stricter local margin at 19,105 instructions, so it was never uploaded. Coordinating observation and combat budgets reduced the final local maximum to 17,982 without relaxing the gate.',
        '', '## Why specialization matters', '',
        'Three historical specialists that beat an older Richard version each went 0/40 on both colors against v135 in the separate 320-game verification. Their older success did not transfer. The current Jordan-tuned recall can cancel a distant return to defend; the earlier, persistent critical warning has a verified blue benefit against Richard135. Red has different classes and routes, and these group-assault changes did not demonstrate the same transfer.',
        '', 'The policy reacts to public observations and remembered sightings. It does not read opponent policy IDs or hidden positions. General player identification and broad leaderboard qualification remain outside this Richard-focused study’s validated results.',
        '', '## Preserved inputs and reproduction', '',
        f"All {result['captured_input_files']} captured session files were copied and hash-verified unchanged. The recording was bound to audited episode `ereq_15e13437-273d-4c4f-84cc-162b01b602b4`, historical bound_idle red versus Richard135 blue. The session contained no attached policy; the comparison baseline was explicitly bound to the deployed `be6affd3…` source.",
        '', '- [Session references](session-references.json)', '- [Complete result index](results.json)',
        '- [Captured coaching inputs](session-inputs/)',
        '- [Semantic coaching implementation map](semantic-coaching-map.json)',
        '- [Captured conversion tooling manifest](tooling-manifest.json)',
        f'- Raw evidence, replays, native proofs, and frozen plans: `{STUDY}`',
        '', 'Each evaluated directory contains primary `policy.py`, semantic `policy.ir.json`, regenerated `policy.bas`, extracted IR, semantics, manifest, and validation. Outcome feedback changed the IR beliefs and evidence; every evaluated BASIC remains byte-identical to its tested source.',
        '', 'To verify every saved pair with the captured repo conversion, from any directory:',
        '', '```sh',f'python3 "{DEST}/reproduce.py"','```',
        '', 'This verifies conversion and source parity. The recorded live results are evidence files, not a promise of identical performance against future opponent versions.', '']
    (DEST/'README.md').write_text('\n'.join(lines))
    html=report.render().decode().replace('<meta http-equiv="refresh" content="20">','')
    html=html.replace('This report refreshes every 20 seconds.', 'Completed study; archived report.')
    html=html.replace('<h1>Richard v135 — coached counter</h1>',
        '<h1>Richard v135 — coached counter</h1><p><b>'+headline+'</b></p>')
    docs=ROOT/'docs/reports';docs.mkdir(parents=True,exist_ok=True)
    path=docs/'2026-09-20-richard135-coaching.html';path.write_text(html)
    shutil.copy2(path,DEST/'report.html')
    campaign_report=CAMPAIGN/'COACHING_RICHARD135_RESULT.md'
    campaign_report.write_text('\n'.join(lines[:6])+f'\n\nPrimary saved package: {DEST}\n\nFull report: {path}\n\nNo coaching-study batch remains pending. Resume independent Richard v135 red research; preserve all frozen sources and avoid repeating these exact failed variants.\n')
    experiment=ROOT/'games/gods_of_the_arena/experiments/2026-09-20-richard135-coaching.md'
    experiment.parent.mkdir(parents=True,exist_ok=True)
    ids=[]
    for p in STUDY.glob('**/hosted-plan.json'):
        for arm in read(p)['arms']:
            f=Path(arm['directory'])/'batch/created.json'
            if f.exists():ids.append(read(f)['id'])
    experiment.write_text('---\nid: 2026-09-20-richard135-coaching\nstatus: '+('target-discovery-qualified' if qualified else 'rejected-for-promotion')+'\nevals: '+json.dumps(sorted(set(ids)))+'\n---\n\n'+headline+f'\n\nSaved IR/policy/results: {DEST}\nSession: {result["session"]}\nFull 800-game accounting, including 40 invalid games: {DEST}/results.json\n')
    log=ROOT/'games/gods_of_the_arena/players/richard135-counter/VERSION_LOG.md'
    text=log.read_text();marker='## Coaching study disposition — 2026-09-20'
    if marker not in text:
        text+='\n'+marker+'\n\n'+headline+'\n\n'
        for r in result['candidates']:
            if r.get('uploaded_version'):
                h=r['Richard'];text+=f"- `{r['uploaded_version']['id']}` / `{r['name']}`: red {outcome(h['red'])}; blue {outcome(h['blue'])}. Both-color target gate: {r['Richard_both_color_gate_passed']}. No league promotion.\n"
        text+=f'\nEvaluated semantic feedback and exact tested bytes: {DEST}\n';log.write_text(text)
    write(DEST/'report-artifacts.json',{'html':str(path),'html_sha256':digest(path.read_bytes()),
        'readme_sha256':digest((DEST/'README.md').read_bytes()),'written_at':datetime.now(timezone.utc).isoformat()})
    print(str(DEST/'README.md'),flush=True)


if __name__=='__main__':main()
