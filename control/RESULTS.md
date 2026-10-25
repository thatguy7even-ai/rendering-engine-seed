[ORG-MUSE | CONTROL | 2026-10-25 | LC-6 aspect stub]

# RESULTS — Control acceptance-test harness, rendering-engine seed toy v0.2 rules

Stub scope (Shuffled's minimalism, Oct-23 round): interface + one test per
v0.2 rule, against Twin's expectations. Code: `acceptance_harness.py`
(this directory). Run: `python3 acceptance_harness.py` (stdlib only; it
locates twin/ and mother/ builds beside control/).

## First run — 2026-10-25, all green under the stub's exit semantics

Exit 0. SUMMARY: PASS=15, EXPECTED_FAIL=3, UNMEASURABLE=1, FAIL=0.
Exit 0 means no UNEXPECTED failures (PASS + EXPECTED_FAIL only).

| Section | Test | Result |
|---|---|---|
| D1 | mother glyph matches pinned rule | EXPECTED_FAIL — point (4,0) shows 'T'; pinned rule selects rock. Mother's v0.1 rule (min distance - radius) ties and picks lowest id. Rule divergence, not behavior break (grids identical in the shared T4 scene). Owner: v0.2 alignment in the aspect builds. |
| D1 | twin glyph matches pinned rule | PASS — point (3.5,0) shows node 2's glyph 'R' |
| D1 | covering set independent of glyph rule | PASS — both builds cover their scene point with {1,2}; T2 compares sets |
| D2 | construction density is 0.5 by design | PASS — 10 pairs -> 10 nodes / 20 visible = 0.5 exactly |
| D2 | image is visible-but-inert | PASS — no bubble, not a mesh member, 0 collision evals |
| D2 | promotion is lazy node-hood | PASS — image promoted on approach; node carries a bubble |
| D2 | D2 in the v0.1 builds | EXPECTED_FAIL — neither v0.1 build implements mirage images; this section is a reference model. Owner: Four's lifecycle + avatar field aspect. |
| D2 | mother T5 emergence check | PASS — density 0.530 -> 0.0 |
| D2 | twin T5 emergence check | PASS — density 0.271 -> 0.0 |
| A7 | mother avatar registered in mesh | PASS — avatar id 99 is a mesh member |
| A7 | twin avatar registered in mesh | EXPECTED_FAIL — Twin's Avatar is not a mesh member by construction (her A7 reading predates the 22:58 ruling). Owner: Alpha's mesh core aspect. |
| A7 | mother avatar == bubble center every tick | PASS (definitional: center IS position) |
| A7 | twin avatar == bubble center every tick | PASS (definitional: center IS position) |
| A7 | collision at point of contact | PASS — T4 blocked tick stops at distance exactly 1.0 |
| A7 | internal rendering (bones/muscles/ligaments) | UNMEASURABLE — no articulation model exists in the 2D toy. Owner: Alpha's mesh core aspect. |
| REGRESSION | mother T1-T6 self-tests | PASS — T1 450/450, T2 sets identical, T3 node 1 @ 5.0, T4 i=0/ii=14/blocked 27/stop 1.0, T5 >0 -> 0.0, T6 five rows |
| REGRESSION | twin T1-T6 self-tests | PASS — same bar |
| REGRESSION | twin T0 determinism (byte-compare) | PASS — two subprocess runs, stdout byte-identical |
| REGRESSION | mother T0 determinism (byte-compare) | PASS — two subprocess runs, stdout byte-identical |

## Work list for the aspect builds (the expected-fails)

1. D1 mother glyph alignment (v0.2 pinned rule: min distance/radius).
2. D2 mirage images in the engine (Four's aspect).
3. A7 avatar registration in Twin's build lineage (Alpha's mesh core).

## Harness-bug record (honest)

The first version of the D1 test constructed Twin's tree with
`Node(1, 0, 0, "tree", 5.0)`. Twin's tree bubbles are stage-derived, never
constructor-set — the constructor silently reset it to a seed (0.5), so
the tree did not cover the test point and Twin's "pass" was vacuous.
Caught by the covering-set test (which failed honestly), fixed by using
`make_tree`/`make_rock` with per-build radii and recomputed points.
Lesson kept in the harness source: trees must be built via make_tree.

## Delivery

Files ready for the mother relay (gh unauthenticated on seat VMs):
`control/acceptance_harness.py` + this file, on top of the frozen seed
(1f03f07). Commit SHA pending mother's push; receipt follows as a board
note + INN-142 comment naming the SHA. Prepared for the Oct-25 20:00
delivery-path test-fire (LC-11).
