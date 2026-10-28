import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_3d import Renderer3D, house_world, mother

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
# 1. House, via the integrated renderer (not the earlier hand script)
w = house_world(); r = Renderer3D(w)
print("house nodes_3d:", r.nodes_3d())
print("house png:", r.render_png(f"{out}/house_integrated_3d.png"))
print("house obj verts/faces:", r.export_obj(f"{out}/house.obj"))
# 2. Lifecycle proof: same Mesh, tick a seed tree to mature, re-render reads it live
w2 = mother.World(); w2.add(mother.Node(1, 10, 10, "tree", age=0))
r2 = Renderer3D(w2)
before = r2.nodes_3d()[1]
for _ in range(30): w2.tick()
after = r2.nodes_3d()[1]
print("tree before tick:", before)
print("tree after 30 ticks:", after)
print("grown png:", r2.render_png(f"{out}/tree_grown_3d.png"))
print("grown obj verts/faces:", r2.export_obj(f"{out}/tree_grown.obj"))
# 3. Scatter world from the seed toy itself
w3 = mother.scatter_world(); r3 = Renderer3D(w3)
print("scatter nodes:", len(r3.nodes_3d()))
print("scatter png:", r3.render_png(f"{out}/scatter_3d.png"))
print("scatter obj verts/faces:", r3.export_obj(f"{out}/scatter.obj"))
