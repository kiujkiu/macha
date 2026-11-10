"""
m3_bush_v4 — top_cap_v4 的 Φ6.5 (M6) 配重孔转 M3 用的打印衬套 (2026-11-10, 用户: 没有 Φ12 垫片, 做一个和 M6 兼容的)。
孔本身不改 (拆掉衬套照样插 M6)。每个孔用 2 个同样的衬套: 上面一个凸台朝下插入, 下面一个凸台朝上插入,
两凸台在孔中不相碰 (3+3 < 条厚 7), 靠两个 Φ12 法兰把条夹住; M3 螺丝从上穿, 螺母在下。
  · 法兰 Φ12 × 1 (用户 11-10: 1 mm 够), 凸台 Φ6.2 × 3 (孔 Φ6.5, 单边 0.15 间隙), 中孔 Φ3.4。
  · 打印: 法兰贴床, 凸台朝上, 0.2 层, 100% 填充 (PETG/PLA 都行)。每孔 2 个, 建议打 8 个。
适用孔 (顶盖零件系): 条端 (−11, ±56) r57 = 101°/259°, 翼 (−55, ±14) r56.8 = 166°/194°。
  核过: 法兰 Φ12 @ (−11,±56) 离偏心屏顶 M3 头 (+6.7,±64) 10.7; 翼侧孔法兰离中孔 M6 大扁头 Φ12.5 1.75。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

FL_D, FL_T = 12.0, 1.0
SP_D, SP_H = 6.2, 3.0
BORE = 3.4
BAR_T, HOLE_D = 7.0, 6.5
assert 2 * SP_H < BAR_T - 0.5 and SP_D < HOLE_D

def cyl(d, h, z0=0.0, seg=64):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, seg, False).translate((0, 0, z0))

part = cyl(FL_D, FL_T) + cyl(SP_D, SP_H, FL_T)
part -= cyl(BORE, FL_T + SP_H + 2, -1)
mesh = part.to_mesh()
v = np.asarray(mesh.vert_properties)[:, :3]
t = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("m3_bush_v4.stl")
with out.open("wb") as f:
    f.write(b"POV3D m3_bush_v4 (print pose)".ljust(80, b" "))
    f.write(struct.pack("<I", len(t)))
    for a, b, c in t:
        n = np.cross(v[b] - v[a], v[c] - v[a]); L = np.linalg.norm(n); n = n / L if L else n
        f.write(struct.pack("<12fH", *n, *v[a], *v[b], *v[c], 0))
vol = part.volume()
print(f"wrote {out.name}: {len(t)} tris, {vol:.0f} mm3 ≈ {vol*1.27/1000:.2f} g PETG; 总高 {FL_T+SP_H:g}")
