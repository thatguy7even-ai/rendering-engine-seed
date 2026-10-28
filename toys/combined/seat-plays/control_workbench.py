"""Control's workbench session — the six toys as ONE session, not six demos.

One Mesh (mother's seed toy), one world, one continuous sequence:
  see (3D render) -> voice-lock (hold) -> gesture (rotate rest)
  -> grab/carry/release (pickup/putdown) -> walk (avatar field)
  -> tick (lifecycle) -> read back (covering set / raycast / glyph).

Every verb below operates on world.mesh.nodes. No second node store
is created anywhere in this file.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother, Renderer3D


def rotate_rest(world, held_id, degrees):
    """hold_rotate.py's verb, reused verbatim in shape."""
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


def try_release(world, node):
    """pickup_putdown.py's verb, reused verbatim in shape."""
    tps = world.mesh.ticks_per_stage
    cands = world.mesh.bubble_intersections(
        node.x, node.y, node.bubble_radius(tps), exclude_id=node.id)
    for other in cands:
        d = math.hypot(other.x - node.x, other.y - node.y)
        if d < other.body_radius(tps):
            return False, other.id
    return True, None


def show(world, label):
    tps = world.mesh.ticks_per_stage
    print(label)
    for nid, n in sorted(world.mesh.nodes.items()):
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) "
              f"bubble={n.bubble_radius(tps)} body={n.body_radius(tps)}")


# 1) THE WORLD — the house-world scene all the toy demos share.
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "control_workbench_before.png"))
show(w, "BEFORE — one world, one Mesh:")

# 2) VOICE LOCKS, GESTURE MOVES — "hold sector A2", rotate rest +90.
print()
print('VOICE: "hold sector A2" -> rock 2 locked.')
print("GESTURE: rotate rest +90 degrees around rock 2.")
rotate_rest(w, held_id=2, degrees=90)
# COMPOSITION FINDING (see note at the end): rotate_rest moves nodes by
# direct assignment and does NOT rehash — the Mesh's spatial hash still
# holds pre-rotation cells. Any mesh query after a rotation (release
# check, covering set, collision) reads STALE positions until rehash.
# The mover must rehash, per the codebase's own convention (carry()
# rehashes every step; avatar_try_move rehashes). Rehash all moved nodes:
for _n in w.mesh.nodes.values():
    w.mesh.rehash(_n)
show(w, "AFTER ROTATION (rock 2 exactly put, everything else moved):")
assert (w.mesh.nodes[2].x, w.mesh.nodes[2].y) == (7.0, 4.0)

# 3) GRAB / CARRY / RELEASE — rock 3, blocked on the tree, then clear.
rock3 = w.mesh.nodes[3]
print()
print(f"GRAB rock 3 at ({rock3.x:.1f},{rock3.y:.1f}) — bound to the hand.")
tree = w.mesh.nodes[1]
rock3.x, rock3.y = tree.x, tree.y  # hand moves onto the tree
w.mesh.rehash(rock3)
ok, blocker = try_release(w, rock3)
print(f"RELEASE on the tree -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker)}"
      f" — blocked release HOLDS, rock 3 stays at the hand.")
assert not ok and blocker == 1
rock3.x, rock3.y = 13.0, 8.0  # hand moves clear, retry
w.mesh.rehash(rock3)
ok, blocker = try_release(w, rock3)
print(f"RELEASE at (13,8) -> {'RELEASED' if ok else 'BLOCKED'}")
assert ok

# 4) WALK — avatar field collision, body 0, field IS the zone.
# NOTE: the walk meets the world as the earlier verbs left it. After the
# rotation the tree sits WEST at (2,7), so walking east does NOT meet
# the tree — it meets rock 3, which this session placed at (13,8).
# That is the workbench behaving like a world, not a script: earlier
# manipulations change later collisions. The check is therefore
# general: stopped outside all bodies, one step short of penetration.
av = w.mesh.nodes[99]
print()
print(f"AVATAR WALK east from ({av.x:.1f},{av.y:.1f}):")
steps = 0
while steps < 40:
    moved = w.avatar_try_move(av, av.x + 0.5, av.y)
    steps += 1
    if not moved:
        break
tps = w.mesh.ticks_per_stage
free = all(math.hypot(n.x - av.x, n.y - av.y) >= n.body_radius(tps)
           for n in w.mesh.nodes.values() if n.id != av.id)
cand = (av.x + 0.5, av.y)
blocked_by = [n.id for n in w.mesh.nodes.values() if n.id != av.id
              and math.hypot(n.x - cand[0], n.y - cand[1])
              < n.body_radius(tps)]
print(f"  blocked after {steps} steps at ({av.x:.1f},{av.y:.1f}); "
      f"current position free of all bodies: {free}; "
      f"next candidate {cand} would penetrate body of node(s) {blocked_by}")
assert free and blocked_by

# 5) TICK — the lifecycle still runs on the same Mesh.
w.tick()
print()
print("TICK — lifecycle advanced on the same Mesh; tree still mature.")

# 6) READ BACK — covering set, raycast, glyph, all from the same Mesh.
samp = mother.Sampler(w, 0, 0, 26, 13, 1.0)
print()
print("READ BACK through the same Mesh (no second representation):")
print(f"  covering set at avatar ({av.x:.1f},{av.y:.1f}): "
      f"{sorted(w.mesh.covering_set(av.x, av.y))}")
print(f"  raycast east from avatar: {w.mesh.raycast(av.x, av.y, 0.0)}")
print(f"  glyph at tree cell: "
      f"{w.mesh.nodes[1].glyph(w.mesh.ticks_per_stage)}")

r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "control_workbench_after.png"))
show(w, "AFTER — final world state:")
print()
print("OVERALL: PASS — hold, rotate, grab, carry, release, walk, tick, "
      "and read-back all operated on world.mesh.nodes, one store.")
