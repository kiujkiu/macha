# -*- coding: utf-8 -*-
"""转子盘B 转子罩 (11-17 夜, 用户: 罩子 4 片 → 2 片; 锁到屏幕固定件上)。
    cd v1.2/scripts && ../../.venv/bin/python rotor_shroud_b_v1_2.py
由 V1.2 rotor_shroud_v1_2 (罩身 A/B 沿 x=0 分 + 顶盖 ±y 两片) 改:
  - 分法: 沿灯板那条线分成 +y / −y 两半, 每半连自己的顶盖做成一件 (罩身两端竖缝 y −14.46…+5.74 本来就把罩壁断开, 顶盖本来就是 ±y 两片)
  - 原 x=0 分缝凸耳 + 切向螺丝取消 (那条缝没了)
  - (11-21) 罩底 8 个耳朵坐屏幕支撑件 (PETG 打印, rotor_b) 顶 Z LS.Z0 (38.5), 耳厚 4.5: 用户「罩子还是用螺丝向下锁 螺母嵌在这个支撑件上」
    DIN912 M3×12 从耳顶往下, 穿耳 + 支撑件, 拧进支撑件底面倒扣的 M3 法兰螺母 (Z30.5–34.2), 尾 Z31 离承载盘顶 0.5; 罩顶开 Φ7 起子孔 (起子 Φ6)
    A 件 (0/180°) 锁点本地 (61, ±30.5) r68.2 (用户图), 耳 = 本地 x56.5→罩壁 × y26…35 (悬伸 ~18, 整条坐在支撑件上);
    B 件 (90/270°) 锁点 (73, ±19.5) r75.56, 耳 x68.5→壁 × y15…24; 45° 斜撑从锁点外 4.3 起
    外圈 8 颗法兰螺母嵌支撑件顶面 (顶低于件顶 0.3), 罩耳可直接盖过
    (之前 11-20 夜: M3×10 超薄头从屏幕玻纤板底往上 + 耳顶法兰螺母, 耳 Z33.5–37.5; 更早外圈 M3×18 / ±14° —— 均作废)
  - (11-21) 天线槽 25.2° → 9.2° (A 件罩耳压在原位); 竖缝上边 −0.19 → +0.35, 顶盖内边再退 0.2 (罩 ↔ 灯板 0.108 → ≥0.3)
  - 配重孔按新锁点自动避让 (_wa_ok: 与 Φ10 套筒孔中心距 ≥ (10+5.8)/2+1), 候选 = 原 RS.W_A + 40/140/220/320 + 22.5+45k (旧套筒位)
  - (11-20 夜) 天线 FPC 改贴罩内壁 (用户「贴到罩子吧」「罩子天然有这个侧立面」「这个天线是fpc的」): 定位浅槽 38.1×18.9×0.3 @25.2° (+y 半) / 205.2° (−y 半), Z32.68–70.78;
    侧立件天线板取消 ⇒ 两端竖缝从 y −14.79…5.41 收窄到 −9.19…−0.19 (只让灯板 + 夹条端头, 外角 r82.35 进罩壁)
  - (11-20 夜) 用户「罩子桥板让位放到0.3」: 顶盖桥板通槽外边外扩 0.15 (BR_POCKET_ADD), 离桥板 FPC 座 0.19 → ≈0.34
  - 顶盖螺丝 (原 47.5/132.5/227.5/312.5°) 取消, 盖与唇局部填实; 配重孔上方顶盖开 Φ5.8 孔, 配重螺丝从罩顶插
打印: 倒放 (罩顶 Z73.08 落床, 顶盖整面贴床; 原单独顶盖时唇顶低 2 要支撑, 现在没有了)。
"""
import io, contextlib, json, math
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import rotor_b_v1_2 as RB
RS, B, LS = RB.RS, RB.B, RB.LS
from helpers import write_doc
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz, solids = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz, B.solids
common, common_v, sector, pol, prism_xz = RB.common, RB.common_v, RS.sector, RS.pol, RS.prism_xz
Z0, Z1, R0, R1 = RS.Z0, RS.Z1, RS.R0, RS.R1
BOSS_Z0 = RB.SP_Z1                    # 38.5 耳底 = 支撑件顶 (= 灯板下沿 LS.Z0, 跟灯板走)
BOSS_T = RB.SHR_EAR_T                 # 4.5 (按 DIN912 M3×12 尾离承载盘顶 0.5 反推)
BOSS_Z1 = BOSS_Z0 + BOSS_T            # 43.0 螺丝头支承 = 耳顶
# 11-21 罩锁改从上往下 (用户「罩子还是用螺丝向下锁 螺母嵌在这个支撑件上」): 螺母倒扣嵌在支撑件底面, 耳上只有 Φ3.4 过孔 + 起子孔
EAR_HW = 4.5                          # 耳宽 9 (以锁点为中线, 沿支撑件局部 x 方向伸到罩壁)
EAR_IN = 4.5                          # 耳内端在锁点内侧 4.5 (孔边料 2.8)
NUT_T = RB.NUT_T
NUT_D = RB.WELL_FL_D
EAR_X0 = RB.SHR_LOC_X - EAR_IN        # 68.5 (B 件; A 件 56.5) 兼容旧名
EAR_Y0, EAR_Y1 = RB.SHR_LOC_Y - EAR_HW, RB.SHR_LOC_Y + EAR_HW   # B 件 15…24 兼容旧名
BOSS_W = 2 * EAR_HW
BOSS_RI = EAR_X0                      # 兼容旧名 (图纸)
HOLE_R = RB.SHR_LOCK_R                # {'a': 68.2, 'b': 75.56}
MNT_PTS = list(RB.SHR_LOCK_PTS)       # 世界 8 点
MNT_A = list(RB.SHR_LOCK_ANG)         # 26.57/75.04/104.96/153.43/206.57/255.04/284.96/333.43
MNT_L = RB.SHR_SCR_L                  # DIN912 M3×12 从耳顶往下 (支承 Z43 → 尾 Z31)
NUT_Z = RB.LOCK_NUT_Z                 # 30.5–34.2 倒扣在支撑件底
SCR_TIP = RB.SHR_SCR_TIP              # 31.0
ACC_D = 7.0                           # 起子孔 Φ7 (起子/内六角扳手 Φ6 包络 + 0.5/边; DIN912 头 Φ5.5); 与 r<R0 取交, 不切罩壁
assert ACC_D >= 6.0 + 1.0 - 1e-9 and max(HOLE_R.values()) + ACC_D / 2 <= R0 - 0.5
GUSSET_X0 = ACC_D / 2 + 0.8           # 45° 斜撑从锁点外侧 4.3 起 (不挡起子孔)
OUT_PTS = list(RB.ANCHOR_PTS) + list(RB.OUT_NUT_PTS)   # 外圈 8 颗法兰螺母 (嵌在支撑件顶面, 顶低于件顶 0.3, 罩子之前装; 罩耳可盖过)
# 配重孔: 候选 原 RS.W_A + 40/140/220/320, 去掉与起子孔相碰的 (中心距 < (ACC_D+5.8)/2 + 1)
def _wa_ok(a): return all(math.dist(pol(RS.W_R, a), p) >= (ACC_D + RS.W_CB_D) / 2 + 1.0 for p in MNT_PTS)
W_CAND = sorted(set(RS.W_A) | {40.0, 140.0, 220.0, 320.0})
W_A = sorted(a for a in W_CAND if _wa_ok(a))
def acc_cut(x, y, z0, z1):
    """起子孔 Φ ACC_D, 只切到罩壁内面 (r ≤ R0)"""
    return common(cyl(x, y, ACC_D, z0, z1), cyl(0, 0, 2 * R0, z0 - 1, z1 + 1))
W_DROP = [a for a in W_CAND if not _wa_ok(a)]
# 11-20 夜 两端竖缝收窄: 原 y RS.SLOT_Y0…SLOT_Y1 (−14.79…5.41, 让天线板) → 只让灯板 + 夹条端头 (两端 x±81.88 处 y −8.79…−0.59, 外角 r82.35 进罩壁) 各 0.4
SLOT_Y0, SLOT_Y1 = -8.79 - 0.4, 0.0 + 0.35     # −9.19…+0.35 (跨分缝 y=ECC −4.69); 11-21 上边 −0.19 → +0.35: 灯板 A 两端 MIP 顶到 y0.0 (v2_boards 灯板, x80.4–81.88), 原缝边离它 0.12
# 11-20 夜 天线 FPC 18.5×37.7 改贴罩子内壁 (用户「贴到罩子吧」「罩子天然有这个侧立面」「这个天线是fpc的」), 定位浅槽 38.1×18.9×0.3, 长边沿 Z, 槽底 = 圆柱面 r82.3
#   位置 (LS.ANT_B_ANG): 两端 0°/180° 附近罩壁被竖缝 + 罩耳 (板本地 y 15.5…24.5 接壁处 ±17.38°) 夹住只剩弧长 ~15 < 18.9 ⇒ 挪到 罩耳外侧 ~ 唇 (33°) 之间, 中心 25.2° (+y 半) / 205.2° (−y 半)
# 11-21 A 件罩耳 (板本地 y 26…35, 接壁 18.5°…25.3°) 正好压在原天线位 25.2° ± 6.6° ⇒ 天线挪到 竖缝 (≈0°) 与 A 件罩耳之间: 中心 ANT_ANG_NEW
#   ⚠ 天线实体 / 原值在 led_support (LS.ANT_B_ANG = 25.2/205.2) —— 本脚本不改 led_support, 槽按新角度切, 校核用本地重建的天线 (ant_new); 需同步 LS.ANT_B_ANG
ANT_ANG_NEW = 9.2
ANT_ANG = (ANT_ANG_NEW, ANT_ANG_NEW + 180.0)
ANT_HA = math.degrees(LS.ANT_W / 2 / R0)         # 6.60° 半角 (弧长 18.9 @r82)
ANT_Z0, ANT_Z1 = LS.ANT_B_ZC - LS.ANT_L / 2, LS.ANT_B_ZC + LS.ANT_L / 2   # 32.68–70.78 (顶离顶盖底 Z71.08 0.3)
_EAR_A_IN = math.degrees(math.asin((RB.LOCK_A_LOC[0][1] - EAR_HW) / R0))     # A 件 +y 罩耳下边接壁角 18.5°
_SLOT_A = math.degrees(math.atan2(SLOT_Y1, R0))                               # 竖缝上边 (y +0.35) ≈ 0.24°
ANT_MARGIN = dict(ear=round(_EAR_A_IN - (ANT_ANG[0] + ANT_HA), 2),          # 槽边 ↔ A 件罩耳 (度)
                  slot=round((ANT_ANG[0] - ANT_HA) - _SLOT_A, 2))           # 槽边 ↔ 竖缝 (度)
assert min(ANT_MARGIN.values()) > 0.5 and ANT_Z1 <= RS.LID_Z0 - 0.2, ANT_MARGIN
_ha_ant = math.degrees(LS.ANT_SZ[1] / 2 / LS.ANT_B_R)
def _ant_new(a):   # 同 led_support._ant_b, 角度换新
    r1 = LS.ANT_B_R + LS.ANT_REC
    o = cyl(0, 0, 2 * r1, LS.ANT_B_ZC - LS.ANT_SZ[0] / 2, LS.ANT_B_ZC + LS.ANT_SZ[0] / 2, ang=2 * _ha_ant, a0=a - _ha_ant)
    return cut(o, cyl(0, 0, 2 * (r1 - 0.15), LS.ANT_B_ZC - LS.ANT_SZ[0] / 2 - 1, LS.ANT_B_ZC + LS.ANT_SZ[0] / 2 + 1))
ant_new_a, ant_new_b = _ant_new(ANT_ANG[0]), _ant_new(ANT_ANG[1])
# 11-20 夜 用户「罩子桥板让位放到0.3」: 顶盖桥板通槽外边 (RS.BR_POCKET, 叠高 +0.4 ⇒ ECC±11.318) 离桥板 FPC 座 (y 6.44 / −15.82, ECC±11.13) 只 0.19
#   ⇒ 本件槽外边再外扩 BR_POCKET_ADD 0.15 (ECC±11.468, 离座 ≈0.34); 槽半宽 |x|≤38.5 (离桥板 0.5) 不动; RS 原罩不改
BR_POCKET_ADD = 0.15
# 11-21 罩 a ↔ 灯板 A MIP 顶 (x±81.6, Z71–73) 只 0.108: 顶盖内边 (RS.LID_YIN, 板厚按 1.468 算的) 两片各再退 0.2 ⇒ 0.308
LID_YIN_ADD = 0.2
BR_POCKET = {k: (x0, yb + (BR_POCKET_ADD if k == 'a' else -BR_POCKET_ADD)) for k, (x0, yb) in RS.BR_POCKET.items()}   # +6.778 / −16.158
SPLIT_Y = RS.ECC                      # 分界: 灯板中面 y = SCR_ECC (11-18 夜 −4.69, 原 −4.36; 两端竖缝内)
# 11-18 夜 用户: 底板上边 R85 圆弧伸出罩壁 r82–85 ⇒ +y 半罩底开缺口 = 底板板框外扩 BB_NOTCH_CLR, 从罩底到板顶 + BB_NOTCH_CLR (伸出的板被玻璃座挡住, 外面看不到)
BB_NOTCH = False                      # 11-19 用户: 底板回 r4j 矩形 (最远 r76.78 < 罩内壁 r82), 不再开缺口; 要恢复 R85 圆弧时改 True
BB_NOTCH_CLR = 0.5
BB_NOTCH_Z1 = B.Z_BB0 + B.BB_T + BB_NOTCH_CLR   # 37.1


def bb_notch():
    from shapely.geometry import Polygon as _P
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    poly = _P(RB.V.BB_POLY).buffer(BB_NOTCH_CLR, join_style=2)
    pg = BRepBuilderAPI_MakePolygon()
    for x, y in list(poly.exterior.coords)[:-1]: pg.Add(gp_Pnt(x, y, Z0 - 1))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, BB_NOTCH_Z1 - (Z0 - 1))).Shape()


def ring_body_b():
    s = B.ann(R0, R1, Z0, Z1)
    for a0, a1 in RS.LIP_ARCS: s = fuse(s, sector(RS.LIP_R0, R0 + 0.5, RS.LIP_Z0, RS.LID_Z0, a0, a1))
    clip = cyl(0, 0, 2 * (R0 + 0.5), BOSS_Z0 - 1, Z1 + 1)
    for a in RB.SP_ANG:               # 耳坐支撑件顶 (局部沿 x 的长条: 锁点内侧 EAR_IN → 罩壁, 宽 9, 耳顶平) + 45° 斜撑 (从锁点外 GUSSET_X0 起) 接罩壁
        for lx, ly in RB.SHR_LOCK_SET[a]:
            y0, y1 = ly - EAR_HW, ly + EAR_HW
            b = fuse(gbox(lx - EAR_IN, y0, BOSS_Z0, R0 + 0.5, y1, BOSS_Z1),
                     prism_xz([(lx + GUSSET_X0, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 + (R0 + 0.5 - lx - GUSSET_X0))], y0, y1))
            s = fuse(s, xf(common(b, clip), rotz(a)) if a else common(b, clip))
    s = clean(s)
    for x, y in MNT_PTS:
        s = cut(s, cyl(x, y, 3.4, BOSS_Z0 - 1, BOSS_Z1 + 0.01), acc_cut(x, y, BOSS_Z1, Z1 + 1))
    for a in W_A:                     # 配重孔 (原顶盖螺丝位也改成配重孔; 11-20 按新锁点增删)
        x, y = pol(RS.W_R, a)
        s = cut(s, cyl(x, y, 3.4, RS.LIP_Z0 - 1, Z1 + 1), cyl(x, y, RS.W_CB_D, RS.W_BEAR, Z1 + 1))
    for sx in (1, -1):                # 两端竖缝 (11-20 夜 天线板取消, 缝收窄到只让灯板/夹条端头)
        x0, x1 = (RS.SLOT_X0, R1 + 1) if sx > 0 else (-R1 - 1, -RS.SLOT_X0)
        s = cut(s, gbox(x0, SLOT_Y0, Z0 - 1, x1, SLOT_Y1, Z1 + 1))
    for a in ANT_ANG:                 # 天线 FPC 定位浅槽 (罩内壁 r82 → r82.3, 弧长 ANT_W × 高 ANT_L, 槽底仍是圆柱面)
        s = cut(s, sector(R0 - 0.2, R0 + LS.ANT_REC, ANT_Z0, ANT_Z1, a - ANT_HA, a + ANT_HA))
    return clean(s)


def lid_plain(k):
    """原顶盖去掉螺丝凸块/沉孔: 取原盖 Z≥LID_Z0 的板, 再把螺丝位的 Φ3.4/Φ5.7 孔补实"""
    lid = RS.lid_a if k == 'a' else RS.lid_b
    plate = common(lid, gbox(-100, -100, RS.LID_Z0, 100, 100, Z1 + 1))
    scr = RS.LID_SCR_A if k == 'a' else [a + 180 for a in RS.LID_SCR_A]
    fill = [common(cyl(*pol(RS.W_R, a), 7.0, RS.LID_Z0, Z1), cyl(0, 0, 2 * RS.LID_R, RS.LID_Z0 - 1, Z1 + 1)) for a in scr]
    x0, yb = BR_POCKET[k]; yb0 = RS.BR_POCKET[k][1]   # 桥板让位槽外边外扩 (11-20 夜, 离桥板 ≥0.3)
    yi = RS.LID_YIN[k]                                # 盖内边 (RS 按板厚 1.468 算; 板改 1.6 后离 MIP 顶只剩 0.108) ⇒ 再退 LID_YIN_ADD (11-21, ≥0.3)
    yin_cut = gbox(-100, yi - 1, RS.LID_Z0 - 1, 100, yi + LID_YIN_ADD, Z1 + 1) if k == 'a' else gbox(-100, yi - LID_YIN_ADD, RS.LID_Z0 - 1, 100, yi + 1, Z1 + 1)
    return clean(cut(fuse(plate, *fill), gbox(x0, min(yb, yb0 - 0.01 * (1 if k == 'a' else -1)), RS.LID_Z0 - 1, -x0, max(yb, yb0 - 0.01 * (1 if k == 'a' else -1)), Z1 + 1), yin_cut))


def half(k):
    sy = 1 if k == 'a' else -1
    ring = ring_body_b()
    y0, y1 = (SPLIT_Y, 100) if sy > 0 else (-100, SPLIT_Y)
    s = common(ring, gbox(-100, y0, Z0 - 1, 100, y1, Z1 + 1))
    s = fuse(s, lid_plain(k))
    if sy > 0 and BB_NOTCH: s = cut(s, bb_notch())  # 底板 R85 缺口
    for a in W_A:                     # 配重孔上方顶盖开孔 (配重螺丝从罩顶插)
        x, y = pol(RS.W_R, a)
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, cyl(x, y, RS.W_CB_D, RS.W_BEAR, Z1 + 1))
    for x, y in MNT_PTS:              # 套筒孔穿顶盖
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, acc_cut(x, y, BOSS_Z1, Z1 + 1))
    return clean(s)


shr_a, shr_b = half('a'), half('b')

def balance():
    """两半罩 PLA 1.24 g/cm³ 的质心偏移 (g·mm, 相对转轴), 各半 + 合计"""
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    out = {}; tx = ty = 0.0
    for k, sh in (('a', shr_a), ('b', shr_b)):
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(sh, g); c = g.CentreOfMass(); m = g.Mass() * 1.24e-3
        out[k] = dict(m=round(m, 2), cx=round(c.X(), 3), cy=round(c.Y(), 3), Ux=round(m * c.X(), 1), Uy=round(m * c.Y(), 1)); tx += m * c.X(); ty += m * c.Y()
    out['U'] = dict(x=round(tx, 1), y=round(ty, 1), abs=round(math.hypot(tx, ty), 1))
    return out


def report():
    _fpc = RB.load_fpc()
    rep = dict(vol=dict(a=round(vol(shr_a), 1), b=round(vol(shr_b), 1)), mass_g=dict(a=round(vol(shr_a) * 1.24e-3, 1), b=round(vol(shr_b) * 1.24e-3, 1)),
               valid=dict(a=BRepCheck_Analyzer(shr_a).IsValid(), b=BRepCheck_Analyzer(shr_b).IsValid()), solids=dict(a=len(solids(shr_a)), b=len(solids(shr_b))),
               boss=dict(z=(BOSS_Z0, BOSS_Z1), w=BOSS_W, ear_loc=dict(x0=EAR_X0, y=(EAR_Y0, EAR_Y1)), hole_r=HOLE_R, ang=MNT_A, screw=f'DIN912 M3×{MNT_L:g} 从耳顶往下 尾 Z{SCR_TIP:g}', nut_z=NUT_Z, acc_d=ACC_D,
                         w_a=W_A, w_drop=W_DROP, n_w=len(W_A)),
               balance=balance(), slot_y=(SLOT_Y0, SLOT_Y1), br_pocket={k: round(v[1], 3) for k, v in BR_POCKET.items()}, antenna=dict(ang=ANT_ANG, half_ang=round(ANT_HA, 3), z=(ANT_Z0, ANT_Z1), margin_deg=ANT_MARGIN))
    others = dict(承载盘B=RB.rim, **{n: sh for n, sh, _ in RB.SCREEN_PARTS}, 底板=RB.VB['baseboard'], 底板器件=RB.VB['bb_parts'], CZ06=RB.VB['cz06'],
                  灯板=RB.VB['led'], 夹条=LS.bar_s, 顶部件=LS.top, 无线托盘=RB.WH.H, FPC_A=_fpc['fpc_a_v1_2'], FPC_B=_fpc['fpc_b_v1_2'],
                  桥板A=_fpc['bridge_a_v1_2'], 桥板B=_fpc['bridge_b_v1_2'], FPC座=_fpc['bb_fpc_seats_v1_2'], 天线a=ant_new_a, 天线b=ant_new_b)
    inter = {}
    for n1, s1 in (('罩A(+y)', shr_a), ('罩B(-y)', shr_b)):
        for n2, s2 in others.items():
            v = common_v(s1, s2)
            if v > 1e-3: inter[f'{n1} × {n2}'] = round(v, 3)
    v = common_v(shr_a, shr_b)
    if v > 1e-3: inter['罩A × 罩B'] = round(v, 3)
    rep['interference_mm3'] = inter
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


if __name__ == '__main__':
    rep = report()
    for name, sh, col in (('rotor_shroud_b_a_v1_2b', shr_a, '#6FA8DC'), ('rotor_shroud_b_b_v1_2b', shr_b, '#93C47D')):
        d = B.V12 / 'models' / name; d.mkdir(parents=True, exist_ok=True)
        write_doc([(name, sh, col, None, False)], d / f'{name}.step', name)
        BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(d / f'{name}.stl'))
        fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); t = xf(sh, fx)   # 倒放: 罩顶落床
        tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, -bbox(t)[2])); t = xf(t, tz)
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(d / f'{name}_print.stl'))
    (B.V12 / 'models' / 'rotor_shroud_b_a_v1_2b' / 'shroud_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('ok')
