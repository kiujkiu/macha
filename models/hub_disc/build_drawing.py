"""
Generate a 2D engineering drawing (PDF, A3 landscape) for the POV3D hub disc.

Views:
  1) TOP VIEW       (俯视图, 1:1)    — all 4 outline circles (Φ165, Φ145, Φ80,
                                       Φ60), diamond (12×15) outline, square
                                       30×30 outline, both PCD circles (Φ70,
                                       Φ155), all 24 holes shown as Φ3.2 solid
                                       circle + dashed Φ7 or Φ4.2 CB (CB
                                       hidden from top), and a crosshair.
  2) SECTION A-A    (剖视图 A-A, 1:1) — cut along +X axis (0°), passes through:
                                       diamond holes at (±6, 0),
                                       PCD-70 holes at (±35, 0),
                                       PCD-155 holes at (±77.5, 0).
                                       Shows 3-step Z structure: base 3, lower
                                       center boss step at Z=5.5 (Φ80), upper
                                       boss step at Z=9 (Φ60), rim boss
                                       between Z=3..5.5 at R=72.5..82.5, and
                                       the stepped hole profiles.
  3) DETAIL B       (详图 B, 4:1)    — M3 + Φ7 × 4 CB stack (diamond holes).
  4) DETAIL C       (详图 C, 4:1)    — M3 + Φ4.2 × 4 CB stack (the other 20).
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
BASE_OD       = 165.0
BASE_T        = 3.0

LOWER_BOSS_D  = 80.0
LOWER_BOSS_T  = 2.5

UPPER_BOSS_D  = 60.0
UPPER_BOSS_T  = 3.5

RIM_BOSS_ID   = 145.0
RIM_BOSS_OD   = 165.0
RIM_BOSS_T    = 2.5

RIM_CUTOUT_A_S = 0.0    # 外凸圈切口起始角
RIM_CUTOUT_A_E = 5.0    # 外凸圈切口结束角

TOTAL_H = BASE_T + LOWER_BOSS_T + UPPER_BOSS_T   # 9

M3_DIAM   = 3.2
CB_A_DIAM = 7.0
CB_B_DIAM = 4.2
CB_DEPTH  = 4.0

# Center counterbore — Φ6.2 × 2.2 mm pocket, opens from BOTTOM face at (0,0).
# No through-hole, pocket only.
CENTER_CB_DIAM  = 6.2
CENTER_CB_DEPTH = 2.2

DIAG_X = 12.0
DIAG_Y = 15.0
SQUARE_SIDE = 30.0
INNER_PCD_R = 35.0
INNER_PCD   = 2 * INNER_PCD_R    # 70
OUTER_PCD_R = 77.5
OUTER_PCD   = 2 * OUTER_PCD_R    # 155

# Angular rotation (degrees, CCW positive) applied to BOTH PCD ring patterns
# (PCD70 and PCD155). The 4 diamond holes and 4 square holes are NOT rotated.
# Must match the same parameter in build_stl.py / hub_disc.scad.
RING_HOLE_ROTATION = 22.5

# Convenience radii
R_BO        = BASE_OD / 2        # 82.5
R_LBO       = LOWER_BOSS_D / 2   # 40.0
R_UBO       = UPPER_BOSS_D / 2   # 30.0
R_RBI       = RIM_BOSS_ID / 2    # 72.5
R_RBO       = RIM_BOSS_OD / 2    # 82.5

# Z levels
Z0 = 0.0
Z1 = BASE_T                                  # 3.0
Z2 = BASE_T + LOWER_BOSS_T                   # 5.5
Z3 = TOTAL_H                                 # 9.0

# Pattern A — diamond
PATTERN_A = [( DIAG_X/2, 0.0), (-DIAG_X/2, 0.0),
             ( 0.0,  DIAG_Y/2), (0.0, -DIAG_Y/2)]
# Pattern B — square
PATTERN_B = [( SQUARE_SIDE/2,  SQUARE_SIDE/2),
             (-SQUARE_SIDE/2,  SQUARE_SIDE/2),
             ( SQUARE_SIDE/2, -SQUARE_SIDE/2),
             (-SQUARE_SIDE/2, -SQUARE_SIDE/2)]
# Pattern C — inner PCD Φ70, rotated by RING_HOLE_ROTATION
PATTERN_C = [(INNER_PCD_R * math.cos(math.radians(k * 45 + RING_HOLE_ROTATION)),
              INNER_PCD_R * math.sin(math.radians(k * 45 + RING_HOLE_ROTATION)))
             for k in range(8)]
# Pattern D — outer PCD Φ155, rotated by RING_HOLE_ROTATION
PATTERN_D = [(OUTER_PCD_R * math.cos(math.radians(k * 45 + RING_HOLE_ROTATION)),
              OUTER_PCD_R * math.sin(math.radians(k * 45 + RING_HOLE_ROTATION)))
             for k in range(8)]

# Angular positions of PCD-ring holes after rotation (degrees from +X axis).
PCD_HOLE_ANGLES = [k * 45 + RING_HOLE_ROTATION for k in range(8)]

def pcd_hole_on_x_axis(tol_deg=1e-3):
    """Return list of (signed_radial_distance) on the X axis for a given PCD
    radius — empty if RING_HOLE_ROTATION puts no hole on the 0°/180° line."""
    hits = []
    for a in PCD_HOLE_ANGLES:
        am = a % 360
        if abs(am) < tol_deg or abs(am - 360) < tol_deg:
            hits.append(+1)
        elif abs(am - 180) < tol_deg:
            hits.append(-1)
    return hits

PCD_RINGS_ON_X_AXIS = bool(pcd_hole_on_x_axis())

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
text(PAGE_W/2, 13, "POV 3D 轴座盘  Hub Disc", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19,
     f"基盘 Φ{BASE_OD:g}×{BASE_T:g} / 下凸台 Φ{LOWER_BOSS_D:g}×{LOWER_BOSS_T:g} / "
     f"上凸台 Φ{UPPER_BOSS_D:g}×{UPPER_BOSS_T:g} / 外缘凸圈 Φ{RIM_BOSS_OD:g}/Φ{RIM_BOSS_ID:g}×{RIM_BOSS_T:g} (切口 {RIM_CUTOUT_A_S:g}°–{RIM_CUTOUT_A_E:g}°) / "
     f"24×Φ{M3_DIAM:g} M3 + Φ{CB_A_DIAM:g} 沉孔 (顶面, 菱形) + Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔 (底面, 其余) + 中心 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔 (底面)",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 110, 158
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 30, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Section A-A cutting line — along +X (0° / 180°)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
end1 = tv( R_BO + 14, 0)
end2 = tv(-R_BO - 14, 0)
pdf.line(end1[0], end1[1], end2[0], end2[1])
pdf.set_dash_pattern()
text(end1[0] + 2, end1[1] + 4, "A", size=6)
text(end2[0] - 7, end2[1] + 4, "A", size=6)

# ---- Geometry circles ----
_w(GEOM_W)
ccx, ccy = tv(0, 0)
pdf.circle(ccx, ccy, R_BO,  style="D")   # Φ165 base OD (intact — base under cutout)
pdf.circle(ccx, ccy, R_LBO, style="D")   # Φ80 lower boss OD
pdf.circle(ccx, ccy, R_UBO, style="D")   # Φ60 upper boss OD
# Center Φ6.2 counterbore — hidden from top (opens on bottom face), so dashed.
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
pdf.circle(ccx, ccy, CENTER_CB_DIAM / 2, style="D")
pdf.set_dash_pattern()
_w(GEOM_W)
# Φ145 rim boss ID — drawn as an arc with a gap at the cutout angular range
import math as _m
_arc_segs = 240
_a_start_skip = _m.radians(RIM_CUTOUT_A_S)
_a_end_skip   = _m.radians(RIM_CUTOUT_A_E)
def _ang_in_cutout(a):
    return _a_start_skip <= (a % (2 * _m.pi)) <= _a_end_skip
_arc_pts = []
for _i in range(_arc_segs + 1):
    _a = 2 * _m.pi * _i / _arc_segs
    if _ang_in_cutout(_a):
        if _arc_pts:
            for _k in range(len(_arc_pts) - 1):
                pdf.line(_arc_pts[_k][0], _arc_pts[_k][1],
                         _arc_pts[_k+1][0], _arc_pts[_k+1][1])
            _arc_pts = []
        continue
    _arc_pts.append((ccx + R_RBI * _m.cos(_a),
                     ccy - R_RBI * _m.sin(_a)))
for _k in range(len(_arc_pts) - 1):
    pdf.line(_arc_pts[_k][0], _arc_pts[_k][1],
             _arc_pts[_k+1][0], _arc_pts[_k+1][1])
# Radial step edges where the boss wall ends at the cutout (visible top edges)
for _ang_d in (RIM_CUTOUT_A_S, RIM_CUTOUT_A_E):
    _a = _m.radians(_ang_d)
    _x_in  = ccx + R_RBI * _m.cos(_a)
    _y_in  = ccy - R_RBI * _m.sin(_a)
    _x_out = ccx + R_BO  * _m.cos(_a)
    _y_out = ccy - R_BO  * _m.sin(_a)
    pdf.line(_x_in, _y_in, _x_out, _y_out)
# Angular dim labels for cutout (just outside the OD)
for _ang_d in (RIM_CUTOUT_A_S, RIM_CUTOUT_A_E):
    _a = _m.radians(_ang_d)
    _lx = ccx + (R_BO + 8) * _m.cos(_a)
    _ly = ccy - (R_BO + 8) * _m.sin(_a)
    text(_lx, _ly, f"{_ang_d:g}°", size=TXT_D, anchor="middle")

# ---- PCD reference circles (dashed) for inner PCD Φ70 and outer PCD Φ155 ----
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(ccx, ccy, INNER_PCD_R, style="D")
pdf.circle(ccx, ccy, OUTER_PCD_R, style="D")
pdf.set_dash_pattern()
_w(GEOM_W)

# ---- Diamond outline (light dashed) and square outline (dashed) ----
pdf.set_dash_pattern(dash=2, gap=1.2); _w(0.18)
# Diamond polyline: through the 4 vertices
d_pts = [tv(p[0], p[1]) for p in
         [(DIAG_X/2, 0), (0, DIAG_Y/2), (-DIAG_X/2, 0), (0, -DIAG_Y/2), (DIAG_X/2, 0)]]
for i in range(len(d_pts) - 1):
    pdf.line(*d_pts[i], *d_pts[i+1])
# Square
s_pts = [tv(p[0], p[1]) for p in
         [( SQUARE_SIDE/2,  SQUARE_SIDE/2), (-SQUARE_SIDE/2,  SQUARE_SIDE/2),
          (-SQUARE_SIDE/2, -SQUARE_SIDE/2), ( SQUARE_SIDE/2, -SQUARE_SIDE/2),
          ( SQUARE_SIDE/2,  SQUARE_SIDE/2)]]
for i in range(len(s_pts) - 1):
    pdf.line(*s_pts[i], *s_pts[i+1])
pdf.set_dash_pattern()
_w(GEOM_W)

# ---- Holes (24 total) ----
def draw_hole(cx, cy, cb_diam, crosshair_r=2.6, cb_visible_from_top=False):
    # M3 through-hole — solid Φ3.2 (always visible, goes all the way through)
    pdf.circle(cx, cy, M3_DIAM/2, style="D")
    # CB: solid if it opens on the TOP face (visible from above),
    # dashed if it opens on the BOTTOM face (hidden from top).
    if cb_visible_from_top:
        _w(GEOM_W)
        pdf.circle(cx, cy, cb_diam/2, style="D")
    else:
        pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
        pdf.circle(cx, cy, cb_diam/2, style="D")
        pdf.set_dash_pattern()
    # tiny crosshair
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(cx - crosshair_r, cy, cx + crosshair_r, cy)
    pdf.line(cx, cy - crosshair_r, cx, cy + crosshair_r)
    pdf.set_dash_pattern()
    _w(GEOM_W)

# Diamond holes — CB now opens from the TOP, so it's VISIBLE (solid circle).
for (x, y) in PATTERN_A:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, CB_A_DIAM, crosshair_r=4.0, cb_visible_from_top=True)
# All other 20 holes — CB opens from the BOTTOM, so still dashed from top.
for (x, y) in PATTERN_B:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, CB_B_DIAM, crosshair_r=2.8)
for (x, y) in PATTERN_C:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, CB_B_DIAM, crosshair_r=2.8)
for (x, y) in PATTERN_D:
    cx, cy = tv(x, y)
    draw_hole(cx, cy, CB_B_DIAM, crosshair_r=2.8)

# Center cross (axis lines) — dashed
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
# (Section line already covers horizontal axis; add a vertical centerline.)
pdf.line(tv(0, -R_BO - 8)[0], tv(0, -R_BO - 8)[1],
         tv(0,  R_BO + 8)[0], tv(0,  R_BO + 8)[1])
pdf.set_dash_pattern()

# ---- Diamond diagonal dims (12 horizontal, 15 vertical) ----
# SHORT labels placed inside the diamond region (using the helper to append mm).
# X = 12 horizontally between the two diamond vertices at (±6, 0); since the
# diamond is tiny, drop the label just below the horizontal axis using a short
# leader to the right gutter.
_w(EXT_W)
# Horizontal "12" — short label inside, slightly above the X axis between the
# left and right diamond vertices. The two vertices are at (±6, 0), so 12mm
# wide. Place text at (-3, 2) just above the X axis inside the diamond.
text(*tv(0, 2.5), f"{DIAG_X:g}", size=TXT_D - 0.5, anchor="middle")
# Vertical "15" — short label to the right of the Y axis inside the diamond.
text(*tv(2.5, -1.0), f"{DIAG_Y:g}", size=TXT_D - 0.5, anchor="start")
# Tiny diagonal indicator lines inside the diamond
pdf.set_dash_pattern(dash=1, gap=0.8); _w(0.12)
pdf.line(*tv(-DIAG_X/2 + 0.5, 0), *tv(DIAG_X/2 - 0.5, 0))
pdf.line(*tv(0, -DIAG_Y/2 + 0.5), *tv(0, DIAG_Y/2 - 0.5))
pdf.set_dash_pattern()

# ---- Four feature callouts, spread to the FOUR cardinal directions
# outside the disc OD so each takes its own quadrant. The top-view disc
# bbox is x ∈ [27.5, 192.5], y ∈ [75.5, 240.5].
#
# Each LEADER is routed in the direction of the matching cardinal so the
# four callouts visually fan outward from the disc center to one of the
# four "compass corners" of the page:
#   N (top-left  corner): 4 × Φ7 diamond CB (顶面) — leader from N diamond vertex
#   E (top-right edge):   4 × Φ4.2 square (方形) — leader from NE square corner
#   S (bottom-right):     8 × Φ4.2 PCD70 inner ring — leader from S-most PCD70 hole
#   W (bottom-left):      8 × Φ4.2 PCD155 outer ring — leader from W-most PCD155 hole

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

# ---- NORTH-WEST corner: 4 × Φ7 diamond CB (顶面) ----
# Label parked at top-left of disc, ABOVE the disc but BELOW the page
# subtitle. y_label=24 is just below the page subtitle (y≈19). To stay
# out of the dim-stack arrows (x ≈ [15..30]) we tuck the label further left.
# Leader: from N diamond vertex (0, +7.5) going NW diagonally outside disc.
nf_x, nf_y = tv(0, DIAG_Y/2)
nw_label_x = 8
nw_label_y = 24
# Single diagonal-then-horizontal leader: feature -> off-disc NW corner -> right to label
nw_kink_x = tv(-90, 0)[0]
nw_kink_y = nw_label_y
pdf.line(nf_x, nf_y, nw_kink_x, nw_kink_y)
pdf.line(nw_kink_x, nw_kink_y, nw_label_x, nw_label_y)
text(nw_label_x + 1.5, nw_label_y - 1.2,
     f"4 × Φ{M3_DIAM:g} + Φ{CB_A_DIAM:g}×{CB_DEPTH:g} 沉孔 (菱形, 顶面)",
     size=TXT_D, anchor="start")

# ---- NORTH-EAST corner: 4 × Φ4.2 square (方形) ----
# Label parked at the top-right above the disc but BELOW the section title.
# Section A-A title sits at y=50,57 and dim stacks for section start at y=65.
# So the band y ≈ [22, 48] is clear above the disc-right area.
ef_x, ef_y = tv(SQUARE_SIDE/2, SQUARE_SIDE/2)
ne_label_y = 24
ne_label_x = 215
ne_kink_x = tv(90, 0)[0]
ne_kink_y = ne_label_y
pdf.line(ef_x, ef_y, ne_kink_x, ne_kink_y)
pdf.line(ne_kink_x, ne_kink_y, ne_label_x, ne_label_y)
text(ne_label_x + 1.5, ne_label_y - 1.2,
     f"4 × Φ{M3_DIAM:g} + Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔 (方形 {SQUARE_SIDE:g}×{SQUARE_SIDE:g})",
     size=TXT_D, anchor="start")

# ---- SOUTH-EAST corner: 8 × Φ4.2 PCD70 inner ring ----
# Label parked BELOW the disc on the right half (so the W callout has room
# on the left half of the strip).
iy_x, iy_y = _closest_hole(PATTERN_C, -90)
sf_x, sf_y = tv(iy_x, iy_y)
se_label_x = tv(8, 0)[0]
se_label_y = 252
se_kink_x = tv(8, 0)[0]
pdf.line(sf_x, sf_y, sf_x, sf_y + 6)
pdf.line(sf_x, sf_y + 6, se_kink_x, se_label_y)
pdf.line(se_kink_x, se_label_y, se_label_x, se_label_y)
text(se_label_x + 1.5, se_label_y - 1.2,
     f"8 × Φ{M3_DIAM:g} + Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔 (内圈 PCD Φ{INNER_PCD:g})",
     size=TXT_D, anchor="start")

# ---- SOUTH-WEST corner: 8 × Φ4.2 PCD155 outer ring ----
# Label parked BELOW the disc on the left half of the bottom strip.
ow_x, ow_y = _closest_hole(PATTERN_D, 180)
wf_x, wf_y = tv(ow_x, ow_y)
sw_label_x = 10
sw_label_y = 263
sw_kink_x = tv(-95, 0)[0]
pdf.line(wf_x, wf_y, sw_kink_x, wf_y)
pdf.line(sw_kink_x, wf_y, sw_kink_x, sw_label_y)
pdf.line(sw_kink_x, sw_label_y, sw_label_x, sw_label_y)
text(sw_label_x + 1.5, sw_label_y - 1.2,
     f"8 × Φ{M3_DIAM:g} + Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔 (外圈 PCD Φ{OUTER_PCD:g})",
     size=TXT_D, anchor="start")

# ---- Top-view diameter dims (stacked above the disc) ----
hdim(tv(-R_BO,  0)[0], tv(R_BO,  0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O1, f"Φ{BASE_OD:g}")
hdim(tv(-R_RBI, 0)[0], tv(R_RBI, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O2, f"Φ{RIM_BOSS_ID:g}")
hdim(tv(-R_LBO, 0)[0], tv(R_LBO, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - DIM_O3, f"Φ{LOWER_BOSS_D:g}")
hdim(tv(-R_UBO, 0)[0], tv(R_UBO, 0)[0],
     tv(0, R_BO)[1], tv(0, R_BO)[1] - (DIM_O3 + 12), f"Φ{UPPER_BOSS_D:g}")

# ===== SECTION A-A (1:1) =====
sa_t_zero_x = 295
sa_z_zero_y = 175
def sa(t, z): return (sa_t_zero_x + t, sa_z_zero_y - z)

text(sa_t_zero_x, 50, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
_sec_note = ("(沿 +X 轴剖切 / cut along the X axis at 0°"
             f"; PCD 环形孔已旋转 {RING_HOLE_ROTATION:g}° CCW, 不在剖切面上)")
text(sa_t_zero_x, 57, _sec_note, size=TXT_I, anchor="middle")

_w(GEOM_W)

# Section: cut along +X, so "t" = X. Holes intersected:
#   diamond at t = ±DIAG_X/2 = ±6     (CB Φ7,   M3 Φ3.2)
#   PCD-70  at t = ±35                (CB Φ4.2, M3 Φ3.2)
#   PCD-155 at t = ±77.5              (CB Φ4.2, M3 Φ3.2)
# Note: square holes at (±15, ±15) are NOT on the X axis, so they don't appear
# in section A-A.
#
# Material at each radius t (looking radially):
#   |t| <= R_UBO=30           -> material from Z=0 to Z=9 (base + lower + upper)
#   R_UBO=30 < |t| <= R_LBO=40 -> material from Z=0 to Z=5.5 (base + lower)
#   R_LBO=40 < |t| < R_RBI=72.5 -> material from Z=0 to Z=3 (base only)
#   R_RBI=72.5 <= |t| <= R_BO=82.5 -> material at Z=0..3 (base) AND Z=3..5.5 (rim boss)
#                                     (the rim boss sits on top of the base in this band)
#
# So the OUTLINE of the section on the right (+t) is, starting from t=0,Z=Z3 going CW:
#   - top of upper boss: horiz from (0, Z3) to (R_UBO, Z3)
#   - upper boss outer wall down: from (R_UBO, Z3) to (R_UBO, Z2)
#   - top of lower boss: horiz from (R_UBO, Z2) to (R_LBO, Z2)
#   - lower boss outer wall down: from (R_LBO, Z2) to (R_LBO, Z1)
#   - top of base (between lower boss and rim boss): from (R_LBO, Z1) to (R_RBI, Z1)
#   - rim boss inner wall up: from (R_RBI, Z1) to (R_RBI, Z2)
#   - top of rim boss: from (R_RBI, Z2) to (R_RBO, Z2)
#   - outer wall of base+rim down: from (R_RBO, Z2) to (R_RBO, Z0) [= R_BO]
#   - bottom of base: from (R_RBO, Z0) back to (0, Z0)
# Mirror on the -t side.

# Top outline (right half)
line(*sa(0,     Z3), *sa(R_UBO, Z3), GEOM_W)        # top of upper boss
line(*sa(R_UBO, Z3), *sa(R_UBO, Z2), GEOM_W)        # upper boss side
line(*sa(R_UBO, Z2), *sa(R_LBO, Z2), GEOM_W)        # top of lower boss
line(*sa(R_LBO, Z2), *sa(R_LBO, Z1), GEOM_W)        # lower boss side
line(*sa(R_LBO, Z1), *sa(R_RBI, Z1), GEOM_W)        # top of base (gap between lower & rim)
line(*sa(R_RBI, Z1), *sa(R_RBI, Z2), GEOM_W)        # rim boss inner wall
line(*sa(R_RBI, Z2), *sa(R_RBO, Z2), GEOM_W)        # top of rim boss
line(*sa(R_RBO, Z2), *sa(R_RBO, Z0), GEOM_W)        # outer wall (rim+base)
# bottom of base (right half) — interrupted by CBs (handled later as gap subtraction)
# Top outline (left half — mirror)
line(*sa(0,      Z3), *sa(-R_UBO, Z3), GEOM_W)
line(*sa(-R_UBO, Z3), *sa(-R_UBO, Z2), GEOM_W)
line(*sa(-R_UBO, Z2), *sa(-R_LBO, Z2), GEOM_W)
line(*sa(-R_LBO, Z2), *sa(-R_LBO, Z1), GEOM_W)
line(*sa(-R_LBO, Z1), *sa(-R_RBI, Z1), GEOM_W)
line(*sa(-R_RBI, Z1), *sa(-R_RBI, Z2), GEOM_W)
line(*sa(-R_RBI, Z2), *sa(-R_RBO, Z2), GEOM_W)
line(*sa(-R_RBO, Z2), *sa(-R_RBO, Z0), GEOM_W)

# ---- Hole profile drawing ----
# Each hole creates a void:
#   CB (diam = cb_d) from z=0 to z=CB_DEPTH=4
#   M3 (diam = M3) from z=CB_DEPTH to whatever material top exists
# In our section the material top at hole t0 is:
#   diamond hole at t=±6:   top is Z3=9 (upper boss covers it)
#   PCD-70 hole at t=±35:   top is Z2=5.5 (lower boss covers it; upper boss outer R=30 < 35)
#   PCD-155 hole at t=±77.5: top is Z2=5.5 (rim boss covers it; 72.5..82.5 band)
# The CB cuts the bottom face from Z=0 up to Z=4 (so 1mm into the material above
# the base at t=±6 and t=±35 and t=±77.5). The M3 then goes from Z=4 to the
# top of the material at that radius.

def hole_top_z(t0):
    a = abs(t0)
    if a <= R_UBO:  return Z3   # upper boss
    if a <= R_LBO:  return Z2   # lower boss
    if R_RBI <= a <= R_RBO: return Z2  # rim boss
    return Z1                   # base only

def draw_hole_profile(t0, cb_d, cb_from_top=False):
    """Draw the hole stack at radial position t0 in the section view.

    cb_from_top=False (default): CB sits at the BOTTOM (Z=0..CB_DEPTH),
                                 M3 above it up to z_top.
    cb_from_top=True:            CB sits at the TOP (Z = z_top - CB_DEPTH .. z_top),
                                 M3 below it from Z=0 up to the CB floor.
    """
    hcb = cb_d / 2
    hm3 = M3_DIAM / 2
    z_top = hole_top_z(t0)
    if cb_from_top:
        # CB pocket at top of stack, M3 through-hole below it.
        cb_floor = z_top - CB_DEPTH        # for the diamond t=±6 case: 9 - 4 = 5
        # Left wall: M3 from Z=0 up to cb_floor, then CB widens out to z_top
        line(*sa(t0 - hm3, 0),         *sa(t0 - hm3, cb_floor), GEOM_W)
        line(*sa(t0 - hm3, cb_floor),  *sa(t0 - hcb, cb_floor), GEOM_W)
        line(*sa(t0 - hcb, cb_floor),  *sa(t0 - hcb, z_top),    GEOM_W)
        # Right wall
        line(*sa(t0 + hm3, 0),         *sa(t0 + hm3, cb_floor), GEOM_W)
        line(*sa(t0 + hm3, cb_floor),  *sa(t0 + hcb, cb_floor), GEOM_W)
        line(*sa(t0 + hcb, cb_floor),  *sa(t0 + hcb, z_top),    GEOM_W)
    else:
        # Left wall (CB then M3)
        line(*sa(t0 - hcb, 0),         *sa(t0 - hcb, CB_DEPTH), GEOM_W)
        line(*sa(t0 - hcb, CB_DEPTH),  *sa(t0 - hm3, CB_DEPTH), GEOM_W)
        line(*sa(t0 - hm3, CB_DEPTH),  *sa(t0 - hm3, z_top),    GEOM_W)
        # Right wall
        line(*sa(t0 + hcb, 0),         *sa(t0 + hcb, CB_DEPTH), GEOM_W)
        line(*sa(t0 + hcb, CB_DEPTH),  *sa(t0 + hm3, CB_DEPTH), GEOM_W)
        line(*sa(t0 + hm3, CB_DEPTH),  *sa(t0 + hm3, z_top),    GEOM_W)
    # Tiny centerline (dashed)
    pdf.set_dash_pattern(dash=2, gap=1); _w(0.12)
    pdf.line(*sa(t0, -2), *sa(t0, z_top + 2))
    pdf.set_dash_pattern()
    _w(GEOM_W)

# All hole locations on the X-axis intersection of the section plane.
# Each spec: (t-position, cb-diameter, cb-from-top flag).
# Diamond holes at (±DIAG_X/2, 0) are always on the X axis (unchanged).
# PCD ring holes are included ONLY if RING_HOLE_ROTATION puts a hole back on
# the 0°/180° line — otherwise the section view shows only bosses + diamonds.
hole_specs = [
    ( DIAG_X/2,    CB_A_DIAM, True),     # diamond — CB on TOP face
    (-DIAG_X/2,    CB_A_DIAM, True),     # diamond — CB on TOP face
]
if PCD_RINGS_ON_X_AXIS:
    for sign in pcd_hole_on_x_axis():
        hole_specs.append(( sign * INNER_PCD_R, CB_B_DIAM, False))
        hole_specs.append(( sign * OUTER_PCD_R, CB_B_DIAM, False))

# ---- Bottom edge (Z=0) drawn from -R_BO to +R_BO, broken at each opening on
# the bottom face. For top-opening CBs the bottom face only has the Φ3.2 M3
# through-hole opening (M3 still goes all the way through); for bottom-opening
# CBs the bottom face has the full CB Φ opening.
def bot_gap(spec):
    t0, cb, top = spec
    half = (M3_DIAM if top else cb) / 2
    return (t0 - half, t0 + half)

gaps_bot = sorted(
    [bot_gap(s) for s in hole_specs]
    + [(-CENTER_CB_DIAM / 2, CENTER_CB_DIAM / 2)]   # center CB bottom opening
)
t_prev = -R_BO
for gl, gr in gaps_bot:
    if gl > t_prev:
        line(*sa(t_prev, 0), *sa(gl, 0), GEOM_W)
    t_prev = max(t_prev, gr)
if R_BO > t_prev:
    line(*sa(t_prev, 0), *sa(R_BO, 0), GEOM_W)

# Center Φ6.2 × 2.2mm bottom-opening CB — walls + flat floor
_half_cc = CENTER_CB_DIAM / 2
line(*sa(-_half_cc, 0),                *sa(-_half_cc, CENTER_CB_DEPTH), GEOM_W)
line(*sa( _half_cc, 0),                *sa( _half_cc, CENTER_CB_DEPTH), GEOM_W)
line(*sa(-_half_cc, CENTER_CB_DEPTH),  *sa( _half_cc, CENTER_CB_DEPTH), GEOM_W)

# Leader/callout for the center CB — label sits below the section bottom edge,
# clear of the diamond-hole region (t < 4.4) and the right-side dim stack.
_cc_anchor_x, _cc_anchor_y = sa(0, CENTER_CB_DEPTH / 2)
_cc_kink_x,   _cc_kink_y   = sa(20, -12)
_cc_label_x,  _cc_label_y  = sa(22, -12)
_w(EXT_W)
pdf.line(_cc_anchor_x, _cc_anchor_y, _cc_kink_x, _cc_kink_y)
text(_cc_label_x, _cc_label_y + 1.5,
     f"中心 Φ{CENTER_CB_DIAM:g} × {CENTER_CB_DEPTH:g} 沉孔 (底面)",
     size=TXT_D, anchor="start")
_w(GEOM_W)

# Top face break: at each hole position, break the top edge by the radius of
# whatever opens there. Top-opening diamond CBs break by hcb (Φ7), the rest
# break by hm3 (Φ3.2 since the M3 goes all the way through).
pdf.set_draw_color(255, 255, 255); _w(GEOM_W + 0.4)
for (t0, cb_d, cb_from_top) in hole_specs:
    z_top = hole_top_z(t0)
    half = (cb_d if cb_from_top else M3_DIAM) / 2
    pdf.line(*sa(t0 - half, z_top), *sa(t0 + half, z_top))
pdf.set_draw_color(0, 0, 0)
_w(GEOM_W)

# Draw the stepped hole profiles
for (t0, cb_d, cb_from_top) in hole_specs:
    draw_hole_profile(t0, cb_d, cb_from_top=cb_from_top)

# ----- Section A-A dimensions -----
# LEFT side: stagger the three Z segments (base 3 / lower 2.5 / upper 3.5) at
# DIM_O1, DIM_O2, DIM_O3 to avoid arrow-vs-arrow collision between adjacent
# segments sharing an endpoint at z=Z1 and z=Z2. Total height goes on the
# right side instead.
left_x1 = sa(-R_BO, 0)[0] - DIM_O1
left_x2 = sa(-R_BO, 0)[0] - DIM_O2
left_x3 = sa(-R_BO, 0)[0] - DIM_O3
vdim(sa(0, Z1)[1], sa(0, 0)[1],
     sa(-R_BO, 0)[0], left_x1, f"{BASE_T:g}")
vdim(sa(0, Z2)[1], sa(0, Z1)[1],
     sa(-R_BO, 0)[0], left_x2, f"{LOWER_BOSS_T:g}")
vdim(sa(0, Z3)[1], sa(0, Z2)[1],
     sa(-R_BO, 0)[0], left_x3, f"{UPPER_BOSS_T:g}")

# RIGHT side: CB depth (Z=0 .. CB_DEPTH=4) on DIM_O1, rim boss thickness
# (Z1..Z2 = 2.5) on DIM_O2, total height (9) on DIM_O3.
right_x1 = sa(R_BO, 0)[0] + DIM_O1
right_x2 = sa(R_BO, 0)[0] + DIM_O2
right_x3 = sa(R_BO, 0)[0] + DIM_O3
vdim(sa(0, CB_DEPTH)[1], sa(0, 0)[1],
     sa(R_BO, 0)[0], right_x1, f"{CB_DEPTH:g}")
vdim(sa(0, Z2)[1], sa(0, Z1)[1],
     sa(R_BO, 0)[0], right_x2, f"{RIM_BOSS_T:g}")
vdim(sa(0, TOTAL_H)[1], sa(0, 0)[1],
     sa(R_BO, 0)[0], right_x3, f"{TOTAL_H:g}")

# Top horizontal dims, stacked from closest to furthest. The PCD ring holes
# are no longer on the X axis after RING_HOLE_ROTATION, so we keep the PCD
# diameter dims to communicate the ring layout (still meaningful even though
# no individual hole sits on the cutting plane) only when PCD_RINGS_ON_X_AXIS.
# Otherwise we omit them (handled by the top-view callouts).
top_y1 = sa(0, TOTAL_H)[1] - DIM_O1
hdim(sa(-R_UBO, 0)[0], sa(R_UBO, 0)[0],
     sa(0, TOTAL_H)[1], top_y1, f"Φ{UPPER_BOSS_D:g}")
top_y2 = sa(0, TOTAL_H)[1] - DIM_O2
hdim(sa(-R_LBO, 0)[0], sa(R_LBO, 0)[0],
     sa(0, TOTAL_H)[1], top_y2, f"Φ{LOWER_BOSS_D:g}")
top_y3 = sa(0, TOTAL_H)[1] - DIM_O3
hdim(sa(-R_RBI, 0)[0], sa(R_RBI, 0)[0],
     sa(0, TOTAL_H)[1], top_y3, f"Φ{RIM_BOSS_ID:g}")
top_y4 = sa(0, TOTAL_H)[1] - (DIM_O3 + 12)
hdim(sa(-R_BO, 0)[0], sa(R_BO, 0)[0],
     sa(0, TOTAL_H)[1], top_y4, f"Φ{BASE_OD:g}")

# ===== DETAIL B (4:1) — M3 + Φ7 × 4 CB stack (diamond holes) =====
# Placed below the SECTION A-A view (right column, outside the top-view bbox).
DB_SCALE = 4.0
db_cx, db_cy = 250, 258
DB_DIM_O = 12.0
def db(t, z): return (db_cx + t * DB_SCALE, db_cy - z * DB_SCALE)

text(db_cx, db_cy - Z3 * DB_SCALE - DB_DIM_O - 12,
     "详图 B  Detail B  (4:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(db_cx, db_cy - Z3 * DB_SCALE - DB_DIM_O - 5,
     f"中心菱形孔: M3 + Φ{CB_A_DIAM:g}×{CB_DEPTH:g} 沉孔 (顶面)",
     size=TXT_I, anchor="middle")

# For detail B, show local cross-section at a diamond hole position (t=6).
# Local material at t=6 spans Z=0..Z3 (base + lower + upper boss).
# The Φ7 CB pocket now opens from the TOP (Z = Z3 - CB_DEPTH .. Z3 = 5..9),
# and the Φ3.2 M3 through-hole runs from Z=0 up to the CB floor at Z=5.
DB_HALF_BASE = 7.0
DB_HALF_CB   = CB_A_DIAM / 2   # 3.5
DB_HALF_M3   = M3_DIAM / 2     # 1.6
db_z_top     = Z3              # 9.0
db_cb_floor  = Z3 - CB_DEPTH   # 5.0

_w(GEOM_W)
# Bottom edge with M3 gap (only Φ3.2 opens on the bottom now)
line(*db(-DB_HALF_BASE, 0),       *db(-DB_HALF_M3, 0),       GEOM_W)
line(*db( DB_HALF_M3,   0),       *db( DB_HALF_BASE, 0),     GEOM_W)
# M3 walls — from Z=0 up to the CB floor at Z=5
line(*db(-DB_HALF_M3, 0),         *db(-DB_HALF_M3, db_cb_floor), GEOM_W)
line(*db( DB_HALF_M3, 0),         *db( DB_HALF_M3, db_cb_floor), GEOM_W)
# CB shoulder (M3 widens out to Φ7 at the floor of the pocket)
line(*db(-DB_HALF_CB, db_cb_floor), *db(-DB_HALF_M3, db_cb_floor), GEOM_W)
line(*db( DB_HALF_M3, db_cb_floor), *db( DB_HALF_CB, db_cb_floor), GEOM_W)
# CB walls — from cb_floor up to the top
line(*db(-DB_HALF_CB, db_cb_floor), *db(-DB_HALF_CB, db_z_top), GEOM_W)
line(*db( DB_HALF_CB, db_cb_floor), *db( DB_HALF_CB, db_z_top), GEOM_W)
# Top edge with CB gap (Φ7 opens on the top)
line(*db(-DB_HALF_BASE, db_z_top), *db(-DB_HALF_CB, db_z_top), GEOM_W)
line(*db( DB_HALF_CB,   db_z_top), *db( DB_HALF_BASE, db_z_top), GEOM_W)
# Outer edges
line(*db(-DB_HALF_BASE, 0), *db(-DB_HALF_BASE, db_z_top), GEOM_W)
line(*db( DB_HALF_BASE, 0), *db( DB_HALF_BASE, db_z_top), GEOM_W)
# Internal step lines (light) showing the Z=Z1 (3) and Z=Z2 (5.5) interfaces.
# At Z1 the M3 through-hole crosses (gap = ±hm3); at Z2 the CB pocket crosses
# (gap = ±hcb, since Z2=5.5 is above cb_floor=5).
pdf.set_dash_pattern(dash=1.5, gap=1.2); _w(0.12)
pdf.line(*db(-DB_HALF_BASE, Z1), *db(-DB_HALF_M3, Z1))
pdf.line(*db( DB_HALF_M3,   Z1), *db( DB_HALF_BASE, Z1))
pdf.line(*db(-DB_HALF_BASE, Z2), *db(-DB_HALF_CB, Z2))
pdf.line(*db( DB_HALF_CB,   Z2), *db( DB_HALF_BASE, Z2))
pdf.set_dash_pattern()
_w(GEOM_W)

# Centerline
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(db(0, -2)[0], db(0, -2)[1], db(0, db_z_top + 2)[0], db(0, db_z_top + 2)[1])
pdf.set_dash_pattern()
_w(GEOM_W)

# Detail B dims — CB depth (4) measured from top face downward (Z3 → cb_floor).
# Place the CB depth vdim on the RIGHT side of Detail B to keep clear of the
# top-view's bottom-left diamond-diagonal leader label.
# Φ7 on the TOP edge (where it opens), Φ3.2 on the BOTTOM edge.
vdim(db(0, db_z_top)[1], db(0, db_cb_floor)[1],
     db(DB_HALF_BASE, 0)[0], db(DB_HALF_BASE, 0)[0] + DB_DIM_O,
     f"{CB_DEPTH:g}")
hdim(db(-DB_HALF_CB, 0)[0], db(DB_HALF_CB, 0)[0],
     db(0, db_z_top)[1], db(0, db_z_top)[1] - DB_DIM_O,
     f"Φ{CB_A_DIAM:g}")
hdim(db(-DB_HALF_M3, 0)[0], db(DB_HALF_M3, 0)[0],
     db(0, 0)[1], db(0, 0)[1] + DB_DIM_O,
     f"Φ{M3_DIAM:g}")

# ===== DETAIL C (4:1) — M3 + Φ4.2 × 4 CB stack (the other 20 holes) =====
# Placed below the SECTION A-A view, to the right of Detail B.
DC_SCALE = 4.0
dc_cx, dc_cy = 340, 258
DC_DIM_O = 12.0
def dc(t, z): return (dc_cx + t * DC_SCALE, dc_cy - z * DC_SCALE)

text(dc_cx, dc_cy - Z3 * DC_SCALE - DC_DIM_O - 12,
     "详图 C  Detail C  (4:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(dc_cx, dc_cy - Z3 * DC_SCALE - DC_DIM_O - 5,
     f"方形 / 内 PCD / 外 PCD 孔: M3 + Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔",
     size=TXT_I, anchor="middle")

DC_HALF_BASE = 7.0
DC_HALF_CB   = CB_B_DIAM / 2   # 2.1
DC_HALF_M3   = M3_DIAM / 2     # 1.6
# Show the material spanning Z=0..Z2=5.5 (base + lower boss, typical of PCD-70
# and PCD-155 hole positions). For the diamond case the top extends to Z3,
# but that's covered by Detail B.
dc_z_top = Z2     # 5.5

_w(GEOM_W)
line(*dc(-DC_HALF_BASE, 0),       *dc(-DC_HALF_CB,   0),       GEOM_W)
line(*dc( DC_HALF_CB,   0),       *dc( DC_HALF_BASE, 0),       GEOM_W)
line(*dc(-DC_HALF_CB, 0),         *dc(-DC_HALF_CB, CB_DEPTH),  GEOM_W)
line(*dc( DC_HALF_CB, 0),         *dc( DC_HALF_CB, CB_DEPTH),  GEOM_W)
line(*dc(-DC_HALF_CB, CB_DEPTH),  *dc(-DC_HALF_M3, CB_DEPTH),  GEOM_W)
line(*dc( DC_HALF_M3, CB_DEPTH),  *dc( DC_HALF_CB, CB_DEPTH),  GEOM_W)
line(*dc(-DC_HALF_M3, CB_DEPTH),  *dc(-DC_HALF_M3, dc_z_top),  GEOM_W)
line(*dc( DC_HALF_M3, CB_DEPTH),  *dc( DC_HALF_M3, dc_z_top),  GEOM_W)
line(*dc(-DC_HALF_BASE, dc_z_top), *dc(-DC_HALF_M3, dc_z_top), GEOM_W)
line(*dc( DC_HALF_M3,   dc_z_top), *dc( DC_HALF_BASE, dc_z_top), GEOM_W)
line(*dc(-DC_HALF_BASE, 0), *dc(-DC_HALF_BASE, dc_z_top), GEOM_W)
line(*dc( DC_HALF_BASE, 0), *dc( DC_HALF_BASE, dc_z_top), GEOM_W)
# Step interface at Z=Z1 (3): dashed
pdf.set_dash_pattern(dash=1.5, gap=1.2); _w(0.12)
pdf.line(*dc(-DC_HALF_BASE, Z1), *dc(-DC_HALF_M3, Z1))
pdf.line(*dc( DC_HALF_M3,   Z1), *dc( DC_HALF_BASE, Z1))
pdf.set_dash_pattern()
_w(GEOM_W)

# Centerline
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(dc(0, -2)[0], dc(0, -2)[1], dc(0, dc_z_top + 2)[0], dc(0, dc_z_top + 2)[1])
pdf.set_dash_pattern()
_w(GEOM_W)

vdim(dc(0, CB_DEPTH)[1], dc(0, 0)[1],
     dc(-DC_HALF_BASE, 0)[0], dc(-DC_HALF_BASE, 0)[0] - DC_DIM_O,
     f"{CB_DEPTH:g}")
hdim(dc(-DC_HALF_CB, 0)[0], dc(DC_HALF_CB, 0)[0],
     dc(0, 0)[1], dc(0, 0)[1] + DC_DIM_O,
     f"Φ{CB_B_DIAM:g}")
hdim(dc(-DC_HALF_M3, 0)[0], dc(DC_HALF_M3, 0)[0],
     dc(0, dc_z_top)[1], dc(0, dc_z_top)[1] - DC_DIM_O,
     f"Φ{M3_DIAM:g}")

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — 轴座盘 (Hub Disc)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖) / 4:1 (详 B, C)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_OD:g}×{BASE_T:g} 基盘 / 下凸 Φ{LOWER_BOSS_D:g}×{LOWER_BOSS_T:g} / "
     f"上凸 Φ{UPPER_BOSS_D:g}×{UPPER_BOSS_T:g} / 凸圈 Φ{RIM_BOSS_OD:g}/Φ{RIM_BOSS_ID:g}×{RIM_BOSS_T:g} (切口 {RIM_CUTOUT_A_S:g}°–{RIM_CUTOUT_A_E:g}°) / "
     f"24×Φ{M3_DIAM:g} + Φ{CB_A_DIAM:g}/Φ{CB_B_DIAM:g}×{CB_DEPTH:g} 沉孔 + 中心 Φ{CENTER_CB_DIAM:g}×{CENTER_CB_DEPTH:g} 沉孔 (底)  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-04  /  POV3D / models / hub_disc / hub_disc.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("hub_disc_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    # Final PDF is held open by an external viewer; write to a sibling temp
    # path so the run still succeeds and the caller can finish the swap once
    # the viewer is closed.
    alt = Path(__file__).with_name("hub_disc_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
