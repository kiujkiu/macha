"""
screen_plate_v3 — v3 双面屏支架两件套之一: 屏幕板 (2026-07-10)。

v3 相对 l_bracket_v2/screen_plate 的改动 (双面屏, 背靠背对称):
  • 板居中到轴平面: X -3..+3 (厚 6 不变)。两块屏分别贴两面:
    前屏 X -10.27..-3 (LED 面 -10.27 朝 -X), 后屏 X +3..+10.27 (LED 面 +10.27 朝 +X)。
  • 宽 156→176 (±88): 塔柱移到屏幕宽度之外 (Y 76..88), 板加宽到塔外缘。
  • 顶部加中央凸舌 (±40 × Z 213.5..235, 伸到屏顶 219 之上): top_cap_v3 双腿
    夹舌, 4×Φ3.2 @ (±22, Z {225.3, 230.8}) M3×18 贯通 腿4+板6+腿4=14 锁死。
    (v2 帽借屏顶螺母孔的做法失效 —— 板两面都是屏, 帽腿没处贴。)
  • 4×Φ3.2 屏幕孔位置同 v2, 但 **两侧共用**: 每孔两颗 M3 对头拧进各自屏的
    自带螺母, 螺杆侵入板内各 ≤2.5 (合计 <6) 不相碰 → 按屏螺母高度选短螺丝
    (如 M3×6/8)。下排 (±52.5, 60.5) 上排 (±49.975, 207.5)。
  • 接口窗 (±27 × 93..127 + R27 拱) 两屏共用: 两屏接口 (各占位凸 6) 相向伸进
    同一窗 —— 若实测凸出 >3, 两侧各加尼龙垫柱增大屏-板间隙 (待实测)。
  • 6×底座连接孔移到 (±82, Z {28,56,84}) 随塔柱外移; 底部中央让位缺口
    (±60 × 21..50) 不变。

平躺打印 (任一面朝下, 层纹顺板面), 全部竖直通孔免支撑。
局部坐标系 = 盘坐标系 (未转45°), Z0 = 盘顶面; 翼板底边 Z21。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 共享参数 (与 build_gantry.py / build_cap.py 一致) =====
FIN_T      = 6.0
FIN_X0     = -FIN_T / 2          # -3 (居中)
FIN_X1     = +FIN_T / 2          # +3
FIN_HW     = 88.0                # 半宽 (156→176, 塔柱外移)
SCREEN_LIFT = 50.0               # 屏底沿距盘面
PLATE_Z0   = 21.0                # 翼板底边 (堆叠顶 + 余量)
NOTCH_HW, NOTCH_TOP = 60.0, 50.0 # 板底中央让位缺口
FIN_TOP    = SCREEN_LIFT + 10.5 + 147.0 + 6.0   # 213.5
TAB_HW     = 40.0                # 顶部凸舌半宽
TAB_TOP    = 235.0               # 凸舌顶 (屏顶 219 之上; 帽板底 238 留 3)
CAP_HOLE_Y = 22.0
CAP_HOLE_Z = [225.3, 230.8]      # (装配系 271.0 / 276.5)
WIN_HW = 27.0
WIN_Z0, WIN_Z1 = SCREEN_LIFT + 60.0 - 17.0, SCREEN_LIFT + 60.0 + 17.0   # 93..127
M3 = 3.2
SCREEN_HOLES = [(-52.5, SCREEN_LIFT+10.5), (52.5, SCREEN_LIFT+10.5),
                (-49.975, SCREEN_LIFT+157.5), (49.975, SCREEN_LIFT+157.5)]
JOINT_Y  = 82.0                  # 连接孔 Y (= 塔柱中心, 71→82)
JOINT_Z  = [28.0, 56.0, 84.0]

SEG = 96

# ---- 板体: (Y,Z) 轮廓 → 沿 X 挤出 ----
plate_cs = m3d.CrossSection([[(-FIN_HW, PLATE_Z0), (FIN_HW, PLATE_Z0),
                              (FIN_HW, FIN_TOP), (-FIN_HW, FIN_TOP)]])
tab_cs = m3d.CrossSection([[(-TAB_HW, FIN_TOP - 1.0), (TAB_HW, FIN_TOP - 1.0),
                            (TAB_HW, TAB_TOP), (-TAB_HW, TAB_TOP)]])
win = m3d.CrossSection([[(-WIN_HW, WIN_Z0), (WIN_HW, WIN_Z0),
                         (WIN_HW, WIN_Z1), (-WIN_HW, WIN_Z1)]]) + \
      m3d.CrossSection.circle(WIN_HW, SEG).translate((0.0, WIN_Z1))
notch = m3d.CrossSection([[(-NOTCH_HW, PLATE_Z0-1), (NOTCH_HW, PLATE_Z0-1),
                           (NOTCH_HW, NOTCH_TOP), (-NOTCH_HW, NOTCH_TOP)]])
plate_cs = plate_cs + tab_cs - win - notch
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
for z in CAP_HOLE_Z:
    for s in (1.0, -1.0):
        plate = plate - xcyl(M3, FIN_X0 - 1, FIN_X1 + 1, s * CAP_HOLE_Y, z)

# ===== export =====
mesh = plate.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("screen_plate_v3.stl")
_hdr = b"POV3D screen_plate_v3"
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
print(f"  plate Y ±{FIN_HW:g} × Z {PLATE_Z0:g}..{FIN_TOP:g} × X {FIN_X0:g}..{FIN_X1:g} (居中)")
print(f"  顶舌 ±{TAB_HW:g} × Z {FIN_TOP:g}..{TAB_TOP:g}; 帽孔 (±{CAP_HOLE_Y:g}, {CAP_HOLE_Z})")
print(f"  screen holes {SCREEN_HOLES} (两侧共用, 对头短螺丝)")
print(f"  joint holes (±{JOINT_Y:g}, {JOINT_Z}) Φ{M3:g} 直通")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
      f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
print("  打印: 平躺, 全部竖直通孔, 免支撑 (176×214 < X2D 256²)")
