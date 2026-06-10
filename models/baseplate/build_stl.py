"""
Build POV 3D baseplate STL using manifold3d.

Features:
  - Square base 100 × 100 × 5 mm (centered on origin in XY, base bottom at Z = 0)
  - 4 × M6 (Φ6.5) corner mounting holes on a 75 × 75 mm pattern
  - 4 × M3 (Φ3.2) center mounting holes on a square with diagonal 25 mm
       (square side ≈ 17.68 mm, hole positions (±8.84, ±8.84))
  - 4 × Φ7 counterbores at the M3 hole positions, open downward from Z = 0
       up to depth 2 mm (for M3 socket cap heads to recess from below)
  - Central Φ12 counterbore (1 mm deep) at origin, open downward from the
       top face of the base (Z = BASE_THICK .. BASE_THICK - 1)
  - Annular boss centered on origin, sitting on top of base:
       OD 65, ID 55, height 23 mm  (Z = 5 .. 28)
  - Notch in boss wall: angular range 75°–105° (30° wide), heights 0–8 mm
       of boss (= Z = 5 .. 13 absolute), full radial cut through the boss wall

Final orientation: length axes are X and Y (base sides), boss axis is +Z (up).
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
BASE_SIDE  = 100.0
BASE_THICK = 5.0

M6_PATTERN_SIDE = 75.0
M6_DIAM         = 6.5

M3_DIAG         = 25.0                       # diagonal of M3 hole pattern
M3_PATTERN_SIDE = M3_DIAG / math.sqrt(2)     # ≈ 17.678
M3_DIAM         = 3.2
CB_DIAM         = 7.0                        # M7 counterbore diameter
CB_DEPTH        = 2.0                        # counterbore depth (from bottom)

# Central Φ12 counterbore (top-face pocket, e.g. shaft/bearing seat)
CENTER_CB_DIAM  = 12.0
CENTER_CB_DEPTH = 1.0

BOSS_OD = 65.0
BOSS_ID = 55.0
BOSS_H  = 23.0

NOTCH_A_START = 75.0
NOTCH_A_END   = 105.0
NOTCH_H       = 8.0
NOTCH_R       = BOSS_OD / 2 + 2.0
NOTCH_SEG     = 24

# ===== Build base =====
base = m3d.Manifold.cube((BASE_SIDE, BASE_SIDE, BASE_THICK), True)
base = base.translate((0, 0, BASE_THICK / 2))

# 4 × M6 corner holes
m6_hp = M6_PATTERN_SIDE / 2
hole_h = BASE_THICK + 2
for sx in (-1, 1):
    for sy in (-1, 1):
        h = m3d.Manifold.cylinder(hole_h, M6_DIAM / 2, M6_DIAM / 2, 48, True)
        h = h.translate((sx * m6_hp, sy * m6_hp, BASE_THICK / 2))
        base = base - h

# 4 × M3 center holes + Φ7 counterbore (counterbore from bottom)
m3_hp = M3_PATTERN_SIDE / 2
for sx in (-1, 1):
    for sy in (-1, 1):
        # M3 through-hole, full base thickness
        h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2, 32, True)
        h = h.translate((sx * m3_hp, sy * m3_hp, BASE_THICK / 2))
        base = base - h
        # Φ7 counterbore, from Z=0 up to Z=CB_DEPTH (with 1mm undercut for clean cut)
        cb_h = CB_DEPTH + 1.0
        cb = m3d.Manifold.cylinder(cb_h, CB_DIAM / 2, CB_DIAM / 2, 48, False)
        cb = cb.translate((sx * m3_hp, sy * m3_hp, -1.0))
        base = base - cb

# Central Φ12 counterbore, open downward from the top face of the base
ccb_h = CENTER_CB_DEPTH + 1.0   # +1 mm overhang above the top face for clean CSG
ccb = m3d.Manifold.cylinder(ccb_h, CENTER_CB_DIAM / 2, CENTER_CB_DIAM / 2, 64, False)
ccb = ccb.translate((0.0, 0.0, BASE_THICK - CENTER_CB_DEPTH))
base = base - ccb

# ===== Annular boss =====
boss_outer = m3d.Manifold.cylinder(BOSS_H, BOSS_OD / 2, BOSS_OD / 2, 96, False)
boss_inner = m3d.Manifold.cylinder(BOSS_H + 2, BOSS_ID / 2, BOSS_ID / 2, 96, False)
boss_inner = boss_inner.translate((0, 0, -1))
boss = boss_outer - boss_inner
boss = boss.translate((0, 0, BASE_THICK))

# ===== Notch wedge =====
# Cut only from the boss (NOT from the base). Bottom of wedge sits exactly on
# top of base; top extends 0.1 mm past the intended notch height for clean CSG.
wedge_pts = [(0.0, 0.0)]
for i in range(NOTCH_SEG + 1):
    a_deg = NOTCH_A_START + i * (NOTCH_A_END - NOTCH_A_START) / NOTCH_SEG
    a_rad = math.radians(a_deg)
    wedge_pts.append((NOTCH_R * math.cos(a_rad), NOTCH_R * math.sin(a_rad)))
notch = m3d.CrossSection([wedge_pts]).extrude(NOTCH_H + 0.1)
notch = notch.translate((0, 0, BASE_THICK))   # bottom of wedge = top of base, exactly

# Subtract the notch from the boss ONLY, then union with base.
boss = boss - notch

# ===== Combine =====
part = base + boss

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("baseplate.stl")
with out.open("wb") as f:
    f.write(b"POV3D baseplate".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

print(f"wrote {out} ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}")
print(f"  volume:        {part.volume():8.2f} mm^3")
print(f"  surface area:  {part.surface_area():8.2f} mm^2")
print(f"  M6 corners at (±{m6_hp:.2f}, ±{m6_hp:.2f})")
print(f"  M3 centers at (±{m3_hp:.3f}, ±{m3_hp:.3f})  (diagonal {M3_DIAG} mm)")
