"""
top_cap_v1_0 —— V1.0 屏幕顶盖 (2026-10-20), 参考 V0.3.1 top_cap_v3_1_1 (扁条压屏顶 + 中心 M6 → Φ8 螺柱
进 frame_A/B 的 688 轴承):

  · 扁条压在两块灯板上沿, Y 盖过板宽, X 盖住两板 (0..8.28) 和中心 M6 头
  · 2× M3 上螺丝 (每侧一颗) 从顶面往下, 穿上组 (A+B) 两颗铜螺母 —— 锁两屏 + 把顶盖压在屏上
  · 中心 (0,0) M6 平头从底面 Φ13×2.7 头窝藏进 (⚠ 先装 M6 再压屏), 往上拧进 Φ8 螺柱
    (螺柱穿 688 轴承, 长度见装配报告)

  · 光电同步 (沿用 V0.3.1 top_cap_v3_1_1 / V0.4 那套, 2026-10-20 用户): 对射模块 (LM393, 槽宽 10) 平贴顶盖顶面,
    2×M3 从底面上穿 (底面 Φ7.5×2.5 头窝) + 排针尾避空槽 9×8 (穿透, 斜置)。两孔连线中点 M 落在屏顶 M3 连线
    X = COL_X 上 (Y -45), 模块绕 M 转 SEN_TH 使光轴 (平行孔线、偏 17) 过旋转中心; 静止挡光片 = vane_slider_v4
    (锁 frame_B 臂筋, 刀片下插槽内)。
零件系 = 世界系 (底面 = 灯板上沿 Z)。打印: 顶面朝下平放 (头窝朝上, 免支撑)。
输出: top_cap_v1_0.stl = 打印姿态 (绕 X 翻 180°, 顶面 Z0 贴床); top_cap_v1_0_asm.stl = 世界系 (装配用)。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import COL_X, COL_Y, LED_EDGE_HALF_W, LED_EDGE_TOP_Z, write_stl  # noqa: E402

CAP_T = 7.0
X_LO, X_HI = -8.0, COL_X + 12.0      # 盖住 M6 头 Φ13 (中心 X0) 与两板 (X 0..8.28)
Y_HALF = LED_EDGE_HALF_W + 2.0
M6_HEAD_D, M6_HEAD_H, M6_D = 13.0, 2.7, 6.4
M3_D = 3.4
Z0 = LED_EDGE_TOP_Z

# ---- 光电模块定位 (同 top_cap_v3_1_1 的通用解) ----
SEN_BEAM_OFF, SEN_PITCH = 17.0, 14.0           # 光轴到孔线垂距 / 两孔中心距 (模块几何)
SEN_M = (COL_X, -45.0)                         # 孔线中点: 屏顶 M3 连线 X=COL_X 上
_d = math.hypot(*SEN_M)
SEN_TH = math.degrees(math.asin(SEN_BEAM_OFF / _d))
_ua = math.radians(math.degrees(math.atan2(SEN_M[1], SEN_M[0])) + SEN_TH)
_u = (math.cos(_ua), math.sin(_ua))
SEN_HOLES = [(SEN_M[0] + s * SEN_PITCH / 2 * _u[0], SEN_M[1] + s * SEN_PITCH / 2 * _u[1]) for s in (1, -1)]
assert abs(abs(SEN_M[0] * _u[1] - SEN_M[1] * _u[0]) - SEN_BEAM_OFF) < 1e-9, "光轴未过圆心"
SEN_VANE_R = math.sqrt(_d ** 2 - SEN_BEAM_OFF ** 2)   # 光轴穿槽中心的半径
SEN_CB_D, SEN_CB_T = 7.5, 2.5
SEN_SLOT_L, SEN_SLOT_W = 9.0, 8.0


def build():
    c = m3d.Manifold.cube((X_HI - X_LO, 2 * Y_HALF, CAP_T)).translate((X_LO, -Y_HALF, Z0))
    for sy in (1, -1):
        c -= m3d.Manifold.cylinder(CAP_T + 2, M3_D / 2, M3_D / 2, 32).translate((COL_X, sy * COL_Y, Z0 - 1))
    c -= m3d.Manifold.cylinder(CAP_T + 2, M6_D / 2, M6_D / 2, 48).translate((0, 0, Z0 - 1))
    c -= m3d.Manifold.cylinder(M6_HEAD_H + 1, M6_HEAD_D / 2, M6_HEAD_D / 2, 64).translate((0, 0, Z0 - 1))
    c -= m3d.Manifold.cube((SEN_SLOT_L, SEN_SLOT_W, CAP_T + 2)).translate((-SEN_SLOT_L / 2, -SEN_SLOT_W / 2, 0)) \
        .rotate((0, 0, math.degrees(_ua))).translate((SEN_M[0], SEN_M[1], Z0 - 1))      # 排针尾避空槽
    for sx, sy in SEN_HOLES:
        c -= m3d.Manifold.cylinder(CAP_T + 2, 1.6, 1.6, 32).translate((sx, sy, Z0 - 1))
        c -= m3d.Manifold.cylinder(SEN_CB_T + 1, SEN_CB_D / 2, SEN_CB_D / 2, 48).translate((sx, sy, Z0 - 1))
    return c


if __name__ == "__main__":
    c = build()
    out = Path(__file__).with_name("top_cap_v1_0.stl")
    write_stl(c, Path(__file__).with_name("top_cap_v1_0_asm.stl"), "POV3D top_cap_v1_0 (asm)")
    cp = c.rotate((180, 0, 0))
    b = cp.bounding_box()
    write_stl(cp.translate((-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2])), out, "POV3D top_cap_v1_0 (print pose)")
    print(f"wrote {out}  体积 {c.volume():.1f} mm³  {X_HI - X_LO:.2f}×{2 * Y_HALF:.2f}×{CAP_T:g}  "
          f"Z {Z0:.2f}..{Z0 + CAP_T:.2f}")
    print(f"  光电: M {SEN_M}, 转 {SEN_TH:.3f}°, 孔 {[(round(x, 2), round(y, 2)) for x, y in SEN_HOLES]}, "
          f"光轴穿槽中心 r {SEN_VANE_R:.2f}")
    for sx, sy in SEN_HOLES:
        assert X_LO + SEN_CB_D / 2 < sx < X_HI - SEN_CB_D / 2, "光电孔头窝出顶盖"
