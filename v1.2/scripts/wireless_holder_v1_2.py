"""V1.2 无线供电接收模块固定件 (用户 11-16: 线圈 → 24V 模块独立放转子盘 −y 侧, 两根线送 24V 到底板 r2)。
    cd v1.2/scripts && ../../.venv/bin/python wireless_holder_v1_2.py
世界坐标 (同 build_v1_2): Z0 = 底盘顶, 承载盘顶 Z32, 灯板下沿 Z37, 灯板面平行 XZ。
11-16 晚改 (转子罩壁缩到 r82–85, 照 V0.4): 托盘 + 模块 + 引脚/螺丝/铜螺母整体随 B.MOD_HOLES 往 +y 挪 3,
    外墙外面 r84.5 → r81.7 (罩内壁 r82 留 0.3); 整件最大半径 81.7。
11-16 晚 Φ175 方案 A 时外墙曾放宽到 r84.2; 同晚转子改回 Φ170 (罩内壁 r82) ⇒ 外墙外面收回 r81.7 (托盘/螺丝位置不动 = B.MOD_HOLES 不动);
    灯板组平移 SCR_ECC (−4.36) 后禁区随之平移 (板 B MIP 顶 y−8.72), 中间 T 件取消, 两端立板改耳朵脚 (x≥69), 罩底凸台 @B.SHR_ANG。
模块: 30.5×49×15, 19.2 g, 长边沿 x, 中心 (0, MOD_YC) = (0, −56.75), y −72…−41.5; 引脚 (KiCad POV3D_V2_BaseBoard_r1 P1 "AC-DC24V_Module" 封装, 框 48.6×30):
    1/2 = AC (接线圈) 在 +x 短边, 3 = 24V / 4 = GND 在 −x 短边; 假设脚从模块底面朝下伸出 ≤3 (托盘底窗口内焊线)。
固定件 (打印 PETG/PLA, 一件):
  托盘底 3 厚 (Z32–35) + 外侧 (−y, 径向外) 承力厚墙 (外面 r81.7 圆弧, 挡离心力; x=0 处厚 9.7, 角 (±26.5, −77.28) 厚 5.3)
  + 两端侧墙 + 内侧矮墙;
  3×M3×8 内六角锁承载盘铜螺母: 外墙内 2 颗 (±11, −76.5) (r77.3, 沉孔 Φ6 外缘 r80.3, 到墙外面剩 1.4) + 内侧舌 1 颗 (0, −28) (r28);
  2 条扎带 (4.8 宽, y −55 / −62.5, 槽在两窗之间) 沿 x 绕 "模块顶 → 侧墙外槽 → 托盘底面槽" 压住模块;
  4 个底窗: +x 端 2 个对承载盘 AC 引线孔 (21, −70) / (21, −49) (线圈线 Φ3 孔直上进底窗, 焊 AC1 (21.5, −69.25) / AC2 (22.3, −44) 脚;
            AC2 窗 y −51.5…−41.5 同时罩住孔和脚, 线在 3 深窗内横走 5); −x 端 2 个从侧墙底穿出
            (24V (−21.6, −43.75) / GND (−22.0, −68.5) 线贴承载盘顶面向 −x 出, 到 x≈−55 再沿 +y 去底板)。
输出: v1.2/models/wireless_holder_v1_2/wireless_holder_v1_2.{step,stl} (装配坐标, STEP 含模块占位/螺丝/铜螺母/引脚)
      out/打印STL/wireless_holder_v1_2.stl (打印姿态 = 装配姿态, 底落床)
      models/wireless_holder_v1_2/wireless_holder_report.json
"""
import io, contextlib, json, math
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
from helpers import write_doc
from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool

cyl, cut, fuse, clean, gbox, vol, bbox, xf = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf
NAME = 'wireless_holder_v1_2'
OUT = B.V12 / 'models' / NAME; OUT.mkdir(parents=True, exist_ok=True)
def tr(dx, dy, dz): t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz)); return t
def max_r(s):                               # 最大半径: 网格顶点 + 圆柱/圆弧 (取包围盒角与 r 采样的保守值)
    BRepMesh_IncrementalMesh(s, 0.01, False, 0.05, True)
    ex = TopExp_Explorer(s, TopAbs_FACE); r = 0.0
    while ex.More():
        f = TopoDS.Face(ex.Current()) if hasattr(TopoDS, "Face") else TopoDS.Face_s(ex.Current()); loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(loc.Transformation()); r = max(r, math.hypot(p.X(), p.Y()))
        ex.Next()
    return r
def common_v(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return vol(o.Shape()) if o.IsDone() else -1
def cog(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); p = g.CentreOfMass(); return g.Mass(), (p.X(), p.Y(), p.Z())

# ---------------- 尺寸 ----------------
RIM_TOP = B.Z_RIM_TOP                       # 32.0
MOD_L, MOD_W, MOD_H, MOD_G = 49.0, 30.5, 15.0, 19.2
SCR_OUT = sorted(h for h in B.MOD_HOLES if h[1] < -50)    # 外墙 2 颗 (±11, −76.5)
SCR_IN = [h for h in B.MOD_HOLES if h[1] >= -50]           # 内舌 1 颗 (0, −28)
assert len(SCR_OUT) == 2 and len(SCR_IN) == 1, B.MOD_HOLES
MOD_Y0 = SCR_OUT[0][1] + 4.5                # 模块外 (−y) 长边 −72 (螺丝外 4.5, 同原关系); 角 (±24.5, −72) r76.1
MOD_Y1 = MOD_Y0 + MOD_W                     # −41.5
MOD_YC = (MOD_Y0 + MOD_Y1) / 2              # −56.75
FLOOR_T = 3.0
MZ0 = RIM_TOP + FLOOR_T; MZ1 = MZ0 + MOD_H  # 模块 Z35–50
HX = MOD_L / 2                              # 24.5
SIDE_T, SIDE_Z1 = 2.0, MZ0 + 10.0           # 侧墙 2 厚, 顶 Z45
IN_T, IN_Z1 = 2.0, MZ0 + 5.0                # 内侧矮墙 2 厚, 顶 Z40
OUT_R, OUT_Z1 = 81.7, MZ1                   # 外墙外面 r81.7 (11-16 晚 改回 Φ170: 转子罩壁 r82–85, 留 0.3; Φ175 时曾 r84.2), 顶 = 模块顶 Z50
OX = HX + SIDE_T                            # 26.5 外包 x
R_MAX = 81.7                                # 罩内一切 ≤ r81.7
SHR_R0, SHR_R1 = 82.0, 85.0                 # 转子罩壁 (Φ175 时曾 84.5/87.5)
ECC = B.SCR_ECC                             # −4.36 灯板组 y 平移
CB_D, CB_Z = 6.0, RIM_TOP + 4.0             # M3×8 头 Φ5.5×3 → 沉孔 Φ6, 头支承 Z36 ⇒ 尾 Z28, 铜螺母 Z27.8–32 啮合 4
TONGUE_X, TONGUE_Y1, TONGUE_Z1 = 6.0, SCR_IN[0][1] + 4.0, RIM_TOP + 4.0   # 内舌到 y −24
# 引脚 (封装本地 fx 向右, fy 向下, 框 48.6×30; 绕 Z 转 180° 使 AC 在 +x): X = −(fx − 24.3), Y = MOD_YC + (fy − 15)
FP = {'AC1': (2.8, 2.5), 'AC2': (2.0, 27.75), '24V': (45.91, 28.0), 'GND': (46.28, 3.22)}
PINS = {k: (round(-(fx - 24.3), 2), round(MOD_YC + (fy - 15.0), 2)) for k, (fx, fy) in FP.items()}
AC_HOLES = sorted(B.AC_HOLES, key=lambda h: h[1])   # (21, −70) / (21, −49): 线圈腔 r34–76 上方 (没动, 模块挪了窗按孔+脚取)
# 底窗 (x0, x1, y0, y1); −x 端两个穿出侧墙。AC 窗同时罩住承载盘孔 (Φ3 + 0.5 余) 和模块脚
_ac1 = max(AC_HOLES[0][1] + 2.0, PINS['AC1'][1] + 2.0)       # −67.25
_ac2 = min(AC_HOLES[1][1] - 2.5, PINS['AC2'][1] - 3.0)       # −51.5
WIN = {'AC1': (17.0, HX, MOD_Y0, _ac1), 'AC2': (17.0, HX, _ac2, MOD_Y1),
       'GND': (-OX - 1, -17.0, MOD_Y0, PINS['GND'][1] + 2.5), '24V': (-OX - 1, -17.0, PINS['24V'][1] - 4.75, MOD_Y1)}
TIE_W, TIE_T = 5.0, 1.5                     # 扎带 4.8×1.2 → 槽 5×1.5
TIE_Y = [-55.0, -62.5]                      # 两窗之间 (y −66…−51.5; 槽 −65…−52.5)
for _y in TIE_Y:
    assert all(not (w[2] < _y + TIE_W / 2 and _y - TIE_W / 2 < w[3]) for w in WIN.values()), ('扎带槽撞底窗', _y)

# ---------------- 固定件 ----------------
def holder():
    s = gbox(-OX, MOD_Y0, RIM_TOP, OX, MOD_Y1 + IN_T, MZ0)                                   # 底
    s = fuse(s, B.op(BRepAlgoAPI_Common, gbox(-OX, -OUT_R - 1, RIM_TOP, OX, MOD_Y0, OUT_Z1), cyl(0, 0, 2 * OUT_R, RIM_TOP - 1, OUT_Z1 + 1)))  # 外墙
    for sx in (1, -1):
        x0, x1 = (HX, OX) if sx > 0 else (-OX, -HX)
        s = fuse(s, gbox(x0, MOD_Y0 - 0.01, RIM_TOP, x1, MOD_Y1 + IN_T, SIDE_Z1))             # 侧墙
    s = fuse(s, gbox(-OX, MOD_Y1, RIM_TOP, OX, MOD_Y1 + IN_T, IN_Z1))                        # 内矮墙
    s = fuse(s, gbox(-TONGUE_X, MOD_Y1 + IN_T - 0.01, RIM_TOP, TONGUE_X, TONGUE_Y1, TONGUE_Z1))  # 内舌
    for x, y in SCR_OUT + SCR_IN:
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, CB_Z), cyl(x, y, CB_D, CB_Z, OUT_Z1 + 1))
    for x0, x1, y0, y1 in WIN.values():
        s = cut(s, gbox(x0, y0, RIM_TOP - 1, x1, y1, MZ0 + 0.01))
    for y in TIE_Y:
        y0, y1 = y - TIE_W / 2, y + TIE_W / 2
        s = cut(s, gbox(-OX - 1, y0, RIM_TOP - 1, OX + 1, y1, RIM_TOP + TIE_T))            # 底面槽
        for sx in (1, -1):
            xa, xb = (OX - TIE_T, OX + 1) if sx > 0 else (-OX - 1, -OX + TIE_T)
            s = cut(s, gbox(xa, y0, RIM_TOP - 1, xb, y1, SIDE_Z1 + 1))                       # 侧墙外槽
    return clean(s)

H = holder()
module = gbox(-HX, MOD_Y0, MZ0, HX, MOD_Y1, MZ1)
pins = {k: cyl(x, y, 1.0, MZ0 - 2.5, MZ0) for k, (x, y) in PINS.items()}   # 示意: 脚伸出 2.5 (在底窗内)
def sock(x, y, zb, L): return fuse(cyl(x, y, 5.5, zb, zb + 3.0), cyl(x, y, 3.0, zb - L, zb + 0.01))
screws = [sock(x, y, CB_Z, 8.0) for x, y in SCR_OUT + SCR_IN]
inserts = [cut(cyl(x, y, 4.2, RIM_TOP - 4.0, RIM_TOP), cyl(x, y, 3.0, 0, 40)) for x, y in SCR_OUT + SCR_IN]
ties = []
for y in TIE_Y:                                  # 扎带回路 (1.2 厚) 示意
    y0, y1 = y - 2.4, y + 2.4
    ties += [gbox(-HX, y0, MZ1, HX, y1, MZ1 + 1.2), gbox(-OX + TIE_T - 1.2, y0, RIM_TOP + TIE_T - 1.2, -OX + TIE_T, y1, MZ1 + 1.2),
             gbox(OX - TIE_T, y0, RIM_TOP + TIE_T - 1.2, OX - TIE_T + 1.2, y1, MZ1 + 1.2),
             gbox(-OX + TIE_T - 1.2, y0, RIM_TOP + TIE_T - 1.2, OX - TIE_T + 1.2, y1, RIM_TOP + TIE_T)]
tie_s = fuse(*ties) if len(ties) > 1 else ties[0]
# 注: 扎带竖段在侧墙外槽 (x ±25.0..26.5) 里, 底段在底面槽里 (Z33.5 以下 ⇒ 底面槽 Z32–33.5, 带 Z32.3–33.5)

# ---------------- 周边禁区 (按 11-16 晚接口规格 spec_wall82; 转子罩/T 脚按规格尺寸做包络) ----------------
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
KEEP = {
    # 灯板组 (局部中面 y=0) 整体平移 ECC: 板 A F 面 −2.06 / MIP 顶 0; 板 B F 面 −6.66 / LED 面 −8.128 / MIP 顶 −8.72
    'led_a(+y)': gbox(-81.88, ECC + 2.3, 37, 81.88, ECC + 4.36, 245), 'led_b(−y, 含 MIP 凸到 −8.72)': gbox(-81.88, ECC - 4.36, 37, 81.88, ECC - 2.3, 245),
    '夹条 |y−ECC|≤2.3': gbox(-81.88, ECC - 2.3, 37, 81.88, ECC + 2.3, 54),
    'bridge_b': gbox(-32, ECC - 8.4, 37, 32, ECC - 3.77, 73), 'fpc_seat_b': gbox(-20.75, ECC - 10.4, 39, 20.75, ECC - 8.4, 43.4),
    'J3 VH+插头+线 (x±6 假设)': gbox(-58.75 - 6, ECC - 26, 38, -58.75 + 6, ECC - 3.77, 48),
    # 两端立板 (11-16 晚 耳朵脚): 横杆 x69–77 局部 |y|≤14 Z32–37 + 耳朵 x69–77 |y|≤33.73 Z32–36 + 腹板/天线板到 x83.7 (包络)
    '两端立板+耳朵 +x': gbox(69, -33.73, 32, 83.7, 33.73, 37), '两端立板+耳朵 −x': gbox(-83.7, -33.73, 32, -69, 33.73, 37),
    '24V 线走廊 x≈−55 (±3, y≥−50)': gbox(-58, -50, 32, -52, 14, 37),
    'FPC 下缝 |x|≤18': gbox(-18, ECC - 10.4, 32, 18, ECC + 10.4, 37),
    '转子罩壁 r82–85': ann(SHR_R0, SHR_R1, 32, B.Z_VIEW0), '罩内余量 r81.7–82': ann(R_MAX, SHR_R0, 24, B.Z_VIEW0),
    **{f'罩底凸台 @{a:g}° (r72.5–82 × 宽 8 × Z32–36 包络)': xf(gbox(72.5, -4.0, 32.0, 82.0, 4.0, 36.0), B.rotz(a)) for a in B.SHR_ANG},
    **{f'罩底铜螺母孔 @{a:g}° (Φ8 包络)': cyl(x, y, 8, 28, 40) for a, (x, y) in zip(B.SHR_ANG, B.SHR_HOLES)},
    **{f'AC 线孔 ({x:g},{y:g}) Φ3 上方 Z32–35 (托盘不许盖)': cyl(x, y, 3.0, RIM_TOP, MZ0) for x, y in AC_HOLES},
    '底板 r4c 外包 x−51.2…47.3 y8.6–66.6': gbox(-51.2, 8.6, B.Z_BB0, 47.3, 66.6, B.Z_BB0 + B.BB_T),
    'rim': B.rim, 'hub': B.hub, 'shroud_lo': B.shroud_lo, 'shroud_hi': B.shroud_hi, 'glass': B.tube,
}
PARTS = dict(holder=H, module=module, screws=fuse(*screws), inserts=fuse(*inserts), ties=tie_s, **{f'pin {k}': v for k, v in pins.items()})

def report():
    rep = dict(interf={}, interf_nonzero={}, misc={})
    for a, sa in PARTS.items():
        for b, sb in KEEP.items():
            if a == 'inserts' and b == 'rim': continue          # 铜螺母本来就在承载盘孔里 (孔 Φ4.2 = 螺母外径, 应 0, 单列)
            if a == 'pin AC1' and b.startswith('AC 线孔 (21,-70)'): continue   # AC1 脚就在孔正上方 (线直上焊脚, 本意)
            v = round(common_v(sa, sb), 4); rep['interf'][f'{a} × {b}'] = v
            if abs(v) > 1e-4: rep['interf_nonzero'][f'{a} × {b}'] = v
    rep['misc']['inserts × rim'] = round(common_v(PARTS['inserts'], B.rim), 4)
    for a in ('module', 'screws', 'ties', *[f'pin {k}' for k in pins]):
        v = round(common_v(H, PARTS[a]), 4); rep['interf'][f'holder × {a}'] = v
        if abs(v) > 1e-4: rep['interf_nonzero'][f'holder × {a}'] = v
    rep['misc']['n_checks'] = len(rep['interf']) + 1
    rep['misc']['module_max_r'] = round(max(math.hypot(x, y) for x in (-HX, HX) for y in (MOD_Y0, MOD_Y1)), 2)
    hb = bbox(H); rep['misc']['holder_bbox'] = [round(v, 2) for v in hb]
    rep['misc']['holder_max_r'] = round(max_r(H), 3)
    rep['misc']['max_r_all'] = {k: round(max_r(v), 3) for k, v in PARTS.items()}
    rep['misc']['max_r_ok'] = max(rep['misc']['max_r_all'].values()) <= R_MAX + 1e-6
    rep['gap'] = {}
    asm = fuse(H, module, PARTS['screws'], tie_s)
    for b in ('led_b(−y, 含 MIP 凸到 −8.72)', '夹条 |y−ECC|≤2.3', '两端立板+耳朵 +x', '两端立板+耳朵 −x', 'fpc_seat_b', 'FPC 下缝 |x|≤18',
              '24V 线走廊 x≈−55 (±3, y≥−50)', '转子罩壁 r82–85', 'J3 VH+插头+线 (x±6 假设)', 'bridge_b',
              *[k for k in KEEP if k.startswith('罩底') or k.startswith('AC 线孔')]):
        d = BRepExtrema_DistShapeShape(H if b.startswith('AC 线孔') else asm, KEEP[b]); d.Perform()
        rep['gap'][('holder × ' if b.startswith('AC 线孔') else '整件 × ') + b] = round(d.Value(), 2)
    rep['misc']['ac_holes'] = {f'{x},{y}': round(math.hypot(x, y), 2) for x, y in AC_HOLES}
    rep['misc']['rim_new_holes_solid'] = {k: v for k, v in B.LOG['rim_new_holes_solid'].items() if k.startswith('mod')}
    rep['misc']['ac_hole_in_window'] = {f'{x},{y}': any(w[0] <= x - 1.5 and x + 1.5 <= w[1] and w[2] <= y - 1.5 and y + 1.5 <= w[3] for w in WIN.values()) for x, y in AC_HOLES}
    rep['pins'] = PINS
    # 质量 / 平衡 (打印件按 PETG 1.27 g/cm³ 实心; 模块 19.2 g 按几何中心)
    RHO = 1.27e-3
    mh, ch = cog(H); gh = mh * RHO
    mod_c = (0.0, MOD_YC, (MZ0 + MZ1) / 2)
    M3_G, INS_G = 0.8, 0.5
    items = [('holder', gh, ch), ('module', MOD_G, mod_c)] + [('M3×8+铜螺母', M3_G + INS_G, (x, y, 30)) for x, y in SCR_OUT + SCR_IN]
    tot = sum(g for _, g, _ in items)
    c = [sum(g * p[i] for _, g, p in items) / tot for i in range(3)]
    rep['balance'] = dict(holder_g=round(gh, 2), holder_cog=[round(v, 2) for v in ch], module_cog=mod_c,
                          total_g=round(tot, 2), total_cog=[round(v, 2) for v in c],
                          U_gmm=[round(tot * c[0], 1), round(tot * c[1], 1)],
                          F_centrifugal_N_1200rpm=round(tot * 1e-3 * math.hypot(c[0], c[1]) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1),
                          F_module_N=round(MOD_G * 1e-3 * abs(MOD_YC) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1))
    rep['valid'] = BRepCheck_Analyzer(H).IsValid()
    rep['volume_mm3'] = round(mh, 1)
    return rep

if __name__ == '__main__':
    items = [(NAME, H, '#F1C232', None, False), ('无线供电模块 30.5×49×15 (占位)', module, '#3D85C6', None, False)]
    PCOL = {'AC1': '#E69138', 'AC2': '#E69138', '24V': '#CC0000', 'GND': '#222222'}
    items += [(f'模块脚 {k}', v, PCOL[k], None, False) for k, v in pins.items()]
    items += [('M3×8 内六角', s, '#888888', None, False) for s in screws] + [('M3×4 铜螺母 (承载盘)', s, '#B8860B', None, False) for s in inserts]
    items += [('扎带 4.8×1.2 (示意)', tie_s, '#EEEEEE', None, False)]
    write_doc(items, OUT / f'{NAME}.step', NAME)
    BRepMesh_IncrementalMesh(H, 0.02, False, 0.2, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(H, str(OUT / f'{NAME}.stl'))
    bb = bbox(H); t = xf(H, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))       # 打印姿态 = 装配姿态, 底落床
    BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAME}.stl'))
    rep = report()
    json.dump(rep, open(OUT / 'wireless_holder_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rep.items() if k != 'interf'}, indent=1, ensure_ascii=False))
