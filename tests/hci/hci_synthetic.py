"""Hand-built journey trace with known geometry, so the analysis layer is testable without a browser."""
from __future__ import annotations

import copy


def box(x, y, w, h):
    return {"x": x, "y": y, "w": w, "h": h}


def target(step, name, frm, to, w, h, selector=None, via_label=False, raw=None):
    return {"step": step, "name": name, "selector": selector or "#" + step, "tag": "button", "from": frm, "to": to,
            "effective": box(to[0] - w / 2, to[1] - h / 2, w, h), "raw": raw or box(to[0] - w / 2, to[1] - h / 2, w, h),
            "via_label": via_label, "scrolled": False}


def control(selector, x, y, w, h, name="c", raw_w=None, raw_h=None, via_label=False):
    return {"selector": selector, "tag": "button", "name": name, "x": x, "y": y, "w": w, "h": h,
            "raw_w": raw_w if raw_w is not None else w, "raw_h": raw_h if raw_h is not None else h,
            "via_label": via_label, "disabled": False, "in_viewport": True}


def view(controls, violations=(), chunks=(3, 4)):
    c = {"controls": chunks[0], "content_groups": chunks[1], "atoms": 9, "chunks": chunks[0] + chunks[1]}
    return {"controls": list(controls), "chunks_viewport": c, "chunks_page": dict(c), "tabbable": 3, "geometry": {},
            "visual_state_only": [], "axe": {"axe_core": "4.12.1", "violations": list(violations), "incomplete": []}}


def step(step_id, interaction=None, decision=None, **extra):
    s = {"id": step_id, "label": step_id, "kind": "click", "ref": "#" + step_id}
    if interaction is not None:
        s["interaction"] = {"target": "button", "kind": "pointer", "first_feedback_ms": 1.0, "settled_ms": interaction, "mutation_batches": 3}
        s["focus_lost_after"] = False
    if decision:
        s["decision"] = {"name": "pick", "selectors": ["x"], "n_choices": decision[0], "n_screen": decision[1]}
    s.update(extra)
    return s


def pointer_pass(settled=(50.0, 900.0)):
    targets = [
        target("s1", "First", None, [100, 100], 200, 40),
        target("s2", "Second", [100, 100], [500, 100], 100, 40),  # D=400 W=40 -> ID = log2(11)
        target("s3", "Tiny", [500, 100], [700, 100], 100, 20),  # W=20 < 24
        target("s4", "Far", [700, 100], [1500, 100], 100, 40, selector="#far"),  # D=800 -> ID = log2(21) > 4
    ]
    ops = []
    for t in targets:
        ops += [{"step": t["step"], "op": "P", "note": "point", "fitts": True}, {"step": t["step"], "op": "B", "note": "b"},
                {"step": t["step"], "op": "B", "note": "b"}]
    ops.insert(0, {"step": "s1", "op": "M", "note": "think"})
    steps = [step("s1"), step("s2", settled[0], decision=(3, 9)), step("s3", settled[1], decision=(9, 9)), step("s4", 10.0)]
    views = {"one": view([control("#a", 0, 0, 100, 40), control("#tiny", 0, 100, 16, 16), control("#tiny2", 20, 100, 16, 16)],
                         violations=[{"id": "color-contrast", "impact": "serious", "help": "contrast", "help_url": "u", "tags": ["wcag2aa"],
                                      "nodes": [{"target": "#a", "html": "<a>", "summary": "s"}]}]),
             "two": view([control("#a", 0, 0, 100, 40)])}
    return {"modality": "pointer", "steps": steps, "operators": ops, "pointer_targets": targets, "views": views,
            "responsive": {"320x568": {"change": {"scroll_width": 320, "inner_width": 320, "controls": [control("#z", 0, 0, 100, 44)]}}},
            "errors": [], "http_failures": []}


def keyboard_pass():
    steps = [
        step("s1", 30.0, focus_stops=[{"name": "A", "selector": "#a", "visible_ring": True, "focus_visible": True, "lost": False,
                                       "rect": box(0, 100, 10, 10)}], tab_presses=1),
        step("s2", 30.0, tab_presses=4, focus_stops=[
            {"name": "B", "selector": "#b", "visible_ring": False, "focus_visible": True, "lost": False, "rect": box(0, 200, 10, 10)},
            {"name": "C", "selector": "#c", "visible_ring": True, "focus_visible": True, "lost": False, "rect": box(0, 100, 10, 10)}]),
    ]
    steps[0]["focus_lost_after"] = True
    ops = [{"step": "s1", "op": "K", "note": "Tab"}, {"step": "s1", "op": "K", "note": "Enter"}]
    return {"modality": "keyboard", "steps": steps, "operators": ops, "pointer_targets": [], "views": {}, "responsive": None,
            "errors": [], "http_failures": []}


def raw():
    p0 = pointer_pass()
    return {"environment": {"platform": "test-os", "python": "3.12", "chrome": "0", "playwright": "0", "axe_playwright_python": "0",
                            "axe_core": "4.12.1", "viewport": {"width": 1440, "height": 900}, "headless": True, "repeats": 2,
                            "ui_sha256": {"app.js": "0" * 64}, "provider": "offline (synthetic)", "identity_source": "pytest-harness",
                            "device_scale_factor": 1},
            "pointer_passes": [p0, copy.deepcopy(pointer_pass(settled=(60.0, 300.0)))], "keyboard_pass": keyboard_pass()}
