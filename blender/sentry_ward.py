"""
Procedural Blender model + Factorio render of the sentry ward (a 1x1 radar).

A small gold-and-purple watch totem: an all-seeing eye on a slewing ring
sweeps around, driven by a spinning heart crystal in a lantern beside the
column. Radars draw `pictures` as a RotatedSprite and pick the direction that
matches their current orientation, so every frame here is one heading of a
seamless clockwise turn (frame i = orientation i / N, 0 = north):

    blender -b --factory-startup -P blender/sentry_ward.py -- \
        --out graphics/generated/sentry-ward [--preview --frame 0,16]

Renders main-NNN / glow-NNN (pack with blender/stitch.py) and per-direction
shadows into <out>/shadow/main-NNN.png (already black, density in alpha; pack
them with stitch.py too, see the bottom of this file). World units are tiles,
the entity is centred on the origin, +y is north, +z is up.
"""

import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("sentry-ward", frames=64, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N
OUT = fblend.OUT

SCLERA = paint("sclera", (0.78, 0.70, 0.66), (0.25, 0.17, 0.18), noise_scale=30.0,
               bump=0.05, dirt=0.05)


def iris_material():
    """Self-lit iris: hot pink round the pupil fading to deep violet, with
    radial fibres, so it reads as an eye and not a lamp."""
    m, nt, bsdf = node_mat("iris")
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    L(sep.outputs["X"], comb.inputs["X"])
    L(sep.outputs["Z"], comb.inputs["Z"])
    rad = nt.nodes.new("ShaderNodeVectorMath")
    rad.operation = "LENGTH"
    L(comb.outputs[0], rad.inputs[0])
    norm = nt.nodes.new("ShaderNodeMapRange")
    norm.inputs["From Max"].default_value = 0.11          # ~ iris radius in eye units
    L(rad.outputs["Value"], norm.inputs["Value"])
    ang = nt.nodes.new("ShaderNodeMath")
    ang.operation = "ARCTAN2"
    L(sep.outputs["X"], ang.inputs[0])
    L(sep.outputs["Z"], ang.inputs[1])
    fib_v = nt.nodes.new("ShaderNodeCombineXYZ")
    sc = nt.nodes.new("ShaderNodeMath")
    sc.operation = "MULTIPLY"
    sc.inputs[1].default_value = 6.0
    L(ang.outputs[0], sc.inputs[0])
    L(sc.outputs[0], fib_v.inputs["X"])
    L(norm.outputs["Result"], fib_v.inputs["Y"])
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 3.0
    fib.inputs["Detail"].default_value = 4.0
    L(fib_v.outputs[0], fib.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.3, (0.85, 0.95, 1.0, 1)
    els[1].position, els[1].color = 1.0, (0.04, 0.1, 0.35, 1)
    e = els.new(0.55)
    e.color = (0.4, 0.7, 1.0, 1)
    e = els.new(0.92)
    e.color = (0.12, 0.3, 0.8, 1)
    L(norm.outputs["Result"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.6
    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.inputs["To Min"].default_value = 0.35
    fr.inputs["To Max"].default_value = 1.4
    L(fib.outputs["Fac"], fr.inputs["Value"])
    L(ramp.outputs["Color"], mix.inputs["A"])
    L(fr.outputs["Result"], mix.inputs["B"])
    L(mix.outputs["Result"], bsdf.inputs["Base Color"])
    L(mix.outputs["Result"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 3.0
    bsdf.inputs["Roughness"].default_value = 0.1
    bsdf.inputs["Coat Weight"].default_value = 1.0
    return m, bsdf.inputs["Emission Strength"]


IRIS, IRIS_EM = iris_material()
PUPIL = gem("pupil", (0.01, 0.005, 0.012))
HEART, HEART_EM = emitter("heart", (0.7, 0.88, 1.0), 3.0, base=(0.45, 0.6, 0.8), glass=True)
ICE = (0.55, 0.78, 1.0)     # the ward's cold blue-white light (eye, runes, heart, gaze)

# ----------------------------------------------------------------------------
# Materials: a watchtower of silver and marble
# ----------------------------------------------------------------------------
# The ward has its own identity among the gold-and-purple machines: pale veined
# marble base and pillar, tarnished silver castings, polished and blued steel
# for the drive and the eye mount. Gold survives only on a few small fittings,
# purple only in two amethysts.


def marble(name, base, vein, scale=3.0):
    """Veined stone: fblend's grime (AO, dirt, mottling) multiplied by distorted
    wave-texture veins, so the white reads as stone at 64 px per tile."""
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Metallic"].default_value = 0.0
    grime(nt, bsdf, base, (0.42, 0.41, 0.4), noise_scale=12.0, rough=(0.3, 0.5),
          bump=0.08, bump_scale=40.0, dirt=0.25)
    L = nt.links.new
    old = bsdf.inputs["Base Color"].links[0].from_socket
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 8.0
    wave.inputs["Detail Roughness"].default_value = 0.7
    L(tc.outputs["Object"], wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, (*vein, 1)
    els[1].position, els[1].color = 0.12, (1, 1, 1, 1)
    e = els.new(0.55)
    e.color = (0.93, 0.93, 0.95, 1)
    L(wave.outputs["Fac"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    L(old, mix.inputs["A"])
    L(ramp.outputs["Color"], mix.inputs["B"])
    L(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Coat Weight"].default_value = 0.3     # honed, faintly polished
    return m


MARBLE = marble("marble", (0.93, 0.92, 0.89), (0.4, 0.42, 0.48))
MARBLE_DARK = marble("marble_dark", (0.5, 0.5, 0.52), (0.12, 0.13, 0.16), scale=4.0)
SILVER = metal("silver", (0.74, 0.74, 0.76), (0.08, 0.08, 0.09), rough=(0.3, 0.55), dirt=0.35)
BLUED = metal("blued_steel", (0.36, 0.4, 0.47), (0.05, 0.055, 0.07), rough=(0.38, 0.6),
              dirt=0.2)
MOONSTONE = gem("moonstone", (0.55, 0.72, 0.95))
AMETHYST = gem("amethyst", (0.45, 0.12, 0.6))
GILT = fblend.GOLD           # the real gold, kept for a few small fittings
fblend.GOLD = SILVER         # fblend's helpers (frames, filigree, studs) default to it
GOLD, RUBY, BRONZE, PURPLE = SILVER, MOONSTONE, STEEL, MARBLE

# ----------------------------------------------------------------------------
# Dimensions
# ----------------------------------------------------------------------------
#
# Sized like the vanilla 1x1 buildings: the plinth fills most of the tile like
# the small lamp, the totem rises about as high as a small electric pole's
# body so it stays readable among them. Rendered at 64 px/tile -> Lua scale 0.5.

PL, PL_CH, PLINTH_H = 0.40, 0.10, 0.09     # bronze plinth half size / chamfer / height
SK_B, SK_T, SK_H = 0.36, 0.25, 0.27        # sloped purple skirt: bottom/top half size, top z
SK_CH = 0.08
COL_R0, COL_R1, COL_Z1 = 0.15, 0.125, 0.86  # octagonal column apothem bottom/top, top z
RG_Z, RG_T, RG_R = 0.905, 30, 0.2           # slewing ring gear (on the head)
PIN_T = 10
PIN_R = RG_R * PIN_T / RG_T
DRIVE_A = math.radians(225)                 # drive lantern sits south-west of the column
DRIVE = Vector((math.cos(DRIVE_A), math.sin(DRIVE_A), 0)) * (RG_R + PIN_R)
TT_Z0, TT_Z1, TT_R = 0.935, 0.985, 0.17     # turntable disc riding on the ring gear
EYE_R = 0.16
SHELL_R = EYE_R * 1.1
EYE_C = Vector((0, 0.0, TT_Z1 + 0.05 + SHELL_R))   # eye centre in head-local coords
EYE_TILT = math.radians(8)    # looks a touch up, so its gaze meets the 45 degree camera
FIL_R = 0.02                                       # scrollwork at 1x1 scale

root = bpy.data.objects.new("sentry_ward", None)
link(root)
# Modelled on a 0.8 tile plinth, then scaled up so the totem is as wide on
# screen as the vanilla 1x1 buildings (small lamp ~1.1 tiles) at Lua scale 0.5.
root.scale = (1.15,) * 3


def octagon(apothem, rot=math.pi / 8):
    """Regular octagon with flat faces facing the axes (and diagonals)."""
    r = apothem / math.cos(math.pi / 8)
    return [(r * math.cos(rot + k * math.pi / 4), r * math.sin(rot + k * math.pi / 4))
            for k in range(8)]


def chamfered(h, ch):
    """Square of half size h with chamfered corners, CCW from the south-west."""
    return [(-h + ch, -h), (h - ch, -h), (h, -h + ch), (h, h - ch), (h - ch, h), (-h + ch, h),
            (-h, h - ch), (-h, -h + ch)]


def frustum(name, bot, z0, top, z1, mat, parent=None, bevel=0.006):
    """Closed solid between two CCW outlines of equal length."""
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in bot]
    t = [bm.verts.new((x, y, z1)) for x, y in top]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(bot)):
        j = (i + 1) % len(bot)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent or root, bevel=bevel)
    o.data.shade_flat()
    return o


def walls(bot, z0, top, z1):
    """Outward-facing Panels of a frustum (for ornaments)."""
    out = []
    for i in range(len(bot)):
        j = (i + 1) % len(bot)
        out.append(Panel((*bot[i], z0), (*bot[j], z0), (*top[j], z1), (*top[i], z1)))
    return out


def rail(name, pts, r, closed=False, mat=None, parent=None):
    return curve_obj(name, [tuple(p) for p in pts], mat or GOLD, r, parent or root, closed=closed)


def ring_pts(r, z, n=48, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(TAU * i / n), cy + r * math.sin(TAU * i / n), z) for i in range(n)]


animated = []      # (obj, fn(obj, theta)) with theta = heading clockwise from north

# ----------------------------------------------------------------------------
# Base: bronze plinth, sloped purple skirt with scrollwork
# ----------------------------------------------------------------------------
plinth = chamfered(PL, PL_CH)
frustum("plinth", plinth, 0, [(x * 0.97, y * 0.97) for x, y in plinth], PLINTH_H, MARBLE_DARK)
rail("plinth_rail", [(x, y, PLINTH_H) for x, y in plinth], 0.02, closed=True)
rail("plinth_foot", [(x * 1.01, y * 1.01, 0.012) for x, y in plinth], 0.016, closed=True)
for i in (7, 0, 1, 2):      # rivets on the faces the camera sees
    a, b = Vector((*plinth[i], 0)), Vector((*plinth[(i + 1) % 8], 0))
    nrm = Vector((b.y - a.y, -(b.x - a.x), 0)).normalized()
    n = 1 if i % 2 else 4
    for k in range(n):
        p = a.lerp(b, (k + 0.5) / n) + nrm * 0.004
        sphere(f"rivet{i}_{k}", 0.016, (p.x, p.y, PLINTH_H * 0.48), GOLD, root)

sk_bot, sk_top = chamfered(SK_B, SK_CH), chamfered(SK_T, SK_CH * 0.7)
frustum("skirt", sk_bot, PLINTH_H, sk_top, SK_H, PURPLE)
rail("skirt_top", [(x, y, SK_H) for x, y in sk_top], 0.018, closed=True)   # silver trim
for k in range(8):          # carved marble mouldings on the skirt's corner edges
    rail(f"skirt_rib{k}", [(*sk_bot[k], PLINTH_H + 0.01), (*sk_top[k], SK_H)], 0.024, mat=MARBLE)
sk_walls = walls(sk_bot, PLINTH_H, sk_top, SK_H)
for i in (0, 2, 6):         # big faces: a framed double scroll each (south, east, west)
    sp = sub_panel(sk_walls[i], 0.06, 0.94, 0.12, 0.9)
    gold_frame(sp, f"skirt_frame{i}", r=0.018, parent=root, mat=MARBLE)   # carved relief
    inner = sub_panel(sp, 0.08, 0.92, 0.12, 0.88)
    inner.filigree(f"skirt_fil{i}a", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.42, 1.0)],
                   radius=FIL_R, lift=0.01, parent=root, mat=MARBLE)
    inner.filigree(f"skirt_fil{i}b", [fit(scroll_c(0, 0, 1), 0.58, 0.0, 1.0, 1.0, flip_x=True)],
                   radius=FIL_R, lift=0.01, parent=root, mat=MARBLE)
    inner.studs(f"skirt_gem{i}", [(0.5, 0.45)], r=0.026, mat=RUBY, parent=root)
for i in (1, 7):            # front chamfer faces: a single ruby in a gold boss
    c = sk_walls[i].at(0.5, 0.5, 0.01)
    sphere(f"skirt_boss{i}", 0.03, c, GOLD, root)
    sphere(f"skirt_boss_gem{i}", 0.02, sk_walls[i].at(0.5, 0.5, 0.035), RUBY, root)

# ----------------------------------------------------------------------------
# Column: octagonal marble shaft with carved edges and silver bands. Its three front
# faces carry rune inlays that light up as the eye sweeps over their sector.
# ----------------------------------------------------------------------------
col_b, col_t = octagon(COL_R0), octagon(COL_R1)
frustum("column", col_b, SK_H, col_t, COL_Z1, PURPLE)
for k in range(8):
    rail(f"col_rib{k}", [(*col_b[k], SK_H), (*col_t[k], COL_Z1)], 0.016, mat=MARBLE)
for z, r in ((SK_H + 0.025, COL_R0 + 0.025), (0.58, (COL_R0 + COL_R1) / 2 + 0.02),
             (COL_Z1 - 0.02, COL_R1 + 0.03)):
    rail(f"col_band{z}", [(x, y, z) for x, y in octagon(r)], 0.022, closed=True)
col_walls = walls(col_b, SK_H, col_t, COL_Z1)
RUNE_FACES = []            # (compass angle of the face normal, emission socket)
for k, glyph in ((4, 0), (5, 2), (6, 3)):      # SW, S, SE faces (edge k faces 45 + 45k deg)
    w = col_walls[k]
    face_n = Vector(w.n)
    compass = math.atan2(face_n.x, face_n.y)     # clockwise from north
    mat, em = emitter(f"rune_face{k}", ICE, 0.3, base=(0.05, 0.07, 0.1))
    for half, (v0, v1) in enumerate(((0.06, 0.48), (0.53, 0.95))):
        pnl = sub_panel(w, 0.12, 0.88, v0, v1)
        for gi, stroke in enumerate(RUNES[(glyph + half) % len(RUNES)]):
            glow(curve_obj(f"col_rune{k}_{half}_{gi}",
                           [pnl.at(0.15 + 0.7 * u, 0.1 + 0.8 * v, 0.006) for u, v in stroke],
                           mat, 0.011, root))
    RUNE_FACES.append((compass, em))
# fixed bearing collar the head turns on
cyl("collar", COL_R1 + 0.035, 0.05, (0, 0, COL_Z1 + 0.01), BRONZE, root, verts=48)
rail("collar_rim", ring_pts(COL_R1 + 0.04, COL_Z1 + 0.035), 0.014, closed=True)

# gold gussets on the other three diagonals brace the column: a concave sweep
# from high on the column down to the skirt corner, ending in a curl
for a in (45, 135, 315):
    d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
    r0, r1 = COL_R0 / math.cos(math.pi / 8) - 0.01, SK_T * 1.2
    sweep = bezier2((r0, 0.6), (r0 + 0.01, SK_H + 0.02), (r1, SK_H + 0.02), n=14)
    curl = [(r1 + u * 0.06, SK_H + 0.02 + v * 0.06) for u, v in
            fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0, flip_x=True)][::-1]
    for k, (rr, zz) in enumerate(((0.0, 0.0), (-0.045, -0.06))):
        pts = [(r + rr * (1 - t / 14), z + zz * (1 - t / 14)) for t, (r, z) in enumerate(sweep)]
        rail(f"gusset{a}_{k}", [tuple(d * r + Vector((0, 0, z))) for r, z in pts], 0.026 - 0.008 * k,
             mat=MARBLE)
    rail(f"gusset_curl{a}", [tuple(d * r + Vector((0, 0, z))) for r, z in curl], 0.014)
    sphere(f"gusset_gem{a}", 0.022, tuple(d * (r0 + 0.02) + Vector((0, 0, 0.6))), RUBY, root)

# ----------------------------------------------------------------------------
# Drive: heart crystal in a gold lantern -> pinion -> slewing ring on the head
# ----------------------------------------------------------------------------
LAN_R, LAN_Z0, LAN_Z1 = 0.068, SK_H, 0.72
lantern = bpy.data.objects.new("lantern", None)
link(lantern, root)
lantern.location = (DRIVE.x, DRIVE.y, 0)
cyl("lan_foot", LAN_R + 0.02, 0.05, (0, 0, LAN_Z0 + 0.02), GOLD, lantern, verts=24,
    r2=LAN_R + 0.005)
cyl("lan_cup", LAN_R + 0.01, 0.04, (0, 0, LAN_Z0 + 0.065), BRONZE, lantern, verts=24)
cyl("lan_cap", LAN_R + 0.012, 0.045, (0, 0, LAN_Z1), BRONZE, lantern, verts=24, r2=LAN_R * 0.55)
rail("lan_cap_rim", [(DRIVE.x + x, DRIVE.y + y, LAN_Z1 - 0.02) for x, y, _ in
                     ring_pts(LAN_R + 0.014, 0, 24)], 0.012, closed=True)
for k in range(6):          # cage bars: the heart is seen only between them
    a = TAU * k / 6 + 0.3
    p = (LAN_R * math.cos(a), LAN_R * math.sin(a))
    curve_obj(f"lan_bar{k}", [(*p, LAN_Z0 + 0.08), (p[0] * 1.15, p[1] * 1.15, (LAN_Z0 + LAN_Z1) / 2),
                              (*p, LAN_Z1 - 0.02)], GOLD, 0.011, lantern)
# brackets tying the lantern to the column
for z in (0.42, 0.66):
    rail(f"lan_bracket{z}", [tuple(DRIVE * ((COL_R0 - 0.01) / DRIVE.length) + Vector((0, 0, z))),
                             tuple(DRIVE * ((DRIVE.length - LAN_R) / DRIVE.length) + Vector((0, 0, z)))],
         0.016)
# drive shaft: heart below, pinion on top, all on one spindle
spindle = bpy.data.objects.new("spindle", None)
link(spindle, root)
spindle.location = (DRIVE.x, DRIVE.y, 0)
cyl("spindle_rod", 0.014, RG_Z - LAN_Z0 - 0.05, (0, 0, (RG_Z + LAN_Z0 + 0.05) / 2), STEEL, spindle,
    verts=12)
pinion = gear("pinion", PIN_T, PIN_R, 0.045, STEEL, spindle, spokes=0, inner=0.4)
pinion.location = (0, 0, RG_Z)
cyl("pinion_cap", 0.022, 0.03, (0, 0, RG_Z + 0.035), GILT, spindle, verts=12)
HEART_Z = (LAN_Z0 + 0.09 + LAN_Z1 - 0.03) / 2
bm = bmesh.new()            # hexagonal bipyramid crystal
ring_v = [bm.verts.new((0.042 * math.cos(TAU * k / 6), 0.042 * math.sin(TAU * k / 6), 0))
          for k in range(6)]
top_v, bot_v = bm.verts.new((0, 0, 0.14)), bm.verts.new((0, 0, -0.1))
for k in range(6):
    bm.faces.new((ring_v[k], ring_v[(k + 1) % 6], top_v))
    bm.faces.new((ring_v[(k + 1) % 6], ring_v[k], bot_v))
heart = mesh_obj("heart", bm, HEART, spindle)
heart.data.shade_flat()
heart.location = (0, 0, HEART_Z)
glow(heart)
heart_light_d = bpy.data.lights.new("heart_light", "POINT")
heart_light_d.color = ICE
heart_light_d.shadow_soft_size = 0.03
heart_light_d.energy = 1.2
o = bpy.data.objects.new("heart_light", heart_light_d)
link(o, root)
o.location = (DRIVE.x, DRIVE.y, HEART_Z)

# The head turns once per loop (clockwise seen from above, like a radar's
# orientation); the pinion meshes externally so it turns RG_T/PIN_T = 3 times
# the other way. Teeth pass at 30 per loop: 0.47 pitch per frame at 64.
th_ring = mesh_angle(DRIVE_A, RG_T, gap=False)
th_pin = mesh_angle(DRIVE_A + math.pi, PIN_T, gap=True)
animated.append((spindle, lambda o, th: setattr(o, "rotation_euler", (0, 0, th_pin + RG_T / PIN_T * th))))

# ----------------------------------------------------------------------------
# Head: slewing ring, turntable, yoke and the eye
# ----------------------------------------------------------------------------
head = bpy.data.objects.new("head", None)
link(head, root)
animated.append((head, lambda o, th: setattr(o, "rotation_euler", (0, 0, -th))))

ring = gear("slewing_ring", RG_T, RG_R, 0.05, GOLD, head, spokes=6, inner=0.7)
ring.location = (0, 0, RG_Z)
ring.rotation_euler = (0, 0, th_ring)
cyl("turntable", TT_R, TT_Z1 - TT_Z0, (0, 0, (TT_Z0 + TT_Z1) / 2), BLUED, head, verts=48)
rail("turntable_rim", ring_pts(TT_R + 0.005, TT_Z1), 0.02, closed=True, parent=head)
for k in range(8):
    a = TAU * (k + 0.5) / 8
    sphere(f"tt_stud{k}", 0.018, (TT_R * 0.98 * math.cos(a), TT_R * 0.98 * math.sin(a),
                                  (TT_Z0 + TT_Z1) / 2), RUBY if k % 2 else GOLD, head)

# eye assembly, tilted down a little, held in a gold fork
eye = bpy.data.objects.new("eye", None)
link(eye, head)
eye.location = EYE_C
eye.rotation_euler = (EYE_TILT, 0, 0)

sphere("eyeball", EYE_R, (0, 0, 0), SCLERA, eye, segs=48)
IRIS_A = math.radians(40)          # angular radius of the iris


def cap(name, r, keep, mat, parent, segs=64):
    """Part of a sphere: keep the vertices for which keep(co) is true."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep(v.co)], context="VERTS")
    return mesh_obj(name, bm, mat, parent, smooth=True)


iris = cap("iris", EYE_R * 1.008, lambda c: c.y > EYE_R * 1.008 * math.cos(IRIS_A), IRIS, eye)
glow(iris)
pupil = sphere("pupil", EYE_R * 0.42, (0, EYE_R * 0.82, 0), PUPIL, eye, segs=24)
pupil.scale = (0.22, 0.5, 0.95)    # a vertical slit, like a dragon's eye
limbal = [(EYE_R * 1.01 * math.sin(IRIS_A) * math.cos(TAU * i / 40), EYE_R * 1.01 * math.cos(IRIS_A),
           EYE_R * 1.01 * math.sin(IRIS_A) * math.sin(TAU * i / 40)) for i in range(40)]
curve_obj("limbal_ring", limbal, GILT, 0.008, eye, closed=True)

# Purple shell with an almond slot: the eye is only seen through its lids.
SLOT_W, SLOT_H = SHELL_R * 0.9, SHELL_R * 0.52


def slot_h(x):
    return SLOT_H * max(0.0, 1 - (x / SLOT_W) ** 2)


SHELL_PAINT = BLUED            # dark blued steel, so the silver ribs and lids read on it
shell = cap("shell", SHELL_R, lambda c: not (c.y > 0 and abs(c.z) < slot_h(c.x) + 0.004),
            SHELL_PAINT, eye, segs=64)
sol = shell.modifiers.new("solid", "SOLIDIFY")
sol.thickness = 0.014
sol.offset = 1
for sgn in (1, -1):        # heavy gold eyelids on the slot edges
    lid = []
    for i in range(33):
        x = -SLOT_W + 2 * SLOT_W * i / 32
        z = sgn * slot_h(x)
        y = math.sqrt(max(SHELL_R ** 2 - x * x - z * z, 0.0))
        lid.append((x * 1.02, y * 1.02, z * 1.02 + sgn * 0.006))
    curve_obj(f"lid{sgn}", lid, GOLD, 0.02 if sgn > 0 else 0.017, eye)
for sx in (-1, 1):         # rubies in the corners of the eye
    sphere(f"eye_corner{sx}", 0.02, (sx * SLOT_W * 1.04, math.sqrt(SHELL_R ** 2 - SLOT_W ** 2) + 0.01, 0),
           RUBY, eye)
# lashes: gold spikes fanning from the upper lid, the ward's crown
for k in range(5):
    x = SLOT_W * (k - 2) / 2.6
    z = slot_h(x)
    base = Vector((x, math.sqrt(max(SHELL_R ** 2 - x * x - z * z, 0)), z)) * 1.03
    out = (base.normalized() + Vector((x * 2.0, 0.25, 1.6))).normalized()
    ln = 0.07 if k == 2 else 0.055
    curve_obj(f"lash{k}", [tuple(base), tuple(base + out * ln * 0.6), tuple(base + out * ln)],
              GOLD, 0.013, eye, taper=lambda t: 1.0 - 0.75 * t)
# meridian ribs over the shell, front to back
for k, a in enumerate((0.0,)):
    pts = []
    for i in range(25):
        t = math.radians(30 + 170 * i / 24)          # from above the slot over the top
        p = Vector((0, math.cos(t), math.sin(t))) * (SHELL_R + 0.012)
        pts.append(tuple(Matrix.Rotation(a, 3, "Y") @ p))
    curve_obj(f"shell_rib{k}", pts, GOLD, 0.014, eye)
rail("shell_band", [(SHELL_R * 1.01 * math.cos(t), SHELL_R * 1.01 * math.sin(t), 0)
                    for t in (math.radians(a) for a in range(200, 341, 10))], 0.016, parent=eye)
# finial on the crown
cyl("finial_base", 0.03, 0.04, (0, -0.02, SHELL_R + 0.02), GILT, eye, verts=16, r2=0.018)
cyl("finial_spike", 0.012, 0.09, (0, -0.02, SHELL_R + 0.08), GILT, eye, verts=12, r2=0.002)
sphere("finial_gem", 0.022, (0, -0.02, SHELL_R + 0.06), AMETHYST, eye)


def on_shell(center, t1, t2, strokes, span, name, r=FIL_R, mat=None):
    """Scrollwork drawn on the shell: unit-square strokes centred on direction
    `center`, spread `span` radians along tangents t1 (u) and t2 (v)."""
    c, t1, t2 = Vector(center).normalized(), Vector(t1), Vector(t2)
    for i, pts in enumerate(strokes):
        out = []
        for u, v in pts:
            d = (c + t1 * math.tan((u - 0.5) * span) + t2 * math.tan((v - 0.5) * span)).normalized()
            out.append(tuple(d * (SHELL_R + 0.012)))
        curve_obj(f"{name}{i}", out, mat or GOLD, r, eye)


lyre = []
for m in (False, True):     # double scroll filling the back of the shell
    lyre.append(fit(scroll_c(0, 0, 1), 0.52 if m else 0.0, 0.0, 1.0 if m else 0.48, 0.9, flip_x=m))
lyre.append([(0.5, 0.05), (0.5, 0.75)])
on_shell((0, -1, 0.25), (-1, 0, 0), (0, 0, 1), lyre, math.radians(95), "back_lyre")
sphere("back_gem", 0.026, tuple(Vector((0, -1, 0.62)).normalized() * (SHELL_R + 0.02)), RUBY, eye)
for sx in (-1, 1):          # side scrolls framing the pivot bosses
    for k, up in enumerate((True, False)):
        st = fit(scroll_c(0, 0, 1, up=up), 0.0, 0.5 if up else 0.0, 0.5, 1.0 if up else 0.5,
                 flip_x=(sx < 0))
        on_shell((sx, 0.15, 0), (0, sx, 0), (0, 0, 1), [st], math.radians(90), f"side{sx}_{k}")
# heavy brow above the slot, so the eye reads as hooded
brow = []
for i in range(25):
    x = -SLOT_W * 0.95 + 2 * SLOT_W * 0.95 * i / 24
    z = slot_h(x) + 0.045 + 0.02 * (1 - (x / SLOT_W) ** 2)
    y = math.sqrt(max(SHELL_R ** 2 - x * x - z * z, 0.0))
    brow.append((x * 1.06, y * 1.06, z * 1.04))
curve_obj("brow", brow, GOLD, 0.017, eye)
sphere("brow_gem", 0.022, brow[12], AMETHYST, eye)
# counterweight slung under the back balances the eye on its pivots
sphere("counterweight", 0.05, (0, -SHELL_R * 0.75, -SHELL_R * 0.78), BRONZE, eye, segs=20)
cyl("counterweight_band", 0.052, 0.022, (0, -SHELL_R * 0.75, -SHELL_R * 0.78), GOLD, eye,
    rot=(math.radians(90), 0, 0), verts=24)

# fork: two gold arms from the turntable to pivot bosses on the shell's sides
FORK_X = SHELL_R + 0.03
for sx in (-1, 1):
    rail(f"fork{sx}", [(sx * 0.1, 0, TT_Z1), (sx * FORK_X, 0, TT_Z1 + 0.04), (sx * FORK_X, 0, EYE_C.z)],
         0.022, parent=head)
    cyl(f"pivot{sx}", 0.035, 0.03, (sx * (FORK_X + 0.005), 0, EYE_C.z), GILT, head,
        rot=(0, math.radians(90), 0), verts=20)
    sphere(f"pivot_gem{sx}", 0.016, (sx * (FORK_X + 0.025), 0, EYE_C.z), RUBY, head)

eye_light_d = bpy.data.lights.new("eye_light", "POINT")
eye_light_d.color = ICE
eye_light_d.shadow_soft_size = 0.02
eye_light_d.energy = 0.6
o = bpy.data.objects.new("eye_light", eye_light_d)
link(o, eye)
o.location = (0, SHELL_R + 0.06, 0)

# The ward's gaze: soft light cast on the ground by a beam from the eye,
# sweeping round with it. Only rendered into the glow (night light) pass, so by
# day the eye just turns and by night its gaze visibly scans the surroundings.
# The pool is an ellipse stretched along the gaze (a beam meeting the ground at
# a slant) with a smooth (1 - r^2)^2 falloff: brightest in the middle, zero at
# the edge, no rim. It fades out while the eye looks north, where the pool
# would sit behind the head on screen.
GAZE_D, GAZE_W, GAZE_L = 1.0, 0.3, 0.42     # head-local (x1.15 in world); fits GLOW_FRAME
GAZE_PEAK = 0.55                            # alpha in the middle of the pool


def gaze_material():
    m = bpy.data.materials.new("gaze")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.6, 0.8, 1.0, 1)
    em.inputs["Strength"].default_value = 1.2
    tc = nt.nodes.new("ShaderNodeTexCoord")      # unit disc in object space
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    L(tc.outputs["Object"], ln.inputs[0])
    sq = nt.nodes.new("ShaderNodeMath")
    sq.operation = "POWER"
    sq.inputs[1].default_value = 2.0
    L(ln.outputs["Value"], sq.inputs[0])
    t = nt.nodes.new("ShaderNodeMath")
    t.operation = "SUBTRACT"
    t.use_clamp = True
    t.inputs[0].default_value = 1.0
    L(sq.outputs[0], t.inputs[1])
    t2 = nt.nodes.new("ShaderNodeMath")
    t2.operation = "POWER"
    t2.inputs[1].default_value = 2.0
    L(t.outputs[0], t2.inputs[0])
    fade = nt.nodes.new("ShaderNodeValue")
    fade.name = "fade"
    amt = nt.nodes.new("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    L(t2.outputs[0], amt.inputs[0])
    L(fade.outputs[0], amt.inputs[1])
    L(amt.outputs[0], mix.inputs["Fac"])
    L(tr.outputs[0], mix.inputs[1])
    L(em.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs[0])
    return m, fade.outputs[0]


bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=1.0)
GAZE_MAT, GAZE_FADE = gaze_material()
gaze = mesh_obj("gaze_pool", bm, GAZE_MAT, head)
gaze.location = (0, GAZE_D, 0.01)
gaze.scale = (GAZE_W, GAZE_L, 1)
glow(gaze)
gaze["glow_only"] = True


def pose_magic(th):
    """Runes light up as the eye sweeps over their sector; the eye stays lit."""
    for compass, em in RUNE_FACES:
        c = max(0.0, math.cos(th - compass))
        em.default_value = 0.2 + 1.5 * c ** 6
    # gaze pool: full when looking south, gone when it would sit behind the head
    GAZE_FADE.default_value = GAZE_PEAK * ((1 - math.cos(th)) / 2) ** 0.7


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
# Each pass has its own frame (w, h, screen centre x, y in tiles, +y up); the
# Lua shift of a layer is {cx, -cy} at scale 0.5.
MAIN_FRAME = (1.25, 2.0, 0.0, 0.4)
GLOW_FRAME = (3.5, 2.5, 0.0, 0.0)        # room for the gaze pool all round
SHADOW_FRAME = (3.3, 1.3, 1.1, -0.15)   # shadows fall south-east
rig = setup_scene(*MAIN_FRAME[:2], MAIN_FRAME[3])


def pose(f):
    th = TAU * f / N
    for o, fn in animated:
        fn(o, th)
    pose_magic(th)


def set_frame(w, h, cx, cy):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.ortho_scale = max(w, h)
    scene.render.resolution_x = round(w * args.px_per_tile)
    scene.render.resolution_y = round(h * args.px_per_tile)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((cx, 0, cy * math.sqrt(2))) - look * 30


def blacken(path):
    """Factorio shadow sprites: black, density in alpha."""
    img = bpy.data.images.load(str(path))
    px = list(img.pixels)
    for i in range(0, len(px), 4):
        px[i] = px[i + 1] = px[i + 2] = 0.0
    img.pixels = px
    img.save()
    bpy.data.images.remove(img)


def render_all():
    scene = bpy.context.scene
    lights = (rig.sun_d, rig.fill_d, heart_light_d, eye_light_d)
    frames = [int(f) for f in args.frame.split(",")] if args.preview else range(N)
    glow_only = [o for o in scene.objects if o.get("glow_only")]
    for o in glow_only:
        o.hide_render = True
    # GLOW_ONLY=1 re-renders just the glow pass (the other passes are unchanged)
    only_glow = os.environ.get("GLOW_ONLY") == "1"
    set_frame(*MAIN_FRAME)
    for f in ([] if only_glow else frames):
        pose(f)
        fblend.render(OUT / f"main-{f:03d}.png")
    if not args.no_glow:
        energies = [l.energy for l in lights]
        rig.bg.inputs["Strength"].default_value = 0.0
        for l in lights:
            l.energy = 0.0
        for o in scene.objects:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = not o.get("glow", False)
        for o in glow_only:
            o.hide_render = False
        set_frame(*GLOW_FRAME)
        for f in frames:
            pose(f)
            fblend.render(OUT / f"glow-{f:03d}.png")
        for o in scene.objects:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = False
        for o in glow_only:
            o.hide_render = True
        for l, e in zip(lights, energies):
            l.energy = e
        rig.bg.inputs["Strength"].default_value = 0.15
    if only_glow:
        return
    # Shadows: one per direction (the eye and its fork turn), same low key sun
    # as fblend.render_passes, cast onto the catcher with the totem invisible.
    set_frame(*SHADOW_FRAME)
    rig.ground.hide_render = False
    for l in lights:
        l.energy = 0.0
    rig.sun_d.energy = 4.6
    rig.bg.inputs["Strength"].default_value = 0.0
    for o in scene.objects:
        if o is not rig.ground and o.type in ("MESH", "CURVE"):
            o.visible_camera = False
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((1.0, -0.35, -0.75)).normalized()).to_euler()
    sh_dir = OUT / "shadow"
    sh_dir.mkdir(exist_ok=True)
    scene.cycles.samples = max(32, args.samples // 3)
    for f in frames:
        pose(f)
        p = sh_dir / f"main-{f:03d}.png"
        fblend.render(p)
        blacken(p)


render_all()
# Pack:  .venv/bin/python blender/stitch.py graphics/generated/sentry-ward --name sentry-ward
#        .venv/bin/python blender/stitch.py graphics/generated/sentry-ward/shadow \
#            --name sentry-ward-shadow     (-> graphics/sentry-ward-shadow-animation.png)
