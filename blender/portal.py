"""
Procedural Blender model + Factorio render of the portal (endgame "Portal home").

One model, two entities, chosen with --state:

  inactive  The gate is being dialled home while it crafts "portal-home"
            (120 s, fed with divination essence). Two steam engines on the
            gate's flanks, fired by divination essence in the boilers at the
            front corners, drive the great toothed rune ring through pinions.
            It turns a glyph or two, the master chevron at the top clamps
            down on the chosen glyph and one more chevron lights; after eight
            locks the dark membrane in the ring surges and the cycle starts
            again (an assembling machine's animation simply loops). Frame 0
            is the dormant gate: shown frozen whenever the portal is idle.
  active    The portal is open: all chevrons lit, the rune ring turns
            steadily (the engines keep running - it needs a steady stream of
            essence to stay open), a swirling vortex with a glimpse of home
            at its heart fills the ring, four magic orbs orbit the event
            horizon and arcs crackle between the chevrons and the vortex.

    blender -b --factory-startup -P blender/portal.py -- --state inactive \
        [--preview --frame 0,20] [--out graphics/generated/inactive-portal]

The building is a 7x7 monument: a stepped octagonal dais with a stair at the
front (the player walks up into the vortex - control.lua wins the game when
the player stands within 3 tiles of the centre), the ring gate standing a bit
north of centre, tall pylon towers and crystal obelisks behind it.

Shared helpers live in blender/fblend.py. World units are Factorio tiles; the
entity is centred on the origin, +y is north, +z is up. The gate itself is
modelled in its own frame (see GATE below): local x = world x, local y =
world up, local +z = towards the camera (south).
"""

import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

STATE = "inactive"
if "--state" in sys.argv:
    _i = sys.argv.index("--state")
    STATE = sys.argv[_i + 1]
    del sys.argv[_i:_i + 2]
assert STATE in ("inactive", "active"), STATE
ACTIVE = STATE == "active"
BOUNDS_ONLY = "--bounds-only" in sys.argv
if BOUNDS_ONLY:
    sys.argv.remove("--bounds-only")
ENTITY = f"{STATE}-portal"

args = fblend.parse_args(ENTITY, frames=48 if ACTIVE else 64, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT
S2 = math.sqrt(2)


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------

def stone(name, base, dark, scale=14.0):
    m, nt, bsdf = node_mat(name)
    grime(nt, bsdf, base, dark, noise_scale=scale, rough=(0.55, 0.85), bump=0.5,
          bump_scale=40.0, dirt=0.35, wear=tuple(min(1.0, c * 1.6) for c in base))
    return m


def flagstones(name, base, mortar):
    """Dais paving: irregular slabs with dark joints, mottled and worn."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 2.6
    L(tc.outputs["Object"], vor.inputs["Vector"])
    vcol = nt.nodes.new("ShaderNodeTexVoronoi")       # per-slab tone
    vcol.inputs["Scale"].default_value = 2.6
    L(tc.outputs["Object"], vcol.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 16.0
    noise.inputs["Detail"].default_value = 8.0
    L(tc.outputs["Object"], noise.inputs["Vector"])
    joint = nt.nodes.new("ShaderNodeMapRange")
    joint.inputs["From Min"].default_value = 0.0
    joint.inputs["From Max"].default_value = 0.035
    L(vor.outputs["Distance"], joint.inputs["Value"])
    tone = nt.nodes.new("ShaderNodeMix")
    tone.data_type = "RGBA"
    tone.inputs["A"].default_value = (*base, 1)
    tone.inputs["B"].default_value = (*(c * 0.62 for c in base), 1)
    L(vcol.outputs["Color"], tone.inputs["Factor"])
    mott = nt.nodes.new("ShaderNodeMix")
    mott.data_type = "RGBA"
    mott.blend_type = "MULTIPLY"
    mott.inputs["Factor"].default_value = 0.45
    L(tone.outputs["Result"], mott.inputs["A"])
    L(noise.outputs["Color"], mott.inputs["B"])
    jm = nt.nodes.new("ShaderNodeMix")
    jm.data_type = "RGBA"
    jm.inputs["A"].default_value = (*mortar, 1)
    L(joint.outputs["Result"], jm.inputs["Factor"])
    L(mott.outputs["Result"], jm.inputs["B"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.3
    L(jm.outputs["Result"], ao.inputs["Color"])
    L(ao.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.75
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.6
    b.inputs["Distance"].default_value = 0.02
    L(joint.outputs["Result"], b.inputs["Height"])
    b2 = nt.nodes.new("ShaderNodeBump")
    b2.inputs["Strength"].default_value = 0.25
    b2.inputs["Distance"].default_value = 0.01
    L(noise.outputs["Fac"], b2.inputs["Height"])
    L(b.outputs["Normal"], b2.inputs["Normal"])
    L(b2.outputs["Normal"], bsdf.inputs["Normal"])
    return m


SLATE = stone("slate", (0.15, 0.12, 0.14), (0.025, 0.018, 0.024))
PAVING = flagstones("paving", (0.15, 0.115, 0.13), (0.02, 0.012, 0.016))
DARK = metal("dark_iron", (0.13, 0.11, 0.12), (0.02, 0.015, 0.02), rough=(0.3, 0.6))
ORB, ORB_EM = emitter("orb", (0.85, 0.08, 0.75), 1.0, base=(0.5, 0.03, 0.42), glass=True)
LAMP, LAMP_EM = emitter("lamp", (0.95, 0.35, 1.0), 1.5, base=(0.5, 0.1, 0.5), glass=True)
FIRE, FIRE_EM = emitter("essence_fire", (0.55, 0.35, 1.0), 6.0)
EMBER, EMBER_EM = emitter("embers", (1.0, 0.3, 0.75), 3.0, base=(0.2, 0.02, 0.1))
SPARK, _ = emitter("spark", (0.85, 0.7, 1.0), 12.0)
HORIZON, HORIZON_EM = emitter("horizon", (1.0, 0.45, 1.0), 4.0)
CRYSTAL, CRYSTAL_EM = emitter("obelisk_crystal", (0.7, 0.25, 1.0), 2.0,
                              base=(0.3, 0.08, 0.45), glass=True)
GLYPH, GLYPH_EM = emitter("glyph", (0.85, 0.3, 1.0), 0.5, base=(0.08, 0.02, 0.08))
FLOOR_RUNE, FLOOR_RUNE_EM = emitter("floor_rune", (0.8, 0.2, 1.0), 0.6,
                                    base=(0.08, 0.02, 0.08))


def chevron_mat(k):
    """Every chevron crystal has its own emission so they light one by one."""
    return emitter(f"chevron{k}", (1.0, 0.42, 0.95), 0.0, base=(0.35, 0.06, 0.25),
                   glass=True)


def vortex_material():
    """Swirling event horizon. Everything is a function of the polar angle
    through cos/sin(k * angle'), so the pattern has k-fold symmetry and one
    loop (T: 0 -> 1) turns it by exactly 1/k: the animation is seamless. The
    log-radius twist makes the arms spiral, so the turn reads as an inflow."""
    m, nt, bsdf = node_mat("vortex")
    L = nt.links.new
    node = nt.nodes.new

    def math_(op, a, b=None, clamp=False):
        n = node("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L(v, n.inputs[i])
        return n.outputs[0]

    tc = node("ShaderNodeTexCoord")
    sep = node("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], sep.inputs[0])
    x, y = sep.outputs["X"], sep.outputs["Y"]
    r = math_("DIVIDE", math_("SQRT", math_("ADD", math_("MULTIPLY", x, x),
                                             math_("MULTIPLY", y, y))), RA)
    ang = math_("ARCTAN2", y, x)
    phase = node("ShaderNodeValue")
    phase.label = "phase"
    K = 3
    TWIST = 2.4
    # angle' = angle + twist*ln(r) - TAU*T/K (arms rotate 1/K turn per loop)
    a2 = math_("ADD", ang, math_("MULTIPLY", math_("LOGARITHM", math_("ADD", r, 0.03), math.e),
                                 TWIST))
    a2 = math_("SUBTRACT", a2, math_("MULTIPLY", phase.outputs[0], TAU / K))
    ka = math_("MULTIPLY", a2, float(K))
    arms = math_("ADD", 0.5, math_("MULTIPLY", 0.5, math_("SINE", ka)))
    comb = node("ShaderNodeCombineXYZ")
    L(math_("MULTIPLY", math_("COSINE", ka), 1.2), comb.inputs["X"])
    L(math_("MULTIPLY", math_("SINE", ka), 1.2), comb.inputs["Y"])
    L(math_("MULTIPLY", r, 3.5), comb.inputs["Z"])
    nz = node("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 8.0
    nz.inputs["Roughness"].default_value = 0.6
    nz.inputs["Distortion"].default_value = 0.6
    L(comb.outputs[0], nz.inputs["Vector"])
    # finer second octave with 2K-fold symmetry (still loops after 1/K turn)
    ka2 = math_("MULTIPLY", math_("ADD", a2, math_("MULTIPLY", r, 1.5)), float(2 * K))
    comb2 = node("ShaderNodeCombineXYZ")
    L(math_("COSINE", ka2), comb2.inputs["X"])
    L(math_("SINE", ka2), comb2.inputs["Y"])
    L(math_("MULTIPLY", r, 7.0), comb2.inputs["Z"])
    nz2 = node("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 2.5
    nz2.inputs["Detail"].default_value = 6.0
    L(comb2.outputs[0], nz2.inputs["Vector"])
    v = math_("ADD", math_("MULTIPLY", arms, 0.45), math_("MULTIPLY", nz.outputs["Fac"], 0.75))
    v = math_("ADD", v, math_("MULTIPLY", nz2.outputs["Fac"], 0.35))
    v = math_("SUBTRACT", v, 0.55)
    # brighter towards the throat, a dark band then a hot rim at the edge
    centre = math_("POWER", math_("SUBTRACT", 1.0, r, clamp=True), 2.0)
    rim = math_("POWER", r, 8.0)
    v = math_("ADD", v, math_("MULTIPLY", centre, 0.8))
    v = math_("ADD", v, math_("MULTIPLY", rim, 0.5), clamp=True)
    ramp = node("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.05
    els[0].color = (0.03, 0.0, 0.06, 1)
    els[1].position = 0.95
    els[1].color = (1.0, 0.85, 1.0, 1)
    for pos, col in ((0.3, (0.22, 0.02, 0.4, 1)), (0.55, (0.6, 0.08, 0.75, 1)),
                     (0.78, (1.0, 0.4, 0.95, 1))):
        e = els.new(pos)
        e.color = col
    L(v, ramp.inputs["Fac"])
    # a glimpse of home in the throat: pale sky blue, only when open
    home = math_("POWER", math_("SUBTRACT", 1.0, math_("MULTIPLY", r, 3.2), clamp=True), 1.5)
    hm = node("ShaderNodeMix")
    hm.data_type = "RGBA"
    hm.inputs["B"].default_value = (0.55, 0.85, 1.0, 1)
    home_amt = node("ShaderNodeValue")
    home_amt.label = "home"
    L(math_("MULTIPLY", home, home_amt.outputs[0]), hm.inputs["Factor"])
    L(ramp.outputs["Color"], hm.inputs["A"])
    L(hm.outputs["Result"], bsdf.inputs["Emission Color"])
    strength = node("ShaderNodeValue")
    strength.label = "strength"
    L(math_("MULTIPLY", math_("ADD", v, 0.15), strength.outputs[0]),
      bsdf.inputs["Emission Strength"])
    bsdf.inputs["Base Color"].default_value = (0.02, 0.0, 0.03, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Coat Weight"].default_value = 0.35
    return m, phase.outputs[0], strength.outputs[0], home_amt.outputs[0]


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------

root = bpy.data.objects.new("portal", None)
link(root)


def prism(name, poly, z0, z1, mat, parent=None, bevel=0.012, top_poly=None):
    """Extrude a 2D polygon (CCW) from z0 to z1; `top_poly` (same vertex
    count) makes sloped walls. Returns the object and the side Panels."""
    top_poly = top_poly or poly
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in top_poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent or root, bevel=bevel)
    o.data.shade_flat()
    panels = [Panel((*poly[i], z0), (*poly[(i + 1) % n], z0), (*top_poly[(i + 1) % n], z1),
                    (*top_poly[i], z1)) for i in range(n)]
    return o, panels


def rail(name, pts, r, closed=False, mat=None, parent=None):
    return curve_obj(name, [tuple(p) for p in pts], mat or GOLD, r, parent or root,
                     closed=closed)


def circle_pts(r, n=96, a0=0.0, a1=TAU, z=0.0, closed=True):
    m = n if closed else n + 1
    return [(r * math.cos(a0 + (a1 - a0) * i / n), r * math.sin(a0 + (a1 - a0) * i / n), z)
            for i in range(m)]


def annulus(name, r0, r1, z0, z1, mat, parent, n=192):
    o = mesh_obj(name, ring_mesh([p[:2] for p in circle_pts(r1, n)],
                                 [p[:2] for p in circle_pts(r0, n)], z0, z1),
                 mat, parent, smooth=True, bevel=0.012, segs=2)
    return o


def lyre(cu=0.5, cv=0.5, w=1.0, h=1.0):
    """Symmetric double-scroll motif (as on the conjuration machine)."""
    S = []
    big = scroll_c(0, 0, 1, up=True)
    small = scroll_c(0, 0, 1, up=False)
    for m in (False, True):
        sg = 1 if m else -1
        S.append(fit(big, cu + sg * 0.03 * w, cv - 0.45 * h, cu + sg * 0.4 * w, cv + 0.45 * h))
        S.append(fit(small, cu + sg * 0.28 * w, cv - 0.4 * h, cu + sg * 0.48 * w, cv + 0.05 * h))
    S.append([(cu, cv - 0.45 * h), (cu, cv + 0.1 * h)])
    S.append(bezier2((cu - 0.12 * w, cv + 0.32 * h), (cu, cv + 0.02 * h),
                     (cu + 0.12 * w, cv + 0.32 * h)))
    return S


FIL_R = 0.04          # raised scrollwork thickness


def decorate(p, name, seg_len=0.85, fil_r=FIL_R, gems=True, frame_r=0.034, motif=None):
    """Split a wall panel into framed bays filled with scrollwork + studs."""
    length = (p.c[1] - p.c[0]).length
    n = max(1, round(length / seg_len))
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        sp = sub_panel(p, u0 + 0.012 / max(length, 0.1), u1 - 0.012 / max(length, 0.1),
                       0.1, 0.9)
        gold_frame(sp, f"{name}{k}_frame", frame_r, parent=root)
        inner = sub_panel(sp, 0.07, 0.93, 0.1, 0.9)
        kind = motif(k, n) if motif else ("lyre" if (k % 2 == (n // 2) % 2) else "scroll")
        if kind == "lyre":
            inner.filigree(f"{name}{k}_fil", lyre(), radius=fil_r, parent=root)
            if gems:
                inner.studs(f"{name}{k}_gem", [(0.5, 0.82)], r=0.035, mat=RUBY, parent=root)
        else:
            mirror = k % 2 == 1
            big = scroll_c(0, 0, 1, up=True)
            small = scroll_c(0, 0, 1, up=False)
            inner.filigree(f"{name}{k}_fil", [
                fit(big, 0.12, 0.0, 0.98, 1.0, flip_x=mirror),
                fit(small, 0.0 if not mirror else 0.6, 0.05, 0.4 if not mirror else 1.0, 0.55,
                    flip_x=not mirror)], radius=fil_r * 0.9, parent=root)
            inner.studs(f"{name}{k}_dot", [(0.85 if not mirror else 0.15, 0.85)], r=0.022,
                        parent=root)


def bolt_row(name, a, b, z, n, r=0.026, nrm=(0, -1, 0), mat=None):
    a, b = Vector(a), Vector(b)
    for k in range(n):
        p = a.lerp(b, (k + 0.5) / n) + Vector(nrm) * 0.005
        sphere(f"{name}{k}", r, (p.x, p.y, z), mat or GOLD, root, segs=10)


# ----------------------------------------------------------------------------
# The dais: two stepped octagonal tiers with a stair cut into the front
# ----------------------------------------------------------------------------

STAIR_W = 0.9                     # half width of the stair
STAIR_Y = -2.55                   # where the stair reaches the dais top
DAIS_Z = 0.62
T1_Z = 0.32


def oct_notched(h, ch, notch=True):
    pts = [(-h + ch, -h)]
    if notch:
        pts += [(-STAIR_W, -h), (-STAIR_W, STAIR_Y), (STAIR_W, STAIR_Y), (STAIR_W, -h)]
    pts += [(h - ch, -h), (h, -h + ch), (h, h - ch), (h - ch, h), (-h + ch, h), (-h, h - ch),
            (-h, -h + ch)]
    return pts


def oct_notched_top(h, ch, inset):
    """Top outline of a sloped tier: the outer edges move in by `inset`, the
    stair notch keeps its x."""
    hi = h - inset
    return [(-hi + ch, -hi), (-STAIR_W, -hi), (-STAIR_W, STAIR_Y), (STAIR_W, STAIR_Y),
            (STAIR_W, -hi), (hi - ch, -hi), (hi, -hi + ch), (hi, hi - ch), (hi - ch, hi),
            (-hi + ch, hi), (-hi, hi - ch), (-hi, -hi + ch)]


T1_H, T2_H = 3.47, 3.13
_, t1p = prism("tier1", oct_notched(T1_H, 0.95), 0.0, T1_Z, SLATE,
               top_poly=oct_notched_top(T1_H, 0.95, 0.12))
_, t2p = prism("tier2", oct_notched(T2_H, 0.82), T1_Z, DAIS_Z, PURPLE,
               top_poly=oct_notched_top(T2_H, 0.82, 0.1))
T2_TOP = oct_notched_top(T2_H, 0.82, 0.1)
# paving on the dais top
bm = bmesh.new()
vs = [bm.verts.new((x, y, DAIS_Z + 0.002)) for x, y in T2_TOP]
bm.faces.new(vs)
mesh_obj("dais_floor", bm, PAVING, root)
# heavy gold rails along the tier edges, rivets on the slate tier
rail("t1_top_rail", [(x, y, T1_Z + 0.01) for x, y in oct_notched_top(T1_H, 0.95, 0.12)], 0.05,
     closed=True)
rail("t1_foot", [(x * 1.004, y * 1.004, 0.03) for x, y in oct_notched(T1_H, 0.95)], 0.035,
     closed=True)
rail("t2_top_rail", [(x, y, DAIS_Z + 0.01) for x, y in T2_TOP], 0.065, closed=True)
rail("t2_foot", [(x, y, T1_Z + 0.025) for x, y in oct_notched(T2_H, 0.82)], 0.04, closed=True)
# visible faces: front pieces (1 and 5 are the outer front runs), chamfers, sides
for name, panels in (("t2", t2p),):
    for i, p in enumerate(panels):
        nrm = p.n
        if nrm.y > 0.5:            # back faces never show
            continue
        L_ = (p.c[1] - p.c[0]).length
        if L_ < 0.5:
            continue
        decorate(p, f"{name}_{i}_", seg_len=0.62, fil_r=0.032, frame_r=0.028)
for i, p in enumerate(t1p):        # slate tier: rivet rows and gold straps
    if p.n.y > 0.5 or (p.c[1] - p.c[0]).length < 0.5:
        continue
    a, b = p.at(0, 0.5, 0.0), p.at(1, 0.5, 0.0)
    n = max(2, int((Vector(b) - Vector(a)).length / 0.3))
    for k in range(n):
        q = p.at((k + 0.5) / n, 0.5, 0.012)
        sphere(f"t1_rivet{i}_{k}", 0.03, q, GOLD if k % 3 else RUBY, root, segs=10)

# stair: three slate steps with gold nosings, balustrade with lamps on top
STEP_D = (STAIR_Y + T1_H) / 3
for k in range(3):
    y0 = -T1_H + STEP_D * k
    top = DAIS_Z * (k + 1) / 3
    box(f"step{k}", (2 * STAIR_W, STAIR_Y - y0, top), (0, (y0 + STAIR_Y) / 2, top / 2), SLATE,
        bevel=0.015)
    rail(f"step{k}_nose", [(-STAIR_W, y0 + 0.02, top), (STAIR_W, y0 + 0.02, top)], 0.035)
    # purple runner carpet up the middle
    box(f"step{k}_runner", (0.9, STEP_D + 0.002, 0.012),
        (0, y0 + STEP_D / 2 + 0.01, top + 0.004), PURPLE, bevel=0.003)
box("runner_top", (0.9, 0.5, 0.012), (0, STAIR_Y + 0.25, DAIS_Z + 0.006), PURPLE, bevel=0.003)
for sx in (-1, 1):
    x = sx * (STAIR_W + 0.09)
    box(f"stair_cheek{sx}", (0.18, STAIR_Y + T1_H, 0.2), (x, (STAIR_Y - T1_H) / 2, DAIS_Z + 0.02),
        PURPLE, bevel=0.02)
    rail(f"balustrade{sx}", [(x, -T1_H + 0.08, 0.5), (x, STAIR_Y - 0.15, DAIS_Z + 0.42),
                             (x, STAIR_Y + 0.15, DAIS_Z + 0.42)], 0.045)
    for k, y in enumerate((-T1_H + 0.1, (STAIR_Y - T1_H) / 2)):
        cyl(f"baluster{sx}{k}", 0.035, 0.3, (x, y, DAIS_Z + 0.08 + 0.1 * k), BRASS)
    # lamp posts at the stair head
    post = Vector((sx * (STAIR_W + 0.12), STAIR_Y + 0.15, DAIS_Z))
    cyl(f"lamp_base{sx}", 0.15, 0.12, post + Vector((0, 0, 0.06)), GOLD, verts=8)
    cyl(f"lamp_post{sx}", 0.06, 0.9, post + Vector((0, 0, 0.55)), BRASS, verts=16)
    for zz in (0.3, 0.7):
        cyl(f"lamp_band{sx}{zz}", 0.075, 0.04, post + Vector((0, 0, zz)), GOLD, verts=16)
    cyl(f"lamp_cup{sx}", 0.11, 0.08, post + Vector((0, 0, 1.0)), GOLD, verts=16, r2=0.14)
    glow(sphere(f"lamp_orb{sx}", 0.1, post + Vector((0, 0, 1.13)), LAMP, root, segs=20))
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        rail(f"lamp_claw{sx}{k}", [post + Vector((0.12 * math.cos(a), 0.12 * math.sin(a), 1.04)),
                                   post + Vector((0.11 * math.cos(a), 0.11 * math.sin(a), 1.2)),
                                   post + Vector((0.05 * math.cos(a), 0.05 * math.sin(a), 1.25))],
             0.014)

# summoning circle inlaid in the floor in front of the gate
CIRC = Vector((0, -1.32, DAIS_Z + 0.004))
for rr, w in ((0.95, 0.04), (0.76, 0.03), (0.3, 0.03)):
    rail(f"circle{rr}", [CIRC + Vector(p) for p in circle_pts(rr, 96)], w, closed=True)
for k in range(12):
    a = TAU * k / 12 + math.pi / 2
    cell = Panel(CIRC + Vector((0.8 * math.cos(a - 0.2), 0.8 * math.sin(a - 0.2), 0)),
                 CIRC + Vector((0.8 * math.cos(a + 0.2), 0.8 * math.sin(a + 0.2), 0)),
                 CIRC + Vector((0.98 * math.cos(a + 0.17), 0.98 * math.sin(a + 0.17), 0)),
                 CIRC + Vector((0.98 * math.cos(a - 0.17), 0.98 * math.sin(a - 0.17), 0)))
    for gi, stroke in enumerate(RUNES[k % len(RUNES)]):
        glow(curve_obj(f"floor_rune{k}_{gi}", [cell.at(0.2 + 0.6 * u, 0.15 + 0.7 * v, 0.004)
                                               for u, v in stroke], FLOOR_RUNE, 0.016, root))
for k in range(6):   # hexagram between the inner rings
    a0, a1 = TAU * k / 6 + math.pi / 2, TAU * (k + 2) / 6 + math.pi / 2
    rail(f"hexagram{k}", [CIRC + Vector((0.76 * math.cos(a0), 0.76 * math.sin(a0), 0)),
                          CIRC + Vector((0.76 * math.cos(a1), 0.76 * math.sin(a1), 0))], 0.022)
glow(cyl("circle_heart", 0.3, 0.01, CIRC, FLOOR_RUNE, verts=48))


# ----------------------------------------------------------------------------
# The gate
# ----------------------------------------------------------------------------
#
# A fixed purple stator ring frames the aperture and carries eight chevron
# crystals. Around it runs the rotor: a dark bronze ring with forty rune
# glyphs on its face and forty teeth on its rim. Two pinions high on its
# flanks turn it; each sits on a shaft with a big gear meshing a crank gear,
# whose crank is worked by an inverted steam cylinder below it (steam from the
# essence-fired boilers at the front corners). The master chevron on top
# clamps down on the rotor to lock each glyph.

YG = 0.3                      # gate plane (world y)
ZC = 2.35                     # ring centre height
RA = 1.85                     # aperture radius
RS = 2.25                     # stator outer radius
ROT_T = 40
ROT_R = 2.66                  # rotor pitch radius (module 0.133)
TOOTH_H = 0.09                # half the tooth height (all gears share the module)
GLYPHS = 40

GATE = bpy.data.objects.new("gate", None)
link(GATE, root)
GATE.location = (0, YG, ZC)
GATE.rotation_euler = (math.radians(90), 0, 0)   # local y -> up, local z -> south


def pol(r, a, z=0.0):
    return (r * math.cos(a), r * math.sin(a), z)


def to_world(p):
    return GATE.matrix_world @ Vector(p)


bpy.context.view_layer.update()

# --- stator ------------------------------------------------------------------
annulus("stator", RA, RS, -0.28, 0.28, PURPLE, GATE)
for rr, w, z in ((RA + 0.04, 0.075, 0.28), (RS - 0.035, 0.07, 0.28), (RA + 0.04, 0.06, -0.28)):
    curve_obj(f"stator_rim{rr}{z}", circle_pts(rr, 160, z=z), GOLD, w, GATE, closed=True)
# aperture lining: gold-ribbed bronze sleeve (its lower half faces the camera)
mesh_obj("aperture_sleeve", ring_mesh([p[:2] for p in circle_pts(RA + 0.01, 160)],
                                       [p[:2] for p in circle_pts(RA - 0.03, 160)], -0.27, 0.27),
         BRONZE, GATE, smooth=True)
for k in range(36):
    a = TAU * k / 36
    box(f"sleeve_rib{k}", (0.05, 0.035, 0.5), pol(RA - 0.03, a), GOLD, GATE, rot=(0, 0, a),
        bevel=0.008)

CHEV_A = [math.radians(d) for d in (56.25, 22.5, -11.25, -45.0, 123.75, 157.5, 191.25, 225.0)]
MASTER_A = math.pi / 2
# lighting order: right side bottom-up from the top, then the left side
CHEV_EM = []
CHEV_LIGHTS = []


def polar_panel(a0, a1, r0, r1, z):
    """Panel on the ring face: u along the angle, v radially outwards."""
    return Panel(pol(r0, a0, z), pol(r0, a1, z), pol(r1, a1, z), pol(r1, a0, z))


def chevron(k, a):
    mat, em = chevron_mat(k)
    CHEV_EM.append(em)
    hold = bpy.data.objects.new(f"chev{k}", None)
    link(hold, GATE)
    hold.rotation_euler = (0, 0, a - math.pi / 2)      # local +y points outwards
    # housing: gold trapezoid straddling the stator, overhanging the rotor
    poly = [(-0.24, RA - 0.02), (0.24, RA - 0.02), (0.17, RS + 0.16), (-0.17, RS + 0.16)]
    o = mesh_obj(f"chev{k}_house", ring_mesh_poly(poly, 0.26, 0.42), GOLD, hold, bevel=0.012)
    o.data.shade_flat()
    # V-shaped crystal pointing inwards
    vpoly = [(-0.15, 2.22), (0.0, 1.98), (0.15, 2.22), (0.15, 2.32), (0.0, 2.1), (-0.15, 2.32)]
    o = mesh_obj(f"chev{k}_crystal", ring_mesh_poly(vpoly, 0.42, 0.47), mat, hold, bevel=0.006)
    o.data.shade_flat()
    glow(o)
    sphere(f"chev{k}_ruby", 0.04, (0, RS + 0.07, 0.44), RUBY, hold)
    for sx in (-1, 1):
        sphere(f"chev{k}_bolt{sx}", 0.025, (sx * 0.17, RA + 0.06, 0.43), GOLD, hold, segs=10)
    return hold


def ring_mesh_poly(poly, z0, z1):
    """Prism of a convex-or-not 2D polygon between z0 and z1."""
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


for k, a in enumerate(CHEV_A):
    chevron(k, a)
# scrollwork on the stator face between the chevrons
_all = sorted(CHEV_A + [MASTER_A, math.radians(270)])
for k, a0 in enumerate(_all):
    a1 = _all[(k + 1) % len(_all)] + (TAU if k == len(_all) - 1 else 0)
    if a1 - a0 < 0.2:
        continue
    ga0, ga1 = a0 + 0.13, a1 - 0.13
    pp = polar_panel(ga0, ga1, RA + 0.1, RS - 0.08, 0.29)
    pp_strokes = [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.5, 1.0),
                  fit(scroll_c(0, 0, 1), 0.5, 0.0, 1.0, 1.0, flip_x=True)]
    for si, st in enumerate(pp_strokes):
        curve_obj(f"stator_fil{k}_{si}", [pol(RA + 0.1 + v * (RS - RA - 0.18),
                                              ga1 - u * (ga1 - ga0), 0.3) for u, v in st],
                  GOLD, 0.03, GATE)
    am = (a0 + a1) / 2
    sphere(f"stator_gem{k}", 0.04, pol((RA + RS) / 2, am, 0.31), RUBY, GATE)

# --- rotor (dial) ------------------------------------------------------------
ROTOR = bpy.data.objects.new("rotor", None)
link(ROTOR, GATE)
outer, inner = [], []
for k in range(ROT_T):
    a, da = TAU * k / ROT_T, TAU / ROT_T
    for frac, rad in ((0.0, ROT_R - TOOTH_H), (0.18, ROT_R + TOOTH_H), (0.5, ROT_R + TOOTH_H),
                      (0.68, ROT_R - TOOTH_H)):
        outer.append((rad * math.cos(a + frac * da), rad * math.sin(a + frac * da)))
        inner.append(((RS + 0.01) * math.cos(a + frac * da), (RS + 0.01) * math.sin(a + frac * da)))
inner = [(x * (ROT_R - TOOTH_H - 0.12) / (RS + 0.01), y * (ROT_R - TOOTH_H - 0.12) / (RS + 0.01))
         for x, y in inner]
o = mesh_obj("rotor_teeth", ring_mesh(outer, inner, -0.08, 0.08), STEEL, ROTOR, bevel=0.008)
o.data.shade_flat()
annulus("rotor_body", RS + 0.01, ROT_R - TOOTH_H - 0.02, -0.18, 0.18, BRONZE, ROTOR)
for rr, w in ((RS + 0.04, 0.04), (ROT_R - TOOTH_H - 0.04, 0.045)):
    curve_obj(f"rotor_rim{rr}", circle_pts(rr, 160, z=0.19), GOLD, w, ROTOR, closed=True)
GCELL = TAU / GLYPHS
for k in range(GLYPHS):
    ac = GCELL * (k + 0.5)
    box(f"rotor_sep{k}", (ROT_R - TOOTH_H - RS - 0.1, 0.035, 0.03),
        pol((RS + ROT_R - TOOTH_H) / 2, GCELL * k, 0.2), GOLD, ROTOR, rot=(0, 0, GCELL * k),
        bevel=0.006)
    r0, r1 = RS + 0.08, ROT_R - TOOTH_H - 0.08
    for gi, stroke in enumerate(RUNES[k % len(RUNES)]):
        pts = [pol(r0 + (r1 - r0) * (0.1 + 0.8 * v), ac + (0.5 - u) * GCELL * 0.62, 0.195)
               for u, v in stroke]
        glow(curve_obj(f"glyph{k}_{gi}", pts, GLYPH, 0.016, ROTOR))
# back face of the rotor gets a plain gold rim so its silhouette reads
curve_obj("rotor_back_rim", circle_pts(ROT_R - TOOTH_H - 0.04, 160, z=-0.19), GOLD, 0.04,
          ROTOR, closed=True)

# --- master chevron: bridge over the rotor at the top, sliding claw ----------
MCH = bpy.data.objects.new("master", None)
link(MCH, GATE)
MCH.rotation_euler = (0, 0, 0)            # local y is outwards at the top
crest_poly = [(-0.5, ROT_R + 0.12), (0.5, ROT_R + 0.12), (0.4, ROT_R + 0.5),
              (0.0, ROT_R + 0.86), (-0.4, ROT_R + 0.5)]
o = mesh_obj("master_crest", ring_mesh_poly(crest_poly, -0.22, 0.3), GOLD, MCH, bevel=0.02)
o.data.shade_flat()
inset = [(x * 0.78, ROT_R + 0.12 + (y - ROT_R - 0.12) * 0.82 + 0.06) for x, y in crest_poly]
o = mesh_obj("master_crest_inset", ring_mesh_poly(inset, 0.3, 0.33), PURPLE, MCH, bevel=0.006)
o.data.shade_flat()
curve_obj("master_crest_rim", [(x, y, 0.32) for x, y in crest_poly], GOLD, 0.05, MCH,
          closed=True)
for sx in (-1, 1):                         # bridge cheeks down to the stator
    o = mesh_obj(f"master_cheek{sx}", ring_mesh_poly(
        [(sx * 0.24, RS - 0.05), (sx * 0.42, RS - 0.05), (sx * 0.48, ROT_R + 0.2),
         (sx * 0.3, ROT_R + 0.2)], 0.2, 0.44), GOLD, MCH, bevel=0.012)
    o.data.shade_flat()
    sphere(f"master_cheek_ruby{sx}", 0.045, (sx * 0.36, RS + 0.2, 0.46), RUBY, MCH)
    curve_obj(f"master_curl{sx}", [(sx * x, y, 0.38) for x, y in
                                   fit(scroll_c(0, 0, 1), 0.48, ROT_R + 0.2, 0.9, ROT_R + 0.65,
                                       flip_x=True)], GOLD, 0.045, MCH)
sphere("master_jewel", 0.1, (0, ROT_R + 0.52, 0.38), RUBY, MCH, segs=20)
fil = Panel((-0.3, ROT_R + 0.2, 0.37), (0.3, ROT_R + 0.2, 0.37), (0.3, ROT_R + 0.42, 0.37),
            (-0.3, ROT_R + 0.42, 0.37))
fil.filigree("master_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.48, 1.0),
                            fit(scroll_c(0, 0, 1), 0.52, 0.0, 1.0, 1.0, flip_x=True)],
             radius=0.028, lift=0.0, parent=MCH)
CLAW = bpy.data.objects.new("master_claw", None)
link(CLAW, MCH)
CLAW_UP, CLAW_DOWN = 0.28, 0.0      # radial travel (down = on the glyph)
MASTER_MAT, MASTER_EM = chevron_mat(99)
o = mesh_obj("claw_body", ring_mesh_poly([(-0.2, RS + 0.2), (0.0, RS + 0.04), (0.2, RS + 0.2),
                                          (0.2, ROT_R + 0.2), (-0.2, ROT_R + 0.2)], 0.21, 0.31),
             GOLD, CLAW, bevel=0.012)
o.data.shade_flat()
o = mesh_obj("claw_crystal", ring_mesh_poly([(-0.13, RS + 0.3), (0.0, RS + 0.14), (0.13, RS + 0.3),
                                             (0.13, RS + 0.38), (0.0, RS + 0.22),
                                             (-0.13, RS + 0.38)], 0.31, 0.36),
             MASTER_MAT, CLAW, bevel=0.005)
glow(o)
cyl("claw_rod", 0.04, 0.5, (0, ROT_R + 0.35, 0.26), STEEL, CLAW, rot=(math.radians(90), 0, 0))

# --- drive trains on both flanks ------------------------------------------------
P_T, Q_T, D_T = 8, 16, 8
P_R = ROT_R * P_T / ROT_T              # 0.532, same module as the rotor
Q_R, D_R = 0.5, 0.25                   # second module 0.0625
Q_Z, CRANK_Z = 0.45, 0.62              # gear plane and crank/rod plane (local z)
CRANK_R, ROD_L = 0.17, 0.78
TRAIN_A = math.radians(35)
TRAIN_D = math.radians(-70)            # Q -> D direction (right side)
CYL_Y0, CYL_Y1 = -0.72, -0.02          # steam cylinder (local y), below the crank
GUIDE_Y1 = 0.62


def mesh_phase(alpha, th_a, n_a, n_b):
    """Rotation of gear B (n_b teeth) that meshes, at world angle alpha seen
    from A's centre, with gear A (n_a teeth) turned to th_a: A's tooth offset
    from the contact line plus B's gap offset must sum to whole teeth."""
    s_a = (alpha - th_a) * n_a / TAU - TOOTH_C
    return alpha + math.pi - TAU * (GAP_C - s_a) / n_b


class Train:
    pass


TRAINS = []
for side in (1, -1):
    t = Train()
    t.side = side
    a = TRAIN_A if side > 0 else math.pi - TRAIN_A
    t.alpha = a
    t.pc = Vector(pol(ROT_R + P_R, a))
    dd = TRAIN_D if side > 0 else math.pi - TRAIN_D
    t.dd = dd
    t.dc = t.pc + Vector(pol(Q_R + D_R, dd))
    sfx = "R" if side > 0 else "L"
    t.P = gear(f"pinion{sfx}", P_T, P_R, 0.16, DARK, GATE, spokes=4, inner=0.55,
               tooth=2 * TOOTH_H / P_R)
    t.P.location = t.pc
    t.Q = gear(f"gearQ{sfx}", Q_T, Q_R, 0.08, STEEL, GATE, spokes=4, inner=0.7,
               tooth=0.14 / Q_R)
    t.Q.location = (t.pc.x, t.pc.y, Q_Z)
    for k in range(4):     # rubies between the spokes, like the reference gears
        aa = TAU * (k + 0.5) / 4
        sphere(f"gearQ{sfx}_gem{k}", 0.03, (0.36 * math.cos(aa), 0.36 * math.sin(aa), 0.05),
               RUBY, t.Q)
    t.D = gear(f"gearD{sfx}", D_T, D_R, 0.08, GOLD, GATE, spokes=0, inner=0.5,
               tooth=0.14 / D_R)
    t.D.location = (t.dc.x, t.dc.y, Q_Z)
    # crank web (an arm, so the gold crank gear behind it stays visible)
    cyl(f"crank_hub{sfx}", 0.08, 0.06, (0, 0, CRANK_Z - Q_Z - 0.05), BRASS, t.D, verts=24)
    box(f"crank_web{sfx}", (CRANK_R + 0.08, 0.09, 0.04), (CRANK_R / 2, 0, CRANK_Z - Q_Z - 0.04),
        BRASS, t.D, bevel=0.012)
    cyl(f"crank_pin{sfx}", 0.035, 0.12, (CRANK_R, 0, CRANK_Z - Q_Z + 0.02), STEEL, t.D)
    box(f"crank_weight{sfx}", (0.1, 0.16, 0.05), (-0.09, 0, CRANK_Z - Q_Z - 0.04), BRASS, t.D,
        bevel=0.015)
    # shafts back into the pylon
    cyl(f"pin_shaft{sfx}", 0.06, 1.3, (t.pc.x, t.pc.y, -0.25), STEEL, GATE)
    cyl(f"pin_nut{sfx}", 0.09, 0.08, (t.pc.x, t.pc.y, Q_Z + 0.07), GOLD, GATE, verts=6)
    cyl(f"d_shaft{sfx}", 0.05, 1.1, (t.dc.x, t.dc.y, 0.0), STEEL, GATE)
    # steam cylinder hanging below the crank, crosshead guides between
    cx = t.dc.x
    t.cx = cx
    cyl(f"steam_cyl{sfx}", 0.2, CYL_Y1 - CYL_Y0, (cx, (CYL_Y0 + CYL_Y1) / 2, CRANK_Z), BRASS,
        GATE, rot=(math.radians(90), 0, 0), verts=40)
    for yy in (CYL_Y0 + 0.03, (CYL_Y0 + CYL_Y1) / 2, CYL_Y1 - 0.03):
        cyl(f"steam_cyl{sfx}_band{yy}", 0.22, 0.05, (cx, yy, CRANK_Z), GOLD, GATE,
            rot=(math.radians(90), 0, 0), verts=40)
    box(f"valve_chest{sfx}", (0.12, 0.45, 0.2), (cx + side * 0.25, (CYL_Y0 + CYL_Y1) / 2,
                                                  CRANK_Z), BRONZE, GATE, bevel=0.015)
    for gx in (-1, 1):
        box(f"guide{sfx}{gx}", (0.035, GUIDE_Y1 - CYL_Y1, 0.05),
            (cx + gx * 0.09, (GUIDE_Y1 + CYL_Y1) / 2, CRANK_Z), STEEL, GATE, bevel=0.006)
    box(f"guide_cap{sfx}", (0.26, 0.05, 0.07), (cx, GUIDE_Y1, CRANK_Z), STEEL, GATE, bevel=0.006)
    # brackets: cylinder and guides bolted back to the pylon (local -z)
    for yy in ((CYL_Y0 + CYL_Y1) / 2, GUIDE_Y1):
        box(f"bracket{sfx}{yy}", (0.14, 0.1, 1.05), (cx + side * 0.12, yy, CRANK_Z - 0.6),
            BRONZE, GATE, bevel=0.015)
    t.piston = cyl(f"piston{sfx}", 0.03, 1.0, (cx, 0, CRANK_Z), STEEL, GATE,
                   rot=(math.radians(90), 0, 0))
    t.cross = box(f"crosshead{sfx}", (0.13, 0.1, 0.09), (cx, 0, CRANK_Z), BRASS, GATE,
                  bevel=0.012)
    TRAINS.append(t)


ROT0 = 0.0


# ----------------------------------------------------------------------------
# Pylons, cradle, obelisks, boilers
# ----------------------------------------------------------------------------

PY_X0, PY_X1 = 2.62, 3.42
PY_Y0, PY_Y1 = YG + 0.32, YG + 0.98
PY_Z1 = 4.75
for sx in (-1, 1):
    xi, xo = sx * PY_X0, sx * PY_X1
    xo_top = sx * (PY_X1 - 0.3)
    bot = [(xi, PY_Y0), (xo, PY_Y0), (xo, PY_Y1), (xi, PY_Y1)]
    top = [(xi, PY_Y0 + 0.05), (xo_top, PY_Y0 + 0.05), (xo_top, PY_Y1 - 0.05),
           (xi, PY_Y1 - 0.05)]
    if sx < 0:
        bot = [bot[1], bot[0], bot[3], bot[2]]
        top = [top[1], top[0], top[3], top[2]]
    _, pp = prism(f"pylon{sx}", bot, DAIS_Z, PY_Z1, PURPLE, top_poly=top)
    for i, p in enumerate(pp):
        if p.n.y > 0.5:
            continue
        if abs(p.n.y) > 0.5:      # front face: tall framed bays
            for k, (v0, v1) in enumerate(((0.02, 0.36), (0.36, 0.7), (0.7, 0.98))):
                sp = sub_panel(p, 0.06, 0.94, v0 + 0.01, v1 - 0.01)
                gold_frame(sp, f"pylon{sx}_{i}_{k}_frame", 0.032, parent=root)
                inner = sub_panel(sp, 0.1, 0.9, 0.06, 0.94)
                inner.filigree(f"pylon{sx}_{i}_{k}_fil", lyre(), radius=0.034, parent=root)
                inner.studs(f"pylon{sx}_{i}_{k}_gem", [(0.5, 0.85)], r=0.035, mat=RUBY,
                            parent=root)
        elif p.n.x * sx > 0.3:    # sloped outer wing
            decorate(p, f"pylon{sx}_wing", seg_len=1.0, fil_r=0.034)
    for c in range(4):
        rail(f"pylon{sx}_rib{c}", [(*bot[c], DAIS_Z + 0.02), (*top[c], PY_Z1)], 0.06)
    # cap: stepped gold cornice, dome and an orb finial
    cxm = sx * (PY_X0 + PY_X1 - 0.3) / 2
    cym = (PY_Y0 + PY_Y1) / 2
    box(f"pylon{sx}_cornice", (abs(xo_top - xi) + 0.16, PY_Y1 - PY_Y0 + 0.06, 0.12),
        (cxm, cym, PY_Z1 + 0.06), GOLD, bevel=0.03)
    cyl(f"pylon{sx}_dome", 0.3, 0.32, (cxm, cym, PY_Z1 + 0.28), PURPLE, r2=0.08, verts=24)
    cyl(f"pylon{sx}_neck", 0.08, 0.18, (cxm, cym, PY_Z1 + 0.5), GOLD, verts=16)
    glow(sphere(f"pylon{sx}_orb", 0.13, (cxm, cym, PY_Z1 + 0.68), LAMP, root, segs=20))
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        rail(f"pylon{sx}_claw{k}", [(cxm + 0.08 * math.cos(a), cym + 0.08 * math.sin(a), PY_Z1 + 0.56),
                                    (cxm + 0.15 * math.cos(a), cym + 0.15 * math.sin(a), PY_Z1 + 0.68),
                                    (cxm + 0.06 * math.cos(a), cym + 0.06 * math.sin(a), PY_Z1 + 0.82)],
             0.018)

# cradle: the ring sits in a massive saddle on the dais
CR_X, CR_Z = 2.35, DAIS_Z + 0.42
cr_bot = [(-CR_X, YG - 0.55), (CR_X, YG - 0.55), (CR_X, YG + 0.5), (-CR_X, YG + 0.5)]
cr_top = [(-CR_X + 0.15, YG - 0.4), (CR_X - 0.15, YG - 0.4), (CR_X - 0.15, YG + 0.4),
          (-CR_X + 0.15, YG + 0.4)]
_, crp = prism("cradle", cr_bot, DAIS_Z, CR_Z, PURPLE, top_poly=cr_top)
decorate(crp[0], "cradle_front", seg_len=0.9, fil_r=0.034)
rail("cradle_rail", [(x, y, CR_Z + 0.01) for x, y in cr_top], 0.06, closed=True)
for k, p in enumerate((crp[1], crp[3])):
    decorate(p, f"cradle_side{k}", seg_len=1.0, fil_r=0.03)
# threshold step in the aperture: gold-edged, where the player walks through
box("threshold", (2 * RA - 0.6, 0.9, 0.06), (0, YG, CR_Z + 0.03), SLATE, bevel=0.015)
rail("threshold_edge", [(-RA + 0.3, YG - 0.45, CR_Z + 0.06), (RA - 0.3, YG - 0.45, CR_Z + 0.06)],
     0.04)

# crystal obelisks at the back corners: they store the essence for the dial
OB = 2.38
for sx in (-1, 1):
    base = Vector((sx * OB, OB, DAIS_Z))
    box(f"ob{sx}_plinth", (0.62, 0.62, 0.28), base + Vector((0, 0, 0.14)), SLATE, bevel=0.03)
    rail(f"ob{sx}_plinth_rail", [base + Vector((x, y, 0.28)) for x, y in
                                 ((-0.31, -0.31), (0.31, -0.31), (0.31, 0.31), (-0.31, 0.31))],
         0.04, closed=True)
    _, op = prism(f"ob{sx}_shaft", [(base.x + x, base.y + y) for x, y in
                                    ((-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22))],
                  DAIS_Z + 0.28, DAIS_Z + 2.4, PURPLE,
                  top_poly=[(base.x + x, base.y + y) for x, y in
                            ((-0.14, -0.14), (0.14, -0.14), (0.14, 0.14), (-0.14, 0.14))])
    for c, (x, y) in enumerate(((-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22))):
        rail(f"ob{sx}_edge{c}", [base + Vector((x, y, 0.3)),
                                 base + Vector((x * 0.64, y * 0.64, 2.4))], 0.035)
    rune(sub_panel(op[0], 0.15, 0.85, 0.15, 0.55), f"ob{sx}_rune", sx + 1, radius=0.02,
         parent=root)
    cyl(f"ob{sx}_collar", 0.2, 0.1, base + Vector((0, 0, 2.42)), GOLD, verts=8)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.16, radius2=0.0, depth=0.55)
    o = mesh_obj(f"ob{sx}_crystal", bm, CRYSTAL, root)
    o.location = base + Vector((0, 0, 2.74))
    o.data.shade_flat()
    glow(o)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.16, radius2=0.0, depth=0.22)
    o = mesh_obj(f"ob{sx}_crystal_b", bm, CRYSTAL, root)
    o.location = base + Vector((0, 0, 2.36))
    o.rotation_euler = (math.pi, 0, 0)
    o.data.shade_flat()
    glow(o)
    # essence conduit from the obelisk to the pylon
    rail(f"ob{sx}_conduit", [base + Vector((-sx * 0.22, -0.1, 0.9)),
                             Vector((sx * 2.95, PY_Y1 + 0.02, DAIS_Z + 0.9))], 0.05, mat=BRASS)

# boilers at the front corners: essence fireboxes with copper drums
BOILERS = []
FLAMES = []
for sx in (-1, 1):
    bc = Vector((sx * 2.32, -1.85, DAIS_Z))
    fb = [(bc.x - 0.42, bc.y - 0.36), (bc.x + 0.42, bc.y - 0.36), (bc.x + 0.42, bc.y + 0.36),
          (bc.x - 0.42, bc.y + 0.36)]
    fbt = [(bc.x - 0.36, bc.y - 0.3), (bc.x + 0.36, bc.y - 0.3), (bc.x + 0.36, bc.y + 0.3),
           (bc.x - 0.36, bc.y + 0.3)]
    _, bp = prism(f"firebox{sx}", fb, DAIS_Z, DAIS_Z + 0.55, DARK, top_poly=fbt)
    front = bp[0]
    # fire door opening: glowing grate with essence flames behind bars
    door = sub_panel(front, 0.2, 0.8, 0.12, 0.72)
    gold_frame(door, f"firebox{sx}_door", 0.035, parent=root)
    glow(door.build(f"firebox{sx}_embers", EMBER, thick=0.005, parent=root))
    for k in range(5):
        u = 0.12 + 0.76 * k / 4
        rail(f"firebox{sx}_bar{k}", [door.at(u, 0.0, 0.03), door.at(u, 1.0, 0.03)], 0.018,
             mat=STEEL)
    for k in range(3):
        fl = bpy.data.objects.new(f"flame{sx}{k}", None)
        link(fl, root)
        fl.location = door.at(0.25 + 0.25 * k, 0.05, -0.04)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.07, radius2=0.0,
                              depth=0.3)
        o = mesh_obj(f"flame{sx}{k}_m", bm, FIRE, fl, smooth=True)
        o.location = (0, 0, 0.15)
        glow(o)
        FLAMES.append((fl, k + (0 if sx > 0 else 3)))
    gold_frame(sub_panel(front, 0.03, 0.97, 0.04, 0.96), f"firebox{sx}_frame", 0.03, parent=root)
    bolt_row(f"firebox{sx}_bolts", front.at(0.05, 0.9, 0.0), front.at(0.95, 0.9, 0.0),
             front.at(0, 0.9)[2], 6)
    # copper drum lying north-south on top
    drum_z = DAIS_Z + 0.55 + 0.26
    cyl(f"drum{sx}", 0.27, 0.86, (bc.x, bc.y, drum_z), COPPER, rot=(math.radians(90), 0, 0),
        verts=40)
    for yy in (-0.36, 0.0, 0.36):
        cyl(f"drum{sx}_band{yy}", 0.285, 0.05, (bc.x, bc.y + yy, drum_z), GOLD,
            rot=(math.radians(90), 0, 0), verts=40)
    cyl(f"drum{sx}_cap", 0.2, 0.06, (bc.x, bc.y - 0.44, drum_z), BRASS,
        rot=(math.radians(90), 0, 0), verts=32)
    sphere(f"drum{sx}_cap_gem", 0.05, (bc.x, bc.y - 0.48, drum_z), RUBY)
    cyl(f"dome{sx}", 0.11, 0.18, (bc.x, bc.y + 0.12, drum_z + 0.3), BRASS, verts=24)
    sphere(f"dome{sx}_top", 0.11, (bc.x, bc.y + 0.12, drum_z + 0.39), GOLD, segs=16)
    for yy in (-0.3, 0.3):
        box(f"drum{sx}_saddle{yy}", (0.5, 0.08, 0.14), (bc.x, bc.y + yy, DAIS_Z + 0.58), BRONZE,
            bevel=0.01)
    # chimney stack at the back of the firebox
    cyl(f"stack{sx}", 0.08, 0.7, (bc.x - sx * 0.25, bc.y + 0.25, DAIS_Z + 0.9), DARK, verts=20)
    cyl(f"stack{sx}_crown", 0.11, 0.08, (bc.x - sx * 0.25, bc.y + 0.25, DAIS_Z + 1.26), GOLD,
        verts=20, r2=0.13)
    BOILERS.append(bc)

# fuel: crates of divination essence vials next to each boiler (the burner's
# fuel), and gold inlay lines tying the summoning circle to the dais corners
ESSENCE, ESSENCE_EM = emitter("essence", (0.45, 0.55, 1.0), 2.0, base=(0.2, 0.25, 0.6),
                              glass=True)
for sx in (-1, 1):
    cc = Vector((sx * 1.5, -2.0, DAIS_Z))
    box(f"crate{sx}", (0.5, 0.42, 0.3), cc + Vector((0, 0, 0.15)), BRONZE, bevel=0.02)
    for yy in (-0.211, 0.211):
        rail(f"crate{sx}_band{yy}", [cc + Vector((-0.25, yy, 0.02)), cc + Vector((-0.25, yy, 0.3)),
                                     cc + Vector((0.25, yy, 0.3)), cc + Vector((0.25, yy, 0.02))],
             0.02)
    for xx in (-0.16, 0.16):
        rail(f"crate{sx}_strap{xx}", [cc + Vector((xx, -0.215, 0.02)),
                                      cc + Vector((xx, -0.215, 0.3))], 0.022)
    sphere(f"crate{sx}_lock", 0.03, cc + Vector((0, -0.215, 0.22)), RUBY)
    for k in range(6):
        vx, vy = -0.15 + 0.15 * (k % 3), -0.08 + 0.16 * (k // 3)
        vp = cc + Vector((vx, vy, 0.3))
        cyl(f"vial{sx}{k}", 0.05, 0.16, vp + Vector((0, 0, 0.08)), GLASS, verts=16)
        glow(cyl(f"vial{sx}{k}_liq", 0.042, 0.12, vp + Vector((0, 0, 0.065)), ESSENCE,
                 verts=16))
        cyl(f"vial{sx}{k}_cork", 0.03, 0.04, vp + Vector((0, 0, 0.18)), BRASS, verts=12)
    # feed line from each boiler along the floor into the cradle: it carries
    # the essence vapour that feeds the ring
    pts = [(sx * 2.32, -1.42, DAIS_Z + 0.08), (sx * 2.32, -0.75, DAIS_Z + 0.08),
           (sx * 2.0, YG - 0.62, DAIS_Z + 0.08), (sx * 1.85, YG - 0.55, DAIS_Z + 0.18)]
    curve_obj(f"feed{sx}", pts, COPPER, 0.05, root, res=3)
    for k, t_ in enumerate((0.3, 0.7)):
        cyl(f"feed{sx}_band{k}", 0.065, 0.04, (sx * 2.32, -1.42 + 0.67 * t_, DAIS_Z + 0.08), GOLD,
            rot=(math.radians(90), 0, 0), verts=16)
for k, (ax, ay) in enumerate(((-1, -1), (1, -1), (-1, 0.15), (1, 0.15))):
    a = math.atan2(ay, ax)
    rail(f"inlay{k}", [CIRC + Vector((0.95 * math.cos(a), 0.95 * math.sin(a), 0)),
                       CIRC + Vector((1.5 * math.cos(a), 1.5 * math.sin(a), 0))], 0.02)

# steam pipes: boiler dome -> valve chest on the cylinder (world coordinates)
for t, bc in zip(TRAINS, sorted(BOILERS, key=lambda b: -b.x)):
    sx = t.side
    vc = to_world((t.cx + sx * 0.25, (CYL_Y0 + CYL_Y1) / 2 - 0.25, CRANK_Z))
    dome = Vector((bc.x, bc.y + 0.12, DAIS_Z + 0.55 + 0.26 + 0.42))
    pts = [dome, dome + Vector((0, 0, 0.12)), Vector((sx * 3.02, bc.y + 0.4, dome.z + 0.12)),
           Vector((sx * 3.1, vc.y - 0.15, vc.z - 0.1)), vc]
    curve_obj(f"steam_pipe{sx}", [tuple(p) for p in pts], BRASS, 0.055, root, res=4)
    for k in (1, 2, 3):
        cyl(f"steam_pipe{sx}_flange{k}", 0.08, 0.05, tuple(pts[k]), GOLD, verts=16)


# ----------------------------------------------------------------------------
# Vortex, horizon, orbs, sparks
# ----------------------------------------------------------------------------

VORTEX, V_PHASE, V_STRENGTH, V_HOME = vortex_material()
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=RA + 0.02)
vortex = mesh_obj("vortex", bm, VORTEX, GATE)
vortex.location = (0, 0, -0.05)
glow(vortex)
horizon = curve_obj("horizon", circle_pts(RA - 0.03, 160, z=0.0), HORIZON, 0.035, GATE,
                    closed=True)
glow(horizon)

gate_light_d = bpy.data.lights.new("vortex_light", "POINT")
gate_light_d.color = (0.9, 0.35, 1.0)
gate_light_d.shadow_soft_size = 1.2
o = bpy.data.objects.new("vortex_light", gate_light_d)
link(o, GATE)
o.location = (0, 0, 0.9)
fire_lights = []
for bc in BOILERS:
    d = bpy.data.lights.new("fire_light", "POINT")
    d.color = (0.65, 0.4, 1.0)
    d.shadow_soft_size = 0.15
    o = bpy.data.objects.new("fire_light", d)
    link(o, root)
    o.location = bc + Vector((0, -0.6, 0.35))
    fire_lights.append(d)

ORBS = []
ORB_R = 1.55
if ACTIVE:
    for k in range(4):
        h = bpy.data.objects.new(f"orbit{k}", None)
        link(h, GATE)
        glow(sphere(f"orbit_orb{k}", 0.13, (0, 0, 0), ORB, h, segs=24))
        ring = mesh_obj(f"orbit_ring{k}", ring_mesh(
            [(0.19 * math.cos(TAU * i / 40), 0.19 * math.sin(TAU * i / 40)) for i in range(40)],
            [(0.17 * math.cos(TAU * i / 40), 0.17 * math.sin(TAU * i / 40)) for i in range(40)],
            -0.012, 0.012), GOLD, h, smooth=True)
        ring.rotation_euler = (math.radians(70), 0, 0)
        ORBS.append(h)
TRANSIENT = []


def clear_transient():
    for o in TRANSIENT:
        if o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)
    TRANSIENT.clear()


def arc(name, a, b, rng, jag=0.08, r=0.012, segs=7, mat=None, parent=None):
    a, b = Vector(a), Vector(b)
    d = b - a
    side = Vector((-d.y, d.x, 0)).normalized() if d.length else Vector((1, 0, 0))
    pts = []
    for i in range(segs + 1):
        t = i / segs
        p = a.lerp(b, t)
        if 0 < i < segs:
            p += side * rng.uniform(-jag, jag) + Vector((0, 0, rng.uniform(-0.02, 0.02)))
        pts.append(tuple(p))
    o = curve_obj(name, pts, mat or SPARK, r, parent or GATE, taper=lambda t: 1.0 - 0.6 * t)
    TRANSIENT.append(glow(o))


# ----------------------------------------------------------------------------
# Timelines
# ----------------------------------------------------------------------------
#
# Inactive (64 frames): eight dial steps of 7 frames - the rotor turns
# 1-2 glyphs (5 frames, eased), the master claw drops onto the glyph and the
# next chevron lights - then 8 frames of surge and fade back to dormant.
# The steps sum to zero, so the rotor (and every gear) ends where it began.
# Active (48 frames): the rotor turns 4 glyphs (one RUNES period) per loop,
# the pinions half a turn (4 spokes), the crank gears exactly once.

STEPS = [+2, -1, +1, -2, +1, +2, -1, -2]
STEP_F, MOVE_F = 7, 5
assert sum(STEPS) == 0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rotor_glyphs(f):
    """Rotor rotation in glyph pitches at frame f."""
    if ACTIVE:
        return 4.0 * f / N
    s, done = 0.0, 0
    for k, d in enumerate(STEPS):
        f0 = k * STEP_F
        if f >= f0 + MOVE_F:
            s += d
            done = k + 1
        elif f >= f0:
            s += d * smooth((f - f0) / MOVE_F)
    return s


def chevron_level(k, f):
    """Brightness 0..1 of chevron k (inactive: lights at its lock, holds,
    fades over the last frames)."""
    if ACTIVE:
        return 0.85 + 0.15 * math.sin(TAU * (2 * f / N + k / 8))
    lock = k * STEP_F + MOVE_F + 1
    if f < lock:
        return 0.0
    fade = smooth((f - (N - 5)) / 4.0)     # last frames fade to dark
    flash = 0.6 * math.exp(-(f - lock) / 1.5)
    return min(1.6, (1.0 + flash) * (1 - fade))


def claw_down(f):
    if ACTIVE:
        return 0.0
    if f >= len(STEPS) * STEP_F:
        return 0.0
    k, fl = divmod(f, STEP_F)
    return {MOVE_F: 0.7, MOVE_F + 1: 1.0}.get(fl, 0.0)


def lock_age(f):
    """Frames since the last claw lock (inactive)."""
    best = 99
    for k in range(len(STEPS)):
        lk = k * STEP_F + MOVE_F + 1
        if f >= lk:
            best = min(best, f - lk)
    return best


def charge(f):
    """How many chevrons are lit, as 0..1 (inactive)."""
    return sum(1 for k in range(8) if chevron_level(k, f) > 0.3) / 8.0


def pose(f):
    clear_transient()
    ph = TAU * f / N
    g = rotor_glyphs(f)
    turn = g * TAU / ROT_T
    th_r = ROT0 + turn
    ROTOR.rotation_euler = (0, 0, th_r)
    for t in TRAINS:
        th_p = mesh_phase(t.alpha, th_r, ROT_T, P_T)
        t.P.rotation_euler = (0, 0, th_p)
        t.Q.rotation_euler = (0, 0, th_p)
        th_d = mesh_phase(t.dd, th_p, Q_T, D_T)
        t.D.rotation_euler = (0, 0, th_d)
        # slider-crank: crosshead below the crank on the cylinder axis
        pin = t.dc + Vector((CRANK_R * math.cos(th_d), CRANK_R * math.sin(th_d), 0))
        dx = pin.x - t.cx
        yh = pin.y - math.sqrt(ROD_L ** 2 - dx * dx)
        t.cross.location = (t.cx, yh, CRANK_Z)
        t.piston.location = (t.cx, (yh + CYL_Y1 - 0.1) / 2, CRANK_Z)
        t.piston.scale.z = yh - CYL_Y1 + 0.1
        a, b = Vector((t.cx, yh, CRANK_Z + 0.06)), Vector((pin.x, pin.y, CRANK_Z + 0.06))
        d = b - a
        o = bpy.data.objects.new(f"conrod{t.side}", None)
        link(o, GATE)
        o.location = a
        o.rotation_euler = d.to_track_quat("X", "Z").to_euler()
        box("conrod_bar", (d.length, 0.07, 0.04), (d.length / 2, 0, 0), STEEL, o, bevel=0.008)
        for x in (0, d.length):
            cyl("conrod_end", 0.05, 0.06, (x, 0, 0), BRASS, o, verts=20)
        TRANSIENT.extend([o] + list(o.children_recursive))
    # chevrons, master claw
    for k, em in enumerate(CHEV_EM):
        em.default_value = 0.15 + 3.0 * chevron_level(k, f)
    down = claw_down(f)
    CLAW.location = (0, CLAW_UP * (1 - down) - 0.04, 0)
    # fire flicker (integer cycles per loop)
    flick = 0.8 + 0.15 * math.sin(3 * ph) + 0.08 * math.sin(7 * ph + 1.0)
    FIRE_EM.default_value = 6.0 * flick
    EMBER_EM.default_value = 2.5 * flick
    for fl, k in FLAMES:
        s = 0.75 + 0.25 * math.sin(5 * ph + k * 1.7) + 0.1 * math.sin(11 * ph + k)
        fl.scale = (1.0, 1.0, s)
    for d in fire_lights:
        d.energy = 6.0 * flick
    V_PHASE.default_value = f / N
    if ACTIVE:
        V_STRENGTH.default_value = 1.7
        V_HOME.default_value = 1.0
        MASTER_EM.default_value = 5.0 + 1.0 * math.sin(2 * ph)
        GLYPH_EM.default_value = 1.2 + 0.3 * math.sin(4 * ph)
        HORIZON_EM.default_value = 6.0 + 1.5 * math.sin(6 * ph)
        CRYSTAL_EM.default_value = 4.0 + 1.0 * math.sin(2 * ph + 1)
        FLOOR_RUNE_EM.default_value = 1.6 + 0.5 * math.sin(2 * ph)
        LAMP_EM.default_value = 2.5
        gate_light_d.energy = 140.0 + 25 * math.sin(6 * ph)
        for k, h in enumerate(ORBS):
            a = TAU * (k / 4 + f / (4 * N)) + 0.3
            h.location = pol(ORB_R, a, 0.32 + 0.04 * math.sin(2 * a))
            # comet tail behind the orb, along the orbit
            pts = [pol(ORB_R, a - 0.05 * i, 0.32) for i in range(1, 12)]
            o = curve_obj(f"orb_tail{k}", pts, ORB, 0.045, GATE,
                          taper=lambda t: 1.0 - 0.9 * t)
            TRANSIENT.append(glow(o))
        rng = random.Random(1000 + f)
        for k in range(4):     # arcs from chevrons into the vortex
            a = CHEV_A[rng.randrange(8)]
            arc(f"arc{k}", pol(RA + 0.05, a, 0.3),
                pol(rng.uniform(0.6, 1.4), a + rng.uniform(-0.6, 0.6), 0.1), rng, jag=0.12,
                r=0.016)
        for k, h in enumerate(ORBS):    # orbs discharge into the horizon
            if rng.random() < 0.5:
                a = TAU * (k / 4 + f / (4 * N)) + 0.3
                arc(f"orbarc{k}", pol(ORB_R, a, 0.32), pol(RA - 0.02, a + 0.25, 0.05), rng,
                    jag=0.06, r=0.011)
    else:
        c = charge(f)
        age = lock_age(f)
        flare = math.exp(-age / 2.0) if age < 99 else 0.0
        surge = smooth((f - 56) / 3.0) * (1 - smooth((f - 59) / 5.0))
        V_STRENGTH.default_value = 0.12 + 0.55 * c + 0.4 * flare + 1.2 * surge
        V_HOME.default_value = 0.0
        MASTER_EM.default_value = 0.2 + 7.0 * flare * (down > 0 or age < 3)
        GLYPH_EM.default_value = 0.25 + 0.5 * c + 0.6 * flare
        HORIZON_EM.default_value = 0.2 + 2.0 * c + 3.0 * surge
        CRYSTAL_EM.default_value = 0.6 + 2.5 * c
        FLOOR_RUNE_EM.default_value = 0.15 + 0.8 * c
        LAMP_EM.default_value = 1.2
        gate_light_d.energy = 6.0 + 30.0 * c + 60.0 * surge
        if age <= 1:   # sparks where the claw bites
            rng = random.Random(77 + f)
            for k in range(7):
                a = MASTER_A + rng.uniform(-0.25, 0.25)
                arc(f"lockspark{k}", pol(RS + 0.2, MASTER_A, 0.34),
                    pol(RS + 0.2 + rng.uniform(0.1, 0.45), a, 0.4 + rng.uniform(0, 0.2)), rng,
                    jag=0.03, r=0.012 * (1 - age * 0.4), segs=3)


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

FRAME_W, FRAME_H, FRAME_CY = 7.5, 7.5, 1.1
rig = setup_scene(frame_w=FRAME_W, frame_h=FRAME_H, frame_cy=FRAME_CY)
rig.ground.scale = (3, 3, 1)


def report_bounds():
    """Screen-space content bounds (tiles) to size the frame."""
    xs, ys = [], []
    for o in bpy.data.objects:
        if o.type not in ("MESH", "CURVE"):
            continue
        if o is rig.ground:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x)
            ys.append((w.y + w.z) / S2)
    print(f"BOUNDS screen x {min(xs):.2f}..{max(xs):.2f}  y {min(ys):.2f}..{max(ys):.2f}")


pose(0)
bpy.context.view_layer.update()
report_bounds()

# The gate stands over 5 tiles tall, so its shadow reaches far east: the
# shadow gets its own, wider frame (SHADOW_* in tiles, centre relative to the
# entity) instead of being cropped to the animation frame.
SHADOW_W, SHADOW_H, SHADOW_CX, SHADOW_CY = 15.0, 8.0, 3.75, 0.75


def render_shadow():
    scene = bpy.context.scene
    cam = scene.camera
    ppt = args.px_per_tile
    cam.data.ortho_scale = max(SHADOW_W, SHADOW_H)
    scene.render.resolution_x = round(SHADOW_W * ppt)
    scene.render.resolution_y = round(SHADOW_H * ppt)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((SHADOW_CX, 0, SHADOW_CY * S2)) - look * 30
    rig.ground.hide_render = False
    pose(0)
    for o in scene.objects:
        if o.type == "LIGHT":
            o.data.energy = 0.0
    rig.bg.inputs["Strength"].default_value = 0.0
    V_STRENGTH.default_value = 0.0         # self-lit parts must not light the ground
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
        if b and not b.inputs["Emission Strength"].is_linked:
            b.inputs["Emission Strength"].default_value = 0.0
    rig.sun_d.energy = 4.6
    for o in scene.objects:
        if o is not rig.ground and o.type in ("MESH", "CURVE"):
            o.visible_camera = False
            o.is_holdout = False
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((1.0, -0.35, -0.75)).normalized()).to_euler()
    fblend.render(OUT / "shadow.png")


if not BOUNDS_ONLY:
    # fblend's passes (main + glow); its own shadow frame is replaced below
    render_passes(rig, pose, extra_lights=(gate_light_d, *fire_lights), name=ENTITY)
    render_shadow()
