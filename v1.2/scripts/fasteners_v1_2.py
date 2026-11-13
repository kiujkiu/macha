"""V1.2 紧固件装配预览 (2026-11-12 晚, 按用户实物参数): 按 build_v1_2 的孔位/高度放螺丝、螺母、铜螺母, 出 3MF + 干涉/啮合表。
    cd v1.2/scripts && ../../.venv/bin/python fasteners_v1_2.py
只 import build_v1_2 (不 import export_3mf_v1_2, 不写 models/); 输出:
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
M3_HEAD_D, M3_HEAD_H = 7.0, 1.5
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
                  hh=kw.get('hh', M3_HEAD_H), engage=engage, shape=sh))


# 1 电机 4×M3 盘底沉孔往上, 拧电机底面螺纹 (螺纹深度待电机规格书)
L_MOTOR = 8.0
for i, (x, y) in enumerate(B.MOTOR_HOLES):
    screw("M3x8 电机", i, x, y, CB_BEAR, L_MOTOR, True, engage=("电机底螺纹", B.MOTOR_Z0, None))
# 2 线圈环四角 4×M3 盘底往上 + 法兰螺母压四角顶 (11-12 夜: 角厚 4.5 ⇒ Z4.5..8.2); 尾端 Z8.0 < 法兰盘底 Z8.5
L_RING = 12.0
for i, (x, y) in enumerate(B.RING_M3):
    screw("M3x12 线圈环角", i, x, y, CB_BEAR, L_RING, True, engage=("法兰螺母", B.RING_CORNER_T, B.RING_CORNER_T + NUT_T))
    add(f"M3 法兰螺母 线圈环角 #{i}", flange_nut(x, y, B.RING_CORNER_T), "#707070")
# 3 下罩三角块 4×M3 盘底往上 + 法兰螺母压三角块顶 (Z5..8.7)
L_SH = 14.0
for i, (x, y) in enumerate(B.SH_M6):
    screw("M3x14 下罩", i, x, y, CB_BEAR, L_SH, True, engage=("法兰螺母", B.TRI_T, B.TRI_T + NUT_T))
    add(f"M3 法兰螺母 下罩 #{i}", flange_nut(x, y, B.TRI_T), "#707070")
# 4 中央 8×M3 安装法兰顶沉孔往下, 拧底盘底面铜螺母 (M3×4 齐底面 Z-6..-2)
L_C = 20.0
for i, (x, y) in enumerate(B.FLANGE_SCREWS):
    screw("M3x20 中央", i, x, y, MF_BEAR, L_C, False, engage=("铜螺母", ZB, ZB + INS_L_DISC))
    add(f"铜螺母 M3x4 底盘 G #{i}", insert(x, y, ZB, INS_L_DISC), "#B8860B")
# 5 外圈 8×M3 安装法兰顶沉孔往下, 拧法兰盘底面铜螺母 (11-12 夜: M3×4 齐法兰盘底 Z8.5..12.5); M3×6 尾端 Z8.5 齐底面, 啮合 4
L_LID = 6.0
for i, (x, y) in enumerate(B.LID_SCREWS):
    screw("M3x6 上下盖", i, x, y, MF_BEAR, L_LID, False, engage=("铜螺母", B.FL_Z0, B.FL_Z0 + INS_L_FL))
    add(f"铜螺母 M3x4 法兰盘 B #{i}", insert(x, y, B.FL_Z0, INS_L_FL), "#B8860B")
# 6 控制板 4×M3 (用户 11-13): 盘底 Φ7×2 沉孔往上, 穿底盘 + 板, M3 法兰螺母坐板顶 (原板顶往下进底盘 H 铜螺母)
L_BD = 10.0                                        # 支承 Z-4, 尖 Z6; 螺母 Z1.6..5.3 ⇒ 吃满 3.7, 露 0.7
for i, (bx, by) in enumerate(B.BHOLES):
    p = gp_Pnt(bx, by, 0).Transformed(B.BT)
    screw("M3x10 控制板", i, p.X(), p.Y(), CB_BEAR, L_BD, True, engage=("法兰螺母", BOARD_TOP, BOARD_TOP + NUT_T))
    add(f"M3 法兰螺母 控制板 #{i}", flange_nut(p.X(), p.Y(), BOARD_TOP), "#707070")
# 7 XT60 2×M3 (用户 11-12 晚, 原 M6×20 + M6 螺母): 盘底 Φ7×2 沉孔往上, 穿底盘+底垫+压块 (叠高 13),
#   11-12 晚 (二): 压块顶螺母座取消, M3 法兰螺母直接坐压块顶 Z13..16.7, 尖 Z16 ⇒ 啮合 3.0; 下罩 Φ8.2 井到 Z17.5
L_XT = 20.0
XT_NUT_Z0 = B.XT_H                                 # 13 (螺母座取消, 原 XT_H - XT_NUT_SEAT_H = 12)
for i, (x, y) in enumerate(B.XT_GHOLES_DISC):
    screw("M3x20 XT60", i, x, y, CB_BEAR, L_XT, True, engage=("法兰螺母", XT_NUT_Z0, XT_NUT_Z0 + NUT_T))
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

# 9 按键支架 (用户 11-13, scripts/key_bracket_v1_2.py): 支架脚 2×M3 盘底 Φ7×2 沉孔往上 → 支架脚底面压入的 M3×4 铜螺母 (Z0..4);
#   M3×8 支承 Z-4 尖 Z4 ⇒ 进铜螺母 4.0 (吃满, 尖低于孔顶 0.2)
_K = B.KEY
_ki0, _ki1 = _K['insert_z']
for i, (x, y) in enumerate(_K['disc_m3']):
    screw(f"M3x{_K['foot_screw_L']:g} 按键支架", i, x, y, CB_BEAR, _K['foot_screw_L'], True, engage=("铜螺母", _ki0, _ki1))
    add(f"铜螺母 M3x4 按键支架 #{i}", insert(x, y, _ki0, _ki1 - _ki0), "#B8860B")
# 10 按键板 2×M3 (沿 −Y): 超薄头坐立柱前面 (y103.6), 穿立柱 3 + 板 1.6, 板背面 (y99) 上 M3 法兰螺母 (y99→95.3); 尖 y95.6 ⇒ 啮合 3.4
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

# ---------------- 零件 ----------------
PARTS = {"底盘": B.disc, "线圈环": B.ring, "电机": B.motor, "控制板": B.board, "散热片": B.heatsink,
         "法兰盘": B.flange_disc, "安装法兰": B.mounting_flange, "转子毂盘": B.hub, "承载盘": B.rim,
         "下罩": B.seat, "XT60压块": B.xt_clamp, "XT60底垫": B.xt_shim,
         **({"MOS压块": B.CD.clamp} if B.CD.HAS_MC else {}), **({"电容卡件": B.CD.cap_clamp} if B.CD.HAS_CC else {}), "驱动板": B.CD.pcb, "驱动MOS": B.CD.mos, "驱动电解电容": B.CD.cap, "驱动散热片": B.CD.sink2, "按键支架": B.key_bracket, "按键板": B.key_board}
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
    hdist, hpart = probe(x, y, (M6_HEAD_D if d > 3 else M3_HEAD_D) - 0.2, head_out, not up)
    row = dict(组=s['group'], 号=s['i'], x=round(x, 2), y=round(y, 2), r=round(math.hypot(x, y), 2), 方向="↑" if up else "↓",
               支承面Z=round(bear, 2), 尾端Z=round(tip, 2), 啮合=en, 啮合长=round(eng, 2),
               尾端前方=tpart, 尾端距离=None if tdist is None else round(tdist, 2),
               头外侧=hpart, 头外侧距离=None if hdist is None else round(hdist, 2), 头外侧Z=round(head_out, 2))
    T.append(row)
    print("  " + "  ".join(f"{k}={v}" for k, v in row.items()))
for row in KEY_ROWS:                                               # 按键板横向螺丝 (沿 −Y), 不走 Z 向 probe
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
BOARD_LITE = comp([s for s in solids(B.board) if (lambda b: max(b[3] - b[0], b[4] - b[1]) >= 1.2 or b[5] - b[2] >= 1.0)(bbox(s))])
grp = {}
for n, sh, c in F:
    grp.setdefault((n.split(" #")[0], c), []).append(sh)
FAST = [(k, comp(v), c, 0.05) for (k, c), v in grp.items()]
P_ = [('底盘 Φ220×6', B.disc, '#8A8F98', 0.05), ('线圈环', B.ring, '#E0A030', 0.05), ('电机 Φ55×21.5 (占位)', B.motor, '#333333', 0.05),
      ('电机控制板', BOARD_LITE, '#2E7D32', 0.08), ('散热片 40×20×6', B.heatsink, '#C0392B', 0.05),
      ('法兰盘 flange_disc_v1_2', B.flange_disc, '#D9A441', 0.05), ('安装法兰 mounting_flange_v1_2', B.mounting_flange, '#B5895A', 0.05),
      ('转子毂盘 hub_disc_v1_2', B.hub, '#4F86C6', 0.05), ('承载盘 rim_ring Φ178', B.rim, '#6AA84F', 0.05),
      ('下罩 (合并) glass_shroud_v1_2', B.seat, '#7FB3D5', 0.05), ('XT60 压块', B.xt_clamp, '#F1C232', 0.05), ('XT60 底垫', B.xt_shim, '#E69138', 0.05),
      *([('MOS 压块 mos_clamp_v1_2', B.CD.clamp, '#E69138', 0.05)] if B.CD.HAS_MC else []), *([('电容卡件 cap_clamp_v1_2', B.CD.cap_clamp, '#B45F06', 0.05)] if B.CD.HAS_CC else []), ('线圈驱动板 (元件级)', B.CD.pcb, '#38761D', 0.05), ('线圈驱动 MOS', B.CD.mos, '#222222', 0.05),
      ('线圈驱动 电解电容', B.CD.cap, '#1155CC', 0.05), ('线圈驱动 散热片', B.CD.sink2, '#C0392B', 0.05),
      ('按键支架 key_bracket_v1_2', B.key_bracket, '#F1C232', 0.03), ('按键板 (简模)', B.key_board, '#2E7D32', 0.03)]
out = f"{B.V12 / 'assembly_v1_2'}_整机+螺丝.3mf"
write3mf(out, P_ + FAST)
print("wrote", out)
