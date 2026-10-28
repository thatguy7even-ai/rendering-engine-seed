"""Integrated workbench session — Blink, Oct 27, 2026, at Dakota's order to
play with the toys as pieces, not as separate demos.

One World, one Mesh, six verbs in sequence, state carrying between verbs:
  1. seed toy Mesh/World (house built from nodes only)
  2. 3D view (Renderer3D reads world.mesh.nodes live, no second store)
  3. avatar field (avatar body 0, its field IS the collision zone)
  4. voice hold + gesture rotate (voice locks, gesture rotates the rest)
  5. pick-up / put-down (grab binds, carry follows, release checks
     field first then body, blocked release holds)
  6. the workbench itself: the session above, run as one thing.

Verbs rotate_rest / grab / carry / try_release are copied from
hold_rotate.py and pickup_putdown.py rather than imported, because those
modules run their own demos on import. Mesh/World/Renderer3D are imported
from engine_3d, which loads mother's seed toy — the one spatial structure.

This is a 2D toy proof of composition, NOT a holodeck, NOT hand
tracking, NOT touch hardware, NOT voice recognition.
"""
import math, os, sys
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
        # FIX (Control's Oct-27 composition find, independently reproduced
        # by this session before the fix: release wrongly RELEASED onto the
        # tree): hold_rotate.py's rotate_rest moves nodes by direct
        # assignment without rehash, leaving the Mesh spatial hash stale.
        # Rehash each rotated node, per carry()'s own convention.
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
    evals = 0
    for other in cands:
        evals += 1
        d = math.hypot(other.x - node.x, other.y - node.y)
        body = other.body_radius(tps)
        print(f"    candidate node {other.id} ({other.kind}): centre distance {d:.2f}, body {body:.1f} -> {'BLOCKS' if d < body else 'passes'}")
        if d < body:
            return False, other.id, evals
    return True, None, evals


def show(world, label):
    print(f"{label}")
    for nid, n in sorted(world.mesh.nodes.items()):
        tps = world.mesh.ticks_per_stage
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) bubble={n.bubble_radius(tps)} body={n.body_radius(tps)}")


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# 0) BUILD THE HOUSE on the one Mesh (same nodes as the demos).
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))   # roof
w.add(mother.Node(2, 7, 4, "rock"))            # wall
w.add(mother.Node(3, 13, 4, "rock"))           # wall
w.add(mother.Node(99, 10, 4, "avatar"))        # door
show(w, "0) HOUSE BUILT on the one Mesh:")
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "integrated_before.png"))
print("  3D view rendered from the same Mesh (integrated_before.png).")

# 1) VOICE hold + GESTURE rotate: "hold sector A2" locks rock 2, rest +90.
print()
print('1) VOICE: "hold sector A2" -> hold node 2 (rock at 7,4).')
held_pos = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
dists_before = {nid: dist((n.x, n.y), held_pos) for nid, n in w.mesh.nodes.items()}
print("   GESTURE: rotate rest +90 degrees around held node 2.")
rotate_rest(w, held_id=2, degrees=90)
show(w, "   AFTER ROTATION (state now carries into the next verb):")
held_after = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
assert held_after == held_pos, "held node moved during rotation"
for nid, n in w.mesh.nodes.items():
    assert abs(dist((n.x, n.y), held_after) - dists_before[nid]) < 1e-9, f"node {nid} distance changed"
print("   CHECK: held node 2 exactly put; all distances to pivot preserved.")
tree_after_rotation = (w.mesh.nodes[1].x, w.mesh.nodes[1].y)

# 2) PICK UP rock 3 in the ROTATED world (not the pristine house).
print()
print("2) SEAT PICKS UP ROCK 3 (now at its rotated position), tries the tree, retries:")
rock3 = grab(w, 3)
carry(w, rock3, [(tree_after_rotation[0], tree_after_rotation[1])])
print(f"  RELEASE at tree {tree_after_rotation}:")
ok, blocker, evals = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)}")
assert (not ok) and blocker == 1 and (rock3.x, rock3.y) == tree_after_rotation
print("  Blocked release does NOT drop it — rock 3 stays held. Seat moves hand to (13,8):")
carry(w, rock3, [(13, 8)])
print("  RELEASE at (13,8):")
ok, blocker, evals = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)}")
assert ok and (rock3.x, rock3.y) == (13.0, 8.0)

# 3) PICK UP THE AVATAR (itself a node, body 0) in the rotated world.
print()
print("3) SEAT PICKS UP THE AVATAR, tries the tree body, retries field-only:")
av = grab(w, 99)
carry(w, av, [(tree_after_rotation[0], tree_after_rotation[1])])
print(f"  RELEASE at tree {tree_after_rotation}:")
ok, blocker, evals = try_release(w, av)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)}")
assert (not ok) and blocker == 1
print("  Seat moves hand to (2,5) — inside the tree field, outside its body — and retries:")
carry(w, av, [(2, 5)])
print("  RELEASE at (2,5):")
ok, blocker, evals = try_release(w, av)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)}")
assert ok and (av.x, av.y) == (2.0, 5.0)

# 4) VOICE release unlocks rock 2. Render the rearranged world.
print()
print('4) VOICE: "release" -> node 2 unlocks.')
show(w, "FINAL — one Mesh, after hold/rotate + two pickups:")
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "integrated_after.png"))
r.export_obj(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "integrated_after.obj"))
print("  3D view + OBJ rendered from the same Mesh AFTER the verbs ran.")
print("  (If the view were a copy, it would still show the pristine house.)")

print()
print("CHECKS:")
print(f"  held node 2 exactly put through rotation: {'PASS' if held_after == held_pos else 'FAIL'}")
print(f"  tree moved by rotation only, never by pickup: {'PASS' if (w.mesh.nodes[1].x, w.mesh.nodes[1].y) == tree_after_rotation else 'FAIL'}")
print(f"  rock 3: blocked on tree, released at (13,8): {'PASS' if (rock3.x, rock3.y) == (13.0, 8.0) else 'FAIL'}")
print(f"  avatar: blocked on tree body, released field-only at (2,5): {'PASS' if (av.x, av.y) == (2.0, 5.0) else 'FAIL'}")
cover = sorted(w.mesh.covering_set(2, 5))
print(f"  covering set at avatar (2,5): {cover} (tree field + avatar field): {'PASS' if 1 in cover and 99 in cover else 'FAIL'}")
assert 1 in cover and 99 in cover
cover3 = sorted(w.mesh.covering_set(13, 8))
print(f"  covering set at rock 3 (13,8): {cover3} (rock 3 alone): {'PASS' if cover3 == [3] else 'FAIL'}")
assert cover3 == [3]
ray = w.mesh.raycast(0, 4, 0.0, exclude_id=None)
print(f"  raycast east from (0,4) on the rearranged Mesh: {ray} (origin now inside the moved tree field; pristine house gave rock 2 at 5.0): {'PASS' if ray == (1, 0.0) else 'FAIL'}")
assert ray == (1, 0.0)
print("  overall: PASS — six verbs, one Mesh, state carried between verbs")
