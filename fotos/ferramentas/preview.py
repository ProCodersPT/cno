"""Grid previews (10% lines) of every source photo, 6 per sheet, to choose crops."""
import os, sys, json
from PIL import Image, ImageOps, ImageDraw, ImageFont

REPO = "/Users/vicentevaz/Documents/GitHub/cno/fotos"
WORK = os.path.dirname(os.path.abspath(__file__))
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)

def sources():
    out = []
    for d in ("originais", "facebook"):
        for f in sorted(os.listdir(os.path.join(REPO, d))):
            if f.startswith(".") or f.endswith(".md"):
                continue
            p = os.path.join(REPO, d, f)
            if f.lower().endswith(".heic"):
                p = os.path.join(WORK, "src", os.path.splitext(f)[0] + ".jpg")
            key = ("o:" if d == "originais" else "f:") + os.path.splitext(f)[0]
            out.append((key, p))
    return out

def load(p):
    im = Image.open(p)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")

if __name__ == "__main__":
    srcs = sources()
    json.dump(srcs, open(os.path.join(WORK, "sources.json"), "w"), indent=1)
    cell = 620
    for s in range(0, len(srcs), 6):
        sheet = Image.new("RGB", (cell * 3, cell * 2 + 40), "white")
        for k, (key, p) in enumerate(srcs[s:s + 6]):
            im = load(p)
            W, H = im.size
            im.thumbnail((cell - 20, cell - 50))
            w, h = im.size
            d = ImageDraw.Draw(im)
            for i in range(1, 10):
                d.line([(w * i / 10, 0), (w * i / 10, h)], fill=(255, 255, 0), width=1)
                d.line([(0, h * i / 10), (w, h * i / 10)], fill=(255, 255, 0), width=1)
                d.text((w * i / 10 + 2, 2), str(i), fill=(255, 255, 0), font=small)
                d.text((2, h * i / 10 + 1), str(i), fill=(255, 255, 0), font=small)
            x, y = (k % 3) * cell + 10, (k // 3) * cell + 40
            sheet.paste(im, (x, y))
            ImageDraw.Draw(sheet).text((x, y - 24), f"{key}  {W}x{H}", fill="black", font=font)
        sheet.save(os.path.join(WORK, f"grid_{s // 6:02d}.jpg"), quality=82)
    print(len(srcs))
