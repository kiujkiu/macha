"""
glass_seat_v1_1 —— V1.1 透明罩定位环 + 底板 PCB 托架 (2026-10-21)

罩子 (亚克力/PC 管) OD200 × 壁 5 (ID190) 罩整机, 坐在 Φ200 圆底板上 (用户: 玻璃 8 → 亚克力 5)。
本件一体打印:
  · 底座圈 R LIP_IR..100 × SEAT_H: 罩子坐在上面, 外缘与底板齐平。+Y 开过线槽 (电源线从罩子底下钻进来)
  · 定位唇 R LIP_IR..LIP_OR, 高到 Z LIP_TOP, 顶部外倒角 (罩子往下套时自动导正): 插进罩子内孔 (R95) 定心,
    单边名义间隙 0.8 (给管子公差)。唇在 +Y 断开 (LIP_GAP_A), 让给 PCB
  · 4 个凸耳 (±62.5,±62.5) = 底板 M6 网格孔: M6 内六角从顶面锁, 头沉在凸耳里
  · PCB 托架 (2026-10-21 用户: PCB 4×8 cm): 两条导轨 X ±(31..40), 顶面 Z PCB_Z0, 各压 2 颗 M3 热熔铜螺母;
    PCB 内边搭在定子底盘方块顶面 (同为 Z5), 外边落导轨, M3 从上往下锁
上限: 定子 mounting_flange R85 底面 Z15.5 ⇒ LIP_TOP < 15.5; 转子 rim_ring R90 在 Z31.7 以上, 碰不到。
零件系 = 世界系 (底板顶面 Z0)。打印: 原样平放, 底面贴床。

PCB 尺寸/位置 (PCB_*) 也在这里定, 装配 assembly_v1_1.py 直接 import。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "v1.0" / "models"))
from params_v1_0 import write_stl  # noqa: E402

GLASS_OD, GLASS_T, GLASS_H = 200.0, 5.0, 450.0   # 名字沿用 GLASS_*, 实物是亚克力/PC 管
GLASS_IR = GLASS_OD / 2 - GLASS_T             # 95
SEAT_H = 4.0
SLOT_W = 16.0                                 # +Y 过线槽 (贯穿底座圈, 高 = SEAT_H)
LIP_IR, LIP_OR, LIP_TOP, LIP_CH = 91.0, GLASS_IR - 0.8, 12.0, 1.5
LIP_GAP_A = (60.0, 120.0)                     # 唇断开的角度段 (让 PCB)
EAR_D, EAR_C = 14.0, (62.5, 62.5)
M6_D, M6_CB_D, M6_CB_H = 6.5, 11.0, 6.5
GLASS_Z0 = SEAT_H

# ---- 底板 PCB 40 (径向) × 80 (切向), 放 +Y 正对电机线缺口 75..105° ----
# 板底 Z5 = 定子底盘方块顶面: 内边可以伸到方块上面, 只需让开方块顶上的 M6 大扁头 (±37.5,±37.5) Φ12.5
# (头外缘 Y43.75) ⇒ 内边 Y44.25。外角离罩子内壁要 ≥ 1.5。
PCB_W, PCB_L = 40.0, 80.0
PCB_Y0 = 37.5 + 12.5 / 2 + 0.5               # 44.25
PCB_Y1 = PCB_Y0 + PCB_W                       # 84.25
PCB_Z0, PCB_T = 5.0, 1.6
PCB_COMP_TOP = 15.5 - 1.0                     # r<85 内: 定子法兰底 Z15.5 留 1
PCB_COMP_H = PCB_COMP_TOP - (PCB_Z0 + PCB_T)
PCB_HOLES = [(sx * (PCB_L / 2 - 4.0), y) for sx in (1, -1) for y in (PCB_Y0 + 7.0, PCB_Y1 - 7.0)]
RAIL_X = (31.0, 40.0)
RAIL_Y0 = 46.75 + 0.5                         # 让开底盘方块侧面
INSERT_D, INSERT_H = 4.2, 4.5
assert math.hypot(PCB_L / 2, PCB_Y1) <= GLASS_IR - 1.5, "PCB 外角离罩子内壁不足 1.5"


def build():
    seat = (m3d.Manifold.cylinder(SEAT_H, GLASS_OD / 2, GLASS_OD / 2, 256)
            - m3d.Manifold.cylinder(SEAT_H + 2, LIP_IR, LIP_IR, 256).translate((0, 0, -1)))
    seat -= m3d.Manifold.cube((SLOT_W, 20.0, SEAT_H + 2)).translate((-SLOT_W / 2, 88.0, -1))
    lip = (m3d.Manifold.cylinder(LIP_TOP - LIP_CH, LIP_OR, LIP_OR, 256)
           + m3d.Manifold.cylinder(LIP_CH, LIP_OR, LIP_OR - LIP_CH, 256).translate((0, 0, LIP_TOP - LIP_CH)))
    lip -= m3d.Manifold.cylinder(LIP_TOP + 2, LIP_IR, LIP_IR, 256).translate((0, 0, -1))
    a0, a1 = (math.radians(a) for a in LIP_GAP_A)
    wedge = m3d.CrossSection([[(0, 0), (130 * math.cos(a0), 130 * math.sin(a0)), (0, 130),
                               (130 * math.cos(a1), 130 * math.sin(a1))]])
    lip -= m3d.Manifold.extrude(wedge, LIP_TOP + 2).translate((0, 0, -1))
    c = seat + lip
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * EAR_C[0], sy * EAR_C[1]
            ear = m3d.Manifold.cylinder(LIP_TOP, EAR_D / 2, EAR_D / 2, 48).translate((x, y, 0))
            c += ear ^ m3d.Manifold.cylinder(LIP_TOP, LIP_OR - LIP_CH, LIP_OR - LIP_CH, 256)
            c -= m3d.Manifold.cylinder(LIP_TOP + 2, M6_D / 2, M6_D / 2, 32).translate((x, y, -1))
            c -= m3d.Manifold.cylinder(M6_CB_H + 1, M6_CB_D / 2, M6_CB_D / 2, 48).translate((x, y, LIP_TOP - M6_CB_H))
    # PCB 导轨: 从底盘方块外一路接到底座圈, 不伸到罩子壁下面 (r ≤ LIP_OR)
    for sx in (1, -1):
        x0, x1 = sorted((sx * RAIL_X[0], sx * RAIL_X[1]))
        rail = m3d.Manifold.cube((x1 - x0, 100.0 - RAIL_Y0, PCB_Z0)).translate((x0, RAIL_Y0, 0))
        c += rail ^ m3d.Manifold.cylinder(PCB_Z0, LIP_OR, LIP_OR, 256)
    for hx, hy in PCB_HOLES:
        c -= m3d.Manifold.cylinder(INSERT_H + 1, INSERT_D / 2, INSERT_D / 2, 32).translate((hx, hy, PCB_Z0 - INSERT_H))
    return c


if __name__ == "__main__":
    c = build()
    out = Path(__file__).with_name("glass_seat_v1_1.stl")
    write_stl(c, out, "POV3D glass_seat_v1_1 (acrylic tube OD200x5)")
    b = c.bounding_box()
    print(f"wrote {out}  体积 {c.volume():.0f} mm³  bbox {[round(v, 2) for v in b]}")
    print(f"罩子: OD{GLASS_OD:g} ID{2 * GLASS_IR:g} 高 {GLASS_H:g}; 定位唇 R{LIP_IR:g}..{LIP_OR:g} 到 Z{LIP_TOP:g}")
    print(f"PCB {PCB_W:g}×{PCB_L:g}: Y {PCB_Y0:.2f}..{PCB_Y1:.2f}, 外角 r {math.hypot(PCB_L / 2, PCB_Y1):.2f} "
          f"(罩内壁 R{GLASS_IR:g}, 余 {GLASS_IR - math.hypot(PCB_L / 2, PCB_Y1):.2f}); 板 Z {PCB_Z0:g}..{PCB_Z0 + PCB_T:g}, "
          f"元件限高 {PCB_COMP_H:.1f} (r<85); 孔 {PCB_HOLES}")
