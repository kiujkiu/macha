"""V1.2 顶部连接 第二版 (11-25 19:34 用户三张图): 绿 = 5 厚长条 led_top_bar / 蓝 = 衔接件 post_holder / 紫 = M3 螺柱 Φ5×60 (阳 6) / 695ZZ / 顶螺丝。
设计区: 接口只读主模型 (build_v1_2 / led_support_v1_2), 不改主模型。前一版 (Φ8 压轴 + 688) = top_joint_v1_2.py (TJ=base 出基线)。
锁法: 绿件 ← 3 根 M3×20 (左/右头在板顶, 中间头沉进板顶) 各穿两颗铜螺母 (两屏交错); 蓝件 ← 2 根 M3 从上往下, 法兰螺母从绿件底沉孔塞 (法兰朝上);
      螺柱阳牙穿蓝件 2 厚隔板, 拧蓝件底沉孔里的法兰螺母, 外套 Φ5.2 扶正; 顶端 695ZZ 从堵头上口放入, 顶螺丝压螺柱端面。
    cd v1.2/scripts && ../../.venv/bin/python top_stack_v1_2.py      # ~2 分钟
"""
import io, contextlib, math, json, time, struct
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import led_support_v1_2 as L
from mf3_v1_2 import mesh, write3mf
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakePolygon
from OCP.BRepLib import BRepLib
from OCP.Geom import Geom_CylindricalSurface
from OCP.Geom2d import Geom2d_Line
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax3, gp_Pnt2d, gp_Dir2d
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
cyl, gbox, cut, fuse, clean, xf, rotz, vol, revol = B.cyl, B.gbox, B.cut, B.fuse, B.clean, B.xf, B.rotz, B.vol, B.revol
OUT = B.V12 / '顶部连接'; (OUT / '零件').mkdir(parents=True, exist_ok=True)
IF = dict(z_led=L.Z1, ecc=L.ECC, gap=4.6, z_glass0=B.GD_Z0, z_glass1=B.GD_Z1, hole_d=B.GD_ID, glass_t=B.GD_T)
DY = (2 * L.GAP_HALF - IF['gap']) / 2            # 本设计区两屏间隙 4.6 (主模型 5.0), 中面不动
P = dict(bar_t=5.0, bar_hx=83.0, bar_hy=4.5, rib_t=4.6, rib_h=3.0, rib_hx=81.5, hole=3.4, slot=0.3, nut_x=L.SO_X, nut_af=L.SO_AF, nut_l=L.SO_L,
         scr_l=20.0, head_d=7.0, head_h=1.5, cb_d=7.0, cb_h=2.0,                                # 长条 3 根 M3×20 超薄头; 中间沉孔 Φ7×2
         fx=21.0, pad_w=12.0, disc_d=18.0, fn_d=8.0, fn_h=3.7, fn_fl=7.6, fn_af=5.5,            # 蓝件锁点 ±21 / 圆端条宽 / 中央圆 / 法兰螺母沉孔
         pl_t=6.0, web=2.0, post_fn_h=4.0, bore=5.2, boss_d=14.0, sleeve=20.0,                   # 蓝件: 底板 / 隔板 / 螺柱螺母沉孔深 / 外套内径 / 外径 / 套长
         post_d=5.0, post_l=60.0, post_m=6.0, over=0.5, brg=(5.0, 13.0, 4.0), top_scr=8.0,       # 螺柱 / 伸出轴承 / 695ZZ / 顶螺丝 M3×8
         fix_l=16.0, comb_t=4.0, comb_hole=14.2, comb_ring=22.0, comb_beam_y=4.0, comb_teeth=[16.0, 26.0, 36.0, 46.0], tooth_w=6.0, tooth_y=15.0, slots_y=[6.5, 12.0],
         fl_d=32.0, fl_t=3.0, body_d=19.6, seat_d=13.0, well_d=13.4, lip_d=10.5,                 # 堵头: 盖 / 过玻璃孔的筒 / 695 座 / 放入口 / 底唇孔 (通到底)
         th_d=19.4, th_p=2.5, th_h=0.8, th_flat=0.45, th_clr=0.2, th_up=1.5, nut_t=7.0, nut_od=32.0, n_grip=12, grip_d=5.0, seat_gap=0.0)   # 11-25 21:42 用户「不能用卡扣, 能做螺纹吗, 下边一个件旋转卡住」
WIN = dict(top=(L.Z0 + 166 + 27.97375, L.Z0 + 166 + 37.97375), mid=L.SO_WIN_MID_Z, bot=L.SO_WIN_Z)
z1, ecc = IF['z_led'], IF['ecc']; zc = z1 + P['bar_t']; zp = zc + P['pl_t']; zs = zc + P['post_fn_h'] + P['web']; zb = zs + P['sleeve']
pt = zs + P['post_l']; bz1 = pt - P['over']; bz0 = bz1 - P['brg'][2]; g0, g1 = IF['z_glass0'], IF['z_glass1']; zt = zp + P['comb_t']
NUTS = []
for row, (w0, w1) in WIN.items():
    for bd, sy in (('A', 1), ('B', -1)):
        for col, sx in (('-x', -1), ('0', 0), ('+x', 1)):
            if col == '0' and row == 'mid': continue
            low = ((sx < 0) == (bd == 'A')) if sx else bd == 'A'
            NUTS.append((bd, row, col, sx * P['nut_x'], ecc, w0 if low else w0 + P['nut_l']))
SX = [-P['nut_x'], 0.0, P['nut_x']]

def slot_x(x, y, d, h, a, b): return fuse(gbox(x - h, y - d / 2, a, x + h, y + d / 2, b), cyl(x - h, y, d, a, b), cyl(x + h, y, d, a, b))
def hexp(x, y, af, a, b):
    s = cyl(x, y, af * 1.3, a, b)
    for k in range(3): s = BRepAlgoAPI_Common(s, xf(xf(gbox(-af / 2, -af, a, af / 2, af, b), rotz(60 * k)), L.tr(x, y, 0))).Shape()
    return s
def fnut(x, y, z_top): return cut(fuse(cyl(x, y, P['fn_fl'], z_top - 1.0, z_top), hexp(x, y, P['fn_af'], z_top - P['fn_h'], z_top - 0.99)), cyl(x, y, 2.9, z_top - 9, z_top + 1))      # 法兰朝上
def pad(a, b):                                   # 绿件加宽区 = 蓝件底板外形: 圆端条 (中面) + 中央圆 (转轴)
    w = P['pad_w']; return fuse(gbox(-P['fx'], ecc - w / 2, a, P['fx'], ecc + w / 2, b), cyl(-P['fx'], ecc, w, a, b), cyl(P['fx'], ecc, w, a, b), cyl(0, 0, P['disc_d'], a, b))
def led_top_bar():
    s = fuse(xf(gbox(-P['bar_hx'], -P['bar_hy'], z1, P['bar_hx'], P['bar_hy'], zc), L.tr(0, ecc, 0)), xf(gbox(-P['rib_hx'], -P['rib_t'] / 2, z1 - P['rib_h'], P['rib_hx'], P['rib_t'] / 2, z1 + 0.01), L.tr(0, ecc, 0)), pad(z1, zc))
    for x in SX: s = cut(s, slot_x(x, ecc, P['hole'], P['slot'], z1 - 9, zc + 1) if x else cyl(x, ecc, P['hole'], z1 - 9, zc + 1))
    s = cut(s, cyl(0, ecc, P['cb_d'], zc - P['cb_h'], zc + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['fx'], ecc, P['hole'], z1 - 9, zc + 1), cyl(sx * P['fx'], ecc, P['fn_d'], z1 - 9, z1 + P['fn_h']))
    return clean(s)
def post_holder():
    s = fuse(pad(zc, zp), cyl(0, 0, P['boss_d'], zp - 0.01, zb))
    s = cut(s, cyl(0, 0, P['bore'], zs, zb + 1), cyl(0, 0, P['hole'], zc - 1, zs + 1), cyl(0, 0, P['fn_d'], zc - 1, zc + P['post_fn_h']))
    for sx in (1, -1): s = cut(s, cyl(sx * P['fx'], ecc, P['hole'], zc - 1, zp + 1))
    return clean(s)
def comb():
    xm = P['comb_teeth'][-1] + P['tooth_w'] / 2; w, ty = P['tooth_w'] / 2, P['tooth_y']; s = gbox(-xm, -P['comb_beam_y'], zp, xm, P['comb_beam_y'], zt)
    for sx in (1, -1):
        for t in P['comb_teeth']: s = fuse(s, gbox(sx * t - w, -ty, zp, sx * t + w, ty, zt))
    s = cut(fuse(cyl(0, 0, P['comb_ring'], zp, zt), xf(s, L.tr(0, ecc, 0))), cyl(0, 0, P['comb_hole'], zp - 1, zt + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['fx'], ecc, P['hole'], zp - 1, zt + 1))
    return clean(cut(s, *[cyl(sx * t, ecc + sy * y, 3.4, zp - 1, zt + 1) for sx in (1, -1) for t in P['comb_teeth'] for y in P['slots_y'] for sy in (1, -1)]))
def coil(r0, r1, w0, w1, p, z0, n):                # 梯形螺旋体: 根半径 r0 (埋入) 处轴向宽 w0, 顶 r1 处宽 w1; n 圈
    ln = Geom2d_Line(gp_Pnt2d(0, z0), gp_Dir2d(2 * math.pi, p)); cs = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), r0)
    e = BRepBuilderAPI_MakeEdge(ln, cs, 0, n * math.hypot(2 * math.pi, p)).Edge(); BRepLib.BuildCurves3d_s(e); wire = BRepBuilderAPI_MakeWire(e).Wire()
    pl = BRepBuilderAPI_MakePolygon()
    for r, z in ((r0, z0 - w0 / 2), (r1, z0 - w1 / 2), (r1, z0 + w1 / 2), (r0, z0 + w0 / 2)): pl.Add(gp_Pnt(r, 0, z))
    pl.Close(); m = BRepOffsetAPI_MakePipeShell(wire); m.SetMode(gp_Dir(0, 0, 1)); m.Add(pl.Wire()); m.Build(); m.MakeSolid(); return m.Shape()
def fz(K, a, b):                                  # 带容差布尔 (螺旋面不带容差会丢牙, 体积断言把关)
    o = K(a, b); o.SetFuzzyValue(1e-5); o.Build(); return o.Shape()
def thread(g, z0, z1_):                           # 外螺纹实体 (g = 放大量, 内螺纹刀用): 牙顶 r = th_d/2+g, 牙底 r = 顶 - th_h, 根埋 0.1
    ro = P['th_d'] / 2 + g; ri = ro - P['th_h']; e = 0.1; h = P['th_h']; p = P['th_p']; wt = P['th_flat'] + 2 * g * (math.sqrt(2) - 1); assert wt + 2 * (h + e) < p, '牙根自交'
    core = cyl(0, 0, 2 * ri, z0, z1_); box = cyl(0, 0, 60, z0, z1_); f = core; per = 0.5        # 半圈一段, 逐段并 (整条螺旋一次并不稳)
    seg = coil(ri - e, ro, wt + 2 * (h + e), wt, p, 0, per + 1e-3)
    for k in range(int((z1_ - z0) / p / per) + 14):
        q = BRepAlgoAPI_Common(xf(xf(seg, rotz(360 * per * k)), L.tr(0, 0, ZT0 - 3 * p + p * per * k)), box).Shape()
        if q is not None and vol(q) > 1e-4: f = BRepAlgoAPI_Fuse(f, q).Shape()
    th = (wt + h) * h * 2 * math.pi * (ri + 0.45 * h) / p * (z1_ - z0); v = vol(f) - vol(core); assert abs(v / th - 1) < 0.05, f'牙体积 {v:.1f} 理论 {th:.1f}'
    return f
ZT0 = g0 - P['nut_t']                             # 筒底 = 旋母底
def hub():                                        # 圆环玻璃中心堵头 (紫): 盖 + 筒 + 外螺纹; 695 从上口放入, 底唇托外圈
    ft = P['fl_t']; rf = P['fl_d'] / 2; zu = g0 + P['th_up']; rt = P['th_d'] / 2; ri = rt - P['th_h']
    t = fz(BRepAlgoAPI_Cut, thread(0, ZT0, zu + 0.01), revol([(ri - 0.2, ZT0 - 1), (rt + 5, ZT0 - 1), (rt + 5, ZT0 + P['th_h'] + 5.2), (rt, ZT0 + P['th_h'] + 0.2), (ri - 0.2, ZT0)]))
    s = fuse(t, cyl(0, 0, P['body_d'], zu, g1 + 0.01), revol([(0, g1), (rf, g1), (rf, g1 + ft - 1), (rf - 1, g1 + ft), (0, g1 + ft)]))
    return cut(s, cyl(0, 0, P['lip_d'], ZT0 - 1, g1 + ft + 1), cyl(0, 0, P['seat_d'], bz0, bz1 + 0.01), cyl(0, 0, P['well_d'], bz1, g1 + ft + 1)), ZT0, g1 + ft
def hub_nut():                                    # 旋母 (绿): 玻璃下面拧紧夹玻璃, 外圆 12 个指槽
    g = P['th_clr']; r = P['nut_od'] / 2; ro = P['th_d'] / 2 + g; bl = cyl(0, 0, P['nut_od'], ZT0, g0); c = thread(g, ZT0 - 1, g0 + 1)
    s = fz(BRepAlgoAPI_Cut, bl, c); v0 = vol(bl) - vol(s); ref = L.common_v(bl, c); assert abs(v0 - ref) < 2 and v0 > math.pi * (ro - P['th_h']) ** 2 * P['nut_t'] + 150, (v0, ref)
    for a, sg in ((ZT0, 1), (g0, -1)): s = cut(s, revol([(0, a - sg), (ro + 0.13, a - sg), (ro + 0.13, a), (ro - 0.87, a + sg), (0, a + sg)]))
    return cut(s, *[cyl((r + 1.2) * math.cos(2 * math.pi * k / P['n_grip']), (r + 1.2) * math.sin(2 * math.pi * k / P['n_grip']), P['grip_d'], ZT0 - 1, g0 + 1) for k in range(P['n_grip'])])
bar, hold, comb_s = led_top_bar(), post_holder(), comb(); hub_s, h0, h1 = hub(); hnut = hub_nut()
post = cut(fuse(cyl(0, 0, P['post_d'], zs, pt), cyl(0, 0, 3.0, zs - P['post_m'], zs + 0.01)), cyl(0, 0, 2.5, pt - 10, pt + 1))
brg = cut(cyl(0, 0, P['brg'][1], bz0, bz1), cyl(0, 0, P['brg'][0], bz0 - 1, bz1 + 1))
def scr(x, y, zh, l): return fuse(cyl(x, y, P['head_d'], zh, zh + P['head_h']), cyl(x, y, 3.0, zh - l, zh + 0.01))
SCR = [(f'M3×{P["scr_l"]:g} 长条 x{x:+.2f}', scr(x, ecc, zc - (0 if x else P['cb_h']), P['scr_l'])) for x in SX] + [(f'M3×{P["fix_l"]:g} 蓝件 x{sx * P["fx"]:+g}', scr(sx * P['fx'], ecc, zt, P['fix_l'])) for sx in (1, -1)] + [(f'M3×{P["top_scr"]:g} 顶', scr(0, 0, pt, P['top_scr']))]
FN = [(f'法兰螺母 绿件底 x{sx * P["fx"]:+g}', fnut(sx * P['fx'], ecc, z1 + P['fn_h'])) for sx in (1, -1)] + [('法兰螺母 蓝件底', fnut(0, 0, zc + P['post_fn_h']))]
NS = [(f'铜螺母 板{n[0]} {n[1]} {n[2]}', L.standoff(n[3], n[4], n[5])) for n in NUTS]
PARTS = [('① 绿 屏幕顶长条 led_top_bar', 'led_top_bar', bar, '#6AA84F'), ('② 蓝 螺柱衔接件 post_holder', 'post_holder', hold, '#3D85C6'), ('③ 紫 螺柱 M3 Φ5×60 阳6', 'post', post, '#8E5BA6'),
         ('④ 695ZZ', 'brg695', brg, '#555555'), ('⑤ 中心堵头 glass_top_hub', 'hub', hub_s, '#F1C232'), ('⑦ 旋母 hub_nut', 'hub_nut', hnut, '#38A169'), ('⑥ 配平梳齿 led_comb', 'led_comb', comb_s, '#76A5AF')]
sh = lambda s, dy: xf(s, L.tr(0, dy, 0))
REF = [('灯板 A', sh(L.led_a, -DY), '#145A32'), ('灯板 B', sh(L.led_b, DY), '#0E3B22'), ('圆环玻璃', B.glass_disc, '#BFE3F2'), ('红件', B.glass_top, '#D9534F'), ('绿压环', B.glass_top_clamp, '#93C47D'), ('玻璃罩', B.tube, '#A9CCE3'), ('管内弧形件', L.comp(B.glass_top_lugs), '#E69138'), ('夹条 led_bar', L.bar_s, '#999999')]
R2 = lambda v: round(v, 2)
print('Z: 屏顶', R2(z1), '绿顶', R2(zc), '蓝板顶', R2(zp), '螺柱肩', R2(zs), '外套顶', R2(zb), '695', R2(bz0), R2(bz1), '螺柱顶', R2(pt), '顶螺丝头顶', R2(pt + 1.5), '堵头', R2(h0), R2(h1), '玻璃', g0, g1)
for n, k, s, _ in PARTS: print('  ', n, R2(vol(s)), BRepCheck_Analyzer(s).IsValid())
A = [(n, s) for n, _, s, _ in PARTS] + SCR + FN + NS; INT = []
for i, (n, s) in enumerate(A):
    for m, t in A[i + 1:] + ([(r[0], r[1]) for r in REF] if not n.startswith('铜螺母') else []):
        v = L.common_v(s, t)
        if v > 1e-2: INT.append((n, m, R2(v)))
for q in INT: print('  干涉', *q)
for n, s in NS:
    v = L.common_v(s, L.bar_s)
    if v > 1e-2: print('  铜螺母×夹条', n, R2(v))
d = lambda a, b: R2(BRepExtrema_DistShapeShape(a, b).Value())
print('间隙: 外套↔螺柱', d(hold, post), '绿件↔铜螺母', min(d(bar, s) for n, s in NS if 'top' in n), '梳齿↔蓝', d(comb_s, hold), '堵头↔玻璃', d(hub_s, B.glass_disc), '外套顶↔堵头', d(hold, hub_s), '中螺丝头↔蓝件螺母', d(SCR[1][1], FN[2][1]))
I = math.pi * (P['post_d'] ** 4) / 64; k = lambda a: 3 * 2e5 * I / a ** 3
bm = (bz0 + bz1) / 2
print('旋母×堵头 重叠', R2(L.common_v(hnut, hub_s)), '错半螺距重叠 (须 >0)', R2(L.common_v(xf(hnut, L.tr(0, 0, -P['th_p'] / 2)), hub_s)), '外牙体积', R2(vol(cut(hub_s, cyl(0, 0, P['th_d'] - 2 * P['th_h'], 0, 400))) - vol(cut(cut(hub_s, cyl(0, 0, P['th_d'] - 2 * P['th_h'], 0, 400)), cyl(0, 0, 60, 0, g0)))), '螺纹间隙', d(cut(hnut, cyl(0, 0, 60, g0 - 1.5, g0 + 1)), cut(hub_s, cyl(0, 0, 60, g0, g1 + 9))), '旋母↔蓝套', d(hnut, hold)); print(f'螺柱 10N 挠度: 套内不碰 {10 / k(bm - zs):.3f}, 从套口起 {10 / k(bm - zb):.3f}; 套内倾斜上限在轴承处 {(P["bore"] - P["post_d"]) / P["sleeve"] * (bm - zs):.2f}')
def stl(s, f, flip, z):
    V, T = mesh(s, 0.02); V = V * np.array([1, -1, -1]) if flip else V.copy(); V[:, 2] -= V[:, 2].min()
    with open(OUT / '零件' / f, 'wb') as fh:
        fh.write(f.encode().ljust(80, b' ') + struct.pack('<I', len(T)))
        for t in T:
            q = V[t]; n = np.cross(q[1] - q[0], q[2] - q[0]); n = n / (np.linalg.norm(n) + 1e-12); fh.write(struct.pack('<12fH', *n, *q.ravel(), 0))
for n, k_, s, c in PARTS: w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(OUT / '零件' / f'{k_}.step'))
stl(bar, 'led_top_bar_print.stl', True, 0); stl(hold, 'post_holder_print.stl', False, 0); stl(hub_s, 'glass_top_hub_print.stl', True, 0); stl(hnut, 'hub_nut_print.stl', False, 0); stl(comb_s, 'led_comb_print.stl', False, 0)
write3mf(str(OUT / '顶部连接.3mf'), [(n, s, c, 0.03) for n, _, s, c in PARTS] + [(n, s, '#C0C0C0', 0.03) for n, s in SCR] + [(n, s, '#E69138', 0.03) for n, s in FN] + [(n, s, '#B8860B', 0.03) for n, s in NS] + [(n, s, c, 0.08) for n, s, c in REF[:5]])
D = dict(zc=zc, zp=zp, zs=zs, zb=zb, pt=pt, bz0=bz0, bz1=bz1, h0=h0, h1=h1, zt=zt, led_t=1.6)
(OUT / '参数.json').write_text(json.dumps(dict(IF=IF, P=P, D=D, NUTS=NUTS, WIN=WIN), ensure_ascii=False, indent=1), encoding='utf-8')
M = ['# V1.2 顶部连接 第二版', '', f'由 `v1.2/scripts/top_stack_v1_2.py` 生成 ({time.strftime("%Y-%m-%d %H:%M")}); 主模型未改。', '', '## Z', *[f'- {a}: {b:.2f}' for a, b in (('屏顶', z1), *D.items())], '', '## 重叠 (mm³; 螺纹、压装、占位块为预期)', *[f'- {a} × {b}: {v}' for a, b, v in INT]]
(OUT / '接口与校核.md').write_text('\n'.join(M) + '\n', encoding='utf-8')
