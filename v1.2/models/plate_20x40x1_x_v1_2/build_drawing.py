"""A3 横向图纸: plate_20x40x1_x_v1_2 (俯视 4:1 + 侧视 4:1), 几何从 build_stl 导入。"""
import math
from pathlib import Path
from fpdf import FPDF
from build_stl import W, H, T, RIB, TOP, RIGHT, TRIS

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

GEOM_W = 0.50
DIM_W  = 0.20
EXT_W  = 0.20
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

# SimHei 缺这几个字形 (见 feedback_pdf_drawing_lessons): 落笔前统一替换
_GLYPH_FIX = {"−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ", "³": "^3", "²": "^2"}
def _g(s):
    s = str(s)
    for a, b in _GLYPH_FIX.items():
        if a in s: s = s.replace(a, b)
    return s
def text(x, y, s, size=TXT_D, anchor="start"):
    s = _g(s)
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, angle_deg, size=TXT_D, anchor="middle"):
    s = _g(s)
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
    if x_r - x_l >= 2 * ARR_L + 1:
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
        arrow(xd, y_top, 0,  1); arrow(xd, y_bot, 0, -1)
    lh = pdf.get_string_width(label)
    if gap >= lh + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        rot_text(xd + to, y_bot + (ARR_L + 1.0) + lh / 2 + 1.0,
                 label, angle_deg=90, anchor="middle")


_w(0.3); pdf.rect(5, 5, PAGE_W-10, PAGE_H-10, style="D")
text(PAGE_W/2, 15, "X 字框片 plate_20x40x1_x_v1_2   20 × 40 × 1", size=14, anchor="middle")
text(PAGE_W/2, 22, f"薄板挖 4 个三角通孔: 四边外框宽 {RIB:g} + 两条对角筋宽 {RIB:g} (垂直于筋量)", size=8, anchor="middle")
S = 4.0; cx, cy = 150, 142
def tv(x, y): return (cx + x*S, cy - y*S)
text(cx, 36, "俯视图 Top View (4:1)   尺寸单位: mm", size=11, anchor="middle")
_w(GEOM_W); pdf.rect(*tv(-W/2, H/2), W*S, H*S, style="D")
for t in TRIS: pdf.polygon([tv(*p) for p in t], style="D")
yb, yt = tv(0, -H/2)[1], tv(0, H/2)[1]; xl, xr = tv(-W/2, 0)[0], tv(W/2, 0)[0]
TXT = 9
def lab(x, y, s, ang=None):
    if ang is None: text(x, y, s, size=TXT, anchor="middle")
    else: rot_text(x, y, s, ang, size=TXT)
def H_(a, b, yg, yd, s):
    k = 1 if yd > yg else -1
    line(a, yg+k*EXT_GP, a, yd+k*EXT_OV); line(b, yg+k*EXT_GP, b, yd+k*EXT_OV); line(a, yd, b, yd)
    if b-a > 10: arrow(a, yd, -1, 0); arrow(b, yd, 1, 0)
    else:
        line(a-7, yd, a, yd); line(b, yd, b+7, yd); arrow(a, yd, 1, 0); arrow(b, yd, -1, 0)
    lab((a+b)/2, yd-(2 if b-a > 10 else 4), s)
def V_(a, b, xg, xd, s):
    k = 1 if xd > xg else -1
    line(xg+k*EXT_GP, a, xd+k*EXT_OV, a); line(xg+k*EXT_GP, b, xd+k*EXT_OV, b); line(xd, a, xd, b)
    if b-a > 10: arrow(xd, a, 0, -1); arrow(xd, b, 0, 1)
    else:
        line(xd, a-7, xd, a); line(xd, b, xd, b+7); arrow(xd, a, 0, 1); arrow(xd, b, 0, -1)
    lab(xd-2, (a+b)/2, s, 90)
ix, iy = W/2-RIB, H/2-RIB
H_(tv(-TOP[1][0],0)[0], tv(TOP[1][0],0)[0], yt, yt-9, f"{2*TOP[1][0]:.2f} mm")
H_(xl, xr, yt, yt-20, f"{W:g} mm")
H_(xl, tv(-ix,0)[0], yb, yb+14, f"{RIB:g} mm")
V_(yt, yb, xl, xl-26, f"{H:g} mm")
V_(tv(0,-iy)[1], yb, xl, xl-13, f"{RIB:g} mm")
V_(tv(0,RIGHT[2][1])[1], tv(0,RIGHT[1][1])[1], xr, xr+16, f"{2*RIGHT[2][1]:.2f} mm")
# 对角筋宽: 在右上筋中段, 垂直方向两侧箭头
L = math.hypot(W, H); ux, uy = W/L, H/L; nx, ny = uy, -ux
mx, my = ux*9, uy*9
pa, pb = tv(mx+nx*RIB/2, my+ny*RIB/2), tv(mx-nx*RIB/2, my-ny*RIB/2)
d = (nx, -ny)
arrow(*pa, -d[0], -d[1]); arrow(*pb, d[0], d[1])
line(pb[0]-d[0]*9, pb[1]-d[1]*9, *pb)
q = (pa[0]+d[0]*36, pa[1]+d[1]*36); line(*pa, *q); line(*q, q[0]+6, q[1])
text(q[0]+7, q[1]+1.2, f"筋宽 {RIB:g} mm (垂直于筋)", size=TXT)
# 侧视
sx, sy = 310, 142
text(sx, 36, "侧视图 Side View (4:1)", size=11, anchor="middle")
_w(GEOM_W); pdf.rect(sx-T*S/2, sy-H/2*S, T*S, H*S, style="D")
H_(sx-T*S/2, sx+T*S/2, yt, yt-9, f"{T:g} mm")
V_(yt, yb, sx-T*S/2, sx-20, f"{H:g} mm")
_w(0.3); pdf.rect(20, PAGE_H-32, PAGE_W-40, 18, style="D")
text(26, PAGE_H-20.5, "plate_20x40x1_x_v1_2   数量 1   POV3D V1.2   单位 mm   第一角   2026-11-24   打印: 平放, 免支撑, 100% 填充", size=10)
out = Path(__file__).with_name("plate_20x40x1_x_v1_2_drawing.pdf"); pdf.output(str(out)); print("wrote", out)
