"""
wifi_shell — 新 WiFi 壳子 v1 (2026-07-21, 用户手动改造中; 与旧 wifi_box 并存)。

五面盒: 内腔 15.1(X 宽) × 70.6(Y 长) × 40.4(Z 高), 壁厚 3,
缺的面 = 一个 70.6×40.4 的 X 侧面 (开口朝 +X, 模块侧向滑入)。
+Y 端壁 (15.1×40.4 那条边) 保留 USB 母头出口窗 10.7×19.1
(= 母头壳截面 10.3×18.7 +0.4, 中心在腔 X 中线、模块口轴线高 Z=腔底+20)。

零件系: Z0 = 外底面, 腔底 Z=3; X0 = 封闭壁外面, 开口在 X=18.1;
Y 对称 ±38.3。装配位/固定方式待定 (用户手动排), 先出几何。
参数在模块顶层, build_drawing_shell.py 直接 import 取数 (免双份同步)。

2026-07-21 (用户切片图红标 + 更正: 沿在开口面一侧, 与缺的面共面):
±Y 两端壁各加一条外伸 10 的沿 (3 厚, X 15.1..18.1 与开口面共面, 全宽 46.4),
每条沿 2×Φ3.2 M3 通孔 (孔轴沿 X, 距壁外面 5, 沿宽向 c-c 25 居中)
+ 2 条三角加强筋 (2.5 厚, 45° 斜靠端壁, 从沿内面 X15.1 沿壁到 X5.1,
贴沿的两条宽向端边; +Y 侧筋避开出口窗 Z13.45..32.55 ✓, 垫片区 Φ7 距筋 ≥2.2 ✓)。
安装姿态 = 倒扣: 开口/沿朝下贴盘, 模块放平 (40×70 面贴盘, 14.5 高) 被罩住;
窗 10.7(此姿态竖直)×19.1(水平) 正对放平母头壳 10.3 高×18.7 宽。
打印按安装姿态 (沿贴床), 筋 45° 零支撑。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 参数 =====
CAV_X, CAV_Y, CAV_Z = 15.1, 70.6, 40.4   # 内腔 (含模块 14.5×70×40 的既有间隙)
WALL = 3.0

# 内腔范围 (零件系)
IX0, IX1 = WALL, WALL + CAV_X            # X 3 .. 18.1 (开口面 = X=IX1, 无壁)
IY0, IY1 = -CAV_Y / 2, CAV_Y / 2         # Y ±35.3
IZ0, IZ1 = WALL, WALL + CAV_Z            # Z 3 .. 43.4

# 外廓 (开口侧无壁)
OX0, OX1 = 0.0, IX1                      # X 0 .. 18.1
OY0, OY1 = IY0 - WALL, IY1 + WALL        # Y ±38.3
OZ0, OZ1 = 0.0, IZ1 + WALL               # Z 0 .. 46.4

# +Y 端壁母头出口窗: 10.7 宽(X) × 19.1 高(Z)
# 2026-07-22 对准放平模块 (侧立遗留修正): X 中心 10.55(腔中线) → 10.85
# (= OX1 − 14.5/2, 放平模块口轴线, 倒扣后离盘 7.25); Z 中心 23(腔底+20, 侧立
# 算法) → 23.2 (腔 Z 中线 = 放平模块宽向中线)。母头 10.3×18.7 四周余量 ±0.2。
# 窗口开槽切穿 +Y 沿板 (窗 X 5.5..16.2 与沿 15.1..18.1 交叠 1.1 → 沿上过缺口,
# 否则沿顶(倒扣后离盘 3)挡住母头底(2.1))。
WIN_W, WIN_H = 10.7, 19.1
WIN_XC = OX1 - 14.5 / 2                  # 10.85
WIN_ZC = (IZ0 + IZ1) / 2                 # 23.2

# ±Y 端沿 (2026-07-21, 与开口面共面): 3 厚 (X 15.1..18.1), 外伸 10, 全宽 Z 0..46.4
FLG_L, FLG_T = 10.0, 3.0                 # 外伸 / 厚
FLG_X0 = OX1 - FLG_T                     # 15.1 (沿内面)
FLG_Y1 = OY1 + FLG_L                     # 48.3 (−Y 侧对称)
# 每沿 2×Φ3.2 M3 通孔, 孔轴沿 X: 距壁外面 5, 沿宽向 c-c 25 (绕 Z 中面对称)
M3_D = 3.2
HOLE_YC = OY1 + 5.0                      # 43.3 (±)
HOLE_CC = 25.0
HOLE_ZS = ((OZ1 - OZ0) / 2 - HOLE_CC / 2, (OZ1 - OZ0) / 2 + HOLE_CC / 2)  # 10.7 / 35.7
# 每沿 2 条三角加强筋: 2.5 厚, 45° (臂 10, X 5.1..15.1), 贴沿的两条宽向端边
GUS_T, GUS_ARM = 2.5, 10.0
GUS_ZS = (0.0, OZ1 - GUS_T)              # 筋 Z 带: 0..2.5 / 43.9..46.4

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))

def gusset(y_wall, y_out, z0):
    """三角筋 (X-Y 平面直角三角形, 沿 Z 挤出 GUS_T): 从沿内面 X=FLG_X0 沿端壁
    45° 到 X=FLG_X0−GUS_ARM。CCW 保证 (CW → CrossSection 为空)。"""
    pts = [(FLG_X0, y_wall), (FLG_X0, y_out), (FLG_X0 - GUS_ARM, y_wall)]
    area2 = sum(pts[i][0] * (pts[(i + 1) % 3][1] - pts[(i - 1) % 3][1]) for i in range(3))
    if area2 < 0:
        pts.reverse()
    return m3d.CrossSection([pts]).extrude(GUS_T).translate((0.0, 0.0, z0))

def main():
    # ===== 实体: 外块 − 内腔 (腔向开口侧多挖 1 保证贯通) =====
    part = box(OX0, OX1, OY0, OY1, OZ0, OZ1) - box(IX0, IX1 + 1.0, IY0, IY1, IZ0, IZ1)

    # ===== ±Y 端沿 + 三角筋 + M3 孔 (2026-07-21, 沿与开口面共面) =====
    part += box(FLG_X0, OX1, OY1, FLG_Y1, OZ0, OZ1)          # +Y 沿
    part += box(FLG_X0, OX1, -FLG_Y1, OY0, OZ0, OZ1)         # -Y 沿
    for z0 in GUS_ZS:
        part += gusset(OY1, FLG_Y1, z0)                      # +Y 筋 ×2
        part += gusset(OY0, -FLG_Y1, z0)                     # -Y 筋 ×2
    for zc in HOLE_ZS:                                       # 4× M3 通孔 (孔轴沿 X)
        for yc in (HOLE_YC, -HOLE_YC):
            h = m3d.Manifold.cylinder(FLG_T + 2.0, M3_D / 2, M3_D / 2, 32, False)
            part -= h.rotate((0, 90, 0)).translate((FLG_X0 - 1.0, yc, zc))

    # +Y 端壁出口窗 (穿墙 + 切穿 +Y 沿板, 给放平母头让出下方通道) —— 必须在
    # 加完沿板之后再挖, 否则沿板会把沿上的过缺口填回去 (2026-07-22 教训)
    part -= box(WIN_XC - WIN_W / 2, WIN_XC + WIN_W / 2, IY1 - 1.0, FLG_Y1 + 1.0,
                WIN_ZC - WIN_H / 2, WIN_ZC + WIN_H / 2)

    # ===== export =====
    mesh = part.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name("wifi_shell.stl")
    with out.open("wb") as f:
        f.write(b"POV3D wifi_shell v1 (5-face, side-open)".ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
            if L > 0: n = n / L
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    assert 84 + len(tris) * 50 == out.stat().st_size
    print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3 (~{part.volume()*1.27/1000:.0f} g PETG)")
    print(f"  盒体外廓 {OX1-OX0:g} × {OY1-OY0:g} × {OZ1-OZ0:g}  (X {OX0:g}..{OX1:g}, Y ±{OY1:g}, Z {OZ0:g}..{OZ1:g})")
    print(f"  总包络 (含沿) X {verts[:,0].min():g}..{verts[:,0].max():g}  Y ±{verts[:,1].max():g}  Z {verts[:,2].min():g}..{verts[:,2].max():g}")
    print(f"  内腔 {CAV_X:g} × {CAV_Y:g} × {CAV_Z:g}  (X {IX0:g}..{IX1:g}, Y ±{IY1:g}, Z {IZ0:g}..{IZ1:g})")
    print(f"  开口面 = X={IX1:g} 侧 ({CAV_Y:g}×{CAV_Z:g}); 壁厚 {WALL:g}")
    print(f"  +Y 端壁出口窗 {WIN_W:g}×{WIN_H:g} @ (X{WIN_XC:g}, Z{WIN_ZC:g})")
    print(f"  ±Y 端沿: 外伸 {FLG_L:g} × 厚 {FLG_T:g} (X {FLG_X0:g}..{OX1:g}, 与开口面共面, 全宽 {OZ1-OZ0:g}), 至 Y ±{FLG_Y1:g}")
    print(f"  4×Φ{M3_D:g} 通 (孔轴沿 X) @ Y ±{HOLE_YC:g} (距壁 5), Z {HOLE_ZS[0]:g}/{HOLE_ZS[1]:g} (c-c {HOLE_CC:g})")
    print(f"  三角筋 ×4: {GUS_T:g} 厚, 45° 臂 {GUS_ARM:g} (X {FLG_X0-GUS_ARM:g}..{FLG_X0:g}), Z 带 {GUS_ZS[0]:g}..{GUS_ZS[0]+GUS_T:g} / {GUS_ZS[1]:g}..{GUS_ZS[1]+GUS_T:g}")

if __name__ == "__main__":
    main()
