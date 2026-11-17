"""Build the static site: expand image macros in src/*.html into responsive <picture> tags.

Macro:  [[img nome proporcao sizes classe [eager]]]
  e.g.  [[img sair-da-piscina-touca-rosa 3x2 (min-width:900px)50vw,100vw hero-img eager]]
Output: ./<page>.html  (the site root is the repo root, served as-is on Netlify)
"""
import hashlib, json, re, pathlib

ROOT = pathlib.Path(__file__).parent
FOTOS = json.loads((ROOT / "fotos/web/fotos.json").read_text())
INDEX = {e["nome"]: e for e in FOTOS}
WEB = "fotos/web"


def picture(nome, prop, sizes, cls="", eager=False):
    e = INDEX[nome]
    rec = next(r for r in e["recortes"] if r["proporcao"].replace(":", "x") == prop)
    tam = rec["tamanhos"]
    base = f"{WEB}/{nome}/{nome}-{prop}"
    avif = ", ".join(f"{base}-{t['w']}.avif {t['w']}w" for t in tam)
    jpg = ", ".join(f"{base}-{t['w']}.jpg {t['w']}w" for t in tam)
    mid = min(tam, key=lambda t: abs(t["w"] - 960))
    alt = e["alt"].replace('"', "&quot;")
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    cred = f' data-credito="{e["credito"]}"' if e.get("credito") else ""
    return (f'<picture class="{cls}"{cred}>'
            f'<source type="image/avif" srcset="{avif}" sizes="{sizes}">'
            f'<img src="{base}-{mid["w"]}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{mid["w"]}" height="{mid["h"]}" alt="{alt}" {load}></picture>')


MACRO = re.compile(r"\[\[img\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+(\S+))?(?:\s+(eager))?\]\]")


INCLUDE = re.compile(r"\[\[include\s+(\S+)\]\]")


def expand(html, page):
    html = INCLUDE.sub(lambda m: (ROOT / "src/partials" / f"{m[1]}.html").read_text(), html)
    html = html.replace("[[home]]", "" if page == "index.html" else "./")
    # version the stylesheet and the script by content, so visitors never get a stale cached copy
    for asset in ("assets/css/style.css", "assets/js/main.js"):
        v = hashlib.sha1((ROOT / asset).read_bytes()).hexdigest()[:8]
        html = html.replace(f'"{asset}"', f'"{asset}?v={v}"')
    return MACRO.sub(lambda m: picture(m[1], m[2], m[3], m[4] or "", bool(m[5])), html)


if __name__ == "__main__":
    for src in sorted((ROOT / "src").glob("*.html")):
        out = ROOT / src.name
        out.write_text(expand(src.read_text(), src.name))
        left = MACRO.findall(out.read_text())
        print(f"{src.name} -> {out.name}" + (f"  (macros por expandir: {left})" if left else ""))
