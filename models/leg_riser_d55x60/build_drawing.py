"""
A3 landscape 2D engineering drawing for leg_riser_d55x60 (地脚垫高圆筒).

  1) TOP VIEW (2:1)     — 外圆 Φ55, 米字加强筋 ×4 厚 5
  2) SECTION A-A (2:1)  — 沿 0° 筋中心剖: 高 60, 筋高 55, 顶部 5 无筋, 内径 Φ46, 壁厚 4.5

没有沉孔/盲孔/螺纹孔 → 按项目规则不需要放大详图。
剖视按 GB 惯例: 肋板纵向剖切不画剖面线, 用粗实线与筒壁分开。

⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF
from shapely.geometry import Point, box
from shapely.affinity import rotate as s_rotate
from shapely.ops import unary_union

# ===== Geometry (must match build_stl.py / leg_riser_d55x60.scad) =====
OD         = 55.0
ID         = 46.0
H          = 60.0
RIB_T      = 5.0
TOP_CLEAR  = 5.0
RIB_ANGLES = (0, 45, 90, 135)

R_OD, R_ID = OD / 2, ID / 2
WALL  = R_OD - R_ID        # 4.5
RIB_H = H - TOP_CLEAR      # 55

# 米字筋在内孔里的形状 (俯视轮廓 + 体积)
_strip = box(-R_OD, -RIB_T / 2, R_OD, RIB_T / 2)
_ribs  = unary_union([s_rotate(_strip, a, origin=(0, 0)) for a in RIB_ANGLES])
RIB_SHAPE = _ribs.intersection(Point(0, 0).buffer(R_ID, quad_segs=64))
_rib_area_exact = _ribs.intersection(Point(0, 0).buffer(R_ID, quad_segs=2048)).area
VOL = math.pi * (R_OD**2 - R_ID**2) * H + _rib_area_exact * RIB_H   # mm^3

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

def hdim(x1, x2, yg, yd, label, label_at="middle", outside=False):
    """label_at='right': 标注文字放到右侧尺寸界线外 (窄尺寸时用, 免得字压界线)。
    outside=True: 强制箭头放界线外 (间隙刚过阈值时两箭头仍会顶在一起)。"""
    label = _with_unit(label)
    if yd > yg: ey1, ey2 = yg + EXT_GP, yd + EXT_OV
    else:       ey1, ey2 = yg - EXT_GP, yd - EXT_OV
    line(x1, ey1, x1, ey2, EXT_W)
    line(x2, ey1, x2, ey2, EXT_W)
    x_l, x_r = (x1, x2) if x1 < x2 else (x2, x1)
    if x_r - x_l >= 2 * ARR_L + 1 and not outside:
        line(x_l, yd, x_r, yd, DIM_W)
        arrow(x_l, yd, -1, 0); arrow(x_r, yd, 1, 0)
        ext_r = x_r
    else:
        ext = ARR_L + 1.0
        line(x_l - ext, yd, x_r + ext, yd, DIM_W)
        arrow(x_l, yd,  1, 0); arrow(x_r, yd, -1, 0)
        ext_r = x_r + ext
    if label_at == "right":
        line(x_r, yd, ext_r + 3.0, yd, DIM_W)
        text(ext_r + 4.0, yd + 1.8, label)
    else:
        text((x_l + x_r) / 2, yd - 1.8, label, anchor="middle")

def vdim(y1, y2, xg, xd, label, outside=False):
    label = _with_unit(label)
    if xd > xg: ex1, ex2, to = xg+EXT_GP, xd+EXT_OV,  4.0
    else:       ex1, ex2, to = xg-EXT_GP, xd-EXT_OV, -4.0
    line(ex1, y1, ex2, y1, EXT_W)
    line(ex1, y2, ex2, y2, EXT_W)
    y_top, y_bot = (y1, y2) if y1 < y2 else (y2, y1)
    gap = y_bot - y_top
    if gap >= 2 * ARR_L + 1 and not outside:
        line(xd, y_top, xd, y_bot, DIM_W)
        arrow(xd, y_top, 0, -1); arrow(xd, y_bot, 0, 1)
    else:
        ext = ARR_L + 1.0
        line(xd, y_top - ext, xd, y_bot + ext, DIM_W)
        arrow(xd, y_top, 0,  1); arrow(xd, y_bot, 0, -1)
    pdf.set_font("SimHei", "", TXT_D)
    lh = pdf.get_string_width(_g(label))
    if gap >= lh + 1.0:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        rot_text(xd + to, y_top - (ARR_L + 1.0) - lh / 2 - 1.0,
                 label, angle_deg=90, anchor="middle")

def hatch_rect(x0, y0, x1, y1, step=2.2):
    """45° 剖面线, 裁到纸面矩形 [x0,x1]×[y0,y1] (y0<y1) 内。"""
    _w(0.15)
    c = x0 - (y1 - y0)
    while c <= x1:
        # 直线 x - c = (y1 - y) : 从 (c, y1) 往右上到 (c + h, y0)
        pts = []
        for (px, py) in ((c, y1), (c + (y1 - y0), y0)):
            pts.append((px, py))
        (ax, ay), (bx, by) = pts
        if ax < x0:
            t = (x0 - ax) / (bx - ax); ax, ay = x0, ay + t * (by - ay)
        if bx > x1:
            t = (x1 - ax) / (bx - ax); bx, by = x1, ay + t * (by - ay)
        if bx > ax:
            pdf.line(ax, ay, bx, by)
        c += step

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "地脚垫高圆筒  leg_riser_d55x60   Φ55 × 60", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"圆筒 外径 Φ{OD:g} / 内径 Φ{ID:g} / 高 {H:g} (壁厚 {WALL:g})  ·  内部米字加强筋厚 {RIB_T:g}, "
     f"筋高 {RIB_H:g}, 最上面 {TOP_CLEAR:g} 不做加强",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (2:1) =====
S = 2.0
ccx, ccy = 100, 135
def tv(x, y): return (ccx + x * S, ccy - y * S)

text(ccx, 33, "俯视图  Top View  (2:1)   尺寸单位: mm", size=TXT_L, anchor="middle")

_w(GEOM_W)
pdf.circle(ccx, ccy, R_OD * S, style="D")     # 外圆
pdf.circle(ccx, ccy, R_ID * S, style="D")     # 内孔
# 米字筋顶面轮廓 (Z=55, 从上面看得见)
_coords = list(RIB_SHAPE.exterior.coords)
for (x0, y0), (x1, y1) in zip(_coords[:-1], _coords[1:]):
    pdf.line(*tv(x0, y0), *tv(x1, y1))

# 中心线
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(*tv(-R_OD - 4, 0), *tv(R_OD + 4, 0))
pdf.line(*tv(0, -R_OD - 4), *tv(0, R_OD + 4))
pdf.set_dash_pattern()

# 剖切符号 A-A (沿 0° 筋中心 = X 轴): 只画外圆外两端的粗短划
_w(0.6)
pdf.line(*tv(-R_OD - 6.5, 0), *tv(-R_OD - 1.5, 0))
pdf.line(*tv( R_OD + 1.5, 0), *tv( R_OD + 6.5, 0))
text(*tv(-(R_OD + 4.0), -3.2), "A", size=TXT_L, anchor="middle")
text(*tv( (R_OD + 4.0), -3.2), "A", size=TXT_L, anchor="middle")

# ---- 俯视尺寸 ----
hdim(tv(-R_OD, 0)[0], tv(R_OD, 0)[0], tv(0, R_OD)[1], tv(0, R_OD)[1] - DIM_O1,
     f"Φ{OD:g}")
# 90° 筋的厚度: 界线从筋边与内孔的交点往下引
_yi = -math.sqrt(R_ID**2 - (RIB_T / 2)**2)
hdim(tv(-RIB_T / 2, 0)[0], tv(RIB_T / 2, 0)[0], tv(0, _yi)[1], tv(0, -R_OD)[1] + DIM_O1,
     f"筋厚 {RIB_T:g}", label_at="right", outside=True)

# 米字筋引注 (从 45° 筋引到右上)
_a45 = math.radians(45)
ax0, ay0 = tv(12 * math.cos(_a45), 12 * math.sin(_a45))
lx, ly = tv((R_OD + 8) * math.cos(_a45), (R_OD + 8) * math.sin(_a45))
_w(DIM_W)
pdf.line(ax0, ay0, lx, ly); pdf.line(lx, ly, lx + 10, ly)
pdf.set_fill_color(0, 0, 0); pdf.circle(ax0, ay0, 0.7, style="F")
text(lx + 11, ly + 1.0, f"米字加强筋 ×4", size=TXT_D)
text(lx + 11, ly + 7.0, f"厚 {RIB_T:g} mm, 0°/45°/90°/135°", size=TXT_I)

# ===== SECTION A-A (2:1) =====
SA = 2.0
sax, say = 290, 192
def sa(t, z): return (sax + t * SA, say - z * SA)

text(sax, 33, "剖视图  Section A-A  (2:1)   尺寸单位: mm", size=TXT_L, anchor="middle")
text(sax, 39.5, "(沿 0° 筋中心剖切; 按 GB 惯例肋纵剖不画剖面线, 粗实线与筒壁分开)",
     size=TXT_I, anchor="middle")

# 筒壁剖面 (两侧) 剖面线
for (a0, a1) in ((-R_OD, -R_ID), (R_ID, R_OD)):
    hatch_rect(sa(a0, 0)[0], sa(0, H)[1], sa(a1, 0)[0], sa(0, 0)[1])

_w(GEOM_W)
for (a0, a1) in ((-R_OD, -R_ID), (R_ID, R_OD)):
    line(*sa(a0, H), *sa(a1, H), GEOM_W)              # 壁顶
    line(*sa(a0, 0), *sa(a0, H), GEOM_W)              # 壁外/内侧线
    line(*sa(a1, 0), *sa(a1, H), GEOM_W)
line(*sa(-R_OD, 0), *sa(R_OD, 0), GEOM_W)             # 底面 (壁 + 筋)
line(*sa(-R_ID, RIB_H), *sa(R_ID, RIB_H), GEOM_W)     # 筋顶 Z=55

# 中心线
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(*sa(0, -3), *sa(0, H + 3))
pdf.set_dash_pattern()

# 区域说明
text(sa(-R_ID, 0)[0] + 3, sa(0, H - TOP_CLEAR / 2)[1] + 0.9,
     f"顶部 {TOP_CLEAR:g} mm 不做加强", size=4.8)
text(sa(-R_ID / 2, 0)[0], sa(0, RIB_H / 2)[1] - 2.5, "米字加强筋", size=TXT_D, anchor="middle")
text(sa(-R_ID / 2, 0)[0], sa(0, RIB_H / 2)[1] + 3.5, f"(厚 {RIB_T:g}, 纵剖)", size=4.8, anchor="middle")

# ---- 剖视尺寸 ----
# 左侧链: 筋高 55 + 顶部无筋 5 (界线从内壁引出)
_xg_in = sa(-R_ID, 0)[0]
_xd_l  = sa(-R_OD, 0)[0] - DIM_O1
vdim(sa(0, RIB_H)[1], sa(0, 0)[1], _xg_in, _xd_l, f"{RIB_H:g}")
vdim(sa(0, H)[1], sa(0, RIB_H)[1], _xg_in, _xd_l, f"{TOP_CLEAR:g}", outside=True)  # Z55 处箭头与 55 段重合
# 右侧: 总高 60
vdim(sa(0, H)[1], sa(0, 0)[1], sa(R_OD, 0)[0], sa(R_OD, 0)[0] + DIM_O1, f"{H:g}")
# 上: 外径 + 右壁厚
hdim(sa(-R_OD, 0)[0], sa(R_OD, 0)[0], sa(0, H)[1], sa(0, H)[1] - DIM_O2, f"Φ{OD:g}")
hdim(sa(R_ID, 0)[0], sa(R_OD, 0)[0], sa(0, H)[1], sa(0, H)[1] - DIM_O1, f"{WALL:g}")
# 下: 内径
hdim(sa(-R_ID, 0)[0], sa(R_ID, 0)[0], sa(0, 0)[1], sa(0, 0)[1] + DIM_O1, f"Φ{ID:g}")

# ===== 说明 =====
NX, NY = 25, 222
text(NX, NY, "说明 / Notes", size=TXT_L)
for i, s in enumerate([
    f"1) 尺寸由用户 2026-09-14 直接指定: 外径 Φ{OD:g} / 内径 Φ{ID:g} / 高 {H:g} / 米字加强筋厚 {RIB_T:g} / 最上面 {TOP_CLEAR:g} 不做加强。",
    f"2) 壁厚 {WALL:g}; 4 根筋过中心交成米字 (0°/45°/90°/135°), 从底面做到 Z={RIB_H:g}, 两端并入筒壁。",
    "3) 打印: 有筋那头 (底面) 贴床, 筋与筒壁全部竖直, 无悬空, 零支撑。",
    f"4) 实心体积 {VOL/1000:.1f} cm^3, PLA 实心约 {VOL*1.24e-3:.0f} g (实际随墙数/填充率下降)。",
    "5) 垫高受压件: 建议 4 圈以上墙 + 30% 以上填充; 层纹与载荷方向垂直, 受压可靠, 侧向磕碰是弱项。",
]):
    text(NX, NY + 7 + i * 5.6, s, size=4.8)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "结构件 — 地脚垫高圆筒 (Leg Riser)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 2:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{OD:g}/Φ{ID:g} × {H:g} / 米字筋厚 {RIB_T:g} / 顶部 {TOP_CLEAR:g} 无筋 / 材料 PLA/PETG  /  单位 mm",
     size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-14  /  pov3d / models / leg_riser_d55x60 / leg_riser_d55x60.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("leg_riser_d55x60_drawing.pdf")
try:
    pdf.output(str(out))
except PermissionError:                     # PDF 在阅读器里开着
    out = out.with_suffix(".NEW.pdf")
    pdf.output(str(out))
print(f"wrote {out}")
