"""
A3 landscape 2D engineering drawing for POV3D hub_shim_v4 (转子侧垫片).

  1) TOP VIEW (1:1)    — 外圆 Φ100 全貌
  2) DETAIL A (4:1)    — 中央孔组: 4×Φ3.4 菱形 (对角 12×15) + 中央 Φ6.2
  3) SECTION B-B (4:1) — 沿 Y 轴局部剖 (过 (0,±7.5) 两孔与中央孔), 厚 2

⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / hub_shim_v4.scad) =====
HUB_BASE_OD = 165.0
DIAG_X      = 12.0
DIAG_Y      = 15.0
CENTER_D    = 6.2       # = hub_disc 底面中心盲窝直径
SQUARE_SIDE = 30.0      # hub pattern B (被垫片盖住)
INNER_PCD_R = 30.0      # hub pattern C (被垫片盖住)
OUTER_PCD_R = 77.5      # hub pattern D (在垫片外)
CB_B_DIAM   = 4.2

THICK    = 2.0
OD       = 100.0
M3_DIAM  = 3.4

PATTERN_A = [( DIAG_X/2, 0.0), (-DIAG_X/2, 0.0),
             ( 0.0,  DIAG_Y/2), ( 0.0, -DIAG_Y/2)]

R_OD = OD / 2
R_C  = CENTER_D / 2

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
DIM_O3 = 38.0

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
_GLYPH_FIX = {"−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ"}
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

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D 转子侧垫片  Hub Shim v4", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"Φ{OD:g} × {THICK:g} 圆片 / 中央 Φ{CENTER_D:g} 通孔 / "
     f"4×Φ{M3_DIAM:g} 菱形通孔 对角 {DIAG_X:g}×{DIAG_Y:g} / "
     f"垫在电机 bell top 与 hub_disc 底面之间",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (1:1) =====
S = 1.0
ccx, ccy = 112, 150
def tv(x, y): return (ccx + x * S, ccy - y * S)

text(ccx, 40, "俯视图  Top View  (1:1)   尺寸单位: mm", size=TXT_L, anchor="middle")

_w(GEOM_W)
pdf.circle(ccx, ccy, R_OD * S, style="D")
pdf.circle(ccx, ccy, R_C  * S, style="D")
for (hx, hy) in PATTERN_A:
    px, py = tv(hx, hy)
    pdf.circle(px, py, M3_DIAM / 2 * S, style="D")

# 中心十字
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(*tv(-R_OD - 6, 0), *tv(R_OD + 6, 0))
pdf.line(*tv(0, -R_OD - 6), *tv(0, R_OD + 6))
pdf.set_dash_pattern()

# 详图 A 的范围圈
_w(0.25)
pdf.set_dash_pattern(dash=2, gap=1.5)
pdf.circle(ccx, ccy, 13 * S, style="D")
pdf.set_dash_pattern()
_lax, _lay = tv(9.2, 9.2)
_lbx, _lby = tv(30, 30)
_w(EXT_W); pdf.line(_lax, _lay, _lbx, _lby); pdf.line(_lbx, _lby, _lbx + 8, _lby)
text(_lbx + 9, _lby - 1.2, "详图 A (4:1)", size=TXT_D)

# 剖切线 B-B —— 沿 Y 轴 (过 (0,±7.5) 两孔与中央孔)
pdf.set_dash_pattern(dash=6, gap=1.5); _w(0.3)
pdf.line(*tv(0, -R_OD - 4), *tv(0, R_OD + 4))
pdf.set_dash_pattern()
_w(DIM_W)
text(*tv(-3.5, R_OD + 8), "B", size=TXT_L, anchor="middle")
text(*tv(-3.5, -R_OD - 5), "B", size=TXT_L, anchor="middle")

# ---- 俯视尺寸 ----
hdim(tv(-R_OD, 0)[0], tv(R_OD, 0)[0], tv(0, R_OD)[1], tv(0, R_OD)[1] - DIM_O1,
     f"Φ{OD:g}")

# ===== DETAIL A (4:1) — 中央孔组 =====
DS = 4.0
dax, day = 300, 108
def da(x, y): return (dax + x * DS, day - y * DS)

text(dax, 55, "详图 A  Detail A  (4:1)   中央孔组   尺寸单位: mm",
     size=TXT_L, anchor="middle")

_w(GEOM_W)
pdf.circle(dax, day, R_C * DS, style="D")
for (hx, hy) in PATTERN_A:
    px, py = da(hx, hy)
    pdf.circle(px, py, M3_DIAM / 2 * DS, style="D")
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
    pdf.line(px - 7, py, px + 7, py); pdf.line(px, py - 7, px, py + 7)
    pdf.set_dash_pattern(); _w(GEOM_W)

# 菱形连线 (示意)
pdf.set_dash_pattern(dash=2, gap=1); _w(0.15)
_pts = [da(*PATTERN_A[0]), da(*PATTERN_A[2]), da(*PATTERN_A[1]), da(*PATTERN_A[3])]
for k in range(4):
    pdf.line(*_pts[k], *_pts[(k + 1) % 4])
pdf.set_dash_pattern(); _w(GEOM_W)

# 详图尺寸: 对角 X / 对角 Y / 中央 Φ / 孔 Φ
hdim(da(-DIAG_X/2, 0)[0], da(DIAG_X/2, 0)[0],
     da(0, DIAG_Y/2)[1], da(0, DIAG_Y/2)[1] - DIM_O1, f"{DIAG_X:g}")
vdim(da(0, DIAG_Y/2)[1], da(0, -DIAG_Y/2)[1],
     da(DIAG_X/2, 0)[0], da(DIAG_X/2, 0)[0] + DIM_O2, f"{DIAG_Y:g}")
hdim(da(-R_C, 0)[0], da(R_C, 0)[0],
     da(0, -DIAG_Y/2)[1], da(0, -DIAG_Y/2)[1] + DIM_O1, f"Φ{CENTER_D:g}")

_hx, _hy = da(-DIAG_X/2, 0)
_lx, _ly = da(-DIAG_X/2 - 7, 7)
_w(EXT_W); pdf.line(_hx, _hy, _lx, _ly); pdf.line(_lx, _ly, _lx - 6, _ly)
text(_lx - 7, _ly - 1.2, f"4 × Φ{M3_DIAM:g} 通孔", size=TXT_D, anchor="end")

# ===== SECTION B-B (4:1, 局部) =====
SB = 4.0
sbx, sby = 300, 202
T_HALF = 12.0
def sb(t, z): return (sbx + t * SB, sby - z * SB)

text(sbx, 162, "剖视图  Section B-B  (4:1, 局部)   尺寸单位: mm",
     size=TXT_L, anchor="middle")
text(sbx, 169, "(沿 Y 轴剖切, 过 (0,±7.5) 两孔与中央孔; 两端为局部截断)",
     size=TXT_I, anchor="middle")

_w(GEOM_W)
# 孔在 t = ±DIAG_Y/2 (Φ3.4), 中央孔 t = ±R_C
_gaps = sorted([(-DIAG_Y/2 - M3_DIAM/2, -DIAG_Y/2 + M3_DIAM/2),
                (-R_C, R_C),
                ( DIAG_Y/2 - M3_DIAM/2,  DIAG_Y/2 + M3_DIAM/2)])
_edges = [-T_HALF]
for gl, gr in _gaps:
    _edges += [gl, gr]
_edges.append(T_HALF)
for i in range(0, len(_edges), 2):
    t0, t1 = _edges[i], _edges[i + 1]
    line(*sb(t0, 0),     *sb(t1, 0),     GEOM_W)
    line(*sb(t0, THICK), *sb(t1, THICK), GEOM_W)
for gl, gr in _gaps:
    line(*sb(gl, 0), *sb(gl, THICK), GEOM_W)
    line(*sb(gr, 0), *sb(gr, THICK), GEOM_W)
# 两端截断竖线
line(*sb(-T_HALF, 0), *sb(-T_HALF, THICK), GEOM_W)
line(*sb( T_HALF, 0), *sb( T_HALF, THICK), GEOM_W)

pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(*sb(0, -3), *sb(0, THICK + 3))
pdf.set_dash_pattern()

vdim(sb(0, THICK)[1], sb(0, 0)[1], sb(T_HALF, 0)[0], sb(T_HALF, 0)[0] + DIM_O1,
     f"{THICK:g}")
hdim(sb(-DIAG_Y/2, 0)[0], sb(DIAG_Y/2, 0)[0],
     sb(0, THICK)[1], sb(0, THICK)[1] - DIM_O1, f"{DIAG_Y:g}")
hdim(sb(-R_C, 0)[0], sb(R_C, 0)[0], sb(0, 0)[1], sb(0, 0)[1] + DIM_O1,
     f"Φ{CENTER_D:g}")

# ===== 说明 (两栏, 避开 y=265 的标题栏) =====
NY = 224
_r_b = math.hypot(SQUARE_SIDE/2, SQUARE_SIDE/2) + CB_B_DIAM/2
_r_c = INNER_PCD_R + CB_B_DIAM/2
_r_d = OUTER_PCD_R + CB_B_DIAM/2
text(22, NY, "说明 / Notes", size=TXT_L)
_col_L = [
    "1) 用途: 垫在 C4110 电机 bell top 与 hub_disc 底面之间",
    "   (v4 装配里 hub_disc 正放贴电机), 是 motor_shim_v4 的转子侧对应件。",
    "2) 5 个孔 = 4×Φ%g 菱形过孔 (对角 %g×%g, 对 bell top 4 孔菱形)" % (M3_DIAM, DIAG_X, DIAG_Y),
    "   + 中央 Φ%g 通孔 (对 hub_disc 底面 Φ%g×2.2 中心盲窝)。" % (CENTER_D, CENTER_D),
    "3) 4×Φ%g 比 hub_disc 的 Φ3.2 放大 0.2; bell 固定螺丝需加长 %g。" % (M3_DIAM, THICK),
    "4) 打印: 平放, 底面贴床, 零支撑; 建议 >=4 层实心。",
]
_col_R = [
    "※ Φ%g 会盖住 hub_disc 底面另外 12 个孔:" % OD,
    "   pattern B 方形 30×30 的 4 孔 (沉孔外缘 R%.2f)" % _r_b,
    "   pattern C 内 PCD Φ60 的 8 孔 (沉孔外缘 R%.2f)。" % _r_c,
    "   pattern D 外 PCD Φ155 (R%.2f) 在垫片外, 不受影响。" % _r_d,
    "   这 12 颗若仍需装配, 本件须另开让位孔或缩到 Φ38 以内。",
    "※ 转子组再上移 %g, 增重约 19 g (对称, 不引入不平衡)。" % THICK,
]
for i2, t2 in enumerate(_col_L):
    text(22, NY + 7 + i2 * 5.0, t2, size=4.6)
for i2, t2 in enumerate(_col_R):
    text(215, NY + 7 + i2 * 5.0, t2, size=4.6)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — 转子侧垫片 (Hub Shim)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 1:1 (俯) / 4:1 (详 A, 剖 B-B)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{OD:g}×{THICK:g} / 中央 Φ{CENTER_D:g} / 4×Φ{M3_DIAM:g} 菱形 {DIAG_X:g}×{DIAG_Y:g}"
     f" / 材料 PLA  /  单位 mm", size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-03  /  POV3D / v4 / hub_shim_v4 / hub_shim_v4.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("hub_shim_v4_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
