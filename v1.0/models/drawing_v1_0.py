"""
V1.0 打印件通用 A3 工程图 (2026-10-20)。直接从 STL 出图, 与 build_stl.py 的几何天然一致:

  · 三视图 (GB 第一角: 主视 X-Z 左上 / 左视 置右 / 俯视 置下), 共用一个标准比例
    —— 特征棱 (二面角 > 30°) + 各视图轮廓线; z-buffer 判可见: 实线 = 可见, 细虚线 = 隐藏
  · 外形总尺寸 (主视 宽/高, 左视 深, 俯视 深)
  · 孔组: 在指定视图里按孔心标字母, 右栏孔表 (字母 / 数量 / 规格 / 位置)
  · 右上轴测着色小图, 右栏注意事项, 底部标题栏 (数量 / 材料 / 打印姿态 / 比例 / 单位 mm)

用法: draw(spec) —— spec 见 build_drawings_v1_0.py。
"""
import logging
import math
import struct
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                  # noqa: E402
from matplotlib import font_manager                              # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # SimHei 无粗体
FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["axes.unicode_minus"] = False

PAGE_W, PAGE_H = 420.0, 297.0
MM_PT = 72 / 25.4
SCALES = [(5, "5:1"), (4, "4:1"), (2.5, "2.5:1"), (2, "2:1"), (1.5, "1.5:1"), (1, "1:1"),
          (2 / 3, "1:1.5"), (0.5, "1:2"), (0.4, "1:2.5")]
VIEW_AREA = (18.0, 45.0, 290.0, 286.0)       # x0 y0 x1 y1 (页面 mm, y 向上)
DIM_SP = 16.0                                 # 视图外留给尺寸的宽度
GAP = 10.0

# 视图: (水平轴, 竖直轴, 观察方向 = 指向观察者)
VIEWS = {
    "front": (np.array([1., 0, 0]), np.array([0, 0, 1.]), np.array([0, -1., 0])),
    "left": (np.array([0, -1., 0]), np.array([0, 0, 1.]), np.array([-1., 0, 0])),
    "top": (np.array([1., 0, 0]), np.array([0, 1., 0]), np.array([0, 0, 1.])),
}
VIEW_NAME = {"front": "主视图", "left": "左视图", "top": "俯视图"}


def read_stl(path):
    raw = Path(path).read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(raw, dt, n, 84)["v"].astype(np.float64)


def _edges(tris, feat_deg=30.0):
    """返回 (边端点 [m,2,3], 两侧法向 n1/n2 [m,3], has2, feature)。
    退化 (零面积, 三点共线) 三角形的法向不可信: 取它两条短边对面的正常三角形法向 —— 共线三点的长边
    对面那侧, 实际几何就是短边外侧的面 (manifold 输出里常见, 不处理会在平面上画出假斜线)。"""
    v = tris.reshape(-1, 3)
    q = np.round(v / 1e-4).astype(np.int64)
    _, vid = np.unique(q, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    a2 = np.linalg.norm(n, axis=1)
    ok = a2 > 1e-6 * max(1.0, float(np.median(a2)))
    n = n / (a2[:, None] + 1e-30)
    adj = {}
    for t in range(len(vid)):
        a, b, c = vid[t]
        for e in ((a, b), (b, c), (c, a)):
            if e[0] != e[1]:                           # 重复顶点 → 零长边, 不算邻接
                adj.setdefault((min(e), max(e)), []).append(t)
    for _ in range(4):                                 # 退化三角形链: 迭代几轮
        bad = np.where(~ok)[0]
        if not len(bad):
            break
        for t in bad:
            P = tris[t]
            el = [np.linalg.norm(P[(k + 1) % 3] - P[k]) for k in range(3)]
            kl = int(np.argmax(el))
            for k in range(3):
                if k == kl:
                    continue
                e = (vid[t][k], vid[t][(k + 1) % 3])
                if e[0] == e[1]:
                    continue
                nb = [u for u in adj[(min(e), max(e))] if u != t and ok[u]]
                if nb:
                    n[t] = n[nb[0]]
                    ok[t] = True
                    break
    pts, n1, n2, has2, feature = [], [], [], [], []
    cth = math.cos(math.radians(feat_deg))
    for (a, b), ts in adj.items():
        t0 = ts[0]
        ia, ib = list(vid[t0]).index(a), list(vid[t0]).index(b)
        pts.append((tris[t0][ia], tris[t0][ib]))
        good = [u for u in ts if ok[u]]
        if len(good) >= 2:
            na, nb = n[good[0]], n[good[1]]
            cmin = min(float(n[x] @ n[y]) for x in good for y in good)
            n1.append(na), n2.append(nb), has2.append(True), feature.append(cmin < cth)
        else:
            nn = n[good[0]] if good else np.zeros(3)
            n1.append(nn), n2.append(np.zeros(3)), has2.append(False), feature.append(len(ts) < 2)
    return (np.asarray(pts), np.asarray(n1), np.asarray(n2), np.asarray(has2), np.asarray(feature))


class Part:
    def __init__(self, tris):
        self.tris = tris
        self.pts, self.n1, self.n2, self.has2, self.feature = _edges(tris)
        self.lo, self.hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)

    def view_lines(self, view):
        u, w, d = VIEWS[view]
        s1, s2 = self.n1 @ d, self.n2 @ d
        eps = 1e-3                                   # 面法向 ⟂ 视线 (n·d≈0) 的抖动不算轮廓
        sil = self.has2 & (((s1 > eps) & (s2 < -eps)) | ((s1 < -eps) & (s2 > eps)))
        sel = self.feature | sil
        P = self.pts[sel]
        T = self.tris
        tu, tw, td = T @ u, T @ w, T @ d
        ext = max(tu.max() - tu.min(), tw.max() - tw.min())
        res = max(ext / 1400.0, 0.04)
        u0, w0 = tu.min() - 2 * res, tw.min() - 2 * res
        W = int((tu.max() - u0) / res) + 3
        H = int((tw.max() - w0) / res) + 3
        zb = np.full((H, W), -np.inf)
        U, Wv = (tu - u0) / res, (tw - w0) / res
        for i in range(len(T)):
            xs, ys, zs = U[i], Wv[i], td[i]
            x0, x1 = int(math.floor(xs.min())), int(math.ceil(xs.max()))
            y0, y1 = int(math.floor(ys.min())), int(math.ceil(ys.max()))
            den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.0, np.arange(y0, y1 + 1) + 0.0)
            a = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
            b = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
            c = 1 - a - b
            m = (a >= -1e-3) & (b >= -1e-3) & (c >= -1e-3)
            if not m.any():
                continue
            z = a * zs[0] + b * zs[1] + c * zs[2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            np.maximum(sub, np.where(m, z, -np.inf), out=sub)
        # 边采样判可见
        vis, hid = [], []
        tol = 0.15 + 2 * res
        for p0, p1 in P:
            L = np.linalg.norm(p1 - p0)
            k = max(2, int(L / (res * 1.5)) + 1)
            t = np.linspace(0, 1, k)
            q = p0[None] + t[:, None] * (p1 - p0)[None]
            qu, qw, qd = q @ u, q @ w, q @ d
            ix = np.clip(np.round((qu - u0) / res).astype(int), 0, W - 1)
            iy = np.clip(np.round((qw - w0) / res).astype(int), 0, H - 1)
            # 3×3 邻域取最小 —— 边落在面交界, 用邻域里最远的面判断, 免得被自己所在的面挡
            zz = np.full(k, np.inf)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    zz = np.minimum(zz, zb[np.clip(iy + dy, 0, H - 1), np.clip(ix + dx, 0, W - 1)])
            v = qd >= zz - tol
            # 连续段
            start = 0
            for j in range(1, k + 1):
                if j == k or v[j] != v[start]:
                    seg = [(qu[start], qw[start]), (qu[min(j, k - 1)], qw[min(j, k - 1)])]
                    (vis if v[start] else hid).append(seg)
                    start = j
        return vis, hid

    def extent(self, view):
        u, w, _ = VIEWS[view]
        V = self.tris.reshape(-1, 3)
        return (V @ u).min(), (V @ u).max(), (V @ w).min(), (V @ w).max()


# ---------------- 页面绘制工具 (页面 mm 坐标) ----------------
class Page:
    def __init__(self):
        self.fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, PAGE_W)
        self.ax.set_ylim(0, PAGE_H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def text(self, x, y, s, size=3.2, ha="left", va="baseline", rot=0, halo=False, weight="normal"):
        s = s.replace("⚠", "注意:").replace("−", "-")          # SimHei 没这两个字形
        t = self.ax.text(x, y, s, fontsize=size * MM_PT, ha=ha, va=va, rotation=rot, weight=weight, zorder=5)
        if halo:
            t.set_bbox(dict(facecolor="white", edgecolor="none", pad=0.6))
        return t

    def line(self, x0, y0, x1, y1, lw=0.2, ls="-", color="k", z=3):
        self.ax.plot([x0, x1], [y0, y1], lw=lw * MM_PT, ls=ls, color=color, zorder=z, solid_capstyle="butt")

    def rect(self, x0, y0, x1, y1, lw=0.3):
        for a in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
            self.line(*a, lw=lw)

    def arrow(self, x, y, dx, dy, L=3.0, Wd=0.9):
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        bx, by = x - L * ux, y - L * uy
        self.ax.fill([x, bx - Wd * uy, bx + Wd * uy], [y, by + Wd * ux, by - Wd * ux], color="k", zorder=4, lw=0)

    def hdim(self, x0, x1, yg, yd, label):
        sgn = 1 if yd > yg else -1
        for x in (x0, x1):
            self.line(x, yg + sgn * 1.0, x, yd + sgn * 1.8, lw=0.15)
        self.line(x0, yd, x1, yd, lw=0.15)
        self.arrow(x0, yd, -1, 0)
        self.arrow(x1, yd, 1, 0)
        self.text((x0 + x1) / 2, yd + 0.9, label, size=3.0, ha="center", va="bottom", halo=True)

    def vdim(self, y0, y1, xg, xd, label):
        sgn = 1 if xd > xg else -1
        for y in (y0, y1):
            self.line(xg + sgn * 1.0, y, xd + sgn * 1.8, y, lw=0.15)
        self.line(xd, y0, xd, y1, lw=0.15)
        self.arrow(xd, y0, 0, -1)
        self.arrow(xd, y1, 0, 1)
        self.text(xd - 0.9, (y0 + y1) / 2, label, size=3.0, ha="right" if sgn < 0 else "left",
                  va="center", rot=90, halo=True)

    def save(self, path):
        self.fig.savefig(path)
        png = Path(path).with_name(Path(path).stem + "_preview.png")
        self.fig.savefig(png, dpi=110)
        plt.close(self.fig)
        return png


def _fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _iso(pg, part, box):
    """右上轴测着色图 (画家算法)。"""
    x0, y0, x1, y1 = box
    T = part.tris
    az, el = math.radians(-50), math.radians(28)
    R1 = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    R2 = np.array([[1, 0, 0], [0, math.cos(el), -math.sin(el)], [0, math.sin(el), math.cos(el)]])
    P = T @ (R2 @ R1).T                       # 视线 = -Y'
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    front = n[:, 1] < 0
    P, n = P[front], n[front]
    order = np.argsort(-P[:, :, 1].mean(1))   # 远 (y 大) 先画
    P, n = P[order], n[order]
    L = np.array([-0.4, -0.75, 0.55]); L /= np.linalg.norm(L)
    sh = np.clip(0.35 + 0.65 * np.abs(n @ L), 0, 1)
    xy = P[:, :, [0, 2]]
    lo, hi = xy.reshape(-1, 2).min(0), xy.reshape(-1, 2).max(0)
    s = min((x1 - x0) / (hi[0] - lo[0]), (y1 - y0) / (hi[1] - lo[1])) * 0.92
    c = (np.array([x0 + x1, y0 + y1]) / 2) - (lo + hi) / 2 * s
    xy = xy * s + c
    col = np.stack([0.95 * sh, 0.62 * sh, 0.25 * sh], 1)
    pg.ax.add_collection(PolyCollection(xy, facecolors=col, edgecolors=col, linewidths=0.35, antialiaseds=False, zorder=2))


def draw(spec):
    """spec: dict(stl, out, title, code, qty, material, orient, notes[list], holes[list], date, src,
    poses: 可选 3×3 旋转 (图纸姿态), origin: 'bbox' | 'zero', origin_note)。"""
    tris = read_stl(spec["stl"])
    if spec.get("rot") is not None:
        tris = tris @ np.asarray(spec["rot"], float).T
    if spec.get("origin", "zero") == "bbox":
        tris = tris - tris.reshape(-1, 3).min(0)
    part = Part(tris)
    ex = {v: part.extent(v) for v in VIEWS}
    Wx = ex["front"][1] - ex["front"][0]
    Hz = ex["front"][3] - ex["front"][2]
    Dy = ex["top"][3] - ex["top"][2]
    views = spec.get("views", ("front", "left", "top"))
    Wl = Dy if "left" in views else 0.0
    ax0, ay0, ax1, ay1 = VIEW_AREA
    availW = ax1 - ax0 - 2 * DIM_SP - (GAP if Wl else 0)
    availH = ay1 - ay0 - 2 * DIM_SP - GAP - 8
    scale, slabel = SCALES[-1]
    for s, lab in SCALES:
        if (Wx + Wl) * s <= availW and (Hz + Dy) * s <= availH:
            scale, slabel = s, lab
            break
    S = scale
    # 视图原点 (页面 mm): 主视左上, 左视在右, 俯视在下
    fx0 = ax0 + DIM_SP + (availW - (Wx + Wl) * S) / 2
    ty0 = ay0 + DIM_SP / 2 + (availH - (Hz + Dy) * S) / 2
    fy0 = ty0 + Dy * S + GAP + 8
    lx0 = fx0 + Wx * S + GAP
    place = {"front": (fx0, fy0), "left": (lx0, fy0), "top": (fx0, ty0)}

    def to_page(view, uu, ww):
        e = ex[view]
        px, py = place[view]
        return px + (uu - e[0]) * S, py + (ww - e[2]) * S

    pg = Page()
    pg.rect(5, 5, PAGE_W - 5, PAGE_H - 5, lw=0.5)
    pg.text(PAGE_W / 2, PAGE_H - 13, f"POV3D {spec.get('proj', 'V1.0')} — {spec['code']}  {spec['title']}", size=5.5, ha="center")
    if spec.get("subtitle"):
        pg.text(PAGE_W / 2, PAGE_H - 19, spec["subtitle"], size=3.0, ha="center")

    for view in views:
        vis, hid = part.view_lines(view)
        e = ex[view]
        px, py = place[view]

        def tf(segs):
            a = np.asarray(segs, float).reshape(-1, 2, 2)
            a[..., 0] = px + (a[..., 0] - e[0]) * S
            a[..., 1] = py + (a[..., 1] - e[2]) * S
            return a
        if hid:
            pg.ax.add_collection(LineCollection(tf(hid), colors="0.45", linewidths=0.18 * MM_PT,
                                                linestyles=(0, (2.2, 1.2)), zorder=2))
        if vis:
            pg.ax.add_collection(LineCollection(tf(vis), colors="k", linewidths=0.42 * MM_PT,
                                                capstyle="round", zorder=3))
        w_, h_ = (e[1] - e[0]) * S, (e[3] - e[2]) * S
        pg.text(px + w_ / 2, py - 6.5, f"{VIEW_NAME[view]}", size=3.6, ha="center")     # 视图名放视图正下方
        if view == "front":
            pg.hdim(px, px + w_, py + h_, py + h_ + 8, f"{_fmt(e[1] - e[0])}")
            pg.vdim(py, py + h_, px, px - 8, f"{_fmt(e[3] - e[2])}")
        elif view == "left":
            pg.hdim(px, px + w_, py + h_, py + h_ + 8, f"{_fmt(e[1] - e[0])}")
        else:
            pg.vdim(py, py + h_, px, px - 8, f"{_fmt(e[3] - e[2])}")
            if "left" not in views:
                pg.vdim(py, py + h_, px + w_, px + w_ + 8, "")
                pg.text(px + w_ + 9, py + h_ / 2, f"Y {_fmt(e[3] - e[2])}", size=3.0, va="center", rot=90, halo=True)
        for dmn in spec.get("dims", []):
            if dmn["view"] != view:
                continue
            (u0, w0), (u1, w1) = dmn["p0"], dmn["p1"]
            a0, b0 = to_page(view, u0, w0)
            a1, b1 = to_page(view, u1, w1)
            off = dmn.get("off", 8)
            if dmn["kind"] == "h":
                yb = (py + h_ if off > 0 else py)
                pg.hdim(a0, a1, max(b0, b1) if off > 0 else min(b0, b1), yb + off, dmn["label"])
            else:
                xb = (px + w_ if off > 0 else px)
                pg.vdim(b0, b1, max(a0, a1) if off > 0 else min(a0, a1), xb + off, dmn["label"])

    # 孔组字母
    for h in spec.get("holes", []):
        view = h.get("view", "top")
        for (hu, hw) in h["pts"]:
            x, y = to_page(view, hu, hw)
            ox, oy = h.get("lab_off", (2.2, 2.2))
            pg.line(x, y, x + ox * 0.75, y + oy * 0.75, lw=0.12, color="#c00000")
            pg.text(x + ox, y + oy, h["tag"], size=2.6, ha="center", va="center", halo=True)
    # 右栏: 轴测 + 孔表 + 注意
    rx0, rx1 = 296.0, PAGE_W - 10
    pg.rect(rx0, 196, rx1, PAGE_H - 24, lw=0.2)
    pg.text(rx0 + 2, PAGE_H - 28, "轴测 (示意, 非比例)", size=2.8)
    _iso(pg, part, (rx0 + 3, 199, rx1 - 3, PAGE_H - 30))
    y = 190.0
    if spec.get("holes"):
        pg.text(rx0, y, "孔表 (坐标 = 图示姿态, 见下方原点说明)", size=3.2, weight="bold")
        y -= 5.5
        for h in spec["holes"]:
            pg.text(rx0, y, f"{h['tag']}", size=3.0, weight="bold")
            pg.text(rx0 + 6, y, f"×{len(h['pts'])}  {h['spec']}", size=2.8)
            y -= 4.2
            for ln in h.get("where", "").split("\n"):
                if ln:
                    pg.text(rx0 + 6, y, ln, size=2.4)
                    y -= 3.6
            y -= 1.0
    y -= 2
    pg.text(rx0, y, "说明", size=3.2, weight="bold")
    y -= 5.0
    for ln in spec.get("notes", []):
        pg.text(rx0, y, "· " + ln, size=2.5)
        y -= 3.9
    # 原点说明 (视图区左下)
    pg.text(ax0, ay0 - 3, spec.get("origin_note", "") + f"   图示外形: X {_fmt(Wx)} × Y {_fmt(Dy)} × Z {_fmt(Hz)}",
            size=2.6)
    # 标题栏
    tb = (10, 10, PAGE_W - 10, 38)
    pg.rect(*tb, lw=0.35)
    pg.line(tb[0], 24, tb[2], 24, lw=0.2)
    for xx in (110, 180, 228, 268):
        pg.line(xx, tb[1], xx, tb[3], lw=0.2)
    pg.text(14, 29, f"{spec['code']}", size=4.6, weight="bold")
    pg.text(14, 15.5, spec["short"], size=3.0)
    pg.text(114, 29, f"数量: {spec['qty']}", size=3.0)
    pg.text(114, 15.5, f"材料: {spec.get('material', 'PLA')}", size=3.0)
    pg.text(184, 29, f"比例 {slabel}", size=3.4)
    pg.text(184, 15.5, "单位 mm / 第一角", size=3.0)
    pg.text(232, 29, spec.get("date", "2026-10-20"), size=3.0)
    pg.text(232, 15.5, "POV3D " + spec.get("proj", "V1.0"), size=3.0)
    pg.text(272, 29, "打印姿态:", size=3.0)
    pg.text(272, 15.5, spec["orient"], size=2.8)
    pg.text(14, 6.5, f"STL: {spec['src']}   (线: 实线 = 可见棱/轮廓, 灰虚线 = 不可见)", size=2.4)
    png = pg.save(spec["out"])
    return spec["out"], png, slabel
