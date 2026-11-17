"""转子盘B 方案示意 (11-17 晚, 开工前给用户看): 左 = 径向半剖叠层, 右 = 俯视孔位 (整机世界坐标)。非精确模型。"""
import math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon
FONT = "/mnt/c/Windows/Fonts/simhei.ttf"; font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False

import numpy as np
def _board(R=6.0, x0=-51.2, x1=51.2, y0=8.6, y1=60.5, n=12):
    pts = []
    for cx, cy, a0 in ((x1 - R, y0 + R, -90), (x1 - R, y1 - R, 0), (x0 + R, y1 - R, 90), (x0 + R, y0 + R, 180)):
        pts += [(cx + R * math.cos(math.radians(a0 + 90 * k / n)), cy + R * math.sin(math.radians(a0 + 90 * k / n))) for k in range(n + 1)]
    return pts
BOARD = _board()
BB = [(-46.75, 13.05), (46.75, 13.05), (-46.75, 56.05), (46.75, 56.05)]   # r4j 对称 (待 96)
C = dict(motor='#555555', fr4='#C9B458', rim='#7FB069', coil='#D9822B', holder='#E6B422', shroud='#6FA8DC', screw='#B03A2E', nut='#8E44AD')
# ---- Z 叠层 (世界, 电机顶 Z21.5) ----
ZM = 21.5; T_FR4 = 3.0; CB = 1.5; CAV = 2.8; TRAY = 5.0; HOLD = 5.0
Z_F1 = ZM + T_FR4; Z_T0 = Z_F1 + CAV; Z_TOP = Z_T0 + TRAY; Z_H1 = Z_TOP + HOLD
R_IN, R_OUT, R_MOT = 34.0, 77.5, 8.0

fig = plt.figure(figsize=(19, 10.5))
ax = fig.add_axes([0.03, 0.08, 0.47, 0.82]); bx = fig.add_axes([0.53, 0.05, 0.45, 0.88])

# ===== 左: 径向半剖 (r 0→90) =====
def rect(r0, r1, z0, z1, c, **kw): ax.add_patch(Rectangle((r0, z0), r1 - r0, z1 - z0, fc=c, ec='k', lw=0.8, **kw))
rect(0, 27.5, ZM - 8, ZM, C['motor'])                                     # 电机 Φ55
ax.text(13, ZM - 4, '电机 Φ55', color='w', ha='center', va='center', fontsize=11)
rect(0, 82.5, ZM, Z_F1, C['fr4'])                                          # 玻纤板 Φ165×3
# 承载盘: 中心实体 r≤40, 外环 r72.5–85 下到玻纤板, 托盘 r40–72.5 Z_T0–Z_TOP, 外唇 r82.5–85
ax.add_patch(Polygon([(0, Z_F1), (40, Z_F1), (40, Z_T0), (72.5, Z_T0), (72.5, Z_F1), (82.5, Z_F1), (82.5, ZM), (85, ZM), (85, Z_TOP), (0, Z_TOP)],
                     closed=True, fc=C['rim'], ec='k', lw=0.8))
rect(40.3, 72.2, Z_F1, Z_F1 + 2.7, C['coil'])                             # 线圈 2.7 厚
ax.text(56, Z_F1 + 1.35, '转子线圈 ID80 × 厚2.7 (腔深 2.8)', ha='center', va='center', fontsize=10)
# 电机螺丝 (R8, 从上往下, 顶面 Φ7×4 沉孔)
rect(R_MOT - 3.5, R_MOT + 3.5, Z_TOP - 4, Z_TOP, 'w'); rect(R_MOT - 1.5, R_MOT + 1.5, ZM - 4, Z_TOP - 4, C['screw'], alpha=0.9)
rect(R_MOT - 2.75, R_MOT + 2.75, Z_TOP - 4, Z_TOP - 2.2, C['screw'])
ax.annotate('电机 4×M3 从上往下\n(顶面 Φ7×4 沉孔, M3×12)', (R_MOT, Z_TOP), (3, Z_H1 + 9), fontsize=10, arrowprops=dict(arrowstyle='->'))
# 中心窝
rect(0, 2.6, ZM, Z_F1 + 0.5, 'w'); ax.text(1.5, ZM - 1.2, 'Φ5.2', fontsize=8, ha='center')
# 内圈 R34: 从下往上 → 承载盘顶面铜螺母
def bolt(r, z_head0, z_tip, nut_z0=None, nut_z1=None, flange=False):
    rect(r - 3.6, r + 3.6, ZM, ZM + CB, 'w')                               # 玻纤板底面沉孔 Φ7.2×1.5
    rect(r - 2.75, r + 2.75, ZM, ZM + 1.4, C['screw'])                      # 头
    rect(r - 1.5, r + 1.5, ZM + 1.4, z_tip, C['screw'], alpha=0.9)
    if nut_z0 is not None:
        rect(r - (3.8 if flange else 2.1), r + (3.8 if flange else 2.1), nut_z0, nut_z1, C['nut'])
bolt(R_IN, ZM, Z_TOP - 0.3, Z_TOP - 4.0, Z_TOP)
ax.annotate('内圈 8×M3 @R34 从下往上\n→ 承载盘顶面铜螺母 Φ4.2×4', (R_IN, Z_TOP - 2), (24, Z_H1 + 4), fontsize=10, arrowprops=dict(arrowstyle='->'))
# 外圈 R77.5: 屏幕固定件处 (穿固定件, 法兰螺母)
rect(75.5, 81.5, Z_TOP, Z_H1, C['holder'])
ax.text(78.5, Z_H1 + 0.6, '屏幕固定件 (厚 5)', ha='center', fontsize=10)
bolt(R_OUT, ZM, Z_H1 + 4.2, Z_H1, Z_H1 + 3.7, flange=True)
ax.annotate('外圈 4 颗: 从下往上穿 玻纤板+承载盘+固定件\n→ 固定件顶面法兰螺母 (凸出 3.7)\n外圈另 4 颗: 同内圈, 进承载盘铜螺母', (R_OUT + 3.8, Z_H1 + 2), (45, Z_H1 + 16), fontsize=10, arrowprops=dict(arrowstyle='->'))
# 罩壁
rect(82, 85, Z_TOP, Z_TOP + 16, C['shroud'], alpha=0.85); ax.text(83.5, Z_TOP + 17, '罩壁\nr82–85', ha='center', fontsize=10)
# 尺寸
def zdim(x, z0, z1, t):
    ax.annotate('', (x, z0), (x, z1), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(x + 0.6, (z0 + z1) / 2, t, va='center', fontsize=9)
zdim(88, ZM, Z_F1, f'玻纤 {T_FR4:g}'); zdim(88, Z_F1, Z_T0, f'腔 {CAV:g}'); zdim(88, Z_T0, Z_TOP, f'托盘 {TRAY:g}'); zdim(88, Z_TOP, Z_H1, f'固定件 {HOLD:g}')
zdim(-4, ZM, ZM + CB, f'沉孔 {CB:g}')
for z, t in ((ZM, f'Z{ZM:g} 电机顶'), (Z_TOP, f'Z{Z_TOP:g} 承载盘顶'), (Z_H1, f'Z{Z_H1:g}')):
    ax.axhline(z, color='0.6', lw=0.5, ls=':'); ax.text(-13, z, t, fontsize=9, va='center')
ax.axvline(0, color='k', lw=0.6, ls='-.'); ax.text(0.5, Z_H1 + 22, '转轴', fontsize=9)
ax.set_xlim(-14, 98); ax.set_ylim(ZM - 9, Z_H1 + 25); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('径向半剖 (示意, 竖向放大看叠层)', fontsize=13)

# ===== 右: 俯视 (世界坐标; 屏幕沿 x, 偏心 y-4.36) =====
pol = lambda r, a: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))  # noqa: E731
bx.add_patch(Circle((0, 0), 85, fc='#E8F0E0', ec='k', lw=1))                       # 承载盘 Φ170
bx.add_patch(Circle((0, 0), 82.5, fc='none', ec=C['fr4'], lw=2, ls='--'))         # 玻纤板 Φ165
bx.add_patch(Wedge((0, 0), 72.5, 0, 360, width=32.5, fc=C['coil'], alpha=0.18, ec='none'))
bx.add_patch(Circle((0, 0), 27.5, fc='none', ec=C['motor'], lw=1.2, ls=':')); bx.text(0, -24, '电机 Φ55', ha='center', fontsize=9, color=C['motor'])
H_R0, H_R1, H_SPAN = 75.5, 81.5, 72.5                                              # 屏幕固定件弧形带 r75.5-81.5, 中心 ±72.5°
_bpts = np.array(BOARD + [(x + 3 * math.cos(t), y + 3 * math.sin(t)) for x, y in BB for t in np.linspace(0, 2 * math.pi, 24)])
_ang = np.degrees(np.arctan2(_bpts[:, 1], _bpts[:, 0])); _r = np.hypot(_bpts[:, 0], _bpts[:, 1])
_hit = _ang[_r > H_R0 - 0.5]
NOTCH = (round(float(_hit[_hit > 0][_hit[_hit > 0] < 90].min()) - 2, 1), round(float(_hit[_hit > 0][_hit[_hit > 0] < 90].max()) + 2, 1)) if len(_hit) else None
print('底板压到带子的角度 (+x 件, 已加 2° 余量):', NOTCH, ' 镜像:', (round(180 - NOTCH[1], 1), round(180 - NOTCH[0], 1)) if NOTCH else None)
for c0 in (0, 180):
    bx.add_patch(Wedge((0, 0), H_R1, c0 - H_SPAN, c0 + H_SPAN, width=H_R1 - H_R0, fc=C['holder'], ec='k', lw=0.8, alpha=0.9))
    if NOTCH:
        for sgn in (1, -1):
            a0, a1 = sorted((c0 + sgn * NOTCH[0], c0 + sgn * NOTCH[1]))
            bx.add_patch(Wedge((0, 0), H_R1, a0, a1, width=H_R1 - H_R0, fc='w', ec='k', lw=0.6, hatch='///'))
    for a in (c0 - 67.5, c0 + 67.5):
        x, y = pol(77.5, a); bx.add_patch(Circle((x, y), 5.0, fc=C['holder'], ec='k', lw=0.8))
bx.add_patch(Rectangle((-80, -4.36 - 2.5), 160, 5, fc='#C0392B', alpha=0.8)); bx.text(-40, -4.36 + 4, '屏幕 (沿 x, 偏心 y-4.36)', fontsize=10, color='#C0392B')
bx.plot([-88, 88], [-4.36, -4.36], color=C['shroud'], lw=1.5, ls='--'); bx.text(60, -12, '罩子分缝 (2 片: +y / -y)', fontsize=10, color=C['shroud'])
for a in range(8):                                                                  # 内圈 R34
    x, y = pol(R_IN, 22.5 + 45 * a); bx.add_patch(Circle((x, y), 1.6, fc=C['nut'], ec='k'))
for a in (22.5, 157.5, 202.5, 337.5):                                              # 外圈进承载盘铜螺母
    x, y = pol(R_OUT, a); bx.add_patch(Circle((x, y), 1.6, fc=C['nut'], ec='k'))
for a in (67.5, 112.5, 247.5, 292.5):                                              # 外圈穿固定件
    x, y = pol(R_OUT, a); bx.add_patch(Circle((x, y), 2.4, fc=C['screw'], ec='k'))
for a in (40, 140, 220, 320):                                                       # 罩子热熔螺母 (固定件上)
    x, y = pol(79, a); bx.add_patch(Rectangle((x - 2.1, y - 2.1), 4.2, 4.2, fc=C['shroud'], ec='k'))
for a in range(4):
    x, y = pol(R_MOT, 45 + 90 * a); bx.add_patch(Circle((x, y), 1.6, fc='w', ec='k', lw=1.2))
bx.add_patch(Circle((0, 0), 2.6, fc='w', ec='k'))
MOD = [(11.0, -76.5), (-11.0, -76.5), (0.0, -31.0)]; AC = [(21.0, -70.0), (21.0, -49.0)]
bx.add_patch(Polygon(BOARD, fc='#2E7D32', ec='#2E7D32', lw=1, alpha=0.12)); bx.text(-30, 50, '底板 r4j (对称, 待 96)', fontsize=10, color='#2E7D32')
for (x, y) in BB: bx.add_patch(Circle((x, y), 1.7, fc='#2E7D32', ec='k'))
for (x, y) in MOD: bx.add_patch(Circle((x, y), 1.7, fc='#1F618D', ec='k'))
for (x, y) in AC: bx.add_patch(Circle((x, y), 1.5, fc='#F39C12', ec='k'))
bx.text(-8, -82, '无线托盘 3 孔', fontsize=9, color='#1F618D'); bx.text(24, -60, 'AC 引线 2', fontsize=9, color='#F39C12')
leg = [('紫 ● 内圈 R34 ×8 + 外圈 22.5/157.5/202.5/337.5: 从下往上 → 承载盘铜螺母', C['nut']),
       ('红 ● 外圈 67.5/112.5/247.5/292.5: 从下往上穿固定件 → 法兰螺母', C['screw']),
       ('蓝 ■ 罩子锁点 r79 @40/140/220/320: 固定件顶面热熔螺母', C['shroud']),
       ('白 ○ 电机 4 孔 R8@45° (从上往下) + 中心 Φ5.2', 'k'),
       ('黄带 = 屏幕固定件 ×2 (同件, ±x 两端, 弧 r75.5-81.5 + 锚点 Φ10 凸台; 斜线 = 底板角处减薄到 ≤2 让底板)', '#B7950B'),
       ('橙环 = 线圈腔 r40–72.5 (承载盘底面)   黄虚线 = 玻纤板 Φ165', C['coil']),
       ('绿 = V1.2 底板 4 孔 / 深蓝 = 托盘 3 孔 / 橙 = AC 2 孔 (替换 V0.4 pi2hub/wifi 孔)', '#2E7D32')]
for i, (t, c) in enumerate(leg): bx.text(-95, -96 - 6.2 * i, t, fontsize=10, color=c)
bx.set_xlim(-97, 97); bx.set_ylim(-142, 92); bx.set_aspect('equal'); bx.axis('off')
bx.set_title('俯视 (整机世界坐标, 示意)', fontsize=13)
fig.suptitle('转子盘B 方案示意: 玻纤板 3 mm + 承载盘单件 (并入毂盘) + 屏幕固定件 ×2 + 罩子 2 片   (11-17, 开工前确认用)', fontsize=15)
out = __file__.replace('.py', '.png'); fig.savefig(out, dpi=110); print(out)
