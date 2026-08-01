"""
top_bearing frame v4 — STATIC bearing frames frame_A_v4 / frame_B_v4. PLA.

(v4, 2026-08-01, 用户圈图指定: 四柱不再坐 200 网格板自带的 4 个安装孔
 (±75,±75), 改坐**网格 M6 螺纹孔** (87.5,37.5) 族 —— 螺纹孔不用螺母,
 M6 双头螺柱一头拧板一头拧柱内丝, 板底完全不凸。
   柱位 (87.5,37.5) / (-37.5,87.5) / (-87.5,-37.5) / (37.5,-87.5)
   → POST_R = 12.5·√58 = 95.197,  POST_A0 = atan(3/7) = 23.199°  (+90k)
 与 v3 的区别**只有柱半径和柱角向**: 臂/筋再短 10.87, 件更小更硬。
 ⚠ 柱内缘 91.197 对转动件: 罩/托盘 R85 余 6.20; wifi 线缆母头扫掠 R90.51
   只余 0.69 —— **用户明确认可, 线自行处理** (往内收/改短线/走内侧)。
 ⚠ 挡光滑片仍锁 frame_B 的 ang=90 臂筋 (孔 r36.7/46.7 不变, 滑片不用重印);
   它在装配里的角向随之从 asm 45° 变为 asm 23.199° —— 光电模块随转子扫全圈,
   角向无所谓, 只有半径/Z 有约束, 那两项都没动。

v2 vs v1 (build_stl.py frame_piece): ONLY the post radius changes.
The v2 perfboard is a centre-anchored 25 mm grid; the four Φ8×350 posts
(M6 axial threads) sit in the (±100, ±100) grid holes
→ POST_R = 75·√2 = 106.066  (v2.1 was 141.421, v2 176.777, v1 194.5).
  • arm bar: R18 .. POST_R (length POST_R−18, same construction as v1)
  • top/bottom rib: R24 .. R164  (rib end ~12.78 from pad centre, keeps
    v1's ~12.7 relation: 194.5−182 = 12.5)
Everything else is IDENTICAL to v1: hub Φ44, arms 18 wide × 8 thick,
ribs 4×6, pads Φ18 (A height 8 / B column height 16), M6 Φ6.5 plain
through holes (no counterbore), 688 press pocket Φ15.8×5 + Φ13 shoulder
bore through, 4×Φ3.2 @ R14 (45°+90k°) clamping the two hubs together.
A prints as built; B prints flipped (rotate 180° about X, +16 up).

Assembly heights (tower Z, axis = (0,0)):  post tops at Z = 350.
  frame_A hub 350..358, bearing #1 pressed 353..358 (pocket opens UP)
  frame_B hub 358..366, bearing #2 pressed 361..366 (pocket opens UP)
BOM: 688 ×2, M6×16 ×2 (A pads), M6×30 ×2 (B column pads),
     M3×20+nut ×4 (hub stack).
STLs are written in PRINT orientation.
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

SEG = 96
M3_TIGHT = 3.2
M6_CLEAR = 6.5

ARM_W, ARM_T = 18.0, 8.0   # arm width = pad Φ18
RIB_W, RIB_T = 4.0, 8.0   # 2026-07-24 用户: 筋加高 6→8 (与臂同高, 给挡光滑片孔留肉)
HUB_D = 44.0
BOLT_R = 14.0
BRG_POCKET_D, BRG_POCKET_DEPTH, BRG_SHOULDER_D = 15.8, 5.0, 13.0  # 688 press-fit
PAD_D = 18.0
# v4 (2026-08-01): 柱坐网格 M6 螺纹孔 (87.5, 37.5) 族
POST_GRID = (87.5, 37.5)                                    # 一根柱的网格坐标
POST_R = math.hypot(*POST_GRID)                             # 95.197 = 12.5·√58
POST_A0 = math.degrees(math.atan2(POST_GRID[1], POST_GRID[0]))   # 23.199°
RIB_R0 = 24.0
RIB_R1 = POST_R - 12.78           # rib span (end 12.78 from pad centre, 随柱半径)

BED = 256.0                       # X2D print bed (enclosed, 256³)


def frame_piece(upper):
    """Build in LOCAL asm-like frame: A spans z 0..14 (arms 0..8, ribs 8..14);
    B spans z 0..16 (pads 0..16, arms 8..16, ribs 2..8). Local z0 = asm 350."""
    z_arm = 8.0 if upper else 0.0
    p = m3d.Manifold.cylinder(ARM_T, HUB_D/2, HUB_D/2, SEG, False).translate((0, 0, z_arm))
    for ang in (0.0, 90.0):
        bar = m3d.Manifold.cube((POST_R - 18.0, ARM_W, ARM_T), False)
        bar = bar.translate((18.0, -ARM_W/2, z_arm)).rotate((0, 0, ang))
        rib_z = (z_arm - RIB_T) if upper else (z_arm + ARM_T)
        rb = m3d.Manifold.cube((RIB_R1 - RIB_R0, RIB_W, RIB_T), False)
        rb = rb.translate((RIB_R0, -RIB_W/2, rib_z)).rotate((0, 0, ang))
        pad_h = 16.0 if upper else 8.0
        pad = m3d.Manifold.cylinder(pad_h, PAD_D/2, PAD_D/2, SEG, False)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        pad = pad.translate((POST_R*ca, POST_R*sa, 0.0))
        p = p + bar + rb + pad
        # M6: plain Φ6.5 through hole (no counterbore; B pads need M6×30)
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
# ===== 光电挡光滑片安装孔 (2026-07-24 终版, 用户: 两件都普通 M3 圆孔不开槽,
# 高度调节改为刀片印长 5cm 装机剪裁): frame_B ang=90 臂筋 (asm 45°) 上
# 2×Φ3.2 沿 X 贯穿圆孔, 居中在筋 8 高的中点 z4 (asm 294) @ y 36.7 / 46.7
# (孔距 1cm; 六改: 模块绕孔中点转 22.19° 光轴过圆心 → 刀片中心 r41.7, 净通道 r36.78..46.66);
# M3×20+螺母 ×2 把滑片 (vane_slider_v3) 夹在侧面。
VANE_BOLT_RS, VANE_BOLT_Z = (36.7, 46.7), 4.0
for br in VANE_BOLT_RS:
    h = m3d.Manifold.cylinder(RIB_W + 2, M3_TIGHT/2, M3_TIGHT/2, 24, False)
    frame_b = frame_b - h.rotate((0, 90, 0)).translate((-RIB_W/2 - 1, br, VANE_BOLT_Z))
# print frame_B flipped (ribs/pads print-up): print_z = 16 - z, print_y = -y
fb_print = frame_b.rotate((180, 0, 0)).translate((0, 0, 16.0))


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
    sx = v[:, 0].max() - v[:, 0].min()
    sy = v[:, 1].max() - v[:, 1].min()
    print(f"{name:16s} {len(tris):5d} tris  "
          f"X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  "
          f"Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}  "
          f"Z {v[:,2].min():6.2f}..{v[:,2].max():6.2f}  vol {part.volume()/1000:.1f}cm³")
    fits = sx <= BED and sy <= BED
    print(f"{'':16s} print footprint {sx:.2f} × {sy:.2f} mm  "
          f"→ {'FITS' if fits else 'DOES NOT FIT'} X2D {BED:g}×{BED:g} bed")
    assert fits, f"{name} exceeds the {BED:g} mm bed!"


print(f"POST_R = {POST_R:.3f} mm  (网格 {POST_GRID[0]:g},{POST_GRID[1]:g} = 12.5·√58; v3 was 106.066)")
print(f"POST_A0 = {POST_A0:.3f}°  → 柱角向 {POST_A0:.3f} / {POST_A0+90:.3f} / "
      f"{POST_A0+180:.3f} / {POST_A0+270:.3f}  (v3 was 45+90k)")
write_stl(frame_a, "frame_A_v4.stl")
write_stl(fb_print, "frame_B_v4.stl")
print(f"臂条长 {POST_R-18:.2f} (v3 88.07), 筋 R{RIB_R0:g}..{RIB_R1:.2f} (v3 24..93.29); "
      f"挡光滑片孔 r{VANE_BOLT_RS[0]:g}/{VANE_BOLT_RS[1]:g} 不变 → vane_slider_v3_1 不用重印")
print("asm heights: 柱顶 290 / A hub 290..298 (688 #1 293..298) / "
      "B hub 298..306 (688 #2 301..306)")
print("BOM v4: 688 ×2, M6×16 ×2 (A垫) + M6×30 ×2 (B柱垫), M3×20+螺母 ×4;"
      " 柱脚 M6 双头螺柱 ×4 (拧入板 M6 螺纹孔)")
