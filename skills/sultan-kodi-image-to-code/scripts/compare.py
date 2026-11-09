#!/usr/bin/env python3
"""Compare a reference image with a screenshot. Usage: compare.py ref.png shot.png [diff_out.png]
Needs Pillow (pip install pillow). Prints a similarity score and the worst regions."""
import sys, warnings
warnings.filterwarnings("ignore")
try:
    from PIL import Image, ImageChops
except ImportError:
    sys.exit("Pillow missing: pip install pillow --break-system-packages")
if len(sys.argv) < 3: sys.exit(__doc__)
a = Image.open(sys.argv[1]).convert("RGB"); b = Image.open(sys.argv[2]).convert("RGB")
print(f"reference {a.size}, screenshot {b.size}")
if a.size != b.size:
    print("sizes differ: resizing screenshot to reference width keeping aspect ratio")
    b = b.resize((a.width, round(b.height * a.width / b.width)))
    h = min(a.height, b.height); a = a.crop((0, 0, a.width, h)); b = b.crop((0, 0, a.width, h))
d = ImageChops.difference(a, b).convert("L")
px = list(d.getdata()); mean = sum(px) / len(px)
score = 100 * (1 - mean / 255)
changed = sum(1 for v in px if v > 40) / len(px) * 100
print(f"similarity {score:.1f}/100, {changed:.1f}% of pixels differ noticeably")
cols, rows = 4, 4; w, h = d.size; worst = []
for r in range(rows):
    for c in range(cols):
        box = (c * w // cols, r * h // rows, (c + 1) * w // cols, (r + 1) * h // rows)
        reg = list(d.crop(box).getdata()); worst.append((sum(reg) / len(reg), r, c))
worst.sort(reverse=True)
print("worst regions (row, col of 4x4 grid, higher = more different):")
for v, r, c in worst[:3]: print(f"  row {r + 1}, col {c + 1}: {v:.1f}")
if len(sys.argv) > 3: d.point(lambda v: min(255, v * 4)).save(sys.argv[3]); print("diff image:", sys.argv[3])
print("verdict:", "close match" if score >= 93 else "visible differences, keep iterating")
