"""Crop, adjust and export every photo in the recipe to AVIF + JPG at several widths."""
import os, json, sys
import numpy as np
from PIL import Image, ImageFilter
from preview import sources, load
from receita import R

OUT = "/Users/vicentevaz/Documents/GitHub/cno/fotos/web"
WIDTHS = [480, 960, 1600, 2400]
RATIOS = {"3:2": 1.5, "4:3": 4 / 3, "16:9": 16 / 9, "4:5": .8, "1:1": 1.0}

def crop_box(W, H, ratio, cx, cy, s):
    r = RATIOS[ratio]
    w = min(W, H * r) * s
    h = w / r
    x0 = min(max(cx * W - w / 2, 0), W - w)
    y0 = min(max(cy * H - h / 2, 0), H - h)
    return tuple(int(round(v)) for v in (x0, y0, x0 + w, y0 + h))

def srgb_to_lin(x): return np.where(x <= .04045, x / 12.92, ((x + .055) / 1.055) ** 2.4)
def lin_to_srgb(x): return np.where(x <= .0031308, x * 12.92, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - .055)

def adjust(im, p):
    a = np.asarray(im).astype(np.float32) / 255
    lin = srgb_to_lin(a)
    # white balance: grey-world on mid-tones, blended by strength
    wb = p.get("wb", 0)
    if wb:
        Y = lin @ np.array([.2126, .7152, .0722])
        m = (Y > .05) & (Y < .8)
        means = lin[m].mean(0)
        gains = means.mean() / means
        lin = lin * (1 + wb * (gains - 1))
    if p.get("exp"):
        lin = lin * 2 ** p["exp"]
    a = np.clip(lin_to_srgb(np.clip(lin, 0, 1)), 0, 1)
    # gentle levels on luma: stretch 0.3% / 99.7% percentiles halfway
    Y = a @ np.array([.299, .587, .114])
    lo, hi = np.percentile(Y, [.3, 99.7])
    lo, hi = lo * .5, hi + (1 - hi) * .5
    a = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1)
    # shadow lift
    lift = p.get("lift", 0)
    if lift:
        Y = a @ np.array([.299, .587, .114])
        boost = lift * (1 - Y) ** 3
        a = np.clip(a + boost[..., None] * (1 - a) * .6, 0, 1)
    # mild S-curve contrast
    con = p.get("con", .12)
    a = a + con * (a - .5) * (1 - np.abs(2 * a - 1))
    # vibrance-like saturation (boost low-saturation pixels more)
    sat = p.get("sat", 1.08)
    Y = (a @ np.array([.299, .587, .114]))[..., None]
    chroma = np.abs(a - Y).max(-1, keepdims=True)
    k = 1 + (sat - 1) * (1 - np.clip(chroma * 2, 0, 1))
    a = np.clip(Y + (a - Y) * k, 0, 1)
    return Image.fromarray((a * 255 + .5).astype(np.uint8))

def main(only=None):
    src = dict(sources())
    manifest = []
    for key, name, crops, adj, credit, alt in R:
        if only and name not in only:
            continue
        im = load(src[key])
        W, H = im.size
        base = im if credit else adjust(im, adj)  # photographers already graded their work
        os.makedirs(os.path.join(OUT, name), exist_ok=True)
        entry = {"nome": name, "origem": key, "alt": alt, "credito": credit, "recortes": []}
        for ratio, cx, cy, s in crops:
            box = crop_box(W, H, ratio, cx, cy, s)
            c = base.crop(box)
            cw = c.size[0]
            widths = [w for w in WIDTHS if w <= cw] or [cw]
            if cw not in widths and cw < WIDTHS[-1] and cw > widths[-1] * 1.15:
                widths.append(cw)
            tag = ratio.replace(":", "x")
            files = []
            for w in widths:
                h = round(w * c.size[1] / cw)
                r = c.resize((w, h), Image.LANCZOS) if w != cw else c
                if w < cw:
                    r = r.filter(ImageFilter.UnsharpMask(radius=.8, percent=40, threshold=2))
                stem = os.path.join(OUT, name, f"{name}-{tag}-{w}")
                r.save(stem + ".avif", quality=58, speed=4)
                r.save(stem + ".jpg", quality=82, optimize=True, progressive=True)
                files.append({"w": w, "h": h})
            entry["recortes"].append({"proporcao": ratio, "tamanhos": files})
        manifest.append(entry)
        print(name, [(c["proporcao"], c["tamanhos"][-1]["w"]) for c in entry["recortes"]], flush=True)
    if not only:
        json.dump(manifest, open(os.path.join(OUT, "fotos.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1:] or None)
