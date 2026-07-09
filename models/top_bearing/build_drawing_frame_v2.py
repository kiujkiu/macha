"""
A3 drawing for top_bearing frame v2 — frame_A_v2 / frame_B_v2 on ONE sheet
(GB first-angle, layout/helpers carried over from build_drawing.py sheet 1):
  top view (1:1, POST_R 176.78) + 688 press-pocket DETAIL A (4:1)
  + hub stack section (2:1) + arm cross-section (2:1) + post pad section (2:1)

v2 vs v1: posts moved IN — perfboard is a centre-anchored 25 mm grid, the
four Φ8×350 M6-threaded posts sit in the outermost corner holes (±125,±125)
→ POST_R = 125·√2 = 176.777 (v1: 194.5); ribs R24..R164. All else identical.
Assembly heights: post tops 350; A hub 350..358 (688 #1 353..358);
B hub 358..366 (688 #2 361..366).
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== geometry (mirror build_frame_v2.py) =====
ARM_W, ARM_T = 18.0, 8.0
RIB_W, RIB_T = 4.0, 6.0
HUB_D, BOLT_R = 44.0, 14.0
BRG_D, BRG_DEPTH, BRG_SH = 15.8, 5.0, 13.0
PAD_D = 18.0
POST_R = 125.0 * math.sqrt(2.0)          # 176.777
RIB_R0, RIB_R1 = 24.0, 164.0
M6_CLEAR = 6.5
M3_TIGHT = 3.2

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
def title_block(line1, line2):
    tb_y, tb_x, tb_w, tb_h = PAGE_H - 28, 20, PAGE_W - 40, 18
    _w(0.3)
    pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
    pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
    text(tb_x + 4, tb_y + 6, line1, size=TXT_L, anchor="start")
    text(tb_x + tb_w - 4, tb_y + 6, "投影 1st-angle / PLA / 单位 mm", size=TXT_I, anchor="end")
    text(tb_x + 4, tb_y + 14.5, line2, size=TXT_I, anchor="start")
    text(tb_x + tb_w - 4, tb_y + 14.5, "2026-07-09 / POV3D / models / top_bearing", size=TXT_I, anchor="end")
def save(name):
    out = Path(__file__).with_name(name)
    try:
        pdf.output(str(out)); print(f"wrote {out}")
    except PermissionError:
        alt = Path(__file__).with_name(name.replace(".pdf", ".NEW.pdf"))
        pdf.output(str(alt)); print(f"wrote {alt} (original locked)")

# ============================================================
# SHEET — frame_A_v2 / frame_B_v2
# ============================================================
text(PAGE_W/2, 14, "POV 3D top_bearing frame v2 — frame_A_v2 / frame_B_v2  (静止轴承架, 锁 4 立柱顶, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"臂 {ARM_W:g}×{ARM_T:g} (宽=柱垫Φ{PAD_D:g}) + 筋 {RIB_W:g}×{RIB_T:g} (R{RIB_R0:g}..R{RIB_R1:g}) / 轴毂 Φ{HUB_D:g} 双层, 各嵌 1 × 688 (腔 Φ{BRG_D:g}×{BRG_DEPTH:g} 压入, 挡肩 Φ{BRG_SH:g}), 4×Φ{M3_TIGHT:g}@R{BOLT_R:g} / "
     f"柱垫 Φ{PAD_D:g} @R{POST_R:.2f}: 仅 Φ{M6_CLEAR:g} 通孔, A 用 M6×16 / B 柱垫高16 用 M6×30",
     size=TXT_I, anchor="middle")

# --- frame_A_v2 top view 1:1 ---
fx0, fy0 = 58.0, 245.0
def fv(x, y): return (fx0 + x, fy0 - y)
text(fx0 + 100, 32, "frame_A_v2 俯视 (1:1)  尺寸单位: mm", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.circle(*fv(0, 0), HUB_D/2, style="D")
for ang in (0.0, 90.0):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for off in (-ARM_W/2, ARM_W/2):
        line(*fv(18*ca - off*sa, 18*sa + off*ca),
             *fv((POST_R-9)*ca - off*sa, (POST_R-9)*sa + off*ca), GEOM_W)
    for off in (-RIB_W/2, RIB_W/2):
        line(*fv(RIB_R0*ca - off*sa, RIB_R0*sa + off*ca),
             *fv(RIB_R1*ca - off*sa, RIB_R1*sa + off*ca), 0.25)
    pdf.circle(*fv(POST_R*ca, POST_R*sa), PAD_D/2, style="D")
    pdf.circle(*fv(POST_R*ca, POST_R*sa), M6_CLEAR/2, style="D")
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
pdf.circle(*fv(0, 0), BRG_D/2, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)
pdf.circle(*fv(0, 0), BRG_SH/2, style="D")
for k in range(4):
    a = math.radians(45 + 90*k)
    pdf.circle(*fv(BOLT_R*math.cos(a), BOLT_R*math.sin(a)), M3_TIGHT/2, style="D")
hdim(fv(0, 0)[0], fv(POST_R, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"{POST_R:.2f}")
hdim(fv(RIB_R0, 0)[0], fv(RIB_R1, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O2, f"{RIB_R1-RIB_R0:g} (筋)")
vdim(fv(0, 0)[1], fv(0, POST_R)[1], fv(0, 0)[0], fv(0, 0)[0] - DIM_O1, f"{POST_R:.2f}")
text(*fv(40, 196), "双臂 90°, 柱垫对角放置 → 打印床 207.8×207.8 (X2D 256 内)", TXT_I, "start", True)
text(*fv(40, 189), "柱位 = 洞洞板最外角孔 (±125,±125), R = 125×√2 ≈ 176.78", TXT_I, "start", True)
text(*fv(40, 60), f"中心: 688 腔 Φ{BRG_D:g}(虚线,压入) + 挡肩 Φ{BRG_SH:g} / 4 × Φ{M3_TIGHT:g} @ R{BOLT_R:g}", TXT_I, "start", True)
text(*fv(40, 46), f"臂 {ARM_W:g} 宽 × {ARM_T:g} 厚, 筋 {RIB_W:g}×{RIB_T:g} (A 上 / B 下)", TXT_I, "start", True)

# ---- DETAIL A (4:1) — 688 press pocket (non-through feature) ----
DAS = 4.0
ddx, ddy = 222.0, 96.0            # ddy = local z0 (hub underside); x kept clear
                                  # of the hub-stack section's left "5" vdim @274
def dv(x, z): return (ddx + DAS*x, ddy - DAS*z)
text(ddx, 40, "详图 A (4:1) — 688 压装孔 (A/B 同)", size=TXT_L, anchor="middle")
pr_, shr = BRG_D/2, BRG_SH/2      # 7.9, 6.5
_w(GEOM_W)
for sgn in (1, -1):
    pts = [(11, 0), (11, 8), (pr_, 8), (pr_, 3), (shr, 3), (shr, 0), (11, 0)]
    prev = None
    for (x, z) in pts:
        cur = dv(sgn*x, z)
        if prev: line(*prev, *cur, GEOM_W)
        prev = cur
# 688 bearing (dashed, pressed into the pocket) + centre line
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(0.25)
pdf.rect(dv(-8, 8)[0], dv(-8, 8)[1], DAS*16, DAS*5, style="D")
pdf.set_dash_pattern(dash=3.0, gap=1.5)
line(*dv(0, 10), *dv(0, -2), 0.2)
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(dv(-pr_, 8)[0], dv(pr_, 8)[0], dv(0, 8)[1], dv(0, 8)[1] - DIM_O1, f"Φ{BRG_D:g}")
hdim(dv(-shr, 0)[0], dv(shr, 0)[0], dv(0, 0)[1], dv(0, 0)[1] + DIM_O1, f"Φ{BRG_SH:g}")
vdim(dv(0, 3)[1], dv(0, 8)[1], dv(-11, 0)[0], dv(-11, 0)[0] - 8, f"{BRG_DEPTH:g}")
text(ddx, ddy + 20, "688 轴承 8×16×5 压入 (腔 Φ15.8 偏紧, 腔口朝毂顶面)", TXT_I, "middle", True)
text(ddx, ddy + 26, "挡肩 Φ13 贯通 — 只托外圈, 内圈不蹭", TXT_I, "middle", True)

# --- hub stack section 2:1 ---
SS = 2.0
sx0, sy0 = 330.0, 105.0
def sv(x, z): return (sx0 + SS*x, sy0 - SS*z)
text(sx0, 40, "轴毂叠层剖面 (2:1) — 688 ×2 + Φ8 轴", size=TXT_L, anchor="middle")
hw = HUB_D/2
_w(GEOM_W)
# A hub (z 0..8): pocket 3..8 opening UP; B hub (8..16): pocket 11..16 opening UP
for z0, z1, pk0, pk1 in ((0, 8, 3, 8), (8, 16, 11, 16)):
    for sgn in (1, -1):
        line(*sv(sgn*hw, z0), *sv(sgn*hw, z1), GEOM_W)
        line(*sv(sgn*pr_, pk0), *sv(sgn*pr_, pk1), GEOM_W)
        line(*sv(sgn*shr, z0), *sv(sgn*shr, pk0), GEOM_W)
        line(*sv(sgn*pr_, pk0), *sv(sgn*shr, pk0), GEOM_W)
        line(*sv(sgn*hw, z0), *sv(sgn*shr, z0), GEOM_W)
        line(*sv(sgn*hw, z1), *sv(sgn*pr_, z1), GEOM_W)
# bearings (dashed rects) and rod centreline
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(0.25)
for bz in (3, 11):
    pdf.rect(sv(-8, bz + 5)[0], sv(-8, bz + 5)[1], SS*16, SS*5, style="D")
pdf.set_dash_pattern(dash=3.0, gap=1.5)
line(*sv(0, -10), *sv(0, 22), 0.2)
for sgn in (1, -1):
    line(*sv(sgn*4, -8), *sv(sgn*4, 20), 0.25)
pdf.set_dash_pattern(); _w(GEOM_W)
vdim(sv(0, 0)[1], sv(0, 8)[1], sv(hw, 0)[0], sv(hw, 0)[0] + 8, "8")
vdim(sv(0, 8)[1], sv(0, 16)[1], sv(hw, 0)[0], sv(hw, 0)[0] + 16, "8")
vdim(sv(0, 3)[1], sv(0, 8)[1], sv(-hw, 0)[0], sv(-hw, 0)[0] - 8, f"{BRG_DEPTH:g}")
hdim(sv(-pr_, 16)[0], sv(pr_, 16)[0], sv(0, 16)[1], sv(0, 16)[1] - DIM_O1, f"Φ{BRG_D:g}")
hdim(sv(-shr, 0)[0], sv(shr, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + DIM_O1, f"Φ{BRG_SH:g}")
text(sx0, sy0 + 22, "A 腔口朝上 (688 #1, 353-358), B 腔口朝上 (688 #2, 361-366)", TXT_I, "middle", True)
text(sx0, sy0 + 28, "柱顶 350: A 毂 350-358, B 毂 358-366; Φ8 轴穿两轴承内圈", TXT_I, "middle", True)

# --- arm cross-section 2:1 (bar 18×8 + rib 4×6 on top, frame_A_v2) ---
ax0, ay0 = 160.0, 150.0
def av(x, z): return (ax0 + SS*x, ay0 - SS*z)
text(ax0, 99, "臂横截面 (2:1, A; B 筋朝下)", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(av(-ARM_W/2, ARM_T)[0], av(-ARM_W/2, ARM_T)[1], SS*ARM_W, SS*ARM_T, style="D")
pdf.rect(av(-RIB_W/2, ARM_T + RIB_T)[0], av(-RIB_W/2, ARM_T + RIB_T)[1], SS*RIB_W, SS*RIB_T, style="D")
hdim(av(-ARM_W/2, 0)[0], av(ARM_W/2, 0)[0], av(0, 0)[1], av(0, 0)[1] + DIM_O1, f"{ARM_W:g}")
hdim(av(-RIB_W/2, ARM_T + RIB_T)[0], av(RIB_W/2, ARM_T + RIB_T)[0],
     av(0, ARM_T + RIB_T)[1], av(0, ARM_T + RIB_T)[1] - DIM_O1, f"{RIB_W:g}")
vdim(av(0, 0)[1], av(0, ARM_T)[1], av(ARM_W/2, 0)[0], av(ARM_W/2, 0)[0] + 8, f"{ARM_T:g}")
vdim(av(0, ARM_T)[1], av(0, ARM_T + RIB_T)[1], av(ARM_W/2, 0)[0], av(ARM_W/2, 0)[0] + 16, f"{RIB_T:g}")

# --- post pad M6 section 2:1 (frame_A_v2 pad on a post) ---
px0, py0 = 330.0, 215.0
def qv(x, z): return (px0 + SS*x, py0 - SS*z)
text(px0, 152, "柱垫剖面 (2:1, frame_A_v2; B 柱高 16): 仅 Φ6.5 通孔", size=TXT_L, anchor="middle")
pr, thr = PAD_D/2, M6_CLEAR/2
_w(GEOM_W)
pts_r = [(thr, 0), (pr, 0), (pr, 8), (thr, 8), (thr, 0)]
for sgn in (1, -1):
    prev = None
    for (x, z) in pts_r:
        cur = qv(sgn*x, z)
        if prev: line(*prev, *cur, GEOM_W)
        prev = cur
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
line(*qv(-4, 0), *qv(-4, -14), HID_W); line(*qv(4, 0), *qv(4, -14), HID_W)
line(*qv(-thr, 0), *qv(-thr, -10), 0.2); line(*qv(thr, 0), *qv(thr, -10), 0.2)
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(qv(-pr, 8)[0], qv(pr, 8)[0], qv(0, 8)[1], qv(0, 8)[1] - DIM_O1, f"Φ{PAD_D:g}")
hdim(qv(-thr, 0)[0], qv(thr, 0)[0], qv(0, 0)[1], qv(0, 0)[1] + DIM_O1, f"Φ{M6_CLEAR:g}")
vdim(qv(0, 0)[1], qv(0, 8)[1], qv(-pr, 0)[0], qv(-pr, 0)[0] - 8, "8")
text(px0, py0 + 18, "M6 螺丝自上穿入拧进立柱顶 (A: M6×16, B: M6×30) — 锁死轴向", TXT_I, "middle", True)
text(px0, py0 + 24, "立柱 Φ8×350 (轴向 M6 内丝), 柱顶 Z = 350", TXT_I, "middle", True)

title_block("POV 3D — top_bearing frame v2 / frame_A_v2 + frame_B_v2 (各 ×1) / PLA / 柱位 (±125,±125) Φ8×350 M6螺纹柱",
            "R柱 = 125×√2 ≈ 176.78 / 厚度: 臂/毂 8, 筋 6 (总高 A=14, B=16), 柱垫 A=8/B=16 仅Φ6.5通孔 / 高度: 柱顶350, A 350-358 (轴承353-358), B 358-366 (轴承361-366) / "
            "BOM: 688×2, M6×16×2 (A垫), M6×30×2 (B柱垫), M3×20+螺母×4 / A 正打, B 反打")
save("top_bearing_frame_v2_drawing.pdf")
