"""
vane_slider_v3 — v3 光电挡光滑片, 高度可调版 (2026-07-24; 同日二改, 用户图:
锁到 frame_B 加高后的臂筋上, 不再用 frame_A 臂)。

挂在 frame_B 的 ang=90 臂筋 (B 装配 rot-45 后落 asm 45°) 侧面:
筋 4 宽 × 8 高 (asm 290..298), 筋上 2×Φ3.2 圆孔居中 z4 (asm 294),
孔距 10, 对称于刀片中心 r41.7 (六改: 模块绕孔中点转 22.19°, 光轴过圆心, 净通道 r36.78..46.66);
本件也是 2×Φ3.2 普通圆孔 (终版: 两件都圆孔不开槽), M3×20+螺母 ×2
穿 板4+筋4, 全通孔无攻牙。

高度调节 (终版, 用户): 刀片印长 — 全件总长 50, 装机按实际架高用刀剪短,
剪裁目标: 刀尖距压条顶面 12mm (名义剪至 10+架高偏差)。

局部系: X = 沿臂径向 (离轴距离), Y = 切向 (板贴筋面 y 2..6), Z0 = 板底
(随架, = 筋底 asm 290)。

  · 板: X 33.7..49.7 (宽 16) × Y 2..6 (厚 4) × Z 0..8 —— 恰好填满筋侧面
    (2026-07-24 四改, 用户: 板顶到底 → 底与筋底平 asm 290, 顶抵臂底
    asm 298 成定位靠面, 装时向上顶到位+防转); 2×Φ3.2 圆孔在板正中
    (X 36.7 / 46.7 孔距 10, Z 4) 对齐筋孔; 板底对旋转叉顶 285.65 余 4.35+δ
  · 刀片: X 40.15..42.78 (厚 2.63), 印长 42 (Z −42..0, 全件总长 50);
    切向偏置 2..6 按真实半径修正 → 四角半径恰 40.20..43.20 (扫掠净通道
    36.78..46.66 内, 双侧余量 ~3.4); 剪短后刀尖 asm 280 (光轴 282.4)
打印: 平躺 (Y=2 面贴床), 足迹 16×50, 高 4, 零支撑。
STL 为打印姿态: (x, y, z)_件 → (x, z, y−2)_打印。
另出 vane_slider_v3_1_asm.stl (已剪短孪生, 刀尖 280) 供装配/干涉校核。
BOM: M3×20+螺母 ×2 (穿 板4+筋4)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

PLATE_X0, PLATE_X1 = 33.7, 49.7
PLATE_Y0, PLATE_Y1 = 2.0, 6.0
PLATE_Z1 = 8.0                       # = 筋高, 底平筋底 / 顶抵臂底 (定位靠面)
HOLE_XS, HOLE_D = (36.7, 46.7), 3.2   # 孔距 10, 对称于刀片中心 41.7
HOLE_Z = 4.0                         # 板正中, 对筋孔 z4 (asm 294) → 板底 asm 290
# ===== v3.1 (2026-07-31): 刀片径向外移 =====
# 光电模块随 v3.1 挪到 M(6.7,-45) 并重解转角后, 叉扫掠的净通道整体外移。
# **布尔全周扫掠实测** (1° 步进 ×360): δ=0 时 3 个角度相交, 最大 0.229 mm³ @148°;
# δ≥0.5 即不碰。取 **δ=2.0** 使两侧余量均衡 → 刀片半径 40.20..43.20 → 42.20..45.18。
# ⚠ 只改本件, frame_B_v3 的臂筋孔 (r36.7/46.7) **原位不动, 不用重印**。
# ⚠ 刀片长度不变 (压条高度与模块 Z 未变, 仍是印长 42 装机剪短、刀尖距压条顶 12)。
# ⚠ 教训: 径向带比较法与 (r,z) 占位法都给出了错误结论 (分别 -0.15 干涉 / 完全不碰),
#   只有**布尔全周扫掠**可信 —— 偏心弦布局必须扫掠验证。
BLADE_DR = 2.0                       # 径向外移量
BLADE_X0, BLADE_X1 = 40.15 + BLADE_DR, 42.78 + BLADE_DR   # 切向偏置修正后半径 42.20..45.18
BLADE_Z0 = -42.0                     # 印长: 全件总长 50, 装机剪短
TRIM_Z0 = -10.0                      # 已剪短孪生: 板底 290 → 刀尖 asm 280

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

part = box(PLATE_X0, PLATE_X1, PLATE_Y0, PLATE_Y1, 0.0, PLATE_Z1)
part += box(BLADE_X0, BLADE_X1, PLATE_Y0, PLATE_Y1, BLADE_Z0, 0.0)
for hx in HOLE_XS:
    part -= m3d.Manifold.cylinder(PLATE_Y1 - PLATE_Y0 + 2, HOLE_D/2, HOLE_D/2, 32, False)\
        .rotate((-90, 0, 0)).translate((hx, PLATE_Y0 - 1, HOLE_Z))

assert len(part.decompose()) == 1
# 四角真实半径校核 (随 BLADE_DR 参数化; v3 原版是 40.20..43.20)
_R_LO, _R_HI = 40.20 + BLADE_DR, 43.20 + BLADE_DR
_rs = [ (bx*bx + by*by) ** 0.5
        for (bx, by) in ((BLADE_X0, PLATE_Y0), (BLADE_X0, PLATE_Y1),
                         (BLADE_X1, PLATE_Y0), (BLADE_X1, PLATE_Y1)) ]
assert _R_LO - 0.02 <= min(_rs) and max(_rs) <= _R_HI + 0.02, (min(_rs), max(_rs), _R_LO, _R_HI)

# 已剪短孪生 (装配/干涉校核用): 刀片截到 TRIM_Z0 (刀尖 asm 280)
part_asm = part ^ box(PLATE_X0 - 1, PLATE_X1 + 1, PLATE_Y0 - 1, PLATE_Y1 + 1,
                      TRIM_Z0, PLATE_Z1 + 1)

def write_stl(solid, name, header):
    # 打印姿态: (x, y, z) → (x, z, y−PLATE_Y0), 平躺零支撑
    mesh = solid.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3].copy()
    verts = verts[:, [0, 2, 1]]
    verts[:, 2] -= PLATE_Y0
    tris = np.asarray(mesh.tri_verts)[:, ::-1]    # 轴交换 = 镜像 → 翻回绕向
    out = Path(__file__).with_name(name)
    with out.open("wb") as f:
        f.write(header.encode().ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
            if L > 0: n = n/L
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    assert 84 + len(tris)*50 == out.stat().st_size
    print(f"wrote {out} ({len(tris)} tris)  vol {solid.volume()/1000:.2f} cm3 (~{solid.volume()*1.27/1000:.1f} g)")

write_stl(part, "vane_slider_v3_1.stl", "POV3D vane_slider_v3 v3 (print, blade 50 trim-to-fit)")
write_stl(part_asm, "vane_slider_v3_1_asm.stl", "POV3D vane_slider_v3 asm twin (trimmed, tip 280)")
print(f"  板 {PLATE_X1-PLATE_X0:g}×{PLATE_Z1:g}×4 @ X{PLATE_X0:g}..{PLATE_X1:g}; 2×Φ{HOLE_D:g} 圆孔在板正中 (X{HOLE_XS[0]:g}/{HOLE_XS[1]:g}, Z{HOLE_Z:g}) 对筋孔 asm294")
print(f"  刀片半径带 {min(_rs):.2f}..{max(_rs):.2f} (外移 δ={BLADE_DR:g}); X{BLADE_X0:g}..{BLADE_X1:g} 印长 {-BLADE_Z0:g} (全件总长 {PLATE_Z1-BLADE_Z0:g}); 装机剪短, 目标: 刀尖距压条顶 12mm (孪生剪至 {-TRIM_Z0:g})")
print(f"  锁 frame_B 筋圆孔 (asm 45° 臂, 孔居中 z4) M3×20+螺母 ×2; 平躺打印零支撑")
