"""
index_vane_v2 — v2 装配的静止挡光片。v1 (build_vane.py) 保留不动。

v2 变化:
  • v2 洞洞板网格改为中心锚定 25mm (0/±25..±125)。2026-07-07 缩半径:
    R_SLOT 112→98 (随 sensor_bracket_v2) → 脚改用切向一对 (-100,±25)
    (径向孔 (-100,0) 正好在挡片正下方, (-75,0) 会压到 d100 底座角 R70.7)。
  • θ=180 (随 sensor_bracket_v2, 用户 2026-07-03 晚)。Z 与 v1 相同 (盘面 46.7;
    2026-07-03 曾按错误的 "rim_ring 堆叠+9" 抬到 55.7, 用户纠正后改回):
    梁 (-112, 0, 37.7); 槽口底 28; 挡片顶 39 (>37.7, <槽底板 41)。盘厚6→5后整体-1 (2026-07-06)。

  • 脚: 5mm 板 X -108..-92 × Y ±32, 2× Φ6.5 M6 @ (-100,±25) 切向跨挡片。
  • 挡片: 径向窄 4 (X -100..-96, 居中 R98), 切向长 — 槽下 ±5 粗, 槽内 ±4 薄。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

BEAM = (-98.0, 0.0, 37.7)
FOOT_Z = 5.0
M6_GRID = [(-100.0, 25.0), (-100.0, -25.0)]   # 切向一对, 跨挡片
M6_CLEAR = 6.5
BLADE_X0, BLADE_X1 = -100.0, -96.0            # 4mm 径向, 居中 R98
SLOT_BOT = 28.0                                # 模块槽口下沿 (盘面 45.7)
BLADE_TOP = 39.0                               # > 梁 37.7, < 槽底板 41
LOW_HALF, UP_HALF = 5.0, 4.0                   # 切向半厚 (槽下 10 / 槽内 8)

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def zcyl(z0, z1, r, x, y, seg=32):
    return m3d.Manifold.cylinder(z1-z0, r, r, seg, False).translate((x, y, z0))

# 脚
vane = box(-108.0, -92.0, -32.0, 32.0, 0.0, FOOT_Z)
for (x, y) in M6_GRID:
    vane = vane - zcyl(-1, FOOT_Z + 1, M6_CLEAR/2, x, y)
# 挡片: 槽下粗段 + 槽内薄段
vane = vane + box(BLADE_X0, BLADE_X1, -LOW_HALF, LOW_HALF, FOOT_Z - 1, SLOT_BOT)
vane = vane + box(BLADE_X0, BLADE_X1, -UP_HALF, UP_HALF, SLOT_BOT, BLADE_TOP)

# ---- export ----
mesh = vane.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("index_vane_v2.stl")
with out.open("wb") as f:
    f.write(b"POV3D index_vane_v2".ljust(80, b" ")[:80])
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
print(f"index_vane_v2.stl  {len(tris)} tris  X {v[:,0].min():.1f}..{v[:,0].max():.1f}  "
      f"Y {v[:,1].min():.1f}..{v[:,1].max():.1f}  Z {v[:,2].min():.1f}..{v[:,2].max():.1f}  "
      f"vol {vane.volume()/1000:.2f}cm³")
print(f"脚 M6 @ {M6_GRID}; 挡片 X{BLADE_X0:g}..{BLADE_X1:g}, 顶 {BLADE_TOP:g}; 梁 {BEAM}")
