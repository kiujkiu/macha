"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D baseplate.

Two views:
  1) TOP VIEW (俯视图, 1:1) — shows base outline, all holes, boss diameters,
                              notch angular position
  2) SECTION A-A (剖视图 A-A, 1:1) — diagonal cut at 45° through center,
                                     showing base thickness, boss height,
                                     counterbore depth, notch height
"""

import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
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

# Section A-A: cut along the +Y axis (passes through notch bisector at 90°).
# t in section coords corresponds to real Y; no holes intersect this plane.
T_BASE = BASE_SIDE / 2    # 50 — half-width along Y
T_BO   = BOSS_OD / 2      # 32.5
T_BI   = BOSS_ID / 2      # 27.5
T_CCB  = CENTER_CB_DIAM / 2  # 6 — half-width of central counterbore

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
TXT_D  = 5.5     # was 4.5 — readability bump #2
TXT_L  = 8.0     # was 6.5
TXT_T  = 9.5     # was 8.0
TXT_I  = 5.0     # was 4.0
DIM_O1 = 14.0
DIM_O2 = 26.0
DIM_O3 = 38.0

def _w(v): pdf.set_line_width(v)

def line(x1, y1, x2, y2, w=DIM_W):
    _w(w); pdf.line(x1, y1, x2, y2)

def dline(x1, y1, x2, y2, w=HID_W, dash=2.0, gap=1.2):
    pdf.set_dash_pattern(dash=dash, gap=gap); _w(w)
    pdf.line(x1, y1, x2, y2)
    pdf.set_dash_pattern()

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
    if not s or unit in s or "°" in s:
        return s
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
    """Vertical dim. Auto-switches to outside-arrows when narrow."""
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
        arrow(xd, y_top, 0,  1)
        arrow(xd, y_bot, 0, -1)
    label_h_rot = pdf.get_string_width(label)
    if gap >= label_h_rot + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        y_label = y_bot + (ARR_L + 1.0) + label_h_rot / 2 + 1.0
        rot_text(xd + to, y_label, label, angle_deg=90, anchor="middle")

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D 底盘  Baseplate", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"100×100×{BASE_THICK:g} / 4×M6 角孔 / 4×M3 中心孔 + Φ{CB_DIAM:g} 沉孔 / 中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔(顶) / 凸台 Φ65/55 H23 / 槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° H{NOTCH_H:g}",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 110, 130
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 32, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A line (long-dashed, with A markers)
# Cut is along the +Y axis (passes through notch bisector at 90°).
pdf.set_dash_pattern(dash=6, gap=2)
_w(0.18)
end1 = tv(0, -55); end2 = tv(0, 55)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
text(end2[0] - 5, end2[1] - 4, "A", size=5)   # top marker
text(end1[0] - 5, end1[1] + 8, "A", size=5)   # bottom marker

# Base square 100×100
_w(GEOM_W)
bx0, by0 = tv(-50, 50)   # top-left in PDF coords
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
        # small crosshair
        pdf.set_dash_pattern(dash=1.5, gap=0.7); _w(0.12)
        pdf.line(cx-3, cy, cx+3, cy)
        pdf.line(cx, cy-3, cx, cy+3)
        pdf.set_dash_pattern()
        _w(GEOM_W)

# 4 × M3 holes at center pattern + Φ7 CB (CB shown as dashed circle, hidden since from bottom)
m3_hp = M3_SIDE / 2
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = tv(sx * m3_hp, sy * m3_hp)
        # M3 hole (solid)
        pdf.circle(cx, cy, M3_DIAM/2, style="D")
        # CB (dashed: feature is on bottom face, hidden from this top view)
        pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
        pdf.circle(cx, cy, CB_DIAM/2, style="D")
        pdf.set_dash_pattern()
        _w(GEOM_W)

# Boss outer (Φ65) and inner (Φ55) circles
ccx, ccy = tv(0, 0)
pdf.circle(ccx, ccy, BOSS_OD/2, style="D")
pdf.circle(ccx, ccy, BOSS_ID/2, style="D")

# Central Φ12 counterbore — visible from top (recessed into base top face,
# inside the boss cavity). Solid circle.
pdf.circle(ccx, ccy, CENTER_CB_DIAM/2, style="D")

# Notch (hidden from above — boss top covers it). Show as dashed radial lines.
pdf.set_dash_pattern(dash=2.0, gap=1.0); _w(HID_W)
for ang_d in (NOTCH_A_S, NOTCH_A_E):
    a = math.radians(ang_d)
    x_in  = ccx + (BOSS_ID/2) * math.cos(a)
    y_in  = ccy - (BOSS_ID/2) * math.sin(a)
    x_out = ccx + (BOSS_OD/2) * math.cos(a)
    y_out = ccy - (BOSS_OD/2) * math.sin(a)
    pdf.line(x_in, y_in, x_out, y_out)
pdf.set_dash_pattern()

# Notch angle arc + label
_w(DIM_W)
ang_r = (BOSS_OD/2 + BOSS_ID/2) / 2   # midline of wall
arc_n = 12
arc_pts = []
for i in range(arc_n + 1):
    t = i / arc_n
    a = math.radians(NOTCH_A_S + t * (NOTCH_A_E - NOTCH_A_S))
    arc_pts.append((ccx + ang_r * math.cos(a), ccy - ang_r * math.sin(a)))
for i in range(len(arc_pts) - 1):
    pdf.line(*arc_pts[i], *arc_pts[i+1])

# Radial dim arrows for 35° and 55°
# Outside the boss, radial dimension lines from center
for ang_d in (NOTCH_A_S, NOTCH_A_E):
    a = math.radians(ang_d)
    rd_x = ccx + (BOSS_OD/2 + 8) * math.cos(a)
    rd_y = ccy - (BOSS_OD/2 + 8) * math.sin(a)
    pdf.line(ccx, ccy, rd_x, rd_y)
    arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
    # label
    lx = ccx + (BOSS_OD/2 + 12) * math.cos(a)
    ly = ccy - (BOSS_OD/2 + 12) * math.sin(a)
    text(lx, ly, f"{int(ang_d)}°", size=TXT_D, anchor="middle")

# --- Top view dimensions ---
# Overall 100 (bottom)
hdim(tv(-50, -50)[0], tv(50, -50)[0], tv(0, -50)[1], tv(0, -50)[1] + DIM_O2, "100")
# Overall 100 (right)
vdim(tv(0, -50)[1], tv(0, 50)[1], tv(50, 0)[0], tv(50, 0)[0] + DIM_O2, "100")
# M6 pattern 75 (top)
hdim(tv(-m6_hp, m6_hp)[0], tv(m6_hp, m6_hp)[0],
     tv(0, m6_hp)[1], tv(0, m6_hp)[1] - DIM_O1, "75")
# M6 pattern 75 (left)
vdim(tv(0, m6_hp)[1], tv(0, -m6_hp)[1],
     tv(-m6_hp, 0)[0], tv(-m6_hp, 0)[0] - DIM_O1, "75")

# M3 diagonal 25 — diagonal dim from (-m3_hp,-m3_hp) to (m3_hp,m3_hp)
diag_p1 = tv(-m3_hp, -m3_hp)
diag_p2 = tv(m3_hp, m3_hp)
# Place a leader text
text(diag_p2[0] + 4, diag_p2[1] - 2, "对角 25", size=TXT_D, anchor="start")
# Draw a small diagonal arrow indicator
pdf.line(diag_p1[0], diag_p1[1], diag_p2[0], diag_p2[1])
arrow(diag_p1[0], diag_p1[1], -1, 1); arrow(diag_p2[0], diag_p2[1], 1, -1)

# Hole callouts — placed in the empty area RIGHT of the right 100 dim line.
# (Between the top-view right dim line at tv x≈+76 and Section A-A's leftmost
# extent there's ~75mm of empty space — plenty of room for two stacked callouts.)
#
# M6 callout: leader from RIGHT-SIDE M6 hole (upper-right). Leader ducks right
# past the dim line, then a horizontal stub carries the text.
hx, hy = tv(m6_hp, m6_hp)
lx, ly = tv(82, 28)
_w(EXT_W)
pdf.line(hx + M6_DIAM/2*0.7, hy - M6_DIAM/2*0.7, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1, f"4 × Φ{M6_DIAM:g} (M6 通孔)", size=TXT_D, anchor="start")

# M3 callout: leader from UPPER-RIGHT M3 hole, BELOW the M6 callout.
hx, hy = tv(m3_hp, m3_hp)
lx, ly = tv(82, 8)
pdf.line(hx + M3_DIAM/2*0.7, hy - M3_DIAM/2*0.7, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1,
     f"4 × Φ{M3_DIAM:g} 通孔 + Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 (底面)",
     size=TXT_D, anchor="start")

# Central CB callout: leader from CB edge at ~-45° (lower-right), text on the
# right side below the M3 callout.
ccb_a = math.radians(-45)
ccb_x = ccx + (CENTER_CB_DIAM/2) * math.cos(ccb_a)
ccb_y = ccy - (CENTER_CB_DIAM/2) * math.sin(ccb_a)
lx, ly = tv(82, -12)
pdf.line(ccb_x, ccb_y, lx, ly)
pdf.line(lx, ly, lx + 8, ly)
text(lx + 8, ly - 1,
     f"中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔 (顶面)",
     size=TXT_D, anchor="start")

# Boss callout — UPPER LEFT, leader from boss outer at 135°
bx, by = tv(BOSS_OD/2 * math.cos(math.radians(135)),
            BOSS_OD/2 * math.sin(math.radians(135)))
lx, ly = tv(-55, 44)
pdf.line(bx, by, lx, ly)
pdf.line(lx, ly, lx - 8, ly)
text(lx - 8, ly - 1, f"凸台 Φ{BOSS_OD:g} / Φ{BOSS_ID:g}, 高 {BOSS_H:g}",
     size=TXT_D, anchor="end")

# Notch callout — UPPER RIGHT, leader from notch arc midpoint (~90°) going up-right.
# Now sits alone in the top-right area since M6 callout moved to mid-right.
notch_mid_a = math.radians((NOTCH_A_S + NOTCH_A_E) / 2)
nx, ny = tv((BOSS_OD/2 + 4) * math.cos(notch_mid_a),
            (BOSS_OD/2 + 4) * math.sin(notch_mid_a))
lx, ly = tv(20, 56)
pdf.line(nx, ny, lx, ly)
pdf.line(lx, ly, lx + 10, ly)
text(lx + 10, ly - 1,
     f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}°, 高 {NOTCH_H:g} (距底面 {BASE_THICK:g}–{BASE_THICK+NOTCH_H:g})",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
sa_t_zero_x = 310     # PDF x where t=0
sa_z_zero_y = 165     # PDF y where z=0 (raised to free space below for Detail B)

def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 70, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 78,
     "(沿 +Y 方向剖切, 过槽口中分线 / cut along +Y axis through notch bisector)",
     size=TXT_I, anchor="middle")

# ----- Base section profile (no holes intersect this cut plane) -----
_w(GEOM_W)
# Bottom edge (z=0): full span, no cutouts
line(*sa(-T_BASE, 0), *sa(T_BASE, 0), GEOM_W)
# Top edge (z=BASE_THICK): broken where the LEFT boss wall covers it AND
# where the central Φ12 counterbore dips 1 mm into the top face.
# Right boss wall is removed by notch at this Z, so base top is visible there.
line(*sa(-T_BASE, BASE_THICK), *sa(-T_BO, BASE_THICK), GEOM_W)
# (gap from -T_BO to -T_BI: hidden under left boss wall)
line(*sa(-T_BI,  BASE_THICK), *sa(-T_CCB, BASE_THICK), GEOM_W)
# Central CB step: down at -T_CCB, floor at z=BASE_THICK-CENTER_CB_DEPTH, up at +T_CCB
line(*sa(-T_CCB, BASE_THICK), *sa(-T_CCB, BASE_THICK - CENTER_CB_DEPTH), GEOM_W)
line(*sa(-T_CCB, BASE_THICK - CENTER_CB_DEPTH),
     *sa( T_CCB, BASE_THICK - CENTER_CB_DEPTH), GEOM_W)
line(*sa( T_CCB, BASE_THICK - CENTER_CB_DEPTH), *sa( T_CCB, BASE_THICK), GEOM_W)
line(*sa( T_CCB, BASE_THICK), *sa( T_BASE, BASE_THICK), GEOM_W)

# Base left & right edges (z=0 to BASE_THICK)
line(*sa(-T_BASE, 0), *sa(-T_BASE, BASE_THICK), GEOM_W)
line(*sa( T_BASE, 0), *sa( T_BASE, BASE_THICK), GEOM_W)

# Outer left wall
line(*sa(-T_BO, BASE_THICK), *sa(-T_BO, BASE_THICK + BOSS_H), GEOM_W)
# Top of left wall
line(*sa(-T_BO, BASE_THICK + BOSS_H), *sa(-T_BI, BASE_THICK + BOSS_H), GEOM_W)
# Inner left wall
line(*sa(-T_BI, BASE_THICK + BOSS_H), *sa(-T_BI, BASE_THICK), GEOM_W)

# ----- Boss right wall (above notch, floating; notch removes lower NOTCH_H) -----
# Outer right wall
line(*sa(T_BO, BASE_THICK + NOTCH_H), *sa(T_BO, BASE_THICK + BOSS_H), GEOM_W)
# Top
line(*sa(T_BO, BASE_THICK + BOSS_H), *sa(T_BI, BASE_THICK + BOSS_H), GEOM_W)
# Inner right wall
line(*sa(T_BI, BASE_THICK + BOSS_H), *sa(T_BI, BASE_THICK + NOTCH_H), GEOM_W)
# Notch ceiling (bottom face of right wall)
line(*sa(T_BI, BASE_THICK + NOTCH_H), *sa(T_BO, BASE_THICK + NOTCH_H), GEOM_W)

# ----- Section A-A dimensions -----
# Stacked from the right side: boss height (large, closer), base thickness
# (narrow, further out). vdim handles the narrow-gap case automatically.
right_dim_x  = sa(T_BASE, 0)[0] + DIM_O1
right_dim_x2 = sa(T_BASE, 0)[0] + DIM_O2
vdim(sa(0, BASE_THICK + BOSS_H)[1], sa(0, BASE_THICK)[1],
     sa(T_BASE, 0)[0], right_dim_x, f"{BOSS_H:g}")
vdim(sa(0, BASE_THICK)[1], sa(0, 0)[1],
     sa(T_BASE, 0)[0], right_dim_x2, f"{BASE_THICK:g}")
# Notch height — outside the right boss wall (uses vdim's narrow-gap handling)
notch_dim_x = sa(T_BO + 8, 0)[0]
vdim(sa(0, BASE_THICK + NOTCH_H)[1], sa(0, BASE_THICK)[1],
     sa(T_BO, 0)[0], notch_dim_x, f"{NOTCH_H:g}")

# Wall thickness 5 (boss wall, on left side, above) — kept at DIM_O1
hdim(sa(-T_BO, 0)[0], sa(-T_BI, 0)[0],
     sa(0, BASE_THICK + BOSS_H)[1],
     sa(0, BASE_THICK + BOSS_H)[1] - DIM_O1, f"{(BOSS_OD-BOSS_ID)/2:g}")

# Boss ID (Φ55) at DIM_O2 — not DIM_O1, because that level is taken by the
# wall-thickness "5" dim on the left and they would share an endpoint arrow.
hdim(sa(-T_BI, 0)[0], sa(T_BI, 0)[0],
     sa(0, BASE_THICK + BOSS_H)[1],
     sa(0, BASE_THICK + BOSS_H)[1] - DIM_O2, f"Φ{BOSS_ID:g}")
# Boss OD (Φ65) at DIM_O3 — further out (longer span, outer walls)
hdim(sa(-T_BO, 0)[0], sa(T_BO, 0)[0],
     sa(0, BASE_THICK + BOSS_H)[1],
     sa(0, BASE_THICK + BOSS_H)[1] - DIM_O3, f"Φ{BOSS_OD:g}")

# Central Φ12 × 1mm CB — inline dim inside the boss inner cavity
# (yg at base top = step; yd ~10mm above, well below boss-top dim stack at y=137)
hdim(sa(-T_CCB, 0)[0], sa(T_CCB, 0)[0],
     sa(0, BASE_THICK)[1], sa(0, BASE_THICK + 10)[1],
     f"Φ{CENTER_CB_DIAM:g} mm × 深 {CENTER_CB_DEPTH:g} mm")

# Bottom dim: base side
hdim(sa(-T_BASE, 0)[0], sa(T_BASE, 0)[0],
     sa(0, 0)[1], sa(0, 0)[1] + DIM_O2, f"{BASE_SIDE:g}")

# ===== DETAIL B (3:1) — M3 + Φ7 CB stepped hole stack =====
# Section A-A cut plane doesn't pass through M3 holes, so the counterbore
# step isn't visible there. Detail B shows that stepped hole structure.
DB_SCALE = 3.0
db_cx, db_cy = sa_t_zero_x, 240     # below section A-A
DB_DIM_O = 12.0                      # tighter dim offset for the detail
def db(t, z): return (db_cx + t * DB_SCALE, db_cy - z * DB_SCALE)

# Title above the detail, well clear of section A-A's "100" bottom dim
text(db_cx, db_cy - BASE_THICK * DB_SCALE - DB_DIM_O - 6,
     "详图 B  Detail B  (3:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Half-widths in real mm; context rectangle ~20mm wide
DB_HALF_BASE  = 10.0          # 20mm wide base context
DB_HALF_CB    = CB_DIAM / 2   # 3.5
DB_HALF_M3    = M3_DIAM / 2   # 1.6

# Draw base profile with stepped cutout, going around clockwise from
# bottom-left corner. The hole is centered at t=0; CB is on bottom (z=0..CB_DEPTH),
# narrowing to M3 from z=CB_DEPTH up to z=BASE_THICK.
_w(GEOM_W)
# Bottom edge: left part + (CB opening gap) + right part
line(*db(-DB_HALF_BASE, 0),       *db(-DB_HALF_CB, 0),       GEOM_W)
line(*db( DB_HALF_CB,   0),       *db( DB_HALF_BASE, 0),     GEOM_W)
# CB walls (vertical from z=0 to z=CB_DEPTH on each side)
line(*db(-DB_HALF_CB, 0),         *db(-DB_HALF_CB, CB_DEPTH),GEOM_W)
line(*db( DB_HALF_CB, 0),         *db( DB_HALF_CB, CB_DEPTH),GEOM_W)
# CB shoulder (horizontal step at z=CB_DEPTH, from CB wall to M3 wall)
line(*db(-DB_HALF_CB, CB_DEPTH),  *db(-DB_HALF_M3, CB_DEPTH),GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH),  *db( DB_HALF_CB, CB_DEPTH),GEOM_W)
# M3 walls (vertical from z=CB_DEPTH up to z=BASE_THICK)
line(*db(-DB_HALF_M3, CB_DEPTH),  *db(-DB_HALF_M3, BASE_THICK), GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH),  *db( DB_HALF_M3, BASE_THICK), GEOM_W)
# Top edge: left part + (M3 opening gap) + right part
line(*db(-DB_HALF_BASE, BASE_THICK), *db(-DB_HALF_M3, BASE_THICK), GEOM_W)
line(*db( DB_HALF_M3,   BASE_THICK), *db( DB_HALF_BASE, BASE_THICK), GEOM_W)
# Left & right outer edges
line(*db(-DB_HALF_BASE, 0), *db(-DB_HALF_BASE, BASE_THICK), GEOM_W)
line(*db( DB_HALF_BASE, 0), *db( DB_HALF_BASE, BASE_THICK), GEOM_W)

# Centerline (dashed)
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(db(0, -2)[0], db(0, -2)[1], db(0, BASE_THICK + 2)[0], db(0, BASE_THICK + 2)[1])
pdf.set_dash_pattern()
_w(GEOM_W)

# Dims — base thickness (5) on RIGHT, CB depth (2) on LEFT.
# Both are at 3:1 scale so they appear with plenty of room for inward arrows.
vdim(db(0, BASE_THICK)[1], db(0, 0)[1],
     db(DB_HALF_BASE, 0)[0], db(DB_HALF_BASE, 0)[0] + DB_DIM_O,
     f"{BASE_THICK:g}")
vdim(db(0, CB_DEPTH)[1], db(0, 0)[1],
     db(-DB_HALF_BASE, 0)[0], db(-DB_HALF_BASE, 0)[0] - DB_DIM_O,
     f"{CB_DEPTH:g}")
# Φ7 (CB diam) at BOTTOM — dim line below the base
hdim(db(-DB_HALF_CB, 0)[0], db(DB_HALF_CB, 0)[0],
     db(0, 0)[1], db(0, 0)[1] + DB_DIM_O,
     f"Φ{CB_DIAM:g}")
# Φ3.2 (M3 diam) at TOP — dim line above the base
hdim(db(-DB_HALF_M3, 0)[0], db(DB_HALF_M3, 0)[0],
     db(0, BASE_THICK)[1], db(0, BASE_THICK)[1] - DB_DIM_O,
     f"Φ{M3_DIAM:g}")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 底盘 (Baseplate)", size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"100×100×{BASE_THICK:g} / 4×M6 / 4×M3+Φ7×{CB_DEPTH:g} 沉孔 / 中央 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔(顶) / 凸台 Φ65/Φ55 H23 / 槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° H{NOTCH_H:g}  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-04  /  POV3D / models / baseplate / baseplate.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("baseplate_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
