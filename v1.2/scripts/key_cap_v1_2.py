# -*- coding: utf-8 -*-
"""按键帽 key_cap_v1_2 —— 标准件占位 + 叠层核算 + 建议外皮开孔 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python key_cap_v1_2.py
输出 v1.2/models/key_cap_v1_2/: key_cap_v1_2.step/.stl (局部姿态: 轴 +Z, 底面 z0) + key_cap_stack_preview.png (剖面叠层)

用户 11-13 图纸: 帽身 Φ5.5, 总高 4.5 (底面→顶), 顶面球面 R15.1; 底部裙边 Φ7.4 厚 0.5; 内孔 Φ3.1 / Φ3.4 两档, 深 3.4 (从底面算)。
  内孔选型: 6×6 轻触开关圆杆 (高 ≥5 的规格) 规格书多为 Φ3.5 (±0.1, 部分品牌 Φ3.4); Φ3.4 孔套 Φ3.5 杆 = 单边 0.05 过盈, 是配 6×6 圆杆的那一档
  ⇒ 默认 BORE_D 3.4。Φ3.1 那档配细杆 (Φ3.0–3.2 的小型/贴片 6×6、4.5×4.5 等), 本机不用。
  帽靠内孔底压在杆顶 ⇒ 帽底面 = 杆顶 − BORE_H; 帽顶 = 杆顶 + (CAP_H − BORE_H) = 杆顶 + 1.1。

叠层 (整机 y, 板正面 y100.6; 按键在板系 (11,14.5)/(11,5.5) → 整机 x9, Z17.5 / 8.5; 外皮 r110 圆柱在 x9 处 y109.631):
  开关高 H → 杆顶 100.6+H, 帽底 杆顶−3.4, 裙边顶 帽底+0.5, 帽顶 杆顶+1.1。外露 e = 帽顶 − 109.631。
  H7: 帽顶 108.70 (缩在外皮里 0.93), 且帽底离本体顶只 0.10 < 行程 0.25 (按下裙边顶到开关本体) ⇒ 不成立。
  H9 (推荐): 杆顶 109.6, 帽底 106.2, 裙边顶 106.7, 帽顶 110.7 ⇒ 外露 1.07 (圆柱面上帽边 0.63 / 1.08)。

装配 (结论): "帽先套按键再竖直罩下罩" 不可行 —— 帽身 (y106.7..110.7) 穿过外皮外表面, 罩下时外皮要整条让开 ⇒ 外面看得见的通槽。
  建议: 下罩罩下时 支架+板+帽 整体先往里退 ASSY_DY (=4.2), 帽全在裙边让位面 y(裙边顶+0.2) 以下; 罩好后整体沿 +y 推出 ASSY_DY,
  帽身沿自身轴线插进外皮 Φ5.9 孔, 裙边进让位; 再从盘底拧 2×M3。让位腔 = 原外包 y 向往里扫 ASSY_DY (腔内面打穿墙内面 r90.8, 机内开窗)。
不 import build_v1_2 / key_bracket_v1_2 (只读 key_board_outline_v1_2 常数)。"""
import math
from pathlib import Path

from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Ax1
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer

import key_board_outline_v1_2 as KB

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_cap_v1_2'

# ---- 图纸尺寸 ----
CAP_D, CAP_H, TOP_R = 5.5, 4.5, 15.1      # 帽身 / 总高 / 顶球面
FLANGE_D, FLANGE_T = 7.4, 0.5             # 裙边
BORE_D, BORE_H = 3.4, 3.4                 # 内孔 (配 Φ3.5 圆杆; 另一档 3.1)
BORE_D_ALT = 3.1
TOP_SAG = TOP_R - math.sqrt(TOP_R ** 2 - (CAP_D / 2) ** 2)   # 0.2525 顶球面拱高
# ---- 建议 ----
SW_H = 9.0                                # 推荐开关 6×6×9 (杆 Φ3.5, 杆顶离板面 9; 本体高 3.5)
SW_BODY_H, SW_TRAVEL = 3.5, 0.25
SKIN_HOLE_D = 5.9                         # 外皮帽孔 (单边 0.2)
FLANGE_CLR_D = 8.2                        # 裙边让位 (单边 0.4); 让位腔用方截面宽 8.0 → 见 skin_cuts
FLANGE_GAP = 0.2                          # 不按时裙边顶 → 外皮让位面
ASSY_DY = 4.2                             # 装配: 支架组件先往里退 4.2, 罩下罩后推出
CLR = 0.3                                 # 让位腔单边间隙 (同 key_bracket CLR)
SH_OUT = 110.0
SKIN_MIN = 1.5

DEFAULTS = dict(CAP_D=CAP_D, CAP_H=CAP_H, TOP_R=TOP_R, FLANGE_D=FLANGE_D, FLANGE_T=FLANGE_T, BORE_D=BORE_D, BORE_H=BORE_H)


def op(cls, a, b):
    o = cls(a, b); o.Build(); assert o.IsDone(); return o.Shape()
def cyl(x, y, d, z0, z1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), d / 2, z1 - z0).Shape()
def ycyl(x, z, d, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), d / 2, y1 - y0).Shape()
def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)), gp_Pnt(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()


def make_key_cap(p=None):
    """局部姿态: 轴 +Z, 底面 z0 (裙边底), 顶球面顶点 z = CAP_H"""
    P = dict(DEFAULTS, **(p or {}))
    body = cyl(0, 0, P['CAP_D'], 0, P['CAP_H'])
    sph = BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, P['CAP_H'] - P['TOP_R']), P['TOP_R']).Shape()
    body = op(BRepAlgoAPI_Common, body, sph)
    s = op(BRepAlgoAPI_Fuse, body, cyl(0, 0, P['FLANGE_D'], 0, P['FLANGE_T']))
    s = op(BRepAlgoAPI_Cut, s, cyl(0, 0, P['BORE_D'], -1, P['BORE_H']))
    u = ShapeUpgrade_UnifySameDomain(s, True, True, True); u.Build(); s = u.Shape()
    assert BRepCheck_Analyzer(s).IsValid()
    return s


def place_cap(cap, x, z, y_bottom):
    """局部 (+Z 轴, 底 z0) → 整机: 轴沿 +y, 底面在 y_bottom, 中心 (x, z)"""
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -math.pi / 2)   # +Z → +Y
    t2 = gp_Trsf(); t2.SetTranslation(gp_Pnt(0, 0, 0), gp_Pnt(x, y_bottom, z))
    return BRepBuilderAPI_Transform(cap, t2.Multiplied(t), True).Shape()


def y_out(x):
    """外皮 r110 圆柱在 x 处的 y"""
    return math.sqrt(SH_OUT ** 2 - x ** 2)


def stack(H=SW_H, X=None, gap=FLANGE_GAP):
    """叠层 (整机 y). H = 开关高 (杆顶离板面)"""
    yF = KB.Y_BOARD_FRONT
    x = KB.to_global(*KB.BTN[0])[0] if X is None else X           # 9.0
    stem = yF + H
    yb = stem - BORE_H
    r = dict(H=H, board_front=yF, body_top=yF + SW_BODY_H, stem_top=stem, cap_bottom=yb, flange_top=yb + FLANGE_T,
             cap_top=stem + CAP_H - BORE_H, cap_edge_top=stem + CAP_H - BORE_H - TOP_SAG,
             skin_in=yb + FLANGE_T + gap, skin_out=y_out(x))
    r['protrude'] = r['cap_top'] - r['skin_out']
    r['protrude_edge'] = (r['cap_edge_top'] - y_out(x - CAP_D / 2), r['cap_edge_top'] - y_out(x + CAP_D / 2))
    r['body_gap'] = yb - r['body_top']                            # 帽底 → 本体顶, 要 > 行程
    r['skin_t_center'] = r['skin_out'] - r['skin_in']
    r['skin_t_min'] = y_out(x + FLANGE_CLR_D / 2) - r['skin_in']  # 让位最外沿处外皮
    r['assy_dy'] = r['cap_top'] + CLR - r['skin_in']             # 退多少帽顶才在让位面下 (+CLR)
    return r


def skin_cuts(H=SW_H, dy=ASSY_DY, gap=FLANGE_GAP):
    """建议下罩按键处切除 (整机坐标, 每颗按键): 外皮帽孔 Φ5.9 + 裙边让位方腔 (宽 8.0, 顶 = 裙边顶+gap, 往下开到 Z−1, 往里到 帽底−dy−CLR)。
    方腔顶就是裙边止挡面; 方腔底开 ⇒ 下罩可竖直罩下 (此时帽在 −dy 位置, 全在方腔里), 外皮外面看不到槽。"""
    s = stack(H, gap=gap)
    assert dy >= s['assy_dy'] - 1e-9, f'ASSY_DY {dy} < 需要 {s["assy_dy"]:.2f}'
    hw = FLANGE_D / 2 + CLR
    out = []
    for X, Y in KB.BTN:
        x, z = KB.to_global(X, Y)
        out.append(ycyl(x, z, SKIN_HOLE_D, s['skin_in'] - 0.5, SH_OUT + 2))
        out.append(box(x - hw, s['cap_bottom'] - dy - CLR, -1.0, x + hw, s['skin_in'], z + hw))
        skin = y_out(x + hw) - s['skin_in']
        assert skin >= SKIN_MIN, skin
    return out


def write_stl(sh, path):
    BRepMesh_IncrementalMesh(sh, 0.005, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(sh, str(path))


def preview(path):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon
    from matplotlib import font_manager as fm
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    s = stack()
    yF, yB = KB.Y_BOARD_FRONT, KB.Y_BOARD_BACK
    x0 = KB.to_global(*KB.BTN[0])[0]
    zs = [KB.to_global(X, Y)[1] for X, Y in KB.BTN]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(15, 8.6), dpi=110, gridspec_kw=dict(width_ratios=[1.35, 1]))

    def cap_poly(zc, yb):          # 帽剖面 (YZ 平面, 横轴 y, 纵轴 Z)
        rb, rf, rbo = CAP_D / 2, FLANGE_D / 2, BORE_D / 2
        top = []
        for i in range(21):
            t = -rb + 2 * rb * i / 20
            top.append((yb + CAP_H - (TOP_R - math.sqrt(TOP_R ** 2 - t * t)), zc + t))
        pts = [(yb, zc - rf), (yb + FLANGE_T, zc - rf), (yb + FLANGE_T, zc - rb)] + top + \
              [(yb + FLANGE_T, zc + rb), (yb + FLANGE_T, zc + rf), (yb, zc + rf), (yb, zc + rbo), (yb + BORE_H, zc + rbo),
               (yb + BORE_H, zc - rbo), (yb, zc - rbo)]
        return pts

    # ---- 左: x=9 剖面 (YZ) ----
    so, si = s['skin_out'], s['skin_in']
    hw = FLANGE_D / 2 + CLR
    ax.add_patch(Rectangle((yB, KB.Z0), KB.T, KB.H, fc='#2E7D32', alpha=.6, ec='k'))
    # 外皮 (下罩): 外表面 so; 让位腔顶 si; 帽孔
    zt = zs[0] + hw
    ax.add_patch(Polygon([(si, -1), (so, -1), (so, 26), (si - 2.0, 26), (si - 2.0, zt), (si, zt)], closed=True, fc='#9FC5E8', ec='#3d85c6', alpha=.55))
    for zc in zs:
        ax.add_patch(Rectangle((si - 0.01, zc - SKIN_HOLE_D / 2), so - si + 0.02, SKIN_HOLE_D, fc='white', ec='none'))
    ax.add_patch(Rectangle((s['cap_bottom'] - ASSY_DY - CLR, -1), si - (s['cap_bottom'] - ASSY_DY - CLR), zt + 1, fc='none', ec='#3d85c6', ls='--', lw=1))
    for zc in zs:
        ax.add_patch(Rectangle((yF, zc - 3), SW_BODY_H, 6, fc='#bbb', ec='k'))
        ax.add_patch(Rectangle((yF + SW_BODY_H, zc - 1.75), s['H'] - SW_BODY_H, 3.5, fc='#555', ec='k'))
        ax.add_patch(Polygon(cap_poly(zc, s['cap_bottom']), closed=True, fc='#F6B26B', ec='k', lw=1.2))
        ax.add_patch(Polygon(cap_poly(zc, s['cap_bottom'] - ASSY_DY), closed=True, fc='none', ec='#e69138', ls=':', lw=1))
    zl = -3.0
    for i, (k, v) in enumerate([('板正面', yF), ('本体顶', s['body_top']), ('帽底', s['cap_bottom']), ('裙边顶', s['flange_top']),
                                ('让位面', si), ('杆顶', s['stem_top']), ('外皮外', so), ('帽顶', s['cap_top'])]):
        ax.plot([v, v], [zl - 0.3, 25], color='#999', lw=.5, ls=':')
        ax.text(v, zl - 0.6 - (i % 4) * 1.6, f'{k}\n{v:.2f}', ha='center', va='top', fontsize=7)
    ax.annotate('', (so, 22.5), (s['cap_top'], 22.5), arrowprops=dict(arrowstyle='<->', color='r'))
    ax.text((so + s['cap_top']) / 2, 23, f'外露 {s["protrude"]:.2f}', color='r', ha='center', fontsize=8)
    ax.annotate('', (s['flange_top'], 21.8), (si, 21.8), arrowprops=dict(arrowstyle='<->', color='b'))
    ax.text(si - 0.1, 20.3, f'间隙 {FLANGE_GAP:g}', color='b', ha='right', fontsize=7)
    ax.annotate('', (s['body_top'], zs[1] - 4.5), (s['cap_bottom'], zs[1] - 4.5), arrowprops=dict(arrowstyle='<->'))
    ax.text((s['body_top'] + s['cap_bottom']) / 2, zs[1] - 4.3, f'{s["body_gap"]:.2f} > 行程 {SW_TRAVEL}', ha='center', va='bottom', fontsize=7)
    ax.text(s['cap_bottom'] - ASSY_DY, 25.2, f'虚线帽 = 罩下罩时组件后退 {ASSY_DY:g}\n蓝虚框 = 让位方腔 (顶 y{si:.1f}, 底开到 Z−1)', fontsize=7, color='#e69138', ha='center')
    ax.set_xlim(97.5, 112.5); ax.set_ylim(-9, 28); ax.set_aspect('equal'); ax.set_xlabel('整机 y'); ax.set_ylabel('整机 Z')
    ax.set_title(f'x={x0:g} 剖面 (YZ): 板 → 6×6×{s["H"]:g} 开关 → 帽 → 外皮 r110', fontsize=10)
    # ---- 右: Z=17.5 剖面 (XY, 俯视), 看 r110 圆柱弧 ----
    zc = zs[0]
    xs = [x0 - 9 + 0.1 * i for i in range(181)]
    bx.fill_between(xs, [si] * len(xs), [y_out(x) for x in xs], color='#9FC5E8', alpha=.55)
    bx.plot(xs, [y_out(x) for x in xs], color='#3d85c6')
    bx.add_patch(Rectangle((x0 - SKIN_HOLE_D / 2, si - 0.01), SKIN_HOLE_D, 3.3, fc='white', ec='none'))
    bx.add_patch(Rectangle((x0 - 3, yF), 6, SW_BODY_H, fc='#bbb', ec='k'))
    bx.add_patch(Rectangle((x0 - 1.75, yF + SW_BODY_H), 3.5, s['H'] - SW_BODY_H, fc='#555', ec='k'))
    bx.add_patch(Polygon([(2 * x0 - b, a) for a, b in [(p[0], p[1] - zc + x0) for p in cap_poly(zc, s['cap_bottom'])]], closed=True, fc='#F6B26B', ec='k'))
    bx.add_patch(Rectangle((x0 - 10, yB), 20, KB.T, fc='#2E7D32', alpha=.6, ec='k'))
    e0, e1 = s['protrude_edge']
    bx.text(x0, s['cap_top'] + 0.3, f'帽顶外露: 中 {s["protrude"]:.2f} / 边 {e0:.2f}…{e1:.2f}', ha='center', fontsize=8, color='r')
    bx.text(x0 + 4.4, si - 0.6, f'外皮孔 Φ{SKIN_HOLE_D:g}, 裙边让位宽 {2 * hw:.1f}\n外皮最薄 {s["skin_t_min"]:.2f} (让位边)', fontsize=7.5)
    bx.set_xlim(x0 - 8, x0 + 8); bx.set_ylim(99, 112); bx.set_aspect('equal'); bx.set_xlabel('整机 x'); bx.set_ylabel('整机 y')
    bx.set_title(f'Z={zc:g} 剖面 (俯视, 上按键)', fontsize=10)
    fig.suptitle(f'按键帽叠层: 帽 Φ{CAP_D:g}×{CAP_H:g} 顶 R{TOP_R:g}, 裙边 Φ{FLANGE_D:g}×{FLANGE_T:g}, 内孔 Φ{BORE_D:g} 深 {BORE_H:g} 套 Φ3.5 杆', fontsize=12)
    plt.tight_layout(); plt.savefig(path); plt.close(fig)


def main():
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from helpers import write_doc
    OUT.mkdir(parents=True, exist_ok=True)
    cap = make_key_cap()
    print(f'帽体积 {vol(cap):.2f} mm3, 顶拱高 {TOP_SAG:.3f}')
    write_doc([('key_cap_v1_2', cap, '#F6B26B', None, False)], OUT / 'key_cap_v1_2.step', 'key_cap_v1_2')
    write_stl(cap, OUT / 'key_cap_v1_2.stl')
    print('开关高 | 杆顶 | 帽底 | 裙边顶 | 帽顶 | 外皮外 | 外露(中/边) | 帽底-本体 | 退让 dy')
    for H in (5, 6, 7, 8, 9, 9.5, 10):
        s = stack(H)
        print(f'{H:5g} | {s["stem_top"]:.2f} | {s["cap_bottom"]:.2f} | {s["flange_top"]:.2f} | {s["cap_top"]:.2f} | {s["skin_out"]:.3f} | '
              f'{s["protrude"]:+.2f} ({s["protrude_edge"][0]:+.2f}/{s["protrude_edge"][1]:+.2f}) | {s["body_gap"]:+.2f} | {s["assy_dy"]:.2f}')
    s = stack()
    print('推荐 H9: 让位面 y', round(s['skin_in'], 2), '外皮 中', round(s['skin_t_center'], 2), '最薄', round(s['skin_t_min'], 2))
    cuts = skin_cuts()
    print('skin_cuts 体积', [round(vol(c), 1) for c in cuts])
    # 两颗按键 / RGB 孔间距
    (x1, z1), (x2, z2) = [KB.to_global(*b) for b in KB.BTN]
    xr, zr = KB.to_global(*KB.RGB)
    print('帽孔间筋', round(abs(z1 - z2) - SKIN_HOLE_D, 2), '帽孔-RGB孔 外表面筋', round(math.hypot(x1 - xr, z1 - zr) - SKIN_HOLE_D / 2 - 5.3 / 2, 2),
          '让位方腔-RGB腔 (x)', round((x1 - FLANGE_D / 2 - CLR) - (xr + KB.RGB_D / 2 + CLR), 2))
    preview(OUT / 'key_cap_stack_preview.png')
    print('写出', OUT)


if __name__ == '__main__':
    main()
