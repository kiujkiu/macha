"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D
mounting flange.

Two views + one detail:
  1) TOP VIEW       (俯视图, 1:1)        — disc outline, rim-boss ring (broken
                                          in two angular wedges at 0°-10° and
                                          40°-50°), all 16 M3+CB holes with
                                          dashed Φ7 CB and crosshair, PCD
                                          arcs.
  2) SECTION A-A    (剖视图 A-A, 1:1)    — cut at 90° (+Y axis), which passes
                                          through the inner-PCD and outer-PCD
                                          holes at 90°. Rim boss is intact on
                                          both sides.
  3) DETAIL B       (详图 B, 3:1)        — zoom on one M3+CB stepped hole.
"""

import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
BASE_OD = 170.0
BASE_ID = 65.0
BASE_T  = 3.0

BOSS_OD = 170.0
BOSS_ID = 165.0
BOSS_H  = 7.0
TOTAL_H = BASE_T + BOSS_H   # 10

M3_DIAM  = 3.2
CB_DIAM  = 7.0
CB_DEPTH = 2.0
N_HOLES  = 8
HOLE_ROTATION = 22.5  # CCW 22.5°

INNER_HOLE_R = 36.25      # PCD 72.5
OUTER_HOLE_R = 77.5       # PCD 155
INNER_PCD = 2 * INNER_HOLE_R
OUTER_PCD = 2 * OUTER_HOLE_R

CUT1_A_S = -5.0
CUT1_A_E = 0.0
CUT2_A_S = -45.0
CUT2_A_E = -40.0

# Convenience
R_BO  = BASE_OD / 2     # 85.0
R_BI  = BASE_ID / 2     # 32.5
R_OBI = BOSS_ID / 2     # 82.5 (inside wall of rim boss)
R_OBO = BOSS_OD / 2     # 85.0 (outside wall = base OD)

# Section A-A: cut along +Y axis (90°), passes through the two 90° hole stacks.
# Both ±Y sides show identical intact rim boss outside and a stepped hole.

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
text(PAGE_W/2, 13, "POV 3D 安装法兰  Mounting Flange",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19,
     f"基环 Φ{BASE_OD:g}/Φ{BASE_ID:g}×{BASE_T:g} / 外缘凸圈 Φ{BOSS_OD:g}/Φ{BOSS_ID:g}×{BOSS_H:g} / "
     f"16×Φ{M3_DIAM:g} 通孔 + Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 (底面) / "
     f"凸圈缺口 {CUT1_A_S:g}°–{CUT1_A_E:g}° 及 {CUT2_A_S:g}°–{CUT2_A_E:g}°",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 120, 158
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 30, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A cutting line — along +Y axis (90° / 270°)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
end1 = tv(0,  R_BO + 14)   # top  (90°)
end2 = tv(0, -R_BO - 14)   # bot  (270°)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
text(end1[0] + 3, end1[1] + 4, "A", size=6)
text(end2[0] + 3, end2[1] - 1, "A", size=6)

# ---- Geometry circles ----
_w(GEOM_W)
ccx, ccy = tv(0, 0)
# Base OD 170
pdf.circle(ccx, ccy, R_BO, style="D")
# Base ID 65
pdf.circle(ccx, ccy, R_BI, style="D")
# Rim boss ID 165 (inner edge of rim boss)
pdf.circle(ccx, ccy, R_OBI, style="D")

# ---- Erase the cutout-wedge portions of the OD and OBI circles by re-drawing
# them in white (matches flange_disc pattern). Then close with radial segments.
pdf.set_draw_color(255, 255, 255); _w(GEOM_W + 0.4)
n_wipe = 24
for (a_s, a_e) in ((CUT1_A_S, CUT1_A_E), (CUT2_A_S, CUT2_A_E)):
    for r in (R_BO, R_OBI):
        pts = []
        for i in range(n_wipe + 1):
            a = math.radians(a_s + i * (a_e - a_s) / n_wipe)
            pts.append((ccx + r * math.cos(a), ccy - r * math.sin(a)))
        for i in range(len(pts) - 1):
            pdf.line(*pts[i], *pts[i+1])
pdf.set_draw_color(0, 0, 0)
_w(GEOM_W)

# Radial closing lines at cutout edges between R_OBI and R_BO (boss-only gap)
for (a_s, a_e) in ((CUT1_A_S, CUT1_A_E), (CUT2_A_S, CUT2_A_E)):
    for ang_d in (a_s, a_e):
        a = math.radians(ang_d)
        x_in  = ccx + R_OBI * math.cos(a)
        y_in  = ccy - R_OBI * math.sin(a)
        x_out = ccx + R_BO * math.cos(a)
        y_out = ccy - R_BO * math.sin(a)
        pdf.line(x_in, y_in, x_out, y_out)

# ---- PCD reference arcs (dashed) for inner and outer hole rings ----
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(ccx, ccy, INNER_HOLE_R, style="D")
pdf.circle(ccx, ccy, OUTER_HOLE_R, style="D")
pdf.set_dash_pattern()
_w(GEOM_W)

# ---- 16 × M3 holes with dashed Φ7 CB (CB is on bottom face = hidden) ----
def draw_hole(cx, cy):
    # M3 through-hole — solid Φ3.2
    pdf.circle(cx, cy, M3_DIAM/2, style="D")
    # CB dashed (hidden from top)
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    pdf.circle(cx, cy, CB_DIAM/2, style="D")
    pdf.set_dash_pattern()
    # tiny crosshair
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(cx-4.5, cy, cx+4.5, cy)
    pdf.line(cx, cy-4.5, cx, cy+4.5)
    pdf.set_dash_pattern()
    _w(GEOM_W)

for hole_R in (INNER_HOLE_R, OUTER_HOLE_R):
    for k in range(N_HOLES):
        ang_d = k * 360.0 / N_HOLES + HOLE_ROTATION
        a = math.radians(ang_d)
        cx = ccx + hole_R * math.cos(a)
        cy = ccy - hole_R * math.sin(a)
        draw_hole(cx, cy)

# Center cross (axis lines) — dashed
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(tv(-R_BO - 8, 0)[0], tv(-R_BO - 8, 0)[1],
         tv( R_BO + 8, 0)[0], tv( R_BO + 8, 0)[1])
pdf.line(tv(0, -R_BO - 8)[0], tv(0, -R_BO - 8)[1],
         tv(0,  R_BO + 8)[0], tv(0,  R_BO + 8)[1])
pdf.set_dash_pattern()

# ---- Angular annotations for the two boss cutouts ----
# Cutout 1: 0°-10°  -- arrows at 0° and 10°
# Cutout 2: 40°-50° -- arrows at 40° and 50°
_w(DIM_W)
for ang_d in (CUT1_A_S, CUT1_A_E, CUT2_A_S, CUT2_A_E):
    a = math.radians(ang_d)
    rd_x = ccx + (R_BO + 6) * math.cos(a)
    rd_y = ccy - (R_BO + 6) * math.sin(a)
    pdf.line(ccx + R_BO * math.cos(a), ccy - R_BO * math.sin(a), rd_x, rd_y)
    arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
    lx = ccx + (R_BO + 14) * math.cos(a)
    ly = ccy - (R_BO + 14) * math.sin(a)
    # offset label vertical for the 0° point so it stays clear of horizontal axis
    if abs(ang_d) < 1e-3:
        ly += 6
    text(lx, ly + 1.2, f"{ang_d:g}°", size=TXT_D, anchor="middle")

# ---- Top-view diameter dimensions (stacked above the disc) ----
# Φ170 (OD)
hdim(tv(-R_BO, 0)[0], tv(R_BO, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O1, f"Φ{BASE_OD:g}")
# Φ165 (boss ID)
hdim(tv(-R_OBI, 0)[0], tv(R_OBI, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O2, f"Φ{BOSS_ID:g}")
# Φ65 (base ID) on bottom
hdim(tv(-R_BI, 0)[0], tv(R_BI, 0)[0],
     tv(0, -R_BO)[1], tv(0, -R_BO)[1] + DIM_O1, f"Φ{BASE_ID:g}")

# ---- PCD annotations as leaders ----
# Place callouts in the LEFT gutter (between page edge x=5 and top view's left
# edge at x=tv(-R_BO,0)[0]=35). Text reads left-to-right but anchored "start"
# at x>=8 so we don't hit page margin.
_w(EXT_W)

# Inner PCD leader from 135° inner hole — exits up-left to upper-left gutter
ih_a = math.radians(135)
ih_x = ccx + INNER_HOLE_R * math.cos(ih_a)
ih_y = ccy - INNER_HOLE_R * math.sin(ih_a)
ih_lx, ih_ly = tv(-65, 50)
pdf.line(ih_x, ih_y, ih_lx, ih_ly)
pdf.line(ih_lx, ih_ly, ih_lx - 50, ih_ly)
text(ih_lx - 50 + 1, ih_ly - 1.2,
     f"8 × 内圈 PCD Φ{INNER_PCD:g}",
     size=TXT_D, anchor="start")

# Outer PCD leader from 135° outer hole — slightly below the inner PCD label
oh_a = math.radians(135)
oh_x = ccx + OUTER_HOLE_R * math.cos(oh_a)
oh_y = ccy - OUTER_HOLE_R * math.sin(oh_a)
oh_lx, oh_ly = tv(-90, 30)
pdf.line(oh_x, oh_y, oh_lx, oh_ly)
pdf.line(oh_lx, oh_ly, oh_lx - 25, oh_ly)
text(oh_lx - 25 + 1, oh_ly - 1.2,
     f"8 × 外圈 PCD Φ{OUTER_PCD:g}",
     size=TXT_D, anchor="start")

# Hole spec callout — leader from 225° outer hole, exits down-left into the
# left gutter beneath the disc.
hc_a = math.radians(225)
hc_x = ccx + OUTER_HOLE_R * math.cos(hc_a)
hc_y = ccy - OUTER_HOLE_R * math.sin(hc_a)
hc_lx, hc_ly = tv(-75, -78)
pdf.line(hc_x, hc_y, hc_lx, hc_ly)
pdf.line(hc_lx, hc_ly, hc_lx - 30, hc_ly)
text(hc_lx - 30 + 1, hc_ly - 1.2,
     f"16 × Φ{M3_DIAM:g} 通孔 + Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 (底面)",
     size=TXT_D, anchor="start")

# Boss-cutout group callout — leader from cutout 1 midpoint (~5°), to the
# right-of-disc area, sitting BELOW the section view's upper boundary.
cm_a = math.radians((CUT1_A_S + CUT1_A_E) / 2)
cm_x = ccx + (R_BO - 4) * math.cos(cm_a)
cm_y = ccy - (R_BO - 4) * math.sin(cm_a)
cm_lx, cm_ly = tv(110, -78)
pdf.line(cm_x, cm_y, cm_lx, cm_ly)
pdf.line(cm_lx, cm_ly, cm_lx + 8, cm_ly)
text(cm_lx + 8 + 1, cm_ly - 1.2,
     f"凸圈缺口 {CUT1_A_S:g}°–{CUT1_A_E:g}° / {CUT2_A_S:g}°–{CUT2_A_E:g}° (仅去除凸圈)",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
# Layout: page is 420 wide. Section center at 295. Right edge of dim chain at
# 295+85+26=406 (14mm margin). Section's leftmost vdim extension is at
# 295-85-14=196. Top view's rightmost cutout-angle leader/arrow tip is at
# tv(R_BO+6,0)[0] = 211, and the angle label at tv(R_BO+14,0)[0] = 219 — so
# there's no real overlap with section view (left edge 210), just visual
# proximity. The angle label "0°" sits at x=219, the section view starts
# geometrically at x=210, so the section view's outer rim line (x=210) is
# clear of the top view's cutout label (x=219 with text width ~6 going +/- 3).
sa_t_zero_x = 295
sa_z_zero_y = 175
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 50, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 57,
     "(沿 +Y 方向剖切, 过 90° 孔 / cut along +Y, through 90° holes)",
     size=TXT_I, anchor="middle")

_w(GEOM_W)

# Section conventions:
#   t-axis = the radial direction in the cut plane (here = Y axis)
#   z-axis = vertical (up)
# Rim boss is intact on BOTH sides (90° is away from the 0°-10° and 40°-50° cutouts).
# Each side has one M3+CB hole at t = ±INNER_HOLE_R and t = ±OUTER_HOLE_R.

# Helper: profile of one M3+CB stepped hole at t = t0 (drawn as the section
# "void" through the base; rim boss does NOT cover the hole since hole stays
# inside R_OBI radially: 36.25 < 82.5 and 77.5 < 82.5).
def draw_hole_profile(t0):
    # CB sits at Z=0..CB_DEPTH, half-width CB_DIAM/2
    # M3 sits at Z=CB_DEPTH..BASE_T, half-width M3_DIAM/2
    hcb = CB_DIAM / 2
    hm3 = M3_DIAM / 2
    # Left CB wall + step + M3 wall
    line(*sa(t0 - hcb, 0),         *sa(t0 - hcb, CB_DEPTH), GEOM_W)
    line(*sa(t0 - hcb, CB_DEPTH),  *sa(t0 - hm3, CB_DEPTH), GEOM_W)
    line(*sa(t0 - hm3, CB_DEPTH),  *sa(t0 - hm3, BASE_T),   GEOM_W)
    # Right side
    line(*sa(t0 + hcb, 0),         *sa(t0 + hcb, CB_DEPTH), GEOM_W)
    line(*sa(t0 + hcb, CB_DEPTH),  *sa(t0 + hm3, CB_DEPTH), GEOM_W)
    line(*sa(t0 + hm3, CB_DEPTH),  *sa(t0 + hm3, BASE_T),   GEOM_W)
    # tiny centerline (dashed)
    pdf.set_dash_pattern(dash=2, gap=1); _w(0.12)
    pdf.line(*sa(t0, -2), *sa(t0, BASE_T + 2))
    pdf.set_dash_pattern()
    _w(GEOM_W)

# Hole locations on section (t = ±INNER_HOLE_R, ±OUTER_HOLE_R)
hole_t = sorted([-OUTER_HOLE_R, -INNER_HOLE_R, INNER_HOLE_R, OUTER_HOLE_R])

# --- Base bottom (z=0): a single continuous segment from -R_BO to +R_BO,
# BUT broken by the CB openings of the 4 holes. ---
# Build a list of "gap" intervals on z=0
gaps_bot = []
for t0 in hole_t:
    gaps_bot.append((t0 - CB_DIAM/2, t0 + CB_DIAM/2))
gaps_bot.sort()

t_prev = -R_BO
for gl, gr in gaps_bot:
    if gl > t_prev:
        line(*sa(t_prev, 0), *sa(gl, 0), GEOM_W)
    t_prev = max(t_prev, gr)
if R_BO > t_prev:
    line(*sa(t_prev, 0), *sa(R_BO, 0), GEOM_W)

# Inner-bore opening: the base also has a Φ65 hole through it.
# We draw the base bottom as broken between -R_BI and R_BI (inner bore).
# Wait — the bottom-edge list above doesn't account for the inner bore. Redo
# bottom with both inner bore AND CB gaps.
# (Redo by overdrawing: erase the bottom line we drew across the inner bore.)
pdf.set_draw_color(255, 255, 255); _w(GEOM_W + 0.4)
pdf.line(*sa(-R_BI, 0), *sa(R_BI, 0))
pdf.set_draw_color(0, 0, 0); _w(GEOM_W)
# Now redraw bottom as two pieces: outer rim to first CB, etc. but skipping
# inside the inner bore. The CB gaps already cover the holes; we now need the
# inner bore (R_BI) wall to be drawn as vertical walls on both sides at z=0..BASE_T,
# and the base TOP at z=BASE_T to NOT span the inner bore.

# Inner bore vertical walls of base at t = ±R_BI from z=0 up to z=BASE_T
line(*sa(-R_BI, 0), *sa(-R_BI, BASE_T), GEOM_W)
line(*sa( R_BI, 0), *sa( R_BI, BASE_T), GEOM_W)

# Outer rim of base at t = ±R_BO from z=0 up to z=TOTAL_H (boss sits on top)
line(*sa(-R_BO, 0), *sa(-R_BO, TOTAL_H), GEOM_W)
line(*sa( R_BO, 0), *sa( R_BO, TOTAL_H), GEOM_W)

# Base TOP (z=BASE_T): broken by inner bore AND by M3 openings of the 4 holes.
gaps_top = [(-R_BI, R_BI)]
for t0 in hole_t:
    gaps_top.append((t0 - M3_DIAM/2, t0 + M3_DIAM/2))
gaps_top.sort()

t_prev = -R_BO
for gl, gr in gaps_top:
    if gl > t_prev:
        line(*sa(t_prev, BASE_T), *sa(gl, BASE_T), GEOM_W)
    t_prev = max(t_prev, gr)
if R_BO > t_prev:
    line(*sa(t_prev, BASE_T), *sa(R_BO, BASE_T), GEOM_W)

# Rim boss section: at t = ±R_OBI (inner wall) and ±R_BO (outer wall).
# Outer wall already drawn (z=0..TOTAL_H, the base outer rim is integral with
# the rim boss outer wall).
# Inner wall of rim boss
line(*sa(-R_OBI, BASE_T), *sa(-R_OBI, TOTAL_H), GEOM_W)
line(*sa( R_OBI, BASE_T), *sa( R_OBI, TOTAL_H), GEOM_W)
# Top of rim boss (z = TOTAL_H)
line(*sa(-R_BO,  TOTAL_H), *sa(-R_OBI, TOTAL_H), GEOM_W)
line(*sa( R_OBI, TOTAL_H), *sa( R_BO,  TOTAL_H), GEOM_W)

# Draw the four stepped hole profiles
for t0 in hole_t:
    draw_hole_profile(t0)

# ----- Section A-A dimensions -----
# RIGHT side stays clean (close to page edge). Put the BASE_T + BOSS_H + TOTAL_H
# vertical chain on the RIGHT, but use only DIM_O1 and DIM_O2 for the two
# component dims and skip the redundant TOTAL_H (already inferable). Add
# TOTAL_H as a single chain on the LEFT side at DIM_O1 since boss-wall hdim
# uses DIM_O2 there.
right_x1 = sa(R_BO, 0)[0] + DIM_O1
right_x2 = sa(R_BO, 0)[0] + DIM_O2
vdim(sa(0, BASE_T)[1], sa(0, 0)[1],
     sa(R_BO, 0)[0], right_x1, f"{BASE_T:g}")
vdim(sa(0, TOTAL_H)[1], sa(0, BASE_T)[1],
     sa(R_BO, 0)[0], right_x2, f"{BOSS_H:g}")

# LEFT side: total height (BASE_T + BOSS_H = 10) on the closest offset.
left_x1 = sa(-R_BO, 0)[0] - DIM_O1
vdim(sa(0, TOTAL_H)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_x1, f"{TOTAL_H:g}")
# Boss wall thickness — dim BELOW the base (between base bottom and bottom
# dim line for the inner bore). Placed on the LEFT side under the boss only.
hdim(sa(-R_BO, 0)[0], sa(-R_OBI, 0)[0],
     sa(0, 0)[1], sa(0, 0)[1] + DIM_O1,
     f"{(BOSS_OD-BOSS_ID)/2:g}")

# Top horizontal dims, stacked from closest to furthest:
# Φ65 (inner bore) at DIM_O1 — short span
hdim(sa(-R_BI, 0)[0], sa(R_BI, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - DIM_O1, f"Φ{BASE_ID:g}")
# PCD Φ72.5 (inner) at DIM_O2
hdim(sa(-INNER_HOLE_R, 0)[0], sa(INNER_HOLE_R, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - DIM_O2, f"PCD Φ{INNER_PCD:g}")
# PCD Φ155 (outer) at DIM_O3
hdim(sa(-OUTER_HOLE_R, 0)[0], sa(OUTER_HOLE_R, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - DIM_O3, f"PCD Φ{OUTER_PCD:g}")
# Φ165 (boss ID) further still
hdim(sa(-R_OBI, 0)[0], sa(R_OBI, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - (DIM_O3 + 12),
     f"Φ{BOSS_ID:g}")
# Φ170 (base/boss OD) furthest
hdim(sa(-R_BO, 0)[0], sa(R_BO, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - (DIM_O3 + 24),
     f"Φ{BASE_OD:g}")

# ===== DETAIL B (3:1) — M3 + Φ7 CB stepped hole stack =====
DB_SCALE = 3.0
db_cx, db_cy = sa_t_zero_x, 248
DB_DIM_O = 12.0
def db(t, z): return (db_cx + t * DB_SCALE, db_cy - z * DB_SCALE)

text(db_cx, db_cy - BASE_T * DB_SCALE - DB_DIM_O - 6,
     "详图 B  Detail B  (3:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

DB_HALF_BASE = 8.0           # 16mm wide base context
DB_HALF_CB   = CB_DIAM / 2   # 3.5
DB_HALF_M3   = M3_DIAM / 2   # 1.6

_w(GEOM_W)
# Bottom edge with CB gap
line(*db(-DB_HALF_BASE, 0),       *db(-DB_HALF_CB, 0),       GEOM_W)
line(*db( DB_HALF_CB,   0),       *db( DB_HALF_BASE, 0),     GEOM_W)
# CB walls
line(*db(-DB_HALF_CB, 0),         *db(-DB_HALF_CB, CB_DEPTH),GEOM_W)
line(*db( DB_HALF_CB, 0),         *db( DB_HALF_CB, CB_DEPTH),GEOM_W)
# CB shoulder
line(*db(-DB_HALF_CB, CB_DEPTH),  *db(-DB_HALF_M3, CB_DEPTH),GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH),  *db( DB_HALF_CB, CB_DEPTH),GEOM_W)
# M3 walls
line(*db(-DB_HALF_M3, CB_DEPTH),  *db(-DB_HALF_M3, BASE_T), GEOM_W)
line(*db( DB_HALF_M3, CB_DEPTH),  *db( DB_HALF_M3, BASE_T), GEOM_W)
# Top edge with M3 gap
line(*db(-DB_HALF_BASE, BASE_T), *db(-DB_HALF_M3, BASE_T), GEOM_W)
line(*db( DB_HALF_M3,   BASE_T), *db( DB_HALF_BASE, BASE_T), GEOM_W)
# Outer edges
line(*db(-DB_HALF_BASE, 0), *db(-DB_HALF_BASE, BASE_T), GEOM_W)
line(*db( DB_HALF_BASE, 0), *db( DB_HALF_BASE, BASE_T), GEOM_W)

# Centerline
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(db(0, -2)[0], db(0, -2)[1], db(0, BASE_T + 2)[0], db(0, BASE_T + 2)[1])
pdf.set_dash_pattern()
_w(GEOM_W)

# Detail dims
vdim(db(0, BASE_T)[1], db(0, 0)[1],
     db(DB_HALF_BASE, 0)[0], db(DB_HALF_BASE, 0)[0] + DB_DIM_O,
     f"{BASE_T:g}")
vdim(db(0, CB_DEPTH)[1], db(0, 0)[1],
     db(-DB_HALF_BASE, 0)[0], db(-DB_HALF_BASE, 0)[0] - DB_DIM_O,
     f"{CB_DEPTH:g}")
hdim(db(-DB_HALF_CB, 0)[0], db(DB_HALF_CB, 0)[0],
     db(0, 0)[1], db(0, 0)[1] + DB_DIM_O,
     f"Φ{CB_DIAM:g}")
hdim(db(-DB_HALF_M3, 0)[0], db(DB_HALF_M3, 0)[0],
     db(0, BASE_T)[1], db(0, BASE_T)[1] - DB_DIM_O,
     f"Φ{M3_DIAM:g}")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 安装法兰 (Mounting Flange)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖) / 3:1 (详 B)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_OD:g}/Φ{BASE_ID:g}×{BASE_T:g} 基环 / 凸圈 Φ{BOSS_OD:g}/Φ{BOSS_ID:g}×{BOSS_H:g} / "
     f"16×Φ{M3_DIAM:g} + Φ{CB_DIAM:g}×{CB_DEPTH:g} 沉孔 / "
     f"凸圈缺口 {CUT1_A_S:g}°–{CUT1_A_E:g}°, {CUT2_A_S:g}°–{CUT2_A_E:g}°  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-04  /  POV3D / models / mounting_flange / mounting_flange.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("mounting_flange_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
