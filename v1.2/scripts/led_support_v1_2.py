"""V2 灯板支撑 (11-14 定 V0.4 portal 改; 11-16 按新转子布局重做: 灯板下沿 Z45.2 → Z37, 底板 r2 在 +y, 无线模块在 −y)。
    cd v1.2/scripts && ../../.venv/bin/python led_support_v1_2.py
世界坐标 (同 build_v1_2): Z0 = 底盘顶, 承载盘顶 Z32 (r<24.5 毂盘顶 Z30.4), 灯板下沿 B.Z_SCR0 = 37 / 上沿 245.0; 灯板面平行 XZ。
两块 LED_V0.2.0 背靠背: 板 A F 面 (背面) 在 y=+2.3, LED 面 +y; 板 B = 板 A 绕 Z 转 180° (间隙 4.6 = 铜柱, 用户 11-14)。
零件 (打印, PETG/PLA):
  led_post_a_v1_2  +x 端立板: T 形底脚 (横杆沿 y 到承载盘原 R82.5 孔 @22.5°/337.5°, 2×M3×16 内六角从上穿承载盘+毂盘进毂盘底铜螺母)
                   + 立刀 (夹在两板之间, M3 穿 H1) + 竖贴天线板 (外面 r≤84.7)
  led_post_b_v1_2  −x 端立板 (镜像, 孔 @157.5°/202.5°)
  led_gate_v1_2    中间门形支撑: 两腿 (±30,0) 各 1×M3×6 进承载盘铜螺母, 横梁 x−30..30 顶 Z37 托两板下沿, 梁下给 FPC 留缝, 中间立舌进下中 F.Mask 窗
  led_top_v1_2     顶部件: 舌 (上中窗) + 帽压两板上沿 + Φ14 轴座 (加长 8.2), 压 Φ8×50 钢轴, 轴进玻璃上盖堵头的 688; 帽上 2×M3×4 铜螺母锁梳齿
  led_comb_v1_2    顶部配平梳齿: 横梁沿 x 套在轴座上、坐帽顶 (2×M3×8 锁帽), 每侧 4 个齿 (沿 y), 每齿 4 个 Φ3.4 竖孔挂 M3 螺丝+螺母配重
外购: Φ8×50 钢轴 (h6), 688ZZ; M3×16 内六角 ×4 (T 脚) + 毂盘底 M3×4 铜螺母 ×4 (原有孔); M3×6 内六角 ×2 + 承载盘 M3×4 铜螺母 ×2 (门腿);
      M3×12 内六角 ×2 + M3 法兰螺母 ×2 (H1/H2); M3×8 内六角 ×2 + M3×4 铜螺母 ×2 (梳齿 → 帽); 配重 M3×8 + M3 螺母 (按需);
      Molex 219611 (Wi-Fi 6E, 35×15×0.1, MHF) ×2 竖贴两端。
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
R_CLIP = 85.0                                     # 底脚外缘 ≤ 承载盘外缘 r85 (转子罩内壁 r86)

# ---------------- 两端立板: T 形底脚 ----------------
# 承载盘 R82.5 原孔 (22.5°+45k; 灯板用 22.5/157.5/202.5/337.5°): 承载盘 Z27–32 Φ3.6 通, 毂盘 Z26–27 Φ3.4 + 毂盘底 Φ4.2 Z21.5–26 铜螺母孔 (实测)
R_HOLE = 82.5
FOOT_PTS = [(R_HOLE * math.cos(math.radians(a)), R_HOLE * math.sin(math.radians(a))) for a in (22.5, 337.5, 157.5, 202.5)]   # (±76.22, ±31.57)
HUB_BOT = 21.5                                    # 毂盘底面
HUB_INS = (HUB_BOT, HUB_BOT + 4.0)                # M3×4 铜螺母 (毂盘底 Φ4.2×4.5 孔, 底面齐平压入) Z21.5–25.5
FOOT_SCREW_L = 16.0                               # M3×16 内六角
FOOT_CB_Z = HUB_BOT + FOOT_SCREW_L                # 头支承 Z37.5 ⇒ 尾 Z21.5 (= 毂盘底, 不露), 啮合 4.0
FOOT_CB_D = 0.0                                   # 不沉孔: 头坐在 Φ8 凸台顶 (凸台在 |y|31.6, 离灯板远)
PAD_D = 8.0                                       # 孔凸台 Φ8, Z32–37.5
T_X = R_HOLE * math.cos(math.radians(22.5))       # 76.22 横杆中线
T_W = 8.0                                         # 横杆宽 (x 72.22–80.22)
FOOT_X0, FOOT_X1 = T_X - T_W / 2, None            # 兼容旧名 (FOOT_X1 = ANT_X1, 下面定)
BLADE_X0, BLADE_X1, BLADE_Z1 = 75.6, 81.6, Z0 + 17.0   # 立刀 x75.6–81.6 (盖住下角 F.Mask 窗 75.9–81.9 / 下沿+7…17), 顶 Z54; 实体向外延到天线板
# 天线板: 两端都竖贴; 外面 r≤84.7 (转子罩内壁 r86 要让); 内面让 H1 法兰螺母 (Φ7.6 → x82.43)
ANT_X0, ANT_X1, ANT_HW = 82.6, 84.3, 8.0          # 厚 1.7, |y|≤8 ⇒ 外角 r = hypot(84.3, 8) = 84.68
ANT_R_MAX = 84.7
ANT_L, ANT_W, ANT_REC = 35.4, 15.4, 0.3           # Molex 219611 35×15×0.1 → 定位浅槽 35.4×15.4×0.3 (背胶贴)
ANT_ZC = 56.6                                     # 槽 Z38.9–74.3 (长边沿 Z)
ANT_Z1 = ANT_ZC + ANT_L / 2 + 1.3                 # 板顶 Z75.6
ANT_A = dict(y=ANT_HW, z0=RIM_TOP, z1=ANT_Z1, zc=ANT_ZC)   # 兼容旧名 (两端相同)
ANT_B = ANT_A
FOOT_X1 = ANT_X1
FOOT_Y = R_HOLE * math.sin(math.radians(22.5))    # 31.57 (T 杆半长)
SCREW_H1_L = 12.0

# ---------------- 中间门形支撑 ----------------
GATE_PTS = [tuple(p) for p in B.GATE_PTS]         # (±30, 0) 承载盘 Φ4.2×4.2 铜螺母孔 (build 已切)
GATE_INS = (RIM_TOP - 4.0, RIM_TOP)               # M3×4 铜螺母 Z28–32
GATE_SCREW_L = 6.0                                # M3×6 内六角
GATE_CB_D, GATE_CB_Z = 6.0, GATE_INS[0] + GATE_SCREW_L   # 头 Φ5.5×3 沉孔 Φ6 底 Z34 ⇒ 头顶 Z37 (与梁顶齐), 尾 Z28, 啮合 4.0
LEG_HX, LEG_HY = 4.0, 4.5                         # 腿 8×9 (Φ6 沉孔壁 ≥1.0)
BEAM_X0, BEAM_X1, BEAM_Y = -30.0, 30.0, 3.9       # 横梁 x−30..30, |y|≤3.9 (盖住两板 |y|≤3.768)
FPC_T, FPC_CLR = 0.3, 2.0                         # FPC 平铺在毂盘顶 Z30.4 (|x|≤18 ⇒ r≤23 全在毂盘上); 梁下净空 ≥2
BEAM_Z0 = 33.0                                    # 梁底 (FPC 顶 30.7 → 2.3 净空)
assert BEAM_Z0 - (HUB_TOP + FPC_T) >= FPC_CLR
TONGUE_X, TONGUE_Z1 = 2.8, Z0 + 17.0              # 立舌 x±2.8 y±2.2, 到下沿+17 (下中 F.Mask 窗 下沿+7…17)

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
    """sx=+1 → +x 端 (孔 22.5°/337.5°); −1 → −x 端 (镜像, 157.5°/202.5°)"""
    def X(a, b): return (min(sx * a, sx * b), max(sx * a, sx * b))
    tx = X(T_X - T_W / 2, ANT_X1); bx = X(BLADE_X0, ANT_X0 + 0.01); ax = X(ANT_X0, ANT_X1)
    pts = [(x, y) for x, y in FOOT_PTS if x * sx > 0]
    # T 脚: 中段 (横杆 + 接天线板) Z32–37 (顶 = 灯板下沿, 托两板), 横杆沿 y 到 |y|31.57, 孔凸台 Φ8 到 Z37.5
    s = gbox(tx[0], -ANT_HW, RIM_TOP, tx[1], ANT_HW, Z0)
    s = fuse(s, gbox(sx * T_X - T_W / 2, -FOOT_Y, RIM_TOP, sx * T_X + T_W / 2, FOOT_Y, Z0))
    for x, y in pts: s = fuse(s, cyl(x, y, PAD_D, RIM_TOP, FOOT_CB_Z))
    s = common(s, cyl(0, 0, 2 * R_CLIP, RIM_TOP - 1, FOOT_CB_Z + 1))
    s = fuse(s, gbox(bx[0], -BLADE_T / 2, Z0 - 0.01, bx[1], BLADE_T / 2, BLADE_Z1))
    s = fuse(s, common(gbox(ax[0], -ANT_HW, RIM_TOP, ax[1], ANT_HW, ANT_Z1), cyl(0, 0, 2 * ANT_R_MAX, RIM_TOP - 1, ANT_Z1 + 1)))
    for x, y in pts:
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, FOOT_CB_Z + 1))
    s = cut(s, ycyl(sx * H1_X, H1_Z, 3.4, -5, 5))
    xo = sx * ANT_X1
    rec = gbox(min(xo - sx * ANT_REC, xo + sx * 1), -ANT_W / 2, ANT_ZC - ANT_L / 2, max(xo - sx * ANT_REC, xo + sx * 1), ANT_W / 2, ANT_ZC + ANT_L / 2)
    s = cut(s, rec)
    return clean(s)


def gate():
    s = gbox(BEAM_X0, -BEAM_Y, BEAM_Z0, BEAM_X1, BEAM_Y, Z0)
    for x, y in GATE_PTS:
        s = fuse(s, gbox(x - LEG_HX, y - LEG_HY, RIM_TOP, x + LEG_HX, y + LEG_HY, Z0))
    s = fuse(s, gbox(-TONGUE_X, -BLADE_T / 2, Z0 - 0.01, TONGUE_X, BLADE_T / 2, TONGUE_Z1))
    for x, y in GATE_PTS:
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, Z0 + 1), cyl(x, y, GATE_CB_D, GATE_CB_Z, Z0 + 1))
    return clean(s)


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
post_a, post_b, gate_s, top, comb_s = post(+1), post(-1), gate(), top_piece(), comb()
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
foot_scr = [('M3×16 内六角 T 脚', sock(x, y, FOOT_CB_Z, FOOT_SCREW_L)) for x, y in FOOT_PTS]
foot_ins = [('M3×4 铜螺母 毂盘底 T 脚', ins(x, y, *HUB_INS)) for x, y in FOOT_PTS]
gate_scr = [('M3×6 内六角 门腿', sock(x, y, GATE_CB_Z, GATE_SCREW_L)) for x, y in GATE_PTS]
gate_ins = [('M3×4 铜螺母 承载盘 门腿', ins(x, y, *GATE_INS)) for x, y in GATE_PTS]
comb_scr = [('M3×8 内六角 梳齿→帽', sock(sx * COMB_FIX_X, 0, COMB_Z1, 8.0)) for sx in (1, -1)]
comb_ins = [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, 0, Z1, Z1 + CAP_T)) for sx in (1, -1)]
# 天线 (35×15×0.1 片), 外面 x=±(ANT_X1 − 0.2)
ant_a = gbox(ANT_X1 - ANT_REC, -ANT_W / 2 + 0.2, ANT_ZC - 17.5, ANT_X1 - ANT_REC + 0.1, ANT_W / 2 - 0.2, ANT_ZC + 17.5)
ant_b = xf(ant_a, rotz(180))

# ---------------- 板子 ----------------
VB = V.make(B)
led_a = xf(VB['led'], tr(0, Y_LED, 0))
led_b = xf(led_a, rotz(180))
# 桥板 64×36×1.6 (B 面 = LED 面, AXK 合高 3.0), 下沿 = 灯板下沿; FPC 座 XW0525512 在桥板外面, 下沿+2…6.4 (插口朝下)
br_a = gbox(-32, Y_LED + 3.0, Z0, 32, Y_LED + 4.6, Z0 + 36)
fpc_a = gbox(-20.75, Y_LED + 4.6, Z0 + 2.0, 20.75, Y_LED + 6.6, Z0 + 6.4)
br_b, fpc_b = xf(br_a, rotz(180)), xf(fpc_a, rotz(180))
bb_step = VB['bb_step']                            # r2 交付 STEP (已 +Z_BB0)
# r2 没 3D 模型的件 (r2_说明 §1–§5) → 框 × 高 (板顶以上)
zt = B.Z_BB0 + B.BB_T
ENV = {  # 名: (x0,y0,x1,y1,h)
    'J5 FPC 外座': (-20.75, 25.36, 20.75, 33.44, 2.0), 'J6 FPC 内座': (-20.75, 14.5, 20.75, 22.59, 2.0),
    'J8 VH 立式+插头': (37.3, 31.3, 46.25, 40.89, 10.0 + 7.0), 'J10 VH 立式+插头': (37.3, 21.4, 46.25, 30.99, 10.0 + 7.0),
    'J9 XH 立式+插头': (30.7, 41.6, 37.54, 52.59, 7.0 + 5.0), 'J11 排针': (30.7, 57.6, 35.61, 60.79, 4.5), 'J12 排针': (30.7, 53.8, 39.42, 56.99, 4.5),
    'J13 TF': (21.2, 14.5, 36.29, 30.29, 2.0), 'U1 WiFi+IPEX': (-50.8, 35.45, -30.91, 64.54, 4.0),
    'CZ06 (DF40+板+件)': (-30.0, 36.0, 30.0, 71.0, B.CZ06_H), 'P1 24V 焊盘+线头': (-31.05, 31.31, -20.96, 35.39, 3.0),
}
env = {k: gbox(a, b_, zt, c, d, zt + h) for k, (a, b_, c, d, h) in ENV.items()}
env['底面件 (r2 B.CrtYd × 限高)'] = VB['bb_parts']
# 灯板 J3 (VH 立式, LED 面) + 插头: 板 A 在 +x (y 3.77–26), 板 B 在 −x (−y)
env['J3 插头 板A'] = gbox(54.85, Y_LED, Z0 + 1.4, 63.55, 26.0, Z0 + 11.0); env['J3 插头 板B'] = xf(env['J3 插头 板A'], rotz(180))
# 24V 线 (无线模块 → P1): 贴盘面到 (−40,−40), 沿 x≈−40 从灯板下缝穿到 +y (Φ3 包络)
env['24V 线 x≈−40'] = gbox(-41.5, -40.0, RIM_TOP, -38.5, 30.0, RIM_TOP + 3.0)
# 两根 FPC (平铺段, 0.3 厚): B 从桥板 B 座下来贴毂盘顶到 J6; A 从桥板 A 座下来拱过 J6 到 J5
fpc_flat_b = gbox(-18.0, -Y_LED - 5.6, HUB_TOP, 18.0, 12.0, HUB_TOP + FPC_T)
WL_STEP = B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_v1_2.step'
wl = read_step(WL_STEP) if WL_STEP.exists() else gbox(-24.5, -75.5, 32, 24.5, -45, 50)

SUP = dict(post_a=post_a, post_b=post_b, gate=gate_s, top=top, comb=comb_s)


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
    # A: 桥板 A 座 (y 9.37) 下出 1.5 后弯向 +y, 拱过 J6 顶 (Z38.6, 留 0.4) 到 J5 口 (y25.36), 进到触点排 y32.42
    pa = [(yb, zb + 2.5), (yb, zj), (12.0, 39.0), (23.0, 39.0), (25.36, zj), (32.42, zj)]
    return dict(fpc_b_mm=round(L(pb), 1), fpc_a_mm=round(L(pa), 1), path_b_yz=pb, path_a_yz=pa,
                note='座内插入段 2.5 (桥板座) + 到触点排 (底板座); 未计余量, 建议 B ≥50、A ≥35 (A 要在 J6 顶上拱 S 弯)')


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
    fast = h1 + foot_scr + gate_scr + comb_scr
    for nm, s in fast:
        for b in ('led_a', 'led_b', 'bb_r2_step', 'wireless_holder', 'bridge_a', 'bridge_b', 'rim', 'hub', 'shroud_lo', 'shroud_hi', 'key_bracket'):
            v = common_v(s, OTHERS[b])
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[b] = round(v, 3)
        for a, sa in SUP.items():
            v = common_v(s, sa)
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[a] = round(v, 3)
    # 铜螺母 Φ4.2 与 Φ4.2 孔同轴同径, OCC 布尔会把整环算成重叠 ⇒ 校核用 Φ4.1 (孔本身另核: Φ4.1 实心柱 × 毂盘 = 0, 探针量孔径 Φ4.1–4.3)
    chk_ins = ([('M3×4 铜螺母 毂盘底 T 脚', ins(x, y, *HUB_INS, d=4.1)) for x, y in FOOT_PTS] + [('M3×4 铜螺母 承载盘 门腿', ins(x, y, *GATE_INS, d=4.1)) for x, y in GATE_PTS]
               + [('M3×4 铜螺母 帽', ins(sx * COMB_FIX_X, 0, Z1, Z1 + CAP_T, d=4.1)) for sx in (1, -1)])
    rep['fasteners']['hub_insert_hole_Φ4.1_solid × hub'] = round(sum(common_v(cyl(x, y, 4.1, *HUB_INS), B.hub) for x, y in FOOT_PTS), 4)
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
                 head_r_max=round(R_HOLE + 2.75, 2)),
        门腿=dict(spec=f'M3×{GATE_SCREW_L:g} 内六角 ×2', pts=GATE_PTS, bear_z=GATE_CB_Z, tip_z=GATE_CB_Z - GATE_SCREW_L, insert_z=GATE_INS,
                 engage=round(min(GATE_CB_Z, GATE_INS[1]) - max(GATE_CB_Z - GATE_SCREW_L, GATE_INS[0]), 2)),
        梳齿=dict(spec='M3×8 内六角 ×2 → 帽内 M3×4 铜螺母', engage=4.0, slots=len(COMB_SLOTS), slot_r_max=round(max(math.hypot(*p) for p in COMB_SLOTS), 1)))

    # 转动包络 vs 静止件: 每 Z 段转动件最大 r 与静止件最小 r
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.1):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot_parts = [post_a, post_b, gate_s, top, comb_s, ant_a, ant_b] + [s for _, s in foot_scr + comb_scr]
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
    rep['misc']['beam_fpc_clear'] = round(BEAM_Z0 - (HUB_TOP + FPC_T), 2)
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
    for nm, s in foot_scr + gate_scr + h1 + comb_scr:
        m, c = cog(s); add(f'{nm} @({c[0]:.0f},{c[1]:.0f})', m * RHO_ST, *c)
    sup_U = (round(Ux, 1), round(Uy, 1)); bal['supports_U_gmm'] = sup_U
    add('底板 r2 (r2_说明 §6, 不含 FPC/线)', 44.9, -5.1, 43.5, zt + 3.0)
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


NAMES = dict(post_a='led_post_a_v1_2', post_b='led_post_b_v1_2', gate='led_gate_v1_2', top='led_top_v1_2', comb='led_comb_v1_2')
if __name__ == '__main__':
    COL = dict(post_a='#F1C232', post_b='#E69138', gate='#B45F06', top='#6FA8DC', comb='#3D85C6')
    # 打印姿态: 立板/门形正放 (底面 Z32 落床; 门形梁下 Z32–33 窄缝要支撑或桥接); 顶部件倒放 (轴座顶 Φ14 落床, 帽两端小悬空); 梳齿平放
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    for k, s in SUP.items():        # 同其他 V1.2 件: models/<件>/<件>.{step,stl} = 装配坐标 (出图用); 打印姿态 STL → out/打印STL/
        d = B.V12 / 'models' / NAMES[k]; d.mkdir(exist_ok=True)
        write_doc([(NAMES[k], s, COL[k], None, False)], d / f'{NAMES[k]}.step', NAMES[k])
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(d / f'{NAMES[k]}.stl'))
        t = xf(s, fx) if k == 'top' else s
        bb = bbox(t); t = xf(t, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAMES[k]}.stl'))
    items = [(NAMES[k], s, COL[k], None, False) for k, s in SUP.items()] + [
        (f'Φ8×{ROD_L:g} 钢轴', rod, '#999999', None, False), ('688ZZ', brg, '#666666', None, False),
        ('灯板 A (+y) 板框', gbox(-HALF_W, GAP_HALF, Z0, HALF_W, Y_LED, Z1), '#145A32', None, False), ('灯板 B (−y) 板框', gbox(-HALF_W, -Y_LED, Z0, HALF_W, -GAP_HALF, Z1), '#145A32', None, False),
        ('桥板 A', br_a, '#1E8449', None, False), ('桥板 B', br_b, '#1E8449', None, False),
        ('天线 219611 +x 竖', ant_a, '#C0392B', None, False), ('天线 219611 −x 竖', ant_b, '#C0392B', None, False),
        ('底板 r2 板框', VB['baseboard'], '#2E7D32', None, False), ('FPC B 平铺段 (示意)', fpc_flat_b, '#E67E22', None, False)] + [
        (n, s, '#888888', None, False) for n, s in h1 + foot_scr + foot_ins + gate_scr + gate_ins + comb_scr + comb_ins]
    write_doc(items, OUT / 'led_support_装配位.step', 'led_support_asm')
    rep = report()
    json.dump(rep, open(OUT / 'led_support_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
