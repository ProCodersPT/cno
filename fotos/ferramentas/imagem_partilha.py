"""Imagem de partilha (WhatsApp, Facebook): fotos/web/partilha/cno-partilha-1200x630.jpg.

Uso: python imagem_partilha.py <pasta> <saida.jpg>, a partir da raiz do projeto.
A <pasta> tem de ter cno-simbolo.png (o SVG do simbolo convertido, ex. com resvg-py),
bricolage.ttf e instrument-italic.ttf (Google Fonts).
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S, OUT = sys.argv[1], sys.argv[2]
W, H = 1200, 630
NIGHT=(6,10,28); PINK=(255,61,127); PAPER=(243,240,232); AQUA=(127,216,247); POOL=(3,161,226)

# background: the pool lanes photo, darkened and pushed into the club navy
bg = Image.open('fotos/web/pistas-detalhe/pistas-detalhe-16x9-1600.jpg').convert('RGB')
r = max(W/bg.width, H/bg.height); bg = bg.resize((round(bg.width*r), round(bg.height*r)), Image.LANCZOS)
bg = bg.crop(((bg.width-W)//2, (bg.height-H)//2, (bg.width-W)//2+W, (bg.height-H)//2+H))
bg = ImageEnhance.Brightness(bg).enhance(.55)
img = bg.convert('RGBA')
grad = Image.new('RGBA', (W, H))
gd = ImageDraw.Draw(grad)
for x in range(W):   # solid navy on the left (logo), fading to show the water on the right
    a = int(245 - 150 * max(0, (x - 380) / (W - 380)))
    gd.line([(x, 0), (x, H)], fill=NIGHT + (a,))
img.alpha_composite(grad)

d = ImageDraw.Draw(img)
# lane rope across the top, like the site's progress bar
x = 0; cols = [PINK, PAPER, POOL, PAPER]; i = 0
while x < W:
    d.rectangle([x, 0, x + 22, 9], fill=cols[i % 4]); x += 22; i += 1

# crest: white rounded tile with the swimmer symbol (as in the site's header)
tile = 300; tx, ty = 80, (H - tile) // 2 + 5
shadow = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([tx, ty + 18, tx + tile, ty + tile + 18], 64, fill=(0, 0, 0, 150))
img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)))
d.rounded_rectangle([tx, ty, tx + tile, ty + tile], 64, fill=PAPER)
sym = Image.open(f'{S}/cno-simbolo.png'); sw = 236; sym = sym.resize((sw, round(sym.height * sw / sym.width)), Image.LANCZOS)
img.alpha_composite(sym, (tx + (tile - sw) // 2, ty + (tile - sym.height) // 2))

def bric(size, wght=700):
    f = ImageFont.truetype(f'{S}/bricolage.ttf', size)
    f.set_variation_by_axes([min(96, size), wght, 100]); return f
ser = ImageFont.truetype(f'{S}/instrument-italic.ttf', 104)
inter = bric(20, 700)

lx = 450
def spaced(xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + track
spaced((lx, 150), 'CLUBE NATAÇÃO DE OLHÃO', inter, AQUA, 4.2)
big = bric(88, 760)
d.text((lx - 4, 190), 'Desde 2005', font=big, fill=PAPER)
d.text((lx - 4, 286), 'a fazer ', font=big, fill=PAPER)
d.text((lx - 4 + d.textlength('a fazer ', font=big), 278), 'crescer', font=ser, fill=PINK)
d.text((lx - 4, 382), 'nadadores.', font=big, fill=PAPER)
small = bric(24, 500)
d.text((lx, 512), 'Da escolinha à 1.ª Divisão nacional  ·  Olhão, Algarve', font=small, fill=(243, 240, 232, 170))
img.convert('RGB').save(OUT, quality=90, optimize=True, progressive=True)
