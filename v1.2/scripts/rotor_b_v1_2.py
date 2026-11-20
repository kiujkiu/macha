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
  (11-20 起) 屏幕固定件 = 玻纤平板 screen_fr4_v1_2b ×4 (同一件, 0/90/180/270°, Z30.5–33.5; 11-20 晚改长方形 x66–81.2 |y|≤35, 外角按 r81.7 圆角) + 侧立件 screen_post_v1_2b ×2 (同一件, 底 Z33.5; 11-20 夜只剩垫块, 天线 FPC 改贴罩内壁);
      原 screen_holder_v1_2b_a/b (PETG 弧形带 + 立板一体, Z30.5–37) 作废 (产物移 转子盘B/作废_11-20/)
螺丝 (全部在桌上装好再上电机):
  - 屏幕夹条 2×M3×12 超薄头: 从屏幕玻纤板底面 Φ7.2×1.5 沉孔往上 (支承 Z32) 穿 玻纤板 → 侧立件 → 自攻进夹条 (尾 Z44) ⇒ 先把 玻纤板 + 侧立件 + 夹条 拧成一组, 再整组放上承载盘
  - 16 颗从 fr4_plate 底往上 (头埋 Φ7.2×1.5 沉孔, 支承 Z23): 内圈 R34 ×8 → 承载盘顶面 Φ8×3.7 沉孔 M3 法兰螺母 (M3×7);
    外圈 r77.5 @22.5+45k ×8 → 穿承载盘 + 屏幕玻纤板, 法兰螺母坐屏幕玻纤板顶 Z33.5–37.2 (M3×15, 尾 Z38 露 0.8; 11-20 夜恢复, 只锁屏幕玻纤板)
  - 罩子锁点 ×8 (11-20 夜 用户「罩子要在这里从下往上装一个螺丝，然后罩子放上，然后装一个法兰螺母」「这装罩子的孔是装在屏幕安装这个件上的，不需要在转子盘做」):
    每块屏幕玻纤板本地 (73, ±19.5) Φ3.2 通 + 板底 Φ7.2×1.5 沉孔; M3×10 超薄头从板底往上 (支承 Z32, 头藏板底, 板坐承载盘上螺丝掉不下来),
    穿板剩余 1.5 + 罩耳 Z33.5–37.5, 罩耳顶 M3 法兰螺母 Z37.5–41.2, 尾 Z42 露 0.8; 承载盘 / fr4_plate 不开这些孔
    (之前 11-20 晚: 罩子锁点 = 外圈 8 孔 M3×18 螺母坐罩耳顶; 再之前 ±14° M3×12 从上往下进承载盘窝 —— 均作废)
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
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Ax2, gp_Pnt, gp_Dir

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz, solids = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz, B.solids
def common(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return o.Shape()
def common_v(a, b):
    o = BRepAlgoAPI_Common(a, b); o.Build(); return vol(o.Shape()) if o.IsDone() else -1.0
def ann(r0, r1, z0, z1): return cut(cyl(0, 0, 2 * r1, z0, z1), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
def sector(r0, r1, z0, z1, a0, a1): return cut(cyl(0, 0, 2 * r1, z0, z1, ang=a1 - a0, a0=a0), cyl(0, 0, 2 * r0, z0 - 1, z1 + 1))
pol = lambda r, a: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))   # noqa: E731
def _rz(sh, a): return xf(sh, rotz(a)) if a else sh
def _mv(sh, dx, dy, dz=0.0): t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz)); return xf(sh, t)
def _ocm(a, b): return B.op(BRepAlgoAPI_Common, a, b)

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
CENTER_D, CENTER_H = 5.2, 3.5                     # 用户 11-17: M5 真实 5.2, 深 3.5 (有无玻纤板都能用)
BB_CB_D, BB_CB_H = 7.4, 1.5                       # 底板螺丝 薄头 Φ7×1.5 埋进托盘
# 11-20 夜 罩子锁点改在屏幕玻纤板上 (用户「我画的这装罩子的孔是装在屏幕安装这个件上的，不需要在转子盘做」; 图上圈 (±72,−21)(±22,−72)):
#   每块板本地 (SHR_LOC_X, ±SHR_LOC_Y), 4 板同件 ⇒ 8 点对称; 定位见下面 SP 段 (SHR_LOCK_LOC / SHR_LOCK_PTS / SHR_LOCK_ANG / SHR_LOCK_R)
SHR_LOC_X, SHR_LOC_Y = 73.0, 19.5                 # 用户量的 (72, ±21) 微调: 离外圈孔 (71.6, ±29.66) 10.26 (两个 Φ8 螺母不打架); 罩耳内边 y15.5 离侧立件 (y≥−14.44) 1.06
SHR_LOCK_R = math.hypot(SHR_LOC_X, SHR_LOC_Y)     # 75.56
OUT_SCR_BEAR = Z_F0 + 1.5                         # 23.0 超薄头支承 (fr4_plate 底 Φ7.2×1.5 沉孔)
OUT_SCR_L = 15.0                                  # 11-20 夜恢复 M3×15: 尾 Z38.0; 屏幕玻纤板顶法兰螺母 Z33.5–37.2 吃满, 露 0.8 (11-20 晚 M3×18 到罩耳顶 作废)
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
IN_NUT_D, IN_NUT_H = 8.0, 3.7                    # 11-19 16:53 用户「这8个改一下，用法兰螺母，沉孔改为深度3.7mm，直径8mm」: 内圈 R34 ×8 取消铜螺母, 顶面 Φ8×3.7 沉孔放 M3 法兰螺母 (底 Z26.8, 下面中心实体剩 2.3)
assert R_IN + IN_NUT_D / 2 <= COIL_R0 - 1.0       # 沉孔不进线圈腔 (r38 < 39.9)
for x, y in IN_PTS:
    cuts += [cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1), cyl(x, y, IN_NUT_D, Z_TOP - IN_NUT_H, Z_TOP + 1)]
assert R_OUT - 3.4 / 2 >= COIL_R1 + 1.0 and R_OUT + 4.0 <= LIP_R0   # 外圈通孔边离线圈腔外壁 ≥ 1; 螺母法兰 Φ8 在罩壁/外唇 r82 以内
for x, y in OUT_NUT_PTS:                                            # 外圈 4 颗只做 Φ3.4 通孔 (11-20 用户「就做通孔就行」); 与锚孔 4 颗一样: 穿屏幕玻纤板, 法兰螺母坐屏幕玻纤板顶
    cuts.append(cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1))
for x, y in ANCHOR_PTS:                                             # 4 颗穿到固定件: Φ3.4 通
    cuts.append(cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1))
for x, y in B.BB_HOLES:                                             # 底板 r4j 4 孔: Φ3.4 通 + 底面 Φ7.4 让位到 Z_T0+1.5 (头埋托盘)
    cuts += [cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1), cyl(x, y, BB_CB_D, Z_F1 - 0.1, Z_T0 + BB_CB_H)]
for x, y in B.MOD_HOLES:                                            # 11-19 用户「螺丝是从下往上锁」「和 soc 底板一样」: 无线模块两夹块 4 孔同底板 —— Φ3.4 通 + 底面 Φ7.4 让位到 Z_T0+1.5 (M3×6 超薄头埋托盘, 进夹块底面 M3×4 铜螺母)
    cuts += [cyl(x, y, 3.4, Z_F0 - 1, Z_TOP + 1), cyl(x, y, BB_CB_D, Z_F1 - 0.1, Z_T0 + BB_CB_H)]
for x, y in B.AC_HOLES:                                             # 线圈 AC 引线 Φ3 通 + 外环处 Φ3.4 缺口
    cuts += [cyl(x, y, B.AC_HOLE_D, Z_F0 - 1, Z_TOP + 1), cyl(x, y, B.AC_HOLE_D + 0.4, Z_F1 - 0.1, Z_T0 + 0.01)]
    _r = math.hypot(x, y)
    if _r < COIL_R0 + 1.0:                                          # 11-19: 孔落在线圈内圈 (中心实体) 里 ⇒ 腔层开径向槽 (宽 Φ+0.4) 从孔通到线圈腔, 引线从线圈内缘过来
        _w = B.AC_HOLE_D + 0.4
        _sl = gbox(_r - 0.01, -_w / 2, Z_F1 - 0.1, COIL_R0 + 0.5, _w / 2, Z_T0 + 0.01)
        cuts.append(xf(_sl, rotz(math.degrees(math.atan2(y, x)))))
# 罩子锁点不在承载盘上开孔 (11-20 夜 只在屏幕玻纤板上; 原承载盘顶面六角法兰螺母窝 LOCK_POCKET 已删, 17:4x 用户「这里不需要孔」)
rim = clean(cut(rim, *cuts))

# ---------------- 11-20 屏幕固定件拆成: 玻纤平板 ×4 (同一件) + 侧立件 ×2 (同一件) ----------------
# 用户 11-20 原话: 「这4个件我们细化一下，1.厚度做到3mm，固定屏幕的m3螺丝沉孔做到1.5深度，上边锁法兰螺母通孔就行 2.上下我理解也做一个吧，罩子锁4个点稳定一点，现在动平衡难度较大，不能让本体旋转有晃动」
#   「左右两个件是不是能做成1个，开两个孔就行」「然后侧立面这个，能不能做到别的件，我想锁屏幕这个做玻纤」「能不能这4个玻纤做成一样，做成2个款也行」
#   「不要干涉到灯板，在安装孔的位置」
# 玻纤板 screen_fr4_v1_2b (外协 CNC, 无铜 FR4 3 厚) ×4: 同一零件放 0/90/180/270°, 平贴承载盘顶 Z30.5–33.5; 每块板孔位相对自身中心角:
#   外圈 2×Φ3.4 @±22.5° r77.5 (fr4_plate 底往上的 M3×15, 法兰螺母坐本板顶) / 罩子锁点 2×Φ3.2 + 底面 Φ7.2×1.5 沉孔 @(73, ±19.5) (11-20 夜, M3×10 从板底往上, 罩耳顶法兰螺母) /
#   屏幕夹条孔 2×Φ3.4 + 底面沉孔 @局部 (73, ±4.69) (只用一个) / 侧立件定位孔 3×Φ3.2 @局部 (77.5, 0 / ±9.38) (左右板用 2 个, 上下板全空)
# 侧立件 screen_post_v1_2b (PETG 打印) ×2: 11-20 夜起只剩垫块 x67–80.4 |y|≤9.5 Z33.5–37.5 (天线 FPC 改贴罩内壁, 腹板 + 天线板去掉); 下面两行为 11-20 旧说明:
#   原 holder() 里 LS.post 的横杆 + 腹板 + 天线板, 底面坐玻纤板顶 Z33.5 (原从 Z30.5 起, 截掉 3);
#   横杆局部 |y| 14 → 8 (当时让 ±14° 罩耳; 11-20 晚罩耳挪到 ±22.5° 后不再紧, 保持 8 不重打), 再与自身 y 镜像取交 ⇒ ±x 两件 = 同一零件转 180°; 底面 2 个 Φ3×2 定位销插玻纤板 Φ3.2 孔
#   夹条竖螺丝 M3 从玻纤板底沉孔往上: 玻纤板 → 侧立件 → 夹条 (自攻), 一颗压三层
SP_Z0, SP_T = Z_TOP, 3.0
SP_Z1 = SP_Z0 + SP_T                              # 33.5 玻纤板顶 = 侧立件底 = 罩耳底
SP_R1 = LS.R_CLIP                                 # 81.7 外角圆角半径 (以轴心为圆心, = 原弧形带外缘, 罩壁 r82 以内)
# 11-20 晚 用户「我感觉长方形就行」: 外形 = 长方形 x SP_X0–SP_X1 × |y|≤SP_HY, 两个外角超出 r81.7 的部分按 r81.7 圆弧切掉 (不改回扇形; 原扇形 r73–81.7 ±32° + 内伸舌 x68 |y|≤13 作废)
SP_X0, SP_X1, SP_HY = 66.0, 81.2, 35.0            # 内边 x66 (放 270° 时离无线夹块 y−63.6 ≥2.4; 外圈孔边 3.9); 外边 x81.2 (销孔边 2.1, |y|≤9.0 段为直边); |y|≤35 (外圈孔边 3.64, 托住罩耳)
SP_ANG = (0.0, 90.0, 180.0, 270.0)
SP_HOLE_A = (22.5, -22.5)                         # 外圈螺丝 (承载盘 r77.5 @22.5+45k 全 8 颗都穿本板)
SP_SCR_X, SP_SCR_DY = LS.BAR_SCR_X[0], abs(LS.ECC)   # 屏幕夹条孔 局部 (73, ±4.69): 板放 0° 用 y=ECC 那个, 放 180° 用另一个
SP_CB_D, SP_CB_H = 7.2, 1.5                       # 底面沉孔: 用户「沉孔做到1.5深度」; 直径按超薄头 Φ7 (同 fr4_plate Φ7.2×1.5; 任务单写 Φ6 装不下 Φ7 头, 待用户确认)
POST_HY = 9.5                                     # 侧立件垫块局部半长 (11-20 夜 8 → 9.5): 世界 y −14.19…4.81, 离罩耳内边 (y ±15.5) 1.31
POST_X0, POST_X1 = 67.0, 80.4                     # 垫块 x (11-20 夜, 原横杆 x69–77 + 腹板到 83.7): 落在屏幕玻纤板 x66–81.2 内; 外角 r81.64 < 81.7
# 11-20 夜 用户「贴到罩子吧」「罩子天然有这个侧立面」「这个天线是fpc的」: 天线 FPC 改贴罩子内壁 ⇒ 侧立件去掉腹板 + 天线板, 只剩垫块 (平放打印)
#   用户要「4 个 M3 + 沉孔, 沉孔都从下往上」锁侧立件: 放不下 (见报告) ⇒ 仍是 夹条 M3×12 (一颗压 玻纤板+垫块+夹条) + 2 销 定位
PIN_D, PIN_H, PIN_HOLE_D = 3.0, 2.0, 3.2          # 侧立件底面定位销 Φ3×2 → 玻纤板 Φ3.2 通孔
PIN_X = 77.5                                      # 销 局部 (77.5, ±4.69) ⇒ 世界 y 0 / 2·ECC; 板上孔 (77.5, 0 / ±9.38) 对 x 轴对称 (4 板同件)
SP_PIN_LOC = [(PIN_X, 0.0), (PIN_X, 2 * SP_SCR_DY), (PIN_X, -2 * SP_SCR_DY)]
SHR_HOLE_D = 3.2                                  # 罩子锁点 Φ3.2 通 (超薄头从板底沉孔往上, 头藏板底)
SHR_LOCK_LOC = [(SHR_LOC_X, SHR_LOC_Y), (SHR_LOC_X, -SHR_LOC_Y)]
SP_HOLES_LOC = dict(out=[pol(R_OUT, a) for a in SP_HOLE_A],
                    scr=[(SP_SCR_X, SP_SCR_DY), (SP_SCR_X, -SP_SCR_DY)], pin=SP_PIN_LOC, lock=SHR_LOCK_LOC)
def _rot(p, a): c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c)
SHR_LOCK_PTS = sorted([_rot(p, a) for a in SP_ANG for p in SHR_LOCK_LOC], key=lambda p: math.atan2(p[1], p[0]) % (2 * math.pi))   # 世界 8 点
SHR_LOCK_ANG = tuple(round(math.degrees(math.atan2(y, x)) % 360, 3) for x, y in SHR_LOCK_PTS)    # 14.96/75.04/104.96/165.04/194.96/255.04/284.96/345.04
SHR_SCR_BEAR = SP_Z0 + SP_CB_H                    # 32.0 罩锁螺丝超薄头支承
SHR_SCR_L = 10.0                                  # M3×10: 尾 Z42.0, 罩耳顶法兰螺母 Z37.5–41.2 吃满 3.7, 露 0.8 (M3×8 尾 Z40 只吃 2.5)
OUT_NUT_Z = (SP_Z1, SP_Z1 + 3.7)                  # 外圈法兰螺母坐本板顶 33.5–37.2
SHR_GAP = dict(out=round(min(math.dist(p, q) for p in SHR_LOCK_LOC for q in SP_HOLES_LOC['out']), 2),           # 罩锁孔 ↔ 外圈孔 圆心距
               pin=round(min(math.dist(p, q) for p in SHR_LOCK_LOC for q in SP_PIN_LOC) - SP_CB_D / 2 - PIN_HOLE_D / 2, 2),
               scr=round(min(math.dist(p, q) for p in SHR_LOCK_LOC for q in SP_HOLES_LOC['scr']) - SP_CB_D, 2))
assert SHR_GAP['out'] >= 10.0 and SHR_GAP['pin'] >= 1.0 and SHR_GAP['scr'] >= 1.0, SHR_GAP
assert math.hypot(SP_SCR_X - PIN_X, SP_SCR_DY) - SP_CB_D / 2 - PIN_HOLE_D / 2 >= 1.0      # 沉孔 ↔ 定位孔壁 ≥ 1
def _edge(x, y, rh):
    """孔 (半径 rh) 到长方形+圆角外形的最小边距"""
    return min(x - rh - SP_X0, SP_X1 - x - rh, SP_HY - abs(y) - rh, SP_R1 - math.hypot(x, y) - rh)
SP_EDGE = dict(out=round(min(_edge(x, y, 1.7) for x, y in SP_HOLES_LOC['out']), 2), scr_cb=round(min(_edge(x, y, SP_CB_D / 2) for x, y in SP_HOLES_LOC['scr']), 2),
               pin=round(min(_edge(x, y, PIN_HOLE_D / 2) for x, y in SP_PIN_LOC), 2), lock_cb=round(min(_edge(x, y, SP_CB_D / 2) for x, y in SHR_LOCK_LOC), 2))
assert SP_EDGE['lock_cb'] >= 2.0 and SP_EDGE['out'] >= 2.0 and SP_EDGE['pin'] >= 2.0 and SP_EDGE['scr_cb'] >= 1.0, SP_EDGE


def screen_fr4_local():
    """板中心在 0° 的局部坐标 (= 放 0° 时的世界坐标)"""
    s = _ocm(gbox(SP_X0, -SP_HY, SP_Z0, SP_X1, SP_HY, SP_Z1), cyl(0, 0, 2 * SP_R1, SP_Z0 - 1, SP_Z1 + 1))   # 长方形 ∩ r81.7 (外角圆角)
    s = cut(s, *[cyl(x, y, 3.4, SP_Z0 - 1, SP_Z1 + 1) for x, y in SP_HOLES_LOC['out'] + SP_HOLES_LOC['scr']],
            *[cyl(x, y, SP_CB_D, SP_Z0 - 1, SP_Z0 + SP_CB_H) for x, y in SP_HOLES_LOC['scr'] + SHR_LOCK_LOC],
            *[cyl(x, y, PIN_HOLE_D, SP_Z0 - 1, SP_Z1 + 1) for x, y in SP_PIN_LOC],
            *[cyl(x, y, SHR_HOLE_D, SP_Z0 - 1, SP_Z1 + 1) for x, y in SHR_LOCK_LOC])
    return clean(s)

def screen_post_local():
    """侧立件局部 (灯板组坐标, y 未加 ECC): 11-20 夜 只剩垫块 (腹板 + 天线板去掉, 天线 FPC 改贴罩子内壁), 两端同件 (转 180°)
    垫块 x POST_X0–POST_X1 × |y|≤POST_HY × Z33.5–37.5 (顶 = 灯板/夹条下沿); 夹条螺丝 Φ3.4 @(73, 0); 底面 2 个 Φ3×2 定位销 @(77.5, ±4.69)"""
    p = gbox(POST_X0, -POST_HY, SP_Z1, POST_X1, POST_HY, LS.Z0)
    p = cut(p, cyl(SP_SCR_X, 0.0, 3.4, SP_Z1 - 1, LS.Z0 + 1))
    p = fuse(p, *[cyl(PIN_X, sy * SP_SCR_DY, PIN_D, SP_Z1 - PIN_H, SP_Z1 + 0.01) for sy in (1, -1)])
    return clean(p)

screen_fr4_loc = screen_fr4_local()
screen_post_loc = screen_post_local()
SCR_FR4 = [_rz(screen_fr4_loc, a) for a in SP_ANG]                 # 0° (+x) / 90° (+y) / 180° (−x) / 270° (−y)
post_a = _mv(screen_post_loc, 0, LS.ECC)                          # +x 侧立件
post_b = _mv(_rz(screen_post_loc, 180), 0, LS.ECC)                # −x 侧立件 (同一零件转 180°)
SCREEN_PARTS = [(f'屏幕玻纤板 screen_fr4_v1_2b @{a:g}°', sh, '#C9B458') for a, sh in zip(SP_ANG, SCR_FR4)] + \
               [('侧立件 +x screen_post_v1_2b', post_a, '#F1C232'), ('侧立件 −x screen_post_v1_2b', post_b, '#E69138')]
SCREEN_KEYS = ['scr_fr4_0', 'scr_fr4_90', 'scr_fr4_180', 'scr_fr4_270', 'post_b_a', 'post_b_b']   # 校核用短名
BAR_SCR_PTS = [(sx * SP_SCR_X, LS.ECC) for sx in (1, -1)]           # 实际用的屏幕夹条螺丝 (世界)
BAR_SCR_BEAR = SP_Z0 + SP_CB_H                                       # 32.0 超薄头支承
BAR_SCR_L = 12.0                                                     # M3×12: 尾 Z44.0, 进夹条 (Z37.5–45.5 Φ2.6 自攻) 6.5 (原 M3×8 进 4)
assert LS.Z0 < BAR_SCR_BEAR + BAR_SCR_L <= LS.Z0 + LS.BAR_TAP_H

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
    rep = dict(z=dict(fr4=(Z_F0, Z_F1), cavity=(Z_F1, Z_T0), tray=(Z_T0, Z_TOP), screen_fr4=(SP_Z0, SP_Z1), post=(SP_Z1, LS.Z0)),
               vol=dict(fr4=round(vol(fr4), 1), rim=round(vol(rim), 1), screen_fr4=round(vol(screen_fr4_loc), 1), post=round(vol(screen_post_loc), 1)),
               mass_g=dict(fr4=round(vol(fr4) * 1.85e-3, 1), rim_PLA=round(vol(rim) * 1.24e-3, 1), screen_fr4_each=round(vol(screen_fr4_loc) * 1.85e-3, 2),
                           post_PETG_each=round(vol(screen_post_loc) * 1.27e-3, 2)),
               valid=dict(rim=BRepCheck_Analyzer(rim).IsValid(), fr4=BRepCheck_Analyzer(fr4).IsValid(), screen_fr4=BRepCheck_Analyzer(screen_fr4_loc).IsValid(),
                          post=BRepCheck_Analyzer(screen_post_loc).IsValid()),
               solids=dict(rim=len(solids(rim)), screen_fr4=len(solids(screen_fr4_loc)), post=len(solids(screen_post_loc))),
               lock=dict(r=SHR_LOCK_R, ang=SHR_LOCK_ANG, pts=[(round(x, 2), round(y, 2)) for x, y in SHR_LOCK_PTS],
                         loc=SHR_LOCK_LOC, gap=SHR_GAP, screw=f'M3×{SHR_SCR_L:g} 超薄头 支承 Z{SHR_SCR_BEAR:g} 尾 Z{SHR_SCR_BEAR + SHR_SCR_L:g}, 法兰螺母坐罩耳顶',
                         out_screw=f'M3×{OUT_SCR_L:g} 超薄头 支承 Z{OUT_SCR_BEAR:g} 尾 Z{OUT_SCR_BEAR + OUT_SCR_L:g}, 法兰螺母坐屏幕玻纤板顶 Z{OUT_NUT_Z[0]:g}–{OUT_NUT_Z[1]:g}'),
               screen_fr4_outline=dict(x=(SP_X0, SP_X1), hy=SP_HY, r_clip=SP_R1, edge=SP_EDGE))
    others = dict(底板=VB['baseboard'], 底板器件=VB['bb_parts'], CZ06=VB['cz06'], 灯板=VB['led'], 夹条=LS.bar_s, 顶部件=LS.top,
                  无线托盘=WH.H, 无线模块=WH.module, FPC_A=_fpc['fpc_a_v1_2'], FPC_B=_fpc['fpc_b_v1_2'], 桥板A=_fpc['bridge_a_v1_2'], 桥板B=_fpc['bridge_b_v1_2'], FPC座=_fpc['bb_fpc_seats_v1_2'], 电机=B.motor, 定子盘=B.flange_disc, 安装法兰=B.mounting_flange, 线圈环=B.ring)
    mine = dict(玻纤板=fr4, 承载盘=rim, 线圈=coil, **{n.split(' ')[0] + n.split(' ')[-1]: sh for n, sh, _ in SCREEN_PARTS})
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


def export_screen_fr4_dxf():
    """外协 CNC 用 2D: 外形 + 通孔 + 沉孔 (单独图层 CBORE, 文字注深度)。坐标 = 板放 0° 时世界 xy (轴心原点)。"""
    import ezdxf
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    for ly, col in (('OUTLINE', 7), ('HOLES', 1), ('CBORE', 3), ('TEXT', 2)): doc.layers.add(ly, color=col)
    # 外形 (11-20 晚 长方形): 内边 x66 直线 + 上下边 |y|=35 直线 + 外角 r81.7 圆弧 (圆心 = 轴心) + 外边 x81.2 直线 (|y|≤9.0)
    xa = math.sqrt(SP_R1 ** 2 - SP_HY ** 2); ya = math.sqrt(SP_R1 ** 2 - SP_X1 ** 2)
    aa, ab = math.degrees(math.atan2(SP_HY, xa)), math.degrees(math.atan2(ya, SP_X1))
    L = dict(dxfattribs=dict(layer='OUTLINE'))
    msp.add_line((SP_X0, -SP_HY), (SP_X0, SP_HY), **L)
    msp.add_line((SP_X0, SP_HY), (xa, SP_HY), **L); msp.add_line((SP_X0, -SP_HY), (xa, -SP_HY), **L)
    msp.add_arc((0, 0), SP_R1, ab, aa, **L); msp.add_arc((0, 0), SP_R1, -aa, -ab, **L)
    msp.add_line((SP_X1, -ya), (SP_X1, ya), **L)
    for x, y in SP_HOLES_LOC['out'] + SP_HOLES_LOC['scr']:
        msp.add_circle((x, y), 1.7, dxfattribs=dict(layer='HOLES'))
    for x, y in SP_PIN_LOC:
        msp.add_circle((x, y), PIN_HOLE_D / 2, dxfattribs=dict(layer='HOLES'))
    for x, y in SHR_LOCK_LOC:
        msp.add_circle((x, y), SHR_HOLE_D / 2, dxfattribs=dict(layer='HOLES'))
    for x, y in SP_HOLES_LOC['scr'] + SHR_LOCK_LOC:
        msp.add_circle((x, y), SP_CB_D / 2, dxfattribs=dict(layer='CBORE'))
        msp.add_text(f'底面沉孔 %%c{SP_CB_D:g} 深{SP_CB_H:g}', height=1.2, dxfattribs=dict(layer='TEXT')).set_placement((x - 9.5, y + (4.2 if y > 0 else -5.4)))
    msp.add_text(f'screen_fr4_v1_2b  FR4 无铜 厚{SP_T:g}  数量 4  孔: 4x%%c3.4 通 / 5x%%c{SHR_HOLE_D:g} 通 (销孔 3 + 罩锁 2) / 4x 底面沉孔 %%c{SP_CB_D:g}x{SP_CB_H:g} (夹条 2 + 罩锁 2)  未注公差 ±0.1',
                 height=1.5, dxfattribs=dict(layer='TEXT')).set_placement((40, -50))
    d = B.V12 / 'models' / 'screen_fr4_v1_2b'; d.mkdir(parents=True, exist_ok=True)
    doc.saveas(d / 'screen_fr4_v1_2b.dxf')
    return d / 'screen_fr4_v1_2b.dxf'


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
    out('screen_fr4_v1_2b', screen_fr4_loc, color='#C9B458')               # 玻纤板 (外协 CNC; STEP/STL 为放 0° 的装配位, _print 落床); DXF 见 export_screen_fr4_dxf()
    out('screen_post_v1_2b', post_a, color='#F1C232')                      # 侧立件 (+x 装配位; −x 同件转 180°)
    export_screen_fr4_dxf()
    write_doc([('fr4_plate_v1_2b (装配位)', fr4, '#C9B458', None, False), ('rim_ring_v1_2b', rim, '#6AA84F', None, False),
               *[(n, sh, c, None, False) for n, sh, c in SCREEN_PARTS],
               ('线圈 (占位)', coil, '#D9822B', None, False)], B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step', 'rotor_b')
    (B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出', OUTD)
