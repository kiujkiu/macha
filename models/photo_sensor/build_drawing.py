"""
A3 drawings for the printed photo_sensor parts — TWO PDFs:
  photo_sensor_bracket_drawing.pdf — sensor_bracket (flat plate on the disc top)
  photo_sensor_vane_drawing.pdf    — index_vane (static flag on the breadboard)
sensor_module is a BOUGHT part (dims in build_module.py) — no fab sheet.
Geometry mirrors build_bracket.py / build_vane.py. 1st-angle, mm, PLA.
"""
import math, os
from pathlib import Path
from fpdf import FPDF

PAGE_W, PAGE_H = 420.0, 297.0
GEOM_W, DIM_W, EXT_W, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W = 4.2, 1.5
EXT_OV, EXT_GP = 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 5.0, 8.0, 9.5, 5.0
DIM_O1, DIM_O2 = 12.0, 22.0
_FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
if not os.path.exists(_FONT): raise FileNotFoundError("SimHei not found")

pdf = None
def new_doc():
    global pdf
    pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False)
    pdf.add_page(); pdf.add_font("SimHei", "", _FONT); pdf.set_line_width(0.3)
    pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W): _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L; bx, by = tx - ARR_L*ux, ty - ARR_L*uy
    px, py = -uy, ux; pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx + ARR_W*px, by + ARR_W*py), (bx - ARR_W*px, by - ARR_W*py)], style="F")
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    if halo:
        sw, fh = pdf.get_string_width(s), pdf.font_size
        pdf.set_fill_color(255, 255, 255); pdf.rect(x-0.4, y-fh*0.85, sw+0.8, fh*1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, ang, size=TXT_D, anchor="middle", halo=False):
    pdf.set_font("SimHei", "", size); sw = pdf.get_string_width(s)
    with pdf.rotation(angle=ang, x=cx, y=cy):
        dx = -sw/2 if anchor == "middle" else (-sw if anchor == "end" else 0)
        if halo:
            fh = pdf.font_size; pdf.set_fill_color(255, 255, 255)
            pdf.rect(cx+dx-0.4, cy-fh*0.85, sw+0.8, fh*1.1, style="F"); pdf.set_fill_color(0, 0, 0)
        pdf.text(cx + dx, cy, s)
def _u(label):
    s = str(label).strip()
    return s if (not s or "mm" in s or "°" in s) else f"{s} mm"
def hdim(x1, x2, yg, yd, label):
    label = _u(label)
    if yd > yg: e1, e2 = yg+EXT_GP, yd+EXT_OV
    else:       e1, e2 = yg-EXT_GP, yd-EXT_OV
    line(x1, e1, x1, e2, EXT_W); line(x2, e1, x2, e2, EXT_W)
    xl, xr = (x1, x2) if x1 < x2 else (x2, x1)
    if xr-xl >= 2*ARR_L+1:
        line(xl, yd, xr, yd, DIM_W); arrow(xl, yd, -1, 0); arrow(xr, yd, 1, 0)
    else:
        line(xl-ARR_L-1, yd, xr+ARR_L+1, yd, DIM_W); arrow(xl, yd, 1, 0); arrow(xr, yd, -1, 0)
    text((xl+xr)/2, yd-1.8, label, anchor="middle", halo=True)
def vdim(y1, y2, xg, xd, label):
    label = _u(label)
    if xd > xg: e1, e2, to = xg+EXT_GP, xd+EXT_OV, 4.0
    else:       e1, e2, to = xg-EXT_GP, xd-EXT_OV, -4.0
    line(e1, y1, e2, y1, EXT_W); line(e1, y2, e2, y2, EXT_W)
    yt, yb = (y1, y2) if y1 < y2 else (y2, y1); gap = yb-yt
    if gap >= 2*ARR_L+1:
        line(xd, yt, xd, yb, DIM_W); arrow(xd, yt, 0, -1); arrow(xd, yb, 0, 1)
    else:
        line(xd, yt-ARR_L-1, xd, yb+ARR_L+1, DIM_W); arrow(xd, yt, 0, 1); arrow(xd, yb, 0, -1)
    lh = pdf.get_string_width(label)
    if gap >= lh+1.0: rot_text(xd+to, (yt+yb)/2, label, 90, anchor="middle", halo=True)
    else:             rot_text(xd+to, yb+ARR_L+1+lh/2+1, label, 90, anchor="middle", halo=True)
def circle(cx, cy, d, dashed=False):
    if dashed: pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
    else: _w(GEOM_W)
    pdf.circle(cx, cy, d/2, style="D")
    if dashed: pdf.set_dash_pattern()
def rect_dashed(x, y, w, h):
    pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W); pdf.rect(x, y, w, h, style="D"); pdf.set_dash_pattern()
def title_block(line1, line2):
    tb_y, tb_x, tb_w, tb_h = PAGE_H-28, 20, PAGE_W-40, 18
    _w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
    pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
    text(tb_x+4, tb_y+6, line1, size=TXT_L, anchor="start")
    text(tb_x+tb_w-4, tb_y+6, "投影 1st-angle / PLA / 单位 mm", size=TXT_I, anchor="end")
    text(tb_x+4, tb_y+14.5, line2, size=TXT_I, anchor="start")
    text(tb_x+tb_w-4, tb_y+14.5, "2026-06-15 / POV3D / models / photo_sensor", size=TXT_I, anchor="end")
def save(name):
    out = Path(__file__).with_name(name)
    try: pdf.output(str(out)); print(f"wrote {out}")
    except PermissionError:
        alt = Path(__file__).with_name(name.replace(".pdf", ".NEW.pdf")); pdf.output(str(alt)); print(f"wrote {alt}")

# ============================================================
# SHEET 1 — sensor_bracket  (local datum at the −X,−Y corner)
# Plate 41(X,radial) × 50(Y,tangential) × 5 thick. Holes (local lx,ly):
#   RED  (34.5,44) (34.5,4)  plain M3 Φ3.4    BLUE (22,41)(8,41) M3+Φ4.2×4 CB
# ============================================================
new_doc()
text(PAGE_W/2, 14, "POV 3D photo_sensor — sensor_bracket  (圆盘上平板, 外伸挂光电开关, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20,
     "贴圆盘上表面, 锁(-92.5,±20)圆盘孔(2×M3通孔, 从上往下, 无沉孔) / 外伸段下面挂模块: 2×M3+Φ4.2×4沉孔 + 3让位坑(底面深2) / 厚5",
     size=TXT_I, anchor="middle")
S = 3.0
ax0, ay0 = 70.0, 70.0
def bv(lx, ly): return (ax0 + S*lx, ay0 + S*(50.0 - ly))   # plan: page-y flips so ly up
text(ax0 + 60, 46, "俯视 (3:1)  (沿 -Z 看顶面)  尺寸单位: mm", size=TXT_L, anchor="middle")
_w(GEOM_W); pdf.rect(bv(0, 50)[0], bv(0, 50)[1], S*41, S*50, style="D")
RED_L = [(34.5, 44.0), (34.5, 4.0)]
BLUE_L = [(22.0, 41.0), (8.0, 41.0)]
for (lx, ly) in RED_L: circle(*bv(lx, ly), S*3.4)
for (lx, ly) in BLUE_L:
    circle(*bv(lx, ly), S*4.2)          # CB
    circle(*bv(lx, ly), S*3.2)          # thru
# 3 relief pockets (dashed, underside): local rects
POCK_L = [(5.0, 11.0, 19.5, 28.5), (19.0, 25.0, 19.5, 28.5), (10.5, 19.5, 39.0, 45.5)]
for (x0, x1, y0, y1) in POCK_L:
    rect_dashed(bv(x0, y1)[0], bv(x0, y1)[1], S*(x1-x0), S*(y1-y0))
# dims
hdim(bv(0, 0)[0], bv(41, 0)[0], bv(0, 0)[1], bv(0, 0)[1]+DIM_O1, "41")
vdim(bv(0, 0)[1], bv(0, 50)[1], bv(0, 0)[0], bv(0, 0)[0]-DIM_O1, "50")
hdim(bv(8, 41)[0], bv(22, 41)[0], bv(0, 41)[1], bv(0, 41)[1]-DIM_O1, "14 (模块孔距)")
vdim(bv(34.5, 4)[1], bv(34.5, 44)[1], bv(41, 0)[0], bv(41, 0)[0]+DIM_O1, "40 (圆盘孔距)")
hdim(bv(0, 41)[0], bv(8, 41)[0], bv(0, 50)[1], bv(0, 50)[1]-DIM_O1, "8")
text(bv(22, 41)[0]+3, bv(22, 41)[1]-3, "2×Φ3.2 + Φ4.2×4沉孔 (锁模块)", TXT_I, "start", True)
text(bv(34.5, 24)[0]+3, bv(34.5, 24)[1], "2×Φ3.4 (锁圆盘, 无沉孔)", TXT_I, "start", True)
text(bv(12, 24)[0]-2, bv(12, 24)[1], "3×让位坑 深2 (虚线, 底面)", TXT_I, "start", True)

# side section (X-Z) 3:1
sx0, sz0 = 250.0, 230.0
def sv(lx, z): return (sx0 + S*lx, sz0 - S*z)   # z up
text(sx0 + 50, 150, "侧视 (3:1)  (沿 -Y 看, 厚5)", size=TXT_L, anchor="middle")
_w(GEOM_W); pdf.rect(sv(0, 5)[0], sv(0, 5)[1], S*41, S*5, style="D")
# BLUE CB (Φ4.2×4 from top) at lx 8 and 22 — show as notch
for lx in (8.0, 22.0):
    pdf.rect(sv(lx-2.1, 5)[0], sv(lx-2.1, 5)[1], S*4.2, S*4, style="D")   # CB pocket from top
    line(*sv(lx, 1.0), *sv(lx, 0), GEOM_W)                                # M3 thru stub
# pockets (2mm from bottom) at lx ~5-25 (shown as bottom notches, dashed)
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
pdf.rect(sv(5, 2)[0], sv(5, 2)[1], S*20, S*2, style="D"); pdf.set_dash_pattern()
vdim(sv(41, 0)[1], sv(41, 5)[1], sv(41, 0)[0], sv(41, 0)[0]+DIM_O1, "5")
vdim(sv(0, 5-4)[1], sv(0, 5)[1], sv(0, 0)[0], sv(0, 0)[0]-DIM_O1, "沉孔4")
vdim(sv(30, 0)[1], sv(30, 2)[1], sv(30, 0)[0], sv(30, 0)[0]+DIM_O1, "坑2")
text(sx0, 168, "RED 圆盘孔=通孔无沉孔; BLUE 模块孔=Φ4.2×4 顶面沉孔; 底面 3 让位坑深2", TXT_I, "start", True)

# ---- detail markers on the plan (RED holes are plain through → no detail) ----
def detail_mark(cx, cy, letter, r=6.5):
    _w(0.25); pdf.set_dash_pattern(dash=1.0, gap=0.8); pdf.circle(cx, cy, r, style="D"); pdf.set_dash_pattern()
    text(cx + r + 0.5, cy - r + 1, letter, size=TXT_L)
detail_mark(*bv(22, 41), "A")            # BLUE counterbored module hole
detail_mark(*bv(8, 24), "B")             # relief pocket

# ---- DETAIL A (6:1) — BLUE counterbore (Φ3.2 thru + Φ4.2×4 CB) ----
DS = 6.0; dax, daz = 250.0, 130.0
def da(x, z): return (dax + DS*x, daz - DS*z)
text(dax + 24, 60, "详图 A (6:1)  模块孔沉孔", size=TXT_L, anchor="middle")
_w(GEOM_W)
for a, b in [((0,0),(2.4,0)),((2.4,0),(2.4,1)),((2.4,1),(1.9,1)),((1.9,1),(1.9,5)),((1.9,5),(0,5)),((0,5),(0,0))]:
    line(*da(*a), *da(*b), GEOM_W)
for a, b in [((8,0),(5.6,0)),((5.6,0),(5.6,1)),((5.6,1),(6.1,1)),((6.1,1),(6.1,5)),((6.1,5),(8,5)),((8,5),(8,0))]:
    line(*da(*a), *da(*b), GEOM_W)
pdf.set_dash_pattern(dash=1.2, gap=0.8); _w(0.13); pdf.line(*da(4,5.6), *da(4,-0.6)); pdf.set_dash_pattern()
hdim(da(1.9,5)[0], da(6.1,5)[0], da(0,5)[1], da(0,5)[1]-DIM_O1, "Φ4.2")
hdim(da(2.4,0)[0], da(5.6,0)[0], da(0,0)[1], da(0,0)[1]+DIM_O1, "Φ3.2 通")
vdim(da(0,0)[1], da(0,5)[1], da(0,0)[0], da(0,0)[0]-DIM_O1, "5")
vdim(da(8,1)[1], da(8,5)[1], da(8,0)[0], da(8,0)[0]+DIM_O1, "深4")
text(dax + 4, 122, "(顶面进, 锁模块)", TXT_I, "start", True)

# ---- DETAIL B (6:1) — relief pocket (2mm blind, underside) ----
dbx, dbz = 350.0, 130.0
def db(x, z): return (dbx + DS*x, dbz - DS*z)
text(dbx + 24, 60, "详图 B (6:1)  让位坑", size=TXT_L, anchor="middle")
_w(GEOM_W)
for a, b in [((0,0),(1,0)),((1,0),(1,2)),((1,2),(7,2)),((7,2),(7,0)),((7,0),(8,0)),((8,0),(8,5)),((8,5),(0,5)),((0,5),(0,0))]:
    line(*db(*a), *db(*b), GEOM_W)
hdim(db(1,2)[0], db(7,2)[0], db(0,2)[1], db(0,2)[1]-DIM_O1, "坑宽")
vdim(db(8,0)[1], db(8,2)[1], db(8,0)[0], db(8,0)[0]+DIM_O1, "深2")
vdim(db(0,0)[1], db(0,5)[1], db(0,0)[0], db(0,0)[0]-DIM_O1, "5")
text(dbx + 4, 122, "(底面进, 让焊脚)", TXT_I, "start", True)

title_block("POV 3D — photo_sensor / sensor_bracket (×1, 转子)",
            "平板 41×50×5 贴圆盘顶 / 2×Φ3.4锁圆盘(通孔无沉孔) + 2×Φ3.2+Φ4.2×4沉孔锁模块(详图A) + 3让位坑深2(详图B) / 外伸悬挑")
save("photo_sensor_bracket_drawing.pdf")

# ============================================================
# SHEET 2 — index_vane  (local datum at foot −X,−Y corner)
# Foot 23(X)×36(Y)×5; 2×Φ6.5 M6 (grid); blade narrow-radial 4 × long-tang,
# total height 40 (crosses beam Z38.7).  build_vane: X[-119,-99] Y[-18,18]
# blade X[-114,-110] (R110-114). Local lx = X+119 (0..20), ly = Y+18 (0..36).
# ============================================================
new_doc()
text(PAGE_W/2, 14, "POV 3D photo_sensor — index_vane  (固定遮挡片, 锁洞洞板 M6, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20,
     "底板锁洞洞板 (2×Φ6.5 @25中心距) / 叶片: 窄径向4 × 长切向(槽内8/底10), 升到高40 横穿光束Z38.7(配合支架抬高)",
     size=TXT_I, anchor="middle")
V = 4.0
vx0, vy0 = 80.0, 78.0
def vv(lx, ly): return (vx0 + V*lx, vy0 + V*(36.0 - ly))
text(vx0 + 40, 52, "俯视 (4:1)  (沿 -Z 看)  尺寸单位: mm", size=TXT_L, anchor="middle")
_w(GEOM_W); pdf.rect(vv(0, 36)[0], vv(0, 36)[1], V*20, V*36, style="D")    # foot 20×36
# blade footprint: X[-114,-110] → local lx 5..9 ; tangential (Y) ±5 below → ly 13..23
pdf.rect(vv(5, 23)[0], vv(5, 23)[1], V*4, V*10, style="D")
# 2× M6 at (-112.5,±12.5) → local lx=6.5, ly=5.5 and 30.5
for ly in (5.5, 30.5): circle(*vv(6.5, ly), V*6.5)
hdim(vv(0, 0)[0], vv(20, 0)[0], vv(0, 0)[1], vv(0, 0)[1]+DIM_O1, "20")
vdim(vv(0, 0)[1], vv(0, 36)[1], vv(0, 0)[0], vv(0, 0)[0]-DIM_O1, "36")
vdim(vv(6.5, 5.5)[1], vv(6.5, 30.5)[1], vv(20, 0)[0], vv(20, 0)[0]+DIM_O1, "25 (M6孔距)")
hdim(vv(5, 18)[0], vv(9, 18)[0], vv(5, 13)[1], vv(5, 13)[1]+DIM_O1, "4 (叶片径向)")
text(vv(6.5, 36)[0], vv(6.5, 36)[1]-3, "2×Φ6.5 锁洞洞板", TXT_I, "middle", True)

# side (X-Z): foot 5 + blade to Z40, beam line @Z38.7
s2x0, s2z0 = 250.0, 255.0
def s2(lx, z): return (s2x0 + V*lx, s2z0 - V*z)
text(s2x0 + 30, 130, "侧视 (4:1)  (沿 -Y 看)", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(s2(0, 5)[0], s2(0, 5)[1], V*20, V*5, style="D")                   # foot
pdf.rect(s2(5, 40)[0], s2(5, 40)[1], V*4, V*35, style="D")                 # blade (lx5-9, Z5-40)
pdf.set_dash_pattern(dash=1.2, gap=0.8); _w(0.13)
pdf.line(*s2(2, 38.7), *s2(12, 38.7)); pdf.set_dash_pattern(); _w(GEOM_W)
vdim(s2(20, 0)[1], s2(20, 40)[1], s2(20, 0)[0], s2(20, 0)[0]+DIM_O1, "40 (总高)")
vdim(s2(0, 0)[1], s2(0, 5)[1], s2(0, 0)[0], s2(0, 0)[0]-DIM_O1, "5")
text(s2(12, 38.7)[0]+2, s2(12, 38.7)[1], "光束 Z38.7 (叶片须过此线)", TXT_I, "start", True)
text(s2x0-20, 150, "叶片切向: 槽内8 / 槽下底10 (此视图为径向厚4)", TXT_I, "start", True)
text(vx0, 250, "注: 孔均为 Φ6.5 通孔, 无沉孔/特殊非通孔, 无需放大详图", TXT_I, "start", True)

title_block("POV 3D — photo_sensor / index_vane (×1, 固定)",
            "底板 20×36×5 (2×Φ6.5@25锁洞洞板) + 叶片 径向4×切向8~10, 高40 过光束Z38.7 / R112 @θ180")
save("photo_sensor_vane_drawing.pdf")
