"""
XT60 电源接头压块 xt60_clamp_16p6x9p2x23p9 (v4.10, 2026-09-16)

用户: 把 XT60 电源接头锁到底座 (v4 M6 网格板, 节距 25, 板厚 13)。

尺寸来源:
  v1/v2 用用户口述包络 16.6 × 9.7 × 24。2026-09-16 用户给了 AMASS XT60H-M 图纸 (23.90 / 16.40 × 9.20),
  图上量测 + 卡尺复核, 接头分两段:
      插合本体 (光面, 印 XT60H-M)          11.9 长 (图上 11.88), 截面 15.4 × 8.2
      出线端护套 (带波纹, 往后端收窄)       12.0 长 (图上 12.02), 截面最大 16.4 × 9.2
  本体相对护套: 9.2 方向**上下各缩 0.5** (用户卡尺); 16.4 方向两侧基本对称, 偏心约 0.07 可忽略
  (曾在用户画了红框的截图上量成 0.78/0.26 → 偏心 0.26, 是红框压线的误差; 干净原图 0.56/0.42, 官方 2025V0 图 0.53/0.40)。

朝向 (v4 修的就是这个):
  v3 把 16.4×9.2 那段放在开口面、15.4×8.2 放在堵头侧 —— **做反了**。
  用户 2026-09-16 看实物纠正:「应该是没有挡板这边是小一点」; 照片里黑色护套顶着堵头、线从那头出去。
  => 开口面 (没挡板) = 插合本体 (小); 堵头 = 护套 (大, 线从护套后端出来走 U 口)。
  v3 实际扣上去: 9.2 高的护套顶在 8.6 的低槽顶 => 压块扣不下去。

v4.1 (同日, 用户看 v4 图纸圈了两个槽宽): 「这俩应该是16.6和15.6，不要留余量，紧配」
  => 护套宽 16.6 / 本体宽 15.6 (用户给的数, 与他 09-14 最早口述的 16.6 一致; 图纸标 16.40), 槽宽 = 接头宽, 单侧间隙 0。
     (本体偏心实测约 0.07, 零间隙下可忽略, 模型按同轴。)
v4.2 (同日): 用户「所有间隙都改为0」=> 槽台阶提前量 0 (台阶对齐, 轴向零窜动)、垫片四周/前后间隙 0
     (垫片 = 本体底面投影 15.6 × 11.9 × 0.5)。M6 过孔 Φ6.5 不算间隙, 未动。
v4.3 (同日): 用户看详图 B 槽顶 9.0 / 8.6:「这个应该是8.7和9.2吧」=> 高度压紧量也 0,
     槽顶 = 接头顶 (护套 9.2 / 本体 0.5 + 8.2 = 8.7), 件高 12.0 -> 12.2。所有方向都按接头名义尺寸。
v4.4 (同日): 用户圈主视图件高 12.2:「厚度改为11mm」=> 件高 11 定死, 槽顶厚由它反算 (护套段 1.8 / 本体段 2.3)。
v4.5 (同日): 用户「这两个底部垫片这样会掉，改一下，各自改成和整个件一样的长宽，基础厚度2mm，然后通过m6螺丝孔的位置保证不掉」
     => 件 2 改成底板垫片: 外形 = 压块 38 × 26.9, 底板厚 2, 本体投影区凸台 15.6 × 11.9 高 0.5 (总厚 2.5),
        2×Φ6.5 与压块同轴, M6 穿过即定位; 叠层高 2 + 11 = 13, 螺丝长度按叠层算。
v4.6 (同日): 用户「出线端就都在中央吧，直径都改为2.5mm」=> U 口 Φ3 圆心 1.5 (贴板) 改为 Φ2.5 = 线径零余量,
     圆心 = 护套高/2 = 4.6 (针轴线, 线直出), 仍是 U 型开到底面; 间距仍按用户最早给的 7 (官方针距 7.2)。
v4.7 (同日): 用户「上下两个件加一些嵌套，卡在一起」+ 俯视图红框标 左/右/开口端 三条边 +「因为有一个出线的口，
     下边这个部分正好可以和上边卡成一个圆形」+「厚度2mm，高度2mm」=>
     (a) 止口: 底板顶面沿 左右 X 端 (全长) + 开口端 (槽口处断开) 凸起 2×2 边框, 压块底面同位置切 2×2 台阶, 零间隙;
     (b) 堵头处不做边框, 改为底板在每个 U 口下立舌头 (宽 2.5 × 长 3 = 堵头厚, 高到针轴 4.6, 顶面挖 R1.25),
         与压块 U 口半圆顶扣成 Φ2.5 整圆。
v4.8 (同日): 用户画草图确认舌头扣圆 +「两个件就留0.1mm装配就行」=> 压块 ↔ 底板垫片 嵌套配合面单边 ASSY_CLR = 0.1:
     压块止口台阶 (2+0.1)×(2+0.1) / 舌头宽 2.5−0.2 = 2.3 / 凸台宽 15.6−0.2 = 15.4。接头配合与出线圆 R1.25 仍零余量。
v4.9 (同日): 用户「上下两个件组和后从外边看要是一个立方体，只是有孔而已」=> 台阶高度方向不留间隙 (2.1×2.0),
     边框顶面贴台阶顶面, 外表面平齐; 新增 6 面外观 assert (外表面只有 M6 孔 / 接头口 / 出线口)。
v4.10 (同日): 用户「底板的四个边都加凸台吧」「圆孔的位置简单一点吧」(草图: 下件平顶到线底, 上件 U 口)
     「高度不足2mm无所谓」「1.四周都加凸台，高度2mm需要砍高度的位置就砍」
     「2.凸台厚度在出线这里是不是改成3mm和之前出线的那个厚度一致好一点，别的位置是2mm就行」
     => 取消舌头; 止口四边高 2: 左右 / 开口端宽 2 (开口端槽口处断开), 后边 (出线边) 宽 3 = 堵头厚, X 全宽;
        出线处若线底 LEDGE < 2 就在 U 口宽度内把后边框削到 LEDGE (XT60 线底 3.35, 不削; MR30 削到 1.4)。
        出线孔 = 压块 U 口 (半圆顶 + 直边) + 后边框顶 (平底)。底板四个方向都被止口卡住。

v4 做法 (宽度已按 v4.1 改):
  1) 阶梯槽: 本体段 (开口侧) 15.6 × 8.7 / 护套段 (堵头侧) 16.6 × 9.2, 宽高都 = 接头 (过盈 0, 间隙 0)。
     槽台阶与接头台阶对齐 (STEP_MARGIN=0; v4 曾提前 0.3)。
  2) 轴向限位: 插入 (+Y) 靠堵头挡; 拔出 (-Y) 护套前端面直接顶窄槽台阶 —— 零窜动, 不靠摩擦。
  3) 件 2 底板垫片 xt60_shim: 和压块同外形的 2 厚底板 + 本体底面投影区凸台 (高 0.5 = 本体底面离护套底面),
     2×Φ6.5 与压块同轴, M6 穿过压块和底板拧进网格板 => 底板被螺杆定位不会掉 (最多晃 0.25);
     凸台卡进本体段槽 (两侧各留 ASSY_CLR 0.1), 托住本体; 护套直接坐底板。

沿用的取舍 (用户选定):
  - 2×Φ6.5 @ 孔距 25 横跨接头, 大扁头坐平顶面; 孔心到开口面 12.5 (落在护套段)。
  - 堵头 3 厚, U 型出线口 Φ2.5 (= 线径, 零余量) 半圆顶 + 直边开到底面, 圆心高 4.6 = 针轴线, X=±3.5 (间距 7)。
  - 槽深 = 接头全长 23.9, 护套后端直接顶堵头。线从护套尾孔与针同轴出来 (离底板顶面 4.6), U 口圆心就在 4.6,
    线直着出去不用弯 (v4.5 以前 U 口贴板圆心 1.5, 弯线空间 0; 用户先说不改, 加底板垫片后改为中央出线)。

建模简化: 护套按 16.6 × 9.2 的方盒算 (实物往后端收窄, 矩形槽只会更松, 贴合只发生在护套前段满截面那几毫米)。

坐标: X = 两孔连线 (横跨接头宽度), Y = 槽方向 (-Y 开口, +Y 堵头), Z 向上, 贴板底面 Z=0。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

VERSION = "v4.10"

# ===== 参数 =====
# 接头 (AMASS 图纸 + 卡尺)
BODY_W,   BODY_H   = 15.6, 8.2    # 插合本体 (开口面一侧); 宽 15.6 用户 09-16 指定 (图纸推 15.4)
SHEATH_W, SHEATH_H = 16.6, 9.2    # 出线端护套 (堵头一侧, 最大截面); 宽 16.6 用户指定 (图纸 16.40)
BODY_L,   SHEATH_L = 11.9, 12.0
XT_L      = BODY_L + SHEATH_L     # 23.9 总长
XT_ECC    = 0.0                   # 本体相对护套偏心: 干净图/官方图约 0.07, 按同轴
BODY_LIFT = (SHEATH_H - BODY_H) / 2   # 0.5 本体底面离板 (用户: 上下各 0.5)

# 槽
SIDE_CLR_S  = 0.0     # 护套段 槽宽单侧间隙 —— 用户要求紧配不留余量
SIDE_CLR_B  = 0.0     # 本体段 槽宽单侧间隙 —— 同上
PRELOAD_S   = 0.0     # 护套段 压紧量 (槽顶比接头低多少) —— 用户: 槽顶 9.2 (v4.2 为 0.2)
PRELOAD_B   = 0.0     # 本体段 压紧量 —— 用户: 槽顶 8.7 (v4.2 为 0.1)
STEP_MARGIN = 0.0     # 槽台阶比接头台阶往开口侧提前多少 = 拔出方向窜动量; 用户要求所有间隙 0 (v4 为 0.3)

# 件 2 底板垫片 (v4.5): 外形 = 压块, 底板 BASE_T + 本体投影区凸台 SHIM_T, 2×Φ6.5 同压块孔 (M6 定位防掉)
BASE_T          = 2.0         # 底板厚 (用户「基础厚度2mm」)
RIM_W           = 2.0         # 止口边框宽 (用户「厚度2mm」): 底板凸起 / 压块底面台阶, 零间隙
RIM_H           = 2.0         # 止口高 (用户「高度2mm」)
ASSY_CLR        = 0.1         # 压块 ↔ 底板垫片 嵌套面单边装配间隙 (用户「两个件就留0.1mm装配」)
SHIM_T          = BODY_LIFT   # 0.5 凸台高
SHIM_CLR        = ASSY_CLR    # 凸台在本体段槽里的 ±X 间隙 (两件之间, 0.1)
SHIM_OPEN_INSET = 0.0         # 凸台前端缩进开口面
SHIM_BACK_GAP   = 0.0         # 凸台后端离护套前端面

HTOP        = 11.0    # 件高 (用户 09-16 指定「厚度改为11mm」; 槽顶厚由它反算)
CAP_T       = 3.0     # 堵头厚 (用户指定)
WIRE_D      = 2.5     # 出线口径 = 线径 2.5, 零余量 (用户「直径都改为2.5mm」)
WIRE_PITCH  = 7.0     # 出线口间距 (用户最早指定; 官方针距 7.2)
WIRE_ZC     = SHEATH_H / 2   # U 口圆心高 = 针轴线 4.6 (用户「出线端就都在中央」)
PITCH       = 25.0    # 孔距 = 网格节距 (用户选定, 横跨接头)
HOLE_D      = 6.5     # M6 通孔
END         = 6.5     # 孔心到 X 端面 (>= 头半径 6.25)
HOLE_Y_OPEN = 12.5    # 孔心到开口面 (用户指定)

# 五金 / 板 (只用于校核)
HEAD_D, HEAD_T = 12.5, 2.6   # M6 大扁头 实测
PLATE_T    = 13.0            # v4 网格板厚
M6_SHANK_D = 6.0             # M6 螺杆外径

SEG = 96

# ===== 导出量 =====
CH_W_B = BODY_W + 2 * SIDE_CLR_B             # 15.6 本体段槽宽
CH_H_B = BODY_LIFT + BODY_H - PRELOAD_B      #  8.7 本体段槽高 (从板面算)
CH_W_S = SHEATH_W + 2 * SIDE_CLR_S           # 16.6 护套段槽宽
CH_H_S = SHEATH_H - PRELOAD_S                #  9.2 护套段槽高
T_TOP  = HTOP - CH_H_S                       # 1.8 槽顶厚 (护套段); 本体段 HTOP - CH_H_B = 2.3
STACK_H = BASE_T + HTOP                     # 13 叠层高 (底板垫片 + 压块), 螺丝长度按它算
HX     = PITCH / 2                           # 12.5
HALF_L = HX + END                            # 19
L      = 2 * HALF_L                          # 38
Y_OPEN  = -XT_L / 2                          # -11.95 开口面
Y_XSTEP = Y_OPEN + BODY_L                    #  -0.05 接头自己的台阶 (本体/护套交界)
Y_STEP  = Y_XSTEP - STEP_MARGIN              #  -0.05 槽的台阶 (= 接头台阶)
Y_CAPI  =  XT_L / 2                          #  11.95 堵头内面
Y_END   = Y_CAPI + CAP_T                     #  14.95 堵头外面
DEPTH   = Y_END - Y_OPEN                     #  26.9
HOLE_Y  = Y_OPEN + HOLE_Y_OPEN               #   0.55 孔心 Y (护套段)
WEB_S     = HX - HOLE_D / 2 - CH_W_S / 2         # 0.95 孔壁到护套段槽壁
WEB_B     = HX - HOLE_D / 2 - CH_W_B / 2         # 1.45 孔壁到本体段槽壁
SHANK_GAP = HX - M6_SHANK_D / 2 - CH_W_S / 2     # 1.20 螺杆到护套侧面
WIRE_X = (-WIRE_PITCH / 2, WIRE_PITCH / 2)

SHIM_W  = CH_W_B - 2 * SHIM_CLR              # 15.4
BACK_RIM_W = CAP_T                           # 3  后边 (出线边) 止口宽 = 堵头厚 (用户)
LEDGE = WIRE_ZC - WIRE_D / 2                  # 3.35 出线圆最低点 (线底); 低于 RIM_H 时后边框在出线处削到这里
SLOT_BOTTOM = min(RIM_H, LEDGE)               # 2  出线孔平底高度 (XT60 = 边框顶 2)
SHIM_Y0 = Y_OPEN + SHIM_OPEN_INSET           # -11.95
SHIM_Y1 = Y_XSTEP - SHIM_BACK_GAP            #  -0.05
SHIM_L  = SHIM_Y1 - SHIM_Y0                  #  11.9

# 横向浮动量 (紧配 = 0)
S_FLOAT = (CH_W_S - SHEATH_W) / 2    # 0
B_FLOAT = (CH_W_B - BODY_W) / 2      # 0

assert WEB_S > 0.5, f"孔已经破进护套段槽里: {WEB_S}"
assert WEB_B > WEB_S, "本体段槽更窄, 肉应该更厚"
assert SHANK_GAP > 0.5, f"螺杆离接头太近: {SHANK_GAP}"
assert HX + HEAD_D / 2 <= HALF_L, "头超出 X 端面"
assert Y_OPEN + HEAD_D / 2 <= HOLE_Y <= Y_END - HEAD_D / 2, "头超出件的前/后端"
assert HOLE_Y > Y_XSTEP, "孔心应落在护套段"
assert WIRE_PITCH / 2 + WIRE_D / 2 <= CH_W_S / 2 - 3.0, "出线口离槽壁太近"
assert WIRE_PITCH > WIRE_D + 3.0, "两个 U 口之间肉太薄"
assert WIRE_ZC + WIRE_D / 2 < CH_H_S
assert STEP_MARGIN >= 0 and Y_OPEN < Y_STEP <= Y_XSTEP, "槽的台阶位置不对 (不能在接头台阶的堵头侧, 否则护套顶低槽顶)"
assert BODY_LIFT + BODY_H < CH_H_S, f"本体顶 {BODY_LIFT+BODY_H} 顶到护套段槽顶 {CH_H_S}"
assert CH_H_B < CH_H_S and CH_W_B < CH_W_S, "本体段槽应该比护套段窄且低"
assert SIDE_CLR_S == 0 and SIDE_CLR_B == 0, "用户要求紧配 (09-16)"
assert PRELOAD_S == 0 and PRELOAD_B == 0, "用户要求槽顶 = 接头顶 9.2 / 8.7 (09-16)"
assert T_TOP >= 1.2, f"槽顶只剩 {T_TOP:.2f}, 太薄 (0.4 喷嘴 3 层线宽)"
assert Y_OPEN <= SHIM_Y0 < SHIM_Y1 <= Y_XSTEP, "凸台 Y 向放不进本体下面"
assert SHIM_W / 2 < HX - HOLE_D / 2, "凸台碰到螺丝孔"
RIM_HOLE_WALL = (HALF_L - RIM_W - ASSY_CLR) - (HX + HOLE_D / 2)     # 1.15 压块台阶内壁到 M6 孔外缘
assert RIM_HOLE_WALL >= 1.0, f"止口台阶离 M6 孔只剩 {RIM_HOLE_WALL}"
assert CH_W_B / 2 < HALF_L - RIM_W, "开口端止口段长度为 0"
RIM_BACK_HOLE_WALL = (Y_CAPI - ASSY_CLR) - (HOLE_Y + HOLE_D / 2)
assert RIM_BACK_HOLE_WALL >= 1.0, f"后边止口台阶离 M6 孔只剩 {RIM_BACK_HOLE_WALL}"

# ===== 建模 =====
body = m3d.Manifold.cube((L, DEPTH, HTOP), False).translate((-HALF_L, Y_OPEN, 0))
# 阶梯槽: 本体段 (从 -Y 开口到槽台阶, 窄且低) + 护套段 (槽台阶到堵头内面, 宽且高)
ch_b = (m3d.Manifold.cube((CH_W_B, (Y_STEP - Y_OPEN) + 1, CH_H_B + 1), False)
        .translate((-CH_W_B / 2, Y_OPEN - 1, -1)))
ch_s = (m3d.Manifold.cube((CH_W_S, Y_CAPI - Y_STEP, CH_H_S + 1), False)
        .translate((-CH_W_S / 2, Y_STEP, -1)))
hole = m3d.Manifold.cylinder(HTOP + 2, HOLE_D / 2, HOLE_D / 2, SEG, False)

def u_slot_cs(xc):
    """(X, Z) 平面里的 U 口: Φ 半圆顶 + 直边开到 Z<0。"""
    r = WIRE_D / 2
    return (m3d.CrossSection.circle(r, SEG).translate((xc, WIRE_ZC))
            + m3d.CrossSection.square((WIRE_D, WIRE_ZC + 1)).translate((xc - r, -1)))

u_cs  = u_slot_cs(WIRE_X[0]) + u_slot_cs(WIRE_X[1])
u_len = CAP_T + 2
# extrude 沿 Z -> rotate((90,0,0)) 把 (x, y, z) 变成 (x, -z, y): 截面 Y 成世界 Z, 挤出沿 -Y
u_cut = u_cs.extrude(u_len).rotate((90, 0, 0)).translate((0, Y_END + 1, 0))

def rim_region(e=0.0, gw=0.0, gh=0.0):
    """止口区域: 左右 X 端条 (Y 全长, 宽 RIM_W) + 开口端条 (槽口处断开, 宽 RIM_W) + 后边条 (X 全宽, 宽 BACK_RIM_W)。
    e>0 向外/向下多延伸 e (切除用); gw 向内加宽, gh 向上加高 (压块台阶 = 边框 + 装配间隙)。"""
    w, h = RIM_W + gw, RIM_H + gh
    r = m3d.Manifold()
    for sx in (-1, 1):
        x_side  = HALF_L - w if sx > 0 else -HALF_L - e
        r = r + m3d.Manifold.cube((w + e, DEPTH + 2 * e, h + e), False).translate((x_side, Y_OPEN - e, -e))
        x_front = CH_W_B / 2 if sx > 0 else -HALF_L - e
        r = r + m3d.Manifold.cube((HALF_L - CH_W_B / 2 + e, w + e, h + e), False).translate((x_front, Y_OPEN - e, -e))
    wb = BACK_RIM_W + gw
    r = r + m3d.Manifold.cube((L + 2 * e, wb + e, h + e), False).translate((-HALF_L - e, Y_END - wb, -e))
    return r

part = body - ch_b - ch_s - u_cut - rim_region(1.0, ASSY_CLR, 0.0)   # 压块底面止口台阶: 宽 +0.1, 高不加 (外观平齐)
for sx in (-1, 1):
    part = part - hole.translate((sx * HX, HOLE_Y, -1))

# 件 2 底板垫片 (装配坐标: 底板 z∈[-BASE_T,0], 凸台 z∈[0,SHIM_T]; 导出时整体上移 BASE_T)
base = m3d.Manifold.cube((L, DEPTH, BASE_T), False).translate((-HALF_L, Y_OPEN, -BASE_T))
pad  = m3d.Manifold.cube((SHIM_W, SHIM_L, SHIM_T), False).translate((-SHIM_W / 2, SHIM_Y0, 0))
rim  = rim_region(0.0)                                      # 底板止口边框 (四边, 开口端槽口断开, 后边 3 宽)
notches = m3d.Manifold()                                    # 出线处削后边框 (线底低于边框顶时)
if LEDGE < RIM_H:
    for xc in WIRE_X:
        notches = notches + (m3d.Manifold.cube((WIRE_D, BACK_RIM_W + 2, RIM_H - LEDGE + 1), False)
                             .translate((xc - WIRE_D / 2, Y_CAPI - 1, LEDGE)))
shim = base + pad + (rim - notches)
for sx in (-1, 1):
    shim = shim - hole.translate((sx * HX, HOLE_Y, -BASE_T - 1))

# ===== 校核 =====
assert len(part.decompose()) == 1, "件不是一整块"
assert len(shim.decompose()) == 1, "垫片不是一整块"

def inter_vol(a, b):
    # 直接求交: 零间隙共面贴合时 a.volume() - (a - b).volume() 会被差集的共面数值问题算错 (v4.10 实测多出 246 mm^3)
    return (a ^ b).volume()

def xt60(dx=0.0, dy=0.0, ecc=0.0):
    """接头 (阶梯实体): 护套坐板上 (堵头侧); 本体底面离板 BODY_LIFT (开口侧), 相对护套在 X 上偏心 ecc。"""
    b = (m3d.Manifold.cube((BODY_W, BODY_L, BODY_H), False)
         .translate((-BODY_W / 2 + dx + ecc, Y_OPEN + dy, BODY_LIFT)))
    s = m3d.Manifold.cube((SHEATH_W, SHEATH_L, SHEATH_H), False).translate((-SHEATH_W / 2 + dx, Y_XSTEP + dy, 0))
    return b + s

hole_poly = SEG / 2 * math.sin(2 * math.pi / SEG) * (HOLE_D / 2) ** 2
_cap_box  = m3d.CrossSection.square((CH_W_S, CH_H_S)).translate((-CH_W_S / 2, 0))
u_area    = (u_cs - (u_cs - _cap_box)).area() / 2             # 单个 U 口在槽截面内的面积
_sh_cs    = m3d.CrossSection.square((SHEATH_W, SHEATH_H)).translate((-SHEATH_W / 2, 0))
u_area_s  = (u_cs - (u_cs - _sh_cs)).area() / 2               # 单口落在护套截面内的那部分

# 1) 接头放进槽顶住堵头: 与压块重叠 = 压紧量 (现为 0), 侧壁/槽顶/堵头/台阶零干涉;
#    紧配: 往任一侧或往上挪 0.05 就吃进槽壁 / 槽顶。
ov_b = BODY_W   * (Y_STEP - Y_OPEN) * PRELOAD_B     # 本体: 只有槽台阶之前那段在低槽顶下
ov_s = SHEATH_W * SHEATH_L          * PRELOAD_S     # 护套: 全长都在高槽顶下
ov_expect = ov_b + ov_s
E = 1e-4
ov = inter_vol(xt60(), part)
assert abs(ov - ov_expect) < 1e-3, f"接头就位: 重叠 {ov:.4f} != {ov_expect:.4f}"
NUDGE = 0.05
side_expect = NUDGE * (CH_H_S * SHEATH_L + (CH_H_B - BODY_LIFT) * (Y_STEP - Y_OPEN))   # 两段侧面贴槽壁的面积 × 挪动量
for sx in (-1, 1):
    side = inter_vol(xt60(dx=sx * NUDGE), part) - ov_expect
    assert side > 0.5 * side_expect, f"紧配没生效: 挪 {NUDGE} 只多吃 {side:.4f}"
up_expect = NUDGE * (SHEATH_W * SHEATH_L + BODY_W * (Y_STEP - Y_OPEN))     # 两段顶面贴槽顶的面积 × 挪动量
up = inter_vol(xt60().translate((0, 0, NUDGE)), part) - ov_expect
assert up > 0.9 * up_expect, f"高度没贴合: 抬 {NUDGE} 只多吃 {up:.4f} (应 {up_expect:.4f})"

# 2) 插入方向 (+Y): 再推 PUSH -> 护套上部 (z ≥ RIM_H) 吃进压块堵头 (扣 U 口);
#    护套下部 (z < RIM_H, 压块此处是后边台阶) 吃进底板后边框 (扣出线缺口)
PUSH = 0.1
extra = inter_vol(xt60(dy=PUSH), part) - ov_expect
_sh_lo = m3d.CrossSection.square((SHEATH_W, RIM_H)).translate((-SHEATH_W / 2, 0))
u_lo_area = (u_cs - (u_cs - _sh_lo)).area()                 # U 口落在护套下部带内的面积 (全部口)
extra_expect = (PUSH * (SHEATH_W * SHEATH_H - 2 * u_area_s - (SHEATH_W * RIM_H - u_lo_area))
                - PUSH * SHEATH_W * PRELOAD_S - PUSH * BODY_W * PRELOAD_B)
assert abs(extra - extra_expect) < 1e-3, f"堵头没挡住: {extra:.4f} vs {extra_expect:.4f}"
_notch_lo = 0.0 if LEDGE >= RIM_H else len(WIRE_X) * WIRE_D * (RIM_H - LEDGE)
push_base = inter_vol(xt60(dy=PUSH), shim)
push_base_expect = PUSH * (SHEATH_W * RIM_H - _notch_lo)
assert abs(push_base - push_base_expect) < 1e-3, f"后边框没挡住护套下部: {push_base:.4f} vs {push_base_expect:.4f}"

# 3) 拔出方向 (-Y) 窄槽台阶挡住护套: 退 STEP_MARGIN 以内重叠不变; 再多退 PULL 护套前端吃进窄低槽
if STEP_MARGIN > 0:
    ov_pull_free = inter_vol(xt60(dy=-(STEP_MARGIN - E)), part)
    assert abs(ov_pull_free - ov_expect) < 1e-2, f"拔出方向 {STEP_MARGIN} 以内就碰了: {ov_pull_free:.4f}"
PULL = 0.1
pull_extra = inter_vol(xt60(dy=-(STEP_MARGIN + PULL)), part) - ov_expect
pull_expect = (PULL * (SHEATH_W * SHEATH_H - CH_W_B * CH_H_B)
               - PULL * SHEATH_W * PRELOAD_S - PULL * BODY_W * PRELOAD_B)
assert abs(pull_extra - pull_expect) < 1e-3, f"台阶没挡住护套: {pull_extra:.4f} vs {pull_expect:.4f}"

# 4) U 型出线口: Φ(线径-0.01) 线沿针轴穿过堵头零干涉, Φ(线径+0.05) 就吃进口壁 (零余量); 口开到底面; 堵头其余实心
wire = m3d.Manifold.cylinder(CAP_T + 4, (WIRE_D - 0.01) / 2, (WIRE_D - 0.01) / 2, SEG, False).rotate((-90, 0, 0))
wire_fat = m3d.Manifold.cylinder(CAP_T + 4, (WIRE_D + 0.05) / 2, (WIRE_D + 0.05) / 2, SEG, False).rotate((-90, 0, 0))
assert abs(WIRE_ZC - SHEATH_H / 2) < 1e-9, "U 口圆心应在针轴线 (护套高/2)"
for xc in WIRE_X:
    assert inter_vol(wire.translate((xc, Y_CAPI - 1, WIRE_ZC)), part) < 1e-9, "线穿不过出线口"
    assert inter_vol(wire_fat.translate((xc, Y_CAPI - 1, WIRE_ZC)), part) > 1e-3, "出线口不是零余量"
    mouth = (m3d.Manifold.cube((WIRE_D - 0.01, CAP_T, WIRE_ZC), False)
             .translate((xc - (WIRE_D - 0.01) / 2, Y_CAPI, 0)))
    assert inter_vol(mouth, part) < 1e-9, "U 口没开到底面"
cap_box = m3d.Manifold.cube((CH_W_S, CAP_T, CH_H_S), False).translate((-CH_W_S / 2, Y_CAPI, 0))
cap_solid = inter_vol(cap_box, part)
_cap_hi = m3d.CrossSection.square((CH_W_S, CH_H_S - RIM_H)).translate((-CH_W_S / 2, RIM_H))
u_hi_area = (u_cs - (u_cs - _cap_hi)).area()                # U 口在堵头 z ≥ RIM_H 部分的面积 (下部 RIM_H 是后边台阶, 空)
cap_solid_expect = CAP_T * (CH_W_S * (CH_H_S - RIM_H) - u_hi_area)
assert abs(cap_solid - cap_solid_expect) < 1e-3, f"堵头实心部分不对 {cap_solid:.3f} vs {cap_solid_expect:.3f}"

# 5) 大扁头坐顶面: 与件零干涉; 头投影除孔外整圈落在顶面上
top = part.slice(HTOP - 1e-3)
head = m3d.Manifold.cylinder(HEAD_T, HEAD_D / 2, HEAD_D / 2, SEG, False)
for sx in (-1, 1):
    assert inter_vol(head.translate((sx * HX, HOLE_Y, HTOP)), part) < 1e-9, "头与件干涉"
    disk = m3d.CrossSection.circle(HEAD_D / 2, SEG).translate((sx * HX, HOLE_Y))
    unsup = (disk - top).area()
    assert abs(unsup - hole_poly) < 0.01 * hole_poly, f"头有悬空: {unsup} vs 孔 {hole_poly}"

# 6) 孔壁与槽壁之间那条肉在设计上是实心的 (探针条 = 两侧各缩 0.02); 护套段 / 本体段各查一次
for sx in (-1, 1):
    for cw, yc, ch in ((CH_W_S, HOLE_Y, CH_H_S), (CH_W_B, (Y_OPEN + Y_STEP) / 2, CH_H_B)):
        w_in, w_out = cw / 2 + 0.02, HX - HOLE_D / 2 - 0.02
        x0 = w_in if sx > 0 else -w_out
        probe = m3d.Manifold.cube((w_out - w_in, 0.1, ch - 0.2), False).translate((x0, yc - 0.05, 0.1))
        assert abs(inter_vol(probe, part) - probe.volume()) < 1e-9, "孔壁与槽壁之间不是实心"

# 7) 螺杆 (Φ6) 与接头零干涉
shank = m3d.Manifold.cylinder(HTOP, M6_SHANK_D / 2, M6_SHANK_D / 2, SEG, False)
for sx in (-1, 1):
    assert inter_vol(shank.translate((sx * HX, HOLE_Y, 0)), xt60()) < 1e-9, "螺杆碰到接头"

# 8) 件 2 底板垫片: 与压块/接头零干涉; 凸台卡进本体段槽 (两侧各 0.1); 外形 = 压块; M6 螺杆定位防掉; 不挡出线
assert inter_vol(shim, part) < 1e-9, "底板垫片碰到压块"
assert inter_vol(shim, xt60()) < 1e-9, "底板垫片与接头干涉 (本体应正好坐凸台, 护套坐底板)"
assert abs(inter_vol(xt60() + shim, part) - ov_expect) < 1e-3, "垫片+接头 一起放, 重叠应该还是压紧量 (0)"
for sx in (-1, 1):
    assert inter_vol(pad.translate((sx * (SHIM_CLR + 0.05), 0, 0)), part) > 1e-6, "凸台 ±X 没卡进本体段槽"
    assert inter_vol(pad.translate((sx * (SHIM_CLR - 0.01), 0, 0)), part) < 1e-9, "凸台装配间隙不足"
assert inter_vol(pad.translate((0, SHIM_BACK_GAP + 0.05, 0)), xt60()) > 1e-6, "凸台后端没贴护套"
assert abs(SHIM_W - (CH_W_B - 2 * ASSY_CLR)) < 1e-9 and abs(SHIM_L - BODY_L) < 1e-9, "凸台应 = 本体段槽宽 − 2×装配间隙 × 本体长"
def _bb(m):
    v = np.asarray(m.to_mesh().vert_properties)[:, :3]
    return v.min(axis=0), v.max(axis=0)
(sb0, sb1), (pb0, pb1) = _bb(shim), _bb(part)
assert np.allclose(sb0[:2], pb0[:2]) and np.allclose(sb1[:2], pb1[:2]), f"底板外形 {sb0[:2]}..{sb1[:2]} != 压块 {pb0[:2]}..{pb1[:2]}"
assert abs(sb0[2] + BASE_T) < 1e-9 and abs(sb1[2] - max(SHIM_T, RIM_H)) < 1e-9, "底板/凸台/边框 Z 范围不对"
# 止口卡住: 底板 ±X / ±Y 在装配间隙内 (0.09) 不碰, 超出 (0.15) 就吃进压块台阶
NEST_IN, NEST_OUT = ASSY_CLR - 0.01, ASSY_CLR + 0.05
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    assert inter_vol(shim.translate((dx * NEST_IN, dy * NEST_IN, 0)), part) < 1e-9, f"装配间隙内就碰了 ({dx},{dy})"
    assert inter_vol(shim.translate((dx * NEST_OUT, dy * NEST_OUT, 0)), part) > 1e-3, f"止口没卡住 ({dx},{dy})"
# 出线孔 = 压块 U 口 + 后边框顶 (出线处削到线底): 线 Φ(线径-0.01) 两件都不碰, Φ(线径+0.05) 吃进压块;
#          线底 ≤ 边框顶时 (削了) 粗线还要吃进底板缺口底
for xc in WIRE_X:
    fat = wire_fat.translate((xc, Y_CAPI - 1, WIRE_ZC))
    assert inter_vol(fat, part) > 1e-3, "粗线没顶到压块 U 口"
    if LEDGE <= RIM_H + 1e-9:
        assert inter_vol(fat, shim) > 1e-4, "粗线没顶到底板缺口底 (线底应贴平底)"
    else:
        assert inter_vol(fat, shim) < 1e-9, "线底高于边框时不应碰底板"
if LEDGE < RIM_H:
    _nb = m3d.Manifold.cube((WIRE_D - 0.02, BACK_RIM_W - 0.02, RIM_H - LEDGE - 0.02), False)
    for xc in WIRE_X:
        assert inter_vol(_nb.translate((xc - WIRE_D / 2 + 0.01, Y_CAPI + 0.01, LEDGE + 0.01)), shim) < 1e-9, "后边框出线缺口没削开"
rod = m3d.Manifold.cylinder(STACK_H + 2, M6_SHANK_D / 2, M6_SHANK_D / 2, SEG, False)
screws = m3d.Manifold()
for sx in (-1, 1):
    r_ = rod.translate((sx * HX, HOLE_Y, -BASE_T - 1))
    assert inter_vol(r_, shim) < 1e-9 and inter_vol(r_, part) < 1e-9, "M6 杆穿不过压块+底板"
    screws = screws + r_
SCREW_PLAY = (HOLE_D - M6_SHANK_D) / 2                    # 0.25
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7071, 0.7071)):
    assert inter_vol(shim.translate((dx * (SCREW_PLAY - 0.01), dy * (SCREW_PLAY - 0.01), 0)), screws) < 1e-9, "螺杆余量内就碰了"
    assert inter_vol(shim.translate((dx * 0.3, dy * 0.3, 0)), screws) > 1e-6, "底板挪 0.3 螺杆没挡住 (会掉)"
for xc in WIRE_X:
    assert inter_vol(wire.translate((xc, Y_CAPI - 1, WIRE_ZC)), shim) < 1e-9, "出线碰到底板垫片"
# 理论体积按 Y 分段 (2D 截面): 前段 [Y_OPEN, 后边条前沿) 左右条 + 开口端两段; 后边条段 全宽截面 (扣缺口 / 扣本来就空的)
def _xc_union(cs_fn):
    u = m3d.CrossSection()
    for xc in WIRE_X:
        u = u + cs_fn().translate((xc, 0))
    return u
_r = WIRE_D / 2
_u2d = (m3d.CrossSection.circle(_r, SEG).translate((0, WIRE_ZC))
        + m3d.CrossSection.square((WIRE_D, WIRE_ZC + 1)).translate((-_r, -1)))
_U_all = _xc_union(lambda: _u2d)
_N_all = (_xc_union(lambda: m3d.CrossSection.square((WIRE_D, RIM_H - LEDGE)).translate((-_r, LEDGE)))
          if LEDGE < RIM_H else m3d.CrossSection())
_full = m3d.CrossSection.square((L, RIM_H)).translate((-HALF_L, 0))
def _front_part(w, y_len):                                   # 左右条 (长 y_len) + 开口端两段 (扣角)
    return (2 * w * y_len + 2 * (HALF_L - CH_W_B / 2 - w) * w) * RIM_H
# 底板边框
rim_vol = _front_part(RIM_W, DEPTH - BACK_RIM_W) + BACK_RIM_W * (_full - _N_all).area()
shim_theory = L * DEPTH * BASE_T + SHIM_W * SHIM_L * SHIM_T - 2 * hole_poly * BASE_T + rim_vol
# 压块台阶: 后边条前沿 Y_CAPI-0.1; [Y_CAPI-0.1, Y_CAPI] 扣掉护套段槽, [Y_CAPI, Y_END] 扣掉 U 口
_WC = RIM_W + ASSY_CLR
_chan = m3d.CrossSection.square((CH_W_S, RIM_H + 1)).translate((-CH_W_S / 2, -0.5))
rebate_vol = (_front_part(_WC, DEPTH - BACK_RIM_W - ASSY_CLR)
              + ASSY_CLR * (_full - _chan).area()
              + BACK_RIM_W * (_full - _U_all).area())
assert abs(shim.volume() - shim_theory) < 1e-3, f"底板垫片体积 {shim.volume():.3f} != 理论 {shim_theory:.3f}"

# 9) 组合外观: 压块 + 底板垫片 外形是 38×26.9×13 长方体, 6 个外表面只有允许的开口 (M6 孔 / 接头口 / 出线口)
assy = part + shim
(ab0, ab1) = _bb(assy)
assert np.allclose(ab0, (-HALF_L, Y_OPEN, -BASE_T)) and np.allclose(ab1, (HALF_L, Y_END, HTOP)), f"组合外形不是长方体 {ab0}..{ab1}"
SKIN = 0.05
def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))
_holes = m3d.Manifold()
for sx in (-1, 1):
    _holes = _holes + m3d.Manifold.cylinder(STACK_H + 4, HOLE_D / 2, HOLE_D / 2, SEG, False).translate((sx * HX, HOLE_Y, -BASE_T - 2))
_wire_ok = m3d.Manifold()
for xc in WIRE_X:
    _wire_ok = _wire_ok + _box(xc - WIRE_D / 2, xc + WIRE_D / 2, Y_END - 1, Y_END + 1, SLOT_BOTTOM - 0.01, WIRE_ZC + WIRE_D / 2 + 0.01)
_faces = {
    "+X 侧面":  (_box(HALF_L - SKIN, HALF_L, Y_OPEN, Y_END, -BASE_T, HTOP), m3d.Manifold()),
    "-X 侧面":  (_box(-HALF_L, -HALF_L + SKIN, Y_OPEN, Y_END, -BASE_T, HTOP), m3d.Manifold()),
    "开口端面": (_box(-HALF_L, HALF_L, Y_OPEN, Y_OPEN + SKIN, -BASE_T, HTOP),
                 _box(-CH_W_B / 2 - 0.01, CH_W_B / 2 + 0.01, Y_OPEN - 1, Y_OPEN + 1, -0.01, CH_H_B + 0.01)),
    "堵头外面": (_box(-HALF_L, HALF_L, Y_END - SKIN, Y_END, -BASE_T, HTOP), _wire_ok),
    "顶面":     (_box(-HALF_L, HALF_L, Y_OPEN, Y_END, HTOP - SKIN, HTOP), _holes),
    "底面":     (_box(-HALF_L, HALF_L, Y_OPEN, Y_END, -BASE_T, -BASE_T + SKIN), _holes),
}
face_void = {}
for name, (slab, allowed) in _faces.items():
    v = ((slab - assy) - allowed).volume()
    face_void[name] = v
    assert v < 1e-6, f"组合外观 {name} 有允许开口以外的缝/坑: {v:.6f} mm^3"

# 10) 板上网格孔落在件底面投影里的 (两孔连线与网格同排)
covered = [(float(gx), float(gy)) for gx in HX + np.arange(-3, 3) * PITCH for gy in HOLE_Y + np.arange(-3, 4) * PITCH
           if -HALF_L < gx < HALF_L and Y_OPEN < gy < Y_END]

# 11) 理论体积
vol_theory = (L * DEPTH * HTOP
              - CH_W_B * (Y_STEP - Y_OPEN) * CH_H_B
              - CH_W_S * (Y_CAPI - Y_STEP) * CH_H_S
              - 2 * hole_poly * HTOP
              - 2 * u_area * CAP_T
              - rebate_vol)

# ===== 导出 STL =====
def write_stl(solid, name, header):
    mesh  = solid.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris  = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name(name)
    with out.open("wb") as f:
        f.write(header.encode("ascii").ljust(80, b" ")[:80])   # STL 头必须 <=80 字节并截断
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1 - v0, v2 - v0)
            nl = float(np.linalg.norm(n))
            if nl > 0:
                n = n / nl
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    expected = 84 + len(tris) * 50
    assert out.stat().st_size == expected, f"STL 大小不对: {out.stat().st_size} != {expected} (STL 头溢出?)"
    print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
    return verts

verts = write_stl(part, "xt60_clamp_16p6x9p2x23p9.stl",
                  f"xt60_clamp {VERSION} 16.6x9.2x23.9 L{L:g} W{DEPTH:g} H{HTOP:g} rim {RIM_W:g}/{BACK_RIM_W:g}x{RIM_H:g}")
shim_verts = write_stl(shim.translate((0, 0, BASE_T)), "xt60_shim_38x26p9x2p5.stl",
                       f"xt60_shim {VERSION} base {L:g}x{DEPTH:g}x{BASE_T:g} pad {SHIM_W:g} rim {RIM_W:g}/{BACK_RIM_W:g}x{RIM_H:g} 2xM6")

vol = part.volume()
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume: {vol:.2f} mm^3  (理论 {vol_theory:.2f}, 差 {abs(vol-vol_theory):.4f})   PLA 实心约 {vol*1.24e-3:.1f} g")
print(f"  平顶 外形 {L:g}×{DEPTH:g}×{HTOP:g} / 顶厚 {T_TOP:g} (本体段处 {HTOP-CH_H_B:g}) / 堵头 {CAP_T:g}")
print(f"  阶梯槽: 本体段(开口侧) {CH_W_B:g}×{CH_H_B:g} 长 {Y_STEP-Y_OPEN:g} (本体 {BODY_W:g}×{BODY_H:g}×{BODY_L:g} 抬高 {BODY_LIFT:g}, 间隙 {SIDE_CLR_B:g}/侧, 过盈 {PRELOAD_B:g})")
print(f"          护套段(堵头侧) {CH_W_S:g}×{CH_H_S:g} 长 {Y_CAPI-Y_STEP:g} (护套 {SHEATH_W:g}×{SHEATH_H:g}×{SHEATH_L:g}, 间隙 {SIDE_CLR_S:g}/侧, 过盈 {PRELOAD_S:g})")
print(f"          槽台阶 Y={Y_STEP:g} 比接头台阶 Y={Y_XSTEP:g} 往开口侧提前 {STEP_MARGIN:g}; 两段均紧配 (间隙 0)")
print(f"  件 2 底板垫片: {L:g}×{DEPTH:g}×{BASE_T:g} + 凸台 {SHIM_W:g}×{SHIM_L:g}×{SHIM_T:g} (Y {SHIM_Y0:g}..{SHIM_Y1:g}), 2×Φ{HOLE_D:g}; "
      f"体积 {shim.volume():.2f} (理论 {shim_theory:.2f}) ≈ {shim.volume()*1.24e-3:.1f} g; 导出 Z {shim_verts[:,2].min():.2f}..{shim_verts[:,2].max():.2f}")
print(f"  2×Φ{HOLE_D:g} @ {PITCH:g}, 孔心 Y={HOLE_Y:g} (距开口面 {HOLE_Y_OPEN:g}, 落在护套段) / "
      f"孔壁到槽壁 护套段 {WEB_S:.2f} 本体段 {WEB_B:.2f} / 螺杆到接头 {SHANK_GAP:.2f} / 头离 X 端面 {HALF_L-HX-HEAD_D/2:.2f}")
print(f"  U 口 2×Φ{WIRE_D:g} @ {WIRE_PITCH:g}, 圆心高 {WIRE_ZC:g}, 单口面积 {u_area:.3f}; 口间肉 {WIRE_PITCH-WIRE_D:g}, 口外侧到护套段槽壁 {CH_W_S/2-WIRE_PITCH/2-WIRE_D/2:g}")
print(f"  接头就位: 重叠 {ov_expect:.2f} (过盈 0); 贴合: 横向挪 {NUDGE:g} 吃进槽壁 {side:.3f} / 往上抬 {NUDGE:g} 吃进槽顶 {up:.3f} (理论 {up_expect:.3f})")
print(f"  插入 +Y: 再推 {PUSH:g} 压块堵头多吃 {extra:.3f} (理论 {extra_expect:.3f}) + 底板后边框吃 {push_base:.3f} (理论 {push_base_expect:.3f}) / 堵头实心 {cap_solid:.2f}")
print(f"  拔出 -Y: 提前量 {STEP_MARGIN:g} (零窜动); 退 {PULL:g} 护套即吃进台阶 {pull_extra:.3f} (理论 {pull_expect:.3f})")
print(f"  底板垫片零干涉 / 凸台卡本体段槽 (两侧各 {ASSY_CLR:g}) / M6 杆穿过零干涉, 底板余量 {SCREW_PLAY:g} 内能晃, 挪 0.3 被螺杆挡住 / 出线不碰底板")
print(f"  止口四边 高 {RIM_H:g}: 左右/开口端 宽 {RIM_W:g} (压块台阶 {RIM_W+ASSY_CLR:g}), 后边 宽 {BACK_RIM_W:g} 全宽 (压块台阶 {BACK_RIM_W+ASSY_CLR:g}); "
      f"线底 {LEDGE:g} {'< 边框顶, 出线处削到线底' if LEDGE < RIM_H else '>= 边框顶, 不削'}; 出线孔平底 {SLOT_BOTTOM:g}; 台阶内壁到 M6 孔 侧 {RIM_HOLE_WALL:.2f} / 后 {RIM_BACK_HOLE_WALL:.2f}")
print(f"  组合外形 {L:g}×{DEPTH:g}×{STACK_H:g} 长方体; 6 面外观 (去掉允许开口后) 缝隙: " + ", ".join(f"{k} {v:.1e}" for k, v in face_void.items()))
print(f"  装配间隙 {ASSY_CLR:g}: 底板 ±X/±Y 挪 {NEST_IN:g} 不碰, 挪 {NEST_OUT:g} 卡住; 凸台宽 {SHIM_W:g} (两侧各 {ASSY_CLR:g})")
print(f"  线 Φ{WIRE_D-0.01:g} 沿针轴 (z={WIRE_ZC:g}) 穿口零干涉, Φ{WIRE_D+0.05:g} 吃进口壁 (零余量), U 口开到底面, 口顶 {WIRE_ZC+WIRE_D/2:g} / 大扁头坐顶面零干涉零悬空 / 孔-槽肉实心 / 螺杆不碰接头")
print(f"  底面投影内的网格孔 (件坐标): {covered}")
print(f"  螺丝按叠层高 {STACK_H:g} (底板 {BASE_T:g} + 压块 {HTOP:g}):")
for Ls in (16, 20, 25, 30):
    eng = Ls - STACK_H
    prot = eng - PLATE_T
    tag = "穿出板底!" if prot > 1e-9 else ("旋入偏少" if eng < 6 else "OK")
    print(f"  M6×{Ls}: 旋入 {eng:.1f}, 距板底 {-prot:.1f}  {tag}")
