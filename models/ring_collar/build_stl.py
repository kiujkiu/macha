"""
Build the POV 3D annular ring collar STL using manifold3d.

Geometry:
  - Outer diameter:  Φ80 mm
  - Inner diameter:  Φ65 mm  (wall thickness 7.5 mm)
  - Height:          13 mm
  - Notch:           angular range 0°–30° (30° wedge),
                     heights 0–8 mm (lower 8 mm of wall),
                     cuts through full wall thickness

Final orientation:
  - Ring axis along +Z; bottom at Z=0, top at Z=13.
  - 0° angle along +X axis (CCW from +X is positive angle).
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
OD      = 80.0
ID      = 65.0
HEIGHT  = 13.0

NOTCH_A_START = 0.0
NOTCH_A_END   = 30.0
NOTCH_H       = 6.0
NOTCH_R       = OD / 2 + 2.0    # extend just past OD for clean outer cut
NOTCH_SEG     = 28              # arc segments

CYL_SEG = 128                   # cylinder facets

# ===== Build ring =====
outer = m3d.Manifold.cylinder(HEIGHT, OD / 2, OD / 2, CYL_SEG, False)
inner = m3d.Manifold.cylinder(HEIGHT + 2, ID / 2, ID / 2, CYL_SEG, False)
inner = inner.translate((0, 0, -1))
ring  = outer - inner

# ===== Notch wedge (subtract from ring only) =====
wedge_pts = [(0.0, 0.0)]
for i in range(NOTCH_SEG + 1):
    a_deg = NOTCH_A_START + i * (NOTCH_A_END - NOTCH_A_START) / NOTCH_SEG
    a_rad = math.radians(a_deg)
    wedge_pts.append((NOTCH_R * math.cos(a_rad), NOTCH_R * math.sin(a_rad)))
notch = m3d.CrossSection([wedge_pts]).extrude(NOTCH_H + 0.1)
notch = notch.translate((0, 0, -0.05))   # tiny slop below z=0

part = ring - notch

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("ring_collar.stl")
with out.open("wb") as f:
    f.write(b"POV3D ring collar OD80 ID65 H13 / notch 0-30deg H8".ljust(80, b" "))
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
print(f"  volume:        {part.volume():8.2f} mm^3")
print(f"  surface area:  {part.surface_area():8.2f} mm^2")
