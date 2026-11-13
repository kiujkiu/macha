"""V1.2 不装玻璃整机 (用户 11-13 晚「不装玻璃的组和图做一个」): 3MF + A3 装配图 (PDF/PNG)。
    cd v1.2/scripts && ../../.venv/bin/python assembly_noglass_v1_2.py
零件 = 玻璃罩版整机 (分体外卡环) 去掉 玻璃罩 / 玻璃上 / 圆环玻璃 / 中心堵头, 加 V2 转子电路占位 (v2_boards_v1_2: 转接板 + CZ06 + 1 块灯板)。
输出: ../assembly_v1_2_不装玻璃_整机+V2板.3mf, ../assembly_v1_2_不装玻璃_装配图.{pdf,png}
"""
import io, contextlib, math
import numpy as np
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
import v2_boards_v1_2 as V
from mf3_v1_2 import mesh, write3mf
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt

# 控制板去掉 < 1.2 的小件 (同 export_3mf_v1_2)
_b = BRep_Builder(); board = TopoDS_Compound(); _b.MakeCompound(board)
for s in B.solids(B.board):
    bb = B.bbox(s)
    if max(bb[3] - bb[0], bb[4] - bb[1]) >= 1.2 or bb[5] - bb[2] >= 1.0: _b.Add(board, s)
VB = V.make(B)
CD = B.CD
PARTS = [  # (名, 形状, 颜色, 3MF 弦差)
    ('底盘 base_disc_v1_2', B.disc, '#8A8F98', 0.05), ('线圈环 coil_ring_v1_2', B.ring, '#E0A030', 0.05), ('电机 Φ55×21.5 (占位)', B.motor, '#333333', 0.05),
    ('电机控制板', board, '#2E7D32', 0.08), ('散热片 40×20×6', B.heatsink, '#C0392B', 0.05),
    *([('MOS 压块 mos_clamp_v1_2', CD.clamp, '#E69138', 0.05)] if CD.HAS_MC else []), *([('电容卡件 cap_clamp_v1_2', CD.cap_clamp, '#B45F06', 0.05)] if CD.HAS_CC else []),
    ('线圈驱动板', CD.pcb, '#38761D', 0.05), ('线圈驱动 MOS', CD.mos, '#222222', 0.05), ('线圈驱动 电解电容', CD.cap, '#1155CC', 0.05), ('线圈驱动 散热片', CD.sink2, '#C0392B', 0.05),
    ('按键支架 key_bracket_v1_2', B.key_bracket, '#F1C232', 0.03), ('按键板 (简模)', B.key_board, '#2E7D32', 0.03),
    ('法兰盘 flange_disc_v1_2', B.flange_disc, '#D9A441', 0.05), ('安装法兰 mounting_flange_v1_2', B.mounting_flange, '#B5895A', 0.05),
    ('转子毂盘 hub_disc_v1_2', B.hub, '#4F86C6', 0.05), ('承载盘 rim_ring', B.rim, '#6AA84F', 0.05),
    ('玻璃下 (分体下罩) glass_shroud_split_v1_2', B.shroud_split, '#7FB3D5', 0.05), ('外卡环 glass_clamp_ring_v1_2', B.clamp_ring, '#2E86C1', 0.05),
    ('XT60 压块', B.xt_clamp, '#F1C232', 0.05), ('XT60 底垫', B.xt_shim, '#E69138', 0.05),
    ('V2 转接板 140×80 (占位)', VB['baseboard'], '#1E8449', 0.05), ('V2 转接板器件 (限高包络)', VB['bb_parts'], '#7D8C8E', 0.05),
    ('CZ06 核心板 (6.6 包络)', VB['cz06'], '#5B2C6F', 0.05), ('V2 灯板 LED_V0.2.0 (1 块, 位置参考)', VB['led'], '#145A32', 0.05),
]
OUT3 = B.V12 / 'assembly_v1_2_不装玻璃_整机+V2板.3mf'
write3mf(str(OUT3), PARTS)

# ---------------- 装配图 ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager, colors as mcolors
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False

def tris(shape, defl):
    try: Vv, T = mesh(shape, defl)
    except ValueError: return np.zeros((0, 3, 3))                # 空 (切片里没有这个件)
    return Vv[T]                                                 # (n,3,3)

def shade(P, rgb, view):
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    k = 0.45 + 0.55 * np.abs(n @ np.asarray(view, float))
    return np.clip(np.asarray(rgb)[None, :] * k[:, None], 0, 1)

def render(ax, items, ax_u, ax_v, depth, view, flip_u=False):
    """items: [(tris, rgb)]; 投影到 (u,v), 按 depth 从远到近画 (画家算法)"""
    allP, allC, allD = [], [], []
    for P, rgb in items:
        if len(P) == 0: continue
        allP.append(P); allC.append(shade(P, rgb, view)); allD.append(P[:, :, depth].mean(1) * (1 if view[depth] < 0 else -1))
    P = np.concatenate(allP); Cc = np.concatenate(allC); D = np.concatenate(allD)
    o = np.argsort(D)[::-1]                                      # 远 → 近
    uv = P[o][:, :, [ax_u, ax_v]].copy()
    if flip_u: uv[:, :, 0] *= -1
    ax.add_collection(PolyCollection(uv, facecolors=Cc[o], edgecolors='none', antialiased=False))

print('meshing ...', flush=True)
MESH = [(n, tris(s, max(d, 0.15) if 'LED' not in n else 0.3), mcolors.to_rgb(c)) for n, s, c, d in PARTS]

def slab(shape, x0, x1):
    c = BRepAlgoAPI_Common(shape, BRepPrimAPI_MakeBox(gp_Pnt(x0, -150, -50), gp_Pnt(x1, 150, 400)).Shape()); c.Build()
    return c.Shape()

fig = plt.figure(figsize=(16.54, 11.69))                        # A3 横
fig.suptitle('POV3D V1.2 — 不装玻璃整机 + V2 转子电路 (占位)    装配图', fontsize=15, y=0.975)
axF = fig.add_axes([0.03, 0.12, 0.33, 0.80]); axS = fig.add_axes([0.37, 0.12, 0.27, 0.80]); axT = fig.add_axes([0.76, 0.50, 0.22, 0.42])
# 主视图: 从 +Y 看 (看 LED 面), 屏幕右 = -X
render(axF, [(P, c) for _, P, c in MESH], 0, 2, 1, (0, 1, 0), flip_u=True)
axF.set_title('主视图 (从 +Y 看 LED 面)', fontsize=11)
# 剖视 A-A: X=0 平面, 只画 X∈[−0.05, 0.05] 薄片 (= 剖面), 从 +X 看; 后面加 X<0 半边淡色
SEC = [(n, tris(slab(s, -0.05, 0.05), 0.1), mcolors.to_rgb(c)) for n, s, c, d in PARTS]
BACK = [(n, tris(slab(s, -200, -0.05), max(d, 0.2)), mcolors.to_rgb(c)) for n, s, c, d in PARTS]
render(axS, [(P, tuple(0.55 + 0.45 * np.array(c))) for _, P, c in BACK], 1, 2, 0, (1, 0, 0))
render(axS, [(P, c) for _, P, c in SEC], 1, 2, 0, (1, 0, 0))
axS.set_title('剖视 A-A (X=0 平面, 从 +X 看; 浅色 = 剖面后的半边)', fontsize=11)
# 俯视 (Z 从上往下)
render(axT, [(P, c) for _, P, c in MESH], 0, 1, 2, (0, 0, 1))
axT.set_title('俯视 (从 +Z 看)', fontsize=11)
for ax in (axF, axS, axT):
    ax.set_aspect('equal'); ax.tick_params(labelsize=7); ax.grid(lw=0.2, color='#ccc')
axF.set_xlim(-118, 118); axF.set_ylim(-10, 270); axS.set_xlim(-118, 118); axS.set_ylim(-10, 270); axT.set_xlim(-115, 115); axT.set_ylim(-115, 115)
axF.set_xlabel('-X (mm)', fontsize=8); axS.set_xlabel('Y (mm)', fontsize=8); axT.set_xlabel('X', fontsize=8); axT.set_ylabel('Y', fontsize=8)
axT.plot([0, 0], [-112, 112], 'r-.', lw=0.8); axT.text(2, 105, 'A', color='r'); axT.text(2, -112, 'A', color='r')
# 标高
LV = [(0, '底盘顶 Z0'), (B.Z_RIM_TOP, f'承载盘顶 Z{B.Z_RIM_TOP:g}'), (B.Z_BB0, f'转接板底 Z{B.Z_BB0:g} (垫 {B.BB_STANDOFF:g})'),
      (B.Z_BB0 + B.BB_T + B.CZ06_H, f'CZ06 顶 Z{B.Z_BB0 + B.BB_T + B.CZ06_H:g}'), (B.Z_SCR0, f'灯板下沿 Z{B.Z_SCR0:g}'),
      (B.Z_G, f'玻璃下端 Z{B.Z_G:g} (不装)'), (B.Z_LED0, f'LED 下沿 = 内卡顶 Z{B.Z_LED0:g}'), (B.Z_SCR1, f'灯板上沿 Z{B.Z_SCR1:g}')]
LV.sort(); zt_ = []                                              # 标签往上推开, 最小间隔 7 (数据单位), 引线连回标高
for z, t in LV:
    zt_.append(max(z, zt_[-1] + 7.0) if zt_ else z)
for (z, t), zl in zip(LV, zt_):
    for ax in (axF, axS): ax.axhline(z, color='#C0392B', lw=0.4, ls='--')
    axS.annotate(t, xy=(118, z), xytext=(128, zl), fontsize=7.5, va='center', ha='left', color='#922B21', annotation_clip=False,
                 arrowprops=dict(arrowstyle='-', lw=0.4, color='#C0392B'))
# 图例 + 说明
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def _dist(a, b):
    d = BRepExtrema_DistShapeShape(a, b); d.Perform(); return d.Value()
D_BB, D_CZ = _dist(VB['led'], VB['bb_parts']), _dist(VB['led'], VB['cz06'])
_PL = dict((n, P) for n, P, _ in MESH)['V2 灯板 LED_V0.2.0 (1 块, 位置参考)']
R_LED = float(np.hypot(_PL[:, :, 0], _PL[:, :, 1]).max())
assert R_LED < B.SPIG_IN - 1.0 and D_BB > 0.5 and D_CZ > 0.5, (R_LED, D_BB, D_CZ)
print('clearance', D_BB, D_CZ, R_LED)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(fc=c, label=n) for n, _, c in MESH], loc='upper left', bbox_to_anchor=(0.745, 0.46), fontsize=7, ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
note = [f'玻璃罩 OD{B.GL_OD:g}×{B.GL_T:g}×{B.GL_H:g} / 玻璃上 / 圆环玻璃 / 中心堵头 不装; 装上后玻璃上端 Z{B.Z_GT:g}',
        f'V2 转子: 转接板 140×80×{B.BB_T:g} 垫 {B.BB_STANDOFF:g} + CZ06 {B.CZ06_H:g} + 留 {B.CZ06_CLR:g} = 灯板下沿 Z{B.Z_SCR0:g}',
        '转接板器件按 F.CrtYd 外框 × 限高 (VH 10 / 电解 10.8 / 牛角 9 等) 做方块, 不是实物 3D',
        '灯板只放 1 块 (板背贴 Y=0, LED 面朝 +Y); 两块背靠背的间距/偏心未定, 桥板/FPC 未建',
        f'实测: 灯板-转接板器件最近 {D_BB:.2f}, 灯板-CZ06 {D_CZ:.2f}, 灯板最大转动半径 {R_LED:.2f} (玻璃下内面 r{B.SPIG_IN:g}, 余 {B.SPIG_IN - R_LED:.2f})']
fig.text(0.03, 0.025, '\n'.join('· ' + s for s in note), fontsize=8, va='bottom')
fig.text(0.98, 0.012, f'v1.2/scripts/assembly_noglass_v1_2.py  2026-11-13', fontsize=7, ha='right', color='#666')
OUT2 = B.V12 / 'assembly_v1_2_不装玻璃_装配图'
fig.savefig(f'{OUT2}.pdf'); fig.savefig(f'{OUT2}.png', dpi=110)
print('wrote', OUT3, f'{OUT2}.pdf')
