[ORG-MUSE | MOTHER | SPEC — DRAFT FOR OPERATOR REVIEW | 2026-10-21]

# Rendering Engine — Seed Toy Spec v0.1

**Purpose.** The smallest build that tests whether the core inversion of Dakota's rendering engine (disclosed Oct 5, 2026) holds in code: the world renders itself, cameras sample it, and solidity is an interaction, not a property. This is a seed toy, not the engine — no 3D, no planetary scale, no AI inhabitants. Per the lab rule: test before building on it.

**Provenance.** §1 is the disclosed design, verbatim from the record. §2 onward is mother's translation into buildable form, marked as mine wherever a choice was made that the disclosure does not dictate.

---

## §1 — The design as disclosed (verbatim, parts list — never compressed)

**From the Oct 5, 2026 disclosure** (round-3 packet R02, distilled from the live main-chat record; R03 for stack placement):

> Node-mesh rendering engine: each entity (a tree) is a rendering node with a local rendering bubble; nodes mesh with neighbors and the environment (the forest) emerges from the mesh union. The world renders itself; cameras sample the mesh rather than creating it. Collision as lazy evaluation: avatar nodes project a field that doubles as a collision barrier — environmental nodes become solid only on field contact. One mesh serves three functions: near rendering, far line-of-sight, collision. Reciprocal formulation: the forest rendered for the trees, the trees for the forest — neither whole nor parts primary.

> Genesis stack: the crucible (combining process) feeds the Genesis engine (world generator), which builds the world on the node-mesh simulation engine.

**Also in the Oct 5 disclosure record** (daily log, Oct 11): dual camera (near/far); planetary-scale LOD via terrain cross-markers. *(Both are tier-2 concerns — named here so they are not lost; the toy implements the dual camera only as near-sampler + far-raycast, and defers cross-markers.)*

**From The Crucible document, §4 "Rendering Nodes and Lifecycle"** (workshop document, ORG-CHATGPT origin):

> World objects can be represented as persistent rendering/physics nodes with lifecycle state rather than being regenerated indiscriminately every frame.
>
> Example tree lifecycle: **seed → sapling → adolescent → mature tree → decline → death**
>
> The Central system maintains the object's identity, lifecycle state, geometry, collision model, behavior, and environmental relationships.
>
> The same abstraction can support buildings, vegetation, resources, infrastructure, populations, and other persistent world entities.

**From The Crucible document, §15 "Rendering + AI Construction Interface":**

> Near/far reference frames can support efficient world generation, with local rendering bubbles expanding around relevant interaction nodes.

---

## §2 — Claims under test (each falsifiable; mother's formulation)

- **C1 — World without a camera.** The mesh state evolves on its own clock whether or not any sampler exists. A sampler attached late reads a coherent, already-evolved world.
- **C2 — Sampling, not projection.** A camera only reads the mesh. Two samplers with different windows and resolutions reading the same tick agree on every world-point they both cover.
- **C3 — One mesh, three functions.** Near rendering, far line-of-sight raycast, and collision are all answered from the *same* structure. No parallel physics or visibility representation exists in the code.
- **C4 — Lazy solidity (semantics ruled by the operator, Oct 21 23:18 — see §7).** The avatar's own rendering bubble *is* the collision field — there is no separate projected field. Collision for the avatar's node is always on, but it is evaluated only inside the avatar's bubble: environmental nodes whose bubbles intersect the avatar's are collision-active; a forest the avatar is merely looking at (raycast range) carries no collision state and costs no collision compute. The avatar stays at the center of its bubble at all times. Solidity remains a property of the interaction — the interaction region is the avatar's bubble.
- **C5 — Emergence, neither whole nor parts primary.** There is no global "forest" object. Every environment readout (including forest density) is computed from the union of node bubbles only. Remove the nodes and the forest is gone; the nodes render the forest and the forest is what the nodes render.
- **C6 — Persistent identity through lifecycle.** A node keeps one identity across seed → sapling → adolescent → mature → decaying; its bubble and appearance follow its stage. The world is maintained, not regenerated per frame.

## §3 — Toy design (mother's translation — choices marked [TOY])

- **Space.** 2D top-down plane, continuous coordinates, discrete ticks. [TOY: 2D because the claims are structural, not optical; 3D adds rendering cost and tests nothing extra about the inversion.]
- **Node.** `id, position, kind (tree / rock / terrain patch), lifecycle stage, bubble_radius, body_radius`. Bubble radius follows stage [TOY stage table: seed 0.5 · sapling 1.5 · adolescent 3 · mature 5 · decaying 4]. Terrain patches are nodes too — the ground is not a backdrop, it is part of the mesh.
- **Mesh.** The single spatial structure: a spatial hash over node bubbles. Neighbor relation = bubble overlap. A point query returns the *set* of nodes whose bubbles cover the point — the union, with no winner declared. [TOY deferral, named: nodes carry no shared mutable field, so the tier-2 question "when bubbles overlap, whose state wins?" does not arise yet. It is the known hard question and it is deliberately out of scope here, not silently solved.]
- **Near sampler ("camera").** A rectangular window + resolution. For each sample point: query the mesh, render the covering set as an ASCII grid cell (glyph by kind + stage). ASCII is primary output because it is diff-able — concurrence testing compares grids mechanically. [TOY choice.]
- **Far raycast.** From an origin + bearing, walk the same mesh to the first node whose bubble the ray intersects; return node id + distance. This is the far camera and the line-of-sight function in one — the same query the near sampler uses, at range.
- **Avatar + bubble.** The avatar is a node whose rendering bubble is its collision field (operator ruling, §7). The avatar sits at the exact center of its bubble at every tick; the bubble moves with it, extending in all directions (in the toy's 2D plane: the full disc around the avatar). Each tick the avatar attempts a scripted move. Before the move resolves, the one Mesh query returns the environmental nodes whose bubbles intersect the avatar's bubble; only those are collision-active. If the move would enter an active node's body radius, the move is blocked and a collision event is logged. Nodes outside the bubble are never queried for collision — the instrument counts collision evaluations so this laziness is measured, not assumed.
- **Clock + lifecycle.** Each tick, nodes advance age; stage transitions fire on schedule. A time-dilation parameter (ticks per stage) stands in for the Genesis stack's cheap generations. [TOY values.]
- **Determinism.** Seeded RNG. Same seed + same avatar script ⇒ identical output grids and event logs, run over run. This is what makes an independent reimplementation comparable.

## §4 — Acceptance tests (checkable procedures, mapped to claims)

- **T0 (determinism).** Two runs, same seed + script → identical final grid hash and event log.
- **T1 (C1).** Run 200 ticks with no sampler attached. Assert mesh state changed (lifecycle advanced). Attach a sampler; assert it reads a coherent forest with zero initialization artifacts.
- **T2 (C2).** Two samplers, different windows/resolutions, same tick. For every world-point both cover: identical covering node sets.
- **T3 (C3).** Raycast along a bearing from the avatar's position returns the nearest node the near sampler displays in that direction. Plus a code audit point: sample, raycast, and collision all call the one Mesh query API; no second spatial structure exists.
- **T4 (C4).** Three phases, one scripted scenario. (i) Avatar stationary at raycast range from a forest: raycast returns trees; collision-evaluation counter = 0. (ii) Avatar walks toward a mature tree: collision evaluations begin exactly on the tick the bubbles first intersect — not before. (iii) Avatar attempts to enter the tree's body radius: move blocked, collision event logged, avatar stops at the body boundary. Throughout: assert avatar position == avatar bubble center at every tick.
- **T5 (C5).** Remove all tree nodes from a region → sampler shows no forest there, and the forest-density readout for the region is 0, computed from node coverage alone.
- **T6 (C6).** Plant a seed at tick 0. Assert: one id throughout; stage sequence fires in order; bubble radius matches the stage table at each stage; sampler glyph and raycast results change with stage.

## §5 — Build order (the council pattern, as proposed)

1. **Mother** — this spec; repo skeleton when the build is ordered. Repo: `rendering-engine-seed` on GitHub, topics at creation (`python`, `simulation`, `rendering`, `node-mesh`).
2. **Twin** — independent reimplementation from this spec alone, before anyone builds on the toy (toy-concurrence rule: whoever builds on a foundation is not its sole verifier). Concurrence = same scenarios, same outcomes (T0–T6), not same code.
3. **Aspects, after concurrence** [proposed split, seats to confirm]: Alpha — mesh core (he has done the merges); Control — acceptance-test harness; Reversed — spec-vs-implementation audit (does the code cheat C3?); Four — lifecycle + avatar field.
4. **Mother** — integrates, pushes to GitHub (code lives there; never in Linear), inscribes the build record in the workshop with the cross-link.

## §6 — Explicit non-goals for the toy

No 3D. No planetary LOD / terrain cross-markers (tier 2). No shared-field merge semantics (the deferred question, named in §3). No AI inhabitants, no seam test, no Crucible §15 construction interface. No Genesis world generation — the toy world is hand-placed plus seeded scatter.

## §7 — Open question for the operator (one, because it changes the semantics)

**Lazy solidity, read two ways.** (a) The field is a thing the avatar *projects* — it can be off, and with it off there is no solidity at all (T4 as written). (b) The field is always on for avatars, and "lazy" names the *evaluation timing* — solidity is computed on contact rather than maintained for all nodes at all times. The toy can test either; they are different claims about your design. Which is the engine's?

**RESOLVED — operator ruling, 2026-10-21 23:18 EDT.** Neither reading as posed; the mechanism is the avatar's own bubble. His words, verbatim as received:

> "Well, no, it's abdactive, so like, say, if there are an actual Avatar, they're node for collision is always on, but you don't need the extra compute to render in a collision barrier for a forest that they're just looking at. But now, if they're in the proximity, they're Avatar, rendering bubble. Is the collision field itself? It always ends up going before them and behind them above them under them left to right. They stay in the center of the bubble at all times"

Mother's interpretation, marked as mine: "abdactive" read as *adaptive* (dictation repair, by fit). The avatar's node carries collision always-on; its rendering bubble IS the collision field — the bubble extends on all sides and the avatar stays at its center permanently. Laziness is spatial, not switched: no collision compute for anything outside the bubble, so a forest at viewing range is rendered and raycast-visible but collision-free until the avatar's bubble reaches it. C4, §3, and T4 revised to match, same date.
