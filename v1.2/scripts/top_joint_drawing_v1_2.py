"""V1.2 顶部连接组件 A3 2D 图 (11-25 用户「这部分2d图出一个」)。画的是旧基线 (led_top 舌+帽); 先跑 TJ=base top_joint_v1_2.py (写 参数.json + 零件/*.step), 本文件只读这些, 几秒出图。
    cd v1.2/scripts && ../../.venv/bin/python top_joint_drawing_v1_2.py
→ v1.2/顶部连接/顶部连接_2D图.{pdf,dxf} + _preview.png      (DXF 1:1, 按件分层)
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

OUT = Path(__file__).resolve().parents[1] / '顶部连接' / '基线'
J = json.loads((OUT / '参数.json').read_text(encoding='utf-8')); IF, P, D = J['IF'], J['P'], J['D']
def load(k):
    r = STEPControl_Reader(); r.ReadFile(str(OUT / '零件' / f'{k}.step')); r.TransferRoots(); return r.OneShape()
S = {k: load(k) for k in ('led_top', 'led_comb', 'rod', 'brg', 'hub')}
COL = dict(led_top='#DCEAF7', led_comb='#BBD3EC', rod='#DADADA', brg='#BDBDBD', hub='#FBEBB5', glass='#E6F4FA', led='#CFE5D3')
HATCH = dict(led_top='////', led_comb='\\\\\\\\', rod=None, brg='xxxx', hub='////')
ecc, z1, zcap, zc1 = IF['ecc'], IF['z_led'], D['zcap'], D['zc1']
g0, g1, bz1 = IF['z_glass0'], IF['z_glass1'], P['boss_z1']

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

pg = Page(); ax = pg.ax
doc = ezdxf.new('R2010', setup=True); doc.units = 4; msp = doc.modelspace()
for n, c in (('led_top', 5), ('led_comb', 4), ('rod', 8), ('brg', 9), ('hub', 2), ('glass', 150), ('led', 3), ('screw', 1), ('center', 6), ('text', 7)): doc.layers.add(n, color=c)
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
t16 = D['led_t']; gp = IF['gap'] / 2; ZB = IF['tongue_z0'] - 3.0

# ---------- A-A (x=0), 2:1 ----------
A = V(80, 62, 2, 0, ZB, (0, 0)); A.y_top = 330
for a, b in ((ecc + gp, ecc + gp + t16), (ecc - gp - t16, ecc - gp)): A.box(a, b, ZB, z1, COL['led'], 'led')
for sg in (1, -1): A.box(sg * IF['hole_d'] / 2, sg * 23, g0, g1, COL['glass'], 'glass')
for k in ('led_top', 'led_comb', 'hub', 'brg', 'rod'): A.part(k, 'x', 0)
A.cl((0, ZB - 2), (0, D['hub_z1'] + 4)); A.cl((ecc, ZB - 2), (ecc, zcap + 1))
title(80, 278, 'A-A  剖视 (x=0, 横 = y)   2:1', A)
zs = [IF['tongue_z0'], z1, zcap, zc1, D['rod_z0'], bz1, D['hub_z0'], g0, g1, D['brg_z1'], D['hub_z1']]
vchain(pg, [A.y(z) for z in zs], [F(b - a) for a, b in zip(zs, zs[1:])], A.x(8.5), 132)
vdim(pg, A.y(D['rod_z0']), A.y(bz1), A.x(8), 151, '压入 ' + F(bz1 - D['rod_z0'])); vdim(pg, A.y(bz1), A.y(D['brg_z0']), A.x(8), 151, ''); pg.text(149.6, A.y(299), f'悬伸 {F(D["brg_z0"] - bz1)} mm', size=2.8, ha='right', va='center', rot=90, halo=True)
vdim(pg, A.y(z1), A.y(g0), A.x(-11.5), 28, ''); pg.text(26.4, A.y(274), f'灯板上沿到玻璃底 {F(g0 - z1)} mm', size=2.8, ha='right', va='center', rot=90, halo=True); vdim(pg, A.y(IF['tongue_z0']), A.y(D['hub_z1']), A.x(-16.5), 17, ''); pg.text(15.4, A.y(277), f'总高 {F(D["hub_z1"] - IF["tongue_z0"])} mm', size=2.8, ha='right', va='center', rot=90, halo=True)
for z, t in ((D['hub_z1'], '堵头顶'), (bz1, '轴座顶'), (z1, '灯板上沿')): pg.text(A.x(-8.5) - 1, A.y(z) + (1 if z != z1 else -3.2), f'{t} Z{z:.2f}', size=2.3, ha='right', halo=True)
pg.text(A.x(-22.5), A.y(g1) - 3.4, f'玻璃顶 Z{g1:.2f}', size=2.3); pg.text(A.x(-22.5), A.y(g0) + 1, f'玻璃底 Z{g0:.2f}', size=2.3)
yb = A.y(ZB)
hchain(pg, [A.x(v) for v in (ecc - gp - t16, ecc - gp, ecc - P['tongue_t'] / 2, ecc + P['tongue_t'] / 2, ecc + gp, ecc + gp + t16)], [F(t16), F(gp - P['tongue_t'] / 2), '舌厚 ' + F(P['tongue_t']), F(gp - P['tongue_t'] / 2), F(t16)], yb, yb - 4, size=2.1, skip=(1, 3))
hdim(pg, A.x(ecc), A.x(0), A.y(zcap) - 8 * 2 + 4, A.y(zcap) - 8 * 2 - 6, '偏心 ' + F(-ecc), size=2.4)
hdim(pg, A.x(-P['boss_d'] / 2), A.x(P['boss_d'] / 2), A.y(bz1), A.y(bz1) + 7, '轴座 Φ' + F(P['boss_d']), size=2.5)
hdim(pg, A.x(-P['rod_d'] / 2), A.x(P['rod_d'] / 2), A.y(bz1) + 20, A.y(bz1) + 24, '钢轴 Φ' + F(P['rod_d']), size=2.5)
ref(A.x(-4.8), A.y(270), 1, A.x(-16), A.y(273)); ref(A.x(-9.5), A.y(zcap + 2), 2, A.x(-17), A.y(zcap + 8)); ref(A.x(-1.5), A.y(292), 3, A.x(-16), A.y(294))

# ---------- B 详图 (堵头/688/玻璃孔), 3:1 ----------
Bv = V(222, 197, 3, 0, D['hub_z0'], (70, 0)); Bv.y_top = 330
for sg in (1, -1): Bv.box(sg * IF['hole_d'] / 2, sg * 18, g0, g1, COL['glass'], 'glass')
for k in ('hub', 'brg'): Bv.part(k, 'x', 0)
ro = P['rod_d'] / 2; Bv.box(-ro, ro, D['hub_z0'] - 3, D['rod_z1'], COL['rod'], 'rod', z=1.6)
Bv.cl((0, D['hub_z0'] - 4), (0, D['hub_z1'] + 2))
title(222, 278, 'B  详图: 堵头 / 688 / 玻璃孔   3:1', Bv)
rh = IF['hole_d'] / 2; rb = rh + P['barb']; r1 = rh - P['claw_clr']; zc = g0 - P['catch_dz']
zs = [D['hub_z0'], zc - 0.5, zc, g0, g1, D['brg_z1'], D['brg_z1'] + P['relief'][1], D['hub_z1']]
vchain(pg, [Bv.y(z) for z in zs], [F(b - a) for a, b in zip(zs, zs[1:])], Bv.x(18), 281)
vdim(pg, Bv.y(D['brg_z1']), Bv.y(D['rod_z1']), Bv.x(-16.5), 166, '轴伸出 ' + F(D['rod_z1'] - D['brg_z1']), size=2.3)
vdim(pg, Bv.y(D['hub_z0']), Bv.y(g1 - 1), Bv.x(-18.2), 162, '爪槽长\n' + F(g1 - 1 - D['hub_z0']), size=2.3)
hdim(pg, Bv.x(-P['fl_d'] / 2), Bv.x(P['fl_d'] / 2), Bv.y(D['hub_z1']), Bv.y(D['hub_z1']) + 4.5, 'Φ' + F(P['fl_d']), size=2.5)
hdim(pg, Bv.x(-P['brg_d'] / 2), Bv.x(P['brg_d'] / 2), Bv.y(g1 + 2), Bv.y(g1) + 5, '688 窝 Φ' + F(P['brg_d']), size=2.3)
hdim(pg, Bv.x(-P['relief'][0] / 2), Bv.x(P['relief'][0] / 2), Bv.y(D['brg_z1'] + 1), Bv.y(D['brg_z1']) + 9.3, '让位 Φ' + F(P['relief'][0]), size=2.1)
y0 = Bv.y(D['hub_z0'])
for i, (r, t) in enumerate(((P['claw_r0'], '爪内'), (r1, '爪外'), (rh, '玻璃孔'), (rb, '倒钩'))):
    ys = (y0, Bv.y(g0 + 3), Bv.y(g0), Bv.y(zc))[i]; hdim(pg, Bv.x(-r), Bv.x(r), ys, y0 - 5 - 5.2 * i, f'{t} Φ{F(2 * r)}', size=2.3)
ref(Bv.x(-12.5), Bv.y(319), 5, Bv.x(-19.5), Bv.y(326.5)); ref(Bv.x(6.2), Bv.y(317.3), 4, Bv.x(19.5), Bv.y(327))

# ---------- C-C (y = ECC, 过舌 / 锁帽螺丝), 1.5:1 ----------
C = V(238, 114, 1.5, 0, ZB, (170, 0)); C.y_top = 265
zt = 258.0
for k in ('led_top', 'led_comb'):
    for f in sec(S[k], 'y', ecc):
        f = [[(u, min(w, zt)) for u, w in lp] for lp in f]; C.face(f, COL[k], HATCH[k], k)
for sx in (1, -1):                               # M3×8 + 铜螺母
    x = sx * P['comb_fix_x']
    C.face([[(x - 2.1, z1), (x - 2.1, zcap), (x + 2.1, zcap), (x + 2.1, z1)]], '#E3C877', None, 'screw', z=2.5, lw=0.2)
    C.face([[(x - 1.5, zc1 - 8), (x + 1.5, zc1 - 8), (x + 1.5, zc1), (x + 2.75, zc1), (x + 2.75, zc1 + 3), (x - 2.75, zc1 + 3), (x - 2.75, zc1), (x - 1.5, zc1)]], '#EEEEEE', None, 'screw', z=3, lw=0.25)
    C.cl((x, z1 - 2), (x, zc1 + 5))
C.cl((0, ZB), (0, zt + 2)); title(238, 169, f'C-C  剖视 (y={ecc:g} 灯板中面, 横 = x; 轴座截断)   1.5:1', C)
xm = P['comb_teeth'][-1] + P['tooth_w'] / 2
vchain(pg, [C.y(z) for z in (IF['tongue_z0'], z1, zcap, zc1, zc1 + 3)], ['舌 ' + F(z1 - IF['tongue_z0']), '帽 ' + F(zcap - z1), '梳齿 ' + F(zc1 - zcap), '头 3'], C.x(xm), C.x(xm) + 5)
hdim(pg, C.x(-P['tongue_hx']), C.x(P['tongue_hx']), C.y(IF['tongue_z0']), C.y(IF['tongue_z0']) - 5, '舌宽 ' + F(2 * P['tongue_hx']), size=2.3)
hdim(pg, C.x(-P['comb_fix_x']), C.x(P['comb_fix_x']), C.y(z1), C.y(z1) - 6, F(2 * P['comb_fix_x']), size=2.3); hdim(pg, C.x(-P['cap_hx']), C.x(P['cap_hx']), C.y(z1), C.y(z1) - 11.5, '帽长 ' + F(2 * P['cap_hx']), size=2.3)
pg.text(C.x(-48), C.y(z1) - 8, '2×M3×8 内六角 (梳齿→帽)\n帽孔 Φ4.2 压 M3×4 铜螺母\n梳齿孔 Φ3.4', size=2.2, va='center'); ref(C.x(-30), C.y(zcap + 2), 2, C.x(-34), C.y(zc1) + 7)

# ---------- 俯视 (①+②+③), 1.5:1 ----------
T = V(238, 75, 1.5, 0, 0, (170, -60)); T.y_top = 25
vis, _ = hlr([S['led_comb'], S['led_top'], S['rod']], (0, 0, 1), (1, 0, 0))
for q in vis: T.pl(q, lw=0.3, lay='led_comb')
a, b = P['cap_hx'], P['cap_hy']; T.pl([(-a, ecc - b), (a, ecc - b), (a, ecc + b), (-a, ecc + b), (-a, ecc - b)], lw=0.2, ls=(0, (4, 2)), color='0.35', lay='led_top')
circ = lambda r: [(r * math.cos(i * math.pi / 36), r * math.sin(i * math.pi / 36)) for i in range(73)]
T.pl(circ(P['pad_d'] / 2), lw=0.2, ls=(0, (4, 2)), color='0.35', lay='led_top')
T.cl((-xm - 3, 0), (xm + 3, 0)); T.cl((0, ecc - P['tooth_y'] - 2), (0, 14)); T.cl((-xm - 3, ecc), (xm + 3, ecc))
title(238, 100, '俯视 (灰虚线 = 帽 / 圆垫, 在梳齿下)   1.5:1', T)
yb = T.y(ecc - P['tooth_y']); tt = [0] + P['comb_teeth']
hchain(pg, [T.x(v) for v in tt], [F(q - p) for p, q in zip(tt, tt[1:])], yb, yb - 4, size=2.2)
hdim(pg, T.x(-xm), T.x(-xm + P['tooth_w']), yb, yb - 4, '齿宽 ' + F(P['tooth_w']), size=2.2); hdim(pg, T.x(-xm), T.x(0), yb, yb - 7.5, F(xm), size=2.2)
xr = T.x(xm)
sy = [ecc - P['tooth_y'], ecc - 12, ecc - 6.5, ecc, ecc + 6.5, ecc + 12, ecc + P['tooth_y']]
vchain(pg, [T.y(v) for v in sy], [F(q - p) for p, q in zip(sy, sy[1:])], xr, xr + 4.5, size=2.2)
vdim(pg, T.y(ecc), T.y(0), T.x(-xm), T.x(-xm) - 5, '偏心\n' + F(-ecc), size=2.2)
vdim(pg, T.y(ecc - P['comb_beam_y']), T.y(ecc + P['comb_beam_y']), T.x(-xm), T.x(-xm) - 15, '梁宽\n' + F(2 * P['comb_beam_y']), size=2.2)
for (u, w), t, (tx, ty) in (((P['comb_ring'] / 2 * .707, P['comb_ring'] / 2 * .707), f'梳齿环 Φ{F(P["comb_ring"])} / 孔 Φ{F(P["comb_hole"])} (套轴座 Φ{F(P["boss_d"])})', (T.x(13.2), T.y(13.2))),):
    pg.line(T.x(u), T.y(w), tx, ty, lw=0.15); pg.text(tx + 0.6, ty, t, size=2.2, va='center', halo=True)
pg.text(T.x(-xm), T.y(13.2), f'配重孔 Φ3.4 ×{4 * 2 * len(P["comb_teeth"])}', size=2.2, va='center')

# ---------- 堵头仰视, 2:1 ----------
H = V(368, 238, 2, 0, 0, (70, -60)); H.y_top = 25
vis, _ = hlr([S['hub']], (0, 0, -1), (1, 0, 0))
for q in vis: H.pl(q, lw=0.3, lay='hub')
H.cl((-18, 0), (18, 0)); H.cl((0, -18), (0, 18)); title(368, 278, '⑤ 堵头 仰视 (从下看爪)   2:1', H)
hdim(pg, H.x(-P['fl_d'] / 2), H.x(P['fl_d'] / 2), H.y(-8), H.y(-P['fl_d'] / 2) - 5, 'Φ' + F(P['fl_d']), size=2.4)
pg.text(368, H.y(-P['fl_d'] / 2) - 10, f'{P["n_slot"]} 爪, 槽宽 {F(P["slot_w"])} mm, 60° 均布', size=2.4, ha='center')

# ---------- 明细 / 说明 ----------
x0, y = 333, 190
pg.text(x0, y, '明细', size=3.2, weight='bold'); y -= 5
for n, t, m, q in (('1', '灯板顶部件 led_top', 'PETG 打印', 1), ('2', '配平梳齿 led_comb', 'PETG / PLA 打印', 1), ('3', f'钢轴 Φ{F(P["rod_d"])} h6 × {F(P["rod_l"])}', '外购', 1), ('4', '轴承 688ZZ 8×16×5', '外购', 1), ('5', '中心堵头 glass_top_hub', 'PETG 打印', 1),
                   ('', 'M3×8 内六角 + M3×4 铜螺母', '标准件', 2)):
    pg.line(x0, y - 1.2, 408, y - 1.2, lw=0.1); pg.text(x0, y, n, size=2.5); pg.text(x0 + 5, y, t, size=2.5); pg.text(x0 + 46, y, m, size=2.3); pg.text(408, y, f'×{q}', size=2.5, ha='right'); y -= 4.8
y -= 2; pg.text(x0, y, '说明', size=3.2, weight='bold'); y -= 5
for t in (f'坐标: 轴心 (0,0), Z0 = 底盘顶面', f'灯板组中面 y = {ecc:g}; 转轴 / 轴座 / 688 在 (0,0)', f'轴座孔 Φ{F(P["rod_hole"])} 盲孔深 {F(bz1 - D["rod_z0"])}, 压 Φ8 h6 钢轴 (试配)',
          f'舌 {F(2 * P["tongue_hx"])}×{F(P["tongue_t"])}×{F(z1 - IF["tongue_z0"])} 插两灯板之间 (间隙 {F(IF["gap"])}),', '   单边余 0.1, 无螺丝', f'帽 {F(2 * P["cap_hx"])}×{F(2 * P["cap_hy"])}×{F(P["cap_t"])} + 圆垫 Φ{F(P["pad_d"])} (托轴座, 同厚)',
          f'玻璃 (参考): 厚 {F(IF["glass_t"])}, 孔 Φ{F(IF["hole_d"])}; 管端 Z{IF["z_tube"]:.2f}', f'轴顶过冲余量 {F(D["brg_z1"] + P["relief"][1] - D["rod_z1"])}', '灯板厚按 1.6 画 (绿), 玻璃浅蓝, 均为邻件', 'DXF 同名文件: 1:1, 按件分层'):
    pg.text(x0, y, ('· ' if not t.startswith(' ') else '') + t, size=2.3); y -= 3.7
pg.rect(5, 5, 415, 292, lw=0.4); tb = (10, 10, 410, 34); pg.rect(*tb, lw=0.35); pg.line(10, 22, 410, 22, lw=0.2)
for xx in (130, 200, 270, 330): pg.line(xx, 10, xx, 34, lw=0.2)
pg.text(14, 26, '顶部连接组件 (屏幕顶 - 圆环玻璃)', size=4.2, weight='bold'); pg.text(14, 14.5, 'POV3D V1.2  装配 2D 图 (现行件基线)', size=2.9)
pg.text(134, 26, '件数: 5 + 标准件', size=2.9); pg.text(134, 14.5, '材料: 见明细', size=2.9); pg.text(204, 26, '比例: 各视图旁注', size=2.9); pg.text(204, 14.5, '单位 mm / 第一角', size=2.9)
pg.text(274, 26, time.strftime('%Y-%m-%d'), size=2.9); pg.text(274, 14.5, 'A3 (420×297)', size=2.9); pg.text(334, 26, 'top_joint_drawing_v1_2.py', size=2.6); pg.text(334, 14.5, '剖视 = B-rep 精确剖切', size=2.6)
try: png = pg.save(OUT / '顶部连接_2D图.pdf')
except PermissionError: png = pg.save(OUT / '顶部连接_2D图.NEW.pdf')
try: doc.saveas(OUT / '顶部连接_2D图.dxf')
except PermissionError: doc.saveas(OUT / '顶部连接_2D图.NEW.dxf')
print(png)
