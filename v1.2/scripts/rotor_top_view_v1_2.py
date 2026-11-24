"""V1.2 转子盘B — 承载盘一级连接件俯视图 (直接坐/锁在承载盘上的件 + 它们的螺丝螺母)。
11-23 用户「转子盘俯视图更新一下」: 原图 (11-20 15:40) 是临时脚本出的, 这里固化成项目脚本, 改件后重跑即可。
    cd v1.2/scripts && ../../.venv/bin/python rotor_top_view_v1_2.py
输出: ../assembly_v1_2_转子盘B_一级连接件俯视.{png,pdf}
"""
import io, contextlib, math, time
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import fasteners_v1_2 as FS
    import led_support_v1_2 as L
    import wireless_holder_v1_2 as WH
    import rotor_shroud_b_v1_2 as RSB
RB = RSB.RB
from mf3_v1_2 import mesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager, colors as mcolors
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
assert B.ROTOR_B, '本图只画转子盘B'

# 层: G 玻纤板 / R 承载盘 / U 承载盘上的件 / S 螺丝 / N 螺母
PARTS = [(f'玻纤板 fr4_plate_v1_2b Φ{RB.FR4_OD:g}×{RB.FR4_T:g}', RB.fr4, '#C9B458', 'G'),
         ('承载盘 rim_ring_v1_2b', RB.rim, '#6AA84F', 'R'),
         *[(n, sh, c, 'U') for n, sh, c in RB.SCREEN_PARTS],
         ('V2 底板 (交付 STEP)', L.bb_step, '#1E8449', 'U'),
         ('无线夹块 wireless_holder_v1_2 ×2', WH.H, '#FFD966', 'U'), ('无线供电模块 (占位)', WH.module, '#3D85C6', 'U')]
NP = len(PARTS)
for n, sh, c in FS.F:
    if any(k in n for k in ('玻璃', '转子罩', '梳齿', '夹条', '灯板', '电机')): continue
    bb = B.bbox(sh)
    if bb[2] < 16.0 or bb[5] > 45.0 or max(abs(bb[0]), abs(bb[3]), abs(bb[1]), abs(bb[4])) > 95: continue
    PARTS.append((n, sh, '#B0B0B0' if c.upper() == '#C0C0C0' else c, 'S' if c.upper() == '#C0C0C0' else 'N'))
CNT = {}
for n, _, _, Lr in PARTS[NP:]:
    g = n.rsplit(' #', 1)[0]; CNT[(Lr, g)] = CNT.get((Lr, g), 0) + 1


def tris(shape, defl):
    try: V, T = mesh(shape, defl)
    except ValueError: return np.zeros((0, 3, 3))
    return V[T]
MESH = [(n, tris(s, 0.25 if L_ in 'GR' else 0.15), np.array(mcolors.to_rgb(c)), L_) for n, s, c, L_ in PARTS]


def basis(az, el):
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    u = np.array([-math.sin(a), math.cos(a), 0.0]); return u, np.cross(d, u), d


def render(ax, items, az, el):
    u, v, d = basis(az, el); PP, CC, DD = [], [], []
    lt = 0.6 * d + 0.4 * np.array([0, 0, 1.0]); lt /= np.linalg.norm(lt)
    for P, rgb in items:
        if not len(P): continue
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        PP.append(P); CC.append(np.clip(rgb[None, :] * (0.4 + 0.6 * np.abs(n @ lt))[:, None], 0, 1)); DD.append(P.mean(1) @ d)
    P = np.concatenate(PP); C = np.concatenate(CC); D = np.concatenate(DD); o = np.argsort(D)
    ax.add_collection(PolyCollection(np.stack([P[o] @ u, P[o] @ v], axis=-1), facecolors=C[o], edgecolors='none', antialiased=False, rasterized=True))
    ax.set_aspect('equal'); ax.axis('off'); ax.autoscale_view(); ax.margins(0.02)
    return u, v


fig = plt.figure(figsize=(20, 11.2))
ax0 = fig.add_axes([0.0, 0.08, 0.5, 0.84]); ax1 = fig.add_axes([0.5, 0.44, 0.5, 0.50])
items = [(P, c) for _, P, c, _ in MESH]
u, v = render(ax0, items, -90.0, 89.99); ax0.set_title('俯视 (+x 右, +y 上)', fontsize=13)
render(ax1, items, -60.0, 30.0); ax1.set_title('轴测', fontsize=13)
for a in RB.SP_ANG:   # 支撑件标注
    p = np.array([62.0 * math.cos(math.radians(a)), 62.0 * math.sin(math.radians(a)), 40.0])
    k = RB.SP_TYPE[a]
    t = (f'A 屏幕支架件 @{a:g}°\n主体高 {RB.SP_A_LOW:g}, 两翼罩锁块 {RB.SP_T:g}' if k == 'a' else f'B 上下件 @{a:g}°\n高 {RB.SP_T:g}, 顶面全平 (翻面打印)')
    ax0.annotate(t, (p @ u, p @ v), xytext=(-0.55 * (p @ u), -0.55 * (p @ v)), textcoords='offset points', fontsize=9.5, color='#7F6000',
                 ha='center', bbox=dict(fc='white', alpha=0.85, ec='none', pad=1), arrowprops=dict(arrowstyle='->', color='#7F6000'))
cx, cy = np.array([0, 0, 40.0]) @ u, np.array([0, 0, 40.0]) @ v
ax0.plot(cx, cy, '+', ms=22, mew=2, color='red')
T = ['件 (直接坐/锁在承载盘上):'] + [f'  · {n}' for n, _, _, _ in PARTS[:NP]] + ['', '螺丝:'] + \
    [f'  · {g} ×{k}' for (Lr, g), k in sorted(CNT.items()) if Lr == 'S'] + ['', '螺母:'] + [f'  · {g} ×{k}' for (Lr, g), k in sorted(CNT.items()) if Lr == 'N']
fig.text(0.51, 0.43, '\n'.join(T), fontsize=8.3, va="top", linespacing=1.3)
fig.suptitle(f'POV3D V1.2 转子盘B — 承载盘一级连接件俯视 (灯板下沿 Z{B.Z_SCR0:g} = 承载盘顶 + {B.SCREEN_GAP:g})', fontsize=15, y=0.985)
fig.text(0.99, 0.005, f'v1.2/scripts/rotor_top_view_v1_2.py  {time.strftime("%Y-%m-%d %H:%M")}', fontsize=7, ha='right', color='#666')
out = B.V12 / 'assembly_v1_2_转子盘B_一级连接件俯视.png'
fig.savefig(out, dpi=110); fig.savefig(str(out).replace('.png', '.pdf'), dpi=200)
print(out)
