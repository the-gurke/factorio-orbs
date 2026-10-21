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

HAND_W_PX, HAND_H_PX = 128, 164     # vanilla height; wider than vanilla (72) so the
                                    # digits wrapped round a held item fit
HAND_PPT = 128                      # its pixels per tile (scale 0.25)
GRIP_ROW = 18                       # vanilla tine centre: the held item's row
HAND_STRETCH = 1.25                 # pre-stretch against the engine's measured ~0.6-0.77 squash
PLAT = dict(w=1.0, h=0.75, cx=0.0625, cy=0.0)   # platform frame box, screen tiles
SS = 4                              # hand supersampling
GLOVE_SCALE = 1.0                   # the glove below is modelled at on-screen size


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

    # platform: one 4-frame row per pass. The shadow is baked into the main
    # sheet like vanilla's platform: inserter platforms sit on a render layer
    # below the shadow pass, so a separate draw_as_shadow sheet gets drawn
    # OVER the plate in the engine (seen in 2.1.22: the plate came out at
    # ~45% brightness). Vanilla's baked shadow is black at alpha ~128.
    for kind, suffix in (("main", ""), ("glow", "-glow")):
        imgs = [load(src / f"platform-{kind}-{d}.png") for d in range(4)]
        if kind == "glow":
            imgs = [as_light(im) for im in imgs]
        else:
            baked = []
            for d, im in enumerate(imgs):
                sh = shadow(load(src / f"platform-shadow-{d}.png"), 0.5)
                sh.alpha_composite(im)
                baked.append(sh)
            imgs = baked
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
        # soft ground shadow of a hovering hand: the silhouette shrunk a little
        # about its centre, blurred, light density (the engine draws it
        # displaced on the ground, which is what sells the height)
        sil = shadow(main, 0.42)
        bb = sil.getchannel("A").getbbox()
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        k = 0.88
        small = sil.resize((round(sil.width * k), round(sil.height * k)), Image.LANCZOS)
        sh = Image.new("RGBA", sil.size, (0, 0, 0, 0))
        sh.paste(small, (round(cx - cx * k), round(cy - cy * k)))
        sh = sh.filter(ImageFilter.GaussianBlur(2.5))
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
    """The magic orb item's look: pale, faintly blue-white glass with a milky,
    softly clouded inside, a little brighter in the core, under a clear coat
    that takes a sharp sun highlight."""
    m, em = emitter("magic_orb", (0.82, 0.9, 1.0), 0.55, base=(0.78, 0.84, 0.9), glass=True)
    nt = m.node_tree
    L = nt.links.new
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.5
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Distortion"].default_value = 1.5
    L(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.3, (0.62, 0.72, 0.82, 1)
    els[1].position, els[1].color = 0.75, (0.95, 0.98, 1.0, 1)
    L(noise.outputs["Fac"], ramp.inputs["Fac"])
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    core = nt.nodes.new("ShaderNodeMapRange")       # facing -> 1 at centre, 0.45 at rim
    core.inputs["To Min"].default_value = 1.0
    core.inputs["To Max"].default_value = 0.45
    L(lw.outputs["Facing"], core.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L(ramp.outputs["Color"], mul.inputs["A"])
    L(core.outputs["Result"], mul.inputs["B"])
    L(mul.outputs["Result"], bsdf.inputs["Emission Color"])
    L(mul.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.15
    bsdf.inputs["Coat Roughness"].default_value = 0.03
    return m, em


ORB, ORB_EM = orb_material()
GEM_EM_MAT, GEM_EM = emitter("cuff_gem", (0.8, 0.2, 1.0), 0.6, base=(0.35, 0.05, 0.45),
                             glass=True)


def cloth():
    """Cream glove fabric: soft weave bump, a touch of sheen, and a slightly
    darker rim (by facing ratio) so the silhouette holds on light ground."""
    m = paint("glove", (0.93, 0.9, 0.81), (0.45, 0.42, 0.38), noise_scale=30.0,
              bump=0.35, bump_scale=220.0, dirt=0.0, ao_dist=0.08)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Sheen Weight"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.1
    b.inputs["Subsurface Radius"].default_value = (0.02, 0.02, 0.02)
    col = b.inputs["Base Color"].links[0].from_socket
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    rim = nt.nodes.new("ShaderNodeMix")
    rim.data_type = "RGBA"
    rim.inputs["B"].default_value = (0.5, 0.46, 0.4, 1)
    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.inputs["From Min"].default_value = 0.55
    fr.inputs["From Max"].default_value = 1.0
    fr.inputs["To Max"].default_value = 0.8
    nt.links.new(lw.outputs["Facing"], fr.inputs["Value"])
    nt.links.new(fr.outputs["Result"], rim.inputs["Factor"])
    nt.links.new(col, rim.inputs["A"])
    nt.links.new(rim.outputs["Result"], b.inputs["Base Color"])
    return m


CLOTH = cloth()
DECK = paint("deck", (0.18, 0.03, 0.135), (0.02, 0.003, 0.016), noise_scale=9.0, bump=0.6,
             bump_scale=25.0, dirt=0.2, hammered=True)    # PURPLE, darker: it faces the sun
SEAM = paint("seam", (0.72, 0.68, 0.6), (0.4, 0.37, 0.33), bump=0.0, dirt=0.0)
CUFF_IN = paint("cuff_inside", (0.35, 0.32, 0.28), (0.08, 0.07, 0.06), bump=0.0, dirt=0.0)


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

# The orb is the magic orb item itself (graphics/magic-orb.png: pale,
# slightly blue-white glass) at the size it shows lying on the ground: items
# on the ground are drawn with the icon 0.5 tiles wide and the sphere fills
# 62% of the icon, so ~0.31 tiles across. It rests in a low, open gold ring
# with four short claws, so the orb dominates the plate.
ORB_R = 0.155
SEAT_R, SEAT_Z = 0.112, DECK_Z + 0.035        # ring the orb sits in
ORB_Z = SEAT_Z + math.sqrt(ORB_R ** 2 - SEAT_R ** 2)
lathe("cradle", [(0.13, DECK_Z), (0.13, DECK_Z + 0.01), (0.11, DECK_Z + 0.02),
                 (0.105, SEAT_Z - 0.005), (0.118, SEAT_Z + 0.004), (0.11, SEAT_Z + 0.008),
                 (0.07, SEAT_Z - 0.01), (0.0, SEAT_Z - 0.012)], GOLD, plat)
curve_obj("cradle_lip", ring_pts(SEAT_R + 0.006, SEAT_Z + 0.004, 48), GOLD, 0.013, plat,
          closed=True)
curve_obj("cradle_foot", ring_pts(0.13, DECK_Z + 0.006, 48), BRONZE, 0.012, plat, closed=True)
for k in range(4):
    a = k * math.pi / 2 + math.pi / 4
    c, s_ = math.cos(a), math.sin(a)
    # short claws following the orb's lower half, 0.012 off its surface
    pts = []
    for t in range(5):
        el = math.radians(-45 + t * 10)
        rr = ORB_R + 0.012
        pts.append((c * rr * math.cos(el), s_ * rr * math.cos(el), ORB_Z + rr * math.sin(el)))
    curve_obj(f"claw{k}", pts, GOLD, 0.013, plat, taper=lambda t: 1.15 - 0.4 * t)
    sphere(f"claw_tip{k}", 0.015, pts[-1], RUBY if k % 2 else GOLD, plat, segs=12)

orb = sphere("orb", ORB_R, (0, 0, ORB_Z), ORB, plat, segs=64)
glow(orb)
orb.visible_shadow = False          # the orb light sits inside it
orb_light_d = bpy.data.lights.new("orb_light", "POINT")
orb_light_d.color = (0.82, 0.9, 1.0)
orb_light_d.energy = 0.35
orb_light_d.shadow_soft_size = ORB_R * 0.8
orb_light = bpy.data.objects.new("orb_light", orb_light_d)
link(orb_light, plat)
orb_light.location = (0, 0, ORB_Z)

PLATFORM_OBJS = [plat] + list(plat.children_recursive)

# ============================================================================
# Glove (natural on-screen proportions; local frame: grip point at the origin,
# fingers towards +y, up +z towards the camera; a right hand, thumb on -x)
# ============================================================================
#
# The engine draws the held item's icon AFTER the hand sprite, centred on the
# grip point and NOT rotated with the hand (2.1.22 screenshots): a ~0.5 tile
# box whose content (an iron plate, ~85% of the box for most icons) covers
# everything within ~ITEM_R of the grip, whatever the arm's angle. So the
# glove pinches the item from behind: palm, back of the hand and cuff sit on
# the arm side, and the thumb and the fingers reach forward round the item's
# left and right edges, staying outside ITEM_R so they read as wrapped round
# it, not hidden under it. Open, the same hand hovers with the digits spread
# and hanging down, ready to pinch. Fingertips point down, so seen from above
# they are foreshortened knobs; the cuff rises towards the (invisible) arm, so
# its opening shows. That, overhead light and soft occlusion between the
# digits give it volume.
#
# Lengthwise the engine squashes the canvas by s ~ 0.55-1.0 on top of
# HAND_STRETCH, so a natural y shows at y * HAND_STRETCH * s: things beside
# the item (|x| > ITEM_R) are safe at any squash, the palm's front edge sits
# back far enough to clear the item at the typical squash.

MB_K = 0.575        # metaball surface radius / element radius (stiffness 2, threshold 0.6)
ITEM_R = 0.24       # screen radius around the grip covered by a held item icon (plates and
                    # gears reach ~0.23-0.24; the fingertips just touch that edge)


def blob(name, elems, mat, parent):
    """Smooth blobby mesh from metaball capsules/ellipsoids. elems: list of
    ("cap", p0, p1, r) or ("ell", centre, (rx, ry, rz), pitch) in surface radii."""
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
            _, c, (rx, ry, rz), pitch = e
            el.type = "ELLIPSOID"
            el.co = c
            rmax = max(rx, ry, rz)
            el.radius = rmax / MB_K
            el.size_x, el.size_y, el.size_z = rx / rmax, ry / rmax, rz / rmax
            el.rotation = Euler((pitch, 0, 0)).to_quaternion()
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


def digit(name, pts, radii, parent):
    """A finger or thumb: a chain of capsules through pts, tapering."""
    return blob(name, [("cap", pts[i], pts[i + 1], radii[i]) for i in range(len(pts) - 1)],
                CLOTH, parent)


WRIST = Vector((0.0, -0.59, 0.20))
CUFF_TILT = math.atan(0.5)          # the cuff rises towards the arm
CUFF_LEN = 0.12


def cuff(name, parent):
    """Rolled cuff rising back towards the invisible arm: a flared fabric tube
    with a fat rolled lip (its opening shows from above), a thin gold band
    and a small purple gem on top."""
    holder = bpy.data.objects.new(name, None)
    link(holder, parent)
    holder.location = WRIST
    holder.rotation_euler = (-CUFF_TILT, 0, 0)
    tube = lathe(name + "_tube", [(0.07, 0.03), (0.08, 0.0), (0.088, -0.06),
                                  (0.1, -CUFF_LEN + 0.012), (0.096, -CUFF_LEN)], CLOTH, holder,
                 axis="Y")
    tube.scale = (1.0, 1.0, 0.8)
    inner = lathe(name + "_inside", [(0.088, -CUFF_LEN + 0.004), (0.07, -0.03)], CUFF_IN, holder,
                  axis="Y")
    inner.scale = (1.0, 1.0, 0.8)
    lip = curve_obj(name + "_lip", [(0.1 * math.cos(t), -CUFF_LEN + 0.008, 0.08 * math.sin(t))
                                    for t in (TAU * k / 48 for k in range(48))],
                    CLOTH, 0.024, holder, closed=True)
    lip.data.bevel_resolution = 6
    bz = -0.035
    curve_obj(name + "_band", [(0.088 * math.cos(t), bz, 0.0715 * math.sin(t))
                               for t in (TAU * k / 48 for k in range(48))],
              GOLD, 0.011, holder, closed=True)
    gz = 0.0715 + 0.008
    curve_obj(name + "_bezel", [(0.021 * math.cos(t), bz + 0.021 * math.sin(t), gz)
                                for t in (TAU * k / 24 for k in range(24))], GOLD, 0.007, holder,
              closed=True)
    gem = sphere(name + "_gem", 0.016, (0.0, bz, gz + 0.004), GEM_EM_MAT, holder, segs=20)
    gem.scale = (1, 1, 0.7)
    gem["gem"] = True
    return holder


def seam(name, hand, parent):
    """One faint seam down the middle of the back, laid on the surface."""
    inv = hand.matrix_world.inverted()
    pts = []
    for k in range(10):
        y = -0.51 + 0.16 * k / 9
        ok, loc, *_ = hand.ray_cast(inv @ Vector((0.02, y, 1.0)), Vector((0, 0, -1)))
        if ok:
            pts.append((0.02, y, loc.z + 0.001))
    curve_obj(name + "_seam", pts, SEAM, 0.0035, parent)


def hand_back(name, parent):
    """Big puffy back of the hand hovering just behind the item, tipped down
    at the front, and the wrist rising to the cuff. Cartoon proportions: the
    palm is about as wide as the item it holds."""
    return blob(name, [("ell", (0.0, -0.41, 0.16), (0.2, 0.15, 0.1), math.radians(-14)),
                       ("cap", (0.0, -0.47, 0.18), tuple(WRIST + Vector((0, 0.02, 0))), 0.095)],
                CLOTH, parent)


# fat, short cartoon digits with round tips
R_FINGER = (0.064, 0.06)
R_THUMB = (0.07, 0.066)


def glove_open():
    root = bpy.data.objects.new("glove_open", None)
    link(root)
    back = hand_back("open_back", root)
    # spread and hanging down, ready to pinch: thumb out to the left, fingers
    # fanning round the right and front of where the item will be
    digit("open_thumb", [(-0.17, -0.39, 0.15), (-0.33, -0.27, 0.11), (-0.38, -0.11, 0.04)],
          R_THUMB, root)
    digit("open_index", [(0.04, -0.3, 0.19), (0.12, -0.14, 0.15), (0.17, 0.0, 0.05)],
          R_FINGER, root)
    digit("open_middle", [(0.12, -0.32, 0.18), (0.27, -0.21, 0.14), (0.35, -0.07, 0.04)],
          R_FINGER, root)
    digit("open_ring", [(0.17, -0.39, 0.17), (0.33, -0.33, 0.12), (0.39, -0.22, 0.04)],
          (0.06, 0.056), root)
    digit("open_pinky", [(0.17, -0.47, 0.15), (0.31, -0.47, 0.1), (0.36, -0.38, 0.04)],
          (0.052, 0.048), root)
    cuff("open_cuff", root)
    seam("open", back, root)
    return root


def glove_closed():
    root = bpy.data.objects.new("glove_closed", None)
    link(root)
    back = hand_back("fist_back", root)
    # pinching the item from behind: the thumb wraps down its left edge, index
    # and middle wrap down its right edge, staying outside ITEM_R so the icon
    # drawn over the hand leaves them visible; ring and pinky curled in
    xt = ITEM_R + R_THUMB[1]
    xf = ITEM_R + R_FINGER[1]
    digit("fist_thumb", [(-0.17, -0.36, 0.15), (-xt - 0.04, -0.2, 0.1), (-xt, -0.03, 0.03)],
          R_THUMB, root)
    digit("fist_index", [(0.13, -0.3, 0.18), (xf + 0.03, -0.17, 0.12), (xf, -0.01, 0.03)],
          R_FINGER, root)
    digit("fist_middle", [(0.17, -0.37, 0.17), (xf + 0.06, -0.28, 0.1), (xf + 0.04, -0.15, 0.02)],
          R_FINGER, root)
    digit("fist_ring", [(0.18, -0.44, 0.15), (0.31, -0.43, 0.09), (0.31, -0.37, 0.04)],
          (0.056, 0.052), root)
    digit("fist_pinky", [(0.15, -0.5, 0.13), (0.27, -0.51, 0.08)], (0.048,), root)
    cuff("fist_cuff", root)
    seam("fist", back, root)
    return root


GLOVES = {"open": glove_open(), "closed": glove_closed()}
for g in GLOVES.values():
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
        ORB_EM.default_value = 0.55
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
