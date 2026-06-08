"""
Build POV 3D flanged annular disc STL using manifold3d.

Geometry (all dimensions mm, axis along +Z):

  - Base ring (disc):    ID 65, OD 165, thickness 5      (Z = 0 .. 5)
  - Inner boss ring:     ID 65, OD 80,  thickness 2      (Z = 5 .. 7)
                         8 × M3 (Φ3.2) through-holes (depth 7 mm, through boss + base)
                         on a PCD = 72.5 (R = 36.25), at 0°, 45°, ..., 315°
  - Outer boss ring:     ID 145, OD 165, thickness 2     (Z = 5 .. 7)
                         8 × M3 (Φ3.2) through-holes (depth 7 mm, through boss + base)
                         on a PCD = 155 (R = 77.5), at 0°, 45°, ..., 315°
                         Cutout: outer boss removed in the angular wedge 40°–50°
                         (10° gap). Base stays intact under that wedge. This wipes
                         out the 45° outer-boss hole — final outer hole count = 7.
  - Slot/notch:          annular wedge cut from the disc, R = 40 .. 82.5,
                         Z = 3 .. 7 (4 mm tall), angular 0°–10°.
                         Cuts upper 2 mm of base AND the FULL outer boss in
                         that wedge. Bottom 3 mm of base remain; the outer
                         boss is completely removed in the wedge (no cap
                         above the slot). Slot also clips the 0° outer-boss
                         hole.

Final orientation: base bottom at Z=0, top of bosses at Z=7.
Print orientation: flat on bed, base down.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
BASE_OD   = 165.0
BASE_ID   = 65.0
BASE_T    = 4.5  # 底盘厚度 5→4.5

INNER_BOSS_OD = 80.0
INNER_BOSS_ID = 65.0
OUTER_BOSS_OD = 165.0
OUTER_BOSS_ID = 145.0
BOSS_T        = 2.5     # boss thickness above base (2→2.5)
TOTAL_H       = BASE_T + BOSS_T   # 7.5

M3_DIAM = 3.2
N_HOLES = 8
HOLE_ROTATION = -22.5  # 16 通孔顺时针旋转 20° (CW 负角)
M42_DIAM = 4.2         # 外圈 8 个沉孔直径
M42_DEPTH = 4.0        # 沉孔深度 (从底部 z=0 向上)

INNER_HOLE_R = (INNER_BOSS_ID/2 + INNER_BOSS_OD/2) / 2   # 36.25
OUTER_HOLE_R = (OUTER_BOSS_ID/2 + OUTER_BOSS_OD/2) / 2   # 77.5

OUTER_CUTOUT_A_S = 40.0
OUTER_CUTOUT_A_E = 45.0

SLOT_R_IN  = INNER_BOSS_OD / 2   # 40
SLOT_R_OUT = OUTER_BOSS_OD / 2   # 82.5
SLOT_Z_BOT = 2.0
SLOT_Z_TOP = 7.0
SLOT_A_S   = 0.0
SLOT_A_E   = 5.0

CYL_SEG = 192       # facets for the big disc
HOLE_SEG = 32
WEDGE_SEG = 24

# ===== Helpers =====
def annular_wedge_cross_section(r_in, r_out, a_start_deg, a_end_deg, seg):
    """CrossSection of an annular wedge (r_in..r_out, between a_start..a_end)."""
    pts = []
    # outer arc CCW
    for i in range(seg + 1):
        t = i / seg
        a = math.radians(a_start_deg + t * (a_end_deg - a_start_deg))
        pts.append((r_out * math.cos(a), r_out * math.sin(a)))
    # inner arc CW (reverse)
    for i in range(seg + 1):
        t = i / seg
        a = math.radians(a_end_deg - t * (a_end_deg - a_start_deg))
        pts.append((r_in * math.cos(a), r_in * math.sin(a)))
    return m3d.CrossSection([pts])

def pie_wedge_cross_section(r, a_start_deg, a_end_deg, seg):
    """CrossSection of a pie wedge from origin (for boss cutout incl. center)."""
    pts = [(0.0, 0.0)]
    for i in range(seg + 1):
        t = i / seg
        a = math.radians(a_start_deg + t * (a_end_deg - a_start_deg))
        pts.append((r * math.cos(a), r * math.sin(a)))
    return m3d.CrossSection([pts])

# ===== Build base disc (annular: OD 165, ID 65, T 5) =====
base_outer = m3d.Manifold.cylinder(BASE_T, BASE_OD / 2, BASE_OD / 2, CYL_SEG, False)
base_inner = m3d.Manifold.cylinder(BASE_T + 2, BASE_ID / 2, BASE_ID / 2, CYL_SEG, False)
base_inner = base_inner.translate((0, 0, -1))
base = base_outer - base_inner

# ===== Inner boss (annular ring on top, Z=5..7) =====
ib_outer = m3d.Manifold.cylinder(BOSS_T, INNER_BOSS_OD / 2, INNER_BOSS_OD / 2, CYL_SEG, False)
ib_inner = m3d.Manifold.cylinder(BOSS_T + 2, INNER_BOSS_ID / 2, INNER_BOSS_ID / 2, CYL_SEG, False)
ib_inner = ib_inner.translate((0, 0, -1))
inner_boss = ib_outer - ib_inner
inner_boss = inner_boss.translate((0, 0, BASE_T))

# ===== Outer boss (annular ring on top, Z=5..7) =====
ob_outer = m3d.Manifold.cylinder(BOSS_T, OUTER_BOSS_OD / 2, OUTER_BOSS_OD / 2, CYL_SEG, False)
ob_inner = m3d.Manifold.cylinder(BOSS_T + 2, OUTER_BOSS_ID / 2, OUTER_BOSS_ID / 2, CYL_SEG, False)
ob_inner = ob_inner.translate((0, 0, -1))
outer_boss = ob_outer - ob_inner
outer_boss = outer_boss.translate((0, 0, BASE_T))

# ===== Cutout from outer boss (40°-50° wedge) — boss only =====
cutout_r = OUTER_BOSS_OD / 2 + 2.0
cutout_xs = pie_wedge_cross_section(cutout_r, OUTER_CUTOUT_A_S, OUTER_CUTOUT_A_E, WEDGE_SEG)
cutout = cutout_xs.extrude(BOSS_T + 0.2)
cutout = cutout.translate((0, 0, BASE_T - 0.1))
outer_boss = outer_boss - cutout

# ===== Union base + bosses =====
part = base + inner_boss + outer_boss

# ===== Slot (annular wedge, R 40..82.5, Z 3..7, 0°-10°) =====
slot_xs = annular_wedge_cross_section(SLOT_R_IN, SLOT_R_OUT,
                                      SLOT_A_S, SLOT_A_E, WEDGE_SEG)
slot = slot_xs.extrude(SLOT_Z_TOP - SLOT_Z_BOT)
slot = slot.translate((0, 0, SLOT_Z_BOT))
part = part - slot

# ===== M3 through-holes — inner ring (8 @ -20°, 25°, ..., 295°), 顺时针 20° =====
hole_h = TOTAL_H + 2.0
for k in range(N_HOLES):
    ang = math.radians(k * 360.0 / N_HOLES + HOLE_ROTATION)
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM/2, M3_DIAM/2, HOLE_SEG, False)
    h = h.translate((INNER_HOLE_R * math.cos(ang),
                     INNER_HOLE_R * math.sin(ang),
                     -1.0))
    part = part - h

# ===== M3 through-holes — outer ring (8 @ -20°, 25°, ..., 295°), 顺时针 20° =====
for k in range(N_HOLES):
    ang = math.radians(k * 360.0 / N_HOLES + HOLE_ROTATION)
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM/2, M3_DIAM/2, HOLE_SEG, False)
    h = h.translate((OUTER_HOLE_R * math.cos(ang),
                     OUTER_HOLE_R * math.sin(ang),
                     -1.0))
    part = part - h

# ===== M4.2 沉孔 — 内圈 8 个孔位置, 从底部 z=0 向上 4mm =====
cbore_h = M42_DEPTH + 0.1
for k in range(N_HOLES):
    ang = math.radians(k * 360.0 / N_HOLES + HOLE_ROTATION)
    cb = m3d.Manifold.cylinder(cbore_h, M42_DIAM/2, M42_DIAM/2, HOLE_SEG, False)
    cb = cb.translate((INNER_HOLE_R * math.cos(ang),
                       INNER_HOLE_R * math.sin(ang),
                       -0.1))
    part = part - cb

# ===== M4.2 沉孔 — 外圈 8 个孔位置, 从底部 z=0 向上 4mm =====
for k in range(N_HOLES):
    ang = math.radians(k * 360.0 / N_HOLES + HOLE_ROTATION)
    cb = m3d.Manifold.cylinder(cbore_h, M42_DIAM/2, M42_DIAM/2, HOLE_SEG, False)
    cb = cb.translate((OUTER_HOLE_R * math.cos(ang),
                       OUTER_HOLE_R * math.sin(ang),
                       -0.1))
    part = part - cb

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("flange_disc.stl")
with out.open("wb") as f:
    f.write(b"POV3D flange disc OD165 ID65 T5 / inner+outer bosses / 16 M3 / slot+cutout".ljust(80, b" "))
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
print(f"  outer hole PCD R = {OUTER_HOLE_R}  (8 holes initially; 45° eaten by cutout = 7 effective)")
