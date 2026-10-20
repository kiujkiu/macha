"""
A3 landscape 2D engineering drawing for POV3D motor_shim_v4.

  1) TOP VIEW (2:1)   — 外圆 Φ54, 中央 Φ12, 4 × Φ3.4 @ 对角 25
  2) SECTION A-A (4:1)— 沿 +X 剖, 过中央孔与一对电机孔 (厚 2)

⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / motor_shim_v4.scad) =====
BOSS_ID    = 55.0
M3_ROT     = 0.0
M3_DIAG    = 25.0
CENTER_D   = 12.0

THICK      = 2.0
OD         = 54.0                       # 2026-09-03 用户指定
CLEAR_RAD  = (BOSS_ID - OD) / 2         # 派生: 0.5
M3_DIAM    = 3.4

M3_SIDE    = M3_DIAG / math.sqrt(2)     # 17.6777
M3_OFF     = M3_SIDE / 2                # 8.8388

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
text(PAGE_W/2, 14, "POV 3D 电机垫片  Motor Shim v4", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"Φ{OD:g} × {THICK:g} 圆片 / 中央 Φ{CENTER_D:g} 通孔 / "
     f"4×Φ{M3_DIAM:g} 通孔 对角 {M3_DIAG:g} (方形节距 {M3_SIDE:.2f}) / "
     f"落 baseplate_collar_v4 凸台内孔 Φ{BOSS_ID:g} (单边隙 {CLEAR_RAD:g})",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (2:1) =====
S = 2.0
ccx, ccy = 130, 145
def tv(x, y): return (ccx + x * S, ccy - y * S)

text(ccx, 40, "俯视图  Top View  (2:1)   尺寸单位: mm", size=TXT_L, anchor="middle")

_w(GEOM_W)
pdf.circle(ccx, ccy, R_OD * S, style="D")     # 外圆
pdf.circle(ccx, ccy, R_C  * S, style="D")     # 中央孔

# 4 × Φ3.4
holes = []
for sx in (-1, 1):
    for sy in (-1, 1):
        x0, y0 = sx * M3_OFF, sy * M3_OFF
        a = math.radians(M3_ROT)
        hx = x0 * math.cos(a) - y0 * math.sin(a)
        hy = x0 * math.sin(a) + y0 * math.cos(a)
        holes.append((hx, hy))
        px, py = tv(hx, hy)
        pdf.circle(px, py, M3_DIAM / 2 * S, style="D")
        pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.12)
        pdf.line(px - 6, py, px + 6, py); pdf.line(px, py - 6, px, py + 6)
        pdf.set_dash_pattern(); _w(GEOM_W)

# 中心十字
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(*tv(-R_OD - 5, 0), *tv(R_OD + 5, 0))
pdf.line(*tv(0, -R_OD - 5), *tv(0, R_OD + 5))
pdf.set_dash_pattern()

# 剖切线 A-A —— 沿 45° 对角线 (孔在 (±8.84,±8.84), 只有对角线才过孔;
# 沿坐标轴剖是过不到电机孔的)
_c45 = math.cos(math.radians(45))
_e = R_OD + 5
pdf.set_dash_pattern(dash=6, gap=1.5); _w(0.3)
pdf.line(*tv(-_e*_c45, -_e*_c45), *tv(_e*_c45, _e*_c45))
pdf.set_dash_pattern()
_w(DIM_W)
_a = (R_OD + 9) * _c45
text(*tv(-_a, -_a + 0.6), "A", size=TXT_L, anchor="middle")
text(*tv( _a,  _a + 0.6), "A", size=TXT_L, anchor="middle")

# ---- 俯视尺寸 ----
hdim(tv(-R_OD, 0)[0], tv(R_OD, 0)[0], tv(0, R_OD)[1], tv(0, R_OD)[1] - DIM_O1,
     f"Φ{OD:g}")
hdim(tv(-R_C, 0)[0], tv(R_C, 0)[0], tv(0, -R_OD)[1], tv(0, -R_OD)[1] + DIM_O1,
     f"Φ{CENTER_D:g}")
# 方形节距 (只在左侧标一次, 底部不重复)
vdim(tv(0, M3_OFF)[1], tv(0, -M3_OFF)[1],
     tv(-R_OD, 0)[0], tv(-R_OD, 0)[0] - DIM_O1, f"{M3_SIDE:.2f}")

# 孔组引注
hx0, hy0 = tv(M3_OFF, M3_OFF)
lx, ly = tv(R_OD + 6, R_OD - 6)
pdf.line(hx0, hy0, lx, ly); pdf.line(lx, ly, lx + 8, ly)
text(lx + 9, ly - 1.2, f"4 × Φ{M3_DIAM:g} 通孔, 对角 {M3_DIAG:g}", size=TXT_D)
text(lx + 9, ly + 4.2, "(对底盘 4×M3 电机孔)", size=TXT_D)

# 中央孔引注
cx0, cy0 = tv(-R_C * 0.71, R_C * 0.71)
lx2, ly2 = tv(-R_OD - 6, R_OD - 2)
pdf.line(cx0, cy0, lx2, ly2); pdf.line(lx2, ly2, lx2 - 8, ly2)
text(lx2 - 9, ly2 - 1.2, f"中央 Φ{CENTER_D:g} 通孔", size=TXT_D, anchor="end")
text(lx2 - 9, ly2 + 4.2, "(对底盘 Φ12×1 中央沉孔)", size=TXT_D, anchor="end")

# ===== SECTION A-A (4:1) =====
SA = 2.0
sax, say = 300, 150
def sa(t, z): return (sax + t * SA, say - z * SA)

text(sax, 40, "剖视图  Section A-A  (2:1)   尺寸单位: mm", size=TXT_L, anchor="middle")
text(sax, 47, "(沿 45° 对角线 A-A 剖切, 过中央孔与一对对角电机孔)",
     size=TXT_I, anchor="middle")

_w(GEOM_W)
# 剖面 = 两段实体: [-R_OD..-R_C] 和 [R_C..R_OD], 各被一个 Φ3.4 孔断开
seg = [(-R_OD, -R_C), (R_C, R_OD)]
hole_t = [-M3_DIAG/2, M3_DIAG/2]   # 对角线上孔心半径 = 对角/2 = 12.5
for (a0, a1) in seg:
    gaps = [(t - M3_DIAM/2, t + M3_DIAM/2) for t in hole_t if a0 < t < a1]
    edges = [a0]
    for gl, gr in sorted(gaps):
        edges += [gl, gr]
    edges.append(a1)
    for i in range(0, len(edges), 2):
        t0, t1 = edges[i], edges[i+1]
        line(*sa(t0, 0),     *sa(t1, 0),     GEOM_W)   # 底面
        line(*sa(t0, THICK), *sa(t1, THICK), GEOM_W)   # 顶面
    # 两端竖壁
    line(*sa(a0, 0), *sa(a0, THICK), GEOM_W)
    line(*sa(a1, 0), *sa(a1, THICK), GEOM_W)
    # 孔壁
    for gl, gr in gaps:
        line(*sa(gl, 0), *sa(gl, THICK), GEOM_W)
        line(*sa(gr, 0), *sa(gr, THICK), GEOM_W)

# 中心线
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(*sa(0, -3), *sa(0, THICK + 3))
pdf.set_dash_pattern()

# ---- 剖视尺寸 ----
vdim(sa(0, THICK)[1], sa(0, 0)[1], sa(R_OD, 0)[0], sa(R_OD, 0)[0] + DIM_O1, f"{THICK:g}")
hdim(sa(-R_OD, 0)[0], sa(R_OD, 0)[0], sa(0, THICK)[1], sa(0, THICK)[1] - DIM_O1,
     f"Φ{OD:g}")
hdim(sa(-R_C, 0)[0], sa(R_C, 0)[0], sa(0, THICK)[1], sa(0, THICK)[1] - DIM_O2,
     f"Φ{CENTER_D:g}")
hdim(sa(-M3_DIAG/2, 0)[0], sa(M3_DIAG/2, 0)[0], sa(0, 0)[1], sa(0, 0)[1] + DIM_O1,
     f"{M3_DIAG:g}")

# ===== 说明 =====
NX, NY = 25, 222
text(NX, NY, "说明 / Notes", size=TXT_L)
for i, s in enumerate([
    "1) 用途: 垫在 baseplate_collar_v4 凸台内腔底面 (装配 Z=5) 与 C4110 电机之间, 把电机抬高 %g。" % THICK,
    "2) 外圆 Φ%g 落进凸台内孔 Φ%g, 单边隙 %g —— 靠外圆自定位, 无需另设定位特征。" % (OD, BOSS_ID, CLEAR_RAD),
    "3) 4×Φ%g 比底盘的 Φ3.2 放大 0.2, 散件好对位; 电机固定螺丝需相应加长 %g。" % (M3_DIAM, THICK),
    "4) 中央 Φ%g 与底盘顶面 Φ12×1 中央沉孔同径, 让位深度由 1 变为 %g。" % (CENTER_D, 1 + THICK),
    "5) 打印: 平放, 底面贴床, 零支撑; 建议 >=4 层实心 (2mm 件不要用稀疏填充)。",
    "※ 装机影响: 电机抬高 %g => 转子面 31.7->33.7, 转子及以上整组上移 %g。顶轴承/柱高固定," % (THICK, THICK),
    "   装前请确认中间轴与 688 的配合、屏幕上下位置仍在允许范围内。",
]):
    text(NX, NY + 7 + i * 5.2, s, size=4.8)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — 电机垫片 (Motor Shim)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 2:1 (俯, 剖)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{OD:g}×{THICK:g} / 中央 Φ{CENTER_D:g} / 4×Φ{M3_DIAM:g} 对角 {M3_DIAG:g}"
     f" / 材料 PLA  /  单位 mm", size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-03  /  POV3D / v4 / motor_shim_v4 / motor_shim_v4.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("motor_shim_v4_drawing.pdf")
pdf.output(str(out))
print(f"wrote {out}")
