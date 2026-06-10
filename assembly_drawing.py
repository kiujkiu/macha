"""
POV 3D assembly drawing — rim_ring + rim_top_disc + l_bracket_170x60.

Layout (A3 landscape):
  • LEFT half  — TOP VIEW (1:1) looking down on the assembly
      rim_ring (Φ170 + Φ60 ID + notch + 16 M3 holes)
      rim_top_disc (Φ170 disc + 2 radial ribs + 16 matching holes + 2 rib holes)
      l_bracket_170x60 vleg footprint (70 × 90 rectangle), 4 mating holes in red,
      hleg fin's footprint (4 × 90 narrow strip), 2 gusset holes aligned with
      rib holes.

  • RIGHT half — SIDE ELEVATION (1:1, looking from +X)
      Cross-section profile in the Y-Z plane showing the layer stack:
        rim base (Z=0..3.5), rim upper wall (Z=3.5..9, at R=82.5..85),
        disc (Z=9..14), ribs (Z=14..44), bracket vleg slab (Z=14..18),
        bracket hleg fin (Z=14..214, 200 mm tall, 90 wide in Y),
        gusset hole through both ribs at Z=33.

NOT a manufacturing drawing — the part drawings are separate. This is for
visual confirmation of how the three parts assemble.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== rim_ring geometry =====
RIM_OD       = 170.0
RIM_ID       = 60.0
RIM_BASE_H   = 3.5
RIM_WALL_OD  = 170.0
RIM_WALL_ID  = 165.0
RIM_WALL_H   = 5.5            # Z = 3.5 .. 9.0
RIM_TOTAL_H  = RIM_BASE_H + RIM_WALL_H   # 9.0
M3_DIAM      = 3.2
INNER_PCD_R  = 35.0
OUTER_PCD_R  = 77.5
HOLE_ANGLES_DEG = [22.5 + k * 45.0 for k in range(8)]

# ===== rim_top_disc geometry =====
DISC_OD      = 200.0
DISC_THICK   = 5.0
DISC_Z0      = RIM_TOTAL_H          # 9.0 — disc bottom (sits on rim wall top)
DISC_Z1      = DISC_Z0 + DISC_THICK  # 14.0 — disc top

RIB_THICK    = 5.0
RIB_HEIGHT   = 30.0
RIB_CC       = 95.0
RIB_HALF_OUT = RIB_CC/2 + RIB_THICK/2     # 50
RIB_HALF_LEN = math.sqrt((DISC_OD/2)**2 - RIB_HALF_OUT**2) - 0.5
RIB_LENGTH   = 2 * RIB_HALF_LEN           # ~136.5
RIB_Z0       = DISC_Z1                    # 14
RIB_Z1       = DISC_Z1 + RIB_HEIGHT       # 44

# ===== l_bracket_170x60 geometry (in assembly frame) =====
HLEG_DIST_FROM_CENTER = 14.3
BRACKET_LEG_B  = 70.0          # vleg radial dimension
BRACKET_WIDTH  = 90.0          # bracket Y dimension
BRACKET_THICK  = 4.0
BRACKET_LEG_A  = 200.0
RIM_R_IN_BR    = 35.0
RIM_R_OUT_BR   = 77.5
BRACKET_ANG    = (157.5, 202.5)   # the 4 mating angles

# Vleg footprint in rim frame
VLEG_X_INNER = -HLEG_DIST_FROM_CENTER                    # -14.3
VLEG_X_OUTER = -HLEG_DIST_FROM_CENTER - BRACKET_LEG_B    # -84.3
VLEG_Y_MIN   = -BRACKET_WIDTH/2                          # -45
VLEG_Y_MAX   = +BRACKET_WIDTH/2                          # +45
VLEG_Z0      = DISC_Z1                                   # 14 — vleg bottom on disc top
VLEG_Z1      = DISC_Z1 + BRACKET_THICK                   # 18 — vleg top

# Hleg fin in rim frame
HFIN_X_INNER = -HLEG_DIST_FROM_CENTER                    # -14.3
HFIN_X_OUTER = -HLEG_DIST_FROM_CENTER - BRACKET_THICK    # -18.3
HFIN_Z0      = DISC_Z1                                   # 14 — fin base
HFIN_Z1      = DISC_Z1 + BRACKET_LEG_A                   # 214 — fin top (200 mm tall)

# 4 vleg mating holes (rim coords)
def _mating_holes():
    out = []
    for R in (RIM_R_IN_BR, RIM_R_OUT_BR):
        for a in BRACKET_ANG:
            out.append((R * math.cos(math.radians(a)),
                        R * math.sin(math.radians(a))))
    return out
MATING_HOLES_XY = _mating_holes()

# Bracket gusset hole positions in assembly frame:
#   x_assembly = -(z_print) - 14.3 = -34.3 or -64.3
#   z_assembly = x_print + DISC_Z1 = 19 + 14 = 33
GUSSET_HOLE_X = (-34.3, -64.3)
GUSSET_HOLE_Z = 33.0
GUSSET_HOLE_DIAM = 3.2

# 6 special M3 + Φ4.2 CB on the disc top face (+X half, opposite the bracket)
SPECIAL_M3_DIAM = 3.2
SPECIAL_CB_DIAM = 4.2
SPECIAL_POSITIONS = [
    ( 5.0,  37.5), ( 5.0, -37.5),
    (51.0,  37.5), (51.0, -37.5),
    (60.0,  22.0), (60.0, -22.0),
]
# Slot on +Y rib
SLOT_WIDTH    = 15.0
SLOT_HEIGHT   = 6.0
SLOT_X_CENTER = 35.0                  # was 16
SLOT_BOTTOM_Z = DISC_THICK + 11.0     # disc-build Z=16 (was 19)
# Slot bottom in disc-build frame = 16. In assembly: DISC_Z0 + 16 = 9+16 = 25.
SLOT_BOTTOM_Z_ASM = DISC_Z0 + SLOT_BOTTOM_Z   # 25 in assembly Z

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
def text(x, y, s, size=TXT_D, anchor="start", color=(0,0,0)):
    pdf.set_font("SimHei", "", size)
    pdf.set_text_color(*color)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)
    pdf.set_text_color(0, 0, 0)
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
    sw = pdf.get_string_width(label)
    label_y = (y_top + y_bot)/2 if gap >= sw + 1.0 else (y_bot + ARR_L + 1.0 + sw/2 + 1.0)
    pdf.set_font("SimHei", "", TXT_D)
    with pdf.rotation(angle=90, x=xd + to, y=label_y):
        pdf.text(xd + to - sw/2, label_y, label)

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14,
     "POV 3D 装配示意  Assembly  —  rim_ring + rim_top_disc + l_bracket_170x60",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"立板贴 disc 顶面 (Z={DISC_Z1:g}),hleg 立柱 200 mm,距圆心 {HLEG_DIST_FROM_CENTER:g} mm /  "
     f"4 个 M3 对位 rim 内圈 PCD Φ{2*INNER_PCD_R:g} + 外圈 PCD Φ{2*OUTER_PCD_R:g} @ "
     f"{BRACKET_ANG[0]:g}°/{BRACKET_ANG[1]:g}°  /  立柱两侧用 2 条 5×{RIB_HEIGHT:g} 肋夹住,"
     f"c-to-c {RIB_CC:g} mm  /  2 个加强筋 M3 螺栓贯通两肋 + bracket 加强筋",
     size=TXT_I, anchor="middle")

# ============================================================================
# LEFT HALF — TOP VIEW (1:1)
# ============================================================================
tv_cx, tv_cy = 110, 150
def tv(x, y): return (tv_cx + x, tv_cy - y)

text(tv_cx, 35, "俯视图  Top View  (1:1)   (沿 -Z 看)",
     size=TXT_L, anchor="middle")

# rim_top_disc OD (Φ200, the largest visible outline from above)
_w(GEOM_W)
pdf.circle(tv_cx, tv_cy, DISC_OD/2, style="D")
# rim_ring OD (Φ170, hidden under disc) + ID (Φ60, visible through disc hole? no — disc is solid)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
pdf.circle(tv_cx, tv_cy, RIM_OD/2, style="D")
pdf.circle(tv_cx, tv_cy, RIM_ID/2, style="D")
pdf.circle(tv_cx, tv_cy, RIM_WALL_ID/2, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# PCD reference circles
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(tv_cx, tv_cy, INNER_PCD_R, style="D")
pdf.circle(tv_cx, tv_cy, OUTER_PCD_R, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# Centerlines
pdf.set_dash_pattern(dash=4.0, gap=1.5, phase=2.0); _w(0.18)
pdf.line(tv_cx - RIM_OD/2 - 6, tv_cy, tv_cx + RIM_OD/2 + 6, tv_cy)
pdf.line(tv_cx, tv_cy - RIM_OD/2 - 6, tv_cx, tv_cy + RIM_OD/2 + 6)
pdf.set_dash_pattern(); _w(GEOM_W)

# 16 M3 holes (also = disc holes, same positions)
for R in (INNER_PCD_R, OUTER_PCD_R):
    for a in HOLE_ANGLES_DEG:
        cx = R * math.cos(math.radians(a))
        cy = R * math.sin(math.radians(a))
        pcx, pcy = tv(cx, cy)
        pdf.circle(pcx, pcy, M3_DIAM/2, style="D")

# 6 special M3 + CB holes (on disc, +X side, away from bracket)
for (hx, hy) in SPECIAL_POSITIONS:
    pcx, pcy = tv(hx, hy)
    # CB hidden dashed
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    pdf.circle(pcx, pcy, SPECIAL_CB_DIAM/2, style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    pdf.circle(pcx, pcy, SPECIAL_M3_DIAM/2, style="D")

# 2 ribs on disc (sit on top of disc, visible from above)
_w(GEOM_W)
for ry in (+RIB_CC/2, -RIB_CC/2):
    rx0, rry0 = tv(-RIB_LENGTH/2, ry + RIB_THICK/2)
    pdf.rect(rx0, rry0, RIB_LENGTH, RIB_THICK, style="D")

# 2 rib through-holes (along Y) — appear as long dashed lines + small circles at ribs
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
for hx in GUSSET_HOLE_X:
    p1 = tv(hx, +(RIB_CC/2 + RIB_THICK/2 + 1))
    p2 = tv(hx, -(RIB_CC/2 + RIB_THICK/2 + 1))
    pdf.line(p1[0], p1[1], p2[0], p2[1])
pdf.set_dash_pattern(); _w(GEOM_W)
for hx in GUSSET_HOLE_X:
    for ry in (+RIB_CC/2, -RIB_CC/2):
        pcx, pcy = tv(hx, ry)
        pdf.circle(pcx, pcy, GUSSET_HOLE_DIAM/2, style="D")

# Slot on +Y rib (hidden in top view since under the rib's top surface)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
sx0, sy0 = tv(SLOT_X_CENTER - SLOT_WIDTH/2, +RIB_CC/2 + RIB_THICK/2)
pdf.rect(sx0, sy0, SLOT_WIDTH, RIB_THICK, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# Bracket vleg footprint (solid green outline)
pdf.set_draw_color(0, 130, 0); _w(0.6)
vx0, vy0 = tv(VLEG_X_OUTER, VLEG_Y_MAX)
pdf.rect(vx0, vy0, BRACKET_LEG_B, BRACKET_WIDTH, style="D")
pdf.set_draw_color(0, 0, 0); _w(GEOM_W)

# Hleg fin footprint (narrow rectangle, 4 wide × 90 tall along Y) — green dashed
pdf.set_draw_color(0, 130, 0); pdf.set_dash_pattern(dash=2.0, gap=1.0); _w(0.5)
fx0, fy0 = tv(HFIN_X_OUTER, VLEG_Y_MAX)
pdf.rect(fx0, fy0, BRACKET_THICK, BRACKET_WIDTH, style="D")
pdf.set_dash_pattern(); pdf.set_draw_color(0, 0, 0); _w(GEOM_W)

# 4 mating holes highlighted in red
pdf.set_draw_color(200, 0, 0); _w(0.4)
for (mx, my) in MATING_HOLES_XY:
    pcx, pcy = tv(mx, my)
    pdf.circle(pcx, pcy, M3_DIAM/2 + 1.0, style="D")    # red ring around the hole
pdf.set_draw_color(0, 0, 0); _w(GEOM_W)

# Top-view dims
# Φ200 disc OD (visible outline)
hdim(tv(-DISC_OD/2, 0)[0], tv(DISC_OD/2, 0)[0],
     tv(0, -DISC_OD/2)[1], tv(0, -DISC_OD/2)[1] + DIM_O3 + 8,
     f"Φ{DISC_OD:g}")
# 95 rib c-to-c
vdim(tv(0, +RIB_CC/2)[1], tv(0, -RIB_CC/2)[1],
     tv(RIM_OD/2, 0)[0], tv(RIM_OD/2, 0)[0] + DIM_O1,
     f"{RIB_CC:g}")
# 14.3 from center to hleg face
hdim(tv(0, 0)[0], tv(HFIN_X_INNER, 0)[0],
     tv(0, +VLEG_Y_MAX + 8)[1], tv(0, +VLEG_Y_MAX + 8)[1] - DIM_O1,
     f"{HLEG_DIST_FROM_CENTER:g}")
# Bracket vleg X-extent (70 = LEG_B)
hdim(tv(VLEG_X_OUTER, 0)[0], tv(VLEG_X_INNER, 0)[0],
     tv(0, -VLEG_Y_MAX - 10)[1], tv(0, -VLEG_Y_MAX - 10)[1] + DIM_O1,
     f"{BRACKET_LEG_B:g}")
# Bracket WIDTH (90)
vdim(tv(0, VLEG_Y_MAX)[1], tv(0, -VLEG_Y_MAX)[1],
     tv(VLEG_X_OUTER, 0)[0], tv(VLEG_X_OUTER, 0)[0] - DIM_O1,
     f"{BRACKET_WIDTH:g}")

text(tv_cx, tv(0, -RIM_OD/2 - 12)[1] + DIM_O3 + 18,
     "红圈: 4 个 M3 立板对位孔 (rim 内/外圈各 2)  /  绿色: l_bracket 立板 70×90 + hleg 立柱 4×90 投影",
     size=TXT_I, anchor="middle")

# ============================================================================
# RIGHT HALF — SIDE ELEVATION (1:1, looking from +X, so we see Y-Z plane)
# ============================================================================
sv_cx, sv_z0 = 300, 270        # PDF X = Y_rim center; PDF Y = sv_z0 - Z_rim
def sv(y, z): return (sv_cx + y, sv_z0 - z)

text(sv_cx, 35, "侧视图  Side View  (1:1)   (沿 +X 看)",
     size=TXT_L, anchor="middle")

_w(GEOM_W)
# rim base (annular slice, but viewed from side appears as a Y × Z rectangle)
rb_l, rb_t = sv(-RIM_OD/2, RIM_BASE_H); rb_r, rb_b = sv(RIM_OD/2, 0)
pdf.rect(rb_l, rb_t, rb_r - rb_l, rb_b - rb_t, style="D")
# rim upper wall — 2 strips at Y = ±82.5..±85
for sgn in (-1, +1):
    wx_l, wy_t = sv(sgn * RIM_WALL_ID/2 if sgn > 0 else sgn * RIM_OD/2, RIM_TOTAL_H)
    wx_r, wy_b = sv(sgn * RIM_OD/2 if sgn > 0 else sgn * RIM_WALL_ID/2, RIM_BASE_H)
    pdf.rect(wx_l, wy_t, abs(wx_r - wx_l), wy_b - wy_t, style="D")

# disc (170 wide × 5 tall) sitting at Z = 9..14
dx_l, dy_t = sv(-DISC_OD/2, DISC_Z1)
dx_r, dy_b = sv(DISC_OD/2, DISC_Z0)
pdf.rect(dx_l, dy_t, dx_r - dx_l, dy_b - dy_t, style="D")

# 2 ribs at Y = ±47.5, 5 thick × 30 tall (drawn solid)
for ry in (+RIB_CC/2, -RIB_CC/2):
    rx_l, ry_t = sv(ry - RIB_THICK/2, RIB_Z1)
    rx_r, ry_b = sv(ry + RIB_THICK/2, RIB_Z0)
    pdf.rect(rx_l, ry_t, rx_r - rx_l, ry_b - ry_t, style="D")

# Bracket vleg slab (visible? — vleg is at X = -84.3 to -14.3, all behind the
# viewer at +X. The vleg is BEHIND the disc in the +X view but on the disc top.
# Show as a green dashed outline.)
pdf.set_draw_color(0, 130, 0); pdf.set_dash_pattern(dash=2.0, gap=1.5); _w(0.5)
vx_l, vy_t = sv(VLEG_Y_MIN, VLEG_Z1)
vx_r, vy_b = sv(VLEG_Y_MAX, VLEG_Z0)
pdf.rect(vx_l, vy_t, vx_r - vx_l, vy_b - vy_t, style="D")
pdf.set_dash_pattern(); pdf.set_draw_color(0, 0, 0); _w(GEOM_W)

# Bracket hleg fin — vertical 200 mm rectangle at Y = ±45
pdf.set_draw_color(0, 130, 0); _w(0.6)
fx_l, fy_t = sv(VLEG_Y_MIN, HFIN_Z1)
fx_r, fy_b = sv(VLEG_Y_MAX, HFIN_Z0)
pdf.rect(fx_l, fy_t, fx_r - fx_l, fy_b - fy_t, style="D")
pdf.set_draw_color(0, 0, 0); _w(GEOM_W)

# Slot on +Y rib — dashed rectangle in side view (slot is hidden behind rib right end in +X projection)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
sx_l, sy_t = sv(+RIB_CC/2 - RIB_THICK/2, SLOT_BOTTOM_Z_ASM + SLOT_HEIGHT)
sx_r, sy_b = sv(+RIB_CC/2 + RIB_THICK/2, SLOT_BOTTOM_Z_ASM)
pdf.rect(sx_l, sy_t, sx_r - sx_l, sy_b - sy_t, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# Gusset hole at Z = 33 — appears as a horizontal line spanning Y from rib to rib
# (since the hole is along +Y axis, it projects to a horizontal line in this view)
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
p1 = sv(-(RIB_CC/2 + RIB_THICK/2 + 1), GUSSET_HOLE_Z)
p2 = sv(+(RIB_CC/2 + RIB_THICK/2 + 1), GUSSET_HOLE_Z)
pdf.line(p1[0], p1[1], p2[0], p2[1])
# Two hole circles at the rib locations
pdf.set_dash_pattern(); _w(GEOM_W)
for ry in (+RIB_CC/2, -RIB_CC/2):
    pcx, pcy = sv(ry, GUSSET_HOLE_Z)
    pdf.circle(pcx, pcy, GUSSET_HOLE_DIAM/2, style="D")

# Side-view dims
# Total height (Z = 0 .. 214)
vdim(sv(0, HFIN_Z1)[1], sv(0, 0)[1],
     sv(RIM_OD/2, 0)[0], sv(RIM_OD/2, 0)[0] + DIM_O2,
     f"{HFIN_Z1:g}")
# Rib c-to-c
hdim(sv(-RIB_CC/2, 0)[0], sv(+RIB_CC/2, 0)[0],
     sv(0, 0)[1], sv(0, 0)[1] + DIM_O1, f"{RIB_CC:g}")
# Bracket WIDTH between ribs
text(sv_cx, sv(0, HFIN_Z1)[1] - 4,
     f"hleg 立柱 {BRACKET_LEG_A:g} mm 高  /  Y 方向被两条 5×30 肋夹紧 (c-to-c {RIB_CC:g})",
     size=TXT_I, anchor="middle")
# Gusset hole Z position
vdim(sv(0, 0)[1], sv(0, GUSSET_HOLE_Z)[1],
     sv(-RIB_CC/2 - RIB_THICK/2 - 4, 0)[0],
     sv(-RIB_CC/2 - RIB_THICK/2 - 4, 0)[0] - DIM_O1,
     f"{GUSSET_HOLE_Z:g}")
# Rib height
vdim(sv(0, RIB_Z0)[1], sv(0, RIB_Z1)[1],
     sv(+RIB_CC/2 + RIB_THICK/2, 0)[0],
     sv(+RIB_CC/2 + RIB_THICK/2, 0)[0] + DIM_O1,
     f"{RIB_HEIGHT:g}")
# Disc thickness
vdim(sv(0, DISC_Z0)[1], sv(0, DISC_Z1)[1],
     sv(RIM_OD/2, 0)[0], sv(RIM_OD/2, 0)[0] + DIM_O1,
     f"{DISC_THICK:g}")
# Rim total
vdim(sv(0, 0)[1], sv(0, RIM_TOTAL_H)[1],
     sv(-RIM_OD/2, 0)[0], sv(-RIM_OD/2, 0)[0] - DIM_O1,
     f"{RIM_TOTAL_H:g}")

# ===== Title block =====
tb_y = PAGE_H - 28
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 装配 — rim_ring + rim_top_disc + l_bracket_170x60",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "比例 1:1 (俯, 侧)  /  非加工图,确认装配关系用",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Z stack: rim 0..{RIM_TOTAL_H:g} / disc {DISC_Z0:g}..{DISC_Z1:g} / 肋 {RIB_Z0:g}..{RIB_Z1:g} / 立板 {VLEG_Z0:g}..{VLEG_Z1:g} / hleg 立柱 {HFIN_Z0:g}..{HFIN_Z1:g}",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-10  /  POV3D / assembly_drawing.pdf",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("assembly_drawing.pdf")
try:
    pdf.output(str(out))
    print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("assembly_drawing.NEW.pdf")
    pdf.output(str(alt))
    print(f"wrote {alt}  (original {out.name} was locked)")
