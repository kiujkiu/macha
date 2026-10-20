"""
wifi_plate_v1_0 —— V1.0 WiFi 托板 (2026-10-20 用户: 原占位托架改成一块板 + 4 个 M3 孔, 尼龙螺柱固定; H 形)

  · 板 3 厚, X ±PLATE_X, Y ±PLATE_Y, 平放在 FS03 (RJ45/USB 顶) 上方, WiFi 模块平躺在板上
  · 4×Φ3.4 = DR1M90 顶面 4 只贴片 M3 铜柱位 (板系 (-60,±30)/(60,±20) 转 BASE_ROT): M3 尼龙螺柱
    (M-F, 长 NYLON_L) 公头拧进铜柱, M3 螺丝从板顶拧进尼龙柱母头
  · H 形: 两端居中各开一个口 (X ±NOTCH_HX, 从板端到 |Y|=NOTCH_Y0)。+Y 口正对 FS03 的 J6 (立式 USB-A,
    世界 X -3..3 / Y 22..43): 扁平 USB 延长线 (AMRI 弯头公 → 插 J6 / AF 母 → 接 WiFi 插头) 从这里上下穿;
    -Y 口对称 (H 形, 不打印方向件)
  · 4×Φ3.4 = wifi_shell 两端沿孔 (世界 (±12.5, 37.3) / (±12.5, -49.3), 罩居中 + WIFI_DY -6):
    M3 从**托板底面往上**穿托板 + 罩沿, 螺母在罩沿顶面 (用户 2026-10-20: 托板与 wifi 盒用 M3 通孔锁一起;
    (+12.5,37.3) 那颗正在 RJ45 上方, 板底只余 1.82, 板底放不下螺母 2.4, 放得下 Φ7×1.5 薄头 ⇒ 4 颗统一从下往上)
    装法: 先把螺丝从下穿托板、扣罩、拧螺母 (托板 + 罩 + 模块成一组), 再整组拧到 4 根尼龙柱上
    H 口半宽 10 → 8, 让沿孔 Φ7 头/螺母边离口边 1
零件系: 世界 XY, 板底 Z0 (装配平移到托板高度)。打印: 平放。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import BASE_HOLES_BOARD, BASE_ROT, write_stl  # noqa: E402

PLATE_T = 3.0
PLATE_X, PLATE_Y = 35.0, 64.0
NOTCH_HX, NOTCH_Y0 = 8.0, 18.0
SHELL_HOLES = [(sx * 12.5, y) for y in (37.3, -49.3) for sx in (1, -1)]   # wifi_shell 沿孔 (世界)
HOLE_D = 3.4
NYLON_L = 25.0                       # 尼龙螺柱长 (铜柱顶 → 板底)


def holes_world():
    r = math.radians(BASE_ROT)
    c, s = math.cos(r), math.sin(r)
    return [(c * x - s * y, s * x + c * y) for x, y in BASE_HOLES_BOARD]


HOLES = holes_world()


def build():
    p = m3d.Manifold.cube((2 * PLATE_X, 2 * PLATE_Y, PLATE_T)).translate((-PLATE_X, -PLATE_Y, 0))
    for sy in (1, -1):
        y0, y1 = (NOTCH_Y0, PLATE_Y + 1) if sy > 0 else (-PLATE_Y - 1, -NOTCH_Y0)
        p -= m3d.Manifold.cube((2 * NOTCH_HX, y1 - y0, PLATE_T + 2)).translate((-NOTCH_HX, y0, -1))
    for x, y in HOLES + SHELL_HOLES:
        p -= m3d.Manifold.cylinder(PLATE_T + 2, HOLE_D / 2, HOLE_D / 2, 32).translate((x, y, -1))
    return p


if __name__ == "__main__":
    p = build()
    out = Path(__file__).with_name("wifi_plate_v1_0.stl")
    write_stl(p, out, "POV3D wifi_plate_v1_0")
    print(f"wrote {out}  {2 * PLATE_X:g}×{2 * PLATE_Y:g}×{PLATE_T:g} H 形 (口 {2 * NOTCH_HX:g} 宽, 深 {PLATE_Y - NOTCH_Y0:g})  "
          f"体积 {p.volume():.0f} mm³")
    print("  4 尼龙柱孔 (世界): " + ", ".join(f"({x:.1f},{y:.1f})" for x, y in HOLES))
    print("  4 罩沿孔 (世界): " + ", ".join(f"({x:.1f},{y:.1f})" for x, y in SHELL_HOLES))
    for x, y in SHELL_HOLES:
        assert abs(y) < NOTCH_Y0 - 3.5 or abs(x) - 3.5 >= NOTCH_HX + 1.0 - 1e-9, "罩沿孔螺丝头压到 H 口"
    for x, y in HOLES:
        assert abs(x) - HOLE_D / 2 - 2.75 > NOTCH_HX or abs(y) < NOTCH_Y0, "尼龙柱贴着 H 口"
