"""WCAG 2.2 SC 2.5.8 Target Size (Minimum): pure geometry.

A pointer target must be at least 24x24 CSS px, OR satisfy the spacing exception: a 24 px diameter
circle centred on the target's bounding box must not intersect another target (or that other
undersized target's own 24 px circle). Other exceptions (inline text links, user-agent-controlled
size, equivalent control elsewhere, essential) need human judgement and are NOT evaluated here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .laws import MIN_TARGET_PX


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)

    @property
    def smaller(self) -> float:
        return min(self.w, self.h)


def circle_hits_box(cx: float, cy: float, radius: float, box: Box) -> bool:
    """True if the open disc (cx, cy, radius) intersects the axis-aligned box."""
    nearest_x = min(max(cx, box.x), box.x + box.w)
    nearest_y = min(max(cy, box.y), box.y + box.h)
    return math.hypot(cx - nearest_x, cy - nearest_y) < radius


def target_size_status(index: int, boxes: list[Box], minimum: float = MIN_TARGET_PX) -> str:
    """`pass` (>= minimum), `pass-spacing` (undersized but isolated per the exception) or `fail`."""
    box = boxes[index]
    if box.w >= minimum and box.h >= minimum:
        return "pass"
    radius = minimum / 2.0
    cx, cy = box.center
    for other_index, other in enumerate(boxes):
        if other_index == index:
            continue
        if other.w >= minimum and other.h >= minimum:
            if circle_hits_box(cx, cy, radius, other):
                return "fail"
        else:  # both undersized: their 24 px circles may not overlap
            ox, oy = other.center
            if math.hypot(cx - ox, cy - oy) < minimum:
                return "fail"
    return "pass-spacing"
