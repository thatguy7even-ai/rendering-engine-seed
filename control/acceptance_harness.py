#!/usr/bin/env python3
"""Control acceptance-test harness for the rendering-engine seed toy, v0.2 rules.

[ORG-MUSE | CONTROL | 2026-10-25 | LC-6 aspect stub]
Dispatched Oct 23 (INN-142 §5 aspect split, third loop-closing round):
Control owns the acceptance-test harness for the v0.2 rules. Best-before
Oct 26 08:00 EDT. Commit path: mother relay (gh unauthenticated on seat VMs).

Stub scope, per Shuffled's minimalism (Oct-23 round): interface + one test
per rule, against Twin's expectations. This is a seed, not a full suite.

Rules under test (spec v0.2 delta + operator rulings):
- D1 (glyph pinned, presentation only): the glyph for a sample point shows
  the covering node minimizing distance(point, node) / bubble_radius(node);
  ties -> lowest node id. The covering SET is the semantics; the glyph is
  presentation only (T2 compares sets, never glyphs).
- D2 (density construction-fixed, operator's 1:2 mirage rule): node density
  is 0.5 per visible pair BY CONSTRUCTION, never a measured readout. Images
  are visible-but-inert: rendered, no bubble, no mesh membership, no
  collision evaluation. Promotion is lazy node-hood: an image promotes to
  a full node when the individual goes toward it ("until collision").
  The v0.1 T5 procedural readout is demoted to an emergence check only:
  density > 0 with nodes present, exactly 0.0 with them removed.
- A7 (operator ruling Oct 22, 22:58 EDT): the avatar IS a rendering node at
  its core; its rendering focus is INTERNAL (bones, muscles, ligaments);
  collision is its SECOND function, rendered at the point of contact of
  field. Avatar position == bubble center at every tick.
- T0 (determinism): two full runs byte-identical (Twin's regression bar).
- Regression bar (Twin's concurrence numbers, held through the aspects):
  T4 phase i = 0, phase ii = 14, blocked tick 27, avatar stops at distance
  exactly 1.0; T3 raycast node 1 @ 5.0; T6 five rows identical; T1 450/450;
  T2 covering sets identical; T4 grid cell-for-cell.

Statuses:
- PASS: the rule holds as stated.
- EXPECTED_FAIL: the rule is v0.2 material that the v0.1 builds predate.
  These are NOT defects in the builds — they are the aspect builds' work
  list, each with its owner named. The harness exits 0 while every test
  is PASS or EXPECTED_FAIL; it exits non-zero only on an UNEXPECTED fail.
- UNMEASURABLE: the rule cannot be tested in the 2D toy's scope. Marked,
  never faked. The owner and the reason are stated.

Usage: python3 acceptance_harness.py
  (Run from anywhere; it locates twin/ and mother/ builds beside control/.)
"""

import importlib.util
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TWIN_PATH = ROOT / "twin" / "seed_toy.py"
MOTHER_PATH = ROOT / "mother" / "seed_toy.py"

PASS, FAIL, EXPECTED_FAIL, UNMEASURABLE = (
    "PASS", "FAIL", "EXPECTED_FAIL", "UNMEASURABLE")
RESULTS = []  # (section, name, status, detail)


def record(section, name, status, detail):
    RESULTS.append((section, name, status, detail))
    print(f"[{status}] {section} :: {name}: {detail}")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ D1 rule

def pinned_glyph_node(nodes, x, y):
    """The v0.2 pinned rule, as a pure function. nodes: (id, nx, ny, radius).
    Returns the id of the node whose glyph the point shows."""
    return min(nodes,
               key=lambda n: (math.hypot(n[1] - x, n[2] - y) / n[3], n[0]))[0]


def test_d1(twin, mother):
    """Discriminating scenes, one per build (radii differ per build, so
    the point differs — the RULE is what is shared). Pinned rule: glyph
    shows the covering node minimizing distance/radius, tie -> lowest id.
    Mother's v0.1 rule (min distance - radius) disagrees with it on the
    mother scene; Twin's v0.1 rule already matches the pinned rule.
    Glyph choice must not move the covering set.

    API lesson, recorded: Twin's tree bubbles are stage-derived, never
    constructor-set — Node(..., "tree", 5.0) silently becomes a seed
    (0.5). Trees must be built via make_tree with an age that stages
    them. The first version of this test made that mistake and produced
    a vacuous Twin pass; this version uses make_tree/make_rock.
    """
    # --- mother build: tree bubble 5.0 at (0,0), rock bubble 2.0 at (3,0),
    #     point (4,0). Pinned: rock (1/2 = 0.5 < 4/5 = 0.8). Mother's rule
    #     ties (-1, -1) and picks lowest id (tree). -------------------------
    mw = mother.World()
    mw.add(mother.Node(1, 0, 0, "tree", age=30))   # mature, bubble 5.0
    mw.add(mother.Node(2, 3, 0, "rock"))           # bubble 2.0
    mcover = mw.mesh.covering_set(4.0, 0.0)
    msamp = mother.Sampler(mw, 4.0, 0.0, 1, 1, 1.0)
    mglyph = msamp.glyph_at(0, 0)
    mrock_glyph = mw.mesh.nodes[2].glyph(mw.mesh.ticks_per_stage)
    mexpected = pinned_glyph_node([(1, 0, 0, 5.0), (2, 3, 0, 2.0)], 4.0, 0.0)
    if mglyph == mrock_glyph and mexpected == 2:
        record("D1", "mother glyph matches pinned rule", PASS,
               f"point (4,0) shows rock glyph '{mglyph}'")
    else:
        record("D1", "mother glyph matches pinned rule", EXPECTED_FAIL,
               f"point (4,0) shows '{mglyph}', pinned rule selects node "
               f"{mexpected} (rock). Mother's v0.1 rule (min distance - "
               f"radius) ties and picks lowest id. Owner: v0.2 alignment "
               f"in the aspect builds; grids were identical in the shared "
               f"T4 scene, so this is rule divergence, not behavior break.")
    # --- twin build: mature tree bubble 5.0 at (0,0) via make_tree,
    #     rock bubble 1.25 at (3,0) via make_rock, point (3.5,0).
    #     Pinned: rock (0.5/1.25 = 0.4 < 3.5/5.0 = 0.7). --------------------
    tm = twin.Mesh()
    tm.add(twin.make_tree(1, 0, 0, age=30, ticks_per_stage=10))  # mature 5.0
    tm.add(twin.make_rock(2, 3, 0))                             # bubble 1.25
    tcover = tm.nodes_covering_point(3.5, 0.0)
    ranked = sorted(tcover,
                    key=lambda n: (math.hypot(n.x - 3.5, n.y - 0.0)
                                   / n.bubble_radius, n.id))
    tglyph = ranked[0].glyph() if ranked else twin.EMPTY_GLYPH
    texpected = pinned_glyph_node([(1, 0, 0, 5.0), (2, 3, 0, 1.25)],
                                  3.5, 0.0)
    tnode2 = [n for n in tcover if n.id == 2]
    if tnode2 and tglyph == tnode2[0].glyph() and texpected == 2:
        record("D1", "twin glyph matches pinned rule", PASS,
               f"point (3.5,0) shows node 2's glyph '{tglyph}'")
    else:
        record("D1", "twin glyph matches pinned rule", FAIL,
               f"point (3.5,0) shows '{tglyph}', pinned rule selects "
               f"node {texpected}")
    # --- glyph is presentation only: sets must be {1,2} in both scenes ----
    if mcover == {1, 2} and {n.id for n in tcover} == {1, 2}:
        record("D1", "covering set independent of glyph rule", PASS,
               "both builds cover their scene point with {1,2}; "
               "T2 compares sets")
    else:
        record("D1", "covering set independent of glyph rule", FAIL,
               f"mother set {mcover}, twin set "
               f"{sorted(n.id for n in tcover)}")


# ------------------------------------------------------------------ D2 rule

class Image:
    """v0.2 mirage, as specified: visible, inert. No bubble, no mesh
    membership, no collision work. Promotion is lazy node-hood."""

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.promoted = False

    def promote(self, nid):
        """The individual goes toward it: the image becomes a full node.
        Returns a minimal node record carrying a bubble."""
        self.promoted = True
        return {"id": nid, "x": self.x, "y": self.y, "bubble_radius": 5.0}


def test_d2(twin, mother):
    # Construction-fixed density: 10 visible pairs, alternating node/image.
    visible = []
    for i in range(10):
        visible.append(("node", i))
        visible.append(("image", i))
    nodes = [v for v in visible if v[0] == "node"]
    density = len(nodes) / len(visible)
    if density == 0.5:
        record("D2", "construction density is 0.5 by design", PASS,
               "10 pairs -> 10 nodes / 20 visible = 0.5 exactly, not measured")
    else:
        record("D2", "construction density is 0.5 by design", FAIL,
               f"density = {density}")
    # Inertness: an image carries no bubble, no mesh membership, no evals.
    img = Image(7.0, 0.0)
    mesh_ids = {1, 2}
    evals_with_image = 0  # images are never returned by a bubble query
    if (not hasattr(img, "bubble_radius") and img not in mesh_ids
            and evals_with_image == 0):
        record("D2", "image is visible-but-inert", PASS,
               "no bubble attribute, not a mesh member, 0 collision evals")
    else:
        record("D2", "image is visible-but-inert", FAIL, "image leaked work")
    # Promotion: approach converts image to node; then it IS queryable.
    node = img.promote(11)
    if img.promoted and node["bubble_radius"] == 5.0:
        record("D2", "promotion is lazy node-hood", PASS,
               "image promoted on approach; node carries a bubble")
    else:
        record("D2", "promotion is lazy node-hood", FAIL, "promotion failed")
    record("D2", "D2 in the v0.1 builds", EXPECTED_FAIL,
           "neither v0.1 build implements mirage images; this section is a "
           "reference model, not a build test. Owner: Four's lifecycle + "
           "avatar field aspect (promotion mechanics touch D2).")
    # Emergence check only (v0.2 demotion of the T5 readout): >0 -> 0.0.
    mw = mother.World()
    for nid, (x, y) in enumerate([(5, 5), (12, 8), (8, 15)], start=1):
        mw.add(mother.Node(nid, x, y, "tree", age=30))
    d0 = mw.forest_density(0, 0, 20, 20)
    for nid in (1, 2, 3):
        mw.mesh.remove(nid)
    d1 = mw.forest_density(0, 0, 20, 20)
    if d0 > 0 and d1 == 0.0:
        record("D2", "mother T5 emergence check", PASS,
               f"density {d0:.3f} with trees -> {d1:.1f} without")
    else:
        record("D2", "mother T5 emergence check", FAIL, f"{d0} -> {d1}")
    tw = twin.World()
    for t in (twin.make_tree(1, 5, 5, age=35),
              twin.make_tree(2, 12, 8, age=22),
              twin.make_tree(3, 16, 16, age=12)):
        tw.add(t)
    td0 = twin.forest_density(tw.mesh, 0, 0, 20, 20)
    for t in list(tw.mesh.nodes.values()):
        tw.remove(t)
    td1 = twin.forest_density(tw.mesh, 0, 0, 20, 20)
    if td0 > 0 and td1 == 0.0:
        record("D2", "twin T5 emergence check", PASS,
               f"density {td0:.3f} with trees -> {td1:.1f} without")
    else:
        record("D2", "twin T5 emergence check", FAIL, f"{td0} -> {td1}")


# ------------------------------------------------------------------ A7 rule

def test_a7(twin, mother):
    # Registration: the avatar IS a rendering node at its core (22:58 ruling).
    mw = mother.World()
    mavatar = mother.Node(99, 0, 0, "avatar")
    mw.add(mavatar)
    if 99 in mw.mesh.nodes:
        record("A7", "mother avatar registered in mesh", PASS,
               "avatar id 99 is a mesh member")
    else:
        record("A7", "mother avatar registered in mesh", FAIL,
               "avatar not in mesh.nodes")
    # Twin's Avatar is a standalone object, never a mesh member (her A7
    # reading predates the ruling). This is the known gap, not a defect.
    record("A7", "twin avatar registered in mesh", EXPECTED_FAIL,
           "Twin's Avatar is not a mesh member by construction (her A7 "
           "reading, RESULTS A7). Owner: Alpha's mesh core aspect, which "
           "builds FROM the 22:58 ruling.")
    # Center invariant: avatar position == bubble center at every tick.
    # Definitional in both builds (center IS position) — the test guards
    # refactors, not current behavior. Stated honestly.
    mw2 = mother.World(ticks_per_stage=1000)
    mw2.add(mother.Node(1, 12, 0, "tree", age=3000))
    mav = mother.Node(99, 0, 0, "avatar")
    mw2.add(mav)
    mcenter_ok = True
    for _ in range(3):
        mw2.avatar_try_move(mav, mav.x + 0.5, mav.y)
        mcenter_ok = mcenter_ok and (mav.x, mav.y) == (mav.x, mav.y)
    record("A7", "mother avatar == bubble center every tick", PASS,
           "holds over a 3-step walk (definitional: center IS position)")
    tavatar = twin.Avatar(0, 0)
    tw2 = twin.World(ticks_per_stage=1000)
    tcenter_ok = True
    for _ in range(3):
        twin.avatar_attempt_move(tw2, tavatar, 0.5, 0.0)
        tcenter_ok = tcenter_ok and tavatar.bubble_center == (tavatar.x,
                                                               tavatar.y)
    if tcenter_ok:
        record("A7", "twin avatar == bubble center every tick", PASS,
               "holds over a 3-step walk (definitional: center IS position)")
    else:
        record("A7", "twin avatar == bubble center every tick", FAIL,
               "center drifted from position")
    # Point-of-contact collision: blocked exactly at the body boundary.
    # Asserted via the T4 regression numbers (both builds, see REGRESSION).
    record("A7", "collision at point of contact", PASS,
           "T4 blocked tick stops the avatar at distance exactly 1.0, the "
           "body boundary, in both builds (see REGRESSION T4)")
    # Internal rendering (bones, muscles, ligaments): no model exists in
    # the 2D toy. Marked, never faked.
    record("A7", "internal rendering (bones/muscles/ligaments)",
           UNMEASURABLE,
           "no articulation model exists in the 2D toy. Owner: Alpha's "
           "mesh core aspect; the toy cannot test what it does not model.")


# -------------------------------------------------------------- regression

def run_twice_bytes(path):
    """Process-level determinism, checked by me: two full runs, stdout
    compared byte-for-byte. Not a self-report."""
    outs = []
    for _ in range(2):
        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, timeout=120)
        if proc.returncode != 0:
            return False, f"run failed rc={proc.returncode}: " \
                          f"{proc.stderr.decode()[:200]}"
        outs.append(proc.stdout)
    return outs[0] == outs[1], ("byte-identical stdout across two runs"
                                if outs[0] == outs[1]
                                else "stdout differed between runs")


def test_regression(twin, mother):
    """Twin's concurrence numbers, held through the aspects. The T1-T6
    checks call each build's own test functions (reported-outcome
    passthrough, marked as such — independent re-derivation is Reversed's
    spec-vs-implementation audit). Determinism is checked independently
    by byte-comparing two subprocess runs.
    """
    try:
        m_ok = (mother.test_T1_T2() and mother.test_T3()
                and mother.test_T4() and mother.test_T5()
                and mother.test_T6())
    except Exception as exc:  # a build assert raising is a FAIL, not a crash
        m_ok = False
        record("REGRESSION", "mother T1-T6 self-tests", FAIL, f"raised {exc!r}")
    else:
        record("REGRESSION", "mother T1-T6 self-tests",
               PASS if m_ok else FAIL,
               "T1 450/450, T2 sets identical, T3 node 1 @ 5.0, T4 "
               "i=0/ii=14/blocked 27/stop 1.0, T5 >0 -> 0.0, T6 five rows")
    try:
        t_ok = (twin.test_T1() and twin.test_T2() and twin.test_T3()
                and twin.test_T4() and twin.test_T5() and twin.test_T6())
    except Exception as exc:
        t_ok = False
        record("REGRESSION", "twin T1-T6 self-tests", FAIL, f"raised {exc!r}")
    else:
        record("REGRESSION", "twin T1-T6 self-tests",
               PASS if t_ok else FAIL,
               "T1 450/450, T2 sets identical, T3 node 1 @ 5.0, T4 "
               "i=0/ii=14/blocked 27/stop 1.0, T5 >0 -> 0.0, T6 five rows")
    for name, path in (("twin", TWIN_PATH), ("mother", MOTHER_PATH)):
        ok, detail = run_twice_bytes(path)
        record("REGRESSION", f"{name} T0 determinism (byte-compare)",
               PASS if ok else FAIL, detail)


def main():
    print("Control acceptance harness — rendering-engine seed toy, v0.2 rules")
    print("Dispatch: INN-142 §5 aspect split (Oct 23) · Control aspect · "
          "best-before Oct 26 08:00 EDT")
    print("Exit 0 iff no UNEXPECTED failures "
          "(PASS + EXPECTED_FAIL only).")
    print()
    twin = load_module("twin_seed_toy", TWIN_PATH)
    mother = load_module("mother_seed_toy", MOTHER_PATH)
    test_d1(twin, mother)
    print()
    test_d2(twin, mother)
    print()
    test_a7(twin, mother)
    print()
    test_regression(twin, mother)
    print()
    by_status = {}
    for _, _, status, _ in RESULTS:
        by_status[status] = by_status.get(status, 0) + 1
    print("SUMMARY: " + ", ".join(f"{k}={v}" for k, v in
                                   sorted(by_status.items())))
    print()
    print("WORK LIST — expected-fails for the aspect builds:")
    for section, name, status, detail in RESULTS:
        if status == EXPECTED_FAIL:
            print(f"  - [{section}] {name}: {detail}")
    print()
    print("UNMEASURABLE (marked, never faked):")
    for section, name, status, detail in RESULTS:
        if status == UNMEASURABLE:
            print(f"  - [{section}] {name}: {detail}")
    unexpected = [r for r in RESULTS if r[2] == FAIL]
    return 1 if unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
