# [ORG-MUSE | ALPHA | LC-6 MESH CORE STUB | 2026-10-26]

"""Mesh core — Alpha's LC-6 aspect stub (A7's home).

Builds FROM the operator's A7 ruling (Oct 22, 2026, 22:58 EDT), itemized
in INN-142 comment bbff4429:
  A7.1 The avatar IS a rendering node at its core.
  A7.2 Reason: it has to render the avatar itself.
  A7.3 Its rendering focus is INTERNAL: bones, muscles, ligaments.
  A7.4 Purpose of the internal rendering: fluid body movement.
  A7.5 Collision is the avatar's SECOND function.
  A7.6 Collision is rendered at the point of contact of field.

Builds ON mother's integration build (~/workspace/rendering-engine-seed/
mother/seed_toy.py) — the dispatch condition ("no move until mother's
integration build exists") is met: concurrence HOLDS, T4 bar fixed.

STUB DISCIPLINE (Shuffled's minimalism, dispatch answer 2):
interface + one test against Twin's expectations. Seed, don't sprout.
What this stub does: it makes A7.1–A7.6 assertable structure — the
avatar as a mesh member, internal render FIRST, collision SECOND and
only at field contact. What it does NOT do: articulate. No
articulation model exists in the 2D toy, so internal_render() names
the render order (bones, muscles, ligaments) without faking movement.
Control's harness marks internal rendering UNMEASURABLE, and that
mark STANDS — the toy cannot test what it does not model. A 3D
articulation model is out of toy scope, deferred, not silently solved.

Python 3 stdlib only, deterministic. No state beyond mother's Node.
"""

import importlib.util
import os

_MOTHER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "mother", "seed_toy.py")
_spec = importlib.util.spec_from_file_location("mother_seed_toy", _MOTHER_PATH)
mother = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mother)


class AvatarNode(mother.Node):
    """A rendering node of a specialized kind (A7.1).

    A mesh member like any Node (registration closes the gap Twin's
    build leaves as EXPECTED_FAIL in Control's harness — her A7
    reading predates the ruling, a known gap, not a defect), with
    one specialization: its rendering focus is inward.
    """

    __slots__ = ()

    # A7.3, in render order. A parts list, never a simulation.
    INTERNAL_PARTS = ("bones", "muscles", "ligaments")

    def __init__(self, nid, x, y, age=0):
        # An AvatarNode is an avatar node by construction; kind is
        # not a caller choice. (Mother's Node requires kind; this
        # subclass fixes it — the A7.1 specialization, in the type.)
        super().__init__(nid, x, y, "avatar", age)

    def internal_render(self):
        """First function (A7.3–A7.4): the internal render order.

        Returns the ordered parts. This is the stub: it names what
        renders, in what order, for fluid movement. It does not move
        them — articulation needs a model the 2D toy does not have.
        """
        return list(self.INTERNAL_PARTS)

    def render_tick(self, world, nx, ny):
        """One tick, in A7 order: internal FIRST, collision SECOND.

        Returns (order, moved), where order is a list of
        ("internal", parts) then ("collision", evaluations_delta).
        Collision runs only through world.avatar_try_move, which
        body-checks solely nodes whose bubbles intersect the avatar
        bubble at the candidate position — that is, only at field
        contact (A7.5–A7.6, and the Sec.7 ruling: the avatar's
        bubble IS its collision field).
        """
        order = [("internal", self.internal_render())]
        before = world.collision_evaluations
        moved = world.avatar_try_move(self, nx, ny)
        order.append(("collision", world.collision_evaluations - before))
        return order, moved
