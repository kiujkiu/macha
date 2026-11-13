# -*- coding: utf-8 -*-
"""导光管 light_pipe_v1_2 —— 标准件占位 + 装配核算 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python light_pipe_v1_2.py
输出 v1.2/models/light_pipe_v1_2/: light_pipe_v1_2.step/.stl (单件, 本地坐标) + light_pipe_装配位.step + light_pipe_preview.png

用户买的导光管 (20 个): 管身 Φ3.0 (根部/管尾 Φ2.8, 略锥), 头部 Φ3.3 圆顶高 0.8, 总长 4.5 (含头部)。
装法: 下罩罩好后从外皮外面把管尾先插进外皮孔 (紧配), Φ3.3 头卡在 r110 外表面, 管身往里伸向 LED 顶。
本地坐标: 轴 = +Y (朝外), 管尾端面 y=0, 头底 (支承面) y=BODY_L, 圆顶顶 y=L_TOTAL。
核算: 头底支承在孔周 Φ3.3 范围内外皮最外点 (r110 圆柱 → 离 x=0 最近那一侧), 管尾 y = 支承 y − 管身长。
不 import build_v1_2 (只 import 板常数 key_board_outline_v1_2; 预览图里调 key_bracket_v1_2 取下罩让位腔截面)。
"""
import math
from pathlib import Path

from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

import key_board_outline_v1_2 as KB

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'light_pipe_v1_2'

# ---- 导光管 (用户图纸) ----
D_BODY = 3.0          # 管身 (头下)
D_TAIL = 2.8          # 管尾 (略锥)
D_HEAD = 3.3          # 头部
H_HEAD = 0.8          # 圆顶高
L_TOTAL = 4.5         # 总长 (含头部)
BODY_L = L_TOTAL - H_HEAD   # 3.7 管身

SH_OUT = 110.0        # 下罩外表面 r110 圆柱 (= DISC_D / 2)
CLR_POCKET = 0.3      # key_bracket 让位腔单边间隙 (腔前面 = LED 顶 + 0.3)
GAP_OK = (0.0, 0.5)   # 管尾到 LED 顶 理想
GAP_TARGET = 0.3      # 修短目标间隙
HOLE_D = 3.1          # 外皮孔建议 (管身 Φ3.0 紧配; FDM 横孔偏小 0.1~0.15, 必要时 Φ3.0 钻头过一下)

DEFAULTS = dict(D_BODY=D_BODY, D_TAIL=D_TAIL, D_HEAD=D_HEAD, H_HEAD=H_HEAD, L_TOTAL=L_TOTAL)


def make_light_pipe(p=None):
    """标准件占位 (本地坐标, 轴 +Y, 管尾 y=0)。p 可改 L_TOTAL (修短后的长度) 等。"""
    P = dict(DEFAULTS, **(p or {}))
    body_l = P['L_TOTAL'] - P['H_HEAD']
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    body = BRepPrimAPI_MakeCone(ax, P['D_TAIL'] / 2, P['D_BODY'] / 2, body_l).Shape()
    a, h = P['D_HEAD'] / 2, P['H_HEAD']
    R = (a * a + h * h) / (2 * h)                     # 球冠半径 (底 Φ3.3, 高 0.8)
    sph = BRepPrimAPI_MakeSphere(gp_Pnt(0, P['L_TOTAL'] - R, 0), R).Shape()
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
    """[(名, x, z, LED Φ, LED 顶 y)] 整机坐标"""
    r = [('RGB Φ5', *KB.to_global(*KB.RGB), KB.RGB_D, KB.Y_BOARD_FRONT + KB.RGB_H)]
    for i, q in enumerate(KB.LED, 1):
        r.append((f'单色{i} Φ3', *KB.to_global(*q), KB.LED_D, KB.Y_BOARD_FRONT + KB.LED_H))
    return r


def calc(L=L_TOTAL):
    """每颗 LED: 外皮内/外表面、支承、管尾、间隙、为达 GAP_TARGET 的管长"""
    rows = []
    for name, x, z, d, top in leds():
        inner = top + CLR_POCKET                       # 让位腔前面 (外皮内表面)
        seat = y_out(max(abs(x) - D_HEAD / 2, 0.0))     # Φ3.3 头底支承 = 孔周最外点
        tail = seat - (L - H_HEAD)
        gap = tail - top
        L_fit = seat - top - GAP_TARGET + H_HEAD        # 修到目标间隙的总长
        rows.append(dict(name=name, x=x, z=z, d=d, top=top, inner=inner, outer=y_out(x), seat=seat,
                         skin=y_out(x) - inner, tail=tail, gap=gap, L_fit=L_fit,
                         wedge=seat - y_out(abs(x) + D_HEAD / 2)))   # 头底与曲面的楔形缝 (外侧边)
    return rows


def preview(rows):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon
    from matplotlib import font_manager as fm
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
    from OCP.gp import gp_Pln
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopoDS import TopoDS
    import key_bracket_v1_2 as KBR
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    Zc = KB.Z0 + KB.RGB[1]                              # 板孔中心高 Z13
    fig, ax = plt.subplots(figsize=(14, 8.2), dpi=120)
    # 外皮 (r110 外 → 让位腔): 先画外皮实体区 (r 90.8..110) 再用腔截面盖白
    xs = [i / 10 for i in range(-160, 101)]
    ax.fill_between(xs, [y_out(x) for x in xs], [98.0] * len(xs), color='#B0BEC5', alpha=.55, lw=0, label='下罩 (外皮)')
    ax.plot(xs, [y_out(x) for x in xs], 'k', lw=1.2)
    kr = KBR.make_key_bracket()
    sec = BRepAlgoAPI_Section(kr['pocket'], gp_Pln(gp_Pnt(0, 0, Zc), gp_Dir(0, 0, 1))); sec.Build()
    segs = []
    e = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(e.Current()))
        p0, p1 = c.Value(c.FirstParameter()), c.Value(c.LastParameter())
        segs.append(((p0.X(), p0.Y()), (p1.X(), p1.Y()))); e.Next()
    # 腔截面是直线围成的多边形, 按端点串起来填白
    pts = [segs[0][0], segs[0][1]]; left = segs[1:]
    while left:
        for i, (a, b) in enumerate(left):
            if math.dist(a, pts[-1]) < 1e-6: pts.append(b); left.pop(i); break
            if math.dist(b, pts[-1]) < 1e-6: pts.append(a); left.pop(i); break
        else: break
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec='#607D8B', lw=1, zorder=2, label='下罩让位腔 (Z13 截面)'))
    # 板 + 支架立柱
    ax.add_patch(Rectangle((-KB.W / 2, KB.Y_BOARD_BACK), KB.W, KB.T, fc='#2E7D32', alpha=.7, zorder=3, label='按键板'))
    for s in (1, -1):
        ax.add_patch(Rectangle((min(13 * s, 21 * s), KB.Y_BOARD_FRONT), 8, 3, fc='#F1C232', alpha=.8, zorder=3))
    ax.text(-17, 102.1, '支架立柱', ha='center', fontsize=8, zorder=4)
    for i, r in enumerate(rows):
        x, d, top = r['x'], r['d'], r['top']
        dome = d / 2
        yb = KB.Y_BOARD_FRONT
        ax.add_patch(Polygon([(x - d / 2, yb), (x + d / 2, yb), (x + d / 2, top - dome)] +
                             [(x + d / 2 * math.cos(t / 20 * math.pi), top - dome + dome * math.sin(t / 20 * math.pi)) for t in range(21)] +
                             [(x - d / 2, top - dome)], closed=True, fc='#E040FB' if i == 0 else '#FFD966', ec='k', lw=.8, zorder=4))
        # 导光管 (4.5 原长), 头支承在 seat
        tl, sb = r['tail'], r['seat']
        a = D_HEAD / 2; R = (a * a + H_HEAD ** 2) / (2 * H_HEAD); yc = sb + H_HEAD - R
        ang = math.asin(a / R)
        cap = [(x + R * math.sin(-ang + 2 * ang * k / 30), yc + R * math.cos(-ang + 2 * ang * k / 30)) for k in range(31)]
        pipe = [(x - D_TAIL / 2, tl), (x + D_TAIL / 2, tl), (x + D_BODY / 2, sb), (x + a, sb)] + cap[::-1] + [(x - a, sb), (x - D_BODY / 2, sb)]
        bad = r['gap'] < 0
        ax.add_patch(Polygon(pipe, closed=True, fc='#80DEEA', ec='r' if bad else '#00838F', lw=1.2, alpha=.85, zorder=5))
        col = 'r' if bad else ('#E65100' if r['gap'] < 0.1 else 'g')
        txt = (f"{r['name']} x{x:g}\nLED 顶 y{top:.2f}\n外皮 内{r['inner']:.2f}/外{r['outer']:.2f} (厚{r['skin']:.2f})\n"
               f"管尾 y{tl:.2f} → 间隙 {r['gap']:+.2f}\n" + (f"需修到 L{r['L_fit']:.1f}" if r['gap'] < 0.1 else 'L4.5 可用'))
        ax.text(x, 96.0 - (i % 2) * 2.4, txt, ha='center', va='top', fontsize=7.5, color=col,
                bbox=dict(fc='white', ec=col, lw=.8, alpha=.9), zorder=6)
        ax.plot([x, x], [top, tl], color=col, lw=2.2, zorder=7)
    ax.set_xlim(-16, 9); ax.set_ylim(88.5, 111.2); ax.set_aspect('equal')
    ax.invert_xaxis()                                  # 从上往下看, 外面 (+Y) 在上 ⇒ 板正视方向一致 (左 = 板系 X 小)
    ax.set_xlabel('整机 x (mm, 已左右翻转与板正视一致)'); ax.set_ylabel('整机 y (mm)')
    ax.set_title(f'导光管 Φ3 L{L_TOTAL:g} 装配核算 — 俯视剖面 Z{Zc:g} (板孔中心); 头 Φ{D_HEAD:g} 支承在 r110 外表面 (孔周最外点)', fontsize=11)
    ax.legend(loc='lower left', fontsize=8)
    ax.grid(alpha=.25)
    plt.tight_layout(); plt.savefig(OUT / 'light_pipe_preview.png')


def main():
    from helpers import write_doc
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    OUT.mkdir(parents=True, exist_ok=True)
    lp = make_light_pipe()
    BRepMesh_IncrementalMesh(lp, 0.005, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(lp, str(OUT / 'light_pipe_v1_2.stl'))
    write_doc([('light_pipe_v1_2', lp, '#80DEEA', None, False)], OUT / 'light_pipe_v1_2.step', 'light_pipe_v1_2')
    rows = calc()
    # 装配位: 按推荐 (单色 1/2 原长, 修短的按 L_fit 取 0.1 向下)
    items = []
    for r in rows:
        L = L_TOTAL if r['gap'] >= 0.1 else math.floor(r['L_fit'] * 10) / 10
        items.append((f"light_pipe_{r['name'].split()[0]}_L{L:g}", place(make_light_pipe(dict(L_TOTAL=L)), r['x'], r['z'], r['seat'] - (L - H_HEAD)),
                      '#80DEEA', None, False))
    write_doc(items, OUT / 'light_pipe_装配位.step', 'light_pipes')
    print(f'{"LED":10s} {"x":>6s} {"LED顶":>7s} {"皮内":>7s} {"皮外":>7s} {"皮厚":>5s} {"支承":>7s} {"管尾":>7s} {"间隙":>6s} {"修到L":>6s} {"楔缝":>5s}')
    for r in rows:
        print(f"{r['name']:10s} {r['x']:6.1f} {r['top']:7.2f} {r['inner']:7.2f} {r['outer']:7.2f} {r['skin']:5.2f} "
              f"{r['seat']:7.3f} {r['tail']:7.3f} {r['gap']:+6.2f} {r['L_fit']:6.2f} {r['wedge']:5.2f}")
    preview(rows)
    print('输出', OUT)


if __name__ == '__main__':
    main()
