"""
Put a rendered frame next to vanilla sprites at in-game scale for review.

    .venv/bin/python blender/compare.py graphics/generated/distillery/main-000.png \
        --vanilla base/graphics/entity/chemical-plant/chemical-plant.png:220:292 \
        --tiles 3 --out /tmp/cmp.png

Renders are 128 px per tile (stitch.py halves them); vanilla "hr" sprites are
64 px per tile at scale 0.5. Prints the content bounding boxes and the Lua
`scale` that would make the render's content as wide as the vanilla one.
Shows a 2x zoomed panel (detail) and a 1x panel (what players see at zoom 1).
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

DATA = Path.home() / ".local/share/Steam/steamapps/common/Factorio/data"

ap = argparse.ArgumentParser()
ap.add_argument("render", help="a main-NNN.png from a blender/<entity>.py run")
ap.add_argument("--vanilla", action="append", default=[],
                help="path (relative to Factorio data/) :frame_w:frame_h of frame 0")
ap.add_argument("--extra", action="append", default=[],
                help="another image already at 64 px/tile (e.g. an old mod sprite)")
ap.add_argument("--tiles", type=float, default=3, help="footprint size, draws the box")
ap.add_argument("--out", required=True)
args = ap.parse_args()


def content_bbox(im):
    return im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()


ren = Image.open(args.render).convert("RGBA")
ren = ren.resize((ren.width // 2, ren.height // 2), Image.LANCZOS)   # -> 64 px/tile
imgs = [("render", ren)]
for spec in args.vanilla:
    path, w, h = spec.split(":")
    sheet = Image.open(DATA / path).convert("RGBA")
    imgs.append((Path(path).stem, sheet.crop((0, 0, int(w), int(h)))))
for p in args.extra:
    imgs.append((Path(p).stem, Image.open(p).convert("RGBA")))

rb = content_bbox(ren)
print(f"render content bbox {rb} -> {rb[2] - rb[0]}x{rb[3] - rb[1]} px")
for name, im in imgs[1:]:
    b = content_bbox(im)
    w, h = b[2] - b[0], b[3] - b[1]
    print(f"{name} content bbox {b} -> {w}x{h} px; Lua scale to match width: "
          f"{0.5 * w / (rb[2] - rb[0]):.3f}, height: {0.5 * h / (rb[3] - rb[1]):.3f}")

T = 64
pad = 24
cell_w = max(im.width for _, im in imgs) + pad
cell_h = max(im.height for _, im in imgs) + pad
panel = Image.new("RGBA", (cell_w * len(imgs), cell_h), (96, 88, 72, 255))
d = ImageDraw.Draw(panel)
for x in range(0, panel.width, T // 2):
    d.line([(x, 0), (x, panel.height)], fill=(86, 79, 65, 255))
for y in range(0, panel.height, T // 2):
    d.line([(0, y), (panel.width, y)], fill=(86, 79, 65, 255))
for k, (name, im) in enumerate(imgs):
    cx, cy = k * cell_w + cell_w // 2, cell_h // 2
    panel.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))
    half = args.tiles * T / 2
    d.rectangle([cx - half, cy - half, cx + half, cy + half], outline=(0, 255, 0, 255))
    d.text((k * cell_w + 4, 4), name, fill=(240, 235, 220, 255))
zoom2 = panel.resize((panel.width * 2, panel.height * 2), Image.LANCZOS)
zoom1 = panel.resize((panel.width // 2, panel.height // 2), Image.LANCZOS)
out = Image.new("RGBA", (zoom2.width, zoom2.height + zoom1.height + 8), (40, 40, 40, 255))
out.alpha_composite(zoom2, (0, 0))
out.alpha_composite(zoom1, (0, zoom2.height + 8))
out.save(args.out)
print("wrote", args.out)
