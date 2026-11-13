"""
线圈驱动两件打印件 A3 工程图 (POV3D V1.2, 2026-11-12):
    cd v1.2/scripts && ../../.venv/bin/python drawing_coil_clamps_v1_2.py
输出 v1.2/models/mos_clamp_v1_2/mos_clamp_v1_2_drawing.pdf (+ _preview.png)
     v1.2/models/cap_clamp_v1_2/cap_clamp_v1_2_drawing.pdf (+ _preview.png)

版式照 drawing_xt60_clamp_v1_2.py (主视 / 俯视 / 剖视 + 放大详图 + 技术要求 + 标题栏)。
几何与数值全部来自生成器: mos_clamp_v1_2.make_mos_clamp / cap_clamp_v1_2.make_cap_clamp, 参数取整机快照
v1.2/out/coil_drv_params.json (coil_drv_geom.make 写出, 与导出 STL 一致; 不 import build_v1_2)。
  · OCP 实体 → 按面方向三角化 + 顶点合并 → manifold (与 STL 同精度)
  · 主视 / 俯视: drawing_v1_0.Part 消隐投影; 剖视 / 详图: manifold.slice 精确平面截面
  · 出图前核对: 件外形 = 已导出 STL 的包围盒 (assert)
图面坐标: x' = x − 板中轴 (外形中线), y' = y − 件中线 (孔心), z = 装配系 (Z0 = 底盘顶)。
"""
import json
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
from matplotlib.collections import LineCollection  # noqa: E402
import manifold3d as m3d  # noqa: E402
from OCP.BRepMesh import BRepMesh_IncrementalMesh  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED  # noqa: E402
from OCP.TopoDS import TopoDS  # noqa: E402
from OCP.TopLoc import TopLoc_Location  # noqa: E402
from OCP.BRep import BRep_Tool  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402

import mos_clamp_v1_2 as MOSG  # noqa: E402
import cap_clamp_v1_2 as CAPG  # noqa: E402

plt.rcParams["hatch.linewidth"] = 0.35
V12 = HERE.parent
PARAMS = json.loads((V12 / "out" / "coil_drv_params.json").read_text(encoding="utf-8"))
with contextlib.redirect_stdout(io.StringIO()):          # 生成器的 KEEPOUT 提示不刷屏
    RM = MOSG.make_mos_clamp(PARAMS["mos_clamp"])
    RC = CAPG.make_cap_clamp(PARAMS["cap_clamp"])


# ---------------- 工具 ----------------
def F(v, n=2):
    s = f"{v:.{n}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def mm(s):
    s = str(s)
    if not s or "mm" in s or "°" in s or "→" in s:
        return s
    return s.replace(" (", " mm (", 1) if " (" in s else s + " mm"


def to_manifold(sh, dx=0.0, dy=0.0, defl=0.005):
    """OCP 实体 → manifold (按面方向定三角绕向, 共享边上的节点按坐标合并), 再平移 (dx, dy, 0)。"""
    BRepMesh_IncrementalMesh(sh, defl, False, 0.05, True)
    V, Fc = [], []
    ex = TopExp_Explorer(sh, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current()) if hasattr(TopoDS, "Face_s") else TopoDS.Face(ex.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            tr = loc.Transformation()
            base = len(V)
            for i in range(tri.NbNodes()):
                p = tri.Node(i + 1).Transformed(tr)
                V.append((p.X(), p.Y(), p.Z()))
            rev = f.Orientation() == TopAbs_REVERSED
            for i in range(tri.NbTriangles()):
                a, b, c = tri.Triangle(i + 1).Get()
                Fc.append((base + a - 1, base + c - 1, base + b - 1) if rev else (base + a - 1, base + b - 1, base + c - 1))
        ex.Next()
    V = np.asarray(V)
    key = np.round(V / 1e-5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    Vu = V[first]
    T = inv.reshape(-1)[np.asarray(Fc)]
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    m = m3d.Manifold(m3d.Mesh(vert_properties=Vu.astype(np.float32), tri_verts=T.astype(np.uint32)))
    assert m.status() == m3d.Error.NoError and not m.is_empty(), ("三角化不成流形", m.status())
    return m.translate((dx, dy, 0.0))


def tris_of(m):
    me = m.to_mesh()
    v = np.asarray(me.vert_properties)[:, :3]
    return v[np.asarray(me.tri_verts)]


def stl_extent(path):
    b = Path(path).read_bytes()
    n = int.from_bytes(b[80:84], "little")
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))["v"].reshape(-1, 3)
    return a.max(0) - a.min(0)


def sec_y(m, y0):
    """平面 Y=y0 截面 → CrossSection, 坐标 (x, z) (沿 +Y 看, X 向右)。"""
    return m.translate((0, -y0, 0)).rotate((-90, 0, 0)).slice(0.0)


def sec_x(m, x0):
    """平面 X=x0 截面 → [(y, z) 多边形]。"""
    cs = m.translate((-x0, 0, 0)).rotate((0, 90, 0)).slice(0.0)
    return [np.asarray(q)[:, ::-1] for q in cs.to_polygons()]


def clip_cs(cs, u0, u1, w0, w1):
    return (cs ^ m3d.CrossSection.square((u1 - u0, w1 - w0)).translate((u0, w0))).to_polygons()


def layer_round(v, h):
    return math.floor(v / h + 0.5 + 1e-9) * h


# ---------------- 页面工具 (同 drawing_xt60_clamp_v1_2) ----------------
ARR = 2.6
TXT = []        # 自检: 记录所有文字对象


def T_(pg, *a, **k):
    t = pg.text(*a, **k)
    TXT.append(t)
    return t


def hd(pg, x0, x1, yg0, yg1, yd, label, size=2.5, tx=None):
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
    T_(pg, (x0 + x1) / 2 if tx is None else tx, yd + 0.7, mm(label), size=size, ha="center", va="bottom", halo=True)


def vd(pg, y0, y1, xg0, xg1, xd, label, size=2.5, side=None, ty=None):
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
        T_(pg, xd + (0.8 if side == "r" else -0.8), (y0 + y1) / 2, lab, size=size,
           ha="left" if side == "r" else "right", va="center", rot=90, halo=True)
    else:
        yy = (y0 + y1) / 2 if ty is None else ty
        T_(pg, xd + (1.0 if side == "r" else -1.0), yy, lab, size=size,
           ha="left" if side == "r" else "right", va="center", halo=True)


def leader(pg, p, t, s, size=2.5, ha="left", dot=True):
    if dot:
        pg.ax.add_patch(MCircle(p, 0.35, color="k", zorder=6, lw=0))
    pg.line(p[0], p[1], t[0], t[1], lw=0.15)
    sh = 2.5 if ha == "left" else -2.5
    pg.line(t[0], t[1], t[0] + sh, t[1], lw=0.15)
    for i, ln in enumerate(s.split("\n")):
        T_(pg, t[0] + sh + (0.6 if ha == "left" else -0.6), t[1] - i * size * 1.25, ln, size=size,
           ha=ha, va="center", halo=True)


def segs(pg, S, T, lw=0.35, ls="-", color="k", z=3):
    if not S:
        return
    L = [[T(*a), T(*b)] for a, b in S]
    pg.ax.add_collection(LineCollection(L, linewidths=lw * MM_PT, colors=color, linestyles=ls, zorder=z, capstyle="butt"))


def poly(pg, pts, T, lw=0.35, ls="-", color="k", closed=False, z=3):
    P = [T(*p) for p in pts]
    if closed:
        P.append(P[0])
    xs, ys = zip(*P)
    pg.ax.plot(xs, ys, lw=lw * MM_PT, ls=ls, color=color, zorder=z, solid_capstyle="butt")


def polys(pg, Q, T, **k):
    for q in Q:
        poly(pg, [tuple(p) for p in np.asarray(q)], T, closed=True, **k)


def chain(pg, a, b):
    pg.ax.plot([a[0], b[0]], [a[1], b[1]], lw=0.15 * MM_PT, color="0.3", ls=(0, (9, 2, 1.5, 2)), zorder=2)


def sec_patch(pg, Q, T, hatch="////", lw=0.4, ec="k", hc=None, z=3):
    V, C = [], []
    for q in Q:
        q = [T(*p) for p in np.asarray(q)]
        V += q + [q[0]]
        C += [MPath.MOVETO] + [MPath.LINETO] * (len(q) - 1) + [MPath.CLOSEPOLY]
    if not V:
        return
    pp = PathPatch(MPath(np.array(V), C), facecolor="none", edgecolor=ec, lw=lw * MM_PT, hatch=hatch, zorder=z)
    pg.ax.add_patch(pp)
    if hc is not None:
        pp.set_edgecolor(hc)
        pg.ax.add_patch(PathPatch(MPath(np.array(V), C), facecolor="none", edgecolor=ec, lw=lw * MM_PT, zorder=z))


def view_title(pg, x, y, s, sub=None):
    T_(pg, x, y, s, size=3.6, ha="center", weight="bold")
    if sub:
        T_(pg, x, y - 4.2, sub, size=2.4, ha="center")


def sec_mark(pg, p0, p1, letter, look):
    d = np.subtract(p1, p0)
    d = d / np.linalg.norm(d)
    for p, sg in ((p0, 1), (p1, -1)):
        pg.line(p[0], p[1], p[0] + sg * d[0] * 4, p[1] + sg * d[1] * 4, lw=0.6)
        pg.line(p[0], p[1], p[0] + look[0] * 4.5, p[1] + look[1] * 4.5, lw=0.2)
        pg.arrow(p[0] + look[0] * 4.5, p[1] + look[1] * 4.5, look[0], look[1], L=2.0, Wd=0.6)
        T_(pg, p[0] - sg * d[0] * 2.5 + look[0] * 2.5, p[1] - sg * d[1] * 2.5 + look[1] * 2.5, letter, size=3.2,
           ha="center", va="center")
    chain(pg, p0, p1)


def frame(pg, title, sub):
    pg.rect(5, 5, PAGE_W - 5, PAGE_H - 5, lw=0.5)
    T_(pg, PAGE_W / 2, PAGE_H - 13, title, size=5.0, ha="center")
    T_(pg, PAGE_W / 2, PAGE_H - 19, sub, size=2.6, ha="center")
    tb = (10, 10, PAGE_W - 10, 34)
    pg.rect(*tb, lw=0.35)
    pg.line(tb[0], 22, tb[2], 22, lw=0.2)
    for xx in (130, 200, 256, 300):
        pg.line(xx, tb[1], xx, tb[3], lw=0.2)


def title_block(pg, code, short, qty, scale, orient, ver, src):
    T_(pg, 14, 26, code, size=4.4, weight="bold")
    T_(pg, 14, 14, short, size=2.6)
    T_(pg, 134, 26, f"数量: {qty}", size=2.9)
    T_(pg, 134, 14, "材料: PLA / PETG", size=2.9)
    T_(pg, 204, 26, scale, size=2.6)
    T_(pg, 204, 14, "单位 mm / 第一角", size=2.9)
    T_(pg, 260, 26, f"{ver}  2026-11-12", size=2.6)
    T_(pg, 260, 14, "POV3D V1.2  第 1/1 页", size=2.6)
    T_(pg, 304, 26, "打印姿态:", size=2.9)
    T_(pg, 304, 14, orient, size=2.5)
    T_(pg, 14, 6.5, src, size=2.2)


def notes(pg, x, y, head, items, size=2.3, dy=3.15):
    T_(pg, x, y, head, size=3.0, weight="bold")
    y -= 4.4
    for s in items:
        for k, ln in enumerate(s.split("\n")):
            T_(pg, x + (0 if k == 0 else 3.0), y, ln, size=size)
            y -= dy
    return y


def break_v(pg, x, y0, y1):
    """局部详图窗口的波浪断裂线 (竖)。"""
    ys = np.linspace(y0, y1, 40)
    xs = x + 0.8 * np.sin((ys - y0) / (y1 - y0) * 4 * math.pi)
    pg.ax.plot(xs, ys, lw=0.15 * MM_PT, color="k", zorder=4)


GR = dict(lw=0.25, color="0.45")          # 示意件 (螺丝/铜螺母/MOS/电容/底盘)
DASH = (0, (6, 1.5, 1.5, 1.5))


def insert_detail(pg, cx, cy, Dk, part, ins, scr, hx, xo, top, ear, P, tip, extra_z=None, letter="E"):
    """详图: 铜螺母孔 (过孔心 Y 剖), 窗口 = 右孔 ±; part/ins/scr = 截面 CrossSection (x', z)。"""
    ID, HD, IL = P["INSERT_D"], P["HOLE_D"], P["INSERT_L"]
    u0, u1 = hx - ID / 2 - 2.6, xo + 0.6
    w0, w1 = max(ear - 3.0, -0.3), top + 0.6
    uc = (u0 + u1) / 2
    TK = lambda x, z: (cx + (x - uc) * Dk, cy + (z - (w0 + w1) / 2) * Dk)  # noqa: E731
    sec_patch(pg, clip_cs(part, u0, u1, w0, top + 1), TK, hatch="////")
    for q in clip_cs(ins, u0, u1, w0, w1 + 1):
        poly(pg, [tuple(p) for p in np.asarray(q)], TK, closed=True, z=4, **GR)
    for q in clip_cs(scr, u0, u1, w0, w1 + 1):
        poly(pg, [tuple(p) for p in np.asarray(q)], TK, closed=True, z=4, ls=(0, (4, 1.2)), lw=0.22, color="0.4")
    break_v(pg, TK(u0, 0)[0], TK(0, w0)[1], TK(0, top)[1])
    chain(pg, TK(hx, w0 - 0.6), TK(hx, top + 1.2))
    xr = TK(xo, 0)[0]
    # 孔径
    yt = TK(0, top)[1]
    hd(pg, TK(hx - ID / 2, 0)[0], TK(hx + ID / 2, 0)[0], yt, yt, yt + 6, f"Φ{F(ID)}")
    yb = TK(0, w0)[1]
    hd(pg, TK(hx - HD / 2, 0)[0], TK(hx + HD / 2, 0)[0], TK(0, ear - 0.6)[1], TK(0, ear - 0.6)[1], yb - 4, f"Φ{F(HD)} 通")
    # 深度 / 铜螺母长 / 底隙
    vd(pg, TK(0, ear)[1], yt, TK(hx + ID / 2, 0)[0], TK(hx + ID / 2, 0)[0], xr + 6, f"孔深 {F(top - ear)}", side="r")
    vd(pg, TK(0, top - IL)[1], yt, xr, xr, xr + 19, f"铜螺母 {F(IL)}", side="r")
    vd(pg, TK(0, ear)[1], TK(0, top - IL)[1], xr, xr, xr + 19, F(top - IL - ear), side="r", ty=TK(0, ear)[1] - 6.5)
    # 端壁
    hd(pg, TK(hx + ID / 2, 0)[0], xr, TK(0, top - 0.8)[1], TK(0, top - 0.8)[1], yt + 13, F(xo - hx - ID / 2), tx=xr + 7)
    # 孔底台阶环 (打印唯一朝下面)
    leader(pg, TK(hx - (ID + HD) / 4, ear), (TK(u0, 0)[0] - 3, TK(0, ear)[1] - 9),
           f"孔底台阶环 宽 {F((ID - HD) / 2)}\n= 铜螺母底支承\n(打印时唯一朝下面, 小桥接)", ha="right", size=2.2)
    leader(pg, TK(hx, tip), (TK(u0, 0)[0] - 3, TK(0, tip)[1] + 9),
           f"M3 尖 Z{F(tip)}\n(件顶 Z{F(top)})", ha="right", size=2.2)
    return TK


# =====================================================================================
# MOS 压块
# =====================================================================================
def draw_mos():
    r, P, C = RM, RM["params"], RM["checks"]
    XPC = P["XPC"]
    x0g, x1g = r["x_span"]
    ya, yb = r["y_span"]
    YM = r["holes"][0][1]
    ext = stl_extent(V12 / "models" / "mos_clamp_v1_2" / "mos_clamp_v1_2.stl")
    W, L, TOP = x1g - x0g, yb - ya, r["top"]
    assert np.allclose(ext, (W, L, TOP), atol=2e-3), ("与已导出 STL 外形不一致", ext, (W, L, TOP))
    dx, dy = -XPC, -YM
    PART = to_manifold(r["clamp"], dx, dy)
    assert abs(PART.volume() - r["volume"]) / r["volume"] < 2e-3, (PART.volume(), r["volume"])
    MOS = to_manifold(r["mos"], dx, dy)
    INS = [to_manifold(n, dx, dy) for n in r["nuts"]]
    SCR = [to_manifold(s, dx, dy) for s in r["screws"]]
    DISC = to_manifold(r["disc_block"], dx, dy)
    SINK = to_manifold(r["sink"], dx, dy)
    XO, HY = W / 2, L / 2
    HX = r["holes"][1][0] - XPC
    G0, G1 = (g - XPC for g in r["groove_x"])
    OFF = C["groove_off"]
    XB = r["mos_x"] - XPC
    Y_ROOT, Y_BODY, Y_TIP = (v - YM for v in r["mos_y"])
    Y_OPEN = ya - YM
    CH_W, CH_H, T_TOP = r["ch_w"], r["ch_h"], C["t_top"]
    EAR, TIP, BEAR = r["ear_top"], r["tip"], r["bear_z"]
    DT = P["DISC_T"]
    CAV_H = C["gap_tab_above"]
    BAF = P["BAFFLE_T"]
    OH = C["overhang"]
    S, Dk = 3.0, 5.0

    pg = Page()
    frame(pg, f"POV3D V1.2 — mos_clamp_v1_2   TO-220 MOS 压块 ({MOSG.VERSION})",
          f"外形 {F(W)} × {F(L)} × {F(TOP)}  ·  底面盲槽 {F(CH_W)} × {F(CH_H)} 偏心 +{F(OFF)}  ·  2×Φ{F(P['HOLE_D'])} 通 孔距 {F(C['pitch'])} (以板中轴对称)  ·  "
          f"顶面 2×Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])} 压 M3×{F(P['INSERT_L'])} 铜螺母  ·  M3×{F(r['screw_len'])} 从底盘下往上")

    # ---- 主视 (端视, 从 −Y 开口端看) ----
    FX, FZ = 92.0, 230.0
    TF = lambda x, z: (FX + x * S, FZ + z * S)  # noqa: E731
    view_title(pg, FX, 270, "主视图 (端视) 3:1", "沿 +Y 看 (从开口端 = 引脚侧); 槽口可见, 虚线 = 孔")
    vis, hid = Part(tris_of(PART)).view_lines("front")
    segs(pg, hid, TF, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
    segs(pg, vis, TF, lw=0.4)
    chain(pg, TF(0, -3), TF(0, TOP + 3))
    chain(pg, TF(XB, -3), TF(XB, TOP + 3))
    for sx in (-1, 1):
        chain(pg, TF(sx * HX, -3), TF(sx * HX, TOP + 2))
    hd(pg, TF(0, 0)[0], TF(XB, 0)[0], TF(0, TOP)[1], TF(0, TOP)[1], TF(0, TOP)[1] + 5, f"偏心 +{F(OFF)} (槽中线 − 板中轴)", tx=TF(XB, 0)[0] + 22)
    yb0 = TF(0, 0)[1]
    hd(pg, TF(G0, 0)[0], TF(G1, 0)[0], yb0, yb0, yb0 - 6, f"槽宽 {F(CH_W)}")
    hd(pg, TF(-HX, 0)[0], TF(HX, 0)[0], yb0, yb0, yb0 - 13, f"{F(C['pitch'])} (孔距)")
    hd(pg, TF(-XO, 0)[0], TF(XO, 0)[0], yb0, yb0, yb0 - 20, F(W))
    xl, xr = TF(-XO, 0)[0], TF(XO, 0)[0]
    vd(pg, yb0, TF(0, TOP)[1], xl, xl, xl - 7, F(TOP), side="l")
    vd(pg, yb0, TF(0, CH_H)[1], TF(G1, 0)[0], TF(G1, 0)[0], xr + 7, f"槽高 {F(CH_H)}", side="r")
    vd(pg, TF(0, CH_H)[1], TF(0, TOP)[1], xr, xr, xr + 7, f"槽顶厚 {F(T_TOP)}", side="r", ty=TF(0, TOP)[1] + 4.5)

    # ---- 俯视 ----
    TX, TY = 92.0, 158.0
    TT = lambda x, y: (TX + x * S, TY + y * S)  # noqa: E731
    view_title(pg, TX, 203, "俯视图 3:1", "沿 −Z 看 (件顶面); 下方 = 开口端 (引脚侧, −Y), 上方 = 挡板 (+Y)")
    vis, hid = Part(tris_of(PART)).view_lines("top")
    segs(pg, hid, TT, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
    segs(pg, vis, TT, lw=0.4)
    chain(pg, TT(-XO - 3, 0), TT(XO + 3, 0))
    for sx in (-1, 1):
        chain(pg, TT(sx * HX, -4), TT(sx * HX, 4))
    chain(pg, TT(0, -HY - 3), TT(0, HY + 3))
    sec_mark(pg, TT(XB, -HY - 2.5), TT(XB, HY + 2.5), "B", (1, 0))
    sec_mark(pg, TT(-XO - 4.5, 0), TT(XO + 4.5, 0), "D", (0, 1))
    xl, xr = TT(-XO, 0)[0], TT(XO, 0)[0]
    vd(pg, TT(0, -HY)[1], TT(0, HY)[1], xr, xr, xr + 24, F(L), side="r")
    vd(pg, TT(0, -HY)[1], TT(0, 0)[1], TT(-HX, 0)[0], xl, xl - 9, F(HY), side="l")
    vd(pg, TT(0, Y_TIP)[1], TT(0, HY)[1], TT(G0, 0)[0], xl, xl - 9, f"挡板 {F(BAF)}", side="l", ty=TT(0, HY)[1] + 5)
    ybt = TT(0, -HY)[1]
    hd(pg, TT(-HX, 0)[0], TT(HX, 0)[0], TT(0, 0)[1], TT(0, 0)[1], ybt - 15, f"{F(C['pitch'])} (2×Φ{F(P['HOLE_D'])} 通 + 顶面 Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])})")
    hd(pg, xl, xr, ybt, ybt, ybt - 23, F(W))
    leader(pg, TT(HX + P["INSERT_D"] / 2 * 0.71, P["INSERT_D"] / 2 * 0.71), (xr + 4, TT(0, HY)[1] + 6),
           f"2×Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])}\n压 M3×{F(P['INSERT_L'])} 铜螺母 (顶齐件顶)", size=2.3)
    leader(pg, TT(G0, -HY + 3), (xl - 3, TT(0, -HY)[1] - 3), f"虚线 = 底面盲槽\n{F(CH_W)} 宽, 偏心 +{F(OFF)}", ha="right", size=2.2)

    # ---- 剖视 B-B (X = MOS 中线) ----
    BX, BZ = 226.0, 232.0
    TB = lambda y, z: (BX - y * S, BZ + z * S)  # noqa: E731
    view_title(pg, BX, 270, "B-B 剖视 3:1", f"过 MOS 中线 (X = 板中轴 +{F(OFF)}), 沿 +X 看; 开口端在右; 灰 = TO-220 + 散热片 (示意)")
    sec_patch(pg, sec_x(PART, XB), TB, hatch="////")
    polys(pg, sec_x(MOS, XB), TB, z=4, ls=DASH, lw=0.22, color="0.45")
    sk = clip_cs(SINK.translate((0, 0, 0)).rotate((0, 0, 0)).translate((-XB, 0, 0)).rotate((0, 90, 0)).slice(0.0), -999, 999, -2.0, 0.01)
    for q in sk:
        q = np.asarray(q)[:, ::-1]
        poly(pg, [tuple(p) for p in q], TB, closed=True, lw=0.2, color="0.55")
    yb0 = TB(0, -2.0)[1]
    hd(pg, TB(Y_TIP, 0)[0], TB(Y_OPEN, 0)[0], TB(0, 0)[1], TB(0, 0)[1], yb0 - 5, f"槽长 {F(Y_TIP - Y_OPEN)}")
    hd(pg, TB(HY, 0)[0], TB(Y_TIP, 0)[0], TB(0, 0)[1], TB(0, 0)[1], yb0 - 5, F(BAF), tx=TB(HY, 0)[0] - 5)
    hd(pg, TB(HY, 0)[0], TB(-HY, 0)[0], TB(0, 0)[1], TB(0, 0)[1], yb0 - 12, F(L))
    hd(pg, TB(Y_TIP, 0)[0], TB(Y_BODY, 0)[0], TB(0, CH_H)[1], TB(0, CH_H)[1], TB(0, TOP)[1] + 5, f"背板露出段 {F(Y_TIP - Y_BODY)}")
    hd(pg, TB(Y_ROOT, 0)[0], TB(Y_OPEN, 0)[0], TB(0, CH_H)[1], TB(0, CH_H)[1], TB(0, TOP)[1] + 5, F(P["OPEN_CLR"]), tx=TB(Y_OPEN, 0)[0] - 4)
    xL, xR = TB(HY, 0)[0], TB(-HY, 0)[0]
    vd(pg, TB(0, 0)[1], TB(0, TOP)[1], xL, xL, xL - 7, F(TOP), side="l")
    vd(pg, TB(0, 0)[1], TB(0, CH_H)[1], xR, xR, xR + 7, F(CH_H), side="r")
    vd(pg, TB(0, CH_H)[1], TB(0, TOP)[1], xR, xR, xR + 7, F(T_TOP), side="r", ty=TB(0, TOP)[1] + 4.5)
    leader(pg, TB((Y_TIP + Y_BODY) / 2, (P["MOS_A1"] + CH_H) / 2), (xL - 4, TB(0, TOP)[1] + 12),
           f"背板露出段上方空腔 {F(CAV_H)} 高\n(背板 {F(P['MOS_A1'])} 厚, 不压; 只压塑封体)", ha="right", size=2.2)
    leader(pg, TB((Y_ROOT + Y_BODY) / 2, CH_H), (xR + 5, TB(0, TOP)[1] + 12),
           f"槽顶贴塑封体顶 (A {F(P['MOS_A'])}, 零过盈)", ha="left", size=2.2)
    leader(pg, TB(Y_TIP, CH_H * 0.35), (xL - 4, TB(0, -2)[1] - 18), f"挡板内面顶背板尖 (0 隙)", ha="right", size=2.2)
    T_(pg, xR + 3, TB(0, 0)[1] - 3.5, "← 引脚从开口端出", size=2.0, ha="left", va="center")

    # ---- 剖视 D-D (Y = 孔心) + 螺丝 / 铜螺母 / 底盘 ----
    DX, DZ = 252.0, 152.0
    TD = lambda x, z: (DX + x * S, DZ + z * S)  # noqa: E731
    view_title(pg, DX, 203, "D-D 剖视 3:1", f"过两孔心, 沿 +Y 看; 灰 = M3×{F(r['screw_len'])} + 铜螺母 + TO-220 + 底盘/散热片 (示意)")
    pd = sec_y(PART, 0.0)
    sec_patch(pg, pd.to_polygons(), TD, hatch="////")
    dsc = sec_y(DISC, 0.0)
    sec_patch(pg, dsc.to_polygons(), TD, hatch="\\\\\\\\", lw=0.2, ec="0.5")
    polys(pg, sec_y(SINK, 0.0).to_polygons(), TD, lw=0.2, color="0.55")
    polys(pg, sec_y(MOS, 0.0).to_polygons(), TD, z=4, ls=DASH, lw=0.22, color="0.45")
    for m in INS:
        polys(pg, sec_y(m, 0.0).to_polygons(), TD, z=4, **GR)
    for m in SCR:
        polys(pg, sec_y(m, 0.0).to_polygons(), TD, z=4, ls=(0, (4, 1.2)), lw=0.25, color="0.4")
    for sx in (-1, 1):
        chain(pg, TD(sx * HX, -DT - 3), TD(sx * HX, TOP + 2))
    chain(pg, TD(0, -DT - 1), TD(0, TOP + 2))
    T_(pg, TD(-P["SINK_W"] / 2 + 1, 0)[0], TD(0, -DT)[1] + 1.2, "散热片", size=2.0, ha="left")
    T_(pg, TD(XO + 1.0, 0)[0], TD(0, -DT)[1] + 1.2, f"底盘 {F(DT)}", size=2.0, ha="left")
    xr, xl = TD(XO + 3, 0)[0], TD(-XO - 3, 0)[0]
    vd(pg, TD(0, BEAR)[1], TD(0, TIP)[1], TD(HX + 1.5, 0)[0], TD(HX + 1.5, 0)[0], xr + 6, f"M3×{F(r['screw_len'])} (头支承 Z{F(BEAR)} → 尖 Z{F(TIP)})", side="r",
       ty=TD(0, BEAR)[1] - 2)
    vd(pg, TD(0, -DT)[1], TD(0, BEAR)[1], xr, xr, xr + 6, f"沉孔 Φ{F(P['M3_CB_D'])}×{F(P['M3_CB_H'])}", side="r", ty=TD(0, -DT)[1] - 3)
    vd(pg, TD(0, TOP - P["INSERT_L"])[1], TD(0, TOP)[1], xr, xr, xr + 22, f"进铜螺母 {F(r['engage'])}", side="r", ty=TD(0, TOP)[1] + 4)
    vd(pg, TD(0, -DT)[1], TD(0, 0)[1], xl, xl, xl - 6, F(DT), side="l")
    leader(pg, TD(-HX, TOP - 1.0), (TD(-HX, 0)[0] + 12, TD(0, TOP)[1] + 9), f"M3×{F(P['INSERT_L'])} 铜螺母 (外径 {F(P['INSERT_D'])})\n顶齐件顶 Z{F(TOP)}", ha="left", size=2.2)
    T_(pg, DX, TD(0, -DT)[1] - 7.5, f"MOS 背板朝下贴散热片顶 Z0; 两孔 Φ{F(P['M3_CB_D'])} 沉孔离散热片槽壁 {F(C['wall_cb_slot'])}; Φ{F(P['INSERT_D'])} 孔离槽壁 {F(C['wall_well_groove'])} / 离端面 {F(C['wall_well_xend'])}",
       size=2.1, ha="center")
    # 详图 E 圈
    ec = TD(HX, (EAR + TOP) / 2)
    pg.ax.add_patch(MCircle(ec, 4.2 * S / 2 + 3.5, fill=False, lw=0.25 * MM_PT, zorder=4))
    T_(pg, ec[0] + 8.5, ec[1] + 8.5, "E", size=3.4)

    # ---- 详图 E ----
    EX, EZ = 356.0, 236.0
    view_title(pg, EX, 270, "详图 E 5:1", "铜螺母孔 (D-D 剖, 右孔)")
    insert_detail(pg, EX, EZ, Dk, pd, sec_y(INS[1], 0.0), sec_y(SCR[1], 0.0), HX, XO, TOP, EAR, P, TIP)

    # ---- 层高估算 (打印姿态: 顶面贴床 ⇒ 槽底离床 = 槽顶厚, 槽深 = 件高 − 槽底) ----
    rows = []
    for h in (0.1, 0.15, 0.2, 0.25):
        Hp = layer_round(TOP, h)
        fl = layer_round(T_TOP, h)
        rows.append((h, Hp, Hp - fl, layer_round(TOP - EAR, h)))
    ok = [rw for rw in rows if rw[2] <= CH_H + 1e-6]
    best = min(ok or rows, key=lambda rw: (abs(rw[2] - CH_H), abs(rw[1] - TOP), -rw[0]))
    tab = "; ".join(f"{F(h)}: 槽深 {F(dp)} / 件高 {F(Hp)}" for h, Hp, dp, _ in rows)

    oh_area = sum(o[1] for o in OH)
    y = notes(pg, 16, 92, "技术要求 / 说明", [
        f"1. 数值全部来自 mos_clamp_v1_2.py ({MOSG.VERSION}) make_mos_clamp(整机参数 out/coil_drv_params.json, Z_LIMIT {F(P['Z_LIMIT'])} = 定子盘底 Z{F(P['STATOR_Z0'])} − 0.5); "
        f"外形 {F(W)}×{F(L)}×{F(TOP)} 已与导出 STL 核对一致。",
        f"2. 底面盲槽 {F(CH_W)}×{F(CH_H)}: 宽 = MOS E {F(P['MOS_E'])} + 2×{F(P['CLR_SIDE'])}, 高 = A {F(P['MOS_A'])} (槽顶零过盈压塑封体); 从开口端 (越过塑封体根 {F(P['OPEN_CLR'])}) 到挡板内面, 长 {F(Y_TIP - Y_OPEN)}; "
        f"挡板 {F(BAF)} 内面顶背板尖。背板露出段 ({F(Y_TIP - Y_BODY)} 长) 上方空腔 {F(CAV_H)} 高, 不压背板。",
        f"3. 偏心: 槽中线 = MOS 中线, 相对外形中线 (= 板中轴) 偏 +{F(OFF)} (+X); 外形与 2×Φ{F(P['HOLE_D'])} 通孔以板中轴对称, 孔距 {F(C['pitch'])} (孔在竖放散热片 {F(P['SINK_W'])} 宽之外)。装反 (槽偏向 −X) 则 MOS 装不进。",
        f"4. 紧固: 2×M3×{F(r['screw_len'])} 超薄头 (需新购, BOM 原有 8/12/14/20) 从底盘底面 Φ{F(P['M3_CB_D'])}×{F(P['M3_CB_H'])} 沉孔往上 (头支承 Z{F(BEAR)}), 穿底盘 {F(DT)} + 件 Φ{F(P['HOLE_D'])}, "
        f"拧进铜螺母 {F(r['engage'])} (全长), 尖 Z{F(TIP)} = 件顶, 不冒头。",
        f"5. 铜螺母孔: 顶面 Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])} (铜螺母 M3×{F(P['INSERT_L'])} + 孔底 {F(P['INSERT_CLR'])}), 铜螺母顶齐件顶; 孔径按压入款 (外径 {F(P['INSERT_D'])}, 孔 = 外径, 台钳/烙铁压入)。"
        f"\n若改用热熔款 (锥形, 外径常大于 {F(P['INSERT_D'])}) 需按厂家推荐孔径改 INSERT_D 重出 STL。",
        f"6. 打印: 顶面贴床、槽口朝上, 免支撑 (槽/挡板/通孔均为竖壁或朝上面; 唯一朝下面 = 两孔底台阶环, 宽 {F((P['INSERT_D'] - P['HOLE_D']) / 2)}, 共 {F(oh_area, 1)} mm^2, 小桥接)。",
        f"   铜螺母孔口在床面, 首层象脚会缩孔: 压铜螺母前用 Φ{F(P['INSERT_D'])} 钻头手转修孔口 (或切片开象脚补偿)。",
        f"7. 层高 (按就近层取整估算 槽深 / 件高): {tab}。建议 {F(best[0])} (槽深 {F(best[2])} ≤ {F(CH_H)}, 有压紧不松动)。重约 {F(r['volume'] * 1.24e-3, 1)} g PLA。",
        f"8. 装配: 压铜螺母 → MOS 背板朝下贴散热片 (尖朝 +Y) → 扣压块 (挡板顶背板尖, 引脚从开口端出) → M3 从底盘下往上拧紧。",
    ], size=2.3, dy=3.15)
    assert y > 36, f"说明压到标题栏 {y}"
    title_block(pg, "mos_clamp_v1_2", "TO-220 MOS 压块: 盲槽偏心 + 铜螺母 M3", "1 / 台",
                "主/俯/B-B/D-D 3:1, 详图 E 5:1", "顶面贴床, 槽口朝上, 免支撑", MOSG.VERSION,
                "STL/STEP: v1.2/models/mos_clamp_v1_2/mos_clamp_v1_2.stl / .step (打印姿态)   (视图 = 消隐投影, 剖视/详图 = 精确截面; 由 v1.2/scripts/drawing_coil_clamps_v1_2.py 生成)")
    return pg, dict(best=best, rows=rows, oh=oh_area)


# =====================================================================================
# 电容卡件
# =====================================================================================
def draw_cap():
    r, P, C = RC, RC["params"], RC["checks"]
    CX = P["CAP_CX"]
    x0g, x1g = r["x_span"]
    ya, yb = r["y_span"]
    YM = r["holes"][0][1]
    ext = stl_extent(V12 / "models" / "cap_clamp_v1_2" / "cap_clamp_v1_2.stl")
    W, L, TOP = x1g - x0g, yb - ya, r["top"]
    assert np.allclose(ext, (W, L, TOP), atol=2e-3), ("与已导出 STL 外形不一致", ext, (W, L, TOP))
    dx, dy = -CX, -YM
    PART = to_manifold(r["clamp"], dx, dy)
    assert abs(PART.volume() - r["volume"]) / r["volume"] < 2e-3, (PART.volume(), r["volume"])
    CAP = to_manifold(r["cap"], dx, dy)
    INS = [to_manifold(n, dx, dy) for n in r["nuts"]]
    SCR = [to_manifold(s, dx, dy) for s in r["screws"]]
    DISC = to_manifold(r["disc_block"], dx, dy)
    XO, HY = W / 2, L / 2
    HX = r["holes"][1][0] - CX
    R0, ZC, G = r["r0"], r["cap_zc"], r["groove"]
    T_TOP = TOP - ZC - R0
    EAR, TIP, BEAR = r["ear_top"], r["tip"], r["bear_z"]
    DT, SZ = P["DISC_T"], P["STATOR_Z0"]
    GAP_ST = SZ - TOP
    Rc = P["CAP_D"] / 2
    CY0, CY1 = P["CAP_Y0"] - YM, P["CAP_Y1"] - YM
    OH = C["overhang"]
    S, Dk = 3.0, 5.0

    pg = Page()
    frame(pg, f"POV3D V1.2 — cap_clamp_v1_2   电解电容半圆卡件 ({CAPG.VERSION}, 铜螺母版)",
          f"外形 {F(W)} × {F(L)} × {F(TOP)}  ·  底面半圆槽 R{F(R0)} (电容 Φ{F(P['CAP_D'])} + {F(P['CLR'])}), 顶厚 {F(T_TOP)}  ·  2×Φ{F(P['HOLE_D'])} 通 孔距 {F(C['pitch_used'])}  ·  "
          f"顶面 2×Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])} 压 M3×{F(P['INSERT_L'])} 铜螺母  ·  M3×{F(r['screw_len'])}  ·  件顶离定子盘底 {F(GAP_ST)}")

    # ---- 主视 (端视, 沿电容轴) ----
    FX, FZ = 92.0, 226.0
    TF = lambda x, z: (FX + x * S, FZ + z * S)  # noqa: E731
    view_title(pg, FX, 270, "主视图 (端视) 3:1", "沿 +Y 看 (沿电容轴); 半圆槽贯通可见, 虚线 = 孔")
    vis, hid = Part(tris_of(PART)).view_lines("front")
    segs(pg, hid, TF, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
    segs(pg, vis, TF, lw=0.4)
    chain(pg, TF(0, -3), TF(0, TOP + 3))
    chain(pg, TF(-R0 - 2, ZC), TF(R0 + 2, ZC))
    for sx in (-1, 1):
        chain(pg, TF(sx * HX, -3), TF(sx * HX, TOP + 2))
    yb0 = TF(0, 0)[1]
    hd(pg, TF(-R0, 0)[0], TF(R0, 0)[0], yb0, yb0, yb0 - 6, f"槽宽 {F(2 * R0)}")
    hd(pg, TF(-HX, 0)[0], TF(HX, 0)[0], yb0, yb0, yb0 - 13, f"{F(C['pitch_used'])} (孔距)")
    hd(pg, TF(-XO, 0)[0], TF(XO, 0)[0], yb0, yb0, yb0 - 20, F(W))
    xl, xr = TF(-XO, 0)[0], TF(XO, 0)[0]
    vd(pg, yb0, TF(0, TOP)[1], xl, xl, xl - 7, F(TOP), side="l")
    vd(pg, yb0, TF(0, ZC)[1], TF(-R0, 0)[0], TF(-R0, 0)[0], xl - 15, f"槽心 {F(ZC)}", side="l", ty=TF(0, 0)[1] - 4.5)
    vd(pg, TF(0, ZC + R0)[1], TF(0, TOP)[1], xr, xr, xr + 7, f"顶厚 {F(T_TOP)}", side="r", ty=TF(0, TOP)[1] + 4.5)
    vd(pg, yb0, TF(0, ZC + R0)[1], TF(0, 0)[0], xr, xr + 7, F(ZC + R0), side="r")
    a = math.radians(135)
    leader(pg, TF(R0 * math.cos(a), ZC + R0 * math.sin(a)), (TF(-XO, 0)[0] + 4, TF(0, TOP)[1] + 7),
           f"R{F(R0)} (电容 R{F(Rc)} + {F(P['CLR'])})", ha="left", size=2.3)

    # ---- 俯视 ----
    TX, TY = 92.0, 158.0
    TT = lambda x, y: (TX + x * S, TY + y * S)  # noqa: E731
    view_title(pg, TX, 197, "俯视图 3:1", "沿 −Z 看 (件顶面); 竖直方向 = 电容轴 (Y)")
    vis, hid = Part(tris_of(PART)).view_lines("top")
    segs(pg, hid, TT, lw=0.18, ls=(0, (3, 1.5)), color="0.35")
    segs(pg, vis, TT, lw=0.4)
    chain(pg, TT(-XO - 3, 0), TT(XO + 3, 0))
    chain(pg, TT(0, -HY - 3), TT(0, HY + 3))
    for sx in (-1, 1):
        chain(pg, TT(sx * HX, -4), TT(sx * HX, 4))
    sec_mark(pg, TT(0, -HY - 2.5), TT(0, HY + 2.5), "B", (1, 0))
    sec_mark(pg, TT(-XO - 4.5, 0), TT(XO + 4.5, 0), "D", (0, 1))
    xl, xr = TT(-XO, 0)[0], TT(XO, 0)[0]
    vd(pg, TT(0, -HY)[1], TT(0, HY)[1], xr, xr, xr + 24, F(L), side="r")
    vd(pg, TT(0, -HY)[1], TT(0, 0)[1], TT(-HX, 0)[0], xl, xl - 9, F(HY), side="l")
    ybt = TT(0, -HY)[1]
    hd(pg, TT(-HX, 0)[0], TT(HX, 0)[0], TT(0, 0)[1], TT(0, 0)[1], ybt - 15, f"{F(C['pitch_used'])} (2×Φ{F(P['HOLE_D'])} 通 + 顶面 Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])})")
    hd(pg, xl, xr, ybt, ybt, ybt - 23, F(W))
    leader(pg, TT(HX + P["INSERT_D"] / 2 * 0.71, P["INSERT_D"] / 2 * 0.71), (xr + 4, TT(0, HY)[1] + 8),
           f"2×Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])}\n压 M3×{F(P['INSERT_L'])} 铜螺母 (顶齐件顶)", size=2.3)
    leader(pg, TT(-R0, HY - 1.5), (xl - 3, TT(0, HY)[1] + 6), f"虚线 = 底面半圆槽\n{F(2 * R0)} 宽, 贯通", ha="right", size=2.2)

    # ---- 剖视 B-B (X = 电容轴) + 电容 + 定子盘底 ----
    BX, BZ = 232.0, 232.0
    yv0, yv1 = CY0 - 1.5, CY1 + 1.5
    ymid = (max(yv0, -HY - 6) + min(yv1, HY + 6)) / 2
    TB = lambda y, z: (BX - (y - ymid) * S, BZ + z * S)  # noqa: E731
    view_title(pg, BX, 270, "B-B 剖视 3:1", "过电容轴 (X = 0), 沿 +X 看; 灰 = 电容 / 底盘 (示意), 红点划 = 定子盘底")
    sec_patch(pg, sec_x(PART, 0.0), TB, hatch="////")
    yc0, yc1 = max(CY0, -HY - 6), min(CY1, HY + 6)
    cq = clip_cs(CAP.translate((0, 0, 0)).rotate((0, 90, 0)).slice(0.0), -1, 99, yc0, yc1)
    for q in cq:
        poly(pg, [tuple(p) for p in np.asarray(q)[:, ::-1]], TB, closed=True, z=4, ls=DASH, lw=0.22, color="0.45")
    dq = clip_cs(DISC.rotate((0, 90, 0)).slice(0.0), -99, 99, yc0, yc1)
    for q in dq:
        q = np.asarray(q)[:, ::-1]
        sec_patch(pg, [q], TB, hatch="\\\\\\\\", lw=0.2, ec="0.5")
    for yy in (yc0, yc1):
        if yy in (CY0, CY1):
            continue
        break_v(pg, TB(yy, 0)[0], TB(0, -DT)[1], TB(0, Rc * 2 - G)[1])
    xs0, xs1 = TB(yc1, 0)[0] - 2, TB(yc0, 0)[0] + 2
    pg.line(xs0, TB(0, SZ)[1], xs1, TB(0, SZ)[1], lw=0.3, color="r")
    T_(pg, xs0 - 0.8, TB(0, SZ)[1], f"定子盘底 Z{F(SZ)}", size=2.1, ha="right", va="center")
    xL, xR = TB(HY, 0)[0], TB(-HY, 0)[0]
    vd(pg, TB(0, TOP)[1], TB(0, SZ)[1], xR, xR, xR + 6, f"仅 {F(GAP_ST)}", side="r", ty=TB(0, SZ)[1] + 5.5)
    vd(pg, TB(0, ZC + R0)[1], TB(0, TOP)[1], xL, xL, xL - 6, F(T_TOP), side="l", ty=TB(0, ZC + R0)[1] - 5)
    vd(pg, TB(0, 0)[1], TB(0, TOP)[1], xL, xL, xL - 16, F(TOP), side="l")
    vd(pg, TB(0, ZC + Rc)[1], TB(0, ZC + R0)[1], TB(HY - 1, 0)[0], TB(HY - 1, 0)[0], xR + 18, F(P["CLR"]), side="r",
       ty=TB(0, ZC + Rc)[1] - 5)
    T_(pg, xR + 19, TB(0, ZC + Rc)[1] - 8.5, "电容顶隙", size=2.0, ha="left")
    yb0 = TB(0, -DT)[1]
    hd(pg, xL, xR, yb0, yb0, yb0 - 5, F(L))
    leader(pg, TB(CY0 + 2.5 if CY0 > yc0 else yc0 + 2.5, ZC), (xL - 10, TB(0, -DT)[1] - 10),
           f"电容 Φ{F(P['CAP_D'])}×{F(P['CAP_L'])} 平躺, 下沉底盘弧形槽 {F(G)}\n(轴心 Z{F(ZC)}, 顶 Z{F(ZC + Rc)})", ha="right", size=2.2)

    # ---- 剖视 D-D (Y = 孔心) ----
    DX, DZ = 236.0, 150.0
    TD = lambda x, z: (DX + x * S, DZ + z * S)  # noqa: E731
    view_title(pg, DX, 197, "D-D 剖视 3:1", f"过两孔心, 沿 +Y 看; 灰 = M3×{F(r['screw_len'])} + 铜螺母 + 电容 + 底盘 (示意), 红 = 定子盘底")
    pd = sec_y(PART, 0.0)
    sec_patch(pg, pd.to_polygons(), TD, hatch="////")
    sec_patch(pg, sec_y(DISC, 0.0).to_polygons(), TD, hatch="\\\\\\\\", lw=0.2, ec="0.5")
    polys(pg, sec_y(CAP, 0.0).to_polygons(), TD, z=4, ls=DASH, lw=0.22, color="0.45")
    for m in INS:
        polys(pg, sec_y(m, 0.0).to_polygons(), TD, z=4, **GR)
    for m in SCR:
        polys(pg, sec_y(m, 0.0).to_polygons(), TD, z=4, ls=(0, (4, 1.2)), lw=0.25, color="0.4")
    for sx in (-1, 1):
        chain(pg, TD(sx * HX, -DT - 3), TD(sx * HX, TOP + 2))
    chain(pg, TD(0, -DT - 1), TD(0, TOP + 2))
    chain(pg, TD(-Rc - 2, ZC), TD(Rc + 2, ZC))
    xdl, xdr = TD(-XO - 3, 0)[0], TD(XO + 3, 0)[0]
    pg.line(xdl, TD(0, SZ)[1], xdr, TD(0, SZ)[1], lw=0.3, color="r")
    xr, xl = TD(XO + 3, 0)[0], TD(-XO - 3, 0)[0]
    vd(pg, TD(0, BEAR)[1], TD(0, TIP)[1], TD(HX + 1.5, 0)[0], TD(HX + 1.5, 0)[0], xr + 6, f"M3×{F(r['screw_len'])} (头支承 Z{F(BEAR)} → 尖 Z{F(TIP)})", side="r",
       ty=TD(0, BEAR)[1] - 2)
    vd(pg, TD(0, -DT)[1], TD(0, BEAR)[1], xr, xr, xr + 6, f"沉孔 Φ{F(P['M3_CB_D'])}×{F(P['M3_CB_H'])}", side="r", ty=TD(0, -DT)[1] - 3)
    vd(pg, TD(0, TOP - P["INSERT_L"])[1], TD(0, TIP)[1], xr, xr, xr + 22, f"进铜螺母 {F(r['engage'])}", side="r", ty=TD(0, TOP)[1] + 6)
    vd(pg, TD(0, -DT)[1], TD(0, 0)[1], xl, xl, xl - 6, F(DT), side="l")
    vd(pg, TD(0, -G)[1], TD(0, 0)[1], TD(-Rc, 0)[0], TD(-Rc, 0)[0], xl - 14, f"槽深 {F(G)}", side="l", ty=TD(0, -G)[1] - 3)
    leader(pg, TD(-HX, TOP - 1.0), (TD(-HX, 0)[0] + 12, TD(0, TOP)[1] + 9), f"M3×{F(P['INSERT_L'])} 铜螺母 (外径 {F(P['INSERT_D'])})\n顶齐件顶 Z{F(TOP)}", ha="left", size=2.2)
    T_(pg, DX, TD(0, -DT)[1] - 7.5, f"底盘弧形槽 R{F(r['trough']['r'])} (槽底 = 电容底, 底盘剩 {F(C['disc_under_trough'])}); Φ{F(P['INSERT_D'])} 孔离半圆槽 {F(C['wall_well_groove'])} / 离端面 {F(C['wall_well_xend'])}",
       size=2.1, ha="center")
    ec = TD(HX, (EAR + TOP) / 2)
    pg.ax.add_patch(MCircle(ec, 4.2 * S / 2 + 3.5, fill=False, lw=0.25 * MM_PT, zorder=4))
    T_(pg, ec[0] + 8.5, ec[1] + 8.5, "E", size=3.4)

    # ---- 详图 E ----
    EX, EZ = 356.0, 232.0
    view_title(pg, EX, 270, "详图 E 5:1", "铜螺母孔 (D-D 剖, 右孔)")
    insert_detail(pg, EX, EZ, Dk, pd, sec_y(INS[1], 0.0), sec_y(SCR[1], 0.0), HX, XO, TOP, EAR, P, TIP)

    # ---- 层高估算 (顶面贴床: 槽顶离床 = 顶厚; 件高决定离定子盘底间隙) ----
    rows = []
    for h in (0.1, 0.15, 0.2, 0.25):
        Hp = layer_round(TOP, h)
        tp = layer_round(T_TOP, h)
        gap_st = SZ - Hp
        clr = (Hp - tp) - (ZC + Rc)           # 槽顶 (装配 Z) − 电容顶
        rows.append((h, Hp, tp, gap_st, clr))
    best = max(rows, key=lambda rw: (round(min(rw[3], rw[4]), 6), rw[0]))
    tab = "; ".join(f"{F(h)}: 件高 {F(Hp)} 离定子 {F(g)} 电容顶隙 {F(c)}" for h, Hp, tp, g, c in rows)

    oh_area = sum(o[1] for o in OH)
    y = notes(pg, 16, 92, "技术要求 / 说明", [
        f"1. 数值全部来自 cap_clamp_v1_2.py ({CAPG.VERSION}) make_cap_clamp(整机参数 out/coil_drv_params.json, 卡件 Z_LIMIT {F(P['Z_LIMIT'])}); 外形 {F(W)}×{F(L)}×{F(TOP)} 已与导出 STL 核对一致。",
        f"2. 底面半圆槽 R{F(R0)} = 电容 Φ{F(P['CAP_D'])}/2 + {F(P['CLR'])} 间隙, 槽心 Z{F(ZC)} (电容下沉底盘弧形槽 {F(G)}), 槽心以下直壁到底面 (开口 {F(2 * R0)}); 顶厚 {F(T_TOP)}。"
        f"槽沿 Y 贯通, 卡件 {F(L)} 长压在电容远端段。",
        f"3. 件顶 Z{F(TOP)} 离定子盘 (法兰盘) 底 Z{F(SZ)} 仅 {F(GAP_ST)}: 打印后量件高, 超 {F(TOP)} 要磨顶面; 顶面不得有毛刺/拉丝/象脚外翻, 不加 brim 在顶面一侧。",
        f"4. 紧固: 2×M3×{F(r['screw_len'])} 超薄头 (BOM 已有) 从底盘底面 Φ{F(P['M3_CB_D'])}×{F(P['M3_CB_H'])} 沉孔往上 (头支承 Z{F(BEAR)}), 穿底盘 {F(DT)} + 件 Φ{F(P['HOLE_D'])}, "
        f"进铜螺母 {F(r['engage'])}, 尖 Z{F(TIP)} 低于件顶 {F(TOP - TIP)}, 不冒头。孔距 {F(C['pitch_used'])} 以电容轴对称。",
        f"5. 铜螺母孔: 顶面 Φ{F(P['INSERT_D'])} 深 {F(r['hole_depth'])} (铜螺母 M3×{F(P['INSERT_L'])} + 孔底 {F(P['INSERT_CLR'])}), 铜螺母顶齐件顶; 孔径按压入款 (外径 {F(P['INSERT_D'])}, 孔 = 外径)。"
        f"\n若改用热熔款 (锥形, 外径常大于 {F(P['INSERT_D'])}) 需按厂家推荐孔径改 INSERT_D 重出 STL; 压入时铜螺母不得高出件顶 (会顶定子盘)。",
        f"6. 打印: 顶面贴床、槽口朝上, 免支撑 (半圆槽开口朝上; 唯一朝下面 = 两孔底台阶环, 宽 {F((P['INSERT_D'] - P['HOLE_D']) / 2)}, 共 {F(oh_area, 1)} mm^2, 小桥接)。",
        f"   铜螺母孔口在床面, 首层象脚会缩孔: 压铜螺母前用 Φ{F(P['INSERT_D'])} 钻头手转修孔口 (或切片开象脚补偿)。",
        f"7. 层高 (按就近层取整估算): {tab}。",
        f"   建议 {F(best[0])} (件高 {F(best[1])}, 离定子盘 {F(best[3])}, 电容顶隙 {F(best[4])})。重约 {F(r['volume'] * 1.24e-3, 1)} g PLA。",
        f"8. 装配: 压铜螺母 → 电容平躺入底盘弧形槽 (引脚朝驱动板) → 扣卡件 → M3 从底盘下往上拧紧。",
    ], size=2.3, dy=3.15)
    assert y > 36, f"说明压到标题栏 {y}"
    title_block(pg, "cap_clamp_v1_2", "电解电容半圆卡件: 实心块 + R 槽 + 铜螺母 M3", "1 / 台",
                "主/俯/B-B/D-D 3:1, 详图 E 5:1", "顶面贴床, 槽口朝上, 免支撑", CAPG.VERSION,
                "STL/STEP: v1.2/models/cap_clamp_v1_2/cap_clamp_v1_2.stl / .step (打印姿态)   (视图 = 消隐投影, 剖视/详图 = 精确截面; 由 v1.2/scripts/drawing_coil_clamps_v1_2.py 生成)")
    return pg, dict(best=best, rows=rows, oh=oh_area)


# ---------------- 自检: 文字框两两不重叠, 不出页框 ----------------
def overlap_check(pg, start):
    pg.fig.canvas.draw()
    R = pg.fig.canvas.get_renderer()
    inv = pg.ax.transData.inverted()
    boxes = []
    for t in TXT[start:]:
        if not t.get_text().strip():
            continue
        bb = t.get_window_extent(R)
        (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        boxes.append((x0, y0, x1, y1, t.get_text()[:30]))
    bad = []
    for i in range(len(boxes)):
        a = boxes[i]
        if a[0] < 5 or a[2] > PAGE_W - 5 or a[1] < 5 or a[3] > PAGE_H - 5:
            bad.append(("出框", a[4]))
        for j in range(i + 1, len(boxes)):
            b = boxes[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 0.3 and oy > 0.3:
                bad.append((a[4], b[4], round(ox, 2), round(oy, 2)))
    return bad


if __name__ == "__main__":
    for name, fn in (("mos_clamp_v1_2", draw_mos), ("cap_clamp_v1_2", draw_cap)):
        n0 = len(TXT)
        pg, info = fn()
        bad = overlap_check(pg, n0)
        out = V12 / "models" / name / f"{name}_drawing.pdf"
        pg.fig.savefig(out)
        pg.fig.savefig(out.with_name(out.stem + "_preview.png"), dpi=110)
        plt.close(pg.fig)
        print(f"wrote {out}")
        print(f"  层高表 {info['rows']}  建议 {info['best'][0]}; 朝下面 {info['oh']:.2f} mm^2")
        if bad:
            print("  [文字重叠/出框]")
            for b in bad:
                print("   ", b)
        else:
            print("  文字无重叠")
