"""Single-file preview of the home page for opening on a phone (everything inlined).

Output: _telemovel/cno-site.html  (gitignored; not used by the real site)
Photos are re-encoded to 720 px JPG, the hero uses a light 540x960 video.
Links to the other pages point to sections of this page instead.
"""
import base64, io, re, pathlib, subprocess
from PIL import Image

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "_telemovel"
OUT.mkdir(exist_ok=True)


def b64(data, mime):
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def jpg_uri(path, maxw=720, q=74):
    im = Image.open(path).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(maxw * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return b64(buf.getvalue(), "image/jpeg"), im.size


html = (ROOT / "index.html").read_text()

# ---- styles and script inline
css = (ROOT / "assets/css/style.css").read_text()
poster_uri, _ = jpg_uri(ROOT / "fotos/web/video/mergulho-9x16-poster.jpg", 540, 70)
css = css.replace('url("../../fotos/web/video/mergulho-16x9-poster.jpg")', f'url("{poster_uri}")')
html = re.sub(r'<link rel="stylesheet" href="assets/css/style\.css[^"]*">', lambda m: f"<style>{css}</style>", html)
js = (ROOT / "assets/js/main.js").read_text()
js = js.replace("video.src = tall ? video.dataset.srcTall : video.dataset.srcWide;", "video.src = video.dataset.srcTall;")
html = re.sub(r'<script src="assets/js/main\.js[^"]*" defer></script>',
              lambda m: '<script>document.addEventListener("DOMContentLoaded", () => {\n' + js + "\n});</script>", html)

# ---- responsive pictures -> one inline JPG each
PIC = re.compile(r'<picture class="([^"]*)"(?: data-credito="[^"]*")?><source type="image/avif" srcset="[^"]*" sizes="[^"]*">'
                 r'<img src="[^"]*" srcset="([^"]*)" sizes="[^"]*" width="\d+" height="\d+" alt="([^"]*)"[^>]*></picture>')


def pic(m):
    cands = [(int(w[:-1]), u) for u, w in (c.strip().split(" ") for c in m[2].split(","))]
    fit = [c for c in cands if c[0] <= 960] or cands
    w, url = max(fit)
    uri, (W, H) = jpg_uri(ROOT / url)
    return f'<picture class="{m[1]}"><img src="{uri}" width="{W}" height="{H}" alt="{m[3]}"></picture>'


html, n = PIC.subn(pic, html)
print("fotos embutidas:", n)

# ---- the cap (transparent): one WebP
html = re.sub(r'<source type="image/avif" srcset="assets/img/touca-antiga-800\.avif[^>]*>', "", html)
cap = b64((ROOT / "assets/img/touca-antiga-800.webp").read_bytes(), "image/webp")
html = re.sub(r'src="assets/img/touca-antiga-1600\.png" srcset="[^"]*"', f'src="{cap}"', html)

# ---- logos
for name in ("cno-simbolo.svg", "cno-logo-fundo-escuro.svg"):
    uri = b64((ROOT / "assets/img" / name).read_bytes(), "image/svg+xml")
    html = html.replace(f"assets/img/{name}", uri)

# ---- hero video
vid = b64((OUT / "mergulho-movel.mp4").read_bytes(), "video/mp4")
html = re.sub(r'poster="fotos/web/video/mergulho-16x9-poster\.jpg[^"]*"', lambda m: f'poster="{poster_uri}"', html)
html = re.sub(r'data-src-wide="fotos/web/video/mergulho-16x9\.mp4[^"]*"', 'data-src-wide=""', html)
html = re.sub(r'data-src-tall="fotos/web/video/mergulho-9x16\.mp4[^"]*"', lambda m: f'data-src-tall="{vid}"', html)
html = re.sub(r'data-poster-tall="fotos/web/video/mergulho-9x16-poster\.jpg[^"]*"', "", html)

# ---- other pages are not in this file: point to sections here
html = re.sub(r'href="historia\.html(#[^"]*)?"', 'href="#percurso"', html)
html = html.replace('href="inscricoes.html"', 'href="#treinar"')
html = re.sub(r'<meta property="og:image"[^>]*>\n?', "", html)

left = sorted(set(re.findall(r'(?:src|href|srcset|poster)="((?:fotos|assets)/[^"]*)"', html)))
assert not left, left
out = OUT / "cno-site.html"
out.write_text(html)
print(out, f"{out.stat().st_size / 1e6:.1f} MB")
