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
args = ap.parse_args()

src = Path(args.dir)


def load(p):
    im = Image.open(p).convert("RGBA")
    k = args.ppt / args.render_ppt
    w = round(im.width * k)
    h = round(im.height * k)
    return im.resize((w, h), Image.LANCZOS)


dest = Path(args.dest)


def sheet(prefix, suffix):
    frames = sorted(src.glob(f"{prefix}-*.png"))
    if not frames:
        return
    imgs = [load(p) for p in frames]
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
