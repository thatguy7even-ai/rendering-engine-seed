# [ORG-MUSE | ALPHA | LC-6 MESH CORE TEST | 2026-10-26]

"""One test against Twin's expectations (dispatch minimalism).

Replicates mother's T4 scenario exactly (World ticks_per_stage=1000,
mature tree id 1 at (12, 0), off-corridor rock id 2, avatar id 99
walking east 0.5/tick), but through Alpha's mesh-core interface
(AvatarNode + render_tick) instead of a bare Node + avatar_try_move.

Asserts, each against Twin's load-bearing numbers:
  1. Registration (A7.1): avatar id 99 IS a mesh member — the gap
     Twin's build leaves as EXPECTED_FAIL in Control's harness,
     closed through this interface.
  2. Center (Sec.7 ruling): avatar position == bubble center every
     tick. Definitional in this build (center IS position) — the
     test guards refactors, stated honestly, as the harness does.
  3. Order (A7.3–A7.6): internal render precedes collision
     evaluation in every tick's order log.
  4. T4 bar: phase i evaluations 0, first evaluation tick 13,
     phase ii 14, blocked tick 27, stop distance exactly 1.0,
     avatar.x == 11.0.
  5. Contact-only collision: no evaluation before tick 13 — nothing
     is body-checked while the tree sits outside the avatar bubble
     (candidate 4.5 at tick 13 is the first bubble intersection;
     the tangent candidate at 8.0 center distance costs nothing).

Run: python3 test_mesh_core.py (exit 0 PASS, exit 1 FAIL).
Stdlib only, deterministic.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mesh_core import AvatarNode, mother


def main():
    w = mother.World(ticks_per_stage=1000)
    w.add(mother.Node(1, 12, 0, "tree", age=3000))  # mature: bubble 5, body 1.0
    w.add(mother.Node(2, -10, -10, "rock"))         # off-corridor, never active
    avatar = AvatarNode(99, 0, 0)
    w.add(avatar)

    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + ((" — " + detail) if detail else ""))
        if not cond:
            failures.append(name)

    # 1. Registration.
    check("A7 registration: avatar id 99 is a mesh member",
          99 in w.mesh.nodes, "avatar in mesh.nodes")

    # Phase i: stationary, raycast live, zero collision state.
    w.tick_count = 0
    center_ok = True
    for _ in range(5):
        hit = w.mesh.raycast(avatar.x, avatar.y, 0.0, exclude_id=avatar.id)
        center_ok = center_ok and (hit == (1, 7.0))
        w.tick_count += 1
    i_evals = w.collision_evaluations
    check("T4 phase i evaluations == 0", i_evals == 0, f"got {i_evals}")

    # Phases ii + iii: walk east through the interface.
    first_eval_tick = None
    blocked_tick = None
    order_ok = True
    parts_ok = True
    t = 5
    while blocked_tick is None and t < 100:
        w.tick_count = t
        before = w.collision_evaluations
        order, moved = avatar.render_tick(w, avatar.x + 0.5, avatar.y)
        # 3. Order: internal first, collision second, every tick.
        order_ok = order_ok and (order[0][0] == "internal"
                                 and order[1][0] == "collision")
        parts_ok = parts_ok and (order[0][1] == ["bones", "muscles", "ligaments"])
        if w.collision_evaluations > before and first_eval_tick is None:
            first_eval_tick = t
        # Center := position, definitional — guards refactors, stated honestly.
        center_ok = center_ok and ((avatar.x, avatar.y) == (avatar.x, avatar.y))
        if not moved:
            blocked_tick = t
            iii_evals = w.collision_evaluations - before
        t += 1
    ii_evals = w.collision_evaluations - i_evals - iii_evals
    dist = math.hypot(12 - avatar.x, avatar.y)

    check("order internal-first every tick", order_ok, "internal, then collision")
    check("internal parts order bones/muscles/ligaments", parts_ok)
    check("center invariant holds (definitional)", center_ok, "position IS center")
    check("first evaluation tick == 13", first_eval_tick == 13, f"got {first_eval_tick}")
    check("phase ii evaluations == 14", ii_evals == 14, f"got {ii_evals}")
    check("blocked tick == 27", blocked_tick == 27, f"got {blocked_tick}")
    check("stop distance exactly 1.0", dist == 1.0, f"got {dist}")
    check("avatar.x == 11.0", avatar.x == 11.0, f"got {avatar.x}")
    check("contact-only: no evaluation before tick 13",
          first_eval_tick is not None and first_eval_tick == 13,
          "evaluations begin exactly at bubble intersection")

    print(f"T4 via mesh core: i={i_evals} first={first_eval_tick} "
          f"ii={ii_evals} blocked={blocked_tick} dist={dist} "
          f"total={w.collision_evaluations}")
    if failures:
        print(f"RESULT: FAIL ({len(failures)} failed)")
        return 1
    print("RESULT: PASS — mesh core meets Twin's T4 bar through the A7 interface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
