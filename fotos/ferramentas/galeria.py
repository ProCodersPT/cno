"""Galeria de revisão: todas as fotos enviadas, e onde (ou se) cada uma aparece no site.

Gera _partilha/galeria-fotos/index.html (+ miniaturas dos originais) a partir de
receita.py, fotos/originais, fotos/facebook e das páginas em src/.
Uso: python3 fotos/ferramentas/galeria.py
"""
import html, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from receita import R  # noqa: E402

OUT = RAIZ / "_partilha" / "galeria-fotos"
MINI = OUT / "originais"
MINI.mkdir(parents=True, exist_ok=True)
PAGINAS = {"index.html": "Início", "historia.html": "História", "inscricoes.html": "Inscrições"}


def seccoes(pagina):
    """Lista de (linha, nome da secção) a partir dos 'eyebrow' e títulos de cada página."""
    linhas = (RAIZ / "src" / pagina).read_text().splitlines()
    inicios = [i for i, l in enumerate(linhas) if "<section" in l] + [len(linhas)]
    marcas = []
    for a, b in zip(inicios, inicios[1:]):
        nome = None
        for l in linhas[a:b]:
            m = re.search(r'class="eyebrow[^"]*">(.*?)</p>', l)
            if m:
                nome = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split()).lstrip("— ")
                break
        if 'class="hero' in linhas[a] or 'class="page-hero' in linhas[a]:
            nome = "Topo da página"
        marcas.append((a, nome or "—"))
    return linhas, marcas


USOS = {}  # nome web -> [ "Página · Secção (recorte)" ]
for pagina, rotulo in PAGINAS.items():
    linhas, marcas = seccoes(pagina)
    for i, l in enumerate(linhas):
        for m in re.finditer(r"\[\[img ([\w-]+) (\w+)", l):
            nome, rec = m.groups()
            sec = next((s for j, s in reversed(marcas) if j <= i), "Topo")
            USOS.setdefault(nome, []).append(f"{rotulo} · {sec} ({rec.replace('x', ':')})")
        for m in re.finditer(r'og:image" content="fotos/web/([\w-]+)/', l):
            USOS.setdefault(m.group(1), []).append(f"{rotulo} · imagem de partilha (redes sociais)")


def miniatura(src: Path) -> str:
    dst = MINI / (src.stem + ".jpg")
    if not dst.exists():
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "-Z", "700",
                        str(src), "--out", str(dst)], check=True, capture_output=True)
    return f"originais/{dst.name}"


def original(origem):
    tipo, nome = origem.split(":", 1)
    pasta = RAIZ / "fotos" / ("originais" if tipo == "o" else "facebook")
    return next(p for p in pasta.iterdir() if p.stem == nome)


def web_preview(nome):
    d = RAIZ / "fotos" / "web" / nome
    jpgs = sorted(d.glob(f"{nome}-*-960.jpg")) or sorted(d.glob("*.jpg"))
    return f"../../fotos/web/{nome}/{jpgs[0].name}" if jpgs else None


cartoes = {"o": [], "f": []}
usadas_orig = set()
for origem, nome, recortes, _aj, credito, alt in R:
    src = original(origem)
    usadas_orig.add(src.name)
    usos = USOS.get(nome, [])
    if nome == "touca-antiga":
        usos = usos + ["Início · 05 A touca (a touca do site foi redesenhada a partir da foto da touca antiga)"]
    cartoes[origem[0]].append(dict(ficheiro=src.name, nome=nome, alt=alt, credito=credito,
                                    mini=miniatura(src), web=web_preview(nome), usos=usos))

# fotos enviadas que nunca entraram na receita
extra = []
for p in sorted((RAIZ / "fotos" / "originais").iterdir()):
    if p.suffix.lower() in (".jpg", ".jpeg", ".heic", ".png") and p.name not in usadas_orig:
        usos = ["Início · 05 A touca (a touca do site foi redesenhada a partir da foto da touca antiga)"] if p.stem == "touca-antiga-2" else []
        extra.append(dict(ficheiro=p.name, nome="—", alt="Não foi preparada para a web", credito=None,
                          mini=miniatura(p), web=None, usos=usos))
cartoes["o"] += extra


def cartao(c, n):
    no_site = bool(c["usos"])
    estado = '<span class="tag sim">No site</span>' if no_site else '<span class="tag nao">Fora do site</span>'
    usos = "".join(f"<li>{html.escape(u)}</li>" for u in c["usos"]) or "<li class='vazio'>Não aparece em nenhuma página</li>"
    web = (f'<figure><img loading="lazy" src="{c["web"]}"><figcaption>Como está preparada para o site</figcaption></figure>'
           if c["web"] else "")
    cred = f'<p class="cred">Crédito: {html.escape(c["credito"])}</p>' if c["credito"] else ""
    return f"""<article class="card {'on' if no_site else 'off'}">
  <div class="num">{n}</div>
  <div class="imgs"><figure><img loading="lazy" src="{c['mini']}"><figcaption>Original que enviaste</figcaption></figure>{web}</div>
  <div class="info">{estado}<h3>{html.escape(c['ficheiro'])}</h3>
  <p class="nome">Nome no site: <code>{html.escape(c['nome'])}</code></p>
  <p class="alt">{html.escape(c['alt'])}</p>{cred}<ul>{usos}</ul></div>
</article>"""


def bloco(titulo, sub, lista, inicio):
    on = sum(bool(c["usos"]) for c in lista)
    lista = sorted(lista, key=lambda c: not c["usos"])
    corpo = "\n".join(cartao(c, inicio + i) for i, c in enumerate(lista))
    return (f'<section><h2>{titulo} <small>{len(lista)} fotos · {on} no site · {len(lista) - on} fora</small></h2>'
            f'<p class="sub">{sub}</p><div class="grid">{corpo}</div></section>'), len(lista)


b1, n1 = bloco("Fotos que me enviaste", "Da pasta fotos/originais. Primeiro as que estão no site, depois as que ficaram de fora.",
               cartoes["o"], 1)
b2, _ = bloco("Fotos do Facebook do clube", "Não foram enviadas por ti: fui buscá-las à página do clube no Facebook.",
              cartoes["f"], n1 + 1)

(OUT / "index.html").write_text(f"""<!doctype html><html lang="pt"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Fotos do CNO</title>
<style>
:root{{--ink:#0b1b2b;--pink:#ff3d7f;--paper:#f6f4ef;--mut:#5b6773}}
body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.45 -apple-system,system-ui,sans-serif}}
header{{padding:40px 24px 8px;max-width:1400px;margin:auto}} h1{{margin:0 0 6px;font-size:34px}}
header p{{color:var(--mut);margin:0}} section{{max-width:1400px;margin:auto;padding:24px}}
h2{{font-size:24px;margin:24px 0 4px}} h2 small{{font-size:14px;color:var(--mut);font-weight:500;margin-left:8px}}
.sub{{color:var(--mut);margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:18px}}
.card{{background:#fff;border-radius:14px;padding:14px;position:relative;box-shadow:0 1px 3px #0001;border:2px solid transparent}}
.card.off{{border-color:#ccd3da;background:#fbfbfb}}
.num{{position:absolute;top:10px;left:10px;background:var(--ink);color:#fff;font-weight:700;border-radius:20px;padding:2px 10px;z-index:1}}
.imgs{{display:flex;gap:8px}} figure{{margin:0;flex:1;min-width:0}}
figure img{{width:100%;height:210px;object-fit:contain;background:#eef1f4;border-radius:8px;display:block}}
figcaption{{font-size:11px;color:var(--mut);margin-top:3px}}
h3{{margin:8px 0 2px;font-size:16px}} .nome,.cred{{margin:0;font-size:13px;color:var(--mut)}} .alt{{margin:4px 0}}
ul{{margin:6px 0 0;padding-left:18px}} li.vazio{{color:var(--mut);list-style:none;margin-left:-18px}}
.tag{{display:inline-block;font-size:12px;font-weight:700;border-radius:20px;padding:2px 10px;margin-top:8px}}
.tag.sim{{background:var(--pink);color:#fff}} .tag.nao{{background:#dfe4e9;color:var(--ink)}}
@media(max-width:500px){{.grid{{grid-template-columns:1fr}} figure img{{height:150px}}}}
</style></head><body>
<header><h1>Fotos do Clube Natação de Olhão</h1>
<p>Cada cartão tem um número, para me dizeres facilmente qual queres trocar, tirar ou pôr no site.
À esquerda está a foto original; à direita, o recorte preparado para o site.</p></header>
{b1}{b2}
</body></html>""")
print(OUT / "index.html", sum(map(len, cartoes.values())), "fotos")
