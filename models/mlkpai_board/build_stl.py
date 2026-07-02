"""
Digital-twin model of the 米联派 MLKPAI-FS03 ZYNQ-7020 core board (BOUGHT part,
NOT printed) — reduced to what the user asked for (2026-07-01):
  board outline + 4 corner M3 holes + the two 2×25 pin headers (J11, J12).

All geometry measured off the official 位号图
(04_外形尺寸/MLKPAI-FS03_240909位号图.pdf, TOP art film, scale 25.52 px/mm):
  - board 85 × 56 mm; PCB thickness assumed 1.6 mm (not on the drawing)
  - 4 × M3 corner holes, pitch 79 × 50 (3 mm inset) → (±39.5, ±25)  [user-confirmed]
  - J11 top / J12 bottom: 2×25 dual-row 2.54 mm headers, pin-field span 63.5 mm,
    centred X=0, rows at Y = ±24.15 ± 1.27  (autocorr pitch 2.547 → 2.54)
    Pin 1 = left end on J11, right end on J12 (numbering only; geometry identical).
Header pins point DOWN (user-confirmed 2026-07-01): plastic base on the board BOTTOM
face, male 2.54 posts protruding below. Centred frame, +Y up, board bottom at Z=0.
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Board =====
BW, BH = 85.0, 56.0
THICK  = 1.6                                   # assumed (standard core board)

# 4 corner M3 holes — pitch 79×50, 3 mm inset (user-confirmed)
CHX, CHY = 39.5, 25.0
CORNER = [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]
M3 = 3.2

# ===== Pin headers (2×25, 2.54 pitch) =====
PITCH   = 2.54
NCOL    = 25
ROW_DY  = 2.54                                 # row-to-row spacing
HDR_YC  = 24.15                                # |Y| of header centre-line
PIN_SQ  = 0.64                                 # square pin cross-section
PIN_UP  = 5.6                                  # exposed pin length BEYOND the base (user 2026-07-01)
BASE_H  = 2.6                                  # plastic base thickness (user 2026-07-01)
PIN_LEN = 11.0                                 # TOTAL pin length — pokes out both sides (user 2026-07-01)
PIN_BOT = -(BASE_H + PIN_UP)                   # -8.2 : pin tip below board
PIN_TOP = PIN_BOT + PIN_LEN                    #  2.8 : pin tail 1.2 above PCB top (THICK=1.6)
assert PIN_TOP > THICK, "pin too short to reach the top face"
BASE_L  = NCOL * PITCH                          # 63.5 mm plastic body length (X)
BASE_W  = ROW_DY + 3.0                          # 5.54 mm body width (Y)

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), True).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
def _cyl(d, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, max(48, int(d*10)), True).translate((x, y, (z0+z1)/2))

# ----- board with holes -----
part = _box(-BW/2, BW/2, -BH/2, BH/2, 0, THICK)
for (x, y) in CORNER:
    part = part - _cyl(M3, x, y, -1, THICK+1)

# ----- one 2×25 header at centre-line yc (pins DOWN) -----
def header(yc):
    body = _box(-BASE_L/2, BASE_L/2, yc-BASE_W/2, yc+BASE_W/2, -BASE_H, 0.0)  # base under board
    xs = [(i - (NCOL-1)/2) * PITCH for i in range(NCOL)]      # -30.48 .. 30.48
    ys = [yc - ROW_DY/2, yc + ROW_DY/2]
    for x in xs:
        for y in ys:
            body = body + _box(x-PIN_SQ/2, x+PIN_SQ/2, y-PIN_SQ/2, y+PIN_SQ/2,
                               PIN_BOT, PIN_TOP)               # 11mm total, both sides
    return body

part = part + header(HDR_YC) + header(-HDR_YC)               # J11 top, J12 bottom

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("mlkpai_board.stl")
_hdr = b"POV3D mlkpai_board (MLKPAI-FS03 twin)"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size, "STL size mismatch"

print(f"wrote {out} ({len(tris)} tris)")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
print(f"  board {BW}×{BH}×{THICK}; 4×M3 Φ{M3} @ (±{CHX},±{CHY})")
print(f"  J11/J12: 2×{NCOL} @ {PITCH} pitch, span {(NCOL-1)*PITCH:.2f}, centre-lines Y ±{HDR_YC}, rows ±{ROW_DY/2:g}")
print(f"  header: base {BASE_H} on board bottom, pin total {PIN_LEN} (Z {PIN_BOT:.1f}..{PIN_TOP:.1f}); {PIN_UP} below base, {PIN_TOP-THICK:.1f} above PCB top")
print(f"  volume {part.volume():.1f} mm^3")
