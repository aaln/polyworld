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
    parser.add_argument('--watch-directory', type=Path)
    options, rest = parser.parse_known_args()
    sys.argv = [sys.argv[0], *rest]
    if options.watch_directory:
        class WatchingState(dashboard.State):
            def poll_forever(self):
                with client() as c:
                    while True:
                        for receipt in options.watch_directory.glob('**/batch/created.json'):
                            try:
                                request = json.loads(receipt.read_text())['id']
                            except (OSError, ValueError, KeyError):
                                continue
                            with self.lock:
                                if request not in self.data:
                                    self.xreqs.append(request)
                                    self.data[request] = {'episodes': [], 'started': time.time()}
                        for request in list(self.xreqs):
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
    dashboard.main()
