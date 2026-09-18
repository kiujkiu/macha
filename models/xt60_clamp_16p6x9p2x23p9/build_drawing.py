"""
A3 landscape 2D engineering drawing for xt60_clamp_16p6x9p2x23p9 (XT60 电源接头压块 v4.10: 阶梯槽 = 接头名义尺寸, 间隙/过盈全 0, 件高 11 + 件 2 底板垫片, 朝向已按实物纠正).

  1) 主视图 Front (2.5:1)    沿 +Y 看 (从开口端): 平顶块 + 本体段窄槽口; 护套段宽槽在后面 (虚线); 堵头 U 口; 底板垫片 (灰)
  2) 左视图 全剖 (2.5:1)     沿对称面 X=0 剖, 沿 +X 看 (+Y 堵头在左): 阶梯槽顶 + 堵头; 灰线 = 本体(开口侧) + 护套(堵头侧) + 底板垫片
  3) 俯视图 Top   (2.5:1)    2×Φ6.5 @ 25, 外形 38×26.9, 孔心距开口面 12.5, 阶梯槽 / U 口 (虚线)
  4) 详图 A (5:1)            堵头 U 型出线口: 间距 7 / 口宽 2.5 / R1.25 / 圆心高 4.6 (针轴线) / 口顶高 5.85
  5) 详图 B (5:1)            槽台阶处 Z 向堆叠: 护套段槽顶 9.2 / 本体段槽顶 8.7 (从垫片底板顶面算) / 凸台 0.5 / 接头两段顶面贴合
  6) 件 2 底板垫片 (1:1)     38 × 26.9 × 2 + 凸台 15.4 × 11.9 × 0.5 + 止口四边高 2 (总高 4), 2×Φ6.5 同压块孔

v3 -> v4: 两段前后对调 (v3 把大截面护套放在开口端, 做反了)。v4 -> v4.1: 槽宽按用户 16.6 / 15.6 紧配。v4.2: 所有间隙 0 (台阶对齐, 垫片 = 本体底面)。v4.3: 高度过盈也 0 (槽顶 9.2 / 8.7)。v4.4: 件高 11 (用户指定), 槽顶厚 1.8 / 2.3。v4.5: 垫片改整块底板 (厚 2 + 凸台 0.5), M6 孔定位防掉。v4.6: U 口 Φ2.5 零余量, 圆心 4.6 中央出线。v4.7: 上下件嵌套 —— 止口 2×2 (左右+开口端) + 堵头处舌头与 U 口扣成整圆。v4.8: 嵌套面留 0.1 装配间隙。v4.9: 台阶高不留间隙, 组合外形平齐成长方体。v4.10: 取消舌头, 止口四边 (后边宽 3), 出线孔平底到后边框顶。
剖切面为对称面且左视图按投影关系配置 → 按 GB 省略剖切符号。
⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / xt60_clamp_16p6x9p2x23p9.scad) =====
BODY_W,   BODY_H   = 15.6, 8.2
SHEATH_W, SHEATH_H = 16.6, 9.2
BODY_L,   SHEATH_L = 11.9, 12.0
XT_L      = BODY_L + SHEATH_L
BODY_LIFT = (SHEATH_H - BODY_H) / 2
SIDE_CLR_S, SIDE_CLR_B = 0.0, 0.0
PRELOAD_S,  PRELOAD_B  = 0.0, 0.0
STEP_MARGIN = 0.0
BASE_T          = 2.0
RIM_W, RIM_H    = 2.0, 2.0
ASSY_CLR        = 0.1
SHIM_T          = BODY_LIFT
SHIM_CLR        = ASSY_CLR
SHIM_OPEN_INSET = 0.0
SHIM_BACK_GAP   = 0.0
HTOP        = 11.0     # 件高 (用户指定)
CAP_T       = 3.0
WIRE_D      = 2.5
WIRE_PITCH  = 7.0
WIRE_ZC     = SHEATH_H / 2
PITCH       = 25.0
HOLE_D      = 6.5
END         = 6.5
HOLE_Y_OPEN = 12.5
HEAD_D, HEAD_T = 12.5, 2.6
PLATE_T     = 13.0
M6_SHANK_D  = 6.0

CH_W_B = BODY_W + 2 * SIDE_CLR_B             # 15.6
CH_H_B = BODY_LIFT + BODY_H - PRELOAD_B      #  8.7
CH_W_S = SHEATH_W + 2 * SIDE_CLR_S           # 16.6
CH_H_S = SHEATH_H - PRELOAD_S                #  9.2
T_TOP  = HTOP - CH_H_S                       # 1.8
STACK_H = BASE_T + HTOP                     # 13
HX     = PITCH / 2
HALF_L = HX + END
L      = 2 * HALF_L                          # 38
Y_OPEN  = -XT_L / 2                          # -11.95
Y_XSTEP = Y_OPEN + BODY_L                    #  -0.05
Y_STEP  = Y_XSTEP - STEP_MARGIN              #  -0.05
Y_CAPI  =  XT_L / 2                          #  11.95
Y_END   = Y_CAPI + CAP_T                     #  14.95
DEPTH   = Y_END - Y_OPEN                     #  26.9
HOLE_Y  = Y_OPEN + HOLE_Y_OPEN               #   0.55
WEB_S     = HX - HOLE_D / 2 - CH_W_S / 2     # 0.95
WEB_B     = HX - HOLE_D / 2 - CH_W_B / 2     # 1.45
SHANK_GAP = HX - M6_SHANK_D / 2 - CH_W_S / 2 # 1.20
WIRE_X = (-WIRE_PITCH / 2, WIRE_PITCH / 2)
SHIM_W  = CH_W_B - 2 * SHIM_CLR              # 15.4
BACK_RIM_W = CAP_T                           # 3 后边止口宽
LEDGE = WIRE_ZC - WIRE_D / 2                 # 3.35 线底
SLOT_BOTTOM = min(RIM_H, LEDGE)              # 2 出线口平底
SHIM_Y0 = Y_OPEN + SHIM_OPEN_INSET           # -11.95
SHIM_Y1 = Y_XSTEP - SHIM_BACK_GAP            #  -0.05
SHIM_L  = SHIM_Y1 - SHIM_Y0                  #  11.9
U_AREA = WIRE_D * WIRE_ZC + math.pi * (WIRE_D / 2) ** 2 / 2
_RW, _RH = RIM_W + ASSY_CLR, RIM_H                # 压块台阶 (宽 +0.1, 高贴合)
RIM_VOL = ((2 * _RW * (DEPTH - BACK_RIM_W - ASSY_CLR) + 2 * (HALF_L - CH_W_B / 2 - _RW) * _RW) * _RH
           + ASSY_CLR * (L - CH_W_S) * RIM_H + BACK_RIM_W * (L * RIM_H - 2 * WIRE_D * SLOT_BOTTOM))
VOL = (L * DEPTH * HTOP - CH_W_B * (Y_STEP - Y_OPEN) * CH_H_B - CH_W_S * (Y_CAPI - Y_STEP) * CH_H_S
       - 2 * math.pi * (HOLE_D / 2) ** 2 * HTOP - 2 * U_AREA * CAP_T - RIM_VOL)

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
GRAY   = 125

def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W):
    _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L_ = math.hypot(dx, dy); ux, uy = dx/L_, dy/L_
    bx, by = tx - ARR_L*ux, ty - ARR_L*uy
    px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx + ARR_W*px, by + ARR_W*py),
                 (bx - ARR_W*px, by - ARR_W*py)], style="F")

# SimHei 缺这几个字形 (见 feedback_pdf_drawing_lessons): 落笔前统一替换
_GLYPH_FIX = {"↑": "^", "−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ", "³": "^3", "²": "^2"}
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
    """label_at='right': 标注文字放到右侧尺寸界线外。outside=True: 强制箭头放界线外。"""
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

def vdim(y1, y2, xg, xd, label, outside=False, xg2=None):
    """xg2: 第二条 (y2) 尺寸界线的起点, 默认同 xg。"""
    label = _with_unit(label)
    xg2 = xg if xg2 is None else xg2
    gp = EXT_GP if xd > xg else -EXT_GP
    if xd > xg: ex2, to = xd+EXT_OV,  4.0
    else:       ex2, to = xd-EXT_OV, -4.0
    line(xg + gp, y1, ex2, y1, EXT_W)
    line(xg2 + gp, y2, ex2, y2, EXT_W)
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

def polyline(pts, closed=True, w=GEOM_W):
    _w(w)
    seq = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(seq[:-1], seq[1:]):
        pdf.line(*a, *b)

def rect(p0, p1, w=GEOM_W):
    (x0, y0), (x1, y1) = p0, p1
    polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w=w)

def hatch_rect(p0, p1, step=1.6):
    """45° 剖面线, 裁到纸面矩形。线族 x + y = k·step 用全局相位, 相邻矩形拼接处线条对齐。"""
    (x0, y0), (x1, y1) = p0, p1
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    _w(0.15)
    for k in range(math.ceil((x0 + y0) / step), math.floor((x1 + y1) / step) + 1):
        c = k * step
        lo, hi = max(x0, c - y1), min(x1, c - y0)
        if hi - lo > 0.05:
            pdf.line(lo, c - lo, hi, c - hi)

def u_outline(xc, n=24, z0=0.0):
    """单个 U 口轮廓 (真实坐标 X, Z): 左直边底 (z0) -> 半圆顶 -> 右直边底。"""
    r = WIRE_D / 2
    pts = [(xc - r, z0), (xc - r, WIRE_ZC)]
    for i in range(1, n):
        a = math.pi - math.pi * i / n
        pts.append((xc + r * math.cos(a), WIRE_ZC + r * math.sin(a)))
    pts += [(xc + r, WIRE_ZC), (xc + r, z0)]
    return pts

def hidden():  pdf.set_draw_color(0); pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(0.30)
def center():  pdf.set_draw_color(0); pdf.set_dash_pattern(dash=5.0, gap=1.2); _w(0.15)
def phantom(): pdf.set_draw_color(GRAY); pdf.set_dash_pattern(dash=3.0, gap=1.2); _w(0.30)
def solid():   pdf.set_draw_color(0); pdf.set_dash_pattern()


# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "XT60 电源接头压块  xt60_clamp_16p6x9p2x23p9   (v4.10 压块 11 + 底板垫片 = 38×26.9×13 长方体, 止口四边, 中央出线 Φ2.5)", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"锁 XT60H-M (插合本体 {BODY_W:g}×{BODY_H:g}×{BODY_L:g} 在开口端 + 出线护套 {SHEATH_W:g}×{SHEATH_H:g}×{SHEATH_L:g} 在堵头端) 到 M6 网格板  ·  "
     f"外形 {L:g}×{DEPTH:g}×{HTOP:g}  ·  阶梯槽 {CH_W_B:g}×{CH_H_B:g} / {CH_W_S:g}×{CH_H_S:g}  ·  件2 底板垫片 {L:g}×{DEPTH:g}×{BASE_T:g} + 凸台 {SHIM_T:g} + 止口四边高 {RIM_H:g} (总高 {BASE_T+RIM_H:g})",
     size=TXT_I, anchor="middle")

# ===== FRONT VIEW (2.5:1) — X 水平, Z 竖直; 从 -Y 开口端看 =====
S = 2.5
fx, fy = 118.0, 82.0
def fv(x, z): return (fx + x * S, fy - z * S)

text(fx, 33, "主视图  Front (2.5:1)   沿 +Y 看 (从开口端)   尺寸单位: mm", size=TXT_L, anchor="middle")

# 大扁头灰线先画, 让黑轮廓盖住重合的顶面边 (MR30 agent 复核指出)
phantom()
for sx in (-1, 1):
    rect(fv(sx*HX - HEAD_D/2, HTOP), fv(sx*HX + HEAD_D/2, HTOP + HEAD_T), w=0.30)
rect(fv(-HALF_L, -BASE_T), fv(HALF_L, 0), w=0.30)                 # 件 2 底板垫片
rect(fv(-SHIM_W/2, 0), fv(SHIM_W/2, SHIM_T), w=0.30)            # 凸台 (开口端就看得到)
for sx in (-1, 1):
    rect(fv(sx*HALF_L, 0), fv(sx*(HALF_L - RIM_W), RIM_H), w=0.30)      # 止口边框 左右
    rect(fv(sx*(HALF_L - RIM_W), 0), fv(sx*CH_W_B/2, RIM_H), w=0.30)    # 止口边框 开口端两段
rect(fv(-CH_W_B/2, 0), fv(CH_W_B/2, RIM_H), w=0.30)               # 件 2 后边框 (槽口里看得到的前端面)
solid()
polyline([fv(*p) for p in [(-HALF_L, _RH), (-HALF_L + _RW, _RH), (-HALF_L + _RW, 0), (-CH_W_B/2, 0),
                           (-CH_W_B/2, CH_H_B), (CH_W_B/2, CH_H_B), (CH_W_B/2, 0), (HALF_L - _RW, 0),
                           (HALF_L - _RW, _RH), (HALF_L, _RH), (HALF_L, HTOP), (-HALF_L, HTOP)]])
for sx in (-1, 1):
    pdf.line(*fv(sx*(HALF_L - _RW), _RH), *fv(sx*CH_W_B/2, _RH))  # 开口端止口台阶上沿 (前端面底边)
# 堵头内面: 底边 Z=0 + 两个 U 口 (从窄槽口里看得见)
_edge = [(-CH_W_B/2, SLOT_BOTTOM)]
for xc in WIRE_X:
    _edge += u_outline(xc, z0=SLOT_BOTTOM)
_edge += [(CH_W_B/2, SLOT_BOTTOM)]
polyline([fv(*p) for p in _edge], closed=False, w=GEOM_W)
hidden()
polyline([fv(-CH_W_S/2, 0), fv(-CH_W_S/2, CH_H_S), fv(CH_W_S/2, CH_H_S), fv(CH_W_S/2, 0)], closed=False, w=0.30)  # 护套段宽槽 (被挡住)
for sx in (-1, 1):
    for e in (-HOLE_D/2, HOLE_D/2):
        pdf.line(*fv(sx*HX + e, 0), *fv(sx*HX + e, HTOP))
center()
for sx in (-1, 1):
    pdf.line(*fv(sx*HX, -1.5), *fv(sx*HX, HTOP + HEAD_T + 1.5))
pdf.line(*fv(0, -1.5), *fv(0, HTOP + 1.5))
solid()

# 详图 A 标记 (纸面半径 14.5 包住两个 U 口)
_ax, _ay = fv(0, WIRE_ZC)
_w(0.25); pdf.circle(_ax, _ay, 14.5, style="D")
text(_ax + 12.0, _ay - 13.0, "A", size=TXT_L)          # 基线落在顶面线和 9.2 虚线之间 (审查 #15a)

vdim(fv(0, HTOP)[1], fv(0, 0)[1], fv(-HALF_L, 0)[0], fv(-HALF_L, 0)[0] - DIM_O1, f"{HTOP:g}")
hdim(fv(-CH_W_B/2, 0)[0], fv(CH_W_B/2, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + 16.0, f"{CH_W_B:g}")
hdim(fv(-CH_W_S/2, 0)[0], fv(CH_W_S/2, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + 27.0, f"{CH_W_S:g} mm (护套段, 虚线)")

# 大扁头引注
_hx, _hy = fv(HX + HEAD_D/2, HTOP + HEAD_T)
_w(DIM_W)
pdf.line(_hx, _hy, _hx + 12, _hy - 4); pdf.line(_hx + 12, _hy - 4, _hx + 16, _hy - 4)
text(_hx + 17, _hy - 3, f"M6 大扁头 Φ{HEAD_D:g}×{HEAD_T:g} 坐顶面 (灰线)", size=TXT_D)
_nx, _ny = fv(-HALF_L + RIM_W / 2, RIM_H / 2)
_w(DIM_W); pdf.set_fill_color(0, 0, 0); pdf.circle(_nx, _ny, 0.5, style="F")
pdf.line(_nx, _ny, _nx - 8, _ny + 9); pdf.line(_nx - 8, _ny + 9, _nx - 12, _ny + 9)
text(_nx - 12.5, _ny + 10, f"止口: 件 2 边框 {RIM_W:g}×{RIM_H:g} (灰), 压块台阶 {_RW:g}×{_RH:g}", size=TXT_I, anchor="end")

# 孔壁到槽壁薄肉引注 (右侧, 指向本体段那条)
_wx, _wy = fv(CH_W_B/2 + WEB_B/2, CH_H_B * 0.75)
_w(DIM_W)
pdf.set_fill_color(0, 0, 0); pdf.circle(_wx, _wy, 0.6, style="F")
pdf.line(_wx, _wy, 176, 86); pdf.line(176, 86, 180, 86)
text(181, 85, f"孔壁到槽壁: 本体段 {WEB_B:g} / 护套段 {WEB_S:g} (两侧)", size=TXT_D)
text(181, 91, f"螺杆离接头 >= {SHANK_GAP:g}", size=TXT_I)

# ===== LEFT VIEW, FULL SECTION (2.5:1) — 沿对称面 X=0 剖, 沿 +X 看: 纸面水平 = -Y (堵头 +Y 在左) =====
sx0 = 300.0
_ymid = (Y_OPEN + Y_END) / 2
def sv(y, z): return (sx0 - (y - _ymid) * S, fy - z * S)

text(sx0, 33, "左视图 (全剖)  Section (2.5:1)   沿对称面 X=0 剖, 沿 +X 看", size=TXT_L, anchor="middle")

hatch_rect(sv(Y_OPEN, HTOP), sv(Y_STEP, CH_H_B))     # 顶板 本体段 (厚 HTOP-CH_H_B)
hatch_rect(sv(Y_STEP, HTOP), sv(Y_CAPI, CH_H_S))     # 顶板 护套段
hatch_rect(sv(Y_CAPI, HTOP), sv(Y_END, RIM_H))       # 堵头 (X=0 在两个 U 口之间, 实心; 下部 RIM_H 是后边台阶)
phantom()
polyline([sv(Y_OPEN, BODY_LIFT), sv(Y_OPEN, BODY_LIFT + BODY_H), sv(Y_XSTEP, BODY_LIFT + BODY_H), sv(Y_XSTEP, SHEATH_H),
          sv(Y_CAPI, SHEATH_H), sv(Y_CAPI, 0), sv(Y_XSTEP, 0), sv(Y_XSTEP, BODY_LIFT)], w=0.30)   # 本体 + 护套 (先画)
rect(sv(Y_OPEN, -BASE_T), sv(Y_END, 0), w=0.30)      # 件 2 底板垫片
rect(sv(Y_CAPI, 0), sv(Y_END, RIM_H), w=0.30)        # 件 2 后边框 (宽 3)
rect(sv(Y_OPEN, 0), sv(Y_OPEN + RIM_W, RIM_H), w=0.30)   # 件 2 开口端边框 (在剖切面后方)
rect(sv(SHIM_Y0, 0), sv(SHIM_Y1, SHIM_T), w=0.30)    # 凸台
solid()
polyline([sv(Y_OPEN, RIM_H), sv(Y_OPEN + _RW, RIM_H), sv(Y_OPEN + _RW, 0), sv(Y_CAPI - ASSY_CLR, 0), sv(Y_CAPI - ASSY_CLR, RIM_H), sv(Y_END, RIM_H),
          sv(Y_END, HTOP), sv(Y_OPEN, HTOP)])                                        # 压块外廓 (后边台阶)
polyline([sv(Y_OPEN, CH_H_B), sv(Y_STEP, CH_H_B), sv(Y_STEP, CH_H_S), sv(Y_CAPI, CH_H_S), sv(Y_CAPI, RIM_H)], closed=False)
center()
pdf.line(*sv(HOLE_Y, -1.5), *sv(HOLE_Y, HTOP + 1.5))  # 孔轴线 (孔在剖面后方)
solid()
# 详图 B 标记
_bx, _by = sv(Y_STEP, (CH_H_S + CH_H_B) / 2)
_w(0.25); pdf.circle(_bx, _by, 6.0, style="D")
text(_bx + 5.5, _by - 8.0, "B", size=TXT_L)

hdim(sv(Y_END, 0)[0], sv(Y_CAPI, 0)[0], sv(0, HTOP)[1], sv(0, HTOP)[1] - 10.0,
     f"堵头 {CAP_T:g}", label_at="right")
hdim(sv(Y_CAPI, 0)[0], sv(Y_STEP, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + 9.0, f"{Y_CAPI - Y_STEP:g}")
hdim(sv(Y_STEP, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + 9.0, f"{Y_STEP - Y_OPEN:g}")
hdim(sv(Y_CAPI, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + 19.0, f"槽深 {XT_L:g}")
hdim(sv(Y_END, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + 29.0, f"{DEPTH:g}")
text(sv(Y_OPEN, 0)[0], sv(0, HTOP)[1] - 3.5, "开口端", size=TXT_D, anchor="middle")
text(sv(Y_END - 1.5, 0)[0], sv(0, HTOP)[1] - 3.5, "出线端", size=TXT_D, anchor="middle")
text(sx0, fy + 39, f"灰线: 件 2 底板垫片 (厚 {BASE_T:g}, 凸台 {SHIM_T:g}, 止口高 {RIM_H:g}) + 插合本体 (开口侧) + 出线护套 (堵头侧)", size=TXT_I, anchor="middle")
text(sx0, fy + 45, f"槽顶 = 接头顶面 (过盈 0): 护套段 {CH_H_S:g} / 本体段 {CH_H_B:g} = 凸台 {SHIM_T:g} + {BODY_H:g}, 均从底板顶面算 (见详图 B)",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (2.5:1) — X 水平, Y 竖直 (+Y 堵头在上) =====
tx0, ty0 = fx, 162.0
def tv(x, y): return (tx0 + x * S, ty0 - y * S)

text(tx0, 118, "俯视图  Top (2.5:1)   沿 -Z 看", size=TXT_L, anchor="middle")

solid()
rect(tv(-HALF_L, Y_END), tv(HALF_L, Y_OPEN))
_w(GEOM_W)
for sx in (-1, 1):
    pdf.circle(*tv(sx*HX, HOLE_Y), HOLE_D/2 * S, style="D")
hidden()
polyline([tv(-CH_W_B/2, Y_OPEN), tv(-CH_W_B/2, Y_STEP), tv(-CH_W_S/2, Y_STEP), tv(-CH_W_S/2, Y_CAPI),
          tv(CH_W_S/2, Y_CAPI), tv(CH_W_S/2, Y_STEP), tv(CH_W_B/2, Y_STEP), tv(CH_W_B/2, Y_OPEN)],
         closed=False, w=0.30)                                   # 阶梯槽 (止于堵头)
pdf.line(*tv(-CH_W_B/2, Y_STEP), *tv(CH_W_B/2, Y_STEP))          # 槽顶台阶线
for sx in (-1, 1):
    pdf.line(*tv(sx*(HALF_L - _RW), Y_OPEN + _RW), *tv(sx*(HALF_L - _RW), Y_CAPI - ASSY_CLR))   # 底面止口台阶 (左右)
    pdf.line(*tv(sx*CH_W_S/2, Y_CAPI - ASSY_CLR), *tv(sx*(HALF_L - _RW), Y_CAPI - ASSY_CLR))   # 底面止口台阶 (后边 3.1 宽前沿)
    pdf.line(*tv(sx*CH_W_B/2, Y_OPEN + _RW), *tv(sx*(HALF_L - _RW), Y_OPEN + _RW))    # 底面止口台阶 (开口端)
for xc in WIRE_X:
    for e in (-WIRE_D/2, WIRE_D/2):
        pdf.line(*tv(xc + e, Y_CAPI), *tv(xc + e, Y_END))          # U 口两侧边
phantom()
for sx in (-1, 1):
    pdf.circle(*tv(sx*HX, HOLE_Y), HEAD_D/2 * S, style="D")      # 头投影
center()
pdf.line(*tv(-HALF_L - 2, HOLE_Y), *tv(HALF_L + 2, HOLE_Y))
for sx in (-1, 1):
    pdf.line(*tv(sx*HX, Y_END + 2), *tv(sx*HX, Y_OPEN - 2))
solid()

hdim(tv(-HX, 0)[0], tv(HX, 0)[0], tv(0, Y_OPEN)[1], tv(0, Y_OPEN)[1] + DIM_O1, f"{PITCH:g}")
hdim(tv(-HALF_L, 0)[0], tv(HALF_L, 0)[0], tv(0, Y_OPEN)[1], tv(0, Y_OPEN)[1] + DIM_O2, f"{L:g}")
vdim(tv(0, HOLE_Y)[1], tv(0, Y_OPEN)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + DIM_O1, f"{HOLE_Y_OPEN:g}")
vdim(tv(0, Y_END)[1], tv(0, Y_OPEN)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + DIM_O2, f"{DEPTH:g}")
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_END)[1] + 5.0, "堵头侧 (护套)", size=TXT_D, anchor="end")
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_OPEN)[1] - 2.0, "开口侧 (本体)", size=TXT_D, anchor="end")

# 孔引注 (左上)
_a = math.radians(45)
_px, _py = tv(-HX, HOLE_Y)
_px -= HOLE_D/2 * S * math.cos(_a); _py -= HOLE_D/2 * S * math.sin(_a)
_w(DIM_W)
pdf.line(_px, _py, 52, 128); pdf.line(52, 128, 47, 128)
text(46, 129, f"2×Φ{HOLE_D:g} 通孔 (配 M6)", size=TXT_D, anchor="end")

# ===== DETAIL A (5:1) — U 型出线口, 沿 +Y 看 (同主视图) =====
DS = 5.0
dx0, dy0 = 332.0, 182.0
BREAK_Z = WIRE_ZC + WIRE_D / 2 + 1.6
def da(x, z): return (dx0 + x * DS, dy0 - z * DS)

text(dx0, 136, "详图 A (5:1)   堵头 U 型出线口 (沿 +Y 看)", size=TXT_L, anchor="middle")

# 沿 +Y 看 (视图): 两侧是本体段槽口 ±CH_W_B/2 (一直到 z=0); 里面是堵头内面, 下沿 SLOT_BOTTOM + U 口
_edgeA = [(-CH_W_B/2, SLOT_BOTTOM)]
for xc in WIRE_X:
    _edgeA += u_outline(xc, z0=SLOT_BOTTOM)
_edgeA += [(CH_W_B/2, SLOT_BOTTOM)]
phantom()
rect(da(-CH_W_B/2, 0), da(CH_W_B/2, RIM_H), w=0.35)                 # 件 2 后边框 (顶面 = 出线口平底)
solid()
for sx in (-1, 1):
    polyline([da(sx*CH_W_B/2, 0), da(sx*CH_W_B/2, BREAK_Z)], closed=False, w=GEOM_W)
polyline([da(*p) for p in _edgeA], closed=False, w=GEOM_W)
_w(0.20)
_wave = [da(x / 8.0, BREAK_Z + 0.3 * math.sin(x / 8.0 * 1.6)) for x in range(int(-(CH_W_B/2 + 0.8) * 8), int((CH_W_B/2 + 0.8) * 8) + 1)]
for a, b in zip(_wave[:-1], _wave[1:]):
    pdf.line(*a, *b)
center()
for xc in WIRE_X:
    pdf.line(*da(xc, -1.2), *da(xc, WIRE_ZC + WIRE_D/2 + 1.8))
pdf.line(*da(WIRE_X[0] - WIRE_D/2 - 1.0, WIRE_ZC), *da(WIRE_X[1] + WIRE_D/2 + 1.0, WIRE_ZC))
pdf.line(*da(0, -1.2), *da(0, WIRE_ZC + WIRE_D/2 + 1.0))
solid()

hdim(da(WIRE_X[0], 0)[0], da(WIRE_X[1], 0)[0], da(0, WIRE_ZC + WIRE_D/2)[1], da(0, WIRE_ZC + WIRE_D/2)[1] - 12.0,
     f"{WIRE_PITCH:g}")
hdim(da(WIRE_X[1] - WIRE_D/2, 0)[0], da(WIRE_X[1] + WIRE_D/2, 0)[0], da(0, 0)[1], da(0, 0)[1] + 12.0,
     f"{WIRE_D:g}")
_xl = da(-CH_W_B/2, 0)[0]
_xu = da(WIRE_X[0] - WIRE_D/2, 0)[0]          # 左 U 口左直边: 底边界线从这里往左, 不横穿 U 口 (MR30 agent 复核指出)
vdim(da(0, WIRE_ZC)[1], da(0, 0)[1], _xu, _xl - 7.0, f"{WIRE_ZC:g}")
vdim(da(0, WIRE_ZC + WIRE_D/2)[1], da(0, 0)[1], da(WIRE_X[0], 0)[0], _xl - 18.0, f"{WIRE_ZC + WIRE_D/2:g}", xg2=_xu)
_rx, _ry = da(WIRE_X[1] + WIRE_D/2 * math.cos(_a), WIRE_ZC + WIRE_D/2 * math.sin(_a))
_w(DIM_W)
pdf.line(_rx, _ry, 380, 150); pdf.line(380, 150, 384, 150)
text(385, 151, f"R{WIRE_D/2:g} (Φ{WIRE_D:g})", size=TXT_D)
text(dx0, 207, f"U 口 = 半圆顶 + 直边, 平底 = 件 2 后边框顶 z {SLOT_BOTTOM:g} (灰, 宽 {BACK_RIM_W:g} 高 {RIM_H:g}); 线底 {LEDGE:g} 高于边框, 不削", size=TXT_I, anchor="middle")
text(dx0, 213, f"线 Φ{WIRE_D:g} 零余量, 从护套尾孔沿针轴直出 (圆心 {WIRE_ZC:g} = 护套高/2)", size=TXT_I, anchor="middle")

# ===== DETAIL B (5:1) — 槽台阶处 Z 向堆叠, 同左视图方向 (+Y 护套在左, -Y 本体在右) =====
BS = 5.0
bx0, by0 = 232.0, 172.0
BW = 2.4                                  # 窗口: Y_STEP ± BW
B_TOP = CH_H_S + 0.8                      # 上断裂线
def db(y, z): return (bx0 - (y - Y_STEP) * BS, by0 - z * BS)

text(bx0, 118, "详图 B (5:1)   槽台阶 Z 向堆叠", size=TXT_L, anchor="middle")

_yl, _yr = Y_STEP + BW, Y_STEP - BW       # 纸面左 (+Y 护套段) / 右 (-Y 本体段)
hatch_rect(db(_yl, B_TOP), db(Y_STEP, CH_H_S))
hatch_rect(db(Y_STEP, B_TOP), db(_yr, CH_H_B))
phantom()
polyline([db(_yl, SHEATH_H), db(Y_XSTEP, SHEATH_H), db(Y_XSTEP, BODY_LIFT + BODY_H), db(_yr, BODY_LIFT + BODY_H)],
         closed=False, w=0.30)                                           # 接头顶面 (护套 9.2 -> 本体 8.7)
polyline([db(Y_XSTEP, 0), db(Y_XSTEP, BODY_LIFT), db(_yr, BODY_LIFT)], closed=False, w=0.30)   # 护套前端面 + 本体底面
polyline([db(SHIM_Y1, 0), db(SHIM_Y1, SHIM_T), db(_yr, SHIM_T)], closed=False, w=0.30)        # 凸台 (底边=底板顶面)
solid()
polyline([db(_yl, CH_H_S), db(Y_STEP, CH_H_S), db(Y_STEP, CH_H_B), db(_yr, CH_H_B)], closed=False)   # 槽顶
pdf.line(*db(Y_STEP, 0), *db(Y_STEP, CH_H_B))                              # 槽宽台阶棱 (本体段 7.8 壁 -> 护套段 8.3 壁)
_w(0.6)
pdf.line(*db(_yl, 0), *db(_yr, 0))                                        # 件 2 底板顶面
_w(0.20)
_wave = [db(_yl - i * (2 * BW) / 40, B_TOP + 0.12 * math.sin(i / 40 * 2 * math.pi * 2)) for i in range(41)]
for a, b in zip(_wave[:-1], _wave[1:]):
    pdf.line(*a, *b)
text(db(_yl, 0)[0], db(0, 0)[1] + 4.5, "护套段", size=TXT_I, anchor="start")

# 左侧: 护套段槽顶 CH_H_S ; 右侧: 本体段槽顶 CH_H_B
vdim(db(_yl, CH_H_S)[1], db(_yl, 0)[1], db(_yl, 0)[0], db(_yl, 0)[0] - 9.0, f"{CH_H_S:g}")
vdim(db(_yr, CH_H_B)[1], db(_yr, 0)[1], db(_yr, 0)[0], db(_yr, 0)[0] + 9.0, f"{CH_H_B:g}")
# 顶面贴合: 写在槽内空白处 (原引线拐点压断裂线、斜线像剖面线, 审查 #15b)
_tx = (db(_yl, 0)[0] + db(Y_STEP, 0)[0]) / 2                  # 护套段半边中间, 避开台阶棱
text(_tx, db(0, 6.2)[1], "槽顶=接头顶", size=4.2, anchor="middle")
text(_tx, db(0, 6.2)[1] + 4.5, "过盈 0", size=4.2, anchor="middle")
# 凸台高: 引注往右下
_p3 = db((SHIM_Y1 + _yr) / 2 - 0.4, SHIM_T / 2)
pdf.set_fill_color(0, 0, 0); pdf.circle(*_p3, 0.5, style="F")
text(_p3[0] - 1.5, db(0, 0)[1] + 4.5, "本体段", size=TXT_I, anchor="end")
pdf.line(*_p3, _p3[0] + 4, 179.5); pdf.line(_p3[0] + 4, 179.5, _p3[0] + 7, 179.5)
text(_p3[0] + 7.5, 180.5, f"凸台 {SHIM_T:g} (件 2)", size=TXT_I)

# ===== 件 2: 底板垫片 (1:1) — 俯视, 开口端在下 =====
PS = 1.0
px0, py0 = 232.0, 201.5
def pv(x, y): return (px0 + x * PS, py0 - (y - (Y_OPEN + Y_END) / 2) * PS)

text(px0, 185.6, f"件 2  底板垫片 (1:1)  底板 {BASE_T:g} + 凸台 {SHIM_T:g} + 止口四边高 {RIM_H:g}", size=TXT_L, anchor="middle")
solid()
rect(pv(-HALF_L, Y_END), pv(HALF_L, Y_OPEN))
rect(pv(-SHIM_W/2, SHIM_Y1), pv(SHIM_W/2, SHIM_Y0), w=0.35)          # 凸台
_w(0.35)
for sx in (-1, 1):
    pdf.circle(*pv(sx*HX, HOLE_Y), HOLE_D/2 * PS, style="D")
    pdf.line(*pv(sx*(HALF_L - RIM_W), Y_OPEN + RIM_W), *pv(sx*(HALF_L - RIM_W), Y_CAPI))   # 止口边框内沿 (左右)
    pdf.line(*pv(sx*CH_W_B/2, Y_OPEN + RIM_W), *pv(sx*(HALF_L - RIM_W), Y_OPEN + RIM_W))  # 止口边框内沿 (开口端)
pdf.line(*pv(-(HALF_L - RIM_W), Y_CAPI), *pv(HALF_L - RIM_W, Y_CAPI))                    # 后边框内沿 (宽 3)
_rx2, _ry2 = pv(-HALF_L + RIM_W / 2, Y_OPEN + 8)
_w(DIM_W); pdf.set_fill_color(0, 0, 0); pdf.circle(_rx2, _ry2, 0.4, style="F")
pdf.line(_rx2, _ry2, _rx2 - 5, _ry2); text(_rx2 - 5.5, _ry2 + 0.8, f"止口高 {RIM_H:g}: 侧/前宽 {RIM_W:g}", size=4.2, anchor="end")
text(pv(0, 0)[0], pv(0, Y_CAPI - 1.6)[1] + 0.6, f"上方后边框 宽 {BACK_RIM_W:g} 高 {RIM_H:g} (出线边)", size=4.0, anchor="middle")
hdim(pv(-HALF_L, 0)[0], pv(HALF_L, 0)[0], pv(0, Y_OPEN)[1], pv(0, Y_OPEN)[1] + 4.5, f"{L:g}")
vdim(pv(0, Y_END)[1], pv(0, Y_OPEN)[1], pv(HALF_L, 0)[0], pv(HALF_L, 0)[0] + 5.5, f"{DEPTH:g}")
text(pv(0, 0)[0], pv(0, (SHIM_Y0 + SHIM_Y1) / 2)[1] + 0.8, f"凸台 {SHIM_W:g}×{SHIM_L:g}", size=4.2, anchor="middle")
text(pv(0, 0)[0], pv(0, HOLE_Y + 2.2)[1] + 0.6, f"2×Φ{HOLE_D:g} 同压块孔", size=4.0, anchor="middle")
text(pv(-HALF_L, 0)[0] - 1.0, pv(0, Y_OPEN)[1], "开口端", size=4.2, anchor="end")

# ===== 说明 =====
NX, NY = 25, 219
text(NX, NY, "说明 / Notes", size=TXT_L)
for i, s in enumerate([
    f"1) 尺寸: 宽 {SHEATH_W:g} / {BODY_W:g} 用户指定 (图纸 16.40), 高/长按 AMASS XT60H-M 图纸 + 卡尺。插合本体 {BODY_W:g}×{BODY_H:g} 长 {BODY_L:g} 在开口端; 出线护套 {SHEATH_W:g}×{SHEATH_H:g} 长 {SHEATH_L:g} 在堵头端 (本体上下各缩 {BODY_LIFT:g})。v4 纠正了 v3 前后装反。",
    f"2) 阶梯槽紧配不留余量 (用户要求): 本体段 {CH_W_B:g}×{CH_H_B:g} / 护套段 {CH_W_S:g}×{CH_H_S:g}, 宽高都 = 接头 (间隙 0, 过盈 0), 槽台阶与接头台阶对齐。",
    f"3) 限位: 插入方向护套上部顶堵头、下部顶件 2 后边框; 拔出方向护套前端面顶窄槽台阶 (零窜动)。件 2 底板垫片 {L:g}×{DEPTH:g}×{BASE_T:g} + 本体下凸台 {SHIM_T:g} + 止口四边高 {RIM_H:g} (左右/开口端宽 {RIM_W:g} 开口端槽口断开, 后边宽 {BACK_RIM_W:g}; 压块台阶宽多 {ASSY_CLR:g}); 两件嵌套面留 {ASSY_CLR:g}; M6 定位。",
    f"4) 装配: 底板垫片放板上 -> 接头 (本体坐凸台, 护套坐底板顶住后边框) -> 压块扣下 (套进止口, 线落进 U 口) -> M6 穿压块+底板。叠层 {STACK_H:g}: M6×20 旋入 {20-STACK_H:g} 距板底 {PLATE_T-(20-STACK_H):g}; M6×25 旋入 {25-STACK_H:g} 距板底 {PLATE_T-(25-STACK_H):g}。",
    f"5) 孔壁到槽壁: 护套段 {WEB_S:g} / 本体段 {WEB_B:g} (两侧), 打印可能破口, 不影响夹紧; 螺杆离接头 >= {SHANK_GAP:g}。孔心距开口面 {HOLE_Y_OPEN:g}。堵头 {CAP_T:g} + 2 个 U 口 Φ{WIRE_D:g} @ {WIRE_PITCH:g}, 圆心高 {WIRE_ZC:g}。",
    f"6) 槽顶厚 护套段 {T_TOP:g} / 本体段 {HTOP-CH_H_B:g} (件高 11 用户指定)。打印: 压块顶面贴床零支撑; 实心 {VOL/1000:.2f} cm^3, PLA 约 {VOL*1.24e-3:.1f} g。底板垫片底面贴床零支撑。",
    f"7) 组合外形: 压块 + 底板垫片 = {L:g}×{DEPTH:g}×{STACK_H:g} 长方体, 外表面只有 2×M6 孔、开口端接头口、堵头 2 个出线口 (压块 U 口, 平底 = 后边框顶 z {SLOT_BOTTOM:g}); 止口、凸台都在内部, 边框顶贴台阶顶不留缝。",
    f"8) 层高 (零间隙对层高敏感): 两件都用 0.1 (全部整层) 或 0.25 (首层也 0.25, 本体段/护套段各松 0.05); 不要用 0.2 —— 本体段槽顶和凸台顶落在层中间, 本体段会过盈 0.2 扣不到底。",
]):
    text(NX, NY + 7 + i * 5.0, s, size=4.6)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "结构件 — XT60 电源接头压块 (XT60 Clamp v4.10, 组合 38×26.9×13 长方体, 零间隙, 中央出线, 止口四边) + 件 2 底板垫片", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 2.5:1 (主, 左剖, 俯), 5:1 (详图 A, B), 1:1 (件 2)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"{L:g}×{DEPTH:g}×{HTOP:g} / 阶梯槽 {CH_W_B:g}×{CH_H_B:g} (开口) + {CH_W_S:g}×{CH_H_S:g} (堵头) / 堵头 {CAP_T:g} + 2×U 口 / "
     f"2×Φ{HOLE_D:g} @ {PITCH:g} / 底板垫片 {L:g}×{DEPTH:g}×{BASE_T:g}+凸台 {SHIM_T:g}+止口四边 高 {RIM_H:g} (后边宽 {BACK_RIM_W:g}) / M6×20 / PLA/PETG / mm",
     size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-16  /  pov3d / models / xt60_clamp_16p6x9p2x23p9 / *.stl (压块 + xt60_shim_38x26p9x2p5)",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("xt60_clamp_16p6x9p2x23p9_drawing.pdf")
try:
    pdf.output(str(out))
except PermissionError:                     # PDF 在阅读器里开着
    out = out.with_suffix(".NEW.pdf")
    pdf.output(str(out))
print(f"wrote {out}")
