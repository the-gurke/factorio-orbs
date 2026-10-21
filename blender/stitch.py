"""
Turn the raw Blender renders into Factorio sprite sheets.

Downsamples the frames to 64 px per tile and packs them into a sheet, plus a
Factorio-style shadow sprite (black, density in alpha).

    .venv/bin/python blender/stitch.py graphics/generated/conjuration-machine \
        --name conjuration-machine --cols 8
"""

import argparse
import math
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("--name", required=True)
ap.add_argument("--cols", type=int, default=8)
ap.add_argument("--render-ppt", type=int, default=128)
ap.add_argument("--ppt", type=float, default=64)
ap.add_argument("--dest", default="graphics")
ap.add_argument("--crop", action="store_true",
                help="trim main and glow frames to the union of their opaque pixels "
                     "(keeps the centre on a whole pixel) and print the Lua shift correction")
args = ap.parse_args()

src = Path(args.dir)


def load(p):
    im = Image.open(p).convert("RGBA")
    k = args.ppt / args.render_ppt
    w = round(im.width * k)
    h = round(im.height * k)
    return im.resize((w, h), Image.LANCZOS)


dest = Path(args.dest)


def crop_box():
    """Union bbox of every main and glow frame, grown so the crop's centre
    sits a whole number of pixels from the frame's centre."""
    box = None
    for p in sorted(src.glob("main-*.png")) + sorted(src.glob("glow-*.png")):
        im = load(p)
        b = im.getchannel("A").point(lambda a: 255 if a > 2 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                         max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box
    W, H = im.size
    if (x0 + x1 - W) % 2:
        x1 += 1
    if (y0 + y1 - H) % 2:
        y1 += 1
    dx, dy = (x0 + x1 - W) / 2, (y0 + y1 - H) / 2
    print(f"crop {x1 - x0}x{y1 - y0}: add shift {{{dx / args.ppt:g}, {dy / args.ppt:g}}} "
          f"tiles (at {args.ppt:g} px per tile) to the uncropped frame's shift")
    return x0, y0, x1, y1


CROP = crop_box() if args.crop else None


def sheet(prefix, suffix):
    frames = sorted(src.glob(f"{prefix}-*.png"))
    if not frames:
        return
    imgs = [load(p) for p in frames]
    if CROP:
        imgs = [im.crop(CROP) for im in imgs]
    w, h = imgs[0].size
    rows = math.ceil(len(imgs) / args.cols)
    cols = min(args.cols, len(imgs))
    out = Image.new("RGBA", (w * cols, h * rows))
    for i, im in enumerate(imgs):
        out.paste(im, ((i % cols) * w, (i // cols) * h))
    out.save(dest / f"{args.name}-{suffix}.png", optimize=True)
    print(f"{suffix}: {len(imgs)} frames of {w}x{h}, sheet {out.size}")


sheet("main", "animation")
sheet("glow", "glow")

shadow = src / "shadow.png"
if shadow.exists():
    sh = load(shadow)
    # Factorio shadow sprites: black, density in alpha
    a = sh.getchannel("A")
    out = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    out.putalpha(a)
    out.save(dest / f"{args.name}-shadow.png", optimize=True)
    print(f"shadow {sh.size}")
