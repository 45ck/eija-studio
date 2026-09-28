#!/usr/bin/env python3
"""Run local tests and inspect source identity; NEVER stamp changed source as trusted."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from eija_studio.adapters.identity import identity

def main():
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    result=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(evidence/'tests.xml')],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (evidence/'tests.log').write_text(result.stdout)
    current=identity();report={'tests_exit_code':result.returncode,'identity':current,'source_review':'SELF_AUTHORED_RELEASE_FIXTURE_MATCH' if current['trusted_fixture'] else 'SOURCE_REVIEW_REQUIRED','live_providers':'NOT_TESTED_BY_THIS_SCRIPT'}
    (evidence/'last-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result.stdout,end='');print(json.dumps(report,indent=2))
    return result.returncode or (0 if current['trusted_fixture'] else 2)

if __name__=='__main__':raise SystemExit(main())
