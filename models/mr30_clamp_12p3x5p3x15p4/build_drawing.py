"""
A3 landscape 2D engineering drawing for mr30_clamp_12p3x5p3x15p4 (MR30 电源/电机接头压块 v2: 阶梯槽 = 接头名义尺寸, 间隙/过盈全 0 + 件 2 底板垫片).

  1) 主视图 Front (3:1)      沿 +Y 看 (从开口端): 平顶块 + 本体段窄槽口 (实线); 护套段宽槽在后面 (虚线); 堵头 3 个 U 口; 底板垫片 (灰)
  2) C-C 全剖 (3:1)          沿对称面 X=0 剖 (过中间出线口), 沿 +X 看 (+Y 堵头 / 出线端在左): 阶梯槽顶 + 堵头 + 剖面后方可见轮廓; 灰线 = 本体 + 护套 + 底板垫片
  3) 俯视图 Top   (3:1)      2×Φ6.5 @ 25, 外形 38×18.4, 孔心距开口面 11.9, 阶梯槽 / U 口 (虚线)
  4) 详图 A (6:1)            堵头出线口, 视图 (沿 +Y 从本体段槽口看进去, 实线槽口 11.8, 护套段 12.3 虚线): 针距 3.5 / 口宽 2.5 / R1.25 / 圆心高 2.65 / 口顶 3.9 / 缺口底 1.4
  5) 详图 B (8:1)            槽台阶处 Z 向堆叠: 护套段槽顶 5.3 / 本体段槽顶 5.05 / 凸台 0.25 / 垫片底板顶面
  6) 件 2 垫片 (2:1) 俯视    底板 38 × 18.4 × 2 + 凸台 11.6 × 8.5 × 0.25 + 2×Φ6.5 同轴 + 止口四边 (侧/前 宽 2, 后 宽 3, 高 2; 出线处削到 1.4)
  嵌套 (用户 09-16): 压块底面切台阶 (侧/前 2.1, 后 3.1, 高 2) 套住边框, 竖直面留 0.1、高度贴合 => 组合外形平齐长方体;
  出线孔 = 压块 U 口 + 后边框缺口平底 1.4, 内切 Φ2.5。

接头尺寸按用户 09-16 给定 12.3×5.3×15.4 (前 8.5 单边小 0.25), 阶梯槽照 XT60 做法。
主视图与 C-C 之间隔着件 2 视图 → 按 GB/T 4458.6 在主视图 X=0 处标剖切符号 C (箭头指 +X)。
⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / mr30_clamp_12p3x5p3x15p4.scad) =====
SHEATH_W, SHEATH_H = 12.3, 5.3
BODY_STEP = 0.25
BODY_W    = SHEATH_W - 2 * BODY_STEP     # 11.8
BODY_H    = SHEATH_H - 2 * BODY_STEP     #  4.8
MR_L      = 15.4
BODY_L    = 8.5
SHEATH_L  = MR_L - BODY_L                #  6.9
BODY_LIFT = (SHEATH_H - BODY_H) / 2      #  0.25
PIN_ZC    = SHEATH_H / 2                 #  2.65
MR_PITCH  = 3.5
N_WIRE    = 3
SIDE_CLR_S, SIDE_CLR_B = 0.0, 0.0
PRELOAD_S,  PRELOAD_B  = 0.0, 0.0
STEP_MARGIN = 0.0
BASE_T          = 2.0         # 垫片底板厚 (用户)
BOSS_T          = BODY_LIFT   # 0.25 凸台高
BOSS_CLR        = 0.1         # = ASSY_CLR
RIM_W, RIM_H    = 2.0, 2.0    # 止口 (侧/前 宽 2, 高 2)
REAR_RIM_W      = 3.0         # 止口后边宽 = 堵头厚
ASSY_CLR        = 0.1         # 上下件嵌套面装配间隙
BOSS_OPEN_INSET = 0.0
BOSS_BACK_GAP   = 0.0
T_TOP       = 3.0
CAP_T       = 3.0
WIRE_OD     = 2.5
WIRE_CLR    = 0.0
WIRE_D      = WIRE_OD + 2 * WIRE_CLR
WIRE_PITCH  = MR_PITCH
WIRE_ZC     = PIN_ZC                     # 护套厚/2
PITCH       = 25.0
HOLE_D      = 6.5
END         = 6.5
HOLE_Y_OPEN = 11.9                       # 待用户定
HEAD_D, HEAD_T = 12.5, 2.6
PLATE_T     = 13.0
M6_SHANK_D  = 6.0

CH_W_B = BODY_W + 2 * SIDE_CLR_B             # 11.8
CH_H_B = BODY_LIFT + BODY_H - PRELOAD_B      #  5.05
CH_W_S = SHEATH_W + 2 * SIDE_CLR_S           # 12.3
CH_H_S = SHEATH_H - PRELOAD_S                #  5.3
HTOP   = CH_H_S + T_TOP                      #  8.3
T_TOP_B = HTOP - CH_H_B                      #  3.25
HX     = PITCH / 2
HALF_L = HX + END
L      = 2 * HALF_L                          # 38
Y_OPEN  = -MR_L / 2                          # -7.7
Y_XSTEP = Y_OPEN + BODY_L                    #  0.8
Y_STEP  = Y_XSTEP - STEP_MARGIN              #  0.8
Y_CAPI  =  MR_L / 2                          #  7.7
Y_END   = Y_CAPI + CAP_T                     # 10.7
DEPTH   = Y_END - Y_OPEN                     # 18.4
HOLE_Y  = Y_OPEN + HOLE_Y_OPEN               #  4.2
WEB_S     = HX - HOLE_D / 2 - CH_W_S / 2     # 3.1
SHANK_GAP = HX - M6_SHANK_D / 2 - CH_W_S / 2 # 3.35
WIRE_X = tuple((i - (N_WIRE - 1) / 2) * WIRE_PITCH for i in range(N_WIRE))
U_TOP  = WIRE_ZC + WIRE_D / 2                # 3.9
U_ROOF = CH_H_S - U_TOP                      # 1.4
U_RIB  = WIRE_PITCH - WIRE_D                 # 1.0
U_SIDE = CH_W_S / 2 - (WIRE_X[-1] + WIRE_D / 2)   # 1.4
BOSS_W  = CH_W_B - 2 * BOSS_CLR              # 11.8
BOSS_Y0 = Y_OPEN + BOSS_OPEN_INSET           # -7.7
BOSS_Y1 = Y_XSTEP - BOSS_BACK_GAP            #  0.8
BOSS_L  = BOSS_Y1 - BOSS_Y0                  #  8.5
SHIM_TOTAL = BASE_T + BOSS_T                 #  2.25
RIM_X_IN   = HALF_L - RIM_W                  # 17
RIM_Y1     = Y_OPEN + RIM_W                  # -5.7
RIM_SEG_X0 = CH_W_B / 2                      #  5.9
STEP_W     = RIM_W + ASSY_CLR                #  2.1 压块侧/前台阶宽
STEP_H     = RIM_H                           #  2.0 压块台阶高 (高度不留缝)
STEP_X_IN  = HALF_L - STEP_W                 # 16.9
STEP_Y1    = Y_OPEN + STEP_W                 # -5.6
REAR_RIM_Y0  = Y_END - REAR_RIM_W            #  7.7 后边框前沿
REAR_STEP_Y0 = Y_END - (REAR_RIM_W + ASSY_CLR)   # 7.6 压块后台阶前沿
LEDGE_H    = WIRE_ZC - WIRE_OD / 2           #  1.4 出线处缺口底
STEP_HOLE_WEB = STEP_X_IN - (HX + HOLE_D / 2)          # 1.15
REAR_HOLE_WEB = REAR_STEP_Y0 - (HOLE_Y + HOLE_D / 2)   # 0.15 ⚠
STACK_H    = BASE_T + HTOP                   # 10.3 螺丝夹持叠层
U_AREA = WIRE_D * WIRE_ZC + math.pi * (WIRE_D / 2) ** 2 / 2
VOL = (L * DEPTH * HTOP - CH_W_B * (Y_STEP - Y_OPEN) * CH_H_B - CH_W_S * (Y_CAPI - Y_STEP) * CH_H_S
       - 2 * math.pi * (HOLE_D / 2) ** 2 * HTOP - N_WIRE * U_AREA * CAP_T
       - (2 * (HALF_L - CH_W_B / 2) * STEP_H * (STEP_Y1 - Y_OPEN)
          + 2 * STEP_W * STEP_H * (REAR_STEP_Y0 - STEP_Y1)
          + (L - CH_W_S) * STEP_H * (Y_CAPI - REAR_STEP_Y0)
          + (L * STEP_H - N_WIRE * WIRE_D * STEP_H) * CAP_T))
SHIM_VOL = (L * DEPTH * BASE_T - 2 * math.pi * (HOLE_D / 2) ** 2 * BASE_T + BOSS_W * BOSS_L * BOSS_T
            + 2 * (HALF_L - CH_W_B / 2) * RIM_H * RIM_W + 2 * RIM_W * RIM_H * (REAR_RIM_Y0 - RIM_Y1)
            + (L * RIM_H - N_WIRE * WIRE_D * (RIM_H - LEDGE_H)) * REAR_RIM_W)
SCREW = 20
ENG = SCREW - STACK_H                        # 9.7

def f2(v):
    """尺寸文字: 去掉多余的 0。"""
    return f"{round(v, 2):g}"

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
TXT_N  = 4.8
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
def text_w(s, size):
    pdf.set_font("SimHei", "", size)
    return pdf.get_string_width(_g(s))
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
    """xg2: 第二条尺寸界线 (y2 端) 的起点 x, 默认同 xg。"""
    label = _with_unit(label)
    xg2 = xg if xg2 is None else xg2
    sgn = 1.0 if xd > xg else -1.0
    ex2, to = xd + sgn * EXT_OV, 4.0 * sgn
    line(xg + sgn * EXT_GP, y1, ex2, y1, EXT_W)
    line(xg2 + sgn * EXT_GP, y2, ex2, y2, EXT_W)
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

def rear_rim_top(x0, x1):
    """件 2 后边框顶轮廓 (X, Z), 从 x0 到 x1: 高 RIM_H, 出线处缺口削到 LEDGE_H。"""
    pts = [(x0, RIM_H)]
    for xc in WIRE_X:
        a, b = xc - WIRE_D / 2, xc + WIRE_D / 2
        if b <= x0 or a >= x1:
            continue
        pts += [(a, RIM_H), (a, LEDGE_H), (b, LEDGE_H), (b, RIM_H)]
    return pts + [(x1, RIM_H)]

def cap_face_edge(w, z0=0.0):
    """堵头内面底边 (高 z0, 宽 w), 绕开 N 个 U 口。"""
    e = [(-w/2, z0)]
    for xc in WIRE_X:
        e += u_outline(xc, z0=z0)
    return e + [(w/2, z0)]

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "MR30 电源/电机接头压块  mr30_clamp_12p3x5p3x15p4   (v2 阶梯槽 间隙/过盈 0, 底板垫片嵌套, 孔距 25)", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"锁 MR30 (本体 {BODY_W:g}×{BODY_H:g}×{BODY_L:g} 在开口端 + 护套 {SHEATH_W:g}×{SHEATH_H:g}×{SHEATH_L:g} 在堵头端) 到 M6 网格板  ·  "
     f"外形 {L:g}×{f2(DEPTH)}×{f2(HTOP)}  ·  阶梯槽 {CH_W_B:g}×{f2(CH_H_B)} / {CH_W_S:g}×{CH_H_S:g}  ·  "
     f"{N_WIRE}×U 口 Φ{WIRE_D:g} @ {WIRE_PITCH:g} 中心高 {WIRE_ZC:g}  ·  件2 垫片 底板 {L:g}×{f2(DEPTH)}×{BASE_T:g} + 止口四边 (后 {REAR_RIM_W:g} 宽, 出线处削到 {LEDGE_H:g})  ·  组合 {L:g}×{f2(DEPTH)}×{f2(STACK_H)}",
     size=TXT_I, anchor="middle")

# ===== FRONT VIEW (3:1) — X 水平, Z 竖直; 从 -Y 开口端看 =====
S = 3.0
fx, fy = 112.0, 76.0
def fv(x, z): return (fx + x * S, fy - z * S)

text(fx, 33, "主视图  Front (3:1)   沿 +Y 看 (从开口端)   尺寸单位: mm", size=TXT_L, anchor="middle")

phantom()                                                            # 灰线先画, 黑轮廓盖住重合边
for sx in (-1, 1):
    rect(fv(sx*HX - HEAD_D/2, HTOP), fv(sx*HX + HEAD_D/2, HTOP + HEAD_T), w=0.30)
rect(fv(-HALF_L, -BASE_T), fv(HALF_L, 0), w=0.30)                   # 件 2 底板 (z -2..0)
rect(fv(-BOSS_W/2, 0), fv(BOSS_W/2, BOSS_T), w=0.30)                  # 件 2 凸台
polyline([fv(*q) for q in [(-HALF_L, 0.0)] + rear_rim_top(-HALF_L, HALF_L) + [(HALF_L, 0.0)]], closed=False, w=0.30)   # 件 2 止口 (投影 = 后边框全宽, 出线处缺口)
for sx in (-1, 1):
    for e in (-HOLE_D/2, HOLE_D/2):
        pdf.line(*fv(sx*HX + e, -BASE_T), *fv(sx*HX + e, 0))          # 底板孔
solid()
polyline([fv(*p) for p in [(-HALF_L, STEP_H), (-STEP_X_IN, STEP_H), (-STEP_X_IN, 0), (-CH_W_B/2, 0), (-CH_W_B/2, CH_H_B),
                           (CH_W_B/2, CH_H_B), (CH_W_B/2, 0), (STEP_X_IN, 0), (STEP_X_IN, STEP_H), (HALF_L, STEP_H),
                           (HALF_L, HTOP), (-HALF_L, HTOP)]])   # 本体段窄槽口 = 实线; 两底角台阶缺口
for sx in (-1, 1):
    pdf.line(*fv(sx*CH_W_B/2, STEP_H), *fv(sx*STEP_X_IN, STEP_H))      # 开口端台阶边线 (前端面底边)
polyline([fv(*p) for p in cap_face_edge(CH_W_B, STEP_H)], closed=False, w=GEOM_W)   # 堵头内面底边 (后台阶顶 2) + U 口
hidden()
polyline([fv(-CH_W_S/2, 0), fv(-CH_W_S/2, CH_H_S), fv(CH_W_S/2, CH_H_S), fv(CH_W_S/2, 0)], closed=False, w=0.30)  # 护套段宽槽 (虚线)
for sx in (-1, 1):
    for e in (-HOLE_D/2, HOLE_D/2):
        pdf.line(*fv(sx*HX + e, 0), *fv(sx*HX + e, HTOP))
center()
for sx in (-1, 1):
    pdf.line(*fv(sx*HX, -BASE_T - 1.0), *fv(sx*HX, HTOP + HEAD_T + 1.5))
pdf.line(*fv(0, -1.5), *fv(0, HTOP + 1.5))
solid()

# 详图 A 标记
_ax, _ay = fv(0, (LEDGE_H + U_TOP) / 2)
_ar = math.hypot((WIRE_X[-1] + WIRE_D/2) * S, (U_TOP - LEDGE_H) / 2 * S) + 1.0
_w(0.25); pdf.circle(_ax, _ay, _ar, style="D")
text(_ax + _ar * 0.78, _ay - _ar * 0.78, "A", size=TXT_L)          # 右上 (下方被底板灰线占了)

vdim(fv(0, HTOP)[1], fv(0, 0)[1], fv(-HALF_L, 0)[0], fv(-HALF_L, 0)[0] - DIM_O1, f2(HTOP), xg2=fv(-STEP_X_IN, 0)[0])
hdim(fv(-CH_W_B/2, 0)[0], fv(CH_W_B/2, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + 22.0, f"{CH_W_B:g}")
hdim(fv(-CH_W_S/2, 0)[0], fv(CH_W_S/2, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + 32.0, f"{CH_W_S:g} mm (护套段, 虚线)")

# 剖切符号 C (GB/T 4458.6): X=0 剖切面两端粗短画 + 箭头指投影方向 (+X) + 字母
for _y0, _y1 in ((44.5, 39.5), (fv(0, -BASE_T)[1] + 4.5, fv(0, -BASE_T)[1] + 9.5)):
    _w(0.8); pdf.line(fx, _y0, fx, _y1)
    _w(DIM_W); pdf.line(fx, _y1, fx + 7.0, _y1); arrow(fx + 7.0, _y1, 1, 0)
    text(fx + 9.0, _y1 + 1.5, "C", size=TXT_L)

_hx, _hy = fv(HX + HEAD_D/2, HTOP + HEAD_T)
_w(DIM_W)
pdf.line(_hx, _hy, _hx + 10, _hy - 4); pdf.line(_hx + 10, _hy - 4, _hx + 14, _hy - 4)
text(_hx + 15, _hy - 3, f"M6 大扁头 Φ{HEAD_D:g}×{HEAD_T:g} 坐顶面 (灰线)", size=TXT_D)

_wx, _wy = fv(-(CH_W_S/2 + WEB_S/2), CH_H_S * 0.5)                  # 左侧护套段那条肉 (孔整个在护套段); 引注放左下
_w(DIM_W)
pdf.set_fill_color(0, 0, 0); pdf.circle(_wx, _wy, 0.6, style="F")
pdf.line(_wx, _wy, 60, 96); pdf.line(60, 96, 56, 96)
text(55, 95, f"孔壁到槽壁 {f2(WEB_S)} (护套段, 最薄处)", size=TXT_D, anchor="end")
text(55, 101, f"螺杆离接头 {f2(SHANK_GAP)}", size=TXT_I, anchor="end")

# ===== LEFT VIEW, FULL SECTION (3:1) — 沿 X=0 剖, 沿 +X 看: 纸面水平 = -Y (堵头/出线端在左) =====
sx0 = 352.0
_ymid = (Y_OPEN + Y_END) / 2
def sv(y, z): return (sx0 - (y - _ymid) * S, fy - z * S)

text(sx0, 33, "C-C (全剖)  Section (3:1)   沿对称面 X=0 剖, 沿 +X 看", size=TXT_L, anchor="middle")

hatch_rect(sv(Y_OPEN, HTOP), sv(Y_STEP, CH_H_B))     # 顶板 本体段
hatch_rect(sv(Y_STEP, HTOP), sv(Y_CAPI, CH_H_S))     # 顶板 护套段
hatch_rect(sv(Y_CAPI, HTOP), sv(Y_END, U_TOP))       # 堵头: X=0 过中间 U 口, 口顶以下没料
phantom()
polyline([sv(Y_OPEN, BODY_LIFT), sv(Y_OPEN, BODY_LIFT + BODY_H), sv(Y_XSTEP, BODY_LIFT + BODY_H), sv(Y_XSTEP, SHEATH_H),
          sv(Y_CAPI, SHEATH_H), sv(Y_CAPI, 0), sv(Y_XSTEP, 0), sv(Y_XSTEP, BODY_LIFT)], w=0.30)   # 本体 + 护套
rect(sv(Y_OPEN, -BASE_T), sv(Y_END, 0), w=0.30)     # 件 2 底板
rect(sv(BOSS_Y0, 0), sv(BOSS_Y1, BOSS_T), w=0.30)    # 件 2 凸台
rect(sv(REAR_RIM_Y0, 0), sv(Y_END, LEDGE_H), w=0.30)   # 件 2 后边框 (X=0 在中间缺口, 削到 1.4)
rect(sv(REAR_RIM_Y0, LEDGE_H), sv(Y_END, RIM_H), w=0.30)   # 剖面后方: 缺口侧壁 (1.4..2)
solid()
polyline([sv(Y_OPEN, HTOP), sv(Y_END, HTOP), sv(Y_END, U_TOP), sv(Y_CAPI, U_TOP), sv(Y_CAPI, CH_H_S),
          sv(Y_STEP, CH_H_S), sv(Y_STEP, CH_H_B), sv(Y_OPEN, CH_H_B)])            # 剖面轮廓 (阶梯槽顶)
polyline([sv(Y_END, U_TOP), sv(Y_END, STEP_H), sv(Y_CAPI, STEP_H), sv(Y_CAPI, U_TOP)], closed=False)   # 剖面后方 U 口侧壁 (压块到台阶顶 2)
polyline([sv(Y_OPEN, CH_H_B), sv(Y_OPEN, STEP_H), sv(STEP_Y1, STEP_H), sv(STEP_Y1, 0), sv(REAR_STEP_Y0, 0),
          sv(REAR_STEP_Y0, STEP_H), sv(Y_CAPI, STEP_H)], closed=False)          # 剖面后方可见: 槽侧壁下沿 + 开口端 / 后边台阶
pdf.line(*sv(Y_STEP, 0), *sv(Y_STEP, CH_H_B))                                   # 本体段壁 (5.9) 到护套段壁 (6.15) 的台阶棱
center()
pdf.line(*sv(HOLE_Y, -BASE_T - 0.5), *sv(HOLE_Y, HTOP + 1.5))
solid()
_BW, _BTOP = 2.0, CH_H_S + 0.8                                                  # = 详图 B 的实际范围 (Y_STEP ± 2, z 0..6.1)
_w(0.25); rect(sv(Y_STEP + _BW, _BTOP), sv(Y_STEP - _BW, 0), w=0.25)
text(sv(Y_STEP - _BW, 0)[0] + 1.0, sv(0, HTOP)[1] - 2.0, "B", size=TXT_L)

hdim(sv(Y_END, 0)[0], sv(Y_CAPI, 0)[0], sv(0, HTOP)[1], sv(0, HTOP)[1] - 10.0, f"堵头 {CAP_T:g}", label_at="right")
vdim(sv(0, U_TOP)[1], sv(0, 0)[1], sv(Y_END, 0)[0], sv(Y_END, 0)[0] - DIM_O1, f"{U_TOP:g}")
_sd = BASE_T * S                                     # 底板灰线占掉 z=0 以下 6 mm 纸面, 尺寸整体下移
hdim(sv(Y_CAPI, 0)[0], sv(Y_STEP, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + _sd + 6.0, f"{f2(Y_CAPI - Y_STEP)}")
hdim(sv(Y_STEP, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + _sd + 6.0, f"{f2(Y_STEP - Y_OPEN)}")
hdim(sv(Y_CAPI, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + _sd + 15.0, f"槽深 {MR_L:g}")
hdim(sv(Y_END, 0)[0], sv(Y_OPEN, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + _sd + 24.0, f2(DEPTH))
text(sv(Y_OPEN, 0)[0], sv(0, HTOP)[1] - 3.5, "开口端", size=TXT_D, anchor="middle")
text(sv((Y_CAPI + Y_END) / 2, 0)[0], sv(0, WIRE_ZC)[1] + 0.9, f"Φ{WIRE_D:g}", size=TXT_I, anchor="middle")   # 缺口底 1.4 ~ 口顶 3.9
text(sv(Y_END - 1.5, 0)[0], sv(0, HTOP)[1] - 3.5, "出线端", size=TXT_D, anchor="middle")
_s1 = "灰线: 开口侧本体 (凸台托) / 护套 (坐底板, 顶堵头 + 后边框) / 件 2 后边框"
_s2 = f"槽顶 {CH_H_S:g} / {f2(CH_H_B)} (详图 B); 出线孔 = 缺口底 {LEDGE_H:g} ~ 口顶 {U_TOP:g}, 内切 Φ{WIRE_D:g} (详图 A)"
for _t in (_s1, _s2):
    assert text_w(_t, TXT_I) <= 118, f"左视图说明太长: {text_w(_t, TXT_I):.1f}"
text(sx0, fy + 39, _s1, size=TXT_I, anchor="middle")
text(sx0, fy + 45, _s2, size=TXT_I, anchor="middle")

# ===== TOP VIEW (3:1) — X 水平, Y 竖直 (+Y 堵头在上) =====
tx0, ty0 = fx, 158.0
def tv(x, y): return (tx0 + x * S, ty0 - y * S)

text(tx0, 116, "俯视图  Top (3:1)   沿 -Z 看", size=TXT_L, anchor="middle")

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
    pdf.line(*tv(sx*STEP_X_IN, STEP_Y1), *tv(sx*STEP_X_IN, REAR_STEP_Y0))  # 压块底面台阶 (左右; 开口端角上与开口端台阶连成一片, 无棱)
    pdf.line(*tv(sx*CH_W_B/2, STEP_Y1), *tv(sx*STEP_X_IN, STEP_Y1))        # 压块底面台阶 (开口端)
    pdf.line(*tv(sx*CH_W_S/2, REAR_STEP_Y0), *tv(sx*STEP_X_IN, REAR_STEP_Y0))   # 压块底面台阶 (后边前沿)
for xc in WIRE_X:
    for e in (-WIRE_D/2, WIRE_D/2):
        pdf.line(*tv(xc + e, Y_CAPI), *tv(xc + e, Y_END))          # U 口两侧边
phantom()
for sx in (-1, 1):
    pdf.circle(*tv(sx*HX, HOLE_Y), HEAD_D/2 * S, style="D")
center()
pdf.line(*tv(-HALF_L - 2, HOLE_Y), *tv(HALF_L + 2, HOLE_Y))
for sx in (-1, 1):
    pdf.line(*tv(sx*HX, Y_END + 2), *tv(sx*HX, Y_OPEN - 2))
solid()

hdim(tv(-HX, 0)[0], tv(HX, 0)[0], tv(0, Y_OPEN)[1], tv(0, Y_OPEN)[1] + 12.0, f"{PITCH:g}")
hdim(tv(-HALF_L, 0)[0], tv(HALF_L, 0)[0], tv(0, Y_OPEN)[1], tv(0, Y_OPEN)[1] + 22.0, f"{L:g}")
vdim(tv(0, HOLE_Y)[1], tv(0, Y_OPEN)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + 12.0, f2(HOLE_Y_OPEN))
vdim(tv(0, Y_END)[1], tv(0, Y_OPEN)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + 22.0, f2(DEPTH))
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_END)[1] + 5.0, "堵头侧 (护套)", size=TXT_D, anchor="end")
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_OPEN)[1] - 2.0, "开口侧 (本体)", size=TXT_D, anchor="end")

_a = math.radians(135)
_px, _py = tv(-HX, HOLE_Y)
_px += HOLE_D/2 * S * math.cos(_a); _py -= HOLE_D/2 * S * math.sin(_a)
_w(DIM_W)
pdf.line(_px, _py, 50, 121); pdf.line(50, 121, 46, 121)
text(45, 122, f"2×Φ{HOLE_D:g} 通孔 (配 M6×{SCREW})", size=TXT_D, anchor="end")

# ===== 件 2: 垫片 (2:1) — 俯视: 底板 + 凸台 + 2 孔 =====
PS = 2.0
px0, py0 = 250.0, 77.0
_pyc = (Y_OPEN + Y_END) / 2
def pv(x, y): return (px0 + x * PS, py0 - (y - _pyc) * PS)

text(px0, 44.0, "件 2  垫片 mr30_shim (2:1)   俯视", size=TXT_L, anchor="middle")
_p1 = f"底板厚 {BASE_T:g} / 凸台 {BOSS_W:g}×{BOSS_L:g}×{BOSS_T:g} / 2×Φ{HOLE_D:g} 与压块孔同轴"
_p2 = f"止口高 {RIM_H:g}: 侧/前 宽 {RIM_W:g}, 后 宽 {REAR_RIM_W:g} (全宽); 出线处 {N_WIRE} 个缺口 宽 {WIRE_D:g} 削到 {LEDGE_H:g}"
for _t in (_p1, _p2):
    assert text_w(_t, TXT_I) <= 100, f"件 2 说明太长: {text_w(_t, TXT_I):.1f}"
text(px0, 49.5, _p1, size=TXT_I, anchor="middle")
text(px0, 54.5, _p2, size=TXT_I, anchor="middle")
solid()
rect(pv(-HALF_L, Y_END), pv(HALF_L, Y_OPEN))                         # 底板外形 = 压块外形
rect(pv(-BOSS_W/2, BOSS_Y1), pv(BOSS_W/2, BOSS_Y0))                  # 凸台 (顶面可见)
for sx in (-1, 1):
    pdf.line(*pv(sx*RIM_X_IN, RIM_Y1), *pv(sx*RIM_X_IN, REAR_RIM_Y0))   # 止口边框内缘 (左右; 开口端角上与前边框连成一片)
    pdf.line(*pv(sx*RIM_SEG_X0, RIM_Y1), *pv(sx*RIM_X_IN, RIM_Y1))    # 开口端边框内缘
    pdf.line(*pv(sx*RIM_SEG_X0, Y_OPEN), *pv(sx*RIM_SEG_X0, RIM_Y1))  # 开口端边框在槽口处断开
pdf.line(*pv(-RIM_X_IN, REAR_RIM_Y0), *pv(RIM_X_IN, REAR_RIM_Y0))   # 后边框内缘
for xc in WIRE_X:
    rect(pv(xc - WIRE_D/2, Y_END), pv(xc + WIRE_D/2, REAR_RIM_Y0))    # 出线缺口 (削到 1.4)
_w(GEOM_W)
for sx in (-1, 1):
    pdf.circle(*pv(sx*HX, HOLE_Y), HOLE_D/2 * PS, style="D")
center()
for sx in (-1, 1):
    pdf.line(*pv(sx*HX - HOLE_D/2 - 1.2, HOLE_Y), *pv(sx*HX + HOLE_D/2 + 1.2, HOLE_Y))
    pdf.line(*pv(sx*HX, HOLE_Y + HOLE_D/2 + 1.2), *pv(sx*HX, HOLE_Y - HOLE_D/2 - 1.2))
solid()
hdim(pv(-HALF_L, 0)[0], pv(HALF_L, 0)[0], pv(0, Y_OPEN)[1], pv(0, Y_OPEN)[1] + 7.0, f"{L:g}")
hdim(pv(-HX, 0)[0], pv(HX, 0)[0], pv(0, Y_OPEN)[1], pv(0, Y_OPEN)[1] + 16.0, f"{PITCH:g}")
vdim(pv(0, Y_END)[1], pv(0, Y_OPEN)[1], pv(HALF_L, 0)[0], pv(HALF_L, 0)[0] + 7.0, f2(DEPTH))
vdim(pv(0, HOLE_Y)[1], pv(0, Y_OPEN)[1], pv(-HALF_L, 0)[0], pv(-HALF_L, 0)[0] - 7.0, f2(HOLE_Y_OPEN))
hdim(pv(-BOSS_W/2, 0)[0], pv(BOSS_W/2, 0)[0], pv(0, BOSS_Y1)[1], pv(0, BOSS_Y1)[1] - 7.0, f"{BOSS_W:g}")
vdim(pv(0, BOSS_Y1)[1], pv(0, BOSS_Y0)[1], pv(-BOSS_W/2, 0)[0], pv(-BOSS_W/2, 0)[0] - 5.0, f"{BOSS_L:g}")

# ===== DETAIL B (8:1) — 槽台阶处 Z 向堆叠, 同左视图方向 (+Y 护套在左, -Y 本体在右) =====
BS = 8.0
bx0, by0 = 248.0, 189.0
BW = 2.0
B_TOP = CH_H_S + 0.8
def db(y, z): return (bx0 - (y - Y_STEP) * BS, by0 - z * BS)

text(bx0, 131, "详图 B (8:1)   槽台阶 Z 向堆叠", size=TXT_L, anchor="middle")

_yl, _yr = Y_STEP + BW, Y_STEP - BW
hatch_rect(db(_yl, B_TOP), db(Y_STEP, CH_H_S))
hatch_rect(db(Y_STEP, B_TOP), db(_yr, CH_H_B))
phantom()
polyline([db(_yl, SHEATH_H), db(Y_XSTEP, SHEATH_H), db(Y_XSTEP, BODY_LIFT + BODY_H), db(_yr, BODY_LIFT + BODY_H)],
         closed=False, w=0.30)                                           # 接头顶面 (护套 5.3 -> 本体 5.05)
polyline([db(Y_XSTEP, 0), db(Y_XSTEP, BODY_LIFT), db(_yr, BODY_LIFT)], closed=False, w=0.30)   # 护套前端面 + 本体底面
polyline([db(BOSS_Y1, 0), db(BOSS_Y1, BOSS_T), db(_yr, BOSS_T)], closed=False, w=0.30)        # 件 2 凸台
solid()
polyline([db(_yl, CH_H_S), db(Y_STEP, CH_H_S), db(Y_STEP, CH_H_B), db(_yr, CH_H_B)], closed=False)   # 槽顶
_w(0.6)
pdf.line(*db(_yl, 0), *db(_yr, 0))                                        # 垫片底板顶面 (z=0)
_w(0.20)
_wave = [db(_yl - i * (2 * BW) / 40, B_TOP + 0.08 * math.sin(i / 40 * 2 * math.pi * 2)) for i in range(41)]
for a, b in zip(_wave[:-1], _wave[1:]):
    pdf.line(*a, *b)
text(db(_yl, 0)[0], by0 + 4.5, "护套段", size=TXT_I, anchor="start")
text(db(_yl, 0)[0], by0 + 9.5, "垫片底板顶面", size=TXT_I, anchor="start")

vdim(db(_yl, CH_H_S)[1], db(_yl, 0)[1], db(_yl, 0)[0], db(_yl, 0)[0] - 9.0, f"{CH_H_S:g}")
vdim(db(_yr, CH_H_B)[1], db(_yr, 0)[1], db(_yr, 0)[0], db(_yr, 0)[0] + 9.0, f2(CH_H_B))
_w(DIM_W)
_p1 = db(Y_STEP + 1.2, CH_H_S)
pdf.line(*_p1, _p1[0] - 5, 138.5); pdf.line(_p1[0] - 5, 138.5, _p1[0] - 8, 138.5)
text(_p1[0] - 8.5, 139.5, "护套顶贴合", size=TXT_I, anchor="end")
_p2 = db(Y_STEP - 1.2, CH_H_B)
pdf.line(*_p2, _p2[0] + 5, 138.5); pdf.line(_p2[0] + 5, 138.5, _p2[0] + 8, 138.5)
text(_p2[0] + 8.5, 139.5, "本体顶贴合", size=TXT_I)
_p3 = db((BOSS_Y1 + _yr) / 2 - 0.3, BOSS_T / 2)
pdf.set_fill_color(0, 0, 0); pdf.circle(*_p3, 0.5, style="F")
text(_p3[0] - 1.5, by0 + 4.5, "本体段", size=TXT_I, anchor="end")
pdf.line(*_p3, _p3[0] + 4, 197.5); pdf.line(_p3[0] + 4, 197.5, _p3[0] + 7, 197.5)
text(_p3[0] + 7.5, 198.5, f"凸台 {BOSS_T:g} (件 2)", size=TXT_I)

# ===== DETAIL A (6:1) — U 型出线口, 沿 +Y 看: 护套段槽截面 + 堵头内面 =====
DS = 6.0
dx0, dy0 = 355.0, 185.0
def da(x, z): return (dx0 + x * DS, dy0 - z * DS)

text(dx0, 128, f"详图 A (6:1)   堵头出线口 (沿 +Y 看, 实线槽口 {CH_W_B:g})", size=TXT_L, anchor="middle")

phantom()
polyline([da(*q) for q in rear_rim_top(-CH_W_B/2, CH_W_B/2)], closed=False, w=0.30)   # 件 2 后边框 (高 2, 出线处缺口 1.4, 先画)
pdf.line(*da(-CH_W_B/2, 0), *da(CH_W_B/2, 0))                                        # 底板顶面
hidden()
polyline([da(*p) for p in [(-CH_W_S/2, 0.0), (-CH_W_S/2, CH_H_S), (CH_W_S/2, CH_H_S), (CH_W_S/2, 0.0)]], closed=False, w=0.30)   # 护套段槽 12.3 (被本体段槽口挡住)
solid()
polyline([da(*p) for p in [(-CH_W_B/2, 0.0), (-CH_W_B/2, CH_H_B), (CH_W_B/2, CH_H_B), (CH_W_B/2, 0.0)]], closed=False)   # 本体段槽口 11.8 × 5.05 (可见)
polyline([da(*p) for p in cap_face_edge(CH_W_B, STEP_H)], closed=False, w=GEOM_W)   # 压块堵头面从 z=2 起
center()
for xc in WIRE_X:
    pdf.line(*da(xc, -1.0), *da(xc, U_TOP + 0.6))
pdf.line(*da(WIRE_X[0] - WIRE_D/2 - 0.6, WIRE_ZC), *da(WIRE_X[-1] + WIRE_D/2 + 0.6, WIRE_ZC))
solid()

_ceil = da(0, CH_H_S)[1]
hdim(da(WIRE_X[0], 0)[0], da(WIRE_X[1], 0)[0], da(0, U_TOP)[1], _ceil - 7.0, f"{WIRE_PITCH:g}")
hdim(da(WIRE_X[0], 0)[0], da(WIRE_X[-1], 0)[0], da(0, U_TOP)[1], _ceil - 16.0, f"{WIRE_PITCH * (N_WIRE-1):g}")
_yb = da(0, 0)[1] + 12.0
hdim(da(-CH_W_S/2, 0)[0], da(WIRE_X[0] - WIRE_D/2, 0)[0], da(0, LEDGE_H)[1], _yb, f2(U_SIDE), outside=True)
hdim(da(WIRE_X[0] + WIRE_D/2, 0)[0], da(WIRE_X[1] - WIRE_D/2, 0)[0], da(0, LEDGE_H)[1], _yb, f2(U_RIB), outside=True)
hdim(da(WIRE_X[-1] - WIRE_D/2, 0)[0], da(WIRE_X[-1] + WIRE_D/2, 0)[0], da(0, LEDGE_H)[1], _yb, f"{WIRE_D:g}")
_xr = da(CH_W_S/2, 0)[0]
vdim(da(0, LEDGE_H)[1], da(0, 0)[1], da(WIRE_X[-1] + WIRE_D/2, 0)[0], _xr + 9.0, f"{LEDGE_H:g}", xg2=da(CH_W_B/2, 0)[0])   # 缺口底
_xl = da(-CH_W_S/2, 0)[0]
_xu = da(WIRE_X[0] - WIRE_D/2, 0)[0]          # 左 U 口左直边: 两条底边界线都从这里往左, 不横穿 U 口
vdim(da(0, WIRE_ZC)[1], da(0, 0)[1], _xu, _xl - 9.0, f"{WIRE_ZC:g}")
vdim(da(0, U_TOP)[1], da(0, 0)[1], da(WIRE_X[0], 0)[0], _xl - 22.0, f"{U_TOP:g}", xg2=_xu)
_a = math.radians(45)
_rx, _ry = da(WIRE_X[-1] + WIRE_D/2 * math.cos(_a), WIRE_ZC + WIRE_D/2 * math.sin(_a))
_w(DIM_W)
pdf.line(_rx, _ry, 404, 150); pdf.line(404, 150, 408, 150)
text(412, 147.5, f"R{WIRE_D/2:g} (Φ{WIRE_D:g})", size=TXT_D, anchor="end")
text(dx0, 204.0, f"灰线 = 件 2 后边框 (高 {RIM_H:g}), 出线处削到 {LEDGE_H:g} 平底, 与 U 口合成内切 Φ{WIRE_D:g} 的孔", size=TXT_I, anchor="middle")

# ===== 说明 (左下) =====
NX, NY = 20, 211
NOTE_MAX_X = 228.0
text(NX, NY, "说明 / Notes", size=TXT_L)
notes = [
    f"1) 接头 (用户 09-16) {MR_L:g} 含护套: 前 {BODY_L:g} 本体 {BODY_W:g}×{BODY_H:g} 在开口端, 后 {SHEATH_L:g} 护套 {SHEATH_W:g}×{SHEATH_H:g} 在堵头端; 阶梯槽配合间隙/过盈 0。",
    f"2) 件 2 = 底板 {L:g}×{f2(DEPTH)}×{BASE_T:g} + 凸台 {BOSS_W:g}×{BOSS_L:g}×{BOSS_T:g} + 2×Φ{HOLE_D:g}; 止口四边: 侧/前 宽 {RIM_W:g}, 后 宽 {REAR_RIM_W:g}, 高 {RIM_H:g} (前边槽口断开)。",
    f"3) 出线: U 口 Φ{WIRE_D:g} 圆心 {WIRE_ZC:g} + 后边框缺口 宽 {WIRE_D:g} 削到 {LEDGE_H:g} 平底, 合成内切 Φ{WIRE_D:g} 出线孔, 线零余量。",
    f"4) 嵌套: 压块底切台阶 (侧/前 {STEP_W:g}, 后 {REAR_RIM_W + ASSY_CLR:g}, 高 {STEP_H:g}), 竖直面留 {ASSY_CLR:g}、高度贴合; 组合外形 {L:g}×{f2(DEPTH)}×{f2(STACK_H)} 长方体。",
    f"5) 外表面只有 2×M6 孔、开口端接头口、3 个出线孔; 插入靠堵头 + 后边框, 拔出靠护套顶台阶。",
    f"6) 孔壁到槽壁 {f2(WEB_S)} (护套段, 最薄处); 侧台阶到孔 {f2(STEP_HOLE_WEB)}; ※ 后台阶到 M6 孔只剩 {REAR_HOLE_WEB:.2f} (底部 {STEP_H:g} 高内); 孔心距开口面 {f2(HOLE_Y_OPEN)} 待定。",
    f"7) 层高: 推荐 0.2 (本体段松 0.1, 其余整层); 不要用 0.25 (出线通道少 0.2)。件高 {f2(HTOP)}; PLA 约 {VOL*1.24e-3:.1f} + {SHIM_VOL*1.24e-3:.1f} g。",
    f"8) 装配: 底板放板上 -> 接头放上, 线落进缺口 -> 压块扣下 (止口卡住) -> M6×{SCREW} 穿两件 (旋入 {ENG:.1f}, 距板底 {PLATE_T-ENG:.1f})。",
]
for i, s in enumerate(notes):
    assert NX + text_w(s, TXT_N) <= NOTE_MAX_X, f"说明第 {i+1} 行太长: {NX + text_w(s, TXT_N):.1f} > {NOTE_MAX_X}"
    text(NX, NY + 6.5 + i * 5.2, s, size=TXT_N)

# ===== 尺寸来源 / 待定 (右下) =====
RX, RY = 236, 211
RX_MAX = 410.0
text(RX, RY, "MR30 尺寸来源 / 待定项", size=TXT_L)
src = [
    f"用户 09-16: {SHEATH_W:g}×{SHEATH_H:g}×{MR_L:g} (含护套), 前 {BODY_L:g} 宽厚各小 0.5 (单边 {BODY_STEP:g})。",
    "用户附图 MR30-M (无护套): 13.40 长 / 12.30 高 / 5.30 厚, 端面跑道形。",
    "针距 3.50 取自 Amass 官方目录; 线径 2.5 用户给 (U 口零余量)。",
    "建模按矩形; 实物端面跑道形, 台肩实际贴合面约为矩形的一半。",
    "本件按公头 MR30-M; 母头 MR30-FB 全长 14.40, 锁母头需改。",
    f"※ 待用户定: 孔心距开口面 {f2(HOLE_Y_OPEN)} (XT60 为 12.5); 后台阶到孔仅 {REAR_HOLE_WEB:.2f}。",
]
for i, s in enumerate(src):
    assert RX + text_w(s, TXT_N) <= RX_MAX, f"来源第 {i+1} 行太长: {RX + text_w(s, TXT_N):.1f} > {RX_MAX}"
    text(RX, RY + 6.5 + i * 5.0, s, size=TXT_N)

# ===== Title block (3 行) =====
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 27
tb_y = PAGE_H - 12 - tb_h
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + 9, tb_x + tb_w, tb_y + 9)
pdf.line(tb_x, tb_y + 18, tb_x + tb_w, tb_y + 18)
text(tb_x + 4, tb_y + 6, "结构件 — MR30 电源/电机接头压块 (MR30 Clamp v2, 阶梯槽 间隙/过盈全 0) + 件 2 底板垫片 (四边止口嵌套)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 3:1 (主, 左剖, 俯), 2:1 (件 2), 6:1 (详图 A), 8:1 (详图 B)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"{L:g}×{f2(DEPTH)}×{f2(HTOP)} / 阶梯槽 {CH_W_B:g}×{f2(CH_H_B)} (开口) + {CH_W_S:g}×{CH_H_S:g} (堵头) / 堵头 {CAP_T:g} + {N_WIRE}×U 口 Φ{WIRE_D:g} @ {WIRE_PITCH:g} 中心高 {WIRE_ZC:g} / "
     f"2×Φ{HOLE_D:g} @ {PITCH:g} / 配 M6×{SCREW} / 垫片 底板 {BASE_T:g} + 止口 侧前 {RIM_W:g} 后 {REAR_RIM_W:g} 高 {RIM_H:g} / 嵌套间隙 {ASSY_CLR:g} / PLA/PETG / mm",
     size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-16  /  pov3d / models / mr30_clamp_12p3x5p3x15p4 / *.stl (压块 + mr30_shim)",
     size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 23.5,
     f"接头尺寸来源: 用户 09-16 给定 {SHEATH_W:g}×{SHEATH_H:g}×{MR_L:g} (含护套), 前 {BODY_L:g} 本体单边小 {BODY_STEP:g}; 线径 {WIRE_OD:g} 用户给; 针距 3.50 Amass 官方   "
     f"※ 待定: 孔心到开口面 {f2(HOLE_Y_OPEN)}; 后台阶到 M6 孔仅 {REAR_HOLE_WEB:.2f}",
     size=TXT_I)

out = Path(__file__).with_name("mr30_clamp_12p3x5p3x15p4_drawing.pdf")
try:
    pdf.output(str(out))
except PermissionError:                     # PDF 在阅读器里开着
    out = out.with_suffix(".NEW.pdf")
    pdf.output(str(out))
print(f"wrote {out}")
