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
  (11-21 起) 屏幕支撑件 = PETG 打印 ×4, 两种件, Z30.5 (承载盘顶) → 灯板下沿 LS.Z0 (灯板 +1 后 38.5, 高 8):
      A 屏幕支架件 screen_sup_a_v1_2b ×2 (0°/180° 同件) 托灯板/夹条; B 上下件 screen_sup_b_v1_2b ×2 (90°/270° 同件)
      取代 屏幕玻纤板 screen_fr4_v1_2b ×4 + 侧立件 screen_post_v1_2b ×2 (11-20, 产物移 转子盘B/作废_11-21/)
光电对射 (11-23): 通光孔 Φ3.2 @ r77.5 90° 穿承载盘 (fr4_plate 现场配钻); 接收板 (0603 光敏管 + 电阻, 朝下) 嵌 B 件底面槽, 3 芯焊线沿件底线槽到件内边 → 底板 J9 (参数 OPT_* / RX_*)
螺丝 (全部在桌上装好再上电机):
  - 屏幕螺丝 2× M3 超薄头 (长度按铜螺柱 Z 自动选, 现 M3×18): 从 A 件底面 Φ7.6×1.5 沉孔往上 (支承 Z32) 穿 A 件 → 中缝 → 拧进灯板 F 面每端下颗铜螺柱
  - 16 颗从 fr4_plate 底往上 (头埋 Φ7.2×1.5 沉孔, 支承 Z23): 内圈 R34 ×8 → 承载盘顶面 Φ8×3.7 沉孔 M3 法兰螺母 (M3×7);
    外圈 r77.5 @22.5+45k ×8 → 穿承载盘 + 支撑件, 法兰螺母嵌在支撑件顶面六角窝 (法兰朝上, 顶低于件顶 0.3), M3×15 尾低于件顶 0.5
  - 罩子锁点 ×8 (11-21 用户「罩子还是用螺丝向下锁 螺母嵌在这个支撑件上」): DIN912 M3×12 从罩耳顶往下, 穿罩耳 → 支撑件,
    拧进 倒扣嵌在支撑件底面六角窝的 M3 法兰螺母 (法兰朝下, 支撑件压在承载盘上螺母掉不出来); 承载盘 / fr4_plate 不开孔;
    A 件本地 (61, ±30.5) (用户图), B 件本地 (73, ±19.5)
    (之前 11-20 夜: M3×10 超薄头从屏幕玻纤板底往上, 罩耳顶法兰螺母; 再之前外圈 M3×18 / ±14° 承载盘窝 —— 均作废)
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
# 罩子锁点 / 外圈螺丝 / 屏幕螺丝 参数见下面「屏幕支撑件」段 (11-21 改 PETG 打印支撑件 ×4, 罩锁从上往下进嵌入式法兰螺母)
H_Z1 = LS.Z0                                      # 37.0 = 灯板下沿 = 横杆顶
MOT_CB_H = Z_TOP - 27.0                           # 3.5: 电机螺丝头支承仍 Z27 (M3×10 进电机 4.5 不变), 头顶 Z30 低于盘顶 0.5
# FPC B 从桥板 B 下沿过转轴到底板 J6, 原实测最低 Z30.6 (x±17.75, y −14.26…6.74), 比盘顶 Z32 低 ⇒ 原托盘顶面开让位槽; 11-18 改灯板抬 2 (FPC 最低 Z31.1, 盘顶 30.5) (V1.2 原承载盘中心是 Φ50 通孔, 自然让开)
FPC_POCKET = None                                  # 11-18 用户「不需要, 取消吧」: 取消让位槽 (原 (-18.5, -15.0, 18.5, 7.5, 30.0) x0,y0,x1,y1,槽底Z); 电机沉孔深 5 保留 (螺丝不变)
# ---- 11-23 光电对射 (转速/零位): 发射管在定子盘朝上, 接收管在转子朝下 (B 件 @90° 底面小板槽) ----
# 用户: 通光孔与外圈 8 孔同半径 r77.5, 放 90° ⇒ 世界 (0, 77.5); 「电路板尽量小, 接插件待确认」⇒ 接收板最小 (只 0603 光敏管 + 0603 电阻), 暂按焊线出线。
#   以下全是参数, 接插件定了改这里即可 (槽 / 深 / 线槽都由它推出)。
OPT_ANG, OPT_R, OPT_D = 90.0, R_OUT, 3.4          # 通光孔: 角度 / 半径 / 直径 (承载盘全厚通; fr4_plate 现场配钻; 11-23 用户: 与 M3 通孔同 Φ3.4 一个钻头)
RX_PCB_L, RX_PCB_W, RX_PCB_T = 4.0, 3.0, 1.0      # 接收板 长 (沿径向) × 宽 (切向) × 厚, FR4
RX_PT_DX = 1.0                                    # 光敏管中心离板中心 (沿径向, + = 朝外); 电阻在内侧半边 ⇒ 板中心 = 孔心 − RX_PT_DX
RX_CLR = 0.5                                      # 槽每边余量 (槽 = 板 + 2×0.5)
RX_DEV_H = 0.7                                    # 板底面器件高 (0603 光敏管 / 电阻, 朝下; 器件底 ≈ 承载盘顶)
RX_TOP_H = 1.0                                    # 板顶焊点 / 线头余量
RX_SLOT_H = RX_DEV_H + RX_PCB_T + RX_TOP_H        # 2.7 槽深 (从件底往上)
RX_EXIT = 'wire'                                  # 出线方式: 'wire' = 3 芯焊线沿件底线槽到件内边 (→ 底板 DR1M90 J9 焊盘, 世界约 (41.5, 39)); 接插件定了再加分支
RX_WIRE_W, RX_WIRE_H = 2.5, 2.0                   # 线槽 宽 × 深 (件底面开口)
RX_POCKET_WALL = 1.5                              # 槽 / 线槽 ↔ 顶面减重槽 水平壁

# ---------------- 玻纤板 (装配体, 与 models/fr4_plate_v1_2b/build.py 同参数) ----------------
fr4 = cyl(0, 0, FR4_OD, Z_F0, Z_F1)
for x, y in IN_PTS + ANCHOR_PTS + OUT_NUT_PTS:
    fr4 = cut(fr4, cyl(x, y, 3.2, Z_F0 - 1, Z_F1 + 1), cyl(x, y, 7.2, Z_F0 - 1, Z_F0 + 1.5))
fr4 = clean(cut(fr4, *[cyl(x, y, 3.2, Z_F0 - 1, Z_F1 + 1) for x, y in MOT_PTS], cyl(0, 0, CENTER_D, Z_F0 - 1, Z_F1 + 1)))
OPT_PT = pol(OPT_R, OPT_ANG)                       # (0, 77.5) 光电通光孔
# 11-23 光电通光孔 Φ3.2: 只在装配体里体现 —— 现场配钻 (用户用台钻以承载盘为钻模配钻), 板厂文件 models/fr4_plate_v1_2b/build.py 不改
fr4 = clean(cut(fr4, cyl(*OPT_PT, OPT_D, Z_F0 - 1, Z_F1 + 1)))

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
cuts.append(cyl(*OPT_PT, OPT_D, Z_F0 - 1, Z_TOP + 1))                # 11-23 光电通光孔 Φ3.4 全厚通 (兼 fr4_plate 现场配钻钻模)
# 罩子锁点不在承载盘上开孔 (11-20 夜 只在屏幕玻纤板上; 原承载盘顶面六角法兰螺母窝 LOCK_POCKET 已删, 17:4x 用户「这里不需要孔」)
rim = clean(cut(rim, *cuts))

# ---------------- 11-21 屏幕支撑件 = PETG 打印 ×4 (两种件), 取代 屏幕玻纤板 ×4 + 侧立件 ×2 ----------------
# 用户 11-20 夜 原话: 「既然无法兼容，屏幕支架和这个，做两个，屏幕支架改一下」「所有的这个固定我们改一下，反扣一个法兰螺母在这里」
#   「罩子还是用螺丝向下锁 螺母嵌在这个支撑件上，我们还是用3d打印方式做」「我们留4mm给这个件在屏幕下边厚度」
#   「锁罩子是另一回事，我们要把这个法兰螺母嵌入到这个支撑件里面，这样罩子安装就很灵活」
# 高度 = 承载盘顶 Z_TOP → 灯板下沿 LS.Z0 (灯板 +1 后 30.5 → 38.5 = 8), 不写死。
#   A 屏幕支架件 screen_sup_a_v1_2b ×2 (0° / 180°, 同件转 180°): 托灯板/夹条; 屏幕螺丝从本件底往上拧灯板铜螺柱; 罩锁点挪到本地 (61, ±30.5) (用户图上 (±61, ±30.5))
#   B 上下件     screen_sup_b_v1_2b ×2 (90° / 270°, 同件): 不托灯板, 罩锁点保持本地 (73, ±19.5)
# 罩锁 ×8: 螺丝从上往下 (DIN912 M3 内六角圆柱头, 头坐罩耳顶), 穿罩耳 → 拧进 倒扣嵌在支撑件底面的 M3 法兰螺母 (法兰朝下, 从件底压进六角窝,
#   拧紧时六角顶顶在窝顶打印料上; 支撑件压在承载盘上螺母掉不出来); 承载盘不开孔; 尾离承载盘顶 SHR_TIP_CLR
# 外圈 8 颗 (r77.5 @22.5+45k): 仍从 fr4_plate 底往上穿 承载盘 → 支撑件, 法兰螺母改嵌在支撑件顶面 (法兰朝上, 六角窝止转, 顶低于件顶 0.3, 罩耳可直接盖过去);
#   法兰窝外侧离件外缘只剩 0.1 ⇒ 法兰窝朝外开口 (U 形, 罩壁内面离螺母 ≥0.7)
SP_Z0 = Z_TOP                                     # 30.5 支撑件底 = 承载盘顶
SP_Z1 = LS.Z0                                     # 38.5 支撑件顶 = 灯板下沿 (跟灯板走)
SP_T = round(SP_Z1 - SP_Z0, 3)                    # 8
assert SP_T >= 4.0, SP_T                          # 用户「留4mm给这个件在屏幕下边厚度」
SP_R1 = LS.R_CLIP                                 # 81.7 外缘 (以轴心为圆心; 罩壁内面 r82)
SP_X1 = 81.2                                      # 外边直线段 (两种件同)
SP_ANG = (0.0, 90.0, 180.0, 270.0)
SP_TYPE = {0.0: 'a', 90.0: 'b', 180.0: 'a', 270.0: 'b'}
SP_HOLE_A = (22.5, -22.5)                         # 外圈螺丝 (承载盘 r77.5 @22.5+45k 全 8 颗都穿支撑件)
# A 件外形: 主体 x66–81.2 × |y|≤37 ∩ r81.7 + 内伸翼 x54.5–66 × 22≤|y|≤37 (包住罩锁螺母窝, 壁 ≥2.4); B 件: x66.5–81.2 × |y|≤35 ∩ r81.7
SP_A_X0, SP_A_HY, SP_A_WING = 66.0, 37.0, (54.5, 22.0)     # 翼 x0 / 翼内边 |y|
SP_B_X0, SP_B_HY = 66.5, 35.0                     # 66 → 66.5: 放 90° 时内边 y66 离 CZ06 包络 (y≤65.82, Z35.1–41.7) 只 0.18 (件变高 8 后 Z 重叠); 放 270° 离无线夹块 2.9
SP_X0, SP_HY = SP_A_X0, SP_A_HY                   # 兼容旧名
LOCK_A_LOC = [(61.0, 30.5), (61.0, -30.5)]        # A 件罩锁 (用户图上量 (±61, ±30.5), r68.20; 原 (73, ±19.5) 在 A 件上删 —— 原 −x 端套筒 Φ9 离灯板B 0.33)
SHR_LOC_X, SHR_LOC_Y = 73.0, 19.5                 # B 件罩锁 (保持)
LOCK_B_LOC = [(SHR_LOC_X, SHR_LOC_Y), (SHR_LOC_X, -SHR_LOC_Y)]
SHR_LOCK_SET = {a: (LOCK_A_LOC if SP_TYPE[a] == 'a' else LOCK_B_LOC) for a in SP_ANG}
# 屏幕螺丝 (A 件): 灯板铜螺柱 x=±78.88, 放 0° 用局部 (78.88, −4.89), 放 180° 用 (78.88, +4.49) ⇒ 孔 Φ3.4 腰形 中心 ±4.69 沿 y ±0.2 (两个孔都开, 同件), 底面沉孔 Φ7.6
SP_SCR_X, SP_SCR_DY = LS.SO_X, abs(LS.ECC)
SP_SCR_SL = LS.SO_YL                              # 腰形半长 0.2
SP_SCR_CB_D = 7.2 + 2 * SP_SCR_SL                 # 7.6 (外缘 x82.68 破出件外边 1.48, 该处罩壁是两端竖缝)
SP_CB_H = 1.5                                     # 屏幕螺丝底面沉孔深 (超薄头 Φ7×1.2~1.5; 用户说 ≈2, 但 2 深时 M3×16 吃牙 2.8 / M3×18 尾顶上颗 ⇒ 1.5, 见 BAR_SCR_*)
SP_CB_D = 7.2                                     # 兼容旧名
# 法兰螺母 (同 fasteners_v1_2: 法兰 Φ7.6×1.0, 六角对边 5.9, 总高 3.7) 的窝 (参考 cap_clamp cap-c NUT_HEX_WELL: 六角窝 AF6.1 + 法兰窝 Φ8.2)
NUT_FL_D, NUT_FL_H, NUT_AF, NUT_T = 7.6, 1.0, 5.9, 3.7
WELL_FL_D, WELL_FL_H = 8.2, 1.1                   # 法兰窝 Φ8.2 × 1.1 (法兰 1.0 + 0.1)
WELL_AF_LOCK = 6.0                                # 罩锁螺母 (从件底压进, 倒放): 六角窝对边 6.0 (单边 0.05 轻压, 拿起支撑件时螺母不掉; 打印孔偏小时用烙铁/锉刀修)
WELL_AF_OUT = 6.1                                 # 外圈螺母 (从件顶放进, 重力在下): 对边 6.1
WELL_TOP_CLR = 0.1                                # 罩锁螺母六角顶 ↔ 窝顶 (拧紧后贴死)
LOCK_NUT_Z = (SP_Z0, SP_Z0 + NUT_T)               # 30.5–34.2 法兰朝下坐承载盘顶
OUT_NUT_TOP = SP_Z1 - 0.3                         # 外圈螺母顶低于件顶 0.3
OUT_NUT_Z = (OUT_NUT_TOP - NUT_T, OUT_NUT_TOP)    # 34.5–38.2
# 罩锁螺丝: DIN912 M3 内六角圆柱头 (头 Φ5.5×3, 2.5 内六角, 起子 Φ6 包络) 从罩耳顶往下; 罩耳厚按选定长度反推, 尾离承载盘顶 SHR_TIP_CLR
SHR_SCR_L, SHR_TIP_CLR = 12.0, 0.5
SHR_SCR_TIP = SP_Z0 + SHR_TIP_CLR                 # 31.0 (吃螺母 34.2 − 31.0 = 3.2; 承载盘顶不开孔所以吃不满 3.7)
SHR_SCR_BEAR = SHR_SCR_TIP + SHR_SCR_L            # 43.0 = 罩耳顶
SHR_EAR_T = round(SHR_SCR_BEAR - SP_Z1, 3)        # 4.5
assert 3.5 <= SHR_EAR_T <= 6.0, SHR_EAR_T
SHR_ENG = round(LOCK_NUT_Z[1] - SHR_SCR_TIP, 2)
assert SHR_ENG >= 3.0, SHR_ENG
SHR_HEAD_D, SHR_HEAD_H = 5.5, 3.0
SHR_HOLE_D = 3.4
# 外圈螺丝 M3 超薄头 从 fr4_plate 底 (支承 Z23) 往上: 选最长的标准长度使尾 ≤ 件顶 −0.3 (罩耳盖在上面), 吃螺母 ≥3
OUT_SCR_BEAR = Z_F0 + 1.5                         # 23.0
OUT_SCR_L = max(L for L in (10, 12, 14, 15, 16, 18, 20) if OUT_SCR_BEAR + L <= SP_Z1 - 0.3)
OUT_ENG = round(OUT_SCR_BEAR + OUT_SCR_L - OUT_NUT_Z[0], 2)
assert OUT_ENG >= 3.0, (OUT_SCR_L, OUT_ENG)
# 屏幕螺丝 M3 超薄头 从 A 件底沉孔往上 (支承 Z_TOP + SP_CB_H), 拧进每端下颗铜螺柱: 吃牙 ≥3, 尾离上颗底 ≥0.5
BAR_SCR_BEAR = SP_Z0 + SP_CB_H                    # 32.0
BAR_SCR_L = float(min(L for L in (12, 14, 16, 18, 20, 22) if BAR_SCR_BEAR + L - LS.SO_Z0 >= 3.0))
BAR_SCR_ENG = round(BAR_SCR_BEAR + BAR_SCR_L - LS.SO_Z0, 2)
assert 3.0 <= BAR_SCR_ENG and BAR_SCR_BEAR + BAR_SCR_L <= LS.SO_Z1 - 0.5, (BAR_SCR_L, BAR_SCR_ENG)
BAR_SCR_PTS = list(LS.SO_PTS)                     # 世界: (78.88, ECC−0.2) 板B 下颗 / (−78.88, ECC+0.2) 板A 下颗
# 减重 (动平衡 / 惯量): 顶面开口盲槽, 槽底留 SP_POCKET_FLOOR; 不在灯板/夹条正下方、不在罩耳下、离孔/螺母窝 ≥2
SP_POCKET_FLOOR = 3.0
SP_POCKETS = {'a': [(68.0, 12.5, 76.5, 23.5), (68.0, -23.5, 76.5, -12.5)],     # (x0, y0, x1, y1) 局部
              'b': [(68.5, -13.4, 77.5, 13.4)]}
# 11-23 B 件底面接收板槽 (局部 = 放 0°; B 件装 90° 时局部 (OPT_R, 0) = 世界通光孔; 270° 那个同件, 下面没孔)
RX_X0 = OPT_R - RX_PT_DX - RX_PCB_L / 2 - RX_CLR  # 74.0
RX_X1 = OPT_R - RX_PT_DX + RX_PCB_L / 2 + RX_CLR  # 79.0
RX_HY = RX_PCB_W / 2 + RX_CLR                     # 2.0
RX_Z1 = SP_Z0 + RX_SLOT_H                         # 33.2 槽顶
assert SP_TYPE[(OPT_ANG + 360) % 360] == 'b'
if RX_HY + RX_POCKET_WALL > 0:                    # B 件减重槽在中间劈开, 让出接收板槽 + 线槽 (槽顶 33.2 vs 减重槽底 33.5 只差 0.3)
    _hy = max(RX_HY, RX_WIRE_W / 2) + RX_POCKET_WALL
    SP_POCKETS['b'] = [(x0, y0, x1, y1) for X0, Y0, X1, Y1 in SP_POCKETS['b'] for (x0, y0, x1, y1) in ((X0, _hy, X1, Y1), (X0, Y0, X1, -_hy)) if y1 - y0 > 1.0]
def rx_cuts():
    c = [gbox(RX_X0, -RX_HY, SP_Z0 - 1, RX_X1, RX_HY, RX_Z1)]
    if RX_EXIT == 'wire':                         # 线槽沿件底 −x (朝轴心) 通出内边
        c.append(gbox(SP_B_X0 - 1, -RX_WIRE_W / 2, SP_Z0 - 1, RX_X0 + 0.01, RX_WIRE_W / 2, SP_Z0 + RX_WIRE_H))
    return c

def _rot(p, a): c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c)
SHR_LOCK_PTS = sorted([_rot(p, a) for a in SP_ANG for p in SHR_LOCK_SET[a]], key=lambda p: math.atan2(p[1], p[0]) % (2 * math.pi))   # 世界 8 点
SHR_LOCK_ANG = tuple(round(math.degrees(math.atan2(y, x)) % 360, 3) for x, y in SHR_LOCK_PTS)
SHR_LOCK_R = {k: round(math.hypot(*L[0]), 3) for k, L in (('a', LOCK_A_LOC), ('b', LOCK_B_LOC))}   # a 68.20 / b 75.56
SP_HOLES_LOC = dict(out=[pol(R_OUT, a) for a in SP_HOLE_A], scr=[(SP_SCR_X, SP_SCR_DY), (SP_SCR_X, -SP_SCR_DY)], lock_a=LOCK_A_LOC, lock_b=LOCK_B_LOC,
                    lock=LOCK_B_LOC)              # lock: 兼容旧名

def _hexp(x, y, af, z0, z1, ang=0.0):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    rc = af / math.sqrt(3); pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        t = math.radians(ang + 30 + 60 * k); pg.Add(gp_Pnt(x + rc * math.cos(t), y + rc * math.sin(t), z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()

def _slot(x, y, z0, z1, d=3.4, hl=SP_SCR_SL):
    """沿 y 的腰形孔 (中心 (x, y), 半长 hl)"""
    return fuse(cyl(x, y - hl, d, z0, z1), cyl(x, y + hl, d, z0, z1), gbox(x - d / 2, y - hl, z0, x + d / 2, y + hl, z1))

def lock_nut_well(x, y):
    """罩锁: 件底面倒扣法兰螺母窝 (法兰窝 Φ8.2×1.1 + 六角窝 AF6.0 到 螺母顶 +0.1) + Φ3.4 通"""
    return fuse(cyl(x, y, WELL_FL_D, SP_Z0 - 1, SP_Z0 + WELL_FL_H), _hexp(x, y, WELL_AF_LOCK, SP_Z0 + WELL_FL_H - 0.01, LOCK_NUT_Z[1] + WELL_TOP_CLR, math.degrees(math.atan2(y, x))),
                cyl(x, y, SHR_HOLE_D, SP_Z0 - 1, SP_Z1 + 1))

def out_nut_well(x, y):
    """外圈: 件顶面法兰螺母窝 (法兰朝上; 六角窝 AF6.1 平边朝径向 + 法兰窝 Φ8.2 往外开口到件外) + Φ3.4 通"""
    a = math.degrees(math.atan2(y, x)); zf = OUT_NUT_Z[1] - NUT_FL_H - 0.1     # 法兰支承台阶
    fl = fuse(cyl(x, y, WELL_FL_D, zf, SP_Z1 + 1), xf(gbox(math.hypot(x, y), -WELL_FL_D / 2, zf, SP_R1 + 2, WELL_FL_D / 2, SP_Z1 + 1), rotz(a)))
    return fuse(fl, _hexp(x, y, WELL_AF_OUT, OUT_NUT_Z[0] - 0.1, zf + 0.01, a), cyl(x, y, 3.4, SP_Z0 - 1, SP_Z1 + 1))

def screen_sup_local(kind):
    """kind 'a' = 屏幕支架件 (放 0°/180°), 'b' = 上下件 (放 90°/270°); 局部 = 放 0° 时的世界坐标"""
    clip = cyl(0, 0, 2 * SP_R1, SP_Z0 - 1, SP_Z1 + 1)
    if kind == 'a':
        s = fuse(gbox(SP_A_X0, -SP_A_HY, SP_Z0, SP_X1, SP_A_HY, SP_Z1),
                 gbox(SP_A_WING[0], SP_A_WING[1], SP_Z0, SP_A_X0 + 0.01, SP_A_HY, SP_Z1), gbox(SP_A_WING[0], -SP_A_HY, SP_Z0, SP_A_X0 + 0.01, -SP_A_WING[1], SP_Z1))
        locks = LOCK_A_LOC
    else:
        s = gbox(SP_B_X0, -SP_B_HY, SP_Z0, SP_X1, SP_B_HY, SP_Z1); locks = LOCK_B_LOC
    s = _ocm(s, clip)
    cuts = [out_nut_well(x, y) for x, y in SP_HOLES_LOC['out']] + [lock_nut_well(x, y) for x, y in locks]
    if kind == 'a':
        cuts += [_slot(x, y, SP_Z0 - 1, SP_Z1 + 1) for x, y in SP_HOLES_LOC['scr']] + [cyl(x, y, SP_SCR_CB_D, SP_Z0 - 1, SP_Z0 + SP_CB_H) for x, y in SP_HOLES_LOC['scr']]
    cuts += [gbox(x0, y0, SP_Z0 + SP_POCKET_FLOOR, x1, y1, SP_Z1 + 1) for x0, y0, x1, y1 in SP_POCKETS[kind]]
    if kind == 'b': cuts += rx_cuts()             # 11-23 底面接收板槽 + 线槽
    return clean(cut(s, *cuts))

screen_sup_a_loc = screen_sup_local('a')
screen_sup_b_loc = screen_sup_local('b')
SCR_SUP = [_rz(screen_sup_a_loc if SP_TYPE[a] == 'a' else screen_sup_b_loc, a) for a in SP_ANG]   # 0° (+x) / 90° (+y) / 180° (−x) / 270° (−y)
SCR_FR4 = SCR_SUP                                 # 兼容旧名 (fpc_v1_2 / group_asm 等)
post_a, post_b = SCR_SUP[0], SCR_SUP[2]           # 兼容旧名 (原侧立件 +x / −x; 现 = A 件两个装配位)
screen_fr4_loc, screen_post_loc = screen_sup_a_loc, screen_sup_b_loc   # 兼容旧名 (图纸旧段)
SCREEN_PARTS = [(f'屏幕支撑件 {"A screen_sup_a_v1_2b" if SP_TYPE[a] == "a" else "B screen_sup_b_v1_2b"} @{a:g}°', sh, '#F1C232' if SP_TYPE[a] == 'a' else '#C9B458')
                for a, sh in zip(SP_ANG, SCR_SUP)]
SCREEN_KEYS = ['scr_sup_0', 'scr_sup_90', 'scr_sup_180', 'scr_sup_270']   # 校核用短名

def _edge(kind, x, y, rh):
    """孔 (半径 rh) 到件外形的最小边距 (近似: 直边 + r81.7)"""
    if kind == 'a':
        x0 = SP_A_WING[0] if abs(y) >= SP_A_WING[1] else SP_A_X0
        return min(x - rh - x0, SP_X1 - x - rh, SP_A_HY - abs(y) - rh, SP_R1 - math.hypot(x, y) - rh)
    return min(x - rh - SP_B_X0, SP_X1 - x - rh, SP_B_HY - abs(y) - rh, SP_R1 - math.hypot(x, y) - rh)
SP_EDGE = dict(a_lock_well=round(min(_edge('a', x, y, WELL_FL_D / 2) for x, y in LOCK_A_LOC), 2),
               b_lock_well=round(min(_edge('b', x, y, WELL_FL_D / 2) for x, y in LOCK_B_LOC), 2),
               out_hex=round(min(_edge('a', x, y, WELL_AF_OUT / 2) for x, y in SP_HOLES_LOC['out']), 2),   # 六角平边朝外
               scr_hole=round(min(_edge('a', x, y, 1.7) for x, y in SP_HOLES_LOC['scr']), 2),
               lock_out_a=round(min(math.dist(p, q) for p in LOCK_A_LOC for q in SP_HOLES_LOC['out']) - WELL_FL_D, 2),   # 罩锁窝 ↔ 外圈窝 壁 (不同 Z, 保守)
               lock_out_b=round(min(math.dist(p, q) for p in LOCK_B_LOC for q in SP_HOLES_LOC['out']) - WELL_FL_D, 2))
def _d_rect(x, y, x0, y0, x1, y1): return math.dist((min(max(x, x0), x1), min(max(y, y0), y1)), (x, y))
_pk = SP_POCKETS['b']; _pky = min(min(abs(y0), abs(y1)) for _, y0, _, y1 in _pk)
RX_WALL = dict(槽外端_件外边=round(min(SP_X1, math.sqrt(SP_R1 ** 2 - RX_HY ** 2)) - RX_X1, 2),
               槽_减重槽=round(_pky - RX_HY, 2), 线槽_减重槽=round(_pky - RX_WIRE_W / 2, 2),
               槽_罩锁窝=round(min(_d_rect(x, y, RX_X0, -RX_HY, RX_X1, RX_HY) for x, y in LOCK_B_LOC) - WELL_FL_D / 2, 2),
               线槽_罩锁窝=round(min(_d_rect(x, y, SP_B_X0, -RX_WIRE_W / 2, RX_X0, RX_WIRE_W / 2) for x, y in LOCK_B_LOC) - WELL_FL_D / 2, 2),
               槽_外圈螺丝孔=round(min(_d_rect(x, y, RX_X0, -RX_HY, RX_X1, RX_HY) for x, y in SP_HOLES_LOC['out']) - 3.4 / 2, 2),
               线槽_外圈螺丝孔=round(min(_d_rect(x, y, SP_B_X0, -RX_WIRE_W / 2, RX_X0, RX_WIRE_W / 2) for x, y in SP_HOLES_LOC['out']) - 3.4 / 2, 2),
               槽顶_件顶=round(SP_Z1 - RX_Z1, 2), 线槽顶_件顶=round(SP_Z1 - SP_Z0 - RX_WIRE_H, 2))
assert min(v for v in RX_WALL.values()) >= 1.2, RX_WALL
# 承载盘通光孔 Φ3.2 @ (0, 77.5) 壁厚: 线圈腔外壁 r72.5 / 外缘 r85 / fr4_plate 外缘 r82.5 / 其它孔
_oh = [(x, y, 3.4) for x, y in IN_PTS + ANCHOR_PTS + OUT_NUT_PTS + list(B.BB_HOLES) + list(B.MOD_HOLES)] + [(x, y, 3.2) for x, y in MOT_PTS] + [(x, y, B.AC_HOLE_D + 0.4) for x, y in B.AC_HOLES]
OPT_WALL = dict(腔外壁=round(OPT_R - OPT_D / 2 - COIL_R1, 2), 盘外缘=round(RIM_R - OPT_R - OPT_D / 2, 2), fr4外缘=round(FR4_OD / 2 - OPT_R - OPT_D / 2, 2),
                最近孔=round(min(math.dist(OPT_PT, (x, y)) - OPT_D / 2 - d / 2 for x, y, d in _oh), 2),
                底板让位窝=round(min(math.dist(OPT_PT, p) for p in B.BB_HOLES) - OPT_D / 2 - BB_CB_D / 2, 2))
assert SP_EDGE['a_lock_well'] >= 2.0 and SP_EDGE['b_lock_well'] >= 2.0 and SP_EDGE['scr_hole'] >= 0.5 and SP_EDGE['out_hex'] >= 1.0, SP_EDGE

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
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    def _mc(sh, rho):
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(sh, g); c = g.CentreOfMass(); m = g.Mass() * rho
        return dict(m=round(m, 2), c=(round(c.X(), 2), round(c.Y(), 2), round(c.Z(), 2)))
    U = [0.0, 0.0]
    for sh in SCR_SUP:
        d = _mc(sh, 1.27e-3); U[0] += d['m'] * d['c'][0]; U[1] += d['m'] * d['c'][1]
    rep = dict(z=dict(fr4=(Z_F0, Z_F1), cavity=(Z_F1, Z_T0), tray=(Z_T0, Z_TOP), sup=(SP_Z0, SP_Z1), sup_h=SP_T),
               vol=dict(fr4=round(vol(fr4), 1), rim=round(vol(rim), 1), sup_a=round(vol(screen_sup_a_loc), 1), sup_b=round(vol(screen_sup_b_loc), 1)),
               mass_g=dict(fr4=round(vol(fr4) * 1.85e-3, 1), rim_PLA=round(vol(rim) * 1.24e-3, 1), sup_a_PETG_solid=round(vol(screen_sup_a_loc) * 1.27e-3, 2),
                           sup_b_PETG_solid=round(vol(screen_sup_b_loc) * 1.27e-3, 2)),
               sup_com=dict(a=_mc(screen_sup_a_loc, 1.27e-3), b=_mc(screen_sup_b_loc, 1.27e-3), U4_gmm=round(math.hypot(*U), 3)),
               valid=dict(rim=BRepCheck_Analyzer(rim).IsValid(), fr4=BRepCheck_Analyzer(fr4).IsValid(), sup_a=BRepCheck_Analyzer(screen_sup_a_loc).IsValid(),
                          sup_b=BRepCheck_Analyzer(screen_sup_b_loc).IsValid()),
               solids=dict(rim=len(solids(rim)), sup_a=len(solids(screen_sup_a_loc)), sup_b=len(solids(screen_sup_b_loc))),
               lock=dict(r=SHR_LOCK_R, ang=SHR_LOCK_ANG, pts=[(round(x, 2), round(y, 2)) for x, y in SHR_LOCK_PTS], loc_a=LOCK_A_LOC, loc_b=LOCK_B_LOC,
                         screw=f'DIN912 M3×{SHR_SCR_L:g} 从罩耳顶往下 支承 Z{SHR_SCR_BEAR:g} 尾 Z{SHR_SCR_TIP:g} (离承载盘顶 {SHR_TIP_CLR:g}), 倒扣法兰螺母 Z{LOCK_NUT_Z[0]:g}–{LOCK_NUT_Z[1]:g} 吃 {SHR_ENG:g}',
                         ear_t=SHR_EAR_T,
                         out_screw=f'M3×{OUT_SCR_L:g} 超薄头 支承 Z{OUT_SCR_BEAR:g} 尾 Z{OUT_SCR_BEAR + OUT_SCR_L:g}, 法兰螺母嵌支撑件顶 Z{OUT_NUT_Z[0]:g}–{OUT_NUT_Z[1]:g} 吃 {OUT_ENG:g}',
                         scr_screw=f'M3×{BAR_SCR_L:g} 超薄头 支承 Z{BAR_SCR_BEAR:g} 尾 Z{BAR_SCR_BEAR + BAR_SCR_L:g}, 铜螺柱 Z{LS.SO_Z0:g}–{LS.SO_Z1:g} 吃 {BAR_SCR_ENG:g}, 离上颗 {round(LS.SO_Z1 - BAR_SCR_BEAR - BAR_SCR_L, 2):g}'),
               edge=SP_EDGE,
               optical=dict(hole=dict(pt=(round(OPT_PT[0], 3), round(OPT_PT[1], 3)), d=OPT_D, note='承载盘全厚通; fr4_plate 同位 Φ3.2 现场配钻 (以承载盘为钻模)', wall=OPT_WALL),
                            rx_slot=dict(loc_x=(RX_X0, RX_X1), loc_hy=RX_HY, z=(SP_Z0, RX_Z1), pcb=(RX_PCB_L, RX_PCB_W, RX_PCB_T), pt_dx=RX_PT_DX, exit=RX_EXIT,
                                         wire=dict(w=RX_WIRE_W, h=RX_WIRE_H, loc_x=(SP_B_X0, RX_X0)), pockets_b=SP_POCKETS['b'], wall=RX_WALL)))
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
    out('screen_sup_a_v1_2b', screen_sup_a_loc, color='#F1C232')           # A 屏幕支架件 (放 0° 装配位; 180° 同件); _print 底面落床 (底面窝开口朝床, 窝顶 6 mm 桥接)
    out('screen_sup_b_v1_2b', screen_sup_b_loc, color='#C9B458')           # B 上下件 (放 0° 局部; 装 90°/270°)
    write_doc([('fr4_plate_v1_2b (装配位)', fr4, '#C9B458', None, False), ('rim_ring_v1_2b', rim, '#6AA84F', None, False),
               *[(n, sh, c, None, False) for n, sh, c in SCREEN_PARTS],
               ('线圈 (占位)', coil, '#D9822B', None, False)], B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step', 'rotor_b')
    (B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出', OUTD)
