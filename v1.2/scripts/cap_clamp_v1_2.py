"""
电解电容半圆卡件 cap_clamp_v1_2 —— 独立生成器 (POV3D V1.2, 2026-11-12 夜)

V1.2-cap-d (用户 11-12 夜「cap和mos的件，m3做通孔加M4.2沉孔」「压铜螺母深度4mm」→ 孔深统一 4.2, NUT_MODE='insert' 缺省):
  不再用法兰螺母 + 螺母井: Φ3.4 通孔贯通 + 顶面往下 Φ4.2 盲孔深 4.2 (比铜螺母长 0.2), 压入/热熔 M3×4 铜螺母 (外径 4.2, 同底盘 G/H), 顶齐卡件顶;
  M3 从底盘底面 Φ7×2 沉孔往上 (头支承 Z−4) 拧进铜螺母。卡件顶仍由电容定 (电容顶 + 0.15 + 1.2), 螺丝取 尖 ≤ 卡件顶 且进铜螺母最多者
  (卡件顶 9.0 ⇒ M3×12 尖 8.0, 进 3.0)。无井 / 六角 / 牺牲层 ⇒ 宽按 Φ4.2 孔 + 1.2 端壁 / EAR_OUT 收窄。打印仍倒扣 (顶面贴床)。
  NUT_MODE='flange' 回到 cap-c 法兰螺母井。

V1.2-cap-c: 卡件长 10.6 (井到 Y 端 1.2); 螺母防转 = 下段六角井 AF6.1 + 上段 Φ8.2, 法兰螺母法兰朝上倒放 (见 NUT_HEX_WELL 注释);
  井底 0.2 牺牲层 (SAC_LAYER, 默认开, 装配前 M3 捅穿)。
V1.2-cap-b (用户 11-12 夜看 STL 选方案 2): 不要拱形加耳, 改实心方块 (参考 XT60 压块) ——
  长方体 Z0..顶 (顶 = 电容顶 + 1.2 = 8.85 ≤ 9.0), 底面半圆槽 R5.15 (槽心 = 电容轴), 2×Φ3.4 通孔位置不变 (孔距 21),
  顶面往下 Φ8.2 螺母井到 Z3.3 (= 螺母底, M3×12 尖 8.0 仍吃满 3.7, 螺母顶 7.0 低于顶面 1.85);
  井壁离半圆槽 ≥1.0 (不够自动外拉孔距), 井离 X 端面 ≥ OUT_WALL 1.2 ⇒ 宽 31.6 (原 29.4 端壁只剩 0.1)。
  打印姿态改为倒扣 (顶面贴床, 槽口朝上)。唯一悬空 = 两个螺母井的井底 (Φ8.2 环形, 中间 Φ3.4 孔) 变成井顶, 需桥接 ~8.2;
  建议切片开桥接, 或用"牺牲层"技巧 (井顶先封一层 0.2, 装时用 M3 捅穿)。
以下为 V1.2-cap-a (鞍形 + 耳) 的原说明, 截面 / 打印姿态部分已被上面取代, 高度链仍有效:
    cd v1.2/scripts && ../../.venv/bin/python cap_clamp_v1_2.py
输出 v1.2/models/cap_clamp_v1_2/cap_clamp_v1_2.stl/.step (打印姿态) + v1.2/out/cap_clamp_v1_2_preview.png

用户 11-12 夜: 「再做一个卡电容的吧，电容卡半圆吧」「螺丝就在左右两边」
  线圈驱动小板一字排布 MOS → PCB 16.5×28 → 电解电容 Φ10×20 (平躺, 轴沿 Y, 对准板中心线, 引脚可弯, 高度可调)。
  电容下半沉进底盘弧形槽 (深 CAP_GROOVE), 上半被鞍形卡件包住; 卡件两侧 (±X) 低耳各一个 M3:
  同 XT60 / MOS 压块 —— M3 超薄头从底盘底面 Φ7×2 沉孔往上 (头支承面 Z −DISC_T+M3_CB_H = −4), 穿底盘 + 耳 Φ3.4,
  M3 法兰螺母 (Φ7.6 / 对边 5.9 / 厚 3.7) 平坐耳顶, 无螺母座。

不 import build_v1_2 (循环 + 慢), 工具函数自带。build_v1_2 / coil_drv_geom 合并时调 make_cap_clamp(p), p 给装配系参数。

截面 (端视, 垂直电容轴):
  鞍 = 外 R1 (= R + CLR + T_TOP) 上半圆 + Z0..轴心 竖壁 − 内 R0 (= R + CLR) 上半圆 + 轴心以下 ±R0 竖槽;
  耳 = Z0..EAR_TOP 矩形, 沿 Y 与鞍等长 (整件是一个 XZ 截面沿 Y 拉伸 + 2 个 Φ3.4 竖孔 ⇒ 立着打印零支撑, 见下)。
高度链 (缺省): 槽深 g ⇒ 电容轴 Z = R − g, 卡件顶 = 2R − g + CLR + T_TOP ≤ Z_LIMIT ⇒ g ≥ 2R + CLR + T_TOP − Z_LIMIT (=2.35);
  螺丝从 {8,12,14,20} 选: 尖 = −4 + L ≤ Z_LIMIT 且 耳顶 = min(EAR_T, 尖 − 3.7) ≥ EAR_MIN ⇒ 只有 M3×12 (尖 8.0);
  耳顶 3.3 ⇒ 螺母 3.3..7.0, 啮合 3.7 吃满, 尖露出螺母 1.0。

打印姿态 (导出文件就是这个姿态): 电容轴竖直 —— 一个 Y 端面贴床, 截面 (半圆 + 双耳) 一层层堆上去。
  - 零悬空: 整件是 XZ 截面沿 Y 的拉伸, 只有 2 个 Φ3.4 孔变成横孔 (小孔顶 ~1.7 跨度, 免支撑);
  - 半圆每层都是整圆弧 ⇒ 内径精度最好 (0.15 间隙不会被下垂吃掉);
  - 鞍的环向拉力 (螺丝把耳往下拉) 全在层内, 不拉层间。
  对比 装配姿态 (Z0 底面贴床): 也能免支撑 —— 内腔拱顶 45° 以上那段是桥 (宽 2·R0·sin45 ≈ 7.3, 能桥), 但桥会下垂 0.1~0.3
  直接吃掉 0.15 间隙, 而且 1.2 薄壁在轴心高度处竖向受拉 = 拉层间, 易开裂 ⇒ 不选。
  倒扣 (顶朝下) 只有一条线贴床、耳悬空 ⇒ 不行。
  立着打印接触面 = 截面积 ~70 mm², 高 = 卡件长 10, 稳; 建议加 3 mm brim。
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

VERSION = "V1.2-cap-d"
HERE = Path(__file__).resolve().parent
V12 = HERE.parent
MODEL_DIR = V12 / 'models' / 'cap_clamp_v1_2'
OUT = V12 / 'out'

# ======================== 缺省参数 (装配系, mm) ========================
DEFAULTS = dict(
    # 电容 (装配系: 轴沿 Y, CAP_Y0 < CAP_Y1)
    CAP_CX=55.05,        # 电容轴 x (= 板中心线, coil_drv_geom.XPC)
    CAP_Y0=-51.0, CAP_Y1=-31.0,
    CAP_D=10.0, CAP_L=20.0,
    CAP_GROOVE=0.0,      # 底盘弧形槽深 (电容底在 Z0 以下多少) —— 建议值; < 最小可行值时自动加深 (上限 3, 底盘剩 ≥3)
                         #   cap-d: 2.5 → 0 (= 自动取最小可行 2.35, 同 coil_drv_geom 传参), 独立导出的 STL 与整机装配一致 (顶 9.0)
    CAP_ZC=None,         # 电容轴心 Z; None ⇒ = CAP_D/2 − 槽深。给了就以它为准 (反算槽深, 不自动调)
    TROUGH_CLR=0.2,      # 弧形槽半径余量 (槽 R5.2, 槽底 = 电容底 ⇒ 电容贴槽底, 两侧 0.2)
    TROUGH_EXT=0.5,      # 槽沿 Y 两端各长出电容
    GROOVE_MAX=3.0,      # 槽深上限 (底盘 6 剩 ≥3)
    # 底盘 / 上方限高
    DISC_T=6.0,          # 底盘 Z −6..0
    Z_LIMIT=8.35,        # 用户 11-12 夜: 法兰盘底 9.5 → 8.5, 槽深挖到上限 3 后卡件顶 = 电容顶 7 + 0.15 + 1.2 = 8.35 ⇒ 卡件单独放宽到 8.35 (离定子盘底只剩 0.15); 整机由 coil_drv_geom 传
    STATOR_Z0=8.5,       # 定子盘 (法兰盘) 底, 只用于预览画线 (用户 11-12 夜 9.5 → 8.5); 整机由 coil_drv_geom 按 B.FL_Z0 传
    # 卡件
    CLR=0.15,            # 内半圆单边间隙 ⇒ R0 5.15
    T_TOP=1.2,           # 鞍顶 / 侧壁厚 ⇒ R1 6.35
    CLAMP_LEN=10.6,      # 卡件沿电容轴长 (cap-c: 10 → 10.6, Φ8.2 井到 Y 两端壁 1.2)
    CLAMP_Y_OFF=-5.0,    # 卡件中心相对电容中点的 Y 偏移 (−5: 卡件齐电容远端, 孔让开网格 M6 (37.5,−37.5) 沉孔 Φ13, 壁 1.0)
    PITCH=21.0,          # 两孔距 (电容轴 ±10.5; 法兰 Φ7.6 离鞍外壁 0.40)
    EAR_T=3.3,           # 耳厚 (Z0..耳顶) 期望值; 受螺丝尖 / 啮合约束会被压低
    EAR_MIN=2.5,         # 耳厚下限
    EAR_OUT=4.2,         # 外形 X 端面离孔心的下限 (原鞍形耳外缘)
    WELL_D=8.2,          # 螺母井 Φ (法兰 Φ7.6 + 0.6), 从顶面往下到螺母底 (= EAR_TOP)
    WELL_WALL=1.0,       # 螺母井 ↔ 半圆槽 最小壁; 不够就把孔距往外拉 (0.5 一档)
    OUT_WALL=1.2,        # 螺母井 ↔ X 端面 最小壁 (外形宽度由它和 EAR_OUT 取大)
    # cap-c 螺母防转: 六角井 + 法兰螺母**法兰朝上倒放**。
    #   协调方给的"下段 Φ8.2 放法兰 / 上段六角"装不进去: 螺母从顶面放入, 法兰 Φ7.6 > 六角井外接圆 6.1/cos30 = 7.04, 过不了六角段。
    #   ⇒ 反过来: 下段 (井底 EAR_TOP 起) 六角 AF6.1 高 NUT_T − WELL_FL_H = 2.5 卡住螺母六角 (螺母六角实长 2.7 ≥ 2.5, 法兰不会先搁在台阶上),
    #      上段 Φ8.2 容法兰 (取 1.2 留余)。六角端面压井底 (支承面 = 六角 − Φ3.4), 螺丝从下拧, 螺母不转。
    #   NUT_HEX_WELL=False ⇒ 退回全圆 Φ8.2 井, 法兰朝下坐井底。
    NUT_HEX_WELL=True, WELL_AF=6.1, WELL_FL_H=1.2,
    # cap-c 牺牲层: 倒扣打印时井底是悬空的井顶 ⇒ 在 Φ3.4 孔的井底端留 SAC_LAYER 厚封口 (装配 Z EAR_TOP−0.2..EAR_TOP),
    #   第一层桥接整片不留孔, 打出来封口, 装配前用 M3 捅穿。0 ⇒ 关。返回的 clamp 是捅穿后的 (校核/装配用),
    #   clamp_print / 导出 STL·STEP 带牺牲层, clamp_sac 是带牺牲层的装配姿态。
    SAC_LAYER=0.2,
    HOLE_D=3.4,          # 件上 M3 通孔
    # cap-d: 'insert' = 铜螺母 M3×4 (外径 4.2) 顶面 Φ4.2 盲孔深 INSERT_L + INSERT_CLR = 4.2; 'flange' = cap-c 螺母井 (EAR_* / WELL_* / NUT_HEX_WELL / SAC_LAYER 只在 flange 用)
    NUT_MODE='insert',
    INSERT_D=4.2, INSERT_L=4.0, INSERT_CLR=0.2,   # 用户: 铜螺母 M3×4 孔深统一 4.2 (铜螺母顶齐件顶, 孔底留 0.2)
    INSERT_ENGAGE_MIN=3.0, INSERT_WALL=1.0,       # 螺丝进铜螺母 ≥3; Φ4.2 孔 ↔ 半圆槽 ≥1
    # 紧固件 (同 fasteners_v1_2)
    M3_D=3.2, M3_CB_D=7.0, M3_CB_H=2.0,          # 底盘: Φ3.2 通 + 底面 Φ7×2 沉孔
    SCREW_LENS=(8.0, 10.0, 12.0, 14.0, 20.0),    # BOM 已有 M3 长度 (10 = MOS 压块 mos-b 新增)
    HEAD_D=7.0, HEAD_H=1.5, SHANK_D=3.0,
    NUT_FL_D=7.6, NUT_FL_H=1.0, NUT_AF=5.9, NUT_T=3.7,
    # 合并时的禁区 (底盘上已有的孔/沉孔): [(x, y, r)], 要求本件 Φ7 沉孔与之壁厚 ≥ KEEPOUT_WALL
    KEEPOUT=[(37.5, -37.5, 6.5), (37.5, -62.5, 6.5), (62.5, -62.5, 6.5)],   # 原 M6 网格 Φ13 沉孔 ((62.5,−37.5) coil_drv 已去掉)
    KEEPOUT_WALL=1.0,
    MIN_WALL=1.0,        # 沉孔 ↔ 弧形槽 最小壁
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
def make_cap_clamp(p=None):
    """p: dict 或带属性的对象 (只取 DEFAULTS 里有的键, 缺的用缺省)。返回 dict, 全部为装配系 (全局 Z, 底盘顶 Z0)。"""
    P = dict(DEFAULTS)
    if p is not None:
        src = p if isinstance(p, dict) else vars(p)
        P.update({k: src[k] for k in DEFAULTS if k in src})
    R = P['CAP_D'] / 2
    CLR, T = P['CLR'], P['T_TOP']
    R0, R1 = R + CLR, R + CLR + T
    ZL, DT = P['Z_LIMIT'], P['DISC_T']
    BEAR_Z = -DT + P['M3_CB_H']                           # 螺丝头支承面 −4
    assert abs((P['CAP_Y1'] - P['CAP_Y0']) - P['CAP_L']) < 1e-6, 'CAP_Y1−CAP_Y0 ≠ CAP_L'

    # ---- 槽深: 卡件顶 = 2R − g + CLR + T ≤ Z_LIMIT ----
    g_min = max(0.0, 2 * R + CLR + T - ZL)
    g_max = min(P['GROOVE_MAX'], DT - 3.0)
    if P['CAP_ZC'] is not None:
        g = R - P['CAP_ZC']; g_src = 'CAP_ZC 指定'
    else:
        g_in = P['CAP_GROOVE']
        g = max(g_in, math.ceil(g_min * 20 - 1e-9) / 20)   # 不够深就加深到 0.05 整
        g_src = '输入值' if g == g_in else f'输入 {g_in:g} 不够, 自动加深'
    assert g_min <= g + 1e-9, f'槽深 {g:.2f} < 最小可行 {g_min:.2f} (卡件顶会 > Z_LIMIT)'
    assert g <= g_max + 1e-9, f'槽深 {g:.2f} > 上限 {g_max:.2f} (底盘剩 < 3) —— 减薄 T_TOP / CLR 或放宽 Z_LIMIT'
    ZC = R - g                                            # 电容轴心
    TOP = ZC + R1                                         # 卡件顶
    assert ZC > 0, '电容轴心在 Z0 以下, 半圆鞍形不成立'

    # ---- 螺丝 / 耳高: 尖 ≤ Z_LIMIT, 螺母 (坐耳顶) 吃满 3.7 ⇒ 耳顶 ≤ 尖 − 3.7; 取最短可行 ----
    INS = P['NUT_MODE'] == 'insert'
    assert P['NUT_MODE'] in ('insert', 'flange'), P['NUT_MODE']
    if INS:   # 铜螺母顶齐卡件顶; 尖 ≤ 顶 (不冒头), 进铜螺母 ≥ INSERT_ENGAGE_MIN; 取啮合最大, 再取最短
        IL = P['INSERT_L']; HDEP = IL + P['INSERT_CLR']
        NUT_Z1 = TOP; NUT_Z0 = TOP - IL
        cands = []
        for L in sorted(P['SCREW_LENS']):
            tip = BEAR_Z + L
            eng = min(tip, NUT_Z1) - NUT_Z0
            if tip > min(TOP, ZL) + 1e-9 or eng < P['INSERT_ENGAGE_MIN'] - 1e-9: continue
            cands.append((-eng, L, tip))
        assert cands, '没有可用 M3 长度 (尖 ≤ 卡件顶 且进铜螺母 ≥ INSERT_ENGAGE_MIN)'
        _, SCREW_L, TIP = min(cands)
        EAR_TOP = TOP - HDEP                              # Φ4.2 盲孔底 (兼容旧键名 ear_top)
    else:
        choice = None
        for L in sorted(P['SCREW_LENS']):
            tip = BEAR_Z + L
            if tip > ZL + 1e-9: continue
            ear = min(P['EAR_T'], tip - P['NUT_T'])
            if ear >= P['EAR_MIN'] - 1e-9 and ear + P['NUT_T'] <= ZL + 1e-9:
                choice = (L, tip, ear); break
        assert choice, '没有可用的 M3 长度 (尖 ≤ Z_LIMIT 且耳厚 ≥ EAR_MIN)'
        SCREW_L, TIP, EAR_TOP = choice
        NUT_Z0, NUT_Z1 = EAR_TOP, EAR_TOP + P['NUT_T']
    ENGAGE = min(TIP, NUT_Z1) - NUT_Z0

    # ---- 平面位置 ----
    CX = P['CAP_CX']
    YM = (P['CAP_Y0'] + P['CAP_Y1']) / 2 + P['CLAMP_Y_OFF']
    YA, YB = YM - P['CLAMP_LEN'] / 2, YM + P['CLAMP_LEN'] / 2
    HX = P['PITCH'] / 2
    WR = P['INSERT_D'] / 2 if INS else P['WELL_D'] / 2
    WWALL = P['INSERT_WALL'] if INS else P['WELL_WALL']
    _ghw = math.sqrt(R0 ** 2 - (EAR_TOP - ZC) ** 2) if EAR_TOP > ZC else R0     # 井底高度处半圆槽半宽
    while HX - WR - _ghw < WWALL - 1e-9: HX += 0.25                  # 井壁不够 ⇒ 孔距外拉
    PITCH_USED = 2 * HX
    HOLES = [(CX - HX, YM), (CX + HX, YM)]
    XO = max(HX + P['EAR_OUT'], HX + WR + P['OUT_WALL'])  # 外形 X 半宽
    assert INS or P['CLAMP_LEN'] >= P['NUT_FL_D'] - 1e-9, '卡件比法兰短, 法兰底支承不全'

    # ---- 卡件 (装配姿态) ----
    # 方案 2 (用户 11-12 夜, 参考 XT60 压块): 实心长方体 Z0..TOP, 底面半圆槽 R0 (槽心 = 电容轴), 2×Φ3.4 通 + 顶面 Φ8.2 螺母井到 EAR_TOP
    cc = cut(box(CX - XO, YA, 0, CX + XO, YB, TOP),
             ycyl(CX, ZC, 2 * R0, YA - 1, YB + 1), box(CX - R0, YA - 1, -1, CX + R0, YB + 1, ZC))
    for x, y in HOLES:
        cc = cut(cc, cyl(x, y, P['HOLE_D'], -1, TOP + 1))
    HEXW = P['NUT_HEX_WELL'] and not INS
    Z_STEP = NUT_Z1 - P['WELL_FL_H'] if HEXW else EAR_TOP          # 六角段顶 / 圆段底
    def well(x, y):
        if INS: return cyl(x, y, P['INSERT_D'], EAR_TOP, TOP + 1)          # 铜螺母 Φ4.2 盲孔
        w = cyl(x, y, P['WELL_D'], Z_STEP, TOP + 1)
        return fuse(w, hexprism(x, y, P['WELL_AF'], EAR_TOP, Z_STEP + 0.01)) if HEXW else w
    wells = [well(x, y) for x, y in HOLES]
    for w in wells: cc = cut(cc, w)
    groove_solid = fuse(ycyl(CX, ZC, 2 * R0, YA - 1, YB + 1), box(CX - R0, YA - 1, -1, CX + R0, YB + 1, ZC))
    clamp = clean(cc)
    SAC = 0.0 if INS else P['SAC_LAYER']
    clamp_sac = clean(fuse(clamp, *[cyl(x, y, P['HOLE_D'] + 0.02, EAR_TOP - SAC, EAR_TOP) for x, y in HOLES])) if SAC > 0 else clamp

    # ---- 电容 / 紧固件 (校核 + 预览) ----
    cap = ycyl(CX, ZC, P['CAP_D'], P['CAP_Y0'], P['CAP_Y1'])

    def screw(x, y):
        return fuse(cyl(x, y, P['HEAD_D'], BEAR_Z - P['HEAD_H'], BEAR_Z), cyl(x, y, P['SHANK_D'], BEAR_Z, TIP))

    def nut(x, y):
        if INS:    # 铜螺母 Φ4.2×4, 中心 Φ3 (同 fasteners_v1_2.insert)
            return cut(cyl(x, y, P['INSERT_D'], NUT_Z0, NUT_Z1), cyl(x, y, P['SHANK_D'], NUT_Z0 - 1, NUT_Z1 + 1))
        if HEXW:   # 法兰朝上: 六角 NUT_Z0..NUT_Z1−FL_H, 法兰在上
            body = fuse(hexprism(x, y, P['NUT_AF'], NUT_Z0, NUT_Z1 - P['NUT_FL_H']), cyl(x, y, P['NUT_FL_D'], NUT_Z1 - P['NUT_FL_H'], NUT_Z1))
        else:
            body = fuse(cyl(x, y, P['NUT_FL_D'], NUT_Z0, NUT_Z0 + P['NUT_FL_H']), hexprism(x, y, P['NUT_AF'], NUT_Z0 + P['NUT_FL_H'], NUT_Z1))
        return cut(body,
                   cyl(x, y, P['SHANK_D'], NUT_Z0 - 1, NUT_Z1 + 1))
    screws = [screw(x, y) for x, y in HOLES]
    nuts = [nut(x, y) for x, y in HOLES]

    # ---- 底盘切口: 弧形槽 + 2×(Φ3.2 通 + 底面 Φ7×2) ----
    RT = R + P['TROUGH_CLR']
    TZ = -g + RT                                          # 槽圆心 (槽底 = 电容底 −g)
    trough = common(ycyl(CX, TZ, 2 * RT, P['CAP_Y0'] - P['TROUGH_EXT'], P['CAP_Y1'] + P['TROUGH_EXT']),
                    box(CX - RT - 1, P['CAP_Y0'] - 5, -DT - 1, CX + RT + 1, P['CAP_Y1'] + 5, 1))
    thru = [cyl(x, y, P['M3_D'], -DT - 1, 1) for x, y in HOLES]
    cbs = [cyl(x, y, P['M3_CB_D'], -DT - 1, BEAR_Z) for x, y in HOLES]
    disc_cuts = [trough] + thru + cbs
    TROUGH_HW = math.sqrt(max(RT ** 2 - (TZ) ** 2, 0)) if TZ > 0 else RT      # 槽顶面开口半宽

    # ---- 校核 ----
    pad = 3
    bx0, bx1 = CX - XO - pad, CX + XO + pad
    by0, by1 = min(YA, P['CAP_Y0']) - pad, max(YB, P['CAP_Y1']) + pad
    disc_blk = cut(box(bx0, by0, -DT, bx1, by1, 0), *disc_cuts)              # 局部底盘块
    C = {}
    C['clamp_valid'] = BRepCheck_Analyzer(clamp).IsValid()
    C['clamp_solids'] = nsolids(clamp)
    C['iv_clamp_cap'] = iv(clamp, cap)
    C['gap_clamp_cap'] = dist(clamp, cap)
    C['iv_clamp_disc'] = iv(clamp, disc_blk)
    C['iv_cap_disc'] = iv(cap, disc_blk)
    C['iv_clamp_screw'] = sum(iv(clamp, s) for s in screws)
    C['iv_clamp_nut'] = sum(iv(clamp, n) for n in nuts)
    C['iv_disc_screw'] = sum(iv(disc_blk, s) for s in screws)
    C['gap_nut_saddle'] = min(dist(n, common(clamp, box(x - 10, YA - 1, NUT_Z0 + 1e-3, x + 10, YB + 1, TOP + 1))) for n, (x, _) in zip(nuts, HOLES))  # 螺母 ↔ 井壁径向
    C['wall_well_groove'] = min(dist(w, groove_solid) for w in wells)
    C['wall_well_xend'] = XO - HX - WR
    C['wall_well_yend'] = min(YM - YA, YB - YM) - WR
    C['pitch_used'] = PITCH_USED; C['width'] = 2 * XO
    C['nut_recess'] = TOP - NUT_Z1
    # 法兰底全支承: 法兰底下 0.01 薄片 (去孔) 与卡件的重合率
    fl_ring = cut(cyl(0, 0, P['INSERT_D'], -0.01, 0) if INS else hexprism(0, 0, P['NUT_AF'], -0.01, 0) if HEXW else cyl(0, 0, P['NUT_FL_D'], -0.01, 0), cyl(0, 0, P['HOLE_D'], -1, 1))
    sup = []
    for x, y in HOLES:
        t = gp_Trsf(); t.SetTranslation(gp_Vec(x, y, EAR_TOP if INS else NUT_Z0))   # INS: 孔底台阶 (Φ4.2→Φ3.4) 有实体
        r = xf(fl_ring, t); sup.append(iv(r, clamp) / vol(r))
    C['nut_support'] = min(sup)
    if HEXW:   # 防转: 螺母转 5° 必须撞六角井
        rot = gp_Trsf(); rot.SetRotation(gp_Ax1(gp_Pnt(*HOLES[0], 0), gp_Dir(0, 0, 1)), math.radians(5))
        C['antirot_iv_5deg'] = iv(xf(nuts[0], rot), clamp)
        C['hex_corner_wall_groove'] = min(dist(hexprism(x, y, P['WELL_AF'], EAR_TOP, Z_STEP), groove_solid) for x, y in HOLES)
        C['hex_corner_wall_end'] = min(XO - P['PITCH'] / 2 - P['WELL_AF'] / math.sqrt(3), min(YM - YA, YB - YM) - P['WELL_AF'] / math.sqrt(3))
        assert C['antirot_iv_5deg'] > 1e-3, '六角井不防转'
        assert min(C['hex_corner_wall_groove'], C['hex_corner_wall_end']) >= 1.0 - 1e-6, '六角角壁 <1'
    C['nut_mode'] = P['NUT_MODE']
    C['nut_well'] = (f'铜螺母孔 Φ{P["INSERT_D"]:g} Z{EAR_TOP:g}..{TOP:g} (深 {TOP - EAR_TOP:g})' if INS else f'六角 AF{P["WELL_AF"]:g} Z{EAR_TOP:g}..{Z_STEP:g} + Φ{P["WELL_D"]:g} Z{Z_STEP:g}..顶 (法兰朝上)' if HEXW else f'全圆 Φ{P["WELL_D"]:g}')
    C['sac_layer'] = SAC
    C['wall_cb_trough'] = min(dist(cb, trough) for cb in cbs)
    C['wall_hole_trough'] = min(dist(h, trough) for h in thru)
    C['disc_under_trough'] = DT - g
    C['keepout_wall'] = min((math.hypot(x - a, y - b) - P['M3_CB_D'] / 2 - r for x, y in HOLES for a, b, r in P['KEEPOUT']), default=99)
    C['top'] = TOP; C['nut_top'] = NUT_Z1; C['tip'] = TIP; C['engage'] = ENGAGE

    assert C['clamp_valid'] and C['clamp_solids'] == 1, '卡件不是单个有效实体'
    assert C['iv_clamp_cap'] < EPS_V and abs(C['gap_clamp_cap'] - CLR) < 1e-3, ('卡件-电容', C['iv_clamp_cap'], C['gap_clamp_cap'])
    assert C['iv_clamp_disc'] < EPS_V, ('卡件-底盘干涉', C['iv_clamp_disc'])
    assert C['iv_cap_disc'] < EPS_V, ('电容-底盘干涉', C['iv_cap_disc'])
    assert C['iv_clamp_screw'] < EPS_V and C['iv_clamp_nut'] < EPS_V, '螺丝/螺母碰卡件'
    assert C['iv_disc_screw'] < EPS_V, '螺丝碰底盘'
    _g = 0.0 if INS else min((P['WELL_AF'] - P['NUT_AF']) / 2, (P['WELL_D'] - P['NUT_FL_D']) / 2) if P['NUT_HEX_WELL'] else 0.25
    assert C['gap_nut_saddle'] >= _g - 1e-6, (f'螺母离井壁 <{_g}', C['gap_nut_saddle'])
    assert C['wall_well_groove'] >= WWALL - 1e-6, ('螺母井离半圆槽太近', C['wall_well_groove'])
    assert TIP <= TOP + 1e-9, '螺尖冒出卡件顶面'
    if C['wall_well_yend'] < 1.0: print(f"  [注意] 螺母井离 Y 端面壁 {C['wall_well_yend']:.2f} (CLAMP_LEN {P['CLAMP_LEN']:g} / 井 Φ{P['WELL_D']:g})")
    assert C['nut_support'] > 0.999, ('法兰底支承不全', C['nut_support'])
    assert TOP <= ZL + 1e-9 and NUT_Z1 <= ZL + 1e-9 and TIP <= ZL + 1e-9, ('超高', TOP, NUT_Z1, TIP)
    if INS:
        assert ENGAGE >= P['INSERT_ENGAGE_MIN'] - 1e-9, ('铜螺母啮合不足', ENGAGE)
        assert EAR_TOP > 0, '铜螺母孔底低于 Z0'
    else:
        assert ENGAGE >= P['NUT_T'] - 1e-9, '螺母没吃满'
    assert C['wall_cb_trough'] >= P['MIN_WALL'] - 1e-6 and C['wall_hole_trough'] >= P['MIN_WALL'] - 1e-6, ('孔/沉孔离槽太近', C['wall_cb_trough'], C['wall_hole_trough'])
    assert C['disc_under_trough'] >= 3.0 - 1e-9
    if C['keepout_wall'] < P['KEEPOUT_WALL'] - 1e-6:
        print(f"  [警告] M3 沉孔离禁区 (KEEPOUT) 壁 {C['keepout_wall']:.2f} < {P['KEEPOUT_WALL']}")

    # ---- 打印姿态: 绕 X 转 +90° (Y→Z), −Y 端面 (YA) 贴床, x 以电容轴为 0 ----
    tr = gp_Trsf(); tr.SetRotation(gp_Ax1(gp_Pnt(CX, YM, TOP / 2), gp_Dir(1, 0, 0)), math.radians(180))   # 倒扣: 顶面贴床
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(-CX, -YM, -TOP / 2 + TOP / 2)); tp = t2.Multiplied(tr)
    clamp_print = xf(clamp_sac, tp)
    pb = bbox(clamp_print)
    assert abs(pb[2]) < 1e-6, pb
    C['overhang'] = overhangs(clamp_print)          # 打印姿态下朝下且不在床面的面: [(类型, 面积, z)]

    return dict(clamp=clamp, clamp_sac=clamp_sac, clamp_print=clamp_print, print_trsf=tp, cap=cap, screws=screws, nuts=nuts, inserts=nuts if INS else [], nut_mode=P['NUT_MODE'],
                disc_cuts=disc_cuts, disc_cut_labels=['电容弧形槽'] + [f'M3通{i}' for i in range(2)] + [f'M3沉孔{i}' for i in range(2)],
                holes=HOLES, screw_len=SCREW_L, nut_z0=NUT_Z0, nut_z1=NUT_Z1, insert_z0=NUT_Z0 if INS else None, insert_z1=NUT_Z1 if INS else None, hole_depth=TOP - EAR_TOP, tip=TIP, engage=ENGAGE,
                ear_top=EAR_TOP, top=TOP, cap_zc=ZC, groove=g, groove_min=g_min, groove_max=g_max, groove_src=g_src,
                bear_z=BEAR_Z, r0=R0, r1=R1, y_span=(YA, YB), x_span=(CX - XO, CX + XO),
                trough=dict(center_z=TZ, r=RT, top_halfwidth=TROUGH_HW, y=(P['CAP_Y0'] - P['TROUGH_EXT'], P['CAP_Y1'] + P['TROUGH_EXT'])),
                checks=C, params=P, disc_block=disc_blk, volume=vol(clamp))


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
    P = r['params']; INS = r['nut_mode'] == 'insert'; CX = P['CAP_CX']; YM = r['holes'][0][1]
    fig = plt.figure(figsize=(18, 10))

    # 1) 3D 装配
    ax = fig.add_subplot(2, 3, 1, projection='3d')
    blk = r['disc_block']
    for sh, col, a in ((blk, '#555555', 0.35), (r['cap'], '#1f3b73', 0.9), (r['clamp'], '#e08a1e', 0.95)) + \
            tuple((s, '#999999', 1) for s in r['screws']) + tuple((n, '#bbbbbb', 1) for n in r['nuts']):
        pc = Poly3DCollection(tris(sh), facecolor=col, edgecolor='none', alpha=a); ax.add_collection3d(pc)
    b = bbox(blk)
    ax.set_xlim(b[0], b[3]); ax.set_ylim(b[1], b[4]); ax.set_zlim(-8, 12)
    ax.set_box_aspect((b[3] - b[0], b[4] - b[1], 20)); ax.view_init(25, -60)
    ax.set_title('装配 (局部底盘块 + 电容 + 卡件 + M3)'); ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')

    # 2) 3D 打印姿态
    ax = fig.add_subplot(2, 3, 4, projection='3d')
    ax.add_collection3d(Poly3DCollection(tris(r['clamp_print']), facecolor='#e08a1e', edgecolor='#00000020', alpha=1))
    b = bbox(r['clamp_print'])
    ax.set_xlim(b[0] - 2, b[3] + 2); ax.set_ylim(b[1] - 2, b[4] + 2); ax.set_zlim(0, b[5] + 2)
    ax.set_box_aspect((b[3] - b[0] + 4, b[4] - b[1] + 4, b[5] + 2)); ax.view_init(30, -50)
    ax.set_title(f'打印姿态: 倒扣, 顶面贴床 (槽口朝上)\n{b[3]-b[0]:.1f}×{b[4]-b[1]:.1f}×{b[5]:.1f}  体积 {r["volume"]:.0f} mm³')

    # 3) 端视剖面 (过孔心 Y)
    ax = fig.add_subplot(1, 3, (2, 3))
    pln = gp_Pln(gp_Pnt(0, YM, 0), gp_Dir(0, 1, 0))
    items = [(blk, '#555555', '底盘 (槽+沉孔)'), (r['cap'], '#1f3b73', '电容 Φ10'), (r['clamp'], '#e08a1e', '卡件')] + \
            [(s, '#777777', 'M3' if i == 0 else None) for i, s in enumerate(r['screws'])] + \
            [(n, '#2a9d8f', ('铜螺母 M3×4' if INS else '法兰螺母') if i == 0 else None) for i, n in enumerate(r['nuts'])]
    for sh, col, lab in items:
        first = True
        for pl in section_polylines(sh, pln):
            xs = [q[0] for q in pl]; zs = [q[2] for q in pl]
            ax.plot(xs, zs, color=col, lw=1.6, label=lab if first else None); first = False
    x0, x1 = r['x_span']
    ax.axhline(P['STATOR_Z0'], color='r', lw=1, ls='-'); ax.text(x0 - 3, P['STATOR_Z0'] + 0.1, f'定子盘底 Z{P["STATOR_Z0"]:g}', color='r', fontsize=9)
    ax.axhline(P['Z_LIMIT'], color='r', lw=0.8, ls='--'); ax.text(x0 - 3, P['Z_LIMIT'] - 0.45, f'Z_LIMIT {P["Z_LIMIT"]:g}', color='r', fontsize=9)
    # Z 链标注
    hx = r['holes'][1][0]
    chain = [(r['bear_z'], '头支承面'), (-r['groove'], '槽底 = 电容底'), (0, '底盘顶'), (r['cap_zc'], '电容轴'),
             (r['ear_top'], 'Φ4.2 孔底 = 铜螺母底' if INS else '井底 = 螺母底'), (r['nut_z1'], '铜螺母顶 = 卡件顶' if INS else '螺母顶'), (r['tip'], f'M3×{r["screw_len"]:g} 尖'), (r['top'], '卡件顶')]
    xa = x1 + 4
    zt_prev = None
    for z, t in sorted(chain, key=lambda c: c[0]):
        zt = z if zt_prev is None else max(z, zt_prev + 0.6); zt_prev = zt
        ax.plot([x1 + 0.5, xa - 1, xa], [z, z, zt], color='k', lw=0.5, ls=':')
        ax.text(xa + 0.3, zt, f'Z{z:+.2f}  {t}', va='center', fontsize=9)
    ax.annotate('', (hx + 5, r['nut_z0']), (hx + 5, r['nut_z1']), arrowprops=dict(arrowstyle='<->', lw=0.8))
    ax.text(hx + 5.3, (r['nut_z0'] + r['nut_z1']) / 2, f'啮合 {r["engage"]:.1f}', fontsize=8, va='center')
    C = r['checks']
    txt = (f'槽深 {r["groove"]:.2f} ({r["groove_src"]}; 最小可行 {r["groove_min"]:.2f}, 上限 {r["groove_max"]:.2f}) 底盘剩 {C["disc_under_trough"]:.2f}\n'
           f'槽 R{r["r0"]:.2f} (间隙 {C["gap_clamp_cap"]:.3f}); 顶 {r["top"]:.2f}, {"铜螺母" if INS else "螺母"}顶低于顶面 {C["nut_recess"]:.2f}, 卡件长 {P["CLAMP_LEN"]:g} @ y {r["y_span"][0]:.1f}..{r["y_span"][1]:.1f}\n'
           f'宽 {C["width"]:.2f} 孔距 {C["pitch_used"]:.2f}; {C["nut_well"]}; 孔/井-槽壁 {C["wall_well_groove"]:.2f} / -X端 {C["wall_well_xend"]:.2f} / -Y端 {C["wall_well_yend"]:.2f}; 螺母离井壁 {C["gap_nut_saddle"]:.2f}\n'
           f' 沉孔-槽壁 {C["wall_cb_trough"]:.2f}; 通孔-槽壁 {C["wall_hole_trough"]:.2f}; 沉孔-禁区壁 {C["keepout_wall"]:.2f}\n'
           f'干涉体积: 卡件-电容 {C["iv_clamp_cap"]:.1e}, 卡件-底盘 {C["iv_clamp_disc"]:.1e}, 卡件-螺丝/螺母 {C["iv_clamp_screw"] + C["iv_clamp_nut"]:.1e}')
    ax.text(0.01, 0.01, txt, transform=ax.transAxes, fontsize=8.5, va='bottom', family=plt.rcParams['font.family'],
            bbox=dict(fc='white', ec='#ccc'))
    ax.set_xlim(x0 - 4, xa + 22); ax.set_ylim(-11, 11.5); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_xlabel('X (装配系)'); ax.set_ylabel('Z')
    ax.set_title(f'端视剖面 y = {YM:.2f} (过两孔心)')
    ax.legend(loc='lower right', fontsize=8)
    fig.suptitle(f'cap_clamp_v1_2 电容半圆卡件 ({VERSION})', fontsize=14)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def main():
    r = make_cap_clamp()
    MODEL_DIR.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    write_stl(r['clamp_print'], MODEL_DIR / 'cap_clamp_v1_2.stl')
    write_step(r['clamp_print'], MODEL_DIR / 'cap_clamp_v1_2.step')
    preview(r, OUT / 'cap_clamp_v1_2_preview.png')
    C, P = r['checks'], r['params']
    b = bbox(r['clamp']); pb = bbox(r['clamp_print'])
    print(f'cap_clamp_v1_2 {VERSION}')
    print(f'  装配 bbox x {b[0]:.2f}..{b[3]:.2f}  y {b[1]:.2f}..{b[4]:.2f}  z {b[2]:.2f}..{b[5]:.2f}; 体积 {r["volume"]:.1f}')
    print(f'  打印 bbox {pb[3]-pb[0]:.2f} × {pb[4]-pb[1]:.2f} × {pb[5]-pb[2]:.2f} (倒扣, 顶面 z=0 贴床)')
    print(f'  槽深 {r["groove"]:.2f} [{r["groove_src"]}] 最小可行 {r["groove_min"]:.2f} 上限 {r["groove_max"]:.2f}; 电容轴 Z{r["cap_zc"]:.2f}; '
          f'槽 R{r["trough"]["r"]:.2f} 圆心 Z{r["trough"]["center_z"]:.2f} 顶面开口 ±{r["trough"]["top_halfwidth"]:.2f}')
    print(f'  Z 链: 头支承 {r["bear_z"]:g} / 槽底 {-r["groove"]:g} / 耳顶 {r["ear_top"]:g} / 螺母 {r["nut_z0"]:g}..{r["nut_z1"]:g} / '
          f'M3×{r["screw_len"]:g} 尖 {r["tip"]:g} / 卡件顶 {r["top"]:.2f} (≤ {P["Z_LIMIT"]:g}); 啮合 {r["engage"]:.2f}')
    print(f'  孔 {[(round(x, 2), round(y, 2)) for x, y in r["holes"]]}')
    for k, v in C.items():
        print(f'  {k:22s} {v if not isinstance(v, float) else round(v, 4)}')
    print('  STL/STEP ->', MODEL_DIR, '; 预览 ->', OUT / 'cap_clamp_v1_2_preview.png')


if __name__ == '__main__':
    main()
