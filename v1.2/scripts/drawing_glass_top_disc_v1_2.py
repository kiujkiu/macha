"""
玻璃上 圆环透明玻璃 (外购件) 2D 询价图 + DXF (2026-11-13 用户: 外径 180 / 内径 20 / 厚 10)
    cd v1.2/scripts && ../../.venv/bin/python drawing_glass_top_disc_v1_2.py
输出 v1.2/models/glass_top_disc_v1_2/
    glass_top_disc_v1_2_drawing.pdf / _drawing.png  (A3 横, 1:1 主视 + 剖视 A-A + 技术要求)
    glass_top_disc_v1_2.dxf                         (1:1 外形, 给切割/水刀)
"""
from pathlib import Path

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

OD, ID, T = 180.0, 20.0, 10.0
CH = 0.5                                    # 边缘倒角 C0.5 (内外圈上下四条棱)
OUT = Path(__file__).resolve().parents[1] / "models" / "glass_top_disc_v1_2"
OUT.mkdir(parents=True, exist_ok=True)
NAME = "glass_top_disc_v1_2"

for f in ("/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/simhei.ttf"):
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

# ---------------- DXF ----------------
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.MM
msp = doc.modelspace()
msp.add_circle((0, 0), OD / 2)
msp.add_circle((0, 0), ID / 2)
doc.saveas(OUT / f"{NAME}.dxf")

# ---------------- 图纸 (A4 横 297x210, 1:1) ----------------
W, H = 420.0, 297.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off")
LW, THIN = 0.7, 0.3
ax.add_patch(Rectangle((10, 10), W - 20, H - 20, fill=False, lw=LW))


def dim_h(x0, x1, y, txt, ext_from=None):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 1.2, txt, ha="center", va="bottom", fontsize=8)
    if ext_from is not None:
        for x in (x0, x1):
            ax.plot([x, x], [ext_from, y - 1 if y < ext_from else y + 1], lw=THIN, color="k")


# 主视 (俯视), 圆心 (100, 105)
cx, cy = 130.0, 160.0
ax.add_patch(Circle((cx, cy), OD / 2, fill=False, lw=LW))
ax.add_patch(Circle((cx, cy), ID / 2, fill=False, lw=LW))
for dx, dy in ((1, 0), (0, 1)):
    ax.plot([cx - dx * (OD / 2 + 5), cx + dx * (OD / 2 + 5)], [cy - dy * (OD / 2 + 5), cy + dy * (OD / 2 + 5)],
            lw=THIN, color="k", ls=(0, (12, 3, 2, 3)))
# 直径标注 (斜线引出)
import math  # noqa: E402
a = math.radians(40)
ax.annotate("", (cx + OD / 2 * math.cos(a), cy + OD / 2 * math.sin(a)), (cx - OD / 2 * math.cos(a), cy - OD / 2 * math.sin(a)),
            arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
ax.text(cx + 52, cy + 52, f"Ø{OD:g} ±0.2", fontsize=9, rotation=40, ha="center", va="bottom")
b = math.radians(-35)
ax.annotate("", (cx + ID / 2 * math.cos(b), cy + ID / 2 * math.sin(b)), (cx - ID / 2 * math.cos(b), cy - ID / 2 * math.sin(b)),
            arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
ax.annotate(f"Ø{ID:g} +0.2/0 (通孔, 同心度 ≤ 0.2)", (cx + ID / 2 * math.cos(b), cy + ID / 2 * math.sin(b)), (cx + 28, cy - 40),
            fontsize=8, arrowprops=dict(arrowstyle="-", lw=THIN))
ax.plot([cx - OD / 2 - 3, cx + OD / 2 + 3], [cy, cy], lw=0)  # 占位
for xx in (cx - OD / 2 - 8, cx + OD / 2 + 4):
    ax.text(xx, cy + 3, "A", fontsize=11)
    ax.plot([xx + 1, xx + 5], [cy, cy], lw=1.2, color="k")
ax.text(cx, cy - OD / 2 - 6, "主视图 1:1", ha="center", fontsize=9)

# 剖视 A-A (沿直径), 放右侧竖放: 厚度方向 x, 直径方向 y; 比例 1:1, 中心 (225, 105)
sx, sy = 285.0, 160.0
for y0, y1 in ((-OD / 2, -ID / 2), (ID / 2, OD / 2)):
    ax.add_patch(Rectangle((sx - T / 2, sy + y0), T, y1 - y0, fill=True, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
ax.plot([sx, sx], [sy - OD / 2 - 4, sy + OD / 2 + 4], lw=THIN, color="k", ls=(0, (12, 3, 2, 3)))
ax.plot([sx - T / 2 - 4, sx + T / 2 + 4], [sy, sy], lw=THIN, color="k", ls=(0, (12, 3, 2, 3)))
dim_h(sx - T / 2, sx + T / 2, sy + OD / 2 + 4, f"{T:g} ±0.3")
ax.text(sx, sy - OD / 2 - 6, "剖视 A-A 1:1", ha="center", fontsize=9)
ax.annotate(f"四周棱边 C{CH:g}\n(内外圈上下共 4 条)", (sx + T / 2, sy + OD / 2), (sx + 14, sy + OD / 2 - 18), fontsize=7.5,
            arrowprops=dict(arrowstyle="-", lw=THIN))

# 技术要求 + 标题栏
req = [
    "技术要求:",
    "1. 材质: 透明玻璃, 优先 超白钢化玻璃",
    "   (备选 高硼硅 / 光学亚克力, 请分别报价);",
    "   透光率 ≥ 90 %, 无气泡、划痕、崩边。",
    f"2. 外径 Ø{OD:g} ±0.2, 内孔 Ø{ID:g} +0.2/0, 内外圆同心度 ≤ 0.2。",
    f"3. 厚度 {T:g} ±0.3, 平面度 ≤ 0.3; 上下两面抛光 (透明)。",
    f"4. 内外圆周边 磨边 + 倒角 C{CH:g}, 无锐边。",
    "5. 若钢化: 先开孔、磨边后再钢化。",
    "6. 未注公差 ±0.3。数量: 询价按 2 / 10 / 50 件分别报价。",
]
ax.text(310, 120, "\n".join(req), fontsize=8, va="top", linespacing=1.5)
tb_x, tb_y = 270, 12
ax.add_patch(Rectangle((tb_x, tb_y), W - 10 - tb_x, 22, fill=False, lw=LW))
for yy in (tb_y + 11,):
    ax.plot([tb_x, W - 10], [yy, yy], lw=THIN, color="k")
ax.text(tb_x + 2, tb_y + 14.5, "POV3D V1.2  玻璃上 圆环透明玻璃 (外购)", fontsize=10)
ax.text(tb_x + 2, tb_y + 4, f"{NAME}   Ø{OD:g}/Ø{ID:g}×{T:g}   比例 1:1   单位 mm   A3   2026-11-13", fontsize=8)

fig.savefig(OUT / f"{NAME}_drawing.pdf")
fig.savefig(OUT / f"{NAME}_drawing.png", dpi=150)
print("wrote", OUT)
