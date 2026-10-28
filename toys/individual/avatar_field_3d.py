import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, os
# Scene at blocked position: avatar at (11,0), tree at (12,0), rock far
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
u = np.linspace(0, 2*np.pi, 24); v = np.linspace(0, np.pi, 16)
def sphere(x, y, z, r, color, alpha, wire=False):
    xs = x + r*np.outer(np.cos(u), np.sin(v))
    ys = y + r*np.outer(np.sin(u), np.sin(v))
    zs = z + r*np.outer(np.ones_like(u), np.cos(v))
    if wire:
        ax.plot_wireframe(xs, ys, zs, color=color, alpha=0.9, linewidth=0.5)
    else:
        ax.plot_surface(xs, ys, zs, color=color, alpha=alpha, linewidth=0)
# Other node field: tree bubble solid green, body small dark sphere at centre
sphere(12, 0, 5, 5, "green", 0.35)
sphere(12, 0, 1, 1, "darkgreen", 0.9)
# Avatar field: DISTINCT — wireframe red sphere, radius 3, centre = avatar, no body sphere
sphere(11, 0, 3, 3, "red", 0.9, wire=True)
ax.scatter([11], [0], [3], color="red", s=60, label="avatar centre")
ax.text(11, 0, 6.5, "avatar FIELD (wireframe, radius 3)\ncentre = avatar, body = 0", fontsize=8, color="red")
ax.text(12, 0, 11, "tree FIELD (solid, radius 5)\nbody at centre, radius 1.0", fontsize=8, color="darkgreen")
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
ax.set_title("Avatar field vs other fields — avatar field is the collision zone itself")
ax.view_init(elev=20, azim=-60)
plt.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "avatar_field_3d.png")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
plt.savefig(out, dpi=150)
print(out)
