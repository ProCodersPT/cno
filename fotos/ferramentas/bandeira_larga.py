"""Versão larga da foto da bandeira (IMG_2944) para o percurso: a bandeira inteira cabe
em qualquer moldura (4:3 a 2,3:1) porque a parede é prolongada para os lados."""
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from pathlib import Path
R = Path(__file__).resolve().parents[2] / "fotos" / "originais"
im = ImageOps.exif_transpose(Image.open(R / "IMG_2944.JPG")).convert("RGB")
a = np.asarray(im).astype(np.float32)[:1140]          # bandeira + foto de equipa
H, W, _ = a.shape
NW = int(round(H * 2.3)); pad = (NW - W) // 2
out = np.zeros((H, NW, 3), np.float32)
out[:, pad:pad + W] = a
rng = np.random.default_rng(7)
for side, strip in (("l", a[:, 8:70]), ("r", a[:, W - 70:W - 8])):
    col = strip.mean(1)                                  # cor da parede, linha a linha
    col = np.asarray(Image.fromarray(col[:, None].clip(0, 255).astype(np.uint8)).resize((1, H)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)[:, 0]
    sd = strip.std(1).mean() * .6
    fill = np.repeat(col[:, None], pad + 1, 1) + rng.normal(0, sd, (H, pad + 1, 1))
    if side == "l":
        out[:, :pad] = fill[:, :pad]
        for k in range(40):                              # costura suave
            t = k / 40; out[:, pad + k] = a[:, k] * t + col * (1 - t)
    else:
        out[:, pad + W:] = fill[:, :NW - pad - W]
        for k in range(40):
            t = k / 40; out[:, pad + W - 1 - k] = a[:, W - 1 - k] * t + col * (1 - t)
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(R / "bandeira-larga.jpg", quality=95)
print(NW, H)
