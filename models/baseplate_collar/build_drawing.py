"""
A3 landscape 2D engineering drawing for POV3D baseplate_collar
(merged baseplate + ring collar). Three views:
  1) TOP VIEW (1:1) — base square, all holes, boss Φ65/Φ55, collar Φ80,
                       both notches aligned at 75°–105° (dashed)
  2) SECTION A-A (1:1) — cut along +Y axis through notch bisector. Shows
                          combined boss+collar annulus Z=5..18, boss alone
                          Z=18..28, base profile with central Φ12 pocket,
                          and floating right-side pieces at the notch.
  3) DETAIL B (3:1) — M3 + Φ7 CB stepped hole.
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / baseplate_collar.scad) =====
BASE_SIDE  = 100.0
BASE_THICK = 5.0
M6_PATTERN = 75.0
M6_DIAM    = 6.5
M3_DIAG    = 25.0
M3_SIDE    = M3_DIAG / math.sqrt(2)
M3_DIAM    = 3.2
CB_DIAM    = 7.0
CB_DEPTH   = 2.0
CENTER_CB_DIAM  = 12.0
CENTER_CB_DEPTH = 1.0
BOSS_OD    = 65.0
BOSS_ID    = 55.0
BOSS_H     = 23.0
NOTCH_A_S  = 75.0
NOTCH_A_E  = 105.0
NOTCH_H    = 8.0

COLLAR_OD  = 80.0
COLLAR_ID  = 65.0           # = BOSS_OD
COLLAR_H   = 13.0
COLLAR_Z0  = BASE_THICK     # 5
COLLAR_Z1  = COLLAR_Z0 + COLLAR_H  # 18
COLLAR_NOTCH_H = 6.0

T_BASE = BASE_SIDE / 2      # 50
T_CO   = COLLAR_OD / 2      # 40 (collar outer)
T_BO   = BOSS_OD / 2        # 32.5 (boss outer = collar inner)
T_BI   = BOSS_ID / 2        # 27.5 (boss inner)
T_CCB  = CENTER_CB_DIAM / 2 # 6

# Notch ceiling Z (absolute)
Z_BOSS_NOTCH_CEIL   = BASE_THICK + NOTCH_H          # 13
Z_COLLAR_NOTCH_CEIL = COLLAR_Z0 + COLLAR_NOTCH_H    # 11
Z_BOSS_TOP          = BASE_THICK + BOSS_H           # 28

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
def text(x, y, s, size=TXT_D, anchor="start"):
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, angle_deg, size=TXT_D, anchor="middle"):
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
text(PAGE_W/2, 14, "POV 3D 底盘+套环 合并件  Baseplate + Ring Collar",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"100×100×{BASE_THICK:g} 底盘 / 4×M6 / 4×M3+Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 / "
     f"中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔(顶) / "
     f"凸台 Φ{BOSS_OD:g}/Φ{BOSS_ID:g} H{BOSS_H:g} / "
     f"套环 Φ{COLLAR_OD:g}/Φ{COLLAR_ID:g} H{COLLAR_H:g} / "
     f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° 对齐",
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

# Base square 100×100
_w(GEOM_W)
bx0, by0 = tv(-50, 50)
pdf.rect(bx0, by0, 100, 100, style="D")

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
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = tv(sx * m3_hp, sy * m3_hp)
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
hdim(tv(-50, -50)[0], tv(50, -50)[0], tv(0, -50)[1], tv(0, -50)[1] + DIM_O2, "100")
vdim(tv(0, -50)[1], tv(0, 50)[1], tv(50, 0)[0], tv(50, 0)[0] + DIM_O2, "100")
hdim(tv(-m6_hp, m6_hp)[0], tv(m6_hp, m6_hp)[0],
     tv(0, m6_hp)[1], tv(0, m6_hp)[1] - DIM_O1, "75")
vdim(tv(0, m6_hp)[1], tv(0, -m6_hp)[1],
     tv(-m6_hp, 0)[0], tv(-m6_hp, 0)[0] - DIM_O1, "75")

# M3 diagonal 25
diag_p1 = tv(-m3_hp, -m3_hp)
diag_p2 = tv(m3_hp, m3_hp)
text(diag_p2[0] + 4, diag_p2[1] - 2, "对角 25", size=TXT_D, anchor="start")
pdf.line(diag_p1[0], diag_p1[1], diag_p2[0], diag_p2[1])
arrow(diag_p1[0], diag_p1[1], -1, 1); arrow(diag_p2[0], diag_p2[1], 1, -1)

# ----- Callouts (right side) -----
_w(EXT_W)
# M6
hx, hy = tv(m6_hp, m6_hp)
lx, ly = tv(82, 32)
pdf.line(hx + M6_DIAM/2*0.7, hy - M6_DIAM/2*0.7, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1, f"4 × Φ{M6_DIAM:g} (M6 通孔)", size=TXT_D, anchor="start")
# M3 + CB
hx, hy = tv(m3_hp, m3_hp)
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
notch_mid_a = math.radians((NOTCH_A_S + NOTCH_A_E) / 2)
nx, ny = tv((COLLAR_OD/2 + 4) * math.cos(notch_mid_a),
            (COLLAR_OD/2 + 4) * math.sin(notch_mid_a))
lx, ly = tv(18, 56)
pdf.line(nx, ny, lx, ly)
pdf.line(lx, ly, lx + 10, ly)
text(lx + 10, ly - 1,
     f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° (对齐): 凸台 H{NOTCH_H:g} / 套环 H{COLLAR_NOTCH_H:g}",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
sa_t_zero_x = 310
sa_z_zero_y = 175
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 70, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 78,
     "(沿 +Y 方向剖切, 过对齐槽口中分线 / cut along +Y axis through aligned notch bisector)",
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
line(*sa( T_CCB, BASE_THICK), *sa( T_BASE, BASE_THICK), GEOM_W)

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
line(*sa(T_BI, Z_BOSS_NOTCH_CEIL),   *sa(T_BO, Z_BOSS_NOTCH_CEIL),   GEOM_W)
line(*sa(T_BO, Z_BOSS_NOTCH_CEIL),   *sa(T_BO, Z_COLLAR_NOTCH_CEIL), GEOM_W)
line(*sa(T_BO, Z_COLLAR_NOTCH_CEIL), *sa(T_CO, Z_COLLAR_NOTCH_CEIL), GEOM_W)
line(*sa(T_CO, Z_COLLAR_NOTCH_CEIL), *sa(T_CO, COLLAR_Z1),           GEOM_W)
line(*sa(T_CO, COLLAR_Z1),           *sa(T_BO, COLLAR_Z1),           GEOM_W)
line(*sa(T_BO, COLLAR_Z1),           *sa(T_BO, Z_BOSS_TOP),          GEOM_W)
line(*sa(T_BO, Z_BOSS_TOP),          *sa(T_BI, Z_BOSS_TOP),          GEOM_W)
line(*sa(T_BI, Z_BOSS_TOP),          *sa(T_BI, Z_BOSS_NOTCH_CEIL),   GEOM_W)

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

# Notch heights — on the right side near T_CO, in the open notch area
# Boss notch height (8) — between Z=BASE_THICK and Z=Z_BOSS_NOTCH_CEIL,
# placed outside the collar (x > T_CO)
boss_nh_x = sa(T_CO + 9, 0)[0]
vdim(sa(0, Z_BOSS_NOTCH_CEIL)[1], sa(0, BASE_THICK)[1],
     sa(T_CO, 0)[0], boss_nh_x, f"{NOTCH_H:g}")
# Collar notch height (6) — placed further out (x > boss_nh_x)
coll_nh_x = sa(T_CO + 17, 0)[0]
vdim(sa(0, Z_COLLAR_NOTCH_CEIL)[1], sa(0, BASE_THICK)[1],
     sa(T_CO, 0)[0], coll_nh_x, f"{COLLAR_NOTCH_H:g}")

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
db_cx, db_cy = sa_t_zero_x, 248
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

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 底盘+套环 合并件 (Baseplate + Ring Collar)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖) / 3:1 (详图 B)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"100×100×{BASE_THICK:g} / 4×M6 / 4×M3+Φ7×{CB_DEPTH:g} / 中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g}(顶) / "
     f"凸台 Φ{BOSS_OD:g}/Φ{BOSS_ID:g} H{BOSS_H:g} / 套环 Φ{COLLAR_OD:g}/Φ{COLLAR_ID:g} H{COLLAR_H:g} / "
     f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° 对齐  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-08  /  POV3D / models / baseplate_collar / baseplate_collar.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("baseplate_collar_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
