"""V1.2 转子部分 (转子盘B) 组合图 (用户 11-18「转子部分组合看一下」)。
件取自 assembly_noglass_v1_2 同一套变量 (B.ROTOR_B); 螺丝取 fasteners_v1_2 里 Z≥16、非玻璃的那些 (转子侧)。
    cd v1.2/scripts && ../../.venv/bin/python rotor_asm_v1_2.py
输出: ../assembly_v1_2_转子盘B_组合图.{pdf,png} + ../assembly_v1_2_转子盘B.3mf
"""
import io, contextlib, math
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import fasteners_v1_2 as FS
    import led_support_v1_2 as L
    import fpc_v1_2 as F
    import wireless_holder_v1_2 as WH
    import rotor_shroud_b_v1_2 as RSB
RB = RSB.RB
from mf3_v1_2 import mesh, write3mf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager, colors as mcolors
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
assert B.ROTOR_B, '本图只画转子盘B'

# 层: M 电机 (参考) / G 玻纤板 / R 承载盘 / U 承载盘上的件 / C 罩子 / S 螺丝 / N 螺母铜螺母
PARTS = [('电机 Φ55×21.5 (占位, 参考)', B.motor, '#333333', 'M'),
         (f'玻纤板 fr4_plate_v1_2b Φ{RB.FR4_OD:g}×{RB.FR4_T:g}', RB.fr4, '#C9B458', 'G'),
         ('承载盘 rim_ring_v1_2b', RB.rim, '#6AA84F', 'R'),
         ('屏幕固定件 +x screen_holder_v1_2b_a', RB.hold_a, '#F1C232', 'U'), ('屏幕固定件 -x screen_holder_v1_2b_b', RB.hold_b, '#E69138', 'U'),
         ('灯板夹条 led_bar', L.bar_s, '#8E7CC3', 'U'), ('灯板顶部件 led_top', L.top, '#6FA8DC', 'U'), ('灯板梳齿 led_comb', L.comb_s, '#9FC5E8', 'U'),
         ('灯板 A (+y)', L.led_a, '#145A32', 'U'), ('灯板 B (-y)', L.led_b, '#0E3B22', 'U'),
         (f'Φ8×{L.ROD_L:g} 钢轴', L.rod, '#999999', 'U'),
         ('桥板 A/B', L.comp([F.bridge_a, F.bridge_b]), '#1E8449', 'U'), ('FPC A/B', L.comp([F.fpc_a, F.fpc_b]), '#E67E22', 'U'),
         ('天线软板 ×2', L.comp([L.ant_a, L.ant_b]), '#C0392B', 'U'),
         ('V2 底板 (交付 STEP)', L.bb_step, '#1E8449', 'U'),
         ('无线托盘 wireless_holder_v1_2', WH.H, '#FFD966', 'U'), ('无线供电模块 (占位)', WH.module, '#3D85C6', 'U'),
         ('转子罩 +y 半 rotor_shroud_b_a_v1_2b', RSB.shr_a, '#A4C2F4', 'C'), ('转子罩 -y 半 rotor_shroud_b_b_v1_2b', RSB.shr_b, '#B6D7A8', 'C')]
NP = len(PARTS)
for n, sh, c in FS.F:
    if '玻璃' in n: continue
    bb = B.bbox(sh)
    if bb[2] < 16.0 or max(abs(bb[0]), abs(bb[3]), abs(bb[1]), abs(bb[4])) > 95: continue
    PARTS.append((n, sh, '#B0B0B0' if c.upper() == '#C0C0C0' else c, 'S' if c.upper() == '#C0C0C0' else 'N'))
SCREWS = {}
for n, _, _, Lr in PARTS[NP:]:
    if Lr == 'S': g = n.rsplit(' #', 1)[0]; SCREWS[g] = SCREWS.get(g, 0) + 1
NUTS = {}
for n, _, _, Lr in PARTS[NP:]:
    if Lr == 'N': g = n.rsplit(' #', 1)[0]; NUTS[g] = NUTS.get(g, 0) + 1

def tris(shape, defl):
    try: V, T = mesh(shape, defl)
    except ValueError: return np.zeros((0, 3, 3))
    return V[T]
MESH = [(n, tris(s, 0.25 if L_ in 'MGRC' else 0.15), np.array(mcolors.to_rgb(c)), L_) for n, s, c, L_ in PARTS]

def basis(az, el):
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    u = np.array([-math.sin(a), math.cos(a), 0.0]); v = np.cross(d, u)
    return u, v, d
def render(ax, items, az, el):
    u, v, d = basis(az, el); allP, allC, allD = [], [], []
    lt = 0.6 * d + 0.4 * np.array([0, 0, 1.0]); lt /= np.linalg.norm(lt)
    for P, rgb in items:
        if len(P) == 0: continue
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        k = 0.4 + 0.6 * np.abs(n @ lt)
        allP.append(P); allC.append(np.clip(rgb[None, :] * k[:, None], 0, 1)); allD.append(P.mean(1) @ d)
    P = np.concatenate(allP); C = np.concatenate(allC); D = np.concatenate(allD); o = np.argsort(D)
    ax.add_collection(PolyCollection(np.stack([P[o] @ u, P[o] @ v], axis=-1), facecolors=C[o], edgecolors='none', antialiased=False, rasterized=True))
    ax.set_aspect('equal'); ax.axis('off'); ax.autoscale_view(); ax.margins(0.02)

# 爆炸: 玻纤板往下, 玻纤板底往上的螺丝更往下, 罩子往上
def ex(n, P, L_):
    if not len(P): return P
    dz = {'M': -70.0, 'G': -25.0}.get(L_, 0.0); dy = 0.0
    if L_ == 'S' and '玻纤板' in n: dz = -55.0
    if L_ == 'C' or (L_ == 'S' and ('转子罩' in n)):          # 罩子沿 ±y 两边拉开 (往上会卡在灯板中间)
        dy = 110.0 if (('+y' in n) or (P[:, :, 1].mean() > 0)) else -110.0
    return P + np.array([0, dy, dz])

fig = plt.figure(figsize=(16.54, 11.69))
fig.suptitle('POV3D V1.2 — 转子部分 (转子盘B) 组合图', fontsize=15, y=0.985)
AZ, EL = -60.0, 22.0
axA = fig.add_axes([0.00, 0.47, 0.26, 0.45]); axO = fig.add_axes([0.25, 0.47, 0.27, 0.45])
axE = fig.add_axes([0.51, 0.04, 0.28, 0.89]); axT = fig.add_axes([0.00, 0.02, 0.26, 0.42]); axF = fig.add_axes([0.25, 0.02, 0.27, 0.42])
render(axA, [(P, c) for n, P, c, L_ in MESH if L_ != 'M'], AZ, EL); axA.set_title('装配 (轴测, 带罩子)', fontsize=11)
render(axO, [(P, c) for n, P, c, L_ in MESH if L_ not in 'MC' and not ('转子罩' in n)], AZ, EL); axO.set_title('去掉罩子', fontsize=11)
render(axE, [(ex(n, P, L_), c) for n, P, c, L_ in MESH], AZ, EL); axE.set_title('爆炸: 电机 / 玻纤板+底部螺丝 ↓, 罩子两半沿 ±y 拉开', fontsize=11)
render(axT, [(P, c) for n, P, c, L_ in MESH if L_ not in 'MC' and '转子罩' not in n], -90.0, 89.99); axT.set_title('俯视 (去罩子)', fontsize=11)
render(axF, [(P, c) for n, P, c, L_ in MESH if L_ != 'C' and '转子罩' not in n], -90.0, 0.01); axF.set_title('正视 (看 +y, 去罩子, 含电机)', fontsize=11)

tx = fig.add_axes([0.80, 0.04, 0.19, 0.90]); tx.axis('off')
T = [f'承载盘顶 Z{RB.Z_TOP:g}; 灯板下沿 Z{RB.H_Z1:g}', '', '件']
T += [f'  · {n}' for n, _, _, Lr in PARTS[:NP]]
T += ['', '螺丝 (每台)'] + [f'  · {g} ×{k}' for g, k in sorted(SCREWS.items())]
T += ['', '螺母 / 铜螺母 / 垫柱'] + [f'  · {g} ×{k}' for g, k in sorted(NUTS.items())]
tx.text(0, 1, '\n'.join(T), va='top', fontsize=7.6, linespacing=1.45)
fig.text(0.99, 0.008, 'v1.2/scripts/rotor_asm_v1_2.py  2026-11-18', fontsize=7, ha='right', color='#666')
V12 = B.V12
fig.savefig(V12 / 'assembly_v1_2_转子盘B_组合图.pdf', dpi=200); fig.savefig(V12 / 'assembly_v1_2_转子盘B_组合图.png', dpi=110)
write3mf(str(V12 / 'assembly_v1_2_转子盘B.3mf'), [(n, s, c, 0.05) for n, s, c, _ in PARTS])
print('件', NP, '螺丝', SCREWS, '螺母', NUTS)
