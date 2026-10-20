"""
Procedural Blender model + Factorio render of the distillery.

A heat-powered alembic: the four heat-pipe connections feed a heat chamber
under a copper pot still. The brew boils (bubbles in the porthole, vapour
glowing in the column), the vapour climbs the column, runs down the swan
neck into the coil of a worm tub and condenses; the distillate passes a
glass spirit safe and pours from a spout into a flask. A hot-air engine
running off the same heat chamber turns a Geneva drive that indexes a
four-flask carousel a quarter turn per loop: fill (north), wait (east),
decant into the output chute (south), wait empty (west), fill again.

    blender -b --factory-startup -P blender/distillery.py -- \
        --out graphics/generated/distillery [--preview --frame 0,24]

Passes (all under --out): main-NNN / glow-NNN (working loop), idle-main
(the machine standing still, no flow), heat (heated pipes only, for the
energy source's heat_picture) and shadow (wider frame, see SHADOW_*).
World units are model tiles; the entity is 3x3 centred on the origin, +y is
north, +z is up. Rendered for Lua scale 0.5 (1 model unit = 1 tile on screen
horizontally), which lets the heat inlets line up with real heat pipes.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("distillery", frames=64, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT
S2 = math.sqrt(2)

# --- extra materials ----------------------------------------------------------
POTION, POTION_EM = emitter("distillate", (0.95, 0.22, 0.78), 1.2)
BREW, BREW_EM = emitter("brew", (0.85, 0.18, 0.7), 1.0, base=(0.35, 0.04, 0.3))
BUBBLE, _ = emitter("bubble", (1.0, 0.6, 0.95), 2.5)
VAPOUR, VAPOUR_EM = emitter("vapour", (1.0, 0.45, 0.9), 1.0, base=(0.3, 0.1, 0.3), glass=True)
SOOT = metal("soot", (0.06, 0.045, 0.04), (0.01, 0.008, 0.006), rough=(0.5, 0.8), dirt=0.0)
IVORY, _, _ = node_mat("ivory")
IVORY.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.72, 0.55, 1)
IVORY.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
HERB = paint("herbs", (0.16, 0.3, 0.08), (0.03, 0.05, 0.01), noise_scale=40.0, bump=0.8,
             bump_scale=80.0, dirt=0.0)
WATER, _, _ = node_mat("coolant")
_w = WATER.node_tree.nodes["Principled BSDF"]
_w.inputs["Base Color"].default_value = (0.05, 0.02, 0.06, 1)
_w.inputs["Roughness"].default_value = 0.18
_wn = WATER.node_tree.nodes.new("ShaderNodeTexNoise")
_wn.inputs["Scale"].default_value = 30.0
_wb = WATER.node_tree.nodes.new("ShaderNodeBump")
_wb.inputs["Strength"].default_value = 0.35
WATER.node_tree.links.new(_wn.outputs["Fac"], _wb.inputs["Height"])
WATER.node_tree.links.new(_wb.outputs["Normal"], _w.inputs["Normal"])
# the heat-pipe flask glass is marked glow so the liquid inside shows in the
# light pass; give it a hint of tint so it reads as glass in daylight too
FLASK_GLASS, _, _ = node_mat("flask_glass")
_g = FLASK_GLASS.node_tree.nodes["Principled BSDF"]
_g.inputs["Base Color"].default_value = (0.92, 0.9, 1.0, 1)
_g.inputs["Transmission Weight"].default_value = 1.0
_g.inputs["Roughness"].default_value = 0.05


def hot_copper():
    """Heat-pipe copper that can be switched to glowing hot: the main passes
    show it cold (the game's heat_picture adds the glow by temperature), the
    heat pass shows it white-orange hot."""
    m, nt, bsdf = node_mat("hot_copper")
    bsdf.inputs["Metallic"].default_value = 1.0
    grime(nt, bsdf, (0.85, 0.42, 0.24), (0.2, 0.07, 0.03), rough=(0.2, 0.45))
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.42, 0.1, 1)
    em.inputs["Strength"].default_value = 0.9
    # hotter (yellower) towards the light-facing top, like the vanilla heated pipes
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.4
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (1.0, 0.62, 0.22, 1)
    ramp.color_ramp.elements[1].color = (0.75, 0.14, 0.02, 1)
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes["Material Output"]
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    mix.inputs[0].default_value = 0.0
    return m, mix.inputs[0]


HOT, HOT_MIX = hot_copper()


def heat(obj):
    """Mark an object as a heated part: kept in the heat pass."""
    obj["heat"] = True
    for c in obj.children_recursive:
        c["heat"] = True
    return obj


# ----------------------------------------------------------------------------
# Plinth
# ----------------------------------------------------------------------------
#
# Like the vanilla 3x3 assemblers: a decorated base whose side walls slope in
# (they read as wings), a flat working deck on top, the tall apparatus at the
# back. Factorio's projection squeezes the ground by 1/sqrt(2) on screen
# (screen y = (y + z) / sqrt(2)), so the back of the footprint sits only ~2.1
# tiles above its front edge; the tall still covers the rest of the north tile.

root = bpy.data.objects.new("distillery", None)
link(root)

HALF = 1.38          # base half width: leaves the heat stubs room to show
CH = 0.28            # front corner chamfer
PLINTH_H = 0.14
XT = 1.17            # deck half width (walls slope in to here)
TC = 0.24
YF, YB = -1.13, 1.28  # deck front / back edge
Z_D = 0.62           # deck height
RIM_W = 0.13

bot2d = [(-HALF + CH, -HALF), (HALF - CH, -HALF), (HALF, -HALF + CH),
         (HALF, HALF), (-HALF, HALF), (-HALF, -HALF + CH)]
top2d = [(-XT + TC, YF), (XT - TC, YF), (XT, YF + TC), (XT, YB), (-XT, YB), (-XT, YF + TC)]
B3 = [Vector((x, y, PLINTH_H)) for x, y in bot2d]
T3 = [Vector((x, y, Z_D)) for x, y in top2d]


def prism(name, poly, z0, z1, mat, parent=None, bevel=0.01):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, mat, parent or root, bevel=bevel)
    o.data.shade_flat()
    return o


def rail(name, pts3, r, closed=False, mat=None, parent=None):
    return curve_obj(name, [tuple(p) for p in pts3], mat or GOLD, r, parent or root,
                     closed=closed)


def lathe(name, prof, mat, parent=None, loc=(0, 0, 0), segs=48, bevel=0.0):
    """Surface of revolution about local z from (r, z) pairs, bottom to top."""
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        if r < 1e-5:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(TAU * i / segs),
                                        r * math.sin(TAU * i / segs), z))
                          for i in range(segs)])
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1 and len(b) > 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1 and len(a) > 1:
                bm.faces.new((a[i], a[j], b[0]))
            elif len(a) > 1:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, mat, parent or root, smooth=True, bevel=bevel)
    o.location = loc
    return o


def ring(name, r_out, r_in, z0, z1, mat, parent=None, loc=(0, 0, 0), segs=48, bevel=0.006):
    o = mesh_obj(name, ring_mesh(
        [(r_out * math.cos(TAU * i / segs), r_out * math.sin(TAU * i / segs)) for i in range(segs)],
        [(r_in * math.cos(TAU * i / segs), r_in * math.sin(TAU * i / segs)) for i in range(segs)],
        z0, z1), mat, parent or root, smooth=True, bevel=bevel)
    o.location = loc
    return o


def lyre(cu=0.5, cv=0.5, w=1.0, h=1.0):
    """Symmetric double-scroll motif."""
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


FIL_R = 0.04         # raised scrollwork thickness

prism("plinth", bot2d, 0, PLINTH_H, BRONZE)
rail("plinth_rail", [(x, y, PLINTH_H) for x, y in bot2d], 0.06, closed=True)
rail("plinth_foot", [(x * 1.006, y * 1.006, 0.02) for x, y in bot2d], 0.028, closed=True)

walls = {}
for i in range(6):
    j = (i + 1) % 6
    p = Panel(B3[i], B3[j], T3[j], T3[i])
    p.build(f"wall{i}", PURPLE, parent=root)
    walls[i] = p
for i in range(6):
    rail(f"corner_rib{i}", [B3[i] + Vector((0, 0, 0.02)), T3[i]], 0.065)

# deck: wide studded gold rim band around a bronze tread plate
inner2d = [(-XT + TC + 0.06, YF + RIM_W), (XT - TC - 0.06, YF + RIM_W), (XT - RIM_W, YF + TC + 0.06),
           (XT - RIM_W, YB - RIM_W), (-XT + RIM_W, YB - RIM_W), (-XT + RIM_W, YF + TC + 0.06)]
I3 = [Vector((x, y, Z_D)) for x, y in inner2d]
bm = bmesh.new()
vo = [bm.verts.new(tuple(v)) for v in T3]
vi = [bm.verts.new(tuple(v)) for v in I3]
for i in range(6):
    j = (i + 1) % 6
    bm.faces.new((vo[i], vo[j], vi[j], vi[i]))
rim_o = mesh_obj("rim_band", bm, GOLD, root, bevel=0.01)
rim_o.modifiers.new("solid", "SOLIDIFY").thickness = 0.04
rail("rim_outer", [t + Vector((0, 0, 0.015)) for t in T3], 0.07, closed=True)
rail("rim_inner", [v + Vector((0, 0, 0.015)) for v in I3], 0.045, closed=True)
for i in range(6):
    a = T3[i].lerp(I3[i], 0.5)
    b = T3[(i + 1) % 6].lerp(I3[(i + 1) % 6], 0.5)
    n = max(2, int((b - a).length / 0.2))
    for k in range(n + 1):
        p = a.lerp(b, k / n) + Vector((0, 0, 0.03))
        sphere(f"rim_stud{i}_{k}", 0.028 if k % 2 else 0.034, tuple(p), RUBY if k % 2 else GOLD, root)
DECK_MAT = metal("deck_plate", (0.24, 0.16, 0.1), (0.04, 0.025, 0.015), rough=(0.35, 0.65), dirt=0.35,
                 bump=0.3, bump_scale=25.0)
prism("deck", inner2d, Z_D - 0.05, Z_D - 0.005, DECK_MAT)
# riveted plate seams so the visible deck reads as heavy floor plates
for k, y in enumerate((-0.86, -0.42, 0.02, 0.46, 0.9)):
    box(f"seam_y{k}", (2 * (XT - RIM_W) - 0.02, 0.025, 0.012), (0, y, Z_D), BRASS, root, bevel=0.004)
for k, x in enumerate((-0.6, 0.0, 0.6)):
    box(f"seam_x{k}", (0.025, YB - YF - 2 * RIM_W - 0.02, 0.012), (x, (YB + YF) / 2, Z_D), BRASS, root, bevel=0.004)
for y in (-0.86, -0.42, 0.02, 0.46, 0.9):
    for x in (-1.0, -0.8, -0.4, -0.2, 0.2, 0.4, 0.8, 1.0):
        sphere(f"seam_rivet{x}{y}", 0.016, (x, y, Z_D + 0.008), GOLD, root, segs=8)

# --- wall decoration -----------------------------------------------------------
front = walls[0]
ribs_u = (0.3, 0.7)
for k, u in enumerate(ribs_u):
    rail(f"front_rib{k}", [Vector(front.at(u, 0, 0.03)), Vector(front.at(u, 1, 0.03))], 0.055)
for k, (u0, u1) in enumerate(((0.0, ribs_u[0]), ribs_u, (ribs_u[1], 1.0))):
    if k == 1:
        continue      # centre panel carries the south heat port, see below
    sp = sub_panel(front, u0 + 0.03, u1 - 0.03, 0.1, 0.9)
    gold_frame(sp, f"fp{k}_frame", 0.03, parent=root)
    inner = sub_panel(sp, 0.06, 0.94, 0.1, 0.9)
    inner.filigree(f"fp{k}_fil", [fit(scroll_c(0, 0, 1), 0.02, 0.0, 0.98, 1.0, flip_x=(k == 2)),
                                  fit(scroll_c(0, 0, 1, up=False), 0.05 if k == 2 else 0.55, 0.05,
                                      0.45 if k == 2 else 0.95, 0.5, flip_x=(k != 2))],
                   radius=FIL_R, parent=root)
    inner.studs(f"fp{k}_dots", [(0.5, 0.92), (0.12 if k == 0 else 0.88, 0.1)], r=0.022, parent=root)
for i in (5, 1):    # front chamfers
    sp = sub_panel(walls[i], 0.1, 0.9, 0.12, 0.9)
    sp.filigree(f"ch{i}_fil", [fit(scroll_c(0, 0, 1), 0.05, 0.05, 0.95, 0.95, flip_x=(i == 1))],
                radius=FIL_R, parent=root)
    sp.studs(f"ch{i}_gem", [(0.5, 0.5)], r=0.03, mat=RUBY, parent=root)

# ----------------------------------------------------------------------------
# Heat connections
# ----------------------------------------------------------------------------
#
# Heat enters at the middle tile of each side ({0,-1} N, {1,0} E, {0,1} S,
# {-1,0} W in Factorio). Each inlet is a twin copper stub like the vanilla heat
# pipe, ending on the footprint edge where the neighbouring heat pipe (or the
# vanilla pipe cover) continues it. Positions are chosen ON SCREEN: with the
# Lua shift that puts the front edge of the footprint on the tile edge, the
# east/west tile centre row lies at y + z = HEAT_EW_YZ in the model, and the
# north edge is hidden behind the still.
HP_R = 0.085               # vanilla heat pipe: two ~0.17-tile copper tubes
HP_GAP = 0.115             # half distance between the two tubes
HP_Z = HP_R + 0.005
FRONT_U = -1.5 / S2        # screen height of the footprint's front edge (z = 0)
HEAT_EW_YZ = 0.62          # model y + z of the east/west connection row
HEAT_EW_Y = HEAT_EW_YZ - HP_Z
EDGE = 1.5


def heat_stub(name, axis_dir, centre_off, inner, outer):
    """Twin heat tubes running along axis_dir ('x' or 'y') between the
    coordinates inner..outer, offset centre_off in the other axis."""
    grp = bpy.data.objects.new(name, None)
    link(grp, root)
    for s in (-1, 1):
        o = centre_off + s * HP_GAP
        if axis_dir == "x":
            a, b = (inner, o, HP_Z), (outer, o, HP_Z)
        else:
            a, b = (o, inner, HP_Z), (o, outer, HP_Z)
        curve_obj(f"{name}_tube{s}", [a, b], HOT, HP_R, grp, res=4)
    # dark steel clamp band near the tile edge, as on the vanilla pipes
    mid = outer - math.copysign(0.07, outer)
    size = (0.05, 2 * HP_GAP + 2 * HP_R + 0.035, 2 * HP_R + 0.03)
    if axis_dir == "x":
        box(f"{name}_clamp", size, (mid, centre_off, HP_Z), STEEL, root, bevel=0.01)
    else:
        box(f"{name}_clamp", (size[1], size[0], size[2]), (centre_off, mid, HP_Z), STEEL, root,
            bevel=0.01)
    heat(grp)
    return grp


def port_flange(name, loc, along_x, w=0.44, h=0.3):
    """Gold flange plate on the wall where the stub enters the plinth, with a
    round ruby-bolted collar on each tube."""
    sz = (0.05, w, h) if along_x else (w, 0.05, h)
    box(name, sz, loc, GOLD, root, bevel=0.015)
    out = 1 if (loc[0] if along_x else loc[1]) > 0 else -1
    for s_ in (-1, 1):
        off = s_ * HP_GAP
        if along_x:
            c = (loc[0] + out * 0.04, loc[1] + off, HP_Z)
            rot = (0, math.radians(90), 0)
        else:
            c = (loc[0] + off, loc[1] + out * 0.04, HP_Z)
            rot = (math.radians(90), 0, 0)
        ring(f"{name}_collar{s_}", HP_R + 0.035, HP_R - 0.01, -0.025, 0.025, GOLD, root, loc=c).rotation_euler = rot
        for k in range(4):
            a = TAU * (k + 0.5) / 4
            d = Vector((0, math.cos(a), math.sin(a))) if along_x else Vector((math.cos(a), 0, math.sin(a)))
            sphere(f"{name}_bolt{s_}{k}", 0.014, tuple(Vector(c) + d * (HP_R + 0.02) +
                                                       (Vector((out * 0.026, 0, 0)) if along_x else
                                                        Vector((0, out * 0.026, 0)))),
                   RUBY if k % 2 else GOLD, root, segs=8)


heat_stub("heat_S", "y", 0.0, -HALF + 0.12, -EDGE)
heat_stub("heat_N", "y", 0.0, HALF - 0.12, EDGE)
heat_stub("heat_E", "x", HEAT_EW_Y, HALF - 0.12, EDGE)
heat_stub("heat_W", "x", HEAT_EW_Y, -HALF + 0.12, -EDGE)
port_flange("flange_S", (0, -HALF - 0.005, 0.16), False)
port_flange("flange_N", (0, HALF + 0.005, 0.16), False)
port_flange("flange_E", (HALF + 0.005, HEAT_EW_Y, 0.16), True)
port_flange("flange_W", (-HALF - 0.005, HEAT_EW_Y, 0.16), True)


def port_window(p, name, u0, u1, v0, v1, bars=3):
    """Gold-arched window in a wall showing the glowing heat coils behind it."""
    win = sub_panel(p, u0, u1, v0, v1)
    back = Panel(*[Vector(c) - win.n * 0.0 for c in win.c])
    back.build(f"{name}_back", SOOT, thick=0.01, parent=root)
    for k in range(bars):
        v = (k + 0.7) / (bars + 0.4)
        o = curve_obj(f"{name}_coil{k}", [win.at(0.06, v, 0.012), win.at(0.94, v, 0.012)], HOT,
                      0.022, root, res=3)
        heat(o)
    for k, u in enumerate((0.33, 0.67)):
        rail(f"{name}_grille{k}", [Vector(win.at(u, 0.0, 0.035)), Vector(win.at(u, 1.0, 0.035))],
             0.018)
    # round-topped gold arch around the window
    pts = [win.at(0.0, 0.0, 0.03)]
    for k in range(13):
        a = math.pi * k / 12
        pts.append(win.at(0.5 - 0.5 * math.cos(a), 0.78 + 0.22 * math.sin(a), 0.03))
    pts.append(win.at(1.0, 0.0, 0.03))
    rail(f"{name}_arch", pts, 0.035)
    win.studs(f"{name}_key", [(0.5, 1.07)], r=0.035, mat=RUBY, parent=root)
    return win


# south port in the centre front panel, lyre motif above it
cp = sub_panel(front, ribs_u[0] + 0.03, ribs_u[1] - 0.03, 0.1, 0.9)
gold_frame(cp, "fp1_frame", 0.03, parent=root)
port_window(cp, "port_S", 0.3, 0.7, 0.04, 0.5)
sub_panel(cp, 0.06, 0.94, 0.55, 0.95).filigree("fp1_lyre", lyre(0.5, 0.5, 1.0, 1.0),
                                                radius=FIL_R * 0.85, parent=root)
cp.studs("fp1_dots", [(0.12, 0.85), (0.88, 0.85), (0.12, 0.15), (0.88, 0.15)], r=0.024,
         parent=root)

# side wings: rune plate at the front, heat port window, scrollwork at the back
for i, sgn in ((2, 1), (4, -1)):
    w = walls[i]
    y_lo, y_hi = -HALF + CH, HALF          # wall base runs between these y

    def u_of(y):
        t = (y - y_lo) / (y_hi - y_lo)
        return t if sgn > 0 else 1 - t

    port_u = u_of(HEAT_EW_Y)
    segs = (("rune", u_of(-1.05), u_of(0.05)), ("port", u_of(0.12), u_of(0.92)),
            ("scroll", u_of(0.98), u_of(1.42)))
    for kind, ua, ub in segs:
        u0, u1 = min(ua, ub), max(ua, ub)
        sp = sub_panel(w, u0, u1, 0.1, 0.9)
        gold_frame(sp, f"side{i}_{kind}_frame", 0.03, parent=root)
        inner = sub_panel(sp, 0.08, 0.92, 0.08, 0.92)
        if kind == "rune":
            rune(inner, f"side{i}_rune", 1 if sgn > 0 else 3, parent=root)
            inner.studs(f"side{i}_rgem", [(0.5, 0.0), (0.5, 1.0)], r=0.026, mat=RUBY, parent=root)
            inner.filigree(f"side{i}_rfil", [fit(scroll_c(0, 0, 1), 0.0, 0.55, 0.3, 1.0),
                                             fit(scroll_c(0, 0, 1), 0.7, 0.55, 1.0, 1.0, flip_x=True)],
                           radius=FIL_R * 0.6, parent=root)
        elif kind == "port":
            pu = (port_u - u0) / (u1 - u0)
            port_window(sp, f"port{i}", pu - 0.2, pu + 0.2, 0.0, 0.52)
            inner.filigree(f"side{i}_pfil", [fit(scroll_c(0, 0, 1), 0.0, 0.62, 0.45, 1.0),
                                             fit(scroll_c(0, 0, 1), 0.55, 0.62, 1.0, 1.0,
                                                 flip_x=True)],
                           radius=FIL_R * 0.8, parent=root)
        else:
            inner.filigree(f"side{i}_sfil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0,
                                                 flip_x=sgn < 0)], radius=FIL_R * 0.8, parent=root)
            inner.studs(f"side{i}_sgem", [(0.5, 0.5)], r=0.03, mat=RUBY, parent=root)

# ----------------------------------------------------------------------------
# Heat chamber and pot still
# ----------------------------------------------------------------------------
app = bpy.data.objects.new("apparatus", None)
link(app, root)
animated = []          # (obj, fn(obj, f)) evaluated per frame

POT = Vector((-0.35, 0.35, 0.0))
FB_R, FB_TOP = 0.5, 1.12

# heat chamber: dark iron drum banded in gold, coils glowing behind grilles
lathe("chamber", [(FB_R + 0.04, Z_D), (FB_R + 0.04, Z_D + 0.06), (FB_R, Z_D + 0.07),
                  (FB_R, FB_TOP - 0.06), (FB_R + 0.03, FB_TOP - 0.05), (FB_R + 0.03, FB_TOP),
                  (0.0, FB_TOP)], STEEL, app, loc=POT, segs=64)
for z in (Z_D + 0.07, FB_TOP - 0.02):
    ring("chamber_band%.2f" % z, FB_R + 0.045, FB_R - 0.01, z - 0.025, z + 0.025, GOLD, app,
         loc=POT, segs=64)
for k in range(12):
    a = TAU * k / 12
    p = POT + Vector((math.cos(a) * (FB_R + 0.012), math.sin(a) * (FB_R + 0.012), 0))
    box(f"chamber_rib{k}", (0.035, 0.035, FB_TOP - Z_D - 0.1), (p.x, p.y, (Z_D + FB_TOP) / 2),
        GOLD, app, rot=(0, 0, a), bevel=0.008)
for k, deg in enumerate((-75, -45, -15, -165, 15)):
    a = math.radians(deg) + TAU / 24
    c = POT + Vector((math.cos(a) * FB_R, math.sin(a) * FB_R, 0))
    t = Vector((-math.sin(a), math.cos(a), 0))
    hw = FB_R * math.sin(TAU / 24) * 0.85
    win = Panel(tuple(c - t * hw + Vector((0, 0, Z_D + 0.13))), tuple(c + t * hw + Vector((0, 0, Z_D + 0.13))),
                tuple(c + t * hw + Vector((0, 0, FB_TOP - 0.1))),
                tuple(c - t * hw + Vector((0, 0, FB_TOP - 0.1))))
    win.build(f"chamber_win{k}", SOOT, thick=0.01, parent=app)
    for b in range(3):
        o = curve_obj(f"chamber_coil{k}_{b}", [win.at(0.1, (b + 0.6) / 3.2, 0.006),
                                               win.at(0.9, (b + 0.6) / 3.2, 0.006)], HOT, 0.02,
                      app, res=3)
        heat(o)
    rail(f"chamber_bar{k}", [Vector(win.at(0.5, 0, 0.03)), Vector(win.at(0.5, 1, 0.03))], 0.014,
         parent=app)

# manifold ring at the chamber foot, fed by the west and north inlets
heat(curve_obj("manifold", [(POT.x + 0.58 * math.cos(TAU * i / 48), POT.y + 0.58 * math.sin(TAU * i / 48),
                             Z_D + 0.055) for i in range(48)], HOT, 0.05, app, closed=True, res=4))
for k in range(8):
    a = TAU * (k + 0.5) / 8
    box(f"manifold_clip{k}", (0.05, 0.13, 0.11), (POT.x + 0.58 * math.cos(a), POT.y + 0.58 * math.sin(a),
                                                  Z_D + 0.055), STEEL, app, rot=(0, 0, a), bevel=0.01)


def deck_pipe(name, pts2):
    """Twin heat tubes on the deck along a 2D polyline (mitred offsets)."""
    P = [Vector((x, y)) for x, y in pts2]
    for sgn in (-1, 1):
        out = []
        for i, p in enumerate(P):
            dirs = []
            if i > 0:
                dirs.append((p - P[i - 1]).normalized())
            if i < len(P) - 1:
                dirs.append((P[i + 1] - p).normalized())
            t = sum(dirs, Vector((0, 0))).normalized()
            n = Vector((-t.y, t.x))
            miter = 1.0 / max(0.5, n.dot(Vector((-dirs[0].y, dirs[0].x))))
            q = p + n * HP_GAP * 0.75 * sgn * miter
            out.append((q.x, q.y, Z_D + 0.055))
        heat(curve_obj(f"{name}{sgn}", out, HOT, 0.045, app, res=3))
    a, b = P[0], P[1]
    along_x = abs(b.x - a.x) > abs(b.y - a.y)
    box(f"{name}_collar", (0.08, 0.3, 0.13) if along_x else (0.3, 0.08, 0.13),
        (a.x, a.y, Z_D + 0.055), GOLD, app, bevel=0.015)
    for k in range(1, len(P) - 1):     # clamp at every bend
        box(f"{name}_clip{k}", (0.13, 0.13, 0.12), (P[k].x, P[k].y, Z_D + 0.06), STEEL, app,
            bevel=0.015)


deck_pipe("deck_pipe_W", [(-XT + 0.06, HEAT_EW_Y), (POT.x - 0.56, HEAT_EW_Y)])
deck_pipe("deck_pipe_N", [(-0.04, YB - 0.06), (-0.04, POT.y + 0.55)])
deck_pipe("deck_pipe_E", [(XT - 0.08, HEAT_EW_Y), (XT - 0.12, 0.12), (0.19, 0.12)])
deck_pipe("deck_pipe_S", [(0.0, YF + 0.05), (0.0, -0.98), (-0.2, -0.9), (-0.2, -0.17)])
# heat valve with a big handwheel on the west feed
HW = Vector((-1.0, HEAT_EW_Y, Z_D + 0.0))
box("heat_valve_body", (0.26, 0.34, 0.15), (HW.x, HW.y, Z_D + 0.075), BRASS, app, bevel=0.03)
cyl("heat_valve_stem", 0.02, 0.2, (HW.x, HW.y, Z_D + 0.24), STEEL, app, verts=12)
ring("handwheel", 0.12, 0.095, -0.015, 0.015, GOLD, app, loc=(HW.x, HW.y, Z_D + 0.33), segs=40)
for k in range(5):
    a = TAU * k / 5
    box(f"handwheel_spoke{k}", (0.1, 0.018, 0.015), (HW.x + 0.05 * math.cos(a), HW.y + 0.05 * math.sin(a),
                                                     Z_D + 0.33), GOLD, app, rot=(0, 0, a), bevel=0.003)
    sphere(f"handwheel_knob{k}", 0.02, (HW.x + 0.12 * math.cos(a + 0.6), HW.y + 0.12 * math.sin(a + 0.6),
                                         Z_D + 0.33), RUBY if k == 0 else GOLD, app)

# pot: hammered copper onion, gold equator band and rivets
POT_Z = FB_TOP
pot_prof = [(0.44, POT_Z), (0.52, POT_Z + 0.08), (0.56, POT_Z + 0.2), (0.545, POT_Z + 0.32),
            (0.48, POT_Z + 0.44), (0.36, POT_Z + 0.53), (0.22, POT_Z + 0.59), (0.17, POT_Z + 0.64),
            (0.16, POT_Z + 0.7)]
COPPER_POT = metal("pot_copper", (0.82, 0.4, 0.22), (0.16, 0.05, 0.025), rough=(0.18, 0.42),
                   dirt=0.25, bump=0.5, bump_scale=30.0, hammered=True)
lathe("pot", pot_prof, COPPER_POT, app, loc=POT, segs=64)
for z, r in ((POT_Z + 0.02, 0.47), (POT_Z + 0.26, 0.56)):
    ring(f"pot_band{z:.2f}", r + 0.025, r - 0.02, z - 0.03, z + 0.03, GOLD, app, loc=POT, segs=64)
    for k in range(20):
        a = TAU * (k + 0.5) / 20
        sphere(f"pot_rivet{z:.2f}_{k}", 0.018, (POT.x + (r + 0.027) * math.cos(a),
                                                 POT.y + (r + 0.027) * math.sin(a), z), GOLD, app)
# gold scroll straps over the shoulder
for k in range(8):
    a = TAU * (k + 0.25) / 8
    pts = []
    for t in range(9):
        tt = t / 8
        z = POT_Z + 0.3 + tt * 0.3
        r = 0.555 - 0.4 * tt ** 1.5 + 0.02
        pts.append((POT.x + r * math.cos(a + 0.15 * math.sin(tt * 3)),
                    POT.y + r * math.sin(a + 0.15 * math.sin(tt * 3)), z))
    rail(f"pot_strap{k}", pts, 0.026, parent=app)

# porthole on the pot's front: the brew boils behind it
PH_A = math.radians(-62)
PH_C = POT + Vector((0.553 * math.cos(PH_A), 0.553 * math.sin(PH_A), POT_Z + 0.2))
PH_N = Vector((math.cos(PH_A), math.sin(PH_A), 0.12)).normalized()
porthole = bpy.data.objects.new("porthole", None)
link(porthole, app)
porthole.location = PH_C
porthole.rotation_euler = Vector((0, 0, 1)).rotation_difference(PH_N).to_euler()
ring("porthole_bezel", 0.115, 0.08, -0.01, 0.035, GOLD, porthole, segs=40, bevel=0.01)
for k in range(8):
    a = TAU * k / 8
    sphere(f"porthole_bolt{k}", 0.014, (0.098 * math.cos(a), 0.098 * math.sin(a), 0.036), BRASS,
           porthole)
brew_disc = cyl("porthole_brew", 0.082, 0.01, (0, 0, 0.004), BREW, porthole, verts=32)
glow(brew_disc)
pglass = sphere("porthole_glass", 0.082, (0, 0, -0.04), FLASK_GLASS, porthole, segs=24)
pglass.scale = (1, 1, 0.75)
glow(pglass)
PH_UP = (Vector((0, 0, 1)) - PH_N * PH_N.z).normalized()
PH_SIDE = PH_N.cross(PH_UP)
BUBBLES = []
for k in range(7):
    b = sphere(f"bubble{k}", 0.012 + 0.005 * (k % 3), (0, 0, 0), BUBBLE, app, segs=10)
    glow(b)
    BUBBLES.append((b, k))


def bubble_pos(o, f, k):
    # rise across the porthole (local +y is up the pot side after the tilt)
    rise = ((f / N) * (3 + k % 2) + k * 0.29) % 1.0
    x = 0.045 * math.sin(k * 2.1 + 3 * TAU * f / N * (1 + k % 2))
    o.location = PH_C + PH_N * 0.014 + PH_SIDE * x * (1 - rise) + PH_UP * (-0.07 + 0.14 * rise)
    o.scale = [0.4 + 0.6 * math.sin(math.pi * rise)] * 3


for b, k in BUBBLES:
    animated.append((b, lambda o, f, k=k: bubble_pos(o, f, k)))

# helmet, gauge and rectifying column
HEL_Z = POT_Z + 0.7
lathe("helmet", [(0.16, HEL_Z), (0.22, HEL_Z + 0.04), (0.27, HEL_Z + 0.12), (0.265, HEL_Z + 0.2),
                 (0.2, HEL_Z + 0.27), (0.14, HEL_Z + 0.3)], COPPER_POT, app, loc=POT, segs=48)
ring("helmet_band", 0.285, 0.25, HEL_Z + 0.1, HEL_Z + 0.15, GOLD, app, loc=POT)
ring("neck_collar", 0.2, 0.14, HEL_Z - 0.03, HEL_Z + 0.03, GOLD, app, loc=POT)
COL_Z0, COL_Z1, COL_R = HEL_Z + 0.3, HEL_Z + 0.95, 0.13
cyl("column", COL_R, COL_Z1 - COL_Z0, (POT.x, POT.y, (COL_Z0 + COL_Z1) / 2), BRASS, app, verts=40)
for z in (COL_Z0 + 0.03, COL_Z0 + 0.33, COL_Z1 - 0.03):
    ring(f"column_ring{z:.2f}", COL_R + 0.03, COL_R - 0.01, z - 0.03, z + 0.03, GOLD, app,
         loc=POT, segs=40)
VAP = []
for k, z in enumerate((COL_Z0 + 0.18, COL_Z0 + 0.48)):
    a = math.radians(-80)
    c = POT + Vector((COL_R * math.cos(a), COL_R * math.sin(a), z))
    holder = bpy.data.objects.new(f"col_glass{k}", None)
    link(holder, app)
    holder.location = c
    holder.rotation_euler = Vector((0, 0, 1)).rotation_difference(
        Vector((math.cos(a), math.sin(a), 0))).to_euler()
    ring(f"col_glass_bezel{k}", 0.065, 0.045, -0.005, 0.025, GOLD, holder, segs=32)
    v = cyl(f"col_glass_vapour{k}", 0.047, 0.012, (0, 0, 0.004), VAPOUR, holder, verts=24)
    glow(v)
lathe("column_dome", [(COL_R + 0.03, COL_Z1), (COL_R + 0.035, COL_Z1 + 0.03), (0.12, COL_Z1 + 0.1),
                      (0.06, COL_Z1 + 0.15), (0.0, COL_Z1 + 0.16)], GOLD, app, loc=POT, segs=40)
sphere("column_finial", 0.04, (POT.x, POT.y, COL_Z1 + 0.19), RUBY, app)
# safety valve: weighted lever on the helmet, pops a little with every boil surge
SV = POT + Vector((0.16, 0.12, HEL_Z + 0.28))
cyl("valve_body", 0.035, 0.08, SV, BRASS, app)
valve_lever = bpy.data.objects.new("valve_lever", None)
link(valve_lever, app)
valve_lever.location = SV + Vector((0, 0, 0.05))
box("valve_arm", (0.22, 0.022, 0.022), (0.1, 0, 0), STEEL, valve_lever, bevel=0.005)
sphere("valve_weight", 0.035, (0.21, 0, 0), GOLD, valve_lever)

# pressure gauge on a stem off the helmet, dial tilted to face the viewer
GAUGE_C = POT + Vector((-0.17, -0.27, HEL_Z + 0.17))
cyl("gauge_stem", 0.018, 0.1, POT + Vector((-0.12, -0.2, HEL_Z + 0.15)), BRASS, app,
    rot=(math.radians(60), 0, math.radians(-30)))
gauge = bpy.data.objects.new("gauge", None)
link(gauge, app)
gauge.location = GAUGE_C
gauge.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector((-0.25, -0.75, 0.62))).to_euler()
cyl("gauge_case", 0.085, 0.04, (0, 0, -0.02), BRASS, gauge, verts=32)
ring("gauge_bezel", 0.09, 0.07, 0.0, 0.02, GOLD, gauge, segs=32)
cyl("gauge_face", 0.07, 0.004, (0, 0, 0.004), IVORY, gauge, verts=32)
for k in range(9):    # tick marks over a 270 degree scale
    a = math.radians(225 - 270 * k / 8)
    box(f"gauge_tick{k}", (0.016, 0.005, 0.004), (0.055 * math.cos(a), 0.055 * math.sin(a), 0.008),
        SOOT, gauge, rot=(0, 0, a), bevel=0)
box("gauge_red", (0.02, 0.008, 0.004), (0.055 * math.cos(math.radians(-45)),
                                        0.055 * math.sin(math.radians(-45)), 0.009), RUBY, gauge,
    rot=(0, 0, math.radians(-45)), bevel=0)
needle = bpy.data.objects.new("gauge_needle", None)
link(needle, gauge)
needle.location = (0, 0, 0.012)
box("needle_bar", (0.06, 0.008, 0.004), (0.022, 0, 0), RUBY, needle, bevel=0)
sphere("needle_hub", 0.01, (0, 0, 0), GOLD, needle)

# ingredient hopper at the back-left: inserters drop the herbs in, a chute
# feeds them into the pot shoulder
HOP = Vector((-0.92, 0.98, 0.0))
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f"hopper_leg{sx}{sy}", (0.04, 0.04, 0.72), (HOP.x + sx * 0.14, HOP.y + sy * 0.14, Z_D + 0.36),
            BRONZE, app, bevel=0.008)
lathe("hopper", [(0.06, Z_D + 0.7), (0.08, Z_D + 0.72), (0.22, Z_D + 0.98), (0.235, Z_D + 1.02),
                 (0.215, Z_D + 1.02), (0.2, Z_D + 0.99), (0.0, Z_D + 0.93)], COPPER, app, loc=HOP, segs=40)
ring("hopper_rim", 0.25, 0.2, Z_D + 0.995, Z_D + 1.04, GOLD, app, loc=HOP, segs=40)
ring("hopper_band", 0.16, 0.13, Z_D + 0.84, Z_D + 0.88, GOLD, app, loc=HOP, segs=40)
lathe("hopper_herbs", [(0.205, Z_D + 0.985), (0.16, Z_D + 1.03), (0.08, Z_D + 1.06), (0.0, Z_D + 1.07)],
      HERB, app, loc=HOP, segs=32)
for k in range(8):
    a = TAU * k / 8
    sphere(f"herb{k}", 0.035 + 0.01 * (k % 3), (HOP.x + 0.12 * math.cos(a), HOP.y + 0.12 * math.sin(a),
                                               Z_D + 1.02 + 0.015 * (k % 2)), HERB, app, segs=8)
    sphere(f"hopper_gem{k}", 0.018, (HOP.x + 0.24 * math.cos(a), HOP.y + 0.24 * math.sin(a), Z_D + 1.02),
           RUBY if k % 2 else GOLD, app)
curve_obj("hopper_chute", [(HOP.x, HOP.y, Z_D + 0.7), (HOP.x + 0.06, HOP.y - 0.15, Z_D + 0.62),
                           (POT.x - 0.38, POT.y + 0.3, POT_Z + 0.48)], BRASS, 0.05, app, res=3)
ring("chute_collar", 0.075, 0.04, -0.03, 0.03, GOLD, app, loc=(POT.x - 0.37, POT.y + 0.29, POT_Z + 0.48))

# ----------------------------------------------------------------------------
# Condenser: swan neck -> worm tub -> spirit safe -> spout
# ----------------------------------------------------------------------------
TUB = Vector((0.8, 0.64, 0.0))
TUB_R, TUB_Z0, TUB_Z1 = 0.44, 1.1, 1.8
# stand: purple drum with gold legs, carrying the tub high enough for the
# distillate to fall to the flasks
lathe("tub_stand", [(0.3, Z_D), (0.3, TUB_Z0 - 0.06), (0.36, TUB_Z0 - 0.02), (0.36, TUB_Z0),
                    (0.0, TUB_Z0)], PURPLE, app, loc=TUB, segs=48)
for k in range(4):
    a = TAU * (k + 0.5) / 4
    p0 = TUB + Vector((0.38 * math.cos(a), 0.38 * math.sin(a), Z_D))
    p1 = TUB + Vector((0.33 * math.cos(a), 0.33 * math.sin(a), TUB_Z0))
    rail(f"tub_leg{k}", [p0, p1], 0.045, parent=app)
    sphere(f"tub_foot{k}", 0.05, tuple(p0 + Vector((0, 0, 0.02))), GOLD, app)
sp_stand = Panel(tuple(TUB + Vector((-0.13, -0.3, Z_D + 0.06))), tuple(TUB + Vector((0.13, -0.3, Z_D + 0.06))),
                 tuple(TUB + Vector((0.13, -0.3, TUB_Z0 - 0.1))), tuple(TUB + Vector((-0.13, -0.3, TUB_Z0 - 0.1))))
sp_stand.filigree("tub_stand_fil", lyre(0.5, 0.5, 1.0, 1.0), radius=0.022, lift=0.0, parent=app)
# staved bronze tub with heavy gold hoops
lathe("tub", [(TUB_R - 0.02, TUB_Z0), (TUB_R, TUB_Z0 + 0.02), (TUB_R + 0.02, (TUB_Z0 + TUB_Z1) / 2),
              (TUB_R, TUB_Z1), (TUB_R - 0.04, TUB_Z1), (TUB_R - 0.04, TUB_Z1 - 0.1),
              (0.0, TUB_Z1 - 0.1)], BRONZE, app, loc=TUB, segs=64)
for k in range(24):
    a = TAU * k / 24
    box(f"tub_stave{k}", (0.012, 0.03, TUB_Z1 - TUB_Z0 - 0.04),
        (TUB.x + (TUB_R + 0.013) * math.cos(a), TUB.y + (TUB_R + 0.013) * math.sin(a),
         (TUB_Z0 + TUB_Z1) / 2), BRASS, app, rot=(0, 0, a), bevel=0.004)
for k, z in enumerate((TUB_Z0 + 0.07, (TUB_Z0 + TUB_Z1) / 2, TUB_Z1 - 0.04)):
    r = TUB_R + (0.02 if k == 1 else 0.005)
    ring(f"tub_hoop{k}", r + 0.04, r - 0.01, z - 0.035, z + 0.035, GOLD, app, loc=TUB, segs=64)
    for m in range(10):
        a = TAU * (m + 0.5 * k) / 10
        sphere(f"tub_hoop{k}_gem{m}", 0.022, (TUB.x + (r + 0.04) * math.cos(a),
                                               TUB.y + (r + 0.04) * math.sin(a), z),
               RUBY if m % 2 else GOLD, app)
WATER_Z = TUB_Z1 - 0.07
water = cyl("tub_water", TUB_R - 0.04, 0.01, (TUB.x, TUB.y, WATER_Z), WATER, app, verts=48)
# coil: comes in over the rim, top turn arches out of the water, then spirals
# down through the coolant and leaves the tub low at the front
COIL_R = 0.29
coil = []
a0 = math.radians(150)
for i in range(160):
    t = i / 159
    a = a0 - t * 3.25 * TAU
    # first ~0.8 turn rides just above the coolant, then the coil dives
    z = WATER_Z + 0.045 - max(0.0, t - 0.25) / 0.75 * (WATER_Z - TUB_Z0 - 0.12)
    coil.append((TUB.x + COIL_R * math.cos(a), TUB.y + COIL_R * math.sin(a), z))
curve_obj("worm_coil", coil, COPPER, 0.035, app, res=3)

# swan neck from the column head down to the coil inlet
LYNE = [(POT.x + 0.05, POT.y, COL_Z1 + 0.08), (POT.x + 0.2, POT.y + 0.02, COL_Z1 + 0.13),
        (0.05, 0.44, COL_Z1 + 0.12), (0.3, 0.52, COL_Z1 - 0.02), (0.5, 0.58, WATER_Z + 0.45),
        (0.62, 0.62, WATER_Z + 0.22), coil[0][:2] + (WATER_Z + 0.12,), coil[0]]
curve_obj("swan_neck", LYNE, COPPER_POT, 0.06, app, res=4,
          taper=lambda t: 1.25 - 0.55 * t)
for k, t in enumerate((0.12, 0.38, 0.62)):
    i = int(t * (len(LYNE) - 1))
    p = Vector(LYNE[i]).lerp(Vector(LYNE[i + 1]), (t * (len(LYNE) - 1)) % 1)
    d = (Vector(LYNE[i + 1]) - Vector(LYNE[i])).normalized()
    o = ring(f"neck_band{k}", 0.085 - 0.012 * k, 0.03, -0.022, 0.022, GOLD, app, loc=tuple(p))
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()

# spirit safe: locked gold-framed glass box where the distillate is checked
SAFE = Vector((0.6, -0.1, 1.2))
SAFE_SZ = Vector((0.26, 0.2, 0.18))
outlet = [(TUB.x - 0.2, TUB.y - TUB_R + 0.05, TUB_Z0 + 0.12), (TUB.x - 0.2, TUB.y - TUB_R - 0.06, TUB_Z0 + 0.11),
          (SAFE.x, SAFE.y + SAFE_SZ.y / 2 + 0.1, SAFE.z + 0.06), (SAFE.x, SAFE.y + SAFE_SZ.y / 2, SAFE.z + 0.04)]
curve_obj("tub_outlet", outlet, COPPER, 0.032, app, res=3)
cyl("safe_pedestal", 0.06, SAFE.z - SAFE_SZ.z / 2 - Z_D, (SAFE.x, SAFE.y, (SAFE.z - SAFE_SZ.z / 2 + Z_D) / 2),
    BRONZE, app, verts=24)
cyl("safe_foot", 0.1, 0.05, (SAFE.x, SAFE.y, Z_D + 0.025), GOLD, app, verts=24)
safe_liq = box("safe_liquid", (SAFE_SZ.x - 0.04, SAFE_SZ.y - 0.04, 0.05),
               (SAFE.x, SAFE.y, SAFE.z - SAFE_SZ.z / 2 + 0.04), POTION, app, bevel=0.01)
glow(safe_liq)
safe_glass = box("safe_glass", tuple(SAFE_SZ - Vector((0.01, 0.01, 0.01))), tuple(SAFE), FLASK_GLASS, app,
                 bevel=0.004)
glow(safe_glass)
# hydrometer float bobbing in the safe's sample cup
hydro = sphere("safe_float", 0.025, (SAFE.x + 0.05, SAFE.y, SAFE.z - 0.02), GOLD, app, segs=12)
hx, hy, hz = SAFE_SZ / 2
corners = [Vector((sx * hx, sy * hy, sz * hz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
for a in corners:
    for b in corners:
        if (b - a).length > 1e-6 and sum(abs(c) < 1e-6 for c in (b - a)) == 2 and \
                (b - a).dot(Vector((1, 1, 1))) > 0:
            rail(f"safe_edge{tuple(a)}{tuple(b)}", [SAFE + a, SAFE + b], 0.016, parent=app)
box("safe_lid", (SAFE_SZ.x + 0.04, SAFE_SZ.y + 0.04, 0.03), tuple(SAFE + Vector((0, 0, hz + 0.015))), GOLD,
    app, bevel=0.01)
sphere("safe_lock", 0.03, tuple(SAFE + Vector((0, -hy - 0.012, hz - 0.02))), RUBY, app)
for sx in (-1, 1):
    sphere(f"safe_knob{sx}", 0.022, tuple(SAFE + Vector((sx * (hx - 0.03), -hy - 0.01, -hz + 0.03))), GOLD,
           app)

# ----------------------------------------------------------------------------
# Flask carousel on a Geneva drive
# ----------------------------------------------------------------------------
#
# The carousel plate IS the Geneva wheel (4 slots); a pin on the driver disc
# enters a slot, turns the plate a quarter turn and leaves it, the driver's
# locking disc then holds the plate still. One driver revolution per loop:
# frames 0..IDX0-1 dwell (fill / decant), IDX0..N-1 index. 4-fold symmetry
# makes the loop seamless.
CAR = Vector((0.72, -0.74, 0.0))
G_R = 0.42                       # plate radius
G_C = G_R * S2                   # centre distance, 4-slot Geneva
G_A = G_R                        # driver pin radius (= G_C sin 45)
LOCK_R = 0.3                    # locking arc radius
SLOT_W = 0.04                    # slot half width
PIN_R = 0.03
DRV = CAR - Vector((G_C, 0, 0))
PLATE_Z0, PLATE_Z1 = Z_D + 0.1, Z_D + 0.15
IDX0 = 48
FL_RAD = 0.2                    # flask circle radius on the plate
FL_R = 0.072                     # flask bulb radius
VALVE_OPEN, VALVE_CLOSE = 4, 42
BOT_H = 0.17                     # bottle body height
DRAIN_OPEN, DRAIN_CLOSE = 8, 40


def geneva_outline():
    """Plate outline: 4 radial slots, with a concave locking arc (for the
    driver's locking disc) between each pair of slots."""
    pts = []
    beta = math.acos((G_R ** 2 + G_C ** 2 - LOCK_R ** 2) / (2 * G_R * G_C))
    slot_in = G_C - G_A - 0.01
    ds = math.asin(SLOT_W / G_R)

    def wrap(a):
        return (a + math.pi) % TAU - math.pi

    for k in range(4):
        s = TAU * k / 4
        dirv = Vector((math.cos(s), math.sin(s)))
        nrm = Vector((-math.sin(s), math.cos(s)))
        bot = dirv * slot_in
        pts.append(tuple(Vector((math.cos(s - ds), math.sin(s - ds))) * G_R))
        for i in range(9):
            t = math.pi * i / 8
            pts.append(tuple(bot + (-nrm * math.cos(t) - dirv * math.sin(t)) * SLOT_W))
        pts.append(tuple(Vector((math.cos(s + ds), math.sin(s + ds))) * G_R))
        m = s + TAU / 8
        M = Vector((math.cos(m), math.sin(m))) * G_C
        p1 = Vector((math.cos(m - beta), math.sin(m - beta))) * G_R
        p2 = Vector((math.cos(m + beta), math.sin(m + beta))) * G_R
        for a in (s + ds + 0.5 * (m - beta - s - ds),):
            pts.append((G_R * math.cos(a), G_R * math.sin(a)))
        a1 = math.atan2(p1.y - M.y, p1.x - M.x)
        a2 = math.atan2(p2.y - M.y, p2.x - M.x)
        am = math.atan2(-M.y, -M.x)
        d2, d1 = wrap(a2 - a1), wrap(am - a1)
        if not (d1 * d2 > 0 and abs(d1) < abs(d2)):
            d2 -= math.copysign(TAU, d2)
        pts += [tuple(M + LOCK_R * Vector((math.cos(a1 + d2 * i / 16), math.sin(a1 + d2 * i / 16))))
                for i in range(17)]
        a = m + beta + 0.5 * (s + TAU / 4 - ds - m - beta)
        pts.append((G_R * math.cos(a), G_R * math.sin(a)))
    return pts


def extrude(name, poly, z0, z1, mat, parent, bevel=0.006):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    o = mesh_obj(name, bm, mat, parent, bevel=bevel)
    o.data.shade_flat()
    return o


plate = bpy.data.objects.new("carousel", None)
link(plate, app)
plate.location = (CAR.x, CAR.y, 0)
extrude("geneva_plate", geneva_outline(), PLATE_Z0, PLATE_Z1, BRASS, plate)
cyl("plate_hub", 0.07, PLATE_Z1 - Z_D + 0.08, (0, 0, (PLATE_Z1 + Z_D + 0.08) / 2), GOLD, plate, verts=32)
# central post with a crown finial
lathe("plate_crown", [(0.085, PLATE_Z1), (0.09, PLATE_Z1 + 0.03), (0.06, PLATE_Z1 + 0.08),
                      (0.0, PLATE_Z1 + 0.1)], GOLD, plate, segs=24)
sphere("plate_crown_gem", 0.03, (0, 0, PLATE_Z1 + 0.11), RUBY, plate)
for k in range(4):     # gold cup holders for the flasks, struts to the post
    a = TAU * (k + 0.5) / 4
    c = Vector((FL_RAD * math.cos(a), FL_RAD * math.sin(a), 0))
    ring(f"cup{k}", FL_R + 0.02, FL_R - 0.005, PLATE_Z1, PLATE_Z1 + 0.05, GOLD, plate,
         loc=tuple(c), segs=32)
    s_ = TAU * k / 4      # ruby at the mouth of each slot pair's horn
    sphere(f"slot_gem{k}", 0.02, (0.085 * math.cos(s_ + TAU / 8), 0.085 * math.sin(s_ + TAU / 8),
                                  PLATE_Z1 + 0.01), RUBY, plate)
FLASKS = []
for k in range(4):
    a = TAU * (k + 0.5) / 4
    fl = bpy.data.objects.new(f"flask{k}", None)
    link(fl, plate)
    fl.location = (FL_RAD * math.cos(a), FL_RAD * math.sin(a), PLATE_Z1 + 0.012)
    # potion bottle: straight body (the level reads from the camera), round
    # shoulder, short neck with a gold lip
    g = lathe(f"flask{k}_glass", [(FL_R - 0.01, 0.0), (FL_R, 0.01), (FL_R, BOT_H), (FL_R * 0.7, BOT_H + 0.035),
                                  (0.025, BOT_H + 0.05), (0.025, BOT_H + 0.1), (0.0, BOT_H + 0.1)],
              FLASK_GLASS, fl, segs=24)
    n_ = g
    cyl(f"flask{k}_lip", 0.033, 0.016, (0, 0, BOT_H + 0.095), GOLD, fl, verts=20)
    ring(f"flask{k}_band", FL_R + 0.008, FL_R - 0.004, BOT_H * 0.55, BOT_H * 0.55 + 0.02, GOLD, fl, segs=24)
    glow(g)
    glow(n_)
    FLASKS.append(fl)

# driver: locking disc with its clearance cut, crank arm, pin
drv = bpy.data.objects.new("geneva_driver", None)
link(drv, app)
drv.location = (DRV.x, DRV.y, 0)
lock_pts = []
cut_c = Vector((G_C, 0))          # wheel centre when the pin is on the centre line
for i in range(96):
    a = TAU * i / 96
    p = Vector((math.cos(a), math.sin(a))) * (LOCK_R - 0.012)
    if (p - cut_c).length < G_R + 0.02:
        # project onto the clearance circle round the passing wheel horns
        p = cut_c + (p - cut_c).normalized() * (G_R + 0.02)
        if p.length > LOCK_R - 0.012:
            continue
    lock_pts.append(tuple(p))
extrude("lock_disc", lock_pts, PLATE_Z0, PLATE_Z1, STEEL, drv)
cyl("driver_hub", 0.06, 0.12, (0, 0, PLATE_Z1 + 0.05), BRASS, drv, verts=24)
box("driver_arm", (G_A, 0.07, 0.035), (G_A / 2, 0, PLATE_Z1 + 0.04), GOLD, drv, bevel=0.012)
cyl("driver_pin", PIN_R, PLATE_Z1 - PLATE_Z0 + 0.06, (G_A, 0, (PLATE_Z0 + PLATE_Z1) / 2 + 0.02), STEEL, drv,
    verts=16)
sphere("driver_pin_cap", 0.035, (G_A, 0, PLATE_Z1 + 0.06), RUBY, drv)
cyl("driver_base", 0.09, PLATE_Z0 - Z_D, (0, 0, (PLATE_Z0 + Z_D) / 2), BRONZE, drv, verts=24)


def driver_angle(f):
    """Driver turns CCW once per loop; the pin leaves the slot at frame 0."""
    return math.radians(45) + TAU * f / N


def plate_angle(f):
    """Plate rotation (slot 0 direction) from the Geneva geometry."""
    phi = (driver_angle(f) + math.pi) % TAU - math.pi     # pin angle, -pi..pi
    if f < IDX0:
        return math.radians(135)
    # engaged slot points from the wheel centre at the pin
    slot = math.atan2(G_A * math.sin(phi), G_A * math.cos(phi) - G_C)
    return slot - math.radians(90)


# engagement must start exactly at IDX0 and the pin must sit in the slot
assert abs(((driver_angle(IDX0) + math.pi) % TAU - math.pi) + math.pi / 4) < 1e-6
assert abs(math.degrees(plate_angle(N - 1)) - 45) < 10

# spout from the safe to the fill station
FILL = CAR + Vector((0, FL_RAD, 0))      # north station
SPOUT_TIP = Vector((FILL.x, FILL.y, 1.14))
spout = [(SAFE.x - 0.06, SAFE.y - hy, SAFE.z - 0.02), (SAFE.x - 0.08, SAFE.y - hy - 0.08, SAFE.z - 0.03),
         (FILL.x + 0.02, FILL.y + 0.06, SPOUT_TIP.z + 0.04), tuple(SPOUT_TIP + Vector((0, 0, 0.03))),
         tuple(SPOUT_TIP)]
curve_obj("spout", spout, COPPER, 0.026, app, res=3)
cyl("spout_nozzle", 0.03, 0.05, SPOUT_TIP + Vector((0, 0, 0.0)), GOLD, app, r2=0.022, verts=20)
# valve on the spout with a handle that swings open and shut
VALVE = Vector(spout[1]) + Vector((0, 0, 0.0))
cyl("spout_valve", 0.035, 0.06, VALVE, BRASS, app, verts=20)
valve_handle = bpy.data.objects.new("valve_handle", None)
link(valve_handle, app)
valve_handle.location = VALVE + Vector((0, 0, 0.04))
box("valve_handle_bar", (0.11, 0.02, 0.016), (0.045, 0, 0), RUBY, valve_handle, bevel=0.004)
sphere("valve_handle_knob", 0.016, (0, 0, 0), GOLD, valve_handle)

# decanting station (south): a fixed tap-opener under the plate drains the
# flask into a gold gutter that spills into the output chute in the deck
DECANT = CAR + Vector((0, -FL_RAD, 0))
gutter_end = Vector((DECANT.x, YF + 0.02, Z_D + 0.06))
curve_obj("gutter", [(DECANT.x, DECANT.y + 0.04, PLATE_Z0 - 0.02), (DECANT.x, DECANT.y - 0.1, Z_D + 0.07),
                     tuple(gutter_end)], GOLD, 0.022, app, res=2)
CHUTE = Vector((DECANT.x, YF - 0.02, Z_D))
ring("chute_funnel", 0.075, 0.05, -0.03, 0.02, GOLD, app, loc=CHUTE, segs=32)
cyl("chute_hole", 0.05, 0.01, CHUTE + Vector((0, 0, -0.01)), SOOT, app, verts=24)
cyl("decant_opener", 0.025, PLATE_Z0 - Z_D, (DECANT.x, DECANT.y, (PLATE_Z0 + Z_D) / 2), STEEL, app,
    verts=12)

# ----------------------------------------------------------------------------
# Hot-air engine: heat chamber -> piston -> crank -> bevel pair -> Geneva driver
# ----------------------------------------------------------------------------
#
# Its hot end sits in the heat chamber; the crankshaft runs east along the
# front and drives the Geneva driver's vertical shaft through a 1:2 bevel pair
# (engine 2 revolutions per loop, driver 1).
SH_Y, SH_Z = DRV.y, Z_D + 0.4      # crankshaft line
ENG_X = -0.62
CRANK_R, ROD_L = 0.07, 0.22
FLY_X, FLY_R = -0.98, 0.32
SH_X0, SH_X1 = -0.98 + 0.08, DRV.x - 0.17
BEV_S, BEV_B = 0.075, 0.15
rx = (math.radians(90), 0, 0)
ry = (0, math.radians(90), 0)

cyl("crankshaft", 0.028, SH_X1 - SH_X0, ((SH_X0 + SH_X1) / 2, SH_Y, SH_Z), STEEL, app, rot=ry, verts=16)
for k, x in enumerate((-0.84, -0.42)):
    box(f"pillow{k}", (0.1, 0.13, SH_Z - Z_D), (x, SH_Y, (SH_Z + Z_D) / 2 - 0.02), BRONZE, app, bevel=0.015)
    cyl(f"pillow_cap{k}", 0.06, 0.11, (x, SH_Y, SH_Z), BRASS, app, rot=ry, verts=24)
    sphere(f"pillow_gem{k}", 0.02, (x, SH_Y - 0.06, SH_Z + 0.02), RUBY, app)

shaft = bpy.data.objects.new("shaft_rot", None)   # everything turning with the crankshaft
link(shaft, app)
shaft.location = (0, SH_Y, SH_Z)
shaft.rotation_mode = "XYZ"
# west end: bevel pair up to a flyball governor (a flywheel on this shaft
# would be seen exactly edge-on by Factorio's camera)
GOV = Vector((-0.98, SH_Y, 0.0))
GOV_TOP = SH_Z + 0.78
ARM_L, LINK_L = 0.3, 0.15
gbev = bpy.data.objects.new("gov_bevel_shaft", None)
link(gbev, shaft)
gbev.location = (GOV.x + 0.1, 0, 0)
gbev.rotation_euler = (0, math.radians(-90), 0)      # cone points west, to the spindle
gov = bpy.data.objects.new("governor", None)
link(gov, app)
gov.location = (GOV.x, GOV.y, 0)
cyl("gov_spindle", 0.028, GOV_TOP - SH_Z + 0.12, (0, 0, (GOV_TOP + SH_Z) / 2 - 0.04), STEEL, gov, verts=12)
gb = bpy.data.objects.new("gov_bevel", None)
link(gb, gov)
gb.location = (0, 0, SH_Z + BEV_S + 0.02)
gb.rotation_euler = (math.pi, 0, 0)                  # cone points down to the shaft
lathe("gov_cap", [(0.05, GOV_TOP - 0.02), (0.055, GOV_TOP + 0.03), (0.03, GOV_TOP + 0.07), (0.0, GOV_TOP + 0.08)],
      GOLD, gov, segs=24)
sphere("gov_cap_gem", 0.026, (0, 0, GOV_TOP + 0.1), RUBY, gov)
sleeve = cyl("gov_sleeve", 0.04, 0.06, (0, 0, 0), BRASS, gov, verts=20)
GOV_ARMS = []
for sgn in (-1, 1):
    arm = bpy.data.objects.new(f"gov_arm{sgn}", None)
    link(arm, gov)
    arm.location = (sgn * 0.02, 0, GOV_TOP)
    box(f"gov_arm{sgn}_bar", (0.032, 0.032, ARM_L), (0, 0, -ARM_L / 2), BRASS, arm, bevel=0.005)
    sphere(f"gov_ball{sgn}", 0.08, (0, 0, -ARM_L), GOLD, arm, segs=16)
    lk = bpy.data.objects.new(f"gov_link{sgn}", None)
    link(lk, gov)
    box(f"gov_link{sgn}_bar", (0.018, 0.018, LINK_L), (0, 0, LINK_L / 2), STEEL, lk, bevel=0.004)
    GOV_ARMS.append((sgn, arm, lk))
box("gov_bracket", (0.05, 0.05, SH_Z - Z_D - 0.05), (GOV.x, GOV.y - 0.0, (SH_Z + Z_D) / 2 - 0.05), BRONZE,
    app, bevel=0.01)


def pose_governor(f):
    # 1:1 bevels: the spindle turns twice per loop; the balls fly out a little
    # further on every boil surge (the engine speeds up)
    gov.rotation_euler = (0, 0, -crank_angle(f))
    th = math.radians(42 + 5 * math.sin(4 * TAU * f / N))
    zs = GOV_TOP - 2 * (ARM_L / 2) * math.cos(th)
    sleeve.location = (0, 0, zs)
    for sgn, arm, lk in GOV_ARMS:
        arm.rotation_euler = (0, -sgn * th, 0)
        lk.location = (sgn * 0.02, 0, zs)
        lk.rotation_euler = (0, sgn * th, 0)


# crank disc and pin at the engine line
cd = bpy.data.objects.new("crank_disc", None)
link(cd, shaft)
cd.location = (ENG_X + 0.05, 0, 0)
cd.rotation_euler = ry
cyl("crank_web", 0.1, 0.035, (0, 0, 0), BRASS, cd, verts=32)
# crank pin at local +y of the shaft frame (child of the Ry frame: local y stays y)
cyl("crank_pin", 0.02, 0.07, (0, CRANK_R, -0.035), STEEL, cd, verts=12)
# small bevel at the east end of the shaft
sbev = bpy.data.objects.new("bevel_small", None)
link(sbev, shaft)
sbev.location = (SH_X1 - 0.03, 0, 0)
sbev.rotation_euler = ry


def bevel(name, teeth, r, parent, mat):
    """Bevel gear as a toothed cone frustum, axis local z, wide end at z=0."""
    outer = []
    for k in range(teeth):
        a, da = TAU * k / teeth, TAU / teeth
        for frac, rad in ((0.0, 0.9), (0.18, 1.08), (0.5, 1.08), (0.68, 0.9)):
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


bevel("bevel_small_g", 10, BEV_S, sbev, BRASS)
bevel("gov_bevel_a", 10, BEV_S, gbev, BRASS)
bevel("gov_bevel_b", 10, BEV_S, gb, GOLD)
# big bevel on the driver's vertical shaft, under the crankshaft
bbev = bpy.data.objects.new("bevel_big", None)
link(bbev, drv)
bbev.location = (0, 0, SH_Z - BEV_S - 0.05)
bevel("bevel_big_g", 20, BEV_B, bbev, GOLD)
cyl("driver_shaft", 0.025, SH_Z + 0.1 - PLATE_Z1, (0, 0, (SH_Z + 0.1 + PLATE_Z1) / 2), STEEL, drv,
    verts=12)
# bridge carrying the top bearing, standing outside the pin's sweep
BR_Y = DRV.y + G_A + 0.1
box("driver_bracket", (0.06, 0.06, SH_Z + 0.1 - Z_D), (DRV.x, BR_Y, (SH_Z + 0.1 + Z_D) / 2), BRONZE, app,
    bevel=0.012)
box("driver_bracket_top", (0.06, DRV.y - BR_Y, 0.05), (DRV.x, (DRV.y + BR_Y) / 2, SH_Z + 0.1), BRONZE, app,
    bevel=0.012)
cyl("driver_bearing", 0.05, 0.07, (DRV.x, DRV.y, SH_Z + 0.1), BRASS, app, verts=20)
sphere("driver_bearing_gem", 0.025, (DRV.x, DRV.y, SH_Z + 0.15), RUBY, app)

# engine cylinder: hot end buried in the heat chamber (finned, glowing),
# cold end with cooling fins, crosshead guides towards the crank
ENG_Y0 = POT.y - math.sqrt(FB_R ** 2 - (ENG_X - POT.x) ** 2) + 0.06   # inside the chamber wall
ENG_Y1 = SH_Y + 0.42
cyl("engine_cyl", 0.1, ENG_Y0 - ENG_Y1, (ENG_X, (ENG_Y0 + ENG_Y1) / 2, SH_Z), BRASS, app, rot=rx, verts=32)
for k in range(3):
    y = ENG_Y0 - 0.07 - k * 0.035
    o = ring(f"hot_fin{k}", 0.13, 0.08, -0.008, 0.008, HOT, app, loc=(ENG_X, y, SH_Z), segs=32)
    o.rotation_euler = rx
    heat(o)
for k in range(2):
    y = ENG_Y1 + 0.04 + k * 0.04
    o = ring(f"cold_fin{k}", 0.125, 0.08, -0.01, 0.01, GOLD, app, loc=(ENG_X, y, SH_Z), segs=32)
    o.rotation_euler = rx
o = ring("engine_flange", 0.12, 0.06, -0.015, 0.015, GOLD, app, loc=(ENG_X, ENG_Y1, SH_Z), segs=32)
o.rotation_euler = rx
box("engine_saddle", (0.16, 0.24, SH_Z - Z_D - 0.06), (ENG_X, ENG_Y1 + 0.1, (SH_Z + Z_D) / 2 - 0.04),
    BRONZE, app, bevel=0.015)
GUIDE_Y0, GUIDE_Y1 = ENG_Y1, SH_Y + 0.12
for sx in (-1, 1):
    box(f"guide{sx}", (0.025, GUIDE_Y0 - GUIDE_Y1, 0.04),
        (ENG_X + sx * 0.055, (GUIDE_Y0 + GUIDE_Y1) / 2, SH_Z), STEEL, app, bevel=0.005)
piston_rod = cyl("piston_rod", 0.018, 1.0, (ENG_X, 0, SH_Z), STEEL, app, rot=rx, verts=12)
crosshead = box("crosshead", (0.08, 0.06, 0.06), (ENG_X, 0, SH_Z), BRASS, app, bevel=0.01)
conrod = bpy.data.objects.new("conrod", None)
link(conrod, app)
box("conrod_bar", (0.03, 1.0, 0.025), (0, 0.5, 0), GOLD, conrod, bevel=0.006)
ENG_BETA0 = math.radians(90)


def crank_angle(f):
    # shaft turns negatively about +x (see the bevel sense), 2 revs per loop
    return ENG_BETA0 - 2 * TAU * f / N


def pose_engine(f):
    b = crank_angle(f)
    shaft.rotation_euler = (b, 0, 0)
    pin = Vector((ENG_X, SH_Y + CRANK_R * math.cos(b), SH_Z + CRANK_R * math.sin(b)))
    dz = pin.z - SH_Z
    yc = pin.y + math.sqrt(ROD_L ** 2 - dz ** 2)
    crosshead.location = (ENG_X, yc, SH_Z)
    piston_rod.location = (ENG_X, (yc + ENG_Y1 + 0.05) / 2, SH_Z)
    piston_rod.scale = (1, 1, ENG_Y1 + 0.05 - yc)
    d = Vector((ENG_X, yc, SH_Z)) - pin
    conrod.location = pin
    conrod.scale = (1, d.length, 1)
    conrod.rotation_euler = (math.atan2(d.z, d.y), 0, 0)
    # big bevel: 20 teeth vs 10, driver turns once per loop
    drv.rotation_euler = (0, 0, driver_angle(f))


animated.append((None, lambda o, f: pose_engine(f)))

# --- coolant pump: an eccentric on the crankshaft works a plunger pump that
# pushes cold coolant up into the worm tub; the warm water returns from the
# tub's foot along the deck to the pump's suction (a closed circuit).
PUMP_X = -0.2
ECC_E, ECC_ROD = 0.035, 0.26
PUMP_Z0, PUMP_Z1 = SH_Z + 0.2, SH_Z + 0.48
ecc = bpy.data.objects.new("eccentric", None)
link(ecc, shaft)
ecc.location = (PUMP_X, 0, 0)
ecc.rotation_euler = ry
# sheave offset by ECC_E along local y (y stays y under the Ry frame)
cyl("ecc_sheave", 0.065, 0.05, (0, ECC_E, 0), BRASS, ecc, verts=32)
strap = bpy.data.objects.new("ecc_strap", None)
link(strap, app)
ring("ecc_strap_ring", 0.085, 0.064, -0.022, 0.022, GOLD, strap, segs=32).rotation_euler = ry
ecc_rod = box("ecc_rod", (0.03, 0.03, 1.0), (0, 0, 0.5), STEEL, strap, bevel=0.006)
cyl("pump_barrel", 0.075, PUMP_Z1 - PUMP_Z0, (PUMP_X, SH_Y, (PUMP_Z0 + PUMP_Z1) / 2), BRASS, app, verts=32)
for z in (PUMP_Z0 + 0.02, PUMP_Z1 - 0.02):
    ring(f"pump_band{z:.2f}", 0.095, 0.07, z - 0.025, z + 0.025, GOLD, app, loc=(PUMP_X, SH_Y, 0), segs=32)
lathe("pump_air_vessel", [(0.08, PUMP_Z1), (0.09, PUMP_Z1 + 0.06), (0.085, PUMP_Z1 + 0.16),
                          (0.05, PUMP_Z1 + 0.22), (0.0, PUMP_Z1 + 0.235)], COPPER_POT, app,
      loc=(PUMP_X, SH_Y, 0), segs=32)
sphere("pump_finial", 0.03, (PUMP_X, SH_Y, PUMP_Z1 + 0.25), RUBY, app)
for sx in (-1, 1):   # frame carrying the pump over the crankshaft
    box(f"pump_post{sx}", (0.035, 0.035, PUMP_Z0 - Z_D + 0.03),
        (PUMP_X + sx * 0.15, SH_Y + 0.09, (PUMP_Z0 + Z_D) / 2), BRONZE, app, bevel=0.008)
box("pump_yoke", (0.34, 0.05, 0.04), (PUMP_X, SH_Y + 0.09, PUMP_Z0), BRONZE, app, bevel=0.008)
plunger = cyl("pump_plunger", 0.03, 0.2, (PUMP_X, SH_Y, 0), STEEL, app, verts=16)
# outlet: from the air vessel round the pot into the tub's west side
curve_obj("coolant_out", [(PUMP_X + 0.06, SH_Y + 0.04, PUMP_Z1 + 0.1), (PUMP_X + 0.2, SH_Y + 0.1, PUMP_Z1 + 0.12),
                          (0.3, -0.25, 1.62), (0.38, 0.25, 1.62), (TUB.x - TUB_R - 0.06, 0.5, 1.6),
                          (TUB.x - TUB_R + 0.02, 0.52, 1.6)], COPPER, 0.035, app, res=3)
ring("coolant_out_flange", 0.06, 0.03, -0.02, 0.02, GOLD, app, loc=(TUB.x - TUB_R - 0.02, 0.51, 1.6)
     ).rotation_euler = ry
RISER = Vector((-0.42, -0.4))
curve_obj("coolant_return", [(TUB.x - TUB_R + 0.03, 0.62, TUB_Z0 + 0.06), (TUB.x - TUB_R - 0.08, 0.6, TUB_Z0 + 0.06),
                             (0.26, 0.52, 1.0), (0.3, 0.36, Z_D + 0.05), (0.3, -0.3, Z_D + 0.05),
                             (RISER.x, RISER.y, Z_D + 0.05), (RISER.x, RISER.y, PUMP_Z0 + 0.05),
                             (PUMP_X - 0.06, SH_Y + 0.04, PUMP_Z0 + 0.07)], BRASS, 0.03, app, res=3)
for k, (x, y) in enumerate(((0.3, 0.0), (-0.1, -0.35))):
    box(f"return_clip{k}", (0.09, 0.09, 0.06), (x, y, Z_D + 0.04), STEEL, app, bevel=0.01)


def pose_pump(f):
    b = crank_angle(f)
    c = Vector((PUMP_X, SH_Y + ECC_E * math.cos(b), SH_Z + ECC_E * math.sin(b)))
    top_z = c.z + math.sqrt(ECC_ROD ** 2 - (c.y - SH_Y) ** 2)
    strap.location = c
    d = Vector((PUMP_X, SH_Y, top_z)) - c
    strap.rotation_euler = (-math.atan2(d.y, d.z), 0, 0)
    ecc_rod.scale = (1, 1, d.length)
    ecc_rod.location = (0, 0, d.length / 2)
    plunger.location = (PUMP_X, SH_Y, top_z + 0.1)


animated.append((None, lambda o, f: pose_pump(f)))
animated.append((None, lambda o, f: pose_governor(f)))


# ----------------------------------------------------------------------------
# Flows: distillate stream, flask levels, decanting, boiling
# ----------------------------------------------------------------------------
DYN = []
IDLE = False


def flask_level(alpha, f):
    """Liquid level (0..1) of a flask at absolute angle alpha."""
    if abs(math.cos(alpha)) < 1e-3 and math.sin(alpha) > 0:      # fill station
        if f >= IDX0:
            return 1.0
        return max(0.0, min(1.0, (f - VALVE_OPEN) / (VALVE_CLOSE - VALVE_OPEN)))
    if abs(math.cos(alpha)) < 1e-3 and math.sin(alpha) < 0:      # decant station
        if f >= IDX0:
            return 0.0
        return 1.0 - max(0.0, min(1.0, (f - DRAIN_OPEN) / (DRAIN_CLOSE - DRAIN_OPEN)))
    return 1.0 if math.cos(alpha) > 0 else 0.0


def liquid_mesh(name, level, parent):
    """Liquid column in a bottle."""
    if level <= 0.02:
        return None
    h = (BOT_H - 0.02) * level
    o = cyl(name, FL_R - 0.012, h, (0, 0, 0.012 + h / 2), POTION, parent, verts=20)
    return glow(o)


def stream(name, pts, r):
    o = curve_obj(name, [tuple(p) for p in pts], POTION, r, app, res=2,
                  taper=lambda t: 1.0 - 0.35 * t)
    return glow(o)


def pose_flows(f):
    for o in DYN:
        bpy.data.objects.remove(o, do_unlink=True)
    DYN.clear()
    th = plate_angle(f)
    plate.rotation_euler = (0, 0, th)
    for k, fl in enumerate(FLASKS):
        alpha = th + TAU * (k + 0.5) / 4
        lv = flask_level(alpha, f)
        o = liquid_mesh(f"liquid{k}", lv, fl)
        if o:
            DYN.append(o)
    # spout valve: handle swings 90 degrees to open
    opening = VALVE_OPEN <= f < VALVE_CLOSE and not IDLE
    valve_handle.rotation_euler = (0, 0, math.radians(-90 if opening else 0) + math.radians(30))
    if opening:
        lv = flask_level(math.pi / 2, f)
        top = SPOUT_TIP - Vector((0, 0, 0.02))
        bot = Vector((FILL.x, FILL.y, PLATE_Z1 + 0.03 + (BOT_H - 0.02) * lv))
        DYN.append(stream("fill_stream", [top, top.lerp(bot, 0.5), bot], 0.012))
    elif not IDLE and VALVE_CLOSE <= f < VALVE_CLOSE + 4:
        # the last drop falls off the nozzle
        t = (f - VALVE_CLOSE + 1) / 4
        p = SPOUT_TIP - Vector((0, 0, 0.03 + 0.2 * t * t))
        DYN.append(glow(sphere("drop", 0.014, tuple(p), POTION, app, segs=8)))
    if not IDLE and DRAIN_OPEN <= f < DRAIN_CLOSE:
        DYN.append(stream("decant_stream", [gutter_end + Vector((0, 0.0, 0.0)),
                                            gutter_end + Vector((0, -0.03, -0.02)),
                                            CHUTE + Vector((0, 0.0, 0.01))], 0.014))
        DYN.append(stream("gutter_flow", [(DECANT.x, DECANT.y + 0.04, PLATE_Z0 - 0.01),
                                          (DECANT.x, DECANT.y - 0.1, Z_D + 0.085),
                                          tuple(gutter_end + Vector((0, 0, 0.018)))], 0.012))


def pose_magic(f):
    """Boil surges 4x per loop: vapour, porthole, gauge, safety valve, runes."""
    ph = TAU * f / N
    surge = 0.5 + 0.5 * math.sin(4 * ph)
    if IDLE:
        BREW_EM.default_value = 0.15
        VAPOUR_EM.default_value = 0.0
        POTION_EM.default_value = 0.35
        RUNE_EM.default_value = 0.08
        needle.rotation_euler = (0, 0, math.radians(200))
        valve_lever.rotation_euler = (0, 0, 0)
        for b, _ in BUBBLES:
            b.hide_render = True
        hydro.location.z = SAFE.z - 0.05
        return
    for b, _ in BUBBLES:
        b.hide_render = False
    BREW_EM.default_value = 0.8 + 0.6 * surge
    VAPOUR_EM.default_value = 0.6 + 1.6 * surge
    POTION_EM.default_value = 1.2
    RUNE_EM.default_value = 0.2 + 0.5 * surge
    # needle sits in the working band, kicked by each surge
    needle.rotation_euler = (0, 0, math.radians(40 - 25 * surge))
    valve_lever.rotation_euler = (0, math.radians(-6 * max(0.0, math.sin(4 * ph)) ** 4), 0)
    # float rides up with the flow through the safe
    flowing = VALVE_OPEN <= f < VALVE_CLOSE
    hydro.location.z = SAFE.z - 0.03 + (0.02 if flowing else 0.0) + 0.006 * math.sin(8 * ph)


def pose(f):
    for o, fn in animated:
        fn(o, f)
    pose_flows(f)
    pose_magic(f)


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
FRAME_W, FRAME_H, FRAME_CY = 4.5, 4.125, 0.66
SHADOW_W, SHADOW_SHIFT_X = 5.625, 0.5625    # shadow frame: wider, shifted east
rig = setup_scene(frame_w=FRAME_W, frame_h=FRAME_H, frame_cy=FRAME_CY)
scene = bpy.context.scene
cam = scene.camera
pt_d = bpy.data.lights.new("porthole_light", "POINT")
pt_d.color = (1.0, 0.35, 0.85)
pt_d.shadow_soft_size = 0.05
pt_d.energy = 0.6
o = bpy.data.objects.new("porthole_light", pt_d)
link(o, app)
o.location = PH_C + PH_N * 0.12
fl_d = bpy.data.lights.new("flask_light", "POINT")
fl_d.color = (1.0, 0.3, 0.85)
fl_d.shadow_soft_size = 0.05
fl_d.energy = 0.8
o = bpy.data.objects.new("flask_light", fl_d)
link(o, app)
o.location = (CAR.x, CAR.y, PLATE_Z1 + 0.35)
EXTRA = (pt_d, fl_d)
LIGHTS = (rig.sun_d, rig.fill_d) + EXTRA
LIGHT_E = {l: l.energy for l in LIGHTS}
BG_E = rig.bg.inputs["Strength"].default_value


def mesh_objs():
    return [o for o in scene.objects if o.type in ("MESH", "CURVE")]


def reset():
    for l in LIGHTS:
        l.energy = LIGHT_E[l]
    rig.bg.inputs["Strength"].default_value = BG_E
    for o in mesh_objs():
        o.is_holdout = False
    HOT_MIX.default_value = 0.0


def lights_off():
    rig.bg.inputs["Strength"].default_value = 0.0
    for l in LIGHTS:
        l.energy = 0.0


def render_glow(path, f):
    pose(f)
    lights_off()
    for o in mesh_objs():
        o.is_holdout = not o.get("glow", False)
    render(path)
    reset()


frames = [int(f) for f in args.frame.split(",")] if args.preview else range(N)
for f in frames:
    reset()
    pose(f)
    render(OUT / f"main-{f:03d}.png")
if not args.no_glow:
    for f in frames:
        render_glow(OUT / f"glow-{f:03d}.png", f)

# idle: the machine at rest (frame 0 pose, nothing flowing, no boil)
IDLE = True
reset()
pose(0)
fl_d.energy = 0.15
pt_d.energy = 0.1
render(OUT / "idle-main.png")
IDLE = False
reset()

# heat: only the heated pipes, white-orange hot, everything else held out
pose(0)
lights_off()
HOT_MIX.default_value = 1.0
for o in mesh_objs():
    o.is_holdout = not o.get("heat", False)
render(OUT / "heat.png")
reset()

# shadow: key light only, lower from the west like the vanilla shadows, in a
# wider frame shifted east so long shadows of the column are not cut off
pose(0)
rig.ground.hide_render = False
lights_off()
rig.sun_d.energy = 4.6
for o in mesh_objs():
    if o is not rig.ground:
        o.visible_camera = False
rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
    Vector((1.0, -0.3, -1.45)).normalized()).to_euler()
cam.data.ortho_scale = max(SHADOW_W, FRAME_H)
cam.data.shift_x = SHADOW_SHIFT_X / max(SHADOW_W, FRAME_H)
scene.render.resolution_x = round(SHADOW_W * args.px_per_tile)
render(OUT / "shadow.png")
