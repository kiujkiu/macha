"""
A3 INTERFACE / REFERENCE drawing for the ZYNQ board (BOUGHT, not printed —
this is NOT a fab sheet).  Documents the mechanically-relevant, measured
geometry for designing the POV3D mount:
  - board outline 82 x 52 x 1.6
  - 4 x M3 Phi3.2 corner holes (rectangle 75 x 44.6, ~3.5 inset) + Phi7 keep-out
  - two 2.54 dual-row 2x20 pin headers, soldered on the BOTTOM (pins DOWN)
  - JTAG 2x7 + rough connector blocks (indicative)
Geometry mirrors build_module.py.  Drawn long-axis horizontal (scan view).
1st-angle, mm.  Run tools/verify_drawing.py afterwards.
"""
import math, os
from pathlib import Path
from fpdf import FPDF

PAGE_W, PAGE_H = 420.0, 297.0
GEOM_W, DIM_W, EXT_W, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W = 4.2, 1.5
EXT_OV, EXT_GP = 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 5.0, 8.0, 9.5, 5.0
DIM_O1, DIM_O2 = 13.0, 25.0
_FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
if not os.path.exists(_FONT): raise FileNotFoundError("SimHei not found")

# ---- board params (from build_module.py) ----
BW, BH, BT = 52.0, 82.0, 1.6          # model: X short, Y long
HOLES = [(-22.3, 37.5), (22.3, 37.5), (-22.3, -37.5), (22.3, -37.5)]
HOLE_D, KEEPOUT_D = 3.2, 7.0
PITCH, NPIN = 2.54, 20
OUTER = BW/2 - 1.5                     # 24.5
YCEN = -3.0
YTOP = YCEN + (NPIN-1)*PITCH/2
HDR_DROP = 8.54                        # pins reach Z = -8.54

pdf = None
def new_doc():
    global pdf
    pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False)
    pdf.add_page(); pdf.add_font("SimHei", "", _FONT); pdf.set_line_width(0.3)
    pdf.rect(5, 5, PAGE_W-10, PAGE_H-10, style="D")
def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W): _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L; bx, by = tx-ARR_L*ux, ty-ARR_L*uy
    px, py = -uy, ux; pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx+ARR_W*px, by+ARR_W*py), (bx-ARR_W*px, by-ARR_W*py)], style="F")
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
        pdf.text(cx+dx, cy, s)
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
def circle(cx, cy, d, dashed=False, w=None):
    if dashed: pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(w or HID_W)
    else: _w(w or GEOM_W)
    pdf.circle(cx, cy, d/2, style="D")
    if dashed: pdf.set_dash_pattern()
def title_block(line1, line2):
    tb_y, tb_x, tb_w, tb_h = PAGE_H-26, 20, PAGE_W-40, 18
    _w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
    pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
    text(tb_x+4, tb_y+6, line1, size=TXT_L, anchor="start")
    text(tb_x+tb_w-4, tb_y+6, "接口参考图(买来板/非加工图) / 1st-angle / 单位 mm", size=TXT_I, anchor="end")
    text(tb_x+4, tb_y+14.5, line2, size=TXT_I, anchor="start")
    text(tb_x+tb_w-4, tb_y+14.5, "2026-06-18 / POV3D / models / zynq_board", size=TXT_I, anchor="end")
def save(name):
    out = Path(__file__).with_name(name)
    try: pdf.output(str(out)); print(f"wrote {out}")
    except PermissionError:
        alt = Path(__file__).with_name(name.replace(".pdf", ".NEW.pdf")); pdf.output(str(alt)); print(f"wrote {alt}")

# ============================================================
# Single A3 sheet.  Long axis (model Y) -> page X (horizontal).
#   plan  pv(mx,my) = (ORX + S*my, ORY - S*mx)   (model +Y->right, +X->up)
#   model Y (long) -> page-X horizontal ;  model X (short) -> page-Y vertical
# ============================================================
new_doc()
text(PAGE_W/2, 13, "POV 3D — ZYNQ7010/7020 板 (鹿小班, 买来现成板 / 非打印 / 接口参考)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19,
     "实测+200DPI扫描: 板 82×52×1.6 / 4×M3Φ3.2 / 2条2.54双排2×20排针(焊于板底针朝下) / 每孔Φ7净空",
     size=TXT_I, anchor="middle")

S = 2.5
ORX, ORY = 168.0, 122.0
def pv(mx, my): return (ORX + S*my, ORY - S*mx)
# board page extents
BLFx, BTPy = pv(BW/2, -BH/2)              # board top-left page corner
BRx,  BBy  = pv(-BW/2, BH/2)              # board bottom-right page corner
text((BLFx+BRx)/2, BTPy-DIM_O2-7, "俯视 (2.5:1) (沿 +Z 看元件面)  尺寸单位: mm", size=TXT_L, anchor="middle")

# board outline
_w(GEOM_W); pdf.rect(BLFx, BTPy, S*BH, S*BW, style="D")

# pin-header pads (2x20 each, BOTTOM side -> dashed) + field outline
for sgn in (-1, 1):                        # two headers at model X = +/-OUTER
    cols = [sgn*OUTER, sgn*(OUTER-PITCH)]
    xa, ya = pv(sgn*(OUTER+0.9), YTOP+0.9)
    xb, yb = pv(sgn*(OUTER-PITCH-0.9), YTOP-(NPIN-1)*PITCH-0.9)
    pdf.set_dash_pattern(dash=1.2, gap=0.8); _w(HID_W)
    pdf.rect(min(xa,xb), min(ya,yb), abs(xb-xa), abs(yb-ya), style="D"); pdf.set_dash_pattern()
    for cx in cols:
        for k in range(NPIN):
            circle(*pv(cx, YTOP-k*PITCH), S*1.2, dashed=True)

# JTAG 2x7 (top side) — solid rectangle
jx, jy = 4.5, -35.5
jw, jh = (7-1)*PITCH+4.0, (2-1)*PITCH+4.0
xa, ya = pv(jx+jh/2, jy-jw/2); xb, yb = pv(jx-jh/2, jy+jw/2)
_w(GEOM_W); pdf.rect(min(xa,xb), min(ya,yb), abs(xb-xa), abs(yb-ya), style="D")
text(*pv(jx, jy), "JTAG 2×7", TXT_I, "middle", True)

# rough connector blocks (indicative, dashed)
def blk(mx, my, sx, sy, lbl):
    xa, ya = pv(mx+sx/2, my-sy/2); xb, yb = pv(mx-sx/2, my+sy/2)
    pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
    pdf.rect(min(xa,xb), min(ya,yb), abs(xb-xa), abs(yb-ya), style="D"); pdf.set_dash_pattern()
    text((xa+xb)/2, (ya+yb)/2, lbl, TXT_I, "middle", True)
blk(-8, 26, 16, 21, "RJ45")
blk(9, 25, 15, 12, "HDMI")
blk(-9, -30, 8, 6, "USB")

# holes + Phi7 keep-out
for (hx, hy) in HOLES:
    cx, cy = pv(hx, hy)
    circle(cx, cy, S*HOLE_D)                               # M3 Phi3.2
    circle(cx, cy, S*KEEPOUT_D, dashed=True, w=0.25)       # Phi7 keep-out

# ---- plan dimensions ----
# horizontals (model Y, page-X): board 82 outer (top), hole 75 inner (top)
hdim(BLFx, BRx, BTPy, BTPy-DIM_O2, "82 (板长)")
hL, hR = pv(0, -37.5)[0], pv(0, 37.5)[0]
hdim(hL, hR, BTPy, BTPy-DIM_O1, "75 (孔距)")
# verticals (model X, page-Y): board 52 outer (left), hole 44.6 inner (left)
vdim(BTPy, BBy, BLFx, BLFx-DIM_O2, "52 (板宽)")
hT, hB = pv(22.3, 0)[1], pv(-22.3, 0)[1]
vdim(hT, hB, BLFx, BLFx-DIM_O1, "44.6 (孔距)")
# corner inset 3.5 (model Y) — bottom-right, below board
hdim(pv(-22.3, 37.5)[0], BRx, BBy, BBy+DIM_O1, "3.5 (内缩)")
# header pin field 48.3 (model Y, page-X) — below the TOP header row
hf0 = pv(OUTER, YTOP); hf1 = pv(OUTER, YTOP-(NPIN-1)*PITCH)
hdim(hf0[0], hf1[0], hf0[1], pv(OUTER, 0)[1]+10, "48.3 (=19×2.54)")
# header outer-row inset 1.5 (model X, page-Y) — right end of top header
xe = pv(OUTER, -30)[0]
vdim(pv(BW/2, -30)[1], pv(OUTER, -30)[1], xe, xe+DIM_O1, "1.5")

# ---- plan call-outs ----
text(pv(22.3, 37.5)[0]+6, pv(22.3, 37.5)[1]-3, "4×M3 Φ3.2 通孔", TXT_I, "start", True)
text((BLFx+BRx)/2, BBy-3, "红虚线圈 = Φ7 净空 (两面禁止遮挡/干涉)", TXT_I, "middle", True)
text(pv(-OUTER, YCEN)[0], pv(-OUTER, YCEN)[1]+9, "2×20 P2.54 (虚线=焊于板底背面)", TXT_I, "middle", True)

# ============================================================
# SIDE view (look along model -X): page-X = model Y (long), page-Y = Z.
#   sv(my, z) = (SOX + S*my, SOZ - S*z)
# ============================================================
SOX, SOZ = 168.0, 238.0
def sv(my, z): return (SOX + S*my, SOZ - S*z)
text(SOX, 200, "侧视 (2.5:1) (沿板短边看)  排针焊于板底, 朝下", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(*sv(-BH/2, BT), S*BH, S*BT, style="D")                         # board slab
ha, hb = sv(YTOP, 0); hc, hd = sv(YTOP-(NPIN-1)*PITCH, -HDR_DROP)       # header envelope (down)
pdf.rect(min(ha,hc), min(hb,hd), abs(hc-ha), abs(hd-hb), style="D")
ja, jb = sv(jx-jw/2, 9.0); jc, jd = sv(jx+jw/2, 0)                      # JTAG shroud (up)
pdf.rect(min(ja,jc), min(jb,jd), abs(jc-ja), abs(jd-jb), style="D")
text((ja+jc)/2, jb-1.5, "JTAG", TXT_I, "middle", True)
vdim(sv(-BH/2,0)[1], sv(-BH/2,BT)[1], sv(-BH/2,0)[0], sv(-BH/2,0)[0]-DIM_O1, "1.6 (板厚)")
vdim(sv(YTOP,-HDR_DROP)[1], sv(YTOP,0)[1], sv(YTOP,0)[0], sv(YTOP,0)[0]+DIM_O1, "8.5 (排针下伸)")
text(sv(YCEN,-HDR_DROP)[0], sv(YCEN,-HDR_DROP)[1]+7, "排针在板底焊接, 针朝下对插", TXT_I, "middle", True)

# ---- notes (right column) ----
nx, ny = 300, 60
text(nx, ny, "说明:", TXT_L, "start")
for i, s in enumerate([
    "- 买来现成板, 不打印; 此图仅记录机械接口尺寸",
    "- 板框 82×52×1.6 (实测), 圆角约 R3",
    "- 4×M3 Φ3.2 通孔; 孔距矩形 75×44.6, 内缩约 3.5",
    "- 每个 M3 孔周围 Φ7 范围两面禁止遮挡/干涉",
    "- 2 条 2.54 双排排针, 各 2×20, 焊于板底针朝下",
    "- 排针距板长中心偏约 3 (朝 JTAG 端); 外排距边约 1.5",
    "- RJ45/HDMI/USB/JTAG 为示意块, 位置粗略",
]):
    text(nx, ny+9+i*6.4, s, TXT_I, "start")

title_block("POV 3D — ZYNQ 板 (买来现成板, 非打印)",
            "板 82×52×1.6 / 4×M3Φ3.2(孔距75×44.6,Φ7净空) / 2×(2.54双排2×20)排针焊于板底朝下 / 接口参考")
save("zynq_board_drawing.pdf")
