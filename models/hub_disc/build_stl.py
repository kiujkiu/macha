"""
Build POV 3D hub disc STL using manifold3d.

Geometry (all mm, axis along +Z, base bottom at Z=0):

  - Base disc (solid):     Φ165 × thickness 3        (Z = 0 .. 3)
  - Lower center boss:     Φ80  × 2.5                (Z = 3 .. 5.5)  solid
  - Upper center boss:     Φ60  × 3.5                (Z = 5.5 .. 9)  solid
  - Outer rim boss:        ID 145 / OD 165 × 2.5     (Z = 3 .. 5.5)  annular

  - 24 holes (axes along Z, Φ3.2 through):
      A — center diamond (4 holes): rhombus diagonals 12 & 15
          positions (±6, 0), (0, ±7.5); CB Φ7 × 4 mm deep,
          opens from the TOP face (Z = 5 .. 9, recessed into upper Φ60 boss)
      B — center square   (4 holes): corners of 30×30 square (±15, ±15)
          CB Φ4.2 × 4 mm deep, opens from the BOTTOM face (Z = 0 .. 4)
      C — inner PCD ring  (8 holes): PCD Φ70 (R=35), rotated by
          RING_HOLE_ROTATION (default 22.5° CCW)
          CB Φ4.2 × 4 mm deep, opens from the BOTTOM face (Z = 0 .. 4)
      D — outer PCD ring  (8 holes): PCD Φ155 (R=77.5), rotated by
          RING_HOLE_ROTATION (default 22.5° CCW)
          CB Φ4.2 × 4 mm deep, opens from the BOTTOM face (Z = 0 .. 4)

  - For the bottom-opening CBs (B/C/D): depth 4 mm > base thickness 3 mm,
    so the CB cuts 3 mm of base plus 1 mm into whatever sits above.
  - For the top-opening diamond CBs: 4 mm depth is fully inside the upper
    Φ60 boss (3.5 mm) plus 0.5 mm into the lower Φ80 boss below.

Final orientation: base bottom at Z=0, top of upper center boss at Z=9.
Print orientation: flat on bed, base down.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
BASE_OD = 165.0
BASE_T  = 3.0      # Z = 0 .. 3

LOWER_BOSS_D = 80.0
LOWER_BOSS_T = 2.5   # Z = 3 .. 5.5

UPPER_BOSS_D = 60.0
UPPER_BOSS_T = 3.5   # Z = 5.5 .. 9

RIM_BOSS_ID = 145.0
RIM_BOSS_OD = 165.0
RIM_BOSS_T  = 2.5    # Z = 3 .. 5.5

# Rim-boss angular cutout (removes boss only — base remains intact under it)
RIM_CUTOUT_A_S = 0.0
RIM_CUTOUT_A_E = 5.0

TOTAL_H = BASE_T + LOWER_BOSS_T + UPPER_BOSS_T   # 9

# Hole specs
M3_DIAM   = 3.2
CB_A_DIAM = 7.0    # diamond holes
CB_B_DIAM = 4.2    # square / PCD-70 / PCD-155 holes
CB_DEPTH  = 4.0    # 4 mm pocket depth

# Center counterbore — Φ6.2 × 2.2 mm, opens from the BOTTOM face (Z=0..2.2)
# at (0, 0). Pocket only (no through-hole), recessed into the base from below.
CENTER_CB_DIAM  = 6.2
CENTER_CB_DEPTH = 2.2

# Direction toggle: the central diamond (pattern A) counterbore now opens
# from the TOP face (top of upper boss, Z=TOTAL_H) downward, so the screw
# head sits recessed inside the upper Φ60 boss top face. All other 20
# counterbores (square / PCD-70 / PCD-155) still open from the bottom.
DIAMOND_CB_FROM_TOP = True

# Angular rotation (degrees, CCW positive) applied to BOTH PCD ring patterns
# (PCD70 and PCD155). The 4 diamond holes and 4 square holes are NOT rotated.
RING_HOLE_ROTATION = 22.5

# Pattern A — center diamond, diagonals 12 and 15
DIAG_X = 12.0
DIAG_Y = 15.0
PATTERN_A = [( DIAG_X/2, 0.0),
             (-DIAG_X/2, 0.0),
             ( 0.0,  DIAG_Y/2),
             ( 0.0, -DIAG_Y/2)]

# Pattern B — center square 30×30
SQUARE_SIDE = 30.0
PATTERN_B = [( SQUARE_SIDE/2,  SQUARE_SIDE/2),
             (-SQUARE_SIDE/2,  SQUARE_SIDE/2),
             ( SQUARE_SIDE/2, -SQUARE_SIDE/2),
             (-SQUARE_SIDE/2, -SQUARE_SIDE/2)]

# Pattern C — inner PCD ring Φ70 (8 holes), rotated by RING_HOLE_ROTATION
INNER_PCD_R = 35.0    # Φ70
PATTERN_C = [(INNER_PCD_R * math.cos(math.radians(k * 360.0 / 8 + RING_HOLE_ROTATION)),
              INNER_PCD_R * math.sin(math.radians(k * 360.0 / 8 + RING_HOLE_ROTATION)))
             for k in range(8)]

# Pattern D — outer PCD ring Φ155 (8 holes), rotated by RING_HOLE_ROTATION
OUTER_PCD_R = 77.5    # Φ155
PATTERN_D = [(OUTER_PCD_R * math.cos(math.radians(k * 360.0 / 8 + RING_HOLE_ROTATION)),
              OUTER_PCD_R * math.sin(math.radians(k * 360.0 / 8 + RING_HOLE_ROTATION)))
             for k in range(8)]

CYL_SEG  = 192
HOLE_SEG = 32

# ===== Build the solid =====
# Base disc (solid cylinder)
base = m3d.Manifold.cylinder(BASE_T, BASE_OD / 2, BASE_OD / 2, CYL_SEG, False)

# Lower center boss (solid)
lower_boss = m3d.Manifold.cylinder(LOWER_BOSS_T, LOWER_BOSS_D / 2,
                                   LOWER_BOSS_D / 2, CYL_SEG, False)
lower_boss = lower_boss.translate((0.0, 0.0, BASE_T))

# Upper center boss (solid)
upper_boss = m3d.Manifold.cylinder(UPPER_BOSS_T, UPPER_BOSS_D / 2,
                                   UPPER_BOSS_D / 2, CYL_SEG, False)
upper_boss = upper_boss.translate((0.0, 0.0, BASE_T + LOWER_BOSS_T))

# Outer rim boss (annular ring on top of base)
rim_outer = m3d.Manifold.cylinder(RIM_BOSS_T, RIM_BOSS_OD / 2,
                                  RIM_BOSS_OD / 2, CYL_SEG, False)
rim_inner = m3d.Manifold.cylinder(RIM_BOSS_T + 2.0, RIM_BOSS_ID / 2,
                                  RIM_BOSS_ID / 2, CYL_SEG, False)
rim_inner = rim_inner.translate((0.0, 0.0, -1.0))
rim_boss  = rim_outer - rim_inner
rim_boss  = rim_boss.translate((0.0, 0.0, BASE_T))

# Cutout: pie wedge from origin to a radius past OD, subtracted from rim_boss only
# so the base remains intact under the wedge.
import math as _math
_wedge_pts = [(0.0, 0.0)]
_wedge_r = RIM_BOSS_OD / 2 + 2.0
_n_seg = 24
for _i in range(_n_seg + 1):
    _a = _math.radians(RIM_CUTOUT_A_S +
                       _i * (RIM_CUTOUT_A_E - RIM_CUTOUT_A_S) / _n_seg)
    _wedge_pts.append((_wedge_r * _math.cos(_a), _wedge_r * _math.sin(_a)))
_wedge = m3d.CrossSection([_wedge_pts]).extrude(RIM_BOSS_T + 0.2)
_wedge = _wedge.translate((0.0, 0.0, BASE_T - 0.1))
rim_boss = rim_boss - _wedge

part = base + lower_boss + upper_boss + rim_boss

# ===== Drill holes =====
def drill_through_and_cb(part, x, y, cb_diam, cb_from_top=False):
    """Cut a Φ3.2 through-hole and a CB Φ × CB_DEPTH.

    cb_from_top=False (default): CB opens from the BOTTOM face (Z=0 .. CB_DEPTH).
    cb_from_top=True:            CB opens from the TOP face
                                 (Z = TOTAL_H - CB_DEPTH .. TOTAL_H).
    A small `slop` is added so the cut breaks cleanly through the surface.
    """
    slop = 0.1
    hole_h = TOTAL_H + 2.0
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2, HOLE_SEG, False)
    h = h.translate((x, y, -1.0))
    part = part - h

    cb_h = CB_DEPTH + slop
    cb = m3d.Manifold.cylinder(cb_h, cb_diam / 2, cb_diam / 2, HOLE_SEG, False)
    if cb_from_top:
        # span Z = (TOTAL_H - CB_DEPTH) .. (TOTAL_H + slop)
        cb = cb.translate((x, y, TOTAL_H - CB_DEPTH))
    else:
        # span Z = -slop .. CB_DEPTH
        cb = cb.translate((x, y, -slop))
    part = part - cb
    return part

for (x, y) in PATTERN_A:
    part = drill_through_and_cb(part, x, y, CB_A_DIAM,
                                cb_from_top=DIAMOND_CB_FROM_TOP)   # Φ7 CB
for (x, y) in PATTERN_B:
    part = drill_through_and_cb(part, x, y, CB_B_DIAM)              # Φ4.2 CB
for (x, y) in PATTERN_C:
    part = drill_through_and_cb(part, x, y, CB_B_DIAM)              # Φ4.2 CB
for (x, y) in PATTERN_D:
    part = drill_through_and_cb(part, x, y, CB_B_DIAM)              # Φ4.2 CB

# Center counterbore — Φ6.2 × 2.2 mm pocket only, opens from the BOTTOM
# (no through-hole). Cut a cylinder from Z = -slop .. CENTER_CB_DEPTH.
_center_slop = 0.1
_center_cb = m3d.Manifold.cylinder(CENTER_CB_DEPTH + _center_slop,
                                   CENTER_CB_DIAM / 2,
                                   CENTER_CB_DIAM / 2,
                                   HOLE_SEG, False)
_center_cb = _center_cb.translate((0.0, 0.0, -_center_slop))
part = part - _center_cb

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("hub_disc.stl")
with out.open("wb") as f:
    f.write(b"POV3D hub_disc OD165 / 2-boss + rim / 24 holes".ljust(80, b" "))
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

print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume:        {part.volume():10.2f} mm^3")
print(f"  surface area:  {part.surface_area():10.2f} mm^2")
print(f"  4 + 4 + 8 + 8 = 24 holes total + 1 center Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} CB (bottom)")
# Sanity-check binary STL: 80-byte header + u32 + 50 bytes/triangle
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, (
    f"STL size mismatch: expected {_expected} (84+{len(tris)}*50), got {_actual}"
)
print(f"  STL size OK: {_actual} bytes (= 84 + {len(tris)}*50)")
