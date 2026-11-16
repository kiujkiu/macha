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


# ---------------- 自动链式尺寸 (11-16: 剖视每段厚度 / 每个台阶半径) ----------------
def _tw(s, size):
    """文字宽 (页面 mm) 估算: ASCII 0.56·size, 其它 (中文/Φ/°) 1.0·size。"""
    return sum(0.56 * size if ord(c) < 128 else 1.0 * size for c in s)


def step_levels(polys, u0, u1, w0, w1, axis, tol=1e-3, min_len=0.4, merge_gap=0.3):
    """剖面轮廓里水平 (axis='w': 返回 Z 值) 或竖直 (axis='u': 返回 u 值) 直线段的位置 → [(值, 总长)]。
    只计窗口 [u0,u1]×[w0,w1] 内部分; 间隔 < merge_gap 的合并 (取长者)。"""
    acc = {}
    for P in polys:
        for a, b in zip(P[:-1], P[1:]):
            du, dw = b[0] - a[0], b[1] - a[1]
            if axis == "w":
                if abs(dw) > tol:
                    continue
                lo, hi = max(min(a[0], b[0]), u0), min(max(a[0], b[0]), u1)
                v = (a[1] + b[1]) / 2
                if not (w0 - 1e-6 <= v <= w1 + 1e-6):
                    continue
            else:
                if abs(du) > tol:
                    continue
                lo, hi = max(min(a[1], b[1]), w0), min(max(a[1], b[1]), w1)
                v = (a[0] + b[0]) / 2
                if not (u0 - 1e-6 <= v <= u1 + 1e-6):
                    continue
            if hi - lo > 1e-6:
                k = round(v, 3)
                acc[k] = acc.get(k, 0.0) + (hi - lo)
    lv = sorted((v, L) for v, L in acc.items() if L >= min_len)
    out = []
    for v, L in lv:
        if out and v - out[-1][0] < merge_gap:
            pv, pL = out[-1]
            out[-1] = (pv if pL >= L else v, pL + L)
        else:
            out.append((v, L))
    return out


def thin_levels(lv, ends, nmax=9):
    """层级太多时只留主要台阶: 两端必留, 其余按边长取前 nmax-2。"""
    vals = [v for v, _ in lv]
    keep = set()
    for e in ends:
        if e is None:
            continue
        keep.add(min(vals, key=lambda v: abs(v - e)) if vals and min(abs(v - e) for v in vals) < 0.3 else e)
    rest = sorted([(L, v) for v, L in lv if v not in keep], reverse=True)
    for L, v in rest[:max(0, nmax - len(keep))]:
        keep.add(v)
    out = []
    for v in sorted(keep):
        if out and v - out[-1] < 0.3:
            continue
        out.append(v)
    return out


def spread(pos, sizes, lo=None, hi=None):
    """一维去重叠: pos 期望中心, sizes 各自占宽; 返回新中心 (保序, 相邻间距 ≥ (s_i+s_j)/2), 整组尽量贴原位。"""
    n = len(pos)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: pos[i])
    p = [pos[i] for i in order]
    s = [sizes[i] for i in order]
    # 聚类合并法 (每簇居中于其成员期望位置均值)
    clusters = [[k] for k in range(n)]

    def place(c):
        need = [0.0]
        for a, b in zip(c[:-1], c[1:]):
            need.append(need[-1] + (s[a] + s[b]) / 2)
        off = sum(p[k] - need[j] for j, k in enumerate(c)) / len(c)
        return [off + d for d in need]
    pl = [place(c) for c in clusters]
    changed = True
    while changed:
        changed = False
        for i in range(len(clusters) - 1):
            a, b = clusters[i], clusters[i + 1]
            if pl[i][-1] + (s[a[-1]] + s[b[0]]) / 2 > pl[i + 1][0] + 1e-9:
                clusters[i] = a + b
                pl[i] = place(clusters[i])
                del clusters[i + 1], pl[i + 1]
                changed = True
                break
    flat = [x for q in pl for x in q]
    if lo is not None and flat[0] - s[0] / 2 < lo:
        d = lo - (flat[0] - s[0] / 2)
        flat = [x + d for x in flat]
    if hi is not None and flat[-1] + s[-1] / 2 > hi:
        d = (flat[-1] + s[-1] / 2) - hi
        flat = [x - d for x in flat]
    out = [0.0] * n
    for j, i in enumerate(order):
        out[i] = flat[j]
    return out


def _tick(pg, x, y, dx, dy, seg_page):
    if seg_page >= 2 * ARR_L + 0.6:
        pg.arrow(x, y, dx, dy, L=ARR_L)
    else:
        pg.arrow(x, y, dx, dy, L=min(ARR_L, max(1.2, seg_page * 0.45)), Wd=0.7)


def vchain(pg, ys, labels, xg, xd, size=2.3, skip=()):
    """竖向链式尺寸: ys 页面 y (升序), labels[i] 对应 ys[i]..ys[i+1]; 文字放尺寸线右侧, 挤时上下推开 + 引线。
    skip: 不画文字/箭头的段号 (与手写重复)。返回文字最右 x。"""
    for y in ys:
        pg.line(xg + 0.8, y, xd + 1.6, y, lw=0.15)
    pg.line(xd, ys[0], xd, ys[-1], lw=0.15)
    segs = [i for i in range(len(ys) - 1) if i not in skip]
    for i in segs:
        h = ys[i + 1] - ys[i]
        _tick(pg, xd, ys[i], 0, -1, h)
        _tick(pg, xd, ys[i + 1], 0, 1, h)
    th = size * 1.05
    want = [(ys[i] + ys[i + 1]) / 2 for i in segs]
    got = spread(want, [th] * len(segs))
    xmax = xd
    for k, i in enumerate(segs):
        lab = mm(labels[i])
        moved = abs(got[k] - want[k]) > 0.3
        tx = xd + (3.6 if moved else 1.2)
        if moved:
            pg.line(xd, want[k], xd + 1.0, want[k], lw=0.12)
            pg.line(xd + 1.0, want[k], tx - 0.3, got[k], lw=0.12)
        pg.text(tx, got[k], lab, size=size, ha="left", va="center", halo=True)
        xmax = max(xmax, tx + _tw(lab, size))
    return xmax


def hchain(pg, xs, labels, yg, yd, size=2.3, skip=(), dry=False):
    """横向链式尺寸 (尺寸线在 yg 下方 yd): 文字在尺寸线上方, 挤时左右推开 + 引线 (文字上抬一行)。"""
    segs = [i for i in range(len(xs) - 1) if i not in skip]
    if not dry:
        for x in xs:
            pg.line(x, yg - 0.8, x, yd - 1.6, lw=0.15)
        pg.line(xs[0], yd, xs[-1], yd, lw=0.15)
        for i in segs:
            w = xs[i + 1] - xs[i]
            _tick(pg, xs[i], yd, -1, 0, w)
            _tick(pg, xs[i + 1], yd, 1, 0, w)
    labs = [mm(labels[i]) for i in segs]
    want = [(xs[i] + xs[i + 1]) / 2 for i in segs]
    wid = [_tw(t, size) + 1.2 for t in labs]
    # 第 0 行 = 尺寸线上方 (放得下的段); 放不下的依次进下方 1..3 行 (引线连段中点); 再放不下的最后一行左右推开
    rows = {}
    place = {}
    leads = []                                   # (x0 在尺寸线, x1 在文字, 行)
    rowy = lambda r: yd - 1.4 - (r - 1) * (size + 0.9) - size * 0.5   # noqa: E731  第 r 行文字中线 y
    free = lambda r, a, b: all(b <= a2 or a >= b2 for a2, b2 in rows.get(r, []))   # noqa: E731

    def lead_x(x0, x1, r, q):                    # 引线 (尺寸线 x0 → 第 r 行 x1) 在第 q 行中线处的 x
        y_end = rowy(r) + size * 0.5
        t = (yd - rowy(q)) / max(1e-6, yd - y_end)
        return x0 + (x1 - x0) * min(1.0, t)
    for k in sorted(range(len(segs)), key=lambda k: -(xs[segs[k] + 1] - xs[segs[k]])):
        fits = wid[k] <= (xs[segs[k] + 1] - xs[segs[k]]) + 0.6
        w2 = wid[k] / 2
        near = (0.0, -w2 + 0.6, w2 - 0.6, w2 + 0.6, -w2 - 0.6)          # 文字仍贴着本段中点
        far = (wid[k] + 0.6, -wid[k] - 0.6)
        cands = ([(0, 0.0)] if fits else []) + [(r, dx) for r in (1, 2, 3, 4) for dx in near] + [(r, dx) for r in (1, 2, 3, 4) for dx in far]
        for r, dx in cands:
            done = False
            for _ in (0,):
                c = want[k] + dx
                a, b = c - wid[k] / 2, c + wid[k] / 2
                if not free(r, a, b):
                    continue
                if r >= 1 and any(not free(q, lead_x(want[k], c, r, q) - 0.4, lead_x(want[k], c, r, q) + 0.4) for q in range(1, r)):
                    continue                     # 本引线穿过上面行的文字
                if r >= 1 and any(lr > r and a - 0.4 < lead_x(l0, l1, lr, r) < b + 0.4 for l0, l1, lr in leads):
                    continue                     # 文字压到更深行的引线
                rows.setdefault(r, []).append((a, b))
                place[k] = (r, c)
                if r >= 1:
                    leads.append((want[k], c, r))
                done = True
                break
            if done:
                break
    rest = [k for k in range(len(segs)) if k not in place]
    if rest:
        got = spread([want[k] for k in rest], [wid[k] for k in rest])
        for k, g in zip(rest, got):
            place[k] = (5, g)
    for k, (r, x) in place.items():
        if dry:
            continue
        if r == 0:
            pg.text(x, yd + 0.8, labs[k], size=size, ha="center", va="bottom", halo=True)
        else:
            ty = yd - 1.4 - (r - 1) * (size + 0.9)
            pg.line(want[k], yd, x, ty + 0.1, lw=0.12)
            pg.text(x, ty, labs[k], size=size, ha="center", va="top", halo=True)
    return max([r for r, _ in place.values()] + [0])


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
    if e[2] - 1 <= 0 <= e[3] + 1:                 # 中心线只在轴心落在零件范围内时画 (偏心件不画, 免得穿进右侧说明区)
        chain(pg, (vx0 - 6, vx1 + 6), oy, oy)
    if e[0] - 1 <= 0 <= e[1] + 1:
        chain(pg, (ox, ox), vy0 - 6, vy1 + 6)
    pg.text(cx, TOP_BOX[1] + 1, f"俯视图  Top View  ({slab})   尺寸单位: mm", size=3.6, ha="center")
    for i, d in enumerate(phis):
        yd = vy1 + 8 + 9 * i
        hdim(pg, ox - d[0] / 2 * S, ox + d[0] / 2 * S, vy1 + 1, yd, d[1])
    # 剖切线 A-A
    sec = spec["sec"]
    a = math.radians(sec["ang"])
    ax_, ay_ = math.cos(a), math.sin(a)
    # 剖切线沿剖切方向覆盖零件投影 (偏心件如端部立板: 轴心在零件外, 线从零件近端前 6 mm 起, 不从页外的轴心画起)
    _pj = [x * ax_ + y * ay_ for x in e[:2] for y in e[2:]]
    R = (max(W, H) / 2 if abs(e[0] + e[1]) < 1e-3 * W and abs(e[2] + e[3]) < 1e-3 * H else max(_pj)) * S + 8
    Rs = max(0.0, min(_pj) * S - 6)
    pg.ax.plot([ox + ax_ * Rs, ox + ax_ * R], [oy + ay_ * Rs, oy + ay_ * R], lw=0.35 * MM_PT, color="#c00000", ls=(0, (10, 2, 1.5, 2)), zorder=4)
    pg.arrow(ox + ax_ * R - ay_ * 5, oy + ay_ * R + ax_ * 5, -ay_, ax_, L=2.5)
    pg.text(ox + ax_ * (R + 4), oy + ay_ * (R + 4), "A", size=3.4, ha="center", va="center", halo=True)
    pg.text(ox + ax_ * Rs - 4, oy + ay_ * Rs - 4, "A", size=3.4, ha="center", va="center", halo=True)
    # 孔组字母
    for h in spec.get("holes", []):
        lo = h.get("lab_off", (2.4, 2.4))
        for (hx, hy) in h["pts"]:
            x, y = T(hx, hy)
            pg.line(x, y, x + lo[0] * 0.7, y + lo[1] * 0.7, lw=0.12, color="#c00000")
            pg.text(x + lo[0], y + lo[1], h["tag"], size=2.4, ha="center", va="center", halo=True)

    # ---- 剖视 A-A (半剖) ----
    shape = spec["shape"]
    polys = section_polylines(shape, sec["ang"], sec.get("origin", (0.0, 0.0)))   # 11-16 晚: 偏心件剖切面可偏离转轴
    zs = np.concatenate([p[:, 1] for p in polys])
    us = np.concatenate([p[:, 0] for p in polys])
    r1 = sec.get("r1", float(us.max()))
    r0 = sec.get("r0", 0.0)
    z0, z1 = float(zs.min()), float(zs.max())
    dets = [dict(h["det"], tag=h["tag"]) for h in spec.get("holes", []) if h.get("det")] + spec.get("dets", [])
    SB = (244, 0, 412, 268)
    nz = len(sec.get("zd", []))
    nr = len(sec.get("rd", []))
    # 剖视可用高度: 页高 − 标题栏 − 下方 (径向尺寸行 + 详图 + 孔表/说明) 估算; 窄高件 (罩壁类) 因此能放大
    _txt = 4.6 + sum(3.5 + 3.1 * len([q for q in h.get("where", "").split("\n") if q]) for h in spec.get("holes", [])) \
        + 5.7 + 3.3 * len(spec.get("notes", []))
    _below = 7 * (nr + 1) + 6 + 12 + (math.ceil(len(dets) / 3) * spec.get("det_h", 46.0) + 5 if dets else 0) + _txt
    hmax = sec.get("hmax", min(120.0, max(52.0 if dets else 60.0, SB[3] - 14 - 40 - _below)))
    # 自动链式尺寸 (sec['auto_dims'] = False 关; 手写 zd/rd 优先, 重复段不画)
    auto = sec.get("auto_dims", True)
    nmax = sec.get("auto_nmax", 9)
    close = lambda a, b: abs(a - b) < 0.05   # noqa: E731
    zl, ul, zskip, uskip = [], [], set(), set()
    if auto and sec.get("auto_z", True):
        zl = thin_levels(step_levels(polys, r0, r1, z0, z1, "w"), (z0, z1), nmax)
        zl = sorted(set([z0] + [z for z in zl if z0 + 0.25 < z < z1 - 0.25] + [z1]))
        if len(zl) < 3:                      # 只有一段 = 总高, 交给"总高"一条
            zl = []
    if auto and sec.get("auto_r", True):      # auto_r=False: 只关径向链 (如多孔平板, 竖边全是孔壁)
        ul = thin_levels(step_levels(polys, r0, r1, z0, z1, "u"), (), nmax)
        if r0 <= 0 and ul and ul[0] > 0.25:
            ul = [0.0] + ul
        if len(ul) < 2:
            ul = []
    man_z = [(min(d[0], d[1]), max(d[0], d[1])) for d in sec.get("zd", [])]
    man_r = [(min(d[0], d[1]), max(d[0], d[1])) for d in sec.get("rd", [])]
    for i in range(len(zl) - 1):
        if any(close(zl[i], a) and close(zl[i + 1], b) for a, b in man_z):
            zskip.add(i)
    for i in range(len(ul) - 1):
        if any(close(ul[i], a) and close(ul[i + 1], b) for a, b in man_r):
            uskip.add(i)
    if zl and len(zskip) == len(zl) - 1:
        zl = []
    if ul and len(uskip) == len(ul) - 1:
        ul = []
    zlab = [F(b - a) for a, b in zip(zl[:-1], zl[1:])]
    rpre = "" if any(abs(c) > 1e-6 for c in sec.get("origin", (0.0, 0.0))) else "R"   # 偏心剖切面: u 不是半径
    ulab = [f"{rpre}{F(b)}" if abs(a) < 1e-9 else F(b - a) for a, b in zip(ul[:-1], ul[1:])]
    want_tot = auto and not any(close(a, z0) and close(b, z1) for a, b in man_z)
    W_a = max(10.0, 7.6 + max(_tw(mm(s), 2.3) for s in zlab)) + 1 if zl else 0.0
    W_tot = 10.0 if want_tot else 0.0
    # 手写 zd 列距按文字宽自适应 (长标签不再压到外一列尺寸线)
    zcol = [0.0]
    for zd in sec.get("zd", []):
        lab = zd[2] if len(zd) > 2 else F(zd[1] - zd[0])
        zcol.append(zcol[-1] + max(10.0, _tw(mm(lab), 2.8) + 3.0))
    s2, slab2 = pick_scale([(r1 - r0, SB[2] - SB[0] - 16 - zcol[-1] - W_a - W_tot), (z1 - z0, hmax)], cap=4)
    print(f"  auto {spec['code']}: Z链 {[F(z) for z in zl]}  径向链 {[F(u) for u in ul]}", flush=True)
    px0 = SB[0] + 10
    py0 = SB[3] - 14 - (z1 - z0) * s2

    def T2(u, w):
        return px0 + (u - r0) * s2, py0 + (w - z0) * s2
    nra = 1 if ul else 0
    hrows = hchain(None, [T2(u, z0)[0] for u in ul], ulab, py0, py0 - 7, skip=uskip, dry=True) if ul else 0
    hext = (hrows * 3.2 + 1.0) if hrows else 0.0          # 径向链下方引出文字占高
    sec_bot = py0 - 7 * (nr + nra) - 6 - hext
    segs = clip(polys, r0, r1, z0 - 1, z1 + 1)
    if segs:
        a2 = np.array([[T2(*p), T2(*q)] for p, q in segs])
        pg.ax.add_collection(LineCollection(a2, colors="k", linewidths=0.42 * MM_PT, zorder=3))
    if r0 <= 0:
        chain(pg, (T2(0, 0)[0], T2(0, 0)[0]), py0 - 4, T2(0, z1)[1] + 4)
    pg.text((SB[0] + SB[2]) / 2, SB[3] - 2, f"剖视图  Section A-A  ({slab2})   尺寸单位: mm", size=3.6, ha="center")
    pg.text((SB[0] + SB[2]) / 2, SB[3] - 7, f"半剖: 轴线 → 外缘, 沿 {F(sec['ang'])}° 方向; Z = 装配高度", size=2.4, ha="center")
    xr = T2(r1, 0)[0]
    xcol = xr + 6
    if zl:                                    # 自动竖向链: 紧贴剖视, 每段厚度
        xm = vchain(pg, [T2(0, z)[1] for z in zl], zlab, xr + 1, xcol, skip=zskip)
        xcol = max(xcol + 10, xm + 4)
    for i, zd in enumerate(sec.get("zd", [])):
        za, zb = zd[0], zd[1]
        lab = zd[2] if len(zd) > 2 else F(zb - za)
        vdim(pg, T2(0, za)[1], T2(0, zb)[1], xr + 1, xcol + zcol[i], lab)
    if want_tot:                              # 总高: 最外侧
        vdim(pg, T2(0, z0)[1], T2(0, z1)[1], xr + 1, xcol + zcol[nz], F(z1 - z0))
    if ul:                                    # 自动径向链: 紧贴剖视下方
        hchain(pg, [T2(u, z0)[0] for u in ul], ulab, py0, py0 - 7, skip=uskip)
        if ul[0] > 1e-9:                      # 链起点的绝对半径 (第一条界线左侧, 尺寸线上方)
            pg.text(T2(ul[0], z0)[0] - 1.0, py0 - 6.2, (f"R{F(ul[0])}" if rpre else f"起 {F(ul[0])}"), size=2.3, ha="right", va="bottom", halo=True)
    for i, rd in enumerate(sec.get("rd", [])):
        ra, rb = rd[0], rd[1]
        lab = rd[2] if len(rd) > 2 else (f"R{F(rb)}" if ra == 0 else F(rb - ra))
        yb = py0 - 7 - 7 * (i + nra) - hext
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
