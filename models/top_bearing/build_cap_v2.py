"""
top_cap_v2 — v2 rotor cap for the top steady-bearing module (single-screen rotor).
PLA. L-SHAPE: leg at the +X end (the screen assembly — screen + screen_plate +
gate tower — is rotated 180 deg about Z, so screen_plate's back face now points
+X at asm X=+13.27). Derived from build_stl.py's top_cap v3.4 (same axis
hardware: M6x40 flat head + Phi8x50 M6-female standoff through 2x688).

Assembly frame (Z = perfboard top, axis = (0,0)); CAPTOP = 292.7.

  1. slab 9 thick: Z 283.7..292.7, X -65..+17.27, Y +-72. Top face FULLY FLAT
     (asm top = print bottom / bed). The +X end is flush with the leg's outer
     face -> the side section is an L.
  2. back leg 4 thick: X +13.27..+17.27 (front face lands on screen_plate's
     back face X=+13.27), Y +-56, Z 247..292.7 — fused with the slab; in print
     orientation the leg rises from print z 9 to 45.7 and stays inside the
     slab footprint (no overhang).
  3. axis: Phi6.2 through the slab at (0,0) + Phi13x2.7 head recess cut from
     the slab BOTTOM face (= print top). M6x40 flat head sits at 283.7..286.4.
  4. cap fixing: 2 x Phi3.4 along X through the leg at asm (Y=+-49.975,
     Z=253.2) — the screens' own top-row nut holes (unchanged by the 180 deg
     turn); swap the screen's M3 for M3x16 (from the back through leg 4 +
     plate 6 into the screen nut).
  5. counterweight bank (unchanged, -X overhang — axis and counterweights sit
     on the SAME side of the leg, which is what allows the L):
     19 x Phi6.5 vertical through holes, 品字形, 14 mm equilateral-triangle
     pitch; row A X=-46, 10 holes Y=(k-4.5)*14 (k 0..9); row B X=-58.12,
     9 holes Y=(k-4)*14 (k 0..8). Each with a Phi13x2.7 counterbore from the
     slab TOP face (asm Z292.7 = print z0) so M6 wafer heads (Phi12.5x2.6)
     recess flush.

PRINT pose (slab top on the bed, leg up), same flip mapping as v1:
    print_z = CAPTOP - asm_z,  print_x = asm_x,  print_y = -asm_y
The model below is built directly in PRINT coordinates with that mapping
applied inline (comments give the asm values). Export: top_cap_v2.stl.
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
TP_X0, TP_X1, TP_HW = -65.0, 17.27, 72.0    # X -65..+17.27, Y +-72 (82.27 x 144)

# --- back leg (asm X +13.27..+17.27, Y +-56, Z 247..292.7) ---
LEG_X0, LEG_X1 = 13.27, 17.27        # 4 thick; front face on screen_plate back,
                                     # outer face flush with the slab +X edge (L)
LEG_HW = 56.0                        # Y +-56 (112 wide)
LEG_ZBOT_ASM = 247.0
LEG_H = CAPTOP - LEG_ZBOT_ASM        # 45.7 (print z 0..45.7)

# --- axis bore + head recess ---
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7

# --- cap fixing holes (through the leg, along X) ---
SCREW_Y_ASM = 49.975                 # asm Y = +-49.975 (screen top-row nuts)
SCREW_Z_ASM = 253.2                  # -> print z = 292.7 - 253.2 = 39.5

# --- M6 counterweight bank (-X overhang; mirror of v1 v3.4) ---
CW_M6 = 6.5
CW_TRI = 14.0
CW_ROW_DX = CW_TRI * math.sin(math.radians(60))     # 12.12 row-to-row
CW_ROW_A_X = -46.0
CW_ROW_B_X = CW_ROW_A_X - CW_ROW_DX                 # -58.12
CW_HOLES = [(CW_ROW_A_X, (k - 4.5) * CW_TRI) for k in range(10)] \
         + [(CW_ROW_B_X, (k - 4.0) * CW_TRI) for k in range(9)]  # 10 + 9 = 19

# ===================== build (PRINT coordinates) =====================
# slab: print z 0..9 (asm 292.7..283.7), flat face on the bed
cap = m3d.Manifold.cube((TP_X1 - TP_X0, 2 * TP_HW, SLAB_T), False) \
        .translate((TP_X0, -TP_HW, 0.0))
# leg: print z 0..45.7 (fused with the slab; inside the slab footprint)
cap = cap + m3d.Manifold.cube((LEG_X1 - LEG_X0, 2 * LEG_HW, LEG_H), False) \
        .translate((LEG_X0, -LEG_HW, 0.0))
# axis: Phi6.2 through the slab + Phi13x2.7 head recess from the slab bottom
# face (asm 283.7 = print TOP z9)
cap = cap - m3d.Manifold.cylinder(SLAB_T + 2, M6_BORE/2, M6_BORE/2, 48, False) \
        .translate((0, 0, -1.0))
cap = cap - m3d.Manifold.cylinder(HEAD_DEPTH + 1, HEAD_D/2, HEAD_D/2, 48, False) \
        .translate((0, 0, SLAB_T - HEAD_DEPTH))
# 2 x Phi3.4 along X through the leg: asm (Y=+-49.975, Z=253.2)
# -> print (y = -+49.975, z = 39.5); symmetric in Y so the flip is a no-op
for ay in (SCREW_Y_ASM, -SCREW_Y_ASM):
    s = m3d.Manifold.cylinder((LEG_X1 - LEG_X0) + 2, M3_CLEAR/2, M3_CLEAR/2, 24, False)
    s = s.rotate((0, 90, 0))
    cap = cap - s.translate((LEG_X0 - 1.0, -ay, CAPTOP - SCREW_Z_ASM))
# 19 x Phi6.5 counterweight holes (vertical, through the slab) in the -X
# overhang, each with a Phi13x2.7 counterbore from the slab TOP face
# (asm 292.7 = print z0, bed side) — M6 wafer head Phi12.5x2.6 sits flush.
for (cx, cy) in CW_HOLES:                     # rows are Y-symmetric: -asm_y = same set
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

v = write_stl(cap, "top_cap_v2.stl")
# print-pose bbox self-check (X2D 256^3)
assert abs(v[:, 0].min() - TP_X0) < 1e-3 and abs(v[:, 0].max() - TP_X1) < 1e-3
assert abs(v[:, 1].min() + TP_HW) < 1e-3 and abs(v[:, 1].max() - TP_HW) < 1e-3
assert abs(v[:, 2].min()) < 1e-3 and abs(v[:, 2].max() - LEG_H) < 1e-3
for span, lim in ((TP_X1 - TP_X0, 256), (2 * TP_HW, 256), (LEG_H, 256)):
    assert span < lim
print(f"print bbox OK: {TP_X1-TP_X0:g} x {2*TP_HW:g} x {LEG_H:g} (X2D 256³ 内)")
print("BOM v2 cap: M6×40 平头 ×1, Φ8×50 单头螺柱(M6内丝) ×1, M3×16 ×2 (替换屏上排原M3), "
      "M6 平头配重螺丝+螺母 按需")
