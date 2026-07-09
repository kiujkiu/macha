"""
A3 drawing (GB first-angle) for top_cap_v2 — the v2 rotor cap.
Views: plan 1:1 (hole bank + leg + axis, fully dimensioned) + side section 2:1
(Y=0 cut: slab 9, leg 45.7 down to asm Z247, M3 hole at Z253.2, head recess)
+ detail A 4:1 (counterweight counterbore, from the TOP face)
+ detail B 4:1 (axis head recess, from the BOTTOM face — opposite direction).
Layout / helpers carried over from build_drawing.py.
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== geometry (mirror build_cap_v2.py — L shape, leg at the +X end) =====
SLAB_T = 9.0
TP_X0, TP_X1, TP_HW = -65.0, 17.27, 72.0       # slab 82.27 x 144
LEG_X0, LEG_X1, LEG_HW = 13.27, 17.27, 56.0    # leg 4 x 112, outer face flush w/ slab +X edge
LEG_H = 45.7                                   # asm Z 247..292.7
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7
M3_CLEAR, SCREW_Y = 3.4, 49.975                # M3 holes @ asm Z253.2 (leg bottom +6.2)
SCREW_ZLOC = 6.2                               # above leg bottom (asm 247)
CW_M6, CW_TRI = 6.5, 14.0
CW_DX = CW_TRI * math.sin(math.radians(60))    # 12.12
CWA_X, CWB_X = -46.0, -46.0 - CW_DX            # -46 / -58.12
CW_A = [(CWA_X, (k - 4.5) * CW_TRI) for k in range(10)]
CW_B = [(CWB_X, (k - 4.0) * CW_TRI) for k in range(9)]

PAGE_W, PAGE_H = 420.0, 297.0
GEOM_W, DIM_W, EXT_W, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W = 4.2, 1.5
EXT_OV, EXT_GP = 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 5.0, 8.0, 9.5, 5.0
DIM_O1, DIM_O2 = 12.0, 22.0
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
text(PAGE_W/2, 14, "POV 3D top_bearing — top_cap_v2  (v2 转子帽, 单屏转子, L型, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"L型 (腿在+X端; 屏幕组件转180°后) / 平板 {TP_X1-TP_X0:g}×{2*TP_HW:g}×{SLAB_T:g} (asm X-65..+17.27, Y±72, Z283.7..292.7, 顶面全平) + 背板腿 {LEG_X1-LEG_X0:g}×{2*LEG_HW:g} 下至Z247 / "
     f"中心Φ{M6_BORE:g}通+底面头窝Φ{HEAD_D:g}×{HEAD_DEPTH:g} / -X悬出 19×Φ{CW_M6:g} 配重 (10+9品字形, 三角{CW_TRI:g}, 顶面沉孔Φ{HEAD_D:g}×{HEAD_DEPTH:g}) / 腿 2×Φ{M3_CLEAR:g}→屏上排螺母 (M3×16)",
     size=TXT_I, anchor="middle")

# ============================================================
# PLAN VIEW 1:1  (asm, looking -Z at the flat top face)
# pdf x = part Y + gx0 ; pdf y = gy0 - part X   (+X up)
# ============================================================
gx0, gy0 = 118.0, 92.0
def gv(x, y): return (gx0 + y, gy0 - x)
text(gx0, 38, "俯视 (1:1)  (沿 -Z 看顶面)  尺寸单位: mm", size=TXT_L, anchor="middle")
text(gx0, 45, f"中心 Φ{M6_BORE:g} 通, 底面头窝 Φ{HEAD_D:g}×{HEAD_DEPTH:g} 虚线 (详图B)",
     size=TXT_I, anchor="middle")
_w(GEOM_W)
pdf.rect(gv(TP_X1, -TP_HW)[0], gv(TP_X1, -TP_HW)[1],
         2*TP_HW, TP_X1 - TP_X0, style="D")                     # slab outline
# centerlines
dash(True, 3.0, 1.5); _w(0.15)
pdf.line(gv(TP_X1, 0)[0], gv(TP_X1, 0)[1] - 4, gv(TP_X0, 0)[0], gv(TP_X0, 0)[1] + 5)
pdf.line(gv(0, -TP_HW)[0] - 4, gv(0, 0)[1], gv(0, TP_HW)[0] + 40, gv(0, 0)[1])
dash(False)
# leg (hidden below the slab) + M3 hole marks — rect corner at the LARGER X
# (pdf y = gy0 - x), so the band spans exactly X +13.27..+17.27
dash(True); _w(HID_W)
pdf.rect(gv(LEG_X1, -LEG_HW)[0], gv(LEG_X1, -LEG_HW)[1],
         2*LEG_HW, LEG_X1 - LEG_X0, style="D")
for sy in (-SCREW_Y, SCREW_Y):
    for off in (-M3_CLEAR/2, M3_CLEAR/2):
        pdf.line(gv(LEG_X0, sy + off)[0], gv(LEG_X0, sy)[1],
                 gv(LEG_X1, sy + off)[0], gv(LEG_X1, sy)[1])
dash(False)
# axis hole: Φ6.2 (solid) + Φ13 head recess (hidden, bottom face)
_w(GEOM_W); pdf.circle(*gv(0, 0), M6_BORE/2, style="D")
dash(True); _w(HID_W); pdf.circle(*gv(0, 0), HEAD_D/2, style="D"); dash(False)
# counterweight bank: Φ13 CB (top face, visible) + Φ6.5 through
_w(GEOM_W)
for (cx, cy) in CW_A + CW_B:
    pdf.circle(*gv(cx, cy), HEAD_D/2, style="D")
    pdf.circle(*gv(cx, cy), CW_M6/2, style="D")
# detail callouts: A on the row-B end hole, B on the axis hole
_w(0.25); dash(True, 1.0, 0.8)
pdf.circle(*gv(CWB_X, -LEG_HW), 9.0, style="D")
pdf.circle(*gv(0, 0), 9.0, style="D")
dash(False)
text(gv(CWB_X, -LEG_HW)[0] - 12.5, gv(CWB_X, -LEG_HW)[1] + 11, "A", size=TXT_L)
text(gv(0, 0)[0] + 10.5, gv(0, 0)[1] - 8.5, "B", size=TXT_L)
# --- dims --- (leg now AT the +X top edge -> stack its dims above the part)
hdim(gv(LEG_X1, -SCREW_Y)[0], gv(LEG_X1, SCREW_Y)[0],
     gv(LEG_X1, 0)[1], gv(LEG_X1, 0)[1] - 6.7, "99.95 (=2×49.975)")       # M3 span
hdim(gv(LEG_X1, -LEG_HW)[0], gv(LEG_X1, LEG_HW)[0],
     gv(LEG_X1, 0)[1], gv(LEG_X1, 0)[1] - 14.7, f"{2*LEG_HW:g}")          # 112
hdim(gv(TP_X1, -TP_HW)[0], gv(TP_X1, TP_HW)[0],
     gv(TP_X1, 0)[1], gv(TP_X1, 0)[1] - 22.7, f"{2*TP_HW:g}")             # 144
vdim(gv(TP_X1, 0)[1], gv(TP_X0, 0)[1],
     gv(0, -TP_HW)[0], gv(0, -TP_HW)[0] - DIM_O1, f"{TP_X1-TP_X0:g}")     # 82.27
# counterweight rows: pitch 14 below the part, row offsets at the right
hdim(gv(CWB_X, 0)[0], gv(CWB_X, CW_TRI)[0],
     gv(CWB_X, 0)[1], gv(TP_X0, 0)[1] + 8, f"{CW_TRI:g}")
vdim(gv(0, 0)[1], gv(CWA_X, 0)[1], gv(0, TP_HW)[0], gv(0, TP_HW)[0] + DIM_O1 + 12, "46")
vdim(gv(CWA_X, 0)[1], gv(CWB_X, 0)[1], gv(0, TP_HW)[0], gv(0, TP_HW)[0] + DIM_O1, "12.12")
vdim(gv(0, 0)[1], gv(CWB_X, 0)[1], gv(0, TP_HW)[0], gv(0, TP_HW)[0] + DIM_O1 + 24, "58.12")
# notes under the plan
text(gx0, 171, f"配重 19×Φ{CW_M6:g} 通: 行A X=-46 十孔 / 行B X=-58.12 九孔 (品字形, 沉孔见详图A)",
     size=TXT_I, anchor="middle", halo=True)
text(gx0, 177, f"腿(虚线) {LEG_X1-LEG_X0:g} 厚 X +13.27..+17.27 (顶端, 与+X边齐平), 2×Φ{M3_CLEAR:g} @Y=±{SCREW_Y:g} (M3×16)",
     size=TXT_I, anchor="middle", halo=True)

# ============================================================
# SIDE SECTION 2:1  (asm, looking +Y, cutting plane Y = 0)
# local z: 0 = leg bottom (asm 247) .. 45.7 = top face (asm 292.7)
# ============================================================
PS = 2.0
px0, py0 = 366.0, 160.0
def pv(x, z): return (px0 + PS*x, py0 - PS*z)
text(318, 46, "侧视剖面 (2:1)  (沿 +Y 看, 剖切面 Y=0) — L型, 腿在+X端", size=TXT_L, anchor="middle")
ZT, ZB = LEG_H, LEG_H - SLAB_T                 # 45.7 / 36.7 (slab top/bottom)
CBZ = ZT - HEAD_DEPTH                          # 43.0 (CW counterbore floor)
RCZ = ZB + HEAD_DEPTH                          # 39.4 (head recess ceiling)
br, hr, cr = M6_BORE/2, HEAD_D/2, CW_M6/2
segs = [
    # top face, broken by the CW CB (at X=-58.12) and the axis bore
    ((TP_X0, ZT), (CWB_X - hr, ZT)), ((CWB_X + hr, ZT), (-br, ZT)),
    ((br, ZT), (TP_X1, ZT)),
    # CW hole: Φ13×2.7 CB from the top + Φ6.5 through
    ((CWB_X - hr, ZT), (CWB_X - hr, CBZ)), ((CWB_X + hr, ZT), (CWB_X + hr, CBZ)),
    ((CWB_X - hr, CBZ), (CWB_X - cr, CBZ)), ((CWB_X + cr, CBZ), (CWB_X + hr, CBZ)),
    ((CWB_X - cr, CBZ), (CWB_X - cr, ZB)), ((CWB_X + cr, CBZ), (CWB_X + cr, ZB)),
    # outer edges: -X face (slab only) + full-height +X face (leg outer, L)
    ((TP_X0, ZT), (TP_X0, ZB)), ((TP_X1, ZT), (TP_X1, 0)),
    # slab bottom face, broken at the CW bore, the head recess and the leg
    ((TP_X0, ZB), (CWB_X - cr, ZB)), ((CWB_X + cr, ZB), (-hr, ZB)),
    ((hr, ZB), (LEG_X0, ZB)),
    # leg (down to asm Z247; outer face = the +X edge above)
    ((LEG_X0, ZB), (LEG_X0, 0)), ((LEG_X0, 0), (TP_X1, 0)),
    # axis: Φ13×2.7 head recess from the bottom + Φ6.2 bore to the top
    ((-hr, ZB), (-hr, RCZ)), ((hr, ZB), (hr, RCZ)),
    ((-hr, RCZ), (-br, RCZ)), ((br, RCZ), (hr, RCZ)),
    ((-br, RCZ), (-br, ZT)), ((br, RCZ), (br, ZT)),
]
_w(GEOM_W)
for (a, b) in segs:
    line(*pv(*a), *pv(*b), GEOM_W)
# M3 hole through the leg (off-plane at Y=±49.975 — hidden projection)
dash(True); _w(HID_W)
for zz in (SCREW_ZLOC - M3_CLEAR/2, SCREW_ZLOC + M3_CLEAR/2):
    pdf.line(*pv(LEG_X0, zz), *pv(LEG_X1, zz))
dash(False)
# centerlines: axis + CW hole
dash(True, 3.0, 1.5); _w(0.15)
pdf.line(*pv(0, ZT + 4), *pv(0, -8))
pdf.line(*pv(CWB_X, ZT + 2), *pv(CWB_X, ZB - 2))
pdf.line(*pv(LEG_X0 - 2.5, SCREW_ZLOC), *pv(LEG_X1 + 2.5, SCREW_ZLOC))
dash(False)
# detail callouts
_w(0.25); dash(True, 1.0, 0.8)
pdf.circle(pv(CWB_X, (ZT + CBZ)/2)[0], pv(CWB_X, (ZT + CBZ)/2)[1] + 1.3, 10.0, style="D")
pdf.circle(pv(0, ZB + 1.2)[0], pv(0, ZB + 1.2)[1], 10.0, style="D")
dash(False)
text(pv(CWB_X, 0)[0] + 11, pv(0, ZT)[1] - 4.5, "A", size=TXT_L)
text(pv(0, ZB)[0] + 11.5, pv(0, ZB)[1] + 12, "B", size=TXT_L)
# --- dims ---
hdim(pv(TP_X0, 0)[0], pv(0, 0)[0], pv(0, ZT)[1], pv(0, ZT)[1] - 8.6, "65")   # -X edge to axis
hdim(pv(0, 0)[0], pv(TP_X1, 0)[0], pv(0, ZT)[1], pv(0, ZT)[1] - 8.6,
     f"{TP_X1:g}")                                                            # axis to +X edge (17.27)
vdim(pv(0, ZT)[1], pv(0, ZB)[1], pv(TP_X0, 0)[0], pv(TP_X0, 0)[0] - 10, f"{SLAB_T:g}")   # 9
vdim(pv(0, ZT)[1], pv(0, 0)[1], pv(TP_X1, 0)[0], pv(TP_X1, 0)[0] + 8, f"{LEG_H:g}")      # 45.7 (L outer edge)
vdim(pv(0, SCREW_ZLOC)[1], pv(0, 0)[1], pv(LEG_X0, 0)[0], pv(LEG_X0, 0)[0] - 8,
     f"{SCREW_ZLOC:g}")                                                       # 6.2 (left of the leg)
hdim(pv(LEG_X0, 0)[0], pv(LEG_X1, 0)[0], pv(0, 0)[1], pv(0, 0)[1] + 6, "4")   # leg thick
hdim(pv(0, 0)[0], pv(LEG_X0, 0)[0], pv(0, 0)[1], pv(0, 0)[1] + 14, "13.27")   # axis→leg front face
text(pv(TP_X0, 0)[0], pv(0, 0)[1] + 24,
     f"腿底 asm Z247, 孔心 Z253.2 (=腿底+{SCREW_ZLOC:g}), 顶面 Z292.7", size=TXT_I, halo=True)

# ============================================================
# DETAIL A (4:1) — counterweight counterbore, cut FROM THE TOP face
# ============================================================
DS = 4.0; dax, daz = 48.0, 248.0
def da(x, z): return (dax + DS*x, daz - DS*z)     # z: 0=slab bottom .. 9=top
text(dax + 32, 192, "详图 A (4:1)  配重沉孔 — 顶面进", size=TXT_L, anchor="middle")
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
vdim(da(16,0)[1], da(16,SLAB_T)[1], da(16,0)[0], da(16,0)[0]+DIM_O1, f"{SLAB_T:g}")
text(dax - 10, 265, "M6 平头 (Φ12.5×2.6) 沉平", size=TXT_I)

# ============================================================
# DETAIL B (4:1) — axis head recess, cut FROM THE BOTTOM face
# ============================================================
dbx, dbz = 172.0, 248.0
def db(x, z): return (dbx + DS*x, dbz - DS*z)     # z: 0=slab bottom .. 9=top
text(dbx + 36, 192, "详图 B (4:1)  轴孔头窝 — 底面进 (方向与A相反)", size=TXT_L, anchor="middle")
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
vdim(db(18,0)[1], db(18,SLAB_T)[1], db(18,0)[0], db(18,0)[0]+DIM_O1, f"{SLAB_T:g}")
text(dbx - 6, 265, "M6×40 平头自底面入 (头 283.7..286.4)", size=TXT_I)

# ===== assembly / print notes (bottom right) =====
nx = 286.0
text(nx, 198, "打印姿态: 平板顶面 (asm Z292.7) 朝下贴床, 腿朝上, 免支撑", size=TXT_I)
text(nx, 205, "轴系: M6×40 平头自底面头窝入 → Φ8×50 M6内丝螺柱 → 2×688", size=TXT_I)
text(nx, 212, "固定: M3×16 ×2 自腿背面穿 (腿4 + screen_plate 6) 拧入屏上排螺母", size=TXT_I)
text(nx, 219, "腿前面贴 screen_plate 背面 (asm X=+13.27; 屏幕组件绕Z转180°后)", size=TXT_I)
text(nx, 226, "配重: M6 平头自顶面沉孔入 + 螺母, 逐孔配平", size=TXT_I)

# ===== title block =====
tb_y, tb_x, tb_w, tb_h = PAGE_H - 28, 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D — top_bearing / top_cap_v2 (v2 转子帽) (×1)",
     size=TXT_L, anchor="start")
text(tb_x + tb_w - 4, tb_y + 6, "投影 1st-angle / PLA / 单位 mm", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     "PLA / 打印姿态: 平板顶面朝下 (腿朝上, 免支撑) / L型 (腿在+X端; 屏幕组件转180°后) / 平板9厚 82.27×144, 腿4厚 高45.7 / "
     "BOM: M6×40平头, Φ8×50螺柱, M3×16 ×2, M6平头配重+螺母按需", size=TXT_I, anchor="start")
text(tb_x + tb_w - 4, tb_y + 14.5, "2026-07-09 / POV3D / models / top_bearing",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("top_bearing_cap_v2_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("top_bearing_cap_v2_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt} (original locked)")
