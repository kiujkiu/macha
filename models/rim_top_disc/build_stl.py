"""
Build POV 3D rim_top_disc STL.

A Φ170 × 5 mm flat disc that sits on TOP of rim_ring's upper-wall top face
(Z = 9 .. 14 in the assembled frame; here the disc's own build frame puts
the disc at Z = 0 .. 5 with ribs at Z = 5 .. 35).

Features:
  • 16 × Φ3.2 M3 through-holes — identical positions to rim_ring's 16 holes
    (8 on PCD Φ70 + 8 on PCD Φ155, angles 22.5 + k·45°, k=0..7).
    Each with a Φ7 × 2.5 mm counterbore opening from the TOP face.
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
DISC_THICK  = 6.0          # was 5, then 7
DISC_SEG    = 240

# ===== M3 hole pattern (mirrors rim_ring exactly) =====
M3_DIAM         = 3.2
M3_SEG          = 24
M3_CB_DIAM      = 7.0     # counterbore from TOP face, for bolt head recess
M3_CB_DEPTH     = 2.5
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

# ===== 8 M3 through-holes + Φ4.2 bottom CBs (user-specified mount pattern) =====
# All in disc XY frame (rim center = origin). M3 through goes all the way
# through the disc; Φ4.2 counterbore opens from BOTTOM face up
# (so the bolt head can recess flush from below).
# The 4 BOSS positions additionally get a Φ10 × 3 boss on the TOP face
# (M3 drilled through disc + boss) and a DEEPER 7 mm CB (2026-06-11);
# 6 (disc) + 3 (boss) − 7 (CB) = 2 mm of thread-side material left.
SPECIAL_M3_DIAM  = 3.2         # plain holes
SPECIAL_CB_DIAM  = 4.2         # plain holes round CB
SPECIAL_CB_DEPTH      = 4.0    # CB depth at the 4 plain positions
SPECIAL_BOSS_DIAM     = 6.0    # was 10; →6 on 2026-06-12
SPECIAL_BOSS_H        = 3.0
# Boss holes (2026-06-12): Φ3.5 through + HEX nut pocket from the bottom,
# across-flats 5.4 × 2.2 deep (M3 nut). 6+3−2.2 = 6.8 mm thread-side material.
BOSS_THRU_DIAM   = 3.5
BOSS_HEX_AF      = 5.4                      # across-flats
BOSS_HEX_DEPTH   = 2.2                      # was 3 in the first request, then 2.2
BOSS_HEX_R       = BOSS_HEX_AF / math.sqrt(3.0)   # circumradius ≈ 3.06
# The 6 boss holes mount the pi2hub75e PCB (82 × 62, 6 × Φ3.3 holes; STEP at
# /mnt/d/工程项目/硬件/pov/MTR_BOARD_V0.1_451/PCB/pi2hub75e.step).
# Mapping for COMPONENT SIDE UP (proper rotation, det +1; PCB frame origin =
# board corner, connector edge toward disc +X):
#   disc_X = PCB_OFF_X − pcb_y,  disc_Y = pcb_x − PCB_OFF_Y
PCB_HOLES = [   # (pcb_x, pcb_y) of the 6 Φ3.3 mounting holes
    ( 3.2, 58.8), ( 3.2, 48.8),
    (79.0, 58.8), (79.0, 48.8),
    ( 3.5,  3.1), (78.4,  3.0),
]
PCB_OFF_X = 53.8
PCB_OFF_Y = 41.0
SPECIAL_BOSS_POSITIONS = [
    (round(PCB_OFF_X - py, 2), round(px - PCB_OFF_Y, 2)) for (px, py) in PCB_HOLES
]   # → (-5, -37.8) (5, -37.8) (-5, 38) (5, 38) (50.7, -37.5) (50.8, 37.4)
SPECIAL_PLAIN_POSITIONS = [
    (62.0,  21.0), (62.0, -21.0),   # +2 right on 2026-06-12 (was 60)
    (88.0,  28.5), (88.0, -28.5),   # +26 right of the (62, ±21) pair, 57 c-to-c (PSU ears)
    (-92.5,  20.0), (-92.5, -20.0), # X=-92.5 pair, 40 c-to-c (was -85, moved -7.5 on 2026-06-12)
]

# ===== Rectangular slots on the ribs =====
# 15 × 10 mm slots cut through each rib's Y-thickness, both with the same
# bottom height. +Y rib slot X-center 41; -Y rib slot X-center 18.5
# (added 2026-06-12).
SLOT_WIDTH    = 15.0
SLOT_HEIGHT   = 16.0                    # was 6, 10; →16 on 2026-06-12 (reaches the rib top: open notch)
SLOT_BOTTOM_Z = DISC_THICK + 14.0      # was +12; raised 2 on 2026-06-12
SLOTS = [
    (41.0, +RIB_CC/2),    # +Y rib (+47.5)
    (18.5, -RIB_CC/2),    # -Y rib (-47.5)
]

# ===== 1 M4 through-hole outside the rim_ring footprint =====
# Φ4.2 vertical through-hole BETWEEN the two ribs, hugging the -Y rib
# (center 5 from the rib inner face at Y=-45), radius kept at rim_ring
# R85 + 7 = 92 → center (82.85, -40). Required: ≥5 edge clearance from the
# plain hole at (88, -28.5) — actual edge-edge 8.4. (position iterated
# 3× on 2026-06-12 per user)
M4_DIAM = 4.2
M4_R    = 85.0 + 7.0
M4_Y    = -40.0
M4_X    = math.sqrt(M4_R**2 - M4_Y**2)   # 82.85

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

# 16 M3 holes through disc (vertical, along +Z) + Φ7 × 2.5 CB from TOP
for R in (INNER_PCD_R, OUTER_PCD_R):
    for a in HOLE_ANGLES_DEG:
        cx = R * math.cos(math.radians(a))
        cy = R * math.sin(math.radians(a))
        h = m3d.Manifold.cylinder(DISC_THICK + 2, M3_DIAM/2, M3_DIAM/2,
                                  M3_SEG, False)
        h = h.translate((cx, cy, -1.0))
        part = part - h
        cb = m3d.Manifold.cylinder(M3_CB_DEPTH + 1.0,
                                   M3_CB_DIAM/2, M3_CB_DIAM/2,
                                   48, False)
        cb = cb.translate((cx, cy, DISC_THICK - M3_CB_DEPTH))
        part = part - cb

# Boss positions: Φ10 × 3 boss on top, Φ3.5 through disc+boss,
# hex nut pocket (AF 5.3 × 3 deep) from the bottom.
for (hx, hy) in SPECIAL_BOSS_POSITIONS:
    boss = m3d.Manifold.cylinder(SPECIAL_BOSS_H,
                                 SPECIAL_BOSS_DIAM/2, SPECIAL_BOSS_DIAM/2,
                                 48, False)
    boss = boss.translate((hx, hy, DISC_THICK))
    part = part + boss
    h = m3d.Manifold.cylinder(DISC_THICK + SPECIAL_BOSS_H + 2,
                              BOSS_THRU_DIAM/2, BOSS_THRU_DIAM/2,
                              M3_SEG, False)
    h = h.translate((hx, hy, -1.0))
    part = part - h
    # hexagonal pocket: 6-segment "cylinder" with circumradius AF/√3
    hexp = m3d.Manifold.cylinder(BOSS_HEX_DEPTH + 1.0,
                                 BOSS_HEX_R, BOSS_HEX_R, 6, False)
    hexp = hexp.translate((hx, hy, -1.0))
    part = part - hexp
# Plain positions: Φ3.2 M3 through + Φ4.2 × 4 round CB from the bottom
for (hx, hy) in SPECIAL_PLAIN_POSITIONS:
    h = m3d.Manifold.cylinder(DISC_THICK + 2,
                              SPECIAL_M3_DIAM/2, SPECIAL_M3_DIAM/2,
                              M3_SEG, False)
    h = h.translate((hx, hy, -1.0))
    part = part - h
    cb = m3d.Manifold.cylinder(SPECIAL_CB_DEPTH + 1.0,
                               SPECIAL_CB_DIAM/2, SPECIAL_CB_DIAM/2,
                               48, False)
    cb = cb.translate((hx, hy, -1.0))
    part = part - cb

# M4 through-hole outside the ring footprint
h = m3d.Manifold.cylinder(DISC_THICK + 2, M4_DIAM/2, M4_DIAM/2, M3_SEG, False)
h = h.translate((M4_X, M4_Y, -1.0))
part = part - h

# Rectangular slots through the ribs
for (sx, sy) in SLOTS:
    slot = m3d.Manifold.cube((SLOT_WIDTH, RIB_THICK + 2.0, SLOT_HEIGHT), False)
    slot = slot.translate((sx - SLOT_WIDTH/2,
                           sy - RIB_THICK/2 - 1.0,
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
