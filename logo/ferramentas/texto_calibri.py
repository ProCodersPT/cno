"""Set 'CLUBE NATAÇÃO OLHÃO' in Calibri Bold as outlines, fitted to the original logo's wordmark."""
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = "/Applications/Microsoft Word.app/Contents/Resources/DFonts/Calibrib.ttf"
TEXT = "CLUBE NATAÇÃO OLHÃO"
CAP_TOP, BASELINE = 699.0, 739.0     # measured on the original (px)
INK_LEFT, INK_RIGHT = 46.0, 698.0    # measured ink extents (px)

tt = TTFont(FONT)
gs = tt.getGlyphSet()
cap = tt["OS/2"].sCapHeight
scale = (BASELINE - CAP_TOP) / cap  # px per font unit

blob = hb.Blob.from_file_path(FONT)
font = hb.Font(hb.Face(blob))
buf = hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties()
hb.shape(font, buf, {"kern": False, "liga": False})  # original was set without kerning (Word default)
order = tt.getGlyphOrder()
glyphs = [(order[i.codepoint], p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

def layout(track):
    x, out = 0.0, []
    for name, adv, xo, yo in glyphs:
        out.append((name, x + xo, yo))
        x += adv + track
    return out

def ink_bounds(items):
    lo, hi = None, None
    for name, x, y in items:
        bp = BoundsPen(gs); gs[name].draw(bp)
        if bp.bounds:
            lo = x + bp.bounds[0] if lo is None else min(lo, x + bp.bounds[0])
            hi = x + bp.bounds[2] if hi is None else max(hi, x + bp.bounds[2])
    return lo, hi

# Fit letter tracking, extra word space and x-offset to the measured letter edges (least squares).
RUNS = [(46, 75), (82, 103), (109, 141), (151, 179), (187, 209), (232, 264), (270, 306), (309, 338),
        (341, 377), (382, 410), (414, 450), (455, 491), (512, 548), (557, 578), (584, 614), (620, 656), (661, 697)]
import numpy as np
base = layout(0)
rows, rhs = [], []
spaces = 0
li = 0
for k, (name, x, y) in enumerate(base):
    if name == "space":
        spaces += 1
        continue
    bp = BoundsPen(gs); gs[name].draw(bp)
    for edge, meas in ((bp.bounds[0], RUNS[li][0]), (bp.bounds[2], RUNS[li][1] + 1)):
        # meas = dx + sx*(x + edge) + (sx*track)*k + (sx*word)*spaces   (linear in dx, sx, sx*track, sx*word)
        rows.append([1.0, x + edge, k, spaces]); rhs.append(meas)
    li += 1
sol, *_ = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)
resid = np.array(rows) @ sol - np.array(rhs)
dx, sx, track, word = sol[0], sol[1], sol[2] / sol[1], sol[3] / sol[1]
print(f"sx/sy {sx/scale:.3f} track {track:.1f}u word {word:.1f}u maxerr {abs(resid).max():.2f}px", file=sys.stderr)

def layout2():
    x, out = 0.0, []
    for name, adv, xo, yo in glyphs:
        out.append((name, x + xo, yo))
        x += adv + track + (word if name == "space" else 0)
    return out
items = layout2()

d = []
for name, x, y in items:
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    # font units are y-up; flip and place on the baseline
    gs[name].draw(TransformPen(pen, (sx, 0, 0, -scale, dx + x * sx, BASELINE - y * scale)))
    d.append(pen.getCommands())
print(f"tracking {track:.1f} units ({track*scale:.2f}px)", file=sys.stderr)
print("".join(d))
