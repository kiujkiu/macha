# -*- coding: utf-8 -*-
"""按键板板框 (V1.2, 用户 11-13): 2 按键 + 1 三色 LED + 3 单色 LED, 40 x 20 板, 竖放在 +Y 下罩墙里, 正面朝外。
固定: 板子左右边插 U 形支架两根立柱的竖槽 (不打螺丝), 下罩罩下来压住上沿; 支架脚 2xM3 从底盘下往上锁铜螺母。
输出 models/key_board_v1_2/key_board_outline_v1_2.dxf (板框 + 禁布 + 推荐元件位, 给画 PCB 用) + _layout.png
坐标: 板正视 (从外面看), 原点 = 板左下角, X 向右 (= 整机 -X), Y 向上 (= 整机 +Z)。"""
import math
from pathlib import Path
import ezdxf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib import font_manager as fm

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_board_v1_2'; OUT.mkdir(parents=True, exist_ok=True)

W, H, T = 40.0, 20.0, 1.6          # 板框 / 板厚
SLOT_KO = 2.0                      # 左右边插槽禁布 (槽深 1.5 + 0.5)
BOT_KO = 1.5                       # 下沿禁布 (支架底托)
TOP_KO = 1.0                       # 上沿禁布 (下罩压条)
BACK_MAX = 6.0                     # 背面元件最高 (含插座)
BTN = [(7.5, 10.0), (32.5, 10.0)]  # 6x6 轻触开关 中心
RGB = (20.0, 14.0)                 # 三色 LED 5mm (或 5050 贴片) 中心
LED = [(14.0, 6.5), (20.0, 6.5), (26.0, 6.5)]   # 3mm 单色 LED 中心

# 整机里的位置 (供核对, 结构件后续按这个做)
SH_OUT, SPIG_IN = 110.0, 90.8
X_RAIL = W / 2 + 3.0               # 立柱外侧
Y_ARC_END = math.sqrt(SH_OUT ** 2 - X_RAIL ** 2)   # 立柱外侧处外圆 y
SKIN = 1.5                         # 前皮最薄处
Y_FRONT_COMP = Y_ARC_END - SKIN    # 元件最前 (按键帽 / LED 顶) 不超过这个
BTN_H = 7.0                        # 6x6x7 轻触 (从板面算); 杆伸进前皮孔
Y_BOARD_FRONT = round(Y_ARC_END - BTN_H, 1)   # 板正面 y (按键顶与前皮外面齐, 杆在孔里)
Y_BOARD_BACK = Y_BOARD_FRONT - T
Y_BACK_MAX = Y_BOARD_BACK - BACK_MAX
Z0 = 3.0                           # 板下沿离底盘顶 (支架底托)

doc = ezdxf.new('R2000'); msp = doc.modelspace()
for n, c in (('Edge_Cuts', 7), ('KeepOut', 1), ('Comp', 3), ('Text', 5)): doc.layers.add(n, color=c)
msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'Edge_Cuts'})
for r in ((0, 0, SLOT_KO, H), (W - SLOT_KO, 0, SLOT_KO, H), (0, 0, W, BOT_KO), (0, H - TOP_KO, W, TOP_KO)):
    x, y, w, h = r; msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={'layer': 'KeepOut'})
for x, y in BTN:
    msp.add_lwpolyline([(x - 3, y - 3), (x + 3, y - 3), (x + 3, y + 3), (x - 3, y + 3)], close=True, dxfattribs={'layer': 'Comp'})
    msp.add_circle((x, y), 1.75, dxfattribs={'layer': 'Comp'})
msp.add_circle(RGB, 2.5, dxfattribs={'layer': 'Comp'})
for p in LED: msp.add_circle(p, 1.5, dxfattribs={'layer': 'Comp'})
doc.saveas(OUT / 'key_board_outline_v1_2.dxf')

fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
fig, ax = plt.subplots(figsize=(11, 6.6), dpi=110)
ax.add_patch(Rectangle((0, 0), W, H, fc='#2E7D32', alpha=.25, ec='k', lw=2))
for x, y, w, h in ((0, 0, SLOT_KO, H), (W - SLOT_KO, 0, SLOT_KO, H), (0, 0, W, BOT_KO), (0, H - TOP_KO, W, TOP_KO)):
    ax.add_patch(Rectangle((x, y), w, h, fc='red', alpha=.18, ec='none'))
for i, (x, y) in enumerate(BTN, 1):
    ax.add_patch(Rectangle((x - 3, y - 3), 6, 6, fc='#ddd', ec='k')); ax.add_patch(Circle((x, y), 1.75, fc='#555'))
    ax.text(x, y - 4.6, f'按键{i} 6×6×7\n({x:g}, {y:g})', ha='center', va='top', fontsize=8)
ax.add_patch(Circle(RGB, 2.5, fc='white', ec='m', lw=2)); ax.text(RGB[0], RGB[1] + 3, f'三色 LED Φ5 ({RGB[0]:g}, {RGB[1]:g})', ha='center', fontsize=8)
for x, y in LED: ax.add_patch(Circle((x, y), 1.5, fc='#ffd966', ec='k'))
ax.text(20, 3.2, '单色 LED Φ3 ×3  (14 / 20 / 26, 6.5)', ha='center', fontsize=8)
ax.annotate('', (0, -2), (W, -2), arrowprops=dict(arrowstyle='<->')); ax.text(W / 2, -3.4, f'{W:g}', ha='center')
ax.annotate('', (-2, 0), (-2, H), arrowprops=dict(arrowstyle='<->')); ax.text(-3.4, H / 2, f'{H:g}', va='center', rotation=90)
ax.text(1, H / 2, f'插槽禁布 {SLOT_KO:g}', rotation=90, va='center', fontsize=7, color='r')
ax.text(W - 1, H / 2, f'插槽禁布 {SLOT_KO:g}', rotation=90, va='center', ha='center', fontsize=7, color='r')
ax.set_title(f'按键板板框 {W:g}×{H:g}×{T:g} (正视 = 从机器外面看; 红 = 禁布)', fontsize=12)
note = (f'正面: 只放按键 / LED (其余元件放背面); 背面元件高 ≤ {BACK_MAX:g} (含插座, 建议 PH2.0 卧式, 出线朝下)\n'
        f'不开安装孔: 左右边插支架竖槽 (槽宽 = 板厚 + 0.2), 下罩压住上沿; 支架脚 2×M3 从底盘下锁铜螺母\n'
        f'整机位置: 板中心 x=0 (+Y 侧), 板正面 y≈{Y_BOARD_FRONT:g}, 下沿 Z{Z0:g}–上沿 Z{Z0 + H:g}; 前皮最薄 {SKIN:g}, 按键杆 / LED 穿前皮孔')
ax.text(-3, -6.5, note, fontsize=8, va='top')
ax.set_xlim(-6, W + 4); ax.set_ylim(-14, H + 4); ax.set_aspect('equal'); ax.axis('off')
plt.tight_layout(); plt.savefig(OUT / 'key_board_outline_v1_2_layout.png')
print(f'板 {W}x{H}x{T}; 立柱外侧 x±{X_RAIL:g} 外圆 y {Y_ARC_END:.2f}; 板正面 y {Y_BOARD_FRONT} 背面 {Y_BOARD_BACK:.1f} 背元件到 {Y_BACK_MAX:.1f} (下罩内墙 r{SPIG_IN})')
