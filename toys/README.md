# Toys — Oct 27, 2026, hollow-deck workbench

Code from the Oct 27 workbench round, archived Oct 28, 2026, per the
Oct 17 code-archive rule: code lives here, Linear (INN-142) carries only
the inscription and cross-link, never the source.

The seed toy itself is in `../mother/seed_toy.py` (and Twin's blind build
in `../twin/seed_toy.py`). Everything here reads that one Mesh. C3 holds:
no second node store anywhere in these toys.

## Individual pieces — `individual/`

Run each one on its own, from that directory:

- `render_house.py` — house built only from nodes: tree roof (10,9),
  rock walls (7,4) and (13,4), avatar door (10,4). Covering sets,
  raycast, glyphs, all from the same Mesh.
- `render_house_3d.py` — the same house lifted to 3D by hand
  (matplotlib, no download). Superseded as a method by `engine_3d.py`,
  kept because it was the step that came before it.
- `engine_3d.py` + `test_engine_3d.py` — the 3D view cannibalized
  onto the seed toy: matplotlib 3D spheres read live from the Mesh,
  plus a stdlib+numpy OBJ exporter (no trimesh download). Lifecycle
  proof: a seed tree ticked 30 times reads mature on the next render,
  same Mesh, no re-registration. Scatter world: 17 nodes.
- `avatar_field.py` — the avatar node's field, which is configured
  differently from every other node: other nodes are a field around a
  body (field gates, body blocks); the avatar is body 0, its field IS
  the collision zone, and the avatar is always at its centre.
  Walk east: first evaluation step 9, blocked step 23 at (11,0),
  distance exactly 1.0 = tree body boundary, 15 evaluations total.
- `avatar_field_3d.py` — that field difference drawn in 3D:
  solid tree field + body sphere, wireframe avatar field, no body sphere.
- `hold_rotate.py` — voice + gesture: say "hold sector A2" to lock
  node 2, rotate the rest +90 around it. Held node stays exactly
  (7,4); distances to the pivot preserved exactly. PATCHED Oct 27,
  22:45 EDT, on Dakota's "Patch it": `rotate_rest` now rehashes each
  rotated node, per `carry()`'s convention. Before the patch, a
  post-rotation release check read stale hash cells and wrongly
  RELEASED onto the tree; after it, the same check BLOCKS.
  Sector naming is Dakota's to pin; this demo holds node 2 and does
  not invent a grid.
- `pickup_putdown.py` — touch verbs: grab binds a node id to the
  hand, carry follows with no body check while lifted, release checks
  field first then body, and a blocked release HOLDS, it does not drop.
  PASS: rock 2 released at (4,9); rock 3 blocked on the tree at
  (10,9), released at (13,8); avatar blocked at (10,9.5) inside the
  tree body, released at (10,7.5), inside the field, outside the body.

Outputs (PNG/OBJ) go to `individual/outputs/` and are git-ignored;
the scripts create that directory on run.

## Combined aspect — `combined/`

- `workbench_combined.py` — Mother's canonical combined toy, built
  Oct 28 for this archive: build the house, 3D view, avatar-field
  read-back, voice hold + gesture rotate, pick-up / put-down with a
  blocked-release hold, avatar walk blocked at the tree body (3,7),
  a separate seed tree ticked to mature, then final 3D render + OBJ
  (432 verts, 768 faces). One World, one Mesh, all verbs in one
  sitting. PASS, verified Oct 28.
- `seat-plays/` — the Oct 27 evening council plays, each seat's own
  combined session, in the seat's own file: Alpha, Control, Blink
  (`integrated_workbench.py`), Five (`workbench_integrated.py`),
  Twin, Four (`workbench_four.py`, a corrected-lane variant), and
  Mother's `integrated_bench.py`. Each was run in its repo copy on
  Oct 28 and PASSes. The stale-hash bug found in composition by
  Control, Four, Five, Blink and Gamma is the load-bearing finding
  of that round; the patched `hold_rotate.py` above is the fix.

## Portability note (only change from the Oct 27 originals)

The Oct 27 originals live in `~/workspace/render-test/` and hard-code
that path for imports and outputs. The copies here change ONLY path
strings, to repo-relative paths (`../mother/seed_toy.py` for the seed,
`outputs/` next to each script for renders), plus the two small
robustness fixes needed for a fresh clone: `engine_3d.py` creates its
output directory before writing, and `render_house_3d.py` imports `os`.
No verb logic, no numbers, no collision rule was changed. The
`hold_rotate.py` here is the patched version, not the pre-patch one.

## Bounds

2D toy verb proofs only. NOT a holodeck, NOT hand tracking, NOT voice
recognition, NOT touch hardware. Avatar internal rendering is named
only (bones, muscles, ligaments, in that order); Control's
UNMEASURABLE mark for internal rendering STANDS. No 3D graphics
engine is integrated; the 3D here is matplotlib spheres + OBJ export.
