"""POV3D V1.2 结构: V1.0 基础上换电机 Φ55x21.5 + 打印底盘 Φ220 + 柱回 V0.4 柱位 + 承载盘外唇 Φ178."""
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
RIM_D = 178.0                          # 承载盘外唇 (原 180)
DISC_D, DISC_T = 220.0, 6.0
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
WIRE_A0, WIRE_AW, WIRE_ZH = 270.0, 40.0, 6.0      # 用户 11-13: 电机出线口 270–310° (宽 40, 对准实物出线 ~285–290°), 高 6 (底面 Z0 起); 原 255–285° 高到 Z11.2
r_ = cut(r_, cut(_octa(COLLAR_FLAT + 1, RING_CH, RING_CORNER_T, FL_Z0 + 1), cyl(0, 0, COLLAR_D, RING_CORNER_T - 1, FL_Z0 + 2)))  # 圆外四角削到 RING_CORNER_T (4.5) 厚
r_ = cut(r_, op(BRepAlgoAPI_Common, cyl(0, 0, 90, -1, WIRE_ZH, ang=WIRE_AW, a0=WIRE_A0), cyl(0, 0, 90, -1, WIRE_ZH)))
# 用户 11-13: 出线口边 (310° 射线) 切过 315° 角耳, 在底边留一个尖三角 ⇒ 角耳出线口一侧 (310–315°) 修成绕螺丝孔的圆 R4.3 (法兰螺母 Φ7.6 + 0.5)
_ca = math.radians(round((WIRE_A0 + WIRE_AW - 45) / 90) * 90 + 45)            # 出线口末端相邻的角 (315°)
_cx, _cy = RING_M3_XY * math.sqrt(2) * math.cos(_ca), RING_M3_XY * math.sqrt(2) * math.sin(_ca)
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
MF_THIN_LOW = 3.0                             # 11-12 夜: 只 flange_disc 加厚; 安装法兰外裙 (r82.5–85) 底仍按原 FL_THIN 3 切 ⇒ 底 Z9.5 (下罩法兰螺母顶 8.7 下方留 0.8)
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
import math as m
v_old_holes = 4 * (m.pi * 1.6**2 * 5 + m.pi * 3.5**2 * 4)
LOG['hub'] = dict(v0=v0, v=vol(hub), fill=v_fill, old_holes_expected=v_old_holes)

# ---------------- 3 承载盘 ----------------
r0 = one(C10 / 'rim_ring_v1_0.step'); v0 = vol(r0)
rim = zdown(clean(op(BRepAlgoAPI_Common, r0, cyl(0, 0, RIM_D, 25, 50)))); LOG['rim'] = dict(v0=v0, v=vol(rim))

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
_raw = one(BOARD_F); _B = _BB(); _bc = _TC(); _B.MakeCompound(_bc); _drop = 0
NOPOP = [(20.1, 28.4, 24.7, 41.0), (94.0, 99.5, 28.9, 41.0)]       # XT60 / MR30 (V1.0 同, 板系 +20/+10)
for s__ in solids(_raw):
    b__ = bbox(s__)
    if any(b__[0] >= x0 - .01 and b__[3] <= x1 + .01 and b__[1] >= y0 - .01 and b__[4] <= y1 + .01 for x0, x1, y0, y1 in NOPOP) \
       and (b__[5] > 1.61 or b__[2] < -0.02):
        _drop += 1; continue
    _B.Add(_bc, s__)
board = xf(_bc, BT); LOG['board'] = dict(dropped_solids=_drop)
def bl(x0, y0, x1, y1, z0, z1):      # 板本地矩形 -> 全局实体 (z 为全局)
    return xf(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0 - BOARD_Z), gp_Pnt(x1, y1, z1 - BOARD_Z)).Shape(), BT)
BHOLES = [(24.49, 14.49), (24.49, 45.49), (95.49, 14.49), (95.49, 45.49)]
SINK = (72.0, 10.0, 92.0, 50.0)                                     # 板系 x52..72 y0..40, 盖 6 颗 MOS
RELIEFS = [(21.0, 28.3, 24.8, 40.9), (94.1, 99.0, 29.0, 40.9), (54.7, 62.3, 10.3, 12.8)]   # x0,x1,y0,y1 背面焊点/排针
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
# 4b 底盘: 剩下的 M6 网格位 (节距 25, ±12.5..±87.5, 同原金属网格板) 全做通孔+沉孔
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
M3_D, M3_CB_D, M3_CB_H = 3.2, 7.0, 2.0           # 内六角 M3 头 Φ5.5x3; 盘底往上装沉孔 用户 11-12: Φ6.5×3.5 → Φ7×2
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
KEY = key_bracket_v1_2.make_key_bracket(dict(SH_OUT=DISC_D / 2, DISC_T=DISC_T, M3_CB_H=2.0, M3_D=3.2))
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
LOG['disc_holes'] = dict(collar=len(COLLAR_M6), grid=len(EXTRA), skipped=SKIP)
d = cyl(0, 0, DISC_D, -DISC_T, 0)
for x, y in FIXED + EXTRA:
    d = cut(d, cyl(x, y, M6_D, -DISC_T - 1, 1), cyl(x, y, CB_D, -DISC_T - 1, -DISC_T + CB_H))
for x, y in MOTOR_HOLES:                                                                  # 电机 4×M3 从盘底往上
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1))
d = cut(d, bl(SINK[0], SINK[1], SINK[2], SINK[3], -DISC_T - 1, 1))                       # 散热片通槽 20x40, 零间隙
for x0, x1, y0, y1 in RELIEFS:
    d = cut(d, bl(x0, y0, x1, y1, -3.0, 1))                                               # 背面让位 深 3
for x, y in BHOLES:
    p = gp_Pnt(x, y, 0).Transformed(BT)
    d = cut(d, cyl(p.X(), p.Y(), M3_D, -DISC_T - 1, 1), cyl(p.X(), p.Y(), M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))  # 用户 11-13: 控制板 4×M3 改盘底 Φ7×2 沉孔往上, 法兰螺母坐板顶 (原板顶往下进铜螺母)
for x, y in MOTOR_HOLES:                                                                   # 电机 4×M3 盘底上锁
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
d = cut(d, cyl(0, 0, 12.0, -3.0, 1))                                                       # 电机中央 Φ12x3
for x, y in RING_M3:                                                                      # 线圈环四角 4×M3x10: 盘底沉孔, 穿四角 (5 厚) 通孔顶面上螺母
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D / 2 + M3_CB_D / 2 + 1.0 for x, y in RING_M3 for a, b in FIXED + EXTRA), '线圈环 M3 沉孔离 M6 沉孔太近'
for x, y in FLANGE_SCREWS:                                                                 # 线圈环/法兰 8×M3: 铜螺母从盘底压
    d = cut(d, cyl(x, y, 3.2, -DISC_T - 1, 1), cyl(x, y, INS_HOLE_D, -DISC_T - 1, -DISC_T + INS_HOLE_H))
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
disc = clean(d); LOG['disc'] = dict(v=vol(disc))
LOG['coil_drv'] = dict(xpc=CD.XPC, xb=CD.XB, has_mc=CD.HAS_MC, has_cc=CD.HAS_CC, merge_err=CD.MERGE_ERR, mc_holes=[(round(x, 2), round(y, 2)) for x, y in CD.MC_HOLES],
                       cc_holes=[(round(x, 2), round(y, 2)) for x, y in CD.CC_HOLES], pcb_z=(CD.PCB_Z0, CD.PCB_Z1), mos_y=(CD.MOS_Y_LEAD, CD.MOS_Y_TIP), bcap_pits=CD.BCAP_PITS,
                       cap=(CD.CAP_CX, CD.CAP_Y0, CD.CAP_Y1, CD.CAP_ZC, CD.CAP_GROOVE), sink=(CD.SINK_X0, CD.SINK_Y0, CD.SINK_X1, CD.SINK_Y1))
# 4c 玻璃罩下罩+定位环 V1.2 (用户 11-11): 玻璃 OD200x5 高 245, 下端原与转子承载盘顶齐平 (11-13 晚改: 内卡顶 = LED 下沿, 见 Z_G); 下罩从底盘包住定子到玻璃下端,
#    顶上承台托玻璃, 内卡 (伸进玻璃内) 深 20, 外卡深 10; 用 V1.1 定位环 4 个 M6 孔 (±62.5,±62.5) 从盘底锁
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
GL_OD, GL_T, GL_H = 200.0, 5.0, 245.0
Z_RIM_TOP = round(bbox(rim)[5], 2)                 # 承载盘顶 32.0
SH_OUT = DISC_D / 2                                # 用户草图 11-11: 外面与底盘外缘齐平 r110
SPIG_T = 4.0                                       # 用户 11-11 嫌内卡薄: 2.8 → 4.0, 往里加 (内卡 r90.8–94.8, 离承载盘外缘 1.8)
GL_CLR = 0.2                                       # 玻璃单边间隙
IN_DEPTH, OUT_DEPTH = 20.0, 10.0                   # 内卡 20, 外卡贴玻璃处 10, 顶面 45° 往外降
# 用户 11-13 晚: V2 灯板 (LED_V0.2.0 11-13, 板高 208, LED 在上部); SoC+WiFi 同一平面 = 转接板 (POV3D_V2_BaseBoard 140×80×1.6,
#   器件全在顶面, 底面只有插件脚) + MLK CZ06 核心板 (60×35, DF40 合高 3.0 + 板 1.6 + 顶面器件 ≈2.0 = 6.6, 转接板 README), 转接板出 2 根 FPC 给桥板;
#   玻璃下加高, 内卡顶 (不透光部分的最高点) = LED 下沿 ⇒ 灯全露出来
BB_STANDOFF, BB_T, CZ06_H, CZ06_CLR = 3.0, 1.6, 6.6, 2.0   # 转接板垫柱 (让插件脚) / 板厚 / CZ06 堆高 / CZ06 顶 → 灯板下沿
Z_BB0 = Z_RIM_TOP + BB_STANDOFF                    # 转接板底 35.0
SCREEN_GAP = BB_STANDOFF + BB_T + CZ06_H + CZ06_CLR   # 承载盘顶 → 灯板下沿 13.2
LED_BOARD_H = 208.0                                # 灯板高 (板框 163.76 × 208.01)
LED_LOW_OFF = 37.88                                # 灯板下沿 → 最下一行 LED 像素下沿 (行心 38.66 − 节距 1.5626/2)
Z_SCR0 = Z_RIM_TOP + SCREEN_GAP                    # 灯板下沿 45.2
Z_LED0 = Z_SCR0 + LED_LOW_OFF                      # LED 下沿 83.08
Z_SCR1 = Z_SCR0 + LED_BOARD_H                      # 灯板上沿 253.2
Z_G = round(Z_LED0 - IN_DEPTH, 2)                  # 玻璃下端 63.08 (原 = 承载盘顶 32.0)
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
LOG['key'] = dict(m3=[(round(x, 2), round(y, 2)) for x, y in KEY_M3], skin=KEY['skin'], flap={k: KEY['flap'][k] for k in ('F_top', 'F_bot', 't_top')}, pocket_bbox=KEY['pocket_bbox'], bracket_vol=KEY['bracket_vol'],
                  holes=[(round(x, 2), round(z, 2), dd) for x, z, dd in KEY['holes']])
def _stl(f):
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopoDS import TopoDS_Shape
    sh = TopoDS_Shape(); StlAPI_Reader().Read(sh, str(f)); return sh
_tz = gp_Trsf(); _tz.SetTranslation(gp_Vec(0, 0, 2.0))
# 读 STEP (m2b 由同一 mesh 转的实体, 体积与 STL 差 <0.01%); STL 读进来只是壳, 紧固件干涉 (BRepAlgoAPI_Common) 算不出体积
xt_clamp = xf(xf(one(XT_DIR / 'xt60_clamp_v1_2.step'), _tz), XT_T)
xt_shim = xf(one(XT_DIR / 'xt60_shim_v1_2.step'), XT_T)
assert all(math.hypot(a - c, b - d_) < 1e-6 for (a, b), (c, d_) in zip(sorted(XT_GHOLES), sorted(XT_GHOLES_DISC))), (XT_GHOLES, XT_GHOLES_DISC)
LOG['outer'] = dict(n=len(OUT_SCREWS), skipped=OUT_SKIPPED)
LOG['xt60'] = dict(ang=XT_ANG, holes=[(round(x, 2), round(y, 2)) for x, y in XT_GHOLES])
_fd = flange_disc                                  # 用户 11-12: 定子盘外径改回原尺寸 (不再扩 Φ181)
_fd = cut(_fd, xf(gbox(-XT_HW - 0.5, XT_Y0 - 5, -1, XT_HW + 0.5, XT_Y1 + 0.5, XT_H + 0.5), XT_T))   # XT60 压块处让位 (11-13 压块内移: 切到 r82.3, 只切 Z≤13.5)
# 用户 11-12: 外圈 r78 8 孔保留 (原 V0.4 定子盘/安装法兰上下盖互锁螺丝), 不再补实
CAV_R0 = 31.7 + CB7                                # 线圈腔内壁 r40 → r38.7 (内墙 r31.7–38.7)
CAV_R1 = 82.5 - CB7                                # 线圈腔外壁 r72.6 → r75.5 (外墙 r75.5–82.5)
CAV_Z0 = FL_Z0 + 2.5                               # 腔底 Z11.0 不变 (底板 1.5 → 2.5, 11-12 夜)
LID_R = 82.5 - CB7 / 2                             # 用户 11-12: 上下盖孔居中到外墙 r79 (原 V0.4 r77.5, 曾误开 r78)
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
flange_disc = clean(_fd)
_mf2 = mounting_flange                             # 11-12 外径回原 Φ170: 保留 V0.4 原外裙 r82.5–85 (已同步短到 z9.3 = 定子盘底); 原先 cut ann(82.8,86) 是错的, 还留 0.3 薄片
for x, y in _V04_OUT: _mf2 = fuse(_mf2, cyl(x, y, CB7 + 0.4, FL_TOP, MF_TOP))  # 原 r77.5 Φ7 沉孔 + 孔补实 (板内)
for x, y in LID_SCREWS: _mf2 = cut(_mf2, cyl(x, y, 3.2, 0, 30), cyl(x, y, CB7, MF_TOP - MF_CB, 40))   # 上盖 r79: Φ3.2 + 顶面 Φ7×1.5
_mf2 = cut(_mf2, xf(gbox(-XT_HW - 0.5, XT_Y0 - 5, -1, XT_HW + 0.5, XT_Y1 + 0.5, XT_H + 0.5), XT_T))   # 11-13: 安装法兰外裙 r82.5–85 在 XT60 压块处让位 (Z≤13.5)
mounting_flange = clean(_mf2)
seat = clean(s_); LOG['seat'] = dict(v=vol(seat), z_g=Z_G)          # 合并版 (下罩+外卡一体)
# 分体版 (用户 11-11): 外卡三角区单独一个环, 玻璃先套内卡再从上套环; 环底 2x2 凸筋插下罩顶槽 (单边 0.1)
TG_R0, TG_W, TG_H, TG_CLR = 104.0, 2.0, 2.0, 0.1
_lip = ann(go, SH_OUT + 1, Z_G, Z_G + OUT_DEPTH + 1)
clamp_ring = clean(fuse(op(BRepAlgoAPI_Common, seat, _lip), ann(TG_R0, TG_R0 + TG_W, Z_G - TG_H, Z_G + 0.5)))
shroud_split = clean(cut(seat, _lip, ann(TG_R0 - TG_CLR, TG_R0 + TG_W + TG_CLR, Z_G - TG_H - TG_CLR, Z_G + 1)))
LOG['split'] = dict(ring=vol(clamp_ring), shroud=vol(shroud_split))
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
Z_GT = Z_G + GL_H                                  # 玻璃上端 (11-13 晚 Z_G 63.08 ⇒ 308.08; 原 277.0)
GT_DEPTH = 12.0                                    # 内/外卡深 (玻璃下 20/10; 这里同深, 底面同高好打印)
GT_TOP_T = 4.0                                     # 玻璃端面以上板厚
GT_Z0, GT_Z1 = Z_GT - GT_DEPTH, Z_GT + GT_TOP_T    # 265 / 281
assert Z_SCR1 + 3.0 <= GT_Z0, f'灯板上沿 Z{Z_SCR1} 离玻璃上最低处 Z{GT_Z0} 不足 3'
LOG['screen'] = dict(z_board=(Z_SCR0, Z_SCR1), z_led0=round(Z_LED0, 2), z_g=Z_G, z_gt=Z_GT, top_clear=round(GT_Z0 - Z_SCR1, 2), min_gl_h=round(Z_SCR1 + 3.0 + GT_DEPTH - Z_G, 2))
GT_FOOT = 1.0                                      # 外卡底平带 (r100.2–101.2, 落床), 斜面 → r110 处
GT_CH = 1.0                                        # 顶面外缘倒角
GD_OD, GD_ID, GD_T = 180.0, 20.0, 10.0             # 圆环玻璃 (用户 11-13: t5 → t10)
GD_CLR, GD_RECESS = 0.3, 0.2                       # 玻璃窝径向单边 / 玻璃顶低于环顶
GD_Z1 = GT_Z1 - GD_RECESS                          # 280.8
GD_Z0 = GD_Z1 - GD_T                               # 270.8 (窝深 10.2)
GD_POCKET_R = GD_OD / 2 + GD_CLR                   # 90.3
GT_LEDGE_R, GT_LEDGE_V = 85.5, 0.5                 # 托台内缘 r85.5 (搭玻璃 4.5), 内缘直边 0.5, 下面 45° 斜回内卡内面
_gin = gi - SPIG_T                                 # 90.8
assert (GD_Z0 - GT_LEDGE_V - GT_Z0) >= (_gin - GT_LEDGE_R) - 1e-6, '托台底面要 ≥45° (正立打印免支撑)'
GT_RZ = [(_gin, GT_Z0), (gi, GT_Z0), (gi, Z_GT), (go, Z_GT), (go, GT_Z0), (go + GT_FOOT, GT_Z0),
         (SH_OUT, Z_GT - LIP_EDGE), (SH_OUT, GT_Z1 - GT_CH), (SH_OUT - GT_CH, GT_Z1),
         (GD_POCKET_R + 0.5, GT_Z1), (GD_POCKET_R, GT_Z1 - 0.5),                       # 窝口 0.5 倒角 (放玻璃)
         (GD_POCKET_R, GD_Z0), (GT_LEDGE_R, GD_Z0), (GT_LEDGE_R, GD_Z0 - GT_LEDGE_V)]
GT_CONE_DEG = math.degrees(math.atan2(Z_GT - LIP_EDGE - GT_Z0, SH_OUT - go - GT_FOOT))   # 外卡斜面与水平 (≥45 免支撑)
glass_top = clean(revol(GT_RZ))
glass_disc = ann(GD_ID / 2, GD_OD / 2, GD_Z0, GD_Z1)                           # 外购圆环玻璃 (装配用实体)
# 中心堵头 (一件): 顶法兰 Φ32 压玻璃顶; 管 r8.2–9.8 穿 Φ20 孔 (单边 0.2); 孔下 30° 倒钩到 r11 (钩 1.0), 45° 导入到 r9; 6 条 2 宽槽 → 6 爪
GT_BEARING = bool(int(os.environ.get('GT_BEARING', '0')))   # 默认堵头; 1 = 法兰内开 688 轴承窝 (Φ8 轴从下穿爪内孔进来)
GH_FL_D, GH_FL_T = 32.0, 3.0
GH_R0, GH_R1 = 8.2, GD_ID / 2 - 0.2               # 爪内 r8.2 (Φ16.4 > 688 外径 16, 轴承可从下穿进窝) / 外 r9.8
GH_BARB, GH_CATCH_DZ, GH_TIP_R = 1.0, 0.7, 9.0     # 倒钩外 r = 10 + 1.0; 钩面 30° (Δz 0.7); 导入 45° 到 r9
GH_SLOTS, GH_SLOT_W = 6, 2.0
BRG_D, BRG_H, BRG_ROOF = 16.1, 5.0, 1.5            # 688 = 8×16×5; 窝 Φ16.1 (打印孔偏小, 试配), 顶留 1.5
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
    _gh = cut(_gh, cyl(0, 0, BRG_D, GD_Z1 - 0.01, GD_Z1 + BRG_H))
glass_top_hub = clean(_gh)
GH_L = GH_SLOT_TOP - _zt
GH_STRAIN = 1.5 * (GH_R1 - GH_R0) * GH_BARB / GH_L ** 2   # 悬臂根部应变 ≈ 1.5·t·δ/L²
LOG['glass_top'] = dict(v=vol(glass_top), z=(GT_Z0, GT_Z1), z_tube_top=Z_GT, cone_deg=round(GT_CONE_DEG, 1), disc_z=(GD_Z0, GD_Z1), disc_mass_g=round(vol(glass_disc) * 2.5e-3),
                        hub_v=vol(glass_top_hub), hub_z=(round(_zt, 2), GD_Z1 + _fl_t), finger_L=round(GH_L, 2), finger_strain=round(GH_STRAIN, 4), bearing=GT_BEARING,
                        valid=(BRepCheck_Analyzer(glass_top).IsValid(), BRepCheck_Analyzer(glass_top_hub).IsValid()))
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
    ('rim_ring_v1_2_D178', rim, '#6aa84f', 'rim'),
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
