# -*- coding: utf-8 -*-
"""转子盘B (2026-11-17 晚 用户定, 第一版): 玻纤底板 3 mm + 承载盘单件 (并入毂盘) + 屏幕固定件 ×2。
    cd v1.2/scripts && ../../.venv/bin/python rotor_b_v1_2.py
世界坐标同 build_v1_2 (电机顶 Z21.5 = 原毂盘底)。11-18 用户: 承载盘总厚 9 = 外唇 3 + 线圈腔 2.8 + 托盘 3.2 ⇒ 盘顶 Z30.5 (原 32, 承载盘以上件随 B.Z_RIM_TOP 下来 1.5);
灯板下沿离盘顶 5 → 7 (屏幕相对抬 2, 绝对 Z37 → 37.5), FPC B 让位槽取消; 承载盘铜螺母改 M3×3。
叠层 (下→上):
  玻纤板 fr4_plate_v1_2b  Φ165 × 3, Z21.5–24.5, 无铜 FR4 (models/fr4_plate_v1_2b/build.py 出板厂文件; 这里只按同参数建装配体)
  承载盘 rim_ring_v1_2b   V0.4 rim_ring 外形 (Φ170) + 并入毂盘:
      托盘 r≤85 Z27.3–32 (厚 4.7); 底面线圈腔 r39.9–72.5 Z24.5–27.3 (深 2.8, 线圈 ID80 × 2.7, 用户 11-17);
      中心实体 r≤39.9 / 外环 r72.5–85 都下到玻纤板顶 Z24.5; 外唇 r82.7–85 再往下包住玻纤板边到 Z21.5
  屏幕固定件 screen_holder_v1_2b_a/_b: = V1.2 立板 led_post (横杆 + 腹板 + 天线板) 把两只耳朵换成弧形带
      r73–81.7, ±44° (绕 ±x), Z32–37 (厚 5, 顶 = 灯板下沿); 锚孔 = 原耳朵孔 22.5°/337.5° (+x) / 157.5°/202.5° (−x) 在 R77.5;
      带上罩子锁点 M3 热熔铜螺母 Φ4.2×4 @ r77 ±40° / ±140° (罩子 4 个耳朵改坐到带顶 Z37)
螺丝 (全部在桌上装好再上电机):
  - 固定件 → 夹条 2×M3×8 自攻 (同 V1.2 立板): 头在固定件底面 Φ6×3 沉孔里 ⇒ 先把固定件和夹条拧好, 再整组放上承载盘 (11-18 补挖: 弧形带原把这孔填实了)
  - 16 颗从玻纤板底往上 (头埋玻纤板 Φ7.2×1.5 沉孔): 内圈 R34 ×8 + 外圈 67.5/112.5/247.5/292.5° ×4 → 承载盘顶面 M3×4 铜螺母;
    外圈 22.5/157.5/202.5/337.5° ×4 → 穿承载盘 + 固定件, 固定件顶面 M3 法兰螺母
  - 电机 4×M3×10 从承载盘顶面 Φ7×5 沉孔往下 (头顶 Z30), 穿玻纤板进电机 4.5
  - (11-18 取消) 托盘顶面 FPC B 让位槽 37×22.5 深 2
  - 底板 r4j 4 孔: 承载盘底面 Φ7.4×1.5 沉孔 (头埋进托盘, 不进线圈腔) 往上
"""
import io, contextlib, json, math
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
    import v2_boards_v1_2 as V
    import led_support_v1_2 as LS
    import rotor_shroud_v1_2 as RS
    import wireless_holder_v1_2 as WH
from helpers import write_doc
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz, solids = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz, B.solids
def common(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return o.Shape()
def common_v(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return vol(o.Shape()) if o.IsDone() else -1.0
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
def sector(r0, r1, z0, z1, a0, a1): return cut(cyl(0, 0, 2 * r1, z0, z1, ang=a1 - a0, a0=a0), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
pol = lambda r, a: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))   # noqa: E731

# ---------------- 参数 ----------------
Z_F0 = B.ROTOR_TOP                     # 21.5 电机顶 = 玻纤板底
FR4_T, FR4_OD = 3.0, 165.0
Z_F1 = Z_F0 + FR4_T                    # 24.5 玻纤板顶 = 承载盘底 (中心/外环)
CAV_H = 2.8                            # 线圈腔深 (线圈 2.7, 用户 11-17 定 2.8, 同定子)
Z_T0 = Z_F1 + CAV_H                    # 27.3 托盘底 (腔顶)
Z_TOP = B.Z_RIM_TOP                    # 30.5 承载盘顶 (11-18 用户: 总厚 9 = 3 + 2.8 + 3.2, 托盘 3.2; 原 32 托盘 4.7)
assert abs(Z_TOP - (Z_T0 + 3.2)) < 1e-6
COIL_R0 = B.COIL_SEAT_R                # 39.9 线圈内定位 (ID80, 间隙 0.2)
COIL_R1 = 72.5                         # 线圈腔外壁 = 外环内径 (外环宽 10 到 r82.5, 用户 ≥1 cm)
RIM_R = 85.0                           # Φ170
LIP_R0 = FR4_OD / 2 + 0.2              # 82.7 外唇内壁包玻纤板边 (单边 0.2)
R_IN, R_OUT, R_MOT = 34.0, 77.5, 8.0
IN_PTS = [pol(R_IN, 22.5 + 45 * k) for k in range(8)]
ANCHOR_ANG = (22.5, 157.5, 202.5, 337.5)          # = V1.2 立板耳朵孔, 用户在玻纤板图上圈的 4 个
NUT_OUT_ANG = (67.5, 112.5, 247.5, 292.5)
ANCHOR_PTS = [pol(R_OUT, a) for a in ANCHOR_ANG]
OUT_NUT_PTS = [pol(R_OUT, a) for a in NUT_OUT_ANG]
MOT_PTS = [pol(R_MOT, 45 + 90 * k) for k in range(4)]
INS_D, INS_H = B.INS_HOLE_D, 3.0                  # 11-18 用户: 热熔螺母改 M3×3 (盘减薄), 孔 Φ4.2 × 3.0 (原 M3×4)
H_INS_H = 4.0                                     # 屏幕固定件带顶罩子锁点铜螺母仍 M3×4 (只承载盘改 M3×3)
CENTER_D, CENTER_H = 5.2, 3.5                     # 用户 11-17: M5 真实 5.2, 深 3.5 (有无玻纤板都能用)
BB_CB_D, BB_CB_H = 7.4, 1.5                       # 底板螺丝 薄头 Φ7×1.5 埋进托盘
SHR_LOCK_R = 77.0                                 # 罩子锁点半径 (原 79: 带外缘 81.7, 铜螺母孔壁太薄 ⇒ 内移 2)
SHR_LOCK_ANG = (40.0, 140.0, 220.0, 320.0)        # 角度同 V1.2 (B.SHR_ANG)
SHR_LOCK_PTS = [pol(SHR_LOCK_R, a) for a in SHR_LOCK_ANG]
H_R0, H_R1, H_SPAN = 73.0, LS.R_CLIP, 44.0        # 固定件弧形带
H_Z1 = LS.Z0                                      # 37.0 = 灯板下沿 = 横杆顶
MOT_CB_H = Z_TOP - 27.0                           # 3.5: 电机螺丝头支承仍 Z27 (M3×10 进电机 4.5 不变), 头顶 Z30 低于盘顶 0.5
# FPC B 从桥板 B 下沿过转轴到底板 J6, 原实测最低 Z30.6 (x±17.75, y −14.26…6.74), 比盘顶 Z32 低 ⇒ 原托盘顶面开让位槽; 11-18 改灯板抬 2 (FPC 最低 Z31.1, 盘顶 30.5) (V1.2 原承载盘中心是 Φ50 通孔, 自然让开)
FPC_POCKET = None                                  # 11-18 用户「不需要, 取消吧」: 取消让位槽 (原 (-18.5, -15.0, 18.5, 7.5, 30.0) x0,y0,x1,y1,槽底Z); 电机沉孔深 5 保留 (螺丝不变)

# ---------------- 玻纤板 (装配体, 与 models/fr4_plate_v1_2b/build.py 同参数) ----------------
fr4 = cyl(0, 0, FR4_OD, Z_F0, Z_F1)
for x, y in IN_PTS + ANCHOR_PTS + OUT_NUT_PTS:
    fr4 = cut(fr4, cyl(x, y, 3.2, Z_F0 - 1, Z_F1 + 1), cyl(x, y, 7.2, Z_F0 - 1, Z_F0 + 1.5))
fr4 = clean(cut(fr4, *[cyl(x, y, 3.2, Z_F0 - 1, Z_F1 + 1) for x, y in MOT_PTS], cyl(0, 0, CENTER_D, Z_F0 - 1, Z_F1 + 1)))

# ---------------- 承载盘单件 ----------------
rim = fuse(cyl(0, 0, 2 * RIM_R, Z_T0, Z_TOP),                      # 托盘
           cyl(0, 0, 2 * COIL_R0, Z_F1, Z_T0 + 0.01),              # 中心实体 (线圈内定位)
           ann(COIL_R1, RIM_R, Z_F1, Z_T0 + 0.01),                 # 外环 (铜螺母环)
           ann(LIP_R0, RIM_R, Z_F0, Z_F1 + 0.01))                  # 外唇包玻纤板边
rim = clean(rim)
cuts = []
for x, y in MOT_PTS:                                                # 电机 4 孔: Φ3.2 通 + 顶面 Φ7×4 沉孔
    cuts += [cyl(x, y, 3.2, Z_F0 - 1, Z_TOP + 1), cyl(x, y, 7.0, Z_TOP - MOT_CB_H, Z_TOP + 1)]
cuts.append(cyl(0, 0, CENTER_D, Z_F1 - 1, Z_F1 + CENTER_H))        # 中心窝 Φ5.2×3.5 (底面)
if FPC_POCKET: cuts.append(gbox(FPC_POCKET[0], FPC_POCKET[1], FPC_POCKET[4], FPC_POCKET[2], FPC_POCKET[3], Z_TOP + 1))   # FPC B 让位槽
for x, y in IN_PTS + OUT_NUT_PTS:                                   # 12 颗从下往上进铜螺母: Φ3.2 通 + 顶面 Φ4.2×4
    cuts += [cyl(x, y, 3.2, Z_F0 - 1, Z_TOP + 1), cyl(x, y, INS_D, Z_TOP - INS_H, Z_TOP + 1)]
for x, y in ANCHOR_PTS:                                             # 4 颗穿到固定件: Φ3.4 通
    cuts.append(cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1))
for x, y in B.BB_HOLES:                                             # 底板 r4j 4 孔: Φ3.4 通 + 底面 Φ7.4 让位到 Z_T0+1.5 (头埋托盘)
    cuts += [cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1), cyl(x, y, BB_CB_D, Z_F1 - 0.1, Z_T0 + BB_CB_H)]
for x, y in B.MOD_HOLES:                                            # 11-19 无线模块两夹块 4 孔: 顶面 Φ4.2×3 铜螺母 (M3×3); M3×8 从耳顶 Z35.5 下来尾 Z27.5 = 螺母底, 不再挖 Φ3.2 让尖 (内侧 2 孔 r41 在线圈腔上方, 托盘底留 0.2)
    cuts += [cyl(x, y, INS_D, Z_TOP - INS_H, Z_TOP + 1)]
for x, y in B.AC_HOLES:                                             # 线圈 AC 引线 Φ3 通 + 外环处 Φ3.4 缺口
    cuts += [cyl(x, y, B.AC_HOLE_D, Z_F0 - 1, Z_TOP + 1), cyl(x, y, B.AC_HOLE_D + 0.4, Z_F1 - 0.1, Z_T0 + 0.01)]
rim = clean(cut(rim, *cuts))

# ---------------- 屏幕固定件 (= 立板 led_post 换掉耳朵) ----------------
def holder(sx):
    c0 = 0.0 if sx > 0 else 180.0
    p = LS.post(sx)
    # 去掉原耳朵: 只留 横杆 (Z≤37 的部分在 x 69–77 局部 |y|≤14) + 腹板/天线板; 原耳朵在 Z32–36, 横杆外 |y| 方向
    keep = fuse(xf(gbox(min(sx * 60, sx * 90), -LS.FOOT_Y, LS.RIM_TOP - 1, max(sx * 60, sx * 90), LS.FOOT_Y, 400), LS.T_ECC),
                gbox(-200, -200, H_Z1, 200, 200, 400))
    p = common(p, keep)
    band = sector(H_R0, H_R1, LS.RIM_TOP, H_Z1, c0 - H_SPAN, c0 + H_SPAN)
    s = fuse(p, band)
    pts = [(x, y) for x, y in ANCHOR_PTS if x * sx > 0]
    lk = [(x, y) for x, y in SHR_LOCK_PTS if x * sx > 0]
    xb = sx * LS.BAR_SCR_X[0]                                    # 11-18: 弧形带 r73–81.7 盖住了立板 → 夹条竖螺丝 (x±73, y=ECC) ⇒ 重挖 Φ3.4 通 + 底面 Φ6×3 沉孔 (同 LS.post)
    s = cut(s, *[cyl(x, y, 3.4, LS.RIM_TOP - 1, H_Z1 + 1) for x, y in pts],
            *[cyl(x, y, INS_D, H_Z1 - H_INS_H, H_Z1 + 1) for x, y in lk],
            cyl(xb, LS.BAR_SCR_Y, 3.4, LS.RIM_TOP - 1, LS.Z0 + 1), cyl(xb, LS.BAR_SCR_Y, 6.0, LS.RIM_TOP - 1, LS.BAR_SCR_BEAR))
    return clean(s), pts, lk

hold_a, ANC_A, LK_A = holder(+1)
hold_b, ANC_B, LK_B = holder(-1)

# ---------------- 校核 (11-18: 挪进 report(), import 时不跑; 整机切转子盘B 后各脚本都要 import 本模块) ----------------
coil = cut(ann(COIL_R0 + 0.1, COIL_R1 - 0.1, Z_F1, Z_F1 + 2.7), *[cyl(x, y, 4.0, Z_F1 - 1, Z_T0) for x, y in B.AC_HOLES])
VB = LS.VB
_FPC_CACHE = {}
def load_fpc():
    from helpers import read_step
    if not _FPC_CACHE:
        _FPC_CACHE.update({n: read_step(B.V12 / 'models' / 'fpc_v1_2' / 'r4i_定稿' / f'{n}.step') for n in ('fpc_a_v1_2', 'fpc_b_v1_2', 'bridge_a_v1_2', 'bridge_b_v1_2', 'bb_fpc_seats_v1_2')})
    return _FPC_CACHE

def report():
    _fpc = load_fpc()
    rep = dict(z=dict(fr4=(Z_F0, Z_F1), cavity=(Z_F1, Z_T0), tray=(Z_T0, Z_TOP), holder=(LS.RIM_TOP, H_Z1)),
               vol=dict(fr4=round(vol(fr4), 1), rim=round(vol(rim), 1), hold_a=round(vol(hold_a), 1), hold_b=round(vol(hold_b), 1)),
               mass_g=dict(fr4=round(vol(fr4) * 1.85e-3, 1), rim_PLA=round(vol(rim) * 1.24e-3, 1), hold_PLA=round(vol(hold_a) * 1.24e-3, 1)),
               valid=dict(rim=BRepCheck_Analyzer(rim).IsValid(), fr4=BRepCheck_Analyzer(fr4).IsValid(), hold_a=BRepCheck_Analyzer(hold_a).IsValid(),
                          hold_b=BRepCheck_Analyzer(hold_b).IsValid()),
               solids=dict(rim=len(solids(rim)), hold_a=len(solids(hold_a)), hold_b=len(solids(hold_b))))
    others = dict(底板=VB['baseboard'], 底板器件=VB['bb_parts'], CZ06=VB['cz06'], 灯板=VB['led'], 夹条=LS.bar_s, 顶部件=LS.top,
                  无线托盘=WH.H, FPC_A=_fpc['fpc_a_v1_2'], FPC_B=_fpc['fpc_b_v1_2'], 桥板A=_fpc['bridge_a_v1_2'], 桥板B=_fpc['bridge_b_v1_2'], FPC座=_fpc['bb_fpc_seats_v1_2'], 电机=B.motor, 定子盘=B.flange_disc, 安装法兰=B.mounting_flange, 线圈环=B.ring)
    mine = dict(玻纤板=fr4, 承载盘=rim, 固定件A=hold_a, 固定件B=hold_b, 线圈=coil)
    inter = {}
    for n1, s1 in mine.items():
        for n2, s2 in list(others.items()) + [(k, v) for k, v in mine.items() if k > n1]:
            if n2 == n1: continue
            v = common_v(s1, s2)
            if v > 1e-3: inter[f'{n1} × {n2}'] = round(v, 3)
    rep['interference_mm3'] = inter
    # 罩子 (rotor_shroud_b_v1_2, 2 片) 的干涉在它自己的 report() 和整机 check_v1_2 里查 (这里 import 不了, 它反过来 import 本模块)
    print(json.dumps(rep, ensure_ascii=False, indent=1))

    return rep


# ---------------- 输出 ----------------
OUTD = {}
def out(name, sh, flip=False, color='#8A8F98'):
    d = B.V12 / 'models' / name; d.mkdir(parents=True, exist_ok=True)
    write_doc([(name, sh, color, None, False)], d / f'{name}.step', name)
    BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(d / f'{name}.stl'))
    t = sh
    if flip:
        fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); t = xf(t, fx)
    tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, -bbox(t)[2])); t = xf(t, tz)
    BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(d / f'{name}_print.stl'))
    OUTD[name] = str(d)
if __name__ == '__main__':
    rep = report()
    out('rim_ring_v1_2b', rim, flip=True, color='#6AA84F')               # 打印: 托盘顶面朝下, 线圈腔/外环朝上 (免支撑)
    out('screen_holder_v1_2b_a', hold_a, color='#F1C232')
    out('screen_holder_v1_2b_b', hold_b, color='#E69138')
    write_doc([('fr4_plate_v1_2b (装配位)', fr4, '#C9B458', None, False), ('rim_ring_v1_2b', rim, '#6AA84F', None, False),
               ('screen_holder_v1_2b_a', hold_a, '#F1C232', None, False), ('screen_holder_v1_2b_b', hold_b, '#E69138', None, False),
               ('线圈 (占位)', coil, '#D9822B', None, False)], B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step', 'rotor_b')
    (B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出', OUTD)
