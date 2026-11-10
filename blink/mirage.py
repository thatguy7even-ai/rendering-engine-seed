#!/usr/bin/env python3
"""LC-13 — D2 build-level mirage (lifecycle + avatar-field aspect stub).

[ORG-MUSE | BLINK | LC-13 STUB | 2026-11-09]

Fourth and last aspect of LC-6 (spec §5): Four's lifecycle + avatar-field
work, reassigned to Blink Nov 7, 2026 (INN-142 comment 4860eafb), bound
Nov 10, 2026, 08:00 EST. Builds ON mother's integration build
(mother/seed_toy.py) and Alpha's mesh core (alpha/mesh_core.py) — the
dispatch condition is met (concurrence holds, T4 bar fixed).

WHAT THIS STUB IS: the D2 mirage, at build level. The operator's Oct-22
1:2 rule (INN-142 comment d4333135) and the spec-v0.2 delta (D2): in a
forest, alternate trees — one is a full rendering node, the next an image
(a mirage, a placeholder for a rendering node) until the individual goes
toward it, at which point the mirage state ends. Node density is
construction-fixed (0.5 per visible pair). Images are visible-but-inert.
Promotion is lazy node-hood.

CHOICES, stated on the face so Reversed's audit can check them:
  1. An Image carries NO bubble_radius attribute (not a method returning
     0, no attribute at all) — matching Control's harness inertness check
     (`not hasattr(img, "bubble_radius")`). A bubble query can never
     return an image, because there is no bubble to query. Images are
     never added to the Mesh; they live in a separate list.
  2. An Image renders with the mature tree glyph "T" — it looks like the
     tree it placeholders. The mirage is a visual lie, not a missing tree.
  3. Promotion materializes the node the image depicted: a mature tree
     node (age set so stage == "mature", bubble 5.0), keeping the image's
     id (C6 persistent identity — one id across the mirage-to-node
     transition, and onward through the lifecycle). This matches
     Control's harness D2 reference model, which returns
     bubble_radius 5.0 for a promoted node. The lifecycle then runs
     from mature onward (mature -> decaying by the clock).
  4. The trigger is the avatar field: an image promotes when its position
     falls inside the avatar's bubble (distance < avatar bubble radius,
     3.0). The avatar's bubble IS the collision field (Sec.7 ruling, A7)
     — the same bubble that gates collision also gates promotion. One
     interaction region, two consequences. Promotion is checked after
     each avatar move (sweep), not per tick — the individual goes toward
     the image; the image does not come to the individual.
  5. After promotion the node is an ordinary mother's Node in the Mesh:
     it is returned by covering_set, raycast, and bubble_intersections,
     and avatar_try_move body-checks it ("until collision", the
     operator's words). The stub adds no second spatial structure (C3).

STUB DISCIPLINE (Shuffled's minimalism, dispatch answer 2): interface +
one test against Twin's expectations. Seed, don't sprout. What this stub
does NOT do: articulate (no articulation model — same UNMEASURABLE as
Alpha's mesh core); shared-field merge semantics (tier-2, deferred);
3D; Genesis world generation (positions are given, not scattered).

Python 3 stdlib only, deterministic. No RNG — positions are caller-given.
"""

import math
import os
import importlib.util

_MOTHER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "mother", "seed_toy.py")
_spec = importlib.util.spec_from_file_location("mother_seed_toy", _MOTHER_PATH)
mother = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mother)

_MATURE_AGE = 3 * mother.DEFAULT_TICKS_PER_STAGE  # stage idx 3 == "mature"


class Image:
    """A v0.2 mirage: visible, inert. No bubble, no mesh membership,
    no collision work. Deliberately no bubble_radius attribute."""

    __slots__ = ("id", "x", "y", "kind", "promoted")

    def __init__(self, iid, x, y):
        self.id = iid
        self.x = float(x)
        self.y = float(y)
        self.kind = "image"
        self.promoted = False

    def glyph(self):
        """What the sampler shows: the mature tree it placeholders."""
        return mother.TREE_GLYPH["mature"]

    def promote(self, world):
        """The individual went toward it: the mirage state ends.

        Materializes a mature tree Node with this image's id (C6) and
        adds it to the world's mesh. Returns the Node. The image is
        spent (promoted=True) and must not be promoted twice.
        """
        if self.promoted:
            raise ValueError(f"image {self.id} already promoted")
        self.promoted = True
        node = mother.Node(self.id, self.x, self.y, "tree", age=_MATURE_AGE)
        world.add(node)
        return node


def build_forest(world, positions, first_id=1):
    """Construction-fixed density (D2, operator's 1:2 rule).

    positions: a list of (x, y) — one visible tree per position.
    Alternates node, image, node, image... so exactly half the visible
    trees are nodes by design. Returns (nodes, images). Visible count
    is len(positions); node density is 0.5 by construction, never
    measured.
    """
    nodes, images = [], []
    for i, (x, y) in enumerate(positions):
        nid = first_id + i
        if i % 2 == 0:
            node = mother.Node(nid, x, y, "tree", age=_MATURE_AGE)
            world.add(node)
            nodes.append(node)
        else:
            images.append(Image(nid, x, y))
    return nodes, images


def visible_density(nodes, images):
    """Nodes over visible (nodes + images). 0.5 by construction."""
    total = len(nodes) + len(images)
    return len(nodes) / total if total else 0.0


def sweep(world, avatar, images):
    """Avatar-field promotion check, after an avatar move.

    For each unpromoted image whose position falls inside the avatar's
    bubble (distance < avatar bubble radius), promote it. Returns the
    list of Nodes materialized by this sweep. Images outside the bubble
    stay mirages — node-hood materializes only where the individual
    actually goes.
    """
    tps = world.mesh.ticks_per_stage
    reach = avatar.bubble_radius(tps)
    made = []
    for img in images:
        if img.promoted:
            continue
        if math.hypot(img.x - avatar.x, img.y - avatar.y) < reach:
            made.append(img.promote(world))
    return made
