"""
Top steady-bearing module v2 — 3 printed parts + 688 bearing + Φ8 rod.
PLA. Fixes vs v1: (1) the 45° wedge that collided with the screens is GONE
(cap now prints flat upside-down); (2) the frame mounts on the POST TOPS
with M6 screws (posts have axial M6 threads) — no vertical play;
(3) reinforcement ribs on the frame arms and the cap corner.

Assembly frame (tower, Z up, axis = (0,0); post tops at Z = 400):

• top_cap ×1 (ROTATING, carries the 688 bearing):
    back plate 4 thick (X −18.3..−14.3, Y −105..106, Z 315..337.7), 4 × Φ3.4
    to the screens' top 井 holes; top plate 4 thick (Z 333.7..337.7,
    X −18.3..12, Y ±30) above the screens; center boss Φ26 (Z 337.7..342.7)
    with bearing pocket Φ16.1 × 5 opening UP + 45° cone to Φ13 through;
    corner rib (X −18.3..−10, Y ±30, Z 337.7..341.7). Bearing at
    337.7..342.7; the static Φ8 rod enters its bore from above.
    PRINT: flipped flat (boss+pocket on the bed side) — support-free.

• frame_A ×1 (STATIC, lower): hub Φ44 (Z 400..408, Φ7.8 center rod hole,
    4 × Φ3.2 @ R14) + 2 arms 90° apart (14 × 8) with 4 × 6 top ribs
    (R24..R182) + Φ18 post pads (Z 400..408) at R194.5 with M6: Φ6.5
    through + Φ11 × 4 CB. Arms → SW + NW posts (placed rotated 135°).
    PRINT: flat as built.

• frame_B ×1 (STATIC, upper): same but hub/arms at Z 408..416, ribs BELOW
    the arms (402..408), post pads are Φ18 × 16 columns (Z 400..416,
    CB Φ11 × 12). Arms → NE + SE posts (placed rotated −45°). Stacked on
    frame_A's hub; 4 × M3×20+nut clamp the hubs AND the rod hole grips the
    Φ8 rod over 16 mm (Φ7.8 light press + glue).
    PRINT: flipped (ribs up) — support-free.

• Φ8 steel rod × 78 (cut from post stock): clamped in the frame hubs
    (top flush at 416), hangs to Z 338 — 4.5 mm inside the bearing bore.

BOM: 688 ×1, Φ8×78 rod ×1, M6×16 ×4 (pads→post tops), M3×8 ×4 (cap→screens),
M3×20+nut ×4 (hub stack), glue (rod + bearing).
STLs in PRINT orientation.
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

SEG = 96
M3_CLEAR, M3_TIGHT = 3.4, 3.2
M6_CLEAR, M6_CB_D = 6.5, 11.0

# ===================== top_cap v3.2 (print flipped; CAPTOP = asm 342.7,
# print_z = 342.7 - asm_z, print_x = asm_x, print_y = -asm_y) =====================
# v3.2: the top face is now FULLY FLAT. The v3.1 protruding Φ26×5 column +
# +X edge flange + spoke rib + corner rib are GONE — the whole top plate is a
# single solid 9-thick slab (asm 333.7..342.7, prints flat on the bed face-up).
# The steel M6×40 + standoff carry the span; the plastic only seats the head.
# M6 Φ6.2 bore through the slab + Φ13×2.7 head recess at the slab bottom
# (= print top). Back plate (4 thick) drops to the screens' top 井 holes.
CAP_T = 4.0
SLAB_T = 9.0
TP_X0, TP_X1, TP_HW = -18.3, 65.0, 72.0    # v3.4: slab WIDER (Y±72) + LONGER (+X to 65) for a big M6 counterweight bank
BP_H = 22.7
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7
SCREW_YZ_ASM = [(-94.0, 324.7), (-34.0, 324.7), (35.0, 325.7), (95.0, 325.7)]
CAPTOP = 342.7
# M6 counterweight bank in the +X overhang (away from the screen): 2 staggered
# rows, 品字形, 14 mm equilateral-triangle pitch, 10 + 9 = 19 holes. Rows moved
# OUT to X=46/58 (≈2cm farther from the axis → more counterweight leverage).
# Φ6.5 through (vertical) — add M6 wafer screws (Φ12.5 head ×2.6, M6×30) + nuts
# to trim the rotor balance.
CW_M6 = 6.5
CW_TRI = 14.0
CW_ROW_DX = CW_TRI * math.sin(math.radians(60))   # 12.12 (row-to-row, radial)
CW_ROW_A_X = 46.0
CW_ROW_B_X = CW_ROW_A_X + CW_ROW_DX               # 58.12
CW_HOLES = [(CW_ROW_A_X, (k - 4.5) * CW_TRI) for k in range(10)] \
         + [(CW_ROW_B_X, (k - 4.0) * CW_TRI) for k in range(9)]   # 10 + 9 = 19

# top slab: one solid block, flat top face (print 0..9 = asm 342.7..333.7)
cap = m3d.Manifold.cube((TP_X1 - TP_X0, 2*TP_HW, SLAB_T), False).translate((TP_X0, -TP_HW, 0.0))
# back plate: filled DOWN to the bed (print Z0) so the ends beyond the slab
# (|Y|>72) don't print floating — print Z0..27.7 (= asm 315..342.7)
cap = cap + m3d.Manifold.cube((CAP_T, 211.0, BP_H + (SLAB_T - CAP_T)), False).translate((-18.3, -106.0, 0.0))
# M6 bore (through the slab) + Φ13 head recess from the print TOP (= slab underside)
cap = cap - m3d.Manifold.cylinder(SLAB_T + 2, M6_BORE/2, M6_BORE/2, 48, False).translate((0, 0, -1.0))
cap = cap - m3d.Manifold.cylinder(HEAD_DEPTH + 1, HEAD_D/2, HEAD_D/2, 48, False).translate((0, 0, SLAB_T - HEAD_DEPTH))
# 4 × M3 clearance holes (along X) into the back plate -> screens' 井 top row
for (ay, az) in SCREW_YZ_ASM:
    s = m3d.Manifold.cylinder(CAP_T + 2, M3_CLEAR/2, M3_CLEAR/2, 24, False)
    s = s.rotate((0, 90, 0))
    cap = cap - s.translate((-18.3 - 1.0, -ay, CAPTOP - az))
# M6 counterweight holes (vertical, Φ6.5 through the slab) in the +X overhang,
# each with a Φ13 × 2.7 head counterbore from the TOP face (asm 342.7 = print
# Z0) so the M6 wafer head (Φ12.5×2.6) recesses flush.
for (cx, cy) in CW_HOLES:
    cap = cap - m3d.Manifold.cylinder(SLAB_T + 2, CW_M6/2, CW_M6/2, 32, False).translate((cx, cy, -1.0))
    cap = cap - m3d.Manifold.cylinder(HEAD_DEPTH + 1, HEAD_D/2, HEAD_D/2, 48, False).translate((cx, cy, -1.0))

# ===================== frame pieces =====================
ARM_W, ARM_T = 18.0, 8.0   # arm width = pad Φ18 (v3)
RIB_W, RIB_T = 4.0, 6.0
HUB_D = 44.0
BOLT_R = 14.0
BRG_POCKET_D, BRG_POCKET_DEPTH, BRG_SHOULDER_D = 15.8, 5.0, 13.0  # 688 press-fit (v3)
PAD_D = 18.0
POST_R = 194.5

def frame_piece(upper):
    """Build in LOCAL asm-like frame: A spans z 0..14 (arms 0..8, ribs 8..14);
    B spans z 0..16 (pads 0..16, arms 8..16, ribs 2..8). Local z0 = asm 400."""
    z_arm = 8.0 if upper else 0.0
    p = m3d.Manifold.cylinder(ARM_T, HUB_D/2, HUB_D/2, SEG, False).translate((0, 0, z_arm))
    for ang in (0.0, 90.0):
        bar = m3d.Manifold.cube((POST_R - 18.0, ARM_W, ARM_T), False)
        bar = bar.translate((18.0, -ARM_W/2, z_arm)).rotate((0, 0, ang))
        rib_z = (z_arm - RIB_T) if upper else (z_arm + ARM_T)
        rb = m3d.Manifold.cube((182.0 - 24.0, RIB_W, RIB_T), False)
        rb = rb.translate((24.0, -RIB_W/2, rib_z)).rotate((0, 0, ang))
        pad_h = 16.0 if upper else 8.0
        pad = m3d.Manifold.cylinder(pad_h, PAD_D/2, PAD_D/2, SEG, False)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        pad = pad.translate((POST_R*ca, POST_R*sa, 0.0))
        p = p + bar + rb + pad
        # M6: plain Φ6.5 through hole (v3 — no counterbore; B pads need M6×30)
        thr = m3d.Manifold.cylinder(20.0, M6_CLEAR/2, M6_CLEAR/2, 32, False)
        p = p - thr.translate((POST_R*ca, POST_R*sa, -1.0))
    # 688 bearing pocket Φ15.8 × 5 from the piece's LOCAL TOP (A prints
    # upright -> pocket asm-up; B prints flipped -> pocket asm-down), with
    # Φ13 shoulder bore through the remaining 3.
    z_top = (8.0 + ARM_T) if upper else ARM_T   # local hub top: A 8, B 16
    pk = m3d.Manifold.cylinder(BRG_POCKET_DEPTH + 1, BRG_POCKET_D/2, BRG_POCKET_D/2, 96, False)
    p = p - pk.translate((0, 0, z_top - BRG_POCKET_DEPTH))
    p = p - m3d.Manifold.cylinder(30.0, BRG_SHOULDER_D/2, BRG_SHOULDER_D/2, 96, False).translate((0, 0, -1.0))
    for k in range(4):
        a = math.radians(45 + 90*k)
        s = m3d.Manifold.cylinder(30.0, M3_TIGHT/2, M3_TIGHT/2, 24, False)
        p = p - s.translate((BOLT_R*math.cos(a), BOLT_R*math.sin(a), -1.0))
    return p

frame_a = frame_piece(upper=False)                 # print as built
frame_b = frame_piece(upper=True)
# print frame_b flipped (ribs/pads print-up): print_z = 16 - z, print_y = -y
fb_mesh_src = frame_b.rotate((180, 0, 0)).translate((0, 0, 16.0))

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
    print(f"{name:14s} {len(tris):5d} tris  "
          f"X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  "
          f"Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}  "
          f"Z {v[:,2].min():6.2f}..{v[:,2].max():6.2f}  vol {part.volume()/1000:.1f}cm³")

write_stl(cap, "top_cap.stl")
write_stl(frame_a, "frame_A.stl")
write_stl(fb_mesh_src, "frame_B.stl")
print("BOM v3.1: 688 ×2, M6×40 平头内六角 ×1, Φ8×50 单头螺柱(M6内丝) ×1, M6 螺母 ×1 (柱顶锁紧), "
      "M6×16 ×2 (A 垫) + M6×30 ×2 (B 柱垫), M3×8 ×4, M3×20+nut ×4")
