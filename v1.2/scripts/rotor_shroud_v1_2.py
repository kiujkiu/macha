# -*- coding: utf-8 -*-
"""V1.2 转子罩 (11-16, 方案见 v1.2/concept/shroud_balance_concept.png; 高度按 11-16 新布局: 灯板下沿 Z37 / LED 下沿 Z74.88)。
    cd v1.2/scripts && ../../.venv/bin/python rotor_shroud_v1_2.py
世界坐标同 build_v1_2: 承载盘顶 Z32, 不转玻璃座内卡内壁 r90.8 (顶 Z73.08)。
结构:
  - 罩壁 r86–89, Z32–72.5 (顶开口; 外面一整圈光滑, 只有 x=0 两条分缝), 两半 A (+x) / B (−x); B = A 绕 Z 转 180° (同一个件, 打 2 个)。
  - 罩底 4 个凸台 (67.5/112.5/247.5/292.5° @ r82.5) 压承载盘顶 Z32: M3×14 内六角从上往下, 穿承载盘 + 毂盘进毂盘底 M3 铜螺母;
    凸台上面 45° 斜撑接罩壁, 斜撑里 Φ6.5 竖孔让螺丝头/起子 (起子从罩顶开口竖直进, 穿配重唇 Φ6.5 让位孔)。凸台在 |y|<72.3 削平 (让底板 r2 板边 y72)。
  - 分缝 (x=0, ±y) 内侧凸耳 x±7 × r77.5–罩壁 × Z51–67.5 (上接配重唇), 2 颗切向 M3×14 (Z55 / Z63.5), 一侧螺丝头, 另一侧六角螺母槽 (槽口朝罩内, 螺母从内侧推进)。
    +y 缝: 头在 B 侧 (x<0), 螺母在 A 侧; −y 缝相反 (180° 对称)。凸耳底 Z51 > 无线模块固定件顶 Z50。
  - 配重唇 r78–86, Z67.5–72.5, 33°–147° / 213°–327° (让开 ±x 灯板两端/支撑/天线); 24 个 M3 孔 @ r82 (每侧 12 个, 7.5° 左右间距),
    顶面 Φ6 沉孔深 3.2 (M3×18 内六角头顶 Z72.3 < 罩顶 72.5); 唇下挂 M3 螺母/垫片 (最多 6 颗螺母, 尾端 Z51.3 > 模块固定件顶 Z50)。
  - 罩底内沿 r83.5–86 Z32–34.5 + 45° 斜面 (33°–70.9° / 109.1°–147° 及对侧, 让开 ±y |x|≤27.5 的无线模块固定件 r84.5)。
打印: 倒放 (罩顶 Z72.5 + 配重唇顶面落床), 免支撑 (凸台/凸耳/内沿全部 45° 或从唇上长出; 只有 Φ6.5 / Φ6 孔顶小搭桥)。
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
Z1 = 72.5                           # 罩顶 (内卡顶 Z_VIEW0 73.08 下 0.58; LED 下沿 74.88)
R0, R1 = 86.0, 89.0                 # 罩壁 (离静止内壁 r90.8 留 1.8)
ST_IN = B.SPIG_IN                   # 90.8
assert Z1 <= B.Z_VIEW0 - 0.5 and Z1 < B.Z_LED0
# 底部固定 (4 孔)
HOLE_R = 82.5
MNT_A = [67.5, 112.5, 247.5, 292.5]
BOSS_W, BOSS_RI, BOSS_Z1 = 8.0, 78.5, 36.0     # 凸台 宽 8 (切向) × r78.5–罩壁 × Z32–36
GUS_Z1 = BOSS_Z1 + (R0 - BOSS_RI)              # 45° 斜撑顶 (贴壁处) Z44
ACC_D = 6.5                                    # 螺丝头 / 起子让位孔
BB_EDGE = 72.0 + 0.3                           # 底板 r2 板边 y=72 (+0.3)
WH_EDGE = 26.5 + 0.5                           # 无线模块固定件外墙 |x|≤26.5 (+0.5); 180° 对称 ⇒ 4 个凸台都削
MNT_L = 14.0                                   # M3×14: 头支承 Z36 ⇒ 尾 Z22.0 (毂盘底 Z21.5 上 0.5)
INS_Z = (22.0, 26.0)                           # 毂盘底 Φ4.2 盲孔 Z21.5–26.0 (探测); M3×4 铜螺母顶到孔顶 ⇒ Z22.0–26.0
# 分缝凸耳
LUG_HX, LUG_Y0, LUG_Y1 = 7.0, 77.5, 87.0       # x 0..±7, |y| 77.5..87 (外端埋进罩壁)
LUG_Z0 = 51.0                                  # > 无线模块固定件顶 Z50
LUG_SY, LUG_SZ = 82.0, (55.0, 63.5)            # 切向螺丝轴线 |y|=82, Z55 / Z63.5
NUT_AF, NUT_T, NUT_DEPTH = 5.5, 2.4, 2.5       # M3 螺母; 槽 x 4.5..7 (口朝罩内)
SEAM_L = 14.0                                  # M3×14: 头支承 x=∓7 ⇒ 尾 ±7 (与螺母外面齐)
# 配重唇
LIP_R0, LIP_Z0 = 78.0, 67.5
LIP_ARCS = [(33.0, 147.0), (213.0, 327.0)]
W_R = 82.0
_Q = [37.5, 45.0, 52.5, 60.0, 74.5, 80.0]      # 第一象限; 镜像到四个象限 (让开 67.5/112.5 起子孔与 x=0 分缝凸耳/螺丝头)
W_A = sorted(set([a for q in _Q for a in (q, 180 - q, 180 + q, 360 - q)]))
W_CB_D, W_CB_H = 6.0, 3.2                      # 沉孔 (头 Φ5.5×3 ⇒ 头顶 Z72.3)
W_L, W_NUT_MAX = 18.0, 6                       # M3×18 内六角, 唇下最多 6 颗 M3 螺母
W_BEAR = Z1 - W_CB_H                           # 69.3
W_TIP = W_BEAR - W_L                           # 51.3
assert W_TIP >= 50.5
# 罩底内沿 (承载盘顶压一圈)
LEDGE_R0, LEDGE_Z1 = 83.5, 34.5
HOLDER_X = 27.5                                # 无线模块固定件 |x|≤26.5 (+1)
_la = math.degrees(math.acos(HOLDER_X / 84.0))  # 70.9°
LEDGE_ARCS = [(33.0, _la), (180 - _la, 147.0), (180 + 33.0, 180 + _la), (360 - _la, 327.0)]
RHO_PLA, RHO_ST, RHO_BR = 1.24e-3, 7.85e-3, 8.5e-3


# ---------------- 罩 (整圈, 再切两半) ----------------
def ring_body():
    s = B.ann(R0, R1, Z0, Z1)
    for a0, a1 in LIP_ARCS: s = fuse(s, sector(LIP_R0, R0 + 0.5, LIP_Z0, Z1, a0, a1))
    # 内沿: r83.5–86 Z32–34.5 + 45° 斜面到 (r86, Z37)
    lr = fuse(B.ann(LEDGE_R0, R0 + 0.5, Z0, LEDGE_Z1),
              cut(cyl(0, 0, 2 * (R0 + 0.5), LEDGE_Z1, LEDGE_Z1 + R0 - LEDGE_R0),
                  BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(0, 0, LEDGE_Z1), gp_Dir(0, 0, 1)), LEDGE_R0, R0, R0 - LEDGE_R0).Shape()))
    for a0, a1 in LEDGE_ARCS: s = fuse(s, common(lr, cyl(0, 0, 2 * R1 + 2, Z0 - 1, Z1, ang=a1 - a0, a0=a0)))
    # 凸台 + 45° 斜撑 (局部 +x 方向建, 再转)
    for a in MNT_A:
        b = fuse(gbox(BOSS_RI, -BOSS_W / 2, Z0, R0 + 0.5, BOSS_W / 2, BOSS_Z1),
                 prism_xz([(BOSS_RI, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 - 0.01), (R0 + 0.5, GUS_Z1 + 0.5)], -BOSS_W / 2, BOSS_W / 2))
        b = xf(b, rotz(a))
        b = cut(b, gbox(-200, -BB_EDGE, Z0 - 1, 200, BB_EDGE, 80), gbox(-WH_EDGE, -200, Z0 - 1, WH_EDGE, 200, 80))   # |y|<72.3 (底板板边) / |x|<27 (模块固定件) 削掉
        s = fuse(s, b)
    s = clean(s)
    for a in MNT_A:
        x, y = pol(HOLE_R, a)
        s = cut(s, cyl(x, y, 3.4, Z0 - 1, BOSS_Z1 + 0.01), cyl(x, y, ACC_D, BOSS_Z1, Z1 + 1))
    for a in W_A:
        x, y = pol(W_R, a)
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
FAST['M3×14 内六角 (罩底→毂盘)'] = [sock_z(*pol(HOLE_R, a), BOSS_Z1, MNT_L) for a in MNT_A]
FAST['M3×4 铜螺母 Φ4.0 (毂盘底孔)'] = [cut(cyl(*pol(HOLE_R, a), 4.0, *INS_Z), cyl(*pol(HOLE_R, a), 3.0, 0, 40)) for a in MNT_A]
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
w_scr = [sock_z(*pol(W_R, a), W_BEAR, W_L) for a in W_A]
w_stack = [cut(cyl(*pol(W_R, a), 7.0, LIP_Z0 - W_NUT_MAX * NUT_T, LIP_Z0), cyl(*pol(W_R, a), 3.0, 0, 90)) for a in W_A]   # 满载包络 Φ7 (垫片外径/螺母外接圆 6.35)
FAST['M3×18 内六角 (配重)'] = w_scr
FAST['配重 M3 螺母/垫片 满载包络 Φ7×14.4'] = w_stack

# 质量 (钢): 实际单件
def m_sock(L): return RHO_ST * (math.pi * 2.75**2 * 3.0 - 2.5**2 * math.sqrt(3) / 2 * 1.5 + math.pi * 1.5**2 * L)
M_NUT = RHO_ST * (NUT_AF**2 * math.sqrt(3) / 2 - math.pi * 1.6**2) * NUT_T
M_WASH = RHO_ST * math.pi * (3.5**2 - 1.6**2) * 0.5


# ---------------- 其它件 ----------------
VB = V.make(B)
Y_LED = 2.3 + 1.468
led_a = xf(VB['led'], tr(0, Y_LED, 0)); led_b = xf(led_a, rotz(180))
j3_a = gbox(54.85, Y_LED, 38.0, 63.55, 26.0, 48.0); j3_b = xf(j3_a, rotz(180))   # J3 VH 座 + 插头包络
BB_DIR = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/review/结构交付')
bb_r2 = xf(read_step(BB_DIR / 'POV3D_V2_BaseBoard_r2.step'), tr(0, 0, B.Z_BB0))
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
    allf = {n: comp(v) for n, v in FAST.items()}
    for n, c in allf.items():
        for k, s in HALVES.items():
            rep['fasteners'][f'{n} × 罩{k}'] = round(common_v(c, s), 4)
        for o in ('rim', 'hub', 'shroud_lo', 'shroud_hi', 'baseboard_r2', 'wireless_holder', 'led_a', 'led_b', 'j3_a', 'j3_b'):
            v = common_v(c, OTHERS[o])
            if abs(v) > 1e-4 or o in ('rim', 'hub', 'wireless_holder', 'baseboard_r2'): rep['fasteners'][f'{n} × {o}'] = round(v, 4)
    names = list(allf)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = common_v(allf[names[i]], allf[names[j]])
            if v > 1e-4: rep['fasteners'][f'{names[i]} × {names[j]}'] = round(v, 4)
    # 起子通道: 罩底螺丝头顶 Z39 → 罩顶上方, Φ6 竖直
    for a in MNT_A:
        x, y = pol(HOLE_R, a); ch = cyl(x, y, 6.0, BOSS_Z1 + 3.05, Z1 + 10)
        rep['access'][f'{a}° 起子 Φ6 通道'] = round(sum(common_v(ch, s) for s in list(HALVES.values()) + [comp(w_scr + w_stack + seam_scr)]), 4)
    # 转动外径 vs 静止内壁
    import numpy as np
    from mf3_v1_2 import mesh
    def rz(shape, defl=0.05):
        Vv, T = mesh(shape, defl); return np.hypot(Vv[:, 0], Vv[:, 1]), Vv[:, 2]
    rot = [shr_a, shr_b] + [s for v in FAST.values() for s in v]
    R = [rz(s) for s in rot]
    r_rot = np.concatenate([r for r, z in R]); z_rot = np.concatenate([z for r, z in R])
    st = {k: rz(s, 0.05) for k, s in dict(shroud_lo=B.shroud_lo, shroud_hi=B.shroud_hi, glass=B.tube).items()}
    rows = []
    for z0 in np.arange(20, 74, 1.0):
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
    rep['mass']['钢件单重_g'] = {'M3×14 内六角': round(m_sock(14), 3), 'M3×18 内六角': round(m_sock(18), 3), 'M3 螺母': round(M_NUT, 3), 'M3 平垫 7×0.5': round(M_WASH, 3)}
    # 配重唇可调范围
    m_min = m_sock(W_L) + M_NUT                 # 螺丝 + 1 颗锁紧螺母
    m_max = m_sock(W_L) + W_NUT_MAX * M_NUT
    neg = [a for a in W_A if a > 180]
    proj = sum(-math.sin(math.radians(a)) for a in neg)
    dU = (m_max - m_min) * W_R * proj
    rep['balance'] = dict(
        holes=len(W_A), angles=W_A, r=W_R, per_side=len(neg),
        per_hole_g=dict(empty=0, min_screw_1nut=round(m_min, 2), max_screw_6nut=round(m_max, 2)),
        per_side_proj_sum=round(proj, 3),
        per_side_U_max_gmm=dict(from_empty=round(m_max * W_R * proj, 0), from_min_loaded=round(dU, 0)),
        per_side_eq_g_at_r83=dict(from_empty=round(m_max * W_R * proj / 83, 1), from_min_loaded=round(dU / 83, 1)),
        step_gmm=dict(one_nut=round(M_NUT * W_R, 1), one_washer=round(M_WASH * W_R, 1)),
        shroud_U_gmm=[round(sum(cog(s)[0] * cog(s)[1][i] for s in HALVES.values()) * RHO_PLA, 2) for i in (0, 1)],
        note='两半是同一件转 180°, 罩自身不偏心; 配重 −y / +y 两侧各 12 孔, 任意方向可调')
    rep['screws'] = {
        '罩底 M3×14': dict(bear_z=BOSS_Z1, tip_z=BOSS_Z1 - MNT_L, through='凸台 4 + 承载盘 5 + 毂盘', insert_z=INS_Z,
                          engage=round(INS_Z[1] - max(INS_Z[0], BOSS_Z1 - MNT_L), 2), hub_bottom=21.5,
                          note='铜螺母若与毂盘底面齐 (Z21.5–25.5) 则啮合 3.5; 尾端 Z22.0 在毂盘底上 0.5'),
        '分缝 M3×14': dict(head_x='∓10..∓7', nut_x='4.5..6.9 (槽 4.5..7, 口朝罩内)', engage=NUT_T, tip='与螺母外面齐'),
        '配重 M3×18': dict(bear_z=W_BEAR, head_top=W_BEAR + 3, tip_z=W_TIP, below_lip=round(LIP_Z0 - W_TIP, 1), max_nuts=W_NUT_MAX),
    }
    rep['valid'] = {k: BRepCheck_Analyzer(v).IsValid() for k, v in HALVES.items()}
    rep['misc'] = dict(Z0=Z0, Z1=Z1, R=(R0, R1), static_in=ST_IN, Z_VIEW0=B.Z_VIEW0, Z_LED0=B.Z_LED0,
                       lip=dict(r=(LIP_R0, R0), z=(LIP_Z0, Z1), arcs=LIP_ARCS), ledge_arcs=[(round(a, 1), round(b, 1)) for a, b in LEDGE_ARCS],
                       lug=dict(x=LUG_HX, y=(LUG_Y0, LUG_Y1), z=(LUG_Z0, LIP_Z0), screw_z=LUG_SZ),
                       wireless_holder=str(WH) if WH.exists() else '占位盒', bbox_a=[round(v, 2) for v in bbox(shr_a)])
    return rep


if __name__ == '__main__':
    NAMES = dict(a='rotor_shroud_a_v1_2', b='rotor_shroud_b_v1_2'); COL = dict(a='#6FA8DC', b='#93C47D')
    # 打印姿态: 绕 X 转 180° (倒放), 罩顶 Z72.5 / 配重唇顶面落床; 分缝面 x=0 竖直
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    for k, s in HALVES.items():
        d = B.V12 / 'models' / NAMES[k]; d.mkdir(exist_ok=True)
        write_doc([(NAMES[k], s, COL[k], None, False)], d / f'{NAMES[k]}.step', NAMES[k])
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(d / f'{NAMES[k]}.stl'))
        t = xf(s, fx); bb = bbox(t); t = xf(t, tr(-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(t, str(B.OUT / '打印STL' / f'{NAMES[k]}.stl'))
    items = [(NAMES[k], s, COL[k], None, False) for k, s in HALVES.items()]
    for n, v in FAST.items():
        items += [(f'{n} {i}', s, '#888888' if '包络' not in n else '#E69138', None, False) for i, s in enumerate(v)]
    write_doc(items, OUT / 'rotor_shroud_装配位.step', 'rotor_shroud_asm')
    rep = report()
    json.dump(rep, open(OUT / 'rotor_shroud_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rep.items() if k != 'sweep'}, indent=1, ensure_ascii=False))
    print('sweep min', rep['sweep']['min_gap'], 'zmax', rep['sweep']['rot_zmax'])
