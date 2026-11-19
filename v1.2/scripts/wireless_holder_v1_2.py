"""V1.2 无线供电接收模块固定件 —— 11-19 用户改: 两件对称夹块 (草图: 绿 = 模块 PCB, 黑 = 两夹块, 红 = 四角焊脚)。
    cd v1.2/scripts && ../../.venv/bin/python wireless_holder_v1_2.py
用户 11-19 原话: 「我们两个对称的件锁住就行 1.这个板子四个脚需要焊接线，朝上，因此红色框需要留直径3mm出口 2.pcb距离底面4mm 3，螺丝打通孔就行」
世界坐标同 build_v1_2: 转子盘B 承载盘顶 Z_RIM_TOP = 30.5。模块 30.5×49 (长边沿 x), 转子盘 −y 侧。
  · 模块 PCB (厚按 1.6 假设) 底面离承载盘顶 4 ⇒ PCB Z34.5–36.1; 元件 (总高 15) 假设只在 PCB 中段 |x|≤19, 两短边端部 5 宽带空 (夹块压这条带)。
  · 夹块 a (+x) / b (−x) 关于 x=0 镜像 (打印时切片里镜像一件即可): 实心块 x 19.5–30.5, 底 Z30.5, 顶 Z39.3;
    PCB 夹槽 Z34.5–36.3 (PCB + 0.2), 从 x=19.5 往外深到 PCB 端 +0.3, ±y 两端封口 (墙 1.5, 挡离心力); 槽上盖 3 厚。
  · 11-19 14:22 用户改: 「1.这个件往中央挪一点 2.如图，螺丝放在左右，不放在上下 3.电路板出线位置，四角5*5mm的位置，这里要上部留空」
  · 焊脚敞开区: 以焊脚为心 5×5 往上全空 (PCB 顶面以上无盖), 往 ±y 并到槽端、往 x 并到槽口和 AC 通道 (OPEN_BOX), 直接从上面焊线;
    盖只剩两排焊脚之间一段压 PCB。一个位置同时罩住镜像两侧的脚 (+x AC1/AC2, −x GND/24V 坐标差 ≤0.5); 脚下 Φ3 让位孔。
  · AC 引线 (11-19 15:00 改): 承载盘 Φ3.5 孔 B.AC_HOLES 在线圈腔正上方 (托盘最薄处), 内孔 (41.5, −17) 靠腔内缘 / 外孔 (51.4, −46.8) 靠腔外缘, 都在 AC 侧夹块外侧; 线从腔里竖上来, 跨 +x 夹块顶进敞开区焊 AC 脚; 夹块实心无通道。
  · 11-19 14:33 简化: 每件就是一根沿 y 的直方条 x21–36.4 × y(PCB±) × Z30.5–38.3, 无台阶/耳朵/圆弧裁。
  · 螺丝 (11-19 用户: 从下往上, 同底板): 每件 2×M3×6 超薄头, 从承载盘底 Φ7.4×1.5 让位 (支承 Z28.8) 穿 Φ3.4 通孔, 进方条底面 M3×4 铜螺母 (x34.0, y 对齐两排焊脚), 啮合 4; 线圈/玻纤板装之前拧。
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
MOD_L, MOD_W, MOD_H, MOD_G = 49.0, 30.5, 15.0, 19.2
HX = MOD_L / 2                              # 24.5
MOD_Y0 = -51.5                              # 11-19 用户「往中央挪」+ 补充: 挪到离灯板组正好 5 (实测最近 桥板 B 5.02, 次近 FPC B, 挪动量取整 0.5) ⇒ 比上午 −69.5 往 +y 挪 18.0 (11-16 托盘版 −72); 实测见 scratchpad wl_dist.py
MOD_Y1 = MOD_Y0 + MOD_W                     # −39.0
MOD_YC = (MOD_Y0 + MOD_Y1) / 2              # −54.25
PCB_T = 1.6                                 # 假设 (待实物)
PCB_GAP = 4.0                               # 用户: PCB 离底面 4
MZ0 = RIM_TOP + PCB_GAP                     # 34.5 PCB 底
PCB_Z1 = MZ0 + PCB_T                        # 36.1
MZ1 = MZ0 + MOD_H                           # 49.5 模块顶 (元件包络)
COMP_X = None                               # (下面按 GRIP 定)
SLOT_CLR_Z, SLOT_CLR_X, SLOT_CLR_Y = 0.2, 0.3, 0.3
SLOT_Z0, SLOT_Z1 = MZ0, PCB_Z1 + SLOT_CLR_Z  # 34.5–36.3
CAP_T = 2.0                                 # 11-19 14:33 简化成直方条: 盖 2 (用户「其余可薄」)
TOP_Z = SLOT_Z1 + CAP_T                     # 38.3
GRIP = 3.5                                  # 11-19 14:29 用户「这个件压住电路板宽度做到3.5mm就行了」(原压 5)
# 11-19 14:33 用户草图「我感觉就是这么一个件，然后有的壁厚一点」: 夹块 = 沿 y 直方条 (直角, 无台阶/耳朵/圆弧裁), 外侧半边 2 颗 M3 竖直通孔
CH_X = HX + SLOT_CLR_X + 1.2 + 1.5          # 27.5 (11-19 15:00 AC 竖通道已取消, 只作螺丝定位参考)
# 11-19 用户「螺丝是从下往上锁」「这个不通过玻纤，这个是 rim 上边的东西，和 soc 底板一样」: 照底板 BB_HOLES ——
#   承载盘 rim_ring_v1_2b 底面 Φ7.4×1.5 让位 (头埋托盘, 支承 Z28.8) + Φ3.4 通 → 夹块底面热压 M3×4 铜螺母 (Φ4.2×4, Z30.5–34.5) + Φ3.2 让尖到 Z35.5
#   螺丝 M3×6 超薄头 (Φ7×1.5): 支承 Z28.8 → 尾 Z34.8, 铜螺母啮合 4。须在线圈/玻纤板装上之前从承载盘底拧 (同底板)。
INS_D, INS_H = 4.2, 4.0
WALL_SCR = 2.0                              # 铜螺母孔壁 ≥2
BB_CB_D, BB_CB_H = 7.4, 1.5                 # = rotor_b 底板孔 (承载盘底让位)
SCR_X = 34.0                                # 螺丝心 x
assert SCR_X >= CH_X + 1.5 + WALL_SCR + INS_D / 2 - 1e-9                     # 夹块里: 铜螺母孔离 AC 通道壁 ≥2 (33.1)
# 11-19 15:00 用户「换个位置开，你开的不行，直径3.5mm。这两个孔需要在最薄的位置开，然后不要影响屏幕，然后和最薄这个环形相接就行」:
#   AC 引线孔 Φ3.5 改到 +x 夹块外侧 (螺丝再往外) 线圈腔 r39.9–72.5 正上方 (托盘最薄 3.2), 线圈线从腔里直接竖上来, 绕过夹块顶进焊脚敞开区; 夹块里 AC 竖通道取消
XI, XO = HX - GRIP, SCR_X + INS_D / 2 + WALL_SCR  # 方条 x 21.0–38.1 (+x 件); 槽深 = 3.5 + 端部余量 0.3
XF = XO                                     # (旧名)
COMP_X = XI                                 # 元件包络假设 |x|≤21 (两端 3.5 宽带给夹块)
WALL_OUT, WALL_IN = 3.0, 1.5                # 槽 −y 封口墙 (挡离心, 厚) / +y 封口墙
WALL_Y = WALL_IN
BY0, BY1 = MOD_Y0 - SLOT_CLR_Y - WALL_OUT, MOD_Y1 + SLOT_CLR_Y + WALL_IN   # 方条 y −55.3…−19.7
CB_Z = 27.3 + BB_CB_H                       # 28.8 螺丝头支承 (托盘底 Z_T0 27.3 + 1.5, 同底板)
SCR_L = 6.0                                 # M3×6 超薄头: 尾 Z34.8
REL_Z1 = CB_Z + SCR_L + 0.7                 # 35.5 让尖
EAR_Z1 = TOP_Z                              # (旧名)
R_MAX = 81.7                                # 罩内一切 ≤ r81.7
SHR_R0, SHR_R1 = 82.0, 85.0
OUT_R = R_MAX
ECC = B.SCR_ECC
# 引脚 (封装本地 fx 向右, fy 向下, 框 48.6×30; 绕 Z 转 180° 使 AC 在 +x): X = −(fx − 24.3), Y = MOD_YC + (fy − 15)  (待实物核)
FP = {'AC1': (2.8, 2.5), 'AC2': (2.0, 27.75), '24V': (45.91, 28.0), 'GND': (46.28, 3.22)}
PINS = {k: (round(-(fx - 24.3), 2), round(MOD_YC + (fy - 15.0), 2)) for k, (fx, fy) in FP.items()}
EXIT_D = 3.0
EXIT_X = 21.85                              # 镜像两侧共用
EXIT_Y = [MOD_Y0 + 3.1, MOD_Y0 + 28.1]      # −48.4 / −23.4 (两排焊脚)
SCR_OUT = [(SCR_X, EXIT_Y[0]), (-SCR_X, EXIT_Y[0])]   # 螺丝 y 对齐焊脚行: (±34, −48.4)
SCR_IN = [(SCR_X, EXIT_Y[1]), (-SCR_X, EXIT_Y[1])]    # (±34, −23.4)
OPEN = 5.0                                  # 用户「四角5*5mm的位置，这里要上部留空」: 以焊脚为心 5×5 以上全空; 往 ±y 并到槽端、往 x 并到槽口和 AC 通道 (不留细条)
OPEN_DY = OPEN / 2                          # 焊脚行 ±2.5
for k, (px, py) in PINS.items():            # 每个脚 (Φ1) 都要在某个 Φ3 出口里, 偏心 ≤ 1
    assert min(math.hypot(abs(px) - EXIT_X, py - ey) for ey in EXIT_Y) <= 1.0 - 1e-9, (k, px, py)
AC_HOLES = list(B.AC_HOLES)                 # 11-19 15:00: 内孔 (41.5, −17.0) r44.85 / 外孔 (51.4, −46.8) r69.48, 外孔从下往上看在内孔逆时针 20° (俯视顺时针)
def _box_gap(x, y, x0, y0, x1, y1): return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))
for _x, _y in AC_HOLES:
    _r = math.hypot(_x, _y); assert 39.9 + 1 + B.AC_HOLE_D / 2 <= _r <= 72.5 - 1 - B.AC_HOLE_D / 2, ('AC 孔离线圈腔内外缘 <1', _r)
    assert _box_gap(_x, _y, XI, BY0, XO, BY1) - B.AC_HOLE_D / 2 >= 1.5 - 1e-9, ('AC 孔离夹块 <1.5', _x, _y)
# 敞开区 (+x 件, 世界坐标 x0, y0, x1, y1): 外排从槽端到焊脚 +2.5, 内排从焊脚 −2.5 到槽端; x 从槽口外到 AC 通道外缘
OPEN_X0, OPEN_X1 = min(XI - 1.0, EXIT_X - OPEN / 2), HX + SLOT_CLR_X     # x 到槽端 (AC 竖通道取消)
OPEN_BOX = [(OPEN_X0, MOD_Y0 - SLOT_CLR_Y, OPEN_X1, EXIT_Y[0] + OPEN_DY), (OPEN_X0, EXIT_Y[1] - OPEN_DY, OPEN_X1, MOD_Y1 + SLOT_CLR_Y)]
assert all(b[0] <= EXIT_X - OPEN / 2 and EXIT_X + OPEN / 2 <= b[2] and b[1] <= ey - OPEN_DY + 1e-9 and ey + OPEN_DY <= b[3] + 1e-9 for b, ey in zip(OPEN_BOX, EXIT_Y))
assert sorted(AC_HOLES) == sorted(B.AC_HOLES), (AC_HOLES, B.AC_HOLES)

# ---------------- 夹块 ----------------
def clamp_a():
    s = gbox(XI, BY0, RIM_TOP, XO, BY1, TOP_Z)                                                    # 直方条
    s = cut(s, gbox(XI - 1, MOD_Y0 - SLOT_CLR_Y, SLOT_Z0, HX + SLOT_CLR_X, MOD_Y1 + SLOT_CLR_Y, SLOT_Z1))   # PCB 夹槽
    for x, y in (SCR_OUT[0], SCR_IN[0]):
        s = cut(s, cyl(x, y, INS_D, RIM_TOP - 1, RIM_TOP + INS_H), cyl(x, y, 3.2, RIM_TOP, REL_Z1))   # 底面铜螺母孔 Φ4.2×4 + Φ3.2 让尖
    for y in EXIT_Y:
        s = cut(s, cyl(EXIT_X, y, EXIT_D, RIM_TOP - 1, SLOT_Z0 + 0.01))                            # 焊脚下 Φ3 让位 (脚尾)
    for x0, y0, x1, y1 in OPEN_BOX:
        s = cut(s, gbox(x0, y0, PCB_Z1, x1, y1, TOP_Z + 1))                                        # 焊脚 5×5 以上全空 (PCB 顶面往上)
    return clean(s)

HA = clamp_a()
HB = clean(xf(HA, mirx()))
H = fuse(HA, HB)
pcb = gbox(-HX, MOD_Y0, MZ0, HX, MOD_Y1, PCB_Z1)
module = fuse(pcb, gbox(-COMP_X, MOD_Y0, PCB_Z1 - 0.01, COMP_X, MOD_Y1, MZ1))    # 占位: PCB + 中段元件包络
pins = {k: cyl(x, y, 1.0, PCB_Z1, PCB_Z1 + 2.0) for k, (x, y) in PINS.items()}   # 示意: 脚朝上伸出 2
def thin_up(x, y, zb, L): return fuse(cyl(x, y, 7.0, zb - 1.5, zb), cyl(x, y, 3.0, zb - 0.01, zb + L))   # 超薄头 Φ7×1.5 头在下
screws = [thin_up(x, y, CB_Z, SCR_L) for x, y in SCR_OUT + SCR_IN]
inserts = [cut(cyl(x, y, INS_D, RIM_TOP, RIM_TOP + INS_H), cyl(x, y, 3.0, 0, 50)) for x, y in SCR_OUT + SCR_IN]   # 夹块里 M3×4 铜螺母

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
                                                    离腔内缘=round(math.hypot(x, y) - B.AC_HOLE_D / 2 - 39.9, 2), 离腔外缘=round(72.5 - math.hypot(x, y) - B.AC_HOLE_D / 2, 2)) for x, y in AC_HOLES}
    rep['misc']['pin_exit_offset'] = {k: round(min(math.hypot(abs(px) - EXIT_X, py - ey) for ey in EXIT_Y), 2) for k, (px, py) in PINS.items()}
    # 最薄: 槽端 → AC 通道 / 通道 → 外面 / 螺丝孔 → r81.7
    rep['misc']['bar_size'] = dict(x=round(XO - XI, 2), y=round(BY1 - BY0, 2), z=round(TOP_Z - RIM_TOP, 2), x_range=[XI, round(XO, 2)], y_range=[round(BY0, 2), round(BY1, 2)])
    rep['misc']['walls'] = {'槽端→铜螺母孔': round(SCR_X - INS_D / 2 - (HX + SLOT_CLR_X), 2),
                            '铜螺母孔→条外面': round(XO - SCR_X - INS_D / 2, 2), '铜螺母孔→条 ±y 端': round(min(EXIT_Y[0] - INS_D / 2 - BY0, BY1 - EXIT_Y[1] - INS_D / 2), 2),
                            '槽 −y 封口墙': WALL_OUT, '槽 +y 封口墙': WALL_IN, '盖厚': CAP_T, '槽底 (PCB 下)': PCB_GAP, '压 PCB 宽': GRIP}
    rep['misc']['open_box_a'] = [[round(v, 2) for v in b] for b in OPEN_BOX]
    rep['misc']['cap_left_y'] = [round(OPEN_BOX[0][3], 2), round(OPEN_BOX[1][1], 2)]
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
    items = [('clamp_a', ma * RHO, ca), ('clamp_b', mb * RHO, cb), ('module', MOD_G, mod_c)] + [('M3×6超薄头+铜螺母', M3_G + INS_G, (x, y, 30)) for x, y in SCR_OUT + SCR_IN]
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
    items += [('M3×6 超薄头 (承载盘底往上)', s, '#888888', None, False) for s in screws] + [('M3×4 铜螺母 (夹块底面)', s, '#B8860B', None, False) for s in inserts]
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
