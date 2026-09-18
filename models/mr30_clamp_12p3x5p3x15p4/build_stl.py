"""
MR30 电源/电机接头压块 mr30_clamp_12p3x5p3x15p4 (v2 阶梯槽 + 底板垫片嵌套, 2026-09-16)

用户: 把 MR30 接头 (Amass MR30-M + 灰色护套) 锁到底座 (v4 M6 网格板, 节距 25, 板厚 13), 做法照 XT60 压块。

尺寸来源 (用户 09-16 给定):
  用户:「mr30应该是15.4*5.3*12.3 同样有台阶，在前边8.5mm宽度内，长宽分别小0.5mm，也就是单边0.25mm」
  附图 MR30-M 不带护套: 13.40 长 / 12.30 高 / 5.30 厚, 端面跑道形。
      插合本体 (开口侧)   前 8.5 长, 截面 11.8 × 4.8 (比护套单边小 0.25, 同轴, 底面离板 0.25)
      出线护套 (堵头侧)   后 6.9 长, 截面 12.3 × 5.3; 针 / 出线轴线离板 2.65。

用户要求 (09-16 原话):
  - 朝向: 开口端 = 本体 (小), 堵头端 = 护套 (大); 所有接头配合间隙 0 / 过盈 0 (阶梯槽照 XT60 做法)。
  - 出线:「线的直径是2.5mm，不需要余量，从中间出，然后U型口就行」。
  - 垫片:「各自改成和整个件一样的长宽，基础厚度2mm，然后通过m6螺丝孔的位置保证不掉」。
  - 嵌套:「上下两个件加一些嵌套，卡在一起」/「两个件就留0.1mm装配就行」/
          「上下两个件组和后从外边看要是一个立方体，只是有孔而已」/「底板的四个边都加凸台吧」/「高度不足2mm无所谓」/
          「四周都加凸台，高度2mm需要砍高度的位置就砍」/「凸台厚度在出线这里是不是改成3mm和之前出线的那个厚度一致好一点，别的位置是2mm就行」。

现行做法:
  1) 阶梯槽, 接头配合间隙 0 / 过盈 0: 本体段 11.8 × 5.05 长 8.5 / 护套段 12.3 × 5.3 长 6.9; 槽台阶与接头台阶对齐。
     插入 (+Y) 护套顶堵头 (上部压块 + 下部底板后边框); 拔出 (-Y) 护套前端面顶窄槽台阶。
  2) 件 2 垫片 mr30_shim: 底板 38 × 18.4 × 2 (装配坐标 z -2..0) + 凸台 11.6 × 8.5 × 0.25 (托本体) + 2×Φ6.5 与压块孔同轴
     + 止口边框四边 高 2: 左右 / 开口端 宽 2 (开口端在槽口处断开 |X| < 5.9), 后边 (出线边) 宽 3 = 堵头厚、X 全宽;
     后边框在每个出线口 |X - xc| ≤ 1.25 处削到 LEDGE = 线心 2.65 - 线半径 1.25 = 1.4 (平底缺口, 宽 2.5 = U 口宽)。
  3) 压块底面同位置切台阶: 左右 / 开口端 2.1 宽, 后边 3.1 宽 (Y_CAPI - 0.1 .. Y_END), 高 2 ——
     竖直配合面留 0.1 装配间隙, 高度不留 (边框顶贴台阶顶, 外观平齐)。凸台宽 11.8 - 0.2 = 11.6 (两侧让 0.1, 高度不加)。
  4) 出线孔 = 压块 U 口 (半圆顶 R1.25 圆心 2.65 + 直边) + 底板缺口 (平底 1.4): 内切 Φ2.5, 线零余量。
  5) 组合外形 38 × 18.4 × 10.3 长方体, 外表面只有 2×M6 孔、开口端接头口、3 个出线孔。
  ⚠ 后边台阶前沿 (距开口面 15.3) 到 M6 孔后缘 (15.15) 只剩 0.15 (只在压块最下面 2 高内) —— 孔位 / 后边宽都是用户定的,
     按协调要求只打印警告, 等用户定 (相关开放项: 孔心距开口面 11.9 vs 12.5)。

沿用 / 待用户定: 2×Φ6.5 @ 孔距 25 横跨接头, 大扁头坐平顶面; 堵头 3; 件深 18.4; 孔心到开口面 11.9 (待定); 按公头 MR30-M。
建模简化: 本体 / 护套按矩形盒算 (实物端面跑道形)。
坐标: X = 两孔连线, Y = 槽方向 (-Y 开口, +Y 堵头), Z 向上; 压块底面 / 底板顶面 z=0, 底板底面 z=-2。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== 参数 =====
# 接头 (用户 09-16 给定)
SHEATH_W, SHEATH_H = 12.3, 5.3     # 出线护套 (堵头侧)
BODY_STEP = 0.25                   # 本体比护套单边小 (宽、厚各小 0.5, 同轴)
BODY_W    = SHEATH_W - 2 * BODY_STEP   # 11.8 插合本体 (开口侧)
BODY_H    = SHEATH_H - 2 * BODY_STEP   #  4.8
MR_L      = 15.4                   # 总长 (含护套)
BODY_L    = 8.5                    # 本体段长
SHEATH_L  = MR_L - BODY_L          # 6.9 护套段长
BODY_LIFT = (SHEATH_H - BODY_H) / 2    # 0.25 本体底面离板
PIN_ZC    = SHEATH_H / 2           # 2.65 针 / 出线轴线离板
MR_PITCH  = 3.5                    # 针距 (Amass 官方)
N_WIRE    = 3

# 槽 (接头配合: 间隙 0 / 过盈 0)
SIDE_CLR_S = SIDE_CLR_B = 0.0
PRELOAD_S = PRELOAD_B = 0.0
STEP_MARGIN = 0.0

# 件 2 垫片
BASE_T          = 2.0         # 底板厚
BOSS_T          = BODY_LIFT   # 0.25 凸台高 (托本体, 不加间隙)
ASSY_CLR        = 0.1         # 压块 ↔ 垫片 嵌套竖直面装配间隙
BOSS_CLR        = ASSY_CLR    # 凸台 ±X
RIM_W           = 2.0         # 止口宽: 左右 / 开口端
REAR_RIM_W      = 3.0         # 止口宽: 后边 (出线边) = 堵头厚
RIM_H           = 2.0         # 止口高
STEP_GW, STEP_GH = ASSY_CLR, 0.0   # 压块台阶: 宽度加 0.1, 高度不加 (外观平齐)

T_TOP       = 3.0
CAP_T       = 3.0
WIRE_OD     = 2.5
WIRE_CLR    = 0.0
WIRE_D      = WIRE_OD + 2 * WIRE_CLR
WIRE_PITCH  = MR_PITCH
WIRE_ZC     = PIN_ZC
PITCH       = 25.0
HOLE_D      = 6.5
END         = 6.5
HOLE_Y_OPEN = 11.9    # 待用户定

HEAD_D, HEAD_T = 12.5, 2.6
PLATE_T    = 13.0
M6_SHANK_D = 6.0
SEG = 96

# ===== 导出量 =====
CH_W_B = BODY_W + 2 * SIDE_CLR_B             # 11.8
CH_H_B = BODY_LIFT + BODY_H - PRELOAD_B      #  5.05
CH_W_S = SHEATH_W + 2 * SIDE_CLR_S           # 12.3
CH_H_S = SHEATH_H - PRELOAD_S                #  5.3
HTOP   = CH_H_S + T_TOP                      #  8.3
T_TOP_B = HTOP - CH_H_B                      #  3.25
HX     = PITCH / 2
HALF_L = HX + END                            # 19
L      = 2 * HALF_L                          # 38
Y_OPEN  = -MR_L / 2                          # -7.7
Y_XSTEP = Y_OPEN + BODY_L                    #  0.8
Y_STEP  = Y_XSTEP - STEP_MARGIN              #  0.8
Y_CAPI  =  MR_L / 2                          #  7.7
Y_END   = Y_CAPI + CAP_T                     # 10.7
DEPTH   = Y_END - Y_OPEN                     # 18.4
HOLE_Y  = Y_OPEN + HOLE_Y_OPEN               #  4.2
WEB_S     = HX - HOLE_D / 2 - CH_W_S / 2     # 3.10
WEB_B     = HX - HOLE_D / 2 - CH_W_B / 2     # 3.35 本体段侧壁厚 (孔不在本体段, 只作侧壁实心校核, 不是孔壁肉)
SHANK_GAP = HX - M6_SHANK_D / 2 - CH_W_S / 2 # 3.35
WIRE_X = tuple((i - (N_WIRE - 1) / 2) * WIRE_PITCH for i in range(N_WIRE))
PIN_X  = tuple((i - (N_WIRE - 1) / 2) * MR_PITCH for i in range(N_WIRE))
U_TOP  = WIRE_ZC + WIRE_D / 2                # 3.9
U_ROOF = CH_H_S - U_TOP                      # 1.4
U_RIB  = WIRE_PITCH - WIRE_D                 # 1.0
U_SIDE = CH_W_S / 2 - (WIRE_X[-1] + WIRE_D / 2)   # 1.4
LEDGE_H = WIRE_ZC - WIRE_OD / 2              # 1.4 出线圆最低点 = 后边框缺口底
NOTCH   = LEDGE_H < RIM_H                    # 只有线底低于边框顶才削缺口 (XT60 线底 3.35 不削)

BOSS_W  = CH_W_B - 2 * BOSS_CLR              # 11.6
BOSS_Y0 = Y_OPEN                             # -7.7
BOSS_Y1 = Y_XSTEP                            #  0.8
BOSS_L  = BOSS_Y1 - BOSS_Y0                  #  8.5
STACK_H = BASE_T + HTOP                      # 10.3
SCREW_RADIAL = (HOLE_D - M6_SHANK_D) / 2     #  0.25
RIM_SEG_X0   = CH_W_B / 2                    #  5.9 开口端边框在槽口处断开
RIM_X_IN     = HALF_L - RIM_W                # 17   左右边框内缘
RIM_Y1       = Y_OPEN + RIM_W                # -5.7 开口端边框内缘
REAR_RIM_Y0  = Y_END - REAR_RIM_W            #  7.7 后边框前沿 (= 堵头内面, 贴护套后端面)
STEP_X_IN    = HALF_L - (RIM_W + STEP_GW)    # 16.9 压块侧台阶内壁
STEP_Y1      = Y_OPEN + RIM_W + STEP_GW      # -5.6 压块开口端台阶内壁
REAR_STEP_Y0 = Y_END - (REAR_RIM_W + STEP_GW)   # 7.6 压块后台阶前沿 (距开口面 15.3)
STEP_H       = RIM_H + STEP_GH               #  2.0
STEP_HOLE_WEB = STEP_X_IN - (HX + HOLE_D / 2)          # 1.15 侧台阶到 M6 孔
REAR_HOLE_WEB = REAR_STEP_Y0 - (HOLE_Y + HOLE_D / 2)   # 0.15 后台阶到 M6 孔 (⚠)

assert abs(BODY_L + SHEATH_L - MR_L) < 1e-12 and SHEATH_L > 0
assert abs(BODY_LIFT + BODY_H / 2 - PIN_ZC) < 1e-12, "本体与护套应同轴"
assert WEB_S > 0.5 and WEB_B > WEB_S and SHANK_GAP > 0.5
assert HX + HEAD_D / 2 <= HALF_L, "头超出 X 端面"
assert Y_OPEN + HEAD_D / 2 <= HOLE_Y <= Y_END - HEAD_D / 2, "头超出件的前/后端"
assert HOLE_Y - HOLE_D / 2 > Y_XSTEP and HOLE_Y + HOLE_D / 2 < Y_CAPI, "孔应整个落在护套段"
assert Y_OPEN + 12.5 + HEAD_D / 2 > Y_END, "XT60 的 12.5 其实放得下, 该沿用"
assert STEP_MARGIN == 0 and SIDE_CLR_S == 0 and SIDE_CLR_B == 0 and PRELOAD_S == 0 and PRELOAD_B == 0, "用户: 接头配合间隙/过盈 0"
assert CH_H_B < CH_H_S and CH_W_B < CH_W_S
assert T_TOP >= 1.2 and T_TOP_B >= T_TOP
assert abs(WIRE_ZC - PIN_ZC) < 1e-12 and WIRE_CLR == 0 and abs(WIRE_D - WIRE_OD) < 1e-12, "用户: 线从中间出, U 口零余量"
assert all(abs(a - b) < 1e-12 for a, b in zip(WIRE_X, PIN_X)), "U 口没对准三针"
assert U_TOP < CH_H_S and U_ROOF > 0.8 and U_SIDE >= 1.0 and U_RIB >= 0.8
assert abs(ASSY_CLR - 0.1) < 1e-12 and abs(BOSS_CLR - ASSY_CLR) < 1e-12 and STEP_GH == 0, "用户: 嵌套竖直面 0.1, 高度不留缝"
assert RIM_W == 2.0 and RIM_H == 2.0 and REAR_RIM_W == CAP_T, "用户: 侧/前 宽 2, 后 宽 3 (= 堵头厚), 高 2"
assert abs(LEDGE_H - (WIRE_ZC - WIRE_OD / 2)) < 1e-12 and NOTCH, "缺口底 = 线心 - 线径/2"
assert STEP_HOLE_WEB >= 1.0, f"侧台阶到 M6 孔的肉太薄: {STEP_HOLE_WEB}"
assert REAR_HOLE_WEB > 0, "后台阶已经切进 M6 孔"
assert STEP_H < CH_H_B and RIM_Y1 < HOLE_Y - HOLE_D / 2 and STEP_X_IN > CH_W_S / 2 and RIM_X_IN > WIRE_X[-1] + WIRE_D / 2
assert REAR_RIM_Y0 >= Y_CAPI - 1e-12, "后边框不能伸进护套段 (会顶护套)"
REAR_WEB_WARN = (f"⚠ 警告: 后边台阶前沿 Y={REAR_STEP_Y0:g} (距开口面 {REAR_STEP_Y0 - Y_OPEN:g}) 到 M6 孔后缘 Y={HOLE_Y + HOLE_D/2:g} "
                 f"(距开口面 {HOLE_Y_OPEN + HOLE_D/2:g}) 只剩 {REAR_HOLE_WEB:.2f} mm, 只在压块底部 {STEP_H:g} 高内 —— 孔位/后边宽待用户定")

# ===== 2D 截面工具 (X, Z 平面) =====
def rect_cs(x0, z0, x1, z1):
    return m3d.CrossSection.square((x1 - x0, z1 - z0)).translate((x0, z0))

def clip(a, b):                       # a ∩ b (CrossSection 没有 &)
    return a - (a - b)

def u_slot_cs(xc):
    """U 口: Φ 半圆顶 (圆心高 WIRE_ZC) + 直边开到 Z<0。"""
    r = WIRE_D / 2
    return (m3d.CrossSection.circle(r, SEG).translate((xc, WIRE_ZC))
            + m3d.CrossSection.square((WIRE_D, WIRE_ZC + 1)).translate((xc - r, -1)))

u_cs = u_slot_cs(WIRE_X[0])
for xc in WIRE_X[1:]:
    u_cs = u_cs + u_slot_cs(xc)
notch_cs = None                       # 后边框缺口 (线底 LEDGE_H 到边框顶)
for xc in WIRE_X:
    n = rect_cs(xc - WIRE_D / 2, LEDGE_H, xc + WIRE_D / 2, RIM_H)
    notch_cs = n if notch_cs is None else notch_cs + n
circ_cs = None
for xc in WIRE_X:
    c = m3d.CrossSection.circle(WIRE_D / 2, SEG).translate((xc, WIRE_ZC))
    circ_cs = c if circ_cs is None else circ_cs + c
BIG = 100.0
def zup(zb):
    return rect_cs(-BIG, zb, BIG, BIG)
def zdn(zt):
    return rect_cs(-BIG, -BIG, BIG, zt)
rear_rim_cs = rect_cs(-HALF_L, 0, HALF_L, RIM_H) - (notch_cs if NOTCH else rect_cs(0, 0, 0, 0))   # 后边框截面
side_rims_cs = rect_cs(-HALF_L, 0, -RIM_X_IN, RIM_H) + rect_cs(RIM_X_IN, 0, HALF_L, RIM_H)
open_rims_cs = rect_cs(-HALF_L, 0, -RIM_SEG_X0, RIM_H) + rect_cs(RIM_SEG_X0, 0, HALF_L, RIM_H)
boss_cs      = rect_cs(-BOSS_W / 2, 0, BOSS_W / 2, BOSS_T)

def prism_y(cs, y0, y1):
    """CrossSection (X, Z) 沿 Y 从 y0 挤到 y1。"""
    return cs.extrude(y1 - y0).rotate((90, 0, 0)).translate((0, y1, 0))

# ===== 建模 =====
blank = m3d.Manifold.cube((L, DEPTH, HTOP), False).translate((-HALF_L, Y_OPEN, 0))
ch_b = (m3d.Manifold.cube((CH_W_B, (Y_STEP - Y_OPEN) + 1, CH_H_B + 1), False)
        .translate((-CH_W_B / 2, Y_OPEN - 1, -1)))
ch_s = (m3d.Manifold.cube((CH_W_S, Y_CAPI - Y_STEP, CH_H_S + 1), False)
        .translate((-CH_W_S / 2, Y_STEP, -1)))
hole = m3d.Manifold.cylinder(HTOP + 2, HOLE_D / 2, HOLE_D / 2, SEG, False)
u_cut = prism_y(u_cs, Y_CAPI - 1, Y_END + 1)

def rim_boxes(gw, gh, z0):
    """止口区域 (宽度加 gw, 顶面 RIM_H + gh, 底面 z0): 左右全长 + 开口端两段 (槽口处断开) + 后边全宽 (宽 REAR_RIM_W + gw)。"""
    h = RIM_H + gh - z0
    w = RIM_W + gw
    wr = REAR_RIM_W + gw
    out = (m3d.Manifold.cube((wr * 0 + L, wr, h), False).translate((-HALF_L, Y_END - wr, z0)))            # 后边
    for sx in (-1, 1):
        out = out + m3d.Manifold.cube((w, DEPTH, h), False).translate(((HALF_L - w if sx > 0 else -HALF_L), Y_OPEN, z0))   # 左右
        out = out + m3d.Manifold.cube((HALF_L - RIM_SEG_X0, w, h), False).translate(((RIM_SEG_X0 if sx > 0 else -HALF_L), Y_OPEN, z0))  # 开口端
    return out

part = blank - ch_b - ch_s - u_cut - rim_boxes(STEP_GW, STEP_GH, -1.0)
for sx in (-1, 1):
    part = part - hole.translate((sx * HX, HOLE_Y, -1))

shim_base = m3d.Manifold.cube((L, DEPTH, BASE_T), False).translate((-HALF_L, Y_OPEN, -BASE_T))
shim_boss = m3d.Manifold.cube((BOSS_W, BOSS_L, BOSS_T), False).translate((-BOSS_W / 2, BOSS_Y0, 0))
shim_rim  = rim_boxes(0.0, 0.0, 0.0)
if NOTCH:
    for xc in WIRE_X:
        shim_rim = shim_rim - m3d.Manifold.cube((WIRE_D, REAR_RIM_W + 2, RIM_H + 1), False).translate((xc - WIRE_D / 2, REAR_RIM_Y0 - 1, LEDGE_H))
shim = shim_base + shim_boss + shim_rim
for sx in (-1, 1):
    shim = shim - m3d.Manifold.cylinder(BASE_T + 2, HOLE_D / 2, HOLE_D / 2, SEG, False).translate((sx * HX, HOLE_Y, -BASE_T - 1))

# ===== 校核 =====
assert len(part.decompose()) == 1, "件不是一整块"
assert len(shim.decompose()) == 1, "垫片不是一整块"

def inter_vol(a, b):
    return (a ^ b).volume()           # 直接求交 (a - (a - b) 在共面零间隙处会被差集数值问题算错)

def mr30(dx=0.0, dy=0.0):
    b = (m3d.Manifold.cube((BODY_W, BODY_L, BODY_H), False)
         .translate((-BODY_W / 2 + dx, Y_OPEN + dy, BODY_LIFT)))
    s = m3d.Manifold.cube((SHEATH_W, SHEATH_L, SHEATH_H), False).translate((-SHEATH_W / 2 + dx, Y_XSTEP + dy, 0))
    return b + s

hole_poly = SEG / 2 * math.sin(2 * math.pi / SEG) * (HOLE_D / 2) ** 2
_cap_box  = rect_cs(-CH_W_S / 2, 0, CH_W_S / 2, CH_H_S)
u_area    = clip(u_cs, _cap_box).area() / N_WIRE
sheath_cs = rect_cs(-SHEATH_W / 2, 0, SHEATH_W / 2, SHEATH_H)
L_B = Y_STEP - Y_OPEN
L_S = Y_CAPI - Y_STEP
_body_only   = m3d.Manifold.cube((BODY_W, BODY_L, BODY_H), False).translate((-BODY_W / 2, Y_OPEN, BODY_LIFT))
_sheath_only = m3d.Manifold.cube((SHEATH_W, SHEATH_L, SHEATH_H), False).translate((-SHEATH_W / 2, Y_XSTEP, 0))

# 1) 就位重叠 0; 横向挪 0.05 吃进槽壁 / 上抬 0.05 吃进槽顶 = 理论 (两段分别核对)
ov = inter_vol(mr30(), part)
assert ov < 1e-6, f"接头就位: 重叠 {ov:.4f} != 0"
NUDGE = 0.05
side_b_full = NUDGE * L_B * (CH_H_B - BODY_LIFT)
side_b_exp  = side_b_full - NUDGE * (RIM_W + STEP_GW) * (STEP_H - BODY_LIFT)   # 开口端底角被台阶切掉 2.1 × 1.75
side_b_asm  = side_b_exp + NUDGE * RIM_W * (RIM_H - BODY_LIFT)                  # 边框补回 2 × 1.75
side_s_exp  = NUDGE * (SHEATH_L * CH_H_S - STEP_GW * STEP_H)                    # 护套侧面: 后台阶前沿那 0.1 × 2 空了
side_expect = side_b_exp + side_s_exp
for sx in (-1, 1):
    side = inter_vol(mr30(dx=sx * NUDGE), part)
    assert abs(side - side_expect) < 1e-3, f"横向挪 {sx*NUDGE:+g}: {side:.4f} != 理论 {side_expect:.4f}"
up_b_exp = NUDGE * BODY_W * L_B
up_s_exp = NUDGE * SHEATH_W * SHEATH_L
up = inter_vol(mr30().translate((0, 0, NUDGE)), part)
assert abs(up - (up_b_exp + up_s_exp)) < 1e-3, f"上抬: {up:.4f} != {up_b_exp + up_s_exp:.4f}"
assert abs(inter_vol(_body_only.translate((NUDGE, 0, 0)), part) - side_b_exp) < 1e-3, "本体段横向"
assert abs(inter_vol(_sheath_only.translate((NUDGE, 0, 0)), part) - side_s_exp) < 1e-3, "护套段横向"
assert abs(inter_vol(_body_only.translate((0, 0, NUDGE)), part) - up_b_exp) < 1e-3, "本体段槽顶"
assert abs(inter_vol(_sheath_only.translate((0, 0, NUDGE)), part) - up_s_exp) < 1e-3, "护套段槽顶"

# 2) 插入 (+Y): 护套上部顶压块堵头 (z >= RIM_H, 扣 U 口), 下部顶底板后边框 (z < RIM_H, 扣缺口) —— 各自 = 理论
PUSH = 0.1
push_part_exp = PUSH * (clip(sheath_cs, zup(RIM_H)) - u_cs).area()
push_shim_exp = PUSH * (clip(sheath_cs, zdn(RIM_H)) - (notch_cs if NOTCH else rect_cs(0, 0, 0, 0))).area()
push_part = inter_vol(mr30(dy=PUSH), part)
push_shim = inter_vol(mr30(dy=PUSH), shim)
assert abs(push_part - push_part_exp) < 1e-3, f"压块堵头没挡住: {push_part:.4f} vs {push_part_exp:.4f}"
assert abs(push_shim - push_shim_exp) < 1e-3, f"后边框没挡住: {push_shim:.4f} vs {push_shim_exp:.4f}"

# 3) 拔出 (-Y): 护套前端吃进窄低槽台阶
PULL = 0.1
pull_extra = inter_vol(mr30(dy=-PULL), part)
pull_expect = PULL * (SHEATH_W * SHEATH_H - CH_W_B * CH_H_B)
assert abs(pull_extra - pull_expect) < 1e-3, f"台阶没挡住护套: {pull_extra:.4f} vs {pull_expect:.4f}"
SHOULDER_RECT = SHEATH_W * SHEATH_H - CH_W_B * CH_H_B

# 4) 压块 U 口 / 堵头
def wire_probe(d):
    return m3d.Manifold.cylinder(CAP_T + 4, d / 2, d / 2, SEG, False).rotate((-90, 0, 0))
FAT = 0.05
wire_fit, wire_fat = wire_probe(WIRE_OD - 0.01), wire_probe(WIRE_OD + FAT)
fat_cs = m3d.CrossSection.circle((WIRE_OD + FAT) / 2, SEG)
PART_FAT, SHIM_FAT = [], []
for xc in PIN_X:
    wf = wire_fit.translate((xc, Y_CAPI - 1, PIN_ZC))
    wb = wire_fat.translate((xc, Y_CAPI - 1, PIN_ZC))
    assert inter_vol(wf, part) < 1e-9, "Φ2.49 线碰到压块"
    assert inter_vol(wf, shim) < 1e-9, "Φ2.49 线碰到底板"
    fc = fat_cs.translate((xc, PIN_ZC))
    pb, pb_exp = inter_vol(wb, part), (clip(fc, zup(RIM_H)) - u_slot_cs(xc)).area() * CAP_T
    sb, sb_exp = inter_vol(wb, shim), clip(fc, rear_rim_cs).area() * CAP_T
    assert pb > 0.05 and abs(pb - pb_exp) < 0.02 * pb_exp, f"Φ2.55 线应吃进压块: {pb} vs {pb_exp}"
    assert sb > 0.005 and abs(sb - sb_exp) < 0.03 * sb_exp, f"Φ2.55 线应吃进底板缺口底: {sb} vs {sb_exp}"   # 线比平底只低 0.025, 透镜很小
    PART_FAT.append(pb); SHIM_FAT.append(sb)
    mouth = m3d.Manifold.cube((WIRE_D - 0.01, CAP_T, WIRE_ZC), False).translate((xc - (WIRE_D - 0.01) / 2, Y_CAPI, 0))
    assert inter_vol(mouth, part) < 1e-9, "压块 U 口没开到底面"
    # 缺口底 = LEDGE_H: 底下是料, 上面是空
    below = m3d.Manifold.cube((0.2, 0.2, 0.01), False).translate((xc - 0.1, (REAR_RIM_Y0 + Y_END) / 2, LEDGE_H - 0.01))
    above = below.translate((0, 0, 0.01))
    assert abs(inter_vol(below, shim) - below.volume()) < 1e-12 and inter_vol(above, shim) < 1e-12, "缺口底高度不对"
for xa, xb in zip(WIRE_X[:-1], WIRE_X[1:]):
    r_in, r_out = xa + WIRE_D / 2 + 0.02, xb - WIRE_D / 2 - 0.02
    rib = m3d.Manifold.cube((r_out - r_in, CAP_T - 0.04, CH_H_S - RIM_H - 0.06), False).translate((r_in, Y_CAPI + 0.02, RIM_H + 0.02))
    assert abs(inter_vol(rib, part) - rib.volume()) < 1e-9, "U 口之间的肉不是实心"
cap_box = m3d.Manifold.cube((CH_W_S, CAP_T, CH_H_S), False).translate((-CH_W_S / 2, Y_CAPI, 0))
cap_solid = inter_vol(cap_box, part)
cap_solid_exp = CAP_T * (clip(_cap_box, zup(RIM_H)) - u_cs).area()                 # 只算 z >= RIM_H
assert abs(cap_solid - cap_solid_exp) < 1e-3, f"堵头实心部分不对: {cap_solid} vs {cap_solid_exp}"

def stadium(w, h, zc):
    a = w - h
    return (m3d.CrossSection.square((a, h)).translate((-a / 2, zc - h / 2))
            + m3d.CrossSection.circle(h / 2, SEG).translate((-a / 2, zc))
            + m3d.CrossSection.circle(h / 2, SEG).translate((a / 2, zc)))
_st_s = stadium(SHEATH_W, SHEATH_H, PIN_ZC)
hole_cs = clip(u_cs, zup(LEDGE_H))                    # 组合后的出线孔截面
STOP_RECT = (sheath_cs - hole_cs).area()
STOP_STADIUM = (_st_s - hole_cs).area()
_rect_b = rect_cs(-CH_W_B / 2, 0, CH_W_B / 2, CH_H_B)
SHOULDER_STADIUM = (_st_s - _rect_b).area()
assert STOP_STADIUM > 0.3 * _st_s.area() and SHOULDER_STADIUM > 1.0

# 5) 大扁头坐顶面零干涉零悬空
top = part.slice(HTOP - 1e-3)
head = m3d.Manifold.cylinder(HEAD_T, HEAD_D / 2, HEAD_D / 2, SEG, False)
for sx in (-1, 1):
    assert inter_vol(head.translate((sx * HX, HOLE_Y, HTOP)), part) < 1e-9, "头与件干涉"
    disk = m3d.CrossSection.circle(HEAD_D / 2, SEG).translate((sx * HX, HOLE_Y))
    assert abs((disk - top).area() - hole_poly) < 0.01 * hole_poly, "头有悬空"

# 6) 孔壁到槽壁的肉实心 (护套段, 孔所在段) + 本体段侧壁实心
for sx in (-1, 1):
    for cw, yc, ch in ((CH_W_S, HOLE_Y, CH_H_S), (CH_W_B, (Y_OPEN + Y_STEP) / 2, CH_H_B)):
        w_in, w_out = cw / 2 + 0.02, HX - HOLE_D / 2 - 0.02
        x0 = w_in if sx > 0 else -w_out
        probe = m3d.Manifold.cube((w_out - w_in, 0.1, ch - 0.2), False).translate((x0, yc - 0.05, 0.1))
        assert abs(inter_vol(probe, part) - probe.volume()) < 1e-9, "孔壁与槽壁之间不是实心"

# 7) 螺杆不碰接头
shank = m3d.Manifold.cylinder(HTOP, M6_SHANK_D / 2, M6_SHANK_D / 2, SEG, False)
for sx in (-1, 1):
    assert inter_vol(shank.translate((sx * HX, HOLE_Y, 0)), mr30()) < 1e-9, "螺杆碰到接头"

# 8) 件 2 垫片
#  8.1 一整块; XY = 压块外形; Z -BASE_T..RIM_H
_sb, _pb = shim.bounding_box(), part.bounding_box()
assert all(abs(_sb[i] - _pb[i]) < 1e-6 for i in (0, 1, 3, 4)), f"垫片 XY 外形 {_sb} != 压块 {_pb}"
assert abs(_sb[2] + BASE_T) < 1e-6 and abs(_sb[5] - max(BOSS_T, RIM_H)) < 1e-6, f"垫片 Z 范围 {_sb}"
#  8.2 与压块零干涉; 四个方向挪 0.09 不碰, 挪 0.15 吃进 = 理论; 凸台单独 ±X 同样查
assert inter_vol(shim, part) < 1e-9, "垫片碰到压块"
FREE, BITE = ASSY_CLR - 0.01, ASSY_CLR + 0.05
DEEP = BITE - ASSY_CLR
bite_exp = {
    "+X": DEEP * RIM_H * (REAR_STEP_Y0 - STEP_Y1) + DEEP * BOSS_T * (BOSS_L - (RIM_W + STEP_GW)),   # 远侧边框 + 凸台
    "-X": DEEP * RIM_H * (REAR_STEP_Y0 - STEP_Y1) + DEEP * BOSS_T * (BOSS_L - (RIM_W + STEP_GW)),
    "+Y": DEEP * RIM_H * 2 * (STEP_X_IN - RIM_SEG_X0),        # 开口端两段边框顶台阶
    "-Y": DEEP * RIM_H * 2 * (STEP_X_IN - CH_W_S / 2),        # 后边框前侧面顶台阶 (槽口处本来就空)
}
dirs = {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}
SHIM_MOVE = {}
for k, (ux, uy) in dirs.items():
    vf = inter_vol(shim.translate((ux * FREE, uy * FREE, 0)), part)
    vb = inter_vol(shim.translate((ux * BITE, uy * BITE, 0)), part)
    assert vf < 1e-9, f"垫片 {k} 挪 {FREE:g} 就碰压块了: {vf}"
    assert abs(vb - bite_exp[k]) < 1e-3, f"垫片 {k} 挪 {BITE:g}: {vb:.4f} != 理论 {bite_exp[k]:.4f}"
    SHIM_MOVE[k] = vb
boss_x_exp = DEEP * BOSS_T * (BOSS_L - (RIM_W + STEP_GW))
for sx in (-1, 1):
    assert inter_vol(shim_boss.translate((sx * FREE, 0, 0)), part) < 1e-9, "凸台挪 0.09 就碰了"
    assert abs(inter_vol(shim_boss.translate((sx * BITE, 0, 0)), part) - boss_x_exp) < 1e-4, "凸台挪 0.15 吃进量不对"
assert abs(BOSS_W - (CH_W_B - 2 * ASSY_CLR)) < 1e-9 and abs(BOSS_L - BODY_L) < 1e-9 and abs(BOSS_T - BODY_LIFT) < 1e-9
#  8.3 与接头零干涉 / 本体底贴凸台、护套底贴底板 / 边框补回本体段底角
assert inter_vol(shim, mr30()) < 1e-9, "垫片与接头干涉"
assert inter_vol(mr30() + shim, part) < 1e-6, "垫片+接头 一起放, 与压块重叠应 = 0"
assert abs(inter_vol(_body_only.translate((NUDGE, 0, 0)), part + shim) - side_b_asm) < 1e-3, "压块+边框 本体段横向"
down_b_exp = NUDGE * BOSS_W * BOSS_L
down_s_exp = NUDGE * SHEATH_W * SHEATH_L
down = inter_vol(mr30().translate((0, 0, -NUDGE)), shim)
assert abs(down - (down_b_exp + down_s_exp)) < 1e-3, f"接头没贴住垫片: {down} vs {down_b_exp + down_s_exp}"
#  台阶到 M6 孔的肉: 侧面 >= 1.0 (实心); 后面只剩 REAR_HOLE_WEB (警告, 实心也查)
for sx in (-1, 1):
    x_in, x_out = HX + HOLE_D / 2 + 0.02, STEP_X_IN - 0.02
    x0 = x_in if sx > 0 else -x_out
    web = m3d.Manifold.cube((x_out - x_in, 0.1, STEP_H - 0.04), False).translate((x0, HOLE_Y - 0.05, 0.02))
    assert abs(inter_vol(web, part) - web.volume()) < 1e-9, "侧台阶与 M6 孔之间不是实心"
    y_in, y_out = HOLE_Y + HOLE_D / 2 + 0.005, REAR_STEP_Y0 - 0.005
    rweb = m3d.Manifold.cube((0.1, y_out - y_in, STEP_H - 0.04), False).translate((sx * HX - 0.05, y_in, 0.02))
    assert abs(inter_vol(rweb, part) - rweb.volume()) < 1e-9, "后台阶与 M6 孔之间不是实心"
#  8.4 防掉: M6 螺杆穿两件零干涉; 底板任意方向挪 0.3 被挡, 挪 0.24 不碰
shanks = None
for sx in (-1, 1):
    sh = m3d.Manifold.cylinder(STACK_H, M6_SHANK_D / 2, M6_SHANK_D / 2, SEG, False).translate((sx * HX, HOLE_Y, -BASE_T))
    shanks = sh if shanks is None else shanks + sh
assert inter_vol(shanks, part) < 1e-9 and inter_vol(shanks, shim) < 1e-9, "M6 螺杆穿不过"
N_DIR = 16
blocked, freeish = [], []
for k in range(N_DIR):
    a = 2 * math.pi * k / N_DIR
    blocked.append(inter_vol(shim.translate((0.3 * math.cos(a), 0.3 * math.sin(a), 0)), shanks))
    freeish.append(inter_vol(shim.translate((0.24 * math.cos(a), 0.24 * math.sin(a), 0)), shanks))
assert min(blocked) > 1e-6 and max(freeish) < 1e-9
#  8.5 出线孔: 压块 U 口 + 底板缺口平底 = 内切 Φ2.5; Φ2.5 圆柱里两件都没料; 残留空隙 3D = 2D
_zpos = rect_cs(-CH_W_S / 2, 0, CH_W_S / 2, HTOP)
u_prism_cs = clip(u_cs, _zpos)
u_prism = prism_y(u_prism_cs, Y_CAPI, Y_END)
circ = prism_y(circ_cs, Y_CAPI, Y_END)
assert inter_vol(circ, part) < 1e-6 and inter_vol(circ, shim) < 1e-6, "Φ2.5 出线圆里有料"
ROUND_RESIDUAL = (u_prism - part - shim - circ).volume()
ROUND_RESIDUAL_2D = (u_prism_cs - rear_rim_cs - circ_cs).area() * CAP_T
assert abs(ROUND_RESIDUAL - ROUND_RESIDUAL_2D) < 1e-3, f"出线孔残留 3D {ROUND_RESIDUAL} != 2D {ROUND_RESIDUAL_2D}"
#  8.6 组合外观 = 平齐长方体, 外表面只有允许的开口
asm = part + shim
_ab = asm.bounding_box()
assert all(abs(a - b) < 1e-6 for a, b in zip(_ab, (-HALF_L, Y_OPEN, -BASE_T, HALF_L, Y_END, HTOP))), f"组合包围盒 {_ab}"
SK = 0.05
def box(x0, y0, z0, x1, y1, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))
ZB, ZT = -BASE_T, HTOP
holes_all = None
for sx in (-1, 1):
    h_ = m3d.Manifold.cylinder(STACK_H + 2, HOLE_D / 2, HOLE_D / 2, SEG, False).translate((sx * HX, HOLE_Y, ZB - 1))
    holes_all = h_ if holes_all is None else holes_all + h_
wire_ok = None
for xc in WIRE_X:
    b = box(xc - WIRE_D / 2, Y_END - 1, LEDGE_H, xc + WIRE_D / 2, Y_END + 1, U_TOP)
    wire_ok = b if wire_ok is None else wire_ok + b
faces = {
    "+X 侧面":  (box(HALF_L - SK, Y_OPEN, ZB, HALF_L, Y_END, ZT), None),
    "-X 侧面":  (box(-HALF_L, Y_OPEN, ZB, -HALF_L + SK, Y_END, ZT), None),
    "开口端面": (box(-HALF_L, Y_OPEN, ZB, HALF_L, Y_OPEN + SK, ZT), box(-CH_W_B / 2, Y_OPEN - 1, 0.0, CH_W_B / 2, Y_OPEN + 1, CH_H_B)),
    "堵头外面": (box(-HALF_L, Y_END - SK, ZB, HALF_L, Y_END, ZT), wire_ok),
    "顶面":     (box(-HALF_L, Y_OPEN, ZT - SK, HALF_L, Y_END, ZT), holes_all),
    "底面":     (box(-HALF_L, Y_OPEN, ZB, HALF_L, Y_END, ZB + SK), holes_all),
}
FACE_VOID = {}
for name, (sl, allowed) in faces.items():
    void = sl - asm
    raw = void.volume()
    rest = (void - allowed).volume() if allowed is not None else raw
    FACE_VOID[name] = (raw, rest)
    assert rest < 1e-6, f"{name}: 允许开口之外还有空隙 {rest}"
assert FACE_VOID["+X 侧面"][0] < 1e-6 and FACE_VOID["-X 侧面"][0] < 1e-6, "侧面有缝"
assert all(FACE_VOID[n][0] > 0 for n in ("开口端面", "堵头外面", "顶面", "底面"))

# 9) 网格孔
covered = [(round(float(gx), 3), round(float(gy), 3)) for gx in HX + np.arange(-3, 3) * PITCH for gy in HOLE_Y + np.arange(-3, 4) * PITCH
           if -HALF_L < gx < HALF_L and Y_OPEN < gy < Y_END]

# 10) 理论体积 (按 Y 分段, 2D 截面)
full2 = rect_cs(-HALF_L, 0, HALF_L, STEP_H)
seg_part = [   # 压块台阶切掉的料: (截面, 段长)
    ((full2 - rect_cs(-CH_W_B / 2, 0, CH_W_B / 2, STEP_H)).area(), STEP_Y1 - Y_OPEN),                                   # 开口端 (扣本体段槽)
    ((rect_cs(-HALF_L, 0, -STEP_X_IN, STEP_H) + rect_cs(STEP_X_IN, 0, HALF_L, STEP_H)).area(), REAR_STEP_Y0 - STEP_Y1), # 左右
    ((full2 - rect_cs(-CH_W_S / 2, 0, CH_W_S / 2, STEP_H)).area(), Y_CAPI - REAR_STEP_Y0),                              # 后台阶前沿 0.1 (扣护套段槽)
    ((full2 - u_cs).area(), Y_END - Y_CAPI),                                                                             # 堵头段 (扣 U 口)
]
STEP_VOL = sum(a * l for a, l in seg_part)
vol_theory = (L * DEPTH * HTOP - CH_W_B * L_B * CH_H_B - CH_W_S * L_S * CH_H_S
              - 2 * hole_poly * HTOP - N_WIRE * u_area * CAP_T - STEP_VOL)
seg_shim = [   # 底板以上: (截面, 段长)
    ((open_rims_cs + side_rims_cs + boss_cs).area(), RIM_Y1 - Y_OPEN),
    ((side_rims_cs + boss_cs).area(), BOSS_Y1 - RIM_Y1),
    (side_rims_cs.area(), REAR_RIM_Y0 - BOSS_Y1),
    ((rear_rim_cs + side_rims_cs).area(), Y_END - REAR_RIM_Y0),
]
shim_vol_theory = (L * DEPTH - 2 * hole_poly) * BASE_T + sum(a * l for a, l in seg_shim)

# ===== 导出 STL =====
def write_stl(solid, name, header):
    mesh  = solid.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris  = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name(name)
    with out.open("wb") as f:
        f.write(header.encode("ascii").ljust(80, b" ")[:80])
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
    assert out.stat().st_size == expected, f"STL 大小不对: {out.stat().st_size} != {expected}"
    print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
    return verts

verts = write_stl(part, "mr30_clamp_12p3x5p3x15p4.stl",
                  f"mr30_clamp v2 12.3x5.3x15.4 stepped+rim L{L:g} W{DEPTH:g} H{HTOP:g} p{PITCH:g}")
shim_print = shim.translate((0, 0, BASE_T))
shim_verts = write_stl(shim_print, "mr30_shim_38x18p4x2p25.stl",
                       f"mr30_shim base {L:g}x{DEPTH:g}x{BASE_T:g} rim {RIM_W:g}/{REAR_RIM_W:g}x{RIM_H:g}")

vol = part.volume()
shim_vol = shim.volume()
assert abs(vol - vol_theory) < 0.01, f"压块体积: {vol} vs 理论 {vol_theory}"
assert abs(shim_vol - shim_vol_theory) < 0.01, f"垫片体积: {shim_vol} vs 理论 {shim_vol_theory}"
assert np.allclose(verts.min(axis=0), (-HALF_L, Y_OPEN, 0), atol=1e-4) and np.allclose(verts.max(axis=0), (HALF_L, Y_END, HTOP), atol=1e-4)
assert np.allclose(shim_verts.min(axis=0), (-HALF_L, Y_OPEN, 0), atol=1e-4) and np.allclose(shim_verts.max(axis=0), (HALF_L, Y_END, BASE_T + RIM_H), atol=1e-4)

print(f"  压块 bbox X {verts[:,0].min():.3f}..{verts[:,0].max():.3f} / Y {verts[:,1].min():.3f}..{verts[:,1].max():.3f} / Z {verts[:,2].min():.3f}..{verts[:,2].max():.3f}")
print(f"  压块体积 {vol:.2f} mm^3 (理论 {vol_theory:.2f}, 差 {abs(vol-vol_theory):.4f}) PLA 约 {vol*1.24e-3:.1f} g; 台阶切除 {STEP_VOL:.2f} = " +
      " + ".join(f"{a:.2f}×{l:g}" for a, l in seg_part))
print(f"  垫片体积 {shim_vol:.2f} mm^3 (理论 {shim_vol_theory:.2f}, 差 {abs(shim_vol-shim_vol_theory):.4f}) PLA 约 {shim_vol*1.24e-3:.1f} g; 底板以上 = " +
      " + ".join(f"{a:.2f}×{l:g}" for a, l in seg_shim))
print(f"  接头: 本体 {BODY_W:g}×{BODY_H:g}×{BODY_L:g} (离板 {BODY_LIFT:g}) / 护套 {SHEATH_W:g}×{SHEATH_H:g}×{SHEATH_L:g}; 针轴线 {PIN_ZC:g}")
print(f"  外形 {L:g}×{DEPTH:g}×{HTOP:g} / 顶厚 {T_TOP:g} (本体段 {T_TOP_B:g}) / 堵头 {CAP_T:g}; 阶梯槽 {CH_W_B:g}×{CH_H_B:g} 长 {L_B:g} + {CH_W_S:g}×{CH_H_S:g} 长 {L_S:g} (间隙/过盈 0)")
print(f"  就位重叠 {ov:.4f}; 横向挪 {NUDGE:g} 吃槽壁 {side:.4f} (本体段 {side_b_exp:.4f} + 护套段 {side_s_exp:.4f}); 上抬吃槽顶 {up:.4f}")
print(f"  插入 +Y {PUSH:g}: 吃压块堵头 {push_part:.4f} (理论 {push_part_exp:.4f}) + 吃底板后边框 {push_shim:.4f} (理论 {push_shim_exp:.4f}); 堵头实心 (z>={RIM_H:g}) {cap_solid:.2f}")
print(f"  拔出 -Y {PULL:g}: 护套吃台阶 {pull_extra:.4f} (理论 {pull_expect:.4f}); 台肩 矩形 {SHOULDER_RECT:.2f} / 跑道形 {SHOULDER_STADIUM:.2f} mm^2")
print(f"  件 2 垫片: 底板 {L:g}×{DEPTH:g}×{BASE_T:g} + 凸台 {BOSS_W:g}×{BOSS_L:g}×{BOSS_T:g} + 2×Φ{HOLE_D:g} 同轴")
print(f"    止口高 {RIM_H:g}: 左右宽 {RIM_W:g} (|X| {RIM_X_IN:g}..{HALF_L:g}) / 开口端宽 {RIM_W:g} (Y {Y_OPEN:g}..{RIM_Y1:g}, |X| >= {RIM_SEG_X0:g}) / "
      f"后边宽 {REAR_RIM_W:g} (Y {REAR_RIM_Y0:g}..{Y_END:g}, X 全宽); 出线处缺口 宽 {WIRE_D:g} 削到 {LEDGE_H:g} (线心 {WIRE_ZC:g} - 线半径 {WIRE_OD/2:g})")
print(f"    压块台阶 高 {STEP_H:g}: 左右内壁 |X| {STEP_X_IN:g} / 开口端 Y {STEP_Y1:g} / 后边前沿 Y {REAR_STEP_Y0:g} (竖直面留 {STEP_GW:g}, 高度 {STEP_GH:g})")
print(f"    垫片挪 {FREE:g} (±X ±Y) 都不碰; 挪 {BITE:g}: " + " / ".join(f"{k} {SHIM_MOVE[k]:.4f} (理论 {bite_exp[k]:.4f})" for k in dirs))
print(f"    与接头零干涉; 接头下挪 {NUDGE:g} 吃垫片 {down:.4f}; 本体段横向 仅压块 {side_b_exp:.4f} / 压块+边框 {side_b_asm:.4f}")
print(f"    出线孔: Φ2.49 与两件零干涉; Φ2.55 吃压块 {PART_FAT[0]:.4f} + 吃底板缺口底 {SHIM_FAT[0]:.4f} /口; Φ2.5 圆里无料; 残留 3D {ROUND_RESIDUAL:.4f} = 2D {ROUND_RESIDUAL_2D:.4f} mm^3")
print(f"    防掉: 螺杆全高 {STACK_H:g} 穿两件零干涉, 径向 {SCREW_RADIAL:g}; 16 向挪 0.3 全被挡 (最小 {min(blocked):.4f}) / 挪 0.24 全不碰")
print(f"    侧台阶到 M6 孔 {STEP_HOLE_WEB:.2f} (>= 1.0)")
print(f"    {REAR_WEB_WARN}")
print(f"    组合外形 {_ab[3]-_ab[0]:g}×{_ab[4]-_ab[1]:g}×{_ab[5]-_ab[2]:g}; 外表面 {SK:g} 薄片空隙 (总 / 扣允许开口后):")
for name, (raw, rest) in FACE_VOID.items():
    print(f"      {name}: {raw:.4f} / {rest:.2e}")
print(f"  2×Φ{HOLE_D:g} @ {PITCH:g}, 孔心 Y={HOLE_Y:g} (距开口面 {HOLE_Y_OPEN:g}, 孔整个在护套段); 孔壁到槽壁 {WEB_S:.2f} (护套段, 最薄处); 螺杆到护套 {SHANK_GAP:.2f}")
print(f"  U 口 {N_WIRE}×Φ{WIRE_D:g} @ {WIRE_PITCH:g}, 圆心 {WIRE_ZC:g}, 口顶 {U_TOP:g}; 口间肉 {U_RIB:g} / 外侧到槽壁 {U_SIDE:.2f} / 口顶到槽顶 {U_ROOF:.2f}")
print(f"  挡插入面 (组合): 矩形 {STOP_RECT:.2f} / 跑道形 {STOP_STADIUM:.2f} mm^2")
print(f"  底面投影内网格孔: {covered}")
print(f"  螺丝叠层 {STACK_H:g}:")
for Ls in (12, 16, 20, 25):
    eng = Ls - STACK_H
    prot = eng - PLATE_T
    tag = "穿出板底!" if prot > 1e-9 else ("旋入偏少" if eng < 6 else "OK")
    print(f"    M6×{Ls}: 旋入 {eng:.1f}, 距板底 {-prot:.1f}  {tag}")
