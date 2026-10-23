#!/usr/bin/env python3
"""Rendering-engine seed toy — Twin's independent implementation.

Built from mother's spec v0.1 alone (toy concurrence, Oct 14 rule).
Core inversion under test: the world renders itself, cameras sample it,
solidity is an interaction, not a property.

Design points (spec section refs):
- One spatial structure (Mesh, spatial hash over node bubbles) serves near
  sampling (C2/C3), far raycast (C3), and collision (C3/C4). No second
  spatial structure exists in this file (T3 audit point).
- Mesh point query returns the covering SET of nodes — the union, no
  winner declared (sec.3 Mesh).
- Avatar's rendering bubble IS its collision field (operator ruling, sec.7);
  avatar is at the bubble center at all times; collision is evaluated only
  for environmental nodes whose bubbles intersect the avatar's bubble (C4).
- World evolves on its own clock with no sampler attached (C1); nodes keep
  one identity across lifecycle stages (C6); there is no global forest
  object — density is computed from node coverage alone (C5).
- Deterministic: seeded RNG only; no wall clock, no set-iteration order
  dependence (candidates always sorted by id before use).

Ambiguity resolutions are logged in RESULTS.md (A1–A11); the choices made
here are the ones flagged there.
"""

import hashlib
import math
import random

# ---------------------------------------------------------------- nodes

# Spec sec.3 stage table (tree lifecycle).
STAGE_TABLE = [
    ("seed", 0.5),
    ("sapling", 1.5),
    ("adolescent", 3.0),
    ("mature", 5.0),
    ("decaying", 4.0),
]
STAGE_RADIUS = dict(STAGE_TABLE)

# A2: spec gives no body radii. body_radius = bubble_radius * kind fraction.
BODY_FRACTION = {"tree": 0.2, "rock": 0.8, "terrain": 0.0}

# A3: spec gives no avatar bubble radius. Fixed at 3.0.
AVATAR_BUBBLE_RADIUS = 3.0

TREE_GLYPHS = {
    "seed": "v",
    "sapling": "s",
    "adolescent": "a",
    "mature": "T",
    "decaying": "d",
}
KIND_GLYPHS = {"rock": "R", "terrain": ","}
EMPTY_GLYPH = "."


class Node:
    __slots__ = ("id", "x", "y", "kind", "age", "stage_index",
                 "bubble_radius", "body_radius")

    def __init__(self, node_id, x, y, kind, bubble_radius, age=0):
        self.id = node_id
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.age = age
        self.bubble_radius = float(bubble_radius)
        self.body_radius = self.bubble_radius * BODY_FRACTION[kind]
        # A8: only trees run the lifecycle.
        self.stage_index = 0
        if kind == "tree":
            self.sync_stage(ticks_per_stage=10**9)  # placeholder; world sets

    @property
    def stage(self):
        if self.kind == "tree":
            return STAGE_TABLE[self.stage_index][0]
        return "static"

    def sync_stage(self, ticks_per_stage):
        """Recompute stage + radii from age (trees only). Returns True if
        the stage (and therefore the bubble) changed."""
        if self.kind != "tree":
            return False
        idx = min(self.age // ticks_per_stage, len(STAGE_TABLE) - 1)
        if idx == self.stage_index and self.age != 0:
            return False
        changed = idx != self.stage_index
        self.stage_index = idx
        self.bubble_radius = STAGE_TABLE[idx][1]
        self.body_radius = self.bubble_radius * BODY_FRACTION["tree"]
        return changed

    def glyph(self):
        if self.kind == "tree":
            return TREE_GLYPHS[self.stage]
        return KIND_GLYPHS[self.kind]


def make_tree(node_id, x, y, age=0, ticks_per_stage=10):
    n = Node(node_id, x, y, "tree", STAGE_TABLE[0][1], age=age)
    n.sync_stage(ticks_per_stage)
    return n


def make_rock(node_id, x, y):
    return Node(node_id, x, y, "rock", 1.25)


def make_terrain(node_id, x, y):
    return Node(node_id, x, y, "terrain", 2.0)


# ---------------------------------------------------------------- mesh
# THE one spatial structure. Sampler, raycast, and collision all query it
# through the three methods below (T3 audit point).

class Mesh:
    def __init__(self, cell_size=10.0):
        self.cell_size = float(cell_size)
        self.nodes = {}          # id -> Node
        self._hash = {}          # (cx, cy) -> set of ids
        self.max_bubble_radius = 0.0

    # -- index maintenance ------------------------------------------------
    def _cells_for(self, x, y, r):
        cs = self.cell_size
        cx0 = math.floor((x - r) / cs)
        cx1 = math.floor((x + r) / cs)
        cy0 = math.floor((y - r) / cs)
        cy1 = math.floor((y + r) / cs)
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                yield (cx, cy)

    def add(self, node):
        self.nodes[node.id] = node
        for cell in self._cells_for(node.x, node.y, node.bubble_radius):
            self._hash.setdefault(cell, set()).add(node.id)
        self._refresh_max()

    def remove(self, node):
        for cell in self._cells_for(node.x, node.y, node.bubble_radius):
            bucket = self._hash.get(cell)
            if bucket is not None:
                bucket.discard(node.id)
                if not bucket:
                    del self._hash[cell]
        del self.nodes[node.id]
        self._refresh_max()

    def reindex(self, node):
        """Call after a node's bubble radius changed (stage transition)."""
        self.remove(node)
        self.add(node)

    def _refresh_max(self):
        self.max_bubble_radius = max(
            (n.bubble_radius for n in self.nodes.values()), default=0.0)

    def _candidates(self, x, y, reach):
        """Broadphase: ids in cells overlapped by the square of half-side
        `reach` around (x, y). Exact tests happen in the query methods."""
        ids = set()
        for cell in self._cells_for(x, y, reach):
            ids.update(self._hash.get(cell, ()))
        return ids

    # -- the three query functions (C3) ------------------------------------
    def nodes_covering_point(self, x, y):
        """Point query: the set of nodes whose bubbles cover the point.
        Union, no winner declared (sec.3)."""
        out = []
        for nid in self._candidates(x, y, self.max_bubble_radius):
            n = self.nodes[nid]
            if math.hypot(n.x - x, n.y - y) <= n.bubble_radius:
                out.append(n)
        out.sort(key=lambda n: n.id)
        return out

    def nodes_intersecting_bubble(self, x, y, r):
        """Bubble query: nodes whose bubbles intersect the query bubble
        (strict <: tangent does not count, A4). Used by collision (C4)."""
        out = []
        reach = r + self.max_bubble_radius
        for nid in self._candidates(x, y, reach):
            n = self.nodes[nid]
            if math.hypot(n.x - x, n.y - y) < r + n.bubble_radius:
                out.append(n)
        out.sort(key=lambda n: n.id)
        return out

    def raycast(self, ox, oy, bearing_deg):
        """Far raycast: first node whose bubble the ray intersects.
        Returns (node, distance-to-bubble-surface) or None (A6).
        Iterates the mesh's own node registry — no second structure."""
        dx = math.cos(math.radians(bearing_deg))
        dy = math.sin(math.radians(bearing_deg))
        best = None
        best_t = None
        for n in sorted(self.nodes.values(), key=lambda m: m.id):
            cx, cy = n.x - ox, n.y - oy
            t_ca = cx * dx + cy * dy
            d2 = cx * cx + cy * cy - t_ca * t_ca
            r2 = n.bubble_radius * n.bubble_radius
            if d2 > r2:
                continue
            t = t_ca - math.sqrt(max(r2 - d2, 0.0))
            if t < 0.0:
                if t_ca < 0.0 and math.hypot(cx, cy) > n.bubble_radius:
                    continue  # bubble entirely behind the ray origin
                t = 0.0  # origin inside the bubble
            if best_t is None or t < best_t:
                best, best_t = n, t
        if best is None:
            return None
        return best, best_t


# ---------------------------------------------------------------- world

class World:
    def __init__(self, ticks_per_stage=10):
        self.mesh = Mesh()
        self.ticks_per_stage = ticks_per_stage
        self.tick_count = 0
        self.events = []            # (tick, kind, detail)
        self.collision_evaluations = 0

    def add(self, node):
        if node.kind == "tree":
            node.sync_stage(self.ticks_per_stage)
        self.mesh.add(node)

    def remove(self, node):
        self.mesh.remove(node)

    def advance_clock(self):
        """C1: the world evolves on its own clock, sampler or not.
        C6: stage transitions update bubble + glyph under one identity."""
        self.tick_count += 1
        for node in sorted(self.mesh.nodes.values(), key=lambda n: n.id):
            if node.kind != "tree":
                continue
            node.age += 1
            if node.sync_stage(self.ticks_per_stage):
                self.mesh.reindex(node)
                self.events.append(
                    (self.tick_count, "stage", (node.id, node.stage)))


# ---------------------------------------------------------------- avatar

class Avatar:
    """A node (not a mesh member, A7) whose rendering bubble IS its
    collision field (sec.7 ruling). Position == bubble center, always:
    the center is defined as the avatar's position (single source)."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.bubble_radius = AVATAR_BUBBLE_RADIUS

    @property
    def bubble_center(self):
        return (self.x, self.y)


def avatar_attempt_move(world, avatar, dx, dy):
    """One tick of the avatar script. The Mesh bubble query runs at the
    candidate position BEFORE the move resolves (A4). Only nodes the
    query returns are collision-active; each returned node costs one
    collision evaluation for its body check (A10). A3: the avatar is a
    point for the body test — blocked iff the candidate position would
    enter an active node's body radius. No clamping (A11).
    Returns (moved: bool, evaluations_this_tick: int)."""
    cand_x, cand_y = avatar.x + dx, avatar.y + dy
    active = world.mesh.nodes_intersecting_bubble(
        cand_x, cand_y, avatar.bubble_radius)
    evals = 0
    blocked_by = None
    for node in active:
        evals += 1
        if math.hypot(node.x - cand_x, node.y - cand_y) < node.body_radius:
            blocked_by = node
            break
    world.collision_evaluations += evals
    if blocked_by is not None:
        world.events.append(
            (world.tick_count, "collision_blocked", (blocked_by.id,)))
        return False, evals
    avatar.x, avatar.y = cand_x, cand_y
    return True, evals


# ---------------------------------------------------------------- sampler

def glyph_for_covering(covering):
    """A5: the query returns a set (no winner). For the rendered cell,
    pick the covering node minimizing distance/bubble_radius, tie-break
    lowest id. Sets — not glyphs — are the concurrence surface."""
    if not covering:
        return EMPTY_GLYPH
    return covering[0].glyph()


def sample_points(mesh, cx, cy, width, height, res):
    """A9: corner-anchored grid points (point = min + index * res), so
    cross-resolution agreement (T2) is well-defined.
    Returns {(x, y): (glyph, frozenset(ids), covering_list_sorted)} where
    covering_list is sorted by (dist/bubble_radius, id) for glyph choice
    but the SET is the data."""
    cols = int(round(width / res))
    rows = int(round(height / res))
    x0 = cx - width / 2.0
    y0 = cy - height / 2.0
    out = {}
    for r in range(rows):
        y = y0 + r * res
        for c in range(cols):
            x = x0 + c * res
            covering = mesh.nodes_covering_point(x, y)
            ranked = sorted(
                covering,
                key=lambda n: (math.hypot(n.x - x, n.y - y)
                               / n.bubble_radius, n.id))
            glyph = ranked[0].glyph() if ranked else EMPTY_GLYPH
            out[(x, y)] = (glyph, frozenset(n.id for n in covering))
    return out


def render_grid(mesh, cx, cy, width, height, res):
    """ASCII grid, north (max y) on the top row."""
    samples = sample_points(mesh, cx, cy, width, height, res)
    cols = int(round(width / res))
    rows_n = int(round(height / res))
    x0 = cx - width / 2.0
    y0 = cy - height / 2.0
    lines = []
    for r in range(rows_n - 1, -1, -1):
        y = y0 + r * res
        line = "".join(samples[(x0 + c * res, y)][0] for c in range(cols))
        lines.append(line)
    return "\n".join(lines)


def forest_density(mesh, x_min, y_min, x_max, y_max, res=0.5):
    """C5: computed from tree-bubble coverage alone. No forest object."""
    covered = 0
    total = 0
    y = y_min
    while y <= y_max + 1e-9:
        x = x_min
        while x <= x_max + 1e-9:
            total += 1
            if any(n.kind == "tree"
                   for n in mesh.nodes_covering_point(x, y)):
                covered += 1
            x += res
        y += res
    return covered / total if total else 0.0


# ---------------------------------------------------------------- worlds

def scatter_world(seed, ticks_per_stage=10):
    """Seeded scatter (sec.6: hand-placed plus seeded scatter)."""
    rng = random.Random(seed)
    world = World(ticks_per_stage=ticks_per_stage)
    nid = 1
    for _ in range(15):
        world.add(make_tree(nid, rng.uniform(-25, 25), rng.uniform(-25, 25),
                            age=rng.randrange(0, 50),
                            ticks_per_stage=ticks_per_stage))
        nid += 1
    for _ in range(5):
        world.add(make_rock(nid, rng.uniform(-25, 25), rng.uniform(-25, 25)))
        nid += 1
    for _ in range(4):
        world.add(make_terrain(nid, rng.uniform(-25, 25),
                               rng.uniform(-25, 25)))
        nid += 1
    return world


# ---------------------------------------------------------------- tests

RESULTS = []


def record(name, passed, detail):
    RESULTS.append((name, passed, detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")


def test_T0():
    hashes = []
    for _ in range(2):
        world = scatter_world(seed=42)
        avatar = Avatar(0, 0)
        script = [(0.5, 0.0)] * 10 + [(0.0, 0.5)] * 10 + [(-0.5, 0.0)] * 10
        for (dx, dy) in script:
            avatar_attempt_move(world, avatar, dx, dy)
            world.advance_clock()
        grid = render_grid(world.mesh, 0, 0, 30, 15, 1.0)
        log = repr(world.events)
        hashes.append(hashlib.sha256(
            (grid + "|" + log).encode()).hexdigest())
    ok = hashes[0] == hashes[1]
    record("T0 determinism", ok, f"two runs, grid+log sha256 {hashes[0][:16]}… "
                                 f"identical={ok}")
    return ok


def test_T1():
    world = scatter_world(seed=7)
    before = {n.id: n.stage for n in world.mesh.nodes.values()}
    for _ in range(200):
        world.advance_clock()  # no sampler attached (C1)
    after = {n.id: n.stage for n in world.mesh.nodes.values()}
    changed = before != after
    # Attach a sampler late; it must read a coherent world: every glyph
    # agrees with a direct mesh query at the same point.
    samples = sample_points(world.mesh, 0, 0, 30, 15, 1.0)
    coherent = True
    for (x, y), (glyph, ids) in samples.items():
        direct = frozenset(
            n.id for n in world.mesh.nodes_covering_point(x, y))
        if direct != ids:
            coherent = False
            break
        if (glyph == EMPTY_GLYPH) != (len(ids) == 0):
            coherent = False
            break
    ok = (world.tick_count == 200) and changed and coherent
    record("T1 world without camera (C1)", ok,
           f"200 ticks samplerless; stage map changed={changed}; "
           f"late sampler coherent at all {len(samples)} points={coherent}")
    return ok


def test_T2():
    world = scatter_world(seed=11)
    a = sample_points(world.mesh, 0, 0, 20, 20, 1.0)
    b = sample_points(world.mesh, 0, 0, 10, 10, 2.0)
    shared = set(a) & set(b)
    agree = all(a[p][1] == b[p][1] for p in shared) and len(shared) > 0
    record("T2 sampling not projection (C2)", agree,
           f"{len(shared)} shared world-points, covering sets identical "
           f"at all of them={agree}")
    return agree


def test_T3():
    world = World()
    world.add(make_tree(1, 10, 0, age=35))     # mature, bubble 5
    world.add(make_rock(2, 0, 10))             # off-axis
    avatar = Avatar(0, 0)
    hit = world.mesh.raycast(avatar.x, avatar.y, 0)
    samples = sample_points(world.mesh, 0, 0, 24, 12, 1.0)
    east = sorted(p for p in samples if p[1] == 0.0 and p[0] > avatar.x)
    first_covered = next(
        (p for p in east if samples[p][1]), None)
    ok = (hit is not None and hit[0].id == 1
          and first_covered is not None
          and samples[first_covered][1] == frozenset({1})
          and abs(hit[1] - 5.0) < 1e-9
          and abs(first_covered[0] - 5.0) < 1e-9)
    record("T3 one mesh three functions (C3)", ok,
           f"raycast east -> node {hit[0].id if hit else None} at "
           f"{hit[1] if hit else None}; first covered sampler point east "
           f"on y=0 is {first_covered} with set "
           f"{samples[first_covered][1] if first_covered else None}; "
           f"collision uses the same Mesh (see T4)")
    return ok


def test_T4():
    # ticks_per_stage=1000 keeps the tree mature for the whole scenario
    # (lifecycle timing is T1/T6's subject; T4's geometry must be stable).
    world = World(ticks_per_stage=1000)
    tree = make_tree(1, 12, 0, age=3500, ticks_per_stage=1000)
    # mature: bubble 5, body 1.0
    world.add(tree)
    world.add(make_rock(2, -10, -10))          # distant, off-corridor
    avatar = Avatar(0, 0)
    per_tick = []  # (tick, pos_after, evals, moved, center_ok)

    def step(dx, dy):
        moved, evals = avatar_attempt_move(world, avatar, dx, dy)
        center_ok = avatar.bubble_center == (avatar.x, avatar.y)
        per_tick.append((world.tick_count, (avatar.x, avatar.y),
                         evals, moved, center_ok))
        world.advance_clock()

    # Phase i: stationary at raycast range, 5 ticks.
    for _ in range(5):
        step(0.0, 0.0)
    hit_i = world.mesh.raycast(avatar.x, avatar.y, 0)
    phase_i_evals = sum(t[2] for t in per_tick)

    # Phases ii+iii: walk east at 0.5/tick until blocked (max 60 ticks).
    walk_start = len(per_tick)
    blocked_tick = None
    for _ in range(60):
        step(0.5, 0.0)
        if not per_tick[-1][3]:
            blocked_tick = per_tick[-1][0]
            break
    walk = per_tick[walk_start:]
    first_eval_tick = next((t[0] for t in walk if t[2] > 0), None)
    # Phase ii = walking ticks through the last successful move;
    # the blocked tick is phase iii (A10).
    phase_ii_evals = sum(t[2] for t in walk if t[3])
    phase_iii_evals = sum(t[2] for t in walk if not t[3])
    final_dist = math.hypot(tree.x - avatar.x, tree.y - avatar.y)
    centers_ok = all(t[4] for t in per_tick)
    blocked_events = [e for e in world.events if e[1] == "collision_blocked"]

    ok = (phase_i_evals == 0
          and hit_i is not None and hit_i[0].id == 1
          and first_eval_tick == 13
          and blocked_tick is not None
          and len(blocked_events) == 1
          and abs(final_dist - tree.body_radius) < 1e-9
          and centers_ok)
    grid = render_grid(world.mesh, 6, 0, 26, 13, 1.0)
    record("T4 lazy solidity (C4)", ok,
           f"phase i evals={phase_i_evals} (raycast hit node "
           f"{hit_i[0].id if hit_i else None} at {hit_i[1] if hit_i else None}); "
           f"first evaluation tick={first_eval_tick}; phase ii evals="
           f"{phase_ii_evals}; phase iii (blocked tick) evals="
           f"{phase_iii_evals}; blocked tick={blocked_tick}; avatar final "
           f"pos=({avatar.x}, {avatar.y}), distance to tree center="
           f"{final_dist} == body radius {tree.body_radius}; "
           f"center==position every tick={centers_ok}")
    print("--- T4 final sampler grid (center (6,0), 26x13, res 1.0) ---")
    print(grid)
    print(f"--- avatar final position ({avatar.x}, {avatar.y}); "
          f"tree node 1 at (12, 0) ---")
    print(f"T4_COUNTS phase_i={phase_i_evals} phase_ii={phase_ii_evals} "
          f"phase_iii={phase_iii_evals} first_eval_tick={first_eval_tick} "
          f"total={world.collision_evaluations}")
    return ok


def test_T5():
    world = World()
    trees = [make_tree(1, 5, 5, age=35), make_tree(2, 12, 8, age=22),
             make_tree(3, 16, 16, age=12)]
    for t in trees:
        world.add(t)
    d_before = forest_density(world.mesh, 0, 0, 20, 20)
    for t in trees:
        world.remove(t)
    d_after = forest_density(world.mesh, 0, 0, 20, 20)
    samples = sample_points(world.mesh, 10, 10, 20, 20, 1.0)
    tree_glyphs = set(TREE_GLYPHS.values())
    no_forest = all(g not in tree_glyphs for (g, _) in samples.values())
    ok = d_before > 0.0 and d_after == 0.0 and no_forest
    record("T5 emergence, no forest object (C5)", ok,
           f"density before={d_before:.3f}; after removing all tree "
           f"nodes density={d_after} and no tree glyphs in sampler="
           f"{no_forest}")
    return ok


def test_T6():
    world = World(ticks_per_stage=10)
    tree = make_tree(1, 0, 0, age=0)
    world.add(tree)
    expected = [
        (0, "seed", 0.5, 19.5),
        (10, "sapling", 1.5, 18.5),
        (20, "adolescent", 3.0, 17.0),
        (30, "mature", 5.0, 15.0),
        (40, "decaying", 4.0, 16.0),
    ]
    seen = []
    ok = True
    for (tick_at, stage, radius, ray_dist) in expected:
        while world.tick_count < tick_at:
            world.advance_clock()
        hit = world.mesh.raycast(-20, 0, 0)
        covering = world.mesh.nodes_covering_point(0, 0)
        glyph = covering[0].glyph() if covering else EMPTY_GLYPH
        row_ok = (tree.id == 1 and tree.stage == stage
                  and abs(tree.bubble_radius - radius) < 1e-9
                  and hit is not None and hit[0].id == 1
                  and abs(hit[1] - ray_dist) < 1e-9
                  and glyph == TREE_GLYPHS[stage])
        seen.append((tick_at, tree.stage, tree.bubble_radius,
                     hit[1] if hit else None, glyph))
        ok = ok and row_ok
    record("T6 persistent identity through lifecycle (C6)", ok,
           f"one id throughout; (tick, stage, radius, raydist, glyph) = "
           f"{seen}")
    return ok


def main():
    print("Rendering-engine seed toy — Twin implementation, spec v0.1")
    oks = [test_T0(), test_T1(), test_T2(), test_T3(),
           test_T4(), test_T5(), test_T6()]
    print(f"SUMMARY {sum(oks)}/7 passed")
    return 0 if all(oks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
