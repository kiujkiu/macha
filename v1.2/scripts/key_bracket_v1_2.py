# -*- coding: utf-8 -*-
"""按键板 L 形支架 key_bracket_v1_2 —— 独立生成器 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python key_bracket_v1_2.py
输出 v1.2/models/key_bracket_v1_2/key_bracket_v1_2.stl/.step (打印姿态) + key_board_bracket_装配位.step + key_bracket_v1_2_preview.png

用户 11-13: 按键板 40×20×1.6 (scripts/key_board_outline_v1_2.py) 竖放在 +Y 侧下罩墙里, 正面朝外, 外面只看得到按键 / LED 孔。
  板: 正面 y100.6 / 背面 y99.0, 下沿 Z3 / 上沿 Z23, 板中心 x=0, 板系 X → 整机 x = 20 − X。
11-13 (二) 用户「支撑件做 L 型, 两边加三角加强; 底板依然螺丝从下往上, 螺母在上边; 固定电路板螺丝要沉孔, pcb 这边用螺母」:
  一件式 (两侧 L + 板下横条连成一体, 横条给板定位/托底):
  竖边 = 立柱 (压板正面): |x| 13..22.6, y 100.6..104.1 (厚 3.5), Z0..18; 横孔 Φ3.2 @ (±16.5, Z13) = 板孔;
         外侧 Φ7.4×1.7 沉孔埋超薄头 (Φ7×1.5, 头顶低于立柱前面 0.2), 沉孔底剩壁 1.8;
         (立柱内沿 |x|13 被板上按键 / LED 卡死, 不能再往里: Φ7.4 沉孔在内侧破边 0.2 —— 头 Φ7 本身刚好到 |x|13, 不出立柱)
  横边 = 脚 (贴底盘顶往里 −Y): |x| 20.6..32, y 90..100, Z0..4 (在板宽外, 不碰板 / 背面元件区 |x|<20 y93..99);
         M3 Φ3.2 竖孔 @ (±27, y95), M3×12 从底盘底 Φ7×2 沉孔往上, 法兰螺母 (Φ7.6×3.7) 坐脚顶 Z4..7.7, 尖 Z8 ⇒ 吃满 3.7 (露 0.3);
         螺母法兰外离脚边 ≥1.2。
  三角筋 = |x| 20.6..22.6 (厚 2) 竖板, 侧视梯形: (y100.6, Z18) 立柱顶 → (y90, Z4) 脚内端, 底 Z0;
         离板边 0.6, 离板背面法兰螺母 (|x|≤20.3) 0.3, 离脚螺母法兰 (|x|≥23.2) 0.6。
  横条 = |x| ≤22.6, y 98..104.1, Z0..3 (板下沿坐上面, 背面多 1 托板底)。
板螺丝: M3×8 超薄头从外 (+Y) 往里, 支承 = 沉孔底 y102.4, 穿立柱剩壁 1.8 + 板 1.6, 板背面 M3 法兰螺母 y99..95.3, 尖 y94.4 ⇒ 吃满 3.7。
打印姿态 (用户 11-13): **前面 y104.1 朝下贴床** (立柱前面 + 横条前面 + 脚前端补齐成一整片平面, |x|>29 端部 45° 倒角免外皮过薄且无悬空); 沉孔 Φ7.4 在床面上; 脚 Φ3.2 孔变横孔 (小圆孔自桥)。
下罩让位腔 = 每件外包 (box) +0.3, 全部从 Z−1 开到件顶 ⇒ 竖直柱体并集, 下罩竖直罩下无倒扣。

不 import build_v1_2; build_v1_2 调 make_key_bracket(p) 拿 支架 / 板简模 / 下罩让位 (pocket) / 外皮孔 / 底盘孔 / 紧固件位置。
"""
import math
from pathlib import Path

from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer

import key_board_outline_v1_2 as KB

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_bracket_v1_2'

DEFAULTS = dict(
    SH_OUT=110.0, SPIG_IN=90.8,        # 下罩外圆 / 墙内面
    SKIN_MIN=1.5,                      # 让位腔到 r110 外皮最薄
    CLR=0.3,                           # 让位腔单边间隙
    BAR_Y0=98.0, BAR_Z1=3.0,           # 板下横条 (板下沿坐 Z3)
    PIL_X0=13.0, PIL_X1=22.6, PIL_T=3.5, PIL_Z1=18.0,     # 竖边 (立柱)
    CB_D=7.4, CB_H=1.7,                # 立柱外侧沉孔 (超薄头 Φ7×1.5 埋 0.2)
    FOOT_X0=20.6, FOOT_X1=32.0, FOOT_Y0=90.0, FOOT_Y1=100.0, FOOT_T=4.0,   # 横边 (脚)
    RIB_X0=20.6, RIB_X1=22.6,          # 三角筋 (厚 2)
    FILL_X=29.0, FILL_CH=3.0,          # 用户 11-13: 脚前端补齐到立柱前面 (y104.1) 成整片平面, 可前面贴床打印; |x|>29 处 45° 倒角 (外皮 ≥1.5)
    FOOT_HX=27.0, FOOT_HY=95.0,        # 脚 M3 孔
    M3_D=3.2,
    HEAD_D=7.0, HEAD_H=1.5,            # M3 超薄头
    NUT_FL_D=7.6, NUT_T=3.7,           # M3 法兰螺母
    BOARD_SCREW_L=8.0, FOOT_SCREW_L=12.0,
    DISC_T=6.0, M3_CB_H=2.0,           # 底盘 / Φ7×2 沉孔 (M3 从盘底往上, 头支承 Z−4)
    BACK_Z0=4.5, BACK_Z1=22.0,         # 背面元件区 (用户)
    HOLE_BTN=4.0, HOLE_RGB=5.3, HOLE_LED=3.3,   # 前皮孔
)


# ---------------- 最小 OCP 工具 ----------------
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def op(cls, a, b):
    o = cls(a, b); o.Build(); assert o.IsDone(); return o.Shape()
def cut(a, *bs):
    for b in bs: a = op(BRepAlgoAPI_Cut, a, b)
    return a
def fuse(a, *bs):
    for b in bs: a = op(BRepAlgoAPI_Fuse, a, b)
    return a
def clean(s):
    u = ShapeUpgrade_UnifySameDomain(s, True, True, True); u.Build(); return u.Shape()
def xf(s, t): return BRepBuilderAPI_Transform(s, t, True).Shape()
def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)), gp_Pnt(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()
def cyl(x, y, d, z0, z1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), d / 2, z1 - z0).Shape()
def ycyl(x, z, d, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), d / 2, y1 - y0).Shape()
def yz_prism(pts, x0, x1):
    """YZ 平面多边形 pts=[(y, z)...] 沿 X 从 x0 拉到 x1"""
    x0, x1 = min(x0, x1), max(x0, x1)
    pg = BRepBuilderAPI_MakePolygon()
    for y, z in pts: pg.Add(gp_Pnt(x0, y, z))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(x1 - x0, 0, 0)).Shape()
def xy_prism(pts, z0, z1):
    """XY 平面多边形 pts=[(x, y)...] 沿 Z 从 z0 拉到 z1"""
    pg = BRepBuilderAPI_MakePolygon()
    for x, y in pts: pg.Add(gp_Pnt(x, y, z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()
def fill_poly(P, yP, s, o=0.0):
    """脚前端补块 (俯视): 立柱外侧 → FILL_X 齐 y=yP, 再 45° 倒到脚端; o = 外扩间隙"""
    fx, x1, y1 = P['FILL_X'], P['FOOT_X1'], P['FOOT_Y1']
    k = o * math.tan(math.radians(22.5))
    pts = [(P['PIL_X1'] - 0.01, y1 - o), (P['PIL_X1'] - 0.01, yP + o), (fx + k, yP + o), (x1 + o, yP - (x1 - fx) + k), (x1 + o, y1 - o)]
    return [(s * x, y) for x, y in pts]
def comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c


def make_key_bracket(p=None):
    P = dict(DEFAULTS, **(p or {}))
    c = P['CLR']
    yF, yB = KB.Y_BOARD_FRONT, KB.Y_BOARD_BACK                 # 100.6 / 99.0
    yP = yF + P['PIL_T']                                        # 立柱前面 104.1
    yBear = yP - P['CB_H']                                      # 沉孔底 = 板螺丝头支承面 102.4
    MH = [KB.to_global(X, Y) for X, Y in KB.MH]                 # [(16.5, 13), (-16.5, 13)]
    FT, nT = P['FOOT_T'], P['NUT_T']
    FH = [(s * P['FOOT_HX'], P['FOOT_HY']) for s in (1, -1)]    # 脚 M3 / 底盘孔
    rib = [(P['FOOT_Y0'], 0), (yF, 0), (yF, P['PIL_Z1']), (P['FOOT_Y0'], FT)]   # 筋侧视: 立柱顶背面 → 脚内端
    # ---- 支架 ----
    br = box(-P['PIL_X1'], P['BAR_Y0'], 0, P['PIL_X1'], yP, P['BAR_Z1'])          # 板下横条
    for s in (1, -1):
        br = fuse(br, box(s * P['PIL_X0'], yF, 0, s * P['PIL_X1'], yP, P['PIL_Z1']),                      # 竖边
                  box(s * P['FOOT_X0'], P['FOOT_Y0'], 0, s * P['FOOT_X1'], P['FOOT_Y1'], FT),              # 横边
                  yz_prism(rib, s * P['RIB_X0'], s * P['RIB_X1']),                                          # 三角筋
                  xy_prism(fill_poly(P, yP, s)[::s], 0, P['FOOT_T']))                                          # 脚前端补齐 (前面整片平面)
    for x, z in MH:
        br = cut(br, ycyl(x, z, P['M3_D'], yF - 1, yP + 1), ycyl(x, z, P['CB_D'], yBear, yP + 1))
    for x, y in FH:
        br = cut(br, cyl(x, y, P['M3_D'], -1, FT + 1))
    bracket = clean(br)
    assert BRepCheck_Analyzer(bracket).IsValid()
    # 自检: 沉孔底剩壁, 筋 / 脚 / 螺母避让
    assert P['PIL_T'] - P['CB_H'] >= 1.5 - 1e-9 and P['CB_H'] >= P['HEAD_H']
    assert P['RIB_X0'] >= max(KB.W / 2 + 0.5, abs(MH[0][0]) + P['NUT_FL_D'] / 2 + 0.3) - 1e-9     # 筋离板边 / 板背面螺母
    assert P['FOOT_X0'] >= KB.W / 2 + 0.5 - 1e-9
    nr = P['NUT_FL_D'] / 2
    assert P['FOOT_HX'] - nr >= P['RIB_X1'] + 0.5 and P['FOOT_X1'] - (P['FOOT_HX'] + nr) >= 1.0 - 1e-9
    assert P['FOOT_HY'] - nr - P['FOOT_Y0'] >= 1.0 - 1e-9 and P['FOOT_Y1'] - (P['FOOT_HY'] + nr) >= 1.0 - 1e-9
    # ---- 板 + 元件简模 ----
    bd = box(-KB.W / 2, yB, KB.Z0, KB.W / 2, yF, KB.Z0 + KB.H)
    for x, z in MH: bd = cut(bd, ycyl(x, z, KB.MH_D, yB - 1, yF + 1))
    parts = [bd]; holes = []; env = []                          # env: (x0, x1, y0, y1, z1) 元件外包 (未加间隙)
    for X, Y in KB.BTN:
        x, z = KB.to_global(X, Y); h = KB.BTN_BODY / 2
        parts += [box(x - h, yF, z - h, x + h, yF + KB.BTN_BODY_H, z + h), ycyl(x, z, KB.BTN_STEM_D, yF + KB.BTN_BODY_H, yF + KB.BTN_H)]
        env += [(x - h, x + h, yF, yF + KB.BTN_BODY_H, z + h), (x - KB.BTN_STEM_D / 2, x + KB.BTN_STEM_D / 2, yF, yF + KB.BTN_H, z + KB.BTN_STEM_D / 2)]
        holes.append((x, z, P['HOLE_BTN']))
    for (X, Y), d, hgt, hd in [(KB.RGB, KB.RGB_D, KB.RGB_H, P['HOLE_RGB'])] + [(q, KB.LED_D, KB.LED_H, P['HOLE_LED']) for q in KB.LED]:
        x, z = KB.to_global(X, Y)
        parts.append(ycyl(x, z, d, yF, yF + hgt)); env.append((x - d / 2, x + d / 2, yF, yF + hgt, z + d / 2)); holes.append((x, z, hd))
    board = comp(parts)
    # ---- 紧固件位置 ----
    hr = P['HEAD_D'] / 2
    foot_tip = -P['DISC_T'] + P['M3_CB_H'] + P['FOOT_SCREW_L']                    # Z8
    for x, z in MH:
        env += [(x - nr, x + nr, yB - nT, yB, z + nr),                             # 背面法兰螺母 (头已埋进立柱沉孔)
                (x - 1.5, x + 1.5, yBear - P['BOARD_SCREW_L'], yB, z + 1.5)]       # 杆尖
    for x, y in FH:
        env += [(x - nr, x + nr, y - nr, y + nr, FT + nT), (x - 1.5, x + 1.5, y - 1.5, y + 1.5, foot_tip)]   # 脚顶法兰螺母 / 杆尖
    # 支架 / 板 / 背面元件区
    for s in (1, -1):
        lo = lambda a, b: (min(s * a, s * b), max(s * a, s * b))
        env += [(*lo(P['PIL_X0'], P['PIL_X1']), yF, yP, P['PIL_Z1']),
                (*lo(P['FOOT_X0'], P['FOOT_X1']), P['FOOT_Y0'], P['FOOT_Y1'], FT),
                (*lo(P['RIB_X0'], P['RIB_X1']), P['FOOT_Y0'], yF, P['PIL_Z1'])]     # 筋按外包盒让 (腔仍是竖柱体)
    env += [(-P['PIL_X1'], P['PIL_X1'], P['BAR_Y0'], yP, P['BAR_Z1']),
            (-KB.W / 2, KB.W / 2, yB, yF, KB.Z0 + KB.H),
            (-KB.W / 2, KB.W / 2, KB.Y_BACK_MAX, yB, P['BACK_Z1'])]
    # ---- 下罩让位腔: 每个外包 +CLR, 底一律开到 Z−1 (下罩从上往下罩, 竖直柱体并集 ⇒ 无倒扣) ----
    boxes = [(x0 - c, x1 + c, y0 - c, y1 + c, -1.0, z1 + c) for x0, x1, y0, y1, z1 in env]
    fills = [fill_poly(P, yP, s, c) for s in (1, -1)]
    pocket = clean(fuse(*[box(a, d, f, b_, e, g) for a, b_, d, e, f, g in boxes], *[xy_prism(q[::s], -1.0, P['FOOT_T'] + c) for q, s in zip(fills, (1, -1))]))
    r_max = max([math.hypot(max(abs(a), abs(b_)), max(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes] + [math.hypot(x, y) for q in fills for x, y in q])
    r_min = min(math.hypot(0 if a < 0 < b_ else min(abs(a), abs(b_)), min(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes)
    skin = P['SH_OUT'] - r_max
    assert skin >= P['SKIN_MIN'] - 1e-9, f'让位腔外皮 {skin:.2f} < {P["SKIN_MIN"]}'
    assert r_min >= P['SPIG_IN'] + 0.5, f'让位腔碰墙内面 r{r_min:.2f}'
    skin_holes = [ycyl(x, z, d, yF, P['SH_OUT'] + 2) for x, z, d in holes]
    bb = [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes), max(b[5] for b in boxes)]
    res = dict(
        bracket=bracket, board=board, pocket=pocket, skin_holes=skin_holes,
        disc_m3=FH,                                             # 底盘 M3 孔 (Φ3.2 + 底面 Φ7×2) = 脚孔心
        foot_nut_z=(FT, FT + nT),                               # 脚顶法兰螺母 Z4..7.7
        foot_screw_L=P['FOOT_SCREW_L'], foot_screw_bear=-P['DISC_T'] + P['M3_CB_H'], foot_screw_tip=foot_tip,
        board_screws=[dict(x=x, z=z, bear_y=yBear, L=P['BOARD_SCREW_L'], nut_y=yB) for x, z in MH],
        holes=holes, skin=round(skin, 3), pocket_bbox=[round(v, 2) for v in bb], pocket_rmin=round(r_min, 2),
        rib=rib, bracket_ymin=P['FOOT_Y0'], bracket_rmin=round(math.hypot(P['FOOT_X0'], P['FOOT_Y0']), 2),
        bracket_vol=round(vol(bracket), 1), params=P)
    return res


def write_stl(sh, path):
    BRepMesh_IncrementalMesh(sh, 0.01, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(sh, str(path))


def preview(r, path):
    """侧视 (沿 −X 看, YZ) + 俯视 (XY) 两张, 画支架 / 板 / 紧固件 / 让位腔外包。"""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon, Circle
    from matplotlib import font_manager as fm
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    P = r['params']; yF, yB = KB.Y_BOARD_FRONT, KB.Y_BOARD_BACK; yP = yF + P['PIL_T']; FT = P['FOOT_T']
    bs = r['board_screws'][0]; yBear = bs['bear_y']
    Y = '#F1C232'; G = '#2E7D32'; S = '#9E9E9E'; N = '#555555'
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7.2), dpi=110)
    # ---- 侧视 (横轴 y, 纵轴 Z) ----
    a1.add_patch(Polygon(r['rib'], fc=Y, ec='k', alpha=.55, label='三角筋 (|x| 20.6–22.6)'))
    a1.add_patch(Rectangle((P['FOOT_Y0'], 0), P['FOOT_Y1'] - P['FOOT_Y0'], FT, fc=Y, ec='k', alpha=.8, label='横边 脚 (|x| 20.6–32)'))
    a1.add_patch(Rectangle((yF, 0), P['PIL_T'], P['PIL_Z1'], fc=Y, ec='k', alpha=.95, label='竖边 立柱 (|x| 13–22.6)'))
    a1.add_patch(Rectangle((P['FOOT_Y1'], 0), yP - P['FOOT_Y1'], FT, fc=Y, ec='k', alpha=.95, hatch='xx', label=f"脚前端补齐 (|x| 22.6–{P['FILL_X']:g}, 端部 45° 倒角)"))
    a1.add_patch(Rectangle((P['BAR_Y0'], 0), yP - P['BAR_Y0'], P['BAR_Z1'], fc=Y, ec='k', hatch='//', alpha=.6, label='板下横条'))
    a1.add_patch(Rectangle((yB, KB.Z0), KB.T, KB.H, fc=G, ec='k', alpha=.8, label='按键板'))
    a1.add_patch(Rectangle((KB.Y_BACK_MAX, P['BACK_Z0']), yB - KB.Y_BACK_MAX, P['BACK_Z1'] - P['BACK_Z0'], fc='none', ec=G, ls='--', label='背面元件区'))
    z = bs['z']
    a1.add_patch(Rectangle((yBear, z - 3.5), 1.5, 7, fc=S, ec='k', label=f"M3×{bs['L']:g} 超薄头 (沉孔 Φ{P['CB_D']}×{P['CB_H']})"))
    a1.add_patch(Rectangle((yBear - bs['L'], z - 1.5), bs['L'], 3, fc=S, ec='k'))
    a1.add_patch(Rectangle((yB - P['NUT_T'], z - 3.8), P['NUT_T'], 7.6, fc=N, ec='k', label='M3 法兰螺母'))
    a1.plot([yP - P['CB_H']] * 2, [z - P['CB_D'] / 2, z + P['CB_D'] / 2], 'r-', lw=1)
    fy = P['FOOT_HY']; t0 = r['foot_screw_bear']
    a1.add_patch(Rectangle((fy - 1.5, t0), 3, r['foot_screw_L'], fc=S, ec='k', label=f"M3×{r['foot_screw_L']:g} 底盘往上"))
    a1.add_patch(Rectangle((fy - 3.5, t0 - 1.5), 7, 1.5, fc=S, ec='k'))
    a1.add_patch(Rectangle((fy - 3.8, FT), 7.6, P['NUT_T'], fc=N, ec='k'))
    a1.add_patch(Rectangle((80, -P['DISC_T']), 32, P['DISC_T'], fc='#ccc', ec='k', alpha=.5, label='底盘'))
    a1.axvline(P['SH_OUT'], color='b', lw=1); a1.axvline(P['SPIG_IN'], color='b', lw=1, ls=':')
    a1.text(P['SH_OUT'] + .2, 20, '下罩外皮 r110 (x=0)', color='b', rotation=90, va='top'); a1.text(P['SPIG_IN'] - .9, 20, '墙内面 r90.8 (x=0)', color='b', rotation=90, va='top')
    pb = r['pocket_bbox']
    a1.set_xlim(85, 113); a1.set_ylim(-8, 36); a1.set_aspect('equal'); a1.grid(alpha=.3)
    a1.set_xlabel('y (外 →)'); a1.set_ylabel('Z'); a1.set_title('侧视 (x=+16.5 / +27 截面叠画)  L 形: 竖边压板正面, 脚往里伸')
    a1.legend(fontsize=7.5, loc='upper left', ncol=2)
    # ---- 俯视 (横轴 x, 纵轴 y) ----
    for s in (1, -1):
        def rx(a, b, y0, y1, **kw): a2.add_patch(Rectangle((min(s * a, s * b), y0), abs(b - a), y1 - y0, **kw))
        rx(P['FOOT_X0'], P['FOOT_X1'], P['FOOT_Y0'], P['FOOT_Y1'], fc=Y, ec='k', alpha=.7)
        rx(P['RIB_X0'], P['RIB_X1'], P['FOOT_Y0'], yF, fc='#E0A800', ec='k')
        rx(P['PIL_X0'], P['PIL_X1'], yF, yP, fc=Y, ec='k')
        a2.add_patch(Polygon(fill_poly(P, yP, s), closed=True, fc=Y, ec='k', alpha=.9))                   # 脚前端补齐
        hx, hy = s * P['FOOT_HX'], P['FOOT_HY']
        a2.add_patch(Circle((hx, hy), P['NUT_FL_D'] / 2, fc=N, ec='k', alpha=.7)); a2.add_patch(Circle((hx, hy), 1.6, fc='w', ec='k'))
        a2.text(hx, hy - 5.5, f'M3 ({hx:+g}, {hy:g})', ha='center', fontsize=8)
        x = s * 16.5
        a2.add_patch(Rectangle((x - 3.5, yBear), 7, 1.5, fc=S, ec='k')); a2.add_patch(Rectangle((x - 3.8, yB - P['NUT_T']), 7.6, P['NUT_T'], fc=N, ec='k'))
    a2.add_patch(Rectangle((-P['PIL_X1'], P['BAR_Y0']), 2 * P['PIL_X1'], yP - P['BAR_Y0'], fc=Y, ec='k', hatch='//', alpha=.4))
    a2.add_patch(Rectangle((-KB.W / 2, yB), KB.W, KB.T, fc=G, ec='k'))
    a2.add_patch(Rectangle((-KB.W / 2, KB.Y_BACK_MAX), KB.W, yB - KB.Y_BACK_MAX, fc='none', ec=G, ls='--'))
    a2.add_patch(Rectangle((pb[0], pb[2]), pb[1] - pb[0], pb[3] - pb[2], fc='none', ec='r', ls=':', label='让位腔外包'))
    for R, ls in ((P['SH_OUT'], '-'), (P['SH_OUT'] - P['SKIN_MIN'], '--'), (P['SPIG_IN'], ':')):
        xs = [R * math.cos(math.radians(a)) for a in range(60, 121)]; ys = [R * math.sin(math.radians(a)) for a in range(60, 121)]
        a2.plot(xs, ys, 'b', ls=ls, lw=1)
    a2.set_xlim(-40, 40); a2.set_ylim(84, 112); a2.set_aspect('equal'); a2.grid(alpha=.3)
    a2.set_xlabel('x'); a2.set_ylabel('y'); a2.legend(fontsize=8, loc='lower center')
    a2.set_title(f"俯视  外皮最薄 {r['skin']:.2f} (蓝虚线 = 外皮 1.5 界)  腔最内 r{r['pocket_rmin']}")
    fig.suptitle('按键板 L 形支架 key_bracket_v1_2 (11-13)  一件式, 前面 (y104.1) 朝下贴床打印', fontsize=13)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    from helpers import write_doc, bbox
    r = make_key_bracket()
    OUT.mkdir(parents=True, exist_ok=True)
    b = bbox(r['bracket'])
    t = gp_Trsf(); t.SetTranslation(gp_Vec(0, -b[1], -b[2]))     # 打印姿态 = 装配姿态, y 平移到 0
    pr = xf(r['bracket'], t)
    write_stl(pr, OUT / 'key_bracket_v1_2.stl')
    write_doc([('key_bracket_v1_2', pr, '#F1C232', None, False)], OUT / 'key_bracket_v1_2.step', 'key_bracket_v1_2')
    write_doc([('key_board_v1_2', r['board'], '#2E7D32', None, False), ('key_bracket_v1_2', r['bracket'], '#F1C232', None, False)],
              OUT / 'key_board_bracket_装配位.step', 'key_board_bracket')
    preview(r, OUT / 'key_bracket_v1_2_preview.png')
    print('支架 bbox', [round(v, 2) for v in b], '体积', r['bracket_vol'], 'mm3')
    print('底盘 M3 / 脚孔', r['disc_m3'], '脚螺母 Z', r['foot_nut_z'], '脚螺丝尖 Z', r['foot_screw_tip'],
          '板螺丝', [(s['x'], s['z'], s['bear_y']) for s in r['board_screws']])
    print('让位腔 bbox', r['pocket_bbox'], '外皮最薄', r['skin'], '腔最内 r', r['pocket_rmin'])


if __name__ == '__main__':
    main()
