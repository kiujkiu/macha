"""
A3 landscape 2D engineering drawing for POV3D washer_m3_6p8x1p5.

  1) TOP VIEW (10:1)    — 外圆 Φ6.8, 中央 Φ3.3 通孔
  2) SECTION A-A (10:1) — 过中心剖, 厚 1.5

件很小 (Φ6.8), 所以两个视图都放到 10:1。
全部是通孔, 没有沉孔/盲孔/让位窝 → 按项目规则不需要放大详图。

⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / washer_m3_6p8x1p5.scad) =====
OD    = 6.8
ID    = 3.3
THICK = 1.5
WALL  = (OD - ID) / 2      # 1.75

R_OD = OD / 2
R_ID = ID / 2

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

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D 平垫圈  Washer M3  Φ6.8 × 1.5", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"圆环片 外圆 Φ{OD:g} / 内孔 Φ{ID:g} (M3 过孔) / 厚 {THICK:g} / 环宽 (单边) {WALL:g}",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (10:1) =====
S = 10.0
ccx, ccy = 130, 150
def tv(x, y): return (ccx + x * S, ccy - y * S)

text(ccx, 45, "俯视图  Top View  (10:1)   尺寸单位: mm", size=TXT_L, anchor="middle")

_w(GEOM_W)
pdf.circle(ccx, ccy, R_OD * S, style="D")     # 外圆
pdf.circle(ccx, ccy, R_ID * S, style="D")     # 内孔

# 中心十字
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(*tv(-R_OD - 0.9, 0), *tv(R_OD + 0.9, 0))
pdf.line(*tv(0, -R_OD - 0.9), *tv(0, R_OD + 0.9))
pdf.set_dash_pattern()

# 剖切线 A-A (沿 X 轴)
_e = R_OD + 1.4
pdf.set_dash_pattern(dash=6, gap=1.5); _w(0.3)
pdf.line(*tv(-_e, 0), *tv(_e, 0))
pdf.set_dash_pattern()
_w(DIM_W)
text(*tv(-(R_OD + 2.2), -0.25), "A", size=TXT_L, anchor="middle")
text(*tv( (R_OD + 2.2), -0.25), "A", size=TXT_L, anchor="middle")

# ---- 俯视尺寸: 外圆在上, 内孔在下 ----
hdim(tv(-R_OD, 0)[0], tv(R_OD, 0)[0], tv(0, R_OD)[1], tv(0, R_OD)[1] - DIM_O1,
     f"Φ{OD:g}")
hdim(tv(-R_ID, 0)[0], tv(R_ID, 0)[0], tv(0, -R_OD)[1], tv(0, -R_OD)[1] + DIM_O1,
     f"Φ{ID:g}")

# 环宽引注 (45° 方向引出到右上)
_a45 = math.radians(45)
ax0, ay0 = tv((R_ID + R_OD) / 2 * math.cos(_a45),
              (R_ID + R_OD) / 2 * math.sin(_a45))
lx, ly = ccx + (R_OD + 2.0) * S * math.cos(_a45), ccy - (R_OD + 2.0) * S * math.sin(_a45)
_w(DIM_W)
pdf.line(ax0, ay0, lx, ly); pdf.line(lx, ly, lx + 10, ly)
text(lx + 11, ly - 1.0, f"环宽 (单边) {WALL:g} mm", size=TXT_D)

# ===== SECTION A-A (10:1) =====
SA = 10.0
sax, say = 305, 152
def sa(t, z): return (sax + t * SA, say - z * SA)

text(sax, 45, "剖视图  Section A-A  (10:1)   尺寸单位: mm", size=TXT_L, anchor="middle")
text(sax, 52, "(过中心沿 A-A 剖切; 全部为通孔, 无沉孔/盲孔)",
     size=TXT_I, anchor="middle")

_w(GEOM_W)
# 剖面 = 两段矩形: [-R_OD..-R_ID] 与 [R_ID..R_OD]
for (a0, a1) in ((-R_OD, -R_ID), (R_ID, R_OD)):
    line(*sa(a0, 0),     *sa(a1, 0),     GEOM_W)      # 底面
    line(*sa(a0, THICK), *sa(a1, THICK), GEOM_W)      # 顶面
    line(*sa(a0, 0), *sa(a0, THICK), GEOM_W)          # 左壁
    line(*sa(a1, 0), *sa(a1, THICK), GEOM_W)          # 右壁

# 剖面线 (45° 影线)
_w(0.15)
_hstep = 2.2
for (a0, a1) in ((-R_OD, -R_ID), (R_ID, R_OD)):
    x0p, x1p = sa(a0, 0)[0], sa(a1, 0)[0]
    ytop, ybot = sa(0, THICK)[1], sa(0, 0)[1]
    h = ybot - ytop
    c = x0p - h
    while c <= x1p:
        # 线段 (c, ybot) -> (c + h, ytop), 裁到矩形内
        p0x, p0y = c, ybot
        p1x, p1y = c + h, ytop
        if p0x < x0p:
            t = (x0p - p0x) / (p1x - p0x); p0x, p0y = x0p, ybot + t * (ytop - ybot)
        if p1x > x1p:
            t = (x1p - p0x) / (p1x - p0x); p1x, p1y = x1p, p0y + t * (p1y - p0y)
        if p1x > p0x:
            pdf.line(p0x, p0y, p1x, p1y)
        c += _hstep

# 中心线
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(*sa(0, -0.5), *sa(0, THICK + 0.5))
pdf.set_dash_pattern()

# ---- 剖视尺寸 ----
vdim(sa(0, THICK)[1], sa(0, 0)[1], sa(R_OD, 0)[0], sa(R_OD, 0)[0] + DIM_O1, f"{THICK:g}")
hdim(sa(-R_OD, 0)[0], sa(R_OD, 0)[0], sa(0, THICK)[1], sa(0, THICK)[1] - DIM_O1,
     f"Φ{OD:g}")
hdim(sa(-R_ID, 0)[0], sa(R_ID, 0)[0], sa(0, 0)[1], sa(0, 0)[1] + DIM_O1,
     f"Φ{ID:g}")

# ===== 说明 =====
NX, NY = 25, 218
text(NX, NY, "说明 / Notes", size=TXT_L)
for i, s in enumerate([
    "1) 全部尺寸由用户 2026-09-07 直接指定: 外径 %g / 内径 %g / 厚 %g。" % (OD, ID, THICK),
    "2) 内孔 Φ%g 为 M3 螺杆过孔 (公称 3 + 0.3 间隙); 全通孔, 无沉孔/倒角要求。" % (ID,),
    "3) 参考标准件: GB/T 848 小垫圈 M3 = Φ6×0.5, GB/T 97.1 = Φ7×0.5 —— 本件为加厚非标, 用于补螺栓链厚度。",
    "4) 打印: 平放贴床, 零支撑; 件小, 建议 100%% 填充 + 一次多排几只。",
    "5) 单只体积 41.6 立方毫米, PLA 约 0.05 g。",
    "※ FDM 打小孔普遍偏小: 若装配偏紧, 用 Φ3.2 钻头过一刀, 或把 build_stl.py 的 ID 放到 3.4-3.5 重印。",
]):
    text(NX, NY + 7 + i * 5.2, s, size=4.8)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — 平垫圈 (Washer M3)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 10:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{OD:g} × {THICK:g} / 内孔 Φ{ID:g} / 材料 PLA  /  单位 mm", size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-07  /  POV3D / models / washer_m3_6p8x1p5 / washer_m3_6p8x1p5.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("washer_m3_6p8x1p5_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
