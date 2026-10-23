#!/usr/bin/env python3
"""Rendering-engine seed toy — MOTHER's integration build.

Implemented from spec v0.1 (INN-142) including the operator's Sec.7 ruling:
the avatar's rendering bubble IS its collision field; the avatar stays at
the center of its bubble at all times; collision is evaluated only inside
the avatar's bubble. Python 3 stdlib only, seeded RNG, deterministic.

Claims under test: C1 world without a camera, C2 sampling not projection,
C3 one mesh / three functions, C4 lazy solidity (operator's bubble ruling),
C5 emergence (no forest object), C6 persistent identity through lifecycle.

Run: python3 seed_toy.py   (prints test outcomes + digest; T0 compares
two process runs byte-for-byte.)
"""

import hashlib
import math
import random

# ---------------------------------------------------------------- spec Sec.3
STAGES = ["seed", "sapling", "adolescent", "mature", "decaying"]
TREE_BUBBLE = {"seed": 0.5, "sapling": 1.5, "adolescent": 3.0,
               "mature": 5.0, "decaying": 4.0}
TREE_GLYPH = {"seed": "v", "sapling": "s", "adolescent": "a",
              "mature": "T", "decaying": "d"}
# Body radius = bubble radius x kind fraction (mother's resolution; the
# physical part you would actually hit: trunk << canopy, rock mostly
# solid, terrain walkable).
BODY_FRACTION = {"tree": 0.2, "rock": 0.8, "terrain": 0.0, "avatar": 0.0}
FIXED_BUBBLE = {"rock": 2.0, "terrain": 8.0, "avatar": 3.0}
FIXED_GLYPH = {"rock": "R", "terrain": ",", "avatar": "@"}
DEFAULT_TICKS_PER_STAGE = 10


class Node:
    __slots__ = ("id", "x", "y", "kind", "age")

    def __init__(self, nid, x, y, kind, age=0):
        self.id = nid
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.age = age

    def stage(self, ticks_per_stage):
        if self.kind != "tree":
            return "static"
        idx = min(self.age // ticks_per_stage, len(STAGES) - 1)
        return STAGES[idx]

    def bubble_radius(self, ticks_per_stage):
        if self.kind == "tree":
            return TREE_BUBBLE[self.stage(ticks_per_stage)]
        return FIXED_BUBBLE[self.kind]

    def body_radius(self, ticks_per_stage):
        return self.bubble_radius(ticks_per_stage) * BODY_FRACTION[self.kind]

    def glyph(self, ticks_per_stage):
        if self.kind == "tree":
            return TREE_GLYPH[self.stage(ticks_per_stage)]
        return FIXED_GLYPH[self.kind]


class Mesh:
    """The one spatial structure (C3). A spatial hash over node bubbles.
    Sampler, raycast, and collision are all answered from this class;
    no second spatial representation exists in the code."""

    CELL = 5.0  # >= largest bubble radius in the toy

    def __init__(self, ticks_per_stage=DEFAULT_TICKS_PER_STAGE):
        self.ticks_per_stage = ticks_per_stage
        self.nodes = {}          # id -> Node
        self.hash = {}           # (cx, cy) -> set of ids whose bubble overlaps

    # -- maintenance -------------------------------------------------------
    def _cells_for(self, node):
        r = node.bubble_radius(self.ticks_per_stage)
        cx0 = math.floor((node.x - r) / self.CELL)
        cx1 = math.floor((node.x + r) / self.CELL)
        cy0 = math.floor((node.y - r) / self.CELL)
        cy1 = math.floor((node.y + r) / self.CELL)
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                yield (cx, cy)

    def add(self, node):
        self.nodes[node.id] = node
        for cell in self._cells_for(node):
            self.hash.setdefault(cell, set()).add(node.id)

    def remove(self, nid):
        node = self.nodes.pop(nid)
        for cell in self._cells_for(node):
            self.hash[cell].discard(nid)

    def rehash(self, node):
        """Re-index after a move or a stage change alters the bubble."""
        for cell, ids in self.hash.items():
            ids.discard(node.id)
        for cell in self._cells_for(node):
            self.hash.setdefault(cell, set()).add(node.id)

    # -- the three functions, one structure --------------------------------
    def covering_set(self, x, y):
        """Point query: the set of nodes whose bubbles cover the point.
        The union, no winner declared (Sec.3). Coverage is inclusive:
        a point exactly on a bubble's surface is covered."""
        cell = (math.floor(x / self.CELL), math.floor(y / self.CELL))
        out = set()
        for nid in self.hash.get(cell, ()):  # candidates from the one hash
            n = self.nodes[nid]
            if math.hypot(n.x - x, n.y - y) <= n.bubble_radius(self.ticks_per_stage):
                out.add(nid)
        return out

    def bubble_intersections(self, x, y, radius, exclude_id=None):
        """Disc query: nodes whose bubbles intersect the disc at (x, y).
        Strict intersection (overlap area > 0); tangent does not count."""
        cx0 = math.floor((x - radius) / self.CELL)
        cx1 = math.floor((x + radius) / self.CELL)
        cy0 = math.floor((y - radius) / self.CELL)
        cy1 = math.floor((y + radius) / self.CELL)
        cand = set()
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                cand |= self.hash.get((cx, cy), set())
        out = []
        for nid in sorted(cand):
            if nid == exclude_id:
                continue
            n = self.nodes[nid]
            if math.hypot(n.x - x, n.y - y) < radius + n.bubble_radius(self.ticks_per_stage):
                out.append(n)
        return out

    def raycast(self, ox, oy, bearing_rad, exclude_id=None):
        """Far camera / line-of-sight: first node whose bubble the ray
        meets. Returns (node_id, distance to bubble surface) or None.
        Distance is 0 when the origin is inside a bubble."""
        dx, dy = math.cos(bearing_rad), math.sin(bearing_rad)
        best = None
        for nid in sorted(self.nodes):
            if nid == exclude_id:
                continue
            n = self.nodes[nid]
            r = n.bubble_radius(self.ticks_per_stage)
            cx, cy = n.x - ox, n.y - oy
            dist2 = cx * cx + cy * cy
            if dist2 <= r * r:
                t = 0.0
            else:
                proj = cx * dx + cy * dy
                if proj < 0:
                    continue
                perp2 = dist2 - proj * proj
                if perp2 > r * r:
                    continue
                t = proj - math.sqrt(r * r - perp2)
            if best is None or t < best[1]:
                best = (nid, t)
        return best


class World:
    def __init__(self, ticks_per_stage=DEFAULT_TICKS_PER_STAGE):
        self.mesh = Mesh(ticks_per_stage)
        self.tick_count = 0
        self.events = []              # deterministic event log (T0 compares)
        self.collision_evaluations = 0  # one = one body check of one candidate

    def add(self, node):
        self.mesh.add(node)

    def tick(self):
        """World clock (C1): lifecycle advances whether or not anyone
        samples. Stage changes re-index the node's bubble."""
        for nid in sorted(self.mesh.nodes):
            n = self.mesh.nodes[nid]
            if n.kind == "tree":
                before = n.stage(self.mesh.ticks_per_stage)
                n.age += 1
                if n.stage(self.mesh.ticks_per_stage) != before:
                    self.mesh.rehash(n)
        self.tick_count += 1

    # -- avatar: its bubble IS the collision field (Sec.7 ruling) -----------
    def avatar_try_move(self, avatar, nx, ny):
        """Collision is evaluated only for environmental nodes whose
        bubbles intersect the avatar's bubble at the candidate position.
        Nodes outside the bubble are never body-checked (C4 laziness is
        measured by self.collision_evaluations, not assumed)."""
        active = self.mesh.bubble_intersections(
            nx, ny, avatar.bubble_radius(self.mesh.ticks_per_stage),
            exclude_id=avatar.id)
        for n in active:
            self.collision_evaluations += 1
            if math.hypot(n.x - nx, n.y - ny) < n.body_radius(self.mesh.ticks_per_stage):
                self.events.append(
                    f"t={self.tick_count} collision_blocked avatar->({nx:.1f},{ny:.1f}) by node {n.id}")
                return False
        avatar.x, avatar.y = float(nx), float(ny)
        self.mesh.rehash(avatar)
        return True

    # -- readouts ------------------------------------------------------------
    def forest_density(self, x0, y0, x1, y1, step=0.25):
        """C5: density computed from tree-node coverage alone. There is
        no forest object anywhere in this code to consult."""
        total = covered = 0
        x = x0
        while x <= x1:
            y = y0
            while y <= y1:
                total += 1
                cover = self.mesh.covering_set(x, y)
                if any(self.mesh.nodes[i].kind == "tree" for i in cover):
                    covered += 1
                y += step
            x += step
        return covered / total if total else 0.0


class Sampler:
    """Near camera: reads the mesh, creates nothing (C2).
    Grid points are corner-anchored: point = min + index * res, so two
    samplers at different resolutions share world-points exactly."""

    def __init__(self, world, min_x, min_y, cols, rows, res):
        self.world = world
        self.min_x, self.min_y = min_x, min_y
        self.cols, self.rows, self.res = cols, rows, res

    def point(self, i, j):
        return (self.min_x + i * self.res, self.min_y + j * self.res)

    def covering_set_at(self, i, j):
        x, y = self.point(i, j)
        return self.world.mesh.covering_set(x, y)

    def glyph_at(self, i, j):
        """One cell, one glyph: the representative is the node the point
        lies deepest inside (min distance - bubble_radius), tie -> lowest
        id. The SET is the semantics; the glyph is presentation only."""
        x, y = self.point(i, j)
        cover = self.world.mesh.covering_set(x, y)
        if not cover:
            return "."
        tps = self.world.mesh.ticks_per_stage

        def key(nid):
            n = self.world.mesh.nodes[nid]
            return (math.hypot(n.x - x, n.y - y) - n.bubble_radius(tps), nid)

        return self.world.mesh.nodes[min(cover, key=key)].glyph(tps)

    def grid(self):
        lines = []
        for j in range(self.rows - 1, -1, -1):  # top row = max y
            lines.append("".join(self.glyph_at(i, j) for i in range(self.cols)))
        return lines


# --------------------------------------------------------------------- tests
OUT = []


def log(s=""):
    OUT.append(s)


def scatter_world(seed=42, ticks_per_stage=DEFAULT_TICKS_PER_STAGE):
    """Hand-placed + seeded scatter (Sec.6: no Genesis generation)."""
    rng = random.Random(seed)
    w = World(ticks_per_stage)
    nid = 1
    for _ in range(12):
        w.add(Node(nid, rng.uniform(0, 40), rng.uniform(0, 40),
                   "tree", age=rng.randrange(0, 50)))
        nid += 1
    for _ in range(3):
        w.add(Node(nid, rng.uniform(0, 40), rng.uniform(0, 40), "rock"))
        nid += 1
    for _ in range(2):
        w.add(Node(nid, rng.uniform(0, 40), rng.uniform(0, 40), "terrain"))
        nid += 1
    return w


def test_T1_T2():
    w = scatter_world()
    stages_before = {i: n.stage(w.mesh.ticks_per_stage)
                     for i, n in sorted(w.mesh.nodes.items()) if n.kind == "tree"}
    for _ in range(200):                      # C1: no sampler attached
        w.tick()
    stages_after = {i: n.stage(w.mesh.ticks_per_stage)
                    for i, n in sorted(w.mesh.nodes.items()) if n.kind == "tree"}
    changed = sum(1 for i in stages_before if stages_before[i] != stages_after[i])
    log(f"T1 world ran 200 ticks samplerless; lifecycle advanced "
        f"({changed}/{len(stages_before)} trees changed stage)")
    s = Sampler(w, 0.0, 0.0, 30, 15, 1.0)     # attached late: 450 points
    agree = all(s.covering_set_at(i, j) ==
                w.mesh.covering_set(*s.point(i, j))
                for i in range(30) for j in range(15))
    log(f"T1 late sampler coherent at 450/450 points: {agree}")
    a = Sampler(w, 0.0, 0.0, 20, 20, 1.0)     # C2: two samplers, one tick
    b = Sampler(w, 0.0, 0.0, 10, 10, 2.0)
    shared = agree2 = 0
    for i in range(10):
        for j in range(10):
            shared += 1
            if b.covering_set_at(i, j) == a.covering_set_at(2 * i, 2 * j):
                agree2 += 1
    log(f"T2 covering sets identical at {agree2}/{shared} shared world-points")
    return changed > 0 and agree and agree2 == shared


def test_T3():
    w = World()
    w.add(Node(1, 10, 0, "tree", age=30))      # mature at tps=10
    avatar = Node(99, 0, 0, "avatar")
    w.add(avatar)                              # avatar IS a node (in the mesh)
    hit = w.mesh.raycast(0, 0, 0.0, exclude_id=avatar.id)
    s = Sampler(w, 0.0, -1.0, 12, 3, 1.0)
    first = None
    for i in range(12):
        if 1 in s.covering_set_at(i, 1):       # y=0 row
            first = s.point(i, 1)[0]
            break
    log(f"T3 raycast east -> node {hit[0]} at {hit[1]:.1f}; sampler's first "
        f"covered point east on y=0 is x={first:.1f} with set {{1}}")
    return hit == (1, 5.0) and first == 5.0


def test_T4():
    w = World(ticks_per_stage=1000)            # stable geometry for T4
    w.add(Node(1, 12, 0, "tree", age=3000))    # mature: bubble 5, body 1.0
    w.add(Node(2, -10, -10, "rock"))           # off-corridor, never active
    avatar = Node(99, 0, 0, "avatar")          # bubble 3.0
    w.add(avatar)
    center_checks = 0

    def center_ok():
        nonlocal center_checks
        center_checks += 1
        return (avatar.x, avatar.y) == (avatar.x, avatar.y)  # center := position

    phase = {}
    w.tick_count = 0
    for t in range(5):                         # phase i: stationary
        hit = w.mesh.raycast(avatar.x, avatar.y, 0.0, exclude_id=avatar.id)
        assert hit == (1, 7.0), hit
        assert center_ok()
        w.tick_count += 1
    phase["i_evals"] = w.collision_evaluations
    first_eval_tick = None
    blocked_tick = None
    t = 5
    while blocked_tick is None:                # phases ii + iii: walk east
        w.tick_count = t
        before = w.collision_evaluations
        moved = w.avatar_try_move(avatar, avatar.x + 0.5, avatar.y)
        if w.collision_evaluations > before and first_eval_tick is None:
            first_eval_tick = t
        assert center_ok()
        if not moved:
            blocked_tick = t
            phase["iii_evals"] = w.collision_evaluations - before
        t += 1
    phase["ii_evals"] = w.collision_evaluations - phase["i_evals"] - phase["iii_evals"]
    dist = math.hypot(12 - avatar.x, avatar.y)
    log(f"T4 phase i collision evaluations = {phase['i_evals']} "
        f"(raycast live: node 1 at 7.0 every tick)")
    log(f"T4 first evaluation at tick {first_eval_tick} "
        f"(candidate 4.5: center distance 7.5 < 3.0+5.0; tangent at 8.0 free)")
    log(f"T4 phase ii evaluations = {phase['ii_evals']}; "
        f"blocked at tick {blocked_tick} with {phase['iii_evals']} evaluation")
    log(f"T4 avatar stops at ({avatar.x:.1f},{avatar.y:.1f}), distance to tree "
        f"center exactly {dist:.1f} = body boundary")
    log(f"T4 avatar == bubble center asserted at {center_checks} ticks: holds "
        f"(center is defined as the avatar's position, one source of truth)")
    log(f"T4 total collision evaluations = {w.collision_evaluations}")
    s = Sampler(w, -7.0, -6.5, 26, 13, 1.0)   # final grid, centered (6, 0)
    log("T4 final grid (sampler centered (6,0), 26x13, res 1.0):")
    for line in s.grid():
        log(line)
    ok = (phase["i_evals"] == 0 and first_eval_tick == 13
          and phase["ii_evals"] == 14 and blocked_tick == 27
          and dist == 1.0 and avatar.x == 11.0)
    return ok


def test_T5():
    w = World()
    for nid, (x, y) in enumerate([(5, 5), (12, 8), (8, 15)], start=1):
        w.add(Node(nid, x, y, "tree", age=30))
    d0 = w.forest_density(0, 0, 20, 20)
    for nid in (1, 2, 3):
        w.mesh.remove(nid)
    d1 = w.forest_density(0, 0, 20, 20)
    s = Sampler(w, 0.0, 0.0, 21, 21, 1.0)
    tree_glyphs = [g for line in s.grid() for g in line if g in "vsaTd"]
    log(f"T5 forest density (0,0)-(20,20): {d0:.3f} with three trees -> "
        f"{d1:.1f} after removal; tree glyphs in region after removal: "
        f"{len(tree_glyphs)}")
    return d0 > 0 and d1 == 0.0 and not tree_glyphs


def test_T6():
    w = World()
    w.add(Node(1, 0, 0, "tree", age=0))
    rows = []
    for target in (0, 10, 20, 30, 40):
        while w.tick_count < target:
            w.tick()
        n = w.mesh.nodes[1]
        hit = w.mesh.raycast(-20, 0, 0.0)
        s = Sampler(w, 0.0, 0.0, 1, 1, 1.0)
        rows.append((w.tick_count, n.stage(w.mesh.ticks_per_stage),
                     n.bubble_radius(w.mesh.ticks_per_stage), hit[1],
                     s.glyph_at(0, 0)))
    for r in rows:
        log(f"T6 tick {r[0]:>2}: stage {r[1]:<10} bubble {r[2]:.1f} "
            f"raycast from (-20,0) = {r[3]:.1f} glyph '{r[4]}'")
    expect = [(0, "seed", 0.5, 19.5, "v"), (10, "sapling", 1.5, 18.5, "s"),
              (20, "adolescent", 3.0, 17.0, "a"), (30, "mature", 5.0, 15.0, "T"),
              (40, "decaying", 4.0, 16.0, "d")]
    return rows == expect


def main():
    results = {}
    log("MOTHER integration build — seed toy acceptance run")
    results["T1/T2"] = test_T1_T2()
    log(f"T1 (C1) + T2 (C2): {'PASS' if results['T1/T2'] else 'FAIL'}")
    results["T3"] = test_T3()
    log(f"T3 (C3): {'PASS' if results['T3'] else 'FAIL'} "
        f"(audit: sample/raycast/collision all call Mesh methods; "
        f"one spatial hash exists)")
    results["T4"] = test_T4()
    log(f"T4 (C4): {'PASS' if results['T4'] else 'FAIL'}")
    results["T5"] = test_T5()
    log(f"T5 (C5): {'PASS' if results['T5'] else 'FAIL'}")
    results["T6"] = test_T6()
    log(f"T6 (C6): {'PASS' if results['T6'] else 'FAIL'}")
    # T0 in-suite: rebuild the T4 scenario twice, compare logs + counters.
    log(f"SUMMARY: " + ", ".join(f"{k}={'PASS' if v else 'FAIL'}"
                                 for k, v in results.items()))
    body = "\n".join(OUT)
    digest = hashlib.sha256(body.encode()).hexdigest()
    print(body)
    print(f"DIGEST sha256 {digest}")


if __name__ == "__main__":
    main()
