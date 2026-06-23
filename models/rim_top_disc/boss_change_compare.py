"""
Comparison figure: rim_top_disc 6 boss-hole positions BEFORE (component side
down mapping, 2026-06-12 morning) vs AFTER (component side up correction).
Left: full top view. Right: per-hole zoom panels (the shifts are 0.1-0.2 mm).
Output: boss_change_compare.png
"""
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
fm.fontManager.addfont("/mnt/c/Windows/Fonts/simhei.ttf")
matplotlib.rcParams["font.family"] = "SimHei"
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

OLD = [(-5.0,  37.8), (5.0,  37.8), (-5.0, -38.0), (5.0, -38.0),
       (50.7,  37.5), (50.8, -37.4)]
NEW = [(-5.0,  38.0), (5.0,  38.0), (-5.0, -37.8), (5.0, -37.8),
       (50.8,  37.4), (50.7, -37.5)]   # paired by nearest physical location
LABELS = ["左上对·左", "左上对·右", "左下对·左", "左下对·右", "右上单", "右下单"]

fig = plt.figure(figsize=(16, 8))
fig.suptitle("rim_top_disc 凸台孔位改动对比 — 元件面朝上修正 (红=旧, 绿=新)",
             fontsize=14, fontfamily="SimHei")

# ---- left: full top view ----
ax = fig.add_subplot(1, 2, 1)
ax.add_patch(Circle((0, 0), 100, fill=False, lw=1.2, color="k"))
for ry in (47.5, -47.5):
    half = math.sqrt(100**2 - 50**2) - 0.5
    ax.add_patch(Rectangle((-half, ry - 2.5), 2*half, 5, fill=False,
                           lw=0.8, color="gray"))
for (x, y) in OLD:
    ax.add_patch(Circle((x, y), 5, fill=False, color="red", lw=1.0, ls="--"))
for (x, y) in NEW:
    ax.add_patch(Circle((x, y), 5, fill=False, color="green", lw=1.0))
    ax.add_patch(Circle((x, y), 1.6, fill=False, color="green", lw=0.7))
ax.set_xlim(-105, 105); ax.set_ylim(-105, 105)
ax.set_aspect("equal"); ax.grid(True, lw=0.3, alpha=0.4)
ax.set_title("整盘俯视 (Φ10 凸台轮廓)", fontfamily="SimHei")
ax.axhline(0, color="k", lw=0.4, ls=":"); ax.axvline(0, color="k", lw=0.4, ls=":")

# ---- right: 6 zoom panels ----
for i, ((ox, oy), (nx, ny), lab) in enumerate(zip(OLD, NEW, LABELS)):
    axz = fig.add_subplot(2, 6, 4 + i % 3 + (i // 3) * 6)
    cx, cy = (ox + nx) / 2, (oy + ny) / 2
    axz.plot(ox, oy, "x", color="red", ms=10, mew=2)
    axz.plot(nx, ny, "+", color="green", ms=12, mew=2)
    axz.add_patch(FancyArrowPatch((ox, oy), (nx, ny), color="blue",
                                  arrowstyle="-|>", mutation_scale=14, lw=1.2))
    dx, dy = nx - ox, ny - oy
    axz.set_title(f"{lab}\n({ox:g},{oy:g})→({nx:g},{ny:g})\n"
                  f"Δ=({dx:+.1f}, {dy:+.1f}) |{math.hypot(dx,dy):.2f}mm|",
                  fontsize=9, fontfamily="SimHei")
    W = 0.35
    axz.set_xlim(cx - W, cx + W); axz.set_ylim(cy - W, cy + W)
    axz.set_aspect("equal"); axz.grid(True, lw=0.3, alpha=0.5)
    axz.tick_params(labelsize=6)

fig.tight_layout(rect=(0, 0, 1, 0.95))
out = Path(__file__).with_name("boss_change_compare.png")
fig.savefig(out, dpi=110)
print(f"wrote {out}")
