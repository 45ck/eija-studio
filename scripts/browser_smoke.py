#!/usr/bin/env python3
"""Optional real-browser check. Needs playwright + a Chromium installation; no AI credentials used."""
from __future__ import annotations
import argparse, json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--chromium",default="/usr/bin/chromium");args=parser.parse_args()
    from playwright.sync_api import sync_playwright
    evidence=ROOT/"evidence";evidence.mkdir(exist_ok=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0));port=sock.getsockname()[1]
    checks=[]
    with tempfile.TemporaryDirectory(prefix="eija-browser-") as temp:
        log=Path(temp)/"server.log"; env=os.environ.copy();env["PYTHONPATH"]=str(ROOT/"src")
        with log.open("w+") as output:
            server=subprocess.Popen([sys.executable,"-m","eija_studio","serve","--workspace",str(Path(temp)/"workspace"),"--port",str(port)],env=env,stdout=output,stderr=output)
            try:
                url=None
                for _ in range(150):
                    text=log.read_text()
                    for line in text.splitlines():
                        if line.startswith("http://127.0.0.1:"):url=line
                    if url:
                        try:
                            with socket.create_connection(("127.0.0.1",port),timeout=.1):break
                        except OSError:pass
                    time.sleep(.1)
                if not url:raise RuntimeError("Server did not start")
                with sync_playwright() as p:
                    browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=["--no-sandbox"])
                    page=browser.new_page(viewport={"width":1512,"height":1100},device_scale_factor=1)
                    errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
                    page.goto(url);page.wait_for_function("document.querySelector('#connection').textContent.includes('offline')")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.screenshot(path=str(evidence/"studio-start.png"),full_page=True)
                    page.click("#create");page.wait_for_selector("#workspace:not([hidden])");page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.click("#propose");page.wait_for_selector(".option");page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    assert page.locator(".option").count()==3;checks.append("three explicit interpretations")
                    page.get_by_role("button",name="Select this meaning",exact=True).click()
                    page.wait_for_selector("#editor:not([hidden])");page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.screenshot(path=str(evidence/"studio-change.png"),full_page=True)
                    page.click('[data-tab="try"]');page.click("#reset")
                    page.wait_for_function("document.querySelector('#runtime-state').textContent==='Draft'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.locator("#runtime-actions").get_by_role("button",name="Submit",exact=True).click()
                    page.wait_for_function("document.querySelector('#runtime-state').textContent==='Submitted'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.select_option("#actor","teacher-unassigned")
                    page.locator("#runtime-actions").get_by_role("button",name="Recommend",exact=True).click()
                    page.wait_for_function("document.querySelector('#notice').textContent.includes('ASSIGNMENT_DENIED')")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    assert page.locator("#runtime-state").inner_text()=="Submitted";checks.append("denied recommendation does not fake success")
                    page.screenshot(path=str(evidence/"studio-denied.png"),full_page=True)
                    page.select_option("#actor","teacher-assigned")
                    page.locator("#runtime-actions").get_by_role("button",name="Recommend",exact=True).click()
                    page.wait_for_function("document.querySelector('#runtime-state').textContent==='Recommended'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.select_option("#actor","registrar")
                    page.locator("#runtime-actions").get_by_role("button",name="Approve",exact=True).click()
                    page.wait_for_function("document.querySelector('#runtime-state').textContent==='Approved'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    checks.append("persisted teacher-submit/recommend and registrar-approve journey")
                    page.click('[data-tab="impact"]');page.screenshot(path=str(evidence/"studio-impact.png"),full_page=True)
                    page.click('[data-tab="evidence"]');page.click("#verify")
                    page.wait_for_function("!document.querySelector('#approve').disabled")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.screenshot(path=str(evidence/"studio-evidence.png"),full_page=True)
                    for key,value in {"authority":"Registrar","assignment":"No","reject_entry":"Recommended"}.items():page.fill("#q-"+key,value)
                    page.check("#acknowledge");page.click("#approve")
                    page.wait_for_function("document.querySelector('#case-stage').textContent==='APPROVED'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.click('[data-tab="impact"]');page.select_option("#diagram-source","Submitted");page.click("#edit-state")
                    page.wait_for_function("document.querySelector('#case-stage').textContent==='PREVIEW'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.click('[data-tab="evidence"]')
                    assert page.locator("#apply").is_disabled()
                    assert "STALE" in page.locator("#claims").inner_text();checks.append("state-view semantic edit invalidates receipt and decision")
                    page.click("#verify");page.wait_for_function("!document.querySelector('#approve').disabled")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    for key,value in {"authority":"Registrar","assignment":"No","reject_entry":"Submitted"}.items():page.fill("#q-"+key,value)
                    page.check("#acknowledge");page.click("#approve");page.wait_for_function("!document.querySelector('#apply').disabled")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    page.click("#apply");page.wait_for_function("document.querySelector('#case-stage').textContent==='APPLIED'")
                    page.wait_for_function("!document.body.hasAttribute('aria-busy')")
                    checks.append("exact-subject approval and explicit local apply")
                    with page.expect_download() as d:page.click("#export")
                    download=d.value;download.save_as(str(evidence/"browser-case-export.json"))
                    checks.append("browser export download")
                    page.set_viewport_size({"width":390,"height":844})
                    page.screenshot(path=str(evidence/"studio-mobile.png"),full_page=True)
                    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth+1")
                    checks.append("390px viewport has no document-level horizontal overflow")
                    assert not errors,errors
                    report={"browser":"Chromium", "mode":"headless", "fixture":"synthetic excursion", "checks":checks,
                        "javascript_errors":errors,"status":"PASS","human_usability_study":"NOT_RUN","live_provider_calls":0}
                    (evidence/"browser-report.json").write_text(json.dumps(report,indent=2)+"\n")
                    browser.close()
            finally:
                server.terminate()
                try:server.wait(timeout=10)
                except subprocess.TimeoutExpired:server.kill();server.wait()
    print(json.dumps({"status":"PASS","checks":len(checks)},indent=2))

if __name__=="__main__":main()
