"""
mlkpai_carrier_disc — 转子承载盘 Φ170×6 (2026-07-01, 旧 rim_top_disc 保留)。

叠层: 盘 → 6 凸台(带铜螺母)固定 pi2hub → pi2hub(下, 板底件1.2) → 尼龙柱+排针排座 → 米联派(上)。
承载盘特征 (居中坐标系, 盘体 Z = 0..6; 位置为 pi2hub 居中、转45° 前的 disc 本体系):
  • Φ170 × 6 flat disc
  • 16 × Φ3.2 M3 挂环孔 (PCD Φ70 R35 + PCD Φ155 R77.5, 角度 22.5+45k°) + 顶面 Φ7×2.5 沉孔 → 装 rim_ring
  • 6 × Φ10 安装凸台 (高2, Z 6..8) 在 pi2hub 6 孔位 (±39.5, 25/-25/-55): 每个 = 从 *盘底面*
    Φ4.2 沉孔向上 4 深 (Z0..4, 压 M3×4×4.5 注塑铜花螺母 OD4.5, 被 Z4 台肩挡住) + Φ3.2
    通到凸台顶 (顶上螺丝穿 pi2hub 拧下来把铜螺母拉紧)。凸台顶 = pi2hub 落座面; 板底件1.2 在2间隙避空。
  • 3 × Φ3 支托 (高2, Z 6..8, 实心无孔) 顶住 pi2hub 顶排连接器 (T1/T2/T3, 让开排针):
    T1(-47,37) 顶排左端 / T2(-5,37) 顶排中间空档 / T3(47,37) 顶排右端。
"""
import math, struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

DISC_OD, THICK, SEG = 170.0, 6.0, 192

# 16 rim-mounting holes
INNER_R, OUTER_R = 35.0, 77.5
ANGLES = [22.5 + k*45.0 for k in range(8)]
M3, M3_CB_D, M3_CB_DEEP = 3.2, 7.0, 2.5

# 6 pi2hub mounting bosses (centred, pre-45° disc frame)
BOSS_XY = [(-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0), (-39.5, -55.0), (39.5, -55.0)]
BOSS_D, BOSS_H = 10.0, 2.0
THRU_D, INSERT_D, INSERT_DEEP = 3.2, 4.2, 4.0     # 通孔 + 铜螺母沉孔 (从凸台顶)

# 3 support pads 托 (solid, no hole) — Φ3, 让开所有排针孔 (>1.6mm gap, 实测)
TUO_XY = [(-48.5, 37.0), (-4.0, 37.0), (45.0, 40.0)]
TUO_D, TUO_H = 3.0, 2.0

TOP = THICK                                        # disc top Z=6
BOSS_TOP = TOP + BOSS_H                             # 8

def _cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

# ===== disc =====
disc = m3d.Manifold.cylinder(THICK, DISC_OD/2, DISC_OD/2, SEG, False)

# add bosses + support pads (solid) BEFORE cutting holes
for (x, y) in BOSS_XY:
    disc = disc + _cyl(BOSS_D, x, y, TOP, BOSS_TOP, 64)
for (x, y) in TUO_XY:
    disc = disc + _cyl(TUO_D, x, y, TOP, BOSS_TOP, 48)

# 16 rim holes + top CB
for R in (INNER_R, OUTER_R):
    for a in ANGLES:
        x, y = R*math.cos(math.radians(a)), R*math.sin(math.radians(a))
        disc = disc - _cyl(M3, x, y, -1, THICK+1)
        disc = disc - _cyl(M3_CB_D, x, y, THICK - M3_CB_DEEP, THICK+1)

# 6 boss insert holes: Φ3.2 through (disc+boss) + Φ4.2 pocket 4mm from DISC BOTTOM (up)
for (x, y) in BOSS_XY:
    disc = disc - _cyl(THRU_D, x, y, -1, BOSS_TOP+1)
    disc = disc - _cyl(INSERT_D, x, y, -1, INSERT_DEEP)                       # Z 0..4 from bottom

# ===== export =====
mesh = disc.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("mlkpai_carrier_disc.stl")
_hdr = b"POV3D mlkpai_carrier_disc"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80]); f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)")
print(f"  disc Φ{DISC_OD:g}×{THICK:g}; 16×M3 rim holes + Φ{M3_CB_D:g}×{M3_CB_DEEP:g} top CB")
print(f"  6× Φ{BOSS_D:g} bosses h{BOSS_H:g} (Z{TOP:g}..{BOSS_TOP:g}) @ {BOSS_XY}")
print(f"     each: Φ{THRU_D:g} through + Φ{INSERT_D:g}×{INSERT_DEEP:g} pocket from boss top (铜花螺母)")
print(f"  3× Φ{TUO_D:g} 托 h{TUO_H:g} @ {TUO_XY}")
print(f"  bbox X {verts[:,0].min():.1f}..{verts[:,0].max():.1f}  Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}  vol {disc.volume():.0f}")
