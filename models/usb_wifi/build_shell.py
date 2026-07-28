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
import math
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

# ===== 盘缘裁切 (2026-07-27, 用户: "有个脚出来了, 要砍掉") =====
# −Y 端沿的外角原本伸到盘系 r=90.22, 悬出 Φ170 承载盘缘 (R85) 5.2 —— 是全机
# 唯一探出盘外的结构件; 加转子罩 (rotor_shroud_v3, 内壁 R82) 后更必须收回。
# 裁法 = 在盘系里用一个 R_TRIM 圆柱把壳切齐 (圆柱轴 = 转子轴)。
# 零件系→盘系映射 (见 assembly_v3 §12: rotY(+90) 倒扣 + XC/YC 平移):
#     disc_X = z_part + (WIFI_XC − WS_W/2) = z_part + 19.8
#     disc_Y = y_part + WIFI_YC            = y_part − 13
# 组转 135° 只绕轴转, 不改半径, 故裁切只与上面两式有关。
# R_TRIM 取值权衡 (2026-07-27):
#   · −Y 沿最外那颗 M3 孔中心在盘系 r=79.06, Φ4.2 沉孔边 r=81.16 —— 裁到 R81.5
#     (罩内壁 R82 完全不用让位) 只剩 0.34 料, 等于废掉该螺丝并要挪 rim_ring 沿孔;
#   · 取 R83.5: 孔外留 2.34 料, 4 颗沿螺丝全保住, rim_ring 不动;
#     罩子在该处开内壁让位窝到 R84.0 (留 1.0 皮, 同 portal_tee 脚角的处理)。
# 内腔最外角在盘系 r=79.55 < R_TRIM → 裁切不会破腔 (build 时 assert 复核)。
TRIM_R = 83.5
TRIM_CX_Z = 19.8      # 转子轴在零件系的 z 坐标 (= −(WIFI_XC − WS_W/2) 的相反数)
TRIM_CY_Y = 13.0      # 转子轴在零件系的 y 坐标 (= −WIFI_YC)

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

    # ===== 盘缘裁切 (2026-07-27): 与转子轴同心的 R_TRIM 圆柱求交 =====
    # 必须放在最后 (所有加料/挖料之后), 否则后续 union 会把切掉的角补回来。
    v_before = part.volume()
    trim = (m3d.Manifold.cylinder(400.0, TRIM_R, TRIM_R, 512, False)
            .rotate((0, 90, 0))                       # 轴 +Z → +X (平行零件系 X)
            .translate((-200.0, TRIM_CY_Y, -TRIM_CX_Z)))
    part = part ^ trim
    # 复核: 不破腔 (内腔最外角半径 < TRIM_R) + 仍是单连通体
    cav_r = max(math.hypot(z + TRIM_CX_Z, y - TRIM_CY_Y)
                for z in (IZ0, IZ1) for y in (IY0, IY1))
    assert cav_r < TRIM_R, f"裁切破腔: 腔角 r={cav_r:.2f} ≥ TRIM_R={TRIM_R}"
    n_body = len(part.decompose())
    assert n_body == 1, f"裁切把壳切成了 {n_body} 块"

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
    disc_r = np.hypot(verts[:, 2] + TRIM_CX_Z, verts[:, 1] - TRIM_CY_Y)
    print(f"  盘缘裁切 R{TRIM_R:g}: 削掉 {v_before-part.volume():.1f} mm³ "
          f"({(v_before-part.volume())/v_before*100:.1f}%), 裁后盘系 r_max {disc_r.max():.2f} "
          f"(盘缘 85 / 罩内壁 82); 内腔角 r {cav_r:.2f}, 连通体 {n_body}")

if __name__ == "__main__":
    main()
