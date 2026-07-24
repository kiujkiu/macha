"""
Build POV 3D rim_ring STL using manifold3d.

Geometry (all mm, axis along +Z, base bottom at Z=0; CCW positive angles,
0 deg = +X axis):

2026-07-20 改动 (承载盘并入):
  mlkpai_carrier_disc 取消 —— rim_ring 翻过来 (托盘平面朝上) 自己当承载面,
  pi2hub 直接坐托盘顶。为此:
    • 托盘 BASE_H 3.5 -> 5 (要塞下 Phi4.2 x 4.5 铜螺母沉孔), 总高 9 -> 10.5
    • 并入原承载盘那 7 个 pi2hub 安装孔: Phi3.2 通孔 + Phi4.2 x 4.5 沉孔,
      沉孔从装配下方(唇侧)往上开; 孔位 = 承载盘系 (x, -y) (装配里绕 X 翻转)
    • 外唇两个角度缺口全部取消 -> 外环凸台补全为完整整圈 (互锁不要了)
    • 新增 2 个 Phi4 通孔 @ (-10°,R72) 和 (-42.5°,R56)
    • 2026-07-21 晚: 4 个 wifi_shell 沿孔 (Phi3.2 通 + Phi4.2x4.5 唇侧沉孔,
      同 pi2hub 孔型), 位置 = 盒局部 (33.5/58.5, ±43.3) 转 135° 后取 (x,-y)

2026-07-21 深夜 (hub 中央凸台让渡, 与 hub_disc 同步改):
    • 中孔 ID 60 -> 50; 内圈 8 孔 PCD Phi70 -> Phi60 (R35 -> R30)
    • 新增内凸台环 OD80/ID70 x 2.5 (唇侧 Z 5..7.5) —— 落 hub 底板顶,
      ID70 套 hub 缩小后的 Phi70 下凸台 (径向定心从中孔转移到这)

  Feature 1 - Base annulus:
      ID 50, OD 170, height 5  (Z = 0 .. 5)
      Notch cutout (扇形挖槽): remove band r in [35, 61],
                    angles -45 deg .. -40 deg,
                    lip-side top 2mm (Z = 3 .. 5)  (2026-07-20 改 R40..OD -> R35..R61)

  Feature 2 - 16 Phi3.2 M3 through-holes:
      PCD Phi60  (R = 30)  x 8 holes  (2026-07-21 深夜: was Phi70)
      PCD Phi155 (R = 77.5) x 8 holes
      Both rings: angles = 22.5 + k * 45  for k = 0..7
      Through the full Z range. No counterbores.

  Feature 3 - Outer rim boss:
      ID 165, OD 170 (2.5 mm wall), height 5.5  (Z = 3.5 .. 9.0)
      Two angular cutouts (boss only):
          - 5 deg .. 0 deg   (5 deg-wide gap straddling +X axis)
          - 45 deg .. -40 deg (aligned with Feature-1 notch)

Total part height: 9.0 mm.
Print orientation: flat on bed, base down.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Parameters =====
# Base annulus ("托盘")
# 2026-07-21 深夜 (hub 凸台让渡): 中孔 ID 60 -> 50 (hub 上凸台 Phi60->50, 继续
# 名义套合; 内圈 8 孔挪 R30 后 ID60 会切孔, 必须同步缩)。
BASE_ID = 50.0
BASE_OD = 170.0
BASE_H  = 5.0           # Z = 0 .. 5   (2026-07-20: 3.5 -> 5, 见文件头)

# Notch in base (扇形挖槽, lip-side 2mm 深)
# 2026-07-20: 径向范围 R40..OD 改为 R35..R61; 2026-07-22: 内径改回 40 (用户)
# —— 正好从内凸台环 (R35..40) 外缘起, 凸台环不再跨槽桥接。
NOTCH_R_MIN = 40.0      # 内径 (2026-07-22: 35 -> 40)
NOTCH_R_MAX = 61.0      # 外径 (was BASE_OD/2 = 85)
NOTCH_A_S   = -45.0     # deg
NOTCH_A_E   = -40.0     # deg
NOTCH_DEPTH = 2.0       # 深度 2 (从唇侧面往下), 不随 BASE_H 变
NOTCH_Z_S   = BASE_H - NOTCH_DEPTH   # Z lower
NOTCH_Z_E   = BASE_H                 # Z upper

# Outer rim boss
RIM_ID  = 165.0
RIM_OD  = 170.0
RIM_H   = 5.5           # Z = BASE_H .. BASE_H + RIM_H = 3.5 .. 9.0

# 内凸台环 (2026-07-21 深夜, hub 凸台让渡): OD80/ID70 x 2.5, 长在唇侧面上
# (part Z 5..7.5)。装配翻转后落到 asm 34.7..37.2, 底面坐 hub 底板顶 (34.7),
# ID70 套住 hub 缩小后的 Phi70 下凸台 (名义对名义, 打印后松配, 起径向定心)。
# 挖槽 2026-07-22 起于 R40 = 本凸台环外缘, 凸台环不跨槽无桥接;
# 走线通道 (asm 37.2..39.2) 在凸台环之上, 不被挡。
IBOSS_OD, IBOSS_ID, IBOSS_H = 80.0, 70.0, 2.5

# Rim-boss angular cutouts (boss only)
RIM_CUT1_A_S = -5.0
RIM_CUT1_A_E =  0.0
RIM_CUT2_A_S = -45.0
RIM_CUT2_A_E = -40.0

TOTAL_H = BASE_H + RIM_H   # 9.0

# 16 Phi3.2 M3 through-holes
M3_DIAM = 3.2
INNER_PCD_R = 30.0           # Phi 60 (2026-07-21 深夜: 35->30, 与 hub_disc 同步)
OUTER_PCD_R = 77.5            # Phi 155
HOLE_ANGLES = [22.5 + k * 45.0 for k in range(8)]
PATTERN_INNER = [(INNER_PCD_R * math.cos(math.radians(a)),
                  INNER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]
PATTERN_OUTER = [(OUTER_PCD_R * math.cos(math.radians(a)),
                  OUTER_PCD_R * math.sin(math.radians(a))) for a in HOLE_ANGLES]

CYL_SEG  = 240
HOLE_SEG = 32

# 2 个 Φ4 通孔 (2026-07-20 用户新增), 极坐标 (角度从 +X 起, CCW 正):
EXTRA_HOLE_D = 4.0
EXTRA_HOLES_POLAR = [(-10.0, 72.0), (-42.5, 56.0)]   # (deg, R)  (2026-07-20: 42.5->-42.5; 2026-07-21: 2.5->10->-10)
EXTRA_HOLES = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)))
               for (a, R) in EXTRA_HOLES_POLAR]

# (2026-07-21: WiFi 盒改绕圆心转 135° [与 pi2hub 边平行]; 侧立方案的"脚落现成
#  环孔"已随 wifi_shell 放平方案作废, 专用沿孔见下方 WIFI_HOLES。)

# ===== 7 pi2hub mounting holes (2026-07-20, 从 mlkpai_carrier_disc 并入) =====
# 承载盘取消后, rim_ring 翻过来 (托盘平面朝上) 自己当承载面。
# 装配中 rim_ring 绕 X 翻转 (y -> -y), 所以零件系坐标 = 原承载盘系的 (x, -y)。
PCB_ROT = 90.0
PCB_OFF = (-10.0, 0.0)
# 2026-07-21: 7 孔整组绕圆心逆时针再转 135° (从上往下看装配). 在盘设计系
# (翻转前) 加 +135°, 装配绕 X 翻转后即等于俯视逆时针 135°。板/柱/米联派同步转。
PI_ROT_EXTRA = 135.0
def _rotp(pts, deg=PCB_ROT, off=PCB_OFF):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    return [(round(c*x - s_*y + off[0], 3), round(s_*x + c*y + off[1], 3)) for (x, y) in pts]
def _rot_about_origin(pts, deg):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    return [(round(c*x - s_*y, 3), round(s_*x + c*y, 3)) for (x, y) in pts]
_PI_BASE = _rotp([(-47.0, 44.0), (0.0, 44.0), (47.0, 44.0),
                  (-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0)])
_PI_DISC = _rot_about_origin(_PI_BASE, PI_ROT_EXTRA)   # 绕圆心 +135°
PI_HOLES = [(x, -y) for (x, y) in _PI_DISC]        # 翻转 -> 零件系
PI_THRU_D, PI_INSERT_D, PI_INSERT_DEEP = 3.2, 4.2, 4.5

# ===== 4 wifi_shell 沿孔 (2026-07-21 晚) =====
# wifi_shell (放平倒扣罩) 双端沿 4×Φ3.2, 装配系局部 (盒 footprint 中线 XC=46):
# X = 46 − 46.4/2 + {10.7, 35.7} = 33.5/58.5, Y ±43.3; 随 WIFI_ROT_EXTRA=135°
# 组转 (装配系直接转, 与 PI 的"设计系+135 再翻"不同), 零件系 = 装配系 (x, −y)。
# 孔型与 pi2hub 孔同款: Φ3.2 通 + Φ4.2×4.5 铜螺母沉孔从唇侧往上, 承载面留 0.5
# 台肩; M3×8 从壳沿顶面拧入 (沿 3 + 台肩 0.5 + 螺母 4.5)。
# 2026-07-22 定稿 (用户): 盒向 pi2hub 靠 3mm (XC 46→43) + 只保留一组孔,
# 位置 = 原位沿长边平移 −13 (局部 −Y, 母头/线缆收回盘内; 2026-07-22 从 −15
# 改 −13: −15 时最内孔沉孔边 r39.5 侵入内凸台环 R40 达 0.5, 用户要求消除 —
# −13 时最内孔 (30.5,30.3) r43.0, 沉孔边 40.9, 距凸台环 0.9 ✓)。此前 0/−10/−20
# 三档滑位方案作废。4 孔半径 43.0/63.2/64.0/79.1, 全在盘内。
WIFI_XC, WIFI_ROT = 43.0, 135.0
WIFI_SHIFTS = (-13.0,)
_WIFI_LOCAL = [(round(WIFI_XC - 46.4/2 + z, 3), round(y + dy, 3))
               for dy in WIFI_SHIFTS
               for z in (10.7, 35.7) for y in (43.3, -43.3)]
_WIFI_LOCAL = [(x, y) for (x, y) in _WIFI_LOCAL
               if math.hypot(x, y) <= 85.0 - 1.6 - 1.0]   # 孔边距盘边 ≥1
_WIFI_ASM = _rot_about_origin(_WIFI_LOCAL, WIFI_ROT)
WIFI_HOLES = [(x, -y) for (x, y) in _WIFI_ASM]

# ===== 4 个环孔螺丝头沉孔 (2026-07-22; 当晚用户图纸红圈改版) =====
# wifi 角落的 4 颗 ring→hub 锁紧 M3: 内圈 R30 + 外圈 R77.5 的 202.5°/247.5°
# 各 2 孔, 从托盘承载面 (part Z0) 统一加 Φ7.5×2.0 头沉孔 (先前 H1/H2 的
# Φ6.5×2.2 被此规格取代)。内圈 2 颗在放平 wifi 模块肚子底下 (沉平才能放模块),
# 外圈 2 颗紧挨盒东侧 (CB 边距壳壁 1.65)。其余 12 环孔头仍外露。
HEAD_CB_D, HEAD_CB_DEEP = 7.5, 2.0
HEAD_CB_ANGLES = (202.5, 247.5)
HEAD_CB_XY = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
              for r in (INNER_PCD_R, OUTER_PCD_R) for a in HEAD_CB_ANGLES]
# 沉孔从装配下方 (唇侧面 Z=BASE_H) 往上 4.5 -> 占 Z 0.5..5, 朝上的托盘面留 0.5 台肩。
# (2026-07-20 用户定 4.5, 与 hub_disc 环孔 2026-07-14 的 4->4.5 一致。)
# 铜螺母 (M3x4x4.5, OD4.5) 从 hub_disc 那圈 r40..72.5 的空槽里往上压入。

# ===== Helpers =====
def annulus(z0, h, r_in, r_out, segments=CYL_SEG):
    """Return a manifold annulus extending from Z=z0 to Z=z0+h."""
    outer = m3d.Manifold.cylinder(h, r_out, r_out, segments, False)
    inner = m3d.Manifold.cylinder(h + 2.0, r_in, r_in, segments, False)
    inner = inner.translate((0.0, 0.0, -1.0))
    ring = outer - inner
    return ring.translate((0.0, 0.0, z0))

def wedge(a_start_deg, a_end_deg, r, h, z0, n_seg=24):
    """Build a pie wedge centered at origin, sweeping a_start..a_end (deg) at
    radius r, extruded by h starting at Z=z0. r should be larger than any
    geometry it must clear."""
    pts = [(0.0, 0.0)]
    for i in range(n_seg + 1):
        a = math.radians(a_start_deg + i * (a_end_deg - a_start_deg) / n_seg)
        pts.append((r * math.cos(a), r * math.sin(a)))
    w = m3d.CrossSection([pts]).extrude(h)
    return w.translate((0.0, 0.0, z0))

# ===== Build the solid =====

# Base annulus (full)
base = annulus(0.0, BASE_H, BASE_ID / 2, BASE_OD / 2)

# Notch in base: remove the outer band (r > 40) in the wedge -45..-40 deg
# from Z=2.5 to Z=5. Subtract intersection of:
#   - the wedge (clears full OD radially)
#   - an annulus (cuts only r > NOTCH_R_MIN)
# at Z in [NOTCH_Z_S, NOTCH_Z_E].
notch_h = NOTCH_Z_E - NOTCH_Z_S          # 2.5
notch_clearance_r = BASE_OD / 2 + 2.0    # 87
notch_wedge = wedge(NOTCH_A_S, NOTCH_A_E, notch_clearance_r,
                    notch_h + 0.4, NOTCH_Z_S - 0.2, n_seg=24)
# Annulus that limits the cut to R_MIN..R_MAX within the wedge:
notch_outer_ann = annulus(NOTCH_Z_S - 0.2, notch_h + 0.4,
                          NOTCH_R_MIN, NOTCH_R_MAX)
notch_cutter = m3d.Manifold.batch_boolean(
    [notch_wedge, notch_outer_ann], m3d.OpType.Intersect)
base = base - notch_cutter

# Outer rim boss (annular) — 2026-07-20: 两个角度缺口 (RIM_CUT1/2) 全部取消,
# 外唇补全为完整整圈 (用户: 互锁不要了, 都补全)。
rim = annulus(BASE_H, RIM_H, RIM_ID / 2, RIM_OD / 2)

# 内凸台环 OD80/ID70 x 2.5 (唇侧面上, 见参数注释)
iboss = annulus(BASE_H, IBOSS_H, IBOSS_ID / 2, IBOSS_OD / 2)

part = base + rim + iboss

# ===== Drill 16 Phi3.2 through-holes =====
def drill_through(part, x, y):
    hole_h = TOTAL_H + 2.0
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2,
                              HOLE_SEG, False)
    h = h.translate((x, y, -1.0))
    return part - h

for (x, y) in PATTERN_INNER:
    part = drill_through(part, x, y)
for (x, y) in PATTERN_OUTER:
    part = drill_through(part, x, y)

# ===== 2 个 Φ4 通孔 (2026-07-20) =====
for (x, y) in EXTRA_HOLES:
    h = m3d.Manifold.cylinder(TOTAL_H + 2.0, EXTRA_HOLE_D / 2, EXTRA_HOLE_D / 2,
                              HOLE_SEG, False).translate((x, y, -1.0))
    part = part - h


# ===== 7 pi2hub 孔: Phi3.2 通孔 + Phi4.2 x 4 铜螺母沉孔 (从唇侧 Z=BASE_H 往下) =====
def _cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg, False).translate((x, y, z0))

for (x, y) in PI_HOLES:
    part = part - _cyl(PI_THRU_D, x, y, -1.0, BASE_H + 1.0)
    part = part - _cyl(PI_INSERT_D, x, y, BASE_H - PI_INSERT_DEEP, BASE_H + 1.0)

# ===== 4 wifi_shell 沿孔: 同款 Φ3.2 通 + Φ4.2×4.5 唇侧沉孔 =====
for (x, y) in WIFI_HOLES:
    part = part - _cyl(PI_THRU_D, x, y, -1.0, BASE_H + 1.0)
    part = part - _cyl(PI_INSERT_D, x, y, BASE_H - PI_INSERT_DEEP, BASE_H + 1.0)

# ===== 4 个环孔头沉孔 Φ7.5×2.0 (承载面 Z0 侧, 见参数注释) =====
for (x, y) in HEAD_CB_XY:
    part = part - _cyl(HEAD_CB_D, x, y, -1.0, HEAD_CB_DEEP)

# ===== Export STL =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("rim_ring.stl")
_header = b"POV3D rim_ring"
assert len(_header) <= 80, f"STL header too long: {len(_header)} bytes"
with out.open("wb") as f:
    f.write(_header.ljust(80, b" "))
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
print(f"  volume:        {part.volume():10.2f} mm^3")
print(f"  surface area:  {part.surface_area():10.2f} mm^2")
print(f"  16 Phi3.2 through-holes (8 on PCD Phi{2*INNER_PCD_R:g}, 8 on PCD Phi{2*OUTER_PCD_R:g})")
print(f"  中孔 ID{BASE_ID:g}; 内凸台环 OD{IBOSS_OD:g}/ID{IBOSS_ID:g}x{IBOSS_H:g} (唇侧)")
print(f"  angles: 22.5 + k*45 (k=0..7) = {[round(a,1) for a in HOLE_ANGLES]}")
print(f"  7 pi2hub 孔: Phi{PI_THRU_D:g} 通 + Phi{PI_INSERT_D:g}x{PI_INSERT_DEEP:g} 沉(从唇侧)")
print(f"  {len(WIFI_HOLES)} wifi_shell 沿孔 (同款, 定稿单组: XC43 + 长边平移−13): 零件系 {WIFI_HOLES}")
print(f"  {len(HEAD_CB_XY)} 环孔头沉孔 Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} (承载面侧, R30+R77.5 @{HEAD_CB_ANGLES}): {[(round(x,3),round(y,3)) for (x,y) in HEAD_CB_XY]}")
print(f"  2 Phi{EXTRA_HOLE_D:g} 通孔 @ (deg,R)={EXTRA_HOLES_POLAR}")

print(f"  外唇缺口全部取消 -> 完整整圈")

# Sanity-check binary STL: 80-byte header + u32 + 50 bytes/triangle
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, (
    f"STL size mismatch: expected {_expected} (84+{len(tris)}*50), got {_actual}"
)
print(f"  STL size OK: {_actual} bytes (= 84 + {len(tris)}*50)")
