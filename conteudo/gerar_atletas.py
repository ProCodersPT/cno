"""Gera src/partials/atletas.html a partir de conteudo/atletas.txt (um nome por linha).

Linhas vazias e linhas começadas por # são ignoradas. A ordem no site é alfabética
pelo primeiro nome (ignorando acentos). Depois corre python3 build.py.
"""
import html, pathlib, unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
nomes = []
for linha in (ROOT / "conteudo/atletas.txt").read_text().splitlines():
    linha = " ".join(linha.split("#", 1)[0].split())
    if linha and linha not in nomes:
        nomes.append(linha)

chave = lambda n: unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
nomes.sort(key=chave)

ponto = '<span class="roll__dot" aria-hidden="true">●</span>'
lista = f"\n{ponto}\n".join(f'<span class="roll__name">{html.escape(n)}</span>' for n in nomes)
(ROOT / "src/partials/atletas.html").write_text(f"""<div class="wrap">
    <p class="roll__count reveal">{len(nomes)} nadadores vestiram a touca rosa desde 2005.</p>
  </div>
  <p class="roll__names" aria-label="Lista de atletas do clube">
{lista}
  </p>
  <div class="wrap">
    <p class="roll__note">Lista feita a partir de resultados oficiais e notícias. Falta alguém? Diz-nos para o acrescentarmos.</p>
  </div>
""")
print(len(nomes), "nomes")
