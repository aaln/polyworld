"""Reconcile release5 evidence and verify the best policy on both league players."""
from copy import deepcopy
from datetime import datetime,timezone
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest,bundle,compile_policy,extract,refresh_grounding
from release_deploy import champions
from release_deploy_pair import check_champions,verify_owned
from release_workspace import RUN,VERSION
from win_hosted import live

VERSIONS={'ply_594ec24d-d7f3-4370-a000-468354ec41c9':'810d3860-af35-4fed-9364-a4e4bd8b0c2b',
          'ply_630a768f-d623-44b2-80fa-36968d6fa75a':'fa0cab2a-708f-40e0-b6b8-1e44ffeea124'}
OUT=RUN/'coached-lanes/deployment-r5'


def main():
    game=live();OUT.mkdir(exist_ok=True)
    parent=read(RUN/'coached-lanes/validated-baseline-r5/policy.ir.json')
    p=deepcopy(parent);source=(HERE/'win_bounded_0916.evaluated.bas').read_bytes()
    paths=[RUN/'coached-lanes/r5-convoy/hosted/current/result.json',RUN/'coached-lanes/r5-current-field/result.json']
    team,field=[read(path) for path in paths]
    assert team['rivals']['jordan']['wins']==80 and field['games']==100 and field['wins']==75 and field['equipment_games']==100
    refs=[{'artifact':str(path),'sha256':digest(path.read_bytes())} for path in paths]
    p['situation']['notes']=f'Published{VERSION}, exact clean source f2ab9598d8f8001b6beae3e66404e341770c803f. Enemy god is protected by two guard towers. Current executable revalidated in180hostedgames. Coaching session inputs preserved separately; captured PudgeWars source was not used as GotA baseline.'
    claim='Live2026.9.16.5: exact deployed bounded executable won80/80 versusJordanv175 with40games/color and two distinct team commandtapes. Separate100sampled mixed-team fieldgames yielded75wins, all100boughtgear, alltenVMs/fullreplays valid. FieldLich3/10 suggests further diagnosis; class samples are small and rosters differ. No broad superiority or rank1 claim. Tested wholesale lane-rush replacements failed local gates; retain this executable.'
    p['belief']['claims']['B_r5_field']={'claim':claim,'status':'supported','evidence':refs}
    p['update']={'revision':parent['update']['revision']+1,'parent':digest(parent),'change':'Reconcile complete180game release5 evidence and retain the best validated deployed executable under both existing players.','needs_review':['belief/B_lane_coverage'],'evidence':parent['update']['evidence']+refs}
    refresh_grounding(p)
    assert compile_policy(p).encode()==source and extract(source.decode(),p)==p
    pair=OUT/'policy';bundle(p,pair)
    write(HERE/'win_bounded_0916.r5.evaluated.ir.json',p);(HERE/'win_bounded_0916.r5.evaluated.bas').write_bytes(source)
    tags={'semantic_ir_sha256':digest(p),'symbolic_policy_sha256':digest(source),'ir_revision':str(p['update']['revision']),
          'game_version':VERSION,'validation':claim,'validation_scope':'Two repeated teamlineups plus separate100game sampled mixedteam field; no newbehavior or rankclaim.',
          'field_sha256':refs[1]['sha256'],'jordan175_sha256':refs[0]['sha256'],'feedback_parity':'Exact IR compile and symbolic reverse extraction; unchanged tested BASIC.'}
    write(OUT/'requested-tags.json',tags);verified=[]
    with client() as c:
        before=check_champions(champions(c),VERSIONS,VERSIONS)
        write(OUT/'before.json',list(before.values()))
        for player,version in VERSIONS.items():
            row=before[player]['policy_version'];verify_owned(c,{'id':version,'name':row['policy']['name']},player)
            path=RUN/'win-first-study'/('hosted-discovery/bounded' if player.endswith('468354ec41c9') else 'deployment-pair/aaron-upload')
            meta,receipt=read(path/'upload-request.json'),read(path/'uploaded-version.json')
            if receipt['id']!=version or meta['player_id']!=player or meta['content_hash']!=digest(source) or meta['size_bytes']!=len(source):raise ValueError('Tested upload provenance differs')
            pv=get(c,'/stats/policy-versions/'+version)
            if pv.get('player_file_content_hash') not in (None,digest(source)):raise ValueError('Remote executable mismatch')
            write(OUT/(version+'-before-tags.json'),pv.get('tags',{}))
            response=c.put('/stats/policy-versions/'+version+'/tags',json=(pv.get('tags') or {})|tags);response.raise_for_status()
            after=get(c,'/stats/policy-versions/'+version)
            if any(after['tags'].get(k)!=v for k,v in tags.items()):raise ValueError('Metadata readback failed')
            verified.append({'player':player,'version':version,'label':row['label'],'source_sha256':digest(source),'ir_sha256':digest(p),'upload_receipt':str(path/'uploaded-version.json')})
        after=check_champions(champions(c),VERSIONS,VERSIONS)
        assert all(after[player]['policy_version']['id']==version for player,version in VERSIONS.items())
    write(OUT/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'authorization':'User: deploy the policies and then keep autoresearching','owned_active_ladder_players':2,'players':verified,'game_version':VERSION,'coworld_id':game['id'],'selection_action':'Both best validated versions were already selected and active; no duplicate version or player created. Updated current-release IR/evidence metadata on both, verified readback and active selection.','executable_changed':False,'ir_policy_pair':str(pair)})
    write(HERE/'active_policy.json',{'players':verified,'policy':str(pair/'policy.bas'),'semantic_ir':str(pair/'policy.ir.json'),'deployment_receipt':str(OUT/'deployment-verified.json')})
    with (HERE/'VERSION_LOG.md').open('a') as f:f.write(f'\n## Release5 deployment verification {datetime.now(timezone.utc).isoformat()}\n\nBoth existing players remain active on the best validated bounded executable.180new valid hostedgames:80/80vsJordan175(two commandtapes),75/100mixedfield. No newbehavior deployed. FinalIR `{digest(p)}`; BASIC `{digest(source)}`. Evidence and live readback `{OUT}`.\n')
    print('Both active league policies verified; release5 IR and evidence metadata updated.',flush=True)


if __name__=='__main__':main()
