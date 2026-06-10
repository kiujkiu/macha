"""
Build the POV 3D baseplate_collar STL (merged baseplate + ring collar).

Combines:
  - baseplate: square 100×100×5 base + central boss Φ65/Φ55 H23
    (4×M6 corner holes, 4×M3+Φ7 CB center holes, Φ12×1 center CB on top,
    boss notch 75°–105° H8)
  - ring_collar: annular ring Φ80/Φ65 H13 sleeved over the boss
    (notch 75°–105° H6, aligned with the boss notch on the +Y side)

Since collar ID (Φ65) equals boss OD (Φ65), the two surfaces coincide and
the merged solid forms a single continuous annulus r=27.5..40 from Z=5..18,
stepping down to r=27.5..32.5 from Z=18..28 (boss only above collar top).

Final orientation: print flat on bed (Z up), base bottom at Z=0.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Baseplate parameters =====
BASE_SIDE  = 100.0
BASE_THICK = 5.0

M6_PATTERN_SIDE = 75.0
M6_DIAM         = 6.5

M3_DIAG         = 25.0
M3_PATTERN_SIDE = M3_DIAG / math.sqrt(2)
M3_DIAM         = 3.2
CB_DIAM         = 7.0
CB_DEPTH        = 2.0

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

# ===== Ring collar parameters (aligned with baseplate) =====
COLLAR_OD = 80.0
COLLAR_ID = 65.0                  # = BOSS_OD → press-fit alignment
COLLAR_H  = 13.0
COLLAR_Z0 = BASE_THICK            # ring bottom sits on base top (Z=5)
COLLAR_NOTCH_A_START = NOTCH_A_START
COLLAR_NOTCH_A_END   = NOTCH_A_END
COLLAR_NOTCH_H       = 6.0
COLLAR_NOTCH_R       = COLLAR_OD / 2 + 2.0
COLLAR_NOTCH_SEG     = 28

assert abs(COLLAR_ID - BOSS_OD) < 1e-9, "collar ID must equal boss OD for alignment"

# ===== Base =====
base = m3d.Manifold.cube((BASE_SIDE, BASE_SIDE, BASE_THICK), True)
base = base.translate((0, 0, BASE_THICK / 2))

# 4 × M6 corner holes (through)
m6_hp = M6_PATTERN_SIDE / 2
hole_h = BASE_THICK + 2
for sx in (-1, 1):
    for sy in (-1, 1):
        h = m3d.Manifold.cylinder(hole_h, M6_DIAM / 2, M6_DIAM / 2, 48, True)
        h = h.translate((sx * m6_hp, sy * m6_hp, BASE_THICK / 2))
        base = base - h

# 4 × M3 center holes + Φ7 counterbore (from bottom)
m3_hp = M3_PATTERN_SIDE / 2
for sx in (-1, 1):
    for sy in (-1, 1):
        h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2, 32, True)
        h = h.translate((sx * m3_hp, sy * m3_hp, BASE_THICK / 2))
        base = base - h
        cb_h = CB_DEPTH + 1.0
        cb = m3d.Manifold.cylinder(cb_h, CB_DIAM / 2, CB_DIAM / 2, 48, False)
        cb = cb.translate((sx * m3_hp, sy * m3_hp, -1.0))
        base = base - cb

# Central Φ12 × 1 mm CB on top face
ccb_h = CENTER_CB_DEPTH + 1.0
ccb = m3d.Manifold.cylinder(ccb_h, CENTER_CB_DIAM / 2, CENTER_CB_DIAM / 2, 64, False)
ccb = ccb.translate((0.0, 0.0, BASE_THICK - CENTER_CB_DEPTH))
base = base - ccb

# ===== Boss =====
boss_outer = m3d.Manifold.cylinder(BOSS_H, BOSS_OD / 2, BOSS_OD / 2, 96, False)
boss_inner = m3d.Manifold.cylinder(BOSS_H + 2, BOSS_ID / 2, BOSS_ID / 2, 96, False)
boss_inner = boss_inner.translate((0, 0, -1))
boss = boss_outer - boss_inner
boss = boss.translate((0, 0, BASE_THICK))

# Boss notch (cuts the boss wall only)
wedge_pts = [(0.0, 0.0)]
for i in range(NOTCH_SEG + 1):
    a_deg = NOTCH_A_START + i * (NOTCH_A_END - NOTCH_A_START) / NOTCH_SEG
    a_rad = math.radians(a_deg)
    wedge_pts.append((NOTCH_R * math.cos(a_rad), NOTCH_R * math.sin(a_rad)))
notch = m3d.CrossSection([wedge_pts]).extrude(NOTCH_H + 0.1)
notch = notch.translate((0, 0, BASE_THICK))
boss = boss - notch

# ===== Ring collar (sleeved over boss) =====
collar_outer = m3d.Manifold.cylinder(COLLAR_H, COLLAR_OD / 2, COLLAR_OD / 2, 128, False)
collar_inner = m3d.Manifold.cylinder(COLLAR_H + 2, COLLAR_ID / 2, COLLAR_ID / 2, 128, False)
collar_inner = collar_inner.translate((0, 0, -1))
collar = collar_outer - collar_inner
collar = collar.translate((0, 0, COLLAR_Z0))

# Collar notch (aligned with boss notch on +Y side)
c_wedge_pts = [(0.0, 0.0)]
for i in range(COLLAR_NOTCH_SEG + 1):
    a_deg = COLLAR_NOTCH_A_START + i * (COLLAR_NOTCH_A_END - COLLAR_NOTCH_A_START) / COLLAR_NOTCH_SEG
    a_rad = math.radians(a_deg)
    c_wedge_pts.append((COLLAR_NOTCH_R * math.cos(a_rad), COLLAR_NOTCH_R * math.sin(a_rad)))
c_notch = m3d.CrossSection([c_wedge_pts]).extrude(COLLAR_NOTCH_H + 0.1)
c_notch = c_notch.translate((0, 0, COLLAR_Z0 - 0.05))
collar = collar - c_notch

# ===== Combine =====
part = base + boss + collar

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("baseplate_collar.stl")
_header = b"POV3D baseplate_collar"
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
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}")
print(f"  volume:        {part.volume():8.2f} mm^3")
print(f"  surface area:  {part.surface_area():8.2f} mm^2")
print(f"  notches aligned at {NOTCH_A_START:g}°–{NOTCH_A_END:g}° (boss H{NOTCH_H:g}, collar H{COLLAR_NOTCH_H:g})")

# Sanity-check binary STL size
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, (
    f"STL size mismatch: expected {_expected} (84+{len(tris)}*50), got {_actual}"
)
print(f"  STL size OK: {_actual} bytes (= 84 + {len(tris)}*50)")
