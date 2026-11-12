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
ins = "Φ3.2 通 + 底面 Φ4.2×4.5 铜螺母孔"
SPECS.append(dict(
    code="base_disc_v1_2", shape=B.disc, short=f"底盘 Φ{F(B.DISC_D)}×{F(B.DISC_T)}", qty="1",
    title=f"打印底盘 Φ{F(B.DISC_D)}×{F(B.DISC_T)} (合并电机控制板托板 + 散热片槽)",
    subtitle="沉孔 / 铜螺母孔全部开在底面 (Z-6); 顶面 Z0 = 装配基准 (电机/控制板/线圈环/下罩都坐在上面)",
    orient="顶面 (Z0) 贴床, 底面沉孔朝上",
    phi=[24, 2 * B.R_SCREW, 2 * B.STATOR_R, (2 * B.RING_M3_XY, f"{F(2 * B.RING_M3_XY)} (方)"), 2 * B.SH_R, B.DISC_D],
    sec=dict(ang=45, zd=[(-B.DISC_T, 0.0)], rd=[(0, B.STATOR_R), (0, math.hypot(B.RING_M3_XY, B.RING_M3_XY)), (0, B.SH_R)]),
    holes=[
        dict(tag="A", pts=B.POSTS, spec=cb6 + " (立柱)", where="V0.4 柱位 " + xy(B.POSTS),
             det=dict(kind="cb", d=B.M6_D, D=B.CB_D, h=B.CB_H, side="bot", z=ZD, pt=B.POSTS[0], title="M6 沉孔 (A/B/C 同)")),
        dict(tag="B", pts=grid_np, spec=cb6 + "  同详图 A", where=f"原 M6 网格 节距 25, 盘内放得下的全开; 跳过 {len(B.SKIP)} 位"),
        dict(tag="C", pts=B.XT_GHOLES_DISC, spec=cb6 + "  同详图 A (XT60 压块)", where=xy(B.XT_GHOLES_DISC) + "  M6×20", lab_off=(-2.4, 2.4)),
        dict(tag="D", pts=B.MOTOR_HOLES, spec=cb3 + " (电机)", where=f"对角 {F(2 * B.STATOR_R)}  M3×8 (待电机螺孔深度确认)",
             det=dict(kind="cb", d=B.M3_D, D=B.M3_CB_D, h=B.M3_CB_H, side="bot", z=ZD, pt=B.MOTOR_HOLES[0], title="M3 沉孔 (D/E/F 同)")),
        dict(tag="E", pts=B.RING_M3, spec=cb3 + "  同详图 D (线圈环四角)", where=f"(±{F(B.RING_M3_XY)}, ±{F(B.RING_M3_XY)})  M3×12, 法兰螺母压四角顶"),
        dict(tag="F", pts=B.SH_M6, spec=cb3 + "  同详图 D (下罩)", where=ring_txt(B.SH_M6) + "  M3×14, 法兰螺母压三角块顶"),
        dict(tag="G", pts=B.FLANGE_SCREWS, spec=ins + " (线圈环/定子盘)", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20",
             det=dict(kind="ins", d=3.2, D=4.2, h=4.5, side="bot", z=ZD, pt=B.FLANGE_SCREWS[0], title="M3 铜螺母孔 (G/H 同)")),
        dict(tag="H", pts=BH, spec=ins + "  同详图 G (控制板)", where=xy(BH)),
    ],
    dets=[dict(tag="J", kind="blind", D=12.0, h=3.0, side="top", z=ZD, pt=(0.0, 0.0), ang=0.0, W=9.0, title="盘心 Φ12×3 盲窝 (顶面)"),
          dict(tag="K", kind="free", z=ZD, pt=(_rp.X(), _rp.Y()), ang=0.0, W=6.0, title="控制板背面让位槽 ×3 (顶面)",
               zd=[(-3.0, 0.0, "3")])],
    notes=["散热片通槽 20×40 (零间隙, 散热片 40×20×6 鳍朝下)",
           "控制板背面让位 3 处, 顶面深 3 (详图 K; XT60/MR30 焊点 + 排针)",
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
    dets=[dict(tag="C", kind="free", z=(0, B.TUBE_TOP), pt=(0.0, -34.0), ang=270.0, W=6.5,
               title=f"-Y 出线口 {F(B.WIRE_A0)}–{F(B.WIRE_A0 + 30)}° 处 (r34 中心)",
               zd=[(0, B.FL_Z0 + 2.7, F(B.FL_Z0 + 2.7), 0), (B.FL_Z0 + 2.7, B.TUBE_TOP, F(B.TUBE_TOP - B.FL_Z0 - 2.7), 8)],
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
             where=ring_txt(B.LID_SCREWS) + "  上下盖互锁 M3×5",
             det=dict(kind="ins", d=3.2, D=B.LID_INS_D, h=B.LID_INS_H, side="bot", z=(B.FL_Z0, B.FL_TOP), pt=B.LID_SCREWS[0], title="外圈 M3 铜螺母孔")),
    ],
    notes=[f"Z{F(B.FL_Z0)}→{F(B.FL_TOP)}, 原 V0.4 底板 4.5 → {F(4.5 - B.FL_THIN)}; 线圈腔 r{F(B.CAV_R0)}–{F(B.CAV_R1)} 底 Z{F(B.CAV_Z0)}",
           f"内墙 r31.7–{F(B.CAV_R0)} / 外墙 r{F(B.CAV_R1)}–82.5 都是 {F(B.CB7)} 宽 (= 安装法兰 Φ{F(B.CB7)} 沉孔), 螺丝居中",
           "+X 处 XT60 压块让位缺口; 原 +X 线圈引线槽 (r40–61) 减薄后变通槽 (待定)"],
))

# ---------------- mounting_flange_v1_2 ----------------
SPECS.append(dict(
    code="mounting_flange_v1_2", shape=B.mounting_flange, short="安装法兰 (无线供电上盖)", qty="1",
    title=f"安装法兰 Φ170: V0.4 件外裙短 {F(B.FL_THIN)}, 板顶减 {F(B.MF_THIN)}, 中心孔 Φ{F(2 * B.MF_HOLE_R)}",
    subtitle=f"外裙 r82.5–85 包住定子盘外缘, 底到 Z{F(B.FL_Z0)} = 定子盘底",
    orient="翻面打印 (板顶朝下)",
    phi=[2 * B.MF_HOLE_R, 2 * B.R_SCREW, 2 * 78.0, 165.0, 170.0],
    sec=dict(ang=22.5, zd=[(B.FL_Z0, B.FL_TOP), (B.FL_TOP, B.MF_TOP), (B.FL_Z0, B.MF_TOP)]),
    holes=[
        dict(tag="A", pts=B.FLANGE_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔", where=ring_txt(B.FLANGE_SCREWS) + "  M3×20",
             det=dict(kind="cb", d=3.2, D=7.0, h=B.MF_CB, side="top", z=(B.FL_TOP, B.MF_TOP), pt=B.FLANGE_SCREWS[0], title="M3 沉孔 (A/B 同)")),
        dict(tag="B", pts=B.LID_SCREWS, spec=f"Φ3.2 通 + 顶面 Φ7×{F(B.MF_CB)} 沉孔  同详图 A", where=ring_txt(B.LID_SCREWS) + "  M3×5 锁定子盘 B"),
    ],
    dets=[dict(tag="D", kind="free", z=(B.FL_Z0, B.MF_TOP), pt=(83.75 * math.cos(math.radians(22.5)), 83.75 * math.sin(math.radians(22.5))), ang=22.5, W=5.0,
               title="外裙 r82.5–85 (中心 r83.75)", zd=[(B.FL_Z0, B.FL_TOP, F(B.FL_TOP - B.FL_Z0), 0), (B.FL_TOP, B.MF_TOP, F(B.MF_TOP - B.FL_TOP), 0)], ud=[(-1.25, 1.25, "2.5")])],
    notes=["外裙 = V0.4 原件, 同步短到定子盘底 (11-12 修: 上一版误切, 留 0.3 薄片)", "外圈 B 孔 r79 居中于定子盘外墙 (原 V0.4 r77.5 已补实)",
           f"中心孔 Φ{F(2 * B.MF_HOLE_R)}: 线圈环内管 Φ{F(B.TUBE_OD)} 穿过, 顶齐 Z{F(B.MF_TOP)}"],
))

# ---------------- 玻璃罩下罩三件 ----------------
sup = B.OUT_SCREWS
gl_notes = [f"玻璃 OD{F(B.GL_OD)}×{F(B.GL_T)} H{F(B.GL_H)} 坐 Z{F(B.Z_G)} (= 承载盘顶), 单边间隙 {F(B.GL_CLR)}",
            f"墙 r{F(B.SPIG_IN)}–{F(B.SH_OUT)} Z0→{F(B.Z_G)}; 内卡 r{F(B.gi - B.SPIG_T)}–{F(B.gi)} 深 {F(B.IN_DEPTH)}; A 孔心到墙内面 {F(B.SPIG_IN - B.SH_R)}",
            f"三角块厚 {F(B.TRI_T)} (十字 ±{F(B.P_N)} 外); 墙内面 = 内卡内面 r{F(B.SPIG_IN)} 直下; 无托块",
            f"+X XT60 开口 = 压块 +0.2; M6 螺母井 Φ14 Z{F(B.XT_H)}→{F(B.XT_H + 6.5)}"]
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
    code="glass_shroud_split_v1_2", shape=B.shroud_split, short="玻璃罩下罩 (分体)", qty="1 (配外卡环)",
    title="玻璃罩下罩 (分体版, 顶面开凸筋槽)", orient="底面 (Z0) 贴床",
    phi=[2 * B.SH_R, 2 * B.SPIG_IN, 2 * B.gi, 2 * B.SH_OUT],
    sec=dict(ang=45, r0=70.0, zd=sh_zd[:2] + [(B.Z_G - B.TG_H - B.TG_CLR, B.Z_G), (B.Z_G, B.Z_G + B.IN_DEPTH)],
             rd=[sh_rd[0], sh_rd[1], (B.TG_R0 - B.TG_CLR, B.TG_R0 + B.TG_W + B.TG_CLR)]), holes=sh_holes,
    notes=gl_notes + [f"顶面槽 r{F(B.TG_R0 - B.TG_CLR)}–{F(B.TG_R0 + B.TG_W + B.TG_CLR)} 深 {F(B.TG_H + B.TG_CLR)} (配外卡环凸筋, 单边 {F(B.TG_CLR)})"]))
SPECS.append(dict(
    code="glass_clamp_ring_v1_2", shape=B.clamp_ring, short="外卡环 (分体)", qty="1",
    title=f"外卡环: r{F(B.go)}–{F(B.SH_OUT)} 斜顶 + 底凸筋 {F(B.TG_W)}×{F(B.TG_H)}", orient="凸筋朝上, 斜顶朝下需支撑 (或按切片软件)",
    phi=[2 * B.go, 2 * B.TG_R0, 2 * (B.TG_R0 + B.TG_W), 2 * B.SH_OUT],
    sec=dict(ang=0, r0=96.0, zd=[(B.Z_G - B.TG_H, B.Z_G), (B.Z_G, B.Z_G + B.OUT_DEPTH), (B.Z_G, B.Z_G + B.LIP_EDGE, f"{F(B.LIP_EDGE)} (外缘直边)")],
             rd=[(B.go, B.SH_OUT), (B.TG_R0, B.TG_R0 + B.TG_W)]),
    holes=[],
    notes=[f"内面 r{F(B.go)} 贴玻璃外壁 (单边间隙 {F(B.GL_CLR)})",
           f"底凸筋 r{F(B.TG_R0)}–{F(B.TG_R0 + B.TG_W)} 高 {F(B.TG_H)} 插下罩顶槽", "装配: 玻璃先套内卡, 再从上套环"]))

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
