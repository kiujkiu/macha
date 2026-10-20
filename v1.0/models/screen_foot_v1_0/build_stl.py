"""
screen_foot_v1_0 —— V1.0 屏幕底座 (2026-10-20 第 3 版)。沿用 V0.3.1 portal_tee 的结构 (用户: 方便 3D 打印):
**整件所有特征都从同一个平面 (内侧面 Y=Y_IN) 长出来 —— 平躺、内侧面贴床, 零支撑**。

每侧板边一件 (+Y 件 / -Y 件互为 Y 镜像, 各打一件)。螺母列轴线 (COL_X, ±COL_Y):
  · 底条 (厚 5): X ±BAR_X, Y Y_IN..BAR_Y1; 2×Φ3.4 借 **rim_ring 外圈 R82.5 现成环孔**
    (+Y 件 67.5°/112.5°, -Y 件 247.5°/292.5°), M3 拧进 **hub_disc 底面铜螺母** (rim_ring 不加孔)
  · 梯形加强壁 (厚 WALL_T, 齐内侧面): 底边 = 底条全宽, 顶边 = 顶托宽; 在两颗环孔正上方开 Φ8
    竖直工艺井 (贯穿到壁顶) —— Φ7 螺丝头 + 批头从上面直进直出 (同 portal_tee)
  · 两条立腿 (轴线 ±X 两侧, 内侧离轴线 4) + 顶托 (厚 5, 顶面 = 灯板下沿) 托两块灯板下角
  · 屏幕下螺丝轴线: 顶托 Φ3.4 过孔; 壁沿轴线开 Φ8 半圆槽 (底条顶 → 顶托底) 给 Φ7 头让位;
    底条上轴线孔 Φ3 (用户 2026-10-20: 原 Φ8 让位孔改 Φ3)
  · 外形裁到 R ≤ CLIP_R, 给以后罩住 LED 以下的圆罩子让位

零件系 = 世界系 (+Y 件), 直接放进装配; -Y 件 = 绕 XZ 面镜像。
打印: 内侧面 (Y=Y_IN) 朝下贴床 —— 底条/壁/腿/顶托都是从这个面拉伸出来的棱柱。
输出: *_posY/negY.stl = 打印姿态 (内侧面 Z0 贴床, XY 居中); *_asm.stl = 世界系 (装配用)。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import (COL_X, COL_Y, DISC_OD, DISC_TOP, LED_EDGE_BOT_Z, M3_HEAD_D, M3_HEAD_H,  # noqa: E402
                         RING_OUTER_PCD_R, write_stl)

HEAD_D, HEAD_H = M3_HEAD_D, M3_HEAD_H   # Φ7×3
HEAD_CLR = 0.5
WELL_D = HEAD_D + 2 * HEAD_CLR       # 工艺井 / 让位 Φ8 (头 Φ7 单边 0.5)
RING_R, RING_A = RING_OUTER_PCD_R, (67.5, 112.5)   # 借用的 rim_ring 外圈环孔 (+Y 件)
RING_HOLES = [(RING_R * math.cos(math.radians(a)), RING_R * math.sin(math.radians(a))) for a in RING_A]
Y_IN = 71.0                          # 内侧面 = 打印贴床面 (DR1M90 板边 Y70 外留 1)
BAR_T = 5.0                          # 底条厚 (Z)
BAR_X = max(abs(x) for x, _ in RING_HOLES) + HEAD_D / 2 + 0.5     # 35.57
BAR_Y1 = max(y for _, y in RING_HOLES) + HEAD_D / 2 + 1.5         # 81.22
WALL_T = 5.0                         # 梯形壁厚 (Y 71..76, 同 portal_tee)
LEG_IN, LEG_W = HEAD_D / 2 + HEAD_CLR, 5.0                         # 腿内侧离轴线 4 / 腿宽
LEG_Y1 = 80.5                        # 腿/顶托外沿 (顶托托住板角, 板边 81.975)
TRAY_T = 5.0
SCREW_D = 3.4
AXIS_BAR_D = 3.0                     # 底条上轴线孔 (用户 2026-10-20)
CLIP_R = RING_R + HEAD_D / 2 + 1.0   # 87 (Φ7 头外缘 r86; 圆罩内壁要 ≥ 此值)
Z0, Z1 = DISC_TOP, LED_EDGE_BOT_Z
LX0, LX1 = COL_X - LEG_IN - LEG_W, COL_X + LEG_IN + LEG_W          # 两腿外侧 = 顶托宽
FOOT_HOLES_WORLD = [(x, sy * y) for sy in (1, -1) for x, y in RING_HOLES]
assert min(y for _, y in RING_HOLES) - HEAD_D / 2 > Y_IN, "Φ7 螺丝头伸进 DR1M90 板边下"
assert CLIP_R < DISC_OD / 2


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg).translate((x, y, z0))


def prism_xz(pts, y0, y1):
    """X-Z 平面多边形沿 Y 拉伸 (y0..y1)。"""
    a2 = sum(pts[i][0] * (pts[(i + 1) % len(pts)][1] - pts[i - 1][1]) for i in range(len(pts)))
    if a2 < 0:
        pts = pts[::-1]
    return m3d.CrossSection([pts]).extrude(y1 - y0).rotate((90, 0, 0)).translate((0, y1, 0))


def build():
    bar = box(-BAR_X, BAR_X, Y_IN, BAR_Y1, Z0, Z0 + BAR_T)
    wall = prism_xz([(-BAR_X, Z0 + BAR_T), (BAR_X, Z0 + BAR_T), (LX1, Z1 - TRAY_T), (LX0, Z1 - TRAY_T)],
                    Y_IN, Y_IN + WALL_T)
    legs = [box(LX0, COL_X - LEG_IN, Y_IN, LEG_Y1, Z0, Z1), box(COL_X + LEG_IN, LX1, Y_IN, LEG_Y1, Z0, Z1)]
    tray = box(LX0, LX1, Y_IN, LEG_Y1, Z1 - TRAY_T, Z1)
    f = m3d.Manifold.batch_boolean([bar, wall, *legs, tray], m3d.OpType.Add)
    f ^= m3d.Manifold.cylinder(Z1 - Z0 + 2, CLIP_R, CLIP_R, 360).translate((0, 0, Z0 - 1))
    for x, y in RING_HOLES:                                   # 环孔: Φ3.4 + 上方 Φ8 工艺井贯穿壁
        f -= cyl(SCREW_D, x, y, Z0 - 1, Z0 + BAR_T + 1)
        f -= cyl(WELL_D, x, y, Z0 + BAR_T, Z1 + 1)
    f -= cyl(WELL_D, COL_X, COL_Y, Z0 + BAR_T, Z1 - TRAY_T)   # 底条顶 → 顶托底: Φ7 头让位
    f -= cyl(AXIS_BAR_D, COL_X, COL_Y, Z0 - 1, Z0 + BAR_T + 1)  # 底条轴线孔 Φ3
    f -= cyl(SCREW_D, COL_X, COL_Y, Z1 - TRAY_T - 1, Z1 + 1)  # 顶托过孔
    # 自检: 环孔螺丝头 + 批头竖直通道、长螺丝通道 内无实体; 贴床面 = 内侧面
    for x, y in RING_HOLES:
        assert (f ^ cyl(WELL_D, x, y, Z0 + BAR_T + 0.01, Z1 + 5)).volume() < 1e-6, "环孔上方工艺井不通"
    assert (f ^ cyl(WELL_D, COL_X, COL_Y, Z0 + BAR_T + 0.01, Z1 - TRAY_T - 0.01)).volume() < 1e-6, "螺丝头让位槽不通"
    assert abs(f.bounding_box()[1] - Y_IN) < 1e-6, "贴床面不是内侧面"
    return f


if __name__ == "__main__":
    f = build()
    here = Path(__file__).parent
    fn = f.mirror((0, 1, 0))
    write_stl(f, here / "screen_foot_v1_0_posY_asm.stl", "POV3D screen_foot_v1_0 +Y (asm)")
    write_stl(fn, here / "screen_foot_v1_0_negY_asm.stl", "POV3D screen_foot_v1_0 -Y (asm, mirror)")
    for part, ang, tag in ((f, 90, "posY"), (fn, -90, "negY")):       # 内侧面 → Z0 贴床
        pp = part.rotate((ang, 0, 0))
        b = pp.bounding_box()
        pp = pp.translate((-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]))
        write_stl(pp, here / f"screen_foot_v1_0_{tag}.stl", f"POV3D screen_foot_v1_0 {tag} (print pose)")
    bb = f.bounding_box()
    print(f"wrote screen_foot_v1_0_posY/negY.stl  体积 {f.volume():.1f} mm³")
    print(f"  bbox X {bb[0]:.2f}..{bb[3]:.2f}  Y {bb[1]:.2f}..{bb[4]:.2f}  Z {bb[2]:.2f}..{bb[5]:.2f} "
          f"(高 {Z1 - Z0:.2f}), 外形 R≤{CLIP_R}; 打印: Y{Y_IN:g} 面贴床, 印高 {bb[4] - bb[1]:.2f}")
    print(f"  底条 {2 * BAR_X:.2f}×{BAR_Y1 - Y_IN:.2f}×{BAR_T:g}; 梯形壁厚 {WALL_T:g} "
          f"(底 ±{BAR_X:.2f} → 顶 {LX0:.2f}..{LX1:.2f}); 顶托过孔 ({COL_X:.2f},±{COL_Y})")
    print(f"  环孔 (世界): {[(round(x, 2), round(y, 2)) for x, y in FOOT_HOLES_WORLD]}, 上方 Φ{WELL_D:g} 工艺井贯穿")
