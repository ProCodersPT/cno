# Fotos e vídeos prontos para o site

Gerados a 17/11/2026 a partir de `fotos/originais/`, `fotos/facebook/` e `fotos/videos/`. **Esta é a pasta que o site usa.** Os originais não se tocam.

## Como estão organizadas

Cada foto tem a sua pasta, com um ou mais **recortes** e vários **tamanhos** de cada um:

```
web/<nome>/<nome>-<proporção>-<largura>.avif   ← formato principal (leve)
web/<nome>/<nome>-<proporção>-<largura>.jpg    ← alternativa para browsers antigos
```

- **Proporções:**
  - `3x2` e `16x9`: horizontais, para banners e fundos;
  - `4x3`;
  - `4x5`: vertical, para cartões e telemóvel;
  - `1x1`: quadrado, para grelhas.
- **Larguras:** 480, 960, 1600 e 2400 px, ou o máximo que a foto original permite. Nunca se amplia.
- **`fotos.json`:** lista tudo o que existe, com os recortes, os tamanhos, o **texto alternativo** (alt) de cada foto e o **crédito do fotógrafo**. O site pode gerar o `<picture>` diretamente a partir dele.

Exemplo de uso:
```html
<picture>
  <source type="image/avif" srcset="fotos/web/sair-da-piscina-touca-rosa/sair-da-piscina-touca-rosa-3x2-960.avif 960w, …-1500.avif 1500w">
  <img src="fotos/web/sair-da-piscina-touca-rosa/sair-da-piscina-touca-rosa-3x2-960.jpg"
       alt="Nadador do CNO com a touca rosa do clube a sair da piscina pela escada" width="1500" height="1000" loading="lazy">
</picture>
```

## O que foi feito

- **Recortes** escolhidos foto a foto: centrados nas pessoas, sem céu, teto ou chão a mais, e sem cortar cabeças nem pés nas fotos de grupo.
- **Fotos do telemóvel:** ajuste suave de níveis, contraste e cor. Algumas tiveram correções específicas:
  - **Balanço de brancos:** a bandeira antiga, a touca antiga, o troféu e a equipa de infantis.
  - **Sombras mais abertas:** a equipa ao sol com o troféu, a equipa debaixo das palmeiras, a equipa à noite e Torremolinos.
  - **Rotação:** a panorâmica `equipa-blocos-exterior`.
- **Fotos de fotógrafos** (AmoNadar, Virgílio Afonso, Luís Mestre, Alexandra Hoesen): **sem alterações de cor**, só recorte e redimensionamento, para respeitar a edição de cada fotógrafo. As marcas de água ficaram.
- **Exportação:** AVIF (qualidade 58) e JPG progressivo (qualidade 82), com nitidez leve nas reduções.

## As melhores para cada uso

| Uso | Fotos |
|---|---|
| **Topo do site / imagem grande** | `sair-da-piscina-touca-rosa`, `mariposa-salpicos`, `concentracao-touca-rosa`, `bloco-touca-branca`, `toucas-rosa-na-agua` |
| **Os 20 anos / história** | `bandeira-historica`, `touca-antiga`, `equipa-2019`, `celebracao-trofeus` |
| **Palmarés** | `trofeu-regional-infantis-2026`, `podio-loule`, `podio-estafetas`, `podio-regional`, `atleta-nacionais-fpn`, `medalhas` |
| **Equipa técnica** | `equipa-absolutos-tecnicos`, `equipa-noite-tecnicos` |
| **"Uma família"** | `jantar-clube`, `almoco-equipa`, `equipa-infantis`, `equipa-piscina-exterior`, `equipa-palmeiras`, `convivio-campeonato`, `viagem-carrinha` |
| **Em prova** | `chegada-prova`, `open-lisboa`, `nacional-juniores-bloco`, `partida-exterior`, `crol-perto`, `mariposa-touca-rosa` |
| **Texturas e fundos** | `pistas-detalhe`, `toucas-rosa-na-parede`, `equipa-toucas-de-costas` |

## Touca antiga em fundo transparente (`web/touca-antiga-recorte/`)

A touca rosa "C. N. OLHÃO" foi reconstruída a partir da foto `originais/touca-antiga-2.jpg` (a touca esticada), como se tivesse sido fotografada em estúdio.
- **Forma:** medida na foto, altura a altura, e tornada simétrica. Tem a cúpula redonda, o degrau onde os lados recolhem para a faixa direita do rebordo e a base com uma onda suave, mais baixa ao centro.
- **Cores:** o rosa coral e o azul real da touca.
- **Volume:** é o de uma touca pousada. A superfície é quase plana, com as bordas arredondadas por igual em toda a volta (cúpula e rebordo) e um volume geral muito leve. A luz vem de cima à esquerda. Tem o brilho suave do silicone e um grão fino na superfície. Não tem rugas.
- **Impressão:** está nivelada (na foto estava rodada 1,4°).
  - O nadador e o "aqualoja" vêm da foto, com os contornos alisados. O "aqualoja" usa uma letra redonda que não existe no Mac, por isso não foi recomposto.
  - As pistas foram redesenhadas a direito, com as ameias regulares.
  - "C. N. OLHÃO" foi recomposto em **Arial Bold**, ligeiramente estreitada para igualar a impressão.
- **Ficheiros** (todos com transparência, em `.avif`, `.webp` e `.png`):
  - `touca-antiga-{400,800,1600,2400}`: só a touca;
  - `touca-antiga-sombra-{…}`: com sombra suave no chão, para pousar sobre fundos claros.

## Vídeos (`web/video/`)

Ciclos sem som e sem corte visível (o fim funde-se no início), em MP4 H.264 com início rápido, para pôr em `<video autoplay muted loop playsinline>`.

| Ficheiro | Duração | Peso | Conteúdo |
|---|---|---|---|
| `mergulho-16x9.mp4` | 9 s | 7,4 MB | **Topo do site no computador**: impulsão na parede, pernada, nadador a passar sobre as linhas e mergulho, com transições suaves |
| `mergulho-9x16.mp4` | 11 s | 5,3 MB | **Topo do site no telemóvel**: mergulho vertical, impulsão na parede e nadadores ao fundo |
| `pistas-calmo-16x9.mp4` | 5,5 s | 4,6 MB | Fundo calmo: linhas da piscina vistas de baixo de água |
| `pistas-calmo-9x16.mp4` | 5,5 s | 2,8 MB | O mesmo na vertical |
| `*-poster.jpg` | | | Primeiro fotograma de cada vídeo, para mostrar enquanto o vídeo carrega |

- Os vídeos têm uma ligeira correção de contraste e saturação.
- O 16:9 foi recortado do 4K vertical original, com mais resolução do que o necessário.
- Testei o AV1/WebM, mas nestes vídeos de água ficava maior do que o MP4 com a mesma qualidade, por isso ficou só o MP4.

## ⚠️ Antes de publicar
- **Créditos:** pedir autorização e creditar AmoNadar, Virgílio Afonso / Algarve a Nadar, Luís Mestre e Alexandra Hoesen. Estão no `fotos.json`.
- **Menores:** confirmar com o clube a autorização de imagem para as fotos de grupo com atletas jovens.

## Refazer
Os scripts estão em `fotos/ferramentas/`. `receita.py` define o recorte e os ajustes de cada foto, `processar.py` exporta e `videos.py` gera os ciclos. Os HEIC têm de ser convertidos antes para `ferramentas/src/`, com este comando:

```bash
sips -s format jpeg -s formatOptions 95 fotos/originais/X.HEIC --out fotos/ferramentas/src/X.jpg
```
