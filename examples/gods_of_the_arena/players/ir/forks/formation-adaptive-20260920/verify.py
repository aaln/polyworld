"""Verify a standalone adaptive IR/BASIC pair and its frozen compiler."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import zipfile


def main():
    folder = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
    sha = lambda data: hashlib.sha256(data).hexdigest()
    read = lambda path: json.loads(path.read_text())
    m = read(folder/'compiler-manifest.json')
    assert sha((folder/'compiler.zip').read_bytes()) == m['compiler_zip_sha256']
    assert sha((folder/'contracts.json').read_bytes()) == m['contracts_sha256']
    with tempfile.TemporaryDirectory(prefix='formation-adaptive-ir-') as tmp:
        with zipfile.ZipFile(folder/'compiler.zip') as z:
            assert set(z.namelist()) == set(m['compiler_files'])
            for name, expected in m['compiler_files'].items():
                assert sha(z.read(name)) == expected
                assert not Path(name).is_absolute() and '..' not in Path(name).parts
            z.extractall(tmp)
        sys.path.insert(0, str(Path(tmp)/'examples/gods_of_the_arena/players/ir'))
        from binding import CONTRACTS, Contract
        for name, fields in read(folder/'contracts.json').items():
            for key in ('reads','writes','actions','memory'):
                fields[key] = tuple(fields[key])
            fields['parameters'] = {k: tuple(v) for k,v in fields['parameters'].items()}
            CONTRACTS[name] = Contract(**fields)
        from policy_ir import compile_policy, extract, digest, grounded
        p = runpy.run_path(str(folder/'policy.py'))['POLICY']
        assert p == read(folder/'policy.ir.json')
        source = compile_policy(p).encode()
        assert source == (folder/'policy.bas').read_bytes()
        assert sha(source) == m['source_sha256']
        assert extract(source.decode(), p) == p == read(folder/'extracted.ir.json')
        assert grounded(p) == read(folder/'semantics.json')
        manifest = read(folder/'manifest.json')
        assert digest(p) == manifest['policy_sha256']
        for name, expected in manifest['artifacts'].items():
            assert sha((folder/name).read_bytes()) == expected, name
        print(json.dumps({'verified': True, 'source_sha256': sha(source),
                          'policy_sha256': digest(p), 'compiler_modules': len(m['compiler_files'])}))


if __name__ == '__main__':
    main()
