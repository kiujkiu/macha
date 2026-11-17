"""
地脚垫高圆筒 leg_riser_d55x60 (2026-09-14, 用户指定)

原地脚高度差 10cm; 用户换思路, 不复刻方形地脚, 改做一个圆筒垫高件:
  - 圆筒 外径 Φ55 / 内径 Φ46 / 高 60 (壁厚 4.5)
  - 内部米字加强: 4 根厚 5 的筋 (0°/45°/90°/135°) 过中心交叉, 两端并入筒壁
  - 加强筋从底面 Z=0 做到 Z=55, 最上面 5mm 不做加强

尺寸全部由用户直接给定, 不派生自任何其它零件。
坐标: 筒轴 = Z, 底面 (有筋那头) Z=0, 0° 筋沿 X 轴。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d
from shapely.geometry import Point, box
from shapely.affinity import rotate as s_rotate
from shapely.ops import unary_union

# ===== 参数 (2026-09-14 用户指定) =====
OD         = 55.0    # 外径
ID         = 46.0    # 内径
H          = 60.0    # 总高
RIB_T      = 5.0     # 米字加强筋厚度
TOP_CLEAR  = 5.0     # 最上面不做加强的高度
RIB_ANGLES = (0, 45, 90, 135)

CYL_SEG = 256

R_OD, R_ID = OD / 2, ID / 2
WALL  = R_OD - R_ID          # 4.5
RIB_H = H - TOP_CLEAR        # 55
RIB_L = R_ID + R_OD          # 筋条总长: 两端各伸进壁厚中线, 保证与筒壁融合

assert ID < OD
assert 0 < TOP_CLEAR < H
# 筋条矩形的四个角必须落在外圆内, 否则会从筒外壁冒出来
assert math.hypot(RIB_L / 2, RIB_T / 2) < R_OD * math.cos(math.pi / CYL_SEG), "筋条角点穿出外壁"

# ===== 建模 =====
tube = (m3d.Manifold.cylinder(H, R_OD, R_OD, CYL_SEG, False)
        - m3d.Manifold.cylinder(H + 2, R_ID, R_ID, CYL_SEG, False).translate((0, 0, -1)))

bar = m3d.Manifold.cube((RIB_L, RIB_T, RIB_H), False).translate((-RIB_L / 2, -RIB_T / 2, 0))
ribs = bar.rotate((0, 0, RIB_ANGLES[0]))
for a in RIB_ANGLES[1:]:
    ribs = ribs + bar.rotate((0, 0, a))

part = tube + ribs

# ===== 校核 =====
assert len(part.decompose()) == 1, "件不是一整块"

# 理论体积 (shapely 真圆近似到 0.01 级): 筒壁环 × H + 米字筋在内孔内的面积 × RIB_H
disk_id = Point(0, 0).buffer(R_ID, quad_segs=2048)
strip = box(-R_OD, -RIB_T / 2, R_OD, RIB_T / 2)
rib_area = unary_union([s_rotate(strip, a, origin=(0, 0)) for a in RIB_ANGLES]).intersection(disk_id).area
ring_area = math.pi * (R_OD**2 - R_ID**2)
vol_theory = ring_area * H + rib_area * RIB_H

# 分层截面: 筋区 / 顶部无筋区
a_low = part.slice(RIB_H / 2).area()
a_top = part.slice(H - TOP_CLEAR / 2).area()
a_top_expect = CYL_SEG / 2 * math.sin(2 * math.pi / CYL_SEG) * (R_OD**2 - R_ID**2)  # 正多边形环
assert abs(a_top - a_top_expect) < 1e-3, f"顶部 {TOP_CLEAR} 区不该有筋: {a_top} vs {a_top_expect}"
assert a_low > a_top + 0.9 * rib_area, "筋区截面积不对"

# ===== 导出 STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("leg_riser_d55x60.stl")
with out.open("wb") as f:
    _hdr = f"leg_riser OD{OD:g} ID{ID:g} H{H:g} rib{RIB_T:g}".encode("ascii")
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

vol = part.volume()
print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume:        {vol:10.2f} mm^3   "
      f"(理论 {vol_theory:.2f}, 差 {abs(vol-vol_theory)/vol_theory*100:.3f}% 多边形近似)")
print(f"    = 筒壁 {ring_area*H:.2f} + 米字筋 {rib_area:.2f} mm^2 × {RIB_H:g} = {rib_area*RIB_H:.2f}")
print(f"  截面积 Z={RIB_H/2:g}: {a_low:.2f} (含筋)  /  Z={H-TOP_CLEAR/2:g}: {a_top:.2f} (纯环)")
print(f"  PLA 实心约 {vol*1.24e-3:.1f} g")
print(f"  Φ{OD:g}/Φ{ID:g} 壁厚 {WALL:g} / 高 {H:g} / 米字筋厚 {RIB_T:g} 高 {RIB_H:g} / 顶部无筋 {TOP_CLEAR:g}")
