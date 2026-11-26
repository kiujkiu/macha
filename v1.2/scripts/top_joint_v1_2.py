"""V1.2 顶部连接组件 (屏幕顶 ↔ 圆环玻璃) —— 11-25 用户「屏幕上和上边玻璃连接这个部分，我们拆出来单独设计吧」。

本文件是独立设计区: 接口 IF 只从主模型 (build_v1_2 / led_support_v1_2) 读, 不改主模型; 件的参数 P 和形体都在本文件, 随便改。
11-25 晚 用户「屏幕上边，做一个长条，厚度5mm，然后左右两边锁这个m3的铜螺母」+ 红框图 (每块屏 8 个焊位, 六角铜螺母, 上下错开):
  led_top 的舌 + 帽 → 5 厚长条 (平底, 盖两板上沿), 每端一根 M3×20 从上往下穿长条, 拧过上面那颗 + 下面那颗 (分属两块屏, 用户「两个屏幕之间是交错的，这样可以通过一个螺丝锁住这个螺母，锁住两个屏幕」), 孔在中面 y=ECC; 轴座留在转轴 (0,0)。梳齿跟着坐长条顶 (+1)。TJ=base 出旧基线。
定稿后再合回 led_support (led_top / led_comb / 轴) 与 build_v1_2 (glass_top_hub)。P 初值 = 现行件, 跑一遍会和现行件比体积差。
    cd v1.2/scripts && ../../.venv/bin/python top_joint_v1_2.py
输出 v1.2/顶部连接/: 顶部连接.3mf (5 件 + 邻件参考) / 顶部连接_剖面.{png,pdf} / 接口与校核.md / 零件/*.step
"""
import io, contextlib, math, sys, time
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import led_support_v1_2 as L
from mf3_v1_2 import mesh, write3mf
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
cyl, gbox, cut, fuse, clean, xf, rotz, vol, revol = B.cyl, B.gbox, B.cut, B.fuse, B.clean, B.xf, B.rotz, B.vol, B.revol
import os
BAR = os.environ.get('TJ', 'base') == 'bar'
OUT = B.V12 / '顶部连接' / ('' if BAR else '基线'); (OUT / '零件').mkdir(parents=True, exist_ok=True)

# ---------------- 接口 (主模型给, 本组件不能动) ----------------
IF = dict(z_led=L.Z1, ecc=L.ECC, gap=2 * L.GAP_HALF, tongue_z0=L.TOP_TONGUE_Z0,       # 下: 灯板上沿 / 灯板组偏心 / 板间隙 / 上中窗底
          z_glass0=B.GD_Z0, z_glass1=B.GD_Z1, hole_d=B.GD_ID, glass_t=B.GD_T,          # 上: 圆环玻璃 底 / 顶 / 中孔 / 厚
          r_in=B.GL_R0, z_tube=B.Z_GT, z_green=B.GC_Z1)                               # 侧: 管内弧形件内面 / 玻璃管端 / 绿件顶
# 11-25 18:32 用户草图「两个pcb间距4.6mm，就是6边螺母的距离」: 本设计区两屏间隙 4.6 (主模型仍 5.0; 中面 ECC 不动, 两屏各往里 0.2) ⇒ 两颗铜螺母同心 y=ECC, 都贴两屏
if BAR: IF['gap'] = 4.6
DY = (2 * L.GAP_HALF - IF['gap']) / 2
# ---------------- 参数 (随便改; 初值 = 现行件) ----------------
P = dict(tongue_hx=2.8, tongue_t=4.8, cap_hx=14.5, cap_hy=6.0, cap_t=4.0, pad_d=16.0, boss_d=14.0, boss_z1=L.BOSS_Z1, rod_hole=7.85,
         comb_fix_x=10.5, comb_t=4.0, comb_hole=14.2, comb_ring=22.0, comb_beam_y=4.0, comb_teeth=[16.0, 26.0, 36.0, 46.0], tooth_w=6.0, tooth_y=15.0, slots_y=[6.5, 12.0],
         rod_d=8.0, rod_l=65.0, rod_over=1.3, brg=(8.0, 16.0, 5.0),
         fl_d=32.0, claw_r0=8.2, claw_clr=0.2, barb=1.0, catch_dz=0.7, tip_r=9.0, n_slot=6, slot_w=2.0, brg_d=16.1, roof=4.0, relief=(9.0, 2.5))

# 11-25 晚 长条
P.update(rib_t=4.6, rib_h=3.0, rib_hx=81.5, bar_t=5.0, bar_hx=83.0, bar_hy=4.5, bar_hole=3.4, bar_slot=0.3, scr_l=20.0, head_d=7.0, head_h=1.5, nut_af=L.SO_AF, nut_l=L.SO_L, nut_x=L.SO_X)
WIN = dict(top=(L.Z0 + 166 + 27.97375, L.Z0 + 166 + 37.97375), mid=L.SO_WIN_MID_Z, bot=L.SO_WIN_Z)        # 开窗世界 Z (KiCad y 底边 166, 顶边 -42)
NUTS = []                                        # (板, 行, 列, x, y, z0)  板本地 左=下半 右=上半 (板 B 绕 (0,ECC) 转 180°); 中列: 板 A 下半 / 板 B 上半 (假设, 不受力)
for row, (w0, w1) in WIN.items():
    for bd, sy in (('A', 1), ('B', -1)):
        for col, sx in (('-x', -1), ('0', 0), ('+x', 1)):
            if col == '0' and row == 'mid': continue
            low = ((sx < 0) == (bd == 'A')) if sx else bd == 'A'
            NUTS.append((bd, row, col, sx * P['nut_x'], IF['ecc'] + sy * (IF['gap'] - P['nut_af']) / 2, w0 if low else w0 + P['nut_l']))
TOPN = [n for n in NUTS if n[1] == 'top' and n[2] != '0' and n[5] > WIN['top'][0] + 1]                     # 每端靠上那颗: +x 板 A / -x 板 B
if BAR: P['cap_t'] = P['bar_t']

# ---------------- 形体 ----------------
z1, ecc = IF['z_led'], IF['ecc']; zcap = z1 + P['cap_t']; zc1 = zcap + P['comb_t']
brg_z0 = IF['z_glass1']; brg_z1 = brg_z0 + P['brg'][2]; rod_z1 = round(brg_z1 + P['rod_over'], 6); rod_z0 = rod_z1 - P['rod_l']
EC = L.T_ECC
def slot_x(x, y, d, h, z0, z1_): return fuse(gbox(x - h, y - d / 2, z0, x + h, y + d / 2, z1_), cyl(x - h, y, d, z0, z1_), cyl(x + h, y, d, z0, z1_))
def led_top_bar():
    s = fuse(xf(gbox(-P['bar_hx'], -P['bar_hy'], z1, P['bar_hx'], P['bar_hy'], zcap), EC), cyl(0, 0, P['pad_d'], z1, zcap),
             xf(gbox(-P['rib_hx'], -P['rib_t'] / 2, z1 - P['rib_h'], P['rib_hx'], P['rib_t'] / 2, z1 + 0.01), EC))   # 筋: 插两屏之间, 底离上颗铜螺母 1.03
    s = fuse(s, cyl(0, 0, P['boss_d'], zcap - 0.01, P['boss_z1']))
    s = cut(s, cyl(0, 0, P['rod_hole'], rod_z0, P['boss_z1'] + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['comb_fix_x'], ecc, 4.2, z1, zcap + 0.01))
    for n in TOPN: s = cut(s, slot_x(n[3], ecc, P['bar_hole'], P['bar_slot'], z1 - P['rib_h'] - 1, zcap + 1))
    return clean(s)
def led_top():
    if BAR: return led_top_bar()
    s = fuse(gbox(-P['tongue_hx'], -P['tongue_t'] / 2, IF['tongue_z0'], P['tongue_hx'], P['tongue_t'] / 2, z1 + 0.01), gbox(-P['cap_hx'], -P['cap_hy'], z1, P['cap_hx'], P['cap_hy'], zcap))
    s = fuse(xf(s, EC), cyl(0, 0, P['pad_d'], z1, zcap))
    s = fuse(s, cyl(0, 0, P['boss_d'], zcap - 0.01, P['boss_z1']))
    s = cut(s, cyl(0, 0, P['rod_hole'], rod_z0, P['boss_z1'] + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['comb_fix_x'], ecc, 4.2, z1 - 1, zcap + 0.01))
    return clean(s)
def comb():
    xm = P['comb_teeth'][-1] + P['tooth_w'] / 2; w, ty = P['tooth_w'] / 2, P['tooth_y']
    s = gbox(-xm, -P['comb_beam_y'], zcap, xm, P['comb_beam_y'], zc1)
    for sx in (1, -1):
        for t in P['comb_teeth']: s = fuse(s, gbox(sx * t - w, -ty, zcap, sx * t + w, ty, zc1))
    s = fuse(cyl(0, 0, P['comb_ring'], zcap, zc1), xf(s, EC))
    s = cut(s, cyl(0, 0, P['comb_hole'], zcap - 1, zc1 + 1))
    for sx in (1, -1): s = cut(s, cyl(sx * P['comb_fix_x'], ecc, 3.4, zcap - 1, zc1 + 1))
    return clean(cut(s, *[cyl(sx * t, ecc + sy * y, 3.4, zcap - 1, zc1 + 1) for sx in (1, -1) for t in P['comb_teeth'] for y in P['slots_y'] for sy in (1, -1)]))
def hub():
    g0, g1 = IF['z_glass0'], IF['z_glass1']; rh = IF['hole_d'] / 2; rb = rh + P['barb']; r1 = rh - P['claw_clr']; rf = P['fl_d'] / 2
    zc = g0 - P['catch_dz']; zt = zc - 0.5 - (rb - P['tip_r']); ft = P['brg'][2] + P['roof']
    s = revol([(P['claw_r0'], zt), (P['tip_r'], zt), (rb, zc - 0.5), (rb, zc), (r1, g0), (r1, g1), (rf, g1), (rf, g1 + ft - 1), (rf - 1, g1 + ft), (0, g1 + ft), (0, g1), (P['claw_r0'], g1)])
    for k in range(P['n_slot']): s = cut(s, xf(gbox(-P['slot_w'] / 2, 0, zt - 1, P['slot_w'] / 2, 20, g1 - 1.0), rotz(30 + 360 / P['n_slot'] * k)))
    s = cut(s, cyl(0, 0, P['brg_d'], g1 - 0.01, brg_z1), cyl(0, 0, P['relief'][0], brg_z1 - 0.01, brg_z1 + P['relief'][1]))
    return clean(s), zt, g1 + ft
top, comb_s = led_top(), comb(); hub_s, hub_z0, hub_z1 = hub()
rod = cyl(0, 0, P['rod_d'], rod_z0, rod_z1)
brg = cut(cyl(0, 0, P['brg'][1], brg_z0, brg_z1), cyl(0, 0, P['brg'][0], brg_z0 - 1, brg_z1 + 1))
SCR = [fuse(cyl(n[3], ecc, P['head_d'], zcap, zcap + P['head_h']), cyl(n[3], ecc, 3.0, zcap - P['scr_l'], zcap + 0.01)) for n in TOPN]
def in_gap(z0):                                  # 灯板 STEP 里伸进两屏之间、高于 z0 的小件 (不含 J4/J5 占位铜块)
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    out = []
    for nm, led in (('A', REF[0][1]), ('B', REF[1][1])):
        e = TopExp_Explorer(led, TopAbs_SOLID)
        while e.More():
            b = L.bbox(e.Current()); e.Next()
            if b[3] - b[0] < 100 and b[5] > z0 and b[1] < ecc + IF['gap'] / 2 - 0.05 and b[4] > ecc - IF['gap'] / 2 + 0.05: out.append((nm, [round(v, 2) for v in b]))
    return out
NUTS_S = [L.standoff(x, y, z) for _, _, _, x, y, z in NUTS]
PARTS = [('① 屏幕顶长条 led_top_bar' if BAR else '① 灯板顶部件 led_top', 'led_top', top, '#6FA8DC', L.top), ('② 配平梳齿 led_comb', 'led_comb', comb_s, '#3D85C6', L.comb_s),
         (f'③ 钢轴 Φ{P["rod_d"]:g}×{P["rod_l"]:g}', 'rod', rod, '#8A8A8A', L.rod), ('④ 688 轴承', 'brg', brg, '#555555', L.brg), ('⑤ 中心堵头 glass_top_hub', 'hub', hub_s, '#F1C232', B.glass_top_hub)]
_sh = lambda s, dy: xf(s, B.tr(0, dy, 0)) if hasattr(B, 'tr') else xf(s, L.tr(0, dy, 0))
REF = [('灯板 A', _sh(L.led_a, -DY) if BAR else L.led_a, '#145A32'), ('灯板 B', _sh(L.led_b, DY) if BAR else L.led_b, '#0E3B22'), (f'圆环玻璃 OD{B.GD_OD:g}×{B.GD_T:g}', B.glass_disc, '#BFE3F2'), ('玻璃上 红件', B.glass_top, '#D9534F'),
       ('玻璃上 绿件', B.glass_top_clamp, '#5CB85C'), ('玻璃罩', B.tube, '#A9CCE3'), ('管内弧形件 ×8', L.comp(B.glass_top_lugs), '#E69138')]

# ---------------- 校核 ----------------
dist = lambda a, b: BRepExtrema_DistShapeShape(a, b).Value()
print('与现行件比 (体积差 mm³ / 有效):')
CMP = []
for n, k, s, c, o in PARTS:
    dv = vol(s) - vol(o); sd = vol(cut(s, o)) + vol(cut(o, s)) if abs(dv) < 1e9 else 0
    CMP.append((n, round(vol(s), 1), round(dv, 3), round(sd, 3), BRepCheck_Analyzer(s).IsValid())); print('  ', *CMP[-1])
INT = []
for i, (n, k, s, *_ ) in enumerate(PARTS):
    for m, t in [(q[0], q[2]) for q in PARTS[i + 1:]] + [(r[0], r[1]) for r in REF]:
        v = L.common_v(s, t)
        if v > 1e-3: INT.append((n, m, round(v, 2)))
ov = rod_z0, P['boss_z1']; ins = P['boss_z1'] - rod_z0; free = brg_z0 - P['boss_z1']
hl = (IF['z_glass1'] - 1.0) - hub_z0
def strain(t): l = (t - 1) + (IF['z_glass0'] - hub_z0); return 1.5 * (IF['hole_d'] / 2 - P['claw_clr'] - P['claw_r0']) * P['barb'] / l ** 2
I = math.pi * P['rod_d'] ** 4 / 64; df = lambda F: F * free ** 3 / (3 * 205000 * I)
print('干涉:', INT); print(f'压入 {ins:.2f}  悬伸 {free:.2f}  爪长 {hl:.2f}  爪应变 t10 {strain(10):.4f} t5 {strain(5):.4f}  轴端 10N 挠度 {df(10):.4f}')

tip = zcap - P['scr_l']
for n in TOPN if BAR else []: print('锁点', n, '螺母', round(n[5], 2), round(n[5] + P['nut_l'], 2), '尾', round(tip, 2), '吃上颗', P['nut_l'], '吃下颗', round(min(n[5] - tip, P['nut_l']), 2), '尾伸出下颗', round(n[5] - P['nut_l'] - tip, 2))
if BAR:
    print('筋范围内背面件:', in_gap(z1 - P['rib_h']) or '无'); g_ = sorted(in_gap(z1 - 16), key=lambda q: -q[1][5])[:6]; print('离上沿最近的背面件:', g_)
if BAR:
    for nm, g in (('长条', [top]), ('螺丝', SCR)):
        for m, t in [(q[0], q[2]) for q in PARTS if q[2] is not top] + [('夹条 led_bar', L.bar_s)] + [(x[0], x[1]) for x in REF]:
            v = sum(L.common_v(a, t) for a in g)
            if v > 1e-3 and not (nm == '长条' and '钢轴' in m): print(f'  {nm} × {m}: {v:.2f} mm3')
    for i, a in enumerate(NUTS_S):
        for j in range(i + 1, len(NUTS_S)):
            if L.common_v(a, NUTS_S[j]) > 1e-3: print('  螺母重叠', NUTS[i], NUTS[j])
        v = L.common_v(a, L.bar_s)
        if v > 1e-3: print('  铜螺母 × 夹条', NUTS[i], round(v, 2))
    print('  长条到: 梳齿', round(dist(top, comb_s), 2), '红件', round(dist(top, B.glass_top), 2), '弧形件', round(dist(top, REF[-1][1]), 2), '玻璃罩', round(dist(top, B.tube), 2))
# ---------------- 输出 ----------------
for n, k, s, c, o in PARTS:
    k = 'led_top_bar' if BAR and k == 'led_top' else k
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(OUT / '零件' / f'{k}.step'))
if BAR:                                          # 打印 STL (筋贴床, 轴座朝上, 板底两侧要支撑)
    import struct
    _V, _T = mesh(top, 0.02); _V = _V - np.array([0, 0, z1 - P['rib_h']])
    with open(OUT / '零件' / 'led_top_bar_print.stl', 'wb') as fh:
        fh.write(b'led_top_bar_v1_2'.ljust(80, b' ') + struct.pack('<I', len(_T)))
        for t in _T:
            q = _V[t]; n_ = np.cross(q[1] - q[0], q[2] - q[0]); n_ = n_ / (np.linalg.norm(n_) + 1e-12); fh.write(struct.pack('<12fH', *n_, *q.ravel(), 0))
write3mf(str(OUT / '顶部连接.3mf'), [(n, s, c, 0.03) for n, _, s, c, _ in PARTS] + [(n, s, c, 0.08) for n, s, c in REF[:5]]
          + ([(f'M3×{P["scr_l"]:g} 超薄头 #{i}', s, '#C0C0C0', 0.03) for i, s in enumerate(SCR)] + [(f'铜螺母 板{n[0]} {n[1]} {n[2]}', s, '#B8860B', 0.03) for n, s in zip(NUTS, NUTS_S)] if BAR else []))

import json
(OUT / '参数.json').write_text(json.dumps(dict(IF=IF, P=P, D=dict(zcap=zcap, zc1=zc1, brg_z0=brg_z0, brg_z1=brg_z1, rod_z0=rod_z0, rod_z1=rod_z1, hub_z0=hub_z0, hub_z1=hub_z1, led_t=1.6, zcap_=zcap), NUTS=NUTS, TOPN=TOPN, WIN=WIN), ensure_ascii=False, indent=1), encoding='utf-8')   # top_joint_drawing_v1_2 读
if BAR:                                          # 长条版: 图由 led_top_bar_drawing_v1_2.py 出; 下面的基线剖面只在 TJ=base 画
    M = ['# V1.2 顶部连接 (屏幕顶长条 led_top_bar)', '', f'由 `v1.2/scripts/top_joint_v1_2.py` 生成 ({time.strftime("%Y-%m-%d %H:%M")}); 设计区, 主模型未改。', '', '## 锁点 (每端一根 M3 穿两颗铜螺母)', '| 端 | 上颗(板) | 上颗 Z | 下颗 Z | 螺丝尾 Z | 吃上颗 | 吃下颗 |', '|---|---|---|---|---|---|---|']
    M += [f'| {n[2]} | {n[0]} | {n[5]:.2f}–{n[5] + P["nut_l"]:.2f} | {n[5] - P["nut_l"]:.2f}–{n[5]:.2f} | {tip:.2f} | {P["nut_l"]:g} | {min(n[5] - tip, P["nut_l"]):.2f} |' for n in TOPN]
    M += ['', '## 铜螺母 (每屏 8, 共 16; 中列上下为假设)', '| 板 | 行 | 列 | x | y | Z |', '|---|---|---|---|---|---|'] + [f'| {n[0]} | {n[1]} | {n[2]} | {n[3]:.2f} | {n[4]:.2f} | {n[5]:.2f}–{n[5] + P["nut_l"]:.2f} |' for n in NUTS]
    M += ['', '## 干涉', '- 长条 × 钢轴 52.84 mm³ (压装过盈, 预期); 螺丝 × 灯板 = STEP 里 J4/J5 占位铜块 (预期); 螺丝 × 铜螺母 = 螺纹 (未比)', '- 下中焊位铜螺母 (板 A 下半 Z41.70–46.70) × 夹条 led_bar (见控制台) —— 若下中真焊, 夹条要开口', '- 梳齿内排配重孔 (y ±6.5) 螺母 r3.2 会碰长条边 (4.5)']
    (OUT / '接口与校核.md').write_text('\n'.join(M) + '\n', encoding='utf-8'); sys.exit(0)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MP
from matplotlib import font_manager, colors as mc
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
def section(shape, axis, rot=0.0):
    """x=0 (axis 0, 横轴 y) 或 y=0 (axis 1, 横轴 x) 平面截面 → 闭合折线"""
    if rot: shape = xf(shape, rotz(rot))
    V, T = mesh(shape, 0.05); V = V.copy(); h = 1 - axis; d = V[:, axis] - 1.3e-4; segs = []
    for tri in T:
        s = d[tri]; q = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if s[a] * s[b] < 0:
                t = s[a] / (s[a] - s[b]); p = V[tri[a]] + t * (V[tri[b]] - V[tri[a]]); q.append((round(p[h], 4), round(p[2], 4)))
        if len(q) == 2 and q[0] != q[1]: segs.append(q)
    adj = {}
    for a, b in segs: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    loops = []
    while adj:
        st = next(iter(adj)); lp = [st]; cur = st
        while adj.get(cur):
            nx = adj[cur].pop(); adj[nx].remove(cur)
            lp.append(nx); cur = nx
            if cur == st: break
        for k in [k for k, v in adj.items() if not v]: del adj[k]
        if len(lp) > 3: loops.append(lp)
    return loops
def draw(ax, shape, axis, col, hatch=None, rot=0.0, alpha=1.0):
    vs, cs = [], []
    for lp in section(shape, axis, rot): vs += lp; cs += [MP.MOVETO] + [MP.LINETO] * (len(lp) - 2) + [MP.CLOSEPOLY]
    if vs: ax.add_patch(PathPatch(MP(vs, cs), fc=mc.to_rgba(col, alpha), ec='#111', lw=0.5, hatch=hatch))
fig = plt.figure(figsize=(16.54, 11.69))
fig.suptitle('POV3D V1.2 — 顶部连接组件 (屏幕顶 - 圆环玻璃) 拆分基线 = 现行件', fontsize=15, y=0.985)
axA = fig.add_axes([0.035, 0.05, 0.40, 0.89]); axB = fig.add_axes([0.45, 0.45, 0.32, 0.49]); axC = fig.add_axes([0.45, 0.05, 0.32, 0.36])
def all_sec(ax, axis):
    for n, s, c in REF: draw(ax, s, axis, c, alpha=0.75)
    for n, k, s, c, o in PARTS: draw(ax, s, axis, c, hatch='////' if k in ('led_top', 'hub') else None)
def vdim(ax, x, a, b, t, xr=None, fs=8):
    ax.annotate('', (x, b), (x, a), arrowprops=dict(arrowstyle='<->', lw=0.7, color='#B00', shrinkA=0, shrinkB=0))
    ax.text(x + 0.5, (a + b) / 2, t, fontsize=fs, color='#B00', va='center')
    if xr is not None:
        for z in (a, b): ax.plot([xr, x], [z, z], lw=0.3, color='#B00')
def hdim(ax, z, a, b, t, zr=None, fs=8):
    ax.annotate('', (b, z), (a, z), arrowprops=dict(arrowstyle='<->', lw=0.7, color='#06C', shrinkA=0, shrinkB=0))
    ax.text((a + b) / 2, z + 0.4, t, fontsize=fs, color='#06C', ha='center', va='bottom')
    if zr is not None:
        for x in (a, b): ax.plot([x, x], [zr, z], lw=0.3, color='#06C')
F = lambda v: f'{round(v, 2):g}'
all_sec(axA, 0); axA.set_xlim(-34, 46); axA.set_ylim(225, 331); axA.set_aspect('equal'); axA.set_title('A  剖面 x=0 (横 = y, 竖 = Z)  堵头剖在爪上', fontsize=11); axA.tick_params(labelsize=7)
vdim(axA, 20, IF['tongue_z0'], z1, f'舌 {F(z1 - IF["tongue_z0"])}', 5); vdim(axA, 20, z1, zcap, f'帽 {F(zcap - z1)}', 8); vdim(axA, 20, zcap, zc1, f'梳齿 {F(zc1 - zcap)}', 11)
vdim(axA, 20, zc1, P['boss_z1'], f'轴座(梳齿上) {F(P["boss_z1"] - zc1)}', 7); vdim(axA, 20, P['boss_z1'], hub_z0, f'轴座顶到爪尖 {F(hub_z0 - P["boss_z1"])}', 7)
vdim(axA, 20, hub_z0, IF['z_glass0'], f'爪伸出 {F(IF["z_glass0"] - hub_z0)}', 9); vdim(axA, 20, IF['z_glass0'], IF['z_glass1'], f'玻璃 {F(IF["glass_t"])}', 16)
vdim(axA, 20, IF['z_glass1'], brg_z1, f'688 {F(P["brg"][2])}', 16); vdim(axA, 20, brg_z1, hub_z1, f'堵头顶壁 {F(hub_z1 - brg_z1)}', 16)
vdim(axA, 35, rod_z0, P['boss_z1'], f'轴压入 {F(ins)}', 7); vdim(axA, 35, P['boss_z1'], brg_z0, f'轴悬伸 {F(free)}', 20); vdim(axA, -32, z1, IF['z_glass0'], f'灯板上沿\n到玻璃底\n{F(IF["z_glass0"] - z1)}', -12)
for z, t in ((z1, '灯板上沿'), (IF['z_tube'], '玻璃管端'), (IF['z_glass0'], '玻璃底'), (IF['z_glass1'], '玻璃顶'), (hub_z1, '堵头顶')): axA.text(-33 if z in (z1, IF['z_tube']) else -31, z + (-2.2 if z in (z1, IF['z_glass1']) else 0.4), f'{t} Z{z:.2f}', fontsize=7, color='#333')
all_sec(axB, 0); axB.set_xlim(-22, 22); axB.set_ylim(296, 331); axB.set_aspect('equal'); axB.set_title('B  上端放大: 堵头 / 688 / 玻璃孔', fontsize=11); axB.tick_params(labelsize=7)
hdim(axB, 327.5, -P['fl_d'] / 2, P['fl_d'] / 2, f'堵头法兰 Φ{F(P["fl_d"])}', hub_z1); hdim(axB, 299.8, -IF['hole_d'] / 2, IF['hole_d'] / 2, f'玻璃孔 Φ{F(IF["hole_d"])}', IF['z_glass0']); hdim(axB, 297.3, -P['claw_r0'], P['claw_r0'], f'爪内 Φ{F(2 * P["claw_r0"])} / 爪厚 {F(IF["hole_d"] / 2 - P["claw_clr"] - P["claw_r0"])}', hub_z0)
hdim(axB, 318.4, -P['brg_d'] / 2, P['brg_d'] / 2, f'688 窝 Φ{F(P["brg_d"])}'); vdim(axB, 15.5, hub_z0, IF['z_glass1'] - 1, f'爪长 {F(hl)}', 9, 8); vdim(axB, -20, rod_z1, brg_z1 + P['relief'][1], '', -4); axB.text(-21.5, 321.2, f'过冲 {F(brg_z1 + P["relief"][1] - rod_z1)}', fontsize=8, color='#B00')
all_sec(axC, 1); axC.set_xlim(-55, 55); axC.set_ylim(226, 292); axC.set_aspect('equal'); axC.set_title('C  剖面 y=0 (横 = x)', fontsize=11); axC.tick_params(labelsize=7)
hdim(axC, 288, -P['boss_d'] / 2, P['boss_d'] / 2, f'轴座 Φ{F(P["boss_d"])}', P['boss_z1']); xm = P['comb_teeth'][-1] + P['tooth_w'] / 2; hdim(axC, 232, -xm, xm, f'梳齿全长 {F(2 * xm)}', zcap); hdim(axC, 237, -P['pad_d'] / 2, P['pad_d'] / 2, f'圆垫 Φ{F(P["pad_d"])}', z1)
tx = fig.add_axes([0.785, 0.03, 0.21, 0.92]); tx.axis('off')
T = ['件'] + [f'  {n}' for n, *_ in PARTS] + ['', '接口 (本组件不能动)', f'  灯板上沿 Z{z1:.2f}, 板间隙 {F(IF["gap"])}', f'  灯板组偏心 y {F(ecc)} (轴仍在 0,0)', f'  玻璃 Z{IF["z_glass0"]:.2f}–{IF["z_glass1"]:.2f}, 孔 Φ{F(IF["hole_d"])}',
     f'  管内弧形件内面 r{F(IF["r_in"])}', '', '配合 / 受力', f'  舌 {F(2 * P["tongue_hx"])}×{F(P["tongue_t"])}×{F(z1 - IF["tongue_z0"])} 插两板间 (间隙 {F(IF["gap"])}, 无螺丝)', f'  轴压入 {F(ins)}, 悬伸 {F(free)}, 底 Z{rod_z0:.2f} 顶 Z{rod_z1:.2f}',
     f'  10 N 侧力 → 轴端弯 {df(10) * 1000:.1f} um (轴本身, 不含塑料座)', f'  爪应变: 玻璃厚 10 → {strain(10) * 100:.1f}% ; 厚 5 → {strain(5) * 100:.1f}%', '', '干涉 (>0.001 mm3)'] + [f'  {a} × {b}: {v}' for a, b, v in INT] + ['', '与现行件差 (对称差 mm3)'] + [f'  {n}: {sd}' for n, v, dv, sd, ok in CMP]
tx.text(0, 1, '\n'.join(T), va='top', fontsize=8, linespacing=1.55)
fig.text(0.99, 0.006, f'v1.2/scripts/top_joint_v1_2.py  {time.strftime("%Y-%m-%d %H:%M")}', fontsize=7, ha='right', color='#666')
fig.savefig(OUT / '顶部连接_剖面.png', dpi=110); fig.savefig(OUT / '顶部连接_剖面.pdf')
M = ['# V1.2 顶部连接组件 (屏幕顶 ↔ 圆环玻璃)', '', f'由 `v1.2/scripts/top_joint_v1_2.py` 生成 ({time.strftime("%Y-%m-%d %H:%M")})。独立设计区, 定稿前不动主模型。', '', '## 接口 (主模型给)', '| 项 | 值 |', '|---|---|'] + [f'| {k} | {v if not isinstance(v, float) else round(v, 3)} |' for k, v in IF.items()]
M += ['', '## 件', '| 件 | 体积 mm³ | 与现行差 | 对称差 | 有效 |', '|---|---|---|---|---|'] + [f'| {" | ".join(map(str, r))} |' for r in CMP] + ['', '## 干涉', *([f'- {a} × {b}: {v} mm³' for a, b, v in INT] or ['- 无']), '', '## 配合', *[f'- {t.strip()}' for t in T[T.index('配合 / 受力') + 1:T.index('干涉 (>0.001 mm3)') - 1]]]
(OUT / '接口与校核.md').write_text('\n'.join(M) + '\n', encoding='utf-8')
