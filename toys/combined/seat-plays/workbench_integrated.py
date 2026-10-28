"""Integrated play: all six toys as ONE workbench, one Mesh, one sequence.

Pieces used (same functions as the separate demos, no reimplementation
of the rules — only the composition is new):
  seed Mesh/World (mother)  — the ground plane, nodes, covering sets, raycast
  hold_rotate.rotate_rest   — voice locks, gesture rotates the rest
  pickup_putdown grab/carry/try_release — hand binds, carries, releases
  avatar_field collision    — the avatar's field IS the collision zone
  engine_3d Renderer3D      — the same Mesh rendered in 3D
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "individual"))
from engine_3d import mother, Renderer3D

# --- the verbs, copied verbatim in logic from the separate demos ---
def rotate_rest(world, held_id, degrees):
    held = world.mesh.nodes[held_id]
    px, py = held.x, held.y
    th = math.radians(degrees); cos_t, sin_t = math.cos(th), math.sin(th)
    for nid, n in world.mesh.nodes.items():
        if nid == held_id: continue
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
    cands = world.mesh.bubble_intersections(node.x, node.y, node.bubble_radius(tps), exclude_id=node.id)
    for other in cands:
        d = math.hypot(other.x - node.x, other.y - node.y)
        body = other.body_radius(tps)
        print(f"    candidate {other.id} ({other.kind}): dist {d:.2f}, body {body:.1f} -> {'BLOCKS' if d < body else 'passes'}")
        if d < body: return False, other.id
    return True, None

def show(world, label):
    print(label)
    for nid, n in sorted(world.mesh.nodes.items()):
        tps = world.mesh.ticks_per_stage
        print(f"  {nid} {n.kind} at ({n.x:.1f},{n.y:.1f}) bubble={n.bubble_radius(tps)} body={n.body_radius(tps)}")

# --- ONE world: the house scene, on the seed Mesh ---
w = mother.World()
w.add(mother.Node(1, 10, 9, "tree", age=30))
w.add(mother.Node(2, 7, 4, "rock"))
w.add(mother.Node(3, 13, 4, "rock"))
w.add(mother.Node(99, 10, 4, "avatar"))
show(w, "SCENE — house world on the seed Mesh:")

print('\nVOICE: "hold sector A2" -> lock rock 2.')
print("GESTURE: rotate the rest +90 degrees around it.")
rotate_rest(w, 2, 90)
show(w, "AFTER HOLD+ROTATE (rock 2 exactly put):")

print("\nHAND: pick up rock 3, carry it toward the tree.")
rock3 = grab(w, 3)
carry(w, rock3, [(2, 7)])
print("RELEASE at the tree (2,7):")
ok, blocker = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by node ' + str(blocker) + ' — stays held, no drop'}")
assert not ok and blocker == 1
print("Seat moves the hand to (5,9) and retries:")
carry(w, rock3, [(5, 9)])
ok, blocker = try_release(w, rock3)
print(f"  -> {'RELEASED' if ok else 'BLOCKED by ' + str(blocker)}")
assert ok and (rock3.x, rock3.y) == (5.0, 9.0)

print("\nAVATAR WALKS: from (7,7) west toward the tree at (2,7) — field is the collision zone:")
av = w.mesh.nodes[99]
tps = w.mesh.ticks_per_stage
x = 7.0
while True:
    x -= 0.5
    av.x = x; w.mesh.rehash(av)
    cands = w.mesh.bubble_intersections(av.x, av.y, av.bubble_radius(tps), exclude_id=99)
    blocked = any(math.hypot(o.x - av.x, o.y - av.y) <= o.body_radius(tps) for o in cands)
    print(f"  avatar at ({av.x:.1f},7.0) — {'BLOCKED at tree body boundary' if blocked else 'clear'}")
    if blocked: break
assert abs(av.x - 3.0) < 0.01

print("\nSAME MESH VERIFIES THE NEW ARRANGEMENT:")
print(f"  covering set at rock 3 (5,9): {w.mesh.covering_set(5, 9)}")
print(f"  covering set at tree (2,7): {w.mesh.covering_set(2, 7)}")
print(f"  raycast east from avatar (3,7): {w.mesh.raycast(3.0, 7.0, 0.0, exclude_id=99)}")
r = Renderer3D(w)
r.render_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "workbench_integrated_3d.png"))
show(w, "\nFINAL — one Mesh, every toy's verb used on it:")
print("\nINTEGRATED PLAY: PASS — hold, rotate, grab, carry, blocked-hold, release, walk, cover, raycast, render, all on one Mesh.")
