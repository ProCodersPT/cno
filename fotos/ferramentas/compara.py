"""Before/after sheet: original crop (left) vs processed (right)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
from preview import sources, load
from receita import R
from processar import crop_box
OUT="/Users/vicentevaz/Documents/GitHub/cno/fotos/web"
font=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf",16)
src=dict(sources()); names=sys.argv[2:]; rows=[]
for key,name,crops,adj,credit,alt in R:
    if names and name not in names: continue
    ratio,cx,cy,s=crops[0]; im=load(src[key]); box=crop_box(*im.size,ratio,cx,cy,s)
    a=im.crop(box); tag=ratio.replace(':','x')
    fs=sorted(f for f in os.listdir(os.path.join(OUT,name)) if f.startswith(f"{name}-{tag}-") and f.endswith('.jpg'))
    b=Image.open(os.path.join(OUT,name,fs[-1]))
    for x in (a,b): x.thumbnail((440,440))
    rows.append((name,a,b))
cell=460; sheet=Image.new('RGB',(cell*4,cell*((len(rows)+1)//2)),'white'); d=ImageDraw.Draw(sheet)
for i,(n,a,b) in enumerate(rows):
    x=(i%2)*cell*2; y=(i//2)*cell
    sheet.paste(a,(x+10,y+30)); sheet.paste(b,(x+cell,y+30)); d.text((x+10,y+6),n+"  (antes | depois)",fill='black',font=font)
sheet.save(sys.argv[1],quality=85)
