"""
给硬件的说明图: ACG525-CORE-V2 两只 LB3524 插头中心距 26.636 是怎么来的 (2026-10-16)。
数据直接从官方文件机读 (不手抄):
  ① 核心板封装  发票内容/ACG525-CORE_LIB.zip → ACG525-CORE.PcbLib「ACG525-CORE_NEW260310」
  ② 官方底板    ACG525-CB-V2-260316_SMT/coord…/Pick Place for HQCoord.csv  (P1/P2)
  ③ 桥板 10-14  结构堆叠交接_2026-10-15/源工程/…高云转接板_1014….epro2  (CN3/CN6)
输出 A3 横版 PDF + PNG。用法: ../../.venv/bin/python build_acg525_spacing.py
"""
import io
import json
import sys
import zipfile
from pathlib import Path
import numpy as np
import olefile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "boards"))
import pcblib_dump as P                      # noqa: E402

LIB_ZIP = Path("/mnt/d/claude_workspace/发票/发票内容/ACG525-CORE_LIB.zip")
CB_CSV = Path("/mnt/d/claude_workspace/发票/发票内容/ACG525-CB-V2-260316-工程源文件/"
              "ACG525-CB-V2-260316_SMT/coord_ACG525-CB-V2-260316/Pick Place for HQCoord.csv")
BR_EPRO = Path("/mnt/d/claude_workspace/pov3d/结构堆叠交接_2026-10-15/源工程/"
               "ProPrj_01_ICN2260_LED_V01_高云转接板_1014_2026-10-14.epro2")
MIL = 0.0254

font_manager.fontManager.addfont("/mnt/c/Windows/Fonts/simhei.ttf")
plt.rcParams["font.family"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False

# ---------- ① 封装 ----------
zf = zipfile.ZipFile(LIB_ZIP)
lib = next(n for n in zf.namelist() if n.endswith(".PcbLib"))
ole = olefile.OleFileIO(io.BytesIO(zf.read(lib)))
prims = P.parse(ole.openstream(["ACG525-CORE_NEW260310", "Data"]).read())
pads = [p for p in prims if p[0] == "pad" and p[7] < 0.01]
holes = [p for p in prims if p[0] == "pad" and p[7] > 2.0]
silk = [p for p in prims if p[0] == "track" and p[1] == 33]
A = np.array([(p[3], p[4]) for p in pads if p[2].startswith("A")])
B = np.array([(p[3], p[4]) for p in pads if p[2].startswith("B")])
A_rows = sorted(set(np.round(A[:, 1], 3)))
B_rows = sorted(set(np.round(B[:, 1], 3)))
cA, cB = A.mean(0), B.mean(0)
D_FP = cB[1] - cA[1]
DX_FP = cB[0] - cA[0]
pad_w, pad_h = pads[0][5], pads[0][6]

# ---------- ② 官方底板贴片坐标 ----------
cb = {}
for line in CB_CSV.read_bytes().decode("gbk", "replace").splitlines():
    f = line.split(",")
    if f[0] in ("P1", "P2"):
        cb[f[0]] = (float(f[5]), float(f[6]), float(f[7]))
D_CB = (cb["P2"][1] - cb["P1"][1]) * MIL
DX_CB = (cb["P2"][0] - cb["P1"][0]) * MIL

# ---------- ③ 桥板 epro2 ----------
ez = zipfile.ZipFile(BR_EPRO)
epru = ez.read(next(n for n in ez.namelist() if n.endswith(".epru"))).decode("utf-8")
comp, desig = {}, {}
for l in epru.split("\n"):
    if l.startswith('{"type":"COMPONENT"'):
        h, b = l.split("||")[:2]
        comp[json.loads(h)["id"]] = json.loads(b.rstrip("|"))
for l in epru.split("\n"):
    if l.startswith('{"type":"ATTR"') and '"key":"Designator"' in l and '"partitionId"' in l:
        b = json.loads(l.split("||")[1].rstrip("|"))
        if b.get("value") in ("CN3", "CN6") and b.get("parentId") in comp:
            desig[b["value"]] = comp[b["parentId"]]
br = {k: (v["x"], v["y"], v["angle"]) for k, v in desig.items()}
D_BR = abs(br["CN3"][0] - br["CN6"][0]) * MIL
DY_BR = abs(br["CN3"][1] - br["CN6"][1]) * MIL

print(f"封装 A ({cA[0]:.3f},{cA[1]:.3f})  B ({cB[0]:.3f},{cB[1]:.3f})  中心距 {D_FP:.3f}  错位 {DX_FP:+.3f}")
print(f"官方底板 P1 {cb['P1']} P2 {cb['P2']}  ΔY {D_CB:.3f}  ΔX {DX_CB:+.3f}")
print(f"桥板 CN6 {br['CN6']} CN3 {br['CN3']}  间距 {D_BR:.3f}  错位 {DY_BR:.3f}")
assert abs(D_FP - D_CB) < 0.005, "封装与官方底板不一致"

# ================= 画图 =================
fig = plt.figure(figsize=(16.54, 11.69))       # A3 横
fig.text(0.5, 0.965, "ACG525-CORE-V2 两只 LB3524 插头中心距 = 26.636 mm  —— 推导与核对",
         ha="center", fontsize=20, weight="bold")
fig.text(0.5, 0.94, "数据全部从官方文件机读 (封装 PcbLib 焊盘坐标 / 官方底板贴片坐标 / 桥板 10-14 工程), 未手抄。2026-10-16",
         ha="center", fontsize=11, color="#555")

# ---- 左: 封装俯视 ----
ax = fig.add_axes([0.03, 0.08, 0.50, 0.83])
ax.set_aspect("equal"); ax.axis("off")
xs = [q for p in silk for q in (p[2], p[4])]; ys = [q for p in silk for q in (p[3], p[5])]
ox0, ox1, oy0, oy1 = min(xs), max(xs), min(ys), max(ys)
ax.add_patch(Rectangle((ox0, oy0), ox1 - ox0, oy1 - oy0, fill=False, lw=1.2, ec="#222"))
for h in holes:
    ax.add_patch(Circle((h[3], h[4]), h[7] / 2, fill=False, lw=1, ec="#222"))
    ax.add_patch(Circle((h[3], h[4]), 2.0, fill=False, lw=0.5, ec="#999", ls="--"))
for p in pads:
    col = "#d9822b" if p[2].startswith("A") else "#2b7bd9"
    ax.add_patch(Rectangle((p[3] - p[5] / 2, p[4] - p[6] / 2), p[5], p[6], fc=col, ec="none", alpha=0.8))
# 排中心线 + 插头中心线
for rows, c, col, tag in ((A_rows, cA, "#d9822b", "A"), (B_rows, cB, "#2b7bd9", "B")):
    for y in rows:
        ax.plot([ox0 - 1, ox1 + 1], [y, y], color=col, lw=0.4, ls=":")
    ax.plot([ox0 - 3, ox1 + 6], [c[1], c[1]], color=col, lw=0.9, ls="-.")
    ax.plot(*c, marker="+", ms=14, mew=1.6, color="k")
    ax.text(c[0], c[1] + (-3.4 if tag == "A" else 3.0),
            f"插头 {tag} 中心 ({c[0]:.3f}, {c[1]:.3f})", ha="center", fontsize=10, weight="bold")


def vdim(x, y0, y1, txt, col="#c00", fs=12, side="right"):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.3))
    ax.text(x + (0.8 if side == "right" else -0.8), (y0 + y1) / 2, txt, color=col, fontsize=fs,
            rotation=90, va="center", ha="left" if side == "right" else "right", weight="bold")


vdim(ox1 + 5, cA[1], cB[1], f"{D_FP:.3f}", fs=16)
vdim(ox1 + 1.6, A_rows[0], A_rows[1], f"{A_rows[1]-A_rows[0]:.1f} 排距", col="#d9822b", fs=9)
vdim(ox1 + 1.6, B_rows[0], B_rows[1], f"{B_rows[1]-B_rows[0]:.1f}", col="#2b7bd9", fs=9)
# 0.211 错位
ax.plot([cA[0], cA[0]], [cA[1], cB[1] + 4.5], color="#d9822b", lw=0.6, ls="--")
ax.plot([cB[0], cB[0]], [cB[1], cB[1] + 4.5], color="#2b7bd9", lw=0.6, ls="--")
ax.annotate(f"B 比 A 沿 X 错开 {abs(DX_FP):.3f}", (cA[0], cB[1] + 4.2), (cA[0] + 7, cB[1] + 6.2),
            fontsize=10, color="#c00", arrowprops=dict(arrowstyle="->", color="#c00", lw=0.8))
# 孔距
ax.annotate("", (holes[0][3] if False else 0, oy0 - 3), (46, oy0 - 3),
            arrowprops=dict(arrowstyle="<->", color="#555", lw=0.8))
ax.text(23, oy0 - 4.6, "孔距 46 (4×Φ2.7)", ha="center", fontsize=9, color="#555")
ax.annotate("", (ox0 - 3, 0), (ox0 - 3, 31), arrowprops=dict(arrowstyle="<->", color="#555", lw=0.8))
ax.text(ox0 - 3.8, 15.5, "31", rotation=90, va="center", ha="right", fontsize=9, color="#555")
ax.text(23, oy1 + 7.5, f"ACG525-CORE_NEW260310 封装 (俯视 = 核心板插头面, 单位 mm, 原点 = 孔 H4)\n"
        f"外框 {ox1-ox0:.3f} × {oy1-oy0:.3f}; 焊盘 {pad_w:.2f}×{pad_h:.2f}; "
        f"A1..A100 橙 / B1..B100 蓝", ha="center", fontsize=10)
ax.set_xlim(ox0 - 9, ox1 + 14); ax.set_ylim(oy0 - 8, oy1 + 12)

# ---- 右: 推导 + 核对 ----
tx = fig.add_axes([0.55, 0.06, 0.43, 0.86]); tx.axis("off")
y = 0.98


def block(title, lines, color="#222", box=None):
    global y
    tx.text(0.0, y, title, fontsize=13.5, weight="bold", color=color, va="top")
    y -= 0.042
    for s in lines:
        tx.text(0.02, y, s, fontsize=11, va="top", family="SimHei")
        y -= 0.034
    y -= 0.018


block("① 封装焊盘坐标 → 插头中心 (每只 = 100 个焊盘的平均)", [
    f"A 插头两排焊盘 Y = {A_rows[0]:.3f} / {A_rows[1]:.3f}  →  中心 Y = {cA[1]:.3f}",
    f"B 插头两排焊盘 Y = {B_rows[0]:.3f} / {B_rows[1]:.3f}  →  中心 Y = {cB[1]:.3f}",
    f"中心距 = {cB[1]:.3f} - {cA[1]:.3f} = {D_FP:.3f} mm",
    f"沿插头长向: A 中心 X {cA[0]:.3f}, B 中心 X {cB[0]:.3f}  →  错开 {abs(DX_FP):.3f} mm",
])
block("② 官方底板 ACG525-CB-V2 贴片坐标 (独立来源, 单位 mil)", [
    f"P1  LB3524-G100P  ({cb['P1'][0]:.2f}, {cb['P1'][1]:.2f})  {cb['P1'][2]:.0f}°",
    f"P2  LB3524-G100P  ({cb['P2'][0]:.2f}, {cb['P2'][1]:.2f})    {cb['P2'][2]:.0f}°",
    f"ΔY = {cb['P2'][1]-cb['P1'][1]:.2f} mil = {D_CB:.3f} mm    ΔX = {cb['P2'][0]-cb['P1'][0]:.2f} mil = {abs(DX_CB):.3f} mm",
    "→ 与 ① 完全一致 (中心距与错位都对上)",
], color="#1a7f37")
block("③ 桥板 10-14 版 (同为 LB3524-G100P 封装, 焊盘关于原点对称)", [
    f"CN6  ({br['CN6'][0]:.4f}, {br['CN6'][1]:.2f}) mil  {br['CN6'][2]:.0f}°",
    f"CN3  ({br['CN3'][0]:.4f}, {br['CN3'][1]:.2f}) mil  {br['CN3'][2]:.0f}°",
    f"间距 = {abs(br['CN3'][0]-br['CN6'][0]):.3f} mil = {D_BR:.3f} mm    错位 = {DY_BR:.3f}",
    f"× 比官方少 {D_FP-D_BR:.3f} mm, 且缺 {abs(DX_FP):.2f} 错位  (26.000 = 旧 V1/ACA420 封装的数)",
], color="#c00")
block("④ 卡尺实测 (实物 V2 核心板, 量插头塑壳)", [
    "外卡 31.5 / 内卡 21.5  →  中心距 = (31.5 + 21.5) / 2 = 26.5",
    f"与 {D_FP:.3f} 差 {D_FP-26.5:.2f}: 卡尺 0.1 分辨率 ×2 + 塑壳拔模/倒角, 在量法误差内",
    "同样证明桥板的 26.000 不对 (差 0.5 以上)",
])

tx.add_patch(FancyBboxPatch((0.0, y - 0.135), 1.0, 0.135, boxstyle="round,pad=0.01",
                            fc="#fff4e5", ec="#d9822b", lw=1.5, transform=tx.transAxes))
tx.text(0.02, y - 0.01, "桥板需要改", fontsize=14, weight="bold", color="#c00", va="top")
tx.text(0.02, y - 0.05, f"· CN3 与 CN6 中心距  26.000 → {D_FP:.3f} mm  ({D_CB/MIL:.2f} mil)", fontsize=12, va="top")
tx.text(0.02, y - 0.085, f"· 两只沿插头长向错开 {abs(DX_FP):.3f} mm ({abs(cb['P2'][0]-cb['P1'][0]):.2f} mil),"
        " 方向照官方底板 P1/P2", fontsize=12, va="top")
tx.text(0.02, y - 0.12, "  最稳妥: 直接按官方 CB-V2 底板 P1/P2 的相对坐标与角度摆放", fontsize=11, va="top", color="#555")

fig.text(0.03, 0.025, f"源: {LIB_ZIP.name} · {CB_CSV.name} · {BR_EPRO.name}    "
         "生成脚本 pov3d/v1.0/docs/build_acg525_spacing.py", fontsize=8, color="#888")
for ext in ("pdf", "png"):
    out = HERE / f"ACG525_V2_插头中心距_26.636.{ext}"
    fig.savefig(out, dpi=150 if ext == "png" else None)
    print("wrote", out)
