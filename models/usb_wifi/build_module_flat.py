"""
usb_wifi_module_flat — AX1800 网卡数字孪生, 第四版 (2026-07-22): 放平方案。

用户定稿 (wifi_shell 配套): 天线反折收进本体, 整块 = 14.5×40×70, 以 40×70
大面贴承载盘躺平, 14.5 高, 插头朝 +Y (局部系; 随 135° 组转后同 pi2hub 走线向)。
孪生建在盘系局部最终位 (Z0 = 承载面, 盒 footprint 中线 XC=46), assembly 只做
+DISC_TOP 平移 + rot(ROTOR_ROT + WIFI_ROT_EXTRA=135°)。

放平后口轴线高 = 14.5/2 = 7.25; 插头截面 12 宽(X) × 4.5 高, 母头壳
18.7 宽 × 10.3 高 —— 与 wifi_shell 出口窗 (10.7 竖 × 19.1 横, 中心离盘 7.25)
四周 ±0.2 余量 (窗随 2026-07-22 的 WIN_XC/WIN_ZC 修正对准本口)。
旧侧立孪生 build_module.py / usb_wifi_module.stl 已废弃 (留档不删)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

from wifi_common import (PLUG_L, PLUG_W, PLUG_T, FEM_L, FEM_W, FEM_T, CABLE_D)

BLK_W, BLK_L, BLK_H = 40.0, 70.0, 14.5   # 宽(X) × 长(Y) × 高(Z), 放平
XC = 43.0    # 同 wifi_shell / 装配 XC_WIFI (2026-07-22 定稿: 46→43, 靠向 pi2hub 3)
YC = -13.0   # 沿长边平移 −13 (2026-07-22: −15 时沿孔沉孔侵内凸台环, 改 −13)
ZC_PORT = BLK_H / 2                       # 7.25

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

# 整块 (放平)
part = box(XC-BLK_W/2, XC+BLK_W/2, YC-BLK_L/2, YC+BLK_L/2, 0.0, BLK_H)
# USB 头 (放平: 12 宽 × 4.5 高, 居中)
part += box(XC-PLUG_W/2, XC+PLUG_W/2, YC+BLK_L/2, YC+BLK_L/2+PLUG_L,
            ZC_PORT-PLUG_T/2, ZC_PORT+PLUG_T/2)
# 母头壳 (放平: 18.7 宽 × 10.3 高; 插合态, 前面贴块尾, 吞下插头)
part += box(XC-FEM_W/2, XC+FEM_W/2, YC+BLK_L/2, YC+BLK_L/2+FEM_L,
            ZC_PORT-FEM_T/2, ZC_PORT+FEM_T/2)
# 线缆头 20mm
part += m3d.Manifold.cylinder(20.0, CABLE_D/2, CABLE_D/2, 32, False)\
    .rotate((-90, 0, 0)).translate((XC, YC+BLK_L/2+FEM_L, ZC_PORT))

# ===== export =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("usb_wifi_module_flat.stl")
with out.open("wb") as f:
    f.write(b"POV3D usb_wifi_module_flat v4 (bought, twin)".ljust(80, b" ")[:80])
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
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3")
print(f"  bbox X {verts[:,0].min():.1f}..{verts[:,0].max():.1f}  Y {verts[:,1].min():.1f}..{verts[:,1].max():.1f}"
      f"  Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}   max R {r_max:.1f}")
print(f"  放平整块 {BLK_W:g}×{BLK_L:g}×{BLK_H:g} 高 @ X{XC:g}; 插头朝 +Y (局部), 口轴线高 Z{ZC_PORT:g}")
