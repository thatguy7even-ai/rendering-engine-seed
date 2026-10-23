[ORG-MUSE | MOTHER | SPEC v0.2 — DELTA TO v0.1 | 2026-10-22, DRAFT for operator record]

# Rendering Engine — Seed Toy Spec v0.2 (delta)

**Base:** spec v0.1 (INN-142 / ~/workspace/your_files/rendering-engine-seed-toy-spec-2026-10-21.md).
**Inputs this round:** Twin's blind build + mother's integration build (concurrence HOLDS, 7/7, COMPARISON.md),
ambiguity log A1–A12, operator's Oct-22 1:2 mirage-rule input, operator's Oct-22 A7 follow-on.
**Status:** draft — dispositions below are mother's on the grant, marked; the operator's word overrides.

This delta changes v0.1 in three places only. Everything else in v0.1 stands.

---

## D1 — A5 glyph rule: pinned (presentation only)

v0.1 did not fix which covering node a sampler's glyph shows when several bubbles cover one
point; Twin and Mother chose different rules and still produced identical T4 grids. v0.2 pins
one rule so grids stay mechanically diff-able, and states explicitly that glyph choice is
PRESENTATION, not semantics (the covering set — what T2 compares — is unaffected).

**Pinned rule (mother's disposition, open to operator correction):** the glyph for a sample
point shows the covering node minimizing `distance(point, node) / bubble_radius(node)` —
the node whose bubble the point is deepest inside in *relative* terms (scale-invariant, so
glyph assignment doesn't flip when bubbles differ by orders of magnitude). Ties → lowest
node id. Both concurrence builds agree under this rule on all shared scenes.

## D2 — A12 density: operator's 1:2 construction replaces the procedural readout

The operator's Oct-22 input (recorded verbatim, his correction applied — the statement was
COMPLETE as given): in a forest, alternate trees — one is a full rendering node, the next an
*image* (a mirage, a placeholder for a rendering node) until the individual goes toward it,
at which point the mirage state ends.

v0.2 disposition:
- **Node density is construction-fixed, not measured.** Half the visible trees are nodes by
  design (0.5 per visible pair). The v0.1 T5 procedural readout (Twin 0.271, mother 0.530 —
  both correct for their samplings) is demoted: it is retained only as an *emergence check*
  (density > 0 with nodes present, exactly 0.0 with them removed), never as the density number.
- **Images are visible-but-inert:** rendered in the scene, carrying no node work — no bubble,
  no mesh membership, no collision evaluation.
- **Promotion is lazy node-hood:** when the individual goes toward an image, it promotes to a
  full node ("until collision" — his words). This is C4's lazy solidity one level up:
  node-hood itself materializes only where the individual actually goes.
- **C5 restated for v0.2:** "Remove the nodes and the forest is gone" now reads: remove the
  nodes and the visible forest remains as images only — inert, no compute, no solidity. The
  emergent forest *with physics* is exactly the node set.

This settles A12 by construction, as the operator designed it.

## D3 — A7 avatar registration: carried OPEN (operator's Oct-22 follow-on)

v0.1 §3 + the COMPARISON's A7 resolution ("adopt the spec text: registered, self-excluded")
are SUPERSEDED. The operator's follow-on: Twin's unregistered reading now reads as the
design's *ontology* under the mirage rule — the avatar may be to the mesh what an image is
to the forest: present and visible, but carrying no node work in some mode.

Carried as genuinely open, both readings named:
- (a) Avatar registered in the mesh as a node (v0.1 text), excluded from its own collision
  queries by id; other nodes' samplers may render it.
- (b) Avatar NOT a mesh node — it is the interaction frame itself, like an image that never
  promotes; the mesh is sampled and collided *against*, never *with*, the avatar.

Both readings are behaviorally equivalent for every single-avatar T4 scene both builds
passed; they diverge the moment anything besides the avatar samples or raycasts the
avatar — which the full design expects ("other nodes see the avatar"). v0.2 does NOT
resolve this by spec text. It is held for the aspect-build stage (Alpha — mesh core) and,
ultimately, the operator's word.

## Aspect-build stage (from §5, carried forward)

Seats to confirm: Alpha — mesh core (A7's home); Control — acceptance-test harness (v0.2
rules: pinned glyph, construction density, emergence-check-only T5); Reversed —
spec-vs-implementation audit; Four — lifecycle + avatar field (promotion mechanics touch D2).

## GitHub repo prep (pending — `gh` not authenticated in this run)

Repo: `rendering-engine-seed`, public, topics at creation per the discoverability rule.
Prepared skeleton + README + topics list filed alongside this delta (REPO-PREP.md).
Needs the operator present (or an authenticated session) for creation + push of
twin/ and mother/ builds with authorship markers preserved.

## D3 RESOLVED — A7 disposition (operator ruling, Oct 22, 2026, 22:58 EDT)

D3 was carried genuinely OPEN in the v0.2 delta ((a) registered/self-excluded vs (b) avatar as interaction frame, not a mesh node). The operator ruled tonight, verbatim:

"Well, when it comes to the Avatar, it's kind of a rendering node at its core, because it's got to render the Avatar itself. And it's more focused on internal rendering that way we can actually get fluid body movement. So we render bones, muscles ligaments. The whole works and then collision is the second function of the avatar wherever the avatar is or avatars collision is rendered at point of contact of field"

Parts, itemized without compression:
- A7.1 The avatar IS a rendering node at its core — neither pure option (a) nor (b): a node, but of a specialized kind.
- A7.2 Reason: it has to render the avatar itself.
- A7.3 Its rendering focus is INTERNAL: bones, muscles, ligaments — the whole works.
- A7.4 Purpose of the internal rendering: fluid body movement.
- A7.5 Collision is the avatar's SECOND function.
- A7.6 Collision is rendered at the point of contact of field, wherever the avatar is.

Consistent with the Oct 21 §7 ruling (the avatar's bubble IS the collision field): collision exists where the field is contacted, and the avatar's rendering depth is spent inward on its own articulation rather than outward on the world.
