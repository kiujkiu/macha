"""
Build POV 3D rim_top_disc STL.

A Φ170 × 5 mm flat disc that sits on TOP of rim_ring's upper-wall top face
(Z = 9 .. 14 in the assembled frame; here the disc's own build frame puts
the disc at Z = 0 .. 5 with ribs at Z = 5 .. 35).

Features:
  • 16 × Φ3.2 M3 through-holes — identical positions to rim_ring's 16 holes
    (8 on PCD Φ70 + 8 on PCD Φ155, angles 22.5 + k·45°, k=0..7).
  • 2 radial reinforcement ribs, 5 mm thick × 30 mm tall, running ALONG
    +X (radial direction), centered at Y = ±47.5 (center-to-center 95 mm).
    Rib length is the chord of the disc at the outer rib face (~137 mm) so
    the rib's footprint stays inside the disc.
  • 2 × Φ3.2 M3 through-holes drilled along +Y through BOTH ribs at
    (X = −34.3, Z = 24) and (X = −64.3, Z = 24) — these align with the
    l_bracket_170x60 gusset holes when the bracket is installed (vleg flat
    on disc, hleg fin 90 mm wide clamped between the two ribs).

Print orientation: disc bottom on bed (Z = 0 .. 5), ribs sticking up.
A1 mini build volume 180 mm — Φ170 disc fits.
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== Disc =====
DISC_OD     = 200.0          # was 170, +30 to give ribs more chord-length room.
                              # NOTE: 200 > A1 mini 180 mm build volume → print diagonally
                              # (200 < 180 × √2 ≈ 254 mm) or split.
DISC_THICK  = 5.0
DISC_SEG    = 240

# ===== M3 hole pattern (mirrors rim_ring exactly) =====
M3_DIAM         = 3.2
M3_SEG          = 24
INNER_PCD_R     = 35.0    # rim PCD Φ70
OUTER_PCD_R     = 77.5    # rim PCD Φ155
HOLE_ANGLES_DEG = [22.5 + k * 45.0 for k in range(8)]

# ===== 2 radial reinforcement ribs =====
RIB_THICK    = 5.0
RIB_HEIGHT   = 30.0
RIB_CC       = 95.0           # center-to-center spacing (bracket WIDTH 90 + rib 5)
RIB_HALF_OUT = RIB_CC/2 + RIB_THICK/2   # 50 — outer face Y
# chord at outer rib face — used to bound rib length so it stays inside disc
RIB_HALF_LEN = math.sqrt((DISC_OD/2)**2 - RIB_HALF_OUT**2) - 0.5   # 0.5 mm inset
RIB_LENGTH   = 2 * RIB_HALF_LEN
RIB_Y_CENTERS = (+RIB_CC/2, -RIB_CC/2)   # +47.5, −47.5

# ===== 6 M3 + Φ4.2 × 3 mm CB through-holes (user-specified mount pattern) =====
# All in disc XY frame (rim center = origin). M3 through goes all the way
# through the disc; Φ4.2 counterbore opens from BOTTOM face up 3 mm
# (so the bolt head can recess flush from below).
SPECIAL_M3_DIAM  = 3.2
SPECIAL_CB_DIAM  = 4.2
SPECIAL_CB_DEPTH = 3.0
SPECIAL_POSITIONS = [
    ( 5.0,  37.5), ( 5.0, -37.5),
    (51.0,  37.5), (51.0, -37.5),
    (60.0,  22.0), (60.0, -22.0),
]

# ===== Rectangular slot on the +Y rib =====
# 15 × 6 mm slot cut through the rib's Y-thickness. Slot bottom is at
# rib-local Z=14 (= disc-frame Z = DISC_THICK + 14 = 19); slot center X is
# 16 mm right of disc center.
SLOT_WIDTH    = 15.0
SLOT_HEIGHT   = 6.0
SLOT_X_CENTER = 35.0                   # was 16, +X 35 from disc center
SLOT_BOTTOM_Z = DISC_THICK + 11.0      # was DISC_THICK+14; now 16 in disc build frame (11 above rib base)
SLOT_RIB_Y    = +RIB_CC/2               # only the +Y rib (+47.5)

# ===== 2 M3 through-holes through both ribs (mate with bracket gusset holes) =====
# Bracket gusset hole positions in disc build frame:
#   X_disc = X_assembly_local − HLEG_DIST_FROM_CENTER
#          = (−z_print_bracket) − 14.3
#          = −20 − 14.3 = −34.3    (gusset hole at print Z=20)
#          = −50 − 14.3 = −64.3    (gusset hole at print Z=50)
#   Z_disc = z_assembly_local + 0   (disc build frame: disc top is at Z=DISC_THICK=5;
#                                    bracket hole's z_assembly_local = x_print_bracket = 19,
#                                    so Z_disc = 5 + 19 = 24)
RIB_HOLE_DIAM = 3.2
RIB_HOLE_X    = (-34.3, -64.3)
RIB_HOLE_Z    = DISC_THICK + 19.0      # 24

# ===== Build =====
disc = m3d.Manifold.cylinder(DISC_THICK, DISC_OD/2, DISC_OD/2, DISC_SEG, False)
part = disc

# Add 2 ribs on top of disc
for ry in RIB_Y_CENTERS:
    rib = m3d.Manifold.cube((RIB_LENGTH, RIB_THICK, RIB_HEIGHT), False)
    rib = rib.translate((-RIB_LENGTH/2, ry - RIB_THICK/2, DISC_THICK))
    part = part + rib

# 16 M3 holes through disc (vertical, along +Z)
for R in (INNER_PCD_R, OUTER_PCD_R):
    for a in HOLE_ANGLES_DEG:
        cx = R * math.cos(math.radians(a))
        cy = R * math.sin(math.radians(a))
        h = m3d.Manifold.cylinder(DISC_THICK + 2, M3_DIAM/2, M3_DIAM/2,
                                  M3_SEG, False)
        h = h.translate((cx, cy, -1.0))
        part = part - h

# 6 special holes: Φ3.2 M3 through + Φ4.2 × 3 mm CB from BOTTOM
for (hx, hy) in SPECIAL_POSITIONS:
    # M3 through-hole, full disc thickness + slop
    h = m3d.Manifold.cylinder(DISC_THICK + 2,
                              SPECIAL_M3_DIAM/2, SPECIAL_M3_DIAM/2,
                              M3_SEG, False)
    h = h.translate((hx, hy, -1.0))
    part = part - h
    # Φ4.2 counterbore opening from the bottom (Z=0) going up SPECIAL_CB_DEPTH (=3)
    cb = m3d.Manifold.cylinder(SPECIAL_CB_DEPTH + 1.0,
                               SPECIAL_CB_DIAM/2, SPECIAL_CB_DIAM/2,
                               48, False)
    cb = cb.translate((hx, hy, -1.0))   # spans Z=-1 .. SPECIAL_CB_DEPTH (=3)
    part = part - cb

# Rectangular slot through the +Y rib
slot = m3d.Manifold.cube((SLOT_WIDTH, RIB_THICK + 2.0, SLOT_HEIGHT), False)
slot = slot.translate((SLOT_X_CENTER - SLOT_WIDTH/2,
                       SLOT_RIB_Y - RIB_THICK/2 - 1.0,
                       SLOT_BOTTOM_Z))
part = part - slot

# 2 M3 holes through both ribs (horizontal, along +Y axis)
# Cylinder default axis is +Z; rotate −90° about X so axis becomes +Y.
for hx in RIB_HOLE_X:
    h = m3d.Manifold.cylinder(RIB_CC + RIB_THICK + 2.0,    # 102 mm; spans Y=−51 .. +51
                              RIB_HOLE_DIAM/2, RIB_HOLE_DIAM/2,
                              M3_SEG, False)
    h = h.rotate((-90, 0, 0))
    h = h.translate((hx, -(RIB_CC/2 + RIB_THICK/2 + 1.0), RIB_HOLE_Z))
    part = part - h

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("rim_top_disc.stl")
_header = b"POV3D rim_top_disc"
assert len(_header) <= 80
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
print(f"  volume: {part.volume():.2f} mm³")
print(f"  rib length (chord-bounded): {RIB_LENGTH:.2f} mm")

_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, f"STL size mismatch: {_expected} vs {_actual}"
print(f"  STL size OK: {_actual} bytes")
