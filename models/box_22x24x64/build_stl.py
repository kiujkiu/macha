"""
Build a box open on ONE LONG SIDE (5 faces), with an asymmetric windowed front
panel + M4 holes.

Spec (user 2026-06-22, revised twice):
  - External size (X × Y × Z) = 22 × 24 × 64 mm
  - OPEN face = the +X side (a 64×24 face). The other 5 faces are present:
        bottom(-Z) & top(+Z)  : 22×24, 2 mm each
        front(-Y) panel        : 64×22, 1 mm   (the thin face; window + holes)
        back(+Y) panel         : 64×22, 2 mm   (holes)
        side(-X)               : 64×24, 2 mm
  - On the 1 mm FRONT panel: a centered through WINDOW 35 (along Z, the 64 length)
        × 14 (along X, the 22 width), centered at (X=0, Z=32).
  - On each 64×22 panel (front & back): 2 × M4 (Φ4.5) through-holes, X-centered,
        c-c 44 → Z = 10 / 54 (clear of the window's Z=14.5..49.5 span).

Print note: lay the -X solid side on the bed (open +X side up) → no supports.
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
EXT_L, EXT_W, EXT_H = 22.0, 24.0, 64.0   # X, Y, Z
WALL_FRONT = 1.0   # -Y panel (thin, windowed)
WALL_BACK  = 2.0   # +Y panel
WALL_SIDE  = 2.0   # -X side (closed); +X side is OPEN
WALL_END   = 2.0   # top & bottom (±Z)

WIN_Z = 35.0       # window extent along Z (the 64 length)
WIN_X = 14.0       # window extent along X (the 22 width)
WIN_ZC = EXT_H/2   # 32, centered in height
WIN_XC = 4.0       # shifted +4 toward the open +X side → right edge flush with the
                   # +X panel edge (X=11). Removes the former 4 mm tab; window now
                   # opens onto the +X side as an edge notch.

HOLE_DIAM = 4.5
HOLE_CC = 44.0
HOLE_Z = [EXT_H/2 - HOLE_CC/2, EXT_H/2 + HOLE_CC/2]   # 10, 54

# derived cavity (open toward +X)
CAV_X0 = -EXT_L/2 + WALL_SIDE          # -9
CAV_X1 =  EXT_L/2 + 1.0                # 12 (1 mm past the open +X face)
CAV_Y0 = -EXT_W/2 + WALL_FRONT         # -11
CAV_Y1 =  EXT_W/2 - WALL_BACK          #  10
CAV_Z0 =  WALL_END                      # 2
CAV_Z1 =  EXT_H - WALL_END             # 62

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), True).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))

# ===== Build solid =====
outer = m3d.Manifold.cube((EXT_L, EXT_W, EXT_H), True).translate((0, 0, EXT_H/2))
cav = _box(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, CAV_Z0, CAV_Z1)
part = outer - cav

# Through window in the front (-Y) panel. If its +X edge reaches the panel edge,
# extend the cut 1 mm past it so the notch opens cleanly onto the +X side.
win_x1 = WIN_XC + WIN_X/2
if win_x1 >= EXT_L/2 - 1e-6:
    win_x1 = EXT_L/2 + 1.0
win = _box(WIN_XC - WIN_X/2, win_x1, -EXT_W/2 - 1, CAV_Y0 + 0.5,
           WIN_ZC - WIN_Z/2, WIN_ZC + WIN_Z/2)
part = part - win

# 2 × M4 holes along Y, through both 64×22 panels
for hz in HOLE_Z:
    h = m3d.Manifold.cylinder(EXT_W + 4, HOLE_DIAM/2, HOLE_DIAM/2, 48, True)
    h = h.rotate((90, 0, 0)).translate((0, 0, hz))
    part = part - h

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("box_22x24x64.stl")
with out.open("wb") as f:
    f.write(b"box_22x24x64".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

assert 84 + len(tris) * 50 == out.stat().st_size, "STL size mismatch (header overflow?)"

print(f"wrote {out} ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}  (ext {EXT_L:g})")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}  (ext {EXT_W:g})")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}  (ext {EXT_H:g})")
print(f"  OPEN face = +X (64×24)")
print(f"  walls: front(-Y) {WALL_FRONT:g} / back(+Y) {WALL_BACK:g} / side(-X) {WALL_SIDE:g} / ends(±Z) {WALL_END:g}")
print(f"  window(front): X{WIN_X:g} × Z{WIN_Z:g} @ (X={WIN_XC:g}, Z={WIN_ZC:g}), through")
print(f"  holes : 2 per panel @ X=0, Z={HOLE_Z}  Φ{HOLE_DIAM:g} (M4), c-c {HOLE_CC:g}")
print(f"  volume:        {part.volume():9.2f} mm^3")
