"""V1.2 无线供电接收模块固定件 —— 11-19 用户改: 两件对称夹块 (草图: 绿 = 模块 PCB, 黑 = 两夹块, 红 = 四角焊脚)。
    cd v1.2/scripts && ../../.venv/bin/python wireless_holder_v1_2.py
用户 11-19 原话: 「我们两个对称的件锁住就行 1.这个板子四个脚需要焊接线，朝上，因此红色框需要留直径3mm出口 2.pcb距离底面4mm 3，螺丝打通孔就行」
世界坐标同 build_v1_2: 转子盘B 承载盘顶 Z_RIM_TOP = 30.5。模块 30.5×49 (长边沿 x), 转子盘 −y 侧。
  · 模块 PCB (厚按 1.6 假设) 底面离承载盘顶 4 ⇒ PCB Z34.5–36.1; 元件 (总高 15) 假设只在 PCB 中段 |x|≤19, 两短边端部 5 宽带空 (夹块压这条带)。
  · 夹块 a (+x) / b (−x) 关于 x=0 镜像 (打印时切片里镜像一件即可): 实心块 x 19.5–30.5, 底 Z30.5, 顶 Z39.3;
    PCB 夹槽 Z34.5–36.3 (PCB + 0.2), 从 x=19.5 往外深到 PCB 端 +0.3, ±y 两端封口 (墙 1.5, 挡离心力); 槽上盖 3 厚。
  · 11-19 14:22 用户改: 「1.这个件往中央挪一点 2.如图，螺丝放在左右，不放在上下 3.电路板出线位置，四角5*5mm的位置，这里要上部留空」
  · 焊脚开窗 (15:40 用户): 只在 2 厚压盖上开 3.5 (压边全宽) × 5 (以焊脚为心) 窗, 主体台阶不挖, 直接从上面焊线;
    盖只剩两排焊脚之间一段压 PCB。一个位置同时罩住镜像两侧的脚 (+x AC1/AC2, −x GND/24V 坐标差 ≤0.5); 脚下 Φ3 让位孔。
  · AC 引线 (11-19 15:00 改): 承载盘 Φ3.5 孔 B.AC_HOLES 在线圈腔正上方 (托盘最薄处), 内孔 (38.54, −15.79) 孔边切腔内缘 / 外孔 (43.29, -55.96) 孔边切腔外缘, 都在 AC 侧夹块外侧; 线从腔里竖上来, 跨 +x 夹块顶进敞开区焊 AC 脚; 夹块实心无通道。
  · 11-19 14:33 简化: 每件就是一根沿 y 的直方条 x21–32 (15:32 收窄, 宽 11) × y(PCB±) × Z30.5–36.5 (15:45 总高 6), 无台阶/耳朵/圆弧裁。
  · 螺丝 (11-19 用户: 从下往上, 同底板; 15:30「螺丝应该是通孔，上边锁螺母」): 每件 2×M3×14 超薄头, 从承载盘底 Φ7.4×1.5 让位 (支承 Z28.8) 穿承载盘 + 方条 Φ3.4 通孔 (x28.3, y 对齐两排焊脚), 方条顶面拧 M3 尼龙防松螺母; 线圈/玻纤板装之前装。
  · 模块位置: y −51.5…−21 (离灯板组实测最近 桥板 B 5.02; 11-19 上午 −69.5…−39, 11-16 托盘版 −72…−41.5)。
  · 11-19 14:29 用户「这个件压住电路板宽度做到3.5mm就行了」: 夹块 x 21–30.5 (槽深 3.5 + 0.3)。
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
MOD_L, MOD_W, MOD_H, MOD_G = 48.5, 30.0, 15.0, 19.2   # 11-19 15:46 用户「pcb宽度是30mm」+ 组件尺寸 48.5+8×2 (原 49×30.5)
HX = MOD_L / 2                              # 24.25
MOD_Y0 = -66.5                              # 11-19 19:40 用户「无线电路挡住中央8个螺丝的其中两个了往边上挪一下」: 往 −y 挪 15.0 (PCB 让开内圈 247.5/292.5° 法兰 Φ8 留 1.1; 再挪 1 夹块就碰外圈 247.5/292.5° 铜螺母, 现留 0.9; 离 −y 半罩 6.2); 之前 −51.5: 用户「往中央挪」+ 补充: 挪到离灯板组正好 5 (实测最近 桥板 B 5.02, 次近 FPC B, 挪动量取整 0.5) ⇒ 比上午 −69.5 往 +y 挪 18.0 (11-16 托盘版 −72); 实测见 scratchpad wl_dist.py
MOD_Y1 = MOD_Y0 + MOD_W                     # −21.5
MOD_YC = (MOD_Y0 + MOD_Y1) / 2              # −36.5
PCB_T = 1.6                                 # 假设 (待实物)
PCB_TOP_GAP = 4.0                           # 11-19 15:45 用户「pcb上边高度就是4mm，件总高是6mm」: PCB 顶面离盘顶 4
MZ0 = RIM_TOP + PCB_TOP_GAP - PCB_T         # 32.9 PCB 底 (离盘顶 2.4)
PCB_GAP = MZ0 - RIM_TOP                     # 2.4
PCB_Z1 = MZ0 + PCB_T                        # 34.5 PCB 顶
MZ1 = MZ0 + MOD_H                           # 47.9 模块顶 (元件包络, 假设在 PCB 上方)
# 11-19 15:46 用户最终形状 (侧视倒 L + 俯视): 「侧面看，上边有个沿挡住pcb上边，然后右边是为了把这个件锁到转子盘，因此绿色宽度是3.5 蓝色是法兰螺母是8mm。
#   当然这个件除了上边，也要挡住pcb水平移动，因此俯视如图2，pcb宽度是30mm，两边各加2mm挡住」
#   截面 (a 件, +x): 外侧立柱 x 宽 8 (Z30.5–36.5, 顶面放 M3 法兰螺母) + 内侧上沿 x 宽 3.5 (Z34.5–36.5, 压 PCB 顶), 上沿下面空 (不托 PCB);
#   PCB 端面顶立柱内侧面留 0.2; y 两端在上沿 3.5 宽处各加 2 厚挡块 (盘面通到上沿, 挡 PCB 沿 y, −y 端扛离心)。
END_CLR, X_CLR = 0.1, 0.0                   # 15:50 用户「不留间隙」; 19:26 用户: y 两挡块之间净距 +0.2 (30→30.2, 每边 0.1), 组件 34→34.2
GRIP = 3.5                                  # 上沿宽 (用户「压住电路板宽度做到3.5mm」)
COL_W = 8.0                                 # 立柱宽 (法兰螺母)
XC0 = HX + X_CLR                            # 24.25 立柱内侧面 = PCB 端面
XI, XO = XC0 - GRIP, XC0 + COL_W            # 20.75–32.25 (单件宽 11.5, 两件外面之间 64.5 = 48.5 + 2×8); 上沿压 PCB 3.5
XF = XO
COMP_X = XI                                 # 元件包络假设 |x|≤21.2
CAP_T = 2.0
LIP_Z0 = PCB_Z1                             # 34.5 上沿底 = PCB 顶
TOP_Z = LIP_Z0 + CAP_T                      # 36.5 总高 6
SLOT_Z0, SLOT_Z1 = MZ0, PCB_Z1              # (旧名) PCB 所在高度
SLOT_CLR_X, SLOT_CLR_Y, SLOT_CLR_Z = X_CLR, END_CLR, 0.0
END_T = 2.0                                 # y 两端挡块厚 (用户「两边各加2mm」, 组件宽 34)
WALL_OUT = WALL_IN = WALL_Y = END_T
BY0, BY1 = MOD_Y0 - END_CLR - END_T, MOD_Y1 + END_CLR + END_T   # y −53.6…−19.4 (长 34.2)
# 螺丝 (11-19 用户「螺丝是从下往上锁」「和 soc 底板一样」「螺丝应该是通孔，上边锁螺母」「蓝色是法兰螺母」):
#   承载盘底面 Φ7.4×1.5 让位 (头支承 Z28.8) + Φ3.4 通 → 立柱 Φ3.4 通孔 → 顶面 M3 法兰螺母 (带齿防松, 法兰 Φ7.6 × 高 3.7)。
#   M3×14 超薄头: 支承 Z28.8 → 立柱顶 36.5 (7.7) + 法兰螺母 3.7 + 露出 2.6 → 尾 Z42.8。头在线圈腔上方 ⇒ 装线圈/玻纤板之前装。
NUT_FL_D, NUT_H = 8.0, 3.7                  # 15:52 用户: 法兰螺母 Φ8 (立柱 8 宽正好)
NUT_AF = 5.9
BB_CB_D, BB_CB_H = 7.4, 1.5                 # = rotor_b 底板孔
SCR_X = XC0 + COL_W / 2                     # 28.25 立柱中心
assert COL_W - NUT_FL_D >= -1e-9
SCR_PITCH = 18.0                            # 15:52 用户「每件两颗螺丝间距 18」: y = 组件中心 ±9 (法兰之间净空 10, 离块两端各 4)
CB_Z = 27.3 + BB_CB_H                       # 28.8
SCR_L = 14.0
EAR_Z1 = TOP_Z
R_MAX = 81.7
SHR_R0, SHR_R1 = 82.0, 85.0
OUT_R = R_MAX
ECC = B.SCR_ECC
# 引脚 (封装本地 fx 向右, fy 向下, 框 48.6×30; 绕 Z 转 180° 使 AC 在 +x): X = −(fx − 24.3), Y = MOD_YC + (fy − 15)  (待实物核)
FP = {'AC1': (2.8, 2.5), 'AC2': (2.0, 27.75), '24V': (45.91, 28.0), 'GND': (46.28, 3.22)}
PINS = {k: (round(-(fx - 24.3), 2), round(MOD_YC + (fy - 15.0), 2)) for k, (fx, fy) in FP.items()}
EXIT_D = 3.0
EXIT_X = 21.85
EXIT_Y = [round(MOD_Y0 + 2.86, 2), round(MOD_Y0 + 27.9, 2)]   # −48.64 / −23.6 (两排焊脚)
SCR_OUT = [(SCR_X, MOD_YC - SCR_PITCH / 2), (-SCR_X, MOD_YC - SCR_PITCH / 2)]   # (±28.25, −45.5)
SCR_IN = [(SCR_X, MOD_YC + SCR_PITCH / 2), (-SCR_X, MOD_YC + SCR_PITCH / 2)]      # (±28.25, −27.5)
assert min(SCR_OUT[0][1] - BY0, BY1 - SCR_IN[0][1]) >= NUT_FL_D / 2 - 1e-9
OPEN = 5.0                                  # 焊脚开窗 3.5 (上沿全宽) × 5 (以脚为心)
OPEN_DY = OPEN / 2
AC_HOLES = list(B.AC_HOLES)                 # 内孔 (38.54, −15.79) r41.65 孔边切腔内缘 / 外孔 (43.29, −55.96) r70.75 孔边切腔外缘, 外孔从下往上看在内孔逆时针 30°
def _box_gap(x, y, x0, y0, x1, y1): return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))
for _x, _y in AC_HOLES:
    _r = math.hypot(_x, _y); assert B.COIL_SEAT_R + B.AC_HOLE_D / 2 - 0.01 <= _r <= 72.5 - B.AC_HOLE_D / 2 + 0.01, ('AC 孔出线圈腔', _r)
    assert _box_gap(_x, _y, XI, BY0, XO, BY1) - B.AC_HOLE_D / 2 >= 1.5 - 1e-9, ('AC 孔离夹块 <1.5', _x, _y)
# 开窗: 上沿 x XI–XC0, y 以焊脚为心 ±2.5; 靠 y 端挡块那侧并到挡块面 (不留 <1 细条)
OPEN_X0, OPEN_X1 = XI - 0.01, XC0 + 0.01
OPEN_LEN = round(max(EXIT_Y[0] + OPEN_DY - MOD_Y0, MOD_Y1 - (EXIT_Y[1] - OPEN_DY)), 2)   # 5.36: 两端开窗等长 ⇒ 夹块关于自身 y 中心对称 (16:00 用户「拆成独立的，就留1个」: b = a 绕 Z 转 180°, 同一零件)
OPEN_BOX = [(OPEN_X0, MOD_Y0 - END_CLR, OPEN_X1, MOD_Y0 + OPEN_LEN), (OPEN_X0, MOD_Y1 - OPEN_LEN, OPEN_X1, MOD_Y1 + END_CLR)]
assert all(b[0] <= abs(px) - 0.5 and abs(px) + 0.5 <= b[2] and b[1] <= py - 0.5 and py + 0.5 <= b[3] for px, py in PINS.values() for b in [min(OPEN_BOX, key=lambda bb: abs((bb[1] + bb[3]) / 2 - py))])   # 每个脚 (Φ1) 都在开窗里
assert sorted((round(x, 3), round(y, 3)) for x, y in SCR_OUT + SCR_IN) == sorted((round(x, 3), round(y, 3)) for x, y in B.MOD_HOLES), (SCR_OUT + SCR_IN, B.MOD_HOLES)

# ---------------- 夹块 (倒 L) ----------------
def clamp_a():
    s = fuse(gbox(XC0, BY0, RIM_TOP, XO, BY1, TOP_Z),                                              # 立柱 8 宽
             gbox(XI, BY0, LIP_Z0, XC0 + 0.01, BY1, TOP_Z),                                          # 上沿 3.5 宽 2 厚
             gbox(XI, BY0, RIM_TOP, XC0 + 0.01, BY0 + END_T, TOP_Z),                                 # −y 端挡块
             gbox(XI, BY1 - END_T, RIM_TOP, XC0 + 0.01, BY1, TOP_Z))                                 # +y 端挡块
    for x, y in (SCR_OUT[0], SCR_IN[0]):
        s = cut(s, cyl(x, y, 3.4, RIM_TOP - 1, TOP_Z + 1))                                          # Φ3.4 通孔
    for x0, y0, x1, y1 in OPEN_BOX:
        s = cut(s, gbox(x0, y0, LIP_Z0 - 0.01, x1, y1, TOP_Z + 1))                                  # 焊脚开窗 (只开上沿)
    return clean(s)

HA = clamp_a()
HB = clean(xf(HA, mirx()))                  # 关于 x=0 镜像; a 自身 y 对称 ⇒ = a 绕 Z 转 180° (同一零件 wireless_clamp_v1_2)
PART = 'wireless_clamp_v1_2'
H = fuse(HA, HB)
pcb = gbox(-HX, MOD_Y0, MZ0, HX, MOD_Y1, PCB_Z1)
module = fuse(pcb, gbox(-COMP_X, MOD_Y0, PCB_Z1 - 0.01, COMP_X, MOD_Y1, MZ1))    # 占位: PCB + 中段元件包络
pins = {k: cyl(x, y, 1.0, PCB_Z1, PCB_Z1 + 2.0) for k, (x, y) in PINS.items()}   # 示意: 脚朝上伸出 2
def thin_up(x, y, zb, L): return fuse(cyl(x, y, 7.0, zb - 1.2, zb), cyl(x, y, 3.0, zb - 0.01, zb + L))   # 超薄头 Φ7×1.2 头在下 (用户: 头厚约 1.2; 沉孔 1.5 缩进 0.3)
screws = [thin_up(x, y, CB_Z, SCR_L) for x, y in SCR_OUT + SCR_IN]
def _hexnut(x, y, z0):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    R = NUT_AF / math.sqrt(3); pg = BRepBuilderAPI_MakePolygon()
    for k in range(6): pg.Add(gp_Pnt(x + R * math.cos(math.radians(60 * k)), y + R * math.sin(math.radians(60 * k)), z0 + 1.0))
    pg.Close(); hexp = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, NUT_H - 1.0)).Shape()
    return cut(fuse(cyl(x, y, NUT_FL_D, z0, z0 + 1.0), hexp), cyl(x, y, 3.0, z0 - 1, z0 + NUT_H + 1))   # 法兰 Φ7.6×1 + 六角
inserts = [_hexnut(x, y, TOP_Z) for x, y in SCR_OUT + SCR_IN]   # (旧名) 立柱顶面 M3 法兰螺母

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
    rep['misc']['ac_holes'] = {f'{x:g},{y:g}': dict(r=round(math.hypot(x, y), 2), 方位角=round(math.degrees(math.atan2(y, x)), 2), 离夹块=round(_box_gap(x, y, XI, BY0, XO, BY1) - B.AC_HOLE_D / 2, 2),
                                                    离腔内缘=round(math.hypot(x, y) - B.AC_HOLE_D / 2 - B.COIL_SEAT_R, 2), 离腔外缘=round(72.5 - math.hypot(x, y) - B.AC_HOLE_D / 2, 2)) for x, y in AC_HOLES}
    rep['misc']['pin_exit_offset'] = {k: round(min(math.hypot(abs(px) - EXIT_X, py - ey) for ey in EXIT_Y), 2) for k, (px, py) in PINS.items()}
    # 最薄: 槽端 → AC 通道 / 通道 → 外面 / 螺丝孔 → r81.7
    rep['misc']['bar_size'] = dict(x=round(XO - XI, 2), y=round(BY1 - BY0, 2), z=round(TOP_Z - RIM_TOP, 2), x_range=[XI, round(XO, 2)], y_range=[round(BY0, 2), round(BY1, 2)])
    rep['misc']['walls'] = {'法兰 Φ7.6→立柱外面': round(XO - SCR_X - NUT_FL_D / 2, 2), '法兰→立柱内面': round(SCR_X - NUT_FL_D / 2 - XC0, 2), '法兰→y 端': round(min(SCR_OUT[0][1] - NUT_FL_D / 2 - BY0, BY1 - SCR_IN[0][1] - NUT_FL_D / 2), 2), '两法兰净空': round(SCR_PITCH - NUT_FL_D, 2),
                            'y 端挡块': END_T, '上沿厚': CAP_T, '上沿宽': GRIP, '立柱宽': COL_W}
    rep['misc']['open_box_a'] = [[round(v, 2) for v in b] for b in OPEN_BOX]
    rep['misc']['section'] = {'立柱 x 宽': COL_W, '上沿 x 宽': GRIP, '上沿实压 PCB': round(HX - XI, 2), '上沿厚': CAP_T, '总高': round(TOP_Z - RIM_TOP, 2), 'PCB 顶离盘顶': PCB_TOP_GAP, 'PCB 底离盘顶': round(PCB_GAP, 2),
                              '上沿下': '空 (不托 PCB)', 'PCB 端→立柱': X_CLR, 'PCB 侧→y 挡块': END_CLR, 'y 挡块厚': END_T, '开窗 x×y (外排/内排)': [round(OPEN_X1 - OPEN_X0, 2), [round(b[3] - b[1], 2) for b in OPEN_BOX]],
                              '单件 x×y×z': [round(XO - XI, 2), round(BY1 - BY0, 2), round(TOP_Z - RIM_TOP, 2)], '整组外包 x×y': [round(2 * XO, 2), round(BY1 - BY0, 2)]}
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
    items = [('clamp_a', ma * RHO, ca), ('clamp_b', mb * RHO, cb), ('module', MOD_G, mod_c)] + [('M3×14超薄头+螺母', M3_G + INS_G, (x, y, 30)) for x, y in SCR_OUT + SCR_IN]
    tot = sum(g for _, g, _ in items)
    c = [sum(g * p[i] for _, g, p in items) / tot for i in range(3)]
    rep['balance'] = dict(holder_g=round((ma + mb) * RHO, 2), clamp_each_g=round(ma * RHO, 2), holder_cog=[round(v, 2) for v in ca],
                          module_cog=mod_c, total_g=round(tot, 2), total_cog=[round(v, 2) for v in c],
                          U_gmm=[round(tot * c[0], 1), round(tot * c[1], 1)],
                          F_centrifugal_N_1200rpm=round(tot * 1e-3 * math.hypot(c[0], c[1]) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1),
                          F_module_N=round(MOD_G * 1e-3 * abs(MOD_YC) * 1e-3 * (1200 * 2 * math.pi / 60) ** 2, 1))
    rep['valid'] = BRepCheck_Analyzer(HA).IsValid() and BRepCheck_Analyzer(HB).IsValid()
    try:                                    # a 绕 (0, MOD_YC) 转 180° 应与 b 重合 ⇒ 同一零件
        from OCP.gp import gp_Ax1, gp_Pnt as _P, gp_Dir as _D
        _t = gp_Trsf(); _t.SetRotation(gp_Ax1(_P(0, MOD_YC, 0), _D(0, 0, 1)), math.pi); _ra = xf(HA, _t)
        rep['misc']['a_rot180_vs_b_xor_mm3'] = round(vol(B.cut(HB, _ra)) + vol(B.cut(_ra, HB)), 3)
    except Exception as e:
        rep['misc']['a_rot180_vs_b_xor_mm3'] = str(e)
    rep['volume_mm3_each'] = round(ma, 1)
    return rep

if __name__ == '__main__':
    items = [('wireless_clamp_v1_2 ×2: +x', HA, '#F1C232', None, False), ('wireless_clamp_v1_2 ×2: −x (转 180°)', HB, '#F1C232', None, False),
             ('无线供电模块 PCB 48.5×30×1.6 + 元件包络 (占位)', module, '#3D85C6', None, False)]
    PCOL = {'AC1': '#E69138', 'AC2': '#E69138', '24V': '#CC0000', 'GND': '#222222'}
    items += [(f'模块脚 {k}', v, PCOL[k], None, False) for k, v in pins.items()]
    items += [('M3×14 超薄头 (承载盘底往上)', s, '#888888', None, False) for s in screws] + [('M3 法兰螺母 (立柱顶)', s, '#B8860B', None, False) for s in inserts]
    write_doc(items, OUT / f'{NAME}.step', NAME)
    BRepMesh_IncrementalMesh(H, 0.02, False, 0.2, True)
    w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(H, str(OUT / f'{NAME}.stl'))
    bb = bbox(HA); t = clean(xf(HA, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2])))      # 单件: 打印姿态 = 装配姿态, 底落床, 原点在件中心
    write_doc([(PART, t, '#F1C232', None, False)], OUT / f'{PART}.step', PART)
    BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
    for d in (OUT, B.OUT / '打印STL'):
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(d / f'{PART}.stl'))
    rep = report()
    json.dump(rep, open(OUT / 'wireless_holder_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rep.items() if k != 'interf'}, indent=1, ensure_ascii=False))
