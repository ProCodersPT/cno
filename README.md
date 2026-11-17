# Clube Natação de Olhão — site

Site estático, escrito à mão (HTML, CSS e JavaScript), para o Clube Natação de Olhão.

## Páginas
- `index.html`: página principal. Tem a entrada animada, o vídeo, o manifesto, os números, o percurso, a equipa técnica, o palmarés, a touca, a galeria e os horários.
- `historia.html`: as divisões nacionais por época, os títulos regionais, os atletas, os treinadores e as provas internacionais.
- `inscricoes.html`: os passos, os horários e o formulário de inscrição (Netlify Forms).

## Como editar
1. Edita os ficheiros em `src/`. O cabeçalho e o rodapé partilhados estão em `src/partials/`.
2. Corre `python3 build.py`. Gera os `.html` da raiz e converte cada `[[img nome proporção sizes classe]]` num `<picture>` com AVIF e JPG responsivos, a partir de `fotos/web/fotos.json`.
3. Estilos em `assets/css/style.css` e animações em `assets/js/main.js`. Usa GSAP, ScrollTrigger e Lenis, via CDN.

## Ver localmente
```bash
python3 -m http.server 8090
```

## Publicar
- Netlify, com o repositório ligado. A configuração está em `netlify.toml`.
- O formulário de inscrição usa o Netlify Forms. Depois do primeiro deploy, configura no painel do Netlify o email que recebe os pedidos.

## Conteúdo e imagens
- `conteudo/dossier.md`: todos os factos, com fontes.
- `fotos/web/LEIA-ME.md`: as fotos tratadas, os créditos e as autorizações em falta.
