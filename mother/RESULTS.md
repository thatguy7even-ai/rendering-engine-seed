[ORG-MUSE | MOTHER | 2026-10-22]

# RESULTS — Rendering-engine seed toy, mother's integration build

Built from spec v0.1 (INN-142) + the operator's §7 ruling, as the
integration counterpart to Twin's independent concurrence build
(`../twin/`). Python 3 stdlib only, seeded RNG, deterministic.
Code: `seed_toy.py` (this directory). Run: `python3 seed_toy.py`.

## Acceptance tests — all PASS

- **T0 (determinism) — PASS.** Two full process runs byte-identical
  (output digest sha256 `c374f748c91dbc5f…`).
- **T1 (C1) — PASS.** 200 ticks, no sampler attached; lifecycle advanced
  (9/12 trees changed stage). Sampler attached at tick 200 reads a
  coherent world: covering sets agree with direct mesh queries at
  450/450 sample points, zero initialization artifacts.
- **T2 (C2) — PASS.** Two samplers (20×20 @ res 1.0; 10×10 @ res 2.0),
  same tick: covering node sets identical at 100/100 shared
  world-points. (Count differs from Twin's 25 — sampler geometry, not
  semantics; the invariant is agreement.)
- **T3 (C3) — PASS.** Raycast east from the avatar returns node 1
  (mature tree at (10, 0)) at distance 5.0; the near sampler's first
  covered point east on y=0 is (5.0, 0.0) with covering set {1}. Code
  audit: exactly one spatial structure exists (`class Mesh`, one spatial
  hash); sampler, raycast, and collision all call its three query
  methods (`covering_set`, `raycast`, `bubble_intersections`).
- **T4 (C4) — PASS.** Same shared scenario as Twin's filing (avatar at
  (0, 0), bubble 3.0; mature tree node 1 at (12, 0), bubble 5.0, body
  1.0; rock off-corridor; 5 stationary ticks, then walk east 0.5/tick).
  Phase i: **collision evaluations = 0**, raycast returns node 1 at 7.0
  every tick. **First evaluation at tick 13** (candidate 4.5, center
  distance 7.5 < 3.0 + 5.0; the tangent pass at exactly 8.0 costs
  nothing). Phase ii: **14 evaluations** (ticks 13–26). Blocked at
  **tick 27** (1 evaluation), avatar stops at (11.0, 0.0) — distance to
  tree center exactly 1.0, the body boundary. Total evaluations 15.
  Avatar == bubble center asserted at every tick (28 ticks): holds —
  the center is defined as the avatar's position, one source of truth.
- **T5 (C5) — PASS.** Forest density of region (0,0)–(20,20): 0.530
  with three trees, computed from node coverage alone; after removing
  all tree nodes, 0.0, and the sampler shows no tree glyphs in the
  region. No forest object exists in the code. (The 0.530 value is
  placement- and sampling-dependent — see A12 in the comparison.)
- **T6 (C6) — PASS.** One seed, one id throughout; (tick, stage, bubble
  radius, raycast distance from (−20, 0), glyph):
  (0, seed, 0.5, 19.5, 'v') · (10, sapling, 1.5, 18.5, 's') ·
  (20, adolescent, 3.0, 17.0, 'a') · (30, mature, 5.0, 15.0, 'T') ·
  (40, decaying, 4.0, 16.0, 'd'). Radii match the §3 stage table at
  every stage; glyph and raycast track the stage.

Final T4 grid in the run output is cell-for-cell identical to Twin's
filed grid (see COMPARISON.md for why that is and isn't surprising).
