"""
V1.0 转子动平衡预估 (2026-11-03)
================================
读 assembly_v1_0.py 的零件网格 (exec 到 merge/export 之前, 不写任何文件), 给转子件按材料/估重配质量,
算: 转子质量、质心、静不平衡 U、力偶不平衡; 两平面 (下=rim_ring/hub 外圈 R82.5 / 上=top_cap) 配重解;
ISO 21940-11 G6.3 允许残余; 900 rpm 离心力; 顶轴承支架 (4 根 Φ8 钢柱) 一阶摆动临界转速粗估。

板子没有实测重量 → 按 PCB 尺寸 × FR4 密度 + 元件估重 (BOARD_MASS, 见下表注释)。上秤后改这里重跑即可。
质量分布: 网格闭合的件用均匀密度 (体积分 → 质心/惯量); PCB 件把估重按网格体积分布 (质心取网格的)。

用法: ../../.venv/bin/python balance_v1_0.py [--rpm 900] [--G 6.3]
"""
import argparse
import contextlib
import io
import math
import sys
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--rpm", type=float, default=900.0)
ap.add_argument("--G", type=float, default=6.3, help="ISO 21940 平衡等级 (mm/s)")
args = ap.parse_args()

# ---------------- 读装配 ----------------
SRC = Path(__file__).resolve().parents[1] / "assembly_v1_0.py"
code = SRC.read_text().split("# ===================== merge + export")[0]
g = {"__file__": str(SRC), "__name__": "asm"}
_argv, sys.argv = sys.argv, [str(SRC)]
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(code, str(SRC), "exec"), g)
sys.argv = _argv
PARTS = g["parts"]
P1 = g["P1"]

# ---------------- 质量设定 ----------------
PRINT_RHO = 1.10        # g/cm³, PLA/PETG 打印件等效 (实体 1.24, 薄件多墙 ≈ 85–90%)
RHO = {"steel": 7.85, "brass": 8.5, "nylon": 1.15, "print": PRINT_RHO}

# PCB 估重 (g): FR4 板 = 长×宽×厚×1.9 (含铜) + 元件估计。都是估的, 上秤后替换。
#   LED 灯板 163.95×225×1.84 = 67.9 cm³ → 129 g; + LED 阵列/ICN2260/220µF 电容 ≈ 35 g (STEP 无 LED 本体)
#   桥板 140×50×1.6 = 11.2 cm³ → 21 g; + 连接器 CN1..CN6/FPC 座/电源 ≈ 15 g
#   ACG525 核心板 50.5×35.6×1.6 → 5.5 g; + GW5A BGA/DDR/插头 ≈ 9 g
#   DR1M90 底板 140×80×1.6 = 17.9 cm³ → 34 g; + 驱动/接插件/铜柱 ≈ 26 g
#   FS03 (米联派孪生) 板 + RJ45 + USB + SoC ≈ 45 g;  WiFi AX1800 USB 网卡 (去壳带散热) ≈ 35 g
BOARD_MASS = {
    "LED board": 164.0, "bridge": 36.0, "ACG525": 14.5, "DR1M90": 60.0, "FS03": 45.0, "wifi module": 35.0,
    "FPC": 4.0,
}
# 名前缀 → 材料 (转子件); None = 定子 (不转, 不计)
MAT = [
    ("grid plate", None), ("baseplate_collar", None), ("flange_disc", None), ("mounting_flange", None),
    ("motor", None), ("post", None), ("frame", None), ("688", None), ("vane", None),
    ("hub_disc", "print"), ("rim_ring", "print"), ("wifi_plate", "print"), ("wifi_shell", "print"),
    ("screen_foot", "print"), ("top_cap", "print"), ("sensor", "print"),
    ("nylon", "nylon"), ("hex nut", "brass"), ("standoff", "steel"),
    ("screen screw", "steel"), ("foot screw", "steel"), ("wifi shell screw", "steel"), ("M6", "steel"),
]


def mass_props(t):
    """闭合三角网 → 体积, 一阶矩 (∫x,∫y,∫z), 二阶矩 ∫[x²,y²,z²,xy,yz,zx] (单位 mm)。"""
    a, b, c = (t[:, i].astype(np.float64) for i in range(3))
    d = np.einsum("ij,ij->i", a, np.cross(b, c))       # 6 × 四面体体积 (带号)
    V = d.sum() / 6
    m1 = (d[:, None] * (a + b + c)).sum(0) / 24
    def s2(i, j):
        return (d * (2 * (a[:, i] * a[:, j] + b[:, i] * b[:, j] + c[:, i] * c[:, j])
                     + a[:, i] * b[:, j] + a[:, j] * b[:, i] + a[:, i] * c[:, j] + a[:, j] * c[:, i]
                     + b[:, i] * c[:, j] + b[:, j] * c[:, i])).sum() / 120
    m2 = np.array([s2(0, 0), s2(1, 1), s2(2, 2), s2(0, 1), s2(1, 2), s2(2, 0)])
    return V, m1, m2


rows = []   # name, mass g, m1 (g·mm), m2 (g·mm²)
for name, t in PARTS:
    V, m1, m2 = mass_props(t)
    bm = next((v for k, v in BOARD_MASS.items() if name.startswith(k)), None)
    if bm is not None:
        k = bm / (V / 1000.0)             # g/cm³ 等效 → 估重按网格体积分布
        src = f"估 {bm:g} g"
    else:
        mat = next((m for p, m in MAT if name.startswith(p)), "??")
        if mat is None:
            continue
        if mat == "??":
            raise SystemExit(f"未分类零件: {name}")
        k = RHO[mat]
        src = f"{mat} ρ{k:g}"
    s = k / 1000.0                        # 体积 mm³ → g
    rows.append((name, V * s, m1 * s, m2 * s, src))

M = sum(r[1] for r in rows)
S1 = sum(r[2] for r in rows)
S2 = sum(r[3] for r in rows)
cg = S1 / M
Ux, Uy = S1[0], S1[1]                         # 静不平衡 g·mm (相对转轴)
Pxz, Pyz = S2[5], S2[4]                        # 惯性积 ∫xz, ∫yz (g·mm², 原点 Z=0)

print("=" * 96)
print(f"V1.0 转子质量表 (转速 {args.rpm:g} rpm)")
print(f"{'零件':38s} {'质量 g':>8s} {'质心 X':>8s} {'Y':>8s} {'Z':>8s}  m·r (g·mm)  来源")
for name, m, m1, m2, src in sorted(rows, key=lambda r: -r[1]):
    c = m1 / m
    print(f"{name[:38]:38s} {m:8.1f} {c[0]:8.2f} {c[1]:8.2f} {c[2]:8.1f}  {math.hypot(m1[0], m1[1]):9.1f}  {src}")
print("-" * 96)
print(f"转子总质量 {M:.0f} g;  质心 ({cg[0]:.2f}, {cg[1]:.2f}, {cg[2]:.1f})")
U = math.hypot(Ux, Uy)
print(f"静不平衡 U = {U:.0f} g·mm  @ {math.degrees(math.atan2(Uy, Ux)):.1f}°  (= 质心偏 {U / M:.2f} mm)")

# ---------------- 两平面配重 ----------------
# 下平面: rim_ring/hub 外圈 R82.5 空闲环孔; 上平面: top_cap (顶 333.23) —— 两个平面都按 r 给出需要的 m
Z_LO = P1.DISC_TOP - 5.0           # 配重挂在 hub 底面/环孔里, 约 Z 37
R_LO = P1.RING_OUTER_PCD_R
Z_HI = P1.LED_EDGE_TOP_Z + 7.0 / 2   # top_cap 中面
R_HI = 55.0                          # 上平面配重半径 (top_cap 需加 -X 翼, 仿 top_cap_v4 r55)
# 解: u_lo + u_hi = -U ;  u_lo·Z_LO + u_hi·Z_HI = -Σ m·r·z   (矢量, g·mm)
Mz = np.array([Pxz, Pyz])
Uv = np.array([Ux, Uy])
u_hi = (-Mz + Uv * Z_LO) / (Z_HI - Z_LO)
u_lo = -Uv - u_hi
print(f"\n两平面配重 (下 Z{Z_LO:.1f} r{R_LO:g} / 上 Z{Z_HI:.1f} r{R_HI:g}):")
for tag, u, r in (("下", u_lo, R_LO), ("上", u_hi, R_HI)):
    um = float(np.hypot(*u))
    print(f"  {tag}平面: {um:6.0f} g·mm @ {math.degrees(math.atan2(u[1], u[0])):6.1f}°  → r{r:g} 处 {um / r:5.1f} g")
z_static = (Mz @ Uv) / (Uv @ Uv) if U > 0 else float("nan")
print(f"  (不平衡等效作用高度 Z ≈ {z_static:.0f}; 只在一个平面配会留下力偶)")
# 只用下平面 (单面静平衡) 的残余力偶
print(f"  对比: 只配下平面 → 残余力偶 {float(np.hypot(*(Mz - Uv * Z_LO))) / 1000:.0f} g·m·mm")

# 下平面能用的环孔 (8×R82.5 @22.5+45k, 4 个被 screen_foot 占: 67.5/112.5/247.5/292.5)
free = [22.5, 157.5, 202.5, 337.5]
ang = math.degrees(math.atan2(u_lo[1], u_lo[0]))
pair = sorted(free, key=lambda a: abs((a - ang + 180) % 360 - 180))[:2]
A = np.array([[math.cos(math.radians(a)) for a in pair], [math.sin(math.radians(a)) for a in pair]]) * R_LO
w = np.linalg.solve(A, u_lo)
print(f"  下平面用空闲环孔 {pair[0]:g}°/{pair[1]:g}° 分解: {w[0]:.1f} g + {w[1]:.1f} g"
      f"{'  (有负值 → 角度不在两孔之间)' if (w < 0).any() else ''}")

# ---------------- ISO 允许残余 & 离心力 ----------------
om = args.rpm * 2 * math.pi / 60
Uper = 9549 * args.G * (M / 1000) / args.rpm
print(f"\nISO 21940-11 G{args.G:g} @ {args.rpm:g} rpm: 允许残余 U_per = {Uper:.0f} g·mm (每平面约一半)")
print(f"  未配重: 离心力 {U * 1e-6 * om ** 2:.1f} N (≈ {U * 1e-6 * om ** 2 / 9.81:.2f} kgf), "
      f"是允许值的 {U / Uper:.0f} 倍 → CAD 预配重后残余需 < {100 * Uper / U:.0f}% 才达标")

# ---------------- 一阶临界转速粗估 ----------------
# 模型: 转子刚体绕电机轴承 (Z_P) 摆动, 顶部 688 (Z_T) 被 4 根 Φ8×360 钢柱 + frame 横向弹簧拉住。
#   柱: 底端锁网格板 (按固支), 顶端 frame 是打印件 —— 顶端转动约束介于 铰支 (3EI/L³) 和 导向 (12EI/L³)。
#   frame + 柱上 1/3 质量算到顶点。电机轴承本身的摆动刚度没算 (只会更低)。
E, d, L = 200e3, 8.0, P1.POST_H                 # N/mm², mm
I = math.pi * d ** 4 / 64
fr_m = sum(mass_props(t)[0] for n, t in PARTS if n.startswith("frame")) / 1000 * PRINT_RHO \
    + 4 * math.pi * 16 * L / 1000 * 7.85 / 3
Z_P = 25.0                                      # 电机轴承/转子摆动支点 (电机占位 Z5..31.7)
Z_T = 367.0                                     # 688 两颗中间
# 转子绕支点的横向转动惯量: ∫[(z-Zp)² + x²] dm (绕 Y 轴; 取 x/y 平均)
Ixx_c = S2[2] - 2 * Z_P * S1[2] + Z_P ** 2 * M + 0.5 * (S2[0] + S2[1])   # g·mm²
Ieq = Ixx_c + fr_m * (Z_T - Z_P) ** 2
print(f"\n一阶摆动临界 (转子绕 Z{Z_P:g} 摆, 顶 Z{Z_T:g} 由 4×Φ8×{L:g} 钢柱拉住; frame+柱顶等效 {fr_m:.0f} g):")
print(f"  转子绕支点转动惯量 {Ixx_c * 1e-5:.0f} kg·cm² (= {Ixx_c * 1e-9:.4f} kg·m²)")
for tag, kk in (("铰支 3EI/L³", 3), ("导向 12EI/L³", 12)):
    k = 4 * kk * E * I / L ** 3                 # N/mm
    w_n = math.sqrt(k * 1e3 * ((Z_T - Z_P) * 1e-3) ** 2 / (Ieq * 1e-9))
    f = w_n / 2 / math.pi
    print(f"  {tag:14s}: k = {k:5.1f} N/mm → f₁ ≈ {f:5.1f} Hz = {f * 60:5.0f} rpm  "
          f"(工作 {args.rpm:g} rpm 是它的 {args.rpm / (f * 60):.2f}×)")
print("  ⚠ 打印 frame 本身的弯曲、柱底 M6 锁紧、电机轴承间隙都会让实际值更低 —— 必须上机扫频确认。")
