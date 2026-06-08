"""
Build the POV 3D L-bracket STL using manifold3d (boolean CSG).

Geometry (mm):
  - Bracket length      = 200
  - Cross-section: L with two 15 mm legs, 5 mm wall thickness
  - Inside corner angle = 105°
  - 4 × M3 clearance holes (ø3.2) through leg A
      * X positions: 6.5, 65.5, 134.5, 193.5 mm
        (centered: length/2 ± 64 ± 59/2 = 100 ± 64 ± 29.5)
      * Y position : 10 mm from outer corner
                     (= 5 mm from leg A's free end)
      * Hole axis perpendicular to leg A face

Output STL is oriented so length is along +X, leg A lies in the XY plane
(bottom of leg A on Z = 0), leg B extends upward + tilted into -Y.
"""

import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
LENGTH    = 140.0
LEG_A     = 15.0
LEG_B     = 6.0
THICK_A   = 3.0
THICK_B   = 3.0
ANGLE_DEG = 90.0

HOLE_DIAM            = 3.2
HOLE_Y_FROM_FREE_END = 5.0
HOLE_SEGMENTS        = 48      # smoother hole cylinders

# Hole X positions — kept at original (6, 66, 134) after right-side trim to 170.
# Original 4-hole pattern was [6, 66, 134, 194] on 200 mm; X=194 is cut off.
HOLE_X_POSITIONS = [6.0, 66.0, 134.0]
HOLE_Y = LEG_A - HOLE_Y_FROM_FREE_END
HOLE_R = HOLE_DIAM / 2.0

theta = math.radians(ANGLE_DEG)
ct = math.cos(theta)
st = math.sin(theta)

# Inner corner: intersection of (Z = THICK_A) with the inner face of leg B
u_inner = (THICK_A + THICK_B * ct) / st
P3_y    = THICK_B * st + u_inner * ct

P0 = (0.0, 0.0)
P1 = (LEG_A, 0.0)
P2 = (LEG_A, THICK_A)
P3 = (P3_y, THICK_A)
P5 = (LEG_B * ct,                    LEG_B * st)
P4 = (P5[0] + THICK_B * st,          P5[1] - THICK_B * ct)
profile = [P0, P1, P2, P3, P4, P5]

# ===== Build solid =====
cs    = m3d.CrossSection([profile])
solid = cs.extrude(LENGTH)
# After extrude: manifold X = u = Y_geom, manifold Y = v = Z_geom, manifold Z = length

# Subtract M3 hole cylinders (axis along Z_geom = manifold Y)
hole_height = THICK_A + 2.0
for hx in HOLE_X_POSITIONS:
    cyl = m3d.Manifold.cylinder(hole_height, HOLE_R, HOLE_R, HOLE_SEGMENTS, True)
    # cylinder is centered on Z axis. Rotate so axis is along +Y.
    cyl = cyl.rotate((-90, 0, 0))   # Rx(-90°): +Z → +Y
    cyl = cyl.translate((HOLE_Y, THICK_A / 2, hx))
    solid = solid - cyl

# ===== Rotate to length-along-X orientation =====
# Currently manifold (X, Y, Z) = (Y_geom, Z_geom, length).
# Target:    final     (X, Y, Z) = (length, Y_geom, Z_geom).
# That is the cyclic permutation Rz(90°) then Ry(90°).
solid = solid.rotate((0, 0, 90))
solid = solid.rotate((0, 90, 0))

# ===== Write binary STL =====
mesh  = solid.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("l_bracket.stl")
with out.open("wb") as f:
    f.write(b"L-bracket 200 / 15x15 / t5 / 105deg / 4xM3".ljust(80, b" "))
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
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}")
print(f"  volume:        {solid.volume():8.2f} mm^3")
print(f"  surface area:  {solid.surface_area():8.2f} mm^2")
print(f"  cross-section P3 (inner corner): ({P3_y:.3f}, {THICK_A})")
print(f"  hole X positions: {HOLE_X_POSITIONS}")
print(f"  hole Y position : {HOLE_Y}")
