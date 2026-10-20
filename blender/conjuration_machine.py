"""
Procedural Blender model + Factorio render of the conjuration machine.

Builds the machine from scratch (no .blend file to keep in sync), animates the
mechanism as a seamless loop and renders the frames Factorio needs:

    blender -b --factory-startup -P blender/conjuration_machine.py -- \
        --out graphics/generated/conjuration-machine [--preview] [--frames 32]

Shared helpers live in blender/fblend.py. Then stitch with blender/stitch.py. World units are Factorio tiles; the entity
is 3x3 centred on the origin, +y is north, +z is up.
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

args = fblend.parse_args("conjuration-machine", frames=64, samples=256)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT

POTION, POTION_EM = emitter("potion", (0.7, 0.15, 0.6), 0.9)
TANK_LIQ, _ = emitter("tank_liquid", (0.45, 0.06, 0.38), 0.35, base=(0.25, 0.03, 0.2))
POTION_TEAL, _ = emitter("potion_teal", (0.12, 0.55, 0.5), 0.7)
POTION_AMBER, _ = emitter("potion_amber", (0.8, 0.45, 0.1), 0.7)
BREW, _ = emitter("brew", (0.7, 0.15, 0.62), 0.8)
ORB, ORB_EM = emitter("orb", (0.85, 0.08, 0.75), 1.0, base=(0.5, 0.03, 0.42), glass=True)
SPARK, _ = emitter("spark", (1.0, 0.45, 0.12), 5.0)
SHARD, SHARD_EM = emitter("shard", (1.0, 0.35, 0.85), 5.0, glass=True)

# ----------------------------------------------------------------------------
# The machine
# ----------------------------------------------------------------------------
#
# Shape follows the vanilla assemblers seen through Factorio's projection
# (screen y = (y + z) / sqrt(2), see core/lualib/math3d.lua): side walls slope
# outwards so they read as decorated wings, and the rim rises towards the
# back, so the tall back wall faces the camera like in the reference art.

root = bpy.data.objects.new("conjuration_machine", None)
link(root)

HALF = 1.46          # half footprint
CH = 0.3             # front corner chamfer of the plinth
PLINTH_H = 0.22
XT = 1.08            # half width of the rim (side walls slope in to here)
TC = 0.22            # front corner chamfer of the rim
YF, ZF = -1.08, 0.82   # rim front edge
YB, ZB = 1.36, 1.5     # rim back edge
RIM_W = 0.19         # width of the gold rim band around the opening
FLOOR_Z = 0.55
x0, x1 = -XT + RIM_W, XT - RIM_W            # opening
y0, y1 = YF + RIM_W, YB - 0.1


def zr(y):
    """Height of the sloped rim plane at y."""
    return ZF + (y - YF) / (YB - YF) * (ZB - ZF)


DECK_Z = zr(0.0)     # rim height mid-way, used for things standing on the rim

# Outlines, counter-clockwise: front, FR chamfer, right, back, left, FL chamfer
bot2d = [(-HALF + CH, -HALF), (HALF - CH, -HALF), (HALF, -HALF + CH),
         (HALF, HALF), (-HALF, HALF), (-HALF, -HALF + CH)]
top2d = [(-XT + TC, YF), (XT - TC, YF), (XT, YF + TC), (XT, YB), (-XT, YB), (-XT, YF + TC)]
B3 = [Vector((x, y, PLINTH_H)) for x, y in bot2d]
T3 = [Vector((x, y, zr(y))) for x, y in top2d]


def prism(name, poly, z0, z1, mat, bevel=0.01):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, root, bevel=bevel)
    o.data.shade_flat()
    return o


def rail(name, pts3, r, closed=False, mat=None):
    return curve_obj(name, [tuple(p) for p in pts3], mat or GOLD, r, root, closed=closed)


def sub_panel(p, u0, u1, v0=0.0, v1=1.0):
    return Panel(p.at(u0, v0), p.at(u1, v0), p.at(u1, v1), p.at(u0, v1))


def frame(p, name, r=0.045, inset=0.0):
    """Thick bevelled gold frame around a panel."""
    q = sub_panel(p, inset, 1 - inset, inset, 1 - inset) if inset else p
    rail(name, [Vector(q.at(u, v, r * 0.4)) for u, v in ((0, 0), (1, 0), (1, 1), (0, 1))], r,
         closed=True)


def lyre(cu=0.5, cv=0.5, w=1.0, h=1.0):
    """Symmetric double-scroll motif."""
    S = []
    big = scroll_c(0, 0, 1, up=True)
    small = scroll_c(0, 0, 1, up=False)
    for m in (False, True):
        sg = 1 if m else -1
        S.append(fit(big, cu + sg * 0.03 * w, cv - 0.45 * h, cu + sg * 0.4 * w,
                     cv + 0.45 * h))
        S.append(fit(small, cu + sg * 0.28 * w, cv - 0.4 * h, cu + sg * 0.48 * w,
                     cv + 0.05 * h))
    S.append([(cu, cv - 0.45 * h), (cu, cv + 0.1 * h)])
    S.append(bezier2((cu - 0.12 * w, cv + 0.32 * h), (cu, cv + 0.02 * h),
                     (cu + 0.12 * w, cv + 0.32 * h)))
    return S


def scroll_pair(u0, u1, v0=0.06, v1=0.94, mirror=False):
    """A big scroll with a counter-curl, filling a panel like the reference."""
    big = scroll_c(0, 0, 1, up=True)
    small = scroll_c(0, 0, 1, up=False)
    w = u1 - u0
    return [fit(big, u0 + 0.12 * w, v0, u1 - 0.02 * w, v1, flip_x=mirror),
            fit(small, u0 + 0.02 * w if not mirror else u1 - 0.42 * w, v0 + 0.04,
                u0 + 0.42 * w if not mirror else u1 - 0.02 * w, v0 + 0.5 * (v1 - v0),
                flip_x=not mirror)]


FIL_R = 0.042        # raised scrollwork thickness (the reference's heavy gold)
# Elder-futhark-like rune glyphs (unit square strokes) for the glowing inlays.
RUNES = (
    [[(0.35, 0.1), (0.35, 0.9)], [(0.35, 0.55), (0.72, 0.75)], [(0.35, 0.78), (0.72, 0.98)]],
    [[(0.5, 0.05), (0.5, 0.95)], [(0.5, 0.6), (0.18, 0.92)], [(0.5, 0.6), (0.82, 0.92)]],
    [[(0.18, 0.05), (0.65, 0.5), (0.5, 0.8), (0.35, 0.5), (0.82, 0.05)]],
    [[(0.32, 0.05), (0.32, 0.95), (0.68, 0.75), (0.32, 0.52), (0.72, 0.05)]],
)

# --- plinth: dark bronze band with a thick gold top rail and rivet row -------
prism("plinth", bot2d, 0, PLINTH_H, BRONZE)
rail("plinth_rail", [(x, y, PLINTH_H) for x, y in bot2d], 0.065, closed=True)
rail("plinth_foot", [(x * 1.006, y * 1.006, 0.02) for x, y in bot2d], 0.03, closed=True)
for fi in (5, 0, 1):
    a, b = Vector((*bot2d[fi], 0)), Vector((*bot2d[(fi + 1) % 6], 0))
    nrm = Vector((b.y - a.y, -(b.x - a.x), 0)).normalized()
    count = 4 if fi else 15
    for k in range(count):
        p = a.lerp(b, (k + 0.5) / count) + nrm * 0.004
        sphere(f"rivet{fi}_{k}", 0.026, (p.x, p.y, PLINTH_H * 0.5), GOLD, root)

# --- body walls ---------------------------------------------------------------
walls = {}
for i in range(6):
    j = (i + 1) % 6
    p = Panel(B3[i], B3[j], T3[j], T3[i])
    p.build(f"wall{i}", PURPLE, parent=root)
    walls[i] = p
for i in range(6):   # thick gold ribs on the corner edges
    rail(f"corner_rib{i}", [B3[i] + Vector((0, 0, 0.02)), T3[i]], 0.07)

front = walls[0]
ribs_u = (0.3, 0.7)
for k, u in enumerate(ribs_u):
    rail(f"front_rib{k}", [Vector(front.at(u, 0, 0.03)), Vector(front.at(u, 1, 0.03))], 0.06)
for k, (u0, u1) in enumerate(((0.0, ribs_u[0]), ribs_u, (ribs_u[1], 1.0))):
    sp = sub_panel(front, u0 + 0.03, u1 - 0.03, 0.08, 0.92)
    frame(sp, f"fp{k}_frame", 0.032)
    inner = sub_panel(sp, 0.06, 0.94, 0.08, 0.92)
    if k == 1:
        inner.filigree("fp_lyre", lyre(0.5, 0.5, 1.0, 1.0), radius=FIL_R, parent=root)
        inner.studs("fp_gem", [(0.5, 0.86)], r=0.04, mat=RUBY, parent=root)
        inner.studs("fp_dots", [(0.12, 0.85), (0.88, 0.85), (0.12, 0.15), (0.88, 0.15)],
                    r=0.022, parent=root)
    else:
        inner.filigree(f"fp{k}_fil", scroll_pair(0.0, 1.0, mirror=(k == 2)), radius=FIL_R,
                       parent=root)
        inner.studs(f"fp{k}_dots", [(0.5, 0.9), (0.15 if k == 0 else 0.85, 0.12)], r=0.022,
                    parent=root)
for i in (5, 1):    # front chamfers
    sp = sub_panel(walls[i], 0.1, 0.9, 0.1, 0.9)
    sp.filigree(f"ch{i}_fil", [fit(scroll_c(0, 0, 1), 0.05, 0.05, 0.95, 0.95, flip_x=(i == 1))],
                radius=FIL_R, parent=root)
for i in (2, 4):    # sloped side wings: framed plates of scrollwork, rune inlays
    w = walls[i]
    # u runs front->back on the left wall and back->front on the right one
    segs = ((0.0, 0.34), (0.34, 0.67), (0.67, 1.0))
    for k, (u0, u1) in enumerate(segs):
        sp = sub_panel(w, u0 + 0.02, u1 - 0.02, 0.1, 0.9)
        frame(sp, f"side{i}_{k}_frame", 0.032)
        inner = sub_panel(sp, 0.08, 0.92, 0.08, 0.92)
        if k == 1:   # rune inlay that pulses with every hammer blow
            for gi, stroke in enumerate(RUNES[(i // 2) % len(RUNES)]):
                glow(curve_obj(f"side{i}_rune{gi}", [inner.at(0.15 + 0.7 * u, 0.1 + 0.8 * v, 0.006)
                                                     for u, v in stroke], RUNE, 0.014, root))
            inner.studs(f"side{i}_{k}_gem", [(0.5, 0.0), (0.5, 1.0)], r=0.025, mat=RUBY,
                        parent=root)
        else:
            inner.filigree(f"side{i}_{k}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0,
                                                        flip_x=(k % 2 == 1))],
                           radius=FIL_R * 0.85, parent=root)
            inner.studs(f"side{i}_{k}_gem", [(0.5, 0.5)], r=0.03, mat=RUBY, parent=root)
    for k, u in enumerate((0.34, 0.67)):
        rail(f"side{i}_rib{k}", [Vector(w.at(u, 0, 0.03)), Vector(w.at(u, 1, 0.03))], 0.055)

# --- rim: a wide gold band around the opening, studded --------------------------
outer = T3
inner_pts = [Vector((x, y, zr(y))) for x, y in
             ((x0 + 0.06, y0), (x1 - 0.06, y0), (x1, y0 + 0.06), (x1, y1), (x0, y1),
              (x0, y0 + 0.06))]
bm = bmesh.new()
vo = [bm.verts.new(tuple(v)) for v in outer]
vi = [bm.verts.new(tuple(v)) for v in inner_pts]
for i in range(6):
    j = (i + 1) % 6
    bm.faces.new((vo[i], vo[j], vi[j], vi[i]))
rim_o = mesh_obj("rim_band", bm, GOLD, root, bevel=0.01)
rim_o.modifiers.new("solid", "SOLIDIFY").thickness = 0.045
rail("rim_outer", [t + Vector((0, 0, 0.02)) for t in T3], 0.075, closed=True)
rail("rim_inner", [v + Vector((0, 0, 0.02)) for v in inner_pts], 0.06, closed=True)
for i in range(6):
    a, b = outer[i].lerp(inner_pts[i], 0.5), outer[(i + 1) % 6].lerp(inner_pts[(i + 1) % 6], 0.5)
    n = max(2, int((b - a).length / 0.22))
    for k in range(n + 1):
        p = a.lerp(b, k / n) + Vector((0, 0, 0.03))
        sphere(f"rim_stud{i}_{k}", 0.03 if k % 2 else 0.036, tuple(p),
               RUBY if k % 2 else GOLD, root)

# --- bay: inner walls and organic floor ---------------------------------------
bay_corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
for i in range(4):
    (ax, ay), (bx, by) = bay_corners[i], bay_corners[(i + 1) % 4]
    p = Panel((ax, ay, FLOOR_Z), (bx, by, FLOOR_Z), (bx, by, zr(by)), (ax, ay, zr(ay)))
    p.build(f"bay_wall{i}", BRONZE, thick=0.03, parent=root)
# back wall faces the camera: framed purple panel with scrollwork behind the gears
back = Panel((x1 - 0.02, y1 - 0.025, FLOOR_Z + 0.25), (x0 + 0.02, y1 - 0.025, FLOOR_Z + 0.25),
             (x0 + 0.02, y1 - 0.025, zr(y1)), (x1 - 0.02, y1 - 0.025, zr(y1)))
# Panel faces -y when built from these corners; build mirrored so it faces the bay
back = Panel(back.c[1], back.c[0], back.c[3], back.c[2])
back.build("back_panel", PURPLE, parent=root)
frame(back, "back_frame", 0.03, inset=0.02)
bf = sub_panel(back, 0.05, 0.95, 0.12, 0.92)
bf.filigree("back_fil", [fit(scroll_c(0, 0, 1), u, 0.0, u + 0.16, 1.0, flip_x=(k % 2 == 1))
                         for k, u in enumerate((0.0, 0.21, 0.42, 0.63, 0.84))],
            radius=FIL_R * 0.8, parent=root)

bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=100, y_segments=100, size=1.0)
bmesh.ops.scale(bm, vec=((x1 - x0) / 2, (y1 - y0) / 2, 1), verts=bm.verts)
floor = mesh_obj("bay_floor", bm, FLESH, root, smooth=True)
floor.location = ((x0 + x1) / 2, (y0 + y1) / 2, FLOOR_Z)
tex = bpy.data.textures.new("flesh_disp", "VORONOI")
tex.noise_scale = 0.32
dm = floor.modifiers.new("disp", "DISPLACE")
dm.texture = tex
dm.strength = 0.09
dm.texture_coords = "OBJECT"

# filigree corner brackets reaching into the opening (partly veil the bay)
for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
    sx, sy = (1 if cx < 0 else -1), (1 if cy < 0 else -1)
    size = 0.34 if cy < 0 else 0.26
    pts = [(cx + sx * size, cy), (cx, cy), (cx, cy + sy * size)]
    rail(f"bracket{cx}{cy}", [(x, y, zr(y) + 0.03) for x, y in pts], 0.035)
    curl = fit(scroll_c(0, 0, 1), 0, 0, size * 0.8, size * 0.8)
    rail(f"bracket_curl{cx}{cy}", [(cx + sx * u, cy + sy * v, zr(cy + sy * v) + 0.03)
                                   for u, v in curl], 0.025)
    sphere(f"bracket_gem{cx}{cy}", 0.035, (cx + sx * 0.05, cy + sy * 0.05, zr(cy) + 0.07),
           RUBY, root)

# --- crest: heavy scrolls rising along the back edge ----------------------------
crest = Panel((-XT, YB + 0.02, ZB), (XT, YB + 0.02, ZB), (XT, YB + 0.02, ZB + 0.32),
              (-XT, YB + 0.02, ZB + 0.32))
S = []
for u0, m in ((0.0, False), (0.82, True)):
    S.append(fit(scroll_c(0, 0, 1), u0, 0.0, u0 + 0.18, 1.0, flip_x=m))
S += [[(0.18, 0.12), (0.82, 0.12)]]
crest.filigree("crest", S, radius=0.045, lift=0.0, parent=root)
crest.studs("crest_gem", [(0.5, 0.12)], r=0.04, mat=RUBY, parent=root)
for side in (-1, 1):   # curls rising off the back corners
    rail(f"curl{side}", [(side * x, YB - 0.05, z) for x, z in
                         fit(scroll_c(0, 0, 1), XT - 0.32, ZB, XT, ZB + 0.24,
                             flip_x=True)], 0.045)

# ----------------------------------------------------------------------------
# Mechanism
# ----------------------------------------------------------------------------
#
# Everything in the bay does a job, driven from one source:
#   steam cylinder (west) -> piston -> connecting rod -> crank on the gold gear
#   gold gear -> steel gear -> bevel pair -> camshaft across the bay
#   camshaft cams    -> trip hammer forging a glowing shard on an anvil
#   camshaft crank   -> four-bar linkage tipping a potion flask into a cauldron
#   every hammer blow charges the conjuration orb hovering above the machine.
# All joints are solved per frame from fixed link lengths, so nothing stretches.
# Coordinates in this section are world coordinates.

mech = bpy.data.objects.new("mechanism", None)
link(mech, root)
animated = []   # (obj, fn(obj, phase)) evaluated per frame
ry = (0, math.radians(90), 0)      # cylinder axis along x
rx = (math.radians(90), 0, 0)      # cylinder axis along y

TOOTH_C, GAP_C = 0.34, 0.84   # tooth / gap centre as a fraction of the pitch


def mesh_angle(alpha, teeth, gap):
    """Rotation that puts a tooth (or gap) centre of a gear at angle alpha."""
    return alpha - TAU * (GAP_C if gap else TOOTH_C) / teeth


# --- gear train --------------------------------------------------------------
# One loop = one revolution of the gold gear = one steam stroke cycle. Per loop
# the steel gear turns 2 rev and the dark gear 1/2, so teeth and spokes all
# repeat exactly; teeth move 0.375 pitches per frame at 64 frames (no strobing).
GZ = 1.25                                # gear plane, about rim height
G1_T, G1_R = 24, 0.42
G2_T = 12
G2_R = G1_R * G2_T / G1_T
P_T, P_R = 8, G1_R * 8 / G1_T            # pinion under the gold gear
G4_T = 16
G4_R = P_R * G4_T / P_T
SHAFT_Y, SHAFT_Z = -0.08, GZ + 0.24      # camshaft across the bay (axis x)

G1 = gear("gear_gold", G1_T, G1_R, 0.065, GOLD, mech, spokes=6)
G1.location = (-0.2, 0.5, GZ)
pin_gear = gear("gear_pinion", P_T, P_R, 0.05, STEEL, G1, spokes=0, inner=0.4)
pin_gear.location = (0, 0, -0.13)
CRANK1_R = 0.16
CRANK_DZ = 0.2      # crank pin height above the gear, clear of the rim
cyl("gold_crank_boss", 0.06, CRANK_DZ, (0, 0, CRANK_DZ / 2), BRASS, G1, verts=24)
box("gold_crank_web", (CRANK1_R, 0.07, 0.035), (CRANK1_R / 2, 0, CRANK_DZ - 0.02), STEEL, G1,
    bevel=0.01)
cyl("gold_crank_pin", 0.035, 0.08, (CRANK1_R, 0, CRANK_DZ + 0.01), BRASS, G1, verts=16)
for k in range(G1_T):   # crown teeth on the gear's face drive the back gear train
    a = TAU * (k + TOOTH_C) / G1_T
    box(f"gold_crown{k}", (0.05, 0.035, 0.04), (0.37 * math.cos(a), 0.37 * math.sin(a), 0.05),
        GOLD, G1, rot=(0, 0, a), bevel=0.006)
cyl("gear_gold_shaft", 0.045, GZ - FLOOR_Z, (G1.location.x, G1.location.y,
                                              (GZ + FLOOR_Z) / 2), STEEL, mech)

g2_dy = SHAFT_Y - G1.location.y
alpha2 = math.atan2(g2_dy, math.sqrt((G1_R + G2_R) ** 2 - g2_dy ** 2))
G2 = gear("gear_steel", G2_T, G2_R, 0.055, STEEL, mech, spokes=4)
G2.location = (G1.location.x + (G1_R + G2_R) * math.cos(alpha2), SHAFT_Y, GZ)
cyl("gear_steel_shaft", 0.035, GZ - FLOOR_Z, (G2.location.x, SHAFT_Y, (GZ + FLOOR_Z) / 2),
    STEEL, mech)
th1 = mesh_angle(alpha2, G1_T, gap=False)
th2 = mesh_angle(alpha2 + math.pi, G2_T, gap=True)
beta = th1 + TAU * (3 + TOOTH_C) / P_T   # a pinion tooth sits there in this phase
G4 = gear("gear_dark", G4_T, G4_R, 0.05, BRONZE, mech, spokes=4)
G4.location = (G1.location.x + (P_R + G4_R) * math.cos(beta),
               G1.location.y + (P_R + G4_R) * math.sin(beta), GZ - 0.13)
th4 = mesh_angle(beta + math.pi, G4_T, gap=True)
cyl("gear_dark_shaft", 0.035, 0.3, (G4.location.x, G4.location.y, GZ - 0.25), STEEL, mech)


def spin(o, ph, th0, ratio):
    o.rotation_euler = (0, 0, th0 + ratio * ph)


animated += [
    (G1, lambda o, ph: spin(o, ph, th1, 1)),
    (G2, lambda o, ph: spin(o, ph, th2, -G1_T / G2_T)),
    (G4, lambda o, ph: spin(o, ph, th4, -P_T / G4_T)),
]


def gold_pin(ph):
    a = th1 + ph
    return Vector((G1.location.x + CRANK1_R * math.cos(a),
                   G1.location.y + CRANK1_R * math.sin(a), GZ + CRANK_DZ))


# --- bevel pair: steel gear shaft (vertical) -> camshaft (along x), 2:1 ------
def bevel(name, teeth, r, parent, mat):
    """Bevel gear as a toothed cone frustum, axis local z, wide end at z=0."""
    outer = []
    for k in range(teeth):
        a, da = TAU * k / teeth, TAU / teeth
        for frac, rad in ((0.0, 0.92), (0.18, 1.06), (0.5, 1.06), (0.68, 0.92)):
            outer.append((r * rad * math.cos(a + frac * da), r * rad * math.sin(a + frac * da)))
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, 0)) for x, y in outer]
    hi = [bm.verts.new((x * 0.55, y * 0.55, r * 0.45)) for x, y in outer]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(len(outer)):
        j = (i + 1) % len(outer)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    o = mesh_obj(name, bm, mat, parent, bevel=0.004)
    o.data.shade_flat()
    return o


BEV_S, BEV_B = 0.08, 0.16
small_bev = bpy.data.objects.new("bevel_small", None)
link(small_bev, G2)
small_bev.location = (0, 0, SHAFT_Z - BEV_B - GZ - 0.04)
bevel("bevel_small_g", 8, BEV_S, small_bev, BRASS)
cyl("gear_steel_upshaft", 0.03, small_bev.location.z, (0, 0, small_bev.location.z / 2),
    STEEL, G2)

camshaft = bpy.data.objects.new("camshaft", None)
link(camshaft, mech)
camshaft.location = (0, SHAFT_Y, SHAFT_Z)
camshaft.rotation_mode = "XYZ"
cyl("camshaft_rod", 0.04, 1.9, (0, 0, 0), STEEL, camshaft, rot=ry, verts=20)
big_bev = bpy.data.objects.new("bevel_big", None)
link(big_bev, camshaft)
big_bev.location = (G2.location.x + BEV_S + 0.04, 0, 0)
big_bev.rotation_euler = (0, math.radians(-90), 0)   # cone points back to the axis
bevel("bevel_big_g", 16, BEV_B, big_bev, GOLD)
# camshaft turns once per loop (steel gear 2 rev, 2:1 bevel). The steel gear
# runs clockwise seen from above and the big bevel sits east of it, so the
# camshaft turns backwards about +x: its front side moves up.
animated.append((camshaft, lambda o, ph: setattr(o, "rotation_euler", (-ph, 0, 0))))
for sx in (-1, 1):   # pillow blocks standing on the bay floor
    box(f"cam_block{sx}", (0.12, 0.16, SHAFT_Z - FLOOR_Z),
        (sx * 0.9, SHAFT_Y, (SHAFT_Z + FLOOR_Z) / 2 - 0.02), BRONZE, mech, bevel=0.015)
    cyl(f"cam_block_cap{sx}", 0.07, 0.14, (sx * 0.9, SHAFT_Y, SHAFT_Z), BRASS, mech, rot=ry)

# --- steam engine: cylinder on the west flank, crosshead in guides -----------
ENG_Y, ENG_Z = G1.location.y, GZ + CRANK_DZ
CYL_X0, CYL_X1 = -1.32, -0.92
cyl("steam_cyl", 0.14, CYL_X1 - CYL_X0, ((CYL_X0 + CYL_X1) / 2, ENG_Y, ENG_Z + 0.02), BRASS,
    mech, rot=ry, verts=48)
for kk, x in enumerate((CYL_X0 + 0.02, (CYL_X0 + CYL_X1) / 2, CYL_X1 - 0.02)):
    cyl(f"steam_cyl_band{kk}", 0.155, 0.04, (x, ENG_Y, ENG_Z + 0.02), GOLD, mech, rot=ry, verts=48)
for kk in range(8):
    a = TAU * kk / 8
    sphere(f"steam_cyl_bolt{kk}", 0.014, (CYL_X1 + 0.005, ENG_Y + 0.12 * math.cos(a),
                                          ENG_Z + 0.02 + 0.12 * math.sin(a)), GOLD, mech)
box("steam_cyl_saddle", (0.3, 0.26, ENG_Z - zr(ENG_Y) - 0.08),
    ((CYL_X0 + CYL_X1) / 2, ENG_Y, (ENG_Z + zr(ENG_Y)) / 2 - 0.06), BRONZE, mech, bevel=0.015)
GUIDE_X0, GUIDE_X1 = CYL_X1, -0.42
for sy in (-1, 1):
    box(f"guide{sy}", (GUIDE_X1 - GUIDE_X0, 0.03, 0.05),
        ((GUIDE_X0 + GUIDE_X1) / 2, ENG_Y + sy * 0.065, ENG_Z), STEEL, mech, bevel=0.006)
box("guide_end", (0.04, 0.17, 0.05), (GUIDE_X1, ENG_Y, ENG_Z), STEEL, mech, bevel=0.006)
ROD_L = 0.5
piston = cyl("piston_rod", 0.025, 1.0, (0, ENG_Y, ENG_Z), STEEL, mech, rot=ry)
crosshead = box("crosshead", (0.1, 0.1, 0.07), (0, ENG_Y, ENG_Z), BRASS, mech, bevel=0.01)

# steam in from the west connection, exhaust puffs up behind the cylinder
PIPE_Z = 0.45        # height of the west / east fluid connections
pipe = [(-HALF - 0.08, 0.0, PIPE_Z), (-1.42, 0.0, PIPE_Z), (-1.36, 0.08, 0.9),
        (-1.42, 0.3, 1.38), (-1.42, ENG_Y, ENG_Z + 0.02), (CYL_X0 - 0.01, ENG_Y, ENG_Z + 0.02)]
curve_obj("steam_pipe", pipe, BRASS, 0.06, mech, res=4)
cyl("pipe_flange_w", 0.085, 0.05, (-HALF - 0.02, 0.0, PIPE_Z), GOLD, mech, rot=ry)
cyl("pipe_flange_c", 0.085, 0.04, (CYL_X0 - 0.03, ENG_Y, ENG_Z + 0.02), GOLD, mech, rot=ry)

# --- stamp hammer ---------------------------------------------------------------
# A stamp mill: a cam on the camshaft catches the tappet collar on the stamp's
# stem, lifts it slowly and lets it drop onto the shard on the anvil.
HX = -0.7                                    # stamp plane, clear of the gold gear
STEM_Y = SHAFT_Y - 0.34                      # stem sits just clear of the cam's sweep
ANVIL = Vector((HX, STEM_Y, 0.95))           # anvil face (the shard lies on it)
WORK_TOP = ANVIL.z + 0.045
HEAD_H = 0.2
TAPPET_REACH = 0.21                          # collar reaches back over the cam
TAPPET_Y = STEM_Y + TAPPET_REACH             # contact line (y) on the cam
CAM_R0, CAM_LIFT = 0.07, 0.3
STRIKE_SHIFT = 0.25                          # strikes at frames N/8 and 5N/8
TAPPET_Z0 = SHAFT_Z + 0.04                   # collar underside with the stamp down


def cam_r(psi):
    """Two-lobe snail cam: base-circle dwell (stamp resting on the anvil), slow
    rise, then a sudden drop (radius at cam angle psi)."""
    u = (2 * psi / TAU - STRIKE_SHIFT) % 1.0
    return CAM_R0 + CAM_LIFT * max(0.0, (u - 0.3) / 0.7)


CAM_N = 240
CAM_PROFILE = [(cam_r(TAU * i / CAM_N + 1e-4), TAU * i / CAM_N) for i in range(CAM_N)]


def stamp_lift(ph):
    """Highest point of the turned cam on the collar's contact line."""
    d = TAPPET_Y - SHAFT_Y
    top = -1.0
    pts = [(r * math.cos(a - ph), r * math.sin(a - ph)) for r, a in CAM_PROFILE]
    for (ya, za), (yb, zb) in zip(pts, pts[1:] + pts[:1]):
        if (ya - d) * (yb - d) <= 0 and ya != yb:
            z = za + (zb - za) * (d - ya) / (yb - ya)
            top = max(top, z)
    return max(0.0, SHAFT_Z + top - TAPPET_Z0)


def strike_age(f):
    """Frames since the last hammer blow."""
    return min((f - s) % N for s in STRIKES)


_lifts = [stamp_lift(TAU * f / N) for f in range(N)]
STRIKES = [f for f in range(N) if _lifts[f - 1] > 0.08 and _lifts[f] < 0.02]
assert len(STRIKES) == 2, STRIKES
print("STRIKES", STRIKES)

cam = bpy.data.objects.new("stamp_cam", None)
link(cam, camshaft)
cam.location = (HX, 0, 0)
bm = bmesh.new()
lo = [bm.verts.new((-0.035, r * math.cos(a), r * math.sin(a))) for r, a in CAM_PROFILE]
hi = [bm.verts.new((0.035, r * math.cos(a), r * math.sin(a))) for r, a in CAM_PROFILE]
bm.faces.new(lo)
bm.faces.new(list(reversed(hi)))
for i in range(CAM_N):
    j = (i + 1) % CAM_N
    bm.faces.new((lo[i], hi[i], hi[j], lo[j]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh_obj("stamp_cam_body", bm, STEEL, cam, bevel=0.006).data.shade_flat()
cyl("stamp_cam_hub", 0.07, 0.1, (0, 0, 0), BRASS, cam, rot=ry)

stamp = bpy.data.objects.new("stamp", None)
link(stamp, mech)
stamp.location = (HX, STEM_Y, WORK_TOP)       # origin = face of the stamp head
STEM_TOP = 1.05
cyl("stamp_stem", 0.03, STEM_TOP - HEAD_H, (0, 0, (STEM_TOP + HEAD_H) / 2), STEEL, stamp)
box("stamp_head", (0.26, 0.2, HEAD_H - 0.05), (0, 0, (HEAD_H + 0.05) / 2), STEEL, stamp,
    bevel=0.02)
box("stamp_shoe", (0.16, 0.13, 0.05), (0, 0, 0.025), BRONZE, stamp, bevel=0.008)
for zz in (HEAD_H - 0.03, 0.08):
    box(f"stamp_band{zz}", (0.275, 0.215, 0.035), (0, 0, zz), GOLD, stamp, bevel=0.008)
tz = TAPPET_Z0 - WORK_TOP
box("stamp_tappet", (0.07, TAPPET_REACH + 0.06, 0.05), (0, TAPPET_REACH / 2 + 0.01, tz + 0.025),
    BRASS, stamp, bevel=0.01)
cyl("stamp_collar", 0.05, 0.08, (0, 0, tz + 0.03), BRASS, stamp, verts=24)
cyl("stamp_cap", 0.045, 0.04, (0, 0, STEM_TOP), GOLD, stamp, verts=24)
animated.append((stamp, lambda o, ph: setattr(o, "location", (HX, STEM_Y, WORK_TOP + stamp_lift(ph)))))
# guide frame: two posts with guide bars the stem slides through
GUIDE_TOP = TAPPET_Z0 + CAM_LIFT + 0.17   # above the tappet's highest point
for sx in (-1, 1):
    box(f"stamp_post{sx}", (0.04, 0.05, GUIDE_TOP - FLOOR_Z),
        (HX + sx * 0.14, STEM_Y - 0.05, (GUIDE_TOP + FLOOR_Z) / 2), BRONZE, mech, bevel=0.008)
box("stamp_guide", (0.32, 0.06, 0.04), (HX, STEM_Y - 0.05, GUIDE_TOP), STEEL, mech, bevel=0.008)
cyl("stamp_bush", 0.045, 0.05, (HX, STEM_Y, GUIDE_TOP), BRASS, mech, verts=20)

# anvil standing on the bay floor, shard being forged on top
box("anvil_foot", (0.3, 0.26, 0.12), (HX, ANVIL.y, FLOOR_Z + 0.06), STEEL, mech, bevel=0.02)
box("anvil_waist", (0.16, 0.15, ANVIL.z - FLOOR_Z - 0.2), (HX, ANVIL.y, (ANVIL.z + FLOOR_Z) / 2),
    STEEL, mech, bevel=0.015)
box("anvil_face", (0.32, 0.2, 0.09), (HX, ANVIL.y, ANVIL.z - 0.045), STEEL, mech, bevel=0.015)
cyl("anvil_horn", 0.065, 0.16, (HX + 0.23, ANVIL.y, ANVIL.z - 0.05), STEEL, mech, rot=ry,
    r2=0.015)

# --- potion pour: crank on the camshaft tips a flask over the cauldron -------
PX = 0.5                                       # pour mechanism plane
CRANK2_R, LEVER_R, COUPLER = 0.07, 0.1, 0.24
FPIV = Vector((PX, SHAFT_Y - 0.23, SHAFT_Z - 0.14))   # flask pivot (axis x)
crank2 = bpy.data.objects.new("pour_crank", None)
link(crank2, camshaft)
crank2.location = (PX - 0.06, 0, 0)
cyl("pour_crank_disc", 0.1, 0.03, (0, 0, 0), BRASS, crank2, rot=ry, verts=32)
cyl("pour_crank_pin", 0.02, 0.06, (0, 0, CRANK2_R), STEEL, crank2, rot=ry)


def pour_pin(ph):
    # point (0, 0, r) on the camshaft, rotated by -ph about +x
    return Vector((PX - 0.06, SHAFT_Y + CRANK2_R * math.sin(ph), SHAFT_Z + CRANK2_R * math.cos(ph)))


def lever_q(t):
    # lever end; t measured in the (forward = -y, up = z) plane
    return Vector((PX - 0.06, FPIV.y - LEVER_R * math.cos(t), FPIV.z + LEVER_R * math.sin(t)))


def track_lever():
    """Rocker angle for every frame, following one branch continuously."""
    out, prev = [], math.radians(135)
    for f in range(N + 1):
        pin = pour_pin(TAU * f / N)
        g = lambda t: (lever_q(t) - pin).length - COUPLER
        roots, grid = [], [prev + i * 0.005 for i in range(-400, 401)]
        for a, b in zip(grid, grid[1:]):
            if g(a) * g(b) <= 0:
                for _ in range(40):
                    m = (a + b) / 2
                    a, b = (a, m) if g(a) * g(m) <= 0 else (m, b)
                roots.append((a + b) / 2)
        assert roots, "pour linkage cannot close"
        prev = min(roots, key=lambda t: abs(t - prev))
        out.append(prev)
    assert abs(out[0] - out[-1]) < 1e-3, "pour linkage does not loop"
    return out[:N]


LEVER_T = track_lever()
T_UP = max(LEVER_T)            # flask upright; tips forward as the lever swings down


def flask_tilt(f):
    return T_UP - LEVER_T[f % N]


flask = bpy.data.objects.new("flask", None)
link(flask, mech)
flask.location = FPIV
glass_o = sphere("flask_glass", 0.085, (PX - FPIV.x, 0, 0.1), GLASS, flask, segs=24)
cyl("flask_neck", 0.03, 0.12, (PX - FPIV.x, 0, 0.21), GLASS, flask, verts=20)
cyl("flask_lip", 0.038, 0.015, (PX - FPIV.x, 0, 0.27), BRASS, flask, verts=20)
liquid = sphere("flask_liquid", 0.072, (PX - FPIV.x, 0, 0.09), POTION, flask, segs=20)
liquid.scale = (1, 1, 0.8)
glow(liquid)
cradle = mesh_obj("flask_cradle", ring_mesh(
    [(0.092 * math.cos(TAU * i / 32), 0.092 * math.sin(TAU * i / 32)) for i in range(32)],
    [(0.08 * math.cos(TAU * i / 32), 0.08 * math.sin(TAU * i / 32)) for i in range(32)],
    -0.015, 0.015), GOLD, flask, smooth=True)
cradle.location = (PX - FPIV.x, 0, 0.1)
cyl("flask_axle", 0.025, 0.3, (0.05, 0, 0), STEEL, flask, rot=ry)
for sx in (-0.1, 0.2):
    box(f"flask_post{sx}", (0.04, 0.08, FPIV.z - FLOOR_Z),
        (PX + sx, FPIV.y, (FPIV.z + FLOOR_Z) / 2), BRONZE, mech, bevel=0.008)
flask.rotation_mode = "XYZ"
MOUTH_LOCAL = Vector((PX - FPIV.x, 0, 0.28))

CAUL = Vector((PX, -0.66, 0.95))               # cauldron rim centre
caul_out = [(0.17 * math.cos(TAU * i / 48), 0.17 * math.sin(TAU * i / 48)) for i in range(48)]
caul_in = [(0.14 * math.cos(TAU * i / 48), 0.14 * math.sin(TAU * i / 48)) for i in range(48)]
o = mesh_obj("cauldron_rim", ring_mesh(caul_out, caul_in, -0.03, 0.0), GOLD, mech, smooth=True,
             bevel=0.01)
o.location = CAUL
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.17)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.0], context="VERTS")
o = mesh_obj("cauldron_bowl", bm, STEEL, mech, smooth=True)
o.location = CAUL - Vector((0, 0, 0.02))
o.modifiers.new("solid", "SOLIDIFY").thickness = 0.02
for k in range(3):
    a = TAU * k / 3 + 0.5
    box(f"cauldron_leg{k}", (0.03, 0.03, CAUL.z - FLOOR_Z - 0.1),
        (CAUL.x + 0.13 * math.cos(a), CAUL.y + 0.13 * math.sin(a), (CAUL.z + FLOOR_Z) / 2 - 0.08),
        BRONZE, mech)
brew = cyl("cauldron_brew", 0.14, 0.01, CAUL - Vector((0, 0, 0.04)), BREW, mech, verts=48)
glow(brew)
caul_light = bpy.data.lights.new("cauldron_light", "POINT")
caul_light.color = (1.0, 0.35, 0.85)
caul_light.shadow_soft_size = 0.1
o = bpy.data.objects.new("cauldron_light", caul_light)
link(o, mech)
o.location = CAUL + Vector((0, 0, 0.12))

STREAM = []


def pose_stream(f):
    for o in STREAM:
        bpy.data.objects.remove(o, do_unlink=True)
    STREAM.clear()
    tilt = flask_tilt(f)
    flow = max(0.0, min(1.0, (tilt - math.radians(70)) / math.radians(20)))
    if flow <= 0:
        return
    mouth = FPIV + Matrix.Rotation(tilt, 3, "X") @ MOUTH_LOCAL
    end = Vector((CAUL.x, CAUL.y + 0.04, CAUL.z - 0.04))
    pts = []
    for i in range(13):
        t = i / 12
        # leaves the lip moving forward, then falls (parabola)
        p = mouth.lerp(end, t)
        p.y += -0.05 * math.sin(math.pi * t)
        p.z += 0.03 * math.sin(math.pi * t) * (1 - t)
        pts.append(tuple(p))
    o = curve_obj("pour_stream", pts, POTION, 0.018 * flow, mech, res=2,
                  taper=lambda t: 1.0 - 0.45 * t)
    STREAM.append(glow(o))


# --- conjuration orb hovering over the machine --------------------------------
ORB_C = Vector((0.72, 0.8, 2.0))    # hovering over the potion tank
orb = bpy.data.objects.new("orb", None)
link(orb, mech)
orb_core = sphere("orb_core", 0.13, (0, 0, 0), ORB, orb, segs=32)
glow(orb_core)
rings = []
for k, (rx_, ry_) in enumerate(((math.radians(70), 0), (math.radians(-35), math.radians(60)))):
    holder = bpy.data.objects.new(f"orb_gimbal{k}", None)
    link(holder, orb)
    holder.rotation_euler = (rx_, ry_, 0)
    ring = mesh_obj(f"orb_ring{k}", ring_mesh(
        [(0.2 * math.cos(TAU * i / 48), 0.2 * math.sin(TAU * i / 48)) for i in range(48)],
        [(0.182 * math.cos(TAU * i / 48), 0.182 * math.sin(TAU * i / 48)) for i in range(48)],
        -0.012, 0.012), GOLD, holder, smooth=True, bevel=0.004)
    for g in range(4):
        sphere(f"orb_ring{k}_gem{g}", 0.02, (0.191 * math.cos(TAU * g / 4),
                                            0.191 * math.sin(TAU * g / 4), 0), RUBY, ring)
    rings.append(ring)
animated.append((rings[0], lambda o, ph: setattr(o, "rotation_euler", (0, 0, ph))))
animated.append((rings[1], lambda o, ph: setattr(o, "rotation_euler", (0, 0, -2 * ph))))
orb_light_d = bpy.data.lights.new("orb_light", "POINT")
orb_light_d.color = (1.0, 0.3, 0.9)
orb_light_d.shadow_soft_size = 0.1
orb_light = bpy.data.objects.new("orb_light", orb_light_d)
link(orb_light, orb)
animated.append((orb, lambda o, ph: setattr(o, "location", ORB_C + Vector((
    0.06 * math.cos(ph), 0.06 * math.sin(ph), 0.035 * math.sin(2 * ph))))))

# --- sparks off the anvil -----------------------------------------------------
SPARKS = []


def pose_sparks(f):
    for o in SPARKS:
        bpy.data.objects.remove(o, do_unlink=True)
    SPARKS.clear()
    age = strike_age(f)
    if age > 3:
        return
    rng = random.Random(f - age)
    origin = Vector((HX, ANVIL.y, WORK_TOP + 0.01))
    for k in range(18):
        a = rng.uniform(0, TAU)
        v = Vector((math.cos(a), math.sin(a) * 0.8, rng.uniform(0.6, 1.4))) * rng.uniform(0.18, 0.32)
        t0, t1 = age * 0.6, age * 0.6 + 0.5
        p0 = origin + v * t0 + Vector((0, 0, -0.08 * t0 * t0))
        p1 = origin + v * t1 + Vector((0, 0, -0.08 * t1 * t1))
        o = curve_obj(f"spark{k}", [tuple(p0), tuple(p1)], SPARK, 0.011 * (1 - age / 4), mech)
        SPARKS.append(glow(o))


def pose_magic(f):
    """Blow-synchronised emission: shard glows hot, orb and runes flare."""
    age = strike_age(f)
    flare = math.exp(-age / 5.0)
    SHARD_EM.default_value = 1.0 + 5.0 * flare
    ORB_EM.default_value = 0.6 + 2.2 * flare
    RUNE_EM.default_value = 0.15 + 0.6 * math.exp(-age / 9.0)
    orb_light_d.energy = 1.5 + 6.0 * flare
    caul_light.energy = 0.8 + 0.4 * math.sin(TAU * f / N * 3)
    flash_d.energy = 6.0 * math.exp(-age / 1.5)


flash_d = bpy.data.lights.new("strike_flash", "POINT")
flash_d.color = (1.0, 0.45, 0.75)
flash_d.shadow_soft_size = 0.05
o = bpy.data.objects.new("strike_flash", flash_d)
link(o, mech)
o.location = (HX, ANVIL.y - 0.15, WORK_TOP + 0.12)

shard = bpy.data.objects.new("shard", None)
link(shard, mech)
shard.location = (HX, ANVIL.y, ANVIL.z)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.045, radius2=0.0, depth=0.16)
o = mesh_obj("shard_crystal", bm, SHARD, shard)
o.rotation_euler = (0, math.radians(90), 0.4)
o.location = (0, 0, 0.03)
o.data.shade_flat()
glow(o)

# coil spools in the back corners
for kk, ((sx, sy), sr, nrings) in enumerate((((-0.74, 0.92), 0.16, 4),)):
    sp = bpy.data.objects.new(f"spool{kk}", None)
    link(sp, mech)
    sp.location = (sx, sy, FLOOR_Z)
    top_z = zr(sy) + 0.14 - FLOOR_Z
    ring_o = [(sr * math.cos(TAU * i / 64), sr * math.sin(TAU * i / 64)) for i in range(64)]
    ring_i = [(sr * 0.52 * math.cos(TAU * i / 64), sr * 0.52 * math.sin(TAU * i / 64))
              for i in range(64)]
    for r_ in range(nrings):
        z = top_z - 0.065 - r_ * 0.07
        mesh_obj(f"spool{kk}_ring{r_}", ring_mesh(ring_o, ring_i, z, z + 0.06),
                 GOLD if r_ == 0 else BRASS, sp, smooth=True, bevel=0.022, segs=3)
    cyl(f"spool{kk}_core", sr * 0.55, top_z, (0, 0, top_z / 2 - 0.03), BRONZE, sp)
    th = cyl(f"spool{kk}_throat", sr * 0.4, 0.02, (0, 0, top_z - 0.015), RUNE, sp)
    glow(th)

# --- back gear train, face-on on the back wall ---------------------------------
# A pinion riding on the gold gear's crown teeth turns a shaft running back to
# gear A; A drives B and C. All teeth pass at the gold gear's rate (24/loop).
BACK_Y = y1 - 0.09


def upright_gear(name, teeth, r, x, z, spokes, mat):
    g = gear(name, teeth, r, 0.06, mat, mech, spokes=spokes)
    g.location = (x, BACK_Y, z)
    g.rotation_mode = "ZXY"          # spin about the gear's axis, then stand it up
    for k in range(spokes):          # rubies on the rim, like the reference's gears
        a = TAU * (k + 0.5) / spokes
        sphere(f"{name}_gem{k}", 0.022, (r * 0.78 * math.cos(a), r * 0.78 * math.sin(a), 0.04),
               RUBY, g)
    return g


PIN_T, PIN_R = 12, G1_R * 12 / G1_T
pin2 = gear("crown_pinion", PIN_T, PIN_R, 0.05, STEEL, mech, spokes=0, inner=0.45)
pin2.location = (G1.location.x, G1.location.y + 0.36, GZ + 0.07 + PIN_R)
pin2.rotation_mode = "ZXY"
A_T, B_T, C_T = 12, 24, 15
A_R, B_R, C_R = (G1_R * t / G1_T for t in (A_T, B_T, C_T))
AX, AZ = G1.location.x, pin2.location.z
GA = upright_gear("back_gear_a", A_T, A_R, AX, AZ, 4, BRASS)
phi_b, phi_c = math.radians(-12), math.radians(196)
GB = upright_gear("back_gear_b", B_T, B_R, AX + (A_R + B_R) * math.cos(phi_b),
                  AZ + (A_R + B_R) * math.sin(phi_b), 6, GOLD)
GC = upright_gear("back_gear_c", C_T, C_R, AX + (A_R + C_R) * math.cos(phi_c),
                  AZ + (A_R + C_R) * math.sin(phi_c), 5, GOLD)
cyl("back_shaft", 0.03, BACK_Y - pin2.location.y, (AX, (BACK_Y + pin2.location.y) / 2, AZ),
    STEEL, mech, rot=rx)
for g in (GB, GC):
    cyl(f"{g.name}_boss", 0.05, 0.12, (g.location.x, BACK_Y + 0.05, g.location.z), BRASS, mech,
        rot=rx)
# Gears stand up by -90 deg about x: local angle a points along (cos a, -sin a)
# in world (x, z). Mesh phases are set in that local frame.
ta = mesh_angle(-phi_b, A_T, gap=False)
tb = mesh_angle(-phi_b + math.pi, B_T, gap=True)
ta_c = mesh_angle(-phi_c, A_T, gap=False)
tc = mesh_angle(-phi_c + math.pi, C_T, gap=True) + (ta - ta_c) * (-A_T / C_T)
UP = math.radians(-90)
# crown at the gold gear's back rim moves -x; the pinion's underside must too,
# which makes it turn positively about +y (= its local z after standing up)
animated += [
    (pin2, lambda o, ph: setattr(o, "rotation_euler", (UP, 0, 2 * ph))),
    (GA, lambda o, ph: setattr(o, "rotation_euler", (UP, 0, ta + 2 * ph))),
    (GB, lambda o, ph: setattr(o, "rotation_euler", (UP, 0, tb - 2 * ph * A_T / B_T))),
    (GC, lambda o, ph: setattr(o, "rotation_euler", (UP, 0, tc - 2 * ph * A_T / C_T))),
]

# --- floor machinery: gearboxes and pipework under the moving parts ------------
def bolted_box(name, size, loc, mat=BRONZE):
    box(name, size, loc, mat, mech, bevel=0.02)
    sx, sy, sz = size
    for u in (-1, 1):
        for v in (-1, 1):
            sphere(f"{name}_bolt{u}{v}", 0.018, (loc[0] + u * (sx / 2 - 0.035),
                                                 loc[1] + v * (sy / 2 - 0.035), loc[2] + sz / 2),
                   GOLD, mech)


bolted_box("gearbox_gold", (0.42, 0.36, GZ - 0.2 - FLOOR_Z),
           (G1.location.x, G1.location.y, (GZ - 0.2 + FLOOR_Z) / 2))
bolted_box("gearbox_steel", (0.26, 0.24, GZ - 0.12 - FLOOR_Z),
           (G2.location.x, SHAFT_Y, (GZ - 0.12 + FLOOR_Z) / 2))
bolted_box("pour_base", (0.36, 0.22, 0.25), (PX + 0.05, FPIV.y + 0.02, FLOOR_Z + 0.125))
bolted_box("tank_base", (0.38, 0.38, 0.12), (0.72, 0.78, FLOOR_Z + 0.06), mat=STEEL)
for k, (a, b) in enumerate((((-0.95, 0.15), (0.95, 0.15)), ((-0.95, -0.85), (0.2, -0.85)),
                            ((0.32, -0.3), (0.32, 0.6)))):
    curve_obj(f"floor_pipe{k}", [(a[0], a[1], FLOOR_Z + 0.07), (b[0], b[1], FLOOR_Z + 0.07)],
              BRASS if k % 2 else COPPER, 0.045, mech)
    for t in (0.2, 0.5, 0.8):
        cyl(f"floor_pipe{k}_band{t}", 0.058, 0.03,
            (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, FLOOR_Z + 0.07), GOLD, mech,
            rot=ry if abs(b[0] - a[0]) > abs(b[1] - a[1]) else rx)

# --- potion tank, fed from the east fluid connection, refilling the flask ------
TANK = Vector((0.72, 0.78, FLOOR_Z))
TANK_R, TANK_H = 0.15, 1.0
tank = bpy.data.objects.new("tank", None)
link(tank, mech)
tank.location = TANK
cyl("tank_glass", TANK_R, TANK_H, (0, 0, TANK_H / 2), GLASS, tank, verts=40)
tank_liq = cyl("tank_liquid", TANK_R - 0.015, TANK_H * 0.72, (0, 0, TANK_H * 0.38), TANK_LIQ,
               tank, verts=40)
glow(tank_liq)
for zz in (0.0, TANK_H):
    cyl(f"tank_cap{zz}", TANK_R + 0.03, 0.06, (0, 0, zz), GOLD, tank, verts=40)
for k in range(4):
    a = TAU * k / 4 + math.pi / 4
    box(f"tank_strap{k}", (0.025, 0.025, TANK_H), ((TANK_R + 0.01) * math.cos(a),
                                                   (TANK_R + 0.01) * math.sin(a), TANK_H / 2),
        GOLD, tank, rot=(0, 0, a), bevel=0.005)
sphere("tank_finial", 0.04, (0, 0, TANK_H + 0.07), RUBY, tank)
BUBBLES = []
for k in range(7):
    b = sphere(f"bubble{k}", 0.018 + 0.006 * (k % 3), (0, 0, 0), POTION, tank)
    glow(b)
    BUBBLES.append((b, k))


def bubble_pos(o, ph, k):
    rise = ((ph / TAU) * (2 + k % 2) + k * 0.37) % 1.0      # integer laps per loop
    a = k * 2.4
    o.location = (0.07 * math.cos(a), 0.07 * math.sin(a), 0.08 + rise * TANK_H * 0.62)


for b, k in BUBBLES:
    animated.append((b, lambda o, ph, k=k: bubble_pos(o, ph, k)))

curve_obj("pipe_east", [(HALF + 0.08, 0.0, PIPE_Z), (1.42, 0.0, PIPE_Z), (1.36, 0.1, 0.9),
                        (1.2, 0.45, 1.45), (0.95, 0.72, 1.7), (0.78, TANK.y, 1.7),
                        (TANK.x, TANK.y, TANK.z + TANK_H + 0.02)], BRASS, 0.05, mech, res=4)
cyl("pipe_flange_e", 0.085, 0.05, (HALF + 0.02, 0.0, PIPE_Z), GOLD, mech, rot=ry)

# hose from the tank to a nozzle over the flask's upright position
NOZZLE = FPIV + MOUTH_LOCAL + Vector((0, 0, 0.2))
hose = [(TANK.x - 0.12, TANK.y - 0.05, TANK.z + 0.25)]
for t in (0.25, 0.5, 0.75, 1.0):
    p = Vector(hose[0]).lerp(NOZZLE + Vector((0, 0, 0.12)), t)
    p.z += 0.35 * math.sin(math.pi * t) + (0.12 if t == 1.0 else 0)
    hose.append(tuple(p))
hose.append(tuple(NOZZLE + Vector((0, 0, 0.12))))
hose.append(tuple(NOZZLE))
curve_obj("hose", hose, BRONZE, 0.03, mech, res=3)
for t in (0.2, 0.5, 0.8):
    i = int(t * (len(hose) - 2))
    p = Vector(hose[i]).lerp(Vector(hose[i + 1]), 0.5)
    sphere(f"hose_ferrule{t}", 0.04, tuple(p), GOLD, mech)
cyl("nozzle", 0.03, 0.08, NOZZLE + Vector((0, 0, 0.04)), BRASS, mech, r2=0.045)
cyl("nozzle_valve", 0.045, 0.04, NOZZLE + Vector((0, 0, 0.1)), GOLD, mech)

# flask level: falls while pouring, rises under the nozzle; scaled so it closes
_pour = [max(0.0, min(1.0, (flask_tilt(f) - math.radians(70)) / math.radians(20)))
         for f in range(N)]
_fill = [1.0 if flask_tilt(f) < math.radians(8) else 0.0 for f in range(N)]
_k = sum(_pour) / sum(_fill)
_c, _acc = [], 0.0
for f in range(N):
    _c.append(_acc)
    _acc += _k * _fill[f] - _pour[f]
_lo, _hi = min(_c), max(_c)
LEVEL = [0.3 + 0.7 * (c - _lo) / (_hi - _lo) for c in _c]
REFILL = []


def pose_refill(f):
    for o in REFILL:
        bpy.data.objects.remove(o, do_unlink=True)
    REFILL.clear()
    s = 0.45 + 0.55 * LEVEL[f % N]
    liquid.scale = (s, s, 0.8 * s)
    liquid.location.z = 0.1 - 0.07 * (1 - s)
    if _fill[f % N]:
        top = NOZZLE - Vector((0, 0, 0.01))
        bottom = FPIV + Matrix.Rotation(flask_tilt(f), 3, "X") @ (MOUTH_LOCAL - Vector((0, 0, 0.1)))
        o = curve_obj("refill_stream", [tuple(top), tuple(bottom)], POTION, 0.014, mech,
                      taper=lambda t: 1.0 - 0.3 * t)
        REFILL.append(glow(o))


# cauldron drains to the anvil, where the brew quenches the forged shard
curve_obj("drain", [(CAUL.x, CAUL.y, CAUL.z - 0.18), (CAUL.x, CAUL.y, FLOOR_Z + 0.06),
                    (CAUL.x - 0.3, CAUL.y + 0.1, FLOOR_Z + 0.05),
                    (HX + 0.15, STEM_Y - 0.02, FLOOR_Z + 0.05)], BRASS, 0.03, mech)

LINK = []


def bar(name, a, b, w=0.06, h=0.04, mat=None):
    """Flat link with rounded ends between two points."""
    A, B = Vector(a), Vector(b)
    o = bpy.data.objects.new(name, None)
    link(o, mech)
    o.location = A
    d = B - A
    o.rotation_euler = d.to_track_quat("X", "Z").to_euler()
    box(name + "_bar", (d.length, w, h), (d.length / 2, 0, 0), mat or STEEL, o, bevel=0.008)
    for e, x in (("a", 0), ("b", d.length)):
        cyl(name + "_end" + e, w / 2 + 0.008, h + 0.01, (x, 0, 0), BRASS, o, verts=20)
    return o


def pose_linkage(f):
    for o in LINK:
        for c in o.children_recursive:
            bpy.data.objects.remove(c, do_unlink=True)
        bpy.data.objects.remove(o, do_unlink=True)
    LINK.clear()
    ph = TAU * f / N
    # slider-crank: crosshead slides along x, rod to the gold gear's crank pin
    pin = gold_pin(ph)
    dy = pin.y - ENG_Y
    xh = pin.x - math.sqrt(ROD_L ** 2 - dy ** 2)
    crosshead.location.x = xh
    piston.location.x = (CYL_X1 - 0.1 + xh) / 2
    piston.scale.z = (xh - CYL_X1 + 0.1)        # unit-length rod scaled to fit
    LINK.append(bar("conrod", (xh, ENG_Y, ENG_Z), (pin.x, pin.y, ENG_Z), w=0.07, h=0.05))
    # pour four-bar: crank pin -> coupler -> lever on the flask axle
    t = LEVER_T[f % N]
    q = lever_q(t)
    LINK.append(bar("pour_coupler", pour_pin(ph), q, w=0.04, h=0.03))
    LINK.append(bar("pour_lever", (PX - 0.06, FPIV.y, FPIV.z), q, w=0.05, h=0.035,
                    mat=BRASS))
    flask.rotation_euler = (flask_tilt(f), 0, 0)


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

rig = setup_scene(frame_w=4.0, frame_h=4.0, frame_cy=0.42)


def pose(f):
    ph = TAU * f / N
    for o, fn in animated:
        fn(o, ph)
    pose_linkage(f)
    pose_stream(f)
    pose_refill(f)
    pose_sparks(f)
    pose_magic(f)


render_passes(rig, pose, extra_lights=(orb_light_d, caul_light, flash_d),
              name="conjuration-machine")
