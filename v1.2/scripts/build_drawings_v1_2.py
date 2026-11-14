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
    code="glass_shroud_lower_v1_2", shape=B.shroud_lo, short="玻璃下 下段 (分体)", qty="1 (配上段 + 外卡环)",
    title=f"玻璃下 下段: Z0→{F(B.SPLIT_Z)} + 顶面止口凸筋, {B.JN_N}× M3 通孔 + 底面法兰螺母沉孔", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.JN_R, 2 * B.RG_R0, 2 * (B.RG_R0 + B.RG_W), 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=70.0, zd=[(0, B.TRI_T), (0, B.SPLIT_Z), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H)], rd=[(B.SPIG_IN, B.SH_OUT), (B.RG_R0, B.RG_R0 + B.RG_W)]),
    holes=sh_holes + [dict(tag="J", pts=B.JN_PTS, spec=f"Φ3.4 通 + 底面 Φ{F(B.JN_NUT_D)} 沉孔深 {F(B.JN_NUT_Z1)} (M3 法兰螺母 法兰朝上)",
                           where=ring_txt(B.JN_PTS) + f"  配上段 M3×{F(B.JN_L)}",
                           det=dict(kind="cb", d=3.4, D=B.JN_NUT_D, h=B.JN_NUT_Z1, side="bot", z=(0, B.SPLIT_Z), pt=B.JN_PTS[0], title="螺母沉孔 J"))],
    notes=[f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.SPLIT_Z)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}"] + gl_notes[2:] + [f"上下段分界 Z{F(B.SPLIT_Z)} (承载盘顶); 顶面止口凸筋 r{F(B.RG_R0)}–{F(B.RG_R0 + B.RG_W)} 高 {F(B.RG_H)} 插上段底槽 (单边 {F(B.RG_CLR)})",
                          "以后改可视高度只重打上段, 本件不动", f"M3×{F(B.JN_L)} 穿通两段: 尾 Z{F(B.JN_TIP)}, 法兰螺母 Z{F(B.JN_TIP)}..{F(B.JN_NUT_Z1)} 全埋, 底面平坐底盘"]))
SPECS.append(dict(
    code="glass_shroud_upper_v1_2", shape=B.shroud_hi, short="玻璃下 上段 (分体)", qty="1",
    title=f"玻璃下 上段: Z{F(B.SPLIT_Z)}→{F(B.Z_G)} 墙 + 内卡到 Z{F(B.Z_VIEW0)}, {B.JN_N}× M3 沉孔", orient="底面 (止口槽面) 贴床",
    phi=[2 * B.SPIG_IN, 2 * B.gi, 2 * B.JN_R, 2 * B.TG_R0, 2 * B.SH_OUT],
    sec=dict(ang=B.JN_ANG0, r0=86.0, zd=[(B.SPLIT_Z, B.Z_G), (B.Z_G, B.Z_G + B.IN_DEPTH), (B.SPLIT_Z, B.SPLIT_Z + B.RG_H + B.RG_CLR), (B.Z_G - B.TG_H - B.TG_CLR, B.Z_G)],
             rd=[(B.gi - B.SPIG_T, B.gi), (B.SPIG_IN, B.SH_OUT), (B.RG_R0 - B.RG_CLR, B.RG_R0 + B.RG_W + B.RG_CLR)]),
    holes=[dict(tag="J", pts=B.JN_PTS, spec=f"Φ3.4 通 + 顶面 Φ7 沉孔深 {F(B.Z_G - B.JN_BEAR)}", where=ring_txt(B.JN_PTS) + f"  M3×{F(B.JN_L)} 穿通到下段底面法兰螺母",
                det=dict(kind="cb", d=3.4, D=7.0, h=B.Z_G - B.JN_BEAR, side="top", z=(B.SPLIT_Z, B.Z_G), pt=B.JN_PTS[0], title="M3 沉孔 J"))],
    notes=[gl_notes[0], f"内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)} (顶 Z{F(B.Z_VIEW0)} = 可视下边界)",
           f"底面止口槽 r{F(B.RG_R0 - B.RG_CLR)}–{F(B.RG_R0 + B.RG_W + B.RG_CLR)} 深 {F(B.RG_H + B.RG_CLR)}; 顶面外卡环槽 r{F(B.TG_R0 - B.TG_CLR)}–{F(B.TG_R0 + B.TG_W + B.TG_CLR)} 深 {F(B.TG_H + B.TG_CLR)}",
           f"螺丝头顶 Z{F(B.JN_BEAR + 1.5)}, 玻璃端面 + 外卡环盖住; 拆: 外卡环 → 玻璃 → {B.JN_N} 螺丝 → 上段"]))
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
           "可选 GT_BEARING=1: 法兰加厚到 6.5, 内开 688 窝 Φ16.1×5 (轴承从下穿爪内孔 Φ16.4 压入)"]))

for sp in SPECS:
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
