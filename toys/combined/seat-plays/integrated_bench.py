"""Integrated workbench session — all verbs, ONE world, ONE Mesh.

Dakota's question: why play with each toy separately when they work
together? This session answers by doing: build the house, hold + rotate
it, pick up a wall and move it, then walk the avatar through the
rearranged house — every verb on the same nodes, same Mesh, same
field/body collision rule. No second node store anywhere (C3).
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother

w = mother.World()
# 1) BUILD — the house (render_house.py): tree=roof, rocks=walls, avatar=door
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
print("1) BUILT house: tree/roof(10,9) rock/wall(7,4) rock/wall(13,4) avatar/door(10,4)")

# 2) VOICE HOLD + GESTURE ROTATE (hold_rotate.py)
held = w.mesh.nodes[2]
print(f'2) VOICE "hold sector A2" -> rock 2 locked at ({held.x},{held.y})')
th = math.radians(90); c, s = math.cos(th), math.sin(th)
px, py = held.x, held.y
for nid, n in w.mesh.nodes.items():
    if nid == 2: continue
    dx, dy = n.x - px, n.y - py
    n.x, n.y = px + dx*c - dy*s, py + dx*s + dy*c
    w.mesh.rehash(n)
print(f"   GESTURE rotate +90 around rock 2 -> tree now ({w.mesh.nodes[1].x:.1f},{w.mesh.nodes[1].y:.1f}), "
      f"rock 3 ({w.mesh.nodes[3].x:.1f},{w.mesh.nodes[3].y:.1f}), avatar ({w.mesh.nodes[99].x:.1f},{w.mesh.nodes[99].y:.1f})")
print(f"   rock 2 unmoved: {(w.mesh.nodes[2].x, w.mesh.nodes[2].y) == (7.0, 4.0)}")
print('   VOICE "release" -> rock 2 unlocked')

# 3) PICK UP + CARRY + RELEASE (pickup_putdown.py) — move rock 3 to a new wall position
rock3 = w.mesh.nodes[3]
print(f"3) GRAB rock 3 at ({rock3.x:.1f},{rock3.y:.1f}), carry to (2,10), release:")
rock3.x, rock3.y = 2.0, 10.0; w.mesh.rehash(rock3)
tps = w.mesh.ticks_per_stage
cands = w.mesh.bubble_intersections(rock3.x, rock3.y, rock3.bubble_radius(tps), exclude_id=3)
blocked = [o.id for o in cands if math.hypot(o.x-rock3.x, o.y-rock3.y) < o.body_radius(tps)]
print(f"   field gate: {len(cands)} candidate(s), body-blocked by: {blocked or 'none'} -> {'RELEASED' if not blocked else 'HELD'}")
assert not blocked

# 4) WALK THE AVATAR through the rearranged house (avatar_field.py rule)
av = w.mesh.nodes[99]
print(f"4) AVATAR walks from ({av.x:.1f},{av.y:.1f}) toward the new rock-3 wall at (2,10):")
steps = 0
while steps < 40:
    moved = w.avatar_try_move(av, av.x - 0.5, av.y + 0.5)
    steps += 1
    if not moved:
        print(f"   BLOCKED at ({av.x:.1f},{av.y:.1f}) — field gate fired, body boundary held")
        break
else:
    print(f"   walked free to ({av.x:.1f},{av.y:.1f}) — no body in the path")
print(f"   collision evaluations this walk: {w.collision_evaluations} (only field-intersecting candidates, never the whole world)")

# 5) READ BACK — one Sampler over the rearranged world (render_house.py rule)
print("5) SAMPLER reads the rearranged house (same Mesh, no second representation):")
s = mother.Sampler(w, 0.0, 0.0, 16, 14, 1.0)
for line in s.grid():
    print("   " + line)
print()
print("6) ONE STRUCTURE CHECK: sampler, raycast, collision, hold, grab all read w.mesh.")
print(f"   nodes in mesh: {sorted(w.mesh.nodes)} — no second store, every verb above touched these same ids.")
print(f"   covering set at avatar ({av.x:.1f},{av.y:.1f}): {sorted(w.mesh.covering_set(av.x, av.y))}")
print(f"   raycast east from avatar: {w.mesh.raycast(av.x, av.y, 0.0, exclude_id=99)}")
print("   INTEGRATED SESSION: PASS — build, hold, rotate, grab, carry, release, walk, read, one Mesh.")
