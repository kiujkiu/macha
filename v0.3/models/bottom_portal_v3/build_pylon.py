"""
portal_pylon_v3 — v3 双面屏底部支撑, C 形单件 v2 (2026-07-22 深夜六改, 用户
三视图二稿: 立柱在外侧、脚板与顶臂同向内伸 [C 形], 修正 v1 梯形壁罩住脚螺丝
无法安装的 bug)。

一件 ×2 (同件, 第二件绕 Z 转 180°), 固定屏幕底边两个螺丝孔到转子平台:
  · 脚板: X ±33.5 × Y 67..76 × Z 0..8, 2×Φ3.4 @ (±29.658, 71.601) 借盘环孔
    —— 螺丝头顶上方露天 (柱/臂/筋都在 X ±12 内, 不遮 ±29.66), 从上直装 ✓
  · 外侧立柱: X ±12 × Y 76..84 × Z 0..40 (含脚板段; 柱角 r 84.85 < R85,
    受 R85 限制柱宽 ±12 —— 手绘大三角壁在此处会超盘缘, 改窄柱+纵筋)
  · 顶臂: X ±10 × Y 58..84 × Z 40..50, 托面 Z50 = 屏底; 1×Φ3.2 @ (0, 64)
    = 屏底 ±64 螺丝孔
  · 纵向斜筋 (Y-Z 面): X ±10, 三角 (Y58,Z40)-(Y76,Z40)-(Y76,Z22), 45° 斜边
    托住悬臂 → 站立打印零支撑; 筋在 (0,64) 处开 Φ6.5 头窝通道到臂底 (Z40),
    M3×16 头藏通道内向上拧进模组底孔
  · 屏底中央孔 (0,0) 空置; 模组 = 连接左右两件的"横梁"
打印: 站立 (脚板贴床), 零支撑。BOM: 屏底 M3×16 ×2 + 脚 M3×20 ×4
(脚8+环5+hub~5.5 入 hub 底铜螺母-既有); 无接缝五金, 无攻牙件。
盘系 (Z0 = 承载面), 装配随 V3_SCR_ROT=-45°。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

FOOT_X, FOOT_Y0, FOOT_Y1, FOOT_T = 33.5, 67.0, 76.0, 8.0
FOOT_HOLES = [(29.658, 71.601), (-29.658, 71.601)]
FOOT_HOLE_D = 3.4
COL_X, COL_Y0, COL_Y1, COL_Z1 = 12.0, 76.0, 84.0, 40.0
ARM_X, ARM_Y0, ARM_Z0, ARM_Z1 = 10.0, 58.0, 40.0, 50.0
RIB_X, RIB_Y0, RIB_Z_DROP = 10.0, 58.0, 18.0     # 筋三角: (58,40)(76,40)(76,22)
SCREW_D, SCREW_Y = 3.2, 64.0
HEAD_CB_D = 6.5

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def cyl_z(d, x, y, z0, z1, seg=32):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

part = box(-FOOT_X, FOOT_X, FOOT_Y0, FOOT_Y1, 0.0, FOOT_T)          # 脚板
part += box(-COL_X, COL_X, COL_Y0, COL_Y1, 0.0, COL_Z1)             # 外侧立柱
part += box(-ARM_X, ARM_X, ARM_Y0, COL_Y1, ARM_Z0, ARM_Z1)          # 顶臂
# 纵向斜筋 (Y-Z 面三角, 沿 X 挤 ±10): (58,40)(76,40)(76,22), CCW 保证
pts = [(RIB_Y0, ARM_Z0), (COL_Y0, ARM_Z0), (COL_Y0, ARM_Z0 - RIB_Z_DROP)]
area2 = sum(pts[i][0]*(pts[(i+1) % 3][1]-pts[(i-1) % 3][1]) for i in range(3))
if area2 < 0:
    pts.reverse()
rib = m3d.CrossSection([pts]).extrude(2*RIB_X)
rib = rib.rotate((90, 0, -90)).translate((-RIB_X, 0.0, 0.0))
part += rib
# 孔
for (hx, hy) in FOOT_HOLES:
    part -= cyl_z(FOOT_HOLE_D, hx, hy, -1.0, FOOT_T + 1.0)
part -= cyl_z(SCREW_D, 0.0, SCREW_Y, ARM_Z0 - 0.001, ARM_Z1 + 1.0)   # 臂上 Φ3.2
part -= cyl_z(HEAD_CB_D, 0.0, SCREW_Y, ARM_Z0 - RIB_Z_DROP - 1.0, ARM_Z0)  # 筋内头窝通道

mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("portal_pylon_v3.stl")
with out.open("wb") as f:
    f.write(b"POV3D portal_pylon_v3 C v2 (x2, 2nd rotZ180)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
r_max = float(np.hypot(verts[:, 0], verts[:, 1]).max())
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3 (~{part.volume()*1.27/1000:.0f} g)  r_max {r_max:.2f}")
print(f"  脚板 {2*FOOT_X:g}×{FOOT_Y1-FOOT_Y0:g}×{FOOT_T:g} (2 孔露天可装); 柱 {2*COL_X:g}×{COL_Y1-COL_Y0:g} 到 Z{COL_Z1:g}")
print(f"  顶臂 {2*ARM_X:g}×{COL_Y1-ARM_Y0:g}×{ARM_Z1-ARM_Z0:g} (托面 Z{ARM_Z1:g}=屏底) + 45° 纵筋; 屏孔 Φ{SCREW_D:g}@(0,{SCREW_Y:g}) 带 Φ{HEAD_CB_D:g} 头窝通道")
print(f"  站立打印零支撑; ×2 对角; 中央孔空置, 模组为梁")
