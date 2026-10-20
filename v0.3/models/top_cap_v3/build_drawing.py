"""
A3 drawing (GB first-angle) for top_cap_v3 — the v3 rotor cap (double-screen
rotor: symmetric flat slab + two-leg clevis gripping the screen_plate_v3 tab).
Views: plan 1:1 (asm top face = print bed face: both CW banks, hidden legs,
axis) + side section 1.2:1 (Y=0 cut: slab 9, legs down to asm Z267, M3 hole
heights, head recess with its +1 overshoot notching the leg roots)
+ detail A 4:1 (counterweight counterbore, from the TOP face)
+ detail B 4:1 (axis head recess, from the BOTTOM face — opposite direction).
Geometry authority: build_cap.py (print coords; print_z = 292.7 - asm_z).
Layout / helpers carried over from models/top_bearing/build_drawing_cap_v2.py.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== geometry (mirror build_cap.py — symmetric slab, clevis at center) =====
SLAB_T = 9.0
TP_HX, TP_HW = 65.0, 72.0                      # slab 130 x 144
LEG_T, LEG_XI, LEG_HW = 4.0, 3.0, 36.0         # legs 4 thick, X +-(3..7), Y +-36
LEG_XO = LEG_XI + LEG_T                        # 7
CAPTOP, LEG_ZBOT_ASM = 292.7, 267.0
LEG_H = CAPTOP - LEG_ZBOT_ASM                  # 25.7 (local z: 0 = leg bottom)
SLAB_ZB = LEG_H - SLAB_T                       # 16.7 local (= asm 283.7)
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7
RC_CEIL = SLAB_ZB + HEAD_DEPTH                 # 19.4 local (recess ceiling)
RC_FLOOR = SLAB_ZB - 1.0                       # 15.7 local (+1 overshoot notch)
CBZ = LEG_H - HEAD_DEPTH                       # 23.0 local (CW CB floor)
M3_CLEAR, SCREW_Y = 3.4, 22.0
SCREW_ZLOC = [271.0 - LEG_ZBOT_ASM, 276.5 - LEG_ZBOT_ASM]   # 4.0 / 9.5
CW_M6, CW_TRI = 6.5, 14.0
CW_DX = CW_TRI * math.sin(math.radians(60))    # 12.12
CWA, CWB = 46.0, 46.0 + CW_DX                  # 46 / 58.12
CW_HOLES = []
for _sx in (1.0, -1.0):
    CW_HOLES += [(_sx * CWA, (k - 4.5) * CW_TRI) for k in range(10)]
    CW_HOLES += [(_sx * CWB, (k - 4.0) * CW_TRI) for k in range(9)]

PAGE_W, PAGE_H = 420.0, 297.0
GEOM_W, DIM_W, EXT_W, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W = 4.2, 1.5
EXT_OV, EXT_GP = 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 5.0, 8.0, 9.5, 5.0
DIM_O1 = 12.0
_FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
if not os.path.exists(_FONT): raise FileNotFoundError("SimHei not found")

pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", _FONT)
pdf.set_line_width(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")

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
        pdf.rect(x - 0.4, y - fh*0.85, sw + 0.8, fh*1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, ang, size=TXT_D, anchor="middle", halo=False):
    pdf.set_font("SimHei", "", size)
    sw = pdf.get_string_width(s)
    with pdf.rotation(angle=ang, x=cx, y=cy):
        dx = -sw/2 if anchor == "middle" else (-sw if anchor == "end" else 0)
        if halo:
            fh = pdf.font_size
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(cx + dx - 0.4, cy - fh*0.85, sw + 0.8, fh*1.1, style="F")
            pdf.set_fill_color(0, 0, 0)
        pdf.text(cx + dx, cy, s)
def _u(label):
    s = str(label).strip()
    return s if (not s or "mm" in s or "°" in s) else f"{s} mm"
def hdim(x1, x2, yg, yd, label):
    label = _u(label)
    if yd > yg: e1, e2 = yg + EXT_GP, yd + EXT_OV
    else:       e1, e2 = yg - EXT_GP, yd - EXT_OV
    line(x1, e1, x1, e2, EXT_W); line(x2, e1, x2, e2, EXT_W)
    xl, xr = (x1, x2) if x1 < x2 else (x2, x1)
    if xr - xl >= 2*ARR_L + 1:
        line(xl, yd, xr, yd, DIM_W); arrow(xl, yd, -1, 0); arrow(xr, yd, 1, 0)
    else:
        line(xl - ARR_L - 1, yd, xr + ARR_L + 1, yd, DIM_W)
        arrow(xl, yd, 1, 0); arrow(xr, yd, -1, 0)
    text((xl + xr)/2, yd - 1.8, label, anchor="middle", halo=True)
def vdim(y1, y2, xg, xd, label):
    label = _u(label)
    if xd > xg: e1, e2, to = xg+EXT_GP, xd+EXT_OV,  4.0
    else:       e1, e2, to = xg-EXT_GP, xd-EXT_OV, -4.0
    line(e1, y1, e2, y1, EXT_W); line(e1, y2, e2, y2, EXT_W)
    yt, yb = (y1, y2) if y1 < y2 else (y2, y1)
    gap = yb - yt
    if gap >= 2*ARR_L + 1:
        line(xd, yt, xd, yb, DIM_W); arrow(xd, yt, 0, -1); arrow(xd, yb, 0, 1)
    else:
        line(xd, yt - ARR_L - 1, xd, yb + ARR_L + 1, DIM_W)
        arrow(xd, yt, 0, 1); arrow(xd, yb, 0, -1)
    lh = pdf.get_string_width(label)
    if gap >= lh + 1.0:
        rot_text(xd + to, (yt + yb)/2, label, 90, anchor="middle", halo=True)
    else:
        rot_text(xd + to, yb + ARR_L + 1 + lh/2 + 1, label, 90, anchor="middle", halo=True)
def dash(on=True, d=1.5, g=1.0):
    if on: pdf.set_dash_pattern(dash=d, gap=g)
    else:  pdf.set_dash_pattern()

# ===== header =====
text(PAGE_W/2, 14, "POV 3D v3 — top_cap_v3  (v3 转子顶轴承帽, 双面屏转子, 对称一字型 + 双腿夹舌, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"对称一字板 {2*TP_HX:g}×{2*TP_HW:g}×{SLAB_T:g} (asm Z283.7..292.7, 顶面全平) + 双腿 {LEG_T:g}厚×2 @X±{LEG_XI:g}..±{LEG_XO:g} (净距6 夹舌, Y±{LEG_HW:g}, 下至Z267) / "
     f"中心Φ{M6_BORE:g}通+底面头窝Φ{HEAD_D:g}×{HEAD_DEPTH:g} / 4×Φ{M3_CLEAR:g} 沿X贯通双腿 (Y±{SCREW_Y:g}, Z271.0/276.5) / "
     f"配重两端对称 2×19×Φ{CW_M6:g} (行±{CWA:g}+±58.12, 品字{CW_TRI:g}, 顶面沉孔Φ{HEAD_D:g}×{HEAD_DEPTH:g})",
     size=TXT_I, anchor="middle")

# ============================================================
# PLAN VIEW 1:1  (asm, looking -Z at the flat top face = print bed face)
# pdf x = part Y + gx0 ; pdf y = gy0 - part X   (+X up)
# ============================================================
gx0, gy0 = 120.0, 114.0
def gv(x, y): return (gx0 + y, gy0 - x)
text(gx0, 27, "俯视 (1:1)  (沿 -Z 看装配顶面 = 打印贴床面)  尺寸单位: mm",
     size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(gv(TP_HX, -TP_HW)[0], gv(TP_HX, -TP_HW)[1],
         2*TP_HW, 2*TP_HX, style="D")                          # slab outline
# centerlines
dash(True, 3.0, 1.5); _w(0.15)
pdf.line(gx0, gv(TP_HX, 0)[1] - 4, gx0, 182.0)                 # Y=0 (vertical)
pdf.line(gv(0, -TP_HW)[0] - 4, gy0, gv(0, TP_HW)[0] + 2, gy0)  # X=0 (horizontal)
dash(False)
# clevis legs (hidden below the slab) + 4 x M3 hole marks
dash(True); _w(HID_W)
pdf.rect(gv(LEG_XO, -LEG_HW)[0], gv(LEG_XO, -LEG_HW)[1], 2*LEG_HW, LEG_T, style="D")
pdf.rect(gv(-LEG_XI, -LEG_HW)[0], gv(-LEG_XI, -LEG_HW)[1], 2*LEG_HW, LEG_T, style="D")
for sy in (-SCREW_Y, SCREW_Y):
    for (bx0, bx1) in ((LEG_XI, LEG_XO), (-LEG_XO, -LEG_XI)):
        for off in (-M3_CLEAR/2, M3_CLEAR/2):
            pdf.line(gv(bx0, sy + off)[0], gv(bx0, sy)[1],
                     gv(bx1, sy + off)[0], gv(bx1, sy)[1])
dash(False)
# axis hole: Φ6.2 (solid) + Φ13 head recess (hidden, bottom face)
_w(GEOM_W); pdf.circle(*gv(0, 0), M6_BORE/2, style="D")
dash(True); _w(HID_W); pdf.circle(*gv(0, 0), HEAD_D/2, style="D"); dash(False)
# counterweight banks both ends: Φ13 CB (top face, visible) + Φ6.5 through
_w(GEOM_W)
for (cx, cy) in CW_HOLES:
    pdf.circle(*gv(cx, cy), HEAD_D/2, style="D")
    pdf.circle(*gv(cx, cy), CW_M6/2, style="D")
# detail callouts: A on a row-B end hole (+X bank), B on the axis hole
_w(0.25); dash(True, 1.0, 0.8)
pdf.circle(*gv(CWB, -LEG_HW - 20.0), 9.0, style="D")           # (58.12, -56)
pdf.circle(*gv(0, 0), 9.0, style="D")
dash(False)
text(50, 46, "A", size=TXT_L)
text(gv(0, 0)[0] + 10.5, gv(0, 0)[1] - 8.5, "B", size=TXT_L)
# --- dims ---
hdim(gv(LEG_XO, -SCREW_Y)[0], gv(LEG_XO, SCREW_Y)[0],
     gv(LEG_XO, 0)[1], 42.0, "44 (=2×22)")                     # M3 span
hdim(gv(LEG_XO, -LEG_HW)[0], gv(LEG_XO, LEG_HW)[0],
     gv(LEG_XO, 0)[1], 35.0, f"{2*LEG_HW:g}")                  # 72 leg width
hdim(gv(-TP_HX, -TP_HW)[0], gv(-TP_HX, TP_HW)[0],
     gv(-TP_HX, 0)[1], 186.0, f"{2*TP_HW:g}")                  # 144
hdim(gv(-CWB, -4*CW_TRI)[0], gv(-CWB, -3*CW_TRI)[0],
     gv(-CWB, 0)[1], 194.0, f"{CW_TRI:g}")                     # pitch 14 (row B)
vdim(gv(TP_HX, 0)[1], gv(-TP_HX, 0)[1],
     gv(0, -TP_HW)[0], gv(0, -TP_HW)[0] - 10, f"{2*TP_HX:g}")  # 130
vdim(gv(0, 0)[1], gv(-CWA, 0)[1], gv(0, TP_HW)[0], 202.0, "46")
vdim(gv(-CWA, 0)[1], gv(-CWB, 0)[1], gv(0, TP_HW)[0], 210.0, "12.12")
vdim(gv(0, 0)[1], gv(-CWB, 0)[1], gv(0, TP_HW)[0], 219.0, "58.12")
# notes under the plan
text(gx0, 201, f"配重两端对称 2×19×Φ{CW_M6:g} 通: 行 X=±{CWA:g} 各10孔 (Y=(k-4.5)×14) / X=±58.12 各9孔 (Y=(k-4)×14), 品字形, 沉孔见详图A",
     size=TXT_I, anchor="middle", halo=True)
text(gx0, 207, f"双腿 (虚线, 板下方) 各{LEG_T:g}厚 @X ±{LEG_XI:g}..±{LEG_XO:g}, 4×Φ{M3_CLEAR:g} @Y=±{SCREW_Y:g} 沿X贯通 (M3×18); 中心 Φ{M6_BORE:g} 通 + 底面头窝 Φ{HEAD_D:g}×{HEAD_DEPTH:g} (虚线, 详图B)",
     size=TXT_I, anchor="middle", halo=True)

# ============================================================
# SIDE SECTION 1.2:1  (asm, looking +Y, cutting plane Y = 0)
# local z: 0 = leg bottom (asm 267) .. 25.7 = top face (asm 292.7)
# ============================================================
PS = 1.2
px0, py0 = 332.0, 100.0
def pv(x, z): return (px0 + PS*x, py0 - PS*z)
text(px0, 50, "侧视剖面 (1.2:1)  (沿 +Y 看, 剖切面 Y=0) — 对称一字型, 双腿夹舌",
     size=TXT_L, anchor="middle")
br, hr, cr = M6_BORE/2, HEAD_D/2, CW_M6/2
ZT, ZB = LEG_H, SLAB_ZB
_w(GEOM_W)
for sx in (1.0, -1.0):
    pairs = [
        # top face, broken by the row-B CW CB and the axis bore
        ((br, ZT), (CWB - hr, ZT)), ((CWB + hr, ZT), (TP_HX, ZT)),
        # CW hole: Φ13×2.7 CB from the top + Φ6.5 through
        ((CWB - hr, ZT), (CWB - hr, CBZ)), ((CWB + hr, ZT), (CWB + hr, CBZ)),
        ((CWB - hr, CBZ), (CWB - cr, CBZ)), ((CWB + cr, CBZ), (CWB + hr, CBZ)),
        ((CWB - cr, CBZ), (CWB - cr, ZB)), ((CWB + cr, CBZ), (CWB + cr, ZB)),
        # outer edge + slab bottom face (broken at the CW bore and the leg)
        ((TP_HX, ZT), (TP_HX, ZB)),
        ((TP_HX, ZB), (CWB + cr, ZB)), ((CWB - cr, ZB), (LEG_XO, ZB)),
        # leg down to asm Z267
        ((LEG_XO, ZB), (LEG_XO, 0)), ((LEG_XO, 0), (LEG_XI, 0)),
        ((LEG_XI, 0), (LEG_XI, RC_FLOOR)),
        # head recess Φ13: +1 overshoot notches the leg root (floor 15.7)
        ((LEG_XI, RC_FLOOR), (hr, RC_FLOOR)), ((hr, RC_FLOOR), (hr, RC_CEIL)),
        ((hr, RC_CEIL), (br, RC_CEIL)),
        # axis bore Φ6.2 up to the top face
        ((br, RC_CEIL), (br, ZT)),
    ]
    for (a, b) in pairs:
        line(*pv(sx*a[0], a[1]), *pv(sx*b[0], b[1]), GEOM_W)
# 4 x M3 holes through both legs (off-plane at Y=±22 — hidden projection)
dash(True); _w(HID_W)
for zc in SCREW_ZLOC:
    for (bx0, bx1) in ((LEG_XI, LEG_XO), (-LEG_XO, -LEG_XI)):
        for off in (-M3_CLEAR/2, M3_CLEAR/2):
            pdf.line(*pv(bx0, zc + off), *pv(bx1, zc + off))
dash(False)
# centerlines: axis, both row-B CW holes, M3 holes
dash(True, 3.0, 1.5); _w(0.15)
pdf.line(*pv(0, ZT + 2), *pv(0, -2))
for sx in (1.0, -1.0):
    pdf.line(*pv(sx*CWB, ZT + 1.5), *pv(sx*CWB, ZB - 1.5))
for zc in SCREW_ZLOC:
    pdf.line(*pv(-10, zc), *pv(10, zc))
dash(False)
# detail callouts
_w(0.25); dash(True, 1.0, 0.8)
pdf.circle(*pv(CWB, ZT - 1.2), 8.0, style="D")
pdf.circle(pv(0, 17.5)[0], pv(0, 17.5)[1], 9.0, style="D")
dash(False)
text(384, 66, "A", size=TXT_L)
text(320, 65, "B", size=TXT_L)
# --- dims ---
hdim(pv(-TP_HX, 0)[0], pv(0, 0)[0], pv(0, ZT)[1], 61.5, f"{TP_HX:g}")
hdim(pv(0, 0)[0], pv(TP_HX, 0)[0], pv(0, ZT)[1], 61.5, f"{TP_HX:g}")
vdim(pv(0, ZT)[1], pv(0, ZB)[1], pv(-TP_HX, 0)[0], 246.0, f"{SLAB_T:g}")   # 9
vdim(pv(0, ZB)[1], pv(0, 0)[1], pv(-TP_HX, 0)[0], 246.0, f"{ZB:g}")        # 16.7
vdim(pv(0, ZT)[1], pv(0, 0)[1], pv(-TP_HX, 0)[0], 237.0, f"{LEG_H:g}")     # 25.7
hdim(pv(LEG_XI, 0)[0], pv(LEG_XO, 0)[0], pv(0, 0)[1], 106.0, f"{LEG_T:g}") # 4
hdim(pv(-LEG_XI, 0)[0], pv(LEG_XI, 0)[0], pv(0, 0)[1], 113.0, "6")         # gap 6
vdim(pv(0, SCREW_ZLOC[0])[1], pv(0, 0)[1], pv(-LEG_XO, 0)[0], 314.0,
     f"{SCREW_ZLOC[0]:g}")                                                 # 4
vdim(pv(0, SCREW_ZLOC[1])[1], pv(0, 0)[1], pv(-LEG_XO, 0)[0], 304.0,
     f"{SCREW_ZLOC[1]:g}")                                                 # 9.5
text(px0, 121, "腿底 asm Z267 (屏顶264.7 留2.3) / M3孔心 asm Z271.0·276.5 = 腿底+4.0·9.5 (打印z 21.7·16.2) / 顶面 asm Z292.7",
     size=TXT_I, anchor="middle", halo=True)

# ============================================================
# DETAIL A (4:1) — counterweight counterbore, cut FROM THE TOP face
# ============================================================
DS = 4.0; dax, daz = 242.0, 205.0
def da(x, z): return (dax + DS*x, daz - DS*z)     # z: 0=slab bottom .. 9=top
text(dax + 32, 148, "详图 A (4:1)  配重沉孔 — 顶面(床面)进", size=TXT_L, anchor="middle")
cbz = SLAB_T - HEAD_DEPTH   # 6.3
_w(GEOM_W)
for a, b in [((0,0),(8-cr,0)),((8-cr,0),(8-cr,cbz)),((8-cr,cbz),(8-hr,cbz)),
             ((8-hr,cbz),(8-hr,SLAB_T)),((8-hr,SLAB_T),(0,SLAB_T)),((0,SLAB_T),(0,0))]:
    line(*da(*a), *da(*b), GEOM_W)
for a, b in [((16,0),(8+cr,0)),((8+cr,0),(8+cr,cbz)),((8+cr,cbz),(8+hr,cbz)),
             ((8+hr,cbz),(8+hr,SLAB_T)),((8+hr,SLAB_T),(16,SLAB_T)),((16,SLAB_T),(16,0))]:
    line(*da(*a), *da(*b), GEOM_W)
dash(True, 1.2, 0.8); _w(0.13)
pdf.line(*da(8, SLAB_T + 1), *da(8, -1)); dash(False)
hdim(da(8-hr,SLAB_T)[0], da(8+hr,SLAB_T)[0], da(8,SLAB_T)[1], da(8,SLAB_T)[1]-DIM_O1, f"Φ{HEAD_D:g}")
hdim(da(8-cr,0)[0], da(8+cr,0)[0], da(8,0)[1], da(8,0)[1]+DIM_O1, f"Φ{CW_M6:g} 通")
vdim(da(0,cbz)[1], da(0,SLAB_T)[1], da(0,0)[0], da(0,0)[0]-DIM_O1, f"{HEAD_DEPTH:g}")
text(dax - 10, 224, "M6 平头 (Φ12.5×2.6) 沉平; 顶面 = 打印贴床面", size=TXT_I)

# ============================================================
# DETAIL B (4:1) — axis head recess, cut FROM THE BOTTOM face
# ============================================================
dbx, dbz = 330.0, 205.0
def db(x, z): return (dbx + DS*x, dbz - DS*z)     # z: 0=slab bottom .. 9=top
text(dbx + 36, 148, "详图 B (4:1)  轴孔头窝 — 底面进 (与A反向)", size=TXT_L, anchor="middle")
_w(GEOM_W)
for a, b in [((0,0),(9-hr,0)),((9-hr,0),(9-hr,HEAD_DEPTH)),((9-hr,HEAD_DEPTH),(9-br,HEAD_DEPTH)),
             ((9-br,HEAD_DEPTH),(9-br,SLAB_T)),((9-br,SLAB_T),(0,SLAB_T)),((0,SLAB_T),(0,0))]:
    line(*db(*a), *db(*b), GEOM_W)
for a, b in [((18,0),(9+hr,0)),((9+hr,0),(9+hr,HEAD_DEPTH)),((9+hr,HEAD_DEPTH),(9+br,HEAD_DEPTH)),
             ((9+br,HEAD_DEPTH),(9+br,SLAB_T)),((9+br,SLAB_T),(18,SLAB_T)),((18,SLAB_T),(18,0))]:
    line(*db(*a), *db(*b), GEOM_W)
dash(True, 1.2, 0.8); _w(0.13)
pdf.line(*db(9, SLAB_T + 1), *db(9, -1)); dash(False)
hdim(db(9-br,SLAB_T)[0], db(9+br,SLAB_T)[0], db(9,SLAB_T)[1], db(9,SLAB_T)[1]-DIM_O1, f"Φ{M6_BORE:g} 通")
hdim(db(9-hr,0)[0], db(9+hr,0)[0], db(9,0)[1], db(9,0)[1]+DIM_O1, f"Φ{HEAD_D:g}")
vdim(db(0,0)[1], db(0,HEAD_DEPTH)[1], db(0,0)[0], db(0,0)[0]-DIM_O1, f"{HEAD_DEPTH:g}")
vdim(db(0,0)[1], db(0,SLAB_T)[1], db(0,0)[0], db(0,0)[0]-20, f"{SLAB_T:g}")
text(dbx - 14, 224, "M6×40 平头自底面入 (头 asm 283.7..286.4); 头窝越程+1 切入腿根 (见剖面)", size=TXT_I)

# ===== assembly / print notes (bottom left, under the plan) =====
nx = 20.0
text(nx, 216, "打印姿态: 板顶面 (asm Z292.7) 朝下贴床, 双腿朝上, 免支撑; 打印 z = 292.7 - asm Z", size=TXT_I)
text(nx, 222, "对称一字帽: 双腿 4厚 @X ±3..±7 (内面净距 6) 夹 screen_plate_v3 中央顶舌 (6厚, Y±40); 腿底 Z267 距屏顶 264.7 留 2.3", size=TXT_I)
text(nx, 228, "轴系: M6×40 平头自板底面头窝入 → Φ8×50 M6内丝螺柱 → 2×688; 舌顶 280.7 距头底仅 3 → 必须先装 M6 再夹舌!", size=TXT_I)
text(nx, 234, "夹舌固定: M3×18 ×4 沿 X 贯通 (腿4+舌6+腿4=14) + 垫片+螺母; 孔 Φ3.4 @ Y=±22, asm Z=271.0 / 276.5", size=TXT_I)
text(nx, 240, "配重: 两端对称各 19×Φ6.5 (共38), 行 X=±46 (10孔) / X=±58.12 (9孔), M6 平头自顶面沉孔入+螺母 对称配平", size=TXT_I)

# ===== title block =====
tb_y, tb_x, tb_w, tb_h = PAGE_H - 28, 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D — v3 / top_cap_v3 (v3 转子顶轴承帽) (×1)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6, "投影 1st-angle / PLA / 单位 mm", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     "对称一字帽, 双腿夹 screen_plate_v3 顶舌; M6×40 先装后夹舌 / 板9厚 130×144, 腿4厚 高25.7 / "
     "BOM: M6×40平头×1, Φ8×50螺柱(M6内丝)×1, M3×18×4+垫片螺母, M6平头配重+螺母按需", size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5, "2026-07-10 / POV3D / v3 / models / top_cap_v3",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("top_cap_v3_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("top_cap_v3_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt} (original locked)")
