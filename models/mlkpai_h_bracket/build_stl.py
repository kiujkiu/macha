"""
H-shaped 3 mm bracket for the 米联派 MLKPAI-FS03 ZYNQ-7020 board (85×56).
Rotated-H (slots open LEFT/RIGHT, per user 2026-06-23): solid full-width top &
bottom bars + a central vertical spine; notches on the left & right sides.
Central 5 holes (Φ24 + 4×M3 square) CENTRED on the board (0,0) per user.

Board data (MLKPAI-FS03 pack): outline 85×56×18.1; ZYNQ chip centroid (0,+3.7).
4 corner M3 holes: ESTIMATE (pitch 78×49, ~3.5 inset) — verify with calipers.
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Board (centred frame, +Y up) =====
BW, BH = 85.0, 56.0
HX, HY = BW/2, BH/2                    # 42.5, 28
CHIP = (0.0, 3.7)                      # ZYNQ centre (ref only; holes are centred below)

# central 5 holes — CENTRED on the board per user
CEN = (0.0, 0.0)
CENTER_D = 24.0
SQ = 24.0
SQ_HOLES = [(CEN[0] + sx*SQ/2, CEN[1] + sy*SQ/2) for sx in (-1, 1) for sy in (-1, 1)]   # (±12,±12)

# 4 corner mounting holes — pitch 79×50 (user-confirmed), centred → 3 mm inset
CHX, CHY = 39.5, 25.0
CORNER = [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]

# ===== Part params =====
THICK     = 3.0
M3_CORNER = 3.4
M3_SQ     = 3.4

# ----- rotated-H outline (slots 25 wide × 44 tall, both sides) -----
SLOT_W, SLOT_H = 25.0, 44.0
BAR_IN  = SLOT_H / 2                    # 22 → bars y[±22..±28] (6 mm), slot height 44
SPINE_X = HX - SLOT_W                   # 17.5 → slot width 25 (edge-open to ±42.5)

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), True).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
def _hole(d, x, y):
    return m3d.Manifold.cylinder(THICK + 2, d/2, d/2, max(48, int(d*8)), True).translate((x, y, THICK/2))

# ===== Build =====
plate = (_box(-HX, HX, BAR_IN, HY, 0, THICK)          # top bar (full width)
         + _box(-HX, HX, -HY, -BAR_IN, 0, THICK)      # bottom bar
         + _box(-SPINE_X, SPINE_X, -HY, HY, 0, THICK)) # central spine
plate = plate - _hole(CENTER_D, *CEN)
for (x, y) in CORNER:
    plate = plate - _hole(M3_CORNER, x, y)
for (x, y) in SQ_HOLES:
    plate = plate - _hole(M3_SQ, x, y)

# ===== Export STL =====
mesh = plate.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("mlkpai_h_bracket.stl")
with out.open("wb") as f:
    f.write(b"mlkpai_h_bracket".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris) * 50 == out.stat().st_size, "STL size mismatch"

print(f"wrote {out} ({len(tris)} tris)")
print(f"  bbox X {verts[:,0].min():.1f}..{verts[:,0].max():.1f}  Y {verts[:,1].min():.1f}..{verts[:,1].max():.1f}  Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}")
print(f"  rotated-H: bars y±[{BAR_IN:g}..{HY:g}] (6mm), spine x±{SPINE_X:g}; slots {SLOT_W:g}×{SLOT_H:g} open L/R")
print(f"  central 5 holes CENTRED @ {CEN}: Φ{CENTER_D:g} + 4×Φ{M3_SQ:g} @ (±{SQ/2:g},±{SQ/2:g})")
print(f"  4 corner M3 Φ{M3_CORNER:g} @ (±{CHX:g},±{CHY:g})  pitch {2*CHX:g}×{2*CHY:g}")
print(f"  volume {plate.volume():.1f} mm^3  (chip ref {CHIP}, +3.7 above hole centre)")
