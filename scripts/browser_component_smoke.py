#!/usr/bin/env python3
"""Actual Chromium DOM + unmodified application JS, bridged to FastAPI TestClient.

No browser navigation or security policy is changed. This is a component/in-process
integration test, NOT an unrestricted browser-network end-to-end test.
Requires Playwright + Chromium. Tests real application rendering and handlers.
"""
from __future__ import annotations
import argparse, json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--chromium',default='/usr/bin/chromium');args=parser.parse_args()
    from playwright.sync_api import sync_playwright
    from fastapi.testclient import TestClient
    from eija_studio.bootstrap import build_studio
    from eija_studio.interfaces.http import create_app
    web=ROOT/'src/eija_studio/resources/web';evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eija-component-') as temp:
        studio=build_studio(Path(temp));client=TestClient(create_app(studio,'component-session'),base_url='http://127.0.0.1:8765')
        def bridge(path,options):
            headers=dict(options.get('headers',{}));headers['Origin']='http://127.0.0.1:8765'
            response=client.request(options.get('method','GET'),path,headers=headers,content=options.get('body'))
            return {'ok':response.is_success,'status':response.status_code,'data':response.json()}
        checks=[]
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1512,'height':1100},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.expose_function('eijaComponentTransport',bridge)
            html=(web/'index.html').read_text().replace('<link rel="stylesheet" href="/assets/app.css">','').replace('<script src="/assets/app.js" defer></script>','')
            page.set_content(html)
            page.add_style_tag(content=(web/'app.css').read_text())
            page.evaluate('''() => {
              Object.defineProperty(window, 'sessionStorage', {value:{getItem:()=> 'component-session',setItem:()=>{}}});
              window.fetch=async(path,options={})=>{const r=await window.eijaComponentTransport(path,options);return {...r,json:async()=>r.data};};
              if(!crypto.randomUUID)crypto.randomUUID=()=> 'test-op-'+Date.now()+'-'+Math.random().toString(16).slice(2);
            }''')
            page.add_script_tag(content=(web/'app.js').read_text())
            page.wait_for_function("document.querySelector('#connection').textContent.includes('offline')")
            page.screenshot(path=str(evidence/'studio-start.png'),full_page=True)
            page.click('#create');page.wait_for_selector('#workspace:not([hidden])')
            page.wait_for_function("!document.body.hasAttribute('aria-busy')")
            page.click('#propose');page.wait_for_selector('.option')
            page.wait_for_function("!document.body.hasAttribute('aria-busy')")
            assert page.locator('.option').count()==3;checks.append('three explicit interpretations')
            page.get_by_role('button',name='Select this meaning',exact=True).click();page.wait_for_selector('#editor:not([hidden])')
            page.wait_for_function("!document.body.hasAttribute('aria-busy')")
            page.screenshot(path=str(evidence/'studio-change.png'),full_page=True)
            page.click('[data-tab="try"]');page.click('#reset')
            page.wait_for_function("document.querySelector('#runtime-state').textContent==='Draft' && !document.body.hasAttribute('aria-busy')")
            page.locator('#runtime-actions').get_by_role('button',name='Submit',exact=True).click()
            page.wait_for_function("document.querySelector('#runtime-state').textContent==='Submitted' && !document.body.hasAttribute('aria-busy')")
            page.select_option('#actor','teacher-unassigned');page.locator('#runtime-actions').get_by_role('button',name='Recommend',exact=True).click()
            page.wait_for_function("document.querySelector('#notice').textContent.includes('ASSIGNMENT_DENIED') && !document.body.hasAttribute('aria-busy')")
            assert page.locator('#runtime-state').inner_text()=='Submitted';checks.append('denial retains persisted state')
            page.screenshot(path=str(evidence/'studio-denied.png'),full_page=True)
            page.select_option('#actor','teacher-assigned');page.locator('#runtime-actions').get_by_role('button',name='Recommend',exact=True).click()
            page.wait_for_function("document.querySelector('#runtime-state').textContent==='Recommended' && !document.body.hasAttribute('aria-busy')")
            page.select_option('#actor','registrar');page.locator('#runtime-actions').get_by_role('button',name='Approve',exact=True).click()
            page.wait_for_function("document.querySelector('#runtime-state').textContent==='Approved' && !document.body.hasAttribute('aria-busy')")
            checks.append('teacher submits/recommends; registrar approves')
            page.click('[data-tab="impact"]');page.screenshot(path=str(evidence/'studio-impact.png'),full_page=True)
            page.click('[data-tab="evidence"]');page.click('#verify')
            page.wait_for_function("!document.querySelector('#approve').disabled && !document.body.hasAttribute('aria-busy')")
            page.screenshot(path=str(evidence/'studio-evidence.png'),full_page=True)
            for k,v in {'authority':'Registrar','assignment':'No','reject_entry':'Recommended'}.items():page.fill('#q-'+k,v)
            page.check('#acknowledge');page.click('#approve')
            page.wait_for_function("document.querySelector('#case-stage').textContent==='APPROVED' && !document.body.hasAttribute('aria-busy')")
            page.click('[data-tab="impact"]');page.select_option('#diagram-source','Submitted');page.click('#edit-state')
            page.wait_for_function("document.querySelector('#case-stage').textContent==='PREVIEW' && !document.body.hasAttribute('aria-busy')")
            page.click('[data-tab="evidence"]');assert page.locator('#apply').is_disabled()
            assert 'STALE' in page.locator('#claims').inner_text();checks.append('state-view edit invalidates receipt and decision')
            page.click('#verify');page.wait_for_function("!document.querySelector('#approve').disabled && !document.body.hasAttribute('aria-busy')")
            for k,v in {'authority':'Registrar','assignment':'No','reject_entry':'Submitted'}.items():page.fill('#q-'+k,v)
            page.check('#acknowledge');page.click('#approve');page.wait_for_function("!document.querySelector('#apply').disabled && !document.body.hasAttribute('aria-busy')")
            page.click('#apply');page.wait_for_function("document.querySelector('#case-stage').textContent==='APPLIED' && !document.body.hasAttribute('aria-busy')")
            checks.append('explicit exact-subject approval and local apply')
            c=studio.store.list_cases()[0];export=studio.export(c['id'])
            (evidence/'component-case-export.json').write_text(json.dumps(export,indent=2)+'\n')
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(evidence/'studio-mobile.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1');checks.append('390px viewport no document-level horizontal overflow')
            assert not errors,errors
            (evidence/'browser-component-report.json').write_text(json.dumps({'status':'PASS','mode':'Chromium DOM + FastAPI in-process transport bridge','checks':checks,'javascript_errors':errors,'network_e2e':'NOT_RUN_ENVIRONMENT_BROWSER_NAVIGATION_BLOCKED','download_button':'NOT_RUN','human_usability_study':'NOT_RUN','live_provider_calls':0},indent=2)+'\n')
            browser.close();client.close()
    print(json.dumps({'status':'PASS','mode':'component integration','checks':len(checks)},indent=2))

if __name__=='__main__':main()
