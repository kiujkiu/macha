"""
A3 drawings for top_bearing v2 — split into TWO PDFs for readability:
  top_bearing_frame_drawing.pdf — frame_A top view (1:1!) + hub stack
      section (2:1) + post-pad M6 section (2:1)
  top_bearing_cap_drawing.pdf   — top_cap front view (1:1) + plan view
      (1:1) + side profile section (3:1)
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== geometry (mirror build_stl.py v2) =====
ARM_W, ARM_T = 18.0, 8.0
RIB_W, RIB_T = 4.0, 6.0
HUB_D, BOLT_R = 44.0, 14.0
BRG_D, BRG_DEPTH, BRG_SH = 15.8, 5.0, 13.0
PAD_D, POST_R = 18.0, 194.5
M6_CLEAR, M6_CB_D = 6.5, 11.0
M3_TIGHT, M3_CLEAR = 3.2, 3.4
CAP_T, SLAB_T = 4.0, 9.0          # v3.2: flat top slab 9 thick (replaces column/flange/spoke)
M6_BORE, HEAD_D, HEAD_DEPTH = 6.2, 13.0, 2.7
TP_X0, TP_X1, TP_HW = -18.3, 65.0, 72.0    # v3.4: slab WIDER (Y±72) + LONGER (+X 65)
CW_M6, CW_TRI = 6.5, 14.0
CWA_X, CWB_X = 46.0, 46.0 + 14.0 * (3 ** 0.5) / 2   # 46.0 / 58.12 (rows ≈2cm farther out)
CW_A = [(CWA_X, (k - 4.5) * CW_TRI) for k in range(10)]   # 10 holes
CW_B = [(CWB_X, (k - 4.0) * CW_TRI) for k in range(9)]    # 9 holes
BP_H = 22.7
SCREW_YZ = [(-94.0, 13.0), (-34.0, 13.0), (35.0, 12.0), (95.0, 12.0)]

PAGE_W, PAGE_H = 420.0, 297.0
GEOM_W, DIM_W, EXT_W, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W = 4.2, 1.5
EXT_OV, EXT_GP = 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 5.0, 8.0, 9.5, 5.0
DIM_O1, DIM_O2 = 12.0, 22.0
_FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
if not os.path.exists(_FONT): raise FileNotFoundError("SimHei not found")

pdf = None   # current document (helpers reference this global)

def new_doc():
    global pdf
    pdf = FPDF(orientation="L", unit="mm", format="A3")
    pdf.set_auto_page_break(False)
    pdf.add_page()
    pdf.add_font("SimHei", "", _FONT)
    pdf.set_line_width(0.3)
    pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
    return pdf

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
    text(tb_x + tb_w - 4, tb_y + 14.5, "2026-06-12 / POV3D / models / top_bearing", size=TXT_I, anchor="end")
def save(name):
    out = Path(__file__).with_name(name)
    try:
        pdf.output(str(out)); print(f"wrote {out}")
    except PermissionError:
        alt = Path(__file__).with_name(name.replace(".pdf", ".NEW.pdf"))
        pdf.output(str(alt)); print(f"wrote {alt} (original locked)")

# ============================================================
# SHEET 1 — frame_A / frame_B
# ============================================================
new_doc()
text(PAGE_W/2, 14, "POV 3D top_bearing v3 — frame_A / frame_B  (顶架, 锁 4 立柱顶, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"臂 {ARM_W:g}×{ARM_T:g} (宽=柱垫Φ{PAD_D:g}) + 筋 {RIB_W:g}×{RIB_T:g} / 轴毂 Φ{HUB_D:g} 双层, 各嵌 1 × 688 (腔 Φ{BRG_D:g}×{BRG_DEPTH:g} 压入, 挡肩 Φ{BRG_SH:g}), 4×Φ{M3_TIGHT:g}@R{BOLT_R:g} / "
     f"柱垫 Φ{PAD_D:g} @R{POST_R:g}: 仅 Φ{M6_CLEAR:g} 通孔, A 用 M6×16 / B 柱垫高16 用 M6×30",
     size=TXT_I, anchor="middle")

# --- frame_A top view 1:1 ---
fx0, fy0 = 58.0, 245.0
def fv(x, y): return (fx0 + x, fy0 - y)
text(fx0 + 100, 32, "frame_A 俯视 (1:1)  尺寸单位: mm", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.circle(*fv(0, 0), HUB_D/2, style="D")
for ang in (0.0, 90.0):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for off in (-ARM_W/2, ARM_W/2):
        line(*fv(18*ca - off*sa, 18*sa + off*ca),
             *fv((POST_R-9)*ca - off*sa, (POST_R-9)*sa + off*ca), GEOM_W)
    for off in (-RIB_W/2, RIB_W/2):
        line(*fv(24*ca - off*sa, 24*sa + off*ca),
             *fv(182*ca - off*sa, 182*sa + off*ca), 0.25)
    pdf.circle(*fv(POST_R*ca, POST_R*sa), PAD_D/2, style="D")
    pdf.circle(*fv(POST_R*ca, POST_R*sa), M6_CLEAR/2, style="D")
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
pdf.circle(*fv(0, 0), BRG_D/2, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)
pdf.circle(*fv(0, 0), BRG_SH/2, style="D")
for k in range(4):
    a = math.radians(45 + 90*k)
    pdf.circle(*fv(BOLT_R*math.cos(a), BOLT_R*math.sin(a)), M3_TIGHT/2, style="D")
hdim(fv(0, 0)[0], fv(POST_R, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"{POST_R:g}")
hdim(fv(24, 0)[0], fv(182, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O2, "158 (筋)")
vdim(fv(0, 0)[1], fv(0, POST_R)[1], fv(0, 0)[0], fv(0, 0)[0] - DIM_O1, f"{POST_R:g}")
text(*fv(40, 196), f"双臂 90°, 柱垫对角放置 → 打印床 224×224 (X2D 256 内)", TXT_I, "start", True)
text(*fv(40, 60), f"中心: 688 腔 Φ{BRG_D:g}(虚线,压入) + 挡肩 Φ{BRG_SH:g} / 4 × Φ{M3_TIGHT:g} @ R{BOLT_R:g}", TXT_I, "start", True)
text(*fv(40, 46), f"臂 {ARM_W:g} 宽 × {ARM_T:g} 厚, 筋 {RIB_W:g}×{RIB_T:g} (A 上 / B 下)", TXT_I, "start", True)

# --- hub stack section 2:1 ---
SS = 2.0
sx0, sy0 = 330.0, 105.0
def sv(x, z): return (sx0 + SS*x, sy0 - SS*z)
text(sx0, 40, "轴毂叠层剖面 (2:1) — 688 ×2 + Φ8 螺柱", size=TXT_L, anchor="middle")
hw, pr_, shr = HUB_D/2, BRG_D/2, BRG_SH/2
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
# bearings (hatch-free rects) and standoff centerline
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
text(sx0, sy0 + 22, "A 腔口朝上(688 #1, 403-408), B 腔口朝上(688 #2, 411-416)", TXT_I, "middle", True)
text(sx0, sy0 + 28, "Φ8×50 螺柱穿两轴承内圈 (368.4-418.4); 腔 Φ15.8 偏紧压入", TXT_I, "middle", True)

# --- post pad M6 section 2:1 (frame_A pad on a post) ---
px0, py0 = 330.0, 215.0
def qv(x, z): return (px0 + SS*x, py0 - SS*z)
text(px0, 152, "柱垫剖面 (2:1, frame_A; B 柱高 16): 仅 Φ6.5 通孔", size=TXT_L, anchor="middle")
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
# --- arm cross-section 2:1 (bar 14×8 + rib 4×6 on top, frame_A) ---
ax0, ay0 = 195.0, 135.0
def av(x, z): return (ax0 + SS*x, ay0 - SS*z)
text(ax0, 84, "臂横截面 (2:1, frame_A; B 筋朝下)", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(av(-ARM_W/2, ARM_T)[0], av(-ARM_W/2, ARM_T)[1], SS*ARM_W, SS*ARM_T, style="D")
pdf.rect(av(-RIB_W/2, ARM_T + RIB_T)[0], av(-RIB_W/2, ARM_T + RIB_T)[1], SS*RIB_W, SS*RIB_T, style="D")
hdim(av(-ARM_W/2, 0)[0], av(ARM_W/2, 0)[0], av(0, 0)[1], av(0, 0)[1] + DIM_O1, f"{ARM_W:g}")
hdim(av(-RIB_W/2, ARM_T + RIB_T)[0], av(RIB_W/2, ARM_T + RIB_T)[0],
     av(0, ARM_T + RIB_T)[1], av(0, ARM_T + RIB_T)[1] - DIM_O1, f"{RIB_W:g}")
vdim(av(0, 0)[1], av(0, ARM_T)[1], av(ARM_W/2, 0)[0], av(ARM_W/2, 0)[0] + 8, f"{ARM_T:g}")
vdim(av(0, ARM_T)[1], av(0, ARM_T + RIB_T)[1], av(ARM_W/2, 0)[0], av(ARM_W/2, 0)[0] + 16, f"{RIB_T:g}")

title_block("POV 3D — top_bearing v3 / frame_A + frame_B (各 ×1)",
            "厚度: 臂/毂 8, 筋 6 (总高 A=14, B=16), 柱垫 A=8/B=16 仅Φ6.5通孔 / BOM: 688×2, M6×16 ×2 + M6×30 ×2, M3×20+螺母 ×4 / A 正打, B 反打")
save("top_bearing_frame_drawing.pdf")

# ============================================================
# SHEET 2 — top_cap
# ============================================================
new_doc()
text(PAGE_W/2, 14, "POV 3D top_bearing v3.4 — top_cap  (旋转盖板, 顶面全平 + M6配重排, PLA)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"背板 211×{BP_H:g}×{CAP_T:g} (4×Φ{M3_CLEAR:g} 锁屏顶井字孔) / 顶板平板 {TP_X1-TP_X0:g}×{2*TP_HW:g}×{SLAB_T:g} (整块顶面全平) / 中心 Φ{M6_BORE:g}通 + 底面头槽 Φ{HEAD_D:g}×{HEAD_DEPTH:g} / "
     f"+X 悬出区 19×Φ{CW_M6:g} M6配重孔(10+9品字形, 三角{CW_TRI:g}, 顶面Φ{HEAD_D:g}×{HEAD_DEPTH:g}沉孔, 加M6平头螺丝配平) / 倒扣平放免支撑",
     size=TXT_I, anchor="middle")

# --- front view 1:1 (looking -X) ---
cx0, cy0 = 210.0, 88.0
def cv(y, z): return (cx0 + y, cy0 - z)
SLAB_TOP = BP_H + (SLAB_T - CAP_T)   # 27.7
SLAB_BOT = SLAB_TOP - SLAB_T         # 18.7
text(cx0 - 80, 40, "正视 (1:1)  (沿 -X 看背板)  尺寸单位: mm", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(cv(-105, BP_H)[0], cv(-105, BP_H)[1], 211, BP_H, style="D")           # back plate
pdf.rect(cv(-TP_HW, SLAB_TOP)[0], cv(-TP_HW, SLAB_TOP)[1], 2*TP_HW, SLAB_T, style="D")  # flat slab
# back-plate ends (|Y|>72, beyond the slab) filled UP to the top face (免悬空打印)
pdf.rect(cv(TP_HW, SLAB_TOP)[0], cv(TP_HW, SLAB_TOP)[1], 105 - TP_HW, SLAB_TOP - BP_H, style="D")
pdf.rect(cv(-105, SLAB_TOP)[0], cv(-105, SLAB_TOP)[1], 105 - TP_HW, SLAB_TOP - BP_H, style="D")
for (sy_, sz_) in SCREW_YZ:
    pdf.circle(*cv(sy_, sz_), M3_CLEAR/2, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cv(sy_-3, sz_)[0], cv(sy_, sz_)[1], cv(sy_+3, sz_)[0], cv(sy_, sz_)[1])
    pdf.line(cv(sy_, sz_)[0], cv(sy_, sz_-3)[1], cv(sy_, sz_)[0], cv(sy_, sz_+3)[1])
    pdf.set_dash_pattern(); _w(GEOM_W)
hdim(cv(-105, 0)[0], cv(106, 0)[0], cv(0, 0)[1], cv(0, 0)[1] + DIM_O2, "211")
hdim(cv(-94, 0)[0], cv(-34, 0)[0], cv(0, 0)[1], cv(0, 0)[1] + DIM_O1, "60")
hdim(cv(-34, 0)[0], cv(35, 0)[0], cv(0, 0)[1], cv(0, 0)[1] + 17, "69")
hdim(cv(35, 0)[0], cv(95, 0)[0], cv(0, 0)[1], cv(0, 0)[1] + DIM_O1, "60")
hdim(cv(-TP_HW, SLAB_TOP)[0], cv(TP_HW, SLAB_TOP)[0],
     cv(0, SLAB_TOP)[1], cv(0, SLAB_TOP)[1] - DIM_O1, f"{2*TP_HW:g}")
vdim(cv(0, BP_H)[1], cv(0, 0)[1], cv(106, 0)[0], cv(106, 0)[0] + DIM_O1, f"{BP_H:g}")
vdim(cv(0, SLAB_TOP)[1], cv(0, 0)[1], cv(-105, 0)[0], cv(-105, 0)[0] - DIM_O1,
     f"{SLAB_TOP:g}")
vdim(cv(0, SCREW_YZ[0][1])[1], cv(0, 0)[1], cv(-94 - 6, 0)[0], cv(-94 - 14, 0)[0], "13")
vdim(cv(0, SCREW_YZ[3][1])[1], cv(0, 0)[1], cv(95 + 6, 0)[0], cv(95 + 14, 0)[0], "12")
text(cv(-90, 33)[0], cv(-90, 33)[1],
     f"4 × Φ{M3_CLEAR:g} 对屏顶井字孔 (左对孔高 13, 右对 12: +Y 屏整体高 1)", TXT_I, "start", True)

# --- plan view 1:1 (looking -Z, flat top) ---
gx0, gy0 = 210.0, 205.0
def gv(x, y): return (gx0 + y, gy0 - x)   # plan: pdf x = part Y, pdf y = -part X
text(gx0 - 150, 136, "俯视 (1:1)  (沿 -Z 看顶面 — 全平)", size=TXT_L, anchor="middle")
_w(GEOM_W)
pdf.rect(gv(TP_X1, -TP_HW)[0], gv(TP_X1, -TP_HW)[1], 2*TP_HW, TP_X1 - TP_X0, style="D")  # flat slab
pdf.set_dash_pattern(dash=1.5, gap=1.0); _w(HID_W)
pdf.rect(gv(-14.3, -105)[0], gv(-14.3, -105)[1], 211, CAP_T, style="D")                  # back plate (hidden, below)
pdf.circle(*gv(0, 0), HEAD_D/2, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)
pdf.circle(*gv(0, 0), M6_BORE/2, style="D")
# M6 counterweight bank (品字形) in the +X overhang: Φ13 top CB + Φ6.5 through
for (cx, cy) in CW_A + CW_B:
    pdf.circle(*gv(cx, cy), HEAD_D/2, style="D")     # Φ13 counterbore (top face)
    pdf.circle(*gv(cx, cy), CW_M6/2, style="D")      # Φ6.5 through
# detail mark on one CW hole
_w(0.25); pdf.set_dash_pattern(dash=1.0, gap=0.8)
pdf.circle(*gv(CWB_X, 0), 9.0, style="D"); pdf.set_dash_pattern()
text(gv(CWB_X, 0)[0] + 9.5, gv(CWB_X, 0)[1] - 8, "A", size=TXT_L)
hdim(gv(TP_X1, -TP_HW)[0], gv(TP_X1, TP_HW)[0], gv(TP_X1, 0)[1], gv(TP_X1, 0)[1] - DIM_O1,
     f"{2*TP_HW:g}")
vdim(gv(TP_X1, 0)[1], gv(TP_X0, 0)[1], gv(0, TP_HW)[0] + 6, gv(0, TP_HW)[0] + 14,
     f"{TP_X1 - TP_X0:g}")
hdim(gv(CWA_X, 7)[0], gv(CWA_X, 21)[0], gv(CWA_X, 21)[1], gv(CWA_X, 21)[1] + DIM_O1, f"{CW_TRI:g}")
vdim(gv(0, 0)[1], gv(CWA_X, 0)[1], gv(0, -TP_HW)[0] - 6, gv(0, -TP_HW)[0] - 14, f"{CWA_X:g}")
text(286, 150, f"19×Φ{CW_M6:g} M6 配重孔", TXT_I, "start", True)
text(286, 156, f"10+9 品字形, 三角间距 {CW_TRI:g}", TXT_I, "start", True)
text(286, 162, f"顶面 Φ{HEAD_D:g}×{HEAD_DEPTH:g} 沉孔 (详图A)", TXT_I, "start", True)
text(286, 210, f"中心孔 Φ{M6_BORE:g} 通 / 底面头槽 Φ{HEAD_D:g}×{HEAD_DEPTH:g} (虚线)", TXT_I, "start", True)

# ---- DETAIL A (4:1) — M6 counterweight counterbored hole (upper-left, free) ----
DAS = 4.0; dax, daz = 22.0, 110.0
def da(x, z): return (dax + DAS*x, daz - DAS*z)
text(dax + 32, 50, "详图 A (4:1)  M6 配重沉孔", size=TXT_L, anchor="middle")
hd, br6 = HEAD_D/2, CW_M6/2; cbz = SLAB_T - HEAD_DEPTH   # 6.3
_w(GEOM_W)
for a, b in [((0,0),(8-br6,0)),((8-br6,0),(8-br6,cbz)),((8-br6,cbz),(8-hd,cbz)),
             ((8-hd,cbz),(8-hd,SLAB_T)),((8-hd,SLAB_T),(0,SLAB_T)),((0,SLAB_T),(0,0))]:
    line(*da(*a), *da(*b), GEOM_W)
for a, b in [((16,0),(8+br6,0)),((8+br6,0),(8+br6,cbz)),((8+br6,cbz),(8+hd,cbz)),
             ((8+hd,cbz),(8+hd,SLAB_T)),((8+hd,SLAB_T),(16,SLAB_T)),((16,SLAB_T),(16,0))]:
    line(*da(*a), *da(*b), GEOM_W)
pdf.set_dash_pattern(dash=1.2, gap=0.8); _w(0.13); pdf.line(*da(8,SLAB_T+1), *da(8,-1)); pdf.set_dash_pattern()
hdim(da(8-hd,SLAB_T)[0], da(8+hd,SLAB_T)[0], da(8,SLAB_T)[1], da(8,SLAB_T)[1]-DIM_O1, f"Φ{HEAD_D:g}")
hdim(da(8-br6,0)[0], da(8+br6,0)[0], da(8,0)[1], da(8,0)[1]+DIM_O1, f"Φ{CW_M6:g} 通")
vdim(da(0,cbz)[1], da(0,SLAB_T)[1], da(0,0)[0], da(0,0)[0]-DIM_O1, f"{HEAD_DEPTH:g}")
vdim(da(16,0)[1], da(16,SLAB_T)[1], da(16,0)[0], da(16,0)[0]+DIM_O1, f"{SLAB_T:g}")
text(dax - 8, 122, "(顶面进, M6平头沉入)", TXT_I, "start", True)

# --- side profile section 2:1 (looking +Y; slab now reaches +X 45) ---
PS = 2.0
px0, py0 = 95.0, 252.0
def pv(x, z): return (px0 + PS*x, py0 - PS*z)
text(px0 + 45, 228, "侧视剖面 (2:1)  (沿 +Y 看)", size=TXT_L, anchor="middle")
# local z=0 at slab bottom; slab 0..SLAB_T. Back plate full extent is in the
# front view (211×22.7); here only its attach face is shown at the -X end.
br, hr = M6_BORE/2, HEAD_D/2
cwl, cwr = CWB_X - CW_M6/2, CWB_X + CW_M6/2       # the (38.12,0) M6 hole, in this section plane
segs = [
    # flat top, broken by the M6 bore AND the centre-line M6 counterweight hole
    ((TP_X0, SLAB_T), (-br, SLAB_T)),
    ((br, SLAB_T), (cwl, SLAB_T)),
    ((cwr, SLAB_T), (TP_X1, SLAB_T)),
    ((cwl, SLAB_T), (cwl, 0)), ((cwr, SLAB_T), (cwr, 0)),   # M6 counterweight hole walls (Φ6.5 through)
    ((TP_X1, SLAB_T), (TP_X1, 0)),                # +X face
    ((TP_X1, 0), (cwr, 0)), ((cwl, 0), (hr, 0)),  # bottom, broken at the M6 hole
    ((hr, 0), (hr, HEAD_DEPTH)),                  # head recess wall (R)
    ((hr, HEAD_DEPTH), (br, HEAD_DEPTH)),
    ((br, HEAD_DEPTH), (br, SLAB_T)),             # bore wall (R) up to top
    ((-br, SLAB_T), (-br, HEAD_DEPTH)),           # bore wall (L)
    ((-br, HEAD_DEPTH), (-hr, HEAD_DEPTH)),
    ((-hr, HEAD_DEPTH), (-hr, 0)),                # head recess wall (L)
    ((-hr, 0), (TP_X0, 0)),                       # bottom toward -X face
    ((TP_X0, 0), (TP_X0, SLAB_T)),                # -X face (back plate attaches here)
]
_w(GEOM_W)
for (a, b) in segs:
    line(*pv(*a), *pv(*b), GEOM_W)
# bore centre line
pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
pdf.line(*pv(0, SLAB_T + 2), *pv(0, -2))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(pv(TP_X0, 0)[0], pv(TP_X1, 0)[0], pv(0, 0)[1], pv(0, 0)[1] + DIM_O1, f"{TP_X1 - TP_X0:g}")
hdim(pv(-br, SLAB_T)[0], pv(br, SLAB_T)[0], pv(0, SLAB_T)[1], pv(0, SLAB_T)[1] - DIM_O1,
     f"Φ{M6_BORE:g}")
hdim(pv(-hr, 0)[0], pv(hr, 0)[0], pv(0, 0)[1], pv(0, 0)[1] + DIM_O2, f"Φ{HEAD_D:g}")
vdim(pv(0, 0)[1], pv(0, SLAB_T)[1], pv(TP_X1, 0)[0], pv(TP_X1, 0)[0] + DIM_O1, f"{SLAB_T:g}")
vdim(pv(0, 0)[1], pv(0, HEAD_DEPTH)[1], pv(hr, 0)[0] + 14, pv(hr, 0)[0] + 22, f"头槽 {HEAD_DEPTH:g}")
text(pv(TP_X0, SLAB_T)[0] - 4, pv(TP_X0, SLAB_T)[1] - 6, "背板向下延伸 (211×22.7, 见正视)",
     TXT_I, "start", True)
text(250, 240, f"顶面全平 (无柱/翻边/辐板)", TXT_I, "start", True)
text(250, 246, f"M6×40 平头自下入头槽; 螺柱旋至咬合≥10", TXT_I, "start", True)
text(250, 252, f"M6 螺母在柱顶锁紧; Φ8×50 螺柱穿两 688 内圈", TXT_I, "start", True)
title_block("POV 3D — top_bearing v3.4 / top_cap (×1)",
            "厚度: 背板4, 顶板平板9 (144×83.3, 顶面全平), 头槽Φ13×2.7, 中心孔Φ6.2 / +X悬出19×Φ6.5 M6配重(10+9品字形三角14) / 背板端头(|Y|>72)补至顶面免悬空 / BOM: M6×40, M6螺母, Φ8×50螺柱, M3×8 ×4, M6平头螺丝(配重,按需) / 倒扣平放免支撑")
save("top_bearing_cap_drawing.pdf")
