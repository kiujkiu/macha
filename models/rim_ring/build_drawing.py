"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D rim_ring.

Views:
  1) TOP VIEW (Top View, 1:1) - outline circles Phi60, Phi80 (notch boundary),
                                  Phi165, Phi170; both PCD circles Phi70 and
                                  Phi155 dashed; all 16 Phi3.2 holes solid with
                                  crosshairs; angular cutouts shown as breaks
                                  in the relevant arcs with radial step lines
                                  and angle labels (-45 deg, -40 deg, -5 deg,
                                  0 deg).
  2) SECTION A-A (1:1) - cut along +X axis (0 deg / 180 deg). Shows stepped
                          profile: base annulus 5mm, rim boss 5.5mm on top.
                          PCD155 holes at t=+/-77.5 (Phi3.2 through).
                          PCD70 holes are NOT on the X axis after the 22.5 deg
                          rotation, so they only show in the top view.
  3) SECTION B-B (1:1) - cut along -42.5 deg axis (through the notch +
                          aligned boss-gap), so the radial slot is visible.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / rim_ring.scad) =====
BASE_ID  = 60.0
BASE_OD  = 170.0
BASE_H   = 5.0

NOTCH_R_MIN = 40.0          # Phi 80
NOTCH_A_S   = -45.0
NOTCH_A_E   = -40.0
NOTCH_Z_S   = 2.5
NOTCH_Z_E   = BASE_H        # 5

RIM_ID = 165.0
RIM_OD = 170.0
RIM_H  = 5.5

RIM_CUT1_A_S = -5.0
RIM_CUT1_A_E =  0.0
RIM_CUT2_A_S = -45.0
RIM_CUT2_A_E = -40.0

TOTAL_H = BASE_H + RIM_H    # 10.5

M3_DIAM    = 3.2
INNER_PCD_R = 35.0          # Phi 70
INNER_PCD   = 2 * INNER_PCD_R
OUTER_PCD_R = 77.5          # Phi 155
OUTER_PCD   = 2 * OUTER_PCD_R

HOLE_ANGLES = [22.5 + k * 45.0 for k in range(8)]
PATTERN_INNER = [(INNER_PCD_R * math.cos(math.radians(a)),
                  INNER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]
PATTERN_OUTER = [(OUTER_PCD_R * math.cos(math.radians(a)),
                  OUTER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]

# Section A-A cuts along the +X / -X axis. After hole rotation 22.5 deg, no
# PCD70 hole is on the X axis. The closest PCD155 holes to the X axis are at
# 22.5 deg and -22.5 deg (337.5 deg) -- not on the axis. So the only holes
# crossed by section A-A are: none on the rings. However for visual clarity
# (a "synthetic" through-hole indication is wrong) we leave the section
# without ring-hole intersections and label the rings via PCD reference
# circles + top-view callouts.

# Section B-B cuts along the -42.5 deg radial (mid-angle of the notch and
# the aligned boss gap, both -45..-40). PCD70 and PCD155 holes are NOT on
# this radial either. So Section B-B is purely a radial structural view
# showing the notch step.
SECTION_BB_ANGLE = -42.5

# Convenience radii
R_BI    = BASE_ID / 2        # 30
R_BO    = BASE_OD / 2        # 85
R_RBI   = RIM_ID / 2         # 82.5
R_RBO   = RIM_OD / 2         # 85
R_NOTCH = NOTCH_R_MIN        # 40

# Z levels
Z0 = 0.0
Z_NOTCH = NOTCH_Z_S          # 2.5
Z1 = BASE_H                   # 5
Z2 = TOTAL_H                  # 10.5

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
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
text(PAGE_W/2, 13, "POV 3D 外缘环  Rim Ring", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19,
     (f"基环 Φ{BASE_OD:g}/Φ{BASE_ID:g}xH{BASE_H:g}  "
      f"(切口 r>{NOTCH_R_MIN:g} / {NOTCH_A_S:g}°~{NOTCH_A_E:g}° / Z={NOTCH_Z_S:g}~{NOTCH_Z_E:g}) / "
      f"外凸圈 Φ{RIM_OD:g}/Φ{RIM_ID:g}xH{RIM_H:g}  "
      f"(切口 {RIM_CUT1_A_S:g}°~{RIM_CUT1_A_E:g}° + {RIM_CUT2_A_S:g}°~{RIM_CUT2_A_E:g}°) / "
      f"16xΦ{M3_DIAM:g} (8 内PCD Φ{INNER_PCD:g} + 8 外PCD Φ{OUTER_PCD:g}, 起 22.5°)"),
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 115, 158
def tv(x, y): return (tv_cx + x, tv_cy - y)

# Top view title sits to the LEFT, BELOW the top dim stack. The leftmost
# extension line is at x = tv(-R_BO, 0).x = 30, so for x <= 28 there is no
# stack interference. We anchor at the LEFT margin (x = 8) on the line just
# below the lowest top dim (Φ170 dim line at y=59, label at y=57.2).
text(8, 67, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_I, anchor="start")

# ----- Section A-A cutting line (along +X / -X axis = 0 deg / 180 deg) -----
# Keep the cutting line short. Endpoint labels are placed CLOSE to the disc
# OD (not extending into the Section A-A gutter where its left vdims live).
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
end1 = tv( R_BO + 4, 0)
end2 = tv(-R_BO - 4, 0)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
# Place "A" labels just ABOVE the cutting line, hugging the disc OD on the
# OUTSIDE. The right "A" sits below the line (clearing the 0 deg angle label
# at y=154) at y=164; the left "A" sits above the line as usual.
text(end1[0] - 4, end1[1] + 5, "A", size=TXT_I)
text(end2[0] + 1, end2[1] - 2, "A", size=TXT_I)

# ----- Section B-B cutting line (along -42.5 deg radial through notch) -----
bb_rad = math.radians(SECTION_BB_ANGLE)
bb_ux, bb_uy = math.cos(bb_rad), math.sin(bb_rad)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
# Draw from (-OD-4) to (+OD+4) along the -42.5 deg radial
bb_e1 = tv( (R_BO + 4) * bb_ux,  (R_BO + 4) * bb_uy)
bb_e2 = tv(-(R_BO + 4) * bb_ux, -(R_BO + 4) * bb_uy)
pdf.line(bb_e1[0], bb_e1[1], bb_e2[0], bb_e2[1])
pdf.set_dash_pattern()
text(bb_e1[0] - 4, bb_e1[1] - 1, "B", size=TXT_I)
text(bb_e2[0] + 1, bb_e2[1] - 1, "B", size=TXT_I)

# ----- Disc geometry circles -----
_w(GEOM_W)
ccx, ccy = tv(0, 0)
pdf.circle(ccx, ccy, R_BI, style="D")    # Phi60 base ID
# Phi80 notch reference circle (dashed - this is the notch r-boundary,
# only physically a step inside the notched wedge; show as dashed reference)
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.18)
pdf.circle(ccx, ccy, R_NOTCH, style="D")
pdf.set_dash_pattern()
_w(GEOM_W)

# Base OD Phi170 - drawn as a full circle EXCEPT where the notch goes to the
# top face (-45..-40 deg). In that wedge, the top-face OD is missing (since
# r > 40 is removed from Z=2.5..5), but the BOTTOM face still goes to OD 170.
# In top-down view, looking at the top face, the OD outline visible is broken
# at the notch wedge -- we render the notch as a visible break + radial step
# lines + arc at r=40 (the inner edge of the notch).
import math as _m
_arc_segs = 320

def _ang_in_any(a_rad, wedges_deg):
    """Return True if angle a (rad) falls inside any (start, end) wedge (deg)
    -- handles wedges that wrap through 360 by normalizing to [0, 360)."""
    a_deg = math.degrees(a_rad) % 360
    for (s, e) in wedges_deg:
        s_n = s % 360
        e_n = e % 360
        if s_n <= e_n:
            if s_n <= a_deg <= e_n:
                return True
        else:
            # Wraps: e.g. s=355, e=5 -> in [355,360) U [0,5]
            if a_deg >= s_n or a_deg <= e_n:
                return True
    return False

def draw_arc_with_breaks(ccx, ccy, r, break_wedges_deg, n_seg=320):
    """Draw a circle at (ccx, ccy) radius r, with gaps wherever the angle
    falls in any of the listed (start, end)-degree wedges."""
    segs = []
    pts = []
    for i in range(n_seg + 1):
        a = 2 * _m.pi * i / n_seg
        if _ang_in_any(a, break_wedges_deg):
            if pts:
                segs.append(pts); pts = []
            continue
        # Note: in screen coords, y is flipped (tv uses cy - y)
        pts.append((ccx + r * _m.cos(a), ccy - r * _m.sin(a)))
    if pts: segs.append(pts)
    for seg in segs:
        for i in range(len(seg) - 1):
            pdf.line(seg[i][0], seg[i][1], seg[i+1][0], seg[i+1][1])

# Phi170 base OD: top-face outline is broken in the -45..-40 deg notch wedge.
draw_arc_with_breaks(ccx, ccy, R_BO,
                     [(NOTCH_A_S, NOTCH_A_E)])
# Phi165 rim boss ID: top-face outline is broken at BOTH rim cutout wedges.
draw_arc_with_breaks(ccx, ccy, R_RBI,
                     [(RIM_CUT1_A_S, RIM_CUT1_A_E),
                      (RIM_CUT2_A_S, RIM_CUT2_A_E)])
# Phi170 rim boss OD: same gaps as inner (rim is removed there).
# But the BASE Phi170 OD (drawn above) covers most of this -- however
# in the boss cutout wedge the boss OD is missing AND base OD shows only as
# a partial top-face hint. Since the base OD circle at Phi170 was already
# drawn, the visual is consistent: in the rim cutout wedges (-5..0, -45..-40),
# the rim OD = base OD = Phi170; the base top-face OD is visible there.
# In the -45..-40 notch wedge, both base OD AND rim OD top faces are missing.
# So we redraw the rim OD outline only in the rim cutout wedges so that the
# boss OD "step down" between rim height (10.5) and base top (5) is implied
# (a CAD would show a step edge here -- we simulate it via the inner edge of
# the boss at the cutout boundary, drawn below).

# ----- Radial step edges at each cutout boundary (visible top edges) -----
# Notch (-45..-40 deg, r=40..85 area is missing on top): top-face step edges
# are radial lines at angle = -45 and -40 spanning r in [40, 85] (in the
# notch wedge, the base top face is missing for r>40 on top of base; the
# step is visible at the wedge boundary radials AND at r=40 inside the wedge).
for _ang_d in (NOTCH_A_S, NOTCH_A_E):
    _a = _m.radians(_ang_d)
    _x_in  = ccx + R_NOTCH * _m.cos(_a)
    _y_in  = ccy - R_NOTCH * _m.sin(_a)
    _x_out = ccx + R_BO    * _m.cos(_a)
    _y_out = ccy - R_BO    * _m.sin(_a)
    line(_x_in, _y_in, _x_out, _y_out, GEOM_W)
# Arc inside the notch wedge at r=40 (inner step edge): visible top edge
# along the bottom of the notch step.
pts_arc = []
for i in range(21):
    a_d = NOTCH_A_S + (NOTCH_A_E - NOTCH_A_S) * i / 20
    a = _m.radians(a_d)
    pts_arc.append((ccx + R_NOTCH * _m.cos(a),
                    ccy - R_NOTCH * _m.sin(a)))
for i in range(len(pts_arc) - 1):
    line(pts_arc[i][0], pts_arc[i][1], pts_arc[i+1][0], pts_arc[i+1][1], GEOM_W)

# Rim cutout boss step edges (-5..0 deg and -45..-40 deg): radial step edges
# at each boundary spanning r in [82.5, 85] (the rim boss inner..outer).
for (a_s, a_e) in ((RIM_CUT1_A_S, RIM_CUT1_A_E), (RIM_CUT2_A_S, RIM_CUT2_A_E)):
    for _ang_d in (a_s, a_e):
        _a = _m.radians(_ang_d)
        _x_in  = ccx + R_RBI * _m.cos(_a)
        _y_in  = ccy - R_RBI * _m.sin(_a)
        _x_out = ccx + R_RBO * _m.cos(_a)
        _y_out = ccy - R_RBO * _m.sin(_a)
        line(_x_in, _y_in, _x_out, _y_out, GEOM_W)

# ----- Angle labels for cutouts -----
def _angle_label(ang_d, radial_offset=10):
    a = _m.radians(ang_d)
    lx = ccx + (R_BO + radial_offset) * _m.cos(a)
    ly = ccy - (R_BO + radial_offset) * _m.sin(a)
    text(lx, ly, f"{ang_d:g}°", size=TXT_D, anchor="middle")

# Place 4 angle labels staggered so they don't overlap each other.
# -45 and -40 are 5 deg apart; -5 and 0 are 5 deg apart. Use different
# radial offsets so the 2 in each pair don't collide. The -5 and 0 deg
# labels are kept tight to the disc OD so they don't collide with the
# Section A-A left vdim column (which starts at sa(-R_BO).x - SA_DIM_O2 = 207).
_angle_label(NOTCH_A_S,    radial_offset=11)
_angle_label(NOTCH_A_E,    radial_offset=18)
# -5 deg label below the disc OD, hugging the OD radially.
_a5 = _m.radians(RIM_CUT1_A_S)
text(ccx + (R_BO + 4) * _m.cos(_a5),
     ccy - (R_BO + 4) * _m.sin(_a5) + 7,
     f"{RIM_CUT1_A_S:g}°", size=TXT_D - 0.5, anchor="middle")
# 0 deg label above the disc OD, hugging the OD radially.
_a0 = _m.radians(RIM_CUT1_A_E)
text(ccx + (R_BO + 4) * _m.cos(_a0),
     ccy - (R_BO + 4) * _m.sin(_a0) - 4,
     f"{RIM_CUT1_A_E:g}°", size=TXT_D - 0.5, anchor="middle")

# ----- PCD reference circles (dashed) -----
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(ccx, ccy, INNER_PCD_R, style="D")
pdf.circle(ccx, ccy, OUTER_PCD_R, style="D")
pdf.set_dash_pattern()
_w(GEOM_W)

# ----- 16 Phi3.2 holes (solid circles + crosshairs) -----
def draw_hole(cx, cy, crosshair_r=2.6):
    _w(GEOM_W)
    pdf.circle(cx, cy, M3_DIAM / 2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(cx - crosshair_r, cy, cx + crosshair_r, cy)
    pdf.line(cx, cy - crosshair_r, cx, cy + crosshair_r)
    pdf.set_dash_pattern()
    _w(GEOM_W)

for (x, y) in PATTERN_INNER:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, crosshair_r=3.0)
for (x, y) in PATTERN_OUTER:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, crosshair_r=3.0)

# Vertical centerline (the +X axis is the A-A cut line already drawn)
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(tv(0, -R_BO - 8)[0], tv(0, -R_BO - 8)[1],
         tv(0,  R_BO + 8)[0], tv(0,  R_BO + 8)[1])
pdf.set_dash_pattern()

# ----- Top-view diameter dims (stacked above the disc) -----
hdim(tv(-R_BO,  0)[0], tv(R_BO,  0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O1, f"Φ{BASE_OD:g}")
hdim(tv(-R_RBI, 0)[0], tv(R_RBI, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O2, f"Φ{RIM_ID:g}")
hdim(tv(-R_NOTCH, 0)[0], tv(R_NOTCH, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O3, f"Φ{NOTCH_R_MIN*2:g}")
hdim(tv(-R_BI, 0)[0], tv(R_BI, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O4, f"Φ{BASE_ID:g}")

# ----- Hole-ring diameter dims (stacked below the disc) -----
# Below the disc we also share the y-strip with the rim cutouts callout and
# the title block (y_top = PAGE_H - 32 = 265). So keep the stack tight.
hdim(tv(-INNER_PCD_R, 0)[0], tv(INNER_PCD_R, 0)[0],
     tv(0, -R_BO)[1], tv(0, -R_BO)[1] + 7, f"Φ{INNER_PCD:g} PCD")
hdim(tv(-OUTER_PCD_R, 0)[0], tv(OUTER_PCD_R, 0)[0],
     tv(0, -R_BO)[1], tv(0, -R_BO)[1] + 16, f"Φ{OUTER_PCD:g} PCD")

# ----- Hole-ring callouts -----
_w(EXT_W)

def _closest_hole(pattern, target_deg):
    """Return (x, y) of the hole in pattern whose angle is closest to target."""
    tx = math.cos(math.radians(target_deg))
    ty = math.sin(math.radians(target_deg))
    best = pattern[0]; bestd = -1e9
    for (x, y) in pattern:
        r = math.hypot(x, y)
        if r == 0: continue
        dot = (x * tx + y * ty) / r
        if dot > bestd:
            bestd = dot; best = (x, y)
    return best

# Inner PCD callout - leader from a top-half PCD70 hole, label parked
# to the LEFT-CENTER (away from the dim stacks).
ih_x, ih_y = _closest_hole(PATTERN_INNER, 110)   # upper-left-ish
ih_fx, ih_fy = tv(ih_x, ih_y)
ipcd_label_x = 10
ipcd_label_y = 90
pdf.line(ih_fx, ih_fy, ipcd_label_x + 60, ih_fy)
pdf.line(ipcd_label_x + 60, ih_fy, ipcd_label_x + 60, ipcd_label_y)
pdf.line(ipcd_label_x + 60, ipcd_label_y, ipcd_label_x, ipcd_label_y)
text(ipcd_label_x + 1.5, ipcd_label_y - 1.2,
     f"8 x Φ{M3_DIAM:g} (内圈 PCD Φ{INNER_PCD:g}, 起 22.5°)",
     size=TXT_D, anchor="start")

# Outer PCD callout - leader from a top-half PCD155 hole, label parked
# to the RIGHT-CENTER (top half).
oh_x, oh_y = _closest_hole(PATTERN_OUTER, 70)    # upper-right-ish
oh_fx, oh_fy = tv(oh_x, oh_y)
opcd_label_x = 215
opcd_label_y = 90
pdf.line(oh_fx, oh_fy, opcd_label_x - 60, oh_fy)
pdf.line(opcd_label_x - 60, oh_fy, opcd_label_x - 60, opcd_label_y)
pdf.line(opcd_label_x - 60, opcd_label_y, opcd_label_x, opcd_label_y)
text(opcd_label_x + 1.5, opcd_label_y - 1.2,
     f"8 x Φ{M3_DIAM:g} (外圈 PCD Φ{OUTER_PCD:g}, 起 22.5°)",
     size=TXT_D, anchor="start")

# Notch callout - short label in the strip below-left of the disc, above the
# PCD70 dim line (which spans x in [tv(-35,0)[0], tv(35,0)[0]] = [80, 150]).
# Place the label at (x=5..70, y=246) -- a single line, short.
nh_fx, nh_fy = tv(R_BO * math.cos(math.radians((NOTCH_A_S+NOTCH_A_E)/2)),
                  R_BO * math.sin(math.radians((NOTCH_A_S+NOTCH_A_E)/2)))
nh_label_x = 7
nh_label_y = 246
# Short leader: feature -> kink horizontally clear of disc -> label
pdf.line(nh_fx, nh_fy, nh_fx, nh_label_y - 4)
pdf.line(nh_fx, nh_label_y - 4, nh_label_x + 60, nh_label_y - 4)
pdf.line(nh_label_x + 60, nh_label_y - 4, nh_label_x, nh_label_y)
text(nh_label_x + 1.5, nh_label_y - 1.2,
     f"基环切口: r>{NOTCH_R_MIN:g} / {NOTCH_A_S:g}°~{NOTCH_A_E:g}° / Z={NOTCH_Z_S:g}~{NOTCH_Z_E:g}",
     size=TXT_D, anchor="start")

# Rim boss cutouts callout - short label in the strip below-right of the disc.
rc_fx, rc_fy = tv(R_RBO * math.cos(math.radians((RIM_CUT1_A_S+RIM_CUT1_A_E)/2)),
                  R_RBO * math.sin(math.radians((RIM_CUT1_A_S+RIM_CUT1_A_E)/2)))
rc_label_x = 160
rc_label_y = 246
pdf.line(rc_fx, rc_fy, rc_fx, rc_label_y - 4)
pdf.line(rc_fx, rc_label_y - 4, rc_label_x - 8, rc_label_y - 4)
pdf.line(rc_label_x - 8, rc_label_y - 4, rc_label_x, rc_label_y)
text(rc_label_x + 1.5, rc_label_y - 1.2,
     f"凸圈切口: {RIM_CUT1_A_S:g}°~{RIM_CUT1_A_E:g}° + {RIM_CUT2_A_S:g}°~{RIM_CUT2_A_E:g}°",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
# sa_t_zero_x chosen so the left dims clear top view's right edge (200) and
# the right dims stay inside the page right margin (~415). We use compact
# dim offsets dedicated to the section views (SA_DIM_*) below.
SA_DIM_O1 = 10.0
SA_DIM_O2 = 18.0
sa_t_zero_x = 310
sa_z_zero_y = 165
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 50, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
_sec_a_note = ("(沿 +X 轴剖切 / cut along the X axis at 0°"
               "; PCD 环形孔已旋转 22.5°, 不在剖切面上)")
text(sa_t_zero_x, 57, _sec_a_note, size=TXT_I, anchor="middle")

_w(GEOM_W)

# Geometry: Section A-A along X axis. The +X cut at 0 deg DOES pass through
# the rim-boss cutout (-5..0), so at +t in [R_RBI, R_RBO]=[82.5, 85] the rim
# boss is ABSENT on the +X side (cut wedge straddles +X to -5).
# On the -X side (cutting plane = -180 deg = 180 deg), the rim boss IS
# present. So the section is asymmetric.
#
# Material profile at radial t (t = X):
#   t in [-85, -82.5]: base (Z=0..5) + rim (Z=5..10.5)    [solid rim]
#   t in [-82.5, -30]: base only (Z=0..5)
#   t in (-30, 30):    void (inner hole)
#   t in (30, 82.5):   base only (Z=0..5)
#   t in [82.5, 85]:   base (Z=0..5) ONLY (rim ABSENT because the +X cut at
#                                            0 deg is right inside the
#                                            -5..0 boss cutout)
#
# But wait -- the cut is AT 0 deg; the cutout wedge is -5..0 deg. The cut
# plane is the X axis. Material visible at +X side of the cut at radius
# r=83 is what exists at angle EXACTLY 0 deg. At 0 deg, we're at the
# boundary of the wedge -5..0. So technically at 0 deg the cut is right on
# the edge. To make the section meaningful and to match the user spec saying
# "rim boss on top of base from r=82.5..85 at Z=5..10.5" -- which assumes
# both sides have the boss -- the standard approach is to cut at a tiny
# offset INSIDE 0 deg (say 0.01 deg), where the rim IS present. So treat
# the rim as present on BOTH sides.
#
# (Per spec: "Section A-A ... rim boss on top of base from r=82.5..85 at
# Z=5..10.5". So both sides show rim.)

# Section profile - right half (positive t):
#   - top of base from (0, Z1) to (R_RBI, Z1)
#   - rim boss inner wall up: (R_RBI, Z1) to (R_RBI, Z2)
#   - top of rim boss: (R_RBI, Z2) to (R_RBO, Z2)
#   - outer wall down: (R_RBO, Z2) to (R_RBO, Z0)
#   - bottom of base from (R_RBO, Z0) to (R_BI, Z0)
#   - inner wall up: (R_BI, Z0) to (R_BI, Z1)
#   - top of base back to start.

# Right half
line(*sa(R_BI,  Z1), *sa(R_RBI, Z1), GEOM_W)     # top of base
line(*sa(R_RBI, Z1), *sa(R_RBI, Z2), GEOM_W)     # rim boss inner wall
line(*sa(R_RBI, Z2), *sa(R_RBO, Z2), GEOM_W)     # top of rim boss
line(*sa(R_RBO, Z2), *sa(R_RBO, Z0), GEOM_W)     # outer wall
line(*sa(R_BI,  Z0), *sa(R_BI,  Z1), GEOM_W)     # inner wall

# Left half (mirror)
line(*sa(-R_BI,  Z1), *sa(-R_RBI, Z1), GEOM_W)
line(*sa(-R_RBI, Z1), *sa(-R_RBI, Z2), GEOM_W)
line(*sa(-R_RBI, Z2), *sa(-R_RBO, Z2), GEOM_W)
line(*sa(-R_RBO, Z2), *sa(-R_RBO, Z0), GEOM_W)
line(*sa(-R_BI,  Z0), *sa(-R_BI,  Z1), GEOM_W)

# Bottom of base - drawn from -OD to -ID and ID to OD (skip the central hole).
# The Phi155 PCD holes at t=+/-77.5 are NOT on the X axis (they're at
# 22.5 deg from X), so they don't appear in section A-A. No hole gaps.
line(*sa(-R_RBO, 0), *sa(-R_BI, 0), GEOM_W)
line(*sa( R_BI,  0), *sa( R_RBO, 0), GEOM_W)

# ----- Section A-A dimensions -----
# LEFT side: stack base 5 / rim 5.5 / total 10.5 vertically with compact
# offsets. Left dim x-positions: sa(-R_BO).x - SA_DIM_O1 (=300) and
# sa(-R_BO).x - SA_DIM_O2 (=292) -- both clear of the top-view disc OD at
# x = tv_cx + R_BO = 200, with a 92mm buffer.
left_x1 = sa(-R_BO, 0)[0] - SA_DIM_O1
left_x2 = sa(-R_BO, 0)[0] - SA_DIM_O2
vdim(sa(0, Z1)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_x1, f"{BASE_H:g}")
vdim(sa(0, Z2)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_x2, f"{TOTAL_H:g}")

# Top horizontal dims (stacked above) - 3 diameter stacks at SA_DIM_O1/O2/3rd.
SA_TOP_O1 = 10.0
SA_TOP_O2 = 20.0
SA_TOP_O3 = 30.0
top_y1 = sa(0, Z2)[1] - SA_TOP_O1
hdim(sa(-R_BI, 0)[0], sa(R_BI, 0)[0],
     sa(0, Z2)[1], top_y1, f"Φ{BASE_ID:g}")
top_y2 = sa(0, Z2)[1] - SA_TOP_O2
hdim(sa(-R_RBI, 0)[0], sa(R_RBI, 0)[0],
     sa(0, Z2)[1], top_y2, f"Φ{RIM_ID:g}")
top_y3 = sa(0, Z2)[1] - SA_TOP_O3
hdim(sa(-R_RBO, 0)[0], sa(R_RBO, 0)[0],
     sa(0, Z2)[1], top_y3, f"Φ{BASE_OD:g}")

# Right-side vdim for rim boss height (5.5)
vdim(sa(0, Z2)[1], sa(0, Z1)[1],
     sa(R_BO, 0)[0], sa(R_BO, 0)[0] + SA_DIM_O1, f"{RIM_H:g}")

# ===== SECTION B-B (1:1) along -42.5 deg radial =====
# This cut passes through the notch wedge (-45..-40 deg) on the +radial side
# at angle -42.5 deg, and at angle 180-42.5 = 137.5 deg on the -radial side
# (no cutouts at 137.5 deg, so left half is the intact section).
sb_t_zero_x = 310
sb_z_zero_y = 240
def sb(t, z): return (sb_t_zero_x + t, sb_z_zero_y - z)

text(sb_t_zero_x, 195, "剖视图  Section B-B  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
_sec_b_note = (f"(沿 {SECTION_BB_ANGLE:g}° 径向剖切 / cut along the {SECTION_BB_ANGLE:g}° radial; "
               "+t 通过基环切口和凸圈切口; -t 为完整段)")
text(sb_t_zero_x, 201, _sec_b_note, size=TXT_I, anchor="middle")

_w(GEOM_W)
# Right half (+t side) at -42.5 deg: inside the notch wedge AND inside the
# rim cutout 2 (-45..-40). So material at +t:
#   t in [R_BI=30, R_NOTCH=40]: base (Z=0..5) intact
#   t in [R_NOTCH=40, R_RBO=85]: base only from Z=0..2.5 (the notch step;
#                                   r>40 is removed at Z=2.5..5),
#                                no rim boss (-45..-40 is also a rim cutout)
# Right half outline (going from origin outward):
#   top of base at r in [30, 40]: from (R_BI, Z1) to (R_NOTCH, Z1)
#   notch step down: (R_NOTCH, Z1) to (R_NOTCH, Z_NOTCH)
#   notch floor: (R_NOTCH, Z_NOTCH) to (R_RBO, Z_NOTCH)
#   outer wall down: (R_RBO, Z_NOTCH) to (R_RBO, Z0)
#   bottom across to inner: (R_RBO, Z0) to (R_BI, Z0)
#   inner wall up: (R_BI, Z0) to (R_BI, Z1)

line(*sb(R_BI,    Z1),       *sb(R_NOTCH, Z1),       GEOM_W)
line(*sb(R_NOTCH, Z1),       *sb(R_NOTCH, Z_NOTCH),  GEOM_W)
line(*sb(R_NOTCH, Z_NOTCH),  *sb(R_RBO,   Z_NOTCH),  GEOM_W)
line(*sb(R_RBO,   Z_NOTCH),  *sb(R_RBO,   Z0),       GEOM_W)
line(*sb(R_RBO,   Z0),       *sb(R_BI,    Z0),       GEOM_W)
line(*sb(R_BI,    Z0),       *sb(R_BI,    Z1),       GEOM_W)

# Left half (-t side at 137.5 deg): no cutouts. Full base + rim boss.
line(*sb(-R_BI,  Z1), *sb(-R_RBI, Z1), GEOM_W)
line(*sb(-R_RBI, Z1), *sb(-R_RBI, Z2), GEOM_W)
line(*sb(-R_RBI, Z2), *sb(-R_RBO, Z2), GEOM_W)
line(*sb(-R_RBO, Z2), *sb(-R_RBO, Z0), GEOM_W)
line(*sb(-R_RBO, Z0), *sb(-R_BI,  Z0), GEOM_W)
line(*sb(-R_BI,  Z0), *sb(-R_BI,  Z1), GEOM_W)

# ----- Section B-B dimensions -----
# Z heights: notch step Z=2.5 on the +t side (vdim on right outer)
SB_DIM_O1 = 10.0
SB_DIM_O2 = 18.0
vdim(sb(0, Z_NOTCH)[1], sb(0, Z0)[1],
     sb(R_BO, 0)[0], sb(R_BO, 0)[0] + SB_DIM_O1, f"{Z_NOTCH:g}")
vdim(sb(0, Z1)[1], sb(0, Z_NOTCH)[1],
     sb(R_BO, 0)[0], sb(R_BO, 0)[0] + SB_DIM_O2, f"{Z1-Z_NOTCH:g}")
# Total height on the LEFT side
vdim(sb(0, Z2)[1], sb(0, Z0)[1],
     sb(-R_BO, 0)[0], sb(-R_BO, 0)[0] - SB_DIM_O1, f"{TOTAL_H:g}")
# Notch radial start (r=40) horizontal dim above the cut on the +t side
mid_y = sb(0, Z2)[1] - SB_DIM_O1
hdim(sb(0, 0)[0], sb(R_NOTCH, 0)[0],
     sb(0, Z1)[1], mid_y, f"r={NOTCH_R_MIN:g}")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 外缘环 (Rim Ring)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖 A-A, 剖 B-B)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_OD:g}/Φ{BASE_ID:g}xH{BASE_H:g} 基环 "
     f"(切口 r>{NOTCH_R_MIN:g} / {NOTCH_A_S:g}°~{NOTCH_A_E:g}° / Z={NOTCH_Z_S:g}~{NOTCH_Z_E:g}) / "
     f"Φ{RIM_OD:g}/Φ{RIM_ID:g}xH{RIM_H:g} 外凸圈 "
     f"(切口 {RIM_CUT1_A_S:g}°~{RIM_CUT1_A_E:g}° + {RIM_CUT2_A_S:g}°~{RIM_CUT2_A_E:g}°) / "
     f"16xΦ{M3_DIAM:g} (8 内PCD Φ{INNER_PCD:g} + 8 外PCD Φ{OUTER_PCD:g}, 起 22.5°)  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-08  /  POV3D / models / rim_ring / rim_ring.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("rim_ring_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("rim_ring_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
