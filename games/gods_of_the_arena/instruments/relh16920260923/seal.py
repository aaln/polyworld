"""Seal portable research files after publication, before verification/commit."""
from audit import OUT, ROOT, sha, write

rows = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name not in {'artifact-manifest.json', 'verification.json'} and '__pycache__' not in path.parts:
        rows.append({'path': str(path.relative_to(OUT)), 'sha256': sha(path)})
for path in sorted((ROOT / 'games/gods_of_the_arena/instruments/relh16920260923').glob('*')):
    if path.is_file():
        import os
        rows.append({'path': os.path.relpath(path, OUT), 'sha256': sha(path)})
write(OUT / 'artifact-manifest.json', rows)
print(f'Sealed {len(rows)} artifacts')
