"""
Procedural Blender model + Factorio render of the soul collector.

The soul collector is a container (one slot) that pulls the soul of anything
dying within 35 tiles into itself and keeps it. Containers only take a static
`picture`, so this renders a single frame (main + glow + shadow):

    blender -b --factory-startup -P blender/soul_collector.py -- \
        --out graphics/generated/soul-collector [--preview] [--samples 32]

Shared helpers live in blender/fblend.py; stitch with blender/stitch.py.
World units are Factorio tiles; the entity is 2x2 centred on the origin,
+y is north, +z is up.

What the building shows, top to bottom, and why:
  * a gold intake funnel opening to the sky with spiral vanes and a teal
    vortex being drawn down its throat - that is where souls come in;
  * a handwheel valve on the funnel neck that seals the chamber once full
    (it holds exactly one soul);
  * a bulbous glass reliquary in a gold cage with the captured soul inside,
    its tail shackled to the chamber floor by gold chains (souls in this mod
    are teal, wispy and chained, see graphics/bound-soul*.png);
  * a rune-banded socket and a capacity gauge (needle on "1") under it;
  * a sloped purple pedestal with heavy gold scrollwork, rune inlays and a
    studded rim; four corner posts, the tall back pair bracing the funnel.
"""

import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import fblend  # noqa: E402

args = fblend.parse_args("soul-collector", frames=1, samples=192)
fblend.standard_materials()
from fblend import *  # noqa: E402,F401,F403

OUT = fblend.OUT

# ----------------------------------------------------------------------------
# Material identity: a necromantic soul trap
# ----------------------------------------------------------------------------
# The conjuration machine owns the gold-and-purple look; this building is the
# cold one of the set: black basalt/obsidian body, black iron fittings, ivory
# bone for ribs, cage bars and trims, and spectral teal ghost-light instead of
# magenta. Real gold survives only on a couple of tiny fittings. The shared
# names are rebound (here and in fblend, whose helpers default to its GOLD /
# PURPLE) so the model code below stays unchanged.


def obsidian(name):
    """Volcanic glass: near-black, very glossy, with a deep green/purple sheen
    in the highlights (tinted specular + coat), conchoidal chipped facets
    (smooth voronoi cells + concentric ripple bump) and a faint glassy
    green-grey on sharp, thin edges (pointiness), where real obsidian goes
    translucent. Mottled so large faces don't read as flat black holes."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # chipped facets: smooth F1 voronoi cells give scalloped flake scars
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "SMOOTH_F1"
    vor.inputs["Scale"].default_value = 11.0
    vor.inputs["Smoothness"].default_value = 0.35
    L(geo.outputs["Position"], vor.inputs["Vector"])
    # conchoidal ripples inside each scar
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 9.0
    wave.inputs["Distortion"].default_value = 4.0
    wave.inputs["Detail"].default_value = 2.0
    L(geo.outputs["Position"], wave.inputs["Vector"])
    b1 = nt.nodes.new("ShaderNodeBump")
    b1.inputs["Strength"].default_value = 0.55
    b1.inputs["Distance"].default_value = 0.03
    L(vor.outputs["Distance"], b1.inputs["Height"])
    b2 = nt.nodes.new("ShaderNodeBump")
    b2.inputs["Strength"].default_value = 0.12
    b2.inputs["Distance"].default_value = 0.01
    L(wave.outputs["Fac"], b2.inputs["Height"])
    L(b1.outputs["Normal"], b2.inputs["Normal"])
    L(b2.outputs["Normal"], bsdf.inputs["Normal"])
    L(b2.outputs["Normal"], bsdf.inputs["Coat Normal"])
    # mottled near-black body, glassy green-grey on thin sharp edges
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6.0
    nz.inputs["Detail"].default_value = 6.0
    L(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.004, 0.004, 0.006, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.018, 0.018, 0.024, 1)
    L(nz.outputs["Fac"], ramp.inputs["Fac"])
    edge = nt.nodes.new("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value = 0.56
    edge.inputs["From Max"].default_value = 0.66
    L(geo.outputs["Pointiness"], edge.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (0.035, 0.055, 0.05, 1)
    L(edge.outputs["Result"], mix.inputs["Factor"])
    L(ramp.outputs["Color"], mix.inputs["A"])
    L(mix.outputs["Result"], bsdf.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.05
    rr.inputs["To Max"].default_value = 0.22
    L(nz.outputs["Fac"], rr.inputs["Value"])
    L(rr.outputs["Result"], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.75
    bsdf.inputs["Specular Tint"].default_value = (0.72, 0.9, 0.82, 1)   # green sheen
    bsdf.inputs["Coat Weight"].default_value = 0.6
    bsdf.inputs["Coat Roughness"].default_value = 0.04
    bsdf.inputs["Coat Tint"].default_value = (0.9, 0.82, 1.0, 1)        # purple sheen
    bsdf.inputs["Transmission Weight"].default_value = 0.08
    return m


REAL_GOLD = GOLD
OBSIDIAN = obsidian("obsidian")
# aged, yellowed bone with porous pitting - not clean ivory, which reads as plastic
BONE = paint("bone", (0.53, 0.47, 0.35), (0.13, 0.1, 0.06), noise_scale=22.0, bump=0.6,
             bump_scale=90.0, dirt=0.5)
IRON = metal("black_iron", (0.17, 0.165, 0.16), (0.018, 0.017, 0.016), rough=(0.35, 0.62),
             wear=(0.42, 0.4, 0.37), dirt=0.3)
SOULSTONE = gem("soulstone", (0.1, 0.55, 0.52))
# Obsidian dominates: body, base, frames, ribs and trims are all knapped
# volcanic glass; black iron holds the vessel; bone only on the skull,
# post finials and the funnel's rib vanes; teal runes are the body's light.
GOLD = OBSIDIAN             # rails, ribs, studs drawn by this script
PURPLE = BRONZE = OBSIDIAN  # panels, posts, plinth, deck, socket
BRASS = COPPER = IRON
RUBY = SOULSTONE
fblend.GOLD = OBSIDIAN      # helper defaults: frames, studs
fblend.PURPLE = OBSIDIAN
# runes glow ghost-teal, not magenta
_rn = RUNE.node_tree.nodes["Principled BSDF"]
_rn.inputs["Emission Color"].default_value = (0.2, 0.95, 0.85, 1)
_rn.inputs["Base Color"].default_value = (0.01, 0.05, 0.05, 1)

# souls are pale teal (bound-soul, tormented-soul); the binding magic is purple
SOUL_C = (0.42, 0.95, 0.88)
SOUL_DEEP = (0.05, 0.45, 0.42)
# Emission kept below 1.0 per channel: the sprite is saved with the Standard
# view transform, so anything brighter clips to white and loses its teal hue.
VORTEX, VORTEX_EM = emitter("vortex", (0.18, 0.92, 0.82), 0.62, base=(0.01, 0.06, 0.05))
GAUGE_FACE = paint("gauge_face", (0.8, 0.74, 0.58), (0.3, 0.25, 0.15), dirt=0.1, bump=0.05)
SOOT = paint("soot", (0.02, 0.018, 0.02), (0.0, 0.0, 0.0), dirt=0.0, bump=0.0)
RUNE_EM.default_value = 0.6


def soul_material(name, strength, dens_lo, dens_hi, blend):
    """Wispy ghost: streaky emission (noise stretched along z) mixed with
    transparency so the core reads bright and the edges fray into smoke."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    out = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (9.0, 9.0, 2.5)       # streaks run upwards
    L(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8.0
    nz.inputs["Distortion"].default_value = 1.2
    L(mp.outputs[0], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (*SOUL_DEEP, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (*SOUL_C, 1)
    L(nz.outputs["Fac"], ramp.inputs["Fac"])
    # facing ratio: silhouette edges thinner (smoke), centre dense
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = blend
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L(lw.outputs["Facing"], inv.inputs[1])
    dens = nt.nodes.new("ShaderNodeMath")
    dens.operation = "MULTIPLY"
    dens.use_clamp = True
    L(inv.outputs[0], dens.inputs[0])
    nm = nt.nodes.new("ShaderNodeMapRange")
    nm.inputs["From Min"].default_value = 0.3
    nm.inputs["From Max"].default_value = 0.6
    nm.inputs["To Min"].default_value = dens_lo
    nm.inputs["To Max"].default_value = dens_hi
    L(nz.outputs["Fac"], nm.inputs["Value"])
    L(nm.outputs["Result"], dens.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    L(ramp.outputs["Color"], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    L(dens.outputs[0], mix.inputs["Fac"])
    L(tr.outputs[0], mix.inputs[1])
    L(em.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs[0])
    return m


# Layered like smoke: a faint, frayed outer veil, a denser core inside it and
# loose wisps, each translucent, so the soul shades softly instead of
# reading as a solid shape. Strengths stay low so overlaps do not clip.
SOUL = soul_material("soul", 0.62, 0.0, 0.55, 0.65)
SOUL_CORE = soul_material("soul_core", 0.8, 0.5, 1.2, 0.4)
SOUL_WISP = soul_material("soul_wisp", 0.55, 0.2, 0.8, 0.5)


def glass_mat():
    """Thin, faintly teal glass: mostly see-through (alpha) with a glossy
    sheen. Real transmission mirrors the gold cage at this angle and hides
    the soul, which is the whole point of the chamber."""
    m, nt, bsdf = node_mat("chamber_glass")
    bsdf.inputs["Base Color"].default_value = (0.3, 0.55, 0.52, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Alpha"].default_value = 0.14
    return m


CGLASS = glass_mat()
FUNNEL_IN = paint("funnel_in", (0.1, 0.06, 0.035), (0.015, 0.01, 0.006), noise_scale=12.0,
                  bump=0.4, bump_scale=40.0, dirt=0.0)
VELVET = paint("velvet", (0.03, 0.04, 0.045), (0.004, 0.005, 0.006), noise_scale=30.0, dirt=0.0,
               bump=0.3, bump_scale=80.0)

root = bpy.data.objects.new("soul_collector", None)
link(root)

# ----------------------------------------------------------------------------
# Pedestal
# ----------------------------------------------------------------------------
#
# Chamfered-square pedestal whose walls slope inwards (they read as wings in
# Factorio's projection, like the vanilla 2x2 buildings' skirts). It fills the
# footprint like the steel furnace / accumulator do.

HALF = 0.95          # half footprint at the ground
CH = 0.26            # corner chamfer at the ground
PLINTH_H = 0.12
XT = 0.76            # half width of the deck (walls slope in to here)
TCH = 0.2            # deck corner chamfer
DECK_Z = 0.5
CX, CY = 0.0, 0.06   # chamber axis, nudged north so the tall part sits at the back


def octo(h, c):
    """Chamfered square, counter-clockwise from the front-left corner."""
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c),
            (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]


def prism(name, poly, z0, z1, mat, bevel=0.01, parent=None):
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in poly]
    t = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((b[i], b[j], t[j], t[i]))
    o = mesh_obj(name, bm, mat, parent or root, bevel=bevel)
    o.data.shade_flat()
    return o


def rail(name, pts, r, closed=False, mat=None):
    mat = mat or GOLD
    # obsidian trims get a diamond section: sharp knapped ridges, not tubes
    return curve_obj(name, [tuple(p) for p in pts], mat, r, root, closed=closed,
                     res=0 if mat is OBSIDIAN else 3)


def lathe(name, profile, mat, loc, segs=48, parent=None, smooth=True, bevel=0.0):
    """Surface of revolution about local z from (radius, z) profile points."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        rings.append([bm.verts.new((r * math.cos(TAU * k / segs), r * math.sin(TAU * k / segs), z))
                      for k in range(segs)])
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            q = (k + 1) % segs
            bm.faces.new((a[k], a[q], b[q], b[k]))
    o = mesh_obj(name, bm, mat, parent or root, smooth=smooth, bevel=bevel)
    o.location = loc
    return o


bot2d = octo(HALF, CH)
top2d = octo(XT, TCH)
B3 = [Vector((x, y, PLINTH_H)) for x, y in bot2d]
T3 = [Vector((x, y, DECK_Z)) for x, y in top2d]

# plinth: dark bronze band, thick gold top rail, rivets on the visible faces
prism("plinth", bot2d, 0, PLINTH_H, BRONZE)
rail("plinth_rail", [(x, y, PLINTH_H) for x, y in bot2d], 0.055, closed=True, mat=IRON)
rail("plinth_foot", [(x * 1.008, y * 1.008, 0.02) for x, y in bot2d], 0.028, closed=True, mat=IRON)
for fi in (7, 0, 1, 2, 6):
    a, b = Vector((*bot2d[fi], 0)), Vector((*bot2d[(fi + 1) % 8], 0))
    nrm = Vector((b.y - a.y, -(b.x - a.x), 0)).normalized()
    count = max(2, round((b - a).length / 0.16))
    for k in range(count):
        p = a.lerp(b, (k + 0.5) / count) + nrm * 0.004
        sphere(f"rivet{fi}_{k}", 0.024, (p.x, p.y, PLINTH_H * 0.5), IRON, root)

walls = {}
for i in range(8):
    j = (i + 1) % 8
    p = Panel(B3[i], B3[j], T3[j], T3[i])
    p.build(f"wall{i}", PURPLE, parent=root)
    walls[i] = p
for i in range(8):     # knapped obsidian ridges on the corner edges
    rail(f"corner_rib{i}", [B3[i] + Vector((0, 0, 0.02)), T3[i] + Vector((0, 0, 0.01))], 0.055)

FIL_R = 0.036        # raised scrollwork (heavy gold, still >2 px at 64 px/tile)


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
    return S


# front: three framed bays - scrolls either side of a glowing rune plate
front = walls[0]
ribs_u = (0.33, 0.67)
for k, u in enumerate(ribs_u):
    rail(f"front_rib{k}", [Vector(front.at(u, 0, 0.03)), Vector(front.at(u, 1, 0.03))], 0.045)
for k, (u0, u1) in enumerate(((0.0, ribs_u[0]), ribs_u, (ribs_u[1], 1.0))):
    sp = sub_panel(front, u0 + 0.04, u1 - 0.04, 0.1, 0.9)
    gold_frame(sp, f"fp{k}_frame", 0.028, parent=root)
    inner = sub_panel(sp, 0.1, 0.9, 0.1, 0.9)
    # glowing runes carved into every bay: the body's light source
    rune(inner, f"fp{k}_rune", (0, 1, 3)[k], radius=0.017, parent=root)
    if k == 1:
        inner.studs("fp_gem", [(0.5, 1.0)], r=0.034, mat=RUBY, parent=root)

# side wings: scroll pairs around a ruby, a rune plate in the middle
for i in (2, 6):
    w = walls[i]
    for k, (u0, u1) in enumerate(((0.0, 0.36), (0.36, 0.64), (0.64, 1.0))):
        sp = sub_panel(w, u0 + 0.03, u1 - 0.03, 0.1, 0.9)
        gold_frame(sp, f"side{i}_{k}_frame", 0.026, parent=root)
        inner = sub_panel(sp, 0.1, 0.9, 0.1, 0.9)
        rune(inner, f"side{i}_{k}_rune", (i + k) % 4, radius=0.017, parent=root)
# chamfers: a single big curl each, ruby at the eye
for i in (1, 7, 3, 5):
    sp = sub_panel(walls[i], 0.12, 0.88, 0.12, 0.88)
    rune(sp, f"ch{i}_rune", i, radius=0.017, parent=root)

# deck: bronze plate, wide gold rim band studded with gold and rubies
prism("deck", top2d, DECK_Z - 0.04, DECK_Z, BRONZE, bevel=0.008)
rail("deck_outer", [t + Vector((0, 0, 0.02)) for t in T3], 0.06, closed=True)
inner_deck = [Vector((x, y, DECK_Z + 0.015)) for x, y in octo(XT - 0.13, TCH * 0.6)]
rail("deck_inner", inner_deck, 0.035, closed=True)
for i in range(8):
    a = T3[i].lerp(inner_deck[i], 0.5)
    b = T3[(i + 1) % 8].lerp(inner_deck[(i + 1) % 8], 0.5)
    n = max(1, round((b - a).length / 0.2))
    for k in range(n):
        p = a.lerp(b, (k + 0.5) / n) + Vector((0, 0, 0.025))
        sphere(f"deck_stud{i}_{k}", 0.028 if k % 2 else 0.032, tuple(p),
               RUBY if k % 2 else GOLD, root)

# ----------------------------------------------------------------------------
# Corner posts
# ----------------------------------------------------------------------------
# Back pair tall (they brace the funnel, tall parts at the back like vanilla),
# front pair short with glowing rune faces.

POST_W = 0.15
POSTS = [(-0.56, -0.52, 0.9), (0.56, -0.52, 0.9), (-0.56, 0.54, 1.75), (0.56, 0.54, 1.75)]
for pi, (px, py, top) in enumerate(POSTS):
    h = top - DECK_Z
    box(f"post{pi}", (POST_W, POST_W, h), (px, py, DECK_Z + h / 2), PURPLE, root, bevel=0.015)
    box(f"post{pi}_foot", (POST_W + 0.07, POST_W + 0.07, 0.08), (px, py, DECK_Z + 0.04), IRON,
        root, bevel=0.015)
    box(f"post{pi}_cap", (POST_W + 0.06, POST_W + 0.06, 0.06), (px, py, top + 0.03), IRON, root,
        bevel=0.015)
    for sx in (-1, 1):       # sharp obsidian corner arrises
        for sy in (-1, 1):
            rail(f"post{pi}_edge{sx}{sy}", [(px + sx * POST_W / 2, py + sy * POST_W / 2, DECK_Z + 0.08),
                                            (px + sx * POST_W / 2, py + sy * POST_W / 2, top)], 0.02)
    # finial: bone knob holding a knapped obsidian spike
    lathe(f"post{pi}_finial", [(0.0, 0.0), (0.06, 0.02), (0.05, 0.06), (0.03, 0.08), (0.0, 0.09)],
          BONE, (px, py, top + 0.06), segs=20)
    cyl(f"post{pi}_spike", 0.045, 0.2, (px, py, top + 0.22), OBSIDIAN, root, verts=5, r2=0.0,
        bevel=0.0).data.shade_flat()
    # rune on the south face
    face = Panel((px - POST_W / 2, py - POST_W / 2 - 0.002, DECK_Z + 0.12),
                 (px + POST_W / 2, py - POST_W / 2 - 0.002, DECK_Z + 0.12),
                 (px + POST_W / 2, py - POST_W / 2 - 0.002, top - 0.05),
                 (px - POST_W / 2, py - POST_W / 2 - 0.002, top - 0.05))
    if top > 1:      # tall pillars carry a column of runes
        for ri, (v0, v1) in enumerate(((0.03, 0.33), (0.36, 0.66), (0.69, 0.99))):
            rune(sub_panel(face, 0.05, 0.95, v0, v1), f"post{pi}_rune{ri}", pi + ri,
                 radius=0.015, parent=root)
    else:
        rune(sub_panel(face, 0.05, 0.95, 0.05, 0.95), f"post{pi}_rune", pi, radius=0.015,
             parent=root)

# ----------------------------------------------------------------------------
# Soul chamber
# ----------------------------------------------------------------------------

SOCK_Z0, SOCK_Z1 = DECK_Z, DECK_Z + 0.14     # rune-banded socket the glass sits in
GL_Z0, GL_Z1 = SOCK_Z1, 1.6                   # glass bulb
# Tall and slim on purpose: at 45 degrees the lid hides everything inside a
# squat bulb; the soul's face must be seen through the front of the glass.
GL_PROFILE = [(0.29, 0.0), (0.34, 0.1), (0.37, 0.25), (0.37, 0.55), (0.35, 0.72),
              (0.3, 0.86), (0.28, GL_Z1 - GL_Z0)]


def glass_r(z):
    """Radius of the bulb at height z (world)."""
    t = z - GL_Z0
    for (r0, z0), (r1, z1) in zip(GL_PROFILE, GL_PROFILE[1:]):
        if z0 <= t <= z1:
            return r0 + (r1 - r0) * (t - z0) / (z1 - z0)
    return GL_PROFILE[-1][0]


sock = lathe("socket", [(0.42, 0.0), (0.46, 0.02), (0.46, 0.04), (0.41, 0.05), (0.41, 0.11),
                        (0.44, 0.12), (0.44, 0.14), (0.0, 0.14)],
             BRONZE, (CX, CY, SOCK_Z0), bevel=0.0)
rail("socket_ring_lo", [(CX + 0.465 * math.cos(TAU * k / 48), CY + 0.465 * math.sin(TAU * k / 48),
                         SOCK_Z0 + 0.03) for k in range(48)], 0.03, closed=True, mat=IRON)
rail("socket_ring_hi", [(CX + 0.45 * math.cos(TAU * k / 48), CY + 0.45 * math.sin(TAU * k / 48),
                         SOCK_Z1) for k in range(48)], 0.04, closed=True)
# bolt ring fastening the socket to the deck
for k in range(16):
    a = TAU * (k + 0.5) / 16
    sphere(f"sock_bolt{k}", 0.02, (CX + 0.5 * math.cos(a), CY + 0.5 * math.sin(a), DECK_Z + 0.005),
           GOLD, root, segs=10)
# rune band round the socket: each glyph on a tangent plate facing out
for k in range(9):
    if k == 4:
        continue        # the skull sits at the front
    a = math.radians(-90) + TAU * (k - 4) / 14            # front arc only (the back is hidden)
    n = Vector((math.cos(a), math.sin(a), 0))
    t = Vector((-math.sin(a), math.cos(a), 0))
    c = Vector((CX, CY, (SOCK_Z0 + SOCK_Z1) / 2 + 0.005)) + n * 0.415
    hw, hh = 0.045, 0.04
    plate = Panel(c - t * hw - Vector((0, 0, hh)), c + t * hw - Vector((0, 0, hh)),
                  c + t * hw + Vector((0, 0, hh)), c - t * hw + Vector((0, 0, hh)))
    if plate.n.dot(n) < 0:
        plate = Panel(plate.c[1], plate.c[0], plate.c[3], plate.c[2])
    rune(plate, f"sock_rune{k}", k, radius=0.009, parent=root)

# dark velvet lining the back half of the bulb: the soul glows against it
lining = lathe("lining", [(r - 0.03, z) for r, z in GL_PROFILE], VELVET, (CX, CY, GL_Z0), segs=64)
bm_ = bmesh.new()
bm_.from_mesh(lining.data)
bmesh.ops.delete(bm_, geom=[v for v in bm_.verts if v.co.y < -0.02], context="VERTS")
bm_.to_mesh(lining.data)
bm_.free()
bulb = lathe("glass_bulb", GL_PROFILE, CGLASS, (CX, CY, GL_Z0), segs=64)
bulb.modifiers.new("solid", "SOLIDIFY").thickness = 0.012
bulb["see_through"] = True

# black iron cage: 6 slim ribs, none across the front, so the vessel and the
# soul inside stay the clear focal point
for k in range(6):
    a = TAU * k / 6
    pts = [(CX + (glass_r(z) + 0.022) * math.cos(a), CY + (glass_r(z) + 0.022) * math.sin(a), z)
           for z in [GL_Z0 + (GL_Z1 - GL_Z0) * i / 16 for i in range(17)]]
    rail(f"cage_rib{k}", pts, 0.017, mat=IRON)

# --- the soul: a wispy teal wraith, like a cold flame, twisting up from the
# floor socket. No face - at 64 px per tile features read as an emoji; only a
# faint hollow on the head hints at one.
SOUL_Z = GL_Z0 + 0.04
SOUL_Y = CY - 0.04   # leaning towards the glass so it is in view under the lid
WRAITH = [(0.0, 0.0), (0.05, 0.04), (0.11, 0.13), (0.155, 0.26), (0.165, 0.38), (0.15, 0.48),
          (0.12, 0.56), (0.11, 0.62), (0.09, 0.68), (0.05, 0.75), (0.02, 0.8), (0.0, 0.84)]


def wraith(name, scale, mat, twist, noise, disp):
    o = lathe(name, [(r * scale, z * (0.92 + 0.08 * scale)) for r, z in WRAITH], mat,
              (CX, SOUL_Y, SOUL_Z), segs=40)
    # twist it into a rising spiral and fray the surface so it reads as smoke
    tw = o.modifiers.new("twist", "SIMPLE_DEFORM")
    tw.deform_method = "TWIST"
    tw.angle = math.radians(twist)
    tw.deform_axis = "Z"
    bend = o.modifiers.new("bend", "SIMPLE_DEFORM")     # tip curls over like a flame
    bend.deform_method = "BEND"
    bend.angle = math.radians(25)
    bend.deform_axis = "Y"
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    tex = bpy.data.textures.new(name + "_wisp", "CLOUDS")
    tex.noise_scale = noise
    tex.noise_depth = 3
    dm = o.modifiers.new("disp", "DISPLACE")
    dm.texture = tex
    dm.strength = disp
    dm.texture_coords = "OBJECT"
    return glow(o)


soul = wraith("soul_veil", 0.8, SOUL, 150, 0.07, 0.07)
wraith("soul_core", 0.42, SOUL_CORE, 200, 0.1, 0.035)
# the faintest suggestion of a face: a soft, half-transparent hollow
HOLLOW, _, _ = node_mat("soul_hollow")
_nt = HOLLOW.node_tree
_mix = _nt.nodes.new("ShaderNodeMixShader")
_mix.inputs["Fac"].default_value = 0.35
_tr = _nt.nodes.new("ShaderNodeBsdfTransparent")
_nt.links.new(_tr.outputs[0], _mix.inputs[1])
_nt.links.new(_nt.nodes["Principled BSDF"].outputs[0], _mix.inputs[2])
_nt.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.03, 0.04, 1)
_nt.links.new(_mix.outputs[0], _nt.nodes["Material Output"].inputs[0])
HEAD = Vector((CX, SOUL_Y, SOUL_Z + 0.6))
h = sphere("soul_hollow", 0.045, (HEAD.x + 0.01, HEAD.y - 0.06, HEAD.z), HOLLOW, root, segs=16)
h.scale = (1.3, 0.5, 0.8)
h["see_through"] = True        # no hard black hole in the glow layer
# smoke curling off the body into the bulb
rng = random.Random(7)
for k in range(14):
    a0 = rng.uniform(0, TAU)
    r0 = rng.uniform(0.1, 0.17)
    z0 = SOUL_Z + rng.uniform(0.05, 0.4)
    pts = [(CX + (r0 + 0.08 * t) * math.cos(a0 + 2.2 * t), SOUL_Y + (r0 + 0.08 * t) * math.sin(a0 + 2.2 * t),
            z0 + 0.25 * t) for t in (i / 10 for i in range(11))]
    glow(curve_obj(f"soul_wisp{k}", pts, SOUL_WISP, 0.026, root, res=2,
                   taper=lambda t: (1.0 - t) ** 0.7))

soul_light_d = bpy.data.lights.new("soul_light", "POINT")
soul_light_d.color = SOUL_C
soul_light_d.energy = 4.0
soul_light_d.shadow_soft_size = 0.15
o = bpy.data.objects.new("soul_light", soul_light_d)
link(o, root)
o.location = (CX, CY - 0.05, SOUL_Z + 0.4)


# --- chains: the soul is bound by gold chain wound round it, pinned to the floor
def chain_link(name, p, d, w, k):
    """One oval link at p, long axis along d, alternate links turned 90 deg."""
    d = d.normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d)
    if k % 2:
        side, up = up, side
    L, W = 0.048, 0.03
    pts = [tuple(p + d * L * math.cos(TAU * i / 16) + side * W * math.sin(TAU * i / 16))
           for i in range(16)]
    return curve_obj(name, pts, IRON, 0.014, root, closed=True, res=2)


def chain(name, path, step=0.068):
    """Lay links along a polyline at constant spacing."""
    pts = [Vector(p) for p in path]
    segs = list(zip(pts, pts[1:]))
    total = sum((b - a).length for a, b in segs)
    n = int(total / step)
    for k in range(n + 1):
        s = k * step
        for a, b in segs:
            ln = (b - a).length
            if s <= ln:
                chain_link(f"{name}{k}", a.lerp(b, s / ln), b - a, 0.024, k)
                break
            s -= ln


# The chains hold only the soul's tail: links crossing the glowing body read
# as dark scribbles (eyes and mouths) at game scale.
SHACKLE_Z = SOUL_Z + 0.1
SHACKLE_R = 0.085
anchors = [(CX - 0.22, CY - 0.12, GL_Z0 + 0.01), (CX + 0.22, CY - 0.1, GL_Z0 + 0.01),
           (CX, CY + 0.2, GL_Z0 + 0.01)]
for ci, (ax, ay, az) in enumerate(anchors):
    d = Vector((ax - CX, ay - SOUL_Y, 0)).normalized()
    end = Vector((CX, SOUL_Y, SHACKLE_Z)) + d * SHACKLE_R
    mid = Vector((ax, ay, az)).lerp(end, 0.5) - Vector((0, 0, 0.02))   # slight sag
    chain(f"chain{ci}_", [(ax, ay, az + 0.02), tuple(mid), tuple(end)], step=0.075)
    cyl(f"chain_eye{ci}", 0.04, 0.03, (ax, ay, az), GOLD, root, verts=20)
    sphere(f"chain_pin{ci}", 0.022, (ax, ay, az + 0.02), RUBY, root, segs=10)
rail("soul_shackle", [(CX + SHACKLE_R * math.cos(TAU * k / 32), SOUL_Y + SHACKLE_R * math.sin(TAU * k / 32),
                       SHACKLE_Z) for k in range(32)], 0.022, closed=True)

# ----------------------------------------------------------------------------
# Lid, valve and intake funnel
# ----------------------------------------------------------------------------

LID_Z = GL_Z1
lathe("lid", [(0.31, 0.0), (0.32, 0.03), (0.28, 0.06), (0.22, 0.11), (0.15, 0.15),
              (0.12, 0.17), (0.0, 0.17)], OBSIDIAN, (CX, CY, LID_Z - 0.01), bevel=0.0)
rail("lid_ring", [(CX + 0.305 * math.cos(TAU * k / 48), CY + 0.305 * math.sin(TAU * k / 48), LID_Z)
                  for k in range(48)], 0.04, closed=True, mat=IRON)
for k in range(8):            # bolted clamp lugs holding the lid on the glass
    a = TAU * (k + 0.5) / 8
    c = Vector((CX + 0.31 * math.cos(a), CY + 0.31 * math.sin(a), LID_Z - 0.01))
    box(f"lid_lug{k}", (0.07, 0.06, 0.09), tuple(c), BRONZE, root, rot=(0, 0, a), bevel=0.012)
    sphere(f"lid_bolt{k}", 0.02, tuple(c + Vector((0.03 * math.cos(a), 0.03 * math.sin(a), 0.02))),
           GOLD, root, segs=10)
for k in range(4):            # scroll ribs up the lid
    a = TAU * (k + 0.5) / 4 - math.pi / 2
    pts = [(CX + r * math.cos(a), CY + r * math.sin(a), LID_Z + zz) for r, zz in
           ((0.31, 0.04), (0.26, 0.08), (0.2, 0.12), (0.14, 0.17), (0.12, 0.22))]
    rail(f"lid_rib{k}", pts, 0.022, mat=IRON)

NECK_Z0, NECK_Z1 = LID_Z + 0.15, LID_Z + 0.3
neck = cyl("neck", 0.1, NECK_Z1 - NECK_Z0, (CX, CY, (NECK_Z0 + NECK_Z1) / 2), BRASS, root, verts=32)
for z in (NECK_Z0 + 0.03, NECK_Z1 - 0.02):
    cyl(f"neck_band{z:.2f}", 0.12, 0.035, (CX, CY, z), GOLD, root, verts=32)

# seal valve on the neck, handwheel facing the camera (south)
VALVE = Vector((CX, CY - 0.12, (NECK_Z0 + NECK_Z1) / 2))
rx = (math.radians(90), 0, 0)
cyl("valve_body", 0.055, 0.08, tuple(VALVE + Vector((0, 0.02, 0))), BRASS, root, rot=rx, verts=24)
cyl("valve_stem", 0.016, 0.12, tuple(VALVE - Vector((0, 0.06, 0))), STEEL, root, rot=rx)
WHEEL = VALVE - Vector((0, 0.12, 0))
WR = 0.1
rail("valve_wheel", mat=REAL_GOLD, pts=[(WHEEL.x + WR * math.cos(TAU * k / 32), WHEEL.y, WHEEL.z + WR * math.sin(TAU * k / 32))
                     for k in range(32)], r=0.018, closed=True)
for k in range(5):
    a = TAU * k / 5 + 0.3
    rail(f"valve_spoke{k}", [tuple(WHEEL), (WHEEL.x + WR * math.cos(a), WHEEL.y, WHEEL.z + WR * math.sin(a))],
         0.011)
    sphere(f"valve_knob{k}", 0.017, (WHEEL.x + WR * math.cos(a), WHEEL.y, WHEEL.z + WR * math.sin(a)),
           GOLD, root, segs=10)
sphere("valve_hub", 0.026, tuple(WHEEL), RUBY, root, segs=12)

# funnel: flared trumpet, gold outside, dark bronze inside
FUN_Z = NECK_Z1 - 0.02
FUN_PROFILE = [(0.09, 0.0), (0.12, 0.06), (0.17, 0.13), (0.25, 0.2), (0.35, 0.26),
               (0.4, 0.3), (0.43, 0.315)]
outer_f = lathe("funnel_outer", FUN_PROFILE, OBSIDIAN, (CX, CY, FUN_Z), segs=64)
sol = outer_f.modifiers.new("solid", "SOLIDIFY")
sol.thickness = 0.02
sol.offset = 1.0      # outwards: lathe normals face out, keep the bore clear
inner_f = lathe("funnel_inner", [(r - 0.012, z + 0.006) for r, z in FUN_PROFILE], FUNNEL_IN,
                (CX, CY, FUN_Z), segs=64)
FUN_TOP = FUN_Z + FUN_PROFILE[-1][1]
rail("funnel_lip", [(CX + 0.43 * math.cos(TAU * k / 64), CY + 0.43 * math.sin(TAU * k / 64), FUN_TOP)
                    for k in range(64)], 0.035, closed=True)
for k in range(12):           # studs round the lip, alternating gold / ruby
    a = TAU * k / 12
    sphere(f"lip_stud{k}", 0.026 if k % 2 else 0.03,
           (CX + 0.43 * math.cos(a), CY + 0.43 * math.sin(a), FUN_TOP + 0.03),
           RUBY if k % 2 else GOLD, root, segs=10)


def fun_r(t):
    """Funnel inner radius at height t above FUN_Z."""
    for (r0, z0), (r1, z1) in zip(FUN_PROFILE, FUN_PROFILE[1:]):
        if z0 <= t <= z1:
            return r0 + (r1 - r0) * (t - z0) / (z1 - z0)
    return FUN_PROFILE[-1][0]


# spiral guide vanes inside the funnel: they set the incoming souls spinning
for k in range(6):
    pts = []
    for i in range(17):
        s = i / 16
        t = FUN_PROFILE[-1][1] * (1 - s) + 0.02 * s
        a = TAU * k / 6 + 2.0 * s
        r = fun_r(t) - 0.03
        pts.append((CX + r * math.cos(a), CY + r * math.sin(a), FUN_Z + t + 0.015))
    rail(f"vane{k}", pts, 0.017, mat=BONE)      # rib-bone vanes
# the vortex: glowing teal streams spiralling down the throat
for k in range(5):
    pts = []
    for i in range(25):
        s = i / 24
        t = FUN_PROFILE[-1][1] * 0.95 * (1 - s) + 0.0 * s
        a = TAU * k / 5 + 0.7 + 3.4 * s
        r = (fun_r(t) - 0.06) * (1 - 0.15 * s)
        pts.append((CX + r * math.cos(a), CY + r * math.sin(a), FUN_Z + t + 0.03))
    glow(curve_obj(f"vortex{k}", pts, VORTEX, 0.016, root, res=2,
                   taper=lambda t: 0.35 + 0.65 * math.sin(math.pi * min(1.0, t * 1.2))))
throat = cyl("throat", 0.075, 0.01, (CX, CY, FUN_Z + 0.012), VORTEX, root, verts=24)
glow(throat)

# ring of runes carved into the obsidian lid under the funnel (front arc; the
# funnel's own flank is edge-on to the 45 degree camera, the lid faces it).
# The valve sits dead front, so that slot stays empty.
LID_LO = Vector((0.0, 0.0, LID_Z - 0.01)), 0.3, 0.04     # (origin, r, z) on the lid slope
LID_HI = 0.19, 0.125
for k in range(7):
    if k == 3:
        continue
    a = math.radians(-90) + math.radians(27) * (k - 3)
    rad = Vector((math.cos(a), math.sin(a), 0))
    tan = Vector((-math.sin(a), math.cos(a), 0))
    lo = Vector((CX, CY, LID_Z - 0.01 + LID_LO[2])) + rad * LID_LO[1]
    hi = Vector((CX, CY, LID_Z - 0.01 + LID_HI[1])) + rad * LID_HI[0]
    wall_n = (hi - lo).cross(tan).normalized()
    if wall_n.dot(rad) < 0:
        wall_n = -wall_n
    off = wall_n * 0.004
    hw = 0.05
    plate = Panel(lo - tan * hw + off, lo + tan * hw + off, hi + tan * hw * 0.75 + off,
                  hi - tan * hw * 0.75 + off)
    if plate.n.dot(wall_n) < 0:
        plate = Panel(plate.c[1], plate.c[0], plate.c[3], plate.c[2])
    rune(plate, f"lid_rune{k}", k, radius=0.012, parent=root)
vlight_d = bpy.data.lights.new("vortex_light", "POINT")
vlight_d.color = SOUL_C
vlight_d.energy = 1.2
vlight_d.shadow_soft_size = 0.1
o = bpy.data.objects.new("vortex_light", vlight_d)
link(o, root)
o.location = (CX, CY, FUN_Z + 0.12)

# braces from the tall back posts to the neck, with scroll curls
for sx in (-1, 1):
    px, py, top = POSTS[2 if sx < 0 else 3]
    a = Vector((px, py, top - 0.1))
    b = Vector((CX + sx * 0.12, CY + 0.03, NECK_Z0 + 0.08))
    mid = a.lerp(b, 0.5) + Vector((0, 0, 0.12))
    rail(f"brace{sx}", [a, a.lerp(mid, 0.5) + Vector((0, 0, 0.03)), mid,
                        mid.lerp(b, 0.5) + Vector((0, 0, 0.02)), b], 0.028)
    curl = fit(scroll_c(0, 0, 1), 0, 0, 0.16, 0.16, flip_x=sx > 0)
    rail(f"brace_curl{sx}", [(mid.x + sx * (u - 0.08) * 0.8, mid.y, mid.z - 0.2 + v)
                             for u, v in curl], 0.018)
    cyl(f"brace_collar{sx}", 0.03, 0.05, tuple(b), GOLD, root, rot=(0, math.radians(90), 0))

# soul conduit: copper pipe from the back of the funnel down the back post into
# the pedestal (excess soul-stuff is bled off into the ground)
for sx in (-1, 1):
    px, py, top = POSTS[2 if sx < 0 else 3]
    pts = [(CX + sx * 0.26, CY + 0.18, FUN_Z + 0.18), (px + sx * 0.02, py + 0.04, top - 0.05),
           (px + sx * 0.1, py + 0.1, top - 0.2), (px + sx * 0.1, py + 0.1, DECK_Z + 0.05)]
    curve_obj(f"conduit{sx}", pts, COPPER, 0.026, root, res=3)
    for t in (0.35, 0.6, 0.85):
        z = top - 0.2 + (DECK_Z + 0.05 - (top - 0.2)) * t
        cyl(f"conduit{sx}_band{t}", 0.034, 0.02, (px + sx * 0.1, py + 0.1, z), GOLD, root, verts=16)

# ----------------------------------------------------------------------------
# Capacity gauge on the front of the socket (needle on "one soul")
# ----------------------------------------------------------------------------
GA = Vector((CX + 0.27, CY - 0.43, DECK_Z + 0.12))
rxg = (math.radians(90), 0, 0)
cyl("gauge_case", 0.085, 0.05, tuple(GA), BRASS, root, rot=rxg, verts=32)
cyl("gauge_face", 0.068, 0.01, tuple(GA - Vector((0, 0.027, 0))), GAUGE_FACE, root, rot=rxg, verts=32)
rail("gauge_bezel", mat=REAL_GOLD, pts=[(GA.x + 0.075 * math.cos(TAU * k / 32), GA.y - 0.03, GA.z + 0.075 * math.sin(TAU * k / 32))
                     for k in range(32)], r=0.014, closed=True)
for k in range(5):     # tick marks
    a = math.radians(210 - 60 * k)
    rail(f"gauge_tick{k}", [(GA.x + 0.045 * math.cos(a), GA.y - 0.034, GA.z + 0.045 * math.sin(a)),
                            (GA.x + 0.062 * math.cos(a), GA.y - 0.034, GA.z + 0.062 * math.sin(a))],
         0.005, mat=SOOT)
a = math.radians(-30)  # full: one soul held
rail("gauge_needle", [(GA.x, GA.y - 0.038, GA.z),
                      (GA.x + 0.058 * math.cos(a), GA.y - 0.038, GA.z + 0.058 * math.sin(a))],
     0.008, mat=RUBY)
box("gauge_bracket", (0.05, 0.05, 0.08), (GA.x, GA.y + 0.03, DECK_Z + 0.04), BRONZE, root, bevel=0.01)

# soul lamp on the other side of the socket: lit while a soul is held
LP = Vector((CX - 0.27, CY - 0.43, DECK_Z + 0.1))
cyl("lamp_base", 0.05, 0.05, (LP.x, LP.y, DECK_Z + 0.03), BRONZE, root, verts=24)
lamp = sphere("lamp_glass", 0.045, tuple(LP), VORTEX, root, segs=16)
glow(lamp)
for k in range(4):
    a = TAU * k / 4 + math.pi / 4
    rail(f"lamp_cage{k}", [(LP.x + 0.05 * math.cos(a), LP.y + 0.05 * math.sin(a), DECK_Z + 0.05),
                           (LP.x + 0.055 * math.cos(a), LP.y + 0.055 * math.sin(a), LP.z),
                           (LP.x, LP.y, LP.z + 0.065)], 0.009)
sphere("lamp_top", 0.018, (LP.x, LP.y, LP.z + 0.065), GOLD, root, segs=10)

# bone skull on the front of the socket, ghost-light in its eye sockets
SK = Vector((CX, CY - 0.53, SOCK_Z0 + 0.085))
sk = sphere("skull_cranium", 0.08, tuple(SK + Vector((0, 0.01, 0.015))), BONE, root, segs=20)
sk.scale = (1.0, 0.95, 0.9)
box("skull_jaw", (0.09, 0.06, 0.045), tuple(SK + Vector((0, -0.01, -0.06))), BONE, root, bevel=0.012)
for sx in (-1, 1):
    e = sphere(f"skull_socket{sx}", 0.025, tuple(SK + Vector((sx * 0.032, -0.066, 0.01))), SOOT, root,
               segs=10)
    glow(sphere(f"skull_eye{sx}", 0.012, tuple(SK + Vector((sx * 0.032, -0.08, 0.01))), VORTEX,
                root, segs=8))
sphere("skull_nose", 0.014, tuple(SK + Vector((0, -0.075, -0.022))), SOOT, root, segs=8)
for sx in (-1, 1):       # crossed bones behind it
    a = math.radians(35) * sx
    d = Vector((math.cos(a), 0, math.sin(a))) * 0.15
    c = SK + Vector((0, 0.02, -0.005))
    rail(f"skull_bone{sx}", [c - d, c + d], 0.014, mat=BONE)
    for e in (-1, 1):
        sphere(f"skull_knob{sx}{e}", 0.02, tuple(c + d * e * 1.05), BONE, root, segs=10)

# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
#
# fblend.render_passes holds out every non-glowing object in the glow pass;
# that would make the glass bulb an opaque mask over the soul. Same passes
# here, but see-through objects are hidden from the glow pass instead.

# frame widened and slid east so the long south-east shadow of the funnel fits;
# the Lua shift compensates (x = +FRAME_CX tiles at scale 0.5)
FRAME_CX = 1.1
rig = setup_scene(frame_w=5.3, frame_h=3.7, frame_cy=0.52)
bpy.context.scene.camera.location.x += FRAME_CX
LIGHTS = (rig.sun_d, rig.fill_d, soul_light_d, vlight_d)


def render_static():
    scene = bpy.context.scene
    render(OUT / "main-000.png")
    if not args.no_glow:
        energies = [l.energy for l in LIGHTS]
        bg = rig.bg.inputs["Strength"].default_value
        rig.bg.inputs["Strength"].default_value = 0.0
        for l in LIGHTS:
            l.energy = 0.0
        for o in scene.objects:
            if o.type in ("MESH", "CURVE"):
                if o.get("see_through"):
                    o.visible_camera = False
                else:
                    o.is_holdout = not o.get("glow", False)
        render(OUT / "glow-000.png")
        for o in scene.objects:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = False
                o.visible_camera = True
        for l, e in zip(LIGHTS, energies):
            l.energy = e
        rig.bg.inputs["Strength"].default_value = bg
    # shadow: key light only, lowered so the shadow falls south-east like vanilla
    rig.ground.hide_render = False
    for l in LIGHTS:
        l.energy = 0.0
    rig.sun_d.energy = 4.6
    for o in scene.objects:
        if o is not rig.ground and o.type in ("MESH", "CURVE"):
            o.visible_camera = False
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((1.0, -0.35, -0.75)).normalized()).to_euler()
    render(OUT / "shadow.png")


if args.save_blend:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "soul-collector.blend"))
render_static()
