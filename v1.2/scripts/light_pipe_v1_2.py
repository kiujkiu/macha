# -*- coding: utf-8 -*-
"""导光柱 light_pipe_v1_2 —— 标准件占位 + 装配核算 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python light_pipe_v1_2.py
输出 v1.2/models/light_pipe_v1_2/: light_pipe_v1_2.step/.stl (单件, 本地坐标, 推荐 8.9 型) + light_pipe_装配位.step (每颗剪到推荐长度)
     + light_pipe_preview.png

11-13 (三) 选型 (协调定): Bivar PLP2 系列 (或国产同款) 前装圆顶导光柱, 头部 Φ3.3×0.8 法兰, 管身 Φ2.8, 压筋参考 Φ3.1;
  现货长度 8.9 (PLP2-350) / 9.5 (PLP2-375) / 10 (PLP2-10MM) —— **下单前按图纸核对 "长度" 是否含法兰**; RGB 那路建议雾化版 (-D)。
  外皮压管孔 Φ3.0 (官方推荐 Φ2.9, 打印放到 3.0; 不用 3.1 会松); 支架前面平板隔光孔 Φ3.2 (只做遮光通道, 不夹管)。
装法: 下罩罩好后从外皮外面把管插进外皮孔 (压筋紧配), Φ3.3 法兰卡在 r110 外表面, 管身穿过外皮 → 平板隔光孔 → 伸向 LED 顶。
长度规则 (协调): 管长 (法兰下) = LED 顶面到外皮外表面 (孔轴线处) 的距离 − 0.3。
本地坐标: 轴 = +Y (朝外), 管尾端面 y=0, 法兰底 (支承面) y=BODY_L, 圆顶顶 y=BODY_L+H_HEAD。
核算: 法兰底支承在孔周 Φ3.3 范围内外皮最外点 (r110 圆柱 → 离 x=0 最近那一侧), 管尾 y = 支承 y − 管身长。
不 import build_v1_2 (只 import 板常数 key_board_outline_v1_2 + 支架参数 key_bracket_v1_2)。
"""
import math
from pathlib import Path

from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

import key_board_outline_v1_2 as KB
import key_bracket_v1_2 as KBR

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'light_pipe_v1_2'

# ---- 导光柱 PLP2 (协调 11-13) ----
D_BODY = 2.8          # 管身
D_RIB = 3.1           # 压筋外径 (参考)
D_HEAD = 3.3          # 法兰 / 圆顶
H_HEAD = 0.8          # 法兰+圆顶高
STOCK = [(8.9, 'PLP2-350'), (9.5, 'PLP2-375'), (10.0, 'PLP2-10MM')]   # 现货长度 (按法兰下管长算; 若含法兰则管身短 0.8)
BODY_L = 8.9          # 默认单件 = 8.9 型 (法兰下)

SH_OUT = KBR.DEFAULTS['SH_OUT']           # 下罩外表面 r110
HOLE_D = KBR.DEFAULTS['HOLE_LED']         # 外皮压管孔 Φ3.0
PL_HOLE_D = KBR.DEFAULTS['PL_LED_D']      # 平板隔光孔 Φ3.2
Y_PLATE = KBR.DEFAULTS['PL_Y1']           # 平板前面 y105.7
CLR_POCKET = KBR.DEFAULTS['CLR']          # 让位腔间隙 (外皮内面 = 平板前面 + 0.3)
GAP_TARGET = 0.3                          # 管尾离 LED 顶

DEFAULTS = dict(D_BODY=D_BODY, D_HEAD=D_HEAD, H_HEAD=H_HEAD, BODY_L=BODY_L)


def make_light_pipe(p=None):
    """标准件占位 (本地坐标, 轴 +Y, 管尾 y=0)。p 可改 BODY_L (剪短后的法兰下管长)。压筋不建模 (按 Φ2.8 管身)。"""
    P = dict(DEFAULTS, **(p or {}))
    body_l = P['BODY_L']
    body = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), P['D_BODY'] / 2, body_l).Shape()
    a, h = P['D_HEAD'] / 2, P['H_HEAD']
    R = (a * a + h * h) / (2 * h)                     # 球冠半径 (底 Φ3.3, 高 0.8)
    sph = BRepPrimAPI_MakeSphere(gp_Pnt(0, body_l + h - R, 0), R).Shape()
    cy = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, body_l, 0), gp_Dir(0, 1, 0)), a, h).Shape()
    o = BRepAlgoAPI_Common(sph, cy); o.Build(); head = o.Shape()
    o = BRepAlgoAPI_Fuse(body, head); o.Build()
    u = ShapeUpgrade_UnifySameDomain(o.Shape(), True, True, True); u.Build(); s = u.Shape()
    assert BRepCheck_Analyzer(s).IsValid()
    return s


def place(shape, x, z, y_tail):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(x, y_tail, z))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def y_out(x):
    return math.sqrt(SH_OUT ** 2 - x * x)


def leds():
    """[(名, x, z, 宽, 长, LED 顶 y)] 整机坐标"""
    return [(nm, *KB.to_global(X, Y), w, l, KB.Y_BOARD_FRONT + h) for nm, X, Y, w, l, h in KB.leds()]


def calc(body_l=BODY_L):
    """每颗 LED: LED 顶 / 外皮内外表面 / 法兰支承 / 管尾 (按 body_l) / 间隙 / 推荐长度"""
    rows = []
    for name, x, z, w, l, top in leds():
        inner = Y_PLATE + CLR_POCKET                    # 外皮内面 (让位腔前面) 106.0
        seat = y_out(max(abs(x) - D_HEAD / 2, 0.0))     # Φ3.3 法兰底支承 = 孔周最外点
        tail = seat - body_l
        dist = y_out(x) - top                           # LED 顶 → 外皮外表面 (孔轴线)
        L_rule = dist - GAP_TARGET                      # 协调规则
        L_exact = seat - top - GAP_TARGET               # 按法兰实际支承点, 管尾正好离 LED 0.3
        stock = next(((L, n) for L, n in STOCK if L >= L_exact), STOCK[-1])
        rows.append(dict(name=name, x=x, z=z, top=top, inner=inner, outer=y_out(x), seat=seat, skin=y_out(x) - inner,
                         tail=tail, gap=tail - top, dist=dist, L_rule=L_rule, L_exact=L_exact, stock=stock,
                         gap_stock=seat - stock[0] - top, gap_stock_incl=seat - (stock[0] - H_HEAD) - top,   # 现货原长 (法兰下 / 含法兰)
                         in_plate=Y_PLATE - (seat - L_exact),        # 管伸进平板隔光孔深度
                         wedge=seat - y_out(abs(x) + D_HEAD / 2)))   # 法兰底与曲面的楔形缝 (外侧边)
    return rows


def preview(rows):
    """俯视剖面 Z16 (11-13 (五) LED 行 = 板中线; 过 4 颗 LED): 下罩 / 支架平板 / 板 (光栅化真实几何) + 剪到推荐长度的导光柱 + 每颗数值"""
    import numpy as np
    from matplotlib.patches import Polygon
    plt = KBR._font()
    kr = KBR.make_key_bracket()
    sh = KBR.shroud_local(kr)
    Zc = rows[0]['z']
    U, V = (-16, 9), (97.5, 111.2)
    img = KBR.raster([(sh, KBR.C_SH), (kr['bracket'], KBR.C_BR), (kr['board'], KBR.C_BD)], ('z', Zc), U, V, res=0.06)
    fig, ax = plt.subplots(figsize=(14, 9), dpi=120)
    ax.imshow(img, origin='lower', extent=(U[0], U[1], V[0], V[1]), interpolation='nearest')
    for i, r in enumerate(rows):
        x, top, sb = r['x'], r['top'], r['seat']
        L = r['L_exact']; tl = sb - L
        a = D_HEAD / 2; R = (a * a + H_HEAD ** 2) / (2 * H_HEAD); yc = sb + H_HEAD - R
        ang = math.asin(a / R)
        cap = [(x + R * math.sin(-ang + 2 * ang * k / 30), yc + R * math.cos(-ang + 2 * ang * k / 30)) for k in range(31)]
        pipe = [(x - D_BODY / 2, tl), (x + D_BODY / 2, tl), (x + D_BODY / 2, sb), (x + a, sb)] + cap[::-1] + [(x - a, sb), (x - D_BODY / 2, sb)]
        ax.add_patch(Polygon(pipe, closed=True, fc='#80DEEA', ec='#00838F', lw=1, alpha=.8, zorder=5))
        txt = (f"{r['name']} x{x:g}\nLED 顶 y{top:.2f}, 外皮外 y{r['outer']:.2f}\n距离 {r['dist']:.2f} − 0.3 = L{r['L_rule']:.2f}\n"
               f"(按法兰支承 L{r['L_exact']:.2f})\n{r['stock'][1]} {r['stock'][0]:g} 剪到 {math.floor(r['L_exact'] * 10) / 10:.1f}")
        ax.text(x, 99.6 - (i % 2) * 0.1, txt, ha='center', va='top', fontsize=7, bbox=dict(fc='white', ec='#00838F', lw=.6, alpha=.92), zorder=6)
    ax.invert_xaxis()                                  # 左右与板正视一致
    ax.set_xlim(U[1], U[0]); ax.set_ylim(91.5, V[1])
    ax.set_xlabel('整机 x (mm, 已左右翻转与板正视一致)'); ax.set_ylabel('整机 y (mm)'); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_title(f'导光柱 PLP2 Φ{D_BODY:g} (头 Φ{D_HEAD:g}×{H_HEAD:g}) 装配核算 — 俯视剖面 Z{Zc:g}; 外皮孔 Φ{HOLE_D:g} 压管 + 平板 Φ{PL_HOLE_D:g} 隔光通道 (同轴); '
                 f'管剪到 管尾离 LED 顶 {GAP_TARGET:g}\n灰 = 下罩, 黄 = 支架平板, 绿 = 板 + LED, 青 = 导光柱 (法兰下长度)', fontsize=10)
    plt.tight_layout(); plt.savefig(OUT / 'light_pipe_preview.png'); plt.close(fig)


def main():
    from helpers import write_doc
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    OUT.mkdir(parents=True, exist_ok=True)
    lp = make_light_pipe()
    BRepMesh_IncrementalMesh(lp, 0.005, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(lp, str(OUT / 'light_pipe_v1_2.stl'))
    write_doc([('light_pipe_v1_2_L8.9', lp, '#80DEEA', None, False)], OUT / 'light_pipe_v1_2.step', 'light_pipe_v1_2')
    rows = calc()
    items = []                                         # 装配位: 每颗剪到推荐长度 (0.1 向下取整, 管尾离 LED ≥0.3)
    for r in rows:
        L = math.floor(r['L_exact'] * 10) / 10
        items.append((f"light_pipe_{r['name'].split()[0]}_L{L:g}", place(make_light_pipe(dict(BODY_L=L)), r['x'], r['z'], r['seat'] - L), '#80DEEA', None, False))
    write_doc(items, OUT / 'light_pipe_装配位.step', 'light_pipes')
    print(f'{"LED":10s} {"x":>6s} {"LED顶":>7s} {"皮内":>7s} {"皮外":>7s} {"皮厚":>5s} {"支承":>7s} {"8.9尾":>7s} {"8.9隙":>6s} {"距离":>6s} {"规则L":>6s} {"精确L":>6s} {"进平板":>6s} 现货')
    for r in rows:
        print(f"{r['name']:10s} {r['x']:6.1f} {r['top']:7.2f} {r['inner']:7.2f} {r['outer']:7.2f} {r['skin']:5.2f} {r['seat']:7.3f} {r['tail']:7.3f} {r['gap']:+6.2f} "
              f"{r['dist']:6.2f} {r['L_rule']:6.2f} {r['L_exact']:6.2f} {r['in_plate']:6.2f} {r['stock'][1]} {r['stock'][0]:g} (原长隙 {r['gap_stock']:+.2f}, 若含法兰 {r['gap_stock_incl']:+.2f})")
    preview(rows)
    print('输出', OUT)


if __name__ == '__main__':
    main()
