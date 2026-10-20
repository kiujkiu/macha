"""
top_cap_v3 — v3 rotor cap for the top steady-bearing module (double-screen rotor).
PLA. SYMMETRIC (2026-07-10): the v2 L-shape is impossible — both plate faces now
carry screens, so the leg has nowhere to land. Instead screen_plate_v3 grows a
central top TAB (Y ±40, asm Z 259.2..280.7, above the screen tops 264.7) and the
cap becomes a flat symmetric slab with a two-leg CLEVIS that grips the tab.
Axis hardware unchanged: M6x40 flat head + Phi8x50 M6-female standoff through
2x688 (posts/frames = top_bearing *_v2, reused as-is).

Assembly frame (Z = perfboard top, axis = (0,0)); CAPTOP = 292.7.

  1. slab 9 thick: Z 283.7..292.7, X -65..+65 (symmetric), Y +-72. Top face
     FULLY FLAT (asm top = print bottom / bed).
  2. clevis legs 4 thick x2: X -7..-3 and +3..+7 (inner faces grip the 6-thick
     tab), Y +-36, Z 267..292.7 (bottoms clear the screen tops 264.7 by 2.3).
  3. tab fixing: 4 x Phi3.4 along X through both legs at asm (Y=+-22,
     Z={271.0, 276.5}) — matches screen_plate_v3 tab holes; M3x18 through
     leg4+plate6+leg4=14, washer+nut.
  4. axis: Phi6.2 through the slab at (0,0) + Phi13x2.7 head recess cut from
     the slab BOTTOM face. M6x40 flat head sits at 283.7..286.4.
     NOTE: the tab top (280.7) sits 3 under the head — preinstall the M6 screw
     in the cap BEFORE bolting the clevis onto the tab.
  5. counterweight banks BOTH ends (symmetric trim): 19 x Phi6.5 vertical
     holes each side, 品字形 14 pitch; rows A X=+-46 (10 holes,
     Y=(k-4.5)*14) and B X=+-58.12 (9 holes, Y=(k-4)*14). Each with a
     Phi13x2.7 counterbore from the slab TOP face for M6 wafer heads.

PRINT pose (slab top on the bed, legs up), same flip mapping as v1/v2:
    print_z = CAPTOP - asm_z,  print_x = asm_x,  print_y = -asm_y
Built directly in PRINT coordinates. Export: top_cap_v3.stl.
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

M3_CLEAR = 3.4
CAPTOP = 292.7                       # asm Z of the slab top face (print z0)

# --- slab (asm Z 283.7..292.7 -> print z 0..9) ---
SLAB_T = 9.0
TP_HX, TP_HW = 65.0, 72.0            # X +-65, Y +-72 (130 x 144)

# --- clevis legs (asm X +-(3..7), Y +-36, Z 267..292.7) ---
LEG_T  = 4.0
LEG_XI = 3.0                         # inner face = plate face (tab 6 thick)
LEG_HW = 36.0
LEG_ZBOT_ASM = 267.0                 # screen top 264.7 + 2.3
LEG_H = CAPTOP - LEG_ZBOT_ASM        # 25.7 (print z 0..25.7)

# --- axis bore + head recess ---
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7

# --- tab fixing holes (through both legs, along X) ---
SCREW_Y = 22.0                       # asm Y = +-22
SCREW_Z_ASM = [271.0, 276.5]         # -> print z 21.7 / 16.2

# --- M6 counterweight banks (both +-X, symmetric) ---
CW_M6 = 6.5
CW_TRI = 14.0
CW_ROW_DX = CW_TRI * math.sin(math.radians(60))     # 12.12 row-to-row
CW_HOLES = []
for sx in (1.0, -1.0):
    CW_HOLES += [(sx * 46.0, (k - 4.5) * CW_TRI) for k in range(10)]
    CW_HOLES += [(sx * (46.0 + CW_ROW_DX), (k - 4.0) * CW_TRI) for k in range(9)]

# ===================== build (PRINT coordinates) =====================
# slab: print z 0..9, flat face on the bed
cap = m3d.Manifold.cube((2 * TP_HX, 2 * TP_HW, SLAB_T), False) \
        .translate((-TP_HX, -TP_HW, 0.0))
# clevis legs: print z 0..25.7 (fused with the slab, inside its footprint)
for sx in (1.0, -1.0):
    x0 = LEG_XI if sx > 0 else -(LEG_XI + LEG_T)
    cap = cap + m3d.Manifold.cube((LEG_T, 2 * LEG_HW, LEG_H), False) \
            .translate((x0, -LEG_HW, 0.0))
# axis: Phi6.2 through the slab + Phi13x2.7 head recess from the slab bottom
# face (asm 283.7 = print TOP z9); the recess notches the leg roots — intended.
cap = cap - m3d.Manifold.cylinder(SLAB_T + LEG_H + 2, M6_BORE/2, M6_BORE/2, 48, False) \
        .translate((0, 0, -1.0))
cap = cap - m3d.Manifold.cylinder(HEAD_DEPTH + 1, HEAD_D/2, HEAD_D/2, 48, False) \
        .translate((0, 0, SLAB_T - HEAD_DEPTH))
# 4 x Phi3.4 along X through both legs: asm (Y=+-22, Z={271, 276.5});
# Y-symmetric so the print flip (y -> -y) is a no-op.
for az in SCREW_Z_ASM:
    for ay in (SCREW_Y, -SCREW_Y):
        s = m3d.Manifold.cylinder(2 * (LEG_XI + LEG_T) + 2, M3_CLEAR/2, M3_CLEAR/2, 24, False)
        s = s.rotate((0, 90, 0))
        cap = cap - s.translate((-(LEG_XI + LEG_T) - 1.0, ay, CAPTOP - az))
# 2 x 19 Phi6.5 counterweight holes (vertical, through the slab), each with a
# Phi13x2.7 counterbore from the slab TOP face (asm 292.7 = print z0, bed side)
for (cx, cy) in CW_HOLES:                     # Y-symmetric rows: flip is a no-op
    cap = cap - m3d.Manifold.cylinder(SLAB_T + 2, CW_M6/2, CW_M6/2, 32, False) \
            .translate((cx, cy, -1.0))
    cap = cap - m3d.Manifold.cylinder(HEAD_DEPTH + 1, HEAD_D/2, HEAD_D/2, 48, False) \
            .translate((cx, cy, -1.0))

# ===================== export =====================
def write_stl(part, name):
    mesh = part.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name(name)
    header = f"POV3D {name[:-4]}".encode()[:80]
    with out.open("wb") as f:
        f.write(header.ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1 - v0, v2 - v0)
            L = float(np.linalg.norm(n))
            if L > 0: n = n / L
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    assert 84 + len(tris)*50 == out.stat().st_size
    v = verts
    print(f"{name:16s} {len(tris):5d} tris  "
          f"X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  "
          f"Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}  "
          f"Z {v[:,2].min():6.2f}..{v[:,2].max():6.2f}  vol {part.volume()/1000:.1f}cm³")
    return v

v = write_stl(cap, "top_cap_v3.stl")
# print-pose bbox self-check (X2D 256^3)
assert abs(v[:, 0].min() + TP_HX) < 1e-3 and abs(v[:, 0].max() - TP_HX) < 1e-3
assert abs(v[:, 1].min() + TP_HW) < 1e-3 and abs(v[:, 1].max() - TP_HW) < 1e-3
assert abs(v[:, 2].min()) < 1e-3 and abs(v[:, 2].max() - LEG_H) < 1e-3
for span, lim in ((2 * TP_HX, 256), (2 * TP_HW, 256), (LEG_H, 256)):
    assert span < lim
print(f"print bbox OK: {2*TP_HX:g} x {2*TP_HW:g} x {LEG_H:g} (X2D 256³ 内)")
print("BOM v3 cap: M6×40 平头 ×1 (先装后夹舌!), Φ8×50 单头螺柱(M6内丝) ×1, "
      "M3×18 ×4 + 垫片 + 螺母 (夹舌), M6 平头配重螺丝+螺母 按需 (±X 两端对称配平)")
