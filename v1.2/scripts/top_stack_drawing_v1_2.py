"""V1.2 顶部连接第二版 A3 2D 图 ×2 (装配 / 零件)。先跑 top_stack_v1_2.py, 本文件只读 参数.json + 零件/*.step。
    cd v1.2/scripts && ../../.venv/bin/python top_stack_drawing_v1_2.py
→ v1.2/顶部连接/顶部连接_装配_2D图.{pdf,dxf} / 顶部连接_零件_2D图.{pdf,dxf} + _preview.png
"""
import json, math, time
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
from matplotlib import font_manager
import matplotlib.pyplot as plt
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
from drawing_v1_2 import Page, hdim, vdim, vchain, hchain, chain, F, MM_PT
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
import ezdxf
from OCP.STEPControl import STEPControl_Reader
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.BRepLib import BRepLib

OUT = Path(__file__).resolve().parents[1] / '顶部连接'
J = json.loads((OUT / '参数.json').read_text(encoding='utf-8')); IF, P, D = J['IF'], J['P'], J['D']
def load(k):
    r = STEPControl_Reader(); r.ReadFile(str(OUT / '零件' / f'{k}.step')); r.TransferRoots(); return r.OneShape()
KEYS = ('led_top_bar', 'post_holder', 'post', 'brg695', 'hub', 'led_comb', 'hub_nut'); S = {k: load(k) for k in KEYS}
COL = dict(led_top_bar='#D5E8CC', post_holder='#CFE2F3', post='#DCCBE6', brg695='#C9C9C9', hub='#FBEBB5', led_comb='#D0E0E3', hub_nut='#BFE5CC', glass='#E6F4FA', led='#CFE5D3')
HATCH = dict(led_top_bar='////', post_holder='\\\\\\\\', post=None, brg695='xxxx', hub='////', led_comb='....', hub_nut='\\\\\\\\')
ecc, z1 = IF['ecc'], IF['z_led']; g0, g1 = IF['z_glass0'], IF['z_glass1']
def _pts(e, rev=False):
    g = GCPnts_QuasiUniformDeflection(BRepAdaptor_Curve(e), 0.01)
    q = [g.Value(i) for i in range(1, g.NbPoints() + 1)]
    return q[::-1] if rev else q
def sec(shape, axis, at):                        # axis 'x': 平面 x=at (横 = y); 'y': 平面 y=at (横 = x) → 闭合环
    pl = gp_Pln(gp_Pnt(at, 0, 0), gp_Dir(1, 0, 0)) if axis == 'x' else gp_Pln(gp_Pnt(0, at, 0), gp_Dir(0, 1, 0))
    c = BRepAlgoAPI_Common(shape, BRepBuilderAPI_MakeFace(pl, -400, 400, -400, 400).Face()).Shape()
    out = []; ef = TopExp_Explorer(c, TopAbs_FACE)
    while ef.More():
        f = TopoDS.Face(ef.Current()); ew = TopExp_Explorer(f, TopAbs_WIRE); face = []
        while ew.More():
            w = BRepTools_WireExplorer(TopoDS.Wire(ew.Current()), f); lp = []
            while w.More():
                e = w.Current(); q = _pts(e, e.Orientation() == TopAbs_REVERSED)
                lp += [((p.Y() if axis == 'x' else p.X()), p.Z()) for p in q[:-1]]; w.Next()
            face.append(lp); ew.Next()
        out.append(face); ef.Next()
    return out
def hlr(shapes, d, xdir):                        # 从 d 方向看 (d 指向观察者) → 可见 / 隐藏折线
    c = TopoDS_Compound(); b = BRep_Builder(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    a = HLRBRep_Algo(); a.Add(c); a.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*d), gp_Dir(*xdir)))); a.Update(); a.Hide()
    h = HLRBRep_HLRToShape(a); R = []
    for grp in ((h.VCompound, h.OutLineVCompound), (h.HCompound,)):
        o = []
        for fn in grp:
            sh = fn()
            if sh is None or sh.IsNull(): continue
            BRepLib.BuildCurves3d_s(sh); e = TopExp_Explorer(sh, TopAbs_EDGE)
            while e.More(): o.append([(p.X(), p.Y()) for p in _pts(TopoDS.Edge(e.Current()))]); e.Next()
        R.append(o)
    return R

def newpage():
    global pg, ax, doc, msp
    pg = Page(); ax = pg.ax; doc = ezdxf.new('R2010', setup=True); doc.units = 4; msp = doc.modelspace()
    for n, c in (('led_top_bar', 3), ('post_holder', 5), ('post', 6), ('brg695', 9), ('hub', 2), ('led_comb', 4), ('hub_nut', 3), ('glass', 150), ('led', 94), ('screw', 8), ('nut', 30), ('center', 1), ('text', 7)): doc.layers.add(n, color=c)
newpage()
DX = {}                                          # 视图 → DXF 偏移
class V:                                         # 视图: 模型 (u,w) → 页面
    def __init__(s, X, Y, k, u0, w0, dx): s.X, s.Y, s.k, s.u0, s.w0, s.dx = X, Y, k, u0, w0, dx
    def x(s, u): return s.X + (u - s.u0) * s.k
    def y(s, w): return s.Y + (w - s.w0) * s.k
    def face(s, face, col, hatch=None, lay=None, z=1.5, lw=0.35):
        v, c = [], []
        for lp in face:
            q = [(s.x(u), s.y(w)) for u, w in lp]; v += q + [q[0]]; c += [MP.MOVETO] + [MP.LINETO] * (len(q) - 1) + [MP.CLOSEPOLY]
            if lay: msp.add_lwpolyline([(u + s.dx[0], w + s.dx[1]) for u, w in lp], close=True, dxfattribs=dict(layer=lay))
        ax.add_patch(PathPatch(MP(v, c), fc=col, ec='none', zorder=z))
        if hatch: ax.add_patch(PathPatch(MP(v, c), fc='none', ec='#8a8a8a', lw=0, hatch=hatch, zorder=z + 0.1))
        ax.add_patch(PathPatch(MP(v, c), fc='none', ec='k', lw=lw * MM_PT, zorder=z + 0.6))
    def part(s, k, axis, at, hatch=True):
        for f in sec(S[k], axis, at): s.face(f, COL[k], HATCH[k] if hatch else None, k)
    def box(s, u0, u1, w0, w1, col, lay, z=1.2, brk=()):
        s.face([[(u0, w0), (u1, w0), (u1, w1), (u0, w1)]], col, None, lay, z=z, lw=0.2)
    def pl(s, P_, lw=0.3, ls='-', color='k', lay=None, z=3):
        ax.plot([s.x(a) for a, _ in P_], [s.y(b) for _, b in P_], lw=lw * MM_PT, ls=ls, color=color, zorder=z, solid_capstyle='round')
        if lay: msp.add_lwpolyline([(a + s.dx[0], b + s.dx[1]) for a, b in P_], dxfattribs=dict(layer=lay, linetype='DASHED' if ls != '-' else 'CONTINUOUS'))
    def cl(s, a, b, lw=0.15):
        ax.plot([s.x(a[0]), s.x(b[0])], [s.y(a[1]), s.y(b[1])], lw=lw * MM_PT, color='0.3', ls=(0, (8, 2, 1.5, 2)), zorder=4)
        msp.add_line((a[0] + s.dx[0], a[1] + s.dx[1]), (b[0] + s.dx[0], b[1] + s.dx[1]), dxfattribs=dict(layer='center', linetype='CENTER'))
def title(x, y, t, v): pg.text(x, y, t, size=3.4, ha='center', weight='bold'); msp.add_text(t, height=3, dxfattribs=dict(layer='text')).set_placement((v.dx[0], v.dx[1] + (v.y_top if hasattr(v, 'y_top') else 0)))
def ref(x, y, n, tx, ty):                        # 件号引线
    pg.line(x, y, tx, ty, lw=0.15); ax.plot([x], [y], 'k.', ms=2.5, zorder=6)
    ax.add_patch(plt.Circle((tx, ty), 2.9, fc='w', ec='k', lw=0.5, zorder=6)); pg.text(tx, ty - 0.05, str(n), size=3.2, ha='center', va='center').set_zorder(7)

from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
def clipx(s, a, b): return BRepAlgoAPI_Common(s, BRepPrimAPI_MakeBox(gp_Pnt(a, -100, 100), gp_Pnt(b, 100, 400)).Shape()).Shape()
zc, zp, zs, zb, pt, bz0, bz1, h0, h1, zt = (D[k] for k in ('zc', 'zp', 'zs', 'zb', 'pt', 'bz0', 'bz1', 'h0', 'h1', 'zt'))
fx, nx, bx, by = P['fx'], P['nut_x'], P['bar_hx'], P['bar_hy']; zr = z1 - P['rib_h']; w0, w1 = J['WIN']['top']; zm = w0 + P['nut_l']; e0 = IF['gap'] / 2; t16 = D['led_t']; rc = P['nut_af'] / math.sqrt(3); rh = IF['hole_d'] / 2
GR, OR, CU = '#EEEEEE', '#F6B26B', '#E3C877'
def scr(v, x, zh, l, z=3): q, h = P['head_d'] / 2, P['head_h']; v.face([[(x - 1.5, zh - l), (x + 1.5, zh - l), (x + 1.5, zh), (x + q, zh), (x + q, zh + h), (x - q, zh + h), (x - q, zh), (x - 1.5, zh)]], GR, None, 'screw', z=z, lw=0.25)
def fnut(v, x, zt_, z=2.6): v.face([[(x - 3.8, zt_), (x + 3.8, zt_), (x + 3.8, zt_ - 1), (x + 2.75, zt_ - 1), (x + 2.75, zt_ - 3.7), (x - 2.75, zt_ - 3.7), (x - 2.75, zt_ - 1), (x - 3.8, zt_ - 1)]], OR, None, 'nut', z=z, lw=0.25)
def stud(v, x=0): v.face([[(x - 1.5, zs - P['post_m']), (x + 1.5, zs - P['post_m']), (x + 1.5, zs), (x - 1.5, zs)]], '#C4A7D6', None, 'post', z=3, lw=0.2)
def lab(v, u, w, tu, tw, t, ha='left', size=2.3): pg.line(v.x(u), v.y(w), v.x(tu), v.y(tw), lw=0.15); ax.plot([v.x(u)], [v.y(w)], 'k.', ms=2, zorder=8); pg.text(v.x(tu) + (0.5 if ha == 'left' else -0.5), v.y(tw), t, size=size, ha=ha, va='center', halo=True)
def frame(name, l2, qty, fn):
    pg.rect(5, 5, 415, 292, lw=0.4); pg.rect(10, 10, 410, 30, lw=0.35); pg.line(10, 20, 410, 20, lw=0.2)
    for xx in (130, 200, 270, 330): pg.line(xx, 10, xx, 30, lw=0.2)
    pg.text(14, 23.5, name, size=4, weight='bold'); pg.text(14, 13.5, l2, size=2.8); pg.text(134, 23.5, qty, size=2.8); pg.text(134, 13.5, '材料: 打印件 PETG', size=2.8); pg.text(204, 23.5, '比例: 各视图旁注', size=2.8); pg.text(204, 13.5, '单位 mm / 第一角', size=2.8)
    pg.text(274, 23.5, time.strftime('%Y-%m-%d'), size=2.8); pg.text(274, 13.5, 'A3 (420×297)', size=2.8); pg.text(334, 23.5, 'top_stack_drawing_v1_2.py', size=2.5); pg.text(334, 13.5, '剖视 = B-rep 精确剖切', size=2.5)
    for ext, f in (('pdf', lambda q: print(pg.save(q))), ('dxf', doc.saveas)):
        try: f(OUT / f'{fn}.{ext}')
        except PermissionError: f(OUT / f'{fn}.NEW.{ext}')

# ================= 装配 =================
def glass(v):
    for a, b in ((-40, -rh), (rh, 40)): v.box(max(a, -26), min(b, 26), g0, g1, COL['glass'], 'glass', z=1.1)
F1 = V(112, 150, 1, 0, w0, (0, 0)); F1.y_top = 320                      # 正视阶梯剖 1:1
for f in sec(S['led_top_bar'], 'y', ecc): F1.face(f, COL['led_top_bar'], '////', 'led_top_bar')
for a, b, y in ((-9, 9, 0), (-40, -9, ecc), (9, 40, ecc)):
    for f in sec(clipx(S['post_holder'], a, b), 'y', y): F1.face(f, COL['post_holder'], HATCH['post_holder'], 'post_holder')
for a, b in ((-60, -9), (9, 60)):
    for f in sec(clipx(S['led_comb'], a, b), 'y', ecc): F1.face(f, COL['led_comb'], None, 'led_comb')
for k in ('post', 'brg695', 'hub', 'hub_nut'): F1.part(k, 'y', 0)
glass(F1); stud(F1); fnut(F1, 0, zc + P['post_fn_h']); scr(F1, 0, pt, P['top_scr'])
for s in (1, -1): fnut(F1, s * fx, z1 + P['fn_h']); scr(F1, s * fx, zt, P['fix_l'])
for x in (-nx, 0, nx):
    scr(F1, x, zc - (0 if x else P['cb_h']), P['scr_l'])
    for q in (w0, zm): F1.face([[(x - rc, q), (x + rc, q), (x + rc, q + 5), (x - rc, q + 5)]], CU, None, 'nut', z=2, lw=0.25)
    F1.cl((x, w0 - 4), (x, zc + (4 if x else 0)))
F1.pl([(-81.88, w0 - 8), (-81.88, z1), (81.88, z1), (81.88, w0 - 8)], lw=0.3, color='#222222', lay='led'); F1.cl((0, zp), (0, h1 + 4))
title(112, 270, '正视阶梯剖 (长条/锁点剖 y=-4.69, 螺柱处剖 y=0)   1:1', F1)
vchain(pg, [F1.y(v) for v in (w0, zm, w1, zr, z1, zc, zp, zt, zb, h0, g0, g1, h1)], ['下颗 5', '上颗 5', F(zr - w1), '筋 ' + F(P['rib_h']), '绿 ' + F(P['bar_t']), '蓝板 ' + F(P['pl_t']), '梳齿 ' + F(P['comb_t']), '外套(梳齿上) ' + F(zb - zt), '露出 ' + F(h0 - zb), '旋母 ' + F(g0 - h0), '玻璃 ' + F(g1 - g0), '堵头盖 ' + F(h1 - g1)], F1.x(84), F1.x(93), size=2.2)
vdim(pg, F1.y(zs), F1.y(pt), F1.x(-16), F1.x(-36), '螺柱 ' + F(P['post_l']), size=2.6); vdim(pg, F1.y(z1), F1.y(h1), F1.x(-60), F1.x(-74), '屏顶到堵头顶 ' + F(h1 - z1), size=2.6)
hdim(pg, F1.x(-nx), F1.x(nx), F1.y(w0), F1.y(w0) - 12, '3 根 M3×20: 2×' + F(nx), size=2.5); hdim(pg, F1.x(-fx), F1.x(fx), F1.y(w0), F1.y(w0) - 5.5, '蓝件锁点 ' + F(2 * fx), size=2.4)
for (u, w), n, (tu, tw) in (((-60, zc - 2), 1, (-60, zc + 16)), ((-24, zc + 1.5), 2, (-46, zc + 22)), ((0.5, zb + 14), 3, (22, zb + 14)), ((5, bz0 + 2), 4, (-31, bz0 - 14)), ((13, h1 - 1.5), 5, (31, h1 + 6)), ((40, zt - 2), 6, (48, zt + 14)), ((13, h0 + 2), 7, (31, h0 - 12))): ref(F1.x(u), F1.y(w), n, F1.x(tu), F1.y(tw))

G = V(262, 133, 1.5, 0, w0, (160, 0)); G.y_top = 320                    # 侧剖 x=0
for k in ('led_top_bar', 'post_holder', 'post', 'brg695', 'hub', 'hub_nut', 'led_comb'): G.part(k, 'x', 0)
glass(G); stud(G); fnut(G, 0, zc + P['post_fn_h']); scr(G, 0, pt, P['top_scr']); scr(G, ecc, zc - P['cb_h'], P['scr_l'])
for a in (ecc + e0, ecc - e0 - t16): G.box(a, a + t16, w0 - 5, z1, COL['led'], 'led', z=1.5)
for q in (w0, zm): G.box(ecc - 2.3, ecc + 2.3, q, q + 5, CU, 'nut', z=2)
G.cl((0, zc - 2), (0, h1 + 4)); G.cl((ecc, w0 - 6), (ecc, zc + 1)); title(262, 284, '侧剖 x=0 (横 = y)   1.5:1', G)
hdim(pg, G.x(ecc), G.x(0), G.y(w0 - 5), G.y(w0 - 5) - 4, '偏心 ' + F(-ecc), size=2.3)
vchain(pg, [G.y(v) for v in (zr, z1, zc, zc + P['post_fn_h'], zs, zb, bz0, bz1, pt, pt + P['head_h'])], ['筋 3', '绿 5', '螺母沉孔 ' + F(P['post_fn_h']), '隔板 ' + F(P['web']), '外套 ' + F(P['sleeve']), F(bz0 - zb), '695 ' + F(P['brg'][2]), '伸出 ' + F(P['over']), '头 ' + F(P['head_h'])], G.x(27), G.x(30), size=2.3)
lab(G, ecc - 2.5, zc - 1, -22, zc - 8, '中间头沉 2', 'right'); lab(G, -3.2, zc + 3.2, -22, zc + 9, '法兰螺母', 'right'); lab(G, 2.6, zb - 2, 12, zb + 6, f'套 Φ{F(P["bore"])} / 柱 Φ5')

x0, y = 330, 284                                                         # 说明
def notes(hd, L_):
    global y
    pg.text(x0, y, hd, size=3.1, weight='bold'); y -= 4.8
    for t in L_: pg.text(x0, y, t, size=2.35); y -= 4.0
    y -= 2
notes('件号', ['1 绿  屏幕顶长条 led_top_bar (打印)', '2 蓝  螺柱衔接件 post_holder (打印)', '3 紫  M3 螺柱 Φ5×60, 阳牙 6', '4 轴承 695ZZ 5×13×4', '5 中心堵头 glass_top_hub (打印, 改)', '6 配平梳齿 led_comb (打印, 锁孔改 ±21)', '7 旋母 hub_nut (打印, 拧紧夹玻璃)'])
notes('螺丝', ['3× M3×20 超薄头 头 Φ7×1.5 (绿, 左中右)', '2× M3×16 超薄头 (梳齿+蓝+绿)', '   不装梳齿用 M3×12', '1× M3×8 超薄头 (螺柱顶)', '3× M3 法兰螺母 (Φ8 沉孔)', '3× 定位套 Φ8×2 (防螺母转)'])
notes('装配顺序', ['1. 两颗法兰螺母 + 定位套压进绿件底', '2. 绿件放两屏顶, 3 根 M3×20 锁屏', '3. 法兰螺母从蓝件底推到沉孔顶 (深 ' + F(P['post_fn_h']) + '), 再压定位套', '4. 螺柱插进外套, 拧进螺母到肩', '5. 蓝件 (+梳齿) 用 2 根 M3 锁绿件', '6. 堵头穿玻璃孔, 下面旋母拧紧, 整块落上', '7. 695 从堵头顶面按进 (齐平)', '8. 顶螺丝锁螺柱 (压柱端, 不压死轴承)'])
notes('配合', ['外套内 Φ5.2 / 螺柱 Φ5 (单边 0.1)', '695 座 Φ13.0, 顶齐堵头面, 口倒角 0.5', '旋母螺纹径向间隙 0.2', '筋厚 4.6 = 两屏间隙 = 螺母对边', '法兰螺母沉孔 Φ8 (绿 3.7 / 蓝 4.0)'])
frame('顶部连接 第二版 装配', 'POV3D V1.2  (设计区, 未合回主模型)', '数量: 1 套', '顶部连接_装配_2D图')

# ================= 零件 =================
newpage()
T = V(112, 252, 1, 0, ecc, (0, 0)); T.y_top = 25                        # 绿 俯视
vis, hid = hlr([S['led_top_bar']], (0, 0, 1), (1, 0, 0))
for q in hid: T.pl(q, lw=0.12, ls=(0, (4, 2)), color='0.45', z=2)
for q in vis: T.pl(q, lw=0.3, lay='led_top_bar')
T.cl((-bx - 3, ecc), (bx + 3, ecc)); [T.cl((u, ecc - 8), (u, ecc + 9)) for u in (-nx, -fx, fx, nx, 0)]; T.cl((-12, 0), (12, 0)); title(112, 280, '绿 ① led_top_bar  俯视 (虚线 = 底面)   1:1', T)
yb = T.y(ecc - 6); hdim(pg, T.x(-fx), T.x(fx), yb, yb - 4.5, F(2 * fx), size=2.4); hdim(pg, T.x(-nx), T.x(nx), yb, yb - 10.5, F(2 * nx), size=2.4); hdim(pg, T.x(-bx), T.x(bx), yb, yb - 16.5, '总长 ' + F(2 * bx), size=2.6)
vdim(pg, T.y(ecc - by), T.y(ecc + by), T.x(bx), T.x(bx) + 5, F(2 * by), size=2.4); vdim(pg, T.y(ecc - 6), T.y(ecc + 6), T.x(-26), T.x(-34), F(P['pad_w']), size=2.4); vdim(pg, T.y(ecc), T.y(0), T.x(-9), T.x(-12), F(-ecc), size=2.2)
lab(T, 6.4, 6.4, 14, 11, f'Φ{F(P["disc_d"])} (转轴)'); lab(T, fx + 3, ecc + 2.6, 34, 5, f'2× Φ3.4 通 / 底 Φ{F(P["fn_d"])} 深 {F(P["fn_h"])}'); lab(T, -2.5, ecc + 2.5, -20, 9, f'Φ3.4 通 / 顶 Φ{F(P["cb_d"])} 深 {F(P["cb_h"])}', 'right'); lab(T, -nx + 1, ecc + 1.6, -74, 5, '2× 腰孔 4×3.4'.replace('4×', F(P['hole'] + 2 * P['slot']) + '×'))
C = V(112, 208, 1, 0, zr, (0, -60)); C.y_top = 12                       # 绿 y=ecc 剖
for f in sec(S['led_top_bar'], 'y', ecc): C.face(f, COL['led_top_bar'], '////', 'led_top_bar')
title(112, 221, f'绿 剖 y={ecc:g}   1:1', C); vchain(pg, [C.y(v) for v in (zr, z1, zc)], ['筋 ' + F(P['rib_h']), '板 ' + F(P['bar_t'])], C.x(bx), C.x(bx) + 5, size=2.3); hdim(pg, C.x(-P['rib_hx']), C.x(P['rib_hx']), C.y(zr), C.y(zr) - 4.5, '筋长 ' + F(2 * P['rib_hx']), size=2.4)
def endsec(X, Y, at, t, k=3):
    E = V(X, Y, k, ecc, zr, (110, -60 - X / 3)); E.y_top = 12
    for f in sec(S['led_top_bar'], 'x', at): E.face(f, COL['led_top_bar'], '////', 'led_top_bar')
    title(X, E.y(zc) + 9, t, E); return E
E = endsec(38, 160, nx, '绿 剖 x=78.88   3:1'); vchain(pg, [E.y(v) for v in (zr, z1, zc)], ['3', '5'], E.x(ecc + by), E.x(ecc + by) + 5, size=2.3); hdim(pg, E.x(ecc - 2.3), E.x(ecc + 2.3), E.y(zr), E.y(zr) - 4, '筋厚 4.6', size=2.3); hdim(pg, E.x(ecc - by), E.x(ecc + by), E.y(zc), E.y(zc) + 3.5, F(2 * by), size=2.3)
E = endsec(102, 160, fx, '绿 剖 x=21   3:1'); vchain(pg, [E.y(v) for v in (z1, z1 + P['fn_h'], zc)], ['沉孔 ' + F(P['fn_h']), F(P['bar_t'] - P['fn_h'])], E.x(ecc + 6), E.x(ecc + 6) + 5, size=2.3); hdim(pg, E.x(ecc - 4), E.x(ecc + 4), E.y(zr), E.y(zr) - 4, 'Φ8', size=2.3); hdim(pg, E.x(ecc - 6), E.x(ecc + 6), E.y(zc), E.y(zc) + 3.5, F(P['pad_w']), size=2.3)
E = endsec(172, 160, 0, '绿 剖 x=0   3:1'); vchain(pg, [E.y(v) for v in (z1, zc - P['cb_h'], zc)], [F(P['bar_t'] - P['cb_h']), '沉 ' + F(P['cb_h'])], E.x(9), E.x(9) + 5, size=2.3); hdim(pg, E.x(ecc - 3.5), E.x(ecc + 3.5), E.y(zc), E.y(zc) + 3.5, 'Φ7', size=2.3); hchain(pg, [E.x(v) for v in (ecc - 6, ecc, 0, 9)], ['6', F(-ecc), 'R9'], E.y(zr), E.y(zr) - 4, size=2.3)

H = V(74, 62, 1.5, 0, zc, (0, -160)); H.y_top = 34                      # 蓝 阶梯剖
for a, b, yy in ((-9, 9, 0), (-40, -9, ecc), (9, 40, ecc)):
    for f in sec(clipx(S['post_holder'], a, b), 'y', yy): H.face(f, COL['post_holder'], HATCH['post_holder'], 'post_holder')
title(74, 122, '蓝 ② post_holder  阶梯剖 (中 y=0, 两侧 y=-4.69)   1.5:1', H); H.cl((0, zc - 2), (0, zb + 3)); [H.cl((s * fx, zc - 2), (s * fx, zp + 3)) for s in (1, -1)]
vchain(pg, [H.y(v) for v in (zc, zc + P['post_fn_h'], zs, zb)], ['沉孔 ' + F(P['post_fn_h']), '隔板 ' + F(P['web']), '套 ' + F(P['sleeve'])], H.x(10), H.x(29), size=2.3); vdim(pg, H.y(zc), H.y(zb), H.x(-9), H.x(-31), '总高 ' + F(zb - zc), size=2.4); vdim(pg, H.y(zc), H.y(zp), H.x(-27), H.x(-28) - 0.5, F(P['pl_t']), size=2.2)
hchain(pg, [H.x(v) for v in (-4, 4)], ['Φ8'], H.y(zc), H.y(zc) - 4.5, size=2.3); hdim(pg, H.x(-fx), H.x(fx), H.y(zc), H.y(zc) - 10.5, '2× Φ3.4  距 ' + F(2 * fx), size=2.4); hdim(pg, H.x(-7), H.x(7), H.y(zb), H.y(zb) + 4, f'Φ{F(P["boss_d"])} / 内 Φ{F(P["bore"])}', size=2.4); lab(H, 0.8, zs - 1, 14, zs + 9, 'Φ3.4')
U = V(178, 74, 1.5, 0, ecc, (90, -160)); U.y_top = 16                   # 蓝 俯视
for q in hlr([S['post_holder']], (0, 0, 1), (1, 0, 0))[0]: U.pl(q, lw=0.3, lay='post_holder')
U.cl((-30, ecc), (30, ecc)); U.cl((-12, 0), (12, 0)); U.cl((0, -12), (0, 11)); title(172, 112, '蓝 俯视   1.5:1', U)
yb = U.y(ecc - 6); hdim(pg, U.x(-fx), U.x(fx), yb, yb - 5, F(2 * fx), size=2.4); hdim(pg, U.x(-fx - 6), U.x(fx + 6), yb, yb - 11, '全长 ' + F(2 * fx + 12), size=2.4); vdim(pg, U.y(ecc - 6), U.y(ecc + 6), U.x(27), U.x(27) + 5, F(P['pad_w']), size=2.4); vdim(pg, U.y(ecc), U.y(0), U.x(-9), U.x(-16), F(-ecc), size=2.3); lab(U, 6.5, 6.2, 14, 9, f'Φ{F(P["disc_d"])}')

Q = V(300, 205, 2.5, 0, h0, (230, 0)); Q.y_top = 24                     # 堵头 + 旋母 剖
for k in ('hub', 'hub_nut'):
    for f in sec(S[k], 'x', 0): Q.face(f, COL[k], HATCH[k], k)
for a, b in ((-22, -rh), (rh, 22)): Q.box(a, b, g0, g1, COL['glass'], 'glass', z=1.1)
for f in sec(S['brg695'], 'x', 0): Q.face(f, COL['brg695'], 'xxxx', 'brg695', z=1.3, lw=0.15)
Q.cl((0, h0 - 2), (0, h1 + 3)); title(300, 274, '紫 ⑤ 堵头 + 绿 ⑦ 旋母  剖 x=0 (含 695、玻璃)   2.5:1', Q)
hdim(pg, Q.x(-16), Q.x(16), Q.y(h1), Q.y(h1) + 12, 'Φ' + F(P['fl_d']), size=2.4); hdim(pg, Q.x(-P['seat_d'] / 2 - 0.5), Q.x(P['seat_d'] / 2 + 0.5), Q.y(h1), Q.y(h1) + 5, '口倒角 0.5 → Φ' + F(P['seat_d'] + 1), size=2.3)
yb = Q.y(h0); hdim(pg, Q.x(-P['lip_d'] / 2), Q.x(P['lip_d'] / 2), yb, yb - 5, '内孔 Φ' + F(P['lip_d']), size=2.3); hdim(pg, Q.x(-P['th_d'] / 2), Q.x(P['th_d'] / 2), yb, yb - 11, f'外螺纹 大径 Φ{F(P["th_d"])} 小径 Φ{F(P["th_d"] - 2 * P["th_h"])} 螺距 {F(P["th_p"])}', size=2.3); hdim(pg, Q.x(-16), Q.x(16), yb, yb - 17, f'旋母 Φ{F(P["nut_od"])}', size=2.3)
vchain(pg, [Q.y(v) for v in (h0, bz0, bz1)], [F(bz0 - h0), '695 座 4 (Φ13.0, 顶齐盖面)'], Q.x(22), Q.x(22) + 6, size=2.3); vchain(pg, [Q.y(v) for v in (h0, g0, g0 + P['th_up'], g1)], ['旋母 ' + F(P['nut_t']), '螺纹到 ' + F(P['th_up']), f'筒 Φ{F(P["body_d"])}  ' + F(g1 - g0 - P['th_up'])], Q.x(-22), Q.x(-22) - 22, size=2.3)
for X, k, d, t in ((268, 'hub', (0, 0, -1), '堵头 仰视   1.5:1'), (340, 'hub_nut', (0, 0, 1), '旋母 俯视 (12 指槽 R2.5)   1.5:1')):
    Y_ = V(X, 134, 1.5, 0, 0, (X, -80)); Y_.y_top = 18
    for q in hlr([S[k]], d, (1, 0, 0))[0]: Y_.pl(q, lw=0.25, lay=k)
    title(X, 162, t, Y_)
hdim(pg, 340 - 1.5 * (P['th_d'] / 2 + P['th_clr']), 340 + 1.5 * (P['th_d'] / 2 + P['th_clr']), 134 - 24, 134 - 28, f'内螺纹 大径 Φ{F(P["th_d"] + 2 * P["th_clr"])} 小径 Φ{F(P["th_d"] - 2 * P["th_h"] + 2 * P["th_clr"])}', size=2.2)
x0, y = 240, 90
notes('说明', ['绿: 打印时顶面贴床、筋朝上, 不用支撑', '蓝: 板底贴床; Φ8 沉孔顶是桥接 (8 跨), 不用支撑', '堵头: 盖面贴床, 螺纹朝上; 底唇悬 1.25, 不用支撑', '旋母: 平放; 螺纹牙 45 度, 不用支撑; 右旋单头', '梳齿: 只改锁孔 ±10.5 为 ±21, 其余不变 (STL 已出)', '695 座 / 法兰螺母沉孔按 0 间隙 (打印孔偏小时轻压)', f'轴心 (0,0); 屏中面 y={ecc:g}; Z0 = 底盘顶面, 屏顶 Z{z1:.2f}', '绿件两端腰孔 x 向 ±0.3, 中间圆孔定位'])
frame('顶部连接 第二版 零件', 'POV3D V1.2  (设计区, 未合回主模型)', '数量: 各 1', '顶部连接_零件_2D图')
