"""
mlkpai_carrier_disc — 转子承载盘 Φ170×5 (2026-07-06 厚 6→5; 2026-07-01 建, 旧 rim_top_disc 保留)。

叠层: 盘 → (M3 尼龙垫柱 ~5) → pi2hub(下, 新版 100×75, 底面焊脚) → 尼龙柱+排针排座 → 米联派(上)。
(2026-07-03 晚: 3 个 Φ3 支托取消。 2026-07-06: 7 个凸台也取消 — 用户要求,
 只留 Φ3.2 通孔 + 盘底 Φ4.2×4 铜螺母沉孔; 板与盘之间用尼龙垫柱隔开。
 凸台取消后不再挤 R35 环孔 → 16 环孔的 Φ7 顶沉全部恢复。)
承载盘特征 (居中坐标系, 盘体 Z = 0..5; 位置为 pi2hub 居中、转45° 前的 disc 本体系):
  注意: 铜螺母沉孔仍 4 深 → 台肩只剩 1mm (原 2), 压入时勿过深。
  • Φ170 × 5 flat disc
  • 16 × Φ3.2 M3 挂环孔 (PCD Φ70 R35 + PCD Φ155 R77.5, 角度 22.5+45k°) + 顶面 Φ7×2.5 沉孔 → 装 rim_ring
  • 7 × pi2hub 安装孔 (孔位 = 2026-07-03 STEP 7 孔, 转90°+挪(-10,0) 后):
    每个 = Φ3.2 通孔 + 从 *盘底面* Φ4.2 沉孔向上 4 深 (Z0..4, 压 M3×4×4.5
    注塑铜花螺母 OD4.5, 被 Z4 台肩挡住)。无凸台 (2026-07-06)。
"""
import math, struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

DISC_OD, THICK, SEG = 170.0, 5.0, 192

# 16 rim-mounting holes
INNER_R, OUTER_R = 35.0, 77.5
ANGLES = [22.5 + k*45.0 for k in range(8)]
M3, M3_CB_D, M3_CB_DEEP = 3.2, 7.0, 2.5

# 7 pi2hub mounting bosses (centred, pre-45° disc frame) — 2026-07-03 新版 STEP 孔位
# PCB_ROT: pcb 安装方向在盘上再转 90° (用户 2026-07-03; 反向改 -90)。凸台/支托随转。
# 16 挂环孔是 45° 阵列, 转 90° 后凸台-环孔间隙关系不变 (原核查继续有效)。
PCB_ROT = 90.0
PCB_OFF = (-10.0, 0.0)   # 2026-07-03 晚: PCB 再沿盘 -X 挪 10 (用户箭头方向)
def _rotp(pts, deg=PCB_ROT, off=PCB_OFF):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    return [(round(c*x - s_*y + off[0], 3), round(s_*x + c*y + off[1], 3)) for (x, y) in pts]
BOSS_XY = _rotp([(-47.0, 44.0), (0.0, 44.0), (47.0, 44.0),
                 (-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0)])
# (2026-07-06 凸台取消 → 与环孔不再冲突, 16 环孔顶沉全部保留)
THRU_D, INSERT_D, INSERT_DEEP = 3.2, 4.2, 4.0     # 通孔 + 铜螺母沉孔 (从盘底)

TOP = THICK                                        # disc top Z=5

def _cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

# ===== disc =====
disc = m3d.Manifold.cylinder(THICK, DISC_OD/2, DISC_OD/2, SEG, False)

# 16 rim holes + top CB (全部有顶沉)
for R in (INNER_R, OUTER_R):
    for a in ANGLES:
        x, y = R*math.cos(math.radians(a)), R*math.sin(math.radians(a))
        disc = disc - _cyl(M3, x, y, -1, THICK+1)
        disc = disc - _cyl(M3_CB_D, x, y, THICK - M3_CB_DEEP, THICK+1)

# 7 pi2hub holes: Φ3.2 through + Φ4.2 pocket 4mm from DISC BOTTOM (up)
for (x, y) in BOSS_XY:
    disc = disc - _cyl(THRU_D, x, y, -1, THICK+1)
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
print(f"  {len(BOSS_XY)}× pi2hub 孔 (无凸台, 2026-07-06) @ {BOSS_XY}")
print(f"  PCB_ROT={PCB_ROT:g}° + PCB_OFF={PCB_OFF}; 16 环孔顶沉全部保留")
print(f"     each: Φ{THRU_D:g} through + Φ{INSERT_D:g}×{INSERT_DEEP:g} pocket from disc bottom (铜花螺母)")
print(f"  bbox X {verts[:,0].min():.1f}..{verts[:,0].max():.1f}  Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}  vol {disc.volume():.0f}")
