"""
usb_wifi_module — AX1800 网卡数字孪生, 第三版 (2026-07-09): 侧立整块包络。

用户定稿: 天线反折收进本体, 整块 = 14.5×40×70, 以 14.5×70 面坐盘, 40 竖直,
插头朝 +Y。孪生 = 整块 + 侧立插头 + 插合母头 + 线缆头, 建在盘系最终位
(Z0 = 盘顶面), assembly_v2 只做 +DISC_TOP 平移 + ROTOR_ROT 旋转。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

from wifi_common import (BLK_H, BLK_T, PLUG_L, PLUG_W, PLUG_T, FEM_L, FEM_W,
                         FEM_T, CABLE_D, XC, BLK_Y0, BLK_Y1, ZC_PORT)

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

# 整块 (侧立)
part = box(XC-BLK_T/2, XC+BLK_T/2, BLK_Y0, BLK_Y1, 0, BLK_H)
# USB 头 (侧立: 4.5 宽 × 12 高, 居中)
part += box(XC-PLUG_T/2, XC+PLUG_T/2, BLK_Y1, BLK_Y1+PLUG_L,
            ZC_PORT-PLUG_W/2, ZC_PORT+PLUG_W/2)
# 母头壳 (侧立: 10.3 宽 × 18.7 高; 插合态, 前面贴块尾, 吞下插头)
part += box(XC-FEM_T/2, XC+FEM_T/2, BLK_Y1, BLK_Y1+FEM_L,
            ZC_PORT-FEM_W/2, ZC_PORT+FEM_W/2)
# 线缆头 20mm
part += m3d.Manifold.cylinder(20.0, CABLE_D/2, CABLE_D/2, 32, False)\
    .rotate((-90, 0, 0)).translate((XC, BLK_Y1+FEM_L, ZC_PORT))

# ===== export =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("usb_wifi_module.stl")
with out.open("wb") as f:
    f.write(b"POV3D usb_wifi_module v3 (bought, twin)".ljust(80, b" ")[:80])
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
print(f"  侧立整块 {BLK_T:g}×{BLK_H:g}×{BLK_Y1-BLK_Y0:g} @ X{XC:g}; 插头朝 +Y (同 J6), 轴线高 Z{ZC_PORT:g}")
