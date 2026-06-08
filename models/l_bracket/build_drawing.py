"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D L-bracket.

Two views:
  1) TOP VIEW  (俯视图, 1:1) — bracket viewed from above, showing length and
                                4-hole pattern with chain dimensions
  2) SIDE VIEW (侧视图, 5:1) — cross-section of the 90° L profile, showing
                                leg lengths, wall thicknesses, and angle

PDF unit = mm. Both views are at correctly stated scales; real product
dimensions appear in dimension labels regardless of view scale.
"""

import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (real mm) =====
LENGTH    = 140.0
LEG_A     = 15.0
LEG_B     = 6.0
THICK_A   = 3.0
THICK_B   = 3.0
ANGLE_DEG = 90.0
HOLE_DIAM = 3.2
HOLE_Y    = LEG_A - 5.0           # 10 mm from outer corner
HOLE_X    = [6.0, 66.0, 134.0]    # original 4-hole pattern; X=194 trimmed off at length 170

theta = math.radians(ANGLE_DEG)
ct, st = math.cos(theta), math.sin(theta)
u_inner = (THICK_A + THICK_B * ct) / st
P3_y    = THICK_B * st + u_inner * ct
P0 = (0.0, 0.0)
P1 = (LEG_A, 0.0)
P2 = (LEG_A, THICK_A)
P3 = (P3_y, THICK_A)
P5 = (LEG_B * ct, LEG_B * st)
P4 = (P5[0] + THICK_B * st, P5[1] - THICK_B * ct)
profile = [P0, P1, P2, P3, P4, P5]

csy_min = min(v[0] for v in profile)
csy_max = max(v[0] for v in profile)
TV_Y_MIN = csy_min
TV_Y_MAX = csy_max

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

# Style
GEOM_W   = 0.70
DIM_W    = 0.30
EXT_W    = 0.20
HID_W    = 0.28
ARROW_L  = 4.2
ARROW_W  = 1.5
EXT_OVER = 2.4
EXT_GAP  = 1.0
TXT_DIM     = 5.5     # was 4.5 — bumped per user feedback (readability)
TXT_LABEL   = 8.0     # was 6.5
TXT_TITLE   = 9.5     # was 5.5 (now used for main title)
TXT_INFO    = 5.0     # was 2.6
DIM_OFF1 = 14.0       # widened to fit larger text
DIM_OFF2 = 26.0

# ===== Drawing helpers (all distances in PDF mm) =====
def _w(v): pdf.set_line_width(v)

def line(x1, y1, x2, y2, w=DIM_W):
    _w(w); pdf.line(x1, y1, x2, y2)

def arrow(tip_x, tip_y, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    tx, ty = tip_x - ARROW_L * ux, tip_y - ARROW_L * uy
    px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tip_x, tip_y),
                 (tx + ARROW_W * px, ty + ARROW_W * py),
                 (tx - ARROW_W * px, ty - ARROW_W * py)], style="F")

def text(x, y, s, size=TXT_DIM, anchor="start"):
    pdf.set_font("SimHei", "", size)
    if anchor == "middle":
        x -= pdf.get_string_width(s) / 2
    elif anchor == "end":
        x -= pdf.get_string_width(s)
    pdf.text(x, y, s)

def rotated_text(cx, cy, s, angle_deg, size=TXT_DIM, anchor="middle", offset_perp=0):
    """Draw text rotated by angle_deg around (cx, cy). Text reads along the rotated +X axis.
       offset_perp: shift the text perpendicular to its reading direction (positive = above the line)."""
    pdf.set_font("SimHei", "", size)
    sw = pdf.get_string_width(s)
    if anchor == "middle":
        dx0 = -sw / 2
    elif anchor == "end":
        dx0 = -sw
    else:
        dx0 = 0
    with pdf.rotation(angle=angle_deg, x=cx, y=cy):
        # In the rotated frame, drawing at (cx + dx0, cy + dy0) places text accordingly
        pdf.text(cx + dx0, cy - offset_perp, s)

def _with_unit(label, unit="mm"):
    s = str(label).strip()
    if not s or unit in s or "°" in s:
        return s
    return f"{s} {unit}"

def hdim(x1, x2, y_geom, y_dim, label):
    label = _with_unit(label)
    if y_dim > y_geom:
        ey_s, ey_e = y_geom + EXT_GAP, y_dim + EXT_OVER
    else:
        ey_s, ey_e = y_geom - EXT_GAP, y_dim - EXT_OVER
    line(x1, ey_s, x1, ey_e, EXT_W)
    line(x2, ey_s, x2, ey_e, EXT_W)
    x_l, x_r = (x1, x2) if x1 < x2 else (x2, x1)
    gap = x_r - x_l
    if gap >= 2 * ARROW_L + 1:
        line(x_l, y_dim, x_r, y_dim, DIM_W)
        arrow(x_l, y_dim, -1, 0); arrow(x_r, y_dim, 1, 0)
    else:
        ext = ARROW_L + 1.0
        line(x_l - ext, y_dim, x_r + ext, y_dim, DIM_W)
        arrow(x_l, y_dim,  1, 0); arrow(x_r, y_dim, -1, 0)
    text((x_l + x_r) / 2, y_dim - 1.8, label, anchor="middle")

def vdim(y1, y2, x_geom, x_dim, label):
    label = _with_unit(label)
    if x_dim > x_geom:
        ex_s, ex_e = x_geom + EXT_GAP, x_dim + EXT_OVER
        tx_off = 4.0
    else:
        ex_s, ex_e = x_geom - EXT_GAP, x_dim - EXT_OVER
        tx_off = -4.0
    line(ex_s, y1, ex_e, y1, EXT_W)
    line(ex_s, y2, ex_e, y2, EXT_W)
    y_top, y_bot = (y1, y2) if y1 < y2 else (y2, y1)
    gap = y_bot - y_top
    if gap >= 2 * ARROW_L + 1:
        line(x_dim, y_top, x_dim, y_bot, DIM_W)
        arrow(x_dim, y_top, 0, -1); arrow(x_dim, y_bot, 0, 1)
    else:
        ext = ARROW_L + 1.0
        line(x_dim, y_top - ext, x_dim, y_bot + ext, DIM_W)
        arrow(x_dim, y_top, 0,  1)
        arrow(x_dim, y_bot, 0, -1)
    label_h_rot = pdf.get_string_width(label)
    if gap >= label_h_rot + 1.0:
        rotated_text(x_dim + tx_off, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        y_label = y_bot + (ARROW_L + 1.0) + label_h_rot / 2 + 1.0
        rotated_text(x_dim + tx_off, y_label, label, angle_deg=90, anchor="middle")

def linear_dim_along(p1_pdf, p2_pdf, perp_dx, perp_dy, dim_off, label):
    """Generic linear dimension between two PDF points, with dim line offset along (perp_dx, perp_dy) by dim_off PDF mm."""
    a1 = (p1_pdf[0] + perp_dx * dim_off, p1_pdf[1] + perp_dy * dim_off)
    a2 = (p2_pdf[0] + perp_dx * dim_off, p2_pdf[1] + perp_dy * dim_off)
    # Extension lines
    e1_s = (p1_pdf[0] + perp_dx * EXT_GAP, p1_pdf[1] + perp_dy * EXT_GAP)
    e1_e = (p1_pdf[0] + perp_dx * (dim_off + EXT_OVER), p1_pdf[1] + perp_dy * (dim_off + EXT_OVER))
    e2_s = (p2_pdf[0] + perp_dx * EXT_GAP, p2_pdf[1] + perp_dy * EXT_GAP)
    e2_e = (p2_pdf[0] + perp_dx * (dim_off + EXT_OVER), p2_pdf[1] + perp_dy * (dim_off + EXT_OVER))
    line(*e1_s, *e1_e, EXT_W)
    line(*e2_s, *e2_e, EXT_W)
    line(*a1, *a2, DIM_W)
    # Arrows pointing along the dim line direction
    L = math.hypot(a2[0] - a1[0], a2[1] - a1[1])
    ux, uy = (a2[0] - a1[0]) / L, (a2[1] - a1[1]) / L
    arrow(a1[0], a1[1], -ux, -uy)
    arrow(a2[0], a2[1],  ux,  uy)
    # Text along the dim line direction, slightly offset toward perp direction
    mx, my = (a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2
    # Text angle: reading direction is along (ux, uy). Compute the rotation angle in degrees.
    # We want text to read "naturally" — for vertical/near-vertical lines, text reads bottom-to-top (rotate -90 from horizontal).
    angle = math.degrees(math.atan2(uy, ux))
    # Normalize: if angle is in (90, 270) or (-270, -90), flip to keep text upright
    if angle > 90:
        angle -= 180
    elif angle < -90:
        angle += 180
    # Place text just on the dim line, slightly above (toward outward perp)
    text_offset_perp = 1.2 + TXT_DIM / 2     # mm above the dim line in the perp direction
    text_x = mx - perp_dx * text_offset_perp
    text_y = my - perp_dy * text_offset_perp
    # Actually no: we want text ABOVE the dim line (between dim line and geometry interior side).
    # The text should be on the OPPOSITE side from the outward perp.
    text_x = mx + perp_dx * -text_offset_perp * 0   # actually try a different approach
    # Cleaner approach: text just above the dim line (in direction OPPOSITE to perp, since perp points outward)
    text_anchor_x = mx + (-perp_dx) * 1.4
    text_anchor_y = my + (-perp_dy) * 1.4
    rotated_text(mx, my, label, angle_deg=angle, anchor="middle", offset_perp=1.4)

# ===== Page frame =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")

# ===== Title at top =====
text(PAGE_W / 2, 16,
     "L 型角条  L-Angle Bracket  —  POV 3D 结构件",
     size=TXT_TITLE, anchor="middle")
text(PAGE_W / 2, 22,
     f"长 {LENGTH:g}  /  截面 {LEG_A:g}×{LEG_B:g}  /  壁厚 {THICK_A:g}  /  夹角 {ANGLE_DEG:g}°  /  3 × M3 (Φ{HOLE_DIAM:g}) 通孔",
     size=TXT_INFO, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_x = (PAGE_W - LENGTH) / 2
tv_y_center = 70

def tv_pdf(bx, by):
    return (tv_x + bx, tv_y_center - by)

text(PAGE_W / 2, 38,
     "俯视图  Top View  (1:1)   尺寸单位: mm", size=TXT_LABEL, anchor="middle")

top_y_max = tv_pdf(0, TV_Y_MAX)[1]
top_y_min = tv_pdf(0, TV_Y_MIN)[1]
tv_left   = tv_pdf(0, 0)[0]
tv_right  = tv_pdf(LENGTH, 0)[0]

# Outer outline & internal edges (visible from above)
_w(GEOM_W)
pdf.line(tv_left,  top_y_max, tv_right, top_y_max)        # leg A free-end side (Y_max=15)
pdf.line(tv_left,  top_y_min, tv_right, top_y_min)        # leg B outer face side (Y_min≈-3.88)
pdf.line(tv_left,  top_y_max, tv_left,  top_y_min)        # left end
pdf.line(tv_right, top_y_max, tv_right, top_y_min)        # right end
y_at_y0 = tv_pdf(0, 0)[1]
pdf.line(tv_left, y_at_y0, tv_right, y_at_y0)             # outer corner edge (Y=0)
y_at_p3 = tv_pdf(0, P3_y)[1]
pdf.line(tv_left, y_at_p3, tv_right, y_at_p3)             # inner corner edge (Y = P3_y)

# Hole centerline along X
y_hole_line = tv_pdf(0, HOLE_Y)[1]
pdf.set_dash_pattern(dash=4.0, gap=1.5)
_w(0.15)
pdf.line(tv_left - 6, y_hole_line, tv_right + 6, y_hole_line)
# Length centerline
x_center = tv_pdf(LENGTH / 2, 0)[0]
pdf.line(x_center, top_y_max - 6, x_center, top_y_min + 6)
pdf.set_dash_pattern()

# Hole circles
for hx in HOLE_X:
    cx, cy = tv_pdf(hx, HOLE_Y)
    _w(GEOM_W); pdf.circle(cx, cy, HOLE_DIAM / 2, style="D")
    pdf.set_dash_pattern(dash=1.5, gap=0.8)
    _w(0.12)
    pdf.line(cx - 3, cy, cx + 3, cy)
    pdf.line(cx, cy - 3, cx, cy + 3)
    pdf.set_dash_pattern()

# --- Top view dimensions ---
chain_dim_y = top_y_min + 10
end_dim_y   = top_y_min + 18
chain_pts = [0.0] + list(HOLE_X) + [LENGTH]
chain_lbl = [f"{chain_pts[i+1] - chain_pts[i]:g}" for i in range(len(chain_pts) - 1)]
for i in range(len(chain_pts) - 1):
    xa = tv_pdf(chain_pts[i], 0)[0]
    xb = tv_pdf(chain_pts[i + 1], 0)[0]
    hdim(xa, xb, top_y_min, chain_dim_y, chain_lbl[i])
hdim(tv_left, tv_right, top_y_min, end_dim_y, f"{LENGTH:g}")

# Left-side Y dimensions: hole Y position (10) and inner-corner Y (3.84)
left_dim_x1 = tv_left - 10
left_dim_x2 = tv_left - 18
vdim(top_y_max, y_hole_line, tv_left, left_dim_x1, "10")
vdim(y_at_y0, y_at_p3, tv_left, left_dim_x2, f"{P3_y:.2f}")
# Right-side: overall Y extent
right_dim_x = tv_right + 10
vdim(top_y_max, top_y_min, tv_right, right_dim_x, f"{TV_Y_MAX - TV_Y_MIN:.2f}")

# Hole callout
cx0, cy0 = tv_pdf(HOLE_X[0], HOLE_Y)
leader_x, leader_y = cx0 - 14, cy0 - 9
_w(EXT_W)
pdf.line(cx0 - HOLE_DIAM / 2 - 0.4, cy0 - HOLE_DIAM / 2 - 0.4, leader_x, leader_y)
pdf.line(leader_x, leader_y, leader_x - 8, leader_y)
text(leader_x - 8, leader_y - 1.2, f"{len(HOLE_X)} × Φ{HOLE_DIAM:g} (M3 通孔)", size=TXT_DIM, anchor="end")

# ===== SIDE VIEW (5:1) =====
SCALE_SIDE = 5
sv_x_offset = PAGE_W / 2 - 5       # PDF X for cross-section's Y=0
sv_y_baseline = 245                # PDF Y for cross-section's Z=0
sv_label_y = 135

def sv_pdf(y_geom, z_geom):
    return (sv_x_offset + y_geom * SCALE_SIDE,
            sv_y_baseline - z_geom * SCALE_SIDE)

text(PAGE_W / 2, sv_label_y,
     "侧视图 (截面)  Side View / Section  (5:1)   尺寸单位: mm",
     size=TXT_LABEL, anchor="middle")

# Cross-section polygon
poly_pts = [sv_pdf(v[0], v[1]) for v in profile]
_w(GEOM_W)
pdf.polygon(poly_pts, style="D")

# Pre-compute PDF points
P0_pdf = sv_pdf(*P0)
P1_pdf = sv_pdf(*P1)
P2_pdf = sv_pdf(*P2)
P3_pdf = sv_pdf(*P3)
P4_pdf = sv_pdf(*P4)
P5_pdf = sv_pdf(*P5)

# --- Side view dimensions ---
# 1) Leg A outer length 15 mm  (P0→P1, horizontal in PDF)
#    Place dim line BELOW (positive PDF Y, away from material)
hdim(P0_pdf[0], P1_pdf[0], P0_pdf[1],
     P0_pdf[1] + DIM_OFF1, f"{LEG_A:g}")

# 2) Leg A thickness 5 mm  (P1→P2, vertical in PDF)
#    Place dim line to the RIGHT
vdim(P2_pdf[1], P1_pdf[1], P1_pdf[0],
     P1_pdf[0] + DIM_OFF1, f"{THICK_A:g}")

# 3) Leg B outer length 15 mm  (P0→P5, along leg B direction)
# Direction in PDF from P0 to P5:
dx_b = P5_pdf[0] - P0_pdf[0]
dy_b = P5_pdf[1] - P0_pdf[1]
L_b = math.hypot(dx_b, dy_b)
ux_b, uy_b = dx_b / L_b, dy_b / L_b
# Outward perpendicular in PDF coords (PDF +Y points DOWN).
# Walking P0→P5 in PDF direction (ux_b, uy_b); the visual-left perpendicular —
# which is the outside-of-bracket side since leg A lies on the visual-right — is
# (uy, -ux) under PDF's flipped-Y convention.
out_x =  uy_b
out_y = -ux_b
linear_dim_along(P0_pdf, P5_pdf, out_x, out_y, DIM_OFF1, f"{LEG_B:g}")

# 4) Leg B thickness 5 mm  (P5→P4, perpendicular to leg B's outer face)
# Place beyond P5 along +leg-B direction (axial).
ax_b, ay_b = ux_b, uy_b   # axial direction along leg B (P0→P5)
linear_dim_along(P5_pdf, P4_pdf, ax_b, ay_b, DIM_OFF1, f"{THICK_B:g}")

# 5) Inside angle 90° at outer corner P0
ang_r = 18      # arc radius in PDF mm
n_seg = 24
arc_pts = []
for i in range(n_seg + 1):
    t = i / n_seg
    a = -theta * t   # PDF angle: cross-section CCW from +X (=leg A) toward +B direction
    arc_pts.append((P0_pdf[0] + ang_r * math.cos(a),
                    P0_pdf[1] + ang_r * math.sin(a)))
_w(DIM_W)
for i in range(len(arc_pts) - 1):
    pdf.line(arc_pts[i][0], arc_pts[i][1], arc_pts[i + 1][0], arc_pts[i + 1][1])
# Arrows tangent to arc at both ends
# Start tangent (a=0): direction (-sin(0), cos(0)) = (0, 1)  → downward in PDF (toward inside)
arrow(arc_pts[0][0], arc_pts[0][1], 0, 1)
# End tangent (a=-theta): direction (-sin(-theta), cos(-theta)) = (sin_t, cos_t) in math; but we used
# -theta as PDF angle and need PDF-frame tangent. d/da (cos a, sin a) = (-sin a, cos a). At a=-theta,
# tangent = (-sin(-theta), cos(-theta)) = (sin_t, cos_t). Sign for direction along arc as a decreases
# from 0 to -theta: derivative w.r.t. parameter t is -theta*(-sin(-t*theta), cos(-t*theta)). Net direction
# at the end: opposite of tangent direction. We want the arrow head to point INWARD along the arc.
end_tan_x = math.sin(theta)
end_tan_y = math.cos(theta)
arrow(arc_pts[-1][0], arc_pts[-1][1], -end_tan_x, -end_tan_y)
# Label '90°' just outside the arc
mid_a = -theta / 2
lbl_x = P0_pdf[0] + (ang_r + 4) * math.cos(mid_a)
lbl_y = P0_pdf[1] + (ang_r + 4) * math.sin(mid_a)
text(lbl_x, lbl_y, "90°", size=TXT_DIM, anchor="start")

# Vertex callouts (light gray, very small): label inner corner & outer corner positions for clarity
# (skipped to keep the drawing uncluttered)

# ===== Title block (bottom) =====
tb_y = PAGE_H - 38
tb_x = 20
tb_w = PAGE_W - 40
tb_h = 20
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h / 2, tb_x + tb_w, tb_y + tb_h / 2)

text(tb_x + 4, tb_y + 6.5,
     "POV 3D 结构件 — L 型 90° 角支架",
     size=TXT_LABEL, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6.5,
     "投影 1st-angle  /  比例 1:1 (俯) , 5:1 (侧)",
     size=TXT_INFO, anchor="end")
text(tb_x + 4, tb_y + 15.5,
     f"总长 {LENGTH:g}  /  截面 {LEG_A:g}×{LEG_B:g}  /  壁厚 {THICK_A:g}  /  夹角 {ANGLE_DEG:g}°  /  3×Φ{HOLE_DIAM:g} 通孔  /  单位 mm",
     size=TXT_INFO, anchor="start")
text(tb_x + tb_w - 4, tb_y + 15.5,
     "日期 2026-06-04  /  POV3D / models / l_bracket.stl",
     size=TXT_INFO, anchor="end")

# ===== Save =====
out_path = Path(__file__).with_name("l_bracket_drawing.pdf")
pdf.output(str(out_path))
print(f"wrote {out_path}")
