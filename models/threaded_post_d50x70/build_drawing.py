"""
A3 landscape 2D engineering drawing for threaded_post_d50x70 (螺纹柱).

  1) 主视图 沿 0° 筋全剖 (2:1) — Φ50 空心下柱 (壁/筋/顶板/过渡为 50 kg 受力分析定稿 FB) + 外螺纹柱高 15 (中空壁厚 3),
                                 顶端倒角 C1.5; GB: 肋纵剖不画剖面线, 螺纹剖面线画到大径粗实线
  2) B-B 横剖 (1:1)            — 筒壁环 + 米字加强筋 ×4 (厚 RIB_T)
  3) 详图 A (20:1)             — 螺纹牙型轴向剖面: 螺距 3 / 牙顶、牙底平台 / 牙高 1 / 牙型角 60°
  4) 详图 C (2.5:1)            — 筒壁/米字筋与顶板 45° 过渡 (直角边 GUSSET, 腔顶无水平面, 免支撑)

⚠ 参数是从 build_stl.py **复刻**的 (项目惯例, 不 import) —— 改 build_stl 必须同步这里。
"""
import math
from pathlib import Path

import numpy as np
from fpdf import FPDF
from shapely.geometry import LineString, Point, Polygon, box
from shapely.affinity import affine_transform, rotate as s_rotate
from shapely.ops import polylabel, unary_union

# ===== Geometry (must match build_stl.py / threaded_post_d50x70.scad) =====
BASE_D   = 50.0
BASE_H   = 70.0
THR_H    = 15.0
THR_MAJ  = 27.5     # 改⑥ (原 26.5)
THR_MIN  = 24.5
PITCH    = 3.0
WALL     = 2.52     # 改⑥ 50 kg 定稿 FB (F1 2.94)
RIB_T    = 3.36
THR_CLEAR = 0.0     # 改⑥ 直接按 27.5/24.5 建模 (F1 0.4)
BOT_CH    = 0.3
GUSSET    = 6.2     # 改⑥ (F1 6.0)
FLANK_ANGLE = 60.0
RIGHT_HAND  = True
CHAMFER     = 1.75  # 改⑥ (F1 1.5; 牙高 1.5 时 C1.5 顶端半径 = 小径半径)
PLATE_T     = 2.52  # 改⑥ (F1 3.36)
STUD_WALL   = 3.0   # 改⑥ 螺纹柱中空, 壁厚从牙底量
BORE_D      = THR_MIN - 2 * STUD_WALL   # 18.5
BORE_DEPTH  = THR_H                     # 盲孔深 15, 孔底在台阶面
RIB_ANGLES  = (0, 45, 90, 135)

R_BASE = BASE_D / 2
R_MAJ, R_MIN = (THR_MAJ - THR_CLEAR) / 2, (THR_MIN - THR_CLEAR) / 2   # 实际建模 (已扣打印间隙)
DEPTH  = R_MAJ - R_MIN
FLANK_RUN = DEPTH * math.tan(math.radians(FLANK_ANGLE / 2))
CREST  = (PITCH - 2 * FLANK_RUN) / 2
ROOT   = PITCH - 2 * FLANK_RUN - CREST
Z_TOP  = BASE_H + THR_H
R_CH_TOP = R_MAJ - CHAMFER
R_CAV  = R_BASE - WALL
R_BORE = BORE_D / 2
Z_CEIL = BASE_H - PLATE_T
HC  = CREST / 2                  # 牙顶半宽
HB0 = CREST / 2 + FLANK_RUN      # 牙根 (小径处) 半宽
HAND = "右" if RIGHT_HAND else "左"

def prof_r(dz):
    """离最近牙顶中心轴向距离 dz 处的半径 (牙型)。"""
    d = abs(dz - PITCH * round(dz / PITCH))
    if d <= HC:  return R_MAJ
    if d <= HB0: return R_MAJ - (d - HC) / FLANK_RUN * DEPTH
    return R_MIN

# 米字筋 (俯视, 真圆近似) 与内腔的交
_strip = box(-R_BASE, -RIB_T / 2, R_BASE, RIB_T / 2)
RIBS = unary_union([s_rotate(_strip, a, origin=(0, 0)) for a in RIB_ANGLES])
_rib_area = RIBS.intersection(Point(0, 0).buffer(R_CAV, quad_segs=2048)).area
# 腔被筋分成的 8 格: 内切圆半径 = 45° 过渡要盖满腔顶所需的最小直角边
_cells = Point(0, 0).buffer(R_CAV, quad_segs=256).difference(RIBS)
assert len(_cells.geoms) == 2 * len(RIB_ANGLES)
R_INSC = max(c.exterior.distance(polylabel(c, 1e-3)) for c in _cells.geoms)
assert GUSSET > R_INSC, f"45° 过渡盖不满腔顶: {GUSSET} <= {R_INSC}"

# 实心体积: 下柱 (扣腔、加筋) + 螺纹段逐层积分 (每层截面 = π/P ∫ min(R(u), R_倒角(z))² du) − 内孔
_u = (np.arange(6000) + 0.5) / 6000 * PITCH
_R_u = np.array([prof_r(u) for u in _u])
_z = BASE_H + (np.arange(3000) + 0.5) / 3000 * THR_H
_Rc = np.where(CHAMFER > 0, R_CH_TOP + (Z_TOP - _z), 1e9)
_A = math.pi * np.mean(np.minimum(_R_u[None, :], _Rc[:, None])**2, axis=1)
_ts = (np.arange(200) + 0.5) / 200 * GUSSET          # 45° 过渡段: 腔截面 = 8 格向内偏移 t
_gus_cav = float(np.mean([_cells.buffer(-t, join_style="mitre").area for t in _ts])) * GUSSET
VOL = (math.pi * R_BASE**2 * BASE_H - (math.pi * R_CAV**2 - _rib_area) * (Z_CEIL - GUSSET) - _gus_cav
       + float(np.mean(_A)) * THR_H - math.pi * R_BORE**2 * BORE_DEPTH
       - 2 * math.pi * (R_BASE - BOT_CH / 3) * BOT_CH**2 / 2)          # 底边倒角 (三角形回转)

# ===== PDF setup =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

GEOM_W = 0.50
THIN_W = 0.22
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
def polyline(pts, w=DIM_W):
    _w(w)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        pdf.line(x0, y0, x1, y1)
def arrow(tx, ty, dx, dy, al=ARR_L, aw=ARR_W):
    L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
    bx, by = tx - al*ux, ty - al*uy
    px, py = -uy, ux
    pdf.set_fill_color(0, 0, 0)
    pdf.polygon([(tx, ty), (bx + aw*px, by + aw*py),
                 (bx - aw*px, by - aw*py)], style="F")

# SimHei 缺这几个字形 (见 feedback_pdf_drawing_lessons): 落笔前统一替换
_GLYPH_FIX = {"−": "-", "⇒": "=>", "⚠": "※", "Ø": "Φ", "ø": "Φ", "•": "·", "⨯": "×", "∅": "Φ", "³": "^3", "²": "^2"}
def _g(s):
    s = str(s)
    for a, b in _GLYPH_FIX.items():
        if a in s: s = s.replace(a, b)
    return s
def text(x, y, s, size=TXT_D, anchor="start", halo=False):
    """halo=True: 字后垫白底, 挡住穿过文字的线 (verify_drawing 会跳过白色填充)。"""
    s = _g(s)
    pdf.set_font("SimHei", "", size)
    sw = pdf.get_string_width(s)
    if   anchor == "middle": x -= sw/2
    elif anchor == "end":    x -= sw
    if halo:
        fh = pdf.font_size
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(x - 0.4, y - fh * 0.85, sw + 0.8, fh * 1.1, style="F")
    pdf.text(x, y, s)
def str_w(s, size):
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

def hdim(x1, x2, yg, yd, label, outside=False):
    label = _with_unit(label)
    if yd > yg: ey1, ey2 = yg + EXT_GP, yd + EXT_OV
    else:       ey1, ey2 = yg - EXT_GP, yd - EXT_OV
    line(x1, ey1, x1, ey2, EXT_W)
    line(x2, ey1, x2, ey2, EXT_W)
    x_l, x_r = (x1, x2) if x1 < x2 else (x2, x1)
    if x_r - x_l >= 2 * ARR_L + 1 and not outside:
        line(x_l, yd, x_r, yd, DIM_W)
        arrow(x_l, yd, -1, 0); arrow(x_r, yd, 1, 0)
    else:
        ext = ARR_L + 1.0
        line(x_l - ext, yd, x_r + ext, yd, DIM_W)
        arrow(x_l, yd,  1, 0); arrow(x_r, yd, -1, 0)
    text((x_l + x_r) / 2, yd - 1.8, label, anchor="middle")

def vdim(y1, y2, xg, xd, label, outside=False):
    """xg 可给 (xg1, xg2): 两条尺寸界线各自从不同的 x 引出。"""
    label = _with_unit(label)
    xg1, xg2 = xg if isinstance(xg, tuple) else (xg, xg)
    side = 1.0 if xd > xg1 else -1.0
    to = 4.0 * side
    line(xg1 + side*EXT_GP, y1, xd + side*EXT_OV, y1, EXT_W)
    line(xg2 + side*EXT_GP, y2, xd + side*EXT_OV, y2, EXT_W)
    y_top, y_bot = (y1, y2) if y1 < y2 else (y2, y1)
    gap = y_bot - y_top
    if gap >= 2 * ARR_L + 1 and not outside:
        line(xd, y_top, xd, y_bot, DIM_W)
        arrow(xd, y_top, 0, -1); arrow(xd, y_bot, 0, 1)
    else:
        ext = ARR_L + 1.0
        line(xd, y_top - ext, xd, y_bot + ext, DIM_W)
        arrow(xd, y_top, 0,  1); arrow(xd, y_bot, 0, -1)
    lh = str_w(label, TXT_D)
    if gap >= lh + 1.0 or not outside:
        rot_text(xd + to, (y_top + y_bot) / 2, label, angle_deg=90, anchor="middle")
    else:
        rot_text(xd + to, y_top - (ARR_L + 1.0) - lh / 2 - 1.0,
                 label, angle_deg=90, anchor="middle")

def leader(tip, bend, land_x, label, size=TXT_D, dot=False):
    """引线: 尖点 → 折点 → 水平落笔段, 文字写在落笔段上方。
    折点必须在尖点的落笔段一侧, 否则箭头会反向。dot=True: 指向面内部 (如筋) 用圆点代替箭头。"""
    (tx, ty), (bx, by) = tip, bend
    line(bx, by, tx, ty, DIM_W)
    line(land_x, by, bx, by, DIM_W)
    if dot:
        pdf.set_fill_color(0, 0, 0); pdf.circle(tx, ty, 0.7, style="F")
    else:
        arrow(tx, ty, tx - bx, ty - by)
    x0 = min(land_x, bx) + 2.0
    assert x0 + str_w(label, size) <= max(land_x, bx) - 1.0, f"引线文字超出落笔段: {label}"
    text(x0, by - 1.8, label, size=size)

def wavy(p, q, amp=0.8, wl=7.0):
    """波浪线 (断裂边界, 细实线)。"""
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    n = max(12, int(L / wl * 16))
    pts = []
    for i in range(n + 1):
        s = L * i / n
        o = amp * math.sin(2 * math.pi * s / wl)
        pts.append((x0 + ux*s - uy*o, y0 + uy*s + ux*o))
    polyline(pts, THIN_W)

def hatch(geom, step=2.2):
    """45° 剖面线, 裁到 shapely 几何 (纸面坐标, 可带洞) 内。"""
    minx, miny, maxx, maxy = geom.bounds
    H = (maxy - miny) + (maxx - minx)
    _w(0.15)
    c = minx - H
    while c <= maxx:
        cut = geom.intersection(LineString([(c, maxy), (c + H, maxy - H)]))
        for sg in getattr(cut, "geoms", [cut]):
            if sg.is_empty or sg.geom_type != "LineString": continue
            (ax, ay), (bx, by) = sg.coords[0], sg.coords[-1]
            pdf.line(ax, ay, bx, by)
        c += step

def outline(geom, w=GEOM_W):
    for p in getattr(geom, "geoms", [geom]):
        polyline(list(p.exterior.coords), w)
        for ring in p.interiors:
            polyline(list(ring.coords), w)

def centerline(x1, y1, x2, y2):
    pdf.set_dash_pattern(dash=6, gap=1.5); _w(0.15)
    pdf.line(x1, y1, x2, y2)
    pdf.set_dash_pattern()

# ===== Page frame & title =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 14,
     f"螺纹柱  threaded_post_d50x70   Φ{BASE_D:g}×{BASE_H:g} + 外螺纹 Φ{THR_MAJ:g}×P{PITCH:g}",
     size=TXT_T, anchor="middle")
text(PAGE_W/2, 19.5,
     f"下部圆柱 Φ{BASE_D:g} / 高 {BASE_H:g}  ·  上部外螺纹柱高 {THR_H:g}, 大径 Φ{THR_MAJ:g} / 小径 Φ{THR_MIN:g} / "
     f"螺距 {PITCH:g}  ·  壁 {WALL:g} / 米字筋 {RIB_T:g} / 顶板 {PLATE_T:g}  ·  总高 {Z_TOP:g}  ·  "
     f"单件承重 50 kg 定稿 (PETG, 100% 实心; 螺纹柱中空壁厚 {STUD_WALL:g})",
     size=TXT_I, anchor="middle")

# ===== 主视图 沿 0° 筋全剖 (2:1) =====
S = 2.0
FX, FY = 120, 228
def fv(x, z): return (FX + x * S, FY - z * S)
def to_fv(g): return affine_transform(g, [S, 0, 0, -S, FX, FY])

text(FX, 31, "主视图 (沿 0° 筋全剖)  (2:1)   尺寸单位: mm", size=TXT_L, anchor="middle")
text(FX, 36.5, f"(外螺纹 {HAND}旋单线, 非标; 牙型见详图 A)", size=TXT_I, anchor="middle")

_outer = Polygon([(-R_BASE + BOT_CH, 0), (R_BASE - BOT_CH, 0), (R_BASE, BOT_CH), (R_BASE, BASE_H), (R_MAJ, BASE_H),
                  (R_MAJ, Z_TOP - CHAMFER), (R_CH_TOP, Z_TOP), (-R_CH_TOP, Z_TOP),
                  (-R_MAJ, Z_TOP - CHAMFER), (-R_MAJ, BASE_H), (-R_BASE, BASE_H), (-R_BASE, BOT_CH)])
_cav  = Polygon([(-R_CAV, 0), (R_CAV, 0), (R_CAV, Z_CEIL - GUSSET), (R_CAV - GUSSET, Z_CEIL),
                 (-(R_CAV - GUSSET), Z_CEIL), (-R_CAV, Z_CEIL - GUSSET)])
# ↑ 被 0° 筋纵剖占满, GB 不画剖面线; 两上角 = 筒壁与腔顶 45° 过渡 (随筒壁画剖面线)
_sec_real = _outer.difference(_cav)
if BORE_D > 0:
    _sec_real = _sec_real.difference(box(-R_BORE, Z_TOP - BORE_DEPTH, R_BORE, Z_TOP + 1))
_sec  = to_fv(_sec_real)
hatch(_sec)
outline(_sec)
line(*fv(-R_CAV, 0), *fv(R_CAV, 0), GEOM_W)          # 筋底边
# 小径细实线: 画进倒角, 止于与倒角线相交处; 螺纹终止线 (粗) 只画在牙高范围
z_minor_end = Z_TOP - max(0.0, R_MIN - R_CH_TOP)
for sx in (-1, 1):
    line(*fv(sx * R_MIN, BASE_H), *fv(sx * R_MIN, z_minor_end), THIN_W)
    line(*fv(sx * R_MIN, BASE_H), *fv(sx * R_MAJ, BASE_H), GEOM_W)
centerline(*fv(0, -3), *fv(0, Z_TOP + 4))

text(fv(R_CAV / 2, 0)[0], fv(0, Z_CEIL * 0.55)[1], "加强筋纵剖", size=TXT_D, anchor="middle")
text(fv(R_CAV / 2, 0)[0], fv(0, Z_CEIL * 0.55)[1] + 5.5, "(不画剖面线)", size=TXT_I, anchor="middle")

# ---- 主视尺寸 ----
hdim(fv(-R_CAV, 0)[0], fv(R_CAV, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O1, f"Φ{2*R_CAV:g}")
hdim(fv(-R_BASE, 0)[0], fv(R_BASE, 0)[0], fv(0, 0)[1], fv(0, 0)[1] + DIM_O2, f"Φ{BASE_D:g}")
if BORE_D > 0:
    hdim(fv(-R_BORE, 0)[0], fv(R_BORE, 0)[0], fv(0, Z_TOP)[1], fv(0, Z_TOP)[1] - DIM_O1, f"Φ{2*R_BORE:g}")
_xO1 = fv(R_BASE, 0)[0] + DIM_O1
_xO2 = fv(R_BASE, 0)[0] + DIM_O2
vdim(fv(0, BASE_H)[1], fv(0, 0)[1], fv(R_BASE, 0)[0], _xO1, f"{BASE_H:g}")
vdim(fv(0, Z_TOP)[1], fv(0, BASE_H)[1], (fv(R_CH_TOP, 0)[0], fv(R_BASE, 0)[0]), _xO1, f"{THR_H:g}")
vdim(fv(0, Z_TOP)[1], fv(0, 0)[1], (fv(R_CH_TOP, 0)[0], fv(R_BASE, 0)[0]), _xO2, f"{Z_TOP:g}")
# 腔深 (= 筋高): 画在腔内左半, 底边界线沿筋底
vdim(fv(0, Z_CEIL)[1], fv(0, 0)[1], (fv(-(R_CAV - GUSSET), 0)[0], fv(-R_CAV, 0)[0]),   # 上界线从 45° 过渡上端引出
     fv(-R_CAV + 8, 0)[0], f"{Z_CEIL:g}")
if BORE_D > 0:                         # 内孔深: 画在孔内左半
    vdim(fv(0, Z_TOP)[1], fv(0, Z_TOP - BORE_DEPTH)[1], fv(-R_BORE, 0)[0], fv(-R_BORE + 2.75, 0)[0],
         f"{BORE_DEPTH:g}")
# 螺纹 + 倒角: 左侧引线
_th_tip = fv(-R_MAJ, BASE_H + 7)
leader(_th_tip, (_th_tip[0] - 8, _th_tip[1]), 28, f"大径 Φ{2*R_MAJ:g} / 小径 Φ{2*R_MIN:g} / P{PITCH:g}")
_th_note = (f"(名义 Φ{THR_MAJ:g}/Φ{THR_MIN:g}, 已缩 {THR_CLEAR:g} 打印间隙)" if THR_CLEAR > 0
            else "(直接按此尺寸建模, 不留打印间隙)")
assert 30 + str_w(_th_note, TXT_I) < fv(-R_MAJ, 0)[0] - 3, "螺纹名义尺寸注释压到螺纹柱"
text(30, _th_tip[1] + 5.0, _th_note, size=TXT_I)
_ch_mid = fv(-(R_MAJ - CHAMFER / 2), Z_TOP - CHAMFER / 2)
leader(_ch_mid, (_ch_mid[0] - 11, _ch_mid[1] - 11.5), 36, f"C{CHAMFER:g} (45° 倒角)")
# 底边倒角 (防象脚)
_bc_mid = fv(-(R_BASE - BOT_CH / 2), BOT_CH / 2)
leader(_bc_mid, (_bc_mid[0] - 12, _bc_mid[1] + 12), 30, f"C{BOT_CH:g} (防象脚)")

# 剖切符号 B-B (Z = 腔深一半): 轮廓外两端粗短划 + 向下看的箭头
_zb = round(Z_CEIL * 0.45)
_yb = fv(0, _zb)[1]
for sx in (-1, 1):
    x_in, x_out = fv(sx * (R_BASE + 1.5), 0)[0], fv(sx * (R_BASE + 4.5), 0)[0]
    line(x_in, _yb, x_out, _yb, 0.6)
    line(x_out, _yb, x_out, _yb + 4.0, DIM_W)
    arrow(x_out, _yb + 6.5, 0, 1, al=3.0, aw=1.1)
    text(x_out - sx * 3.2, _yb + 7.5, "B", size=TXT_L, anchor="middle")

# 详图 A 标记圈 (右侧螺纹中段)
_acx, _acy = fv(R_MAJ - DEPTH / 2, BASE_H + 9.5)
_w(0.25); pdf.circle(_acx, _acy, 7.5, style="D")
text(_acx + 9.0, _acy + 4.0, "A", size=TXT_L)
# 详图 C 标记圈 (右侧筒壁与腔顶 45° 过渡)
_ccx, _ccy = fv(R_CAV - GUSSET / 2, Z_CEIL - GUSSET / 2)
_w(0.25); pdf.circle(_ccx, _ccy, 7.0, style="D")
text(fv(R_BASE, 0)[0] + 4.0, _ccy + 3.0, "C", size=TXT_L)

# ===== B-B 横剖 (1:1) =====
BS = 1.0
BCX, BCY = 381.0, 92.0
def to_bv(g): return affine_transform(g, [BS, 0, 0, -BS, BCX, BCY])

text(BCX, 50, "B-B  (1:1)", size=TXT_L, anchor="middle")
text(BCX, 56.5, f"米字加强筋 ×{len(RIB_ANGLES)}", size=TXT_I, anchor="middle")

_ring = Point(0, 0).buffer(R_BASE, quad_segs=64).difference(Point(0, 0).buffer(R_CAV, quad_segs=64))
_bsec = to_bv(unary_union([_ring, RIBS.intersection(Point(0, 0).buffer(R_BASE - 0.01, quad_segs=64))]))
hatch(_bsec, step=1.6)
outline(_bsec)
centerline(BCX - R_BASE - 4, BCY, BCX + R_BASE + 4, BCY)
centerline(BCX, BCY - R_BASE - 4, BCX, BCY + R_BASE + 4)
_a = math.radians(225)                                # 45° 筋的左下臂
leader((BCX + 12 * math.cos(_a), BCY - 12 * math.sin(_a)), (BCX - 17, BCY + R_BASE + 9), BCX + 6,
       f"筋厚 {RIB_T:g} mm", dot=True)

# ===== 详图 C (2.5:1): 右侧筒壁与腔顶 45° 过渡 (米字筋两侧与顶板同样过渡) =====
CS_ = 2.5
CX0, CY0 = 352.0, 152.0                                  # 纸面上 x=CXL / z=BASE_H 的位置
CXL, CZB = R_CAV - GUSSET - 1.0, Z_CEIL - GUSSET - 4.0    # 视图左边界 (顶板断开) / 下边界 (筒壁断开)
def dc(x, z): return (CX0 + (x - CXL) * CS_, CY0 - (z - BASE_H) * CS_)
_cmx = dc((CXL + R_BASE) / 2, 0)[0]
text(_cmx, 140, f"详图 C  ({CS_:g}:1)", size=TXT_L, anchor="middle")
text(_cmx, 146, f"筋/筒壁与顶板 45°×{GUSSET:g} 过渡", size=TXT_I, anchor="middle")
_cpoly = Polygon([dc(CXL, Z_CEIL), dc(R_CAV - GUSSET, Z_CEIL), dc(R_CAV, Z_CEIL - GUSSET), dc(R_CAV, CZB),
                  dc(R_BASE, CZB), dc(R_BASE, BASE_H), dc(CXL, BASE_H)])
hatch(_cpoly, step=1.8)
polyline([dc(CXL, BASE_H), dc(R_BASE, BASE_H), dc(R_BASE, CZB)], GEOM_W)            # 台阶面 + 外壁
polyline([dc(CXL, Z_CEIL), dc(R_CAV - GUSSET, Z_CEIL), dc(R_CAV, Z_CEIL - GUSSET),
          dc(R_CAV, CZB)], GEOM_W)                                                   # 腔顶 → 45° 过渡 → 内壁
wavy(dc(CXL, BASE_H), dc(CXL, Z_CEIL))
wavy(dc(R_CAV, CZB), dc(R_BASE, CZB))
# 过渡直角边: 竖直 5, 两条界线都穿过空腔 (45° 由标题给出, 水平边界线会与之交叉故不标)
vdim(dc(0, Z_CEIL)[1], dc(0, Z_CEIL - GUSSET)[1], (dc(R_CAV - GUSSET, 0)[0], dc(R_CAV, 0)[0]),
     dc(CXL, 0)[0] + 0.5, f"{GUSSET:g}")

# ===== 详图 A (20:1): 牙型轴向剖面 =====
AS = 20.0
AX0, AY0 = 285.0, 110.0            # 纸面上 t=R_MAJ 的 x / 局部 z=0 (牙顶中心) 的 y
def da(t, z): return (AX0 + (t - R_MAJ) * AS, AY0 - z * AS)
Z_LO, Z_HI = -4.0, 2.3
T_L = R_MIN - 1.2

text(AX0 - 8, 50, "详图 A  (20:1)", size=TXT_L, anchor="middle")
text(AX0 - 8, 56.5, f"螺纹牙型 (轴向剖面)  {FLANK_ANGLE:g}° 对称梯形", size=TXT_I, anchor="middle")

_knots = {Z_LO, Z_HI}
for k in range(-3, 3):
    c = k * PITCH
    for dz in (-HB0, -HC, HC, HB0):
        if Z_LO < c + dz < Z_HI: _knots.add(c + dz)
_prof = [da(prof_r(z), z) for z in sorted(_knots)]
hatch(Polygon([da(T_L, Z_LO)] + _prof + [da(T_L, Z_HI)]))
polyline(_prof, GEOM_W)
wavy(da(T_L, Z_LO), da(T_L, Z_HI))
wavy(da(T_L, Z_LO), da(prof_r(Z_LO), Z_LO))
wavy(da(T_L, Z_HI), da(prof_r(Z_HI), Z_HI))

# 牙顶平台 / 牙底平台 / 螺距
_aO1 = AX0 + 30
_aO2 = AX0 + 46
vdim(da(0, HC)[1], da(0, -HC)[1], AX0, _aO1, f"{CREST:.2f}")
vdim(da(0, PITCH/2 + ROOT/2)[1], da(0, PITCH/2 - ROOT/2)[1], da(R_MIN, 0)[0], _aO1, f"{ROOT:.2f}")
vdim(da(0, HC)[1], da(0, -PITCH + HC)[1], AX0, _aO2, f"{PITCH:g}")

# 牙高: 画在中间牙槽里, 左箭头直接顶牙底平台, 右端从上方牙顶角点引界线
_yd = da(0, -PITCH / 2)[1]
line(AX0, da(0, -HC)[1] + EXT_GP, AX0, _yd + EXT_OV, EXT_W)
line(da(R_MIN, 0)[0], _yd, AX0, _yd, DIM_W)
arrow(da(R_MIN, 0)[0], _yd, -1, 0); arrow(AX0, _yd, 1, 0)
text((da(R_MIN, 0)[0] + AX0) / 2, _yd - 1.8, _with_unit(f"{DEPTH:g}"), anchor="middle")

# 牙型角: 下方那颗牙的两侧牙面延长交于顶点, 在顶点右侧标对顶角
_apx, _apy = da(R_MAJ + HC * DEPTH / FLANK_RUN, -PITCH)
_R_ARC, _EXT = 11.0, 14.0
for sgn in (1, -1):
    cx, cy = da(R_MAJ, -PITCH + sgn * HC)
    ux, uy = _apx - cx, _apy - cy
    L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    line(cx + ux * 0.8, cy + uy * 0.8, _apx + ux * _EXT, _apy + uy * _EXT, EXT_W)
_half = FLANK_ANGLE / 2
_arc = [(_apx + _R_ARC * math.cos(math.radians(a)), _apy - _R_ARC * math.sin(math.radians(a)))
        for a in np.linspace(-_half, _half, 25)]
polyline(_arc, DIM_W)
for a in (_half, -_half):          # 弧长只有 ~11.5, 用小箭头, 否则两头箭头把弧线整段盖住
    ar = math.radians(a)
    s = 1 if a > 0 else -1
    arrow(_apx + _R_ARC * math.cos(ar), _apy - _R_ARC * math.sin(ar),
          -s * math.sin(ar), -s * math.cos(ar), al=2.6, aw=0.9)
text(_apx + _R_ARC + 3.0, _apy + 2.0, f"{FLANK_ANGLE:g}°")

# ===== 说明 =====
NX, NY = 218, 206
text(NX, NY, "说明 / Notes", size=TXT_L)
_notes = [
    f"1) 设计载荷: 单件静载 50 kg = 该脚最不利着地 (含三点着地) 载荷; 四脚刚性家具未找平时总重 ≤100 kg, 垫片找平后 ≤170 kg。",
    f"2) 下柱: 筒壁 {WALL:g} / 米字筋 {RIB_T:g} / 顶板 {PLATE_T:g} (腔深 {Z_CEIL:g}) / 45° 过渡 {GUSSET:g} (详图 C) / 底边 C{BOT_CH:g}; "
    + ("螺纹柱实心。" if BORE_D == 0 else f"螺纹柱中空壁厚 {STUD_WALL:g} (内孔 Φ{BORE_D:g} 深 {BORE_DEPTH:g})。"),
    ("3) ※ 中空螺纹柱复核: 50 kg 冲击工况最低安全系数 1.19 (<1.5, 实心为 1.40), 未达设计目标; 按用户决定保留中空, 承重前须做实物试验。"
     if BORE_D > 0 else "3) 最弱处是螺纹柱根部 Z=70 层面 (冷界面): 必须拧到被支撑物压实台阶面 (接触 ≥Φ48), 不可半旋出当调平脚。"),
    f"4) 螺纹凸起 Φ{2*R_MAJ:g} / 凹陷 Φ{2*R_MIN:g} × P{PITCH:g}" + (" 直接建模 (间隙 0)" if THR_CLEAR == 0 else f" (已缩 {THR_CLEAR:g} 间隙)")
    + "; 已由试打件确认可拧上 (配塑料/打印内螺纹, 2026-09-15)。",
    "5) 验收: 指尖 ≤0.3 N·m 拧到台阶贴合、台阶外圈 4 方位 0.05 塞尺塞不进, 禁止工具强拧; 内螺纹小径须 ≤25.5; 画对齐标记。",
    "6) 只用 PETG 100% 实心: Arachne / 墙 ≥8 圈 / 象脚补偿 0 / 每盘 1 件; 螺纹段层高 0.12; Z69–71 关熨烫、低风扇、升温 5 到 10°C。",
    "7) 地面 ≥3 mm 毡垫或邵 A≤40 ≥6 mm 软橡胶; 整体平放贴地再松手, 禁单边先着地; 抬起挪动不拖拽, 禁以脚为轴原地转动。",
    "8) 防转: 可拆硅酮沿螺纹中段 ≤1/4 圈 (禁整圈、禁厌氧胶), 退转 >30° 重新拧到底; 软底面家具台阶处加 ≥Φ48 硬垫圈; 长期 ≤35°C。",
    f"9) 螺纹 {FLANK_ANGLE:g}° 对称梯形 (牙高 {DEPTH:g}, 平台 {CREST:.2f}), {HAND}旋, 顶端 C{CHAMFER:g}; "
    f"主视图沿 0° 筋全剖, 肋纵剖不画剖面线。 体积 {VOL/1000:.1f} cm³。",
]
NOTE_SZ = 5.0
for i, s in enumerate(_notes):
    assert NX + str_w(s, NOTE_SZ) <= PAGE_W - 10, f"说明第 {i+1} 行超出页面: {str_w(s, NOTE_SZ):.1f}"
    text(NX, NY + 7 + i * 5.6, s, size=NOTE_SZ)

# ===== Title block =====
tb_y = PAGE_H - 32
tb_x, tb_w, tb_h = 20, PAGE_W - 40, 18
_w(0.3)
pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y + tb_h/2, tb_x + tb_w, tb_y + tb_h/2)
text(tb_x + 4, tb_y + 6, "结构件 — 螺纹柱 (Threaded Post)", size=TXT_L)
text(tb_x + tb_w - 4, tb_y + 6,
     "投影 1st-angle  /  比例 2:1 (主视), 1:1 (B-B), 20:1 (详图 A), 2.5:1 (详图 C)", size=TXT_I, anchor="end")
text(tb_x + 4, tb_y + 14.5,
     f"Φ{BASE_D:g}/Φ{2*R_CAV:g}×{BASE_H:g} + 外螺纹 Φ{2*R_MAJ:g}/Φ{2*R_MIN:g}×P{PITCH:g}×{THR_H:g} {HAND}旋 "
     f"内孔 Φ{BORE_D:g}×{BORE_DEPTH:g} / 壁 {WALL:g} / 筋 {RIB_T:g} / 顶板 {PLATE_T:g} / 底边 C{BOT_CH:g} / "
     f"PETG 100% 实心 / 单件 50 kg  /  单位 mm",
     size=TXT_I)
text(tb_x + tb_w - 4, tb_y + 14.5,
     "2026-09-15  /  pov3d / models / threaded_post_d50x70 / threaded_post_d50x70.stl",
     size=TXT_I, anchor="end")

out = Path(__file__).with_name("threaded_post_d50x70_drawing.pdf")
try:
    pdf.output(str(out))
except PermissionError:                     # PDF 在阅读器里开着
    out = out.with_suffix(".NEW.pdf")
    pdf.output(str(out))
print(f"wrote {out}")
print(f"  VOL (积分) = {VOL:.2f} mm^3,  腔顶格内切圆半径 {R_INSC:.3f} (< 45° 过渡 {GUSSET:g})")
