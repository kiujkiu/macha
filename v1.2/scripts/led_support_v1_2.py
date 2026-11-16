"""V2 灯板支撑 (11-14 定 V0.4 portal 改; 11-16 按新转子布局重做: 灯板下沿 Z37, 底板 r3 在 +y, 无线模块在 −y;
11-16 晚 用户: 灯板下端沿用 V0.4 —— 夹条托在两板之间, T 件在下面, 竖直螺丝从下往上锁)。
    cd v1.2/scripts && ../../.venv/bin/python led_support_v1_2.py
世界坐标 (同 build_v1_2): Z0 = 底盘顶, 承载盘顶 Z32 (r<24.5 毂盘顶 Z30.4), 灯板下沿 B.Z_SCR0 = 37 / 上沿 245.0; 灯板面平行 XZ。
两块 LED_V0.2.0 背靠背: 板 A F 面 (背面) 在 y=+2.3, LED 面 +y; 板 B = 板 A 绕 Z 转 180° (间隙 4.6 = 铜柱, 用户 11-14)。
零件 (打印, PETG/PLA):
  led_bar_v1_2     夹条: 夹在两板 F 面之间 (厚 4.6), Z37–46, 两端 |x|≥68 加高到 Z54; H1/H2 (±78.63, Z41) M3 横穿 板-条-板;
                   底面 4 个 Φ2.6 竖孔 (x ±74 / ±38) 给 T 件来的 M3×8 自攻; F 面器件处挖浅槽
  led_post_a_v1_2  +x 端立板 (11-16 晚 转子罩缩到 r82–85 坐盘上, 改成同中间 T 件做法): T 脚横杆 x70–78 沿 y |y|≤14 Z32–37,
                   两脚孔 (74, ±10) M3×6 内六角从上面进承载盘顶面铜螺母; 腹板 |y|≤8 x78→82.6 连竖贴天线板 (在罩壁缝里, r≤84.7);
                   除腹板+天线板外整件 r≤81.7; 底面沉孔 M3×8 往上锁夹条 (原立刀取消, 夹条代替)
  led_post_b_v1_2  −x 端立板 (镜像, 孔 (−74, ±10))
  led_mid_t_v1_2   中间 T 件 ×2 (同件转 180°): x ±38 沿 y 横杆 Z32–37, 两脚孔 (±38, ±10) M3×6 从上面进承载盘铜螺母; 底面沉孔 M3×8 往上锁夹条
  led_top_v1_2     顶部件: 舌 (上中窗) + 帽压两板上沿 + Φ14 轴座 (加长 8.2), 压 Φ8×50 钢轴, 轴进玻璃上盖堵头的 688; 帽上 2×M3×4 铜螺母锁梳齿
  led_comb_v1_2    顶部配平梳齿: 横梁沿 x 套在轴座上、坐帽顶 (2×M3×8 锁帽), 每侧 4 个齿 (沿 y), 每齿 4 个 Φ3.4 竖孔挂 M3 螺丝+螺母配重
装法: 桌上先把灯板 A/B + 夹条用 H1/H2 两颗 M3 横穿夹好, 再把两端立板 + 两个中间 T 件从下面用 4×M3×8 锁到夹条上;
      整体放上转子, 从上面拧 T 脚 4×M3×6 (承载盘铜螺母) + 中间 T 件 4×M3×6 (承载盘铜螺母)。
外购: Φ8×50 钢轴 (h6), 688ZZ; M3×6 内六角 ×4 (两端 T 脚) + 承载盘顶面 M3×4 铜螺母 ×4 (END_T_HOLES); M3×6 内六角 ×4 + 承载盘 M3×4 铜螺母 ×4 (中间 T 件);
      M3×8 内六角 ×4 (T 件 → 夹条, 自攻); M3×12 内六角 ×2 + M3 法兰螺母 ×2 (H1/H2); M3×8 内六角 ×2 + M3×4 铜螺母 ×2 (梳齿 → 帽); 配重 M3×8 + M3 螺母 (按需);
      WiFi 天线 18.5×37.7 软板 (11-16 晚 用户; 原 Molex 219611 35×15) ×2 竖贴两端。
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
GAP_HALF = 2.3                                    # 板 F 面 y=±2.3 (间隙 4.6, 用户 11-14)
PCB_T = 1.468                                     # STEP 板厚 (A10 写 1.54; 按 STEP)
Y_LED = GAP_HALF + PCB_T                          # LED 面 y=±3.768
HALF_W = 81.879                                   # 板半宽
H1_X, H1_Z = 78.63, Z0 + 4.0                      # H1/H2 M3 (±78.63, 下沿+4 = Z41)
CLR = 0.1                                         # 立刀/舌 与板 F 面单边
BLADE_T = 2 * (GAP_HALF - CLR)                    # 4.4
RIM_TOP = B.Z_RIM_TOP                             # 32.0
HUB_TOP = 30.4                                    # 毂盘顶 (r<24.5, 实测 build 毂盘)
R_CLIP = 81.7                                     # 11-16 晚: 转子罩壁 r82–85 ⇒ 罩内件外缘 ≤ r81.7 (留 0.3); 腹板+天线板例外 (罩壁缝 |y|≤8.6, r≤ANT_R_MAX)

# ---------------- 两端立板: T 形底脚 ----------------
# 11-16 晚 (转子罩缩到 r82–85 坐承载盘顶, 用户照 V0.4): 原 R82.5 孔 + M3×16 进毂盘底铜螺母的 T 脚会撞罩壁 ⇒ 改成同中间 T 件:
#   横杆 x (±)70–78 沿 y |y|≤14 Z32–37, 两脚孔 B.END_T_HOLES (±74, ±10): Φ3.4 通 + 顶面 Φ6 沉孔 (底 Z34),
#   M3×6 内六角头支承 Z34 (头顶齐 Z37), 尾 Z28, 进承载盘顶面 M3×4 铜螺母 Z28–32, 啮合 4 (同 GATE_*)。
#   下面这些名字别的脚本 (build_drawings / fasteners / check / assembly_noglass) 在用, 名字沿用、含义改新。
FOOT_PTS = [tuple(p) for p in B.END_T_HOLES]       # (±74, ±10) 承载盘顶面 Φ4.2×4 铜螺母孔 (build 已切)
R_HOLE = math.hypot(*FOOT_PTS[0])                 # 74.67 (脚孔半径; 原 R82.5 孔不再用)
HUB_BOT = 21.5                                    # 毂盘底面 (仅参考, T 脚不再进毂盘)
HUB_INS = (RIM_TOP - 4.0, RIM_TOP)                # 11-16 晚起是承载盘顶面 M3×4 铜螺母 Z28–32 (名字沿用, 不再是毂盘底)
FOOT_SCREW_L = 6.0                                # M3×6 内六角
FOOT_CB_Z = 34.0                                  # 头支承 Z34 (Φ6 沉孔底) ⇒ 头顶 Z37 齐 T 脚顶, 尾 Z28, 啮合 4.0
FOOT_CB_D = 6.0                                   # 顶面 Φ6 沉孔 Z34–37
PAD_D = 8.0                                       # 不再有凸台 (横杆宽 8 本身); 保留给出图脚本 = 孔位处实体宽
T_X = 74.0                                        # 横杆中线 (= 脚孔 / 夹条竖螺丝 x)
T_W = 8.0                                         # 横杆宽 (x 70–78)
FOOT_Y = 14.0                                     # 横杆半长 |y|≤14 (同中间 T 件 MID_Y)
FOOT_X0, FOOT_X1 = T_X - T_W / 2, None            # 兼容旧名 (FOOT_X1 = ANT_X1, 下面定)
BLADE_X0, BLADE_X1, BLADE_Z1 = 75.6, 81.6, Z0 + 17.0   # 立刀 x75.6–81.6 (盖住下角 F.Mask 窗 75.9–81.9 / 下沿+7…17), 顶 Z54; 实体向外延到天线板
# 天线板: 两端都竖贴; 外面 r≤84.7 (转子罩内壁 r86 要让); 内面让 H1 法兰螺母 (Φ7.6 → x82.43)
ANT_X0, ANT_X1, ANT_HW = 82.6, 84.3, 9.75         # 厚 1.7, |y|≤9.75 (11-16 晚: 天线换 18.5×37.7 软板) ⇒ 外角 r = hypot(84.3, 9.75) = 84.86
ANT_R_MAX = 84.9                                  # < 罩外圆 r85
ANT_SZ = (37.7, 18.5)                             # 11-16 晚 用户: 实际天线 = 18.5×37.7 软板 (FPC), 长边沿 Z
ANT_L, ANT_W, ANT_REC = ANT_SZ[0] + 0.4, ANT_SZ[1] + 0.4, 0.3   # 定位浅槽 38.1×18.9×0.3 (背胶贴)
ANT_Z1_MAX = B.Z_VIEW0                            # 板顶不高于罩顶/顶盖 Z73.08 (原 75.6 冒出 2.5)
ANT_ZC = round(ANT_Z1_MAX - 1.3 - ANT_L / 2, 2)    # 52.73 ⇒ 槽 Z33.7–71.8
ANT_Z1 = ANT_ZC + ANT_L / 2 + 1.3                 # 板顶 Z73.08
ANT_A = dict(y=ANT_HW, z0=RIM_TOP, z1=ANT_Z1, zc=ANT_ZC)   # 兼容旧名 (两端相同)
ANT_B = ANT_A
FOOT_X1 = ANT_X1
SCREW_H1_L = 12.0

# ---------------- 夹条 + T 件 (11-16 晚 用户: 灯板下端沿用 V0.4 —— 托在下面, 竖直螺丝从下往上锁) ----------------
# 夹条 led_bar: 夹在两板 F 面之间 (厚 = 间隙 4.6, 零间隙), 下沿齐灯板下沿 Z37; 两端用板 H1/H2 (±78.63, Z41) M3 横穿 板-条-板;
#   F 面器件按包围盒 +0.3 挖浅槽; 4 个竖孔从底面往上 (M3 自攻进打印件, 两侧被灯板夹住不怕胀)
BAR_Z1 = Z0 + 9.0                                 # 46 (盖住 H1 Z41 / M2 Z40)
BAR_END_X, BAR_END_Z1 = 68.0, Z0 + 17.0           # |x|≥68 两端加高到 Z54 (原立刀位置, 盖下角 F.Mask 窗 下沿+7…17)
BAR_M2 = [(23.0, Z0 + 3.0), (-23.0, Z0 + 3.0)]    # 板下中 M2 孔 (±23, Z40): 夹条留 Φ2.4 通孔, 可选加 M2 横穿 (桥板与 LED 面之间只 3.0, 用薄头)
BAR_TAP_D, BAR_TAP_H = 2.6, 8.0                   # 竖孔 Φ2.6 深 8 (M3 自攻)
BAR_SCR_X = [74.0, 38.0, -38.0, -74.0]            # 竖螺丝 x (两端 T 脚 / 中间 T 件), y=0
BAR_SCR_L = 8.0                                   # M3×8 内六角: 头在 T 件底面沉孔 (支承 Z35), 尾 Z43 (进夹条 6)
BAR_SCR_BEAR = RIM_TOP + 3.0                      # 35 (T 件底面 Φ6×3 沉孔, 头 Z32–35)
# 中间 T 件 led_mid_t ×2 (同件, 转 180°): x ±38, 沿 y 横杆, 两脚孔 (±38, ±10) M3×6 从上面进承载盘铜螺母 (同原门腿)
GATE_PTS = [tuple(p) for p in B.GATE_PTS]         # (±38, ±10) 承载盘 Φ4.2×4.2 铜螺母孔 (build 已切)
GATE_INS = (RIM_TOP - 4.0, RIM_TOP)               # M3×4 铜螺母 Z28–32
GATE_SCREW_L = 6.0                                # M3×6 内六角
GATE_CB_D, GATE_CB_Z = 6.0, GATE_INS[0] + GATE_SCREW_L   # 头 Φ5.5×3 沉孔 Φ6 底 Z34 ⇒ 头顶 Z37 (与 T 件顶齐), 尾 Z28, 啮合 4.0
MID_X, MID_W, MID_Y = 38.0, 8.0, 14.0             # 横杆 x 34–42, y ±14, Z32–37 (顶 = 灯板/夹条下沿)
FPC_T = 0.3
TONGUE_X = 2.8                                    # 顶部件立舌半宽 (上中 F.Mask 窗)

# ---------------- 顶部件 + 梳齿 ----------------
TOP_TONGUE_Z0 = Z1 - 13.7                         # 231.3 (上中窗 上沿−4…14)
CAP_X, CAP_Y, CAP_T = 14.5, 6.0, 4.0              # 帽 29×12×4 (原 20×12: 加宽放梳齿 2×M3 铜螺母)
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
COMB_FIX_X = 10.5                                 # 梳齿 → 帽 2×M3×8 (头 Φ5.5 外让轴座 r7.1), 帽里 Φ4.2×4 铜螺母 (穿通帽, 下面是两板间隙)
COMB_TEETH_X = [16.0, 26.0, 36.0, 46.0]           # 每侧 4 齿 (±x), 齿宽 6
COMB_TOOTH_W, COMB_TOOTH_Y = 6.0, 15.0            # 齿沿 y ±15
COMB_SLOTS_Y = [6.5, 12.0]                        # 每齿 ±6.5 / ±12 四个 Φ3.4 竖孔 (配重 M3 螺丝竖装, 螺母在齿下 Z246.6–249 > 板上沿 245)
COMB_SCREW_MAX_L = COMB_Z1 - Z1                   # 配重螺丝尾端不低于板上沿 ⇒ 头下长 ≤ 8 (+每多叠 1 个螺母可 +2.4)


def post(sx):
    """sx=+1 → +x 端 (脚孔 (74, ±10)); −1 → −x 端 (镜像, (−74, ±10))"""
    def X(a, b): return (min(sx * a, sx * b), max(sx * a, sx * b))
    tx = X(T_X - T_W / 2, T_X + T_W / 2); wx = X(T_X + T_W / 2, ANT_X1); ax = X(ANT_X0, ANT_X1)
    pts = [(x, y) for x, y in FOOT_PTS if x * sx > 0]
    # T 脚横杆: x 70–78 沿 y |y|≤14, Z32–37 (顶 = 灯板/夹条下沿, 托两板); 裁到 r≤R_CLIP (罩内壁 r82 留 0.3)
    s = common(gbox(tx[0], -FOOT_Y, RIM_TOP, tx[1], FOOT_Y, Z0), cyl(0, 0, 2 * R_CLIP, RIM_TOP - 1, Z0 + 1))
    # 腹板 (|y|≤8, x78→天线板, Z32–37) + 天线板: 在罩壁缝 |y|≤8.6 里, 裁到 r≤ANT_R_MAX
    wa = fuse(gbox(wx[0], -ANT_HW, RIM_TOP, wx[1], ANT_HW, Z0), gbox(ax[0], -ANT_HW, RIM_TOP, ax[1], ANT_HW, ANT_Z1))
    s = fuse(s, common(wa, cyl(0, 0, 2 * ANT_R_MAX, RIM_TOP - 1, ANT_Z1 + 1)))
    for x, y in pts:                                # 脚孔: Φ3.4 通 + 顶面 Φ6 沉孔 (底 Z34) → M3×6 进承载盘铜螺母
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, Z0 + 1), cyl(x, y, FOOT_CB_D, FOOT_CB_Z, Z0 + 1))
    xb = sx * BAR_SCR_X[0]                          # 底面竖螺丝 → 夹条 (Φ3.4 通 + 底面 Φ6×3 沉孔)
    s = cut(s, cyl(xb, 0, 3.4, RIM_TOP - 1, Z0 + 1), cyl(xb, 0, 6.0, RIM_TOP - 1, BAR_SCR_BEAR))
    xo = sx * ANT_X1
    rec = gbox(min(xo - sx * ANT_REC, xo + sx * 1), -ANT_W / 2, ANT_ZC - ANT_L / 2, max(xo - sx * ANT_REC, xo + sx * 1), ANT_W / 2, ANT_ZC + ANT_L / 2)
    s = cut(s, rec)
    return clean(s)


def mid_t():
    """中间 T 件 (+x 那个; −x = 转 180°)"""
    s = gbox(MID_X - MID_W / 2, -MID_Y, RIM_TOP, MID_X + MID_W / 2, MID_Y, Z0)
    for x, y in GATE_PTS:
        if x > 0: s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, Z0 + 1), cyl(x, y, GATE_CB_D, GATE_CB_Z, Z0 + 1))
    s = cut(s, cyl(MID_X, 0, 3.4, RIM_TOP - 1, Z0 + 1), cyl(MID_X, 0, 6.0, RIM_TOP - 1, BAR_SCR_BEAR))
    return clean(s)


def bar(led_pair):
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
    s = gbox(-TONGUE_X, -BLADE_T / 2, TOP_TONGUE_Z0, TONGUE_X, BLADE_T / 2, Z1 + 0.01)
    s = fuse(s, gbox(-CAP_X, -CAP_Y, Z1, CAP_X, CAP_Y, Z1 + CAP_T))
    s = fuse(s, cyl(0, 0, BOSS_D, Z1 + CAP_T - 0.01, BOSS_Z1))
    s = cut(s, cyl(0, 0, ROD_HOLE_D, ROD_Z0, BOSS_Z1 + 1))
    for sx in (1, -1):                              # 梳齿锁帽: M3×4 铜螺母孔 Φ4.2 穿通帽 (下面是两板间隙 |y|<2.3, 孔 r2.1)
        s = cut(s, cyl(sx * COMB_FIX_X, 0, 4.2, Z1 - 1, Z1 + CAP_T + 0.01))
    return clean(s)


def comb():
    s = cyl(0, 0, COMB_RING_D, COMB_Z0, COMB_Z1)
    xm = COMB_TEETH_X[-1] + COMB_TOOTH_W / 2
    s = fuse(s, gbox(-xm, -COMB_BEAM_Y, COMB_Z0, xm, COMB_BEAM_Y, COMB_Z1))
    for sx in (1, -1):
        for tx_ in COMB_TEETH_X:
            s = fuse(s, gbox(sx * tx_ - COMB_TOOTH_W / 2, -COMB_TOOTH_Y, COMB_Z0, sx * tx_ + COMB_TOOTH_W / 2, COMB_TOOTH_Y, COMB_Z1))
    s = cut(s, cyl(0, 0, COMB_HOLE_D, COMB_Z0 - 1, COMB_Z1 + 1))
    for sx in (1, -1):
        s = cut(s, cyl(sx * COMB_FIX_X, 0, 3.4, COMB_Z0 - 1, COMB_Z1 + 1))
        for tx_ in COMB_TEETH_X:
            for y in COMB_SLOTS_Y:
                for sy in (1, -1):
                    s = cut(s, cyl(sx * tx_, sy * y, 3.4, COMB_Z0 - 1, COMB_Z1 + 1))
    return clean(s)


COMB_SLOTS = [(sx * tx_, sy * y) for sx in (1, -1) for tx_ in COMB_TEETH_X for y in COMB_SLOTS_Y for sy in (1, -1)]
post_a, post_b, top, comb_s = post(+1), post(-1), top_piece(), comb()
mid_a = mid_t(); mid_b = clean(xf(mid_a, rotz(180)))
gate_s = comp([mid_a, mid_b])                     # 兼容旧名 (两个中间 T 件)
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
# ⇒ +x 端: 头 (Φ5.5) 在 +y, 法兰螺母在 −y; −x 端相反。
h1 = []
for sx in (1, -1):
    sy_head = 1 if sx > 0 else -1
    h1.append(('M3×12 内六角 灯板 H1/H2', sock(sx * H1_X, H1_Z, sy_head * Y_LED, SCREW_H1_L, axis='y', sy=sy_head)))
    h1.append(('M3 法兰螺母 灯板 H1/H2', fnut_y(sx * H1_X, H1_Z, -sy_head * Y_LED, -sy_head)))
foot_scr = [('M3×6 内六角 T 脚', sock(x, y, FOOT_CB_Z, FOOT_SCREW_L)) for x, y in FOOT_PTS]
foot_ins = [('M3×4 铜螺母 承载盘 T 脚', ins(x, y, *HUB_INS)) for x, y in FOOT_PTS]
gate_scr = [('M3×6 内六角 中间 T 件脚', sock(x, y, GATE_CB_Z, GATE_SCREW_L)) for x, y in GATE_PTS]
gate_ins = [('M3×4 铜螺母 承载盘 门腿', ins(x, y, *GATE_INS)) for x, y in GATE_PTS]
bar_scr = [('M3×8 内六角 T 件→夹条 (从下往上)', fuse(cyl(x, 0, 5.5, BAR_SCR_BEAR - 3.0, BAR_SCR_BEAR), cyl(x, 0, 3.0, BAR_SCR_BEAR - 0.01, BAR_SCR_BEAR + BAR_SCR_L))) for x in BAR_SCR_X]
comb_scr = [('M3×8 内六角 梳齿→帽', sock(sx * COMB_FIX_X, 0, COMB_Z1, 8.0)) for sx in (1, -1)]
comb_ins = [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, 0, Z1, Z1 + CAP_T)) for sx in (1, -1)]
# 天线 (35×15×0.1 片), 外面 x=±(ANT_X1 − 0.2)
ant_a = gbox(ANT_X1 - ANT_REC, -ANT_SZ[1] / 2, ANT_ZC - ANT_SZ[0] / 2, ANT_X1 - ANT_REC + 0.15, ANT_SZ[1] / 2, ANT_ZC + ANT_SZ[0] / 2)   # 软板 0.15 厚
ant_b = xf(ant_a, rotz(180))

# ---------------- 板子 ----------------
VB = V.make(B)
led_a = xf(VB['led'], tr(0, Y_LED, 0))
led_b = xf(led_a, rotz(180))
# 桥板 64×36×1.6 (B 面 = LED 面, AXK 合高 3.0), 下沿 = 灯板下沿; FPC 座 XW0525512 在桥板外面, 下沿+2…6.4 (插口朝下)
br_a = gbox(-32, Y_LED + 3.0, Z0, 32, Y_LED + 4.6, Z0 + 36)
fpc_a = gbox(-20.75, Y_LED + 4.6, Z0 + 2.0, 20.75, Y_LED + 6.6, Z0 + 6.4)
br_b, fpc_b = xf(br_a, rotz(180)), xf(fpc_a, rotz(180))
bar_s, BAR_CUTS = bar([led_a, led_b])
bb_step = VB['bb_step']                            # r2 交付 STEP (已 +Z_BB0)
# r3 没 3D 模型的件 → 框 (r3 kicad 解析 courtyard) × 高 (板顶以上, 插座含插头)
zt = B.Z_BB0 + B.BB_T
_H_ENV = {'J5': 2.0, 'J6': 2.0, 'J8': 17.0, 'J10': 17.0, 'J9': 12.0, 'J11': 4.5, 'J12': 4.5, 'J13': 2.0, 'J14': 8.0, 'U1': 4.0, 'P1': 3.0, 'C13': 10.8}
_bbp = {r: bb for r, fp, bb, h in V.baseboard_parts()[0]}
ENV = {k: (*_bbp[k], h) for k, h in _H_ENV.items() if k in _bbp}
ENV['CZ06 (DF40+板+件)'] = (-30.0, 30.82, 30.0, 65.82, B.CZ06_H)   # rev c
env = {k: gbox(a, b_, zt, c, d, zt + h) for k, (a, b_, c, d, h) in ENV.items()}
env['底面件 (r2 B.CrtYd × 限高)'] = VB['bb_parts']
# 灯板 J3 (VH 立式, LED 面) + 插头: 板 A 在 +x (y 3.77–26), 板 B 在 −x (−y)
env['J3 插头 板A'] = gbox(54.85, Y_LED, Z0 + 1.4, 63.55, 26.0, Z0 + 11.0); env['J3 插头 板B'] = xf(env['J3 插头 板A'], rotz(180))
# 24V 线 (无线模块 → P1): 贴盘面, 沿 x≈−55 (中间 T 件 x−42 与两端 T 脚 x−72 之间) 从灯板下缝穿到 +y, 再沿内座后面到 P1 (Φ3 包络)
env['24V 线 x≈−55'] = gbox(-56.5, -40.0, RIM_TOP, -53.5, 12.0, RIM_TOP + 3.0)
# 两根 FPC (平铺段, 0.3 厚): B 从桥板 B 座下来贴毂盘顶到 J6; A 从桥板 A 座下来拱过 J6 到 J5
fpc_flat_b = gbox(-18.0, -Y_LED - 5.6, HUB_TOP, 18.0, 12.0, HUB_TOP + FPC_T)
WL_STEP = B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_v1_2.step'
wl = read_step(WL_STEP) if WL_STEP.exists() else gbox(-24.5, -75.5, 32, 24.5, -45, 50)

SUP = dict(post_a=post_a, post_b=post_b, mid_a=mid_a, mid_b=mid_b, bar=bar_s, top=top, comb=comb_s)


def fpc_len():
    """两根 FPC 实际走线 (中线折线 + 弯曲按 r1.5 四分之一圆近似); 端点 = 桥板座插口 (Z39, 朝下) → 底板座触点排"""
    def L(pts):
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    yb = Y_LED + 5.6                                # 桥板座中线 |y| 9.37
    zb = Z0 + 2.0                                   # 座插口 Z39
    zf = HUB_TOP + FPC_T / 2                        # 平铺 Z30.55
    zj = zt + 0.7                                   # 底板座插口中线 Z37.3
    # B: 桥板 B 座 (y −9.37) 往下到毂盘顶, 平铺到 y≈10, 斜上到 J6 口 (y14.5), 进 J6 到触点排 y21.58
    pb = [(-yb, zb + 2.5), (-yb, zf), (10.0, zf), (14.5, zj), (21.58, zj)]
    # A (r3): 桥板 A 座 (y 9.37) 下出后弯向 +y, 拱过 J6 顶 (Z38.6) 爬上 CZ06 顶 (Z43.2 +0.5), 过 CZ06 外沿 y66 折下到 J5 口 (y72), 进到触点排 y79.07
    zc = zt + B.CZ06_H + 0.5
    pa = [(yb, zb + 2.5), (yb, zb), (14.0, 39.2), (23.0, 39.2), (30.82, zc), (65.82, zc), (70.85, zj), (77.92, zj)]   # rev c: J5 口 y70.85, 触点排 y77.92
    return dict(fpc_b_mm=round(L(pb), 1), fpc_a_mm=round(L(pa), 1), path_b_yz=pb, path_a_yz=pa,
                note='座内插入段 2.5 (桥板座) + 到触点排 (底板座); 未计余量 (r3: A 跨 CZ06 顶到外座, 贴 CZ06 顶用聚酰亚胺双面胶)')


def report():
    """干涉 / 转动包络 / 质量平衡 (慢, 几分钟)"""
    # ---------------- 干涉 ----------------
    OTHERS = dict(led_a=led_a, led_b=led_b, bridge_a=br_a, bridge_b=br_b, fpc_conn_a=fpc_a, fpc_conn_b=fpc_b,
                  bb_r2_step=bb_step, bb_r2_pcb=VB['baseboard'], wireless_holder=wl, fpc_flat_b=fpc_flat_b,
                  rim=B.rim, hub=B.hub, shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube,
                  glass_top=B.glass_top, glass_top_hub=B.glass_top_hub, key_bracket=B.key_bracket,
                  **{f'env {k}': v for k, v in env.items()})
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
    fast = h1 + foot_scr + gate_scr + bar_scr + comb_scr
    for nm, s in fast:
        for b in ('led_a', 'led_b', 'bb_r2_step', 'wireless_holder', 'bridge_a', 'bridge_b', 'rim', 'hub', 'shroud_lo', 'shroud_hi', 'key_bracket'):
            v = common_v(s, OTHERS[b])
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[b] = round(v, 3)
        for a, sa in SUP.items():
            v = common_v(s, sa)
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[a] = round(v, 3)
    # 铜螺母 Φ4.2 与 Φ4.2 孔同轴同径, OCC 布尔会把整环算成重叠 ⇒ 校核用 Φ4.1 (孔本身另核: Φ4.1 实心柱 × 毂盘 = 0, 探针量孔径 Φ4.1–4.3)
    chk_ins = ([('M3×4 铜螺母 承载盘 T 脚', ins(x, y, *HUB_INS, d=4.1)) for x, y in FOOT_PTS] + [('M3×4 铜螺母 承载盘 门腿', ins(x, y, *GATE_INS, d=4.1)) for x, y in GATE_PTS]
               + [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, 0, Z1, Z1 + CAP_T, d=4.1)) for sx in (1, -1)])
    # 11-16 晚: T 脚铜螺母在承载盘顶面 (HUB_INS 名字沿用) ⇒ 孔核承载盘 rim (Φ4.1 实心柱 × rim 应 0); 顺带核不进毂盘
    rep['fasteners']['endt_insert_hole_Φ4.1_solid × rim'] = round(sum(common_v(cyl(x, y, 4.1, *HUB_INS), B.rim) for x, y in FOOT_PTS), 4)
    rep['fasteners']['endt_insert_hole_Φ4.1_solid × hub'] = round(sum(common_v(cyl(x, y, 4.1, *HUB_INS), B.hub) for x, y in FOOT_PTS), 4)
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
    rep['screws'] = dict(
        T脚=dict(spec=f'M3×{FOOT_SCREW_L:g} 内六角 ×4', pts=[(round(x, 2), round(y, 2)) for x, y in FOOT_PTS], bear_z=FOOT_CB_Z,
                 tip_z=FOOT_CB_Z - FOOT_SCREW_L, insert_z=HUB_INS, engage=round(min(FOOT_CB_Z, HUB_INS[1]) - max(FOOT_CB_Z - FOOT_SCREW_L, HUB_INS[0]), 2),
                 head_r_max=round(max(math.hypot(abs(x) + 2.75, abs(y)) for x, y in FOOT_PTS), 2), insert='承载盘顶面 M3×4 铜螺母 (END_T_HOLES)'),
        中间T件脚=dict(spec=f'M3×{GATE_SCREW_L:g} 内六角 ×4', pts=GATE_PTS, bear_z=GATE_CB_Z, tip_z=GATE_CB_Z - GATE_SCREW_L, insert_z=GATE_INS,
                 engage=round(min(GATE_CB_Z, GATE_INS[1]) - max(GATE_CB_Z - GATE_SCREW_L, GATE_INS[0]), 2)),
        夹条竖螺丝=dict(spec=f'M3×{BAR_SCR_L:g} 内六角 ×4 从 T 件底面往上 (自攻进夹条 Φ{BAR_TAP_D:g})', x=BAR_SCR_X, bear_z=BAR_SCR_BEAR, tip_z=BAR_SCR_BEAR + BAR_SCR_L, bar_tap=(Z0, Z0 + BAR_TAP_H)),
        梳齿=dict(spec='M3×8 内六角 ×2 → 帽内 M3×4 铜螺母', engage=4.0, slots=len(COMB_SLOTS), slot_r_max=round(max(math.hypot(*p) for p in COMB_SLOTS), 1)))

    # 转动包络 vs 静止件: 每 Z 段转动件最大 r 与静止件最小 r
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.1):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot_parts = [post_a, post_b, mid_a, mid_b, bar_s, top, comb_s, ant_a, ant_b] + [s for _, s in foot_scr + comb_scr]
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
    rep['misc']['rot_r_max'] = dict(post=round(float(max(rz(post_a)[0].max(), rz(post_b)[0].max())), 2), T脚螺丝头=round(float(max(rz(s)[0].max() for _, s in foot_scr)), 2),
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
    for nm, s in foot_scr + gate_scr + bar_scr + h1 + comb_scr:
        m, c = cog(s); add(f'{nm} @({c[0]:.0f},{c[1]:.0f})', m * RHO_ST, *c)
    sup_U = (round(Ux, 1), round(Uy, 1)); bal['supports_U_gmm'] = sup_U
    add('底板 r3 rev b (r3_说明 §3, 不含 FPC/线)', 44.5, -6.3, 43.2, zt + 3.0)
    add('无线模块+固定件 (wireless_holder 11-16)', 39.1, 0.08, -63.39, 41.0)
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
                            note='假设灯板/桥板/玻璃件对称; 罩内配重面 Z 未定 (按 45), 梳齿只修上面残余, 以实测动平衡为准')
    rep['balance'] = bal
    rep['valid'] = {k: BRepCheck_Analyzer(v).IsValid() for k, v in SUP.items()}
    rep['volume_mm3'] = {k: round(vol(v), 1) for k, v in SUP.items()}
    return rep


NAMES = dict(post_a='led_post_a_v1_2', post_b='led_post_b_v1_2', mid_a='led_mid_t_v1_2', mid_b='led_mid_t_v1_2', bar='led_bar_v1_2', top='led_top_v1_2', comb='led_comb_v1_2')
if __name__ == '__main__':
    COL = dict(post_a='#F1C232', post_b='#E69138', mid_a='#B45F06', mid_b='#B45F06', bar='#8E7CC3', top='#6FA8DC', comb='#3D85C6')
    # 打印姿态: 立板/门形正放 (底面 Z32 落床; 门形梁下 Z32–33 窄缝要支撑或桥接); 顶部件倒放 (轴座顶 Φ14 落床, 帽两端小悬空); 梳齿平放
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    rx90 = gp_Trsf(); rx90.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)   # 夹条侧放 (4.6 面落床)
    for k, s in [(k, v) for k, v in SUP.items() if k != 'mid_b']:        # (mid_b = mid_a 转 180°, 同件) 同其他 V1.2 件: models/<件>/<件>.{step,stl} = 装配坐标 (出图用); 打印姿态 STL → out/打印STL/
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
        ('灯板 A (+y) 板框', gbox(-HALF_W, GAP_HALF, Z0, HALF_W, Y_LED, Z1), '#145A32', None, False), ('灯板 B (−y) 板框', gbox(-HALF_W, -Y_LED, Z0, HALF_W, -GAP_HALF, Z1), '#145A32', None, False),
        ('桥板 A', br_a, '#1E8449', None, False), ('桥板 B', br_b, '#1E8449', None, False),
        ('天线 219611 +x 竖', ant_a, '#C0392B', None, False), ('天线 219611 −x 竖', ant_b, '#C0392B', None, False),
        ('底板 r2 板框', VB['baseboard'], '#2E7D32', None, False), ('FPC B 平铺段 (示意)', fpc_flat_b, '#E67E22', None, False)] + [
        (n, s, '#888888', None, False) for n, s in h1 + foot_scr + foot_ins + gate_scr + gate_ins + bar_scr + comb_scr + comb_ins]
    write_doc(items, OUT / 'led_support_装配位.step', 'led_support_asm')
    rep = report()
    json.dump(rep, open(OUT / 'led_support_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
