"""
screen_solder_jig — 焊接时给 screen_150x169 定位的托盘 (2026-07-21 用户).

5 面形状 (底 + 4 壁, 开口朝上): 屏正面朝下落入内腔, 四壁锁住位置,
背面朝上露出接口/引脚供焊接。

内腔 (用户给定):
  • 平面 150.3 (X, 屏宽) × 169.05 (Y, 屏高)  (150/168.75 各 +0.3 间隙)
  • 深度 15 (Z)  —— 屏厚 7.27 落入后, 上沿高出屏背 7.73

壁厚 4 (用户给定) / 底厚 3 (WALL / FLOOR 可调)。
底面 4 × 40×40 方形通孔 (2×2 对称), 减 LED 面接触 + 透气。
外形 158.3 × 177.05 × 18, 落在 X2D 256 床内, 平放底朝下打印, 无支撑。

局部坐标: 内腔在 XY 居中, 底 Z 0..FLOOR, 腔 Z FLOOR..FLOOR+DEPTH, 开口 +Z。
"""
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
CAV_W = 150.3      # X — screen width  (150→150.3, 用户 2026-07-21 +0.3 间隙)
CAV_H = 169.05     # Y — screen height (168.75→169.05, 用户 2026-07-21 +0.3 间隙)
DEPTH = 15.0       # Z — pocket depth (用户 2026-07-21: 10→15)
WALL  = 4.0        # side wall thickness (用户 2026-07-21: 5→4)
FLOOR = 3.0        # floor thickness

OUT_W = CAV_W + 2 * WALL     # 158.3
OUT_H = CAV_H + 2 * WALL     # 177.05
OUT_Z = DEPTH + FLOOR        # 18

# M3 through-holes in the two 150-wide end walls (the ±Y walls, 用户 2026-07-21):
# axis along Y (through the 4mm wall), 3 per wall spaced 64 in X, hole center
# 6.6mm above the internal floor. One Y-axis cylinder pierces BOTH end walls,
# so 3 cylinders = 3 holes per wall.
HOLE_D  = 3.2                 # M3 clearance
HOLE_XS = [-64.0, 0.0, 64.0]  # spacing 64
HOLE_Z  = FLOOR + 6.6         # 9.6 — 距内腔底面 6.6

# 4 × 40×40 square through-holes in the FLOOR (用户 2026-07-21: 4cm×4cm, 对称放).
# 2×2 symmetric, centered — leaves a border ring + central cross ribs so the
# screen's LED face isn't fully backed by plastic. All within the cavity floor
# (don't reach the walls). Margins/ribs ≥ ~19mm.
SQ_SIDE = 40.0
SQ_CX, SQ_CY = 36.0, 42.0
SQ_CENTERS = [(sx * SQ_CX, sy * SQ_CY) for sx in (-1, 1) for sy in (-1, 1)]

_slop = 0.1

# ===== Build =====
# Outer solid block, centered in XY, bottom at Z=0.
outer = m3d.Manifold.cube((OUT_W, OUT_H, OUT_Z), False).translate(
    (-OUT_W / 2, -OUT_H / 2, 0.0))

# Pocket cavity, centered in XY, from top face down by DEPTH (+slop breaks the top).
cav = m3d.Manifold.cube((CAV_W, CAV_H, DEPTH + _slop), False).translate(
    (-CAV_W / 2, -CAV_H / 2, FLOOR))

jig = outer - cav

# M3 through-holes: cylinder along +Y at each (x, HOLE_Z), long enough to
# pierce both ±Y walls (cavity between them stays empty → one cut = both holes).
_hy = OUT_H + 4.0
for x in HOLE_XS:
    h = m3d.Manifold.cylinder(_hy, HOLE_D / 2, HOLE_D / 2, 32, False)
    h = h.translate((0.0, 0.0, -_hy / 2))          # center on origin along its axis
    h = h.rotate((90.0, 0.0, 0.0))                 # axis Z -> Y
    h = h.translate((x, 0.0, HOLE_Z))
    jig = jig - h

# 4 × 40×40 floor cutouts (through the floor, Z 0..FLOOR).
for (sx, sy) in SQ_CENTERS:
    sq = m3d.Manifold.cube((SQ_SIDE, SQ_SIDE, FLOOR + 2 * _slop), False).translate(
        (sx - SQ_SIDE / 2, sy - SQ_SIDE / 2, -_slop))
    jig = jig - sq

# ===== Export STL =====
mesh = jig.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("screen_solder_jig.stl")
with out.open("wb") as f:
    f.write(b"POV3D screen_solder_jig (5-face pocket)".ljust(80, b" ")[:80])
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

assert 84 + len(tris) * 50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris, {len(verts)} verts)")
print(f"  cavity {CAV_W:g}×{CAV_H:g} × depth {DEPTH:g}, wall {WALL:g}, floor {FLOOR:g}")
print(f"  outer  {OUT_W:g}×{OUT_H:g}×{OUT_Z:g}")
print(f"  bbox X {verts[:,0].min():.2f}..{verts[:,0].max():.2f}  "
      f"Y {verts[:,1].min():.2f}..{verts[:,1].max():.2f}  "
      f"Z {verts[:,2].min():.2f}..{verts[:,2].max():.2f}")
print(f"  volume {jig.volume()/1000:.1f} cm^3")
print(f"  M3 holes: ±Y walls, X={HOLE_XS} (间距64), Z={HOLE_Z:g} (底面上6.6), Φ{HOLE_D:g} 通")
print(f"  floor squares: 4 × {SQ_SIDE:g}×{SQ_SIDE:g} @ (±{SQ_CX:g}, ±{SQ_CY:g}) 通底")
