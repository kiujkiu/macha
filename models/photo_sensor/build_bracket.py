"""
sensor_bracket — a SIMPLE flat plate on the disc TOP that reaches OUT past the
disc edge and hangs the photo-interrupter beyond it.

WHY: the disc-mounting screws (−92.5,±20) can only be driven TOP-DOWN, so the
plate sits on the disc TOP and the M3s go top-down into the disc. The plate
then cantilevers OUTWARD past the Φ200 edge; the module mounts on that
outboard underside so its PCB sits BEYOND the disc rim (no PCB↔disc clash).
Because the plate is on top, the whole sensor is raised ~11mm vs the old
under-disc position → index_vane is made taller to match.

Assembly frame (θ=180). R_SLOT=112 so the module's inner edge (R102) clears
the Φ200 disc edge (R100). beam ends up at (−112, 0, 38.7).

  • plate: Z46.7–51.7 (5mm) on the disc top, X[−122,−86]×Y[−24,26].
  • RED (−92.5,±20): M3 thru + Φ6×3 head CB on top — top-down into the disc.
  • BLUE module holes (−105,17)/(−119,17): M3 thru + Φ4.2×4 top CB; module hangs
    FLUSH under the outboard plate (PCB back at Z46.7). 3 relief pockets (2mm)
    in the plate UNDERSIDE for the module's up-pointing solder leads.
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

R_SLOT = 112.0
PL_Z0, PL_Z1 = 46.7, 52.7                       # plate on the disc top (6 mm; 5→6, 2026-07-14)
PL_X0, PL_X1, PL_Y0, PL_Y1 = -127.0, -86.0, -24.0, 26.0   # outer edge +5mm (outer BLUE hole was 3mm from edge → 8mm)
RED  = [(-92.5, 20.0), (-92.5, -20.0)]
BLUE = [(-R_SLOT + 7.0, 17.0), (-R_SLOT - 7.0, 17.0)]   # (−105,17)/(−119,17)
M3_CLEAR = 3.4
CB_D, CB_DEPTH = 4.2, 4.0                        # BLUE counterbore (top)
HEAD_CB_D, HEAD_CB_H = 6.0, 3.0                  # RED head CB (top)


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def zcyl(z0, z1, r, x, y, seg=32):
    return m3d.Manifold.cylinder(z1-z0, r, r, seg, False).translate((x, y, z0))

plate = box(PL_X0, PL_X1, PL_Y0, PL_Y1, PL_Z0, PL_Z1)

# RED — top-down M3 into the disc, PLAIN through-hole (NO counterbore, per user)
for (x, y) in RED:
    plate = plate - zcyl(PL_Z0 - 1, PL_Z1 + 1, M3_CLEAR/2, x, y)

# BLUE — module hangs flush under the outboard plate: M3 thru + Φ4.2×4 top CB
for (x, y) in BLUE:   # Φ3.2 直通 (顶沉取消 2026-07-14)
    plate = plate - zcyl(PL_Z0 - 1, PL_Z1 + 1, 3.2/2, x, y)

# 3 relief pockets (2mm) in the UNDERSIDE for the module's up-leads (R_SLOT=112)
POCKETS = [(-122.0, -116.0, -4.5, 4.5),   # 2 opto legs near (−119,0)
           (-108.0, -102.0, -4.5, 4.5),   # 2 opto legs near (−105,0)
           (-115.85, -108.15, 15.0, 21.5)]   # 宽 9→7.7 (2026-07-14)  # 3 header tails near (−112,18)
for (x0, x1, y0, y1) in POCKETS:
    plate = plate - box(x0, x1, y0, y1, PL_Z0 - 1, PL_Z1 + 1)   # 挖穿 (2026-07-14, 原 2mm 底面避空)

# ---- export ----
mesh = plate.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("sensor_bracket.stl")
with out.open("wb") as f:
    f.write(b"POV3D sensor_bracket".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n)); f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
v = verts
print(f"sensor_bracket.stl  {len(tris)} tris  X {v[:,0].min():.1f}..{v[:,0].max():.1f}  "
      f"Y {v[:,1].min():.1f}..{v[:,1].max():.1f}  Z {v[:,2].min():.1f}..{v[:,2].max():.1f}  "
      f"vol {plate.volume()/1000:.2f}cm³")
print(f"flat plate on disc top (Z{PL_Z0}-{PL_Z1}), cantilever out to R~122; module flush below "
      f"(R_SLOT={R_SLOT}, beam Z38.7); RED top-down, BLUE M3+Φ4.2 CB + 3 pockets")
