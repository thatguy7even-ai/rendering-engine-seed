"""Four's integrated workbench variant — same composition, fixed choreography.

The existing workbench_integrated.py fails at its avatar walk: it releases
rock 3 at (5,7) and then walks the avatar west along y=7, straight through
rock 3's body (first step (6.5,7) is already inside rock 3's body radius
1.6). The walk's message says "tree body boundary" but the blocker is
rock 3 — placed nodes become obstacles for later verbs, which is exactly
what integration testing is for. This variant walks the avatar SOUTH
toward the held rock instead, so the blocker is the node the walk names.

Not an edit of the other seat's file (F10 discipline: coordinate on
shared files, don't overwrite). Same verbs, same one Mesh, corrected lane.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother, Renderer3D


def rotate_rest(world, held_id, degrees):
    held = world.mesh.nodes[held_id]
    px, py = held.x, held.y
    th = math.radians(degrees)
    cos_t, sin_t = math.cos(th), math.sin(th)
    for nid, n in world.mesh.nodes.items():
        if nid == held_id:
            continue
        dx, dy = n.x - px, n.y - py
        n.x = px + dx * cos_t - dy * sin_t
        n.y = py + dx * sin_t + dy * cos_t
        world.mesh.rehash(n)


def grab(world, nid):
    n = world.mesh.nodes[nid]
    print(f"  GRAB node {nid} ({n.kind}) at ({n.x:.1f},{n.y:.1f}) — bound to the hand.")
    return n


def carry(world, node, path):
    for (x, y) in path:
        node.x, node.y = float(x), float(y)
        world.mesh.rehash(node)
        print(f"    hand -> ({x:.1f},{y:.1f}) — node {node.id} follows (held, no body check while lifted)")


def try_release(world, node):
    tps = world.mesh.ticks_per_stage
    cands = world.mesh.bubble_intersections(
        node.x, node.y, node.bubble_radius(tps), exclude_id=node.id)
    for other in cands:
        d = math.hypot(other.x - node.x, other.y - node.y)
        body = other.body_radius(tps)
        print(f"    candidate {other.id} ({other.kind}): dist {d:.2f}, body {body:.1f} -> {'BLOCKS' if d < body else 'passes'}")
        if d < body:
            return False, other.id
    return True, None


def show(world, label):
    print(label)
    tps = world.mesh.ticks_per_stage
    for nid, n in sorted(world.mesh.nodes.items()):
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) bubble={n.bubble_radius(tps)} body={n.body_radius(tps)}")


w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
show(w, "SCENE — one Mesh:")

print('\nVOICE: "hold sector A2" -> lock rock 2.')
print("GESTURE: rotate the rest +90 degrees around it.")
rotate_rest(w, 2, 90)
show(w, "AFTER HOLD+ROTATE (rock 2 exactly put):")

print("\nHAND: pick up rock 3, carry it toward the tree.")
rock3 = grab(w, 3)
carry(w, rock3, [(2, 7)])
ok, blocker = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker) + ' — stays held, no drop'}")
assert not ok and blocker == 1
print("Seat moves the hand to (5,7) and retries:")
carry(w, rock3, [(5, 7)])
ok, blocker = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by ' + str(blocker)}")
assert ok and (rock3.x, rock3.y) == (5.0, 7.0)

print("\nAVATAR WALKS SOUTH from (7,7) toward the HELD rock 2 at (7,4) — field is the collision zone:")
av = w.mesh.nodes[99]
tps = w.mesh.ticks_per_stage
y = 7.0
blocker = None
while True:
    y -= 0.5
    av.y = y
    w.mesh.rehash(av)
    cands = w.mesh.bubble_intersections(av.x, av.y, av.bubble_radius(tps), exclude_id=99)
    hits = [(o.id, math.hypot(o.x - av.x, o.y - av.y), o.body_radius(tps))
            for o in cands if math.hypot(o.x - av.x, o.y - av.y) < o.body_radius(tps)]
    if hits:
        blocker = hits[0][0]
        print(f"  avatar at (7.0,{av.y:.1f}) — BLOCKED by node {blocker} at body boundary")
        break
    print(f"  avatar at (7.0,{av.y:.1f}) — clear")
assert blocker == 2 and abs(av.y - 5.5) < 0.01, (blocker, av.y)

print("\nSAME MESH VERIFIES THE NEW ARRANGEMENT:")
print(f"  covering set at rock 3 (5,7): {sorted(w.mesh.covering_set(5, 7))}")
print(f"  covering set at tree (2,7): {sorted(w.mesh.covering_set(2, 7))}")
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "workbench_four_3d.png"))
show(w, "\nFINAL — one Mesh, every toy's verb used on it:")
print("\nINTEGRATED PLAY (Four variant): PASS — hold, rotate, grab, carry, blocked-hold, release, walk, cover, render, all on one Mesh.")
print("NOTE: the held node still participates in collision — holding locks position, not presence.")
