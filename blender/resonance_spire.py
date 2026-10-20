"""
Procedural Blender model + Factorio render of the resonance spire (a 1x1
beacon that spreads the effect of the orb sitting in its cradle).

    blender -b --factory-startup -P blender/resonance_spire.py -- \
        --out graphics/generated/resonance-spire [--preview --frame 0,16]

The spire is a tall gold-and-purple obelisk crowned by a tuning fork. The orb
sits in a cradle between the tines. A gimbal ring spins around the orb; the
two ruby strikers on its equator pluck both tines every half turn, the fork
rings, and each blow sends a resonance wave down the obelisk: its runes light
up top to bottom, the three floating halo rings jump as the wave passes and
the rune band on the plinth flashes when it reaches the ground.

The orb itself is not part of the animation: Factorio draws it as a beacon
module visualisation, so the spire shows whichever orb is inserted (or an
empty cradle). The frames are split into a back sheet (spire, drawn under the
orb) and a front sheet (everything nearer the camera than the orb's centre,
drawn over it), so the gimbal ring visibly passes in front of and behind the
orb. Output (frames in --out, then stitch.py):

    main-NNN.png        back layer          glow-NNN.png   self-lit parts
    front/main-NNN.png  front layer         shadow.png     wide shadow frame
    orb-<name>.png / orb-<name>-glow.png    module visualisation sprites

World units are Factorio tiles; the entity is 1x1 centred on the origin,
+y is north, +z is up. Shared helpers live in blender/fblend.py.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("resonance-spire", frames=64, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT

root = bpy.data.objects.new("resonance_spire", None)
link(root)

# ----------------------------------------------------------------------------
# Dimensions
# ----------------------------------------------------------------------------
# A 1x1 entity is tiny (64 px per tile), so the spire is built tall and the
# decoration chunky. Through the projection (screen y = (y + z) / sqrt(2)) the
# tine tips at z ~3.8 end up ~2.7 tiles above the footprint, like the vanilla
# medium electric pole.

PL_HALF, PL_CH, PL_H = 0.43, 0.12, 0.2      # octagonal plinth
ST_HALF, ST_CH, ST_Z = 0.32, 0.09, 0.4      # stepped pedestal on top of it
SH_Z0, SH_Z1 = ST_Z, 2.35                   # obelisk shaft (a diamond in plan)
SH_W0, SH_W1 = 0.25, 0.135                  # corner distance at bottom / top
CAP_Z = SH_Z1 + 0.15                        # top of the capital
ROOT_Z = CAP_Z + 0.24                       # tines bend about this height
TIP_Z = ROOT_Z + 0.92
TINE_X = 0.28                               # inner face of the tines
TT, TD = 0.085, 0.12                        # tine thickness (x) and depth (y)
ORB_Z, ORB_R = ROOT_Z + 0.42, 0.15                   # the orb in the cradle
RING_R, RING_T = 0.215, 0.02                # gimbal meridian ring radius / tube
RB, RBALL = 0.27, 0.03                      # striker ball centre radius / size


def sh_w(z):
    """Corner distance of the tapering shaft at height z."""
    return SH_W0 + (SH_W1 - SH_W0) * (z - SH_Z0) / (SH_Z1 - SH_Z0)


def octagon(half, ch):
    return [(-half + ch, -half), (half - ch, -half), (half, -half + ch), (half, half - ch),
            (half - ch, half), (-half + ch, half), (-half, half - ch), (-half, -half + ch)]


def prism(name, poly, z0, z1, mat, parent=root, bevel=0.01, top_poly=None):
    """Solid between a bottom outline and an (optionally smaller) top one."""
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in (top_poly or poly)]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent, bevel=bevel)
    o.data.shade_flat()
    return o


def rail(name, pts, r, closed=False, mat=None, parent=root):
    return curve_obj(name, [tuple(p) for p in pts], mat or GOLD, r, parent, closed=closed)


def ring(name, r, tube, mat, parent, verts=48, z0=None, z1=None):
    """Flat washer-like ring (axis local z)."""
    outer = [((r + tube) * math.cos(TAU * i / verts), (r + tube) * math.sin(TAU * i / verts))
             for i in range(verts)]
    inner = [((r - tube) * math.cos(TAU * i / verts), (r - tube) * math.sin(TAU * i / verts))
             for i in range(verts)]
    return mesh_obj(name, ring_mesh(outer, inner, -tube if z0 is None else z0,
                                    tube if z1 is None else z1),
                    mat, parent, smooth=True, bevel=min(0.006, tube * 0.3))


# Per-element emitters, so the resonance wave can light them one after another
RUNE_ROWS = 4
ROW_Z = [SH_Z0 + (SH_Z1 - SH_Z0) * (k + 0.5) / RUNE_ROWS for k in range(RUNE_ROWS)]
ROW_EM = []
ROW_MAT = []
for k in range(RUNE_ROWS):
    m, s = emitter(f"rune_row{k}", (0.8, 0.2, 1.0), 0.3, base=(0.08, 0.02, 0.08))
    ROW_MAT.append(m)
    ROW_EM.append(s)
BAND_Z = [SH_Z0 + (SH_Z1 - SH_Z0) * k / RUNE_ROWS for k in range(1, RUNE_ROWS)]
HALO_Z = [z + 0.05 for z in BAND_Z]         # floating resonator rings over the bands
HALO_MAT, HALO_EM = [], []
for k in range(len(HALO_Z)):
    m, s = emitter(f"halo_band{k}", (0.85, 0.25, 1.0), 0.3, base=(0.1, 0.02, 0.1))
    HALO_MAT.append(m)
    HALO_EM.append(s)
BASE_RUNE, BASE_EM = emitter("base_rune", (0.8, 0.2, 1.0), 0.3, base=(0.08, 0.02, 0.08))
TINE_RUNE, TINE_EM = emitter("tine_rune", (1.0, 0.45, 1.0), 0.3, base=(0.1, 0.03, 0.1))

# ----------------------------------------------------------------------------
# Plinth and pedestal
# ----------------------------------------------------------------------------
# Like the vanilla 1x1 entities, the base fills most of the tile; it reads as
# an octagon (front face plus two lit chamfers) under a heavy gold rail.

plinth = octagon(PL_HALF, PL_CH)
prism("plinth", plinth, 0, PL_H, BRONZE)
rail("plinth_rail", [(x, y, PL_H) for x, y in plinth], 0.05, closed=True)
rail("plinth_foot", [(x * 1.01, y * 1.01, 0.02) for x, y in plinth], 0.028, closed=True)
P3 = [Vector((x, y, 0.03)) for x, y in plinth]
T3 = [Vector((x, y, PL_H - 0.03)) for x, y in plinth]
for i in (7, 0, 1):          # visible faces: front chamfers and front
    j = (i + 1) % 8
    p = Panel(P3[i], P3[j], T3[j], T3[i])
    if i == 0:
        # front: glowing rune band between gold bosses; flashes when the wave lands
        inner = sub_panel(p, 0.2, 0.8, 0.05, 0.95)
        inner.build("plinth_band", BASE_RUNE, thick=0.004, parent=root)
        glow(bpy.data.objects["plinth_band"])
        for gi, u in enumerate((0.3, 0.5, 0.7)):
            g = sub_panel(inner, u - 0.09, u + 0.09, 0.0, 1.0)
            for si, stroke in enumerate(RUNES[gi + 1]):
                curve_obj(f"plinth_glyph{gi}_{si}",
                          [g.at(0.15 + 0.7 * a, 0.1 + 0.8 * b, 0.01) for a, b in stroke],
                          GOLD, 0.012, root)
        p.studs("plinth_boss", [(0.1, 0.5), (0.9, 0.5)], r=0.035, mat=RUBY, parent=root)
        gold_frame(inner, "plinth_band_frame", r=0.018)
    else:
        p.studs(f"plinth_rivet{i}", [(0.3, 0.5), (0.7, 0.5)], r=0.02, parent=root)

step = octagon(ST_HALF, ST_CH)
prism("step", step, PL_H, ST_Z, PURPLE, top_poly=[(x * 0.9, y * 0.9) for x, y in step])
rail("step_rail", [(x * 0.9, y * 0.9, ST_Z) for x, y in step], 0.035, closed=True)
S3 = [Vector((x, y, PL_H + 0.01)) for x, y in step]
U3 = [Vector((x * 0.9, y * 0.9, ST_Z)) for x, y in step]
for i in (7, 0, 1):
    j = (i + 1) % 8
    p = Panel(S3[i], S3[j], U3[j], U3[i])
    gold_frame(p, f"step_frame{i}", r=0.016, inset=0.06)
    if i == 0:
        sub_panel(p, 0.1, 0.9, 0.1, 0.9).filigree(
            "step_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.46, 1.0),
                         fit(scroll_c(0, 0, 1), 0.54, 0.0, 1.0, 1.0, flip_x=True)],
            radius=0.017, lift=0.012, parent=root)
        p.studs("step_gem", [(0.5, 0.55)], r=0.03, mat=RUBY, parent=root)
    else:
        p.studs(f"step_gem{i}", [(0.5, 0.5)], r=0.022, mat=RUBY, parent=root)

# gold scroll buttresses from the pedestal's corners up onto the shaft
for k in range(4):
    a = TAU * k / 4 - math.pi / 2          # S, E, N, W corners of the diamond
    d = Vector((math.cos(a), math.sin(a), 0))
    curl = fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.17, 0.42, flip_x=True)
    rail(f"buttress{k}", [d * (sh_w(SH_Z0 + v) + 0.02 + u) + Vector((0, 0, SH_Z0 + v))
                          for u, v in curl], 0.024)
    sphere(f"buttress_gem{k}", 0.026, tuple(d * (sh_w(SH_Z0) + 0.13) +
                                            Vector((0, 0, SH_Z0 + 0.03))), RUBY, root)

# ----------------------------------------------------------------------------
# Obelisk shaft
# ----------------------------------------------------------------------------
# A diamond in plan, so the camera sees two faces (the south-west one lit by
# the key light, the south-east one in shade) and a gold rib up the middle.


def corners(z, grow=0.0):
    w = sh_w(z) + grow
    return [Vector((0, -w, z)), Vector((w, 0, z)), Vector((0, w, z)), Vector((-w, 0, z))]


bot, top = corners(SH_Z0), corners(SH_Z1)
prism("shaft", [(v.x, v.y) for v in bot], SH_Z0, SH_Z1, PURPLE, bevel=0.006,
      top_poly=[(v.x, v.y) for v in top])
for k in range(4):
    rail(f"shaft_rib{k}", [bot[k] * 1.0 + Vector((0, 0, 0.0)), top[k]], 0.03)
for k, z in enumerate(BAND_Z):
    rail(f"shaft_band{k}", corners(z, 0.012), 0.024, closed=True)
    for c in corners(z, 0.03)[:2] + corners(z, 0.03)[3:]:
        sphere(f"shaft_band{k}_stud{c.x:.2f}{c.y:.2f}", 0.022, tuple(c), RUBY, root)

# faces: SW = W->S corner, SE = S->E corner (counter-clockwise = outward normal)
edges_z = [SH_Z0] + BAND_Z + [SH_Z1]
for row in range(RUNE_ROWS):
    z0, z1 = edges_z[row] + 0.03, edges_z[row + 1] - 0.03
    lo, hi = corners(z0), corners(z1)
    for fi, (a, b) in enumerate(((3, 0), (0, 1))):
        face = Panel(lo[a], lo[b], hi[b], hi[a])
        inner = sub_panel(face, 0.16, 0.84, 0.04, 0.96)
        gold_frame(inner, f"face{row}_{fi}_frame", r=0.014)
        if (row + fi) % 2 == 0:
            # glowing rune: lights up as the wave passes this row
            for gi, stroke in enumerate(RUNES[(row * 2 + fi) % len(RUNES)]):
                glow(curve_obj(f"face{row}_{fi}_rune{gi}",
                               [inner.at(0.18 + 0.64 * u, 0.12 + 0.76 * v, 0.008)
                                for u, v in stroke], ROW_MAT[row], 0.013, root))
        else:
            inner.filigree(f"face{row}_{fi}_fil",
                           [fit(scroll_c(0, 0, 1), 0.05, 0.05, 0.95, 0.95, flip_x=fi == 1)],
                           radius=0.016, lift=0.01, parent=root)

# capital: flared gold collar carrying the fork's yoke
cyl("capital_neck", sh_w(SH_Z1) * 0.75, 0.06, (0, 0, SH_Z1 + 0.03), GOLD, root, r2=sh_w(SH_Z1) * 0.9)
cyl("capital", 0.12, CAP_Z - SH_Z1 - 0.06, (0, 0, (CAP_Z + SH_Z1 + 0.06) / 2), GOLD, root,
    r2=0.17, verts=8, bevel=0.01).rotation_euler = (0, 0, math.pi / 8)
rail("capital_rim", [(0.175 * math.cos(TAU * i / 8 + math.pi / 8),
                      0.175 * math.sin(TAU * i / 8 + math.pi / 8), CAP_Z) for i in range(8)],
     0.022, closed=True)
for i in range(8):
    a = TAU * i / 8
    sphere(f"capital_gem{i}", 0.02, (0.16 * math.cos(a), 0.16 * math.sin(a), CAP_Z - 0.045),
           RUBY if i % 2 else GOLD, root)
# fork handle: the tuning fork's stem stands in the capital, the U-bend on top
FORK_Z = ROOT_Z - 0.17          # bottom of the U-bend
cyl("fork_handle", 0.045, FORK_Z - CAP_Z + 0.02, (0, 0, (FORK_Z + CAP_Z) / 2), GOLD, root,
    verts=16)
for zz in (CAP_Z + 0.02, FORK_Z - 0.01):
    cyl(f"fork_handle_ring{zz:.2f}", 0.06, 0.03, (0, 0, zz), BRASS, root, verts=16)

# ----------------------------------------------------------------------------
# Halo rings: floating resonators around the shaft
# ----------------------------------------------------------------------------
halos = []
for k, z in enumerate(HALO_Z):
    h = bpy.data.objects.new(f"halo{k}", None)
    link(h, root)
    h.location = (0, 0, z)
    r = sh_w(z) + 0.1
    ring(f"halo{k}_ring", r, 0.034, GOLD, h, verts=64, z0=-0.022, z1=0.022)
    glow(ring(f"halo{k}_band", r - 0.044, 0.008, HALO_MAT[k], h, verts=64, z0=-0.012, z1=0.012))
    for g in range(8):
        a = TAU * (g + 0.5) / 8
        sphere(f"halo{k}_stud{g}", 0.022 if g % 2 else 0.018,
               (r * math.cos(a), r * math.sin(a), 0.022), RUBY if g % 2 else GOLD, h)
    halos.append(h)

# ----------------------------------------------------------------------------
# Tuning fork
# ----------------------------------------------------------------------------
# A U-shaped yoke on the capital carries two gold tines. Each tine is its own
# object pivoting about its root, so it can be bent by the strikers and ring.
XC = TINE_X + TT / 2          # tine centre line
yoke_pts = [(-XC, 0, ROOT_Z + 0.04)]
for i in range(1, 12):
    a = math.pi * i / 12
    yoke_pts.append((-XC * math.cos(a), 0, ROOT_Z - 0.06 - (ROOT_Z - 0.06 - FORK_Z) * math.sin(a)))
yoke_pts.append((XC, 0, ROOT_Z + 0.04))
rail("yoke", yoke_pts, 0.055)
rail("yoke_inlay", [(x, y - 0.05, z) for x, y, z in yoke_pts[2:-2]], 0.016, mat=BRONZE)
for sx in (-1, 1):
    sphere(f"yoke_gem{sx}", 0.03, (sx * 0.2, -0.05, FORK_Z + 0.04), RUBY, root)

tines = []
for side in (-1, 1):
    t = bpy.data.objects.new(f"tine{side}", None)
    link(t, root)
    t.location = (side * XC, 0, ROOT_Z)
    L = TIP_Z - ROOT_Z
    box(f"tine{side}_bar", (TT, TD, L), (0, 0, L / 2), GOLD, t, bevel=0.014)
    # enamel strip with a glowing slot down the front face
    box(f"tine{side}_enamel", (TT * 0.6, 0.01, L * 0.78), (0, -TD / 2 - 0.004, L * 0.47),
        PURPLE, t, bevel=0.003)
    glow(box(f"tine{side}_slot", (TT * 0.22, 0.012, L * 0.66), (0, -TD / 2 - 0.008, L * 0.47),
             TINE_RUNE, t, bevel=0.002))
    for zz in (0.06, L * 0.5, L - 0.08):
        box(f"tine{side}_band{zz:.2f}", (TT + 0.022, TD + 0.022, 0.035), (0, 0, zz), GOLD, t,
            bevel=0.008)
    # outward scroll on the outer face, chunky like the conjuration machine's
    rail(f"tine{side}_scroll", [(side * (TT / 2 + 0.01 + u), -0.0, v) for u, v in
                                fit(scroll_c(0, 0, 1), 0.0, L * 0.12, 0.13, L * 0.55,
                                    flip_x=True)], 0.02, parent=t)
    sphere(f"tine{side}_gem", 0.026, (side * (TT / 2 + 0.03), -0.02, L * 0.12), RUBY, t)
    # tip finial: gold spike with a ruby
    cyl(f"tine{side}_tipcone", TT * 0.62, 0.12, (0, 0, L + 0.06), GOLD, t, verts=8, r2=0.0)
    sphere(f"tine{side}_tipgem", 0.03, (0, -0.02, L - 0.02), RUBY, t)
    tines.append((side, t))

# central spike behind the orb, like the trident in the item icon
cyl("spike_stem", 0.03, 0.22, (0, 0.2, CAP_Z + 0.1), GOLD, root)

# ----------------------------------------------------------------------------
# Cradle and gimbal
# ----------------------------------------------------------------------------
# A bronze stem rises from the capital to a claw cup holding the orb. The
# gimbal is a meridian ring that turns about the stem on a collar at its
# lower pole; an equatorial ring is rigidly pinned to it. The two ruby
# strikers on the equator reach out to RB + RBALL, past the tines' inner faces
# at TINE_X, so every half turn they pluck both tines (outwards, i.e. the
# tuning fork's natural anti-phase mode).
STEM_Z0 = FORK_Z
COLLAR_Z = ORB_Z - RING_R
cyl("stem", 0.03, COLLAR_Z - STEM_Z0 + 0.06, (0, 0, (COLLAR_Z + STEM_Z0 + 0.06) / 2), BRONZE,
    root)
cyl("stem_boss", 0.055, 0.05, (0, 0, STEM_Z0 + 0.03), BRASS, root)
CUP_Z = COLLAR_Z + 0.05
cyl("cup", 0.05, 0.04, (0, 0, CUP_Z), GOLD, root, r2=0.07)
for k in range(4):
    a = TAU * k / 4 + math.pi / 4
    d = Vector((math.cos(a), math.sin(a), 0))
    pts = []
    for i in range(9):          # claw hugging the orb from below
        el = math.radians(-70 + 60 * i / 8)
        r = ORB_R + 0.018
        pts.append(Vector((0, 0, ORB_Z)) + d * r * math.cos(el) + Vector((0, 0, r * math.sin(el))))
    pts.insert(0, Vector((0, 0, CUP_Z)) + d * 0.05)
    curve_obj(f"claw{k}", [tuple(p) for p in pts], GOLD, 0.017, root,
              taper=lambda t: 1.0 - 0.45 * t)
    sphere(f"claw{k}_tip", 0.016, tuple(pts[-1]), RUBY, root)

gimbal = bpy.data.objects.new("gimbal", None)
link(gimbal, root)
gimbal.location = (0, 0, ORB_Z)
mer = ring("gimbal_meridian", RING_R, RING_T, GOLD, gimbal, verts=64, z0=-0.016, z1=0.016)
mer.rotation_euler = (math.radians(90), 0, 0)        # in the local xz plane
ring("gimbal_equator", RING_R + 0.004, 0.016, BRASS, gimbal, verts=64, z0=-0.014, z1=0.014)
cyl("gimbal_collar", 0.05, 0.06, (0, 0, -RING_R), BRASS, gimbal, verts=24)
sphere("gimbal_pole_gem", 0.026, (0, 0, RING_R + 0.012), RUBY, gimbal)
for sx in (-1, 1):
    # striker: pin boss on the equator, arm, ruby ball
    cyl(f"striker{sx}_arm", 0.014, RB - RING_R, (sx * (RING_R + RB) / 2, 0, 0), STEEL, gimbal,
        rot=(0, math.radians(90), 0), verts=12)
    sphere(f"striker{sx}_boss", 0.026, (sx * RING_R, 0, 0), GOLD, gimbal)
    sphere(f"striker{sx}_ball", RBALL, (sx * RB, 0, 0), RUBY, gimbal, segs=16)
for sy in (-1, 1):   # gems where the meridian crosses the equator
    sphere(f"gimbal_cross{sy}", 0.018, (0, sy * RING_R, 0), GOLD, gimbal)

# ----------------------------------------------------------------------------
# The orb (rendered on its own, Factorio draws it as the module visualisation)
# ----------------------------------------------------------------------------
ORBS = {
    # colours sampled from graphics/productivity-orb.png and cleansing-orb.png
    "productivity": ((1.0, 0.36, 0.05), (0.6, 0.1, 0.01)),
    "cleansing": ((0.35, 1.0, 0.55), (0.08, 0.45, 0.22)),
}


def orb_material(name, bright, dark):
    """Glassy self-lit orb with a marbled interior like the item icons."""
    m, em = emitter(f"orb_{name}", bright, 1.2, base=dark, glass=True)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Distortion"].default_value = 2.5
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (*bright, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m, em


orb_mats = {k: orb_material(k, c, b) for k, (c, b) in ORBS.items()}
orb = sphere("orb", ORB_R, (0, 0, ORB_Z), orb_mats["productivity"][0], root, segs=32)
orb_light_d = bpy.data.lights.new("orb_light", "POINT")
orb_light_d.shadow_soft_size = 0.05
orb_light = bpy.data.objects.new("orb_light", orb_light_d)
link(orb_light, root)
orb_light.location = (0, 0, ORB_Z)

# ----------------------------------------------------------------------------
# Kinematics
# ----------------------------------------------------------------------------
# One loop = one turn of the gimbal = two plucks. The tine is a damped
# oscillator that the striker ball can only push outwards (a one-sided
# contact). Integrating it over a few loops gives the periodic steady state:
# the ball shoves the tine out, slips off its edge faster than the tine can
# follow, and the fork rings down until the next pluck.
TINE_PERIOD = 4.5        # frames; slow enough not to alias at 64 frames per loop
TINE_DECAY = 9.0         # frames (1/e of the amplitude)
GIMBAL_0 = -math.radians(40)    # gimbal angle at frame 0


def gimbal_angle(t):
    return GIMBAL_0 + TAU * t / N


def contact(t):
    """How far a striker ball forces the +x tine's face outwards (at orb
    height), or None when no ball touches it. Both balls are checked."""
    best = None
    for k in (0, 1):
        a = gimbal_angle(t) + k * math.pi
        xc, yc = RB * math.cos(a), abs(RB * math.sin(a))
        if xc <= 0:
            continue
        if yc <= TD / 2:
            c = xc + RBALL - TINE_X
        elif yc - TD / 2 < RBALL:
            c = xc + math.sqrt(RBALL ** 2 - (yc - TD / 2) ** 2) - TINE_X
        else:
            continue
        if c > 0 and (best is None or c > best):
            best = c
    return best


def simulate():
    """Damped tine (deflection x at orb height) with a one-sided contact: the
    ball can push the face out but never pull it. Returns the per-frame
    deflection of the steady state and the times the balls slip off."""
    w = TAU / TINE_PERIOD
    zeta = 1.0 / (TINE_DECAY * w)
    dt = 0.002
    per_frame = round(1 / dt)
    x = v = 0.0
    out, releases = [], []
    prev_c = None
    for loop in range(4):
        for s in range(N * per_frame):
            t = s * dt
            if loop == 3 and s % per_frame == 0:
                out.append(x)
            v += (-w * w * x - 2 * zeta * w * v) * dt
            x += v * dt
            c = contact(t)
            if c is not None and x < c:
                x = c
                if prev_c is not None:
                    v = max(v, (c - prev_c) / dt)
            if loop == 3 and prev_c is not None and c is None:
                releases.append(t)
            prev_c = c
    assert abs(out[0] - x) < 2e-3, f"tine motion does not loop ({out[0]} vs {x})"
    return out, releases


DEFLECT, RELEASES = simulate()
STRIKES = sorted(round(r) % N for r in RELEASES)
print("tine deflection range", min(DEFLECT), max(DEFLECT), "plucks at", STRIKES)
print("deflection", " ".join(f"{d:.3f}" for d in DEFLECT))
assert len(STRIKES) == 2, STRIKES

WAVE_SPEED = 0.22        # tiles of height per frame for the resonance wave


def since_strike(f, delay=0.0):
    """Frames since the latest pluck reached a point `delay` frames down the wave."""
    return min((f - s - delay) % N for s in STRIKES)


def pulse(age, width=2.5):
    return math.exp(-0.5 * (age / width) ** 2) if age < N / 2 else 0.0


def kick(age, tau=3.0):
    """Ring jump: quick rise, settling back (zero at age 0)."""
    return (age / tau) * math.exp(1 - age / tau)


def pose(f):
    gimbal.rotation_euler = (0, 0, gimbal_angle(f))
    d = DEFLECT[f % N]
    for side, t in tines:
        # bend about the root so the face moves `d` at orb height
        t.rotation_euler = (0, side * math.atan2(d, ORB_Z - ROOT_Z), 0)
    ring_amp = math.exp(-since_strike(f) / TINE_DECAY)
    TINE_EM.default_value = 0.3 + 3.0 * ring_amp
    for k, z in enumerate(ROW_Z):
        age = since_strike(f, (ROOT_Z - z) / WAVE_SPEED)
        ROW_EM[k].default_value = 0.25 + 3.5 * pulse(age)
    for k, (h, z) in enumerate(zip(halos, HALO_Z)):
        age = since_strike(f, (ROOT_Z - z) / WAVE_SPEED)
        h.location.z = z + 0.05 * kick(age)
        h.rotation_euler = (0, 0, TAU * f / N * (1 if k % 2 else -1) / 4)
        HALO_EM[k].default_value = 0.25 + 3.0 * pulse(age, 3.0)
    BASE_EM.default_value = 0.3 + 3.0 * pulse(since_strike(f, (ROOT_Z - PL_H) / WAVE_SPEED), 3.0)


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
# Frame: 1.25 x 3.25 tiles, centred 1.17 tiles above the origin on screen.
FRAME_W, FRAME_H, FRAME_CY = 1.25, 3.25, 1.17
rig = setup_scene(FRAME_W, FRAME_H, FRAME_CY)
scene = bpy.context.scene
cam = scene.camera

# Holdout plane through the orb centre, facing the camera: in the front pass it
# hides everything farther away than the orb's centre.
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=4)
depth_plane = mesh_obj("depth_plane", bm, BRONZE)
depth_plane.location = (0, 0, ORB_Z)
depth_plane.rotation_euler = (math.radians(45), 0, 0)
depth_plane.is_holdout = True
for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission",
             "visible_volume_scatter"):
    setattr(depth_plane, attr, False)
depth_plane.hide_render = True

frames = [int(f) for f in args.frame.split(",")] if args.preview else range(N)
meshes = [o for o in scene.objects if o.type in ("MESH", "CURVE")]


def reset():
    for o in meshes:
        o.is_holdout = o is depth_plane
        o.visible_camera = True
    depth_plane.hide_render = True
    orb.hide_render = True
    orb_light.hide_render = True
    rig.bg.inputs["Strength"].default_value = 0.15
    rig.sun_d.energy = 4.6
    rig.fill_d.energy = 1.1


# 1. back layer: the spire without the orb (the cradle may be empty)
reset()
for f in frames:
    pose(f)
    render(OUT / f"main-{f:03d}.png")

# 2. front layer: only what is nearer than the orb's centre, orb held out
reset()
depth_plane.hide_render = False
orb.hide_render = False
orb.is_holdout = True
for f in frames:
    pose(f)
    render(OUT / "front" / f"main-{f:03d}.png")

# 3. the orbs, one sprite each (everything else held out), lit by themselves
reset()
pose(0)
orb.hide_render = False
orb_light.hide_render = False
# alone: the parts in front of it come from the front layer, and nothing
# else may cut into the sprite
for o in meshes:
    o.hide_render = o is not orb
for name, (mat, em) in orb_mats.items():
    orb.data.materials[0] = mat
    orb_light_d.color = ORBS[name][0]
    orb_light_d.energy = 0.0
    render(OUT / "orbs" / f"orb-{name}.png")
rig.bg.inputs["Strength"].default_value = 0.0
rig.sun_d.energy = rig.fill_d.energy = 0.0
for name, (mat, em) in orb_mats.items():
    orb.data.materials[0] = mat
    render(OUT / "orbs" / f"orb-{name}-glow.png")

# 4. glow layer: self-lit parts of the spire only
for o in meshes:
    o.hide_render = False
rig.ground.hide_render = True
reset()
if not args.no_glow:
    rig.bg.inputs["Strength"].default_value = 0.0
    rig.sun_d.energy = rig.fill_d.energy = 0.0
    for o in meshes:
        o.is_holdout = not o.get("glow", False)
    for f in frames:
        pose(f)
        render(OUT / f"glow-{f:03d}.png")

# 5. shadow: the tall spire throws a long shadow to the east like the vanilla
# poles, so it gets its own wide frame (camera moved over the shadow).
reset()
SH_W, SH_H, SH_CX, SH_CY = 5.75, 1.5, 2.25, 0.2
pose(0)
rig.ground.hide_render = False
for o in meshes:
    if o is not rig.ground:
        o.visible_camera = False
rig.fill_d.energy = 0.0
rig.bg.inputs["Strength"].default_value = 0.0
# Vanilla poles throw a crisp shadow east and slightly north (up on screen).
rig.sun_d.angle = math.radians(1)
rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
    Vector((1.0, 0.17, -0.75)).normalized()).to_euler()
cam.data.ortho_scale = max(SH_W, SH_H)
scene.render.resolution_x = round(SH_W * args.px_per_tile)
scene.render.resolution_y = round(SH_H * args.px_per_tile)
cam.location.x += SH_CX
# moving the look-at target along z by dz moves the frame by dz / sqrt(2) on screen
cam.location.z += (SH_CY - FRAME_CY) * math.sqrt(2)
render(OUT / "shadow.png")
