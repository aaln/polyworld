"""Render win-first evidence without pooling the rejected duration-sensitive study."""
from pathlib import Path
import markdown
from policy_ir import HERE,read,write
from release_workspace import RUN,ROOT,SOURCE,VERSION
from win_screen import STUDY

def report():
    local=read(STUDY/'local/screen-result.json');disc=read(STUDY/'hosted-discovery/result.json')
    cp=STUDY/'hosted-confirmation/result.json';confirm=read(cp) if cp.exists() else None
    rp=STUDY/'rival-matchups/result.json';rivals=read(rp) if rp.exists() else None
    fp=STUDY/'field/result.json';field=read(fp) if fp.exists() else None
    dp=STUDY/'deployment-pair/deployment-verified.json';deployed=read(dp) if dp.exists() else None
    name=disc['selected'];version=read(STUDY/'hosted-discovery'/name/'uploaded-version.json') if name else None
    lines=['# Gods of the Arena — win-first autoresearch','',
       ('Both existing league players now use the validated successor.' if deployed else 'Successor research is complete through the stages reported below; the confirmed Lich upgrade remains selected on both players.'),'',
       f'Clean game release `{VERSION}`, commit `{SOURCE}`, workspace `{ROOT}`. Original engine edits remain untouched. All policy changes compile from semantic IR and are reverse-extracted; every retained game has a full source-matched replay audit and VM validity proof.','',
       '## Why this is a new study','',
       'The preceding 360-game local screen remained **failed** under its original deaths-per-minute and total-XP gates. Lane routing won 40/40 versus Lich 25/40 with 274 versus 289 total hero deaths. Its shorter games reduced total XP while raising death intensity. Those results selected hypotheses; they were not relabeled as a pass.','',
       'The next study was preregistered before its new games: fort wins first, mean hero deaths per completed game at most 110% of the deployed control, equipment in every game and complete validity. Death intensity and XP/minute remain reported diagnostics. Hosted confirmation also requires a 5-point win gain, one-sided Fisher p < 0.025, and no adverse class test at p < 0.005.','',
       '## Fresh local screen','',
       '| Policy | Wins | Total hero deaths | Mean minutes/game | XP/minute |','|---|---:|---:|---:|---:|']
    for n,m in local['metrics'].items():lines.append(f'| {n} | {m["wins"]}/40 | {m["deaths"]} | {m["mean_minutes"]:.2f} | {m["xp_per_minute"]:.1f} |')
    lines+=['','All 120 games used fresh paired seeds and the clean current engine. Local evidence is a mechanism screen, not a claim of leaderboard strength.','', '## Hosted discovery','',
       '| Policy | Wins | Mean hero deaths/game | Deaths/alive-minute | Mean minutes/game |','|---|---:|---:|---:|---:|']
    for n,m in disc['arms'].items():lines.append(f'| {n} | {m["wins"]}/{m["games"]} | {m["mean_deaths"]:.3f} | {m["death_rate"]:.3f} | {m["mean_minutes"]:.2f} |')
    lines+=['',f'Selected: `{name}`. Discovery outcomes are excluded from independent confirmation; no interim tuning or stopping.','']
    diversity_path=STUDY/'hosted-discovery/command-diversity.json'
    if diversity_path.exists():
        diversity=read(diversity_path)
        lines+=['Complete replay command comparison found '+', '.join(f'{n}: {a["distinct_full_command_tapes"]} distinct tapes in {a["games"]} games' for n,a in diversity['arms'].items())+'. Equality compares every recorded command for all ten heroes. Distinct tapes do not establish statistical independence. The comparison uses ten fixed role rotations; episode-level p-values describe this roster design and do not establish performance against arbitrary opponents.','']
    if confirm:
        lines+=['## Fresh hosted confirmation','', '| Policy | Wins | Win rate | Mean hero deaths/game | Deaths/alive-minute | Gear games |','|---|---:|---:|---:|---:|---:|']
        for n,m in confirm['arms'].items():lines.append(f'| {n} | {m["wins"]}/400 | {m["wins"]/4:.2f}% | {m["mean_deaths"]:.3f} | {m["death_rate"]:.3f} | {m["equipment_games"]}/400 |')
        c=confirm['comparisons'][name]
        lines+=['',f'Gain {100*c["gain"]:+.2f} percentage points; one-sided p={c["one_sided_p"]:.6g}. Adverse classes: {", ".join(c["adverse_classes"]) or "none"}. Frozen overall gate: **{"passed" if confirm["passed"] else "failed"}**. All 800 games and full audits completed before interpretation.','']
        a,b=confirm['arms'][name],confirm['arms']['current']
        lines += [f'Games averaged {a["mean_minutes"]:.2f} versus {b["mean_minutes"]:.2f} minutes. Death intensity was nearly unchanged; the reduction in deaths per game accompanies faster finishes and is not independent evidence of better duel kiting. Mean Glory diagnostic (200 XP/minute penalty) was {a["mean_glory"]:.1f} versus {b["mean_glory"]:.1f}; the league objective remains binary fort wins.','']
    if rivals:
        lines+=['## Named rivals','', '| Exact rival | Red wins | Blue wins | Total W/L/D | Both fixed lineups won? |','|---|---:|---:|---:|---|']
        for r in rivals['rivals'].values():lines.append(f'| {r["label"]} | {r["colors"]["red"]["win"]}/40 | {r["colors"]["blue"]["win"]}/40 | {r["wins"]}/{r["losses"]}/{r["draws"]} | {"Yes" if r["beaten"] else "No"} |')
        lines+=['','Five copies per team create two fixed tactical lineups per rival, one per color. Different seeds can reproduce identical command trajectories. These results describe those lineups; nominal binomial p-values do not establish broad generalization. Mixed-roster and sampled-field results remain separate.','']
        if (STUDY/'rival-matchups/command-diversity.json').exists():
            diversity=read(STUDY/'rival-matchups/command-diversity.json')
            lines+=['Exact command-tape comparisons found '+', '.join(f'{n}: {a["distinct_full_command_tapes"]} distinct full-team tapes across {a["games"]} games' for n,a in diversity['arms'].items())+'.','']
        if (STUDY/'review/codex-red-comparison.png').exists():
            lines+=['A reviewed red-side Codex loss ended at 2:51 with no fort attack commands from our team. The bounded successor reached and destroyed the enemy fort at 2:23. These two source-verified replays use different seeds; the full fixed-lineup results are above.',
                f'[Recorded position comparison]({STUDY/"review/codex-red-comparison.png"}) · [Watch the successor win](https://softmax.com/observatory/v2?tab=episode-requests&detail=episode-request:ereq_0788d2e9-bb3d-455b-987b-a2b19a2a349e).','']
    if field:lines+=['## Current-field check','',f'One 100-episode request sampled current division champions, excluding both owned players from other seats. Candidate: **{field["wins"]}/100 wins**, gear {field["equipment_games"]}/100. Frozen minimum: 50 wins plus complete validity. **{"Passed" if field["passed"] else "Failed"}**. This is a transfer guardrail, not a significance test against the field.','']
    review=STUDY/'review/druid-review-manifest.json'
    if review.exists():
        lines+=['## Remaining gameplay gap','',
          'Bounded pursuit lost all 10 Druid Warden discovery games; full lane routing won 7/10 but failed the overall survival guard. In a reviewed bounded loss, the Druid pushed toward the enemy base while the home fort fell at 3:03 with only one Druid death. A reviewed lane-routing win defended that approach longer and finished at 7:49 with six Druid deaths. These are different-seed examples, not a paired causal estimate. Class-specific lane coverage is a follow-up hypothesis; the evaluated bounded policy was left frozen.', '',
          f'- [Recorded position comparison]({STUDY/"review/druid-movement.png"})', f'- [Replay selection and checks]({review})','']
    lines+=['## Deployment and artifacts','']
    if version:lines += [f'Tested successor: `{version["name"]}:v{version["version"]}` (`{version["id"]}`).','']
    if deployed:
        for p in deployed['players']:lines.append(f'- {p["player"]["name"]}: `{p["policy_version"]["label"]}`, selected and active.')
        lines+=['','Exactly two owned ladder players verified. This does not establish rank #1.','']
        lines += [f'- [Final semantic IR]({HERE/("win_"+name+"_0916.evaluated.ir.json")})',
                  f'- [Exact evaluated BASIC]({HERE/("win_"+name+"_0916.evaluated.bas")})',
                  f'- [IR feedback and parity proof]({STUDY/"reconciled"/name/"reconciliation.json"})','']
        if (STUDY/'deployment-pair/final-metadata/verified.json').exists():
            lines += [f'Final IR and evidence hashes were also read back from both selected versions’ private policy tags. [Metadata receipt]({STUDY/"deployment-pair/final-metadata/verified.json"}).','']
    else:lines+=['Current selected versions remain `aaron-gota-ir-release-lich-nearest-0916:v1` on Optimizer and its byte-identical `-aaron:v1` registration on Aaron. They passed an earlier 1,200-game comparison and a 52/100 current-field guardrail.','']
    new_hosted=sum(a['games'] for a in disc['arms'].values())+(800 if confirm else 0)+(160 if rivals else 0)+(100 if field else 0)
    lines += [f'Completed campaign totals: **880 new local games and {3260+new_hosted:,} hosted games**. Reused controls are not counted again. The win-first hosted stages above account for {new_hosted:,} of those games.','',
      f'- [Frozen win-first plan]({STUDY/"local/plan.json"})',f'- [Discovery evidence]({STUDY/"hosted-discovery/result.json"})',
      f'- [Previous Lich policy report]({RUN/"r3-study/REPORT.html"})',f'- [Source parity proof]({RUN/"r3/source-parity.json"})']
    for title,p in [('Confirmation',cp),('Rival results',rp),('Field check',fp),('Verified deployment',dp)]:
        if p.exists():lines.append(f'- [{title}]({p})')
    text='\n'.join(lines)+'\n';(RUN/'WIN_REPORT.md').write_text(text)
    (RUN/'WIN_REPORT.html').write_text('<!doctype html><meta charset="utf-8"><title>GotA win-first study</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;font:16px/1.6 system-ui;color:#18202a;background:#f6f7f9;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #dde2e8}a{color:#1457af}</style>'+markdown.markdown(text,extensions=['tables']))
    if deployed:
        if not (RUN/'r3-study/REPORT.html').exists():raise ValueError('Archive the preceding report before replacing the latest report')
        for extension in ['md','html']:(RUN/('REPORT.'+extension)).write_bytes((RUN/('WIN_REPORT.'+extension)).read_bytes())
    write(STUDY/'report-summary.json',{'new_local_games_campaign':880,'new_hosted_games_campaign':3260+new_hosted,'candidate':name,'confirmation_passed':confirm['passed'] if confirm else None,'field_passed':field['passed'] if field else None,'deployed':bool(deployed)})
    print(RUN/'WIN_REPORT.html')
if __name__=='__main__':report()
