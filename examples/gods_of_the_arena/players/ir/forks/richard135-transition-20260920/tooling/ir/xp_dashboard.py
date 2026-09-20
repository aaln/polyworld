"""Use the run-eval dashboard with the same authenticated server as XP tools."""
import importlib.util
import argparse
import json
from pathlib import Path
import sys
import time

from softmax.auth import get_api_server, load_current_token
from hosted_wave import client


if __name__ == '__main__':
    path = Path.home() / '.codex/skills/run-eval/scripts/xp_dashboard.py'
    spec = importlib.util.spec_from_file_location('run_eval_dashboard', path)
    dashboard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dashboard)
    dashboard.load_token = lambda: load_current_token(server=get_api_server())
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--watch-directory', type=Path, action='append')
    options, rest = parser.parse_known_args()
    sys.argv = [sys.argv[0], *rest]
    if options.watch_directory:
        class WatchingState(dashboard.State):
            def snapshot(self):
                result = super().snapshot()
                with self.lock:
                    folders = {key: value.get('artifact_folder') for key, value in self.data.items()}
                for request, row in result.items():
                    if not folders.get(request):
                        continue
                    folder = Path(folders[request])
                    arm = folder.parent.name
                    label = {'control': 'Current policies', 'candidate': 'Candidate policies'}.get(arm, arm)
                    part = folder.name.removeprefix('part-')
                    row['label'] = label + (f' · lineup {int(part) + 1}' if part.isdigit() else f' · {folder.name}')
                    try:
                        plan = json.loads((folder / 'plan.json').read_text())
                        if 'rival' in plan:
                            row['label'] = f'{plan["policy_label"]} vs {plan["rival"]} · {folder.name}'
                    except (OSError, ValueError, KeyError):
                        pass
                    row['fetched'] = len(list((folder / 'artifacts').glob('*/.done')))
                    try:
                        row['audited'] = json.loads((folder / 'audit-progress.json').read_text())['verified']
                    except (OSError, ValueError, KeyError):
                        row['audited'] = 0
                return result

            def poll_forever(self):
                with client() as c:
                    while True:
                        receipts = {p for directory in options.watch_directory for p in directory.glob('**/batch/created.json')}
                        for receipt in receipts:
                            try:
                                request = json.loads(receipt.read_text())['id']
                                expected = json.loads((receipt.parent / 'request.json').read_text())['num_episodes']
                            except (OSError, ValueError, KeyError):
                                continue
                            with self.lock:
                                if request not in self.data:
                                    self.xreqs.append(request)
                                    self.data[request] = {'episodes': [], 'started': time.time()}
                                self.data[request]['artifact_folder'] = str(receipt.parent.parent)
                                self.data[request]['expected_episodes'] = expected
                        for request in list(self.xreqs):
                            with self.lock:
                                cached = self.data[request]
                                entries = cached.get('episodes', [])
                                if len(entries) == cached.get('expected_episodes') and all(e['status'] == 'completed' for e in entries):
                                    continue
                            try:
                                response = c.get(f'/v2/experience-requests/{request}/episodes')
                                response.raise_for_status()
                                entries = response.json()
                                entries = entries if isinstance(entries, list) else entries.get('episodes', [])
                                with self.lock:
                                    self.data[request]['episodes'] = entries
                                    self.data[request]['polled'] = time.time()
                                    self.data[request].pop('error', None)
                            except Exception as error:
                                with self.lock:
                                    self.data[request]['error'] = str(error)
                        time.sleep(dashboard.POLL_SECONDS)
        dashboard.State = WatchingState
        dashboard.PAGE = dashboard.PAGE.replace(
            'html += `<h2>${xreq}</h2>`;',
            'html += `<h2>${d.label || xreq}</h2><div class="stats">${xreq}</div>`;')
        dashboard.PAGE = dashboard.PAGE.replace(
            'if (d.rate_per_min) html +=',
            'if (d.audited !== undefined) html += ` &middot; ${d.fetched} artifacts collected &middot; ${d.audited} full replays verified`;\n    if (d.rate_per_min) html +=')
    dashboard.main()
