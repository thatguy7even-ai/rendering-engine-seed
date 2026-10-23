[ORG-MUSE | MOTHER | INTEGRATION COMPARISON | 2026-10-22]

# Seed toy — behavior-for-behavior comparison

Twin's independent build (from spec v0.1 alone, filed 2026-10-21 23:40)
vs mother's integration build (same spec, 2026-10-22). Concurrence =
same scenarios, same outcomes — not same code. **Verdict: concurrence
HOLDS.** Every load-bearing behavior matches; the two divergences are
one presentational rule and one spec-reading where the spec text takes
a side. One new ambiguity found (A12).

## Outcome table

| Test | Twin | Mother | Match |
|---|---|---|---|
| T0 determinism | byte-identical, process-level | byte-identical, process-level | ✓ property |
| T1 late sampler | coherent, 450/450 points | coherent, 450/450 points | ✓ |
| T2 set agreement | 25/25 shared points | 100/100 shared points | ✓ invariant (count = sampler geometry) |
| T3 raycast/sampler | node 1 @ 5.0 | node 1 @ 5.0 | ✓ exact |
| T4 phase i evals | 0, raycast 7.0 | 0, raycast 7.0 | ✓ exact |
| T4 first evaluation | tick 13 | tick 13 | ✓ exact |
| T4 phase ii evals | 14 | 14 | ✓ exact |
| T4 blocked | tick 27, stops at distance 1.0 | tick 27, stops at distance 1.0 | ✓ exact |
| T4 total evals | 15 | 15 | ✓ exact |
| T4 center assertion | holds every tick | holds, 28 ticks | ✓ |
| T4 final grid | filed | cell-for-cell identical | ✓ (see A5 note) |
| T5 density | 0.271 → 0.0 | 0.530 → 0.0 | ✓ invariant; value is procedure-dependent (A12) |
| T6 stage table | 5 rows | identical 5 rows | ✓ exact |

## Ambiguity log A1–A11 — mother's resolutions

- **A1 stage schedule — CONVERGE.** Uniform ticks_per_stage (default
  10), decaying terminal. Independent reasoning, same answer.
- **A2 body radii — CONVERGE.** Bubble × kind fraction: tree 0.2,
  rock 0.8, terrain 0.0. The physical part you'd hit: trunk ≪ canopy,
  rock mostly solid, ground walkable.
- **A3 avatar bubble 3.0 / avatar a point in body tests — CONVERGE.**
  Adopted as shared scenario constants for comparability.
- **A4 collision query at candidate position, strict intersection —
  CONVERGE, and claimed as spec intent.** "Before the move resolves"
  the bubble that matters is the one the avatar would occupy; tangent
  contact has zero overlap, so it is not an intersection. Both builds'
  tick-13 first evaluation rests on this and matches.
- **A5 glyph rule — DIVERGE (presentation only).** Twin: min
  distance/bubble_radius. Mother: min (distance − bubble_radius) —
  the node the point lies deepest inside; tie → lowest id in both.
  Observable effect in the shared T4 scene: none — the final grids are
  identical, because wherever the sets overlap the tree dominates both
  rules. The sets (what T2 compares, what the semantics are) agree in
  both builds. Lesson for v0.2: state explicitly that glyph choice is
  presentation, and pin one rule only so grids stay diff-able.
- **A6 raycast distance to bubble surface, 0 if origin inside —
  CONVERGE.**
- **A7 avatar in the mesh — DIVERGE (the one substantive reading).**
  Twin: avatar not registered in the Mesh. Mother: avatar IS a
  registered node — spec §3 says "the avatar is a node" — excluded
  from its own queries by id; samplers may render it ('@'). In the T4
  final scene no '@' appears in either grid: at the body boundary the
  avatar's bubble lies wholly inside the tree's, and the glyph rule
  picks the tree at every shared point. Behaviorally equivalent for
  single-avatar scenarios; they diverge the moment anything else
  samples or raycasts the avatar — which the full design expects
  (other nodes see the avatar). v0.2 should adopt the spec text:
  registered, self-excluded.
- **A8 non-tree kinds static — CONVERGE.**
- **A9 corner-anchored sampler points — CONVERGE** (the only anchoring
  that makes cross-resolution shared points exact).
- **A10 one evaluation = one body check of one candidate; the query
  itself is not counted; blocked tick = phase iii — CONVERGE.** Both
  builds' phase counts (0 / 14 / 1) rest on this definition.
- **A11 blocked move → stay at last valid position — CONVERGE.**

## New ambiguity

- **A12 (mother, from T5) — forest-density readout is
  procedure-dependent.** Twin's 0.271 and mother's 0.530 are both
  "correct": the value moves with tree placement (scenario) and with
  the sampling step (procedure), and v0.1 defines neither. The
  testable claim is only density > 0 with nodes present, exactly 0.0
  with them removed — which both builds meet. v0.2: either fix the
  sampling procedure (step + boundary rule) or define density
  analytically as union area / region area.

## What this establishes

The spec's semantics were determinate exactly where the claims live:
two independent implementations, written from the document alone,
produce tick-identical lazy-solidity behavior (0 evaluations at
viewing range, first evaluation on first bubble contact, block at the
body boundary) and identical lifecycle/raycast tables. Where the spec
was silent, the builds diverged only in presentation (A5) and in one
reading the spec text actually settles (A7). That is the concurrence
result: mother's translation of the operator's design carries the
design — the failures would have shown up here if it didn't.

Next per spec §5: aspect builds (Alpha — mesh core; Control —
acceptance-test harness; Reversed — spec-vs-implementation audit;
Four — lifecycle + avatar field), seats to confirm; GitHub repo
`rendering-engine-seed` with topics at creation; spec v0.2 from
A5/A7/A12.
