#!/usr/bin/env python3
"""LC-13 — one test for the D2 build-level mirage (Blink's stub).

Stub discipline: interface + ONE test against Twin's expectations.
This single test asserts the whole D2 build-level surface, mirroring
Control's harness D2 reference model (which is a reference model, not a
build test) plus the lifecycle and avatar-field pieces the harness
leaves to this aspect:

  1. construction density is 0.5 by design (10 pairs -> 10/20);
  2. an image is visible-but-inert (glyph "T", no bubble_radius
     attribute, not a mesh member, 0 collision evals);
  3. promotion is lazy node-hood (sweep promotes on approach; the node
     carries a bubble, 5.0, and keeps the image's id);
  4. lifecycle runs after promotion (mature -> decaying by the clock,
     bubble follows the stage table, id unchanged);
  5. collision applies after promotion ("until collision": the promoted
     node is body-checked by avatar_try_move, and a move into its body
     radius is blocked);
  6. determinism (same setup, same sweep outcome, run over run).

Run: python3 test_mirage.py   (stdlib only; exit 0 on PASS, non-zero
on any FAIL.)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirage
from mirage import mother


def test_d2_build():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    # --- setup: a 10-pair forest (20 visible), avatar at the origin ---
    world = mother.World()
    positions = [(10.0 + 4.0 * i, 0.0) for i in range(20)]
    nodes, images = mirage.build_forest(world, positions, first_id=1)
    avatar = mother.Node(99, 0.0, 0.0, "avatar")
    world.add(avatar)

    # 1. construction density is 0.5 by design.
    d = mirage.visible_density(nodes, images)
    check("D2 density 0.5 by construction", d == 0.5,
          f"{len(nodes)} nodes / {len(nodes) + len(images)} visible = {d}")

    # 2. an image is visible-but-inert.
    img = images[0]
    check("D2 image visible (glyph T)", img.glyph() == "T",
          f"glyph {img.glyph()!r}")
    check("D2 image has no bubble_radius attribute",
          not hasattr(img, "bubble_radius"))
    check("D2 image not a mesh member", img.id not in world.mesh.nodes)
    check("D2 image not in covering_set",
          img.id not in world.mesh.covering_set(img.x, img.y))
    check("D2 image not raycastable",
          world.mesh.raycast(0.0, 0.0, 0.0, exclude_id=avatar.id) is None
          or world.mesh.raycast(0.0, 0.0, 0.0, exclude_id=avatar.id)[0] != img.id)
    before = world.collision_evaluations
    moved = world.avatar_try_move(avatar, 2.0, 0.0)  # toward image 2's node, not the image
    check("D2 image costs 0 collision evals before promotion",
          world.collision_evaluations == before, f"evals {before} -> {world.collision_evaluations}")

    # 3. promotion is lazy node-hood (avatar walks toward image 2, id 2).
    #    Image 2 sits at (14, 0); avatar bubble radius is 3.0.
    target = images[0]  # id 2, at (14, 0)
    check("D2 no promotion while image outside bubble",
          mirage.sweep(world, avatar, images) == [])
    world.avatar_try_move(avatar, 12.0, 0.0)  # avatar now 2.0 from image 2
    made = mirage.sweep(world, avatar, images)
    check("D2 sweep promotes on approach", len(made) == 1 and made[0].id == target.id,
          f"promoted {[n.id for n in made]}")
    node = made[0]
    check("D2 promoted node keeps the image's id", node.id == target.id)
    check("D2 promoted node carries a bubble (5.0, mature)",
          node.bubble_radius(world.mesh.ticks_per_stage) == 5.0)
    check("D2 promoted node is a mesh member", node.id in world.mesh.nodes)
    check("D2 promoted node in covering_set",
          node.id in world.mesh.covering_set(node.x, node.y))
    check("D2 promoted node glyph still T (forest unchanged by promotion)",
          node.glyph(world.mesh.ticks_per_stage) == "T")
    check("D2 image spent (cannot promote twice)",
          target.promoted and (lambda: _double_promote(target, world))())

    # 4. lifecycle runs after promotion (mature -> decaying by the clock).
    tps = world.mesh.ticks_per_stage
    for _ in range(tps):
        world.tick()
    check("D2 promoted node advances mature -> decaying",
          node.stage(tps) == "decaying", f"stage {node.stage(tps)}")
    check("D2 bubble follows the stage table (5.0 -> 4.0)",
          node.bubble_radius(tps) == 4.0)
    check("D2 id unchanged through lifecycle", node.id == target.id)

    # 5. collision applies after promotion ("until collision").
    #    Node body radius at decaying: 4.0 * 0.2 = 0.8. Avatar at (12, 0),
    #    node at (14, 0): a move to (13.5, 0) enters the body radius.
    ev_before = world.collision_evaluations
    blocked = not world.avatar_try_move(avatar, 13.5, 0.0)
    check("D2 promoted node is body-checked (evals rise)",
          world.collision_evaluations > ev_before,
          f"evals {ev_before} -> {world.collision_evaluations}")
    check("D2 move into promoted node's body is blocked", blocked)
    check("D2 avatar stopped at the body boundary",
          abs(avatar.x - 12.0) < 1e-9, f"avatar at ({avatar.x}, {avatar.y})")

    # 6. determinism: rebuild, re-run, same outcome.
    w2 = mother.World()
    n2, i2 = mirage.build_forest(w2, positions, first_id=1)
    a2 = mother.Node(99, 0.0, 0.0, "avatar")
    w2.add(a2)
    w2.avatar_try_move(a2, 2.0, 0.0)
    w2.avatar_try_move(a2, 12.0, 0.0)
    m2 = mirage.sweep(w2, a2, i2)
    check("D2 sweep deterministic", [n.id for n in m2] == [n.id for n in made])

    print()
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        return 1
    print("PASS: D2 build-level mirage — all checks green.")
    return 0


def _double_promote(img, world):
    """Promoting twice must raise (the image is spent). Returns True if
    it raises as specified."""
    try:
        img.promote(world)
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    sys.exit(test_d2_build())
