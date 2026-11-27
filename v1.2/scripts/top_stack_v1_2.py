"""V1.2 顶部连接 第二版 (11-25 19:34 用户三张图; 11-27 顶部改亚克力 8: 堵头/旋母/695 → 亚克力 Ø200×8 中心孔 + MR105 + 顶盖 top_cap, 均读主模型): 绿 = 5 厚长条 led_top_bar / 蓝 = 衔接件 post_holder / 紫 = M3 螺柱 Φ5×60 (阳 6) / 695ZZ / 顶螺丝。
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
IF = dict(z_led=L.Z1, ecc=L.ECC, gap=4.6, z_glass0=B.GD_Z0, z_glass1=B.GD_Z1, hole_d=B.GD_ID, glass_t=B.GD_T, ac_bore=B.AC_BORE, ac_sh=B.AC_SHOULDER, mr0=B.MR_Z0, mr1=B.MR_Z1, post_top=B.AC_POST_TOP)   # 11-27 亚克力 (GT_ACR=1)
DY = (2 * L.GAP_HALF - IF['gap']) / 2            # 本设计区两屏间隙 4.6 (主模型 5.0), 中面不动
P = dict(bar_t=5.0, bar_hx=83.0, bar_hy=4.5, rib_t=4.6, rib_h=3.0, rib_hx=81.5, hole=3.4, slot=0.3, nut_x=L.SO_X, nut_af=L.SO_AF, nut_l=L.SO_L,
         scr_l=20.0, head_d=7.0, head_h=1.5, cb_d=7.0, cb_h=2.0,                                # 长条 3 根 M3×20 超薄头; 中间沉孔 Φ7×2
         fx=21.0, pad_w=12.0, disc_d=18.0, fn_d=8.0, fn_h=3.7, fn_fl=7.6, fn_af=5.5,            # 蓝件锁点 ±21 / 圆端条宽 / 中央圆 / 法兰螺母沉孔
         pl_t=6.0, web=2.0, post_fn_h=10.07, bore=5.2, boss_d=17.0, sleeve=10.0, hfn_d=11.0,                   # 蓝件: 底板 / 隔板 / 螺柱螺母沉孔深 / 外套内径 / 外径 / 套长
         post_d=5.0, post_l=None, post_m=6.0, over=0.5, brg=(5.0, 10.0, 3.0), top_scr=8.0,       # 螺柱 (长度由 Z 算) / 伸出轴承 / MR105ZZ / 顶螺丝 M3×8
         fix_l=16.0, comb_t=4.0, comb_hole=17.2, comb_ring=25.0, comb_beam_y=4.0, comb_teeth=[16.0, 26.0, 36.0, 46.0], tooth_w=6.0, tooth_y=15.0, slots_y=[6.5, 12.0],
         )   # 11-27 亚克力方案: 删堵头/旋母/螺纹参数 (fl_*/body_d/seat_d/lip_d/th_*/nut_*), 旧版见 git b66ff23
WIN = dict(top=(L.Z0 + 166 + 27.97375, L.Z0 + 166 + 37.97375), mid=L.SO_WIN_MID_Z, bot=L.SO_WIN_Z)
# 11-26 用户「轴承位置太深了，我放不进去」: 695 顶面 = 堵头顶面 (原低 6.07) ⇒ 螺柱整体抬 6.07, 蓝件底螺母沉孔由 4 加深 (螺母仍贴隔板)
z1, ecc = IF['z_led'], IF['ecc']; g0, g1 = IF['z_glass0'], IF['z_glass1']; zc = z1 + P['bar_t']; zp = zc + P['pl_t']
# 11-27 亚克力: 蓝件不动 (螺柱肩 = 绿顶 + 沉孔 10.07 + 隔板 2), 螺柱顶 = 主模型 AC_POST_TOP (伸出 MR105 0.5) ⇒ 螺柱长度跟着算
bz0, bz1, pt = IF['mr0'], IF['mr1'], IF['post_top']; zs = zc + P['post_fn_h'] + P['web']; P['post_l'] = round(pt - zs, 2); zb = zs + P['sleeve']; zt = zp + P['comb_t']
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
    s = cut(s, cyl(0, 0, P['bore'], zs, zb + 1), cyl(0, 0, P['hole'], zc - 1, zs + 1), cyl(0, 0, P['hfn_d'], zc - 1, zc + P['post_fn_h']))   # 11-26 用户: 沉孔 Φ8→Φ11 (套筒能进), 外套 Φ14→Φ17 保壁厚 3
    for sx in (1, -1): s = cut(s, cyl(sx * P['fx'], ecc, P['hole'], zc - 1, zp + 1))
    return clean(s)
def comb():
    xm = P['comb_teeth'][-1] + P['tooth_w'] / 2; w, ty = P['tooth_w'] / 2, P['tooth_y']; s = gbox(-xm, -P['comb_beam_y'], zp, xm, P['comb_beam_y'], zt)
    for sx in (1, -1):
        for t in P['comb_teeth']: s = fuse(s, gbox(sx * t - w, -ty, zp, sx * t + w, ty, zt))
    s = cut(fuse(cyl(0, 0, P['comb_ring'], zp, zt), xf(s, L.tr(0, ecc, 0))), cyl(0, 0, P['comb_hole'], zp - 1, zt + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['fx'], ecc, P['hole'], zp - 1, zt + 1))
    return clean(cut(s, *[cyl(sx * t, ecc + sy * y, 3.4, zp - 1, zt + 1) for sx in (1, -1) for t in P['comb_teeth'] for y in P['slots_y'] for sy in (1, -1)]))
bar, hold, comb_s = led_top_bar(), post_holder(), comb()
post = cut(fuse(cyl(0, 0, P['post_d'], zs, pt), cyl(0, 0, 3.0, zs - P['post_m'], zs + 0.01)), cyl(0, 0, 2.5, pt - 10, pt + 1))
brg = cut(cyl(0, 0, P['brg'][1], bz0, bz1), cyl(0, 0, P['brg'][0], bz0 - 1, bz1 + 1))
def scr(x, y, zh, l): return fuse(cyl(x, y, P['head_d'], zh, zh + P['head_h']), cyl(x, y, 3.0, zh - l, zh + 0.01))
SCR = [(f'M3×{P["scr_l"]:g} 长条 x{x:+.2f}', scr(x, ecc, zc - (0 if x else P['cb_h']), P['scr_l'])) for x in SX] + [(f'M3×{P["fix_l"]:g} 蓝件 x{sx * P["fx"]:+g}', scr(sx * P['fx'], ecc, zt, P['fix_l'])) for sx in (1, -1)] + [(f'M3×{P["top_scr"]:g} 顶', scr(0, 0, pt, P['top_scr']))]
FN = [(f'法兰螺母 绿件底 x{sx * P["fx"]:+g}', fnut(sx * P['fx'], ecc, z1 + P['fn_h'])) for sx in (1, -1)] + [('法兰螺母 蓝件底', fnut(0, 0, zc + P['post_fn_h']))]
NS = [(f'铜螺母 板{n[0]} {n[1]} {n[2]}', L.standoff(n[3], n[4], n[5])) for n in NUTS]
PARTS = [('① 绿 屏幕顶长条 led_top_bar', 'led_top_bar', bar, '#6AA84F'), ('② 蓝 螺柱衔接件 post_holder', 'post_holder', hold, '#3D85C6'), (f'③ 紫 螺柱 M3 Φ5×{P["post_l"]:g} 阳6', 'post', post, '#8E5BA6'),
         ('④ MR105ZZ', 'mr105', brg, '#555555'), ('⑥ 配平梳齿 led_comb', 'led_comb', comb_s, '#76A5AF')]
sh = lambda s, dy: xf(s, L.tr(0, dy, 0))
REF = [('灯板 A', sh(L.led_a, -DY), '#145A32'), ('灯板 B', sh(L.led_b, DY), '#0E3B22'), ('亚克力 Ø200×8', B.acrylic, '#BFE3F2'), ('顶盖 top_cap', B.top_cap, '#F1C232'), ('外卡环 glass_top_ring', B.glass_top_ring, '#D9534F'), ('玻璃罩', B.tube, '#A9CCE3'), ('管内弧形件', L.comp(B.glass_top_lugs), '#E69138'), ('夹条 led_bar', L.bar_s, '#999999')]
R2 = lambda v: round(v, 2)
print('Z: 屏顶', R2(z1), '绿顶', R2(zc), '蓝板顶', R2(zp), '螺柱肩', R2(zs), '外套顶', R2(zb), 'MR105', R2(bz0), R2(bz1), '螺柱顶', R2(pt), '顶螺丝头顶', R2(pt + 1.5), '亚克力', g0, g1, '螺柱长', P['post_l'])
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
print('间隙: 外套↔螺柱', d(hold, post), '绿件↔铜螺母', min(d(bar, s) for n, s in NS if 'top' in n), '梳齿↔蓝', d(comb_s, hold), '螺柱↔亚克力', d(post, B.acrylic), 'MR105↔亚克力', d(brg, B.acrylic), '顶螺丝↔顶盖', d(SCR[-1][1], B.top_cap), '外套顶↔亚克力底', R2(g0 - zb), '中螺丝头↔蓝件螺母', d(SCR[1][1], FN[2][1]))
I = math.pi * (P['post_d'] ** 4) / 64; k = lambda a: 3 * 2e5 * I / a ** 3
bm = (bz0 + bz1) / 2
print(f'螺柱 10N 挠度: 套内不碰 {10 / k(bm - zs):.3f}, 从套口起 {10 / k(bm - zb):.3f}; 套内倾斜上限在轴承处 {(P["bore"] - P["post_d"]) / P["sleeve"] * (bm - zs):.2f}')
def stl(s, f, flip, z):
    V, T = mesh(s, 0.02); V = V * np.array([1, -1, -1]) if flip else V.copy(); V[:, 2] -= V[:, 2].min()
    with open(OUT / '零件' / f, 'wb') as fh:
        fh.write(f.encode().ljust(80, b' ') + struct.pack('<I', len(T)))
        for t in T:
            q = V[t]; n = np.cross(q[1] - q[0], q[2] - q[0]); n = n / (np.linalg.norm(n) + 1e-12); fh.write(struct.pack('<12fH', *n, *q.ravel(), 0))
for n, k_, s, c in PARTS + [('参考 亚克力 (中心 ±30)', 'ref_acrylic', BRepAlgoAPI_Common(B.acrylic, gbox(-30, -30, g0 - 1, 30, 30, g1 + 1)).Shape(), ''), ('参考 顶盖', 'ref_top_cap', B.top_cap, '')]: w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(OUT / '零件' / f'{k_}.step'))
stl(bar, 'led_top_bar_print.stl', True, 0); stl(hold, 'post_holder_print.stl', False, 0); stl(comb_s, 'led_comb_print.stl', False, 0)
write3mf(str(OUT / '顶部连接.3mf'), [(n, s, c, 0.03) for n, _, s, c in PARTS] + [(n, s, '#C0C0C0', 0.03) for n, s in SCR] + [(n, s, '#E69138', 0.03) for n, s in FN] + [(n, s, '#B8860B', 0.03) for n, s in NS] + [(n, s, c, 0.08) for n, s, c in REF[:5]])
D = dict(zc=zc, zp=zp, zs=zs, zb=zb, pt=pt, bz0=bz0, bz1=bz1, ac0=g0, ac1=g1, zt=zt, led_t=1.6)
(OUT / '参数.json').write_text(json.dumps(dict(IF=IF, P=P, D=D, NUTS=NUTS, WIN=WIN), ensure_ascii=False, indent=1), encoding='utf-8')
M = ['# V1.2 顶部连接 第二版 (11-27 顶部 = 亚克力 8 + MR105)', '', f'由 `v1.2/scripts/top_stack_v1_2.py` 生成 ({time.strftime("%Y-%m-%d %H:%M")}); 亚克力/MR105/顶盖/外卡环读主模型 (GT_ACR=1), 本脚本不改主模型。', f'螺柱 M3 Φ5×{P["post_l"]:g} (阳牙 6, 顶内牙吃 M3×8)', '', '## Z', *[f'- {a}: {b:.2f}' for a, b in (('屏顶', z1), *D.items())], '', '## 重叠 (mm³; 螺纹、压装、占位块为预期)', *[f'- {a} × {b}: {v}' for a, b, v in INT]]
(OUT / '接口与校核.md').write_text('\n'.join(M) + '\n', encoding='utf-8')
