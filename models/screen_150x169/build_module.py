"""
screen_150x169 — 新屏幕数字孪生 (BOUGHT part, 不打印, 无加工图) 2026-07-02。

替代 v2 里原计划的 2×HUB75。本体 150(宽Y)×169(高Z)×7.27(厚X)。
局部坐标系 = 装配对齐 (未转45°前): LED 发光面 = X=0 平面 (朝 +X, 落在旋转轴平面上,
沿用 v1 POV 惯例), 板体 X -7.27..0, 宽度居中 Y ±75, Z0 = 屏幕下边沿。

特征:
  • 4 × M3 孔 (屏上自带螺母, 建 Φ3.2 通孔示意) — 梯形阵:
      下排 (±52.5, 10.5)   横距 105, 距底边 10.5
      上排 (±49.975, 157.5) 横距 99.95, 上下排距 147 (距顶边 11.5)
  • 背面接口: 50(宽Y)×30(高Z), 中心距底边 60, 左右居中 → Y ±25, Z 45..75,
    从背面 (X=-7.27) 向 -X 凸出 CONN_D (实际凸出深度未测, 占位 6)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

W, H, T = 150.0, 169.0, 7.27
HOLE_D = 3.2
HOLES = [(-52.5, 10.5), (52.5, 10.5), (-49.975, 157.5), (49.975, 157.5)]
CONN_W, CONN_H, CONN_ZC, CONN_D = 50.0, 30.0, 60.0, 6.0   # CONN_D 占位!

body = m3d.Manifold.cube((T, W, H), False).translate((-T, -W/2, 0.0))
conn = m3d.Manifold.cube((CONN_D, CONN_W, CONN_H), False).translate(
    (-T - CONN_D, -CONN_W/2, CONN_ZC - CONN_H/2))
scr = body + conn
for (y, z) in HOLES:
    cyl = m3d.Manifold.cylinder(T + 2, HOLE_D/2, HOLE_D/2, 32, False)
    scr = scr - cyl.rotate((0, 90, 0)).translate((-T - 1, y, z))

mesh = scr.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("screen_150x169.stl")
_hdr = b"POV3D screen_150x169 module"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80]); f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris) * 50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)")
print(f"  body {W:g}×{H:g}×{T:g}, LED face X=0; holes {HOLES}")
print(f"  connector {CONN_W:g}×{CONN_H:g} @ Zc={CONN_ZC:g}, 凸出 {CONN_D:g} (占位)")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
      f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
