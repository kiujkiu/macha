"""转子盘B 开工前 4 个问题的图解 (11-17 晚)。示意, 数字按方案。"""
import math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon, FancyBboxPatch
FONT = "/mnt/c/Windows/Fonts/simhei.ttf"; font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name(); plt.rcParams["axes.unicode_minus"] = False
COL = dict(fr4='#C9B458', rim='#7FB069', holder='#E6B422', screen='#C0392B', board='#2E7D32', coil='#D9822B', screw='#8B2E24', shroud='#6FA8DC', bad='#FF0000', ok='#1E8449')
fig = plt.figure(figsize=(20, 22)); gs = fig.add_gridspec(3, 2, left=0.03, right=0.98, top=0.95, bottom=0.02, wspace=0.06, hspace=0.12, height_ratios=[1, 1.15, 0.9])
A1 = fig.add_subplot(gs[0, :]); A2 = fig.add_subplot(gs[1, 0]); A2b = fig.add_subplot(gs[1, 1]); A3 = fig.add_subplot(gs[2, 0]); A4 = fig.add_subplot(gs[2, 1])
def R(ax, x0, y0, x1, y1, c, txt=None, fs=11, tc='k', **kw):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=c, ec='k', lw=0.9, **kw))
    if txt: ax.text((x0 + x1) / 2, (y0 + y1) / 2, txt, ha='center', va='center', fontsize=fs, color=tc)
def box(ax, x, y, t, c='k', fs=12, fc='#FFFFFF'):
    ax.text(x, y, t, fontsize=fs, color=c, va='top', bbox=dict(boxstyle='round,pad=0.4', fc=fc, ec=c, lw=1))
def bad(ax, x, y, t): ax.text(x, y, '× ' + t, color=COL['bad'], fontsize=13, ha='center')
RT = 32.3                                                                                   # 承载盘顶

# ===== 问题 1: 屏幕下沿 vs 固定件 (侧视, 看屏幕一端) =====
ax = A1; ax.set_title('问题 1: 屏幕两端正好压在屏幕固定件上 (侧视, 看 +x 端)', fontsize=16, loc='left')
for ox, title in ((0, '现在 (会撞)'), (40, '方案 a: 屏幕整体抬高 2'), (80, '方案 b: 固定件开槽, 屏幕角嵌进去')):
    ax.text(ox + 15, RT + 40, title, ha='center', fontsize=14)
    R(ax, ox, RT - 5, ox + 32, RT, COL['rim'], '承载盘', fs=10)
    up = 2 if ox == 40 else 0
    if ox == 80:
        ax.add_patch(Polygon([(ox + 18, RT), (ox + 30, RT), (ox + 30, RT + 5), (ox + 26, RT + 5), (ox + 26, RT + 1.5), (ox + 22, RT + 1.5), (ox + 22, RT + 5), (ox + 18, RT + 5)], fc=COL['holder'], ec='k'))
        ax.annotate('槽: 深 3.5, 宽 = 屏幕厚 + 余量', (ox + 24, RT + 2), (ox + 34, RT + 12), fontsize=10, arrowprops=dict(arrowstyle='->'))
        R(ax, ox + 22.6, RT + 1.5, ox + 25.4, RT + 28, COL['screen'], None)
        ax.text(ox + 15, RT + 18, '屏幕下角\n坐进槽里\n(高度不变)', fontsize=10, ha='center', color=COL['screen'])
        ax.text(ox + 15, RT + 3, '固定件', fontsize=10, ha='center')
    else:
        R(ax, ox + 18, RT, ox + 30, RT + 5, COL['holder'], '固定件\n厚 5', fs=9)
        R(ax, ox + 22.6, RT + 5 + up, ox + 25.4, RT + 28, COL['screen'], None)
        ax.text(ox + 12, RT + 18, '屏幕 (灯板)', fontsize=10, ha='center', color=COL['screen'])
    ax.plot([ox - 1, ox + 33], [RT + 5, RT + 5], ls=':', c='0.4', lw=0.8)
    if ox == 0:
        ax.text(ox + 15, RT + 33, '× 屏幕下沿 = 固定件顶\n= 盘顶+5, 0 间隙, 一装就顶', ha='center', fontsize=12, color=COL['bad'])
    if ox == 40:
        ax.text(ox + 15, RT + 33, '可以, 但 LED / 罩顶 / 玻璃\n整机上面全部跟着抬 2', ha='center', fontsize=12, color='#B9770E')
    if ox == 80:
        ax.text(ox + 15, RT + 33, '√ 推荐: 屏幕和上面都不动,\n槽顺便把屏幕下角夹住 (代替横条)', ha='center', fontsize=12, color=COL['ok'])
ax.text(-1, RT + 5, '盘顶+5', fontsize=9, ha='right', va='center')
ax.set_xlim(-6, 122); ax.set_ylim(RT - 6, RT + 44); ax.set_aspect('equal'); ax.axis('off')

# ===== 问题 2: 底板上角压在固定件弧形带上 =====
ax = A2; ax.set_title('问题 2: 底板两个上角伸到固定件弧形带上方 (俯视放大, +x+y 那一角)', fontsize=16, loc='left')
# 俯视放大 (+x+y 象限), 坐标 = 世界
ax.add_patch(Wedge((0, 0), 85, 20, 80, fc='#E8F0E0', ec='k', lw=0.8))
ax.add_patch(Wedge((0, 0), 81.5, 20, 80, width=6, fc=COL['holder'], ec='k', lw=0.8))
ax.add_patch(Wedge((0, 0), 81.5, 45.2, 55.2, width=6, fc='w', ec=COL['bad'], lw=1.5, hatch='///'))
bd = [(51.2 - 6 + 6 * math.cos(math.radians(a)), 60.5 - 6 + 6 * math.sin(math.radians(a))) for a in range(0, 91, 10)]
ax.add_patch(Polygon([(10, 8.6), (51.2, 8.6)] + bd + [(10, 60.5)], fc=COL['board'], alpha=0.35, ec=COL['board'], lw=1.5))
ax.add_patch(Circle((46.75, 56.05), 3, fc='#AED6B5', ec='k')); ax.add_patch(Circle((46.75, 56.05), 1.6, fc='w', ec='k'))
ax.text(28, 40, '底板 r4j\n(+x 上角)', fontsize=12, color=COL['board'], ha='center')
ax.text(60, 72, '固定件弧形带\nr75.5–81.5', fontsize=10, ha='center', rotation=-40)
ax.annotate('底板角 + 垫柱 Φ6 伸到 r76.8,\n超过带子内边 r75.5\n→ 斜线段 45°–55° 底板压在带子上', (49, 58), (5, 78), fontsize=11, color=COL['bad'], arrowprops=dict(arrowstyle='->', color=COL['bad']))
x, y = 79 * math.cos(math.radians(40)), 79 * math.sin(math.radians(40)); ax.add_patch(Rectangle((x - 2.1, y - 2.1), 4.2, 4.2, fc=COL['shroud'], ec='k'))
ax.annotate('罩子锁点 40°\n(问题 3)', (x + 2, y), (72, 40), fontsize=10, color='#2471A3', arrowprops=dict(arrowstyle='->', color='#2471A3'))
ax.set_xlim(0, 92); ax.set_ylim(0, 92); ax.set_aspect('equal'); ax.axis('off')
# 问题 2 侧视 (单独一格, 放大)
ax = A2b; ax.set_title('问题 2 侧视: 底板角下面只有 3 mm 空, 固定件却有 5 mm 高', fontsize=16, loc='left')
for oy, ok in ((26, False), (0, True)):
    R(ax, 0, oy, 60, oy + 5, COL['rim'], '承载盘', fs=11)
    R(ax, 8, oy + 5, 11, oy + 8, '#AED6B5'); ax.annotate('垫柱 3', (9.5, oy + 6.5), (1, oy + 13), fontsize=10, arrowprops=dict(arrowstyle='->'))
    R(ax, 0, oy + 8, 46, oy + 9.6, COL['board']); ax.annotate('底板 (厚 1.6, 板底 = 盘顶 + 3)', (20, oy + 9.6), (14, oy + 13), fontsize=10, color=COL['board'], arrowprops=dict(arrowstyle='->', color=COL['board']))
    if not ok:
        R(ax, 36, oy + 5, 60, oy + 10, COL['holder'], None); ax.text(54, oy + 7.5, '固定件 厚 5', fontsize=10, ha='center')
        ax.add_patch(Rectangle((36, oy + 8), 10, 2, fc=COL['bad'], alpha=0.6, ec=COL['bad']))
        ax.text(30, oy + 18, '× 不改: 红色那块重叠 (固定件顶穿底板)', fontsize=13, color=COL['bad'])
    else:
        R(ax, 36, oy + 5, 60, oy + 7, COL['holder'], None); ax.text(53, oy + 6, '减薄到 2', fontsize=10, ha='center')
        R(ax, 36, oy + 7, 60, oy + 10, COL['holder'], None, alpha=0.2, ls='--')
        ax.text(30, oy + 18, '√ 改法: 底板角下方那 10° 一段带子减薄到 2,\n   从板子底下钻过去 (留 1 间隙), 带子不断开;\n   离开底板角的地方照样厚 5', fontsize=12, color=COL['ok'], va='center')
ax.set_xlim(-2, 92); ax.set_ylim(-3, 52); ax.set_aspect('equal'); ax.axis('off')


# ===== 问题 3: 罩子锁点离减薄区很近 =====
ax = A3; ax.set_title('问题 3: 罩子锁点 (40°) 离减薄区只剩约 3.6 mm (俯视, 把带子拉直看)', fontsize=16, loc='left')
L = lambda a: 79 * math.radians(a)                                                         # r79 上的弧长
R(ax, L(22), 0, L(62), 6, COL['holder']); R(ax, L(45.2), 0, L(55.2), 6, 'w', None, hatch='///')
ax.text(L(50.2), 7.5, '减薄区 45.2°–55.2°\n(让底板角)', ha='center', fontsize=11, color=COL['bad'])
ax.add_patch(Circle((L(40), 3), 2.1, fc=COL['shroud'], ec='k')); ax.add_patch(Circle((L(40), 3), 3.6, fc='none', ec='#2471A3', ls='--'))
ax.text(L(40), -3.5, '罩子热熔螺母 40°\nΦ4.2 (外围壁 ≈ Φ7.2)', ha='center', fontsize=11, color='#2471A3', va='top')
ax.add_patch(Circle((L(22.5), 3), 1.6, fc='#8E44AD', ec='k')); ax.text(L(22.5), -3.5, '外圈孔 22.5°\n(进承载盘铜螺母)', ha='center', fontsize=10, va='top')
ax.annotate('', (L(40) + 3.6, 6.8), (L(45.2), 6.8), arrowprops=dict(arrowstyle='<->')); ax.text((L(40) + 3.6 + L(45.2)) / 2, 9.5, '≈ 3.6', ha='center', fontsize=12)
ax.text(L(19), 18, '放得下, 只是比较紧。开工时量模型, 不够就把锁点从 40° 挪到 38°\n(罩子孔同步挪)。这一条不用你现在定。', fontsize=13)
ax.set_xlim(L(18), L(66)); ax.set_ylim(-14, 24); ax.set_aspect('equal'); ax.axis('off')

# ===== 问题 4: 底板螺丝头伸进线圈腔 =====
ax = A4; ax.set_title('问题 4: 底板 4 颗螺丝头在线圈腔正上方 (剖面)', fontsize=16, loc='left')
for ox, ok in ((0, False), (60, True)):
    R(ax, ox, 0, ox + 50, 3, COL['fr4'], '玻纤板 3', fs=9)
    R(ax, ox, 5.8, ox + 50, 10.8, COL['rim'], None); ax.text(ox + 40, 8.3, '承载盘托盘 5', fontsize=9, ha='center')
    R(ax, ox + 2, 3, ox + 48, 5.7, COL['coil'], None); ax.text(ox + 40, 4.35, '线圈 2.7', fontsize=9, ha='center', va='center')
    R(ax, ox + 23.5, 10.8, ox + 26.5, 14.6, '#AED6B5'); R(ax, ox + 15, 14.6, ox + 35, 16.2, COL['board'], '底板', fs=8, tc='w')
    if ok:
        R(ax, ox + 21.5, 5.8, ox + 28.5, 7.3, 'w'); R(ax, ox + 21.5, 5.8, ox + 28.5, 7.3, COL['screw'], alpha=0.85)
        R(ax, ox + 23.5, 7.3, ox + 26.5, 16.5, COL['screw'], alpha=0.85)
        ax.text(ox + 25, 20, '√ 承载盘底面沉孔 Φ7.4×1.5:\n薄头 (Φ7×1.5) 整个埋进托盘,\n头底跟盘底齐平, 不碰线圈', ha='center', fontsize=11, color=COL['ok'])
    else:
        R(ax, ox + 21.5, 4.3, ox + 28.5, 5.8, COL['screw'], alpha=0.85); R(ax, ox + 23.5, 5.8, ox + 26.5, 16.5, COL['screw'], alpha=0.85)
        ax.add_patch(Rectangle((ox + 20.5, 3.6), 9, 2.4, fc='none', ec=COL['bad'], lw=2, ls='--'))
        bad(ax, ox + 25, 20, '螺丝头凸在盘底下 1.5,\n线圈上面只剩 0.1 空 → 压线圈')
    ax.text(ox + 25, -2.5, '现在 V1.2 做法' if not ok else '改法', ha='center', fontsize=12, va='top')
ax.text(0, 31, '底板孔离转轴 r48–73, 正好在线圈腔 (r40–72.5) 上方;\n螺丝从承载盘底往上拧, 头就在腔里, 而腔只比线圈高 0.1。', fontsize=12)
ax.set_xlim(-3, 113); ax.set_ylim(-7, 38); ax.set_aspect('equal'); ax.axis('off')
fig.suptitle('转子盘B 开工前要定的 4 个问题 (红 × = 不改会出事, 绿 √ = 我的建议; 只有问题 1 要你选)', fontsize=19)
out = __file__.replace('.py', '.png'); fig.savefig(out, dpi=100); print(out)
