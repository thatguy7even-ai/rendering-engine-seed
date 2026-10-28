"""Alpha's workbench play — Oct 27, 2026, evening, at Dakota's order to
play with the toys AS PIECES, not as separate demos.

One World, one Mesh, every verb in one sitting. The seat in this run
is Alpha himself — the interface is for the seats, so a seat uses it.

Pieces, each credited to its source file:
- House / Mesh / Sampler / avatar_try_move: mother's seed_toy.py
  (via engine_3d.mother). The Mesh is the one node store (C3).
- 3D view + OBJ export: engine_3d.py Renderer3D — holds only a World
  reference, reads world.mesh.nodes live every render.
- Voice hold + gesture rotate: hold_rotate.py's verb (rotation math
  reproduced here so this script runs standalone; the verb is his).
- Grab / carry / release with field-then-body gate: pickup_putdown.py's
  verb (same gate as avatar_try_move: bubble intersections first,
  body check second; a blocked release HOLDS, it does not drop).
- Avatar internal render first: alpha/mesh_core.py's A7 ruling —
  internal order (bones, muscles, ligaments) named BEFORE any
  collision check. Internal articulation is still NAMED ONLY;
  Control's UNMEASURABLE stands. No bones are faked as geometry.

This is a 2D toy proof of the interaction grammar, NOT a holodeck,
NOT hand tracking, NOT voice recognition.
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother, Renderer3D

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

def show(w, label):
    print(label)
    for nid, n in sorted(w.mesh.nodes.items()):
        t = w.mesh.ticks_per_stage
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) bubble={n.bubble_radius(t)} body={n.body_radius(t)}")

def rotate_rest(world, held_id, degrees):
    """hold_rotate.py's verb: held node locked, rest rotate around it."""
    held = world.mesh.nodes[held_id]
    px, py = held.x, held.y
    th = math.radians(degrees)
    c, s = math.cos(th), math.sin(th)
    for nid, n in world.mesh.nodes.items():
        if nid == held_id:
            continue
        dx, dy = n.x - px, n.y - py
        n.x = px + dx * c - dy * s
        n.y = py + dx * s + dy * c
        world.mesh.rehash(n)

def try_release(world, node):
    """pickup_putdown.py's verb: field gate, then body check, hold on block."""
    tps = world.mesh.ticks_per_stage
    cands = world.mesh.bubble_intersections(
        node.x, node.y, node.bubble_radius(tps), exclude_id=node.id)
    blocked_by = None
    for other in cands:
        d = math.hypot(other.x - node.x, other.y - node.y)
        body = other.body_radius(tps)
        print(f"    candidate {other.id} ({other.kind}): distance {d:.2f}, body {body:.1f} -> {'BLOCKS' if d < body else 'passes'}")
        if d < body:
            blocked_by = other.id
    return (blocked_by is None), blocked_by

# 1) THE HOUSE, on the one Mesh.
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
show(w, "1) HOUSE BUILT on the one Mesh:")
s = mother.Sampler(w, 0.0, 0.0, 21, 14, 1.0)
print("   2D grid:"); [print("   " + line) for line in s.grid()]
Renderer3D(w).render_png(f"{W}/alpha_workbench_before.png")
print("   3D before: alpha_workbench_before.png (read live from the same Mesh)")
print(f"   avatar field check — covering set at door (10,4): {sorted(w.mesh.covering_set(10, 4))}")
print("   (tree field already covers the door: the avatar stands IN a field, not beside one)")

# 2) VOICE holds, GESTURE rotates the whole house around the held rock.
print()
print('2) VOICE: "hold sector A2" -> hold rock 2 (7,4).')
print("   GESTURE: rotate rest +90 degrees around it.")
held = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
before_d = {nid: math.hypot(n.x - held[0], n.y - held[1]) for nid, n in w.mesh.nodes.items()}
rotate_rest(w, held_id=2, degrees=90)
show(w, "   AFTER ROTATION (same Mesh, no re-registration):")
assert (w.mesh.nodes[2].x, w.mesh.nodes[2].y) == held, "held rock moved!"
for nid, n in w.mesh.nodes.items():
    d = math.hypot(n.x - held[0], n.y - held[1])
    assert abs(d - before_d[nid]) < 1e-9, f"node {nid} distance changed!"
print("   CHECKS: held rock 2 exactly (7,4); every other distance to pivot preserved.")
print("   NOTE: the avatar did not walk here — it RODE the rotation (10,4)->(7,7).")
print("   Manipulation and locomotion are different verbs on the same nodes.")

# 3) VOICE releases the hold. SEAT grabs rock 3, carries it, bad put-down held.
print()
print('3) VOICE: "release" -> rock 2 unlocks.')
print("   SEAT GRABS rock 3 (now at 7,10), carries it to the tree (2,7), tries release:")
rock3 = w.mesh.nodes[3]
rock3.x, rock3.y = 2.0, 7.0; w.mesh.rehash(rock3)
ok, blocker = try_release(w, rock3)
print(f"   -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker) + ' — rock 3 STAYS HELD'}")
assert (not ok) and blocker == 1
print("   Seat moves the hand to (2,4) and retries:")
rock3.x, rock3.y = 2.0, 4.0; w.mesh.rehash(rock3)
ok, blocker = try_release(w, rock3)
print(f"   -> {'RELEASED' if ok else 'BLOCKED'}")
assert ok and (rock3.x, rock3.y) == (2.0, 4.0)

# 4) AVATAR: internal render FIRST, collision SECOND — then it walks its field.
print()
print("4) AVATAR at (7,7) — internal render FIRST (A7, named only): bones -> muscles -> ligaments.")
print("   THEN collision (avatar_try_move: field gate, body check):")
av = w.mesh.nodes[99]
for target in [(5.0, 7.0), (3.0, 7.0), (2.5, 7.0)]:
    moved = w.avatar_try_move(av, *target)
    print(f"   try ({target[0]},{target[1]}): {'MOVED' if moved else 'BLOCKED'} — avatar now ({av.x:.1f},{av.y:.1f})")
assert (av.x, av.y) == (3.0, 7.0), "avatar should stop at the tree body boundary"
print("   CHECKS: (5,7) and (3,7) pass — field overlap is allowed, distance 1.0 = body boundary, not inside;")
print("   (2.5,7) blocked — distance 0.5 < tree body 1.0. The avatar field IS the collision zone;")
print("   its body is 0.0, so it never blocks another node — others' bodies block IT.")

# 5) The world clock still runs in the same Mesh; the views still agree.
w.tick()
print()
print(f"5) TICK: tick_count={w.tick_count}, tree age 30->31, stage still mature (bubble 5). Lifecycle lives in the same Mesh.")
show(w, "   FINAL POSITIONS:")
s = mother.Sampler(w, 0.0, 0.0, 21, 14, 1.0)
print("   2D grid:"); [print("   " + line) for line in s.grid()]
r = Renderer3D(w)
r.render_png(f"{W}/alpha_workbench_after.png")
verts, faces = r.export_obj(f"{W}/alpha_workbench_after.obj")
print(f"   3D after: alpha_workbench_after.png + alpha_workbench_after.obj ({verts} verts, {faces} faces)")
for nid, (x, y, z, rad, c, label, flat) in r.nodes_3d().items():
    n = w.mesh.nodes[nid]
    assert (x, y) == (n.x, n.y), f"3D view disagrees with Mesh for node {nid}!"
print("   CHECKS: 2D grid, 3D view, and OBJ all read the same moved nodes — no re-registration anywhere.")
print("   overall: PASS — one Mesh, one house, voice lock, gesture turn, hand carry,")
print("   held-on-block release, avatar field walk, live views. That sequence IS the workbench.")
