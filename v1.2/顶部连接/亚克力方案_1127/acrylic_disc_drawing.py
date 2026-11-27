"""顶部亚克力圆盘 加工图 (2026-11-27 定): OD200×8, 外台阶 r95–100 深 4, 中心 Ø8.5 通孔 + Ø10.05 沉孔深 6 (台肩 2) 放 MR105ZZ, 无螺丝孔"""
import math
from pathlib import Path
import ezdxf, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle, Polygon
OD, ID, T, D = 200.0, 10.05, 8.0, 4.0      # 11-27 用户「按8mm改」: 厚 8, 外台阶深 4; 中心 MR105ZZ (L-1050 Φ5×Φ10×3) 从顶面放入坐台肩, 上方藏 M3 超薄头, 顶面平
ID_S, BD, CS, CS_H = 8.5, 6.0, 10.05, 0.0   # 11-27 13:2x 用户「8mm吧按照2+3+3」: 台肩 2 (以底面为基准) + MR105 3 + 上方 3 (螺柱伸出 0.5 + 头 1.5 + 隙 0.3 + 盖 0.7)
# 叠层 (Z 从底面): 台肩 0–2, MR105 2–5, 螺柱顶 5.5, M3 超薄头 5.5–7, 隙 0.3, 盖顶板 7.3–8 (裙边坐轴承外圈)
R_OR = 95.0                                 # 外台阶 r95–100 (宽 5)
N, RH, HD, A0 = 0, 90.5, 3.4, 0.0      # 11-27 用户: 亚克力不打孔 (竖向锁取消)
OUT = Path(__file__).resolve().parent; NAME = "glass_top_acrylic_v1_2"
f = "/mnt/c/Windows/Fonts/msyh.ttc"; font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name(); plt.rcParams["axes.unicode_minus"] = False
# DXF (俯视轮廓 + 台阶线 + 孔)
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM; m = doc.modelspace()
for r in (OD / 2, ID_S / 2): m.add_circle((0, 0), r, dxfattribs={"layer": "CUT"})
m.add_circle((0, 0), ID / 2, dxfattribs={"layer": "TOP_BORE"})
m.add_circle((0, 0), R_OR, dxfattribs={"layer": "STEP_4"})
PTS = [(RH * math.cos(math.radians(A0 + 45 * k)), RH * math.sin(math.radians(A0 + 45 * k))) for k in range(N)]
for p in PTS: m.add_circle(p, HD / 2, dxfattribs={"layer": "CUT"})
doc.saveas(OUT / f"{NAME}.dxf")
W, H = 420.0, 297.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off"); LW, THIN = 0.7, 0.3
ax.add_patch(Rectangle((10, 10), W - 20, H - 20, fill=False, lw=LW))
CL = (0, (12, 3, 2, 3))
def arrow(p0, p1): ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
def lead(p, q, t, **k): ax.annotate(t, p, q, fontsize=8, arrowprops=dict(arrowstyle="-", lw=THIN), **k)
# 主视 1:1
cx, cy = 125.0, 160.0
for r, ls in ((OD / 2, "-"), (ID_S / 2, "-"), (ID / 2, "-"), (R_OR, "--")): ax.add_patch(Circle((cx, cy), r, fill=False, lw=LW if ls == "-" else THIN, ls=ls))
for x, y in PTS: ax.add_patch(Circle((cx + x, cy + y), HD / 2, fill=False, lw=LW))
for dx, dy in ((1, 0), (0, 1)): ax.plot([cx - dx * 105, cx + dx * 105], [cy - dy * 105, cy + dy * 105], lw=THIN, color="k", ls=CL)
a = math.radians(-50); arrow((cx + 100 * math.cos(a), cy + 100 * math.sin(a)), (cx - 100 * math.cos(a), cy - 100 * math.sin(a)))
ax.text(cx - 40, cy + 42, "Ø200 ±0.2", fontsize=9, rotation=-50)
lead((cx + R_OR * math.cos(math.radians(150)), cy + R_OR * math.sin(math.radians(150))), (cx - 118, cy + 92), f"外圈台阶 Ø{2 * R_OR:g}–Ø200 (宽 5)\n(虚线 = 台阶边, 深 {D:g})")
lead((cx + CS / 2 * math.cos(math.radians(-60)), cy + CS / 2 * math.sin(math.radians(-60))), (cx + 20, cy - 70), f"中心 Ø{ID:g} 深 {BD:g} + Ø{ID_S:g} 通孔 (见放大 II)")
ax.text(cx, cy - 118, "主视图 (顶面, 台阶面朝上) 1:1", ha="center", fontsize=9)
for xx in (cx - 112, cx + 108): ax.text(xx, cy + 3, "A", fontsize=11)
# 剖视 A-A 1:1 (水平放, 上方) + 局部放大 5:1
sx, sy = 270.0, 255.0
def half(sg, s=1.0, ox=sx, oy=sy):
    P = [(ID_S / 2, 0), (OD / 2, 0), (OD / 2, T - D), (R_OR, T - D), (R_OR, T), (ID / 2, T), (ID / 2, T - BD), (ID_S / 2, T - BD)]
    return [(ox + sg * r * s, oy + z * s) for r, z in P]
# 1:1 剖视太大 (200 宽) → 0.6:1
S = 0.6
for sg in (1, -1): ax.add_patch(Polygon(half(sg, S), closed=True, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
ax.plot([sx, sx], [sy - 6, sy + 9], lw=THIN, color="k", ls=CL); ax.text(sx, sy - 12, "剖视 A-A 0.6:1", ha="center", fontsize=9)
# 局部放大 I (外圈) / II (内圈) 4:1
K = 3.5
bx, by = 230.0, 175.0   # 外圈放大: r 82..101
P = [(88, 0), (100, 0), (100, T - D), (R_OR, T - D), (R_OR, T), (88, T)]
ax.add_patch(Polygon([(bx + (r - 88) * K, by + z * K) for r, z in P], closed=True, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
arrow((bx + (R_OR - 88) * K, by + T * K + 5), (bx + (100 - 88) * K, by + T * K + 5)); ax.text(bx + (97.5 - 88) * K, by + T * K + 6.2, "5 (Ø190→Ø200)", ha="center", fontsize=8)
arrow((bx + 12 * K + 5, by + (T - D) * K), (bx + 12 * K + 5, by + T * K)); ax.text(bx + 12 * K + 7, by + (T - D / 2) * K, f"{D:g} ±0.1", fontsize=8, va="center")
arrow((bx + 12 * K + 18, by), (bx + 12 * K + 18, by + T * K)); ax.text(bx + 12 * K + 20, by + T / 2 * K, f"{T:g} ±0.2", fontsize=8, va="center")
ax.text(bx + 30, by - 20, "局部放大 I (外圈台阶) 3.5:1", ha="center", fontsize=9)
K2 = 5.0; cx2, cy2 = 318.0, 175.0   # 局部放大 II 半剖 r 0..9, 7:1 (左 = 轴线)
RW = 9.0
P = [(ID_S / 2, 0), (RW, 0), (RW, T), (ID / 2, T), (ID / 2, T - BD), (ID_S / 2, T - BD)]
X = lambda r: cx2 + r * K2; Y = lambda z: cy2 + z * K2
ax.add_patch(Polygon([(X(r), Y(z)) for r, z in P], closed=True, fc="#dfe9f3", ec="k", lw=LW, hatch="////"))
ax.plot([X(RW)] * 2, [Y(0), Y(T)], lw=THIN, color="k", ls=(0, (4, 2)))      # 断开线
ax.plot([cx2, cx2], [Y(0) - 4, Y(T) + 4], lw=THIN, color="k", ls=CL)
# 装配示意 (细双点划线): 轴承 / 螺柱 / 螺丝头 / 顶盖
ph = dict(fill=False, lw=0.35, ls=(0, (5, 1.5, 1, 1.5)), ec="#666")
zb0 = T - BD; ax.add_patch(Rectangle((X(2.5), Y(zb0)), (5.0 - 2.5) * K2, 3 * K2, **ph)); ax.text(X(3.75), Y(zb0 + 1.5), "MR105", fontsize=5, ha="center", va="center", color="#666")
ax.add_patch(Rectangle((X(0), Y(-0.6)), 2.5 * K2, (zb0 + 3.5 + 0.6) * K2, **ph)); ax.text(X(1.25), Y(0.6), "螺柱\nΦ5", fontsize=5.5, ha="center", color="#666")
ax.add_patch(Rectangle((X(0), Y(zb0 + 3.5)), 3.5 * K2, 1.5 * K2, **ph)); ax.text(X(1.75), Y(zb0 + 4.25), "M3 头", fontsize=6, ha="center", va="center", color="#666")
ax.add_patch(Polygon([(X(0), Y(T)), (X(5.0), Y(T)), (X(5.0), Y(zb0 + 3)), (X(4.0), Y(zb0 + 3)), (X(4.0), Y(T - 0.7)), (X(0), Y(T - 0.7))], closed=True, **ph)); ax.text(X(2.0), Y(T - 0.35), "盖子", fontsize=5.5, ha="center", va="center", color="#666")
# 直径 (半剖: 轴线 → 孔壁)
arrow((cx2, Y(T) + 5), (X(ID / 2), Y(T) + 5)); ax.text(cx2 + 1, Y(T) + 6.2, f"Ø{ID:g} +0.02/0", fontsize=8)
arrow((cx2, Y(0) - 5), (X(ID_S / 2), Y(0) - 5)); ax.text(cx2 + 1, Y(0) - 10, f"Ø{ID_S:g} +0.1/0 通孔", fontsize=8)
# 深度 (右侧, 都从顶面量)
for xo, z0, z1, t in ((8, 0, T - BD, f"{T - BD:g} ±0.05 (台肩, 以底面为基准)"), (30, 0, T, f"{T:g}")):
    arrow((X(RW) + xo, Y(z0)), (X(RW) + xo, Y(z1))); ax.text(X(RW) + xo + 1.5, Y((z0 + z1) / 2) + (6 if xo == 8 else 0), t, fontsize=7.5, va="center")
for z in (T - BD, 0): ax.plot([X(RW), X(RW) + 32], [Y(z)] * 2, lw=0.2, color="k")
ax.annotate("台肩: 只托轴承外圈 (Ø8.5 > 内圈外径)", (X(ID_S / 2 + 0.4), Y(T - BD)), (cx2 - 8, Y(0) - 18), fontsize=7, arrowprops=dict(arrowstyle="-", lw=THIN))
ax.text(X(9), Y(0) - 27, "局部放大 II (中心孔, 半剖) 5:1   细点划线 = 装配件示意", ha="center", fontsize=9)
req = ["技术要求:",
 "1. 材质: 透明 PMMA 亚克力 (浇铸板优先), 透光率 ≥ 92 %, 无气泡/划痕/银纹。",
 f"2. 外径 Ø{OD:g} ±0.2; 中心 Ø{ID_S:g} +0.1/0 通孔 + 顶面沉孔 Ø{ID:g} +0.02/0 (轴承滑配), 孔底留台肩厚 {T - BD:g} ±0.05 (以底面为基准),",
 "   精镗, 圆度 ≤ 0.01, 与外圆同心度 ≤ 0.05。",
 f"3. 厚度 {T:g} ±0.2; 外圈台阶深 {D:g} ±0.1 (以顶面为基准),",
 f"   台阶 CNC 精铣, 可不抛光; 顶面、底面保持原板光面。",
 "4. 无螺丝孔; MR105ZZ / L-1050 (Φ5×Φ10×3) 从顶面推入坐台肩; 上方藏 M3 超薄头 (螺柱伸出 0.5, 头不碰轴承); 盖子 (打印件) 裙边坐轴承外圈, 顶面齐平;\n   如需加固用环氧, 不用厌氧胶 (会使亚克力开裂)。",
 "5. 外缘棱边 C0.3; 加工后退火消应力 (压轴承前)。",
 "6. 未注公差 ±0.2。附 DXF (CUT 切穿 / STEP_4 顶面台阶 / TOP_BORE 中心沉孔)。",
 "7. 数量: 2 / 10 / 50 件分别报价。"]
ax.text(205, 128, "\n".join(req), fontsize=8, va="top", linespacing=1.55)
tb_x, tb_y = 270, 12
ax.add_patch(Rectangle((tb_x, tb_y), W - 10 - tb_x, 22, fill=False, lw=LW)); ax.plot([tb_x, W - 10], [tb_y + 11] * 2, lw=THIN, color="k")
ax.text(tb_x + 2, tb_y + 14.5, "POV3D V1.2  顶部亚克力圆盘 (外协 CNC)", fontsize=10)
ax.text(tb_x + 2, tb_y + 4, f"{NAME}   Ø200×8 外台阶 + 中心轴承座   单位 mm   A3   2026-11-27", fontsize=8)
try: fig.savefig(OUT / f"{NAME}_drawing.pdf")
except PermissionError: fig.savefig(OUT / f"{NAME}_drawing_NEW.pdf"); print("PDF 被占用, 另存 _NEW.pdf")
fig.savefig(OUT / f"{NAME}_drawing.png", dpi=150); print(OUT / f"{NAME}_drawing.png")
