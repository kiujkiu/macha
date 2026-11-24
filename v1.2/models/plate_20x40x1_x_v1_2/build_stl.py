"""
plate_20x40x1_x_v1_2 X 字框片 (2026-11-24, 用户指定; 同日筋宽 3 → 2 并移入 V1.2)

20×40×1 薄板, 挖 4 个三角形通孔 ⇒ 四边外框 + 两条对角筋 (X)。
  - 外框边宽 / 对角筋宽 都是 2 (平面内, 对角筋按垂直于筋的方向量)
  - 对角筋中线 = 外轮廓角到角
"""
import math, struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

W, H, T = 20.0, 40.0, 1.0
RIB = 2.0

# ===== 三角孔: 内框 (W-2RIB)×(H-2RIB) 减去两条对角筋 =====
IX, IY = W / 2 - RIB, H / 2 - RIB                 # 内框半宽 / 半高
K = H / W                                         # 对角线斜率
C = RIB / 2 * math.hypot(1, K)                    # 筋边线 y = K x ± C
TOP   = [(0, C), ((IY - C) / K, IY), (-(IY - C) / K, IY)]          # 上三角 (下三角 = 上下镜像)
RIGHT = [(C / K, 0), (IX, -(K * IX - C)), (IX, K * IX - C)]        # 右三角 (左三角 = 左右镜像)
TRIS = [TOP, [(-x, -y) for x, y in TOP], RIGHT, [(-x, -y) for x, y in RIGHT]]

if __name__ == "__main__":
    plate = m3d.Manifold.cube((W, H, T), True).translate((0, 0, T / 2))
    for t in TRIS:
        cs = m3d.CrossSection([np.array(t, dtype=np.float64)], m3d.FillRule.NonZero)
        plate = plate - m3d.Manifold.extrude(cs, T + 2).translate((0, 0, -1))
    mesh = plate.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]; tr = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name("plate_20x40x1_x_v1_2.stl")
    with out.open("wb") as f:
        f.write(b"plate 20x40x1 X rib 2".ljust(80, b" ")); f.write(struct.pack("<I", len(tr)))
        for t in tr:
            a, b, c = v[t]; n = np.cross(b - a, c - a); L = np.linalg.norm(n); n = n / L if L > 0 else n
            f.write(struct.pack("<12fH", *n, *a, *b, *c, 0))
    def area(t): return abs(sum(t[i][0] * t[(i + 1) % 3][1] - t[(i + 1) % 3][0] * t[i][1] for i in range(3))) / 2
    theory = (W * H - sum(map(area, TRIS))) * T
    assert abs(plate.volume() - theory) < 0.01 and plate.genus() == 4 and len(plate.decompose()) == 1
    print("bbox", v.min(0), v.max(0), "三角面", len(tr), "通孔数", plate.genus())
    print(f"体积 {plate.volume():.2f} (理论 {theory:.2f}) mm3, PLA {plate.volume()*1.24e-3:.2f} g")
    print("上下三角 底 %.3f 高 %.3f; 左右三角 底 %.3f 高 %.3f" % (TOP[1][0]*2, IY-C, 2*RIGHT[2][1], IX-C/K))
