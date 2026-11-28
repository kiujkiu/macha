"""
侧面玻璃管 (外购件, 开孔) 询价图 + STEP + DXF (2026-11-28 用户「开孔后的模型发我，图纸，我找厂家做」)
尺寸全读 build_v1_2 (GL_OD/GL_T/GL_H, 横锁 GS_ANG/GS_GLASS_D/GB_Z/GS_Z), 主模型改了重跑即可:
    cd v1.2/scripts && ../../.venv/bin/python drawing_glass_tube_v1_2.py
输出 v1.2/models/glass_tube_v1_2/
    glass_tube_v1_2.step               (下端面 Z0, 孔 0° 在 +X)
    glass_tube_v1_2_drawing.pdf / .png (A3 横: 主视 + 俯视 + 孔位展开 + 局部放大 + 技术要求)
    glass_tube_v1_2.dxf                (俯视轮廓 + 孔位展开图, 1:1)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_v1_2 as B  # noqa: E402
from OCP.gp import gp_Trsf, gp_Vec  # noqa: E402
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs  # noqa: E402

import ezdxf  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

OD, T, H = B.GL_OD, B.GL_T, B.GL_H
ID = OD - 2 * T
HOLE = B.GS_GLASS_D
ANG = list(B.GS_ANG)
Z_LO = round(B.GB_Z - B.Z_G, 2)            # 下排孔心离下端
Z_HI = round(B.GS_Z - B.Z_G, 2)            # 上排孔心离下端
E_HI = round(H - Z_HI, 2)                  # 上排孔心离上端
CH = 0.5
NAME = "glass_tube_v1_2"
OUT = Path(__file__).resolve().parents[1] / "models" / NAME
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- STEP (下端面 Z0) ----------------
t = gp_Trsf(); t.SetTranslation(gp_Vec(0, 0, -B.Z_G))
tube0 = B.xf(B.tube, t)
w = STEPControl_Writer(); w.Transfer(tube0, STEPControl_AsIs); w.Write(str(OUT / f"{NAME}.step"))
print("vol", round(B.vol(tube0), 1), "mm3  bbox", [round(v, 2) for v in B.bbox(tube0)])

# ---------------- DXF: 俯视 + 展开 (外圆周长) ----------------
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
m = doc.modelspace()
m.add_circle((0, 0), OD / 2); m.add_circle((0, 0), ID / 2)
L = math.pi * OD
x0, y0 = OD, -H / 2
m.add_lwpolyline([(x0, y0), (x0 + L, y0), (x0 + L, y0 + H), (x0, y0 + H)], close=True)
for a in ANG:
    for z in (Z_LO, Z_HI):
        m.add_circle((x0 + L * a / 360, y0 + z), HOLE / 2)
doc.saveas(OUT / f"{NAME}.dxf")

# ---------------- 图纸 A3 ----------------
for f in ("/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/simhei.ttf"):
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False
W, Hp = 420.0, 297.0
fig = plt.figure(figsize=(W / 25.4, Hp / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, Hp); ax.set_aspect("equal"); ax.axis("off")
LW, THIN = 0.7, 0.3
CL = (0, (12, 3, 2, 3))
ax.add_patch(Rectangle((10, 10), W - 20, Hp - 20, fill=False, lw=LW))


def arrow(p0, p1):
    ax.annotate("", p1, p0, arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))


def dim_v(x, y0_, y1_, txt, xe=None, side=1):
    arrow((x, y0_), (x, y1_))
    ax.text(x + side * 1.2, (y0_ + y1_) / 2, txt, rotation=90, ha="left" if side > 0 else "right", va="center", fontsize=7.5)
    if xe is not None:
        for yy in (y0_, y1_):
            ax.plot([xe, x + side * 1], [yy, yy], lw=THIN, color="k")


def dim_h(x0_, x1_, y, txt, ye=None):
    arrow((x0_, y), (x1_, y))
    ax.text((x0_ + x1_) / 2, y + 1.0, txt, ha="center", va="bottom", fontsize=7.5)
    if ye is not None:
        for xx in (x0_, x1_):
            ax.plot([xx, xx], [ye, y + 1], lw=THIN, color="k")


# 1) 主视 (剖视 A-A, 1:2): 左半外形 / 右半剖开, 0° 孔在右
S1 = 0.5
fx, fy = 75.0, 140.0                         # 轴线 x, 下端面 y
ro, ri, hh = OD / 2 * S1, ID / 2 * S1, H * S1
ax.add_patch(Rectangle((fx - ro, fy), 2 * ro, hh, fill=False, lw=LW))
ax.add_patch(Rectangle((fx + ri, fy), ro - ri, hh, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
ax.plot([fx + ri, fx + ri], [fy, fy + hh], lw=LW, color="k")
ax.plot([fx, fx], [fy - 5, fy + hh + 5], lw=THIN, color="k", ls=CL)
for z in (Z_LO, Z_HI):                       # 右侧 0° 孔 (剖到) + 正面 90° 孔 (外形上的圆)
    yy = fy + z * S1
    ax.add_patch(Rectangle((fx + ri, yy - HOLE / 2 * S1), ro - ri, HOLE * S1, fc="white", ec="k", lw=THIN))
    ax.plot([fx + ri - 2, fx + ro + 2], [yy, yy], lw=THIN, color="k", ls=CL)
    for a in ANG:                            # 外形半边 (左, x<0 一侧) 能看到的孔: 投影 x = r·cos
        c = math.cos(math.radians(a)); s = math.sin(math.radians(a))
        if s < -1e-6 and c <= 1e-6:          # 朝向观察者 (−Y) 的左半
            ax.add_patch(Circle((fx + ro * c, yy), HOLE / 2 * S1, fill=False, lw=THIN))
dim_v(fx + ro + 12, fy, fy + hh, f"{H:g} ±0.3", xe=fx + ro + 1)
dim_v(fx + ro + 5, fy, fy + Z_LO * S1, f"{Z_LO:g}", xe=fx + ro + 1)
dim_v(fx + ro + 5, fy + Z_HI * S1, fy + hh, f"{E_HI:g}", xe=fx + ro + 1)
dim_h(fx - ro, fx + ro, fy + hh + 8, f"Ø{OD:g}", ye=fy + hh + 1)
dim_h(fx + ri, fx + ro, fy - 7, f"{T:g}", ye=fy - 1)
ax.text(fx, fy - 16, "主视图 (右半剖 A-A)  1:2", ha="center", fontsize=9)

# 2) 俯视 (1:2): 孔角度
tx, ty = 215.0, 205.0
ax.add_patch(Circle((tx, ty), ro, fill=False, lw=LW)); ax.add_patch(Circle((tx, ty), ri, fill=False, lw=LW))
for a in ANG:
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    ax.plot([tx + (ri - 3) * c, tx + (ro + 6) * c], [ty + (ri - 3) * s, ty + (ro + 6) * s], lw=THIN, color="k", ls=CL)
    ax.add_patch(Rectangle((0, 0), 0, 0))
    ax.text(tx + (ro + 10) * c, ty + (ro + 10) * s, f"{a:g}°", ha="center", va="center", fontsize=7)
    # 径向孔投影 (两条细线)
    px, py = -s * HOLE / 2 * S1, c * HOLE / 2 * S1
    for k in (1, -1):
        ax.plot([tx + ri * c + k * px, tx + ro * c + k * px], [ty + ri * s + k * py, ty + ro * s + k * py], lw=THIN, color="k")
ax.text(tx + ro + 15, ty + 1.5, "A", fontsize=10); ax.text(tx - ro - 19, ty + 1.5, "A", fontsize=10)   # 剖切线 0°–180°
ax.text(tx, ty - ro - 17, f"俯视图 1:2  (内径 Ø{ID:g}; 上下两排孔角度相同, 8 等分 45°)", ha="center", fontsize=8.5)

# 3) 孔位展开 (外圆周, 横向 1:4 / 纵向 1:2 示意)
ux, uy, SX = 25.0, 40.0, 0.25
SU = 0.25                                   # 展开图竖向也 1:4
Lw = math.pi * OD * SX
ax.add_patch(Rectangle((ux, uy), Lw, H * SU, fill=False, lw=LW))
for a in ANG + [360]:
    xx = ux + Lw * a / 360
    ax.plot([xx, xx], [uy - 2, uy + H * SU + 2], lw=THIN, color="k", ls=CL)
    ax.text(xx, uy - 5, f"{a:g}°", ha="center", fontsize=6.5)
for a in ANG:
    for z in (Z_LO, Z_HI):
        ax.add_patch(Circle((ux + Lw * a / 360, uy + z * SU), HOLE / 2 * SU, fc="white", ec="k", lw=THIN))
ax.text(ux + Lw / 2, uy - 13, f"外圆展开 (周长 {math.pi * OD:.1f}; 1:4)  共 {2 * len(ANG)} 孔", ha="center", fontsize=8.5)
dim_v(ux + Lw + 10, uy, uy + H * SU, f"{H:g}", xe=ux + Lw + 1)

# 4) 局部放大 I (孔, 5:1): 沿轴剖, 壁厚方向 x
dx, dy, S4 = 330.0, 245.0, 5.0
ax.add_patch(Rectangle((dx - T / 2 * S4, dy - 9 * S4 / 2), T * S4, 9 * S4, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
ax.add_patch(Rectangle((dx - T / 2 * S4 - 0.3, dy - HOLE / 2 * S4), T * S4 + 0.6, HOLE * S4, fc="white", ec="k", lw=LW))
ax.plot([dx - T / 2 * S4 - 6, dx + T / 2 * S4 + 6], [dy, dy], lw=THIN, color="k", ls=CL)
dim_v(dx + T / 2 * S4 + 8, dy - HOLE / 2 * S4, dy + HOLE / 2 * S4, f"Ø{HOLE:g} +0.2/0", xe=dx + T / 2 * S4 + 1)
dim_h(dx - T / 2 * S4, dx + T / 2 * S4, dy + 9 * S4 / 2 + 3, f"{T:g}")
ax.text(dx, dy - 9 * S4 / 2 - 7, f"局部放大 I  5:1\n孔口两端倒角 C{CH:g} (去崩边)", ha="center", va="top", fontsize=8)

# 技术要求 + 标题栏
req = [
    "技术要求:",
    "1. 材质: 透明石英玻璃管 (熔融石英), 透光率 ≥ 90 %, 无气泡、气线、划痕、崩边。",
    f"2. 外径 Ø{OD:g}, 壁厚 {T:g} (内径 Ø{ID:g}), 圆度 ≤ 0.3。两端与上下塑料件单边留 {B.GL_CLR:g} 间隙 (配合件 内 Ø{2 * B.gi:g} / 外 Ø{2 * B.go:g}):",
    f"   目标公差 外径 ±{B.GL_CLR:g} / 内径 ±{B.GL_CLR:g}, 请注明实际能做到的公差 (拉制 / 外圆磨削 分别报价)。",
    f"3. 长度 {H:g} ±0.3; 两端面磨平, 与轴线垂直度 ≤ 0.3, 内外棱倒角 C{CH:g}。",
    f"4. 径向通孔 Ø{HOLE:g} +0.2/0 共 {2 * len(ANG)} 个 (穿 M3 螺丝): 下排孔心距下端 {Z_LO:g}, 上排孔心距上端 {E_HI:g},",
    f"   孔边距端面 {min(Z_LO, E_HI) - HOLE / 2:g}; 两排各 8 个沿圆周 45° 等分, 上下孔同角度对齐;",
    "   孔位 ±0.2, 孔口两端倒角 C0.5, 孔壁无裂纹 (建议金刚石钻 / 超声加工)。",
    "5. 未注公差 ±0.3。询价按 2 / 10 / 50 件分别报价。附 STEP 模型 (glass_tube_v1_2.step)。",
]
ax.text(268, 185, "\n".join(req), fontsize=7.3, va="top", linespacing=1.5)
tb_x, tb_y = 268, 12
ax.add_patch(Rectangle((tb_x, tb_y), W - 10 - tb_x, 22, fill=False, lw=LW))
ax.plot([tb_x, W - 10], [tb_y + 11, tb_y + 11], lw=THIN, color="k")
ax.text(tb_x + 2, tb_y + 14.5, "POV3D V1.2  侧面石英玻璃管 (外购, 开孔)", fontsize=10)
ax.text(tb_x + 2, tb_y + 4, f"{NAME}   Ø{OD:g}×{T:g}×{H:g}   孔 {2 * len(ANG)}×Ø{HOLE:g}   单位 mm   A3   2026-11-28", fontsize=7.5)

try:
    fig.savefig(OUT / f"{NAME}_drawing.pdf")
except PermissionError:
    fig.savefig(OUT / f"{NAME}_drawing.NEW.pdf"); print("PDF 被占用, 另存 .NEW.pdf")
fig.savefig(OUT / f"{NAME}_drawing.png", dpi=150)
print("wrote", OUT, " Z_LO", Z_LO, " Z_HI", Z_HI, " E_HI", E_HI)
