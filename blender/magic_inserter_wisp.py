"""
Procedural Blender model + Factorio render of the magic inserter's arm,
"wisp" variant: no glove. A stream of purple magic rises out of the orb on
the platform, runs along the inserter's (invisible) arm and ends in a puffy
cushion of magic right under the held item, carrying it.

    blender -b --factory-startup -P blender/magic_inserter_wisp.py -- \
        --out graphics/generated/magic-inserter-wisp [--samples 64]
    .venv/bin/python blender/magic_inserter_wisp.py --stitch graphics/generated/magic-inserter-wisp

The platform (orb in its gold cradle) is the one from blender/magic_inserter.py;
this script renders only the arm sprites:

    magic-inserter-wisp-base(-light|-shadow).png          hand_base_picture/_shadow
    magic-inserter-wisp-hand-{open,closed}(-light|-shadow).png   hand_*_picture/_shadow

How the engine places the arm (fitted on 2.1.22 screenshots of the vanilla
fast inserter and the magic inserter, 64 px per tile):

* hand_base: the canvas' bottom edge centre sits on the entity centre (the
  orb), its top edge centre on the elbow. Rotated to that direction and
  stretched/squashed along its length to the distance; the width is not
  scaled. With hand_size 0.6 that distance is only 5-60 screen px (0.1-0.9 of
  the 136-row canvas), longest when the arm reaches north.
* hand_open/closed: the canvas' bottom edge sits on the elbow, row GRIP_ROW
  (18 of 164, the vanilla tine row) on the grip point, where the engine draws
  the held item's icon ON TOP of the sprite. Squash 0.55-1.05.
* Both sprites spin through every angle, so they are rendered from straight
  above with overhead light only.

So the stream is a thin whimsical tendril (bright core, faint sheath, a twin
strand spiralling round it, sparkles) drawn as ONE sine wave through both
canvases: it bows out along the base bone, crosses the axis at the elbow and
swings the other way along the hand bone before curling up into the cloud.
The slope at the elbow matches in both canvases at their typical on-screen
scale, so a straight elbow is a smooth arc and any other bend (the fits show
both signs) reads as a twist of the tendril; a small diffuse vapour wisp at
both canvas ends hides the actual joint. A mist rises out of the orb at the
base's foot, which also covers the case of a very short base bone.

The clouds are true Cycles volumes (unit-sphere domains with a feathered
radial falloff, the edge broken up by low-frequency noise, a brighter heart):
one shapeless little haze cloud centred just behind the grip, densest under
the item (whose icon the engine draws on top), two offset haze blobs inside it
only to break the symmetry - no lobes, no cup. Open, a smaller looser puff.
The hand canvas ends only 18 rows past the grip, so the haze thins out before
it (that edge lies under the item).

The orb conjures the stream: the platform (rendered here as a variant of
magic_inserter.py's platform, whose platform code is executed verbatim so
the two stay identical) has fine violet lightning crawling over the visible
ball, all converging on a bright node at the orb's front-bottom rim - that is
where the engine anchors hand_base (the entity centre at ground level, seen
from 45 degrees). The bolts are fixed in screen space, the same in all 4
frames, since the stream may leave in any direction. hand_base's bottom
carries the last step: a compact fan of bolts twisting together into the
tendril. Sprites can't animate, so branching and glow (light layers: violet,
with a soft halo at night) carry the magic.
"""

import math
import random
import sys
from pathlib import Path

HAND_W_PX, HAND_H_PX = 112, 164     # vanilla hand height (the engine anchors by it)
BASE_W_PX, BASE_H_PX = 48, 136      # vanilla hand_base height (wider: the glow halo)
PPT = 128                           # canvas pixels per tile (scale 0.25)
GRIP_ROW = 18                       # vanilla tine centre: the held item's row
HAND_STRETCH = 1.3                  # pre-stretch against the engine's ~0.55-1.05 squash
BASE_STRETCH = 2.2                  # the base bone is squashed to ~0.1-0.9
SS = 4                              # supersampling

PURPLE_DEEP = (0.22, 0.03, 0.48)
PURPLE_GLOW = (0.42, 0.1, 0.95)
CORE_GLOW = (0.78, 0.42, 1.0)


def stitch(src, dest="graphics", name="magic-inserter-wisp"):
    """Pack the renders (needs PIL: run under the repo venv, not Blender)."""
    from PIL import Image, ImageFilter
    src, dest = Path(src), Path(dest)

    def load(p, size):
        return Image.open(p).convert("RGBA").resize(size, Image.LANCZOS)

    def as_light(im, gain=1.0):
        """Glow pass -> light sprite: colour normalised, density in alpha."""
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                m = min(255, round(max(r, g, b) * a / 255 * gain))
                if m < 3:
                    px[x, y] = (0, 0, 0, 0)
                else:
                    s = 255 / max(r, g, b)       # normalised, pulled to violet
                    px[x, y] = (round(0.5 * r * s + 0.5 * 175), round(0.5 * g * s + 0.5 * 70),
                                round(0.5 * min(255, b * s) + 0.5 * 255), m)
        return im

    def shadow(im, density, blur, shrink=1.0):
        """Faint soft shadow of the translucent magic: alpha * density, a
        little shrunk about the centre and blurred."""
        a = im.getchannel("A").point(lambda v: round(v * density))
        sil = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sil.putalpha(a)
        if shrink != 1.0:
            w, h = im.size
            small = sil.resize((round(w * shrink), h), Image.LANCZOS)
            sil = Image.new("RGBA", im.size, (0, 0, 0, 0))
            sil.paste(small, (round((w - small.width) / 2), 0))
        return sil.filter(ImageFilter.GaussianBlur(blur))

    # platform: 4 frames per sheet, 128 -> 64 px per tile, the shadow baked
    # into the main sheet at half density (inserter platforms draw below the
    # shadow pass), as in magic_inserter.py
    for kind, suffix in (("main", ""), ("glow", "-light")):
        imgs = []
        for d in range(4):
            im = Image.open(src / f"platform-{kind}-{d}.png").convert("RGBA")
            im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
            if kind == "glow":
                im = as_light(im, 1.3)
            else:
                sh = Image.open(src / f"platform-shadow-{d}.png").convert("RGBA").resize(
                    im.size, Image.LANCZOS)
                base = Image.new("RGBA", im.size, (0, 0, 0, 0))
                base.putalpha(sh.getchannel("A").point(lambda v: round(v * 0.5)))
                base.alpha_composite(im)
                im = base
            imgs.append(im)
        w, h = imgs[0].size
        out = Image.new("RGBA", (w * 4, h))
        for d, im in enumerate(imgs):
            out.paste(im, (d * w, 0))
        out.save(dest / f"{name}-platform{suffix}.png", optimize=True)
        print(f"platform{suffix}: 4 frames of {w}x{h}")

    parts = [("base", "base", (BASE_W_PX, BASE_H_PX))] + \
        [(f"hand-{s}", f"hand-{s}", (HAND_W_PX, HAND_H_PX)) for s in ("open", "closed")]
    for key, out, size in parts:
        main = load(src / f"{key}-main.png", size)
        main.save(dest / f"{name}-{out}.png", optimize=True)
        light = as_light(load(src / f"{key}-glow.png", size), 1.2)
        # a soft purple halo round it, so at night the magic also lights the
        # ground it passes over
        halo = light.filter(ImageFilter.GaussianBlur(5))
        r, g, b_, a = halo.split()
        halo = Image.merge("RGBA", (r, g, b_, a.point(lambda v: min(255, round(v * 1.3)))))
        tint = Image.new("RGBA", size, (150, 60, 255, 0))
        tint.putalpha(halo.getchannel("A"))
        tint.alpha_composite(light)
        tint.save(dest / f"{name}-{out}-light.png", optimize=True)
        shadow(main, 0.3, 2.0, 0.85).save(dest / f"{name}-{out}-shadow.png", optimize=True)
        print(f"{out}: {size}")


if "--stitch" in sys.argv:
    stitch(sys.argv[sys.argv.index("--stitch") + 1])
    sys.exit(0)

import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("magic-inserter-wisp", frames=1, samples=64)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

OUT = fblend.OUT
scene = bpy.context.scene

# ============================================================================
# Materials
# ============================================================================


def wisp_material(name, base, glow_col, strength, alpha, edge=1.4, noise_scale=9.0,
                  noise_amt=0.55, ao=0.0):
    """Translucent self-lit vapour: opaque-ish where the surface faces the
    camera (thick), fading to nothing at the silhouette (thin), mottled by a
    streaky noise so it reads as smoke rather than glass."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    bsdf.inputs["Base Color"].default_value = (*base, 1)
    bsdf.inputs["Emission Color"].default_value = (*glow_col, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    em = bsdf.inputs["Emission Strength"]
    em.default_value = strength
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    thick = nt.nodes.new("ShaderNodeMath")          # 1 - facing, ^edge
    thick.operation = "SUBTRACT"
    thick.inputs[0].default_value = 1.0
    L(lw.outputs["Facing"], thick.inputs[1])
    powr = nt.nodes.new("ShaderNodeMath")
    powr.operation = "POWER"
    powr.inputs[1].default_value = edge
    L(thick.outputs[0], powr.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Distortion"].default_value = 2.5
    L(tc.outputs["Object"], noise.inputs["Vector"])
    mott = nt.nodes.new("ShaderNodeMapRange")       # noise -> 1-amt .. 1
    mott.inputs["From Min"].default_value = 0.35
    mott.inputs["From Max"].default_value = 0.65
    mott.inputs["To Min"].default_value = 1.0 - noise_amt
    mott.inputs["To Max"].default_value = 1.0
    L(noise.outputs["Fac"], mott.inputs["Value"])
    a = nt.nodes.new("ShaderNodeMath")
    a.operation = "MULTIPLY"
    L(powr.outputs[0], a.inputs[0])
    L(mott.outputs["Result"], a.inputs[1])
    a2 = nt.nodes.new("ShaderNodeMath")
    a2.operation = "MULTIPLY"
    a2.use_clamp = True
    a2.inputs[1].default_value = alpha
    L(a.outputs[0], a2.inputs[0])
    L(a2.outputs[0], bsdf.inputs["Alpha"])
    # brighter where thick, so the body has a glowing heart and soft rim
    emk = nt.nodes.new("ShaderNodeMath")
    emk.operation = "MULTIPLY"
    emk.inputs[1].default_value = strength
    L(a.outputs[0], emk.inputs[0])
    L(emk.outputs[0], em)
    if ao:
        # darker in the folds between the lumps, so the cloud's bulges read
        # under the flat overhead light
        aon = nt.nodes.new("ShaderNodeAmbientOcclusion")
        aon.inputs["Distance"].default_value = 0.06
        aon.only_local = True
        aon.samples = 16
        fold = nt.nodes.new("ShaderNodeMapRange")
        fold.inputs["To Min"].default_value = 1.0 - ao
        L(aon.outputs["AO"], fold.inputs["Value"])
        for sock, col in ((bsdf.inputs["Base Color"], base), (bsdf.inputs["Emission Color"], glow_col)):
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            mix.inputs["A"].default_value = (*col, 1)
            L(fold.outputs["Result"], mix.inputs["B"])
            L(mix.outputs["Result"], sock)
    return m


SHEATH = wisp_material("wisp_sheath", PURPLE_DEEP, PURPLE_GLOW, 1.2, 0.42, edge=1.3,
                       noise_scale=18.0, noise_amt=0.6)
STRAND = wisp_material("wisp_strand", (0.6, 0.35, 0.95), (0.75, 0.45, 1.0), 1.8, 0.6,
                       edge=0.6, noise_scale=14.0, noise_amt=0.5)
CORE = wisp_material("wisp_core", CORE_GLOW, CORE_GLOW, 1.6, 0.9, edge=0.6, noise_amt=0.25)
SPARK, _ = emitter("spark", (1.0, 0.8, 1.0), 6.0, base=(1, 0.9, 1))


def cloud_material(name, density, emit, heart=0.0, noise_scale=2.6, erode=0.9, seed=0.0):
    """Diffuse magic vapour as a true volume inside a unit-sphere domain
    (scaled to the cloud's size): dense in the middle, feathered to nothing
    at the rim, the rim eaten into curling wisps by a distorted noise, an
    optional brighter heart in the middle."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    L(pv.outputs[0], out.inputs["Volume"])
    pv.inputs["Color"].default_value = (0.62, 0.38, 1.0, 1)
    pv.inputs["Absorption Color"].default_value = (0.55, 0.25, 0.95, 1)
    pv.inputs["Emission Color"].default_value = (*PURPLE_GLOW, 1)

    def math_node(op, a, b=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath")
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

    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    L(tc.outputs["Object"], ln.inputs[0])
    r = ln.outputs["Value"]
    fall = nt.nodes.new("ShaderNodeMapRange")        # 1 inside r<0.2 .. 0 at r=1
    fall.interpolation_type = "SMOOTHSTEP"
    fall.inputs["From Min"].default_value = 1.0
    fall.inputs["From Max"].default_value = 0.2
    L(r, fall.inputs["Value"])
    off = nt.nodes.new("ShaderNodeVectorMath")
    off.operation = "ADD"
    off.inputs[1].default_value = (seed, seed * 0.7, seed * 1.3)
    L(tc.outputs["Object"], off.inputs[0])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.6
    noise.inputs["Distortion"].default_value = 1.4
    L(off.outputs[0], noise.inputs["Vector"])
    wisp = nt.nodes.new("ShaderNodeMapRange")
    wisp.inputs["From Min"].default_value = 0.38
    wisp.inputs["From Max"].default_value = 0.7
    L(noise.outputs["Fac"], wisp.inputs["Value"])
    # field = falloff*1.3 - (1 - wisp)*erode: the noise carves the thin rim
    # into wisps but leaves the thick middle whole
    inv = math_node("SUBTRACT", 1.0, wisp.outputs["Result"])
    carve = math_node("MULTIPLY", inv, erode)
    f13 = math_node("MULTIPLY", fall.outputs["Result"], 1.3)
    field = math_node("SUBTRACT", f13, carve, clamp=True)
    L(math_node("MULTIPLY", field, density), pv.inputs["Density"])
    em = math_node("MULTIPLY", field, emit)
    if heart:
        h = nt.nodes.new("ShaderNodeMapRange")       # bright core r < 0.45
        h.interpolation_type = "SMOOTHSTEP"
        h.inputs["From Min"].default_value = 0.5
        h.inputs["From Max"].default_value = 0.0
        h.inputs["To Max"].default_value = heart
        L(r, h.inputs["Value"])
        em = math_node("ADD", em, h.outputs["Result"])
    L(em, pv.inputs["Emission Strength"])
    return m


# ============================================================================
# Geometry
# ============================================================================


def vapour(name, c, radii, mat, parent):
    """A volume domain: unit sphere scaled to radii; mat shapes the vapour."""
    o = sphere(name, 1.0, c, mat, parent, segs=24)
    o.scale = radii
    return o


def helix(name, path, radius, amp, turns, phase, mat, parent, n=80):
    """A thin strand winding round path at distance amp(t)."""
    def p(t):
        x, y, z = path(t)
        a = phase + TAU * turns * t
        return (x + amp(t) * math.cos(a), y, z + amp(t) * math.sin(a) * 0.8)
    return curve_obj(name, [p(i / n) for i in range(n + 1)], mat, 1.0, parent, res=4,
                     taper=radius)


def sparkles(name, path, spread, count, parent, seed, rmin=0.006, rmax=0.01, t0=0.08, t1=0.92):
    rng = random.Random(seed)
    for k in range(count):
        t = t0 + (t1 - t0) * (k + rng.uniform(0.2, 0.8)) / count
        x, y, z = path(t)
        a = rng.uniform(0, TAU)
        d = spread * rng.uniform(0.5, 1.3)
        sphere(f"{name}{k}", rng.uniform(rmin, rmax),
               (x + d * math.cos(a), y, z + abs(d * math.sin(a))), SPARK, parent, segs=10)


def tendril(name, root, path, seed, r_core=0.007, r_sheath=0.03, sparks=3, fade=(0.0, 1.0)):
    """The magic stream: a thin bright core in a faint glowing sheath, a
    fainter twin strand spiralling round it, sparkles along it. Thin ends."""
    n = 60
    pts = [path(i / n) for i in range(n + 1)]

    def taper(lo, hi):
        def f(t):
            a = min(1.0, (t - 0.0) / 0.12) if fade[0] else 1.0
            b = min(1.0, (1.0 - t) / 0.12) if fade[1] else 1.0
            return max(0.25, min(a, b))
        return lambda t: f(t)
    tp = taper(0, 1)
    curve_obj(name + "_core", pts, CORE, r_core, root, res=4, taper=tp)
    curve_obj(name + "_sheath", pts, SHEATH, r_sheath, root, res=6, taper=tp)
    helix(name + "_twin", path, lambda t: 0.0045 * math.sin(math.pi * t) ** 0.6,
          lambda t: r_sheath * 1.05, 2.2, seed, STRAND, root)
    sparkles(name + "_spark", path, r_sheath * 1.6, sparks, root, seed)


def smooth01(t):
    return t * t * (3 - 2 * t)


# violet, not white: it has to show on the pale orb by day; the light layer
# makes it glow at night
BOLT, _ = emitter("bolt", (0.5, 0.14, 1.0), 2.6, base=(0.25, 0.04, 0.6))


def jag(p0, p1, rng, n=6, jitter=0.25):
    """A lightning zig-zag from p0 to p1: n segments, the inner points pushed
    sideways (in the plane perpendicular to the bolt and to view/z) by up to
    jitter x the segment length."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    seg = d.length / n
    pts = [p0]
    for i in range(1, n):
        pts.append(p0 + d * (i / n) + side * rng.uniform(-1, 1) * jitter * seg)
    pts.append(p1)
    return pts


def bolt(name, pts, r, parent, branch_rng=None, branches=0, br_len=0.4):
    """A thin bright bolt along pts (tapering to its end), plus a few short
    side branches forking off it."""
    curve_obj(name, [tuple(p) for p in pts], BOLT, r, parent, res=2,
              taper=lambda t: 1.0 - 0.45 * t)
    rng = branch_rng
    for k in range(branches):
        i = rng.randrange(1, len(pts) - 1)
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        d = (b - a)
        side = d.cross(Vector((0, 0, 1))).normalized() * rng.choice((-1, 1))
        end = a + (d.normalized() * 0.6 + side * 0.8).normalized() * d.length * br_len * 3
        curve_obj(f"{name}_br{k}", [tuple(p) for p in jag(a, end, rng, 3, 0.3)], BOLT, r * 0.7,
                  parent, res=2, taper=lambda t: 1.0 - 0.6 * t)


JOINT = cloud_material("joint", 60.0, 5.0, noise_scale=2.2, erode=0.7, seed=3.0)
ORB_MIST = cloud_material("orb_mist", 35.0, 5.0, noise_scale=2.0, erode=0.6, seed=5.0)

# The stream is one sine wave running through both sprites: it leaves the
# orb, bows out to +x along the base bone, crosses the axis at the elbow
# heading -x, swings out to -x along the hand bone and curls up into the
# cloud. Bow amplitudes are chosen so the slope at the elbow matches in both
# canvases at their typical on-screen scale (base ~0.45 squash x 2.2
# pre-stretch, hand ~0.77 x 1.3: both ~1x natural): pi*B/BASE_SPAN ==
# pi*C/HAND_SPAN. Tangents then meet at a straight elbow; any other bend
# reads as a twist of the tendril, and a small diffuse wisp at both canvas
# ends hides the actual joint.
SLOPE = 0.2          # |dx/dy| of the wave where it crosses the elbow (~11 deg)

# ---------------------------------------------------------------------------
# hand_base: canvas-local, bottom edge (the orb) at y=0, top edge (elbow) at
# y = BASE_LEN; natural (pre-stretch) length.
BASE_LEN = BASE_H_PX / PPT / BASE_STRETCH
B_Y0, B_Y1 = 0.02, BASE_LEN - 0.012
B_AMP = SLOPE * (B_Y1 - B_Y0) / math.pi
Z_ARM = 0.12

base_root = bpy.data.objects.new("base", None)
link(base_root)


def base_path(t):
    return (B_AMP * math.sin(math.pi * t), B_Y0 + (B_Y1 - B_Y0) * t, Z_ARM)


# The canvas bottom is the engine's anchor: the entity centre, which on
# screen is the orb's bottom-front rim. Over the orb the stream would look
# like it starts at the orb's foot, so the bottom ~40% of the canvas carries
# no stream: only a few thin bolts (like the platform's crackle, which they
# blend into where they lie over the orb) climbing to the fade-in point,
# where the tendril tears loose in a small burst of spikes and mist. Across
# the fitted poses the orb's silhouette lies ~0.3-0.5 of the way along the
# base bone when it points up the screen (long bones), ~0.1-0.2 sideways and
# at 0 downward (short bones), so the burst sits at 0.42 and the bolts fill
# everything below it.
Y_FADE = 0.42 * BASE_LEN
T_ROOT = (Y_FADE - B_Y0) / (B_Y1 - B_Y0)
tendril("base", base_root, lambda t: base_path(T_ROOT + (1 - T_ROOT) * t), 1.0, sparks=2,
        fade=(1, 0))
rng_b = random.Random(21)
root_pt = Vector(base_path(T_ROOT))
for k, (x0, y0) in enumerate([(-0.07, 0.03), (-0.035, 0.0), (0.0, 0.07), (0.04, 0.01),
                              (0.075, 0.045)]):
    bolt(f"root_bolt{k}", jag((x0, y0, Z_ARM), root_pt + Vector((rng_b.uniform(-0.01, 0.01),
                                                                 -0.01, 0)), rng_b, 6, 0.4),
         0.006, base_root, rng_b, 1 if k in (0, 4) else 0, 0.25)
# the burst: short spikes radiating from where the stream tears loose
for k in range(6):
    a = math.radians(-90 + k * 36 + rng_b.uniform(-12, 12))
    ln = rng_b.uniform(0.03, 0.055)
    end = root_pt + Vector((math.cos(a) * ln * 1.3, math.sin(a) * ln, 0))
    bolt(f"burst{k}", jag(root_pt, end, rng_b, 3, 0.4), 0.005, base_root)
sphere("burst_core", 0.014, tuple(root_pt), SPARK, base_root, segs=12)
vapour("base_mist", tuple(root_pt), (0.07, 0.05, 0.04), ORB_MIST, base_root)
vapour("base_joint", (0.0, BASE_LEN - 0.02, Z_ARM), (0.055, 0.045, 0.04), JOINT, base_root)
BASE_OBJS = [base_root] + list(base_root.children_recursive)

# ---------------------------------------------------------------------------
# hands: canvas-local, grip point (item centre) at the origin, +y towards the
# canvas top, the elbow at y = -HAND_BOT (canvas bottom).
HAND_BOT = (HAND_H_PX - GRIP_ROW) / PPT / HAND_STRETCH
HAND_TOP = GRIP_ROW / PPT / HAND_STRETCH


def hand(state):
    root = bpy.data.objects.new(f"hand_{state}", None)
    link(root)
    closed = state == "closed"
    rng = random.Random(7 if closed else 11)
    cz = 0.06
    if closed:
        # cushion: one shapeless little cloud of haze centred just behind the
        # grip - densest and brightest right under the item, fading smoothly
        # out to an irregular, noise-broken edge. Two offset haze blobs inside
        # it only break the symmetry (no lobes, no cup). It thins out before
        # the canvas top (HAND_TOP), which lies under the item.
        cy = -0.06
        main = cloud_material("cushion", 150.0, 6.0, heart=16.0, noise_scale=1.5, erode=1.0,
                              seed=1.0)
        haze = cloud_material("cushion_haze", 90.0, 4.5, noise_scale=1.3, erode=1.0, seed=2.0)
        vapour("cushion", (0.0, cy, cz), (0.37, 0.24, 0.08), main, root)
        vapour("cushion_haze0", (0.1, cy - 0.05, cz), (0.24, 0.16, 0.06), haze, root)
        vapour("cushion_haze1", (-0.12, cy + 0.0, cz), (0.22, 0.15, 0.06), haze, root)
        end_y, curl = cy - 0.12, 0.04
    else:
        # open: a smaller, looser puff of the same haze
        cy = -0.06
        main = cloud_material("puff", 130.0, 5.5, heart=10.0, noise_scale=1.4, erode=1.1,
                              seed=4.0)
        haze = cloud_material("puff_haze", 80.0, 4.0, noise_scale=1.2, erode=1.1, seed=6.0)
        vapour("puff", (0.0, cy, cz), (0.2, 0.16, 0.07), main, root)
        vapour("puff_haze", (0.05, cy - 0.05, cz), (0.14, 0.11, 0.05), haze, root)
        end_y, curl = cy - 0.07, 0.035
    # the tendril: enters at the elbow heading -x (continuing the base's
    # wave), swings out and back, then curls up into the cloud's underside
    y0 = -HAND_BOT + 0.012
    span = end_y - y0
    amp = SLOPE * span / math.pi

    def path(t):
        x = -amp * math.sin(math.pi * t)
        # the last stretch hooks round into the cloud
        k = max(0.0, (t - 0.7) / 0.3)
        x += curl * math.sin(math.pi * k) * (1 if closed else -1) * smooth01(k)
        return (x, y0 + span * t, Z_ARM + (cz - Z_ARM) * smooth01(t))
    tendril(f"{state}_arm", root, path, 2.0 if closed else 3.0, sparks=3, fade=(0, 1))
    vapour(f"{state}_joint", (0.0, -HAND_BOT + 0.02, Z_ARM), (0.055, 0.045, 0.04), JOINT, root)
    # a few sparkles drifting off the cloud's rim
    rim = (0.3, 0.2) if closed else (0.16, 0.13)
    for k in range(4 if closed else 3):
        a = rng.uniform(math.radians(195), math.radians(345))
        sphere(f"{state}_rimspark{k}", rng.uniform(0.006, 0.01),
               (rim[0] * math.cos(a), cy + rim[1] * math.sin(a), cz + 0.08), SPARK, root,
               segs=10)
    return root


HANDS = {s: hand(s) for s in ("open", "closed")}
HAND_OBJS = {k: [h] + list(h.children_recursive) for k, h in HANDS.items()}

# ============================================================================
# Platform: the glove version's plate and orb, unchanged (the platform section
# of blender/magic_inserter.py is executed here verbatim, so both stay
# identical), plus static lightning crackling all over the orb.
# ============================================================================

_src = (Path(__file__).parent / "magic_inserter.py").read_text()
_a = _src.index("STONE = paint(")
_b = _src.rindex("# =====", 0, _src.index("# Glove ("))
exec(compile(_src[_a:_b], "magic_inserter.py:platform", "exec"), globals())
PLAT = dict(w=1.0, h=0.75, cx=0.0625, cy=0.0)   # as magic_inserter.py

# The stream may leave the orb in any direction (hand_base's own bolts tie
# into this crackle), so the bolts wrap the whole visible ball, denser over
# its upper half and round its edges. Fixed in screen space: identical in
# all 4 frames while the plate turns.
VIEW = Vector((0, -1, 1)).normalized()
UP_S = Vector((0, 1, 1)).normalized()
RT_S = VIEW.cross(UP_S)
ORB_C = Vector((0, 0, ORB_Z))
crackle = bpy.data.objects.new("crackle", None)
link(crackle)


def on_orb(d, lift=0.004):
    return ORB_C + d.normalized() * (ORB_R + lift)


def ball_dir(az, tilt):
    """Direction from the orb centre: tilt off the view axis, azimuth about
    it (0 = screen up, 90 = screen right)."""
    a, t = math.radians(az), math.radians(tilt)
    return VIEW * math.cos(t) + (UP_S * math.cos(a) + RT_S * math.sin(a)) * math.sin(t)


def surface_bolt(d0, d1, rng, n=9):
    """A zig-zag bolt hugging the sphere from direction d0 to d1."""
    d0, d1 = d0.normalized(), d1.normalized()
    axis = d0.cross(d1).normalized()
    pts = []
    for i in range(n + 1):
        t = i / n
        d = d0.slerp(d1, t)
        if 0 < i < n:
            side = 1 if i % 2 else -1
            d = d + axis * side * rng.uniform(0.04, 0.17) * math.sin(math.pi * t) ** 0.6
        pts.append(on_orb(d))
    return pts


rng_o = random.Random(5)
# (start azimuth, start tilt off the view axis, azimuth turn, end tilt):
# bolts crossing the face from and to the rim, most over the upper half
BOLTS = [(-30, 30, 80, 72), (20, 55, 70, 30), (80, 72, -60, 42), (-80, 66, 50, 35),
         (-140, 74, 60, 48), (140, 58, -50, 78), (175, 42, 60, 70), (0, 80, -70, 82),
         (-170, 50, -60, 80), (-115, 25, 95, 62), (150, 20, -80, 66)]
for k, (az, t0, turn, t1) in enumerate(BOLTS):
    d0 = ball_dir(az + rng_o.uniform(-8, 8), t0)
    d1 = ball_dir(az + turn + rng_o.uniform(-8, 8), t1)
    bolt(f"orb_bolt{k}", surface_bolt(d0, d1, rng_o), 0.0072, crackle, rng_o, 2, 0.25)
for o in list(crackle.children):
    if o.type == "CURVE" and "_br" in o.name:     # branches hug the ball too
        for sp in o.data.splines:
            for pt in sp.points:
                v = Vector(pt.co[:3])
                pt.co = (*on_orb(v - ORB_C, 0.004), 1)
CRACKLE_OBJS = [crackle] + list(crackle.children_recursive)
PLATFORM_OBJS = PLATFORM_OBJS + CRACKLE_OBJS

# ============================================================================
# Render: straight down, overhead light only (the engine spins the sprites)
# ============================================================================

rig = setup_scene(1.0, 1.0, 0.0)
cam = scene.camera
scene.cycles.transparent_max_bounces = 64
scene.cycles.volume_step_rate = 0.25
scene.cycles.volume_bounces = 1


def show(objs):
    keep = set(objs)
    for o in scene.objects:
        if o.type in ("MESH", "CURVE") and o is not rig.ground:
            o.hide_render = o not in keep


def top_camera(w, y0, y1, px_w):
    """Ortho camera straight down over x in [-w/2, w/2], y in [y0, y1]."""
    h = y1 - y0
    cam.rotation_euler = (0, 0, 0)
    cam.location = (0, (y0 + y1) / 2, 5)
    cam.data.ortho_scale = max(w, h)
    scene.render.resolution_x = px_w
    scene.render.resolution_y = round(px_w * h / w)


def passes(key, objs):
    show(objs)
    rig.sun.rotation_euler = (0, 0, 0)
    rig.sun_d.energy, rig.fill_d.energy = 2.2, 0.0
    rig.bg.inputs["Strength"].default_value = 0.5
    render(OUT / f"{key}-main.png")
    # light layer: emission only
    rig.sun_d.energy = 0.0
    rig.bg.inputs["Strength"].default_value = 0.0
    render(OUT / f"{key}-glow.png")


SUN_ROT = rig.sun.rotation_euler.copy()
SHADOW_ROT = Vector((0, 0, -1)).rotation_difference(
    Vector((1.0, -0.35, -0.75)).normalized()).to_euler()


def factorio_camera(b):
    cam.data.ortho_scale = max(b["w"], b["h"])
    scene.render.resolution_x = round(b["w"] * args.px_per_tile)
    scene.render.resolution_y = round(b["h"] * args.px_per_tile)
    cam.rotation_euler = (math.radians(45), 0, 0)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((b["cx"], 0, b["cy"] * math.sqrt(2))) - look * 30


def plat_lights(sun=4.6, fill=1.1, bg=0.15, orb=0.35):
    rig.sun_d.energy, rig.fill_d.energy = sun, fill
    rig.bg.inputs["Strength"].default_value = bg
    orb_light_d.energy = orb


def render_platform():
    """As magic_inserter.py's render_platform (the plate turns per frame),
    plus the crackle, which stays fixed and casts no shadow."""
    show(PLATFORM_OBJS)
    factorio_camera(PLAT)
    meshes = [o for o in PLATFORM_OBJS if o.type in ("MESH", "CURVE")]
    for d in range(4):
        plat.rotation_euler = (0, 0, -d * math.pi / 2)
        rig.sun.rotation_euler = SUN_ROT
        rig.ground.hide_render = True
        for o in meshes:
            o.visible_camera = True
        plat_lights()
        ORB_EM.default_value = 0.55
        render(OUT / f"platform-main-{d}.png")
        plat_lights(sun=0.0, fill=0.0, bg=0.0, orb=0.6)
        render(OUT / f"platform-glow-{d}.png")
        plat_lights(fill=0.0, bg=0.0, orb=0.0)
        rig.sun.rotation_euler = SHADOW_ROT
        rig.ground.hide_render = False
        for o in meshes:
            o.visible_camera = False
        for o in CRACKLE_OBJS:
            if o.type in ("MESH", "CURVE"):
                o.hide_render = True
        render(OUT / f"platform-shadow-{d}.png")
        for o in CRACKLE_OBJS:
            if o.type in ("MESH", "CURVE"):
                o.hide_render = False
    plat.rotation_euler = (0, 0, 0)
    rig.ground.hide_render = True
    rig.sun.rotation_euler = SUN_ROT
    for o in meshes:
        o.visible_camera = True
    orb_light_d.energy = 0.0
    rig.fill_d.energy = 0.0


render_platform()
top_camera(BASE_W_PX / PPT, 0.0, BASE_LEN, BASE_W_PX * SS)
passes("base", BASE_OBJS)
top_camera(HAND_W_PX / PPT, -HAND_BOT, HAND_TOP, HAND_W_PX * SS)
for state, objs in HAND_OBJS.items():
    passes(f"hand-{state}", objs)
