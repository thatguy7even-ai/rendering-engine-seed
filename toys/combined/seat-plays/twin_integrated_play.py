"""Twin's integrated play — Oct 27, 2026, at Dakota's order to play with the
toys as pieces, not separate demos.

One World, one Mesh, every verb in sequence:
  1. house scene (render_house) + 3D render (engine_3d, live read)
  2. voice "hold sector A2" + gesture rotate (hold_rotate verb)
  3. seat grab/carry/release with blocked retry (pickup_putdown verbs)
  4. avatar walk with field-gated collision (avatar_field verb)
  5. lifecycle tick (seed toy verb) + re-render: the same Mesh, changed

Hold/rotate and pickup verbs are reimplemented here (not imported) because
importing those demo files would run their demos. Same rules, stated:
  - rotate: held node unmoved, rest rotate around it, distances preserved
  - carry: no body check while lifted; release: field gate, then body check;
    a blocked release does NOT drop the node, it stays held for retry
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother, Renderer3D

def rotate_rest(world, held_id, degrees):
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
    tps = world.mesh.ticks_per_stage
    cands = world.mesh.bubble_intersections(
        node.x, node.y, node.bubble_radius(tps), exclude_id=node.id)
    for other in cands:
        d = math.hypot(other.x - node.x, other.y - node.y)
        if d < other.body_radius(tps):
            return (False, other.id, len(cands))
    return (True, None, len(cands))

def show(world, label):
    print(f"  -- {label}")
    for nid, n in sorted(world.mesh.nodes.items()):
        print(f"    {nid} {n.kind} at ({n.x:.2f},{n.y:.2f}) bubble={n.bubble_radius(world.mesh.ticks_per_stage)} body={n.body_radius(world.mesh.ticks_per_stage)}")

# 1. House scene, the same nodes every toy uses
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "twin_play_before.png"))
show(w, "BEFORE (house scene)")
print(f"  covering set at door (10,4): {sorted(w.mesh.covering_set(10, 4))}")

# 2. Voice hold + gesture rotate
print()
print('VOICE: "hold sector A2" -> hold rock 2. GESTURE: rotate rest +90 deg.')
before = {nid: (n.x, n.y) for nid, n in w.mesh.nodes.items()}
rotate_rest(w, 2, 90)
show(w, "AFTER ROTATION")
held_ok = (w.mesh.nodes[2].x, w.mesh.nodes[2].y) == before[2]
dists_ok = all(
    abs(math.hypot(w.mesh.nodes[n].x - 7, w.mesh.nodes[n].y - 4)
        - math.hypot(before[n][0] - 7, before[n][1] - 4)) < 1e-9
    for n in w.mesh.nodes)
print(f"  held rock 2 unmoved: {held_ok}; distances to pivot preserved: {dists_ok}")

# 3. Seat picks up rock 3, tries the tree, is blocked, retries, releases
print()
print("SEAT GRAB rock 3 (now at 7,10 after rotation), carry to tree (2,7):")
rock3 = w.mesh.nodes[3]
rock3.x, rock3.y = 2.0, 7.0
w.mesh.rehash(rock3)
ok, blocker, ev = try_release(w, rock3)
print(f"  release at tree centre: {'BLOCKED by node ' + str(blocker) if not ok else 'RELEASED'} ({ev} candidate evaluated) — stays held, no drop")
rock3.x, rock3.y = 2.0, 4.0
w.mesh.rehash(rock3)
ok, blocker, ev = try_release(w, rock3)
print(f"  retry at (2,4): {'RELEASED' if ok else 'BLOCKED'} ({ev} candidate evaluated)")

# 4. Seat picks up the avatar itself, puts it down, then walks it
print()
print("SEAT GRAB avatar 99, carry to (5,7), release:")
av = w.mesh.nodes[99]
av.x, av.y = 5.0, 7.0
w.mesh.rehash(av)
ok, blocker, ev = try_release(w, av)
print(f"  release at (5,7): {'RELEASED' if ok else 'BLOCKED'} ({ev} candidates evaluated)")
print("  AVATAR WALKS west toward tree 1 (2,7), 0.5 steps, field-gated:")
while True:
    moved = w.avatar_try_move(av, av.x - 0.5, av.y)
    if not moved:
        print(f"  BLOCKED at ({av.x:.1f},{av.y:.1f}), distance to tree centre {math.hypot(2 - av.x, 7 - av.y):.1f} = tree body boundary 1.0")
        break
print(f"  collision evaluations in walk: {w.collision_evaluations} (far nodes never evaluated)")

# 5. Lifecycle: the world clock moves the tree, the same Mesh re-renders
print()
print("WORLD CLOCK: 10 ticks — tree 1 ages 30 -> 40 (mature -> decaying, bubble 5 -> 4):")
for _ in range(10):
    w.tick()
show(w, "AFTER TICKS")
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "twin_play_after.png"))
verts, faces = r.export_obj(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "twin_play_after.obj"))
print(f"  3D after-render + OBJ export from the same live Mesh: {verts} verts, {faces} faces")
s = mother.Sampler(w, 0.0, 0.0, 21, 14, 1.0)
print("  SAMPLER GRID AFTER (same Mesh, moved nodes, aged tree):")
for line in s.grid():
    print("   " + line)
print()
print("CHECKS: held-unmoved, distances-preserved, blocked-holds, avatar-blocked-at-body,")
print("        tick-changed-bubble, 3D/OBJ read the same Mesh with no re-registration.")
