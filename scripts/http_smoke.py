#!/usr/bin/env python3
"""Run the actual Uvicorn process over loopback TCP, then restart its persistent workspace."""
from __future__ import annotations
import json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]


def main():
    checks=[]
    with tempfile.TemporaryDirectory(prefix='eija-http-',dir=ROOT/'.tmp' if (ROOT/'.tmp').is_dir() else None,ignore_cleanup_errors=True) as tmp:
        tmp=Path(tmp);workspace=tmp/'workspace';case_id=None
        for cycle in (1,2):
            with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            log=tmp/f'server-{cycle}.log';env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
            with log.open('w+') as output:
                process=subprocess.Popen([sys.executable,'-m','eija_studio','serve','--workspace',str(workspace),'--port',str(port)],env=env,stdout=output,stderr=output)
                try:
                    url=None
                    for _ in range(100):
                        for line in log.read_text().splitlines():
                            if line.startswith('http://127.0.0.1:'):url=line
                        if url:
                            try:
                                with socket.create_connection(('127.0.0.1',port),timeout=.1):break
                            except OSError:pass
                        time.sleep(.1)
                    if not url:raise RuntimeError('Server startup failed')
                    base,token=url.split('#',1);headers={'Authorization':'Bearer '+token,'Origin':base.rstrip('/')}
                    with httpx.Client(base_url=base,trust_env=False,timeout=30) as client:
                        assert client.get('/').status_code==200
                        assert client.get('/assets/app.js').status_code==200
                        assert client.get('/assets/app.css').status_code==200
                        assert client.get('/api/status').status_code==401
                        def get(path):
                            r=client.get(path,headers=headers);assert r.status_code==200,r.text;return r.json()
                        def post(path,body):
                            r=client.post(path,headers=headers,json=body);assert r.status_code==200,r.text;return r.json()
                        if cycle==1:
                            c=post('/api/cases',{'request':'Let teachers sign off excursions.'});case_id=c['id'];root='/api/cases/'+case_id
                            c=post(root+'/propose',{'expected_version':c['version']})
                            c=post(root+'/select',{'expected_version':c['version'],'interpretation':'recommend_only'})
                            instance=post(root+'/preview',{'expected_version':c['version']})
                            for index,(actor,action) in enumerate([('teacher-assigned','Submit'),('teacher-assigned','Recommend'),('registrar','Approve')]):
                                result=post(root+'/execute',{'operation_id':f'smoke-{index}','actor_id':actor,'instance_id':instance['id'],'action':action,'expected_version':instance['version']});instance=result['instance']
                            assert instance['state']=='Approved';checks.append('actual TCP runtime journey commits')
                            c=post(root+'/verify',{'expected_version':c['version']});packet=get(root)['packet']
                            c=post(root+'/approve',{'expected_version':c['version'],'subject_hash':packet['subject_hash'],'answers':{q['id']:q['expected'] for q in packet['questions']},'acknowledge_unknowns':True})
                            c=post(root+'/apply',{'expected_version':c['version']});assert c['stage']=='APPLIED'
                            data=get(root+'/export');assert data['payload']['case']['decision'];checks.append('actual TCP review/apply/export')
                        else:
                            assert get('/api/cases/'+case_id)['case']['stage']=='APPLIED';assert get('/api/status')['baseline_version']==1
                            checks.append('server restart retains baseline and case')
                        checks.append(f'cycle {cycle}: assets and session gate')
                finally:
                    process.terminate()
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
    report={'status':'PASS','mode':'actual CLI/Uvicorn/loopback TCP, offline provider','checks':checks,'live_provider_calls':0,'browser_network_navigation':'NOT_TESTED_BY_THIS_SCRIPT'}
    (ROOT/'evidence/http-smoke-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
