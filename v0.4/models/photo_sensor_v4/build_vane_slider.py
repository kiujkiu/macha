"""
vane_slider_v4 — 光电挡光滑片, **左右对称版** (2026-08-24)。

用户: 「vane_slider_v3_1 这个能做成对称的吗, 我理解 frame_A_v4 和 frame_B_v4 调整就行」。

## 为什么原来不对称
v3.1 把光电模块挪到 M(6.7,-45) 并重解转角后, 叉扫掠的净通道整体外移, 刀片必须
径向外移 δ=2.0 才不蹭 (布尔全周扫掠实测: δ=0 时 3 处相交, 最大 0.229 mm³ @148°)。
当时为了**不重印 frame_B**, 只挪刀片、孔留在原位 ⇒
    孔心 41.700 / 刀片中心 43.465  → 偏出 1.765, 件左右不对称。
后果不只是难看: 绕竖轴翻 180° 装反时, 刀片落到 r38.62..41.25 —— **不碰任何东西,
但半径错位挡不到光轴**, 是个不报错的静默失效 (装上去转起来就是没索引脉冲)。

## 本版做法
把 frame_B 的两个挂孔外移 2.0 (36.7/46.7 → **38.7/48.7**), 刀片中心也落到 43.7,
板随之居中 ⇒ **整件镜像对称于 X=43.7, 装不反**。

  · 板:   X 35.7..51.7 (宽 16, 中心 43.7) × Y 2..6 (厚 4) × Z 0..8
  · 孔:   X 38.7 / 48.7 (孔距 10, 中心 43.7) ← 与 frame_B 的 VANE_BOLT_RS 同步
  · 刀片: X 42.385..45.015 (宽 2.63, 中心 43.7), 印长 42, 全件总长 50
  · 四角真实半径 (hypot 修正, 板贴筋面 y2..6): 见运行输出的 assert

⚠ **只有 frame_B 有这两个挂孔, frame_A 没有** —— 所以只重印 frame_B_v4 一件,
   frame_A_v4 逐字节不变 (build_frame.py 里有 cmp 校核)。
⚠ 刀片长度与 Z 位置全部未动 (压条高度与模块 Z 没变), 仍是印长 42 装机剪短、
   刀尖距压条顶 12mm。
⚠ 半径变了就必须**重跑布尔全周扫掠** (本项目最贵的一条教训: 径向带比较法与
   (r,z) 占位法都会给出错误结论, 只有全周扫掠可信)。

局部系: X = 沿臂径向 (离轴距离), Y = 切向 (板贴筋面 y 2..6), Z0 = 板底 (= 筋底 asm 290)。
打印: 平躺 (Y=2 面贴床), 足迹 16×50, 高 4, 零支撑。
另出 vane_slider_v4_asm.stl (已剪短孪生, 刀尖 asm 280) 供装配/干涉校核。
BOM: M3×20 + 螺母 ×2 (穿 板4 + 筋4)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 对称中心 (唯一的"主参数") =====
SYM_C = 43.7                 # 孔心 / 刀片 / 板 的公共中心; frame_B 挂孔同步到 SYM_C ± HOLE_PITCH/2

HOLE_PITCH, HOLE_D = 10.0, 3.2
PLATE_W = 16.0
PLATE_Y0, PLATE_Y1 = 2.0, 6.0
PLATE_Z1 = 8.0               # = 筋高, 底平筋底 / 顶抵臂底 (定位靠面)
HOLE_Z = 4.0                 # 板正中, 对筋孔 z4 (asm 294)

BLADE_W = 42.78 - 40.15      # 2.63, 与 v3/v3.1 同宽 (只挪不改宽)
BLADE_Z0 = -42.0             # 印长: 全件总长 50, 装机剪短
TRIM_Z0 = -10.0              # 已剪短孪生: 板底 290 → 刀尖 asm 280

# ===== 派生 (全部由 SYM_C 生成, 保证对称) =====
PLATE_X0, PLATE_X1 = SYM_C - PLATE_W/2, SYM_C + PLATE_W/2       # 35.7 .. 51.7
HOLE_XS = (SYM_C - HOLE_PITCH/2, SYM_C + HOLE_PITCH/2)          # 38.7 / 48.7
BLADE_X0, BLADE_X1 = SYM_C - BLADE_W/2, SYM_C + BLADE_W/2       # 42.385 .. 45.015

# 对称性硬校核 —— 以后谁再挪一个数就会在这里炸掉
assert abs((PLATE_X0 + PLATE_X1)/2 - SYM_C) < 1e-9, "板不对称"
assert abs((HOLE_XS[0] + HOLE_XS[1])/2 - SYM_C) < 1e-9, "孔不对称"
assert abs((BLADE_X0 + BLADE_X1)/2 - SYM_C) < 1e-9, "刀片不对称"
assert PLATE_X0 + 1.5 < HOLE_XS[0] and HOLE_XS[1] < PLATE_X1 - 1.5, "孔离板端太近"


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))


part = box(PLATE_X0, PLATE_X1, PLATE_Y0, PLATE_Y1, 0.0, PLATE_Z1)
part += box(BLADE_X0, BLADE_X1, PLATE_Y0, PLATE_Y1, BLADE_Z0, 0.0)
for hx in HOLE_XS:
    part -= m3d.Manifold.cylinder(PLATE_Y1 - PLATE_Y0 + 2, HOLE_D/2, HOLE_D/2, 32, False)\
        .rotate((-90, 0, 0)).translate((hx, PLATE_Y0 - 1, HOLE_Z))
assert len(part.decompose()) == 1, "件不连通"

# 四角真实半径 (⚠ 侧挂件的径向带要用 hypot 修正, 不能直接读 X)
_rs = [(bx*bx + by*by) ** 0.5
       for bx in (BLADE_X0, BLADE_X1) for by in (PLATE_Y0, PLATE_Y1)]
R_LO, R_HI = min(_rs), max(_rs)

# 已剪短孪生 (装配/干涉校核用)
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
    print(f"wrote {out.name} ({len(tris)} tris)  vol {solid.volume()/1000:.2f} cm3 (~{solid.volume()*1.24/1000:.1f} g)")


write_stl(part, "vane_slider_v4.stl", "POV3D vane_slider_v4 (symmetric, print, blade 50 trim-to-fit)")
write_stl(part_asm, "vane_slider_v4_asm.stl", "POV3D vane_slider_v4 asm twin (trimmed, tip 280)")
print(f"  ★ 镜像对称中心 X = {SYM_C:g} (板/孔/刀片三者同心 → 装不反)")
print(f"  板 {PLATE_W:g}×{PLATE_Z1:g}×{PLATE_Y1-PLATE_Y0:g} @ X{PLATE_X0:g}..{PLATE_X1:g}")
print(f"  2×Φ{HOLE_D:g} 圆孔 X{HOLE_XS[0]:g}/{HOLE_XS[1]:g} (孔距 {HOLE_PITCH:g}) → frame_B_v4 的 VANE_BOLT_RS 必须同步")
print(f"  刀片 X{BLADE_X0:g}..{BLADE_X1:g}, 四角真实半径带 {R_LO:.2f}..{R_HI:.2f} (v3_1 是 42.20..45.18)")
print(f"  印长 {-BLADE_Z0:g} (全件总长 {PLATE_Z1-BLADE_Z0:g}); 装机剪短, 刀尖距压条顶 12mm (孪生剪至 {-TRIM_Z0:g})")
