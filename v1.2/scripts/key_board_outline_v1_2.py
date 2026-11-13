# -*- coding: utf-8 -*-
"""按键板板框 (V1.2, 用户 11-13): 2 按键 + 1 三色 LED + 3 单色 LED (全贴片), 40 x 22.5 板, 竖放在 +Y 下罩墙里, 正面朝外。
固定 (11-13 前面平板): 板左右 2×M3 安装孔 Φ3.2 @ (3.5, 10) / (36.5, 10); 支架 (scripts/key_bracket_v1_2.py) 前面是一整块平板 压住板**正面** (整板覆盖),
  M3×8 超薄头埋进平板前面沉孔往里穿平板 + 板 1.6, **背面上 M3 法兰螺母** (Φ7.6×3.7) ⇒ 背面每孔 Φ8 禁布; 正面孔周 Φ4.8 禁布 (平板压板环)。
  平板背面只在元件处开: 按键本体 + 脚让位腔, 每颗 LED 一个 Φ3.2 隔光通道 (导光柱从外皮外面插进来)。其余平板背面全贴板。
  板下沿坐支架底条 (Z3); 支架脚 2×M3 从底盘下往上, 法兰螺母坐脚顶。下罩从上罩下来; 按键 = 下罩外皮 H 形缝舌片 (外皮不开按键孔)。
11-13 (三) 用户新定元件: 按键 6×6×7.5 贴片 ZX-QC66-7.5TP ×2 @ (11, 18.5) / (11, 7.5) (11-13 (四) 间距 11, 板高 22.5); 三色 1615 (XL-1615RGBC) @ (17, 10); 单色 0603 ×3 @ (22 / 26.5 / 31, 10)。
输出 models/key_board_v1_2/key_board_outline_v1_2.dxf (板框 + 安装孔 + 禁布 + 推荐元件位 + 焊盘外包, 给画 PCB 用) + _layout.png
坐标: 板正视 (从外面看), 原点 = 板左下角, X 向右 (= 整机 -X, 整机 x = 20 − X), Y 向上 (= 整机 Z = 3 + Y)。
本文件只在 __main__ 出图; 常数给 key_bracket_v1_2.py import。"""
import math
from pathlib import Path

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_board_v1_2'

W, H, T = 40.0, 22.5, 1.6          # 板框 / 板厚 (11-13 (四): 按键拉开到间距 11, 板高 20 → 22.5, 下沿仍 Z3)
EDGE_KO = 1.0                      # 四边禁布
BACK_MAX = 6.0                     # 背面元件最高 (含插座)
MH = [(3.5, 10.0), (36.5, 10.0)]   # M3 安装孔 Φ3.2 (用户 11-13)
MH_D = 3.2
BACK_KO_D = 8.0                    # 背面法兰螺母 Φ7.6 禁布 Φ8
FRONT_KO_D = 4.8                   # 正面孔周禁布 (平板压板环; 按键焊盘外包离孔心只 2.75, 放不下 Φ8)
# 按键: 6×6×7.5 贴片轻触 ZX-QC66-7.5TP (用户 11-13 (三)); 脚沿板 X 方向伸出 (Y 向两键间距只有 7, 放不下 9.5)
BTN = [(11.0, 18.5), (11.0, 7.5)]  # 中心 (上 / 下); 11-13 (四) 间距 7 → 11 (= 整机 Z21.5 / Z10.5; 两舌片悬臂各 8.5, 弹性力 ≤4 N 定的上限 ≈11.3)
BTN_BODY, BTN_BODY_H, BTN_H, BTN_STEM_D = 6.0, 3.45, 7.5, 3.5   # 本体 6×6 高 3.45, 杆 Φ3.5, 板面到杆顶 7.5
BTN_TRAVEL = 0.2                   # 行程
BTN_LEG_W = 8.6                    # 脚外宽 (X)
BTN_PAD_OUT = (9.5, 5.6)           # 焊盘外包 (X, Y)
BTN_PAD_C = (6.5, 3.4)             # 焊盘中心距 (X, Y) ⇒ 每焊盘 3.0 × 2.2
BTN_PAD = (BTN_PAD_OUT[0] - BTN_PAD_C[0], BTN_PAD_OUT[1] - BTN_PAD_C[1])
BTN_LEG_H = 1.0                    # 脚 + 焊锡高度 (估, 平板背面脚让位按这个 +0.5)
RGB = (17.0, 10.0)                 # 三色 LED 1615 (XL-1615RGBC) 中心
RGB_W, RGB_L, RGB_H = 1.6, 1.5, 0.6     # X × Y × 高
LED = [(22.0, 10.0), (26.5, 10.0), (31.0, 10.0)]   # 单色 0603 中心 (节距 4.5)
LED_W, LED_L, LED_H = 1.6, 0.8, 0.8     # 0603 (高按 0.8 算)

# 整机里的位置 (key_bracket_v1_2 按这个做)
Y_BOARD_FRONT = 100.6              # 板正面 y (用户 11-13)
Y_BOARD_BACK = Y_BOARD_FRONT - T   # 99.0
Y_BACK_MAX = Y_BOARD_BACK - BACK_MAX   # 93.0
Z0 = 3.0                           # 板下沿离底盘顶 (支架底条)


def to_global(X, Y):
    """板系 (X, Y) → 整机 (x, Z)"""
    return 20.0 - X, Z0 + Y


def btn_pads(X, Y):
    """按键 4 个焊盘矩形 (x0, y0, w, h) 板系"""
    pw, ph = BTN_PAD
    return [(X + sx * BTN_PAD_C[0] / 2 - pw / 2, Y + sy * BTN_PAD_C[1] / 2 - ph / 2, pw, ph) for sx in (1, -1) for sy in (1, -1)]


def leds():
    """[(名, X, Y, 宽X, 长Y, 高)] 板系"""
    return [('RGB 1615', *RGB, RGB_W, RGB_L, RGB_H)] + [(f'单色{i} 0603', X, Y, LED_W, LED_L, LED_H) for i, (X, Y) in enumerate(LED, 1)]


def main():
    import ezdxf
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    from matplotlib import font_manager as fm
    OUT.mkdir(parents=True, exist_ok=True)
    KO_E = [(0, 0, W, EDGE_KO), (0, H - EDGE_KO, W, EDGE_KO), (0, 0, EDGE_KO, H), (W - EDGE_KO, 0, EDGE_KO, H)]
    # 自检 (11-13 (三) 贴片件): 本体 / 焊盘外包 不出四边禁布, 离正面孔周禁布 ≥0.3, 互相 ≥0.3
    def rect_gap(a, b):
        return max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
    def circ_gap(r, c, d):   # 矩形 r 到圆 (c, d) 的距离
        dx = max(r[0] - c[0], 0, c[0] - r[0] - r[2]); dy = max(r[1] - c[1], 0, c[1] - r[1] - r[3]); return math.hypot(dx, dy) - d / 2
    btn_out = [(X - BTN_PAD_OUT[0] / 2, Y - BTN_PAD_OUT[1] / 2, *BTN_PAD_OUT) for X, Y in BTN]       # 焊盘外包 9.5×5.6
    btn_body = [(X - BTN_BODY / 2, Y - BTN_BODY / 2, BTN_BODY, BTN_BODY) for X, Y in BTN]
    led_r = [(X - w / 2, Y - l / 2, w, l) for _, X, Y, w, l, _ in leds()]
    comps = btn_out + btn_body + led_r
    assert all(c[0] >= EDGE_KO and c[1] >= EDGE_KO and c[0] + c[2] <= W - EDGE_KO and c[1] + c[3] <= H - EDGE_KO for c in comps), '元件出四边禁布'
    assert min(circ_gap(c, m, FRONT_KO_D) for c in comps for m in MH) >= 0.3 - 1e-9, "元件离正面孔周禁布 <0.3"
    assert rect_gap(btn_body[0], btn_body[1]) >= 0.5 - 1e-9 and rect_gap(btn_out[0], btn_out[1]) >= 0.3 - 1e-9, '两按键太近'
    assert all(rect_gap(b, l) >= 0.3 - 1e-9 for b in btn_out for l in led_r), '按键焊盘离 LED <0.3'
    assert all(rect_gap(a, b) >= 0.3 - 1e-9 for i, a in enumerate(led_r) for b in led_r[i + 1:])
    gap_rgb = min(rect_gap(b, led_r[0]) for b in btn_out)

    doc = ezdxf.new('R2000'); msp = doc.modelspace()
    for n, c in (('Edge_Cuts', 7), ('KeepOut_F', 1), ('KeepOut_B', 6), ('Holes', 4), ('Comp', 3), ('Pads', 2), ('Text', 5)): doc.layers.add(n, color=c)
    msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'Edge_Cuts'})
    def rect(x, y, w, h, layer):
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={'layer': layer})
    for x, y in MH:
        msp.add_circle((x, y), MH_D / 2, dxfattribs={'layer': 'Holes'})
        msp.add_circle((x, y), BACK_KO_D / 2, dxfattribs={'layer': 'KeepOut_B'})
        msp.add_circle((x, y), FRONT_KO_D / 2, dxfattribs={'layer': 'KeepOut_F'})
    for r in KO_E: rect(*r, 'KeepOut_F')
    for (X, Y), b, o in zip(BTN, btn_body, btn_out):
        rect(*b, 'Comp'); rect(*o, 'Pads'); msp.add_circle((X, Y), BTN_STEM_D / 2, dxfattribs={'layer': 'Comp'})
        for pd in btn_pads(X, Y): rect(*pd, 'Pads')
    for r in led_r: rect(*r, 'Comp')
    doc.saveas(OUT / 'key_board_outline_v1_2.dxf')

    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    fig, ax = plt.subplots(figsize=(11, 7.4), dpi=110)
    ax.add_patch(Rectangle((0, 0), W, H, fc='#2E7D32', alpha=.25, ec='k', lw=2))
    for x, y, w, h in KO_E:
        ax.add_patch(Rectangle((x, y), w, h, fc='red', alpha=.15, ec='none'))
    for x, y in MH:
        ax.add_patch(Circle((x, y), FRONT_KO_D / 2, fc='red', alpha=.15, ec='r', ls='--'))
        ax.add_patch(Circle((x, y), BACK_KO_D / 2, fc='none', ec='m', ls=':', lw=1.5))
        ax.add_patch(Circle((x, y), MH_D / 2, fc='white', ec='k'))
        ax.text(x, y - 4.6, f'M3 Φ{MH_D:g}\n({x:g}, {y:g})', ha='center', va='top', fontsize=7)
    for i, ((X, Y), b, o) in enumerate(zip(BTN, btn_body, btn_out), 1):
        ax.add_patch(Rectangle(o[:2], o[2], o[3], fc='none', ec='#E65100', ls='--', lw=1))
        for pd in btn_pads(X, Y): ax.add_patch(Rectangle(pd[:2], pd[2], pd[3], fc='#FFB74D', ec='#E65100', lw=.6))
        ax.add_patch(Rectangle(b[:2], b[2], b[3], fc='#ddd', ec='k', alpha=.85)); ax.add_patch(Circle((X, Y), BTN_STEM_D / 2, fc='#555'))
        ax.text(X, Y + (3.4 if i == 1 else -3.4), f'按键{i} 6×6×7.5 贴片 ({X:g}, {Y:g})', ha='center', va='bottom' if i == 1 else 'top', fontsize=7)
    for (nm, X, Y, w, l, h), r in zip(leds(), led_r):
        ax.add_patch(Rectangle(r[:2], r[2], r[3], fc='#E040FB' if 'RGB' in nm else '#FFD966', ec='k'))
    ax.text(RGB[0], RGB[1] + 1.4, f'三色 1615\n({RGB[0]:g}, {RGB[1]:g})', ha='center', va='bottom', fontsize=7)
    ax.text(26.5, 8.9, '单色 0603 ×3\n(22 / 26.5 / 31, 10)', ha='center', va='top', fontsize=7)
    ax.annotate('', (0, -2), (W, -2), arrowprops=dict(arrowstyle='<->')); ax.text(W / 2, -3.4, f'{W:g}', ha='center')
    ax.annotate('', (-2, 0), (-2, H), arrowprops=dict(arrowstyle='<->')); ax.text(-3.4, H / 2, f'{H:g}', va='center', rotation=90)
    ax.set_title(f'按键板板框 {W:g}×{H:g}×{T:g} (正视 = 从机器外面看; 红 = 正面禁布, 紫虚圈 = 背面 Φ{BACK_KO_D:g} 螺母禁布, 橙虚框 = 按键焊盘外包)', fontsize=10)
    note = (f'固定: 支架前面平板压整板正面; 2×M3×8 超薄头埋平板前面沉孔往里穿 平板 + 板 {T:g}, 背面 M3 法兰螺母 Φ7.6×3.7 (孔周正 / 背面 Φ{FRONT_KO_D:g} 禁布)\n'
            f'正面只放 6 件 (全贴片): 按键 6×6×7.5 (本体高 {BTN_BODY_H:g}, 杆 Φ{BTN_STEM_D:g}, 行程 {BTN_TRAVEL:g}, 焊盘外包 {BTN_PAD_OUT[0]:g}×{BTN_PAD_OUT[1]:g} 脚沿 X);\n'
            f'  三色 1615 {RGB_W:g}×{RGB_L:g}×{RGB_H:g}; 单色 0603 {LED_W:g}×{LED_L:g}×{LED_H:g}。按键焊盘外包离三色 LED 只 {gap_rgb:.2f} (平板背面脚让位与三色隔光孔在板面处连通 1.5 高)\n'
            f'平板背面: 按键本体 + 脚让位腔, 每颗 LED 一个隔光孔, 其余全贴板, 所以正面别放其他件 (含测试点 / 丝印凸起)\n'
            f'背面元件高 ≤ {BACK_MAX:g} (含插座, 建议 PH2.0 卧式, 出线朝下)\n'
            f'整机位置: 板中心 x=0 (+Y 侧), 正面 y{Y_BOARD_FRONT:g} / 背面 y{Y_BOARD_BACK:g}, 下沿 Z{Z0:g}–上沿 Z{Z0 + H:g}; 整机 x = 20 − X, Z = {Z0:g} + Y')
    ax.text(-3, -5.6, note, fontsize=7.3, va='top')
    ax.set_xlim(-6, W + 4); ax.set_ylim(-18, H + 4); ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(); plt.savefig(OUT / 'key_board_outline_v1_2_layout.png')
    print(f'板 {W}x{H}x{T}; 孔 {MH}; 按键 {BTN}; RGB {RGB}; LED {LED}; 按键焊盘离三色 {gap_rgb:.2f}')


if __name__ == '__main__':
    main()
