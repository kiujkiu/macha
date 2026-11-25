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
光电对射 (11-23): 通光孔 Φ3.4 @ r77.5 90° 穿承载盘 (fr4_plate 现场配钻); 接收板双面 (底 0603 光敏管伸进孔 / 顶 47k + 3 焊线焊盘) 嵌 B 件底面槽 (B 件兼压板), 焊盘上方 B 件长圆穿线槽; 11-23 r4 改通用板 10×10 对称 4 定位孔 (r5, RX_*_UV 表), 线出件顶绕 CZ06 → 底板 J9 (参数 OPT_* / RX_* / GH)
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
# 11-23 二版 (用户): 接收板双面 —— 底面 0603 光敏管朝下, 光敏管面平贴承载盘顶 (板底 = Z_TOP), 本体伸进 Φ3.4 通光孔 (中心对孔心);
#   顶面 0603 47k 上拉 + JST GH 1.25 3P 接插件, 线另一头焊底板 J9 焊盘。B 件 = 压板 (与罩锁转接件复用): 底面槽 = 板外形浅槽 (压板顶) + 器件让位, 槽顶压接插件顶。
#   用户草图 (11-23 定): 板沿径向长条, 外端 = 光敏管 (底面, 对通光孔), 中间 = 47k (顶面), 内端 (靠轴心) = 接插件 (顶面);
#   RX_CONN = 'top' 顶入 BM03B-GHS-TBT (默认, 用户定): 接插件正上方 B 件开通窗到顶, 插头 GHR-03V-S 竖直插拔, 线从 B 件顶面上方出来弯 R3 向轴心去 J9
#           'side' 侧入 SM03B-GHS-TB (备选): 插头朝轴心水平插, 件底出线槽通内边
#   接插件 / 插头尺寸 = 用户给的 GH 规格书 (3P)。板外形按最小反推。
#   11-23 三版 (用户定): 去掉接插件, 板顶 3 个焊线焊盘 (SIG / 3V3 / GND), 线从 B 件 Φ3 穿线孔上出 ⇒ RX_CONN = 'pads' (默认; 'top' / 'side' 保留可切回)
RX_CONN = 'pads'
RX_PCB_T = 1.6                                    # 接收板厚 (FR4); 11-24 用户「pcb的厚度应该是1.6mm」(原 0.8)
RX_PT_L, RX_PT_H = 0.8, 0.6                       # 0603 光敏管 沿径向宽 (长边 1.6 沿切向) / 本体高 (板底往下伸进通光孔; 孔 Φ3.4 > 0603 对角 1.79)
RX_R_L, RX_R_W, RX_R_H = 0.8, 1.6, 0.5            # 顶面 0603 47k (长边沿切向)
RX_EDGE, RX_GAP = 0.3, 0.3                        # 板边 ↔ 器件 / 电阻 ↔ 接插件焊盘区
RX_PCB_SIDE = 0.2                                 # 板宽 = 接插件宽 + 2×0.2; 板内边 = 焊盘区内边 − 0.2
GH = dict(side=dict(name='SM03B-GHS-TB', W=7.0, D=4.05, TAIL=0.8, H=4.25, LIFT=0.1, PAD_D=5.4, MATE_L=7.15, MATE_H=4.35),
          top=dict(name='BM03B-GHS-TBT', W=7.0, D=4.25, TAIL=0.7, H=4.05, LIFT=0.15, PAD_D=5.6, MATE_H=7.3))
GH_PLUG = dict(name='GHR-03V-S', W=5.0, L=5.7, T=4.15)   # 插头 宽 (沿针距) / 长 (插入方向) / 厚
RX_WIRE_OD, RX_WIRE_R = 1.0, 3.0                  # 线外径 (AWG30–26 Φ0.76–1.0) / 顶入出线弯半径 (向轴心)
RX_WIRE_BEND = 1.5                                # 侧入: 插头尾后线弯余量 (沿 −x)
RX_PCB_CLR = 0.2                                  # 11-24 用户: 板外形槽每边 0.2 (器件/焊点让位仍 RX_CLR)
RX_CLR = 0.3                                      # 槽 / 窗每边余量 (板 / 器件 / 接插件 / 插头)
RX_PCB_TOP_CLR = 0.1                              # 11-24 用户「深度做1.7」: 板槽深 = 1.6 + 0.1; 板外形浅槽顶 ↔ 板顶 (B 件压板; 11-23 用户定 0.05 → 0, 真压住板)
RX_TOP_CLR = 0.15                                 # 槽顶 ↔ 接插件顶 (压住, 0.1~0.2)
RX_WIRE_W, RX_WIRE_H = 3 * RX_WIRE_OD + 0.6, 4.0  # 侧入用: 件底出线槽 宽 × 高
RX_POCKET_WALL = 1.5                              # 槽 / 窗 ↔ 顶面减重槽 水平壁
# 'pads' 焊线焊盘版: 板沿径向, 外端底面光敏管 (对孔心) / 顶面 47k, 内端顶面 3 焊盘沿径向一排; PT 的 2 个过孔放在焊盘排两侧
RX_SP_N, RX_SP_D, RX_SP_P = 3, 1.0, 1.3           # 焊盘 个数 / 直径 / 中心距 (SIG / 3V3 / GND, 外→内)
RX_VIA_D, RX_VIA_GAP = 0.6, 0.15                  # 过孔焊环 Φ0.6 (钻 0.3) / 过孔环 ↔ 焊盘 间隙
RX_EDGE_MIN = 0.25                                # 过孔环 ↔ 板边 最小
RX_SOLDER_H = 1.0                                 # 焊盘上方焊点 / 线头让位高
RX_WIRE_HOLE_D = 3.0                              # B 件穿线孔 Φ3 (3 根 AWG30, 外径 ~0.5–0.6), 焊盘排中心正上方贯穿到件顶
# 11-23 四版 (用户): 板上 2 个 NPTH 定位孔, B 件底面 2 个销向下插进去定位 (求装得准)。两孔沿径向放在焊盘排两端 (尽量拉开防转):
#   内孔 = 板内端, 外孔 = 焊盘排与外端 (光敏管 / 47k) 之间 (外端再加长会让槽外端离件外边 <1.5)
RX_LOC = True
RX_LOC_D = 2.2                                    # 定位孔 NPTH (r4 第 3 版: Φ1.5 → Φ3.4 → Φ2.2 M2 通孔规格)
RX_PIN_D = RX_LOC_D - 0.1                         # 11-24 用户「凸台直径小于孔0.1」: Φ2.1; B 件销 (r4 第 3 版: Φ2.0, 孔 Φ2.2 单边 0.1)
RX_PIN_H = RX_PCB_T - 0.1                         # 销高 0.7 (销底离承载盘顶 0.1, 不顶)
RX_LOC_CLR = 0.3                                  # 定位孔边 ↔ 板边 / 铜 / 器件 / 过孔
# 11-23 六版 (用户草图, 覆盖 四版 / 五版 对角): 接收板横放 —— 长边沿切向 (件局部 y), 短边沿径向 (x)
#   光敏管 (板底) 在板中央对通光孔; 2 个定位孔在板切向两端、同在 r77.5 线上; 3 焊盘沿切向一排贴板内边 (朝轴心), 线朝轴心出;
#   47k 在顶面光敏管背面; 焊盘做金属化通孔 (两面有铜), 光敏管底面直接走线到焊盘, 不另打过孔。
#   B 件: 焊盘排正上方长圆穿线槽 (宽 RX_WSLOT_W, 盖住 3 焊点) 贯穿到件顶, 线出件顶沿原 CZ06 绕行路线去 J9
# 11-23 r5 (用户「因为生产原因」改 10×10 + 4 定位孔, 需求 pcb/projects/POV3D_Opto_V1.0/review/需求_r5_通用板10x10_2026-11-23.md): r4 第 3 版上半部相对结构不动, 只往轴心加长 5 (v 全 +5)
# (r4 第 3 版: 用户草图「不对」后定, 需求 ..._r4_通用板8x4_2026-11-23.md; 8×4 / 10×5 第 2 版作废)
#   发射/接收同一块通用板 10×10, 关于 u=5 左右对称, 定子 / 转子装法一样 (r = 69.1 + v)。直接写板局部坐标 (表格式, 同定子 IR_*)
#   板局部 (需求里叫 a / b, 这里变量 u / v): u 沿切向 0–10, v 沿径向 0–10 (v=0 朝轴心), 原点 = 板角
#   转子: A 面朝下贴承载盘, x = OPT_R + (v − 8.4) = 69.1 + v, y = u − 5 (对称, 正反 / 镜像都一样)
RX_PCB_U, RX_PCB_V = 10.0, 10.0                   # 外形 (u 切向 × v 径向), 厚 RX_PCB_T
RX_PT_UV = (5.00, 8.40)                           # A 面 0603 光敏管 / B 面 0603 47k 正背面 (长轴都沿 v 径向)
RX_0603_EXT = (0.95, 2.4)                         # 0603 铜外包 (u 向 × v 向; 长轴沿 v)
RX_SP_UV = {'VCC': (3.50, 5.80), 'SIG': (5.00, 5.80), 'GND': (6.50, 5.80)}   # 金属化焊盘 Φ RX_SP_D / 钻 RX_SP_DRILL, 沿切向一排 (P1 3V3 / P2 N=SIG / P3 GND)
RX_LOC_UV = {'H1': (2.00, 8.20), 'H2': (8.00, 8.20), 'H3': (2.00, 2.50), 'H4': (8.00, 2.50)}   # NPTH 定位孔 Φ2.2 (M2 通孔规格) ×4 (r5 加 H3/H4), B 件销 Φ2.0 对准
RX_YS = +1                                        # u → y 方向 (板对称, 取 +1 / −1 结果相同)
RX_CU_EDGE = 0.2                                  # 铜 ↔ 板边
RX_NPTH_EDGE, RX_NPTH_CU = 0.3, 0.25              # NPTH 孔边 ↔ 板边 / ↔ 铜 (r4 规则)
RX_SP_DRILL = 0.5                                 # 焊盘金属化孔径
RX_WSLOT_W = 3.0                                  # 11-24 用户「这个口加大1.5倍」2.0 → 3.0; B 件长圆穿线槽宽 (径向); 长轴沿切向, 长 = 焊盘排 + 宽 (盖住 3 焊点; 离 Φ2 销 0.83)

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
SP_BLOCK_T = 7.0                                  # 11-23 用户: 屏幕下中段只留 4 (屏幕贴近承载盘), 锁罩子的法兰螺母要高度 ⇒ 两头螺母块 7 高, 罩耳坐其顶 (不再跟灯板走)
SP_Z1 = SP_Z0 + SP_BLOCK_T                        # 37.5 支撑件顶 (螺母块顶 = 罩耳底)
SP_T = round(SP_Z1 - SP_Z0, 3)                    # 7
assert LS.Z0 <= SP_Z1 + 1e-6 and LS.Z0 - SP_Z0 >= 4.0 - 1e-6, (LS.Z0, SP_Z1)   # 灯板下沿在中段顶 (≥4), 不高于螺母块顶
SP_R1 = LS.R_CLIP                                 # 81.7 外缘 (以轴心为圆心; 罩壁内面 r82)
SP_X1 = 81.2                                      # 外边直线段 (两种件同)
SP_ANG = (0.0, 90.0, 180.0, 270.0)
SP_TYPE = {0.0: 'a', 90.0: 'b', 180.0: 'a', 270.0: 'b'}
SP_HOLE_A = (22.5, -22.5)                         # 外圈螺丝 (承载盘 r77.5 @22.5+45k 全 8 颗都穿支撑件)
# A 件外形: 主体 x66–81.2 × |y|≤37 ∩ r81.7 + 内伸翼 x54.5–66 × 22≤|y|≤37 (包住罩锁螺母窝, 壁 ≥2.4); B 件: x66.5–81.2 × |y|≤35 ∩ r81.7
# 11-25 用户「挪到边上是不是会好一点」「改吧」: A 件罩锁挪到外圈螺丝外侧的盘边 ⇒ 默认 'rim' = 主体直条 x66–81.2 + 两端块 x58.5 起 |y|≥32 (包住罩锁螺母窝); 高度分界 |y|≥22 满高 7 不变, 锁 (64.8, ±38.8) r75.53; 罩耳不再盖外圈螺母
SP_A_STYLE = __import__('os').environ.get('SP_A_STYLE', 'rim')   # 'ear' = 11-23/24 两翼耳朵 (锁 (61, ±30.5)); 'bar' = 直条 (同 B 不伸翼, 锁 (72.5, ±20.5), 两头 |y|≥SP_A_BAR_KEEP 满高)
assert SP_A_STYLE in ('rim', 'ear', 'bar'), SP_A_STYLE
SP_A_X0, SP_A_HY, SP_A_WING = (66.0, 45.3, (58.5, 32.0)) if SP_A_STYLE == 'rim' else (66.0, 37.0, (54.5, 22.0))     # 翼 x0 / 翼内边 |y|
SP_A_KEEP = 22.0                                  # |y|≥22 满高 SP_T (外圈螺母 N y29.66 坐这里), 中段 SP_A_LOW
SP_A_LOW = round(LS.Z0 - SP_Z0, 3)                # A 件中段高 = 灯板下沿 − 承载盘顶 (托灯板); 11-23 21:4x 用户「sup a只有蓝色这个区域高度是7mm，别的都是4mm高度」: 只有两翼罩锁块 (x54.5–66, 22≤|y|≤37) 满高 SP_T, 其余 Z SP_Z0 → SP_Z0+4
SP_B_X0, SP_B_HY = 66.5, 35.0                     # 66 → 66.5: 放 90° 时内边 y66 离 CZ06 包络 (y≤65.82, Z35.1–41.7) 只 0.18 (件变高 8 后 Z 重叠); 放 270° 离无线夹块 2.9
SP_X0, SP_HY = SP_A_X0, SP_A_HY                   # 兼容旧名
SP_A_BAR_KEEP = 16.0                              # 直条: 用户黑框 |y|≥16 做满高 (罩锁 S Φ8 @y20.5 内边 16.5)
LOCK_A_LOC = {'rim': [(64.8, 38.8), (64.8, -38.8)], 'ear': [(61.0, 30.5), (61.0, -30.5)], 'bar': [(72.5, 20.5), (72.5, -20.5)]}[SP_A_STYLE]   # rim: y38.8 = 罩耳 (半宽 4.5) 避开外圈螺母 Φ7.6 0.84; 73→72.5: 锁窝外壁到 r81.7 1.78→2.26        # A 件罩锁 (用户图上量 (±61, ±30.5), r68.20; 原 (73, ±19.5) 在 A 件上删 —— 原 −x 端套筒 Φ9 离灯板B 0.33)
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
OUT_NUT_Z = (SP_Z1 - 0.3 - NUT_T, SP_Z1 - 0.3)   # 11-23 22:1x N 在 7 高螺母块里: 顶面 Φ8 圆沉孔 (朝外开口), 螺母顶低于块顶/罩耳底 0.3 (Z33.5–37.2)
SP_A_TOP_FLAT = True                              # 11-24 用户「这个沉孔去掉，sup_a的」: A 件 N 顶面沉孔取消, 只留 Φ3.4 通; 螺母 (法兰朝下) 坐块顶 Z SP_Z1 → +NUT_T (11-25 'rim' 罩耳不在螺母上方, 不开让位口; 'ear' 时罩耳底开让位口 rotor_shroud_b NUT_NOTCH_*)
if SP_A_TOP_FLAT: OUT_NUT_Z = (SP_Z1, SP_Z1 + NUT_T)
OUT_NUT_TOP = OUT_NUT_Z[1]
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
OUT_SCR_L = max(L for L in (10, 12, 14, 15, 16, 18, 20) if OUT_SCR_BEAR + L <= OUT_NUT_Z[1])   # 尾不超螺母顶
OUT_ENG = round(OUT_SCR_BEAR + OUT_SCR_L - OUT_NUT_Z[0], 2)
assert OUT_ENG >= 3.0 and OUT_NUT_Z[0] > SP_Z0 + 2.5, (OUT_SCR_L, OUT_ENG, OUT_NUT_Z)
# 屏幕螺丝 M3 超薄头 从 A 件底沉孔往上 (支承 Z_TOP + SP_CB_H), 拧进每端下颗铜螺柱: 吃牙 ≥3, 尾离上颗底 ≥0.5
BAR_SCR_BEAR = SP_Z0 + SP_CB_H                    # 32.0
BAR_SCR_L = float(min(L for L in (12, 14, 16, 18, 20, 22) if BAR_SCR_BEAR + L - LS.SO_Z0 >= 3.0))
BAR_SCR_ENG = round(BAR_SCR_BEAR + BAR_SCR_L - LS.SO_Z0, 2)
assert 3.0 <= BAR_SCR_ENG and BAR_SCR_BEAR + BAR_SCR_L <= LS.SO_Z1 - 0.5, (BAR_SCR_L, BAR_SCR_ENG)
BAR_SCR_PTS = list(LS.SO_PTS)                     # 世界: (78.88, ECC−0.2) 板B 下颗 / (−78.88, ECC+0.2) 板A 下颗
# 减重 (动平衡 / 惯量): 顶面开口盲槽, 槽底留 SP_POCKET_FLOOR; 不在灯板/夹条正下方、不在罩耳下、离孔/螺母窝 ≥2
SP_POCKET_FLOOR = 3.0
SP_POCKETS = {'a': [],                            # 11-23 A 件主体只剩 4 高, 不再开减重槽 (原 (68, ±12.5…±23.5, 76.5))
              'b': [(68.5, -13.4, 77.5, 13.4)]}
# 11-23 用户「sup_b上面的沉孔都去掉」: B 件顶面全平 (无减重盲槽 / 无外圈 N 沉孔+U 口, 只留贯穿孔 + 穿线槽), 翻过来顶面 Z SP_Z1 贴床打印;
#   B 件位置 (90°/270°) 外圈 4 颗的 M3 法兰螺母改坐 B 件顶面 (法兰朝下, Z SP_Z1 → +NUT_T), 外圈螺丝单独选长度 (A 件位置那 4 颗不变);
#   量过 (SP_Z1=37.5): 螺母 Φ7.6 离转子罩B 内壁 0.7 (径向), 罩耳 (y15–24) 不在上方, 无线托盘 4.66; 螺母须在罩子下放前拧好
SP_B_TOP_FLAT = True
OUT_NUT_Z_B = (SP_Z1, SP_Z1 + NUT_T)
OUT_SCR_L_B = max(L for L in (10, 12, 14, 15, 16, 18, 20, 22) if OUT_SCR_BEAR + L <= OUT_NUT_Z_B[1])   # 尾不超螺母顶
OUT_ENG_B = round(OUT_SCR_BEAR + OUT_SCR_L_B - OUT_NUT_Z_B[0], 2)
assert OUT_ENG_B >= 3.0, (OUT_SCR_L_B, OUT_ENG_B)
OUT_B_PTS = [pol(R_OUT, a + d) for a in SP_ANG if SP_TYPE[a] == 'b' for d in SP_HOLE_A]   # 世界 67.5/112.5/247.5/292.5°
# 11-23 B 件底面接收板槽 (局部 = 放 0°; B 件装 90° 时局部 (OPT_R, 0) = 世界通光孔; 270° 那个同件, 下面没孔)
#   径向 (局部 x, −x = 朝轴心) 从外往里: 板外边 | 光敏管 (底, 对孔心) / 47k (顶) | 间隙 | 接插件焊盘区 (尾朝外) | 板内边
assert SP_TYPE[(OPT_ANG + 360) % 360] == 'b'
if RX_CONN == 'pads':
    def rx_uv2xy(u, v): return (OPT_R + (v - RX_PT_UV[1]), RX_YS * (u - RX_PT_UV[0]))   # x = 69.1 + v, y = u − 5
    def _dpr(p, c, hu, hv): return math.dist(p, (min(max(p[0], c[0] - hu), c[0] + hu), min(max(p[1], c[1] - hv), c[1] + hv)))
    # 板上规则自检 (r4 需求: 铜 ↔ 板边 ≥0.2 / NPTH ↔ 板边 ≥0.3 / NPTH ↔ 铜 ≥0.25)
    RX_PCB_CHK = {}
    for n, (u, v) in RX_SP_UV.items(): RX_PCB_CHK[f'焊盘{n}_板边'] = round(min(u, RX_PCB_U - u, v, RX_PCB_V - v) - RX_SP_D / 2, 3)
    _sp = list(RX_SP_UV.values())
    RX_PCB_CHK['焊盘_焊盘'] = round(min(math.dist(p, q) for i, p in enumerate(_sp) for q in _sp[i + 1:]) - RX_SP_D, 3)
    RX_PCB_CHK['0603_板边'] = round(min(RX_PT_UV[0] - RX_0603_EXT[0] / 2, RX_PCB_U - RX_PT_UV[0] - RX_0603_EXT[0] / 2, RX_PT_UV[1] - RX_0603_EXT[1] / 2, RX_PCB_V - RX_PT_UV[1] - RX_0603_EXT[1] / 2), 3)
    for k, (u, v) in RX_LOC_UV.items():
        r = RX_LOC_D / 2
        RX_PCB_CHK[f'{k}_板边'] = round(min(u, RX_PCB_U - u, v, RX_PCB_V - v) - r, 3)
        RX_PCB_CHK[f'{k}_焊盘'] = round(min(math.dist((u, v), q) for q in _sp) - r - RX_SP_D / 2, 3)
        RX_PCB_CHK[f'{k}_0603'] = round(_dpr((u, v), RX_PT_UV, RX_0603_EXT[0] / 2, RX_0603_EXT[1] / 2) - r, 3)
    for k, v in RX_PCB_CHK.items():
        lim = (RX_NPTH_EDGE if '板边' in k else RX_NPTH_CU) if k.startswith('H') else RX_CU_EDGE if '板边' in k else 0.3
        assert v >= lim - 1e-6, (k, v, lim)
    _cx = [rx_uv2xy(u, v) for u in (0.0, RX_PCB_U) for v in (0.0, RX_PCB_V)]
    RX_PCB_X0, RX_PCB_X1 = min(p[0] for p in _cx), max(p[0] for p in _cx)       # 件局部 x 69.1–79.1
    RX_PCB_Y0, RX_PCB_Y1 = min(p[1] for p in _cx), max(p[1] for p in _cx)       # 件局部 y −5…+5
    RX_PCB_L = round(RX_PCB_X1 - RX_PCB_X0, 3)    # 径向 10
    RX_PCB_W = round(RX_PCB_Y1 - RX_PCB_Y0, 3)    # 切向 10
    RX_PT_XY = rx_uv2xy(*RX_PT_UV)                # (77.5, 0) 对通光孔
    assert math.dist(RX_PT_XY, (OPT_R, 0.0)) < 1e-9
    RX_SP_PTS = [rx_uv2xy(u, v) for u, v in RX_SP_UV.values()]
    RX_LOC_PTS = [rx_uv2xy(u, v) for u, v in RX_LOC_UV.values()] if RX_LOC else []
    RX_R_BOX = (RX_PT_XY[0] - RX_0603_EXT[1] / 2 - RX_CLR, RX_PT_XY[1] - RX_0603_EXT[0] / 2 - RX_CLR,
                RX_PT_XY[0] + RX_0603_EXT[1] / 2 + RX_CLR, RX_PT_XY[1] + RX_0603_EXT[0] / 2 + RX_CLR)   # 47k 让位 (长轴沿 x)
    RX_R_X0, RX_R_X1 = RX_R_BOX[0], RX_R_BOX[2]
    RX_PAD_X0, RX_PAD_X1 = min(p[0] for p in RX_SP_PTS) - RX_SP_D / 2, max(p[0] for p in RX_SP_PTS) + RX_SP_D / 2
    RX_PCB_LOCAL = dict(外形_uv=(RX_PCB_U, RX_PCB_V), 光敏管_47k=RX_PT_UV, **{f'焊盘{n}': p for n, p in RX_SP_UV.items()}, **RX_LOC_UV,
                        u_to_y=RX_YS, 焊盘孔径=RX_SP_DRILL)
    RX_Z_PCB = (SP_Z0, SP_Z0 + RX_PCB_T)
    RX_Z1 = RX_Z_PCB[1] + RX_SOLDER_H
    RX_X0, RX_X1 = RX_PCB_X0 - RX_PCB_CLR, RX_PCB_X1 + RX_PCB_CLR   # 11-24 用户「四周做0.2的避让」
    RX_Y0, RX_Y1 = RX_PCB_Y0 - RX_PCB_CLR, RX_PCB_Y1 + RX_PCB_CLR
    RX_HY = max(-RX_Y0, RX_Y1)
    _xs = [x for x, _ in RX_SP_PTS]; _ys = [y for _, y in RX_SP_PTS]
    assert max(_ys) - min(_ys) < 1e-9 or max(_xs) - min(_xs) < 1e-9   # 焊盘排沿轴向一排
    RX_HOLE = dict(x0=min(_xs), x1=max(_xs), y0=min(_ys), y1=max(_ys), w=RX_WSLOT_W)   # 长圆穿线槽: 中心线段 (x0,y0)–(x1,y1) (轴向), 宽 w; 现长轴沿切向 y
    RX_WIN = None
    RX_HDR_X0 = RX_HDR_X1 = RX_HDR_Z1 = RX_MATE_Z1 = RX_PLUG_X0 = None
else:
    RX_HOLE = None
    _C = GH[RX_CONN]
    RX_PCB_X1 = OPT_R + RX_PT_L / 2 + RX_EDGE         # 78.2 板外边
    RX_R_X1 = RX_PCB_X1 - RX_EDGE; RX_R_X0 = RX_R_X1 - RX_R_L          # 47k 77.1–77.9
    RX_PAD_X1 = RX_R_X0 - RX_GAP                      # 76.8 接插件焊盘区外边
    RX_PAD_X0 = RX_PAD_X1 - _C['PAD_D']
    RX_PCB_X0 = RX_PAD_X0 - RX_PCB_SIDE               # 板内边
    RX_PCB_L = round(RX_PCB_X1 - RX_PCB_X0, 3)        # 板长 (径向)
    RX_PCB_W = _C['W'] + 2 * RX_PCB_SIDE              # 板宽 (切向) 7.4
    RX_Z_PCB = (SP_Z0, SP_Z0 + RX_PCB_T)              # 板底贴承载盘顶 30.5–31.3
    RX_HDR_X1 = RX_PAD_X1 - _C['TAIL']                # 接插件本体外端 (尾脚朝外)
    RX_HDR_X0 = RX_HDR_X1 - _C['D']                   # 本体内端
    RX_HDR_Z1 = RX_Z_PCB[1] + _C['LIFT'] + _C['H']    # 接插件顶
    RX_MATE_Z1 = RX_Z_PCB[1] + _C['MATE_H']           # 配合后插头顶 (顶入) / 配合高 (侧入)
    RX_Z1 = (RX_HDR_Z1 if RX_CONN == 'top' else max(RX_HDR_Z1, RX_MATE_Z1)) + RX_TOP_CLR   # 接插件让位槽顶 (压接插件)
    RX_HY = max(RX_PCB_W / 2, _C['W'] / 2) + RX_CLR   # 4.0
    RX_X0 = min(RX_PCB_X0, RX_PAD_X0) - RX_CLR        # 槽内端 (顶入)
    RX_X1 = RX_PCB_X1 + RX_CLR                        # 槽外端
    RX_Y0, RX_Y1 = -RX_HY, RX_HY
    if RX_CONN == 'top':
        RX_PLUG_XC = (RX_HDR_X0 + RX_HDR_X1) / 2      # 插头竖插, 截面 W 沿 y × T 沿 x, 中心对本体中心
        RX_WIN = (RX_PLUG_XC - GH_PLUG['T'] / 2 - RX_CLR, -GH_PLUG['W'] / 2 - RX_CLR, RX_PLUG_XC + GH_PLUG['T'] / 2 + RX_CLR, GH_PLUG['W'] / 2 + RX_CLR)   # 通窗 (x0, y0, x1, y1)
        RX_PLUG_X0 = RX_PLUG_XC - GH_PLUG['T'] / 2
    else:
        RX_PLUG_X0 = RX_HDR_X1 - _C['MATE_L']         # 侧入: 插头尾 (配合总长从本体外端算)
        RX_X0 = RX_PLUG_X0 - RX_WIRE_BEND
        RX_WIN = None
def _top_conflict():                              # 顶入: 插头顶 / 线弯 超出 B 件顶多少
    t = GH['top']; mz = SP_Z0 + RX_PCB_T + t['MATE_H']
    return dict(插头顶=round(mz, 2), 插头超件顶=round(mz - SP_Z1, 2), 线弯外包顶=round(mz + RX_WIRE_R + RX_WIRE_OD / 2, 2),
                线弯超件顶=round(mz + RX_WIRE_R + RX_WIRE_OD / 2 - SP_Z1, 2))
RX_TOP_CONFLICT = _top_conflict()
# B 件减重槽在中间劈开, 让出接收槽 / 通窗 / 穿线槽 (水平壁 ≥ RX_POCKET_WALL; 槽顶高于减重槽底 33.5, 但仍按水平壁留)
if RX_HOLE:
    _ky0 = min(RX_Y0, RX_HOLE['y0'] - RX_HOLE['w'] / 2) - RX_POCKET_WALL
    _ky1 = max(RX_Y1, RX_HOLE['y1'] + RX_HOLE['w'] / 2) + RX_POCKET_WALL
else:
    _ky0, _ky1 = -RX_HY - RX_POCKET_WALL, RX_HY + RX_POCKET_WALL
_P0 = SP_POCKETS['b'][0]                          # 原整块 (68.5, −13.4, 77.5, 13.4)
SP_POCKETS['b'] = [(x0, y0, x1, y1) for X0, Y0, X1, Y1 in SP_POCKETS['b'] for (x0, y0, x1, y1) in ((X0, _ky1, X1, Y1), (X0, Y0, X1, _ky0)) if y1 - y0 > 1.0]
if RX_HOLE:                                       # 焊盘版: 中间条在槽 / 穿线槽内侧 (朝轴心) 那段照原样挖回, 离槽 / 槽 ≥ RX_POCKET_WALL
    _cx1 = min(RX_X0, RX_HOLE['x0'] - RX_HOLE['w'] / 2) - RX_POCKET_WALL
    if _cx1 - _P0[0] > 1.0: SP_POCKETS['b'].append((_P0[0], _ky0, _cx1, _ky1))
if SP_B_TOP_FLAT: SP_POCKETS['b'] = []            # 11-23 B 件顶面全平: 不开减重槽
def rx_cuts():
    zb = RX_Z_PCB[1] + RX_PCB_TOP_CLR
    if RX_CONN == 'pads':                         # 板外形浅槽 (压板顶) + 47k 让位 + 焊盘排焊点让位 + Φ3 穿线孔到件顶
        h = RX_HOLE
        return [gbox(RX_X0, RX_Y0, SP_Z0 - 1, RX_X1, RX_Y1, zb),
                gbox(RX_R_BOX[0], RX_R_BOX[1], SP_Z0 - 1, RX_R_BOX[2], RX_R_BOX[3], RX_Z_PCB[1] + RX_R_H + 0.2),   # 47k (含焊点) 让位
                *[cyl(x, y, RX_SP_D + 2 * RX_CLR, SP_Z0 - 1, RX_Z1) for x, y in RX_SP_PTS],     # 每个焊盘焊点让位
                _slot_seg(h['x0'], h['y0'], h['x1'], h['y1'], RX_Z_PCB[1], SP_Z1 + 1, h['w'])]   # 长圆穿线槽 (焊盘排正上方, 长轴沿切向) 贯穿到件顶
    c = [gbox(RX_PCB_X0 - RX_CLR, -RX_PCB_W / 2 - RX_CLR, SP_Z0 - 1, RX_PCB_X1 + RX_CLR, RX_PCB_W / 2 + RX_CLR, zb),             # 板外形浅槽 (槽顶压板顶)
         gbox(RX_R_X0 - RX_CLR, -RX_R_W / 2 - RX_CLR, SP_Z0 - 1, RX_R_X1 + RX_CLR, RX_R_W / 2 + RX_CLR, RX_Z_PCB[1] + RX_R_H + 0.2),   # 47k 让位
         gbox(RX_PAD_X0 - RX_CLR, -_C['W'] / 2 - RX_CLR, SP_Z0 - 1, RX_PAD_X1 + RX_CLR, _C['W'] / 2 + RX_CLR, RX_Z1)]                # 接插件 (含焊盘区) 让位, 顶压接插件
    if RX_CONN == 'top':                          # 接插件正上方通窗贯穿到件顶, 插头竖直插拔
        c.append(gbox(RX_WIN[0], RX_WIN[1], RX_Z1 - 0.01, RX_WIN[2], RX_WIN[3], SP_Z1 + 1))
    else:                                         # 侧入: 插头 + 线弯让位, 件底出线槽 −x 通出内边
        c.append(gbox(RX_X0, -GH_PLUG['W'] / 2 - RX_CLR, SP_Z0 - 1, RX_PAD_X0, GH_PLUG['W'] / 2 + RX_CLR, RX_Z1))
        c.append(gbox(SP_B_X0 - 1, -RX_WIRE_W / 2, SP_Z0 - 1, RX_X0 + 0.01, RX_WIRE_W / 2, SP_Z0 + RX_WIRE_H))
    return c
def rx_wire_env(run_to=60.0):
    """顶入: 插头露出件顶段 + 3 线竖出弯 R3 向轴心 + 水平段到局部 x=run_to 的外包 (局部, 校核用)"""
    if RX_CONN != 'top': return None
    hy = 1.25 + RX_WIRE_OD / 2 + 0.2; z0 = RX_MATE_Z1; zc = z0 + RX_WIRE_R
    return fuse(gbox(RX_PLUG_X0, -GH_PLUG['W'] / 2, SP_Z1, RX_PLUG_X0 + GH_PLUG['T'], GH_PLUG['W'] / 2, z0 + 0.01),
                gbox(RX_PLUG_XC - RX_WIRE_R - RX_WIRE_OD / 2, -hy, z0, RX_PLUG_XC + RX_WIRE_OD / 2, hy, zc + RX_WIRE_OD / 2),
                gbox(run_to, -hy, zc - RX_WIRE_OD / 2, RX_PLUG_XC - RX_WIRE_R + 0.01, hy, zc + RX_WIRE_OD / 2))

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

def _slot_seg(x0, y0, x1, y1, z0, z1, d):
    """轴向长圆槽 (中心线段 (x0,y0)–(x1,y1), 沿 x 或沿 y, 宽 d)"""
    return fuse(cyl(x0, y0, d, z0, z1), cyl(x1, y1, d, z0, z1), gbox(min(x0, x1) - (d / 2 if y0 != y1 else 0), min(y0, y1) - (d / 2 if x0 != x1 or y0 == y1 else 0), z0,
                                                                     max(x0, x1) + (d / 2 if y0 != y1 else 0), max(y0, y1) + (d / 2 if x0 != x1 or y0 == y1 else 0), z1))

def _slot(x, y, z0, z1, d=3.4, hl=SP_SCR_SL):
    """沿 y 的腰形孔 (中心 (x, y), 半长 hl)"""
    return fuse(cyl(x, y - hl, d, z0, z1), cyl(x, y + hl, d, z0, z1), gbox(x - d / 2, y - hl, z0, x + d / 2, y + hl, z1))

# 11-23 20:4x 用户「锁法兰螺母的位置不对 … 参考这个 (承载盘 Q 孔), 应该是M3通孔加上一个圆形沉孔」:
#   两种螺母窝都改成 Φ3.4 通 + 圆沉孔 Φ SP_NUT_CB_D (同承载盘 Q: Φ8), 不再做六角窝 / 法兰窝台阶; 螺母一律法兰朝下 (法兰压沉孔底面或承载盘顶)
SP_NUT_CB_D = 8.0
def lock_nut_well(x, y):
    """罩锁: 件底面圆沉孔 Φ8 到 螺母顶 +0.1 (法兰螺母法兰朝下从件底塞进, 坐承载盘顶, 拧紧时螺母顶顶沉孔顶) + Φ3.4 通"""
    return fuse(cyl(x, y, SP_NUT_CB_D, SP_Z0 - 1, LOCK_NUT_Z[1] + WELL_TOP_CLR), cyl(x, y, SHR_HOLE_D, SP_Z0 - 1, SP_Z1 + 1))

def out_nut_well(x, y):
    """外圈: 件顶面圆沉孔 Φ8 (底 = 螺母底 OUT_NUT_Z[0], 法兰螺母法兰朝下坐沉孔底, 顶低于件顶 0.3) + Φ3.4 通;
    沉孔外侧离件外缘 r81.7 只剩 0.2 ⇒ 沉孔朝外开口 (U 形, 同宽 Φ8) 免薄皮"""
    a = math.degrees(math.atan2(y, x))
    cb = fuse(cyl(x, y, SP_NUT_CB_D, OUT_NUT_Z[0], SP_Z1 + 1), xf(gbox(math.hypot(x, y), -SP_NUT_CB_D / 2, OUT_NUT_Z[0], SP_R1 + 2, SP_NUT_CB_D / 2, SP_Z1 + 1), rotz(a)))
    return fuse(cb, cyl(x, y, 3.4, SP_Z0 - 1, SP_Z1 + 1))

def screen_sup_local(kind):
    """kind 'a' = 屏幕支架件 (放 0°/180°), 'b' = 上下件 (放 90°/270°); 局部 = 放 0° 时的世界坐标"""
    clip = cyl(0, 0, 2 * SP_R1, SP_Z0 - 1, SP_Z1 + 1)
    if kind == 'a':
        s = gbox(SP_A_X0, -SP_A_HY, SP_Z0, SP_X1, SP_A_HY, SP_Z1)
        if SP_A_STYLE == 'ear': s = fuse(s, gbox(SP_A_WING[0], -SP_A_HY, SP_Z0, SP_A_X0 + 0.01, SP_A_HY, SP_Z1))   # 11-23 用户「这里连上」: 两翼之间补满, 内边 x SP_A_WING[0] 一条直线 (原两翼 |y|≥22 分开)
        if SP_A_STYLE == 'rim': s = fuse(s, *[gbox(SP_A_WING[0], min(sy * SP_A_WING[1], sy * SP_A_HY), SP_Z0, SP_A_X0 + 0.01, max(sy * SP_A_WING[1], sy * SP_A_HY), SP_Z1) for sy in (1, -1)])   # 11-25 两端块
        _kp = SP_A_BAR_KEEP if SP_A_STYLE == 'bar' else SP_A_KEEP
        _low = gbox(SP_A_WING[0] - 1, -SP_A_HY - 1, SP_Z0 + SP_A_LOW, SP_R1 + 2, SP_A_HY + 1, SP_Z1 + 1)
        _keep = [gbox(SP_A_WING[0] - 1, min(sy * _kp, sy * (SP_A_HY + 1)), SP_Z0, SP_R1 + 2, max(sy * _kp, sy * (SP_A_HY + 1)), SP_Z1 + 2) for sy in (1, -1)]   # 11-23 22:1x 两头整块 (|y|≥22, 含 S + N) 满高
        s = cut(s, cut(_low, *_keep))                 # 11-23 其余削到 SP_A_LOW
        locks = LOCK_A_LOC
    else:
        s = gbox(SP_B_X0, -SP_B_HY, SP_Z0, SP_X1, SP_B_HY, SP_Z1); locks = LOCK_B_LOC
    s = _ocm(s, clip)
    cuts = [out_nut_well(x, y) if not (SP_A_TOP_FLAT if kind == 'a' else SP_B_TOP_FLAT) else cyl(x, y, 3.4, SP_Z0 - 1, SP_Z1 + 1) for x, y in SP_HOLES_LOC['out']] + [lock_nut_well(x, y) for x, y in locks]   # 11-23 B 件 N 只留 Φ3.4 通
    if kind == 'a':
        cuts += [_slot(x, y, SP_Z0 - 1, SP_Z1 + 1) for x, y in SP_HOLES_LOC['scr']] + [cyl(x, y, SP_SCR_CB_D, SP_Z0 - 1, SP_Z0 + SP_CB_H) for x, y in SP_HOLES_LOC['scr']]
    cuts += [gbox(x0, y0, SP_Z0 + SP_POCKET_FLOOR, x1, y1, SP_Z1 + 1) for x0, y0, x1, y1 in SP_POCKETS[kind]]
    if kind == 'b': cuts += rx_cuts()             # 11-23 底面接收板槽 + 线槽
    s = cut(s, *cuts)
    if kind == 'b' and RX_CONN == 'pads' and RX_LOC:   # 11-23 定位销: 从板外形浅槽顶往下 (销底 = 板顶 − RX_PIN_H)
        s = fuse(s, *[cyl(x, y, RX_PIN_D, RX_Z_PCB[1] - RX_PIN_H, RX_Z_PCB[1] + RX_PCB_TOP_CLR + 0.01) for x, y in RX_LOC_PTS])
    return clean(s)

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
        x0 = SP_A_X0 if SP_A_STYLE == 'bar' else SP_A_WING[0]                         # 11-23 两翼连成整块, 内边全长 x54.5
        return min(x - rh - x0, SP_X1 - x - rh, SP_A_HY - abs(y) - rh, SP_R1 - math.hypot(x, y) - rh)
    return min(x - rh - SP_B_X0, SP_X1 - x - rh, SP_B_HY - abs(y) - rh, SP_R1 - math.hypot(x, y) - rh)
SP_EDGE = dict(a_lock_well=round(min(_edge('a', x, y, WELL_FL_D / 2) for x, y in LOCK_A_LOC), 2),
               b_lock_well=round(min(_edge('b', x, y, WELL_FL_D / 2) for x, y in LOCK_B_LOC), 2),
               out_cb=round(min(min(x - SP_NUT_CB_D / 2 - x0, SP_X1 - x - SP_NUT_CB_D / 2, hy - abs(y) - SP_NUT_CB_D / 2)
                                for x, y in SP_HOLES_LOC['out'] for x0, hy in ((SP_A_X0, SP_A_HY), (SP_B_X0, SP_B_HY))), 2),   # 11-23 外圈圆沉孔 Φ8 (朝外开口, 只查内侧/两侧壁, A/B 件取小)
               scr_hole=round(min(_edge('a', x, y, 1.7) for x, y in SP_HOLES_LOC['scr']), 2),
               lock_out_a=round(min(math.dist(p, q) for p in LOCK_A_LOC for q in SP_HOLES_LOC['out']) - WELL_FL_D, 2),   # 罩锁窝 ↔ 外圈窝 壁 (不同 Z, 保守)
               lock_out_b=round(min(math.dist(p, q) for p in LOCK_B_LOC for q in SP_HOLES_LOC['out']) - WELL_FL_D, 2))
def _d_rect(x, y, x0, y0, x1, y1): return math.dist((min(max(x, x0), x1), min(max(y, y0), y1)), (x, y))
_pk = SP_POCKETS['b']; _pky = min((min(abs(y0), abs(y1)) for _, y0, _, y1 in _pk), default=math.inf)   # 11-23 B 件无减重槽时 = inf (下面 RX_WALL 去掉)
_sl = (RX_X0, RX_Y0, RX_X1, RX_Y1)                # 槽平面外包
def _rr(a, b): return math.hypot(max(b[0] - a[2], a[0] - b[2], 0), max(b[1] - a[3], a[1] - b[3], 0))   # 两矩形平面距离
RX_WALL = dict(槽外端_件外边=round(min(SP_X1, math.sqrt(SP_R1 ** 2 - max(-RX_Y0, RX_Y1) ** 2)) - RX_X1, 2),
               槽_减重槽=round(min((_rr(_sl, pk) for pk in SP_POCKETS['b']), default=math.inf), 2),
               槽_罩锁窝=round(min(_d_rect(x, y, *_sl) for x, y in LOCK_B_LOC) - WELL_FL_D / 2, 2),
               槽_外圈螺丝孔=round(min(_d_rect(x, y, *_sl) for x, y in SP_HOLES_LOC['out']) - 3.4 / 2, 2),
               接插件槽顶_件顶=round(SP_Z1 - RX_Z1, 2))
if RX_HOLE:                                        # 穿线孔 / 长圆槽 (x, y, 宽, 半长沿 y): 距离按中心线段算
    _h = RX_HOLE; _hd = _h['w']; RX_WALL.pop('接插件槽顶_件顶')
    def _sd(p): return math.dist(p, (min(max(p[0], _h['x0']), _h['x1']), min(max(p[1], _h['y0']), _h['y1'])))   # 点 ↔ 槽中心线段
    def _sdr(x0, y0, x1, y1): return _rr((_h['x0'], _h['y0'], _h['x1'], _h['y1']), (x0, y0, x1, y1))           # 中心线段 (轴向) ↔ 矩形
    _h_ext_y = max(abs(_h['y0']), abs(_h['y1'])) + _hd / 2
    RX_WALL.update(槽内端_件内边=round(RX_X0 - SP_B_X0, 2), 穿线槽_件内边=round(_h['x0'] - _hd / 2 - SP_B_X0, 2),
                   穿线槽_减重槽=round(min((_sdr(*pk) for pk in SP_POCKETS['b']), default=math.inf) - _hd / 2, 2), 穿线槽_罩锁窝=round(min(_sd(p) for p in LOCK_B_LOC) - _hd / 2 - WELL_FL_D / 2, 2),
                   穿线槽_外圈螺丝孔=round(min(_sd(p) for p in SP_HOLES_LOC['out']) - _hd / 2 - 3.4 / 2, 2),
                   穿线槽_件外边=round(min(SP_X1, math.sqrt(SP_R1 ** 2 - _h_ext_y ** 2)) - _h['x1'] - _hd / 2, 2),
                   槽外端_件外边=round(min(SP_X1, math.sqrt(SP_R1 ** 2 - max(-RX_Y0, RX_Y1) ** 2)) - RX_X1, 2))
    if RX_LOC:                                    # 销 ↔ 穿线槽 / 47k 让位 / 浅槽边 (销须落在板外形浅槽顶下, 不悬空)
        def _dr(p, x0, y0, x1, y1): return _d_rect(p[0], p[1], x0, y0, x1, y1)
        RX_PIN_CLR = dict(销_穿线槽=round(min(_sd(p) for p in RX_LOC_PTS) - _hd / 2 - RX_PIN_D / 2, 2),
                          销_焊点让位=round(min(math.dist(p, q) for p in RX_LOC_PTS for q in RX_SP_PTS) - RX_SP_D / 2 - RX_CLR - RX_PIN_D / 2, 2),
                          销_47k让位=round(min(_dr(p, *RX_R_BOX) for p in RX_LOC_PTS) - RX_PIN_D / 2, 2),
                          销_浅槽边=round(min(min(p[1] - RX_Y0, RX_Y1 - p[1], p[0] - RX_X0, RX_X1 - p[0]) for p in RX_LOC_PTS) - RX_PIN_D / 2, 2))
        assert min(RX_PIN_CLR.values()) > 0, RX_PIN_CLR   # 销整个落在浅槽顶 (实体) 下, 不跨让位槽
    RX_WALL = {k: v for k, v in RX_WALL.items() if v is not None}
elif RX_WIN:
    RX_WALL.update(槽内端_件内边=round(RX_X0 - SP_B_X0, 2), 通窗_件内边=round(RX_WIN[0] - SP_B_X0, 2), 通窗_减重槽=round(_pky - RX_WIN[3], 2),
                   通窗_罩锁窝=round(min(_d_rect(x, y, *RX_WIN) for x, y in LOCK_B_LOC) - WELL_FL_D / 2, 2),
                   通窗外端_件外边=round(SP_X1 - RX_WIN[2], 2))
else:
    RX_WALL.update(线槽顶_件顶=round(SP_Z1 - SP_Z0 - RX_WIRE_H, 2))   # 侧入: 槽内端经出线槽通件内边, 不算壁
RX_WALL = {k: v for k, v in RX_WALL.items() if v != math.inf}   # 11-23 B 件顶面全平: 去掉 *_减重槽 项
assert min(v for v in RX_WALL.values()) >= 1.2, RX_WALL
# 承载盘通光孔 Φ3.2 @ (0, 77.5) 壁厚: 线圈腔外壁 r72.5 / 外缘 r85 / fr4_plate 外缘 r82.5 / 其它孔
_oh = [(x, y, 3.4) for x, y in IN_PTS + ANCHOR_PTS + OUT_NUT_PTS + list(B.BB_HOLES) + list(B.MOD_HOLES)] + [(x, y, 3.2) for x, y in MOT_PTS] + [(x, y, B.AC_HOLE_D + 0.4) for x, y in B.AC_HOLES]
OPT_WALL = dict(腔外壁=round(OPT_R - OPT_D / 2 - COIL_R1, 2), 盘外缘=round(RIM_R - OPT_R - OPT_D / 2, 2), fr4外缘=round(FR4_OD / 2 - OPT_R - OPT_D / 2, 2),
                最近孔=round(min(math.dist(OPT_PT, (x, y)) - OPT_D / 2 - d / 2 for x, y, d in _oh), 2),
                底板让位窝=round(min(math.dist(OPT_PT, p) for p in B.BB_HOLES) - OPT_D / 2 - BB_CB_D / 2, 2))
assert SP_EDGE['a_lock_well'] >= 2.0 and SP_EDGE['b_lock_well'] >= 2.0 and SP_EDGE['scr_hole'] >= 0.5 and SP_EDGE['out_cb'] >= 1.0, SP_EDGE

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
                         out_screw=f'M3×{OUT_SCR_L:g} 超薄头 支承 Z{OUT_SCR_BEAR:g} 尾 Z{OUT_SCR_BEAR + OUT_SCR_L:g}, 法兰螺母{"坐" if SP_A_TOP_FLAT else "嵌"}支撑件顶 Z{OUT_NUT_Z[0]:g}–{OUT_NUT_Z[1]:g} 吃 {OUT_ENG:g} (A 件位置)',
                         out_screw_b=f'M3×{OUT_SCR_L_B:g} 超薄头 支承 Z{OUT_SCR_BEAR:g} 尾 Z{OUT_SCR_BEAR + OUT_SCR_L_B:g}, 法兰螺母坐 B 件顶面 Z{OUT_NUT_Z_B[0]:g}–{OUT_NUT_Z_B[1]:g} 吃 {OUT_ENG_B:g} (B 件位置 4 颗)',
                         scr_screw=f'M3×{BAR_SCR_L:g} 超薄头 支承 Z{BAR_SCR_BEAR:g} 尾 Z{BAR_SCR_BEAR + BAR_SCR_L:g}, 铜螺柱 Z{LS.SO_Z0:g}–{LS.SO_Z1:g} 吃 {BAR_SCR_ENG:g}, 离上颗 {round(LS.SO_Z1 - BAR_SCR_BEAR - BAR_SCR_L, 2):g}'),
               edge=SP_EDGE,
               optical=dict(hole=dict(pt=(round(OPT_PT[0], 3), round(OPT_PT[1], 3)), d=OPT_D, note='承载盘全厚通; fr4_plate 同位 Φ3.4 现场配钻 (以承载盘为钻模)', wall=OPT_WALL),
                            rx_slot=dict(conn=RX_CONN, part=GH[RX_CONN]['name'] if RX_CONN in GH else f'{RX_SP_N}×Φ{RX_SP_D:g} 焊线焊盘 P{RX_SP_P:g}', plug=GH_PLUG['name'] if RX_CONN in GH else None,
                                         hole=RX_HOLE, pads=RX_CONN == 'pads' and [tuple(round(v, 3) for v in p) for p in RX_SP_PTS],
                                         loc=RX_CONN == 'pads' and RX_LOC and dict(hole_d=RX_LOC_D, pin_d=RX_PIN_D, pin_h=RX_PIN_H, pts=[tuple(round(v, 3) for v in p) for p in RX_LOC_PTS]),
                                         pcb_local=RX_CONN == 'pads' and RX_PCB_LOCAL, pin_clr=RX_CONN == 'pads' and RX_LOC and RX_PIN_CLR, pcb_chk=RX_CONN == 'pads' and RX_PCB_CHK, loc_x=(round(RX_X0, 3), round(RX_X1, 3)), loc_y=(round(RX_Y0, 3), round(RX_Y1, 3)), z=(SP_Z0, round(RX_Z1, 3)),
                                         pcb=dict(l=RX_PCB_L, w=RX_PCB_W, t=RX_PCB_T, x=(round(RX_PCB_X0, 3), round(RX_PCB_X1, 3)), y=(round(RX_PCB_Y0, 3), round(RX_PCB_Y1, 3)), z=RX_Z_PCB),
                                         header=RX_HDR_X0 is not None and dict(x=(round(RX_HDR_X0, 3), round(RX_HDR_X1, 3)), pad_x=(round(RX_PAD_X0, 3), round(RX_PAD_X1, 3)), top=round(RX_HDR_Z1, 3)),
                                         plug_x0=RX_PLUG_X0 and round(RX_PLUG_X0, 3), plug_top=RX_MATE_Z1 and round(RX_MATE_Z1, 3), win=RX_WIN and tuple(round(v, 3) for v in RX_WIN),
                                         pockets_b=SP_POCKETS['b'], wall=RX_WALL,
                                         top_conflict=RX_TOP_CONFLICT)))
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
    out('screen_sup_b_v1_2b', screen_sup_b_loc, flip=SP_B_TOP_FLAT, color='#C9B458')   # B 上下件 (放 0° 局部; 装 90°/270°); 11-23 顶面全平 ⇒ _print 翻面, 顶面 Z SP_Z1 贴床
    write_doc([('fr4_plate_v1_2b (装配位)', fr4, '#C9B458', None, False), ('rim_ring_v1_2b', rim, '#6AA84F', None, False),
               *[(n, sh, c, None, False) for n, sh, c in SCREEN_PARTS],
               ('线圈 (占位)', coil, '#D9822B', None, False)], B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step', 'rotor_b')
    (B.V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出', OUTD)
