import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Same house nodes, lifted to 3D: (x, y, z, radius, color, label)
nodes = [
    (10, 9, 6, 5.0, "green", "roof/tree"),
    (7, 4, 2, 2.0, "gray", "left wall/rock"),
    (13, 4, 2, 2.0, "gray", "right wall/rock"),
    (10, 4, 1.5, 1.5, "red", "door/avatar"),
]
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
u = np.linspace(0, 2*np.pi, 24); v = np.linspace(0, np.pi, 16)
for x, y, z, r, c, label in nodes:
    xs = x + r*np.outer(np.cos(u), np.sin(v))
    ys = y + r*np.outer(np.sin(u), np.sin(v))
    zs = z + r*np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(xs, ys, zs, color=c, alpha=0.55, linewidth=0)
    ax.scatter([x], [y], [z], color=c, s=20)
    ax.text(x, y, z+r+0.5, label, fontsize=8)
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
ax.set_title("House from rendering-engine nodes, in 3D (matplotlib, no download)")
ax.set_xlim(0, 20); ax.set_ylim(0, 18); ax.set_zlim(0, 14)
plt.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "house_3d.png")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
plt.savefig(out, dpi=150)
print(out)
