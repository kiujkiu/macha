"""V1.2 紧固件装配预览 (2026-11-12 晚, 按用户实物参数): 按 build_v1_2 的孔位/高度放螺丝、螺母、铜螺母, 出 3MF + 干涉/啮合表。
    cd v1.2/scripts && ../../.venv/bin/python fasteners_v1_2.py
import build_v1_2 + 零件脚本 led_support / rotor_shroud / wireless_holder (只取几何, 不 import export_3mf_v1_2, 不写 models/); 输出:
    v1.2/assembly_v1_2_整机+螺丝.3mf   v1.2/out/fasteners_v1_2.json (表格数据)

实物 (用户 11-12):
  M3 螺丝  超薄头/家具头内六角, 头 Φ7 × 1.5, 2mm 六角 — 画成 Φ7×1.5 圆柱头 + Φ3 杆
  M3 螺母  法兰螺母, 法兰 Φ7.6, 对边 5.9 (外接 6.81), 总厚 3.7 — 画成 法兰 Φ7.6×1 + 六角 (对边 5.9) ×2.7, 中心 Φ3 孔 (与杆不重叠, 啮合另算)
  铜螺母  M3 压入/热熔, 外径 4.2, 中心 Φ3 孔; 11-12 夜统一 M3×4 装 Φ4.2×4.2 孔 (底面齐平): 底盘 Z-6..-2, 法兰盘 Z8.5..12.5
  M6      大扁头 Φ12.5×2.5 (项目惯用) + M6 六角螺母 对边 10 × 5.2 (XT60 11-12 晚改 M3 后, 本文件已无 M6 件)
"""
import math, json, zipfile
import numpy as np
import build_v1_2 as B
from build_v1_2 import cyl, fuse, cut, op, vol, bbox, solids
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.gp import gp_Pnt, gp_Vec
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool, BRep_Builder
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Compound

# ---------------- 紧固件尺寸 ----------------
M3_HEAD_D, M3_HEAD_H = 7.0, 1.2                      # 11-19 用户「螺丝的头深度都是1.2mm左右」(原 1.5); 沉孔仍 1.5, 头缩进 0.3
NUT_FL_D, NUT_FL_H, NUT_AF, NUT_T = 7.6, 1.0, 5.9, 3.7
INS_D = 4.2
INS_L_DISC, INS_L_FL = 4.0, 4.0                 # 11-12 夜: 全部 M3×4 (孔 Φ4.2×4.2)
M6_HEAD_D, M6_HEAD_H = 12.5, 2.5
M6_NUT_AF, M6_NUT_T = 10.0, 5.2


def comp(shapes):
    bb = BRep_Builder(); c = TopoDS_Compound(); bb.MakeCompound(c)
    for s in shapes:
        bb.Add(c, s)
    return c


def hexprism(x, y, af, z0, z1):
    rc = af / math.sqrt(3)                       # 外接圆半径
    pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.radians(30 + 60 * k)
        pg.Add(gp_Pnt(x + rc * math.cos(a), y + rc * math.sin(a), z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()


def screw_up(x, y, bear_z, L, d=3.0, hd=M3_HEAD_D, hh=M3_HEAD_H):
    """头在下, 支承面 Z=bear_z, 杆朝上长 L (L 按螺纹长 = 头下长度)。"""
    return fuse(cyl(x, y, hd, bear_z - hh, bear_z), cyl(x, y, d, bear_z, bear_z + L))


def screw_down(x, y, bear_z, L, d=3.0, hd=M3_HEAD_D, hh=M3_HEAD_H):
    """头在上, 支承面 Z=bear_z, 杆朝下长 L。"""
    return fuse(cyl(x, y, hd, bear_z, bear_z + hh), cyl(x, y, d, bear_z - L, bear_z))


def flange_nut(x, y, z0):
    """M3 法兰螺母, 法兰朝下压在 z0 面上。"""
    return cut(fuse(cyl(x, y, NUT_FL_D, z0, z0 + NUT_FL_H), hexprism(x, y, NUT_AF, z0 + NUT_FL_H, z0 + NUT_T)),
               cyl(x, y, 3.0, z0 - 1, z0 + NUT_T + 1))


def flange_nut_inv(x, y, z0):
    """M3 法兰螺母倒放 (MOS 压块 / 电容卡件螺母井): 六角朝下坐井底 z0, 法兰朝上。"""
    return cut(fuse(hexprism(x, y, NUT_AF, z0, z0 + NUT_T - NUT_FL_H), cyl(x, y, NUT_FL_D, z0 + NUT_T - NUT_FL_H, z0 + NUT_T)),
               cyl(x, y, 3.0, z0 - 1, z0 + NUT_T + 1))


def m6_nut(x, y, z0):
    return cut(hexprism(x, y, M6_NUT_AF, z0, z0 + M6_NUT_T), cyl(x, y, 6.0, z0 - 1, z0 + M6_NUT_T + 1))


def insert(x, y, z0, L):
    return cut(cyl(x, y, INS_D, z0, z0 + L), cyl(x, y, 3.0, z0 - 1, z0 + L + 1))


ZB = -B.DISC_T                                     # 底盘底面 Z-6
CB_BEAR = ZB + B.M3_CB_H                           # M3 沉孔底 (头支承面) Z-4
MF_BEAR = B.MF_TOP - B.MF_CB                       # 安装法兰顶沉孔底 Z14.5
BOARD_TOP = B.BOARD_Z + 1.6
F = []                                             # (名称, shape, 颜色)
S = []                                             # 每处螺丝: dict(组, x, y, dir, bear, L, tip, d, 啮合件)


def add(name, sh, color):
    F.append((name, sh, color))


def screw(group, i, x, y, bear, L, up, d=3.0, engage=None, **kw):
    sh = (screw_up if up else screw_down)(x, y, bear, L, d=d, **kw)
    add(f"{group} #{i}", sh, "#C0C0C0")
    S.append(dict(group=group, i=i, x=x, y=y, up=up, bear=bear, L=L, tip=bear + L if up else bear - L, d=d,
                  hh=kw.get('hh', M3_HEAD_H), hd=kw.get('hd'), engage=engage, shape=sh))


# 1 电机 4×M3 盘底沉孔往上, 拧电机底面螺纹 (螺纹深度待电机规格书)
L_MOTOR = 10.0                                     # 11-18 玻纤板底座: 支承 Z-6 (原 -4) ⇒ 盘底往上 M3 全部 +2, 尖不变
for i, (x, y) in enumerate(B.MOTOR_HOLES):
    screw(f"M3x{L_MOTOR:g} 电机", i, x, y, CB_BEAR, L_MOTOR, True, engage=("电机底螺纹", B.MOTOR_Z0, None))
# 2 线圈环四角 4×M3 盘底往上 + 法兰螺母压四角顶 (11-12 夜: 角厚 4.5 ⇒ Z4.5..8.2); 尾端 Z8.0 < 法兰盘底 Z8.5
L_RING = 14.0
for i, (x, y) in enumerate(B.RING_M3):
    screw(f"M3x{L_RING:g} 线圈环角", i, x, y, CB_BEAR, L_RING, True, engage=("法兰螺母", B.RING_CORNER_T, B.RING_CORNER_T + NUT_T))
    add(f"M3 法兰螺母 线圈环角 #{i}", flange_nut(x, y, B.RING_CORNER_T), "#707070")
# 3 下罩三角块 4×M3 盘底往上 + 法兰螺母压三角块顶 (Z5..8.7)
L_SH = 16.0
for i, (x, y) in enumerate(B.SH_M6):
    screw(f"M3x{L_SH:g} 下罩", i, x, y, CB_BEAR, L_SH, True, engage=("法兰螺母", B.TRI_T, B.TRI_T + NUT_T))
    add(f"M3 法兰螺母 下罩 #{i}", flange_nut(x, y, B.TRI_T), "#707070")
# 4 中央 8×M3 安装法兰顶沉孔往下, 拧底盘底面 Φ8×3.7 沉孔里的 M3 法兰螺母 (11-19, 原 M3×4 铜螺母; 法兰朝下齐底面 Z-7.5..-3.8)
L_C = 22.0                                         # 11-18: 底盘底 Z-7.5 (原 -6) ⇒ 20→22, 尖齐底面
for i, (x, y) in enumerate(B.FLANGE_SCREWS):
    screw(f"M3x{L_C:g} 中央", i, x, y, MF_BEAR, L_C, False, engage=("M3 法兰螺母", ZB, ZB + NUT_T))
    add(f"M3 法兰螺母 底盘底 G #{i}", flange_nut(x, y, ZB), "#707070")
# 5 外圈 8×M3 安装法兰顶沉孔往下, 拧法兰盘底面铜螺母 (11-12 夜: M3×4 齐法兰盘底 Z8.5..12.5); M3×6 尾端 Z8.5 齐底面, 啮合 4
L_LID = 6.0
for i, (x, y) in enumerate(B.LID_SCREWS):
    screw("M3x6 上下盖", i, x, y, MF_BEAR, L_LID, False, engage=("铜螺母", B.FL_Z0, B.FL_Z0 + INS_L_FL))
    add(f"铜螺母 M3x4 法兰盘 B #{i}", insert(x, y, B.FL_Z0, INS_L_FL), "#B8860B")
# 6 控制板 4×M3 (用户 11-13): 盘底 Φ7×2 沉孔往上, 穿底盘 + 板, M3 法兰螺母坐板顶 (原板顶往下进底盘 H 铜螺母)
L_BD = 12.0                                        # 支承 Z-4, 尖 Z6; 螺母 Z1.6..5.3 ⇒ 吃满 3.7, 露 0.7
for i, (bx, by) in enumerate(B.BHOLES):
    p = gp_Pnt(bx, by, 0).Transformed(B.BT)
    screw(f"M3x{L_BD:g} 控制板", i, p.X(), p.Y(), CB_BEAR, L_BD, True, engage=("法兰螺母", BOARD_TOP, BOARD_TOP + NUT_T))
    add(f"M3 法兰螺母 控制板 #{i}", flange_nut(p.X(), p.Y(), BOARD_TOP), "#707070")
# 7 XT60 2×M3 (用户 11-12 晚, 原 M6×20 + M6 螺母): 盘底 Φ7×2 沉孔往上, 穿底盘+底垫+压块 (叠高 13),
#   11-12 晚 (二): 压块顶螺母座取消, M3 法兰螺母直接坐压块顶 Z13..16.7, 尖 Z16 ⇒ 啮合 3.0; 下罩 Φ8.2 井到 Z17.5
#   11-13 晚 (V1.2-g): 底盘已打印, XT60 孔仍是 M6 Φ6.4 + 底面 Φ13×3 (沉孔顶 Z−3) ⇒ M3 大垫片 Φ9×0.8 顶在沉孔顶 (Z−3.8..−3), 头支承 Z−3.8, M3×20 尖 Z16.2 ⇒ 啮合 3.2
L_XT = 22.0
XT_NUT_Z0 = B.XT_H                                 # 13 (螺母座取消, 原 XT_H - XT_NUT_SEAT_H = 12)
XT_BEAR = ZB + B.M3_CB_H                          # −4 (新底盘 XT60 孔改标准 M3 Φ7×2 沉孔, 无垫片; 已打印 11-12 底盘另加 Φ9×0.8 大垫片, 见 BOM 6b)
for i, (x, y) in enumerate(B.XT_GHOLES_DISC):
    screw(f"M3x{L_XT:g} XT60", i, x, y, XT_BEAR, L_XT, True, engage=("法兰螺母", XT_NUT_Z0, XT_NUT_Z0 + NUT_T))
    add(f"M3 法兰螺母 XT60 #{i}", flange_nut(x, y, XT_NUT_Z0), "#707070")

# 8 线圈驱动板 MOS 压块 / 电容卡件各 2×M3 (用户 11-12 夜): 盘底 Φ7×2 沉孔往上, 穿底盘 + 件 (Φ3.4 通)
#   11-12 夜 (二) 「cap和mos的件，m3做通孔加M4.2沉孔」: 改铜螺母 M3×4 (外径 4.2) 从件顶面压进 Φ4.2×4.2 盲孔, 顶齐件顶 (生成器 NUT_MODE='insert');
#   旧法兰螺母倒放螺母井 (NUT_MODE='flange') 仍兼容
for _k, _nm in (('MC', 'MOS压块'), ('CC', '电容卡件')):          # 生成器有才放 (scripts/mos_clamp_v1_2.py / cap_clamp_v1_2.py)
    _z0, _L = getattr(B.CD, f'{_k}_NUT_Z0'), getattr(B.CD, f'{_k}_SCREW_L')
    if _z0 is None: continue
    _res = getattr(B.CD, f'{_k}_RES', None) or {}
    _ins = _res.get('nut_mode') == 'insert'
    for i, (x, y) in enumerate(getattr(B.CD, f'{_k}_HOLES')):
        if _ins:
            _i0, _i1 = _res['insert_z0'], _res['insert_z1']
            screw(f"M3x{_L:g} {_nm}", i, x, y, CB_BEAR, _L, True, engage=("铜螺母", _i0, _i1))
            add(f"铜螺母 M3x{_i1 - _i0:g} {_nm} #{i}", insert(x, y, _i0, _i1 - _i0), "#B8860B")
        else:
            screw(f"M3x{_L:g} {_nm}", i, x, y, CB_BEAR, _L, True, engage=("法兰螺母", _z0, _z0 + NUT_T))
            add(f"M3 法兰螺母 {_nm} #{i}", flange_nut_inv(x, y, _z0), "#707070")   # 倒放: 六角朝下坐井底

# 9 按键支架 (用户 11-13 (二) L 形, scripts/key_bracket_v1_2.py): 脚 2×M3 盘底 Φ7×2 沉孔往上, 穿底盘 4 + 脚 4, M3 法兰螺母坐脚顶 (Z4..7.7);
#   M3×12 支承 Z-4 尖 Z8 ⇒ 吃满 3.7, 露 0.3 (M3×10 尖 Z6 只进 2)
_K = B.KEY
_kn0, _kn1 = _K['foot_nut_z']
for i, (x, y) in enumerate(_K['disc_m3']):
    screw(f"M3x{_K['foot_screw_L']:g} 按键支架", i, x, y, CB_BEAR, _K['foot_screw_L'], True, engage=("法兰螺母", _kn0, _kn1))
    add(f"M3 法兰螺母 按键支架 #{i}", flange_nut(x, y, _kn0), "#707070")
# 10 按键板 2×M3 (沿 −Y, 11-13 (三) 前面平板): 超薄头埋进平板前面 Φ7.4×2.4 沉孔 (支承 y103.3), 穿平板剩壁 2.7 + 板 1.6, 板背面 (y99) M3 法兰螺母 (y99→95.3); M3×8 尖 y95.3 ⇒ 吃满 3.7 (尖齐螺母端面)
#    局部沿 Z 造好再绕 X 轴转 +90°: 局部 (x, 13, t) → 整机 (x, −t, 13)
from OCP.gp import gp_Trsf, gp_Ax1, gp_Dir
_RX = gp_Trsf(); _RX.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)
KEY_ROWS = []
for i, s_ in enumerate(_K['board_screws']):
    x, z, by, L, ny = s_['x'], s_['z'], s_['bear_y'], s_['L'], s_['nut_y']
    add(f"M3x{L:g} 按键板 #{i}", B.xf(screw_up(x, z, -by, L), _RX), "#C0C0C0")
    add(f"M3 法兰螺母 按键板 #{i}", B.xf(flange_nut(x, z, -ny), _RX), "#707070")
    tip = by - L
    KEY_ROWS.append(dict(组=f"M3x{L:g} 按键板", 号=i, x=round(x, 2), Z=round(z, 2), 方向="−Y", 支承面y=round(by, 2), 尾端y=round(tip, 2),
                         啮合="法兰螺母", 啮合长=round(max(0.0, min(ny, by) - max(tip, ny - NUT_T)), 2)))

# 7 玻璃下 玻璃座↔底座 8×M3×50 (11-14 四): 玻璃座顶面 Φ7 沉孔往下, 穿通两段, 底座底面 Φ8.2 孔里法兰螺母 (Z3.3..7.0, 法兰朝上)
for i, (x, y) in enumerate(B.JN_PTS):
    screw("M4x50 超薄头 玻璃下底座+玻璃座", i, x, y, B.JN_BEAR, B.JN_L, False, d=4.0, hd=8.5, hh=B.JN_HH, engage=("M4 法兰螺母", B.JN_NUT_Z1 - B.JN_NUT_H, B.JN_NUT_Z1))
    _z0 = B.JN_NUT_Z1 - B.JN_NUT_H                 # 11-16 用户: 法兰朝上 (六角 6.9 在下, 法兰 Φ9.7×1.2 顶窝顶)
    add(f"M4 法兰螺母 玻璃下底座底 #{i}", cut(fuse(hexprism(x, y, 6.9, _z0, B.JN_NUT_Z1 - 1.2), cyl(x, y, 9.7, B.JN_NUT_Z1 - 1.2, B.JN_NUT_Z1)), cyl(x, y, 4.0, -1, 10)), "#707070")
# 7b 玻璃上 外件 (11-17): 8×M3×6 超薄头 (头 Φ7×1.5 在顶面) 穿压圈 Φ3.4 → 玻璃上环顶面 M3×4 铜螺母 (Φ4.2×4.2, 顶齐环顶)
for i, (x, y) in enumerate(B.GC_PTS):
    screw(f"M3x{B.GC_SCREW_L:g} 超薄头 玻璃压圈", i, x, y, B.GC_BEAR, B.GC_SCREW_L, False, hd=B.GC_HEAD_D, hh=B.GC_HEAD_H, engage=("铜螺母", B.GC_Z0 - B.GC_INS_H, B.GC_Z0))
    add(f"铜螺母 M3x4 玻璃上环 #{i}", cut(cyl(x, y, INS_D - 0.02, B.GC_Z0 - B.GC_INS_H, B.GC_Z0), cyl(x, y, 3.0, 0, 400)), "#B8860B")

# 11 V2 灯板支撑 (11-16 晚 偏心 SCR_ECC + 耳朵脚, led_support_v1_2): 中间 T 件取消;
#    两端立板耳朵 4×M3×14 内六角 (头支承 = 耳朵顶 Z36) 穿耳朵 + 承载盘 Φ3.4 → 毂盘底 M3×4 铜螺母 (= 外圈锁盘 k=0/3/4/7, 铜螺母在下面外圈循环里一起放, 不重复计);
#    立板底面 Φ6×3 沉孔 2×M3×8 从下往上自攻进夹条 (x=±73, y=ECC); 梳齿 → 帽 2×M3×8 进帽内铜螺母 (y=ECC);
#    底板 r4e 4×M3 (四角, 11-16 晚 改一颗螺丝穿到底): M3×8 超薄头 (Φ7×1.5) 从承载盘底 Φ7.4×1.5 沉孔往上 (头支承 Z31) → 承载盘 Φ3.4 → 尼龙光孔垫柱 Φ6×3
#    → 板 1.6 → 板顶 M3 尼龙螺母 (B.BB_NUT_SPEC, 高 2.4); 承载盘不再压铜螺母; 装配: 底板先装承载盘, 再装承载盘到毂盘
import led_support_v1_2 as L
for i, (x, y) in enumerate([] if B.ROTOR_B else L.FOOT_PTS):   # 转子盘B: 立板耳朵没了 (固定件锚孔见 12b)
    screw(f"M3x{L.FOOT_SCREW_L:g} 内六角 立板耳朵 (兼锁盘)", i, x, y, L.FOOT_CB_Z, L.FOOT_SCREW_L, False, hd=5.5, hh=3.0, engage=("铜螺母", *L.HUB_INS))
for i, x in enumerate(L.BAR_SCR_X):
    screw(f"M3x{L.BAR_SCR_L:g} 内六角 立板→夹条 (自攻)", i, x, L.BAR_SCR_Y, L.BAR_SCR_BEAR, L.BAR_SCR_L, True, hd=5.5, hh=3.0, engage=("夹条 Φ2.6 自攻", L.Z0, L.Z0 + L.BAR_TAP_H))
for i, sx in enumerate((1, -1)):
    screw("M3x8 内六角 梳齿→帽", i, sx * L.COMB_FIX_X, L.ECC, L.COMB_Z1, 8.0, False, hd=5.5, hh=3.0, engage=("铜螺母", L.Z1, L.Z1 + L.CAP_T))
    add(f"M3x4 铜螺母 灯板顶帽 #{i}", insert(sx * L.COMB_FIX_X, L.ECC, L.Z1, L.CAP_T), "#B8860B")
BB_NUT_Z0 = L.RIM_TOP + B.BB_STANDOFF + B.BB_T                 # 板顶 Z36.6
# 转子盘B: 承载盘底面 Φ7.4×1.5 让位沉孔在托盘底 (头支承 Z28.8, 头不进线圈腔) ⇒ 到板顶螺母顶 Z39 要 10.2 ⇒ M3×12 (尖 Z40.8 出螺母 1.8); 原转子 M3×8 头支承 Z31
_BBZ, _BBL = ((B.Z_RIM_TOP - 3.2 + 1.5), 10.0) if B.ROTOR_B else (B.BB_SCREW_HEAD_Z, B.BB_SCREW_L)
for i, (x, y) in enumerate(B.BB_HOLES):
    add(f"尼龙光孔垫柱 Φ6×3 底板 #{i}", cut(cyl(x, y, 6.0, L.RIM_TOP, L.RIM_TOP + B.BB_STANDOFF), cyl(x, y, 3.2, 0, 60)), "#EEEEEE")
    screw(f"M3x{_BBL:g} 超薄头 底板", i, x, y, _BBZ, _BBL, True, engage=("尼龙螺母", BB_NUT_Z0, BB_NUT_Z0 + B.BB_NUT_H))
    add(f"M3 尼龙螺母 底板 #{i}", cut(hexprism(x, y, 5.5, BB_NUT_Z0, BB_NUT_Z0 + B.BB_NUT_H), cyl(x, y, 3.0, 0, 60)), "#F5F5F0")   # 对边 5.5 × 2.4
# 11-16 晚: 承载盘+毂盘外圈 8 孔 B.RH_R @22.5°+45°k 全 Φ3.4 通孔 (无沉孔); k=1/2/5/6 M3×RH_L 头压盘顶 Z32, k=0/3/4/7 被立板耳朵占 (上面 M3×14)
for i, k in enumerate([] if B.ROTOR_B else B.RH_STD_IDX):
    x, y = B.RH_PTS[k]
    screw(f"M3x{B.RH_L:g} 内六角 承载盘→毂盘 外圈锁盘", i, x, y, B.RH_BEAR, B.RH_L, False, hd=5.5, hh=3.0, engage=("铜螺母", *B.RH_INS))
for i, (x, y) in enumerate([] if B.ROTOR_B else B.RH_PTS):   # 8 颗毂盘底铜螺母 (锁盘 4 + 耳朵 4 共用这一批)
    add(f"M3x4 铜螺母 毂盘底 外圈 #{i}", cut(cyl(x, y, INS_D - 0.02, *B.RH_INS), cyl(x, y, 3.0, 0, 50)), "#B8860B")   # Φ4.18 免同轴同径误报

# 12 转子罩 a/b (11-16 晚, rotor_shroud_v1_2; 偏心后 A/B 两半不同件): 罩壁 RS.R0–R1; 罩底凸台 RS.HOLE_R @RS.MNT_A (= B.SHR_HOLES),
#    M3×8 内六角 头支承凸台顶 Z36 → 承载盘顶面 M3×4 铜螺母 (Z28..32)
import rotor_shroud_v1_2 as RS
for i, a in enumerate([] if B.ROTOR_B else RS.MNT_A):
    x, y = RS.pol(RS.HOLE_R, a)
    screw(f"M3x{RS.MNT_L:g} 内六角 转子罩底", i, x, y, RS.BOSS_Z1, RS.MNT_L, False, hd=5.5, hh=3.0, engage=("铜螺母", *RS.INS_Z))
    add(f"M3x4 铜螺母 承载盘 转子罩 #{i}", insert(x, y, RS.INS_Z[0], RS.INS_Z[1] - RS.INS_Z[0]), "#B8860B")
#    分缝 (x=0, ±y) 4×M3×14 切向 (沿 x): 头支承 x=∓7 (凸耳面), 尾 x=±7; M3 六角螺母 (对边 5.5×2.4) 在对侧凸耳槽 x ±4.5..±6.9 (口朝罩内)
#    形状直接用 rotor_shroud 的外购件实体; 啮合/净空解析 + 沿 x 打探针
SEAM_ROWS = []


def probe_x(y, z, d, x, sx, span=60.0):
    """从 x 沿 sx (±1) 方向打一根 Φd 横柱, 返回 (距离, 件名)"""
    col = RS.xcyl(y, z, d, *sorted((x + sx * 1e-3, x + sx * span)))
    best = (None, None)
    for pn in PARTS:
        for b in common_bbox(col, pn):
            dist = (b[0] - x) if sx > 0 else (x - b[3])
            if best[0] is None or dist < best[0]:
                best = (dist, pn)
    return best


_k = 0
for sy in (() if B.ROTOR_B else (1, -1)):   # 转子盘B 罩子沿灯板线分 2 片, 没有 x=0 分缝
    sxh = -1 if sy > 0 else 1                       # +y 缝头在 −x (B 侧), −y 缝头在 +x (A 侧)
    for z in RS.LUG_SZ:
        add(f"M3x{RS.SEAM_L:g} 内六角 转子罩分缝 #{_k}", RS.seam_scr[_k], "#C0C0C0")
        add(f"M3 螺母 转子罩分缝 #{_k}", RS.seam_nut[_k], "#707070")
        xb = sxh * RS.LUG_HX; xt = xb - sxh * RS.SEAM_L
        xn = sorted((-sxh * (RS.LUG_HX - 0.1), -sxh * (RS.LUG_HX - 0.1 - RS.NUT_T)))
        lo, hi = sorted((xb, xt))
        SEAM_ROWS.append(dict(组=f"M3x{RS.SEAM_L:g} 内六角 转子罩分缝", 号=_k, x=None, y=round(sy * RS.LUG_SY, 2), Z=z, 方向="+X" if sxh < 0 else "−X",
                              支承面x=xb, 尾端x=xt, 啮合="M3 螺母", 啮合长=round(max(0.0, min(hi, xn[1]) - max(lo, xn[0])), 2),
                              螺母x=[round(v, 2) for v in xn], 尾端出螺母=round(abs(xt) - (RS.LUG_HX - 0.1), 2),
                              _probe=(sy * RS.LUG_SY, z, xb + sxh * 3.0, sxh, xt, -sxh)))
        _k += 1
#    配重唇 M3×18 (24 孔, 按需装): 只放 1 个示例 (W_A[0]) + 唇下 1 颗锁紧螺母 (Z65.1..67.5)
_wa = next(a for a in RS.W_A if a not in RS.LID_SCR_ALL)   # 第一个真正的配重孔 (盖螺丝占的 4 个除外)
_wx, _wy = RS.pol(RS.W_R, _wa)
screw(f"M3x{RS.W_L:g} 内六角 转子罩配重 (示例)", 0, _wx, _wy, RS.W_BEAR, RS.W_L, False, hd=5.5, hh=3.0, engage=("M3 螺母", RS.LIP_Z0 - RS.NUT_T, RS.LIP_Z0))
add("M3 螺母 转子罩配重 (示例) #0", RS.hexnut_z(_wa, RS.W_R, RS.LIP_Z0 - RS.NUT_T, RS.LIP_Z0 - 0.01), "#707070")   # 平边朝罩壁
#    顶盖 (11-16 晚: +y 盖 rotor_lid_v1_2 / −y 盖 rotor_lid_b_v1_2 两件不同): 每片 2×M3×8 内六角 (平底沉孔, 头顶齐盖顶 Z73.08) 穿盖凸块 + 配重唇, 唇下 M3 螺母
#    LID_SCR_ALL = +y 片 LID_SCR_A (47.5/132.5°) + −y 片 (+180 = 227.5/312.5°)
for i, (a, sh, nt) in enumerate([] if B.ROTOR_B else zip(RS.LID_SCR_ALL, RS.FAST['M3×8 内六角 (顶盖)'], RS.FAST['M3 螺母 (顶盖, 唇下)'])):
    _lid = "+y 盖" if math.sin(math.radians(a)) > 0 else "−y 盖"
    add(f"M3x{RS.LID_SCR_L:g} 内六角 转子罩顶盖 {_lid} #{i}", sh, "#C0C0C0"); add(f"M3 螺母 转子罩顶盖 {_lid} (唇下) #{i}", nt, "#707070")

# 12b 转子盘B (11-18 进整机; rotor_b_v1_2 / rotor_shroud_b_v1_2):
#    玻纤板底 16 颗超薄头 M3 往上 (头埋 Φ7.2×1.5 沉孔, 支承 Z23.0):
#      内圈 R34 ×8 + 外圈 67.5/112.5/247.5/292.5 ×4 → 承载盘顶面 M3×4 铜螺母 (Z28–32): M3×8 尖 Z31, 啮合 3 (M3×10 会冒出盘顶 1)
#      外圈锚孔 22.5/157.5/202.5/337.5 ×4 → 穿承载盘 + 固定件带 (Z32–37) → 带顶 M3 法兰螺母 (Z37–40.7): M3×18 尖 Z41 (吃满螺母, 冒 0.3)
#    电机 4×M3×10 内六角 从承载盘顶 Φ7×5 沉孔往下 (支承 Z27, 头顶 Z30), 穿玻纤板进电机顶 4.5
#    罩子 2 片 4×M3×8 内六角 凸台顶 Z41 往下 → 固定件带顶 M3×4 铜螺母 (Z33–37)
if B.ROTOR_B:
    import io as _io2, contextlib as _cl2
    with _cl2.redirect_stdout(_io2.StringIO()):
        import rotor_shroud_b_v1_2 as RSB
    RB = RSB.RB
    _FB = RB.Z_F0 + 1.5
    for i, (x, y) in enumerate(RB.IN_PTS):        # 11-19 16:53 内圈 8 颗: 承载盘顶 Φ8×3.7 沉孔里 M3 法兰螺母 (坐沉孔底 Z26.8), M3×7 尾 Z30.0 (低于盘顶 0.5)
        screw("M3x7 超薄头 玻纤板→承载盘 内圈", i, x, y, _FB, 7.0, True, engage=("M3 法兰螺母", RB.Z_TOP - RB.IN_NUT_H, RB.Z_TOP - RB.IN_NUT_H + NUT_T))
        add(f"M3 法兰螺母 承载盘内圈沉孔 #{i}", flange_nut(x, y, RB.Z_TOP - RB.IN_NUT_H), "#707070")
    for i, (x, y) in enumerate(RB.OUT_NUT_PTS):
        screw("M3x7 超薄头 玻纤板→承载盘 外圈", i, x, y, _FB, 7.0, True, engage=("铜螺母", RB.Z_TOP - RB.INS_H, RB.Z_TOP))
        add(f"M3x3 铜螺母 承载盘B #{i}", insert(x, y, RB.Z_TOP - RB.INS_H, RB.INS_H), "#B8860B")
    for i, (x, y) in enumerate(RB.ANCHOR_PTS):
        screw("M3x18 超薄头 玻纤板→固定件锚孔", i, x, y, _FB, 18.0, True, engage=("M3 法兰螺母", RB.H_Z1, RB.H_Z1 + NUT_T))
        add(f"M3 法兰螺母 固定件带顶 #{i}", flange_nut(x, y, RB.H_Z1), "#707070")
    for i, (x, y) in enumerate(RB.MOT_PTS):
        screw("M3x10 内六角 承载盘→电机", i, x, y, RB.Z_TOP - RB.MOT_CB_H, 10.0, False, hd=5.5, hh=3.0, engage=("电机顶螺纹", B.MOTOR_Z0, B.ROTOR_TOP))
    for i, (x, y) in enumerate(RB.SHR_LOCK_PTS):
        screw(f"M3x{RSB.MNT_L:g} 内六角 转子罩B→固定件", i, x, y, RSB.BOSS_Z1, RSB.MNT_L, False, hd=5.5, hh=3.0, engage=("铜螺母", RB.H_Z1 - RB.H_INS_H, RB.H_Z1))
        add(f"M3x4 铜螺母 固定件 罩子锁点 #{i}", insert(x, y, RB.H_Z1 - RB.H_INS_H, RB.H_INS_H), "#B8860B")

# 13 无线供电模块固定件 (11-19 两件对称夹块直方条, wireless_holder_v1_2): 4×M3×14 超薄头从承载盘底往上 (同底板: 底面 Φ7.4×1.5 让位, 头支承 Z28.8), 穿夹块立柱 Φ3.4 通孔, 立柱顶 M3 法兰螺母 (15:30 用户「螺丝应该是通孔，上边锁螺母」, 15:46「蓝色是法兰螺母」)
import wireless_holder_v1_2 as WH
for i, (x, y) in enumerate(B.MOD_HOLES):
    if B.ROTOR_B:
        screw(f"M3x{WH.SCR_L:g} 超薄头 无线夹块", i, x, y, WH.CB_Z, WH.SCR_L, True, engage=("法兰螺母", WH.TOP_Z, WH.TOP_Z + WH.NUT_H))
        add(f"M3 法兰螺母 无线夹块立柱顶 #{i}", WH.inserts[i], "#666666")
    else:
        screw("M3x8 内六角 无线托盘", i, x, y, WH.CB_Z, 8.0, False, hd=5.5, hh=3.0, engage=("铜螺母", WH.RIM_TOP - 4.0, WH.RIM_TOP))

# 14 底盘 MR30 座 + 电机线束线夹 (11-16 晚, motor_wire_v1_2): 各 2×M3 从底盘底面 Φ7×2 沉孔往上 (头支承 Z-4), 进件顶热压 M3×4 铜螺母 (顶齐件顶)
#    MR30 座 M3×12 (件顶 Z8.0) / 线夹 M3×10 (件顶 Z6.0), 尖 = 件顶, 啮合 4
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()):
    import motor_wire_v1_2 as MW
MW_SEAT, MW_CLAMP = MW.mr30_seat(), MW.wire_clamp()
for i, ((x, y), top, L_) in enumerate(zip(MW.MW_M3, MW.MW_TOP, MW.SCREW_L)):
    _nm = "MR30座" if (x, y) in MW.MR_INS else "电机线夹"
    screw(f"M3x{L_:g} {_nm}", i, x, y, MW.BEAR_Z, L_, True, engage=("铜螺母", top - MW.INS_H, top))
    add(f"铜螺母 M3x4 {_nm} #{i}", insert(x, y, top - MW.INS_H, MW.INS_H), "#B8860B")

# ---------------- 零件 ----------------
PARTS = {"灯板立板+x": L.post_a, "灯板立板-x": L.post_b, "灯板夹条": L.bar_s, "灯板顶部件": L.top, "灯板梳齿": L.comb_s, "底盘": B.disc, "线圈环": B.ring, "电机": B.motor, "控制板": B.board, "散热片": B.heatsink,
         "法兰盘": B.flange_disc, "安装法兰": B.mounting_flange, "转子毂盘": B.hub, "承载盘": B.rim,
         "玻璃下底座": B.shroud_lo, "玻璃下玻璃座": B.shroud_hi, "外卡环": B.clamp_ring, "XT60压块": B.xt_clamp, "XT60底垫": B.xt_shim,
         **({"MOS压块": B.CD.clamp} if B.CD.HAS_MC else {}), **({"电容卡件": B.CD.cap_clamp} if B.CD.HAS_CC else {}), "驱动板": B.CD.pcb, "驱动MOS": B.CD.mos, "驱动电解电容": B.CD.cap, "驱动散热片": B.CD.sink2, "按键支架": B.key_bracket, "按键板": B.key_board,
         "转子罩a": RS.shr_a, "转子罩b": RS.shr_b, "转子罩顶盖+y": RS.lid_a, "转子罩顶盖-y": RS.lid_b, "无线托盘": WH.H, "无线模块 (占位)": WH.module, "底板 r4b (板框)": L.VB['baseboard'],
         "MR30座": MW_SEAT, "电机线夹": MW_CLAMP}   # 11-16 新件; 11-16 晚 中间 T 件取消, +MR30 座 / 线夹
if B.ROTOR_B:   # 11-18 转子盘B
    for _k in ("灯板立板+x", "灯板立板-x", "转子毂盘", "承载盘", "转子罩a", "转子罩b", "转子罩顶盖+y", "转子罩顶盖-y"): PARTS.pop(_k)
    PARTS.update({"玻纤板": RB.fr4, "承载盘B": RB.rim, "屏幕固定件+x": RB.hold_a, "屏幕固定件-x": RB.hold_b, "转子罩B+y": RSB.shr_a, "转子罩B-y": RSB.shr_b})
for i, p in enumerate(B.posts):
    PARTS[f"立柱{i}"] = p
PB = {k: bbox(v) for k, v in PARTS.items()}
PSOL = {k: [(s, bbox(s)) for s in solids(v)] or [(v, PB[k])] for k, v in PARTS.items()}


def bb_hit(a, b, m=0.0):
    return not (a[3] < b[0] - m or b[3] < a[0] - m or a[4] < b[1] - m or b[4] < a[1] - m or a[5] < b[2] - m or b[5] < a[2] - m)


def common_vol(sh, pn):
    sb = bbox(sh); v = 0.0
    if not bb_hit(sb, PB[pn]):
        return 0.0
    for s, b in PSOL[pn]:
        if bb_hit(sb, b):
            v += vol(op(BRepAlgoAPI_Common, sh, s))
    return v


def common_bbox(sh, pn):
    sb = bbox(sh); bs = []
    for s, b in PSOL[pn]:
        if bb_hit(sb, b):
            c = op(BRepAlgoAPI_Common, sh, s)
            if vol(c) > 1e-6:
                bs.append(bbox(c))
    return bs


# ---- 干涉: 每个紧固件 vs 每个零件 ----
rows = []
for n, sh, c in F:
    for pn in PARTS:
        v = common_vol(sh, pn)
        if v > 0.01:
            rows.append((n, pn, v))
print("== 紧固件 ↔ 零件 共用体积 (>0.01 mm3) ==")
for n, pn, v in rows:
    print(f"  {n:24s} ↔ {pn:8s} {v:8.3f} mm3")


# ---- 每处: 支承面 / 尾端 / 啮合 / 尾端前方最近件 / 头外侧最近件 ----
def probe(x, y, d, z, up, span=60.0):
    """从 z 沿轴 (up=+Z) 打一根 Φd 柱, 返回 (距离, 件名); 无则 (None, None)。"""
    col = cyl(x, y, d, z + 1e-3, z + span) if up else cyl(x, y, d, z - span, z - 1e-3)
    best = (None, None)
    for pn in PARTS:
        for b in common_bbox(col, pn):
            dist = (b[2] - z) if up else (z - b[5])
            if best[0] is None or dist < best[0]:
                best = (dist, pn)
    return best


T = []
print("== 每处螺丝 ==")
for s in S:
    x, y, up, bear, L, tip, d = s['x'], s['y'], s['up'], s['bear'], s['L'], s['tip'], s['d']
    en, z0, z1 = s['engage']
    if z1 is None:                                             # 电机: 进螺纹深度 = 尾端 - 电机底面
        eng = tip - z0
    else:
        lo, hi = (bear, tip) if up else (tip, bear)
        eng = max(0.0, min(hi, z1) - max(lo, z0))
    tdist, tpart = probe(x, y, d, tip, up)
    head_out = bear - s['hh'] if up else bear + s['hh']
    hdist, hpart = probe(x, y, (s['hd'] or (M6_HEAD_D if d > 3 else M3_HEAD_D)) - 0.2, head_out, not up)   # 11-16: 有 hd 用实际头径 (M4 超薄头 8.5)
    row = dict(组=s['group'], 号=s['i'], x=round(x, 2), y=round(y, 2), r=round(math.hypot(x, y), 2), 方向="↑" if up else "↓",
               支承面Z=round(bear, 2), 尾端Z=round(tip, 2), 啮合=en, 啮合长=round(eng, 2),
               尾端前方=tpart, 尾端距离=None if tdist is None else round(tdist, 2),
               头外侧=hpart, 头外侧距离=None if hdist is None else round(hdist, 2), 头外侧Z=round(head_out, 2))
    T.append(row)
    print("  " + "  ".join(f"{k}={v}" for k, v in row.items()))
for row in KEY_ROWS:                                               # 按键板横向螺丝 (沿 −Y), 不走 Z 向 probe
    T.append(row); print("  " + "  ".join(f"{k}={v}" for k, v in row.items()))
for row in SEAM_ROWS:                                              # 转子罩分缝切向螺丝 (沿 ±X): 沿 x 打探针
    y, z, hx, hs, tx, ts = row.pop('_probe')
    hdist, hpart = probe_x(y, z, 5.5 - 0.2, hx, hs)
    tdist, tpart = probe_x(y, z, 3.0, tx, ts)
    row.update(尾端前方=tpart, 尾端距离=None if tdist is None else round(tdist, 2), 头外侧=hpart, 头外侧距离=None if hdist is None else round(hdist, 2), 头外侧x=round(hx, 2))
    T.append(row); print("  " + "  ".join(f"{k}={v}" for k, v in row.items()))

# 线圈环角法兰螺母 vs Φ77 圆台 (解析)
ring_r = math.hypot(*B.RING_M3[0])
ana = dict(角孔心r=round(ring_r, 3), 法兰外缘内侧r=round(ring_r - NUT_FL_D / 2, 3), 六角外接内侧r=round(ring_r - NUT_AF / math.sqrt(3), 3),
           六角对边内侧r=round(ring_r - NUT_AF / 2, 3), 圆台r=B.COLLAR_D / 2,
           需孔心r_法兰=round(B.COLLAR_D / 2 + NUT_FL_D / 2, 3), 需RING_M3_XY=round((B.COLLAR_D / 2 + NUT_FL_D / 2) / math.sqrt(2), 3))
print("== 线圈环角螺母 vs Φ77 圆台 ==", ana)
sh_r = math.hypot(*B.SH_M6[0])
ana2 = dict(下罩孔心r=round(sh_r, 3), 法兰外缘r=round(sh_r + NUT_FL_D / 2, 3), 墙内面r=B.SPIG_IN, 法兰内缘r=round(sh_r - NUT_FL_D / 2, 3),
            外裙=(82.5, 85.0), 螺母顶Z=B.TRI_T + NUT_T, 外裙底Z=B.FL_Z0)
print("== 下罩螺母 ==", ana2)

(B.OUT).mkdir(exist_ok=True)
json.dump(dict(interf=[dict(件=n, 零件=pn, 体积=round(v, 3)) for n, pn, v in rows], screws=T, ring=ana, shroud=ana2),
          open(B.OUT / 'fasteners_v1_2.json', 'w'), ensure_ascii=False, indent=1)


# ---------------- 3MF (mesh / write3mf 拷自 export_3mf_v1_2.py, 不 import 它) ----------------
def mesh(shape, defl):
    BRepMesh_IncrementalMesh(shape, defl, False, 0.3, True)
    V = []; Tr = []; n = 0; e = TopExp_Explorer(shape, TopAbs_FACE)
    while e.More():
        f = TopoDS.Face(e.Current()); L = TopLoc_Location(); tr = BRep_Tool.Triangulation_s(f, L)
        if tr is not None:
            t = L.Transformation(); k = tr.NbNodes()
            V.append(np.array([[p.X(), p.Y(), p.Z()] for p in (tr.Node(i).Transformed(t) for i in range(1, k + 1))]))
            tt = np.array([[tr.Triangle(i).Value(j) for j in (1, 2, 3)] for i in range(1, tr.NbTriangles() + 1)]) - 1
            if f.Orientation() == TopAbs_REVERSED: tt = tt[:, [0, 2, 1]]
            Tr.append(tt + n); n += k
        e.Next()
    return np.vstack(V), np.vstack(Tr)


def write3mf(path, parts):
    mats = ''.join(f'<base name="{n}" displaycolor="{c}FF"/>' for n, _, c, _ in parts)
    objs = []; items = []
    for i, (n, s, c, defl) in enumerate(parts):
        V, Tr = mesh(s, defl)
        vs = '\n'.join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in V)
        ts = '\n'.join(f'<triangle v1="{a}" v2="{b}" v3="{c_}"/>' for a, b, c_ in Tr)
        objs.append(f'<object id="{i + 2}" name="{n}" type="model" pid="1" pindex="{i}"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i + 2}"/>'); print(n, len(V), len(Tr), flush=True)
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><basematerials id="1">{mats}</basematerials>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', model)


# 控制板: 3MF 里去掉 < 1 mm 小件 (同 export 脚本), 干涉检查用全板
import led_support_v1_2 as LS                       # 上面螺丝循环里 L 被当作长度变量覆盖, 这里重新取模块
BOARD_LITE = comp([s for s in solids(B.board) if (lambda b: max(b[3] - b[0], b[4] - b[1]) >= 1.2 or b[5] - b[2] >= 1.0)(bbox(s))])
grp = {}
for n, sh, c in F:
    grp.setdefault((n.split(" #")[0], c), []).append(sh)
FAST = [(k, comp(v), c, 0.05) for (k, c), v in grp.items()]
P_ = [('打印底盘 Φ220×4.5', B.disc_print, '#8A8F98', 0.05), ('玻纤板 FR4 Φ220×3', B.fr4, '#C8D86A', 0.05), ('线圈环', B.ring, '#E0A030', 0.05), ('电机 Φ55×21.5 (占位)', B.motor, '#333333', 0.05),
      ('电机控制板', BOARD_LITE, '#2E7D32', 0.08), ('散热片 40×20×6', B.heatsink, '#C0392B', 0.05),
      ('法兰盘 flange_disc_v1_2', B.flange_disc, '#D9A441', 0.05), ('安装法兰 mounting_flange_v1_2', B.mounting_flange, '#B5895A', 0.05),
      ('转子毂盘 hub_disc_v1_2', B.hub, '#4F86C6', 0.05), (f'承载盘 rim_ring Φ{B.RIM_D:g}', B.rim, '#6AA84F', 0.05),
      ('玻璃下-底座 glass_shroud_lower_v1_2', B.shroud_lo, '#7FB3D5', 0.05), ('玻璃下-玻璃座 glass_shroud_upper_v1_2', B.shroud_hi, '#5DADE2', 0.05), ('外卡环 glass_clamp_ring_v1_2', B.clamp_ring, '#2E86C1', 0.05), ('XT60 压块', B.xt_clamp, '#F1C232', 0.05), ('XT60 底垫', B.xt_shim, '#E69138', 0.05),
      *([('MOS 压块 mos_clamp_v1_2', B.CD.clamp, '#E69138', 0.05)] if B.CD.HAS_MC else []), *([('电容卡件 cap_clamp_v1_2', B.CD.cap_clamp, '#B45F06', 0.05)] if B.CD.HAS_CC else []), ('线圈驱动板 (元件级)', B.CD.pcb, '#38761D', 0.05), ('线圈驱动 MOS', B.CD.mos, '#222222', 0.05),
      ('线圈驱动 电解电容', B.CD.cap, '#1155CC', 0.05), ('线圈驱动 散热片', B.CD.sink2, '#C0392B', 0.05),
      ('按键支架 key_bracket_v1_2', B.key_bracket, '#F1C232', 0.03), ('按键板 (简模)', B.key_board, '#2E7D32', 0.03),
      ('灯板支撑 +x led_post_a', LS.post_a, '#F1C232', 0.03), ('灯板支撑 -x led_post_b', LS.post_b, '#E69138', 0.03), ('灯板夹条 led_bar', LS.bar_s, '#8E7CC3', 0.03),
      ('灯板顶部件 led_top', LS.top, '#6FA8DC', 0.03), ('灯板梳齿 led_comb', LS.comb_s, '#9FC5E8', 0.03),
      ('转子罩 a rotor_shroud_a_v1_2', RS.shr_a, '#6FA8DC', 0.05), ('转子罩 b rotor_shroud_b_v1_2', RS.shr_b, '#93C47D', 0.05), ('转子罩顶盖 +y rotor_lid_v1_2', RS.lid_a, '#CFE2F3', 0.05), ('转子罩顶盖 −y rotor_lid_b_v1_2', RS.lid_b, '#A4C2F4', 0.05),
      ('无线托盘 wireless_holder_v1_2', WH.H, '#F1C232', 0.03), ('无线供电模块 30.5×49×15 (占位)', WH.module, '#3D85C6', 0.05),
      ('MR30 座 mr30_seat_v1_2', MW_SEAT, '#F1C232', 0.03), ('电机线束线夹 motor_wire_clamp_v1_2', MW_CLAMP, '#E69138', 0.03)]
if B.ROTOR_B:   # 11-18 转子盘B
    _drop = ('转子毂盘', '承载盘 rim_ring', '灯板支撑', '转子罩')
    P_ = [p for p in P_ if not p[0].startswith(_drop)] + [('玻纤板 fr4_plate_v1_2b', RB.fr4, '#C9B458', 0.05), ('承载盘 rim_ring_v1_2b', RB.rim, '#6AA84F', 0.05),
          ('屏幕固定件 +x screen_holder_v1_2b_a', RB.hold_a, '#F1C232', 0.03), ('屏幕固定件 −x screen_holder_v1_2b_b', RB.hold_b, '#E69138', 0.03),
          ('转子罩 +y 半 rotor_shroud_b_a_v1_2b', RSB.shr_a, '#6FA8DC', 0.05), ('转子罩 −y 半 rotor_shroud_b_b_v1_2b', RSB.shr_b, '#93C47D', 0.05)]
out = f"{B.V12 / 'assembly_v1_2'}_整机+螺丝.3mf"
write3mf(out, P_ + FAST)
print("wrote", out)
