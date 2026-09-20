"""Freeze the actual loaded compiler and instantiated semantic bindings."""
from dataclasses import asdict
from pathlib import Path
import sys
import zipfile
import build
from build import STUDY, IR, CLEAN, read, write, digest
from binding import CONTRACTS


def main():
    # Register the exact admitted contracts using the original conversion path.
    # The builder checks every unchanged reference and exact final BASIC bytes.
    sys.argv = [__file__, '--prune']
    build.main()
    p = read(STUDY/'candidates/profile_pruned/policy.ir.json')
    folder = STUDY/'compiler'
    folder.mkdir(exist_ok=True)
    contracts = {s['operator']: asdict(CONTRACTS[s['operator']]) for s in p['skill'].values()}
    write(folder/'contracts.json', contracts)
    modules = sorted({Path(m.__file__).resolve() for m in list(sys.modules.values())
                      if getattr(m, '__file__', None) and
                      Path(m.__file__).resolve().is_relative_to(IR)})
    assert all(path.suffix == '.py' for path in modules)
    modules += [CLEAN/'examples/gods_of_the_arena'/name for name in ('content.nim','bots.nim','sim.nim')]
    modules += [CLEAN/'src/polyworld/basic.nim', CLEAN/'coworld/dependencies.lock']
    files = {str(path.relative_to(CLEAN)): digest(path.read_bytes()) for path in modules}
    with zipfile.ZipFile(folder/'compiler.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in modules:
            info = zipfile.ZipInfo(str(path.relative_to(CLEAN)), (2026, 9, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes())
    write(folder/'manifest.json', {'source_sha256': digest((STUDY/'candidates/profile_pruned/policy.bas').read_bytes()),
          'compiler_files': files, 'compiler_zip_sha256': digest((folder/'compiler.zip').read_bytes()),
          'contracts_sha256': digest((folder/'contracts.json').read_bytes()),
          'interpretation': 'Exact imported compiler modules plus instantiated contracts used by the repo conversion workflow. No policy source patch.'})
    print('Compiler snapshot:', len(files), 'modules', flush=True)


if __name__ == '__main__':
    main()
