"""
gantry_base — v2 屏幕支架两件套之二: 门形底座 (2026-07-02, 方案A 竖拆)。

修订 (2026-07-02 晚, 用户要求): 连接改 **贯通螺丝+螺母** (不用铜花螺母/自攻)。
塔柱改直背方柱 (背面竖直平面坐螺母), 两个体拆成 2 个独立 STL:
  gantry_base_A.stl (+Y 侧) / gantry_base_B.stl (−Y 侧) — 互为镜像 (左右手件,
  塔前面都朝 −X, 不能同一文件打两次; 切片里对其中一个做镜像也等价)。

每件:
  • 脚: 4 厚, X ±36 × Y 63.5..83.5, 外缘平直 (2026-07-03 下午: 原 R85 弧裁边
    改平; 四角伸出盘边, 旋转半径 85→90.9); 2×Φ3.2
    借用盘 R77.5 环孔 @ (±29.658, 71.601) — M3 穿 脚+盘+rim_ring 锁紧。
  • 塔柱: 直背方柱, 宽 15 (Y 63.5..78.5) × 深 10 (X -23.27..-13.27), Z 4..90;
    前面 X=-13.27 贴 screen_plate 背面, 背面平面坐螺母。
    (2026-07-03: 原底部加强墩删除 — 它压住了后侧脚孔 (-29.66,±71.6),
     脚螺丝必须从上往下打; 塔背 -23.27 距垫片区边缘 -26.16 有 2.9 余量 ✓)
  • 外侧筋墙 = 满三角 (2026-07-03 下午最终版, 用户要求"拉平这一面, 打印以此面为底"):
    5 厚 (Y 78.5..83.5, 外面与脚外缘共面 = 打印底面), 轮廓 = 塔顶两条直边拉到
    脚两端: (-36,4)-(36,4)-(-13.27,90)-(-23.27,90)。配套: screen_plate 宽 162→156
    (±78, 给筋墙留 0.5); 原内侧 2.5 小筋删除 (侧躺打印会悬空, 且被大三角取代)。
    避开脚螺丝垫片区 (Y≤75.1, 留3.4) 和塔背螺母 (Y≤74.5, 留4)。
  • 3 × Φ3.2 贯通连接孔 @ (Y 71, Z {28,56,84}): 普通 M3×18/20 从板前面穿过
    板(6)+塔(10)=16, 背面出头 2~4, 套垫片+M3 螺母。全部平面通孔, 无嵌件无沉头。

打印: 侧躺 — 外侧面 (筋墙面+脚外缘, Y=±83.5 平面) 朝下贴床, 全件被支撑,
零支撑, 层线顺三角面 (最强)。切片时把件绕 X 转 90°/-90° 即可。
局部坐标系 = 盘坐标系, Z0 = 盘顶面。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== 共享参数 (与 build_plate.py 一致) =====
SCREEN_T = 7.27
FIN_T    = 6.0
FIN_X0   = -SCREEN_T - FIN_T     # -13.27 塔柱前面 (= 板背面)
M3 = 3.2

FOOT_T   = 4.0
FOOT_HX  = 36.0
FOOT_Y0, FOOT_Y1 = 63.5, 83.5    # 外缘平直 (原 R85 弧裁已改平)
DISC_R   = 85.0                   # 仅作参考
RIM_R    = 77.5
FOOT_ANGS = (67.5, 112.5)

TWR_Y0, TWR_Y1 = 63.5, 78.5      # 塔宽 15, 中心 71
TWR_TOP  = 90.0
TWR_D    = 10.0                   # 塔深 (直背)
TWR_XB   = FIN_X0 - TWR_D         # -23.27 背面 (平面, 坐螺母)
WALL_T   = 5.0                    # 外侧筋墙厚 (Y 78.5..83.5, 外面与脚外缘共面)
WALL_PTS = [(-36.0, 4.0), (36.0, 4.0), (-13.27, 90.0), (-23.27, 90.0)]  # 满三角 (CCW)
JOINT_Y  = 71.0
JOINT_Z  = [28.0, 56.0, 84.0]

def xcyl(d, x0, x1, y, z, seg=32):
    return m3d.Manifold.cylinder(x1 - x0, d/2, d/2, seg, False)\
        .rotate((0, 90, 0)).translate((x0, y, z))

def build_piece(s):
    """s=+1 → A (+Y 侧); s=-1 → B (−Y 侧, 镜像)。"""
    # 脚 (矩形, 外缘平直)
    f = m3d.Manifold.cube((2*FOOT_HX, FOOT_Y1 - FOOT_Y0, FOOT_T), False)\
        .translate((-FOOT_HX, min(s*FOOT_Y0, s*FOOT_Y1), 0.0))
    # 塔柱: XZ 矩形 (CCW) → 挤出 Y 宽 15
    prof = m3d.CrossSection([[(TWR_XB, FOOT_T), (FIN_X0, FOOT_T), (FIN_X0, TWR_TOP),
                              (TWR_XB, TWR_TOP)]])
    twr = prof.extrude(TWR_Y1 - TWR_Y0).rotate((90, 0, 0))         # (x,z,t)→(x,-t,z), y∈[-15,0]
    twr = twr.translate((0.0, TWR_Y1 if s > 0 else -TWR_Y0, 0.0))
    # 外侧筋墙: 满三角, 塔顶直边拉到脚两端 (贴塔外面, 外面与脚外缘共面 = 打印底面)
    wall = m3d.CrossSection([WALL_PTS]).extrude(WALL_T).rotate((90, 0, 0))   # y∈[-5,0]
    wall = wall.translate((0.0, FOOT_Y1 if s > 0 else -TWR_Y1, 0.0))
    piece = f + twr + wall
    # 2 脚孔
    for a in FOOT_ANGS:
        hx = RIM_R * math.cos(math.radians(a)); hy = s * RIM_R * math.sin(math.radians(a))
        piece = piece - m3d.Manifold.cylinder(FOOT_T + 2, M3/2, M3/2, 32, False)\
            .translate((hx, hy, -1))
    # 3 贯通连接孔
    for z in JOINT_Z:
        piece = piece - xcyl(M3, TWR_XB - 1, FIN_X0 + 1, s * JOINT_Y, z)
    return piece

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

A = build_piece(+1.0)
B = build_piece(-1.0)
write_stl(A, "gantry_base_A.stl")
write_stl(B, "gantry_base_B.stl")
print(f"  塔柱 15宽×{TWR_D:g}深 (X {FIN_X0:g}..{TWR_XB:g}) Z {FOOT_T:g}..{TWR_TOP:g}; "
      f"外侧筋墙 {WALL_T:g}厚 满三角 {WALL_PTS} (内侧小筋已删)")
print("  打印: 侧躺, 外侧面 (Y=±83.5) 贴床, 零支撑")
print(f"  连接孔 Φ{M3:g} 贯通 (Y ±{JOINT_Y:g}, Z {JOINT_Z}); 板6+塔{TWR_D:g}=16 → M3×18/20 + 垫片 + 螺母")
print(f"  脚孔 (±{RIM_R*math.cos(math.radians(67.5)):.3f}, ±{RIM_R*math.sin(math.radians(67.5)):.3f})")
print("  A=+Y 件 / B=−Y 件, 互为镜像 (左右手件)")
