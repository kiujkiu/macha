"""V1.2 不装玻璃整机 (用户 11-13 晚「不装玻璃的组和图做一个」; 11-16 按新转子布局重做): 3MF + A3 装配图 (PDF/PNG)。
    cd v1.2/scripts && ../../.venv/bin/python assembly_noglass_v1_2.py
零件 = 玻璃罩版整机 (分体外卡环) 去掉 玻璃罩 / 玻璃上 / 圆环玻璃 / 中心堵头, 加 11-16 转子:
       底板 r3 (+y, 交付 STEP + 未建模器件限高包络 + CZ06) + 两块灯板背靠背 (下沿 B.Z_SCR0) + 灯板支撑 5 件 (post_a/post_b T 脚, gate, top, comb)
       + Φ8×50 轴 + 桥板/天线 (led_support_v1_2) + 转子罩 a/b (rotor_shroud_v1_2) + 无线托盘 + 模块占位 (−y, wireless_holder_v1_2)。
输出: ../assembly_v1_2_不装玻璃_整机+V2板.3mf, ../assembly_v1_2_不装玻璃_装配图.{pdf,png}
"""
import io, contextlib, math
import numpy as np
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
import v2_boards_v1_2 as V
from OCP.gp import gp_Trsf, gp_Vec
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
import led_support_v1_2 as L
import fpc_v1_2 as F                              # 11-16 晚: 桥板真模型 + 两根 FPC 实体 + 双面胶 + 底板真 FPC 座
import rotor_shroud_v1_2 as RS
import wireless_holder_v1_2 as WH
VB = L.VB
CD = B.CD
_ENV_KEEP = [k for k in L.env if not k.startswith(('底面件', 'J3 插头', '24V 线', 'J5', 'J6'))]   # J5/J6 改用 F.seat_j5/j6 真外形   # 底板 r3 交付 STEP 里没 3D 的器件 (框 × 限高)
# 11-16 用户: 灯板贴上真实 LED (MIP-CIMD07TN 4 合 1, 灯板 PCB 坐标 10368 颗/面), 发光面单独换色, 看底座/转子罩挡不挡
_mb, _mt = V.led_mip(B)
LED_BASE = L.comp(list(L.pair(_mb))); LED_TOP = L.comp(list(L.pair(_mt)))   # 11-16 晚 偏心: 随灯板一起 pair() (含 Y_LED 和 ECC)
PARTS = [  # (名, 形状, 颜色, 3MF 弦差)
    ('打印底盘 base_disc_v1_2_gf', B.disc_print, '#8A8F98', 0.05), ('玻纤板 base_fr4_v1_2', B.fr4, '#C8D86A', 0.05), ('线圈环 coil_ring_v1_2', B.ring, '#E0A030', 0.05), ('电机 Φ55×21.5 (占位)', B.motor, '#333333', 0.05),
    ('电机控制板', board, '#2E7D32', 0.08), ('散热片 40×20×6', B.heatsink, '#C0392B', 0.05),
    *([('MOS 压块 mos_clamp_v1_2', CD.clamp, '#E69138', 0.05)] if CD.HAS_MC else []), *([('电容卡件 cap_clamp_v1_2', CD.cap_clamp, '#B45F06', 0.05)] if CD.HAS_CC else []),
    ('线圈驱动板', CD.pcb, '#38761D', 0.05), ('线圈驱动 MOS', CD.mos, '#222222', 0.05), ('线圈驱动 电解电容', CD.cap, '#1155CC', 0.05), ('线圈驱动 散热片', CD.sink2, '#C0392B', 0.05),
    ('按键支架 key_bracket_v1_2', B.key_bracket, '#F1C232', 0.03), ('按键板 (简模)', B.key_board, '#2E7D32', 0.03),
    ('法兰盘 flange_disc_v1_2', B.flange_disc, '#D9A441', 0.05), ('安装法兰 mounting_flange_v1_2', B.mounting_flange, '#B5895A', 0.05),
    ('转子毂盘 hub_disc_v1_2', B.hub, '#4F86C6', 0.05), ('承载盘 rim_ring', B.rim, '#6AA84F', 0.05),
    ('玻璃下-底座 glass_shroud_lower_v1_2', B.shroud_lo, '#7FB3D5', 0.05), ('玻璃下-玻璃座 glass_shroud_upper_v1_2', B.shroud_hi, '#5DADE2', 0.05), ('外卡环 glass_clamp_ring_v1_2', B.clamp_ring, '#2E86C1', 0.05),
    ('XT60 压块', B.xt_clamp, '#F1C232', 0.05), ('XT60 底垫', B.xt_shim, '#E69138', 0.05),
    ('V2 底板 r3 (交付 STEP)', L.bb_step, '#1E8449', 0.05), ('底板 r3 器件包络 + CZ06', L.comp([L.env[k] for k in _ENV_KEEP]), '#7D8C8E', 0.05),
    ('灯板 A (+y)', L.led_a, '#145A32', 0.05), ('灯板 B (-y)', L.led_b, '#0E3B22', 0.05),
    ('MIP LED 4合1 基板部分 (黑) ×2×10368', LED_BASE, '#151515', 0.05), ('MIP LED 4合1 发光面 (红) ×2×10368', LED_TOP, '#FF2020', 0.05),
    ('灯板支撑 +x T 脚 led_post_a', L.post_a, '#F1C232', 0.03), ('灯板支撑 -x T 脚 led_post_b', L.post_b, '#E69138', 0.03), ('灯板夹条 led_bar', L.bar_s, '#8E7CC3', 0.03),
    ('灯板顶部件 led_top', L.top, '#6FA8DC', 0.03), ('灯板梳齿 led_comb', L.comb_s, '#9FC5E8', 0.03),
    (f'Φ8×{L.ROD_L:g} 钢轴', L.rod, '#999999', 0.03), ('桥板 A/B (真模型 V2桥)', L.comp([F.bridge_a, F.bridge_b]), '#1E8449', 0.05), ('FPC A (桥 A → J5)', F.fpc_a, '#E67E22', 0.03), ('FPC B (桥 B → J6)', F.fpc_b, '#D35400', 0.03), ('FPC 双面胶', L.comp([F.tape_a, F.tape_b]), '#F7DC6F', 0.03), ('底板 FPC 座 J5/J6', L.comp([F.seat_j5, F.seat_j6]), '#5D6D7E', 0.03), ('天线 18.5×37.7 软板 ×2', L.comp([L.ant_a, L.ant_b]), '#C0392B', 0.03),
    ('转子罩 a rotor_shroud_a_v1_2', RS.shr_a, '#A4C2F4', 0.05), ('转子罩 b rotor_shroud_b_v1_2', RS.shr_b, '#B6D7A8', 0.05), ('转子罩顶盖 +y rotor_lid_v1_2', RS.lid_a, '#CFE2F3', 0.05), ('转子罩顶盖 −y rotor_lid_b_v1_2', RS.lid_b, '#D9EAD3', 0.05),
    ('无线托盘 wireless_holder_v1_2', WH.H, '#FFD966', 0.03), ('无线供电模块 30.5×49×15 (占位)', WH.module, '#3D85C6', 0.05),
]
# 11-18 整机换成转子盘B (B.ROTOR_B): 毂盘+承载盘 → 玻纤板+承载盘单件; 立板 → 屏幕固定件; 罩子 4 件 → 2 片
POST_N = ('灯板支撑 +x T 脚 led_post_a', '灯板支撑 -x T 脚 led_post_b'); SHR_N = ('转子罩 a rotor_shroud_a_v1_2', '转子罩 b rotor_shroud_b_v1_2')
if B.ROTOR_B:
    import io as _io, contextlib as _cl
    with _cl.redirect_stdout(_io.StringIO()):
        import rotor_shroud_b_v1_2 as RSB
    RB = RSB.RB
    SHR_N = ('转子罩 +y 半 rotor_shroud_b_a_v1_2b', '转子罩 -y 半 rotor_shroud_b_b_v1_2b')
    _new = {'转子毂盘': [('玻纤板 fr4_plate_v1_2b Φ165×3', RB.fr4, '#C9B458', 0.05)], '承载盘 rim_ring': [('承载盘 rim_ring_v1_2b (转子盘B)', RB.rim, '#6AA84F', 0.05)],
            '灯板支撑 +x': [(n, sh, c, 0.03) for n, sh, c in RB.SCREEN_PARTS], '灯板支撑 -x': [],   # 11-21 屏幕支撑件 A ×2 + B ×2 (取代玻纤板 ×4 + 侧立件 ×2)
            '转子罩 a ': [(SHR_N[0], RSB.shr_a, '#A4C2F4', 0.05)], '转子罩 b ': [(SHR_N[1], RSB.shr_b, '#B6D7A8', 0.05)], '转子罩顶盖': []}
    _P = []
    for p_ in PARTS:
        k = next((k for k in _new if p_[0].startswith(k)), None)
        _P += [p_] if k is None else _new[k]
    PARTS = _P
OUT3 = B.V12 / 'assembly_v1_2_不装玻璃_整机+V2板.3mf'
write3mf(str(OUT3), PARTS)
# 11-16 晚 用户: 另出一个不带玻璃托 (玻璃下底座 / 玻璃座 / 外卡环) 的整机 3MF (玻璃本来就不装)
OUT3_NS = B.V12 / 'assembly_v1_2_不装玻璃和玻璃托_整机+V2板.3mf'
write3mf(str(OUT3_NS), [p for p in PARTS if not any(k in p[0] for k in ('玻璃下', '外卡环'))])
# 11-16 晚 用户: 再出一个不带玻璃托、也不带转子罩/顶盖的, 看转子盘和 PCB 的关系
OUT3_NSR = B.V12 / 'assembly_v1_2_不装玻璃玻璃托罩子_转子+PCB.3mf'
write3mf(str(OUT3_NSR), [p for p in PARTS if not any(k in p[0] for k in ('玻璃下', '外卡环', '转子罩'))])
import os as _os
if _os.environ.get('ONLY_3MF'): raise SystemExit(0)

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
_MIP_ENV = {'MIP LED 4合1 基板部分 (黑) ×2×10368': None,
            'MIP LED 4合1 发光面 (红) ×2×10368': L.comp(list(L.pair(B.gbox(-74.88, 0.0, 75.0, 74.88, V.MIP_H, 243.5))))}
# 绘图里 MIP 两万颗小盒子换成每板一块包络 (3MF 里仍是一颗颗; 否则 PDF 57 MB)
MESH = [(n, tris(_MIP_ENV[n] if n in _MIP_ENV else s, max(d, 0.15) if 'LED' not in n else 0.3), mcolors.to_rgb(c)) for n, s, c, d in PARTS if not (n in _MIP_ENV and _MIP_ENV[n] is None)]

def slab(shape, x0, x1):
    c = BRepAlgoAPI_Common(shape, BRepPrimAPI_MakeBox(gp_Pnt(x0, -150, -50), gp_Pnt(x1, 150, 400)).Shape()); c.Build()
    return c.Shape()

fig = plt.figure(figsize=(16.54, 11.69))                        # A3 横
fig.suptitle('POV3D V1.2 — 不装玻璃整机 + V2 转子 (底板 r3 / 灯板 Z%g / 转子罩 / 无线托盘)    装配图' % B.Z_SCR0, fontsize=15, y=0.975)
axF = fig.add_axes([0.03, 0.12, 0.33, 0.80]); axS = fig.add_axes([0.37, 0.12, 0.27, 0.80]); axT = fig.add_axes([0.76, 0.50, 0.22, 0.42])
# 主视图: 从 +Y 看 (看 LED 面), 屏幕右 = -X
render(axF, [(P, c) for _, P, c in MESH], 0, 2, 1, (0, 1, 0), flip_u=True)
axF.set_title('主视图 (从 +Y 看 LED 面)', fontsize=11)
# 剖视 A-A: X=0 平面, 只画 X∈[−0.05, 0.05] 薄片 (= 剖面), 从 +X 看; 后面加 X<0 半边淡色
SEC = [(n, tris(slab(s, -0.05, 0.05), 0.1), mcolors.to_rgb(c)) for n, s, c, d in PARTS if not n.startswith('MIP')]
BACK = [(n, tris(slab(s, -200, -0.05), max(d, 0.2)), mcolors.to_rgb(c)) for n, s, c, d in PARTS if not n.startswith('MIP')]   # 2 万颗小盒子剖切太慢; 剖视里 LED 只有 0.59 厚, 省掉
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
LV = [(0, '底盘顶 Z0'), (B.Z_RIM_TOP, f'承载盘顶 / 罩底 Z{B.Z_RIM_TOP:g}'), (B.Z_BB0, f'底板 r3 底 Z{B.Z_BB0:g} (垫 {B.BB_STANDOFF:g})'),
      (B.Z_SCR0, f'灯板下沿 Z{B.Z_SCR0:g} (承载盘顶 +{B.SCREEN_GAP:g})'), (B.Z_BB0 + B.BB_T + B.CZ06_H, f'CZ06 顶 Z{B.Z_BB0 + B.BB_T + B.CZ06_H:g}'),
      (WH.MZ1, f'无线模块顶 Z{WH.MZ1:g}'), (B.Z_G, f'玻璃下端 Z{B.Z_G:g} (不装)'), (RS.Z1, f'转子罩顶 Z{RS.Z1:g}'),
      (B.Z_VIEW0, f'内卡顶 (可视下边界) Z{B.Z_VIEW0:g}'), (B.Z_LED0, f'LED 下沿 Z{B.Z_LED0:g}'), (B.Z_SCR1, f'灯板上沿 Z{B.Z_SCR1:g}')]
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
_LED2 = L.comp([L.led_a, L.led_b])
D_BB, D_CZ = _dist(_LED2, L.bb_step), _dist(_LED2, VB['cz06'])
D_WH = _dist(_LED2, L.comp([WH.H, WH.module]))
_M = dict((n, P) for n, P, _ in MESH)
R_LED = max(float(np.hypot(_M[k][:, :, 0], _M[k][:, :, 1]).max()) for k in ('灯板 A (+y)', '灯板 B (-y)', *POST_N, '天线 18.5×37.7 软板 ×2'))
R_SHR = max(float(np.hypot(_M[k][:, :, 0], _M[k][:, :, 1]).max()) for k in SHR_N)
assert R_SHR < B.SPIG_IN - 1.0 and R_LED < RS.R1 - 0.1 + 1e-6 and D_BB > 0.5 and D_CZ > 0.5 and D_WH > 0.5, (R_SHR, R_LED, D_BB, D_CZ, D_WH)
print('clearance', D_BB, D_CZ, D_WH, R_LED, R_SHR)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(fc=c, label=n) for n, _, c in MESH], loc='upper left', bbox_to_anchor=(0.745, 0.46), fontsize=7, ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
note = [f'玻璃罩 OD{B.GL_OD:g}×{B.GL_T:g}×{B.GL_H:g} / 玻璃上 / 圆环玻璃 / 中心堵头 不装; 装上后玻璃上端 Z{B.Z_GT:g} (Φ8 轴进玻璃上盖 688, 不装玻璃时轴悬空)',
        f'V2 转子 (11-16): 底板 r3 在 +y, 垫 {B.BB_STANDOFF:g} + 板 {B.BB_T:g} (底 Z{B.Z_BB0:g}); CZ06 在底板上 (顶 Z{B.Z_BB0 + B.BB_T + B.CZ06_H:g}, 不在灯板下); 灯板下沿 = 承载盘顶 + {B.SCREEN_GAP:g} = Z{B.Z_SCR0:g}',
        f'灯板背靠背 (F 面 y=±{L.GAP_HALF:g}); 偏心 SCR_ECC {B.SCR_ECC:g} (板 A MIP 顶在轴线); 两端立板耳朵脚压外圈锁盘螺丝 (4×M3×{L.FOOT_SCREW_L:g} 进毂盘底铜螺母) + 夹条 (两板之间, H1/H2 M3 横穿, 两端 2×M3 自攻) + 顶部件 + 梳齿配平 (2×M3×8)',
        f'转子罩 a/b (r{RS.R0:g}–{RS.R1:g}, Z{RS.Z0:g}–{RS.Z1:g}, 同一件转 180°): 罩底 4×M3×{RS.MNT_L:g} 进毂盘底铜螺母, 分缝 4×M3×{RS.SEAM_L:g} + 螺母, 配重唇 {len(RS.W_A)} 孔 M3×{RS.W_L:g} 按需',
        f'无线托盘 (-y 侧) 3×M3×8 进承载盘铜螺母, 模块 30.5×49×15 Z{WH.MZ0:g}–{WH.MZ1:g}; 底板器件按 F.CrtYd × 限高做方块 (交付 STEP 无 3D 的件), 不是实物',
        f'实测: 灯板-底板 r3 最近 {D_BB:.2f}, 灯板-CZ06 {D_CZ:.2f}, 灯板-无线托盘/模块 {D_WH:.2f}; 灯板/立板/天线最大半径 {R_LED:.2f} (天线板外角, 在罩壁 ±x 缝 |y|≤{RS.SLOT_Y:g} 里; 罩外圆 r{RS.R1:g}, 余 {RS.R1 - R_LED:.2f}); 转子罩外 r{R_SHR:.2f} (玻璃下内面 r{B.SPIG_IN:g}, 余 {B.SPIG_IN - R_SHR:.2f})']
if B.ROTOR_B:
    note[2] = (f'灯板背靠背 (F 面 y=±{L.GAP_HALF:g}); 偏心 SCR_ECC {B.SCR_ECC:g}; 转子盘B: 玻纤板 Φ165×3 + 承载盘单件 (并入毂盘, 线圈腔深 {RB.CAV_H:g}); '
               f'屏幕支撑件 PETG 打印 A ×2 (0/180°, 托灯板) + B ×2 (90/270°), Z{RB.SP_Z0:g}–{RB.SP_Z1:g}; 外圈 8×M3×{RB.OUT_SCR_L:g} 从玻纤板底穿上来 (承载盘+支撑件) 进支撑件顶面嵌入法兰螺母; 夹条 / 顶部件 / 梳齿同前')
    note[3] = (f'转子罩 2 片 (沿灯板线 y{RSB.SPLIT_Y:g} 分, 各带顶盖; r{RSB.R0:g}–{RSB.R1:g}, Z{RSB.Z0:g}–{RSB.Z1:g}): '
               f'8 耳坐支撑件顶 (A 件本地 (61, ±30.5) / B 件 ({RB.SHR_LOC_X:g}, ±{RB.SHR_LOC_Y:g})), DIN912 M3×{RSB.MNT_L:g} 从耳顶往下进支撑件底面倒扣法兰螺母; 配重唇 {len(RSB.W_A)} 孔 M3×{RS.W_L:g} 从罩顶插, 按需')
fig.text(0.03, 0.025, '\n'.join('· ' + s for s in note), fontsize=8, va='bottom')
fig.text(0.98, 0.012, f'v1.2/scripts/assembly_noglass_v1_2.py  2026-11-18 (转子盘B)' if B.ROTOR_B else 'v1.2/scripts/assembly_noglass_v1_2.py  2026-11-16', fontsize=7, ha='right', color='#666')
OUT2 = B.V12 / 'assembly_v1_2_不装玻璃_装配图'
fig.savefig(f'{OUT2}.pdf'); fig.savefig(f'{OUT2}.png', dpi=110)
print('wrote', OUT3, f'{OUT2}.pdf')
