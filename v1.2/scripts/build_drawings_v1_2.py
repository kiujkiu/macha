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


def vd(z0, z1, u, off, label):     # 主视 (X-Z) 竖直尺寸, 尺寸线放视图右侧 off
    return dict(view="front", kind="v", p0=(u, z0), p1=(u, z1), off=off, label=label)


SPECS = []
COMMON = dict(date=DATE, proj="V1.2")
ORIG = "原点 = 轴心, Z = 装配高度 (底盘顶面 Z0); 图示为装配姿态。"

# ---------------- base_disc_v1_2 ----------------
BH = [gp_Pnt(x, y, 0).Transformed(B.BT) for x, y in B.BHOLES]
BH = [(p.X(), p.Y()) for p in BH]
_rl = B.RELIEFS[0]
_rp = gp_Pnt((_rl[0] + _rl[1]) / 2, (_rl[2] + _rl[3]) / 2, 0).Transformed(B.BT)
grid_np = [p for p in B.EXTRA if p not in B.POSTS]
ZD = (-B.DISC_T, 0.0)
cb6 = f"Φ{F(B.M6_D)} 通 + 底面 Φ{F(B.CB_D)}×{F(B.CB_H)} 沉孔"
cb3 = f"Φ{F(B.M3_D)} 通 + 底面 Φ{F(B.M3_CB_D)}×{F(B.M3_CB_H)} 沉孔"
ins = f"Φ3.2 通 + 底面 Φ{F(B.INS_HOLE_D)}×{F(B.INS_HOLE_H)} 铜螺母孔 (M3×4 铜螺母齐底面)"
SPECS.append(dict(
    code="base_disc_v1_2", shape=B.disc, short=f"底盘 Φ{F(B.DISC_D)}×{F(B.DISC_T)}", qty="1",
    title=f"打印底盘 Φ{F(B.DISC_D)}×{F(B.DISC_T)} (合并电机控制板托板 + 散热片槽)",
    subtitle="沉孔 / 铜螺母孔全部开在底面 (Z-6); 顶面 Z0 = 装配基准 (电机/控制板/线圈环/下罩都坐在上面)",
    orient="顶面 (Z0) 贴床",
    phi=[24, 2 * B.R_SCREW, 2 * B.STATOR_R, (2 * B.RING_M3_XY, f"{F(2 * B.RING_M3_XY)} (方)"), 2 * B.SH_R, B.DISC_D],
    sec=dict(ang=45, zd=[(-B.DISC_T, 0.0)], rd=[(0, B.STATOR_R), (0, math.hypot(B.RING_M3_XY, B.RING_M3_XY)), (0, B.SH_R)]),
    holes=[
        dict(tag="A", pts=B.POSTS, spec=cb6 + " (立柱)", where="V0.4 柱位 " + xy(B.POSTS),
             det=dict(kind="cb", d=B.M6_D, D=B.CB_D, h=B.CB_H, side="bot", z=ZD, pt=B.POSTS[0], title="M6 沉孔 (A/B 同)")),
        dict(tag="B", pts=grid_np, spec=cb6 + "  同详图 A", where=f"原 M6 网格 节距 25, 盘内放得下的全开; 跳过 {len(B.SKIP)} 位"),
        dict(tag="C", pts=B.XT_GHOLES_DISC, spec=cb3 + "  同详图 D (XT60 压块 V1.2-g; 11-12 已打印件为 M6 孔, 需加 Φ9 垫片)", where=xy(B.XT_GHOLES_DISC) + "  M3×20 往上, 法兰螺母坐压块顶", lab_off=(-2.4, 2.4)),
        dict(tag="D", pts=B.MOTOR_HOLES, spec=cb3 + " (电机)", where=f"对角 {F(2 * B.STATOR_R)}  M3×8 (待电机螺孔深度确认)",
             det=dict(kind="cb", d=B.M3_D, D=B.M3_CB_D, h=B.M3_CB_H, side="bot", z=ZD, pt=B.MOTOR_HOLES[0], title="M3 沉孔 (C/D/E/F 同)")),
        dict(tag="E", pts=B.RING_M3, spec=cb3 + "  同详图 D (线圈环四角)", where=f"(±{F(B.RING_M3_XY)}, ±{F(B.RING_M3_XY)})  M3×12, 法兰螺母压四角顶"),
        dict(tag="F", pts=B.SH_M6, spec=cb3 + "  同详图 D (下罩)", where=ring_txt(B.SH_M6) + "  M3×14, 法兰螺母压三角块顶"),
        dict(tag="G", pts=B.FLANGE_SCREWS, spec=ins + " (线圈环/定子盘)", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20",
             det=dict(kind="ins", d=3.2, D=B.INS_HOLE_D, h=B.INS_HOLE_H, side="bot", z=ZD, pt=B.FLANGE_SCREWS[0], title="M3 铜螺母孔 (G/H 同)")),
        dict(tag="H", pts=BH, spec=cb3 + "  同详图 D (控制板, 11-13 改从下往上)", where=xy(BH) + "  M3×10 往上, 法兰螺母坐板顶"),
        *([] if not B.CD.ALL_HOLES else [
        dict(tag="L", pts=B.CD.ALL_HOLES, spec=cb3 + "  同详图 D (线圈驱动板: MOS 压块 2 + 电容卡件 2)",
             where=xy(B.CD.ALL_HOLES, 2) + f"  M3×12 往上, 法兰螺母倒放在件顶螺母井")]),
    ],
    dets=[dict(tag="J", kind="blind", D=12.0, h=3.0, side="top", z=ZD, pt=(0.0, 0.0), ang=0.0, W=9.0, title="盘心 Φ12×3 盲窝 (顶面)"),
          dict(tag="K", kind="free", z=ZD, pt=(_rp.X(), _rp.Y()), ang=0.0, W=6.0, title="控制板背面让位槽 ×3 (顶面)",
               zd=[(-3.0, 0.0, "3")])],
    notes=["散热片通槽 20×40 ×2 (零间隙): 控制板 1; 线圈驱动板 1 竖放 "
           f"x{F(B.CD.SINK_X0)}..{F(B.CD.SINK_X1)} y{F(B.CD.SINK_Y0)}..{F(B.CD.SINK_Y1)}; 控制板背面让位 ×3 深 3 (K); 顶面平 (贴床)",
           f"线圈驱动板电容弧形槽 R{F(B.CD.CAP_D / 2 + B.CD.CAP_TROUGH_CLR)} 深 {F(B.CD.CAP_GROOVE)} x{F(B.CD.CAP_TROUGH[0])}..{F(B.CD.CAP_TROUGH[1])} "
           f"y{F(B.CD.CAP_TROUGH[2])}..{F(B.CD.CAP_TROUGH[3])}; 背面电容坑 {"深 " + F(-min(p[4] for p in B.CD.BCAP_PITS)) if B.CD.BCAP_PITS else "取消 (11-13, 板抬高)"}; 网格 M6 取消 {len(B.CD.GRID_REMOVE)} 个 (x62.5)",
           f"控制板平放顶面 Z0, 内长边离轴 {F(B.BOARD_IN)}, 往 +X 让 {F(B.BOARD_DX)}"],
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
    dets=[dict(tag="C", kind="free", z=(0, B.TUBE_TOP), pt=(34 * math.cos(math.radians(B.WIRE_A0 + B.WIRE_AW / 2)), 34 * math.sin(math.radians(B.WIRE_A0 + B.WIRE_AW / 2))), ang=B.WIRE_A0 + B.WIRE_AW / 2, W=6.5,
               title=f"出线口 {F(B.WIRE_A0)}–{F(B.WIRE_A0 + B.WIRE_AW)}° 高 {F(B.WIRE_ZH)} 处 (r34 中心)",
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
    phi=[2 * B.FL_HOLE_R, 2 * B.R_SCREW, 2 * 78.0, 165.0],
    sec=dict(ang=22.5, zd=[(B.FL_Z0, B.FL_TOP)]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec="Φ3.2 通", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20 到底盘铜螺母"),
        dict(tag="B", pts=B.LID_SCREWS, spec=f"Φ3.2 通 + 底面 Φ{F(B.LID_INS_D)}×{F(B.LID_INS_H)} 铜螺母孔",
             where=ring_txt(B.LID_SCREWS) + "  上下盖互锁 M3×6 + M3×4 铜螺母",
             det=dict(kind="ins", d=3.2, D=B.LID_INS_D, h=B.LID_INS_H, side="bot", z=(B.FL_Z0, B.FL_TOP), pt=B.LID_SCREWS[0], title="外圈 M3 铜螺母孔")),
    ],
    notes=[f"Z{F(B.FL_Z0)}→{F(B.FL_TOP)}, 原 V0.4 底板 4.5 → {F(4.5 - B.FL_THIN)}; 线圈腔 r{F(B.CAV_R0)}–{F(B.CAV_R1)} 底 Z{F(B.CAV_Z0)}",
           f"内墙 r31.7–{F(B.CAV_R0)} / 外墙 r{F(B.CAV_R1)}–82.5 都是 {F(B.CB7)} 宽 (= 安装法兰 Φ{F(B.CB7)} 沉孔), 螺丝居中",
           "+X 处 XT60 压块让位缺口; 原 +X 线圈引线槽 (r40–61) 减薄后变通槽 (待定)",
           "底面控制板让位 (11-12 夜): " + "; ".join(f"x{F(p['bbox'][0] - B.BRD_POCKET_GAP)}..{F(p['bbox'][3] + B.BRD_POCKET_GAP)} y{F(p['bbox'][1] - B.BRD_POCKET_GAP)}..{F(p['bbox'][4] + B.BRD_POCKET_GAP)} 深 {F(p['depth'])}" for p in B.BRD_POCKETS)],
))

# ---------------- mounting_flange_v1_2 ----------------
MF_Z0 = B.FL_Z0 + (B.MF_THIN_LOW - B.FL_THIN)      # 外裙底 Z9.5
SPECS.append(dict(
    code="mounting_flange_v1_2", shape=B.mounting_flange, short="安装法兰 (无线供电上盖)", qty="1",
    title=f"安装法兰 Φ170: V0.4 件外裙短 {F(B.MF_THIN_LOW)}, 板顶减 {F(B.MF_THIN)}, 中心孔 Φ{F(2 * B.MF_HOLE_R)}",
    subtitle=f"外裙 r82.5–85 包住定子盘外缘, 底到 Z{F(MF_Z0)} (定子盘底 Z{F(B.FL_Z0)}; 11-12 夜定子盘加厚, 外裙不跟)",
    orient="翻面打印 (板顶朝下)",
    phi=[2 * B.MF_HOLE_R, 2 * B.R_SCREW, 2 * 78.0, 165.0, 170.0],
    sec=dict(ang=22.5, zd=[(MF_Z0, B.FL_TOP), (B.FL_TOP, B.MF_TOP), (MF_Z0, B.MF_TOP)]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20",
             det=dict(kind="cb", d=3.2, D=7.0, h=B.MF_CB, side="top", z=(B.FL_TOP, B.MF_TOP), pt=B.FLANGE_SCREWS[0], title="M3 沉孔 (A/B 同)")),
        dict(tag="B", pts=B.LID_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔  同详图 A", where=ring_txt(B.LID_SCREWS) + "  M3×6 锁定子盘 B"),
    ],
    dets=[dict(tag="D", kind="free", z=(MF_Z0, B.MF_TOP), pt=(83.75 * math.cos(math.radians(22.5)), 83.75 * math.sin(math.radians(22.5))), ang=22.5, W=5.0,
               title="外裙 r82.5–85 (中心 r83.75)", zd=[(MF_Z0, B.FL_TOP, F(B.FL_TOP - MF_Z0), 0), (B.FL_TOP, B.MF_TOP, F(B.MF_TOP - B.FL_TOP), 0)], ud=[(-1.25, 1.25, "2.5")])],
    notes=[f"外裙 = V0.4 原件, 底 Z{F(MF_Z0)} (11-12 夜: 定子盘底降到 {F(B.FL_Z0)}, 外裙不跟, 下罩法兰螺母顶 Z8.7 下留 0.8)", "外圈 B 孔 r79 居中于定子盘外墙 (原 V0.4 r77.5 已补实)",
           f"中心孔 Φ{F(2 * B.MF_HOLE_R)}: 线圈环内管 Φ{F(B.TUBE_OD)} 穿过, 顶齐 Z{F(B.MF_TOP)}"],
))

# ---------------- 玻璃罩下罩三件 ----------------
sup = B.OUT_SCREWS
gl_notes = [f"玻璃 OD{F(B.GL_OD)}×{F(B.GL_T)} H{F(B.GL_H)} 坐 Z{F(B.Z_G)} (内卡顶 Z{F(B.Z_VIEW0)} = LED 下沿 Z{F(B.Z_LED0)} − {F(B.VIEW_MARGIN)}), 单边间隙 {F(B.GL_CLR)}",
            f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.Z_G)}; 内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}",
            f"三角块厚 {F(B.TRI_T)} (十字 ±{F(B.P_N)} 外); 墙内面 = 内卡内面 r{F(B.SPIG_IN)} 直下; 无托块",
            f"三角块两直边各一片斜筋 ×8: 厚 {F(B.GU_T)}, 外侧面齐直边 ±{F(B.P_N)}; 尖角 Z{F(B.TRI_T)} → r{F(B.GU_R85)} Z{F(B.GU_Z1)} (定子盘/外裙下) → 贴墙 Z{F(B.GU_ZH)}",
            f"+X XT60 开口 = 压块 +0.2; M3 法兰螺母井 Φ{F(B.XT_NUT_WELL_D)} Z{F(B.XT_H)}→{F(B.XT_H + B.XT_NUT_WELL_H)}"]
sh_holes = [dict(tag="A", pts=B.SH_M6, spec="Φ3.4 通 (三角块)", where=ring_txt(B.SH_M6) + f"  M3×14 盘底往上; M3 法兰螺母 (Φ7.6, 按 Φ{F(B.SH_NUT_D)} 留位) 压块顶, 贴墙内面 r{F(B.SPIG_IN)}"),
]
sh_zd = [(0, B.TRI_T), (0, B.Z_G), (B.Z_G, B.Z_G + B.OUT_DEPTH), (B.Z_G, B.Z_G + B.IN_DEPTH)]
sh_rd = [(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.go, B.SH_OUT)]
SPECS.append(dict(
    code="glass_shroud_v1_2", shape=B.seat, short="玻璃罩下罩+定位环 (合并)", qty="1 (与分体版二选一)",
    title="玻璃罩下罩 + 定位环 (合并版, 外卡一体)", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.gi, 2 * B.go, 2 * B.SH_OUT],
    sec=dict(ang=45, r0=70.0, zd=sh_zd, rd=sh_rd), holes=sh_holes,
    notes=gl_notes + [f"外卡 r{F(B.go)}–{F(B.SH_OUT)} 深 {F(B.OUT_DEPTH)}, 斜顶 (外缘直边 {F(B.LIP_EDGE)})"]))
SPECS.append(dict(
    code="glass_shroud_lower_v1_2", shape=B.shroud_lo, short="玻璃下 底座 (分体)", qty="1 (配玻璃座 + 外卡环)",
    title=f"玻璃下 底座: Z0→{F(B.SPLIT_Z)} + 顶面止口凸筋, {B.JN_N}× M4 通孔 + 底面法兰螺母窝", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.JN_R, 2 * B.RG_R0, 2 * (B.RG_R0 + B.RG_W), 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=70.0, zd=[(0, B.TRI_T), (0, B.SPLIT_Z), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H)], rd=[(B.SPIG_IN, B.SH_OUT), (B.RG_R0, B.RG_R0 + B.RG_W)]),
    holes=sh_holes + [dict(tag="J", pts=B.JN_PTS, spec=f"Φ{F(B.JN_D)} 通 + 底面圆窝 Φ{F(B.JN_NUT_FD)} 深 {F(B.JN_NUT_Z1)} (M4 法兰螺母 法兰朝上压入)",
                           where=ring_txt(B.JN_PTS) + f"  配玻璃座 M4×{F(B.JN_L)}",
                           det=dict(kind="cb", d=B.JN_D, D=B.JN_NUT_D, h=B.JN_NUT_Z1, side="bot", z=(0, B.SPLIT_Z), pt=B.JN_PTS[0], title="螺母窝 J (圆 Φ9.8, 法兰朝上压入)"))],
    notes=[f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.SPLIT_Z)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}"] + gl_notes[2:] + [f"底座+玻璃座分界 Z{F(B.SPLIT_Z)} (承载盘顶); 顶面止口凸筋 r{F(B.RG_R0)}–{F(B.RG_R0 + B.RG_W)} 高 {F(B.RG_H)} 插玻璃座底槽 (单边 {F(B.RG_CLR)})",
                          "以后改可视高度只重打玻璃座, 本件不动", f"M4×{F(B.JN_L)} 穿通两段: 尾 Z{F(B.JN_TIP)}, 法兰螺母 Z{F(B.JN_NUT_Z1 - B.JN_NUT_H)}..{F(B.JN_NUT_Z1)} (啮合 {F(B.JN_NUT_Z1 - B.JN_TIP)}), 底面平坐底盘"]))
SPECS.append(dict(
    code="glass_shroud_upper_v1_2", shape=B.shroud_hi, short="玻璃下 玻璃座 (分体)", qty="1",
    title=f"玻璃下 玻璃座: Z{F(B.SPLIT_Z)}→{F(B.Z_G)} 墙 + 内卡到 Z{F(B.Z_VIEW0)}, {B.JN_N}× M4 沉孔", orient="底面 (止口槽面) 贴床",
    phi=[2 * B.SPIG_IN, 2 * B.gi, 2 * B.JN_R, 2 * B.TG_R0, 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=86.0, zd=[(B.SPLIT_Z, B.Z_G), (B.Z_G, B.Z_G + B.IN_DEPTH), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H + B.RG_CLR), (B.Z_G - B.TG_H - B.TG_CLR, B.Z_G)],
             rd=[(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.RG_R0 - B.RG_CLR, B.RG_R0 + B.RG_W + B.RG_CLR)]),
    holes=[dict(tag="J", pts=B.JN_PTS, spec=f"Φ{F(B.JN_D)} 通 + 顶面 Φ{F(B.JN_CB)} 沉孔深 {F(B.Z_G - B.JN_BEAR)}", where=ring_txt(B.JN_PTS) + f"  M4×{F(B.JN_L)} 超薄头 穿通到底座底面法兰螺母",
                det=dict(kind="cb", d=B.JN_D, D=B.JN_CB, h=B.Z_G - B.JN_BEAR, side="top", z=(B.SPLIT_Z, B.Z_G), pt=B.JN_PTS[0], title="M4 沉孔 J"))],
    notes=[gl_notes[0], f"内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)} (顶 Z{F(B.Z_VIEW0)} = 可视下边界)",
           f"底面止口槽 r{F(B.RG_R0 - B.RG_CLR)}–{F(B.RG_R0 + B.RG_W + B.RG_CLR)} 深 {F(B.RG_H + B.RG_CLR)}; 顶面外卡环槽 r{F(B.TG_R0 - B.TG_CLR)}–{F(B.TG_R0 + B.TG_W + B.TG_CLR)} 深 {F(B.TG_H + B.TG_CLR)}",
           f"螺丝头顶 Z{F(B.JN_BEAR + B.JN_HH)}, 玻璃端面 + 外卡环盖住; 拆: 外卡环 → 玻璃 → {B.JN_N} 螺丝 → 玻璃座"]))
SPECS.append(dict(
    code="glass_clamp_ring_v1_2", shape=B.clamp_ring, short="外卡环 (分体)", qty="1",
    title=f"外卡环: r{F(B.go)}–{F(B.SH_OUT)} 斜顶 + 底凸筋 {F(B.TG_W)}×{F(B.TG_H)}", orient="凸筋朝上, 斜顶朝下需支撑 (或按切片软件)",
    phi=[2 * B.go, 2 * B.TG_R0, 2 * (B.TG_R0 + B.TG_W), 2 * B.SH_OUT],
    sec=dict(ang=0, r0=96.0, zd=[(B.Z_G - B.TG_H, B.Z_G), (B.Z_G, B.Z_G + B.OUT_DEPTH), (B.Z_G, B.Z_G + B.LIP_EDGE, f"{F(B.LIP_EDGE)} (外缘直边)")],
             rd=[(B.go, B.SH_OUT), (B.TG_R0, B.TG_R0 + B.TG_W)]),
    holes=[],
    notes=[f"内面 r{F(B.go)} 贴玻璃外壁 (单边间隙 {F(B.GL_CLR)})",
           f"底凸筋 r{F(B.TG_R0)}–{F(B.TG_R0 + B.TG_W)} 高 {F(B.TG_H)} 插下罩顶槽", "装配: 玻璃先套内卡, 再从上套环"]))

# ---------------- 玻璃上 (顶盖) 两件 (11-13) ----------------
SPECS.append(dict(
    code="glass_top_v1_2", shape=B.glass_top, short="玻璃上 (顶盖环)", qty="1",
    title=f"玻璃上: 内卡 r{F(B._gin)}–{F(B.gi)} + 外卡 r{F(B.go)}–{F(B.SH_OUT)} 夹玻璃上端, 圆环玻璃窝 Φ{F(2 * B.GD_POCKET_R)}",
    subtitle=f"玻璃罩上端 Z{F(B.Z_GT)}; 圆环玻璃 OD{F(B.GD_OD)}×ID{F(B.GD_ID)}×{F(B.GD_T)} 坐托台 Z{F(B.GD_Z0)}, 顶面低于环顶 {F(B.GD_RECESS)}",
    orient=f"正立 (两卡底面 Z{F(B.GT_Z0)} 贴床), 免支撑: 外卡斜面 {B.GT_CONE_DEG:.0f}°, 托台底面 45°, 玻璃槽顶 {F(B.go - B.gi)} 宽桥接",
    phi=[2 * B.GT_LEDGE_R, 2 * B.GD_POCKET_R, 2 * B.gi, 2 * B.go, 2 * B.SH_OUT],
    sec=dict(ang=0, r0=80.0, zd=[(B.GT_Z0, B.Z_GT), (B.Z_GT, B.GT_Z1), (B.GD_Z0, B.GT_Z1), (B.GT_Z0, B.GT_Z1), (B.Z_GT - B.LIP_EDGE, B.Z_GT)],
             rd=[(B._gin, B.gi), (B.go, B.SH_OUT), (B.GT_LEDGE_R, B.GD_POCKET_R)]),
    holes=[],
    notes=[f"玻璃罩 OD{F(B.GL_OD)}×{F(B.GL_T)} 上端插进 r{F(B.gi)}–{F(B.go)} 槽 (单边 {F(B.GL_CLR)}), 卡深 {F(B.GT_DEPTH)} (内外同深)",
           f"外卡斜面 (r{F(B.go + B.GT_FOOT)}, Z{F(B.GT_Z0)}) → (r{F(B.SH_OUT)}, Z{F(B.Z_GT - B.LIP_EDGE)}) (外缘直边 {F(B.LIP_EDGE)} 同玻璃下), 底平带 {F(B.GT_FOOT)}; 顶外缘倒角 {F(B.GT_CH)}",
           f"圆环玻璃窝 r{F(B.GD_POCKET_R)} (单边 {F(B.GD_CLR)}) 深 {F(B.GT_Z1 - B.GD_Z0)}, 口倒角 0.5; 托台 r{F(B.GT_LEDGE_R)}–{F(B.GD_POCKET_R)} (搭玻璃 {F(B.GD_OD / 2 - B.GT_LEDGE_R)})",
           f"玻璃靠自重 ({B.LOG['glass_top']['disc_mass_g']} g) 坐托台, 径向靠窝; 环靠自重 + 内外卡坐在玻璃罩上端"]))
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

# ---------------- V2 灯板支撑五件 (11-16 新转子布局, led_support_v1_2.py) ----------------
import led_support_v1_2 as L  # noqa: E402
_fa = [p for p in L.FOOT_PTS if p[0] > 0]; _fb = [p for p in L.FOOT_PTS if p[0] < 0]
_eng = lambda bear, L_, ins: min(bear, ins[1]) - max(bear - L_, ins[0])


def _foot_hole(pts):
    return dict(tag="F", pts=pts, spec=f"Φ3.4 通 (凸台 Φ{F(L.PAD_D)} Z{F(L.RIM_TOP)}–{F(L.FOOT_CB_Z)}, 不沉孔); M3×{F(L.FOOT_SCREW_L)} 内六角, 头坐凸台顶 Z{F(L.FOOT_CB_Z)}",
                where=xy(pts) + f"  承载盘 r{F(L.R_HOLE)} 原孔\n从上穿承载盘+毂盘, 进毂盘底 M3×4 铜螺母 Z{F(L.HUB_INS[0])}–{F(L.HUB_INS[1])}, 尾 Z{F(L.FOOT_CB_Z - L.FOOT_SCREW_L)}, 啮合 {F(_eng(L.FOOT_CB_Z, L.FOOT_SCREW_L, L.HUB_INS))}",
                det=dict(kind="free", z=(L.RIM_TOP, L.FOOT_CB_Z), pt=pts[0], ang=90, W=L.PAD_D / 2 + 1.8, title="T 脚凸台孔 F (沿 y 剖)",
                         zd=[(L.RIM_TOP, L.FOOT_CB_Z, F(L.FOOT_CB_Z - L.RIM_TOP))], ud=[(-1.7, 1.7, "Φ3.4"), (-L.PAD_D / 2, L.PAD_D / 2, f"Φ{F(L.PAD_D)} 凸台", 5)]))


_h1 = lambda sx: dict(tag="H", pts=[(sx * L.H1_X, 0.0)], spec=f"Φ3.4 沿 Y 横穿立刀, 中心 Z{F(L.H1_Z)} (灯板下沿 +{F(L.H1_Z - L.Z0)})",
                      where=f"x {F(sx * L.H1_X)}  灯板 H1/H2 M3×{F(L.SCREW_H1_L)} 内六角 + M3 法兰螺母")
_post_notes = [
    f"T 脚: 横杆 x{F(L.T_X - L.T_W / 2)}–{F(L.T_X + L.T_W / 2)} 沿 y 到 |y|{F(L.FOOT_Y)}, Z{F(L.RIM_TOP)}–{F(L.Z0)} 坐承载盘顶; 顶面 Z{F(L.Z0)} 托两灯板下沿",
    f"T 脚中段 |y|≤{F(L.ANT_HW)} 连到天线板; 整件外缘裁到 r≤{F(L.R_CLIP)} (转子罩内壁 r86); 底梁已删",
    f"立刀 x{F(L.BLADE_X0)}–{F(L.BLADE_X1)} 厚 {F(L.BLADE_T)} Z{F(L.Z0)}–{F(L.BLADE_Z1)}, 夹两灯板 F 面之间 (间隙 {F(2 * L.GAP_HALF)}, 单边 {F(L.CLR)}), 盖下角 F.Mask 窗",
    f"天线板 x{F(L.ANT_X0)}–{F(L.ANT_X1)} 厚 {F(L.ANT_X1 - L.ANT_X0)} |y|≤{F(L.ANT_HW)} Z{F(L.RIM_TOP)}–{F(L.ANT_Z1)}, 外角 r≤{F(L.ANT_R_MAX)}",
    f"天线竖贴: 外面浅槽 {F(L.ANT_L)}×{F(L.ANT_W)}×{F(L.ANT_REC)} 贴 Molex 219611 (背胶), 长边沿 Z, 槽心 Z{F(L.ANT_ZC)}",
    f"T 脚螺丝头 Φ5.5 外缘 r{F(L.R_HOLE + 2.75)} (罩内壁 r86)"]
_post = lambda sx: dict(
    shape=L.post_a if sx > 0 else L.post_b, qty="1", material="PETG (建议) / PLA",
    orient=f"正立 (T 脚底面 Z{F(L.RIM_TOP)} 贴床), 免支撑",
    sec=dict(ang=0 if sx > 0 else 180, r0=66.0,
             zd=[(L.RIM_TOP, L.Z0, f"{F(L.Z0 - L.RIM_TOP)} T脚"), (L.Z0, L.BLADE_Z1, f"{F(L.BLADE_Z1 - L.Z0)} 立刀"), (L.RIM_TOP, L.ANT_Z1)],
             rd=[(L.T_X - L.T_W / 2, L.ANT_X1), (L.BLADE_X0, L.ANT_X0), (L.ANT_X0, L.ANT_X1)]),
    holes=[_foot_hole(_fa if sx > 0 else _fb), _h1(sx)])
SPECS.append(dict(
    _post(+1), code="led_post_a_v1_2", short="灯板支撑 +x 端 (T 脚)",
    title="灯板支撑 +x 端: T 形脚 (2×M3×16 进毂盘底铜螺母) + 立刀 (M3 穿 H1) + 竖贴天线板",
    notes=_post_notes + [f"T 脚孔 @22.5°/337.5°; H1: +y 侧内六角头, −y 侧法兰螺母 (+y LED 面有 5.9 高电解)"]))
SPECS.append(dict(
    _post(-1), code="led_post_b_v1_2", short="灯板支撑 −x 端 (T 脚)",
    title="灯板支撑 −x 端: T 形脚 (2×M3×16 进毂盘底铜螺母) + 立刀 (M3 穿 H1) + 竖贴天线板",
    notes=_post_notes + [f"与 +x 端镜像, T 脚孔 @157.5°/202.5°; H1: −y 侧内六角头, +y 侧法兰螺母"]))

_lx0, _lx1 = L.GATE_PTS[0][0] - L.LEG_HX, L.GATE_PTS[0][0] + L.LEG_HX
SPECS.append(dict(
    code="led_gate_v1_2", shape=L.gate_s, short="灯板门形中间支撑", qty="1", material="PETG (建议) / PLA",
    title=f"灯板门形中间支撑: 两腿 M3×{F(L.GATE_SCREW_L)} 锁承载盘 + 横梁 {F(L.BEAM_X1 - L.BEAM_X0)} 托板下沿 + 中间立舌",
    orient=f"正立 (两腿底 Z{F(L.RIM_TOP)} 贴床), 梁底 Z{F(L.BEAM_Z0)} 下 {F(L.BEAM_Z0 - L.RIM_TOP)} 高缝加支撑",
    sec=dict(ang=0, r0=0.0, zd=[(L.RIM_TOP, L.Z0, f"{F(L.Z0 - L.RIM_TOP)} 腿"), (L.Z0, L.TONGUE_Z1, f"{F(L.TONGUE_Z1 - L.Z0)} 立舌"), (L.BEAM_Z0, L.Z0, f"{F(L.Z0 - L.BEAM_Z0)} 梁")],
             rd=[(0, L.TONGUE_X), (_lx0, _lx1, f"{F(_lx1 - _lx0)} 腿"), (0, _lx1)]),
    holes=[dict(tag="G", pts=L.GATE_PTS,
                spec=f"Φ3.4 通 + 顶面 Φ{F(L.GATE_CB_D)} 沉孔深 {F(L.Z0 - L.GATE_CB_Z)} (M3×{F(L.GATE_SCREW_L)} 内六角, 头支承 Z{F(L.GATE_CB_Z)}, 头顶齐梁顶)",
                where=xy(L.GATE_PTS) + f"  进承载盘 M3×4 铜螺母 Z{F(L.GATE_INS[0])}–{F(L.GATE_INS[1])}, 啮合 {F(_eng(L.GATE_CB_Z, L.GATE_SCREW_L, L.GATE_INS))}",
                det=dict(kind="cb", d=3.4, D=L.GATE_CB_D, h=L.Z0 - L.GATE_CB_Z, side="top", z=(L.RIM_TOP, L.Z0), pt=L.GATE_PTS[0], ang=90, title="门腿沉孔 G (沿 y 剖)"))],
    notes=[f"横梁 x{F(L.BEAM_X0)}…{F(L.BEAM_X1)} |y|≤{F(L.BEAM_Y)} Z{F(L.BEAM_Z0)}–{F(L.Z0)}: 梁顶托两灯板下沿 Z{F(L.Z0)} (盖住两板 |y|≤3.77)",
           f"梁下给 FPC 留缝: FPC 平铺毂盘顶 Z{F(L.HUB_TOP)} (厚 {F(L.FPC_T)}), 到梁底净空 {F(L.BEAM_Z0 - L.HUB_TOP - L.FPC_T)}",
           f"两腿 {F(2 * L.LEG_HX)}×{F(2 * L.LEG_HY)} @ x±{F(L.GATE_PTS[0][0])}, Z{F(L.RIM_TOP)}–{F(L.Z0)} 坐承载盘顶",
           f"立舌 x±{F(L.TONGUE_X)} 厚 {F(L.BLADE_T)} Z{F(L.Z0)}–{F(L.TONGUE_Z1)} 插两板之间, 进下中 F.Mask 窗 (下沿 +7…17)"]))

SPECS.append(dict(
    code="led_top_v1_2", shape=L.top, short="灯板顶部件 (加长 Φ14 轴座)", qty="1", material="PETG (建议) / PLA",
    title=f"灯板顶部件: 舌 + 帽 {F(2 * L.CAP_X)}×{F(2 * L.CAP_Y)}×{F(L.CAP_T)} + 加长轴座 Φ{F(L.BOSS_D)}, 压 Φ{F(L.ROD_D)}×{F(L.ROD_L)} 钢轴进 688",
    orient=f"倒放 (轴座顶 Φ{F(L.BOSS_D)} 贴床), 帽两端小悬空",
    sec=dict(ang=0, r0=0.0, zd=[(L.TOP_TONGUE_Z0, L.Z1, f"{F(L.Z1 - L.TOP_TONGUE_Z0)} 舌"), (L.Z1, L.Z1 + L.CAP_T, f"{F(L.CAP_T)} 帽"), (L.Z1 + L.CAP_T, L.BOSS_Z1, f"{F(L.BOSS_Z1 - L.Z1 - L.CAP_T)} 轴座")],
             rd=[(0, L.TONGUE_X, f"{F(L.TONGUE_X)}"), (0, L.BOSS_D / 2, f"R{F(L.BOSS_D / 2)}"), (0, L.CAP_X, f"{F(L.CAP_X)}")]),
    holes=[dict(tag="R", pts=[(0.0, 0.0)], spec=f"Φ{F(L.ROD_HOLE_D)} 盲孔深 {F(L.BOSS_Z1 - L.ROD_Z0)} (压 Φ8 h6 钢轴, 试配)", where="轴心",
                det=dict(kind="blind", D=L.ROD_HOLE_D, h=L.BOSS_Z1 - L.ROD_Z0, side="top", z=(L.Z1 + L.CAP_T, L.BOSS_Z1), pt=(0.0, 0.0), title="轴孔 R")),
           dict(tag="N", pts=[(L.COMB_FIX_X, 0.0), (-L.COMB_FIX_X, 0.0)], spec=f"Φ4.2 通帽 (厚 {F(L.CAP_T)}) 压 M3×4 铜螺母",
                where=f"x ±{F(L.COMB_FIX_X)}  梳齿 led_comb 用 M3×8 锁帽 (孔下是两板间隙)", lab_off=(2.4, -3.0))],
    notes=[f"舌 x±{F(L.TONGUE_X)} 厚 {F(L.BLADE_T)} Z{F(L.TOP_TONGUE_Z0)}–{F(L.Z1)} 插两板之间 (上中窗); 帽底贴板上沿 Z{F(L.Z1)}",
           f"轴座 Z{F(L.Z1 + L.CAP_T)}–{F(L.BOSS_Z1)} (长 {F(L.BOSS_Z1 - L.Z1 - L.CAP_T)}, 11-16 加长), 顶离堵头爪尖 {F(L.BOSS_GAP)}",
           f"钢轴 Φ{F(L.ROD_D)}×{F(L.ROD_L)} h6 Z{F(L.ROD_Z0)}–{F(L.ROD_Z1)}, 压入轴座 {F(L.BOSS_Z1 - L.ROD_Z0)}; 688 Z{F(L.BRG_Z0)}–{F(L.BRG_Z1)}",
           "玻璃罩长度公差: 短 ≤2.0 轴顶进堵头 Φ9 让位; 长 ≤4.5 仍有 0.5 啮合", "轴在 688 内圈滑配 (g6/h6), 可轴向窜动"]))

_cxm = L.COMB_TEETH_X[-1] + L.COMB_TOOTH_W / 2
SPECS.append(dict(
    code="led_comb_v1_2", shape=L.comb_s, short="顶部配平梳齿", qty="1", material="PETG (建议) / PLA",
    title=f"顶部配平梳齿: 套轴座坐帽顶, 2×M3×8 锁帽, 每侧 {len(L.COMB_TEETH_X)} 齿 × 4 孔挂配重",
    orient=f"平放 (底面 Z{F(L.COMB_Z0)} 贴床), 免支撑",
    phi=[L.COMB_HOLE_D, L.COMB_RING_D],
    sec=dict(ang=0, r0=0.0, zd=[(L.COMB_Z0, L.COMB_Z1)],
             rd=[(0, L.COMB_HOLE_D / 2), (0, L.COMB_RING_D / 2), (0, _cxm)], hmax=40),
    holes=[dict(tag="K", pts=[(L.COMB_FIX_X, 0.0), (-L.COMB_FIX_X, 0.0)], spec="Φ3.4 通; M3×8 内六角 → 帽内 M3×4 铜螺母 (啮合 4)",
                where=f"x ±{F(L.COMB_FIX_X)}", lab_off=(2.4, -3.0),
                det=dict(kind="free", z=(L.COMB_Z0, L.COMB_Z1), pt=(L.COMB_FIX_X, 0.0), ang=0, W=3.6, title="锁帽孔 K (沿 x 剖)",
                         zd=[(L.COMB_Z0, L.COMB_Z1, F(L.COMB_T))], ud=[(-1.7, 1.7, "Φ3.4")])),
           dict(tag="W", pts=L.COMB_SLOTS, spec="Φ3.4 竖通 — 配重 M3 螺丝竖装 + 螺母 (按需)", lab_off=(0.0, 0.0),
                where=f"齿 x ±{'/'.join(F(v) for v in L.COMB_TEETH_X)} (宽 {F(L.COMB_TOOTH_W)}), 每齿 y ±{F(L.COMB_SLOTS_Y[0])} / ±{F(L.COMB_SLOTS_Y[1])}; r≤{F(max(math.hypot(*p) for p in L.COMB_SLOTS))}",
                det=dict(kind="free", z=(L.COMB_Z0, L.COMB_Z1), pt=L.COMB_SLOTS[0], ang=0, W=4.6, title="配重孔 W (沿 x 剖)",
                         zd=[(L.COMB_Z0, L.COMB_Z1, F(L.COMB_T))], ud=[(-1.7, 1.7, "Φ3.4"), (-L.COMB_TOOTH_W / 2, L.COMB_TOOTH_W / 2, f"{F(L.COMB_TOOTH_W)} 齿宽", 5)]))],
    notes=[f"横梁 x±{F(_cxm)} |y|≤{F(L.COMB_BEAM_Y)} + 中心环 Φ{F(L.COMB_RING_D)}, 厚 {F(L.COMB_T)} Z{F(L.COMB_Z0)}–{F(L.COMB_Z1)}",
           f"中心孔 Φ{F(L.COMB_HOLE_D)} 套轴座 Φ{F(L.BOSS_D)} (单边 0.1), 坐顶部件帽顶 Z{F(L.COMB_Z0)}",
           f"齿 {F(L.COMB_TOOTH_W)} 宽沿 y ±{F(L.COMB_TOOTH_Y)}; 共 {len(L.COMB_SLOTS)} 个配重孔",
           f"配重 M3 螺丝竖装, 螺母在齿下 Z246.6–{F(L.COMB_Z0)} (> 板上沿 Z{F(L.Z1)}); 头下长 ≤{F(L.COMB_SCREW_MAX_L)} (每多叠 1 螺母 +2.4)",
           "两面配平的上面: 修残余不平衡 (led_support_report.json → balance.two_plane), 以实测动平衡为准"]))

# ---------------- 转子罩 (11-16, rotor_shroud_v1_2.py; import 只建几何, 不写文件) ----------------
import rotor_shroud_v1_2 as RS  # noqa: E402
_rm = [RS.pol(RS.HOLE_R, a) for a in RS.MNT_A if math.cos(math.radians(a)) > 0]
_rw = [RS.pol(RS.W_R, a) for a in RS.W_A if math.cos(math.radians(a)) > 0]
SPECS.append(dict(
    code="rotor_shroud_a_v1_2", shape=RS.shr_a, short="转子罩半壳 (A/B 同件)", qty="2 (A/B 同一件, B = A 绕 Z 转 180°)", material="PETG (建议) / PLA",
    title=f"转子罩半壳 ×2 (两半同件): 罩壁 r{F(RS.R0)}–{F(RS.R1)} + 罩底凸台 + 配重唇 + 分缝凸耳",
    subtitle=f"图示 A 半 (+x); B 半 = 同一打印件绕 Z 转 180° 装在 −x。罩 Z{F(RS.Z0)}–{F(RS.Z1)} 坐承载盘顶, 顶开口",
    orient=f"倒放 (罩顶 Z{F(RS.Z1)} + 配重唇顶面贴床), 免支撑",
    sec=dict(ang=45, r0=74.0, zd=[(RS.Z0, RS.Z1), (RS.LIP_Z0, RS.Z1, f"{F(RS.Z1 - RS.LIP_Z0)} 唇"), (RS.Z0, RS.LEDGE_Z1, f"{F(RS.LEDGE_Z1 - RS.Z0)} 内沿")],
             rd=[(RS.R0, RS.R1, f"{F(RS.R1 - RS.R0)} 壁"), (RS.LIP_R0, RS.R0, f"{F(RS.R0 - RS.LIP_R0)} 唇"), (RS.LEDGE_R0, RS.R0, f"{F(RS.R0 - RS.LEDGE_R0)} 内沿")]),
    holes=[dict(tag="M", pts=_rm, spec=f"Φ3.4 通凸台 Z{F(RS.Z0)}–{F(RS.BOSS_Z1)} + 上方 Φ{F(RS.ACC_D)} 起子让位孔 (斜撑/配重唇)",
                where=xy(_rm) + f"  r{F(RS.HOLE_R)} @ 67.5°/292.5° (B 半: 247.5°/112.5°)\nM3×{F(RS.MNT_L)} 内六角 头支承 Z{F(RS.BOSS_Z1)}, 穿承载盘+毂盘进毂盘底 M3×4 铜螺母 Z{F(RS.INS_Z[0])}–{F(RS.INS_Z[1])}",
                det=dict(kind="free", z=(RS.Z0, RS.GUS_Z1 + 1), pt=_rm[0], W=RS.ACC_D / 2 + 2.0, title="罩底凸台孔 M (径向剖)",
                         zd=[(RS.Z0, RS.BOSS_Z1, f"{F(RS.BOSS_Z1 - RS.Z0)} 凸台")], ud=[(-1.7, 1.7, "Φ3.4"), (-RS.ACC_D / 2, RS.ACC_D / 2, f"Φ{F(RS.ACC_D)} (上)", 5)])),
           dict(tag="W", pts=_rw, spec=f"Φ3.4 通配重唇 + 顶面 Φ{F(RS.W_CB_D)} 沉孔深 {F(RS.W_CB_H)}", lab_off=(-2.6, 2.0),
                where=f"r{F(RS.W_R)} @ " + "/".join(F(a) for a in RS.W_A if math.cos(math.radians(a)) > 0) + "°"
                      + f"\nM3×{F(RS.W_L)} 内六角 头顶 Z{F(RS.W_BEAR + 3)} < 罩顶; 唇下挂 ≤{RS.W_NUT_MAX} 颗 M3 螺母/垫片 (尾 Z{F(RS.W_TIP)})",
                det=dict(kind="cb", d=3.4, D=RS.W_CB_D, h=RS.W_CB_H, side="top", z=(RS.LIP_Z0, RS.Z1), pt=RS.pol(RS.W_R, 45), title="配重孔 W")),
           dict(tag="S", pts=[(RS.LUG_HX / 2, RS.LUG_SY), (RS.LUG_HX / 2, -RS.LUG_SY)],
                spec=f"凸耳 Φ3.4 沿 X 横穿 ×2 层 (Z{F(RS.LUG_SZ[0])} / Z{F(RS.LUG_SZ[1])}), M3×{F(RS.SEAM_L)} + M3 螺母",
                where=f"|y|{F(RS.LUG_SY)}; +y 缝: 外侧 (x{F(RS.LUG_HX - RS.NUT_DEPTH)}–{F(RS.LUG_HX)}) 六角螺母槽 {F(RS.NUT_AF)} 对边, 口朝罩内\n−y 缝: 螺丝头侧 (头坐 x{F(RS.LUG_HX)} 面); 装成整圈后两缝各 1 头 1 螺母",
                det=dict(kind="free", z=(RS.LUG_Z0, RS.LIP_Z0 + 0.5), pt=(RS.LUG_HX / 2, RS.LUG_SY), ang=0, W=RS.LUG_HX / 2 + 2.0, title="+y 分缝凸耳 S (沿 x 剖)",
                         zd=[(RS.LUG_Z0, RS.LIP_Z0 + 0.5, F(RS.LIP_Z0 + 0.5 - RS.LUG_Z0)), (RS.LUG_SZ[0], RS.LUG_SZ[1], F(RS.LUG_SZ[1] - RS.LUG_SZ[0]), 9)],
                         ud=[(-RS.LUG_HX / 2, RS.LUG_HX / 2, F(RS.LUG_HX))]))],
    notes=[f"罩壁 r{F(RS.R0)}–{F(RS.R1)} Z{F(RS.Z0)}–{F(RS.Z1)} (离不转玻璃座内壁 r{F(RS.ST_IN)} 留 {F(RS.ST_IN - RS.R1)}); 外面光滑, 分缝在 x=0",
           "两半 A (+x) / B (−x) 是同一个打印件 (B = A 绕 Z 转 180°), 打 2 个",
           f"罩底 4 凸台 @67.5/112.5/247.5/292.5° (每半 2) 压承载盘顶 + 45° 斜撑; |y|<{F(RS.BB_EDGE)} / |x|<{F(RS.WH_EDGE)} 削平",
           f"配重唇 r{F(RS.LIP_R0)}–{F(RS.R0)} Z{F(RS.LIP_Z0)}–{F(RS.Z1)} @ 33°–147° / 213°–327°; 每半 {len(_rw)} 孔, 全罩 {len(RS.W_A)} 孔",
           f"罩底内沿 r{F(RS.LEDGE_R0)}–{F(RS.R0)} Z{F(RS.Z0)}–{F(RS.LEDGE_Z1)} + 45° 斜面 (4 段, 让开 ±y |x|≤{F(RS.HOLDER_X)} 无线托盘)",
           f"分缝凸耳 x0–{F(RS.LUG_HX)} × |y|{F(RS.LUG_Y0)}–{F(RS.LUG_Y1)} × Z{F(RS.LUG_Z0)}–{F(RS.LIP_Z0)} (底 > 无线托盘顶 Z50)",
           "装/拆: 起子从罩顶开口竖直进, 穿配重唇 Φ6.5 让位孔拧罩底 M3×14",
           "每孔配重 M3×18+1 螺母 1.84 g … +6 螺母 3.55 g (见 rotor_shroud_report.json)"]))

# ---------------- 无线供电模块托盘 (11-16, wireless_holder_v1_2.py; import 只建几何) ----------------
import wireless_holder_v1_2 as WH  # noqa: E402
_wh_scr = WH.SCR_OUT + WH.SCR_IN
SPECS.append(dict(
    code="wireless_holder_v1_2", shape=WH.H, short="无线供电模块托盘", qty="1", material="PETG (建议) / PLA",
    title=f"无线供电模块托盘: 托底 + r{F(WH.OUT_R)} 承力外墙 + 3×M3×8 锁承载盘 + 2 扎带",
    subtitle=f"模块 {F(WH.MOD_W)}×{F(WH.MOD_L)}×{F(WH.MOD_H)} ({F(WH.MOD_G)} g) 长边沿 x, 中心 (0, {F(WH.MOD_YC)}), 坐托底 Z{F(WH.MZ0)}–{F(WH.MZ1)}; 转子盘 −y 侧",
    orient=f"正立 (底面 Z{F(WH.RIM_TOP)} 贴床, 打印姿态 = 装配姿态); 底面扎带槽小搭桥",
    sec=dict(ang=270, r0=24.0,
             zd=[(WH.RIM_TOP, WH.OUT_Z1, f"{F(WH.OUT_Z1 - WH.RIM_TOP)} 外墙"), (WH.RIM_TOP, WH.IN_Z1, f"{F(WH.IN_Z1 - WH.RIM_TOP)} 内墙"),
                 (WH.RIM_TOP, WH.MZ0, f"{F(WH.FLOOR_T)} 底")],   # 内舌高 4 (顶 Z36) 见说明
             rd=[(-WH.TONGUE_Y1, -(WH.MOD_Y1 + WH.IN_T), f"{F(WH.TONGUE_Y1 - WH.MOD_Y1 - WH.IN_T)} 舌"), (-WH.MOD_Y1, -WH.MOD_Y0, f"{F(WH.MOD_W)} 模块"),
                 (-WH.MOD_Y0, WH.OUT_R, f"{F(WH.OUT_R + WH.MOD_Y0)} 外墙")]),
    holes=[dict(tag="M", pts=_wh_scr, spec=f"Φ3.4 通 + 顶面 Φ{F(WH.CB_D)} 沉孔 (头支承 Z{F(WH.CB_Z)}; 内舌顶即 Z{F(WH.TONGUE_Z1)})",
                where=xy(_wh_scr, 3) + f"\nM3×8 内六角 → 承载盘 M3×4 铜螺母 Z{F(WH.RIM_TOP - 4)}–{F(WH.RIM_TOP)}, 啮合 4",
                det=dict(kind="cb", d=3.4, D=WH.CB_D, h=WH.OUT_Z1 - WH.CB_Z, side="top", z=(WH.RIM_TOP, WH.OUT_Z1), pt=WH.SCR_OUT[0], ang=0, title="外墙螺丝孔 M (沿 x 剖)"))],
    notes=[f"外墙 (−y 径向外) y{F(WH.MOD_Y0)} 到外面 r{F(WH.OUT_R)} 圆弧, 顶 Z{F(WH.OUT_Z1)}, 挡离心力 (承载盘 r85, 转子罩内壁 r86)",
           f"侧墙 {F(WH.SIDE_T)} 厚顶 Z{F(WH.SIDE_Z1)}; 内矮墙 {F(WH.IN_T)} 厚顶 Z{F(WH.IN_Z1)}; 内舌 x±{F(WH.TONGUE_X)} 到 y{F(WH.TONGUE_Y1)} 顶 Z{F(WH.TONGUE_Z1)}",
           f"扎带 ×2 (4.8 宽) @ y{F(WH.TIE_Y[0])} / {F(WH.TIE_Y[1])}: 模块顶 → 侧墙外槽 → 底面槽 {F(WH.TIE_W)}×{F(WH.TIE_T)}",
           f"底窗 ×4: +x 端 2 个对承载盘 AC 引线孔 {xy(WH.AC_HOLES, 2)}, 线圈线直上焊 AC 脚",
           "底窗 −x 端 2 个从侧墙底穿出, 24V/GND 线沿承载盘顶面出 (到底板 r2 P1)",
           "整件 + 模块 + 螺丝 ≈ 39.1 g, 质心 (0.08, −63.39); 1200 rpm 离心力 ≈ 39.1 N (wireless_holder_report.json)"]))
_D1116 = {"led_post_a_v1_2", "led_post_b_v1_2", "led_gate_v1_2", "led_top_v1_2", "led_comb_v1_2", "rotor_shroud_a_v1_2", "wireless_holder_v1_2"}
for sp in SPECS:
    if sp["code"] in _D1116:
        sp.setdefault("date", "2026-11-16")      # 11-16 新转子布局
    sp.update({k: v for k, v in COMMON.items() if k not in sp})
    sp["stl"] = M / sp["code"] / f"{sp['code']}.stl"
    sp["src"] = f"v1.2/models/{sp['code']}/{sp['code']}.stl"
    sp.setdefault("origin_note", ORIG)

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sp in SPECS:
        if only and sp["code"] not in only:
            continue
        sp["out"] = sp["stl"].parent / f"{sp['code']}_drawing.pdf"
        try:
            out, png, sl = draw(sp)
        except PermissionError:
            sp["out"] = sp["out"].with_name(f"{sp['code']}_drawing.NEW.pdf")
            out, png, sl = draw(sp)
        print(f"wrote {out}  ({sl})", flush=True)
