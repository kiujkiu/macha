"""
V1.2 打印件 A3 工程图 (2026-11-12), 画法同 v1.0/models/build_drawings_v1_0.py (共用 drawing_v1_0.draw)。
几何取 models/<件>/<件>.stl (装配坐标, 先跑 export_3mf_v1_2.py), 孔位/尺寸全部 import 自 build_v1_2 —— 不手抄数字。
    cd v1.2/scripts && ../../.venv/bin/python build_drawings_v1_2.py [件名 ...]
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V12 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V12.parent / "v1.0" / "models"))
from drawing_v1_2 import draw, F  # noqa: E402
import build_v1_2 as B  # noqa: E402
from OCP.gp import gp_Pnt  # noqa: E402

DATE = "2026-11-12"
M = V12 / "models"


def ang(p):
    return math.degrees(math.atan2(p[1], p[0])) % 360


def xy(pts, per=2):
    s = [f"({x:.2f},{y:.2f})" for x, y in pts]
    return "\n".join("  ".join(s[i:i + per]) for i in range(0, len(s), per))


def ring_txt(pts):
    r = math.hypot(*pts[0])
    a = sorted(ang(p) for p in pts)
    return f"r{F(r)} @ " + "/".join(F(round(x, 1)) for x in a) + "°"


_CYL_CACHE = {}


def cyls(shape):
    """B-rep 里全部圆柱面 → [(直径, x, y, z0, z1)] (几何实测; V1.0 STEP 带来的孔 build 里没有变量, 从这里读)。"""
    k = id(shape)
    if k not in _CYL_CACHE:
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_FACE
        from OCP.TopoDS import TopoDS
        from OCP.BRepAdaptor import BRepAdaptor_Surface
        from OCP.GeomAbs import GeomAbs_Cylinder
        out, e = [], TopExp_Explorer(shape, TopAbs_FACE)
        while e.More():
            f = TopoDS.Face(e.Current())
            a = BRepAdaptor_Surface(f)
            if a.GetType() == GeomAbs_Cylinder:
                c = a.Cylinder(); p = c.Location(); bb = B.bbox(f)
                out.append((round(2 * c.Radius(), 2), round(p.X(), 2), round(p.Y(), 2), round(bb[2], 2), round(bb[5], 2)))
            e.Next()
        _CYL_CACHE[k] = out
    return _CYL_CACHE[k]


def cyl_at(shape, d, pt=None, centered=False, tol=0.05):
    """直径 d 的圆柱面 (pt: 只取轴心在 pt 的; centered: 只取轴心在原点的), 同轴分段合并 → [(x, y, z0, z1)]。"""
    acc = {}
    for dd, x, y, za, zb in cyls(shape):
        if abs(dd - d) > tol:
            continue
        if centered and math.hypot(x, y) > 0.1:
            continue
        if pt is not None and math.hypot(x - pt[0], y - pt[1]) > 0.1:
            continue
        if not centered and pt is None and math.hypot(x, y) < 0.1:
            continue
        kk = (round(x, 1), round(y, 1))
        z = acc.get(kk, (x, y, za, zb))
        acc[kk] = (z[0], z[1], min(z[2], za), max(z[3], zb))
    return sorted(acc.values(), key=lambda v: (round(math.degrees(math.atan2(v[1], v[0])) % 360, 1), math.hypot(v[0], v[1])))


def by_r(rows, n=None):
    """按半径分组 → {r: [rows]} (n: 只留个数 = n 的组)。"""
    g = {}
    for r_ in rows:
        g.setdefault(round(math.hypot(r_[0], r_[1]), 1), []).append(r_)
    return {k: v for k, v in g.items() if n is None or len(v) == n}


def hole_segs(shape, pt, dmax=8.0):
    """pt 处同轴圆柱段 (实测, 自下而上) → [(直径, z0, z1)]。"""
    return sorted(((d, z0, z1) for d, x, y, z0, z1 in cyls(shape) if d <= dmax and math.hypot(x - pt[0], y - pt[1]) < 0.1), key=lambda v: (v[1], v[2]))


def hole_txt(shape, pt):
    """孔段文字 (实测): 'Φ6 Z28–30 / Φ3.4 Z30–32' (自下而上, 同径相邻段合并)。"""
    out = []
    for d, z0, z1 in hole_segs(shape, pt):
        if out and abs(out[-1][0] - d) < 0.05 and z0 <= out[-1][2] + 0.05:
            out[-1] = (d, out[-1][1], max(out[-1][2], z1))
        else:
            out.append((d, z0, z1))
    return " / ".join(f"Φ{F(d)} Z{F(z0)}–{F(z1)}" for d, z0, z1 in out)


def hole_det(shape, pt, tag_title, W=4.0, z=None):
    """孔详图 (free, 实测各段高度标在右侧; z 给定时窗口取 z, 用来带出凸台)。"""
    sg = hole_segs(shape, pt)
    za, zb = z or (min(v[1] for v in sg), max(v[2] for v in sg))
    zs = sorted({round(v, 3) for d, z0, z1 in sg for v in (z0, z1)})
    return dict(kind="free", z=(za, zb), pt=pt, W=W, title=tag_title,
                zd=[(a, b, F(b - a), 4 * (i % 2)) for i, (a, b) in enumerate(zip(zs[:-1], zs[1:]))],
                ud=[(-d / 2, d / 2, f"Φ{F(d)}", 4 * i) for i, d in enumerate(sorted({v[0] for v in sg}))])


def vd(z0, z1, u, off, label):     # 主视 (X-Z) 竖直尺寸, 尺寸线放视图右侧 off
    return dict(view="front", kind="v", p0=(u, z0), p1=(u, z1), off=off, label=label)


SPECS = []
COMMON = dict(date=DATE, proj="V1.2")
ORIG = "原点 = 轴心, Z = 装配高度 (底盘顶面 Z0); 图示为装配姿态。"

# ---------------- base_disc_v1_2_gf (11-18 玻纤板方案) ----------------
FS_L = dict(MOTOR=10.0, RING=14.0, SH=16.0, C=25.0, BD=12.0, XT=22.0)   # 同 fasteners_v1_2.py L_* (改一处两处都改)
BH = [gp_Pnt(x, y, 0).Transformed(B.BT) for x, y in B.BHOLES]
BH = [(p.X(), p.Y()) for p in BH]
_rl = B.RELIEFS[0]
_rp = gp_Pnt((_rl[0] + _rl[1]) / 2, (_rl[2] + _rl[3]) / 2, 0).Transformed(B.BT)
grid_np = [p for p in B.EXTRA if p not in B.POSTS]
ZD = (-B.DISC_T, -B.FR4_T)
cb6 = f"Φ{F(B.M6_D)} 通 + 底面 Φ{F(B.CB_D)}×{F(B.CB_H)} 沉孔"
cb3 = f"Φ{F(B.M3_D)} 通 + 底面 Φ{F(B.M3_CB_D)}×{F(B.M3_CB_H)} 沉孔"
ins = f"Φ3.2 通 + 底面 Φ{F(B.INS_HOLE_D)}×{F(B.INS_HOLE_H)} 铜螺母孔 (M3×4 铜螺母齐底面)"
SPECS.append(dict(
    code="base_disc_v1_2_gf" + ("_old" if B.BOARD_OLD else ""), shape=B.disc_print, short=f"打印底盘 Φ{F(B.DISC_D)}×{F(B.PRINT_T)}" + (" 旧控制板位" if B.BOARD_OLD else ""), qty="1",
    title=f"打印底盘 Φ{F(B.DISC_D)}×{F(B.PRINT_T)} (玻纤板方案, 上压 FR4 {F(B.FR4_T)} 厚 base_fr4_v1_2)",
    subtitle=f"Z{F(-B.DISC_T)}..{F(-B.FR4_T)}; 沉孔全部开在底面; " + ("顶面平 (贴玻纤板底), 顶面槽 (电容/让位/盘心) 都在玻纤板上做通孔" if B.FR4_T >= 3 else f"顶面槽 (电容/让位/盘心 Φ12) 总深 3 = 玻纤板 {F(B.FR4_T)} + 本件顶面 {F(3 - B.FR4_T)}"),
    orient="顶面 (贴玻纤板那面) 贴床",
    phi=[24, 2 * B.R_SCREW, 2 * B.STATOR_R, (2 * B.RING_M3_XY, f"{F(2 * B.RING_M3_XY)} (方)"), 2 * B.SH_R, B.DISC_D],
    det_h=38.0,
    sec=dict(ang=45, auto_r=False, zd=[ZD], rd=[(0, B.STATOR_R), (0, math.hypot(B.RING_M3_XY, B.RING_M3_XY)), (0, B.SH_R)]),
    holes=[
        dict(tag="A", pts=B.POSTS, spec=cb6 + " (外圈固定孔)", where="R95.2 ×4 " + xy(B.POSTS) + "  锁台面/扩展用",
             det=dict(kind="cb", d=B.M6_D, D=B.CB_D, h=B.CB_H, side="bot", z=ZD, pt=B.POSTS[0], title="M6 沉孔")),
    ] + ([dict(tag="B", pts=grid_np, spec=cb6 + "  同详图 A", where=f"原 M6 网格 节距 25")] if grid_np else []) + [
        dict(tag="C", pts=B.XT_GHOLES_DISC, spec=cb3 + "  同详图 D (XT60 压块)", where=xy(B.XT_GHOLES_DISC) + f"  M3×{F(FS_L['XT'])} 往上, 法兰螺母坐压块顶", lab_off=(-2.4, 2.4)),
        dict(tag="D", pts=B.MOTOR_HOLES, spec=cb3 + " (电机)", where=f"对角 {F(2 * B.STATOR_R)}  M3×{F(FS_L['MOTOR'])} (待电机螺孔深度确认)",
             det=dict(kind="cb", d=B.M3_D, D=B.M3_CB_D, h=B.M3_CB_H, side="bot", z=ZD, pt=B.MOTOR_HOLES[0], title="M3 沉孔 (C/D/E/F 同, 超薄头齐底面)")),
        dict(tag="E", pts=B.RING_M3, spec=cb3 + "  同详图 D (线圈环四角)", where=f"(±{F(B.RING_M3_XY)}, ±{F(B.RING_M3_XY)})  M3×{F(FS_L['RING'])}, 法兰螺母压四角顶"),
        dict(tag="F", pts=B.SH_M6, spec=cb3 + "  同详图 D (下罩)", where=ring_txt(B.SH_M6) + f"  M3×{F(FS_L['SH'])}, 法兰螺母压三角块顶"),
        dict(tag="G", pts=B.FLANGE_SCREWS, spec=f"Φ3.2 通 + 底面 Φ{F(B.G_NUT_D)}×{F(B.G_NUT_H)} 沉孔 (M3 法兰螺母, 法兰朝下齐底面) (线圈环/定子盘)", where=ring_txt(B.FLANGE_SCREWS) + f"  M3×{F(FS_L['C'])} 从上往下",
             det=dict(kind="cb", d=3.2, D=B.G_NUT_D, h=B.G_NUT_H, side="bot", z=ZD, pt=B.FLANGE_SCREWS[0], title=f"法兰螺母沉孔 G (Φ{F(B.G_NUT_D)}×{F(B.G_NUT_H)})")),
        dict(tag="H", pts=BH, spec=cb3 + "  同详图 D (控制板)", where=xy(BH) + f"  M3×{F(FS_L['BD'])} 往上, 法兰螺母坐板顶"),
        *([] if not B.CD.ALL_HOLES else [
        dict(tag="L", pts=B.CD.ALL_HOLES, spec=cb3 + "  同详图 D (线圈驱动板: MOS 压块 2 + 电容卡件 2)",
             where=xy(B.CD.ALL_HOLES, 2) + f"  MOS M3×{F(B.CD.MC_SCREW_L)} / 电容 M3×{F(B.CD.CC_SCREW_L)} 往上, 进件顶热压 M3×4 铜螺母")]),
        dict(tag="W", pts=B.MW_M3, spec=cb3 + "  同详图 D (MR30 座 2 + 电机线夹 2)",
             where=xy(B.MW_M3, 2) + f"  MR30 座 M3×14 / 线夹 M3×12 往上, 进件顶热压 M3×4 铜螺母"),
        dict(tag="K", pts=B.KEY_M3, spec=cb3 + "  同详图 D (按键支架脚)", where=xy(B.KEY_M3) + f"  M3×{F(B.KEY['params']['FOOT_SCREW_L'])} 往上, 法兰螺母坐脚顶"),
    ],
    date="2026-11-25",
    notes=[f"11-25: 厚 5 → {F(B.PRINT_T)}, 配 FR4 {F(B.FR4_T)} 厚 (底 Z{F(-B.DISC_T)}); G 法兰螺母沉孔 3.7 → {F(B.G_NUT_H)}, 窝顶剩 {F(B.PRINT_T - B.G_NUT_H)}; 螺丝长度不变 (盘底往上的尖上移 0.5)",
           ("控制板老位置版: 配 11-25 之前的 FR4 (控制板没外挪)" if B.BOARD_OLD else "11-25: 控制板整组 (H 4 孔 / 散热片槽 / 排针槽) 往 +Y (向外) 挪 1, 配 11-25 新 FR4"),
           f"11-18 玻纤板方案: 底座 = 本件 {F(B.PRINT_T)} + FR4 {F(B.FR4_T)} (板顶 Z0, 上面所有件 Z 不变)",
           f"盘底往上的 M3 沉孔 Φ7×{F(B.M3_CB_H)} (超薄头齐底面), 支承 Z{F(-B.DISC_T + B.M3_CB_H)}: 螺丝长度见孔表",
           f"通槽: 散热片 20×40 ×2 (控制板 1; 线圈驱动板 x{F(B.CD.SINK_X0)}..{F(B.CD.SINK_X1)} y{F(B.CD.SINK_Y0)}..{F(B.CD.SINK_Y1)}) + 下载排针背面焊脚通槽 {F(B.RELIEFS[2][1] - B.RELIEFS[2][0])}×{F(B.RELIEFS[2][3] - B.RELIEFS[2][2])}",
           "原顶面 3 深的槽 (盘心 Φ12 / 控制板背面让位 / 电容弧形槽) " + ("全在玻纤板层里, 本件顶面平" if B.FR4_T >= 3 else f"穿玻纤板后还进本件顶面 {F(3 - B.FR4_T)}"),
           "旧一体底盘 base_disc_v1_2 (Φ220×6) 图纸/模型冻结在 models/base_disc_v1_2/, 不再更新"],
))

# ---------------- coil_ring_v1_2 ----------------
SPECS.append(dict(
    code="coil_ring_v1_2", shape=B.ring, short="线圈环 (托定子盘)", qty="1",
    title=f"线圈环: 方座 ±{F(B.COLLAR_FLAT)} 托定子盘 + 内管 Φ{F(B.TUBE_OD)} 穿定子盘",
    subtitle=f"Φ{F(B.COLLAR_D)} 圆内顶 Z{F(B.FL_Z0)} (托定子盘), 圆外四角只留 {F(B.RING_CORNER_T)}; 内管顶 Z{F(B.TUBE_TOP)} = 安装法兰顶 (穿定子盘+安装法兰)",
    orient="底面 (Z0) 贴床",
    phi=[B.BORE_D, B.TUBE_OD, 2 * B.R_SCREW, (2 * B.COLLAR_FLAT, f"{F(2 * B.COLLAR_FLAT)} (方)"), B.COLLAR_D],
    sec=dict(ang=45, zd=[(0, B.RING_CORNER_T), (0, B.FL_Z0), (B.FL_Z0, B.TUBE_TOP), (0, B.TUBE_TOP)],
             rd=[(B.BORE_D / 2, B.TUBE_OD / 2), (0, B.BORE_D / 2, f"R{F(B.BORE_D / 2)}"), (0, B.COLLAR_D / 2, f"R{F(B.COLLAR_D / 2)}")]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec="Φ3.2 通 (方座全高)", where=ring_txt(B.FLANGE_SCREWS) + "  = 底盘 G / 定子盘 A"),
        dict(tag="B", pts=B.RING_M3, spec=f"Φ3.2 通 (四角 {F(B.RING_CORNER_T)} 厚)", where=f"(±{F(B.RING_M3_XY)}, ±{F(B.RING_M3_XY)})  M3×12 盘底往上, 顶面上法兰螺母 (圆台四角 Φ8.2 让位)"),
    ],
    dets=[dict(tag="C", kind="free", z=(0, B.TUBE_TOP), pt=((B.WIRE_XL + B.WIRE_XR) / 2, -34), ang=270, W=6.5,
               title=f"出线槽 x{F(B.WIRE_XL)}…{F(B.WIRE_XR)} (宽 {F(B.WIRE_XR - B.WIRE_XL)}) 高 {F(B.WIRE_ZH)}, A 孔外留 Φ{F(B.WIRE_RING_D)} 小圈",
               zd=[(0, B.WIRE_ZH, F(B.WIRE_ZH), 0), (B.WIRE_ZH, B.TUBE_TOP, F(B.TUBE_TOP - B.WIRE_ZH), 8)],
               ud=[(B.BORE_D / 2 - 34, B.TUBE_OD / 2 - 34, F((B.TUBE_OD - B.BORE_D) / 2))])],
    notes=[f"方座四角倒角 {F(B.RING_CH)}; 内孔 Φ{F(B.BORE_D)}",
           f"圆台四角 Φ{F(B.RING_NUT_CLR_D)} 让位 (Z{F(B.RING_CORNER_T)}→{F(B.FL_Z0)}), 让 M3 法兰螺母 Φ7.6",
           "装配: 先锁线圈环 (B 组 4 颗), 再装定子盘"],
))

# ---------------- flange_disc_v1_2 ----------------
SPECS.append(dict(
    code="flange_disc_v1_2", shape=B.flange_disc, short="定子盘 (无线供电下盖)", qty="1",
    title=f"定子盘 Φ165: V0.4 flange_disc 底板减 {F(B.FL_THIN)}, 中心孔 Φ{F(2 * B.FL_HOLE_R)}",
    orient="按 V0.4 flange_disc 原姿态",
    phi=[2 * B.FL_HOLE_R, 2 * B.CAV_R0, 2 * B.CAV_R1, 165.0],   # 11-17: 标内墙/外墙 (线圈内定位 / 铜螺母环), 孔圈 PCD 见孔表
    sec=dict(ang=22.5, zd=[(B.FL_Z0, B.FL_TOP)]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec="Φ3.2 通", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20 到底盘铜螺母"),
        dict(tag="B", pts=B.LID_SCREWS, spec=f"Φ3.2 通 + 底面 Φ{F(B.LID_INS_D)}×{F(B.LID_INS_H)} 铜螺母孔",
             where=ring_txt(B.LID_SCREWS) + "  上下盖互锁 M3×10 + 底面下挂 M3 法兰螺母 (11-20; Φ4.2 孔沿用, 不嵌)",
             det=dict(kind="ins", d=3.2, D=B.LID_INS_D, h=B.LID_INS_H, side="bot", z=(B.FL_Z0, B.FL_TOP), pt=B.LID_SCREWS[0], title="外圈 M3 铜螺母孔")),
    ],
    notes=[f"Z{F(B.FL_Z0)}→{F(B.FL_TOP)}; 线圈腔 r{F(B.CAV_R0)}–{F(B.CAV_R1)} 深 {F(B.FL_TOP - B.CAV_Z0)} (11-16 晚 用户 2.5 → 2.8), 腔底 Z{F(B.CAV_Z0)}, 底板 {F(B.CAV_Z0 - B.FL_Z0)}",
           f"内墙 r31.7–{F(B.CAV_R0)}: 外圆 Φ{F(2 * B.CAV_R0)} 套线圈内径 Φ{F(B.COIL_ID)} (11-17); 外墙 (铜螺母环) r{F(B.CAV_R1)}–82.5 宽 {F(82.5 - B.CAV_R1)} (11-17 用户 ≥10); 线圈外径需 ≤ Φ{F(2 * B.CAV_R1)}",
           "+X 处 XT60 压块让位缺口; 线圈出线孔 2 个: 内 Φ4 r41.9 @2.5° (11-20 原 r40–61 通槽补实改圆孔, 孔边切腔内缘 r39.9) + 外 Φ4 r70 @30°",
           *(["底面控制板让位: 无 (11-16 晚: 2 颗电解实测高 6.1、3P 排针改弯排针, 都低于定子盘底 Z" + F(B.FL_Z0) + ")"] if not B.BRD_POCKETS else []),
           *(["底面控制板让位 (11-12 夜): " + "; ".join(f"x{F(p['bbox'][0] - B.BRD_POCKET_GAP)}..{F(p['bbox'][3] + B.BRD_POCKET_GAP)} y{F(p['bbox'][1] - B.BRD_POCKET_GAP)}..{F(p['bbox'][4] + B.BRD_POCKET_GAP)} 深 {F(p['depth'])}" for p in B.BRD_POCKETS)] if B.BRD_POCKETS else [])],
))

# ---------------- mounting_flange_v1_2 ----------------
MF_Z0 = B.FL_Z0 + (B.MF_THIN_LOW - B.FL_THIN)      # 外裙底 Z8.5 (11-16 晚, 齐定子盘底)
SPECS.append(dict(
    code="mounting_flange_v1_2", shape=B.mounting_flange, short="安装法兰 (无线供电上盖)", qty="1",
    title=f"安装法兰 Φ170: 外裙 r82.5–85 到定子盘底 (高 {F(B.FL_TOP - MF_Z0)}), 板顶减 {F(B.MF_THIN)}, 中心孔 Φ{F(2 * B.MF_HOLE_R)}",
    subtitle=f"外裙 r82.5–85 整个包住定子盘外缘, 底 Z{F(MF_Z0)} = 定子盘底 (11-16 晚 用户: 从外面看定子盘是完整环形盘)" + (f"; 4 处下罩螺母让位 Φ{F(B.MF_NUT_RELIEF[0])} 到 Z{F(B.MF_NUT_RELIEF[1])}" if B.MF_NUT_RELIEF_ENABLE else ""),
    orient="翻面打印 (板顶朝下)",
    phi=[2 * B.MF_HOLE_R, 2 * B.R_SCREW, 2 * 78.0, 165.0, 170.0],
    sec=dict(ang=22.5, zd=[(MF_Z0, B.FL_TOP), (B.FL_TOP, B.MF_TOP), (MF_Z0, B.MF_TOP)]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔", where=ring_txt(B.FLANGE_SCREWS) + f"  M3×{F(FS_L['C'])} 到底盘 G 法兰螺母",
             det=dict(kind="cb", d=3.2, D=7.0, h=B.MF_CB, side="top", z=(B.FL_TOP, B.MF_TOP), pt=B.FLANGE_SCREWS[0], title="M3 沉孔 (A/B 同)")),
        dict(tag="B", pts=B.LID_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔  同详图 A", where=ring_txt(B.LID_SCREWS) + "  M3×10 + 定子盘底下挂 M3 法兰螺母"),
    ],
    dets=[dict(tag="D", kind="free", z=(MF_Z0, B.MF_TOP), pt=(83.75 * math.cos(math.radians(22.5)), 83.75 * math.sin(math.radians(22.5))), ang=22.5, W=5.0,
               title="外裙 r82.5–85 (中心 r83.75)", zd=[(MF_Z0, B.FL_TOP, F(B.FL_TOP - MF_Z0), 0), (B.FL_TOP, B.MF_TOP, F(B.MF_TOP - B.FL_TOP), 0)], ud=[(-1.25, 1.25, "2.5")])],
    notes=[f"外裙底 Z{F(MF_Z0)} = 定子盘底 (11-16 晚 外裙 4 → 5)" + (f"; 下罩 4 颗 M3 法兰螺母 (r86.8, 顶 Z8.7) 处外裙底挖 Φ{F(B.MF_NUT_RELIEF[0])} 到 Z{F(B.MF_NUT_RELIEF[1])}" if B.MF_NUT_RELIEF_ENABLE else "; 下罩 4 颗 M3 法兰螺母 (r86.8, 顶 Z8.7) 离外裙底 3.3, 不开让位 (11-23 取消)"), "外圈 B 孔 r79 居中于定子盘外墙 (原 V0.4 r77.5 已补实)",
           f"中心孔 Φ{F(2 * B.MF_HOLE_R)}: 线圈环内管 Φ{F(B.TUBE_OD)} 穿过, 顶齐 Z{F(B.MF_TOP)}"],
))

# ---------------- ir_clamp_v1_2 (11-23 光电发射板压片) ----------------
_ICZ1 = B.FL_Z0; _ICZ0 = B.FL_Z0 - B.IR_CL_T
SPECS.append(dict(
    code="ir_clamp_v1_2", shape=B.ir_clamp, short="光电发射板压片", qty="1",
    title=f"光电发射板压片: r77.5 弧条 宽 {F(B.IR_CL_W)} 厚 {F(B.IR_CL_T)}, 两端 Φ{F(B.IR_CL_PAD_D)} 垫锁定子盘 B 孔",
    subtitle=f"顶面贴定子盘底 Z{F(_ICZ1)}; 板槽 {F(B.IR_PCB_W + 2 * B.IR_CLR)}×{F(B.IR_PCB_L + 2 * B.IR_CLR)} 深 {F(B.IR_PCB_T)} + 器件槽 深 {F(B.IR_BOT_H + B.IR_BOT_GAP)}; 2 定位销; 板内端伸出压片露焊盘 (无出线孔); LED r77.5 @{F(B.IR_ANG)}° (两螺丝正中)",
    orient="顶面 (板槽面) 朝上打印",
    phi=[],
    sec=dict(ang=B.IR_ANG, zd=[(_ICZ0, _ICZ1), (_ICZ1 - B.IR_PCB_T, _ICZ1)]),
    holes=[dict(tag="A", pts=B.IR_CL_HOLES, spec=f"Φ{F(B.IR_CL_HOLE_D)} 通 + 底面 Φ{F(B.IR_CL_NUT_CB_D)} 法兰螺母沉孔 (留 {F(B.IR_CL_PAD_T)})",
                where=ring_txt(B.IR_CL_HOLES) + f"  M3×{F(B.IR_CL_SCREW_L)} (定子盘外圈 B 孔, 不换长度)")],
    notes=[f"发射板 {F(B.IR_PCB_W)}×{F(B.IR_PCB_L)}×{F(B.IR_PCB_T)} 双面: 顶 0603 IR (贴定子盘底, 伸进 Φ{F(B.IR_WIN_D)} 通光孔), 底 0603 10k + 2 焊盘",
           f"板槽底整面托板; 2 个定位销 Φ{F(B.IR_PIN_D)} 高 {F(B.IR_PIN_H)} 插板上对角 NPTH 孔 Φ{F(B.IR_HOLE_D)}; 板内端伸出压片内边, 底面 2 焊盘外露, 焊线斜下到控制板 XT60 24V/GND",
           f"螺母处只夹 {F(B.IR_CL_PAD_T)}, 法兰螺母 Z{F(B.FL_Z0 - B.IR_CL_PAD_T - 3.7)}–{F(B.FL_Z0 - B.IR_CL_PAD_T)}, M3×{F(B.IR_CL_SCREW_L)} 吃 3.2"],
))

# ---------------- 玻璃罩下罩三件 ----------------
sup = B.OUT_SCREWS
gl_notes = [f"玻璃 OD{F(B.GL_OD)}×{F(B.GL_T)} H{F(B.GL_H)} 坐 Z{F(B.Z_G)} (内卡顶 Z{F(B.Z_VIEW0)} = LED 下沿 Z{F(B.Z_LED0)} − {F(B.VIEW_MARGIN)}), 单边间隙 {F(B.GL_CLR)}",
            f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.Z_G)}; 内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}",
            f"三角块厚 {F(B.TRI_T)} (十字 ±{F(B.P_N)} 外); 墙内面 = 内卡内面 r{F(B.SPIG_IN)} 直下; 无托块",
            f"三角块两直边各一片斜筋 ×8: 厚 {F(B.GU_T)}, 外侧面齐直边 ±{F(B.P_N)}; 尖角 Z{F(B.TRI_T)} → r{F(B.GU_R85)} Z{F(B.GU_Z1)} (定子盘/外裙下) → 贴墙 Z{F(B.GU_ZH)}",
            f"+X XT60 开口 = 压块 +0.2; M3 法兰螺母井 Φ{F(B.XT_NUT_WELL_D)} Z{F(B.XT_H)}→{F(B.XT_H + B.XT_NUT_WELL_H)}"]
sh_holes = [dict(tag="A", pts=B.SH_M6, spec=f"Φ3.4 通 + 顶面圆沉孔 Φ{F(B.SH_NUT_D)} 深 {F(B.SH_BOSS_Z1 - B.NUT_Z0)} (三角块上圆台 Φ{F(B.SH_BOSS_D)} 加厚到 Z{F(B.SH_BOSS_Z1)})", where=ring_txt(B.SH_M6) + f"  M3×16 盘底往上; M3 法兰螺母法兰朝下坐沉孔底 Z{F(B.NUT_Z0)} (11-24 用户: 加厚 + 通孔加沉孔)"),
]
sh_zd = [(0, B.TRI_T), (0, B.Z_G), (B.Z_G, B.Z_G + B.OUT_DEPTH), (B.Z_G, B.Z_G + B.IN_DEPTH)]
sh_rd = [(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.go, B.SH_OUT)]
SPECS.append(dict(
    code="glass_shroud_v1_2", shape=B.seat, short="玻璃罩下罩+定位环 (合并)", qty="1 (与分体版二选一)",
    title="玻璃罩下罩 + 定位环 (合并版, 外卡一体)", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.gi, 2 * B.go, 2 * B.SH_OUT],
    sec=dict(ang=45, r0=70.0, zd=sh_zd, rd=sh_rd), holes=sh_holes,
    notes=gl_notes + [f"外卡 r{F(B.go)}–{F(B.SH_OUT)} 深 {F(B.OUT_DEPTH)}, 斜顶 (外缘直边 {F(B.LIP_EDGE)})"]))
def _gb_hole(kind):   # 11-25 玻璃下横锁 H: kind 'in' = 玻璃座内卡加厚块 / 'out' = 外卡环
    c45, rr = math.cos(math.pi / 4), (B.GL_R0 if kind == "in" else B.GS_SEAT)
    pts = [(rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))) for a in B.GS_ANG]
    if kind == "in":
        return dict(tag="H", pts=pts, spec=f"内卡加厚块 ×8 (宽 {F(2 * B.GB_HW)} 高 {F(2 * B.GB_HH)}, 内面 r{F(B.GL_R0)}, 底 45°): Φ{F(B.GS_HOLE)} 径向通 + 法兰窝 Φ{F(B.GL_FL_D)}×{F(B.GL_FL_H)} + 六角窝 AF{F(B.GL_HEX_AF)}×{F(B.GL_HEX_H)}",
                    where=f"0+45k°  孔心 Z{F(round(B.GB_Z, 2))} (玻璃下端上 {F(round(B.GB_Z - B.Z_G, 2))}); M3 法兰螺母从内面塞, 法兰与内面齐平, 到内卡外面剩 {F(round(B.gi - B.GL_R0 - B.GL_FL_H - B.GL_HEX_H, 2))}",
                    det=dict(kind="free", z=(B.GB_Z - 11, B.Z_VIEW0), pt=(91.6 * c45, 91.6 * c45), W=5.0, title="加厚块 H (45° 径向剖, 右 = 外)",
                             zd=[(B.GB_Z - B.GB_HH, B.GB_Z, F(B.GB_HH), 0), (B.GB_Z, B.GB_Z + B.GB_HH, F(B.GB_HH), 0)], ud=[(B.GL_R0 - 91.6, B.GL_R0 + B.GL_FL_H - 91.6, F(B.GL_FL_H), 0), (B.GL_R0 + B.GL_FL_H - 91.6, B.GL_R0 + B.GL_FL_H + B.GL_HEX_H - 91.6, F(B.GL_HEX_H), 0), (B.GL_R0 - 91.6, B.gi - 91.6, F(round(B.gi - B.GL_R0, 2)), 5)]))
    return dict(tag="H", pts=pts, spec=f"径向横锁孔 ×8 Φ{F(B.GS_HOLE)} 通 + 外面 Φ{F(B.GS_CB_D)} 平座 (r{F(B.GS_SEAT)})", where=f"0+45k°  孔心 Z{F(round(B.GB_Z, 2))} (环底上 {F(round(B.GB_Z - B.Z_G, 2))}); M3×{F(B.GS_L)} 超薄头, 吃 {F(B.GS_ENG)}",
                det=dict(kind="free", z=(B.Z_G, B.Z_G + B.OUT_DEPTH), pt=(B.GS_SEAT * c45, B.GS_SEAT * c45), W=8.0, title="横锁孔 H (45° 径向剖, 右 = 外)",
                         zd=[(B.Z_G, B.GB_Z, F(round(B.GB_Z - B.Z_G, 2)), 0), (B.GB_Z, B.Z_G + B.OUT_DEPTH, F(round(B.Z_G + B.OUT_DEPTH - B.GB_Z, 2)), 0)], ud=[(B.go - B.GS_SEAT, 0, F(round(B.GS_SEAT - B.go, 2)), 0)]))
SPECS.append(dict(   # 11-20 用户「改一下，2合一，不要那个外卡环，做一个」
    code="glass_shroud_2in1_v1_2", shape=B.shroud_split, short="玻璃下 底座+玻璃座 二合一", qty="1 (+外卡环)", date="2026-11-20",
    title=f"玻璃下 二合一: 底座+玻璃座一体 Z0→{F(B.Z_G)} + 内卡到 Z{F(B.Z_VIEW0)}, 不含外卡环; 顶面嵌合凸筋配外卡环", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.gi, 2 * B.TG_R0, 2 * (B.TG_R0 + B.TG_W), 2 * B.SH_OUT],
    sec=dict(ang=45, r0=70.0, zd=[(0, B.TRI_T), (0, B.Z_G), (B.Z_G, B.Z_G + B.IN_DEPTH), (B.Z_G, B.Z_G + B.TG_H)],
             rd=[(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.TG_R0, B.TG_R0 + B.TG_W)]),
    holes=sh_holes + [_gb_hole("in")],
    notes=gl_notes + [f"= 分体底座+玻璃座合成一件: 不在 Z{F(B.SPLIT_Z)} 横切, 无 {B.JN_N}×M4 对锁孔/螺母窝/止口",
                      f"外卡环 glass_clamp_ring_v1_2 单独打印: 顶面凸筋 r{F(B.TG_R0)}–{F(B.TG_R0 + B.TG_W)} 高 {F(B.TG_H)} 插外卡环底槽 (单边 {F(B.TG_CLR)})"]))
SPECS.append(dict(
    code="glass_shroud_lower_v1_2", shape=B.shroud_lo, short="玻璃下 底座 (分体)", qty="1 (配玻璃座 + 外卡环)",
    title=f"玻璃下 底座: Z0→{F(B.SPLIT_Z)} + 顶面止口凸筋, {B.JN_N}× M4 通孔 + 底面法兰螺母窝", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.JN_R, 2 * B.RG_R0, 2 * (B.RG_R0 + B.RG_W), 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=70.0, zd=[(0, B.TRI_T), (0, B.SPLIT_Z), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H)], rd=[(B.SPIG_IN, B.SH_OUT), (B.RG_R0, B.RG_R0 + B.RG_W)]),
    holes=sh_holes + [dict(tag="J", pts=B.JN_PTS, spec=f"Φ{F(B.JN_D)} 通 + 底面圆窝 Φ{F(B.JN_NUT_FD)} 深 {F(B.JN_NUT_Z1)} (M4 法兰螺母 法兰朝上压入)",
                           where=ring_txt(B.JN_PTS) + f"  配玻璃座 M4×{F(B.JN_L)}",
                           det=dict(kind="cb", d=B.JN_D, D=B.JN_NUT_D, h=B.JN_NUT_Z1, side="bot", z=(0, B.SPLIT_Z), pt=B.JN_PTS[0], title=f"螺母窝 J (圆 Φ{F(B.JN_NUT_FD)}, 法兰朝上压入)"))],
    notes=[f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.SPLIT_Z)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}"] + gl_notes[2:] + [f"底座+玻璃座分界 Z{F(B.SPLIT_Z)} (承载盘顶); 顶面止口凸筋 r{F(B.RG_R0)}–{F(B.RG_R0 + B.RG_W)} 高 {F(B.RG_H)} 插玻璃座底槽 (单边 {F(B.RG_CLR)})",
                          "以后改可视高度只重打玻璃座, 本件不动", f"M4×{F(B.JN_L)} 穿通两段: 尾 Z{F(B.JN_TIP)}, 法兰螺母 Z{F(B.JN_NUT_Z1 - B.JN_NUT_H)}..{F(B.JN_NUT_Z1)} (啮合 {F(B.JN_NUT_Z1 - B.JN_TIP)}), 底面平坐底盘"]))
SPECS.append(dict(
    code="glass_shroud_upper_v1_2", shape=B.shroud_hi, short="玻璃下 玻璃座 (分体)", qty="1", date="2026-11-25",
    title=f"玻璃下 玻璃座: Z{F(B.SPLIT_Z)}→{F(B.Z_G)} 墙 + 内卡到 Z{F(B.Z_VIEW0)}, {B.JN_N}× M4 沉孔", orient="底面 (止口槽面) 贴床",
    phi=[2 * B.SPIG_IN, 2 * B.gi, 2 * B.JN_R, 2 * B.TG_R0, 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=86.0, zd=[(B.SPLIT_Z, B.Z_G), (B.Z_G, B.Z_G + B.IN_DEPTH), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H + B.RG_CLR), (B.Z_G, B.Z_G + B.TG_H)],
             rd=[(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.RG_R0 - B.RG_CLR, B.RG_R0 + B.RG_W + B.RG_CLR), (B.TG_R0, B.TG_R0 + B.TG_W)]),
    holes=[dict(tag="J", pts=B.JN_PTS, spec=f"Φ{F(B.JN_D)} 通 + 顶面 Φ{F(B.JN_CB)} 沉孔深 {F(B.Z_G - B.JN_BEAR)}", where=ring_txt(B.JN_PTS) + f"  M4×{F(B.JN_L)} 超薄头 穿通到底座底面法兰螺母",
                det=dict(kind="cb", d=B.JN_D, D=B.JN_CB, h=B.Z_G - B.JN_BEAR, side="top", z=(B.SPLIT_Z, B.Z_G), pt=B.JN_PTS[0], title="M4 沉孔 J")), _gb_hole("in")],
    notes=[gl_notes[0], f"内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)} (顶 Z{F(B.Z_VIEW0)} = 可视下边界)",
           f"底面止口槽 r{F(B.RG_R0 - B.RG_CLR)}–{F(B.RG_R0 + B.RG_W + B.RG_CLR)} 深 {F(B.RG_H + B.RG_CLR)}; 顶面凸筋 r{F(B.TG_R0)}–{F(B.TG_R0 + B.TG_W)} 高 {F(B.TG_H)} 插外卡环底槽 (11-17 晚 凸筋由外卡环移到本件)",
           f"螺丝头顶 Z{F(B.JN_BEAR + B.JN_HH)}, 玻璃端面 + 外卡环盖住; 拆: 8 横锁螺丝 → 外卡环 → 玻璃 → {B.JN_N} 螺丝 → 玻璃座", "11-25 横锁: 装前把 8 颗 M3 法兰螺母压进内卡窝; 加厚块离转子罩 r85 3.5"]))
SPECS.append(dict(
    code="glass_clamp_ring_v1_2", shape=B.clamp_ring, short="外卡环 (分体)", qty="1",
    title=f"外卡环: r{F(B.go)}–{F(B.SH_OUT)} 高 {F(B.OUT_DEPTH)} 斜面 + 顶平带 {F(B.OUT_FOOT)} + 底面槽 {F(B.TG_W + 2 * B.TG_CLR)}×{F(B.TG_H + B.TG_CLR)}, 8× 横锁孔", orient="底面 (槽面) 贴床, 斜面朝上, 免支撑", date="2026-11-25",
    phi=[2 * B.go, 2 * (B.TG_R0 - B.TG_CLR), 2 * (B.TG_R0 + B.TG_W + B.TG_CLR), 2 * B.SH_OUT],
    sec=dict(ang=22.5, r0=96.0, zd=[(B.Z_G, B.Z_G + B.TG_H + B.TG_CLR), (B.Z_G, B.Z_G + B.OUT_DEPTH), (B.Z_G, B.Z_G + B.LIP_EDGE, f"{F(B.LIP_EDGE)} (外缘直边)")],
             rd=[(B.go, B.go + B.OUT_FOOT), (B.go, B.SH_OUT), (B.TG_R0 - B.TG_CLR, B.TG_R0 + B.TG_W + B.TG_CLR)]),
    holes=[_gb_hole("out")],
    notes=[f"内面 r{F(B.go)} 贴玻璃外壁 (单边间隙 {F(B.GL_CLR)})",
           f"底面槽 r{F(B.TG_R0 - B.TG_CLR)}–{F(B.TG_R0 + B.TG_W + B.TG_CLR)} 深 {F(B.TG_H + B.TG_CLR)} 套玻璃座顶面凸筋 (单边 {F(B.TG_CLR)})",
           f"玻璃管下端 8 孔 Φ{F(B.GS_GLASS_D)} 孔心离端 {F(round(B.GB_Z - B.Z_G, 2))}: 本件套上管子当钻模划线 (底面对齐管端)",
           "装配: 玻璃先套内卡 → 从上套环 → 8 颗横锁螺丝从外往里轻拧"]))

# ---------------- 玻璃上 (顶盖) 两件 (11-13) ----------------
SPECS.append(dict(
    code="glass_top_v1_2", shape=B.glass_top, short="玻璃上 下件 (红, 平板环 + 外卡)", qty="1", date="2026-11-25", stl_asm=True,
    title=f"玻璃上 下件 (红): 平板环 r{F(B.GT_LEDGE_R)}–{F(B.SH_OUT)} 厚 {F(B.GT_TOP_T)} + 外卡 r{F(B.go)} 起深 {F(B.GT_DEPTH)}, {B.GC_N}× 法兰螺母沉孔",
    subtitle=f"底面坐玻璃管上端 Z{F(round(B.Z_GT, 2))}; 顶面 Z{F(round(B.GT_Z1, 2))} 直接托圆环玻璃 (无垫) 并承绿件",
    orient="翻面: 顶面整面贴床, 外卡和螺母沉孔朝上, 免支撑; Φ220 要大床",
    phi=[2 * B.GT_LEDGE_R, 2 * B.GC_R, 2 * B.go, 2 * B.SH_OUT],
    sec=dict(ang=0, r0=80.0, zd=[(B.GT_Z0, B.Z_GT), (B.Z_GT, B.GT_Z1), (B.GT_Z1 - B.LIP_EDGE, B.GT_Z1), (B.GT_Z0, B.GT_Z1)],
             rd=[(B.GT_LEDGE_R, B.go), (B.go, B.go + B.GT_FOOT), (B.go, B.SH_OUT)], auto_dims=False),
    holes=[dict(tag="N", pts=B.GC_PTS, spec=f"Φ{F(B.GC_HOLE)} 通 + 底面圆沉孔 Φ{F(B.GC_NUT_D)} 深 {F(B.GC_NUT_H)} (M3 法兰螺母)", where=ring_txt(B.GC_PTS) + "  螺母法兰朝上顶沉孔底, 从底面塞进; 套上玻璃管后被管端面挡住",
                det=dict(kind="cb", d=B.GC_HOLE, D=B.GC_NUT_D, h=B.GC_NUT_H, side="bot", z=(B.Z_GT, B.GT_Z1), pt=B.GC_PTS[0], title="法兰螺母沉孔 N")),
           dict(tag="H", pts=[(B.GS_SEAT * math.cos(math.radians(a)), B.GS_SEAT * math.sin(math.radians(a))) for a in B.GS_ANG], spec=f"径向横锁孔 Φ{F(B.GS_HOLE)} 通 + 外面 Φ{F(B.GS_CB_D)} 平座 (r{F(B.GS_SEAT)})", where=f"0/45/90/135/180/225/270/315°  孔心 Z{F(round(B.GS_Z, 2))} (管端下 {F(round(B.Z_GT - B.GS_Z, 2))}, 外卡底上 {F(round(B.GS_Z - B.GT_Z0, 2))})",
                det=dict(kind="free", z=(B.GT_Z0, B.Z_GT + 2), pt=(102.7 * math.cos(math.pi / 4), 102.7 * math.sin(math.pi / 4)), W=7.0, title="横锁孔 H (过 45° 径向剖, 右 = 外)",
                         zd=[(B.GT_Z0, B.GS_Z, F(round(B.GS_Z - B.GT_Z0, 2)), 0), (B.GS_Z, B.Z_GT, F(round(B.Z_GT - B.GS_Z, 2)), 0)], ud=[(B.go - B.GS_SEAT, 0, F(round(B.GS_SEAT - B.go, 2)), 0)]))],
    notes=[f"外卡内面 r{F(B.go)} 贴玻璃管外壁 (单边 {F(B.GL_CLR)}); 斜面 (r{F(B.go + B.GT_FOOT)}, Z{F(round(B.GT_Z0, 2))}) → (r{F(B.SH_OUT)}, Z{F(round(B.GT_Z1 - B.LIP_EDGE, 2))}) {B.GT_CONE_DEG:.0f}°, 外缘直边 {F(B.LIP_EDGE)}",
           f"沉孔底以上剩 {F(round(B.GT_TOP_T - B.GC_NUT_H, 2))}; 内缘搭玻璃 {F(B.GD_OD / 2 - B.GT_LEDGE_R)}",
           f"横锁孔 ×{len(B.GS_ANG)} (径向, 45k°, 详图 H): Φ{F(B.GS_HOLE)} 通 + 外面 Φ{F(B.GS_CB_D)} 平座 r{F(B.GS_SEAT)}, 孔心 Z{F(round(B.GS_Z, 2))} = 管端下 {F(round(B.Z_GT - B.GS_Z, 2))}; M3×{F(B.GS_L)} 超薄头",
           f"玻璃管上端 {len(B.GS_ANG)} 孔 Φ{F(B.GS_GLASS_D)} 同角同高 (孔心离管端 {F(round(B.Z_GT - B.GS_Z, 2))}); 本件套上管子当钻模划线",
           "11-25 用户草图: 内卡 / 铜螺母取消, 外卡由绿件并到本件"]))
SPECS.append(dict(
    code="glass_top_clamp_v1_2", shape=B.glass_top_clamp, short="玻璃上 上件 (绿, L 形压环)", qty="1", date="2026-11-25", stl_asm=True,
    title=f"玻璃上 上件 (绿): L 形环 r{F(B.GD_POCKET_R)}–{F(B.SH_OUT)} 高 {F(round(B.GC_Z1 - B.GC_Z0, 2))} + 顶板 r{F(B.GC_R0)} 起厚 {F(B.GC_T)}, {B.GC_N}× M3 锁下件",
    subtitle=f"底面 Z{F(round(B.GC_Z0, 2))} 落红件顶 = 硬限位; 顶 Z{F(round(B.GC_Z1, 2))}; 内孔套圆环玻璃 OD{F(B.GD_OD)}×{F(B.GD_T)} (单边 {F(B.GD_CLR)})",
    orient="翻面: 顶面整面贴床, 玻璃窝朝上, 免支撑 (顶面沉孔 Φ7.4 桥接); Φ220 要大床",
    phi=[2 * B.GC_R0, 2 * B.GD_POCKET_R, 2 * B.GC_R, 2 * B.SH_OUT],
    sec=dict(ang=0, r0=80.0, zd=[(B.GC_Z0, B.GC_ZP), (B.GC_ZP, B.GC_Z1), (B.GC_Z0, B.GC_Z1)],
             rd=[(B.GC_R0, B.GD_POCKET_R), (B.GD_POCKET_R, B.SH_OUT)]),
    holes=[dict(tag="C", pts=B.GC_PTS, spec=f"Φ{F(B.GC_HOLE)} 通 + 顶面沉孔 Φ{F(B.GC_CB_D)} 深 {F(B.GC_CB_H)}", where=ring_txt(B.GC_PTS) + f"  M3×{F(B.GC_SCREW_L)} 超薄头 (Φ{F(B.GC_HEAD_D)}×{F(B.GC_HEAD_H)}) 往下进红件底法兰螺母, 吃 {F(B.GC_ENG)}, 尾离玻璃管端面 {F(round(B.GC_TIP - B.Z_GT, 2))}",
                det=dict(kind="cb", d=B.GC_HOLE, D=B.GC_CB_D, h=B.GC_CB_H, side="top", z=(B.GC_Z0, B.GC_Z1), pt=B.GC_PTS[0], title="螺丝沉孔 C"))],
    notes=[f"玻璃窝 r{F(B.GD_POCKET_R)} 深 {F(round(B.GC_ZP - B.GC_Z0, 2))} = 玻璃 {F(B.GD_T)} + 余量 {F(B.GC_GAP)}; 窝口倒角 0.5; 顶外缘倒角 {F(B.GC_CH)}, 内缘 {F(B.GC_IN_CH)}",
           f"11-25 用户取消硅胶垫: 窝深 11.6 → {F(round(B.GC_ZP - B.GC_Z0, 2))}, 顶板 4 → {F(B.GC_T)} (红件 + 本件 = {F(round(B.GT_TOP_T + B.GC_Z1 - B.GC_Z0, 2))}); 螺丝拧到绿件贴红件即止, 套玻璃管前看螺丝尾不凸出红件底面",
           "装配 (桌上): 红件翻面塞 8 颗法兰螺母 (点胶防掉) → 翻正 → 圆环玻璃 (带堵头) → 本件 → 8 颗对角拧到贴死 → 整组套上玻璃管"]))
SPECS.append(dict(
    code="glass_top_lug_v1_2", shape=B.glass_top_lug, short="玻璃上 管内弧形件 ×8 (横锁)", qty="8", date="2026-11-25", material="PETG", stl_asm=True,
    title=f"玻璃上 管内弧形件: 宽 {F(2 * B.GL_HW)} × 高 {F(2 * B.GL_HH)} × 厚 {F(B.GL_R - B.GL_R0)}, 外弧 R{F(B.GL_R)}, 内面法兰螺母窝",
    subtitle=f"贴玻璃管内壁 (管内 R{F(B.GL_OD / 2 - B.GL_T)}, 中间 0.5 双面胶粘在玻璃内壁, 拆螺丝时不掉); M3×{F(B.GS_L)} 超薄头从管外锁进来",
    orient="内平面 (螺母窝面) 贴床, 外弧朝上, 免支撑",
    sec=dict(ang=0, r0=80.0, auto_dims=False, zd=[(B.GS_Z - B.GL_HH, B.GS_Z + B.GL_HH)], rd=[(B.GL_R0, B.GL_R0 + B.GL_FL_H), (B.GL_R0, B.GL_R0 + B.GL_FL_H + B.GL_HEX_H), (B.GL_R0, B.GL_R)]),
    holes=[],
    notes=[f"孔 Φ{F(B.GS_HOLE)} 通, 孔心在件中心; 内面窝 = 法兰 Φ{F(B.GL_FL_D)} 深 {F(B.GL_FL_H)} + 六角 AF{F(B.GL_HEX_AF)} 再深 {F(B.GL_HEX_H)} (螺母不跟转, 法兰与内面齐平), 到外弧剩 {F(B.GL_WEB)}",
           f"螺丝: 支承 r{F(B.GS_SEAT)} → 尾 r{F(round(B.GS_TIP, 2))} (不出内面 r{F(B.GL_R0)}), 吃 {F(B.GS_ENG)}",
           "装配: 顶盖整组先在桌上锁好, 套上玻璃管, 从管子下口伸手进去贴住本件, 外面拧螺丝 (轻拧, 点螺纹胶)"]))
SPECS.append(dict(
    code="glass_top_hub_v1_2", shape=B.glass_top_hub, short="中心堵头 (卡扣)", qty="1", material="PETG (建议; PLA 先试)",
    title=f"中心堵头: 法兰 Φ{F(B.GH_FL_D)} + {B.GH_SLOTS} 爪卡扣穿圆环玻璃 Φ{F(B.GD_ID)} 孔" + (" + 688 轴承窝" if B.GT_BEARING else ""),
    subtitle=f"爪 r{F(B.GH_R0)}–{F(B.GH_R1)}, 倒钩 r{F(B._rb)} 钩面 30°, 导入 45°; 槽宽 {F(B.GH_SLOT_W)} ×{B.GH_SLOTS}, 爪长 {B.GH_L:.1f}",
    orient="法兰顶面朝下贴床 (爪朝上); 倒钩 30° 钩面悬 1.2, 不加支撑",
    phi=[2 * B.GH_R0, 2 * B.GH_R1, 2 * B._rb, B.GH_FL_D],
    sec=dict(ang=30, r0=0.0, zd=[(B._zt, B.GD_Z0), (B.GD_Z0, B.GD_Z1), (B.GD_Z1, B.GD_Z1 + B._fl_t)],
             rd=[(B.GH_R0, B.GH_R1), (0, B._rb, f"R{F(B._rb)}")]),
    holes=[],
    notes=[f"玻璃厚 {F(B.GD_T)}: 法兰底 Z{F(B.GD_Z1)} 压玻璃顶, 钩面内端 Z{F(B.GD_Z0)} = 玻璃底 (玻璃厚 +0.6 内仍能扣上, 爪带预压)",
           f"爪根应变 ≈ {B.GH_STRAIN * 100:.1f}% → 建议 PETG; PLA 先试",
           (f"688 窝 Φ{F(B.BRG_D)}×{F(B.BRG_H)} (轴承从下穿爪内孔 Φ{F(2 * B.GH_R0)} 压入) + 上方 Φ{F(B.BRG_RELIEF_D)}×{F(B.BRG_RELIEF_H)} 让轴过冲; 法兰厚 {F(B._fl_t)} (11-15 默认开, 灯板顶轴 Φ8 进 688)"
            if B.GT_BEARING else "可选 GT_BEARING=1: 内开 688 窝 (灯板顶轴)")]))

import led_support_v1_2 as L  # noqa: E402
# ---------------- 承载盘 rim_ring_v1_2_D170 (build_v1_2.py; export_3mf 写装配坐标 STL 到 models/<名>/) ----------------
_HUB_R = B.bbox(B.hub)[3]
_rz0, _rz1 = B.bbox(B.rim)[2], B.Z_RIM_TOP
_rh_std = [B.RH_PTS[k] for k in B.RH_STD_IDX]
_rh_ear = [B.RH_PTS[k] for k in B.RH_EAR_IDX]
_ang_txt = lambda pts: "/".join(F(round(ang(p), 1)) for p in pts) + "°"        # noqa: E731
# 承载盘剖面层级 (几何实测): 内孔 = 最小同心圆柱, 盘底 = 内孔底; 下凸台 = 盘底以下、裙边以内的同心圆柱
# 承载盘剖面层级: 盘底 B.RIM_BOT / 内孔 B.RIM_BORE_R / 下凸台 B.RIM_BUMP_R (凸台底 Z 实测)
_R_BORE, _R_PZ0 = B.RIM_BORE_R, B.RIM_BOT
# 11-17: 下凸台取消 (线圈内定位改到毂盘内环)
_rl = [(x, y) for x, y in B.RIM_LOCK_PTS]                                       # r30 锁盘孔 (V1.0 原有)
_R_LOCK = math.hypot(*_rl[0])
_rl_cb = [(x, y, c) for x, y in _rl for c in cyls(B.rim) if 5 < c[0] < 12 and math.hypot(c[1] - x, c[2] - y) < 0.1]
_known = list(B.SHR_HOLES) + list(B.MOD_HOLES) + list(B.BB_HOLES)
_rx = [c for c in cyl_at(B.rim, 4.2) if min(math.hypot(c[0] - x, c[1] - y) for x, y in _known) > 0.5]   # 其它 Φ4.2 (V1.0 原有底面铜螺母孔)
_rc = cyl_at(B.rim, 4.0)                                                        # Φ4 通孔 (V1.0 原有)
SPECS.append(dict(
    code="rim_ring_v1_2_D170", shape=B.rim, short=f"承载盘 Φ{F(B.RIM_D)}", qty="1", stl_asm=True,   # 俯视 STL 出图时从 B.rim 现写, 不依赖 export 是否已重跑
    title=f"承载盘 Φ{F(B.RIM_D)}: 裙边 r{F(B.RIM_SKIRT[0])}–{F(B.RIM_SKIRT[1])} 下到 Z{F(B.RIM_SKIRT[2])} 包住毂盘 r{F(_HUB_R)}; 外圈 8×Φ3.4 通孔 r{F(B.RH_R)}",
    subtitle=f"盘体 Z{F(B.RIM_BOT)}–{F(B.Z_RIM_TOP)} (厚 {F(B.Z_RIM_TOP - B.RIM_BOT)}), 顶面平; 顶面铜螺母孔: 罩底 {len(B.SHR_HOLES)} + 无线托盘 {len(B.MOD_HOLES)} (盘底 Φ{F(B.RIM_BOSS_D)} 凸台); "
             f"底板 {len(B.BB_HOLES)} 孔螺丝从盘底往上",
    orient="翻面: 顶面 (托盘面) 贴床, 裙边朝上 (out/打印STL 已是此姿态)",
    phi=[2 * B.RH_R, 2 * B.RIM_SKIRT[0], B.RIM_D],
    sec=dict(ang=0, r0=20.0, auto_dims=False,
             zd=[(_R_PZ0, _rz1), (B.RIM_SKIRT[2], _R_PZ0), (B.RIM_SKIRT[2], _rz1)],
             rd=[(_R_BORE, B.RIM_SKIRT[0], f"盘底平 {F(B.RIM_SKIRT[0] - _R_BORE)} mm (内孔 R{F(_R_BORE)} → 裙边 R{F(B.RIM_SKIRT[0])})"),
                 (B.RIM_SKIRT[0], B.RIM_SKIRT[1], f"裙边 {F(B.RIM_SKIRT[1] - B.RIM_SKIRT[0])} mm (R{F(B.RIM_SKIRT[0])}–R{F(B.RIM_SKIRT[1])})")]),
    holes=[dict(tag="R", pts=B.RH_PTS, spec="Φ3.4 通 (8 孔全通孔, 无沉孔)",
                where=ring_txt(B.RH_PTS) + f"  → 毂盘底 M3×4 铜螺母 Z{F(B.RH_INS[0])}–{F(B.RH_INS[1])}\n"
                      f"{_ang_txt(_rh_std)}: M3×{F(B.RH_L)} 头压盘顶 Z{F(B.RH_HEAD_Z0)}; {_ang_txt(_rh_ear)}: 立板耳朵 M3×{F(L.FOOT_SCREW_L)} (头压耳朵顶 Z{F(L.FOOT_CB_Z)})",
                det=dict(kind="free", z=(B.RIM_SKIRT[2], _rz1), pt=B.RH_PTS[1], W=5.0, title="外圈孔 R (径向剖, 含裙边)",
                         zd=[(B.RIM_SKIRT[2], _rz1, F(_rz1 - B.RIM_SKIRT[2]))], ud=[(-1.7, 1.7, "Φ3.4")])),
           dict(tag="S", pts=B.SHR_HOLES, spec=f"转子罩底 {len(B.SHR_HOLES)} 孔: 顶面铜螺母孔 " + hole_txt(B.rim, B.SHR_HOLES[0]) + f"; 盘底凸台 Φ{F(B.RIM_BOSS_D)} 到 Z{F(B.RIM_BOSS_Z0)}",
                where=ring_txt(B.SHR_HOLES) + "  压 M3×4 铜螺母",
                det=hole_det(B.rim, B.SHR_HOLES[0], f"罩底孔 S (M 同, 带 Φ{F(B.RIM_BOSS_D)} 凸台)", W=B.RIM_BOSS_D / 2 + 1.0, z=(B.RIM_BOSS_Z0, _rz1))),
           dict(tag="M", pts=B.MOD_HOLES, spec=f"无线托盘 {len(B.MOD_HOLES)} 孔: 顶面铜螺母孔 " + hole_txt(B.rim, B.MOD_HOLES[0]) + "  凸台同详图 S", where=xy(B.MOD_HOLES, 3) + "  压 M3×4 铜螺母"),
           dict(tag="P", pts=B.BB_HOLES, spec=f"底板 {len(B.BB_HOLES)} 孔: " + hole_txt(B.rim, B.BB_HOLES[0]) + " (盘底沉孔, 螺丝从下往上)",
                where=xy(B.BB_HOLES) + f"\n底板 H5/H7/H6/H8: {B.BB_SCREW_SPEC} + {B.BB_STANDOFF_SPEC} + {getattr(B, 'BB_NUT_SPEC', '')}",
                det=hole_det(B.rim, B.BB_HOLES[0], "底板孔 P (盘底沉孔)")),
           dict(tag="L", pts=_rl, spec=f"Φ3.2 通 (r{F(_R_LOCK)} 锁盘孔, V1.0 原有)" + (f"; 其中 {len(_rl_cb)} 个顶面 Φ{F(_rl_cb[0][2][0])}×{F(_rl_cb[0][2][4] - _rl_cb[0][2][3])} 沉孔" if _rl_cb else ""),
                where=ring_txt(_rl) + "  → 毂盘底铜螺母 (毂盘图 L)" + (f"; 沉孔在 {_ang_txt([(x, y) for x, y, _ in _rl_cb])}" if _rl_cb else "")),
           *([dict(tag="X", pts=[(c[0], c[1]) for c in _rx], spec=hole_txt(B.rim, _rx[0][:2]) + " (V1.0 原有底面铜螺母孔, 现未用)", where=xy([(c[0], c[1]) for c in _rx]))] if _rx else []),
           *([dict(tag="C", pts=[(c[0], c[1]) for c in _rc], spec="Φ4 通 (V1.0 原有, 现未用)", where=xy([(c[0], c[1]) for c in _rc]))] if _rc else []),
           dict(tag="A", pts=B.AC_HOLES, spec=f"Φ{F(B.AC_HOLE_D)} 通 (线圈 AC 引线)", where=xy(B.AC_HOLES) + "  进无线托盘底窗")],
    notes=[f"承载盘 Φ{F(B.RIM_D)}, 盘体 Z{F(_R_PZ0)}–{F(_rz1)} 厚 {F(_rz1 - _R_PZ0)}; 裙边 r{F(B.RIM_SKIRT[0])}–{F(B.RIM_SKIRT[1])} 到 Z{F(B.RIM_SKIRT[2])} (= 毂盘底), 毂盘 r{F(_HUB_R)} 嵌进去 (同定子嵌套)",
           f"剖视竖向 (左→右): 盘厚 {F(_rz1 - _R_PZ0)} / 裙边伸出盘底 {F(_R_PZ0 - B.RIM_SKIRT[2])} / 总高 {F(_rz1 - B.RIM_SKIRT[2])}",
           f"内孔 R{F(_R_BORE)} 套毂盘中心凸台定心; 11-17 原底面下凸台 R{F(B.RIM_BUMP_R[0])}–{F(B.RIM_BUMP_R[1])} 取消 (线圈 Φ{F(B.COIL_ID)} 改由毂盘内环定位), 盘底除 S/M 凸台外全平",
           f"外圈 8 孔 r{F(B.RH_R)} @22.5°+45°k 与定子外圈上下对齐; V1.0 原 R82.5 孔补实",
           f"罩底孔 S @" + "/".join(F(a) for a in B.SHR_ANG) + "° (避开底板与立板耳朵); 两端 T 脚 / 中间 T 件孔填实; C / X 孔为 V1.0 原有",
           f"装配: 底板螺丝头在承载盘底面, 所以先把底板装到承载盘上, 再把承载盘装到毂盘上 (毂盘在螺丝头下让位 Φ{F(B.HUB_BB_CLR_D)})"]))

# ---------------- 毂盘 hub_disc_v1_2 (build_v1_2.py; export_3mf 写 out/打印STL (原姿态落床); 出图现写装配坐标 STL) ----------------
_HZ0, _HZ1 = B.bbox(B.hub)[2], B.bbox(B.hub)[5]                                # Z21.5 / Z30.5
_H_TOP = B.RIM_BOT                                                              # 两圈接触环顶 (= 承载盘底, 11-16 晚 加高)
_H_BOSS = (B.RIM_BORE_R,)                                                       # 中心凸台 R25 (伸进承载盘内孔)
_H_GROOVE = (B.HUB_RAISE[0][1], B.HUB_RAISE[1][0], min(c[2] for c in cyl_at(B.hub, 2 * B.HUB_RAISE[0][1], centered=True)))   # 环槽 (线圈腔) R39.9–72.4 (11-17), 槽底 Z 实测
_HUB_R = B.HUB_RAISE[1][1]
# 外圈 8 孔 (B.RH_PTS, B.RH_INS) / 电机 4 孔 (B.ROTOR_R) / 盘心窝 (B.POCKET_*); r30 锁盘 + 方 4 孔 V1.0 原有 ⇒ 实测
_h42 = [c for c in cyl_at(B.hub, 4.2) if abs(math.hypot(c[0], c[1]) - B.RH_R) > 0.5]
_hl = list(by_r(_h42, 8).values())[0]                                           # r30 ×8
_hq = list(by_r(_h42, 4).values())[0]                                           # (±15, ±15) ×4
_H_LOCK = math.hypot(_hl[0][0], _hl[0][1])
_hm_pts = [(sx * B.ROTOR_R * B.s45, sy * B.ROTOR_R * B.s45) for sx in (1, -1) for sy in (1, -1)]
_hm_th = [c for c in cyls(B.hub) if math.hypot(c[1] - _hm_pts[0][0], c[2] - _hm_pts[0][1]) < 0.1]
_HM_d = min(c[0] for c in _hm_th); _HM_D = max(c[0] for c in _hm_th)
_HM_CB0 = min(c[3] for c in _hm_th if c[0] == _HM_D)                            # 沉孔底 Z26.5
_ins_h = lambda rows: rows[0][3] - rows[0][2]                                   # noqa: E731
_hu = [c for d in (B.HUB_BOSS_CLR_D, B.HUB_BB_CLR_D) for c in cyl_at(B.hub, d)]   # 加高环上的让位 (实测: 实际落在环上的才有)
SPECS.append(dict(
    code="hub_disc_v1_2", shape=B.hub, short=f"毂盘 Φ{F(2 * _HUB_R)}", qty="1", stl_asm=True,
    title=f"转子毂盘 Φ{F(2 * _HUB_R)}: 嵌进承载盘裙边 r{F(B.RIM_SKIRT[0])}–{F(B.RIM_SKIRT[1])}; 底面外圈 8×M3 铜螺母 r{F(B.RH_R)}",
    subtitle=f"Z{F(_HZ0)}–{F(_HZ1)} (底面 = 电机顶 Z{F(B.ROTOR_TOP)}); 铜螺母全部从底面压入; 电机 4 孔顶面沉孔",
    orient=f"原姿态: 底面 (Z{F(_HZ0)}) 贴床, 凸台朝上 (out/打印STL 已是此姿态)",
    phi=[2 * _H_BOSS[0], 2 * _H_GROOVE[0], 2 * _H_GROOVE[1], 2 * _HUB_R],
    sec=dict(ang=0, r0=20.0, auto_dims=False,
             zd=[(_HZ0, _H_GROOVE[2]), (_H_GROOVE[2], _H_TOP), (_H_TOP, _HZ1), (_HZ0, _H_TOP), (_HZ0, _HZ1)],
             rd=[(_H_BOSS[0], _H_GROOVE[0], f"内环 {F(_H_GROOVE[0] - _H_BOSS[0])} mm (凸台 R{F(_H_BOSS[0])} → 槽 R{F(_H_GROOVE[0])})"),
                 (_H_GROOVE[0], _H_GROOVE[1], f"环槽宽 {F(_H_GROOVE[1] - _H_GROOVE[0])} mm (R{F(_H_GROOVE[0])}–R{F(_H_GROOVE[1])})"),
                 (_H_GROOVE[1], _HUB_R, f"外环 {F(_HUB_R - _H_GROOVE[1])} mm (R{F(_H_GROOVE[1])}–R{F(_HUB_R)})")]),
    holes=[dict(tag="R", pts=B.RH_PTS, spec=f"Φ3.4 通 + 底面 Φ4.2×{F(B.RH_INS[1] - B.RH_INS[0])} 铜螺母孔 (M3×4 铜螺母齐底面)",
                where=ring_txt(B.RH_PTS) + f"  铜螺母 Z{F(B.RH_INS[0])}–{F(B.RH_INS[1])}, 承载盘 R 孔螺丝从上往下\n"
                      f"k={'/'.join(str(k) for k in B.RH_EAR_IDX)} ({_ang_txt(_rh_ear)}) 被立板耳朵压住: M3×{F(L.FOOT_SCREW_L)}; "
                      f"k={'/'.join(str(k) for k in B.RH_STD_IDX)} ({_ang_txt(_rh_std)}): M3×{F(B.RH_L)}",
                det=dict(kind="ins", d=3.4, D=4.2, h=B.RH_INS[1] - B.RH_INS[0], side="bot", z=(_HZ0, _H_TOP), pt=B.RH_PTS[0], title="外圈铜螺母孔 R (径向剖)")),
           dict(tag="L", pts=[(c[0], c[1]) for c in _hl], spec=f"Φ3.2 通 + 底面 Φ4.2×{F(_ins_h(_hl))} 铜螺母孔 (r{F(_H_LOCK)} 锁盘, V1.0 原有)",
                where=ring_txt([(c[0], c[1]) for c in _hl]) + "  = 承载盘 L 孔, 螺丝从承载盘顶往下",
                det=dict(kind="ins", d=3.2, D=4.2, h=_ins_h(_hl), side="bot", z=(_HZ0, _H_TOP), pt=(_hl[0][0], _hl[0][1]), title="锁盘铜螺母孔 L (径向剖)")),
           dict(tag="Q", pts=[(c[0], c[1]) for c in _hq], spec=f"Φ3.2 通 + 底面 Φ4.2×{F(_ins_h(_hq))} 铜螺母孔 (V1.0 原有, 现未用)", where=xy([(c[0], c[1]) for c in _hq]), lab_off=(-2.4, 2.4)),
           dict(tag="E", pts=_hm_pts, spec=f"Φ{F(_HM_d)} 通 + 顶面 Φ{F(_HM_D)}×{F(_HZ1 - _HM_CB0)} 沉孔 (电机转子)",
                where=f"对角 {F(2 * B.ROTOR_R)} (r{F(B.ROTOR_R)} @45°+90°k)", lab_off=(2.4, -2.4),
                det=dict(kind="cb", d=_HM_d, D=_HM_D, h=_HZ1 - _HM_CB0, side="top", z=(_HZ0, _HZ1), pt=_hm_pts[0], title="电机沉孔 E (径向剖)")),
           *([dict(tag="U", pts=[(c[0], c[1]) for c in _hu], spec=f"接触环让位: 承载盘凸台下 Φ{F(B.HUB_BOSS_CLR_D)} / 底板螺丝头下 Φ{F(B.HUB_BB_CLR_D)}, 顶面 Z{F(_H_TOP)} 往下到 Z{F(min(c[2] for c in _hu))}",
                  where=xy([(c[0], c[1]) for c in _hu], 3), lab_off=(2.4, -2.4))] if _hu else [])],
    dets=[dict(tag="K", kind="blind", D=B.POCKET_D, h=B.POCKET_H, side="bot", z=(_HZ0, _HZ1), pt=(0.0, 0.0), ang=0.0, W=5.0,
               title=f"盘心 Φ{F(B.POCKET_D)}×{F(B.POCKET_H)} 盲窝 (底面, 电机轴头)")],
    notes=[f"剖视竖向 (左→右): 槽底板 {F(_H_GROOVE[2] - _HZ0)} / 环槽深 {F(_H_TOP - _H_GROOVE[2])} / 中心凸台 {F(_HZ1 - _H_TOP)} / 盘厚 (外环、内环) {F(_H_TOP - _HZ0)} / 总高 {F(_HZ1 - _HZ0)}",
           f"外径 Φ{F(2 * _HUB_R)} (r{F(_HUB_R)}), 嵌进承载盘裙边 r{F(B.RIM_SKIRT[0])}–{F(B.RIM_SKIRT[1])}, Z{F(_HZ0)}–{F(_HZ1)}",
           f"底面平 Z{F(_HZ0)}; 顶面: 外环 R{F(_H_GROOVE[1])}–{F(_HUB_R)} 与内环 R{F(_H_BOSS[0])}–{F(_H_GROOVE[0])} 顶 Z{F(_H_TOP)} 托承载盘, "
           f"环槽 (线圈腔) R{F(_H_GROOVE[0])}–{F(_H_GROOVE[1])} 深 {F(_H_TOP - _H_GROOVE[2])};",
           f"11-17: 内环外圆 Φ{F(2 * _H_GROOVE[0])} 套线圈内径 Φ{F(B.COIL_ID)}; 外环 (铜螺母环) 宽 {F(_HUB_R - _H_GROOVE[1])}; 线圈外径需 ≤ Φ{F(2 * _H_GROOVE[1])};  中心凸台 R{F(_H_BOSS[0])} 高 {F(_HZ1 - _H_TOP)} 穿承载盘内孔",
           f"外圈 8 孔 (R) 中 k={'/'.join(str(k) for k in B.RH_EAR_IDX)} 被立板耳朵压住, 用 M3×{F(L.FOOT_SCREW_L)}; k={'/'.join(str(k) for k in B.RH_STD_IDX)} 用 M3×{F(B.RH_L)} (头压承载盘顶)",
           "铜螺母 M3×4 全部从底面压入 (贴床面, 打印后再压); V1.0 原电机菱形 4 孔已补实",
           f"电机 E 组 4 颗从顶面沉孔往下拧进电机转子; 盘心窝 Φ{F(B.POCKET_D)}×{F(B.POCKET_H)} 让电机轴头"]))

# ---------------- V2 灯板支撑四件 (11-16 晚 偏心 SCR_ECC + 耳朵脚 + 中间 T 件取消; led_support_v1_2.py) ----------------
import rotor_shroud_v1_2 as RS  # noqa: E402  (罩壁半径等, 下面立板说明也用)
_fa = [p for p in L.FOOT_PTS if p[0] > 0]; _fb = [p for p in L.FOOT_PTS if p[0] < 0]
_eng = lambda bear, L_, ins: min(bear, ins[1]) - max(bear - L_, ins[0])
_EY = L.ECC


def _foot_hole(pts):
    return dict(tag="F", pts=pts, spec=f"耳朵 Φ3.4 通 (厚 {F(L.EAR_T)}, 无沉孔; M3×{F(L.FOOT_SCREW_L)} 内六角 头压耳朵顶 Z{F(L.FOOT_CB_Z)})",
                where=xy(pts) + f"  = 外圈锁盘孔 r{F(L.R_HOLE)}; 穿耳朵 + 承载盘 → 毂盘底 M3×4 铜螺母 Z{F(L.HUB_INS[0])}–{F(L.HUB_INS[1])}, 啮合 {F(_eng(L.FOOT_CB_Z, L.FOOT_SCREW_L, L.HUB_INS))}",
                det=dict(kind="free", z=(L.RIM_TOP, L.EAR_Z1), pt=pts[0], ang=0, W=L.EAR_PAD_D / 2 + 1.0, title="耳朵孔 F (沿 x 剖)",
                         zd=[(L.RIM_TOP, L.EAR_Z1, F(L.EAR_T))], ud=[(-1.7, 1.7, "Φ3.4"), (-L.EAR_PAD_D / 2, L.EAR_PAD_D / 2, f"Φ{F(L.EAR_PAD_D)}", 5)]))


_h1 = lambda sx: dict(tag="B", pts=[(sx * L.BAR_SCR_X[0], _EY)], spec=f"Φ3.4 通 + 底面 Φ6 沉孔深 {F(L.BAR_SCR_BEAR - L.RIM_TOP)} (M3×{F(L.BAR_SCR_L)} 内六角从下往上, 头支承 Z{F(L.BAR_SCR_BEAR)})",
                      where=f"({F(sx * L.BAR_SCR_X[0])}, {F(_EY)})  锁夹条 led_bar (夹条 Φ{F(L.BAR_TAP_D)} 自攻孔)", lab_off=(2.4, -3.0),
                      det=dict(kind="cb", d=3.4, D=6.0, h=L.BAR_SCR_BEAR - L.RIM_TOP, side="bot", z=(L.RIM_TOP, L.Z0), pt=(sx * L.BAR_SCR_X[0], _EY), ang=90, title="夹条螺丝孔 B (底面沉孔)"))
_post_notes = [
    f"整组灯板偏心 SCR_ECC = {F(B.SCR_ECC)} (沿 y): 横杆 x{F(L.T_X - L.T_W / 2)}–{F(L.T_X + L.T_W / 2)} |y−({F(_EY)})|≤{F(L.FOOT_Y)} Z{F(L.RIM_TOP)}–{F(L.Z0)}, 顶面托夹条 + 两灯板下沿",
    f"耳朵: 横杆同宽沿 y 伸到两颗外圈锁盘孔, 端头 Φ{F(L.EAR_PAD_D)}, Z{F(L.RIM_TOP)}–{F(L.EAR_Z1)}; 外缘 ≤ r{F(L.R_CLIP)} (罩内壁 r{F(RS.R0)}); 原 T 脚铜螺母孔取消",
    f"腹板 + 天线板 x{F(L.ANT_X0)}–{F(L.ANT_X1)} 厚 {F(L.ANT_X1 - L.ANT_X0)}, y {F(L.ANT_Y[0])}…{F(L.ANT_Y[1])}, Z{F(L.RIM_TOP)}–{F(L.ANT_Z1)}, 在罩壁缝里, 外角 r≤{F(L.ANT_R_MAX)}",
    f"天线竖贴: 外面浅槽 {F(L.ANT_L)}×{F(L.ANT_W)}×{F(L.ANT_REC)} 贴 18.5×37.7 软板天线 (背胶), 长边沿 Z, 槽心 Z{F(L.ANT_ZC)}",
    f"装: 桌上 灯板 A/B + 夹条 (H1/H2 横穿) → 两端立板底面 M3×{F(L.BAR_SCR_L)} 往上锁夹条 → 整体放上转子 → 耳朵 4×M3×{F(L.FOOT_SCREW_L)} (兼锁盘)"]
_post = lambda sx: dict(
    shape=L.post_a if sx > 0 else L.post_b, qty="1", material="PETG (建议) / PLA",
    orient=f"正立 (底面 Z{F(L.RIM_TOP)} 贴床), 免支撑",
    sec=dict(ang=0 if sx > 0 else 180, r0=L.T_X - L.T_W / 2 - 3.0,
             zd=[(L.RIM_TOP, L.EAR_Z1, f"{F(L.EAR_T)} 耳"), (L.RIM_TOP, L.Z0, f"{F(L.Z0 - L.RIM_TOP)} 横杆"), (L.RIM_TOP, L.ANT_Z1)],
             rd=[(L.T_X - L.T_W / 2, L.ANT_X1), (L.ANT_X0, L.ANT_X1)]),
    holes=[_foot_hole(_fa if sx > 0 else _fb), _h1(sx)])
SPECS.append(dict(
    _post(+1), code="led_post_a_v1_2", short="灯板支撑 +x 端 (耳朵脚)",
    title=f"灯板支撑 +x 端: 横杆 + 两只耳朵压外圈锁盘螺丝 (22.5°/337.5°, M3×{F(L.FOOT_SCREW_L)}) + 底面 M3 锁夹条 + 竖贴天线板",
    notes=_post_notes + ["耳朵孔 = 外圈锁盘 k=0 (22.5°) / k=7 (337.5°)"]))
SPECS.append(dict(
    _post(-1), code="led_post_b_v1_2", short="灯板支撑 −x 端 (耳朵脚)",
    title=f"灯板支撑 −x 端: 横杆 + 两只耳朵压外圈锁盘螺丝 (157.5°/202.5°, M3×{F(L.FOOT_SCREW_L)}) + 底面 M3 锁夹条 + 竖贴天线板",
    notes=_post_notes + ["与 +x 端关于 x=0 镜像 (偏心沿 y, 镜像后 y 不变); 耳朵孔 = 外圈锁盘 k=3 (157.5°) / k=4 (202.5°)"]))

SPECS.append(dict(
    code="led_bar_v1_2", shape=L.bar_s, short="灯板夹条", qty="1", material="PETG (建议) / PLA",
    title=f"灯板夹条: 夹在两板 F 面之间 厚 {F(2 * L.GAP_HALF)}, Z{F(L.Z0)}–{F(L.BAR_Z1)} (两端到 Z{F(L.BAR_END_Z1)})" + (f", 长 ±{F(L.BAR_HX)} (转子盘B 让铜螺柱, 无螺丝孔)" if B.ROTOR_B else ", H1/H2 M3 横穿, 底面 2 竖孔"),
    subtitle=f"中面 y = {F(_EY)} (偏心 SCR_ECC); " + ("转子盘B: 无螺丝, 靠两板夹持 + F 面器件浅槽定位" if B.ROTOR_B else f"11-16 晚 中间 T 件取消 ⇒ 只两端立板竖螺丝固定 (x ±{F(L.T_X)})"),
    orient="侧放 (4.6 厚的面贴床), 免支撑",
    sec=dict(ang=0, r0=0.0, origin=(0.0, L.ECC), zd=[(L.Z0, L.BAR_Z1, F(L.BAR_Z1 - L.Z0)), (L.Z0, L.BAR_END_Z1, F(L.BAR_END_Z1 - L.Z0))], rd=[(0, L.BAR_HX, f"x±{F(L.BAR_HX)}")]),
    holes=([] if B.ROTOR_B else [dict(tag="T", pts=[(x, _EY) for x in L.BAR_SCR_X], spec=f"底面 Φ{F(L.BAR_TAP_D)} 竖孔深 {F(L.BAR_TAP_H)} (M3 自攻, 两侧被灯板夹住)",
                where="x " + " / ".join(F(x) for x in L.BAR_SCR_X) + f"  两端立板来的 M3×{F(L.BAR_SCR_L)} 进 {F(L.BAR_SCR_BEAR + L.BAR_SCR_L - L.Z0)}", lab_off=(2.4, 3.0)),
           dict(tag="H", pts=[(L.H1_X, _EY), (-L.H1_X, _EY)], spec=f"Φ3.4 沿 Y 横穿, 中心 Z{F(L.H1_Z)} (= 灯板 H1/H2)", where=f"x ±{F(L.H1_X)}  M3×{F(L.SCREW_H1_L)} 内六角 + M3 法兰螺母 (板-条-板)", lab_off=(2.4, -3.0))]) + [
           dict(tag="M", pts=[(x, _EY) for x, z in L.BAR_M2], spec=f"Φ2.4 沿 Y 横穿, Z{F(L.BAR_M2[0][1])} (= 灯板下中 M2 孔, 可选)", where="x ±23  可选 M2 薄头螺丝 (桥板与 LED 面之间只 3.0)", lab_off=(2.4, 3.0))],
    notes=[f"厚 {F(2 * L.GAP_HALF)} = 两板间隙 (每面收 0.01), 下沿齐灯板下沿 Z{F(L.Z0)}; |x|≥{F(L.BAR_END_X)} 加高到 Z{F(L.BAR_END_Z1)}",
           f"F 面器件处挖浅槽 {L.BAR_CUTS} 处 (器件包围盒 +0.3)",
           "原 ±38 两个中间 T 件竖孔取消 (11-16 晚)"] + ([f"11-20 夜(二) 转子盘B: 端头收短到 |x|≤{F(L.BAR_HX)} 让灯板 F 面开窗焊的六角铜螺柱 (x±{F(L.SO_X)} Z{F(L.SO_WIN_Z[0])}–{F(L.SO_WIN_Z[1])}, 每端 2 颗错开) + 屏幕竖螺丝; 两竖自攻孔 + H1/H2 横穿取消",
                                                                "现作用: 两板下沿之间的定距垫条 (保 5.0 间隙, F 面器件卡在浅槽里定位), 坐在两端侧立件上; 不再受螺丝力", "装: 夹进两板之间后再整组拧屏幕螺丝"]
                                                               if B.ROTOR_B else ["装: 先 H1/H2 两颗 M3 横穿夹紧, 再从下面锁两端立板"])))

SPECS.append(dict(
    code="led_top_v1_2", shape=L.top, short="灯板顶部件 (偏心帽 + 轴座在转轴)", qty="1", material="PETG (建议) / PLA",
    title=f"灯板顶部件: 舌 + 帽 {F(2 * L.CAP_X)}×{F(2 * L.CAP_Y)}×{F(L.CAP_T)} (y={F(_EY)}) + Φ{F(L.CAP_PAD_D)} 圆垫跨到转轴 + 轴座 Φ{F(L.BOSS_D)} 在 (0,0)",
    subtitle=f"偏心 SCR_ECC {F(B.SCR_ECC)}: 舌/帽随灯板平移, 轴座/钢轴 Φ{F(L.ROD_D)}×{F(L.ROD_L)} 仍在转轴 (0,0) 进 688",
    orient=f"倒放 (轴座顶 Φ{F(L.BOSS_D)} 贴床), 帽两端小悬空",
    sec=dict(ang=0, r0=0.0, origin=(0.0, L.ECC), zd=[(L.TOP_TONGUE_Z0, L.Z1, f"{F(L.Z1 - L.TOP_TONGUE_Z0)} 舌"), (L.Z1, L.Z1 + L.CAP_T, f"{F(L.CAP_T)} 帽"), (L.Z1 + L.CAP_T, L.BOSS_Z1, f"{F(L.BOSS_Z1 - L.Z1 - L.CAP_T)} 轴座")],
             rd=[(0, L.BOSS_D / 2, f"R{F(L.BOSS_D / 2)}"), (0, L.CAP_PAD_D / 2, f"R{F(L.CAP_PAD_D / 2)}"), (0, L.CAP_X, f"{F(L.CAP_X)}")]),
    holes=[dict(tag="R", pts=[(0.0, 0.0)], spec=f"Φ{F(L.ROD_HOLE_D)} 盲孔深 {F(L.BOSS_Z1 - L.ROD_Z0)} (压 Φ8 h6 钢轴, 试配)", where="轴心 (0, 0)",
                det=dict(kind="blind", D=L.ROD_HOLE_D, h=L.BOSS_Z1 - L.ROD_Z0, side="top", z=(L.Z1 + L.CAP_T, L.BOSS_Z1), pt=(0.0, 0.0), title="轴孔 R")),
           dict(tag="N", pts=[(L.COMB_FIX_X, _EY), (-L.COMB_FIX_X, _EY)], spec=f"Φ4.2 通帽 (厚 {F(L.CAP_T)}) 压 M3×4 铜螺母",
                where=f"(±{F(L.COMB_FIX_X)}, {F(_EY)})  梳齿 led_comb 用 M3×8 锁帽 (孔下是两板间隙)", lab_off=(2.4, -3.0))],
    notes=[f"舌 x±{F(L.TONGUE_X)} 厚 {F(L.BLADE_T)} Z{F(L.TOP_TONGUE_Z0)}–{F(L.Z1)} 插两板之间 (上中窗), 中面 y={F(_EY)}; 帽底贴板上沿 Z{F(L.Z1)}",
           f"帽只到 y={F(_EY + L.CAP_Y)} ⇒ 帽下加 Φ{F(L.CAP_PAD_D)} 圆垫 (中心在转轴) 托住轴座",
           f"轴座 Z{F(L.Z1 + L.CAP_T)}–{F(L.BOSS_Z1)} (长 {F(L.BOSS_Z1 - L.Z1 - L.CAP_T)}), 顶离堵头爪尖 {F(L.BOSS_GAP)}",
           f"钢轴 Φ{F(L.ROD_D)}×{F(L.ROD_L)} h6 Z{F(L.ROD_Z0)}–{F(L.ROD_Z1)}, 压入轴座 {F(L.BOSS_Z1 - L.ROD_Z0)}; 688 Z{F(L.BRG_Z0)}–{F(L.BRG_Z1)}",
           "玻璃罩长度公差: 短 ≤2.0 轴顶进堵头 Φ9 让位; 长 ≤4.5 仍有 0.5 啮合"]))

_cxm = L.COMB_TEETH_X[-1] + L.COMB_TOOTH_W / 2
SPECS.append(dict(
    code="led_comb_v1_2", shape=L.comb_s, short="顶部配平梳齿", qty="1", material="PETG (建议) / PLA",
    title=f"顶部配平梳齿: 中心环套轴座 (0,0) 坐帽顶, 横梁+齿随灯板偏心 (y={F(_EY)}), 2×M3×8 锁帽, 每侧 {len(L.COMB_TEETH_X)} 齿 × 4 孔挂配重",
    orient=f"平放 (底面 Z{F(L.COMB_Z0)} 贴床), 免支撑",
    phi=[L.COMB_HOLE_D, L.COMB_RING_D],
    sec=dict(ang=0, r0=0.0, origin=(0.0, L.ECC), zd=[(L.COMB_Z0, L.COMB_Z1)],
             rd=[(0, L.COMB_HOLE_D / 2), (0, L.COMB_RING_D / 2), (0, _cxm)], hmax=40),
    holes=[dict(tag="K", pts=[(L.COMB_FIX_X, _EY), (-L.COMB_FIX_X, _EY)], spec="Φ3.4 通; M3×8 内六角 → 帽内 M3×4 铜螺母 (啮合 4)",
                where=f"(±{F(L.COMB_FIX_X)}, {F(_EY)})", lab_off=(2.4, -3.0),
                det=dict(kind="free", z=(L.COMB_Z0, L.COMB_Z1), pt=(L.COMB_FIX_X, _EY), ang=0, W=3.6, title="锁帽孔 K (沿 x 剖)",
                         zd=[(L.COMB_Z0, L.COMB_Z1, F(L.COMB_T))], ud=[(-1.7, 1.7, "Φ3.4")])),
           dict(tag="W", pts=L.COMB_SLOTS, spec="Φ3.4 竖通 — 配重 M3 螺丝竖装 + 螺母 (按需)", lab_off=(0.0, 0.0),
                where=f"齿 x ±{'/'.join(F(v) for v in L.COMB_TEETH_X)} (宽 {F(L.COMB_TOOTH_W)}), 每齿 y {F(_EY)}±{F(L.COMB_SLOTS_Y[0])} / ±{F(L.COMB_SLOTS_Y[1])}; r≤{F(max(math.hypot(*p) for p in L.COMB_SLOTS))}",
                det=dict(kind="free", z=(L.COMB_Z0, L.COMB_Z1), pt=L.COMB_SLOTS[0], ang=0, W=4.6, title="配重孔 W (沿 x 剖)",
                         zd=[(L.COMB_Z0, L.COMB_Z1, F(L.COMB_T))], ud=[(-1.7, 1.7, "Φ3.4"), (-L.COMB_TOOTH_W / 2, L.COMB_TOOTH_W / 2, f"{F(L.COMB_TOOTH_W)} 齿宽", 5)]))],
    notes=[f"横梁 x±{F(_cxm)} |y−({F(_EY)})|≤{F(L.COMB_BEAM_Y)} + 中心环 Φ{F(L.COMB_RING_D)} (在转轴), 厚 {F(L.COMB_T)} Z{F(L.COMB_Z0)}–{F(L.COMB_Z1)}",
           f"中心孔 Φ{F(L.COMB_HOLE_D)} 套轴座 Φ{F(L.BOSS_D)} (单边 0.1), 坐顶部件帽顶 Z{F(L.COMB_Z0)}",
           f"齿 {F(L.COMB_TOOTH_W)} 宽沿 y ±{F(L.COMB_TOOTH_Y)}; 共 {len(L.COMB_SLOTS)} 个配重孔",
           f"配重 M3 螺丝竖装, 螺母在齿下 (> 板上沿 Z{F(L.Z1)}); 头下长 ≤{F(L.COMB_SCREW_MAX_L)} (每多叠 1 螺母 +2.4)",
           "两面配平的上面: 修残余不平衡 (led_support_report.json → balance), 以实测动平衡为准"]))

# ---------------- 转子罩 (11-16 晚 偏心后 A/B 不同件, rotor_shroud_v1_2.py; import 只建几何, 不写文件) ----------------


def _shr_spec(k):
    sx = 1 if k == "a" else -1
    sh = RS.shr_a if k == "a" else RS.shr_b
    rm = [RS.pol(RS.HOLE_R, a) for a in RS.MNT_A if math.cos(math.radians(a)) * sx > 0]
    rma = [a for a in RS.MNT_A if math.cos(math.radians(a)) * sx > 0]
    wa = [a for a in RS.W_A if math.cos(math.radians(a)) * sx > 0 and a not in RS.LID_SCR_ALL]
    rw = [RS.pol(RS.W_R, a) for a in wa]
    la = [a for a in RS.LID_SCR_ALL if math.cos(math.radians(a)) * sx > 0]
    nut_sy = 1 if k == "a" else -1                   # A 半 +y 缝凸耳带螺母槽, B 半 −y 缝 (B 未开缝时 = A 转 180°)
    other = "b" if k == "a" else "a"
    side = "+x" if k == "a" else "−x"
    return dict(
        code=f"rotor_shroud_{k}_v1_2", shape=sh, short=f"转子罩半壳 {k.upper()} ({side})", qty="1", material="PETG (建议) / PLA",
        title=f"转子罩半壳 {k.upper()} ({side} 半): 罩壁 r{F(RS.R0)}–{F(RS.R1)} + 罩底凸台 + 配重唇 + 分缝凸耳 + {side} 端天线缝",
        subtitle=f"11-16 晚 偏心后 {side} 端缝在 y {F(RS.SLOT_Y0)}…{F(RS.SLOT_Y1)} ⇒ A/B 两半不再是同件转 180°, 各打 1 个 (与 rotor_shroud_{other}_v1_2 配对)",
        orient=f"倒放 (罩顶 Z{F(RS.Z1)} 贴床); 配重唇比罩顶低 {F(RS.LID_T)} (给顶盖) ⇒ 唇下加热床支撑",
        sec=dict(ang=rma[0], r0=RS.BOSS_RI - 3.0, zd=[(RS.Z0, RS.Z1), (RS.Z0, RS.BOSS_Z1, f"{F(RS.BOSS_Z1 - RS.Z0)} 凸台"), (RS.LIP_Z0, RS.LID_Z0, f"{F(RS.LID_Z0 - RS.LIP_Z0)} 唇")],
                 rd=[(RS.R0, RS.R1, f"{F(RS.R1 - RS.R0)} 壁"), (RS.BOSS_RI, RS.R0, f"{F(RS.R0 - RS.BOSS_RI)} 凸台")]),
        holes=[dict(tag="M", pts=rm, spec=f"Φ3.4 通凸台 Z{F(RS.Z0)}–{F(RS.BOSS_Z1)} + 上方 Φ{F(RS.ACC_D)} 起子让位孔 (斜撑/配重唇)",
                    where=xy(rm) + f"  r{F(RS.HOLE_R)} @ " + "/".join(F(a) for a in rma) + f"°\nM3×{F(RS.MNT_L)} 内六角 头支承 Z{F(RS.BOSS_Z1)}, 进承载盘顶面 M3×4 铜螺母 Z{F(RS.INS_Z[0])}–{F(RS.INS_Z[1])}",
                    det=dict(kind="free", z=(RS.Z0, RS.GUS_Z1 + 1), pt=rm[0], W=RS.ACC_D / 2 + 2.0, title="罩底凸台孔 M (径向剖)",
                             zd=[(RS.Z0, RS.BOSS_Z1, f"{F(RS.BOSS_Z1 - RS.Z0)} 凸台")], ud=[(-1.7, 1.7, "Φ3.4"), (-RS.ACC_D / 2, RS.ACC_D / 2, f"Φ{F(RS.ACC_D)} (上)", 5)])),
               dict(tag="W", pts=rw, spec=f"Φ3.4 通配重唇 + 顶面 Φ{F(RS.W_CB_D)} 沉孔深 {F(RS.W_CB_H)}", lab_off=(-2.6, 2.0),
                    where=f"r{F(RS.W_R)} @ " + "/".join(F(a) for a in wa) + "°"
                          + f"\nM3×{F(RS.W_L)} 内六角 头顶 Z{F(RS.W_BEAR + 3)} < 盖底 Z{F(RS.LID_Z0)}; 唇下挂 ≤{RS.W_NUT_MAX} 颗 M3 螺母 (尾 Z{F(RS.W_TIP)})",
                    det=dict(kind="cb", d=3.4, D=RS.W_CB_D, h=RS.W_CB_H, side="top", z=(RS.LIP_Z0, RS.LID_Z0), pt=rw[0], title="配重孔 W")),
               dict(tag="C", pts=[RS.pol(RS.W_R, a) for a in la], spec=f"Φ3.4 通配重唇 + 切向缺槽 {F(RS.LID_BOSS_W + 0.4)} 宽 × 深 {F(RS.LID_BOSS_H + 0.1)} (顶盖凸块插入)",
                    where=f"r{F(RS.W_R)} @ " + "/".join(F(a) for a in la) + f"°  顶盖 M3×{F(RS.LID_SCR_L)} + 唇下 M3 螺母", lab_off=(2.6, -2.0)),
               dict(tag="S", pts=[(sx * RS.LUG_HX / 2, RS.LUG_SY), (sx * RS.LUG_HX / 2, -RS.LUG_SY)],
                    spec=f"凸耳 Φ3.4 沿 X 横穿 ×2 层 (Z{F(RS.LUG_SZ[0])} / Z{F(RS.LUG_SZ[1])}), M3×{F(RS.SEAM_L)} + M3 螺母",
                    where=f"|y|{F(RS.LUG_SY)}; {'+y' if nut_sy > 0 else '−y'} 缝凸耳带六角螺母槽 {F(RS.NUT_AF)} 对边 (口朝罩内), 另一缝是螺丝头侧",
                    det=dict(kind="free", z=(RS.LUG_Z0, RS.LIP_Z0 + 0.5), pt=(sx * RS.LUG_HX / 2, nut_sy * RS.LUG_SY), ang=0, W=RS.LUG_HX / 2 + 2.0, title=f"{'+y' if nut_sy > 0 else '−y'} 分缝凸耳 S (沿 x 剖)",
                             zd=[(RS.LUG_Z0, RS.LIP_Z0 + 0.5, F(RS.LIP_Z0 + 0.5 - RS.LUG_Z0)), (RS.LUG_SZ[0], RS.LUG_SZ[1], F(RS.LUG_SZ[1] - RS.LUG_SZ[0]), 9)],
                             ud=[(-RS.LUG_HX / 2, RS.LUG_HX / 2, F(RS.LUG_HX))]))],
        notes=[f"罩壁 r{F(RS.R0)}–{F(RS.R1)} Z{F(RS.Z0)}–{F(RS.Z1)} (外圆 Φ{F(2 * RS.R1)}, 承载盘 Φ{F(B.RIM_D)}; 离不转玻璃座内壁 r{F(RS.ST_IN)} 留 {F(RS.ST_IN - RS.R1)}); 分缝在 x=0",
               f"{side} 端天线竖缝 y {F(RS.SLOT_Y0)}…{F(RS.SLOT_Y1)} 全高 (天线板 y {F(L.ANT_Y[0])}…{F(L.ANT_Y[1])} 各让 {F(RS.SLOT_CLR)}), 从 |x|{F(RS.SLOT_X0)} 往外切",
               f"罩底 4 凸台 r{F(RS.HOLE_R)} @" + "/".join(F(a) for a in RS.MNT_A) + "° (本半 " + "/".join(F(a) for a in rma) + "°) 坐承载盘顶 + 45° 斜撑, 避开底板 r4b / 立板耳朵 / 无线托盘",
               f"配重唇 r{F(RS.LIP_R0)}–{F(RS.R0)} Z{F(RS.LIP_Z0)}–{F(RS.LID_Z0)} @ " + " / ".join(f"{F(a0)}°–{F(a1)}°" for a0, a1 in RS.LIP_ARCS) + f"; 全罩 {len(RS.W_A)} 孔 r{F(RS.W_R)} (其中 4 个给顶盖螺丝)",
               f"分缝凸耳 x0–{F(sx * RS.LUG_HX)} × |y|{F(RS.LUG_Y0)}–{F(RS.LUG_Y1)} × Z{F(RS.LUG_Z0)}–{F(RS.LIP_Z0)} (底 > 无线托盘顶 Z50)",
               f"装/拆: 先拆顶盖, 起子从罩顶开口竖直进, 穿 Φ{F(RS.ACC_D)} 让位孔拧罩底 M3×{F(RS.MNT_L)}; 配重见 rotor_shroud_report.json"])


SPECS.append(_shr_spec("a"))
SPECS.append(_shr_spec("b"))


def _lid_spec(k):
    sy = 1 if k == "a" else -1
    code = "rotor_lid_v1_2" if k == "a" else "rotor_lid_b_v1_2"
    la = RS.LID_SCR_A if k == "a" else [a + 180 for a in RS.LID_SCR_A]
    lp = [RS.pol(RS.W_R, a) for a in la]
    yin = RS.LID_YIN[k]
    x0, yb = RS.BR_POCKET[k]
    side = "+y" if k == "a" else "−y"
    return dict(
        code=code, shape=RS.lid_a if k == "a" else RS.lid_b, short=f"转子罩顶盖 {side} 片", qty="1", material="PETG (建议) / PLA",
        title=f"转子罩顶盖 {side} 片: D 形板厚 {F(RS.LID_T)}, 内边 y{F(yin)}, 顶面 Z{F(RS.Z1)} = 罩顶 = 玻璃托顶",
        subtitle=f"11-16 晚 偏心: {'板 A' if k == 'a' else '板 B'} MIP 顶 y≈{F(RS.ECC + sy * (RS.Y_LED0 + RS.MIP_H))} ⇒ 两片顶盖不同件 (另一片 {'rotor_lid_b_v1_2' if k == 'a' else 'rotor_lid_v1_2'}); 坐配重唇顶 Z{F(RS.LID_Z0)}, 外圆 r{F(RS.LID_R)} 嵌罩壁 r{F(RS.R0)}",
        orient="顶面贴床 (平底沉孔口朝床), 凸块朝上, 免支撑",
        sec=dict(ang=90 if k == "a" else 270, r0=0.0, zd=[(RS.LID_Z0, RS.Z1, F(RS.LID_T)), (RS.LID_Z0 - RS.LID_BOSS_H, RS.Z1, f"{F(RS.LID_T + RS.LID_BOSS_H)} 凸块")],
                 rd=[(abs(yin), RS.LID_R, f"y{F(yin)}–r{F(RS.LID_R)}")]),
        holes=[dict(tag="C", pts=lp, spec=f"Φ3.4 通 + 顶面平底沉孔 Φ{F(RS.LID_CB_D)} 深 {F(RS.LID_CB_H)} (底下凸块 {F(RS.LID_BOSS_RAD[1] - RS.LID_BOSS_RAD[0])}×{F(RS.LID_BOSS_W)}×{F(RS.LID_BOSS_H)} 插配重唇缺槽)",
                    where=xy(lp) + f"  r{F(RS.W_R)} @ " + "/".join(F(a) for a in la) + f"° (对准配重唇缺槽)\nM3×{F(RS.LID_SCR_L)} 内六角 DIN912, 头顶齐盖顶, 穿凸块底 + 唇, 唇下 M3 螺母",
                    det=dict(kind="cb", d=3.4, D=RS.LID_CB_D, h=RS.LID_CB_H, side="top", z=(RS.LID_Z0 - RS.LID_BOSS_H, RS.Z1), pt=lp[0], title="沉孔 C (过凸块)"))],
        notes=[f"内边 y{F(yin)} (LED 面 + MIP 0.59, 留 0.44); 桥板段 x{F(x0)}…{F(-x0)} 通槽退到 y{F(yb)} (桥板顶 Z73.0)",
               f"两端缺口 |x|≥{F(RS.ANT_NOTCH[0])}, y {F(RS.ANT_NOTCH[1])}…{F(RS.ANT_NOTCH[2])}: 让立板天线板 (顶 Z{F(L.ANT_Z1)})",
               f"LED 面伸进盖高度的器件按包围盒 +0.4 让开 ({RS.LID_LED_CUTS[k]} 处)",
               "装: 罩两半装好、配重调完后放盖 (凸块插进唇缺槽定位), 2 颗 M3×8 内六角 + 唇下螺母锁; 拆盖才能调配重 / 拧罩底螺丝"])


SPECS.append(_lid_spec("a"))
SPECS.append(_lid_spec("b"))

# ---------------- 无线供电模块两件对称夹块 (11-19 用户改, wireless_holder_v1_2.py; import 只建几何) ----------------
import json as _json  # noqa: E402
import wireless_holder_v1_2 as WH  # noqa: E402
try:
    _whb = _json.load(open(M / "wireless_holder_v1_2" / "wireless_holder_report.json"))["balance"]
    _wh_bal = f"每件 {F(_whb['clamp_each_g'])} g; 两件 + 模块 + 螺丝 ≈ {F(_whb['total_g'])} g, 质心 ({F(_whb['total_cog'][0])}, {F(_whb['total_cog'][1])}); 1200 rpm 离心力 ≈ {F(_whb['F_centrifugal_N_1200rpm'])} N"
except Exception:
    _wh_bal = "质量 / 质心 / 离心力见 wireless_holder_report.json"
_wh_ey = WH.EXIT_Y[1]
SPECS.append(dict(
    code="wireless_holder_v1_2", shape=WH.HA, stl_asm=True, short="无线模块夹块 wireless_clamp_v1_2", qty="2 (同一件, 转 180° 装两侧)", material="PETG (建议) / PLA", date="2026-11-19",
    title=f"无线供电模块夹块 (倒 L, 两件对称) {F(WH.XO - WH.XI)}×{F(WH.BY1 - WH.BY0)}×{F(WH.TOP_Z - WH.RIM_TOP)}: 立柱 {F(WH.COL_W)} (M3 法兰螺母) + 上沿 {F(WH.GRIP)}×{F(WH.CAP_T)} 压 PCB + y 端挡块 {F(WH.END_T)}",
    subtitle=f"图为 +x 装配位; −x 侧同一件绕 Z 转 180° (件自身 y 对称)。打印 STL wireless_clamp_v1_2.stl。PCB {F(WH.MOD_L)}×{F(WH.MOD_W)} Z{F(WH.MZ0)}–{F(WH.PCB_Z1)} (顶面离承载盘顶 {F(WH.PCB_TOP_GAP)}), y {F(WH.MOD_Y0)}…{F(WH.MOD_Y1)}; 整组外包 {F(2 * WH.XO)}×{F(WH.BY1 - WH.BY0)}, PCB 端贴立柱、y 向两挡块净距 {F(WH.MOD_W + 2 * WH.END_CLR)} (每边留 {F(WH.END_CLR)})",
    orient=f"正立 (底面 Z{F(WH.RIM_TOP)} 贴床); 上沿 {F(WH.GRIP)} 悬臂 (下空 {F(WH.LIP_Z0 - WH.RIM_TOP)}), 建议上沿朝下翻转打印或加支撑",
    sec=dict(ang=0, r0=WH.XI - 1.0, r1=WH.XO + 1.0, origin=(0.0, (WH.EXIT_Y[0] + WH.EXIT_Y[1]) / 2),
             zd=[(WH.RIM_TOP, WH.LIP_Z0, f"{F(WH.LIP_Z0 - WH.RIM_TOP)} 上沿下空"), (WH.LIP_Z0, WH.TOP_Z, f"{F(WH.CAP_T)} 上沿"), (WH.RIM_TOP, WH.TOP_Z, f"{F(WH.TOP_Z - WH.RIM_TOP)} 总高")],
             rd=[(WH.XI, WH.XC0, f"{F(WH.GRIP)} 上沿"), (WH.XC0, WH.XO, f"{F(WH.COL_W)} 立柱")]),
    holes=[dict(tag="M", pts=[WH.SCR_OUT[0], WH.SCR_IN[0]], spec=f"Φ3.4 竖直通孔 (立柱中心), 顶面拧 M3 法兰螺母 (法兰 Φ{F(WH.NUT_FL_D)}, 带齿防松)",
                where=xy([WH.SCR_OUT[0], WH.SCR_IN[0]], 2) + f"\nM3×{F(WH.SCR_L)} 超薄头从承载盘底往上 (同底板, 头支承 Z{F(WH.CB_Z)}) → 穿立柱 → 顶面螺母 Z{F(WH.TOP_Z)}–{F(WH.TOP_Z + WH.NUT_H)}",
                det=hole_det(WH.HA, WH.SCR_IN[0], "螺丝通孔 M", W=4.0, z=(WH.RIM_TOP, WH.TOP_Z))),
           dict(tag="E", pts=[(WH.EXIT_X, y) for y in WH.EXIT_Y], spec=f"焊脚开窗: 只开上沿, x {F(WH.GRIP)} (全宽) × y 以脚为心 ±{F(WH.OPEN_DY)} (靠挡块侧并到挡块面), 竖直敞开",
                where="开窗 " + " / ".join(f"x{F(b[0])}–{F(b[2])} y{F(b[1])}…{F(b[3])}" for b in WH.OPEN_BOX) + "\n+x 侧: AC1/AC2; −x 侧: GND/24V")],
    notes=[f"截面: 立柱 x {F(WH.COL_W)} × 高 {F(WH.TOP_Z - WH.RIM_TOP)}; 上沿 x {F(WH.GRIP)} × 厚 {F(WH.CAP_T)} (Z{F(WH.LIP_Z0)}–{F(WH.TOP_Z)}) 压 PCB 顶, 上沿下空 (不托 PCB)",
           f"PCB 端面贴立柱内侧面、两侧贴 y 端挡块 ({F(WH.END_T)} 厚, 盘面通到上沿), 零间隙 (用户「不留间隙」)",
           f"装: 两件套上 PCB 放到承载盘 → 从承载盘底穿 4×M3×{F(WH.SCR_L)} 超薄头, 立柱顶拧法兰螺母 (线圈/玻纤板装之前, 同底板) → 装线圈, AC 线从承载盘 Φ{F(B.AC_HOLE_D)} 孔 {xy(list(WH.AC_HOLES), 2)} (线圈腔正上方) 竖上来, 跨 a 件进开窗 → 从上面焊 4 根线",
           "24V/GND 从 b 件开窗出, 沿盘面去底板",
           f"假设待实物核: PCB 厚 {F(WH.PCB_T)}; 元件在 PCB 上方中段 |x|≤{F(WH.COMP_X)}; 脚位按底板 r1 封装推算", _wh_bal]))

# ---------------- 底盘 MR30 座 + 电机线束线夹 (11-16 晚, motor_wire_v1_2.py; import 只建几何; 出图 STL 由本脚本按装配坐标写 out/dwg_stl/) ----------------
import io as _io, contextlib as _cl  # noqa: E401,E402
with _cl.redirect_stdout(_io.StringIO()):
    import motor_wire_v1_2 as MW  # noqa: E402
_mr = MW.MR_INS; _cl_ = MW.CL_INS
SPECS.append(dict(
    code="mr30_seat_v1_2", shape=MW.mr30_split()[0], stl_asm=True, short="MR30 座上件 (电机线接头)", qty="1", material="PETG (建议) / PLA",
    title=f"MR30 座: {F(2 * MW.SEAT_HX)}×{F(MW.Y_OPEN - MW.Y_R)}×{F(MW.SEAT_H)} 坐底盘顶, 夹 MR30-M 公头 (护套 −y 接电机线, 开口 +y 插母头)",
    subtitle=f"坐玻纤板顶 Z0, −x 侧 x{F(MW.MR_XC - MW.SEAT_HX)}…{F(MW.MR_XC + MW.SEAT_HX)} y{F(MW.Y_R)}…{F(MW.Y_OPEN)}; 顶 Z{F(MW.SEAT_H)} = 定子盘底 − 0.5",
    orient=f"顶面贴床 (槽口朝上), 底片在最上层跨 {F(MW.SHEATH_W)} 架桥, 免支撑", date="2026-11-18",
    sec=dict(ang=180, r0=44.0, r1=78.0, zd=[(0, MW.SEAT_H, F(MW.SEAT_H))]),
    holes=[dict(tag="N", pts=_mr, spec=f"Φ{F(MW.PASS_D)} 通 + 顶面 Φ{F(MW.INS_D)}×{F(MW.INS_H)} 热压 M3×4 铜螺母 (顶齐件顶)",
                where=xy(_mr) + f"  M3×{F(MW.SCREW_L[0])} 超薄头从打印底盘底面 Φ{F(B.M3_CB_D)}×{F(B.M3_CB_H)} 沉孔往上 (头支承 Z{F(MW.BEAR_Z)}), 尖 Z{F(MW.SEAT_H)} 啮合 4",
                det=dict(kind="ins", d=MW.PASS_D, D=MW.INS_D, h=MW.INS_H, side="top", z=(0, MW.SEAT_H), pt=_mr[0], ang=90, title="铜螺母孔 N (沿 y 剖)"))],
    notes=[f"槽: 本体段 {F(MW.BODY_W)} 宽 Z{F(MW.Z_BD0)}..{F(MW.Z_BD1)} / 护套段 {F(MW.SHEATH_W)} 宽 Z{F(MW.Z_SH0)}..{F(MW.Z_SH1)}, 零间隙",
           f"11-18 拆 2 件: 本件 = 上件 Z{F(MW.FLOOR_T)}..{F(MW.SEAT_H)} (顶板 {F(MW.T_TOP)}); 底片另出 mr30_floor (护套段 {F(MW.FLOOR_T)} / 本体段 {F(MW.Z_BD0)}); 装: 下片 → 公头 → 扣本件 → 2×M3",
           f"后墙 {F(MW.REAR_T)} 厚, 出线口 {F(2 * MW.SLOT_HW)}×3 长圆 (3×Φ3 电机线并排, 线心 Z{F(MW.PIN_Z)})",
           "插母头: 护套尾面顶后墙; 拔母头: 护套台肩顶槽台阶 (两侧 + 顶 + 底片台阶 0.25)",
           "⚠ 待用户确认: 公头朝向 / 母头外形 / 线径 Φ3"]))
SPECS.append(dict(
    code="motor_wire_clamp_v1_2", shape=MW.wire_clamp(), stl_asm=True, short="电机线束线夹", qty="1", material="PETG (建议) / PLA",
    title=f"电机线束线夹: 桥形压条 {F(2 * MW.CL_HX)}×{F(MW.CL_Y1 - MW.CL_Y0)}×{F(MW.CL_H)}, 底面通洞 {F(2 * MW.CL_CH_HW)}×{F(MW.CL_CH_H)} 沿 x (3×Φ3 线, 能滑动)",
    subtitle=f"坐玻纤板顶 Z0, x{F(MW.CL_XC - MW.CL_HX)}…{F(MW.CL_XC + MW.CL_HX)} y{F(MW.CL_Y0)}…{F(MW.CL_Y1)}; 只理线限位, 不卡紧",
    orient="顶面贴床 (线槽朝上), 免支撑", date="2026-11-18",
    sec=dict(ang=math.degrees(math.atan2(MW.CL_YC, MW.CL_XC)) % 360, r0=50.0, r1=82.0, zd=[(0, MW.CL_H, F(MW.CL_H)), (0, MW.CL_CH_H, F(MW.CL_CH_H))]),
    holes=[dict(tag="N", pts=_cl_, spec=f"Φ{F(MW.PASS_D)} 通 + 顶面 Φ{F(MW.INS_D)}×{F(MW.INS_H)} 热压 M3×4 铜螺母 (顶齐件顶)",
                where=xy(_cl_) + f"  M3×{F(MW.SCREW_L[2])} 超薄头从打印底盘底面 Φ{F(B.M3_CB_D)}×{F(B.M3_CB_H)} 沉孔往上 (头支承 Z{F(MW.BEAR_Z)}), 尖 Z{F(MW.CL_H)} 啮合 4",
                det=dict(kind="ins", d=MW.PASS_D, D=MW.INS_D, h=MW.INS_H, side="top", z=(0, MW.CL_H), pt=_cl_[0], ang=0, title="铜螺母孔 N (沿 x 剖)"))],
    notes=[f"线束中心 y{F(MW.CL_YC)}, 3 线 Φ3 贴在一起; 洞单边 +{F(MW.CL_CLR)}; 洞顶到件顶 {F(MW.CL_H - MW.CL_CH_H)}",
           f"走线: 出线口 → (30, −45) → 往下到 y≈−62 → 沿 x 穿本件 → (−40, −60) → (−64, −40) → MR30 座 −y 端",
           f"11-18 加宽: 孔离线束中心 ±{F(MW.CL_INS_DY)} (孔到线槽肉 {F(MW.CL_INS_DY - MW.INS_D / 2 - MW.CL_CH_HW)}), 端壁 {F(MW.EAR_H - MW.INS_D / 2)}"]))
# 11-18 用户: MR30 座 / 线夹两版 —— 上面两张 = 玻纤板版 (整机); _old = 配旧一体底盘 Φ220×6 (原孔位, 旧沉孔 Φ7×2 支承 Z-4)
for _base, _shape, _pts, _L in (("mr30_seat_v1_2", MW.mr30_split(MW.MR_INS_DX_OLD)[0], MW.mr_ins(MW.MR_INS_DX_OLD), 12.0),
                                ("motor_wire_clamp_v1_2", MW.wire_clamp(MW.CL_INS_DY_OLD), MW.cl_ins(MW.CL_INS_DY_OLD), 10.0)):
    _src = next(q for q in SPECS if q["code"] == _base)
    _h = dict(_src["holes"][0]); _h["pts"] = _pts
    _h["where"] = xy(_pts) + f"  M3×{F(_L)} 超薄头从旧一体底盘底面 Φ7×2 沉孔往上 (头支承 Z-4), 尖 = 件顶, 啮合 4"
    if "det" in _h: _h["det"] = dict(_h["det"], pt=_pts[0])
    _y0, _y1 = MW.cl_span(MW.CL_INS_DY_OLD)
    _ttl = _src["title"].replace(f"×{F(MW.CL_Y1 - MW.CL_Y0)}×", f"×{F(_y1 - _y0)}×") if "clamp" in _base else _src["title"]
    SPECS.append(dict(_src, code=_base + "_old", shape=_shape, holes=[_h], short=_src["short"] + " (旧底盘版)", title=_ttl,
                      subtitle="_old 版: 配旧一体底盘 Φ220×6 (不带玻纤板), 原孔位; " + _src["subtitle"].split("; ", 1)[-1], date="2026-11-18",
                      notes=["_old 版: 配不带玻纤板的旧一体底盘 base_disc_v1_2 (Φ220×6), 孔位 = 原位; 玻纤板版孔各外移 1 (另一张图)"]
                            + [n for n in _src["notes"] if not n.startswith("11-18 加宽")]
                            + ([f"11-18 加宽 (孔不动): 孔离线束中心 ±{F(MW.CL_INS_DY_OLD)} (孔到线槽肉 {F(MW.CL_INS_DY_OLD - MW.INS_D / 2 - MW.CL_CH_HW)}), 端壁 {F(MW.EAR_H - MW.INS_D / 2)}"] if "clamp" in _base else
                               [f"11-18 加宽 (孔不动): 座宽 {F(2 * MW.SEAT_HX)}, 孔 ±{F(MW.MR_INS_DX_OLD)}: 外壁 {F(MW.SEAT_HX - MW.MR_INS_DX_OLD - MW.INS_D / 2)} / 到护套槽 {F(MW.MR_INS_DX_OLD - MW.INS_D / 2 - MW.SHEATH_W / 2)}"])))
# 11-18 用户: MR30 座拆 2 件 (带底片后公头装不进) ⇒ 下片单独出图 (玻纤板版 / _old 版)
for _code, _dx, _L, _base_txt in (("mr30_floor_v1_2", MW.MR_INS_DX, MW.SCREW_L[0], "玻纤板版"), ("mr30_floor_v1_2_old", MW.MR_INS_DX_OLD, 12.0, "_old 版 (配旧一体底盘 Φ220×6)")):
    _lo = MW.mr30_split(_dx)[1]; _p = MW.mr_ins(_dx)
    SPECS.append(dict(
        code=_code, shape=_lo, stl_asm=True, short="MR30 座下片", qty="1", material="PETG (建议) / PLA", date="2026-11-18",
        title=f"MR30 座下片: {F(2 * MW.SEAT_HX)}×{F(MW.Y_OPEN - MW.Y_R)}×{F(MW.FLOOR_T)} + 本体段垫条 {F(MW.BODY_W)}×{F(MW.BODY_L)}×{F(MW.Z_BD0 - MW.FLOOR_T)}",
        subtitle=f"{_base_txt}; 压在 MR30 公头下面, 上件 mr30_seat 扣在上面 (Z{F(MW.FLOOR_T)} 分开)",
        orient="底面贴床 (垫条朝上)",
        sec=dict(ang=180, r0=44.0, r1=78.0, zd=[(0, MW.Z_BD0, F(MW.Z_BD0))]),
        holes=[dict(tag="N", pts=_p, spec=f"Φ{F(MW.PASS_D)} 通", where=xy(_p) + f"  M3×{F(_L)} 从底盘底面往上穿过本件, 拧进上件铜螺母")],
        notes=[f"护套段底片 {F(MW.FLOOR_T)}; 本体段垫条高 {F(MW.Z_BD0 - MW.FLOOR_T)} (护套比本体单边大 0.25, 保证插头平放)",
               "装配: 下片放底盘上 → 放 MR30 公头 (护套朝 −y) → 扣上件 → 2×M3 从盘底往上拧紧"]))
# ---------------- 转子盘B 承载盘单件 rim_ring_v1_2b (rotor_b_v1_2.py; 11-17 夜) —— 只在点名出图时 import (rotor_b 要建整套转子件, 慢) ----------------
if any("_v1_2b" in a for a in sys.argv[1:]) or (B.ROTOR_B and len(sys.argv) == 1):   # 11-18 整机换成转子盘B 后全量出图也带上
    import io as _io, contextlib as _cl
    with _cl.redirect_stdout(_io.StringIO()):
        import rotor_b_v1_2 as RB
    _zf0, _zf1, _zt0, _ztop = RB.Z_F0, RB.Z_F1, RB.Z_T0, RB.Z_TOP
    _rb_ins = [(x, y) for x, y in RB.IN_PTS]
    SPECS.append(dict(
        code="rim_ring_v1_2b", shape=RB.rim, short="承载盘 Φ170 (转子盘B, 并入毂盘)", qty="1", stl_asm=True, date="2026-11-17",
        title=f"转子盘B 承载盘单件: 托盘 Z{F(_zt0)}–{F(_ztop)} + 底面线圈腔 R{F(RB.COIL_R0)}–{F(RB.COIL_R1)} 深 {F(RB.CAV_H)}; 中心/外环落玻纤板 Z{F(_zf1)}",
        subtitle=f"下面是玻纤板 Φ{F(RB.FR4_OD)}×{F(RB.FR4_T)} (Z{F(_zf0)}–{F(_zf1)}, 压电机顶); 外唇 R{F(RB.LIP_R0)}–{F(RB.RIM_R)} 往下包住玻纤板边到 Z{F(_zf0)}; 盘顶 Z{F(_ztop)} 与 V1.2 相同",
        orient=f"打印: 托盘顶面 (Z{F(_ztop)}) 朝下贴床, 线圈腔 / 外环 / 外唇朝上 (免支撑; models/ 下 _print.stl 已是此姿态)",
        phi=[2 * RB.COIL_R0, 2 * RB.COIL_R1, 2 * RB.LIP_R0, 2 * RB.RIM_R],
        sec=dict(ang=22.5, r0=0.0, auto_dims=False,
                 zd=[(_zf0, _zf1), (_zf1, _zt0), (_zt0, _ztop), (_ztop - RB.INS_H, _ztop), (_zf1, _ztop), (_zf0, _ztop)],
                 rd=[(0.0, RB.COIL_R0, f"中心实体 R{F(RB.COIL_R0)} (外圆 Φ{F(2 * RB.COIL_R0)} 套线圈 ID80)"),
                     (RB.COIL_R0, RB.COIL_R1, f"线圈腔 宽 {F(RB.COIL_R1 - RB.COIL_R0)} (R{F(RB.COIL_R0)}–R{F(RB.COIL_R1)})"),
                     (RB.COIL_R1, RB.LIP_R0, f"外环 {F(RB.LIP_R0 - RB.COIL_R1)} (R{F(RB.COIL_R1)}–R{F(RB.LIP_R0)})"),
                     (RB.LIP_R0, RB.RIM_R, f"外唇 {F(RB.RIM_R - RB.LIP_R0)} (包玻纤板边)")]),
        holes=[dict(tag="M", pts=RB.MOT_PTS, spec="电机 4 孔: " + hole_txt(RB.rim, RB.MOT_PTS[0]), where=ring_txt(RB.MOT_PTS) + "  M3×12 从顶面往下, 穿玻纤板进电机",
                    det=hole_det(RB.rim, RB.MOT_PTS[0], "电机孔 M (顶面沉孔)", W=5.0, z=(_zf1, _ztop))),
               dict(tag="N", pts=list(RB.OUT_NUT_PTS), spec="外圈孔 ×4: " + hole_txt(RB.rim, RB.OUT_NUT_PTS[0]),
                    where=f"外圈 {ring_txt(RB.OUT_NUT_PTS)}; 11-21: M3×{F(RB.OUT_SCR_L)} 超薄头从玻纤板底往上穿本件 + 屏幕支撑件, 法兰螺母坐支撑件顶面 Z{F(RB.OUT_NUT_Z[0])}–{F(RB.OUT_NUT_Z[1])} (尾 Z{F(RB.OUT_SCR_BEAR + RB.OUT_SCR_L)})"),
               dict(tag="Q", pts=_rb_ins, spec=f"Φ3.4 通 + 顶面 Φ{F(RB.IN_NUT_D)}×{F(RB.IN_NUT_H)} 沉孔 (放 M3 法兰螺母) ×8: " + hole_txt(RB.rim, _rb_ins[0]),
                    where=f"内圈 {ring_txt(_rb_ins)}; M3×7 从玻纤板底往上, 尾 Z{F(RB.Z_F0 + 1.5 + 7)}, 沉孔下实体 {F(RB.Z_TOP - RB.IN_NUT_H - RB.Z_F1)}",
                    det=hole_det(RB.rim, _rb_ins[0], "法兰螺母沉孔 Q", W=5.0, z=(_zf1, _ztop))),
               dict(tag="G", pts=RB.ANCHOR_PTS, spec="外圈孔 ×4 (原锚孔): " + hole_txt(RB.rim, RB.ANCHOR_PTS[0]),
                    where=ring_txt(RB.ANCHOR_PTS) + f"\n11-21: 同 N, M3×{F(RB.OUT_SCR_L)} 超薄头往上穿本件 + 屏幕支撑件, 法兰螺母坐支撑件顶面 (罩子锁点螺母嵌支撑件底面, 本件不开孔)"),
               dict(tag="P", pts=list(B.BB_HOLES), spec="底板 r4j 4 孔: " + hole_txt(RB.rim, B.BB_HOLES[0]),
                    where=xy(B.BB_HOLES) + "\n螺丝从底面往上, 薄头 Φ7×1.5 埋进托盘 (不进线圈腔)",
                    det=hole_det(RB.rim, B.BB_HOLES[0], "底板孔 P (底面沉孔)", W=5.0, z=(_zf1, _ztop))),
               dict(tag="W", pts=list(B.MOD_HOLES), spec="无线夹块 4 孔 (同 P): " + hole_txt(RB.rim, B.MOD_HOLES[0]), where=xy(B.MOD_HOLES, 4) + "  M3×14 超薄头往上 → 夹块顶法兰螺母"),
               dict(tag="A", pts=list(B.AC_HOLES), spec=f"线圈 AC 引线 Φ{F(B.AC_HOLE_D)} 通", where=xy(B.AC_HOLES) + "  孔边分别切线圈腔内/外缘"),
               dict(tag="C", pts=[(0.0, 0.0)], spec=f"底面中心窝 Φ{F(RB.CENTER_D)}×{F(RB.CENTER_H)} (电机轴头)", where="盘心", lab_off=(-3, -3))],
        notes=[f"Z: 外唇底 {F(_zf0)} / 中心·外环底 {F(_zf1)} / 腔顶 {F(_zt0)} / 盘顶 {F(_ztop)}; " +
               f"装配: 底板 P / 无线夹块 W 从本件底往上锁好 → 放线圈 → 玻纤板 内圈 8 颗往上进沉孔法兰螺母 → 上电机 → 屏幕支撑件 + 灯板组 (罩锁螺母已压进支撑件底) → 外圈 8 颗 M3×{F(RB.OUT_SCR_L)} 从玻纤板底往上穿本件 + 支撑件, 法兰螺母坐支撑件顶 → 罩子竖直下放 → 罩锁 DIN912 M3×{F(RB.SHR_SCR_L)} 从罩顶往下; 本件无罩子锁点孔"]))
    def _hold_spec_old(k):   # 11-20 作废 (screen_holder_v1_2b_a/b → screen_fr4_v1_2b ×4 + screen_post_v1_2b ×2), 留着对照
        sx = 1 if k == "a" else -1
        sh = RB.hold_a if k == "a" else RB.hold_b
        anc = RB.ANC_A if k == "a" else RB.ANC_B
        lk = RB.LK_A if k == "a" else RB.LK_B
        tb = [(sx * RB.LS.BAR_SCR_X[0], RB.LS.ECC)]
        side = "+x" if sx > 0 else "−x"
        return dict(
            code=f"screen_holder_v1_2b_{k}", shape=sh, stl_asm=True, date="2026-11-17", qty="1", material="PETG (建议) / PLA",
            short=f"屏幕固定件 {side} (转子盘B)",
            title=f"转子盘B 屏幕固定件 {side}: V1.2 立板 (横杆 + 腹板 + 天线板) 去耳朵, 换弧形带 R{F(RB.H_R0)}–{F(RB.H_R1)} ±{F(RB.H_SPAN)}° 厚 {F(RB.H_Z1 - RB.LS.RIM_TOP)}",
            subtitle=f"带底坐承载盘顶 Z{F(RB.LS.RIM_TOP)}, 带顶 = 横杆顶 = 灯板下沿 Z{F(RB.H_Z1)}; 与另一件互为镜像 (灯板偏心 y{F(RB.LS.ECC)})",
            orient=f"带底面 (Z{F(RB.LS.RIM_TOP)}) 贴床, 腹板/天线板竖直朝上",
            sec=dict(ang=0 if sx > 0 else 180, r0=60.0, auto_dims=False,
                     zd=[(RB.LS.RIM_TOP, RB.H_Z1), (RB.H_Z1 - RB.INS_H, RB.H_Z1), (RB.LS.RIM_TOP, RB.LS.ANT_Z1)],
                     rd=[(RB.H_R0, RB.H_R1, f"弧形带 R{F(RB.H_R0)}–R{F(RB.H_R1)}")]),
            holes=[dict(tag="G", pts=anc, spec=f"锚孔 Φ3.4 通 ×{len(anc)}", where=ring_txt(anc) + f"\nM3 从玻纤板底往上穿 玻纤板 + 承载盘 + 本件, 顶面 M3 法兰螺母 (凸出 3.7)"),
                   dict(tag="S", pts=lk, spec=f"罩子锁点 顶面 Φ{F(RB.INS_D)}×{F(RB.INS_H)} 盲孔, 压 M3×4 铜螺母 ×{len(lk)}", where=ring_txt(lk) + "  罩子耳朵坐带顶, M3 从上往下",
                        det=hole_det(sh, lk[0], "罩子锁点 S", W=4.0, z=(RB.LS.RIM_TOP, RB.H_Z1))),
                   dict(tag="T", pts=tb, spec="底面 Φ6×3 沉孔 + Φ3.4 通 (立板原有)", where=xy(tb) + f"  M3×{F(RB.LS.BAR_SCR_L)} 从下往上锁夹条 (先锁, 再上承载盘)")],
            notes=[f"弧形带 R{F(RB.H_R0)}–{F(RB.H_R1)}, 中心 {'0' if sx > 0 else '180'}° ±{F(RB.H_SPAN)}°, Z{F(RB.LS.RIM_TOP)}–{F(RB.H_Z1)} (厚 {F(RB.H_Z1 - RB.LS.RIM_TOP)}); 避开底板 r4j 上角 (47° 起)",
                   f"横杆 / 腹板 / 天线板 同 V1.2 led_post (灯板下沿坐横杆顶 Z{F(RB.H_Z1)}); 原两只耳朵取消",
                   f"锚孔 = 原耳朵孔位 (R{F(RB.R_OUT)} {'/'.join(F(round(ang(p), 1)) for p in anc)}°); 罩子锁点 r{F(RB.SHR_LOCK_R)} (罩子随后改)",
                   "装配: 桌上 玻纤板 + 承载盘 + 本件 用锚孔螺丝一起锁; 屏幕最后装"])
    _H = RB.SP_HOLES_LOC
    def _sup_spec(k):   # 11-21 屏幕支撑件 PETG 打印 (取代 屏幕玻纤板 ×4 + 侧立件 ×2)
        A = k == "a"
        sh = RB.screen_sup_a_loc if A else RB.screen_sup_b_loc
        lk = _H["lock_a"] if A else _H["lock_b"]
        x0, hy = (RB.SP_A_X0, RB.SP_A_HY) if A else (RB.SP_B_X0, RB.SP_B_HY)
        holes = [dict(tag="N", pts=_H["out"], spec=f"外圈 Φ3.4 通 + 顶面圆沉孔 Φ{F(RB.SP_NUT_CB_D)} 深到 Z{F(RB.OUT_NUT_Z[0])} (往外开口) ×2",
                      where=ring_txt(_H["out"]) + f"  M3×{F(RB.OUT_SCR_L)} 超薄头从 fr4_plate 底往上 (尾 Z{F(RB.OUT_SCR_BEAR + RB.OUT_SCR_L)}), M3 法兰螺母法兰朝下放进沉孔 Z{F(RB.OUT_NUT_Z[0])}–{F(RB.OUT_NUT_Z[1])} (顶低于件顶 0.3), 吃 {F(RB.OUT_ENG)}",
                      det=hole_det(sh, _H["out"][0], "外圈螺母沉孔 N (顶面)", W=5.5, z=(RB.SP_Z0, RB.SP_Z1))) if not A and not RB.SP_B_TOP_FLAT else
                 dict(tag="N", pts=_H["out"], spec=f"外圈 Φ3.4 通 + 主体顶面圆沉孔 Φ{F(RB.SP_NUT_CB_D)} 深 {F(RB.SP_Z0 + RB.SP_A_LOW - RB.OUT_NUT_Z[0])} (往外开口) ×2",
                      where=ring_txt(_H["out"]) + f"  M3×{F(RB.OUT_SCR_L)} 超薄头从 fr4_plate 底往上 (尾 Z{F(RB.OUT_SCR_BEAR + RB.OUT_SCR_L)}), M3 法兰螺母法兰朝下坐沉孔底 Z{F(RB.OUT_NUT_Z[0])}–{F(RB.OUT_NUT_Z[1])} (顶低于罩耳底 0.1), 吃 {F(RB.OUT_ENG)}",
                      det=hole_det(sh, _H["out"][0], "外圈螺母沉孔 N (主体顶面)", W=5.5, z=(RB.SP_Z0, RB.SP_Z1))) if A and not RB.SP_A_TOP_FLAT else
                 dict(tag="N", pts=_H["out"], spec="外圈 Φ3.4 通 ×2 (11-24 顶面不开沉孔)",
                      where=ring_txt(_H["out"]) + f"  M3×{F(RB.OUT_SCR_L)} 超薄头从 fr4_plate 底往上 (尾 Z{F(RB.OUT_SCR_BEAR + RB.OUT_SCR_L)}), M3 法兰螺母法兰朝下坐块顶 Z{F(RB.OUT_NUT_Z[0])}–{F(RB.OUT_NUT_Z[1])}, 吃 {F(RB.OUT_ENG)}; 罩耳不在螺母上方") if A else
                 dict(tag="N", pts=_H["out"], spec="外圈 Φ3.4 通 ×2 (11-23 顶面全平, 不开沉孔)",
                      where=ring_txt(_H["out"]) + f"  M3×{F(RB.OUT_SCR_L_B)} 超薄头从 fr4_plate 底往上 (尾 Z{F(RB.OUT_SCR_BEAR + RB.OUT_SCR_L_B)}), M3 法兰螺母法兰朝下坐本件顶面 Z{F(RB.OUT_NUT_Z_B[0])}–{F(RB.OUT_NUT_Z_B[1])}, 吃 {F(RB.OUT_ENG_B)}; 螺母离转子罩内壁 0.7"),
                 dict(tag="S", pts=lk, spec=f"罩锁 Φ{F(RB.SHR_HOLE_D)} 通 + 底面圆沉孔 Φ{F(RB.SP_NUT_CB_D)} 到 Z{F(RB.LOCK_NUT_Z[1] + RB.WELL_TOP_CLR)} ×2",
                      where=xy(lk) + f"  M3 法兰螺母法兰朝下从件底塞进沉孔 (坐承载盘顶); DIN912 M3×{F(RB.SHR_SCR_L)} 从罩耳顶往下, 尾 Z{F(RB.SHR_SCR_TIP)} (离承载盘顶 {F(RB.SHR_TIP_CLR)}), 吃 {F(RB.SHR_ENG)}",
                      det=hole_det(sh, lk[0], "罩锁螺母沉孔 S (底面)", W=5.5, z=(RB.SP_Z0, RB.SP_Z1)))]
        if A:
            holes.append(dict(tag="T", pts=_H["scr"], spec=f"屏幕螺丝 Φ3.4 腰形 (沿 y 长 {F(3.4 + 2 * RB.SP_SCR_SL)}) 通 + 底面 Φ{F(RB.SP_SCR_CB_D)}×{F(RB.SP_CB_H)} 沉孔 ×2 (沉孔外沿破出件外边)",
                              where=xy(_H["scr"]) + f"  放 0° 用 y−, 180° 用 y+; M3×{F(RB.BAR_SCR_L)} 超薄头 (支承 Z{F(RB.BAR_SCR_BEAR)}) 拧进灯板 F 面每端下颗铜螺柱, 吃 {F(RB.BAR_SCR_ENG)}, 尾离上颗 {F(round(RB.LS.SO_Z1 - RB.BAR_SCR_BEAR - RB.BAR_SCR_L, 2))}",
                              det=hole_det(sh, _H["scr"][0], "屏幕螺丝孔 T (底面沉孔, 件边破口)", W=5.0, z=(RB.SP_Z0, RB.SP_Z1))))
        return dict(
            code=f"screen_sup_{k}_v1_2b", shape=sh, stl_asm=True, date="2026-11-25" if A else "2026-11-21", qty="2", material="PETG",
            short=("屏幕支架件 A ×2 (0°/180° 同件, 托灯板)" if A else "上下件 B ×2 (90°/270° 同件)"),
            title=(f"转子盘B 屏幕支撑件 A 屏幕支架件: 主体 x{F(x0)}–{F(RB.SP_X1)}, 端块 x{F(RB.SP_A_WING[0])} 起 |y|{F(RB.SP_A_WING[1])}–{F(hy)}; 中段高 {F(RB.SP_A_LOW)}, |y|≥{F(RB.SP_A_KEEP)} 高 {F(RB.SP_T)}" if A else
                   f"转子盘B 屏幕支撑件 B 上下件: x{F(x0)}–{F(RB.SP_X1)} × |y|≤{F(hy)}, 外角 R{F(RB.SP_R1)}; 高 {F(RB.SP_T)} (Z{F(RB.SP_Z0)} 承载盘顶 → Z{F(RB.SP_Z1)})"),
            subtitle=(f"图示放 0° (+x) 位置; {'180° 同件转 180°; 外角 R' + F(RB.SP_R1) + ', Z' + F(RB.SP_Z0) + ' 承载盘顶 → Z' + F(RB.SP_Z1) + ' 罩耳底 (中段顶 Z' + F(RB.SP_Z0 + RB.SP_A_LOW) + ' = 灯板下沿)' if A else '放 90°/270°, 不托灯板'}; 用户 11-21「螺母嵌在这个支撑件上，我们还是用3d打印方式做」"),
            orient=(f"底面 (Z{F(RB.SP_Z0)}) 贴床; 底面沉孔开口朝床, 孔顶 Φ8 桥接" if A or not RB.SP_B_TOP_FLAT else
                    f"翻面: 顶面 Z{F(RB.SP_Z1)} (全平) 贴床, 底面槽/沉孔/销朝上, 免支撑"),
            sec=dict(ang=(math.degrees(math.atan2(lk[0][1], lk[0][0]))), r0=55.0, auto_dims=False,
                     zd=[(RB.SP_Z0, RB.SP_Z1), (RB.LOCK_NUT_Z[0], RB.LOCK_NUT_Z[1] + RB.WELL_TOP_CLR)] + ([(RB.SP_Z0, RB.SP_Z0 + RB.SP_A_LOW)] if A else [(RB.SP_Z0, RB.SP_Z0 + RB.SP_POCKET_FLOOR)] if not RB.SP_B_TOP_FLAT else [])),
            holes=holes,
            notes=[f"取代 11-20 屏幕玻纤板 screen_fr4_v1_2b ×4 (FR4 3 厚) + 侧立件 screen_post_v1_2b ×2; 高度 = 灯板下沿 − 承载盘顶 = {F(RB.SP_T)} (灯板 +1 后), 跟 LS.Z0 走",
                   (f"11-25 用户「挪到边上」: 罩锁点 S 由 (61, ±30.5) 挪到 ({F(lk[0][0])}, ±{F(lk[0][1])}) (r{F(RB.SHR_LOCK_R['a'])}), 在外圈螺丝外侧; 内边收回 x{F(x0)}" if A else
                    f"罩锁点 S 保持 ({F(lk[0][0])}, ±{F(lk[0][1])}) (r{F(RB.SHR_LOCK_R['b'])}); 内边 x{F(x0)} (放 90° 离 CZ06 0.68, 放 270° 离无线夹块 2.9)"),
                   f"罩锁 = 底面 Φ{F(RB.SP_NUT_CB_D)} 沉孔, 螺母法兰朝下坐承载盘顶; 外圈只 Φ3.4 通, 螺母坐满高段顶; 圆孔螺母会跟转, 拧时用扳手卡住" if A and RB.SP_A_TOP_FLAT else
                   f"螺母沉孔 (11-23 用户: 同承载盘 Q, M3 通孔 + 圆沉孔 Φ{F(RB.SP_NUT_CB_D)}): 罩锁 = 底面沉孔, 螺母法兰朝下坐承载盘顶, 拧紧时螺母顶顶沉孔顶; 外圈 = " + ("只 Φ3.4 通, 螺母坐块顶 (见 N)" if A and RB.SP_A_TOP_FLAT else "主体顶面 (4 高) Φ8 浅沉孔 (朝外开口), 螺母顶低于罩耳底 0.1" if A else "顶面沉孔, 螺母法兰朝下坐沉孔底, 沉孔外侧离件边只 0.2 ⇒ 往外开口" if not RB.SP_B_TOP_FLAT else "本件不开沉孔 (11-23), 螺母坐顶面") + "; 圆孔螺母会跟转, 拧时用扳手/镊子卡住",
                   (f"中段 |y|<{F(RB.SP_A_KEEP)} 高 {F(RB.SP_A_LOW)} (托灯板), 两端高 {F(RB.SP_T)} (S + N 都在满高段); 不开减重槽; 罩锁窝边距 {F(RB.SP_EDGE['a_lock_well'])}; 端块离天线 FPC 2.08" if A else f"减重: 顶面盲槽 槽底留 {F(RB.SP_POCKET_FLOOR)}; 边距 罩锁窝 {F(RB.SP_EDGE['b_lock_well'])}" if not RB.SP_B_TOP_FLAT else
                    f"11-23 用户「sup_b上面的沉孔都去掉」: 顶面全平, 不开减重槽 / 外圈沉孔; 顶面只剩贯穿孔 N Φ3.4 ×2 + S Φ{F(RB.SHR_HOLE_D)} ×2 + 接收板长圆穿线槽; 外圈螺母改坐顶面 (高出 {F(RB.NUT_T)}, 罩耳 y{F(RB.SHR_LOC_Y - 4.5)}–{F(RB.SHR_LOC_Y + 4.5)} 不在其上)"),
                   ("装配: 桌上塞 2 颗罩锁螺母 → 与灯板组拧成一组 → 放承载盘 → 外圈螺丝从 fr4_plate 底往上 → 下放侧环, 罩锁 DIN912 从上拧" if A else
                    ("装配: 罩锁螺母从底面塞进 → 放承载盘 → 外圈螺母放顶面沉孔 + 外圈螺丝从 fr4_plate 底往上 → 罩子竖直下放 → 罩锁 DIN912 从罩顶起子孔拧" if not RB.SP_B_TOP_FLAT else
                     f"装配: 罩锁螺母从底面塞进 → 放承载盘 → 外圈法兰螺母放在顶面孔口 (法兰朝下), 镊子/扳手按住, M3×{F(RB.OUT_SCR_L_B)} 从 fr4_plate 底往上拧 (须在罩子下放前完成) → 罩子竖直下放 → 罩锁 DIN912 从罩顶起子孔拧")),
                   "PETG 打印, 壁 ≥3 圈, 填充 ≥40% (螺母窝/孔周实心); 六角窝打印偏小时用烙铁压入或修窝"])
    SPECS += [_sup_spec("a"), _sup_spec("b")]
    if any("rotor_shroud_b" in a or "rotor_shroud_lid" in a for a in sys.argv[1:]):
        with _cl.redirect_stdout(_io.StringIO()):
            import rotor_shroud_b_v1_2 as RSB

        def _shrb_spec(k):
            sy = 1 if k == "a" else -1
            sh = RSB.shr_a if k == "a" else RSB.shr_b
            side = "+y" if sy > 0 else "−y"
            mp = [p for p in RSB.MNT_PTS if (p[1] > RSB.SPLIT_Y) == (sy > 0)]
            wp = [RSB.pol(RSB.RS.W_R, a) for a in RSB.W_A if (RSB.pol(RSB.RS.W_R, a)[1] > RSB.SPLIT_Y) == (sy > 0)]
            ls = [RSB.LS_PTS[a] for a in RSB.LS_ANG[k]]
            a0 = [a for a, p in zip(RSB.MNT_A, RSB.MNT_PTS) if (p[1] > RSB.SPLIT_Y) == (sy > 0)][0]
            return dict(
                code=f"rotor_shroud_b_{k}_v1_2b", shape=sh, stl_asm=True, date="2026-11-25", qty="1", material="PETG (建议) / PLA",
                short=f"转子罩 {side} 侧环 (不含顶盖, 转子盘B)",
                title=f"转子盘B 转子罩 {side} 侧环: 罩壁 R{F(RSB.R0)}–{F(RSB.R1)} Z{F(RSB.Z0)}–{F(RSB.LID_Z0)} + 配重唇 + 盖螺丝凸块 ×3; 顶盖另件",
                subtitle=f"罩底 {len(mp)} 个耳朵 (宽 {F(RSB.BOSS_W)}) 坐屏幕支撑件顶 Z{F(RSB.BOSS_Z0)}–{F(RSB.BOSS_Z1)}, DIN912 M3×{F(RSB.MNT_L)} 从耳顶往下; 罩壁平底坐承载盘顶 Z{F(RSB.Z0)}",
                orient=f"倒放: 环顶 (Z{F(RSB.LID_Z0)}) 整面贴床, 凸台斜撑 45° 免支撑",
                sec=dict(ang=a0, r0=60.0, auto_dims=False,
                         zd=[(RSB.Z0, RSB.BOSS_Z0), (RSB.BOSS_Z0, RSB.BOSS_Z1), (RSB.RS.LIP_Z0, RSB.LID_Z0), (RSB.Z0, RSB.LID_Z0)],
                         rd=[(RSB.R0, RSB.R1, f"罩壁 {F(RSB.R1 - RSB.R0)}")]),
                holes=[dict(tag="M", pts=mp, spec=f"耳 Φ3.4 通 Z{F(RSB.BOSS_Z0)}–{F(RSB.BOSS_Z1)} + 上方 Φ{F(RSB.ACC_D)} 起子孔 (只切到罩壁内面 R{F(RSB.R0)})",
                            where=ring_txt(mp) + f"  DIN912 M3×{F(RSB.MNT_L)} 头坐耳顶 Z{F(RSB.BOSS_Z1)}, 尾 Z{F(RSB.SCR_TIP)}, 螺母在支撑件底"),
                       dict(tag="L", pts=ls, spec=f"盖螺丝 Φ3.4 通 + 顶面 Φ{F(RSB.LS_SEAT_D)} 深 {F(RSB.LS_SEAT_H)} 定位窝 + 底面六角窝 AF{F(RSB.LS_HEX_AF)} 深 {F(round(RSB.LS_HEX_Z1 - RSB.LS_PAD_Z0, 2))}",
                            where=f"r{F(RSB.LS_R)} @" + "/".join(F(a) for a in RSB.LS_ANG[k]) + f"°  凸块底 Z{F(round(RSB.LS_PAD_Z0, 2))}; M3 法兰螺母从下塞进 (法兰贴凸块底), 窝间壁 {F(RSB.LS_WEB)}",
                            det=dict(hole_det(sh, ls[0], "盖螺丝凸块 L", W=8.0, z=(RSB.LS_PAD_Z0 - 2, RSB.LID_Z0)),
                                     zd=[(RSB.LS_PAD_Z0, RSB.LS_HEX_Z1, F(round(RSB.LS_HEX_Z1 - RSB.LS_PAD_Z0, 2)), 0), (RSB.LS_HEX_Z1, RSB.LID_Z0 - RSB.LS_SEAT_H, F(RSB.LS_WEB), 0),
                                         (RSB.LID_Z0 - RSB.LS_SEAT_H, RSB.LID_Z0, F(RSB.LS_SEAT_H), 0), (RSB.LS_PAD_Z0, RSB.LID_Z0, F(round(RSB.LID_Z0 - RSB.LS_PAD_Z0, 2)), 8)])),
                       dict(tag="W", pts=wp, spec=f"配重孔 Φ3.4 + Φ{F(RSB.RS.W_CB_D)} 沉孔 (到唇 Z{F(RSB.RS.W_BEAR)})",
                            where=f"r{F(RSB.RS.W_R)} ×{len(wp)}  M3×{F(RSB.RS.W_L)} 从盖顶插, 唇下挂 M3 螺母配重 (最多 {RSB.RS.W_NUT_MAX} 颗)")],
                notes=[f"11-25 用户「侧面环形和上面盖子能分开装吗」: 顶盖拆成另件 rotor_shroud_lid_{k}_v1_2b, 调试只拆盖",
                       f"耳坐支撑件顶: A 件本地 ({F(RB.LOCK_A_LOC[0][0])}, ±{F(RB.LOCK_A_LOC[0][1])}) / B 件 ({F(RB.SHR_LOC_X)}, ±{F(RB.SHR_LOC_Y)}); 世界角 " + "/".join(F(round(a, 2)) for a in RSB.MNT_A) + "°",
                       f"耳 = 支撑件局部沿 x 长条 (锁点内 {F(RSB.EAR_IN)} → 罩壁, 宽 {F(RSB.BOSS_W)}, 厚 {F(RSB.BOSS_T)}), 上面 45° 斜撑从锁点外 {F(RSB.GUSSET_X0)} 起接罩壁; 耳底平 (11-25 无螺母让位口)",
                       "配重孔避让起子孔 / 盖螺丝: 取消 " + ("/".join(F(a) for a in RSB.W_DROP) or "无") + f"°, 现 {len(RSB.W_A)} 个 (两半合计)",
                       f"各层高度: 罩壁底 Z{F(RSB.Z0)} (坐承载盘) / 耳 Z{F(RSB.BOSS_Z0)}–{F(RSB.BOSS_Z1)} / 配重唇 Z{F(RSB.RS.LIP_Z0)}–{F(RSB.LID_Z0)}; 环顶 Z{F(RSB.LID_Z0)} 全平",
                       f"两端竖缝 y{F(RSB.SLOT_Y0)}…{F(RSB.SLOT_Y1)} (灯板/夹条端头) 就是两半之间的缝",
                       f"天线 FPC 18.5×37.7 贴本件内壁: 定位浅槽 {F(RB.LS.ANT_L)}×{F(RB.LS.ANT_W)}×{F(RB.LS.ANT_REC)} @" + "/".join(F(a) for a in RSB.ANT_ANG) + f"° Z{F(round(RSB.ANT_Z0, 2))}–{F(round(RSB.ANT_Z1, 2))}",
                       f"装配: 桌上先塞 3 颗盖螺母 → 竖直下放 → 罩锁 DIN912 (起子 ≤Φ6) → 盖上顶盖"])
        def _lid_spec(k):
            sy = 1 if k == "a" else -1
            sh = RSB.lid_a if k == "a" else RSB.lid_b
            side = "+y" if sy > 0 else "−y"
            mp = [p for p in RSB.MNT_PTS if (p[1] > RSB.SPLIT_Y) == (sy > 0)]
            wp = [RSB.pol(RSB.RS.W_R, a) for a in RSB.W_A if (RSB.pol(RSB.RS.W_R, a)[1] > RSB.SPLIT_Y) == (sy > 0)]
            ls = [RSB.LS_PTS[a] for a in RSB.LS_ANG[k]]
            _zb = RSB.LID_Z0 - RSB.LS_BOSS_H
            return dict(
                code=f"rotor_shroud_lid_{k}_v1_2b", shape=sh, stl_asm=True, date="2026-11-25", qty="1", material="PETG (建议) / PLA",
                short=f"转子罩 {side} 顶盖 (转子盘B)",
                title=f"转子盘B 转子罩 {side} 顶盖: 外圆 R{F(RSB.R1)} 厚 {F(RSB.LID_T)} (Z{F(RSB.LID_Z0)}–{F(RSB.Z1)}), 底面 3 个定位圆凸台 Φ{F(RSB.LS_BOSS_D)}×{F(RSB.LS_BOSS_H)}",
                subtitle=f"盖在侧环 rotor_shroud_b_{k}_v1_2b 的罩壁顶 + 配重唇上; 3×M3×{F(RSB.LS_L)} 超薄头从上往下, 头沉盖面",
                orient=f"翻面: 顶面 (Z{F(RSB.Z1)}) 贴床, 凸台朝上, 免支撑",
                sec=dict(ang=RSB.LS_ANG[k][1], r0=60.0, auto_dims=False,
                         zd=[(_zb, RSB.LID_Z0), (RSB.LID_Z0, RSB.Z1), (_zb, RSB.LS_BEAR), (RSB.LS_BEAR, RSB.Z1)], rd=[]),
                holes=[dict(tag="L", pts=ls, spec=f"盖螺丝 Φ3.4 通 + 顶面 Φ{F(RSB.LS_CB_D)} 深 {F(RSB.LS_CB_H)} 沉孔, 底面凸台 Φ{F(RSB.LS_BOSS_D)} 高 {F(RSB.LS_BOSS_H)}",
                            where=f"r{F(RSB.LS_R)} @" + "/".join(F(a) for a in RSB.LS_ANG[k]) + f"°  支承 Z{F(round(RSB.LS_BEAR, 2))}, 尾 Z{F(round(RSB.LS_TIP, 2))} (齐螺母底, 吃 {F(RB.NUT_T)})",
                            det=dict(hole_det(sh, ls[0], "盖螺丝孔 L", W=7.0, z=(_zb, RSB.Z1)),
                                     zd=[(_zb, RSB.LS_BEAR, F(round(RSB.LS_BEAR - _zb, 2)), 0), (RSB.LS_BEAR, RSB.Z1, F(RSB.LS_CB_H), 0), (_zb, RSB.Z1, F(round(RSB.Z1 - _zb, 2)), 8)])),
                       dict(tag="M", pts=mp, spec=f"起子孔 Φ{F(RSB.ACC_D)} 通 (罩锁 DIN912)", where=ring_txt(mp)),
                       dict(tag="W", pts=wp, spec=f"配重孔 Φ{F(RSB.RS.W_CB_D)} 通", where=f"r{F(RSB.RS.W_R)} ×{len(wp)}")],
                notes=[f"定位: 凸台 Φ{F(RSB.LS_BOSS_D)} 落进环上 Φ{F(RSB.LS_SEAT_D)} 窝 (单边 {F(round((RSB.LS_SEAT_D - RSB.LS_BOSS_D) / 2, 2))}, 底隙 {F(round(RSB.LS_SEAT_H - RSB.LS_BOSS_H, 2))})",
                       f"桥板让位通槽: x{F(-RSB.RS.BR_SLOT_HX)}…{F(RSB.RS.BR_SLOT_HX)}, 通到 y{F(round(RSB.BR_POCKET[k][1], 3))}, 全通",
                       f"内边离灯板 ≥0.3; 拆盖: 松 3 颗螺丝 → 抬 5 → 往{'+y' if sy > 0 else '−y'} 平移取出, 不碰灯板/桥板/FPC (先取下玻璃管)",
                       "不拆盖也能: 从起子孔拆整半罩 / 从配重孔加减配重; 动平衡装着盖做"])
        SPECS += [_lid_spec("a"), _lid_spec("b")]
        SPECS += [_shrb_spec("a"), _shrb_spec("b")]
    _FOLDER_B = {"rim_ring_v1_2b": "转子盘B", "screen_sup_a_v1_2b": "转子盘B", "screen_sup_b_v1_2b": "转子盘B", "rotor_shroud_b_a_v1_2b": "转子盘B", "rotor_shroud_b_b_v1_2b": "转子盘B", "rotor_shroud_lid_a_v1_2b": "转子盘B", "rotor_shroud_lid_b_v1_2b": "转子盘B"}
else:
    _FOLDER_B = {}
_DIR = {"motor_wire_clamp_v1_2": "mr30_seat_v1_2", "mr30_seat_v1_2_old": "mr30_seat_v1_2", "motor_wire_clamp_v1_2_old": "mr30_seat_v1_2", "mr30_floor_v1_2": "mr30_seat_v1_2", "mr30_floor_v1_2_old": "mr30_seat_v1_2"}   # 11-18 用户: 线夹文件放 MR30 文件夹 (models/<目录>/)
_D1116 = {"led_post_a_v1_2", "led_post_b_v1_2", "led_bar_v1_2", "led_top_v1_2", "led_comb_v1_2", "rotor_shroud_a_v1_2", "rotor_shroud_b_v1_2",
          "rotor_lid_v1_2", "rotor_lid_b_v1_2", "wireless_holder_v1_2", "rim_ring_v1_2_D170", "hub_disc_v1_2", "base_disc_v1_2", "mr30_seat_v1_2", "motor_wire_clamp_v1_2"}
for sp in SPECS:
    if sp["code"] in _D1116:
        sp.setdefault("date", "2026-11-16")      # 11-16 新转子布局 / 11-16 晚 偏心 + 耳朵脚
    sp.update({k: v for k, v in COMMON.items() if k not in sp})
    _dir = _DIR.get(sp["code"], sp["code"])
    sp["stl"] = M / _dir / f"{sp['code']}.stl"
    sp["src"] = f"v1.2/models/{_dir}/{sp['code']}.stl"
    if sp.get("stl_asm"):                        # models/ 下的 STL 是打印姿态 ⇒ 俯视用装配坐标 STL (出图时现写到 out/dwg_stl/)
        sp["stl"] = V12 / "out" / "dwg_stl" / f"{sp['code']}.stl"
        sp["src"] = f"v1.2/out/dwg_stl/{sp['code']}.stl (装配坐标; 打印件 models/{sp['code']}/)"
    sp.setdefault("origin_note", ORIG)

_FOLDER = {"rim_ring_v1_2_D170": "转子盘", "hub_disc_v1_2": "转子盘", "flange_disc_v1_2": "定子盘", "mounting_flange_v1_2": "定子盘", "ir_clamp_v1_2": "定子盘", **_FOLDER_B}

# 11-18 整机换成转子盘B: 全量出图时不再重出旧转子件 (图纸文件保留, 点名仍可出)
_SUPERSEDED = {"hub_disc_v1_2", "rim_ring_v1_2_D170", "led_post_a_v1_2", "led_post_b_v1_2", "rotor_shroud_a_v1_2", "rotor_shroud_b_v1_2", "rotor_lid_v1_2", "rotor_lid_b_v1_2"} if B.ROTOR_B else set()
if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sp in SPECS:
        if only and sp["code"] not in only:
            continue
        if not only and sp["code"] in _SUPERSEDED:
            continue
        if sp.get("stl_asm"):
            from OCP.BRepMesh import BRepMesh_IncrementalMesh
            from OCP.StlAPI import StlAPI_Writer
            sp["stl"].parent.mkdir(parents=True, exist_ok=True)
            BRepMesh_IncrementalMesh(sp["shape"], 0.02, False, 0.2, True)
            _w = StlAPI_Writer(); _w.ASCIIMode = False; _w.Write(sp["shape"], str(sp["stl"]))
        sp["out"] = M / _DIR.get(sp["code"], sp["code"]) / f"{sp['code']}_drawing.pdf"
        sp["out"].parent.mkdir(parents=True, exist_ok=True)
        try:
            out, png, sl = draw(sp)
        except PermissionError:                  # 原图被阅读器占用 ⇒ .NEW.pdf, 再占用 ⇒ .NEW2.pdf
            for _sfx in ("NEW", "NEW2", "NEW3"):
                sp["out"] = sp["out"].with_name(f"{sp['code']}_drawing.{_sfx}.pdf")
                try:
                    out, png, sl = draw(sp); break
                except PermissionError:
                    continue
            else:
                raise
        print(f"wrote {out}  ({sl})", flush=True)
        if sp["code"] in _FOLDER:                # 11-16 晚: 转子盘 / 定子盘 文件夹里的图纸出图即同步 (export_3mf_v1_2.py 也会拷, 但它先于出图跑)
            import shutil
            _gd = V12 / _FOLDER[sp["code"]]; _gd.mkdir(exist_ok=True)
            try:
                shutil.copy2(out, _gd / f"{sp['code']}_drawing.pdf"); print(f"  → {_FOLDER[sp['code']]}/", flush=True)
            except PermissionError:                # 文件被 PDF 阅读器占用 ⇒ 另存 .NEW.pdf
                shutil.copy2(out, _gd / f"{sp['code']}_drawing.NEW.pdf"); print(f"  !! {_FOLDER[sp['code']]}/{sp['code']}_drawing.pdf 被占用, 已另存 .NEW.pdf", flush=True)
