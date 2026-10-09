"""Убирает белый фон у сгенерированных иллюстраций и подрезает их по содержимому."""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    marker = (255, 0, 255)
    work = im.copy()
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1),
                 (0, h // 2), (w - 1, h // 2)]:
        if work.getpixel(seed) != marker:
            ImageDraw.floodfill(work, seed, marker, thresh=40)
    bg = ImageChops.difference(work, Image.new("RGB", (w, h), marker)).convert("L")
    alpha = bg.point(lambda p: 0 if p < 8 else 255).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.copy()
    rgba.putalpha(alpha)
    bbox = alpha.point(lambda p: 255 if p > 20 else 0).getbbox()
    rgba = rgba.crop(bbox)
    side = max(rgba.size)
    pad = int(side * 0.03)
    canvas = Image.new("RGBA", (side + 2 * pad, side + 2 * pad), (255, 255, 255, 0))
    canvas.paste(rgba, ((canvas.width - rgba.width) // 2, (canvas.height - rgba.height) // 2), rgba)
    canvas = canvas.resize((900, 900), Image.LANCZOS)
    canvas.save(dst)
    print(dst, bbox, im.size)
