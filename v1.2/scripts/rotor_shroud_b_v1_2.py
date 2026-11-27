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
  - (11-25) 用户「侧面环形和上面盖子能分开装吗」「主要是调试的时候不想反反复复拆了」「改吧」: 每半再拆成 侧环 (shr_a/b, Z30.5–LID_Z0) + 顶盖 (lid_a/b, 厚 2, 外圆 R85 盖在罩壁顶 + 配重唇上):
    每片盖 3 颗 M3×8 超薄头 (+y 40/90/140°, −y 220/270/320°, r77) 从上往下, 头沉盖面 1.5; 盖底 Φ9×1.5 圆凸台落进环上凸块 Φ9.3 窝定位; 法兰螺母从凸块底面塞六角窝 (不跟转不掉), 法兰贴凸块底;
    盖螺丝占掉 4 个配重孔 (40/140/220/320); 罩锁起子孔 / 配重孔仍穿盖 (盖着也能拆整半罩 / 加配重); 拆盖: 抬 5 再往外平移, 不碰灯板/桥板/FPC
    A 件罩锁挪到盘边 (64.8, ±38.8) r75.53 (rotor_b SP_A_STYLE 'rim'), 耳底螺母让位口取消
打印: 侧环倒放 (Z LID_Z0 整面落床, 免支撑), 顶盖顶面落床。
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
# 11-24 A 件 N 沉孔取消 ⇒ 外圈法兰螺母坐 A 件块顶 (Z37.5–41.2), 正在 A 件罩耳下 ⇒ 耳底从螺母内侧 NUT_NOTCH_CLR 起到罩壁内面开让位口 (全耳宽), 顶 = 螺母顶 + NUT_NOTCH_TOP; 耳内段 (锁点周围) 照旧坐块顶
NUT_NOTCH_CLR, NUT_NOTCH_TOP = 0.6, 0.3
NUT_NOTCH_X0 = RB.pol(RB.R_OUT, 22.5)[0] - RB.NUT_FL_D / 2 - NUT_NOTCH_CLR    # 67.2
NUT_NOTCH_Z1 = RB.OUT_NUT_Z[1] + NUT_NOTCH_TOP                               # 41.5
NUT_NOTCH_T = round(BOSS_Z1 + (NUT_NOTCH_X0 - RB.LOCK_A_LOC[0][0] - GUSSET_X0) - NUT_NOTCH_Z1, 2)   # 让位口上方最薄 (斜撑处, 竖直)
NUT_NOTCH = RB.SP_A_TOP_FLAT and RB.SP_A_STYLE == 'ear'          # 11-25 'rim' 锁点在外圈螺丝外侧, 螺母不在耳下
if NUT_NOTCH: assert NUT_NOTCH_T >= 3.0 and NUT_NOTCH_X0 - RB.LOCK_A_LOC[0][0] >= RB.SHR_HEAD_D / 2 + 2.0, (NUT_NOTCH_T, NUT_NOTCH_X0)
OUT_PTS = list(RB.ANCHOR_PTS) + list(RB.OUT_NUT_PTS)   # 外圈 8 颗法兰螺母 (嵌在支撑件顶面, 顶低于件顶 0.3, 罩子之前装; 罩耳可盖过)
# 配重孔: 候选 原 RS.W_A + 40/140/220/320, 去掉与起子孔相碰的 (中心距 < (ACC_D+5.8)/2 + 1)
# 11-25 顶盖单独拆: 每片 3 颗 M3×8 超薄头 (Φ7×1.5) 从上往下, 螺母 (M3 法兰) 从环上凸块底面塞进六角窝, 法兰朝下贴凸块底
LID_T, LID_Z0 = RS.LID_T, RS.LID_Z0              # 2 / 69.58 盖底 = 罩壁顶 = 唇顶 (盖外圆 R1)
LS_R, LS_ANG = 77.0, {'a': [40.0, 90.0, 140.0], 'b': [220.0, 270.0, 320.0]}
LS_ALL = LS_ANG['a'] + LS_ANG['b']
LS_PTS = {a: pol(LS_R, a) for a in LS_ALL}
LS_L = 8.0
LS_CB_D, LS_CB_H = 7.4, 1.5                       # 盖面沉孔
LS_BEAR = Z1 - LS_CB_H                            # 70.08
LS_TIP = LS_BEAR - LS_L                           # 62.08 = 螺母底
LS_BOSS_D, LS_BOSS_H = 9.0, 1.5                   # 盖底圆凸台 (定位 + 加厚到 2)
LS_SEAT_D, LS_SEAT_H = 9.3, 1.6                   # 环上凸台窝 (每边 0.15, 底 0.1)
LS_NUT_Z = (LS_TIP, LS_TIP + RB.NUT_T)            # 62.08–65.78
# 11-26 用户 (红框 L)「这个位置，用法兰盘螺母，就是通孔加沉孔那个，深度3.8mm的那个」: 六角窝 → 底面 Φ8 圆沉孔深 3.8 (同 sup_a S / SP_NUT_CB_D),
#   螺母整颗进沉孔 (法兰齐凸块底); 凸块底下移 1 (63.08 → 62.08) 保持窝间壁 2.1, 螺母 / M3×8 位置不变; 圆孔螺母会跟转, 拧时扳手卡住
LS_NUT_CB = True
LS_CB_NUT_D, LS_CB_NUT_H = RB.SP_NUT_CB_D, 3.8   # Φ8 × 3.8
LS_PAD_Z0 = LS_TIP if LS_NUT_CB else LS_TIP + RB.NUT_FL_H   # 62.08 凸块底 (原 63.08, 法兰贴这里)
LS_HEX_AF, LS_HEX_Z1 = RB.WELL_AF_LOCK, (LS_PAD_Z0 + LS_CB_NUT_H) if LS_NUT_CB else LS_TIP + RB.NUT_T + 0.1   # 窝顶 Z65.88 (圆沉孔 / 原六角窝 AF6.0)
LS_WEB = round(LID_Z0 - LS_SEAT_H - LS_HEX_Z1, 2) # 凸台窝底 ↔ 六角窝顶 2.1
LIP_TRIM = 3.0                                    # 唇两端各收 3° (33 → 36°, 盖螺丝凸块 40±4.7° 接上), 免被 A 件起子孔 (30.9°) 啃出尖角
LS_PAD_HW, LS_PAD_R0 = 6.3, 70.7                  # 凸块半宽 / 内端 r
assert LS_WEB >= 2.0 and LS_R + LS_CB_D / 2 <= R0 - 0.5
# 11-27 用户「罩子配重的螺丝是从上往下锁吧，这个沉孔直径应该是螺丝头的8mm吧」「下边应该锁法兰螺母吧m3的，现在距离也不够」:
#   沉孔 Φ5.8 → Φ8 (深不变 3.2, 头在盖底下); 唇下改挂 M3 法兰螺母 (法兰 Φ7.6): 原 r79 时法兰外沿 r82.8 顶进罩壁 ⇒ 孔圈内移到 W_R_B, 法兰离罩壁内面 0.6;
#   唇内沿 RS.LIP_R0 r76 → LIP_R0_B (Φ8 沉孔内沿外再留 1.1)
W_NEW = True
W_CB_D_B = 8.0 if W_NEW else RS.W_CB_D
W_R_B = round(R0 - RB.NUT_FL_D / 2 - 0.6, 2) if W_NEW else RS.W_R      # 77.6
LIP_R0_B = round(W_R_B - W_CB_D_B / 2 - 1.1, 2) if W_NEW else RS.LIP_R0  # 72.5
W_NUT_Z = (RS.LIP_Z0 - RB.NUT_T, RS.LIP_Z0)                             # 法兰朝上贴唇底
def _wa_ok(a):
    p0 = pol(W_R_B, a)
    return all(math.dist(p0, p) >= (ACC_D + W_CB_D_B) / 2 + 1.0 for p in MNT_PTS) and all(math.dist(p0, p) >= LS_PAD_HW + W_CB_D_B / 2 + 0.8 for p in LS_PTS.values())
W_CAND = sorted(set(RS.W_A) | {40.0, 140.0, 220.0, 320.0})
W_A = sorted(a for a in W_CAND if _wa_ok(a))
def acc_cut(x, y, z0, z1):
    """起子孔 Φ ACC_D, 只切到罩壁内面 (r ≤ R0)"""
    return common(cyl(x, y, ACC_D, z0, z1), cyl(0, 0, 2 * R0, z0 - 1, z1 + 1))
W_DROP = [a for a in W_CAND if not _wa_ok(a)]
# 11-20 夜 两端竖缝收窄: 原 y RS.SLOT_Y0…SLOT_Y1 (−14.79…5.41, 让天线板) → 只让灯板 + 夹条端头 (两端 x±81.88 处 y −8.79…−0.59, 外角 r82.35 进罩壁) 各 0.4
SLOT_Y0, SLOT_Y1 = -8.79 - 0.4, 0.0 + 0.35     # −9.19…+0.35 (跨分缝 y=ECC −4.69); 11-21 上边 −0.19 → +0.35: 灯板 A 两端 MIP 顶到 y0.0 (v2_boards 灯板, x80.4–81.88), 原缝边离它 0.12
# 11-26 用户「两个罩子可以是一个造型吗」「侧环做成一个，顶盖不动」: 侧环竖缝改关于 y=0 对称 (±9.19), +y 环两端各切掉 y0.35–9.19 一条 ⇒ −y 环 = +y 环转 180° (同件 ×2);
#   顶盖仍按 SLOT_Y0/SLOT_Y1 (两种); 天线槽被新缝吃掉 ⇒ LS.ANT_B_ANG rim 改 15.5/195.5
RING_SYM = True
# 11-26 用户「顶盖是不是只留安装的3个螺丝孔就够了，顶盖是嵌合到罩子会不会好一点」「改吧，按外裙做」:
#   顶盖去掉配重孔 / 起子孔 (调平衡、拆罩先拆盖), 只留 3 盖螺丝 + 桥板让位槽; 盖外缘下垂外裙 R(R1−SK_T)…R1 高 SK_H−SK_CLR, 罩住环顶外半 (箍住两半侧环防离心外张, 接缝藏裙下)
#   侧环顶外半削台阶 R(R1−SK_T−SK_CLR)…外 × 深 SK_H (径向单边 0.1, 裙底留 0.1)
LID_HOLES = False                     # True = 恢复 11-25 顶盖配重孔 + 起子孔
LID_SKIRT = False                     # 11-27 用户「盖子和罩子不嵌合也行」(外裙打印边缘差) ⇒ 取消外裙/台阶, 盖平放在环顶
SK_T, SK_H, SK_CLR = 1.5, 2.0, 0.1
# 11-27 用户「这个圆形的罩子现在不是一个圆，是不是可以闭合了」: 侧环做成整圈一件 (RING_ONE), 两端竖缝 → 罩壁内面浅槽 (只让灯板/夹条端头, 外角 r82.35 + 0.4),
#   槽 y SLOT_Y0…SLOT_Y1 全高, 槽底 r GROOVE_R, 外面剩壁 R1−GROOVE_R; 整圈从上往下套 (槽通到环顶), shr_b = None
RING_ONE = True
GROOVE_R = 82.75
if RING_ONE: RING_SYM = False
RING_SLOT_Y = (SLOT_Y0, -SLOT_Y0) if RING_SYM else (SLOT_Y0, SLOT_Y1)
# 11-20 夜 天线 FPC 18.5×37.7 改贴罩子内壁 (用户「贴到罩子吧」「罩子天然有这个侧立面」「这个天线是fpc的」), 定位浅槽 38.1×18.9×0.3, 长边沿 Z, 槽底 = 圆柱面 r82.3
#   位置 (LS.ANT_B_ANG): 两端 0°/180° 附近罩壁被竖缝 + 罩耳 (板本地 y 15.5…24.5 接壁处 ±17.38°) 夹住只剩弧长 ~15 < 18.9 ⇒ 挪到 罩耳外侧 ~ 唇 (33°) 之间, 中心 25.2° (+y 半) / 205.2° (−y 半)
# 11-21 A 件罩耳 (板本地 y 26…35, 接壁 18.5°…25.3°) 正好压在原天线位 25.2° ± 6.6° ⇒ 天线挪到 竖缝 (≈0°) 与 A 件罩耳之间: 中心 ANT_ANG_NEW
#   ⚠ 天线实体 / 原值在 led_support (LS.ANT_B_ANG = 25.2/205.2) —— 本脚本不改 led_support, 槽按新角度切, 校核用本地重建的天线 (ant_new); 需同步 LS.ANT_B_ANG
ANT_ANG_NEW = LS.ANT_B_ANG[0]  # 11-24 A 直条 (锁 y±20.5, 耳 y16–25 接壁 11.3°–17.8°) 时天线回原位 25.2
ANT_ANG = (ANT_ANG_NEW, ANT_ANG_NEW + 180.0)
ANT_HA = math.degrees(LS.ANT_W / 2 / R0)         # 6.60° 半角 (弧长 18.9 @r82)
ANT_Z0, ANT_Z1 = LS.ANT_B_ZC - LS.ANT_L / 2, LS.ANT_B_ZC + LS.ANT_L / 2   # 32.68–70.78 (顶离顶盖底 Z71.08 0.3)
_EAR_A_IN = math.degrees(math.asin((RB.LOCK_A_LOC[0][1] - EAR_HW) / R0))     # A 件 +y 罩耳下边接壁角 18.5°
_SLOT_A = math.degrees(math.atan2(RING_SLOT_Y[1], R0))                               # 竖缝上边 (y +0.35) ≈ 0.24°
ANT_MARGIN = dict(ear=round(_EAR_A_IN - (ANT_ANG[0] + ANT_HA), 2),          # 槽边 ↔ A 件罩耳 (度)
                  slot=round((ANT_ANG[0] - ANT_HA) - _SLOT_A, 2)) if RB.SP_A_STYLE in ('ear', 'rim') else \
             dict(ear=round((ANT_ANG[0] - ANT_HA) - math.degrees(math.asin((RB.LOCK_A_LOC[0][1] + EAR_HW) / R0)), 2),   # 11-24 直条: 天线在 A 罩耳上边之外
                  lip=round(min(a0 for a0, a1 in RS.LIP_ARCS if a0 > ANT_ANG[0]) - (ANT_ANG[0] + ANT_HA), 2) if any(a0 > ANT_ANG[0] for a0, a1 in RS.LIP_ARCS) else 9.9)
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
# 11-27 用户「顶盖改一下，盖住这个pcb，就是两个半圆的感觉」: 桥板顶 Z70.5 原来穿出顶盖 (通槽) ⇒ 槽上留顶皮 (盖倒放打印, 顶皮是贴床头几层, 不用搭桥)
LID_BR_ROOF = True
BR_TOP = round(B.Z_SCR0 + 36.0, 2)               # 桥板 PCB 上沿 70.5 (fpc_v1_2 bridge_a/b 实测 34.49–70.5)
BR_ROOF_T = 0.8                                   # 顶皮厚 (0.2 层高 4 层)
BR_ROOF_Z0 = round(Z1 - BR_ROOF_T, 2)             # 顶皮底 70.78
assert BR_ROOF_Z0 - BR_TOP >= 0.25, (BR_ROOF_Z0, BR_TOP)
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
    for a0, a1 in RS.LIP_ARCS: s = fuse(s, sector(LIP_R0_B, R0 + 0.5, RS.LIP_Z0, RS.LID_Z0, a0 + LIP_TRIM, a1 - LIP_TRIM))
    clip = cyl(0, 0, 2 * (R0 + 0.5), BOSS_Z0 - 1, Z1 + 1)
    for a in RB.SP_ANG:               # 耳坐支撑件顶 (局部沿 x 的长条: 锁点内侧 EAR_IN → 罩壁, 宽 9, 耳顶平) + 45° 斜撑 (从锁点外 GUSSET_X0 起) 接罩壁
        for lx, ly in RB.SHR_LOCK_SET[a]:
            y0, y1 = ly - EAR_HW, ly + EAR_HW
            b = fuse(gbox(lx - EAR_IN, y0, BOSS_Z0, R0 + 0.5, y1, BOSS_Z1),
                     prism_xz([(lx + GUSSET_X0, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 + (R0 + 0.5 - lx - GUSSET_X0))], y0, y1))
            if NUT_NOTCH and RB.SP_TYPE[a] == 'a':   # 11-24 外圈螺母让位口
                b = cut(b, gbox(NUT_NOTCH_X0, y0 - 1, BOSS_Z0 - 1, R0 + 5, y1 + 1, NUT_NOTCH_Z1))   # 只切耳 (融罩壁之前), 罩壁不动
            s = fuse(s, xf(common(b, clip), rotz(a)) if a else common(b, clip))
    for a in LS_ALL:                  # 11-25 盖螺丝凸块 (唇下多 1.5, 往里到 LS_PAD_R0)
        s = fuse(s, common(xf(gbox(LS_PAD_R0, -LS_PAD_HW, LS_PAD_Z0, R0 + 0.5, LS_PAD_HW, LID_Z0), rotz(a)), cyl(0, 0, 2 * (R0 + 0.5), LS_PAD_Z0 - 1, Z1)))
    s = clean(s)
    for a in LS_ALL:
        x, y = LS_PTS[a]
        s = cut(s, cyl(x, y, 3.4, LS_PAD_Z0 - 1, Z1 + 1), cyl(x, y, LS_SEAT_D, LID_Z0 - LS_SEAT_H, LID_Z0 + 0.01), cyl(x, y, LS_CB_NUT_D, LS_PAD_Z0 - 1, LS_HEX_Z1) if LS_NUT_CB else RB._hexp(x, y, LS_HEX_AF, LS_PAD_Z0 - 1, LS_HEX_Z1, a))
    for x, y in MNT_PTS:
        s = cut(s, cyl(x, y, 3.4, BOSS_Z0 - 1, BOSS_Z1 + 0.01), acc_cut(x, y, BOSS_Z1, Z1 + 1))
    for a in W_A:                     # 配重孔 (原顶盖螺丝位也改成配重孔; 11-20 按新锁点增删)
        x, y = pol(W_R_B, a)
        s = cut(s, cyl(x, y, 3.4, RS.LIP_Z0 - 1, Z1 + 1), cyl(x, y, W_CB_D_B, RS.W_BEAR, Z1 + 1))
    for sx in (1, -1):                # 两端竖缝 (11-20 夜 天线板取消, 缝收窄到只让灯板/夹条端头); 11-27 整圈: 只切到 GROOVE_R 的内面槽
        x0, x1 = (RS.SLOT_X0, R1 + 1) if sx > 0 else (-R1 - 1, -RS.SLOT_X0)
        g = gbox(x0, RING_SLOT_Y[0], Z0 - 1, x1, RING_SLOT_Y[1], Z1 + 1)
        s = cut(s, common(g, cyl(0, 0, 2 * GROOVE_R, Z0 - 2, Z1 + 2)) if RING_ONE else g)
    if LID_SKIRT: s = cut(s, B.ann(R1 - SK_T - SK_CLR, R1 + 1, LID_Z0 - SK_H, LID_Z0 + 1))   # 11-26 环顶外半台阶 (顶盖外裙落进来)
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
    s = cut(fuse(plate, *fill), gbox(x0, min(yb, yb0 - 0.01 * (1 if k == 'a' else -1)), RS.LID_Z0 - 1, -x0, max(yb, yb0 - 0.01 * (1 if k == 'a' else -1)), Z1 + 1), yin_cut)
    if LID_BR_ROOF:                                   # 桥板槽上补顶皮 (槽内边 = 盖内边, 外边 = 槽外边)
        lo, hi = (yi + LID_YIN_ADD, yb) if k == 'a' else (yb, yi - LID_YIN_ADD)
        s = fuse(s, gbox(x0, lo, BR_ROOF_Z0, -x0, hi, Z1))
    return clean(s)


def half(k):
    """侧环半 (Z0–LID_Z0): 11-25 起不含顶盖"""
    sy = 1 if k == 'a' else -1
    y0, y1 = (SPLIT_Y, 100) if sy > 0 else (-100, SPLIT_Y)
    s = common(ring_body_b(), gbox(-100, y0, Z0 - 1, 100, y1, LID_Z0))
    if sy > 0 and BB_NOTCH: s = cut(s, bb_notch())  # 底板 R85 缺口
    return clean(s)


def lid(k):
    """顶盖 (Z LID_Z0–Z1, 外圆 R1 盖在罩壁顶上): 原盖板 + 罩壁顶一圈 (两端竖缝 / 内边同原盖), 配重孔 / 起子孔穿盖, 3 个沉头孔 + 底面圆凸台"""
    sy = 1 if k == 'a' else -1
    yi = RS.LID_YIN[k] + sy * LID_YIN_ADD
    yi = max(yi, SLOT_Y1) if sy > 0 else min(yi, SLOT_Y0)
    edge = common(B.ann(R0 - 3.0, R1, LID_Z0, Z1), gbox(-100, yi, LID_Z0 - 1, 100, 100, Z1 + 1) if sy > 0 else gbox(-100, -100, LID_Z0 - 1, 100, yi, Z1 + 1))
    s = fuse(lid_plain(k), edge)
    s = fuse(s, *[cyl(*LS_PTS[a], LS_BOSS_D, LID_Z0 - LS_BOSS_H, LID_Z0 + 0.5) for a in LS_ANG[k]])
    for a in LS_ANG[k]: s = cut(s, cyl(*LS_PTS[a], 3.4, LID_Z0 - 5, Z1 + 1), cyl(*LS_PTS[a], LS_CB_D, LS_BEAR, Z1 + 1))
    if LID_SKIRT:                     # 11-26 外裙 (盖同侧半圆, 竖缝处随盖内边截止)
        s = fuse(s, common(B.ann(R1 - SK_T, R1, LID_Z0 - SK_H + SK_CLR, LID_Z0 + 0.01), gbox(-100, yi, LID_Z0 - SK_H - 1, 100, 100, Z1) if sy > 0 else gbox(-100, -100, LID_Z0 - SK_H - 1, 100, yi, Z1)))
    for a in (W_A if LID_HOLES else []):   # 配重孔上方顶盖开孔 (配重螺丝从罩顶插); 11-26 起默认不开
        x, y = pol(RS.W_R, a)
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, cyl(x, y, RS.W_CB_D, LID_Z0 - 1, Z1 + 1))
    for x, y in (MNT_PTS if LID_HOLES else []):   # 起子孔穿顶盖; 11-26 起默认不开
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, acc_cut(x, y, LID_Z0 - 3, Z1 + 1))
    return clean(s)


if RING_ONE:
    shr_a, shr_b = clean(common(ring_body_b(), gbox(-100, -100, Z0 - 1, 100, 100, LID_Z0))), None
else:
    shr_a, shr_b = half('a'), half('b')
if RING_SYM:                          # 11-26 同件: 校核 −y 环 = +y 环转 180° (对称差 ≈0), 然后直接用转出来的, 保证两个文件逐位同形
    _r = xf(shr_a, rotz(180)); RING_SYM_DIFF = round(vol(cut(_r, shr_b)) + vol(cut(shr_b, _r)), 3)
    assert RING_SYM_DIFF < 0.5, RING_SYM_DIFF
    shr_b = _r
lid_a, lid_b = lid('a'), lid('b')
PARTS4 = [('rotor_shroud_b_a_v1_2b', '转子罩 侧环 (整圈)' if RING_ONE else '转子罩 +y 侧环', shr_a, '#6FA8DC')] + ([] if RING_ONE else [('rotor_shroud_b_b_v1_2b', '转子罩 −y 侧环', shr_b, '#93C47D')]) + [
          ('rotor_shroud_lid_a_v1_2b', '转子罩 +y 顶盖', lid_a, '#CFE2F3'), ('rotor_shroud_lid_b_v1_2b', '转子罩 −y 顶盖', lid_b, '#D9EAD3')]

def balance():
    """罩 4 件 PLA 1.24 g/cm³ 的质心偏移 (g·mm, 相对转轴), 各件 + 合计"""
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    out = {}; tx = ty = 0.0
    for k, sh in (('a', shr_a), ('b', shr_b), ('lid_a', lid_a), ('lid_b', lid_b)):
        if sh is None: continue
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(sh, g); c = g.CentreOfMass(); m = g.Mass() * 1.24e-3
        out[k] = dict(m=round(m, 2), cx=round(c.X(), 3), cy=round(c.Y(), 3), Ux=round(m * c.X(), 1), Uy=round(m * c.Y(), 1)); tx += m * c.X(); ty += m * c.Y()
    out['U'] = dict(x=round(tx, 1), y=round(ty, 1), abs=round(math.hypot(tx, ty), 1))
    return out


def report():
    _fpc = RB.load_fpc()
    _P = {k: v for k, v in dict(a=shr_a, b=shr_b, lid_a=lid_a, lid_b=lid_b).items() if v is not None}
    rep = dict(vol={k: round(vol(v), 1) for k, v in _P.items()}, mass_g={k: round(vol(v) * 1.24e-3, 1) for k, v in _P.items()},
               valid={k: BRepCheck_Analyzer(v).IsValid() for k, v in _P.items()}, solids={k: len(solids(v)) for k, v in _P.items()},
               lid=dict(scr=f'M3×{LS_L:g} 超薄头 r{LS_R:g}', ang=LS_ALL, bear=LS_BEAR, tip=LS_TIP, nut_z=LS_NUT_Z, web=LS_WEB),
               boss=dict(z=(BOSS_Z0, BOSS_Z1), w=BOSS_W, ear_loc=dict(x0=EAR_X0, y=(EAR_Y0, EAR_Y1)), hole_r=HOLE_R, ang=MNT_A, screw=f'DIN912 M3×{MNT_L:g} 从耳顶往下 尾 Z{SCR_TIP:g}', nut_z=NUT_Z, acc_d=ACC_D,
                         w_a=W_A, w_drop=W_DROP, n_w=len(W_A)),
               balance=balance(), slot_y=(SLOT_Y0, SLOT_Y1), br_pocket={k: round(v[1], 3) for k, v in BR_POCKET.items()}, antenna=dict(ang=ANT_ANG, half_ang=round(ANT_HA, 3), z=(ANT_Z0, ANT_Z1), margin_deg=ANT_MARGIN))
    others = dict(承载盘B=RB.rim, **{n: sh for n, sh, _ in RB.SCREEN_PARTS}, 底板=RB.VB['baseboard'], 底板器件=RB.VB['bb_parts'], CZ06=RB.VB['cz06'],
                  灯板=RB.VB['led'], 夹条=LS.bar_s, 顶部件=LS.top, 无线托盘=RB.WH.H, FPC_A=_fpc['fpc_a_v1_2'], FPC_B=_fpc['fpc_b_v1_2'],
                  桥板A=_fpc['bridge_a_v1_2'], 桥板B=_fpc['bridge_b_v1_2'], FPC座=_fpc['bb_fpc_seats_v1_2'], 天线a=ant_new_a, 天线b=ant_new_b)
    inter = {}
    w_nuts = [cyl(*pol(W_R_B, a), RB.NUT_FL_D, *W_NUT_Z) for a in W_A]   # 11-27 唇下法兰螺母 (包络 Φ7.6)
    for n1, s1 in (('环A(+y)', shr_a), ('环B(-y)', shr_b), ('盖A(+y)', lid_a), ('盖B(-y)', lid_b), *[(f'配重螺母{a:g}°', n) for a, n in zip(W_A, w_nuts)]):
        if s1 is None: continue
        for n2, s2 in others.items():
            v = common_v(s1, s2)
            if v > 1e-3: inter[f'{n1} × {n2}'] = round(v, 3)
    for (n1, s1), (n2, s2) in __import__('itertools').combinations(_P.items(), 2):
        v = common_v(s1, s2)
        if v > 1e-3: inter[f'罩 {n1} × {n2}'] = round(v, 3)
    rep['interference_mm3'] = inter
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


if __name__ == '__main__':
    rep = report()
    for name, _, sh, col in PARTS4:
        d = B.V12 / 'models' / name; d.mkdir(parents=True, exist_ok=True)
        write_doc([(name, sh, col, None, False)], d / f'{name}.step', name)
        BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(d / f'{name}.stl'))
        fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); t = xf(sh, fx)   # 倒放: 罩顶落床
        tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, -bbox(t)[2])); t = xf(t, tz)
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(d / f'{name}_print.stl'))
    (B.V12 / 'models' / 'rotor_shroud_b_a_v1_2b' / 'shroud_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('ok')
