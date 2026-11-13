"""
TO-220 MOS 压块 mos_clamp_v1_2 —— 独立生成器 (POV3D V1.2, 2026-11-12 夜)
    cd v1.2/scripts && ../../.venv/bin/python mos_clamp_v1_2.py
输出 v1.2/models/mos_clamp_v1_2/mos_clamp_v1_2.stl/.step (打印姿态) + v1.2/out/mos_clamp_v1_2_preview.png
不 import build_v1_2, 工具函数自带 (同 cap_clamp_v1_2)。build_v1_2 / coil_drv_geom 合并时调 make_mos_clamp(p), p 给装配系参数。

mos-b (用户 11-12 夜「cap和mos的件，m3做通孔加M4.2沉孔」「压铜螺母深度4mm」→ 孔深统一 4.2, NUT_MODE='insert' 缺省):
  不再用法兰螺母 + 螺母井: M3 Φ3.4 通孔贯通 + 件顶面往下 Φ4.2 盲孔深 4.2 (比铜螺母长 0.2), 压入/热熔 M3×4 铜螺母 (外径 4.2, 同底盘 G/H), 铜螺母顶齐件顶;
  M3 从底盘底面 Φ7×2 沉孔往上 (头支承 Z−4) 穿底盘 + 件, 拧进铜螺母。件顶 = max(槽高 4.45 + 1.5, 尖) 取最低 ⇒ M3×10 尖 Z6.0 = 件顶 6.0,
  进铜螺母 4.0 (全长); 孔 Φ4.2 到槽壁 ≥ 1.0。打印仍顶面贴床 (孔口在床面, 铜螺母从顶面压); 唯一朝下面 = 孔底 Φ4.2→Φ3.4 环 (宽 0.4)。
  NUT_MODE='flange' 回到下面 mos-a 的法兰螺母井。以下为 mos-a 原说明:
来历: 旧件 models/mos_clamp_16x10x4p5 (平顶压块, 底部盲槽, +Y 挡板 2 顶背板尖, 引脚从开口端出, 过盈 0)。
V1.2 版 (用户 11-12 夜, 同电容卡件 V1.2-cap-b 样式):
  - 实心长方体 Z0..TOP, 平顶; 底面盲槽宽 E + 2×0.2 = 10.5, 槽高 = A 4.45 (塑封体顶面零过盈接触);
    背板露出段 (A1 1.3 厚) 上方同槽高留空 (不压, 只压塑封体); 挡板 2 厚封槽的背板端, 内面顶背板尖; 引脚端开口。
  - MOS 背板朝下平贴散热片 (散热片嵌底盘通槽, 顶齐 Z0); MOS 中心线相对板中轴偏 MOS_DX (+2.95)。
  - 外形 + 2×M3 以板中轴 XPC 对称 ⇒ 槽在压块里偏心; 孔在竖放散热片 (XPC±SINK_W/2) 之外, 底面 Φ7×2 沉孔离散热片槽 ≥ MIN_WALL。
  - 孔 Φ3.4 通; 顶面往下螺母井 (同电容卡件 cap-c): 法兰螺母法兰朝上倒放, 下段六角 AF6.1 高 2.5 (六角端面坐井底, 防转),
    上段 Φ8.2 容法兰; 井底 = 螺母底; Φ3.4 孔井底端留 0.2 牺牲层 (倒打时井底变井顶, 成整片桥; 装配前用螺丝捅穿)。
  - 井到槽壁 ≥ WELL_WALL 1.0, 到外形各端面 ≥ OUT_WALL 1.2 (不够自动对称外拉孔距 / 外形)。
Z 链 (缺省): 头支承面 −DISC_T + M3_CB_H = −4; 螺丝从 SCREW_LENS 取 尖 ≤ Z_LIMIT 且能让螺母吃满的最短者 ⇒ M3×12 尖 8.0;
  件顶 TOP = max(槽高 + T_TOP_MIN 1.5, 井底 EAR_MIN 2.5 + 螺母 3.7) = 6.2 (螺母顶 = 法兰顶齐件顶, 全在井里);
  螺母 2.5..6.2 吃满 3.7, 螺尖露出件顶 1.8 (Z8.0 ≤ Z_LIMIT 9.0)。
打印姿态 (导出文件): 绕 X 翻 180°, 顶面贴床, 槽口朝上。朝下面只有每个井的两级井顶 (都是平面桥, 切片开桥接):
  ① Φ8.2 → 六角台阶 (环, 离床 1.2, 跨 ≤8.2); ② 井底 = 六角整片 (牺牲层封住 Φ3.4, 跨 6.1~7.0, 离床 3.7)。
  槽 / 挡板 / 通孔都是竖壁或朝上面, 无需支撑。
坐标: 装配系 (全局 X/Y, Z0 = 底盘顶 = 散热片顶 = MOS 背板底)。MOS_DIR +1: 背板 (尖) 朝 +Y, 引脚朝 −Y。
"""
import math
from pathlib import Path

from OCP.gp import gp_Ax1, gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf, gp_Pln
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common, BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_EDGE, TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.Interface import Interface_Static
from OCP.IFSelect import IFSelect_RetDone

VERSION = "V1.2-mos-b"
HERE = Path(__file__).resolve().parent
V12 = HERE.parent
MODEL_DIR = V12 / 'models' / 'mos_clamp_v1_2'
OUT = V12 / 'out'

# ======================== 缺省参数 (装配系, mm) ========================
DEFAULTS = dict(
    # 位置
    XPC=55.05,           # 板中轴 x (coil_drv_geom.XPC); 压块外形 / 2 孔以它对称
    MOS_DX=2.95,         # MOS 中心线相对板中轴的 x 偏移 ⇒ MOS 中心 x = XPC + MOS_DX
    MOS_Y_TIP=20.0,      # 背板尖 y
    MOS_DIR=+1,          # +1: 背板 (尖) 朝 +Y / 引脚朝 −Y; −1 反之
    Z0=0.0,              # MOS 背板底 = 散热片顶 = 底盘顶 (本件只支持 0)
    # 散热片 (竖放, 嵌底盘通槽, 槽 = 散热片外形)
    SINK_W=20.0,         # 沿 X, 按 XPC 居中
    SINK_Y0=-8.15, SINK_Y1=31.85,
    # MOS TO-220 (规格书名义值)
    MOS_A=4.45, MOS_A1=1.3, MOS_E=10.1, MOS_D=15.15, MOS_H1=6.5,
    MOS_P=3.6, MOS_Q=2.8,                 # 背板孔 Φ / 孔心离背板尖
    LEAD_Z=2.7, LEAD_W=0.8, LEAD_T=0.5, LEAD_P=2.54, LEAD_L=4.0,   # 引脚中心离背板底 / b / c / e / 露出短段
    # 压块
    CLR_SIDE=0.2,        # 槽宽单边间隙 ⇒ 10.5
    PRELOAD=0.0,         # 槽高 = A − PRELOAD (零过盈)
    T_TOP_MIN=1.5,       # 槽顶最小厚
    BAFFLE_T=2.0,        # 挡板厚 (内面顶背板尖)
    OPEN_CLR=0.5,        # 开口端面越过塑封体根 (向引脚方向)
    EAR_MIN=2.5,         # 井底 (螺母底) 最低高度 = 螺母下方实体厚
    WELL_D=8.2,          # 螺母井 Φ (法兰 Φ7.6 + 0.6)
    # 螺母防转 (照 cap_clamp_v1_2 cap-c): 法兰螺母**法兰朝上倒放** —— 井下段 (井底 = 螺母底起) 六角 AF6.1 高 NUT_T − WELL_FL_H = 2.5,
    #   六角端面坐井底; 上段 Φ8.2 容法兰。(法兰 Φ7.6 > 六角外接圆 7.04, 正放从顶面放不进。) False ⇒ 全圆 Φ8.2 井, 法兰朝下坐井底。
    NUT_HEX_WELL=True, WELL_AF=6.1, WELL_FL_H=1.2,
    # 牺牲层: 倒打时井底变悬空井顶 ⇒ Φ3.4 孔的井底端留 SAC_LAYER 封口, 装配前 M3 捅穿。0 ⇒ 关。
    #   r['clamp'] = 捅穿后 (装配/校核); r['clamp_sac'] 带牺牲层; clamp_print / 导出 STL·STEP 带牺牲层。
    SAC_LAYER=0.2,
    WELL_WALL=1.0,       # 螺母井 ↔ 槽 最小壁; 不够就对称外拉孔距 (0.25 一档)
    OUT_WALL=1.2,        # 螺母井 ↔ 外形各端面 最小壁
    HOLE_D=3.4,          # 件上 M3 通孔
    # mos-b (用户 11-12 夜「cap和mos的件，m3做通孔加M4.2沉孔」「压铜螺母深度4mm」→ 孔深统一 4.2): 'insert' = 铜螺母 (压入/热熔) M3×4 外径 4.2,
    #   件顶面往下 Φ4.2 盲孔深 INSERT_L + INSERT_CLR = 4.2 (铜螺母顶齐件顶), Φ3.4 通孔照旧贯通; 无螺母井 / 六角 / 牺牲层。
    #   'flange' = 旧 mos-a 法兰螺母倒放螺母井 (上面 EAR_MIN / WELL_* / NUT_HEX_WELL / SAC_LAYER 只在 flange 用)。
    NUT_MODE='insert',
    INSERT_D=4.2, INSERT_L=4.0, INSERT_CLR=0.2,   # 孔深 = INSERT_L + INSERT_CLR = 4.2 (用户: 铜螺母 M3×4 孔深统一 4.2)
    INSERT_ENGAGE_MIN=3.0,                        # 螺丝进铜螺母最少长度
    INSERT_WALL=1.0,                              # Φ4.2 孔 ↔ 槽 最小壁
    # 底盘 / 限高
    DISC_T=6.0, Z_LIMIT=8.0,   # 用户 11-12 夜: 法兰盘底 9.5 → 8.5 ⇒ Z_LIMIT = FL_Z0 − 0.5 = 8.0 (整机由 coil_drv_geom 按 B.FL_Z0 传)
    STATOR_Z0=8.5,       # 定子盘 (法兰盘) 底, 只用于预览画线 (用户 11-12 夜 9.5 → 8.5); 整机由 coil_drv_geom 按 B.FL_Z0 传
    # 紧固件 (同 fasteners_v1_2)
    M3_D=3.2, M3_CB_D=7.0, M3_CB_H=2.0,
    SCREW_LENS=(8.0, 10.0, 12.0, 14.0, 20.0),     # 10 = mos-b 新增采购 (BOM 原有 8/12/14/20)
    HEAD_D=7.0, HEAD_H=1.5, SHANK_D=3.0,
    NUT_FL_D=7.6, NUT_FL_H=1.0, NUT_AF=5.9, NUT_T=3.7,
    KEEPOUT=[],          # [(x, y, r)] 底盘已有孔/沉孔; 要求 Φ7 沉孔与之壁 ≥ KEEPOUT_WALL
    KEEPOUT_WALL=1.0,
    MIN_WALL=1.0,        # Φ7 沉孔 ↔ 散热片槽 最小壁
)

EPS_V = 1e-6


# ======================== 最小 OCP 工具 ========================
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


def common(a, b): return op(BRepAlgoAPI_Common, a, b)


def clean(s):
    u = ShapeUpgrade_UnifySameDomain(s, True, True, True); u.Build(); return u.Shape()


def xf(s, t): return BRepBuilderAPI_Transform(s, t, True).Shape()


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)),
                               gp_Pnt(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()


def cyl(x, y, d, z0, z1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), d / 2, z1 - z0).Shape()


def ycyl(x, z, d, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), d / 2, y1 - y0).Shape()


def hexprism(x, y, af, z0, z1):
    rc = af / math.sqrt(3); pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.radians(30 + 60 * k); pg.Add(gp_Pnt(x + rc * math.cos(a), y + rc * math.sin(a), z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()


def bbox(sh):
    b = Bnd_Box(); BRepBndLib.Add_s(sh, b, False); p, q = b.CornerMin(), b.CornerMax()
    return (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())


def nsolids(sh):
    ex = TopExp_Explorer(sh, TopAbs_SOLID); n = 0
    while ex.More(): n += 1; ex.Next()
    return n


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a, b); d.Perform(); assert d.IsDone(); return d.Value()


def iv(a, b): return vol(common(a, b))


def overhangs(sh, cos_lim=-0.7071):
    """打印姿态下的悬空面: 面上采样点法向 z < cos_lim (陡于 45°) 且不在床面 z=0。返回 [(面类型, 面积, z)]"""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.TopAbs import TopAbs_REVERSED
    out = []
    ex = TopExp_Explorer(sh, TopAbs_FACE)
    while ex.More():
        fc = TopoDS.Face(ex.Current()); ad = BRepAdaptor_Surface(fc)
        u0, u1, v0, v1 = ad.FirstUParameter(), ad.LastUParameter(), ad.FirstVParameter(), ad.LastVParameter()
        bad = False; zs = []
        for i in range(5):
            for j in range(5):
                u = u0 + (u1 - u0) * (i + 0.5) / 5; v = v0 + (v1 - v0) * (j + 0.5) / 5
                pr = BRepLProp_SLProps(ad, u, v, 1, 1e-6)
                if not pr.IsNormalDefined(): continue
                n = pr.Normal(); nz = -n.Z() if fc.Orientation() == TopAbs_REVERSED else n.Z()
                zs.append(pr.Value().Z())
                if nz < cos_lim: bad = True
        if bad and zs and max(zs) > 1e-4:
            g = GProp_GProps(); BRepGProp.SurfaceProperties_s(fc, g)
            out.append((str(ad.GetType()).split('_')[-1], round(g.Mass(), 2), round(sum(zs) / len(zs), 2)))
        ex.Next()
    return out


# ======================== 主函数 ========================
def make_mos_clamp(p=None):
    """p: dict 或带属性的对象 (只取 DEFAULTS 里有的键)。返回 dict, 全部装配系。"""
    P = dict(DEFAULTS)
    if p is not None:
        src = p if isinstance(p, dict) else vars(p)
        P.update({k: src[k] for k in DEFAULTS if k in src})
    assert abs(P['Z0']) < 1e-9, '本生成器按 Z0 = 0 (底盘顶) 建'
    s = 1 if P['MOS_DIR'] >= 0 else -1
    XPC = P['XPC']; XB = XPC + P['MOS_DX']
    ZL, DT = P['Z_LIMIT'], P['DISC_T']
    BEAR_Z = -DT + P['M3_CB_H']
    E, A, A1, D, H1 = P['MOS_E'], P['MOS_A'], P['MOS_A1'], P['MOS_D'], P['MOS_H1']
    Y_TIP = P['MOS_Y_TIP']; Y_ROOT = Y_TIP - s * D; Y_BODY = Y_ROOT + s * (D - H1)   # 塑封体全高段 根..Y_BODY

    # ---- 槽 / 高度 ----
    CH_W = E + 2 * P['CLR_SIDE']
    CH_H = A - P['PRELOAD']
    # 螺丝: 尖 ≤ Z_LIMIT, 螺母底 ≥ EAR_MIN 且吃满 (螺母顶 ≤ 尖); 取最短
    INS = P['NUT_MODE'] == 'insert'
    assert P['NUT_MODE'] in ('insert', 'flange'), P['NUT_MODE']
    if INS:
        # 铜螺母顶齐件顶: 件顶 TOP ≥ 槽高 + T_TOP_MIN, 尖 ≤ TOP (不冒头), 啮合 = 尖 − (TOP − INSERT_L) ≥ INSERT_ENGAGE_MIN;
        #   每个长度取最低可行 TOP, 再取 TOP 最低 → 啮合最大 → 螺丝最短
        IL = P['INSERT_L']; HDEP = IL + P['INSERT_CLR']
        top_min = math.ceil((CH_H + P['T_TOP_MIN']) * 100 - 1e-6) / 100
        cands = []
        for L in sorted(P['SCREW_LENS']):
            tip = BEAR_Z + L
            top = max(top_min, tip)
            eng = min(tip, top) - (top - IL)
            if tip > ZL + 1e-9 or top > ZL + 1e-9 or eng < P['INSERT_ENGAGE_MIN'] - 1e-9 or top - HDEP < 0.5: continue
            cands.append((top, -eng, L, tip))
        assert cands, '没有可用 M3 长度 (尖 ≤ 件顶 ≤ Z_LIMIT 且进铜螺母 ≥ INSERT_ENGAGE_MIN)'
        TOP, _, SCREW_L, TIP = min(cands)
        NUT_Z1 = TOP; NUT_Z0 = TOP - IL                    # = 铜螺母 insert_z0 / z1
        EAR_TOP = TOP - HDEP                               # Φ4.2 盲孔底
    else:
        choice = None
        for L in sorted(P['SCREW_LENS']):
            tip = BEAR_Z + L
            if tip > ZL + 1e-9: continue
            if tip - P['NUT_T'] >= P['EAR_MIN'] - 1e-9:
                choice = (L, tip); break
        assert choice, '没有可用 M3 长度'
        SCREW_L, TIP = choice
        TOP = max(CH_H + P['T_TOP_MIN'], P['EAR_MIN'] + P['NUT_T'])
        TOP = math.ceil(TOP * 100 - 1e-6) / 100
        NUT_Z1 = min(TIP, TOP)                                 # 螺母顶齐件顶 (全在井里), 但不高于尖
        NUT_Z0 = NUT_Z1 - P['NUT_T']
        EAR_TOP = NUT_Z0                                       # 井底 = 螺母底
        assert EAR_TOP >= P['EAR_MIN'] - 1e-9
    ENGAGE = min(TIP, NUT_Z1) - NUT_Z0
    T_TOP = TOP - CH_H

    # ---- 平面 ----
    WR = P['INSERT_D'] / 2 if INS else P['WELL_D'] / 2
    WWALL = P['INSERT_WALL'] if INS else P['WELL_WALL']
    G0, G1 = XB - CH_W / 2, XB + CH_W / 2                  # 槽 x
    HX = 0.0
    sink_hw = P['SINK_W'] / 2
    HX = max(HX, sink_hw + P['MIN_WALL'] + P['M3_CB_D'] / 2)                 # 沉孔在散热片槽外
    HX = max(HX, max(G1 - XPC, XPC - G0) + WWALL + WR)              # 井离槽 (薄侧)
    HX = math.ceil(HX * 4 - 1e-6) / 4
    HOLES_X = (XPC - HX, XPC + HX)
    XO = HX + WR + P['OUT_WALL']
    Y_OPEN = Y_ROOT - s * P['OPEN_CLR']
    Y_END = Y_TIP + s * P['BAFFLE_T']
    YA, YB = min(Y_OPEN, Y_END), max(Y_OPEN, Y_END)
    YM = (YA + YB) / 2
    assert (YB - YA) / 2 - WR >= P['OUT_WALL'] - 1e-9, '压块沿 Y 太短, 井离 Y 端面 < OUT_WALL'
    HOLES = [(x, YM) for x in HOLES_X]

    HEXW = P['NUT_HEX_WELL'] and not INS
    HEX_RC = P['WELL_AF'] / math.sqrt(3)
    Z_STEP = NUT_Z1 - P['WELL_FL_H'] if HEXW else EAR_TOP           # 六角段顶 / 圆段底

    # ---- 压块 (装配姿态) ----
    groove = box(G0, Y_OPEN - s * 1, -1, G1, Y_TIP, CH_H)   # 盲槽: 开口端穿出, 止于背板尖 (挡板内面)
    cc = cut(box(XPC - XO, YA, 0, XPC + XO, YB, TOP), groove)
    for x, y in HOLES:
        cc = cut(cc, cyl(x, y, P['HOLE_D'], -1, TOP + 1))

    def well(x, y):
        if INS: return cyl(x, y, P['INSERT_D'], EAR_TOP, TOP + 1)          # 铜螺母 Φ4.2 盲孔
        w = cyl(x, y, P['WELL_D'], Z_STEP, TOP + 1)
        return fuse(w, hexprism(x, y, P['WELL_AF'], EAR_TOP, Z_STEP + 0.01)) if HEXW else w
    wells = [well(x, y) for x, y in HOLES]
    for w in wells: cc = cut(cc, w)
    clamp = clean(cc)
    SAC = 0.0 if INS else P['SAC_LAYER']
    clamp_sac = clean(fuse(clamp, *[cyl(x, y, P['HOLE_D'] + 0.02, EAR_TOP - SAC, EAR_TOP) for x, y in HOLES])) if SAC > 0 else clamp

    # ---- MOS (规格书名义): 背板 E×D×A1 (Φ3.6 孔) + 塑封体 E×(D−H1)×A + 3 引脚短段 ----
    tab = cut(box(XB - E / 2, Y_ROOT, 0, XB + E / 2, Y_TIP, A1), cyl(XB, Y_TIP - s * P['MOS_Q'], P['MOS_P'], -1, A1 + 1))
    body = box(XB - E / 2, Y_ROOT, 0, XB + E / 2, Y_BODY, A)
    leads = [box(XB + k * P['LEAD_P'] - P['LEAD_W'] / 2, Y_ROOT - s * P['LEAD_L'], P['LEAD_Z'] - P['LEAD_T'] / 2,
                 XB + k * P['LEAD_P'] + P['LEAD_W'] / 2, Y_ROOT, P['LEAD_Z'] + P['LEAD_T'] / 2) for k in (-1, 0, 1)]
    mos = clean(fuse(tab, body, *leads))

    # ---- 紧固件 ----
    def screw(x, y):
        return fuse(cyl(x, y, P['HEAD_D'], BEAR_Z - P['HEAD_H'], BEAR_Z), cyl(x, y, P['SHANK_D'], BEAR_Z, TIP))

    def nut(x, y):
        if INS:    # 铜螺母 Φ4.2×4, 中心 Φ3 (同 fasteners_v1_2.insert)
            return cut(cyl(x, y, P['INSERT_D'], NUT_Z0, NUT_Z1), cyl(x, y, P['SHANK_D'], NUT_Z0 - 1, NUT_Z1 + 1))
        if HEXW:   # 法兰朝上: 六角 NUT_Z0..NUT_Z1−FL_H, 法兰在上
            body = fuse(hexprism(x, y, P['NUT_AF'], NUT_Z0, NUT_Z1 - P['NUT_FL_H']), cyl(x, y, P['NUT_FL_D'], NUT_Z1 - P['NUT_FL_H'], NUT_Z1))
        else:
            body = fuse(cyl(x, y, P['NUT_FL_D'], NUT_Z0, NUT_Z0 + P['NUT_FL_H']), hexprism(x, y, P['NUT_AF'], NUT_Z0 + P['NUT_FL_H'], NUT_Z1))
        return cut(body, cyl(x, y, P['SHANK_D'], NUT_Z0 - 1, NUT_Z1 + 1))
    screws = [screw(x, y) for x, y in HOLES]
    nuts = [nut(x, y) for x, y in HOLES]

    # ---- 底盘切口 (本件只给 2×(Φ3.2 通 + 底面 Φ7×2 沉孔); 散热片槽由 coil_drv_geom 切) ----
    thru = [cyl(x, y, P['M3_D'], -DT - 1, 1) for x, y in HOLES]
    cbs = [cyl(x, y, P['M3_CB_D'], -DT - 1, BEAR_Z) for x, y in HOLES]
    disc_cuts = thru + cbs
    slot = box(XPC - sink_hw, P['SINK_Y0'], -DT - 1, XPC + sink_hw, P['SINK_Y1'], 1)
    sink = box(XPC - sink_hw, P['SINK_Y0'], -DT, XPC + sink_hw, P['SINK_Y1'], 0)   # 简化为实心块 (只校核)

    # ---- 校核 ----
    pad = 3
    bx0, bx1 = XPC - XO - pad, XPC + XO + pad
    by0, by1 = min(YA, P['SINK_Y0']) - pad, max(YB, P['SINK_Y1']) + pad
    disc_blk = cut(box(bx0, by0, -DT, bx1, by1, 0), slot, *disc_cuts)
    C = {}
    C['clamp_valid'] = BRepCheck_Analyzer(clamp).IsValid()
    C['clamp_solids'] = nsolids(clamp)
    C['iv_clamp_mos'] = iv(clamp, mos)
    C['gap_clamp_mos'] = dist(clamp, mos)
    C['gap_top_body'] = dist(common(clamp, box(G0 - 1, Y_ROOT, CH_H - 1e-3, G1 + 1, Y_BODY, TOP + 1)), body)     # 槽顶 ↔ 塑封体顶
    C['gap_tab_above'] = CH_H - A1                                                                                 # 背板露出段上方空腔
    C['gap_side'] = (CH_W - E) / 2
    baffle = common(clamp, box(G0 - 1, Y_TIP, 0, G1 + 1, Y_END, TOP + 1))
    C['gap_baffle_tip'] = dist(baffle, tab)
    C['iv_clamp_disc'] = iv(clamp, disc_blk)
    C['iv_clamp_sink'] = iv(clamp, sink)
    C['iv_mos_sink'] = iv(mos, sink); C['iv_mos_disc'] = iv(mos, disc_blk)
    C['iv_clamp_screw'] = sum(iv(clamp, sc) for sc in screws)
    C['iv_clamp_nut'] = sum(iv(clamp, n) for n in nuts)
    C['iv_disc_screw'] = sum(iv(disc_blk, sc) for sc in screws)
    C['iv_sink_screw'] = sum(iv(sink, sc) for sc in screws)
    C['sac_layer'] = SAC
    C['iv_sac_screw'] = sum(iv(clamp_sac, sc) for sc in screws)        # 牺牲层被螺丝捅穿的量 (应 ≈ 2·π·1.5²·0.2)
    groove_in = common(groove, box(XPC - XO, YA, 0, XPC + XO, YB, TOP))
    C['wall_well_groove'] = min(dist(w, groove_in) for w in wells)
    C['wall_well_xend'] = XO - HX - WR
    C['wall_well_yend'] = (YB - YA) / 2 - WR
    if HEXW:   # 防转: 螺母转 5° 必须撞六角井; 六角角壁 ≥1
        rot = gp_Trsf(); rot.SetRotation(gp_Ax1(gp_Pnt(*HOLES[0], 0), gp_Dir(0, 0, 1)), math.radians(5))
        C['antirot_iv_5deg'] = iv(xf(nuts[0], rot), clamp)
        C['hex_corner_wall_groove'] = min(dist(hexprism(x, y, P['WELL_AF'], EAR_TOP, Z_STEP), groove_in) for x, y in HOLES)
        C['hex_corner_wall_end'] = min(XO - HX - HEX_RC, (YB - YA) / 2 - HEX_RC)
        assert C['antirot_iv_5deg'] > 1e-3, '六角井不防转'
        assert min(C['hex_corner_wall_groove'], C['hex_corner_wall_end']) >= 1.0 - 1e-6, '六角角壁 <1'
    C['nut_mode'] = P['NUT_MODE']
    C['nut_well'] = (f'铜螺母孔 Φ{P["INSERT_D"]:g} Z{EAR_TOP:g}..{TOP:g} (深 {TOP - EAR_TOP:g})' if INS else f'六角 AF{P["WELL_AF"]:g} Z{EAR_TOP:g}..{Z_STEP:g} + Φ{P["WELL_D"]:g} Z{Z_STEP:g}..顶 (法兰朝上)' if HEXW else f'全圆 Φ{P["WELL_D"]:g}')
    C['gap_nut_well'] = min(dist(n, common(clamp, box(x - 10, YA - 1, NUT_Z0 + 1e-3, x + 10, YB + 1, TOP + 1))) for n, (x, _) in zip(nuts, HOLES))
    fl_ring = cut(cyl(0, 0, P['INSERT_D'], -0.01, 0) if INS else hexprism(0, 0, P['NUT_AF'], -0.01, 0) if HEXW else cyl(0, 0, P['NUT_FL_D'], -0.01, 0), cyl(0, 0, P['HOLE_D'], -1, 1))
    sup = []
    for x, y in HOLES:
        t = gp_Trsf(); t.SetTranslation(gp_Vec(x, y, EAR_TOP if INS else NUT_Z0)); r = xf(fl_ring, t); sup.append(iv(r, clamp) / vol(r))   # INS: 孔底台阶 (Φ4.2→Φ3.4) 有实体
    C['nut_support'] = min(sup)
    C['wall_cb_slot'] = HX - P['M3_CB_D'] / 2 - sink_hw
    C['keepout_wall'] = min((math.hypot(x - a, y - b) - P['M3_CB_D'] / 2 - r for x, y in HOLES for a, b, r in P['KEEPOUT']), default=99)
    C['pitch'] = 2 * HX; C['width'] = 2 * XO; C['length'] = YB - YA
    C['groove_off'] = XB - XPC
    C['top'] = TOP; C['t_top'] = T_TOP; C['nut_top'] = NUT_Z1; C['tip'] = TIP; C['engage'] = ENGAGE
    C['tip_above_top'] = TIP - TOP

    assert C['clamp_valid'] and C['clamp_solids'] == 1, '压块不是单个有效实体'
    assert C['iv_clamp_mos'] < EPS_V and C['gap_clamp_mos'] < 1e-6, ('压块-MOS', C['iv_clamp_mos'], C['gap_clamp_mos'])
    assert C['gap_top_body'] < 1e-6, ('槽顶没贴塑封体', C['gap_top_body'])
    assert C['gap_baffle_tip'] < 1e-6, ('挡板没顶背板尖', C['gap_baffle_tip'])
    assert C['iv_clamp_disc'] < EPS_V and C['iv_clamp_sink'] < EPS_V, '压块碰底盘/散热片'
    assert C['iv_mos_sink'] < EPS_V and C['iv_mos_disc'] < EPS_V, 'MOS 碰散热片/底盘'
    assert C['iv_clamp_screw'] < EPS_V and C['iv_clamp_nut'] < EPS_V, '螺丝/螺母碰压块'
    assert C['iv_disc_screw'] < EPS_V and C['iv_sink_screw'] < EPS_V, '螺丝碰底盘/散热片'
    _g = 0.0 if INS else min((P['WELL_AF'] - P['NUT_AF']) / 2, (P['WELL_D'] - P['NUT_FL_D']) / 2) if HEXW else 0.25
    assert C['gap_nut_well'] >= _g - 1e-6, (f'螺母离井壁 <{_g}', C['gap_nut_well'])
    assert C['wall_well_groove'] >= WWALL - 1e-6, ('井离槽太近', C['wall_well_groove'])
    assert C['wall_well_xend'] >= P['OUT_WALL'] - 1e-6 and C['wall_well_yend'] >= P['OUT_WALL'] - 1e-6
    assert C['nut_support'] > 0.999, ('法兰底支承不全', C['nut_support'])
    assert C['wall_cb_slot'] >= P['MIN_WALL'] - 1e-6, ('沉孔离散热片槽太近', C['wall_cb_slot'])
    assert T_TOP >= P['T_TOP_MIN'] - 1e-9
    assert TOP <= ZL + 1e-9 and NUT_Z1 <= ZL + 1e-9 and TIP <= ZL + 1e-9, ('超高', TOP, NUT_Z1, TIP)
    if INS:
        assert ENGAGE >= P['INSERT_ENGAGE_MIN'] - 1e-9 and TIP <= TOP + 1e-9, ('铜螺母啮合不足或螺尖冒出件顶', ENGAGE, TIP, TOP)
        assert EAR_TOP > 0, '铜螺母孔底穿到槽底面'
    else:
        assert ENGAGE >= P['NUT_T'] - 1e-9, '螺母没吃满'
    if C['keepout_wall'] < P['KEEPOUT_WALL'] - 1e-6:
        print(f"  [警告] M3 沉孔离禁区 (KEEPOUT) 壁 {C['keepout_wall']:.2f} < {P['KEEPOUT_WALL']}")

    # ---- 打印姿态: 绕过 (XPC, YM, TOP/2) 的 X 轴转 180°, 顶面贴床; 平移使 XPC/YM 为原点 ----
    tr = gp_Trsf(); tr.SetRotation(gp_Ax1(gp_Pnt(XPC, YM, TOP / 2), gp_Dir(1, 0, 0)), math.radians(180))
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(-XPC, -YM, 0)); tp = t2.Multiplied(tr)
    clamp_print = xf(clamp_sac, tp)
    pb = bbox(clamp_print)
    assert abs(pb[2]) < 1e-6, pb
    C['overhang'] = overhangs(clamp_print)
    # 预期朝下面只有井顶 (平面): 井底 z = TOP − EAR_TOP, 六角/圆台阶 z = TOP − Z_STEP
    oh_bad = [o for o in C['overhang'] if not (o[0] == 'Plane' and min(abs(o[2] - (TOP - EAR_TOP)), abs(o[2] - (TOP - Z_STEP))) < 1e-3)]
    assert not oh_bad, ('意外悬空面', oh_bad)

    return dict(clamp=clamp, clamp_sac=clamp_sac, clamp_print=clamp_print, print_trsf=tp, mos=mos, mos_parts=dict(tab=tab, body=body, leads=leads),
                screws=screws, nuts=nuts, inserts=nuts if INS else [], nut_mode=P['NUT_MODE'], sink=sink,
                disc_cuts=disc_cuts, disc_cut_labels=[f'M3通{i}' for i in range(2)] + [f'M3沉孔{i}' for i in range(2)],
                holes=HOLES, screw_len=SCREW_L, nut_z0=NUT_Z0, nut_z1=NUT_Z1, insert_z0=NUT_Z0 if INS else None, insert_z1=NUT_Z1 if INS else None, hole_depth=TOP - EAR_TOP, tip=TIP, engage=ENGAGE, well_step=Z_STEP, ear_top=EAR_TOP,
                top=TOP, ch_w=CH_W, ch_h=CH_H, bear_z=BEAR_Z, x_span=(XPC - XO, XPC + XO), y_span=(YA, YB),
                groove_x=(G0, G1), mos_x=XB, mos_y=(Y_ROOT, Y_BODY, Y_TIP), checks=C, params=P, disc_block=disc_blk, volume=vol(clamp))


# ======================== 导出 / 预览 ========================
def write_stl(sh, path):
    BRepMesh_IncrementalMesh(sh, 0.01, False, 0.1, True)
    w = StlAPI_Writer(); w.ASCIIMode = False
    assert w.Write(sh, str(path))


def write_step(sh, path):
    Interface_Static.SetCVal_s('write.step.schema', 'AP214IS'); Interface_Static.SetCVal_s('write.step.unit', 'MM')
    w = STEPControl_Writer(); w.Transfer(sh, STEPControl_AsIs)
    assert w.Write(str(path)) == IFSelect_RetDone


def section_polylines(sh, pln):
    """sh 与平面的交线, 离散成折线列表 [(N,3) list]"""
    s = BRepAlgoAPI_Section(sh, pln); s.Build()
    out = []
    ex = TopExp_Explorer(s.Shape(), TopAbs_EDGE)
    while ex.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
        d = GCPnts_QuasiUniformDeflection(c, 0.01)
        pts = [d.Value(i + 1) for i in range(d.NbPoints())] if d.IsDone() else [c.Value(c.FirstParameter()), c.Value(c.LastParameter())]
        out.append([(q.X(), q.Y(), q.Z()) for q in pts]); ex.Next()
    return out


def tris(sh, defl=0.05):
    BRepMesh_IncrementalMesh(sh, defl, False, 0.3, True)
    out = []
    ex = TopExp_Explorer(sh, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current()); loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            tr = loc.Transformation()
            nodes = [tri.Node(i + 1).Transformed(tr) for i in range(tri.NbNodes())]
            for i in range(tri.NbTriangles()):
                a, b, c = tri.Triangle(i + 1).Get()
                out.append([(nodes[k - 1].X(), nodes[k - 1].Y(), nodes[k - 1].Z()) for k in (a, b, c)])
        ex.Next()
    return out


def preview(r, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    for f in ('Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'SimHei', 'Microsoft YaHei'):
        if any(f == x.name for x in font_manager.fontManager.ttflist):
            plt.rcParams['font.family'] = f; break
    else:
        import glob
        for fp in glob.glob('/mnt/c/Windows/Fonts/msyh*.tt*') + glob.glob('/mnt/c/Windows/Fonts/simhei.ttf'):
            font_manager.fontManager.addfont(fp); plt.rcParams['font.family'] = font_manager.FontProperties(fname=fp).get_name(); break
    plt.rcParams['axes.unicode_minus'] = False
    P, C = r['params'], r['checks']
    INS = r['nut_mode'] == 'insert'
    XPC = P['XPC']; YM = r['holes'][0][1]; XB = r['mos_x']
    fig = plt.figure(figsize=(20, 12))
    blk = r['disc_block']

    # 1) 3D 装配
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    for sh, col, a in ((blk, '#555555', 0.30), (r['sink'], '#9fb3c8', 0.35), (r['mos'], '#1f1f1f', 0.95), (r['clamp'], '#e08a1e', 0.85)) + \
            tuple((s, '#999999', 1) for s in r['screws']) + tuple((n, '#bbbbbb', 1) for n in r['nuts']):
        ax.add_collection3d(Poly3DCollection(tris(sh), facecolor=col, edgecolor='none', alpha=a))
    b = bbox(blk)
    ax.set_xlim(b[0], b[3]); ax.set_ylim(b[1], b[4]); ax.set_zlim(-8, 12)
    ax.set_box_aspect((b[3] - b[0], b[4] - b[1], 20)); ax.view_init(28, -55)
    ax.set_title('装配 (局部底盘块 + 散热片 + TO-220 + 压块 + M3)'); ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')

    # 2) 3D 打印姿态
    ax = fig.add_subplot(2, 4, 3, projection='3d')
    ax.add_collection3d(Poly3DCollection(tris(r['clamp_print']), facecolor='#e08a1e', edgecolor='#00000020', alpha=1))
    b = bbox(r['clamp_print'])
    ax.set_xlim(b[0] - 2, b[3] + 2); ax.set_ylim(b[1] - 2, b[4] + 2); ax.set_zlim(0, b[5] + 2)
    ax.set_box_aspect((b[3] - b[0] + 4, b[4] - b[1] + 4, b[5] + 2)); ax.view_init(35, -60)
    ax.set_title(('打印姿态: 顶面贴床 (槽口朝上), 铜螺母孔口在床面\n' if INS else '打印姿态: 顶面贴床 (槽口朝上), 带牺牲层\n') + f'{b[3]-b[0]:.1f}×{b[4]-b[1]:.1f}×{b[5]:.2f}  体积 {r["volume"]:.0f} mm³', fontsize=10)
    ax = fig.add_subplot(2, 4, 4)   # 打印姿态俯视 (从床面上方看)
    for pl in section_polylines(r['clamp_print'], gp_Pln(gp_Pnt(0, 0, 0.1), gp_Dir(0, 0, 1))):
        ax.plot([q[0] for q in pl], [q[1] for q in pl], color='#e08a1e', lw=1.2)
    for pl in section_polylines(r['clamp_print'], gp_Pln(gp_Pnt(0, 0, b[5] - 0.1), gp_Dir(0, 0, 1))):
        ax.plot([q[0] for q in pl], [q[1] for q in pl], color='#1f3b73', lw=0.8, ls='--')
    ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_title('打印姿态截面: 橙 z0.1 (床面, ' + ('Φ4.2 铜螺母孔口' if INS else '六角/Φ8.2 井口') + '), 蓝虚 顶层 (槽口)', fontsize=9)
    oh = '; '.join(f'{t} {a:g}mm² @z{z:g}' for t, a, z in C['overhang'])
    ax.text(0.01, -0.18, f'朝下面 (桥接): {oh}', transform=ax.transAxes, fontsize=8, wrap=True)

    chain = [(r['bear_z'], '头支承面'), (-P['DISC_T'], '底盘底'), (0, 'Z0 底盘顶=散热片顶=背板底'), (P['MOS_A1'], '背板顶 A1'),
             (P['LEAD_Z'], '引脚中心'), (r['ch_h'], '槽顶 = 塑封体顶 A')]
    if INS:
        chain += [(r['ear_top'], f'Φ{P["INSERT_D"]:g} 孔底 = 铜螺母底'), (r['top'], '件顶 = 铜螺母顶'), (r['tip'], f'M3×{r["screw_len"]:g} 尖')]
    else:
        chain += [(r['ear_top'] - P['SAC_LAYER'], '牺牲层底'), (r['ear_top'], '井底 = 螺母底'),
                  (r['well_step'], '六角/Φ8.2 台阶'), (r['top'], '件顶 = 螺母(法兰)顶'), (r['tip'], f'M3×{r["screw_len"]:g} 尖')]

    def secplot(ax, pln, u, items):
        for sh, col, lab in items:
            first = True
            for pl in section_polylines(sh, pln):
                ax.plot([q[u] for q in pl], [q[2] for q in pl], color=col, lw=1.5, label=lab if first else None); first = False

    def zchain(ax, xr):
        ax.axhline(P['STATOR_Z0'], color='r', lw=1); ax.text(xr - 1, P['STATOR_Z0'] + 0.1, f'定子盘底 Z{P["STATOR_Z0"]:g}', color='r', fontsize=8, ha='right')
        ax.axhline(P['Z_LIMIT'], color='r', lw=0.8, ls='--')
        ax.text(xr - 1, P['Z_LIMIT'] - 0.45, f'Z_LIMIT {P["Z_LIMIT"]:g}', color='r', fontsize=8, ha='right')
        zs = []
        for z, t in sorted(chain):
            zt = max(z, zs[-1] + 0.8) if zs else z; zs.append(zt)
            ax.plot([xr, xr + 2], [z, zt], color='k', lw=0.4)
            ax.text(xr + 2.2, zt, f'Z{z:+.2f} {t}', va='center', fontsize=7.5)

    # 3) 端视剖面 (过孔心 y)
    ax = fig.add_subplot(2, 2, 3)
    items = [(blk, '#555555', '底盘'), (r['sink'], '#6d8fb3', '散热片 (示意实心)'), (r['mos'], '#111111', 'TO-220'), (r['clamp'], '#e08a1e', '压块')] + \
            [(s, '#777777', 'M3' if i == 0 else None) for i, s in enumerate(r['screws'])] + \
            [(n, '#2a9d8f', ('铜螺母 M3×4' if INS else '法兰螺母 (倒放)') if i == 0 else None) for i, n in enumerate(r['nuts'])]
    secplot(ax, gp_Pln(gp_Pnt(0, YM, 0), gp_Dir(0, 1, 0)), 0, items)
    x0, x1 = r['x_span']
    ax.axvline(XPC, color='g', lw=0.7, ls='-.'); ax.text(XPC, -7.6, f'板中轴 x{XPC:g}', color='g', fontsize=8, ha='center')
    ax.axvline(XB, color='m', lw=0.7, ls='-.'); ax.text(XB, 10.3, f'MOS 中心 x{XB:g}', color='m', fontsize=8, ha='center')
    zchain(ax, x1 + 2)
    ax.set_xlim(x0 - 3, x1 + 24); ax.set_ylim(-8, 11); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_xlabel('X (装配系)'); ax.set_ylabel('Z'); ax.set_title(f'端视剖面 y = {YM:.2f} (过两孔心; 槽偏心 {C["groove_off"]:+.2f})')
    ax.legend(loc='lower left', fontsize=7, ncol=2)

    # 4) 纵剖 (沿 MOS 轴 x = XB)
    ax = fig.add_subplot(2, 2, 4)
    secplot(ax, gp_Pln(gp_Pnt(XB, 0, 0), gp_Dir(1, 0, 0)), 1, items[:4])
    ya, yb = r['y_span']; yr, yby, yt = r['mos_y']
    ax.annotate('背板尖-挡板 0 间隙', (yt, 0.6), (yt + 4 * (1 if yt > yr else -1), -2.5), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.annotate('槽顶贴塑封体 0 间隙', ((yr + yby) / 2, r['ch_h']), ((yr + yby) / 2, -3.2), fontsize=8, ha='center', arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.annotate(f'背板露出段上方空 {C["gap_tab_above"]:.2f}', ((yby + yt) / 2, 2.8), ((yby + yt) / 2, -5), fontsize=8, ha='center', arrowprops=dict(arrowstyle='->', lw=0.6))
    yR = max(ya, yb, P['SINK_Y1'])
    zchain(ax, min(yR, yb + 6) + 1)
    ax.set_xlim(min(ya, yr - P['LEAD_L']) - 4, min(yR, yb + 6) + 24); ax.set_ylim(-8, 11); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_xlabel('Y (装配系)'); ax.set_ylabel('Z'); ax.set_title(f'纵剖 x = {XB:.2f} (沿 MOS 轴; 引脚 → −Y 开口)' if yt > yr else f'纵剖 x = {XB:.2f}')
    txt = (f'外形 {C["width"]:.2f}×{C["length"]:.2f}×{r["top"]:.2f}, 孔距 {C["pitch"]:.2f} (以板中轴对称); 槽 {r["ch_w"]:.2f}×{r["ch_h"]:.2f} 偏心 {C["groove_off"]:+.2f}\n'
           f'{"孔" if INS else "井"}: {C["nut_well"]}; 牺牲层 {C["sac_layer"]:g}\n'
           f'壁: 井-槽 {C["wall_well_groove"]:.2f} / 井-X端 {C["wall_well_xend"]:.2f} / 井-Y端 {C["wall_well_yend"]:.2f} / 沉孔-散热片槽 {C["wall_cb_slot"]:.2f}; 槽顶厚 {C["t_top"]:.2f}\n'
           f'M3×{r["screw_len"]:g}: {"铜螺母" if INS else "螺母"} Z{r["nut_z0"]:g}..{r["nut_z1"]:g} 啮合 {r["engage"]:.2f}, 尖 Z{r["tip"]:g} 露出件顶 {C["tip_above_top"]:.2f}; 防转 5° 干涉 {C.get("antirot_iv_5deg", 0):.2f} mm³\n'
           f'干涉: 压块-MOS {C["iv_clamp_mos"]:.1e}, -底盘 {C["iv_clamp_disc"]:.1e}, -散热片 {C["iv_clamp_sink"]:.1e}, -螺丝/螺母 {C["iv_clamp_screw"] + C["iv_clamp_nut"]:.1e}')
    ax.text(0.01, 0.01, txt, transform=ax.transAxes, fontsize=8, va='bottom', bbox=dict(fc='white', ec='#ccc'))
    ax.legend(loc='upper left', fontsize=7)
    fig.suptitle(f'mos_clamp_v1_2 TO-220 MOS 压块 ({VERSION})', fontsize=14)
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)


def main():
    r = make_mos_clamp()
    MODEL_DIR.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    write_stl(r['clamp_print'], MODEL_DIR / 'mos_clamp_v1_2.stl')
    write_step(r['clamp_print'], MODEL_DIR / 'mos_clamp_v1_2.step')
    preview(r, OUT / 'mos_clamp_v1_2_preview.png')
    C, P = r['checks'], r['params']
    b = bbox(r['clamp']); pb = bbox(r['clamp_print'])
    print(f'mos_clamp_v1_2 {VERSION}')
    print(f'  装配 bbox x {b[0]:.2f}..{b[3]:.2f}  y {b[1]:.2f}..{b[4]:.2f}  z {b[2]:.2f}..{b[5]:.2f}; 体积 {r["volume"]:.1f}')
    print(f'  打印 bbox {pb[3]-pb[0]:.2f} × {pb[4]-pb[1]:.2f} × {pb[5]-pb[2]:.2f} (顶面 z=0 贴床{"" if r["nut_mode"] == "insert" else ", 带牺牲层"})')
    print(f'  MOS 中心 x {r["mos_x"]:g}; y 根/塑封体端/尖 {r["mos_y"]}; 槽 x {r["groove_x"]}')
    print(f'  Z 链: 头支承 {r["bear_z"]:g} / 井(孔)底 {r["ear_top"]:g} / 台阶 {r["well_step"]:g} / 槽顶 {r["ch_h"]:g} / 件顶=螺母顶 {r["top"]:g} / '
          f'M3×{r["screw_len"]:g} 尖 {r["tip"]:g} (≤ {P["Z_LIMIT"]:g}); 啮合 {r["engage"]:.2f}')
    print(f'  孔 {[(round(x, 3), round(y, 3)) for x, y in r["holes"]]}')
    for k, v in C.items():
        print(f'  {k:24s} {v if not isinstance(v, float) else round(v, 4)}')
    print('  STL/STEP ->', MODEL_DIR, '; 预览 ->', OUT / 'mos_clamp_v1_2_preview.png')


if __name__ == '__main__':
    main()
