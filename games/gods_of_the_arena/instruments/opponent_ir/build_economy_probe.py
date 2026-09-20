"""Build isolated logging hooks; leave canonical game sources unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mechanics-root', type=Path, required=True)
    p.add_argument('--deps-root', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--nim', default='nim')
    a = p.parse_args()
    root = a.mechanics_root.resolve()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == 'f2ab9598d8f8001b6beae3e66404e341770c803f'
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--', 'src', 'examples/gods_of_the_arena'], cwd=root)
    overlay = a.output_dir.resolve() / 'overlay'
    folder = overlay / 'examples/gods_of_the_arena'
    source = root / 'examples/gods_of_the_arena'
    for f in source.rglob('*.nim'):
        dest = folder / f.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dest)
    sim = folder / 'sim.nim'
    original = sim.read_text()
    s = original.replace('## Deterministic animation slots shared by every backend.',
        'import std/json\nvar economyRewardTrace*, economyPurchaseTrace*, economyBasicTrace*: seq[JsonNode]\n\n## Deterministic animation slots shared by every backend.', 1)
    for reward, target, kind in [('Footman', 'world.footmen[targetFootman].id', 'creep'),
                                 ('Hero', 'world.heroes[targetHero].id', 'hero'),
                                 ('Tower', 'world.buildings[targetBuilding].id', 'building')]:
        needle = f'      hero.gainRewards({reward}XpReward, {reward}GoldReward)'
        assert s.count(needle) == 1
        s = s.replace(needle, needle + f'''
      economyRewardTrace.add %*{{"tick": world.tick, "hero": hero.id,
        "target": {target}, "kind": "{kind}", "xp": {reward}XpReward,
        "gold": {reward}GoldReward, "level_after": hero.level, "total_xp_after": hero.totalXp}}''', 1)
    needle = '  world.heroes[index].gold -= spec.cost\n  world.heroes[index].refreshHeroStats()\n  true'
    assert s.count(needle) == 1
    s = s.replace(needle, '''  economyPurchaseTrace.add %*{"tick": world.tick, "hero": heroId,
    "item_id": itemId, "item": $item, "gold_before": world.heroes[index].gold,
    "hp_before": world.heroes[index].hp, "cost": spec.cost}
''' + needle, 1)
    needle = '''        applyHeroHit(
          world,
          hero,
          damage,
          targetFootman,
          targetHero,
          targetBuilding,
          fortIndex
        )'''
    assert s.count(needle) == 1
    s = s.replace(needle, '''        economyBasicTrace.add %*{"tick": world.tick, "hero": hero.id,
          "target": (if targetHero >= 0: world.heroes[targetHero].id elif targetFootman >= 0: world.footmen[targetFootman].id elif targetBuilding >= 0: world.buildings[targetBuilding].id else: 0'i32),
          "kind": (if targetHero >= 0: "hero" elif targetFootman >= 0: "creep" elif targetBuilding >= 0: "building" else: "fort"),
          "damage": damage, "level": hero.level}
''' + needle, 1)
    sim.write_text(s)
    (a.output_dir / 'overlay-manifest.json').write_text(json.dumps({
        'game_commit': 'f2ab9598d8f8001b6beae3e66404e341770c803f',
        'canonical_sim_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'overlay_sim_sha256': hashlib.sha256(s.encode()).hexdigest(),
        'scope': 'Only append-only JSON logging at reward, accepted purchase and basic-hit sites; no canonical edits.'}, indent=2) + '\n')
    args = [a.nim, 'c', '--skipParentCfg:on', '--hints:off', '-d:release', '-d:headless', '-d:flatty64']
    for dep in sorted(a.deps_root.iterdir()):
        if (dep / 'src/polyworld').is_dir() or (dep / 'polyworld').is_dir():
            continue
        if dep.is_dir():
            args.extend(['--path:' + str(dep), '--path:' + str(dep / 'src')])
    args += ['--path:' + str(root), '--path:' + str(root / 'src'), '--path:' + str(overlay),
        '-o:' + str(a.output_dir.resolve() / 'economy-probe'), str(Path(__file__).with_name('economy_probe.nim').resolve())]
    subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
