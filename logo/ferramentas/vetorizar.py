"""Vectorize the CNO logo into flat-colour SVG paths.

1. Shape: ink vs paper is decided by unmixing each pixel against white (robust to anti-aliasing).
2. Colour: each ink pixel gets its colour from the nearest *interior* pixel, so JPEG ringing on
   the rims never produces fringes.
3. Each colour layer is traced with potrace into Bezier curves.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
import potrace

SRC, OUT = sys.argv[1], sys.argv[2]
UP = 4
TEXT_Y = 680  # original-pixel row where the wordmark band starts

BLUES = {"dark": (0, 104, 157), "mid": (2, 140, 205), "light": (3, 161, 226)}
NAVY = (10, 9, 47)
WHITES = [(252, 253, 253), (193, 243, 249)]
FILL = {"dark": "#00689D", "mid": "#028CCD", "light": "#03A1E2", "navy": "#0A0A2F"}

im = Image.open(SRC).convert("RGB")
w, h = im.size
im = im.filter(ImageFilter.MedianFilter(3))
a = np.asarray(im.resize((w * UP, h * UP), Image.LANCZOS)).astype(np.float32)
H, W = a.shape[:2]
ty = TEXT_Y * UP

def ink_mask(a, inks):
    """True where the pixel is more ink than paper, testing every ink-vs-white blend."""
    best = np.full(a.shape[:2], np.inf, np.float32)
    ink = np.zeros(a.shape[:2], bool)
    for c in inks:
        for wcol in WHITES:
            c_, w_ = np.array(c, np.float32), np.array(wcol, np.float32)
            v = c_ - w_
            t = np.clip(((a - w_) @ v) / float(v @ v), 0, 1)
            res = ((a - (w_ + t[..., None] * v)) ** 2).sum(-1)
            better = res < best
            best = np.where(better, res, best)
            ink = np.where(better, t >= 0.5, ink)
    return ink

def clean(m, min_area):
    m = ndimage.binary_opening(m, iterations=2)
    m = ndimage.binary_closing(m, iterations=3)
    lbl, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lbl, range(1, n + 1))
        m = np.isin(lbl, 1 + np.where(sizes >= min_area)[0])
    holes = ndimage.binary_fill_holes(m) & ~m
    lbl, n = ndimage.label(holes)
    if n:
        sizes = ndimage.sum(holes, lbl, range(1, n + 1))
        m = m | np.isin(lbl, 1 + np.where(sizes < min_area)[0])
    return m

layers = {}

# --- Swimmers + lanes (blue) ---
top = a[:ty]
ink = clean(ink_mask(top, list(BLUES.values())), 80 * UP)
names = list(BLUES)
# Classify by luma, not RGB: the JPEG stores colour at half resolution, so hue/chroma bleeds
# ~7px past every edge while luma stays sharp. Luma: dark ~79, mid ~106, light ~121.
luma = ndimage.median_filter(top @ np.array([0.299, 0.587, 0.114], np.float32), size=5)
lab = np.digitize(luma, [93, 114])  # 0 dark, 1 mid, 2 light
# Rims blend into the white outline (luma rises), so take colour from >=2.5px inside and propagate.
depth = ndimage.distance_transform_edt(ink)
interior = depth > 2.5 * UP
_, (iy, ix) = ndimage.distance_transform_edt(~interior, return_indices=True)
lab = lab[iy, ix]
votes = np.stack([ndimage.uniform_filter((lab == i).astype(np.float32), 25) for i in range(3)])
lab = votes.argmax(0)
# Regions enclosed by the white outlines are flat in the original: give each one the majority
# colour of its deep pixels. Regions that really mix colours (a lane touching a leg) keep per-pixel.
comp, ncomp = ndimage.label(ink)
for k in range(1, ncomp + 1):
    sel = comp == k
    deep = sel & interior  # include thin parts (lanes) so mixed regions are detected
    counts = np.bincount(lab[deep if deep.any() else sel], minlength=3)
    if counts.max() >= 0.92 * counts.sum():
        lab[sel] = counts.argmax()
for i, n in enumerate(names):
    m = np.zeros((H, W), bool)
    m[:ty] = clean(ink & (lab == i), 120 * UP)
    layers[n] = m

# --- Wordmark (navy) ---
m = np.zeros((H, W), bool)
m[ty:] = clean(ink_mask(a[ty:], [NAVY]), 10 * UP)
layers["navy"] = m

def path_d(mask, scale):
    plist = potrace.Bitmap(~mask).trace(  # potracer: False = filled
        turdsize=30, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0, opticurve=True, opttolerance=0.4)
    f = lambda p: f"{p.x*scale:.2f} {p.y*scale:.2f}"
    out = []
    for curve in plist:
        out.append(f"M{f(curve.start_point)}")
        for seg in curve.segments:
            if seg.is_corner:
                out.append(f"L{f(seg.c)}L{f(seg.end_point)}")
            else:
                out.append(f"C{f(seg.c1)} {f(seg.c2)} {f(seg.end_point)}")
        out.append("Z")
    return "".join(out)

paths = [f'<path fill="{FILL[n]}" fill-rule="evenodd" d="{path_d(layers[n], 1 / UP)}"/>'
         for n in ["dark", "mid", "light", "navy"]]
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
       f'aria-label="Clube Natação de Olhão">' + "".join(paths) + "</svg>")
open(OUT, "w").write(svg)
print("bytes", len(svg))
