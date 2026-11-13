# -*- coding: utf-8 -*-
"""按键板支架 key_bracket_v1_2 —— 独立生成器 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python key_bracket_v1_2.py
输出 v1.2/models/key_bracket_v1_2/key_bracket_v1_2.stl/.step (打印姿态) + key_board_bracket_装配位.step
     + key_bracket_v1_2_preview.png (剖面) + key_flap_front.png (外皮舌片正视)

用户 11-13: 按键板 40×20×1.6 (scripts/key_board_outline_v1_2.py) 竖放在 +Y 侧下罩墙里, 正面朝外。
  板: 正面 y100.6 / 背面 y99.0, 下沿 Z3 / 上沿 Z23, 板中心 x=0, 板系 X → 整机 x = 20 − X。
11-13 (二) L 形: 脚 (横边) 2×M3×12 从盘底往上 + 法兰螺母坐脚顶; 三角筋; 板下横条托底 —— 不变。
11-13 (三) 用户「支架前面做成一整块平板」(原立柱之间是空的露出元件):
  前面平板 = |x| ≤22.6, y100.6..105.7 (厚 5.1), Z0..26.5, 压住整板正面; 前面平 (y105.7 = |x|22.6 角处外皮 1.55 + 腔间隙 0.3 定的上限),
    平板前面离外皮内面 (让位腔前面) 只 0.3 ⇒ 灯光不横向串。
  平板孔: 每颗 LED 一个 Φ3.2 隔光通道 (导光柱从外皮外面插进来, 外皮孔 Φ3.0 压管, 平板孔只隔光不夹管);
          按键杆 Φ3.5 从 Φ4.0 孔穿出; 背面开关本体 (6×6 高 3.45) 让位腔 +0.3 深 3.75, 脚 / 焊盘 (9.5×5.6) 让位 +0.3 深 1.5; 其余平板背面全贴板 (压板)。
  板螺丝 M3×8 超薄头: 平板前面 Φ7.4×2.4 沉孔 (支承 y103.3, 头顶 y104.8 低于平板前面 0.9), 穿平板剩壁 2.7 + 板 1.6,
          背面法兰螺母 y99..95.3, 尖 y95.3 ⇒ 吃满 3.7 (尖齐螺母端面)。
  脚前端: 平板前面 |x|22.6 角起 45° 一路倒到脚端 (x=32, y96.3) —— 前面朝下打印时侧面全 ≥45° 自撑; 脚螺母法兰离倒角面 ≥0.6。
  打印: **前面 (y105.7) 朝下贴床**, 免支撑 (背面让位腔朝上开口; 沉孔 Φ7.4 在床面上; 脚孔变横孔)。
按键 = 下罩外皮舌片 (用户 11-13「沿红色切一下这个边, 这部分按压形变, 推到微动开关」): 外皮切 H 形缝 (两侧竖缝 + 中间横缝),
  上键舌片根在上 (Z30), 下键舌片根在下 (Z2); 舌片内面挖薄 (竖槽底开到 Z−1, 罩下时杆从槽里滑过), 内面凸点 Φ3 正对杆, 离杆顶 0.3。
  缝宽 1.0; 下罩正立打印 (Z0 贴床)。FLAP_MODE: 'support' (主件, 用户 11-13 (四)) = 横缝开到两凸点边各留 0.4 (Z12.4–19.6), 切片在上舌片下加支撑, 钳子拔出;
  'tie' (只做 A 试打块) = 横缝 1.0 + 上舌片底边两侧竖缝各留 0.6 高断开桥 (不切穿), 打完用刀划开。
  11-13 (四) 按键间距 7 → 11 (整机 Z21.5 / Z10.5, 两舌片悬臂各 8.5): 卡在舌片弹性力 ≤~4 N (F ∝ 1/a³, a ≥8.35 ⇒ 间距 ≤11.3); 板高 20 → 22.5 让上键本体 / 焊盘留四边禁布 1。
11-13 (五) 用户: 按键转 90° (焊盘外包 5.6×9.5 竖), 按键 / 螺丝 / LED 对板水平中线对称 ⇒ 板 40×26 (中线 Y13 = 整机 Z16), 螺丝 (±16.5, Z16), LED 行 Z16 (x 3 / −1.5 / −6 / −10.5);
  按键仍 Z21.5 / Z10.5 ⇒ 舌片 / 力不变。单面贴: R1–R6 / C1 在板正面 (Y19.5 一行), 平板背面开一个共用让位腔 (外包 +0.3, 深 1.3), 与 LED 隔光通道之间留实心壁。
  平板顶 = 板顶 Z29 (原 板顶 +1): 下罩让位腔顶 + 屋顶削到 ≤ Z29.65 (= 原值; 分体版外卡环凸筋槽底 Z29.9, 玻璃承台 Z32 不动)。
下罩让位腔 = 每件外包 (box) +0.3, 全部从 Z−1 开到件顶, 顶上再加 45° 双坡屋顶 (下罩正立打印免平顶桥) ⇒ 竖直柱体并集, 下罩竖直罩下无倒扣; 按键杆伸出平板的部分在舌片竖槽里 (不算外皮最薄)。

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
    SKIN_MIN=1.5,                      # 让位腔到 r110 外皮最薄 (舌片处有意挖薄, 不算)
    CLR=0.3,                           # 让位腔单边间隙
    BAR_Y0=98.0, BAR_Z1=3.0,           # 板下横条 (板下沿坐 Z3)
    PL_X1=22.6, PL_Y1=105.7, PL_Z1=29.0,   # 前面平板 |x|≤22.6, 前面 y105.7, Z0..29 (11-13 (五) 板高 26 ⇒ 板顶 Z29; 平板顶齐板顶, 原 +1 放不下: 见 ROOF_ZMAX)
    ROOF_ZMAX=29.65,                   # 下罩让位腔 (含 45° 屋顶) 最高 Z: 分体版外卡环凸筋槽底 Z29.9 (r103.9–106.1) 下留 ≥0.25 (= 11-13 (四) 原值); 屋顶超出就削平
    RIB_Z1=18.0,                       # 三角筋顶 (贴平板背面)
    CB_D=7.4, CB_H=2.4,                # 平板前面沉孔 (超薄头 Φ7×1.5 埋 0.9; M3×8 尖齐螺母端面)
    FOOT_X0=20.6, FOOT_X1=32.0, FOOT_Y0=90.0, FOOT_Y1=100.0, FOOT_T=4.0,   # 横边 (脚)
    RIB_X0=20.6, RIB_X1=22.6,          # 三角筋 (厚 2)
    FOOT_HX=27.0, FOOT_HY=95.0,        # 脚 M3 孔
    M3_D=3.2,
    HEAD_D=7.0, HEAD_H=1.5,            # M3 超薄头
    NUT_FL_D=7.6, NUT_T=3.7,           # M3 法兰螺母
    BOARD_SCREW_L=8.0, FOOT_SCREW_L=12.0,
    DISC_T=6.0, M3_CB_H=2.0,           # 底盘 / Φ7×2 沉孔 (M3 从盘底往上, 头支承 Z−4)
    BACK_Z0=4.5, BACK_Z1=22.0,         # 背面元件区 (用户)
    PL_LED_D=3.2,                      # 平板 LED 隔光通道 (导光柱 PLP2 管身 Φ2.8 / 压筋 Φ3.1, 只隔光不夹管)
    PL_STEM_D=4.0,                     # 平板按键杆孔 (杆 Φ3.5)
    BTN_CLR=0.3, LEG_DEPTH=1.5,        # 背面开关本体 / 焊盘让位间隙, 脚让位深 (脚+锡 ≈1.0 + 0.5)
    HOLE_RGB=3.0, HOLE_LED=3.0,        # 外皮导光柱压管孔 (PLP2 官方 Φ2.9, 打印 Φ3.0; 协调 11-13)
    # 按键舌片: 外皮切 H 形缝 ⇒ 上键舌片根在上, 下键舌片根在下
    FLAP_W=5.5, FLAP_SLOT=1.0,         # 舌片宽 / 缝宽 (切穿外皮; 协调 11-13: 0.8 用 0.4 嘴易糊死 → 1.0)
    FLAP_BAR_Z=(15.5, 16.5),           # 'tie' 模式横缝 (宽 1.0, 两凸点中间); 'support' 模式横缝自动开到凸点边各留 0.4
    FLAP_MODE='support',                   # 'tie' = 横缝 1.0 + 两侧断开桥 (主件现用); 'support' = 无断开桥, 横缝开到两凸点各留 0.4 (≈Z13.9–17.1), 切片在上舌片下加支撑, 钳子拔出
    FLAP_TIE=0.6,                      # 'tie' 模式: 下罩正立打印: 上舌片底边 (横缝顶) 两侧竖缝各留 0.6 高断开桥 (不切穿), 舌片底层成 ~7 跨的两端搭桥; 打完用刀划开
    ROOF=True,                         # 让位腔顶做 45° 双坡屋顶 (下罩正立打印免平顶长桥)
    FLAP_TOP_Z1=30.0, FLAP_BOT_Z0=2.0, # 上舌片根 Z30 (墙实心到 Z32) / 下舌片根 Z2 (下罩底 Z0)
    FLAP_TMIN=0.8, FLAP_TMIN_BOT=0.8,  # 舌片内面挖薄后最薄 (r110 圆柱面 ⇒ 另一边厚 +0.45)
    FLAP_E=3000.0, SW_TRAVEL=0.2,      # 估按压力用: 打印 PLA E / 轻触开关行程
    NUB_D=3.0, NUB_GAP=0.3,            # 舌片内面凸点 Φ3 正对按键杆, 离杆顶 0.3
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
def comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c




def foot_poly(P, yP, s, o=0.0):
    """脚俯视轮廓 (含前端 45° 倒角): 平板前面角 (PL_X1, yP) 起 45° 一路倒到脚端 x=FOOT_X1; o = 外扩间隙"""
    x0, x1, y0 = P['FOOT_X0'], P['FOOT_X1'], P['FOOT_Y0']
    k = o * (math.sqrt(2) - 1)                                  # 45° 边外扩 o 后与水平 / 竖直边交点的偏移
    yc = yP - (x1 - P['PL_X1'])                                  # 倒角到脚端 y
    pts = [(x0 - o, y0 - o), (x1 + o, y0 - o), (x1 + o, yc + k), (P['PL_X1'] + k, yP + o), (x0 - o, yP + o)]
    return [(s * x, y) for x, y in pts]


def gable(x0, x1, y0, y1, z0, z1):
    """外包 box 顶上的 45° 双坡屋顶 (屋脊沿长边, 坡跨短边, 高 = 短边/2)"""
    if x1 - x0 >= y1 - y0:
        return yz_prism([(y0, z1), (y1, z1), ((y0 + y1) / 2, z1 + (y1 - y0) / 2)], x0, x1)
    pg = BRepBuilderAPI_MakePolygon()
    for x, z in [(x0, z1), (x1, z1), ((x0 + x1) / 2, z1 + (x1 - x0) / 2)]: pg.Add(gp_Pnt(x, y0, z))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, y1 - y0, 0)).Shape()


def make_key_bracket(p=None):
    P = dict(DEFAULTS, **(p or {}))
    c = P['CLR']
    yF, yB = KB.Y_BOARD_FRONT, KB.Y_BOARD_BACK                 # 100.6 / 99.0
    yP = P['PL_Y1']                                             # 平板前面 105.7
    yBear = yP - P['CB_H']                                      # 沉孔底 = 板螺丝头支承面 103.3
    MH = [KB.to_global(X, Y) for X, Y in KB.MH]                 # [(16.5, 13), (-16.5, 13)]
    FT, nT, X1 = P['FOOT_T'], P['NUT_T'], P['PL_X1']
    FH = [(s * P['FOOT_HX'], P['FOOT_HY']) for s in (1, -1)]    # 脚 M3 / 底盘孔
    rib = [(P['FOOT_Y0'], 0), (yF, 0), (yF, P['RIB_Z1']), (P['FOOT_Y0'], FT)]   # 筋侧视: 平板背面 Z18 → 脚内端
    bt = [KB.to_global(X, Y) for X, Y in KB.BTN]                # [(9, 19), (9, 12)]
    led = [(nm, *KB.to_global(X, Y), w, l, h) for nm, X, Y, w, l, h in KB.leds()]   # (名, x, z, 宽, 长, 高)
    # ---- 支架 ----
    br = fuse(box(-X1, yF, 0, X1, yP, P['PL_Z1']),                                  # 前面平板
              box(-X1, P['BAR_Y0'], 0, X1, yF, P['BAR_Z1']))                         # 板下横条
    for s in (1, -1):
        br = fuse(br, xy_prism(foot_poly(P, yP, s)[::s], 0, FT),                    # 横边 脚 (前端 45° 倒到平板前面角)
                  yz_prism(rib, s * P['RIB_X0'], s * P['RIB_X1']))                   # 三角筋
    cuts = []
    for x, z in MH:
        cuts += [ycyl(x, z, P['M3_D'], yF - 1, yP + 1), ycyl(x, z, P['CB_D'], yBear, yP + 1)]
    for x, y in FH:
        cuts.append(cyl(x, y, P['M3_D'], -1, FT + 1))
    for _, x, z, *_ in led:                                                          # 每颗 LED 单独隔光通道
        cuts.append(ycyl(x, z, P['PL_LED_D'], yF - 1, yP + 1))
    bc = P['BTN_CLR']; h6 = KB.BTN_BODY / 2 + bc
    px, py = KB.BTN_PAD_OUT[0] / 2 + bc, KB.BTN_PAD_OUT[1] / 2 + bc
    xb = bt[0][0]; zs = [z for _, z in bt]
    # 正面 R1–R6 / C1 共用让位腔 (11-13 (五) 单面贴): KB.smd_pocket() 板系 → 整机, 从平板背面 yF 挖深 d
    sp = KB.smd_pocket(); spx0, spz0 = KB.to_global(sp[2], sp[1]); spx1, spz1 = KB.to_global(sp[0], sp[3])
    cuts.append(box(spx0, yF - 1, spz0, spx1, yF + sp[4], spz1))
    for z in zs:                                                                                   # 每键单独 (间距 11, 中间平板仍压板)
        cuts += [box(xb - h6, yF - 1, z - h6, xb + h6, yF + KB.BTN_BODY_H + bc, z + h6),          # 开关本体让位
                 box(xb - px, yF - 1, z - py, xb + px, yF + P['LEG_DEPTH'], z + py)]               # 脚 / 焊盘让位
    cuts += [ycyl(xb, z, P['PL_STEM_D'], yF, yP + 1) for z in zs]                                 # 杆孔
    bracket = clean(cut(br, *cuts))
    assert BRepCheck_Analyzer(bracket).IsValid()
    # 自检
    assert yBear - yF >= 1.5 and P['CB_H'] >= P['HEAD_H']
    assert yBear - P['BOARD_SCREW_L'] <= yB - nT + 1e-9, '板螺丝没吃满法兰螺母'
    assert P['RIB_X0'] >= max(KB.W / 2 + 0.5, abs(MH[0][0]) + P['NUT_FL_D'] / 2 + 0.3) - 1e-9     # 筋离板边 / 板背面螺母
    assert P['FOOT_X0'] >= KB.W / 2 + 0.5 - 1e-9
    nr = P['NUT_FL_D'] / 2
    assert P['FOOT_HX'] - nr >= P['RIB_X1'] + 0.5 and P['FOOT_X1'] - (P['FOOT_HX'] + nr) >= 1.0 - 1e-9
    assert P['FOOT_HY'] - nr - P['FOOT_Y0'] >= 1.0 - 1e-9
    nut_ch = (X1 + yP - P['FOOT_HX'] - P['FOOT_HY']) / math.sqrt(2) - nr                        # 脚螺母法兰离 45° 倒角面
    assert nut_ch >= 0.5, nut_ch
    # 平板内部壁厚 (报给用户): LED 通道之间 / 通道与沉孔 / 本体腔与沉孔
    lx = sorted(x for _, x, *_ in led)
    walls = dict(LED间=round(min(b - a for a, b in zip(lx, lx[1:])) - P['PL_LED_D'], 2),
                 LED_沉孔=round(min(abs(abs(x) - abs(MH[0][0])) for x in lx) - P['PL_LED_D'] / 2 - P['CB_D'] / 2, 2),
                 本体腔_沉孔=round(abs(MH[0][0]) - P['CB_D'] / 2 - (xb + h6), 2),
                 脚腔_螺丝孔=round(abs(MH[0][0]) - P['M3_D'] / 2 - (xb + px), 2),
                 本体腔_RGB通道=round((xb - h6) - (led[0][1] + P['PL_LED_D'] / 2), 2),          # 11-13 (五) 按键转 90°: 壁厚 (>0 = 不连通)
                 脚腔_RGB通道=round((xb - px) - (led[0][1] + P['PL_LED_D'] / 2), 2),
                 SMD腔_LED通道=round(min(math.hypot(max(spx0 - x, 0, x - spx1), max(spz0 - z, 0, z - spz1)) - P['PL_LED_D'] / 2 for _, x, z, *_ in led), 2),
                 SMD腔_沉孔=round(min(math.hypot(max(spx0 - x, 0, x - spx1), max(spz0 - z, 0, z - spz1)) - P['CB_D'] / 2 for x, z in MH), 2),
                 SMD腔_按键腔=round(min(x_ - max(h6, px) for x_, _ in bt) - spx1, 2),          # 按键在 +x 侧 (x9), 腔在其 −x 侧
                 SMD腔深=sp[4], 平板剩=round(yP - yF - sp[4], 2))
    assert walls['SMD腔_LED通道'] >= 0.8 and walls['本体腔_RGB通道'] > 0 and walls['脚腔_RGB通道'] > 0, walls
    # ---- 板 + 元件简模 ----
    bd = box(-KB.W / 2, yB, KB.Z0, KB.W / 2, yF, KB.Z0 + KB.H)
    for x, z in MH: bd = cut(bd, ycyl(x, z, KB.MH_D, yB - 1, yF + 1))
    parts = [bd]; holes = []; env = []; stem_env = []          # env: (x0, x1, y0, y1, z1) 外包 (未加间隙)
    for X, Y in KB.BTN:
        x, z = KB.to_global(X, Y); h = KB.BTN_BODY / 2
        parts += [box(x - h, yF, z - h, x + h, yF + KB.BTN_BODY_H, z + h), ycyl(x, z, KB.BTN_STEM_D, yF + KB.BTN_BODY_H, yF + KB.BTN_H)]
        for x0, y0, w, hh in KB.btn_pads(X, Y):                                      # 焊盘 + 脚 (高 BTN_LEG_H)
            gx0, gz0 = KB.to_global(x0 + w, y0)
            parts.append(box(gx0, yF, gz0, gx0 + w, yF + KB.BTN_LEG_H, gz0 + hh))
        stem_env.append((x - KB.BTN_STEM_D / 2, x + KB.BTN_STEM_D / 2, yF, yF + KB.BTN_H, z + KB.BTN_STEM_D / 2))
    for (nm, x, z, w, l, hgt), hd in zip(led, [P['HOLE_RGB']] + [P['HOLE_LED']] * len(KB.LED)):
        parts.append(box(x - w / 2, yF, z - l / 2, x + w / 2, yF + hgt, z + l / 2)); holes.append((x, z, hd))
    # 正面 R1–R6 / C1 (PCB 出的 pcb/key_board_v1_2/front_parts.json: 焊盘∪本体外包 + 离板正面高度) —— 必须在平板让位腔里, 每边 ≥0.3, 顶离腔底 ≥0.3
    import json
    fpj = V12 / 'pcb' / 'key_board_v1_2' / 'front_parts.json'
    front_smd = {}
    if fpj.exists():
        for nm, d in json.loads(fpj.read_text(encoding='utf-8'))['parts'].items():
            u0, v0, u1, v1 = d['env_board_XY']; hh = d['height']
            gx0, gz0 = KB.to_global(u1, v0); gx1, gz1 = KB.to_global(u0, v1)
            parts.append(box(gx0, yF, gz0, gx1, yF + hh, gz1))
            m_ = min(u0 - sp[0], v0 - sp[1], sp[2] - u1, sp[3] - v1)
            assert m_ >= KB.SMD_CLR - 1e-6 and sp[4] - hh >= 0.3 - 1e-9, f'{nm} 不在平板让位腔里 (余量 {m_:.3f})'
            front_smd[nm] = (round(m_, 3), round(sp[4] - hh, 2))
    # ---- 背面 J1 (GH 12P 卧贴, 插口朝下) + 插头 + 线弯 / 走线 外包 (11-13 晚) ----
    g = KB.j1_geom()
    def gb(X0, Y0, X1, Y1, y0, y1):            # 板系矩形 → 整机 box (y 方向 y0..y1)
        return box(20.0 - X1, y0, KB.Z0 + Y0, 20.0 - X0, y1, KB.Z0 + Y1)
    yJ = yB - KB.J1_H                                                            # 座 / 插头背面 y94.75
    j1 = [gb(*g['body'], yJ, yB), gb(g['body'][0] + 1.0, g['body'][3], g['body'][2] - 1.0, g['pad_tip_Y'], yB - 0.4, yB)]   # 本体 + 脚尾 (焊盘区高 0.4)
    plug = gb(*g['plug'], yJ, yB)                                                # GHR-12V-S 外包 (露出插口 5.0, 宽 17.25, 厚 4.25)
    zP = KB.Z0 + g['plug'][1]                                                    # 插头端 Z4.0
    cw, ct = KB.CABLE_W / 2, KB.CABLE_T
    y_bar = P['BAR_Y0'] - 0.3                                                    # 线弯离支架底条背面 0.3
    cab_y0 = P['SPIG_IN'] - 4.8                                                  # 走线外包画到墙内面里 4.8 (y86)
    bend = box(-cw, yJ - 1.25, 0.2, cw, y_bar, zP)                               # 插头下 线弯 (Z0.2..4.0, 高 3.8 ≥ BEND)
    run = box(-cw, cab_y0, 0.2, cw, y_bar, 0.2 + ct)                             # 贴底盘往 −Y 出下罩
    cable = fuse(bend, run)
    # 背面贴片件 (PCB agent 出的 pcb/key_board_v1_2/back_parts.json; 11-13 (五) 单面贴后只剩 J1, 这里留着给以后背面加件)
    bpj = V12 / 'pcb' / 'key_board_v1_2' / 'back_parts.json'
    back_parts = {}
    if bpj.exists():
        for nm, d in json.loads(bpj.read_text(encoding='utf-8'))['parts'].items():
            if nm == 'J1': continue
            u0, v0, u1, v1 = d['courtyard_board_XY']                           # (别用 X1: 是平板半宽)
            back_parts[nm] = (u0, v0, u1, v1, d['height'])
            parts.append(gb(u0, v0, u1, v1, yB - d['height'], yB))
            assert d['height'] <= KB.BACK_MAX - 0.5 and all(math.hypot(max(u0 - mx, 0, mx - u1), max(v0 - my, 0, my - v1)) >= KB.BACK_KO_D / 2 for mx, my in KB.MH), f'{nm} 碰螺母禁布'
    parts += j1 + [plug, cable]
    assert zP - 0.2 >= KB.BEND, '插头下线弯不足 3'
    assert yJ - 1.25 >= KB.Y_BACK_MAX + 0.3 - 1e-9, '线弯出背面让位腔'
    j1_nut_gap = abs(MH[0][0]) - P['NUT_FL_D'] / 2 - KB.J1_W / 2                 # 座边到螺母法兰 (x 向)
    assert j1_nut_gap >= 1.0, j1_nut_gap
    assert zP - P['BAR_Z1'] >= 0.5, '插头碰支架底条'                              # 插头 y 跨到 99, 底条 y98..99 Z≤3
    # 下罩内壁底部出线缺口: 线 外包 +CLR_N 往里开穿墙内面 (底开, 下罩竖直罩下时从线上滑过)
    CLR_N = 2.0
    notch = box(-cw - CLR_N, cab_y0 - 1.0, -1.0, cw + CLR_N, yB - KB.BACK_MAX, 0.2 + ct + 1.2)   # x ±9, Z−1..3.0, y85..93
    j1info = dict(center_x=0.0, mate_z=KB.Z0 + KB.J1_MATE_Y, body_z=(KB.Z0 + g['body'][1], KB.Z0 + g['body'][3]), y=(yJ, yB), plug_z=(zP, KB.Z0 + KB.J1_MATE_Y),
                  bend=(round(zP - 0.2, 2), round(yJ - 1.25, 2), round(y_bar, 2)), run_z=(0.2, 0.2 + ct), notch=dict(x=round(cw + CLR_N, 2), z=(0.0, round(0.2 + ct + 1.2, 2)), y=(round(cab_y0 - 1.0, 2), round(yB - KB.BACK_MAX, 2))),
                  back_parts=back_parts, nut_gap=round(j1_nut_gap, 2), bar_gap=round(zP - P['BAR_Z1'], 2), pin1_x=round(20 - g['pins'][0][1], 3), pin12_x=round(20 - g['pins'][-1][1], 3))
    board = comp(parts)
    # ---- 紧固件位置 ----
    foot_tip = -P['DISC_T'] + P['M3_CB_H'] + P['FOOT_SCREW_L']                    # Z8
    for x, z in MH:
        env += [(x - nr, x + nr, yB - nT, yB, z + nr),                             # 背面法兰螺母 (头已埋进平板沉孔)
                (x - 1.5, x + 1.5, yBear - P['BOARD_SCREW_L'], yB, z + 1.5)]       # 杆尖
    for x, y in FH:
        env += [(x - nr, x + nr, y - nr, y + nr, FT + nT), (x - 1.5, x + 1.5, y - 1.5, y + 1.5, foot_tip)]   # 脚顶法兰螺母 / 杆尖
    # 支架 / 板 / 背面元件区 (元件本体都在平板外包里; 杆伸出平板的部分在舌片竖槽里, 另算)
    for s in (1, -1):
        lo = lambda a, b: (min(s * a, s * b), max(s * a, s * b))
        env += [(*lo(P['RIB_X0'], P['RIB_X1']), P['FOOT_Y0'], yF, P['RIB_Z1'])]  # 筋按外包盒让 (腔仍是竖柱体)
    env += [(-X1, X1, yF, yP, P['PL_Z1']),
            (-X1, X1, P['BAR_Y0'], yF, P['BAR_Z1']),
            (-KB.W / 2, KB.W / 2, yB, yF, KB.Z0 + KB.H),
            (-KB.W / 2, KB.W / 2, KB.Y_BACK_MAX, yB, P['BACK_Z1'])]
    # ---- 下罩让位腔: 每个外包 +CLR, 底一律开到 Z−1 (下罩从上往下罩, 竖直柱体并集 ⇒ 无倒扣) ----
    boxes = [(x0 - c, x1 + c, y0 - c, y1 + c, -1.0, z1 + c) for x0, x1, y0, y1, z1 in env]
    ZR = P['ROOF_ZMAX']
    assert max(b_[5] for b_ in boxes) <= ZR + 1e-9, ('让位腔顶超 ROOF_ZMAX', max(b_[5] for b_ in boxes))
    def roof(b_):                                                         # 45° 双坡, 超 ROOF_ZMAX 削平 (剩平顶桥 = 短边 − 2×(ZMAX − 腔顶))
        g_ = gable(*b_)
        if b_[5] + min(b_[1] - b_[0], b_[3] - b_[2]) / 2 > ZR + 1e-9:
            g_ = op(BRepAlgoAPI_Common, g_, box(b_[0] - 1, b_[2] - 1, b_[5] - 1, b_[1] + 1, b_[3] + 1, ZR))
        return g_
    feet = [foot_poly(P, yP, s, c) for s in (1, -1)]
    roofs = [roof(b) for b in boxes] if P['ROOF'] else []              # 每个外包顶加 45° 双坡 (只在外包投影内 ⇒ 外皮最薄不变, 腔仍包住竖直下落外包)
    pocket = clean(fuse(*[box(a, d, f, b_, e, g) for a, b_, d, e, f, g in boxes], *roofs, *[xy_prism(q[::s], -1.0, FT + c) for q, s in zip(feet, (1, -1))]))
    r_max = max([math.hypot(max(abs(a), abs(b_)), max(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes] + [math.hypot(x, y) for q in feet for x, y in q])
    r_min = min([math.hypot(0 if a < 0 < b_ else min(abs(a), abs(b_)), min(abs(d), abs(e))) for a, b_, d, e, _, _ in boxes] +
                [math.hypot(P['FOOT_X0'] - c, P['FOOT_Y0'] - c)])
    skin = P['SH_OUT'] - r_max
    assert skin >= P['SKIN_MIN'] - 1e-9, f'让位腔外皮 {skin:.2f} < {P["SKIN_MIN"]}'
    assert r_min >= P['SPIG_IN'] + 0.5, f'让位腔碰墙内面 r{r_min:.2f}'
    skin_holes = [ycyl(x, z, d, yF, P['SH_OUT'] + 2) for x, z, d in holes]
    # ---- 按键舌片: H 形缝 (切穿外皮) + 舌片内面挖薄 (竖槽, 底开到 Z−1, 罩下无倒扣) + 凸点 ----
    (xb, zhi), (xb2, zlo) = sorted(bt, key=lambda q: -q[1])                 # 上键 / 下键
    assert abs(xb - xb2) < 1e-9
    w2, sl = P['FLAP_W'] / 2, P['FLAP_SLOT']
    zb0, zb1 = P['FLAP_BAR_Z']
    if P['FLAP_MODE'] == 'support':                                         # 横缝开到凸点边各留 0.4
        zb0, zb1 = zlo + P['NUB_D'] / 2 + 0.4, zhi - P['NUB_D'] / 2 - 0.4
    else:
        assert P['FLAP_MODE'] == 'tie', P['FLAP_MODE']
    ys = yF + KB.BTN_H                                                      # 杆顶 108.1
    y_nub = ys + P['NUB_GAP']                                               # 凸点面 108.4
    y_out_min = math.sqrt(P['SH_OUT'] ** 2 - (abs(xb) + w2) ** 2)          # 舌片外缘处外皮外表面 (最靠里)
    y_thin = y_out_min - P['FLAP_TMIN']                                     # 上舌片内面
    y_thin_b = y_out_min - P['FLAP_TMIN_BOT']                               # 下舌片内面
    assert min(y_thin, y_thin_b) - y_nub >= 0.1, (y_thin, y_nub)            # 凸点至少凸 0.1
    assert zhi - P['NUB_D'] / 2 >= zb1 + 0.4 - 1e-9 and zlo + P['NUB_D'] / 2 <= zb0 - 0.4 + 1e-9
    Y0, Y1 = yF + 2.0, P['SH_OUT'] + 2
    rx0, rx1 = xb - w2 - sl, xb + w2 + sl                                   # 挖薄竖槽 x 范围 (= 缝外沿)
    # 杆伸出平板的部分 (+间隙) 必须落在竖槽里 (竖槽底开, 罩下时杆从槽里滑过)
    for a, b_, d, e, z1 in stem_env:
        assert a - c >= rx0 and b_ + c <= rx1 and e + c <= min(y_thin, y_thin_b) - 0.1 and z1 + c <= P['FLAP_TOP_Z1'], '杆不在舌片竖槽里'
    zt = zb1 + (P['FLAP_TIE'] if P['FLAP_MODE'] == 'tie' else 0.0)         # 断开桥 Z zb1..zt (竖缝这段不切)
    slots = [box(xa, Y0, za, xc, Y1, zc) for xa, xc in ((rx0, xb - w2), (xb + w2, rx1))           # 左右竖缝 (上下舌片共用)
             for za, zc in ((P['FLAP_BOT_Z0'], zb1), (zt, P['FLAP_TOP_Z1'])) if zc > za] + \
            [box(rx0, Y0, zb0, rx1, Y1, zb1)]                                   # 中间横缝
    nubs = [ycyl(xb, zlo, P['NUB_D'], y_nub, y_thin_b + 0.01), ycyl(xb, zhi, P['NUB_D'], y_nub, y_thin + 0.01)]
    recess = cut(fuse(box(rx0, Y0, -1.0, rx1, y_thin, P['FLAP_TOP_Z1']),
                      box(rx0, Y0, -1.0, rx1, y_thin_b, zb1)), *nubs)             # 两段都底开 (无倒扣)
    skin_holes += slots + [recess, notch]                                   # notch = J1 出线缺口 (下罩内壁底部)
    yo = [math.sqrt(P['SH_OUT'] ** 2 - xx ** 2) for xx in (abs(xb) - w2, abs(xb) + w2)]
    def force(yt, a):   # 悬臂在杆位置的弹性力 (不含开关力): F = 3EIδ/a³, 厚度沿宽线性 ⇒ I = b·mean(t³)/12; δ = 凸点间隙 + 行程
        t0, t1 = min(yo) - yt, max(yo) - yt
        I = P['FLAP_W'] * (t1 ** 4 - t0 ** 4) / (4 * (t1 - t0)) / 12
        return round(3 * P['FLAP_E'] * I * (P['NUB_GAP'] + P['SW_TRAVEL']) / a ** 3, 2)
    flap = dict(mode=P['FLAP_MODE'], slots=slots, x=xb, w=P['FLAP_W'], slot=sl, bar_z=(zb0, zb1), tie_z=(zb1, round(zt, 3)), top=(zb1, P['FLAP_TOP_Z1']), bot=(P['FLAP_BOT_Z0'], zb0),
                recess_x=(rx0, rx1), y_thin=round(y_thin, 3), y_thin_b=round(y_thin_b, 3),
                t_top=(round(min(yo) - y_thin, 2), round(max(yo) - y_thin, 2)), t_bot=(round(min(yo) - y_thin_b, 2), round(max(yo) - y_thin_b, 2)),
                y_nub=round(y_nub, 3), nub_h=round(min(y_thin, y_thin_b) - y_nub, 2), stem_y=ys, stems_z=(zlo, zhi),
                arm_top=P['FLAP_TOP_Z1'] - zhi, arm_bot=zlo - P['FLAP_BOT_Z0'],
                F_top=force(y_thin, P['FLAP_TOP_Z1'] - zhi), F_bot=force(y_thin_b, zlo - P['FLAP_BOT_Z0']))
    fx = [x for q in feet for x, _ in q]; fy = [y for q in feet for _, y in q]
    bb = [min([b[0] for b in boxes] + fx), max([b[1] for b in boxes] + fx), min([b[2] for b in boxes] + fy), max([b[3] for b in boxes] + fy),
          max(min(b[5] + (min(b[1] - b[0], b[3] - b[2]) / 2 if P['ROOF'] else 0), ZR) for b in boxes)]
    span = max(min(b[1] - b[0], b[3] - b[2]) - (2 * max(ZR - b[5], 0) if b[5] + min(b[1] - b[0], b[3] - b[2]) / 2 > ZR else min(b[1] - b[0], b[3] - b[2])) for b in boxes)   # 削平后剩的最长平顶桥
    res = dict(
        bracket=bracket, board=board, pocket=pocket, skin_holes=skin_holes,
        disc_m3=FH,                                             # 底盘 M3 孔 (Φ3.2 + 底面 Φ7×2) = 脚孔心
        foot_nut_z=(FT, FT + nT),                               # 脚顶法兰螺母 Z4..7.7
        foot_screw_L=P['FOOT_SCREW_L'], foot_screw_bear=-P['DISC_T'] + P['M3_CB_H'], foot_screw_tip=foot_tip,
        board_screws=[dict(x=x, z=z, bear_y=yBear, L=P['BOARD_SCREW_L'], nut_y=yB) for x, z in MH],
        holes=holes, leds=led, flap=flap, walls=walls, nut_chamfer=round(nut_ch, 2), plate=dict(x1=X1, y0=yF, y1=yP, z1=P['PL_Z1'], t=round(yP - yF, 2)),
        roof_span_flat=round(span, 2), skin=round(skin, 3), pocket_bbox=[round(v, 2) for v in bb], pocket_rmin=round(r_min, 2), pocket_front=round(yP + c, 3),
        j1=j1info, front_smd=front_smd, smd_pocket=dict(x=(round(spx0, 3), round(spx1, 3)), z=(round(spz0, 3), round(spz1, 3)), depth=sp[4]), j1_shapes=dict(j1=comp(j1), plug=plug, cable=cable, notch=notch),
        rib=rib, bracket_ymin=P['FOOT_Y0'], bracket_rmin=round(math.hypot(P['FOOT_X0'], P['FOOT_Y0']), 2),
        bracket_vol=round(vol(bracket), 1), params=P)
    return res


def write_stl(sh, path):
    BRepMesh_IncrementalMesh(sh, 0.01, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(sh, str(path))




def shroud_local(r):
    """预览用下罩局部: r90.8..110 墙段 (+Y 侧, Z0..32) − 让位腔 − 外皮孔 / 舌片缝 / 挖薄"""
    P = r['params']
    seg = cut(cyl(0, 0, 2 * P['SH_OUT'], 0, 32.0), cyl(0, 0, 2 * P['SPIG_IN'], -1, 33))
    seg = op(BRepAlgoAPI_Common, seg, box(-40, 80, -1, 40, 115, 33))
    return cut(seg, r['pocket'], *r['skin_holes'])


def _solids(sh):
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    out = []; e = TopExp_Explorer(sh, TopAbs_SOLID)
    while e.More(): out.append(e.Current()); e.Next()
    return out


def raster(layers, plane, u, v, res=0.15):
    """layers = [(shape, rgb)], plane = 'x'/'y'/'z' + 定值; 返回 RGB 图 (行 = v 由小到大)。后面的层盖前面的。"""
    import numpy as np
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.TopAbs import TopAbs_IN
    ax, val = plane
    us = np.arange(u[0], u[1], res); vs = np.arange(v[0], v[1], res)
    img = np.ones((len(vs), len(us), 3))
    for sh, col in layers:
        for so in _solids(sh):
            cl = BRepClass3d_SolidClassifier(so)
            for j, b in enumerate(vs):
                for i, a in enumerate(us):
                    p = {'x': (val, a, b), 'y': (a, val, b), 'z': (a, b, val)}[ax]
                    cl.Perform(gp_Pnt(*p), 1e-6)
                    if cl.State() == TopAbs_IN: img[j, i] = col
    return img


def _font():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    return plt


C_BR, C_BD, C_SH = (0.95, 0.76, 0.2), (0.18, 0.49, 0.2), (0.69, 0.75, 0.77)


def preview(r, sh, path):
    """6 张剖面: 侧视过按键 x=9 / 过三色 x=3, 俯视 Z16 (过 LED) / Z19 (过上键), 正视平板前面 y105.6 / 背面 y101.2"""
    import numpy as np
    from matplotlib.patches import Patch
    plt = _font()
    P = r['params']; f = r['flap']; yF = KB.Y_BOARD_FRONT; yP = P['PL_Y1']
    L = [(sh, C_SH), (r['bracket'], C_BR), (r['board'], C_BD)]
    fig, axs = plt.subplots(2, 3, figsize=(19, 12), dpi=100)
    def show(ax, img, u, v, title, xl, yl, invert=False):
        ax.imshow(img, origin='lower', extent=(u[0], u[1], v[0], v[1]), interpolation='nearest')
        ax.set_title(title, fontsize=10); ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=.25)
        if invert: ax.invert_xaxis()
    U, V = (86, 112), (-2, 34)
    for ax, x, nm in ((axs[0, 0], f['x'], '按键'), (axs[0, 1], r['leds'][0][1], '三色 1615')):
        show(ax, raster(L, ('x', x), U, V), U, V, f'侧视剖面 x={x:g} (过{nm}); 外面在右', 'y', 'Z')
        ax.axvline(P['SH_OUT'], color='b', lw=.6, ls=':')
    a = axs[0, 0]
    for z in f['stems_z']: a.annotate(f'杆顶 y{f["stem_y"]:g} / 凸点面 {f["y_nub"]:g}', (f['stem_y'], z), (93, z + 1.5), fontsize=7, arrowprops=dict(arrowstyle='->', lw=.6))
    a.text(87, 31, f"舌片 宽 {f['w']:g}, 缝 {f['slot']:g}, 横缝 Z{f['bar_z'][0]:g}–{f['bar_z'][1]:g}\n上根 Z{f['top'][1]:g} / 下根 Z{f['bot'][0]:g}; 最薄 {f['t_top'][0]:g}–{f['t_top'][1]:g}\n"
           f"弹性力 上 {f['F_top']:g} N / 下 {f['F_bot']:g} N (δ = 0.3 + 行程 {P['SW_TRAVEL']:g})", fontsize=7.5, va='top', bbox=dict(fc='w', alpha=.85))
    U2, V2 = (-34, 34), (86, 112)
    for ax, z, nm in ((axs[0, 2], r['leds'][0][2], 'LED 中心'), (axs[1, 0], f['stems_z'][1], '上键')):
        show(ax, raster(L, ('z', z), U2, V2), U2, V2, f'俯视剖面 Z{z:g} (过{nm})', 'x', 'y')
    U3, V3 = (-34, 34), (-2, 34)
    show(axs[1, 1], raster(L[1:], ('y', yP - 0.1), U3, V3), U3, V3, f'正视 (从外面看) 平板前面 y{yP - 0.1:g} 截面: 灯孔 Φ{P["PL_LED_D"]:g} / 杆孔 Φ{P["PL_STEM_D"]:g} / 沉孔 Φ{P["CB_D"]:g}', 'x (左右已翻转 = 板正视)', 'Z', invert=True)
    show(axs[1, 2], raster(L[1:], ('y', yF + 0.6), U3, V3), U3, V3, f'正视 平板背面 y{yF + 0.6:g} 截面 (板面上 0.6): 开关本体 + 脚让位 / 灯孔', 'x (左右已翻转 = 板正视)', 'Z', invert=True)
    for _, x, z, *_ in r['leds']:
        axs[1, 1].text(x, z - 2.6, f'x{x:g}', ha='center', fontsize=7)
    fig.legend(handles=[Patch(fc=C_SH, label='下罩 (局部)'), Patch(fc=C_BR, label='支架'), Patch(fc=C_BD, label='按键板 + 元件')], loc='lower center', ncol=3, fontsize=10)
    w = r['walls']
    fig.suptitle(f"按键板支架 key_bracket_v1_2 (11-13 前面平板)  平板 |x|≤{P['PL_X1']:g}, y{yF:g}–{yP:g} (厚 {r['plate']['t']:g}), Z0–{P['PL_Z1']:g};  "
                 f"外皮最薄 {r['skin']:.2f} (舌片除外); 前面 y{yP:g} 朝下打印\n平板内壁: LED 通道间 {w['LED间']:g}, 单色3 通道–沉孔 {w['LED_沉孔']:g}, 开关本体腔–沉孔 {w['本体腔_沉孔']:g}; "
                 f"按键本体腔–三色通道壁 {w['本体腔_RGB通道']:g}; R/C 让位腔 (深 {w['SMD腔深']:g}) –LED 通道壁 {w['SMD腔_LED通道']:g}", fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig(path); plt.close(fig)


def j1_preview(r, sh, path):
    """J1 + 插头 + 线弯 / 出线 vs 支架 / 下罩 / 底盘: 侧剖 x=0, 背面立剖 y(插头中), 俯剖 Z1.0"""
    from matplotlib.patches import Patch
    plt = _font()
    P = r['params']; j = r['j1']; J = r['j1_shapes']
    disc = op(BRepAlgoAPI_Common, cyl(0, 0, 2 * P['SH_OUT'], -P['DISC_T'], 0), box(-40, 70, -7, 40, 115, 1))
    nuts = comp([ycyl(s_['x'], s_['z'], P['NUT_FL_D'], s_['nut_y'] - P['NUT_T'], s_['nut_y']) for s_ in r['board_screws']])
    C_J, C_P, C_C, C_D, C_N = (0.1, 0.1, 0.1), (0.85, 0.85, 0.85), (0.9, 0.3, 0.2), (0.55, 0.45, 0.35), (0.45, 0.45, 0.5)
    L = [(disc, C_D), (sh, C_SH), (r['bracket'], C_BR), (r['board'], C_BD), (nuts, C_N), (J['plug'], C_P), (J['j1'], C_J), (J['cable'], C_C)]
    fig, axs = plt.subplots(1, 3, figsize=(21, 8.5), dpi=100)
    def show(ax, img, u, v, title, xl, yl, invert=False):
        ax.imshow(img, origin='lower', extent=(u[0], u[1], v[0], v[1]), interpolation='nearest')
        ax.set_title(title, fontsize=10); ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=.25)
        if invert: ax.invert_xaxis()
    U, V = (82, 112), (-7, 30)
    show(axs[0], raster(L, ('x', 0.0), U, V, 0.12), U, V, '侧视剖面 x=0 (过 J1 中线); 外面在右', 'y', 'Z')
    a = axs[0]
    a.axvline(P['SPIG_IN'], color='b', lw=.6, ls=':'); a.text(P['SPIG_IN'] - 0.3, 27, f"墙内面 r{P['SPIG_IN']:g}", ha='right', fontsize=7, color='b')
    a.annotate(f"J1 座 Z{j['body_z'][0]:g}–{j['body_z'][1]:.2f}", (96.9, 11), (84, 16), fontsize=8, arrowprops=dict(arrowstyle='->'))
    a.annotate(f"插头 GHR-12V-S 外包 Z{j['plug_z'][0]:g}–{j['plug_z'][1]:g}", (96.9, 6.5), (83, 10), fontsize=8, arrowprops=dict(arrowstyle='->'))
    a.annotate(f"线弯 Z0.2–{j['plug_z'][0]:g} (≥3), 离底条 0.3", (95.5, 2.5), (83, 6), fontsize=8, arrowprops=dict(arrowstyle='->'))
    a.annotate(f"下罩出线缺口 Z0–{j['notch']['z'][1]:g}, x ±{j['notch']['x']:g}", (91.5, 2.2), (83, -4.5), fontsize=8, arrowprops=dict(arrowstyle='->'))
    yc = (j['y'][0] + j['y'][1]) / 2
    U2, V2 = (-30, 30), (-7, 30)
    show(axs[1], raster(L, ('y', yc), U2, V2, 0.15), U2, V2, f'背面立剖 y{yc:.2f} (过插头, 从机器里往外看)', 'x', 'Z')
    axs[1].text(0, 27.5, f"pin1 x{j['pin1_x']:+g} / pin12 x{j['pin12_x']:+g}; 座边离螺母法兰 {j['nut_gap']:g}", ha='center', fontsize=8)
    U3, V3 = (-30, 30), (82, 112)
    show(axs[2], raster(L[1:], ('z', 1.0), U3, V3, 0.15), U3, V3, '俯视剖面 Z1.0 (线贴底盘穿下罩内壁缺口)', 'x', 'y')
    fig.legend(handles=[Patch(fc=c, label=n) for n, c in (('底盘', C_D), ('下罩 (局部)', C_SH), ('支架', C_BR), ('按键板', C_BD), ('M3 法兰螺母', C_N), ('J1 SM12B-GHS-TB', C_J), ('插头外包', C_P), ('线 (弯 + 出线) 外包', C_C))],
               loc='lower center', ncol=8, fontsize=9)
    fig.suptitle(f"按键板背面 J1 (JST GH 12P 卧贴, 插口朝下) 中心 x0, 插口面 Z{j['mate_z']:g}; 插头端 Z{j['plug_z'][0]:g}, 下面 {j['bend'][0]:g} 给线弯; 线贴底盘从下罩内壁底缺口出, 去电机控制板 U24", fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94)); fig.savefig(path); plt.close(fig)


def flap_front(r, sh, path):
    """外皮舌片正视图 (从外面看): r109.9 柱面上采样 (切穿的缝 / 孔 = 白), r 外皮 −1.0 处 (挖薄区 = 浅色)"""
    import numpy as np
    plt = _font()
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.TopAbs import TopAbs_IN
    P = r['params']; f = r['flap']; R = P['SH_OUT']
    cl = BRepClass3d_SolidClassifier(_solids(sh)[0]) if len(_solids(sh)) == 1 else None
    sols = [BRepClass3d_SolidClassifier(s) for s in _solids(sh)]
    def inside(p):
        for c in sols:
            c.Perform(p, 1e-6)
            if c.State() == TopAbs_IN: return True
        return False
    res = 0.1
    xs = np.arange(-16, 16, res); zs = np.arange(-0.5, 33, res)
    img = np.ones((len(zs), len(xs), 3))
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            if not inside(gp_Pnt(x, math.sqrt((R - 0.05) ** 2 - x * x), z)): continue          # 切穿 (缝 / 孔)
            img[j, i] = (0.86, 0.89, 0.91) if not inside(gp_Pnt(x, math.sqrt((R - 1.3) ** 2 - x * x), z)) else C_SH   # 挖薄 (≤1.3)
    fig, ax = plt.subplots(figsize=(9, 9.5), dpi=110)
    ax.imshow(img, origin='lower', extent=(xs[0], xs[-1] + res, zs[0], zs[-1] + res), interpolation='nearest')
    ax.invert_xaxis()
    for z in f['stems_z']:
        ax.add_patch(plt.Circle((f['x'], z), KB.BTN_STEM_D / 2, fc='none', ec='r', ls='--', lw=1))
        ax.text(f['x'] - 3.6, z, f'杆 Z{z:g}', va='center', fontsize=8, color='r')
    for (nm, x, z, *_), (_, _, d) in zip(r['leds'], r['holes']):
        ax.text(x, z - 2.4, f'{nm.split()[0]}\nΦ{d:g}', ha='center', va='top', fontsize=7)
    ax.annotate(f"上舌片 (根 Z{f['top'][1]:g})\n悬臂 {f['arm_top']:g}, 力 {f['F_top']:g} N", (f['x'], 26), (-3, 28), fontsize=8, arrowprops=dict(arrowstyle='->'))
    ax.annotate(f"下舌片 (根 Z{f['bot'][0]:g})\n悬臂 {f['arm_bot']:g}, 力 {f['F_bot']:g} N", (f['x'], 6), (-3, 3), fontsize=8, arrowprops=dict(arrowstyle='->'))
    ax.annotate(f"横缝 Z{f['bar_z'][0]:g}–{f['bar_z'][1]:g}" + (" (正立打印: 上舌片下加切片支撑, 钳子拔出)" if f['mode'] == 'support' else ''),
                (f['x'], sum(f['bar_z']) / 2), (2, 17), fontsize=8, arrowprops=dict(arrowstyle='->'))
    if f['mode'] == 'tie': ax.annotate(f"断开桥 Z{f['tie_z'][0]:g}–{f['tie_z'][1]:g} ×2\n(正立打印用, 打完刀划开)", (f['recess_x'][0] + f['slot'] / 2, sum(f['tie_z']) / 2), (2, 21), fontsize=8, color='#C62828', arrowprops=dict(arrowstyle='->', color='#C62828'))
    ax.set_title(f"下罩外皮正视 (从外面看, +Y 侧, 左右与板正视一致)\n深灰 = 外皮, 浅灰 = 舌片挖薄区 (内面槽, 最薄 {f['t_top'][0]:g}–{f['t_top'][1]:g}), 白 = 切穿 (H 缝宽 {f['slot']:g} / 导光柱孔); 红虚圈 = 按键杆", fontsize=9.5)
    ax.set_xlabel('整机 x (翻转)'); ax.set_ylabel('Z'); ax.set_aspect('equal'); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    from helpers import write_doc, bbox
    r = make_key_bracket()
    OUT.mkdir(parents=True, exist_ok=True)
    b = bbox(r['bracket'])
    t = gp_Trsf(); t.SetTranslation(gp_Vec(0, -b[1], -b[2]))     # 打印姿态 = 装配姿态, y 平移到 0 (切片时把 +Y 面 = 平板前面朝下)
    pr = xf(r['bracket'], t)
    write_stl(pr, OUT / 'key_bracket_v1_2.stl')
    write_doc([('key_bracket_v1_2', pr, '#F1C232', None, False)], OUT / 'key_bracket_v1_2.step', 'key_bracket_v1_2')
    write_doc([('key_board_v1_2', r['board'], '#2E7D32', None, False), ('key_bracket_v1_2', r['bracket'], '#F1C232', None, False)],
              OUT / 'key_board_bracket_装配位.step', 'key_board_bracket')
    sh = shroud_local(r)
    preview(r, sh, OUT / 'key_bracket_v1_2_preview.png')
    flap_front(r, sh, OUT / 'key_flap_front.png')
    j1_preview(r, sh, OUT / 'key_j1_preview.png')
    print('J1', r['j1'])
    print('支架 bbox', [round(v, 2) for v in b], '体积', r['bracket_vol'], 'mm3', '平板', r['plate'])
    print('底盘 M3 / 脚孔', r['disc_m3'], '脚螺母 Z', r['foot_nut_z'], '脚螺丝尖 Z', r['foot_screw_tip'], '脚螺母离倒角', r['nut_chamfer'],
          '板螺丝', [(s['x'], s['z'], s['bear_y'], s['L']) for s in r['board_screws']])
    print('让位腔 bbox', r['pocket_bbox'], '前面 y', r['pocket_front'], '外皮最薄', r['skin'], '腔最内 r', r['pocket_rmin'])
    print('平板内壁', r['walls'], '让位腔削平后最长平顶桥', r['roof_span_flat'])
    print('正面 R/C 让位腔', r['smd_pocket'], '每件 (离腔边, 离腔底)', r['front_smd'])
    print('舌片', {k: v for k, v in r['flap'].items() if k != 'slots'})


if __name__ == '__main__':
    main()
