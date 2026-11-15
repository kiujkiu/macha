"""V2 灯板支撑 (用户 11-14 定: V0.4 portal 改 —— 两端立板 + −x 侧底梁带中间舌 + 顶部件 Φ8 短轴进玻璃上盖 688)。
    cd v1.2/scripts && ../../.venv/bin/python led_support_v1_2.py
世界坐标 (同 build_v1_2): Z0 = 底盘顶, 承载盘顶 Z32, 灯板下沿 Z45.2 / 上沿 Z253.2; 灯板面平行 XZ。
两块 LED_V0.2.0 背靠背: 板 A F 面 (背面) 在 y=+2.3, LED 面 +y; 板 B = 板 A 绕 Z 转 180° (间隙 4.6 = 铜柱, 用户 11-14)。
零件 (打印, PLA/PETG):
  led_post_a_v1_2  +x 端立板: 底块 (2×M3×8 内六角锁承载盘铜螺母) + 立刀 (夹在两板之间, M3 穿 H1) + 竖贴天线板
  led_post_b_v1_2  −x 端立板 + 底梁 (x −75.6…+15, 只在 CZ06 对侧) + 中间舌 (下中 F.Mask 窗) + 横贴天线板
  led_top_v1_2     顶部件: 舌 (上中窗) + 帽压两板上沿 + Φ14 轴座, 压 Φ8×40 钢轴, 轴进玻璃上盖堵头的 688
外购: Φ8×40 钢轴 (h6), 688ZZ, M3×12 内六角 ×2 + M3 法兰螺母 ×2, M3×8 内六角 ×4 + M3×4 铜螺母 ×4,
      Molex 219611 (Wi-Fi 6E 2.4/5/6 GHz, 35×15×0.1, MHF) ×2: −x 近端 219611-0100 (接 P1, 实走≈40), +x 远端 219611-0200 (接 P3, 实走≈175)。
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
def common_v(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return vol(o.Shape()) if o.IsDone() else -1
def cog(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); p = g.CentreOfMass(); return g.Mass(), (p.X(), p.Y(), p.Z())

# ---------------- 灯板 / 间隙 ----------------
Z0 = B.Z_SCR0; Z1 = Z0 + 2 * V.LED_HALF_H          # 45.2 / 253.2075 (STEP 板高 208.0075; 帽底贴板上沿)
GAP_HALF = 2.3                                    # 板 F 面 y=±2.3 (间隙 4.6, 用户 11-14)
PCB_T = 1.468                                     # STEP 板厚 (A10 写 1.54; 按 STEP)
Y_LED = GAP_HALF + PCB_T                          # LED 面 y=±3.768
HALF_W = 81.879                                   # 板半宽
H1_X, H1_Z = 78.63, Z0 + 4.0                      # H1/H2 M3 (±78.63, 下沿+4)
CLR = 0.1                                         # 立刀/舌 与板 F 面单边
BLADE_T = 2 * (GAP_HALF - CLR)                    # 4.4

# ---------------- 两端立板 ----------------
RIM_TOP = B.Z_RIM_TOP                             # 32.0
FOOT_X0, FOOT_X1, FOOT_Y = 71.0, 84.0, 12.0       # 底块 x71–84, |y|≤12 (角 r84.85 < 承载盘 r85)
BLADE_X0, BLADE_X1, BLADE_Z1 = 75.6, 81.6, Z0 + 17.0   # 立刀 x75.6–81.6 (盖住下角 F.Mask 窗 75.9–81.9 / 下沿+7…17), 顶 Z62.2
FOOT_CB_D, FOOT_CB_Z = 6.0, 36.0                  # M3×8 内六角 (头 Φ5.5×3) 沉孔 Φ6, 头支承 Z36 ⇒ 尾 Z28.0, 铜螺母 Z27.8–32 啮合 4.0
FOOT_PTS = [(x, y) for x, y in B.LS_FOOT_PTS]
ANT_X0, ANT_X1 = 82.7, 85.2                       # 天线板 (外面 x=±85.2 贴天线)
ANT_L, ANT_W, ANT_REC = 35.4, 15.4, 0.3           # Molex 219611 35×15×0.1 → 定位浅槽 35.4×15.4×0.3 (背胶贴)
ANT_A = dict(y=9.0, z0=RIM_TOP, z1=72.0, zc=52.0)  # +x 竖贴: 长边沿 Z (槽 Z34.3–69.7), 板 |y|≤9
ANT_B = dict(y=19.0, z0=RIM_TOP, z1=50.0, zc=41.0)  # −x 横贴: 长边沿 Y, 板 |y|≤19, 槽 Z33.3–48.7
SCREW_H1_L = 12.0
# 底梁 (−x 侧, CZ06 对侧; 11-14 用户确认), 中间舌 (下中 F.Mask 窗 x±3 / 下沿+7…17)
BEAM_X0, BEAM_X1, BEAM_Y, BEAM_Z0 = -BLADE_X0, 15.0, 3.9, Z0 - 4.0   # Z41.2–45.2
TONGUE_X, TONGUE_Z1 = 2.8, Z0 + 17.0
# 顶部件 (上中窗 x±3 / 上沿−4…14)
TOP_TONGUE_Z0 = Z1 - 13.7                         # 239.5
CAP_X, CAP_Y, CAP_T = 10.0, 6.0, 4.0
BOSS_D = 14.0
HUB_TIP = B.LOG['glass_top']['hub_z'][0]          # 堵头爪尖底
BOSS_GAP = 3.0                                    # 轴座顶 ↔ 爪尖 (玻璃长短公差)
BOSS_Z1 = HUB_TIP - BOSS_GAP
BRG_Z0 = B.GD_Z1; BRG_Z1 = BRG_Z0 + B.BRG_H       # 688 Z
ROD_D, ROD_L = 8.0, 40.0
ROD_Z1 = BRG_Z1 + 0.5                             # 轴顶伸出轴承 0.5 (上面 Φ9×2.5 让位: 玻璃短 ≤2.0 不顶; 长 ≤4.5 仍有 0.5 啮合)
ROD_Z0 = ROD_Z1 - ROD_L
ROD_HOLE_D = 7.85                                 # 压装孔 (打印孔偏小, 试配)
assert ROD_Z0 > Z1 + CAP_T + 2, ROD_Z0


def post(sx):
    """sx=+1 → +x 端; −1 → −x 端 (镜像)"""
    def X(a, b): return (min(sx * a, sx * b), max(sx * a, sx * b))
    fx = X(FOOT_X0, FOOT_X1); bx = X(BLADE_X0, BLADE_X1); ax = X(ANT_X0, ANT_X1)
    s = gbox(fx[0], -FOOT_Y, RIM_TOP, fx[1], FOOT_Y, Z0)
    s = fuse(s, gbox(bx[0], -BLADE_T / 2, Z0 - 0.01, bx[1], BLADE_T / 2, BLADE_Z1))
    A = ANT_A if sx > 0 else ANT_B
    s = fuse(s, gbox(ax[0], -A['y'], A['z0'], ax[1], A['y'], A['z1']))
    for x, y in FOOT_PTS:
        if x * sx < 0: continue
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, FOOT_CB_Z), cyl(x, y, FOOT_CB_D, FOOT_CB_Z, Z0 + 1))
    s = cut(s, ycyl(sx * H1_X, H1_Z, 3.4, -5, 5))
    xo = sx * ANT_X1
    if sx > 0: rec = gbox(xo - ANT_REC, -ANT_W / 2, A['zc'] - ANT_L / 2, xo + 1, ANT_W / 2, A['zc'] + ANT_L / 2)
    else:      rec = gbox(xo - 1, -ANT_L / 2, A['zc'] - ANT_W / 2, xo + ANT_REC, ANT_L / 2, A['zc'] + ANT_W / 2)
    s = cut(s, rec)
    if sx < 0:
        s = fuse(s, gbox(BEAM_X0, -BEAM_Y, BEAM_Z0, BEAM_X1, BEAM_Y, Z0))
        s = fuse(s, gbox(-TONGUE_X, -BLADE_T / 2, Z0 - 0.01, TONGUE_X, BLADE_T / 2, TONGUE_Z1))
    return clean(s)


def top_piece():
    s = gbox(-TONGUE_X, -BLADE_T / 2, TOP_TONGUE_Z0, TONGUE_X, BLADE_T / 2, Z1 + 0.01)
    s = fuse(s, gbox(-CAP_X, -CAP_Y, Z1, CAP_X, CAP_Y, Z1 + CAP_T))
    s = fuse(s, cyl(0, 0, BOSS_D, Z1 + CAP_T - 0.01, BOSS_Z1))
    s = cut(s, cyl(0, 0, ROD_HOLE_D, ROD_Z0, BOSS_Z1 + 1))
    return clean(s)


post_a, post_b, top = post(+1), post(-1), top_piece()
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

# H1/H2: 板 A (+y) LED 面在 x 67.7–76.3 有 5.9 高电解 (下沿+6…15); 板 B 转 180° 后它到 −x 端 −y 面
# ⇒ +x 端: 头 (Φ5.5) 在 +y, 法兰螺母在 −y; −x 端相反。头 r2.75 离电解角 3.1。
h1 = []
for sx in (1, -1):
    sy_head = 1 if sx > 0 else -1
    h1.append(('M3×12 内六角 灯板 H1/H2', sock(sx * H1_X, H1_Z, sy_head * Y_LED, SCREW_H1_L, axis='y', sy=sy_head)))
    h1.append(('M3 法兰螺母 灯板 H1/H2', fnut_y(sx * H1_X, H1_Z, -sy_head * Y_LED, -sy_head)))
foot_scr = [('M3×8 内六角 立板底脚', sock(x, y, FOOT_CB_Z, 8.0)) for x, y in FOOT_PTS]
foot_ins = [('M3×4 铜螺母 承载盘', cut(cyl(x, y, 4.2, RIM_TOP - 4.2, RIM_TOP), cyl(x, y, 3.0, 0, 40))) for x, y in FOOT_PTS]
# 天线 (35×15×0.1 片 + 中心馈线 Φ1.13 出线 + MHF 插头 2×2×1.2 在 WiFi 模块 IPEX)
ant_a = gbox(ANT_X1, -ANT_W / 2, ANT_A['zc'] - ANT_L / 2, ANT_X1 + 0.1 - ANT_REC, ANT_W / 2, ANT_A['zc'] + ANT_L / 2)
ant_b = gbox(-ANT_X1 - 0.1 + ANT_REC, -ANT_L / 2, ANT_B['zc'] - ANT_W / 2, -ANT_X1, ANT_L / 2, ANT_B['zc'] + ANT_W / 2)

# ---------------- 板子 ----------------
VB = V.make(B)
led_a = xf(VB['led'], tr(0, Y_LED, 0))
led_b = xf(led_a, rotz(180))
# 桥板 64×36×1.6 (B 面 = LED 面, AXK 合高 3.0), 下沿 = 灯板下沿; FPC 座 XW0525512 在桥板外面, 下沿+2…6.4 (插口朝下)
br_a = gbox(-32, Y_LED + 3.0, Z0, 32, Y_LED + 4.6, Z0 + 36)
fpc_a = gbox(-20.75, Y_LED + 4.6, Z0 + 2.0, 20.75, Y_LED + 6.6, Z0 + 6.4)
br_b, fpc_b = xf(br_a, rotz(180)), xf(fpc_a, rotz(180))
BB_DIR = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/review/结构交付')
bb_steps = {k: xf(read_step(BB_DIR / f'POV3D_V2_BaseBoard_r1_{k}.step'), tr(0, 0, B.Z_BB0)) for k in ('pads', 'module')}
# 底板没 3D 模型的件 (交结构 §9) → 按 §3/§4/§5/§7 的框 × 高补包络
zt = B.Z_BB0 + B.BB_T
ENV = {  # 名: (x0,y0,x1,y1,h)
    'J5 FPC': (-20.75, 20.75, 20.75, 28.84, 2.0), 'J6 FPC': (-20.75, -28.84, 20.75, -20.75, 2.0),
    'J8 VH+插头': (57.75, 27.6, 66.7, 37.2, 9.4 + 6.0), 'J10 VH+插头': (-69.7, -39.7, -60.75, -30.1, 9.4 + 6.0),
    'J9 光电 XH+插头': (59.9, 5.5, 66.7, 16.5, 7.0 + 5.0), 'J14': (60.7, -7.55, 66.7, 4.5, 4.5),
    'J13 TF': (-62.0, -4.4, -46.9, 11.4, 1.9), 'U1 WiFi+IPEX': (-69.7, -24.7, -40.6, -4.8, 4.0),
    'CZ06': (21.5, -30.0, 56.5, 30.0, 6.6),
}
env = {k: gbox(a, b_, zt, c, d, zt + h) for k, (a, b_, c, d, h) in ENV.items()}
standoffs = [cut(cyl(x, y, 5.5, RIM_TOP, B.Z_BB0), cyl(x, y, 3.0, 0, 50)) for x, y in B.BB_HOLES]

SUP = dict(post_a=post_a, post_b=post_b, top=top)


def report():
    """干涉 / 转动包络 / 质量平衡 (慢, ~1 min)"""
    # ---------------- 干涉 ----------------
    OTHERS = dict(led_a=led_a, led_b=led_b, bridge_a=br_a, bridge_b=br_b, fpc_conn_a=fpc_a, fpc_conn_b=fpc_b,
                  bb_pads=bb_steps['pads'], bb_module=bb_steps['module'], rim=B.rim, hub=B.hub,
                  shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube,
                  glass_top=B.glass_top, glass_top_hub=B.glass_top_hub, rod=None, key_bracket=B.key_bracket,
                  **{f'env {k}': v for k, v in env.items()})
    OTHERS = {k: v for k, v in OTHERS.items() if v is not None}
    rep = dict(interf={}, fasteners={}, misc={})
    for a, sa in SUP.items():
        for b, sb in OTHERS.items():
            v = common_v(sa, sb)
            if abs(v) > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
        rep['interf'][f'{a} × rod'] = round(common_v(sa, rod), 4)
    for a, b in (('post_a', 'post_b'), ('post_a', 'top'), ('post_b', 'top')):
        v = common_v(SUP[a], SUP[b]);  rep['interf'][f'{a} × {b}'] = round(v, 4) if v > 1e-4 else 0
    for nm, s in h1 + foot_scr:
        for b in ('led_a', 'led_b', 'bb_pads', 'bb_module'):
            v = common_v(s, OTHERS[b])
            if v > 1e-3: rep['fasteners'].setdefault(nm, {})[b] = round(v, 3)
    rep['fasteners']['rod × glass_top_hub'] = round(common_v(rod, B.glass_top_hub), 4)
    rep['fasteners']['688 × glass_top_hub'] = round(common_v(brg, B.glass_top_hub), 4)
    for nm, s in (('antenna_a', ant_a), ('antenna_b', ant_b)):
        for b in ('shroud_lo', 'shroud_hi', 'bb_pads', 'bb_module', 'led_a', 'led_b'):
            v = common_v(s, OTHERS[b])
            if v > 1e-4: rep['fasteners'][f'{nm} × {b}'] = round(v, 4)
    # 底板安装柱 × 板 (柱 Z32–35 在板底下, 应 0)
    rep['fasteners']['standoffs × rim'] = round(sum(common_v(s, B.rim) for s in standoffs), 4)

    # 转动包络 vs 静止件: 每 Z 段转动件最大 r 与静止件最小 r
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.1):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot_parts = [post_a, post_b, top, ant_a, ant_b]
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
    rep['misc']['hub_tip'] = HUB_TIP; rep['misc']['boss_z1'] = BOSS_Z1; rep['misc']['rod_z'] = (ROD_Z0, ROD_Z1); rep['misc']['brg_z'] = (BRG_Z0, BRG_Z1)

    # ---------------- 质量 / 平衡 (打印件按实心 PLA 1.24 g/cm³; 实际填充 <100% 时按比例) ----------------
    RHO = 1.24e-3
    bal = {}
    Ux = Uy = 0.0
    for nm, s in SUP.items():
        m, (cx, cy, cz) = cog(s); g = m * RHO
        bal[nm] = dict(g=round(g, 2), cog=(round(cx, 2), round(cy, 2), round(cz, 1)), U=(round(g * cx, 1), round(g * cy, 1)))
        Ux += g * cx; Uy += g * cy
    bal['supports_U_gmm'] = (round(Ux, 1), round(Uy, 1))
    BB_M, BB_C = 67.4, (2.5, -3.5)                    # pov3d-96 §8 方案 2 估算
    UBx, UBy = BB_M * BB_C[0], BB_M * BB_C[1]
    bal['baseboard_U_gmm'] = (round(UBx, 1), round(UBy, 1))
    TX, TY = Ux + UBx, Uy + UBy
    CW_R = B.CW_R
    bal['total_U_gmm'] = (round(TX, 1), round(TY, 1)); bal['total_U_abs'] = round(math.hypot(TX, TY), 1)
    bal['cw_r'] = CW_R; bal['cw_g'] = round(math.hypot(TX, TY) / CW_R, 2)
    bal['cw_ang_deg'] = round(math.degrees(math.atan2(-TY, -TX)) % 360, 1)
    rep['balance'] = bal
    rep['valid'] = {k: BRepCheck_Analyzer(v).IsValid() for k, v in SUP.items()}
    rep['volume_mm3'] = {k: round(vol(v), 1) for k, v in SUP.items()}

    return rep


if __name__ == '__main__':
    COL = dict(post_a='#F1C232', post_b='#E69138', top='#6FA8DC')
    NAMES = dict(post_a='led_post_a_v1_2', post_b='led_post_b_v1_2', top='led_top_v1_2')
    # 打印姿态: 立板照装配正放 (底块落床; −x 件底梁下 Z32–41.2 要支撑); 顶部件倒放 (轴座顶 Φ14 落床, 帽两端 3 mm 小悬空)
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
        ('Φ8×40 钢轴', rod, '#999999', None, False), ('688ZZ', brg, '#666666', None, False),
        ('灯板 A (+y) 板框', gbox(-HALF_W, GAP_HALF, Z0, HALF_W, Y_LED, Z1), '#145A32', None, False), ('灯板 B (−y) 板框', gbox(-HALF_W, -Y_LED, Z0, HALF_W, -GAP_HALF, Z1), '#145A32', None, False),
        ('桥板 A', br_a, '#1E8449', None, False), ('桥板 B', br_b, '#1E8449', None, False),
        ('天线 219611 +x 竖', ant_a, '#C0392B', None, False), ('天线 219611 −x 横', ant_b, '#C0392B', None, False),
        ('底板 r1 方案1 板框 (外接)', gbox(-70, -40, B.Z_BB0, 67, 44, B.Z_BB0 + B.BB_T), '#2E7D32', None, False)] + [
        (n, s, '#888888', None, False) for n, s in h1 + foot_scr + foot_ins]
    write_doc(items, OUT / 'led_support_装配位.step', 'led_support_asm')
    rep = report()
    json.dump(rep, open(OUT / 'led_support_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
