"""
A3 landscape 2D engineering drawing for POV3D baseplate_collar
(merged baseplate + ring collar). Three views:
  1) TOP VIEW (1:1) — base square, all holes, boss Φ65/Φ55, collar Φ80,
                       both notches aligned at 75°–105° (dashed)
  2) SECTION A-A (1:1) — cut along +Y axis through notch bisector. Shows
                          combined boss+collar annulus Z=5..15.5, boss alone
                          Z=15.5..25.5, base profile with central Φ12 pocket,
                          and floating right-side pieces at the notch.
     (2026-08-27 降高后: 合并环 Z=5..13, 凸台单独 Z=13..23。)
  3) DETAIL B (3:1) — M3 + Φ7 CB stepped hole.
  4) DETAIL C (2:1) — flange 连接孔 (2026-07-10): 套环壁剖面, Φ3.2 通 (Z0..COLLAR_TOP)
                       + Φ4.2×4 沉孔 (2026-08-28 起只剩底面) (压 M3×4×4.5 铜花螺母;
                       底面沉孔同日晚追加)。降高后中段 Φ3.2 剩 Z4..9。
"""
# ═══════════════════════════════════════════════════════════════════════
# baseplate_collar_v4_h28 —— baseplate_collar_v4 的「原高度」变体
# (2026-09-04, 用户: 「之前的高度是多少, 保存一个独立的」)
#
# 与现行 baseplate_collar_v4 的**唯一**差别 = 高度回到 2026-08-28 降高之前:
#     BOSS_H    20.5 → 23.0   (凸台顶 Z 25.5 → 28)
#     COLLAR_H  10.5 → 13.0   (套环顶 Z 15.5 → 18)
# 其余全部相同 (外形 93.5 方+四角 R62.28、M6 节距 75、走线缺口 75°-105°、
# 底面 8×Φ4.2×4 铜花窝、顶面沉孔仍取消 ...)。两件并存, 改一件要想想另一件。
#
# ★ 不变量仍然成立: mounting_flange 底3 + flange_disc 7 + COLLAR_H + BASE_THICK 5
#   = BASE_THICK + BOSS_H  ⇒  3+7+13+5 = 28 = 5+23 ✓
#   所以 flange_disc_v4 / mounting_flange_v4 **不用重印**, 只是整体上移 2.5。
#
# ⚠ BOM 差异: 定子锁紧 8 颗 M3 的夹持 = 3+7+COLLAR_H+5 = **28** (现行件是 25.5)。
#   ⇒ 本件配 **M3×30 + 2mm 垫圈** (现行件是 M3×30 + 垫圈叠 4.5)。装错会顶起定子。
# ═══════════════════════════════════════════════════════════════════════

import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / baseplate_collar.scad) =====
BASE_THICK = 5.0
# 2026-07-29 v4: 底板改用 200×200×13 网格板 (M6 螺纹孔 距边12.5/节距25)。
# 4 个 M6 脚必须落到网格位 (±37.5,±37.5) → 方形节距 75 (= 3 个网格节距),
# 对角 = 75*sqrt(2) = 106.07 (原 d100 是对角 106.07 / 节距 70.71, 配 25 网格的
# 轴向孔 (±50,0)/(0,±50) 并在装配里转 45°; 新板是偶数孔网格, 无中心孔也无
# ±50 轴向孔, 故改走对角网格位, 装配 ROT 45°→0°)。这是 v4 唯一的几何改动。
M6_DIAG    = 75.0 * math.sqrt(2)                    # 角孔对角间距 (user 2026-06-29)
M6_PATTERN = M6_DIAG / math.sqrt(2)   # = 75
M6_DIAM    = 6.5
# 外形裁切 (2026-08-19, 用户提供 M6 大扁头实测 Φ12.5×2.6): 底盘 100×100 →
# 「93.5 方 + 四角 R62.28 圆弧」。直边 = 37.5+6.25+壁3 = ±46.75; 角弧 = 53.033+6.25+3。
# 与 build_stl.py 的 TRIM_ENABLE/M6_HEAD_D/EDGE_WALL 必须一致 (本图纸参数是复刻不是 import)。
TRIM_ENABLE = True
M6_HEAD_D   = 12.5
EDGE_WALL   = 3.0
BASE_HALF   = M6_PATTERN / 2 + M6_HEAD_D / 2 + EDGE_WALL          # 46.75
BASE_SIDE   = 2 * BASE_HALF if TRIM_ENABLE else 100.0             # 93.5
CORNER_R    = math.hypot(M6_PATTERN / 2, M6_PATTERN / 2) + M6_HEAD_D / 2 + EDGE_WALL  # 62.283
# 2026-07-30: 4×M3 电机孔整组转 45° → 孔落坐标轴 (±12.5,0)/(0,±12.5)
# 与 build_stl.py 的 M3_ROT 必须一致 (本图纸参数是复刻不是 import)
M3_ROT     = 0.0      # 2026-07-30 用户改回 0 (曾试 45° 让孔落坐标轴, 随即撤回)
M3_DIAG    = 25.0
M3_SIDE    = M3_DIAG / math.sqrt(2)
M3_DIAM    = 3.2
CB_DIAM    = 7.0
CB_DEPTH   = 2.0
CENTER_CB_DIAM  = 12.0
CENTER_CB_DEPTH = 1.0
BOSS_OD    = 65.0
BOSS_ID    = 55.0
BOSS_H     = 23.0     # h28 变体: 降高前的 23 (现行件 20.5)
# 2026-07-29 v4 (用户"补成整圈"): 走线缺口取消, 凸台/套环整圈连续。
# 与 build_stl.py 的 NOTCH_ENABLE 必须一致 (本图纸参数是复刻不是 import)。
NOTCH_ENABLE = True
NOTCH_A_S  = 75.0
NOTCH_A_E  = 105.0
NOTCH_H    = 8.0

COLLAR_OD  = 84.0
COLLAR_ID  = 65.0           # = BOSS_OD
COLLAR_H   = 13.0     # h28 变体: 降高前的 13 (现行件 10.5)
COLLAR_Z0  = BASE_THICK     # 5
COLLAR_Z1  = COLLAR_Z0 + COLLAR_H  # 13 (降高后)
COLLAR_NOTCH_H = 8.0

# flange_disc 连接孔 (2026-07-10)
FL_HOLE_R    = 36.25          # PCD 72.5 / 2
FL_ANGS      = [22.5 + 45.0 * k for k in range(8)]
FL_M3_DIAM   = 3.2
FL_CB_DIAM   = 4.2
FL_CB_DEPTH  = 4.0
# 2026-08-28 用户圈了详图 C 上面那个沉孔:「这个沉孔取消」(8 个) ⇒ 顶面沉孔关掉,
# 只留底面那 8 个 (本来 BOM 也只备了底面 8 颗铜花螺母)。与 build_stl.py 的
# FLANGE_CB_TOP_ENABLE / FLANGE_CB_BOT_ENABLE 必须一致 (本图纸参数是复刻不是 import)。
FL_CB_TOP    = False
FL_CB_BOT    = True
_CB_FACES    = "+".join([f for f, on in (("顶面", FL_CB_TOP), ("底面", FL_CB_BOT)) if on]) or "无"
_CB_FACES_S  = "".join([f for f, on in (("顶", FL_CB_TOP), ("底", FL_CB_BOT)) if on]) or "无"

T_BASE = BASE_SIDE / 2      # 50
T_CO   = COLLAR_OD / 2      # 40 (collar outer)
T_BO   = BOSS_OD / 2        # 32.5 (boss outer = collar inner)
T_BI   = BOSS_ID / 2        # 27.5 (boss inner)
T_CCB  = CENTER_CB_DIAM / 2 # 6

# Notch ceiling Z (absolute)
Z_BOSS_NOTCH_CEIL   = BASE_THICK + NOTCH_H          # 13
Z_COLLAR_NOTCH_CEIL = COLLAR_Z0 + COLLAR_NOTCH_H    # 13 = 套环顶 ⇒ 缺口吃满套环全高
Z_BOSS_TOP          = BASE_THICK + BOSS_H           # 23 (降高后)

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

GEOM_W = 0.50
DIM_W  = 0.20
EXT_W  = 0.20
HID_W  = 0.30
ARR_L  = 4.2
ARR_W  = 1.5
EXT_OV = 2.4
EXT_GP = 1.0
TXT_D  = 5.5
TXT_L  = 8.0
TXT_T  = 9.5
TXT_I  = 5.0
DIM_O1 = 14.0
DIM_O2 = 26.0
DIM_O3 = 38.0
DIM_O4 = 50.0

def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W):
    _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
    bx, by = tx - ARR_L*ux, ty - ARR_L*uy
    px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx + ARR_W*px, by + ARR_W*py),
                 (bx - ARR_W*px, by - ARR_W*py)], style="F")
# SimHei 没有这几个字形 (fontTools 查 cmap 实锤, fpdf2 也会 warn): − U+2212 / ⇒ U+21D2 /
# ⚠ U+26A0 / Ø / • —— 直接渲染成空白, 图上「−X」会印成「X」。所有落笔的字符串统一替换。
_GLYPH_FIX = {"−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ"}
def _g(s):
    s = str(s)
    for a, b in _GLYPH_FIX.items():
        if a in s: s = s.replace(a, b)
    return s
def text(x, y, s, size=TXT_D, anchor="start"):
    s = _g(s)
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, angle_deg, size=TXT_D, anchor="middle"):
    s = _g(s)
    pdf.set_font("SimHei", "", size)
    sw = pdf.get_string_width(s)
    with pdf.rotation(angle=angle_deg, x=cx, y=cy):
        if   anchor == "middle": dx = -sw/2
        elif anchor == "end":    dx = -sw
        else: dx = 0
        pdf.text(cx + dx, cy, s)

def _with_unit(label, unit="mm"):
    s = str(label).strip()
    if not s or unit in s or "°" in s: return s
    return f"{s} {unit}"

def hdim(x1, x2, yg, yd, label):
    label = _with_unit(label)
    if yd > yg: ey1, ey2 = yg + EXT_GP, yd + EXT_OV
    else:       ey1, ey2 = yg - EXT_GP, yd - EXT_OV
    line(x1, ey1, x1, ey2, EXT_W)
    line(x2, ey1, x2, ey2, EXT_W)
    x_l, x_r = (x1, x2) if x1 < x2 else (x2, x1)
    gap = x_r - x_l
    if gap >= 2 * ARR_L + 1:
        line(x_l, yd, x_r, yd, DIM_W)
        arrow(x_l, yd, -1, 0); arrow(x_r, yd, 1, 0)
    else:
        ext = ARR_L + 1.0
        line(x_l - ext, yd, x_r + ext, yd, DIM_W)
        arrow(x_l, yd,  1, 0); arrow(x_r, yd, -1, 0)
    text((x_l + x_r) / 2, yd - 1.8, label, anchor="middle")

def vdim(y1, y2, xg, xd, label):
    label = _with_unit(label)
    if xd > xg: ex1, ex2, to = xg+EXT_GP, xd+EXT_OV,  4.0
    else:       ex1, ex2, to = xg-EXT_GP, xd-EXT_OV, -4.0
    line(ex1, y1, ex2, y1, EXT_W)
    line(ex1, y2, ex2, y2, EXT_W)
    y_top, y_bot = (y1, y2) if y1 < y2 else (y2, y1)
    gap = y_bot - y_top
    if gap >= 2 * ARR_L + 1:
        line(xd, y_top, xd, y_bot, DIM_W)
        arrow(xd, y_top, 0, -1); arrow(xd, y_bot, 0, 1)
    else:
        ext = ARR_L + 1.0
        line(xd, y_top - ext, xd, y_bot + ext, DIM_W)
        arrow(xd, y_top, 0,  1); arrow(xd, y_bot, 0, -1)
    label_h_rot = pdf.get_string_width(label)
    if gap >= label_h_rot + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        y_label = y_bot + (ARR_L + 1.0) + label_h_rot / 2 + 1.0
        rot_text(xd + to, y_label, label, angle_deg=90, anchor="middle")

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D 底盘+套环 合并件 v4-h28 原高度版 (凸台顶 Z28 / 套环顶 Z18)  Baseplate + Ring Collar v4-h28",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"{BASE_SIDE:g}×{BASE_SIDE:g}×{BASE_THICK:g} 底盘 (四角 R{CORNER_R:.2f}) / 4×M6 (对角{M6_DIAG:.2f}) / 4×M3+Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 / "
     f"中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔(顶) / "
     f"凸台 Φ{BOSS_OD:g}/Φ{BOSS_ID:g} H{BOSS_H:g} / "
     f"套环 Φ{COLLAR_OD:g}/Φ{COLLAR_ID:g} H{COLLAR_H:g} / "
     + (f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° 对齐 / " if NOTCH_ENABLE else "凸台/套环整圈无缺口 (v4) / ")
     + f"8×Φ{FL_M3_DIAM:g}+Φ{FL_CB_DIAM:g}×{FL_CB_DEPTH:g}沉({_CB_FACES_S}) PCD Φ{2*FL_HOLE_R:g}",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 110, 130
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 32, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A line (along +Y axis through notch bisector at 90°)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.18)
end1 = tv(0, -55); end2 = tv(0, 55)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
text(end2[0] - 5, end2[1] - 4, "A", size=5)
text(end1[0] - 5, end1[1] + 8, "A", size=5)

# Base outline: 93.5 方 + 四角 R62.28 圆弧 (2026-08-19 外形裁切)
_w(GEOM_W)
if TRIM_ENABLE:
    _y_arc = math.sqrt(CORNER_R**2 - BASE_HALF**2)      # 弧与直边交点 ±37.14
    assert _y_arc < BASE_HALF, "角弧半径过小, 会切掉整条直边"
    # 4 条直边 (被四角圆弧截短)
    for _sx in (-1, 1):
        line(*tv(_sx * BASE_HALF, -_y_arc), *tv(_sx * BASE_HALF, _y_arc), GEOM_W)
        line(*tv(-_y_arc, _sx * BASE_HALF), *tv(_y_arc, _sx * BASE_HALF), GEOM_W)
    # 4 段角弧
    _a0 = math.degrees(math.atan2(_y_arc, BASE_HALF))
    _a1 = math.degrees(math.atan2(BASE_HALF, _y_arc))
    for _k in range(4):
        _pts = []
        for _i in range(17):
            _a = math.radians(_k * 90 + _a0 + (_a1 - _a0) * _i / 16)
            _pts.append(tv(CORNER_R * math.cos(_a), CORNER_R * math.sin(_a)))
        for _i in range(len(_pts) - 1):
            line(*_pts[_i], *_pts[_i + 1], GEOM_W)
else:
    bx0, by0 = tv(-BASE_HALF, BASE_HALF)
    pdf.rect(bx0, by0, BASE_SIDE, BASE_SIDE, style="D")

# Center cross
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.13)
pdf.line(tv(-58, 0)[0], tv(-58, 0)[1], tv(58, 0)[0], tv(58, 0)[1])
pdf.line(tv(0, -58)[0], tv(0, -58)[1], tv(0, 58)[0], tv(0, 58)[1])
pdf.set_dash_pattern()

# 4 × M6 holes at ±37.5
_w(GEOM_W)
m6_hp = M6_PATTERN / 2
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = tv(sx * m6_hp, sy * m6_hp)
        pdf.circle(cx, cy, M6_DIAM/2, style="D")
        pdf.set_dash_pattern(dash=1.5, gap=0.7); _w(0.12)
        pdf.line(cx-3, cy, cx+3, cy)
        pdf.line(cx, cy-3, cx, cy+3)
        pdf.set_dash_pattern()
        _w(GEOM_W)

# 4 × M3 holes + Φ7 CB (CB on bottom — dashed)
m3_hp = M3_SIDE / 2
_mr = math.radians(M3_ROT)
M3_HOLES = [((sx*m3_hp)*math.cos(_mr) - (sy*m3_hp)*math.sin(_mr),
             (sx*m3_hp)*math.sin(_mr) + (sy*m3_hp)*math.cos(_mr))
            for sx in (-1, 1) for sy in (-1, 1)]
for (mx, my) in M3_HOLES:
    cx, cy = tv(mx, my)
    pdf.circle(cx, cy, M3_DIAM/2, style="D")
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    pdf.circle(cx, cy, CB_DIAM/2, style="D")
    pdf.set_dash_pattern()
    _w(GEOM_W)

# Collar OD Φ80, boss outer Φ65, boss inner Φ55, central Φ12 CB
ccx, ccy = tv(0, 0)
pdf.circle(ccx, ccy, COLLAR_OD/2, style="D")
pdf.circle(ccx, ccy, BOSS_OD/2,   style="D")
pdf.circle(ccx, ccy, BOSS_ID/2,   style="D")
pdf.circle(ccx, ccy, CENTER_CB_DIAM/2, style="D")

# 8 × flange 连接孔 @ R36.25, 22.5°+45k° (Φ3.2 通 + Φ4.2 沉孔, 均从顶可见)
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.13)
pdf.circle(ccx, ccy, FL_HOLE_R, style="D")           # PCD Φ72.5 点划圆
pdf.set_dash_pattern()
_w(GEOM_W)
for a_deg in FL_ANGS:
    a = math.radians(a_deg)
    hx, hy = tv(FL_HOLE_R * math.cos(a), FL_HOLE_R * math.sin(a))
    pdf.circle(hx, hy, FL_M3_DIAM/2, style="D")
    pdf.circle(hx, hy, FL_CB_DIAM/2, style="D")

if NOTCH_ENABLE:
    # Notches (hidden from top — wall below the visible top face). Show dashed
    # radial lines at the notch boundaries, spanning collar OD to boss ID.
    pdf.set_dash_pattern(dash=2.0, gap=1.0); _w(HID_W)
    for ang_d in (NOTCH_A_S, NOTCH_A_E):
        a = math.radians(ang_d)
        x_in  = ccx + (BOSS_ID/2) * math.cos(a)
        y_in  = ccy - (BOSS_ID/2) * math.sin(a)
        x_out = ccx + (COLLAR_OD/2) * math.cos(a)
        y_out = ccy - (COLLAR_OD/2) * math.sin(a)
        pdf.line(x_in, y_in, x_out, y_out)
    pdf.set_dash_pattern()

    # Notch angle arc + radial dim arrows
    _w(DIM_W)
    ang_r = (COLLAR_OD/2 + BOSS_OD/2) / 2 + 2  # midline of the combined wall
    arc_n = 14
    arc_pts = []
    for i in range(arc_n + 1):
        t = i / arc_n
        a = math.radians(NOTCH_A_S + t * (NOTCH_A_E - NOTCH_A_S))
        arc_pts.append((ccx + ang_r * math.cos(a), ccy - ang_r * math.sin(a)))
    for i in range(len(arc_pts) - 1):
        pdf.line(*arc_pts[i], *arc_pts[i+1])

    for ang_d in (NOTCH_A_S, NOTCH_A_E):
        a = math.radians(ang_d)
        rd_x = ccx + (COLLAR_OD/2 + 8) * math.cos(a)
        rd_y = ccy - (COLLAR_OD/2 + 8) * math.sin(a)
        pdf.line(ccx, ccy, rd_x, rd_y)
        arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
        lx = ccx + (COLLAR_OD/2 + 13) * math.cos(a)
        ly = ccy - (COLLAR_OD/2 + 13) * math.sin(a)
        text(lx, ly, f"{int(ang_d)}°", size=TXT_D, anchor="middle")

# Top-view overall dims
hdim(tv(-BASE_HALF, -BASE_HALF)[0], tv(BASE_HALF, -BASE_HALF)[0],
     tv(0, -BASE_HALF)[1], tv(0, -BASE_HALF)[1] + DIM_O2, f"{BASE_SIDE:g}")
vdim(tv(0, -BASE_HALF)[1], tv(0, BASE_HALF)[1],
     tv(BASE_HALF, 0)[0], tv(BASE_HALF, 0)[0] + DIM_O2, f"{BASE_SIDE:g}")
hdim(tv(-m6_hp, m6_hp)[0], tv(m6_hp, m6_hp)[0],
     tv(0, m6_hp)[1], tv(0, m6_hp)[1] - DIM_O1, f"{M6_PATTERN:.1f}")
vdim(tv(0, m6_hp)[1], tv(0, -m6_hp)[1],
     tv(-m6_hp, 0)[0], tv(-m6_hp, 0)[0] - DIM_O1, f"{M6_PATTERN:.1f}")

# M3 diagonal 25
diag_p1 = tv(*M3_HOLES[0])
diag_p2 = tv(*M3_HOLES[3])
text(diag_p2[0] + 4, diag_p2[1] - 2, f"对角 {M3_DIAG:g} (整组转 {M3_ROT:g}°)", size=TXT_D, anchor="start")
pdf.line(diag_p1[0], diag_p1[1], diag_p2[0], diag_p2[1])
arrow(diag_p1[0], diag_p1[1], -1, 1); arrow(diag_p2[0], diag_p2[1], 1, -1)

# ----- Callouts (right side) -----
_w(EXT_W)
# 角弧 R + 壁厚说明 (2026-08-19 外形裁切)
if TRIM_ENABLE:
    _ca = math.radians(225)
    _cx, _cy = tv(CORNER_R * math.cos(_ca), CORNER_R * math.sin(_ca))
    lx, ly = tv(-58, -46)
    pdf.line(_cx, _cy, lx, ly)
    pdf.line(lx, ly, lx - 8, ly)
    text(lx - 8, ly - 1, f"四角 R{CORNER_R:.2f} mm (4×)", size=TXT_D, anchor="end")
    text(lx - 8, ly + 4,
         f"= M6 帽 Φ{M6_HEAD_D:g} 外缘 + 壁 {EDGE_WALL:g} mm", size=TXT_D, anchor="end")
# M6
hx, hy = tv(m6_hp, m6_hp)
lx, ly = tv(82, 32)
pdf.line(hx + M6_DIAM/2*0.7, hy - M6_DIAM/2*0.7, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1, f"4 × Φ{M6_DIAM:g} (M6 通孔)  节距 {M6_PATTERN:g} (对角 {M6_DIAG:.2f})", size=TXT_D, anchor="start")
# M3 + CB
hx, hy = tv(*M3_HOLES[3])
lx, ly = tv(82, 16)
pdf.line(hx + M3_DIAM/2*0.7, hy - M3_DIAM/2*0.7, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1,
     f"4 × Φ{M3_DIAM:g} 通孔 + Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 (底面)",
     size=TXT_D, anchor="start")
# Central CB
ccb_a = math.radians(-45)
ccb_x = ccx + (CENTER_CB_DIAM/2) * math.cos(ccb_a)
ccb_y = ccy - (CENTER_CB_DIAM/2) * math.sin(ccb_a)
lx, ly = tv(82, 0)
pdf.line(ccb_x, ccb_y, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1,
     f"中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔 (顶面)",
     size=TXT_D, anchor="start")
# flange 连接孔 (leader 自 337.5° 孔, 详图 C)
fl_a = math.radians(337.5)
fl_x = ccx + (FL_HOLE_R + FL_CB_DIAM/2*0.7) * math.cos(fl_a)
fl_y = ccy - (FL_HOLE_R + FL_CB_DIAM/2*0.7) * math.sin(fl_a)
lx, ly = tv(82, -16)
pdf.line(fl_x, fl_y, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1,
     f"8 × Φ{FL_M3_DIAM:g} 通孔 + Φ{FL_CB_DIAM:g}×{FL_CB_DEPTH:g} 沉孔({_CB_FACES})",
     size=TXT_D, anchor="start")
text(lx + 8, ly + 4,
     f"PCD Φ{2*FL_HOLE_R:g}, 22.5°+45k° (对 flange_disc 内圈孔) → 详图 C",
     size=TXT_D, anchor="start")
# Boss callout (upper left)
bx, by = tv(BOSS_OD/2 * math.cos(math.radians(135)),
            BOSS_OD/2 * math.sin(math.radians(135)))
lx, ly = tv(-55, 44)
pdf.line(bx, by, lx, ly)
pdf.line(lx, ly, lx - 8, ly)
text(lx - 8, ly - 1, f"凸台 Φ{BOSS_OD:g}/Φ{BOSS_ID:g}, 高 {BOSS_H:g}",
     size=TXT_D, anchor="end")
# Collar callout (left, below boss)
clx_a = math.radians(165)
clx_x = ccx + (COLLAR_OD/2) * math.cos(clx_a)
clx_y = ccy - (COLLAR_OD/2) * math.sin(clx_a)
lx, ly = tv(-55, 22)
pdf.line(clx_x, clx_y, lx, ly)
pdf.line(lx, ly, lx - 8, ly)
text(lx - 8, ly - 1,
     f"套环 Φ{COLLAR_OD:g}/Φ{COLLAR_ID:g}, 高 {COLLAR_H:g} (Z={COLLAR_Z0:g}–{COLLAR_Z1:g})",
     size=TXT_D, anchor="end")
# Notch callout (upper right)
if NOTCH_ENABLE:
    notch_mid_a = math.radians((NOTCH_A_S + NOTCH_A_E) / 2)
    nx, ny = tv((COLLAR_OD/2 + 4) * math.cos(notch_mid_a),
                (COLLAR_OD/2 + 4) * math.sin(notch_mid_a))
    lx, ly = tv(18, 56)
    pdf.line(nx, ny, lx, ly)
    pdf.line(lx, ly, lx + 10, ly)
    text(lx + 10, ly - 1,
         f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° (对齐): 凸台/套环同高 H{NOTCH_H:g}"
         + ("  ⚠ = 套环全高 ⇒ 套环在此段是 30° 开口" if COLLAR_NOTCH_H >= COLLAR_H - 1e-9 else ""),
         size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
sa_t_zero_x = 310
sa_z_zero_y = 175
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 70, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 78,
     ("(沿 +Y 方向剖切, 过对齐槽口中分线)" if NOTCH_ENABLE else "(沿 +Y 方向剖切; v4 无缺口, 左右对称实墙)"),
     size=TXT_I, anchor="middle")

_w(GEOM_W)

# ----- Base outline -----
# Bottom edge z=0 (full span)
line(*sa(-T_BASE, 0), *sa(T_BASE, 0), GEOM_W)
# Left/right base edges
line(*sa(-T_BASE, 0), *sa(-T_BASE, BASE_THICK), GEOM_W)
line(*sa( T_BASE, 0), *sa( T_BASE, BASE_THICK), GEOM_W)

# Top edge z=BASE_THICK, broken by:
#   - left combined wall (covers -T_CO .. -T_BI) on -t side
#   - central CB pocket (-T_CCB .. +T_CCB, dipping to z = BASE_THICK - CCB_DEPTH)
#   - right side: notch removes both walls, so base top fully visible T_BI..T_BASE
line(*sa(-T_BASE, BASE_THICK), *sa(-T_CO, BASE_THICK), GEOM_W)
# (gap: -T_CO to -T_BI hidden under combined boss+collar wall)
line(*sa(-T_BI,   BASE_THICK), *sa(-T_CCB, BASE_THICK), GEOM_W)
# Central Φ12 CB pocket
line(*sa(-T_CCB, BASE_THICK), *sa(-T_CCB, BASE_THICK - CENTER_CB_DEPTH), GEOM_W)
line(*sa(-T_CCB, BASE_THICK - CENTER_CB_DEPTH),
     *sa( T_CCB, BASE_THICK - CENTER_CB_DEPTH), GEOM_W)
line(*sa( T_CCB, BASE_THICK - CENTER_CB_DEPTH), *sa( T_CCB, BASE_THICK), GEOM_W)
if NOTCH_ENABLE:
    line(*sa( T_CCB, BASE_THICK), *sa( T_BASE, BASE_THICK), GEOM_W)
else:
    # 无缺口: 右侧 T_BI..T_CO 被 凸台+套环 实墙盖住, 与左侧对称
    line(*sa( T_CCB, BASE_THICK), *sa( T_BI,   BASE_THICK), GEOM_W)
    line(*sa( T_CO,  BASE_THICK), *sa( T_BASE, BASE_THICK), GEOM_W)

# ----- Left side combined boss+collar wall (intact, no notch on this side) -----
# Outline: collar outer wall up, collar top, boss outer wall up, boss top,
# boss inner wall down, back to base.
line(*sa(-T_CO, BASE_THICK), *sa(-T_CO, COLLAR_Z1), GEOM_W)   # collar outer wall
line(*sa(-T_CO, COLLAR_Z1), *sa(-T_BO, COLLAR_Z1), GEOM_W)   # collar top
line(*sa(-T_BO, COLLAR_Z1), *sa(-T_BO, Z_BOSS_TOP), GEOM_W)  # boss outer above collar
line(*sa(-T_BO, Z_BOSS_TOP), *sa(-T_BI, Z_BOSS_TOP), GEOM_W) # boss top
line(*sa(-T_BI, Z_BOSS_TOP), *sa(-T_BI, BASE_THICK), GEOM_W) # boss inner wall

# ----- Right side: notch removes walls at low Z, leaves two floating pieces -----
# Above-notch combined right wall outline (closed):
#   (T_BI, Z_BOSS_NOTCH_CEIL) -> (T_BO, Z_BOSS_NOTCH_CEIL)  boss notch ceiling
#   (T_BO, Z_BOSS_NOTCH_CEIL) -> (T_BO, Z_COLLAR_NOTCH_CEIL) drop to collar ceiling
#   (T_BO, Z_COLLAR_NOTCH_CEIL) -> (T_CO, Z_COLLAR_NOTCH_CEIL)  collar notch ceiling
#   (T_CO, Z_COLLAR_NOTCH_CEIL) -> (T_CO, COLLAR_Z1)  collar outer wall
#   (T_CO, COLLAR_Z1) -> (T_BO, COLLAR_Z1)  collar top
#   (T_BO, COLLAR_Z1) -> (T_BO, Z_BOSS_TOP)  boss outer above collar
#   (T_BO, Z_BOSS_TOP) -> (T_BI, Z_BOSS_TOP)  boss top
#   (T_BI, Z_BOSS_TOP) -> (T_BI, Z_BOSS_NOTCH_CEIL)  boss inner wall down
# ⚠ 2026-08-27 降高后 COLLAR_NOTCH_H(8) == COLLAR_H(8) ⇒ 缺口吃满套环全高, 缺口这一侧
#   **套环整段没了**, 上面那段"套环缺口顶 → 套环外壁 → 套环顶"的轮廓会画出一块并不存在
#   的 r32.5..42 台阶。所以按"缺口之上套环还剩不剩肉"分支画。
_COLLAR_ABOVE_NOTCH = COLLAR_Z1 - Z_COLLAR_NOTCH_CEIL > 1e-9
if NOTCH_ENABLE:
    line(*sa(T_BI, Z_BOSS_NOTCH_CEIL),   *sa(T_BO, Z_BOSS_NOTCH_CEIL),   GEOM_W)  # 凸台缺口顶
    if _COLLAR_ABOVE_NOTCH:
        line(*sa(T_BO, Z_BOSS_NOTCH_CEIL),   *sa(T_BO, Z_COLLAR_NOTCH_CEIL), GEOM_W)
        line(*sa(T_BO, Z_COLLAR_NOTCH_CEIL), *sa(T_CO, Z_COLLAR_NOTCH_CEIL), GEOM_W)
        line(*sa(T_CO, Z_COLLAR_NOTCH_CEIL), *sa(T_CO, COLLAR_Z1),           GEOM_W)
        line(*sa(T_CO, COLLAR_Z1),           *sa(T_BO, COLLAR_Z1),           GEOM_W)
        line(*sa(T_BO, COLLAR_Z1),           *sa(T_BO, Z_BOSS_TOP),          GEOM_W)
    else:
        line(*sa(T_BO, Z_BOSS_NOTCH_CEIL),   *sa(T_BO, Z_BOSS_TOP),          GEOM_W)
    line(*sa(T_BO, Z_BOSS_TOP),          *sa(T_BI, Z_BOSS_TOP),          GEOM_W)
    line(*sa(T_BI, Z_BOSS_TOP),          *sa(T_BI, Z_BOSS_NOTCH_CEIL),   GEOM_W)
else:
    # 无缺口: 右半边与左半边完全对称 (实墙)
    line(*sa(T_CO, BASE_THICK), *sa(T_CO, COLLAR_Z1),  GEOM_W)   # 套环外壁
    line(*sa(T_CO, COLLAR_Z1),  *sa(T_BO, COLLAR_Z1),  GEOM_W)   # 套环顶
    line(*sa(T_BO, COLLAR_Z1),  *sa(T_BO, Z_BOSS_TOP), GEOM_W)   # 凸台外壁 (套环之上)
    line(*sa(T_BO, Z_BOSS_TOP), *sa(T_BI, Z_BOSS_TOP), GEOM_W)   # 凸台顶
    line(*sa(T_BI, Z_BOSS_TOP), *sa(T_BI, BASE_THICK), GEOM_W)   # 凸台内壁

# ----- Section A-A dimensions -----
right_dim_x  = sa(T_BASE, 0)[0] + DIM_O1
right_dim_x2 = sa(T_BASE, 0)[0] + DIM_O2
right_dim_x3 = sa(T_BASE, 0)[0] + DIM_O3
# Boss total height (from base top to boss top)
vdim(sa(0, Z_BOSS_TOP)[1], sa(0, BASE_THICK)[1],
     sa(T_BASE, 0)[0], right_dim_x, f"{BOSS_H:g}")
# Collar height (from base top to collar top)
vdim(sa(0, COLLAR_Z1)[1], sa(0, BASE_THICK)[1],
     sa(T_BASE, 0)[0], right_dim_x2, f"{COLLAR_H:g}")
# Base thickness (z=0 to BASE_THICK)
vdim(sa(0, BASE_THICK)[1], sa(0, 0)[1],
     sa(T_BASE, 0)[0], right_dim_x3, f"{BASE_THICK:g}")

# Notch height — 凸台/套环同高 (6→8 统一, 2026-07-13), 一条尺寸即可
if NOTCH_ENABLE:
    boss_nh_x = sa(T_CO + 9, 0)[0]
    vdim(sa(0, Z_BOSS_NOTCH_CEIL)[1], sa(0, BASE_THICK)[1],
         sa(T_CO, 0)[0], boss_nh_x, f"{NOTCH_H:g}")

# Top horizontal diameter dims (stacked above boss top)
top_y_ref = sa(0, Z_BOSS_TOP)[1]
hdim(sa(-T_BI, 0)[0], sa(T_BI, 0)[0], top_y_ref, top_y_ref - DIM_O1, f"Φ{BOSS_ID:g}")
hdim(sa(-T_BO, 0)[0], sa(T_BO, 0)[0], top_y_ref, top_y_ref - DIM_O2, f"Φ{BOSS_OD:g}")
hdim(sa(-T_CO, 0)[0], sa(T_CO, 0)[0], top_y_ref, top_y_ref - DIM_O3, f"Φ{COLLAR_OD:g}")

# Central Φ12 CB inline dim (inside boss cavity at z slightly above base top)
hdim(sa(-T_CCB, 0)[0], sa(T_CCB, 0)[0],
     sa(0, BASE_THICK)[1], sa(0, BASE_THICK + 10)[1],
     f"Φ{CENTER_CB_DIAM:g} mm × 深 {CENTER_CB_DEPTH:g} mm")

# Bottom dim: base side (100)
hdim(sa(-T_BASE, 0)[0], sa(T_BASE, 0)[0],
     sa(0, 0)[1], sa(0, 0)[1] + DIM_O2, f"{BASE_SIDE:g}")

# ===== DETAIL B (3:1) — M3 + Φ7 CB stepped hole =====
DB_SCALE = 3.0
db_cx, db_cy = sa_t_zero_x - 22, 248   # 2026-08-27 左移 22: 降高后详图 C 的总高
                                       # 尺寸 (18→13) 标签正好落到详图 B 的板厚尺寸上
DB_DIM_O = 12.0
def db(t, z): return (db_cx + t * DB_SCALE, db_cy - z * DB_SCALE)

text(db_cx, db_cy - BASE_THICK * DB_SCALE - DB_DIM_O - 6,
     "详图 B  Detail B  (3:1)   尺寸单位: mm", size=TXT_L, anchor="middle")

DB_HALF_BASE  = 10.0
DB_HALF_CB    = CB_DIAM / 2
DB_HALF_M3    = M3_DIAM / 2

_w(GEOM_W)
line(*db(-DB_HALF_BASE, 0), *db(-DB_HALF_CB, 0), GEOM_W)
line(*db( DB_HALF_CB,   0), *db( DB_HALF_BASE, 0), GEOM_W)
line(*db(-DB_HALF_CB, 0), *db(-DB_HALF_CB, CB_DEPTH), GEOM_W)
line(*db( DB_HALF_CB, 0), *db( DB_HALF_CB, CB_DEPTH), GEOM_W)
line(*db(-DB_HALF_CB, CB_DEPTH), *db(-DB_HALF_M3, CB_DEPTH), GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH), *db( DB_HALF_CB, CB_DEPTH), GEOM_W)
line(*db(-DB_HALF_M3, CB_DEPTH), *db(-DB_HALF_M3, BASE_THICK), GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH), *db( DB_HALF_M3, BASE_THICK), GEOM_W)
line(*db(-DB_HALF_BASE, BASE_THICK), *db(-DB_HALF_M3, BASE_THICK), GEOM_W)
line(*db( DB_HALF_M3,   BASE_THICK), *db( DB_HALF_BASE, BASE_THICK), GEOM_W)
line(*db(-DB_HALF_BASE, 0), *db(-DB_HALF_BASE, BASE_THICK), GEOM_W)
line(*db( DB_HALF_BASE, 0), *db( DB_HALF_BASE, BASE_THICK), GEOM_W)

pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(db(0, -2)[0], db(0, -2)[1], db(0, BASE_THICK + 2)[0], db(0, BASE_THICK + 2)[1])
pdf.set_dash_pattern(); _w(GEOM_W)

vdim(db(0, BASE_THICK)[1], db(0, 0)[1],
     db(DB_HALF_BASE, 0)[0], db(DB_HALF_BASE, 0)[0] + DB_DIM_O, f"{BASE_THICK:g}")
vdim(db(0, CB_DEPTH)[1], db(0, 0)[1],
     db(-DB_HALF_BASE, 0)[0], db(-DB_HALF_BASE, 0)[0] - DB_DIM_O, f"{CB_DEPTH:g}")
hdim(db(-DB_HALF_CB, 0)[0], db(DB_HALF_CB, 0)[0],
     db(0, 0)[1], db(0, 0)[1] + DB_DIM_O, f"Φ{CB_DIAM:g}")
hdim(db(-DB_HALF_M3, 0)[0], db(DB_HALF_M3, 0)[0],
     db(0, BASE_THICK)[1], db(0, BASE_THICK)[1] - DB_DIM_O, f"Φ{M3_DIAM:g}")

# ===== DETAIL C (2:1) — flange 连接孔: 套环壁剖面 Φ3.2 通 + Φ4.2×4 顶沉 =====
DC_SCALE = 2.0
dc_cx, dc_cy = 383, 248                    # z=0 基线与详图 B 对齐
DC_DIM_O = 11.0
def dc(t, z): return (dc_cx + t * DC_SCALE, dc_cy - z * DC_SCALE)

text(dc_cx, dc_cy - COLLAR_Z1 * DC_SCALE - 17,
     "详图 C  Detail C  (2:1)", size=TXT_L, anchor="middle")

DC_HALF_WALL = (COLLAR_OD - BOSS_OD) / 4   # 3.75 (壁 32.5..40 → 孔居中 ±3.75)
DC_HALF_BASE = 7.0
DC_HALF_M3   = FL_M3_DIAM / 2
DC_HALF_CB   = FL_CB_DIAM / 2
Z_CB0 = (COLLAR_Z1 - FL_CB_DEPTH) if FL_CB_TOP else COLLAR_Z1   # Φ3.2 中段的上端
Z_CB1 = FL_CB_DEPTH if FL_CB_BOT else 0.0                       # Φ3.2 中段的下端 (底沉孔顶)
DC_HALF_TOP = DC_HALF_CB if FL_CB_TOP else DC_HALF_M3           # 套环顶面开口半径
DC_HALF_BOT = DC_HALF_CB if FL_CB_BOT else DC_HALF_M3

_w(GEOM_W)
# 底板条 (z 0..5, 局部) — 底面开口 = Φ4.2 底沉孔
line(*dc(-DC_HALF_BASE, 0), *dc(-DC_HALF_BOT, 0), GEOM_W)
line(*dc( DC_HALF_BOT,  0), *dc( DC_HALF_BASE, 0), GEOM_W)
line(*dc(-DC_HALF_BASE, 0), *dc(-DC_HALF_BASE, BASE_THICK), GEOM_W)
line(*dc( DC_HALF_BASE, 0), *dc( DC_HALF_BASE, BASE_THICK), GEOM_W)
line(*dc(-DC_HALF_BASE, BASE_THICK), *dc(-DC_HALF_WALL, BASE_THICK), GEOM_W)
line(*dc( DC_HALF_WALL, BASE_THICK), *dc( DC_HALF_BASE, BASE_THICK), GEOM_W)
# 套环壁 (z 5..COLLAR_Z1)
line(*dc(-DC_HALF_WALL, BASE_THICK), *dc(-DC_HALF_WALL, COLLAR_Z1), GEOM_W)
line(*dc( DC_HALF_WALL, BASE_THICK), *dc( DC_HALF_WALL, COLLAR_Z1), GEOM_W)
line(*dc(-DC_HALF_WALL, COLLAR_Z1), *dc(-DC_HALF_TOP, COLLAR_Z1), GEOM_W)
line(*dc( DC_HALF_TOP,  COLLAR_Z1), *dc( DC_HALF_WALL, COLLAR_Z1), GEOM_W)
# 顶面沉孔 Φ4.2 — 2026-08-28 取消, 开关打开才画
if FL_CB_TOP:
    line(*dc(-DC_HALF_CB, COLLAR_Z1), *dc(-DC_HALF_CB, Z_CB0), GEOM_W)
    line(*dc( DC_HALF_CB, COLLAR_Z1), *dc( DC_HALF_CB, Z_CB0), GEOM_W)
    line(*dc(-DC_HALF_CB, Z_CB0), *dc(-DC_HALF_M3, Z_CB0), GEOM_W)
    line(*dc( DC_HALF_M3, Z_CB0), *dc( DC_HALF_CB, Z_CB0), GEOM_W)
# 底面沉孔 Φ4.2 (z 0..4)
if FL_CB_BOT:
    line(*dc(-DC_HALF_CB, 0), *dc(-DC_HALF_CB, Z_CB1), GEOM_W)
    line(*dc( DC_HALF_CB, 0), *dc( DC_HALF_CB, Z_CB1), GEOM_W)
    line(*dc(-DC_HALF_CB, Z_CB1), *dc(-DC_HALF_M3, Z_CB1), GEOM_W)
    line(*dc( DC_HALF_M3, Z_CB1), *dc( DC_HALF_CB, Z_CB1), GEOM_W)
# Φ3.2 通孔壁 (z 4..COLLAR_Z1-4)
line(*dc(-DC_HALF_M3, Z_CB0), *dc(-DC_HALF_M3, Z_CB1), GEOM_W)
line(*dc( DC_HALF_M3, Z_CB0), *dc( DC_HALF_M3, Z_CB1), GEOM_W)
# 孔轴线
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(dc(0, -2)[0], dc(0, -2)[1], dc(0, COLLAR_Z1 + 2)[0], dc(0, COLLAR_Z1 + 2)[1])
pdf.set_dash_pattern(); _w(GEOM_W)
# 尺寸
if FL_CB_TOP:
    vdim(dc(0, COLLAR_Z1)[1], dc(0, Z_CB0)[1],
         dc(DC_HALF_BASE, 0)[0], dc(DC_HALF_BASE, 0)[0] + DC_DIM_O, f"{FL_CB_DEPTH:g}")
if FL_CB_BOT:
    vdim(dc(0, Z_CB1)[1], dc(0, 0)[1],
         dc(DC_HALF_BASE, 0)[0], dc(DC_HALF_BASE, 0)[0] + DC_DIM_O, f"{FL_CB_DEPTH:g}")
vdim(dc(0, COLLAR_Z1)[1], dc(0, 0)[1],
     dc(-DC_HALF_BASE, 0)[0], dc(-DC_HALF_BASE, 0)[0] - DC_DIM_O, f"{COLLAR_Z1:g}")
# Φ 标注: 顶沉孔取消后, 顶端露出来的是 Φ3.2 通孔, Φ4.2 挪到底端标底沉孔
hdim(dc(-DC_HALF_TOP, 0)[0], dc(DC_HALF_TOP, 0)[0],
     dc(0, COLLAR_Z1)[1], dc(0, COLLAR_Z1)[1] - DC_DIM_O,
     f"Φ{FL_CB_DIAM if FL_CB_TOP else FL_M3_DIAM:g}")
hdim(dc(-DC_HALF_BOT, 0)[0], dc(DC_HALF_BOT, 0)[0],
     dc(0, 0)[1], dc(0, 0)[1] + DC_DIM_O,
     f"Φ{FL_CB_DIAM if FL_CB_BOT else FL_M3_DIAM:g}")
text(dc_cx, dc_cy + DC_DIM_O + 8,
     f"{_CB_FACES}压 M3×4×4.5 铜花螺母", size=TXT_D, anchor="middle")
# 2026-08-28: 顶面沉孔取消的来龙去脉 (给对着旧图看的人)
if not FL_CB_TOP:
    _lo = max(a for a in FL_ANGS if a < NOTCH_A_S)          # 67.5
    _hi = min(a for a in FL_ANGS if a > NOTCH_A_E)          # 112.5
    _half = math.degrees(math.asin((FL_M3_DIAM / 2) / FL_HOLE_R))
    _rem = math.radians(NOTCH_A_S - (_lo + _half)) * FL_HOLE_R
    _clamp = 3 + 7 + COLLAR_H + BASE_THICK      # mounting_flange 底 + flange_disc + 套环 + 底盘
    text(30, 252, f"※ 本件 = baseplate_collar_v4 的【原高度变体】: 凸台 H{BOSS_H:g} / 套环 H{COLLAR_H:g} "
         f"(现行件 2026-08-28 已降 2.5 为 H20.5 / H10.5)。除这两个高度外, 两件完全相同 —— 外形、孔位、缺口、沉孔全一致。",
         size=4.5)
    text(30, 257, f"   顶面 Φ{FL_CB_DIAM:g}×{FL_CB_DEPTH:g} 沉孔 ×8 同样取消 (铜花螺母本来就只压底面那 8 个, 顶面窝一直空着); "
         f"该处只有 Φ{FL_M3_DIAM:g} 通孔, 肉厚 {_rem:.2f}。",
         size=4.5)
    text(30, 262, f"   ※ 定子锁紧 8 颗 M3 的夹持 = 3+7+{COLLAR_H:g}+{BASE_THICK:g} = {_clamp:g} "
         f"⇒ 本件配 M3×30 + 2mm 垫圈 (现行件夹持 25.5 / 垫圈叠 4.5)。两件垫圈不通用, 别装错。",
         size=4.5)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 底盘+套环 合并件 v4-h28 原高度版 (Baseplate + Ring Collar)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖) / 3:1 (详图 B) / 2:1 (详图 C)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"{BASE_SIDE:g}×{BASE_SIDE:g}×{BASE_THICK:g} (四角 R{CORNER_R:.2f}) / 4×M6 / 4×M3+Φ7×{CB_DEPTH:g} / 中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g}(顶) / "
     f"凸台 Φ{BOSS_OD:g}/Φ{BOSS_ID:g} H{BOSS_H:g} / 套环 Φ{COLLAR_OD:g}/Φ{COLLAR_ID:g} H{COLLAR_H:g} / "
     + (f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° / " if NOTCH_ENABLE else "整圈无缺口 / ")
     + f"8×Φ{FL_M3_DIAM:g}+Φ{FL_CB_DIAM:g}×{FL_CB_DEPTH:g}沉({_CB_FACES_S})  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-04  /  POV3D / v4 / baseplate_collar_v4_h28 / baseplate_collar_v4_h28.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("baseplate_collar_v4_h28_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
