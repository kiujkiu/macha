# -*- coding: utf-8 -*-
"""按键板板框 (V1.2, 用户 11-13): 2 按键 + 1 三色 LED + 3 单色 LED, 40 x 20 板, 竖放在 +Y 下罩墙里, 正面朝外。
固定 (11-13 更新): 板左右 2×M3 安装孔 Φ3.2 @ (3.5, 10) / (36.5, 10); U 形支架 (scripts/key_bracket_v1_2.py) 两根立柱压在板**正面**孔位上,
  M3×8 超薄头从立柱前面 (外侧) 往里穿立柱 3 + 板 1.6, **背面上 M3 法兰螺母** (Φ7.6×3.7) ⇒ 背面每孔 Φ8 禁布; 正面立柱压板处禁布。
  板下沿坐支架底条 (Z3); 支架脚 2×M3 从底盘下往上拧支架脚里的铜螺母。下罩从上罩下来, 只露按键 / LED 孔。
输出 models/key_board_v1_2/key_board_outline_v1_2.dxf (板框 + 安装孔 + 禁布 + 推荐元件位, 给画 PCB 用) + _layout.png
坐标: 板正视 (从外面看), 原点 = 板左下角, X 向右 (= 整机 -X, 整机 x = 20 − X), Y 向上 (= 整机 Z = 3 + Y)。
本文件只在 __main__ 出图; 常数给 key_bracket_v1_2.py import。"""
import math
from pathlib import Path

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_board_v1_2'

W, H, T = 40.0, 20.0, 1.6          # 板框 / 板厚
EDGE_KO = 1.0                      # 四边禁布 (11-13: 去掉插槽禁布, 只留 1)
BACK_MAX = 6.0                     # 背面元件最高 (含插座)
MH = [(3.5, 10.0), (36.5, 10.0)]   # M3 安装孔 Φ3.2 (用户 11-13)
MH_D = 3.2
BACK_KO_D = 8.0                    # 背面法兰螺母 Φ7.6 禁布 Φ8
# 正面立柱压板区 (支架立柱 整机 |x| 13..21, Z0..17.5 ⇒ 板系 X −1..7 / 33..41, Y ≤ 14.5); 板内部分禁布
PIL_X_IN = 7.0                     # 立柱内侧离板边 (= 13 → X 7 / 33)
PIL_Y1 = 14.5                      # 立柱顶 (整机 Z17.5)
BTN = [(11.0, 14.5), (11.0, 5.5)]  # 6x6 轻触开关 中心 (左边上下两个); X11: 本体 8..14 离立柱 1, 杆槽离外皮 ≥1.5
BTN_BODY, BTN_BODY_H, BTN_H, BTN_STEM_D = 6.0, 3.5, 7.0, 3.5   # 6×6×7: 本体高 3.5, 杆 Φ3.5 顶离板面 7
RGB = (17.0, 10.0)                 # 三色 LED 5mm 中心 (右边 4 灯一排, 左一是三色)
RGB_D, RGB_H = 5.0, 7.0            # 高 ≤7 (短体/草帽 5mm; 标准 8.6 顶会进外皮剩 <1.5)
LED = [(22.0, 10.0), (26.5, 10.0), (31.0, 10.0)]   # 3mm 单色 LED 中心 (节距 4.5; 右一离右立柱 0.5)
LED_D, LED_H = 3.0, 5.3

# 整机里的位置 (key_bracket_v1_2 按这个做)
Y_BOARD_FRONT = 100.6              # 板正面 y (用户 11-13)
Y_BOARD_BACK = Y_BOARD_FRONT - T   # 99.0
Y_BACK_MAX = Y_BOARD_BACK - BACK_MAX   # 93.0
Z0 = 3.0                           # 板下沿离底盘顶 (支架底条)


def to_global(X, Y):
    """板系 (X, Y) → 整机 (x, Z)"""
    return 20.0 - X, Z0 + Y


def main():
    import ezdxf
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    from matplotlib import font_manager as fm
    OUT.mkdir(parents=True, exist_ok=True)
    # 正面立柱禁布 (板内部分) + 四边禁布
    KO_F = [(0, 0, PIL_X_IN, PIL_Y1), (W - PIL_X_IN, 0, PIL_X_IN, PIL_Y1)]
    KO_E = [(0, 0, W, EDGE_KO), (0, H - EDGE_KO, W, EDGE_KO), (0, 0, EDGE_KO, H), (W - EDGE_KO, 0, EDGE_KO, H)]
    # 自检: 元件本体离禁布 ≥0.5
    def rect_gap(a, b):
        return max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
    comps = [(x - BTN_BODY / 2, y - BTN_BODY / 2, BTN_BODY, BTN_BODY) for x, y in BTN] + \
            [(RGB[0] - RGB_D / 2, RGB[1] - RGB_D / 2, RGB_D, RGB_D)] + [(x - LED_D / 2, y - LED_D / 2, LED_D, LED_D) for x, y in LED]
    gaps = [rect_gap(c, k) for c in comps for k in KO_F]
    assert min(gaps) >= 0.5 - 1e-9, gaps
    assert all(c[0] >= EDGE_KO and c[1] >= EDGE_KO and c[0] + c[2] <= W - EDGE_KO and c[1] + c[3] <= H - EDGE_KO for c in comps)
    assert all(rect_gap(a, b) >= 0.5 - 1e-9 for i, a in enumerate(comps) for b in comps[i + 1:])

    doc = ezdxf.new('R2000'); msp = doc.modelspace()
    for n, c in (('Edge_Cuts', 7), ('KeepOut_F', 1), ('KeepOut_B', 6), ('Holes', 4), ('Comp', 3), ('Text', 5)): doc.layers.add(n, color=c)
    msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'Edge_Cuts'})
    for x, y in MH:
        msp.add_circle((x, y), MH_D / 2, dxfattribs={'layer': 'Holes'})
        msp.add_circle((x, y), BACK_KO_D / 2, dxfattribs={'layer': 'KeepOut_B'})
    for x, y, w, h in KO_F + KO_E:
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={'layer': 'KeepOut_F'})
    for x, y in BTN:
        msp.add_lwpolyline([(x - 3, y - 3), (x + 3, y - 3), (x + 3, y + 3), (x - 3, y + 3)], close=True, dxfattribs={'layer': 'Comp'})
        msp.add_circle((x, y), BTN_STEM_D / 2, dxfattribs={'layer': 'Comp'})
    msp.add_circle(RGB, RGB_D / 2, dxfattribs={'layer': 'Comp'})
    for p in LED: msp.add_circle(p, LED_D / 2, dxfattribs={'layer': 'Comp'})
    doc.saveas(OUT / 'key_board_outline_v1_2.dxf')

    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=110)
    ax.add_patch(Rectangle((0, 0), W, H, fc='#2E7D32', alpha=.25, ec='k', lw=2))
    for x, y, w, h in KO_E:
        ax.add_patch(Rectangle((x, y), w, h, fc='red', alpha=.15, ec='none'))
    for x, y, w, h in KO_F:
        ax.add_patch(Rectangle((x, y), w, h, fc='red', alpha=.18, ec='r', ls='--'))
    for x, y in MH:
        ax.add_patch(Circle((x, y), BACK_KO_D / 2, fc='none', ec='m', ls=':', lw=1.5))
        ax.add_patch(Circle((x, y), MH_D / 2, fc='white', ec='k'))
        ax.text(x, y - 5.2, f'M3 Φ{MH_D:g}\n({x:g}, {y:g})', ha='center', va='top', fontsize=7)
    for i, (x, y) in enumerate(BTN, 1):
        ax.add_patch(Rectangle((x - 3, y - 3), 6, 6, fc='#ddd', ec='k')); ax.add_patch(Circle((x, y), BTN_STEM_D / 2, fc='#555'))
        ax.text(x + 3.4, y + (1.6 if i == 1 else -1.6), f'按键{i} 6×6×7 ({x:g}, {y:g})', ha='left', va='center', fontsize=7)
    ax.add_patch(Circle(RGB, RGB_D / 2, fc='white', ec='m', lw=2)); ax.text(RGB[0], RGB[1] + 3, f'三色 Φ5 ({RGB[0]:g}, {RGB[1]:g})', ha='center', fontsize=7)
    for x, y in LED: ax.add_patch(Circle((x, y), LED_D / 2, fc='#ffd966', ec='k'))
    ax.text(26.5, 7.6, '单色 Φ3 ×3\n(22 / 26.5 / 31, 10)', ha='center', va='top', fontsize=7)
    ax.text(3.5, 15.5, '正面立柱\n压板区', ha='center', fontsize=6.5, color='r'); ax.text(W - 3.5, 15.5, '正面立柱\n压板区', ha='center', fontsize=6.5, color='r')
    ax.annotate('', (0, -2), (W, -2), arrowprops=dict(arrowstyle='<->')); ax.text(W / 2, -3.4, f'{W:g}', ha='center')
    ax.annotate('', (-2, 0), (-2, H), arrowprops=dict(arrowstyle='<->')); ax.text(-3.4, H / 2, f'{H:g}', va='center', rotation=90)
    ax.set_title(f'按键板板框 {W:g}×{H:g}×{T:g} (正视 = 从机器外面看; 红 = 正面禁布, 紫虚圈 = 背面 Φ{BACK_KO_D:g} 螺母禁布)', fontsize=11)
    note = (f'固定: 2×M3×8 超薄头从支架立柱前面往里穿 立柱 3 + 板 {T:g}, 背面 M3 法兰螺母 Φ7.6×3.7 (背面孔周 Φ{BACK_KO_D:g} 禁布);\n'
            f'  正面立柱压板区 X 0..{PIL_X_IN:g} / {W - PIL_X_IN:g}..{W:g}, Y 0..{PIL_Y1:g} 不放件; 四边禁布 {EDGE_KO:g}\n'
            f'正面: 只放按键 / LED; 按键 6×6×7 (杆 Φ3.5 顶离板面 7), 三色 LED 高 ≤{RGB_H:g} (短体), Φ3 LED 高 ≤{LED_H:g}\n'
            f'背面元件高 ≤ {BACK_MAX:g} (含插座, 建议 PH2.0 卧式, 出线朝下)\n'
            f'整机位置: 板中心 x=0 (+Y 侧), 正面 y{Y_BOARD_FRONT:g} / 背面 y{Y_BOARD_BACK:g}, 下沿 Z{Z0:g}–上沿 Z{Z0 + H:g}; 整机 x = 20 − X, Z = {Z0:g} + Y')
    ax.text(-3, -6.0, note, fontsize=7.5, va='top')
    ax.set_xlim(-6, W + 4); ax.set_ylim(-17, H + 4); ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(); plt.savefig(OUT / 'key_board_outline_v1_2_layout.png')
    print(f'板 {W}x{H}x{T}; 孔 {MH}; 按键 {BTN}; RGB {RGB}; LED {LED}; 正面 y{Y_BOARD_FRONT} 背面 {Y_BOARD_BACK:.1f} 背元件到 {Y_BACK_MAX:.1f}')


if __name__ == '__main__':
    main()
