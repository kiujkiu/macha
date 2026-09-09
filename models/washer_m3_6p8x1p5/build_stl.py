"""
POV 3D 平垫圈 washer_m3_6p8x1p5 (2026-09-07, 用户指定)

最简单的一个件: 一个圆环片, 没有别的特征。
  - 外圆 Φ6.8 × 厚 1.5
  - 中央 Φ3.3 通孔 (M3 螺杆过孔)

尺寸全部由用户直接给定, 不派生自任何其它零件, 所以本文件没有 assert 防漂移
(没有可漂移的上游参数)。要改就改下面三个常量。

参考: 标准 M3 平垫圈 GB/T 848 是 Φ6×0.5、GB/T 97.1 是 Φ7×0.5 ——
本件 Φ6.8×1.5 是加厚的非标件, 用来在螺栓链里补厚度。
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== 参数 (2026-09-07 用户指定) =====
OD    = 6.8     # 外径
ID    = 3.3     # 内径 (M3 过孔)
THICK = 1.5     # 厚度

CYL_SEG  = 128
HOLE_SEG = 96

assert ID < OD, "内径必须小于外径"
WALL = (OD - ID) / 2      # 派生: 单边环宽 1.75

# ===== 建模 =====
part = m3d.Manifold.cylinder(THICK, OD / 2, OD / 2, CYL_SEG, False)
hole = m3d.Manifold.cylinder(THICK + 2, ID / 2, ID / 2, HOLE_SEG, False)
part = part - hole.translate((0, 0, -1.0))

# ===== 导出 STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("washer_m3_6p8x1p5.stl")
with out.open("wb") as f:
    _hdr = f"POV3D washer OD{OD:g} ID{ID:g} T{THICK:g}".encode("ascii")
    f.write(_hdr.ljust(80, b" ")[:80])   # STL 头必须 <=80 字节并截断
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

expected = 84 + len(tris) * 50
assert out.stat().st_size == expected, \
    f"STL 大小不对: {out.stat().st_size} != {expected} (STL 头溢出?)"

import math
vol_theory = math.pi / 4 * (OD**2 - ID**2) * THICK

print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume:        {part.volume():10.3f} mm^3   "
      f"(理论 {vol_theory:.3f}, 差 {abs(part.volume()-vol_theory)/vol_theory*100:.2f}% 多边形近似)")
print(f"  surface area:  {part.surface_area():10.3f} mm^2")
print(f"  PLA 约 {part.volume()*1.24e-3:.3f} g / 只")
print(f"  外圆 Φ{OD:g} / 内孔 Φ{ID:g} / 厚 {THICK:g} / 环宽 (单边) {WALL:g}")
