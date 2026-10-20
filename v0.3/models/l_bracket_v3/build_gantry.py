"""
gantry_v3 — v3 双面屏支架两件套之二: 门形底座 (2026-07-10)。

v3 相对 l_bracket_v2/gantry_base 的改动 (双面屏, screen_plate 居中 X ±3):
  • 塔柱不能再贴板背面 (那里现在是屏幕) → 整个塔柱移到屏幕宽度之外:
    Y 76..88 (宽 12, 中心 82; 屏边 ±75 留 1mm), X -13..-3 (深 10 不变,
    前面 X=-3 贴 screen_plate_v3 板面)。
  • A/B 不再是镜像左右手件 —— 改成 **同一件打印 2 次**, 装配时对角放:
    件1 脚在 +Y (塔在 -X 侧), 件2 = 件1 绕 Z 转 180° (脚 -Y, 塔 +X 侧)。
    180° 旋转对称 → 转子动平衡好; 盘 R77.5 环孔是 45° 阵列, 转 180° 后
    脚孔仍落在既有孔上, 盘不用改。
  • 脚: 4 厚, X ±36 × Y 63.5..93 (外缘随筋墙外移 83.5→93, 旋转半径 99.7);
    2×Φ3.2 借盘 R77.5 环孔 @ (±29.658, 71.601), 同 v2。
  • 外侧筋墙 = 满三角 5 厚 (Y 88..93, 外面与脚外缘共面 = 打印底面),
    轮廓 (-36,4)-(36,4)-(-3,90)-(-13,90)。
  • 3×Φ3.2 贯通连接孔 @ (Y 82, Z {28,56,84}): M3×18/20 贯通 板6+塔10=16,
    塔背垫片+螺母, 同 v2 (螺丝头在板面凸 ~2mm, 位于 Y82 > 屏边 75, 不碰屏)。

打印: 侧躺, 外侧面 (Y=93 平面) 朝下贴床, 零支撑。同一件打 2 次。
局部坐标系 = 盘坐标系, Z0 = 盘顶面。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 共享参数 (与 build_plate.py 一致) =====
PLATE_HT = 3.0                    # 板半厚 (板 X -3..+3)
FIN_X0   = -PLATE_HT              # -3 塔柱前面 (= 板面)
M3 = 3.2

FOOT_T   = 4.0
FOOT_HX  = 36.0
FOOT_Y0, FOOT_Y1 = 63.5, 93.0    # 外缘随筋墙外移
RIM_R    = 77.5
FOOT_ANGS = (67.5, 112.5)

TWR_Y0, TWR_Y1 = 76.0, 88.0      # 塔宽 12, 中心 82 (屏边 75 留 1)
TWR_TOP  = 90.0
TWR_D    = 10.0                   # 塔深 (直背)
TWR_XB   = FIN_X0 - TWR_D         # -13 背面 (平面, 坐螺母)
WALL_T   = 5.0                    # 外侧筋墙厚 (Y 88..93, 外面与脚外缘共面)
WALL_PTS = [(-36.0, 4.0), (36.0, 4.0), (-3.0, 90.0), (-13.0, 90.0)]  # 满三角 (CCW)
JOINT_Y  = 82.0                   # = 塔柱中心
JOINT_Z  = [28.0, 56.0, 84.0]

def xcyl(d, x0, x1, y, z, seg=32):
    return m3d.Manifold.cylinder(x1 - x0, d/2, d/2, seg, False)\
        .rotate((0, 90, 0)).translate((x0, y, z))

# 脚 (矩形, 外缘平直)
piece = m3d.Manifold.cube((2*FOOT_HX, FOOT_Y1 - FOOT_Y0, FOOT_T), False)\
    .translate((-FOOT_HX, FOOT_Y0, 0.0))
# 塔柱: XZ 矩形 (CCW) → 挤出 Y 宽 12
prof = m3d.CrossSection([[(TWR_XB, FOOT_T), (FIN_X0, FOOT_T), (FIN_X0, TWR_TOP),
                          (TWR_XB, TWR_TOP)]])
twr = prof.extrude(TWR_Y1 - TWR_Y0).rotate((90, 0, 0))   # (x,z,t)→(x,-t,z)
piece = piece + twr.translate((0.0, TWR_Y1, 0.0))         # y ∈ [76, 88]
# 外侧筋墙: 满三角, 塔顶直边拉到脚两端 (外面与脚外缘共面 = 打印底面)
wall = m3d.CrossSection([WALL_PTS]).extrude(WALL_T).rotate((90, 0, 0))
piece = piece + wall.translate((0.0, FOOT_Y1, 0.0))       # y ∈ [88, 93]
# 2 脚孔 (借盘 R77.5 环孔)
for a in FOOT_ANGS:
    hx = RIM_R * math.cos(math.radians(a)); hy = RIM_R * math.sin(math.radians(a))
    piece = piece - m3d.Manifold.cylinder(FOOT_T + 2, M3/2, M3/2, 32, False)\
        .translate((hx, hy, -1))
# 3 贯通连接孔
for z in JOINT_Z:
    piece = piece - xcyl(M3, TWR_XB - 1, FIN_X0 + 1, JOINT_Y, z)

def write_stl(man, name):
    mesh = man.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    out = Path(__file__).with_name(name)
    with out.open("wb") as fo:
        fo.write(f"POV3D {name[:-4]}".encode().ljust(80, b" ")[:80])
        fo.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
            if L > 0: n = n / L
            fo.write(struct.pack("<3f", *n))
            fo.write(struct.pack("<3f", *v0)); fo.write(struct.pack("<3f", *v1)); fo.write(struct.pack("<3f", *v2))
            fo.write(struct.pack("<H", 0))
    assert 84 + len(tris) * 50 == out.stat().st_size
    print(f"wrote {out} ({len(tris)} tris)  vol {man.volume()/1000:.1f} cm3  "
          f"bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
          f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")

write_stl(piece, "gantry_v3.stl")
print(f"  塔柱 12宽×{TWR_D:g}深 (X {TWR_XB:g}..{FIN_X0:g}, Y {TWR_Y0:g}..{TWR_Y1:g}) Z {FOOT_T:g}..{TWR_TOP:g}")
print(f"  外侧筋墙 {WALL_T:g}厚 满三角 {WALL_PTS}")
print(f"  连接孔 Φ{M3:g} 贯通 (Y {JOINT_Y:g}, Z {JOINT_Z}); 板6+塔{TWR_D:g}=16 → M3×18/20 + 垫片 + 螺母")
print(f"  脚孔 (±{RIM_R*math.cos(math.radians(67.5)):.3f}, {RIM_R*math.sin(math.radians(67.5)):.3f}); "
      f"旋转半径 {math.hypot(FOOT_HX, FOOT_Y1):.1f}")
print("  打印: 侧躺, 外侧面 (Y=93) 贴床, 零支撑; 同一件打 2 次, 装配对角放 (件2 绕 Z 转 180°)")
