"""Small coordinate helpers for repeated EDA workflow-layout constraints.

No drawing backend or third-party dependencies.
Run: python layout_math.py --self-test
Run: python layout_math.py --example
Import functions for other figures; sample coordinates are not global defaults.
"""
import argparse
import json
import math


def equal_stack(count, height, first_center, aligned_index, aligned_center):
    """Equal-height boxes anchored by the first and one subsequent center."""
    if count < 2 or not 1 <= aligned_index < count or height <= 0:
        raise ValueError("Need >=2 boxes, positive height and a later alignment index")
    pitch = (aligned_center - first_center) / aligned_index
    if pitch <= height:
        raise ValueError("Anchors leave no positive gap between boxes")
    centers = [first_center + i * pitch for i in range(count)]
    return {"centers": centers,
            "tops": [c - height / 2 for c in centers],
            "gap": pitch - height}


def symmetric_dispatch(source_x, target_x, top_y, bottom_y):
    """Unobstructed left-to-right bus with symmetric top/middle/bottom branches."""
    if target_x <= source_x or bottom_y <= top_y:
        raise ValueError("Need a right-hand target and increasing branch y values")
    return {"bus_x": (source_x + target_x) / 2,
            "source_y": (top_y + bottom_y) / 2,
            "branch_ys": [top_y, (top_y + bottom_y) / 2, bottom_y]}


def left_return(source, target, rail_x, minimum_final_run):
    """Leftward exit, upward rail, rightward entry; caller checks scope clearance."""
    sx, sy = source
    tx, ty = target
    if rail_x >= min(sx, tx) or ty >= sy or minimum_final_run <= 0:
        raise ValueError("Return needs a left-side rail, upper target and positive clearance")
    if tx - rail_x < minimum_final_run:
        raise ValueError("Final arrow segment too short: move rail left or expand scope")
    return [[sx, sy], [rail_x, sy], [rail_x, ty], [tx, ty]]


def accepted_example():
    stack = equal_stack(5, 110, 335, 3, 925)
    bus = symmetric_dispatch(1120, 1340, 665, 1185)
    route = left_return((730, stack["centers"][-1]), (729, 365), 680, 48)
    return {"stack": stack, "dispatch": bus, "return_points": route}


def self_test():
    e = accepted_example()
    centers = e["stack"]["centers"]
    gaps = [b - a - 110 for a, b in zip(centers, centers[1:])]
    assert max(gaps) - min(gaps) < 1e-8
    assert math.isclose(centers[3], e["dispatch"]["source_y"])
    assert e["dispatch"]["bus_x"] - 1120 == 1340 - e["dispatch"]["bus_x"]
    a, b, c = e["dispatch"]["branch_ys"]
    assert b - a == c - b
    route = e["return_points"]
    assert all(p[0] == q[0] or p[1] == q[1] for p, q in zip(route, route[1:]))
    assert route[-1][0] - route[-2][0] == 49
    for operation in [lambda: equal_stack(5, 110, 335, 3, 600),
                      lambda: left_return((730, 1120), (729, 365), 710, 48)]:
        try:
            operation()
        except ValueError:
            pass
        else:
            raise AssertionError("Crowded geometry was accepted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--example", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("PASS: equal spacing, aligned symmetric dispatch, orthogonal return and short-run rejection")
    else:
        print(json.dumps(accepted_example(), indent=2))
