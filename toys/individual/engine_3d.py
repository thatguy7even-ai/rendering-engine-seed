"""Next step: 3D view cannibalized onto Mother's rendering-engine seed toy.

CANNIBALIZED, with sources:
  - Mother seed toy (rendering-engine-seed-repo/mother/seed_toy.py):
    Node, Mesh, World, Sampler. The Mesh is STILL the one spatial
    structure (C3). This file holds NO node store of its own: it reads
    world.mesh.nodes live, every render. Move a node, tick a tree, and
    the next render changes with no re-registration.
  - Matplotlib mplot3d (already installed, no download):
    3D axes, sphere surfaces, camera elevation/azimuth, PNG output.
  - Trimesh's mesh-export idea, reimplemented in stdlib+numpy:
    spheres tessellated to vertices/faces and written as OBJ, so the
    scene becomes a real 3D file Blender can open later. No trimesh
    download was made for this step.
  - Alpha mesh core (alpha/mesh_core.py, A7 ruling):
    avatar is a rendering node at its core, internal render FIRST
    (bones, muscles, ligaments, in that order), collision SECOND.
    Internal rendering is still NAMED ONLY here: no articulation
    model exists in the toy, so no bones are faked as geometry.
    Control's UNMEASURABLE mark for internal rendering STANDS.

3D LIFT RULE (stated, not hidden): the toy Mesh is 2D (x, y).
  - tree / rock: sphere centre z = bubble radius, so the sphere
    sits on the ground plane z=0. Radius = bubble radius.
  - terrain: flattened disc, centre z = 0.1, radius = bubble.
  - avatar: centre z = 1.5, radius = 1.0, annotated with its
    internal-render order. Its bubble (3.0) remains the collision
    field, NOT its body — body radius in the toy is 0.0.
"""
import importlib.util, math, os
import numpy as np

_MOTHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mother", "seed_toy.py")
_spec = importlib.util.spec_from_file_location("mother_seed_toy", _MOTHER)
mother = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(mother)

TREE_COLOR = {"seed": "#90ee90", "sapling": "#32cd32", "adolescent": "#228b22",
              "mature": "#006400", "decaying": "#8b4513", "static": "#808080"}
KIND_COLOR = {"rock": "#808080", "terrain": "#d2b48c", "avatar": "#ff0000"}

def node_3d(node, tps):
    """Live read from a Mesh node -> (x, y, z, radius, color, label, flatten)."""
    r = node.bubble_radius(tps)
    if node.kind == "tree":
        stage = node.stage(tps)
        return (node.x, node.y, r, r, TREE_COLOR[stage], f"tree:{stage}", 1.0)
    if node.kind == "terrain":
        return (node.x, node.y, 0.1, r, KIND_COLOR["terrain"], "terrain", 0.08)
    if node.kind == "avatar":
        parts = getattr(node, "internal_render", lambda: ["bones", "muscles", "ligaments"])()
        return (node.x, node.y, 1.5, 1.0, KIND_COLOR["avatar"],
                "avatar:" + ">".join(parts) + " (order only)", 1.0)
    return (node.x, node.y, r, r, KIND_COLOR[node.kind], node.kind, 1.0)

class Renderer3D:
    """Holds only a World reference. No node store. C3 preserved."""
    def __init__(self, world):
        self.world = world
    def nodes_3d(self):
        tps = self.world.mesh.ticks_per_stage
        return {nid: node_3d(n, tps) for nid, n in sorted(self.world.mesh.nodes.items())}
    def render_png(self, path, elev=20, azim=-60):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d")
        u = np.linspace(0, 2*np.pi, 24); v = np.linspace(0, np.pi, 16)
        for nid, (x, y, z, r, c, label, flat) in self.nodes_3d().items():
            xs = x + r*np.outer(np.cos(u), np.sin(v))
            ys = y + r*np.outer(np.sin(u), np.sin(v))
            zs = z + flat*r*np.outer(np.ones_like(u), np.cos(v))
            ax.plot_surface(xs, ys, zs, color=c, alpha=0.55, linewidth=0)
            ax.text(x, y, z + r + 0.5, f"{nid}:{label}", fontsize=7)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
        ax.set_title("Rendering-engine nodes, in 3D — read live from the one Mesh")
        ax.view_init(elev=elev, azim=azim)
        plt.tight_layout(); os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True); plt.savefig(path, dpi=150); plt.close()
        return path
    def export_obj(self, path, nu=12, nv=8):
        """Sphere per node -> OBJ vertices/faces. Returns (verts, faces)."""
        verts, faces, voff = [], [], 0
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            for nid, (x, y, z, r, c, label, flat) in self.nodes_3d().items():
                f.write(f"o node_{nid}_{label}\n")
                for j in range(nv+1):
                    phi = math.pi * j / nv
                    for i in range(nu):
                        th = 2*math.pi * i / nu
                        verts.append((x + r*math.sin(phi)*math.cos(th),
                                      y + r*math.sin(phi)*math.sin(th),
                                      z + flat*r*math.cos(phi)))
                for j in range(nv):
                    for i in range(nu):
                        a = voff + j*nu + i + 1
                        b = voff + j*nu + (i+1) % nu + 1
                        cc = voff + (j+1)*nu + i + 1
                        d = voff + (j+1)*nu + (i+1) % nu + 1
                        faces.append((a, b, d)); faces.append((a, d, cc))
                voff += (nv+1)*nu
            for vx, vy, vz in verts:
                f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")
            for a, b, cc in faces:
                f.write(f"f {a} {b} {cc}\n")
        return len(verts), len(faces)

def house_world():
    w = mother.World()
    w.add(mother.Node(1, 10, 9, "tree", age=30))
    w.add(mother.Node(2, 7, 4, "rock"))
    w.add(mother.Node(3, 13, 4, "rock"))
    w.add(mother.Node(99, 10, 4, "avatar"))
    return w
