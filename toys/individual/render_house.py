import importlib.util, os, math
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mother", "seed_toy.py")
spec = importlib.util.spec_from_file_location("mother_seed_toy", path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

w = m.World()
# A house, built only from nodes in the one Mesh:
#  roof: mature tree node (bubble 5, glyph T)
#  walls: two rock nodes (bubble 2, glyph R)
#  door: avatar node (bubble 3, glyph @) standing in the doorway
w.add(m.Node(1, 10, 9, "tree", age=30))   # mature
w.add(m.Node(2, 7, 4, "rock"))
w.add(m.Node(3, 13, 4, "rock"))
w.add(m.Node(99, 10, 4, "avatar"))

print("NODES (id, kind, x, y, bubble, glyph):")
for nid, n in sorted(w.mesh.nodes.items()):
    print(f"  {nid} {n.kind} ({n.x},{n.y}) bubble={n.bubble_radius(w.mesh.ticks_per_stage)} glyph={n.glyph(w.mesh.ticks_per_stage)}")
print()
print("RENDER (Sampler grid, 21x14, res 1.0, top = max y):")
s = m.Sampler(w, 0.0, 0.0, 21, 14, 1.0)
for line in s.grid():
    print(line)
print()
print("CHECKS from the same Mesh (no second representation):")
print("  covering set at door (10,4):", sorted(w.mesh.covering_set(10, 4)))
print("  covering set at roof peak (10,9):", sorted(w.mesh.covering_set(10, 9)))
print("  covering set at empty ground (0,0):", sorted(w.mesh.covering_set(0, 0)))
print("  raycast east from (0,4):", w.mesh.raycast(0, 4, 0.0, exclude_id=None))
print("  glyph at door cell:", s.glyph_at(10, 4), "| glyph at roof cell:", s.glyph_at(10, 9))
