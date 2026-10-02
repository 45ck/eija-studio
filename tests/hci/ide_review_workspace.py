"""Real browser review journeys with independent server-model and painted-SVG oracles.

No owner verification, approval, apply, live providers, or personal browser profile.
The separate source-freshness scenario mutates only its temporary Git fixture.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import socket
import tempfile
import traceback
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import self_dogfood_replay as replay
from case_preview_navigation import emit, write_json
from ide_journey_edges import Journey
from eija_studio.adapters.providers.process import resolve_command, run_bounded
from quality.hci.server import ROOT
from self_dogfood_subject import capture_subject, compare_subjects, file_identity


def subject_identity():
    subject = capture_subject(ROOT)
    for name in ("tests/hci/ide_review_workspace.py", "tests/hci/ide_journey_edges.py",
                 "tests/hci/case_preview_navigation.py", "quality/hci/server.py"):
        subject["scope"].append(name)
        subject["files"][name] = file_identity(ROOT, name)
    content = {name: item["sha256"] for name, item in subject["files"].items()}
    subject["content_sha256"] = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    return subject


OBSERVE_COMPARE = r"""board => {
    if (!board.matches('svg.compare-svg')) throw new Error('Expected one compare SVG');
    const xy = point => ({x:point.x, y:point.y});
    const box = rect => ({x:rect.x, y:rect.y, width:rect.width, height:rect.height});
    function matrix(element) {
        const value = element.getScreenCTM();
        if (!value || ![value.a,value.b,value.c,value.d,value.e,value.f].every(Number.isFinite)
            || Math.abs(value.a*value.d-value.b*value.c) < 1e-12)
            throw new Error('Unusable SVG screen transform');
        return value;
    }
    const boardMatrix = matrix(board), boardInverse = boardMatrix.inverse();
    function colorPainted(value) {
        return value !== 'none' && value !== 'transparent'
            && !/^rgba\([^,]+,[^,]+,[^,]+,\s*0(?:\.0+)?\s*\)$/.test(value)
            && !/\/\s*0(?:\.0+)?\s*\)$/.test(value);
    }
    function paint(element) {
        const style = getComputedStyle(element);
        let opacity = 1, displayed = element.isConnected;
        for (let current=element; current; current=current.parentElement) {
            const ancestor = getComputedStyle(current);
            opacity *= Number(ancestor.opacity);
            displayed = displayed && ancestor.display !== 'none';
        }
        const visible = displayed && style.visibility === 'visible' && opacity > 0;
        return {visible, opacity, stroke:style.stroke, stroke_width:parseFloat(style.strokeWidth),
            fill:style.fill, stroke_painted:visible && colorPainted(style.stroke)
                && Number(style.strokeOpacity)>0 && parseFloat(style.strokeWidth)>0,
            fill_painted:visible && colorPainted(style.fill) && Number(style.fillOpacity)>0};
    }
    function geometry(element) {
        const local = element.getBBox(), transform = matrix(element);
        const corners = [[local.x,local.y],[local.x+local.width,local.y],
            [local.x,local.y+local.height],[local.x+local.width,local.y+local.height]]
            .map(([x,y]) => new DOMPoint(x,y).matrixTransform(transform).matrixTransform(boardInverse));
        const xs=corners.map(p=>p.x), ys=corners.map(p=>p.y);
        return {local_box:box(local), screen_box:box(element.getBoundingClientRect()),
            graph_box:{x:Math.min(...xs),y:Math.min(...ys),
                width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys)},
            graph_center:xy(new DOMPoint(local.x+local.width/2,local.y+local.height/2)
                .matrixTransform(transform).matrixTransform(boardInverse)), paint:paint(element)};
    }
    function label(element) {
        return {text:element.textContent, font_size:parseFloat(getComputedStyle(element).fontSize),
            ...geometry(element)};
    }
    const nodes = [...board.querySelectorAll('.compare-node')].map(group => {
        const rects=[...group.querySelectorAll('rect.compare-state-box')];
        const labels=[...group.querySelectorAll('.compare-state-label')];
        if(rects.length!==1 || labels.length!==1) throw new Error('Ambiguous compare node shapes/labels');
        return {group, rect:rects[0], state:group.getAttribute('data-state'),
            id:group.getAttribute('data-eija-id'), initial:group.getAttribute('data-initial'),
            initial_labels:[...group.querySelectorAll('text.compare-initial-label')]
                .map(element=>({status_class:element.classList.contains('compare-status-label'), ...label(element)})),
            accessible:group.getAttribute('aria-label'), label:label(labels[0]), ...geometry(rects[0])};
    });
    function contacts(path, distance) {
        const screen = path.getPointAtLength(distance).matrixTransform(matrix(path));
        const hits = nodes.filter(node => node.rect.isPointInStroke(screen.matrixTransform(matrix(node.rect).inverse())));
        return {screen:xy(screen), graph:xy(screen.matrixTransform(boardInverse)),
            states:hits.map(node=>node.state).sort(), ids:hits.map(node=>node.id).sort()};
    }
    const documentIds=[...document.querySelectorAll('[id]')];
    function marker(path) {
        const reference=getComputedStyle(path).markerEnd;
        const match=/^url\(["']?([^"')]+)["']?\)$/.exec(reference);
        const id=match && match[1].includes('#') ? match[1].slice(match[1].lastIndexOf('#')+1) : null;
        const matches=id ? documentIds.filter(element=>element.id===id) : [];
        return {reference, attribute:path.getAttribute('marker-end'), id,
            matches:matches.map(element=>({tag:element.localName, within_svg:board.contains(element),
                width:element.markerWidth?.baseVal.value ?? null,
                height:element.markerHeight?.baseVal.value ?? null,
                orient:element.getAttribute('orient'),
                shapes:[...element.querySelectorAll('path,polygon,polyline,circle,rect')]
                    .map(shape=>({box:box(shape.getBBox()), paint:paint(shape)}))}))};
    }
    const edges=[...board.querySelectorAll('.compare-edge')].map(group => {
        const paths=[...group.querySelectorAll('path.compare-edge-line')];
        const labels=[...group.querySelectorAll('.compare-edge-label')];
        if(paths.length!==1 || labels.length!==1) throw new Error('Ambiguous compare edge paths/labels');
        const path=paths[0], length=path.getTotalLength();
        return {transition:group.getAttribute('data-transition'), id:group.getAttribute('data-eija-id'),
            accessible:group.getAttribute('aria-label'), label:label(labels[0]),
            path_id:path.id, d:path.getAttribute('d'), length, paint:paint(path),
            source:contacts(path,0), target:contacts(path,length), marker:marker(path)};
    });
    return {svg:{id:board.id, view_box:board.getAttribute('viewBox'), screen_box:box(board.getBoundingClientRect()),
                paint:paint(board), ids:[board,...board.querySelectorAll('[id]')].filter(el=>el.id).map(el=>el.id)},
        document_svg_ids:[...document.querySelectorAll('svg[id], svg [id]')].map(element=>element.id),
        initial_label_count:board.querySelectorAll('text.compare-initial-label').length,
        nodes:nodes.map(({group,rect,...record})=>record), edges};
}"""


def observe_compare(svg):
    """Use a side-scoped Playwright locator resolving to exactly one compare SVG."""
    assert svg.count() == 1, "svg_inventory: expected exactly one comparison SVG"
    return svg.evaluate(OBSERVE_COMPARE)


def _workflow_index(model):
    states = model["states"]
    transitions = model["transitions"]
    assert len(states) == len(set(states)), "server_model: duplicate state"
    assert model["initial_state"] in states, "server_model: missing initial state"
    ids = [transition["id"] for transition in transitions]
    assert len(ids) == len(set(ids)), "server_model: duplicate transition"
    assert all(t["from_state"] in states and t["to_state"] in states for t in transitions), "server_model: dangling endpoint"
    return {transition["id"]: transition for transition in transitions}


def semantic_inventory(before, after):
    """Changed-element mapping keyed state:ID, transition:ID, initial:initial_state.

    Every value has kind/id/status/before/after/fields. State and initial values
    are names (or None for an absent side); transitions retain full server JSON.
    Unchanged elements are omitted. Definition and guard/effect order is ignored.
    """
    left, right = _workflow_index(before), _workflow_index(after)
    assert before["id"] == after["id"], "inventory_identity: comparing different workflow packs"
    set_fields = {"guards", "required_effects", "forbidden_effects"}
    inventory = {}
    for state in sorted(set(before["states"]) ^ set(after["states"])):
        added = state in after["states"]
        inventory["state:" + state] = {"kind": "state", "id": state,
            "status": "added" if added else "removed", "before": None if added else state,
            "after": state if added else None, "fields": {}}
    if before["initial_state"] != after["initial_state"]:
        values = {"before": before["initial_state"], "after": after["initial_state"]}
        inventory["initial:initial_state"] = {"kind": "initial", "id": "initial_state",
            "status": "changed", **values, "fields": {"initial_state": dict(values)}}
    for identity in sorted(left.keys() ^ right.keys()):
        inventory["transition:" + identity] = {"kind": "transition", "id": identity,
            "status": "added" if identity in right else "removed", "before": deepcopy(left.get(identity)),
            "after": deepcopy(right.get(identity)), "fields": {}}
    for identity in sorted(left.keys() & right.keys()):
        fields = {}
        for field in sorted(left[identity].keys() | right[identity].keys()):
            a, b = left[identity].get(field), right[identity].get(field)
            equal = set(a) == set(b) if field in set_fields else a == b
            if not equal:
                fields[field] = {"before": deepcopy(a), "after": deepcopy(b)}
        if fields:
            inventory["transition:" + identity] = {"kind": "transition", "id": identity,
                "status": "changed", "before": deepcopy(left[identity]),
                "after": deepcopy(right[identity]), "fields": fields}
    return dict(sorted(inventory.items()))


def _positive_box(box, context):
    assert all(math.isfinite(box[key]) for key in ("x", "y", "width", "height")), f"{context}: nonfinite box"
    assert box["width"] > 0 and box["height"] > 0, f"{context}: empty box"


def _assert_label(label, expected, context):
    assert label["text"] == expected, f"{context}: expected {expected!r}, got {label['text']!r}"
    assert label["paint"]["fill_painted"] or label["paint"]["stroke_painted"], f"{context}: unpainted text"
    _positive_box(label["screen_box"], context)
    assert math.isfinite(label["font_size"]) and label["font_size"] > 0, f"{context}: invalid font size"


def assert_graph(model, observed):
    """Assert side-specific inventory, painted initial label and geometric topology."""
    expected = _workflow_index(model)
    nodes, edges = observed["nodes"], observed["edges"]
    assert sorted(node["state"] for node in nodes) == sorted(model["states"]), "node_inventory: missing, extra or duplicate node"
    assert sorted(edge["transition"] for edge in edges) == sorted(expected), "edge_inventory: missing, extra or duplicate edge"
    ids = observed["document_svg_ids"]
    assert len(ids) == len(set(ids)), "svg_ids: duplicate document SVG IDs"
    assert observed["svg"]["paint"]["visible"], "svg_paint: hidden graph"
    _positive_box(observed["svg"]["screen_box"], "svg_paint")
    assert observed["initial_label_count"] == 1, "initial_label: exactly one painted initial label required"
    assert sum(len(node["initial_labels"]) for node in nodes) == 1, "initial_label: marker outside or duplicated across nodes"
    for node in nodes:
        state = node["state"]
        assert node["id"] == "state:" + state, f"node_identity: {state}"
        assert node["initial"] in (None, "false", "true"), f"initial_marker: unrecognised encoding {node['initial']!r}"
        assert (node["initial"] == "true") == (state == model["initial_state"]), f"initial_marker: {state}"
        initial_labels = node["initial_labels"]
        assert len(initial_labels) == int(state == model["initial_state"]), f"initial_label: wrong node {state}"
        if initial_labels:
            initial_label = initial_labels[0]
            prefix = "● Initial · "
            assert initial_label["status_class"], "initial_label: missing comparison status class"
            assert initial_label["text"].startswith(prefix) and initial_label["text"][len(prefix):].strip(), "initial_label: missing initial prefix or status"
            _assert_label(initial_label, initial_label["text"], "initial_label")
            inner, outer = initial_label["screen_box"], node["screen_box"]
            assert (inner["x"] >= outer["x"] - 1 and inner["y"] >= outer["y"] - 1
                    and inner["x"] + inner["width"] <= outer["x"] + outer["width"] + 1
                    and inner["y"] + inner["height"] <= outer["y"] + outer["height"] + 1), "initial_label: painted text outside its state box"
        _assert_label(node["label"], state, "node_label")
        assert node["paint"]["stroke_painted"], f"node_paint: {state} has no painted border"
        _positive_box(node["screen_box"], "node_paint")
        assert all(math.isfinite(node["graph_center"][axis]) for axis in ("x", "y")), f"node_geometry: {state}"
    for edge in edges:
        transition = expected[edge["transition"]]
        _assert_label(edge["label"], transition["action"], "edge_label")
        assert edge["d"] and math.isfinite(edge["length"]) and edge["length"] > 0, "edge_geometry: empty path"
        assert edge["paint"]["stroke_painted"], "edge_paint: unpainted path"
        for endpoint, field in (("source", "from_state"), ("target", "to_state")):
            wanted = transition[field]
            actual = edge[endpoint]
            assert actual["states"] == [wanted], f"edge_contact: {transition['id']} {endpoint}: expected {wanted!r}, got {actual['states']!r}"
            assert actual["ids"] == ["state:" + wanted], f"edge_contact: {transition['id']} {endpoint} identity"
            assert all(math.isfinite(actual[space][axis]) for space in ("screen", "graph") for axis in ("x", "y")), "edge_geometry: nonfinite endpoint"
        marker = edge["marker"]
        assert marker["id"] and re.fullmatch(r"url\(.+\)", marker["reference"]), "edge_marker: missing marker-end reference"
        assert len(marker["matches"]) == 1, "edge_marker: unresolved or ambiguous marker ID"
        definition = marker["matches"][0]
        assert definition["tag"] == "marker" and definition["within_svg"], "edge_marker: marker belongs to another graph"
        assert definition["width"] > 0 and definition["height"] > 0, "edge_marker: empty marker viewport"
        assert any(shape["box"]["width"] > 0 and shape["box"]["height"] > 0
                   and (shape["paint"]["fill_painted"] or shape["paint"]["stroke_painted"])
                   for shape in definition["shapes"]), "edge_marker: no painted arrow shape"


def graph_negative_controls(model, observed):
    """Pure comparator sensitivity; these copied observations are not browser evidence."""
    assert_graph(model, observed)
    assert observed["nodes"] and observed["edges"], "negative_setup: nonempty fixture required"
    mutations = {}
    missing = deepcopy(observed)
    missing["nodes"].pop()
    mutations["missingnode"] = (missing, "node_inventory:")
    duplicate = deepcopy(observed)
    duplicate["edges"].append(deepcopy(duplicate["edges"][0]))
    mutations["dupeedge"] = (duplicate, "edge_inventory:")
    swapped = deepcopy(observed)
    edge = next((item for item in swapped["edges"] if item["source"]["states"] != item["target"]["states"]), None)
    assert edge is not None, "negative_setup: one non-loop edge required for swapped-contact control"
    edge["source"], edge["target"] = edge["target"], edge["source"]
    mutations["swappedcontact"] = (swapped, "edge_contact:")
    wrong = deepcopy(observed)
    wrong["edges"][0]["label"]["text"] += " [incorrect]"
    mutations["wronglabel"] = (wrong, "edge_label:")
    missing_initial = deepcopy(observed)
    initial = next(node for node in missing_initial["nodes"] if node["state"] == model["initial_state"])
    initial["initial_labels"] = []
    missing_initial["initial_label_count"] = 0
    mutations["missing_initial_label"] = (missing_initial, "initial_label:")
    moved_initial = deepcopy(observed)
    initial = next(node for node in moved_initial["nodes"] if node["state"] == model["initial_state"])
    other = next((node for node in moved_initial["nodes"] if node["state"] != model["initial_state"]), None)
    assert other is not None, "negative_setup: second state required for moved initial-label control"
    other["initial_labels"], initial["initial_labels"] = initial["initial_labels"], []
    mutations["moved_initial_label"] = (moved_initial, "initial_label:")
    detected = {}
    for name, (mutant, expected_reason) in mutations.items():
        try:
            assert_graph(model, mutant)
        except AssertionError as error:
            assert str(error).startswith(expected_reason), f"negative_reason: {name} failed for another reason: {error}"
            detected[name] = {"detected": True, "reason": str(error)}
        else:
            raise AssertionError(f"negative_missed: {name} was accepted")
    return detected


VISIBLE_SELECTION = r"""(board, expected) => {
    const box = node => {const r=node.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
    const clipped={left:0,top:0,right:innerWidth,bottom:innerHeight};
    function intersect(r,x,y){if(x){clipped.left=Math.max(clipped.left,r.left);clipped.right=Math.min(clipped.right,r.right);}
      if(y){clipped.top=Math.max(clipped.top,r.top);clipped.bottom=Math.min(clipped.bottom,r.bottom);}}
    intersect(board.getBoundingClientRect(),true,true);
    for(let parent=board.parentElement;parent;parent=parent.parentElement){
      const style=getComputedStyle(parent),rect=parent.getBoundingClientRect();
      intersect(rect,/(auto|scroll|hidden|clip)/.test(style.overflowX),/(auto|scroll|hidden|clip)/.test(style.overflowY));
    }
    const states=[...new Set([expected.from_state,expected.to_state])].map(id=>{
      const node=[...board.querySelectorAll('g.compare-node')].find(n=>n.dataset.state===id);
      if(!node)throw new Error('Selected endpoint missing: '+id);
      return {id,box:box(node.querySelector('rect.compare-state-box')),label:box(node.querySelector('.compare-state-label'))};
    });
    const edge=[...board.querySelectorAll('g.compare-edge')].find(n=>n.dataset.transition===expected.id);
    if(!edge)throw new Error('Selected transition missing: '+expected.id);
    const label=edge.querySelector('.compare-edge-label');
    return {viewport:{width:innerWidth,height:innerHeight},clip:clipped,states,action:{text:label.textContent,box:box(label)},viewBox:board.getAttribute('viewBox')};
}"""


def assert_visible_selection(expected, observed):
    clip = observed["clip"]
    assert clip["right"] > clip["left"] and clip["bottom"] > clip["top"], "Selected graph has no visible viewport."
    assert observed["action"]["text"] == expected["action"]
    boxes = [(item["id"], item["box"]) for item in observed["states"]]
    boxes.append(("action:" + expected["action"], observed["action"]["box"]))
    for label, box in boxes:
        assert (box["x"] >= clip["left"] - 1 and box["y"] >= clip["top"] - 1
                and box["x"] + box["width"] <= clip["right"] + 1
                and box["y"] + box["height"] <= clip["bottom"] + 1), {
            "reason": "Focus selection clips a required endpoint or action", "element": label, "box": box, "clip": clip}
    return observed


class ReviewWorkspace(Journey):
    def __init__(self, page, out, base):
        super().__init__(page, out, base)
        self.fail_next = None
        self.injected = []
        self.graph_records = []
        self.source_records = []
        self.comparison_selection = None

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"verify", "approve", "apply", "export"}:
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            self.forbidden.append(path)
            route.abort()
        elif request.method == "GET" and path == self.fail_next:
            self.fail_next = None
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            self.injected.append({"stage": self.stage, "status": 503, "path": path})
            route.fulfill(status=503, content_type="application/json", body=json.dumps({
                "code": "REVIEW_FIXTURE_UNAVAILABLE", "message": "Regression fixture: case refresh failed once.",
            }))
        else:
            super().route(route)

    def case_view(self):
        value = self.get("cases/" + self.case_id)
        assert value["case"]["id"] == self.case_id
        return value

    def chosen(self, key):
        self.tab("review")
        self.page.locator(f'[data-compare-key="{key}"]').click()
        kind, ident = key.split(":", 1)
        self.comparison_selection = (kind, ident)
        detail = self.page.locator(".compare-selection")
        replay.expect(detail).to_have_attribute("data-kind", kind)
        replay.expect(detail).to_have_attribute("data-id", ident)
        return detail

    def assert_identity(self, view):
        pair = self.page.locator(".paired-compare")
        replay.expect(pair).to_have_attribute("data-case", view["case"]["id"])
        replay.expect(pair).to_have_attribute("data-revision", str(view["case"]["version"]))
        assert self.packet() == view["packet"], "Displayed current evidence packet differs from the server."

    def assert_inventory(self, view):
        expected = semantic_inventory(view["case"]["baseline"], view["case"]["candidate"])
        actual = self.page.locator("[data-compare-key]").evaluate_all("nodes => nodes.map(n => n.dataset.compareKey)")
        models = (view["case"]["baseline"], view["case"]["candidate"])
        all_keys = {"state:" + state for model in models for state in model["states"]}
        all_keys |= {"transition:" + entry["id"] for model in models for entry in model["transitions"]}
        all_keys.add("initial:initial_state")
        assert sorted(actual) == sorted(all_keys), {"expected": sorted(all_keys), "actual": actual}
        visible = self.page.locator("[data-compare-key]:visible").evaluate_all("nodes => nodes.map(n => n.dataset.compareKey)")
        assert sorted(visible) == sorted(expected), {"expected_changes": expected, "visible": visible}
        return expected

    def observe_pair(self, view, label):
        self.assert_identity(view)
        records = {}
        for side, field in (("before", "baseline"), ("after", "candidate")):
            board = self.page.locator(f'[data-compare-side="{side}"] svg.compare-svg')
            replay.expect(board).to_be_visible()
            observed = board.evaluate(OBSERVE_COMPARE)
            assert_graph(view["case"][field], observed)
            records[side] = observed
        ids = self.page.locator(".paired-compare svg [id]").evaluate_all("nodes => nodes.map(n => n.id)")
        assert len(ids) == len(set(ids)), "Simultaneous diagrams have colliding SVG IDs."
        self.graph_records.append({"label": label, "case": view["case"]["id"], "revision": view["case"]["version"],
                                   "models": {k: view["case"][k] for k in ("baseline", "candidate")}, "observed": records})
        return records

    def source_edit(self, transition, state, end="source"):
        choices = self.get(f"cases/{self.case_id}/affordances")["affordances"]
        wanted = [x for x in choices if x["element"] == "transition:" + transition and x["kind"] == "retarget_" + end
                  and x["target"] == "state:" + state]
        assert len(wanted) == 1 and wanted[0]["legal"] is True, wanted
        before = self.case_view()
        self.tab("model")
        self.page.locator("#transition-select").select_option(transition)
        control = "#model-source" if end == "source" else "#target-state"
        self.page.locator(control).select_option(state)
        self.page.locator("#edit-" + end).click()
        self.settled()
        after = self.case_view()
        expected = deepcopy(before["case"]["candidate"])
        next(t for t in expected["transitions"] if t["id"] == transition)["from_state" if end == "source" else "to_state"] = state
        assert after["case"]["candidate"] == expected
        assert after["case"]["baseline"] == before["case"]["baseline"]
        assert after["case"]["version"] == before["case"]["version"] + 1
        assert after["case"]["transactions"] == [*before["case"]["transactions"], wanted[0]["transaction"]]
        return after

    def prepare(self):
        self.entry()
        self.shot("first-entry")
        emit({"milestone": "normal-csp-entry", "screenshot": str(self.out / "first-entry.png"), "javascript_errors": self.errors})
        self.create_candidate()
        self.case_a = self.case_id
        before = self.snapshot()
        choice = self.edit_role("TR-SAVE", "Agent")
        self.assert_role_edit(before, "TR-SAVE", "Agent", choice["transaction"])
        view = self.source_edit("TR-VERIFY", "SAVED")
        self.connection = self.get("workbench")["connection"]
        assert self.connection["status"] == "connected"
        self.current_a = self.snapshot()
        self.chosen("transition:TR-VERIFY")
        expected = self.assert_inventory(view)
        detail = self.page.locator('.compare-selection [data-field="from_state"]')
        assert detail.locator("td").all_text_contents() == ["PREVIEW", "SAVED"]
        return {"case": self.case_a, "revision": view["case"]["version"], "inventory": expected,
                "parallel_edges": ["TR-VERIFY", "TR-VERIFY-SAVED"], "source_connection": self.connection["source_hash"]}

    def paired_graphs(self):
        before = self.snapshot()
        view = self.case_view()
        self.page.locator('[data-compare-action="overview"]').click()
        pair = self.observe_pair(view, "parallel-overview")
        controls = {side: graph_negative_controls(view["case"][field], pair[side])
                    for side, field in (("before", "baseline"), ("after", "candidate"))}
        board = self.page.locator('[data-compare-side="after"] svg.compare-svg')
        line = board.locator('[data-transition="TR-VERIFY"] path.compare-edge-line')
        actual_path = line.get_attribute("d")
        rejected = None
        try:
            # A planted painted-path defect only; authoritative model data and labels stay intact.
            line.evaluate("node => node.setAttribute('d', 'M 0 0 L 1 1')")
            mutated = board.evaluate(OBSERVE_COMPARE)
            try:
                assert_graph(view["case"]["candidate"], mutated)
            except AssertionError as error:
                assert str(error).startswith("edge_contact:"), str(error)
                rejected = str(error)
            assert rejected, "The oracle accepted a visibly wrong painted transition."
        finally:
            line.evaluate("(node, value) => node.setAttribute('d', value)", actual_path)
        self.observe_pair(view, "painted-negative-control-restored")
        self.chosen("transition:TR-SAVE")
        replay.expect(self.page.locator('[data-compare-side="before"] .compare-presence')).to_contain_text("Not present")
        replay.expect(self.page.locator('[data-compare-side="before"] [data-transition="TR-SAVE"]')).to_have_count(0)
        replay.expect(self.page.locator('[data-compare-side="after"] [data-transition="TR-SAVE"]')).to_have_count(1)
        replay.expect(self.page.locator(".compare-selection")).to_contain_text("Source binding unknown")
        replay.expect(self.page.locator(".compare-selection [data-compare-reference]")).to_have_count(0)
        self.chosen("state:SAVED")
        replay.expect(self.page.locator('[data-compare-side="before"] .compare-presence')).to_contain_text("Not present")
        self.chosen("transition:TR-VERIFY")
        boards = self.page.locator("svg.compare-svg")
        old = [boards.nth(i).get_attribute("viewBox") for i in range(2)]
        self.page.locator('[data-compare-action="zoom-in"]').click()
        new = [boards.nth(i).get_attribute("viewBox") for i in range(2)]
        assert new[0] == new[1] and old != new, "Paired zoom did not synchronously change actual SVG viewports."
        self.observe_pair(view, "parallel-zoomed")
        replay.expect(self.page.locator(".compare-selection")).to_have_attribute("data-id", "TR-VERIFY")
        visible_focus = []
        for width, height in ((1600, 1100), (1280, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.page.locator('[data-compare-action="focus"]').click()
            replay.expect(self.page.locator(".paired-compare")).to_have_attribute("data-compare-view", "focus")
            self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            for side, field in (("before", "baseline"), ("after", "candidate")):
                expected = next(item for item in view["case"][field]["transitions"] if item["id"] == "TR-VERIFY")
                board = self.page.locator(f'[data-compare-side="{side}"] svg.compare-svg')
                observed = board.evaluate(VISIBLE_SELECTION, expected)
                visible_focus.append({"side": side, "observed": assert_visible_selection(expected, observed),
                                      "displayed_scale": self.page.locator("output[data-compare-scale]").inner_text()})
            self.shot(f"selected-endpoints-{width}")
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        self.page.locator('[data-compare-action="focus"]').click()
        self.assert_unchanged(before)
        return {"oracle_controls": controls, "painted_endpoint_negative_control": rejected,
                "visible_selected_endpoints": visible_focus,
                "viewboxes_before": old, "viewboxes_after": new,
                "absent_side_has_no_ghost": True, "case_layout_history_unchanged": True}

    def exact_source(self):
        before = self.snapshot()
        view = self.case_view()
        self.chosen("transition:TR-VERIFY")
        workbench = self.get("workbench")
        term = next(t for t in workbench["language"]["terms"] if "transition:TR-VERIFY" in t.get("refs", []))
        reference = "repo://src/eija_studio/application/service.py#Studio.verify"
        assert reference in term["binds"]
        with self.page.expect_response(lambda r: urlsplit(r.url).path == "/api/repository/source") as pending:
            self.page.locator(f'[data-compare-reference="{reference}"]').click()
        self.settled()
        replay.expect(self.page.locator("#source-reader .source-lines")).to_be_visible()
        source = self.get("repository/source?" + urlencode({"reference": reference, "expected_source_hash": self.connection["source_hash"]}))
        assert pending.value.status == 200 and pending.value.json() == source
        assert parse_qs(urlsplit(pending.value.url).query)["expected_source_hash"] == [self.connection["source_hash"]]
        assert source["status"] == "connected" and source["reference"] == reference
        for key in ("source_hash", "graph_hash"):
            assert source[key] == workbench["connection"][key] == self.connection[key]
        assert source["file_hash"] == workbench["connection"]["file_hashes"][source["path"]]
        assert source["pack_digest"] == workbench["pack"]["digest"]
        assert hashlib.sha256(source["text"].encode()).hexdigest() == source["snippet_hash"]
        expected_lines = source["text"].replace("\r\n", "\n").split("\n")
        if expected_lines[-1] == "":
            expected_lines.pop()
        assert self.page.locator("#source-reader .source-line code").all_text_contents() == [line or " " for line in expected_lines]
        assert self.page.locator("#source-reader .line-number").all_text_contents() == [str(source["lines"]["start"] + i) for i in range(len(expected_lines))]
        replay.expect(self.page.locator("#source-reference")).to_have_value(reference)
        self.page.locator("#source-metadata summary").click()
        for key in ("file_hash", "snippet_hash", "source_hash", "graph_hash"):
            replay.expect(self.page.locator("#source-metadata")).to_contain_text(source[key])
        self.source_records.append(source)
        self.tab("review")
        replay.expect(self.page.locator(".compare-selection")).to_have_attribute("data-id", "TR-VERIFY")
        self.assert_identity(view)
        self.assert_unchanged(before)
        return {"reference": reference, "source": source, "selection_restored": True, "read_only": True}

    def assert_evidence(self, view, displayed="working"):
        packet = view["packet"]
        replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        assert packet["human_understanding"] == "UNKNOWN" and "SOURCE_REVIEW_REQUIRED" in packet["blockers"]
        subject = self.page.locator("#evidence-subject")
        replay.expect(subject).to_have_attribute("data-case-id", view["case"]["id"])
        replay.expect(subject).to_have_attribute("data-revision", str(view["case"]["version"]))
        replay.expect(subject).to_have_attribute("data-subject-hash", packet["subject_hash"])
        replay.expect(subject).to_have_attribute("data-displayed-model", displayed)
        assert self.comparison_selection is not None
        kind, ident = self.comparison_selection
        replay.expect(subject).to_have_attribute("data-comparison-case-id", view["case"]["id"])
        replay.expect(subject).to_have_attribute("data-comparison-revision", str(view["case"]["version"]))
        replay.expect(subject).to_have_attribute("data-comparison-kind", kind)
        replay.expect(subject).to_have_attribute("data-comparison-id", ident)
        replay.expect(subject).to_contain_text(f"Comparison selection: {kind} · {ident}")
        human = self.page.locator("#evidence .human-status")
        replay.expect(human).to_be_visible()
        replay.expect(human).to_contain_text("Human comprehension: " + packet["human_understanding"])
        assert self.page.locator("#claims [data-claim]").count() == len(packet["technical_claims"])
        for name, status in packet["technical_claims"].items():
            row = self.page.locator(f'#claims [data-claim="{name}"] .claim-status')
            replay.expect(row).to_be_visible()
            replay.expect(row).to_have_text(status)
        assert self.page.locator("#formal details[data-evidence-kind]").count() == len(packet["formal_evidence"])
        for item in packet["formal_evidence"]:
            summary = self.page.locator(f'#formal details[data-evidence-kind="{item["kind"]}"] summary').first
            replay.expect(summary).to_be_visible()
            replay.expect(summary).to_contain_text(item["status"])
        for blocker in packet["blockers"]:
            replay.expect(self.page.locator("#blockers")).to_contain_text(blocker)
        assert self.packet() == packet
        replay.expect(self.page.locator("#approve")).to_be_disabled()
        replay.expect(self.page.locator("#apply")).to_be_disabled()

    def focus_recovery(self):
        before = self.snapshot()
        view = self.case_view()
        replay.expect(self.page.locator("#transition-select")).to_have_value("TR-VERIFY")
        self.chosen("transition:TR-SAVE")
        replay.expect(self.page.locator("#transition-select")).to_have_value("TR-VERIFY")
        self.page.locator('[data-compare-action="evidence"]').click()
        self.assert_evidence(view)
        replay.expect(self.page.locator("#evidence-subject")).to_contain_text("Model inspector selection: transition · TR-VERIFY")
        controls = ("#toggle-explorer", "#toggle-inspector", "#toggle-bottom")
        panes = {key: self.page.locator(key).get_attribute("aria-expanded") for key in controls}
        self.page.locator("#focus-evidence").click()
        replay.expect(self.page.locator("body")).to_have_attribute("data-workspace-focused", "true")
        assert all(self.page.locator(key).get_attribute("aria-expanded") == "false" for key in controls)
        self.page.locator("#layout-summary").click()
        self.page.locator("#toggle-explorer").click()
        replay.expect(self.page.locator("#layout-summary")).to_be_focused()
        self.tab("review")
        self.tab("evidence")
        replay.expect(self.page.locator("#toggle-explorer")).to_have_attribute("aria-expanded", "true")
        self.assert_evidence(view)
        self.fail_next = "/api/cases/" + self.case_id
        self.palette("Refresh current model")
        assert self.fail_next is None
        replay.expect(self.page.locator("#error-json")).to_contain_text("REVIEW_FIXTURE_UNAVAILABLE")
        replay.expect(self.page.locator("#problems-pane")).to_be_visible()
        replay.expect(self.page.locator("#toggle-bottom")).to_have_attribute("aria-expanded", "true")
        self.assert_evidence(view)
        self.assert_unchanged(before)
        self.shot("focused-refresh-error")
        with self.page.expect_response(lambda r: r.request.method == "GET" and urlsplit(r.url).path == "/api/cases/" + self.case_id) as pending:
            self.palette("Refresh current model")
        assert pending.value.status == 200 and pending.value.json() == view
        replay.expect(self.page.locator("#error-details")).to_be_hidden()
        replay.expect(self.page.locator("#problems")).not_to_contain_text("REVIEW_FIXTURE_UNAVAILABLE")
        self.assert_evidence(view)
        self.page.locator("#restore-workspace").click()
        replay.expect(self.page.locator("body")).to_have_attribute("data-workspace-focused", "false")
        replay.expect(self.page.locator("#focus-evidence")).to_be_focused()
        assert {key: self.page.locator(key).get_attribute("aria-expanded") for key in controls} == panes
        self.assert_unchanged(before)
        return {"packet_statuses_preserved": True, "normal_panes_restored": panes,
                "explicit_open_survives_navigation": True, "error_and_retry": True}

    def historical_context(self):
        before = self.snapshot()
        history = before["history"]
        assert history["case_id"] == self.case_id and history["edits"][-1]["model"] == before["case"]["candidate"]
        self.palette("Show local case history")
        self.page.locator("#case-history .history-row").first.get_by_role("button", name="View model", exact=True).click()
        replay.expect(self.page.locator("#model-version")).to_have_value("history")
        replay.expect(self.page.locator("#edit-role")).to_be_disabled()
        self.canvas_matches(history["selection"]["model"])
        self.tab("evidence")
        self.assert_evidence(self.case_view(), displayed="history")
        replay.expect(self.page.locator("#evidence-subject")).to_contain_text("histor")
        self.tab("review")
        self.assert_identity(self.case_view())
        self.observe_pair(self.case_view(), "current-pair-while-historical-model-selected")
        self.tab("model")
        self.page.locator("#model-version").select_option("working")
        self.canvas_matches(before["case"]["candidate"])
        self.assert_unchanged(before)
        return {"history_hash": history["selection"]["semantic_hash"], "current_packet_subject": self.case_view()["packet"]["subject_hash"],
                "historical_model_not_current_evidence": True}

    def loop_and_cross_case(self):
        before_a = self.snapshot()
        self.create_candidate()
        self.case_b = self.case_id
        view_b = self.source_edit("TR-SAVE", "PREVIEW", end="target")
        before_b = self.snapshot()
        self.chosen("transition:TR-SAVE")
        self.page.locator('[data-compare-action="overview"]').click()
        self.assert_inventory(view_b)
        self.observe_pair(view_b, "separate-self-loop-case")
        replay.expect(self.page.locator('.compare-selection [data-field="role"]')).to_contain_text("Owner")
        self.switch_case(self.case_a)
        self.case_id = self.case_a
        self.chosen("transition:TR-SAVE")
        view_a = self.case_view()
        self.assert_inventory(view_a)
        replay.expect(self.page.locator('.compare-selection [data-field="role"]')).to_contain_text("Agent")
        self.observe_pair(view_a, "restored-case-a")
        self.assert_unchanged(before_a)
        self.assert_unchanged(before_b)
        return {"case_a": self.case_a, "case_b": self.case_b, "self_loop": "PREVIEW→PREVIEW",
                "same_transition_id_distinct_case_role": True, "navigation_unchanged": True}

    def runtime_context(self):
        view = self.case_view()
        self.tab("try")
        self.page.locator("#reset").click()
        self.settled()
        final = None
        for action, actor in (("Propose", "agent-active"), ("SelectMeaning", "owner-active"), ("Save", "agent-active")):
            self.page.locator("#actor").select_option(actor)
            with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/execute")) as pending:
                self.page.locator(f'#runtime-actions [data-action="{action}"]').click()
            assert pending.value.status == 200
            final = pending.value.json()
            assert final["committed"] is True
            self.settled()
        instance = final["instance"]
        assert instance["state"] == "SAVED" and instance["model_hash"] == view["packet"]["subject"]["semantic"]
        persisted = self.case_view()
        assert instance in persisted["observations"]["instances"]
        assert persisted["case"] == view["case"]
        rendered = {key: self.page.locator("#" + key).inner_text() for key in ("runtime-state", "runtime-version", "runtime-result")}
        writes = [x for x in self.requests if x["method"] != "GET"]
        for tab in ("review", "code", "evidence", "model", "try"):
            self.tab(tab)
        assert {key: self.page.locator("#" + key).inner_text() for key in rendered} == rendered
        assert self.case_view() == persisted
        assert [x for x in self.requests if x["method"] != "GET"] == writes
        return {"persisted_instance": instance, "navigation_retains_runtime_context": True, "no_navigation_writes": True}

    def keyboard_and_viewports(self):
        before = self.snapshot()
        self.tab("evidence")
        self.keyboard_to("#focus-evidence")
        self.page.keyboard.press("Enter")
        replay.expect(self.page.locator("body")).to_have_attribute("data-workspace-focused", "true")
        self.keyboard_to("#layout-summary")
        self.page.keyboard.press("Enter")
        replay.expect(self.page.locator("#workspace-layout")).to_have_attribute("open", "")
        self.page.keyboard.press("Escape")
        self.keyboard_to("#restore-workspace")
        self.page.keyboard.press("Enter")
        replay.expect(self.page.locator("#focus-evidence")).to_be_focused()
        self.chosen("transition:TR-VERIFY")
        measures = []
        for width, height in ((1600, 1100), (1280, 800), (320, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.page.locator('[data-compare-action="readable"]').click()
            labels = self.page.locator(".compare-state-label")
            sizes = [labels.nth(i).bounding_box()["height"] for i in range(labels.count())]
            assert min(sizes) >= 14, {"viewport": [width, height], "label_heights": sizes}
            bounds = self.page.evaluate("({body:document.body.scrollWidth,document:document.documentElement.scrollWidth,viewport:innerWidth})")
            assert bounds["body"] <= width + 1 and bounds["document"] <= width + 1, bounds
            self.observe_pair(self.case_view(), f"readable-{width}")
            self.shot(f"review-{width}")
            measures.append({"viewport": [width, height], "bounds": bounds, "min_state_label_px": min(sizes)})
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        self.assert_unchanged(before)
        return {"keyboard_activations": True, "viewports": measures, "scope": "Synthetic layout checks, not a human usability study."}

    def review_axe(self):
        axe = replay.Axe.from_file(replay.AXE_FILE_PATH)
        observations = []
        for name in ("review", "evidence"):
            self.tab(name)
            if name == "evidence":
                self.page.locator("#focus-evidence").click()
            result = axe.run(self.page, options={
                "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]},
                "resultTypes": ["violations", "incomplete"],
            }).response
            observations.append({"view": name, "focused": name == "evidence", "axe_version": result["testEngine"]["version"],
                                 "violations": result["violations"], "incomplete": result["incomplete"]})
        write_json(self.out / "axe-review.json", observations)
        assert not any(item["violations"] for item in observations), "Automatic accessibility violations: inspect axe-review.json."
        self.page.locator("#restore-workspace").click()
        return {"automatic_violations": 0, "incomplete_count": sum(len(item["incomplete"]) for item in observations),
                "scope": "Automated observations only; incomplete checks and human accessibility remain review required."}



_FRESHNESS_PATH = "src/eija_studio/application/service.py"
_FRESHNESS_REF = "repo://" + _FRESHNESS_PATH + "#Studio.verify"
_FRESHNESS_COMMENT = "# EIJA freshness fixture: externally edited inside Studio.verify."


def _freshness_git(root, *args):
    env = os.environ.copy()
    for key in tuple(env):
        if key.upper().startswith("GIT_"):
            env.pop(key)
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    command = [*resolve_command("git"), "-C", str(root), "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
               "-c", "core.hooksPath=" + str(root / ".git" / "disabled-hooks"), *args]
    result = run_bounded(command, env=env, input=None, timeout=30)
    result.check_returncode()
    return result.stdout.strip()


def _freshness_changed_bytes(original):
    text = original.decode("utf-8")
    tree = ast.parse(text)
    studio = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == "Studio")
    verify = next(item for item in studio.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "verify")
    assert _FRESHNESS_COMMENT not in text, "Fixture marker already exists in the original source"
    lines = text.splitlines(keepends=True)
    at = verify.body[0].lineno - 1
    indent = re.match(r"[ \t]*", lines[at]).group()
    lines.insert(at, indent + _FRESHNESS_COMMENT + ("\r\n" if "\r\n" in text else "\n"))
    changed = "".join(lines)
    ast.parse(changed)
    return changed.encode("utf-8")


def _freshness_query(response, path, **query):
    parsed = urlsplit(response.url)
    actual = parse_qs(parsed.query)
    return (response.request.method == "GET" and parsed.path == path
            and all(actual.get(key) == [value] for key, value in query.items()))


def _freshness_ui_source(page):
    return {"reference": page.locator("#source-reference").input_value(),
            "caption": page.locator("#source-file").inner_text(),
            "source_hash": page.locator("#source-reader").get_attribute("data-source-hash"),
            "lines": page.locator(".source-line code").all_text_contents(),
            "numbers": page.locator(".source-line .line-number").all_text_contents(),
            "metadata": page.locator("#source-metadata").text_content()}


def _freshness_assert_source(page, payload, connection, file_bytes):
    assert payload["status"] == "connected" and payload["read_only"] is True
    assert payload["reference"] == _FRESHNESS_REF and payload["path"] == _FRESHNESS_PATH
    assert payload["symbol"] == "Studio.verify"
    assert payload["source_hash"] == connection["source_hash"]
    assert payload["graph_hash"] == connection["graph_hash"]
    assert payload["pack_digest"] == connection["pack"]["digest"]
    assert payload["file_hash"] == hashlib.sha256(file_bytes).hexdigest() == connection["file_hashes"][_FRESHNESS_PATH]
    assert payload["snippet_hash"] == hashlib.sha256(payload["text"].encode("utf-8")).hexdigest()
    start, end = payload["lines"]["start"], payload["lines"]["end"]
    assert payload["text"] == "".join(file_bytes.decode("utf-8").splitlines(keepends=True)[start - 1:end])
    assert payload["truncated"] is False, "Expected the entire bounded Studio.verify method"
    actual = _freshness_ui_source(page)
    lines = re.split(r"\r?\n", payload["text"])
    if lines and lines[-1] == "":
        lines.pop()
    assert actual["reference"] == payload["reference"] and payload["path"] in actual["caption"]
    assert "Studio.verify" in actual["caption"] and actual["source_hash"] == payload["source_hash"]
    assert actual["lines"] == [line or " " for line in lines]
    assert actual["numbers"] == [str(start + offset) for offset in range(len(lines))]
    assert all(payload[key] in actual["metadata"] for key in ("source_hash", "graph_hash", "file_hash", "snippet_hash"))
    return actual


def _freshness_assert_rejection(payload, old_hash, new_hash):
    assert set(payload) == {"code", "message", "details"}
    assert payload["code"] == "SOURCE_SNAPSHOT_STALE"
    details = payload["details"]
    assert set(details) == {"expected_source_hash", "source_hash", "read_only", "scope"}
    assert details["expected_source_hash"] == old_hash and details["source_hash"] == new_hash
    assert details["read_only"] is True
    assert not ({"text", "impact", "graph_hash", "file_hash", "snippet_hash"} & (payload.keys() | details.keys()))


def run_freshness_fixture(playwright, out):
    """Return PASS/FAIL evidence; callers must propagate its status to the run verdict."""
    class FreshnessJourney(ReviewWorkspace):
        def __init__(self, page, directory, base):
            self.full_requests = []
            super().__init__(page, directory, base)

        def route(self, route):
            request = route.request
            parsed = urlsplit(request.url)
            self.full_requests.append({"stage": self.stage, "method": request.method,
                                       "path": parsed.path, "query": parse_qs(parsed.query)})
            if request.method != "GET":
                self.requests.append({"stage": self.stage, "method": request.method, "path": parsed.path})
                self.forbidden.append(parsed.path)
                route.abort()
            else:
                super().route(route)

        def oracle(self, path, expected_status=200, **params):
            response = self.page.context.request.get(self.base + "api/" + path, params=params,
                headers={"Authorization": "Bearer " + replay.TEST_CAPABILITY}, timeout=30000)
            payload = response.json()
            self.oracles.append({"stage": self.stage, "path": "/api/" + path, "query": params,
                                 "status": response.status, "body": payload})
            assert response.status == expected_status, f"Freshness oracle {path}: HTTP {response.status}"
            return payload

    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    real_root = Path(replay.__file__).resolve().parents[2]
    real_file = real_root / _FRESHNESS_PATH
    original = real_file.read_bytes()
    evidence = {"schema": "eija.review-source-freshness.v1", "status": "FAIL", "checks": [],
                "browser_closed": False, "server_closed": False, "fixture_removed": False,
                "real_file_sha256": hashlib.sha256(original).hexdigest(),
                "scope": "One tracked public source copy; real GETs; external comment edit; no source execution or case mutation."}
    browser = review = fixture = endpoint = None
    try:
        with tempfile.TemporaryDirectory(prefix="tracked-source-", dir=out) as scratch:
            fixture = Path(scratch).resolve()
            target = fixture / _FRESHNESS_PATH
            target.parent.mkdir(parents=True)
            target.write_bytes(original)
            _freshness_git(fixture, "init", "-q", "--template=")
            _freshness_git(fixture, "add", "--", _FRESHNESS_PATH)
            _freshness_git(fixture, "-c", "user.name=EIJA fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Public source freshness fixture")
            assert _freshness_git(fixture, "ls-files").splitlines() == [_FRESHNESS_PATH]
            evidence["fixture_head"] = _freshness_git(fixture, "rev-parse", "HEAD")
            with replay.disposable_server(repository_root=fixture) as base:
                parsed = urlsplit(base)
                endpoint = (parsed.hostname, parsed.port)
                browser = playwright.chromium.launch(headless=True)
                evidence["browser_version"] = browser.version
                try:
                    context = browser.new_context(viewport={"width": 1600, "height": 1100}, reduced_motion="reduce")
                    page = context.new_page()
                    page.set_default_timeout(30000)
                    review = FreshnessJourney(page, out, base)
                    review.stage = "freshness-initial"
                    with page.expect_response(lambda r: _freshness_query(r, "/api/workbench")) as initial:
                        review.entry()
                    assert initial.value.status == 200
                    workbench1 = review.oracle("workbench")
                    connection1 = workbench1["connection"]
                    s1 = connection1["source_hash"]
                    assert connection1["status"] == "connected" and connection1["read_only"] is True
                    assert Path(connection1["root"]).resolve() == fixture
                    assert set(connection1["file_hashes"]) == {_FRESHNESS_PATH}
                    assert initial.value.json()["connection"]["source_hash"] == s1
                    cases_before = review.oracle("cases")
                    assert cases_before == []
                    leaf = page.locator('[data-eija-id="eija-review-slice.term.verify"]')
                    leaf.click()
                    impact_button = page.locator("#selection-detail").get_by_role("button", name="Find repository references", exact=True)
                    with page.expect_response(lambda r: _freshness_query(r, "/api/repository/impact", term="verify", expected_source_hash=s1)) as impact1:
                        impact_button.click()
                    review.settled()
                    assert impact1.value.status == 200
                    assert impact1.value.json() == review.oracle("repository/impact", term="verify", expected_source_hash=s1)
                    replay.expect(page.locator("#inspector-impact")).to_have_attribute("data-source-hash", s1)
                    review.tab("code")
                    page.locator("#source-reference").fill(_FRESHNESS_REF)
                    with page.expect_response(lambda r: _freshness_query(r, "/api/repository/source", reference=_FRESHNESS_REF, expected_source_hash=s1)) as source1:
                        page.locator("#source-reference").press("Enter")
                    assert source1.value.status == 200
                    data1 = review.oracle("repository/source", reference=_FRESHNESS_REF, expected_source_hash=s1)
                    assert source1.value.json() == data1
                    replay.expect(page.locator("#source-freshness")).to_have_attribute("data-status", "captured")
                    ui1 = _freshness_assert_source(page, data1, connection1, original)
                    page.screenshot(path=str(out / "source-s1.png"), full_page=True)
                    evidence["checks"].append({"id": "captured-s1", "status": "PASS", "source_hash": s1})

                    review.stage = "freshness-external-change"
                    modified = _freshness_changed_bytes(original)
                    target.write_bytes(modified)
                    evidence["fixture_file_hashes"] = {"before": hashlib.sha256(original).hexdigest(), "after": hashlib.sha256(modified).hexdigest()}
                    freshness = review.oracle("repository/freshness", expected_source_hash=s1)
                    s2 = freshness["source_hash"]
                    assert freshness["status"] == "stale" and freshness["compared_source_hash"] == s1 and s1 != s2
                    assert freshness["read_only"] is True and all(freshness[key] is None for key in ("changed", "added", "removed"))
                    assert not ({"text", "impact", "file_hash", "snippet_hash", "graph_hash"} & freshness.keys())
                    for path, params in (("source", {"reference": _FRESHNESS_REF}), ("impact", {"term": "verify"})):
                        rejected = review.oracle("repository/" + path, expected_status=409, expected_source_hash=s1, **params)
                        _freshness_assert_rejection(rejected, s1, s2)
                    with page.expect_response(lambda r: _freshness_query(r, "/api/repository/source", reference=_FRESHNESS_REF, expected_source_hash=s1)) as stale_source:
                        page.locator("#source-reference").press("Enter")
                    assert stale_source.value.status == 409
                    _freshness_assert_rejection(stale_source.value.json(), s1, s2)
                    replay.expect(page.locator("#source-freshness")).to_have_attribute("data-status", "stale")
                    replay.expect(page.locator("#source-freshness")).to_contain_text("Previous captured source is retained")
                    assert _freshness_ui_source(page) == ui1, "Stale navigation replaced old source or caption"
                    with page.expect_response(lambda r: _freshness_query(r, "/api/repository/impact", term="verify", expected_source_hash=s1)) as stale_impact:
                        impact_button.click()
                    review.settled()
                    assert stale_impact.value.status == 409
                    _freshness_assert_rejection(stale_impact.value.json(), s1, s2)
                    replay.expect(page.locator("#error-json")).to_contain_text("SOURCE_SNAPSHOT_STALE")
                    assert _freshness_ui_source(page) == ui1
                    page.screenshot(path=str(out / "stale-source-retained.png"), full_page=True)
                    evidence["checks"].append({"id": "stale-rejection-retains-s1", "status": "PASS", "source_hash": s2})

                    review.stage = "freshness-explicit-refresh"
                    review.tab("model")
                    marker = len(review.full_requests)
                    retry = page.locator('#inspector-impact [data-source-refresh="true"]')
                    with page.expect_response(lambda r: _freshness_query(r, "/api/workbench")) as refreshed, page.expect_response(lambda r: _freshness_query(r, "/api/repository/source", reference=_FRESHNESS_REF, expected_source_hash=s2)) as source2:
                        retry.click()
                    review.settled()
                    assert refreshed.value.status == source2.value.status == 200
                    replay.expect(page.locator('[data-tab="model"]')).to_have_attribute("aria-selected", "true")
                    workbench2 = review.oracle("workbench")
                    connection2 = workbench2["connection"]
                    assert refreshed.value.json()["connection"]["source_hash"] == connection2["source_hash"] == s2
                    assert workbench2["model"] == workbench1["model"] and workbench2["baseline_version"] == workbench1["baseline_version"]
                    data2 = review.oracle("repository/source", reference=_FRESHNESS_REF, expected_source_hash=s2)
                    assert source2.value.json() == data2 and _FRESHNESS_COMMENT in data2["text"]
                    replay.expect(page.locator("#source-freshness")).to_have_attribute("data-status", "captured")
                    ui2 = _freshness_assert_source(page, data2, connection2, modified)
                    assert ui2["lines"] != ui1["lines"] and ui2["caption"] == ui1["caption"]
                    assert not any(item["path"] == "/api/repository/impact" for item in review.full_requests[marker:]), "Refresh silently recalculated impact"
                    replay.expect(page.locator("#inspector-impact")).to_contain_text("Find repository references again")
                    with page.expect_response(lambda r: _freshness_query(r, "/api/repository/impact", term="verify", expected_source_hash=s2)) as impact2:
                        impact_button.click()
                    review.settled()
                    assert impact2.value.status == 200
                    current_impact = review.oracle("repository/impact", term="verify", expected_source_hash=s2)
                    assert impact2.value.json() == current_impact
                    assert current_impact["status"] == "connected" and current_impact["source_hash"] == s2
                    replay.expect(page.locator("#inspector-impact")).to_have_attribute("data-source-hash", s2)
                    replay.expect(page.locator('[data-tab="model"]')).to_have_attribute("aria-selected", "true")
                    fresh = review.oracle("repository/freshness", expected_source_hash=s2)
                    assert fresh["status"] == "current" and fresh["source_hash"] == fresh["compared_source_hash"] == s2
                    assert review.oracle("cases") == cases_before
                    review.tab("code")
                    _freshness_assert_source(page, data2, connection2, modified)
                    page.screenshot(path=str(out / "source-s2-refreshed.png"), full_page=True)
                    assert not review.errors and not review.forbidden
                    assert [(item["status"], item["path"]) for item in review.http_errors] == [(409, "/api/repository/source"), (409, "/api/repository/impact")]
                    assert all(item["method"] == "GET" for item in review.full_requests)
                    assert _freshness_git(fixture, "rev-parse", "HEAD") == evidence["fixture_head"]
                    assert target.read_bytes() == modified
                    evidence["checks"].append({"id": "explicit-s2-refresh-and-impact", "status": "PASS", "tab_retained": "model"})
                    evidence.update(status="PASS", s1=s1, s2=s2, source_ui_before=ui1, source_ui_after=ui2)
                finally:
                    try:
                        if review is not None:
                            review.page.screenshot(path=str(out / "final.png"), full_page=True)
                    finally:
                        browser.close()
                        evidence["browser_closed"] = True
            evidence["server_closed"] = True
    except Exception as error:  # Retain failure evidence after fixture/browser/server cleanup.
        evidence["status"] = "FAIL"
        evidence["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]")}
    finally:
        evidence["fixture_removed"] = fixture is not None and not fixture.exists()
        if endpoint is not None:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                evidence["server_closed"] = probe.connect_ex(endpoint) != 0
        evidence["real_file_preserved"] = hashlib.sha256(real_file.read_bytes()).hexdigest() == evidence["real_file_sha256"]
        if not all(evidence[key] for key in ("browser_closed", "server_closed", "fixture_removed", "real_file_preserved")):
            evidence["status"] = "FAIL"
        if review is not None:
            evidence.update(requests=review.full_requests, http_errors=review.http_errors,
                            javascript_errors=review.errors, forbidden_attempts=review.forbidden)
            (out / "authoritative-get-oracles.json").write_text(json.dumps(review.oracles, indent=2) + "\n", encoding="utf-8")
        (out / "result.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        manifest = {item.name: {"bytes": item.stat().st_size, "sha256": hashlib.sha256(item.read_bytes()).hexdigest()}
                    for item in sorted(out.iterdir()) if item.is_file()}
        (out / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return evidence


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Assertion oracles require Python without -O/-OO."})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if replay.PREREQUISITE_ERROR:
        write_json(out / "result.json", {"status": "NOT_RUN", "reason": replay.PREREQUISITE_ERROR})
        return 3
    before = subject_identity()
    write_json(out / "subject-before.json", before)
    result = {"status": "FAIL", "schema": "eija.review-workspace-browser.v1", "utc": datetime.now(UTC).isoformat(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "checks": [],
              "identity": "normal_source_review_required", "pack": "eija-review-slice", "provider": "offline",
              "browser_closed": False, "server_closed": False,
              "not_covered": ["baseline-only removal through UI", "changed initial state through UI", "human comprehension", "live models", "owner authorization"]}
    review, server_address = None, None
    try:
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            server_address = (endpoint.hostname, endpoint.port)
            with replay.sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                result["browser_version"] = browser.version
                try:
                    context = browser.new_context(viewport={"width": 1600, "height": 1100}, reduced_motion="reduce")
                    page = context.new_page()
                    page.set_default_timeout(30000)
                    review = ReviewWorkspace(page, out, base)
                    for name, action in (("model-to-selected-change", review.prepare), ("paired-graph-truth", review.paired_graphs),
                                         ("exact-source-roundtrip", review.exact_source), ("evidence-focus-error-restore", review.focus_recovery),
                                         ("history-current-subject", review.historical_context), ("self-loop-cross-case", review.loop_and_cross_case),
                                         ("runtime-context", review.runtime_context), ("keyboard-responsive-review", review.keyboard_and_viewports),
                                         ("review-accessibility", review.review_axe)):
                        review.step(name, action)
                        emit({"check": name, "status": "PASS"})
                    assert review.http_errors == review.injected and len(review.injected) == 1
                    assert not review.errors and not review.forbidden
                    result["status"] = "PASS"
                finally:
                    try:
                        if review is not None:
                            page.screenshot(path=str(out / "final.png"), full_page=True)
                    finally:
                        browser.close()
                        result["browser_closed"] = True
        with replay.sync_playwright() as playwright:
            result["source_freshness_fixture"] = run_freshness_fixture(playwright, out / "freshness-fixture")
        assert result["source_freshness_fixture"]["status"] == "PASS", result["source_freshness_fixture"]
    except Exception as error:  # Record any failed browser oracle and still close owned resources.
        result["status"] = "FAIL"
        result["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[test-capability]")}
        emit({"status": "FAIL", "error": result["error"]})
    finally:
        if server_address is not None:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                result["server_closed"] = probe.connect_ex(server_address) != 0
        if not result["browser_closed"] or not result["server_closed"]:
            result["status"] = "FAIL"
        if review is not None:
            result.update({"checks": review.checks, "failed_stage": review.stage if result["status"] != "PASS" else None,
                           "requests": review.requests, "http_errors": review.http_errors, "injected": review.injected,
                           "javascript_errors": review.errors, "forbidden_attempts": review.forbidden})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
            write_json(out / "graph-observations.json", review.graph_records)
            write_json(out / "source-observations.json", review.source_records)
        after = subject_identity()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        if result["subject_preservation"]["status"] != "UNCHANGED":
            result["status"] = "FAIL"
        result["subject_content_sha256"] = before["content_sha256"]
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                                    for p in sorted(out.rglob("*")) if p.is_file()})
    emit({key: result[key] for key in ("status", "browser_closed", "server_closed", "subject_preservation")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
