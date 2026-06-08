"""
Build POV 3D mounting flange STL using manifold3d.

Geometry (all dimensions mm, axis along +Z):

  - Base ring (disc):    ID 65, OD 170, thickness 3       (Z = 0 .. 3)
  - Outer rim boss:      ID 165, OD 170 (wall 2.5 mm),
                         height 7                          (Z = 3 .. 10)
                         Two angular cutouts removing boss material only:
                            -  0° .. 10° (10° wedge)
                            - 40° .. 50° (10° wedge)
                         The base remains intact under both cutouts.
  - Hole pattern (16 total, each M3 + Φ7×2 counterbore opening from bottom):
       Outer PCD 155 (R=77.5), 8 holes at 0°, 45°, ..., 315°
       Inner PCD 72.5 (R=36.25), 8 holes at 0°, 45°, ..., 315°
       Each hole: Φ3.2 through (Z=0..3) + Φ7 counterbore (Z=0..2).

Final orientation: base bottom at Z=0, top of rim boss at Z=10.
Print orientation: flat on bed, base down.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
BASE_OD   = 170.0
BASE_ID   = 65.0
BASE_T    = 3.0

BOSS_OD   = 170.0
BOSS_ID   = 165.0
BOSS_H    = 7.0
TOTAL_H   = BASE_T + BOSS_H   # 10

M3_DIAM   = 3.2
CB_DIAM   = 7.0
CB_DEPTH  = 2.0
N_HOLES   = 8
HOLE_ROTATION = 22.5  # CCW 22.5°

INNER_HOLE_R = 36.25      # PCD 72.5
OUTER_HOLE_R = 77.5       # PCD 155

CUT1_A_S = -5.0
CUT1_A_E = 0.0
CUT2_A_S = -45.0
CUT2_A_E = -40.0

CYL_SEG   = 192       # facets for the big disc
HOLE_SEG  = 32
WEDGE_SEG = 24

# ===== Helpers =====
def pie_wedge_cross_section(r, a_start_deg, a_end_deg, seg):
    """CrossSection of a pie wedge from origin (for boss cutout incl. center)."""
    pts = [(0.0, 0.0)]
    for i in range(seg + 1):
        t = i / seg
        a = math.radians(a_start_deg + t * (a_end_deg - a_start_deg))
        pts.append((r * math.cos(a), r * math.sin(a)))
    return m3d.CrossSection([pts])

# ===== Build base ring (annular: OD 170, ID 65, T 3) =====
base_outer = m3d.Manifold.cylinder(BASE_T, BASE_OD / 2, BASE_OD / 2, CYL_SEG, False)
base_inner = m3d.Manifold.cylinder(BASE_T + 2, BASE_ID / 2, BASE_ID / 2, CYL_SEG, False)
base_inner = base_inner.translate((0, 0, -1))
base = base_outer - base_inner

# ===== Outer rim boss (annular ring on top, Z=3..10) =====
ob_outer = m3d.Manifold.cylinder(BOSS_H, BOSS_OD / 2, BOSS_OD / 2, CYL_SEG, False)
ob_inner = m3d.Manifold.cylinder(BOSS_H + 2, BOSS_ID / 2, BOSS_ID / 2, CYL_SEG, False)
ob_inner = ob_inner.translate((0, 0, -1))
rim_boss = ob_outer - ob_inner
rim_boss = rim_boss.translate((0, 0, BASE_T))

# ===== Cutouts from rim boss (0-10° and 40-50°) — boss only =====
cutout_r = BOSS_OD / 2 + 2.0
for a_s, a_e in ((CUT1_A_S, CUT1_A_E), (CUT2_A_S, CUT2_A_E)):
    cutout_xs = pie_wedge_cross_section(cutout_r, a_s, a_e, WEDGE_SEG)
    cutout = cutout_xs.extrude(BOSS_H + 0.2)
    cutout = cutout.translate((0, 0, BASE_T - 0.1))
    rim_boss = rim_boss - cutout

# ===== Union base + boss =====
part = base + rim_boss

# ===== Hole pattern: 16 M3 + Φ7 counterbore (from bottom) =====
hole_h = BASE_T + 2.0
cb_h   = CB_DEPTH + 1.0

for hole_R in (INNER_HOLE_R, OUTER_HOLE_R):
    for k in range(N_HOLES):
        ang = math.radians(k * 360.0 / N_HOLES + HOLE_ROTATION)
        cx = hole_R * math.cos(ang)
        cy = hole_R * math.sin(ang)
        # M3 through-hole
        h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2, HOLE_SEG, False)
        h = h.translate((cx, cy, -1.0))
        part = part - h
        # Φ7 counterbore (from Z=0 up to Z=CB_DEPTH, with 1mm undercut)
        cb = m3d.Manifold.cylinder(cb_h, CB_DIAM / 2, CB_DIAM / 2, HOLE_SEG, False)
        cb = cb.translate((cx, cy, -1.0))
        part = part - cb

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("mounting_flange.stl")
with out.open("wb") as f:
    f.write(b"POV3D mounting flange OD170 ID65 T3 / rim boss H7 / 2 cutouts / 16 M3+CB".ljust(80, b" "))
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
print(f"  inner hole PCD R = {INNER_HOLE_R}  ({N_HOLES} holes @ 0°,45°,...,315°)")
print(f"  outer hole PCD R = {OUTER_HOLE_R}  ({N_HOLES} holes @ 0°,45°,...,315°)")
print(f"  rim boss cutouts: {CUT1_A_S:g}°-{CUT1_A_E:g}° and {CUT2_A_S:g}°-{CUT2_A_E:g}° (boss only)")
