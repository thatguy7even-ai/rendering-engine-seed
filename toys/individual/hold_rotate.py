"""Hollow-deck hold + rotate prototype — Oct 27, 2026, Dakota's verb, not a holodeck claim.

Dakota, Oct 27 ~15:17 EDT, on the @codecrafters60 agentic-coding TikTok:
unlike the video's silent gesturer, he would ALSO speak on top of gestures.
Gestures become key bindings. Example he gave: say "hold sector A2" to hold
something inside the image, then rotate the rest of it with his hand.

Prototype mapping, stated not hidden:
- VOICE = discrete command: hold / release. It names the thing to lock.
  Here the demo holds node 2 (the rock inside the demo's "sector A2" —
  sector naming is Dakota's to pin; the prototype does not invent a grid).
- GESTURE = continuous manipulation: rotation angle in degrees, around the
  held thing. The held thing is the pivot AND stays fixed.
- HOLD = lock: held node's x,y do not move at all during rotation.
  All other nodes rotate around the held node's position, distances to
  the pivot preserved exactly (rotation, not scaling, not translation).

Uses Mother's seed toy Mesh/World only — no second node store (C3).
This is a 2D toy proof of the interaction verb, NOT a 3D holodeck,
NOT a hand-tracking system, NOT a voice recognizer.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_3d import mother, Renderer3D

def rotate_rest(world, held_id, degrees):
    """Rotate every node except held_id around held node's position."""
    held = world.mesh.nodes[held_id]
    px, py = held.x, held.y
    th = math.radians(degrees)
    cos_t, sin_t = math.cos(th), math.sin(th)
    before = {nid: (n.x, n.y) for nid, n in world.mesh.nodes.items()}
    for nid, n in world.mesh.nodes.items():
        if nid == held_id:
            continue
        dx, dy = n.x - px, n.y - py
        n.x = px + dx * cos_t - dy * sin_t
        n.y = py + dx * sin_t + dy * cos_t
        # Patch Oct 27, 2026 (Dakota's "Patch it"): rehash each rotated
        # node, per carry()'s convention — otherwise the Mesh spatial
        # hash goes stale and a post-rotation release check reads
        # pre-rotation cells (Control/Four/Blink/Gamma bug, Oct 27).
        world.mesh.rehash(n)
    return before

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# Demo world: the house from render_house.py, via engine_3d.house_world()
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))

print("BEFORE — voice: (none yet)")
for nid, n in sorted(w.mesh.nodes.items()):
    print(f"  {nid} {n.kind} at ({n.x:.2f},{n.y:.2f})")

r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "hold_rotate_before.png"))

print()
print('VOICE COMMAND: "hold sector A2" -> hold node 2 (rock at 7,4).')
print("  Node 2 is now LOCKED: it will not move during rotation.")
held_pos = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
dists_before = {nid: dist((n.x, n.y), held_pos) for nid, n in w.mesh.nodes.items()}

print()
print("GESTURE: rotate rest +90 degrees (counter-clockwise) around held node 2.")
before = rotate_rest(w, held_id=2, degrees=90)

print("AFTER:")
for nid, n in sorted(w.mesh.nodes.items()):
    print(f"  {nid} {n.kind} at ({n.x:.2f},{n.y:.2f})")

r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "hold_rotate_after.png"))

print()
print("CHECKS:")
held_after = (w.mesh.nodes[2].x, w.mesh.nodes[2].y)
print(f"  held node 2 moved? {held_after} vs {held_pos} -> {'NO — locked' if held_after == held_pos else 'MOVED — FAIL'}")
ok = True
for nid, n in w.mesh.nodes.items():
    d = dist((n.x, n.y), held_after)
    same = abs(d - dists_before[nid]) < 1e-9
    ok = ok and same
    print(f"  node {nid} distance to pivot: {dists_before[nid]:.4f} -> {d:.4f} {'preserved' if same else 'CHANGED — FAIL'}")
print(f"  overall: {'PASS — hold locks, rest rotates around it' if ok and held_after == held_pos else 'FAIL'}")
print()
print("VOICE RELEASE (not executed in this run, stated for completeness):")
print('  Say "release" -> node 2 unlocks, next gesture moves everything again.')
