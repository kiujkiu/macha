"""
V0.4 带屏动平衡 —— 罩顶安装孔圈 ↔ 移动配重块 共用参数 (2026-11-09)。

rotor_shroud_v4 (罩顶铜螺母孔圈) 与 balance_block_v4 (扇形配重块) 都 import 本文件,
保证孔位一一对得上。坐标 = 罩零件系 (= 屏局部系): 0° = +X, 逆时针 (俯视);
装配角 = 零件角 + V3_SCR_ROT (−45°)。Z0 = 承载面 (装配 42.2), 罩顶面 Z50 (装配 92.2)。

可放位置由罩顶面上方的障碍决定 (scratchpad feas.py 扫过):
  · 双面屏 (居中 X−6.7..6.7 / 偏心 0..13.4 都要躲) |Y|≤75, +1 余量
  · −X 配重臂 counterweight_arm (X−85..−44, |Y|≤26), +1 余量
  块半角 21° 时可放中心 = 0/15/30/45/315/330/345 (+X 侧连续 90°) + 120 + 240;
  再加配重臂 (180°), 相邻两位置的夹角都 < 180° ⇒ 任意方向都能矢量合成。
"""
import math

V3_SCR_ROT = -45.0                       # 装配角 = 零件角 + 此值

# ---- 移动配重块 ----
BLK_R_IN, BLK_R_OUT = 54.0, 85.0         # 外缘 = 罩 OD 170 (不超旋转包络)
BLK_HALF = 21.0                          # 半角
BLK_T = 4.8                              # 厚 (同 V1.0 配重块)

# 锁紧: 2×M3 @ r67, 块中心 ±7.5° (= 相邻两个安装孔, 节距 15°)
LOCK_R = 67.0
LOCK_HALF = 7.5

# 块中心可放角 (零件系)。安装孔 = 每个中心 ±7.5°, 去重。
BLK_CENTERS = (0, 15, 30, 45, 315, 330, 345, 120, 240)
MOUNT_ANGS = tuple(sorted({(c + s * LOCK_HALF) % 360 for c in BLK_CENTERS for s in (-1, 1)}))


def pol(r, a_deg):
    a = math.radians(a_deg)
    return r * math.cos(a), r * math.sin(a)


MOUNT_PTS = [pol(LOCK_R, a) for a in MOUNT_ANGS]
