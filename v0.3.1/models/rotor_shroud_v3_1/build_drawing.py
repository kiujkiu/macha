"""
A3 drawing — rotor_shroud_v3_1 转子电路罩 (两半对开, 一张图管 A/B 两件)。
参数 import 自 build_shroud.py (单一数据源)。GB 1st-angle。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

# build_shroud 顶层就建模+导出, 不能整体 import; 只取参数块 (exec 到 STOP 标记前)
_src = (Path(__file__).parent / "build_shroud.py").read_text(encoding="utf-8")
_P = {}
_g = {"math": math, "Path": Path, "__file__": str(Path(__file__).parent / "build_shroud.py")}
exec(_src[:_src.index("def read_stl")], _g, _P)
OD, ID, R_OUT, R_IN, WALL = _P["OD"], _P["ID"], _P["R_OUT"], _P["R_IN"], _P["WALL"]
H, PLATE_T, PLATE_Z0 = _P["H"], _P["PLATE_T"], _P["PLATE_Z0"]
DISC_TOP = _P["DISC_TOP"]
SCR_HW, TEE_HW, TEE_Y0, SLOT_Y1 = _P["SCR_HW"], _P["TEE_HW"], _P["TEE_Y0"], _P["SLOT_Y1"]
COL_R, COL_ANG, COL_D = _P["COL_R"], _P["COL_ANG"], _P["COL_D"]
CWM_XS, CWM_Y, CWM_BOSS_D = _P["CWM_XS"], _P["CWM_Y"], _P["CWM_BOSS_D"]
CWM_BOSS_Z0, CWM_INS_D, CWM_INS_H = _P["CWM_BOSS_Z0"], _P["CWM_INS_D"], _P["CWM_INS_H"]
CWM_BORE_D = _P["CWM_BORE_D"]
WELL_D, FLOOR_T, BORE_D = _P["WELL_D"], _P["FLOOR_T"], _P["BORE_D"]
BOL_R_IN, BOL_HW = _P["BOL_R_IN"], _P["BOL_HW"]
LIP_T, LIP_Z0, LIP_Y = _P["LIP_T"], _P["LIP_Z0"], _P["LIP_Y"]
SEAM_GAP, RELIEF_CLR = _P["SEAM_GAP"], _P["RELIEF_CLR"]
SCR_ECC, SCR_X0, SCR_X1 = _P["SCR_ECC"], _P["SCR_X0"], _P["SCR_X1"]   # v3.1 非对称屏缝
LEAD_D, LEAD_H = 5.0, 0.8


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
def polyline(pts, w=GEOM_W, dash=None):
    if dash: pdf.set_dash_pattern(dash=dash[0], gap=dash[1])
    _w(w)
    for i in range(len(pts)-1):
        pdf.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    if dash: pdf.set_dash_pattern()

_w(0.3); pdf.rect(5, 5, PAGE_W-10, PAGE_H-10, style="D")
text(PAGE_W/2, 14, "POV 3D v3.1 — rotor_shroud_v3_1 转子电路罩 (两半对开; 本图管 A/B 两件)",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 20, f"筒 Φ{OD:g}/Φ{ID:g} 壁 {WALL:g} × 高 {H:g} (装配 {DISC_TOP:g}..{DISC_TOP+H:g} = 承载面→屏底) / "
     f"顶板 {PLATE_T:g} 厚 @ Z{PLATE_Z0:g}..{H:g} / 外壁与 rim_ring Φ170 盘缘齐平",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 25, f"屏缝 (v3.1 偏心屏, 非对称): X {SCR_X0:g}..{SCR_X1:g} (|Y|≤{TEE_Y0:g}) → ±{TEE_HW:g} ({TEE_Y0:g}..{SLOT_Y1:g}, 让 T 顶托 ±16); "
     f"|Y|>{SLOT_Y1:g} 顶板做实 = 屏缝两端封口 / 对开面 = 平面 Y=0, 单边间隙 {SEAM_GAP:g} (两半合计 {2*SEAM_GAP:g})",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 30, f"固定: 每半 2× 沉井立柱 Φ{COL_D:g} @ r{COL_R:g} — Φ{WELL_D:g} 井直通顶板, 井底 {FLOOR_T:g} 厚台肩 + Φ{BORE_D:g} 过孔 + Φ{BORE_D:g}→Φ{LEAD_D:g} 引导锥; "
     f"M3×12 坐井底 (头 Φ7.5 沉井内), 长螺丝刀顺井拧, 拧进 hub 底既有铜花螺母 (借 rim_ring 空闲外圈环孔, rim_ring 不改)",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 40, f"配重安装孔: 每半 2 个 (半A 在 Y+{CWM_Y:g}, 半B 在 Y−{CWM_Y:g} — **两半关于 Y=0 镜像, 不是 180° 旋转**), X {CWM_XS[0]:g}/{CWM_XS[1]:g} 即零件系 −X 侧跨接缝; "
     f"顶板下挂 Φ{CWM_BOSS_D:g} 凸台 Z{CWM_BOSS_Z0:g}..{H:g} + Φ{CWM_INS_D:g}×{CWM_INS_H:g} 铜花螺母窝 (罩内压入) + Φ{CWM_BORE_D:g} 过孔 (详图 C) — 配重件 counterweight_arm 骑顶跨缝, M3×16 ×4 把两半连成一体",
     size=TXT_I, anchor="middle")
text(PAGE_W/2, 35, f"加强: 立柱兼竖筋 / 接缝 bolster (内壁局部 Φ{2*BOL_R_IN:g}, |Y|≤{BOL_HW:g}) / 屏缝下翻边 (X ±{SCR_HW:g}..{SCR_HW+LIP_T:g}, Z{LIP_Z0:g}..{PLATE_Z0:g}, |Y|≤{LIP_Y:g}) — "
     f"打印: 绕 X 翻 180° 顶板贴床, 占地 170×85×50, 零支撑 (GB 1st-angle, mm)",
     size=TXT_I, anchor="middle")

# ===================== 俯视图 1:1 (半 A) =====================
S = 1.0
TX, TYC = 132.0, 182.0
def pv(x, y): return (TX + x*S, TYC - y*S)

text(TX, 52.0, "俯视图 (1:1) — 半 A (+Y 半); 半 B = 本件绕 Z 转 180°", size=TXT_L, anchor="middle")

def arc_pts(r, a0, a1, n=180):
    return [pv(r*math.cos(math.radians(a)), r*math.sin(math.radians(a)))
            for a in [a0 + (a1-a0)*i/n for i in range(n+1)]]

polyline(arc_pts(R_OUT, 0, 180))                     # 外径 R85
polyline(arc_pts(R_IN, 0, 180))                      # 内壁 R82
# 接缝线 (Y=SEAM_GAP)
polyline([pv(-R_OUT, SEAM_GAP), pv(-R_IN, SEAM_GAP)], GEOM_W)
polyline([pv(R_IN, SEAM_GAP), pv(R_OUT, SEAM_GAP)], GEOM_W)
# 顶板内边界 = 屏缝轮廓 (半 A 部分)
slot_edge = [pv(SCR_X1, SEAM_GAP), pv(SCR_X1, TEE_Y0), pv(TEE_HW, TEE_Y0),
             pv(TEE_HW, SLOT_Y1), pv(-TEE_HW, SLOT_Y1), pv(-TEE_HW, TEE_Y0),
             pv(SCR_X0, TEE_Y0), pv(SCR_X0, SEAM_GAP)]
polyline(slot_edge)
# 顶板与筒壁交线 (R82 已画) + 接缝处顶板边
polyline([pv(SCR_X1, SEAM_GAP), pv(R_IN, SEAM_GAP)], GEOM_W)
polyline([pv(-R_IN, SEAM_GAP), pv(SCR_X0, SEAM_GAP)], GEOM_W)
# 屏缝下翻边 (隐藏, 在顶板之下)
for x0, x1 in ((SCR_X1, SCR_X1 + LIP_T), (SCR_X0 - LIP_T, SCR_X0)):
    polyline([pv(x0, SEAM_GAP), pv(x0, LIP_Y), pv(x1, LIP_Y), pv(x1, SEAM_GAP)],
             HID_W, dash=(2.0, 1.2))
# bolster (内壁局部加厚, |Y|≤4)
for xs in (1.0, -1.0):
    ya = BOL_HW
    xa = math.sqrt(max(BOL_R_IN**2 - ya**2, 1.0))
    polyline([pv(xs*R_IN, SEAM_GAP), pv(xs*xa, SEAM_GAP), pv(xs*xa, ya)], GEOM_W)
    polyline(arc_pts(BOL_R_IN, math.degrees(math.asin(ya/BOL_R_IN)) if xs > 0 else 180-math.degrees(math.asin(ya/BOL_R_IN)),
                     0 if xs > 0 else 180, 12), GEOM_W)
# 沉井立柱 ×2 (半 A: 22.5° / 157.5°)
for a in [a for a in COL_ANG if math.sin(math.radians(a)) > 0]:
    cx, cy = pv(COL_R*math.cos(math.radians(a)), COL_R*math.sin(math.radians(a)))
    _w(GEOM_W); pdf.circle(cx, cy, COL_D/2*S, style="D")     # 立柱外径 Φ14
    pdf.circle(cx, cy, WELL_D/2*S, style="D")                # 沉井 Φ9
    pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
    pdf.circle(cx, cy, BORE_D/2*S, style="D")                # 过孔 (隐藏)
    pdf.set_dash_pattern(); _w(GEOM_W); cross(cx, cy, 9.0)

# 配重安装孔 (半 A 的 2 个: X -50/-72 @ Y+14) — 凸台/螺母窝在顶板之下 = 隐藏
_cwm_A = [(x, CWM_Y) for x in CWM_XS]
for (mx, my) in _cwm_A:
    cp = pv(mx, my)
    pdf.set_dash_pattern(dash=2.0, gap=1.2); _w(HID_W)
    pdf.circle(*cp, CWM_BOSS_D/2*S, style="D")               # 凸台 Φ9 (隐藏)
    pdf.circle(*cp, CWM_INS_D/2*S, style="D")                # 铜花螺母窝 (隐藏)
    pdf.set_dash_pattern(); _w(GEOM_W)
    pdf.circle(*cp, CWM_BORE_D/2*S, style="D")               # Φ3.4 过孔 (可见)
    cross(*cp, 8.0)

# 尺寸
hdim(pv(-R_OUT, 0)[0], pv(R_OUT, 0)[0], pv(0, 0)[1], TYC+16, f"Φ{OD:g} (= rim_ring 盘缘)")
hdim(pv(SCR_X0, 0)[0], pv(SCR_X1, 0)[0], pv(0, TEE_Y0/2)[1], TYC+30, f"{SCR_X1-SCR_X0:.1f} 屏缝 (X{SCR_X0:g}..{SCR_X1:g})")
vdim(pv(0, SLOT_Y1)[1], pv(0, SEAM_GAP)[1], pv(-R_OUT, 0)[0], pv(-R_OUT, 0)[0]-DIM_O1, f"{SLOT_Y1:g}")
vdim(pv(0, TEE_Y0)[1], pv(0, SEAM_GAP)[1], pv(-R_OUT, 0)[0], pv(-R_OUT, 0)[0]-DIM_O2-8, f"{TEE_Y0:g}")

_ca = [a for a in COL_ANG if math.sin(math.radians(a)) > 0][0]
_cp = pv(COL_R*math.cos(math.radians(_ca)), COL_R*math.sin(math.radians(_ca)))
note(_cp[0], _cp[1], 330, 62, f"沉井立柱 Φ{COL_D:g} @ r{COL_R:g}, 零件系 22.5°/157.5° "
     f"(装配 337.5°/112.5°) — 详图 B", anchor="start")
_sp = pv(TEE_HW, (TEE_Y0+SLOT_Y1)/2)
note(_sp[0], _sp[1], 300, 78, f"屏缝加宽段 ±{TEE_HW:g} (让 T 件顶托)", anchor="start")
note(*pv(CWM_XS[1], CWM_Y), 30, 88, f"配重安装凸台 ×2 (半A) @ X{CWM_XS[0]:g}/{CWM_XS[1]:g}, Y+{CWM_Y:g} — 详图 C", anchor="start")
note(*pv(CWM_XS[0], CWM_Y), 30, 94, f"半B 是这两个孔关于 Y=0 的镜像 (X 同, Y−{CWM_Y:g})", anchor="start")

# ===================== 剖视 A-A 1:1 (过沉井的径向剖) =====================
EX, EYB = 300.0, 200.0
def ev(r, z): return (EX + (r-COL_R)*S*1.0, EYB - z*S)
text(EX, 112.0, "剖视 A-A (1:1) — 过沉井立柱的径向剖", size=TXT_L, anchor="middle")
# 筒壁 + 立柱 合成外轮廓 (r 70.5..85), 高 0..50
polyline([ev(R_OUT, 0), ev(R_OUT, H), ev(COL_R-COL_D/2, H), ev(COL_R-COL_D/2, 0), ev(R_OUT, 0)])
# 沉井
polyline([ev(COL_R-WELL_D/2, H), ev(COL_R-WELL_D/2, FLOOR_T), ev(COL_R-LEAD_D/2, FLOOR_T)])
polyline([ev(COL_R+WELL_D/2, H), ev(COL_R+WELL_D/2, FLOOR_T), ev(COL_R+LEAD_D/2, FLOOR_T)])
# 引导锥 + 过孔
polyline([ev(COL_R-LEAD_D/2, FLOOR_T), ev(COL_R-BORE_D/2, FLOOR_T-LEAD_H), ev(COL_R-BORE_D/2, 0)])
polyline([ev(COL_R+LEAD_D/2, FLOOR_T), ev(COL_R+BORE_D/2, FLOOR_T-LEAD_H), ev(COL_R+BORE_D/2, 0)])
# 顶板 (r < 70.5 一侧, 示意到 r=40)
polyline([ev(COL_R-COL_D/2, PLATE_Z0), ev(40.0, PLATE_Z0)])
polyline([ev(COL_R-COL_D/2, H), ev(40.0, H)])
polyline([ev(40.0, PLATE_Z0), ev(40.0, H)], HID_W, dash=(2.0, 1.2))
cross(*ev(COL_R, H/2), r=8.0)

vdim(ev(0, H)[1], ev(0, 0)[1], ev(R_OUT, 0)[0], ev(R_OUT, 0)[0]+DIM_O1, f"{H:g}")
vdim(ev(0, H)[1], ev(0, PLATE_Z0)[1], ev(40.0, 0)[0], ev(40.0, 0)[0]-DIM_O1, f"{PLATE_T:g} 顶板")
vdim(ev(0, FLOOR_T)[1], ev(0, 0)[1], ev(R_OUT, 0)[0], ev(R_OUT, 0)[0]+DIM_O2+6, f"{FLOOR_T:g} 井底台肩")
hdim(ev(COL_R-WELL_D/2, 0)[0], ev(COL_R+WELL_D/2, 0)[0], ev(0, H)[1], ev(0, H)[1]-DIM_O1, f"Φ{WELL_D:g} 沉井")
note(*ev(R_OUT, H*0.75), 372, 150, f"壁 {WALL:g} (Φ{OD:g}/Φ{ID:g})", anchor="end")

# ===================== 详图 C — 配重安装凸台 (剖, 4:1) =====================
CS, CX, CYB = 4.0, 250.0, 100.0
def cv(dx, z): return (CX + dx*CS, CYB - (z - CWM_BOSS_Z0)*CS)
text(CX, 50.0, "详图 C — 配重安装凸台 (剖, 4:1)", size=TXT_L, anchor="middle")
_ins_z1 = CWM_BOSS_Z0 + CWM_INS_H
# 轮廓: 顶板 (左右各延伸 11) + 凸台
polyline([cv(-11.0, PLATE_Z0), cv(-CWM_BOSS_D/2, PLATE_Z0), cv(-CWM_BOSS_D/2, CWM_BOSS_Z0),
          cv(CWM_BOSS_D/2, CWM_BOSS_Z0), cv(CWM_BOSS_D/2, PLATE_Z0), cv(11.0, PLATE_Z0)])
polyline([cv(-11.0, H), cv(11.0, H)])
polyline([cv(-11.0, PLATE_Z0), cv(-11.0, H)]); polyline([cv(11.0, PLATE_Z0), cv(11.0, H)])
_w(GEOM_W)
for sgn in (1.0, -1.0):                                   # 铜花螺母窝 Φ4.2 (z 43..47)
    pdf.line(*cv(sgn*CWM_INS_D/2, CWM_BOSS_Z0), *cv(sgn*CWM_INS_D/2, _ins_z1))
    pdf.line(*cv(sgn*CWM_BORE_D/2, _ins_z1), *cv(sgn*CWM_INS_D/2, _ins_z1))
    pdf.line(*cv(sgn*CWM_BORE_D/2, _ins_z1), *cv(sgn*CWM_BORE_D/2, H))   # Φ3.4 过孔到顶面
line(*cv(0, CWM_BOSS_Z0-2.5), *cv(0, H+2.5), DIM_W)       # 中心线
hdim(cv(-CWM_BOSS_D/2, 0)[0], cv(CWM_BOSS_D/2, 0)[0], cv(0, CWM_BOSS_Z0)[1],
     cv(0, CWM_BOSS_Z0)[1]+11.0, f"Φ{CWM_BOSS_D:g} 凸台")
hdim(cv(-CWM_BORE_D/2, 0)[0], cv(CWM_BORE_D/2, 0)[0], cv(0, H)[1],
     cv(0, H)[1]-10.0, f"Φ{CWM_BORE_D:g} M3 通")
vdim(cv(0, H)[1], cv(0, CWM_BOSS_Z0)[1], cv(11.0, 0)[0], cv(11.0, 0)[0]+14.0,
     f"{H-CWM_BOSS_Z0:g} 总厚")
vdim(cv(0, _ins_z1)[1], cv(0, CWM_BOSS_Z0)[1], cv(-CWM_BOSS_D/2, 0)[0],
     cv(-CWM_BOSS_D/2, 0)[0]-13.0, f"{CWM_INS_H:g} 窝深")
note(*cv(CWM_INS_D/2, CWM_BOSS_Z0 + CWM_INS_H/2), 214.0, 120.0,
     f"Φ{CWM_INS_D:g}×{CWM_INS_H:g} 铜花螺母窝 (M3×4×4.5) — **扣半罩前从罩内压入**", anchor="start")

# ===================== 详图 B 沉井底 (4:1) =====================
DS = 4.0
DX, DYB = 300.0, 268.0
def dv(r, z): return (DX + (r-COL_R)*DS, DYB - z*DS)
text(DX, 226.0, "详图 B — 沉井底 (4:1)", size=TXT_L, anchor="middle")
polyline([dv(COL_R-COL_D/2, 8.0), dv(COL_R-COL_D/2, 0), dv(COL_R+COL_D/2, 0), dv(COL_R+COL_D/2, 8.0)])
polyline([dv(COL_R-WELL_D/2, 8.0), dv(COL_R-WELL_D/2, FLOOR_T), dv(COL_R-LEAD_D/2, FLOOR_T),
          dv(COL_R-BORE_D/2, FLOOR_T-LEAD_H), dv(COL_R-BORE_D/2, 0)])
polyline([dv(COL_R+WELL_D/2, 8.0), dv(COL_R+WELL_D/2, FLOOR_T), dv(COL_R+LEAD_D/2, FLOOR_T),
          dv(COL_R+BORE_D/2, FLOOR_T-LEAD_H), dv(COL_R+BORE_D/2, 0)])
hdim(dv(COL_R-LEAD_D/2, 0)[0], dv(COL_R+LEAD_D/2, 0)[0], dv(0, FLOOR_T)[1], dv(0, FLOOR_T)[1]-9, f"Φ{LEAD_D:g} 引导锥口")
hdim(dv(COL_R-BORE_D/2, 0)[0], dv(COL_R+BORE_D/2, 0)[0], dv(0, 0)[1], dv(0, 0)[1]+11, f"Φ{BORE_D:g} 过孔")
vdim(dv(0, FLOOR_T)[1], dv(0, 0)[1], dv(COL_R+COL_D/2, 0)[0], dv(COL_R+COL_D/2, 0)[0]+DIM_O1, f"{FLOOR_T:g}")
note(*dv(COL_R+LEAD_D/2-0.2, FLOOR_T-LEAD_H/2), 372, 246,
     f"45° 引导锥 Φ{BORE_D:g}→Φ{LEAD_D:g} (深 {LEAD_H:g}): 捕捉半径 1.0 > 螺丝在 Φ9 井里的最大偏心 0.75 mm", anchor="end")
note(*dv(COL_R-WELL_D/2+0.2, FLOOR_T+1.2), 232, 238,
     "M3×12 头 Φ7.5 压 Φ5..Φ7.5 环面 (承压环宽 1.25 mm)", anchor="end")

# ===================== A / B 差异说明 =====================
bx, by = 20.0, 236.0
_w(0.3); pdf.rect(bx, by, 205.0, 32.0, style="D")
text(bx+3, by+6, "A / B 两件差异 (基础几何 180° 旋转对称; 让位特征 + 配重安装孔不同):", size=TXT_I)
text(bx+3, by+12, f"· 半 A (+Y 半): 立柱 零件系 22.5°/157.5°; 含 wifi_shell 内壁让位窝 (让位间隙 {RELIEF_CLR:g} mm)", size=TXT_I)
text(bx+3, by+18, "· 半 B (-Y 半): 立柱 零件系 202.5°/337.5°; 含 usb_wifi 线缆出口槽 (通到底边, 供罩子竖直落下)", size=TXT_I)
text(bx+3, by+24, "· 两件均含 portal_tee 脚角让位窝 ×2 (外皮 0.99 mm) 与 wifi 沿最外 M3 头让位窝 (外皮 1.91 mm)", size=TXT_I)
text(bx+3, by+30, f"· 配重安装凸台: 两件各 2 个, X {CWM_XS[0]:g}/{CWM_XS[1]:g} 上 **半A 在 Y+{CWM_Y:g} / 半B 在 Y−{CWM_Y:g} —— 关于 Y=0 镜像, 不是 180° 旋转**", size=TXT_I)

tb_y = PAGE_H-28; tb_x, tb_w, tb_h = 20, PAGE_W-40, 18
_w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
text(tb_x+4, tb_y+6, "POV 3D v3.1 结构件 — rotor_shroud_v3_1 转子电路罩 (屏底以下全封闭)", size=TXT_L)
text(tb_x+tb_w-4, tb_y+6, "投影 1st-angle / 比例 1:1 (详图 4:1)", size=TXT_I, anchor="end")
text(tb_x+4, tb_y+14.5, f"Φ{OD:g}/Φ{ID:g}×{H:g}, 壁 {WALL:g}, 顶板 {PLATE_T:g} / 每件 ~68 cm3 (约 87 g PLA) / "
     f"BOM: M3×12 (头 Φ7.5) ×4 → hub 底既有铜花螺母; 配重安装 M3×4×4.5 铜花螺母 ×2 (罩内压入) — 配重件 counterweight_arm 另出图 / 打印: 顶板贴床, 零支撑 / 单位 mm", size=TXT_I)
text(tb_x+tb_w-4, tb_y+14.5, "2026-08-03  /  POV3D / v3.1 / rotor_shroud_v3_1 / shroud_half_A_v3_1.stl + shroud_half_B_v3_1.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("rotor_shroud_v3_1_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("rotor_shroud_v3_drawing.NEW.pdf")
    pdf.output(str(alt)); print(f"wrote {alt} (locked)")
