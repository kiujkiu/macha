"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D
flanged annular disc.

Two views:
  1) TOP VIEW   (俯视图, 1:1)     — disc outline, inner & outer boss rings,
                                    16 M3 hole pattern (with crosshairs and
                                    Φ3.2 callouts), outer-boss cutout at
                                    40°-50° (boss outline broken in that wedge),
                                    slot at 0°-10° shown with dashed radial
                                    lines + angle annotations.
  2) SECTION A-A (剖视图 A-A, 1:1) — cut along the +X axis (0°). The +t side
                                    shows the slot profile (gap at Z=3..5
                                    in base, Z=5..7 = full outer boss), the
                                    -t side (180°) shows the full intact
                                    section.
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
BASE_OD = 165.0
BASE_ID = 65.0
BASE_T  = 4.5  # 底盘厚度 5→4.5

INNER_BOSS_OD = 80.0
INNER_BOSS_ID = 65.0
OUTER_BOSS_OD = 165.0
OUTER_BOSS_ID = 145.0
BOSS_T        = 2.5     # synced to build_stl.py (was 2.0 → 2.5)
TOTAL_H       = BASE_T + BOSS_T  # 7.5

M3_DIAM = 3.2
N_HOLES = 8
HOLE_ROTATION = -22.5  # CW 20°
M42_DIAM = 4.2
M42_DEPTH = 4.0

INNER_HOLE_R = (INNER_BOSS_ID/2 + INNER_BOSS_OD/2) / 2   # 36.25
OUTER_HOLE_R = (OUTER_BOSS_ID/2 + OUTER_BOSS_OD/2) / 2   # 77.5

OUTER_CUT_A_S = 40.0
OUTER_CUT_A_E = 50.0

SLOT_R_IN  = 40.0
SLOT_R_OUT = 82.5
SLOT_Z_BOT = 2.0
SLOT_Z_TOP = 7.0
SLOT_A_S   = 0.0
SLOT_A_E   = 5.0

# Convenience
R_BO = BASE_OD / 2      # 82.5
R_BI = BASE_ID / 2      # 32.5
R_IBO = INNER_BOSS_OD/2 # 40.0
R_IBI = INNER_BOSS_ID/2 # 32.5
R_OBO = OUTER_BOSS_OD/2 # 82.5
R_OBI = OUTER_BOSS_ID/2 # 72.5

# Section A-A cut direction = +X axis (0°). +t side is 0° (inside slot 0..10°).
# -t side is 180° (outside slot and outside cutout).

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
import os
_font_paths = ["/mnt/c/Windows/Fonts/simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"]
_font = next((p for p in _font_paths if os.path.exists(p)), None)
if _font is None: raise FileNotFoundError("SimHei not found")
pdf.add_font("SimHei", "", _font)

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
text(PAGE_W/2, 13, "POV 3D 法兰盘  Flange Disc", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19,
     f"Φ{BASE_OD:g}/Φ{BASE_ID:g}×{BASE_T:g} 基环 / 内凸缘 Φ{INNER_BOSS_OD:g}/Φ{INNER_BOSS_ID:g}×{BOSS_T:g} / "
     f"外凸缘 Φ{OUTER_BOSS_OD:g}/Φ{OUTER_BOSS_ID:g}×{BOSS_T:g} / 16×Φ{M3_DIAM:g} M3 通孔 / "
     f"外缘缺口 {OUTER_CUT_A_S:g}°–{OUTER_CUT_A_E:g}° / 槽口 {SLOT_A_S:g}°–{SLOT_A_E:g}°",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 110, 155
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 30, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A cutting line — along +X (0° / 180°)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
end1 = tv(R_BO + 14, 0); end2 = tv(-R_BO - 14, 0)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
text(end1[0] + 2, end1[1] + 4, "A", size=6)
text(end2[0] - 7, end2[1] + 4, "A", size=6)

# ---- Geometry circles ----
_w(GEOM_W)
ccx, ccy = tv(0, 0)
# Base OD 165
pdf.circle(ccx, ccy, R_BO, style="D")
# Base ID 65
pdf.circle(ccx, ccy, R_BI, style="D")
# Inner boss OD 80
pdf.circle(ccx, ccy, R_IBO, style="D")
# Outer boss ID 145 (the inner edge of outer boss)
pdf.circle(ccx, ccy, R_OBI, style="D")

# ---- Outer-boss cutout 40°-50° : break the boss outlines in that wedge ----
# To draw a circle with a gap, we draw a poly-arc skipping the wedge angles.
# Wipe out the (already drawn) circles inside cutout wedge by overdrawing white.
# Simpler: just draw radial closing lines at 40° and 50° on the outer boss,
# and accept the full circles (the wedge is visually called out with the
# dashed radials + angle labels). To clearly indicate the gap, however,
# we use white-fill triangles to erase the outer boss outline arcs in the wedge.
#
# Cleaner approach: draw the outer-boss outline manually as TWO arcs
# (50°..40° going the "long way", i.e. 50°->360°+40°), leaving the wedge open.
# Re-draw the OD and OBI as broken arcs; first erase the already drawn full circles
# in the wedge area by overdrawing in white.
def draw_broken_circle(cx, cy, r, gap_start_deg, gap_end_deg, n=180):
    """Draw circle outline as polyline, skipping angular range [gap_start, gap_end]."""
    # parametrize from gap_end CCW around to gap_start
    a0 = gap_end_deg
    a1 = gap_start_deg + 360.0
    span = a1 - a0
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + i * span / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    for i in range(len(pts) - 1):
        pdf.line(*pts[i], *pts[i+1])

# Erase the cutout-wedge portions of the full circles by re-drawing in white
pdf.set_draw_color(255, 255, 255); _w(GEOM_W + 0.4)
# erase OD wedge arc
n_wipe = 24
for r in (R_BO, R_OBI):
    pts = []
    for i in range(n_wipe + 1):
        a = math.radians(OUTER_CUT_A_S + i * (OUTER_CUT_A_E - OUTER_CUT_A_S) / n_wipe)
        pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
    for i in range(len(pts) - 1):
        pdf.line(*pts[i], *pts[i+1])
pdf.set_draw_color(0, 0, 0)
_w(GEOM_W)

# Now draw closing radial segments at 40° and 50° between R_OBI and R_BO (boss ends)
for ang_d in (OUTER_CUT_A_S, OUTER_CUT_A_E):
    a = math.radians(ang_d)
    x_in  = ccx + R_OBI * math.cos(a)
    y_in  = ccy - R_OBI * math.sin(a)
    x_out = ccx + R_BO * math.cos(a)
    y_out = ccy - R_BO * math.sin(a)
    pdf.line(x_in, y_in, x_out, y_out)

# ---- Slot 0°-10° : with slot Z=3..7 the outer boss is FULLY removed in this
#      wedge (no cap above the slot), and only 3 mm of base remains at the
#      bottom (Z=0..3). From above, the wedge shows as exposed base floor at
#      Z=3 in R=40..82.5 (no outer-boss material left in the wedge at all).
#      Show slot as DASHED radial lines at 0° and 10° from R_IBO (40) to R_BO (82.5).
pdf.set_dash_pattern(dash=2.0, gap=1.0); _w(HID_W)
for ang_d in (SLOT_A_S, SLOT_A_E):
    a = math.radians(ang_d)
    x_in  = ccx + SLOT_R_IN  * math.cos(a)
    y_in  = ccy - SLOT_R_IN  * math.sin(a)
    x_out = ccx + SLOT_R_OUT * math.cos(a)
    y_out = ccy - SLOT_R_OUT * math.sin(a)
    pdf.line(x_in, y_in, x_out, y_out)
pdf.set_dash_pattern()
_w(GEOM_W)

# ---- 16 × M3 holes ----
def draw_hole(cx, cy, r=M3_DIAM/2):
    pdf.circle(cx, cy, r, style="D")
    # tiny crosshair
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(cx-2.5, cy, cx+2.5, cy)
    pdf.line(cx, cy-2.5, cx, cy+2.5)
    pdf.set_dash_pattern()
    _w(GEOM_W)

inner_hole_centers = []
for k in range(N_HOLES):
    ang_d = k * 360.0 / N_HOLES + HOLE_ROTATION
    a = math.radians(ang_d)
    cx = ccx + INNER_HOLE_R * math.cos(a)
    cy = ccy - INNER_HOLE_R * math.sin(a)
    inner_hole_centers.append((cx, cy, ang_d))
    draw_hole(cx, cy)
    # M4.2 counterbore (dashed circle, 沉孔 from bottom)
    pdf.set_dash_pattern(dash=2, gap=1)
    _w(0.15)
    pdf.circle(cx, cy, M42_DIAM/2, style="D")
    pdf.set_dash_pattern()
    _w(GEOM_W)

outer_hole_centers = []
for k in range(N_HOLES):
    ang_d = k * 360.0 / N_HOLES + HOLE_ROTATION
    # 25° (rotated 45°) outer hole is eaten by the 40-50° cutout — skip drawing it
    if OUTER_CUT_A_S - 0.5 <= ang_d <= OUTER_CUT_A_E + 0.5:
        continue
    a = math.radians(ang_d)
    cx = ccx + OUTER_HOLE_R * math.cos(a)
    cy = ccy - OUTER_HOLE_R * math.sin(a)
    outer_hole_centers.append((cx, cy, ang_d))
    draw_hole(cx, cy)
    # M4.2 counterbore (dashed circle, 沉孔 from bottom)
    pdf.set_dash_pattern(dash=2, gap=1)
    _w(0.15)
    pdf.circle(cx, cy, M42_DIAM/2, style="D")
    pdf.set_dash_pattern()
    _w(GEOM_W)

# Center cross (axis lines) — dashed
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(tv(-R_BO - 8, 0)[0], tv(-R_BO - 8, 0)[1],
         tv( R_BO + 8, 0)[0], tv( R_BO + 8, 0)[1])
pdf.line(tv(0, -R_BO - 8)[0], tv(0, -R_BO - 8)[1],
         tv(0,  R_BO + 8)[0], tv(0,  R_BO + 8)[1])
pdf.set_dash_pattern()

# ---- Angular annotations: outer cutout (40°, 50°) ----
_w(DIM_W)
for ang_d in (OUTER_CUT_A_S, OUTER_CUT_A_E):
    a = math.radians(ang_d)
    # radial dim line just outside OD
    rd_x = ccx + (R_BO + 6) * math.cos(a)
    rd_y = ccy - (R_BO + 6) * math.sin(a)
    pdf.line(ccx + R_BO * math.cos(a), ccy - R_BO * math.sin(a), rd_x, rd_y)
    arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
    # label well past arrowhead
    lx = ccx + (R_BO + 14) * math.cos(a)
    ly = ccy - (R_BO + 14) * math.sin(a)
    text(lx, ly + 1.2, f"{ang_d:g}°", size=TXT_D, anchor="middle")

# ---- Angular annotations: slot 0° and 10° ----
# 0° label needs separation from section line ("A" mark) — put the leader+arrow
# tighter and label outside the disc.
for ang_d in (SLOT_A_S, SLOT_A_E):
    a = math.radians(ang_d)
    rd_x = ccx + (R_BO + 6) * math.cos(a)
    rd_y = ccy - (R_BO + 6) * math.sin(a)
    pdf.line(ccx + R_BO * math.cos(a), ccy - R_BO * math.sin(a), rd_x, rd_y)
    arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
    # Push labels well outside the arrowhead (arrow tip at R_BO+6, label at +14)
    lx = ccx + (R_BO + 14) * math.cos(a)
    ly = ccy - (R_BO + 14) * math.sin(a)
    if ang_d == 0:
        ly += 7   # push the 0° label well below the section-line "A"
        lx += 1
    text(lx, ly + 1.2, f"{ang_d:g}°", size=TXT_D, anchor="middle")

# ---- Top-view dimensions ----
# Φ165 horizontal across top
hdim(tv(-R_BO, 0)[0], tv(R_BO, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O1, f"Φ{BASE_OD:g}")
# Φ145 (outer boss ID), stacked further out
hdim(tv(-R_OBI, 0)[0], tv(R_OBI, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O2, f"Φ{OUTER_BOSS_ID:g}")
# Φ80 (inner boss OD), stacked even further out
hdim(tv(-R_IBO, 0)[0], tv(R_IBO, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O3, f"Φ{INNER_BOSS_OD:g}")
# Φ65 (base ID) on bottom
hdim(tv(-R_BI, 0)[0], tv(R_BI, 0)[0],
     tv(0, -R_BO)[1], tv(0, -R_BO)[1] + DIM_O1, f"Φ{BASE_ID:g}")

# Inner-hole PCD callout — leader from SW inner hole (225°), goes down-left to below the disc
ih_a = math.radians(225)
ih_x = ccx + INNER_HOLE_R * math.cos(ih_a)
ih_y = ccy - INNER_HOLE_R * math.sin(ih_a)
ih_lx, ih_ly = tv(-65, -78)
_w(EXT_W)
pdf.line(ih_x, ih_y, ih_lx, ih_ly)
pdf.line(ih_lx, ih_ly, ih_lx + 8, ih_ly)
text(ih_lx + 8, ih_ly - 1.2,
     f"8 × Φ{M3_DIAM:g} 内圈通孔, PCD Φ{2*INNER_HOLE_R:g}",
     size=TXT_D, anchor="start")

# Outer-hole PCD callout — leader from SW outer hole (225°), goes down-left further out
oh_a = math.radians(225)
oh_x = ccx + OUTER_HOLE_R * math.cos(oh_a)
oh_y = ccy - OUTER_HOLE_R * math.sin(oh_a)
oh_lx, oh_ly = tv(-65, -93)
pdf.line(oh_x, oh_y, oh_lx, oh_ly)
pdf.line(oh_lx, oh_ly, oh_lx + 8, oh_ly)
text(oh_lx + 8, oh_ly - 1.2,
     f"8 × Φ{M3_DIAM:g} 外圈通孔, PCD Φ{2*OUTER_HOLE_R:g} (45° 位置被缺口截除)",
     size=TXT_D, anchor="start")

# Cutout callout — leader from the wedge midpoint to upper-right
cut_mid_a = math.radians((OUTER_CUT_A_S + OUTER_CUT_A_E) / 2)
cx_lead = ccx + (R_BO - 4) * math.cos(cut_mid_a)
cy_lead = ccy - (R_BO - 4) * math.sin(cut_mid_a)
cut_lx, cut_ly = tv(70, 60)
pdf.line(cx_lead, cy_lead, cut_lx, cut_ly)
pdf.line(cut_lx, cut_ly, cut_lx + 8, cut_ly)
text(cut_lx + 8, cut_ly - 1.2,
     f"外凸缘缺口 {OUTER_CUT_A_S:g}°–{OUTER_CUT_A_E:g}° (仅去除凸缘)",
     size=TXT_D, anchor="start")

# Slot callout — leader from slot midpoint (5°) to upper-right area
slot_mid_a = math.radians((SLOT_A_S + SLOT_A_E) / 2)
slot_r_mid = (SLOT_R_IN + SLOT_R_OUT) / 2
sx_lead = ccx + slot_r_mid * math.cos(slot_mid_a)
sy_lead = ccy - slot_r_mid * math.sin(slot_mid_a)
slot_lx, slot_ly = tv(70, 48)
pdf.line(sx_lead, sy_lead, slot_lx, slot_ly)
pdf.line(slot_lx, slot_ly, slot_lx + 8, slot_ly)
text(slot_lx + 8, slot_ly - 1.2,
     f"槽口 {SLOT_A_S:g}°–{SLOT_A_E:g}°, R{SLOT_R_IN:g}–R{SLOT_R_OUT:g}, Z{SLOT_Z_BOT:g}–{SLOT_Z_TOP:g}",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
# Cut along +X axis. Section coords: t along the cut direction (real X),
# z is vertical. Section is taken at 0° / 180° azimuth.
#
# +t side (0°, inside slot 0°-10°): slot removes a chunk from base + outer boss.
# -t side (180°, no slot, no cutout): full intact profile.
#
# Holes at 0° and 180°: there ARE holes at 0° on both inner & outer rings,
# and at 180° on both. The cut plane passes exactly through these centers,
# so we'd show vertical lines (hole walls). For drawing clarity, we'll show
# the holes as vertical-dashed centerlines + actual hole walls (since these
# are right at the section plane).

sa_t_zero_x = 295
sa_z_zero_y = 215
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 50, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 57,
     "(沿 0°–180° 轴剖切 / cut along the X axis; +t = 0° through slot, -t = 180°)",
     size=TXT_I, anchor="middle")

_w(GEOM_W)

# ---------- LEFT SIDE (-t side, real 180°): full intact profile ----------
# Walls at t = -R_BO, -R_OBO_inner, -R_IBO, -R_BI (mirror of right).
# Base spans t = -R_BO ... -R_BI, Z = 0..BASE_T (full, intact).
# Inner boss spans t = -R_IBO ... -R_BI, Z = BASE_T..TOTAL_H.
# Outer boss spans t = -R_BO ... -R_OBI, Z = BASE_T..TOTAL_H.
# Holes at 180° on inner ring (PCD R=36.25) and outer ring (PCD R=77.5).
# Hole "walls" at t = -INNER_HOLE_R ± M3/2  and  t = -OUTER_HOLE_R ± M3/2.

# Base bottom (z=0): solid horizontal from -R_BO to -R_BI
line(*sa(-R_BO, 0), *sa(-R_BI, 0), GEOM_W)
# Base top (z=BASE_T): solid horizontal from -R_BO to -R_BI
line(*sa(-R_BO, BASE_T), *sa(-R_BI, BASE_T), GEOM_W)
# Base left edge (outer): vertical from z=0 to z=TOTAL_H (because outer boss sits on it)
line(*sa(-R_BO, 0), *sa(-R_BO, TOTAL_H), GEOM_W)
# Base inner edge (ID): vertical from z=0 to z=TOTAL_H (inner boss sits on top)
line(*sa(-R_BI, 0), *sa(-R_BI, TOTAL_H), GEOM_W)

# Inner boss on left side: at t = -R_IBO (= -40), inner wall
# Top of inner boss (z=TOTAL_H): horizontal from -R_IBO to -R_BI (inner boss ID)
line(*sa(-R_IBO, TOTAL_H), *sa(-R_BI, TOTAL_H), GEOM_W)
# Inner boss outer wall (vertical at t=-R_IBO from z=BASE_T to z=TOTAL_H)
line(*sa(-R_IBO, BASE_T), *sa(-R_IBO, TOTAL_H), GEOM_W)

# Outer boss on left side at t = -R_OBI (= -72.5), inner wall (R_OBI is "inner" of outer boss)
# Top of outer boss (z=TOTAL_H): horizontal from -R_BO to -R_OBI
line(*sa(-R_BO, TOTAL_H), *sa(-R_OBI, TOTAL_H), GEOM_W)
# Outer boss inner wall (vertical at t=-R_OBI from z=BASE_T to z=TOTAL_H)
line(*sa(-R_OBI, BASE_T), *sa(-R_OBI, TOTAL_H), GEOM_W)

# ---------- RIGHT SIDE (+t side, real 0°): slot cuts base + outer boss ----------
# Slot removes material in 0°-10° wedge, R = 40..82.5, Z = SLOT_Z_BOT..SLOT_Z_TOP
# (currently 3..7). In the +X half (at 0°), inside the slot: base bottom
# Z=0..SLOT_Z_BOT remains, base top SLOT_Z_BOT..BASE_T removed (in R 40..82.5),
# outer boss Z=BASE_T..TOTAL_H FULLY removed (in R 72.5..82.5) — no cap left.
#
# Inner boss is at R 32.5..40, OUTSIDE the slot's inner R=40 — fully intact.

# Base bottom (z=0): solid from R_BI to R_BO (no slot cut on bottom)
line(*sa(R_BI, 0), *sa(R_BO, 0), GEOM_W)
# Base top (z=BASE_T): solid from R_BI to R_IBO (=40), then broken in slot
# (R 40..82.5 has slot from z=SLOT_Z_BOT..BASE_T → no top surface here at z=BASE_T).
line(*sa(R_BI, BASE_T), *sa(R_IBO, BASE_T), GEOM_W)

# Slot floor at z=SLOT_Z_BOT (=3): horizontal from R_IBO to R_BO — this is the
# new top surface of the remaining base in the slot wedge.
line(*sa(R_IBO, SLOT_Z_BOT), *sa(R_BO, SLOT_Z_BOT), GEOM_W)

# Vertical edges of the slot (slot side walls in the section view):
# At t = R_IBO (=40): slot inner wall climbs from z=SLOT_Z_BOT all the way to
# z=TOTAL_H — because slot now extends to top of boss with no cap. This wall
# coincides with the outer wall of the inner boss above z=BASE_T (inner boss is
# intact), so it's a single continuous vertical from z=SLOT_Z_BOT to z=TOTAL_H.
line(*sa(R_IBO, SLOT_Z_BOT), *sa(R_IBO, TOTAL_H), GEOM_W)
# At t = R_BO (=82.5): outer rim of disc — intact full vertical from z=0 to z=TOTAL_H.
line(*sa(R_BO, 0), *sa(R_BO, TOTAL_H), GEOM_W)
# (No outer-boss cap above the slot anymore — nothing to draw at z=SLOT_Z_TOP or
# at the inner face of the outer boss inside the wedge.)

# Inner boss on right side: at t = R_BI (32.5) to t = R_IBO (40), z = BASE_T..TOTAL_H
# Top
line(*sa(R_BI, TOTAL_H), *sa(R_IBO, TOTAL_H), GEOM_W)
# Outer wall of inner boss is part of the continuous vertical drawn above at t=R_IBO.

# Hatching: simple light diagonals on the cut material would be nice but not required.
# Skipping for cleanliness.

# ---- Section dimensions ----
# Total height on LEFT side (closest only, DIM_O1).
left_total_x = sa(-R_BO, 0)[0] - DIM_O1
vdim(sa(0, TOTAL_H)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_total_x, f"{TOTAL_H:g}")
# Base thickness on LEFT (further out, DIM_O2)
left_base_x = sa(-R_BO, 0)[0] - DIM_O2
vdim(sa(0, BASE_T)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_base_x, f"{BASE_T:g}")

# RIGHT-side vertical dims: slot Z chain
# Slot floor z=0..SLOT_Z_BOT (DIM_O1), slot height SLOT_Z_BOT..SLOT_Z_TOP (DIM_O2)
# With slot extending fully to top (SLOT_Z_TOP == TOTAL_H), no cap segment to dim.
right_dim_x1 = sa(R_BO, 0)[0] + DIM_O1
vdim(sa(0, SLOT_Z_BOT)[1], sa(0, 0)[1],
     sa(R_BO, 0)[0], right_dim_x1, f"{SLOT_Z_BOT:g}")
right_dim_x2 = sa(R_BO, 0)[0] + DIM_O2
vdim(sa(0, SLOT_Z_TOP)[1], sa(0, SLOT_Z_BOT)[1],
     sa(R_BO, 0)[0], right_dim_x2, f"{SLOT_Z_TOP-SLOT_Z_BOT:g}")
if TOTAL_H - SLOT_Z_TOP > 1e-6:
    right_dim_x3 = sa(R_BO, 0)[0] + DIM_O3
    vdim(sa(0, TOTAL_H)[1], sa(0, SLOT_Z_TOP)[1],
         sa(R_BO, 0)[0], right_dim_x3, f"{TOTAL_H-SLOT_Z_TOP:g}")
# Boss thickness — on LEFT, far out (DIM_O3)
left_boss_x = sa(-R_BO, 0)[0] - DIM_O3
vdim(sa(0, TOTAL_H)[1], sa(0, BASE_T)[1],
     sa(-R_BO, 0)[0], left_boss_x, f"{BOSS_T:g}")

# Top horizontal dims: Φ165 (overall OD) and Φ65 (overall ID).
top_dim_y1 = sa(0, TOTAL_H)[1] - DIM_O1
hdim(sa(-R_BO, 0)[0], sa(R_BO, 0)[0],
     sa(0, TOTAL_H)[1], top_dim_y1, f"Φ{BASE_OD:g}")
top_dim_y2 = sa(0, TOTAL_H)[1] - DIM_O2
hdim(sa(-R_BI, 0)[0], sa(R_BI, 0)[0],
     sa(0, TOTAL_H)[1], top_dim_y2, f"Φ{BASE_ID:g}")
# Φ80 (inner boss OD)
top_dim_y3 = sa(0, TOTAL_H)[1] - DIM_O3
hdim(sa(-R_IBO, 0)[0], sa(R_IBO, 0)[0],
     sa(0, TOTAL_H)[1], top_dim_y3, f"Φ{INNER_BOSS_OD:g}")
# Φ145 (outer boss ID) — even further (above the Φ80 line, stack at +12 more)
top_dim_y4 = sa(0, TOTAL_H)[1] - (DIM_O3 + 12)
hdim(sa(-R_OBI, 0)[0], sa(R_OBI, 0)[0],
     sa(0, TOTAL_H)[1], top_dim_y4, f"Φ{OUTER_BOSS_ID:g}")

# Slot label inside the section (annotation in the slot gap)
slot_lbl_x = (sa(R_IBO, 0)[0] + sa(R_BO, 0)[0]) / 2
slot_lbl_y = (sa(0, SLOT_Z_BOT)[1] + sa(0, SLOT_Z_TOP)[1]) / 2
text(slot_lbl_x, slot_lbl_y + 1, "槽口", size=TXT_D, anchor="middle")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — 法兰盘 (Flange Disc)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_OD:g}/Φ{BASE_ID:g}×{BASE_T:g} / 凸缘 Φ{INNER_BOSS_OD:g}+Φ{OUTER_BOSS_ID:g}×{BOSS_T:g} / "
     f"16×Φ{M3_DIAM:g} M3 / 外缘缺口 {OUTER_CUT_A_S:g}°–{OUTER_CUT_A_E:g}° / "
     f"槽口 {SLOT_A_S:g}°–{SLOT_A_E:g}° Z{SLOT_Z_BOT:g}–{SLOT_Z_TOP:g}  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-04  /  POV3D / models / flange_disc / flange_disc.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("flange_disc_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
