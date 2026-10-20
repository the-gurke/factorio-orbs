"""
Procedural Blender model + Factorio render of the defense ward (1x1 turret).

The ward is a purple-and-gold obelisk crowned by a closed lotus bud of six
hinged petals with a focusing crystal sleeping inside. When biters come near
the bud opens (a lift carriage inside the capital pushes the petals' tail
levers up, rolling them open), the crystal floats up out of its cradle with
its two gimbal rings swinging out, and it hovers, gathering motes from the
petal tips, until it fires its one beam.

Renders every turret state as its own seamless clip:

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
SEGMENTS = (("preparing", 16), ("prepared", 32), ("attacking", 16), ("ending", 8))
# Frame boxes in tiles of the render (main/glow, and the longer shadow that
# falls to the south-east). cx/cy: screen position of the box centre relative
# to the entity origin (+y up).
MAIN_BOX = dict(w=1.25, h=1.75, cx=0.0, cy=0.375)
SHADOW_BOX = dict(w=3.0, h=1.5, cx=0.9, cy=-0.25)


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

CRYSTAL, CRYSTAL_EM = emitter("crystal", (0.85, 0.2, 1.0), 1.0, base=(0.35, 0.05, 0.5),
                              glass=True)
ARC, ARC_EM = emitter("arc", (0.95, 0.35, 1.0), 5.0)
MOTE, MOTE_EM = emitter("mote", (0.9, 0.25, 1.0), 1.6)
SOCKET, SOCKET_EM = emitter("socket", (0.7, 0.15, 0.9), 0.5, base=(0.05, 0.01, 0.06))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


root = bpy.data.objects.new("defense_ward", None)
link(root)

# ----------------------------------------------------------------------------
# Body
# ----------------------------------------------------------------------------
#
# A 1x1 building should fill its tile like the vanilla small lamp does, so the
# plinth spans almost the whole footprint. The obelisk tapers strongly so its
# side faces read as wings in the 45 degree view, and the tall crown sits in
# the middle where it cannot hide anything behind it.

PL_B, PL_T, PL_H, PL_CH = 0.46, 0.41, 0.12, 0.1   # plinth half widths, height, chamfer
OB_B, OB_T = 0.30, 0.19                          # obelisk half widths (bottom, top)
OB_Z1 = 0.70                                     # obelisk top
NECK_Z1 = 0.76
Z_H = 0.82                                       # hinge plane on the capital
CAP_R, BORE_R = 0.27, 0.195                      # capital ring outer / bore radius
R_H = 0.205                                      # petal hinge radius


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


# --- plinth: sloped bronze skirt, thick gold rail, rivets and rubies ----------
pb, pt = octagon(PL_B, PL_CH), octagon(PL_T, PL_CH * 0.9)
frustum("plinth", pb, pt, 0.0, PL_H, BRONZE)
curve_obj("plinth_rail", [(x, y, PL_H) for x, y in pt], GOLD, 0.03, root, closed=True)
curve_obj("plinth_foot", [(x, y, 0.015) for x, y in pb], GOLD, 0.018, root, closed=True)
for k, (x, y) in enumerate(((-0.24, -0.43), (-0.08, -0.43), (0.08, -0.43), (0.24, -0.43))):
    sphere(f"plinth_rivet{k}", 0.018, (x, y + 0.012, PL_H * 0.5), GOLD, root)
for sx in (-1, 1):   # rubies on the front chamfers
    a = Vector((sx * (PL_B - PL_CH / 2), -PL_B + PL_CH / 2, PL_H * 0.5))
    sphere(f"plinth_ruby{sx}", 0.026, tuple(a + Vector((sx * 0.01, -0.01, 0))), RUBY, root)

# --- obelisk: four hammered purple faces with gold ribs and frames -------------
ob = [Vector(v) for v in ((-OB_B, -OB_B, PL_H), (OB_B, -OB_B, PL_H), (OB_B, OB_B, PL_H),
                          (-OB_B, OB_B, PL_H))]
ot = [Vector(v) for v in ((-OB_T, -OB_T, OB_Z1), (OB_T, -OB_T, OB_Z1), (OB_T, OB_T, OB_Z1),
                          (-OB_T, OB_T, OB_Z1))]
faces = []
for i in range(4):
    j = (i + 1) % 4
    p = Panel(ob[i], ob[j], ot[j], ot[i])
    p.build(f"ob_face{i}", PURPLE, parent=root)
    faces.append(p)
for i in range(4):       # heavy gold corner ribs
    curve_obj(f"ob_rib{i}", [tuple(ob[i] + Vector((0, 0, 0.01))), tuple(ot[i])], GOLD, 0.032,
              root)
curve_obj("ob_cornice", [tuple(v + Vector((0, 0, 0.005))) for v in ot], GOLD, 0.03, root,
          closed=True)
curve_obj("ob_base_rail", [tuple(v + Vector((0, 0, 0.02))) for v in ob], GOLD, 0.026, root,
          closed=True)

front = faces[0]
fp = sub_panel(front, 0.17, 0.83, 0.1, 0.9)
gold_frame(fp, "front_frame", 0.022, parent=root)
rp = sub_panel(fp, 0.12, 0.88, 0.3, 0.9)
# the ward's sigil: a rune that wakes with the crystal
for gi, stroke in enumerate(RUNES[1]):
    glow(curve_obj(f"front_rune{gi}", [rp.at(0.1 + 0.8 * u, 0.05 + 0.9 * v, 0.008)
                                       for u, v in stroke], RUNE, 0.019, root))
fp.studs("front_ruby", [(0.5, 0.13)], r=0.03, mat=RUBY, parent=root)
fp.filigree("front_fil", [fit(scroll_c(0, 0, 1), 0.06, 0.02, 0.44, 0.26),
                          fit(scroll_c(0, 0, 1), 0.56, 0.02, 0.94, 0.26, flip_x=True)],
            radius=0.014, parent=root)
for i in (1, 3):         # east / west wings: framed scroll plates
    sp = sub_panel(faces[i], 0.14, 0.86, 0.1, 0.9)
    gold_frame(sp, f"side{i}_frame", 0.02, parent=root)
    inner = sub_panel(sp, 0.1, 0.9, 0.08, 0.92)
    inner.filigree(f"side{i}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.3, 1.0, 1.0, flip_x=(i == 3)),
                                    fit(scroll_c(0, 0, 1, up=False), 0.0, 0.0, 0.8, 0.35,
                                        flip_x=(i == 1))],
                   radius=0.016, parent=root)
    inner.studs(f"side{i}_ruby", [(0.5, 0.55)], r=0.024, mat=RUBY, parent=root)
gold_frame(sub_panel(faces[2], 0.14, 0.86, 0.1, 0.9), "back_frame", 0.02, parent=root)

# --- corner pylons: anchor stones that feed the ward, taller at the back -------
PYLONS = []
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * 0.345, sy * 0.345
        h = 0.56 if sy > 0 else 0.4
        frustum(f"pylon{sx}{sy}", [(x + u * 0.055, y + v * 0.055) for u, v in
                                   ((-1, -1), (1, -1), (1, 1), (-1, 1))],
                [(x + u * 0.032, y + v * 0.032) for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
                PL_H, h, BRONZE, bevel=0.006)
        for zz in (PL_H + 0.05, h - 0.03):
            r = 0.05 - 0.02 * (zz - PL_H) / (h - PL_H)
            box(f"pylon_band{sx}{sy}{zz:.2f}", (2 * r + 0.02, 2 * r + 0.02, 0.03), (x, y, zz), GOLD,
                root, bevel=0.006)
        cyl(f"pylon_cap{sx}{sy}", 0.03, 0.04, (x, y, h + 0.02), GOLD, root, verts=16)
        sphere(f"pylon_ruby{sx}{sy}", 0.03, (x, y, h + 0.06), RUBY, root, segs=16)
        PYLONS.append(Vector((x, y, h + 0.06)))
        # gold scroll bracket bracing the pylon against the obelisk
        bz = PL_H + 0.5 * (h - PL_H)
        t = (bz - PL_H) / (OB_Z1 - PL_H)
        half = OB_B + (OB_T - OB_B) * t
        a = Vector((x - sx * 0.03, y - sy * 0.03, bz))
        b = Vector((sx * half, sy * half, bz + 0.08))
        mid = (a + b) / 2 + Vector((0, 0, 0.06))
        curve_obj(f"pylon_brace{sx}{sy}", [tuple(a), tuple(mid), tuple(b)], GOLD, 0.014, root)

# --- neck and capital ring: the bud's hinges stand on it ------------------------
cyl("neck", 0.21, NECK_Z1 - OB_Z1 + 0.01, (0, 0, (OB_Z1 + NECK_Z1) / 2), BRONZE, root, verts=40)
ring_pts = lambda r: [(r * math.cos(TAU * i / 64), r * math.sin(TAU * i / 64)) for i in range(64)]
cap = mesh_obj("capital", ring_mesh(ring_pts(CAP_R), ring_pts(BORE_R), NECK_Z1, Z_H), GOLD, root,
               smooth=True, bevel=0.008)
curve_obj("capital_lip", [(CAP_R * math.cos(TAU * i / 64), CAP_R * math.sin(TAU * i / 64),
                           Z_H - 0.005) for i in range(64)], GOLD, 0.02, root, closed=True)
curve_obj("capital_skirt", [(0.235 * math.cos(TAU * i / 64), 0.235 * math.sin(TAU * i / 64),
                             NECK_Z1 - 0.005) for i in range(64)], GOLD, 0.022, root, closed=True)
BORE_FLOOR = 0.77
cyl("bore_floor", BORE_R, 0.01, (0, 0, BORE_FLOOR), BRONZE, root, verts=40)
for k in range(6):       # rubies between the hinges
    a = TAU * k / 6
    sphere(f"capital_ruby{k}", 0.022, (0.245 * math.cos(a), 0.245 * math.sin(a), Z_H + 0.005),
           RUBY, root)

# ----------------------------------------------------------------------------
# Crown mechanism
# ----------------------------------------------------------------------------
#
# Six petals are hinged on the capital (axis tangent to the hinge circle).
# Each has a short tail lever pointing inwards under the hinge with a roller on
# its tip; the lift carriage in the bore rises under the rollers and rolls the
# petals open. The carriage height is solved from the petal angle so roller
# and carriage always touch. The crystal rests in the carriage's claws while
# folded and levitates out once the bud is open; its gimbal rings swing out
# from flat (stowed inside the bud) to their working tilts.

N_PET = 6
PET_L = 0.36                 # petal length (closed: height of the bud above the hinge)
PHI = math.radians(31)       # half the petal's arc; > 30 so closed petals overlap
TAIL, ROLL_R = 0.075, 0.016  # tail lever length, roller radius
THETA_MAX = math.radians(70)


def bud_r(s):
    """Radius of the closed bud at fraction s of the petal length: an onion
    dome bulging out of the hinge circle and closing to a point."""
    return R_H * (1 + 0.35 * math.sin(math.pi * s * 0.8)) * (1 - s ** 1.8)


S_TIP = 0.95


def petal_mesh():
    """Petal surface in its hinge frame (x radial out, y along the hinge, z up):
    a slice of the bud's surface of revolution."""
    ns, nt = 14, 8
    bm = bmesh.new()
    grid = []
    for i in range(ns + 1):
        s = S_TIP * i / ns
        row = []
        for j in range(nt + 1):
            ph = PHI * (2 * j / nt - 1)
            r = bud_r(s)
            row.append(bm.verts.new((r * math.cos(ph) - R_H, r * math.sin(ph), s * PET_L)))
        grid.append(row)
    for i in range(ns):
        for j in range(nt):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # make normals face outward (+x side of the bud)
    if bm.faces[len(bm.faces) // 2].normal.x < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def petal_point(s, ph, lift=0.0):
    r = bud_r(s) + lift
    return (r * math.cos(ph) - R_H, r * math.sin(ph), s * PET_L)


HINGES = []
TIP_LOCAL = Vector(petal_point(S_TIP - 0.04, 0.0, 0.02))
for k in range(N_PET):
    a = math.radians(-90) + TAU * k / N_PET      # one petal faces the camera
    h = bpy.data.objects.new(f"hinge{k}", None)
    link(h, root)
    h.location = (R_H * math.cos(a), R_H * math.sin(a), Z_H)
    h.rotation_mode = "XYZ"
    pet = mesh_obj(f"petal{k}", petal_mesh(), PURPLE, h, smooth=True)
    pet.data.materials.append(GOLD)              # gilded edges
    sol = pet.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.014
    sol.offset = -1
    sol.material_offset_rim = 1
    # inside: a glowing vein down the middle (it feeds the crystal - the motes
    # run along it) between raised gold scrolls, so the open flower is not
    # bare gold
    IN = -0.02
    glow(curve_obj(f"petal{k}_vein", [petal_point(S_TIP * i / 12, 0.0, IN) for i in range(1, 11)],
                   RUNE, 0.012, h))
    for sgn in (-1, 1):
        curl = fit(scroll_c(0, 0, 1), 0.1, 0.12, 0.62, 0.8, flip_x=(sgn > 0))
        curve_obj(f"petal{k}_iscroll{sgn}", [petal_point(v * S_TIP, sgn * PHI * (0.18 + 0.72 * u),
                                                         IN) for u, v in curl], GOLD, 0.012, h)
    # heavy gold edging and midrib on the outside, ruby at the tip
    edge = ([petal_point(S_TIP * i / 12, -PHI, 0.006) for i in range(13)]
            + [petal_point(S_TIP * (12 - i) / 12, PHI, 0.006) for i in range(13)])
    curve_obj(f"petal{k}_edge", edge, GOLD, 0.016, h)
    curve_obj(f"petal{k}_rib", [petal_point(S_TIP * i / 12, 0.0, 0.012) for i in range(1, 12)],
              GOLD, 0.017, h)
    for sgn in (-1, 1):  # a scroll on each half of the petal
        curl = fit(scroll_c(0, 0, 1), 0.12, 0.25, 0.6, 0.85, flip_x=(sgn > 0))
        curve_obj(f"petal{k}_scroll{sgn}", [petal_point(v * S_TIP, sgn * PHI * (0.15 + 0.7 * u),
                                                        0.01) for u, v in curl], GOLD, 0.011, h)
    sphere(f"petal{k}_ruby", 0.026, tuple(TIP_LOCAL), RUBY, h, segs=16)
    # hinge knuckle and the tail lever with its roller
    cyl(f"petal{k}_knuckle", 0.02, 0.07, (0, 0, 0), BRASS, h, rot=(math.radians(90), 0, 0),
        verts=16)
    box(f"petal{k}_tail", (TAIL, 0.03, 0.018), (-TAIL / 2, 0, 0), BRASS, h, bevel=0.004)
    cyl(f"petal{k}_roller", ROLL_R, 0.034, (-TAIL, 0, 0), STEEL, h,
        rot=(math.radians(90), 0, 0), verts=16)
    HINGES.append((h, a))

# lift carriage: gold table with six claws holding the crystal, on a screw
CARR_T = 0.025
CRY_R, CRY_PRISM, CRY_TOP, CRY_BOT = 0.078, 0.1, 0.11, 0.08
carriage = bpy.data.objects.new("carriage", None)
link(carriage, root)
cyl("carriage_table", 0.17, CARR_T, (0, 0, -CARR_T / 2), GOLD, carriage, verts=36)
glow(cyl("carriage_socket", 0.06, 0.012, (0, 0, 0.004), SOCKET, carriage, verts=24))
for k in range(6):
    a = TAU * (k + 0.5) / 6
    claw = [(0.11 * math.cos(a), 0.11 * math.sin(a), 0.0),
            (0.1 * math.cos(a), 0.1 * math.sin(a), 0.05),
            (0.086 * math.cos(a), 0.086 * math.sin(a), 0.09)]
    curve_obj(f"claw{k}", claw, GOLD, 0.011, carriage)
SCREW_L = 0.25
screw = cyl("lift_screw", 0.035, SCREW_L, (0, 0, -SCREW_L / 2 - CARR_T), STEEL, carriage,
            verts=20)
for k in range(5):       # thread crests so the screw reads as a screw
    cyl(f"lift_thread{k}", 0.042, 0.012, (0, 0, -CARR_T - 0.03 - 0.045 * k), STEEL, carriage,
        verts=20)


def carriage_top(theta):
    """Carriage height that keeps the rollers resting on it (roller tip at
    (-TAIL cos t, TAIL sin t) in the hinge frame)."""
    return Z_H + TAIL * math.sin(theta) - ROLL_R


CRY_REST = CRY_BOT + 0.008 + CRY_PRISM / 2   # crystal centre above the carriage table


# --- the focusing crystal and its gimbal rings ---------------------------------
crystal = bpy.data.objects.new("crystal", None)
link(crystal, root)
bm = bmesh.new()
mid_lo = [bm.verts.new((CRY_R * math.cos(TAU * i / 6), CRY_R * math.sin(TAU * i / 6),
                        -CRY_PRISM / 2)) for i in range(6)]
mid_hi = [bm.verts.new((CRY_R * math.cos(TAU * i / 6), CRY_R * math.sin(TAU * i / 6),
                        CRY_PRISM / 2)) for i in range(6)]
top = bm.verts.new((0, 0, CRY_PRISM / 2 + CRY_TOP))
bot = bm.verts.new((0, 0, -CRY_PRISM / 2 - CRY_BOT))
for i in range(6):
    j = (i + 1) % 6
    bm.faces.new((mid_lo[i], mid_lo[j], mid_hi[j], mid_hi[i]))
    bm.faces.new((mid_hi[i], mid_hi[j], top))
    bm.faces.new((mid_lo[j], mid_lo[i], bot))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
cry_o = mesh_obj("crystal_body", bm, CRYSTAL, crystal)
cry_o.data.shade_flat()
glow(cry_o)
cry_light_d = bpy.data.lights.new("crystal_light", "POINT")
cry_light_d.color = (1.0, 0.35, 0.95)
cry_light_d.shadow_soft_size = 0.05
link(bpy.data.objects.new("crystal_light", cry_light_d), crystal)

RING_TILTS = ((math.radians(68), 0.0), (math.radians(-40), math.radians(58)))
RINGS = []
for k, (rr, w) in enumerate(((0.155, 0.022), (0.128, 0.02))):
    holder = bpy.data.objects.new(f"gimbal{k}", None)
    link(holder, crystal)
    holder.rotation_mode = "XYZ"
    ring = mesh_obj(f"ring{k}", ring_mesh(ring_pts(rr), ring_pts(rr - w), -0.011, 0.011), GOLD,
                    holder, smooth=True, bevel=0.004)
    for g in range(4):
        sphere(f"ring{k}_gem{g}", 0.017, ((rr - w / 2) * math.cos(TAU * g / 4),
                                          (rr - w / 2) * math.sin(TAU * g / 4), 0), RUBY, ring)
    RINGS.append((holder, ring))
Z_HOVER = 1.38

# ----------------------------------------------------------------------------
# States
# ----------------------------------------------------------------------------
#
# Every clip starts and ends on poses that the engine's state changes connect:
# preparing ends in prepared frame 0; attacking frame 0 and the end of the
# ending clip are prepared frame 0 again (crystal spin in whole sixths of a
# turn, ring spin in whole quarters - the crystal is hexagonal, the rings carry
# four gems). Loops close on themselves.

SPIN6, SPIN4 = TAU / 6, TAU / 4


class Pose:
    theta = 0.0          # petal opening
    lift = 0.0           # 0 = crystal in the claws, 1 = hovering
    bob = 0.0
    spin = 0.0           # crystal spin
    ring_spin = 0.0
    glow = 0.1           # 1 = awake
    arcs = 0             # lightning arcs to the petal tips
    motes = None         # phase of the motes (None = no motes)
    seed = 0


def state_pose(state, i, n):
    p = Pose()
    p.seed = zlib.crc32(f"{state}{i}".encode())
    if state == "preparing":
        u = i / (n - 1)
        p.theta = THETA_MAX * smooth(u / 0.55)
        p.lift = smooth((u - 0.3) / 0.7)
        p.spin = SPIN6 * p.lift
        p.ring_spin = SPIN4 * p.lift
        p.glow = 0.1 + 0.9 * smooth(u)
        if p.lift > 0.6:
            p.motes = 0.0
    elif state == "prepared":
        q = i / n
        p.theta, p.lift = THETA_MAX, 1.0
        p.bob = 0.022 * math.sin(TAU * q)
        p.spin = SPIN6 * q
        p.ring_spin = SPIN4 * q
        p.glow = 1.0 + 0.3 * math.sin(TAU * q)     # brightest at the top of the bob
        p.motes = q
    elif state == "attacking":
        q = i / n
        p.theta, p.lift = THETA_MAX, 1.0
        p.bob = 0.006 * math.sin(TAU * q * 4)      # humming with charge
        p.spin = 4 * SPIN6 * q                      # 15 deg per frame
        p.ring_spin = 4 * SPIN4 * q                 # 22.5 deg per frame
        p.glow = 3.2 + 0.6 * random.Random(p.seed).random()
        p.arcs = 3
        p.motes = (2 * q) % 1.0
    elif state == "ending":
        # decelerate from attack speed with constant deceleration: 2t - t^2
        # starts at the attack rate and stops after exactly 1/6 and 1/4 turn
        t = (i + 1) / n
        e = 2 * t - t * t
        p.theta, p.lift = THETA_MAX, 1.0
        p.spin = SPIN6 * e
        p.ring_spin = SPIN4 * e
        p.glow = 1.0 + 2.4 * (1 - e)
        p.arcs = 2 if i < 2 else (1 if i < 4 else 0)
        p.motes = 0.0
    return p


ARCS, MOTES = [], []


def clear(lst):
    for o in lst:
        bpy.data.objects.remove(o, do_unlink=True)
    lst.clear()


def tip_world(k, theta):
    h, a = HINGES[k]
    m = Matrix.Translation(h.location) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(theta, 4, "Y")
    return m @ TIP_LOCAL


def apply(p):
    for h, a in HINGES:
        h.rotation_euler = (0, p.theta, a)
    ct = carriage_top(p.theta)
    carriage.location = (0, 0, ct)
    rest = ct + CRY_REST
    cz = rest + p.lift * (Z_HOVER - rest) + p.bob
    crystal.location = (0, 0, cz)
    crystal.rotation_euler = (0, 0, p.spin)
    for k, (holder, ring) in enumerate(RINGS):
        tx, ty = RING_TILTS[k]
        sw = smooth(p.lift)
        holder.rotation_euler = (tx * sw, ty * sw, -p.spin)    # rings don't share the spin
        ring.rotation_euler = (0, 0, (1 if k == 0 else -1) * p.ring_spin)

    CRYSTAL_EM.default_value = 0.15 + 1.1 * p.glow
    RUNE_EM.default_value = 0.08 + 0.55 * p.glow
    SOCKET_EM.default_value = 0.2 + 0.8 * p.glow
    cry_light_d.energy = 0.0 if p.glow < 0.2 else 0.25 * p.glow
    ARC_EM.default_value = 5.0

    clear(ARCS)
    rng = random.Random(p.seed)
    centre = Vector((0, 0, cz))
    for n in range(p.arcs):
        k = rng.randrange(N_PET)
        end = tip_world(k, p.theta)
        d = end - centre
        start = centre + d.normalized() * CRY_R
        side = d.cross(Vector((0, 0, 1))).normalized()
        pts = []
        for s in range(9):
            t = s / 8
            q = start.lerp(end, t)
            if 0 < s < 8:
                q += side * rng.uniform(-0.04, 0.04) + Vector((0, 0, rng.uniform(-0.03, 0.03)))
            pts.append(tuple(q))
        ARCS.append(glow(curve_obj(f"arc{n}", pts, ARC, 0.0065, root)))

    clear(MOTES)
    if p.motes is not None:
        # one mote per petal drifts from the tip ruby into the crystal; each
        # starts a sixth of a lap after its neighbour, one lap per loop
        for k in range(N_PET):
            t = (p.motes + k / N_PET) % 1.0
            a0 = tip_world(k, THETA_MAX)
            b = centre
            c = a0.lerp(b, 0.5) + Vector((0, 0, 0.12))
            q = (1 - t) ** 2 * a0 + 2 * (1 - t) * t * c + t * t * b
            r = 0.021 * math.sin(math.pi * t) ** 0.5
            if r > 0.004:
                MOTES.append(glow(sphere(f"mote{k}", r, tuple(q), MOTE, root, segs=8)))


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

rig = setup_scene(MAIN_BOX["w"], MAIN_BOX["h"], MAIN_BOX["cy"])
cam = bpy.context.scene.camera


def frame_box(b):
    """Point the Factorio camera at a box (tiles, screen coords from the origin)."""
    scene = bpy.context.scene
    ppt = args.px_per_tile
    cam.data.ortho_scale = max(b["w"], b["h"])
    scene.render.resolution_x = round(b["w"] * ppt)
    scene.render.resolution_y = round(b["h"] * ppt)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    cam.location = Vector((b["cx"], 0, b["cy"] * math.sqrt(2))) - look * 30


TIMELINE = [(s, i, n) for s, n in SEGMENTS for i in range(n)]
frames = [int(f) for f in args.frame.split(",")] if args.preview else range(len(TIMELINE))
scene = bpy.context.scene
lights = (rig.sun_d, rig.fill_d, cry_light_d)
meshes = [o for o in scene.objects if o.type in ("MESH", "CURVE")]
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
