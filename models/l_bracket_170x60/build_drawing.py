"""
A3 landscape 2D engineering drawing for POV3D L-bracket (170×60, W50, T4).
Three views:
  1) FRONT VIEW (1:1) — L profile, looking from +Y. Shows both legs +
                         thicknesses with outer/inner outlines.
  2) TOP VIEW (1:1)   — looking from +Z down on the horizontal leg.
                         Shows long leg footprint 170×50.
  3) RIGHT-SIDE VIEW  — looking from +X. Shows width 50 × short-leg height 60.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
LEG_A = 200.0         # was 170, +30 on the open (right) end
LEG_B = 70.0          # was 60, +10 so vleg reaches rim outer PCD
WIDTH = 90.0          # was 80
THICK = 4.0

GUSSET_WIDTH       = 5.0
GUSSET_Y_POSITIONS = [GUSSET_WIDTH/2, WIDTH - GUSSET_WIDTH/2]   # 2.5, 87.5 (2 gussets)

HLEG_FEAT_X_SHIFT = 30.0           # all hleg-top features shifted +30 in X
M3_DIAM       = 3.2
M3_Y_CENTER   = WIDTH / 2          # 45
M3_X_A        = HLEG_FEAT_X_SHIFT + 95.0      # 125
M3_SPACING_A  = 20.0
M3_X_B        = M3_X_A + 66.0                 # 191
M3_SPACING_B  = 20.0
M3_X_C        = HLEG_FEAT_X_SHIFT + 8.0       # 38
M3_SPACING_C  = 70.0
SHIFT_BOT_X   = 1.0
SHIFT_BOT_Y   = 1.0
M3_PAIRS = [
    (M3_X_A, M3_SPACING_A),
    (M3_X_B, M3_SPACING_B),
    (M3_X_C, M3_SPACING_C),
]
M3_TOP_POSITIONS = [(xv, M3_Y_CENTER - sv/2)               for (xv, sv) in M3_PAIRS]
M3_BOT_POSITIONS = [(xv + SHIFT_BOT_X, M3_Y_CENTER + sv/2 + SHIFT_BOT_Y) for (xv, sv) in M3_PAIRS]
M3_POSITIONS = M3_TOP_POSITIONS + M3_BOT_POSITIONS

# 4 corner features on hleg (boss + M3 through + counterbore from bottom)
CORNER_M3_DIAM   = 3.2
CORNER_BOSS_DIAM = 7.0
CORNER_BOSS_H    = 2.0
CORNER_CB_DIAM   = 4.2
CORNER_CB_DEPTH  = 4.0
CORNER_RECT_X    = 49.0
CORNER_RECT_Y    = 58.0
CORNER_CX        = HLEG_FEAT_X_SHIFT + 52.0   # 82
CORNER_CY        = 45.5
CORNER_POSITIONS = [
    (CORNER_CX - CORNER_RECT_X/2, CORNER_CY - CORNER_RECT_Y/2),
    (CORNER_CX + CORNER_RECT_X/2, CORNER_CY - CORNER_RECT_Y/2),
    (CORNER_CX - CORNER_RECT_X/2, CORNER_CY + CORNER_RECT_Y/2),
    (CORNER_CX + CORNER_RECT_X/2, CORNER_CY + CORNER_RECT_Y/2),
]

# 4 × M3 vleg through-holes — mate with 4 rim_ring holes when the vleg lies
# flat on the rim base. (Trapezoidal pattern, no longer a rectangle.)
VLEG_M3_DIAM             = 3.2
RIM_R_IN                 = 35.0
RIM_R_OUT                = 77.5
RIM_MATING_ANGLES_DEG    = (157.5, 202.5)
HLEG_DIST_FROM_CENTER    = 14.3
def _vleg_pos_from_rim(R, ang_deg):
    x_rim = R * math.cos(math.radians(ang_deg))
    y_rim = R * math.sin(math.radians(ang_deg))
    return (y_rim + WIDTH / 2, -x_rim - HLEG_DIST_FROM_CENTER)
# Order: inner-+Y, inner-−Y, outer-+Y, outer-−Y
VLEG_M3_INNER_TOP = _vleg_pos_from_rim(RIM_R_IN,  RIM_MATING_ANGLES_DEG[0])  # (58.394, 18.036)
VLEG_M3_INNER_BOT = _vleg_pos_from_rim(RIM_R_IN,  RIM_MATING_ANGLES_DEG[1])  # (31.606, 18.036)
VLEG_M3_OUTER_TOP = _vleg_pos_from_rim(RIM_R_OUT, RIM_MATING_ANGLES_DEG[0])  # (74.658, 57.301)
VLEG_M3_OUTER_BOT = _vleg_pos_from_rim(RIM_R_OUT, RIM_MATING_ANGLES_DEG[1])  # (15.342, 57.301)
VLEG_M3_POSITIONS = [VLEG_M3_INNER_TOP, VLEG_M3_INNER_BOT,
                     VLEG_M3_OUTER_TOP, VLEG_M3_OUTER_BOT]
VLEG_INNER_Z = VLEG_M3_INNER_TOP[1]   # 18.036
VLEG_OUTER_Z = VLEG_M3_OUTER_TOP[1]   # 57.301
VLEG_INNER_DY = VLEG_M3_INNER_TOP[0] - VLEG_M3_INNER_BOT[0]   # 26.788
VLEG_OUTER_DY = VLEG_M3_OUTER_TOP[0] - VLEG_M3_OUTER_BOT[0]   # 59.316

# 2 × M3 gusset through-holes (along Y, hit both gussets)
GUSSET_HOLE_DIAM = 3.2
GUSSET_HOLE_X    = THICK + 15.0     # 19
GUSSET_HOLE_Z1   = 20.0
GUSSET_HOLE_Z2   = 50.0

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
text(PAGE_W/2, 14, "POV 3D L 形托架  L-Bracket  ({:g}×{:g}, W{:g}, T{:g})".format(
        LEG_A, LEG_B, WIDTH, THICK), size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"长边 {LEG_A:g} / 短边 {LEG_B:g} / 宽 {WIDTH:g} / 板厚 {THICK:g} / "
     f"6 × Φ{M3_DIAM:g} M3 (下排 X+{SHIFT_BOT_X:g} Y+{SHIFT_BOT_Y:g}) / "
     f"4 × [Φ{CORNER_BOSS_DIAM:g}×{CORNER_BOSS_H:g} 凸台 + Φ{CORNER_M3_DIAM:g} M3 通孔 + Φ{CORNER_CB_DIAM:g}×{CORNER_CB_DEPTH:g} 沉孔(底→顶)] ({CORNER_RECT_X:g}×{CORNER_RECT_Y:g} 角) / "
     f"4 × Φ{VLEG_M3_DIAM:g} M3 立板 (对 rim 内圈R{RIM_R_IN:g}+外圈R{RIM_R_OUT:g} @ 157.5°/202.5°,距圆心{HLEG_DIST_FROM_CENTER:g}) / "
     f"2 × 三角加强筋  (GB 第一角投影)",
     size=TXT_I, anchor="middle")

# ===== FRONT VIEW (1:1) — looking from +Y. PDF x = world X, PDF y = -world Z =====
fv_x0, fv_z0 = 30, 250
def fv(x, z): return (fv_x0 + x, fv_z0 - z)

text(fv_x0 + LEG_A/2, 180, "前视图  Front View  (1:1)   尺寸单位: mm  (沿 +Y 看)",
     size=TXT_L, anchor="middle")

_w(GEOM_W)
# L outline (looking at front, the L-shape is visible)
# Outer boundary (CCW): (0,0) → (LEG_A, 0) → (LEG_A, THICK) → (THICK, THICK) → (THICK, LEG_B) → (0, LEG_B) → (0, 0)
pts = [
    (0, 0), (LEG_A, 0), (LEG_A, THICK),
    (THICK, THICK), (THICK, LEG_B), (0, LEG_B), (0, 0)
]
for i in range(len(pts) - 1):
    x1, z1 = pts[i]; x2, z2 = pts[i + 1]
    line(*fv(x1, z1), *fv(x2, z2), GEOM_W)

# M3 hole hidden lines — each pair has same X so projects to one vertical
# line in the front view, from z=0 to z=THICK. 3 vertical hidden lines.
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
for x_val in (M3_X_A, M3_X_B, M3_X_C):
    pdf.line(*fv(x_val, 0), *fv(x_val, THICK))
# Corner-stack M3 holes — through boss + hleg, so z=0..THICK+BOSS_H
for x_val in sorted(set(p[0] for p in CORNER_POSITIONS)):
    pdf.line(*fv(x_val, 0), *fv(x_val, THICK + CORNER_BOSS_H))
pdf.set_dash_pattern(); _w(GEOM_W)

# Boss bumps on top of hleg — drawn as 3-segment "cap" above the hleg top
# edge at each unique X position of the corner stacks. 4 bosses share 2
# unique X positions, so 2 bumps in the front view.
_w(GEOM_W)
boss_r = CORNER_BOSS_DIAM / 2
for x_val in sorted(set(p[0] for p in CORNER_POSITIONS)):
    line(*fv(x_val - boss_r, THICK), *fv(x_val - boss_r, THICK + CORNER_BOSS_H), GEOM_W)
    line(*fv(x_val - boss_r, THICK + CORNER_BOSS_H),
         *fv(x_val + boss_r, THICK + CORNER_BOSS_H), GEOM_W)
    line(*fv(x_val + boss_r, THICK + CORNER_BOSS_H), *fv(x_val + boss_r, THICK), GEOM_W)

# Gusset hypotenuse line — both gussets project to the same triangle in
# the front view (the legs overlap with the L's inner edges; only the
# hypotenuse from (THICK, LEG_B) to (LEG_A, THICK) is new geometry).
_w(GEOM_W)
line(*fv(THICK, LEG_B), *fv(LEG_A, THICK), GEOM_W)

# 2 × M3 holes through the gussets (along Y axis). Both gusset faces share
# these positions, so the front view shows 2 solid circles inside the triangle.
for hz in (GUSSET_HOLE_Z1, GUSSET_HOLE_Z2):
    cx, cy = fv(GUSSET_HOLE_X, hz)
    _w(GEOM_W)
    pdf.circle(cx, cy, GUSSET_HOLE_DIAM/2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx - 3, cy, cx + 3, cy)
    pdf.line(cx, cy - 3, cx, cy + 3)
    pdf.set_dash_pattern(); _w(GEOM_W)

# Dim: 15 (gusset left edge X=THICK → hole X), placed INSIDE the triangle,
# at the lower hole's Z level. Extension lines go from the hole/edge up to
# a dim line ~8 mm above (visually "inside" the gusset).
hdim(fv(THICK, GUSSET_HOLE_Z1)[0], fv(GUSSET_HOLE_X, GUSSET_HOLE_Z1)[0],
     fv(0, GUSSET_HOLE_Z1)[1], fv(0, GUSSET_HOLE_Z1)[1] - 8,
     f"{GUSSET_HOLE_X - THICK:g}")
# Dim: 30 vertical spacing between the two holes, on the LEFT of the hole column
vdim(fv(0, GUSSET_HOLE_Z2)[1], fv(0, GUSSET_HOLE_Z1)[1],
     fv(GUSSET_HOLE_X, 0)[0], fv(GUSSET_HOLE_X - 6, 0)[0],
     f"{GUSSET_HOLE_Z2 - GUSSET_HOLE_Z1:g}")
# Z dim from hleg top (Z=THICK) to lower gusset hole, on the RIGHT of the hole
vdim(fv(0, GUSSET_HOLE_Z1)[1], fv(0, THICK)[1],
     fv(GUSSET_HOLE_X, 0)[0], fv(GUSSET_HOLE_X + 8, 0)[0],
     f"{GUSSET_HOLE_Z1 - THICK:g}")

text(fv(GUSSET_HOLE_X + 6, GUSSET_HOLE_Z2)[0],
     fv(GUSSET_HOLE_X + 6, GUSSET_HOLE_Z2)[1] - 1,
     f"2 × Φ{GUSSET_HOLE_DIAM:g} 通孔 (M3),贯通两片加强筋",
     size=TXT_I, anchor="start")

# Front-view dims
# Long leg length (along X) at bottom
hdim(fv(0, 0)[0], fv(LEG_A, 0)[0],
     fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"{LEG_A:g}")
# Short leg length (along Z) at left
vdim(fv(0, LEG_B)[1], fv(0, 0)[1],
     fv(0, 0)[0], fv(0, 0)[0] - DIM_O1, f"{LEG_B:g}")
# Horizontal-leg plate thickness (z=0..THICK, vertical 4mm) — at the right end
vdim(fv(LEG_A, 0)[1], fv(LEG_A, THICK)[1],
     fv(LEG_A, 0)[0], fv(LEG_A, 0)[0] + DIM_O1, f"{THICK:g}")
# (Vertical-leg thickness 4mm already shown by the top-edge note in title;
#  omit the narrow hdim here to avoid arrow-bbox precision overlap.)
text(fv(THICK, LEG_B)[0] + 2, fv(THICK, LEG_B)[1] - 1,
     f"板厚 {THICK:g} mm", size=TXT_I, anchor="start")

# ===== TOP VIEW (1:1) — looking from +Z down. PDF x = world X, PDF y = world Y =====
tv_x0, tv_y0 = 30, 55
def tv(x, y): return (tv_x0 + x, tv_y0 + y)

text(tv_x0 + LEG_A/2, 48, "俯视图  Top View  (1:1)   尺寸单位: mm  (沿 -Z 看)",
     size=TXT_L, anchor="middle")

# (gussets drawn below, after the rectangle)

_w(GEOM_W)
# Long leg footprint: 0..LEG_A × 0..WIDTH
pdf.rect(tv_x0, tv_y0, LEG_A, WIDTH, style="D")
# Vertical leg projection (footprint is 0..THICK × 0..WIDTH at the left corner)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
pdf.line(tv_x0 + THICK, tv_y0, tv_x0 + THICK, tv_y0 + WIDTH)
pdf.set_dash_pattern(); _w(GEOM_W)

# Gussets — each projects to a (LEG_A−THICK)×5 rectangle on the hleg top.
_w(GEOM_W)
for yc in GUSSET_Y_POSITIONS:
    gy0 = yc - GUSSET_WIDTH/2
    gy1 = yc + GUSSET_WIDTH/2
    pdf.rect(tv_x0 + THICK, tv_y0 + gy0, LEG_A - THICK, GUSSET_WIDTH, style='D')

# 6 × M3 holes — solid circles + crosshair
for (hx, hy) in M3_POSITIONS:
    cx, cy = tv(hx, hy)
    _w(GEOM_W)
    pdf.circle(cx, cy, M3_DIAM/2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx - 3, cy, cx + 3, cy)
    pdf.line(cx, cy - 3, cx, cy + 3)
    pdf.set_dash_pattern(); _w(GEOM_W)

# 4 corner stacks — each: Φ7 boss outline + Φ3.2 M3 through-hole (solid) +
# Φ4.2 counterbore on bottom face (hidden dashed)
for (hx, hy) in CORNER_POSITIONS:
    cx, cy = tv(hx, hy)
    _w(GEOM_W)
    # Φ7 boss outer (visible solid)
    pdf.circle(cx, cy, CORNER_BOSS_DIAM/2, style="D")
    # Φ4.2 counterbore (on bottom — hidden from top, dashed)
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    pdf.circle(cx, cy, CORNER_CB_DIAM/2, style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    # Φ3.2 M3 through-hole (solid)
    pdf.circle(cx, cy, CORNER_M3_DIAM/2, style="D")
    # crosshair
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx - 4, cy, cx + 4, cy)
    pdf.line(cx, cy - 4, cx, cy + 4)
    pdf.set_dash_pattern(); _w(GEOM_W)

# Bounding rectangle of the 4 corner positions (light dashed reference)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(0.15)
pdf.rect(tv_x0 + CORNER_CX - CORNER_RECT_X/2, tv_y0 + CORNER_CY - CORNER_RECT_Y/2,
         CORNER_RECT_X, CORNER_RECT_Y, style='D')
pdf.set_dash_pattern(); _w(GEOM_W)

# Top-view overall dims
hdim(tv_x0, tv_x0 + LEG_A,
     tv_y0 + WIDTH, tv_y0 + WIDTH + DIM_O3, f"{LEG_A:g}")
vdim(tv_y0, tv_y0 + WIDTH,
     tv_x0 + LEG_A, tv_x0 + LEG_A + DIM_O1, f"{WIDTH:g}")

# X-distance dims (bottom, stacked)
# Level 1 (DIM_O1=12): 8 (left edge to pair C)
hdim(tv_x0, tv_x0 + M3_X_C,
     tv_y0 + WIDTH, tv_y0 + WIDTH + DIM_O1, f"{M3_X_C:g}")
# Level 2 (DIM_O2=22): 95 (left edge to pair A) + 66 (pair A to pair B), chain
hdim(tv_x0, tv_x0 + M3_X_A,
     tv_y0 + WIDTH, tv_y0 + WIDTH + DIM_O2, f"{M3_X_A:g}")
hdim(tv_x0 + M3_X_A, tv_x0 + M3_X_B,
     tv_y0 + WIDTH, tv_y0 + WIDTH + DIM_O2, f"{M3_X_B - M3_X_A:g}")

# Y-spacing dims for each pair — use actual shifted hole positions
hy_A_top = tv(*M3_TOP_POSITIONS[0])[1]
hy_A_bot = tv(*M3_BOT_POSITIONS[0])[1]
hy_B_top = tv(*M3_TOP_POSITIONS[1])[1]
hy_B_bot = tv(*M3_BOT_POSITIONS[1])[1]
hy_C_top = tv(*M3_TOP_POSITIONS[2])[1]
hy_C_bot = tv(*M3_BOT_POSITIONS[2])[1]
SP_A = M3_SPACING_A + SHIFT_BOT_Y   # 21
SP_B = M3_SPACING_B + SHIFT_BOT_Y   # 21
SP_C = M3_SPACING_C + SHIFT_BOT_Y   # 71
vdim(hy_A_top, hy_A_bot, tv_x0 + M3_X_A, tv_x0 + M3_X_A - DIM_O1, f"{SP_A:g}")
vdim(hy_B_top, hy_B_bot, tv_x0 + M3_X_B, tv_x0 + M3_X_B - DIM_O1, f"{SP_B:g}")
vdim(hy_C_top, hy_C_bot, tv_x0 + M3_X_C, tv_x0 + M3_X_C + DIM_O1, f"{SP_C:g}")

# Y reference: 5 (top edge to pair C TOP hole)
vdim(tv_y0, hy_C_top, tv_x0, tv_x0 - DIM_O1,
     f"{M3_Y_CENTER - M3_SPACING_C/2:g}")

# Corner-stack rectangle dims: 49 (X) and 58 (Y)
hxC_L = tv(CORNER_CX - CORNER_RECT_X/2, 0)[0]
hxC_R = tv(CORNER_CX + CORNER_RECT_X/2, 0)[0]
hyC_T = tv(0, CORNER_CY - CORNER_RECT_Y/2)[1]
hyC_B = tv(0, CORNER_CY + CORNER_RECT_Y/2)[1]
hdim(hxC_L, hxC_R, hyC_T, hyC_T - DIM_O1, f"{CORNER_RECT_X:g}")
vdim(hyC_T, hyC_B, hxC_L, hxC_L - DIM_O1, f"{CORNER_RECT_Y:g}")

# Note about the bottom-row M3 shift + corner-stack feature
text(tv_x0 + LEG_A - 2, tv_y0 - 3,
     f"注: M3 下排 X+{SHIFT_BOT_X:g}, Y+{SHIFT_BOT_Y:g} 偏移 / "
     f"4 × Φ{CORNER_BOSS_DIAM:g}×{CORNER_BOSS_H:g} 凸台 + Φ{CORNER_M3_DIAM:g} M3 通孔 + Φ{CORNER_CB_DIAM:g}×{CORNER_CB_DEPTH:g} 沉孔(底→顶)",
     size=TXT_I, anchor="end")

# ===== RIGHT-SIDE VIEW (1:1) — looking from +X. Shows width × height (90 × LEG_B) =====
sv_x0, sv_z0 = 290, 250
def sv(y, z): return (sv_x0 + y, sv_z0 - z)

text(sv_x0 + WIDTH/2, 180,
     "右视图  Right View  (1:1)   尺寸单位: mm  (沿 +X 看,立板 70×90 面)",
     size=TXT_L, anchor="middle")

_w(GEOM_W)
# Right view: outer silhouette is WIDTH × LEG_B rectangle (vleg spans full Y).
pdf.rect(sv_x0, sv_z0 - LEG_B, WIDTH, LEG_B, style="D")

# Gussets project onto the YZ plane as vertical rectangles (Y_start..Y_end,
# Z=THICK..LEG_B). The hypotenuse is hidden behind the vleg outline.
for yc in GUSSET_Y_POSITIONS:
    gy0 = yc - GUSSET_WIDTH/2
    gy1 = yc + GUSSET_WIDTH/2
    pdf.rect(sv_x0 + gy0, sv_z0 - LEG_B, GUSSET_WIDTH, LEG_B - THICK, style='D')

# 4 × M3 vleg through-holes (trapezoidal pattern matching rim_ring holes)
for (hy, hz) in VLEG_M3_POSITIONS:
    cx, cy = sv(hy, hz)
    _w(GEOM_W)
    pdf.circle(cx, cy, VLEG_M3_DIAM/2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx - 3, cy, cx + 3, cy)
    pdf.line(cx, cy - 3, cx, cy + 3)
    pdf.set_dash_pattern(); _w(GEOM_W)

# Trapezoid reference (light dashed) connecting the 4 mating holes
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(0.15)
ord_pts = [VLEG_M3_INNER_BOT, VLEG_M3_INNER_TOP, VLEG_M3_OUTER_TOP, VLEG_M3_OUTER_BOT]
for i in range(len(ord_pts)):
    (y1, z1) = ord_pts[i]
    (y2, z2) = ord_pts[(i + 1) % len(ord_pts)]
    pdf.line(*sv(y1, z1), *sv(y2, z2))
pdf.set_dash_pattern(); _w(GEOM_W)

# Centerline (Y_v = WIDTH/2)
pdf.set_dash_pattern(dash=4.0, gap=1.5, phase=2.0); _w(0.18)
pdf.line(sv(WIDTH/2, -4)[0], sv(WIDTH/2, -4)[1],
         sv(WIDTH/2, LEG_B + 4)[0], sv(WIDTH/2, LEG_B + 4)[1])
pdf.set_dash_pattern(); _w(GEOM_W)

# Dim: outer-pair Y spacing (below outer row)
vy_oL = sv(VLEG_M3_OUTER_BOT[0], 0)[0]
vy_oR = sv(VLEG_M3_OUTER_TOP[0], 0)[0]
vz_outer = sv(0, VLEG_OUTER_Z)[1]
hdim(vy_oL, vy_oR, vz_outer, vz_outer + DIM_O2, f"{VLEG_OUTER_DY:.2f}")

# Dim: inner-pair Y spacing (between rows, above inner row)
vy_iL = sv(VLEG_M3_INNER_BOT[0], 0)[0]
vy_iR = sv(VLEG_M3_INNER_TOP[0], 0)[0]
vz_inner = sv(0, VLEG_INNER_Z)[1]
hdim(vy_iL, vy_iR, vz_inner, vz_inner - DIM_O1, f"{VLEG_INNER_DY:.2f}")

# Dim: Z from vleg bottom edge (Z_v=0, the L-corner edge / closer to rim center
# in assembly) to the two hole rows — stacked on the LEFT of the view
vz_zero = sv(0, 0)[1]
vdim(vz_inner, vz_zero, sv_x0, sv_x0 - DIM_O1, f"{VLEG_INNER_Z:.2f}")
vdim(vz_outer, vz_zero, sv_x0, sv_x0 - DIM_O2, f"{VLEG_OUTER_Z:.2f}")

text(sv_x0, sv_z0 - LEG_B - 6,
     f"4 × Φ{VLEG_M3_DIAM:g} 通孔 (M3),对位 rim 内外圈 ±{180 - RIM_MATING_ANGLES_DEG[0]:g}° "
     f"(R={RIM_R_IN:g} & {RIM_R_OUT:g})  /  Z_v=0 朝圆心,距圆心 {HLEG_DIST_FROM_CENTER:g} mm",
     size=TXT_I, anchor="start")

# Side-view dims
hdim(sv_x0, sv_x0 + WIDTH,
     sv_z0, sv_z0 + DIM_O1, f"{WIDTH:g}")
vdim(sv_z0 - LEG_B, sv_z0,
     sv_x0 + WIDTH, sv_x0 + WIDTH + DIM_O1, f"{LEG_B:g}")

# Note about extending horizontal leg into background
text(sv_x0 + WIDTH/2, sv_z0 + DIM_O1 + 8,
     f"(长边 {LEG_A:g} 沿 +X 方向延伸)", size=TXT_I, anchor="middle")

# ===== Title block =====
tb_y = PAGE_H - 28
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — L 形托架 (L-Bracket 170×60)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (前, 俯, 右)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"长边 {LEG_A:g} / 短边 {LEG_B:g} / 宽 {WIDTH:g} / 板厚 {THICK:g} / "
     f"6 × Φ{M3_DIAM:g} M3 通孔 (3 组,中线对称)  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-09  /  POV3D / models / l_bracket_170x60 / l_bracket_170x60.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("l_bracket_170x60_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("l_bracket_170x60_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
