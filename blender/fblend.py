"""
Shared Blender pipeline for the Orbs mod's building sprites.

Each building is a script (blender/<entity>.py) that builds its model
procedurally with these helpers, animates it as a seamless loop and renders
the passes Factorio needs. Run with

    blender -b --factory-startup -P blender/<entity>.py -- [--preview --frame 0,12]

then pack the frames with blender/stitch.py. See blender/conjuration_machine.py
for the reference building.

Conventions (learned the hard way on the conjuration machine):

* Units are Factorio tiles; the entity is centred on the origin, +y is north,
  +z is up. Factorio's projection is a plain orthographic camera looking down
  at 45 degrees with NO vertical stretch: screen y = (y + z) / sqrt(2)
  (core/lualib/math3d.lua, projection_constant). setup_camera() does this.
* Silhouette like vanilla: side walls slope outwards so they read as wings,
  rims rise towards the back, tall parts sit at the back. Compare every
  preview against the vanilla sprite of the same footprint at the same scale
  and match its on-screen size via the Lua `scale` (content width/height).
* Style of the mod: heavy gold castings (frames 0.05-0.075 tiles thick,
  raised scrollwork filling ~40% of panels), dusky magenta "PURPLE" paint with
  hammered texture, bronze/steel machinery, ruby studs, glowing runes.
  Thin wire-like detail disappears at 64 px per tile - make it chunky.
* Every moving part must move with purpose and be kinematically sound (gears
  mesh with aligned teeth, links keep their length, cams touch followers),
  and every loop must close: teeth, spokes and cranks advance whole periods
  per loop. Keep tooth motion under ~0.4 pitch per frame (no strobing).
* Self-lit parts get glow(obj) so they land in the night-light pass.
"""

import argparse
import fcntl
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

TAU = 2 * math.pi
args = None
OUT = None
N = 64


def parse_args(name, frames=64, samples=192):
    """Common command line; sets module-level args/OUT/N and resets the scene."""
    global args, OUT, N
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"graphics/generated/{name}")
    ap.add_argument("--frames", type=int, default=frames)
    ap.add_argument("--preview", action="store_true", help="render a few frames only")
    ap.add_argument("--frame", default="0", help="frame(s) for --preview, e.g. 8,24")
    ap.add_argument("--samples", type=int, default=samples)
    ap.add_argument("--px-per-tile", type=int, default=128,
                    help="render resolution; stitch.py downsamples to 64")
    ap.add_argument("--no-glow", action="store_true", help="skip the glow pass")
    ap.add_argument("--save-blend", action="store_true")
    args = ap.parse_args(argv)
    OUT = Path(args.out).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    N = args.frames
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return args


def link(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def glow(obj):
    """Mark an object as emissive: it is kept in the glow (light) pass."""
    obj["glow"] = True
    for c in obj.children_recursive:
        c["glow"] = True
    return obj


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------

def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf


DIRT = (0.05, 0.04, 0.03)


def grime(nt, bsdf, base, dark, noise_scale=18.0, ao_dist=0.2,
          rough=(0.25, 0.55), bump=0.15, bump_scale=60.0, dirt=0.3, wear=None,
          hammered=False):
    """Base colour darkened in crevices (AO) and mottled by noise, plus a
    hammered-metal bump. This is what keeps the render from looking CG-clean
    at 64px per tile."""
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 6.0
    L(tc.outputs["Object"], noise.inputs["Vector"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = ao_dist
    ao.samples = 8

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*base, 1)
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L(ao.outputs["AO"], mul.inputs[0])
    nmix = nt.nodes.new("ShaderNodeMapRange")
    nmix.inputs["To Min"].default_value = 0.75
    nmix.inputs["To Max"].default_value = 1.1
    L(noise.outputs["Fac"], nmix.inputs["Value"])
    L(nmix.outputs["Result"], mul.inputs[1])
    L(mul.outputs[0], ramp.inputs["Fac"])
    color = ramp.outputs["Color"]

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    if wear:
        # chipped paint: bare metal shows on convex edges
        pr = nt.nodes.new("ShaderNodeMapRange")
        pr.inputs["From Min"].default_value = 0.55
        pr.inputs["From Max"].default_value = 0.62
        L(geo.outputs["Pointiness"], pr.inputs["Value"])
        wn = nt.nodes.new("ShaderNodeTexNoise")
        wn.inputs["Scale"].default_value = 40.0
        L(geo.outputs["Position"], wn.inputs["Vector"])
        wm = nt.nodes.new("ShaderNodeMath")
        wm.operation = "MULTIPLY"
        L(pr.outputs["Result"], wm.inputs[0])
        L(wn.outputs["Fac"], wm.inputs[1])
        wmix = nt.nodes.new("ShaderNodeMix")
        wmix.data_type = "RGBA"
        wmix.inputs["B"].default_value = (*wear, 1)
        L(wm.outputs[0], wmix.inputs["Factor"])
        L(color, wmix.inputs["A"])
        color = wmix.outputs["Result"]
    if dirt:
        # grime: patchy world-space dirt, heavier towards the ground and in
        # crevices, like the weathering on the vanilla machines
        dn = nt.nodes.new("ShaderNodeTexNoise")
        dn.inputs["Scale"].default_value = 3.5
        dn.inputs["Detail"].default_value = 10.0
        dn.inputs["Roughness"].default_value = 0.65
        L(geo.outputs["Position"], dn.inputs["Vector"])
        dr = nt.nodes.new("ShaderNodeMapRange")
        dr.inputs["From Min"].default_value = 0.42
        dr.inputs["From Max"].default_value = 0.68
        L(dn.outputs["Fac"], dr.inputs["Value"])
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        L(geo.outputs["Position"], sep.inputs[0])
        hz = nt.nodes.new("ShaderNodeMapRange")
        hz.inputs["From Min"].default_value = 0.1
        hz.inputs["From Max"].default_value = 0.9
        hz.inputs["To Min"].default_value = 0.7
        hz.inputs["To Max"].default_value = 0.0
        L(sep.outputs["Z"], hz.inputs["Value"])
        cav = nt.nodes.new("ShaderNodeMath")
        cav.operation = "SUBTRACT"
        cav.inputs[0].default_value = 1.0
        L(ao.outputs["AO"], cav.inputs[1])
        mx = nt.nodes.new("ShaderNodeMath")
        mx.operation = "MAXIMUM"
        L(dr.outputs["Result"], mx.inputs[0])
        L(hz.outputs["Result"], mx.inputs[1])
        mx2 = nt.nodes.new("ShaderNodeMath")
        mx2.operation = "MAXIMUM"
        L(mx.outputs[0], mx2.inputs[0])
        L(cav.outputs[0], mx2.inputs[1])
        amt = nt.nodes.new("ShaderNodeMath")
        amt.operation = "MULTIPLY"
        amt.use_clamp = True
        amt.inputs[1].default_value = dirt
        L(mx2.outputs[0], amt.inputs[0])
        dmix = nt.nodes.new("ShaderNodeMix")
        dmix.data_type = "RGBA"
        dmix.inputs["B"].default_value = (*DIRT, 1)
        L(amt.outputs[0], dmix.inputs["Factor"])
        L(color, dmix.inputs["A"])
        color = dmix.outputs["Result"]
    L(color, bsdf.inputs["Base Color"])

    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough[0]
    rr.inputs["To Max"].default_value = rough[1]
    L(noise.outputs["Fac"], rr.inputs["Value"])
    L(rr.outputs["Result"], bsdf.inputs["Roughness"])

    if bump:
        bn = nt.nodes.new("ShaderNodeTexNoise")
        bn.inputs["Scale"].default_value = bump_scale
        bn.inputs["Detail"].default_value = 4.0
        L(tc.outputs["Object"], bn.inputs["Vector"])
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = 0.01
        L(bn.outputs["Fac"], b.inputs["Height"])
        normal = b.outputs["Normal"]
        if hammered:
            # beaten-metal dimples under the paint, so panels aren't flat fills
            hv = nt.nodes.new("ShaderNodeTexVoronoi")
            hv.inputs["Scale"].default_value = 28.0
            L(geo.outputs["Position"], hv.inputs["Vector"])
            hb = nt.nodes.new("ShaderNodeBump")
            hb.inputs["Strength"].default_value = 0.45
            hb.inputs["Distance"].default_value = 0.02
            L(hv.outputs["Distance"], hb.inputs["Height"])
            L(normal, hb.inputs["Normal"])
            normal = hb.outputs["Normal"]
            # and a mottled two-tone so the purple has depth
            mott = nt.nodes.new("ShaderNodeMix")
            mott.data_type = "RGBA"
            mott.blend_type = "MULTIPLY"
            mott.inputs["Factor"].default_value = 0.35
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.inputs["From Max"].default_value = 0.6
            mr.inputs["To Min"].default_value = 0.55
            L(hv.outputs["Distance"], mr.inputs["Value"])
            L(color, mott.inputs["A"])
            L(mr.outputs["Result"], mott.inputs["B"])
            L(mott.outputs["Result"], bsdf.inputs["Base Color"])
        L(normal, bsdf.inputs["Normal"])


def metal(name, base, dark, rough=(0.22, 0.5), **kw):
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Metallic"].default_value = 1.0
    grime(nt, bsdf, base, dark, rough=rough, **kw)
    return m


def paint(name, base, dark, **kw):
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Metallic"].default_value = 0.0
    grime(nt, bsdf, base, dark, rough=(0.4, 0.65), **kw)
    return m


def gem(name, color, glow=0.0):
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.8
    if glow:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = glow
    return m


def organic(name):
    """Bay floor: copper/rust flesh-like cells, as in the reference art."""
    m, nt, bsdf = node_mat(name)
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 4.5
    L(tc.outputs["Object"], vor.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 8.0
    L(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = (0.05, 0.012, 0.01, 1)
    els[1].position = 0.12
    els[1].color = (0.16, 0.05, 0.025, 1)
    e = els.new(0.45)
    e.color = (0.34, 0.14, 0.06, 1)
    L(vor.outputs["Distance"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.5
    L(ramp.outputs["Color"], mix.inputs["A"])
    L(noise.outputs["Color"], mix.inputs["B"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.15
    L(mix.outputs["Result"], ao.inputs["Color"])
    L(ao.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.55
    bsdf.inputs["Roughness"].default_value = 0.42
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.8
    b.inputs["Distance"].default_value = 0.04
    L(vor.outputs["Distance"], b.inputs["Height"])
    L(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def emitter(name, color, strength, base=None, glass=False):
    """Self-lit material; returns it with its strength socket for animating."""
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Base Color"].default_value = (*(base or color), 1)
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.12
    bsdf.inputs["Coat Weight"].default_value = 1.0 if glass else 0.0
    return m, bsdf.inputs["Emission Strength"]



def standard_materials():
    """Create the mod's shared palette as module globals (GOLD, PURPLE, ...).
    Call after parse_args(), then `from fblend import *` to use them."""
    global GOLD, BRASS, STEEL, BRONZE, COPPER, PURPLE, RUBY, FLESH, GLASS, RUNE, RUNE_EM
    GOLD = metal("gold", (0.95, 0.66, 0.24), (0.12, 0.065, 0.015), rough=(0.18, 0.4),
                 dirt=0.15)
    BRASS = metal("brass", (0.62, 0.45, 0.22), (0.12, 0.07, 0.03), rough=(0.25, 0.5))
    STEEL = metal("steel", (0.42, 0.40, 0.37), (0.04, 0.035, 0.03), rough=(0.25, 0.5))
    BRONZE = metal("bronze", (0.30, 0.20, 0.10), (0.05, 0.03, 0.02), rough=(0.4, 0.7))
    COPPER = metal("copper", (0.80, 0.38, 0.20), (0.18, 0.06, 0.03))
    PURPLE = paint("purple", (0.36, 0.07, 0.27), (0.03, 0.005, 0.022), noise_scale=9.0,
                   bump=0.6, bump_scale=25.0, dirt=0.2, hammered=True)
    RUBY = gem("ruby", (0.75, 0.05, 0.12))
    FLESH = organic("flesh")
    GLASS, _, _ = node_mat("glass")
    g = GLASS.node_tree.nodes["Principled BSDF"]
    g.inputs["Base Color"].default_value = (0.9, 0.88, 0.95, 1)
    g.inputs["Transmission Weight"].default_value = 1.0
    g.inputs["Roughness"].default_value = 0.04
    RUNE, RUNE_EM = emitter("rune", (0.8, 0.2, 1.0), 0.4, base=(0.08, 0.02, 0.08))


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------

def mesh_obj(name, bm, mat, parent=None, smooth=False, bevel=0.0, segs=2):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(mat)
    link(obj, parent)
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segs
        mod.limit_method = "ANGLE"
        mod.harden_normals = False
    return obj


def box(name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.01):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    o = mesh_obj(name, bm, mat, parent, bevel=bevel)
    o.location = loc
    o.rotation_euler = rot
    return o


def cyl(name, r, depth, loc, mat, parent=None, rot=(0, 0, 0), verts=32,
        bevel=0.006, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    o = mesh_obj(name, bm, mat, parent, smooth=True, bevel=bevel)
    o.location = loc
    o.rotation_euler = rot
    return o


def sphere(name, r, loc, mat, parent=None, segs=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2 + 2,
                              radius=r)
    o = mesh_obj(name, bm, mat, parent, smooth=True)
    o.location = loc
    return o


def ring_mesh(outer, inner, z0, z1):
    """Solid between two closed loops of equal length (2D point lists)."""
    bm = bmesh.new()
    n = len(outer)
    ob = [bm.verts.new((x, y, z0)) for x, y in outer]
    ot = [bm.verts.new((x, y, z1)) for x, y in outer]
    ib = [bm.verts.new((x, y, z0)) for x, y in inner]
    it = [bm.verts.new((x, y, z1)) for x, y in inner]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ot[i], ot[j], it[j], it[i]))
        bm.faces.new((ob[j], ob[i], ib[i], ib[j]))
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((ib[j], ib[i], it[i], it[j]))
    return bm


def gear(name, teeth, r, thick, mat, parent=None, spokes=5, inner=0.62,
         tooth=0.09):
    """Spur gear lying in XY (axis = local Z), centred on its origin.
    `r` is the pitch radius; tooth height is `tooth * r`."""
    root, tip = r * (1 - tooth / 2), r * (1 + tooth / 2)
    outer, ring_in = [], []
    for k in range(teeth):
        a = TAU * k / teeth
        da = TAU / teeth
        for frac, rad in ((0.0, root), (0.18, tip), (0.5, tip), (0.68, root)):
            ang = a + frac * da
            outer.append((rad * math.cos(ang), rad * math.sin(ang)))
            ring_in.append((r * inner * math.cos(ang), r * inner * math.sin(ang)))
    root_obj = bpy.data.objects.new(name, None)
    link(root_obj, parent)
    rim = mesh_obj(name + "_rim", ring_mesh(outer, ring_in, -thick / 2, thick / 2),
                   mat, root_obj, bevel=min(0.006, thick * 0.2))
    rim.data.shade_flat()
    hub_r = r * 0.22
    cyl(name + "_hub", hub_r, thick * 1.6, (0, 0, 0), mat, root_obj, verts=24)
    cyl(name + "_axle", hub_r * 0.45, thick * 2.2, (0, 0, 0), STEEL, root_obj,
        verts=16)
    for s in range(spokes):
        a = TAU * s / spokes
        L = r * inner - hub_r * 0.5
        mid = (hub_r * 0.5 + L / 2)
        box(f"{name}_spoke{s}", (L, r * 0.12, thick * 0.7),
            (mid * math.cos(a), mid * math.sin(a), 0), mat, root_obj,
            rot=(0, 0, a), bevel=0.004)
    return root_obj


def curve_obj(name, pts, mat, radius, parent=None, closed=False, res=3,
              taper=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (*co, 1)
        if taper:
            p.radius = 1.0
    if taper:
        n = len(pts)
        for i, p in enumerate(sp.points):
            p.radius = taper(i / max(n - 1, 1))
    sp.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, cu)
    obj.data.materials.append(mat)
    link(obj, parent)
    return obj


def spiral(cx, cy, r0, turns, a0, cw, n=40, shrink=0.12):
    """Log-ish spiral from radius r0 inwards; returns 2D points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = a0 + (-1 if cw else 1) * t * turns * TAU
        rr = r0 * (1 - (1 - shrink) * t) ** 1.3
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def bezier2(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def scroll_c(cx, cy, size, mirror=False, up=True):
    """'C'/'S' scroll: a stem curling into a spiral, the basic filigree unit
    of the reference art."""
    m = -1 if mirror else 1
    s = 1 if up else -1
    stem = bezier2((cx, cy - s * size), (cx + m * size * 0.9, cy - s * size * 0.2),
                   (cx + m * size * 0.35, cy + s * size * 0.45))
    curl_c = (cx + m * size * 0.05, cy + s * size * 0.35)
    start_ang = math.atan2(stem[-1][1] - curl_c[1], stem[-1][0] - curl_c[0])
    curl = spiral(curl_c[0], curl_c[1], math.dist(stem[-1], curl_c), 1.15,
                  start_ang, cw=(m * s > 0), n=30)
    return stem + curl[1:]


def fit(pts, u0, v0, u1, v1, flip_x=False):
    """Scale a 2D stroke to fill the rectangle (u0,v0)-(u1,v1)."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax, bx, ay, by = min(xs), max(xs), min(ys), max(ys)
    out = []
    for x, y in pts:
        tx = (x - ax) / (bx - ax or 1)
        if flip_x:
            tx = 1 - tx
        out.append((u0 + tx * (u1 - u0), v0 + (y - ay) / (by - ay or 1) * (v1 - v0)))
    return out


class Panel:
    """Planar quad (corners in CCW order seen from outside, 3D) with a
    bilinear (u,v) mapping for placing ornaments on it."""

    def __init__(self, c00, c10, c11, c01):
        self.c = [Vector(c) for c in (c00, c10, c11, c01)]
        e1 = self.c[1] - self.c[0]
        e2 = self.c[3] - self.c[0]
        self.n = e1.cross(e2).normalized()

    def at(self, u, v, lift=0.0):
        c00, c10, c11, c01 = self.c
        p = (c00 * (1 - u) * (1 - v) + c10 * u * (1 - v) + c11 * u * v
             + c01 * (1 - u) * v)
        return tuple(p + self.n * lift)

    def build(self, name, mat, thick=0.02, parent=None):
        bm = bmesh.new()
        vs = [bm.verts.new(tuple(c)) for c in self.c]
        bm.faces.new(vs)
        o = mesh_obj(name, bm, mat, parent)
        sol = o.modifiers.new("solid", "SOLIDIFY")
        sol.thickness = thick
        sol.offset = -1
        return o

    def filigree(self, name, strokes, radius=0.011, lift=0.012, parent=None,
                 mat=None):
        for i, pts in enumerate(strokes):
            curve_obj(f"{name}{i}", [self.at(u, v, lift) for u, v in pts],
                      mat or GOLD, radius, parent)

    def rim(self, name, radius=0.022, parent=None, edges=(0, 1, 2, 3)):
        for e in edges:
            a, b = self.c[e], self.c[(e + 1) % 4]
            curve_obj(f"{name}{e}", [tuple(a + self.n * radius * 0.5),
                                     tuple(b + self.n * radius * 0.5)],
                      GOLD, radius, parent)

    def studs(self, name, uvs, r=0.016, mat=None, parent=None):
        for i, (u, v) in enumerate(uvs):
            sphere(f"{name}{i}", r, self.at(u, v, r * 0.3), mat or GOLD, parent)



TOOTH_C, GAP_C = 0.34, 0.84   # tooth / gap centre of gear(), as a fraction of the pitch


def mesh_angle(alpha, teeth, gap):
    """Rotation that puts a tooth (or gap) centre of a gear() at angle alpha;
    give one gear gap=False and its partner (at alpha + pi) gap=True."""
    return alpha - TAU * (GAP_C if gap else TOOTH_C) / teeth


def rot_about(p, origin, axis, ang):
    return origin + Matrix.Rotation(ang, 3, Vector(axis).normalized()) @ (p - origin)


def sub_panel(p, u0, u1, v0=0.0, v1=1.0):
    return Panel(p.at(u0, v0), p.at(u1, v0), p.at(u1, v1), p.at(u0, v1))


def gold_frame(p, name, r=0.045, inset=0.0, parent=None, mat=None):
    """Thick bevelled frame around a panel."""
    q = sub_panel(p, inset, 1 - inset, inset, 1 - inset) if inset else p
    return curve_obj(name, [q.at(u, v, r * 0.4) for u, v in ((0, 0), (1, 0), (1, 1), (0, 1))],
                     mat or GOLD, r, parent, closed=True)


# Elder-futhark-like rune glyphs (unit square strokes) for glowing inlays.
RUNES = (
    [[(0.35, 0.1), (0.35, 0.9)], [(0.35, 0.55), (0.72, 0.75)], [(0.35, 0.78), (0.72, 0.98)]],
    [[(0.5, 0.05), (0.5, 0.95)], [(0.5, 0.6), (0.18, 0.92)], [(0.5, 0.6), (0.82, 0.92)]],
    [[(0.18, 0.05), (0.65, 0.5), (0.5, 0.8), (0.35, 0.5), (0.82, 0.05)]],
    [[(0.32, 0.05), (0.32, 0.95), (0.68, 0.75), (0.32, 0.52), (0.72, 0.05)]],
)


def rune(panel, name, glyph, radius=0.014, parent=None):
    """Glowing rune inlay filling a panel (pulse it via RUNE_EM)."""
    for gi, stroke in enumerate(RUNES[glyph % len(RUNES)]):
        glow(curve_obj(f"{name}{gi}", [panel.at(0.15 + 0.7 * u, 0.1 + 0.8 * v, 0.006)
                                       for u, v in stroke], RUNE, radius, parent))


# ----------------------------------------------------------------------------
# Camera, lights, render passes
# ----------------------------------------------------------------------------

class Rig:
    pass


def setup_scene(frame_w, frame_h, frame_cy):
    """Factorio camera + the standard lighting and Cycles settings.

    frame_w/frame_h: frame size in tiles; frame_cy: screen height (tiles, +up)
    of the frame centre relative to the entity origin. Returns a Rig with the
    lights (sun, sun_d, fill_d, bg) and the shadow-catcher ground."""
    scene = bpy.context.scene
    ppt = args.px_per_tile
    rig = Rig()
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(frame_w, frame_h)
    cam_data.clip_end = 100
    cam = bpy.data.objects.new("cam", cam_data)
    link(cam)
    el = math.radians(45)
    look = Vector((0, math.cos(el), -math.sin(el)))
    target = Vector((0, 0, frame_cy * math.sqrt(2)))
    cam.location = target - look * 30
    cam.rotation_euler = (math.radians(45), 0, 0)
    scene.camera = cam
    scene.render.resolution_x = round(frame_w * ppt)
    scene.render.resolution_y = round(frame_h * ppt)

    # key sun from the north-west like the vanilla sprites (shadows fall south-east)
    rig.sun_d = bpy.data.lights.new("sun", "SUN")
    rig.sun_d.energy = 4.6
    rig.sun_d.angle = math.radians(4)
    rig.sun = bpy.data.objects.new("sun", rig.sun_d)
    link(rig.sun)
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((0.7, -0.5, -0.9)).normalized()).to_euler()
    rig.fill_d = bpy.data.lights.new("fill", "SUN")
    rig.fill_d.energy = 1.1
    rig.fill_d.angle = math.radians(40)
    fill = bpy.data.objects.new("fill", rig.fill_d)
    link(fill)
    # fill from the front-left so the south faces read like the vanilla skirts
    fill.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((0.35, 0.75, -0.55)).normalized()).to_euler()

    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    rig.bg = world.node_tree.nodes["Background"]
    rig.bg.inputs["Color"].default_value = (0.30, 0.25, 0.22, 1)
    rig.bg.inputs["Strength"].default_value = 0.15

    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = dv.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.render.film_transparent = True
    scene.render.filter_size = 1.2
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    # shadow catcher ground (only rendered in the shadow pass)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=8)
    rig.ground = mesh_obj("ground", bm, BRONZE)
    rig.ground.is_shadow_catcher = True
    rig.ground.hide_render = True
    return rig


def render(path):
    """Render one still. Holds a lock so parallel jobs share the GPU in turn."""
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    lock = OUT.parent / ".gpu.lock"
    with open(lock, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            bpy.ops.render.render(write_still=True)
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def render_passes(rig, pose, extra_lights=(), name="entity"):
    """Main frames, glow frames (self-lit parts only, everything else held out)
    and a single shadow frame (machine invisible, casting onto the catcher)."""
    scene = bpy.context.scene
    lights = (rig.sun_d, rig.fill_d) + tuple(extra_lights)
    if args.save_blend:
        pose(0)
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{name}.blend"))

    frames = [int(f) for f in args.frame.split(",")] if args.preview else range(N)
    for f in frames:
        pose(f)
        render(OUT / f"main-{f:03d}.png")

    if not args.no_glow:
        rig.bg.inputs["Strength"].default_value = 0.0
        for f in frames:
            pose(f)
            for l in lights:
                l.energy = 0.0
            for o in scene.objects:
                if o.type in ("MESH", "CURVE"):
                    o.is_holdout = not o.get("glow", False)
            render(OUT / f"glow-{f:03d}.png")
        for o in scene.objects:
            if o.type in ("MESH", "CURVE"):
                o.is_holdout = False

    # Shadow: only the key light, lowered so the shadow reaches south-east
    # like the vanilla machines' shadows do.
    sun_energy = 4.6
    rig.ground.hide_render = False
    pose(0)
    for l in lights:
        l.energy = 0.0
    rig.sun_d.energy = sun_energy
    for o in scene.objects:
        if o is not rig.ground and o.type in ("MESH", "CURVE"):
            o.visible_camera = False
    rig.sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(
        Vector((1.0, -0.35, -0.75)).normalized()).to_euler()
    render(OUT / "shadow.png")
