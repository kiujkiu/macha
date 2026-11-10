"""扇形配重块 counterweight_fan_v4 俯视孔位图 (按用户实装朝向: 打印面朝上, 同用户切片截图: B 在下, A 左, C 右)。
屏幕角 = 零件角 + 90° (纯旋转, 无镜像)。用法: python3 fan_map_top.py → fan_map_top.png"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Polygon, Circle
from matplotlib import font_manager as _fm
import os as _os
for _f in ("/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/simhei.ttf"):
    if _os.path.exists(_f):
        _fm.fontManager.addfont(_f); plt.rcParams["font.sans-serif"] = [_fm.FontProperties(fname=_f).get_name()]; break
plt.rcParams["axes.unicode_minus"] = False
ROT = 90.0
def P(r, a):
    t = math.radians(a + ROT); return r * math.cos(t), r * math.sin(t)
def PX(x, y):
    t = math.radians(ROT); return x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)
fig, ax = plt.subplots(figsize=(11, 7.5))
ax.add_patch(Wedge((0, 0), 85, 100 + ROT, 260 + ROT, width=27, fc="#d9d9d9", ec="#555"))
ax.add_patch(Polygon([PX(-85, -26), PX(-44, -26), PX(-44, 26), PX(-85, 26)], fc="#d9d9d9", ec="#555"))
M6 = [106, 116.6, 127.2, 137.8, 148.4, 159, 180, 201, 211.6, 222.2, 232.8, 243.4, 254]
for a in M6:
    ax.add_patch(Circle(P(78, a), 3.25, fc="white", ec="#555"))
ax.add_patch(Circle(PX(-64, 0), 3.25, fc="white", ec="#555"))
for x, y in [(-50, 14), (-50, -14), (-72, 14), (-72, -14)]:
    ax.add_patch(Circle(PX(x, y), 1.7, fc="#333", ec="#333"))
TRIM = [104 + 8 * i for i in range(9)] + [192 + 8 * i for i in range(9)]
for a in TRIM:
    ax.add_patch(Circle(P(64, a), 1.6, fc="white", ec="#555"))
# 外圈 A/B/C
for lab, a, c in [("A", 106, "#d62728"), ("B", 180, "#2ca02c"), ("C", 254, "#1f77b4")]:
    x, y = P(78, a); ax.add_patch(Circle((x, y), 5, fill=False, ec=c, lw=2.5))
    tx, ty = P(94, a); ax.text(tx, ty, lab, color=c, fontsize=18, fontweight="bold", ha="center", va="center")
# 内圈编号 (从 A 端数)
for i, a in enumerate(TRIM[:9]):
    x, y = P(55.5, a); ax.text(x, y, str(i + 1), fontsize=8, ha="center", va="center", color="#666")
for i, a in enumerate(TRIM[9:]):
    x, y = P(55.5, a); ax.text(x, y, str(9 - i), fontsize=8, ha="center", va="center", color="#666")
# 现装 M3
for a in (112, 120, 128):
    ax.add_patch(Circle(P(64, a), 3.2, fc="#2ca02c", ec="k", alpha=0.8))
for aa in (104, 240):
    ax.add_patch(Circle(P(64, aa), 3.2, fc="#2ca02c", ec="k", alpha=0.8))
x, y = P(64, 144); ax.add_patch(Circle((x, y), 4.2, fill=False, ec="#9467bd", lw=3))
ax.annotate("① 加 1.3 g (144°)\n内圈从 A 端数第 6 个", (x, y), (x - 60, y - 30), fontsize=12, color="#9467bd", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#9467bd", lw=2))
x, y = P(64, 216); ax.add_patch(Circle((x, y), 4.2, fill=False, ec="#8c564b", lw=3))
ax.annotate("② 挪到这 (216°)\n内圈从 C 端数第 6 个", (x, y), (x + 14, y - 30), fontsize=12, color="#8c564b", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#8c564b", lw=2))
x, y = P(64, 104); ax.annotate("③ 拆掉 ② 那颗,\n并拆掉这颗 (104°)", (x, y), (x - 30, y + 28), fontsize=12, color="#d62728", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#d62728", lw=2))
x, y = P(64, 120); ax.annotate("绿色 = 已装 M3 (别动, ③ 时只拆 104)", (x, y), (x - 40, y - 22), fontsize=10, color="#2ca02c", arrowprops=dict(arrowstyle="->", color="#2ca02c"))
ax.text(0, 8, "转轴中心", ha="center", fontsize=10, color="#666"); ax.plot(0, 0, "k+", ms=12)
ax.text(-95, -100, "俯视 (从上往下看, 按你装的朝向, 同你之前那张切片截图)\n灰小字 = 内圈小孔序号; 黑点 = 4 颗锁紧 M3", fontsize=10, color="#444")
ax.set_xlim(-100, 100); ax.set_ylim(-105, 15); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(); fig.savefig("fan_map_top_step3.png", dpi=110)
print("ok")
