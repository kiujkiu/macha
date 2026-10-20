"""
vane_clip_v3 — v3 光电挡光片夹块 (2026-07-23, 光电大改: 传感器搬到顶部压条上,
静止挡光片从顶架臂倒挂; 本件 = 夹在 frame_A_v3 臂上的 U 形夹 + 下垂刀片)。

frame 臂截面: 18 宽 × 8 厚, 顶面中央有 4 宽×6 高的筋 (臂底平, 可夹)。
局部系: X = 沿臂 (径向, 装配时 X0 → r30), Y = 臂宽向 (±), Z0 = 臂底面
(asm = POST_H = 290)。

  · 底板: X 0..12 × Y ±12 × Z −2..0 (贴臂底)
  · 两颊: Y ±(9..12) × X 0..12 × Z −2..10 (贴臂两侧, 上到臂顶+2)
  · 内钩唇: Y ±(4..9) × X 0..12 × Z 8..10 (扣住臂顶面, 避开中央筋 ±2)
  · M3 贯穿孔: 沿 Y @ (X6, Z−1) 穿 底板+两颊, M3×30+螺母 锁紧 (无攻牙)
  · 刀片: X 0..4 (径向薄 4, 中心 r32) × Y ±4 (切向 8) × Z −10..−2
    (下垂到 asm 280, 探入光电槽; 光轴 ~282.4, 叉顶 285.65)
打印: 侧躺 (X=0 面贴床) — 全特征为沿 X 棱柱, 落床零支撑。
装配: 卡上臂后拧 M3; 安装角 = 索引角 (默认挂 135° 方向的 frame_A 臂)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

CLIP_L = 12.0
PLATE_Y, PLATE_T = 12.0, 2.0        # 底板半宽 / 厚
CHEEK_Y0, CHEEK_Y1 = 9.0, 12.0      # 颊 (臂宽 18 → ±9 外贴)
CHEEK_Z1 = 10.0
LIP_Y0, LIP_Y1, LIP_Z0 = 4.0, 9.0, 8.0   # 内钩唇 (臂顶 8, 筋 ±2)
BOLT_Z, BOLT_X, BOLT_D = -1.0, 6.0, 3.2
BLade = None
BLADE_L, BLADE_HW, BLADE_Z0 = 4.0, 4.0, -10.0   # 刀片: X 0..4, Y ±4, Z −10..−2

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

part = box(0, CLIP_L, -PLATE_Y, PLATE_Y, -PLATE_T, 0.0)                  # 底板
part += box(0, CLIP_L, CHEEK_Y0, CHEEK_Y1, -PLATE_T, CHEEK_Z1)           # +Y 颊
part += box(0, CLIP_L, -CHEEK_Y1, -CHEEK_Y0, -PLATE_T, CHEEK_Z1)         # -Y 颊
part += box(0, CLIP_L, LIP_Y0, LIP_Y1, LIP_Z0, CHEEK_Z1)                 # +Y 唇
part += box(0, CLIP_L, -LIP_Y1, -LIP_Y0, LIP_Z0, CHEEK_Z1)               # -Y 唇
part += box(0, BLADE_L, -BLADE_HW, BLADE_HW, BLADE_Z0, -PLATE_T)         # 刀片
bolt = m3d.Manifold.cylinder(2*CHEEK_Y1 + 2, BOLT_D/2, BOLT_D/2, 32, False)
part -= bolt.rotate((-90, 0, 0)).translate((BOLT_X, -CHEEK_Y1 - 1, BOLT_Z))

mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("vane_clip_v3.stl")
with out.open("wb") as f:
    f.write(b"POV3D vane_clip_v3 (static, on frame arm)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
comps = None
v = tris.reshape(-1, 3) if False else None
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.2f} cm3 (~{part.volume()*1.27/1000:.1f} g)")
print(f"  夹 12 长 (r30..42), 底板±{PLATE_Y:g}/颊±{CHEEK_Y0:g}..{CHEEK_Y1:g}/唇±{LIP_Y0:g}..{LIP_Y1:g}; 刀片 {BLADE_L:g}×{2*BLADE_HW:g} 下垂到 Z{BLADE_Z0:g} (asm 280)")
print(f"  M3×30+螺母 @ (X{BOLT_X:g}, Z{BOLT_Z:g}) 沿臂宽贯穿; 侧躺打印零支撑")
