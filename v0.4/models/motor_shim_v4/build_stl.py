"""
POV 3D 电机垫片 motor_shim_v4 (2026-09-03, 用户: 「我理解一个圆形加 5 个圆孔就行」)

垫在 `baseplate_collar_v4` 凸台内腔的底面 (装配 Z=5, 即底盘顶面) 上,
把 C4110 电机整体抬高 THICK。就是用户圈的那个绿圈区域。

几何 = 一个圆 + 5 个孔:
  - 外圆    Φ54 × 2        放进凸台内孔 Φ55, 单边间隙 0.5 (靠外圆自定位)
  - 4 × Φ3.4 电机安装过孔   对角 25 → (±8.8388, ±8.8388), 与底盘 4×M3 同位
  - 1 × Φ12 中央通孔        对齐底盘顶面那个 Φ12×1 中央沉孔 (电机底凸台/轴端让位)

⚠ 参数是从 v4/models/baseplate_collar_v4/build_stl.py **复刻**的 (项目惯例,
   不 import), 那边改了这里要跟着改。下面带 assert 防漂移。

⚠ 装机影响: 电机底面 Z 5→7, 转子面 31.7→33.7, **转子及以上整组上移 2**。
   顶轴承架/柱高是固定的 → 中间轴与 688 的配合、屏幕上下位置都会跟着变。
   装之前先确认这 2mm 是你想要的。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== 复刻自 baseplate_collar_v4 (改那边要同步这里) =====
BOSS_ID         = 55.0     # 凸台内孔 → 垫片外圆的上限
M3_ROT          = 0.0      # 电机孔整组转角
M3_DIAG         = 25.0     # 电机孔对角间距
M3_DIAM_PLATE   = 3.2      # 底盘上的电机孔径 (垫片自己用下面的 M3_DIAM)
CENTER_CB_DIAM  = 12.0     # 底盘顶面中央沉孔直径

# ===== 垫片自身参数 =====
THICK      = 2.0           # 2026-09-03 用户指定
OD         = 54.0          # 2026-09-03 用户指定 (原按 0.3 隙算的 54.4)
CLEAR_RAD  = (BOSS_ID - OD) / 2               # 派生: 0.5 单边隙
M3_DIAM    = 3.4           # 过孔比底盘的 Φ3.2 放 0.2, 散件好对位
CENTER_D   = CENTER_CB_DIAM                    # 12, 与底盘中央沉孔同径

M3_SIDE    = M3_DIAG / math.sqrt(2)            # 17.6777
M3_OFF     = M3_SIDE / 2                       # 8.8388

CYL_SEG  = 192
HOLE_SEG = 48

# ===== 防漂移检查 =====
assert OD < BOSS_ID, "垫片外圆必须小于凸台内孔"
_r_hole_out = M3_DIAG / 2 + M3_DIAM / 2
assert _r_hole_out < OD / 2, "M3 过孔超出垫片外缘"
assert CENTER_D / 2 < M3_DIAG / 2 - M3_DIAM / 2, "中央孔与 M3 过孔相交"

# ===== 建模 =====
part = m3d.Manifold.cylinder(THICK, OD / 2, OD / 2, CYL_SEG, False)

# 中央 Φ12 通孔
c = m3d.Manifold.cylinder(THICK + 2, CENTER_D / 2, CENTER_D / 2, HOLE_SEG, False)
part = part - c.translate((0, 0, -1.0))

# 4 × Φ3.4 电机过孔 (对角 25, 随 M3_ROT 转)
MOTOR_HOLES = []
for sx in (-1, 1):
    for sy in (-1, 1):
        x0, y0 = sx * M3_OFF, sy * M3_OFF
        a = math.radians(M3_ROT)
        hx = x0 * math.cos(a) - y0 * math.sin(a)
        hy = x0 * math.sin(a) + y0 * math.cos(a)
        MOTOR_HOLES.append((hx, hy))
        h = m3d.Manifold.cylinder(THICK + 2, M3_DIAM / 2, M3_DIAM / 2, HOLE_SEG, False)
        part = part - h.translate((hx, hy, -1.0))

# ===== 导出 STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("motor_shim_v4.stl")
with out.open("wb") as f:
    _hdr = (f"POV3D motor_shim_v4 OD{OD:g} T{THICK:g} / 4xPhi{M3_DIAM:g} diag{M3_DIAG:g}"
            f" / center Phi{CENTER_D:g}").encode("ascii")
    f.write(_hdr.ljust(80, b" ")[:80])   # STL 头必须 <=80 字节并截断
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume:        {part.volume():10.2f} mm^3   (PLA ~{part.volume()*1.24e-3:.1f} g)")
print(f"  surface area:  {part.surface_area():10.2f} mm^2")
print(f"  外圆 Φ{OD:g} × {THICK:g}  (凸台内孔 Φ{BOSS_ID:g}, 单边隙 {CLEAR_RAD:g})")
print(f"  中央通孔 Φ{CENTER_D:g}")
print(f"  4 × Φ{M3_DIAM:g} 电机过孔 @ 对角 {M3_DIAG:g}: "
      + ", ".join(f"({x:+.3f},{y:+.3f})" for x, y in MOTOR_HOLES))
print(f"  孔边→外缘 {OD/2 - _r_hole_out:.2f} / 中央孔边→M3 孔边 "
      f"{(M3_DIAG/2 - M3_DIAM/2) - CENTER_D/2:.2f}")
