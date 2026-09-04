"""
POV 3D 转子侧垫片 hub_shim_v4 (2026-09-03, 用户: 「这个底面也加一个 2mm 的垫片,
直径做 10cm 就行, 我理解只需要红圈中这 5 个孔」)

垫在 **电机 bell top 与 hub_disc 底面之间** —— 是 motor_shim_v4 (定子侧) 的转子侧对应件。
v4/v3.1 装配里 hub_disc 是 **正放** 贴电机的 (`hub = stl + [0,0,ROTOR_Z0]`, 无翻转),
所以用户圈的 hub_disc 零件底面 (Z=0) 就是贴 bell top 的那面。

几何 = 一个圆 + 5 个孔 (用户圈的红圈内容):
  - 外圆    Φ100 × 2
  - 4 × Φ3.4 菱形过孔   (±6, 0) / (0, ±7.5) —— hub_disc pattern A, 对角 12×15,
                        对电机 bell top 的 4 孔菱形
  - 1 × Φ6.2 中央通孔   对齐 hub_disc 底面那个 Φ6.2×2.2 中心盲窝 (bell 中心凸起让位)

⚠ 参数复刻自 models/hub_disc/build_stl.py (项目惯例, 不 import)。

⚠⚠ Φ100 会盖住 hub_disc 底面 R50 以内的另外 12 个孔 —— pattern B 方形 4 孔
    (±15,±15, R21.2) 和 pattern C 内 PCD Φ60 的 8 孔 (R30), 它们的 Φ4.2 底面沉孔
    也一并被盖。pattern D (PCD Φ155, R77.5) 在垫片外, 不受影响。
    详见 build_stl 末尾打印的覆盖报告 —— 要不要给这 12 个开让位孔由用户定。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== 复刻自 models/hub_disc/build_stl.py (改那边要同步这里) =====
HUB_BASE_OD     = 165.0
HUB_M3_DIAM     = 3.2      # hub 上的通孔径
DIAG_X          = 12.0     # pattern A 菱形对角 (X)
DIAG_Y          = 15.0     # pattern A 菱形对角 (Y)
CENTER_CB_DIAM  = 6.2      # hub 底面中心盲窝
CENTER_CB_DEPTH = 2.2
SQUARE_SIDE     = 30.0     # pattern B 方形 30×30
INNER_PCD_R     = 30.0     # pattern C 内 PCD Φ60
OUTER_PCD_R     = 77.5     # pattern D 外 PCD Φ155
CB_B_DIAM       = 4.2      # B/C/D 的底面沉孔径
RING_HOLE_ROTATION = 22.5

# ===== 垫片自身参数 =====
THICK    = 2.0            # 2026-09-03 用户指定 (同 motor_shim_v4)
OD       = 100.0          # 2026-09-03 用户指定 (「直径做 10cm 就行」)
M3_DIAM  = 3.4            # 过孔比 hub 的 Φ3.2 放 0.2, 散件好对位
CENTER_D = CENTER_CB_DIAM # 6.2, 与 hub 中心窝同径

# pattern A 菱形孔位 (与 hub_disc PATTERN_A 完全一致)
PATTERN_A = [( DIAG_X/2, 0.0),
             (-DIAG_X/2, 0.0),
             ( 0.0,  DIAG_Y/2),
             ( 0.0, -DIAG_Y/2)]

CYL_SEG  = 192
HOLE_SEG = 48

# ===== 防漂移检查 =====
assert OD < HUB_BASE_OD, "垫片不能大过 hub_disc 基盘"
_r_a_out = max(math.hypot(x, y) for x, y in PATTERN_A) + M3_DIAM / 2
assert _r_a_out < OD / 2, "菱形过孔超出垫片外缘"
_r_a_in = min(math.hypot(x, y) for x, y in PATTERN_A) - M3_DIAM / 2
assert CENTER_D / 2 < _r_a_in, "中央孔与菱形过孔相交"

# ===== 建模 =====
part = m3d.Manifold.cylinder(THICK, OD / 2, OD / 2, CYL_SEG, False)

# 中央 Φ6.2 通孔
c = m3d.Manifold.cylinder(THICK + 2, CENTER_D / 2, CENTER_D / 2, HOLE_SEG, False)
part = part - c.translate((0, 0, -1.0))

# 4 × Φ3.4 菱形过孔
for (hx, hy) in PATTERN_A:
    h = m3d.Manifold.cylinder(THICK + 2, M3_DIAM / 2, M3_DIAM / 2, HOLE_SEG, False)
    part = part - h.translate((hx, hy, -1.0))

# ===== 导出 STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("hub_shim_v4.stl")
with out.open("wb") as f:
    _hdr = (f"POV3D hub_shim_v4 OD{OD:g} T{THICK:g} / 4xPhi{M3_DIAM:g} diamond"
            f" {DIAG_X:g}x{DIAG_Y:g} / center Phi{CENTER_D:g}").encode("ascii")
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
print(f"  外圆 Φ{OD:g} × {THICK:g}   中央通孔 Φ{CENTER_D:g}")
print(f"  4 × Φ{M3_DIAM:g} 菱形过孔 (对角 {DIAG_X:g}×{DIAG_Y:g}): "
      + ", ".join(f"({x:+g},{y:+g})" for x, y in PATTERN_A))

# ===== 覆盖报告: Φ100 盖住了 hub_disc 底面的哪些孔 =====
R = OD / 2
_pat_b = [( SQUARE_SIDE/2,  SQUARE_SIDE/2), (-SQUARE_SIDE/2,  SQUARE_SIDE/2),
          ( SQUARE_SIDE/2, -SQUARE_SIDE/2), (-SQUARE_SIDE/2, -SQUARE_SIDE/2)]
_pat_c = [(INNER_PCD_R * math.cos(math.radians(k*45 + RING_HOLE_ROTATION)),
           INNER_PCD_R * math.sin(math.radians(k*45 + RING_HOLE_ROTATION))) for k in range(8)]
_pat_d = [(OUTER_PCD_R * math.cos(math.radians(k*45 + RING_HOLE_ROTATION)),
           OUTER_PCD_R * math.sin(math.radians(k*45 + RING_HOLE_ROTATION))) for k in range(8)]
print("\n  ── Φ%g 垫片对 hub_disc 底面其余孔的覆盖 ──" % OD)
for name, pat, desc in (("B 方形 30×30", _pat_b, "4 孔 + Φ4.2×4 底沉"),
                        ("C 内 PCD Φ60", _pat_c, "8 孔 + Φ4.2×4.5 底沉"),
                        ("D 外 PCD Φ155", _pat_d, "8 孔 + Φ4.2×4.5 底沉")):
    r_cb_out = max(math.hypot(x, y) for x, y in pat) + CB_B_DIAM / 2
    covered = r_cb_out <= R
    print(f"  {name:14s} ({desc}): 沉孔外缘 R{r_cb_out:6.2f}  "
          + ("⚠ 被垫片盖住" if covered else f"✓ 在垫片外 (余 {r_cb_out - R:.2f})"))
