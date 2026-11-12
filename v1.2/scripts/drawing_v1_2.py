"""
V1.2 A3 工程图引擎 (2026-11-12), 版式照 v0.2/print/hub_disc/hub_disc_drawing.pdf (models/hub_disc/build_drawing.py):
  · 左: 俯视图 (STL 消隐投影, 借 v1.0 drawing_v1_0.Part) + 上方 Φ 尺寸链 + A-A 剖切线 + 孔组字母
  · 右上: 剖视 A-A (半剖, 轴线 → 外缘) —— 直接 BRepAlgoAPI_Section 剖 B-rep, 与模型逐位一致; 右侧高度尺寸
  · 右中: 详图 (每种非普通通孔: 沉孔 / 铜螺母孔 / 盲窝 / 让位槽 各一张, 过孔心径向剖, 自动放大)
  · 右下: 孔表 + 说明; 底: 标题栏
  · 所有尺寸带 " mm"; 窄尺寸自动外箭头。
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v1.0" / "models"))
from drawing_v1_0 import Page, Part, read_stl, _fmt as F, PAGE_W, PAGE_H, MM_PT  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

from OCP.BRepAlgoAPI import BRepAlgoAPI_Section  # noqa: E402
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopAbs import TopAbs_EDGE  # noqa: E402
from OCP.TopoDS import TopoDS  # noqa: E402
from OCP.BRepAdaptor import BRepAdaptor_Curve  # noqa: E402
from OCP.GCPnts import GCPnts_QuasiUniformDeflection  # noqa: E402

SCALES = [(5, "5:1"), (4, "4:1"), (3, "3:1"), (2.5, "2.5:1"), (2, "2:1"), (1.5, "1.5:1"), (1, "1:1"),
          (2 / 3, "1:1.5"), (0.5, "1:2")]
ARR_L = 3.0


def mm(s):
    s = str(s)
    return s if (not s or "mm" in s or "°" in s) else s + " mm"


# ---------------- 尺寸 (页面 mm) ----------------
def hdim(pg, x0, x1, yg, yd, label, size=2.8):
    x0, x1 = min(x0, x1), max(x0, x1)
    sgn = 1 if yd > yg else -1
    for x in (x0, x1):
        pg.line(x, yg + sgn * 0.8, x, yd + sgn * 1.6, lw=0.15)
    if x1 - x0 >= 2 * ARR_L + 0.6:
        pg.line(x0, yd, x1, yd, lw=0.15)
        pg.arrow(x0, yd, -1, 0, L=ARR_L)
        pg.arrow(x1, yd, 1, 0, L=ARR_L)
    else:                                   # 窄: 外箭头指向里
        pg.line(x0 - ARR_L - 3, yd, x1 + ARR_L + 3, yd, lw=0.15)
        pg.arrow(x0, yd, 1, 0, L=ARR_L)
        pg.arrow(x1, yd, -1, 0, L=ARR_L)
    pg.text((x0 + x1) / 2, yd + 0.8, mm(label), size=size, ha="center", va="bottom", halo=True)


def vdim(pg, y0, y1, xg, xd, label, size=2.8):
    y0, y1 = min(y0, y1), max(y0, y1)
    sgn = 1 if xd > xg else -1
    for y in (y0, y1):
        pg.line(xg + sgn * 0.8, y, xd + sgn * 1.6, y, lw=0.15)
    if y1 - y0 >= 2 * ARR_L + 0.6:
        pg.line(xd, y0, xd, y1, lw=0.15)
        pg.arrow(xd, y0, 0, -1, L=ARR_L)
        pg.arrow(xd, y1, 0, 1, L=ARR_L)
    else:
        pg.line(xd, y0 - ARR_L - 3, xd, y1 + ARR_L + 3, lw=0.15)
        pg.arrow(xd, y0, 0, 1, L=ARR_L)
        pg.arrow(xd, y1, 0, -1, L=ARR_L)
    tx = xd + (1.2 if sgn > 0 else -1.2)
    pg.text(tx, (y0 + y1) / 2, mm(label), size=size, ha="left" if sgn > 0 else "right", va="center", halo=True)


def chain(pg, x, y0, y1, lw=0.15):          # 点划中心线
    pg.ax.plot([x[0], x[1]], [y0, y1], lw=lw * MM_PT, color="0.35", ls=(0, (8, 2, 1.5, 2)), zorder=2)


# ---------------- B-rep 剖切 ----------------
def section_polylines(shape, ang_deg, origin=(0.0, 0.0)):
    """过 origin 的竖直平面 (面内方向 = ang), 返回 [(u,w) ndarray], u = 沿 ang 距 origin, w = Z。"""
    a = math.radians(ang_deg)
    d = (math.cos(a), math.sin(a))
    n = gp_Dir(-d[1], d[0], 0)
    sec = BRepAlgoAPI_Section(shape, gp_Pln(gp_Pnt(origin[0], origin[1], 0), n))
    sec.Build()
    out = []
    e = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(e.Current()))
        g = GCPnts_QuasiUniformDeflection(c, 0.01)
        if g.IsDone() and g.NbPoints() >= 2:
            P = [g.Value(i) for i in range(1, g.NbPoints() + 1)]
            out.append(np.array([((p.X() - origin[0]) * d[0] + (p.Y() - origin[1]) * d[1], p.Z()) for p in P]))
        e.Next()
    return out


def clip(polys, u0, u1, w0, w1, step=0.05):
    """折线裁到窗口 (先加密再按点筛)。"""
    segs = []
    for P in polys:
        for a, b in zip(P[:-1], P[1:]):
            L = float(np.hypot(*(b - a)))
            k = max(1, int(L / step))
            t = np.linspace(0, 1, k + 1)[:, None]
            Q = a + t * (b - a)
            ins = (Q[:, 0] >= u0 - 1e-6) & (Q[:, 0] <= u1 + 1e-6) & (Q[:, 1] >= w0 - 1e-6) & (Q[:, 1] <= w1 + 1e-6)
            for i in range(k):
                if ins[i] and ins[i + 1]:
                    segs.append((Q[i], Q[i + 1]))
    return segs


def merge(segs):                             # 共线短段合并, 减小 PDF
    return segs


def pick_scale(sizes_avail, cap=5):
    for s, lab in SCALES:
        if s <= cap and all(sz * s <= av for sz, av in sizes_avail):
            return s, lab
    return SCALES[-1]


# ---------------- 主函数 ----------------
def draw(spec):
    """spec 键:
    code, title, subtitle, short, qty, material, orient, date, proj, stl, src, shape (B-rep), out
    phi: [d...]               俯视图上方 Φ 尺寸链
    sec: dict(ang, r1, zd=[(z0,z1,label?)...], rd=[(r, label?)...])   剖视 A-A
    holes: [dict(tag, pts, spec, where, det=None | dict(kind, d, D, h, side, z=(z0,z1), pt?, ang?, W?, title))]
    dets: 额外详图 (非孔特征) 同 det 格式 + tag
    notes: [str]
    """
    pg = Page()
    pg.rect(5, 5, PAGE_W - 5, PAGE_H - 5, lw=0.5)
    pg.text(PAGE_W / 2, PAGE_H - 13, f"POV3D {spec['proj']} — {spec['code']}  {spec['title']}", size=5.2, ha="center")
    if spec.get("subtitle"):
        pg.text(PAGE_W / 2, PAGE_H - 19, spec["subtitle"], size=2.7, ha="center")

    # ---- 俯视图 ----
    tris = read_stl(spec["stl"])
    part = Part(tris)
    e = part.extent("top")
    W, H = e[1] - e[0], e[3] - e[2]
    phis = sorted([(q, f"Φ{F(q)}") if not isinstance(q, tuple) else q for q in spec.get("phi", [])])
    TOP_BOX = (14, 44, 236, 268)                  # x0 y0 x1 y1
    dim_h = 9 * len(phis) + 6
    S, slab = pick_scale([(W, TOP_BOX[2] - TOP_BOX[0] - 30), (H, TOP_BOX[3] - TOP_BOX[1] - dim_h - 14)], cap=3)
    cx = (TOP_BOX[0] + TOP_BOX[2]) / 2
    cy = TOP_BOX[1] + 10 + (TOP_BOX[3] - TOP_BOX[1] - dim_h - 14) / 2
    ox, oy = cx - (e[0] + e[1]) / 2 * S, cy - (e[2] + e[3]) / 2 * S   # 世界 (0,0) 对应页面

    def T(x, y):
        return ox + x * S, oy + y * S
    vis, hid = part.view_lines("top")

    def tf(segs):
        a = np.asarray(segs, float).reshape(-1, 2, 2).copy()
        a[..., 0] = ox + a[..., 0] * S
        a[..., 1] = oy + a[..., 1] * S
        return a
    if hid:
        pg.ax.add_collection(LineCollection(tf(hid), colors="0.5", linewidths=0.16 * MM_PT, linestyles=(0, (2.2, 1.2)), zorder=2))
    if vis:
        pg.ax.add_collection(LineCollection(tf(vis), colors="k", linewidths=0.4 * MM_PT, capstyle="round", zorder=3))
    vy0, vy1 = oy + e[2] * S, oy + e[3] * S
    vx0, vx1 = ox + e[0] * S, ox + e[1] * S
    chain(pg, (vx0 - 6, vx1 + 6), oy, oy)
    chain(pg, (ox, ox), vy0 - 6, vy1 + 6)
    pg.text(cx, TOP_BOX[1] + 1, f"俯视图  Top View  ({slab})   尺寸单位: mm", size=3.6, ha="center")
    for i, d in enumerate(phis):
        yd = vy1 + 8 + 9 * i
        hdim(pg, ox - d[0] / 2 * S, ox + d[0] / 2 * S, vy1 + 1, yd, d[1])
    # 剖切线 A-A
    sec = spec["sec"]
    a = math.radians(sec["ang"])
    R = max(W, H) / 2 * S + 8
    ax_, ay_ = math.cos(a), math.sin(a)
    pg.ax.plot([ox, ox + ax_ * R], [oy, oy + ay_ * R], lw=0.35 * MM_PT, color="#c00000", ls=(0, (10, 2, 1.5, 2)), zorder=4)
    pg.arrow(ox + ax_ * R - ay_ * 5, oy + ay_ * R + ax_ * 5, -ay_, ax_, L=2.5)
    pg.text(ox + ax_ * (R + 4), oy + ay_ * (R + 4), "A", size=3.4, ha="center", va="center", halo=True)
    pg.text(ox - 4, oy - 4, "A", size=3.4, ha="center", va="center", halo=True)
    # 孔组字母
    for h in spec.get("holes", []):
        lo = h.get("lab_off", (2.4, 2.4))
        for (hx, hy) in h["pts"]:
            x, y = T(hx, hy)
            pg.line(x, y, x + lo[0] * 0.7, y + lo[1] * 0.7, lw=0.12, color="#c00000")
            pg.text(x + lo[0], y + lo[1], h["tag"], size=2.4, ha="center", va="center", halo=True)

    # ---- 剖视 A-A (半剖) ----
    shape = spec["shape"]
    polys = section_polylines(shape, sec["ang"])
    zs = np.concatenate([p[:, 1] for p in polys])
    us = np.concatenate([p[:, 0] for p in polys])
    r1 = sec.get("r1", float(us.max()))
    r0 = sec.get("r0", 0.0)
    z0, z1 = float(zs.min()), float(zs.max())
    dets = [dict(h["det"], tag=h["tag"]) for h in spec.get("holes", []) if h.get("det")] + spec.get("dets", [])
    SB = (244, 0, 412, 268)
    nz = len(sec.get("zd", []))
    nr = len(sec.get("rd", []))
    hmax = sec.get("hmax", 52 if dets else 120)
    s2, slab2 = pick_scale([(r1 - r0, SB[2] - SB[0] - 16 - 10 * nz), (z1 - z0, hmax)], cap=4)
    px0 = SB[0] + 10
    py0 = SB[3] - 14 - (z1 - z0) * s2
    sec_bot = py0 - 7 * nr - 6

    def T2(u, w):
        return px0 + (u - r0) * s2, py0 + (w - z0) * s2
    segs = clip(polys, r0, r1, z0 - 1, z1 + 1)
    if segs:
        a2 = np.array([[T2(*p), T2(*q)] for p, q in segs])
        pg.ax.add_collection(LineCollection(a2, colors="k", linewidths=0.42 * MM_PT, zorder=3))
    if r0 <= 0:
        chain(pg, (T2(0, 0)[0], T2(0, 0)[0]), py0 - 4, T2(0, z1)[1] + 4)
    pg.text((SB[0] + SB[2]) / 2, SB[3] - 2, f"剖视图  Section A-A  ({slab2})   尺寸单位: mm", size=3.6, ha="center")
    pg.text((SB[0] + SB[2]) / 2, SB[3] - 7, f"半剖: 轴线 → 外缘, 沿 {F(sec['ang'])}° 方向; Z = 装配高度", size=2.4, ha="center")
    xr = T2(r1, 0)[0]
    for i, zd in enumerate(sec.get("zd", [])):
        za, zb = zd[0], zd[1]
        lab = zd[2] if len(zd) > 2 else F(zb - za)
        vdim(pg, T2(0, za)[1], T2(0, zb)[1], xr + 1, xr + 6 + 10 * i, lab)
    for i, rd in enumerate(sec.get("rd", [])):
        ra, rb = rd[0], rd[1]
        lab = rd[2] if len(rd) > 2 else (f"R{F(rb)}" if ra == 0 else F(rb - ra))
        yb = py0 - 7 - 7 * i
        hdim(pg, T2(ra, z0)[0], T2(rb, z0)[0], py0, yb, lab, size=2.5)
    # Z 标签 (底/顶)
    pg.text(px0 - 1.5, py0, f"Z{F(z0)}", size=2.3, ha="right", va="center")
    pg.text(px0 - 1.5, T2(0, z1)[1], f"Z{F(z1)}", size=2.3, ha="right", va="center")

    # ---- 详图 ----
    ncol = 3
    nrow = math.ceil(len(dets) / ncol)
    ch = spec.get("det_h", 46.0)
    DB = (244, sec_bot - 2 - nrow * ch, 412, sec_bot - 2)
    cw = (DB[2] - DB[0]) / ncol
    for k, dt in enumerate(dets):
        col, row = k % ncol, k // ncol
        cx0 = DB[0] + col * cw
        cyt = DB[3] - row * ch
        pt = dt.get("pt") or (dt["pts0"] if "pts0" in dt else (0, 0))
        dang = dt.get("ang")
        if dang is None:
            dang = math.degrees(math.atan2(pt[1], pt[0])) if math.hypot(*pt) > 1e-6 else 0.0
        Wd = dt.get("W", max(dt.get("D", 0), dt.get("d", 0)) / 2 + 1.8)
        za, zb = dt["z"]
        sd, sl = pick_scale([(2 * Wd, cw - 22), (zb - za, ch - 26)], cap=5)
        polys = section_polylines(shape, dang, origin=pt)
        segs = clip(polys, -Wd, Wd, za - 0.01, zb + 0.01)
        dcx = cx0 + cw / 2
        dby = cyt - 15 - (zb - za) * sd

        def T3(u, w):
            return dcx + u * sd, dby + (w - za) * sd
        if segs:
            a3 = np.array([[T3(*p), T3(*q)] for p, q in segs])
            pg.ax.add_collection(LineCollection(a3, colors="k", linewidths=0.4 * MM_PT, zorder=3))
        chain(pg, (dcx, dcx), dby - 2, T3(0, zb)[1] + 2)
        pg.text(dcx, cyt - 3, f"详图 {dt['tag']}  ({sl})", size=3.0, ha="center")
        pg.text(dcx, cyt - 7, dt.get("title", ""), size=2.2, ha="center")
        kind = dt["kind"]
        ytop, ybot = T3(0, zb)[1], T3(0, za)[1]
        xr3 = T3(Wd, 0)[0]
        xl3 = T3(-Wd, 0)[0]
        if kind in ("cb", "ins"):
            d, D, h, side = dt["d"], dt["D"], dt["h"], dt["side"]
            yt = ytop if side == "bot" else ybot          # 通孔 Φ 标在对侧
            hdim(pg, T3(-d / 2, 0)[0], T3(d / 2, 0)[0], yt, yt + (4 if side == "bot" else -4) , f"Φ{F(d)}", size=2.3)
            yc = ybot if side == "bot" else ytop
            hdim(pg, T3(-D / 2, 0)[0], T3(D / 2, 0)[0], yc, yc + (-4 if side == "bot" else 4), f"Φ{F(D)}", size=2.3)
            zc0, zc1 = (za, za + h) if side == "bot" else (zb - h, zb)
            vdim(pg, T3(0, zc0)[1], T3(0, zc1)[1], T3(D / 2, 0)[0], xr3 + 3, F(h), size=2.3)
            vdim(pg, ybot, ytop, xl3, xl3 - 3, F(zb - za), size=2.3)
        elif kind == "blind":
            D, h, side = dt["D"], dt["h"], dt["side"]
            yc = ybot if side == "bot" else ytop
            hdim(pg, T3(-D / 2, 0)[0], T3(D / 2, 0)[0], yc, yc + (-4 if side == "bot" else 4), dt.get("Dlab", f"Φ{F(D)}"), size=2.3)
            zc0, zc1 = (za, za + h) if side == "bot" else (zb - h, zb)
            vdim(pg, T3(0, zc0)[1], T3(0, zc1)[1], T3(D / 2, 0)[0], xr3 + 3, F(h), size=2.3)
            vdim(pg, ybot, ytop, xl3, xl3 - 3, F(zb - za), size=2.3)
        elif kind == "free":
            for zd in dt.get("zd", []):
                vdim(pg, T3(0, zd[0])[1], T3(0, zd[1])[1], xr3, xr3 + 3 + zd[3] if len(zd) > 3 else xr3 + 3, zd[2], size=2.3)
            for ud in dt.get("ud", []):
                hdim(pg, T3(ud[0], 0)[0], T3(ud[1], 0)[0], ybot, ybot - 4 - (ud[3] if len(ud) > 3 else 0), ud[2], size=2.3)

    # ---- 孔表 + 说明 ----
    y = DB[1] - 3 if dets else sec_bot - 3
    x0t = 244
    pg.text(x0t, y, "孔组 (字母见俯视图; 有详图的字母 = 详图号)", size=3.0, weight="bold")
    y -= 4.6
    for h in spec.get("holes", []):
        pg.text(x0t, y, f"{h['tag']}  ×{len(h['pts'])}  {h['spec']}", size=2.5)
        y -= 3.5
        for ln in h.get("where", "").split("\n"):
            if ln:
                pg.text(x0t + 5, y, ln, size=2.2)
                y -= 3.1
    y -= 1.5
    pg.text(x0t, y, "说明", size=3.0, weight="bold")
    y -= 4.2
    for ln in spec.get("notes", []):
        pg.text(x0t, y, "· " + ln, size=2.3)
        y -= 3.3
    spec["_ylow"] = y
    if y < 36:
        print(f"  !! {spec['code']}: 孔表/说明 压到标题栏 (y={y:.1f})", flush=True)

    # ---- 标题栏 ----
    tb = (10, 10, PAGE_W - 10, 34)
    pg.rect(*tb, lw=0.35)
    pg.line(tb[0], 22, tb[2], 22, lw=0.2)
    for xx in (110, 180, 236, 276):
        pg.line(xx, tb[1], xx, tb[3], lw=0.2)
    pg.text(14, 26, spec["code"], size=4.4, weight="bold")
    pg.text(14, 14, spec["short"], size=2.9)
    pg.text(114, 26, f"数量: {spec['qty']}", size=2.9)
    pg.text(114, 14, f"材料: {spec.get('material', 'PLA')}", size=2.9)
    pg.text(184, 26, f"俯 {slab} / 剖 {slab2}", size=2.9)
    pg.text(184, 14, "单位 mm / 第一角", size=2.9)
    pg.text(240, 26, spec["date"], size=2.9)
    pg.text(240, 14, "POV3D " + spec["proj"], size=2.9)
    pg.text(280, 26, "打印姿态:", size=2.9)
    pg.text(280, 14, spec["orient"], size=2.6)
    pg.text(14, 6.5, f"STL: {spec['src']}   (俯视: 实线 = 可见, 灰虚线 = 不可见; 剖视/详图 = B-rep 精确剖切)", size=2.3)
    pg.text(14, 38, spec.get("origin_note", ""), size=2.4)
    png = pg.save(spec["out"])
    return spec["out"], png, f"{slab}/{slab2}"
