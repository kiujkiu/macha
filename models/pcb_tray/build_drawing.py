"""
A3 landscape 2D engineering drawing for POV3D pcb_tray (PCB test jig).
Three views:
  1) TOP VIEW (1:1) — jig outline + PCB pocket outline + 4 finger cutouts +
                      33 × Φ1.0 probe through-hole positions (matching PCB M0.8)
  2) BOTTOM VIEW (1:1) — solid bottom showing only the probe-hole pattern
  3) SECTION A-A (1:1) — cut along +Y axis, showing pocket depth, floor
                          thickness, total height, finger cutout in section.

Outline & hole data are read from pcb_outline_points.json (produced by
build_stl.py).
"""
import json
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Load outline + parameters =====
data = json.load(open(Path(__file__).with_name("pcb_outline_points.json")))
PCB_PTS = data["pcb_pts_local"]
PCB_DX, PCB_DY = data["pcb_bbox"]
HOLES = data["m08_holes"]
MOUNT_HOLES = data.get("mount_holes", [])
p = data["params"]

PCB_CLEARANCE = p["PCB_CLEARANCE"]
POCKET_DEPTH  = p["POCKET_DEPTH"]
FLOOR_THICK   = p["FLOOR_THICK"]
JIG_BORDER    = p["JIG_BORDER"]
JIG_R_CORNER  = p["JIG_R_CORNER"]
CORNER_SIZE   = p["CORNER_SIZE"]
SCALLOP_W      = p["SCALLOP_W"]
SCALLOP_REACH  = p.get("SCALLOP_REACH", 2.0)
SCALLOP_DEPTH  = p["SCALLOP_DEPTH"]
MOUNT_DIAM    = p.get("MOUNT_DIAM", 3.2)
PROBE_DIAM    = p["PROBE_DIAM"]
JIG_DX        = p["JIG_DX"]
JIG_DY        = p["JIG_DY"]
TOTAL_H       = p["TOTAL_H"]

PCB_HX, PCB_HY = PCB_DX / 2, PCB_DY / 2
JIG_HX, JIG_HY = JIG_DX / 2, JIG_DY / 2

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
_font_paths = ["/mnt/c/Windows/Fonts/simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"]
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
TXT_D  = 4.5
TXT_L  = 7.5
TXT_T  = 9.0
TXT_I  = 4.5
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
    text((x_l + x_r) / 2, yd - 1.6, label, anchor="middle")

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
text(PAGE_W/2, 13, "POV 3D PCB 测试治具  PCB Test Jig (T200)", size=TXT_T, anchor="middle")
text(PAGE_W/2, 18.5,
     f"{JIG_DX:.1f}×{JIG_DY:.1f}×{TOTAL_H:.0f} 治具 / "
     f"底板 {FLOOR_THICK:g} + 4 角块墙 {CORNER_SIZE:g}方 × {POCKET_DEPTH:g}高 / "
     f"上/下指坑沿 PCB 外形 内偏 {SCALLOP_REACH:g} 深 {SCALLOP_DEPTH:g} (宽 {SCALLOP_W:g}) / "
     f"4 × Φ{MOUNT_DIAM:g} M3 固定通孔 / "
     f"{len(HOLES)} × Φ{PROBE_DIAM:g} 探针通孔 (PCB M0.8 位)",
     size=TXT_I, anchor="middle")

# ===== Helper: draw rounded-rect outline =====
def draw_rounded_rect(cx, cy, dx, dy, r, scale=1.0):
    """Draw rounded-rect outline centered at (cx, cy) in PDF coords. dx/dy/r in real mm."""
    hx = dx/2 * scale - r * scale
    hy = dy/2 * scale - r * scale
    rs = r * scale
    # Sides
    pdf.line(cx - hx, cy - hy - rs, cx + hx, cy - hy - rs)   # top side (PDF y is inverted)
    pdf.line(cx - hx, cy + hy + rs, cx + hx, cy + hy + rs)   # bottom side
    pdf.line(cx - hx - rs, cy - hy, cx - hx - rs, cy + hy)   # left side
    pdf.line(cx + hx + rs, cy - hy, cx + hx + rs, cy + hy)   # right side
    # Corner arcs (approximated by short polyline segments)
    nseg = 16
    for cqx, cqy, a0 in [(cx + hx, cy - hy, -math.pi/2),
                         (cx + hx, cy + hy, 0.0),
                         (cx - hx, cy + hy, math.pi/2),
                         (cx - hx, cy - hy, math.pi)]:
        prev = None
        for i in range(nseg + 1):
            a = a0 + (math.pi/2) * i / nseg
            px = cqx + rs * math.cos(a)
            py = cqy + rs * math.sin(a)
            if prev is not None:
                pdf.line(prev[0], prev[1], px, py)
            prev = (px, py)

def draw_polyline_mm(cx, cy, pts, scale=1.0, close=True):
    """Draw closed polyline (list of (x, y) in mm) centered at PDF (cx, cy).
    PDF y is inverted: world +Y → PDF -y."""
    n = len(pts)
    for i in range(n - (0 if close else 1)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        pdf.line(cx + x1 * scale, cy - y1 * scale,
                 cx + x2 * scale, cy - y2 * scale)

def draw_rect_mm(cx, cy, ox, oy, dx, dy, scale=1.0):
    """Rectangle centered at (cx + ox*scale, cy - oy*scale) with size dx*dy."""
    x = cx + ox * scale - dx/2 * scale
    y = cy - oy * scale - dy/2 * scale
    pdf.rect(x, y, dx * scale, dy * scale, style='D')

# ===== TOP VIEW (1:1) =====
tv_cx, tv_cy = 110, 145
SCALE = 1.0

text(tv_cx, 38, "俯视图  Top View  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# Jig outline (solid)
_w(GEOM_W)
draw_rounded_rect(tv_cx, tv_cy, JIG_DX, JIG_DY, JIG_R_CORNER, SCALE)

# PCB pocket outline (PCB outline + clearance), drawn as solid line on top face
# = the inner edge of the wall.
pocket_pts = [(x * (1 + 0), y * (1 + 0)) for x, y in PCB_PTS]   # placeholder; we draw PCB outline directly
draw_polyline_mm(tv_cx, tv_cy, PCB_PTS, SCALE)

# 4 corner walls (solid rectangles at jig corners — only retained wall material)
def corner_rect_box(sx, sy):
    cx = sx * (JIG_HX - CORNER_SIZE/2)
    cy = sy * (JIG_HY - CORNER_SIZE/2)
    # Draw the square boundary
    pdf.rect(tv_cx + cx*SCALE - CORNER_SIZE*SCALE/2,
             tv_cy - cy*SCALE - CORNER_SIZE*SCALE/2,
             CORNER_SIZE*SCALE, CORNER_SIZE*SCALE, style='D')

for sx in (-1, 1):
    for sy in (-1, 1):
        corner_rect_box(sx, sy)

# Top + bottom scallops follow the PCB outline (offset INWARD by SCALLOP_REACH).
# Compute the scallop polygon using shapely and draw its boundary as dashed.
from shapely.geometry import Polygon as _ShpPoly, box as _shp_box
_pcb_poly = _ShpPoly(PCB_PTS).buffer(0)
_pcb_inset = _pcb_poly.buffer(-SCALLOP_REACH, join_style=1)
_SC_HX = SCALLOP_W / 2
_top_rect = _shp_box(-_SC_HX, 0, _SC_HX, JIG_HY + 1)
_bot_rect = _shp_box(-_SC_HX, -JIG_HY - 1, _SC_HX, 0)
_top_scallop = _top_rect.difference(_pcb_inset)
_bot_scallop = _bot_rect.difference(_pcb_inset)

def _draw_shapely(poly):
    if poly.is_empty: return
    polys = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
    for q in polys:
        coords = list(q.exterior.coords)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            pdf.line(tv_cx + x1*SCALE, tv_cy - y1*SCALE,
                     tv_cx + x2*SCALE, tv_cy - y2*SCALE)

pdf.set_dash_pattern(dash=2.5, gap=1.2); _w(HID_W)
_draw_shapely(_top_scallop)
_draw_shapely(_bot_scallop)
pdf.set_dash_pattern(); _w(GEOM_W)

# Probe holes (Φ1.0): small solid circles + crosshair
_w(GEOM_W)
for (hx, hy) in HOLES:
    cx, cy = tv_cx + hx*SCALE, tv_cy - hy*SCALE
    pdf.circle(cx, cy, PROBE_DIAM/2 * SCALE, style="D")
    pdf.set_dash_pattern(dash=0.8, gap=0.4); _w(0.10)
    pdf.line(cx - 1.2, cy, cx + 1.2, cy)
    pdf.line(cx, cy - 1.2, cx, cy + 1.2)
    pdf.set_dash_pattern(); _w(GEOM_W)

# 4 × M3 mounting through-holes (Φ3.2): bigger circles + crosshair
for (hx, hy) in MOUNT_HOLES:
    cx, cy = tv_cx + hx*SCALE, tv_cy - hy*SCALE
    pdf.circle(cx, cy, MOUNT_DIAM/2 * SCALE, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(cx - 3.5, cy, cx + 3.5, cy)
    pdf.line(cx, cy - 3.5, cx, cy + 3.5)
    pdf.set_dash_pattern(); _w(GEOM_W)

# Section A-A cutting line
pdf.set_dash_pattern(dash=6, gap=2); _w(0.18)
pdf.line(tv_cx, tv_cy - (JIG_HY + 6)*SCALE, tv_cx, tv_cy + (JIG_HY + 6)*SCALE)
pdf.set_dash_pattern()
text(tv_cx - 5, tv_cy - (JIG_HY + 6)*SCALE - 1, "A", size=5)
text(tv_cx - 5, tv_cy + (JIG_HY + 6)*SCALE + 6, "A", size=5)

# Top-view dims
hdim(tv_cx - JIG_HX*SCALE, tv_cx + JIG_HX*SCALE,
     tv_cy + JIG_HY*SCALE, tv_cy + JIG_HY*SCALE + DIM_O1, f"{JIG_DX:.2f}")
vdim(tv_cy - JIG_HY*SCALE, tv_cy + JIG_HY*SCALE,
     tv_cx + JIG_HX*SCALE, tv_cx + JIG_HX*SCALE + DIM_O1, f"{JIG_DY:.2f}")
hdim(tv_cx - PCB_HX*SCALE, tv_cx + PCB_HX*SCALE,
     tv_cy + JIG_HY*SCALE, tv_cy + JIG_HY*SCALE + DIM_O2, f"PCB {PCB_DX:.2f}")
vdim(tv_cy - PCB_HY*SCALE, tv_cy + PCB_HY*SCALE,
     tv_cx + JIG_HX*SCALE, tv_cx + JIG_HX*SCALE + DIM_O2, f"PCB {PCB_DY:.2f}")
# Scallop width
hdim(tv_cx - SCALLOP_W*SCALE/2, tv_cx + SCALLOP_W*SCALE/2,
     tv_cy - JIG_HY*SCALE, tv_cy - JIG_HY*SCALE - DIM_O1, f"{SCALLOP_W:g}")
# Corner square size (on top-right corner)
crx = JIG_HX - CORNER_SIZE
hdim(tv_cx + crx*SCALE, tv_cx + JIG_HX*SCALE,
     tv_cy - JIG_HY*SCALE, tv_cy - JIG_HY*SCALE - DIM_O1, f"{CORNER_SIZE:g}")

# Callouts (right side, in clear space between top view and section view)
_w(EXT_W)
cb_x = tv_cx + JIG_HX*SCALE + 38
cb_y = 50
text(cb_x, cb_y,
     f"底板厚 {FLOOR_THICK:g} mm  /  角块墙高 {POCKET_DEPTH:g} mm  /  PCB 间隙 +{PCB_CLEARANCE:g} mm",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 6,
     f"4 × 角块墙 {CORNER_SIZE:g} × {CORNER_SIZE:g} mm (仅 4 角固定 PCB)",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 12,
     f"上/下指坑沿 PCB 外形, 向 PCB 内偏 {SCALLOP_REACH:g}, 宽 {SCALLOP_W:g}",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 17,
     f"挖深 {SCALLOP_DEPTH:g} (从底板顶面向下), 保留底部 {FLOOR_THICK-SCALLOP_DEPTH:g} mm 底",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 23,
     f"4 × Φ{MOUNT_DIAM:g} M3 固定通孔 (距治具外缘 4 mm)",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 29,
     f"{len(HOLES)} × Φ{PROBE_DIAM:g} 探针通孔 (XY 取自 PCB M0.8 孔位)",
     size=TXT_D, anchor="start")
text(cb_x, cb_y + 35,
     f"打印方向: 底面贴床, 打印高度 {TOTAL_H:g} mm",
     size=TXT_D, anchor="start")

# ===== SECTION A-A (1:1) =====
# Cut along +Y axis through jig center
sa_cx, sa_cy = 310, 145
def sa(t, z): return (sa_cx + t, sa_cy - z)

text(sa_cx, 80, "剖视图  Section A-A  (1:1)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sa_cx, 86, "(沿 +Y 轴剖切, 过上/下指坑 / cut along +Y axis through top/bottom scallops)",
     size=TXT_I, anchor="middle")

# In Section A-A:
#   - t corresponds to real Y (since cut is along +Y, the section plane = XZ plane)
#   - the PCB pocket shape AT X=0 cross-section depends on PCB outline at X=0
#   - PCB extends from Y = -PCB_HY to +PCB_HY (with irregular shape, but at x=0 it
#     looks roughly like: top edge at Y_max_actual at x=0 (the recessed area ~14.2),
#     bottom edge at -PCB_HY)
# For simplicity in the section, draw the pocket as if PCB were a rectangle bbox.
# The actual pocket has more complex shape; this is a representative section.

# Section profile at X=0: corner walls are off-axis (x=±26..36) so NOT visible
# here. Section shows the base with the 2 top/bottom THROUGH-cuts (scallops
# cut all the way through the base now), so the base is fully missing at the
# scallop regions.

# Scallop at X=0 cross-section: scallop inner edges depend on PCB outline at X=0
# Top: PCB tab top at y≈14.69, minus SCALLOP_REACH → scallop inner ≈ 12.69
# Bottom: PCB straight bottom at y≈-22.685, plus SCALLOP_REACH → scallop inner ≈ -20.685
st_y_top = 14.69 - SCALLOP_REACH    # PCB tab top minus reach
st_y_bot = -22.685 + SCALLOP_REACH  # PCB bottom edge plus reach
z_scallop_floor = FLOOR_THICK - SCALLOP_DEPTH  # 1

_w(GEOM_W)
# Section profile of the base (T-shape): full-width slab z=0..1 with a
# central hump z=1..3 between the two scallop inner edges.
line(*sa(-JIG_HY, 0), *sa( JIG_HY, 0), GEOM_W)                                  # bottom
line(*sa( JIG_HY, 0), *sa( JIG_HY, z_scallop_floor), GEOM_W)                   # right edge
line(*sa( JIG_HY, z_scallop_floor), *sa( st_y_top, z_scallop_floor), GEOM_W)   # top of right scallop floor
line(*sa( st_y_top, z_scallop_floor), *sa( st_y_top, FLOOR_THICK), GEOM_W)     # step up (right inner wall)
line(*sa( st_y_top, FLOOR_THICK), *sa( st_y_bot, FLOOR_THICK), GEOM_W)         # central base top
line(*sa( st_y_bot, FLOOR_THICK), *sa( st_y_bot, z_scallop_floor), GEOM_W)     # step down (left inner wall)
line(*sa( st_y_bot, z_scallop_floor), *sa(-JIG_HY, z_scallop_floor), GEOM_W)   # top of left scallop floor
line(*sa(-JIG_HY, z_scallop_floor), *sa(-JIG_HY, 0), GEOM_W)                   # left edge

# Corner walls + their solid base support (off-axis at X=0) shown as dashed
pdf.set_dash_pattern(dash=1.8, gap=1.2); _w(HID_W)
for sy in (-1, 1):
    # Base at the corner-wall area is FULL thickness (no scallop here) — z=0..3
    pdf.line(*sa(sy*PCB_HY, 0), *sa(sy*JIG_HY, 0))
    pdf.line(*sa(sy*PCB_HY, FLOOR_THICK), *sa(sy*JIG_HY, FLOOR_THICK))
    pdf.line(*sa(sy*JIG_HY, 0), *sa(sy*JIG_HY, FLOOR_THICK))
    pdf.line(*sa(sy*PCB_HY, 0), *sa(sy*PCB_HY, FLOOR_THICK))
    # Corner wall on top of base z=3..5
    pdf.line(*sa(sy*PCB_HY, FLOOR_THICK), *sa(sy*PCB_HY, TOTAL_H))
    pdf.line(*sa(sy*JIG_HY, FLOOR_THICK), *sa(sy*JIG_HY, TOTAL_H))
    pdf.line(*sa(sy*PCB_HY, TOTAL_H), *sa(sy*JIG_HY, TOTAL_H))
pdf.set_dash_pattern(); _w(GEOM_W)

# PCB hint (1.6 mm thick, dashed) sitting at z = FLOOR_THICK .. FLOOR_THICK + 1.6
pdf.set_dash_pattern(dash=2, gap=1.2); _w(0.2)
pcb_z0 = FLOOR_THICK
pcb_z1 = FLOOR_THICK + 1.6
pdf.line(*sa(-PCB_HY, pcb_z0), *sa(PCB_HY, pcb_z0))
pdf.line(*sa(-PCB_HY, pcb_z1), *sa(PCB_HY, pcb_z1))
pdf.line(*sa(-PCB_HY, pcb_z0), *sa(-PCB_HY, pcb_z1))
pdf.line(*sa( PCB_HY, pcb_z0), *sa( PCB_HY, pcb_z1))
pdf.set_dash_pattern(); _w(GEOM_W)
text(*sa(0, pcb_z0 + 0.8), "PCB (1.6)", size=TXT_I, anchor="middle")

# ----- Section dims -----
right_dim_x  = sa(JIG_HY, 0)[0] + DIM_O1
right_dim_x2 = sa(JIG_HY, 0)[0] + DIM_O2
# Total height
vdim(sa(0, TOTAL_H)[1], sa(0, 0)[1],
     sa(JIG_HY, 0)[0], right_dim_x, f"{TOTAL_H:g}")
# Floor thickness (base)
vdim(sa(0, FLOOR_THICK)[1], sa(0, 0)[1],
     sa(JIG_HY, 0)[0], right_dim_x2, f"{FLOOR_THICK:g}")
# Corner wall height (boss) — dashed reference
vdim(sa(0, TOTAL_H)[1], sa(0, FLOOR_THICK)[1],
     sa(-JIG_HY, 0)[0], sa(-JIG_HY, 0)[0] - DIM_O1, f"{POCKET_DEPTH:g}")
# Scallops are 2mm scoops (1mm floor remains): inline labels
text(*sa((st_y_top + JIG_HY)/2, FLOOR_THICK + 1.0),
     f"上指坑 -{SCALLOP_DEPTH:g}", size=TXT_D, anchor="middle")
text(*sa((st_y_bot - JIG_HY)/2, FLOOR_THICK + 1.0),
     f"下指坑 -{SCALLOP_DEPTH:g}", size=TXT_D, anchor="middle")

# Bottom dims: overall + PCB span hint
hdim(sa(-JIG_HY, 0)[0], sa(JIG_HY, 0)[0],
     sa(0, 0)[1], sa(0, 0)[1] + DIM_O2, f"{JIG_DY:.2f}")
hdim(sa(-PCB_HY, 0)[0], sa(PCB_HY, 0)[0],
     sa(0, 0)[1], sa(0, 0)[1] + DIM_O1, f"PCB {PCB_DY:.2f}")

# ===== Title block =====
tb_y = PAGE_H - 28
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6,
     "POV 3D 结构件 — PCB 测试治具 (PCB Test Jig)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯, 剖)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"治具 {JIG_DX:.1f}×{JIG_DY:.1f}×{TOTAL_H:.0f} / 底板 {FLOOR_THICK:g} + 4 角块墙 {CORNER_SIZE:g}×{POCKET_DEPTH:g} / "
     f"上下指坑 {SCALLOP_W:g} 宽 × {SCALLOP_DEPTH:g} 深 / 4 × Φ{MOUNT_DIAM:g} M3 固定 / "
     f"{len(HOLES)} × Φ{PROBE_DIAM:g} 探针孔  /  单位 mm",
     size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-06-09  /  POV3D / models / pcb_tray / pcb_tray.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("pcb_tray_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
