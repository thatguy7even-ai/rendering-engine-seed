"""Workbench, combined — Mother's canonical combined toy, Oct 27-28, 2026.

This is the combined aspect Dakota asked for on Oct 28: every individual
toy in toys/individual/, run as ONE session on ONE World / ONE Mesh.

Verbs, in order, all on the same nodes (C3, no second node store):
  1. Build — house from nodes only (render_house.py)
  2. 3D view — Renderer3D reads world.mesh.nodes live (engine_3d.py)
  3. Avatar field — avatar body 0, its field IS the collision zone
     (avatar_field.py); a walk is blocked at a body boundary, not a field edge
  4. Voice hold + gesture rotate — hold rock 2, rotate the rest +90
     around it, patched rehash discipline (hold_rotate.py, Oct 27 patch)
  5. Pick-up / put-down — grab, carry with no body check while lifted,
     release checks field first then body, blocked release HOLDS
     (pickup_putdown.py)
  6. Lifecycle — a separate seed tree, ticked to mature, read live
     (engine_3d.py lifecycle proof; the house tree is left alone)
  7. Read back — covering set, raycast, glyph, 3D render + OBJ export

Bounds, stated not hidden: 2D toy proof of verb composition, NOT a
holodeck, NOT hand tracking, NOT voice recognition, NOT touch hardware.
Avatar internal rendering is named only (bones, muscles, ligaments, in
that order); Control's UNMEASURABLE mark for internal rendering STANDS.
Sector naming for "sector A2" is Dakota's to pin; this demo holds node 2,
as hold_rotate.py does, and does not invent a grid.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "individual"))
from engine_3d import Renderer3D, mother

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT, exist_ok=True)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def rotate_rest(world, held_id, degrees):
    """hold_rotate.py verb, patched: rehash each rotated node."""
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
        if d < other.body_radius(tps):
            return False, other.id, len(cands)
    return True, None, len(cands)


def show(w, label):
    print(label)
    for nid, n in sorted(w.mesh.nodes.items()):
        t = w.mesh.ticks_per_stage
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) bubble={n.bubble_radius(t)} body={n.body_radius(t)}")


# 1) BUILD — house
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
show(w, "1) BUILT house: tree/roof (10,9), rock/wall (7,4), rock/wall (13,4), avatar/door (10,4)")

# 2) 3D VIEW, before
r = Renderer3D(w)
print("2) 3D render before:", r.render_png(os.path.join(OUT, "combined_before.png")))

# 3) AVATAR FIELD, read back before any move
print("3) AVATAR FIELD: avatar 99 bubble=3.0 body=0.0, so its field IS the collision zone.")
print("   covering set at door (10,4):", sorted(w.mesh.covering_set(10, 4)))
print("   raycast east from (0,4):", w.mesh.raycast(0, 4, 0.0, exclude_id=None))

# 4) VOICE HOLD + GESTURE ROTATE
held_pos = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
dists_before = {nid: dist((n.x, n.y), held_pos) for nid, n in w.mesh.nodes.items()}
print('4) VOICE "hold sector A2" -> rock 2 locked at (7,4); GESTURE rotate rest +90 around it.')
rotate_rest(w, held_id=2, degrees=90)
show(w, "   AFTER rotate:")
held_after = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
assert held_after == held_pos, "held node moved — FAIL"
for nid, n in w.mesh.nodes.items():
    assert abs(dist((n.x, n.y), held_after) - dists_before[nid]) < 1e-9, f"distance changed for {nid}"
assert (w.mesh.nodes[1].x, w.mesh.nodes[1].y) == (2.0, 7.0)
assert (w.mesh.nodes[3].x, w.mesh.nodes[3].y) == (7.0, 10.0)
assert (w.mesh.nodes[99].x, w.mesh.nodes[99].y) == (7.0, 7.0)
print("   PASS — held locked, distances preserved, tree (2,7), rock 3 (7,10), avatar (7,7)")

# 5) PICK-UP / PUT-DOWN — move rock 3 to (13,8); blocked-release check first
rock3 = grab(w, 3)
carry(w, rock3, [(2, 7)])  # on the tree: field overlaps, body blocks
ok, blocker, evals = try_release(w, rock3)
print(f"   RELEASE at tree (2,7): {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidates)")
assert (not ok) and blocker == 1, "release onto tree should block"
print("   Blocked release HOLDS — rock 3 stays held, it does not drop.")
carry(w, rock3, [(13, 8)])
ok, blocker, evals = try_release(w, rock3)
print(f"   RELEASE at (13,8): {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidates)")
assert ok and (rock3.x, rock3.y) == (13.0, 8.0)
print("   PASS — rock 3 released at (13,8)")

# 5b) AVATAR WALK — west from (7,7) toward the tree at (2,7), blocked at its body
av = w.mesh.nodes[99]
print("5b) AVATAR WALKS west from (7,7) toward tree (2,7):")
while True:
    moved = w.avatar_try_move(av, av.x - 0.5, av.y)
    if not moved:
        break
print(f"   BLOCKED at avatar ({av.x:.1f},{av.y:.1f}), distance to tree centre "
      f"{math.hypot(2 - av.x, 7 - av.y):.1f} = tree body boundary 1.0")
assert (av.x, av.y) == (3.0, 7.0)
print("   PASS — walk stops at the body, not at the field edge")

# 6) LIFECYCLE, separate world so the house is not disturbed
w2 = mother.World()
w2.add(mother.Node(1, 10, 10, "tree", age=0))
r2 = Renderer3D(w2)
before = r2.nodes_3d()[1]
for _ in range(30):
    w2.tick()
after = r2.nodes_3d()[1]
print(f"6) LIFECYCLE: seed tree before 30 ticks: {before}; after: {after}")
assert after[5] == "tree:mature", "tree should be mature after 30 ticks"

# 7) READ BACK + final 3D render / OBJ
show(w, "7) FINAL house world:")
print("   covering set at avatar (3,7):", sorted(w.mesh.covering_set(3, 7)))
print("   3D render after:", r.render_png(os.path.join(OUT, "combined_after.png")))
verts, faces = r.export_obj(os.path.join(OUT, "combined_after.obj"))
print(f"   OBJ export: {verts} verts, {faces} faces")
print()
print("OVERALL: PASS — one World, one Mesh, all six verbs in one sitting")
