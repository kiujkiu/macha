"""
Build the POV 3D baseplate_collar STL (merged baseplate + ring collar).

Combines:
  - baseplate: square 100×100×5 base + central boss Φ65/Φ55 H23
    (4×M6 corner holes, 4×M3+Φ7 CB center holes, Φ12×1 center CB on top,
    boss notch 75°–105° H8)
  - ring_collar: annular ring Φ80/Φ65 H13 sleeved over the boss
    (notch 75°–105° H6, aligned with the boss notch on the +Y side)

Since collar ID (Φ65) equals boss OD (Φ65), the two surfaces coincide and
the merged solid forms a single continuous annulus r=27.5..40 from Z=5..18,
stepping down to r=27.5..32.5 from Z=18..28 (boss only above collar top).

Final orientation: print flat on bed (Z up), base bottom at Z=0.
"""
# ═══════════════════════════════════════════════════════════════════════
# baseplate_collar_v4_h28 —— baseplate_collar_v4 的「原高度」变体
# (2026-09-04, 用户: 「之前的高度是多少, 保存一个独立的」)
#
# 与现行 baseplate_collar_v4 的**唯一**差别 = 高度回到 2026-08-28 降高之前:
#     BOSS_H    20.5 → 23.0   (凸台顶 Z 25.5 → 28)
#     COLLAR_H  10.5 → 13.0   (套环顶 Z 15.5 → 18)
# 其余全部相同 (外形 93.5 方+四角 R62.28、M6 节距 75、走线缺口 75°-105°、
# 底面 8×Φ4.2×4 铜花窝、顶面沉孔仍取消 ...)。两件并存, 改一件要想想另一件。
#
# ★ 不变量仍然成立: mounting_flange 底3 + flange_disc 7 + COLLAR_H + BASE_THICK 5
#   = BASE_THICK + BOSS_H  ⇒  3+7+13+5 = 28 = 5+23 ✓
#   所以 flange_disc_v4 / mounting_flange_v4 **不用重印**, 只是整体上移 2.5。
#
# ⚠ BOM 差异: 定子锁紧 8 颗 M3 的夹持 = 3+7+COLLAR_H+5 = **28** (现行件是 25.5)。
#   ⇒ 本件配 **M3×30 + 2mm 垫圈** (现行件是 M3×30 + 垫圈叠 4.5)。装错会顶起定子。
# ═══════════════════════════════════════════════════════════════════════

import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== Baseplate parameters =====
# BASE_SIDE 见下面「外形裁切」一节 (2026-08-19: 100 → 93.5 + 四角圆弧)
BASE_THICK = 5.0

# 2026-07-29 v4: 底板改用 200×200×13 网格板 (M6 螺纹孔 距边12.5/节距25)。
# 4 个 M6 脚必须落到网格位 (±37.5,±37.5) → 方形节距 75 (= 3 个网格节距),
# 对角 = 75*sqrt(2) = 106.07 (原 d100 是对角 106.07 / 节距 70.71, 配 25 网格的
# 轴向孔 (±50,0)/(0,±50) 并在装配里转 45°; 新板是偶数孔网格, 无中心孔也无
# ±50 轴向孔, 故改走对角网格位, 装配 ROT 45°→0°)。这是 v4 唯一的几何改动。
M6_DIAG         = 75.0 * math.sqrt(2)                      # corner-hole diagonal spacing (user 2026-06-29)
M6_PATTERN_SIDE = M6_DIAG / math.sqrt(2)     # ≈70.71 square side → diagonal 100
M6_DIAM         = 6.5

# ===== 外形裁切 (2026-08-19, 用户: 「这个件的四周是不是可以做调整」+ M6 大扁头实拍尺寸) =====
# 角孔用 M6 大扁头 (头 Φ12.5 × 厚 2.6, 内六角对边 4), 头坐在底盘顶面 Z5..7.6, 无沉孔。
# 底盘外形 100×100 方 → 「93.5 方 + 四角 R62.28 圆弧」:
#   · 直边 = 孔心 ±37.5 + 头半径 6.25 + 壁 3.0 = ±46.75  ⇒ 边长 93.5
#   · 角弧 = 孔心半径 53.033 + 6.25 + 3.0 = R62.283 (方角原在 R70.711 ⇒ 沿对角切掉 8.43)
# 面积 10000 → 8682 mm² (−13.2%), 底盘减料 6.6 cm³ ≈ 8 g PLA。
# ⚠ EDGE_WALL=3 是这四个角吃 M6 预紧力的最小肉厚, 不要再往下压 (2 mm 只多省 0.8%)。
# ⚠ 能切的量被 v4 的角孔位置卡死: 节距 70.71→75 后孔心外移 3.03, 帽外缘到 R59.28,
#   所以别拿旧 d100 图纸 (对角 100) 的余量来估 —— 那版可以切到 R59.25。
TRIM_ENABLE = True
M6_HEAD_D   = 12.5          # M6 大扁头 头径 (实测, 用户 2026-08-19 提供)
EDGE_WALL   = 3.0           # 帽外缘到件外缘的最小肉厚
CORNER_SEG  = 128           # 角弧分段 (整圆当量)

_m6_hp     = M6_PATTERN_SIDE / 2                       # 37.5
BASE_HALF  = _m6_hp + M6_HEAD_D / 2 + EDGE_WALL        # 46.75
BASE_SIDE  = 2 * BASE_HALF if TRIM_ENABLE else 100.0   # 93.5
CORNER_R   = math.hypot(_m6_hp, _m6_hp) + M6_HEAD_D / 2 + EDGE_WALL   # 62.283
# manifold 的 cylinder 是**内接**正多边形 (顶点在圆上, 边中点内缩 cos(pi/n)),
# 所以按外接放大, 保证多边形的**内切圆**正好是 CORNER_R (不吃掉那 0.02 mm 壁)。
CORNER_R_POLY = CORNER_R / math.cos(math.pi / CORNER_SEG)

# 2026-07-30 用户: 「定子电机的 4 个安装螺丝旋转 45°」
# 原 4×M3 是对角 25 的方形阵 → 孔在 (±8.839, ±8.839) (即对角落在 ±X/±Y 轴上)。
# 转 45° 后孔落到**坐标轴上**: (±12.5, 0) / (0, ±12.5)。
# (半径不变 12.5, 只是绕 Z 转了 45°。)
M3_ROT          = 0.0      # 2026-07-30 用户改回 0 (曾试 45° 让孔落坐标轴, 随即撤回)
M3_DIAG         = 25.0
M3_PATTERN_SIDE = M3_DIAG / math.sqrt(2)
M3_DIAM         = 3.2
CB_DIAM         = 7.0
CB_DEPTH        = 2.0

CENTER_CB_DIAM  = 12.0
CENTER_CB_DEPTH = 1.0

# ===== 降高 (2026-08-27 先降 5, 用户 2026-08-28 改口「减少 5mm 多了, 改成减少 2.5mm」) =====
# **现行降幅 = 2.5** (都是相对原始的 23 / 13 量的):
#   BOSS_H  23 → 20.5  (凸台顶 Z28 → Z25.5)
#   COLLAR_H 13 → 10.5 (套环顶 = COLLAR_TOP Z18 → Z15.5)
# 底盘 5 厚、各 OD/ID、孔位全不动。
# ★ **转子及以上整栈不动**: 电机 C4110 坐在**底盘顶 Z5**(不是套环顶), 转子面仍 31.7
#   ⇒ 承载面 42.2 / 屏 92.2..260.9 / 立柱 290 / 顶轴承 293..306 全部不变, 轴长不用重算。
# ★ **凸台顶与套环顶同降 ⇒ 中间 10 的落差不变**: mounting_flange 总高正好 10 (底 3 +
#   凸圈 7), 仍卡在两面之间; flange_disc(7) 同理。**两件都不用重印, 只是整体下移 2.5**。
#   动的只有装配里两个基准: assembly_v4.py / assembly_v3_1.py 的 BPC_COLLAR_TOP 18→15.5、
#   BPC_BOSS_TOP 28→25.5 (⚠ v3.1 也用这个件; v2/v2.1/v3 用的是 baseplate_collar_d100)。
# ⚠ 连带 1 (BOM): 8 颗定子锁紧螺丝夹持 3+7+COLLAR_H+5, 由 28 变 **25.5**。原配是
#   「M3×30 + 2mm 垫圈」(= 夹持 28 齐平)。**螺丝不用换, 把垫圈叠厚到 4.5** (30−4.5=25.5)
#   即可; 硬要单垫圈就得 M3×27.5 这种非标长度。不补这 2.5 会从底盘底面伸出去把定子顶起来。
# ⚠ 连带 2 (降幅改 2.5 后已不成立): 降 5 那版 COLLAR_H 正好 = COLLAR_NOTCH_H = 8,
#   走线缺口吃满套环全高, 套环成开口 30° 的 C 形弧。现在套环 10.5 > 缺口 8,
#   缺口之上还留 **2.5 过桥**, 套环回到"带槽的整环"。
# ⚠ 连带 3 (2026-08-28 用户已直接取消该沉孔): 降高会把顶面 Φ4.2×4 铜花窝从 Z14..18 往下带
#   (降 2.5 ⇒ Z6.5..10.5), 整段落进走线缺口 (Z5..13) 的 Z 区间, 67.5°/112.5° 那两颗到缺口
#   切面只剩 2.65 肉且整深临空。→ **「这个沉孔取消」(8 个)** ⇒ `FLANGE_CB_TOP_ENABLE = False`。

BOSS_OD = 65.0
BOSS_ID = 55.0
BOSS_H  = 23.0        # h28 变体: 保持降高前的 23 (现行件是 20.5)

# 2026-07-29 v4 (用户: "补成整圈"): 凸台+套环的 75..105° 走线缺口取消 → 整圈连续。
# ⚠⚠ 这个缺口原是**电机线唯一的出口** —— C4110 坐在凸台腔 (ID55) 里, 底盘 5mm 实心,
#    上方是转子, 线只能沿这个缺口径向穿出。补成整圈后电机线无出路, 装机前必须先想好
#    走线方案 (改走别处 / 现场开孔 / 把本开关设回 True)。
NOTCH_ENABLE = True
NOTCH_A_START = 75.0
NOTCH_A_END   = 105.0
NOTCH_H       = 8.0
NOTCH_R       = BOSS_OD / 2 + 2.0
NOTCH_SEG     = 24

# ===== Ring collar parameters (aligned with baseplate) =====
COLLAR_OD = 84.0   # 80→84 (2026-07-10): 铜花螺母孔外侧肉厚 1.65→3.65; M6 帽(Φ12.5)内缘 R43.75 留 1.75
COLLAR_ID = 65.0                  # = BOSS_OD → press-fit alignment
COLLAR_H  = 13.0                  # h28 变体: 保持降高前的 13 (现行件是 10.5)
COLLAR_Z0 = BASE_THICK            # ring bottom sits on base top (Z=5)
COLLAR_NOTCH_A_START = NOTCH_A_START
COLLAR_NOTCH_A_END   = NOTCH_A_END
COLLAR_NOTCH_H       = 8.0   # 6→8 (2026-07-13): 与凸台槽口同高, 内外开口一致
COLLAR_NOTCH_R       = COLLAR_OD / 2 + 2.0
COLLAR_NOTCH_SEG     = 28

assert abs(COLLAR_ID - BOSS_OD) < 1e-9, "collar ID must equal boss OD for alignment"

# ===== flange_disc 连接孔 (2026-07-10) =====
# flange_disc 内圈 8 孔 (PCD 72.5, R36.25, 22.5°+45k°) 坐在套环顶面上 —
# 对应加 8× Φ3.2 通孔 + Φ4.2×4 沉孔。
# **2026-08-28 用户「这个沉孔取消」(圈的是详图 C 上面那个, 8 个): 顶面沉孔关掉,
#   只保留底面那 8 个。** 本来 BOM 里也只备了底面 8 颗铜花螺母 (print sheet 原文
#   「这个方案不压顶面那 8 个」), 顶面窝一直是空着的; 降高后它又整段落进走线缺口的
#   Z 区、67.5°/112.5° 两颗只剩 2.65 肉临空 —— 取消掉正好把这个薄壁隐患一并消掉
#   (只剩 Φ3.2 时该处肉厚 4.75−1.6 = **3.15**)。
#   螺丝路径不受影响: 8 颗 M3×25 本来就是从法兰顶一路进**底盘底面**的铜花螺母。
# R36.25 在套环壁 R32.5..40 正中; 最近孔 (67.5°/112.5°) 距缺口边 (75°/105°)
# 弧向 4.73, 沉孔 Z14..18 与缺口 Z5..11 也不重叠。
FLANGE_HOLE_R     = 36.25            # = flange_disc PCD 72.5 / 2
FLANGE_HOLE_ANGS  = [22.5 + 45.0 * k for k in range(8)]
FLANGE_M3_DIAM    = 3.2
FLANGE_CB_DIAM    = 4.2
FLANGE_CB_DEPTH   = 4.0
FLANGE_CB_TOP_ENABLE = False   # 顶面沉孔 (2026-08-28 用户取消; True = 恢复)
FLANGE_CB_BOT_ENABLE = True    # 底面沉孔 = 真正压铜花螺母的那 8 个
COLLAR_TOP        = COLLAR_Z0 + COLLAR_H          # 18

# ===== Base =====
base = m3d.Manifold.cube((BASE_SIDE, BASE_SIDE, BASE_THICK), True)
base = base.translate((0, 0, BASE_THICK / 2))

if TRIM_ENABLE:
    _corner_cyl = m3d.Manifold.cylinder(BASE_THICK + 2, CORNER_R_POLY,
                                        CORNER_R_POLY, CORNER_SEG, False)
    base = base ^ _corner_cyl.translate((0, 0, -1.0))

# 无孔外形 (用于下面的螺丝帽落位校核)
footprint = base

# 4 × M6 corner holes (through)
m6_hp = M6_PATTERN_SIDE / 2
hole_h = BASE_THICK + 2
for sx in (-1, 1):
    for sy in (-1, 1):
        h = m3d.Manifold.cylinder(hole_h, M6_DIAM / 2, M6_DIAM / 2, 48, True)
        h = h.translate((sx * m6_hp, sy * m6_hp, BASE_THICK / 2))
        base = base - h

# 4 × M3 center holes + Φ7 counterbore (from bottom)
m3_hp = M3_PATTERN_SIDE / 2
_mr = math.radians(M3_ROT)
M3_HOLES = [( (sx*m3_hp)*math.cos(_mr) - (sy*m3_hp)*math.sin(_mr),
              (sx*m3_hp)*math.sin(_mr) + (sy*m3_hp)*math.cos(_mr) )
            for sx in (-1, 1) for sy in (-1, 1)]
for (mx, my) in M3_HOLES:
    h = m3d.Manifold.cylinder(hole_h, M3_DIAM / 2, M3_DIAM / 2, 32, True)
    h = h.translate((mx, my, BASE_THICK / 2))
    base = base - h
    cb_h = CB_DEPTH + 1.0
    cb = m3d.Manifold.cylinder(cb_h, CB_DIAM / 2, CB_DIAM / 2, 48, False)
    cb = cb.translate((mx, my, -1.0))
    base = base - cb

# Central Φ12 × 1 mm CB on top face
ccb_h = CENTER_CB_DEPTH + 1.0
ccb = m3d.Manifold.cylinder(ccb_h, CENTER_CB_DIAM / 2, CENTER_CB_DIAM / 2, 64, False)
ccb = ccb.translate((0.0, 0.0, BASE_THICK - CENTER_CB_DEPTH))
base = base - ccb

# ===== Boss =====
boss_outer = m3d.Manifold.cylinder(BOSS_H, BOSS_OD / 2, BOSS_OD / 2, 96, False)
boss_inner = m3d.Manifold.cylinder(BOSS_H + 2, BOSS_ID / 2, BOSS_ID / 2, 96, False)
boss_inner = boss_inner.translate((0, 0, -1))
boss = boss_outer - boss_inner
boss = boss.translate((0, 0, BASE_THICK))

# Boss notch (cuts the boss wall only)
wedge_pts = [(0.0, 0.0)]
for i in range(NOTCH_SEG + 1):
    a_deg = NOTCH_A_START + i * (NOTCH_A_END - NOTCH_A_START) / NOTCH_SEG
    a_rad = math.radians(a_deg)
    wedge_pts.append((NOTCH_R * math.cos(a_rad), NOTCH_R * math.sin(a_rad)))
notch = m3d.CrossSection([wedge_pts]).extrude(NOTCH_H + 0.1)
notch = notch.translate((0, 0, BASE_THICK))
if NOTCH_ENABLE:
    boss = boss - notch

# ===== Ring collar (sleeved over boss) =====
collar_outer = m3d.Manifold.cylinder(COLLAR_H, COLLAR_OD / 2, COLLAR_OD / 2, 128, False)
collar_inner = m3d.Manifold.cylinder(COLLAR_H + 2, COLLAR_ID / 2, COLLAR_ID / 2, 128, False)
collar_inner = collar_inner.translate((0, 0, -1))
collar = collar_outer - collar_inner
collar = collar.translate((0, 0, COLLAR_Z0))

# Collar notch (aligned with boss notch on +Y side)
c_wedge_pts = [(0.0, 0.0)]
for i in range(COLLAR_NOTCH_SEG + 1):
    a_deg = COLLAR_NOTCH_A_START + i * (COLLAR_NOTCH_A_END - COLLAR_NOTCH_A_START) / COLLAR_NOTCH_SEG
    a_rad = math.radians(a_deg)
    c_wedge_pts.append((COLLAR_NOTCH_R * math.cos(a_rad), COLLAR_NOTCH_R * math.sin(a_rad)))
c_notch = m3d.CrossSection([c_wedge_pts]).extrude(COLLAR_NOTCH_H + 0.1)
c_notch = c_notch.translate((0, 0, COLLAR_Z0 - 0.05))
if NOTCH_ENABLE:
    collar = collar - c_notch

# ===== Combine =====
part = base + boss + collar

# ===== 8× flange_disc 连接孔: Φ3.2 通 (Z0..COLLAR_TOP) + Φ4.2×4 沉孔 =====
# 顶面沉孔 2026-08-28 取消 ⇒ 只剩底面那 8 个 (Z0..4), Φ3.2 中段 Z4..COLLAR_TOP
for a in FLANGE_HOLE_ANGS:
    hx = FLANGE_HOLE_R * math.cos(math.radians(a))
    hy = FLANGE_HOLE_R * math.sin(math.radians(a))
    thr = m3d.Manifold.cylinder(COLLAR_TOP + 2, FLANGE_M3_DIAM / 2,
                                FLANGE_M3_DIAM / 2, 32, False)
    part = part - thr.translate((hx, hy, -1.0))
    cb = m3d.Manifold.cylinder(FLANGE_CB_DEPTH + 1, FLANGE_CB_DIAM / 2,
                               FLANGE_CB_DIAM / 2, 32, False)
    if FLANGE_CB_TOP_ENABLE:
        part = part - cb.translate((hx, hy, COLLAR_TOP - FLANGE_CB_DEPTH))
    if FLANGE_CB_BOT_ENABLE:
        part = part - cb.translate((hx, hy, -1.0))

# ===== 外形裁切校核 (2026-08-19) =====
# ⚠ 教训 (记忆): 旋转/贴合类间隙不要用"半径带/占位网格"近似 —— 这里直接用布尔判定。
if TRIM_ENABLE:
    assert COLLAR_OD / 2 <= BASE_HALF - 1e-9, "套环 OD 超出收窄后的直边"
    assert COLLAR_OD / 2 <= CORNER_R - 1e-9, "套环 OD 超出角弧"
    assert BASE_HALF < 50.0, "没有真的收窄"
    _head_out = 0.0
    for _sx in (-1, 1):
        for _sy in (-1, 1):
            _head = m3d.Manifold.cylinder(BASE_THICK, M6_HEAD_D / 2,
                                          M6_HEAD_D / 2, 96, False)
            _head = _head.translate((_sx * _m6_hp, _sy * _m6_hp, 0.0))
            _head_out += (_head - footprint).volume()
    assert _head_out < 1e-3, (
        f"M6 帽 (Φ{M6_HEAD_D:g}) 悬出件外 {_head_out:.4f} mm³ —— 外形切过头了"
    )
    _fp = np.asarray(footprint.to_mesh().vert_properties)[:, :2]
    _r = np.hypot(_fp[:, 0], _fp[:, 1])
    _wall = _r.max() - (math.hypot(_m6_hp, _m6_hp) + M6_HEAD_D / 2)
    print(f"  外形裁切: 直边 ±{BASE_HALF:g} (边长 {BASE_SIDE:g}) + 四角 R{CORNER_R:.3f}"
          f"  [多边形内切 {CORNER_R_POLY*math.cos(math.pi/CORNER_SEG):.3f}]")
    print(f"    M6 帽 Φ{M6_HEAD_D:g} 落位: 4 角全部落在件内 (悬出 {_head_out:.6f} mm³)"
          f", 帽外缘→件外缘壁厚 {_wall:.2f}")
    print(f"    件外接半径 {_r.max():.3f} (原方角 {math.hypot(50.0, 50.0):.3f})")

# ===== Export STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("baseplate_collar_v4_h28.stl")
_header = b"POV3D baseplate_collar_v4_h28"
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
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}")
print(f"  volume:        {part.volume():8.2f} mm^3")
print(f"  surface area:  {part.surface_area():8.2f} mm^2")
print(f"  走线缺口: {'开 '+str(NOTCH_A_START)+chr(176)+'-'+str(NOTCH_A_END)+chr(176) if NOTCH_ENABLE else '已关闭 → 凸台/套环整圈连续 (v4)'}")
print(f"  4×M3 电机孔 (转 {M3_ROT:g}°): " + ", ".join(f"({x:+.2f},{y:+.2f})" for x,y in M3_HOLES)
      + f"  (半径 {M3_DIAG/2:g})")
_cb_faces = "+".join([f for f, on in (("顶面", FLANGE_CB_TOP_ENABLE), ("底面", FLANGE_CB_BOT_ENABLE)) if on]) or "无"
print(f"  flange 连接孔 8× Φ{FLANGE_M3_DIAM:g} 通 + Φ{FLANGE_CB_DIAM:g}×{FLANGE_CB_DEPTH:g} 沉孔 **{_cb_faces}** "
      f"@ R{FLANGE_HOLE_R:g}, {FLANGE_HOLE_ANGS[0]:g}°+45k° (配 M3×4×4.5 铜花螺母)"
      + ("" if FLANGE_CB_TOP_ENABLE else "  [顶面沉孔 2026-08-28 取消]"))

# Sanity-check binary STL size
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, (
    f"STL size mismatch: expected {_expected} (84+{len(tris)}*50), got {_actual}"
)
print(f"  STL size OK: {_actual} bytes (= 84 + {len(tris)}*50)")
