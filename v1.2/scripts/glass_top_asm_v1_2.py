"""V1.2 玻璃上 2 件 (红 glass_top_v1_2 顶环 + 绿 glass_top_clamp_v1_2 压圈) 组合图 (用户 11-18「玻璃上的2个件组合一下」)。
带: 圆环玻璃 (外购) + 上下硅胶垫 + 中心堵头 glass_top_hub_v1_2 + 玻璃罩上端一段 + 8×M3 压圈螺丝 / 铜螺母。
    cd v1.2/scripts && ../../.venv/bin/python glass_top_asm_v1_2.py
输出: ../assembly_v1_2_玻璃上_组合图.{pdf,png} + ../assembly_v1_2_玻璃上.3mf
"""
import io, contextlib, math
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import fasteners_v1_2 as FS
from mf3_v1_2 import mesh, write3mf
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager, colors as mcolors
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False

TUBE_L = 30.0
tube = B.ann(B.gi, B.go, B.Z_GT - TUBE_L, B.Z_GT)
# 层: T 玻璃罩 / R 红件 / D 玻璃+垫 / H 堵头 / C 绿件 / S 螺丝 / N 法兰螺母
PARTS = [(f'玻璃罩 Φ{B.GL_OD:g}×{B.GL_T:g} 上端 (截 {TUBE_L:g})', tube, '#A9CCE3', 'T'),
         ('红: 玻璃上环 glass_top_v1_2', B.glass_top, '#D9534F', 'R'),
         ('下硅胶垫 OD180×ID171×1', B.glass_gasket_bot, '#333333', 'D'),
         (f'圆环玻璃 OD{B.GD_OD:g}/ID{B.GD_ID:g}/t{B.GD_T:g} (外购)', B.glass_disc, '#BFE3F2', 'D'),
         ('上硅胶垫 OD180×ID171×1', B.glass_gasket_top, '#333333', 'D2'),
         ('中心堵头 glass_top_hub_v1_2', B.glass_top_hub, '#F1C232', 'H'),
         ('绿: 压圈 glass_top_clamp_v1_2', B.glass_top_clamp, '#5CB85C', 'C')]
NP = len(PARTS)
for n, sh, c in FS.F:
    if '玻璃上绿件' in n: PARTS.append((n, sh, '#B0B0B0', 'S'))
    elif '玻璃上红件底' in n: PARTS.append((n, sh, c, 'N'))
cnt = lambda L_: sum(1 for p in PARTS if p[3] == L_)

def tris(shape, defl):
    try: V, T = mesh(shape, defl)
    except ValueError: return np.zeros((0, 3, 3))
    return V[T]
def half(sh):                                     # 留 y≥0 一半 (剖切)
    return BRepAlgoAPI_Common(sh, B.gbox(-200, 0, -10, 200, 200, 400)).Shape()
MESH = [(n, tris(s, 0.1), np.array(mcolors.to_rgb(c)), L_) for n, s, c, L_ in PARTS]
HALF = [(n, tris(half(s), 0.1), np.array(mcolors.to_rgb(c)), L_) for n, s, c, L_ in PARTS]

def basis(az, el):
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    u = np.array([-math.sin(a), math.cos(a), 0.0]); v = np.cross(d, u)
    return u, v, d
def render(ax, items, az, el, lim=None):
    u, v, d = basis(az, el); allP, allC, allD = [], [], []
    lt = 0.6 * d + 0.4 * np.array([0, 0, 1.0]); lt /= np.linalg.norm(lt)
    for P, rgb in items:
        if len(P) == 0: continue
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        allP.append(P); allC.append(np.clip(rgb[None, :] * (0.4 + 0.6 * np.abs(n @ lt))[:, None], 0, 1)); allD.append(P.mean(1) @ d)
    P = np.concatenate(allP); C = np.concatenate(allC); D = np.concatenate(allD); o = np.argsort(D)
    ax.add_collection(PolyCollection(np.stack([P[o] @ u, P[o] @ v], axis=-1), facecolors=C[o], edgecolors='none', antialiased=False, rasterized=True))
    ax.set_aspect('equal'); ax.axis('off')
    if lim: ax.set_xlim(*lim[:2]); ax.set_ylim(*lim[2:])
    else: ax.autoscale_view(); ax.margins(0.02)

EXP = {'T': -45.0, 'R': -15.0, 'D': 10.0, 'D2': 22.0, 'H': 45.0, 'C': 35.0, 'S': 60.0, 'N': -15.0}
fig = plt.figure(figsize=(16.54, 11.69))
fig.suptitle('POV3D V1.2 — 玻璃上 2 件组合 (红 顶环 glass_top + 绿 压圈 glass_top_clamp)', fontsize=15, y=0.985)
AZ, EL = -60.0, 25.0
axA = fig.add_axes([0.00, 0.50, 0.27, 0.43]); axH = fig.add_axes([0.27, 0.50, 0.27, 0.43]); axE = fig.add_axes([0.54, 0.50, 0.26, 0.43])
axS = fig.add_axes([0.02, 0.03, 0.52, 0.44]); axR = fig.add_axes([0.56, 0.03, 0.24, 0.44])
render(axA, [(P, c) for _, P, c, _ in MESH], AZ, EL); axA.set_title('装配 (轴测)', fontsize=11)
render(axH, [(P, c) for _, P, c, _ in HALF], AZ, EL); axH.set_title('剖开一半 (留 y≥0)', fontsize=11)
render(axE, [(P + np.array([0, 0, EXP[L_]]) if len(P) else P, c) for _, P, c, L_ in MESH], AZ, EL); axE.set_title('爆炸', fontsize=11)
# 剖面 (看 +y, 剖面 y=0): 局部放大右侧 r80..112, 过一颗压圈螺丝 (22.5° 不在 y=0 ⇒ 另转一份到 y=0)
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir
rt = gp_Trsf(); rt.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(-22.5))
SEC = [(tris(half(B.xf(s, rt)), 0.05), np.array(mcolors.to_rgb(c))) for n, s, c, L_ in PARTS]
z0, z1 = B.Z_GT - 12, B.GC_Z1 + 3
render(axS, SEC, -90.0, 0.01, lim=(78, 113, z0, z1)); axS.set_title('剖面局部 (过压圈螺丝, r78–113)  坐标: 横 = 半径 mm, 竖 = Z mm', fontsize=11)
for z, t in [(B.Z_GT, f'玻璃罩上端 Z{B.Z_GT:.2f}'), (B.GD_Z0, f'玻璃底 Z{B.GD_Z0:.2f}'), (B.GD_Z1, f'玻璃顶 Z{B.GD_Z1:.2f}'),
             (B.GT_Z1, f'红件顶 = 绿件底 Z{B.GT_Z1:.2f} (硬限位)'), (B.GC_Z1, f'绿件顶 Z{B.GC_Z1:.2f}')]:
    axS.axhline(z, color='#888', lw=0.4, ls=':'); axS.text(78.3, z + 0.15, t, fontsize=7.5, color='#444')
for r in (B.gi, B.go, B.GD_OD / 2, B.GC_R):
    axS.axvline(r, color='#c00', lw=0.3, ls='-.'); axS.text(r + 0.1, z0 + 0.3, f'r{r:.2f}'.rstrip('0').rstrip('.'), fontsize=7, color='#c00', rotation=90)
axS.axis('on'); axS.tick_params(labelsize=7)
render(axR, [(P, c) for n, P, c, _ in MESH if n.startswith(('红', '玻璃罩'))], AZ, EL); axR.set_title('红件坐在玻璃罩上端 (无绿件/玻璃)', fontsize=11)

tx = fig.add_axes([0.81, 0.04, 0.18, 0.90]); tx.axis('off')
T = ['件'] + [f'  · {n}' for n, _, _, _ in PARTS[:NP]]
T += ['', f'螺丝: M3×{B.GC_SCREW_L:g} 超薄头 Φ{B.GC_HEAD_D:g}×{B.GC_HEAD_H:g} ×{cnt("S")}', f'  r{B.GC_R:.2f} @22.5°+45°k, 从绿件顶往下', f'  支承 Z{B.GC_BEAR:.2f} → 尖 Z{B.GC_TIP:.2f}',
      f'M3 法兰螺母 ×{cnt("N")} (红件底面圆沉孔 Φ{B.GC_NUT_D:g}×{B.GC_NUT_H:g}, 法兰朝上)', f'  Z{B.GC_NUT_Z[0]:.2f}–{B.GC_NUT_Z[1]:.2f}, 吃 {B.GC_ENG:g}; 被管端面挡住',
      '', f'硅胶垫 厚 {B.GK_T:g}, 压后 {B.GK_H:g} (压缩 {B.GK_COMP*100:g}%)', '  绿件底落红件顶 = 硬限位, 压缩量固定', '',
      '装配:', '  1 红件翻面塞 8 颗法兰螺母 (点胶)', '  2 翻正: 下垫 → 圆环玻璃 (带堵头) → 上垫', '  3 绿件盖上, 8×M3×20 拧到底', '  4 整组套上玻璃罩上端 (轴进 688)']
tx.text(0, 1, '\n'.join(T), va='top', fontsize=8, linespacing=1.5)
fig.text(0.99, 0.008, 'v1.2/scripts/glass_top_asm_v1_2.py  2026-11-25', fontsize=7, ha='right', color='#666')
try: fig.savefig(B.V12 / 'assembly_v1_2_玻璃上_组合图.pdf', dpi=200)
except PermissionError: fig.savefig(B.V12 / 'assembly_v1_2_玻璃上_组合图.NEW.pdf', dpi=200); print('组合图 PDF 被占用, 另存 .NEW.pdf')   # 正被阅读器打开
fig.savefig(B.V12 / 'assembly_v1_2_玻璃上_组合图.png', dpi=110)
write3mf(str(B.V12 / 'assembly_v1_2_玻璃上.3mf'), [(n, s, c, 0.05) for n, s, c, _ in PARTS])
print('件', NP, '螺丝', cnt('S'), '法兰螺母', cnt('N'))
