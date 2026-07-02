"""
Saddle / strap clamp with a SQUARE bridge for a 6×6 square object, bolting to a
plate with two M6 screws 25 mm apart.  manifold3d.

Spec (user 2026-06-23, revised):
  - Square bridge, inner 6×6 mm (holds a 6 mm square bar lying on the plate, axis Y).
  - Material thickness 3 mm.
  - 2 × M6 (Φ6.5) clearance holes, left & right, c-c 25 mm, through 3 mm feet.

Geometry (object axis = Y, object 6×6 sits on the plate Z=0):
  - Square inverted-U bridge: inner X ±3, Z 0..6; walls 3 mm → outer X ±6, top Z 6..9.
  - Two feet (X ±6 .. ±18.5) lie flat on the plate, 3 mm thick, each with an M6 hole.
  Open bottom → object rests on the plate; the square top wall presses it down.

Print: feet on the bed (Z=0 down), bridge up; the 6 mm flat ceiling bridges fine.
NOTE: inner is 6.0 exactly (per spec) = zero clearance to a 6 mm object; widen
`INNER` slightly (e.g. 6.3) if you need an assembly fit.
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
INNER   = 6.0            # inner square side (holds 6 mm object)
HALF    = INNER / 2.0    # 3.0
ZIN     = INNER          # 6.0 inner height (square)
T       = 3.0            # material thickness
OHALF   = HALF + T       # 6.0 outer half-width of the bridge
HTOP    = ZIN + T        # 9.0 outer top
W       = 14.0           # bridge / foot width (along Y = object axis)
M6_DIAM = 6.5
HOLE_CC = 25.0
HX      = HOLE_CC / 2.0  # 12.5
FOOT    = HX + 6.0       # 18.5 foot outer X

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), True).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))

# ===== Build =====
bridge = _box(-OHALF, OHALF, -W/2, W/2, 0, HTOP)          # outer 12×14×9
inner  = _box(-HALF, HALF, -W/2-1, W/2+1, -1, ZIN)        # square channel, open bottom
bridge = bridge - inner

footR = _box(OHALF, FOOT, -W/2, W/2, 0, T)
footL = _box(-FOOT, -OHALF, -W/2, W/2, 0, T)
body = bridge + footR + footL

for sx in (-1, 1):
    h = m3d.Manifold.cylinder(T + 2, M6_DIAM/2, M6_DIAM/2, 48, True).translate((sx*HX, 0, T/2))
    body = body - h

# ===== Export STL =====
mesh = body.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("saddle_clamp_sq6.stl")
with out.open("wb") as f:
    f.write(b"saddle_clamp_sq6".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

assert 84 + len(tris) * 50 == out.stat().st_size, "STL size mismatch (header overflow?)"

print(f"wrote {out} ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}  (foot ±{FOOT:g})")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}  (width {W:g})")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}  (top {HTOP:g})")
print(f"  inner square {INNER:g}×{INNER:g} / wall {T:g} / outer bridge {2*OHALF:g}×{HTOP:g}")
print(f"  2 × Φ{M6_DIAM:g} M6 @ X=±{HX:g} (c-c {HOLE_CC:g}), through {T:g} feet")
print(f"  volume: {body.volume():9.2f} mm^3")
