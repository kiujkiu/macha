"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D ring collar.

Two views:
  1) TOP VIEW   (俯视图, 1:1)     — ring viewed from above (notch hidden, shown
                                    as dashed radial lines + angle dims)
  2) SECTION A-A (剖视图 A-A, 1:1) — cut along the 15° direction (notch
                                    bisector), showing the notch profile
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
OD      = 80.0
ID      = 65.0
HEIGHT  = 13.0
NOTCH_A_S = 0.0
NOTCH_A_E = 30.0
NOTCH_H = 6.0

R_O = OD / 2     # 40
R_I = ID / 2     # 32.5
WALL = R_O - R_I # 7.5

NOTCH_BISECTOR = (NOTCH_A_S + NOTCH_A_E) / 2   # 15° → cut direction

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

# Style (matching workflow standard)
GEOM_W = 0.60
DIM_W  = 0.28
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
    """Append the unit to numeric labels. Skip if label already has it,
    contains a degree mark, or is an angle/special tag."""
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
        arrow(x_l, yd,  1, 0)   # tip at left end, pointing into gap (right)
        arrow(x_r, yd, -1, 0)   # tip at right end, pointing into gap (left)
    text((x_l + x_r) / 2, yd - 1.8, label, anchor="middle")

def vdim(y1, y2, xg, xd, label):
    """Vertical dim. Auto-switches to outside-arrows when the gap is too narrow."""
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
    # Label rotated: if it fits in gap, center it; else park beside the top arrow.
    label_h_rot = pdf.get_string_width(label)   # rotated label height = string width
    if gap >= label_h_rot + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        # Place label just below the bottom arrow tail (rotated, reading bottom-to-top)
        y_label = y_bot + (ARR_L + 1.0) + label_h_rot / 2 + 1.0
        rot_text(xd + to, y_label, label, angle_deg=90, anchor="middle")

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D 环形件  Ring Collar", size=TXT_T, anchor="middle")
text(PAGE_W/2, 21,
     f"Φ{OD:g} / Φ{ID:g} / 高 {HEIGHT:g}  /  槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° H{NOTCH_H:g} (距底面 0–{NOTCH_H:g})",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 140, 145    # PDF center of ring in top view
def tv(x, y): return (tv_cx + x, tv_cy - y)   # invert Y

text(tv_cx, 38, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A cutting line: along 15° (notch bisector)
cut_a = math.radians(NOTCH_BISECTOR)
line_len = R_O + 18
end1 = tv( line_len * math.cos(cut_a), line_len * math.sin(cut_a))
end2 = tv(-line_len * math.cos(cut_a), -line_len * math.sin(cut_a))
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
# A markers near the line ends
text(end1[0] + 3, end1[1] - 2, "A", size=6)
text(end2[0] - 7, end2[1] + 4, "A", size=6)

# Ring outline: outer Φ80 and inner Φ65
_w(GEOM_W)
ccx, ccy = tv(0, 0)
pdf.circle(ccx, ccy, R_O, style="D")
pdf.circle(ccx, ccy, R_I, style="D")

# Center cross (axis lines)
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(tv(-R_O - 6, 0)[0], tv(-R_O - 6, 0)[1], tv(R_O + 6, 0)[0], tv(R_O + 6, 0)[1])
pdf.line(tv(0, -R_O - 6)[0], tv(0, -R_O - 6)[1], tv(0, R_O + 6)[0], tv(0, R_O + 6)[1])
pdf.set_dash_pattern()

# Notch: hidden from above. Show radial dashed lines at 0° and 30° in the wall.
pdf.set_dash_pattern(dash=2.0, gap=1.0); _w(HID_W)
for ang_d in (NOTCH_A_S, NOTCH_A_E):
    a = math.radians(ang_d)
    x_in  = ccx + R_I * math.cos(a)
    y_in  = ccy - R_I * math.sin(a)
    x_out = ccx + R_O * math.cos(a)
    y_out = ccy - R_O * math.sin(a)
    pdf.line(x_in, y_in, x_out, y_out)
pdf.set_dash_pattern()

# Notch angle arc indicator (within the wall)
_w(DIM_W)
ang_r = (R_O + R_I) / 2
arc_n = 12
arc_pts = []
for i in range(arc_n + 1):
    t = i / arc_n
    a = math.radians(NOTCH_A_S + t * (NOTCH_A_E - NOTCH_A_S))
    arc_pts.append((ccx + ang_r * math.cos(a), ccy - ang_r * math.sin(a)))
for i in range(len(arc_pts) - 1):
    pdf.line(*arc_pts[i], *arc_pts[i+1])

# Radial lines from center at notch ends, with angle labels outside ring
for ang_d in (NOTCH_A_S, NOTCH_A_E):
    a = math.radians(ang_d)
    rd_x = ccx + (R_O + 10) * math.cos(a)
    rd_y = ccy - (R_O + 10) * math.sin(a)
    pdf.line(ccx, ccy, rd_x, rd_y)
    arrow(rd_x, rd_y, math.cos(a), -math.sin(a))
    # label slightly beyond arrow
    lx = ccx + (R_O + 16) * math.cos(a)
    ly = ccy - (R_O + 16) * math.sin(a)
    text(lx, ly, f"{ang_d:g}°", size=TXT_D, anchor="middle")

# --- Top view dimensions ---
# Φ80 horizontal across (top of view)
hdim(tv(-R_O, 0)[0], tv(R_O, 0)[0],
     tv(0, R_O)[1], tv(0, R_O)[1] - DIM_O1, f"Φ{OD:g}")
# Φ65 horizontal across, stacked further out
hdim(tv(-R_I, 0)[0], tv(R_I, 0)[0],
     tv(0, R_O)[1], tv(0, R_O)[1] - DIM_O2, f"Φ{ID:g}")
# Wall thickness 7.5 on the left
hdim(tv(-R_O, 0)[0], tv(-R_I, 0)[0],
     tv(0, -R_O)[1], tv(0, -R_O)[1] + DIM_O1, f"{WALL:g}")

# Notch callout (text annotation)
nx, ny = tv((R_O + 4) * math.cos(math.radians(NOTCH_BISECTOR)),
            (R_O + 4) * math.sin(math.radians(NOTCH_BISECTOR)))
lx, ly = tv(R_O + 28, R_O + 4)
_w(EXT_W)
pdf.line(nx, ny, lx, ly)
pdf.line(lx, ly, lx + 14, ly)
text(lx + 14, ly - 1, f"槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}°, 高 {NOTCH_H:g}", size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
sa_t_zero_x = 310
sa_z_zero_y = 200
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 70, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_t_zero_x, 78,
     f"(沿 {NOTCH_BISECTOR:g}° 方向剖切, 过槽口中分线 / cut along {NOTCH_BISECTOR:g}° through notch bisector)",
     size=TXT_I, anchor="middle")

# At 15° section, t axis along notch bisector. Positive t = inside the notch (0-30° range)
# Left wall (-t side): full rectangle z=0..HEIGHT, t=-R_O..-R_I
# Right wall (+t side): notch removes z=0..NOTCH_H, so wall is z=NOTCH_H..HEIGHT only

_w(GEOM_W)
# Left wall: full rectangle
pdf.rect(sa(-R_O, HEIGHT)[0], sa(-R_O, HEIGHT)[1], WALL, HEIGHT, style="D")

# Right wall: upper portion only (z=NOTCH_H..HEIGHT)
right_h = HEIGHT - NOTCH_H
pdf.rect(sa(R_I, HEIGHT)[0], sa(R_I, HEIGHT)[1], WALL, right_h, style="D")

# --- Section dimensions ---
# Total height (left side)
left_dim_x = sa(-R_O, 0)[0] - DIM_O1
vdim(sa(0, HEIGHT)[1], sa(0, 0)[1],
     sa(-R_O, 0)[0], left_dim_x, f"{HEIGHT:g}")
# Notch height (right side, outside right wall)
right_dim_x = sa(R_O, 0)[0] + DIM_O1
vdim(sa(0, NOTCH_H)[1], sa(0, 0)[1],
     sa(R_O, 0)[0], right_dim_x, f"{NOTCH_H:g}")
# Right wall remaining height (stacked further out)
right_dim_x2 = sa(R_O, 0)[0] + DIM_O2
vdim(sa(0, HEIGHT)[1], sa(0, NOTCH_H)[1],
     sa(R_O, 0)[0], right_dim_x2, f"{right_h:g}")

# Φ80 across top
top_dim_y1 = sa(0, HEIGHT)[1] - DIM_O1
hdim(sa(-R_O, 0)[0], sa(R_O, 0)[0],
     sa(0, HEIGHT)[1], top_dim_y1, f"Φ{OD:g}")
# Φ65 across (stacked further out)
top_dim_y2 = sa(0, HEIGHT)[1] - DIM_O2
hdim(sa(-R_I, 0)[0], sa(R_I, 0)[0],
     sa(0, HEIGHT)[1], top_dim_y2, f"Φ{ID:g}")

# Wall thickness 7.5 on the left wall (bottom dim)
bottom_dim_y = sa(0, 0)[1] + DIM_O1
hdim(sa(-R_O, 0)[0], sa(-R_I, 0)[0],
     sa(0, 0)[1], bottom_dim_y, f"{WALL:g}")
# Wall thickness 7.5 on the right wall (bottom dim, same level)
hdim(sa(R_I, 0)[0], sa(R_O, 0)[0],
     sa(0, 0)[1], bottom_dim_y, f"{WALL:g}")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — 环形件 (Ring Collar)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{OD:g} (外) / Φ{ID:g} (内) / 高 {HEIGHT:g} / 壁厚 {WALL:g} / 槽口 {NOTCH_A_S:g}°–{NOTCH_A_E:g}° H{NOTCH_H:g}  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-05  /  POV3D / models / ring_collar / ring_collar.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("ring_collar_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
