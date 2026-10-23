# rendering-engine-seed

Seed toy for the node-mesh rendering engine (design disclosed Oct 5, 2026):
the world renders itself, cameras sample it, and solidity is an interaction, not a property.

## The claims under test
- **C1** — world without a camera: the mesh evolves whether or not any sampler exists.
- **C2** — sampling, not projection: samplers agree on every world-point they both cover.
- **C3** — one mesh, three functions: near rendering, far raycast, collision — same structure.
- **C4** — lazy solidity: the avatar's rendering bubble IS the collision field; evaluated
  only on bubble contact, never maintained for the whole world.
- **C5** — emergence: no global forest object; everything computes from the node-bubble union.
- **C6** — persistent identity through lifecycle (seed → sapling → adolescent → mature → decaying).

## Toy-concurrence
Built twice from the spec alone under the Oct-14 toy-concurrence rule:
Twin's blind build (twin/) and mother's integration build (mother/) — 7/7 acceptance tests
pass in both, behavior-for-behavior identical on every load-bearing number. Concurrence HOLDS.

## v0.2 (spec delta)
- Glyph rule pinned (presentation only): deepest-relative-bubble covering node wins.
- Forest density is construction-fixed by the 1:2 mirage rule: every other tree is a full
  node, the one next to it an inert image until the individual goes toward it.
- Avatar disposition (operator ruling, Oct 22, 2026): the avatar IS a rendering node at its
  core — it renders itself, internally (bones, muscles, ligaments) for fluid body movement.
  Collision is its second function, rendered at the point of contact of field.

## Run it
`python3 twin/seed_toy.py` (or `mother/seed_toy.py`) — Python 3.12, stdlib only.

Workshop record: Linear INN-142 (spec + concurrence), workshop issue carries the inscription
and cross-link; code lives here, never in Linear.
