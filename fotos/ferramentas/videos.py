"""Build web-ready seamless loops from the underwater clips (H.264 MP4 + AV1 WebM + poster)."""
import subprocess, os, sys

SRC = "/Users/vicentevaz/Documents/GitHub/cno/fotos/videos"
OUT = "/Users/vicentevaz/Documents/GitHub/cno/fotos/web/video"
os.makedirs(OUT, exist_ok=True)
F = 0.3  # crossfade seconds
GRADE = "eq=contrast=1.06:saturation=1.08:gamma=0.98"

# (clip, start, end, vertical centre for the 16:9 crop as a fraction of the portrait frame)
# The user's own cuts (fotos/videos/recortados), used whole. Dives alternate with the
# underwater swim-pasts so two swim-pasts never follow each other; 2877_2 and 2877_3
# overlap (same swim), so they sit as far apart as the loop allows.
MONTAGEM = [("recortados/IMG_2874_2", 0.0, 3.415, .42),   # dive
            ("recortados/IMG_2877_2", 0.0, 5.963, .50),   # underwater swim-past
            ("recortados/IMG_2871_2", 0.0, 1.985, .45),   # dive
            ("recortados/IMG_2876_2", 0.0, 6.945, .42),   # underwater swim-past
            ("recortados/IMG_2870_2", 0.0, 3.463, .45),   # dive down
            ("recortados/IMG_2877_3", 0.0, 4.171, .50)]   # underwater swim-away
CALMO = [("IMG_2870", 7.4, 13.4, .55)]
MONTAGEM_16x9 = MONTAGEM
RATE = {"16x9": ("25", "4M"), "9x16": ("24", "2.5M")}  # crf, maxrate: keeps the longer loop light

def build(name, segs, mode):
    inputs, chains = [], []
    for i, (clip, a, b, cy) in enumerate(segs):
        inputs += ["-i", os.path.join(SRC, clip + ".MOV")]
        if mode == "16x9":
            # portrait 2160x3840 -> 2160x1215 band around cy
            y = int(max(0, min(3840 - 1215, 3840 * cy - 607)))
            geo = f"crop=2160:1215:0:{y},scale=1920:1080:flags=lanczos"
        else:
            geo = "scale=720:1280:flags=lanczos"
        chains.append(f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,{geo},{GRADE},format=yuv420p[v{i}]")
    # crossfade chain
    durs = [b - a for _, a, b, _ in segs]
    last, off = "v0", durs[0]
    for i in range(1, len(segs)):
        off -= F
        chains.append(f"[{last}][v{i}]xfade=transition=fade:duration={F}:offset={off:.3f}[x{i}]")
        last = f"x{i}"; off += durs[i]
    L = off  # total length
    # seamless loop: crossfade the tail into the head
    chains.append(f"[{last}]split[m1][m2]")
    chains.append(f"[m1]trim={F}:{L},setpts=PTS-STARTPTS[t1]")
    chains.append(f"[m2]trim=0:{F},setpts=PTS-STARTPTS[t2]")
    chains.append(f"[t1][t2]xfade=transition=fade:duration={F}:offset={L - 2 * F:.3f},format=yuv420p[out]")
    fc = ";".join(chains)
    stem = os.path.join(OUT, f"{name}-{mode}")
    base = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-an"]
    subprocess.run(base + ["-c:v", "libx264", "-preset", "slow", "-crf", RATE[mode][0], "-maxrate", RATE[mode][1],
                           "-bufsize", "12M", "-profile:v", "high", "-tune", "film",
                           "-movflags", "+faststart", stem + ".mp4"], check=True)
    # AV1 tested: at equal visual quality it was larger than H.264 on this footage, so MP4 only.
    # poster = first frame of the loop
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", stem + ".mp4", "-frames:v", "1", "-q:v", "3",
                    stem + "-poster.jpg"], check=True)
    sz = {e: os.path.getsize(stem + e) // 1024 for e in (".mp4", "-poster.jpg")}
    print(name, mode, f"{L - F:.1f}s", sz, flush=True)

if __name__ == "__main__":
    for mode in ("16x9", "9x16"):
        build("mergulho", MONTAGEM_16x9 if mode == "16x9" else MONTAGEM, mode)
        if "--tudo" in sys.argv:
            build("pistas-calmo", CALMO, mode)
