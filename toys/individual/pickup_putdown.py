"""Hollow-deck workbench pick-up / put-down prototype — Oct 27, 2026.

Dakota, Oct 27 ~15:52 EDT: take the TikTok AR agent visualization +
voice+gesture hold/rotate + the rendering engine + holodeck theory, and
you get a touch interface for the SEATS to pick up holographic images
on the workbench. Confirmed by Dakota Oct 27 ~18:00 EDT ("yes and yes"):
yes, the interface is for the seats (Mother + council), not only for
Dakota; yes, build this pick-up/put-down proof.

Toy mapping, stated not hidden:
- workbench = the Mesh ground plane in the toy (the one spatial
  structure, C3 — no second node store).
- holographic image = a rendered node.
- touch grab = a gesture bound to a node id. Voice may name it, as in
  hold/rotate; this prototype tests the grab/carry/release verbs.
- pick up = the node follows the hand while held. While held it is
  lifted: carry steps move it with NO body checks (it is not on the
  plane to collide with).
- put down = release at the hand's coordinates, WITH the existing
  field/body collision checks: candidates are nodes whose bubbles
  intersect the carried node's bubble at the candidate position
  (the field gate, same as avatar_try_move); a candidate blocks only
  if the distance to its centre is less than its body radius
  (the body check). A blocked release does NOT drop the node — it
  stays held, so the seat can move the hand elsewhere and retry.
- avatar carried: same rule. Its body is 0.0, so it never blocks
  another node as a body — but an avatar put-down is itself blocked
  by another node's body, exactly as avatar_try_move blocks it.

This is a 2D toy proof of the verbs, NOT a 3D holodeck, NOT hand
tracking, NOT touch hardware, NOT voice recognition.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_3d import mother, Renderer3D


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
    """Release at the node's current (hand) position. Returns (ok, blocker, evals)."""
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


# Demo world: the house from hold_rotate.py
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))

show(w, "BEFORE — house world:")
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "pickup_putdown_before.png"))

print()
print("1) SEAT PICKS UP ROCK 2, CARRIES IT, PUTS IT DOWN AT (4,9):")
rock2 = grab(w, 2)
carry(w, rock2, [(6, 6), (4, 9)])
print("  RELEASE at (4,9):")
ok, blocker, evals = try_release(w, rock2)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidate evaluated)")
assert ok and (rock2.x, rock2.y) == (4.0, 9.0)

print()
print("2) SEAT PICKS UP ROCK 3, TRIES TO PUT IT DOWN ON THE TREE AT (10,9):")
rock3 = grab(w, 3)
carry(w, rock3, [(10, 9)])
print("  RELEASE at (10,9):")
ok, blocker, evals = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidate evaluated)")
assert (not ok) and blocker == 1 and rock3.x == 10.0 and rock3.y == 9.0
print("  Blocked release does NOT drop it — rock 3 stays held at the hand.")
print("  Seat moves the hand to (13,8) and retries:")
carry(w, rock3, [(13, 8)])
print("  RELEASE at (13,8):")
ok, blocker, evals = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidate evaluated)")
assert ok and (rock3.x, rock3.y) == (13.0, 8.0)

print()
print("3) SEAT PICKS UP THE AVATAR, TRIES (10,9.5) INSIDE THE TREE BODY, THEN (10,7.5):")
av = grab(w, 99)
carry(w, av, [(10, 9.5)])
print("  RELEASE at (10,9.5):")
ok, blocker, evals = try_release(w, av)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidates evaluated)")
assert (not ok) and blocker == 1
print("  Seat moves the hand to (10,7.5) — inside the tree's field, outside its body — and retries:")
carry(w, av, [(10, 7.5)])
print("  RELEASE at (10,7.5):")
ok, blocker, evals = try_release(w, av)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)} ({evals} candidates evaluated)")
assert ok and (av.x, av.y) == (10.0, 7.5)

print()
show(w, "AFTER — final positions:")
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "pickup_putdown_after.png"))
print()
print("CHECKS:")
print(f"  rock 2: (7,4) -> (4,9) released: {'PASS' if (rock2.x, rock2.y) == (4.0, 9.0) else 'FAIL'}")
print(f"  rock 3: blocked on tree at (10,9), released at (13,8): {'PASS' if (rock3.x, rock3.y) == (13.0, 8.0) else 'FAIL'}")
print(f"  avatar: blocked at (10,9.5) inside tree body, released at (10,7.5) field-only: {'PASS' if (av.x, av.y) == (10.0, 7.5) else 'FAIL'}")
print(f"  tree 1 never moved: {'PASS' if (w.mesh.nodes[1].x, w.mesh.nodes[1].y) == (10.0, 9.0) else 'FAIL'}")
print("  overall: PASS — grab binds, carry follows, release checks field then body, blocked release holds")
