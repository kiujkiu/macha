"""
rim_ring_v1_0 —— V1.0 转子承载盘 (2026-10-20), 由 models/rim_ring (V0.4 现行) 改孔:

  扩径 (2026-10-20 用户, 配 hub_disc_v1_0): 托盘 OD170→180, 外唇 ID165/OD170→175/180,
        外圈 8 环孔 R77.5→82.5
  保留: 托盘 ID50 ×5, 内凸台环 OD80/ID70×2.5,
        走线挖槽 (-45..-40°, R40..61, 唇侧 2 深), 16 环孔 Φ3.2 (R30/R82.5 @22.5+45k),
        2 个 Φ4 通孔, R30 @202.5/247.5° 承载面 Φ7.5×2 头沉孔
  取消: 7 个 pi2hub 孔 + 4 个 wifi_shell 沿孔 (V1.0 没有 pi2hub, wifi 挪到 FS03 上方托架)
  新增:
    · DR1M90 底板 4 孔 —— 同旧 pi2hub 孔型 (用户 2026-10-20: 和之前一样留沉孔和通孔):
      Φ3.2 通孔 + Φ4.2×4.5 铜螺母沉孔从唇侧往上 (承载面留 0.5); M3 尼龙垫柱 5 高拧进铜螺母撑底板
  屏幕底座不加孔: 借外圈 R77.5 现成环孔锁进 hub_disc 铜螺母 (2026-10-20 用户)

零件系 = V0.4 rim_ring 零件系: 托盘底 Z0 (= 装配承载面, 装配时绕 X 翻转: 世界 (x,y) = 零件 (x,-y)),
唇/凸台朝 +Z。打印: 托盘面 (Z0) 朝下平放 (同 V0.4)。
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import BASE_HOLES_BOARD, BASE_ROT, DISC_OD, RING_OUTER_PCD_R, write_stl  # noqa: E402

# ---- 沿用 V0.4 rim_ring ----
BASE_ID, BASE_OD, BASE_H = 50.0, DISC_OD, 5.0
RIM_ID, RIM_OD, RIM_H = DISC_OD - 5.0, DISC_OD, 5.5
IBOSS_OD, IBOSS_ID, IBOSS_H = 80.0, 70.0, 2.5
NOTCH_R_MIN, NOTCH_R_MAX, NOTCH_A_S, NOTCH_A_E, NOTCH_DEPTH = 40.0, 61.0, -45.0, -40.0, 2.0
M3_D = 3.2
RING_HOLES = [(r * math.cos(math.radians(22.5 + 45 * k)), r * math.sin(math.radians(22.5 + 45 * k)))
              for r in (30.0, RING_OUTER_PCD_R) for k in range(8)]
EXTRA_HOLE_D = 4.0
EXTRA_HOLES = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a, R in ((-10.0, 72.0), (-42.5, 56.0))]
HEAD_CB_D, HEAD_CB_DEEP = 7.5, 2.0
HEAD_CB_XY = [(30.0 * math.cos(math.radians(a)), 30.0 * math.sin(math.radians(a))) for a in (202.5, 247.5)]

# ---- V1.0 新增 ----
INSERT_D, INSERT_DEEP = 4.2, 4.5     # 铜螺母沉孔 (全项目统一 Φ4.2, 同旧 pi2hub 孔)


def _base_holes_world():
    r = math.radians(BASE_ROT)
    c, s = math.cos(r), math.sin(r)
    return [(c * x - s * y, s * x + c * y) for x, y in BASE_HOLES_BOARD]


BASE_HOLES_WORLD = _base_holes_world()
BASE_HOLES = [(x, -y) for x, y in BASE_HOLES_WORLD]       # 零件系


def annulus(z0, h, r_in, r_out, seg=240):
    return (m3d.Manifold.cylinder(h, r_out, r_out, seg) - m3d.Manifold.cylinder(h + 2, r_in, r_in, seg)
            .translate((0, 0, -1))).translate((0, 0, z0))


def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg).translate((x, y, z0))


def wedge(a0, a1, r, h, z0, n=24):
    pts = [(0.0, 0.0)] + [(r * math.cos(math.radians(a0 + i * (a1 - a0) / n)),
                           r * math.sin(math.radians(a0 + i * (a1 - a0) / n))) for i in range(n + 1)]
    return m3d.CrossSection([pts]).extrude(h).translate((0, 0, z0))


def build():
    part = annulus(0, BASE_H, BASE_ID / 2, BASE_OD / 2)
    nz0 = BASE_H - NOTCH_DEPTH
    part -= wedge(NOTCH_A_S, NOTCH_A_E, BASE_OD / 2 + 2, NOTCH_DEPTH + 0.4, nz0 - 0.2) \
        ^ annulus(nz0 - 0.2, NOTCH_DEPTH + 0.4, NOTCH_R_MIN, NOTCH_R_MAX)
    part += annulus(BASE_H, RIM_H, RIM_ID / 2, RIM_OD / 2) + annulus(BASE_H, IBOSS_H, IBOSS_ID / 2, IBOSS_OD / 2)
    for x, y in RING_HOLES:
        part -= cyl(M3_D, x, y, -1, BASE_H + RIM_H + 1, 32)
    for x, y in EXTRA_HOLES:
        part -= cyl(EXTRA_HOLE_D, x, y, -1, BASE_H + RIM_H + 1, 32)
    for x, y in HEAD_CB_XY:
        part -= cyl(HEAD_CB_D, x, y, -1, HEAD_CB_DEEP)
    for x, y in BASE_HOLES:
        part -= cyl(M3_D, x, y, -1, BASE_H + 1)
        part -= cyl(INSERT_D, x, y, BASE_H - INSERT_DEEP, BASE_H + 1)
    return part


if __name__ == "__main__":
    part = build()
    out = Path(__file__).with_name("rim_ring_v1_0.stl")
    v = write_stl(part, out, "POV3D rim_ring_v1_0")
    print(f"wrote {out}  bbox Z {v[:, 2].min():.2f}..{v[:, 2].max():.2f}  体积 {part.volume():.1f} mm³  "
          f"genus {part.genus()}")
    for nm, pts in (("DR1M90 底板孔 (通孔+铜螺母沉孔)", BASE_HOLES_WORLD),):
        print(f"  {nm} (世界): " + ", ".join(f"({x:.2f},{y:.2f}) r{math.hypot(x, y):.2f}" for x, y in pts))
    # 新孔与保留孔/槽的最小间距 (孔边到孔边)
    keep = [(p, M3_D) for p in RING_HOLES] + [(p, EXTRA_HOLE_D) for p in EXTRA_HOLES] + [(p, HEAD_CB_D) for p in HEAD_CB_XY]
    new = [(p, INSERT_D) for p in BASE_HOLES]
    gap = min(math.dist(a, b) - (da + db) / 2 for a, da in new for b, db in keep)
    print(f"  新孔/垫柱 与保留孔 最小边距 {gap:.2f}")
    assert gap > 1.0
