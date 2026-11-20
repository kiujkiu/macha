"""V2 灯板支撑 (11-14 定 V0.4 portal 改; 11-16 按新转子布局重做: 灯板下沿 Z37, 底板在 +y, 无线模块在 −y;
11-16 晚 用户: 灯板下端沿用 V0.4 —— 夹条托在两板之间, 竖直螺丝从下往上锁;
11-16 晚 方案 A (转子曾改 Φ175, 同晚改回 Φ170, 其余保留): 整组灯板沿 y 平移 B.SCR_ECC (−4.36, 板 A MIP 顶面落在转轴 y=0); 中间 T 件取消; 两端立板脚改耳朵, 锁外圈锁盘螺丝)。
    cd v1.2/scripts && ../../.venv/bin/python led_support_v1_2.py
世界坐标 (同 build_v1_2): Z0 = 底盘顶, 承载盘顶 Z32 (r<24.5 毂盘顶 Z30.4), 灯板下沿 B.Z_SCR0 = 37 / 上沿 245.0; 灯板面平行 XZ。
两块 LED_V0.2.0 背靠背 (间隙 4.6 = 铜柱, 用户 11-14), 整组中面在 y = ECC = B.SCR_ECC:
  板 A F 面 y=ECC+2.3 = −2.06, LED 面 −0.592 (朝 +y, MIP 顶 y=0); 板 B = 板 A 绕 (0, ECC) 转 180°: F 面 −6.66, LED 面 −8.128, MIP 顶 −8.72。
  下面 "局部坐标" = 灯板组坐标 (中面 y=0), 建好再整体 tr(0, ECC, 0); 转轴 Φ8 / 轴座 / 梳齿环 / 耳朵螺丝 用世界坐标。
零件 (打印, PETG/PLA):
  led_bar_v1_2     夹条: 夹在两板 F 面之间 (厚 4.6), Z37–46, 两端 |x|≥68 加高到 Z54; H1/H2 (±78.63, Z41) M3 横穿 板-条-板;
                   底面 2 个 Φ2.6 竖孔 (x ±73, 局部 y=0) 给立板来的 M3×8 自攻 (中间 ±38 两孔随中间 T 件取消); F 面器件处挖浅槽
  led_post_a_v1_2  +x 端立板: 横杆 x69–77 局部 |y|≤14 Z32–37 托夹条/灯板下沿 + 耳朵 (Z32–36, 厚 4) 沿 y 伸到 22.5°/−22.5° 两颗
                   外圈锁盘螺丝 (B.RH_EAR_PTS k=0/7, r79) ⇒ M3×14 头压耳朵顶 Z36, 穿承载盘进毂盘底铜螺母 (B.RH_INS); 耳朵外缘 ≤ r81.7;
                   腹板 局部 |y|≤9.75 x77→82.0 连竖贴天线板 (在罩壁缝里, r≤ANT_R_MAX); 底面沉孔 M3×8 往上锁夹条
  led_post_b_v1_2  −x 端立板 (x 镜像, 耳朵锁 157.5°/202.5° k=3/4)
  led_top_v1_2     顶部件: 舌 (上中窗) + 帽压两板上沿 (随灯板平移) + Φ14 轴座 (留在转轴 (0,0), 帽下加 Φ16 圆垫跨过去), 压 Φ8×50 钢轴; 帽上 2×M3×4 铜螺母锁梳齿
  led_comb_v1_2    顶部配平梳齿: 环套轴座 (0,0), 横梁/齿随灯板平移, 坐帽顶 (2×M3×8 锁帽), 每侧 4 个齿 (沿 y), 每齿 4 个 Φ3.4 竖孔挂 M3 螺丝+螺母配重
装法: 桌上先把灯板 A/B + 夹条用 H1/H2 两颗 M3 横穿夹好, 再把两端立板从下面用 2×M3×8 锁到夹条上;
      整体放上转子, 从上面拧耳朵 4×M3×14 (穿承载盘, 进毂盘底铜螺母; 这 4 颗兼锁盘)。
外购: Φ8×50 钢轴 (h6), 688ZZ; M3×14 内六角 ×4 (耳朵, 毂盘底 M3×4 铜螺母由锁盘螺丝那套出);
      M3×8 内六角 ×2 (立板 → 夹条, 自攻); M3×12 内六角 ×2 + M3 法兰螺母 ×2 (H1/H2); M3×8 内六角 ×2 + M3×4 铜螺母 ×2 (梳齿 → 帽); 配重 M3×8 + M3 螺母 (按需);
      WiFi 天线 18.5×37.7 软板 (11-16 晚 用户) ×2 竖贴两端。
输出: v1.2/models/<件>/<件>.{step,stl} (装配坐标) + out/打印STL/<件>.stl (打印姿态);
      v1.2/models/led_support_v1_2/: 装配位 STEP + 干涉/平衡报告 led_support_report.json
"""
import io, contextlib, json, math, sys
from pathlib import Path
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
import v2_boards_v1_2 as V
from helpers import read_step, write_doc
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec, gp_Ax2, gp_Dir, gp_Ax1
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz
OUT = B.V12 / 'models' / 'led_support_v1_2'; OUT.mkdir(parents=True, exist_ok=True)

def tr(dx, dy, dz): t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz)); return t
def ycyl(x, z, d, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), d / 2, y1 - y0).Shape()
def xcyl(y, z, d, x0, x1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), d / 2, x1 - x0).Shape()
def comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c
def common(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return o.Shape()
def common_v(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return vol(o.Shape()) if o.IsDone() else -1
def cog(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); p = g.CentreOfMass(); return g.Mass(), (p.X(), p.Y(), p.Z())

# ---------------- 灯板 / 间隙 ----------------
Z0 = B.Z_SCR0; Z1 = Z0 + 2 * V.LED_HALF_H          # 37.0 / 245.0075 (STEP 板高 208.0075; 帽底贴板上沿)
ECC = B.SCR_ECC                                   # −4.36: 整组灯板 (板/夹条/立板/天线/帽/梳齿横梁/FPC) 沿 y 平移; 转轴/轴座/梳齿环/耳朵螺丝不动
T_ECC = tr(0, ECC, 0)
GAP_HALF = 2.5                                    # 板 F 面 局部 y=±2.5 (间隙 5 = 铜柱, 用户 11-18 夜; 原 2.3 / 间隙 4.6, 11-14)
PCB_T = 1.6                                       # 用户 11-18 夜: 灯板厚 1.6 (STEP 仍是 1.468, 模型里板背离 F 面 0.132, 只影响显示); 原 1.468 按 STEP
Y_LED = GAP_HALF + PCB_T                          # LED 面 局部 y=±3.768 (世界 −0.592 / −8.128)
MIP_H = V.MIP_H                                   # MIP 高 0.59 ⇒ 板 A MIP 顶 世界 y = ECC + Y_LED + 0.59 ≈ 0
HALF_W = 81.879                                   # 板半宽
H1_X, H1_Z = 78.63, Z0 + 4.0                      # H1/H2 M3 (±78.63, 下沿+4 = Z41)
CLR = 0.1                                         # 立刀/舌 与板 F 面单边
BLADE_T = 2 * (GAP_HALF - CLR)                    # 4.4
RIM_TOP = B.Z_RIM_TOP                             # 32.0
HUB_TOP = 30.5                                    # 毂盘顶 (r<24.5; 11-16 晚 G 实测 30.5, 原写 30.4)
R_CLIP = 81.7                                     # 11-16 晚 改回 Φ170: 转子罩内壁 r82 ⇒ 罩内件外缘 ≤ r81.7 (Φ175 时曾 84.2); 腹板+天线板例外 (罩壁缝里, r≤ANT_R_MAX)

# ---------------- 两端立板: 耳朵脚 (11-16 晚 方案 A; 改回 Φ170 后耳朵切 r81.7) ----------------
# 原 T 脚 (END_T_HOLES (±74, ±10) M3×6 进承载盘顶铜螺母) 取消 ⇒ 立板根部沿 y 伸出两只耳朵, 盖住外圈锁盘螺丝 B.RH_EAR_PTS:
#   +x 立板 k=0 (22.5°) / k=7 (−22.5°), −x 立板 k=3 (157.5°) / k=4 (202.5°), r = B.RH_R = 79 ⇒ (±72.99, ±30.23)。
#   叠层: 螺丝头压耳朵顶 Z36 → 耳朵 Z32–36 (厚 4, Φ3.4 通孔, 无沉孔) → 承载盘 Φ3.4 → 毂盘底 M3×4 铜螺母 B.RH_INS (Z21.5–25.5)。
#   M3×14: 尾 Z22.0 (= B.RH_EAR_TIP_REC, 啮合 3.5, 不出毂盘底 Z21.5)。耳厚↔螺丝: 1.5–3 → M3×12, 3.5–5 → M3×14, 5.5–7 → M3×16。
#   耳朵只到 |y| = 30.23 + 3.5 = 33.73 / 极角 ≤ 25.1°, 让出 37°–43° 罩底凸台扇区 (@40°); x ≥ 69 > 底板 r4c x47.3 / −51.2。
#   改回 Φ170 (罩内壁 r82): 耳朵整体切到 R_CLIP = r81.7; 端头 Φ8 → Φ7 再切 r81.7 圆弧 ⇒ 孔外侧壁 81.7 − 79 − 1.7 = 1.0 (其余方向 ≥1.8);
#   M3×14 头 Φ5.5 (Z36–39) 外缘 r81.75 比耳朵外缘多悬 0.05, 离罩内壁 r82 = 0.25 (罩凸台在 40°, 耳朵/头处罩壁是光壁, 罩唇/盖在 Z66 以上)。
#   下面这些名字别的脚本 (build_drawings / fasteners / check / assembly_noglass) 在用, 名字沿用、含义改新。
EAR_T = 4.0                                       # 耳朵厚 (Z32–36)
EAR_Z1 = B.RH_EAR_Z0 + EAR_T                      # 36.0 = 螺丝头支承
EAR_PAD_D = 7.0                                   # 耳朵端头 Φ7 圆, 外侧再切 r81.7 圆弧 (改回 Φ170; Φ175 时 Φ8 外缘 r83)
FOOT_PTS = [tuple(p) for p in B.RH_EAR_PTS]       # 4 颗 (r79, 22.5/157.5/202.5/337.5°)
R_HOLE = B.RH_R                                   # 79.0
HUB_BOT = 21.5                                    # 毂盘底面
HUB_INS = tuple(B.RH_INS)                         # 毂盘底 M3×4 铜螺母 Z21.5–25.5 (锁盘螺丝那套, build 已切)
FOOT_SCREW_L = B.rh_ear_screw_len(EAR_T)          # 14.0 ⇒ M3×14
FOOT_CB_Z = EAR_Z1                                # 头支承 = 耳朵顶 Z36 (头 Z36–39)
FOOT_CB_D = 0.0                                   # 无沉孔 (名字留着置 0)
assert B.RH_EAR_TIP_Z[0] <= FOOT_CB_Z - FOOT_SCREW_L <= B.RH_EAR_TIP_Z[1], FOOT_CB_Z - FOOT_SCREW_L
assert FOOT_SCREW_L in (12.0, 14.0, 16.0), FOOT_SCREW_L
PAD_D = EAR_PAD_D                                 # 出图脚本用 = 孔位处实体宽
T_X = 73.0                                        # 横杆中线 (≈ 耳朵螺丝 x 72.99 / 夹条竖螺丝 x)
T_W = 8.0                                         # 横杆宽 (x 69–77)
FOOT_Y = 14.0                                     # 横杆半长 局部 |y|≤14 (世界 y −18.36…9.64), Z32–37
FOOT_X0, FOOT_X1 = T_X - T_W / 2, None            # 兼容旧名 (FOOT_X1 = ANT_X1, 下面定)
BLADE_X0, BLADE_X1, BLADE_Z1 = 75.6, 81.6, Z0 + 17.0   # (旧立刀尺寸, 出图脚本参考)
# 天线板: 两端都竖贴, 随灯板组 y 平移; 在转子罩壁缝里 (罩壁 r82–85)
#   改回 Φ170: 原 x82.6–84.3 偏心后外角 hypot(84.3, 14.11) = 85.47 > 84.9 会被切掉一角 (天线软板贴不全) ⇒ 整块往里挪 0.6 到 x82.0–83.7, 外角 84.88
ANT_X0, ANT_X1, ANT_HW = 82.0, 83.7, 9.75         # 厚 1.7, 局部 |y|≤9.75 ⇒ 世界 y −14.11…5.39 (Φ175 时 x82.6–84.3)
ANT_R_MAX = 84.9                                  # < 罩外圆 r85 (Φ175 时曾 87.4)
ANT_SZ = (37.7, 18.5)                             # 11-16 晚 用户: 实际天线 = 18.5×37.7 软板 (FPC), 长边沿 Z
ANT_L, ANT_W, ANT_REC = ANT_SZ[0] + 0.4, ANT_SZ[1] + 0.4, 0.3   # 定位浅槽 38.1×18.9×0.3 (背胶贴)
ANT_Z1_MAX = B.Z_VIEW0                            # 板顶不高于罩顶/顶盖 Z73.08
ANT_ZC = round(ANT_Z1_MAX - 1.3 - ANT_L / 2, 2)    # 52.73 ⇒ 槽 Z33.7–71.8
ANT_Z1 = ANT_ZC + ANT_L / 2 + 1.3                 # 板顶 Z73.08
ANT_Y = (round(ECC - ANT_HW, 3), round(ECC + ANT_HW, 3))   # 世界 y 范围 (转子罩缝按这个再各让 0.35)
ANT_A = dict(y=ANT_HW, y_world=ANT_Y, z0=RIM_TOP, z1=ANT_Z1, zc=ANT_ZC)   # 兼容旧名 (两端相同)
ANT_B = ANT_A
FOOT_X1 = ANT_X1
SCREW_H1_L = 12.0

# ---------------- 夹条 (11-16 晚 用户: 灯板下端沿用 V0.4 —— 托在下面, 竖直螺丝从下往上锁) ----------------
# 夹条 led_bar: 夹在两板 F 面之间 (厚 = 间隙 4.6, 零间隙), 下沿齐灯板下沿 Z37; 两端用板 H1/H2 (±78.63, Z41) M3 横穿 板-条-板;
#   F 面器件按包围盒 +0.3 挖浅槽; 2 个竖孔从底面往上 (M3 自攻进打印件), 只两端立板固定 (中间 T 件取消)
BAR_Z1 = Z0 + 9.0                                 # 46 (盖住 H1 Z41 / M2 Z40)
BAR_END_X, BAR_END_Z1 = 68.0, Z0 + 17.0           # |x|≥68 两端加高到 Z54 (盖下角 F.Mask 窗 下沿+7…17)
BAR_M2 = [(23.0, Z0 + 3.0), (-23.0, Z0 + 3.0)]    # 板下中 M2 孔 (±23, Z40): 夹条留 Φ2.4 通孔, 可选加 M2 横穿
BAR_TAP_D, BAR_TAP_H = 2.6, 8.0                   # 竖孔 Φ2.6 深 8 (M3 自攻)
BAR_SCR_X = [T_X, -T_X]                           # 竖螺丝 x (两端立板), 局部 y=0 (世界 y=ECC)
BAR_SCR_Y = ECC                                   # 世界 y
BAR_SCR_L = 8.0                                   # M3×8 内六角: 头在立板底面沉孔 (支承 Z35), 尾 Z43 (进夹条 6)
BAR_SCR_BEAR = RIM_TOP + 3.0                      # 35 (立板底面 Φ6×3 沉孔, 头 Z32–35)
FPC_T = 0.3
TONGUE_X = 2.8                                    # 顶部件立舌半宽 (上中 F.Mask 窗)

# ---------------- 顶部件 + 梳齿 ----------------
TOP_TONGUE_Z0 = Z1 - 13.7                         # 231.3 (上中窗 上沿−4…14)
CAP_X, CAP_Y, CAP_T = 14.5, 6.0, 4.0              # 帽 29×12×4 (局部, 随灯板平移; 加宽放梳齿 2×M3 铜螺母)
CAP_PAD_D = 16.0                                  # 11-16 晚 偏心: 帽下加 Φ16 圆垫 (世界 (0,0)), 托住留在转轴上的 Φ14 轴座 (帽本身只到 y=ECC+6=1.64)
BOSS_D = 14.0
HUB_TIP = B.LOG['glass_top']['hub_z'][0]          # 堵头爪尖底 Z288.68
BOSS_GAP = 3.0                                    # 轴座顶 ↔ 爪尖 (玻璃长短公差)
BOSS_Z1 = HUB_TIP - BOSS_GAP                      # 285.68 (轴座 Z249–285.7, 长 36.7; 原 28.5)
BRG_Z0 = B.GD_Z1; BRG_Z1 = BRG_Z0 + B.BRG_H       # 688 Z301.88–306.88
ROD_D, ROD_L = 8.0, 50.0                          # 11-16: Φ8×40 → Φ8×50 (轴座里压入 28.3, 原 18.3)
ROD_Z1 = BRG_Z1 + 0.5                             # 轴顶伸出轴承 0.5 (上面 Φ9×2.5 让位: 玻璃短 ≤2.0 不顶; 长 ≤4.5 仍有 0.5 啮合)
ROD_Z0 = ROD_Z1 - ROD_L                           # 257.38
ROD_HOLE_D = 7.85                                 # 压装孔 (打印孔偏小, 试配)
assert ROD_Z0 > Z1 + CAP_T + 2, ROD_Z0
COMB_Z0 = Z1 + CAP_T; COMB_T = 4.0; COMB_Z1 = COMB_Z0 + COMB_T   # 梳齿板 Z249.0–253.0, 坐帽顶
COMB_HOLE_D = BOSS_D + 0.2                        # 套轴座 Φ14.2 (嵌套单边 0.1)
COMB_RING_D = 22.0
COMB_BEAM_Y = 4.0
COMB_FIX_X = 10.5                                 # (局部 y=0 / 世界 y=ECC) 梳齿 → 帽 2×M3×8 (头 Φ5.5 外让轴座 r7.1), 帽里 Φ4.2×4 铜螺母 (穿通帽, 下面是两板间隙)
COMB_TEETH_X = [16.0, 26.0, 36.0, 46.0]           # 每侧 4 齿 (±x), 齿宽 6
COMB_TOOTH_W, COMB_TOOTH_Y = 6.0, 15.0            # 齿沿 y 局部 ±15 (横梁+齿随灯板平移 ECC, 环 Φ22 留在 (0,0))
COMB_SLOTS_Y = [6.5, 12.0]                        # 每齿 ±6.5 / ±12 四个 Φ3.4 竖孔 (配重 M3 螺丝竖装, 螺母在齿下 Z246.6–249 > 板上沿 245)
COMB_SCREW_MAX_L = COMB_Z1 - Z1                   # 配重螺丝尾端不低于板上沿 ⇒ 头下长 ≤ 8 (+每多叠 1 个螺母可 +2.4)


def post(sx):
    """sx=+1 → +x 端 (耳朵锁 k=0/7); −1 → −x 端 (x 镜像, k=3/4)"""
    def X(a, b): return (min(sx * a, sx * b), max(sx * a, sx * b))
    tx = X(T_X - T_W / 2, T_X + T_W / 2); wx = X(T_X + T_W / 2, ANT_X1); ax = X(ANT_X0, ANT_X1)
    # 局部 (灯板组) 坐标建横杆/腹板/天线板, 再平移 ECC
    bar_ = gbox(tx[0], -FOOT_Y, RIM_TOP, tx[1], FOOT_Y, Z0)                          # 横杆 Z32–37 (顶 = 灯板/夹条下沿, 托两板)
    wa = fuse(gbox(wx[0], -ANT_HW, RIM_TOP, wx[1], ANT_HW, Z0), gbox(ax[0], -ANT_HW, RIM_TOP, ax[1], ANT_HW, ANT_Z1))   # 腹板 + 天线板
    xb = sx * BAR_SCR_X[0]                                                            # 底面竖螺丝 → 夹条 (Φ3.4 通 + 底面 Φ6×3 沉孔)
    hb = fuse(cyl(xb, 0, 3.4, RIM_TOP - 1, Z0 + 1), cyl(xb, 0, 6.0, RIM_TOP - 1, BAR_SCR_BEAR))
    xo = sx * ANT_X1
    rec = gbox(min(xo - sx * ANT_REC, xo + sx * 1), -ANT_W / 2, ANT_ZC - ANT_L / 2, max(xo - sx * ANT_REC, xo + sx * 1), ANT_W / 2, ANT_ZC + ANT_L / 2)
    bar_, wa, hb, rec = (xf(v, T_ECC) for v in (bar_, wa, hb, rec))
    # 耳朵 (世界坐标): 横杆同宽 x69–77 沿 y 连到两颗锁盘螺丝, 端头 Φ8 圆; Z32–36 (头压顶面)
    pts = [(x, y) for x, y in FOOT_PTS if x * sx > 0]
    ys = sorted(y for _, y in pts)
    ear = fuse(gbox(tx[0], ys[0], RIM_TOP, tx[1], ys[-1], EAR_Z1), *[cyl(x, y, EAR_PAD_D, RIM_TOP, EAR_Z1) for x, y in pts])
    s = common(fuse(bar_, ear), cyl(0, 0, 2 * R_CLIP, RIM_TOP - 1, Z0 + 1))            # 罩内件 ≤ r81.7 (耳朵端头外侧成 r81.7 切弧)
    s = fuse(s, common(wa, cyl(0, 0, 2 * ANT_R_MAX, RIM_TOP - 1, ANT_Z1 + 1)))       # 腹板+天线板在罩壁缝里 ≤ ANT_R_MAX
    s = cut(s, hb, rec, *[cyl(x, y, 3.4, RIM_TOP - 1, Z0 + 1) for x, y in pts])      # 耳朵孔 Φ3.4 通 (无沉孔)
    return clean(s)


def bar(led_pair):
    """led_pair = 局部坐标的两块灯板 (中面 y=0); 返回局部坐标夹条 (外面再平移 ECC)"""
    s = gbox(-HALF_W, -GAP_HALF + 0.01, Z0, HALF_W, GAP_HALF - 0.01, BAR_Z1)   # 每面收 0.01: 零间隙贴 F 面, 免布尔假重叠
    for sx in (1, -1):
        s = fuse(s, gbox(min(sx * BAR_END_X, sx * HALF_W), -GAP_HALF + 0.01, Z0, max(sx * BAR_END_X, sx * HALF_W), GAP_HALF - 0.01, BAR_END_Z1))
    # F 面器件让位: 灯板 STEP 里伸进间隙 (|y|<2.3) 且在夹条高度内的件, 包围盒 +0.3
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    cuts = []
    for led in led_pair:
        e = TopExp_Explorer(led, TopAbs_SOLID)
        while e.More():
            b = bbox(e.Current())
            if b[3] - b[0] < 100 and b[2] < BAR_END_Z1 + 0.3 and b[5] > Z0 and b[1] < GAP_HALF - 0.01 and b[4] > -GAP_HALF + 0.01:
                cuts.append(gbox(b[0] - 0.3, max(b[1] - 0.3, -GAP_HALF - 1), b[2] - 0.3, b[3] + 0.3, min(b[4] + 0.3, GAP_HALF + 1), b[5] + 0.3))
            e.Next()
    if cuts: s = cut(s, *cuts)
    for sx in (1, -1): s = cut(s, ycyl(sx * H1_X, H1_Z, 3.4, -5, 5))
    for x, z in BAR_M2: s = cut(s, ycyl(x, z, 2.4, -5, 5))
    for x in BAR_SCR_X: s = cut(s, cyl(x, 0, BAR_TAP_D, Z0 - 1, Z0 + BAR_TAP_H))
    return clean(s), len(cuts)


def top_piece():
    loc = gbox(-TONGUE_X, -BLADE_T / 2, TOP_TONGUE_Z0, TONGUE_X, BLADE_T / 2, Z1 + 0.01)   # 舌 + 帽 (局部, 随灯板平移)
    loc = fuse(loc, gbox(-CAP_X, -CAP_Y, Z1, CAP_X, CAP_Y, Z1 + CAP_T))
    s = fuse(xf(loc, T_ECC), cyl(0, 0, CAP_PAD_D, Z1, Z1 + CAP_T))                   # 帽下圆垫跨到转轴 (0,0)
    s = fuse(s, cyl(0, 0, BOSS_D, Z1 + CAP_T - 0.01, BOSS_Z1))                        # 轴座留在 (0,0)
    s = cut(s, cyl(0, 0, ROD_HOLE_D, ROD_Z0, BOSS_Z1 + 1))
    for sx in (1, -1):                              # 梳齿锁帽: M3×4 铜螺母孔 Φ4.2 穿通帽 (下面是两板间隙 局部 |y|<2.3, 孔 r2.1)
        s = cut(s, cyl(sx * COMB_FIX_X, ECC, 4.2, Z1 - 1, Z1 + CAP_T + 0.01))
    return clean(s)


def comb():
    xm = COMB_TEETH_X[-1] + COMB_TOOTH_W / 2
    loc = gbox(-xm, -COMB_BEAM_Y, COMB_Z0, xm, COMB_BEAM_Y, COMB_Z1)                 # 横梁 + 齿 (局部, 随灯板平移)
    for sx in (1, -1):
        for tx_ in COMB_TEETH_X:
            loc = fuse(loc, gbox(sx * tx_ - COMB_TOOTH_W / 2, -COMB_TOOTH_Y, COMB_Z0, sx * tx_ + COMB_TOOTH_W / 2, COMB_TOOTH_Y, COMB_Z1))
    s = fuse(cyl(0, 0, COMB_RING_D, COMB_Z0, COMB_Z1), xf(loc, T_ECC))               # 环套轴座 (0,0)
    s = cut(s, cyl(0, 0, COMB_HOLE_D, COMB_Z0 - 1, COMB_Z1 + 1))
    for sx in (1, -1):
        s = cut(s, cyl(sx * COMB_FIX_X, ECC, 3.4, COMB_Z0 - 1, COMB_Z1 + 1))
    s = cut(s, *[cyl(x, y, 3.4, COMB_Z0 - 1, COMB_Z1 + 1) for x, y in COMB_SLOTS])
    return clean(s)


COMB_SLOTS = [(sx * tx_, ECC + sy * y) for sx in (1, -1) for tx_ in COMB_TEETH_X for y in COMB_SLOTS_Y for sy in (1, -1)]   # 世界坐标
post_a, post_b, top, comb_s = post(+1), post(-1), top_piece(), comb()
rod = cyl(0, 0, ROD_D, ROD_Z0, ROD_Z1)
brg = cut(cyl(0, 0, 16.0, BRG_Z0, BRG_Z1), cyl(0, 0, 8.0, BRG_Z0 - 1, BRG_Z1 + 1))

# ---------------- 外购件 ----------------
def sock(x, y, z_bear, L, down=True, axis='z', sy=1):
    """内六角 M3 (头 Φ5.5×3); axis z: 头在 z_bear 上方, 杆向下; axis y: 头在 y=z_bear 外侧 (sy 指向头)"""
    if axis == 'z':
        return fuse(cyl(x, y, 5.5, z_bear, z_bear + 3.0), cyl(x, y, 3.0, z_bear - L, z_bear + 0.01))
    yb = z_bear
    h = ycyl(x, y, 5.5, yb, yb + 3.0) if sy > 0 else ycyl(x, y, 5.5, yb - 3.0, yb)
    sh = ycyl(x, y, 3.0, yb - L, yb + 0.01) if sy > 0 else ycyl(x, y, 3.0, yb - 0.01, yb + L)
    return fuse(h, sh)
def fnut_y(x, z, yb, sy):
    """法兰螺母 (Φ7.6 法兰 ×1 + 六角 5.5 对边 → 圆 Φ6.35 简化), 法兰贴 yb, 朝 sy 方向长 3.7"""
    a, b = (yb, yb + sy * 1.0), (yb, yb + sy * 3.7)
    return fuse(ycyl(x, z, 7.6, min(a), max(a)), ycyl(x, z, 6.35, min(b), max(b)))
def ins(x, y, z0, z1, d=4.2): return cut(cyl(x, y, d, z0, z1), cyl(x, y, 3.0, z0 - 1, z1 + 1))

# H1/H2: 板 A (+y) LED 面在 x 67.7–76.3 有 5.9 高电解 (下沿+6…15); 板 B 转 180° 后它到 −x 端 −y 面
# ⇒ +x 端: 头 (Φ5.5) 在 +y, 法兰螺母在 −y; −x 端相反。(局部建, 平移 ECC)
h1 = []
for sx in (1, -1):
    sy_head = 1 if sx > 0 else -1
    h1.append(('M3×12 内六角 灯板 H1/H2', xf(sock(sx * H1_X, H1_Z, sy_head * Y_LED, SCREW_H1_L, axis='y', sy=sy_head), T_ECC)))
    h1.append(('M3 法兰螺母 灯板 H1/H2', xf(fnut_y(sx * H1_X, H1_Z, -sy_head * Y_LED, -sy_head), T_ECC)))
# 耳朵 4 颗 = 外圈锁盘螺丝 k=0/3/4/7 (兼锁盘): M3×14 头压耳朵顶 Z36, 尾 Z22, 进毂盘底 M3×4 铜螺母 (Z21.5–25.5)
foot_scr = [(f'M3×{FOOT_SCREW_L:g} 内六角 立板耳朵 (兼锁盘)', sock(x, y, FOOT_CB_Z, FOOT_SCREW_L)) for x, y in FOOT_PTS]
foot_ins = [('M3×4 铜螺母 毂盘底 立板耳朵', ins(x, y, *HUB_INS)) for x, y in FOOT_PTS]
bar_scr = [('M3×8 内六角 立板→夹条 (从下往上)', fuse(cyl(x, BAR_SCR_Y, 5.5, BAR_SCR_BEAR - 3.0, BAR_SCR_BEAR), cyl(x, BAR_SCR_Y, 3.0, BAR_SCR_BEAR - 0.01, BAR_SCR_BEAR + BAR_SCR_L))) for x in BAR_SCR_X]
comb_scr = [('M3×8 内六角 梳齿→帽', sock(sx * COMB_FIX_X, ECC, COMB_Z1, 8.0)) for sx in (1, -1)]
comb_ins = [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, ECC, Z1, Z1 + CAP_T)) for sx in (1, -1)]
# 天线 (18.5×37.7×0.15 软板), 外面 x=±(ANT_X1 − 0.3); 局部建, 绕 (0, ECC) 转 180° 得 −x 那片
_ant = gbox(ANT_X1 - ANT_REC, -ANT_SZ[1] / 2, ANT_ZC - ANT_SZ[0] / 2, ANT_X1 - ANT_REC + 0.15, ANT_SZ[1] / 2, ANT_ZC + ANT_SZ[0] / 2)
ant_a, ant_b = xf(_ant, T_ECC), xf(xf(_ant, rotz(180)), T_ECC)
# 11-20 夜 转子盘B: 用户「贴到罩子吧」「罩子天然有这个侧立面」「这个天线是fpc的」⇒ 天线 FPC 改贴转子罩内壁 (r82, rotor_shroud_b_v1_2 定位浅槽 0.3 深),
#   软板顺圆柱面弯 (r82.15–82.3), 长边沿 Z; 中心角 ANT_B_ANG (+y 半 25.2° / −y 半 205.2°, 罩耳与配重唇之间), 槽心 Z ANT_B_ZC (槽顶离顶盖底 0.3); 侧立件不再有天线板
ANT_B_R = 82.0                                    # 转子罩内壁 (rotor_shroud_v1_2.R0)
ANT_B_ANG = (25.2, 205.2)
ANT_B_ZC = round(B.Z_VIEW0 - 2.0 - 0.3 - ANT_L / 2, 2)   # 51.73 ⇒ 槽 Z32.68–70.78 (顶盖底 Z71.08)
if B.ROTOR_B:
    def _ant_b(a):
        ha = math.degrees(ANT_SZ[1] / 2 / ANT_B_R)
        r1 = ANT_B_R + ANT_REC
        o = cyl(0, 0, 2 * r1, ANT_B_ZC - ANT_SZ[0] / 2, ANT_B_ZC + ANT_SZ[0] / 2, ang=2 * ha, a0=a - ha)
        return cut(o, cyl(0, 0, 2 * (r1 - 0.15), ANT_B_ZC - ANT_SZ[0] / 2 - 1, ANT_B_ZC + ANT_SZ[0] / 2 + 1))
    ant_a, ant_b = _ant_b(ANT_B_ANG[0]), _ant_b(ANT_B_ANG[1])


def pair(s_a_local0):
    """板 A 坐标系 (B 面/LED 面 y=0) 的形状 → (板 A 世界, 板 B 世界): 先 +Y_LED, 板 B 绕局部原点转 180°, 两块再平移 ECC。
    assembly_noglass 的 MIP LED (V.led_mip) 请用 L.pair(_mb) / L.pair(_mt) 摆, 别再只 +Y_LED。"""
    a = xf(s_a_local0, tr(0, Y_LED, 0))
    return xf(a, T_ECC), xf(xf(a, rotz(180)), T_ECC)


# ---------------- 板子 ----------------
VB = V.make(B)
_led_a0 = xf(VB['led'], tr(0, Y_LED, 0)); _led_b0 = xf(_led_a0, rotz(180))   # 局部 (夹条挖槽用)
led_a, led_b = pair(VB['led'])
# 桥板 64×36×1.6 (B 面 = LED 面, AXK 合高 3.0), 下沿 = 灯板下沿; FPC 座 XW0525512 在桥板外面, 下沿+2…6.4 (插口朝下)
_br = gbox(-32, Y_LED + 3.0, Z0, 32, Y_LED + 4.6, Z0 + 36)
_fpc = gbox(-20.75, Y_LED + 4.6, Z0 + 2.0, 20.75, Y_LED + 6.6, Z0 + 6.4)
br_a, br_b = xf(_br, T_ECC), xf(xf(_br, rotz(180)), T_ECC)
fpc_a, fpc_b = xf(_fpc, T_ECC), xf(xf(_fpc, rotz(180)), T_ECC)
_bar0, BAR_CUTS = bar([_led_a0, _led_b0])
bar_s = xf(_bar0, T_ECC)
bb_step = VB['bb_step']                            # r4c 交付 STEP (已 +Z_BB0; 板框见 VB['baseboard'])
# r3 没 3D 模型的件 → 框 (r3 kicad 解析 courtyard) × 高 (板顶以上, 插座含插头)
zt = B.Z_BB0 + B.BB_T
_H_ENV = {'J5': 2.0, 'J6': 2.0, 'J8': 3.0, 'J10': 3.0, 'J9': 2.0, 'J11': 0.5, 'J12': 0.5, 'J13': 2.0, 'J14': 8.0, 'U1': 4.0, 'P1': 3.0, 'C13': 3.1, 'C79': 3.1}   # r4d: J8/J10/J9 改焊线焊盘 (焊点+线头约 3), J11/J12 测试点, C13/C79 聚合物 7343
_bbp = {r: bb for r, fp, bb, h in V.baseboard_parts()[0]}
ENV = {k: (*_bbp[k], h) for k, h in _H_ENV.items() if k in _bbp}
ENV['CZ06 (DF40+板+件)'] = (-30.0, 17.05, 30.0, 52.05, B.CZ06_H)   # 11-17 r4i (两口朝外) CZ06 17.05–52.05; r4h 18.6–53.6; r4b 18.3–53.3; 11-17 r4g/r4h CZ06 整组 +0.3
env = {k: gbox(a, b_, zt, c, d, zt + h) for k, (a, b_, c, d, h) in ENV.items()}
env['底面件 (r2 B.CrtYd × 限高)'] = VB['bb_parts']
# 灯板 J3 (VH 立式, LED 面) + 插头: 板 A 在 +x (局部 y 3.77–26), 板 B 在 −x (−y); 随灯板平移
_j3 = gbox(54.85, Y_LED, Z0 + 1.4, 63.55, 26.0, Z0 + 11.0)
env['J3 插头 板A'], env['J3 插头 板B'] = xf(_j3, T_ECC), xf(xf(_j3, rotz(180)), T_ECC)
# 24V 线 (无线模块 → P1): 贴盘面, 沿 x≈−55 (−x 立板横杆 x−69 内侧) 从灯板下缝穿到 +y, 再沿内座后面到 P1 (Φ3 包络)
env['24V 线 x≈−55'] = gbox(-56.5, -40.0, RIM_TOP, -53.5, 12.0, RIM_TOP + 3.0)
# 罩底固定凸台包络 (rotor_shroud: 按 B.SHR_ANG 每处 r72.5–82 × 宽 8 × Z32–36, 立板耳朵要让开)
_shr_box = gbox(72.5, -4.0, RIM_TOP, 82.0, 4.0, RIM_TOP + 4.0)
SHR_BOSS = {a: xf(_shr_box, rotz(a)) for a in B.SHR_ANG}
# 两根 FPC (平铺段, 0.3 厚): B 从桥板 B 座下来贴毂盘顶到 J6; A 从桥板 A 座下来拱过 J6 到 J5 (起点随灯板平移)
fpc_flat_b = gbox(-18.0, ECC - Y_LED - 5.6, HUB_TOP, 18.0, 6.3, HUB_TOP + FPC_T)   # r4b: 平铺到 y6.3, 在桥板 A 座外侧 y6.01 与底板下沿 y8.6 之间竖直上到 J6
WL_STEP = B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_v1_2.step'
wl = read_step(WL_STEP) if WL_STEP.exists() else gbox(-24.5, -75.5, 32, 24.5, -45, 50)

SUP = dict(post_a=post_a, post_b=post_b, bar=bar_s, top=top, comb=comb_s)


def fpc_len():
    """两根 FPC 实际走线 (中线折线 + 弯曲按 r1.5 四分之一圆近似); 端点 = 桥板座插口 (Z39, 朝下) → 底板座触点排"""
    def L(pts):
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    yb = Y_LED + 5.6                                # 桥板座中线 局部 |y| 9.37 (世界 +5.01 / −13.73)
    zb = Z0 + 2.0                                   # 座插口 Z39
    zf = HUB_TOP + FPC_T / 2                        # 平铺 Z30.55
    zj = zt + 0.7                                   # 底板座插口中线 Z37.3
    # B: 桥板 B 座 (y −9.37) 往下到毂盘顶, 平铺到 y≈10, 斜上到 J6 口 (y14.5), 进 J6 到触点排 y21.58
    pb = [(ECC - yb, zb + 2.5), (ECC - yb, zf), (6.0, zf), (7.3, zf + 1.3), (7.3, zj - 1.3), (8.7, zj), (15.77, zj)]   # r4b: J6 口 y8.7, 信号脚 y15.77; 竖槽 y6.01–8.6
    # A (r3): 桥板 A 座 (y 9.37) 下出后弯向 +y, 拱过 J6 顶 (Z38.6) 爬上 CZ06 顶 (Z43.2 +0.5), 过 CZ06 外沿 y66 折下到 J5 口 (y72), 进到触点排 y79.07
    zc = zt + B.CZ06_H + 0.5
    pa = [(ECC + yb, zb + 2.5), (ECC + yb, zb), (6.5, 37.9), (8.2, 39.2), (17.0, 39.2), (18.3, zc), (53.3, zc), (58.33, zj), (65.4, zj)]   # r4b: 拱过 J6 (顶 38.6), CZ06 y18.3–53.3, J5 口 y58.33, 信号脚 ≈65.4
    return dict(fpc_b_mm=round(L(pb), 1), fpc_a_mm=round(L(pa), 1), path_b_yz=pb, path_a_yz=pa,
                note='底板 r4b (J6 口 y8.7 / J5 口 y58.33); 座内插入段 2.5 (桥板座) + 到触点排 (底板座); 未计余量 (r3: A 跨 CZ06 顶到外座, 贴 CZ06 顶用聚酰亚胺双面胶)')


def report():
    """干涉 / 转动包络 / 质量平衡 (慢, 几分钟)"""
    # ---------------- 干涉 ----------------
    OTHERS = dict(led_a=led_a, led_b=led_b, bridge_a=br_a, bridge_b=br_b, fpc_conn_a=fpc_a, fpc_conn_b=fpc_b,
                  bb_r2_step=bb_step, bb_r2_pcb=VB['baseboard'], wireless_holder=wl, fpc_flat_b=fpc_flat_b,
                  rim=B.rim, hub=B.hub, shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube,
                  glass_top=B.glass_top, glass_top_hub=B.glass_top_hub, key_bracket=B.key_bracket,
                  **{f'env {k}': v for k, v in env.items()}, **{f'罩底凸台包络 @{a:g}°': v for a, v in SHR_BOSS.items()})
    rep = dict(interf={}, fasteners={}, misc={})
    for a, sa in SUP.items():
        n = 0
        for b, sb in OTHERS.items():
            v = common_v(sa, sb); n += 1
            if abs(v) > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
        rep['interf'][f'{a} × rod'] = round(common_v(sa, rod), 4)
    rep['interf']['_checked'] = f'{len(SUP)} 件 × {len(OTHERS)} 对象 (+rod), 只列非 0; top × rod = Φ8 轴压入 Φ7.85 孔的过盈 (应有)'
    ks = list(SUP)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            v = common_v(SUP[a], SUP[b])
            if v > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
    fast = h1 + foot_scr + bar_scr + comb_scr
    for nm, s in fast:
        for b in ('led_a', 'led_b', 'bb_r2_step', 'bb_r2_pcb', 'wireless_holder', 'bridge_a', 'bridge_b', 'rim', 'hub', 'shroud_lo', 'shroud_hi', 'key_bracket',
                  *[k for k in OTHERS if k.startswith('罩底凸台')]):
            v = common_v(s, OTHERS[b])
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[b] = round(v, 3)
        for a, sa in SUP.items():
            v = common_v(s, sa)
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[a] = round(v, 3)
    # 铜螺母 Φ4.2 与 Φ4.2 孔同轴同径, OCC 布尔会把整环算成重叠 ⇒ 校核用 Φ4.1 (孔本身另核: Φ4.1 实心柱 × 毂盘 = 0)
    chk_ins = ([('M3×4 铜螺母 毂盘底 立板耳朵', ins(x, y, *HUB_INS, d=4.1)) for x, y in FOOT_PTS]
               + [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, ECC, Z1, Z1 + CAP_T, d=4.1)) for sx in (1, -1)])
    # 11-16 晚: 耳朵螺丝的铜螺母在毂盘底 (锁盘螺丝那套) ⇒ Φ4.1 实心柱 × hub 应 0 (孔已切), × rim 应 0 (不进承载盘)
    rep['fasteners']['ear_insert_hole_Φ4.1_solid × hub'] = round(sum(common_v(cyl(x, y, 4.1, *HUB_INS), B.hub) for x, y in FOOT_PTS), 4)
    rep['fasteners']['ear_insert_hole_Φ4.1_solid × rim'] = round(sum(common_v(cyl(x, y, 4.1, *HUB_INS), B.rim) for x, y in FOOT_PTS), 4)
    rep['fasteners']['ear_hole_Φ3.3_solid × rim (承载盘 Φ3.4 通孔在位)'] = round(sum(common_v(cyl(x, y, 3.3, HUB_INS[1], RIM_TOP), B.rim) for x, y in FOOT_PTS), 4)
    for nm, s in chk_ins:
        for b, sb in (('rim', B.rim), ('hub', B.hub), ('top', top)):
            v = common_v(s, sb)
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[b] = round(v, 3)
    rep['fasteners']['rod × glass_top_hub'] = round(common_v(rod, B.glass_top_hub), 4)
    rep['fasteners']['688 × glass_top_hub'] = round(common_v(brg, B.glass_top_hub), 4)
    for nm, s in (('antenna_a', ant_a), ('antenna_b', ant_b)):
        for b in ('shroud_lo', 'shroud_hi', 'bb_r2_step', 'led_a', 'led_b', 'wireless_holder'):
            v = common_v(s, OTHERS[b])
            if v > 1e-4: rep['fasteners'][f'{nm} × {b}'] = round(v, 4)
    rep['fasteners']['_note'] = '只列非 0; 螺丝穿过自己的孔 (承载盘/毂盘/支撑件 Φ3.4) 应为 0'
    # 立板单连通 + 耳朵几何
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    def nsol(sh):
        e = TopExp_Explorer(sh, TopAbs_SOLID); n = 0
        while e.More(): n += 1; e.Next()
        return n
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    def dist(a_, b_):
        d = BRepExtrema_DistShapeShape(a_, b_); d.Perform(); return round(d.Value(), 2)
    rep['ear'] = dict(t=EAR_T, z=(RIM_TOP, EAR_Z1), pad_d=EAR_PAD_D, pts=[(round(x, 2), round(y, 2), round(math.degrees(math.atan2(y, x)) % 360, 1)) for x, y in FOOT_PTS],
                      r_outer=round(min(B.RH_R + EAR_PAD_D / 2, R_CLIP), 2), head_r_outer=round(B.RH_R + 2.75, 2), y_max=round(max(abs(y) for _, y in FOOT_PTS) + EAR_PAD_D / 2, 2),
                      ang_max_deg=round(22.5 + math.degrees(math.asin(EAR_PAD_D / 2 / B.RH_R)), 1),
                      n_solids=dict(post_a=nsol(post_a), post_b=nsol(post_b)),
                      gap_to_shr_boss={f'{nm}×{a:g}°': dist(p_, v) for nm, p_ in (('post_a', post_a), ('post_b', post_b)) for a, v in SHR_BOSS.items()},
                      gap_to_bb_pcb=dict(post_a=dist(post_a, VB['baseboard']), post_b=dist(post_b, VB['baseboard'])),
                      gap_to_wireless=dict(post_a=dist(post_a, wl), post_b=dist(post_b, wl)))
    rep['screws'] = dict(
        耳朵脚=dict(spec=f'M3×{FOOT_SCREW_L:g} 内六角 ×4 (兼外圈锁盘 k={B.RH_EAR_IDX})', pts=[(round(x, 2), round(y, 2)) for x, y in FOOT_PTS], bear_z=FOOT_CB_Z,
                 tip_z=FOOT_CB_Z - FOOT_SCREW_L, insert_z=HUB_INS, engage=round(min(FOOT_CB_Z, HUB_INS[1]) - max(FOOT_CB_Z - FOOT_SCREW_L, HUB_INS[0]), 2),
                 head_r_max=round(B.RH_R + 2.75, 2), head_z=(FOOT_CB_Z, FOOT_CB_Z + 3.0), insert='毂盘底 M3×4 铜螺母 (B.RH_INS, 锁盘螺丝那套)'),
        夹条竖螺丝=dict(spec=f'M3×{BAR_SCR_L:g} 内六角 ×2 从立板底面往上 (自攻进夹条 Φ{BAR_TAP_D:g})', x=BAR_SCR_X, y=BAR_SCR_Y, bear_z=BAR_SCR_BEAR, tip_z=BAR_SCR_BEAR + BAR_SCR_L, bar_tap=(Z0, Z0 + BAR_TAP_H)),
        梳齿=dict(spec='M3×8 内六角 ×2 → 帽内 M3×4 铜螺母', engage=4.0, pts=[(sx * COMB_FIX_X, ECC) for sx in (1, -1)], slots=len(COMB_SLOTS), slot_r_max=round(max(math.hypot(*p) for p in COMB_SLOTS), 1)))
    rep['misc']['ecc'] = dict(SCR_ECC=ECC, boardA_F=round(ECC + GAP_HALF, 3), boardA_LED=round(ECC + Y_LED, 3), boardA_MIP_top=round(ECC + Y_LED + MIP_H, 3),
                              boardB_F=round(ECC - GAP_HALF, 3), boardB_LED=round(ECC - Y_LED, 3), boardB_MIP_top=round(ECC - Y_LED - MIP_H, 3),
                              led_a_bbox_y=[round(v, 3) for v in bbox(led_a)[1::3][:2]], led_b_bbox_y=[round(v, 3) for v in bbox(led_b)[1::3][:2]], antenna_y=ANT_Y)

    # 转动包络 vs 静止件: 每 Z 段转动件最大 r 与静止件最小 r
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.1):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot_parts = [post_a, post_b, bar_s, top, comb_s, ant_a, ant_b] + [s for _, s in foot_scr + comb_scr]
    static = dict(tube=B.tube, shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass_top=B.glass_top, glass_top_hub=B.glass_top_hub)
    env_rows = []
    r_rot = np.concatenate([rz(s)[0] for s in rot_parts]); z_rot = np.concatenate([rz(s)[1] for s in rot_parts])
    st = {k: rz(s, 0.05) for k, s in static.items()}
    for z0 in np.arange(30, 300, 2.0):
        m = (z_rot >= z0) & (z_rot < z0 + 2)
        if not m.any(): continue
        rmax = r_rot[m].max()
        rmin = min([r[(z >= z0 - 1) & (z < z0 + 3)].min() for r, z in st.values() if ((z >= z0 - 1) & (z < z0 + 3)).any()] + [999])
        env_rows.append((float(z0), round(float(rmax), 2), round(float(rmin), 2), round(float(rmin - rmax), 2)))
    rep['misc']['sweep_min_gap'] = min(env_rows, key=lambda r: r[3])
    rep['misc']['sweep_rows_tight'] = [r for r in env_rows if r[3] < 5]
    rep['misc']['rot_r_max'] = dict(post=round(float(max(rz(post_a)[0].max(), rz(post_b)[0].max())), 2), 耳朵螺丝头=round(float(max(rz(s)[0].max() for _, s in foot_scr)), 2),
                                    antenna=round(float(rz(ant_a)[0].max()), 2), comb=round(float(rz(comb_s)[0].max()), 2))
    rep['misc']['hub_tip'] = HUB_TIP; rep['misc']['boss_z'] = (Z1 + CAP_T, BOSS_Z1); rep['misc']['rod'] = f'Φ8×{ROD_L:g} Z{ROD_Z0:.2f}–{ROD_Z1:.2f}, 压入轴座 {BOSS_Z1 - ROD_Z0:.1f}'
    rep['misc']['brg_z'] = (BRG_Z0, BRG_Z1)
    rep['misc']['bar_cuts'] = BAR_CUTS
    rep['misc']['fpc'] = fpc_len()

    # ---------------- 质量 / 平衡 (打印件按实心 PETG 1.27 / 填充按实心算 (偏保守); 钢螺丝 7.85) ----------------
    RHO, RHO_ST = 1.27e-3, 7.85e-3
    bal = {}
    Ux = Uy = Mx = My = 0.0
    def add(nm, g, cx, cy, cz):
        nonlocal Ux, Uy, Mx, My
        bal[nm] = dict(g=round(g, 2), cog=(round(cx, 2), round(cy, 2), round(cz, 1)), U=(round(g * cx, 1), round(g * cy, 1)))
        Ux += g * cx; Uy += g * cy; Mx += g * cx * cz; My += g * cy * cz
    for nm, s in SUP.items():
        m, c = cog(s); add(nm, m * RHO, *c)
    for nm, s in foot_scr + bar_scr + h1 + comb_scr:
        m, c = cog(s); add(f'{nm} @({c[0]:.0f},{c[1]:.0f})', m * RHO_ST, *c)
    sup_U = (round(Ux, 1), round(Uy, 1)); bal['supports_U_gmm'] = sup_U
    # 11-16 晚 偏心: 灯板/桥板整组在 y=ECC ⇒ 不再对称, 按质量 × 几何质心计 (质量为估算)
    #   灯板: STEP 最大实体 (PCB) 体积 × FR4 1.9 + 器件 (ICN2260/电容/接插件 + 10368 颗 MIP) 估 30 g (V1.0 估法 35 g/板); 桥板 64×36×1.6 FR4 + 件 ≈ 12 g
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    e = TopExp_Explorer(led_a, TopAbs_SOLID); vmax = 0.0
    while e.More(): vmax = max(vmax, vol(e.Current())); e.Next()
    LED_G = round(vmax * 1.9e-3 + 30.0, 1)
    for nm, s in (('灯板 A (PCB+件 估)', led_a), ('灯板 B (PCB+件 估)', led_b)):
        _, c = cog(s); add(nm, LED_G, *c)
    for nm, c in (('桥板 A (真模型 mass.json 10.99 g)', (0.21, 3.18, 55.36)), ('桥板 B (真模型 10.99 g)', (-0.21, -11.90, 55.36))):   # 11-16 晚 fpc_v1_2 (G) 实算重心
        add(nm, 10.99, *c)
    bal['led_board_g_est'] = LED_G
    grp_U = (round(Ux - sup_U[0], 1), round(Uy - sup_U[1], 1)); bal['led_group_boards_U_gmm'] = grp_U
    # 底板: r4c 五边形 x −51.2…47.3 y8.6–66.6, 质量沿用 r3 估 44.5 g, 质心取板框包围盒中心
    _bb = bbox(VB['baseboard']); bbc = ((_bb[0] + _bb[3]) / 2, (_bb[1] + _bb[4]) / 2)
    add('底板 r4c (r3 质量 44.5 g 估, 质心 = 板框包围盒中心)', 44.5, bbc[0], bbc[1], zt + 3.0)
    WL_REP = B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_report.json'
    try:
        wb = json.load(open(WL_REP, encoding='utf-8'))['balance']; add('无线模块+固定件 (wireless_holder_report)', wb['total_g'], *wb['total_cog'])
    except Exception:
        add('无线模块+固定件 (wireless_holder 11-16, 缺报告用旧值)', 39.2, 0.04, -60.69, 39.5)
    TX, TY = Ux, Uy
    CW_R = 83.0
    bal['total_U_gmm'] = (round(TX, 1), round(TY, 1)); bal['total_U_abs'] = round(math.hypot(TX, TY), 1)
    bal['cw_r'] = CW_R; bal['cw_g'] = round(math.hypot(TX, TY) / CW_R, 2)
    bal['cw_ang_deg'] = round(math.degrees(math.atan2(-TY, -TX)) % 360, 1)
    zc = math.hypot(Mx, My) / max(math.hypot(TX, TY), 1e-9)
    bal['unbalance_z_eff'] = round(zc, 1)
    # 两面配平: 下面 = 罩内 r83 (Z≈45 假设), 上面 = 梳齿 (Z≈251, r≈40)
    z_lo, z_hi, r_hi = 45.0, COMB_Z1 - 2, 40.0
    Ulo = [(-(Mx_ - z_hi * U_)) / (z_lo - z_hi) for U_, Mx_ in ((TX, Mx), (TY, My))]
    Uhi = [-(U_) - l for U_, l in zip((TX, TY), Ulo)]
    bal['two_plane'] = dict(lo=dict(z=z_lo, r=CW_R, U=(round(Ulo[0], 1), round(Ulo[1], 1)), g=round(math.hypot(*Ulo) / CW_R, 2), ang=round(math.degrees(math.atan2(Ulo[1], Ulo[0])) % 360, 1)),
                            hi=dict(z=z_hi, r=r_hi, U=(round(Uhi[0], 1), round(Uhi[1], 1)), g=round(math.hypot(*Uhi) / r_hi, 2), ang=round(math.degrees(math.atan2(Uhi[1], Uhi[0])) % 360, 1)),
                            note='11-16 晚: 灯板/桥板按 ECC 偏心计入 (质量估); 玻璃件/毂盘/承载盘按对称; 罩内配重面 Z 未定 (按 45), 梳齿只修上面残余, 以实测动平衡为准')
    rep['balance'] = bal
    rep['valid'] = {k: BRepCheck_Analyzer(v).IsValid() for k, v in SUP.items()}
    rep['volume_mm3'] = {k: round(vol(v), 1) for k, v in SUP.items()}
    return rep


NAMES = dict(post_a='led_post_a_v1_2', post_b='led_post_b_v1_2', bar='led_bar_v1_2', top='led_top_v1_2', comb='led_comb_v1_2')
if __name__ == '__main__':
    COL = dict(post_a='#F1C232', post_b='#E69138', bar='#8E7CC3', top='#6FA8DC', comb='#3D85C6')
    # 打印姿态: 立板正放 (底面 Z32 落床, 耳朵同平面); 顶部件倒放 (轴座顶 Φ14 落床, 帽两端小悬空); 梳齿平放
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    rx90 = gp_Trsf(); rx90.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)   # 夹条侧放 (4.6 面落床)
    for k, s in SUP.items():        # 同其他 V1.2 件: models/<件>/<件>.{step,stl} = 装配坐标 (出图用); 打印姿态 STL → out/打印STL/
        d = B.V12 / 'models' / NAMES[k]; d.mkdir(exist_ok=True)
        write_doc([(NAMES[k], s, COL[k], None, False)], d / f'{NAMES[k]}.step', NAMES[k])
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(d / f'{NAMES[k]}.stl'))
        t = xf(s, fx) if k == 'top' else (xf(s, rx90) if k == 'bar' else s)
        bb = bbox(t); t = xf(t, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAMES[k]}.stl'))
    items = [(NAMES[k], s, COL[k], None, False) for k, s in SUP.items()] + [
        (f'Φ8×{ROD_L:g} 钢轴', rod, '#999999', None, False), ('688ZZ', brg, '#666666', None, False),
        ('灯板 A (+y) 板框', gbox(-HALF_W, ECC + GAP_HALF, Z0, HALF_W, ECC + Y_LED, Z1), '#145A32', None, False), ('灯板 B (−y) 板框', gbox(-HALF_W, ECC - Y_LED, Z0, HALF_W, ECC - GAP_HALF, Z1), '#145A32', None, False),
        ('桥板 A', br_a, '#1E8449', None, False), ('桥板 B', br_b, '#1E8449', None, False),
        ('天线 18.5×37.7 软板 +x 竖', ant_a, '#C0392B', None, False), ('天线 18.5×37.7 软板 −x 竖', ant_b, '#C0392B', None, False),
        ('底板 r4c 板框', VB['baseboard'], '#2E7D32', None, False), ('FPC B 平铺段 (示意)', fpc_flat_b, '#E67E22', None, False)] + [
        (n, s, '#888888', None, False) for n, s in h1 + foot_scr + foot_ins + bar_scr + comb_scr + comb_ins]
    write_doc(items, OUT / 'led_support_装配位.step', 'led_support_asm')
    rep = report()
    json.dump(rep, open(OUT / 'led_support_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
