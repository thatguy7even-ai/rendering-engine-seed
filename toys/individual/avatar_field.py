import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_3d import mother

# Stable geometry, ticks_per_stage=1000 so stages do not drift mid-test
w = mother.World(ticks_per_stage=1000)
# Other nodes: fields are bubbles around a body (tree body=1.0, rock body=1.6)
w.add(mother.Node(1, 12, 0, "tree", age=3000))   # mature, bubble 5, body 1.0
w.add(mother.Node(2, -10, 8, "rock"))           # bubble 2, body 1.6, far from avatar path
w.add(mother.Node(3, 0, 12, "tree", age=3000))  # mature, north, far
w.add(mother.Node(4, 6, 6, "rock"))            # bubble 2, northeast, near avatar field on diagonal
avatar = mother.Node(99, 0, 0, "avatar")        # bubble 3 = collision field, body 0.0, center = position
w.add(avatar)

print("FIELDS (bubble = field; body = centre object, if any):")
for nid, n in sorted(w.mesh.nodes.items()):
    print(f"  {nid} {n.kind} at ({n.x},{n.y}) field/bubble={n.bubble_radius(w.mesh.ticks_per_stage)} body={n.body_radius(w.mesh.ticks_per_stage)} glyph={n.glyph(w.mesh.ticks_per_stage)}")
print()
print("AVATAR FIELD IS DIFFERENT: body 0.0, so there is no centre object to hit.")
print("  Its field IS the collision zone, and the avatar stays at its centre always.")
print("  Other nodes: field around a body; collision is body-check, field only gates it.")
print()

# Field map, 2D, distinct marks:
#  @ = avatar centre, o = avatar field only, X = avatar field + another field (collision-candidate zone)
#  T/R = other field only, . = empty
print("FIELD MAP (x -12..16, y 12..-4, res 1.0):")
print("  @ avatar centre | o avatar field only | X avatar field overlapping another field | T/R other field only | . empty")
for y in range(12, -5, -1):
    row = ""
    for x in range(-12, 17):
        cover = w.mesh.covering_set(x, y)
        if x == 0 and y == 0:
            row += "@"
        elif 99 in cover and len(cover) > 1:
            row += "X"
        elif 99 in cover:
            row += "o"
        elif cover:
            # representative glyph of other node
            nid = sorted(cover)[0]
            row += w.mesh.nodes[nid].glyph(w.mesh.ticks_per_stage)
        else:
            row += "."
    print("  " + row)
print()

# Collision test: walk east toward tree 1, step 0.5, exactly as T4
print("COLLISION TEST — walk east from (0,0) toward tree 1 at (12,0):")
w.tick_count = 0
evals_before = w.collision_evaluations
steps = 0
while True:
    before = w.collision_evaluations
    moved = w.avatar_try_move(avatar, avatar.x + 0.5, avatar.y)
    steps += 1
    if w.collision_evaluations > before:
        print(f"  step {steps}: first evaluation at avatar ({avatar.x:.1f},{avatar.y:.1f}) — tree bubble now intersects avatar field")
        break
    if steps > 40: break
while True:
    before = w.collision_evaluations
    moved = w.avatar_try_move(avatar, avatar.x + 0.5, avatar.y)
    steps += 1
    if not moved:
        print(f"  step {steps}: BLOCKED at avatar ({avatar.x:.1f},{avatar.y:.1f}), distance to tree centre {math.hypot(12-avatar.x, avatar.y):.1f} = tree body boundary 1.0")
        break
print(f"  total collision evaluations in walk: {w.collision_evaluations - evals_before}")
print(f"  nodes NEVER evaluated in this walk: rock 2 (far), tree 3 (north), rock 4 (diagonal, field never intersected on east path) — their fields never entered the avatar field")
print()
# Diagonal check: does rock 4 intersect avatar field at start?
print("  bubble_intersections at avatar start (0,0), radius 3:", [n.id for n in w.mesh.bubble_intersections(0, 0, 3.0, exclude_id=99)])
print("  bubble_intersections at (6,0) east path, radius 3:", [n.id for n in w.mesh.bubble_intersections(6, 0, 3.0, exclude_id=99)])
