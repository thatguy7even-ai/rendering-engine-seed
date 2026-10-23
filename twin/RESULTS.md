[ORG-MUSE | TWIN | 2026-10-21]

# RESULTS — Rendering-engine seed toy, Twin's independent implementation

Toy concurrence under the Oct-14 rule: implemented from mother's spec v0.1
alone, no consultation with other seats, built to the operator's §7 ruling
(avatar's rendering bubble IS the collision field; avatar at bubble center
at all times; revised C4/T4). Python 3.12, stdlib only, seeded RNG.

Code: `seed_toy.py` (this directory). Run: `python3 seed_toy.py`.
Process-level determinism verified: two full runs byte-identical.

## Acceptance tests — 7/7 PASS

- **T0 (determinism) — PASS.** Two runs, same seed (42) + same avatar
  script: identical final grid + event log (sha256 `1d0ff86d88c35948…`).
- **T1 (C1, world without a camera) — PASS.** 200 ticks with no sampler
  attached; lifecycle stage map changed over the run; a sampler attached at
  tick 200 reads a coherent world — glyph and covering set agree with a
  direct mesh query at all 450 sample points, zero initialization artifacts.
- **T2 (C2, sampling not projection) — PASS.** Two samplers (20×20 @ res 1.0;
  10×10 @ res 2.0), same tick: covering node sets identical at all 25
  shared world-points.
- **T3 (C3, one mesh, three functions) — PASS.** Raycast east from the
  avatar's position returns node 1 (mature tree at (10, 0)) at distance 5.0;
  the near sampler's first covered point east on y=0 is (5.0, 0.0) with
  covering set {1} — same node, same structure. Code audit point: sampler,
  raycast, and collision call the three query methods of the one `Mesh`
  class in `seed_toy.py`; no second spatial structure exists in the code.
- **T4 (C4, lazy solidity) — PASS.** Details below.
- **T5 (C5, emergence) — PASS.** Forest density of region (0,0)–(20,20)
  with three trees: 0.271, computed from node coverage alone. After
  removing all tree nodes: density 0.0, and the sampler shows no tree
  glyphs in the region. No forest object exists in the code to update.
- **T6 (C6, persistent identity) — PASS.** One seed planted at tick 0, one
  id throughout; (tick, stage, bubble radius, raycast distance from
  (−20, 0), glyph):
  (0, seed, 0.5, 19.5, 'v') · (10, sapling, 1.5, 18.5, 's') ·
  (20, adolescent, 3.0, 17.0, 'a') · (30, mature, 5.0, 15.0, 'T') ·
  (40, decaying, 4.0, 16.0, 'd'). Stage sequence in order, radii match the
  §3 stage table at every stage, glyph and raycast track the stage.

## T4 scenario (as built)

Avatar at (0, 0), bubble radius 3.0 (A3). One mature tree, node 1 at
(12, 0): bubble radius 5.0, body radius 1.0 (A2). One rock far off-corridor
at (−10, −10); it never intersects and never costs an evaluation.
`ticks_per_stage=1000` in this scenario only, so the tree stays mature
(lifecycle timing is T1/T6's subject; T4's geometry must be stable).
Script: 5 stationary ticks, then walk east at 0.5/tick until blocked.
Tick numbering: the first stationary tick is tick 0.

- **Phase i (stationary, raycast range): collision evaluations = 0.**
  Raycast east returns node 1 at distance 7.0 every tick — the forest is
  visible, and carries no collision state and no collision compute.
- **Phase ii (walking, through the last successful move): collision
  evaluations = 14** (one per tick, ticks 13–26; the tree is the only
  candidate). **First evaluation at tick 13** — exactly the tick the
  candidate avatar bubble first intersects the tree's bubble (candidate
  position 4.5, center distance 7.5 < 3.0 + 5.0). At candidate 4.0 the
  distance is exactly 8.0 (tangent): no intersection, no evaluation.
- **Phase iii (blocked tick, reported for completeness): 1 evaluation**,
  tick 27. Candidate position 11.5 would enter the tree's body radius
  (distance 0.5 < 1.0): move blocked, one `collision_blocked` event logged,
  avatar stays at (11.0, 0.0) — distance to tree center exactly 1.0, the
  body boundary. Total evaluations across the scenario: 15.
- **Avatar position == bubble center asserted at every tick: holds**
  (the center is defined as the avatar's position — one source of truth).

Final sampler grid (near sampler centered (6, 0), 26×13, res 1.0; the
avatar is not a mesh member (A7), so it is not rendered — its final
position (11.0, 0.0) is the 'T' cell immediately left of the tree's
center column):

```
..........................
.................TTTTT....
................TTTTTTT...
...............TTTTTTTTT..
...............TTTTTTTTT..
...............TTTTTTTTT..
...............TTTTTTTTT..
...............TTTTTTTTT..
...............TTTTTTTTT..
................TTTTTTT...
.................TTTTT....
..........................
..........................
```

## Ambiguity log — every resolution I had to make myself

These are the spec's real test results: points where v0.1 did not dictate
an answer and I chose. Each choice is marked in the code (A1–A11).

- **A1 — Stage schedule.** The spec gives stage radii but no ages.
  Resolution: uniform `ticks_per_stage` (default 10); stage =
  age // ticks_per_stage; decaying is terminal (C6's sequence ends there;
  no death/removal in the toy).
- **A2 — Body radii.** Not specified. Resolution: body_radius =
  bubble_radius × kind fraction — tree 0.2, rock 0.8, terrain 0.0
  (non-blocking). Consequence: a mature tree's body radius is 1.0.
- **A3 — Avatar bubble radius / avatar body.** Not specified. Resolution:
  avatar bubble radius fixed at 3.0; avatar treated as a point in the body
  test ("the move would enter an active node's body radius").
- **A4 — Collision query position.** "Before the move resolves" does not
  say at which position the bubble query runs. Resolution: at the
  candidate (post-move) position. Bubble intersection is strict
  (distance < r_avatar + r_node); tangent does not count. The
  first-evaluation tick in T4 is defined on this rule.
- **A5 — Rendering a covering set in one cell.** The query returns a set
  ("no winner declared"), but a cell holds one glyph. Resolution: glyph
  of the covering node minimizing distance/bubble_radius, tie-break lowest
  id. Sets, not glyphs, are what T2 compares.
- **A6 — Raycast distance.** "Return node id + distance" does not say to
  what. Resolution: distance to the bubble surface along the ray (0 if
  the origin is inside a bubble). All environmental kinds are raycastable.
- **A7 — Avatar in the mesh?** The avatar "is a node," but the collision
  query must return *environmental* nodes. Resolution: the avatar is a
  Node-like object not registered in the Mesh; its bubble queries the
  Mesh. Consequence: samplers do not render the avatar.
- **A8 — Do rocks/terrain age?** Unspecified. Resolution: only trees run
  the lifecycle; rock/terrain stage is "static," glyph fixed (R / ,).
- **A9 — Sampler point geometry.** Resolution: corner-anchored grid
  points (point = min + index × res), which makes T2's "world-points both
  cover" well-defined across resolutions.
- **A10 — What counts as one collision evaluation.** Resolution: one body
  check of one candidate node returned by the bubble-intersection query;
  the query itself is not counted. Phase counts: phase ii runs through
  the last successful move; the blocked tick is phase iii.
- **A11 — Blocked-move resolution.** No slide/clamp specified.
  Resolution: avatar stays at its last valid position (with the 0.5 step
  and 1.0 body radius it stops exactly on the body boundary).
