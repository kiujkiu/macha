"""
Build POV 3D L-bracket STL (170 × 60 mm legs, 50 mm wide, 4 mm thick).

L-shape with long leg along +X and short leg along +Z, both 50 mm wide
along Y, 4 mm plate thickness. Outer dimensions are measured to the outside
of each leg (i.e., the long leg extends from X=0 to X=170 along the bottom
face, the short leg from Z=0 to Z=60 along the back face).

Final orientation: long leg sits flat on the bed (Z=0..4), short leg stands
vertical along +Z up to Z=60. Bottom-back corner at (0, 0, 0).

A1 mini build volume 180×180×180 mm — fits (170 × 50 × 60).
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== Parameters =====
LEG_A = 200.0    # long-leg outer length (along X) — was 170, +30 on open end
LEG_B = 70.0     # short-leg outer length (along Z) — was 60, +10 to reach rim outer PCD
WIDTH = 90.0     # width (along Y) — was 80
THICK = 4.0      # plate thickness

# 2 triangular gussets (加强筋) on the inside of the L. Each gusset is a
# right triangle in the XZ plane with vertices (THICK, THICK), (LEG_A, THICK),
# (THICK, LEG_B), extruded along Y by GUSSET_WIDTH.
GUSSET_WIDTH       = 5.0
# 2 gussets: at the 2 Y edges only (middle removed per spec)
GUSSET_Y_POSITIONS = [GUSSET_WIDTH/2, WIDTH - GUSSET_WIDTH/2]  # 2.5, 87.5

# M3 through-holes on the horizontal-leg top face. Three pairs, each pair
# centered on the Y midline (Y = WIDTH/2 = 45). All hleg-top features
# (M3 holes + 4 corner stacks) shifted +30 in X from the original layout
# so they sit ~30 mm farther from the vleg back face.
#   Pair A: X = 125,            spacing 20  → (125, 35)  (125, 55)
#   Pair B: X = 125 + 66 = 191, spacing 20  → (191, 35)  (191, 55)
#   Pair C: X = 38,             spacing 70  → (38, 10)   (38, 80)
HLEG_FEAT_X_SHIFT = 30.0
M3_DIAM       = 3.2
M3_SEG        = 24
M3_Y_CENTER   = WIDTH / 2    # 45
M3_X_A        = HLEG_FEAT_X_SHIFT + 95.0     # 125
M3_SPACING_A  = 20.0
M3_X_B        = M3_X_A + 66.0                # 191
M3_SPACING_B  = 20.0
M3_X_C        = HLEG_FEAT_X_SHIFT + 8.0      # 38
M3_SPACING_C  = 70.0

# The 3 BOTTOM holes (one per pair, the +Y side) are shifted (+1 X, +1 Y)
# relative to the symmetric mid-line position. So the pair is no longer
# strictly collinear in X.
SHIFT_BOT_X   = 1.0
SHIFT_BOT_Y   = 1.0

# 4 corner features on the 170×90 horizontal-leg top face. Each one has:
#   - Φ7 × 2 mm tall boss added on top of hleg
#   - M3 (Φ3.2) through-hole through boss + hleg (total height 6 mm)
#   - Φ4.2 × 4 mm deep counterbore opening from the BOTTOM face up (= depth
#     equals hleg thickness, so the counterbore reaches the boss bottom)
# Placed at the corners of a 49 × 58 mm rectangle (X × Y) centered on the
# centroid of the 4 left-side M3 holes (pairs C + A): center = (52, 45.5).
CORNER_M3_DIAM   = 3.2
CORNER_BOSS_DIAM = 7.0
CORNER_BOSS_H    = 2.0
CORNER_CB_DIAM   = 4.2
CORNER_CB_DEPTH  = 4.0
CORNER_RECT_X    = 49.0
CORNER_RECT_Y    = 58.0
CORNER_CX        = (M3_X_C + (M3_X_C + SHIFT_BOT_X) + M3_X_A + (M3_X_A + SHIFT_BOT_X)) / 4
CORNER_CY        = ((M3_Y_CENTER - M3_SPACING_C/2) + (M3_Y_CENTER + M3_SPACING_C/2 + SHIFT_BOT_Y)
                    + (M3_Y_CENTER - M3_SPACING_A/2) + (M3_Y_CENTER + M3_SPACING_A/2 + SHIFT_BOT_Y)) / 4
CORNER_POSITIONS = [
    (CORNER_CX - CORNER_RECT_X/2, CORNER_CY - CORNER_RECT_Y/2),
    (CORNER_CX + CORNER_RECT_X/2, CORNER_CY - CORNER_RECT_Y/2),
    (CORNER_CX - CORNER_RECT_X/2, CORNER_CY + CORNER_RECT_Y/2),
    (CORNER_CX + CORNER_RECT_X/2, CORNER_CY + CORNER_RECT_Y/2),
]

# 4 × M3 (Φ3.2) through-holes on the 70×90 vertical-leg face. Pattern now
# matches 4 specific rim_ring holes (so the bracket bolts down to the rim
# when the vleg lies flat on the rim's base annulus).
#
# Assembly: bracket rotated −90° about Y from print frame → vleg lies flat,
# hleg points UP. Hleg's print-frame Z=0 face becomes a vertical 200×90 face
# placed HLEG_DIST_FROM_CENTER mm from the rim center (closest face). Vleg
# extends radially out from there. Bracket centered on rim Y axis
# (vleg Y_v = WIDTH/2 ↔ rim Y = 0).
#
# rim_ring hole positions used:  (R, angle)
#   • R = 35  (PCD Φ70)  @ 157.5°  and  202.5°  → 2 inner mating holes
#   • R = 77.5 (PCD Φ155) @ 157.5°  and  202.5°  → 2 outer mating holes
# Mapping to vleg local coords (Y_v ∈ [0,90], Z_v ∈ [0,70]):
#   Y_v = R·sin(angle) + WIDTH/2
#   Z_v = −R·cos(angle) − HLEG_DIST_FROM_CENTER
import math as _m

VLEG_M3_DIAM             = 3.2
RIM_R_IN                 = 35.0           # rim PCD Φ70 radius
RIM_R_OUT                = 77.5           # rim PCD Φ155 radius
RIM_MATING_ANGLES_DEG    = (157.5, 202.5) # symmetric about rim −X axis
HLEG_DIST_FROM_CENTER    = 14.3           # rim center → hleg inner 200×90 face

def _vleg_pos_from_rim(R, ang_deg):
    x_rim = R * _m.cos(_m.radians(ang_deg))
    y_rim = R * _m.sin(_m.radians(ang_deg))
    return (y_rim + WIDTH / 2, -x_rim - HLEG_DIST_FROM_CENTER)

VLEG_M3_POSITIONS = [
    _vleg_pos_from_rim(RIM_R_IN,  RIM_MATING_ANGLES_DEG[0]),  # (58.394, 18.036)
    _vleg_pos_from_rim(RIM_R_IN,  RIM_MATING_ANGLES_DEG[1]),  # (31.606, 18.036)
    _vleg_pos_from_rim(RIM_R_OUT, RIM_MATING_ANGLES_DEG[0]),  # (74.658, 57.301)
    _vleg_pos_from_rim(RIM_R_OUT, RIM_MATING_ANGLES_DEG[1]),  # (15.342, 57.301)
]

# 2 × M3 through-holes drilled ALONG +Y (perpendicular to the gusset triangle
# faces). The single drill passes through both 5-mm-wide gussets (and the air
# in between), giving 2 aligned holes on each gusset face. 15 mm right of the
# gusset's vertical (left) edge; 30 mm vertical spacing.
GUSSET_HOLE_DIAM = 3.2
GUSSET_HOLE_X    = THICK + 15.0           # 19
GUSSET_HOLE_Z1   = 20.0                   # lower hole
GUSSET_HOLE_Z2   = 50.0                   # upper hole (30 mm above)
GUSSET_HOLE_Z_POSITIONS = [GUSSET_HOLE_Z1, GUSSET_HOLE_Z2]

# ===== Build the L =====
# Long horizontal leg
hleg = m3d.Manifold.cube((LEG_A, WIDTH, THICK), False)
# Short vertical leg at the left corner of the L
vleg = m3d.Manifold.cube((THICK, WIDTH, LEG_B), False)
part = hleg + vleg

# Triangular gussets: CrossSection in (X, Z) plane → extrude → rotate around
# X by +90° so the extrusion axis becomes world Y → translate to Y-center.
def make_gusset(y_center):
    cs = m3d.CrossSection([[(THICK, THICK), (LEG_A, THICK), (THICK, LEG_B)]])
    prism = cs.extrude(GUSSET_WIDTH)
    rotated = prism.rotate((90, 0, 0))   # (x, y, z) → (x, -z, y)
    return rotated.translate((0, y_center + GUSSET_WIDTH/2, 0))

for y_c in GUSSET_Y_POSITIONS:
    part = part + make_gusset(y_c)

# Drill 2 × M3 through-holes along +Y through both gussets at once
for hz in GUSSET_HOLE_Z_POSITIONS:
    h = m3d.Manifold.cylinder(WIDTH + 2.0,
                              GUSSET_HOLE_DIAM / 2, GUSSET_HOLE_DIAM / 2,
                              M3_SEG, False)
    # default axis +Z; rotate −90° about X so axis becomes +Y
    h = h.rotate((-90, 0, 0))
    h = h.translate((GUSSET_HOLE_X, -1.0, hz))
    part = part - h

# 6 × M3 through-holes drilled vertically through the horizontal leg.
# Top hole of each pair: at (X_pair, Y_center − spacing/2). Bottom hole:
# at (X_pair + SHIFT_BOT_X, Y_center + spacing/2 + SHIFT_BOT_Y).
m3_positions = []
for (x_val, s_val) in [(M3_X_A, M3_SPACING_A),
                       (M3_X_B, M3_SPACING_B),
                       (M3_X_C, M3_SPACING_C)]:
    m3_positions.append((x_val,                M3_Y_CENTER - s_val / 2))
    m3_positions.append((x_val + SHIFT_BOT_X,  M3_Y_CENTER + s_val / 2 + SHIFT_BOT_Y))

for (hx, hy) in m3_positions:
    h = m3d.Manifold.cylinder(THICK + 2, M3_DIAM / 2, M3_DIAM / 2,
                              M3_SEG, False)
    h = h.translate((hx, hy, -1.0))
    part = part - h

# 4 corner features: add Φ7 × 2 bosses on top of hleg (additive)
for (hx, hy) in CORNER_POSITIONS:
    boss = m3d.Manifold.cylinder(CORNER_BOSS_H,
                                 CORNER_BOSS_DIAM / 2, CORNER_BOSS_DIAM / 2,
                                 48, False)
    boss = boss.translate((hx, hy, THICK))
    part = part + boss

# Φ3.2 M3 through-holes (through boss + hleg, z = -1 .. THICK + BOSS_H + 1)
for (hx, hy) in CORNER_POSITIONS:
    h = m3d.Manifold.cylinder(THICK + CORNER_BOSS_H + 2,
                              CORNER_M3_DIAM / 2, CORNER_M3_DIAM / 2,
                              M3_SEG, False)
    h = h.translate((hx, hy, -1.0))
    part = part - h

# Φ4.2 × 4 mm counterbores opening from the bottom face (z = -1 .. CB_DEPTH)
for (hx, hy) in CORNER_POSITIONS:
    cb = m3d.Manifold.cylinder(CORNER_CB_DEPTH + 1.0,
                               CORNER_CB_DIAM / 2, CORNER_CB_DIAM / 2,
                               48, False)
    cb = cb.translate((hx, hy, -1.0))
    part = part - cb

# 4 × M3 through-holes in vleg (horizontal, along X axis)
for (hy, hz) in VLEG_M3_POSITIONS:
    h = m3d.Manifold.cylinder(THICK + 2, VLEG_M3_DIAM / 2, VLEG_M3_DIAM / 2,
                              M3_SEG, False)
    # Cylinder is along Z by default; rotate around Y so axis becomes X
    h = h.rotate((0, 90, 0))
    h = h.translate((-1.0, hy, hz))
    part = part - h

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("l_bracket_170x60.stl")
_header = b"POV3D l_bracket_170x60"
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
print(f"  volume: {part.volume():.2f} mm³")

# Sanity-check binary STL size
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, f"STL size mismatch: {_expected} vs {_actual}"
print(f"  STL size OK: {_actual} bytes")
