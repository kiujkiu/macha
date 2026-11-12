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
FL_THIN = 3.0                                  # 用户 11-11: flange_disc 底板减 3 (4.5→1.5), 顶面不动, 底面上抬
FL_UP = 1.0                                    # 用户 11-11: 定子法兰盘整体上移 1 (线圈环套环加高)
FL_Z0 = 15.5 + FL_THIN - DROP + FL_UP          # 法兰盘底 9.3
MF_THIN = 0.5                                  # 用户 11-11: mounting_flange 板厚 3→2.5 (顶面去 0.5)
MF_CB = 1.5                                    # 用户 11-11: 安装法兰 16 个 Φ7 沉孔深 2.0→1.5
FL_TOP = 22.5 - DROP + FL_UP                   # 法兰盘顶 13.3 (= 安装法兰底)
MF_TOP = 25.5 - MF_THIN - DROP + FL_UP         # 安装法兰顶 15.8
TUBE_TOP = FL_TOP                              # 用户 11-11 螺丝内移: 内管只到法兰盘顶 (不再穿安装法兰, 让螺丝头)
R_SCREW = 34.0                                 # 用户 11-11: 线圈环/法兰 8×M3 r36.3 → r34
TUBE_OD = 63.0                                 # 内管 r29.5–31.5 (壁 2)
COLLAR_D = 77.0                                # 套环 Φ84 → Φ77 (r38.5), 控制板跟着内移
FL_HOLE_R = TUBE_OD / 2 + 0.2                  # 法兰盘中心孔补到 r31.7
MF_HOLE_R = BORE_D / 2 + 0.2                   # 安装法兰中心孔补到 r29.7
BOARD_ANG = 90.0
COLLAR_M6 = []
FLANGE_SCREWS = [(R_SCREW * math.cos(math.radians(22.5 + 45 * k)), R_SCREW * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
COLLAR_FLAT = 35.5                                 # 用户 11-11: 套环四边削平到 ±35.5 (控制板可往里挪 3)
RING_CH = 5.0                                      # 用户 11-12: 套环改方座 ±35.5 (四角倒角 5), 四角 4×M3 先把线圈环锁在底盘上 (装定子盘之前)
RING_M3_XY = 29.5
RING_M3 = [(sx * RING_M3_XY, sy * RING_M3_XY) for sx in (1, -1) for sy in (1, -1)]
RING_CORNER_T = 5.0                                # 用户 11-12: Φ77 圆 (托定子盘) 以外的四角只留 5 厚
# 用户 11-12: 四角只开 Φ3.2 通孔 (不压铜螺母); M3x10 从盘底沉孔往上 (头底 z-2.5, 尾 z7.5, 离定子盘底 1.8), 四角顶面放 M3 螺母
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
WIRE_A0 = 255.0                                    # 用户 11-12: 电机出线口改到下边 (-Y, 255-285°), 原 75-105° 朝控制板
r_ = cut(r_, cut(_octa(COLLAR_FLAT + 1, RING_CH, RING_CORNER_T, FL_Z0 + 1), cyl(0, 0, COLLAR_D, RING_CORNER_T - 1, FL_Z0 + 2)))  # 圆外四角削到 5 厚
r_ = cut(r_, op(BRepAlgoAPI_Common, cyl(0, 0, 90, -1, FL_Z0 + 2.7, ang=30, a0=WIRE_A0), cyl(0, 0, 90, -1, FL_Z0 + 2.7)))
for x, y in FLANGE_SCREWS:
    r_ = cut(r_, cyl(x, y, 3.2, -1, TUBE_TOP + 1))
for x, y in RING_M3:
    r_ = cut(r_, cyl(x, y, 3.2, -1, FL_Z0 + 1))
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
_mf = cut(_mf0, _low, cyl(0, 0, 400, _mf_top, 100))
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
SH_R = 85.0                                        # 11-11 用户: M3 螺母让位圆 Φ14 贴下罩内墙 (r92-7)
SH_R_OLD = 83.0                                        # 用户 11-11: 下罩 M6 用 V1.1 四孔 (±62.5,±62.5) 往里挪到 r83, 下罩内侧加 4 个耳片
SH_M6 = [(SH_R * math.cos(math.radians(a)), SH_R * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
_bb = bbox(board)
SUP_R, SUP_A0 = 84.0, 22.5                         # 用户 11-11 选方案 1: 外圈 8×M3 在 22.5°+45k (M6 夹在每对中间), r86
OUT_ALL = [(SUP_R * math.cos(math.radians(SUP_A0 + 45 * k)), SUP_R * math.sin(math.radians(SUP_A0 + 45 * k))) for k in range(8)]
OUT_SCREWS = [(x, y) for x, y in OUT_ALL if not (_bb[0] - 6 < x < _bb[3] + 6 and _bb[1] - 6 < y < _bb[4] + 6)]   # 有托块, 锁到底盘
OUT_HANG = []                                      # 用户 11-12: 外圈 8×M3 取消, 定子盘只用中央 8×M3 锁底盘; OUT_SCREWS 只剩托块位置 (无孔)
OUT_SKIPPED = []
XT_ANG = 0.0                                       # XT60 正右边 (+X)
_c, _s = math.cos(math.radians(XT_ANG)), math.sin(math.radians(XT_ANG)); _rc = 112.5 - 11.95 - 0.55
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
M3_D, M3_CB_D, M3_CB_H = 3.2, 6.5, 3.5           # 内六角 M3 头 Φ5.5x3
def _loc(X, Y):      # 全局 -> 板本地
    p = gp_Pnt(X, Y, BOARD_Z).Transformed(BT.Inverted()); return p.X(), p.Y()
def _rect_hit(x, y, rad, r):   # 圆 (x,y,rad) 与本地矩形 r=(x0,y0,x1,y1) 相交
    dx = max(r[0] - x, 0, x - r[2]); dy = max(r[1] - y, 0, y - r[3]); return math.hypot(dx, dy) < rad
EXTRA, SKIP = [], []
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
    d = cut(d, cyl(p.X(), p.Y(), 3.2, -DISC_T - 1, 1), cyl(p.X(), p.Y(), 4.2, -DISC_T - 1, -DISC_T + 4.5))  # 铜螺母从底面压
for x, y in MOTOR_HOLES:                                                                   # 电机 4×M3 盘底上锁
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
d = cut(d, cyl(0, 0, 12.0, -3.0, 1))                                                       # 电机中央 Φ12x3
for x, y in RING_M3:                                                                      # 线圈环四角 4×M3x10: 盘底沉孔, 穿四角 (5 厚) 通孔顶面上螺母
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D / 2 + M3_CB_D / 2 + 1.0 for x, y in RING_M3 for a, b in FIXED + EXTRA), '线圈环 M3 沉孔离 M6 沉孔太近'
for x, y in FLANGE_SCREWS:                                                                 # 线圈环/法兰 8×M3: 铜螺母从盘底压
    d = cut(d, cyl(x, y, 3.2, -DISC_T - 1, 1), cyl(x, y, 4.2, -DISC_T - 1, -DISC_T + 4.5))
for x, y in SH_M6:                                                                         # 下罩 4×M3x10: 盘底沉孔往上, 螺母压三角块顶
    d = cut(d, cyl(x, y, M3_D, -DISC_T - 1, 1), cyl(x, y, M3_CB_D, -DISC_T - 1, -DISC_T + M3_CB_H))
assert all(math.hypot(x - a, y - b) >= CB_D + 1.0 for x, y in XT_GHOLES_DISC for a, b in FIXED + EXTRA), 'XT60 孔与网格孔沉孔重叠'
for x, y in XT_GHOLES_DISC:                                                                # XT60 压块 2×M6: 盘底沉孔上锁, 螺母压块顶
    d = cut(d, cyl(x, y, M6_D, -DISC_T - 1, 1), cyl(x, y, CB_D, -DISC_T - 1, -DISC_T + CB_H))
disc = clean(d); LOG['disc'] = dict(v=vol(disc))
# 4c 玻璃罩下罩+定位环 V1.2 (用户 11-11): 玻璃 OD200x5 高 245, 下端与转子承载盘顶齐平; 下罩从底盘包住定子到玻璃下端,
#    顶上承台托玻璃, 内卡 (伸进玻璃内) 深 20, 外卡深 10; 用 V1.1 定位环 4 个 M6 孔 (±62.5,±62.5) 从盘底锁
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
GL_OD, GL_T, GL_H = 200.0, 5.0, 245.0
Z_G = round(bbox(rim)[5], 2)                       # 玻璃下端 = 承载盘顶 32.0
SH_OUT = DISC_D / 2                                # 用户草图 11-11: 外面与底盘外缘齐平 r110
SPIG_IN = 92.0                                     # 墙内面 r92 竖直到底 (控制板最外角 r90.4, 承载盘 r89)
SPIG_T = 4.0                                       # 用户 11-11 嫌内卡薄: 2.8 → 4.0, 往里加 (内卡 r90.8–94.8, 离承载盘外缘 1.8)
GL_CLR = 0.2                                       # 玻璃单边间隙
IN_DEPTH, OUT_DEPTH = 20.0, 10.0                   # 内卡 20, 外卡贴玻璃处 10, 顶面 45° 往外降
TAB_T, TAB_W = 3.5, 18.0                           # 耳片厚 / 宽; M6x10 从盘底, 螺母压耳片顶 (z3.5–8.5, 法兰底 9.3)
NUT_T = 2.4                                        # M3 螺母
gi, go = GL_OD / 2 - GL_T - GL_CLR, GL_OD / 2 + GL_CLR    # 94.8 / 100.2
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
NUT_CLR_D = 10.0                                   # 定子盘/安装法兰在 M3 螺母处开 Φ10 让位 (原 M6 Φ14)
for x, y in SH_M6:
    s_ = cut(s_, cyl(x, y, 3.4, -1, TRI_T + 1))
SUP_W, SUP_IN = 12.0, 76.0                         # 用户 11-11: 托块加大, 宽 12, 从 r76 到墙, 端头 Φ12
for x, y in OUT_SCREWS:
    a_ = math.degrees(math.atan2(y, x))
    _sp = fuse(xf(gbox(SUP_IN + SUP_W / 2, -SUP_W / 2, 0, SPIG_IN + 1.0, SUP_W / 2, FL_Z0), rotz(a_)), cyl((SUP_IN + SUP_W / 2) * math.cos(math.radians(a_)), (SUP_IN + SUP_W / 2) * math.sin(math.radians(a_)), SUP_W, 0, FL_Z0))
    s_ = fuse(s_, _sp)                                 # 用户 11-12: 托块不开 M3 通孔
# XT60 电源口 (用户 11-11: 开口按之前 XT60 锁底板的压块留) — 复用 models/xt60_clamp_16p6x9p2x23p9 (压块 38x26.9x11 + 底垫 2, 叠高 13)
#   局部系: X 横跨 (孔距 25), Y 槽向 (-Y = 接头口, 朝外), Z 底=0; 底垫 z0, 压块 z2
XT_DIR = Path(__file__).resolve().parents[2] / 'models' / 'xt60_clamp_16p6x9p2x23p9'
XT_Y0, XT_Y1, XT_HW, XT_H = -11.95, 14.95, 19.0, 13.0
XT_RF = 112.5                                      # 接头口面半径: 内端 r85.6 让开安装法兰外裙 r85 (z9.3 起), 口面伸出底盘 2.5
XT_HOLES = [(-12.5, 0.55), (12.5, 0.55)]           # 压块 M6 孔 (局部)
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
    s_ = cut(s_, cyl(gx, gy, 14.0, XT_H, XT_H + 6.5))                                 # M6 螺母 (压块顶上) 让位井
def _stl(f):
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopoDS import TopoDS_Shape
    sh = TopoDS_Shape(); StlAPI_Reader().Read(sh, str(f)); return sh
_tz = gp_Trsf(); _tz.SetTranslation(gp_Vec(0, 0, 2.0))
xt_clamp = xf(xf(_stl(XT_DIR / 'xt60_clamp_16p6x9p2x23p9.stl'), _tz), XT_T)
xt_shim = xf(_stl(XT_DIR / 'xt60_shim_38x26p9x2p5.stl'), XT_T)
assert all(math.hypot(a - c, b - d_) < 1e-6 for (a, b), (c, d_) in zip(sorted(XT_GHOLES), sorted(XT_GHOLES_DISC))), (XT_GHOLES, XT_GHOLES_DISC)
LOG['outer'] = dict(n=len(OUT_SCREWS), skipped=OUT_SKIPPED)
LOG['xt60'] = dict(ang=XT_ANG, holes=[(round(x, 2), round(y, 2)) for x, y in XT_GHOLES])
_fd = flange_disc                                  # 用户 11-12: 定子盘外径改回原尺寸 (不再扩 Φ181)
_fd = cut(_fd, xf(gbox(-XT_HW - 0.5, XT_Y0 - 5, -1, XT_HW + 0.5, XT_Y1 + 0.5, 30), XT_T))   # XT60 压块处让位
# 用户 11-12: 外圈 r78 8 孔保留 (原 V0.4 定子盘/安装法兰上下盖互锁螺丝), 不再补实
LID_SCREWS = [(78.0 * math.cos(math.radians(22.5 + 45 * k)), 78.0 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]   # 外圈 r78 8 孔 (上下盖互锁)
LID_INS_D, LID_INS_H = 4.2, 3.0                    # 原 Φ2.5 攻牙孔 → M3x5 + 铜螺母 Φ4.2x3 从定子盘底面压 (顶留 1)
for x, y in LID_SCREWS: _fd = cut(_fd, cyl(x, y, 3.2, 0, 30), cyl(x, y, LID_INS_D, FL_Z0 - 1, FL_Z0 + LID_INS_H))
for x, y in SH_M6: _fd = cut(_fd, cyl(x, y, NUT_CLR_D, 0, 30))                # 下罩 M3 螺母让位
flange_disc = clean(_fd)
_mf2 = mounting_flange                             # 11-12 外径回原 Φ170: 保留 V0.4 原外裙 r82.5–85 (已同步短到 z9.3 = 定子盘底); 原先 cut ann(82.8,86) 是错的, 还留 0.3 薄片
for x, y in LID_SCREWS: _mf2 = cut(_mf2, cyl(x, y, 3.2, 0, 30))                # 上盖外圈 Φ3.2 通孔 (原 Φ7 沉孔保留)
for x, y in SH_M6: _mf2 = cut(_mf2, cyl(x, y, NUT_CLR_D, 0, 30))
mounting_flange = clean(_mf2)
seat = clean(s_); LOG['seat'] = dict(v=vol(seat), z_g=Z_G)          # 合并版 (下罩+外卡一体)
# 分体版 (用户 11-11): 外卡三角区单独一个环, 玻璃先套内卡再从上套环; 环底 2x2 凸筋插下罩顶槽 (单边 0.1)
TG_R0, TG_W, TG_H, TG_CLR = 104.0, 2.0, 2.0, 0.1
_lip = ann(go, SH_OUT + 1, Z_G, Z_G + OUT_DEPTH + 1)
clamp_ring = clean(fuse(op(BRepAlgoAPI_Common, seat, _lip), ann(TG_R0, TG_R0 + TG_W, Z_G - TG_H, Z_G + 0.5)))
shroud_split = clean(cut(seat, _lip, ann(TG_R0 - TG_CLR, TG_R0 + TG_W + TG_CLR, Z_G - TG_H - TG_CLR, Z_G + 1)))
LOG['split'] = dict(ring=vol(clamp_ring), shroud=vol(shroud_split))
tube = ann(GL_OD / 2 - GL_T, GL_OD / 2, Z_G, Z_G + GL_H)                     # 玻璃罩 OD200x5 高 245
nuts = []
seat_nuts = [cyl(x, y, 6.35, NUT_Z0, NUT_Z0 + NUT_T) for x, y in SH_M6]
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
] + [(f'post_D8x360_{i}', p, '#bbbbbb', None) for i, p in enumerate(posts)]
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
    POSE = {'disc': None, 'collar': None, 'hub': None, 'rim': 'flip', 'frameA': None, 'frameB': 'flip'}
    for n, s, col, k in NEW:
        if not k: continue
        t = s
        if POSE[k] == 'flip': t = xf(t, fx)
        z0 = bbox(t)[2]; tt = gp_Trsf(); tt.SetTranslation(gp_Vec(0, 0, -z0)); t = xf(t, tt)
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(OUT / '打印STL' / f'{n}.stl'))
    import pickle
    pickle.dump(dict(new=[(n, k) for n, _, _, k in NEW]), open(OUT / 'names.pkl', 'wb'))
    json.dump(LOG, open(OUT / 'log.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(LOG, indent=1, ensure_ascii=False))
