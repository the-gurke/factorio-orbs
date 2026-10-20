"""
Procedural Blender model + Factorio render of the rune altar.

The altar is a container: players drop six rune words into it in the order
Vitae, Ignis, Tempus, Terra, Umbra, Mortis and control.lua turns them into a
rune research pack. The model tells that story at a glance:

  * a stepped stone and purple-panelled plinth (2x2 footprint, short stair
    at the front, like a temple altar),
  * a round dais carrying six gold sockets, each holding a lettered stone
    tablet in the colours of the rune items: V I T R U M - read left to
    right around the ring, the six runes spell VITRUM ("glass"),
  * glowing channels run from each socket into the central gold chalice,
    where a magenta crystal - the research pack being formed - hovers,
  * a tall arched reredos at the back (tall parts at the back, like vanilla),
    candelabras at the back corners and braziers of purple fire at the front.

Containers only take a static `picture` (a Sprite), so this renders a single
frame: main + glow (draw_as_light) + shadow.

    blender -b --factory-startup -P blender/rune_altar.py -- \
        --out graphics/generated/rune-altar [--preview --frame 0]

Shared helpers live in blender/fblend.py; stitch with blender/stitch.py.
World units are Factorio tiles, the entity is 2x2 centred on the origin, +y
is north, +z is up.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("rune-altar", frames=1, samples=256)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

N = fblend.N


def stone(name, base, dark, bump=0.5, scale=14.0):
    """Weathered carved stone: mottled, chipped edges, grime in the crevices."""
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Metallic"].default_value = 0.0
    grime(nt, bsdf, base, dark, noise_scale=scale, rough=(0.6, 0.9), bump=bump,
          bump_scale=40.0, dirt=0.35, wear=tuple(min(1.0, c * 1.5) for c in base))
    return m


def flagstones(name, base, mortar):
    """Deck paving: irregular brick courses of stone with dark joints."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = 5.0
    brick.inputs["Mortar Size"].default_value = 0.025
    brick.inputs["Brick Width"].default_value = 0.9
    brick.inputs["Row Height"].default_value = 0.45
    brick.inputs["Color1"].default_value = (*base, 1)
    brick.inputs["Color2"].default_value = tuple(c * 0.75 for c in base) + (1,)
    brick.inputs["Mortar"].default_value = (*mortar, 1)
    L(tc.outputs["Object"], brick.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 22.0
    noise.inputs["Detail"].default_value = 8.0
    L(tc.outputs["Object"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.55
    L(brick.outputs["Color"], mix.inputs["A"])
    L(noise.outputs["Color"], mix.inputs["B"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.12
    L(mix.outputs["Result"], ao.inputs["Color"])
    L(ao.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.6
    b.inputs["Distance"].default_value = 0.02
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L(brick.outputs["Fac"], inv.inputs[1])
    L(inv.outputs[0], b.inputs["Height"])
    L(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


STONE = stone("stone", (0.36, 0.31, 0.26), (0.05, 0.04, 0.035))
DARK_STONE = stone("dark_stone", (0.16, 0.12, 0.13), (0.02, 0.015, 0.02))
PAVING = flagstones("paving", (0.24, 0.17, 0.17), (0.03, 0.015, 0.02))
WAX = paint("wax", (0.8, 0.72, 0.55), (0.35, 0.28, 0.2), bump=0.1)
FLAME, FLAME_EM = emitter("flame", (1.0, 0.5, 0.12), 2.5)
PFIRE, PFIRE_EM = emitter("purple_fire", (0.8, 0.15, 1.0), 2.2)
COALS, _ = emitter("coals", (0.9, 0.2, 0.6), 1.2, base=(0.1, 0.02, 0.06))
CRYSTAL, CRYSTAL_EM = emitter("crystal", (0.9, 0.15, 0.8), 0.9, base=(0.6, 0.1, 0.55), glass=True)
CHALICE_LIQ, _ = emitter("chalice_liquid", (0.8, 0.1, 0.65), 0.35, base=(0.12, 0.01, 0.1))
CHANNEL, _ = emitter("channel", (0.85, 0.3, 1.0), 0.9, base=(0.1, 0.02, 0.1))

# Rune tablets follow the rune item icons (graphics/rune-word-*.png): letter,
# tablet stone and letter glow colour.
RUNE_WORDS = (
    ("vitae", "V", (0.20, 0.27, 0.10), (0.35, 0.95, 0.15)),
    ("ignis", "I", (0.13, 0.07, 0.05), (1.0, 0.42, 0.06)),
    ("tempus", "T", (0.24, 0.17, 0.25), (1.0, 0.3, 0.95)),
    ("terra", "R", (0.27, 0.20, 0.12), (0.95, 0.6, 0.2)),
    ("umbra", "U", (0.55, 0.52, 0.46), (0.75, 0.75, 1.0)),
    ("mortis", "M", (0.10, 0.07, 0.14), (0.6, 0.3, 1.0)),
)

# Chunky capital strokes in a unit square (v = 0 at the bottom).
LETTERS = {
    "V": [[(0.12, 0.95), (0.5, 0.05), (0.88, 0.95)]],
    "I": [[(0.5, 0.08), (0.5, 0.92)], [(0.25, 0.92), (0.75, 0.92)], [(0.25, 0.08), (0.75, 0.08)]],
    "T": [[(0.1, 0.92), (0.9, 0.92)], [(0.5, 0.92), (0.5, 0.05)]],
    "R": [[(0.22, 0.05), (0.22, 0.95), (0.62, 0.95), (0.8, 0.85), (0.8, 0.62), (0.62, 0.52),
           (0.22, 0.52)], [(0.5, 0.52), (0.82, 0.05)]],
    "U": [[(0.18, 0.95), (0.18, 0.35)] + [(0.5 - 0.32 * math.cos(math.pi * t / 8),
                                           0.35 - 0.3 * math.sin(math.pi * t / 8))
                                          for t in range(9)] + [(0.82, 0.95)]],
    "M": [[(0.1, 0.05), (0.13, 0.95), (0.5, 0.38), (0.87, 0.95), (0.9, 0.05)]],
}

root = bpy.data.objects.new("rune_altar", None)
link(root)
LIGHTS = []


def point_light(name, loc, color, energy, size=0.05):
    d = bpy.data.lights.new(name, "POINT")
    d.color = color
    d.energy = energy
    d.shadow_soft_size = size
    o = bpy.data.objects.new(name, d)
    link(o, root)
    o.location = loc
    LIGHTS.append(d)
    return d


def rail(name, pts3, r, closed=False, mat=None):
    return curve_obj(name, [tuple(p) for p in pts3], mat or GOLD, r, root, closed=closed)


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


def octagon(h, c):
    """Square of half size h with chamfered corners, CCW from the front edge."""
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h),
            (-h, h - c), (-h, -h + c)]


def circle(r, n=64, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(TAU * i / n), cy + r * math.sin(TAU * i / n)) for i in range(n)]


FIL_R = 0.03         # raised scrollwork (smaller than the 3x3 machine's, same look)

# ----------------------------------------------------------------------------
# Plinth: a stone footing step, then sloped purple walls (read as wings)
# ----------------------------------------------------------------------------
STEP_H, STEP_HALF, STEP_CH = 0.08, 0.99, 0.22
WALL_B, WALL_T, WALL_CH = 0.95, 0.74, 0.2       # wall outline half sizes bottom / top
DECK_Z = 0.44

foot = octagon(STEP_HALF, STEP_CH)
prism("footing", foot, 0, STEP_H, STONE, bevel=0.015)
rail("footing_rail", [(x * 0.995, y * 0.995, STEP_H) for x, y in foot], 0.03, closed=True)
for k, (x, y) in enumerate(foot):   # gold corner shoes on the footing
    sphere(f"foot_boss{k}", 0.035, (x * 0.99, y * 0.99, STEP_H * 0.55), GOLD, root)

bot2d = octagon(WALL_B, WALL_CH + 0.02)
top2d = octagon(WALL_T, WALL_CH)
B3 = [Vector((x, y, STEP_H)) for x, y in bot2d]
T3 = [Vector((x, y, DECK_Z)) for x, y in top2d]
walls = {}
for i in range(8):
    j = (i + 1) % 8
    p = Panel(B3[i], B3[j], T3[j], T3[i])
    p.build(f"wall{i}", PURPLE, parent=root)
    walls[i] = p
for i in range(8):   # thick gold ribs on every corner
    rail(f"corner_rib{i}", [B3[i] + Vector((0, 0, 0.01)), T3[i]], 0.05)
rail("wall_foot_rail", [b + Vector((0, 0, 0.015)) for b in B3], 0.035, closed=True)

# front wall: stair in the middle, framed scroll panels left and right of it
STAIR_W = 0.42
front = walls[0]
su0 = 0.5 - STAIR_W / (2 * (2 * (WALL_B - WALL_CH - 0.02)))
for k, (u0, u1, mirror) in enumerate(((0.03, su0 - 0.03, False), (1 - su0 + 0.03, 0.97, True))):
    sp = sub_panel(front, u0, u1, 0.12, 0.9)
    gold_frame(sp, f"front{k}_frame", 0.026, parent=root)
    inner = sub_panel(sp, 0.08, 0.92, 0.1, 0.9)
    inner.filigree(f"front{k}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.62, 1.0, flip_x=mirror),
                                     fit(scroll_c(0, 0, 1, up=False), 0.55, 0.05, 1.0, 0.6,
                                         flip_x=not mirror)],
                   radius=FIL_R, parent=root)
    inner.studs(f"front{k}_gem", [(0.85 if not mirror else 0.15, 0.82)], r=0.03, mat=RUBY,
                parent=root)
# the stair: three stone steps climbing to the deck, gold nosings
STAIR_Y0 = -STEP_HALF - 0.02
for k in range(3):
    z1 = STEP_H + (k + 1) * (DECK_Z - STEP_H) / 3
    y_front = STAIR_Y0 + k * 0.07
    y_back = -WALL_T + 0.04
    box(f"stair{k}", (STAIR_W - k * 0.02, y_back - y_front, z1 - (STEP_H - 0.02)),
        (0, (y_front + y_back) / 2, (z1 + STEP_H - 0.02) / 2), STONE, root, bevel=0.012)
    rail(f"stair_nose{k}", [(-(STAIR_W - k * 0.02) / 2, y_front + 0.005, z1),
                            ((STAIR_W - k * 0.02) / 2, y_front + 0.005, z1)], 0.018)
for sx in (-1, 1):   # stair cheeks with ruby-topped newel posts
    box(f"stair_cheek{sx}", (0.06, -WALL_T - STAIR_Y0, DECK_Z - STEP_H + 0.06),
        (sx * (STAIR_W / 2 + 0.03), (STAIR_Y0 - WALL_T) / 2 + 0.02, (DECK_Z + STEP_H) / 2 + 0.03),
        STONE, root, bevel=0.012)
    cyl(f"newel{sx}", 0.045, 0.12, (sx * (STAIR_W / 2 + 0.03), STAIR_Y0 + 0.06, DECK_Z + 0.08),
        GOLD, root, verts=16)
    sphere(f"newel_gem{sx}", 0.04, (sx * (STAIR_W / 2 + 0.03), STAIR_Y0 + 0.06, DECK_Z + 0.16),
           RUBY, root)

# front chamfers and the sloped side wings: framed panels, glowing rune glyphs
for i in (7, 1):
    sp = sub_panel(walls[i], 0.12, 0.88, 0.12, 0.88)
    sp.filigree(f"ch{i}_fil", [fit(scroll_c(0, 0, 1), 0.05, 0.05, 0.95, 0.95, flip_x=(i == 1))],
                radius=FIL_R, parent=root)
for i in (2, 6):
    w = walls[i]
    # u runs front->back on the east wall and back->front on the west one
    segs = ((0.0, 0.34), (0.34, 0.66), (0.66, 1.0))
    for k, (u0, u1) in enumerate(segs):
        sp = sub_panel(w, u0 + 0.03, u1 - 0.03, 0.12, 0.88)
        gold_frame(sp, f"side{i}_{k}_frame", 0.026, parent=root)
        inner = sub_panel(sp, 0.1, 0.9, 0.1, 0.9)
        if k == 1:   # rune cartouche between two scroll panels
            rune(inner, f"side{i}_rune", glyph=i // 2, radius=0.014, parent=root)
            inner.studs(f"side{i}_gem", [(0.5, -0.05), (0.5, 1.05)], r=0.022, mat=RUBY,
                        parent=root)
        else:
            inner.filigree(f"side{i}_{k}_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 1.0, 1.0,
                                                    flip_x=(k == 2))],
                           radius=FIL_R * 0.9, parent=root)
            inner.studs(f"side{i}_{k}_gem", [(0.5, 0.5)], r=0.024, mat=RUBY, parent=root)
    for k, u in enumerate((0.34, 0.66)):
        rail(f"side{i}_rib{k}", [Vector(w.at(u, 0, 0.02)), Vector(w.at(u, 1, 0.02))], 0.036)

# ----------------------------------------------------------------------------
# Deck: paving, a heavy studded gold coping, the round dais
# ----------------------------------------------------------------------------
prism("deck", top2d, DECK_Z - 0.04, DECK_Z, PAVING, bevel=0.0)
coping = [Vector((x, y, DECK_Z + 0.02)) for x, y in top2d]
rail("coping", coping, 0.05, closed=True)
for i in range(8):
    a, b = coping[i], coping[(i + 1) % 8]
    n = max(1, int((b - a).length / 0.2))
    for k in range(1, n):
        p = a.lerp(b, k / n) + Vector((0, 0, 0.035))
        sphere(f"coping_stud{i}_{k}", 0.026, tuple(p), RUBY if k % 2 else GOLD, root)

DAIS_R, DAIS_Z = 0.62, DECK_Z + 0.09
d = cyl("dais", DAIS_R, DAIS_Z - DECK_Z, (0, 0, (DAIS_Z + DECK_Z) / 2), DARK_STONE, root,
        verts=96, bevel=0.01)
rail("dais_rim", [(x, y, DAIS_Z) for x, y in circle(DAIS_R, 96)], 0.032, closed=True)
rail("dais_foot", [(x, y, DECK_Z + 0.01) for x, y in circle(DAIS_R + 0.01, 96)], 0.022,
     closed=True)
# a glowing groove circle on the dais top joins all six sockets
glow(rail("ring_groove", [(x, y, DAIS_Z + 0.004) for x, y in circle(0.4, 96)], 0.012,
          closed=True, mat=CHANNEL))
rail("ring_groove_lip", [(x, y, DAIS_Z + 0.004) for x, y in circle(0.43, 96)], 0.012,
     closed=True)

# ----------------------------------------------------------------------------
# Rune sockets: six gold cups with lettered tablets, VITRUM left to right
# ----------------------------------------------------------------------------
# Sockets sit on a ring; the order runs clockwise seen from above starting at
# the west, so on screen the letters read V I T (rising over the back) R U M
# (coming round the front). Tablets all face the camera so the letters read;
# back ones stand tall, front ones are low so they don't hide the chalice.
SOCKET_R = 0.47
SOCKET_ANG = [math.radians(a) for a in (180, 130, 50, 0, -55, -125)]
TAB_W, TAB_D = 0.2, 0.06


def tablet_height(a):
    return 0.24 + 0.07 * math.sin(a)         # 0.31 at the back, 0.17 at the front


for k, ((word, letter, tab_col, glow_col), a) in enumerate(zip(RUNE_WORDS, SOCKET_ANG)):
    cx, cy = SOCKET_R * math.cos(a), SOCKET_R * math.sin(a)
    # gold socket cup with a ruby on its front
    cyl(f"socket{k}", 0.125, 0.05, (cx, cy, DAIS_Z + 0.025), GOLD, root, verts=32, r2=0.105)
    rail(f"socket{k}_lip", [(cx + x, cy + y, DAIS_Z + 0.05) for x, y in circle(0.108, 32)],
         0.016, closed=True)
    sphere(f"socket{k}_gem", 0.022, (cx, cy - 0.122, DAIS_Z + 0.028), RUBY, root)
    # glowing channel from the socket into the chalice
    glow(rail(f"channel{k}", [(cx * 0.82, cy * 0.82, DAIS_Z + 0.004),
                              (cx * 0.36, cy * 0.36, DAIS_Z + 0.004)], 0.012, mat=CHANNEL))
    # tablet leaning back in the cup
    h = tablet_height(a)
    tilt = math.radians(-14)
    M = Matrix.Translation((cx, cy + 0.01, DAIS_Z + 0.03)) @ Matrix.Rotation(tilt, 4, "X")
    tab_mat = stone(f"tablet_{word}", tab_col, tuple(c * 0.25 for c in tab_col), bump=0.35)
    box(f"tablet{k}", (TAB_W, TAB_D, h), M @ Vector((0, 0, h / 2)), tab_mat, root,
        rot=(tilt, 0, 0), bevel=0.012)
    box(f"tablet{k}_cap", (TAB_W + 0.03, TAB_D + 0.03, 0.03), M @ Vector((0, 0, h + 0.01)),
        GOLD, root, rot=(tilt, 0, 0), bevel=0.008)
    sphere(f"tablet{k}_finial", 0.026, tuple(M @ Vector((0, 0, h + 0.045))), GOLD, root)
    face = Panel(M @ Vector((-TAB_W / 2, -TAB_D / 2, 0.0)), M @ Vector((TAB_W / 2, -TAB_D / 2, 0.0)),
                 M @ Vector((TAB_W / 2, -TAB_D / 2, h)), M @ Vector((-TAB_W / 2, -TAB_D / 2, h)))
    gold_frame(sub_panel(face, 0.06, 0.94, 0.05, 0.95), f"tablet{k}_frame", 0.012, parent=root)
    em, _ = emitter(f"letter_{word}", glow_col, 1.1, base=tuple(c * 0.4 for c in glow_col))
    # letters keep their aspect: tall tablets get a tall letter, short ones a square one
    lh = min(0.8, 0.7 * TAB_W / h * 1.25)
    for si, stroke in enumerate(LETTERS[letter]):
        glow(curve_obj(f"tablet{k}_letter{si}",
                       [face.at(0.22 + 0.56 * u, 0.5 - lh / 2 + lh * v, 0.008) for u, v in stroke],
                       em, 0.016 if h > 0.15 else 0.013, root))

# ----------------------------------------------------------------------------
# Chalice and the forming research pack (a hovering crystal)
# ----------------------------------------------------------------------------
CH_Z = DAIS_Z + 0.22                       # chalice rim height
cyl("chalice_foot", 0.15, 0.04, (0, 0, DAIS_Z + 0.02), GOLD, root, verts=48, r2=0.1)
cyl("chalice_stem", 0.045, CH_Z - DAIS_Z - 0.08, (0, 0, (CH_Z + DAIS_Z) / 2 - 0.03), GOLD, root,
    verts=24)
sphere("chalice_knop", 0.06, (0, 0, DAIS_Z + 0.1), GOLD, root, segs=24)
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.17)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.001], context="VERTS")
bowl = mesh_obj("chalice_bowl", bm, GOLD, root, smooth=True)
bowl.location = (0, 0, CH_Z)
bowl.scale = (1, 1, 0.7)
bowl.modifiers.new("solid", "SOLIDIFY").thickness = 0.02
rail("chalice_lip", [(x, y, CH_Z) for x, y in circle(0.17, 48)], 0.022, closed=True)
for k in range(6):    # rubies round the bowl, one per rune
    a = SOCKET_ANG[k]
    sphere(f"chalice_gem{k}", 0.022, (0.15 * math.cos(a), 0.15 * math.sin(a), CH_Z - 0.06), RUBY,
           root)
glow(cyl("chalice_liquid", 0.155, 0.01, (0, 0, CH_Z - 0.025), CHALICE_LIQ, root, verts=48))
# dark brew with a bright swirl drawn into the crystal
CHALICE_LIQ.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
for k in range(2):
    sw = spiral(0, 0, 0.13, 0.8, math.pi * k, cw=True, n=30, shrink=0.15)
    glow(rail(f"chalice_swirl{k}", [(x, y, CH_Z - 0.018) for x, y in sw], 0.008, mat=CHANNEL))

CRYSTAL_C = Vector((0, 0, CH_Z + 0.24))
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.085, radius2=0.0, depth=0.2)
bmesh.ops.translate(bm, vec=(0, 0, 0.1), verts=bm.verts)
bm2 = bmesh.new()
bmesh.ops.create_cone(bm2, cap_ends=True, segments=6, radius1=0.0, radius2=0.085, depth=0.13)
bmesh.ops.translate(bm2, vec=(0, 0, -0.065), verts=bm2.verts)
up = mesh_obj("crystal_top", bm, CRYSTAL, root)
dn = mesh_obj("crystal_bottom", bm2, CRYSTAL, root)
for o in (up, dn):
    o.location = CRYSTAL_C
    o.rotation_euler = (0, 0, 0.3)
    o.data.shade_flat()
    glow(o)
# gold claws curling up from the lip to cradle the crystal without touching it
for k in range(3):
    a = TAU * k / 3 + math.pi / 2
    pts = []
    for i in range(9):
        t = i / 8
        r = 0.17 - 0.07 * t + 0.03 * math.sin(math.pi * t)
        pts.append((r * math.cos(a), r * math.sin(a), CH_Z + 0.33 * t))
    curl = (0.085 * math.cos(a), 0.085 * math.sin(a), CH_Z + 0.36)
    rail(f"claw{k}", pts + [curl], 0.017)
    sphere(f"claw_tip{k}", 0.022, curl, RUBY, root)
# small shards orbiting the crystal: the pack is still condensing
for k in range(3):
    a = TAU * k / 3 + 1.0
    s = sphere(f"mote{k}", 0.018, tuple(CRYSTAL_C + Vector((0.16 * math.cos(a), 0.16 * math.sin(a),
                                                           0.04 * math.sin(2 * a)))), CRYSTAL, root)
    glow(s)
point_light("crystal_light", CRYSTAL_C + Vector((0, -0.12, 0.16)), (1.0, 0.35, 0.9), 4.0)
point_light("chalice_light", (0, 0, CH_Z + 0.02), (1.0, 0.3, 0.85), 0.5)

# ----------------------------------------------------------------------------
# Reredos: tall arched panel at the back framing the ritual
# ----------------------------------------------------------------------------
ARCH_Y, ARCH_T = 0.66, 0.1
ARCH_W, ARCH_Z0, ARCH_SPRING, ARCH_TOP = 0.5, DECK_Z, 0.98, 1.6


def arch_outline(w, z0, zs, zt, n=20):
    """Pointed (two-centred gothic) arch in the xz plane: each flank is an arc
    centred on the opposite side's springing line, meeting at the apex."""
    h = zt - zs
    R = (h * h + w * w) / (2 * w)          # arc through (w, zs) and (0, zt), centre (w - R, zs)
    a_top = math.atan2(h, R - w)
    right = [((w - R) + R * math.cos(a_top * i / n), zs + R * math.sin(a_top * i / n))
             for i in range(n + 1)]
    pts = [(-w, z0), (w, z0)] + right[:-1] + [(0.0, zt)]
    pts += [(-x, z) for x, z in reversed(right[:-1])]
    return pts


outline = arch_outline(ARCH_W, ARCH_Z0, ARCH_SPRING, ARCH_TOP)
bm = bmesh.new()
fr = [bm.verts.new((x, ARCH_Y - ARCH_T / 2, z)) for x, z in outline]
bk = [bm.verts.new((x, ARCH_Y + ARCH_T / 2, z)) for x, z in outline]
bm.faces.new(fr)
bm.faces.new(list(reversed(bk)))
for i in range(len(outline)):
    j = (i + 1) % len(outline)
    bm.faces.new((fr[i], bk[i], bk[j], fr[j]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
arch = mesh_obj("reredos", bm, PURPLE, root, bevel=0.012)
arch.data.shade_flat()
FY = ARCH_Y - ARCH_T / 2 - 0.005           # front face
rail("reredos_frame", [(x * 0.97, FY, ARCH_Z0 + (z - ARCH_Z0) * 0.985 + 0.01)
                       for x, z in outline[1:]], 0.045, closed=False)
rail("reredos_frame_l", [(-ARCH_W * 0.97, FY, ARCH_Z0 + 0.04), (-ARCH_W * 0.97, FY, ARCH_SPRING)],
     0.045)
# rune wheel: a gold ring with the six rune glyph inlays round a ruby boss
WHEEL_C = Vector((0, FY - 0.02, 1.13))
WHEEL_R = 0.28
rail("wheel_ring", [(WHEEL_C.x + WHEEL_R * math.cos(t), WHEEL_C.y, WHEEL_C.z + WHEEL_R * math.sin(t))
                    for t in (TAU * i / 64 for i in range(64))], 0.035, closed=True)
for k in range(6):
    a = TAU * k / 6 + math.pi / 2
    # spoke between two glyphs, glyph between two spokes
    rail(f"wheel_spoke{k}", [WHEEL_C + Vector((0.07 * math.cos(a + TAU / 12), 0, 0.07 * math.sin(a + TAU / 12))),
                             WHEEL_C + Vector((WHEEL_R * math.cos(a + TAU / 12), 0,
                                               WHEEL_R * math.sin(a + TAU / 12)))], 0.016)
    c = WHEEL_C + Vector((WHEEL_R * 0.62 * math.cos(a), 0, WHEEL_R * 0.62 * math.sin(a)))
    s_ = 0.07
    p = Panel((c.x - s_, c.y, c.z - s_), (c.x + s_, c.y, c.z - s_), (c.x + s_, c.y, c.z + s_),
              (c.x - s_, c.y, c.z + s_))
    rune(p, f"wheel_rune{k}", glyph=k, radius=0.012, parent=root)
    b = WHEEL_C + Vector((WHEEL_R * math.cos(a + TAU / 12), -0.03, WHEEL_R * math.sin(a + TAU / 12)))
    sphere(f"wheel_stud{k}", 0.026, tuple(b), RUBY if k % 2 else GOLD, root)
sphere("wheel_boss", 0.06, tuple(WHEEL_C + Vector((0, -0.02, 0))), RUBY, root, segs=24)
rail("wheel_boss_ring", [(WHEEL_C.x + 0.075 * math.cos(t), WHEEL_C.y - 0.01, WHEEL_C.z + 0.075 * math.sin(t))
                         for t in (TAU * i / 32 for i in range(32))], 0.016, closed=True)
# scrollwork filling the lower panel under the wheel
low = Panel((-ARCH_W * 0.85, FY, ARCH_Z0 + 0.12), (ARCH_W * 0.85, FY, ARCH_Z0 + 0.12),
            (ARCH_W * 0.85, FY, 0.78), (-ARCH_W * 0.85, FY, 0.78))
low.filigree("reredos_fil", [fit(scroll_c(0, 0, 1), 0.0, 0.0, 0.45, 1.0),
                              fit(scroll_c(0, 0, 1), 0.55, 0.0, 1.0, 1.0, flip_x=True)],
             radius=FIL_R, lift=0.0, parent=root)
# crest on the apex and pinnacles on the shoulders
sphere("crest_gem", 0.05, (0, FY - 0.01, ARCH_TOP - 0.02), RUBY, root, segs=20)
rail("crest_curl_l", [(x, FY, z) for x, z in fit(scroll_c(0, 0, 1), -0.24, ARCH_TOP - 0.16, -0.04,
                                                  ARCH_TOP + 0.06)], 0.03)
rail("crest_curl_r", [(x, FY, z) for x, z in fit(scroll_c(0, 0, 1), 0.04, ARCH_TOP - 0.16, 0.24,
                                                  ARCH_TOP + 0.06, flip_x=True)], 0.03)
for sx in (-1, 1):
    x = sx * (ARCH_W + 0.03)
    box(f"pillar{sx}", (0.13, ARCH_T + 0.06, ARCH_SPRING - ARCH_Z0), (x, ARCH_Y, (ARCH_SPRING + ARCH_Z0) / 2),
        STONE, root, bevel=0.015)
    for zz in (ARCH_Z0 + 0.05, ARCH_SPRING - 0.02):
        box(f"pillar{sx}_band{zz}", (0.16, ARCH_T + 0.09, 0.045), (x, ARCH_Y, zz), GOLD, root,
            bevel=0.01)
    cyl(f"pinnacle{sx}", 0.06, 0.16, (x, ARCH_Y, ARCH_SPRING + 0.08), GOLD, root, verts=8, r2=0.0,
        bevel=0.004)
    rail(f"pillar{sx}_fil", [(x + sx * 0.0 + 0.4 * (u - 0.5) * 0.13, ARCH_Y - ARCH_T / 2 - 0.035, z)
                            for u, z in fit(scroll_c(0, 0, 1), 0.0, ARCH_Z0 + 0.12, 1.0,
                                            ARCH_SPRING - 0.08, flip_x=(sx > 0))], 0.02)

# ----------------------------------------------------------------------------
# Candelabras (back corners) and braziers of purple fire (front corners)
# ----------------------------------------------------------------------------
def flame(name, loc, mat, h=0.08, r=0.022):
    """Teardrop flame: a cone rising from a small sphere."""
    s = sphere(name + "_base", r, loc, mat, root, segs=12)
    c = cyl(name + "_tip", r * 0.95, h, (loc[0], loc[1], loc[2] + h / 2), mat, root, verts=12,
            r2=0.0, bevel=0.0)
    glow(s)
    glow(c)


for sx in (-1, 1):
    base = Vector((sx * 0.6, 0.48, DECK_Z))
    stem_top = DECK_Z + 0.5
    cyl(f"candle_foot{sx}", 0.09, 0.05, base + Vector((0, 0, 0.025)), GOLD, root, verts=24, r2=0.05)
    cyl(f"candle_stem{sx}", 0.022, stem_top - DECK_Z, base + Vector((0, 0, (stem_top - DECK_Z) / 2)),
        GOLD, root, verts=12)
    sphere(f"candle_knop{sx}", 0.04, base + Vector((0, 0, 0.22)), GOLD, root)
    arms = (-1, 0, 1)
    for a in arms:
        # arms sweep sideways (east-west) so all three flames read on screen
        tip = base + Vector((a * 0.13, 0, (stem_top - DECK_Z) + (0.0 if a else 0.1)))
        if a:
            rail(f"candle_arm{sx}{a}", [base + Vector((0, 0, 0.3)),
                                        base + Vector((a * 0.12, 0, 0.32)), tip], 0.016)
        cup = tip + Vector((0, 0, 0.0))
        cyl(f"candle_cup{sx}{a}", 0.04, 0.025, cup, GOLD, root, verts=16)
        ch = 0.12 if a else 0.15
        cyl(f"candle{sx}{a}", 0.026, ch, cup + Vector((0, 0, ch / 2)), WAX, root, verts=16)
        flame(f"candle_flame{sx}{a}", tuple(cup + Vector((0, 0, ch + 0.022))), FLAME)
    point_light(f"candle_light{sx}", base + Vector((0, -0.05, 0.75)), (1.0, 0.65, 0.3), 4.0)

for sx in (-1, 1):
    c = Vector((sx * 0.58, -0.56, DECK_Z))
    BR_H = 0.2
    for k in range(3):   # tripod legs
        a = TAU * k / 3 + (math.pi / 2 if sx > 0 else -math.pi / 2)
        rail(f"brazier{sx}_leg{k}", [c + Vector((0.1 * math.cos(a), 0.1 * math.sin(a), 0.0)),
                                     c + Vector((0.06 * math.cos(a), 0.06 * math.sin(a), BR_H * 0.6)),
                                     c + Vector((0.08 * math.cos(a), 0.08 * math.sin(a), BR_H))],
             0.016)
        sphere(f"brazier{sx}_foot{k}", 0.022, tuple(c + Vector((0.1 * math.cos(a), 0.1 * math.sin(a),
                                                                 0.015))), GOLD, root)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.11)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.001], context="VERTS")
    bowl = mesh_obj(f"brazier{sx}_bowl", bm, BRONZE, root, smooth=True)
    bowl.location = c + Vector((0, 0, BR_H + 0.08))
    bowl.scale = (1, 1, 0.75)
    bowl.modifiers.new("solid", "SOLIDIFY").thickness = 0.015
    rail(f"brazier{sx}_lip", [(c.x + x, c.y + y, BR_H + DECK_Z + 0.08) for x, y in circle(0.11, 32)],
         0.02, closed=True)
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        sphere(f"brazier{sx}_gem{k}", 0.018, (c.x + 0.1 * math.cos(a), c.y + 0.1 * math.sin(a),
                                              DECK_Z + BR_H + 0.03), RUBY, root)
    glow(cyl(f"brazier{sx}_coals", 0.1, 0.03, c + Vector((0, 0, BR_H + 0.07)), COALS, root,
             verts=24))
    # a cluster of purple tongues of fire
    for k, (dx, dy, h) in enumerate(((0.0, 0.0, 0.2), (0.045, 0.02, 0.13), (-0.045, 0.025, 0.14),
                                     (0.01, -0.045, 0.11))):
        flame(f"brazier{sx}_fire{k}", (c.x + dx, c.y + dy, DECK_Z + BR_H + 0.11), PFIRE, h=h,
              r=0.035 if k == 0 else 0.026)
    point_light(f"brazier_light{sx}", c + Vector((0, -0.05, BR_H + 0.3)), (0.85, 0.3, 1.0), 5.0)

# ----------------------------------------------------------------------------
# Render (single static frame: containers only take a Sprite)
# ----------------------------------------------------------------------------
rig = setup_scene(frame_w=4.0, frame_h=3.0, frame_cy=0.35)


def pose(f):
    pass


render_passes(rig, pose, extra_lights=tuple(LIGHTS), name="rune-altar")
