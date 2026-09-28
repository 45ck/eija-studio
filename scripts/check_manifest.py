#!/usr/bin/env python3
"""Check shipped file bytes, not author identity or correctness. No network access."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
def main():
    doc=json.loads((ROOT/'MANIFEST.json').read_text());errors=[]
    for entry in doc['files']:
        path=(ROOT/entry['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():errors.append(entry['path']);continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:errors.append(entry['path'])
    print(json.dumps({'status':'FAIL' if errors else 'PASS','checked_files':len(doc['files']),'mismatches':errors,'claim':'File integrity only; not authenticity or assurance'},indent=2))
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
