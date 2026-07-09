"""
wifi_box — USB WiFi 网卡倒扣盒 (打印件, PETG, 按安装姿态打印零支撑)。

盘坐标系, Z0 = 盘顶面。五面盒壁厚 3, 开口朝下扣住侧立的模块整块 (14.5×40×70),
4 耳脚 (Z0..3) 接盘环孔 M3×14。+Y 端壁: 母头出口窗 10.7×19.1 (穿墙, 居中 Z20)
+ 上下扎带槽 (扎带勒母头壳, 抗离心 +Y 分量拔脱)。西内壁 3 条 0.25 摩擦筋。
装配: 盒倒置 → 模块放入 → 母头从窗外插入插合 → 翻正扣盘 → 4× M3×14。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

from wifi_common import (XC, IX0, IX1, IY0, IY1, IZ1, OX0, OX1, OY0, OY1, OZ1,
                         WIN_W, WIN_H, ZC_PORT, TIE_W, TIE_H, TIE_ZLO, TIE_ZHI,
                         RIB_YS, RIB_W, RIB_P, DISC_M3, M3_THRU, FLANGE_T,
                         WFL_X0, EFL_X1, EFL_HY, GUS_T, WGUS_YS, EGUS_YS, DISC_R)

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

def gusset(x_out, x_wall, yc):
    """三角加强筋: 站在翼板顶 Z3, 45° 靠墙升到 Z 3+臂长 (打印免支撑)。"""
    arm = abs(x_wall - x_out)
    pts = [(x_out, FLANGE_T), (x_wall, FLANGE_T), (x_wall, FLANGE_T + arm)]
    area2 = sum(pts[i][0]*(pts[(i+1) % 3][1]-pts[(i-1) % 3][1]) for i in range(3))
    if area2 < 0:
        pts.reverse()                          # 保证 CCW (CW → CrossSection 为空)
    prof = m3d.CrossSection([pts])
    return prof.extrude(GUS_T).rotate((90, 0, 0)).translate((0, yc + GUS_T/2, 0))

# ===== 实体 =====
part = box(OX0, OX1, OY0, OY1, 0, OZ1) - box(IX0, IX1, IY0, IY1, -1, IZ1)  # 倒扣壳
for yc in RIB_YS:                                                # 西内壁摩擦筋
    part += box(IX0, IX0+RIB_P, yc-RIB_W/2, yc+RIB_W/2, 1.0, IZ1-1.0)
part += box(WFL_X0, OX0, OY0, OY1, 0, FLANGE_T)                  # 西翼板 (整条, 全长)
part += box(OX1, EFL_X1, -EFL_HY, EFL_HY, 0, FLANGE_T)           # 东翼板 (整条, ±37)
for yc in WGUS_YS:                                               # 西加强筋 ×5
    part += gusset(WFL_X0, OX0, yc)
for yc in EGUS_YS:                                               # 东加强筋 ×5
    part += gusset(EFL_X1, OX1, yc)

# ===== 挖除 =====
part -= box(XC-WIN_W/2, XC+WIN_W/2, IY1-1, OY1+1,                # 母头出口窗
            ZC_PORT-WIN_H/2, ZC_PORT+WIN_H/2)
for z0 in (TIE_ZLO, TIE_ZHI):                                    # 扎带槽 ×2
    part -= box(XC-TIE_W/2, XC+TIE_W/2, IY1-1, OY1+1, z0, z0+TIE_H)
for (hx, hy) in DISC_M3:                                         # 4× M3 耳孔
    part -= cyl(M3_THRU, hx, hy, -1, FLANGE_T+1)

# ===== export =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("wifi_box.stl")
with out.open("wb") as f:
    f.write(b"POV3D wifi_box (inverted box)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
r_max = float(np.hypot(verts[:, 0], verts[:, 1]).max())
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3 (~{part.volume()*1.27/1000:.0f} g PETG)")
print(f"  外廓 X {OX0:g}..{OX1:g}  Y {OY0:g}..{OY1:g}  Z 0..{OZ1:g} (壁 3); 内腔 {IX1-IX0:g}×{IY1-IY0:g}×{IZ1:g}")
print(f"  max R {r_max:.1f} (含耳脚, 全在盘 R{DISC_R:g} 内)")
print(f"  出口窗 {WIN_W:g}×{WIN_H:g} @ (X{XC:g}, Z{ZC_PORT:g}); 扎带槽 Z {TIE_ZLO:g}/{TIE_ZHI:g}")
print(f"  4× M3×14 @ {DISC_M3} (翼板3+盘5+环3.5, 环底垫片+螺母); 加强筋 西{WGUS_YS} 东{EGUS_YS}")
print(f"  打印: 按安装姿态 (开口朝下=顶在上), 零支撑; 顶板 15.1 桥接")
