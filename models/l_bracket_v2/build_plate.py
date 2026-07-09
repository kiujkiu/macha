"""
screen_plate — v2 屏幕支架两件套之一: 屏幕板 (2026-07-02, 方案A 竖拆)。

矩形平板 156(Y)×192.5(Z 21..213.5)×6(X -13.27..-7.27), 平躺打印(前面朝下贴板,
层纹顺板面 = 抗弯最强)。前面 X=-7.27 贴屏幕背面 (LED 面在轴平面 X=0)。
(2026-07-03 下午: 宽 162→156 (±78) — 给 gantry_base 满三角筋墙 (Y 78.5 起) 留 0.5。)
(2026-07-03 深夜, 用户要求: 屏幕底沿抬到 盘面+50 (SCREEN_LIFT 40→50); 且板的
 中间 120 宽 (|Y|≤60) 下缘也 ≥盘面+50 → 板底中央开 ±60×(21..50) 让位缺口,
 两侧翼板仍下伸到 Z21 连塔柱。缺口顶 50 与屏下排孔 60.5 相距 10.5 ✓)
局部坐标系 = 盘坐标系 (未转45°), Z0 = 盘顶面; 翼板底边 Z21 (堆叠顶 17.9 + 3.1)。

特征:
  • 4 × Φ3.2 屏幕孔 (M3 从背面穿入拧进屏上螺母):
      下排 (±52.5, Z60.5) 上排 (±49.975, Z207.5)  [屏底沿 Z50 + 10.5 / +157.5]
  • 接口窗: Y ±27 × Z 93..127 + 顶 R27 半圆拱 (屏底+60 中心)
  • 6 × 底座连接孔 (±71, Z {28,56,84}): Φ3.2 普通直通孔 (无沉头, 用户 2026-07-03
    要求; M3×18/20 贯通 板6+塔10, 塔背面垫片+M3螺母锁死。螺丝头在板前面凸出
    ~2mm — 屏幕背面靠自带螺母垫起, 不干涉)
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 共享参数 (与 build_base.py 一致) =====
SCREEN_T   = 7.27
FIN_T      = 6.0
FIN_X1     = -SCREEN_T           # -7.27 前面
FIN_X0     = FIN_X1 - FIN_T      # -13.27 背面 (= 塔柱前面)
FIN_HW     = 78.0   # 半宽 (162→156, 让位筋墙)
SCREEN_LIFT = 50.0               # 屏底沿距盘面 (40→50, 2026-07-03 深夜)
PLATE_Z0   = 21.0                # 翼板底边 (堆叠顶 17.9 + 3.1)
NOTCH_HW, NOTCH_TOP = 60.0, 50.0 # 板底中央让位缺口: |Y|≤60 (12cm, 2026-07-03), 到 盘面+50
FIN_TOP    = SCREEN_LIFT + 10.5 + 147.0 + 6.0   # 213.5
WIN_HW = 27.0
WIN_Z0, WIN_Z1 = SCREEN_LIFT + 60.0 - 17.0, SCREEN_LIFT + 60.0 + 17.0   # 93..127
M3 = 3.2
SCREEN_HOLES = [(-52.5, SCREEN_LIFT+10.5), (52.5, SCREEN_LIFT+10.5),
                (-49.975, SCREEN_LIFT+157.5), (49.975, SCREEN_LIFT+157.5)]
JOINT_Y  = 71.0                  # 连接孔 Y (= 塔柱中心)
JOINT_Z  = [28.0, 56.0, 84.0]

SEG = 96

# ---- 板体: (Y,Z) 轮廓 → 沿 X 挤出 ----
plate_cs = m3d.CrossSection([[(-FIN_HW, PLATE_Z0), (FIN_HW, PLATE_Z0),
                              (FIN_HW, FIN_TOP), (-FIN_HW, FIN_TOP)]])
win = m3d.CrossSection([[(-WIN_HW, WIN_Z0), (WIN_HW, WIN_Z0),
                         (WIN_HW, WIN_Z1), (-WIN_HW, WIN_Z1)]]) + \
      m3d.CrossSection.circle(WIN_HW, SEG).translate((0.0, WIN_Z1))
notch = m3d.CrossSection([[(-NOTCH_HW, PLATE_Z0-1), (NOTCH_HW, PLATE_Z0-1),
                           (NOTCH_HW, NOTCH_TOP), (-NOTCH_HW, NOTCH_TOP)]])
plate_cs = plate_cs - win - notch
plate = plate_cs.extrude(FIN_T).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((FIN_X0, 0, 0))

# ---- 孔 (轴向 +X) ----
def xcyl(d, x0, x1, y, z, seg=32):
    return m3d.Manifold.cylinder(x1 - x0, d/2, d/2, seg, False)\
        .rotate((0, 90, 0)).translate((x0, y, z))

for (y, z) in SCREEN_HOLES:
    plate = plate - xcyl(M3, FIN_X0 - 1, FIN_X1 + 1, y, z)
for z in JOINT_Z:
    for s in (1.0, -1.0):
        plate = plate - xcyl(M3, FIN_X0 - 1, FIN_X1 + 1, s * JOINT_Y, z)

# ===== export =====
mesh = plate.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("screen_plate.stl")
_hdr = b"POV3D screen_plate"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80]); f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris) * 50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)  vol {plate.volume()/1000:.1f} cm3")
print(f"  plate Y ±{FIN_HW:g} × Z {PLATE_Z0:g}..{FIN_TOP:g} × X {FIN_X0:g}..{FIN_X1:g}")
print(f"  screen holes {SCREEN_HOLES}")
print(f"  joint holes (±{JOINT_Y:g}, {JOINT_Z}) Φ{M3:g} 直通 (无沉头)")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
      f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
print("  打印: 平躺, 前面(X=-7.27 面)朝下贴板; 全部竖直通孔, 免支撑")
