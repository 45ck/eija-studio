import ast, json
from pathlib import Path
from fastapi.testclient import TestClient
from eija_studio.interfaces.http import create_app


def client(studio):
    return TestClient(create_app(studio,"unit-test-token"),base_url="http://127.0.0.1:8765")
HEADERS={"Authorization":"Bearer unit-test-token","Origin":"http://127.0.0.1:8765"}


def test_session_host_origin_and_contract_guards(studio):
    with client(studio) as c:
        assert c.get("/api/status").status_code==401
        assert c.get("/api/status",headers=HEADERS).status_code==200
        assert c.get("/api/status",headers=HEADERS|{"Host":"attacker.invalid"}).status_code==403
        assert c.post("/api/cases",headers=HEADERS|{"Origin":"https://attacker.invalid"},json={"request":"x"}).status_code==403
        assert c.post("/api/cases",headers=HEADERS,json={"request":"x","approved":True}).status_code==422
        assert c.post("/api/cases",headers=HEADERS,content="x"*40000).status_code in (413,415)


def test_frontend_assets_have_csp_and_no_path_escape(studio):
    with client(studio) as c:
        r=c.get("/");assert r.status_code==200 and "frame-ancestors 'none'" in r.headers["content-security-policy"]
        assert c.get("/assets/app.js").status_code==200
        assert c.get("/assets/receipt.key").status_code==404
        assert c.get("/docs").status_code==404


def test_http_happy_path_and_direct_teacher_approval_denial(studio):
    with client(studio) as http:
        def post(path,body):
            response=http.post(path,json=body,headers=HEADERS)
            assert response.status_code==200,response.text
            return response.json()
        c=post("/api/cases",{"request":"Let teachers sign off excursions."});root="/api/cases/"+c["id"]
        c=post(root+"/propose",{"expected_version":c["version"]})
        c=post(root+"/select",{"expected_version":c["version"],"interpretation":"recommend_only"})
        instance=post(root+"/preview",{"expected_version":c["version"],"state":"Recommended"})
        denied=http.post(root+"/execute",headers=HEADERS,json={"operation_id":"no-approval","instance_id":instance["id"],"actor_id":"teacher-assigned","action":"Approve","expected_version":0})
        assert denied.status_code==409 and denied.json()["code"]=="ROLE_DENIED"
        c=post(root+"/verify",{"expected_version":c["version"]})
        packet=http.get(root,headers=HEADERS).json()["packet"]
        c=post(root+"/approve",{"expected_version":c["version"],"subject_hash":packet["subject_hash"],"answers":{q["id"]:q["expected"] for q in packet["questions"]},"acknowledge_unknowns":True})
        c=post(root+"/apply",{"expected_version":c["version"]});assert c["stage"]=="APPLIED"


def test_architecture_dependency_direction():
    root=Path(__file__).resolve().parents[1]/"src/eija_studio"
    for layer in ("domain","application"):
        for file in (root/layer).glob("*.py"):
            tree=ast.parse(file.read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.ImportFrom):
                    module=n.module or ""
                    assert not any(x in module for x in ("eija_studio.adapters","eija_studio.interfaces","fastapi","httpx","sqlite3")),(file,module)
                if isinstance(n,ast.Import):
                    assert all(x.name not in {"fastapi","httpx","sqlite3"} for x in n.names),(file,n)


def test_browser_never_interprets_provider_html():
    js=(Path(__file__).resolve().parents[1]/"src/eija_studio/resources/web/app.js").read_text()
    assert "innerHTML" not in js and "eval(" not in js
