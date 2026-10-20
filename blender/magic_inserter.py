"""
Procedural Blender model + Factorio render of the magic inserter (1x1).

The magic inserter is an ordinary inserter whose arm is gone: a low platform
plate holds a glowing magic orb in a gold cradle, and a white cartoon glove
flies the usual inserter trajectory and grabs items exactly like a vanilla
claw. Nothing is pulled by magic - the glove does the work.

    blender -b --factory-startup -P blender/magic_inserter.py -- \
        --out graphics/generated/magic-inserter [--preview] [--samples 64]
    .venv/bin/python blender/magic_inserter.py --stitch graphics/generated/magic-inserter

How the engine draws an inserter (base/prototypes/entity/entities.lua, the
vanilla hand PNGs, and the long-handed inserter which reuses the same 72x164
hand canvas with hand_size 1.5):

* platform_picture is a Sprite4Way, frames N/E/S/W. Frame k is the prototype's
  pickup/insert vectors rotated k quarter turns clockwise, so in frame 0 the
  pickup is north and the drop south. The platform is static.
* The arm is a two-bone chain (hand_base: platform -> elbow, hand: elbow ->
  grip). Each bone sprite is anchored at its bottom edge, ROTATED to the
  bone's screen direction and STRETCHED/SQUASHED along its length to the
  bone's projected length; the width is not scaled. That is why long-handed
  inserters can reuse the canvases. The fingers point to the TOP of the
  canvas, the held item sits between the vanilla tines (row ~18 of 164).
* Because the sprite turns through every angle, it has to be drawn as seen
  from straight above with rotation-invariant (overhead) light, like the
  vanilla claws - a 3/4 view would tip over when the arm points south.
* The engine squashes the hand canvas along its length. Measured in 2.1.22
  screenshots (hand_size 0.6, chests as the tile scale) the glove part of the
  canvas shows at ~0.6-0.77 of its natural length depending on direction
  (longest reaching north), so the glove is rendered pre-stretched by
  HAND_STRETCH (tuned for the ~0.77 the screenshots show most) and reads as
  a normally proportioned glove, ~1.3-1.5:1 including the cuff. The canvas
  rows below the cuff (towards the invisible elbow) stay empty.

The hand canvas keeps the vanilla geometry exactly (72x164 px at scale 0.25),
so whatever the engine does with the vanilla claw it does with the glove: the
grip point (item centre) is where the vanilla tines grip, the glove reaches
back from there towards the (invisible) elbow, cuff last.
"""

import math
import sys
from pathlib import Path

HAND_W_PX, HAND_H_PX = 72, 164      # vanilla fast-inserter hand canvas
HAND_PPT = 128                      # its pixels per tile (scale 0.25)
GRIP_ROW = 18                       # vanilla tine centre: the held item's row
HAND_STRETCH = 1.25                 # pre-stretch against the engine's measured ~0.6-0.77 squash
PLAT = dict(w=1.0, h=0.75, cx=0.0625, cy=0.0)   # platform frame box, screen tiles
SS = 4                              # hand supersampling
GLOVE_SCALE = 1.1                   # the glove as modelled below -> on screen (~0.55 x 0.36 tiles)


def stitch(src, dest="graphics", name="magic-inserter", render_ppt=128, ppt=64):
    """Pack the renders (needs PIL: run under the repo venv, not Blender)."""
    from PIL import Image, ImageFilter
    src, dest = Path(src), Path(dest)

    def load(p, size=None):
        im = Image.open(p).convert("RGBA")
        if size is None:
            k = ppt / render_ppt
            size = (round(im.width * k), round(im.height * k))
        return im.resize(size, Image.LANCZOS)

    def as_light(im):
        """Glow pass -> light sprite: colour normalised, density in alpha, so
        black (unlit) pixels don't paint darkness into the light map."""
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                m = max(r, g, b) * a // 255
                if m < 3:
                    px[x, y] = (0, 0, 0, 0)
                else:
                    s = 255 / max(r, g, b)
                    px[x, y] = (min(255, round(r * s)), min(255, round(g * s)),
                                min(255, round(b * s)), m)
        return im

    def shadow(im, density=1.0):
        a = im.getchannel("A").point(lambda v: round(v * density))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.putalpha(a)
        return out

    # platform: one 4-frame row per pass
    for kind, suffix in (("main", ""), ("glow", "-glow"), ("shadow", "-shadow")):
        imgs = [load(src / f"platform-{kind}-{d}.png") for d in range(4)]
        if kind == "glow":
            imgs = [as_light(im) for im in imgs]
        if kind == "shadow":
            imgs = [shadow(im) for im in imgs]
        w, h = imgs[0].size
        out = Image.new("RGBA", (w * 4, h))
        for d, im in enumerate(imgs):
            out.paste(im, (d * w, 0))
        out.save(dest / f"{name}-platform{suffix}.png", optimize=True)
        print(f"platform{suffix}: 4 frames of {w}x{h}")

    # hands: rendered SS x oversampled across and 2*SS... along (pre-stretched)
    for state in ("open", "closed"):
        main = load(src / f"hand-{state}-main.png", (HAND_W_PX, HAND_H_PX))
        main.save(dest / f"{name}-hand-{state}.png", optimize=True)
        glow = as_light(load(src / f"hand-{state}-glow.png", (HAND_W_PX, HAND_H_PX)))
        glow.save(dest / f"{name}-hand-{state}-light.png", optimize=True)
        # vanilla hand shadows: the silhouette at half density, slightly soft
        sh = shadow(main, 0.5).filter(ImageFilter.GaussianBlur(0.6))
        sh.save(dest / f"{name}-hand-{state}-shadow.png", optimize=True)
        print(f"hand {state}: {main.size}")


if "--stitch" in sys.argv:
    stitch(sys.argv[sys.argv.index("--stitch") + 1])
    sys.exit(0)

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("magic-inserter", frames=1, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

OUT = fblend.OUT
scene = bpy.context.scene

STONE = paint("stone", (0.20, 0.185, 0.17), (0.035, 0.03, 0.028), noise_scale=14.0,
              bump=0.5, bump_scale=30.0, dirt=0.25)


def orb_material():
    """Glassy self-lit orb: swirling streaks of magenta light (heavily
    distorted bands) brightest at the core, fading to deep purple at the rim,
    under a clear coat that catches the sun."""
    m, em = emitter("magic_orb", (0.95, 0.25, 1.0), 1.1, base=(0.10, 0.0, 0.12), glass=True)
    nt = m.node_tree
    L = nt.links.new
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "DIAGONAL"
    wave.inputs["Scale"].default_value = 2.2
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 2.5
    wave.inputs["Detail Scale"].default_value = 1.5
    L(tc.outputs["Object"], wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.25, (0.20, 0.0, 0.30, 1)
    els[1].position, els[1].color = 0.8, (1.0, 0.35, 1.0, 1)
    e = els.new(0.55)
    e.color = (0.62, 0.06, 0.78, 1)
    L(wave.outputs["Fac"], ramp.inputs["Fac"])
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    core = nt.nodes.new("ShaderNodeMapRange")       # facing -> 1 at centre, 0.2 at rim
    core.inputs["To Min"].default_value = 1.0
    core.inputs["To Max"].default_value = 0.2
    L(lw.outputs["Facing"], core.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L(ramp.outputs["Color"], mul.inputs["A"])
    L(core.outputs["Result"], mul.inputs["B"])
    L(mul.outputs["Result"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["Coat Roughness"].default_value = 0.02
    return m, em


ORB, ORB_EM = orb_material()
GEM_EM_MAT, GEM_EM = emitter("cuff_gem", (0.8, 0.2, 1.0), 0.6, base=(0.35, 0.05, 0.45),
                             glass=True)


def cloth():
    """Off-white glove fabric: soft, a faint weave bump, a touch of sheen and
    grime in the creases so it isn't a flat white blob at 32 px per tile."""
    m = paint("glove", (0.86, 0.85, 0.81), (0.40, 0.38, 0.37), noise_scale=30.0,
              bump=0.25, bump_scale=160.0, dirt=0.0, ao_dist=0.05)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Sheen Weight"].default_value = 0.4
    b.inputs["Subsurface Weight"].default_value = 0.15
    b.inputs["Subsurface Radius"].default_value = (0.02, 0.02, 0.02)
    return m


CLOTH = cloth()
DECK = paint("deck", (0.18, 0.03, 0.135), (0.02, 0.003, 0.016), noise_scale=9.0, bump=0.6,
             bump_scale=25.0, dirt=0.2, hammered=True)    # PURPLE, darker: it faces the sun
STITCH = paint("stitch", (0.30, 0.29, 0.29), (0.12, 0.11, 0.11), bump=0.0, dirt=0.0)


def lathe(name, profile, mat, parent=None, segs=48, axis="Z"):
    """Surface of revolution from (radius, height) points about local z (or y)."""
    bm = bmesh.new()
    rings = []
    for r, h in profile:
        ring = []
        for k in range(segs):
            a = TAU * k / segs
            c, s = r * math.cos(a), r * math.sin(a)
            ring.append(bm.verts.new((c, s, h) if axis == "Z" else (c, h, s)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            q = (k + 1) % segs
            bm.faces.new((a[k], a[q], b[q], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mat, parent, smooth=True)


def frustum(name, bot, top, z0, z1, mat, parent, bevel=0.006):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in bot]
    t = [bm.verts.new((x, y, z1)) for x, y in top]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(bot)):
        j = (i + 1) % len(bot)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, mat, parent, bevel=bevel)
    o.data.shade_flat()
    return o


def ring_pts(r, z, n=48, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(TAU * k / n), cy + r * math.sin(TAU * k / n), z) for k in range(n)]


# ============================================================================
# Platform (frame 0: pickup north = +y, drop south = -y)
# ============================================================================
#
# As low as the vanilla platform ring so it never hides items on the
# neighbouring belts: a 0.08 tile stone-and-gold plate, the orb on top is the
# only tall thing (top at 0.33). The plate is a shield: an octagon whose south
# side runs out into a prow with a gold arrow - the inserter's drop side, the
# way the vanilla platform's legs show its direction.

plat = bpy.data.objects.new("platform", None)
link(plat)

A = 0.355           # plate apothem (legs of the vanilla platform reach ~0.42)
CH = 0.12           # corner chamfer
PROW = 0.455        # prow tip, south
FOOT_Z, DECK_Z = 0.045, 0.075


def shield(a, ch, prow):
    """Octagon (apothem a, chamfer ch) with the south edge pulled into a prow;
    counter-clockwise from the prow tip."""
    return [(0, -prow), (a - ch * 0.4, -a + ch * 0.25), (a, -a + ch), (a, a - ch),
            (a - ch, a), (-a + ch, a), (-a, a - ch), (-a, -a + ch),
            (-a + ch * 0.4, -a + ch * 0.25)]


def inset(poly, d):
    return [(x * (1 - d), y * (1 - d)) for x, y in poly]


foot = shield(A + 0.02, CH, PROW + 0.02)
top = shield(A, CH, PROW)
deck = inset(top, 0.1)
frustum("footing", foot, top, 0.0, FOOT_Z, STONE, plat, bevel=0.008)
curve_obj("footing_lip", [(x * 1.01, y * 1.01, 0.012) for x, y in foot], BRONZE, 0.012, plat,
          closed=True)
frustum("deck", top, deck, FOOT_Z, DECK_Z, DECK, plat, bevel=0.004)
# heavy bevelled gold rim on the plate edge (the brief's 0.05-0.075 frames)
curve_obj("rim", [(x, y, FOOT_Z + 0.006) for x, y in top], GOLD, 0.026, plat, closed=True)
for i, (x, y) in enumerate(top):    # rim corner bosses
    sphere(f"rim_boss{i}", 0.03, (x, y, FOOT_Z + 0.014), GOLD, plat, segs=16)

# deck: a gold inner ring round the cradle, diagonal ribs out to the rim,
# scrollwork in the three plain panels and the drop arrow in the south one
RING_R = 0.135
curve_obj("deck_ring", ring_pts(RING_R, DECK_Z + 0.008, 48), GOLD, 0.02, plat, closed=True)
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2
    p0 = (RING_R * math.cos(a), RING_R * math.sin(a), DECK_Z + 0.008)
    r1 = A * 1.02
    p1 = (r1 * math.cos(a) * 0.9, r1 * math.sin(a) * 0.9, DECK_Z + 0.004)
    curve_obj(f"deck_rib{k}", [p0, p1], GOLD, 0.018, plat)
    # ruby studs in gold bezels where the ribs meet the rim
    bz = (p1[0] * 1.02, p1[1] * 1.02, DECK_Z + 0.006)
    curve_obj(f"stud_bezel{k}", ring_pts(0.026, bz[2], 20, bz[0], bz[1]), GOLD, 0.008, plat,
              closed=True)
    sphere(f"stud{k}", 0.022, bz, RUBY, plat, segs=16)


def scroll_on_deck(name, ang, flip):
    """A C-scroll filling the deck panel centred on direction ang."""
    pts = fit(scroll_c(0, 0, 1), -0.07, 0.0, 0.07, 0.13, flip_x=flip)
    world = []
    for u, v in pts:          # v runs outwards along ang, u across it
        r = RING_R + 0.025 + v
        world.append((r * math.cos(ang) - u * math.sin(ang),
                      r * math.sin(ang) + u * math.cos(ang), DECK_Z + 0.006))
    curve_obj(name, world, GOLD, 0.012, plat)


for k, ang in enumerate((0.0, math.pi / 2, math.pi)):      # east, north, west panels
    scroll_on_deck(f"scroll{k}a", ang - 0.32, False)
    scroll_on_deck(f"scroll{k}b", ang + 0.32, True)
    r = RING_R + 0.1
    sphere(f"panel_dot{k}", 0.016, (r * math.cos(ang), r * math.sin(ang), DECK_Z + 0.01), GOLD,
           plat, segs=12)

# drop arrow: raised gold chevron on the south panel pointing into the prow,
# a ruby at its tip
chev = [(-0.085, -0.2), (0.0, -0.305), (0.085, -0.2)]
curve_obj("arrow", [(x, y, DECK_Z + 0.008) for x, y in chev], GOLD, 0.02, plat)
curve_obj("arrow_shaft", [(0, -RING_R - 0.01, DECK_Z + 0.008), (0, -0.285, DECK_Z + 0.008)], GOLD,
          0.016, plat)
sphere("prow_ruby", 0.026, (0.0, -0.375, DECK_Z + 0.0), RUBY, plat, segs=16)
curve_obj("prow_bezel", ring_pts(0.03, DECK_Z - 0.004, 20, 0.0, -0.375), GOLD, 0.009, plat,
          closed=True)

# cradle: turned gold cup on a short bronze pedestal, four claws holding the orb
ORB_R = 0.095
ORB_Z = 0.232
cup = lathe("cradle", [(0.105, DECK_Z), (0.105, DECK_Z + 0.012), (0.08, DECK_Z + 0.022),
                       (0.05, DECK_Z + 0.04), (0.045, DECK_Z + 0.06), (0.06, DECK_Z + 0.075),
                       (0.088, DECK_Z + 0.095), (0.1, DECK_Z + 0.112), (0.094, DECK_Z + 0.118),
                       (0.075, DECK_Z + 0.105), (0.0, DECK_Z + 0.08)], GOLD, plat)
curve_obj("cradle_lip", ring_pts(0.098, DECK_Z + 0.114, 40), GOLD, 0.012, plat, closed=True)
curve_obj("cradle_collar", ring_pts(0.05, DECK_Z + 0.048, 32), BRONZE, 0.014, plat, closed=True)
for k in range(4):
    a = k * math.pi / 2 + math.pi / 4
    c, s = math.cos(a), math.sin(a)
    # claw follows the orb's surface 0.012 out, from the cup lip up past the
    # equator, so it really holds the sphere
    pts = []
    for t in range(7):
        el = math.radians(-35 + t * 12)     # elevation on the orb
        rr = ORB_R + 0.014
        pts.append((c * rr * math.cos(el), s * rr * math.cos(el), ORB_Z + rr * math.sin(el)))
    curve_obj(f"claw{k}", pts, GOLD, 0.013, plat, taper=lambda t: 1.15 - 0.45 * t)
    sphere(f"claw_tip{k}", 0.014, pts[-1], GOLD, plat, segs=12)

orb = sphere("orb", ORB_R, (0, 0, ORB_Z), ORB, plat, segs=48)
glow(orb)
orb.visible_shadow = False          # the orb light sits inside it
orb_light_d = bpy.data.lights.new("orb_light", "POINT")
orb_light_d.color = (0.85, 0.25, 1.0)
orb_light_d.energy = 0.35
orb_light_d.shadow_soft_size = ORB_R * 0.8
orb_light = bpy.data.objects.new("orb_light", orb_light_d)
link(orb_light, plat)
orb_light.location = (0, 0, ORB_Z)

PLATFORM_OBJS = [plat] + list(plat.children_recursive)

# ============================================================================
# Glove (natural proportions; local frame: grip point at the origin, fingers
# towards +y, back of the hand up +z; a right hand, so the thumb is on -x)
# ============================================================================

MB_K = 0.575        # metaball surface radius / element radius (stiffness 2, threshold 0.6)


def blob(name, elems, mat, parent):
    """Smooth blobby mesh from metaball capsules/ellipsoids. elems: list of
    ("cap", p0, p1, r) or ("ell", centre, (rx, ry, rz)) in surface radii."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = mb.render_resolution = 0.006
    mb.threshold = 0.6
    for e in elems:
        el = mb.elements.new()
        el.stiffness = 2.0
        if e[0] == "cap":
            _, p0, p1, r = e
            p0, p1 = Vector(p0), Vector(p1)
            el.type = "CAPSULE"
            el.co = (p0 + p1) / 2
            el.radius = r / MB_K
            el.size_x = (p1 - p0).length / 2
            el.rotation = (p1 - p0).to_track_quat("X", "Z")
        else:
            _, c, (rx, ry, rz) = e
            el.type = "ELLIPSOID"
            el.co = c
            rmax = max(rx, ry, rz)
            el.radius = rmax / MB_K
            el.size_x, el.size_y, el.size_z = rx / rmax, ry / rmax, rz / rmax
    tmp = bpy.data.objects.new(name + "_mb", mb)
    link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat)
    link(o, parent)
    return o


# Lengthwise layout (y, natural tiles). The item (~0.42 tiles on screen) is
# centred on the grip point, so it spans y = -0.21..0.21: the open glove's
# fingers reach over it, the fist grips its back edge from y ~ -0.1.
CUFF_END, CUFF_START = -0.468, -0.38
WRIST_Y = -0.37


def cuff(name, parent):
    """Rolled cuff: a flared fabric tube with a fat rolled lip, a thin gold
    band and a small purple gem on top (the only magic about the glove)."""
    tube = lathe(name + "_tube", [(0.07, CUFF_START + 0.02), (0.078, CUFF_START - 0.02),
                                  (0.09, CUFF_END + 0.035), (0.098, CUFF_END + 0.01),
                                  (0.08, CUFF_END + 0.005)], CLOTH, parent, axis="Y")
    tube.scale = (1.0, 1.0, 0.72)        # the wrist is flatter than it is wide
    lip = curve_obj(name + "_lip", [(0.098 * math.cos(t), CUFF_END + 0.018,
                                     0.098 * 0.72 * math.sin(t))
                                    for t in (TAU * k / 48 for k in range(48))],
                    CLOTH, 0.022, parent, closed=True)
    lip.data.bevel_resolution = 6
    bz = CUFF_START - 0.035
    band = curve_obj(name + "_band", [(0.084 * math.cos(t), bz, 0.084 * 0.72 * math.sin(t))
                                      for t in (TAU * k / 48 for k in range(48))],
                     GOLD, 0.011, parent, closed=True)
    gz = 0.084 * 0.72 + 0.008
    curve_obj(name + "_bezel", [(0.022 * math.cos(t), bz + 0.022 * math.sin(t), gz)
                                for t in (TAU * k / 24 for k in range(24))], GOLD, 0.007, parent,
              closed=True)
    gem = sphere(name + "_gem", 0.017, (0.0, bz, gz + 0.004), GEM_EM_MAT, parent, segs=20)
    gem.scale = (1, 1, 0.7)
    gem["gem"] = True
    return tube, band, gem


def stitches(name, hand, parent, y0, y1, xs=(-0.036, 0.0, 0.036)):
    """The three stitched lines on the back of the glove, laid on its surface
    by ray-casting down onto the mesh."""
    dg = bpy.context.evaluated_depsgraph_get()
    inv = hand.matrix_world.inverted()
    for i, x in enumerate(xs):
        pts = []
        for k in range(9):
            t = k / 8
            y = y0 + (y1 - y0) * t
            xx = x * (1 + 0.25 * t)        # fan out slightly towards the knuckles
            ok, loc, *_ = hand.ray_cast(inv @ Vector((xx, y, 1.0)), Vector((0, 0, -1)))
            if ok:
                pts.append((xx, y, loc.z + 0.002))
        curve_obj(f"{name}_stitch{i}", pts, STITCH, 0.005, parent)


def glove_open():
    root = bpy.data.objects.new("glove_open", None)
    link(root)
    palm = blob("open_palm", [("ell", (0.0, -0.265, 0.0), (0.105, 0.115, 0.042)),
                              ("cap", (0.0, -0.3, -0.004), (0.0, WRIST_Y - 0.02, -0.004), 0.066)],
                CLOTH, root)
    # four puffy fingers fanning out from the knuckle line, middle longest
    fingers = ((-0.066, 0.165, 0.2), (-0.022, 0.19, 0.06), (0.024, 0.175, -0.07),
               (0.068, 0.135, -0.21))
    for i, (x, ln, ang) in enumerate(fingers):
        base = Vector((x * 0.95, -0.185, 0.004))
        d = Vector((-math.sin(ang), math.cos(ang), 0.0))
        tip = base + d * ln
        blob(f"open_finger{i}", [("cap", tuple(base), tuple(base + d * ln * 0.5 + Vector((0, 0, 0.008))),
                                  0.027),
                                 ("cap", tuple(base + d * ln * 0.5 + Vector((0, 0, 0.008))), tuple(tip),
                                  0.027)], CLOTH, root)
    blob("open_thumb", [("cap", (-0.07, -0.3, -0.005), (-0.15, -0.215, -0.002), 0.031),
                        ("cap", (-0.15, -0.215, -0.002), (-0.178, -0.145, 0.004), 0.029)],
         CLOTH, root)
    cuff("open_cuff", root)
    stitches("open", palm, root, -0.345, -0.215)
    return root


def glove_closed():
    root = bpy.data.objects.new("glove_closed", None)
    link(root)
    palm = blob("fist_palm", [("ell", (0.0, -0.285, 0.0), (0.105, 0.105, 0.055)),
                              ("cap", (0.0, -0.31, -0.004), (0.0, WRIST_Y - 0.02, -0.004), 0.066)],
                CLOTH, root)
    # curled fingers: proximal phalanx forward and down from the knuckles,
    # the rest folded back under the palm - the knuckle row is the fist's
    # front edge, gripping the back edge of the item
    for i, x in enumerate((-0.066, -0.022, 0.023, 0.066)):
        reach = (0.0, 0.012, 0.008, -0.006)[i]
        k0 = Vector((x, -0.205, 0.022))
        k1 = Vector((x * 1.02, -0.135 + reach, -0.004))
        k2 = Vector((x * 1.02, -0.15 + reach, -0.055))
        k3 = Vector((x, -0.2, -0.07))
        blob(f"fist_finger{i}", [("cap", tuple(k0), tuple(k1), 0.03), ("cap", tuple(k1), tuple(k2), 0.028),
                                 ("cap", tuple(k2), tuple(k3), 0.026)], CLOTH, root)
    # thumb folded across the front of the fingers' side, tip forward
    blob("fist_thumb", [("cap", (-0.075, -0.31, -0.01), (-0.12, -0.225, 0.0), 0.032),
                        ("cap", (-0.12, -0.225, 0.0), (-0.1, -0.15, 0.012), 0.029)],
         CLOTH, root)
    cuff("fist_cuff", root)
    stitches("fist", palm, root, -0.36, -0.24)
    return root


GLOVES = {"open": glove_open(), "closed": glove_closed()}
for g in GLOVES.values():
    # a bit bigger than the vanilla claw is wide, scaled about the grip point
    # so the item stays where the vanilla tines hold it
    g.scale = (GLOVE_SCALE,) * 3
HAND_OBJS = {k: [g] + list(g.children_recursive) for k, g in GLOVES.items()}

# ============================================================================
# Render
# ============================================================================

rig = setup_scene(PLAT["w"], PLAT["h"], PLAT["cy"])
cam = scene.camera
SUN_ROT = rig.sun.rotation_euler.copy()
SHADOW_ROT = Vector((0, 0, -1)).rotation_difference(
    Vector((1.0, -0.35, -0.75)).normalized()).to_euler()


def show(objs):
    keep = set(objs)
    for o in scene.objects:
        if o.type in ("MESH", "CURVE", "LIGHT") and o not in (rig.sun, rig.ground) \
                and o.data not in (rig.fill_d,):
            o.hide_render = o not in keep


def factorio_camera(b):
    ppt = args.px_per_tile
    cam.data.ortho_scale = max(b["w"], b["h"])
    scene.render.resolution_x = round(b["w"] * ppt)
    scene.render.resolution_y = round(b["h"] * ppt)
    cam.rotation_euler = (math.radians(45), 0, 0)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((b["cx"], 0, b["cy"] * math.sqrt(2))) - look * 30


def lights(sun=4.6, fill=1.1, bg=0.15, orb=0.35):
    rig.sun_d.energy, rig.fill_d.energy = sun, fill
    rig.bg.inputs["Strength"].default_value = bg
    orb_light_d.energy = orb


def render_platform():
    show(PLATFORM_OBJS)
    factorio_camera(PLAT)
    for d in range(4):
        # frame d = prototype vectors turned d quarter turns clockwise
        plat.rotation_euler = (0, 0, -d * math.pi / 2)
        rig.sun.rotation_euler = SUN_ROT
        rig.ground.hide_render = True
        for o in PLATFORM_OBJS:
            if o.type != "LIGHT":
                o.visible_camera = True
        lights()
        ORB_EM.default_value = 1.1
        render(OUT / f"platform-main-{d}.png")
        # light pass: only the orb's own light, so the cradle and deck pick up
        # its purple spill; turned into a light sprite by --stitch
        lights(sun=0.0, fill=0.0, bg=0.0, orb=0.6)
        render(OUT / f"platform-glow-{d}.png")
        # shadow: plate invisible, casting onto the catcher, key light lowered
        lights(fill=0.0, bg=0.0, orb=0.0)
        rig.sun.rotation_euler = SHADOW_ROT
        rig.ground.hide_render = False
        for o in PLATFORM_OBJS:
            if o.type != "LIGHT":
                o.visible_camera = False
        render(OUT / f"platform-shadow-{d}.png")
    plat.rotation_euler = (0, 0, 0)
    rig.ground.hide_render = True
    rig.sun.rotation_euler = SUN_ROT
    for o in PLATFORM_OBJS:
        if o.type != "LIGHT":
            o.visible_camera = True


def render_hands():
    """Straight down, overhead light only (the engine spins these sprites to
    every angle), pre-stretched lengthwise by HAND_STRETCH."""
    w = HAND_W_PX / HAND_PPT
    h = HAND_H_PX / HAND_PPT / HAND_STRETCH           # natural length shown
    top = GRIP_ROW / HAND_PPT / HAND_STRETCH          # grip point below the top edge
    cam.rotation_euler = (0, 0, 0)
    cam.location = (0, top - h / 2, 5)
    cam.data.ortho_scale = max(w, h)
    scene.render.resolution_x = HAND_W_PX * SS
    scene.render.resolution_y = round(HAND_W_PX * SS * h / w)
    rig.sun.rotation_euler = (0, 0, 0)               # pointing straight down
    for state, objs in HAND_OBJS.items():
        show(objs)
        lights(sun=3.4, fill=0.0, bg=0.55, orb=0.0)
        GEM_EM.default_value = 0.6
        render(OUT / f"hand-{state}-main.png")
        # light layer: just the cuff gem's faint glow
        lights(sun=0.0, fill=0.0, bg=0.0, orb=0.0)
        GEM_EM.default_value = 1.2
        for o in objs:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = not o.get("gem", False)
        render(OUT / f"hand-{state}-glow.png")
        for o in objs:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = False


rig.fill_d.energy = 1.1
import os
if os.environ.get("HANDS_ONLY") != "1":      # HANDS_ONLY=1 re-renders just the gloves
    render_platform()
render_hands()
