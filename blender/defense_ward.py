"""
Procedural Blender model + Factorio render of the defense ward (1x1 turret).

The ward is an active magic shard on a staff: a turned wooden staff with
riveted iron bands, planted in a small stone footing braced with bronze, and
topped by a riveted collar cup whose four gold claws hold the shard. When
biters come near the claws open and the shard lifts out of the cup and hovers,
turning slowly. Just before it fires it stops turning, shudders and glows up
while arcs gather into it from the claws; it fires exactly once (control.lua
destroys the ward when its beam hits), so the beam itself is the engine's.

Renders every turret state as its own clip:

    blender -b --factory-startup -P blender/defense_ward.py -- \
        --out graphics/generated/defense-ward [--preview --frame 0,15,30]

`--frame` takes indices into the concatenated timeline (SEGMENTS below).
Then pack the sheets (per state: main, glow and shadow) with

    .venv/bin/python blender/defense_ward.py --stitch graphics/generated/defense-ward

World units are Factorio tiles; the ward is 1x1 centred on the origin, +y is
north, +z is up. Shared helpers live in blender/fblend.py.
"""

import math
import random
import sys
import zlib
from pathlib import Path

# (state, frame count). Order = timeline order for --frame.
SEGMENTS = (("preparing", 16), ("prepared", 48), ("starting", 12), ("attacking", 8),
            ("ending", 12))
# Frame boxes in render tiles. cx/cy: screen position of the box centre
# relative to the entity origin (+y up). The shadow box reaches far to the
# south-east because the staff is tall.
MAIN_BOX = dict(w=1.0, h=2.375, cx=0.0, cy=0.78)
SHADOW_BOX = dict(w=4.25, h=1.75, cx=1.62, cy=-0.42)


def stitch(src, dest="graphics", name="defense-ward", render_ppt=128, ppt=64, cols=8):
    """Pack the renders into one sheet per state and pass (needs PIL, so this
    runs under the repo's venv python, not inside Blender)."""
    from PIL import Image
    src, dest = Path(src), Path(dest)

    def load(p):
        im = Image.open(p).convert("RGBA")
        k = ppt / render_ppt
        return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)

    for state, n in SEGMENTS:
        for kind, suffix in (("main", ""), ("glow", "-glow"), ("shadow", "-shadow")):
            imgs = [load(src / f"{state}-{kind}-{i:03d}.png") for i in range(n)]
            if kind == "shadow":
                # Factorio shadow sprites: black, density in alpha
                imgs = [Image.merge("RGBA", (*Image.new("RGB", im.size).split(),
                                             im.getchannel("A"))) for im in imgs]
            w, h = imgs[0].size
            c = min(cols, n)
            out = Image.new("RGBA", (w * c, h * math.ceil(n / c)))
            for i, im in enumerate(imgs):
                out.paste(im, ((i % c) * w, (i // c) * h))
            path = dest / f"{name}-{state}{suffix}.png"
            out.save(path, optimize=True)
            print(f"{path}: {n} frames of {w}x{h}, sheet {out.size}")


if "--stitch" in sys.argv:
    stitch(sys.argv[sys.argv.index("--stitch") + 1])
    sys.exit(0)

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("defense-ward", frames=sum(n for _, n in SEGMENTS), samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

OUT = fblend.OUT


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------

def wood(name):
    """Turned oak: long grain streaks along the staff (wave bands stretched
    along z, distorted), darker in the grain, with a fine fibre bump."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 0.08)   # grain runs along z
    L(tc.outputs["Object"], mp.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 9.0
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 3.0
    L(mp.outputs["Vector"], wave.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 30.0
    noise.inputs["Detail"].default_value = 8.0
    L(mp.outputs["Vector"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMath")
    mix.operation = "MULTIPLY"
    L(wave.outputs["Fac"], mix.inputs[0])
    L(noise.outputs["Fac"], mix.inputs[1])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.05, (0.07, 0.035, 0.015, 1)
    els[1].position, els[1].color = 0.45, (0.48, 0.27, 0.12, 1)
    e = els.new(0.25)
    e.color = (0.27, 0.14, 0.06, 1)
    L(mix.outputs[0], ramp.inputs["Fac"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.08
    L(ramp.outputs["Color"], ao.inputs["Color"])
    L(ao.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.62
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.35
    b.inputs["Distance"].default_value = 0.01
    L(mix.outputs[0], b.inputs["Height"])
    L(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


WOOD = wood("wood")
IRON = metal("iron", (0.30, 0.29, 0.28), (0.03, 0.03, 0.03), rough=(0.35, 0.6), hammered=True,
             bump=0.4, bump_scale=40.0)
STONE = paint("stone", (0.16, 0.145, 0.13), (0.035, 0.03, 0.028), noise_scale=12.0, bump=0.8,
              bump_scale=30.0, dirt=0.35)

# The shard: a translucent magenta body, its edges glowing hot and cracked
# veins inside, like the item icon. Emission strengths are animated by glow.
SHARD, SHARD_EM = emitter("shard_body", (0.55, 0.06, 0.95), 0.6, base=(0.3, 0.03, 0.6),
                          glass=True)
_sb = SHARD.node_tree.nodes["Principled BSDF"]
_sb.inputs["Transmission Weight"].default_value = 0.4
_sb.inputs["Roughness"].default_value = 0.18
EDGE, EDGE_EM = emitter("shard_edge", (1.0, 0.22, 0.85), 2.0)
VEIN, VEIN_EM = emitter("shard_vein", (0.95, 0.28, 1.0), 2.4)
ARC, ARC_EM = emitter("arc", (0.9, 0.3, 1.0), 2.5)
SOCKET, SOCKET_EM = emitter("socket", (0.7, 0.12, 0.95), 0.5, base=(0.05, 0.01, 0.06))

root = bpy.data.objects.new("defense_ward", None)
link(root)
# The model is laid out at 1/1.35 size and scaled up as a whole: at true
# size the shard is a few pixels at zoom 1. Scaled, the staff stands like a
# lamp post (about half a medium pole) on a footing still inside its tile.
WARD_SCALE = 1.35
root.scale = (WARD_SCALE,) * 3

# ----------------------------------------------------------------------------
# Footing and staff
# ----------------------------------------------------------------------------
#
# Tall and thin like a lamp post: the footing stays small so the staff and the
# shard are the subject. The stone slab carries a bronze collar that the
# staff is planted in, held by four riveted bronze braces.

SLAB_H, SLAB_HALF = 0.07, 0.29
STAFF_R0, STAFF_R1 = 0.06, 0.05   # staff radius at foot and head
STAFF_Z0, STAFF_Z1 = SLAB_H, 1.2


def octagon(h, ch):
    return [(-h + ch, -h), (h - ch, -h), (h, -h + ch), (h, h - ch),
            (h - ch, h), (-h + ch, h), (-h, h - ch), (-h, -h + ch)]


def frustum(name, bot, top, z0, z1, mat, parent=root, bevel=0.008):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in bot]
    t = [bm.verts.new((x, y, z1)) for x, y in top]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(bot)):
        j = (i + 1) % len(bot)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent, bevel=bevel)
    o.data.shade_flat()
    return o


def ring_pts(r, n=48):
    return [(r * math.cos(TAU * i / n), r * math.sin(TAU * i / n)) for i in range(n)]


def hoop(name, r, z, mat, rad):
    return curve_obj(name, [(x, y, z) for x, y in ring_pts(r)], mat, rad, root, closed=True)


def rivets(name, r, z, n, mat=BRONZE, size=0.012, a0=0.0):
    for k in range(n):
        a = a0 + TAU * k / n
        sphere(f"{name}{k}", size, (r * math.cos(a), r * math.sin(a), z), mat, root, segs=10)


# --- footing ---------------------------------------------------------------------
frustum("slab", octagon(SLAB_HALF, 0.09), octagon(SLAB_HALF - 0.025, 0.08), 0, SLAB_H, STONE)
curve_obj("slab_rail", [(x, y, SLAB_H) for x, y in octagon(SLAB_HALF - 0.025, 0.08)], GOLD,
          0.014, root, closed=True)
COLLAR_Z1 = 0.2
cyl("foot_collar", 0.11, COLLAR_Z1 - SLAB_H, (0, 0, (SLAB_H + COLLAR_Z1) / 2), BRONZE, root,
    verts=32, r2=0.075)
hoop("foot_collar_rim", 0.112, SLAB_H + 0.012, GOLD, 0.016)
hoop("foot_collar_top", 0.078, COLLAR_Z1, BRONZE, 0.014)
rivets("foot_collar_rivet", 0.1, SLAB_H + 0.05, 8, mat=GOLD, size=0.011)
BRACE_Z = 0.42
for k in range(4):       # diagonal braces from the slab corners up to an iron band
    a = TAU * (k + 0.5) / 4
    foot = Vector((0.23 * math.cos(a), 0.23 * math.sin(a), SLAB_H + 0.005))
    head = Vector((0.072 * math.cos(a), 0.072 * math.sin(a), BRACE_Z))
    d = head - foot
    o = bpy.data.objects.new(f"brace{k}", None)
    link(o, root)
    o.location = foot
    o.rotation_euler = d.to_track_quat("X", "Z").to_euler()
    box(f"brace{k}_bar", (d.length, 0.032, 0.014), (d.length / 2, 0, 0), BRONZE, o, bevel=0.004)
    box(f"brace{k}_shoe", (0.06, 0.04, 0.018), (0, 0, -0.004), BRONZE, o, bevel=0.004)
    for t in (0.0, 0.92):
        sphere(f"brace{k}_rivet{t}", 0.011, tuple(foot + d * t + Vector((0, 0, 0.012))), GOLD,
               root, segs=10)

# --- staff: turned wood, riveted iron bands ---------------------------------------
staff_h = STAFF_Z1 - STAFF_Z0
cyl("staff", STAFF_R0, staff_h, (0, 0, (STAFF_Z0 + STAFF_Z1) / 2), WOOD, root, verts=24,
    r2=STAFF_R1, bevel=0.0)


def staff_r(z):
    return STAFF_R0 + (STAFF_R1 - STAFF_R0) * (z - STAFF_Z0) / staff_h


for k, z in enumerate((BRACE_Z, 0.82)):
    r = staff_r(z) + 0.012
    cyl(f"band{k}", r, 0.06, (0, 0, z), IRON, root, verts=32, bevel=0.005)
    rivets(f"band{k}_rivet", r, z, 6, size=0.012, a0=0.3 * k)
for k, z in enumerate((1.06, 1.1)):   # turned beads under the head
    cyl(f"bead{k}", staff_r(z) + 0.012, 0.022, (0, 0, z), WOOD, root, verts=24, bevel=0.008)

# --- collar cup on the head ------------------------------------------------------
CUP_Z0, CUP_Z1 = 1.14, 1.27
CUP_R = 0.105
cyl("cup_neck", 0.07, 0.07, (0, 0, CUP_Z0 + 0.0), IRON, root, verts=32, r2=CUP_R)
cup = mesh_obj("cup", ring_mesh(ring_pts(CUP_R + 0.008), ring_pts(CUP_R - 0.022), CUP_Z0 + 0.03,
                                CUP_Z1), IRON, root, smooth=True, bevel=0.006)
hoop("cup_lip", CUP_R - 0.006, CUP_Z1, GOLD, 0.014)
hoop("cup_foot", CUP_R + 0.008, CUP_Z0 + 0.035, BRONZE, 0.011)
rivets("cup_rivet", CUP_R + 0.012, (CUP_Z0 + CUP_Z1) / 2 + 0.01, 8, size=0.014)
cyl("cup_floor", CUP_R - 0.022, 0.01, (0, 0, CUP_Z1 - 0.05), IRON, root, verts=32)
glow(cyl("cup_socket", 0.05, 0.006, (0, 0, CUP_Z1 - 0.044), SOCKET, root, verts=24))

# --- four gold claws on the cup rim, hinged so they can open ----------------------
CLAW_R = CUP_R - 0.004
CLAW_OPEN = math.radians(32)
CLAWS = []
for k in range(4):
    a = TAU * (k + 0.5) / 4               # on the diagonals: none hides the shard
    h = bpy.data.objects.new(f"claw{k}", None)
    link(h, root)
    h.location = (CLAW_R * math.cos(a), CLAW_R * math.sin(a), CUP_Z1)
    h.rotation_mode = "XYZ"
    # in the hinge frame x points radially out, z up; the claw curls inwards
    pts = [(0.0, 0, 0.0), (0.006, 0, 0.05), (-0.004, 0, 0.1), (-0.03, 0, 0.14), (-0.045, 0, 0.15)]
    curve_obj(f"claw{k}_arm", pts, GOLD, 0.014, h, taper=lambda t: 1.0 - 0.45 * t)
    sphere(f"claw{k}_tip", 0.013, (-0.047, 0, 0.15), GOLD, h, segs=12)
    sphere(f"claw{k}_ruby", 0.016, (0.012, 0, 0.012), RUBY, h, segs=12)
    cyl(f"claw{k}_knuckle", 0.012, 0.035, (0, 0, 0), BRASS, h, rot=(math.radians(90), 0, 0),
        verts=12)
    CLAWS.append((h, a))
CLAW_TIP = Vector((-0.047, 0, 0.15))

# ----------------------------------------------------------------------------
# The shard
# ----------------------------------------------------------------------------
#
# An irregular blade-like shard (flattened cross section, offset apex) built
# from jittered rings, so it reads as a broken shard, not a gem. Its edges are
# traced with glowing curves and cracked veins run inside the translucent body.

rng = random.Random(7)
shard = bpy.data.objects.new("shard", None)
link(shard, root)
NS = 6
LEVELS = ((-0.15, 0.0), (-0.05, 0.62), (0.08, 1.0), (0.24, 0.72), (0.4, 0.3))   # (z, radius scale)
SH_R, SH_FLAT = 0.12, 0.7
APEX = Vector((0.03, -0.01, 0.5))
angles = [TAU * i / NS + rng.uniform(-0.25, 0.25) for i in range(NS)]
radii = [rng.uniform(0.75, 1.0) for _ in range(NS)]
bm = bmesh.new()
rings = []
for li, (z, s) in enumerate(LEVELS):
    if s == 0.0:
        rings.append([bm.verts.new((0.0, 0.0, z))])
        continue
    ring = []
    for i in range(NS):
        r = SH_R * s * radii[i] * rng.uniform(0.9, 1.08)
        a = angles[i] + 0.12 * li                    # a slight twist up the shard
        ring.append(bm.verts.new((r * math.cos(a), SH_FLAT * r * math.sin(a),
                                  z + rng.uniform(-0.015, 0.015))))
    rings.append(ring)
apex = bm.verts.new(tuple(APEX))
rings.append([apex])
for lo, hi in zip(rings, rings[1:]):
    for i in range(NS):
        j = (i + 1) % NS
        if len(lo) == 1:
            bm.faces.new((lo[0], hi[j], hi[i]))
        elif len(hi) == 1:
            bm.faces.new((lo[i], lo[j], hi[0]))
        else:
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
EDGE_LINES = [[tuple(r[0 if len(r) == 1 else i].co) for r in rings] for i in range(NS)]
GIRDLE = [tuple(v.co) for v in rings[2]]
shard_body = mesh_obj("shard_body", bm, SHARD, shard)
shard_body.data.shade_flat()
glow(shard_body)
for i, line in enumerate(EDGE_LINES):    # the ridges glow hot
    glow(curve_obj(f"shard_edge{i}", line, EDGE, 0.0065, shard))
glow(curve_obj("shard_girdle", GIRDLE, EDGE, 0.005, shard, closed=True))


def shard_r(z):
    """Smallest radius of the shard at height z (keeps the veins inside)."""
    zs = [LEVELS[0][0]] + [lz for lz, _ in LEVELS[1:]] + [APEX.z]
    ss = [0.0] + [ls for _, ls in LEVELS[1:]] + [0.0]
    for (z0, s0), (z1, s1) in zip(zip(zs, ss), zip(zs[1:], ss[1:])):
        if z0 <= z <= z1:
            return SH_R * 0.75 * (s0 + (s1 - s0) * (z - z0) / (z1 - z0))
    return 0.0


for k in range(4):                       # cracked veins inside
    z0, z1 = rng.uniform(-0.08, 0.02), rng.uniform(0.22, 0.38)
    u = rng.uniform(-0.5, 0.5)
    pts = []
    for s in range(8):
        z = z0 + (z1 - z0) * s / 7
        u = max(-0.6, min(0.6, u + rng.uniform(-0.35, 0.35)))
        pts.append((u * shard_r(z), 0.0, z))
    glow(curve_obj(f"shard_vein{k}", pts, VEIN, 0.0045, shard))
shard_light_d = bpy.data.lights.new("shard_light", "POINT")
shard_light_d.color = (1.0, 0.3, 0.95)
shard_light_d.shadow_soft_size = 0.05
shard_light = bpy.data.objects.new("shard_light", shard_light_d)
link(shard_light, shard)
shard_light.location = (0, 0, 0.12)

SEAT_Z = CUP_Z1 - 0.06       # shard origin when seated (bottom point inside the cup)
LIFT = 0.17                  # hover height above the seat
HOVER_C = 0.12               # shard centre above its origin (beam source)

# ----------------------------------------------------------------------------
# States
# ----------------------------------------------------------------------------
#
# Clip boundaries meet: preparing ends on prepared frame 0; starting_attack
# starts there and ends at peak charge, which attacking holds and ending_attack
# leaves, returning to prepared frame 0. The shard is irregular, so the idle
# loop turns it one whole revolution.

IDLE_N = dict(SEGMENTS)["prepared"]
IDLE_RATE = TAU / IDLE_N                 # radians per frame while hovering
PEAK = 2.2                               # glow at full charge ("glows up a little")


class Pose:
    open = 0.0           # claws, 0 closed .. 1 open
    lift = 0.0           # 0 seated .. 1 hovering
    bob = 0.0
    spin = 0.0
    shake = Vector((0, 0, 0))
    glow = 0.12
    arcs = ()            # (from, to) world points
    seed = 0


def claw_tip_world(k, op):
    h, a = CLAWS[k]
    m = (Matrix.Translation(h.location) @ Matrix.Rotation(a, 4, "Z")
         @ Matrix.Rotation(CLAW_OPEN * op, 4, "Y"))
    return m @ CLAW_TIP


def shard_centre(p):
    return Vector((0, 0, SEAT_Z + LIFT * p.lift + p.bob + HOVER_C)) + p.shake


def gather_sources(rng, n, op):
    """Points arcs reach the shard from: claw tips, then cup rivets."""
    src = []
    for _ in range(n):
        if rng.random() < 0.7:
            src.append(claw_tip_world(rng.randrange(4), op))
        else:
            a = rng.uniform(0, TAU)
            src.append(Vector(((CUP_R + 0.015) * math.cos(a), (CUP_R + 0.015) * math.sin(a),
                               CUP_Z1 - 0.03)))
    return src


def state_pose(state, i, n):
    p = Pose()
    p.seed = zlib.crc32(f"{state}{i}".encode())
    r = random.Random(p.seed)
    if state == "preparing":
        u = i / (n - 1)
        p.open = smooth(u / 0.55)
        p.lift = smooth((u - 0.3) / 0.7)
        p.glow = 0.12 + 0.88 * smooth(u)
    elif state == "prepared":
        q = i / n
        p.open, p.lift = 1.0, 1.0
        p.bob = 0.014 * math.sin(TAU * q)
        p.spin = TAU * q
        p.glow = 1.0 + 0.12 * math.sin(TAU * q)
        if i in (9, 10, 31):             # an occasional crackle to a claw
            p.arcs = [(claw_tip_world(r.randrange(4), 1.0), None)]
    elif state == "starting":
        # charge-up: the turn slows to a stop (constant deceleration from the
        # idle rate), the shard rises a hair and shudders, arcs gather in
        t = i / n                        # frame 0 = prepared frame 0
        p.open, p.lift = 1.0, 1.0 + 0.15 * smooth(t / 0.8)
        p.spin = IDLE_RATE * n * (t - t * t / 2)
        k = smooth(t / 0.9)
        p.glow = 1.0 + (PEAK - 1.0) * k
        if i:
            p.shake = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0)) * 0.008 * k
        p.arcs = [(s, None) for s in gather_sources(r, round(3 * k + 0.2), 1.0)]
    elif state == "attacking":
        # held at peak charge, humming
        p.open, p.lift = 1.0, 1.15
        p.spin = IDLE_RATE * dict(SEGMENTS)["starting"] / 2
        p.glow = PEAK + 0.05 * math.sin(TAU * i / n)
        if i:
            p.shake = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0)) * 0.008
        p.arcs = [(s, None) for s in gather_sources(r, 3, 1.0)]
    elif state == "ending":
        t = (i + 1) / n                  # last frame = prepared frame 0
        p.open = 1.0
        p.lift = 1.15 - 0.15 * smooth(t)
        p.spin = IDLE_RATE * dict(SEGMENTS)["starting"] / 2 * (1 - smooth(t))
        p.glow = PEAK - (PEAK - 1.0) * smooth(t)
        if i < 3:
            p.arcs = [(s, None) for s in gather_sources(r, 2 - i // 2, 1.0)]
    return p


ARCS = []


def apply(p):
    for h, a in CLAWS:
        h.rotation_euler = (0, CLAW_OPEN * p.open, a)
    c = shard_centre(p)
    shard.location = c - Vector((0, 0, HOVER_C))
    shard.rotation_euler = (0, 0, p.spin)
    g = p.glow
    SHARD_EM.default_value = 0.25 * g
    EDGE_EM.default_value = 1.0 * g
    VEIN_EM.default_value = 1.3 * g
    SOCKET_EM.default_value = 0.15 + 0.6 * g
    RUNE_EM.default_value = 0.1
    shard_light_d.energy = 0.0 if g < 0.2 else 0.5 * g ** 2
    for o in ARCS:
        bpy.data.objects.remove(o, do_unlink=True)
    ARCS.clear()
    rng = random.Random(p.seed)
    for n, (a, _) in enumerate(p.arcs):
        # jagged bolt from the source into the shard's surface
        d = c - a
        end = c - d.normalized() * 0.05
        side = d.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        pts = []
        for s in range(8):
            t = s / 7
            q = a.lerp(end, t)
            if 0 < s < 7:
                q += side * rng.uniform(-0.025, 0.025) + Vector((0, 0, rng.uniform(-0.02, 0.02)))
            pts.append(tuple(q))
        ARCS.append(glow(curve_obj(f"arc{n}", pts, ARC, 0.005, root)))


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

rig = setup_scene(MAIN_BOX["w"], MAIN_BOX["h"], MAIN_BOX["cy"])
cam = bpy.context.scene.camera
scene = bpy.context.scene


def frame_box(b):
    """Point the Factorio camera at a box (tiles, screen coords from the origin)."""
    ppt = args.px_per_tile
    cam.data.ortho_scale = max(b["w"], b["h"])
    scene.render.resolution_x = round(b["w"] * ppt)
    scene.render.resolution_y = round(b["h"] * ppt)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((b["cx"], 0, b["cy"] * math.sqrt(2))) - look * 30


TIMELINE = [(s, i, n) for s, n in SEGMENTS for i in range(n)]
frames = [int(f) for f in args.frame.split(",")] if args.preview else range(len(TIMELINE))
lights = (rig.sun_d, rig.fill_d, shard_light_d)
SUN_ROT = rig.sun.rotation_euler.copy()
SHADOW_ROT = Vector((0, 0, -1)).rotation_difference(
    Vector((1.0, -0.35, -0.75)).normalized()).to_euler()


def all_meshes():
    return [o for o in scene.objects if o.type in ("MESH", "CURVE") and o is not rig.ground]


for g in frames:
    state, i, n = TIMELINE[g]
    p = state_pose(state, i, n)
    stem = f"{state}-%s-{i:03d}.png"

    # main
    frame_box(MAIN_BOX)
    apply(p)
    rig.sun_d.energy, rig.fill_d.energy = 4.6, 1.1
    rig.bg.inputs["Strength"].default_value = 0.15
    rig.ground.hide_render = True
    rig.sun.rotation_euler = SUN_ROT
    for o in all_meshes():
        o.is_holdout = False
        o.visible_camera = True
    render(OUT / (stem % "main"))

    # glow: self-lit parts only, the rest held out
    for l in lights:
        l.energy = 0.0
    rig.bg.inputs["Strength"].default_value = 0.0
    for o in all_meshes():
        o.is_holdout = not o.get("glow", False)
    render(OUT / (stem % "glow"))
    for o in all_meshes():
        o.is_holdout = False

    # shadow: the ward invisible, casting onto the catcher, key light lowered
    # so it falls to the south-east like vanilla shadows
    frame_box(SHADOW_BOX)
    rig.ground.hide_render = False
    rig.sun_d.energy = 4.6
    rig.sun.rotation_euler = SHADOW_ROT
    for o in all_meshes():
        o.visible_camera = False
    render(OUT / (stem % "shadow"))
    for o in all_meshes():
        o.visible_camera = True
