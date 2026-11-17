"""Build web-ready seamless loops from the underwater clips (H.264 MP4 + AV1 WebM + poster)."""
import subprocess, os, sys

SRC = "/Users/vicentevaz/Documents/GitHub/cno/fotos/videos"
OUT = "/Users/vicentevaz/Documents/GitHub/cno/fotos/web/video"
os.makedirs(OUT, exist_ok=True)
F = 0.5  # crossfade seconds
GRADE = "eq=contrast=1.06:saturation=1.08:gamma=0.98"

# (clip, start, end, vertical centre for the 16:9 crop as a fraction of the portrait frame)
MONTAGEM = [("IMG_2871", 1.0, 4.6, .45), ("IMG_2874", 0.8, 4.2, .45),
            ("IMG_2876", 10.0, 13.5, .42), ("IMG_2877", 0.3, 3.0, .50)]
CALMO = [("IMG_2870", 7.4, 13.4, .55)]
# Horizontal crops lose the vertical dive, so desktop uses the horizontal moments.
MONTAGEM_16x9 = [("IMG_2874", 0.6, 3.4, .40), ("IMG_2876", 10.2, 13.5, .42),
                 ("IMG_2877", 0.3, 3.0, .50), ("IMG_2871", 2.4, 5.0, .60)]

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
    subprocess.run(base + ["-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "6M" if mode == "16x9" else "3.5M",
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
        build("pistas-calmo", CALMO, mode)
