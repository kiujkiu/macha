"""
A3 landscape 2D engineering drawing for POV3D rim_top_disc.

Two views:
  1) TOP VIEW (1:1)   — looking from +Z down. Disc Φ170 + 16 M3 holes
                         (mirroring rim_ring) + 2 radial reinforcement ribs
                         at Y = ±47.5 with 95 mm c-to-c spacing.
  2) FRONT VIEW (1:1) — looking from +Y. Disc cross-section (170 × 5)
                         + 2 ribs (5 × 30) standing up, + the 2 horizontal
                         M3 through-holes that mate with l_bracket_170x60's
                         gusset holes.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (mirror build_stl.py) =====
DISC_OD = 200.0
DISC_THICK = 5.0
M3_DIAM = 3.2
INNER_PCD_R = 35.0
OUTER_PCD_R = 77.5
HOLE_ANGLES_DEG = [22.5 + k * 45.0 for k in range(8)]

RIB_THICK = 5.0
RIB_HEIGHT = 30.0
RIB_CC = 95.0
RIB_HALF_OUT = RIB_CC/2 + RIB_THICK/2
RIB_HALF_LEN = math.sqrt((DISC_OD/2)**2 - RIB_HALF_OUT**2) - 0.5
RIB_LENGTH = 2 * RIB_HALF_LEN
RIB_Y_CENTERS = (+RIB_CC/2, -RIB_CC/2)

RIB_HOLE_DIAM = 3.2
RIB_HOLE_X = (-34.3, -64.3)
RIB_HOLE_Z = DISC_THICK + 19.0     # 24 in disc build frame

# 6 special M3 + Φ4.2 CB
SPECIAL_M3_DIAM  = 3.2
SPECIAL_CB_DIAM  = 4.2
SPECIAL_CB_DEPTH = 3.0
SPECIAL_POSITIONS = [
    ( 5.0,  37.5), ( 5.0, -37.5),
    (51.0,  37.5), (51.0, -37.5),
    (60.0,  22.0), (60.0, -22.0),
]

# Rectangular slot on +Y rib (15 × 6 mm; slot bottom at disc-frame Z=19)
SLOT_WIDTH    = 15.0
SLOT_HEIGHT   = 6.0
SLOT_X_CENTER = 35.0                   # was 16
SLOT_BOTTOM_Z = DISC_THICK + 11.0      # was DISC_THICK+14; now 16
SLOT_RIB_Y    = +RIB_CC/2               # +47.5

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
_font_paths = ["/mnt/c/Windows/Fonts/simhei.ttf"]
_font = next((f for f in _font_paths if os.path.exists(f)), None)
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
TXT_D  = 5.0
TXT_L  = 8.0
TXT_T  = 9.5
TXT_I  = 5.0
DIM_O1 = 12.0
DIM_O2 = 22.0
DIM_O3 = 32.0

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
        arrow(x_l, yd, 1, 0); arrow(x_r, yd, -1, 0)
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
        arrow(xd, y_top, 0, 1); arrow(xd, y_bot, 0, -1)
    label_h_rot = pdf.get_string_width(label)
    if gap >= label_h_rot + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        y_label = y_bot + (ARR_L + 1.0) + label_h_rot / 2 + 1.0
        rot_text(xd + to, y_label, label, angle_deg=90, anchor="middle")

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, f"POV 3D rim_top_disc  (Φ{DISC_OD:g} × {DISC_THICK:g},2 × 加强筋 + 16 × M3 + 2 × 肋孔)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"Φ{DISC_OD:g} 圆盘,厚 {DISC_THICK:g} / "
     f"16 × Φ{M3_DIAM:g} M3 (PCD Φ{2*INNER_PCD_R:g} ×8 + PCD Φ{2*OUTER_PCD_R:g} ×8,起 22.5°,45° 等分) / "
     f"2 × 径向肋 {RIB_THICK:g} × {RIB_HEIGHT:g} (中心 Y=±{RIB_CC/2:g},c-to-c {RIB_CC:g}) / "
     f"2 × Φ{RIB_HOLE_DIAM:g} 肋孔 (沿 Y 贯通,X=-34.3 / -64.3,Z={RIB_HOLE_Z:g}) / "
     f"6 × [Φ{SPECIAL_M3_DIAM:g} M3 通孔 + Φ{SPECIAL_CB_DIAM:g} × {SPECIAL_CB_DEPTH:g} 沉孔(底→顶)]  "
     f"(GB 第一角投影)",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) — looking from +Z down. PDF x = world X, PDF y = -world Y =====
tv_cx, tv_cy = 130, 130    # disc center in PDF mm
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 32, "俯视图  Top View  (1:1)   尺寸单位: mm  (沿 -Z 看)",
     size=TXT_L, anchor="middle")

# Disc outer circle
_w(GEOM_W)
pdf.circle(tv_cx, tv_cy, DISC_OD/2, style="D")

# PCD circles (light dashed reference)
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(tv_cx, tv_cy, INNER_PCD_R, style="D")
pdf.circle(tv_cx, tv_cy, OUTER_PCD_R, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# Center crosshair
pdf.set_dash_pattern(dash=4.0, gap=1.5, phase=2.0); _w(0.18)
pdf.line(tv_cx - DISC_OD/2 - 5, tv_cy, tv_cx + DISC_OD/2 + 5, tv_cy)
pdf.line(tv_cx, tv_cy - DISC_OD/2 - 5, tv_cx, tv_cy + DISC_OD/2 + 5)
pdf.set_dash_pattern(); _w(GEOM_W)

# 16 M3 holes
for R in (INNER_PCD_R, OUTER_PCD_R):
    for a in HOLE_ANGLES_DEG:
        cx = R * math.cos(math.radians(a))
        cy = R * math.sin(math.radians(a))
        pcx, pcy = tv(cx, cy)
        pdf.circle(pcx, pcy, M3_DIAM/2, style="D")
        pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
        pdf.line(pcx - 3, pcy, pcx + 3, pcy)
        pdf.line(pcx, pcy - 3, pcx, pcy + 3)
        pdf.set_dash_pattern(); _w(GEOM_W)

# 6 special M3 + Φ4.2 CB holes (CB on bottom face = dashed circle from top view)
for (hx, hy) in SPECIAL_POSITIONS:
    pcx, pcy = tv(hx, hy)
    # CB outline (hidden, dashed)
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    pdf.circle(pcx, pcy, SPECIAL_CB_DIAM/2, style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    # M3 through-hole (visible)
    pdf.circle(pcx, pcy, SPECIAL_M3_DIAM/2, style="D")
    # crosshair
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(pcx - 3.5, pcy, pcx + 3.5, pcy)
    pdf.line(pcx, pcy - 3.5, pcx, pcy + 3.5)
    pdf.set_dash_pattern(); _w(GEOM_W)

# 2 ribs — outlines (visible from above)
_w(GEOM_W)
for ry in RIB_Y_CENTERS:
    rx0 = tv(-RIB_LENGTH/2, ry + RIB_THICK/2)[0]
    ry0 = tv(-RIB_LENGTH/2, ry + RIB_THICK/2)[1]
    pdf.rect(rx0, ry0, RIB_LENGTH, RIB_THICK, style="D")

# Slot on the +Y rib — hidden in top view (cutout passes through rib's Y),
# shown as a dashed rectangle within the rib outline.
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
sx0 = tv(SLOT_X_CENTER - SLOT_WIDTH/2, SLOT_RIB_Y + RIB_THICK/2)[0]
sy0 = tv(SLOT_X_CENTER - SLOT_WIDTH/2, SLOT_RIB_Y + RIB_THICK/2)[1]
pdf.rect(sx0, sy0, SLOT_WIDTH, RIB_THICK, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# 2 rib through-holes (along Y) — show as dashed lines spanning the two ribs
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
for hx in RIB_HOLE_X:
    p1 = tv(hx, +(RIB_CC/2 + RIB_THICK/2 + 1))
    p2 = tv(hx, -(RIB_CC/2 + RIB_THICK/2 + 1))
    pdf.line(p1[0], p1[1], p2[0], p2[1])
    # mark hole centers in each rib with small circles
    for ry in RIB_Y_CENTERS:
        pcx, pcy = tv(hx, ry)
        _w(0.25); pdf.set_dash_pattern()
        pdf.circle(pcx, pcy, RIB_HOLE_DIAM/2, style="D")
        pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
pdf.set_dash_pattern(); _w(GEOM_W)

# Bracket footprint reference (light dotted)
pdf.set_dash_pattern(dash=1.5, gap=2.5); _w(0.15)
HLEG_DIST = 14.3
BRACKET_VLEG_RADIAL = 70.0
BRACKET_WIDTH = 90.0
bx0, by0 = tv(-HLEG_DIST - BRACKET_VLEG_RADIAL, +BRACKET_WIDTH/2)
pdf.rect(bx0, by0, BRACKET_VLEG_RADIAL, BRACKET_WIDTH, style="D")
text(tv(-HLEG_DIST - BRACKET_VLEG_RADIAL/2, BRACKET_WIDTH/2 + 8)[0],
     tv(-HLEG_DIST - BRACKET_VLEG_RADIAL/2, BRACKET_WIDTH/2 + 8)[1],
     "立板贴此处 (l_bracket_170x60 70×90)", size=TXT_I, anchor="middle")
pdf.set_dash_pattern(); _w(GEOM_W)

# Top-view dims
hdim(tv(-DISC_OD/2, -DISC_OD/2)[0], tv(DISC_OD/2, -DISC_OD/2)[0],
     tv(0, -DISC_OD/2)[1], tv(0, -DISC_OD/2)[1] + DIM_O3,
     f"Φ{DISC_OD:g}")
vdim(tv(0, -RIB_CC/2)[1], tv(0, +RIB_CC/2)[1],
     tv(DISC_OD/2, 0)[0], tv(DISC_OD/2, 0)[0] + DIM_O1,
     f"{RIB_CC:g}")
# 4 rib hole X-position dim, below the ribs
hdim(tv(RIB_HOLE_X[1], 0)[0], tv(RIB_HOLE_X[0], 0)[0],
     tv(0, -RIB_CC/2 - RIB_THICK/2)[1] + 4,
     tv(0, -RIB_CC/2 - RIB_THICK/2)[1] + 4 + 0.01,   # dim line slightly below ribs
     f"{abs(RIB_HOLE_X[1] - RIB_HOLE_X[0]):g}")
# Each rib hole X from rim center
hdim(tv(0, 0)[0], tv(RIB_HOLE_X[0], 0)[0],
     tv(0, -RIB_CC/2 - 6)[1], tv(0, -RIB_CC/2 - 6)[1] + DIM_O1,
     f"{abs(RIB_HOLE_X[0]):g}")
hdim(tv(0, 0)[0], tv(RIB_HOLE_X[1], 0)[0],
     tv(0, -RIB_CC/2 - 6)[1], tv(0, -RIB_CC/2 - 6)[1] + DIM_O2,
     f"{abs(RIB_HOLE_X[1]):g}")

# PCD note
text(tv(0, +OUTER_PCD_R + 4)[0], tv(0, +OUTER_PCD_R + 4)[1],
     f"16 × Φ{M3_DIAM:g} 通孔 (M3) — 内圈 PCD Φ{2*INNER_PCD_R:g} × 8,外圈 PCD Φ{2*OUTER_PCD_R:g} × 8,起 22.5° / 45° 等分",
     size=TXT_I, anchor="middle")

# Dims for the 6 special holes (placed above the top view, in +X +Y region)
# Vertical (Y) dims on the right of the +X column
vdim(tv(0, 37.5)[1], tv(0, 0)[1], tv(60, 0)[0] + 8, tv(60, 0)[0] + 8 + DIM_O1,
     "37.5")
vdim(tv(0, 22)[1], tv(0, 0)[1], tv(60, 0)[0] + 8, tv(60, 0)[0] + 8 + DIM_O2,
     "22")
# Horizontal (X) dims below the +X column, stacked
hdim(tv(0, 0)[0], tv(5, 0)[0],  tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O1, "5")
hdim(tv(0, 0)[0], tv(51, 0)[0], tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O2, "51")
hdim(tv(0, 0)[0], tv(60, 0)[0], tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O3, "60")
# Note labeling the 6-hole pattern
text(tv(60, 37.5 + 6)[0], tv(60, 37.5 + 6)[1],
     f"6 × Φ{SPECIAL_M3_DIAM:g} 通孔 + Φ{SPECIAL_CB_DIAM:g} × {SPECIAL_CB_DEPTH:g} 沉孔 (虚线圆,底面)",
     size=TXT_I, anchor="middle")

# ===== FRONT VIEW (1:1) — looking from +Y =====
# Show disc cross-section (170 wide × 5 tall) + 2 ribs on top (5 × 30)
# + 2 rib through-holes (visible as circles since the holes are along Y)
fv_cx = 320      # disc center in PDF X
fv_z0 = 215      # disc top edge (Z=DISC_THICK level) in PDF Y; disc bottom at fv_z0+DISC_THICK
def fv(x, z): return (fv_cx + x, fv_z0 + DISC_THICK - z)

text(fv_cx, 65, "前视图  Front View  (1:1)   尺寸单位: mm  (沿 +Y 看)",
     size=TXT_L, anchor="middle")

_w(GEOM_W)
# Disc rectangle (170 wide × 5 tall) — bottom-left corner at (-85, 0) in disc frame
disc_l = fv(-DISC_OD/2, DISC_THICK)[0]
disc_t = fv(-DISC_OD/2, DISC_THICK)[1]
pdf.rect(disc_l, disc_t, DISC_OD, DISC_THICK, style="D")

# 2 ribs on top (each at one Y center; in front view BOTH project to same outline)
# Show ONE outline since both project identically. Note: in projection there's
# really only one rectangle visible (the +Y rib in front of -Y rib).
rib_l = fv(-RIB_LENGTH/2, DISC_THICK + RIB_HEIGHT)[0]
rib_t = fv(-RIB_LENGTH/2, DISC_THICK + RIB_HEIGHT)[1]
pdf.rect(rib_l, rib_t, RIB_LENGTH, RIB_HEIGHT, style="D")

# 2 rib through-holes — appear as circles in this view (axis along Y, perpendicular to view)
_w(GEOM_W)
for hx in RIB_HOLE_X:
    pcx, pcy = fv(hx, RIB_HOLE_Z)
    pdf.circle(pcx, pcy, RIB_HOLE_DIAM/2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(pcx - 3, pcy, pcx + 3, pcy)
    pdf.line(pcx, pcy - 3, pcx, pcy + 3)
    pdf.set_dash_pattern(); _w(GEOM_W)

# Slot on +Y rib — visible as cutout on the front face. Solid rectangle outline.
_w(GEOM_W)
sx0 = fv(SLOT_X_CENTER - SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[0]
sy0 = fv(SLOT_X_CENTER - SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[1]
pdf.rect(sx0, sy0, SLOT_WIDTH, SLOT_HEIGHT, style="D")
# Slot dims: width (15) at top, height (6) on right side, X position from center, Z from rib base
hdim(fv(SLOT_X_CENTER - SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[0],
     fv(SLOT_X_CENTER + SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[0],
     fv(0, SLOT_BOTTOM_Z + SLOT_HEIGHT)[1],
     fv(0, SLOT_BOTTOM_Z + SLOT_HEIGHT)[1] - DIM_O1,
     f"{SLOT_WIDTH:g}")
vdim(fv(0, SLOT_BOTTOM_Z)[1], fv(0, SLOT_BOTTOM_Z + SLOT_HEIGHT)[1],
     fv(SLOT_X_CENTER + SLOT_WIDTH/2, 0)[0],
     fv(SLOT_X_CENTER + SLOT_WIDTH/2 + 6, 0)[0],
     f"{SLOT_HEIGHT:g}")
# X-center from disc center (rib center is at X=0)
hdim(fv(0, 0)[0], fv(SLOT_X_CENTER, 0)[0],
     fv(0, SLOT_BOTTOM_Z)[1], fv(0, SLOT_BOTTOM_Z)[1] + DIM_O2,
     f"{SLOT_X_CENTER:g}")
# Slot bottom Z above rib base (= disc top)
vdim(fv(0, DISC_THICK)[1], fv(0, SLOT_BOTTOM_Z)[1],
     fv(SLOT_X_CENTER - SLOT_WIDTH/2, 0)[0],
     fv(SLOT_X_CENTER - SLOT_WIDTH/2 - 6, 0)[0],
     f"{SLOT_BOTTOM_Z - DISC_THICK:g}")

# Front-view dims
hdim(fv(-DISC_OD/2, 0)[0], fv(DISC_OD/2, 0)[0],
     fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"{DISC_OD:g}")
vdim(fv(0, 0)[1], fv(0, DISC_THICK)[1],
     fv(DISC_OD/2, 0)[0], fv(DISC_OD/2, 0)[0] + DIM_O1, f"{DISC_THICK:g}")
vdim(fv(0, DISC_THICK)[1], fv(0, DISC_THICK + RIB_HEIGHT)[1],
     fv(DISC_OD/2, 0)[0], fv(DISC_OD/2, 0)[0] + DIM_O2, f"{RIB_HEIGHT:g}")
# Rib length
hdim(fv(-RIB_LENGTH/2, DISC_THICK + RIB_HEIGHT)[0],
     fv(+RIB_LENGTH/2, DISC_THICK + RIB_HEIGHT)[0],
     fv(0, DISC_THICK + RIB_HEIGHT)[1],
     fv(0, DISC_THICK + RIB_HEIGHT)[1] - DIM_O1,
     f"{RIB_LENGTH:.2f}")
# Rib hole positions
vdim(fv(0, DISC_THICK)[1], fv(0, RIB_HOLE_Z)[1],
     fv(RIB_HOLE_X[0], 0)[0], fv(RIB_HOLE_X[0] + 8, 0)[0],
     f"{RIB_HOLE_Z - DISC_THICK:g}")
# X positions of the 2 rib holes (already on top-view, but include for cross-reference)
hdim(fv(RIB_HOLE_X[1], 0)[0], fv(RIB_HOLE_X[0], 0)[0],
     fv(0, RIB_HOLE_Z)[1] + 4, fv(0, RIB_HOLE_Z)[1] + 4 + 0.01,
     f"{abs(RIB_HOLE_X[1] - RIB_HOLE_X[0]):g}")

text(fv_cx, fv(0, DISC_THICK + RIB_HEIGHT)[1] - DIM_O1 - 6,
     f"加强筋 {RIB_THICK:g} × {RIB_HEIGHT:g},2 条沿 X(径向)走,Y=±{RIB_CC/2:g}",
     size=TXT_I, anchor="middle")
text(fv_cx, fv(0, DISC_THICK + RIB_HEIGHT)[1] - DIM_O1 - 11,
     "前视图中两条肋投影到同一矩形",
     size=TXT_I, anchor="middle")

# ===== Title block =====
tb_y = PAGE_H - 28
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — rim_top_disc (Φ170 × 5 + 2 加强筋 + 16 M3 + 2 肋孔)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 前)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{DISC_OD:g} 圆盘 / 厚 {DISC_THICK:g} / 加强筋 {RIB_THICK:g}×{RIB_HEIGHT:g},c-to-c {RIB_CC:g} / "
     f"装在 rim_ring 上方,夹住 l_bracket_170x60 立柱  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-10  /  POV3D / models / rim_top_disc / rim_top_disc.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("rim_top_disc_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("rim_top_disc_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
