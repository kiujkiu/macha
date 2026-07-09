"""
sensor_bracket_v2 — v2 装配 (assembly_v2, mlkpai_carrier_disc Φ170) 的光电支架。
v1 (build_bracket.py, θ=180, 装 rim_top_disc Φ200) 保留不动。

v2 变化:
  • 位置 θ=180 (-X, 用户 2026-07-03 晚定: 与 PCB 同侧, 走线短; 曾短暂放 θ=0)。
  • 安装孔改借盘 R77.5 环孔 @ 157.5°/202.5° = (-71.60, ±29.66) — 与门形底座同招,
    盘不加孔; M3 从上往下穿 板(5)+盘(5)+rim_ring, 下面螺母 (~M3×20)。
  • 盘面 45.7 (asm — hub+rim_ring 嵌套 + 盘厚 6→5, 2026-07-06):
    板 Z 45.7..50.7, 梁 Z 37.7。

板: 5 厚, X -113..-64 × Y ±35, 外端两角 45° 斜切 (压最大半径)。
(2026-07-07 用户要求缩半径: R_SLOT 112→98 — v1 的 112 是让开旧 Φ200 盘;
 v2 盘 R85, 真约束 = 模块内缘 R_SLOT-10 ≥ 定子法兰 R85+3 → R_SLOT≥98。
 模块 R88..111, 板外缘 R113, 旋转最大半径 127→~114。)
模块 (sensor_module, 外购) 翻转扣在外端板底 (槽口朝下, 焊脚朝上),
2× 模块孔 (-91,17)/(-105,17): M3 通 + Φ4.2×4 顶沉 (非平面孔 → 图纸配详图);
3 个 2mm 底面避空槽给朝上焊脚。R_SLOT=112, 梁 (-112, 0, 37.7) 径向过轴心。
与挪位后 PCB 无干涉: 板内缘 -64 vs 板边 -57 (隙7) / 最近凸台边 -59 (隙5)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

R_SLOT = 98.0    # 112→98 (2026-07-07 缩半径)
PL_Z0, PL_Z1 = 45.7, 50.7                       # 盘顶 45.7 (asm) 上的 5mm 板
PL_X0, PL_X1, PL_Y0, PL_Y1 = -113.0, -64.0, -35.0, 35.0
CHAM = [(-113.0, 20.0), (-98.0, 35.0)]   # 外角 45° 斜切起止
RIM = [(-71.601, 29.658), (-71.601, -29.658)]   # 借用盘 R77.5 环孔 @157.5°/202.5°
BLUE = [(-R_SLOT + 7.0, 17.0), (-R_SLOT - 7.0, 17.0)]   # (-91,17)/(-105,17) 模块孔
M3_CLEAR = 3.4
CB_D, CB_DEPTH = 4.2, 4.0                        # BLUE 顶沉孔

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def zcyl(z0, z1, r, x, y, seg=32):
    return m3d.Manifold.cylinder(z1-z0, r, r, seg, False).translate((x, y, z0))

plate = box(PL_X0, PL_X1, PL_Y0, PL_Y1, PL_Z0, PL_Z1)
# 外端两角 45° 斜切
for sy in (1.0, -1.0):
    tri = m3d.CrossSection([[(CHAM[0][0]-1, sy*CHAM[0][1]), (CHAM[0][0]-1, sy*(PL_Y1+1)),
                             (CHAM[1][0], sy*(PL_Y1+1))][::(-1 if sy>0 else 1)]])
    cut = tri.extrude(PL_Z1-PL_Z0+2).translate((0,0,PL_Z0-1))
    plate = plate - cut

# 安装孔 — 平面通孔, M3 从上往下 (穿 板+盘+rim_ring)
for (x, y) in RIM:
    plate = plate - zcyl(PL_Z0 - 1, PL_Z1 + 1, M3_CLEAR/2, x, y)

# 模块孔 — M3 通 + Φ4.2×4 顶沉 (模块扣在板底)
for (x, y) in BLUE:
    plate = plate - zcyl(PL_Z0 - 1, PL_Z1 + 1, 3.2/2, x, y)
    plate = plate - zcyl(PL_Z1 - CB_DEPTH, PL_Z1 + 1, CB_D/2, x, y)

# 3 个 2mm 底面避空槽 (模块朝上焊脚; = v1 槽位绕 Z 转 180°)
POCKETS = [(-R_SLOT-10, -R_SLOT-4, -4.5, 4.5),   # 2 opto 脚 near (-108,0)
           (-R_SLOT+4, -R_SLOT+10, -4.5, 4.5),   # 2 opto 脚 near (-94,0)
           (-R_SLOT-4.5, -R_SLOT+4.5, 15.0, 21.5)]  # 3 排针尾 near (-98,18)
for (x0, x1, y0, y1) in POCKETS:
    plate = plate - box(x0, x1, y0, y1, PL_Z0, PL_Z0 + 2.0)

# ---- export ----
mesh = plate.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("sensor_bracket_v2.stl")
with out.open("wb") as f:
    f.write(b"POV3D sensor_bracket_v2".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n)); f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
v = verts
print(f"sensor_bracket_v2.stl  {len(tris)} tris  X {v[:,0].min():.1f}..{v[:,0].max():.1f}  "
      f"Y {v[:,1].min():.1f}..{v[:,1].max():.1f}  Z {v[:,2].min():.1f}..{v[:,2].max():.1f}  "
      f"vol {plate.volume()/1000:.2f}cm³")
print(f"θ=180 盘顶板 (Z{PL_Z0}-{PL_Z1}), 悬出 R85 到 R{-PL_X0:g}; 借环孔 {RIM}; "
      f"模块孔 {BLUE} + Φ{CB_D:g}×{CB_DEPTH:g} 顶沉; 梁 (-{R_SLOT:g}, 0, {PL_Z0-8:g})")
