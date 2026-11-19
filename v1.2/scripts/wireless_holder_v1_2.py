"""V1.2 无线供电接收模块固定件 —— 11-19 用户改: 两件对称夹块 (草图: 绿 = 模块 PCB, 黑 = 两夹块, 红 = 四角焊脚)。
    cd v1.2/scripts && ../../.venv/bin/python wireless_holder_v1_2.py
用户 11-19 原话: 「我们两个对称的件锁住就行 1.这个板子四个脚需要焊接线，朝上，因此红色框需要留直径3mm出口 2.pcb距离底面4mm 3，螺丝打通孔就行」
世界坐标同 build_v1_2: 转子盘B 承载盘顶 Z_RIM_TOP = 30.5。模块 30.5×49 (长边沿 x), 转子盘 −y 侧。
  · 模块 PCB (厚按 1.6 假设) 底面离承载盘顶 4 ⇒ PCB Z34.5–36.1; 元件 (总高 15) 假设只在 PCB 中段 |x|≤19, 两短边端部 5 宽带空 (夹块压这条带)。
  · 夹块 a (+x) / b (−x) 关于 x=0 镜像 (打印时切片里镜像一件即可): 实心块 x 19.5–30.5, 底 Z30.5, 顶 Z39.3;
    PCB 夹槽 Z34.5–36.3 (PCB + 0.2), 从 x=19.5 往外深到 PCB 端 +0.3, ±y 两端封口 (墙 1.5, 挡离心力); 槽上盖 3 厚。
  · 焊脚出口: 四脚正上方 Φ3 竖通孔 (整块打通, 脚朝上焊线, 线从盖顶出; 先焊线再穿孔装夹块)。
    一个出口位置同时罩住镜像两侧的脚 (+x AC1/AC2, −x GND/24V 坐标差 ≤0.5)。
  · AC 引线 (只 +x 夹块用; −x 那条通道空着): 承载盘 Φ3 孔 B.AC_HOLES (x27.5) 直上进夹块 Φ3 竖通道 → 盖顶面横槽 2.2×1.2 → 弯进焊点出口。
  · 螺丝: 每件 2×M3×8 内六角, 打在夹块伸出 PCB ±y 两端的矮耳上 (耳顶 Z35.5, Φ3.4 直通孔, 无沉孔), 进承载盘顶 M3×3 铜螺母 (Z27.5–30.5) 啮合 3。
    外侧 (−y) 耳被 r81.7 圆弧裁 (转子罩内壁 r82)。
  · 模块整体比 11-16 托盘版往 +y 挪 2.5 (y −69.5…−39), 让外侧螺丝在 r81.7 内。
输出: models/wireless_holder_v1_2/wireless_holder_v1_2.{step,stl} (装配坐标, 两件 + 模块占位/螺丝/铜螺母/脚)
      out/打印STL/wireless_holder_v1_2_a.stl / _b.stl (打印姿态 = 装配姿态, 底落床); wireless_holder_report.json
"""
import io, contextlib, json, math
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
from helpers import write_doc
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax2, gp_Pnt, gp_Dir
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
def mirx():
    t = gp_Trsf(); t.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))); return t
def max_r(s):                               # 最大半径: 网格顶点
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
RIM_TOP = B.Z_RIM_TOP                       # 30.5 (转子盘B)
MOD_L, MOD_W, MOD_H, MOD_G = 49.0, 30.5, 15.0, 19.2
HX = MOD_L / 2                              # 24.5
MOD_Y0 = -69.5                              # 11-19: 外 (−y) 长边 (原 −72, 往 +y 挪 2.5 让外侧螺丝进 r81.7)
MOD_Y1 = MOD_Y0 + MOD_W                     # −39.0
MOD_YC = (MOD_Y0 + MOD_Y1) / 2              # −54.25
PCB_T = 1.6                                 # 假设 (待实物)
PCB_GAP = 4.0                               # 用户: PCB 离底面 4
MZ0 = RIM_TOP + PCB_GAP                     # 34.5 PCB 底
PCB_Z1 = MZ0 + PCB_T                        # 36.1
MZ1 = MZ0 + MOD_H                           # 49.5 模块顶 (元件包络)
COMP_X = HX - 5.5                           # 元件假设只在 |x|≤19 (两端 5.5 宽带给夹块)
SLOT_CLR_Z, SLOT_CLR_X, SLOT_CLR_Y = 0.2, 0.3, 0.3
SLOT_Z0, SLOT_Z1 = MZ0, PCB_Z1 + SLOT_CLR_Z  # 34.5–36.3
CAP_T = 3.0
TOP_Z = SLOT_Z1 + CAP_T                     # 39.3
XI, XO = 19.5, 30.5                         # 夹块 x 范围 (+x 件), 压 PCB 端 5 宽
WALL_Y = 1.5                                # 槽 ±y 封口墙
BY0, BY1 = MOD_Y0 - SLOT_CLR_Y - WALL_Y, MOD_Y1 + SLOT_CLR_Y + WALL_Y   # 块体 y −71.3…−37.2
EAR_Z1 = RIM_TOP + 5.0                      # 35.5 矮耳顶 = 螺丝头支承 (M3×8 ⇒ 尾 Z27.5, 铜螺母 Z27.5–30.5 啮合 3)
CB_Z = EAR_Z1                               # (旧名, fasteners/图纸读)
SCR_L = 8.0
SCR_X = 23.0
SCR_DY = 3.2                                # 螺丝心离块体端面 (头 Φ5.5 离块体 0.45)
SCR_OUT = [(SCR_X, BY0 - SCR_DY), (-SCR_X, BY0 - SCR_DY)]   # (±23, −74.5)
SCR_IN = [(SCR_X, BY1 + SCR_DY), (-SCR_X, BY1 + SCR_DY)]    # (±23, −34.0)
EAR_R = 3.3                                 # 耳端离螺丝心
R_MAX = 81.7                                # 罩内一切 ≤ r81.7
SHR_R0, SHR_R1 = 82.0, 85.0
OUT_R = R_MAX
ECC = B.SCR_ECC
assert sorted(SCR_OUT + SCR_IN) == sorted((round(x, 3), round(y, 3)) for x, y in B.MOD_HOLES), (SCR_OUT + SCR_IN, B.MOD_HOLES)
# 引脚 (封装本地 fx 向右, fy 向下, 框 48.6×30; 绕 Z 转 180° 使 AC 在 +x): X = −(fx − 24.3), Y = MOD_YC + (fy − 15)  (待实物核)
FP = {'AC1': (2.8, 2.5), 'AC2': (2.0, 27.75), '24V': (45.91, 28.0), 'GND': (46.28, 3.22)}
PINS = {k: (round(-(fx - 24.3), 2), round(MOD_YC + (fy - 15.0), 2)) for k, (fx, fy) in FP.items()}
EXIT_D = 3.0
EXIT_X = 21.85                              # 镜像两侧共用
EXIT_Y = [MOD_Y0 + 3.1, MOD_Y0 + 28.1]      # −66.4 / −41.4
for k, (px, py) in PINS.items():            # 每个脚 (Φ1) 都要在某个 Φ3 出口里, 偏心 ≤ 1
    assert min(math.hypot(abs(px) - EXIT_X, py - ey) for ey in EXIT_Y) <= 1.0 - 1e-9, (k, px, py)
CH_X = 27.5                                 # AC 竖通道 (x 27.5, 墙: 到槽端 1.2 / 到外面 1.5)
AC_HOLES = [(CH_X, y) for y in EXIT_Y]
assert sorted(AC_HOLES) == sorted(B.AC_HOLES), (AC_HOLES, B.AC_HOLES)
GROOVE_W, GROOVE_D = 2.2, 1.2               # 盖顶横槽: 通道 → 焊点出口

# ---------------- 夹块 ----------------
def clamp_a():
    s = gbox(XI, BY0, RIM_TOP, XO, BY1, TOP_Z)                                                    # 块体
    for ys in (SCR_OUT[0][1], SCR_IN[0][1]):                                                       # 两端矮耳
        y0, y1 = (ys - EAR_R, BY0 + 0.01) if ys < BY0 else (BY1 - 0.01, ys + EAR_R)
        s = fuse(s, gbox(XI, y0, RIM_TOP, XO, y1, EAR_Z1))
    s = B.op(BRepAlgoAPI_Common, s, cyl(0, 0, 2 * R_MAX, RIM_TOP - 1, TOP_Z + 1))                 # r81.7 裁
    s = cut(s, gbox(XI - 1, MOD_Y0 - SLOT_CLR_Y, SLOT_Z0, HX + SLOT_CLR_X, MOD_Y1 + SLOT_CLR_Y, SLOT_Z1))   # PCB 夹槽
    for x, y in (SCR_OUT[0], SCR_IN[0]):
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, EAR_Z1 + 1))                                        # M3 通孔
    for y in EXIT_Y:
        s = cut(s, cyl(EXIT_X, y, EXIT_D, RIM_TOP - 1, TOP_Z + 1),                                 # 焊脚出口
                cyl(CH_X, y, EXIT_D, RIM_TOP - 1, TOP_Z + 1),                                      # AC 竖通道
                gbox(EXIT_X, y - GROOVE_W / 2, TOP_Z - GROOVE_D, CH_X, y + GROOVE_W / 2, TOP_Z + 1))   # 盖顶横槽
    return clean(s)

HA = clamp_a()
HB = clean(xf(HA, mirx()))
H = fuse(HA, HB)
pcb = gbox(-HX, MOD_Y0, MZ0, HX, MOD_Y1, PCB_Z1)
module = fuse(pcb, gbox(-COMP_X, MOD_Y0, PCB_Z1 - 0.01, COMP_X, MOD_Y1, MZ1))    # 占位: PCB + 中段元件包络
pins = {k: cyl(x, y, 1.0, PCB_Z1, PCB_Z1 + 2.0) for k, (x, y) in PINS.items()}   # 示意: 脚朝上伸出 2
def sock(x, y, zb, L): return fuse(cyl(x, y, 5.5, zb, zb + 3.0), cyl(x, y, 3.0, zb - L, zb + 0.01))
screws = [sock(x, y, CB_Z, SCR_L) for x, y in SCR_OUT + SCR_IN]
inserts = [cut(cyl(x, y, 4.2, RIM_TOP - 3.0, RIM_TOP), cyl(x, y, 3.0, 0, 40)) for x, y in SCR_OUT + SCR_IN]

# ---------------- 周边禁区 ----------------
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
def sector(r0, r1, z0, z1, a0, a1): return cut(cyl(0, 0, 2 * r1, z0, z1, ang=a1 - a0, a0=a0), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
KEEP = {
    'led_a(+y)': gbox(-81.88, ECC + 2.5, 37, 81.88, ECC + 4.69, 245), 'led_b(−y, 含 MIP)': gbox(-81.88, ECC - 4.69, 37, 81.88, ECC - 2.5, 245),
    '夹条 |y−ECC|≤2.5': gbox(-81.88, ECC - 2.5, 37, 81.88, ECC + 2.5, 54),
    'bridge_b (矩形 76 宽)': gbox(-38, ECC - 8.4, 37, 38, ECC - 3.77, 74), 'fpc_seat_b': gbox(-20.75, ECC - 10.4, 37, 20.75, ECC - 8.4, 44),
    'FPC 下缝 |x|≤18': gbox(-18, ECC - 12, RIM_TOP, 18, ECC + 12, 37.5),
    '24V 线走廊 x≈−55 (±3, y≥−50)': gbox(-58, -50, RIM_TOP, -52, 14, 37.5),
    **{f'屏幕固定件弧形带 {"+x" if c == 0 else "−x"} (r73–81.7 ±44°)': sector(73.0, 81.7, RIM_TOP, 37.5, c - 44, c + 44) for c in (0.0, 180.0)},
    '转子罩壁 r82–85': ann(SHR_R0, SHR_R1, RIM_TOP, B.Z_VIEW0), '罩内余量 r81.7–82': ann(R_MAX, SHR_R0, RIM_TOP, B.Z_VIEW0),
    '底板 r4j 外包 x±51.2 y8.6–60.5': gbox(-51.2, 8.6, B.Z_BB0, 51.2, 60.5, B.Z_BB0 + B.BB_T),
    'glass': B.tube,
}
PARTS = dict(clamp_a=HA, clamp_b=HB, module=module, screws=fuse(*screws), inserts=fuse(*inserts), **{f'pin {k}': v for k, v in pins.items()})

def report():
    rep = dict(interf={}, interf_nonzero={}, misc={})
    for a, sa in PARTS.items():
        for b, sb in KEEP.items():
            v = round(common_v(sa, sb), 4); rep['interf'][f'{a} × {b}'] = v
            if abs(v) > 1e-4: rep['interf_nonzero'][f'{a} × {b}'] = v
    for c in ('clamp_a', 'clamp_b'):
        for a in ('module', 'screws', *[f'pin {k}' for k in pins]):
            v = round(common_v(PARTS[c], PARTS[a]), 4); rep['interf'][f'{c} × {a}'] = v
            if abs(v) > 1e-4: rep['interf_nonzero'][f'{c} × {a}'] = v
    rep['misc']['n_checks'] = len(rep['interf'])
    rep['misc']['clamp_a_bbox'] = [round(v, 2) for v in bbox(HA)]
    rep['misc']['max_r_all'] = {k: round(max_r(v), 3) for k, v in PARTS.items()}
    rep['misc']['max_r_ok'] = max(rep['misc']['max_r_all'].values()) <= R_MAX + 1e-3
    rep['misc']['screws'] = {f'{x:g},{y:g}': round(math.hypot(x, y), 2) for x, y in SCR_OUT + SCR_IN}
    rep['misc']['ac_holes'] = {f'{x:g},{y:g}': round(math.hypot(x, y), 2) for x, y in AC_HOLES}
    rep['misc']['pin_exit_offset'] = {k: round(min(math.hypot(abs(px) - EXIT_X, py - ey) for ey in EXIT_Y), 2) for k, (px, py) in PINS.items()}
    # 最薄: 槽端 → AC 通道 / 通道 → 外面 / 螺丝孔 → r81.7
    rep['misc']['walls'] = {'槽端→AC通道': round(CH_X - EXIT_D / 2 - (HX + SLOT_CLR_X), 2), 'AC通道→外面': round(XO - CH_X - EXIT_D / 2, 2),
                            '外螺丝孔→r81.7': round(R_MAX - math.hypot(*SCR_OUT[0]) - 1.7, 2), '槽 ±y 封口墙': WALL_Y, '盖厚': CAP_T,
                            '螺丝头→块体端面': round(SCR_DY - 2.75, 2)}
    rep['gap'] = {}
    asm = fuse(H, module, PARTS['screws'])
    for b in KEEP:
        if b == 'glass': continue
        d = BRepExtrema_DistShapeShape(asm, KEEP[b]); d.Perform(); rep['gap'][f'整件 × {b}'] = round(d.Value(), 2)
    rep['pins'] = PINS
    RHO = 1.27e-3                           # PETG 实心
    ma, ca = cog(HA); mb, cb = cog(HB)
    mod_c = (0.0, MOD_YC, (MZ0 + MZ1) / 2)
    M3_G, INS_G = 0.7, 0.4
    items = [('clamp_a', ma * RHO, ca), ('clamp_b', mb * RHO, cb), ('module', MOD_G, mod_c)] + [('M3×8+铜螺母', M3_G + INS_G, (x, y, 30)) for x, y in SCR_OUT + SCR_IN]
    tot = sum(g for _, g, _ in items)
    c = [sum(g * p[i] for _, g, p in items) / tot for i in range(3)]
    rep['balance'] = dict(holder_g=round((ma + mb) * RHO, 2), clamp_each_g=round(ma * RHO, 2), holder_cog=[round(v, 2) for v in ca],
                          module_cog=mod_c, total_g=round(tot, 2), total_cog=[round(v, 2) for v in c],
                          U_gmm=[round(tot * c[0], 1), round(tot * c[1], 1)],
                          F_centrifugal_N_1200rpm=round(tot * 1e-3 * math.hypot(c[0], c[1]) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1),
                          F_module_N=round(MOD_G * 1e-3 * abs(MOD_YC) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1))
    rep['valid'] = BRepCheck_Analyzer(HA).IsValid() and BRepCheck_Analyzer(HB).IsValid()
    rep['volume_mm3_each'] = round(ma, 1)
    return rep

if __name__ == '__main__':
    items = [('wireless_holder_v1_2_a (+x 夹块)', HA, '#F1C232', None, False), ('wireless_holder_v1_2_b (−x 夹块, 镜像)', HB, '#F1C232', None, False),
             ('无线供电模块 PCB 49×30.5×1.6 + 元件包络 (占位)', module, '#3D85C6', None, False)]
    PCOL = {'AC1': '#E69138', 'AC2': '#E69138', '24V': '#CC0000', 'GND': '#222222'}
    items += [(f'模块脚 {k}', v, PCOL[k], None, False) for k, v in pins.items()]
    items += [('M3×8 内六角', s, '#888888', None, False) for s in screws] + [('M3×3 铜螺母 (承载盘)', s, '#B8860B', None, False) for s in inserts]
    write_doc(items, OUT / f'{NAME}.step', NAME)
    BRepMesh_IncrementalMesh(H, 0.02, False, 0.2, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(H, str(OUT / f'{NAME}.stl'))
    for tag, sh in (('a', HA), ('b', HB)):
        bb = bbox(sh); t = xf(sh, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))       # 打印姿态 = 装配姿态, 底落床
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAME}_{tag}.stl'))
    rep = report()
    json.dump(rep, open(OUT / 'wireless_holder_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rep.items() if k != 'interf'}, indent=1, ensure_ascii=False))
