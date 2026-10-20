"""
Turn a Blender icon render into Factorio icons.

    blender -b --factory-startup -P blender/<entity>.py -- --icon --preview --frame 21 \
        --out graphics/generated/<entity>-icon
    .venv/bin/python blender/icon.py graphics/generated/<entity>-icon/icon.png --name <entity>

writes graphics/icons/<name>.png, a 64 px icon with its 32/16/8 px mipmaps
side by side (120x64, like vanilla's; Factorio picks the mipmaps up from the
image width), and graphics/technology/<name>.png at 256 px. Each size is
downsampled from the full render and sharpened a little more the smaller it
gets, so the silhouette stays crisp in the toolbar and in alt-mode.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("render", help="icon.png from a blender/<entity>.py --icon run")
ap.add_argument("--name", required=True)
ap.add_argument("--dest", default="graphics")
args = ap.parse_args()

src = Image.open(args.render).convert("RGBA")
# square crop around the content, with a hair of padding so nothing touches the edge
box = src.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
side = max(box[2] - box[0], box[3] - box[1])
side = round(side * 1.03)
cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
square = Image.new("RGBA", (side, side))
square.alpha_composite(src.crop(box), (round(side / 2 - (box[2] - box[0]) / 2),
                                       round(side / 2 - (box[3] - box[1]) / 2)))


def sized(px, sharpen):
    """Downsample in premultiplied alpha (no dark fringes), then sharpen."""
    r, g, b, a = square.split()
    pre = Image.merge("RGBA", (*(Image.composite(c, Image.new("L", c.size), a) for c in (r, g, b)), a))
    im = pre.resize((px, px), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1, percent=sharpen, threshold=1))
    alpha = im.getchannel("A")
    out = Image.new("RGBA", (px, px))
    for x in range(px):
        for y in range(px):
            al = alpha.getpixel((x, y))
            if al:
                c = rgb.getpixel((x, y))
                out.putpixel((x, y), (*(min(255, round(v * 255 / al)) for v in c), al))
    return outline(out)


def outline(im):
    """A soft dark rim behind the silhouette, like the vanilla icons' dark
    edges, so the icon separates from light inventory slots; plus a little
    contrast, which the downsampling washes out."""
    a = im.getchannel("A")
    rim = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    back = Image.new("RGBA", im.size, (24, 18, 14, 0))
    back.putalpha(rim.point(lambda v: v * 0.75))
    rgb = ImageEnhance.Contrast(im.convert("RGB")).enhance(1.12)
    front = Image.merge("RGBA", (*rgb.split(), a))
    back.alpha_composite(front)
    return back


dest = Path(args.dest)
(dest / "icons").mkdir(parents=True, exist_ok=True)
(dest / "technology").mkdir(parents=True, exist_ok=True)

strip = Image.new("RGBA", (120, 64))
x = 0
for px, sharpen in ((64, 60), (32, 90), (16, 110), (8, 120)):
    strip.paste(sized(px, sharpen), (x, 0))
    x += px
strip.save(dest / "icons" / f"{args.name}.png", optimize=True)
sized(256, 40).save(dest / "technology" / f"{args.name}.png", optimize=True)
print(f"wrote {dest}/icons/{args.name}.png and {dest}/technology/{args.name}.png")
