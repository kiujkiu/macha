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
DISC_THICK = 6.0          # was 5, then 7
M3_DIAM = 3.2
M3_CB_DIAM = 7.0      # counterbore from TOP face
M3_CB_DEPTH = 2.5
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

# 10 special holes: 6 boss-type + 4 plain (round CB)
SPECIAL_M3_DIAM  = 3.2         # plain holes
SPECIAL_CB_DIAM  = 4.2         # plain holes round CB
SPECIAL_CB_DEPTH      = 4.0    # plain CB depth
SPECIAL_BOSS_DIAM     = 6.0    # was 10; →6 on 2026-06-12
SPECIAL_BOSS_H        = 3.0
BOSS_THRU_DIAM   = 3.5         # boss through-hole (was Φ3.2)
BOSS_HEX_AF      = 5.4         # hex nut pocket across-flats
BOSS_HEX_DEPTH   = 2.2
BOSS_HEX_R       = BOSS_HEX_AF / math.sqrt(3.0)   # ≈ 3.06
# The 6 boss holes align with the pi2hub75e PCB's 6 Φ3.3 mounting holes
# (see build_stl.py for the PCB-frame mapping)
PCB_HOLES = [
    ( 3.2, 58.8), ( 3.2, 48.8),
    (79.0, 58.8), (79.0, 48.8),
    ( 3.5,  3.1), (78.4,  3.0),
]
PCB_OFF_X = 53.8
PCB_OFF_Y = 41.0
# component side UP → disc_Y = pcb_x − PCB_OFF_Y (proper rotation, not mirror)
SPECIAL_BOSS_POSITIONS = [
    (round(PCB_OFF_X - py, 2), round(px - PCB_OFF_Y, 2)) for (px, py) in PCB_HOLES
]   # → (-5, -37.8) (5, -37.8) (-5, 38) (5, 38) (50.7, -37.5) (50.8, 37.4)
SPECIAL_PLAIN_POSITIONS = [
    (62.0,  21.0), (62.0, -21.0),   # +2 right on 2026-06-12 (was 60)
    (88.0,  28.5), (88.0, -28.5),   # +26 right of the (62, ±21) pair, 57 c-to-c (PSU ears)
    (-92.5,  20.0), (-92.5, -20.0), # X=-92.5 pair, 40 c-to-c (was -85, moved -7.5 on 2026-06-12)
]
SPECIAL_POSITIONS = SPECIAL_BOSS_POSITIONS + SPECIAL_PLAIN_POSITIONS

# Rectangular slots on the ribs (15 × 10 each, same bottom height)
SLOT_WIDTH    = 15.0
SLOT_HEIGHT   = 16.0                    # was 6, 10; →16 on 2026-06-12 (reaches the rib top: open notch)
SLOT_BOTTOM_Z = DISC_THICK + 14.0      # was +12; raised 2 on 2026-06-12
SLOT_X_CENTER = 41.0                    # +Y rib slot
SLOT2_X_CENTER = 18.5                   # -Y rib slot (added 2026-06-12)
SLOTS = [
    (SLOT_X_CENTER,  +RIB_CC/2),
    (SLOT2_X_CENTER, -RIB_CC/2),
]

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
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    if halo:
        sw, fh = pdf.get_string_width(s), pdf.font_size
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(x - 0.4, y - fh * 0.85, sw + 0.8, fh * 1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, angle_deg, size=TXT_D, anchor="middle", halo=False):
    pdf.set_font("SimHei", "", size)
    sw = pdf.get_string_width(s)
    with pdf.rotation(angle=angle_deg, x=cx, y=cy):
        if   anchor == "middle": dx = -sw/2
        elif anchor == "end":    dx = -sw
        else: dx = 0
        if halo:
            fh = pdf.font_size
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(cx + dx - 0.4, cy - fh * 0.85, sw + 0.8, fh * 1.1, style="F")
            pdf.set_fill_color(0, 0, 0)
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
    text((x_l + x_r) / 2, yd - 1.8, label, anchor="middle", halo=True)
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
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle", halo=True)
    else:
        y_label = y_bot + (ARR_L + 1.0) + label_h_rot / 2 + 1.0
        rot_text(xd + to, y_label, label, angle_deg=90, anchor="middle", halo=True)

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, f"POV 3D rim_top_disc  (Φ{DISC_OD:g} × {DISC_THICK:g},2 × 加强筋 + 16 × M3 + 2 × 肋孔)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"Φ{DISC_OD:g} 圆盘,厚 {DISC_THICK:g} / "
     f"16 × [Φ{M3_DIAM:g} M3 + Φ{M3_CB_DIAM:g} × {M3_CB_DEPTH:g} 沉孔(顶→底)] (PCD Φ{2*INNER_PCD_R:g} ×8 + PCD Φ{2*OUTER_PCD_R:g} ×8,起 22.5°,45° 等分) / "
     f"2 × 径向肋 {RIB_THICK:g} × {RIB_HEIGHT:g} (中心 Y=±{RIB_CC/2:g},c-to-c {RIB_CC:g}) / "
     f"2 × Φ{RIB_HOLE_DIAM:g} 肋孔 (沿 Y 贯通,X=-34.3 / -64.3,Z={RIB_HOLE_Z:g}) / "
     f"{len(SPECIAL_BOSS_POSITIONS)} × [Φ{SPECIAL_BOSS_DIAM:g}×{SPECIAL_BOSS_H:g} 凸台 + Φ{BOSS_THRU_DIAM:g} 通孔 + 六角沉孔 对边{BOSS_HEX_AF:g}×{BOSS_HEX_DEPTH:g}(底)] + "
     f"4 × [Φ{SPECIAL_M3_DIAM:g} M3 通孔 + Φ{SPECIAL_CB_DIAM:g} × {SPECIAL_CB_DEPTH:g} 沉孔(底→顶)]  "
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

# 16 M3 holes + Φ7 CB from top (CB edge visible from above — solid circle)
for R in (INNER_PCD_R, OUTER_PCD_R):
    for a in HOLE_ANGLES_DEG:
        cx = R * math.cos(math.radians(a))
        cy = R * math.sin(math.radians(a))
        pcx, pcy = tv(cx, cy)
        pdf.circle(pcx, pcy, M3_DIAM/2, style="D")
        pdf.circle(pcx, pcy, M3_CB_DIAM/2, style="D")
        pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
        pdf.line(pcx - 3, pcy, pcx + 3, pcy)
        pdf.line(pcx, pcy - 3, pcx, pcy + 3)
        pdf.set_dash_pattern(); _w(GEOM_W)

# 10 special holes; boss positions: solid Φ10 boss + dashed hex pocket +
# Φ3.5 through; plain positions: dashed Φ4.2 CB + Φ3.2 through
import math as _math
for (hx, hy) in SPECIAL_POSITIONS:
    pcx, pcy = tv(hx, hy)
    is_boss = (hx, hy) in SPECIAL_BOSS_POSITIONS
    if is_boss:
        _w(GEOM_W)
        pdf.circle(pcx, pcy, SPECIAL_BOSS_DIAM/2, style="D")
    # CB outline (hidden, dashed): hexagon for boss, circle for plain
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    if is_boss:
        pts = [(pcx + BOSS_HEX_R * _math.cos(_math.radians(60*k)),
                pcy + BOSS_HEX_R * _math.sin(_math.radians(60*k))) for k in range(6)]
        pdf.polygon(pts, style="D")
    else:
        pdf.circle(pcx, pcy, SPECIAL_CB_DIAM/2, style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    # through-hole (visible)
    pdf.circle(pcx, pcy, (BOSS_THRU_DIAM if is_boss else SPECIAL_M3_DIAM)/2, style="D")
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

# Rib slots — hidden in top view (cutouts pass through each rib's Y),
# shown as dashed rectangles within the rib outlines.
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
for (s_xc, s_ry) in SLOTS:
    sx0 = tv(s_xc - SLOT_WIDTH/2, s_ry + RIB_THICK/2)[0]
    sy0 = tv(s_xc - SLOT_WIDTH/2, s_ry + RIB_THICK/2)[1]
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
text(tv(0, +OUTER_PCD_R + 8.5)[0], tv(0, +OUTER_PCD_R + 8.5)[1],
     f"16 × [Φ{M3_DIAM:g} 通孔 (M3) + Φ{M3_CB_DIAM:g} × {M3_CB_DEPTH:g} 沉孔(顶→底)] — 内圈 PCD Φ{2*INNER_PCD_R:g} × 8,外圈 PCD Φ{2*OUTER_PCD_R:g} × 8,起 22.5° / 45° 等分",
     size=TXT_I, anchor="middle")

# Dims for the special holes (placed above the top view, in +X +Y region)
BP_Y = SPECIAL_BOSS_POSITIONS[2][1]   # boss top-pair Y (38.0)
# Vertical (Y) dims on the right of the +X column
vdim(tv(0, BP_Y)[1], tv(0, 0)[1], tv(62, 0)[0] + 8, tv(62, 0)[0] + 8 + DIM_O1,
     f"{BP_Y:g}")
vdim(tv(0, 21)[1], tv(0, 0)[1], tv(62, 0)[0] + 8, tv(62, 0)[0] + 8 + DIM_O2,
     "21")
# Horizontal (X) dims below the +X column, stacked
hdim(tv(0, 0)[0], tv(5, 0)[0],  tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O1, "5")
hdim(tv(0, 0)[0], tv(SPECIAL_BOSS_POSITIONS[4][0], 0)[0],
     tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O2,
     f"{SPECIAL_BOSS_POSITIONS[4][0]:g}")
hdim(tv(0, 0)[0], tv(62, 0)[0], tv(0, -37.5)[1] + 4, tv(0, -37.5)[1] + 4 + DIM_O3, "62")
# Note labeling the 6-hole pattern
# (note placed BELOW the X axis so the detail-view leader arrows above stay clear)
text(tv(60, -(37.5 + 6))[0], tv(60, -(37.5 + 6))[1],
     f"凸台孔组 ×{len(SPECIAL_BOSS_POSITIONS)} 对齐 pi2hub75e PCB (Φ3.3 孔,见坐标表) / "
     f"普通孔 ×{len(SPECIAL_PLAIN_POSITIONS)} (X=62/88/-92.5) — 均见局部放大",
     size=TXT_I, anchor="middle")
# Boss-hole coordinate table (exact PCB-aligned positions)
# M4 hole between the ribs, hugging the -Y rib, R = 92
M4_DIAM, M4_Y_W = 4.2, -40.0
M4_X_W = math.sqrt(92.0**2 - M4_Y_W**2)   # 82.85
_m4x, _m4y = tv(M4_X_W, M4_Y_W)
_w(GEOM_W)
pdf.circle(_m4x, _m4y, M4_DIAM/2, style="D")
pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
pdf.line(_m4x - 3.5, _m4y, _m4x + 3.5, _m4y)
pdf.line(_m4x, _m4y - 3.5, _m4x, _m4y + 3.5)
pdf.set_dash_pattern(); _w(GEOM_W)
text(_m4x + 6, _m4y + 1.5, f"Φ{M4_DIAM:g} (M4)",
     size=TXT_I, anchor="start", halo=True)

text(45, 244, "凸台孔坐标 (X, Y):", size=TXT_I, anchor="start", halo=True)
text(45, 249,
     "  ".join(f"({x:g}, {y:g})" for (x, y) in SPECIAL_BOSS_POSITIONS[:3]),
     size=TXT_I, anchor="start", halo=True)
text(45, 254,
     "  ".join(f"({x:g}, {y:g})" for (x, y) in SPECIAL_BOSS_POSITIONS[3:]),
     size=TXT_I, anchor="start", halo=True)
text(45, 259,
     f"M4 孔 Φ{M4_DIAM:g}: ({M4_X_W:.2f}, {M4_Y_W:g}), R=92 (环Φ170 外 7), 距 -Y 肋内面 5",
     size=TXT_I, anchor="start", halo=True)
# X dim for the (-5, BP_Y) pair: 10 across to the (5, BP_Y) pair,
# placed above the two top bosses
hdim(tv(-5, 0)[0], tv(5, 0)[0],
     tv(0, BP_Y)[1] - 6, tv(0, BP_Y)[1] - 14, "10")
# PSU-ear pair (88, ±28.5): Y dim on right, X dim in the lower stack
vdim(tv(0, 28.5)[1], tv(0, -28.5)[1], tv(88, 0)[0] + 6, tv(88, 0)[0] + 6 + DIM_O1,
     "57")
hdim(tv(62, 0)[0], tv(88, 0)[0],
     tv(0, -37.5)[1] + 4 + DIM_O3 + 8, tv(0, -37.5)[1] + 4 + DIM_O3 + 8 + 0.01,
     "26")
# X=-92.5 pair (-92.5, ±20): Y dim just left of the pair
vdim(tv(0, 20)[1], tv(0, -20)[1], tv(-92.5, 0)[0] - 6, tv(-92.5, 0)[0] - 14,
     "40")

# ===== FRONT VIEW (1:1) — looking from +Y =====
# Show disc cross-section (170 wide × 5 tall) + 2 ribs on top (5 × 30)
# + 2 rib through-holes (visible as circles since the holes are along Y)
fv_cx = 320      # disc center in PDF X
fv_z0 = 215      # disc top edge (Z=DISC_THICK level) in PDF Y; disc bottom at fv_z0+DISC_THICK
def fv(x, z): return (fv_cx + x, fv_z0 + DISC_THICK - z)

text(fv_cx, 156, "前视图  Front View  (1:1)   尺寸单位: mm  (沿 +Y 看)",
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
# Slot on -Y rib — behind the front rib in this view → hidden dashed rectangle
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
s2x0 = fv(SLOT2_X_CENTER - SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[0]
s2y0 = fv(SLOT2_X_CENTER - SLOT_WIDTH/2, SLOT_BOTTOM_Z + SLOT_HEIGHT)[1]
pdf.rect(s2x0, s2y0, SLOT_WIDTH, SLOT_HEIGHT, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)
# X-center of the -Y rib slot from disc center
hdim(fv(0, 0)[0], fv(SLOT2_X_CENTER, 0)[0],
     fv(0, SLOT_BOTTOM_Z)[1], fv(0, SLOT_BOTTOM_Z)[1] + 38,
     f"{SLOT2_X_CENTER:g}")
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
     f"前视图中两条肋投影到同一矩形 / 槽 {SLOT_WIDTH:g}×{SLOT_HEIGHT:g} ×2: "
     f"+Y 肋 X={SLOT_X_CENTER:g} (实线), -Y 肋 X={SLOT2_X_CENTER:g} (虚线), 槽底距盘顶 {SLOT_BOTTOM_Z - DISC_THICK:g}",
     size=TXT_I, anchor="middle")

# ===== DETAIL VIEW (3:1) — all 3 counterbored hole types, side by side =====
# One disc cross-section strip with three holes:
#   left  = boss group: Φ10×3 boss, Φ3.5 through disc+boss,
#           hex nut pocket AF 5.3 × 2.2 from bottom
#   mid   = plain group: M3 through, Φ4.2×4 CB from bottom
#   right = rim 16-hole type: M3 through, Φ7×2.5 CB from TOP
DT_S   = 3.0
DT_CX  = 296.0                              # real x=0 (boss center) PDF x
DT_TOP = 80.0                               # PDF y of boss top (z = 9)
DT_TOTAL = DISC_THICK + SPECIAL_BOSS_H      # 9
def dt_x(x): return DT_CX + x * DT_S
def dt_y(z): return DT_TOP + (DT_TOTAL - z) * DT_S
_m3r, _cbr, _bor = SPECIAL_M3_DIAM/2, SPECIAL_CB_DIAM/2, SPECIAL_BOSS_DIAM/2
_btr  = BOSS_THRU_DIAM/2                    # 1.75 (boss through)
_hxr  = BOSS_HEX_AF/2                       # 2.65 (hex pocket half across-flats)
_rimr = M3_CB_DIAM/2                        # 3.5 (rim hole top CB)
PLX, RIMX = 14.0, 26.0                      # real-x of plain / rim hole centers
XL, XR = -11.0, 34.0                        # strip extents (real mm)
_cbz  = BOSS_HEX_DEPTH                      # 2.2 (hex pocket top z)
_cbz2 = SPECIAL_CB_DEPTH                    # 4
_rimz = DISC_THICK - M3_CB_DEPTH            # 3.5 (rim CB bottom z)
_w(GEOM_W)
# boss top (gap at the Φ3.5 through opening) + boss sides
line(dt_x(-_bor), dt_y(DT_TOTAL), dt_x(-_btr), dt_y(DT_TOTAL), GEOM_W)
line(dt_x(_btr),  dt_y(DT_TOTAL), dt_x(_bor),  dt_y(DT_TOTAL), GEOM_W)
line(dt_x(-_bor), dt_y(DT_TOTAL), dt_x(-_bor), dt_y(DISC_THICK), GEOM_W)
line(dt_x(_bor),  dt_y(DT_TOTAL), dt_x(_bor),  dt_y(DISC_THICK), GEOM_W)
# disc top (gaps at plain M3 opening and rim CB opening)
line(dt_x(XL), dt_y(DISC_THICK), dt_x(-_bor), dt_y(DISC_THICK), GEOM_W)
line(dt_x(_bor), dt_y(DISC_THICK), dt_x(PLX - _m3r), dt_y(DISC_THICK), GEOM_W)
line(dt_x(PLX + _m3r), dt_y(DISC_THICK), dt_x(RIMX - _rimr), dt_y(DISC_THICK), GEOM_W)
line(dt_x(RIMX + _rimr), dt_y(DISC_THICK), dt_x(XR), dt_y(DISC_THICK), GEOM_W)
# disc sides
line(dt_x(XL), dt_y(DISC_THICK), dt_x(XL), dt_y(0), GEOM_W)
line(dt_x(XR), dt_y(DISC_THICK), dt_x(XR), dt_y(0), GEOM_W)
# disc bottom (gaps at boss hex pocket, plain CB, rim M3)
line(dt_x(XL), dt_y(0), dt_x(-_hxr), dt_y(0), GEOM_W)
line(dt_x(_hxr), dt_y(0), dt_x(PLX - _cbr), dt_y(0), GEOM_W)
line(dt_x(PLX + _cbr), dt_y(0), dt_x(RIMX - _m3r), dt_y(0), GEOM_W)
line(dt_x(RIMX + _m3r), dt_y(0), dt_x(XR), dt_y(0), GEOM_W)
# hidden walls + shelves
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
for s in (-1, 1):
    # boss group: Φ3.5 through (z 2.2..9), hex pocket (z 0..2.2), shelf z=2.2
    pdf.line(dt_x(s*_btr), dt_y(DT_TOTAL), dt_x(s*_btr), dt_y(_cbz))
    pdf.line(dt_x(s*_hxr), dt_y(_cbz), dt_x(s*_hxr), dt_y(0))
    pdf.line(dt_x(s*_btr), dt_y(_cbz), dt_x(s*_hxr), dt_y(_cbz))
    # plain group: M3 (z 4..6), CB (z 0..4), shelf z=4
    pdf.line(dt_x(PLX + s*_m3r), dt_y(DISC_THICK), dt_x(PLX + s*_m3r), dt_y(_cbz2))
    pdf.line(dt_x(PLX + s*_cbr), dt_y(_cbz2), dt_x(PLX + s*_cbr), dt_y(0))
    pdf.line(dt_x(PLX + s*_m3r), dt_y(_cbz2), dt_x(PLX + s*_cbr), dt_y(_cbz2))
    # rim hole: CB Φ7 (z 3.5..6), M3 (z 0..3.5), shelf z=3.5
    pdf.line(dt_x(RIMX + s*_rimr), dt_y(DISC_THICK), dt_x(RIMX + s*_rimr), dt_y(_rimz))
    pdf.line(dt_x(RIMX + s*_m3r), dt_y(_rimz), dt_x(RIMX + s*_m3r), dt_y(0))
    pdf.line(dt_x(RIMX + s*_m3r), dt_y(_rimz), dt_x(RIMX + s*_rimr), dt_y(_rimz))
pdf.set_dash_pattern(); _w(GEOM_W)
# detail dims
hdim(dt_x(-_bor), dt_x(_bor), DT_TOP, DT_TOP - 8, f"Φ{SPECIAL_BOSS_DIAM:g}")
vdim(dt_y(DT_TOTAL), dt_y(DISC_THICK), dt_x(-_bor), dt_x(-_bor) - 8,
     f"{SPECIAL_BOSS_H:g}")
vdim(dt_y(DISC_THICK), dt_y(0), dt_x(XR), dt_x(XR) + 10, f"{DISC_THICK:g}")
vdim(dt_y(_cbz), dt_y(0), dt_x(_hxr), dt_x(_hxr) + 6,
     f"{BOSS_HEX_DEPTH:g}")
hdim(dt_x(-_hxr), dt_x(_hxr), dt_y(0), dt_y(0) + 8, f"对边 {BOSS_HEX_AF:g}")
vdim(dt_y(_cbz2), dt_y(0), dt_x(PLX + _cbr), dt_x(PLX + _cbr) + 6,
     f"{SPECIAL_CB_DEPTH:g}")
hdim(dt_x(PLX - _cbr), dt_x(PLX + _cbr), dt_y(0), dt_y(0) + 8,
     f"Φ{SPECIAL_CB_DIAM:g}")
hdim(dt_x(RIMX - _rimr), dt_x(RIMX + _rimr), dt_y(DISC_THICK), dt_y(DISC_THICK) - 8,
     f"Φ{M3_CB_DIAM:g}")
vdim(dt_y(DISC_THICK), dt_y(_rimz), dt_x(RIMX + _rimr), dt_x(RIMX + _rimr) + 6,
     f"{M3_CB_DEPTH:g}")
hdim(dt_x(RIMX - _m3r), dt_x(RIMX + _m3r), dt_y(0), dt_y(0) + 8,
     f"Φ{SPECIAL_M3_DIAM:g}")
text(330, dt_y(0) + 15,
     f"局部放大 (3:1): 左 = 凸台孔组 ×{len(SPECIAL_BOSS_POSITIONS)} "
     f"(Φ{SPECIAL_BOSS_DIAM:g}×{SPECIAL_BOSS_H:g} 凸台 + Φ{BOSS_THRU_DIAM:g} 通孔 + "
     f"六角螺母沉孔 对边{BOSS_HEX_AF:g} × 深{BOSS_HEX_DEPTH:g},底面)",
     size=TXT_I, anchor="middle")
text(330, dt_y(0) + 20,
     f"中 = 普通孔 ×{len(SPECIAL_PLAIN_POSITIONS)} (Φ{SPECIAL_M3_DIAM:g} M3 + Φ{SPECIAL_CB_DIAM:g}×{SPECIAL_CB_DEPTH:g} 沉孔底面) / "
     f"右 = 16 × M3 (Φ{SPECIAL_M3_DIAM:g} 通孔 + Φ{M3_CB_DIAM:g}×{M3_CB_DEPTH:g} 沉孔顶面)",
     size=TXT_I, anchor="middle")

# Leader arrows from one instance of each hole type to the detail view
def leader(pts, tip_dir):
    _w(DIM_W)
    for i in range(len(pts) - 1):
        pdf.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    arrow(pts[0][0], pts[0][1], tip_dir[0], tip_dir[1])
# A: boss group at (51, 37.5) → detail (route up over the rib, then right)
leader([(186.3, 91.2), (192.0, 72.0), (260.0, 72.0)], (-5.3, 1.3))
# B: plain hole at (88, 28.5) → detail
leader([(tv(88, 28.5)[0], tv(88, 28.5)[1] - 2.4),
        (tv(88, 28.5)[0], 78.0), (258.0, 78.0)], (0, 1))
# C: rim hole at PCD Φ155, 22.5° → detail
_rx, _ry = tv(OUTER_PCD_R * math.cos(math.radians(22.5)),
              OUTER_PCD_R * math.sin(math.radians(22.5)))
leader([(_rx, _ry - 3.8), (_rx, 76.0), (258.0, 76.0)], (0, 1))

# ===== Title block =====
tb_y = PAGE_H - 28
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     f"POV 3D 结构件 — rim_top_disc (Φ{DISC_OD:g} × {DISC_THICK:g} + 2 加强筋 + 16 M3 沉孔 + 2 肋孔)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 前)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{DISC_OD:g} 圆盘 / 厚 {DISC_THICK:g} / 加强筋 {RIB_THICK:g}×{RIB_HEIGHT:g},c-to-c {RIB_CC:g} / "
     f"装在 rim_ring 上方,夹住 l_bracket_170x60 立柱  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-11  /  POV3D / models / rim_top_disc / rim_top_disc.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("rim_top_disc_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("rim_top_disc_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
