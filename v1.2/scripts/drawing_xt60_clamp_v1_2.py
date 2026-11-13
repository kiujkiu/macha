"""
XT60 压块 + 底垫 V1.2 (V1.2-g; 11-13 晚 M3 孔外移 2.8 对上已打印底盘 x100 孔) A3 工程图, 2 页 PDF (2026-11-12; 11-13 V1.2-f 外端 R110 圆弧, 接头口面 r109.7 内接 R110)
    cd v1.2/scripts && ../../.venv/bin/python drawing_xt60_clamp_v1_2.py
输出 v1.2/models/xt60_clamp_v1_2/xt60_clamp_v1_2_drawing.pdf (+ _preview.png 第 1 页, _p2_preview.png 第 2 页)

版式参照 models/xt60_clamp_16p6x9p2x23p9/build_drawing.py (用户认可的 v4.10 图: 主视/剖视/俯视 + 详图 A U 口 + 件 2),
但**数值和几何全部来自 xt60_clamp_v1_2.py**: 执行它到「导出 STL / STEP」之前 (全部 assert 照跑, 不写文件), 拿到参数和
manifold 实体 part / shim (与导出的 STL/STEP 同一个 mesh):
  · 主视 / 俯视: drawing_v1_0.Part 消隐投影 (特征棱 + 轮廓, z-buffer 判可见; 实线 = 可见, 细虚线 = 不可见)
  · 剖视 / 详图: manifold.slice 精确平面截面 (与模型逐位一致), 压块 / 底垫 剖面线方向相反
第 1 页 压块: 主视 (端视, 从开口端) / 俯视 (R110 外弧 + 剖切位置) / 剖视 B-B (X=0) / 剖视 D-D (过孔心, 叠 M3 + 法兰螺母 + 底盘)
             / 详图 K (防呆, 剖 C-C 局部 5:1, 上角属压块 / 下角属底垫) / 详图 A (U 出线口, 过堵头剖 5:1) / 技术要求 (含打印方向)
第 2 页 底垫: 俯视 / 主视 / 剖视 E-E (X=0) / 详图 K2 (下角防呆 8:1) / 技术要求
打印方向: 脚本对 mesh 做悬空面统计 (法向朝下超过 45° 的面积, 不计贴床面), 结果写进技术要求。
"""
import contextlib
import io
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "v1.0" / "models"))
from drawing_v1_0 import Page, Part, PAGE_W, PAGE_H, MM_PT  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch, Circle as MCircle  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
import manifold3d as m3d  # noqa: E402

plt.rcParams["hatch.linewidth"] = 0.35

# ---------------- 几何: 执行生成器 (不导出) ----------------
_src = (HERE / "xt60_clamp_v1_2.py").read_text(encoding="utf-8")
_MARK = "# ===== 导出 STL / STEP ====="
assert _MARK in _src, "生成器结构变了, 找不到导出段标记"
G = {"__file__": str(HERE / "xt60_clamp_v1_2.py"), "__name__": "xt60_clamp_v1_2_geo"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(_src.split(_MARK)[0], str(HERE / "xt60_clamp_v1_2.py"), "exec"), G)
g = type("P", (), G)                       # g.CH_W_B ... 点号取参数
PART, SHIM = G["part"], G["shim"]          # 装配坐标: 压块 z 0..11, 底垫 z −2..2
OUT_DIR = HERE.parents[0] / "models" / "xt60_clamp_v1_2"
OUT = OUT_DIR / "xt60_clamp_v1_2_drawing.pdf"


def F(v, n=2):
    s = f"{v:.{n}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def mm(s):
    s = str(s)
    if not s or "mm" in s or "°" in s:
        return s
    return s.replace(" (", " mm (", 1) if " (" in s else s + " mm"


# 派生量 (全部从生成器)
Y_FC = g.Y_OPEN                                       # V1.2-f: 中段 (|x| < X_ARC0) R110 落在开口面外, 外端 = 开口面
Y_FE = g.FRONT_Y_E                                    # X 端 (x=19) 外端 (R110 剪进)
LEN_C, LEN_E = g.Y_END - Y_FC, g.Y_END - Y_FE        # 26.9 / 25.55
BODY_IN_C = g.Y_STEP - Y_FC                           # 本体段槽长 (= BODY_L)
RIM_C = g.RIM_W + g.ASSY_CLR                          # 压块止口台阶宽 2.1
KEY_X_SHIM = g.CH_W_B / 2 - g.ASSY_CLR                # 底垫下角防呆外侧 7.7
NUT_TOP_L = g.HTOP + g.NUT_T                          # 螺母顶 (压块局部 z)
TIP_L = g.TIP_G - g.Z_GLOBAL                          # 螺丝尖 (局部 z)
HEAD_L = -g.DISC_T + g.DISC_CB_H - g.WASHER_T - g.Z_GLOBAL   # 头支承面 (局部 z) = −5.8 (V1.2-g: Φ13×3 沉孔顶下垫片 0.8)
DISC_L0 = -g.DISC_T - g.Z_GLOBAL                      # 底盘底 (局部) = −8


# ---------------- 打印悬空检查 ----------------
def overhang(m, flip):
    me = m.to_mesh()
    v = np.asarray(me.vert_properties)[:, :3]
    T = v[np.asarray(me.tri_verts)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    A = np.linalg.norm(n, axis=1) / 2
    n = n / (2 * A[:, None] + 1e-30)
    s = -1.0 if flip else 1.0
    nz, zc = n[:, 2] * s, T[:, :, 2].mean(1) * s
    sel = (nz < -math.cos(math.radians(45))) & (zc > zc.min() + 1e-3)
    return float(A[sel].sum())


OH_CLAMP_TOPDOWN = overhang(PART, True)       # 顶面贴床
OH_CLAMP_TOPUP = overhang(PART, False)        # 底面贴床
OH_SHIM = overhang(SHIM, False)               # 底垫底面贴床
assert OH_CLAMP_TOPDOWN < 0.5 and OH_SHIM < 0.5, (OH_CLAMP_TOPDOWN, OH_SHIM)


# ---------------- 页面工具 ----------------
ARR = 2.6


def hd(pg, x0, x1, yg0, yg1, yd, label, size=2.5, tx=None):
    """水平尺寸: 两条界线分别从 (x0,yg0) (x1,yg1) 拉到 yd; 窄尺寸外箭头。tx: 文字中心 x 覆盖。"""
    if x0 > x1:
        x0, x1, yg0, yg1 = x1, x0, yg1, yg0
    for x, yg in ((x0, yg0), (x1, yg1)):
        sg = 1 if yd > yg else -1
        pg.line(x, yg + sg * 0.8, x, yd + sg * 1.4, lw=0.15)
    if x1 - x0 >= 2 * ARR + 0.6:
        pg.line(x0, yd, x1, yd, lw=0.15)
        pg.arrow(x0, yd, -1, 0, L=ARR, Wd=0.75)
        pg.arrow(x1, yd, 1, 0, L=ARR, Wd=0.75)
    else:
        pg.line(x0 - ARR - 2.5, yd, x1 + ARR + 2.5, yd, lw=0.15)
        pg.arrow(x0, yd, 1, 0, L=ARR, Wd=0.75)
        pg.arrow(x1, yd, -1, 0, L=ARR, Wd=0.75)
    pg.text((x0 + x1) / 2 if tx is None else tx, yd + 0.7, mm(label), size=size, ha="center", va="bottom", halo=True)


def vd(pg, y0, y1, xg0, xg1, xd, label, size=2.5, side=None, ty=None):
    """竖直尺寸; 文字竖排在尺寸线左侧 (side='l') 或右侧 ('r'); 窄尺寸外箭头, 文字放到上方延长线外 (ty 可覆盖)。"""
    if y0 > y1:
        y0, y1, xg0, xg1 = y1, y0, xg1, xg0
    for y, xg in ((y0, xg0), (y1, xg1)):
        sg = 1 if xd > xg else -1
        pg.line(xg + sg * 0.8, y, xd + sg * 1.4, y, lw=0.15)
    side = side or ("r" if xd > max(xg0, xg1) else "l")
    narrow = y1 - y0 < 2 * ARR + 0.6
    if not narrow:
        pg.line(xd, y0, xd, y1, lw=0.15)
        pg.arrow(xd, y0, 0, -1, L=ARR, Wd=0.75)
        pg.arrow(xd, y1, 0, 1, L=ARR, Wd=0.75)
    else:
        pg.line(xd, y0 - ARR - 2.5, xd, y1 + ARR + 2.5, lw=0.15)
        pg.arrow(xd, y0, 0, 1, L=ARR, Wd=0.75)
        pg.arrow(xd, y1, 0, -1, L=ARR, Wd=0.75)
    lab = mm(label)
    tlen = len(lab) * size * 0.62
    if not narrow and tlen < (y1 - y0) - 1 and ty is None:
        pg.text(xd + (0.8 if side == "r" else -0.8), (y0 + y1) / 2, lab, size=size,
                ha="left" if side == "r" else "right", va="center", rot=90, halo=True)
    else:                                              # 横排在尺寸线旁
        yy = (y0 + y1) / 2 if ty is None else ty
        pg.text(xd + (1.0 if side == "r" else -1.0), yy, lab, size=size,
                ha="left" if side == "r" else "right", va="center", halo=True)


def leader(pg, p, t, s, size=2.5, ha="left", dot=True):
    if dot:
        pg.ax.add_patch(MCircle(p, 0.35, color="k", zorder=6, lw=0))
    pg.line(p[0], p[1], t[0], t[1], lw=0.15)
    sh = 2.5 if ha == "left" else -2.5
    pg.line(t[0], t[1], t[0] + sh, t[1], lw=0.15)
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        pg.text(t[0] + sh + (0.6 if ha == "left" else -0.6), t[1] - i * size * 1.25, ln, size=size,
                ha=ha, va="center", halo=True)


def segs(pg, S, T, lw=0.35, ls="-", color="k", z=3):
    from matplotlib.collections import LineCollection
    if not S:
        return
    L = [[T(*a), T(*b)] for a, b in S]
    pg.ax.add_collection(LineCollection(L, linewidths=lw * MM_PT, colors=color, linestyles=ls, zorder=z,
                                        capstyle="butt"))


def poly(pg, pts, T, lw=0.35, ls="-", color="k", closed=False, z=3):
    P = [T(*p) for p in pts]
    if closed:
        P.append(P[0])
    xs, ys = zip(*P)
    pg.ax.plot(xs, ys, lw=lw * MM_PT, ls=ls, color=color, zorder=z, solid_capstyle="butt")


def chain(pg, a, b):
    pg.ax.plot([a[0], b[0]], [a[1], b[1]], lw=0.15 * MM_PT, color="0.3", ls=(0, (9, 2, 1.5, 2)), zorder=2)


def sec_patch(pg, polys, T, hatch="////", lw=0.4):
    V, C = [], []
    for q in polys:
        q = [T(*p) for p in np.asarray(q)]
        V += q + [q[0]]
        C += [MPath.MOVETO] + [MPath.LINETO] * (len(q) - 1) + [MPath.CLOSEPOLY]
    if not V:
        return
    pg.ax.add_patch(PathPatch(MPath(np.array(V), C), facecolor="none", edgecolor="k", lw=lw * MM_PT,
                              hatch=hatch, zorder=3))


def sec_y(m, y0):
    """平面 Y=y0 截面 → (x, z) 多边形 (从 −Y 看, X 向右)。"""
    return m.translate((0, -y0, 0)).rotate((-90, 0, 0)).slice(0.0)


def sec_x(m, x0):
    """平面 X=x0 截面 → (y, z) 多边形。"""
    cs = m.translate((-x0, 0, 0)).rotate((0, 90, 0)).slice(0.0)     # 坐标 (z, y)
    return [np.asarray(q)[:, ::-1] for q in cs.to_polygons()]


def clip_cs(cs, u0, u1, w0, w1):
    return (cs ^ m3d.CrossSection.square((u1 - u0, w1 - w0)).translate((u0, w0))).to_polygons()


def view_title(pg, x, y, s, sub=None):
    pg.text(x, y, s, size=3.6, ha="center", weight="bold")
    if sub:
        pg.text(x, y - 4.2, sub, size=2.4, ha="center")


def sec_mark(pg, p0, p1, letter, look):
    """剖切符号: 粗短划 + 字母 + 看向箭头 (look = 页面方向单位向量)。"""
    d = np.subtract(p1, p0)
    d = d / np.linalg.norm(d)
    for p, sg in ((p0, 1), (p1, -1)):
        pg.line(p[0], p[1], p[0] + sg * d[0] * 4, p[1] + sg * d[1] * 4, lw=0.6)
        a0 = (p[0] - sg * d[0] * 0.0, p[1] - sg * d[1] * 0.0)
        pg.line(a0[0], a0[1], a0[0] + look[0] * 4.5, a0[1] + look[1] * 4.5, lw=0.2)
        pg.arrow(a0[0] + look[0] * 4.5, a0[1] + look[1] * 4.5, look[0], look[1], L=2.0, Wd=0.6)
        pg.text(p[0] - sg * d[0] * 2.5 + look[0] * 2.5, p[1] - sg * d[1] * 2.5 + look[1] * 2.5, letter, size=3.2,
                ha="center", va="center")
    chain(pg, p0, p1)


def frame(pg, title, sub, page_no):
    pg.rect(5, 5, PAGE_W - 5, PAGE_H - 5, lw=0.5)
    pg.text(PAGE_W / 2, PAGE_H - 13, title, size=5.0, ha="center")
    pg.text(PAGE_W / 2, PAGE_H - 19, sub, size=2.6, ha="center")
    tb = (10, 10, PAGE_W - 10, 34)
    pg.rect(*tb, lw=0.35)
    pg.line(tb[0], 22, tb[2], 22, lw=0.2)
    for xx in (130, 200, 256, 300):
        pg.line(xx, tb[1], xx, tb[3], lw=0.2)
    return tb


def title_block(pg, code, short, qty, scale, orient, page_no, src):
    pg.text(14, 26, code, size=4.4, weight="bold")
    pg.text(14, 14, short, size=2.6)
    pg.text(134, 26, f"数量: {qty}", size=2.9)
    pg.text(134, 14, "材料: PLA / PETG", size=2.9)
    pg.text(204, 26, scale, size=2.6)
    pg.text(204, 14, "单位 mm / 第一角", size=2.9)
    pg.text(260, 26, f"{g.VERSION}  2026-11-12", size=2.6)
    pg.text(260, 14, f"POV3D V1.2  第 {page_no}/2 页", size=2.6)
    pg.text(304, 26, "打印姿态:", size=2.9)
    pg.text(304, 14, orient, size=2.5)
    pg.text(14, 6.5, src, size=2.2)


def notes(pg, x, y, head, items, size=2.35, dy=3.25, width=None):
    pg.text(x, y, head, size=3.0, weight="bold")
    y -= 4.4
    for s in items:
        for k, ln in enumerate(s.split("\n")):
            pg.text(x + (0 if k == 0 else 3.0), y, ln, size=size)
            y -= dy
    return y


# ---------------- 预计算投影 ----------------
def tris_of(m):
    me = m.to_mesh()
    v = np.asarray(me.vert_properties)[:, :3]
    return v[np.asarray(me.tri_verts)]


P_PART, P_SHIM = Part(tris_of(PART)), Part(tris_of(SHIM))
S = 2.5      # 主比例
D = 5.0      # 详图

# =====================================================================================
# 第 1 页: 压块
# =====================================================================================
pg = Page()
frame(pg, f"POV3D V1.2 — xt60_clamp_v1_2   XT60 电源接头压块 ({g.VERSION})",
      f"锁 XT60H-M: 插合本体 {F(g.BODY_W)}×{F(g.BODY_H)}×{F(g.BODY_L)} (开口端) + 护套 {F(g.SHEATH_W)}×{F(g.SHEATH_H)}×{F(g.SHEATH_L)} (堵头端)  ·  "
      f"外形 {F(g.L)} × {F(LEN_C)} × {F(g.HTOP)}, 外端 R{F(g.TRIM_R)} (接头口面 r{F(g.XT_RF)} 内接)  ·  2×M3 从下往上, 法兰螺母平坐顶面  ·  防呆 R{F(g.KEY_R)} (上角压块 / 下角底垫)", 1)

# ---- 主视图 (端视, 从 −Y 开口端看) ----
FX, FZ = 75.0, 226.0
TF = lambda x, z: (FX + x * S, FZ + z * S)  # noqa: E731
view_title(pg, FX, 268, "主视图 (端视) 2.5:1", "沿 +Y 看 (从开口端); 灰 = 底垫 (件 2); 顶面平, 无螺母座")
vis, hid = P_SHIM.view_lines("front")
segs(pg, vis, TF, lw=0.25, color="0.55")
vis, hid = P_PART.view_lines("front")
segs(pg, hid, TF, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
segs(pg, vis, TF, lw=0.4)
chain(pg, TF(0, -3), TF(0, g.HTOP + 2))
for sx in (-1, 1):
    chain(pg, TF(sx * g.HX, -3), TF(sx * g.HX, g.HTOP + 2))
# 详图 K 圈
kc = TF(g.CH_W_B / 2 - 0.6, (g.BODY_LIFT + g.CH_H_B) / 2)
pg.ax.add_patch(MCircle(kc, 13.0, fill=False, lw=0.25 * MM_PT, zorder=4))
pg.text(kc[0] + 10.5, kc[1] + 10.5, "K", size=3.4)
vd(pg, TF(0, 0)[1], TF(0, g.HTOP)[1], TF(-g.HALF_L, 0)[0], TF(-g.HALF_L, 0)[0], TF(-g.HALF_L, 0)[0] - 8, F(g.HTOP), side="l")
hd(pg, TF(-g.CH_W_B / 2, 0)[0], TF(g.CH_W_B / 2, 0)[0], TF(0, 0)[1], TF(0, 0)[1], TF(0, -2)[1] - 7, f"{F(g.CH_W_B)} (本体段槽)")
hd(pg, TF(-g.HALF_L, 0)[0], TF(g.HALF_L, 0)[0], TF(0, -2)[1], TF(0, -2)[1], TF(0, -2)[1] - 15, F(g.L))
vd(pg, TF(0, 0)[1], TF(0, g.CH_H_B)[1], TF(g.CH_W_B / 2, 0)[0], TF(g.CH_W_B / 2, 0)[0], TF(g.HALF_L, 0)[0] + 7, F(g.CH_H_B), side="r")
pg.text(FX, TF(0, -2)[1] - 21, f"从开口端看得到: 本体段槽口 + 两条防呆 (+X 侧), 堵头内面两个 U 口; 虚线 = 护套段槽 {F(g.CH_W_S)}×{F(g.CH_H_S)}、M3 孔",
        size=2.2, ha="center")

# ---- 俯视图 ----
TX, TY = 75.0, 134.0
TT = lambda x, y: (TX + x * S, TY + y * S)  # noqa: E731
view_title(pg, TX, 186, "俯视图 2.5:1", f"沿 −Z 看; 下方 = 开口端 (R{F(g.TRIM_R)} 外弧, 全局朝外)")
vis, hid = P_PART.view_lines("top")
segs(pg, hid, TT, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
segs(pg, vis, TT, lw=0.4)
chain(pg, TT(-g.HALF_L - 3, g.HOLE_Y), TT(g.HALF_L + 3, g.HOLE_Y))
for sx in (-1, 1):
    chain(pg, TT(sx * g.HX, g.HOLE_Y - 5), TT(sx * g.HX, g.HOLE_Y + 5))
# R110 引出 + 圆弧延长 (细点划)
th = np.linspace(-0.22, 0.22, 80)
arc = [TT(g.TRIM_R * math.sin(t), g.RC - g.TRIM_R * math.cos(t)) for t in th]
pg.ax.plot(*zip(*arc), lw=0.15 * MM_PT, color="0.4", ls=(0, (9, 2, 1.5, 2)), zorder=2)
pa = (-14.0, g.RC - math.sqrt(g.TRIM_R ** 2 - 196.0))
leader(pg, TT(*pa), (TT(-g.HALF_L, 0)[0] - 3, TT(0, -11.0)[1]),
       f"R{F(g.TRIM_R)}\n(= 底盘外圆)", ha="right", dot=True)
# 剖切符号
sec_mark(pg, TT(0, Y_FC - 1.0), TT(0, g.Y_END + 1.5), "B", (-1, 0))
sec_mark(pg, TT(-g.HALF_L - 2, -5.0), TT(g.HALF_L + 2, -5.0), "C", (0, 1))
sec_mark(pg, TT(-g.HALF_L - 2, g.HOLE_Y), TT(g.HALF_L + 2, g.HOLE_Y), "D", (0, 1))
# 尺寸
xr = TT(g.HALF_L, 0)[0]
vd(pg, TT(0, Y_FE)[1], TT(0, g.Y_END)[1], xr, xr, xr + 11, f"{F(LEN_E)} (X 端)", side="r")
vd(pg, TT(0, Y_FC)[1], TT(0, g.Y_END)[1], TT(0, 0)[0], xr, xr + 19, f"{F(LEN_C)} (中线)", side="r")
xl = TT(-g.HALF_L, 0)[0]
vd(pg, TT(0, g.HOLE_Y)[1], TT(0, g.Y_END)[1], TT(-g.HX, 0)[0], xl, xl - 9, F(g.Y_END - g.HOLE_Y), side="l")
yb = TT(0, Y_FE)[1]
hd(pg, TT(-g.HX, 0)[0], TT(g.HX, 0)[0], TT(0, g.HOLE_Y)[1], TT(0, g.HOLE_Y)[1], TT(0, Y_FC)[1] - 7, f"{F(g.PITCH)} (2×Φ{F(g.HOLE_D)} 通孔)")
hd(pg, xl, xr, yb, yb, TT(0, Y_FC)[1] - 12.5, F(g.L))      # 开口面 Y −11.95 比 V1.2-c 低, 尺寸收紧免压技术要求
leader(pg, TT(g.CH_W_B / 2 - 0.5, -6.5), (TT(g.HX, 0)[0] - 3, TT(0, Y_FC)[1] - 3),
       f"防呆 Y 长 {F(g.KEY_LEN)}", ha="left")

# ---- 剖视 B-B (X = 0) ----
BX, BZ = 228.0, 226.0
BYM = (Y_FC + g.Y_END) / 2
TB = lambda y, z: (BX - (y - BYM) * S, BZ + z * S)  # noqa: E731
view_title(pg, BX, 268, "B-B 剖视 2.5:1", "过对称面 X=0, 沿 +X 看 (开口端在右); 灰点划 = 接头 + 底垫轮廓")
sec_patch(pg, sec_x(PART, 0.0), TB, hatch="////")
sec_patch(pg, sec_x(SHIM, 0.0), TB, hatch="\\\\\\\\", lw=0.3)
xtp = [(g.Y_OPEN, g.BODY_LIFT), (g.Y_OPEN, g.BODY_LIFT + g.BODY_H), (g.Y_XSTEP, g.BODY_LIFT + g.BODY_H), (g.Y_XSTEP, g.SHEATH_H),
       (g.Y_CAPI, g.SHEATH_H), (g.Y_CAPI, 0), (g.Y_XSTEP, 0), (g.Y_XSTEP, g.BODY_LIFT)]
poly(pg, xtp, TB, lw=0.22, ls=(0, (6, 1.5, 1.5, 1.5)), color="0.45", closed=True, z=4)
chain(pg, TB(g.HOLE_Y, -3), TB(g.HOLE_Y, g.HTOP + 2.5))
pg.text(TB(g.HOLE_Y, 0)[0] + 1, TB(0, g.HTOP + 2.5)[1], "孔轴 (在剖面后)", size=2.1)
yb0 = TB(0, -g.BASE_T)[1]
hd(pg, TB(g.Y_END, 0)[0], TB(g.Y_CAPI, 0)[0], yb0, yb0, yb0 - 6, F(g.CAP_T))
hd(pg, TB(g.Y_CAPI, 0)[0], TB(g.Y_STEP, 0)[0], yb0, yb0, yb0 - 6, F(g.Y_CAPI - g.Y_STEP))
hd(pg, TB(g.Y_STEP, 0)[0], TB(Y_FC, 0)[0], TB(0, g.CH_H_B)[1], yb0, yb0 - 6, F(BODY_IN_C))
hd(pg, TB(g.Y_CAPI, 0)[0], TB(g.Y_OPEN, 0)[0], yb0, yb0, yb0 - 14, f"槽深 {F(g.XT_L)} (接头全长, 口面与外端平齐)")
hd(pg, TB(g.Y_END, 0)[0], TB(Y_FC, 0)[0], yb0, yb0, yb0 - 22, f"{F(LEN_C)} (中线)")
xL = TB(g.Y_END, 0)[0]
vd(pg, TB(0, 0)[1], TB(0, g.HTOP)[1], xL, xL, xL - 7, F(g.HTOP), side="l")
vd(pg, TB(0, 0)[1], TB(0, g.RIM_H)[1], xL, xL, xL - 15, f"{F(g.RIM_H)}", side="l")
xR = TB(Y_FC, 0)[0]
vd(pg, TB(0, 0)[1], TB(0, g.CH_H_B)[1], xR, xR, xR + 7, F(g.CH_H_B), side="r")
vd(pg, TB(0, 0)[1], TB(0, g.CH_H_S)[1], TB(g.Y_STEP, 0)[0], xR, xR + 15, F(g.CH_H_S), side="r")
leader(pg, TB(g.Y_END - 1.5, g.RIM_H * 0.5), (xL - 4, TB(0, -g.BASE_T)[1] - 2.0),
       f"后边止口: 压块台阶 {F(g.BACK_RIM_W + g.ASSY_CLR)} 宽 × {F(g.RIM_H)} 高\n底垫后边框 {F(g.BACK_RIM_W)}×{F(g.RIM_H)} (0.1 装配隙)", ha="right", size=2.2)
leader(pg, TB(Y_FC + 1.0, g.HTOP - 0.8), (xR + 2, TB(0, g.HTOP)[1] + 7),
       f"接头口面 r{F(g.XT_RF)} 内接 R{F(g.TRIM_R)}, 不伸出 (中线缩进 {F(g.RECESS_C)})", ha="left", size=2.2)

# ---- 剖视 D-D (Y = 孔心) + M3 / 法兰螺母 / 底盘 ----
DX, DZ = 225.0, 131.0
TD = lambda x, z: (DX + x * S, DZ + z * S)  # noqa: E731
view_title(pg, DX, 186, "D-D 剖视 2.5:1", f"过孔心 Y={F(g.HOLE_Y)} (本体段), 沿 +Y 看; 灰 = M3×{F(g.SCREW_L)} + 垫片 + 法兰螺母 + 底盘 (示意)")
sec_patch(pg, sec_y(PART, g.HOLE_Y).to_polygons(), TD, hatch="////")
sec_patch(pg, sec_y(SHIM, g.HOLE_Y).to_polygons(), TD, hatch="\\\\\\\\", lw=0.3)
GR = dict(lw=0.25, color="0.45")
poly(pg, [(-g.HALF_L - 3, DISC_L0), (g.HALF_L + 3, DISC_L0), (g.HALF_L + 3, -g.BASE_T), (-g.HALF_L - 3, -g.BASE_T)], TD, closed=True, **GR)
for sx in (-1, 1):
    x = sx * g.HX
    r, rh, rn = g.M3_SHANK_D / 2, g.M3_HEAD_D / 2, g.NUT_AF / 2
    poly(pg, [(x - r, HEAD_L), (x - r, TIP_L), (x + r, TIP_L), (x + r, HEAD_L)], TD, ls=(0, (4, 1.2)), **GR)
    poly(pg, [(x - rh, HEAD_L - g.M3_HEAD_H), (x + rh, HEAD_L - g.M3_HEAD_H), (x + rh, HEAD_L), (x - rh, HEAD_L)], TD, closed=True, **GR)
    _cb = 6.5; _cbt = HEAD_L + g.WASHER_T                                 # 底盘 Φ13×3 沉孔顶 (已打印); 垫片 Φ9×0.8 在头和沉孔顶之间
    poly(pg, [(x - _cb, DISC_L0), (x - _cb, _cbt), (x + _cb, _cbt), (x + _cb, DISC_L0)], TD, lw=0.2, color="0.55")
    poly(pg, [(x - 4.5, _cbt), (x + 4.5, _cbt), (x + 4.5, HEAD_L), (x - 4.5, HEAD_L)], TD, closed=True, **GR)
    rf = g.NUT_FL_D / 2
    poly(pg, [(x - rf, g.HTOP), (x - rf, g.HTOP + g.NUT_FL_H), (x - rn, g.HTOP + g.NUT_FL_H), (x - rn, NUT_TOP_L),
              (x + rn, NUT_TOP_L), (x + rn, g.HTOP + g.NUT_FL_H), (x + rf, g.HTOP + g.NUT_FL_H), (x + rf, g.HTOP)], TD, closed=True, **GR)
    chain(pg, TD(x, DISC_L0 - 2), TD(x, NUT_TOP_L + 2))
chain(pg, TD(0, -3), TD(0, g.HTOP + 2))
pg.text(DX, TD(0, DISC_L0)[1] + 1.5, f"底盘 {F(g.DISC_T)} (示意)", size=2.1, ha="center")
# 右侧: 螺母 / 啮合
xr = TD(g.HALF_L, 0)[0]
xn = TD(g.HX + g.NUT_FL_D / 2, 0)[0]
vd(pg, TD(0, g.HTOP)[1], TD(0, TIP_L)[1], xn, TD(g.HX + 1.5, 0)[0], xr + 6, f"啮合 {g.ENGAGE:.1f}", side="r")
vd(pg, TD(0, g.HTOP)[1], TD(0, NUT_TOP_L)[1], xn, xn, xr + 24, f"螺母 {F(g.NUT_T)}", side="r")
leader(pg, TD(g.HX + 1.2, TIP_L), (xr + 2, TD(0, NUT_TOP_L)[1] + 7),
       f"M3 尖 Z{F(g.TIP_G)} (低于螺母顶 {F(g.NUT_Z1_G - g.TIP_G)})", ha="left", size=2.2)
leader(pg, TD(-g.HX - g.NUT_FL_D / 2 + 0.5, g.HTOP + 0.5), (TD(-g.HALF_L, 0)[0] + 2, TD(0, NUT_TOP_L)[1] + 7),
       f"M3 法兰螺母 (法兰 Φ{F(g.NUT_FL_D)}) 平坐顶面, 无螺母座; 全局 Z{F(g.NUT_Z0_G)}..{F(g.NUT_Z1_G)}", ha="left", size=2.2)
xl = TD(-g.HALF_L, 0)[0]
vd(pg, TD(0, DISC_L0)[1], TD(0, -g.BASE_T)[1], xl - 3, xl - 3, xl - 6, f"{F(g.DISC_T)}", side="l")
leader(pg, TD(-g.HALF_L + RIM_C / 2, g.RIM_H / 2), (xl - 3, TD(0, DISC_L0)[1] - 4),
       f"侧止口: 压块台阶 {F(RIM_C)}×{F(g.RIM_H)}\n底垫边框 {F(g.RIM_W)}×{F(g.RIM_H)}", ha="right", size=2.2)
yb = TD(0, DISC_L0)[1]
hd(pg, TD(-g.CH_W_B / 2, 0)[0], TD(g.CH_W_B / 2, 0)[0], TD(0, 0)[1], TD(0, 0)[1], yb - 5, f"{F(g.CH_W_B)} (本体段槽)")
hd(pg, TD(-g.HX, 0)[0], TD(g.HX, 0)[0], yb, yb, yb - 12, F(g.PITCH))
leader(pg, TD(g.HX - g.HOLE_D / 2, 5.5), (TD(g.HX, 0)[0] - 14, TD(0, 5.5)[1] + 0.01),
       f"Φ{F(g.HOLE_D)}", ha="right", dot=False)
pg.text(DX, yb - 18.5, f"本体段槽 {F(g.CH_W_B)}×{F(g.CH_H_B)} 紧配 (间隙 0); 孔壁到槽壁 {F(g.WEB_B)}; 孔壁到 R110 外弧 {F(g.WALL_ARC)}",
        size=2.2, ha="center")

# ---- 详图 K (剖 C-C, Y=−5, +X 侧两角) ----
KX, KZ = 350.0, 200.0
KU0, KU1, KW0, KW1 = 3.4, 10.4, -1.2, 10.2
TK = lambda x, z: (KX + (x - (KU0 + KU1) / 2) * D, KZ + z * D)  # noqa: E731
view_title(pg, KX, 268, "详图 K 5:1 (C-C 剖, Y = −5)", f"防呆凹弧三角, 从开口端看; 灰点划 = 正插接头 (本体 +X 角 R{F(g.KEY_R)})")
sec_patch(pg, clip_cs(sec_y(PART, -5.0), KU0, KU1, 0, KW1), TK, hatch="////")
sec_patch(pg, clip_cs(sec_y(SHIM, -5.0), KU0, KU1, KW0, KW1), TK, hatch="\\\\\\\\", lw=0.3)
xs = G["xt60_v12"]().translate((0, 5.0, 0)).rotate((-90, 0, 0)).slice(0.0)
for q in clip_cs(xs, KU0 - 0.5, KU1, KW0, KW1):
    q = np.asarray(q)
    poly(pg, [tuple(p) for p in q], TK, lw=0.22, ls=(0, (6, 1.5, 1.5, 1.5)), color="0.45", closed=True, z=4)
# 断裂线 (左边窗口)
for zz0, zz1 in ((KW0, KW1),):
    pg.line(TK(KU0, 0)[0], TK(0, zz0)[1], TK(KU0, 0)[0], TK(0, zz1)[1], lw=0.15)
xw = g.CH_W_B / 2
R = g.KEY_R
# 上角: 弧心 (xw−R, CH_H_B−R)
cu = (xw - R, g.CH_H_B - R)
pu = (cu[0] + R * math.cos(math.radians(45)), cu[1] + R * math.sin(math.radians(45)))
leader(pg, TK(*pu), (TK(KU1, 0)[0] + 3, TK(0, g.CH_H_B + 0.6)[1]),
       f"上角 R{F(R)} —— 属压块\n(挂槽顶角, 长 {F(g.KEY_LEN)})", ha="left", size=2.4)
cl = (xw - R, g.BODY_LIFT + R)
pl = (cl[0] + R * math.cos(math.radians(-45)), cl[1] + R * math.sin(math.radians(-45)))
leader(pg, TK(*pl), (TK(KU1, 0)[0] + 3, TK(0, 3.6)[1]),
       f"下角 R{F(R)} —— 属底垫\n(坐凸台顶, 长 {F(g.KEY_LEN)})", ha="left", size=2.4)
pg.text(TK(KU1, 0)[0] + 3, TK(0, 2.0)[1], f"R 按图估, 待卡尺确认", size=2.4, weight="bold")
pg.text(TK(KU1, 0)[0] + 3, TK(0, 2.0)[1] - 3.3, f"(另一侧小角约 R{F(g.KEY_R_SM)})", size=2.2)
for c in (cu, cl):
    a, b = TK(c[0], c[1]), TK(c[0] + 0.0, c[1])
    pg.line(a[0] - 1.2, a[1], a[0] + 1.2, a[1], lw=0.15)
    pg.line(a[0], a[1] - 1.2, a[0], a[1] + 1.2, lw=0.15)
# 间隙 0.1 (下角外侧面 7.7 ↔ 槽壁 7.8)
hd(pg, TK(KEY_X_SHIM, 0)[0], TK(xw, 0)[0], TK(0, 1.2)[1], TK(0, 1.2)[1], TK(0, KW0)[1] - 4.5, F(g.ASSY_CLR), tx=TK(xw, 0)[0] + 7)
# 高度
xk = TK(KU0, 0)[0]
vd(pg, TK(0, 0)[1], TK(0, g.CH_H_B)[1], xk, xk, xk - 6, F(g.CH_H_B), side="l")
vd(pg, TK(0, 0)[1], TK(0, g.BODY_LIFT)[1], xk, xk, xk - 13, f"凸台 {F(g.BODY_LIFT)}", side="l", ty=TK(0, 0)[1] - 5.5)
# 弧心位置
hd(pg, TK(cu[0], 0)[0], TK(xw, 0)[0], TK(*cu)[1], TK(0, g.CH_H_B)[1], TK(0, KW1)[1] + 3, F(R))
pg.text(KX, TK(0, KW0)[1] - 9.5, f"z=0: 压块底面 = 底垫底板顶面; 槽壁 x = {F(g.CH_W_B / 2)}", size=2.1, ha="center")

# ---- 详图 A (U 出线口, 过堵头剖) ----
AX, AZ = 362.0, 128.0
YA = g.Y_CAPI + g.CAP_T / 2
AU0, AU1, AW0, AW1 = -7.0, 7.0, -2.0, 7.6
DA = 4.0
TA = lambda x, z: (AX + x * DA, AZ + z * DA)  # noqa: E731
view_title(pg, AX, 177, "详图 A 4:1 (过堵头剖, Y = " + F(YA) + ")", "U 出线口, 从开口端看; 下方 = 底垫后边框 (平底)")
sec_patch(pg, clip_cs(sec_y(PART, YA), AU0, AU1, AW0, AW1), TA, hatch="////")
sec_patch(pg, clip_cs(sec_y(SHIM, YA), AU0, AU1, AW0, AW1), TA, hatch="\\\\\\\\", lw=0.3)
for xc in g.WIRE_X:
    chain(pg, TA(xc, AW0 - 1), TA(xc, g.WIRE_ZC + g.WIRE_D / 2 + 1.5))
chain(pg, TA(g.WIRE_X[0] - 2.2, g.WIRE_ZC), TA(g.WIRE_X[1] + 2.2, g.WIRE_ZC))
hd(pg, TA(g.WIRE_X[0], 0)[0], TA(g.WIRE_X[1], 0)[0], TA(0, g.WIRE_ZC + 2.6)[1], TA(0, g.WIRE_ZC + 2.6)[1],
   TA(0, AW1)[1] + 4, F(g.WIRE_PITCH))
hd(pg, TA(g.WIRE_X[0] - g.WIRE_D / 2, 0)[0], TA(g.WIRE_X[0] + g.WIRE_D / 2, 0)[0], TA(0, AW0)[1], TA(0, AW0)[1],
   TA(0, AW0)[1] - 5, F(g.WIRE_D))
xa = TA(AU0, 0)[0]
vd(pg, TA(0, 0)[1], TA(0, g.WIRE_ZC)[1], xa, xa, xa - 6, F(g.WIRE_ZC), side="l")
vd(pg, TA(0, 0)[1], TA(0, g.SLOT_BOTTOM)[1], xa, xa, xa - 13, f"{F(g.SLOT_BOTTOM)}", side="l", ty=TA(0, g.SLOT_BOTTOM / 2)[1])
a45 = math.radians(45)
leader(pg, TA(g.WIRE_X[1] + g.WIRE_D / 2 * math.cos(a45), g.WIRE_ZC + g.WIRE_D / 2 * math.sin(a45)),
       (TA(AU1, 0)[0] + 3, TA(0, AW1)[1] + 2), f"R{F(g.WIRE_D / 2)}", ha="left", size=2.4)
pg.text(AX, TA(0, AW0)[1] - 12.5, f"堵头 {F(g.CAP_T)} 厚; U 口 Φ{F(g.WIRE_D)} (= 线径, 零余量) 半圆顶 + 直边, 圆心高 {F(g.WIRE_ZC)} = 针轴线;", size=2.2, ha="center")
pg.text(AX, TA(0, AW0)[1] - 15.8, f"平底 = 底垫后边框顶 z {F(g.SLOT_BOTTOM)} (线底 {F(g.LEDGE)} 高于边框, 不削); 高度从底板顶面 z 0 起算", size=2.2, ha="center")

# ---- 技术要求 ----
y = notes(pg, 16, 86, "技术要求 / 说明", [
    f"1. 尺寸全部来自 xt60_clamp_v1_2.py ({g.VERSION}); 阶梯槽紧配不留余量: 本体段 {F(g.CH_W_B)}×{F(g.CH_H_B)} / 护套段 {F(g.CH_W_S)}×{F(g.CH_H_S)} (= 接头, 间隙 0), "
    f"槽台阶与接头台阶对齐; 压块与底垫嵌套面单边 {F(g.ASSY_CLR)}。",
    f"2. 外端 R{F(g.TRIM_R)} = 底盘/下罩外圆 (与玻璃托融为一体)。接头口面 r{F(g.XT_RF)} 内接 R{F(g.TRIM_R)}, 不伸出: 口面角 r{F(g.R_XT_BODY, 2)}, 中线缩进 {F(g.RECESS_C)}; "
    f"|x| < {F(g.X_ARC0)} 段圆弧在开口面外不剪, X 端剪进 {F(g.CUT_E)} (长 中线 {F(LEN_C)} / X 端 {F(LEN_E)})。",
    f"   开口端止口 (Y {F(g.Y_OPEN)}..{F(g.Y_OPEN + g.RIM_W)}) 外侧被 R{F(g.TRIM_R)} 剪去一角, X 端剩 {F(g.RIM_LEFT_E)} 宽 (体积 {g.FRONT_RIM_PCT:.0f}%); 左右侧 {F(RIM_C)}×{F(g.RIM_H)} + 后边 {F(g.BACK_RIM_W + g.ASSY_CLR)}×{F(g.RIM_H)} 完整; M3 杆 (余量 {F(g.SCREW_PLAY)}) 兜底。",
    f"3. 防呆 (详图 K): 接头本体一短边两角大圆角 → 槽 +X 侧上下两角各一条凹弧三角 R{F(g.KEY_R)}, Y 长 {F(g.KEY_LEN)} (开口面 → 槽台阶, 不被圆弧剪)。"
    f"上角属压块; 下角属底垫 (外侧 x≤{F(KEY_X_SHIM)}, 离槽壁 {F(g.ASSY_CLR)})。",
    f"   正插零干涉; 反插两角各吃进约 {F(g.KEY_PEN)} (对角), 合计 {F(g.ov_rev, 1)} mm^3 → 插不进。R{F(g.KEY_R)} / R{F(g.KEY_R_SM)} 按图估, 待卡尺确认; 极性反了改 KEY_SIDE = −1。",
    f"4. 紧固: 2×M3×{F(g.SCREW_L)} 超薄头 + M3 大垫片 Φ9×{F(g.WASHER_T)} 从底盘底 Φ13×{F(g.DISC_CB_H)} 沉孔 (11-12 已打印底盘原样) 往上, 穿 底盘 {F(g.DISC_T)} + 底垫 {F(g.BASE_T)} + 压块 {F(g.HTOP)}; M3 法兰螺母平坐压块顶面 (无螺母座), "
    f"全局 Z{F(g.NUT_Z0_G)}..{F(g.NUT_Z1_G)}, 尖 Z{F(g.TIP_G)} → 啮合 {g.ENGAGE:.1f}/{F(g.NUT_T)} (尖低于螺母顶 {F(g.NUT_Z1_G - g.TIP_G)})。",
    f"5. 打印 (压块): 顶面朝下平放, 免支撑。脚本按 mesh 统计悬空 (朝下 >45°, 不计贴床面): 顶面朝下 {F(OH_CLAMP_TOPDOWN, 1)} mm^2 —— 槽/止口/U 口都开口朝上, 上角防呆变成贴床侧的圆角, 顶面已无螺母座;",
    f"   若底面朝下则有 {F(OH_CLAMP_TOPUP, 0)} mm^2 悬空 (槽顶 {F(g.CH_W_S)} 宽桥接会塌, 正好是零间隙配合面; 侧止口 {F(RIM_C)} 悬臂; U 口拱顶), 不推荐。",
    f"6. 层高: 0.1 或 0.25 (首层也 0.25); 避免 0.2 —— 本体段槽顶 {F(g.CH_H_B)} 与凸台 {F(g.SHIM_T)} 落在层中间, 零间隙会过盈。重 约 {F(g.vol_part * 1.24e-3, 1)} g PLA (实心 {F(g.vol_part / 1000, 2)} cm^3)。",
], size=2.3, dy=3.15)
assert y > 36, f"说明压到标题栏 {y}"

title_block(pg, "xt60_clamp_v1_2", "XT60 压块 (件 1): M3 从下往上 + 防呆上角 + R110 外端", "1 / 台",
            "主/俯/B-B/D-D 2.5:1, 详图 K 5:1, A 4:1", "顶面朝下, 免支撑", 1,
            "STL/STEP: v1.2/models/xt60_clamp_v1_2/xt60_clamp_v1_2.stl / .step   (视图 = STL 消隐投影, 剖视/详图 = manifold 精确截面; 由 v1.2/scripts/drawing_xt60_clamp_v1_2.py 生成)")
FIG1 = pg

# =====================================================================================
# 第 2 页: 底垫
# =====================================================================================
pg = Page()
frame(pg, f"POV3D V1.2 — xt60_shim_v1_2   XT60 压块底垫 (件 2, {g.VERSION})",
      f"底板 {F(g.BASE_T)} + 本体下凸台 {F(g.SHIM_W)}×{F(g.SHIM_L)}×{F(g.SHIM_T)} + 止口 (左右 {F(g.RIM_W)} / 后边 {F(g.BACK_RIM_W)}, 高 {F(g.RIM_H)}) + 下角防呆 R{F(g.KEY_R)}  ·  "
      f"外端 R{F(g.TRIM_R)} 同压块  ·  2×Φ{F(g.HOLE_D)} 同压块孔 (M3 杆定位)", 2)

# 俯视
S2, D2 = 4.0, 8.0
TX, TY = 118.0, 156.0
TT = lambda x, y: (TX + x * S2, TY + y * S2)  # noqa: E731
view_title(pg, TX, 233, "俯视图 4:1", "沿 −Z 看; 下方 = 开口端 (R110)")
vis, hid = P_SHIM.view_lines("top")
segs(pg, hid, TT, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
segs(pg, vis, TT, lw=0.4)
chain(pg, TT(-g.HALF_L - 3, g.HOLE_Y), TT(g.HALF_L + 3, g.HOLE_Y))
for sx in (-1, 1):
    chain(pg, TT(sx * g.HX, g.HOLE_Y - 5), TT(sx * g.HX, g.HOLE_Y + 5))
sec_mark(pg, TT(0, Y_FC - 0.6), TT(0, g.Y_END + 0.8), "E", (-1, 0))
sec_mark(pg, TT(-g.HALF_L - 1.5, -5.0), TT(g.HALF_L + 1.5, -5.0), "C", (0, 1))
xr, xl = TT(g.HALF_L, 0)[0], TT(-g.HALF_L, 0)[0]
vd(pg, TT(0, Y_FE)[1], TT(0, g.Y_END)[1], xr, xr, xr + 11, f"{F(LEN_E)} (X 端)", side="r")
vd(pg, TT(0, Y_FC)[1], TT(0, g.Y_END)[1], TT(0, 0)[0], xr, xr + 21, f"{F(LEN_C)} (中线)", side="r")
vd(pg, TT(0, g.HOLE_Y)[1], TT(0, g.Y_END)[1], TT(-g.HX, 0)[0], xl, xl - 9, F(g.Y_END - g.HOLE_Y), side="l")
vd(pg, TT(0, g.Y_CAPI)[1], TT(0, g.Y_END)[1], TT(-g.HALF_L + 3, g.Y_CAPI)[0], xl, xl - 18, f"后边框 {F(g.BACK_RIM_W)}", side="l")
hd(pg, TT(-g.HX, 0)[0], TT(g.HX, 0)[0], TT(0, g.HOLE_Y)[1], TT(0, g.HOLE_Y)[1], TT(0, Y_FC)[1] - 10, f"{F(g.PITCH)} (2×Φ{F(g.HOLE_D)} 通孔)")
hd(pg, xl, xr, TT(0, Y_FE)[1], TT(0, Y_FE)[1], TT(0, Y_FC)[1] - 18, F(g.L))
hd(pg, TT(-g.SHIM_W / 2, 0)[0], TT(g.SHIM_W / 2, 0)[0], TT(0, -2.5)[1], TT(0, -2.5)[1], TT(0, -2.5)[1],
   f"凸台 {F(g.SHIM_W)} (长到护套前端 Y {F(g.SHIM_Y1)})")
hd(pg, TT(g.HALF_L - g.RIM_W, 0)[0], xr, TT(0, g.Y_CAPI)[1], TT(0, g.Y_CAPI)[1], TT(0, g.Y_END)[1] + 7, F(g.RIM_W))
leader(pg, TT(KEY_X_SHIM - 0.6, -6.5), (xr + 3, TT(0, Y_FC)[1] - 3),
       f"下角防呆 (+X 侧), Y 长 {F(g.KEY_LEN)}", ha="left")
leader(pg, TT(-g.HALF_L + g.RIM_W / 2, -3), (xl - 4, TT(0, -8)[1]), f"侧止口边框\n{F(g.RIM_W)} 宽 × {F(g.RIM_H)} 高", ha="right", size=2.3)

# 主视 (端视)
FX, FZ = 118.0, 249.0
TF = lambda x, z: (FX + x * S2, FZ + z * S2)  # noqa: E731
view_title(pg, FX, 267, "主视图 (端视) 4:1", None)
pg.text(FX, 263.0, "沿 +Y 看 (从开口端)", size=2.4, ha="center")
vis, hid = P_SHIM.view_lines("front")
segs(pg, hid, TF, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
segs(pg, vis, TF, lw=0.4)
xl = TF(-g.HALF_L, 0)[0]
vd(pg, TF(0, -g.BASE_T)[1], TF(0, g.RIM_H)[1], xl, xl, xl - 6, F(g.BASE_T + g.RIM_H), side="l")
vd(pg, TF(0, -g.BASE_T)[1], TF(0, 0)[1], TF(g.HALF_L, 0)[0], TF(g.HALF_L, 0)[0], TF(g.HALF_L, 0)[0] + 6, F(g.BASE_T), side="r")

# 剖视 E-E (X=0)
BX, BZ = 315.0, 244.0
TB = lambda y, z: (BX - (y - BYM) * S2, BZ + z * S2)  # noqa: E731
view_title(pg, BX, 267, "E-E 剖视 4:1", None)
pg.text(BX, 263.0, "过对称面 X=0, 沿 +X 看 (开口端在右)", size=2.4, ha="center")
sec_patch(pg, sec_x(SHIM, 0.0), TB, hatch="\\\\\\\\")
yb0 = TB(0, -g.BASE_T)[1]
hd(pg, TB(g.SHIM_Y1, 0)[0], TB(Y_FC, 0)[0], TB(0, g.SHIM_T)[1], yb0, yb0 - 6, f"凸台 {F(g.SHIM_Y1 - Y_FC)}")
hd(pg, TB(g.Y_END, 0)[0], TB(g.Y_CAPI, 0)[0], TB(0, g.RIM_H)[1], yb0, yb0 - 6, F(g.BACK_RIM_W))
hd(pg, TB(g.Y_END, 0)[0], TB(Y_FC, 0)[0], yb0, yb0, yb0 - 13, f"{F(LEN_C)} (中线)")
xR = TB(Y_FC, 0)[0]
vd(pg, TB(0, 0)[1], TB(0, g.SHIM_T)[1], xR, xR, xR + 6, F(g.SHIM_T), side="r", ty=TB(0, g.SHIM_T)[1] + 5)
xL = TB(g.Y_END, 0)[0]
vd(pg, TB(0, -g.BASE_T)[1], TB(0, g.RIM_H)[1], xL, xL, xL - 6, F(g.BASE_T + g.RIM_H), side="l")
pg.text(BX, yb0 - 19, f"凸台顶 z {F(g.SHIM_T)} 托本体 (本体底面离护套底面 {F(g.BODY_LIFT)}); 护套直接坐底板顶 z 0, 后端顶后边框", size=2.2, ha="center")

# 详图 K2
KX, KZ = 312.0, 145.0
KU0, KU1, KW0, KW1 = 3.4, 10.4, -2.0, 3.6
TK = lambda x, z: (KX + (x - (KU0 + KU1) / 2) * D2, KZ + z * D2)  # noqa: E731
view_title(pg, KX, 203, "详图 K2 8:1 (C-C 剖, Y = −5)", "下角防呆 属底垫; 灰点划 = 正插接头 / 细实线 = 压块槽壁 (0.1 隙)")
sec_patch(pg, clip_cs(sec_y(SHIM, -5.0), KU0, KU1, KW0, KW1), TK, hatch="\\\\\\\\")
for q in clip_cs(xs, KU0 - 0.5, KU1, 0, KW1):
    poly(pg, [tuple(p) for p in np.asarray(q)], TK, lw=0.22, ls=(0, (6, 1.5, 1.5, 1.5)), color="0.45", closed=True, z=4)
for q in clip_cs(sec_y(PART, -5.0), KU0, KU1, 0, KW1):
    poly(pg, [tuple(p) for p in np.asarray(q)], TK, lw=0.2, color="0.5", closed=True, z=2)
pg.line(TK(KU0, 0)[0], TK(0, KW0)[1], TK(KU0, 0)[0], TK(0, KW1)[1], lw=0.15)
pg.line(TK(cl[0], 0)[0] - 1.5, TK(*cl)[1], TK(cl[0], 0)[0] + 1.5, TK(*cl)[1], lw=0.15)
pg.line(TK(cl[0], 0)[0], TK(*cl)[1] - 1.5, TK(cl[0], 0)[0], TK(*cl)[1] + 1.5, lw=0.15)
leader(pg, TK(*pl), (TK(KU1, 0)[0] + 4, TK(0, 2.6)[1]), f"R{F(R)} 凹弧 (弧心 x{F(cl[0])}, z{F(cl[1])})\n贴接头 R{F(R)} 圆角", ha="left", size=2.4)
pg.text(TK(KU1, 0)[0] + 4, TK(0, 0.9)[1], "R 按图估, 待卡尺确认", size=2.5, weight="bold")
pg.text(TK(KU1, 0)[0] + 4, TK(0, 0.2)[1] - 1.5, f"凸台边 x {F(KEY_X_SHIM)} = 防呆外侧面", size=2.2)
pg.text(TK(KU1, 0)[0] + 4, TK(0, -0.5)[1] - 2.5, f"压块槽壁 x {F(g.CH_W_B / 2)}", size=2.2)
hd(pg, TK(KEY_X_SHIM, 0)[0], TK(xw, 0)[0], TK(0, 1.4)[1], TK(0, 1.4)[1], TK(0, KW1)[1] + 4, F(g.ASSY_CLR), tx=TK(xw, 0)[0] + 8)
hd(pg, TK(cl[0], 0)[0], TK(KEY_X_SHIM, 0)[0], TK(0, g.BODY_LIFT)[1], TK(0, g.BODY_LIFT)[1], TK(0, KW0)[1] - 5,
   f"{F(KEY_X_SHIM - cl[0])}")
xk = TK(KU0, 0)[0]
vd(pg, TK(0, -g.BASE_T)[1], TK(0, 0)[1], xk, xk, xk - 6, F(g.BASE_T), side="l")
vd(pg, TK(0, 0)[1], TK(0, g.BODY_LIFT)[1], xk, xk, xk - 14, F(g.SHIM_T), side="l", ty=TK(0, g.BODY_LIFT)[1] + 5)

# 技术要求 2
notes(pg, 16, 86, "技术要求 / 说明 (底垫)", [
    f"1. 外形与压块同 ({F(g.L)} 宽, 外端 R{F(g.TRIM_R)}, 中线长 {F(LEN_C)} / X 端 {F(LEN_E)}); 底板 {F(g.BASE_T)}, 止口边框高 {F(g.RIM_H)}: 左右 / 开口端宽 {F(g.RIM_W)} (开口端槽口处断开, 外侧被 R{F(g.TRIM_R)} 剪, X 端剩 {F(g.RIM_LEFT_E)}), 后边 (出线边) 宽 {F(g.BACK_RIM_W)}。",
    f"2. 凸台 {F(g.SHIM_W)} 宽 × 高 {F(g.SHIM_T)}, 从开口面到护套前端面 (Y {F(g.SHIM_Y1)}), 卡进压块本体段槽两侧各 {F(g.SHIM_CLR)}; 托住接头本体。",
    f"3. 下角防呆 (V1.2-b 从压块移来): 凸台顶上一条凹弧三角, 弧心 ({F(cl[0])}, {F(cl[1])}) R{F(g.KEY_R)}, 外侧面 x {F(KEY_X_SHIM)} 与凸台边齐 (离压块槽壁 {F(g.ASSY_CLR)}), Y 长 {F(g.KEY_LEN)}。"
    f" R 按图估, 待卡尺确认。",
    f"4. 定位: ±X / ±Y 靠止口 (嵌套 {F(g.ASSY_CLR)}; +Y 为剪剩的开口端止口内侧面); 2×M3 杆 (孔 Φ{F(g.HOLE_D)}, 余量 {F(g.SCREW_PLAY)}) 兜底。",
    f"5. 打印: 底面朝下平放, 免支撑 (悬空面 {F(OH_SHIM, 1)} mm^2: 凸台/边框/防呆全部朝上, 防呆凹弧朝上开口)。层高同压块 (0.1 或 0.25)。",
    f"6. 装配: 底垫放底盘 → 接头 (本体坐凸台, 大圆角朝 +X 防呆侧, 护套顶后边框) → 压块扣下 (套止口, 线落 U 口) → M3 从底盘下往上, 法兰螺母平坐压块顶面拧紧。",
], size=2.3, dy=3.3)
title_block(pg, "xt60_shim_v1_2", "XT60 压块底垫 (件 2): 凸台 + 止口 + 下角防呆", "1 / 台",
            "俯/主/E-E 4:1, 详图 K2 8:1", "底面朝下, 免支撑", 2,
            "STL/STEP: v1.2/models/xt60_clamp_v1_2/xt60_shim_v1_2.stl / .step   (STL 局部 z 0..4 = 本图 z −2..2; 视图 = STL 消隐投影, 剖视/详图 = manifold 精确截面)")
FIG2 = pg

# ---------------- 输出 ----------------
PDF_OUT = OUT
try:
    with PdfPages(PDF_OUT) as pdf:
        pdf.savefig(FIG1.fig)
        pdf.savefig(FIG2.fig)
except PermissionError:                     # PDF 在查看器里开着被锁 → 写 .NEW.pdf
    PDF_OUT = OUT.with_name(OUT.stem + ".NEW.pdf")
    with PdfPages(PDF_OUT) as pdf:
        pdf.savefig(FIG1.fig)
        pdf.savefig(FIG2.fig)
    print(f"!! {OUT.name} 被占用, 改写 {PDF_OUT.name}")
FIG1.fig.savefig(OUT.with_name(OUT.stem + "_preview.png"), dpi=110)
FIG2.fig.savefig(OUT.with_name(OUT.stem + "_p2_preview.png"), dpi=110)
print(f"wrote {PDF_OUT}")
print(f"  悬空 (朝下>45°): 压块顶面朝下 {OH_CLAMP_TOPDOWN:.2f} mm^2 / 底面朝下 {OH_CLAMP_TOPUP:.1f} mm^2; 底垫底面朝下 {OH_SHIM:.2f} mm^2")
