"""
A3 drawing — rim_ring 外圈托盘环 v3 (2026-07-22, 承载盘并入 + 内凸台环).

几何与 models/rim_ring/build_stl.py 同步 (参数在下方复刻, 单一来源=build_stl.py):
  托盘环 Φ170/Φ50×5 (Z0..5) + 外唇 Φ170/Φ165×5.5 (Z5..10.5, 完整整圈)
  内凸台环 Φ80/Φ70×2.5 长在唇侧面上 (Z5..7.5), 装配时落 hub_disc 底板顶做径向定心
  扇形挖槽 R40..61 × -45°..-40°, 从唇侧面往下深 2 (Z3..5)
      (2026-07-22: 内径 35→40, 挖槽自内凸台环外缘起, 凸台环不再跨槽)
  16×Φ3.2 通孔 (8@PCD Φ60 + 8@PCD Φ155, 角度 22.5°+k·45°); 其中内圈+外圈
  202.5°/247.5° 共 4 孔从托盘承载面 (Z0) 加 Φ7.5×2.0 头沉孔 (内圈 2 颗螺丝头
  在 wifi 模块底下沉平 / 外圈 2 颗紧挨盒东侧)
  7 pi2hub 孔 + 4 wifi_shell 孔 (2026-07-22 定稿单组: 盒 XC 46→43 + 沿长边平移
  -13, 滑位方案作废): Φ3.2 通 + Φ4.2×4.5 铜螺母沉孔 (从唇侧 Z5 面往下,
  占 Z0.5..5, 托盘面留 0.5 台肩); 2×Φ4 通孔 @ (-10°,R72)/(-42.5°,R56)
注意: 零件系 Z0 托盘面 = 装配后朝上的承载面 (装配中绕 X 翻转使用)。

Views: 俯视 1:1 / 剖视 A–A 1:1 (沿 22.5°–202.5° 直径, 过两圈 Φ3.2 孔) /
       剖面 B–B 2:1 (沿 -42.5° 半径半剖, 过挖槽 + Φ4 孔 + 内凸台环) /
       详图 C 4:1 (沉孔) / 孔位表 ①②③。
GB first-angle, mm。
"""
import math
import os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (mirror of build_stl.py — 不要改这里, 改 build_stl.py 后同步) =====
BASE_ID, BASE_OD, BASE_H = 50.0, 170.0, 5.0          # 托盘环, Z0..5
RIM_ID, RIM_OD, RIM_H = 165.0, 170.0, 5.5            # 外唇, Z5..10.5 (整圈)
IBOSS_OD, IBOSS_ID, IBOSS_H = 80.0, 70.0, 2.5        # 内凸台环, 唇侧 Z5..7.5
NOTCH_R_MIN, NOTCH_R_MAX = 40.0, 61.0                # 扇形挖槽 (2026-07-22: 35→40)
NOTCH_A_S, NOTCH_A_E, NOTCH_DEPTH = -45.0, -40.0, 2.0    # Z3..5
TOTAL_H = BASE_H + RIM_H                             # 10.5
M3_DIAM = 3.2
INNER_PCD_R, OUTER_PCD_R = 30.0, 77.5                # PCD Φ60 / Φ155
HOLE_ANGLES = [22.5 + k * 45.0 for k in range(8)]
EXTRA_HOLE_D = 4.0
EXTRA_HOLES_POLAR = [(-10.0, 72.0), (-42.5, 56.0)]
EXTRA_HOLES = [(round(R * math.cos(math.radians(a)), 3),
                round(R * math.sin(math.radians(a)), 3))
               for (a, R) in EXTRA_HOLES_POLAR]
PI_THRU_D, PI_INSERT_D, PI_INSERT_DEEP = 3.2, 4.2, 4.5
CB_SHOULDER = BASE_H - PI_INSERT_DEEP                # 0.5 台肩 (托盘面侧)

# 7 pi2hub 孔位 (与 build_stl.py 同一公式: 盘系转 90°+偏移(-10,0), 组转 +135°, 翻转取 (x,-y))
PCB_ROT, PCB_OFF, PI_ROT_EXTRA = 90.0, (-10.0, 0.0), 135.0
def _rotp(pts, deg=PCB_ROT, off=PCB_OFF):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    return [(round(c*x - s_*y + off[0], 3), round(s_*x + c*y + off[1], 3)) for (x, y) in pts]
def _rot_o(pts, deg):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    return [(round(c*x - s_*y, 3), round(s_*x + c*y, 3)) for (x, y) in pts]
_PI_BASE = _rotp([(-47.0, 44.0), (0.0, 44.0), (47.0, 44.0),
                  (-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0)])
PI_HOLES = [(x, -y) for (x, y) in _rot_o(_PI_BASE, PI_ROT_EXTRA)]

# 4 wifi_shell 沿孔 (2026-07-22 定稿单组: 盒 XC 46→43 + 沿长边平移 -13;
# 三档滑位 11 孔方案作废。-15→-13: 最内孔沉孔边 r40.9, 距内凸台环 R40 留 0.9。
# 同公式: 装配系局部 → 转 135° → (x,-y))
WIFI_XC, WIFI_ROT = 43.0, 135.0
WIFI_SHIFTS = (-13.0,)
_WIFI_LOCAL = [(round(WIFI_XC - 46.4/2 + z, 3), round(y + dy, 3))
               for dy in WIFI_SHIFTS
               for z in (10.7, 35.7) for y in (43.3, -43.3)]
_WIFI_LOCAL = [(x, y) for (x, y) in _WIFI_LOCAL
               if math.hypot(x, y) <= 85.0 - 1.6 - 1.0]   # 孔边距盘边 ≥1
WIFI_HOLES = [(x, -y) for (x, y) in _rot_o(_WIFI_LOCAL, WIFI_ROT)]

# 4 个环孔螺丝头沉孔 (2026-07-22 晚: Φ6.5×2.2 ×2 改 Φ7.5×2.0 ×4): wifi 角落
# 的 4 颗 ring→hub 锁紧 M3 —— 内圈 R30 + 外圈 R77.5 的 202.5°/247.5° 各 2 孔,
# 从托盘承载面 (part Z0) 加头沉。内圈 2 颗在放平 wifi 模块肚子底下 (沉平才能
# 放模块), 外圈 2 颗紧挨盒东侧。其余 12 环孔头仍外露。
HEAD_CB_D, HEAD_CB_DEEP = 7.5, 2.0
HEAD_CB_ANGLES = (202.5, 247.5)
HEAD_CB_XY = [(round(r * math.cos(math.radians(a)), 3),
               round(r * math.sin(math.radians(a)), 3))
              for r in (INNER_PCD_R, OUTER_PCD_R) for a in HEAD_CB_ANGLES]

# sanity: 与 build_stl.py 2026-07-22 定稿输出核对
assert PI_HOLES[0] == (71.418, 4.95) and PI_HOLES[6] == (-38.537, 17.324)
assert WIFI_HOLES == [(-42.992, -0.141), (18.243, -61.377),
                      (-60.67, -17.819), (0.566, -79.055)]
assert HEAD_CB_XY == [(-27.716, -11.481), (-11.481, -27.716),
                      (-71.601, -29.658), (-29.658, -71.601)]

# ===== PDF setup =====
_font_paths = ["/mnt/c/Windows/Fonts/simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"]
FONT = next((p for p in _font_paths if os.path.exists(p)), None)
if FONT is None:
    raise FileNotFoundError("SimHei not found")

GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
PAGE_W, PAGE_H = 420.0, 297.0

pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False); pdf.add_page()
pdf.add_font("SimHei", "", FONT)

def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W): _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
    bx, by = tx - ARR_L*ux, ty - ARR_L*uy; px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx + ARR_W*px, by + ARR_W*py),
                 (bx - ARR_W*px, by - ARR_W*py)], style="F")
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    pdf.set_font("SimHei", "", size)
    if anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":  x -= pdf.get_string_width(s)
    if halo:
        sw, fh = pdf.get_string_width(s), pdf.font_size
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(x-0.4, y-fh*0.85, sw+0.8, fh*1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, angle_deg, size=TXT_D, anchor="middle", halo=False):
    pdf.set_font("SimHei", "", size); sw = pdf.get_string_width(s)
    with pdf.rotation(angle=angle_deg, x=cx, y=cy):
        dx = -sw/2 if anchor == "middle" else (-sw if anchor == "end" else 0)
        if halo:
            fh = pdf.font_size; pdf.set_fill_color(255, 255, 255)
            pdf.rect(cx+dx-0.4, cy-fh*0.85, sw+0.8, fh*1.1, style="F")
            pdf.set_fill_color(0, 0, 0)
        pdf.text(cx + dx, cy, s)
def _u(label, unit="mm"):
    s = str(label).strip()
    return s if (not s or unit in s or "°" in s) else f"{s} {unit}"
def hdim(x1, x2, yg, yd, label):
    label = _u(label)
    if yd > yg: ey1, ey2 = yg + EXT_GP, yd + EXT_OV
    else:       ey1, ey2 = yg - EXT_GP, yd - EXT_OV
    line(x1, ey1, x1, ey2, EXT_W_); line(x2, ey1, x2, ey2, EXT_W_)
    xl, xr = (x1, x2) if x1 < x2 else (x2, x1)
    if xr - xl >= 2*ARR_L + 1:
        line(xl, yd, xr, yd, DIM_W); arrow(xl, yd, -1, 0); arrow(xr, yd, 1, 0)
    else:
        e = ARR_L + 1.0
        line(xl - e, yd, xr + e, yd, DIM_W)
        arrow(xl, yd, 1, 0); arrow(xr, yd, -1, 0)
    text((xl + xr)/2, yd - 1.8, label, anchor="middle", halo=True)
def vdim(y1, y2, xg, xd, label):
    label = _u(label)
    if xd > xg: ex1, ex2, to = xg + EXT_GP, xd + EXT_OV,  4.0
    else:       ex1, ex2, to = xg - EXT_GP, xd - EXT_OV, -4.0
    line(ex1, y1, ex2, y1, EXT_W_); line(ex1, y2, ex2, y2, EXT_W_)
    yt, yb = (y1, y2) if y1 < y2 else (y2, y1)
    if yb - yt >= 2*ARR_L + 1:
        line(xd, yt, xd, yb, DIM_W); arrow(xd, yt, 0, -1); arrow(xd, yb, 0, 1)
    else:
        e = ARR_L + 1.0
        line(xd, yt - e, xd, yb + e, DIM_W)
        arrow(xd, yt, 0, 1); arrow(xd, yb, 0, -1)
    lh = pdf.get_string_width(label)
    if yb - yt >= lh + 1.0:
        rot_text(xd + to, (yt + yb)/2, label, 90, anchor="middle", halo=True)
    else:
        rot_text(xd + to, yb + (ARR_L + 1.0) + lh/2 + 1.0, label, 90,
                 anchor="middle", halo=True)
def note(xf, yf, xt, yt, label, anchor="start", size=TXT_I):
    line(xf, yf, xt, yt, EXT_W_); arrow(xf, yf, xf - xt, yf - yt)
    text(xt + (1.0 if anchor == "start" else -1.0), yt + 1.2, label,
         size=size, anchor=anchor, halo=True)
def cross(cx, cy, r=4.0):
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx - r, cy, cx + r, cy); pdf.line(cx, cy - r, cx, cy + r)
    pdf.set_dash_pattern(); _w(GEOM_W)
def circ(cx, cy, r, w=GEOM_W, dashed=False):
    if dashed: pdf.set_dash_pattern(dash=2.0, gap=1.2)
    _w(w); pdf.circle(cx, cy, r, style="D")
    if dashed: pdf.set_dash_pattern()

out_pdf = Path(__file__).with_name("rim_ring_drawing.pdf")

# ===== Frame & titles =====
_w(0.3); pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14, "POV 3D — rim_ring 外圈托盘环 v3 (承载盘并入 + 内凸台环)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20,
     f"托盘环 Φ{BASE_OD:g}/Φ{BASE_ID:g}×{BASE_H:g} (Z0..5) + 外唇 Φ{RIM_OD:g}/Φ{RIM_ID:g}×{RIM_H:g} "
     f"(Z5..10.5, 完整整圈) + 内凸台环 Φ{IBOSS_OD:g}/Φ{IBOSS_ID:g}×{IBOSS_H:g} (唇侧 Z5..7.5, 落 hub_disc 底板顶径向定心)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 25,
     f"扇形挖槽 R{NOTCH_R_MIN:g}..R{NOTCH_R_MAX:g} × {NOTCH_A_S:g}°..{NOTCH_A_E:g}° × 深 {NOTCH_DEPTH:g} / "
     f"16×Φ{M3_DIAM:g} 通 (PCD Φ60+Φ155, 4 孔加 Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 头沉) / 7 pi2hub + 4 wifi 沉孔 / 2×Φ{EXTRA_HOLE_D:g} — "
     "注意: 零件系 Z0 托盘面 = 装配后朝上的承载面 (装配绕 X 翻转)",
     size=TXT_I, anchor="middle")

# =====================================================================
# 俯视图 (1:1) — 从零件系 +Z (唇侧) 看; X 右, Y 上
# =====================================================================
TVX, TVY = 110.0, 152.0
def pv(x, y): return (TVX + x, TVY - y)

text(122, 31.5, "俯视图 (1:1) — 从零件系 +Z (唇侧) 看   尺寸单位: mm",
     size=TXT_L, anchor="middle")

# 中心线 (双向)
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.15)
pdf.line(*pv(0, -92), *pv(0, 92))
pdf.line(*pv(-92, 0), *pv(92, 0))
pdf.set_dash_pattern()

# 剖切线 A–A: 沿 22.5°–202.5° 直径
_c, _s = math.cos(math.radians(22.5)), math.sin(math.radians(22.5))
a1 = pv(93*_c, 93*_s); a2 = pv(-93*_c, -93*_s)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
pdf.line(*a1, *a2)
pdf.set_dash_pattern()
text(a1[0] + 1.5, a1[1] - 1.0, "A", size=6)
text(a2[0] - 4.5, a2[1] + 4.0, "A", size=6)
# 剖切线 B–B: 沿 -42.5° 半径 (半剖)
_cb, _sb = math.cos(math.radians(-42.5)), math.sin(math.radians(-42.5))
b2 = pv(93*_cb, 93*_sb)
pdf.set_dash_pattern(dash=6, gap=2); _w(0.20)
pdf.line(*pv(0, 0), *b2)
pdf.set_dash_pattern()
text(b2[0] + 1.5, b2[1] + 3.5, "B", size=6)
text(pv(6, -4)[0], pv(6, -4)[1], "B", size=6)

# 轮廓圆
ccx, ccy = pv(0, 0)
circ(ccx, ccy, BASE_OD/2)          # Φ170 外缘
circ(ccx, ccy, RIM_ID/2)           # Φ165 唇内缘
circ(ccx, ccy, IBOSS_OD/2)         # Φ80 内凸台环外
circ(ccx, ccy, IBOSS_ID/2)         # Φ70 内凸台环内
circ(ccx, ccy, BASE_ID/2)          # Φ50 中孔
# PCD 参考圆 (虚线)
pdf.set_dash_pattern(dash=2.5, gap=1.5); _w(0.15)
pdf.circle(ccx, ccy, INNER_PCD_R, style="D")
pdf.circle(ccx, ccy, OUTER_PCD_R, style="D")
pdf.set_dash_pattern(); _w(GEOM_W)

# 扇形挖槽轮廓 R40..61 (全部可见: 内缘 R40 = 内凸台环外缘, Φ80 圆已画)
def arc_pts(r, adeg0, adeg1, n=16):
    return [pv(r*math.cos(math.radians(adeg0 + i*(adeg1-adeg0)/n)),
               r*math.sin(math.radians(adeg0 + i*(adeg1-adeg0)/n)))
            for i in range(n + 1)]
def polyline(pts, w=GEOM_W, dashed=False):
    if dashed: pdf.set_dash_pattern(dash=2.0, gap=1.2)
    _w(w)
    for i in range(len(pts) - 1):
        pdf.line(*pts[i], *pts[i+1])
    if dashed: pdf.set_dash_pattern()
polyline(arc_pts(NOTCH_R_MAX, NOTCH_A_S, NOTCH_A_E))            # 外弧 R61
for a in (NOTCH_A_S, NOTCH_A_E):                                # 径向边 R40..61
    ca, sa_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    polyline([pv(NOTCH_R_MIN*ca, NOTCH_R_MIN*sa_), pv(NOTCH_R_MAX*ca, NOTCH_R_MAX*sa_)])

# 16×Φ3.2 两圈通孔
for a in HOLE_ANGLES:
    for R in (INNER_PCD_R, OUTER_PCD_R):
        hx, hy = pv(R*math.cos(math.radians(a)), R*math.sin(math.radians(a)))
        circ(hx, hy, M3_DIAM/2); cross(hx, hy, 3.2)
# 7 pi2hub + 4 wifi (Φ3.2 通 + Φ4.2 沉孔从唇侧开 → 俯视可见, 实线)
def marked_hole(x, y, tag, dx=2.4, dy=-2.0):
    hx, hy = pv(x, y)
    circ(hx, hy, PI_THRU_D/2); circ(hx, hy, PI_INSERT_D/2)
    cross(hx, hy, 4.2)
    text(hx + dx, hy + dy, tag, size=3.4)
for i, (x, y) in enumerate(PI_HOLES):
    marked_hole(x, y, f"P{i+1}")
for i, (x, y) in enumerate(WIFI_HOLES):
    dy = -2.8 if i == 0 else -2.0   # W1 标号稍抬, 避开水平中心线
    marked_hole(x, y, f"W{i+1}", 2.4, dy)
# 4×Φ7.5×2 头沉孔 (承载面 Z0 侧开 → 俯视为隐藏, 虚线) @ 内/外圈 202.5°/247.5°
# H2 标号下移避开 Φ50 圆; H3 标号上移避开 A-A 剖切线
_H_OFF = {1: (2.4, 4.2), 2: (2.4, -4.6)}
for i, (x, y) in enumerate(HEAD_CB_XY):
    hx, hy = pv(x, y)
    circ(hx, hy, HEAD_CB_D/2, w=HID_W, dashed=True)
    dx, dy = _H_OFF.get(i, (2.4, -2.0))
    text(hx + dx, hy + dy, f"H{i+1}", size=3.4)
# 2×Φ4
for i, (x, y) in enumerate(EXTRA_HOLES):
    hx, hy = pv(x, y)
    circ(hx, hy, EXTRA_HOLE_D/2); cross(hx, hy, 4.2)
    text(hx + 2.4, hy - 2.0, f"E{i+1}", size=3.4)

# Φ170 直径尺寸 (顶部)
hdim(pv(-BASE_OD/2, 0)[0], pv(BASE_OD/2, 0)[0],
     pv(0, BASE_OD/2)[1], pv(0, BASE_OD/2)[1] - 12, f"Φ{BASE_OD:g}")

# 引出说明 — 顶部左侧 (两圈孔)
_h155 = (OUTER_PCD_R*math.cos(math.radians(112.5)), OUTER_PCD_R*math.sin(math.radians(112.5)))
note(*pv(*_h155), 14, 26, f"8×Φ{M3_DIAM:g} 通孔 均布 PCD Φ{2*OUTER_PCD_R:g} (22.5°+k·45°)")
_h60 = (INNER_PCD_R*math.cos(math.radians(157.5)), INNER_PCD_R*math.sin(math.radians(157.5)))
note(*pv(*_h60), 14, 34, f"8×Φ{M3_DIAM:g} 通孔 均布 PCD Φ{2*INNER_PCD_R:g} (22.5°+k·45°)")
note(*pv(*HEAD_CB_XY[0]), 14, 42,
     f"4×Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 头沉孔 (承载面 Z0 侧, 内圈 2 在 wifi 模块底下 / 外圈 2 挨盒东侧), 见表④")
# 引出说明 — 底部
note(*pv(*PI_HOLES[5]), 12, 246,
     f"7×pi2hub 孔: Φ{PI_THRU_D:g} 通 + Φ{PI_INSERT_D:g}×{PI_INSERT_DEEP:g} 沉孔 (唇侧), 孔位见表①")
note(*pv(*WIFI_HOLES[1]), 12, 254,
     "4×wifi_shell 孔 (定稿单组): 同款沉孔, 孔位见表②")
_notch_mid = (50.5*math.cos(math.radians(-45.0)), 50.5*math.sin(math.radians(-45.0)))
note(*pv(*_notch_mid), 186, 246,
     f"扇形挖槽 R{NOTCH_R_MIN:g}..R{NOTCH_R_MAX:g}, {NOTCH_A_S:g}°..{NOTCH_A_E:g}°, 深 {NOTCH_DEPTH:g} (见 B–B)",
     anchor="end")
note(*pv(*EXTRA_HOLES[0]), 198, 254,
     f"2×Φ{EXTRA_HOLE_D:g} 通孔: E1 (-10°, R72) / E2 (-42.5°, R56), 见表③",
     anchor="end")

# =====================================================================
# 剖视图 A–A (1:1) — 沿 22.5°–202.5° 直径, 过两圈 Φ3.2 孔; r 横, Z 纵
# =====================================================================
SAX, SAY = 305.0, 72.0
def sa(t, z): return (SAX + t, SAY - z)

text(SAX, 37, "剖视图 A–A (1:1) — 沿 22.5°–202.5° 直径   尺寸单位: mm",
     size=TXT_L, anchor="middle")

R_BI, R_BO = BASE_ID/2, BASE_OD/2       # 25 / 85
R_RI = RIM_ID/2                          # 82.5
R_IB_I, R_IB_O = IBOSS_ID/2, IBOSS_OD/2  # 35 / 40
HM3 = M3_DIAM/2
HCB6 = HEAD_CB_D/2                       # 3.75 (头沉孔半宽)
for sgn in (1, -1):
    def X(t): return sgn * t
    # 内孔壁
    line(*sa(X(R_BI), 0), *sa(X(R_BI), BASE_H), GEOM_W)
    # Z5 面: 25..28.4, 31.6..35 (内圈孔), 40..75.9, 79.1..82.5 (外圈孔)
    line(*sa(X(R_BI), BASE_H), *sa(X(INNER_PCD_R - HM3), BASE_H), GEOM_W)
    line(*sa(X(INNER_PCD_R + HM3), BASE_H), *sa(X(R_IB_I), BASE_H), GEOM_W)
    line(*sa(X(R_IB_O), BASE_H), *sa(X(OUTER_PCD_R - HM3), BASE_H), GEOM_W)
    line(*sa(X(OUTER_PCD_R + HM3), BASE_H), *sa(X(R_RI), BASE_H), GEOM_W)
    # 内凸台环 (Z5..7.5)
    line(*sa(X(R_IB_I), BASE_H), *sa(X(R_IB_I), BASE_H + IBOSS_H), GEOM_W)
    line(*sa(X(R_IB_I), BASE_H + IBOSS_H), *sa(X(R_IB_O), BASE_H + IBOSS_H), GEOM_W)
    line(*sa(X(R_IB_O), BASE_H + IBOSS_H), *sa(X(R_IB_O), BASE_H), GEOM_W)
    # 外唇 (Z5..10.5)
    line(*sa(X(R_RI), BASE_H), *sa(X(R_RI), TOTAL_H), GEOM_W)
    line(*sa(X(R_RI), TOTAL_H), *sa(X(R_BO), TOTAL_H), GEOM_W)
    line(*sa(X(R_BO), TOTAL_H), *sa(X(R_BO), 0), GEOM_W)
    # 底面 Z0 — 剖切面左半 (202.5°) 内+外圈孔均有 Φ7.5 头沉开口 (H1/H3),
    # 右半 (22.5°) 两孔为全程 Φ3.2 (对照)
    has_cb = sgn < 0
    bw = HCB6 if has_cb else HM3
    xin = sgn * INNER_PCD_R
    xout = sgn * OUTER_PCD_R
    # 底边分段 (按孔开口打断)
    edges = sorted([X(R_BI), X(R_BO)])
    gaps = sorted([(xin - bw, xin + bw), (xout - bw, xout + bw)])
    t_prev = edges[0]
    for gl, gr in gaps:
        if gl > t_prev:
            line(*sa(t_prev, 0), *sa(gl, 0), GEOM_W)
        t_prev = max(t_prev, gr)
    if edges[1] > t_prev:
        line(*sa(t_prev, 0), *sa(edges[1], 0), GEOM_W)
    # 孔壁
    for xc_ in (xin, xout):
        if has_cb:
            for sg2 in (1, -1):
                line(*sa(xc_ + sg2*HCB6, 0), *sa(xc_ + sg2*HCB6, HEAD_CB_DEEP), GEOM_W)
                line(*sa(xc_ + sg2*HCB6, HEAD_CB_DEEP), *sa(xc_ + sg2*HM3, HEAD_CB_DEEP), GEOM_W)
                line(*sa(xc_ + sg2*HM3, HEAD_CB_DEEP), *sa(xc_ + sg2*HM3, BASE_H), GEOM_W)
        else:
            line(*sa(xc_ - HM3, 0), *sa(xc_ - HM3, BASE_H), GEOM_W)
            line(*sa(xc_ + HM3, 0), *sa(xc_ + HM3, BASE_H), GEOM_W)
    # 孔中心线
    for xc_ in (xin, xout):
        pdf.set_dash_pattern(dash=2, gap=1); _w(0.12)
        pdf.line(*sa(xc_, -1.5), *sa(xc_, BASE_H + 1.5))
        pdf.set_dash_pattern(); _w(GEOM_W)
# 轴中心线
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.13)
pdf.line(*sa(0, -4), *sa(0, TOTAL_H + 4))
pdf.set_dash_pattern(); _w(GEOM_W)

# 尺寸
hdim(sa(-R_RI, 0)[0], sa(R_RI, 0)[0],
     sa(0, TOTAL_H)[1], sa(0, TOTAL_H)[1] - 12, f"Φ{RIM_ID:g}")
hdim(sa(-R_BI, 0)[0], sa(R_BI, 0)[0], SAY, SAY + 12, f"Φ{BASE_ID:g}")
hdim(sa(-INNER_PCD_R, 0)[0], sa(INNER_PCD_R, 0)[0], SAY, SAY + 22,
     f"PCD Φ{2*INNER_PCD_R:g} (8×Φ{M3_DIAM:g})")
hdim(sa(-OUTER_PCD_R, 0)[0], sa(OUTER_PCD_R, 0)[0], SAY, SAY + 32,
     f"PCD Φ{2*OUTER_PCD_R:g} (8×Φ{M3_DIAM:g})")
vdim(sa(0, BASE_H)[1], sa(0, 0)[1], sa(-R_BO, 0)[0], sa(-R_BO, 0)[0] - 10,
     f"{BASE_H:g}")
vdim(sa(0, TOTAL_H)[1], sa(0, BASE_H)[1], sa(-R_BO, 0)[0], sa(-R_BO, 0)[0] - 20,
     f"{RIM_H:g}")
vdim(sa(0, TOTAL_H)[1], sa(0, 0)[1], sa(R_BO, 0)[0], sa(R_BO, 0)[0] + 10,
     f"{TOTAL_H:g}")
# 说明
note(*sa(-(R_IB_I + R_IB_O)/2, BASE_H + IBOSS_H), 228, 50,
     f"内凸台环 Φ{IBOSS_OD:g}/Φ{IBOSS_ID:g}×{IBOSS_H:g} (唇侧 Z5..7.5, 见 B–B)")
note(*sa((R_RI + R_BO)/2, TOTAL_H - 1.5), 408, 46,
     f"外唇 Φ{RIM_OD:g}/Φ{RIM_ID:g}×{RIM_H:g} (Z5..10.5, 整圈)", anchor="end")
note(*sa(-INNER_PCD_R, HEAD_CB_DEEP/2), 211, 112,
     f"Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 头沉孔 (Z0 承载面侧, 内+外圈 202.5°/247.5° 共 4 孔, 剖切面过 H1/H3)")

# =====================================================================
# 剖面 B–B (2:1) — 沿 -42.5° 半径半剖: 挖槽 + Φ4 孔 + 内凸台环
# =====================================================================
BX, BY, BS = 215.0, 158.0, 2.0
def sb(r, z): return (BX + r*BS, BY - z*BS)

text(300, 122, "剖面 B–B (2:1) — 沿 -42.5° 半径半剖   尺寸单位: mm",
     size=TXT_L, anchor="middle")

E4 = EXTRA_HOLE_D/2   # 2
R_E2 = 56.0
NZ_S = BASE_H - NOTCH_DEPTH   # 3
# 内孔壁 / Z5 面 25..35
line(*sb(R_BI, 0), *sb(R_BI, BASE_H), GEOM_W)
line(*sb(R_BI, BASE_H), *sb(R_IB_I, BASE_H), GEOM_W)
# 内凸台环 (R35..40 × Z5..7.5) — 与托盘连成一体, 挖槽自其外缘 R40 起
line(*sb(R_IB_I, BASE_H), *sb(R_IB_I, BASE_H + IBOSS_H), GEOM_W)
line(*sb(R_IB_I, BASE_H + IBOSS_H), *sb(R_IB_O, BASE_H + IBOSS_H), GEOM_W)
# 挖槽内壁 = 凸台环外壁 (R40, Z7.5 → Z3)
line(*sb(R_IB_O, BASE_H + IBOSS_H), *sb(R_IB_O, NZ_S), GEOM_W)
# 槽底 Z3 (被 Φ4 孔打断) / 槽外壁 (61, Z3..5)
line(*sb(NOTCH_R_MIN, NZ_S), *sb(R_E2 - E4, NZ_S), GEOM_W)
line(*sb(R_E2 + E4, NZ_S), *sb(NOTCH_R_MAX, NZ_S), GEOM_W)
line(*sb(NOTCH_R_MAX, NZ_S), *sb(NOTCH_R_MAX, BASE_H), GEOM_W)
# Z5 面 61..82.5 / 外唇 / 外壁 / 底面
line(*sb(NOTCH_R_MAX, BASE_H), *sb(R_RI, BASE_H), GEOM_W)
line(*sb(R_RI, BASE_H), *sb(R_RI, TOTAL_H), GEOM_W)
line(*sb(R_RI, TOTAL_H), *sb(R_BO, TOTAL_H), GEOM_W)
line(*sb(R_BO, TOTAL_H), *sb(R_BO, 0), GEOM_W)
line(*sb(R_BI, 0), *sb(R_E2 - E4, 0), GEOM_W)
line(*sb(R_E2 + E4, 0), *sb(R_BO, 0), GEOM_W)
# Φ4 孔壁 (Z0..3, 穿槽底) + 中心线
line(*sb(R_E2 - E4, 0), *sb(R_E2 - E4, NZ_S), GEOM_W)
line(*sb(R_E2 + E4, 0), *sb(R_E2 + E4, NZ_S), GEOM_W)
pdf.set_dash_pattern(dash=2, gap=1); _w(0.12)
pdf.line(*sb(R_E2, -1.5), *sb(R_E2, BASE_H + 1.0))
pdf.set_dash_pattern(); _w(GEOM_W)
# 轴中心线 r=0
pdf.set_dash_pattern(dash=4, gap=1.5); _w(0.13)
pdf.line(BX, BY - TOTAL_H*BS - 5, BX, BY + 5)
pdf.set_dash_pattern(); _w(GEOM_W)

# 尺寸: 半径定位 (自轴线) + 槽深
hdim(BX, sb(NOTCH_R_MIN, 0)[0], BY, BY + 10, f"R{NOTCH_R_MIN:g}")
hdim(BX, sb(R_E2, 0)[0], BY, BY + 18, f"R{R_E2:g} (Φ{EXTRA_HOLE_D:g} 通孔 E2)")
hdim(BX, sb(NOTCH_R_MAX, 0)[0], BY, BY + 26, f"R{NOTCH_R_MAX:g}")
vdim(sb(0, BASE_H)[1], sb(0, NZ_S)[1], sb(NOTCH_R_MAX, 0)[0],
     sb(NOTCH_R_MAX, 0)[0] + 9, f"{NOTCH_DEPTH:g}")
note(*sb((R_IB_I + R_IB_O)/2, BASE_H + IBOSS_H), 246, 130,
     "挖槽自内凸台环外缘 R40 起 (环不跨槽)")

# =====================================================================
# 详图 C (4:1) — pi2hub / wifi_shell 沉孔 (共 11 处)
# =====================================================================
DCX, DCY, DS = 237.0, 250.0, 4.0
def dc(t, z): return (DCX + t*DS, DCY - z*DS)

text(DCX, 206, "详图 C (4:1)   尺寸单位: mm", size=TXT_L, anchor="middle")
text(DCX, 211.5,
     f"Φ{PI_THRU_D:g} 通 + Φ{PI_INSERT_D:g}×{PI_INSERT_DEEP:g} 沉孔 (唇侧 Z5 面), "
     f"托盘面台肩 {CB_SHOULDER:g} — 共 11 处 (7 pi2hub + 4 wifi)",
     size=TXT_I, anchor="middle")

HB, HCB, HTH = 6.5, PI_INSERT_D/2, PI_THRU_D/2   # 半宽: 材料 / 沉孔 / 通孔
# 顶边 Z5 (唇侧面, 被沉孔打断)
line(*dc(-HB, BASE_H), *dc(-HCB, BASE_H), GEOM_W)
line(*dc(HCB, BASE_H), *dc(HB, BASE_H), GEOM_W)
# 沉孔壁 (Z0.5..5) + 台肩 + 通孔壁 (Z0..0.5)
for sgn in (1, -1):
    line(*dc(sgn*HCB, BASE_H), *dc(sgn*HCB, CB_SHOULDER), GEOM_W)
    line(*dc(sgn*HCB, CB_SHOULDER), *dc(sgn*HTH, CB_SHOULDER), GEOM_W)
    line(*dc(sgn*HTH, CB_SHOULDER), *dc(sgn*HTH, 0), GEOM_W)
    line(*dc(sgn*HB, 0), *dc(sgn*HB, BASE_H), GEOM_W)
# 底边 Z0 (托盘承载面, 被通孔打断)
line(*dc(-HB, 0), *dc(-HTH, 0), GEOM_W)
line(*dc(HTH, 0), *dc(HB, 0), GEOM_W)
# 中心线
pdf.set_dash_pattern(dash=3, gap=1.2); _w(0.13)
pdf.line(*dc(0, -1.5), *dc(0, BASE_H + 1.5))
pdf.set_dash_pattern(); _w(GEOM_W)

hdim(dc(-HCB, 0)[0], dc(HCB, 0)[0], dc(0, BASE_H)[1], dc(0, BASE_H)[1] - 10,
     f"Φ{PI_INSERT_D:g}")
hdim(dc(-HTH, 0)[0], dc(HTH, 0)[0], dc(0, 0)[1], dc(0, 0)[1] + 10,
     f"Φ{PI_THRU_D:g}")
vdim(dc(0, BASE_H)[1], dc(0, CB_SHOULDER)[1], dc(HCB, 0)[0], dc(HB, 0)[0] + 7,
     f"{PI_INSERT_DEEP:g}")
vdim(dc(0, CB_SHOULDER)[1], dc(0, 0)[1], dc(-HCB, 0)[0], dc(-HB, 0)[0] - 7,
     f"{CB_SHOULDER:g}")
text(dc(HB, 0)[0] + 15, dc(0, BASE_H)[1] - 1.0, "Z5 (唇侧面)", size=TXT_I)
text(dc(HB, 0)[0] + 15, dc(0, 0)[1] + 3.0, "Z0 (托盘承载面)", size=TXT_I)

# =====================================================================
# 孔位表 ①②③ (零件系坐标, mm)
# =====================================================================
T1X, T2X = 300.0, 358.0
text(T1X, 202, "表① pi2hub 孔位 ×7 (零件系, mm)", size=TXT_I)
for i, (x, y) in enumerate(PI_HOLES):
    text(T1X, 208 + i*5.5, f"P{i+1}:  {x:+.3f}, {y:+.3f}", size=TXT_I)
text(T1X, 247, "表③ Φ4 孔位 ×2 (极坐标 → 零件系)", size=TXT_I)
for i, ((a, R), (x, y)) in enumerate(zip(EXTRA_HOLES_POLAR, EXTRA_HOLES)):
    text(T1X, 253 + i*5.5, f"E{i+1}: ({a:g}°, R{R:g}) → {x:+.3f}, {y:+.3f}",
         size=TXT_I)
text(T2X, 197, "表② wifi_shell 孔位 ×4 (mm)", size=TXT_I)
text(T2X, 202, "定稿单组: 盒 XC43 + 长边平移 -13", size=TXT_I)
for i, (x, y) in enumerate(WIFI_HOLES):
    text(T2X, 208 + i*5.5, f"W{i+1}:  {x:+.3f}, {y:+.3f}", size=TXT_I)
text(T2X, 231, f"表④ Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 头沉孔 ×4 (承载面 Z0 侧)", size=TXT_I)
text(T2X, 236, "内圈 2 在 wifi 模块底下 / 外圈 2 挨盒东侧", size=TXT_I)
_H_RA = [(r, a) for r in (INNER_PCD_R, OUTER_PCD_R) for a in HEAD_CB_ANGLES]
for i, ((r, a), (x, y)) in enumerate(zip(_H_RA, HEAD_CB_XY)):
    text(T2X, 242 + i*5.5, f"H{i+1}: R{r:g} @{a:g}° → {x:+.3f}, {y:+.3f}",
         size=TXT_I)

# ===== Title block =====
tb_y = PAGE_H - 28; tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "POV 3D 结构件 — rim_ring 外圈托盘环 v3 (承载盘并入 + 内凸台环)",
     size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle / 比例 俯视·A–A 1:1, B–B 2:1, 详图 C 4:1", size=TXT_I,
     anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_OD:g}×总高 {TOTAL_H:g} / 托盘 {BASE_H:g} + 唇 {RIM_H:g} / 内凸台环 Φ{IBOSS_OD:g}/Φ{IBOSS_ID:g}×{IBOSS_H:g} / "
     f"挖槽 R{NOTCH_R_MIN:g}..{NOTCH_R_MAX:g} 深 {NOTCH_DEPTH:g} / 16×Φ{M3_DIAM:g} (4 孔加 Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 头沉) + 11×(Φ{PI_THRU_D:g}+Φ{PI_INSERT_D:g}×{PI_INSERT_DEEP:g} 沉, 7 pi + 4 wifi) + 2×Φ{EXTRA_HOLE_D:g} / "
     "Z0 托盘面 = 装配后朝上承载面 (翻转装) / 平放打印 / PETG / 单位 mm", size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-07-22  /  POV3D / models / rim_ring / rim_ring.stl", size=TXT_I,
     anchor="end")

try:
    pdf.output(str(out_pdf)); print(f"wrote {out_pdf}")
except PermissionError:
    alt = Path(__file__).with_name("rim_ring_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt}  (original {out_pdf.name} was locked)")
