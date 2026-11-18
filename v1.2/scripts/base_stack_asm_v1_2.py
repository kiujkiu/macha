"""V1.2 底座一级连接件组合图 (用户 11-18「锁到底面的件 + 底面 3D 组合图, 只跟底面一次连接的」)。
底座 = 打印底盘 4.5 + 玻纤板 FR4 3 (板顶 Z0); 只放直接坐/锁在底座上的件 + 从盘底往上的螺丝和它们的螺母 / 铜螺母。
定子盘 / 安装法兰 (坐在线圈环上, 第二层) 不放 (用户 11-18「定子盘不要」)。
    cd v1.2/scripts && ../../.venv/bin/python base_stack_asm_v1_2.py
输出: ../assembly_v1_2_底座一级件_组合图.{pdf,png} + ../assembly_v1_2_底座一级件.3mf
"""
import io, contextlib, math
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import fasteners_v1_2 as FS
from mf3_v1_2 import mesh, write3mf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager, colors as mcolors
from OCP.gp import gp_Trsf, gp_Vec
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False

# ---- 件 (名称, 形体, 颜色, 层: 'P' 打印底盘 / 'G' 玻纤板 / 'U' 上面的件 / 'S' 盘底螺丝 / 'N' 螺母铜螺母) ----
BOARD = B.board
PARTS = [('打印底盘 base_disc_v1_2_gf Φ220×4.5', B.disc_print, '#8A8F98', 'P'),
         ('玻纤板 base_fr4_v1_2 Φ220×3', B.fr4, '#C8D86A', 'G'),
         ('电机 Φ55×21.5 (占位)', B.motor, '#333333', 'U'),
         ('线圈环 coil_ring_v1_2', B.ring, '#E0A030', 'U'),
         ('电机控制板', BOARD, '#2E7D32', 'U'), ('控制板散热片 40×20', B.heatsink, '#C0392B', 'U'),
         ('底圈 glass_shroud_lower_v1_2', B.shroud_lo, '#7FB3D5', 'U'),
         ('XT60 压块', B.xt_clamp, '#F1C232', 'U'), ('XT60 底垫', B.xt_shim, '#E69138', 'U'),
         *([('MOS 压块 mos_clamp_v1_2', B.CD.clamp, '#E69138', 'U')] if B.CD.HAS_MC else []),
         *([('电容卡件 cap_clamp_v1_2', B.CD.cap_clamp, '#B45F06', 'U')] if B.CD.HAS_CC else []),
         ('线圈驱动板', B.CD.pcb, '#38761D', 'U'), ('线圈驱动 MOS', B.CD.mos, '#222222', 'U'), ('线圈驱动 电解电容', B.CD.cap, '#1155CC', 'U'),
         ('线圈驱动 散热片', B.CD.sink2, '#C0392B', 'U'),
         ('按键支架 key_bracket_v1_2', B.key_bracket, '#F1C232', 'U'), ('按键板 (简模)', B.key_board, '#2E7D32', 'U'),
         ('MR30 座 mr30_seat_v1_2', FS.MW_SEAT, '#F1C232', 'U'), ('电机线夹 motor_wire_clamp_v1_2', FS.MW_CLAMP, '#E69138', 'U')]
# 盘底往上的螺丝 (支承面 = 盘底沉孔底) + 同组螺母 / 铜螺母
UP = [s for s in FS.S if s['up'] and abs(s['bear'] - FS.CB_BEAR) < 1e-6]     # 支承面在盘底沉孔底的都算 (电机/线圈环角/下罩/控制板/XT60/压块/按键/电机线件)
UP_NAMES = {f"{s['group']} #{s['i']}" for s in UP}
UP_TAGS = {s['group'].split(' ', 1)[1] for s in UP}             # 电机 / 线圈环角 / 下罩 / 控制板 / XT60 / MOS压块 / 电容卡件 / 按键支架 / MR30座 / 电机线夹
for n, sh, c in FS.F:
    if n in UP_NAMES:
        PARTS.append((n, sh, '#B0B0B0', 'S'))
    elif ('螺母' in n) and any(t in n for t in UP_TAGS) and '底盘 G' not in n:
        PARTS.append((n, sh, c, 'N'))
SCREW_TXT = sorted({(s['group'], sum(1 for q in UP if q['group'] == s['group'])) for s in UP})

# ---- 网格 / 渲染 (正交轴测, 画家算法) ----
def tris(shape, defl):
    try: V, T = mesh(shape, defl)
    except ValueError: return np.zeros((0, 3, 3))
    return V[T]

MESH = [(n, tris(s, 0.25 if L in 'PGU' else 0.1), np.array(mcolors.to_rgb(c)), L) for n, s, c, L in PARTS]

def basis(az, el):
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])          # 指向观察者
    u = np.array([-math.sin(a), math.cos(a), 0.0]); v = np.cross(d, u)
    return u, v, d

def render(ax, items, az, el):
    u, v, d = basis(az, el)
    allP, allC, allD = [], [], []
    for P, rgb in items:
        if len(P) == 0: continue
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        k = 0.4 + 0.6 * np.abs(n @ (0.6 * d + 0.4 * np.array([0, 0, 1.0])) / np.linalg.norm(0.6 * d + 0.4 * np.array([0, 0, 1.0])))
        allP.append(P); allC.append(np.clip(rgb[None, :] * k[:, None], 0, 1)); allD.append(P.mean(1) @ d)
    P = np.concatenate(allP); C = np.concatenate(allC); D = np.concatenate(allD)
    o = np.argsort(D)
    uv = np.stack([P[o] @ u, P[o] @ v], axis=-1)
    ax.add_collection(PolyCollection(uv, facecolors=C[o], edgecolors='none', antialiased=False, rasterized=True))
    ax.set_aspect('equal'); ax.axis('off'); ax.autoscale_view()

EXPLODE = {'P': -60.0, 'G': -30.0, 'S': -95.0, 'N': 0.0, 'U': 0.0}
def shifted(P, L): return P + np.array([0, 0, EXPLODE[L]]) if len(P) else P

fig = plt.figure(figsize=(16.54, 11.69))
fig.suptitle('POV3D V1.2 — 底座 (打印底盘 4.5 + 玻纤板 3) 与一级连接件 组合图', fontsize=15, y=0.975)
axA = fig.add_axes([0.01, 0.40, 0.42, 0.55]); axE = fig.add_axes([0.42, 0.30, 0.36, 0.66]); axT = fig.add_axes([0.01, 0.02, 0.36, 0.40])
AZ, EL = -60.0, 28.0
render(axA, [(P, c) for _, P, c, _ in MESH], AZ, EL); axA.set_title('装配 (轴测)', fontsize=11)
render(axE, [(shifted(P, L), c) for _, P, c, L in MESH], AZ, EL); axE.set_title('爆炸 (轴测): 盘底螺丝 ↓ / 打印底盘 / 玻纤板 / 一级件', fontsize=11)
# 俯视 (不画底圈, 看得见里面)
u, v, d = basis(-90.0, 90.0)
render(axT, [(P, c) for n, P, c, L in MESH if not n.startswith('底圈')], -90.0, 89.99); axT.set_title('俯视 (不画底圈)', fontsize=11)
for ax in (axA, axE, axT): ax.margins(0.02)

tx = fig.add_axes([0.79, 0.04, 0.20, 0.90]); tx.axis('off')
L = ['底座', f'  打印底盘 Φ{B.DISC_D:g}×{B.PRINT_T:g}  Z{-B.DISC_T:g}..{-B.FR4_T:g}', f'  玻纤板 FR4 Φ{B.DISC_D:g}×{B.FR4_T:g}  Z{-B.FR4_T:g}..0', '',
     '一级连接件 (坐/锁在底座上)']
L += [f'  · {n}' for n, _, _, Lr in PARTS if Lr == 'U']
L += ['', f'盘底往上螺丝 (沉孔 Φ7×{B.M3_CB_H:g}, 超薄头齐底面,', f'  支承 Z{FS.CB_BEAR:g})']
L += [f'  · {g} ×{k}' for g, k in SCREW_TXT]
L += ['', '不在本图: 定子盘 / 安装法兰 (坐线圈环上, 第二层);', f'  中央 8×M3×{FS.L_C:g} 从上往下进打印底盘铜螺母']
tx.text(0, 1, '\n'.join(L), va='top', fontsize=9, linespacing=1.5)
from pathlib import Path
V12 = Path(__file__).resolve().parent.parent
fig.savefig(V12 / 'assembly_v1_2_底座一级件_组合图.pdf', dpi=200); fig.savefig(V12 / 'assembly_v1_2_底座一级件_组合图.png', dpi=110)
write3mf(str(V12 / 'assembly_v1_2_底座一级件.3mf'), [(n, s, c, 0.05) for n, s, c, _ in PARTS])
print('件', sum(1 for p in PARTS if p[3] == 'U'), '螺丝', len(UP), SCREW_TXT)
