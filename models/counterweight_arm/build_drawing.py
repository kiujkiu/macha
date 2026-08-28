"""
A3 drawing — counterweight_arm 转子配重臂 (2026-08-03, v3 / v3.1 共用件)。
参数 import 自 build_stl.py (单一数据源; import 会幂等重建 STL)。
GB 1st-angle: 俯视 (X-Y, 1:1) 上, 主视 (X-Z, 1:1) 其下, 详图 A M6 底面沉孔 (6:1) 右。
坐标 = 罩子零件系 XY, Z0 = 罩顶面 (装配 Z92.2)。
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_cwa", Path(__file__).with_name("build_stl.py"))
_m = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_m)
R_OUT, BASE_T, X_IN, HW = _m.R_OUT, _m.BASE_T, _m.X_IN, _m.HW
M3_XS, M3_Y, M3_D = _m.M3_XS, _m.M3_Y, _m.M3_D
M6_XS, M6_Y, M6_D = _m.M6_XS, _m.M6_Y, _m.M6_D
M6_EDGE, M6_PITCH = _m.M6_EDGE, _m.M6_PITCH
M6_CB_D, M6_CB_H, M6_CB_BOT = _m.M6_CB_D, _m.M6_CB_H, _m.M6_CB_FROM_BOTTOM
M6_RS = sorted((math.hypot(mx, M6_Y) for mx in M6_XS), reverse=True)   # [77, 64]
M6_R_AVG = sum(M6_RS) / 2.0
CB_EDGE = R_OUT - (M6_RS[0] + M6_CB_D / 2)      # 外沉孔对 R85 外缘的剩余边距
CB_RIB = M6_PITCH - M6_CB_D                     # 两沉孔之间的肋
MASS, VOL = _m.MASS, _m.VOL
OWN = MASS * math.hypot(*_m._cen[:2])           # 本件自带固有配重 g·mm

FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2 = 12.0, 22.0
PAGE_W, PAGE_H = 420.0, 297.0

pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
pdf.add_font("SimHei", "", FONT)

def _w(v): pdf.set_line_width(v)
def line(x1, y1, x2, y2, w=DIM_W): _w(w); pdf.line(x1, y1, x2, y2)
def arrow(tx, ty, dx, dy):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
    bx, by = tx-ARR_L*ux, ty-ARR_L*uy; px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx+ARR_W*px, by+ARR_W*py), (bx-ARR_W*px, by-ARR_W*py)], style="F")
# SimHei 缺字 (fontTools 查 cmap 确认): − U+2212 / ⇒ U+21D2 / ⚠ U+26A0 / Ø / • 都渲染成空白,
# 旧版图里 "−X 轴" 印出来是 "X 轴"。所有落笔的字符串统一过一遍替换。
_GLYPH_FIX = {"−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ"}
def _g(s):
    s = str(s)
    for a, b in _GLYPH_FIX.items():
        if a in s: s = s.replace(a, b)
    return s
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    s = _g(s)
    pdf.set_font("SimHei", "", size)
    if anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end": x -= pdf.get_string_width(s)
    if halo:
        sw, fh = pdf.get_string_width(s), pdf.font_size
        pdf.set_fill_color(255, 255, 255); pdf.rect(x-0.4, y-fh*0.85, sw+0.8, fh*1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, ang, size=TXT_D, halo=False):
    s = _g(s)
    pdf.set_font("SimHei", "", size); sw = pdf.get_string_width(s)
    with pdf.rotation(angle=ang, x=cx, y=cy):
        if halo:
            fh = pdf.font_size; pdf.set_fill_color(255, 255, 255)
            pdf.rect(cx-sw/2-0.4, cy-fh*0.85, sw+0.8, fh*1.1, style="F"); pdf.set_fill_color(0, 0, 0)
        pdf.text(cx-sw/2, cy, s)
def _u(s):
    s = str(s).strip()
    return s if ("mm" in s or "°" in s) else f"{s} mm"
def hdim(x1, x2, yg, yd, label):
    label = _u(label)
    e1, e2 = (yg+EXT_GP, yd+EXT_OV) if yd > yg else (yg-EXT_GP, yd-EXT_OV)
    line(x1, e1, x1, e2, EXT_W_); line(x2, e1, x2, e2, EXT_W_)
    xl, xr = min(x1, x2), max(x1, x2)
    if xr-xl >= 2*ARR_L+1:
        line(xl, yd, xr, yd); arrow(xl, yd, -1, 0); arrow(xr, yd, 1, 0)
    else:
        e = ARR_L+1.0; line(xl-e, yd, xr+e, yd); arrow(xl, yd, 1, 0); arrow(xr, yd, -1, 0)
    text((xl+xr)/2, yd-1.8, label, anchor="middle", halo=True)
def vdim(y1, y2, xg, xd, label):
    label = _u(label)
    e1, e2, to = (xg+EXT_GP, xd+EXT_OV, 4.0) if xd > xg else (xg-EXT_GP, xd-EXT_OV, -4.0)
    line(e1, y1, e2, y1, EXT_W_); line(e1, y2, e2, y2, EXT_W_)
    yt, yb = min(y1, y2), max(y1, y2)
    if yb-yt >= 2*ARR_L+1:
        line(xd, yt, xd, yb); arrow(xd, yt, 0, -1); arrow(xd, yb, 0, 1)
    else:
        e = ARR_L+1.0; line(xd, yt-e, xd, yb+e); arrow(xd, yt, 0, 1); arrow(xd, yb, 0, -1)
    lh = pdf.get_string_width(label)
    if yb-yt >= lh+1.0: rot_text(xd+to, (yt+yb)/2, label, 90, halo=True)
    else: rot_text(xd+to, yb+ARR_L+1.0+lh/2+1.0, label, 90, halo=True)
def note(xf, yf, xt, yt, label, anchor="start"):
    line(xf, yf, xt, yt, EXT_W_); arrow(xf, yf, xf-xt, yf-yt)
    text(xt+(1.0 if anchor == "start" else -1.0), yt+1.2, label, size=TXT_I, anchor=anchor, halo=True)
def rect(x0, y0, x1, y1, w=GEOM_W):
    _w(w); pdf.line(x0, y0, x1, y0); pdf.line(x1, y0, x1, y1)
    pdf.line(x1, y1, x0, y1); pdf.line(x0, y1, x0, y0)
def drect(x0, y0, x1, y1):
    pdf.set_dash_pattern(dash=2.0, gap=1.2); rect(x0, y0, x1, y1, HID_W); pdf.set_dash_pattern()
def cross(cx, cy, r=4.0):
    pdf.set_dash_pattern(dash=1.2, gap=0.6); _w(0.13)
    pdf.line(cx-r, cy, cx+r, cy); pdf.line(cx, cy-r, cx, cy+r)
    pdf.set_dash_pattern(); _w(GEOM_W)
def dline(x1, y1, x2, y2, dash=(2.0, 1.2)):
    pdf.set_dash_pattern(dash=dash[0], gap=dash[1]); _w(HID_W)
    pdf.line(x1, y1, x2, y2); pdf.set_dash_pattern(); _w(GEOM_W)
def polyline(pts, w=GEOM_W, dash=None):
    if dash: pdf.set_dash_pattern(dash=dash[0], gap=dash[1])
    _w(w)
    for i in range(len(pts)-1):
        pdf.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    if dash: pdf.set_dash_pattern()



def dcircle(cx, cy, r):
    pdf.set_dash_pattern(dash=1.8, gap=1.1); _w(HID_W)
    pdf.circle(cx, cy, r, style="D"); pdf.set_dash_pattern(); _w(GEOM_W)
def hatch(x0, y0, x1, y1, step=2.2):
    """45° 剖面线, 裁在矩形内 (y0 上, y1 下)"""
    _w(0.13)
    c0, c1 = x0 - (y1 - y0), x1
    c = c0 - ((c0 - y0) % step)          # 相位按 (x−y) 全局对齐, 免得分段处出现白缝
    while c <= c1 + step:
        ax, ay = c, y0
        bx, by = c + (y1 - y0), y1
        if ax < x0: ay = y0 + (x0 - ax); ax = x0
        if bx > x1: by = y1 - (bx - x1); bx = x1
        if ax <= x1 and bx >= x0 and ay < by:
            pdf.line(ax, ay, bx, by)
        c += step
    _w(GEOM_W)


# ===== 图框 + 图头 =====
_w(0.3); pdf.rect(5, 5, PAGE_W-10, PAGE_H-10, style="D")
text(PAGE_W/2, 14, "POV 3D — counterweight_arm 转子配重臂 (v3 / v3.1 共用, ×1)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20, f"底板 {BASE_T:g} 厚 × 半宽 {HW:g} × X {-R_OUT:g}..{X_IN:g}, 外缘按 R{R_OUT:g} 圆弧裁 ⇒ **旋转包络不超 Φ{2*R_OUT:g}** (用户要求) / "
     f"**2×Φ{M6_D:g} M6 光孔改排成左右: @ X {M6_XS[0]:g} / {M6_XS[1]:g}, Y{M6_Y:g} 上下居中, 孔距 {M6_PITCH:g}, 左孔离左边缘 {M6_EDGE:g}** (2026-08-27 三改)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 25, f"**M6 沉孔 Φ{M6_CB_D:g} × 深 {M6_CB_H:g}, 开在{'底面 (贴罩顶那一面)' if M6_CB_BOT else '顶面'}** — 详图 A。"
     f"⚠ 孔距 {M6_PITCH:g} vs 沉孔 Φ{M6_CB_D:g} ⇒ 两沉孔之间只剩 **{CB_RIB:.1f} 肋**; 外侧沉孔对 R{R_OUT:g} 外缘只剩 **{CB_EDGE:.2f} 边距**; 沉孔上余厚 {BASE_T-M6_CB_H:g}",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 30, f"安装: 骑在 rotor_shroud 顶面 (件系 Z0 = 罩顶 = 装配 Z92.2), **跨对开缝 Y=0** — 4×Φ{M3_D:g} 里 Y+{M3_Y:g} 两颗进 shroud_half_A、Y−{M3_Y:g} 两颗进 shroud_half_B ⇒ **本件把两半在顶部连成一体** / "
     f"配重: **M6 大扁头 (Φ{M6_CB_D:g}×{M6_CB_H:g}) 从下面插入沉进底面沉孔与底面齐平, 螺杆朝上**, Φ12 平垫 / M6 螺母全部叠在板上面 (板下无空间, 螺杆下伸出量必须为 0)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 35, f"方向: 件在零件系 −X ⇒ 修正矢量指向 −X, 正是 v3.1 偏心屏 (+X 偏 6.7) 要抵消的方向 / 两孔力臂 r{M6_RS[0]:.0f} + r{M6_RS[1]:.0f} (等效 2×r{M6_R_AVG:.2f}) / "
     f"本件自重 {MASS:.1f} g PLA 自带 ~{OWN:.0f} g·mm 同向配重 / 材料 PLA / 打印: **翻面 — 顶面贴床, 沉孔口朝上, 零支撑零桥接**  (GB 1st-angle, 1:1, mm)",
     size=TXT_I, anchor="middle")

# ===================== 俯视图 (X-Y, 1:1) =====================
S, TX, TYC = 1.0, 175.0, 100.0
def pv(x, y): return (TX + (x - (X_IN + (-R_OUT))/2)*S, TYC - y*S)
text(TX, 44.0, "俯视图 (X-Y, 1:1) — 从罩子外面看", size=TXT_L, anchor="middle")

def arc_pts(r, a0, a1, n=120):
    return [pv(r*math.cos(math.radians(a)), r*math.sin(math.radians(a)))
            for a in [a0 + (a1-a0)*i/n for i in range(n+1)]]

_amax = math.degrees(math.asin(HW/R_OUT))
polyline(arc_pts(R_OUT, 180-_amax, 180+_amax))                 # 外缘圆弧
polyline([pv(-R_OUT*math.cos(math.radians(_amax)),  HW), pv(X_IN,  HW)])
polyline([pv(-R_OUT*math.cos(math.radians(_amax)), -HW), pv(X_IN, -HW)])
polyline([pv(X_IN, -HW), pv(X_IN, HW)])
_w(GEOM_W)
for _mx in M6_XS:                                                # 2× M6: Φ12.5 沉孔(底面,虚) + Φ6.5 光孔(实)
    dcircle(*pv(_mx, M6_Y), M6_CB_D/2*S)
    pdf.circle(*pv(_mx, M6_Y), M6_D/2*S, style="D")
    cross(*pv(_mx, M6_Y), 9.0)
for mx in M3_XS:
    for sy in (1.0, -1.0):
        pdf.circle(*pv(mx, sy*M3_Y), M3_D/2*S, style="D")
        cross(*pv(mx, sy*M3_Y), 6.5)
line(*pv(-R_OUT-3, 0), *pv(X_IN+3, 0), DIM_W)                    # X 轴中心线 (= 两 M6 孔连心线)
line(*pv((X_IN+(-R_OUT))/2, -HW-5), *pv((X_IN+(-R_OUT))/2, HW+5), DIM_W)
text(pv(X_IN-2, 0)[0]+3, pv(0, 0)[1]-1.2, "← 罩对开缝 Y=0", size=TXT_I)

line(pv(-R_OUT, 0)[0], pv(0, 0)[1]-1.0, pv(-R_OUT, 0)[0], pv(0, HW)[1], EXT_W_)   # 界线拉到 R85 弧顶 (Y=0 才是最左点)
hdim(pv(-R_OUT, 0)[0], pv(M6_XS[0], 0)[0], pv(0, HW)[1], pv(0, HW)[1]-DIM_O1, f"{M6_EDGE:g} (左孔到左边缘)")
hdim(pv(M6_XS[0], 0)[0], pv(M6_XS[1], 0)[0], pv(0, HW)[1], pv(0, HW)[1]-DIM_O2, f"{M6_PITCH:g} (M6 孔距)")
hdim(pv(-R_OUT, 0)[0], pv(X_IN, 0)[0], pv(0, -HW)[1], pv(0, -HW)[1]+DIM_O1, f"{X_IN-(-R_OUT):g} (总长)")
hdim(pv(M3_XS[1], 0)[0], pv(M3_XS[0], 0)[0], pv(0, -HW)[1], pv(0, -HW)[1]+DIM_O2+4, f"{M3_XS[0]-M3_XS[1]:g} (M3 排距)")
hdim(pv(M6_XS[1], 0)[0], pv(X_IN, 0)[0], pv(0, -HW)[1], pv(0, -HW)[1]+DIM_O2+18, f"{X_IN-M6_XS[1]:g} (内 M6 到内端)")
vdim(pv(0, HW)[1], pv(0, -HW)[1], pv(X_IN, 0)[0], pv(X_IN, 0)[0]+DIM_O1, f"{2*HW:g} (宽)")
vdim(pv(0, M3_Y)[1], pv(0, -M3_Y)[1], pv(X_IN, 0)[0], pv(X_IN, 0)[0]+DIM_O2+6, f"{2*M3_Y:g} (M3 孔距)")

note(*pv(M3_XS[1], M3_Y), 28.0, 84.0, f"4×Φ{M3_D:g} @ X{M3_XS[0]:g}/{M3_XS[1]:g}, Y±{M3_Y:g} — 对罩顶 4 个铜花螺母, M3×16 ×4", anchor="start")
note(*pv(M3_XS[1], -M3_Y), 28.0, 90.0, "Y+ 两颗 → shroud_half_A;  Y− 两颗 → shroud_half_B", anchor="start")
for _k, _t in enumerate([
        f"2×Φ{M6_D:g} M6 光孔 — **都在 X 轴上 (Y=0, 上下居中)**, 孔距 {M6_PITCH:g}, 左孔离左边缘 {M6_EDGE:g} (2026-08-27 由上下改左右)",
        f"虚线圆 = **底面 Φ{M6_CB_D:g} 沉孔, 深 {M6_CB_H:g}** (见详图 A) — 两沉孔之间只剩 {CB_RIB:.1f} 肋, 外沉孔对 R{R_OUT:g} 外缘只剩 {CB_EDGE:.2f}",
        f"两孔 Y=0 ⇒ 合矢量仍在 −X 轴上; 力臂 r{M6_RS[0]:.0f} / r{M6_RS[1]:.0f} (等效 2×r{M6_R_AVG:.2f})",
        f"「左边缘」= R{R_OUT:g} 外弧在 Y=0 处的最左点 (X {-R_OUT:g}) — 尺寸 {M6_EDGE:g} 在此量"]):
    text(25.0, 116.0 + _k * 6.0, _t, size=TXT_I)

# ===================== 主视图 (X-Z, 1:1, 置俯视图下方) =====================
FZ0 = 205.0
def fv(x, z): return (TX + (x - (X_IN + (-R_OUT))/2)*S, FZ0 - z*S)
text(TX, 186.0, "主视图 (X-Z, 1:1) — 底面 = 罩顶面", size=TXT_L, anchor="middle")
polyline([fv(-R_OUT, 0), fv(X_IN, 0), fv(X_IN, BASE_T), fv(-R_OUT, BASE_T), fv(-R_OUT, 0)])
_w(GEOM_W)
_cbz = M6_CB_H if M6_CB_BOT else BASE_T - M6_CB_H
_HD = (1.1, 0.8)                                                 # 段短, 虚线要细密才看得出是线
for _mx in M6_XS:                                                # M6 通孔 + 沉孔 (隐藏)
    for _sgn in (1.0, -1.0):
        if M6_CB_BOT:
            dline(*fv(_mx+_sgn*M6_CB_D/2, 0), *fv(_mx+_sgn*M6_CB_D/2, _cbz), _HD)
            dline(*fv(_mx+_sgn*M6_D/2, _cbz), *fv(_mx+_sgn*M6_D/2, BASE_T), _HD)
        else:
            dline(*fv(_mx+_sgn*M6_D/2, 0), *fv(_mx+_sgn*M6_D/2, _cbz), _HD)
            dline(*fv(_mx+_sgn*M6_CB_D/2, _cbz), *fv(_mx+_sgn*M6_CB_D/2, BASE_T), _HD)
        dline(*fv(_mx+_sgn*M6_D/2, _cbz), *fv(_mx+_sgn*M6_CB_D/2, _cbz), _HD)
for mx in M3_XS:                                                 # M3 通孔 (隐藏)
    for _sgn in (1.0, -1.0):
        dline(*fv(mx+_sgn*M3_D/2, 0), *fv(mx+_sgn*M3_D/2, BASE_T), _HD)
for _mx in M6_XS:
    line(*fv(_mx, -3), *fv(_mx, BASE_T+4), DIM_W)
vdim(fv(0, BASE_T)[1], fv(0, 0)[1], fv(X_IN, 0)[0], fv(X_IN, 0)[0]+DIM_O1, f"{BASE_T:g} (板厚)")

# 详图标记 A (圈住左边那个 M6 沉孔)
_w(0.25); pdf.circle(*fv(M6_XS[0], BASE_T/2), 9.0, style="D")
line(fv(M6_XS[0], BASE_T/2)[0], fv(M6_XS[0], BASE_T/2)[1]+9.0,
     fv(M6_XS[0], BASE_T/2)[0], fv(M6_XS[0], BASE_T/2)[1]+13.5, EXT_W_)
text(fv(M6_XS[0], BASE_T/2)[0], fv(M6_XS[0], BASE_T/2)[1]+19.0, "A", size=TXT_L, anchor="middle")

note(*fv(M6_XS[1], 0), 28.0, 232.0,
     f"2×Φ{M6_D:g} 光孔上下通 + **底面 Φ{M6_CB_D:g} × 深 {M6_CB_H:g} 沉孔** (2026-08-27 新增) → 详图 A", anchor="start")
text(29.0, 239.2, "底面 = 罩顶面, 全平贴合 ⇒ 板下无空间, M6 五金全在板上面 (大扁头沉进底面沉孔, 螺杆朝上)", size=TXT_I)

# ===================== 详图 A — M6 沉孔 (6:1 剖) =====================
SD, DX, DY0 = 6.0, 320.0, 145.0
HWD = 9.0 * SD                       # 剖出半宽 9 mm
R_TH, R_CB = M6_D/2*SD, M6_CB_D/2*SD
Y_TOP = DY0 - BASE_T*SD
Y_CB = DY0 - M6_CB_H*SD              # 沉孔底 (底面沉孔 ⇒ 台肩面在 Z=3)
text(DX, 88.0, f"详图 A (6:1) — M6 底面沉孔 Φ{M6_CB_D:g} × 深 {M6_CB_H:g} (剖)", size=TXT_L, anchor="middle")
for _sgn in (-1.0, 1.0):                                          # 左右两块材料
    xo, xi_cb, xi_th = DX + _sgn*HWD, DX + _sgn*R_CB, DX + _sgn*R_TH
    polyline([(xo, Y_TOP), (xi_th, Y_TOP), (xi_th, Y_CB), (xi_cb, Y_CB),
              (xi_cb, DY0), (xo, DY0)])
    hatch(min(xo, xi_cb), Y_TOP, max(xo, xi_cb), DY0)             # 全高段
    hatch(min(xi_cb, xi_th), Y_TOP, max(xi_cb, xi_th), Y_CB)      # 台肩以上段
_w(GEOM_W)
line(DX, Y_TOP-6, DX, DY0+6, DIM_W)                               # 轴线
hdim(DX-R_TH, DX+R_TH, Y_TOP, Y_TOP-DIM_O1, f"Φ{M6_D:g} (M6 过孔, 上下通)")
hdim(DX-R_CB, DX+R_CB, DY0, DY0+DIM_O1, f"Φ{M6_CB_D:g} (沉孔)")
vdim(Y_TOP, DY0, DX-HWD, DX-HWD-DIM_O1, f"{BASE_T:g} (板厚)")
vdim(Y_CB, DY0, DX+HWD, DX+HWD+DIM_O1, f"{M6_CB_H:g} (沉孔深)")
vdim(Y_TOP, Y_CB, DX+HWD, DX+HWD+DIM_O2+6, f"{BASE_T-M6_CB_H:g} (沉孔上余厚)")
text(DX-HWD-1.0, Y_TOP-2.0, "顶面 (五金叠这面)", size=TXT_I)
text(DX-HWD-1.0, DY0+5.0, "底面 = 贴罩顶 — 沉孔口开这面, 大扁头沉平", size=TXT_I)

# ===================== 配重容量表 =====================
RHO, W12 = 7.85e-3, math.pi*(6**2-3**2)*1.6*7.85e-3
bx, by = 250.0, 165.0
_w(0.3); pdf.rect(bx, by, 150.0, 46.0, style="D")
text(bx+3, by+6, f"配重容量 (力臂 r{M6_RS[0]:.0f}+r{M6_RS[1]:.0f} ⇒ 等效 2×r{M6_R_AVG:.2f}; 孔距 {M6_PITCH:g} ⇒ 垫圈外径 ≤ {M6_PITCH:g}, 只能 Φ12 平垫/M6 螺母):", size=TXT_I)
for k, (L, nw) in enumerate(((30, 4), (45, 10), (60, 16), (80, 26))):
    m1 = (471 + 26.0*L)*RHO + nw*W12
    text(bx+3, by+13+k*6, f"· 每孔 M6×{L:<3g} 大扁头 + {nw:2d} 片 Φ12 平垫 ×2 孔 = {2*m1:5.1f} g "
                          f"→ {2*m1*M6_R_AVG:5.0f} g·mm (含本件自重 +{OWN:.0f})", size=TXT_I)
text(bx+3, by+13+4*6, "对照 v3.1 偏心屏 m_屏×6.7: 300g→2010 / 500g→3350 / 800g→5360 g·mm", size=TXT_I)

# ===================== 标题栏 =====================
tb_y = PAGE_H-28; tb_x, tb_w, tb_h = 20, PAGE_W-40, 18
_w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
text(tb_x+4, tb_y+6, "POV 3D 结构件 — counterweight_arm 转子配重臂 (骑罩顶跨接缝, v3 / v3.1 共用)", size=TXT_L)
text(tb_x+tb_w-4, tb_y+6, "投影 1st-angle / 比例 1:1 (详图 A 6:1)", size=TXT_I, anchor="end")
text(tb_x+4, tb_y+14.5, f"{X_IN-(-R_OUT):g}×{2*HW:g}×{BASE_T:g} / {VOL/1000:.2f} cm3 ({MASS:.1f} g PLA) / "
     f"BOM: M3×16 ×4 → 罩顶铜花螺母; **M6 大扁头螺栓 ×2** (头 Φ{M6_CB_D:g}×{M6_CB_H:g} 沉进底面沉孔, 长度按配重量选) + Φ12 平垫/M6 螺母若干 + M6 尼龙锁紧螺母 ×2 / "
     f"⚠ 转速下必须防松 / 打印: 翻面 (顶面贴床), 零支撑 / 单位 mm", size=TXT_I)
text(tb_x+tb_w-4, tb_y+14.5, "2026-08-27  /  POV3D / models / counterweight_arm / counterweight_arm.stl", size=TXT_I, anchor="end")

out = Path(__file__).with_name("counterweight_arm_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except Exception:
    alt = Path(__file__).with_name("counterweight_arm_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt} (locked)")
