"""
A3 drawing — counterweight_arm 转子配重臂 (2026-08-03, v3 / v3.1 共用件)。
参数 import 自 build_stl.py (单一数据源; import 会幂等重建 STL)。
GB 1st-angle: 俯视 (X-Y, 1:1) 左, 主视 (X-Z, 1:1) 其下, 详图 D 六角窝 (2:1) 右。
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
M6_R, M6_BOSS_D, M6_BOSS_T, M6_D = _m.M6_R, _m.M6_BOSS_D, _m.M6_BOSS_T, _m.M6_D
M6_HEX_AF, M6_HEX_H = _m.M6_HEX_AF, _m.M6_HEX_H
MASS, VOL = _m.MASS, _m.VOL

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
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    pdf.set_font("SimHei", "", size)
    if anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end": x -= pdf.get_string_width(s)
    if halo:
        sw, fh = pdf.get_string_width(s), pdf.font_size
        pdf.set_fill_color(255, 255, 255); pdf.rect(x-0.4, y-fh*0.85, sw+0.8, fh*1.1, style="F")
        pdf.set_fill_color(0, 0, 0)
    pdf.text(x, y, s)
def rot_text(cx, cy, s, ang, size=TXT_D, halo=False):
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
def dline(x1, y1, x2, y2):
    pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
    pdf.line(x1, y1, x2, y2); pdf.set_dash_pattern(); _w(GEOM_W)
def polyline(pts, w=GEOM_W, dash=None):
    if dash: pdf.set_dash_pattern(dash=dash[0], gap=dash[1])
    _w(w)
    for i in range(len(pts)-1):
        pdf.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    if dash: pdf.set_dash_pattern()


# ===== 图框 + 图头 =====
_w(0.3); pdf.rect(5, 5, PAGE_W-10, PAGE_H-10, style="D")
text(PAGE_W/2, 14, "POV 3D — counterweight_arm 转子配重臂 (v3 / v3.1 共用, ×1)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20, f"底板 {BASE_T:g} 厚 × 半宽 {HW:g} × X {-R_OUT:g}..{X_IN:g}, 外缘按 R{R_OUT:g} 圆弧裁 ⇒ **旋转包络不超 Φ{2*R_OUT:g}** (用户要求) / "
     f"M6 座 Φ{M6_BOSS_D:g} 凸台高 {M6_BOSS_T:g} @ 力臂 r{M6_R:g} (外缘 r{M6_R+M6_BOSS_D/2:g}, 对 R{R_OUT:g} 余 {R_OUT-M6_R-M6_BOSS_D/2:g})",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 25, f"安装: 骑在 rotor_shroud 顶面 (件系 Z0 = 罩顶 = 装配 Z92.2), **跨对开缝 Y=0** — 4×Φ{M3_D:g} 里 "
     f"Y+{M3_Y:g} 两颗进 shroud_half_A、Y−{M3_Y:g} 两颗进 shroud_half_B ⇒ **本件把两半在顶部连成一体** (接缝原来只有各自 2 颗立柱螺丝)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 30, f"配重: M6 六角头**朝下**卡进底面对边 {M6_HEX_AF:g}×{M6_HEX_H:g} 六角窝 (防转) → 杆朝上穿出 → 从上面叠垫圈/螺母, "
     f"加减配重全在机器外面操作, 不用拆罩; 叠高无上限 (罩顶往上到顶轴承架 290 全空)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 35, f"方向: 件在零件系 −X ⇒ 修正矢量指向 −X, 正是 v3.1 偏心屏 (+X 偏 6.7) 要抵消的方向 / "
     f"本件自重 {MASS:.1f} g PLA 已自带 ~751 g·mm 同向配重 / 材料 PLA / 打印: 底面贴床, 零支撑  (GB 1st-angle, 1:1, mm)",
     size=TXT_I, anchor="middle")

# ===================== 俯视图 (X-Y, 1:1) =====================
S, TX, TYC = 1.0, 175.0, 100.0
def pv(x, y): return (TX + (x - (X_IN + (-R_OUT))/2)*S, TYC - y*S)
text(TX, 74.0, "俯视图 (X-Y, 1:1) — 从罩子外面看", size=TXT_L, anchor="middle")

def arc_pts(r, a0, a1, n=120):
    return [pv(r*math.cos(math.radians(a)), r*math.sin(math.radians(a)))
            for a in [a0 + (a1-a0)*i/n for i in range(n+1)]]

_amax = math.degrees(math.acos(-R_OUT*0/1)) if False else math.degrees(math.asin(HW/R_OUT))
polyline(arc_pts(R_OUT, 180-_amax, 180+_amax))                 # 外缘圆弧
polyline([pv(-R_OUT*math.cos(math.radians(_amax)),  HW), pv(X_IN,  HW)])
polyline([pv(-R_OUT*math.cos(math.radians(_amax)), -HW), pv(X_IN, -HW)])
polyline([pv(X_IN, -HW), pv(X_IN, HW)])
_w(GEOM_W); pdf.circle(*pv(-M6_R, 0), M6_BOSS_D/2*S, style="D")  # M6 凸台外径
pdf.circle(*pv(-M6_R, 0), M6_D/2*S, style="D")                   # M6 通孔
pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)               # 六角窝 (底面, 隐藏)
_hr = M6_HEX_AF/math.sqrt(3.0)*S
polyline([(pv(-M6_R,0)[0]+_hr*math.cos(math.radians(60*k+30)),
           pv(-M6_R,0)[1]+_hr*math.sin(math.radians(60*k+30))) for k in range(7)],
         HID_W, dash=(2.0, 1.2))
pdf.set_dash_pattern(); _w(GEOM_W)
cross(*pv(-M6_R, 0), 11.0)
for mx in M3_XS:
    for sy in (1.0, -1.0):
        pdf.circle(*pv(mx, sy*M3_Y), M3_D/2*S, style="D")
        cross(*pv(mx, sy*M3_Y), 6.5)
line(*pv(-R_OUT-3, 0), *pv(X_IN+3, 0), DIM_W)                    # X 轴中心线
line(*pv((X_IN+(-R_OUT))/2, -HW-5), *pv((X_IN+(-R_OUT))/2, HW+5), DIM_W)
# 接缝标记 (Y=0 = 罩子对开面)
text(pv(X_IN-2, 0)[0]+3, pv(0,0)[1]-1.2, "← 罩对开缝 Y=0", size=TXT_I)

hdim(pv(-R_OUT,0)[0], pv(X_IN,0)[0], pv(0,-HW)[1], pv(0,-HW)[1]+DIM_O1, f"{X_IN-(-R_OUT):g} (总长)")
hdim(pv(M3_XS[1],0)[0], pv(M3_XS[0],0)[0], pv(0,-HW)[1], pv(0,-HW)[1]+DIM_O2+4, f"{M3_XS[0]-M3_XS[1]:g} (M3 排距)")
hdim(pv(-M6_R,0)[0], pv(0,0)[0] if False else pv(X_IN,0)[0], pv(0,HW)[1], pv(0,HW)[1]-DIM_O1,
     f"{M6_R+X_IN:g} (M6 到内端)")
vdim(pv(0,HW)[1], pv(0,-HW)[1], pv(X_IN,0)[0], pv(X_IN,0)[0]+DIM_O1, f"{2*HW:g} (宽)")
vdim(pv(0,M3_Y)[1], pv(0,-M3_Y)[1], pv(X_IN,0)[0], pv(X_IN,0)[0]+DIM_O2+6, f"{2*M3_Y:g} (M3 孔距)")

note(*pv(M3_XS[1], M3_Y), 30.0, 52.0, f"4×Φ{M3_D:g} @ X{M3_XS[0]:g}/{M3_XS[1]:g}, Y±{M3_Y:g} — 对罩顶 4 个铜花螺母, M3×16 ×4", anchor="start")
note(*pv(M3_XS[1], -M3_Y), 30.0, 58.0, "Y+ 两颗 → shroud_half_A;  Y− 两颗 → shroud_half_B", anchor="start")
note(*pv(-M6_R, M6_BOSS_D/2), 30.0, 64.0, f"M6 座 Φ{M6_BOSS_D:g} @ r{M6_R:g} — 详图 D", anchor="start")

# ===================== 主视图 (X-Z, 1:1, 置俯视图下方) =====================
FZ0 = 205.0
def fv(x, z): return (TX + (x - (X_IN + (-R_OUT))/2)*S, FZ0 - z*S)
text(TX, 186.0, "主视图 (X-Z, 1:1) — 底面 = 罩顶面", size=TXT_L, anchor="middle")
polyline([fv(-R_OUT, 0), fv(X_IN, 0), fv(X_IN, BASE_T),
          fv(-M6_R+M6_BOSS_D/2, BASE_T), fv(-M6_R+M6_BOSS_D/2, M6_BOSS_T),
          fv(-M6_R-M6_BOSS_D/2, M6_BOSS_T), fv(-M6_R-M6_BOSS_D/2, BASE_T),
          fv(-R_OUT, BASE_T), fv(-R_OUT, 0)])
_w(GEOM_W)
for sgn in (1.0, -1.0):                                          # 六角窝 (隐藏)
    dline(*fv(-M6_R+sgn*M6_HEX_AF/2, 0), *fv(-M6_R+sgn*M6_HEX_AF/2, M6_HEX_H))
dline(*fv(-M6_R-M6_HEX_AF/2, M6_HEX_H), *fv(-M6_R+M6_HEX_AF/2, M6_HEX_H))
for sgn in (1.0, -1.0):                                          # M6 通孔 (隐藏)
    dline(*fv(-M6_R+sgn*M6_D/2, M6_HEX_H), *fv(-M6_R+sgn*M6_D/2, M6_BOSS_T))
for mx in M3_XS:                                                 # M3 通孔 (隐藏)
    for sgn in (1.0, -1.0):
        dline(*fv(mx+sgn*M3_D/2, 0), *fv(mx+sgn*M3_D/2, BASE_T))
line(*fv(-M6_R, -3), *fv(-M6_R, M6_BOSS_T+4), DIM_W)
vdim(fv(0, BASE_T)[1], fv(0, 0)[1], fv(X_IN,0)[0], fv(X_IN,0)[0]+DIM_O1, f"{BASE_T:g} (底板)")
vdim(fv(0, M6_BOSS_T)[1], fv(0, 0)[1], fv(-R_OUT,0)[0], fv(-R_OUT,0)[0]-DIM_O1, f"{M6_BOSS_T:g} (M6 座)")
note(*fv(-M6_R+M6_HEX_AF/2, M6_HEX_H/2), 30.0, 232.0,
     f"底面 对边 {M6_HEX_AF:g} × 深 {M6_HEX_H:g} 六角窝 — M6 六角头朝下卡入防转; 头上台肩 {M6_BOSS_T-M6_HEX_H:g} 厚承预紧", anchor="start")
note(*fv(-M6_R+M6_D/2, M6_BOSS_T-1.5), 30.0, 238.0,
     f"Φ{M6_D:g} M6 通孔 — 杆朝上穿出, 从上面叠 Φ18×1.6 大垫圈 (1.78 g/mm 叠高) + 尼龙锁紧螺母", anchor="start")

# ===================== 详图 D — 六角窝 (2:1) =====================
DS, DX, DYB = 2.0, 330.0, 128.0
def dv(dx, z): return (DX + dx*DS, DYB - z*DS)
text(DX, 74.0, "详图 D — M6 六角窝 (剖, 2:1)", size=TXT_L, anchor="middle")
polyline([dv(-13.0, 0), dv(-M6_BOSS_D/2, 0), dv(-M6_BOSS_D/2, M6_BOSS_T),
          dv(M6_BOSS_D/2, M6_BOSS_T), dv(M6_BOSS_D/2, 0), dv(13.0, 0)])
polyline([dv(-13.0, 0), dv(-13.0, BASE_T), dv(-M6_BOSS_D/2, BASE_T)])
polyline([dv(13.0, 0), dv(13.0, BASE_T), dv(M6_BOSS_D/2, BASE_T)])
_w(GEOM_W)
for sgn in (1.0, -1.0):
    pdf.line(*dv(sgn*M6_HEX_AF/2, 0), *dv(sgn*M6_HEX_AF/2, M6_HEX_H))
    pdf.line(*dv(sgn*M6_D/2, M6_HEX_H), *dv(sgn*M6_HEX_AF/2, M6_HEX_H))
    pdf.line(*dv(sgn*M6_D/2, M6_HEX_H), *dv(sgn*M6_D/2, M6_BOSS_T))
line(*dv(0, -3), *dv(0, M6_BOSS_T+4), DIM_W)
hdim(dv(-M6_HEX_AF/2,0)[0], dv(M6_HEX_AF/2,0)[0], dv(0,0)[1], dv(0,0)[1]+DIM_O1, f"{M6_HEX_AF:g} 对边")
hdim(dv(-M6_D/2,0)[0], dv(M6_D/2,0)[0], dv(0,M6_BOSS_T)[1], dv(0,M6_BOSS_T)[1]-DIM_O1, f"Φ{M6_D:g}")
vdim(dv(0,M6_HEX_H)[1], dv(0,0)[1], dv(M6_BOSS_D/2,0)[0], dv(M6_BOSS_D/2,0)[0]+DIM_O2, f"{M6_HEX_H:g} 窝深")
vdim(dv(0,M6_BOSS_T)[1], dv(0,M6_HEX_H)[1], dv(-M6_BOSS_D/2,0)[0], dv(-M6_BOSS_D/2,0)[0]-DIM_O1, f"{M6_BOSS_T-M6_HEX_H:g} 台肩")

# ===================== 配重容量表 =====================
bx, by = 250.0, 165.0
_w(0.3); pdf.rect(bx, by, 150.0, 46.0, style="D")
text(bx+3, by+6, f"配重容量 (力臂 r{M6_R:g}; 头朝下卡窝, 杆朝上叠 Φ18×1.6 大垫圈 2.84 g/片):", size=TXT_I)
_rows = [("M6×30 + 5 片 (叠高 8)", 24.0, 1814), ("M6×45 + 14 片 (叠高 22)", 52.7, 3976),
         ("M6×60 + 22 片 (叠高 36)", 78.4, 5923), ("M6×80 + 35 片 (叠高 56)", 119.5, 9019)]
for k, (cfg, m, mom) in enumerate(_rows):
    text(bx+3, by+13+k*6, f"· {cfg:<26s}  {m:5.1f} g  →  {mom:5d} g·mm  (含本件自重 +751)", size=TXT_I)
text(bx+3, by+13+len(_rows)*6, "对照 v3.1 偏心屏 m_屏×6.7: 300g→2010 / 500g→3350 / 800g→5360 g·mm", size=TXT_I)

# ===================== 标题栏 =====================
tb_y = PAGE_H-28; tb_x, tb_w, tb_h = 20, PAGE_W-40, 18
_w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
text(tb_x+4, tb_y+6, "POV 3D 结构件 — counterweight_arm 转子配重臂 (骑罩顶跨接缝, v3 / v3.1 共用)", size=TXT_L)
text(tb_x+tb_w-4, tb_y+6, "投影 1st-angle / 比例 1:1 (详图 2:1)", size=TXT_I, anchor="end")
text(tb_x+4, tb_y+14.5, f"{X_IN-(-R_OUT):g}×{2*HW:g}×{BASE_T:g} (M6 座处 {M6_BOSS_T:g}) / {VOL/1000:.2f} cm3 ({MASS:.1f} g PLA) / "
     f"BOM: M3×16 ×4 → 罩顶铜花螺母; M6 六角头螺栓 ×1 (长度按配重量) + Φ18 大垫圈若干 + M6 尼龙锁紧螺母 ×1 / "
     f"⚠ 转速下必须防松 / 打印: 底面贴床, 零支撑 (六角窝顶面 10.3 桥接) / 单位 mm", size=TXT_I)
text(tb_x+tb_w-4, tb_y+14.5, "2026-08-03  /  POV3D / models / counterweight_arm / counterweight_arm.stl", size=TXT_I, anchor="end")

out = Path(__file__).with_name("counterweight_arm_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except Exception:
    alt = Path(__file__).with_name("counterweight_arm_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt} (locked)")
