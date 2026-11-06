# Place the DancingGiraffe PNG sequence on the speaker's head, frame by frame.
# usage: giraffe_on_head.py person.webm start dur giraffe_seq_dir out_frames_dir
# head top = first alpha row of the person matte (smoothed); the giraffe flies in from the right and leaves to the right.
import sys, json, math, subprocess, os
import numpy as np
from PIL import Image
webm, t0, dur, G, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
FPS = 60; GW, GH = 360, 480
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-c:v", "libvpx-vp9", "-ss", str(t0), "-t", str(dur), "-i", webm,
                      "-vf", "alphaextract,scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
d = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270)
pos = []
for a in d:
    rows = np.where((a > 128).sum(1) > 6)[0]; top = rows[0] if len(rows) else 200
    xs = np.where((a[top:top + 15] > 128).any(0))[0]; pos.append((xs.mean() * 4 if len(xs) else 540, top * 4))
o = np.array(pos); k = 7; pad = np.pad(o, ((k, k), (0, 0)), mode="edge")
H = [pad[i:i + 2 * k + 1].mean(0) for i in range(len(o))]
seq = sorted(f for f in os.listdir(G) if f.endswith(".png"))
gs = [Image.open(os.path.join(G, f)).convert("RGBA").resize((GW, GH), Image.LANCZOS) for f in seq]
os.makedirs(OUT, exist_ok=True); N = len(H); D = N / FPS
for i, (cx, top) in enumerate(H):
    t = i / FPS; dx = dy = 0
    if t < 0.45: u = t / 0.45; dx = (1 - (1 - (1 - u) ** 3)) * 650; dy = -math.sin(u * math.pi) * 160
    elif t > D - 0.45: u = (t - (D - 0.45)) / 0.45; dx = u ** 2 * 650; dy = -math.sin(u * math.pi) * 160
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); x = int(cx - GW * 0.5 + dx); y = int(top + 10 - GH * 0.9875 + dy)
    if -GW < x < 1080: im.alpha_composite(gs[i % len(gs)], (x, y))
    im.save(os.path.join(OUT, f"f{i:04d}.png"))
print("frames", N)
