"""
screen_solder_jig_bar — screen_solder_jig 的可卸底条 (2026-07-21 用户).

红框圈出的那条底部带: 取 screen_solder_jig 外缘 10mm (Y >= CUT_Y) 的部分,
即 L 形截面 = 底端壁 (含 3×M3) + 前方一条底面唇边, 全宽 158.3。
坐标系与 screen_solder_jig 一致 (X 居中, 同一 Z), 便于回装。

⚠ 参数镜像 screen_solder_jig/build_stl.py — 改夹具尺寸时这里要同步。
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters (mirror screen_solder_jig) =====
CAV_W, CAV_H, DEPTH = 150.3, 169.05, 15.0
WALL, FLOOR = 4.0, 3.0
OUT_W = CAV_W + 2 * WALL     # 158.3
OUT_H = CAV_H + 2 * WALL     # 177.05
OUT_Z = DEPTH + FLOOR        # 18
HOLE_D, HOLE_XS = 3.2, [-64.0, 0.0, 64.0]
HOLE_Z = FLOOR + 6.6         # 9.6

BAR_DEPTH_Y = 10.0           # 底条 Y 向宽度 (用户 2026-07-21: 26.525→10)
yo = OUT_H / 2               # 88.525
CUT_Y = yo - BAR_DEPTH_Y     # 78.525 — 保留外缘 10mm 带 (端壁4 + 底唇6)

_slop = 0.1

# ===== Build the jig (same construction), then keep only Y >= CUT_Y =====
outer = m3d.Manifold.cube((OUT_W, OUT_H, OUT_Z), False).translate(
    (-OUT_W / 2, -OUT_H / 2, 0.0))
cav = m3d.Manifold.cube((CAV_W, CAV_H, DEPTH + _slop), False).translate(
    (-CAV_W / 2, -CAV_H / 2, FLOOR))
jig = outer - cav

_hy = OUT_H + 4.0
for x in HOLE_XS:
    h = m3d.Manifold.cylinder(_hy, HOLE_D / 2, HOLE_D / 2, 32, False)
    h = h.translate((0.0, 0.0, -_hy / 2)).rotate((90.0, 0.0, 0.0)).translate((x, 0.0, HOLE_Z))
    jig = jig - h

# Keep box: full X, Y in [CUT_Y, yo], full Z
_kh = (yo + 1.0) - CUT_Y
keep = m3d.Manifold.cube((OUT_W + 2.0, _kh, OUT_Z + 2.0), False).translate(
    (-(OUT_W + 2.0) / 2, CUT_Y, -1.0))
bar = jig ^ keep

# ===== Export STL =====
mesh = bar.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("screen_solder_jig_bar.stl")
with out.open("wb") as f:
    f.write(b"POV3D screen_solder_jig_bar (removable bottom L-bar)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

assert 84 + len(tris) * 50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris, {len(verts)} verts)")
print(f"  L-bar: 全宽 {OUT_W:g} (X), Y {CUT_Y:g}..{yo:g} (深 {yo-CUT_Y:g}), Z 0..{OUT_Z:g}")
print(f"  = 端壁 {WALL:g} 厚×{OUT_Z:g} 高 (含 3×M3 @X{HOLE_XS} Z{HOLE_Z:g}) + 底唇 {yo-CUT_Y-WALL:g} 宽×{FLOOR:g} 厚")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
      f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
print(f"  volume {bar.volume()/1000:.1f} cm^3")
