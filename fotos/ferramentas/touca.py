"""Realistic studio render of the old CNO cap, rebuilt from measurements of the photo.

Coordinates: "photo px" = original photo pixels, with the print levelled (rotated -3.1 deg
about (575, 880)). Everything is rendered at K output px per photo px.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

OUT = sys.argv[1]
K = 1.45                                  # output px per photo px
SSA = 2                                   # supersampling for masks
PINK = np.array([250, 60, 112], np.float32)
NAVY = np.array([48, 80, 166], np.float32)
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_R = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

# ------------------------------------------------------------------ canvas
X0, Y0, X1, Y1 = 40, 60, 1990, 1700       # photo-px window rendered
W, H = int((X1 - X0) * K), int((Y1 - Y0) * K)
def P(x, y, ss=1):                        # photo px -> canvas px
    return ((x - X0) * K * ss, (y - Y0) * K * ss)

# ------------------------------------------------------------------ cap outline (measured)
cap = np.load("cap.npy")
rows = np.nonzero(cap.any(1))[0]
top = rows.min()
CX = 1016.0
YS = 1545                                  # sides measured down to here; below it the rim waves
ry = np.arange(top, YS + 1)
hw = np.array([(np.nonzero(cap[y])[0].max() - np.nonzero(cap[y])[0].min()) / 2 for y in ry], float)
ext = 40
hw2 = np.concatenate([-hw[1:ext + 1][::-1], hw])
hw = np.maximum(ndimage.gaussian_filter1d(hw2, 5, mode="nearest")[ext:], 0)
# bottom rim: symmetric smooth wave fitted to the measured bottom edge
# measured bottom edge, mirrored left/right and smoothed
hb = hw[-1]
qs = np.linspace(-1, 1, 201)
bx = CX + qs * (hb - 6)
by = np.array([np.nonzero(cap[:, int(round(x))])[0].max() for x in bx], float)
by = (by + by[::-1]) / 2
by = ndimage.gaussian_filter1d(by, 6, mode="nearest")
yedge = by[0]
by = yedge + (by - yedge) * 0.8                # keep 80% of the wave
uu = qs[::-1]; byf = by[::-1]
print("corner y", round(yedge, 1), "centre y", round(by[100], 1), "min", round(by.min(), 1))
right = [(CX + h, y) for y, h in zip(ry, hw)] + [(CX + hw[-1], yedge)]
bottom = [(CX + q * hw[-1], b) for q, b in zip(uu, byf)]
left = [(CX - hw[-1], yedge)] + [(CX - h, y) for y, h in zip(ry[::-1], hw[::-1])]
outline = right + bottom + left
hv = hw; YB = yedge
m = Image.new("L", (W * SSA, H * SSA), 0)
ImageDraw.Draw(m).polygon([P(x, y, SSA) for x, y in outline], fill=255)
mm = np.asarray(m).astype(np.float32) / 255
mm = ndimage.gaussian_filter(mm, 4 * K * SSA)            # soften the corners slightly
mm = (mm > 0.5).astype(np.uint8) * 255
alpha = np.asarray(Image.fromarray(mm).resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
inside = alpha > 0.5

# ------------------------------------------------------------------ height field (dome + rolled rim)
d = ndimage.distance_transform_edt(inside)
capw = inside.any(0).sum()
# A cap lying flat: almost flat sheet, edges rounded evenly all round (dome and rim band alike),
# plus a very gentle overall swell so it doesn't look like paper.
d_s = ndimage.gaussian_filter(d, 3 * K)
edge = 14 * K * (1 - np.exp(-d_s / (22 * K)))
swell = ndimage.gaussian_filter(inside.astype(np.float32), 0.22 * capw) * 0.035 * capw
h = (edge + swell) * inside
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
yb_px = P(0, YB)[1]
band = 26 * K                                               # rolled bottom rim
colbot = np.where(inside.any(0), H - 1 - np.argmax(inside[::-1], axis=0), 0).astype(np.float32)
colbot = ndimage.gaussian_filter1d(colbot, 20)
rim = np.exp(-((colbot[None, :] - band * 0.9 - yy) ** 2) / (2 * (band * 0.45) ** 2)) * inside
h = h + rim * band * 0.0
h = ndimage.gaussian_filter(h, 2.0 * K)
gy, gx = np.gradient(h)
N = np.dstack([-gx, -gy, np.ones_like(h)])
N /= np.linalg.norm(N, axis=2, keepdims=True)
L = np.array([-0.45, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0, 0, 1.0])
Hv = (L + V) / np.linalg.norm(L + V)
ndl = np.clip(N @ L, 0, 1)
ndh = np.clip(N @ Hv, 0, 1)
nz = N[..., 2]
diffuse = 0.76 + 0.36 * ndl
spec = 0.20 * ndh ** 36 + 0.05 * ndh ** 6                   # silicone: soft gloss + sheen
edge_ao = 1 - 0.22 * (1 - nz) ** 1.3                        # darker where the surface turns away
# gentle large-scale light falloff (studio key light from top-left)
fall = 1 + 0.06 * (1 - (xx / W + yy / H))

# ------------------------------------------------------------------ print (levelled photo px)
frac = np.asarray(Image.open("frac_rot.png")).astype(np.float32) / 255
ink = frac > 0.45
lbl, n = ndimage.label(ink, structure=np.ones((3, 3)))
ids = [i + 1 for i, s_ in enumerate(ndimage.find_objects(lbl))
       if (s_[0].start < 990 and s_[0].stop > 430 and s_[1].start > 630 and s_[1].stop < 1400)
       or (s_[0].start > 1290 and s_[0].stop < 1420 and s_[1].start > 1270 and s_[1].stop < 1630)]
sym = np.isin(lbl, ids)                                    # swimmer + lanes
LANES = [  # (y_bar_top, y_bar_bottom, tooth_h, x0, x1, tooth_w, period, first_tooth_x)
    (632, 640, 6, 651, 904, 9, 19.6, 667 - 19.6),
    (632, 640, 6, 1119, 1231, 9, 19.6, 1119 + 3),
    (632, 640, 6, 1296, 1371, 9, 19.6, 1296 + 6),
    (757, 767, 9, 660, 1052, 16, 32.5, 684 - 32.5),
    (757, 767, 9, 1246, 1383, 16, 32.5, 1268 - 32.5),
    (952, 980, 22, 646, 1300, 26, 58.1, 688 - 58.1),
]
erase = np.zeros_like(sym)
for yt, ybt, th, x0, x1, tw, per, fx in LANES:
    erase[int(yt - th - 10): int(ybt + 5), int(x0 - 3): int(x1 + 2)] = True
erase[981:1000, 1285:1400] = True               # corner wedge flush with the bottom of the bar
sym = sym & ~erase
# smooth swimmer edges at high resolution
soft = frac * ndimage.binary_dilation(sym, iterations=2) * ~erase   # keep the anti-aliasing
big = Image.fromarray((np.clip(soft, 0, 1) * 255).astype(np.uint8)).resize(
    (sym.shape[1] * 4, sym.shape[0] * 4), Image.BICUBIC)
bigf = ndimage.gaussian_filter(np.asarray(big).astype(np.float32) / 255, 4.0)
thr = np.full(bigf.shape, 0.5, np.float32)
thr[1290 * 4:, :] = 0.66                      # small "aqualoja" text: tighter, keeps the counters open
big = Image.fromarray(((bigf > thr) * 255).astype(np.uint8))

print_l = Image.new("L", (W * SSA, H * SSA), 0)
# paste swimmer: map photo px (levelled) -> canvas
sx = K * SSA / 4
swim = big.resize((int(big.width * sx), int(big.height * sx)), Image.LANCZOS)
ox, oy = P(0, 0, SSA)
print_l.paste(255, (int(ox), int(oy)), swim)
dr = ImageDraw.Draw(print_l)
for yt, ybt, th, x0, x1, tw, per, fx in LANES:
    dr.rectangle([P(x0, yt, SSA), P(x1, ybt, SSA)], fill=255)
    x = fx
    while x <= x1:
        a0, a1 = max(x, x0), min(x + tw, x1)
        if a1 - a0 > 2:
            dr.rectangle([P(a0, yt - th, SSA), P(a1, yt, SSA)], fill=255)
        x += per
# join the redrawn bottom bar to the swimmer's corner wedge (no seam)
dr.rectangle([P(1296, 952, SSA), P(1322, 980, SSA)], fill=255)
dr.rectangle([P(1280, 980.5, SSA), P(1410, 1000, SSA)], fill=0)   # straight bottom edge under the corner

def fit_text(txt, font_path, x0, x1, top, base, cap_char):
    """Natural letter spacing; scale x and y independently so the ink spans x0..x1 and
    cap_char spans top..base (photo px). Matches a slightly condensed print exactly."""
    S0 = 600
    f = ImageFont.truetype(font_path, S0)
    tmp = Image.new("L", (int(f.getlength(txt)) + 400, S0 * 3), 0)
    tb = 200
    ImageDraw.Draw(tmp).text((tb, S0 * 2), txt, font=f, fill=255, anchor="ls")
    bb = tmp.getbbox()
    cb = f.getbbox(cap_char, anchor="ls")              # cap_char height above the baseline
    sy = (base - top) * K * SSA / (cb[3] - cb[1])
    sx = (x1 - x0) * K * SSA / (bb[2] - bb[0])
    part = tmp.crop((bb[0], 0, bb[2], tmp.height))
    part = part.resize((max(1, int(part.width * sx)), max(1, int(part.height * sy))), Image.LANCZOS)
    X, Yb = P(x0, base, SSA)
    print_l.paste(255, (int(X), int(Yb - (S0 * 2) * sy)), part)
    return round(sx / sy, 3)

print(fit_text("C. N. OLHÃO", FONT_B, 632, 1408, 1048, 1147, "N"))
# "aqualoja" uses a single-storey rounded face that is not installed: it is traced from the photo

print_l = print_l.filter(ImageFilter.MaxFilter(3))      # ink spread, like the real print
pr = np.asarray(print_l.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
# printed ink sits on the surface: rotate the print to the cap's own frame (cap is upright,
# print was levelled) - nothing to do; just keep it inside the cap
pr *= np.clip((d - 6 * K) / (4 * K), 0, 1)

# ------------------------------------------------------------------ shade
base = PINK[None, None] * (1 - pr[..., None]) + NAVY[None, None] * pr[..., None]
col = base * (diffuse * edge_ao * fall)[..., None]
gloss = spec * (1 - 0.6 * pr)
col = col + 255 * gloss[..., None] * np.array([1.0, 0.93, 0.97])
# fine silicone grain so it doesn't look like vector art
rng = np.random.default_rng(7)
grain = ndimage.gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), 0.8) * 2.2
col = np.clip(col + grain[..., None], 0, 255)

rgba = np.dstack([col, alpha * 255]).astype(np.uint8)
cap_img = Image.fromarray(rgba, "RGBA")

# ------------------------------------------------------------------ outputs: plain + with shadow
bbox = cap_img.getbbox()
pad = int(0.06 * (bbox[2] - bbox[0]))
crop = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + int(pad * 1.6))
plain = cap_img.crop(crop)
plain.save(OUT + ".png")

sh = Image.new("L", cap_img.size, 0)
a8 = Image.fromarray((alpha * 255).astype(np.uint8))
sh.paste(a8, (int(10 * K), int(16 * K)))
sh = sh.filter(ImageFilter.GaussianBlur(22 * K))
contact = Image.new("L", cap_img.size, 0)
cd = ImageDraw.Draw(contact)
x_l, x_r = P(CX - hv[-1] * 0.98, 0)[0], P(CX + hv[-1] * 0.98, 0)[0]
cd.ellipse([x_l, yb_px - 6 * K, x_r, yb_px + 10 * K], fill=255)
contact = contact.filter(ImageFilter.GaussianBlur(7 * K))
shadow_a = np.clip(np.asarray(sh) * 0.30 + np.asarray(contact) * 0.45, 0, 255).astype(np.uint8)
shadow = Image.fromarray(np.dstack([np.full_like(shadow_a, 20), np.full_like(shadow_a, 10),
                                    np.full_like(shadow_a, 30), shadow_a]), "RGBA")
withsh = Image.alpha_composite(shadow, cap_img).crop(crop)
withsh.save(OUT + "-sombra.png")
print("size", plain.size)
