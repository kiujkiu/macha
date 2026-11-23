"""POV3D V1.2 结构: V1.0 基础上换电机 Φ55x21.5 + 打印底盘 Φ220 + 柱回 V0.4 柱位 + 承载盘外唇 Φ170 (11-14, 原 Φ178); 11-16 晚 方案 A: 屏幕偏心 SCR_ECC + 取消中间 T 件 (转子曾改 Φ175, 同晚用户改回 Φ170, 其余改动保留)."""
import sys, os, math, json
from pathlib import Path
from helpers import read_step, write_doc, bbox, solids
from OCP.gp import gp_Trsf, gp_Ax1, gp_Ax2, gp_Pnt, gp_Dir, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepMesh import BRepMesh_IncrementalMesh

HERE = Path(__file__).resolve().parent
V12 = HERE.parent
SRC = V12 / 'src'                      # 依赖的 V1.0/V0.4/V1.1 源 STEP (已拷进来)
C10 = O10 = SRC
OLDPARTS = os.environ.get('OLDPARTS')  # 可选: 全套旧件目录, 不设就只出 V1.2 件
OUT = V12 / 'out'; (OUT / '零件').mkdir(parents=True, exist_ok=True); (OUT / '打印STL').mkdir(exist_ok=True)
# 11-18 用户「开工, 整机换成转子盘B」: 整机装配/校核/紧固件/出图默认用转子盘B (rotor_b_v1_2: 玻纤板 + 承载盘单件 + 屏幕固定件 ×2,
#   rotor_shroud_b_v1_2: 罩子 2 片); 旧转子 (hub_disc + rim_ring_D170 + 立板 led_post + 罩子 4 件) 仍在本文件里建, 只是不再进整机。
#   环境变量 V12_ROTOR=A 切回旧转子 (对比用)。
ROTOR_B = os.environ.get('V12_ROTOR', 'B').upper() != 'A'

def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def cyl(x, y, d, z0, z1, ang=None, a0=0):
    ax = gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1))
    if ang is None: return BRepPrimAPI_MakeCylinder(ax, d / 2, z1 - z0).Shape()
    ax = gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1), gp_Dir(math.cos(math.radians(a0)), math.sin(math.radians(a0)), 0))
    return BRepPrimAPI_MakeCylinder(ax, d / 2, z1 - z0, math.radians(ang)).Shape()
def op(cls, a, b):
    o = cls(a, b); o.Build(); assert o.IsDone(); return o.Shape()
cut = lambda a, *bs: [a := op(BRepAlgoAPI_Cut, a, b) for b in bs][-1]
fuse = lambda a, *bs: [a := op(BRepAlgoAPI_Fuse, a, b) for b in bs][-1]
def clean(s):
    u = ShapeUpgrade_UnifySameDomain(s, True, True, True); u.Build(); return u.Shape()
def xf(s, t): return BRepBuilderAPI_Transform(s, t, True).Shape()
def rotz(deg):
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(deg)); return t
def one(p): return read_step(p)

LOG = {}
# ---------------- 尺寸 ----------------
MOTOR_D, MOTOR_H = 55.0, 21.5
BOSS_D, BOSS_H = 5.0, 3.2
ROTOR_TOP = 31.7                       # hub_disc 底面 = 电机顶面, 不变
MOTOR_Z0 = ROTOR_TOP - MOTOR_H        # 10.2 (原 5.0)
BORE_D = 59.0                          # 电机座内孔 (原 55), 径向余 2
STATOR_R = 46 / 2; ROTOR_R = 16 / 2   # 对角/2
POCKET_D, POCKET_H = 6.2, 3.5          # 毂盘中心窝 (原 Φ6.2x2.2)
RIM_D = 170.0                          # 承载盘外唇: 11-16 晚 用户改回 Φ170 (同晚曾改 Φ175; 11-14 改回 V0.4 Φ170; V1.0 原 180, V1.2 曾 178)
SCR_ECC = -4.69                        # 11-18 夜 用户: 灯板间距 5 / 板厚 1.6 ⇒ −(2.5+1.6+MIP 0.59) = −4.69 (原 −4.36 = 间隙 4.6 / 板 1.468); 11-16 晚 用户: 整组灯板沿 y 平移 (同 V0.4/V1.0 偏心), 板 A MIP LED 顶面落在转轴 y=0; 各脚本都读 B.SCR_ECC
DISC_D = 220.0
# 用户 11-18: 底座 = 3 mm 玻纤板 (FR4, 顶 Z0) + 打印底盘 4.5 (Z-7.5..-3), 上面所有件 Z 不变。
#   建模时仍按一整块 Z-7.5..0 的 disc 造 (底面沉孔/铜螺母孔相对底面, 顶面槽相对 Z0), 最后拆成 disc_print + fr4。
FR4_T, PRINT_T = 3.0, 4.5
DISC_T = FR4_T + PRINT_T                # 7.5 (原一体底盘 6)
M6_D, CB_D, CB_H = 6.4, 13.0, 3.0
COLLAR_M6 = [(sx * 37.5, sy * 37.5) for sx in (1, -1) for sy in (1, -1)]
POSTS = [(87.5, 37.5), (-37.5, 87.5), (-87.5, -37.5), (37.5, -87.5)]   # V0.4 柱位 R95.197
POST_D, POST_H = 8.0, 360.0
D_ANG = math.degrees(math.atan2(37.5, 87.5) - math.atan2(62.5, 87.5))  # -12.339 轴承架/滑片转角
s45 = math.sqrt(0.5)

# ---------------- 1 方案 C (用户 11-10): 电机直接坐底盘 z0, 电机以上整体降 DROP; 线圈环单独一件 ----------------
DROP = 10.2
MOTOR_Z0 = 0.0
ROTOR_TOP = MOTOR_Z0 + MOTOR_H                 # 21.5 (原 31.7)
FL_THIN = 2.0                                  # 用户 11-11: flange_disc 底板减 3 (4.5→1.5), 顶面不动, 底面上抬; 11-12 夜: 加厚 1 (1.5→2.5) ⇒ 减 2, 总高 16 不变
FL_UP = 1.2                                    # 用户 11-11 上移 1; 11-12 再 +0.2: 内管顶 = 安装法兰顶 = 总高 16 (方座顶 = FL_Z0 8.5, 11-12 夜)
FL_Z0 = 15.5 + FL_THIN - DROP + FL_UP          # 法兰盘底 8.5 (11-12 夜, 原 9.5)
MF_THIN = 0.5                                  # 用户 11-11: mounting_flange 板厚 3→2.5 (顶面去 0.5)
MF_CB = 1.5                                    # 用户 11-11: 安装法兰 16 个 Φ7 沉孔深 2.0→1.5
FL_TOP = 22.5 - DROP + FL_UP                   # 法兰盘顶 13.5 (= 安装法兰底)
MF_TOP = 25.5 - MF_THIN - DROP + FL_UP         # 安装法兰顶 16.0
# 11-23 光电对射发射板 (定子侧, 发射管朝上; 接收管在转子盘B 朝下, 转子通光孔 Φ3.4 @ r77.5)。
#   11-23 用户纠正: 板放在定子盘**底面** (Z FL_Z0 一侧) —— 双面板, 顶面 0603 发射管朝上, 底面 0603 10k + 2 个焊线焊盘 (24V/GND, 不要接插件);
#   板顶面 (LED 面) 平贴定子盘底面, LED 伸进定子盘通光孔 (贯穿) → 安装法兰同轴通光窗 → 气隙 → 转子孔。
#   压片 ir_clamp_v1_2 (打印): 沿 r77.5 的弧形条, 用离板最近的 2 颗外圈 B 螺丝 (M3, 盘底下挂法兰螺母) 夹在定子盘底面与法兰螺母之间, 顶面开板槽托住板。
#   11-23 用户: 板加 2 个 NPTH 定位孔 (对角拉开), 压片上 2 个销插进去定位。
#   板局部坐标 (u, v): u = 切向 (逆时针为正) 从板低角端起, v = 径向 (向外为正) 从板内侧边起; LED 中心 (IR_LED_UV) 落在 r IR_R @ IR_ANG。改板只动这里。
IR_ANG, IR_R = 45.0, 77.5                      # LED 中心角度/半径 (r 必须 = 转子通光孔半径 77.5); 11-23 用户: 放 B 孔 22.5/67.5° 正中 ⇒ 压片外形关于 45° 对称 (原 53°)
IR_PCB_L, IR_PCB_W, IR_PCB_T = 10.0, 10.0, 0.8 # 发射小板 FR4: 切向 L × 径向 W × 厚。11-23 r5 通用板 10×10 (需求_r5_通用板10x10, 用户「因为生产原因」): r4 第 3 版 10×5 往轴心加长 5, 上半部相对结构不动; 板 a (u 切向) × b (v 径向, b0 朝轴心), r = 69.1 + b ⇒ 板 r69.1–79.1, 关于 IR_ANG 对称; 内段 r69.1–75.95 伸在压片内边外 (贴定子盘底, 不另压)
IR_FP = (2.5, 0.95)                            # 0603 焊盘外包 (长 × 宽, LED 与电阻同), 排布校核用
IR_LED_UV = (5.0, 8.4)                         # A 面 0603 发射管 D1 中心 (板 a5.0 b8.4, 长轴沿 b = v 径向)
IR_R_UV = (5.0, 8.4)                           # B 面 0603 10k R1 中心 (长轴沿 v 径向, 在 LED 正背面)
IR_FP_ALONG_U = False                          # 0603 长轴沿 v (径向); r4 第 2 版曾沿 u
IR_PADS_UV = [(3.5, 5.8), (6.5, 5.8)]          # 金属化焊线焊盘 Φ IR_PAD_D: P1 (a3.5 b5.8) = 24V / P3 (a6.5 b5.8) = GND (P2 a5.0 = N 发射板不接); r74.9 真实外缘 r75.415, 露在压片内边 IR_CL_R0 外 ≥0.5
IR_PAD_D = 1.0
IR_HOLES_UV = [(2.0, 8.2), (8.0, 8.2), (2.0, 2.5), (8.0, 2.5)]   # NPTH 定位孔 Φ2.2 (M2 通孔): H1/H2 r77.3 ∓3.0 (压片销插这 2 个); H3/H4 r71.6 ∓3.0 (r5 新增, 在压片内边外, 定子侧不用)
IR_PIN_HOLES = IR_HOLES_UV[:2]                  # 压片定位销只对 H1/H2
IR_HOLE_D = 2.2                                # 板定位孔 NPTH (r4 第 3 版用户定 M2 通孔; 原 1.5, 曾议 Φ3.4)
IR_PIN_D = 2.0                                 # 压片定位销 (r4 第 3 版 M2 孔配 Φ2.0; 原 1.3) ⇒ 销内缘 r76.3, 离压片内边 0.4
IR_PIN_H = IR_PCB_T - 0.1                      # 销高 (从板底面平面起) 0.7, 不顶定子盘
IR_LED_U = IR_LED_UV[0]                        # (兼容旧名)
IR_LED_L, IR_LED_W, IR_LED_H = 1.6, 0.8, 0.6   # 0603 发射管本体 (L 沿 IR_FP_ALONG_U 定的轴; 伸进定子盘通光孔, 对角 1.79 < IR_WIN_D)
IR_BOT_H = 0.45                                # 底面 0603 电阻高
IR_BOT_GAP = 0.2                               # 电阻底到压片槽底余量
IR_REL_M = 0.2                                 # 电阻让位槽比焊盘外包单边大
IR_LEDGE = 0.0                                 # (已废弃; 留给旧引用)
IR_CLR = 0.2                                   # 压片板槽比板单边大
IR_WIN_D = 3.4                                 # 定子盘通光孔 (贯穿 Z FL_Z0..FL_TOP) = 安装法兰通光窗 (同轴); 11-23 用户: 同转子 M3 通孔规格 Φ3.4 (原 3.5)
IR_CL_WALL = 1.2                               # 压片板槽外侧壁
IR_CL_R0 = 75.95                               # 压片弧条内半径 (板从这里伸出去, 焊盘露在外); r4 第 3 版: 焊盘 (切向 ±1.5) 真实外缘 r75.415 + 0.5 ⇒ 75.92, 取 75.95; 销 Φ2.0 内缘 r76.36 离内边 0.41
IR_CL_R1 = IR_R - IR_LED_UV[1] + IR_PCB_W + IR_CLR + IR_CL_WALL      # 外半径 80.5 (r4 第 3 版; 原 80.35)
IR_CL_W = IR_CL_R1 - IR_CL_R0                  # 弧条径向宽 4.55 (r4 第 3 版; 原 6.85)
assert all(math.hypot(IR_R - IR_LED_UV[1] + v, u - IR_LED_UV[0]) + IR_PAD_D / 2 <= IR_CL_R0 - 0.5 for u, v in IR_PADS_UV), '焊盘要露出压片内边 ≥0.5 (按真实半径)'
assert all(math.hypot(IR_R - IR_LED_UV[1] + v, u - IR_LED_UV[0]) - IR_PIN_D / 2 >= IR_CL_R0 + 0.3 for u, v in IR_PIN_HOLES), '定位销要整个落在压片上 (离内边 ≥0.3)'
IR_CL_PAD_D = 9.6                              # 压片螺丝处圆垫 (外缘 r82.3, 不出定子盘 r82.5)
IR_CL_NUT_CB_D = 8.4                           # 圆垫底面法兰螺母沉孔 (法兰 Φ7.6 +0.4), 只留 IR_CL_PAD_T 夹在定子盘底与螺母之间
IR_CL_PAD_T = 0.8                              # 螺母处压片厚 ⇒ 螺母只下移 0.8: Z7.5–11.2 (67.5° 孔正下方控制板器件顶 ~Z5.85)
IR_CL_HOLE_D = 3.4                             # 压片螺丝孔
IR_CL_FLOOR = 1.2                              # 电阻让位槽底厚
IR_CL_T = IR_PCB_T + IR_BOT_H + IR_BOT_GAP + IR_CL_FLOOR   # 压片厚 2.65 (板槽 0.8 + 器件槽 0.65 + 槽底 1.2) ⇒ 底 FL_Z0 − 2.65
IR_CL_SCREW_L = 10.0                           # 压片处 2 颗 B 螺丝仍 M3×10 (支承 Z18, 尾 Z8.0, 吃螺母 3.2/3.7); M3×12 尾 Z6 离 67.5° 下方控制板器件只 0.15, 不可用
TUBE_TOP = MF_TOP                              # 用户 11-12: 内管穿定子盘+安装法兰到 Z16 (6.5); 螺丝 r35.2 的 Φ7 沉孔内缘 r31.7 让开内管 r31.5
CB7 = 7.0                                      # 用户 11-12: 安装法兰 A/B 沉孔 Φ7 = 定子盘内外墙宽
R_SCREW = 31.7 + CB7 / 2                       # 用户 11-12: r34 → r35.2 (Φ7 沉孔从中心孔边 r31.7 起; 原 11-11 r36.3 → r34)
TUBE_OD = 63.0                                 # 内管 r29.5–31.5 (壁 2)
COLLAR_D = 77.0                                # 套环 Φ84 → Φ77 (r38.5), 控制板跟着内移
FL_HOLE_R = TUBE_OD / 2 + 0.2                  # 法兰盘中心孔补到 r31.7
MF_HOLE_R = TUBE_OD / 2 + 0.2                  # 用户 11-12: 内管要穿安装法兰 ⇒ 中心孔 r29.7 → r31.7 (同定子盘)
BOARD_ANG = 90.0
COLLAR_M6 = []
FLANGE_SCREWS = [(R_SCREW * math.cos(math.radians(22.5 + 45 * k)), R_SCREW * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
COLLAR_FLAT = 35.5                                 # 用户 11-11: 套环四边削平到 ±35.5 (控制板可往里挪 3)
RING_CH = 5.0                                      # 用户 11-12: 套环改方座 ±35.5 (四角倒角 5), 四角 4×M3 先把线圈环锁在底盘上 (装定子盘之前)
RING_M3_XY = 29.5
RING_M3 = [(sx * RING_M3_XY, sy * RING_M3_XY) for sx in (1, -1) for sy in (1, -1)]
RING_CORNER_T = 4.5                                # 用户 11-12: Φ77 圆 (托定子盘) 以外的四角只留 5 厚; 11-12 夜: 定子盘底降到 8.5 ⇒ 4.5 (法兰螺母 4.5..8.2, 离定子盘底 0.3)
# 用户 11-12: 四角只开 Φ3.2 通孔 (不压铜螺母); M3x12 从盘底沉孔往上 (支承面 z-4, 尾 z8.0, 离定子盘底 8.5 留 0.5; 11-12 夜), 四角顶面 (z4.5) 放 M3 法兰螺母
def _octa(h, c, z0, z1):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    pts = [(h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c), (-h + c, -h)]
    pg = BRepBuilderAPI_MakePolygon()
    for x, y in pts: pg.Add(gp_Pnt(x, y, z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()
r_ = fuse(cut(_octa(COLLAR_FLAT, RING_CH, 0, FL_Z0), cyl(0, 0, BORE_D, -1, FL_Z0 + 1)),        # 托法兰盘的方座 ±35.5 / 内孔 Φ59
          cut(cyl(0, 0, TUBE_OD, FL_Z0, TUBE_TOP), cyl(0, 0, BORE_D, FL_Z0 - 1, TUBE_TOP + 1)))   # 内管 Φ63 (穿法兰盘孔)
WIRE_A0, WIRE_AW, WIRE_ZH = 268.0, 24.0, 7.5      # 11-20 晚起 WIRE_A0/AW 已废弃 (出线口改直边槽, 见下 WIRE_XL…), 只留给角耳判断/旧引用; 11-20 用户「265°–287°改成268-292 高度从6改到7.5」; 11-19 23:0x 用户「开口高度5mm」(原 6); 292.5° 中央螺丝孔 (13.47,−32.52) 原要求四周实体 ⇒ 终边 ≤287 (孔壁 1.8) —— 11-20 用户改 292, 已知切开 292.5° 螺丝孔 Z0–7.5 下段; 11-19 22:5x 用户「265到287」(先说 265–300 随即改口; 原 270–310); 用户 11-13: 电机出线口 270–310° (宽 40, 对准实物出线 ~285–290°), 高 6 (底面 Z0 起); 原 255–285° 高到 Z11.2
r_ = cut(r_, cut(_octa(COLLAR_FLAT + 1, RING_CH, RING_CORNER_T, FL_Z0 + 1), cyl(0, 0, COLLAR_D, RING_CORNER_T - 1, FL_Z0 + 2)))  # 圆外四角削到 RING_CORNER_T (4.5) 厚
# 11-20 用户「啊不是这个意思，就是这个圈以外的，你多去掉一点，不是从扇形区域去掉」+「这样」(画图): 出线口不再用扇形, 改两条竖直 (平行 y) 边的直槽 Z−1→WIRE_ZH, 从内孔切出方座 −y 平边;
#   左边 x=WIRE_XL; 右边 x=孔心x−WIRE_RING_D/2 (与 292.5° A 孔外 Φ5.2 圈相切), 孔心高度以下再往右切到孔心 x; 减去 Φ5.2 圈 ⇒ 孔外留 1.0 壁小圈, 圈左/左下挖空, 圈右侧原实体保留
WIRE_XL, WIRE_RING_D = -1.5, 5.2
WIRE_HX, WIRE_HY = FLANGE_SCREWS[6]                 # 292.5° 中央 A 孔 (13.47, −32.52)
WIRE_XR = WIRE_HX - WIRE_RING_D / 2                 # 10.87
_wb = lambda x0, y0, z0, x1, y1, z1: GC.tag(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape(), "box", x0, y0, z0, x1, y1, z1)
_wc = fuse(_wb(WIRE_XL, -COLLAR_D / 2 - 5, -1, WIRE_XR, 0, WIRE_ZH),
           _wb(WIRE_XR - 0.01, -COLLAR_D / 2 - 5, -1, WIRE_HX, WIRE_HY, WIRE_ZH))
r_ = cut(r_, cut(_wc, cyl(WIRE_HX, WIRE_HY, WIRE_RING_D, -2, WIRE_ZH + 1)))
# 用户 11-13: 出线口边 (310° 射线) 切过 315° 角耳, 在底边留一个尖三角 ⇒ 角耳出线口一侧 (310–315°) 修成绕螺丝孔的圆 R4.3 (法兰螺母 Φ7.6 + 0.5)
_ca = math.radians(round((WIRE_A0 + WIRE_AW - 45) / 90) * 90 + 45)            # 出线口末端相邻的角 (315°)
_cx, _cy = RING_M3_XY * math.sqrt(2) * math.cos(_ca), RING_M3_XY * math.sqrt(2) * math.sin(_ca)
# 11-19: 只有出线口终边伸进角耳 (角耳起点 = Φ77 圆与 ±35.5 平边交点, 距轴 acos(35.5/38.5)=22.8°) 才修; 265–287 终边 17° < 22.8° 不碰角耳, 不修
_EAR_A = math.degrees(math.acos(COLLAR_FLAT / (COLLAR_D / 2)))
if (WIRE_A0 + WIRE_AW) % 90 > _EAR_A:
  r_ = cut(r_, cut(cut(cyl(0, 0, 120, -1, RING_CORNER_T + 0.01, ang=math.degrees(_ca) - WIRE_A0, a0=WIRE_A0), cyl(0, 0, COLLAR_D, -2, RING_CORNER_T + 1)),
                 cyl(_cx, _cy, 8.6, -2, RING_CORNER_T + 1)))
for x, y in FLANGE_SCREWS:
    r_ = cut(r_, cyl(x, y, 3.2, -1, TUBE_TOP + 1))
for x, y in RING_M3:
    r_ = cut(r_, cyl(x, y, 3.2, -1, FL_Z0 + 1))
RING_NUT_CLR_D = 8.2  # 用户 11-12 方案 a: 圆台四角让 M3 法兰螺母 Φ7.6 (+0.3 单边)
for x, y in RING_M3:
    r_ = cut(r_, cyl(x, y, RING_NUT_CLR_D, RING_CORNER_T, FL_Z0 + 1))
ring = clean(r_); collar = ring; LOG['ring'] = dict(v=vol(ring))
def zdown(sh, dz=DROP):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(0, 0, -dz)); return xf(sh, t)
# 法兰盘 / 安装法兰: 原 V0.4 件在原坐标 z<15.5+FL_THIN 的部分切掉 (底板减薄, 外裙同步缩短), 再整体降 DROP
_low = cyl(0, 0, 400, -100, 15.5 + FL_THIN)
_OLD_SCREWS = [(36.3 * math.cos(math.radians(22.5 + 45 * k)), 36.3 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
_fd = cut(one(C10 / 'flange_disc_v4.step'), _low)
_fd = fuse(_fd, cut(cyl(0, 0, 78.0, 15.5 + FL_THIN, 22.5), cyl(0, 0, FL_HOLE_R * 2, 0, 30)))   # 内墙 r≤39 补满到 r31.7 (旧孔一并补上; 不取 r40 免与线圈腔壁重合)
for x, y in FLANGE_SCREWS: _fd = cut(_fd, cyl(x, y, 3.2, 0, 30))
flange_disc = zdown(clean(_fd), DROP - FL_UP)
def _cb_xy(sh, d=7.0):
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder
    from OCP.TopoDS import TopoDS
    e = TopExp_Explorer(sh, TopAbs_FACE); out = []
    while e.More():
        a = BRepAdaptor_Surface(TopoDS.Face(e.Current()))
        if a.GetType() == GeomAbs_Cylinder and abs(a.Cylinder().Radius() * 2 - d) < 0.05:
            p = a.Cylinder().Location(); xy = (round(p.X(), 3), round(p.Y(), 3))
            if xy not in out: out.append(xy)
        e.Next()
    return out
_mf0 = one(C10 / 'mounting_flange_v4.step')
_mf_top = 25.5 - MF_THIN
MF_THIN_LOW = FL_THIN                         # 11-16 晚 用户: 外裙 4 → 5, 底齐定子盘底 Z8.5 (从外面看定子盘是完整环形盘); 原 3.0 (底 Z9.5)
_mf = cut(_mf0, cyl(0, 0, 400, -100, 15.5 + MF_THIN_LOW), cyl(0, 0, 400, _mf_top, 100))
_cbs = _cb_xy(_mf0); assert len(_cbs) == 16, _cbs
_cbs_out = [c for c in _cbs if math.hypot(*c) > 50]; assert len(_cbs_out) == 8   # 外圈 8 个原样
_CB0 = 23.5                                   # V0.4 原件 Φ7 沉孔底 (原坐标)
if _mf_top - MF_CB < _CB0 - 1e-6:              # 只在要加深时切 (同轴同径重叠切会把实体切坏)
    for x, y in _cbs_out: _mf = cut(_mf, cyl(x, y, 7.0, _mf_top - MF_CB, _CB0 + 0.3))
_mf = fuse(_mf, cut(cyl(0, 0, 81.0, 22.5, _mf_top), cyl(0, 0, MF_HOLE_R * 2, 0, 40)))   # 内圈 r≤40.5 补满到 r29.7 (旧 8 孔补上)
for x, y in FLANGE_SCREWS:
    _mf = cut(_mf, cyl(x, y, 3.2, 0, 40), cyl(x, y, 7.0, _mf_top - MF_CB, 40))
assert _mf_top - MF_CB <= _CB0 + 1e-6, '沉孔要比原件浅, 需补料, 未实现'
mounting_flange = zdown(clean(_mf), DROP - FL_UP)
LOG['flange'] = dict(fd=vol(flange_disc), mf=vol(mounting_flange))

# ---------------- 2 转子毂盘 ----------------
h0 = one(C10 / 'hub_disc_v1_0.step'); v0 = vol(h0)
old = [(6, 0), (-6, 0), (0, 7.5), (0, -7.5)]
h = fuse(h0, *[cyl(x, y, 7.2, 36.7, 40.7) for x, y in old], *[cyl(x, y, 3.4, 31.7, 36.7) for x, y in old])
v_fill = vol(h) - v0
h = cut(h, cyl(0, 0, POCKET_D, 31.7 - 1, 31.7 + POCKET_H))
for sx in (1, -1):
    for sy in (1, -1):
        x, y = sx * ROTOR_R * s45, sy * ROTOR_R * s45
        h = cut(h, cyl(x, y, 3.2, 31.7 - 1, 36.7), cyl(x, y, 7.0, 36.7, 41.0))
hub = zdown(clean(h))
# 11-16 晚 用户: 转子盘和定子盘同半径 ⇒ 毂盘外圆 r87.5 → r85 (= 承载盘 r85 = 安装法兰 r85 = 转子罩外圆), 转子外面一整个 Φ170 圆柱
hub = clean(op(BRepAlgoAPI_Common, hub, cyl(0, 0, 2 * 82.4, -100, 200)))   # 11-16 晚 再改: 毂盘 r82.4 嵌进承载盘裙边 r82.5 (同定子: 定子盘 r82.5 嵌安装法兰外裙); Φ175 时曾 r84.9, 已改回
import math as m
v_old_holes = 4 * (m.pi * 1.6**2 * 5 + m.pi * 3.5**2 * 4)
LOG['hub'] = dict(v0=v0, v=vol(hub), fill=v_fill, old_holes_expected=v_old_holes)

# ---------------- 3 承载盘 ----------------
r0 = one(C10 / 'rim_ring_v1_0.step'); v0 = vol(r0)
rim = zdown(clean(op(BRepAlgoAPI_Common, r0, cyl(0, 0, RIM_D, 25, 50)))); LOG['rim'] = dict(v0=v0, v=vol(rim))
# 11-16 用户改转子布局: 灯板下沿离盘 5; 转接板 r2 在 +y 侧 (pov3d-96), 无线供电模块独立在 −y 侧; 以下承载盘顶面孔表各归一个脚本管:
_rim_pre = rim
#   灯板两端支撑: 11-16 改 T 形脚用承载盘原有 R82.5 孔 (22.5/157.5/202.5/337.5°), 原 (±78,±7.6) 四孔作废 ⇒ 不再切
LS_FOOT_PTS = []
#   中间 T 件 ×2 (led_support_v1_2, 11-16 晚 用户: 灯板下端沿用 V0.4 ⇒ 夹条 + T 件竖直螺丝; 原门形 (±30,0) 作废):
#   每件 2×M3 进承载盘铜螺母 (Φ4.2×4.2), 脚孔在灯板/桥板外 (|y|10) 从上面够得着
#   11-16 晚 用户: 中间 T 件取消 ⇒ 原 (±38, ±10) 4 孔不再切; 名字留着置空 (led_support / fasteners / build_drawings 还在 import)
GATE_PTS = []
# 11-16 晚 pov3d-96 底板 r3 rev b (layout/r3_pads, 两 FPC 座一内一外, CZ06 夹中间): 4×M3 → 承载盘顶面 Φ4.2×4.0 浅孔 (H5/H7/H6/H8; 线圈腔 r34–76 上盘只剩 4.5 厚)
#   11-16 晚 改回 Φ170: 底板换 r4c (96 出, 板角 r81.69 进罩内壁 r82), 孔 H5/H6/H7/H8
#   (原 r3 rev d: (-46,17.8) (18.1,27.55) (±24.25,69.9); r4b: (-47.6,12.6) (-25,61.5) (43.5,53) (25,61.5))
#   11-16 晚 用户: 孔相对底板自身对称, 放板四角附近, 矩形 90.1×49.6 以板中心 (−1.95, 37.6) 为心 (96 出 r4d 给最终坐标); 板框/STEP 仍 r4c
#   (r4c 原: (-47.4, 60.0) (-24.6, 61.5) (43.5, 53.0) (24.6, 61.5)); (−47, 62.4) 在 r78.1, 尼龙柱六角对角外缘约 r81.3 < 罩内壁 r82
BB_HOLES = [(-46.75, 13.05), (46.75, 13.05), (-46.75, 56.05), (46.75, 56.05)]   # 11-17 晚 r4j (96 8dbcae25): 右两孔 42.85 → 46.75, 关于 x=0 对称; 原 11-17 r4i (96 D213R9): 上板边 66.6→60.5, H6/H8 62.15→56.05 (矩形 89.6×43.0); 原 r4e (96 31676a1a): H5 / H7 / H6 / H8 四角矩形 89.6×49.1, 四边内缩 4.45 (4.7 会压 WiFi/F1/L1)
BB_INS_H = 0.0                                    # 11-16 晚 改一颗螺丝穿到底: 承载盘这 4 孔不再压铜螺母 (留名置 0)
#   11-16 晚 用户再改 (承载盘减薄到 2.5, 盘底 RIM_BOT Z29.5): 一颗 M3 超薄头 (头 Φ7×1.5) 从承载盘底往上穿到底 ——
#   承载盘 Φ3.4 通孔 + 盘底 Φ7.4 沉孔深 1.5 (Z29.5–31, 头支承 Z31) → 尼龙光孔垫柱 Φ6×3 (Z32–35) → 底板 1.6 (Z35–36.6) → 板顶 M3 尼龙螺母 (高 2.4, Z36.6–39.0)
#   M3×8: 尾 Z39.0 = 螺母顶 (伸出 0, 螺母吃满 2.4); M3×10 尾 Z41 伸出 2.0 > 1.5 ⇒ 不用
#   装配顺序: 头在承载盘底面 ⇒ 底板先装到承载盘上, 再把承载盘装到毂盘上 (毂盘在 (42.85, 62.15) r75.5 / (−46.75, 62.15) r77.8 两孔下让位, 见下面毂盘加高段)
#   (原: 承载盘孔压 M3×3 铜螺母, M3×8 尼龙盘头从板顶往下拧, 头支承 Z36.6)
RIM_BOT = 29.5                                    # 11-16 晚 用户: 承载盘盘体 Z27–32 (5 厚) 减到 Z29.5–32 (2.5 厚), 顶面 Z32 不动
BB_STANDOFF_SPEC = '尼龙光孔垫柱 M3 Φ6×3 (内孔 3.2)'
BB_SCREW_SPEC = 'M3×8 超薄头内六角 (头 Φ7×1.5, 从承载盘底往上)'
BB_NUT_SPEC = 'M3 尼龙螺母'
BB_NUT_H = 2.4
BB_CB_D, BB_CB_H = 7.4, 1.5                       # 盘底沉孔 Φ7.4 深 1.5 (超薄头 Φ7×1.5)
BB_SCREW_L, BB_SCREW_HEAD_Z = 8.0, RIM_BOT + BB_CB_H   # 螺丝长 / 头支承面 Z31 (头朝下, 杆朝上)
rim = clean(cut(rim, *[fuse(cyl(x, y, 3.4, 20.0, 33.0), cyl(x, y, BB_CB_D, 20.0, BB_SCREW_HEAD_Z)) for x, y in BB_HOLES]))
#   11-16 晚 用户: 转子罩照 V0.4 缩进坐盘上 (罩壁 r82–85, 外圆 = 盘 Φ170) ⇒ 罩底固定 + 两端 T 脚改承载盘顶面铜螺母 (Φ4.2×4.0, 原 R82.5 毂盘底铜螺母孔不再用)
SHR_ANG = (40.0, 140.0, 220.0, 320.0)               # 11-16 晚 (C 定, 改回 Φ170 + r4c 后 F 复核仍可用): 罩底凸台避开底板 r4c 和立板耳朵 (+y 40/140, −y 220/320 = A 半转 180°); 原 @50/140/230/320
SHR_HOLES = [(79.0 * math.cos(math.radians(a)), 79.0 * math.sin(math.radians(a))) for a in SHR_ANG]   # 罩底 4 孔 r79 (同锁盘螺丝 RH_R; 离 22.5° 耳朵螺丝孔心 10.3)
#   11-16 晚 用户: 两端立板脚改锁外圈锁盘螺丝 (RH_EAR_IDX) ⇒ 原 (±74, ±8.5) 4 孔不再切 (= 填实); 名字留着置空 (led_support 还在 import)
END_T_HOLES = []
rim = clean(cut(rim, *[cyl(x, y, 4.2, 32.0 - 4.0, 33.0) for x, y in SHR_HOLES]))
#   11-16 晚 用户: 转子外圈螺丝和定子同半径 ⇒ 承载盘+毂盘外圈 8 孔从 V1.0 的 R82.5 挪到 r79 @22.5°+45°k (= 定子盘/安装法兰外圈 LID_SCREWS, 上下对齐);
#   8×M3×8 内六角从承载盘顶沉孔往下, 进毂盘底 M3×4 铜螺母 (Z21.5–25.5) —— 两盘锁成一体
RH_R = 79.0                                       # 11-16 晚: r79, 与定子 LID_R 上下对齐
RH_PTS = [(RH_R * math.cos(math.radians(22.5 + 45 * k)), RH_R * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
RH_OLD = [(82.5 * math.cos(math.radians(22.5 + 45 * k)), 82.5 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
#   11-16 晚 用户再改: 8 孔都不做沉孔, 一律 Φ3.4 通孔, 承载盘顶 Z32 平 (原 Φ6×3 沉孔 头支承 Z29, M3×8)
RH_HEAD_Z0 = 32.0                                 # 不在耳朵下的 4 颗: 头底直接压承载盘顶 Z32, 头 Z32–35 (外缘 r79+2.75 = r81.75, 罩内壁 r82 留 0.25)
RH_L = 10.0                                       # M3×10: 尾 Z22.0 (铜螺母 Z21.5–25.5 啮合 3.5, 不出毂盘底 Z21.5); M3×12 尾 Z20 会露 1.5 ⇒ 不用
RH_CB_D, RH_BEAR = 0.0, RH_HEAD_Z0                # 沉孔取消 (RH_CB_D 留名置 0); 头支承 = RH_HEAD_Z0
RH_INS = (21.5, 25.5)                             # 毂盘底 M3×4 铜螺母 (底面齐平压入)
#   11-16 晚 用户: 两端立板脚 (led_support 耳朵) 锁在外圈 k=0,3,4,7 (22.5/157.5/202.5/337.5°) 这 4 颗上 (8 孔都是 Φ3.4 通孔, 盘顶 Z32 平);
#   叠层 (从上往下): 螺丝头支承 = 耳朵顶 (Z_RIM_TOP + 耳朵厚, 由 led_support 定) → 耳朵底贴承载盘顶 RH_EAR_Z0 → 穿承载盘 → 毂盘底铜螺母 RH_INS (Z21.5–25.5)
#   螺丝尾 Z 允许 RH_EAR_TIP_Z (下限 = 毂盘底 Z21.5, 不许露出; 上限 Z23.0 = 啮合 ≥2.5); 推荐尾 Z22.0 (同其余 4 颗 M3×10)
#   ⇒ 标准长度对应耳朵厚: M3×12 ↔ 1.5–3.0, M3×14 ↔ 3.5–5.0, M3×16 ↔ 5.5–7.0 (耳朵厚 = L − 32 + 尾 Z)
RH_EAR_IDX = [0, 3, 4, 7]
RH_EAR_PTS = [RH_PTS[k] for k in RH_EAR_IDX]
RH_STD_IDX = [k for k in range(8) if k not in RH_EAR_IDX]   # [1, 2, 5, 6] = 67.5/112.5/247.5/292.5°: M3×RH_L 头压盘顶
RH_EAR_Z0 = 32.0                                  # 耳朵底 = 承载盘顶
RH_EAR_TIP_Z = (21.5, 23.0)                       # 螺丝尾 Z 可用范围
RH_EAR_TIP_REC = 22.0                             # 推荐尾 Z
def rh_ear_screw_len(ear_t, tip=RH_EAR_TIP_REC): return RH_EAR_Z0 + ear_t - tip   # 耳朵厚 ear_t → 螺丝长 (头支承到尾), 例: 3 厚 → 13 (取 M3×12 尾 Z23 或改耳厚)
#   用户: 转子两盘要像定子一样嵌套 (V0.4/V1.0 原样) ⇒ 承载盘补裙边 r82.5–85 下到毂盘底 Z21.5, 毂盘 r82.4 嵌在里面; 转子外面 = 承载盘一个 Φ170 圆柱
RIM_SKIRT = (82.5, 85.0, 21.5)                    # 11-16 晚 改回 Φ170 (Φ175 时曾 r85–87.5)
rim = clean(fuse(rim, *[cyl(x, y, 4.0, 27.0, 32.0) for x, y in RH_OLD]))                                     # 旧 R82.5 Φ3.6 通孔补实
rim = clean(fuse(rim, cut(cyl(0, 0, 2 * RIM_SKIRT[1], RIM_SKIRT[2], 27.6), cyl(0, 0, 2 * RIM_SKIRT[0], RIM_SKIRT[2] - 1, 28.0))))   # 裙边
rim = clean(cut(rim, *[cyl(x, y, 3.4, 20.0, 33.0) for x, y in RH_PTS]))   # 8 孔全 Φ3.4 通孔, 无沉孔
hub = clean(fuse(hub, op(BRepAlgoAPI_Common, fuse(*[cyl(x, y, 4.6, 21.5, 27.0) for x, y in RH_OLD]), cyl(0, 0, 2 * 82.4, 0, 40))))   # 旧 R82.5 孔残口补实 (不出 r82.4)
hub = clean(cut(hub, *[fuse(cyl(x, y, 3.4, 20.0, 28.0), cyl(x, y, 4.2, 20.0, RH_INS[1])) for x, y in RH_PTS]))
#   无线供电模块固定件 (wireless_holder_v1_2.py, −y 侧): M3 铜螺母孔 (11-16 晚: 罩壁缩到 r82, 托盘整体往 +y 挪 3)
MOD_HOLES = [(28.25, -55.5), (-28.25, -55.5), (28.25, -37.5), (-28.25, -37.5)]   # 11-20 用户「这个组件往中间挪一点，让pcb遮住那2个螺母一半」: 无线组往 +y 挪 5.0 (原 y −60.5/−42.5); 11-19 19:40 无线组往 −y 挪 15 (让开内圈 8 孔中 2 个), 原 y −45.5/−27.5; 11-19 15:46 用户最终: 夹块倒 L (立柱 8 宽放 M3 法兰螺母 + 上沿 3.5), 螺丝在立柱中心 x = 24.25+4 (PCB 贴立柱, 无间隙), y = 模块中心 −36.5 ±9 (用户: 间距 18), y 对齐焊脚行;   # 11-19 15:32 夹块收窄到宽 11, 螺丝心 x 34 → 28.3; 15:30 夹块通孔 + 顶面尼龙防松螺母 (M3×16 超薄头从承载盘底往上);   # 11-19 用户: 两件对称夹块 (直方条), 螺丝放左右 (夹块 x 外侧半边, y 对齐焊脚行), 从承载盘底往上 (同底板 BB_HOLES: 底面 Φ7.4×1.5 + Φ3.4 通, 进夹块底面 M3×4 铜螺母); 整组挪到离灯板组 5.0 (实测最近桥板 B 5.02, 模块 y −51.5…−21); 11-19 上午 (±23, −74.5)/(±23, −34) 及原托盘 [(±11, −76.5), (0, −31)] 作废
rim = clean(cut(rim, *[cyl(x, y, 4.2, 32.0 - 4.2, 33.0) for x, y in MOD_HOLES])) if MOD_HOLES else rim
#   线圈 (腔 r34–76) 两根 AC 引线从承载盘小孔上来, 接无线供电模块 (−y 侧) —— 位置归 wireless_holder_v1_2.py
AC_HOLE_D = 3.5                                   # 11-19 15:00 用户「直径3.5mm」(原 3.0)
AC_HOLES = [(32.6, -25.93), (64.12, -29.9)]   # 11-20 无线组往 +y 挪 5 后夹块盖住内孔 (28.93, −29.96) ⇒ 内孔沿 r41.65 (仍切腔内缘) 由 −46° 转到 −38.5° (离夹块 1.74, 转 7.5°); 11-19 22:15 用户「改到 −25°」⇒ 外孔 r70.75 −25° (离屏幕固定件+x 0.5, 离灯板B 13.6, 离无线组 30.4); 之前 22:05 −20°: 11-19 22:05 用户「外环出线孔改到 −20° 看看」⇒ 外孔 r70.75 (仍切腔外缘) 由 −52.28° 转到 −20°: 离屏幕固定件+x 0.5 (径向, 固定件弧形带在 −45…−15° 都是 0.5), 离灯板B 8.6, −15° 以内碰固定件/灯板B; 11-19 21:21 用户画圈「应该这样」⇒ 内孔沿 r41.65 (仍切腔内缘) 转到 −46° (用户点约 −47.8° r43.5 离无线夹块只剩 0.45, 取 −46 留 ~2.7): 离灯板B 5.25→~17, 离桥板B 0→~14, 离 Q 沉孔 ~10; 21:11 版 (36.07,−20.83) @−30° 作废
AC_HOLES_OLD_1519 = [(38.54, -15.79), (43.29, -55.96)]   # 11-19 用户: Φ3.5, 线圈腔正上方, AC 侧夹块外侧; 「内外都改3.5，都做相接」⇒ 内孔边切腔内缘 (r 39.9+1.75 = 41.65 @−22.28°), 外孔边切腔外缘 (r 72.5−1.75 = 70.75 @−52.28°, 从下往上看在内孔逆时针 30°: 原 −42.3° 处离屏幕固定件弧形带只剩 0.5, 转到带外 −44° 以外取离屏幕件最远)
rim = clean(cut(rim, *[cyl(x, y, AC_HOLE_D, 20.0, 33.0) for x, y in AC_HOLES]))
# 11-16 晚 用户: 承载盘减薄 —— 盘体 Z27–32 → RIM_BOT Z29.5–32 (2.5 厚), 顶面 Z32 不动; 毂盘两圈接触面跟着加高 Z27 → Z29.5 (原设计贴合, 间隙 0 照旧)
#   实测原叠层: 承载盘 r25–82.5 Z27–32, 下凸台 r35–40 Z24.5–27 (坐毂盘 r35–40 Z24.5 台阶上, 定位), 裙边 r82.5–85 Z21.5–32;
#              毂盘 r<25 Z21.5–30.5 (中心凸台伸进承载盘 Φ50 内孔), r25–35 / r77.5–82.4 顶 Z27 (与承载盘底贴合), r35–77.5 顶 Z24.5 (线圈腔)
#   ⇒ 承载盘切 r25–82.5 Z27–29.5 环, 留下凸台 r35–40 (Z24.5–29.5 与盘体连成一体) 和裙边; 毂盘 r25–35 / r77.5–82.4 加高到 Z29.5
#   螺丝叠层总高不变: r79 外圈 8 颗 (盘顶 Z32 → 毂盘底铜螺母 Z21.5–25.5) 和 r30 锁盘 8 颗 (V1.0 原有, 毂盘底 Φ4.2 铜螺母 Z21.5–26) 长度都不变
RIM_BORE_R, RIM_BUMP_R = 25.0, (35.0, 40.0)        # 承载盘内孔 / 下凸台 (V1.0 STEP 原有; 11-17 下凸台取消, 见下)
# 11-17 用户: ① 无线线圈内径 80, 原定子内墙 Φ77.4 / 转子毂盘 Φ70 (Φ80 那圈长在承载盘底) 卡不住 ⇒ 两边线圈内定位都做到 Φ(80 − COIL_FIT) 实体
#            ② 外圈铜螺母环太窄 (定子 7 宽, 转子 4.9 宽且 r79 Φ4.2 螺母孔切破环内壁 r77.5) ⇒ 外径不动, 环宽统一 NUT_RING_W = 10
COIL_ID, COIL_FIT = 80.0, 0.2                      # 线圈内径 / 直径间隙 (打印外圆偏大, 松了再减)
COIL_SEAT_R = (COIL_ID - COIL_FIT) / 2             # r39.9: 定子内墙外圆 = 转子毂盘内环外圆
NUT_RING_W = 10.0                                  # 外圈铜螺母环宽 (定子 r72.5–82.5 / 转子 r72.4–82.4) ⇒ 线圈外径需 ≤ Φ144
HUB_RAISE = [(25.0, COIL_SEAT_R), (82.4 - NUT_RING_W, 82.4)]   # 毂盘加高到 Z29.5 的两环 (原 (25,35)/(77.5,82.4); 11-17 内环扩到 r39.9 顶线圈, 外环内扩到 r72.4)
RIM_LOCK_PTS = [(30.0 * math.cos(math.radians(22.5 + 45 * k)), 30.0 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]   # r30 锁盘孔 (V1.0 原有, 承载盘 Φ3.2 / 毂盘 Φ3.2 + 底 Φ4.2 铜螺母)
_ann = lambda r0, r1, z0, z1: cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
#   先切整环 r25–82.5 Z26–29.5 (含下凸台), 再把下凸台 r35–40 补回 Z25.5–30 (与剩下的凸台/盘体都重叠, 连成一体);
#   直接切 "环减凸台" 时 r40 面与 V1.0 凸台面重合, OCC 布尔会静默失败 (只剩凸台)
rim = clean(cut(rim, _ann(RIM_BORE_R - 1.0, RIM_SKIRT[0], 24.0, RIM_BOT)))   # 内径取 r24 (内孔里本来空): 与 r25 内孔面重合时同样静默失败
# 11-17: 下凸台 r35–40 (原 Z24.5) 整个切掉 (上面切到 Z24), 线圈内定位改由毂盘内环 r≤COIL_SEAT_R 实体承担; 承载盘定心靠内孔 Φ50 套毂盘中心凸台
assert len(solids(rim)) == 1 and abs(bbox(rim)[5] - 32.0) < 0.01 and abs(bbox(rim)[2] - RIM_SKIRT[2]) < 0.01, ('承载盘减薄布尔出错', len(solids(rim)), bbox(rim))
#   局部凸台: 罩底 4 (SHR_HOLES) + 无线托盘 3 (MOD_HOLES) 铜螺母孔下, 盘底往下长 Φ9 到 Z27.5 (局部厚 4.5), 铜螺母孔照旧 (SHR Z28–32 / MOD Z27.8–32)
#   这 7 个凸台全落在毂盘加高环上 (SHR r79 / MOD (±11, −76.5) r77.3 在外环 r77.5–82.4, MOD (0, −31) 在内环 r25–35) ⇒ 毂盘在凸台下让位 Φ10 (只加高到原 Z27, 凸台底留 0.5)
RIM_BOSS_D, RIM_BOSS_Z0 = 9.0, 27.5
HUB_BOSS_CLR_D = 10.0
_boss_pts = [(p, 32.0 - 4.0) for p in SHR_HOLES] + [(p, 32.0 - 4.2) for p in MOD_HOLES]
rim = clean(fuse(rim, *[cut(cyl(x, y, RIM_BOSS_D, RIM_BOSS_Z0, RIM_BOT + 0.5), cyl(x, y, 4.2, z0, 33.0)) for (x, y), z0 in _boss_pts]))   # 凸台自带孔 (免同轴同径重切)
#   底板 4 孔 Φ3.4 + 盘底 Φ7.4×1.5 沉孔已在上面切 (凸台不在这 4 处, 不用补切; 同轴同径重切会把实体切坏)
#   毂盘加高: 两环 Z27 → Z29.5; 让位 = 7 个凸台 Φ10 + 底板头 Φ8.4 (r75.5 / r77.8 两孔在外环上, 头底 Z29.5 不压毂盘); 重开 r79 外圈 Φ3.4 和 r30 锁盘 Φ3.2
HUB_BB_CLR_D = 8.4
#   内环内径取 r24.5 (伸进毂盘中心凸台 0.5, 免与 Φ50 面重合); 孔先在加高环上开好再并 (毂盘上同轴同径重切会切坏实体); 并后留十来个零面积碎面, 实体有效
# 11-17: 加高环底从 Z27 改 Z24 (新扩的 r35–39.9 / r72.4–77.5 原是线圈腔, 腔底 Z24.5) ⇒ 两圈铜螺母孔 (r79 Z21.5–25.5 / r30 Z21.5–26) 要在环上一并让开;
#   (21, −70) 线圈 AC 引线孔 r73.1 落到外环上 ⇒ 外环开 Φ3.4 引线缺口 (承载盘孔正下方), 线从腔里直上
_raise = fuse(*[cut(cyl(0, 0, 2 * r1, 24.0, RIM_BOT), cyl(0, 0, 2 * (r0 - 0.5 if r0 < 30 else r0), 23.0, 30.0)) for r0, r1 in HUB_RAISE])
_raise = cut(_raise, *[cyl(x, y, HUB_BOSS_CLR_D, 26.0, 30.0) for (x, y), _ in _boss_pts], *[cyl(x, y, HUB_BB_CLR_D, 26.0, 30.0) for x, y in BB_HOLES],
             *[fuse(cyl(x, y, 3.4, 20.0, 30.0), cyl(x, y, 4.2, 20.0, RH_INS[1])) for x, y in RH_PTS], *[fuse(cyl(x, y, 3.2, 20.0, 30.0), cyl(x, y, 4.2, 20.0, 26.0)) for x, y in RIM_LOCK_PTS],
             *[cyl(x, y, AC_HOLE_D + 0.4, 20.0, 30.0) for x, y in AC_HOLES])
_hub_v0 = vol(hub); _raise_new = vol(cut(_raise, hub))   # 11-17: 环底 Z24 与原实体有重叠, 按净增量校核
hub = clean(fuse(hub, _raise))
assert vol(hub) - _hub_v0 > 0.95 * _raise_new, ('毂盘加高布尔静默失败', vol(hub) - _hub_v0, _raise_new)
assert len(solids(rim)) == 1 and len(solids(hub)) == 1 and abs(bbox(hub)[5] - 30.5) < 0.01, ('承载盘凸台 / 毂盘加高布尔出错', len(solids(rim)), len(solids(hub)), bbox(hub))
LOG['rim_thin'] = dict(bot=RIM_BOT, hub_raise=HUB_RAISE, boss=(RIM_BOSS_D, RIM_BOSS_Z0), n_boss=len(_boss_pts), rim_v=vol(rim), hub_v=vol(hub),
                       rim_valid=BRepCheck_Analyzer(rim).IsValid(), hub_valid=BRepCheck_Analyzer(hub).IsValid(), rim_solids=len(solids(rim)), hub_solids=len(solids(hub)))
#   配平: 11-16 起改在转子罩内配重唇 (rotor_shroud_v1_2.py), 承载盘原 r76@112° 配平孔取消
CW_PT = None
# 校核: 每个新孔外 Φ8 环 (孔壁 1.9) 在盘顶下 4.5 内是实心
LOG['rh_std'] = dict(idx=RH_STD_IDX, head_z0=RH_HEAD_Z0, L=RH_L, tip=RH_HEAD_Z0 - RH_L, ins=RH_INS)
LOG['rh_ear'] = dict(idx=RH_EAR_IDX, pts=[(round(x, 2), round(y, 2)) for x, y in RH_EAR_PTS], z0=RH_EAR_Z0, tip_z=RH_EAR_TIP_Z, tip_rec=RH_EAR_TIP_REC, ins=RH_INS)
LOG['rim_new_holes_solid'] = {f'{n_}{i}': round(vol(op(BRepAlgoAPI_Common, _rim_pre, cut(cyl(x, y, 8.0, 27.6, 32.0), cyl(x, y, 4.3, 27, 33)))) / vol(cut(cyl(x, y, 8.0, 27.6, 32.0), cyl(x, y, 4.3, 27, 33))), 3)
                              for n_, pts in (('bb', BB_HOLES), ('mod', MOD_HOLES), ('shr', SHR_HOLES)) for i, (x, y) in enumerate(pts)}

# ---------------- 4 底盘 ----------------
# 4a 电机控制板 (沿用 V1.0 motor_tray 11-04 做法, 托板并进底盘): 板平放底盘顶面 z0, 器件朝上;
#    板本地 x20..100 y10..50 (= 板系 +20,+10); 外长边 (板系 y0) 朝外, 内长边离轴 BOARD_IN; XT60/MR30 不焊 (直接焊线)
BOARD_F = V12.parent / 'v1.0' / 'boards' / 'step' / 'motor_ctrl_2026-10-23.step'  # 与交付包 _待确认 版逐字节相同
BOARD_DX = 3.5                                   # 往 +X 让 3.5: 铜螺母/散热片槽让开立柱孔 (−37.5,87.5)
BOARD_Z, BOARD_IN = 0.0, COLLAR_FLAT + 0.75     # 内边离套环削平面 0.75 (11-11: 36.25; 原 39.25 / 42.75)
def board_trsf():
    t1 = gp_Trsf(); t1.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi)          # (x,y)->(-x,-y)
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(60 + BOARD_DX, BOARD_IN + 50, BOARD_Z))                        # -> (60-x, IN+50-y)
    t3 = rotz(BOARD_ANG - 90)
    return t3.Multiplied(t2.Multiplied(t1))
BT = board_trsf()
from OCP.BRep import BRep_Builder as _BB
from OCP.TopoDS import TopoDS_Compound as _TC
from helpers import read_step_cached as _rsc; _raw = _rsc(BOARD_F); _B = _BB(); _bc = _TC(); _B.MakeCompound(_bc); _drop = 0
NOPOP = [(20.1, 28.4, 24.7, 41.0), (94.0, 99.5, 28.9, 41.0)]       # XT60 / MR30 (V1.0 同, 板系 +20/+10)
CAP_H_MEAS, _CAP_FIX = 6.1, []
HDR_H_RA, _HDR_FIX = 2.54, []
for s__ in solids(_raw):
    b__ = bbox(s__)
    if any(b__[0] >= x0 - .01 and b__[3] <= x1 + .01 and b__[1] >= y0 - .01 and b__[4] <= y1 + .01 for x0, x1, y0, y1 in NOPOP) \
       and (b__[5] > 1.61 or b__[2] < -0.02):
        _drop += 1; continue
    # 11-16 晚 用户实测: 板上 2 颗电解 (STEP 里 Φ6.3×7.7, 顶 Z9.31) 实物高 6.1 (板面起) ⇒ 换成 Φ 同径圆柱, 顶 = 板面 + 6.1 (Z≈7.7, 定子盘底 Z8.5 下 0.8, 不再挖坑)
    _w, _d = b__[3] - b__[0], b__[4] - b__[1]
    if 6.0 < _w < 7.3 and abs(_w - _d) < 0.5 and b__[5] > 9.0:
        _CAP_FIX.append([round(v, 2) for v in b__])
        s__ = cyl((b__[0] + b__[3]) / 2, (b__[1] + b__[4]) / 2, _w, b__[2], b__[2] + CAP_H_MEAS)
    elif b__[5] > 9.5 and max(_w, _d) < 10.0:
        # 11-16 晚 用户: 3P 直排针改弯排针 (卧装) ⇒ 包络压到板面 + 2.54 (塑料座高), 原顶 Z10.09; 定子盘底面不再挖方坑
        _HDR_FIX.append([round(v, 2) for v in b__])
        s__ = BRepPrimAPI_MakeBox(gp_Pnt(b__[0], b__[1], b__[2]), gp_Pnt(b__[3], b__[4], 1.6 + HDR_H_RA)).Shape()
    _B.Add(_bc, s__)
board = xf(_bc, BT); LOG['board'] = dict(dropped_solids=_drop, caps_fixed=_CAP_FIX, cap_h=CAP_H_MEAS, header_fixed=_HDR_FIX)
def bl(x0, y0, x1, y1, z0, z1):      # 板本地矩形 -> 全局实体 (z 为全局)
    return xf(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0 - BOARD_Z), gp_Pnt(x1, y1, z1 - BOARD_Z)).Shape(), BT)
BHOLES = [(24.49, 14.49), (24.49, 45.49), (95.49, 14.49), (95.49, 45.49)]
SINK = (72.0, 10.0, 92.0, 50.0)                                     # 板系 x52..72 y0..40, 盖 6 颗 MOS
RELIEFS = [(21.0, 28.3, 24.8, 40.9), (94.1, 99.0, 29.0, 40.9), (54.5, 62.5, 10.05, 13.05)]   # x0,x1,y0,y1 背面焊点/排针; 11-17 晚 用户: 第 3 个 (下载排针) 7.6×2.5 → 8×3 同心 (原 54.7–62.3 × 10.3–12.8)
RELIEF_THRU = {2}                                   # 11-17 晚 用户: 第 3 个 (电机控制板下载排针背面焊脚) 由深 3 改通槽
def sink_shape():                                                   # 40x20x6: 底座 2 + 7 鳍, 鳍朝下
    sh = bl(SINK[0], SINK[1], SINK[2], SINK[3], -2.0, 0.0)
    for i in range(7):
        x0 = SINK[0] + i * (20 - 1.4) / 6
        sh = fuse(sh, bl(x0, SINK[1], x0 + 1.4, SINK[3], -6.0, -2.0))
    return sh
heatsink = sink_shape()
SH_NUT_D = 8.0                                     # 用户 11-12: 下罩 A 孔螺母 Φ8 (含余量), 贴墙内面
SH_R = 90.8 - SH_NUT_D / 2                         # 用户 11-12: = r86.8 (墙内面 r90.8 直下 - 4, 孔心到内圆 4); 曾 r88 / r85
SH_R_OLD = 83.0                                        # 用户 11-11: 下罩 M6 用 V1.1 四孔 (±62.5,±62.5) 往里挪到 r83, 下罩内侧加 4 个耳片
SH_M6 = [(SH_R * math.cos(math.radians(a)), SH_R * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
_bb = bbox(board)
SUP_R, SUP_A0 = 84.0, 22.5                         # 用户 11-11 选方案 1: 外圈 8×M3 在 22.5°+45k (M6 夹在每对中间), r86
OUT_ALL = [(SUP_R * math.cos(math.radians(SUP_A0 + 45 * k)), SUP_R * math.sin(math.radians(SUP_A0 + 45 * k))) for k in range(8)]
OUT_SCREWS = [(x, y) for x, y in OUT_ALL if not (_bb[0] - 6 < x < _bb[3] + 6 and _bb[1] - 6 < y < _bb[4] + 6)]   # 有托块, 锁到底盘
OUT_HANG = []                                      # 用户 11-12: 外圈 8×M3 取消, 定子盘只用中央 8×M3 锁底盘; OUT_SCREWS 只剩托块位置 (无孔)
OUT_SKIPPED = []
XT_ANG = 0.0                                       # XT60 正右边 (+X)
_c, _s = math.cos(math.radians(XT_ANG)), math.sin(math.radians(XT_ANG)); XT_Y0, XT_Y1, XT_HW, XT_H = -11.95, 14.95, 19.0, 13.0
XT_RF = 109.7                                      # 用户 11-13 (更正): 只有 XT60 接头口面内接 r110 (口面宽 15.6, √(110²−7.8²)=109.72 取 109.7, 角 r109.98, 中线凹 0.3); 压块/底垫外端仍 r110 圆弧 (原 112.5 伸出 2.5)
XT_HOLE_RC = 100.0                                 # 用户 11-13 晚: 底盘已按 b0a79b0 (11-12) 打印, XT60 孔留在 x100.0 (r100.78) 不动 ⇒ 压块/底垫孔在局部系外移 2.8 (V1.2-g)
_rc = XT_HOLE_RC                                    # (8878ee8 曾改 XT_RF − 11.95 − 0.55 = 97.2, 已撤回)
XT_GHOLES_DISC = [(_rc * _c - xx * _s, _rc * _s + xx * _c) for xx in (12.5, -12.5)]   # 与 4c XT_GHOLES 相同 (下面 assert)
# 4b 底盘: M6 网格位 (节距 25, ±12.5..±87.5, 同原金属网格板); 11-18 起只留外圈 4 个 (POSTS), 见 GRID_DROP
SEAT_M6 = [(62.5, 62.5), (-62.5, 62.5), (-62.5, -62.5), (62.5, -62.5)]   # = V1.1 定位环原孔位 (板放正后 4 个都让得开)
SEAT_ANG = [math.degrees(math.atan2(y, x)) for x, y in SEAT_M6]
BOARD_KEEP = bl(20 - 8, 10 - 8, 100 + 8, 50 + 8, -10, 10)          # 板外框外扩 8 (= 沉孔半径 6.5 + 壁 1.5)
GRID = [(x, y) for x in (-87.5, -62.5, -37.5, -12.5, 12.5, 37.5, 62.5, 87.5) for y in (-87.5, -62.5, -37.5, -12.5, 12.5, 37.5, 62.5, 87.5)]
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_OUT
_kc = BRepClass3d_SolidClassifier(BOARD_KEEP)
def _inkeep(x, y):
    _kc.Perform(gp_Pnt(x, y, 0), 1e-4); return _kc.State() != TopAbs_OUT
FIXED = COLLAR_M6                                  # 用户 11-12: 下罩 4 孔改 M3 (SH_M6 位置不变, 单独开 M3 孔)
MOTOR_HOLES = [(sx * STATOR_R * s45, sy * STATOR_R * s45) for sx in (1, -1) for sy in (1, -1)]
M3_D, M3_CB_D, M3_CB_H = 3.2, 7.0, 1.5           # 内六角 M3 头 Φ5.5x3; 盘底往上装沉孔 用户 11-12: Φ6.5×3.5 → Φ7×2; 11-18 玻纤板方案: Φ7×1.5 (超薄头 1.5 齐底面) ⇒ 支承 Z-6, 盘底往上的 M3 全部 +2, 尖位置不变
INS_HOLE_D, INS_HOLE_H = 4.2, 4.2               # 用户 11-12 夜: 全部 M3 铜螺母孔统一 Φ4.2×4.2 (统一装 M3×4 铜螺母, 底面齐平)
def _loc(X, Y):      # 全局 -> 板本地
    p = gp_Pnt(X, Y, BOARD_Z).Transformed(BT.Inverted()); return p.X(), p.Y()
def _rect_hit(x, y, rad, r):   # 圆 (x,y,rad) 与本地矩形 r=(x0,y0,x1,y1) 相交
    dx = max(r[0] - x, 0, x - r[2]); dy = max(r[1] - y, 0, y - r[3]); return math.hypot(dx, dy) < rad
EXTRA, SKIP = [], []
# 4a' 定子线圈驱动小板 (用户 11-12 晚): MOS 压块 mos_clamp_v1_2 + 电容卡件 cap_clamp_v1_2 + 第二块散热片 (转 90°) + 底盘切口, 几何在 coil_drv_geom.py (不 import 本文件)
import coil_drv_geom
CD = coil_drv_geom.make(sys.modules[__name__])
# 4a'' 按键板 + 支架 (用户 11-13 (二) L 形 / (三) 前面平板): +Y 侧下罩墙里竖放, 几何在 key_bracket_v1_2.py (不 import 本文件); 脚 2×M3×12 从盘底往上, 法兰螺母坐脚顶
import key_bracket_v1_2
KEY = key_bracket_v1_2.make_key_bracket(dict(SH_OUT=DISC_D / 2, DISC_T=DISC_T, M3_CB_H=M3_CB_H, M3_D=3.2, FOOT_SCREW_L=14.0))   # 11-18: 底座 7.5 ⇒ 脚螺丝 12→14
key_bracket, key_board = KEY['bracket'], KEY['board']
KEY_M3 = KEY['disc_m3']                                     # [(±27, 95)] 支架脚孔
for x, y in GRID:                                   # 原洞洞板 M6 网格: 盘内放得下的全开
    if math.hypot(x, y) + CB_D / 2 > DISC_D / 2: continue
    why = []
    if any(math.hypot(x - a, y - b) < CB_D + 1.0 for a, b in COLLAR_M6): why.append('电机座孔')
    if math.hypot(x, y) < COLLAR_D / 2 + M6_D / 2 + 1.0: why.append('电机/线圈环下')
    lx, ly = _loc(x, y)
    if _rect_hit(lx, ly, CB_D / 2 + 1.0, SINK): why.append('散热片槽')
    if any(math.hypot(lx - a, ly - b) < CB_D / 2 + 2.1 + 1.0 for a, b in BHOLES): why.append('铜螺母孔')
    if any(_rect_hit(lx, ly, M6_D / 2 + 1.0, (x0, y0, x1, y1)) for x0, x1, y0, y1 in RELIEFS): why.append('背面让位槽')
    if any(math.hypot(x - a, y - b) < CB_D + 1.0 for a, b in XT_GHOLES_DISC): why.append('XT60 压块孔')
    if any(math.hypot(x - a, y - b) < CB_D + 1.0 for a, b in SH_M6): why.append('下罩耳片孔 (内移)')
    if any(math.hypot(x - a, y - b) < CB_D / 2 + 2.1 + 1.0 for a, b in OUT_SCREWS): why.append('法兰外圈铜螺母')
    if any(math.hypot(x - a, y - b) < 1e-6 for a, b in CD.GRID_REMOVE): why.append('线圈驱动板')
    if any(math.hypot(x - a, y - b) < CB_D / 2 + 7.0 / 2 + 1.0 for a, b in KEY_M3): why.append('按键支架 M3')
    (SKIP if why else EXTRA).append(((x, y), why) if why else (x, y))
assert all(p in EXTRA for p in POSTS), ('立柱孔被挡', [q for q in SKIP if q[0] in POSTS])
GRID_DROP = [p for p in EXTRA if p not in POSTS]          # 用户 11-18: 网格 M6 孔没实际用途 → 只留外圈 4 个 (= POSTS R95.2, 当锁台面/扩展孔), 其余 22 个删掉
EXTRA = [p for p in EXTRA if p in POSTS]
LOG['disc_holes'] = dict(collar=len(COLLAR_M6), grid=len(EXTRA), dropped=GRID_DROP, skipped=SKIP)
d = cyl(0, 0, DISC_D, -DISC_T, 0)
for x, y in FIXED + EXTRA:
    d = cut(d, cyl(x, y, M6_D, -DISC_T - 1, 1), cyl(x, y, CB_D, -DISC_T - 1, -DISC_T + CB_H))
for x, y in MOTOR_HOLES:                                                                  # 电机 4×M3 从盘底往上
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1))
d = cut(d, bl(SINK[0], SINK[1], SINK[2], SINK[3], -DISC_T - 1, 1))                       # 散热片通槽 20x40, 零间隙
for i_, (x0, x1, y0, y1) in enumerate(RELIEFS):
    d = cut(d, bl(x0, y0, x1, y1, -DISC_T - 1 if i_ in RELIEF_THRU else -3.0, 1))           # 背面让位 深 3; RELIEF_THRU 里的打通
for x, y in BHOLES:
    p = gp_Pnt(x, y, 0).Transformed(BT)
    d = cut(d, cyl(p.X(), p.Y(), M3_D, -DISC_T - 1, 1), cyl(p.X(), p.Y(), M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))  # 用户 11-13: 控制板 4×M3 改盘底 Φ7×2 沉孔往上, 法兰螺母坐板顶 (原板顶往下进铜螺母)
for x, y in MOTOR_HOLES:                                                                   # 电机 4×M3 盘底上锁
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
d = cut(d, cyl(0, 0, 12.0, -3.0, 1))                                                       # 电机中央 Φ12x3
for x, y in RING_M3:                                                                      # 线圈环四角 4×M3x10: 盘底沉孔, 穿四角 (5 厚) 通孔顶面上螺母
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D / 2 + M3_CB_D / 2 + 1.0 for x, y in RING_M3 for a, b in FIXED + EXTRA), '线圈环 M3 沉孔离 M6 沉孔太近'
G_NUT_D, G_NUT_H = 8.0, 3.7                    # 11-19 用户「底板最下边8个热熔螺母换成法兰螺母吧也」(同承载盘内圈 d5747d2): 底面 Φ8×3.7 沉孔放 M3 法兰螺母 (法兰朝下齐底面), 原 Φ4.2×4.2 铜螺母孔作废
assert G_NUT_H <= PRINT_T - 0.5                     # 沉孔只在打印底盘里 (Z-7.5..-3.8), 不进玻纤板
for x, y in FLANGE_SCREWS:                                                                 # 线圈环/法兰 8×M3 (从安装法兰顶往下): 盘底沉孔里法兰螺母
    d = cut(d, cyl(x, y, 3.2, -DISC_T - 1, 1), cyl(x, y, G_NUT_D, -DISC_T - 1, -DISC_T + G_NUT_H))
for x, y in SH_M6:                                                                         # 下罩 4×M3x10: 盘底沉孔往上, 螺母压三角块顶
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D + 1.0 for x, y in XT_GHOLES_DISC for a, b in FIXED + EXTRA), 'XT60 孔与网格孔沉孔重叠'
# 用户 11-13 晚: 底盘已打印 (b0a79b0 版), XT60 两孔保持打印件原样 = M6 Φ6.4 通 + 底面 Φ13×3 沉孔 @ (100, ±12.5);
#   装 M3×20 + M3 大垫片 Φ9×0.8 (DIN 9021) 顶在 Φ13 沉孔顶 Z−3 (头支承 Z−3.8), 法兰螺母坐压块顶 Z13..16.7, 尖 Z16.2 (啮合 3.2)
XT_DISC_HOLE = (M3_D, M3_CB_D, M3_CB_H)            # 新底盘 (11-13 晚); 已打印 b0a79b0 件 = (M6_D, CB_D, CB_H) + 垫片 XT_WASHER
XT_WASHER_D, XT_WASHER_T = 9.0, 0.8
for x, y in XT_GHOLES_DISC:
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))   # 用户 11-13 晚: 新底盘兼容 V1.2-g 压块 → 孔位 x100 不变, 改标准 M3 Φ3.2 + 底面 Φ7×2 (不用垫片); 11-12 已打印件仍是 Φ6.4+Φ13×3, 装时加 Φ9 大垫片
for x, y in KEY_M3:                                                                        # 按键支架 2×M3×12 (11-13 L 形): 盘底 Φ7×2 沉孔往上 → 穿脚 (4 厚) → 脚顶法兰螺母
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D / 2 + M3_CB_D / 2 + 1.0 for x, y in KEY_M3 for a, b in FIXED + EXTRA), '按键支架 M3 沉孔离网格孔太近'
assert all(math.hypot(x, y) + M3_CB_D / 2 <= DISC_D / 2 - 1.0 for x, y in KEY_M3), '按键支架 M3 沉孔出盘边'
d = cut(d, *CD.disc_cut_list)                                                              # 线圈驱动板: 散热片通槽 + 3×M3 沉孔 + 电容弧形槽 + 背面电容坑
# 用户 11-16: 电机线 MR30 座 (−x 侧, M6 孔 (−62.5,±12.5) 之间) + 束线夹 (M6 孔 (−37.5/−12.5, −62.5) 之间), 件在 motor_wire_v1_2.py (该脚本 assert 与这里一致)
#   4×M3 Φ3.4 通 + 底面 Φ7×2 沉孔 (M3×12 / M3×10 往上进件顶铜螺母); MR30 护套坑 12.3×6.9 深 0.25 (本体底面落底盘顶 Z0)
MW_M3 = [(-72.0, -0.05), (-50.0, -0.05), (-23.5, -52.5), (-23.5, -71.5)]   # 11-18 用户: 玻纤板版用加宽件 (孔各外移 1); 旧一体底盘配 _old 件 (原孔 (-71/-51, -0.05) (-23.5, -53.5/-70.5))
MW_HOLE_D = 3.4
MW_POCKET = None                                  # 11-18 用户: MR30 座加底片后护套坑取消 (原 (-67.15, -6.5, -54.85, 0.4, 0.25), 玻纤板上成 S1 通孔)
for x, y in MW_M3:
    d = cut(d, cyl(x, y, MW_HOLE_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
disc = clean(d); LOG['disc'] = dict(v=vol(disc))      # 整块 (校核用, 等于 disc_print + fr4 外包)
# 11-18 拆件: 打印底盘 = disc ∩ Z-7.5..-3; 玻纤板 = disc 在 Z-0.1 的截面面 拉 Z-3..0 (顶面槽全部变通孔, 底面沉孔/铜螺母孔不进玻纤板)
disc_print = clean(op(BRepAlgoAPI_Common, disc, cyl(0, 0, DISC_D + 2, -DISC_T - 1, -FR4_T)))
def _fr4_face():
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopoDS import TopoDS
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Plane
    th = op(BRepAlgoAPI_Common, disc, cyl(0, 0, DISC_D + 2, -0.2, -0.1)); fc = []
    ex = TopExp_Explorer(th, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current()); sf = BRepAdaptor_Surface(f)
        if sf.GetType() == GeomAbs_Plane and abs(sf.Plane().Location().Z() + 0.2) < 1e-6: fc.append(f)
        ex.Next()
    assert len(fc) == 1, len(fc)
    t = gp_Trsf(); t.SetTranslation(gp_Vec(0, 0, -FR4_T + 0.2))
    return TopoDS.Face(BRepBuilderAPI_Transform(fc[0], t, True).Shape())
FR4_FACE = _fr4_face()                                  # 板底面 Z-3 (DXF 用)
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
fr4 = clean(BRepPrimAPI_MakePrism(FR4_FACE, gp_Vec(0, 0, FR4_T)).Shape())
LOG['disc_split'] = dict(print=vol(disc_print), fr4=vol(fr4))
LOG['coil_drv'] = dict(xpc=CD.XPC, xb=CD.XB, has_mc=CD.HAS_MC, has_cc=CD.HAS_CC, merge_err=CD.MERGE_ERR, mc_holes=[(round(x, 2), round(y, 2)) for x, y in CD.MC_HOLES],
                       cc_holes=[(round(x, 2), round(y, 2)) for x, y in CD.CC_HOLES], pcb_z=(CD.PCB_Z0, CD.PCB_Z1), mos_y=(CD.MOS_Y_LEAD, CD.MOS_Y_TIP), bcap_pits=CD.BCAP_PITS,
                       cap=(CD.CAP_CX, CD.CAP_Y0, CD.CAP_Y1, CD.CAP_ZC, CD.CAP_GROOVE), sink=(CD.SINK_X0, CD.SINK_Y0, CD.SINK_X1, CD.SINK_Y1))
# 4c 玻璃罩下罩+定位环 V1.2 (用户 11-11): 玻璃 OD200x5 高 245, 下端原与转子承载盘顶齐平 (11-13 晚改: 内卡顶 = LED 下沿 − 10, 见 Z_G); 下罩从底盘包住定子到玻璃下端,
#    顶上承台托玻璃, 内卡 (伸进玻璃内) 深 20, 外卡深 10; 用 V1.1 定位环 4 个 M6 孔 (±62.5,±62.5) 从盘底锁
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
GL_OD, GL_T, GL_H = 200.0, 5.0, 245.0
Z_RIM_TOP = round(bbox(rim)[5], 2)                 # 承载盘顶 32.0
Z_SHR_REF = Z_RIM_TOP                              # 11-18: 玻璃罩 (底圈/玻璃座分缝, 按键开口顶) 仍按原盘顶 Z32 定, 不随转子盘B 减薄动
if ROTOR_B: Z_RIM_TOP = ROTOR_TOP + 3.0 + 2.8 + 3.2   # 11-18 用户: 转子盘B 承载盘总厚 9 = 外唇/玻纤板 3 + 线圈腔 2.8 + 托盘 3.2 ⇒ 盘顶 Z30.5 (原 32)
SH_OUT = DISC_D / 2                                # 用户草图 11-11: 外面与底盘外缘齐平 r110
SPIG_T = 4.0                                       # 用户 11-11 嫌内卡薄: 2.8 → 4.0, 往里加 (内卡 r90.8–94.8, 离承载盘外缘 1.8)
GL_CLR = 0.2                                       # 玻璃单边间隙
IN_DEPTH, OUT_DEPTH = 20.0, 10.0                   # 内卡 20, 外卡贴玻璃处 10, 顶面 45° 往外降
# 用户 11-13 晚: V2 灯板 (LED_V0.2.0 11-13, 板高 208, LED 在上部); SoC+WiFi 同一平面 = 转接板 (POV3D_V2_BaseBoard 140×80×1.6,
#   器件全在顶面, 底面只有插件脚) + MLK CZ06 核心板 (60×35, DF40 合高 3.0 + 板 1.6 + 顶面器件 ≈2.0 = 6.6, 转接板 README), 转接板出 2 根 FPC 给桥板;
#   玻璃下加高, 内卡顶 (不透光部分的最高点) = LED 下沿 − VIEW_MARGIN
BB_STANDOFF, BB_T, CZ06_H, CZ06_CLR = 3.0, 1.6, 6.6, 2.0   # 转接板垫柱 (让插件脚) / 板厚 / CZ06 堆高 / CZ06 顶 → 灯板下沿
Z_BB0 = Z_RIM_TOP + BB_STANDOFF                    # 转接板底 35.0
SCREEN_GAP = 8.0 if ROTOR_B else 5.0               # 11-20 夜 用户「灯板往高挪1mm」(灯板 +1: 7→8, 承载盘顶 Z30.5 → 灯板下沿 Z38.5, 中间由 3D 打印屏幕支撑件占满; 玻璃/罩顶 Z_VIEW0 不动); 11-18 用户「led屏幕抬高2mm」(取消承载盘 FPC B 让位槽, FPC 最低点离盘顶 0.6); 用户 11-16: 灯板几乎贴盘, 下沿离承载盘顶 5 (要过 FPC/线); 转接板移到 +y 侧 (原 13.2 = 垫3+板1.6+CZ06 6.6+留2)
LED_BOARD_H = 208.0                                # 灯板高 (板框 163.76 × 208.01)
LED_LOW_OFF = 37.88                                # 灯板下沿 → 最下一行 LED 像素下沿 (行心 38.66 − 节距 1.5626/2)
Z_SCR0 = Z_RIM_TOP + SCREEN_GAP                    # 灯板下沿 38.5 (转子盘B, 11-20 夜 +1; 原 37.5 / 45.2)
Z_LED0 = Z_SCR0 + LED_LOW_OFF                      # LED 下沿 74.88 (原 83.08)
Z_SCR1 = Z_SCR0 + LED_BOARD_H                      # 灯板上沿 245.0
# 用户 11-16: 底座已打印, 玻璃下两件不改 ⇒ 玻璃落座面钉死 53.08 (原 = LED 下沿 − 10 − 内卡 20); 内卡顶 73.08 仍低于 LED 下沿 1.8
Z_G = 53.08                                        # 玻璃下端
Z_VIEW0 = round(Z_G + IN_DEPTH, 2)                 # 可视下边界 = 内卡顶 73.08
VIEW_MARGIN = round(Z_LED0 - Z_VIEW0, 2)           # 1.8 (原 10)
assert VIEW_MARGIN >= 0, f'内卡顶 Z{Z_VIEW0} 挡住最下一行 LED Z{Z_LED0}'
TAB_T, TAB_W = 3.5, 18.0                           # 耳片厚 / 宽; M6x10 从盘底, 螺母压耳片顶 (z3.5–8.5, 法兰底 9.3)
NUT_T = 2.4                                        # M3 螺母
gi, go = GL_OD / 2 - GL_T - GL_CLR, GL_OD / 2 + GL_CLR    # 94.8 / 100.2
SPIG_IN = gi - SPIG_T                              # 用户 11-12: 墙内面 = 内卡内面 r90.8 一条直线到底 (原 r92 有 1.2 台阶); 控制板最外角 r90.4, 承载盘 r89
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
LIP_EDGE = 1.5                                     # 外卡外缘留 1.5 直边 (分体环不出 0.2 薄边), 斜面 ≈41°
_r1 = SH_OUT + LIP_EDGE * (SH_OUT - go) / (OUT_DEPTH - LIP_EDGE)
_cone = BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(0, 0, Z_G), gp_Dir(0, 0, 1)), _r1, go, OUT_DEPTH).Shape()
s_ = ann(SPIG_IN, SH_OUT, 0, Z_G)                                              # 实心墙 r92–110
s_ = fuse(s_, ann(gi - SPIG_T, gi, Z_G, Z_G + IN_DEPTH))                       # 内卡 (z32 以上, 内面比墙内面往里 1.2)
s_ = fuse(s_, op(BRepAlgoAPI_Common, ann(go, SH_OUT, Z_G - 1, Z_G + OUT_DEPTH), _cone))   # 外卡 45° 斜顶
def gbox(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
# 托台 (用户 11-11 第二版): 角上 M6 三角块厚 5 (螺母压顶面); 8 个定子盘托块单独做, 高到定子盘底 = 线圈环托台高
P_N = 51.0
TRI_T = 5.0
_cross = fuse(gbox(-200, -P_N, -1, 200, P_N, 20), gbox(-P_N, -200, -1, P_N, 200, 20))
s_ = fuse(s_, cut(cyl(0, 0, 2 * SPIG_IN + 1, 0, TRI_T), _cross))                # 四角三角块
NUT_Z0 = TRI_T                                     # 用户 11-12 改 M3: M3x10 从盘底沉孔往上, 穿底盘+三角块, M3 螺母压三角块顶 (z5–7.4)
assert abs(SH_R - (SPIG_IN - SH_NUT_D / 2)) < 1e-9, '下罩螺母要贴墙内面'
# 11-16 晚: 安装法兰外裙伸到 Z8.5 后, 4 颗下罩 M3 法兰螺母 (r86.8 Φ8 含余量, Z5–8.7 实高 3.7) 顶到外裙 r82.5–85 ⇒ 外裙底局部挖 Φ8.6 到 Z9.0 (留 0.3)
MF_NUT_RELIEF = (SH_NUT_D + 0.6, NUT_Z0 + 3.7 + 0.3)
mounting_flange = clean(cut(mounting_flange, *[cyl(x, y, MF_NUT_RELIEF[0], FL_Z0 - 1, MF_NUT_RELIEF[1]) for x, y in SH_M6]))
NUT_CLR_D = 0.0                                    # 用户 11-12: 螺母 r84–92 在定子盘 r82.5 外、顶 Z7.4 < 定子盘底 Z9.3 ⇒ 定子盘/安装法兰不再开让位 (原 Φ10)
for x, y in SH_M6:
    s_ = cut(s_, cyl(x, y, 3.4, -1, TRI_T + 1))
# 用户 11-12: 三角块两条直边 (x=±P_N / y=±P_N) 各立一片斜三角筋, 外侧面与直边齐平, 尖角 → 墙内面全长, 与块顶/墙熔一体
#   侧视: 尖角 Z5 → 内侧面到 r GU_R85 处 Z GU_Z1 (r<85 段 ≤ 定子盘/安装法兰外裙底 FL_Z0 − 0.5) → 贴墙 Z GU_ZH (承载盘/毂盘底 Z21.5 下)
GU_T, GU_ZH, GU_R85 = 2.5, 15.0, 85.5
GU_Z1 = FL_Z0 - 0.5                                # 跟定子盘底走 (FL_Z0 9.5→8.5 时自动变 8.0)
assert GU_Z1 > TRI_T + 1, '定子盘太低, 筋 r<85 段没高度了'
def _gusset():
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    y1 = math.sqrt(GU_R85 ** 2 - P_N ** 2)                     # 内侧面 (x=P_N) 到 r85.5 处
    yw = math.sqrt(SPIG_IN ** 2 - (P_N + GU_T) ** 2)           # 外侧面 (x=P_N+T) 碰墙内面处
    pts = [(P_N, TRI_T - 1), (P_N, TRI_T), (y1, GU_Z1), (yw, GU_ZH), (SPIG_IN + 3, GU_ZH), (SPIG_IN + 3, TRI_T - 1)]
    pg = BRepBuilderAPI_MakePolygon()
    for y, z in pts: pg.Add(gp_Pnt(P_N, y, z))
    pg.Close()
    a = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(GU_T, 0, 0)).Shape()   # x=51 边的筋 (+x+y 角)
    m = gp_Trsf(); m.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(s45, -s45, 0)))                         # 关于 x=y 镜像 → y=51 边
    q = fuse(a, xf(a, m))
    return fuse(q, *[xf(q, rotz(90 * k)) for k in (1, 2, 3)])
GUSSETS = _gusset()
s_ = fuse(s_, GUSSETS)                                                         # 墙内 r>90.8 部分本来就是实体, 熔进去
SUP_W, SUP_IN = 12.0, 76.0                         # 用户 11-11: 托块加大, 宽 12, 从 r76 到墙, 端头 Φ12
for x, y in []:                                    # 用户 11-12: 托块 B 取消 (定子盘靠中央 8×M3 + 线圈环托住)
    a_ = math.degrees(math.atan2(y, x))
    _sp = fuse(xf(gbox(SUP_IN + SUP_W / 2, -SUP_W / 2, 0, SPIG_IN + 1.0, SUP_W / 2, FL_Z0), rotz(a_)), cyl((SUP_IN + SUP_W / 2) * math.cos(math.radians(a_)), (SUP_IN + SUP_W / 2) * math.sin(math.radians(a_)), SUP_W, 0, FL_Z0))
    s_ = fuse(s_, _sp)                                 # 用户 11-12: 托块不开 M3 通孔
# XT60 电源口 (用户 11-11: 开口按之前 XT60 锁底板的压块留) — 用户 11-12 晚改用 V1.2 专用版 scripts/xt60_clamp_v1_2.py
#   (由 models/xt60_clamp_16p6x9p2x23p9 复制: M3 + 防呆 R1.5 + 外端直线 (11-13, 原 r110 圆弧); 压块 38×26.9×11 外包 + 底垫 2, 叠高 13)
#   局部系: X 横跨 (孔距 25), Y 槽向 (-Y = 接头口, 朝外), Z 底=0; 底垫 z0, 压块 z2
XT_DIR = V12 / 'models' / 'xt60_clamp_v1_2'
# XT_Y0/XT_Y1/XT_HW/XT_H 见 4a
# XT_RF 见 4a (11-13 改 109.7): 内端 r82.8 伸进安装法兰外裙 r85 (法兰盘 r82.5 留 0.3, 让位 +0.5 削 0.2) ⇒ 两件在压块处开让位 (只到 Z XT_H+0.5)
XT_HOLES = [(-12.5, -2.25), (12.5, -2.25)]         # 压块 M3 Φ3.4 孔 (局部; V1.2-g: 0.55 → −2.25 = 径向外移 2.8, 对上已打印底盘 x100 孔)
XT_NUT_SEAT_H = 0.0                                # 用户 11-12: 压块顶面不做螺母座, M3 法兰螺母平坐压块顶 Z13..16.7; V1.2-g: M3×20 + 垫片 0.8 (头支承 Z−3.8), 尖 Z16.2 (啮合 3.2)
XT_NUT_WELL_D, XT_NUT_WELL_H = RING_NUT_CLR_D, 4.5 # 下罩里压块顶上的螺母井 Φ8.2 (法兰 Φ7.6 +0.3/边), Z13→17.5 (螺母顶 16.7 / 尖 16)
def xt_tr():                                       # 局部 -> 全局: Y 反向沿径向, 原点在 r = XT_RF + XT_Y0
    t = gp_Trsf(); t.SetValues(0, -1, 0, XT_RF + XT_Y0,  1, 0, 0, 0,  0, 0, 1, 0)   # (X,Y,Z)->(RC - Y, X, Z), 先在 +X 轴上
    return rotz(XT_ANG).Multiplied(t)
XT_T = xt_tr()
def xt_pt(x, y): p = gp_Pnt(x, y, 0).Transformed(XT_T); return p.X(), p.Y()
XT_GHOLES = [xt_pt(*h) for h in XT_HOLES]
def gbox(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
xt_env = xf(gbox(-XT_HW, XT_Y0, 0, XT_HW, XT_Y1, XT_H), XT_T)                         # 压块+底垫外包
s_ = cut(s_, xf(gbox(-XT_HW - 0.2, XT_Y0 - 5, -1, XT_HW + 0.2, XT_Y1 + 0.2, XT_H + 0.2), XT_T))   # 下罩开口 = 压块外形 +0.2
for gx, gy in XT_GHOLES:
    s_ = cut(s_, cyl(gx, gy, XT_NUT_WELL_D, XT_H, XT_H + XT_NUT_WELL_H))              # M3 法兰螺母 (压块顶上) 让位井 (原 M6 Φ14 到 Z19.5)
# 按键板 (11-13 (三)): 让位腔 = 支架 (平板/脚/筋)+板+法兰螺母/杆尖+背面元件区 外包 +0.3, 底开 (下罩从上罩下), 外皮 ≥1.5 (舌片除外); 外皮开导光柱 Φ3.0 ×4 + 按键 H 形缝舌片 (内面挖薄竖槽 + 凸点)
assert KEY['pocket_rmin'] >= SPIG_IN + 0.5 and KEY['skin'] >= 1.5, (KEY['pocket_rmin'], KEY['skin'])
s_ = cut(s_, KEY['pocket'], *KEY['skin_holes'])
# 用户 11-14: 板后面 (内侧) 不要留塑料 ⇒ 板背面到墙内面这段墙整块打通 (x ±筋外 +0.3, 竖直到 Z32 顶面, 下段顶开口由上段盖住; 支架照旧)
KEY_OPEN_X = KEY['params']['RIB_X1'] + KEY['params']['CLR']                       # ±22.9
KEY_OPEN_Y1 = KEY['board_screws'][0]['nut_y']                                    # 板背面 y
s_ = cut(s_, gbox(-KEY_OPEN_X, SPIG_IN - 5, -1, KEY_OPEN_X, KEY_OPEN_Y1, Z_SHR_REF + 0.01))
_kp = KEY['pocket_bbox']                          # 用户 11-18: 开口两侧 (x ±22.9..±腔边 32.3) 腔底 y89.7 与内墙 r86.8 之间的两块三角楔去掉 ⇒ 这段内墙也打通到腔底
s_ = cut(s_, *[gbox(a, 70.0, -1, b, _kp[2] + 0.01, Z_SHR_REF + 0.01) for a, b in ((_kp[0], -KEY_OPEN_X + 0.01), (KEY_OPEN_X - 0.01, _kp[1]))])
LOG['key'] = dict(m3=[(round(x, 2), round(y, 2)) for x, y in KEY_M3], skin=KEY['skin'], flap={k: KEY['flap'][k] for k in ('F_top', 'F_bot', 't_top')}, pocket_bbox=KEY['pocket_bbox'], open=(KEY_OPEN_X, KEY_OPEN_Y1), bracket_vol=KEY['bracket_vol'],
                  holes=[(round(x, 2), round(z, 2), dd) for x, z, dd in KEY['holes']])
def _stl(f):
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopoDS import TopoDS_Shape
    sh = TopoDS_Shape(); StlAPI_Reader().Read(sh, str(f)); return sh
_tz = gp_Trsf(); _tz.SetTranslation(gp_Vec(0, 0, 2.0))
# 读 STEP (m2b 由同一 mesh 转的实体, 体积与 STL 差 <0.01%); STL 读进来只是壳, 紧固件干涉 (BRepAlgoAPI_Common) 算不出体积
xt_clamp = xf(xf(one(XT_DIR / 'xt60_clamp_v1_2.step'), _tz), XT_T)
xt_shim = xf(one(XT_DIR / 'xt60_shim_v1_2.step'), XT_T)
xt_env = _TC(); _B.MakeCompound(xt_env); [_B.Add(xt_env, _s) for _s in (xt_clamp, xt_shim, xf(gbox(-8.3, XT_Y0, 2.0, 8.3, 11.95, 11.2), XT_T))]   # 11-17: 校核用实形 (压块+底垫+接头外包 16.6×23.9×9.2), 原外包盒 (到 r82.8 满高) 会误报安装法兰外裙; 用复合体 (fuse 网格转实体会丢件)
assert all(math.hypot(a - c, b - d_) < 1e-6 for (a, b), (c, d_) in zip(sorted(XT_GHOLES), sorted(XT_GHOLES_DISC))), (XT_GHOLES, XT_GHOLES_DISC)
LOG['outer'] = dict(n=len(OUT_SCREWS), skipped=OUT_SKIPPED)
LOG['xt60'] = dict(ang=XT_ANG, holes=[(round(x, 2), round(y, 2)) for x, y in XT_GHOLES])
_fd = flange_disc                                  # 用户 11-12: 定子盘外径改回原尺寸 (不再扩 Φ181)
_fd = cut(_fd, xf(gbox(-XT_HW - 0.5, XT_Y0 - 5, -1, XT_HW + 0.5, XT_Y1 + 0.5, XT_H + 0.5), XT_T))   # XT60 压块处让位 (11-13 压块内移: 切到 r82.3, 只切 Z≤13.5)
# 用户 11-12: 外圈 r78 8 孔保留 (原 V0.4 定子盘/安装法兰上下盖互锁螺丝), 不再补实
CAV_R0 = COIL_SEAT_R                               # 11-17 用户: 线圈内径 80 ⇒ 内墙外圆 r38.7 → r39.9 (内墙 r31.7–39.9)
CAV_R1 = 82.5 - NUT_RING_W                         # 11-17 用户: 外圈铜螺母环 7 宽 → 10 宽 ⇒ 腔外壁 r75.5 → r72.5 (外墙 r72.5–82.5)
CAV_Z0 = FL_TOP - 2.8                              # 11-16 晚 用户: 线圈腔深 2.5 → 2.8 ⇒ 腔底 Z10.7 (底板 2.2)
LID_R = (CAV_R1 + 82.5) / 2                       # 11-17 晚 用户: 居中到外墙 (螺母环 10 宽 r72.5–82.5) ⇒ r77.5 (原 82.5−CB7/2 = r79 是 7 宽墙时的居中; 现与转子盘B R77.5 对齐, 现行转子 RH_R 仍 79)
LID_SCREWS = [(LID_R * math.cos(math.radians(22.5 + 45 * k)), LID_R * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]   # 外圈 r79 8 孔 (上下盖互锁)
LID_INS_D, LID_INS_H = INS_HOLE_D, INS_HOLE_H      # 原 Φ2.5 攻牙孔 → 铜螺母从定子盘底面压; 11-12 夜: Φ4.2×4.2 (M3×4 铜螺母), 外墙 5 厚顶留 0.8, 螺丝 M3×6 (尾端齐底面 8.5)
_V04_OUT = [(77.5 * math.cos(math.radians(22.5 + 45 * k)), 77.5 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]   # V0.4 原外圈孔
for x, y in _V04_OUT: _fd = fuse(_fd, cyl(x, y, 4.6, FL_Z0, FL_TOP))         # 原 r77.5 孔补实 (先补再挖腔, 免补进腔里)
_fd = cut(_fd, ann(CAV_R0, CAV_R1, CAV_Z0, FL_TOP + 1))                       # 用户 11-12: 内外墙都收到 7 宽 (= Φ7 沉孔)
for x, y in LID_SCREWS: _fd = cut(_fd, cyl(x, y, 3.2, 0, 30), cyl(x, y, LID_INS_D, FL_Z0 - 1, FL_Z0 + LID_INS_H))
# 用户 11-12 夜: 定子盘底降到 8.5 ⇒ 控制板高器件 (2× 电解电容 Φ6.3×7.7 顶 9.31, 3P 排针顶 10.09) 上方底面局部挖让位, 四周/顶各留 BRD_POCKET_GAP
BRD_POCKET_GAP = 0.5
BRD_POCKETS = []
for s__ in solids(board):
    b__ = bbox(s__)
    if b__[5] <= FL_Z0 - BRD_POCKET_GAP: continue
    g_ = BRD_POCKET_GAP; z1_ = b__[5] + g_
    if abs((b__[3] - b__[0]) - (b__[4] - b__[1])) < 0.5:     # 圆柱 (电容): 圆坑
        sh__ = cyl((b__[0] + b__[3]) / 2, (b__[1] + b__[4]) / 2, b__[3] - b__[0] + 2 * g_, FL_Z0 - 1, z1_)
    else:                                                      # 排针: 方坑
        sh__ = BRepPrimAPI_MakeBox(gp_Pnt(b__[0] - g_, b__[1] - g_, FL_Z0 - 1), gp_Pnt(b__[3] + g_, b__[4] + g_, z1_)).Shape()
    _fd = cut(_fd, sh__)
    BRD_POCKETS.append(dict(bbox=[round(v, 2) for v in b__], top=round(z1_, 2), depth=round(z1_ - FL_Z0, 2), floor_in_cavity=round(CAV_Z0 - z1_, 2)))
LOG['board_pockets'] = BRD_POCKETS
_irt = rotz(IR_ANG)
IR_WIN = xf(cyl(IR_R, 0, IR_WIN_D, FL_Z0 - 1, FL_TOP + 1), _irt)                  # 定子盘通光孔 (贯穿)
_fd = cut(_fd, IR_WIN)
LOG['ir_tx'] = dict(ang=IR_ANG, r=IR_R, win_d=IR_WIN_D, led_top=FL_Z0 + IR_LED_H)
flange_disc = clean(_fd)
_mf2 = mounting_flange                             # 11-12 外径回原 Φ170: 保留 V0.4 原外裙 r82.5–85 (已同步短到 z9.3 = 定子盘底); 原先 cut ann(82.8,86) 是错的, 还留 0.3 薄片
for x, y in _V04_OUT: _mf2 = fuse(_mf2, cyl(x, y, CB7 + 0.4, FL_TOP, MF_TOP))  # 原 r77.5 Φ7 沉孔 + 孔补实 (板内)
_mf2 = clean(_mf2)                                 # 11-17 晚: LID_R 改 r77.5 与原孔同轴, 不先 clean 直接挖会布尔失败 (体积 0)
for x, y in LID_SCREWS: _mf2 = cut(_mf2, cyl(x, y, 3.2, 0, 30), cyl(x, y, CB7, MF_TOP - MF_CB, 40))   # 上盖 r79: Φ3.2 + 顶面 Φ7×1.5
# 11-17 用户: 安装法兰不再给 XT60 开缺口 (外裙整圈); 改由 XT60 压块 V1.2-h 在全局 Z8 以上削到接头尾 r85.8 (原 11-13 此处 cut 压块外形 +0.5, Z≤13.5)
_mf2 = cut(_mf2, xf(cyl(IR_R, 0, IR_WIN_D, FL_TOP - 1, MF_TOP + 1), rotz(IR_ANG)))   # 11-23 光电对射通光窗 (与定子盘通光孔同轴)
mounting_flange = clean(_mf2)
# 11-23 光电发射板压片 ir_clamp_v1_2 (打印, 夹在定子盘底面与 2 颗 B 螺丝的下挂法兰螺母之间): 弧形条 r IR_CL_R0–R1 + 两端圆垫,
#   顶面 (贴定子盘底) 开板槽: 全板外形深 IR_PCB_T (板顶面齐定子盘底), 电阻处再深 IR_BOT_H+IR_BOT_GAP; 板槽底长 2 个定位销插板 NPTH 孔; 板内端伸出压片内边, 焊盘露在外直接焊线 (11-23 取消出线孔/槽)。外形关于 IR_ANG 对称。
_ia = lambda xy: math.degrees(math.atan2(xy[1], xy[0])) % 360
IR_CL_HOLES = sorted(sorted(LID_SCREWS, key=lambda p: abs((_ia(p) - IR_ANG + 180) % 360 - 180))[:2], key=_ia)   # 离板最近的 2 颗 B 孔
_a0, _a1 = _ia(IR_CL_HOLES[0]), _ia(IR_CL_HOLES[1])
_cz0, _cz1 = FL_Z0 - IR_CL_T, FL_Z0
_cl = cut(cyl(0, 0, 2 * IR_CL_R1, _cz0, _cz1, ang=_a1 - _a0, a0=_a0), cyl(0, 0, 2 * IR_CL_R0, _cz0 - 1, _cz1 + 1))
_cl = fuse(_cl, *[cyl(x, y, IR_CL_PAD_D, _cz0, _cz1) for x, y in IR_CL_HOLES])
_irbp = lambda u, v: (IR_R + v - IR_LED_UV[1], u - IR_LED_UV[0])                     # 板局部 (u, v) → LED 局部 (径向 x, 切向 y), 再转 IR_ANG
_bx0, _by0 = _irbp(0, 0); _bx1, _by1 = _irbp(IR_PCB_L, IR_PCB_W)                     # 板外形 (x 径向 r69.1–79.1, r5)
_zb = _cz1 - IR_PCB_T                                                                 # 板底面 (销根)
_rc = _irbp(*IR_R_UV); _rhx, _rhy = IR_FP[0] / 2 + IR_REL_M, IR_FP[1] / 2 + IR_REL_M    # 电阻沿 v ⇒ 局部 x 为长边
if IR_FP_ALONG_U: _rhx, _rhy = _rhy, _rhx                                             # r4: 长轴沿 u ⇒ 局部 y (切向) 为长边
_ex, _ey = (0.4, 0.8) if IR_FP_ALONG_U else (0.8, 0.4)                                # 0603 本体 1.6×0.8 半宽 (局部 x 径向, y 切向)
_rx0 = _rc[0] - _rhx if _rc[0] - _rhx - IR_CL_R0 >= 0.8 else IR_CL_R0 - 1             # 电阻槽内端离压片内边 <0.8 ⇒ 直接开通 (免 0.15 薄片)
IR_CL_POCKET = xf(fuse(gbox(_bx0 - IR_CLR, _by0 - IR_CLR, _zb, _bx1 + IR_CLR, _by1 + IR_CLR, _cz1 + 1),                                # 板槽 (板顶面齐压片顶 = 定子盘底; 内端穿出压片内边)
                       gbox(_rx0, _rc[1] - _rhy, _zb - IR_BOT_H - IR_BOT_GAP, _rc[0] + _rhx, _rc[1] + _rhy, _cz1 + 1)), _irt)   # 底面电阻让位槽
_cl = cut(_cl, IR_CL_POCKET, *[cyl(x, y, IR_CL_HOLE_D, _cz0 - 1, _cz1 + 1) for x, y in IR_CL_HOLES], *[cyl(x, y, IR_CL_NUT_CB_D, _cz0 - 1, _cz1 - IR_CL_PAD_T) for x, y in IR_CL_HOLES])
IR_PINS = [xf(cyl(*_irbp(*q), IR_PIN_D, _zb - 0.01, _zb + IR_PIN_H), _irt) for q in IR_PIN_HOLES]   # 定位销 (从板槽底长出; r5 只插 H1/H2)
ir_clamp = clean(fuse(_cl, *IR_PINS))
_lc = _irbp(*IR_LED_UV)
IR_PCB = xf(fuse(cut(gbox(_bx0, _by0, _zb, _bx1, _by1, _cz1), *[cyl(*_irbp(*q), IR_HOLE_D, _zb - 1, _cz1 + 1) for q in IR_HOLES_UV]),   # 板 (顶面贴定子盘底, 带 NPTH 孔)
                 gbox(_rc[0] - _ex, _rc[1] - _ey, _zb - IR_BOT_H, _rc[0] + _ex, _rc[1] + _ey, _zb),                                   # 底面电阻本体 1.6×0.8
                 gbox(_lc[0] - _ex, _lc[1] - _ey, _cz1, _lc[0] + _ex, _lc[1] + _ey, _cz1 + IR_LED_H)), _irt)   # 顶面 LED (本体 IR_LED_L×IR_LED_W, 同电阻方向)
_ca, _sa = math.cos(math.radians(IR_ANG)), math.sin(math.radians(IR_ANG))
IR_PADS_XY = [(_irbp(*q)[0] * _ca - _irbp(*q)[1] * _sa, _irbp(*q)[0] * _sa + _irbp(*q)[1] * _ca) for q in IR_PADS_UV]   # 焊盘世界坐标 (露在压片内边外, 焊线从这里往下)
IR_WIRE_XY = tuple(sum(p[i] for p in IR_PADS_XY) / len(IR_PADS_XY) for i in (0, 1))
LOG['ir_clamp'] = dict(holes=[round(_ia(p), 1) for p in IR_CL_HOLES], t=IR_CL_T, pad_t=IR_CL_PAD_T, z=(_cz0, _cz1), r=(IR_CL_R0, IR_CL_R1), v=round(vol(ir_clamp), 1), screw_L=IR_CL_SCREW_L,
                       pcb=(IR_PCB_L, IR_PCB_W, IR_PCB_T), pads_xy=[[round(v, 2) for v in p] for p in IR_PADS_XY])
seat = clean(s_); LOG['seat'] = dict(v=vol(seat), z_g=Z_G)          # 合并版 (下罩+外卡一体)
# 分体版 (用户 11-11): 外卡三角区单独一个环, 玻璃先套内卡再从上套环; 环底 2x2 凸筋插下罩顶槽 (单边 0.1)
TG_R0, TG_W, TG_H, TG_CLR = 105.0, 2.0, 2.0, 0.1   # 11-17 晚 用户: 凸筋改到玻璃座 (upper) 顶面, 外卡环底开槽; r104 → 105 让开外移后的 J 沉孔 (外缘 r103.9, 隔 1.1)
_lip = ann(go, SH_OUT + 1, Z_G, Z_G + OUT_DEPTH + 1)
clamp_ring = clean(cut(op(BRepAlgoAPI_Common, seat, _lip), ann(TG_R0 - TG_CLR, TG_R0 + TG_W + TG_CLR, Z_G - 1, Z_G + TG_H + TG_CLR)))   # 底面槽
shroud_split = clean(fuse(cut(seat, _lip), ann(TG_R0, TG_R0 + TG_W, Z_G - 0.5, Z_G + TG_H)))                                      # 顶面凸筋
LOG['split'] = dict(ring=vol(clamp_ring), shroud=vol(shroud_split))
# 用户 11-14: 分体下罩太高, 做错要全部重来 ⇒ 在承载盘顶 Z32 横切成上下两段, 8×M3 锁 (上段沉孔往下; (二) 改穿通到下段底面法兰螺母)。
#   Z32 以下 = 原 32 高下罩 (三角块/筋/按键舌片 Z≤30/XT60 井/按键腔顶 Z23.3 都在下面), 以后改可视高度只重打上段。
#   对中: 下段顶面凸筋 r104–106 高 2 插上段底槽 (单边 0.1, 同外卡环); 螺丝 r98.5 @22.5°+45k (避开 +X XT60 / +Y 按键),
#   沉孔 Φ7 开在上段顶面 (玻璃座) 被玻璃端面 + 外卡环盖住; 拆: 外卡环 → 玻璃 → 8 螺丝 → 上段, 不用翻整机。
SPLIT_Z = Z_SHR_REF                                # 32.0
JN_N, JN_R, JN_ANG0 = 8, 99.5, 22.5               # 11-17 晚 用户: r98.5 沉孔内缘 r94.1 啃内卡根 0.7 ⇒ 外挪 1 (内缘 r95.1, 离内卡 0.3)
#   (旧 r98.5: 沉孔 Φ8.8 r94.1–102.9 下切内卡根 0.7, 离外卡环槽 r103.8 0.9)
# 用户 11-14 (二): 要真夹持 ⇒ 螺丝穿通上下两段。11-16 用户买到实物 (图): M4×50 超薄头 (头 Φ8.5×1.8, 2.5 六角) + M4 法兰螺母 (法兰 Φ9.7, 对边 6.9, 厚 4.3)
#   玻璃座顶面 Φ8.8 沉孔深 2.1 (头顶在玻璃底下 0.3); 底座底面圆窝 Φ9.8 深 4.6, 法兰螺母法兰朝上压入 (11-16 用户)
JN_D, JN_CB = 4.5, 8.8                             # M4 通孔 / 沉孔 (头 Φ8.5)
JN_L, JN_HH = 50.0, 1.8                            # M4×50 超薄头, 头厚 1.8
JN_BEAR = Z_G - 2.1                                # 沉孔深 2.1 ⇒ 支承 Z50.98, 头顶 Z52.78 (玻璃底下 0.3)
JN_TIP = JN_BEAR - JN_L                            # 尾端 Z1.08
JN_NUT_H, JN_NUT_FD = 4.3, 10.2                    # 11-19 用户: 底座 8 个 J 沉孔(螺母窝) 9.8→10.2; 11-16 用户: 螺母反过来 (法兰朝上), 法兰朝下会滑 ⇒ 底面圆窝 Φ9.8 (法兰 Φ9.7 压入, 打印偏小即紧配不掉)
JN_NUT_Z1 = 2.3 + JN_NUT_H                         # 用户 11-18: 窝再深 2 (4.6→6.6), 螺母 Z2.3..6.6, 尾 Z1.08 仍穿出螺母底; 原: 窝深 4.6 ⇒ 螺母 Z0.3..4.6, 法兰顶窝顶 (锯齿压窝顶止转), 啮合 3.62
JN_NUT_FZ = JN_NUT_Z1                              # 圆窝一通到顶 (法兰从下面塞进去要过整段, 做不了六角)
JN_NUT_AF = None
JN_NUT_D = JN_NUT_FD                               # 只用于校核
JN_PTS = [(JN_R * math.cos(math.radians(JN_ANG0 + 45 * k)), JN_R * math.sin(math.radians(JN_ANG0 + 45 * k))) for k in range(JN_N)]
RG_R0, RG_W, RG_H, RG_CLR = 104.0, 2.0, 2.0, 0.1   # 两段止口凸筋 (在下段顶)
assert JN_R - JN_CB / 2 >= gi + 0.3 and JN_R + JN_CB / 2 <= TG_R0 - 1.0, '沉孔碰内卡或顶面凸筋'   # 11-16 Φ8.8: 下切内卡根 0.7, 离槽 0.9
assert JN_R - JN_NUT_D / 2 >= SPIG_IN + 2 and JN_R + JN_NUT_D / 2 <= SH_OUT - 2, '螺母孔离墙面太近'
assert JN_R + JN_D / 2 <= RG_R0 - RG_CLR - 1.5, '通孔碰止口凸筋'
assert JN_BEAR + JN_HH <= Z_G - 0.3, '头顶碰玻璃'
assert JN_BEAR - SPLIT_Z >= 10, '上段沉孔下面肉太薄'
_lo_box = cyl(0, 0, 2 * SH_OUT + 10, -5, SPLIT_Z)
_s = cut(op(BRepAlgoAPI_Common, shroud_split, _lo_box), *[fuse(cyl(x, y, JN_D, -1, SPLIT_Z + 1), cyl(x, y, JN_NUT_FD, -1, JN_NUT_Z1)) for x, y in JN_PTS])
_kb = KEY['pocket_bbox']                           # 11-14: 按键让位腔竖直打通到 Z32 ⇒ 止口凸筋在按键段断开 (不然凸筋悬空跨腔)
shroud_lo = clean(fuse(_s, cut(ann(RG_R0, RG_R0 + RG_W, SPLIT_Z - 0.5, SPLIT_Z + RG_H), gbox(_kb[0] - 0.5, _kb[2], SPLIT_Z - 1, _kb[1] + 0.5, SH_OUT + 1, SPLIT_Z + RG_H + 1))))
_s = cut(shroud_split, _lo_box, ann(RG_R0 - RG_CLR, RG_R0 + RG_W + RG_CLR, SPLIT_Z - 1, SPLIT_Z + RG_H + RG_CLR))
for x, y in JN_PTS: _s = cut(_s, cyl(x, y, JN_D, SPLIT_Z - 1, JN_BEAR + 0.01), cyl(x, y, JN_CB, JN_BEAR, Z_G + 0.01))
shroud_hi = clean(_s)
LOG['split2'] = dict(split_z=SPLIT_Z, lo=vol(shroud_lo), hi=vol(shroud_hi), pts=[(round(x, 2), round(y, 2)) for x, y in JN_PTS], bear=JN_BEAR, tip=JN_TIP, nut_z1=JN_NUT_Z1)
tube = ann(GL_OD / 2 - GL_T, GL_OD / 2, Z_G, Z_G + GL_H)                     # 玻璃罩 OD200x5 高 245
# 4d 玻璃上 (顶盖, 用户 11-13): 玻璃上环 glass_top_v1_2 + 圆环玻璃 OD180/ID20/t10 (外购) + 中心卡扣堵头 glass_top_hub_v1_2
#    环 = 玻璃下镜像: 内卡 r90.8–94.8 + 外卡 r100.2–110 夹玻璃上端, 外面 r110 齐平; 内外卡同深 GT_DEPTH, 底面同高 ⇒ 正立打印两卡底落床, 无支撑
#    圆环玻璃坐环内 r90.3 窝 (径向定位) 的托台上 (靠自重; 托台下面 45° 斜, 可打印), 顶面低于环顶 GD_RECESS
#    堵头: 顶法兰压玻璃上面, 6 爪穿 Φ20 孔, 爪端 30° 倒钩钩玻璃下面 (一件, 无螺纹); 可选 688 轴承窝 (GT_BEARING)
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon as _MP, BRepBuilderAPI_MakeFace as _MF
def revol(rz):                                     # (r,z) 闭合折线绕 Z 轴转一圈
    pg = _MP()
    for r, z in rz: pg.Add(gp_Pnt(r, 0, z))
    pg.Close()
    return BRepPrimAPI_MakeRevol(_MF(pg.Wire()).Face(), gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2 * math.pi).Shape()
Z_GT = Z_G + GL_H                                  # 玻璃上端 (11-13 晚 Z_G 53.08 ⇒ 298.08; 原 277.0)
GT_DEPTH = 12.8                                    # 内/外卡深 (玻璃下 20/10; 这里同深, 底面同高好打印); 11-17 压圈: 12 → 12.8 (托台下移 0.8 放底垫, 45° 斜面要这 0.8)
GT_TOP_T = 5.6                                     # 玻璃端面以上板厚 (11-17 压圈: 4 → 4.6; 11-17 晚 用户红/绿分件: 再 +1 → 5.6, 铜螺母底下留 1.4; 圆环玻璃 Z 不动)
GT_Z0, GT_Z1 = Z_GT - GT_DEPTH, Z_GT + GT_TOP_T    # 265 / 281
assert Z_SCR1 + 3.0 <= GT_Z0, f'灯板上沿 Z{Z_SCR1} 离玻璃上最低处 Z{GT_Z0} 不足 3'
LOG['screen'] = dict(z_board=(Z_SCR0, Z_SCR1), z_led0=round(Z_LED0, 2), z_view0=round(Z_VIEW0, 2), z_g=Z_G, z_gt=Z_GT, top_clear=round(GT_Z0 - Z_SCR1, 2), min_gl_h=round(Z_SCR1 + 3.0 + GT_DEPTH - Z_G, 2))
GT_FOOT = 1.0                                      # 外卡底平带 (r100.2–101.2, 落床), 斜面 → r110 处
GT_CH = 1.0                                        # 顶面外缘倒角
GD_OD, GD_ID, GD_T = 180.0, 20.0, 10.0             # 圆环玻璃 (用户 11-13: t5 → t10)
# 11-17 用户: 圆环玻璃要夹住 (原只靠自重) ⇒ 整圈压圈 glass_top_clamp_v1_2, 8×M3 锁到环顶铜螺母; 玻璃上下各垫 1 厚硅胶/TPU 环垫 r85.5–90,
#   压圈底面直接落在环顶 = 硬限位 ⇒ 垫子压缩量固定 GK_COMP (拧多紧都不会再多压玻璃); 上下垫同半径 ⇒ 玻璃只受压不受弯
GK_T, GK_COMP = 1.0, 0.2                           # 环垫厚 / 压缩率 (压后 0.8)
GK_H = GK_T * (1 - GK_COMP)                        # 0.8
GC_LIP = 1.0                                       # 11-17 晚: 外件 (绿) 底面凸缘伸进玻璃窝 1 压上垫 (环顶加厚 1 而玻璃不动)
GD_CLR, GD_RECESS = 0.3, GK_H + GC_LIP             # 玻璃窝径向单边 / 玻璃顶低于环顶 (= 上垫压后 + 凸缘; 原 0.2)
GD_Z1 = GT_Z1 - GD_RECESS                          # 280.8
GD_Z0 = GD_Z1 - GD_T                               # 291.88 (11-17 前后不变)
GT_LEDGE_Z = GD_Z0 - GK_H                          # 托台顶 291.08 (下垫压后 0.8); 窝深 11.6
GD_POCKET_R = GD_OD / 2 + GD_CLR                   # 90.3
GT_LEDGE_R, GT_LEDGE_V = 85.5, 0.5                 # 托台内缘 r85.5 (搭玻璃 4.5), 内缘直边 0.5, 下面 45° 斜回内卡内面
_gin = gi - SPIG_T                                 # 90.8
assert (GT_LEDGE_Z - GT_LEDGE_V - GT_Z0) >= (_gin - GT_LEDGE_R) - 1e-6, '托台底面要 ≥45° (正立打印免支撑)'
# 11-17 晚 用户草图: 玻璃上拆红/绿两件 —— 红 (本件 glass_top_v1_2) = 内卡 + 托台/玻璃窝 + 盖过玻璃罩端面到 r100.1 (坐在端面上);
#   绿 (glass_top_clamp_v1_2) = 顶板 (压玻璃) + 外卡 一体; 螺丝从绿顶面往下进红件桥上的铜螺母 (在玻璃罩壁正上方)
GT_RO = go - 0.1                                   # 红件外面 r100.1 (绿件内面 r100.2, 嵌套单边 0.1)
GT_RZ = [(_gin, GT_Z0), (gi, GT_Z0), (gi, Z_GT), (GT_RO, Z_GT), (GT_RO, GT_Z1),
         (GD_POCKET_R + 0.5, GT_Z1), (GD_POCKET_R, GT_Z1 - 0.5),                       # 窝口 0.5 倒角 (放玻璃)
         (GD_POCKET_R, GT_LEDGE_Z), (GT_LEDGE_R, GT_LEDGE_Z), (GT_LEDGE_R, GT_LEDGE_Z - GT_LEDGE_V)]
GT_CONE_DEG = math.degrees(math.atan2(Z_GT - LIP_EDGE - GT_Z0, SH_OUT - go - GT_FOOT))   # 外卡斜面与水平 (≥45 免支撑)
# 绿件 glass_top_clamp_v1_2: 顶板 r85.5 (= 托台内缘, 不多挡显示区) – r110 厚 3 (顶外缘倒角 1) + 底面凸缘 r85.5–90.0 高 1 压上垫 + 外卡 r100.2–110 (斜面同原)
#   8×M3×6 超薄头 (Φ7×1.5, 头在顶面) @22.5°+45k, r = 红件桥中线 (r90.8–100.1 中点) → 红件顶面 Φ4.2×4.2 铜螺母, 底下离玻璃罩端面 1.4
GC_R0, GC_T, GC_CH, GC_IN_CH = GT_LEDGE_R, 3.0, 1.0, 0.5
GC_LIP_R1 = GD_POCKET_R - 0.3                      # 凸缘外 r90.0 (玻璃窝 r90.3, 单边 0.3)
GC_Z0, GC_Z1 = GT_Z1, GT_Z1 + GC_T                 # 303.68 / 306.68 (顶板底 = 红件顶 = 硬限位)
GC_N, GC_R, GC_ANG0, GC_HOLE = 8, (gi - SPIG_T + 0.5 + GT_RO) / 2, 22.5, 3.4   # r95.45
GC_INS_D, GC_INS_H = 4.2, 4.2
GC_HEAD_D, GC_HEAD_H = 7.0, 1.5                    # M3 超薄头 Φ7×1.5 (头在绿件顶面)
GC_BEAR = GC_Z1                                    # 头支承 Z306.68
GC_SCREW_L = 6.0                                   # M3×6: 尾 Z300.68, 啮合 3.0, 尾离玻璃罩端面 2.6 (M3×8 只剩 0.6, 不用)
# 11-17 晚 用户: 铜螺母是「螺丝从对面穿通孔把螺母拉进来」装的 ⇒ 红件铜螺母孔底下打 Φ3.4 通孔到底面 (底面 Z298.08 = 坐玻璃罩端面那圈, 装玻璃前从下面够得着)
GT_INS_THRU = 3.4
GT_PULL_L = 6.0                                    # 拉装用螺丝: 从红件底面往上 M3×6 (过 1.4 + 进铜螺母 4.2, 尖出顶面 0.4), 用完拆掉
GC_PTS = [(GC_R * math.cos(math.radians(GC_ANG0 + 45 * k)), GC_R * math.sin(math.radians(GC_ANG0 + 45 * k))) for k in range(GC_N)]
assert GC_R - GC_INS_D / 2 >= GD_POCKET_R + 0.5 + 2.0 and GC_R + GC_INS_D / 2 <= GT_RO - 2.0, '铜螺母孔离红件桥两侧太近'
_ins_floor = GT_Z1 - GC_INS_H - Z_GT               # 铜螺母底 → 玻璃罩端面
assert _ins_floor >= 1.2, '铜螺母孔底离玻璃罩端面太薄'
assert GC_BEAR - GC_SCREW_L >= Z_GT + 2.0, '螺丝尖离玻璃罩端面太近'
glass_top = clean(cut(revol(GT_RZ), *[fuse(cyl(x, y, GC_INS_D, GT_Z1 - GC_INS_H, GT_Z1 + 1), cyl(x, y, GT_INS_THRU, Z_GT - 1, GT_Z1)) for x, y in GC_PTS]))
glass_top_clamp = clean(cut(revol([(GC_R0, GC_Z0 - GC_LIP), (GC_LIP_R1, GC_Z0 - GC_LIP), (GC_LIP_R1, GC_Z0), (go, GC_Z0), (go, GT_Z0), (go + GT_FOOT, GT_Z0),
                                   (SH_OUT, Z_GT - LIP_EDGE), (SH_OUT, GC_Z1 - GC_CH), (SH_OUT - GC_CH, GC_Z1), (GC_R0 + GC_IN_CH, GC_Z1), (GC_R0, GC_Z1 - GC_IN_CH)]),
                            *[cyl(x, y, GC_HOLE, GT_Z0 - 1, GC_Z1 + 1) for x, y in GC_PTS]))
glass_gasket_bot = ann(GT_LEDGE_R, GD_OD / 2, GT_LEDGE_Z, GD_Z0)               # 外购/裁切 硅胶垫 OD180×ID171×1 (画压后 0.8)
glass_gasket_top = ann(GT_LEDGE_R, GD_OD / 2, GD_Z1, GD_Z1 + GK_H)
glass_disc = ann(GD_ID / 2, GD_OD / 2, GD_Z0, GD_Z1)                           # 外购圆环玻璃 (装配用实体)
# 中心堵头 (一件): 顶法兰 Φ32 压玻璃顶; 管 r8.2–9.8 穿 Φ20 孔 (单边 0.2); 孔下 30° 倒钩到 r11 (钩 1.0), 45° 导入到 r9; 6 条 2 宽槽 → 6 爪
GT_BEARING = bool(int(os.environ.get('GT_BEARING', '1')))   # 11-14: 灯板顶轴进 688 ⇒ 默认开轴承窝   # 默认堵头; 1 = 法兰内开 688 轴承窝 (Φ8 轴从下穿爪内孔进来)
GH_FL_D, GH_FL_T = 32.0, 3.0
GH_R0, GH_R1 = 8.2, GD_ID / 2 - 0.2               # 爪内 r8.2 (Φ16.4 > 688 外径 16, 轴承可从下穿进窝) / 外 r9.8
GH_BARB, GH_CATCH_DZ, GH_TIP_R = 1.0, 0.7, 9.0     # 倒钩外 r = 10 + 1.0; 钩面 30° (Δz 0.7); 导入 45° 到 r9
GH_SLOTS, GH_SLOT_W = 6, 2.0
BRG_D, BRG_H, BRG_ROOF = 16.1, 5.0, 4.0            # 688 = 8×16×5; 窝 Φ16.1 (打印孔偏小, 试配); 11-15: 顶 1.5 → 4.0, 内开 Φ9×2.5 让轴过冲 (玻璃长度公差)
BRG_RELIEF_D, BRG_RELIEF_H = 9.0, 2.5
_fl_t = (BRG_H + BRG_ROOF) if GT_BEARING else GH_FL_T
_rb = GD_ID / 2 + GH_BARB                          # 11.0
_zc = GD_Z0 - GH_CATCH_DZ                          # 钩面外端
_zt = _zc - 0.5 - (_rb - GH_TIP_R)                 # 爪尖底
GH_RZ = [(GH_R0, _zt), (GH_TIP_R, _zt), (_rb, _zc - 0.5), (_rb, _zc), (GH_R1, GD_Z0), (GH_R1, GD_Z1),
         (GH_FL_D / 2, GD_Z1), (GH_FL_D / 2, GD_Z1 + _fl_t - 1.0), (GH_FL_D / 2 - 1.0, GD_Z1 + _fl_t), (0, GD_Z1 + _fl_t), (0, GD_Z1), (GH_R0, GD_Z1)]
_gh = revol(GH_RZ)
GH_SLOT_TOP = GD_Z1 - 1.0                          # 槽顶 (法兰下 1), 爪自由长
for k in range(GH_SLOTS):
    _gh = cut(_gh, xf(gbox(-GH_SLOT_W / 2, 0, _zt - 1, GH_SLOT_W / 2, 20, GH_SLOT_TOP), rotz(30 + 360 / GH_SLOTS * k)))
if GT_BEARING:
    _gh = cut(_gh, cyl(0, 0, BRG_D, GD_Z1 - 0.01, GD_Z1 + BRG_H), cyl(0, 0, BRG_RELIEF_D, GD_Z1 + BRG_H - 0.01, GD_Z1 + BRG_H + BRG_RELIEF_H))
glass_top_hub = clean(_gh)
GH_L = GH_SLOT_TOP - _zt
GH_STRAIN = 1.5 * (GH_R1 - GH_R0) * GH_BARB / GH_L ** 2   # 悬臂根部应变 ≈ 1.5·t·δ/L²
LOG['glass_top'] = dict(v=vol(glass_top), z=(GT_Z0, GT_Z1), z_tube_top=Z_GT, cone_deg=round(GT_CONE_DEG, 1), disc_z=(GD_Z0, GD_Z1), disc_mass_g=round(vol(glass_disc) * 2.5e-3),
                        hub_v=vol(glass_top_hub), hub_z=(round(_zt, 2), GD_Z1 + _fl_t), finger_L=round(GH_L, 2), finger_strain=round(GH_STRAIN, 4), bearing=GT_BEARING,
                        valid=(BRepCheck_Analyzer(glass_top).IsValid(), BRepCheck_Analyzer(glass_top_hub).IsValid(), BRepCheck_Analyzer(glass_top_clamp).IsValid()),
                        clamp_v=vol(glass_top_clamp), clamp_z=(GC_Z0, GC_Z1), ledge_z=GT_LEDGE_Z, gasket=(GK_T, GK_COMP), clamp_pts=[(round(x, 2), round(y, 2)) for x, y in GC_PTS],
                        ins_floor_meat=round(_ins_floor, 2), screw_tip=GC_BEAR - GC_SCREW_L, screw_engage=round(GT_Z1 - (GC_BEAR - GC_SCREW_L), 2))
nuts = []
seat_nuts = [cyl(x, y, SH_NUT_D, NUT_Z0, NUT_Z0 + NUT_T) for x, y in SH_M6]
hang_nuts = [cyl(x, y, 6.35, FL_Z0 - 2.4, FL_Z0) for x, y in OUT_HANG]          # M3 螺母 (对角 6.35 x 2.4) 吊在定子盘底
hang_tips = [cyl(x, y, 3.0, MF_TOP - MF_CB - 8.0, FL_Z0) for x, y in OUT_HANG]   # M3x8 螺杆 (头座沉孔底)
LOG['hang'] = OUT_HANG
_bp = gp_Pnt(36.3, 26.75, 0).Transformed(BT); LOG['button_r'] = math.hypot(_bp.X(), _bp.Y())

# ---------------- 5 电机占位 / 立柱 ----------------
motor = fuse(cyl(0, 0, MOTOR_D, MOTOR_Z0, ROTOR_TOP), cyl(0, 0, BOSS_D, ROTOR_TOP, ROTOR_TOP + BOSS_H))
posts = [cyl(x, y, POST_D, 0, POST_H) for x, y in POSTS]

# ---------------- 6 顶轴承架 (V0.4) + 滑片 ----------------
fa = one(SRC / 'frame_A_v4_raw.step'); fb = one(SRC / 'frame_B_v4_raw.step')
ang0 = math.degrees(math.atan2(37.5, 87.5))      # 23.199
tA = rotz(90 + ang0); tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, 360)); frameA = xf(xf(fa, tA), tz)
fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
tz2 = gp_Trsf(); tz2.SetTranslation(gp_Vec(0, 0, 376)); frameB = xf(xf(xf(fb, fx), rotz(270 + ang0)), tz2)
vane = xf(one(O10 / 'vane_slider_v4_trimmed.step'), rotz(D_ANG))

for k, s in dict(collar=collar, hub=hub, rim=rim, disc=disc, frameA=frameA, frameB=frameB).items():
    LOG.setdefault(k, {})['valid'] = BRepCheck_Analyzer(s).IsValid(); LOG[k]['bbox'] = [round(v, 2) for v in bbox(s)]

# ---------------- 整机 ----------------
NEW = [  # name, shape, color, 打印?
    ('base_disc_D220x6_v1_2', disc, '#8a8f98', 'disc'),
        ('hub_disc_v1_2', hub, '#4f86c6', 'hub'),
    ('rim_ring_v1_2_D170', rim, '#6aa84f', 'rim'),
    ('motor_placeholder_D55x21.5', motor, '#444444', None),
    ('frame_A_v4', frameA, '#c27ba0', 'frameA'),
    ('frame_B_v4', frameB, '#a64d79', 'frameB'),
    ('vane_slider_v4_trimmed_rot-12.3', vane, '#e06666', None),
] + [('key_bracket_v1_2', key_bracket, '#f1c232', None), ('key_board_v1_2_simple', key_board, '#2e7d32', None)] + ([('mos_clamp_v1_2', CD.clamp, '#e69138', None)] if CD.HAS_MC else []) + ([('cap_clamp_v1_2', CD.cap_clamp, '#b45f06', None)] if CD.HAS_CC else []) + [(f'post_D8x360_{i}', p, '#bbbbbb', None) for i, p in enumerate(posts)]
DROP = {'baseplate_collar_v4', 'motor_placeholder', 'hub_disc_v1_0', 'rim_ring_v1_0'}
KEEP_O10 = ['M6x20_screw_rotor', 'standoff_D8x45_rotor', '688_lower_frame_A', '688_upper_frame_B']
PAL = ['#f6b26b', '#76a5af', '#93c47d', '#ffd966', '#8e7cc3', '#b4a7d6', '#a2c4c9', '#ea9999']
old_items = []
import os
for i, f in enumerate([] if (os.environ.get('NOOLD') or not OLDPARTS) else sorted((Path(OLDPARTS) / '零件_V1.0与V1.1通用').glob('*.step'))):
    if f.stem in DROP: continue
    old_items.append((f.stem, one(f), PAL[i % len(PAL)]))
for f in ([] if (os.environ.get('NOOLD') or not OLDPARTS) else KEEP_O10): old_items.append((f, one(Path(OLDPARTS) / '零件_仅V1.0' / f'{f}.step'), '#cccccc'))
if __name__ == '__main__':
    items = [(n, s, col, None, False) for n, s, col, _ in NEW] + [(n, s, col, None, len(solids(s)) > 20) for n, s, col in old_items]
    for n, s, col, _ in NEW:
        write_doc([(n, s, col, None, False)], OUT / '零件' / f'{n}.step', n)
    write_doc(items, OUT / 'V1.2_整机.step', 'POV3D_V1.2')
    # 打印 STL (打印姿态, 落床 z=0)
    POSE = { 'disc': None, 'collar': None, 'hub': None, 'rim': 'flip', 'frameA': None, 'frameB': 'flip'}
    for n, s, col, k in NEW:
        if not k: continue
        t = s
        if POSE[k] == 'flip': t = xf(t, fx)
        z0 = bbox(t)[2]; tt = gp_Trsf(); tt.SetTranslation(gp_Vec(0, 0, -z0)); t = xf(t, tt)
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(OUT / '打印STL' / f'{n}.stl'))
    # 线圈驱动板 MOS 压块 / 电容卡件: 打印件 (STL/STEP) 由各自生成器 scripts/mos_clamp_v1_2.py / cap_clamp_v1_2.py 出到 models/<名>/, 这里只并进装配
    import pickle
    pickle.dump(dict(new=[(n, k) for n, _, _, k in NEW]), open(OUT / 'names.pkl', 'wb'))
    json.dump(LOG, open(OUT / 'log.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(LOG, indent=1, ensure_ascii=False))
