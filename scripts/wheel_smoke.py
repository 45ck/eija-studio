#!/usr/bin/env python3
"""Install the wheel into a temporary target and execute it outside the source tree.
Dependencies come from the current environment; this is not an offline clean-room install.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    wheel=next((ROOT/'dist').glob('eija_studio-*.whl'));checks=[]
    with zipfile.ZipFile(wheel) as archive:
        assert archive.testzip() is None
        for name in ['eija_studio/resources/web/index.html','eija_studio/resources/web/app.js','eija_studio/resources/web/app.css','eija_studio/resources/trusted_build.json']:
            assert name in archive.namelist(),name
        checks.append('wheel CRC and required resources')
    with tempfile.TemporaryDirectory(prefix='eija-wheel-') as tmp:
        tmp=Path(tmp);target=tmp/'installed'
        result=subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-index','--target',str(target),str(wheel)],cwd=tmp,capture_output=True,text=True)
        if result.returncode:raise RuntimeError('Wheel install failed')
        env=os.environ.copy();env['PYTHONPATH']=str(target)
        def run(args):
            result=subprocess.run([sys.executable,'-m','eija_studio',*args],cwd=tmp,env=env,capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            return result.stdout
        assert run(['--version']).strip()=='0.2.0'
        doctor=json.loads(run(['doctor']));assert doctor['release_fixture_matches'];checks.append('installed wheel source fixture matches')
        run(['demo','--out',str(tmp/'demo.json')]);export=json.loads((tmp/'demo.json').read_text());assert export['payload']['packet']['eligible']
        assert export['payload']['case']['decision'] is None;checks.append('installed offline demo verifies without approval')
        run(['check-export',str(tmp/'demo.json')]);checks.append('installed export integrity command')
        run(['compile',str(ROOT/'examples/excursion-candidate.json'),'--out',str(tmp/'compiled'),'--verify'])
        compiled=json.loads((tmp/'compiled/compiled.json').read_text());assert not compiled['policy_errors'];assert len(compiled['receipt']['artifact']['cells'])==125;checks.append('installed compiler creates actual 125-cell runtime receipt')
    report={'status':'PASS','mode':'wheel installed into temporary target; current environment dependencies reused','checks':checks,'clean_room_dependency_install':'NOT_RUN','live_provider_calls':0}
    (ROOT/'evidence/wheel-smoke-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
