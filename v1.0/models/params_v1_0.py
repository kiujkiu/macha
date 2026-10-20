"""
V1.0 屏幕组件 / 转子盘 共用参数 (2026-10-20)。世界坐标同 assembly_v1_0.py:
网格底板顶面 Z=0, Z 向上; 屏平面 = YZ 面 (LED 面朝 ±X), 偏心 SCR_ECC (面 B LED 面在 X=0)。

高度类数字来自 assembly_v1_0.py 的计算结果 (灯板下沿 = wifi 罩顶 + 3), 装配脚本里有 assert
核对 —— 改了 wifi/底板堆叠导致灯板高度变化, 这里要跟着改, 然后重跑各零件 build_stl.py。
"""
import struct
import numpy as np

# ---- 转子盘 / 底板 ----
DISC_TOP = 42.2                      # rim_ring 承载面
BASE_SPACER = 5.0                    # DR1M90 底板底面离承载面 (rim_ring_v1_0 一体垫柱; 2026-10-20 曾临时
                                     # 8.5, 盘扩 Φ180 + 外圈孔外推到 R82.5 后螺丝头出了板边, 回 5)
BASE_ROT = 90.0                      # DR1M90 板系 → 世界 绕 Z (FPC 对位自动挑出的)
# DR1M90 10-16 版 4 个 Φ4.2 板孔 (板系, 板中心原点; 板顶面焊贴片 M3 通孔铜柱, 高出板面 3.32)
BASE_HOLES_BOARD = [(-60.0, 30.0), (-60.0, -30.0), (60.0, -20.0), (60.0, 20.0)]

# ---- 灯板 ×2 背靠背 ----
LED_T = 1.84
BACK_GAP = 4.6                       # = 六角铜螺母对边
SCR_ECC = BACK_GAP / 2 + LED_T       # 4.14
LED_EDGE_BOT_Z = 101.21              # 灯板下沿 (assembly 算出; 10-20 wifi 托板改 25 尼龙柱 +0.82)
LED_EDGE_TOP_Z = 326.23              # 灯板上沿
LED_EDGE_HALF_W = 81.975             # 板宽半 (世界 |Y|)

# ---- 转子盘扩径 (2026-10-20 用户): Φ170 → Φ180, 外圈 8 孔 R77.5 → 82.5 (rim_ring_v1_0 + hub_disc_v1_0) ----
DISC_OD = 180.0
M3_HEAD_D, M3_HEAD_H = 7.0, 1.5      # 全部 M3 螺丝头 Φ7 × 厚 1.5 (用户 2026-10-20)
RING_OUTER_PCD_R = 82.5

# ---- 屏幕锁紧: 每侧 3 组 × 2 颗侧躺六角铜螺母 (上颗焊 A / 下颗焊 B), 每侧上下 2 根 M3 ----
NUT_AF, NUT_L = 4.6, 4.0             # M3 通孔六角铜螺母 对边 / 长
COL_X = SCR_ECC                      # 螺母列轴线 X (两板缝中心)
COL_Y = 77.0                         # 螺母列 |Y| = 灯板系 x=±77.0 (2026-10-20 用户选方案1: 原立式铜柱孔位
                                     # ±78.475 往里 1.475; 中组那排 (y-28.15) 往里再挪就压到电阻排/电容,
                                     # 预留的 Φ9 焊盘算可用也一样; 灯板 260921 Gerber 背面扫描)
GROUP_Y_BOARD = (79.35, -28.15, -135.65)   # 每组中心 (灯板系 y, LED 区中心原点)
LED_AREA_BOT_BOARD = -84.375
LED_EDGE_BOT_BOARD = -140.66


def group_z(y_board):
    """灯板系 y → 世界 Z (每组 = 两颗螺母交界面)。"""
    return LED_EDGE_BOT_Z + (y_board - LED_EDGE_BOT_BOARD)


GROUP_Z = [group_z(y) for y in GROUP_Y_BOARD]          # 上 / 中 / 下

# ---- 顶部: 顶盖 + M6 + Φ8 螺柱 进 688 轴承 (同 V0.4 思路) ----
POST_H = 360.0


def write_stl(man, path, header):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    t = np.asarray(m.tri_verts)
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri
    with open(path, "wb") as f:
        f.write(header.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        f.write(rec.tobytes())
    return v
