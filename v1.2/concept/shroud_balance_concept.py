# -*- coding: utf-8 -*-
"""11-16 方案示意 (只画图, 不建模): 转子罩 (两半, 内侧切向螺丝合拢) + 罩内配重唇 + 顶部配重梳齿 + 8 孔四四分 + 天线内收
    ../../.venv/bin/python shroud_balance_concept.py  → shroud_balance_concept.png"""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Wedge, Rectangle, Polygon, FancyArrowPatch
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf')
plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False

# ---- 数 (与 build_v1_2 / led_support_v1_2 一致) ----
RIM_R, ST_IN = 85.0, 90.8                   # 承载盘外缘 / 不转下罩内壁 (到 Z73.08)
SR0, SR1 = 86.0, 89.0                       # 转子罩壁 (建议)
HOLE_R = 82.5
SUP_A = [22.5, 157.5, 202.5, 337.5]         # 给灯板支撑
SHR_A = [67.5, 112.5, 247.5, 292.5]         # 给罩子
HALF_W, GAP, PCB_T = 81.879, 2.3, 1.468
ANT_X0, ANT_X1, ANT_Y = 82.4, 84.2, 9.0     # 天线板 (建议: 减薄 + 两端都竖贴)
LIP_R0, LIP_R1 = 80.0, SR0                  # 配重唇
LIP_A = [a for a in range(30, 151, 15)] + [a for a in range(210, 331, 15)]
Z_RIM, Z_SCR0, Z_LED0, Z_VIEW0, Z_SCR1 = 32.0, 45.2, 83.08, 73.08, 253.2
Z_SH1 = 81.0
C_SUP, C_SHR, C_A, C_B = '#E67E22', '#1F77B4', '#AED6F1', '#A9DFBF'

def pt(r, a): return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))

fig = plt.figure(figsize=(22, 15))
fig.suptitle('V1.2 转子罩 + 配平 方案示意 (11-16, 只是示意图, 未建模)', fontsize=18, y=0.985)

# ================= (a) 俯视 Z≈50 =================
ax = fig.add_axes([0.02, 0.36, 0.46, 0.58]); ax.set_aspect('equal')
ax.set_title('① 俯视 (Z≈50 剖, 看罩子 / 8 孔 / 支撑脚 / 天线)', fontsize=13)
ax.add_patch(Circle((0, 0), ST_IN, fill=False, ls='--', color='gray', lw=1.2))
ax.text(0, -ST_IN - 3.5, '不转的玻璃下罩内壁 r90.8', ha='center', color='gray', fontsize=9)
ax.add_patch(Circle((0, 0), RIM_R, color='#EEEEEE', zorder=0))
ax.text(-45, -60, '转子盘 (承载盘) r85', color='#777', fontsize=10)
# 罩两半: A = +x 半 (-90..90), B = -x 半
ax.add_patch(Wedge((0, 0), SR1, -90, 90, width=SR1 - SR0, color=C_A, ec='k', lw=0.8))
ax.add_patch(Wedge((0, 0), SR1, 90, 270, width=SR1 - SR0, color=C_B, ec='k', lw=0.8))
ax.text(92, 30, '罩 A 半\n(+x 侧)', fontsize=11, color='#1F618D')
ax.text(-110, 30, '罩 B 半\n(-x 侧)', fontsize=11, color='#1E8449')
# 配重唇 (Z66–70, 画淡)
for a0, a1 in ((30 - 7, 150 + 7), (210 - 7, 330 + 7)):
    ax.add_patch(Wedge((0, 0), LIP_R1, a0, a1, width=LIP_R1 - LIP_R0, color='#F9E79F', alpha=0.6, zorder=1))
for a in LIP_A:
    ax.add_patch(Circle(pt(83, a), 1.6, fill=False, color='#B7950B', lw=1, zorder=3))
ax.text(-30, 66, '配重唇 (Z66–70, 内壁一圈)\nM3 孔每 15°, 避开灯板两端', fontsize=9, color='#7D6608', ha='center')
# 分缝 + 内侧凸耳 (±y)
for sy in (1, -1):
    for sx, c in ((1, C_A), (-1, C_B)):
        x0 = 0 if sx > 0 else -7
        ax.add_patch(Rectangle((x0, sy * 79 if sy > 0 else -86), 7, 7, color=c, ec='k', lw=0.8, zorder=4))
    ax.plot([-9, 9], [sy * 82.5] * 2, color='k', lw=2.2, zorder=5)
    ax.plot([0, 0], [sy * 78, sy * 90], color='r', lw=1, ls=':', zorder=6)
ax.annotate('分缝 (0,+y): 内侧两个凸耳\n切向 M3 螺丝 + 螺母锁合\n外面平整无孔', xy=(0, 82.5), xytext=(20, 100),
            fontsize=10, arrowprops=dict(arrowstyle='->', color='r'), color='r')
ax.annotate('分缝 (0,-y) 同样', xy=(0, -82.5), xytext=(20, -102), fontsize=10, arrowprops=dict(arrowstyle='->', color='r'), color='r')
# 罩子用的 4 孔 + 罩底凸台
for a in SHR_A:
    x, y = pt(HOLE_R, a)
    c = C_A if math.cos(math.radians(a)) > 0 else C_B
    ax.add_patch(Wedge((0, 0), SR0 + 0.01, a - 6, a + 6, width=SR0 - 78.5, color=c, ec='k', lw=0.6, zorder=4))
    ax.add_patch(Circle((x, y), 1.6, color=C_SHR, zorder=6))
    ax.text(*pt(70, a), f'罩 {a:g}°', ha='center', va='center', fontsize=9, color=C_SHR)
# 灯板
for s in (1, -1):
    y0 = s * GAP if s > 0 else -GAP - PCB_T
    ax.add_patch(Rectangle((-HALF_W, y0), 2 * HALF_W, PCB_T, color='#2E7D32', zorder=5))
ax.text(0, 7, '两块灯板 (背靠背, 端角 r81.9)', ha='center', fontsize=10, color='#2E7D32')
# 支撑脚 (T 形, 外缘裁到 r85) + 4 孔
for sx in (1, -1):
    poly = []
    # 脚: x 71..(r85 弧), |y|≤35 ; 用弧裁
    xs0 = 71.0
    ys = [i * 0.5 for i in range(-70, 71)]
    pts_out = [(min(math.sqrt(max(RIM_R**2 - y * y, 0)), 84.5), y) for y in ys]
    poly = [(xs0, -35)] + pts_out + [(xs0, 35)]
    poly = [(sx * x, y) for x, y in poly]
    ax.add_patch(Polygon(poly, closed=True, color=C_SUP, alpha=0.45, ec=C_SUP, zorder=3))
    ax.add_patch(Rectangle((75.6 if sx > 0 else -81.6, -2.2), 6, 4.4, color=C_SUP, zorder=6))   # 立刀
    # 天线板
    ax.add_patch(Rectangle((ANT_X0 if sx > 0 else -ANT_X1, -ANT_Y), ANT_X1 - ANT_X0, 2 * ANT_Y, color='#8E44AD', zorder=6))
for a in SUP_A:
    ax.add_patch(Circle(pt(HOLE_R, a), 1.6, color=C_SUP, zorder=7, ec='k', lw=0.5))
    ax.text(*pt(HOLE_R - 10, a), f'撑 {a:g}°', ha='center', va='center', fontsize=9, color='#A04000')
ax.annotate('灯板支撑脚改 T 形\n(跨到 ±22.5° 孔, 外缘裁到 r85)\n原 (±78,±7.6) 4 孔作废', xy=(78, 25), xytext=(100, 62),
            fontsize=10, color='#A04000', arrowprops=dict(arrowstyle='->', color='#A04000'))
ax.annotate('天线板: 板端外就是 x81.9, 没法整体往里挪\n→ 板减薄 2.5→1.8 + 两端都竖贴 (|y|≤9)\n转动最远 r87.3 → r84.7', xy=(84.2, -9), xytext=(92, -62),
            fontsize=10, color='#6C3483', arrowprops=dict(arrowstyle='->', color='#6C3483'))
ax.add_patch(Circle(pt(76, 112), 1.6, color='#555', zorder=6))
ax.text(*pt(68, 118), '原配平孔\nr76 112°', fontsize=8, color='#555', ha='center')
ax.set_xlim(-125, 160); ax.set_ylim(-112, 115); ax.axhline(0, color='#ccc', lw=0.5); ax.axvline(0, color='#ccc', lw=0.5)
ax.set_xlabel('x (+x = CZ06 侧)'); ax.set_ylabel('y')
# 图例
for i, (c, t) in enumerate([(C_SUP, '橙 = 4 孔给灯板支撑 (22.5/157.5/202.5/337.5°)'), (C_SHR, '蓝 = 4 孔给罩子 (67.5/112.5/247.5/292.5°), 每半 2 颗'),
                            ('#F9E79F', '黄 = 罩内配重唇'), ('#8E44AD', '紫 = 天线板')]):
    ax.add_patch(Rectangle((-123, -98 + i * -0), 0, 0))
    ax.text(62, 108 - i * 6.5, '■ ', color=c, fontsize=12, va='center'); ax.text(68, 108 - i * 6.5, t, fontsize=9, va='center')

# ================= (b) 径向剖面 (下部) =================
bx = fig.add_axes([0.52, 0.52, 0.46, 0.42])
bx.set_title('② 下部径向剖面 (r–Z, 过罩子孔 67.5° 方向)', fontsize=13)
bx.add_patch(Rectangle((0, 23), RIM_R, 9, color='#DDDDDD')); bx.text(30, 26.5, '转子盘 Z23–32', fontsize=9)
bx.add_patch(Rectangle((ST_IN, 0), 110 - ST_IN, Z_VIEW0, color='#B0BEC5')); bx.text(93, 40, '不转\n玻璃下罩\n(到 Z73.08)', fontsize=9)
bx.add_patch(Rectangle((95, 53.08), 5, 50, color='#D6EAF8', ec='#5DADE2')); bx.text(96, 92, '玻璃罩', fontsize=9, rotation=90)
bx.add_patch(Rectangle((SR0, Z_RIM), SR1 - SR0, Z_SH1 - Z_RIM, color=C_A, ec='k')); bx.text(SR0 - 0.2, 82.5, '转子罩壁 r86–89\nZ32→81 (开口)', fontsize=9, ha='right')
bx.add_patch(Rectangle((78.5, Z_RIM), SR0 - 78.5, 4, color=C_A, ec='k')); bx.text(60, 33, '罩底凸台 (只在 4 孔处)', fontsize=8.5)
bx.plot([HOLE_R, HOLE_R], [14, 38.5], color=C_SHR, lw=2.5); bx.add_patch(Rectangle((HOLE_R - 2.75, 36), 5.5, 3, color=C_SHR))
bx.text(70, 15, 'M3 从上往下拧\n→ 毂盘铜螺母', fontsize=8.5, color=C_SHR)
bx.add_patch(Rectangle((LIP_R0, 66), LIP_R1 - LIP_R0, 4, color='#F9E79F', ec='#B7950B'))
bx.plot([83, 83], [63, 74], color='#555', lw=2); bx.add_patch(Rectangle((80.5, 70), 5, 2.5, color='#555'))
bx.text(66, 68, '配重唇 Z66–70\nM3 + 垫片 (头顶 ≤ Z78)', fontsize=8.5, ha='right', color='#7D6608')
bx.add_patch(Rectangle((0, Z_SCR0), HALF_W, Z_LED0 - Z_SCR0, color='#A5D6A7')); bx.add_patch(Rectangle((0, Z_LED0), HALF_W, 20, color='#2E7D32'))
bx.text(20, 60, '灯板下部 (无灯: 桥板/FPC/天线)', fontsize=9); bx.text(20, 92, '灯区 (LED 下沿 Z83.08)', fontsize=9, color='w')
bx.add_patch(Rectangle((ANT_X0, 32), ANT_X1 - ANT_X0, 40, color='#8E44AD')); bx.text(ANT_X0 - 0.3, 50, '天线 (实际在 0°/180°, 投影画进来)', fontsize=8, ha='right', color='#6C3483', rotation=90)
bx.axhline(Z_VIEW0, color='r', ls=':', lw=1); bx.text(56, Z_VIEW0 + 0.8, '可视下边界 Z73.08', color='r', fontsize=8.5)
bx.axhline(Z_LED0, color='g', ls=':', lw=1)
bx.annotate('', xy=(SR1, 60), xytext=(ST_IN, 60), arrowprops=dict(arrowstyle='<->', color='k')); bx.text(SR1, 62, '1.8', fontsize=8.5)
bx.set_xlim(55, 110); bx.set_ylim(10, 105); bx.set_xlabel('r (mm)'); bx.set_ylabel('Z (mm)'); bx.grid(alpha=0.3)

# ================= (c) 顶部梳齿 俯视 =================
cx = fig.add_axes([0.02, 0.03, 0.30, 0.30]); cx.set_aspect('equal')
cx.set_title('③ 顶部配平梳齿 俯视 (Z≈257–263, 在灯板顶边之上)', fontsize=12)
cx.add_patch(Circle((0, 0), 85, fill=False, ls='--', color='gray')); cx.text(0, -92, '转动外圆 ≤ r85', ha='center', fontsize=8.5, color='gray')
cx.add_patch(Rectangle((-HALF_W, -3.8), 2 * HALF_W, 7.6, color='#2E7D32', alpha=0.35)); cx.text(-80, -12, '下面是灯板 (竖)', fontsize=8.5, color='#2E7D32')
cx.add_patch(Rectangle((-72, -5), 144, 10, color='#B3B6B7', ec='k')); cx.text(0, 6.5, '横梁 (沿灯板, 压在顶堵头上)', ha='center', fontsize=8.5)
cx.add_patch(Circle((0, 0), 7, color='#7F8C8D')); cx.text(0, 0, 'Φ8轴', ha='center', va='center', fontsize=7, color='w')
for x in (-60, -40, -20, 20, 40, 60):
    L = min(40, math.sqrt(80**2 - x * x))
    for s in (1, -1):
        cx.plot([x, x], [s * 5, s * L], color='#34495E', lw=3)
        for k in (0.6, 0.85):
            cx.add_patch(Rectangle((x - 2.75, s * L * k - 1.2), 5.5, 2.4, color='#E67E22'))
cx.text(62, 45, '齿 = 横向金属柱\n(垂直灯板)\n橙 = 配重螺母/垫片', fontsize=8.5)
cx.set_xlim(-95, 110); cx.set_ylim(-98, 60); cx.axis('off')

# ================= (d) 整机侧视 =================
dx = fig.add_axes([0.35, 0.02, 0.21, 0.31])
dx.set_title('④ 整机侧视 (从 +y 看)', fontsize=12)
dx.add_patch(Rectangle((-85, 23), 170, 9, color='#DDDDDD'))
dx.add_patch(Rectangle((-HALF_W, Z_SCR0), 2 * HALF_W, Z_SCR1 - Z_SCR0, color='#A5D6A7'))
dx.add_patch(Rectangle((-78, Z_LED0), 156, 169, color='#2E7D32', alpha=0.8)); dx.text(0, 170, '显示区', color='w', ha='center', fontsize=11)
dx.add_patch(Rectangle((-SR1, Z_RIM), 2 * SR1, Z_SH1 - Z_RIM, color=C_A, alpha=0.85, ec='k')); dx.text(0, 55, '转子罩 (转)\n内含配重唇', ha='center', fontsize=9)
dx.add_patch(Rectangle((-110, 0), 110 - ST_IN, Z_VIEW0, color='#B0BEC5')); dx.add_patch(Rectangle((ST_IN, 0), 110 - ST_IN, Z_VIEW0, color='#B0BEC5'))
dx.add_patch(Rectangle((-72, 257), 144, 6, color='#B3B6B7', ec='k'))
for x in (-60, -40, -20, 20, 40, 60):
    dx.add_patch(Circle((x, 260), 2.2, color='#34495E'))
dx.text(0, 268, '配平梳齿 (齿朝纸面内外)', ha='center', fontsize=9)
dx.add_patch(Rectangle((-7, 253), 14, 33, color='#7F8C8D')); dx.add_patch(Rectangle((-4, 286), 8, 21, color='#555'))
dx.text(10, 296, '→ 688', fontsize=8.5)
dx.axhline(Z_VIEW0, color='r', ls=':', lw=1); dx.axhline(Z_SCR1, color='g', ls=':', lw=1)
dx.text(-108, Z_SCR1 + 2, '灯板顶 Z253', fontsize=8, color='g'); dx.text(-108, Z_VIEW0 + 2, 'Z73', fontsize=8, color='r')
dx.set_xlim(-112, 112); dx.set_ylim(0, 310); dx.set_aspect('equal'); dx.set_xticks([]); dx.set_ylabel('Z')

# ================= (e) 分缝凸耳 局部 =================
ex = fig.add_axes([0.59, 0.04, 0.39, 0.40]); ex.set_aspect('equal')
ex.set_title('⑤ 分缝局部 (俯视, 放大; +y 那条缝)', fontsize=12)
ths = [math.radians(a / 10) for a in range(700, 1101)]
def arc(r, a0, a1): return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / 60 for i in range(61)]]
ex.add_patch(Polygon(arc(SR0, 80, 90) + arc(SR1, 90, 80), color=C_A, ec='k'))
ex.add_patch(Polygon(arc(SR0, 90, 100) + arc(SR1, 100, 90), color=C_B, ec='k'))
ex.add_patch(Rectangle((0.15, 77.5), 8, 8.6, color=C_A, ec='k')); ex.add_patch(Rectangle((-8.15, 77.5), 8, 8.6, color=C_B, ec='k'))
ex.add_patch(Rectangle((-11.2, 79.75), 3, 5.5, color='#555'))           # 螺丝头
ex.add_patch(Rectangle((-8.2, 81.3), 16.5, 2.4, color='#888'))           # 螺杆
ex.add_patch(Polygon([(8.2, 79.8), (10.6, 79.8), (10.6, 85.2), (8.2, 85.2)], color='#555'))   # 螺母
ex.plot([0, 0], [76, 91], 'r:', lw=1)
ex.text(-14, 74.5, 'M3 头', fontsize=9); ex.text(9, 74.5, '螺母', fontsize=9)
ex.text(13, 88, '外面: 一整圈光滑, 只看到一条缝', fontsize=10, color='r')
ex.text(-30, 82, 'B 半凸耳', fontsize=9, color='#1E8449'); ex.text(15, 82, 'A 半凸耳', fontsize=9, color='#1F618D')
ex.text(-30, 70, '每条缝上下 2 颗 (约 Z45 / Z70), 从罩内侧拧;\n罩子开口朝上, 手/螺丝刀从上面伸进去', fontsize=9)
ex.set_xlim(-32, 42); ex.set_ylim(66, 93); ex.set_xlabel('x'); ex.set_ylabel('y')

fig.savefig(__file__.replace('.py', '.png'), dpi=110)
print('ok')
