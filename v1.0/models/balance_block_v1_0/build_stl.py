"""
balance_block_v1_0 —— V1.0 无屏动平衡 M6 配重块 (2026-11-05 用户: 配重不够, 做配重件)

  实测 (balance/solve_four_run.py): 总配重 ~1400~1700 g·mm, 方向 ~84° (孔 2/3 之间偏 2 号), M3 叠不够。
  · 弧形块平贴 rim_ring 顶面 (世界 Z42.2), 2×M3 借相邻两个 R82.5 孔 (相隔 45°) 拧进 hub 铜螺母; 顶面 Φ7.5×2 头沉, 用 M3×14。
  · 4×M6 @ r83, 中心 ±5° / ±15°; 底面 Φ13 头窝, M6 大扁头 (Φ12.5×2.5) 头朝下藏窝里, 螺杆朝上, 上面叠螺母配重。
  · 全部在 R90 内 (用户定)。M6 螺母柱 (对角 11.5) 只有世界角 56.8°~65° (及镜像) 会碰 DR1M90 板角 r80.6: 块中心在 45°/135°/225°/315° 时靠 ±Y 的端列不能用。
  · 厚 4.8: 顶 Z47.0, 比 DR1M90 板底 Z47.2 低 0.2, 块本身不碰板。
  · M3 微调不在块上: 用其余 R82.5 环孔 + 块上 2 颗 M3 头下加垫片。
  · 上屏前要拆: 上屏后不平衡完全不同 (见 balance_v1_0.py)。
零件系: 块中心在 +Y (90°), 原点 = 转轴, 底面 Z0 贴 rim_ring。
打印: 顶面贴床 (窝口朝上), 零支撑; 主 STL 已是打印姿态, *_asm.stl 是装配姿态。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import RING_OUTER_PCD_R, write_stl  # noqa: E402

R_IN, R_OUT, T = 76.0, 90.0, 4.8       # 用户 11-05: 不能超转子盘 R90 (尺寸尽头)
HALF = 29.0                       # 弧半角
M3_DEG = 22.5                     # 相邻环孔相隔 45°
M3_D = 3.2
M3_CB_D, M3_CB_DEEP = 7.5, 2.0     # 用户 11-05: M3 头 Φ7×1.5 要沉 (同 rim_ring 头沉 Φ7.5×2)
M6_R, M6_D = 83.0, 6.5
M6_DEG = (-15.0, -5.0, 5.0, 15.0)
CB_D, CB_DEEP = 13.0, 2.8         # 头窝: 大扁头 Φ12.5×2.5
RHO = 1.10                        # g/cm³, 打印件等效 (同 balance_v1_0.PRINT_RHO)


def pol(r, a):
    a = math.radians(90.0 + a)
    return r * math.cos(a), r * math.sin(a)


M3_HOLES = [pol(RING_OUTER_PCD_R, s * M3_DEG) for s in (-1, 1)]
M6_HOLES = [pol(M6_R, a) for a in M6_DEG]


def outline(n=48):
    a = np.radians(90.0 + np.linspace(-HALF, HALF, n))
    return [(R_OUT * math.cos(x), R_OUT * math.sin(x)) for x in a] + \
           [(R_IN * math.cos(x), R_IN * math.sin(x)) for x in a[::-1]]


def cyl(d, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, 64).translate((x, y, z0))


def build():
    p = m3d.CrossSection([outline()]).extrude(T)
    for x, y in M3_HOLES:
        p -= cyl(M3_D, x, y, -1, T + 1)
        p -= cyl(M3_CB_D, x, y, T - M3_CB_DEEP, T + 1)
    for x, y in M6_HOLES:
        p -= cyl(M6_D, x, y, -1, T + 1)
        p -= cyl(CB_D, x, y, -1, CB_DEEP)
    return p


if __name__ == "__main__":
    p = build()
    here = Path(__file__).parent
    write_stl(p, here / "balance_block_v1_0_asm.stl", "POV3D balance_block_v1_0 asm")
    flip = p.rotate((180, 0, 0)).translate((0, 0, T))     # 顶面贴床
    v = write_stl(flip, here / "balance_block_v1_0.stl", "POV3D balance_block_v1_0 print")
    m = p.volume() / 1000 * RHO
    mesh = p.to_mesh(); vp = np.asarray(mesh.vert_properties)[:, :3]; tri = vp[np.asarray(mesh.tri_verts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = np.einsum("ij,ij->i", a, np.cross(b, c)); cg = (d[:, None] * (a + b + c)).sum(0) / 24 / (d.sum() / 6)
    gap = min(math.dist(q, h) - (CB_D + M3_D) / 2 for q in M3_HOLES for h in M6_HOLES)
    gap6 = min(math.dist(M6_HOLES[i], M6_HOLES[i + 1]) - CB_D for i in range(3))
    print(f"体积 {p.volume():.0f} mm³, 估重 {m:.1f} g, 质心 r{cg[1]:.1f}, 块自身 {m * cg[1]:.0f} g·mm; genus {p.genus()}")
    print(f"窝-M3 孔壁 {gap:.2f}, 窝-窝壁 {gap6:.2f}, 外壁 {R_OUT - M6_R - CB_D / 2:.2f}, 内壁 {M6_R - CB_D / 2 - R_IN:.2f}, 窝底 {T - CB_DEEP:.1f}")
    print("Z", v[:, 2].min(), v[:, 2].max())
