"""
Build POV 3D rim_ring STL using manifold3d.

Geometry (all mm, axis along +Z, base bottom at Z=0; CCW positive angles,
0 deg = +X axis):

  Feature 1 - Base annulus:
      ID 60, OD 170, height 3.5  (Z = 0 .. 3.5)
      Notch cutout: remove the band r > 40 (Phi > 80),
                    angles -45 deg .. -40 deg,
                    Z = 1.5 .. 3.5  (notch depth 2mm)
      Result: inner ring r in [30, 40] is full 3.5mm tall everywhere;
              outer ring r in [40, 85] is 3.5mm tall everywhere except in
              the -45..-40 deg wedge where only the bottom 1.5mm remains.

  Feature 2 - 16 Phi3.2 M3 through-holes:
      PCD Phi70  (R = 35)  x 8 holes
      PCD Phi155 (R = 77.5) x 8 holes
      Both rings: angles = 22.5 + k * 45  for k = 0..7
      Through the full Z range. No counterbores.

  Feature 3 - Outer rim boss:
      ID 165, OD 170 (2.5 mm wall), height 5.5  (Z = 3.5 .. 9.0)
      Two angular cutouts (boss only):
          - 5 deg .. 0 deg   (5 deg-wide gap straddling +X axis)
          - 45 deg .. -40 deg (aligned with Feature-1 notch)

Total part height: 9.0 mm.
Print orientation: flat on bed, base down.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
# Base annulus
BASE_ID = 60.0
BASE_OD = 170.0
BASE_H  = 3.5           # Z = 0 .. 3.5

# Notch in base (outer band only, top half)
NOTCH_R_MIN = 40.0      # Phi 80
NOTCH_A_S   = -45.0     # deg
NOTCH_A_E   = -40.0     # deg
NOTCH_Z_S   = 1.5       # Z lower (notch depth = BASE_H - NOTCH_Z_S = 2.0)
NOTCH_Z_E   = BASE_H    # Z upper

# Outer rim boss
RIM_ID  = 165.0
RIM_OD  = 170.0
RIM_H   = 5.5           # Z = BASE_H .. BASE_H + RIM_H = 3.5 .. 9.0

# Rim-boss angular cutouts (boss only)
RIM_CUT1_A_S = -5.0
RIM_CUT1_A_E =  0.0
RIM_CUT2_A_S = -45.0
RIM_CUT2_A_E = -40.0

TOTAL_H = BASE_H + RIM_H   # 9.0

# 16 Phi3.2 M3 through-holes
M3_DIAM = 3.2
INNER_PCD_R = 35.0           # Phi 70
OUTER_PCD_R = 77.5            # Phi 155
HOLE_ANGLES = [22.5 + k * 45.0 for k in range(8)]
PATTERN_INNER = [(INNER_PCD_R * math.cos(math.radians(a)),
                  INNER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]
PATTERN_OUTER = [(OUTER_PCD_R * math.cos(math.radians(a)),
                  OUTER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]

CYL_SEG  = 240
HOLE_SEG = 32

# ===== Helpers =====
def annulus(z0, h, r_in, r_out, segments=CYL_SEG):
    """Return a manifold annulus extending from Z=z0 to Z=z0+h."""
    outer = m3d.Manifold.cylinder(h, r_out, r_out, segments, False)
    inner = m3d.Manifold.cylinder(h + 2.0, r_in, r_in, segments, False)
    inner = inner.translate((0.0, 0.0, -1.0))
    ring = outer - inner
    return ring.translate((0.0, 0.0, z0))

def wedge(a_start_deg, a_end_deg, r, h, z0, n_seg=24):
    """Build a pie wedge centered at origin, sweeping a_start..a_end (deg) at
    radius r, extruded by h starting at Z=z0. r should be larger than any
    geometry it must clear."""
    pts = [(0.0, 0.0)]
    for i in range(n_seg + 1):
        a = math.radians(a_start_deg + i * (a_end_deg - a_start_deg) / n_seg)
        pts.append((r * math.cos(a), r * math.sin(a)))
    w = m3d.CrossSection([pts]).extrude(h)
    return w.translate((0.0, 0.0, z0))

# ===== Build the solid =====

# Base annulus (full)
base = annulus(0.0, BASE_H, BASE_ID / 2, BASE_OD / 2)

# Notch in base: remove the outer band (r > 40) in the wedge -45..-40 deg
# from Z=2.5 to Z=5. Subtract intersection of:
#   - the wedge (clears full OD radially)
#   - an annulus (cuts only r > NOTCH_R_MIN)
# at Z in [NOTCH_Z_S, NOTCH_Z_E].
notch_h = NOTCH_Z_E - NOTCH_Z_S          # 2.5
notch_clearance_r = BASE_OD / 2 + 2.0    # 87
notch_wedge = wedge(NOTCH_A_S, NOTCH_A_E, notch_clearance_r,
                    notch_h + 0.4, NOTCH_Z_S - 0.2, n_seg=24)
# Annulus that contains only material with r > NOTCH_R_MIN within the wedge:
notch_outer_ann = annulus(NOTCH_Z_S - 0.2, notch_h + 0.4,
                          NOTCH_R_MIN, BASE_OD / 2 + 1.0)
notch_cutter = m3d.Manifold.batch_boolean(
    [notch_wedge, notch_outer_ann], m3d.OpType.Intersect)
base = base - notch_cutter

# Outer rim boss (annular)
rim = annulus(BASE_H, RIM_H, RIM_ID / 2, RIM_OD / 2)

# Two angular cutouts in the rim boss only (base intact under them, except
# where Feature 1 has already cut). Use wedges that clear past the OD.
rim_clearance_r = RIM_OD / 2 + 2.0       # 87
rim_cut1 = wedge(RIM_CUT1_A_S, RIM_CUT1_A_E, rim_clearance_r,
                 RIM_H + 0.4, BASE_H - 0.2, n_seg=24)
rim_cut2 = wedge(RIM_CUT2_A_S, RIM_CUT2_A_E, rim_clearance_r,
                 RIM_H + 0.4, BASE_H - 0.2, n_seg=24)
rim = rim - rim_cut1 - rim_cut2

part = base + rim

# ===== Drill 16 Phi3.2 through-holes =====
def drill_through(part, x, y):
    hole_h = TOTAL_H + 2.0
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2,
                              HOLE_SEG, False)
    h = h.translate((x, y, -1.0))
    return part - h

for (x, y) in PATTERN_INNER:
    part = drill_through(part, x, y)
for (x, y) in PATTERN_OUTER:
    part = drill_through(part, x, y)

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("rim_ring.stl")
_header = b"POV3D rim_ring"
assert len(_header) <= 80, f"STL header too long: {len(_header)} bytes"
with out.open("wb") as f:
    f.write(_header.ljust(80, b" "))
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
print(f"  16 Phi3.2 through-holes (8 on PCD Phi70, 8 on PCD Phi155)")
print(f"  angles: 22.5 + k*45 (k=0..7) = {[round(a,1) for a in HOLE_ANGLES]}")

# Sanity-check binary STL: 80-byte header + u32 + 50 bytes/triangle
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, (
    f"STL size mismatch: expected {_expected} (84+{len(tris)}*50), got {_actual}"
)
print(f"  STL size OK: {_actual} bytes (= 84 + {len(tris)}*50)")
