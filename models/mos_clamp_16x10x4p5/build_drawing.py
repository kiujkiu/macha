"""
A3 landscape 2D engineering drawing for mos_clamp_16x10x4p5 (MOS 管压块).

  1) 主视图 Front (2.5:1)     沿 +Y 看 (从开口端): 槽截面 10.4×4.5, 总高 7.5, 大扁头坐顶面 (灰)
  2) 左视图 全剖 (2.5:1)      沿对称面 X=0 剖, 沿 +X 看 (+Y 挡板在左): 顶板 + 挡板 L 形剖面, 槽深 24, MOS 顶挡板; 详图标记 A
  3) 俯视图 Top   (2.5:1)     2×Φ6.5 @ 25, 外形 38×26, 孔心距开口面 7, 盲槽 (虚线)
  4) 详图 A (5:1)             盲槽封闭端 (X=0 剖): 挡板 2 / 槽顶厚 3 / MOS 过盈 0
  5) 装配位置示意 (1:1)       板面 M6 网格 25; 照片方位: MOS 横放引脚朝左, 挡板在右, 两孔在 MOS 上下

件宽加到 26 后 4:1 的俯视图放不下 A3 → 三视图统一改 2.5:1。
剖切面为对称面且左视图按投影关系配置 → 按 GB 省略剖切符号。
盲槽是非通孔特征 → 按项目规则出详图 A (复核指出)。
⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (must match build_stl.py / mos_clamp_16x10x4p5.scad) =====
MOS_L, MOS_W, MOS_H = 16.0, 10.0, 4.5
SIDE_CLR    = 0.2
PRELOAD     = 0.0
PAD_T       = 0.0
T_TOP       = 3.0
PITCH       = 25.0
HOLE_D      = 6.5
END         = 6.5
HOLE_Y_OPEN = 7.0
CH_D        = 24.0
BAFFLE_T    = 2.0
HEAD_D, HEAD_T = 12.5, 2.6
PLATE_T  = 13.0
SQ6_WALL = 3.0

CH_W   = MOS_W + 2 * SIDE_CLR       # 10.4
CH_H   = MOS_H + PAD_T - PRELOAD    # 4.5
H      = CH_H + T_TOP               # 7.5
HX     = PITCH / 2                  # 12.5
HALF_L = HX + END                   # 19
L      = 2 * HALF_L                 # 38
Y_OPEN = -HOLE_Y_OPEN               # -7
Y_BAF  = Y_OPEN + CH_D              # 17
Y_END  = Y_BAF + BAFFLE_T           # 19
DEPTH  = Y_END - Y_OPEN             # 26
Y_LO, Y_HI = Y_OPEN, Y_END
WEB    = HX - HOLE_D / 2 - CH_W / 2 # 4.05
MOS_Y0 = Y_BAF - MOS_L              # 1
MOS_RECESS = MOS_Y0 - Y_OPEN        # 8
MOS_CY = Y_BAF - MOS_L / 2          # 9
LOWFOOT_CLASH = (CH_W / 2 + SQ6_WALL) - (HX - HEAD_D / 2)   # 1.95
VOL = L * DEPTH * H - CH_W * CH_D * CH_H - 2 * math.pi * (HOLE_D / 2) ** 2 * H

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

def hidden():  pdf.set_draw_color(0); pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(0.30)
def center():  pdf.set_draw_color(0); pdf.set_dash_pattern(dash=5.0, gap=1.2); _w(0.15)
def phantom(): pdf.set_draw_color(GRAY); pdf.set_dash_pattern(dash=3.0, gap=1.2); _w(0.30)
def solid():   pdf.set_draw_color(0); pdf.set_dash_pattern()

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "MOS 管压块  mos_clamp_16x10x4p5   (参考 saddle_clamp_sq6)", size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"压 TO-220 MOS {MOS_L:g}×{MOS_W:g}×{MOS_H:g} 到 M6 网格板 (节距 {PITCH:g})  ·  外形 {L:g}×{DEPTH:g}×{H:g} (槽深 {CH_D:g} + 挡板 {BAFFLE_T:g})  ·  "
     f"底部盲槽 {CH_W:g}×{CH_H:g}  ·  2×Φ{HOLE_D:g} @ {PITCH:g}  ·  M6 大扁头坐顶面",
     size=TXT_I, anchor="middle")

# ===== FRONT VIEW (2.5:1) — X 水平, Z 竖直; 从 -Y 开口端看, 槽口里是挡板内面, 其底边 Z=0 是可见轮廓 =====
S = 2.5
fx, fy = 125.0, 80.0
def fv(x, z): return (fx + x * S, fy - z * S)

text(fx, 33, "主视图  Front (2.5:1)   沿 +Y 看 (从开口端)   尺寸单位: mm", size=TXT_L, anchor="middle")

solid()
polyline([fv(-HALF_L, 0), fv(-CH_W/2, 0), fv(-CH_W/2, CH_H), fv(CH_W/2, CH_H),
          fv(CH_W/2, 0), fv(HALF_L, 0), fv(HALF_L, H), fv(-HALF_L, H)])
line(*fv(-CH_W/2, 0), *fv(CH_W/2, 0), GEOM_W)       # 挡板内面底边 (盲槽口下沿, 复核指出漏画)
hidden()
for sx in (-1, 1):
    for e in (-HOLE_D/2, HOLE_D/2):
        pdf.line(*fv(sx*HX + e, 0), *fv(sx*HX + e, H))
center()
for sx in (-1, 1):
    pdf.line(*fv(sx*HX, -1.2), *fv(sx*HX, H + HEAD_T + 1.2))
pdf.line(*fv(0, -1.2), *fv(0, H + 1.2))
phantom()
for sx in (-1, 1):
    rect(fv(sx*HX - HEAD_D/2, H), fv(sx*HX + HEAD_D/2, H + HEAD_T), w=0.30)
solid()

vdim(fv(0, H)[1], fv(0, 0)[1], fv(-HALF_L, 0)[0], fv(-HALF_L, 0)[0] - DIM_O1, f"{H:g}")
vdim(fv(0, CH_H)[1], fv(0, 0)[1], fv(-CH_W/2, 0)[0], fv(-CH_W/2, 0)[0] + 5.0, f"{CH_H:g}")
hdim(fv(-CH_W/2, 0)[0], fv(CH_W/2, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"{CH_W:g}")

# 大扁头引注
_hx, _hy = fv(HX + HEAD_D/2, H + HEAD_T)
_w(DIM_W)
pdf.line(_hx, _hy, _hx + 12, _hy - 4); pdf.line(_hx + 12, _hy - 4, _hx + 16, _hy - 4)
text(_hx + 17, _hy - 3, f"M6 大扁头 Φ{HEAD_D:g}×{HEAD_T:g} 坐顶面 (灰线)", size=TXT_D)

# ===== LEFT VIEW, FULL SECTION (2.5:1) — 沿对称面 X=0 剖, 沿 +X 看: 纸面水平 = -Y (挡板 +Y 在左) =====
sx0 = 310.0
_ymid = (Y_LO + Y_HI) / 2
def sv(y, z): return (sx0 - (y - _ymid) * S, fy - z * S)

text(sx0, 33, "左视图 (全剖)  Section (2.5:1)   沿对称面 X=0 剖, 沿 +X 看", size=TXT_L, anchor="middle")

# 剖面 = 顶板 (Y 全宽, Z CH_H..H) + 挡板 (Y Y_BAF..Y_END, Z 0..CH_H), 拼成 L 形
hatch_rect(sv(Y_LO, H), sv(Y_HI, CH_H))
hatch_rect(sv(Y_BAF, CH_H), sv(Y_HI, 0))
phantom()
rect(sv(MOS_Y0, PAD_T), sv(Y_BAF, PAD_T + MOS_H), w=0.30)                    # MOS 顶住挡板 (先画, 让黑轮廓盖住重合边)
solid()
rect(sv(Y_LO, 0), sv(Y_HI, H))                                   # 外轮廓 (剖面 + 剖面后方的实体)
polyline([sv(Y_LO, CH_H), sv(Y_BAF, CH_H), sv(Y_BAF, 0)], closed=False)   # 槽顶 + 挡板内面
center()
pdf.line(*sv(0, -1.2), *sv(0, H + 1.2))                          # 孔轴线 (孔在剖面后方)
solid()

# 详图 A 标记 (盲槽封闭端)
_cax, _cay = sv(Y_BAF - 1.0, CH_H * 0.85)
_w(0.25); pdf.circle(_cax, _cay, 13.0, style="D")
text(_cax - 17.0, _cay - 9.0, "A", size=TXT_L)

hdim(sv(Y_BAF, 0)[0], sv(Y_LO, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + DIM_O1, f"槽深 {CH_D:g}")
hdim(sv(Y_HI, 0)[0], sv(Y_LO, 0)[0], sv(0, 0)[1], sv(0, 0)[1] + DIM_O2, f"{DEPTH:g}")
vdim(sv(0, PAD_T + MOS_H)[1], sv(0, PAD_T)[1], sv(MOS_Y0, 0)[0], sv(Y_LO, 0)[0] + 12.0, f"MOS {MOS_H:g}")   # 放到开口面外, 不挤在槽里
text(sv(Y_LO, H)[0], sv(0, H)[1] - 3.5, "开口端 (引脚侧)", size=TXT_D, anchor="middle")
text(sx0, fy + DIM_O2 + 12, f"舌片端顶住挡板时, 引脚端缩进开口 {MOS_RECESS:g}   (灰线 = MOS)", size=TXT_I, anchor="middle")
text(sx0, fy + DIM_O2 + 18, f"槽高 {CH_H:g} = MOS {MOS_H:g}" + (f" + 垫 {PAD_T:g}" if PAD_T else "")
     + (f" - 过盈 {PRELOAD:g}" if PRELOAD else " (过盈 0, 两脚贴板)") + "   剖面线 = 顶板 + 挡板",
     size=TXT_I, anchor="middle")

# ===== TOP VIEW (2.5:1) — X 水平, Y 竖直 (+Y 挡板在上) =====
tx0, ty0 = fx, 165.0
def tv(x, y): return (tx0 + x * S, ty0 - y * S)

text(tx0, 110, "俯视图  Top (2.5:1)   沿 -Z 看", size=TXT_L, anchor="middle")

solid()
rect(tv(-HALF_L, Y_HI), tv(HALF_L, Y_LO))
_w(GEOM_W)
for sx in (-1, 1):
    pdf.circle(*tv(sx*HX, 0), HOLE_D/2 * S, style="D")
hidden()
polyline([tv(-CH_W/2, Y_LO), tv(-CH_W/2, Y_BAF), tv(CH_W/2, Y_BAF), tv(CH_W/2, Y_LO)],
         closed=False, w=0.30)                                   # 底部盲槽 (止于挡板)
phantom()
for sx in (-1, 1):
    pdf.circle(*tv(sx*HX, 0), HEAD_D/2 * S, style="D")           # 头投影
center()
pdf.line(*tv(-HALF_L - 1.5, 0), *tv(HALF_L + 1.5, 0))
for sx in (-1, 1):
    pdf.line(*tv(sx*HX, Y_HI + 1.5), *tv(sx*HX, Y_LO - 1.5))
solid()

hdim(tv(-HX, 0)[0], tv(HX, 0)[0], tv(0, Y_LO)[1], tv(0, Y_LO)[1] + DIM_O1, f"{PITCH:g}")
hdim(tv(-HALF_L, 0)[0], tv(HALF_L, 0)[0], tv(0, Y_LO)[1], tv(0, Y_LO)[1] + DIM_O2, f"{L:g}")
vdim(tv(0, 0)[1], tv(0, Y_LO)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + DIM_O1, f"{HOLE_Y_OPEN:g}")
vdim(tv(0, Y_HI)[1], tv(0, Y_LO)[1], tv(HALF_L, 0)[0], tv(HALF_L, 0)[0] + DIM_O2, f"{DEPTH:g}")
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_HI)[1] + 5.0, "挡板侧", size=TXT_D, anchor="end")
text(tv(-HALF_L, 0)[0] - 2.0, tv(0, Y_LO)[1] - 2.0, "开口侧", size=TXT_D, anchor="end")

# 孔引注
_a = math.radians(45)
_px, _py = tv(HX, 0)
_px += HOLE_D/2 * S * math.cos(_a); _py -= HOLE_D/2 * S * math.sin(_a)
_w(DIM_W)
pdf.line(_px, _py, 200, 108); pdf.line(200, 108, 205, 108)
text(206, 109, f"2×Φ{HOLE_D:g} 通孔 (配 M6)", size=TXT_D)

# ===== DETAIL A (5:1) — 盲槽封闭端, X=0 剖面 (方位同左视图: +Y 在左), 右侧断开 =====
DS = 5.0
dx0, dy0 = 372.0, 222.0
Y_BRK = Y_BAF - 6.0                  # 断裂处 Y
def dA(y, z): return (dx0 - (y - (Y_END - 4.0)) * DS, dy0 - z * DS)

text(dx0 + 3, 172, "详图 A (5:1)   盲槽封闭端 (X=0 剖)", size=TXT_L, anchor="middle")

hatch_rect(dA(Y_BRK, H), dA(Y_END, CH_H))
hatch_rect(dA(Y_BAF, CH_H), dA(Y_END, 0))
phantom()
polyline([dA(Y_BRK, PAD_T + MOS_H), dA(Y_BAF, PAD_T + MOS_H), dA(Y_BAF, PAD_T), dA(Y_BRK, PAD_T)], closed=False, w=0.30)   # MOS 端部 (先画, 断口侧不封边)
solid()
polyline([dA(Y_BRK, H), dA(Y_END, H), dA(Y_END, 0), dA(Y_BAF, 0), dA(Y_BAF, CH_H), dA(Y_BRK, CH_H)],
         closed=False, w=GEOM_W)
_w(0.20)
_bx = dA(Y_BRK, 0)[0]
_wave = [(_bx + 0.8 * math.sin(i * 0.9), dA(0, -0.6 + i * 0.25)[1]) for i in range(int((H + 1.2) / 0.25) + 1)]
for a, b in zip(_wave[:-1], _wave[1:]):
    pdf.line(*a, *b)

hdim(dA(Y_END, 0)[0], dA(Y_BAF, 0)[0], dA(0, 0)[1], dA(0, 0)[1] + 10.0, f"挡板 {BAFFLE_T:g}", label_at="right", outside=True)
vdim(dA(0, H)[1], dA(0, CH_H)[1], _bx + 1.5, _bx + 10.0, f"{T_TOP:g}")
text(dx0 + 3, 242, (f"MOS(+垫) 顶面比槽顶高 {PRELOAD:g} (过盈)" if PRELOAD else "MOS 顶面与槽顶齐平 (过盈 0, 两脚贴板)"),
     size=TXT_I, anchor="middle")

# ===== 装配位置示意 (1:1) — 照片方位: MOS 横放引脚朝左, 挡板在右, 两孔在 MOS 上下 =====
# 纸面 x 对应件的 Y (+Y 挡板朝右), 纸面 y 对应件的 X (两孔连线竖直)
KS = 1.0
kx, ky = 282.0, 190.0
def kv(u, v): return (kx + u * KS, ky - v * KS)

text(kx, 160, f"装配位置示意 (1:1)   板面 M6 网格节距 {PITCH:g}", size=TXT_L, anchor="middle")

for gx in (-PITCH, 0.0, PITCH):
    for gy in (-HX, HX):
        if gx == 0:
            solid(); _w(GEOM_W)
        else:
            pdf.set_draw_color(GRAY); pdf.set_dash_pattern(); _w(0.30)
        pdf.circle(*kv(gx, gy), HOLE_D/2 * KS, style="D")
solid()
rect(kv(Y_LO, HALF_L), kv(Y_HI, -HALF_L), w=0.40)               # 压块外形
phantom()
for sy in (-1, 1):
    pdf.circle(*kv(0, sy*HX), HEAD_D/2 * KS, style="D")          # 大扁头
rect(kv(MOS_Y0, MOS_W/2), kv(Y_BAF, -MOS_W/2), w=0.30)           # MOS 顶住挡板
for ly in (-2.54, 0.0, 2.54):
    pdf.line(*kv(MOS_Y0, ly), *kv(Y_LO - 5, ly))                 # 引脚 (从槽里穿出开口)
solid()

text(kv(Y_LO - 5, 0)[0] - 1.5, ky + 1.0, "引脚 → PCB", size=TXT_D, anchor="end")
_mx, _my = kv(MOS_Y0, -MOS_W/2)
_w(DIM_W)
pdf.line(_mx, _my, _mx - 10, 222); pdf.line(_mx - 10, 222, _mx - 14, 222)
text(_mx - 15, 223, f"MOS {MOS_L:g}×{MOS_W:g}×{MOS_H:g} (灰虚线)", size=TXT_D, anchor="end")
text(kx, 234, f"挡板在右 (舌片侧); MOS 顶挡板时中心偏舌片侧 {MOS_CY:g}", size=TXT_D, anchor="middle")

# ===== 说明 =====
NX, NY = 25, 218
text(NX, NY, "说明 / Notes", size=TXT_L)
for i, s in enumerate([
    f"1) 为什么是平顶而不是 sq6 的低脚: 孔距 {PITCH:g} - 大扁头 Φ{HEAD_D:g} = 两头之间只剩 {PITCH-HEAD_D:g}, 放不下 MOS 宽 {MOS_W:g} + 两侧壁 (低脚方案头压壁 {LOWFOOT_CLASH:.2f});"
    f" 故两脚与顶面齐平, 头坐顶面。",
    f"2) 盲槽 {CH_W:g} × {CH_H:g} 深 {CH_D:g}: 宽度两侧各留 {SIDE_CLR:g} 间隙; 槽高 = MOS {MOS_H:g} + 垫 {PAD_T:g} - 过盈 {PRELOAD:g}。槽与孔之间肉 {WEB:.2f}。封闭端见详图 A。",
    f"3) 挡板: +Y 端厚 {BAFFLE_T:g}, 全长 {L:g} 全高 {H:g}。槽深 {CH_D:g} 比 MOS 长 {MOS_RECESS:g}: 舌片端顶住挡板时引脚端缩进开口 {MOS_RECESS:g}, 引脚要从槽里穿出; 不顶挡板则 MOS 可在槽里前后调 {MOS_RECESS:g}。",
    f"4) 螺丝: 推荐 M6×16 (旋入 {16-H:.1f}, 板厚 {PLATE_T:g} 不穿底); M6×12 可用 (旋入 {12-H:.1f}); M6×10 只旋入 {10-H:.1f} 不推荐。内六角圆柱头 Φ10 也能用。",
    f"5) 摆放: 孔心距开口面 {HOLE_Y_OPEN:g}; MOS 顶住挡板后中心在两孔连线往舌片侧 {MOS_CY:g}。照片里 MOS 约在格子正中 (引脚朝左): 压块锁 MOS 左边那列孔, MOS+PCB 左移约 {PITCH/2 - MOS_CY:g}。",
    "6) 压紧: 件很刚, 过盈取 0 让两脚贴板, 拧到底也压不坏封装 (复核实算: 0.2 过盈时脚落不到板上, 夹紧力全靠拧螺丝会压裂)。"
    "MOS 下垫导热硅胶垫时: PAD_T 改垫厚, PRELOAD 改垫允许的压缩量 (约垫厚 10-20%), 重生成。",
    f"7) 打印: 顶面贴床 (槽口朝上, 挡板竖直), 零支撑。实心 {VOL/1000:.2f} cm^3, PLA 约 {VOL*1.24e-3:.1f} g。",
]):
    text(NX, NY + 7 + i * 5.3, s, size=4.8)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "结构件 — MOS 管压块 (MOS Clamp, TO-220)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 2.5:1 (主, 左剖, 俯), 5:1 (详图 A), 1:1 (装配示意)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"{L:g}×{DEPTH:g}×{H:g} (槽深 {CH_D:g} + 挡板 {BAFFLE_T:g}) / 盲槽 {CH_W:g}×{CH_H:g} / 2×Φ{HOLE_D:g} @ {PITCH:g} / 材料 PLA/PETG  /  单位 mm",
     size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-14  /  pov3d / models / mos_clamp_16x10x4p5 / mos_clamp_16x10x4p5.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("mos_clamp_16x10x4p5_drawing.pdf")
try:
    pdf.output(str(out))
except PermissionError:                     # PDF 在阅读器里开着
    out = out.with_suffix(".NEW.pdf")
    pdf.output(str(out))
print(f"wrote {out}")
