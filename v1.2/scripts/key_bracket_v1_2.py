# -*- coding: utf-8 -*-
"""按键板 U 形支架 key_bracket_v1_2 —— 独立生成器 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python key_bracket_v1_2.py
输出 v1.2/models/key_bracket_v1_2/key_bracket_v1_2.stl/.step (打印姿态) + key_board_v1_2_model.step (板+元件简模, 装配位)

用户 11-13: 按键板 40×20×1.6 (scripts/key_board_outline_v1_2.py) 竖放在 +Y 侧下罩墙里, 正面朝外, 外面只看得到按键 / LED 孔。
  板: 正面 y100.6 / 背面 y99.0, 下沿 Z3 / 上沿 Z23, 板中心 x=0, 板系 X → 整机 x = 20 − X。
  11-13 更正 (取代铜螺母方案): 板不压铜螺母 —— 两根立柱在板**前面** (外侧) 压住两个安装孔, 立柱厚 3 (y100.6→103.6),
  M3×8 超薄头 (Φ7×1.5, 头 y103.6→105.1) 从立柱前面往里穿 立柱 + 板, 板背面上 M3 法兰螺母 (Φ7.6×3.7, y99→95.3)。
  立柱下端并进板下沿的底条 (Z0–3, 板下沿坐在底条上) ⇒ 一个 U 形件; 两立柱脚各一个竖 Φ4.2×4.2 铜螺母孔 (从底面压),
  M3 从底盘底 Φ7×2 沉孔往上拧进去。

形状 (整机坐标):
  底条  x ±21, y 98.0..103.6, Z0..3 (板背面 y99 后面多 1 托住板底)
  立柱  |x| 13..21, y 100.6..103.6, Z0..17.5, 横孔 Φ3.2 (沿 Y) @ (±16.5, Z13) = 板孔
  立柱脚 |x| 13..20, y 100.6..106.2, Z0..5.2 (铜螺母孔 Φ4.2×4.2 @ (±16.5, y103.3), 前壁 0.8 / 后壁到板面 0.6, 顶 1.0)
  立柱之间 (|x|<13) 只有底条 ⇒ 正面按键 / LED、背面元件 (y93..99, Z4.5..22) 都空出来。
打印姿态 = 装配姿态 (底面 Z0 贴床): 无悬空; 横孔 Φ3.2 小孔自桥; 铜螺母盲孔从底面开, 孔顶 Φ4.2 一小段桥接 (免支撑)。

不 import build_v1_2; build_v1_2 调 make_key_bracket(p) 拿 支架 / 板简模 / 下罩让位 (pocket) / 外皮孔 / 底盘孔 / 紧固件位置。
"""
import math
from pathlib import Path

from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
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
    BAR_X=21.0, BAR_Y0=98.0, BAR_Z1=3.0,
    PIL_X0=13.0, PIL_X1=21.0, PIL_T=3.0, PIL_Z1=17.5,
    FOOT_X1=20.0, FOOT_Y1=106.2, FOOT_Z1=5.2,
    INS_D=4.2, INS_H=4.2, INS_Y=103.3,  # 立柱脚铜螺母孔 (统一 Φ4.2×4.2, 装 M3×4)
    M3_D=3.2,
    HEAD_D=7.0, HEAD_H=1.5,            # M3 超薄头
    NUT_FL_D=7.6, NUT_T=3.7,           # M3 法兰螺母
    BOARD_SCREW_L=8.0, FOOT_SCREW_L=8.0,
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
def comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c


def make_key_bracket(p=None):
    P = dict(DEFAULTS, **(p or {}))
    c = P['CLR']
    yF, yB = KB.Y_BOARD_FRONT, KB.Y_BOARD_BACK                 # 100.6 / 99.0
    yP = yF + P['PIL_T']                                        # 立柱前面 103.6 = 螺丝头支承面
    MH = [KB.to_global(X, Y) for X, Y in KB.MH]                 # [(16.5, 13), (-16.5, 13)]
    # ---- 支架 ----
    br = box(-P['BAR_X'], P['BAR_Y0'], 0, P['BAR_X'], yP, P['BAR_Z1'])
    for s in (1, -1):
        br = fuse(br, box(s * P['PIL_X0'], yF, 0, s * P['PIL_X1'], yP, P['PIL_Z1']),
                  box(s * P['PIL_X0'], yF, 0, s * P['FOOT_X1'], P['FOOT_Y1'], P['FOOT_Z1']))
    for x, z in MH:
        br = cut(br, ycyl(x, z, P['M3_D'], yF - 1, P['FOOT_Y1'] + 1))
    INS = [(x, P['INS_Y']) for x, _ in MH]
    for x, y in INS:
        br = cut(br, cyl(x, y, P['INS_D'], -1, P['INS_H']))
    bracket = clean(br)
    assert BRepCheck_Analyzer(bracket).IsValid()
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
    hr, nr = P['HEAD_D'] / 2, P['NUT_FL_D'] / 2
    for x, z in MH:
        env += [(x - hr, x + hr, yP, yP + P['HEAD_H'], z + hr),        # 螺丝头
                (x - nr, x + nr, yB - P['NUT_T'], yB, z + nr)]         # 背面法兰螺母
    # 支架 / 板 / 背面元件区
    env += [(-P['BAR_X'], P['BAR_X'], P['BAR_Y0'], yP, P['BAR_Z1']),
            *[(min(s * P['PIL_X0'], s * P['PIL_X1']), max(s * P['PIL_X0'], s * P['PIL_X1']), yF, yP, P['PIL_Z1']) for s in (1, -1)],
            *[(min(s * P['PIL_X0'], s * P['FOOT_X1']), max(s * P['PIL_X0'], s * P['FOOT_X1']), yF, P['FOOT_Y1'], P['FOOT_Z1']) for s in (1, -1)],
            (-KB.W / 2, KB.W / 2, yB, yF, KB.Z0 + KB.H),
            (-KB.W / 2, KB.W / 2, KB.Y_BACK_MAX, yB, P['BACK_Z1'])]
    # ---- 下罩让位腔: 每个外包 +CLR, 底一律开到 Z−1 (下罩从上往下罩) ----
    boxes = [(x0 - c, x1 + c, y0 - c, y1 + c, -1.0, z1 + c) for x0, x1, y0, y1, z1 in env]
    pocket = clean(fuse(*[box(a, d, f, b_, e, g) for a, b_, d, e, f, g in boxes]))   # box(x0, y0, z0, x1, y1, z1)
    r_max = max(math.hypot(max(abs(a), abs(b_)), max(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes)
    r_min = min(math.hypot(0 if a < 0 < b_ else min(abs(a), abs(b_)), min(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes)
    skin = P['SH_OUT'] - r_max
    assert skin >= P['SKIN_MIN'] - 1e-9, f'让位腔外皮 {skin:.2f} < {P["SKIN_MIN"]}'
    assert r_min >= P['SPIG_IN'] + 0.5, f'让位腔碰墙内面 r{r_min:.2f}'
    skin_holes = [ycyl(x, z, d, yF, P['SH_OUT'] + 2) for x, z, d in holes]
    bb = [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes), max(b[5] for b in boxes)]
    # 支架上点到 r 的最小值 (要在墙内面 r90.8 外)
    br_rmin = math.hypot(0, P['BAR_Y0'])
    res = dict(
        bracket=bracket, board=board, pocket=pocket, skin_holes=skin_holes,
        disc_m3=INS,                                            # 底盘 M3 孔 (Φ3.2 + 底面 Φ7×2) = 铜螺母孔心
        insert_z=(0.0, 4.0),                                    # M3×4 铜螺母齐支架底面
        foot_screw_L=P['FOOT_SCREW_L'], foot_screw_bear=-P['DISC_T'] + P['M3_CB_H'],
        board_screws=[dict(x=x, z=z, bear_y=yP, L=P['BOARD_SCREW_L'], nut_y=yB) for x, z in MH],
        holes=holes, skin=round(skin, 3), pocket_bbox=[round(v, 2) for v in bb], pocket_rmin=round(r_min, 2),
        bracket_ymin=P['BAR_Y0'], bracket_rmin=round(br_rmin, 2), bracket_vol=round(vol(bracket), 1), params=P)
    return res


def write_stl(sh, path):
    BRepMesh_IncrementalMesh(sh, 0.01, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(sh, str(path))


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
    print('支架 bbox', [round(v, 2) for v in b], '体积', r['bracket_vol'], 'mm3')
    print('铜螺母孔 / 底盘 M3', r['disc_m3'], '板螺丝', [(s['x'], s['z']) for s in r['board_screws']])
    print('让位腔 bbox', r['pocket_bbox'], '外皮最薄', r['skin'], '腔最内 r', r['pocket_rmin'])


if __name__ == '__main__':
    main()
