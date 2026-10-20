"""
Procedural Blender model + Factorio render of the rune transformer.

The rune transformer is a 2x2 furnace that turns one rune word into the next
one of its chain (rune-chains.lua). The model shows exactly that: a crucible
of molten rune-stone on a hearth, and behind it a carousel of the nine rune
glyph plates (A I L M R S T U V, the letters of the rune items). A Geneva
drive indexes the carousel one plate at a time; while a plate dwells in front
of the crucible, a beam rises from the melt into its glyph and the melt takes
on that glyph's colour - the rune has been rewritten.

    blender -b --factory-startup -P blender/rune_transformer.py -- \
        --out graphics/generated/rune-transformer [--preview --frame 0,8]

Passes (see render_all): `main` is the machine at rest (embers only, used as
the furnace's animation, which freezes while idle), `work` is the same frame
fully lit; their difference becomes `glow`, the additive working
visualisation, like vanilla's steel-furnace-working.png. Then stitch with
blender/stitch.py. World units are Factorio tiles; the entity is 2x2 centred
on the origin, +y is north, +z is up.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

# 9 indexes of 16 frames: the carousel turns once per loop
FPI = 16                     # frames per index (= one driver revolution)
args = fblend.parse_args("rune-transformer", frames=9 * FPI, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT
assert N % FPI == 0 and (N // FPI) % 9 == 0, "loop must index the carousel a whole turn"

# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------

SLATE = paint("slate", (0.075, 0.055, 0.085), (0.012, 0.008, 0.014), noise_scale=14.0,
              bump=0.5, bump_scale=40.0, dirt=0.1, hammered=True)
DECK = paint("deck", (0.22, 0.045, 0.17), (0.02, 0.004, 0.016), noise_scale=9.0,
             bump=0.6, bump_scale=25.0, dirt=0.35, hammered=True)

# The nine rune words, in carousel order, coloured like their item icons.
GLYPHS = (
    ("A", (0.15, 0.5, 1.0)),     # aqua
    ("S", (0.08, 0.9, 0.75)),    # spiritus
    ("I", (1.0, 0.38, 0.06)),    # ignis
    ("L", (1.0, 0.82, 0.45)),    # lux
    ("V", (0.35, 0.95, 0.2)),    # vitae
    ("T", (1.0, 0.22, 0.9)),     # tempus
    ("U", (0.8, 0.78, 0.95)),    # umbra
    ("M", (0.55, 0.28, 1.0)),    # mortis
    ("R", (0.85, 0.45, 0.18)),   # terra
)
NP = len(GLYPHS)

# Letter strokes in the unit square (u right, v up), chunky enough for 64 px/tile.
LETTERS = {
    "A": [[(0.12, 0.0), (0.5, 1.0), (0.88, 0.0)], [(0.28, 0.38), (0.72, 0.38)]],
    "I": [[(0.5, 0.0), (0.5, 1.0)], [(0.25, 1.0), (0.75, 1.0)], [(0.25, 0.0), (0.75, 0.0)]],
    "L": [[(0.28, 1.0), (0.28, 0.0), (0.85, 0.0)]],
    "M": [[(0.1, 0.0), (0.1, 1.0), (0.5, 0.4), (0.9, 1.0), (0.9, 0.0)]],
    "S": [[(0.82, 0.86), (0.66, 0.99), (0.34, 0.99), (0.17, 0.83), (0.22, 0.62),
           (0.5, 0.51), (0.78, 0.4), (0.84, 0.18), (0.66, 0.01), (0.34, 0.01), (0.16, 0.14)]],
    "T": [[(0.1, 1.0), (0.9, 1.0)], [(0.5, 1.0), (0.5, 0.0)]],
    "U": [[(0.18, 1.0), (0.18, 0.32), (0.28, 0.08), (0.5, 0.0), (0.72, 0.08), (0.82, 0.32),
           (0.82, 1.0)]],
    "R": [[(0.22, 0.0), (0.22, 1.0), (0.6, 1.0), (0.78, 0.9), (0.78, 0.62), (0.6, 0.52),
           (0.22, 0.52)], [(0.48, 0.52), (0.82, 0.0)]],
    "V": [[(0.1, 1.0), (0.5, 0.0), (0.9, 1.0)]],
}

GLYPH_MATS = [emitter(f"glyph_{c}", col, 0.3, base=(0.05, 0.04, 0.05)) for c, col in GLYPHS]


def flowing(name, color, strength, scale=9.0):
    """Molten emissive surface: noise-modulated emission whose texture origin
    is moved along a circle per frame (seamless), with a settable colour."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    L(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 5.0
    L(mp.outputs["Vector"], nz.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["From Min"].default_value = 0.3
    rr.inputs["From Max"].default_value = 0.7
    rr.inputs["To Min"].default_value = 0.35
    rr.inputs["To Max"].default_value = 1.6
    L(nz.outputs["Fac"], rr.inputs["Value"])
    rgb = nt.nodes.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = (*color, 1)
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L(rgb.outputs[0], mul.inputs["A"])
    L(rr.outputs["Result"], mul.inputs["B"])
    # hot spots run towards white
    hot = nt.nodes.new("ShaderNodeMix")
    hot.data_type = "RGBA"
    hot.inputs["B"].default_value = (1, 0.9, 1, 1)
    hf = nt.nodes.new("ShaderNodeMapRange")
    hf.inputs["From Min"].default_value = 0.62
    hf.inputs["From Max"].default_value = 0.85
    hf.inputs["To Max"].default_value = 0.6
    L(nz.outputs["Fac"], hf.inputs["Value"])
    L(hf.outputs["Result"], hot.inputs["Factor"])
    L(mul.outputs["Result"], hot.inputs["A"])
    L(hot.outputs["Result"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Base Color"].default_value = (0.03, 0.015, 0.03, 1)   # cooled crust
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.3
    return m, bsdf.inputs["Emission Strength"], rgb.outputs[0], mp.inputs["Location"]


MELT, MELT_EM, MELT_COL, MELT_UV = flowing("melt", GLYPHS[0][1], 1.0, scale=14.0)
HEARTH, HEARTH_EM, _, HEARTH_UV = flowing("hearth", (0.85, 0.12, 0.7), 1.0, scale=7.0)
ORB, ORB_EM = emitter("orb", (0.85, 0.12, 0.8), 1.0, base=(0.5, 0.03, 0.42), glass=True)
VIAL, VIAL_EM = emitter("vial", (0.6, 0.1, 0.75), 0.6, base=(0.3, 0.03, 0.35))


def beam_mat():
    """Light shaft: emission added to full transparency, so it never occludes."""
    m = bpy.data.materials.new("beam")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], add.inputs[0])
    nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs[0])
    return m, em.inputs["Strength"], em.inputs["Color"]


BEAM, BEAM_EM, BEAM_COL = beam_mat()

# ----------------------------------------------------------------------------
# The body
# ----------------------------------------------------------------------------
#
# A squat 2x2 hearth like the vanilla steel furnace: sloped side walls that
# read as wings, the deck rising slightly towards the back, the tall parts
# (glyph carousel, chimney, mana vial) at the back, the hearth window in the
# south face.

root = bpy.data.objects.new("rune_transformer", None)
link(root)
# The model below is laid out on a 1.4 tile grid and scaled up by K: like the
# vanilla steel furnace (2.05 tiles wide on screen) it overhangs its 1.4 tile
# collision box and fills the 2x2 footprint, at sprite scale 0.5.
K = 1.4
root.scale = (K, K, K)

HALF = 0.66          # half footprint of the plinth
CH = 0.14            # front corner chamfer of the plinth
PLINTH_H = 0.07
XT = 0.56            # half width of the rim (side walls slope in to here)
TC = 0.12            # front corner chamfer of the rim
YF, ZF = -0.52, 0.5   # rim front edge
YB, ZB = 0.6, 0.58     # rim back edge
RIM_W = 0.075
DECK_Z = 0.5        # flat deck plate inside the rim


def zr(y):
    """Height of the (gently) sloped rim at y."""
    return ZF + (y - YF) / (YB - YF) * (ZB - ZF)


bot2d = [(-HALF + CH, -HALF), (HALF - CH, -HALF), (HALF, -HALF + CH),
         (HALF, HALF), (-HALF, HALF), (-HALF, -HALF + CH)]
top2d = [(-XT + TC, YF), (XT - TC, YF), (XT, YF + TC), (XT, YB), (-XT, YB), (-XT, YF + TC)]
B3 = [Vector((x, y, PLINTH_H)) for x, y in bot2d]
T3 = [Vector((x, y, zr(y))) for x, y in top2d]


def prism(name, poly, z0, z1, mat, bevel=0.01, parent=None):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent or root, bevel=bevel)
    o.data.shade_flat()
    return o


def rail(name, pts3, r, closed=False, mat=None, parent=None):
    return curve_obj(name, [tuple(p) for p in pts3], mat or GOLD, r, parent or root,
                     closed=closed)


FIL_R = 0.022        # raised scrollwork (thinner than the 3x3's: smaller panels)

# --- plinth: dark bronze band, gold top rail, rivets ---------------------------
prism("plinth", bot2d, 0, PLINTH_H, BRONZE)
rail("plinth_rail", [(x, y, PLINTH_H) for x, y in bot2d], 0.04, closed=True)
rail("plinth_foot", [(x * 1.006, y * 1.006, 0.015) for x, y in bot2d], 0.02, closed=True)
for fi in (5, 0, 1, 2):
    a, b = Vector((*bot2d[fi], 0)), Vector((*bot2d[(fi + 1) % 6], 0))
    nrm = Vector((b.y - a.y, -(b.x - a.x), 0)).normalized()
    count = {0: 8, 2: 6}.get(fi, 2)
    for k in range(count):
        p = a.lerp(b, (k + 0.5) / count) + nrm * 0.004
        sphere(f"rivet{fi}_{k}", 0.017, (p.x, p.y, PLINTH_H * 0.5), GOLD, root)

# --- walls ----------------------------------------------------------------------
walls = {}
for i in range(6):
    j = (i + 1) % 6
    p = Panel(B3[i], B3[j], T3[j], T3[i])
    p.build(f"wall{i}", PURPLE, parent=root)
    walls[i] = p
for i in range(6):   # heavy gold ribs on the corner edges
    rail(f"corner_rib{i}", [B3[i] + Vector((0, 0, 0.015)), T3[i]], 0.05)

front = walls[0]
# hearth window in the middle of the south face; scrollwork either side
WIN_U0, WIN_U1, WIN_V0, WIN_V1 = 0.29, 0.71, 0.2, 0.8
win = sub_panel(front, WIN_U0, WIN_U1, WIN_V0, WIN_V1)
# recessed firebox: dark throat, glowing coals at the back, grille in front
throat = sub_panel(front, WIN_U0 + 0.01, WIN_U1 - 0.01, WIN_V0 + 0.02, WIN_V1 - 0.02)
fire_o = throat.build("hearth_fire", HEARTH, thick=0.005, parent=root)
fire_o.location = tuple(front.n * 0.004)     # just proud of the wall, behind the grille
glow(fire_o)
gold_frame(win, "hearth_frame", r=0.034, parent=root)
for k in range(5):   # grille bars, partly veiling the fire
    u = (k + 1) / 6
    rail(f"hearth_bar{k}", [win.at(u, 0.0, 0.03), win.at(u, 1.0, 0.03)], 0.012, mat=BRASS)
rail("hearth_crossbar", [win.at(0.0, 0.5, 0.035), win.at(1.0, 0.5, 0.035)], 0.011, mat=BRASS)
# lintel with ruby keystone, sill underneath
win.studs("hearth_key", [(0.5, 1.12)], r=0.03, mat=RUBY, parent=root)
rail("hearth_sill", [win.at(-0.08, -0.1, 0.03), win.at(1.08, -0.1, 0.03)], 0.026)
for k, (u0, u1, m) in enumerate(((0.03, WIN_U0 - 0.05, False), (WIN_U1 + 0.05, 0.97, True))):
    sp = sub_panel(front, u0, u1, 0.12, 0.88)
    gold_frame(sp, f"fp{k}_frame", r=0.022, parent=root)
    inner = sub_panel(sp, 0.1, 0.9, 0.1, 0.9)
    big = scroll_c(0, 0, 1, up=True)
    small = scroll_c(0, 0, 1, up=False)
    inner.filigree(f"fp{k}_fil", [fit(big, 0.0, 0.0, 1.0, 1.0, flip_x=m),
                                  fit(small, 0.0, 0.0, 0.55, 0.5, flip_x=not m)],
                   radius=FIL_R, parent=root)
    inner.studs(f"fp{k}_gem", [(0.5, 0.5)], r=0.022, mat=RUBY, parent=root)
for i in (5, 1):     # front chamfers: a single big scroll each
    sp = sub_panel(walls[i], 0.12, 0.88, 0.14, 0.86)
    sp.filigree(f"ch{i}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0, flip_x=(i == 1))],
                radius=FIL_R, parent=root)
for i in (2, 4):     # side wings: two framed scroll plates with a rune inlay between
    w = walls[i]
    for k, (u0, u1) in enumerate(((0.02, 0.36), (0.36, 0.64), (0.64, 0.98))):
        sp = sub_panel(w, u0 + 0.02, u1 - 0.02, 0.12, 0.88)
        gold_frame(sp, f"side{i}_{k}_frame", r=0.022, parent=root)
        inner = sub_panel(sp, 0.1, 0.9, 0.1, 0.9)
        if k == 1:
            rune(inner, f"side{i}_rune", 1 + i // 2, radius=0.011, parent=root)
        else:
            inner.filigree(f"side{i}_{k}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0,
                                                     flip_x=(k == 2))],
                           radius=FIL_R * 0.9, parent=root)
            inner.studs(f"side{i}_{k}_gem", [(0.5, 0.5)], r=0.02, mat=RUBY, parent=root)

# --- rim and deck -----------------------------------------------------------------
inner_pts = [Vector((x, y, zr(y))) for x, y in
             ((-XT + RIM_W + TC * 0.6, YF + RIM_W), (XT - RIM_W - TC * 0.6, YF + RIM_W),
              (XT - RIM_W, YF + RIM_W + TC * 0.6), (XT - RIM_W, YB - RIM_W),
              (-XT + RIM_W, YB - RIM_W), (-XT + RIM_W, YF + RIM_W + TC * 0.6))]
bm = bmesh.new()
vo = [bm.verts.new(tuple(v)) for v in T3]
vi = [bm.verts.new(tuple(v)) for v in inner_pts]
for i in range(6):
    j = (i + 1) % 6
    bm.faces.new((vo[i], vo[j], vi[j], vi[i]))
rim_o = mesh_obj("rim_band", bm, GOLD, root, bevel=0.008)
rim_o.modifiers.new("solid", "SOLIDIFY").thickness = 0.035
rail("rim_outer", [t + Vector((0, 0, 0.015)) for t in T3], 0.045, closed=True)
rail("rim_inner", [v + Vector((0, 0, 0.012)) for v in inner_pts], 0.032, closed=True)
for i in range(6):
    a = T3[i].lerp(inner_pts[i], 0.5)
    b = T3[(i + 1) % 6].lerp(inner_pts[(i + 1) % 6], 0.5)
    n = max(1, int((b - a).length / 0.16))
    for k in range(n + 1):
        p = a.lerp(b, k / n) + Vector((0, 0, 0.022))
        sphere(f"rim_stud{i}_{k}", 0.02 if k % 2 else 0.024, tuple(p),
               RUBY if k % 2 else GOLD, root)
# deck plate inside the rim (its inner walls are the rim's thickness)
prism("deck", [(v.x, v.y) for v in inner_pts], DECK_Z - 0.1, DECK_Z, DECK)
# gold bolt heads in a band just inside the rim, so the deck isn't a flat fill
for i in range(6):
    a = inner_pts[i].lerp(inner_pts[(i + 1) % 6], 0.0)
    b = inner_pts[(i + 1) % 6]
    n = max(1, int((b - a).length / 0.09))
    for k in range(n):
        p = a.lerp(b, (k + 0.5) / n)
        p = Vector((p.x * 0.93, p.y * 0.93 + (0.02 if p.y > 0 else 0.0), DECK_Z + 0.004))
        sphere(f"deck_bolt{i}_{k}", 0.012, tuple(p), GOLD, root, segs=8)

# ----------------------------------------------------------------------------
# Mechanism
# ----------------------------------------------------------------------------
#
#   hidden mana motor -> driver (constant speed, 1 rev per index)
#   driver crank pin  -> 9-slot Geneva wheel: carousel advances 1/9 turn,
#                        then is held by the locking disc while it dwells
#   carousel          -> nine rune glyph plates; the one dwelling in front of
#                        the crucible is "read": a beam from the melt lights
#                        it and the melt turns that glyph's colour
#   mana vial         -> pipe -> crucible (the melt's supply), hearth heats it

mech = bpy.data.objects.new("mechanism", None)
link(mech, root)
animated = []        # (obj, fn(obj, f))

W = Vector((0.0, 0.2))                 # carousel / Geneva wheel axis (xy)
GENEVA_C = 0.34                        # wheel-driver centre distance
G_SLOT = TAU / NP                      # 40 degrees per index
G_A = GENEVA_C * math.sin(math.pi / NP)        # crank pin radius (tangential entry)
G_B = GENEVA_C * math.cos(math.pi / NP)        # slot mouth radius
G_RW = G_B + 0.006                     # wheel outer radius
G_PIN_R = 0.022
G_SLOT_W = G_PIN_R + 0.006             # slot half width
G_SLOT_IN = GENEVA_C - G_A - 0.04      # slot bottom radius (pin's deepest point + clearance)
G_LOCK_R = G_A - G_PIN_R - 0.035       # locking disc radius (small: sturdy arms)
G_ARC_R = G_LOCK_R + 0.006             # concave seats on the wheel
GZ = DECK_Z + 0.075                    # Geneva plane (wheel mid-plane)
G_T = 0.04                             # wheel thickness
DRV_ANG = math.radians(-140)           # driver sits front-left of the wheel
D = W + GENEVA_C * Vector((math.cos(DRV_ANG), math.sin(DRV_ANG)))
U_DW = (W - D).normalized()            # driver -> wheel
ANG_DW = math.atan2(U_DW.y, U_DW.x)
ANG_WD = ANG_DW + math.pi
ENGAGE = math.pi / 2 - math.pi / NP    # pin is in a slot for |phi| < 70 deg


def boolean_cut(obj, cutters):
    """Bake obj minus the cutters into obj's mesh (exact solver). Cutters are
    built in obj's local frame, so they share its parent."""
    for c in cutters:
        c.parent = obj.parent
        mod = obj.modifiers.new("cut_" + c.name, "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.operand_type = "OBJECT"
        mod.object = c
        mod.solver = "EXACT"
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    obj.data = me
    for c in cutters:
        bpy.data.objects.remove(c, do_unlink=True)
    me.shade_flat()
    return obj


def cutter_cyl(name, r, h, xy, verts=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    link(o)
    o.location = (xy[0], xy[1], 0)
    return o


def cutter_box(name, size, xy, rot):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    link(o)
    o.location = (xy[0], xy[1], 0)
    o.rotation_euler = (0, 0, rot)
    return o


# --- Geneva wheel (local frame: slot k at angle k * 40 deg) --------------------
wheel = bpy.data.objects.new("geneva", None)
link(wheel, mech)
wheel.location = (W.x, W.y, GZ)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=144, radius1=G_RW, radius2=G_RW, depth=G_T)
wheel_body = mesh_obj("geneva_body", bm, BRASS, wheel)
cut = []
for k in range(NP):
    s = k * G_SLOT
    L = G_RW + 0.05 - G_SLOT_IN
    mid = G_SLOT_IN + L / 2
    cut.append(cutter_box(f"gslot{k}", (L, 2 * G_SLOT_W, G_T * 3),
                          (mid * math.cos(s), mid * math.sin(s)), s))
    cut.append(cutter_cyl(f"gslot_end{k}", G_SLOT_W, G_T * 3,
                          (G_SLOT_IN * math.cos(s), G_SLOT_IN * math.sin(s)), 24))
    a = s + G_SLOT / 2
    cut.append(cutter_cyl(f"gseat{k}", G_ARC_R, G_T * 3,
                          (GENEVA_C * math.cos(a), GENEVA_C * math.sin(a)), 64))
boolean_cut(wheel_body, cut)
wheel_body.modifiers.new("bevel", "BEVEL").width = 0.004
for k in range(NP):   # gold bosses and rubies between the slots
    a = (k + 0.5) * G_SLOT
    r = (G_SLOT_IN + GENEVA_C - G_ARC_R) / 2 - 0.015
    cyl(f"geneva_boss{k}", 0.024, G_T + 0.012, (r * math.cos(a), r * math.sin(a), 0), GOLD,
        wheel, verts=16)
    sphere(f"geneva_gem{k}", 0.014, (r * math.cos(a), r * math.sin(a), G_T / 2 + 0.008), RUBY,
           wheel)
cyl("geneva_hub", 0.16, G_T + 0.02, (0, 0, 0), BRONZE, wheel, verts=48)
cyl("geneva_shaft_bearing", 0.07, GZ - DECK_Z, (W.x, W.y, (GZ + DECK_Z) / 2), BRONZE, mech)


# --- driver: crank pin + locking disc (local frame: pin at angle 0) -------------
driver = bpy.data.objects.new("driver", None)
link(driver, mech)
driver.location = (D.x, D.y, GZ)
DRV_BASE_R = G_A + 0.045
cyl("driver_base", DRV_BASE_R, 0.025, (0, 0, -G_T / 2 - 0.016), BRONZE, driver, verts=48)
rail("driver_base_rim", [(DRV_BASE_R * math.cos(TAU * i / 48), DRV_BASE_R * math.sin(TAU * i / 48),
                          -G_T / 2 - 0.004) for i in range(48)], 0.012, closed=True,
     parent=driver)
for s in range(3):     # spokes under the locking disc (3-fold: no strobing)
    a = TAU * (s + 0.5) / 3
    box(f"driver_spoke{s}", (DRV_BASE_R * 0.9, 0.03, 0.02),
        (DRV_BASE_R * 0.45 * math.cos(a), DRV_BASE_R * 0.45 * math.sin(a), -G_T / 2 - 0.002),
        GOLD, driver, rot=(0, 0, a), bevel=0.004)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=G_LOCK_R, radius2=G_LOCK_R,
                      depth=G_T)
lock = mesh_obj("driver_lock", bm, STEEL, driver)
# crescent relief towards the pin lets the wheel's tips pass while it turns
boolean_cut(lock, [cutter_cyl("lock_relief", G_RW + 0.012, G_T * 3, (GENEVA_C, 0), 128)])
lock.modifiers.new("bevel", "BEVEL").width = 0.004
# the arm runs above the wheel's bosses and gems, under the carousel struts
ARM_Z = G_T / 2 + 0.035
box("driver_arm", (G_A, 0.05, 0.02), (G_A / 2, 0, ARM_Z), GOLD, driver, bevel=0.006)
cyl("driver_pin", G_PIN_R, ARM_Z + G_T / 2, (G_A, 0, (ARM_Z - G_T / 2) / 2), BRASS, driver,
    verts=20)
cyl("driver_pin_cap", G_PIN_R + 0.008, 0.012, (G_A, 0, ARM_Z + 0.014), GOLD, driver, verts=20)
cyl("driver_hub", 0.035, ARM_Z + G_T / 2 + 0.03, (0, 0, (ARM_Z + 0.03 - G_T / 2) / 2), GOLD,
    driver, verts=24)
sphere("driver_gem", 0.022, (0, 0, ARM_Z + 0.03), RUBY, driver)
cyl("driver_bearing", 0.06, GZ - DECK_Z - 0.03, (D.x, D.y, (GZ - 0.03 + DECK_Z) / 2), BRONZE,
    mech)


def drive_angle(f):
    """Driver angle relative to the driver->wheel line. Frame 0 has the pin
    pointing away (mid dwell), so the resting machine shows a locked plate."""
    return math.pi + TAU * f / FPI


def beta(phi):
    """Wheel slot angle (relative to the wheel->driver line) holding the pin
    at driver angle phi."""
    p = D + G_A * Vector((math.cos(ANG_DW + phi), math.sin(ANG_DW + phi)))
    a = math.atan2(p.y - W.y, p.x - W.x) - ANG_WD
    return (a + math.pi) % TAU - math.pi


B_IN, B_OUT = beta(-ENGAGE), beta(ENGAGE)
STEP = B_OUT - B_IN
assert abs(abs(STEP) - G_SLOT) < 1e-6, (STEP, G_SLOT)


def wheel_angle(f):
    """Geneva wheel rotation (world, radians, unwrapped) at frame f: an
    engaged slot follows the pin, otherwise the locking disc holds it."""
    tot = drive_angle(f)
    m = round(tot / TAU)
    phi = tot - TAU * m
    if abs(phi) < ENGAGE:
        b = beta(phi)
    else:
        b = B_OUT if phi > 0 else B_IN
    # slot 0 lies on the wheel->driver line at mid-engagement of index 0
    return ANG_WD + m * STEP + b


def motion(f):
    """0 while the carousel dwells, rising to 1 across an index move; plus
    the number of completed indexes."""
    tot = drive_angle(f)
    m = round(tot / TAU)
    phi = tot - TAU * m
    if abs(phi) < ENGAGE:
        return m, (beta(phi) - B_IN) / STEP
    return (m, 1.0) if phi > 0 else (m, 0.0)


for f in range(N):   # continuity check (no jumps) and loop closure
    da = wheel_angle(f + 1) - wheel_angle(f)
    assert abs(da) < G_SLOT * 0.5, (f, da)
assert abs(wheel_angle(N) - wheel_angle(0) - math.copysign(TAU, STEP)) < 1e-6

animated.append((wheel, lambda o, f: setattr(o, "rotation_euler", (0, 0, wheel_angle(f)))))
animated.append((driver, lambda o, f: setattr(o, "rotation_euler",
                                              (0, 0, ANG_DW + drive_angle(f)))))

# --- carousel of glyph plates on the wheel --------------------------------------
# A tapered nonagonal lantern: plates lean back by TILT so the front one faces
# the 45 degree camera. Plate i sits at local angle PLATE0 + i * 40 deg; PLATE0
# puts a plate square to the front (-y) whenever the wheel dwells.
RB, PH, TILT = 0.255, 0.24, math.radians(16)
RT = RB - PH * math.tan(TILT)
CZ0 = GZ + G_T / 2 + 0.11              # plate bottom
CZ1 = CZ0 + PH
FRONT = -math.pi / 2
PLATE0 = (FRONT - wheel_angle(0)) % G_SLOT
carousel = bpy.data.objects.new("carousel", None)
link(carousel, wheel)
cyl("carousel_column", 0.06, CZ1 - GZ - G_T / 2, (0, 0, (CZ1 - GZ + G_T / 2) / 2),
    BRONZE, carousel, verts=24)
plates = []
hw_b, hw_t = RB * math.tan(G_SLOT / 2), RT * math.tan(G_SLOT / 2)
zb, zt = CZ0 - GZ, CZ1 - GZ
for i, (ch, col) in enumerate(GLYPHS):
    th = PLATE0 + i * G_SLOT
    n = Vector((math.cos(th), math.sin(th), 0))
    t = Vector((-math.sin(th), math.cos(th), 0))
    c00 = n * RB - t * hw_b + Vector((0, 0, zb))
    c10 = n * RB + t * hw_b + Vector((0, 0, zb))
    c11 = n * RT + t * hw_t + Vector((0, 0, zt))
    c01 = n * RT - t * hw_t + Vector((0, 0, zt))
    p = Panel(c00, c10, c11, c01)
    p.build(f"plate{i}", SLATE, thick=0.03, parent=carousel)
    face = sub_panel(p, 0.14, 0.86, 0.1, 0.9)
    gold_frame(face, f"plate{i}_frame", r=0.011, parent=carousel)
    for si, stroke in enumerate(LETTERS[ch]):
        glow(curve_obj(f"plate{i}_glyph{si}",
                       [face.at(0.2 + 0.6 * u, 0.12 + 0.76 * v, 0.008) for u, v in stroke],
                       GLYPH_MATS[i][0], 0.014, carousel))
    plates.append(p)
# gold uprights on the plate joints, rings top and bottom, rubies at the foot
corners_b, corners_t = [], []
for i in range(NP):
    th = PLATE0 + (i - 0.5) * G_SLOT
    rb, rt = RB / math.cos(G_SLOT / 2), RT / math.cos(G_SLOT / 2)
    pb = Vector((rb * math.cos(th), rb * math.sin(th), zb))
    pt = Vector((rt * math.cos(th), rt * math.sin(th), zt))
    corners_b.append(pb)
    corners_t.append(pt)
    rail(f"car_post{i}", [pb + (pb - pt).normalized() * 0.02 + Vector((0, 0, -0.02)),
                          pt + Vector((0, 0, 0.03))], 0.02, parent=carousel)
    sphere(f"car_foot_gem{i}", 0.02, tuple(pb * 1.05 + Vector((0, 0, -0.03))), RUBY, carousel)
rail("car_ring_b", [c * 1.04 + Vector((0, 0, -0.012)) for c in corners_b], 0.026, closed=True,
     parent=carousel)
rail("car_ring_t", [c * 1.04 + Vector((0, 0, 0.012)) for c in corners_t], 0.026, closed=True,
     parent=carousel)
# skirt: struts from the hub out to the plate ring (the carousel rides the wheel)
for i in range(NP):
    th = PLATE0 + i * G_SLOT
    a = Vector((0.06 * math.cos(th), 0.06 * math.sin(th), G_T / 2 + 0.01))
    b = Vector((RB * 0.92 * math.cos(th), RB * 0.92 * math.sin(th), zb - 0.015))
    rail(f"car_strut{i}", [a, b], 0.014, mat=BRASS, parent=carousel)
# crown: gilded nonagonal lid, dome, scroll finials, spindle
prism("car_lid", [(c.x * 1.02, c.y * 1.02) for c in corners_t], zt, zt + 0.03, GOLD,
      parent=carousel)
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=RT * 0.78)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
dome = mesh_obj("car_dome", bm, PURPLE, carousel, smooth=True)
dome.location = (0, 0, zt + 0.03)
dome.scale = (1, 1, 0.55)
for i in range(NP):    # gold ribs over the dome
    th = PLATE0 + (i - 0.5) * G_SLOT
    pts = [((RT * 0.8 * math.cos(a)) * math.cos(th), (RT * 0.8 * math.cos(a)) * math.sin(th),
            zt + 0.03 + RT * 0.8 * 0.55 * math.sin(a)) for a in np.linspace(0, 1.4, 8)]
    rail(f"dome_rib{i}", pts, 0.011, parent=carousel)
    sphere(f"crown_ball{i}", 0.018, tuple(corners_t[i] * 1.04 + Vector((0, 0, 0.045))), GOLD,
           carousel)
DOME_TOP = zt + 0.03 + RT * 0.78 * 0.55
cyl("car_spindle", 0.018, 0.12, (0, 0, DOME_TOP + 0.05), GOLD, carousel, verts=16)
cyl("car_spindle_cup", 0.045, 0.02, (0, 0, DOME_TOP + 0.11), GOLD, carousel, verts=24, r2=0.06)

# --- the crucible in front of the reading position -------------------------------
CRU = Vector((0.0, -0.285, DECK_Z + 0.07))   # rim centre
CRU_R = 0.105
o = mesh_obj("crucible_rim", ring_mesh(
    [(CRU_R * math.cos(TAU * i / 48), CRU_R * math.sin(TAU * i / 48)) for i in range(48)],
    [((CRU_R - 0.025) * math.cos(TAU * i / 48), (CRU_R - 0.025) * math.sin(TAU * i / 48))
     for i in range(48)], -0.025, 0.0), GOLD, mech, smooth=True, bevel=0.008)
o.location = CRU
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=CRU_R)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1e-4], context="VERTS")
o = mesh_obj("crucible_bowl", bm, BRONZE, mech, smooth=True)
o.location = CRU
o.scale = (1, 1, 0.7)
o.modifiers.new("solid", "SOLIDIFY").thickness = 0.015
melt = cyl("crucible_melt", CRU_R - 0.022, 0.006, CRU - Vector((0, 0, 0.018)), MELT, mech,
           verts=48)
glow(melt)
for k in range(4):     # gold claw feet / tongs holding it over the hearth
    a = TAU * k / 4 + math.pi / 4
    p0 = CRU + Vector((CRU_R * math.cos(a), CRU_R * math.sin(a), -0.01))
    p1 = Vector((CRU.x + (CRU_R + 0.045) * math.cos(a), CRU.y + (CRU_R + 0.045) * math.sin(a),
                 DECK_Z + 0.03))
    rail(f"crucible_claw{k}", [p0, p0.lerp(p1, 0.5) + Vector((0, 0, 0.02)), p1], 0.014)
    sphere(f"crucible_claw_gem{k}", 0.014, tuple(p0 + Vector((0, 0, 0.012))), RUBY, mech)
# hearth grate around it, glowing through the slots
grate = cyl("hearth_grate", CRU_R + 0.06, 0.012, (CRU.x, CRU.y, DECK_Z + 0.006), HEARTH, mech,
            verts=48)
glow(grate)
for k in range(12):
    a = TAU * k / 12
    box(f"grate_bar{k}", (0.07, 0.016, 0.02),
        (CRU.x + (CRU_R + 0.03) * math.cos(a), CRU.y + (CRU_R + 0.03) * math.sin(a), DECK_Z + 0.016),
        STEEL, mech, rot=(0, 0, a), bevel=0.003)
rail("grate_ring", [(CRU.x + (CRU_R + 0.065) * math.cos(TAU * i / 48),
                     CRU.y + (CRU_R + 0.065) * math.sin(TAU * i / 48), DECK_Z + 0.014)
                    for i in range(48)], 0.014, closed=True, parent=mech)

# --- the reading beam: melt -> front plate's glyph ---------------------------------
front_plate_c = Vector(((RB + RT) / 2 * math.cos(FRONT) + W.x,
                        (RB + RT) / 2 * math.sin(FRONT) + W.y, (CZ0 + CZ1) / 2))
beam_pts = [CRU - Vector((0, 0, 0.015)), CRU + Vector((0, 0.03, 0.12)),
            front_plate_c - Vector((0, 0.04, 0.0))]
beam = curve_obj("beam", [tuple(p) for p in beam_pts], BEAM, 0.05, mech, res=4,
                 taper=lambda t: 1.0 - 0.45 * t)
glow(beam)

# --- rack of waiting rune tiles (front left), the transformer's input ----------
RACK = Vector((-0.33, -0.33, DECK_Z))
box("rack_tray", (0.17, 0.15, 0.025), RACK + Vector((0, 0, 0.0125)), GOLD, mech, bevel=0.006)
for k in range(3):
    tz = 0.025 + 0.012 + k * 0.026
    off = Vector(((k - 1) * 0.008, (1 - k) * 0.006, tz))
    tile = box(f"rack_tile{k}", (0.12, 0.11, 0.024), RACK + off, SLATE, mech,
               rot=(0, 0, (k - 1) * 0.12), bevel=0.006)
top = Panel(RACK + Vector((-0.045, -0.04, 0.025 + 3 * 0.026 - 0.001)),
            RACK + Vector((0.045, -0.04, 0.025 + 3 * 0.026 - 0.001)),
            RACK + Vector((0.045, 0.04, 0.025 + 3 * 0.026 - 0.001)),
            RACK + Vector((-0.045, 0.04, 0.025 + 3 * 0.026 - 0.001)))
for si, stroke in enumerate(LETTERS["T"]):
    glow(curve_obj(f"rack_glyph{si}", [top.at(0.15 + 0.7 * u, 0.15 + 0.7 * v, 0.004)
                                       for u, v in stroke], RUNE, 0.011, mech))
for sx in (-1, 1):   # gold clamps at the tray ends
    box(f"rack_clamp{sx}", (0.02, 0.13, 0.07), RACK + Vector((sx * 0.085, 0, 0.035)), GOLD, mech,
        bevel=0.006)
    sphere(f"rack_gem{sx}", 0.016, RACK + Vector((sx * 0.085, -0.066, 0.06)), RUBY, mech)

# --- mana vial (back right) piped to the crucible --------------------------------
VIAL_P = Vector((0.37, 0.42, DECK_Z))
VIAL_R, VIAL_H = 0.065, 0.46
vial = bpy.data.objects.new("vial", None)
link(vial, mech)
vial.location = VIAL_P
cyl("vial_glass", VIAL_R, VIAL_H, (0, 0, VIAL_H / 2 + 0.04), GLASS, vial, verts=32)
vial_liq = cyl("vial_liquid", VIAL_R - 0.012, VIAL_H * 0.7, (0, 0, VIAL_H * 0.35 + 0.05), VIAL,
               vial, verts=32)
glow(vial_liq)
for zz in (0.04, VIAL_H + 0.04):
    cyl(f"vial_cap{zz}", VIAL_R + 0.022, 0.045, (0, 0, zz), GOLD, vial, verts=32)
for k in range(4):
    a = TAU * k / 4 + math.pi / 4
    box(f"vial_strap{k}", (0.018, 0.018, VIAL_H), ((VIAL_R + 0.008) * math.cos(a),
                                                   (VIAL_R + 0.008) * math.sin(a), VIAL_H / 2 + 0.04),
        GOLD, vial, rot=(0, 0, a), bevel=0.004)
cyl("vial_cone", 0.04, 0.06, (0, 0, VIAL_H + 0.09), GOLD, vial, verts=24, r2=0.01)
sphere("vial_finial", 0.03, (0, 0, VIAL_H + 0.14), RUBY, vial)
pipe = [(VIAL_P.x, VIAL_P.y - 0.03, DECK_Z + 0.06), (0.44, 0.3, DECK_Z + 0.045),
        (0.44, -0.14, DECK_Z + 0.045), (0.36, -0.3, DECK_Z + 0.045),
        (CRU.x + CRU_R + 0.02, CRU.y, CRU.z - 0.01)]
curve_obj("mana_pipe", pipe, COPPER, 0.026, mech, res=3)
for k, t in enumerate((0.15, 0.45, 0.75)):
    i = int(t * (len(pipe) - 1))
    p = Vector(pipe[i]).lerp(Vector(pipe[i + 1]), (t * (len(pipe) - 1)) % 1)
    sphere(f"pipe_band{k}", 0.033, tuple(p), GOLD, mech)
# valve handwheel on the pipe, ruby centre
VALVE = Vector((0.44, 0.05, DECK_Z + 0.1))
cyl("valve_stem", 0.012, 0.06, VALVE - Vector((0, 0, 0.03)), BRASS, mech)
vw = [((0.05 * math.cos(TAU * i / 32)), 0.05 * math.sin(TAU * i / 32)) for i in range(32)]
vwi = [((0.038 * math.cos(TAU * i / 32)), 0.038 * math.sin(TAU * i / 32)) for i in range(32)]
o = mesh_obj("valve_wheel", ring_mesh(vw, vwi, -0.008, 0.008), GOLD, mech, smooth=True)
o.location = VALVE
for k in range(3):
    a = TAU * k / 3
    box(f"valve_spoke{k}", (0.09, 0.01, 0.01), VALVE, GOLD, mech, rot=(0, 0, a), bevel=0.002)
sphere("valve_gem", 0.016, VALVE + Vector((0, 0, 0.01)), RUBY, mech)

# --- chimney (back left): the hearth's flue ---------------------------------------
CHIM = Vector((-0.36, 0.41, DECK_Z))
CHIM_H = 0.62
cyl("chimney_stack", 0.075, CHIM_H, (CHIM.x, CHIM.y, DECK_Z + CHIM_H / 2), BRONZE, mech,
    verts=32, r2=0.06)
cyl("chimney_foot", 0.11, 0.08, (CHIM.x, CHIM.y, DECK_Z + 0.04), PURPLE, mech, verts=32,
    r2=0.085)
for k, zz in enumerate((0.09, 0.3, 0.5)):
    rr = 0.075 - 0.015 * zz / CHIM_H
    cyl(f"chimney_band{k}", rr + 0.014, 0.03, (CHIM.x, CHIM.y, DECK_Z + zz), GOLD, mech, verts=32)
top_z = DECK_Z + CHIM_H
o = mesh_obj("chimney_crown", ring_mesh(
    [(0.085 * math.cos(TAU * i / 36), 0.085 * math.sin(TAU * i / 36)) for i in range(36)],
    [(0.05 * math.cos(TAU * i / 36), 0.05 * math.sin(TAU * i / 36)) for i in range(36)],
    0.0, 0.06), GOLD, mech, smooth=True, bevel=0.008)
o.location = (CHIM.x, CHIM.y, top_z)
for k in range(6):     # crown points
    a = TAU * k / 6
    cyl(f"chimney_point{k}", 0.014, 0.05, (CHIM.x + 0.07 * math.cos(a), CHIM.y + 0.07 * math.sin(a),
                                           top_z + 0.085), GOLD, mech, verts=8, r2=0.002)
ember = cyl("chimney_ember", 0.05, 0.004, (CHIM.x, CHIM.y, top_z + 0.045), HEARTH, mech,
            verts=24)
glow(ember)
for k in range(3):     # scroll brackets tying the stack to the deck
    a = math.radians(-60) + k * math.radians(-60)
    bx, by = CHIM.x + 0.07 * math.cos(a), CHIM.y + 0.07 * math.sin(a)
    rail(f"chimney_brace{k}", [(bx, by, DECK_Z + 0.2),
                               (bx + 0.09 * math.cos(a), by + 0.09 * math.sin(a), DECK_Z + 0.02)],
         0.014)

# --- hovering orb above the carousel: flares when a plate is read -----------------
ORB_C = Vector((W.x, W.y, GZ + DOME_TOP + 0.22))
orb = bpy.data.objects.new("orb", None)
link(orb, mech)
glow(sphere("orb_core", 0.062, (0, 0, 0), ORB, orb, segs=32))
ring = mesh_obj("orb_ring", ring_mesh(
    [(0.095 * math.cos(TAU * i / 48), 0.095 * math.sin(TAU * i / 48)) for i in range(48)],
    [(0.084 * math.cos(TAU * i / 48), 0.084 * math.sin(TAU * i / 48)) for i in range(48)],
    -0.008, 0.008), GOLD, orb, smooth=True, bevel=0.003)
ring.rotation_mode = "ZXY"
for g in range(3):
    sphere(f"orb_ring_gem{g}", 0.014, (0.09 * math.cos(TAU * g / 3), 0.09 * math.sin(TAU * g / 3),
                                       0), RUBY, ring)
# ring precesses once per loop; orb bobs twice per loop
animated.append((ring, lambda o, f: setattr(o, "rotation_euler",
                                            (math.radians(62), 0, TAU * f / N))))
animated.append((orb, lambda o, f: setattr(o, "location", ORB_C + Vector(
    (0, 0, 0.02 * math.sin(2 * TAU * f / N))))))

# --- lights -------------------------------------------------------------------------
def point(name, color, loc, size=0.05):
    d = bpy.data.lights.new(name, "POINT")
    d.color = color
    d.shadow_soft_size = size
    o = bpy.data.objects.new(name, d)
    link(o, mech)
    o.location = loc
    return d


def set_energy(light, e):
    """Light energies are tuned in model units; the scene is K times larger."""
    light.energy = e * K * K


melt_light = point("melt_light", (1, 1, 1), CRU + Vector((0, -0.02, 0.1)))
hearth_light = point("hearth_light", (1.0, 0.3, 0.85), Vector(front.at(0.5, 0.5, 0.12)))
orb_light = point("orb_light", (1.0, 0.3, 0.9), ORB_C + Vector((0, -0.03, 0)))
MAGIC_LIGHTS = (melt_light, hearth_light, orb_light)

# ----------------------------------------------------------------------------
# Per-frame magic
# ----------------------------------------------------------------------------


def front_glyph(f):
    """Which plate faces the crucible (fractional while moving)."""
    rel = (FRONT - wheel_angle(f) - PLATE0) / G_SLOT
    return rel % NP


def lerp3(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def lock_age(f):
    """Frames since the carousel last locked into place."""
    for age in range(N):
        m0 = motion(f - age)[1]
        if 0.0 < motion(f - age - 1)[1] < 1.0 and m0 >= 1.0 - 1e-9:
            return age
        if 0.0 < m0 < 1.0:
            return None          # moving now
    return None


def pose_magic(f, working):
    s = front_glyph(f)
    i0 = int(math.floor(s)) % NP
    i1 = (i0 + 1) % NP
    t = s - math.floor(s)
    t = t * t * (3 - 2 * t)
    col = lerp3(GLYPHS[i0][1], GLYPHS[i1][1], t)
    # the melt takes on the colour of the glyph being read, blending while moving
    MELT_COL.default_value = (*col, 1)
    BEAM_COL.default_value = (*col, 1)
    melt_light.color = col
    _, mv = motion(f)
    age = lock_age(f)
    flare = math.exp(-age / 4.0) if age is not None else 0.0
    # beam: rises after the lock, fades before the next index starts
    # 1 with the pin pointing away (mid dwell), 0 from before engagement on
    dwell = max(0.0, -math.cos(drive_angle(f))) ** 0.7 if not (0.0 < mv < 1.0) else 0.0
    for i, (mat, em) in enumerate(GLYPH_MATS):
        d = min(abs(s - i), NP - abs(s - i))   # plates from the reading position
        near = max(0.0, 1.0 - d)
        em.default_value = (0.5 + 5.0 * near * near * (0.45 + 0.55 * dwell + 0.8 * flare)
                            if working else 0.06 + 0.1 * near)
    # molten textures flow along a closed circle over the loop
    a = TAU * f / N
    MELT_UV.default_value = (0.25 * math.cos(a), 0.25 * math.sin(a), 0.1 * math.sin(2 * a))
    HEARTH_UV.default_value = (0.4 * math.cos(-a), 0.15 * math.sin(2 * a), 0.4 * math.sin(-a))
    if working:
        MELT_EM.default_value = 1.3 + 1.0 * flare
        HEARTH_EM.default_value = 2.0 + 0.4 * math.sin(4 * TAU * f / N)
        BEAM_EM.default_value = 3.0 * dwell + 2.0 * flare
        beam.hide_render = (dwell + flare) < 0.02
        ORB_EM.default_value = 1.2 + 3.0 * flare
        VIAL_EM.default_value = 0.9
        RUNE_EM.default_value = 0.6 + 1.0 * flare
        set_energy(melt_light, 0.8 + 1.0 * dwell + 1.2 * flare)
        set_energy(hearth_light, 0.5)
        set_energy(orb_light, 0.6 + 2.0 * flare)
    else:
        # at rest: embers - the idle sprite must look good on its own
        MELT_EM.default_value = 0.12
        HEARTH_EM.default_value = 0.12
        BEAM_EM.default_value = 0.0
        beam.hide_render = True
        ORB_EM.default_value = 0.2
        VIAL_EM.default_value = 0.15
        RUNE_EM.default_value = 0.06
        set_energy(melt_light, 0.05)
        set_energy(hearth_light, 0.0)
        set_energy(orb_light, 0.05)


def pose(f, working=False):
    for o, fn in animated:
        fn(o, f)
    pose_magic(f, working)


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

FRAME_W, FRAME_H, FRAME_CY = 2.3 * K, 1.85 * K, 0.35 * K
# the shadow gets its own, wider frame (it reaches far east like vanilla's)
SH_W, SH_H, SH_CX, SH_CY = 4.6, 2.6, 0.8, 0.15
rig = setup_scene(FRAME_W, FRAME_H, FRAME_CY)


def load_px(path):
    im = bpy.data.images.load(str(path))
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    return a


def save_px(path, a):
    h, w, _ = a.shape
    im = bpy.data.images.new(path.stem, w, h, alpha=True)
    im.pixels = a.ravel().tolist()
    im.filepath_raw = str(path)
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


def render_all():
    """main (at rest), work (lit) -> glow = work - main, then the shadow.
    Factorio adds the glow sprite on top while the machine works (additive,
    opaque black background like vanilla steel-furnace-working.png)."""
    scene = bpy.context.scene
    frames = [int(x) for x in args.frame.split(",")] if args.preview else range(N)
    if args.save_blend:
        pose(0)
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "rune-transformer.blend"))
    scene.cycles.seed = 7
    for f in frames:
        pose(f, working=False)
        render(OUT / f"main-{f:03d}.png")
    if not args.no_glow:
        for f in frames:
            pose(f, working=True)
            render(OUT / f"work-{f:03d}.png")
        for f in frames:
            m = load_px(OUT / f"main-{f:03d}.png")
            w = load_px(OUT / f"work-{f:03d}.png")
            d = w[..., :3] * w[..., 3:] - m[..., :3] * m[..., 3:]
            d = np.clip(d - 2.5 / 255, 0, 1)        # drop denoiser speckle
            out = np.concatenate([d, np.ones_like(d[..., :1])], axis=-1)
            save_px(OUT / f"glow-{f:03d}.png", out)

    # shadow: the key light only, low from the north-west (as fblend does)
    lights = (rig.sun_d, rig.fill_d) + MAGIC_LIGHTS
    rig.ground.hide_render = False
    pose(0)
    for l in lights:
        l.energy = 0.0
    rig.sun_d.energy = 4.6
    for o in scene.objects:
        if o is not rig.ground and o.type in ("MESH", "CURVE"):
            o.visible_camera = False
    beam.hide_render = True
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((1.0, -0.35, -0.75)).normalized()).to_euler()
    cam = scene.camera
    cam.data.ortho_scale = max(SH_W, SH_H)
    # pan the camera: +x, and up the screen by (SH_CY - FRAME_CY)
    cam.location += Vector((SH_CX, 0, (SH_CY - FRAME_CY) * math.sqrt(2)))
    scene.render.resolution_x = round(SH_W * args.px_per_tile)
    scene.render.resolution_y = round(SH_H * args.px_per_tile)
    render(OUT / "shadow.png")

    # ground light: soft purple pool in front of the hearth, 64 px/tile
    ppt = 64
    gw, gh = int(2.4 * ppt), int(1.9 * ppt)
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    # ground is foreshortened by 1/sqrt(2) on screen
    r = np.sqrt(((xx - gw / 2) / (gw * 0.42)) ** 2 + ((yy - gh * 0.42) / (gh * 0.5)) ** 2)
    k = np.clip(1 - r, 0, 1) ** 1.6
    col = np.array([0.85, 0.3, 0.95], dtype=np.float32)
    g = np.concatenate([k[..., None] * col, np.ones_like(k[..., None])], axis=-1)
    save_px(OUT / "ground-light.png", g[::-1].copy())   # Blender pixels are bottom-up


print("PLATE0", math.degrees(PLATE0), "D", tuple(D), "lock radius", G_LOCK_R)
render_all()
