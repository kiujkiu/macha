# -*- coding: utf-8 -*-
"""V1.2 转子罩 (11-16, 方案见 v1.2/concept/shroud_balance_concept.png; 高度按 11-16 新布局: 灯板下沿 Z37 / LED 下沿 Z74.88; 罩顶 + 顶盖 = 玻璃托顶 Z73.08)。
    cd v1.2/scripts && ../../.venv/bin/python rotor_shroud_v1_2.py
世界坐标同 build_v1_2: 承载盘顶 Z32, 不转玻璃座内卡内壁 r90.8 (顶 Z73.08)。
结构:
  - 11-16 晚 用户: "罩壁缩进坐盘上" (照 V0.4: 罩外径 = 转子盘外径 Φ170, 罩壁平底坐承载盘顶, 螺丝从罩内往下锁, 无裙边)。
  - 罩壁 r82–85, Z32–73.08 (= 玻璃托顶, 上面盖顶盖; 平底整圈直接坐承载盘顶 Z32, 无内沿), 两半 A (+x) / B (−x); B = A 绕 Z 转 180° (同一个件, 打 2 个)。
    ±x 两端罩壁开竖缝 |y|≤8.6, Z 全高 (两端立板天线板 x82.6–84.3 |y|≤8 Z32–75.6 坐在缝里)。静止间隙: 罩外 r85 对玻璃座内壁 r90.8 = 5.8。
  - 罩底 4 个凸台 (B.SHR_HOLES r78.5 @ 50/140/230/320°; A 半管 50°/320°) 宽 8 × r74–罩壁 × Z32–36 压承载盘顶: M3×8 内六角从上往下 (头支承 Z36, 尾 Z28),
    进承载盘顶面 M3×4 铜螺母 (Z28–32, 啮合 4); 凸台上面 45° 斜撑接罩壁, 斜撑里 Φ6.5 竖孔让螺丝头/起子 (起子从罩顶开口竖直进, 穿配重唇 Φ6.5 让位孔)。
    凸台 x 方向离底板 r3 板框 (|x|≤40 / −51.2) 和无线托盘 (|x|≤26.5) 都远, 不用削。
  - 底板 r3 板框 4 个角 (r83 圆弧, 最远 r83.1) 伸进罩壁 r82: 壁内面开 4 段让位槽 r→83.6 × Z34.7–36.9 (+ 转 180° 对称处)。
  - 分缝 (x=0, ±y) 内侧凸耳 x±7 × r74–罩壁 × Z51–66.58 (上接配重唇), 2 颗切向 M3×14 (|y|78.5, Z55 / Z62.5), 一侧螺丝头, 另一侧六角螺母槽 (槽口朝罩内, 螺母从内侧推进)。
    +y 缝: 头在 B 侧 (x<0), 螺母在 A 侧; −y 缝相反 (180° 对称)。凸耳底 Z51 > 无线托盘顶 Z50 / 底板 J5 顶 Z38.6。
  - 顶盖 rotor_lid_v1_2 ×2 (±y D 形, 同件转 180°): 厚 2, 外圆 r81.9, Z71.08–73.08 顶面 = 罩顶 = 玻璃托顶, 坐配重唇上, 内边 |y|4.8; 桥板处通槽 (内边退到 y8.77);
    每片 2×M3×8 内六角 (借 37.5°/127.5° 配重孔, −y 片 217.5°/307.5°; 盖底凸块 r75.6–81.9 × 9.6 × 3 插进唇缺槽, 平底沉孔 Φ5.7×3 头埋平) + 唇下螺母。
  - 配重唇 r76–82, Z66.08–71.08 (顶 = 盖底), 33°–147° / 213°–327° (让开 ±x 灯板两端/支撑/天线); M3 孔 @ r79 (每侧 8 个配重 + 2 个盖螺丝, 避开罩底起子孔 / 分缝凸耳),
    顶面 Φ5.8 沉孔深 3.2 (M3×16 内六角头顶 Z70.88 < 盖底 71.08); 唇下挂 M3 螺母 (最多 6 颗, 平边贴罩壁防转; 唇宽只有 6, Φ7 垫片放不下; 尾端 Z51.88 > 托盘顶 Z50)。
打印: 倒放 (罩顶 Z73.08 落床; 配重唇顶比罩顶低 2 (给顶盖), 倒放时唇悬空 2 mm ⇒ 唇下加热床支撑) (凸台/凸耳全部 45° 或从唇上长出; 只有 Φ6.5 / Φ5.8 孔顶小搭桥)。
"""
import io, contextlib, json, math
from pathlib import Path
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
import v2_boards_v1_2 as V
from helpers import read_step, write_doc
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec, gp_Ax2, gp_Dir, gp_Ax1
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCone
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz
NAME = 'rotor_shroud_v1_2'
OUT = B.V12 / 'models' / NAME; OUT.mkdir(parents=True, exist_ok=True)


def tr(dx, dy, dz): t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz)); return t
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
def prism_xz(pts, y0, y1):
    """(x,z) 闭合折线在 y0 平面, 沿 +y 拉到 y1"""
    pg = BRepBuilderAPI_MakePolygon()
    for x, z in pts: pg.Add(gp_Pnt(x, y0, z))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, y1 - y0, 0)).Shape()
def sector(r0, r1, z0, z1, a0, a1):
    return cut(cyl(0, 0, 2 * r1, z0, z1, ang=a1 - a0, a0=a0), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
def pol(r, a): return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
def hexprism_x(y, z, af, x0, x1):
    """六角 (对边 af, 对边面平行 xz ⇒ 角朝 ±z) 沿 x"""
    rc = af / math.sqrt(3)
    pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.radians(90 + 60 * k); pg.Add(gp_Pnt(x0, y + rc * math.cos(a), z + rc * math.sin(a)))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(x1 - x0, 0, 0)).Shape()


# ---------------- 尺寸 ----------------
Z0 = B.Z_RIM_TOP                    # 32.0 罩底 = 承载盘顶
Z1 = B.Z_VIEW0                      # 罩顶 = 玻璃托 (内卡) 顶 73.08 (用户 11-16: 罩子上沿和玻璃托齐平; 顶盖也在这高度, LED 下沿 ~75.0)
R0, R1 = 82.0, 85.0                 # 罩壁 (11-16 晚 缩进坐盘上: 外圆 = 承载盘 Φ170; 离静止内壁 r90.8 留 5.8)
ST_IN = B.SPIG_IN                   # 90.8
assert Z1 == B.Z_VIEW0 and Z1 < B.Z_LED0
BB_RELIEF_A = []   # 11-16 晚: 底板 r3 rev c 板角已收进 r81.7, 罩壁内面不再开让位槽 (原 59.5–63.5/74–80.5/99.5–106/126–131°)
BB_RELIEF_R, BB_RELIEF_Z = 83.6, (34.7, 36.9)
SLOT_Y = 10.1                       # ±x 两端罩壁竖缝 |y|≤10.1 全高 (天线板 x82.6–84.3 |y|≤9.75; 11-16 晚 天线换 18.5×37.7 软板)
# 底部固定 (4 孔, 进承载盘顶面铜螺母 = B.SHR_HOLES)
HOLE_R = 78.5
MNT_A = [50.0, 140.0, 230.0, 320.0]            # A 半 (+x) 管 50°/320°, B 半 = 转 180°
assert all(math.dist(pol(HOLE_R, a), p) < 1e-6 for a, p in zip(MNT_A, B.SHR_HOLES)), '罩底孔要和 B.SHR_HOLES 一致'
BOSS_W, BOSS_RI, BOSS_Z1 = 8.0, 74.0, 36.0     # 凸台 宽 8 (切向) × r74–罩壁 × Z32–36
GUS_Z1 = BOSS_Z1 + (R0 - BOSS_RI)              # 45° 斜撑顶 (贴壁处) Z44
ACC_D = 6.5                                    # 螺丝头 / 起子让位孔
MNT_L = 8.0                                    # M3×8: 头支承 Z36 ⇒ 尾 Z28 (= 铜螺母底)
INS_Z = (28.0, 32.0)                           # 承载盘顶面 Φ4.2×4.0 孔里的 M3×4 铜螺母 Z28–32
# 分缝凸耳
LUG_HX, LUG_Y0, LUG_Y1 = 7.0, 74.0, 83.0       # x 0..±7, |y| 74..83 (外端埋进罩壁 r82)
LUG_Z0 = 51.0                                  # > 无线托盘顶 Z50 (底板 J5 x±20.7 y72–80 顶 Z38.6 也在下面)
LUG_SY, LUG_SZ = 78.5, (55.0, 62.5)            # 切向螺丝轴线 |y|=78.5, Z55 / Z62.5 (头顶 65.25 < 唇底 66.08)
NUT_AF, NUT_T, NUT_DEPTH = 5.5, 2.4, 2.5       # M3 螺母; 槽 x 4.5..7 (口朝罩内)
SEAM_L = 14.0                                  # M3×14: 头支承 x=∓7 ⇒ 尾 ±7 (与螺母外面齐)
# 配重唇
# 顶盖 (11-16 用户截图: 罩子要把 LED 以下从上面也盖住) — 两片 D 形 (±y, 同件转 180°), 顶面 = 罩顶 = LED 下沿, 坐在配重唇上
LID_T = 2.0
LID_Z0 = Z1 - LID_T                  # 71.08 盖底 = 唇顶
LID_Y0 = 4.8                         # 盖内边 |y| (LED 面 3.768 + MIP 0.59 = 4.36, 留 0.44)
LID_R = R0 - 0.1                     # 盖外圆 r81.9 (罩壁内面 r82, 打印件嵌套单边 0.1)
BR_POCKET = (-32.5, 0.0, 32.5, 8.77, -1.0)   # 桥板 x±32 y6.77–8.37 顶 Z73.0 ≈ 盖顶: 通槽 (盖内边在这段退到 y8.77)
ANT_NOTCH = (82.2, 8.4)              # 两端立板天线板 x82.6–84.3 |y|≤8 顶 Z75.6: 缺口 |x|≥82.2 —— 罩缩到 r82 后已在盖外圆 r81.9 以外, 留着不起作用
# 盖螺丝 (+y 片): 原 45°/135° 离罩底起子孔 50°/140° 太近 ⇒ 37.5° / 127.5° (都离起子孔 12.5°; 用户提的 142.5° 离 140° 只有 2.5°, 不行)
LID_SCR_A = [37.5, 127.5]            # −y 盖 = 转 180° ⇒ 217.5/307.5 (A 半里落在 37.5 / 307.5, 两半同件)
LID_SCR_ALL = LID_SCR_A + [a + 180 for a in LID_SCR_A]
# 11-16 用户: 不能用 V 形沉头 ⇒ 普通 M3 内六角 (头 Φ5.5×3) 平底沉孔; 盖底下长凸块插进配重唇缺槽, 局部加厚到 5 让螺丝头埋平
LID_BOSS_RAD = (75.6, 81.9)          # 凸块径向 (唇 r76–82; 外端与盖外圆齐, 内端多伸 0.4 进空处, 缺槽从 r75 开)
LID_BOSS_W, LID_BOSS_H = 9.6, 3.0    # 凸块切向宽 / 往下伸 (盖底 71.08 → 68.08); 唇缺槽 切向 10 × 深 3.1 (槽底 67.98)
LID_CB_D, LID_CB_H = 5.7, 3.0        # 平底沉孔 Φ5.7 深 3 (r79 ± 2.85 ⇒ 外缘 81.85 < 盖外圆 81.9; 头顶齐盖顶, 头支承 Z70.08, 下面剩 2 厚)
LID_SCR_L = 8.0                      # M3×8 内六角 DIN912: 支承 70.08 → 尾 62.08, 穿凸块底 2 + 唇剩余 1.9, 唇下 M3 螺母 (63.68–66.08)
LIP_R0, LIP_Z0 = 76.0, LID_Z0 - 5.0      # 唇 r76–82 厚 5, 顶 = 盖底
LIP_ARCS = [(33.0, 147.0), (213.0, 327.0)]
W_R = 79.0
# 配重孔: A 半 (+x) 里的角度, B 半 = +180°。避开: 罩底起子孔 50°/320° (Φ6.5 @ r78.5, 中心距 ≥ 6°), 盖螺丝缺槽 37.5°/307.5° (槽宽 10),
#   x=0 分缝凸耳/螺丝头 (|x| ≥ 10.5), 唇端 33°/327°。6.5° 间距 (r79 弦长 8.96, Φ5.8 沉孔之间剩 3.2)
W_A_A = [56.0, 62.5, 69.0, 75.5, 280.0, 286.5, 293.0, 299.5]
W_A = sorted(set([a % 360 for q in W_A_A + LID_SCR_ALL for a in (q, q + 180)]))
W_CB_D, W_CB_H = 5.8, 3.2                      # 沉孔 Φ5.8 (r76.1–81.9 在唇 r76–82 内; 头 Φ5.5×3 ⇒ 头顶 Z70.88)
W_L, W_NUT_MAX = 16.0, 6                       # M3×16 内六角 (罩顶降到 73.08 后 18 会碰无线托盘), 唇下最多 6 颗 M3 螺母
W_BEAR = LID_Z0 - W_CB_H                       # 67.88 (头顶 70.88 < 盖底 71.08)
W_TIP = W_BEAR - W_L                           # 51.88
assert W_TIP >= 50.5
assert all(min(abs((w - m + 180) % 360 - 180) for m in MNT_A) >= 6.0 for w in W_A), '配重孔离罩底起子孔太近'
RHO_PLA, RHO_ST, RHO_BR = 1.24e-3, 7.85e-3, 8.5e-3


# ---------------- 罩 (整圈, 再切两半) ----------------
def ring_body():
    s = B.ann(R0, R1, Z0, Z1)
    for a0, a1 in LIP_ARCS: s = fuse(s, sector(LIP_R0, R0 + 0.5, LIP_Z0, LID_Z0, a0, a1))
    # (11-16 晚: 罩底内沿取消, 罩壁整圈平底直接坐承载盘顶)
    # 凸台 + 45° 斜撑 (局部 +x 方向建, 再转); 离底板 r3 / 无线托盘都远, 不削
    for a in MNT_A:
        b = fuse(gbox(BOSS_RI, -BOSS_W / 2, Z0, R0 + 0.5, BOSS_W / 2, BOSS_Z1),
                 prism_xz([(BOSS_RI, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 - 0.01), (R0 + 0.5, GUS_Z1 + 0.5)], -BOSS_W / 2, BOSS_W / 2))
        s = fuse(s, xf(b, rotz(a)))
    s = clean(s)
    # ±x 两端竖缝 (天线板)
    s = cut(s, gbox(R0 - 1, -SLOT_Y, Z0 - 1, R1 + 1, SLOT_Y, Z1 + 1), gbox(-R1 - 1, -SLOT_Y, Z0 - 1, -R0 + 1, SLOT_Y, Z1 + 1))
    # 底板 r3 板框 4 个角伸出 r82 (r83 圆弧板框: (±21, 80.4) r83.1 / (40, 72.3) r82.6 / (−51.2, 65) r82.7, 板 Z35–36.51):
    #   罩壁内面局部让位槽 r→83.6 × Z34.7–36.9 (壁局部剩 1.4); 两半同件 ⇒ 转 180° 处也开 (空着无害)
    if BB_RELIEF_A: s = cut(s, *[sector(R0 - 1, BB_RELIEF_R, *BB_RELIEF_Z, a0 + k, a1 + k) for a0, a1 in BB_RELIEF_A for k in (0, 180)])
    for a in MNT_A:
        x, y = pol(HOLE_R, a)
        s = cut(s, cyl(x, y, 3.4, Z0 - 1, BOSS_Z1 + 0.01), cyl(x, y, ACC_D, BOSS_Z1, Z1 + 1))
    for a in W_A:
        x, y = pol(W_R, a)
        if a in LID_SCR_ALL:      # 顶盖螺丝位: 只开 Φ3.4 + 切向缺槽 (盖凸块插进来), 不做配重沉孔
            s = cut(s, cyl(x, y, 3.4, LIP_Z0 - 1, Z1 + 1), xf(gbox(LIP_R0 - 1, -(LID_BOSS_W + 0.4) / 2, LID_Z0 - LID_BOSS_H - 0.1, R0, (LID_BOSS_W + 0.4) / 2, Z1 + 1), rotz(a)))
        else:
            s = cut(s, cyl(x, y, 3.4, LIP_Z0 - 1, Z1 + 1), cyl(x, y, W_CB_D, W_BEAR, Z1 + 1))
    return clean(s)


def half_a(ring):
    s = common(ring, gbox(0, -100, Z0 - 5, 100, 100, Z1 + 5))
    # +y 缝: 螺母侧凸耳 (x 0..7); −y 缝: 螺丝头侧凸耳 (x 0..7)
    for sy in (1, -1):
        y0, y1 = sorted((sy * LUG_Y0, sy * LUG_Y1))
        s = fuse(s, gbox(0, y0, LUG_Z0, LUG_HX, y1, LIP_Z0 + 0.5))
    s = common(s, cyl(0, 0, 2 * R1, Z0 - 1, Z1 + 1))          # 凸耳外端不出罩壁外圆
    for sy in (1, -1):
        for z in LUG_SZ:
            s = cut(s, xcyl(sy * LUG_SY, z, 3.4, -1, LUG_HX + 1))
            if sy > 0: s = cut(s, hexprism_x(LUG_SY, z, NUT_AF, LUG_HX - NUT_DEPTH, LUG_HX + 1))
    return clean(s)


ring = ring_body()
shr_a = half_a(ring)
shr_b = clean(xf(shr_a, rotz(180)))
HALVES = dict(a=shr_a, b=shr_b)

# ---------------- 外购件 ----------------
def sock_z(x, y, z_bear, L):          # 内六角 M3, 头在上 (Φ5.5×3), 杆向下
    return fuse(cyl(x, y, 5.5, z_bear, z_bear + 3.0), cyl(x, y, 3.0, z_bear - L, z_bear + 0.01))
def sock_x(y, z, x_bear, L, sx):      # 头在 x_bear 的 sx 侧, 杆朝 −sx
    h = xcyl(y, z, 5.5, *sorted((x_bear, x_bear + sx * 3.0)))
    sh = xcyl(y, z, 3.0, *sorted((x_bear + sx * 0.01, x_bear - sx * L)))
    return fuse(h, sh)

FAST = {}   # 名 → list of shapes
def hexnut_z(a, r, z0, z1, af=NUT_AF - 0.02):
    """M3 螺母 (对边 af) 在 (r, a) 处, 一条平边朝外贴罩壁 (罩壁兼防转)"""
    rc = af / math.sqrt(3); pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        t = math.radians(30 + 60 * k); pg.Add(gp_Pnt(r + rc * math.cos(t), rc * math.sin(t), z0))
    pg.Close()
    h = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()
    return xf(cut(h, cyl(r, 0, 3.0, z0 - 1, z1 + 1)), rotz(a))

FAST['M3×8 内六角 (罩底→承载盘顶)'] = [sock_z(*pol(HOLE_R, a), BOSS_Z1, MNT_L) for a in MNT_A]
FAST['M3×4 铜螺母 Φ4.0 (承载盘顶孔)'] = [cut(cyl(*pol(HOLE_R, a), 4.0, *INS_Z), cyl(*pol(HOLE_R, a), 3.0, 0, 40)) for a in MNT_A]
seam_scr, seam_nut = [], []
for sy in (1, -1):
    sx_head = -1 if sy > 0 else 1          # +y 缝头在 −x (B), −y 缝头在 +x (A)
    for z in LUG_SZ:
        seam_scr.append(sock_x(sy * LUG_SY, z, sx_head * LUG_HX, SEAM_L, sx_head))
        xn1 = -sx_head * LUG_HX - (-sx_head) * 0.1
        xn0 = xn1 - (-sx_head) * NUT_T
        seam_nut.append(cut(hexprism_x(sy * LUG_SY, z, NUT_AF - 0.02, *sorted((xn0, xn1))), xcyl(sy * LUG_SY, z, 3.0, -20, 20)))
FAST['M3×14 内六角 (分缝切向)'] = seam_scr
FAST['M3 螺母 (分缝)'] = seam_nut
w_scr = [sock_z(*pol(W_R, a), W_BEAR, W_L) for a in W_A if a not in LID_SCR_ALL]   # 盖螺丝占的 4 个孔不放配重螺丝 (唇下照样能挂螺母)
w_stack = [hexnut_z(a, W_R, LIP_Z0 - W_NUT_MAX * NUT_T, LIP_Z0 - 0.01) for a in W_A if a not in LID_SCR_ALL]   # 满载 6 颗 M3 螺母 (平边朝罩壁: r79+2.75 = 81.75 < 82)
FAST['M3×16 内六角 (配重)'] = w_scr
FAST['配重 M3 螺母 满载包络 6×2.4'] = w_stack

# 质量 (钢): 实际单件
def m_sock(L): return RHO_ST * (math.pi * 2.75**2 * 3.0 - 2.5**2 * math.sqrt(3) / 2 * 1.5 + math.pi * 1.5**2 * L)
M_NUT = RHO_ST * (NUT_AF**2 * math.sqrt(3) / 2 - math.pi * 1.6**2) * NUT_T
M_WASH = RHO_ST * math.pi * (3.5**2 - 1.6**2) * 0.5


# ---------------- 其它件 ----------------
VB = V.make(B)
Y_LED = 2.3 + 1.468
led_a = xf(VB['led'], tr(0, Y_LED, 0)); led_b = xf(led_a, rotz(180))
j3_a = gbox(54.85, Y_LED, 38.0, 63.55, 26.0, 48.0); j3_b = xf(j3_a, rotz(180))   # J3 VH 座 + 插头包络


# ---------------- 顶盖 (+y 片; −y 片 = 转 180°) ----------------
def lid_boss(a):   # 切到盖外圆 r81.9 以内 (方块角不伸进罩壁)
    return common(xf(gbox(LID_BOSS_RAD[0], -LID_BOSS_W / 2, LID_Z0 - LID_BOSS_H, LID_BOSS_RAD[1] + 1, LID_BOSS_W / 2, LID_Z0 + 0.01), rotz(a)),
                  cyl(0, 0, 2 * LID_R, LID_Z0 - LID_BOSS_H - 1, LID_Z0 + 0.02))


def lid_hole(x, y):
    """Φ3.4 通 + 顶面平底沉孔 Φ5.7 深 3"""
    return fuse(cyl(x, y, 3.4, LID_Z0 - LID_BOSS_H - 1, Z1 + 1), cyl(x, y, LID_CB_D, Z1 - LID_CB_H, Z1 + 1))


def lid_a_make():
    s = common(cyl(0, 0, 2 * LID_R, LID_Z0, Z1), gbox(-100, LID_Y0, LID_Z0 - 1, 100, 100, Z1 + 1))
    x0, y0, x1, y1, t = BR_POCKET
    s = cut(s, gbox(x0, y0, LID_Z0 - 1, x1, y1, Z1 - t))                                # 桥板顶让位
    nx, ny = ANT_NOTCH
    s = cut(s, gbox(nx, -1, LID_Z0 - 1, 100, ny, Z1 + 1), gbox(-100, -1, LID_Z0 - 1, -nx, ny, Z1 + 1))   # 天线板缺口
    # 灯板 LED 面上伸进盖高度 (Z71.08–73.08, 带 0.4 余量) 的器件: 按包围盒 +0.4 让开
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    e = TopExp_Explorer(led_a, TopAbs_SOLID); cuts = []
    while e.More():
        b = bbox(e.Current())
        if b[5] > LID_Z0 - 0.4 and b[2] < Z1 + 0.4 and b[4] > LID_Y0 - 0.4:
            cuts.append(gbox(b[0] - 0.4, b[1] - 0.4, LID_Z0 - 1, b[3] + 0.4, b[4] + 0.4, Z1 + 1))
        e.Next()
    if cuts: s = cut(s, *cuts)
    s = fuse(s, *[lid_boss(a) for a in LID_SCR_A])
    s = cut(s, *[lid_hole(*pol(W_R, a)) for a in LID_SCR_A])
    return clean(s), len(cuts)


lid_a, LID_LED_CUTS = lid_a_make()
lid_b = clean(xf(lid_a, rotz(180)))
LIDS = dict(a=lid_a, b=lid_b)
# 盖螺丝: M3×8 内六角, 头顶 = 盖顶 Z1 (支承 Z1−3), 唇下 M3 螺母
FAST['M3×8 内六角 (顶盖)'] = [sock_z(*pol(W_R, a), Z1 - LID_CB_H, LID_SCR_L) for a in LID_SCR_ALL]
FAST['M3 螺母 (顶盖, 唇下)'] = [hexnut_z(a, W_R, LIP_Z0 - NUT_T, LIP_Z0 - 0.01) for a in LID_SCR_ALL]
assert Z1 - LID_CB_H - LID_SCR_L < LIP_Z0 - NUT_T, '盖螺丝够不到唇下螺母'
BB_DIR = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/review/结构交付')
bb_r2 = xf(read_step(BB_DIR / 'POV3D_V2_BaseBoard_r3.step'), tr(0, 0, B.Z_BB0))   # 11-16 晚 r3 rev b (变量名沿用)
WH = B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_v1_2.step'
wh = read_step(WH) if WH.exists() else gbox(-24.5, -75.5, 32, 24.5, -45, 50)

OTHERS = dict(rim=B.rim, hub=B.hub, shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube,
              baseboard_r2=bb_r2, wireless_holder=wh, led_a=led_a, led_b=led_b, j3_a=j3_a, j3_b=j3_b)


def report():
    rep = dict(interf={}, fasteners={}, access={}, sweep={}, mass={}, balance={}, screws={}, misc={})
    for k, s in HALVES.items():
        for o, so in OTHERS.items():
            rep['interf'][f'{k} × {o}'] = round(common_v(s, so), 4)
    rep['interf']['a × b'] = round(common_v(shr_a, shr_b), 4)
    for k, s in LIDS.items():
        for o, so in list(OTHERS.items()) + list(HALVES.items()):
            rep['interf'][f'盖{k} × {o}'] = round(common_v(s, so), 4)
    rep['interf']['盖a × 盖b'] = round(common_v(lid_a, lid_b), 4)
    allf = {n: comp(v) for n, v in FAST.items()}
    for n, c in allf.items():
        for k, s in list(HALVES.items()) + [('盖' + k, s) for k, s in LIDS.items()]:
            rep['fasteners'][f'{n} × 罩{k}'] = round(common_v(c, s), 4)
        for o in ('rim', 'hub', 'shroud_lo', 'shroud_hi', 'baseboard_r2', 'wireless_holder', 'led_a', 'led_b', 'j3_a', 'j3_b'):
            v = common_v(c, OTHERS[o])
            if abs(v) > 1e-4 or o in ('rim', 'hub', 'wireless_holder', 'baseboard_r2'): rep['fasteners'][f'{n} × {o}'] = round(v, 4)
    names = list(allf)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = common_v(allf[names[i]], allf[names[j]])
            if v > 1e-4: rep['fasteners'][f'{names[i]} × {names[j]}'] = round(v, 4)
    # 起子通道: 罩底螺丝头顶 Z39 → 罩顶上方, Φ6 竖直 (顶盖最后装, 拆罩先拆盖)
    for a in MNT_A:
        x, y = pol(HOLE_R, a); ch = cyl(x, y, 6.0, BOSS_Z1 + 3.05, Z1 + 10)
        rep['access'][f'{a}° 起子 Φ6 通道'] = round(sum(common_v(ch, s) for s in list(HALVES.values()) + [comp(w_scr + w_stack + seam_scr)]), 4)   # 顶盖最后装, 不算
    # 转动外径 vs 静止内壁
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.05):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot = [shr_a, shr_b, lid_a, lid_b] + [s for v in FAST.values() for s in v]
    R = [rz(s) for s in rot]
    r_rot = np.concatenate([r for r, z in R]); z_rot = np.concatenate([z for r, z in R])
    st = {k: rz(s, 0.05) for k, s in dict(shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube).items()}
    rows = []
    for z0 in np.arange(20, 80, 1.0):
        m = (z_rot >= z0) & (z_rot < z0 + 1)
        if not m.any(): continue
        rmax = r_rot[m].max()
        cand = [r[(z >= z0 - 0.5) & (z < z0 + 1.5) & (r > rmax - 0.01)].min() for r, z in st.values()
                if ((z >= z0 - 0.5) & (z < z0 + 1.5) & (r > rmax - 0.01)).any()]
        rmin = min(cand + [999])
        rows.append((float(z0), round(float(rmax), 2), round(float(rmin), 2), round(float(rmin - rmax), 2)))
    rep['sweep']['rows_z_rmax_rstatic_gap'] = rows
    rep['sweep']['min_gap'] = min(rows, key=lambda r: r[3])
    rep['sweep']['rot_zmax'] = round(float(z_rot.max()), 3)
    # 质量
    for k, s in HALVES.items():
        m, c = cog(s)
        rep['mass'][f'罩{k}'] = dict(vol_mm3=round(m, 1), g_PLA=round(m * RHO_PLA, 1), g_PETG=round(m * 1.27e-3, 1), cog=[round(v, 2) for v in c])
    for k, s in LIDS.items():
        m, c = cog(s)
        rep['mass'][f'盖{k}'] = dict(vol_mm3=round(m, 1), g_PLA=round(m * RHO_PLA, 1), g_PETG=round(m * 1.27e-3, 1), cog=[round(v, 2) for v in c])
    rep['mass']['钢件单重_g'] = {'M3×8 内六角': round(m_sock(8), 3), 'M3×14 内六角': round(m_sock(14), 3), 'M3×16 内六角': round(m_sock(16), 3), 'M3 螺母': round(M_NUT, 3), 'M3 平垫 7×0.5': round(M_WASH, 3)}
    # 配重唇可调范围
    m_min = m_sock(W_L) + M_NUT                 # 螺丝 + 1 颗锁紧螺母
    m_max = m_sock(W_L) + W_NUT_MAX * M_NUT
    neg = [a for a in W_A if a > 180 and a not in LID_SCR_ALL]   # 盖螺丝孔不算 (只挂 1 颗螺母)
    proj = sum(-math.sin(math.radians(a)) for a in neg)
    dU = (m_max - m_min) * W_R * proj
    rep['balance'] = dict(
        holes=len(W_A), angles=W_A, lid_screw_angles=LID_SCR_ALL, r=W_R, per_side=len(neg),
        per_hole_g=dict(empty=0, min_screw_1nut=round(m_min, 2), max_screw_6nut=round(m_max, 2)),
        per_side_proj_sum=round(proj, 3),
        per_side_U_max_gmm=dict(from_empty=round(m_max * W_R * proj, 0), from_min_loaded=round(dU, 0)),
        per_side_eq_g_at_r83=dict(from_empty=round(m_max * W_R * proj / 83, 1), from_min_loaded=round(dU / 83, 1)),
        step_gmm=dict(one_nut=round(M_NUT * W_R, 1), one_washer=round(M_WASH * W_R, 1)),
        shroud_U_gmm=[round(sum(cog(s)[0] * cog(s)[1][i] for s in HALVES.values()) * RHO_PLA, 2) for i in (0, 1)],
        note=f'两半是同一件转 180°, 罩自身不偏心; 配重 −y / +y 两侧各 {len(neg)} 孔 (+ 2 个盖螺丝孔), 任意方向可调; 唇宽 6 放不下 Φ7 垫片, 只挂螺母')
    rep['screws'] = {
        '罩底 M3×8': dict(bear_z=BOSS_Z1, tip_z=BOSS_Z1 - MNT_L, through='凸台 4', insert_z=INS_Z, at=MNT_A, r=HOLE_R,
                          engage=round(INS_Z[1] - max(INS_Z[0], BOSS_Z1 - MNT_L), 2),
                          note='承载盘顶面 Φ4.2×4.0 孔 (B.SHR_HOLES) 里 M3×4 铜螺母 Z28–32; 尾端 Z28 = 孔底'),
        '分缝 M3×14': dict(head_x='∓10..∓7', nut_x='4.5..6.9 (槽 4.5..7, 口朝罩内)', engage=NUT_T, tip='与螺母外面齐'),
        '顶盖 M3×8 内六角': dict(bear_z=Z1 - LID_CB_H, head_top=Z1, tip_z=Z1 - LID_CB_H - LID_SCR_L, nut_z=(LIP_Z0 - NUT_T, LIP_Z0), at=LID_SCR_ALL, r=W_R, through='凸块底 2 + 唇缺槽下剩 1.9'),
        '配重 M3×16': dict(bear_z=W_BEAR, head_top=W_BEAR + 3, tip_z=W_TIP, below_lip=round(LIP_Z0 - W_TIP, 1), max_nuts=W_NUT_MAX),
    }
    rep['valid'] = {k: BRepCheck_Analyzer(v).IsValid() for k, v in list(HALVES.items()) + [('盖' + k, v) for k, v in LIDS.items()]}
    rep['misc'] = dict(Z0=Z0, Z1=Z1, R=(R0, R1), static_in=ST_IN, Z_VIEW0=B.Z_VIEW0, Z_LED0=B.Z_LED0,
                       lip=dict(r=(LIP_R0, R0), z=(LIP_Z0, LID_Z0), arcs=LIP_ARCS), lid=dict(t=LID_T, z=(LID_Z0, Z1), y0=LID_Y0, r=LID_R, br_pocket=BR_POCKET, ant_notch=ANT_NOTCH, led_cuts=LID_LED_CUTS, screws=LID_SCR_ALL, boss_rad=LID_BOSS_RAD, bbox_a=[round(v, 2) for v in bbox(lid_a)]),
                       slot_y=SLOT_Y, boss=dict(a=MNT_A, r=HOLE_R, ri=BOSS_RI, w=BOSS_W, z1=BOSS_Z1, gusset_z1=GUS_Z1),
                       lug=dict(x=LUG_HX, y=(LUG_Y0, LUG_Y1), z=(LUG_Z0, LIP_Z0), screw_z=LUG_SZ),
                       wireless_holder=str(WH) if WH.exists() else '占位盒', bbox_a=[round(v, 2) for v in bbox(shr_a)])
    return rep


if __name__ == '__main__':
    NAMES = dict(a='rotor_shroud_a_v1_2', b='rotor_shroud_b_v1_2'); COL = dict(a='#6FA8DC', b='#93C47D')
    # 打印姿态: 绕 X 转 180° (倒放), 罩顶 Z73.08 / 配重唇顶面落床; 分缝面 x=0 竖直
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    for k, s in HALVES.items():
        d = B.V12 / 'models' / NAMES[k]; d.mkdir(exist_ok=True)
        write_doc([(NAMES[k], s, COL[k], None, False)], d / f'{NAMES[k]}.step', NAMES[k])
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(d / f'{NAMES[k]}.stl'))
        t = xf(s, fx); bb = bbox(t); t = xf(t, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAMES[k]}.stl'))
    # 顶盖: 打印 顶面朝下 (沉头锥口在床面), 免支撑 (桥板让位槽在上面)
    for k, s in LIDS.items():
        n = f'rotor_lid_{k}_v1_2' if k == 'b' else 'rotor_lid_v1_2'
        if k == 'b': continue                                    # 同件, 只出一个
        d = B.V12 / 'models' / n; d.mkdir(exist_ok=True)
        write_doc([(n, s, '#CFE2F3', None, False)], d / f'{n}.step', n)
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(d / f'{n}.stl'))
        t = xf(s, fx); bb = bbox(t); t = xf(t, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{n}.stl'))
    items = [(NAMES[k], s, COL[k], None, False) for k, s in HALVES.items()] + [(f'rotor_lid_{k}', s, '#CFE2F3', None, False) for k, s in LIDS.items()]
    for n, v in FAST.items():
        items += [(f'{n} {i}', s, '#888888' if '包络' not in n else '#E69138', None, False) for i, s in enumerate(v)]
    write_doc(items, OUT / 'rotor_shroud_装配位.step', 'rotor_shroud_asm')
    rep = report()
    json.dump(rep, open(OUT / 'rotor_shroud_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rep.items() if k != 'sweep'}, indent=1, ensure_ascii=False))
    print('sweep min', rep['sweep']['min_gap'], 'zmax', rep['sweep']['rot_zmax'])
