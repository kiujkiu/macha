"""
motor_tray_v1_0 —— V1.0 电机控制板托板 (2026-11-04 用户: 靠着电机底座放洞洞板上, 80×45×6, 挖散热片槽, 压铜螺母)

  叠层: 洞洞板顶 Z0 → 托板 (Z0..6) → PCB (板底 Z6, 器件面朝上)。散热片 40×20×6 鳍片朝下落在洞洞板上, 顶面贴 MOS 背面。
  · 托板 Y55..100 贴底板边, 靠 2 颗 M6 定位。PCB 转 180°, 外长边 (板系 y=0) 离底板边 2, 沿 X 挪到 CX=35:
    用户 11-04: 按键要按得到 ⇒ 按键 r≈99 出转子 r90; 排针/XT60 焊盘也出法兰
  · 散热片槽 20×40 通槽, 四周闭合, 零间隙 (板系 x52..72 y0..40, 盖住 6 颗 MOS x56..71 y6..35)
  · 2×M6 大扁头对角锁网格 (37.5,62.5) / (62.5,87.5)
  · 4×Φ3.2 通 + 底面 Φ4.2×4.5 沉孔压铜螺母 (同 rim_ring, PCB 孔距 71×31), M3×6 从 PCB 顶面锁, 拉紧时铜螺母靠孔肩
  · 背面让位 3 个浅槽, 深 3: XT60/MR30 两处 (2026-11-04 用户: 这两个座不焊, 直接焊线, 槽留给背面焊点) + 排针
零件系 = 世界 XY, 托板底 Z0。打印: 底面贴床, 所有特征开口朝上, 零支撑。
"""
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import write_stl  # noqa: E402

PLATE_EDGE = 100.0                             # 洞洞板 +Y 边
TRAY_X, TRAY_Y, TRAY_T = 80.0, 45.0, 6.0
Y0 = PLATE_EDGE - TRAY_Y                       # 55: 用户 11-04 裁掉板内侧空白, 只留到 M6 头窝外 1
CX = 35.0                                      # 托板中心 X
EDGE_WALL = 2.0                                # 用户 11-04: 托板要闭合 ⇒ 槽外留壁, PCB 外边离底板边 2
CY = PLATE_EDGE - EDGE_WALL - 20.0
PCB_L, PCB_W, PCB_T = 80.0, 40.0, 1.6

SINK_L, SINK_W, SINK_H = 40.0, 20.0, 6.0
SINK_BX = (52.0, 72.0)                         # 板系 x
PCB_HOLES_B = [(4.49, 4.49), (4.49, 35.49), (75.49, 4.49), (75.49, 35.49)]
M6_HOLES = [(37.5, 62.5), (62.5, 87.5)]        # 对角
BUTTON_B = (16.3, 16.75)                       # SW-SMD 顶按按键, 板系
M6_D, M6_CB_D, M6_FLOOR = 6.5, 13.0, 2.5       # 过孔 / 头窝 (大扁头 Φ12.5×2.5) / 窝底留厚
INSERT_D, INSERT_H = 4.2, 4.5                  # 铜螺母沉孔, 从底面压入
M3_D = 3.2                                     # 通孔
RELIEF_DEPTH = 3.0
# 背面针让位 (板系 x0,x1,y0,y1); 全部闭合, 不开到托板端面 (壁 ≥ 1)
RELIEFS_B = [(1.0, 8.3, 14.8, 30.9), (74.1, 79.0, 19.0, 30.9), (34.7, 42.3, 0.3, 2.8)]


def b2w(bx, by):
    """PCB 板系 → 世界 (转 180°)"""
    return CX - (bx - PCB_L / 2), CY - (by - PCB_W / 2)


PCB_HOLES = [b2w(*p) for p in PCB_HOLES_B]
SINK_X = sorted(b2w(x, 0)[0] for x in SINK_BX)
SINK_Y = (CY - SINK_L / 2, CY + SINK_L / 2)


def _box_b(x0, x1, y0, y1, z0, z1):
    (a, c), (b, d) = b2w(x0, y0), b2w(x1, y1)
    xa, xb, ya, yb = min(a, b), max(a, b), min(c, d), max(c, d)
    return m3d.Manifold.cube((xb - xa, yb - ya, z1 - z0)).translate((xa, ya, z0))


def build():
    p = m3d.Manifold.cube((TRAY_X, TRAY_Y, TRAY_T)).translate((CX - TRAY_X / 2, Y0, 0))
    p -= _box_b(SINK_BX[0], SINK_BX[1], 0, PCB_W, -1, TRAY_T + 1)
    for r in RELIEFS_B:
        p -= _box_b(*r, TRAY_T - RELIEF_DEPTH, TRAY_T + 1)
    for x, y in M6_HOLES:
        p -= m3d.Manifold.cylinder(TRAY_T + 2, M6_D / 2, M6_D / 2, 48).translate((x, y, -1))
        p -= m3d.Manifold.cylinder(TRAY_T, M6_CB_D / 2, M6_CB_D / 2, 64).translate((x, y, M6_FLOOR))
    for x, y in PCB_HOLES:
        p -= m3d.Manifold.cylinder(TRAY_T + 2, M3_D / 2, M3_D / 2, 32).translate((x, y, -1))
        p -= m3d.Manifold.cylinder(INSERT_H + 1, INSERT_D / 2, INSERT_D / 2, 32).translate((x, y, -1))
    return p


def sink():
    """散热片孪生: 底座 2 + 7 鳍, 鳍朝下, 鳍沿 40 长边"""
    x0, y0 = SINK_X[0], SINK_Y[0]
    s = m3d.Manifold.cube((SINK_W, SINK_L, 2.0)).translate((x0, y0, SINK_H - 2.0))
    for i in range(7):
        s += m3d.Manifold.cube((1.4, SINK_L, SINK_H - 2.0)).translate((x0 + i * (SINK_W - 1.4) / 6, y0, 0))
    return s


if __name__ == "__main__":
    p = build()
    out = Path(__file__).with_name("motor_tray_v1_0.stl")
    write_stl(p, out, "POV3D motor_tray_v1_0")
    print(f"wrote {out} vol {p.volume():.0f} mm3, genus {p.genus()}, parts {len(p.decompose())}")
    print(f"托板 X {CX - TRAY_X / 2:g}..{CX + TRAY_X / 2:g}  Y {Y0:.2f}..{Y0 + TRAY_Y:.2f}; 槽 X {SINK_X}  Y {SINK_Y}")
    print("铜螺母 (世界):", [(round(x, 2), round(y, 2)) for x, y in PCB_HOLES])
    assert len(p.decompose()) == 1
    assert min(y for _, y in M6_HOLES) - M6_CB_D / 2 >= Y0 + 1 - 1e-9, "M6 头窝离托板内边不足 1"
    for mx, my in M6_HOLES:   # 头窝与铜螺母至少 1 壁
        for x, y in PCB_HOLES:
            assert ((mx - x) ** 2 + (my - y) ** 2) ** .5 >= (M6_CB_D + INSERT_D) / 2 + 1, "M6 头窝离铜螺母不足 1"
    bx, by = b2w(*BUTTON_B)
    print(f"按键 世界 ({bx:.1f},{by:.1f}) r {(bx * bx + by * by) ** .5:.1f}")
    assert (bx * bx + by * by) ** .5 > 95, "按键没出转子"
    assert Y0 + TRAY_Y <= 100 and CX - TRAY_X / 2 >= -100
    for x, y in M6_HOLES:   # 头窝不破槽
        assert x - M6_CB_D / 2 >= SINK_X[1] + 1 or x + M6_CB_D / 2 <= SINK_X[0] - 1, "M6 头窝离散热片槽不足 1"
    for x, y in PCB_HOLES:  # 铜螺母壁厚
        assert x + INSERT_D / 2 <= SINK_X[0] - 1 or x - INSERT_D / 2 >= SINK_X[1] + 1, "铜螺母离槽太近"
