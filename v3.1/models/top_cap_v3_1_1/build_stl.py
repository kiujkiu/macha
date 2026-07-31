"""
top_cap_v3_1 — v3 双屏顶部薄压条 v3 (2026-07-22: 用户"顶部只要连接左右两个
M3 孔, 做薄一点" → 31.75 厚压梁块改 7 厚扁条, 五金链按 1cm 分辨率整体下移)。

装配系几何 (导出转打印姿态: 顶面贴床):
  · 扁条 18 (X ±9) × 140 (Y ±70) × 7 厚 (Z 260.95..267.95); 底面 = 屏顶
    260.95 (42.2 + 50 + 168.75), 顶 267.95 = CAPTOP_V3。
  · 轴: Φ6.2 通孔 + 底面 Φ13×2.7 头窝 (开口朝下) —— M6×20 平头从下装入,
    头 260.95..263.65 (头面贴屏顶中央空置孔区上方), 杆到 280.95, 拧进
    Φ8×30 单头内丝螺柱 (267.95..297.95, 底坐条顶兼锁紧, 旋入 13)。
    柱 Φ8×280, 轴承 283..288 / 291..296, 螺柱顶 297.95 完整穿过上 688 顶
    296 (整机 322.7 → 297.95)。⚠ 先装 M6 再压屏 (头窝被屏顶盖住后无法送入)。
  · 屏顶固定 2×: (0, ±64) Φ3.2 平面通孔, 盘头 M3×12~14 从上直拧进屏顶孔
    (旋入 5~7, 孔深 10); 中央孔 (0,0) 被轴占, 屏顶中央孔空置。
打印: 顶面贴床 (头窝朝上), 18×140×7, 零支撑; 全件 100% 填充。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# ===== v3.1 偏心屏 (2026-07-30, 用户选方案 A) =====
# 屏整体偏移 +SCR_ECC 让一面贴轴 → 屏占 X 0..13.4 (原 ±6.7)。
# 原压条 18 宽 (X±9) 盖不住偏心后的屏 (差 4.4) → **对称加宽到 ±16 (32 宽)**:
#   · 同时盖住居中 (±6.7) 与偏心 (0..13.4) 两种落位, 与 portal_tee_v3_1 的
#     3 个离散孔配套, 拧不同孔即可切换实验, 压条不用重印
#   · 光电那一套 (绕 M(0,-45) 转 22.19° 使光轴过圆心, 六轮改出来的) **原位不动**
#   · M6 轴仍在 (0,0), Φ13 头窝外留 16-6.5 = 9.5 壁 (原 2.5, 更宽裕)
# 代价: 22g → 约 39g; -X 侧 16mm 悬空 (下面没屏) —— 正好用作配重区, 见 CW_*
SCR_ECC = 6.7
BLK_X, BLK_Y = 16.0, 70.0            # v3.1: 半宽 9 → 16
BAR_Z0, BAR_Z1 = 260.95, 267.95      # 底面 = 屏顶, 条厚 7
AXIS_BORE = 6.2                      # M6 杆通孔
HEAD_D, HEAD_T = 13.0, 2.7           # M6 平头头窝 (开口朝下)
SCREW_YS, SCREW_D = (64.0, -64.0), 3.2   # 屏顶 M3, Φ3.2 平面通孔
SCREW_XS = (-SCR_ECC, 0.0, SCR_ECC)      # v3.1: 3 个离散 X 孔位 (同 portal_tee_v3_1)
# 配重孔 (细调用): -X 侧悬空区, 一排 M6 通孔。偏心使不平衡指向 +X, 配重放 -X。
# ⚠ 力臂有限 (最远 -13) → 只够细调; 大头配重应放转子盘大半径处 (见 README 核算)
# ★ 对射管焊脚避空 (2026-07-30): v3 压条只到 X±9, 对射管那两个焊脚落在 X≈+12/+14
# 正好悬在条外, 所以原设计不需要避空 (记忆里明确记着"焊脚落条外悬空无需避空,
# ⚠模块挪位后凸出焊脚落点要重查")。v3.1 把条加宽到 ±16 后**焊脚就压到条上了**
# —— 实测两处各扎入 1.5 深、约 1×1 截面 (X 11.67..12.67 / 13.99..14.98,
# Y ≈ -32, Z 266.45..267.95)。这里开两个避空孔 (Φ3 通, 单边余量 ~1)。
LEG_RELIEF = True
LEG_D = 3.0
LEG_XY = ((12.17, -32.47), (14.49, -31.53))   # 实测焊脚中心 (压条零件系 XY)

CW_ENABLE = True
CW_D = 6.5                               # M6 通孔
CW_X = -11.0                             # 配重孔 X (孔边距条边 16-11-3.25 = 1.75)
CW_YS = tuple(float(v) for v in range(-56, 57, 14))   # 9 个, 间距 14
# 2026-07-23 v5: 光电模块直贴条顶 (梁线 r≈32, 模块中心 Y≈-30), 2×M3 @
# (-6,-23)/(-6,-37) + 底面方螺母囚窝 5.8²×2.2 (压条压上屏后螺母被囚, 无攻牙)
# 六改 (用户): 不加宽压条 — 模块绕两孔连线中点 M(0,-45) 旋转 SEN_TH, 使光轴
# (对射连线, 平行孔线偏距 17) 过圆心: sin(SEN_TH) = 17/45 → 22.187°。
# 叉臂扫掠为同心环, 刀片净通道 r36.78..46.66 (刀片 r40.2..43.2, 余量 ~3.4/侧)。
# 对射管焊脚旋转后落条外悬空 (无需避空); 排针尾避空槽随转 (斜置矩形)。
import math
SEN_TH = math.degrees(math.asin(17.0 / 45.0))        # 22.187°
_s, _c = math.sin(math.radians(SEN_TH)), math.cos(math.radians(SEN_TH))
SEN_M = (0.0, -45.0)                                  # 孔线中点 (旋转中心)
SEN_HOLES = [(7*_s, -45.0 - 7*_c), (-7*_s, -45.0 + 7*_c)]   # (±2.644, -51.481/-38.519)
SEN_CB_D, SEN_CB_T = 7.5, 2.5   # 六改: 头沉孔 Φ6.5→7.5 (用户: 小了)
SEN_SLOT_L, SEN_SLOT_W = 9.0, 8.0             # 排针尾避空槽 (穿透, 斜置: 长轴沿孔线;
SEN_SLOT_C = (0.0, -45.0)                     # 九改: 以两孔连线为对称轴 (中心 = M) 且加宽 6→8;
SEN_SLOT_ANG = SEN_TH - 90.0                  # 尾 @ 偏线 1.2 仍被覆盖, 槽端距孔缘 0.9)

def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

part = box(-BLK_X, BLK_X, -BLK_Y, BLK_Y, BAR_Z0, BAR_Z1)

part -= cyl(AXIS_BORE, 0, 0, BAR_Z0-1, BAR_Z1+1)             # 轴 Φ6.2 通孔
part -= cyl(HEAD_D, 0, 0, BAR_Z0-1, BAR_Z0+HEAD_T)           # Φ13×2.7 头窝 (朝下)
part -= m3d.Manifold.cube((SEN_SLOT_L, SEN_SLOT_W, BAR_Z1-BAR_Z0+2), False)\
    .translate((-SEN_SLOT_L/2, -SEN_SLOT_W/2, 0.0))\
    .rotate((0, 0, SEN_SLOT_ANG))\
    .translate((SEN_SLOT_C[0], SEN_SLOT_C[1], BAR_Z0-1))          # 排针尾避空槽 (穿透, 斜置)
for (sx, sy) in SEN_HOLES:                                    # 光电模块 2×M3
    part -= cyl(3.2, sx, sy, BAR_Z0-1, BAR_Z1+1)
    part -= cyl(SEN_CB_D, sx, sy, BAR_Z0-1, BAR_Z0+SEN_CB_T)  # 底面头窝
for sy in SCREW_YS:                                          # v3.1: 3×2 屏顶 M3 通孔
    for sx in SCREW_XS:
        part -= cyl(SCREW_D, sx, sy, BAR_Z0-1, BAR_Z1+1, 32)
if LEG_RELIEF:                                               # 对射管焊脚避空 ×2
    for (lx, ly) in LEG_XY:
        part -= cyl(LEG_D, lx, ly, BAR_Z0-1, BAR_Z1+1, 32)
if CW_ENABLE:                                                # 配重孔一排 (细调)
    for cy in CW_YS:
        part -= cyl(CW_D, CW_X, cy, BAR_Z0-1, BAR_Z1+1, 32)

# ===== 导出为打印姿态 (条顶贴床): print = (x, -y, BAR_Z1 - z) =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3].copy()
verts[:, 1] = -verts[:, 1]
verts[:, 2] = BAR_Z1 - verts[:, 2]
tris = np.asarray(mesh.tri_verts)[:, ::-1]           # 与装配读取端翻绕向配套
out = Path(__file__).with_name("top_cap_v3_1_1.stl")
with out.open("wb") as f:
    f.write(b"POV3D top_cap_v3_1_1 (print pose)".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3 (~{part.volume()*1.27/1000:.0f} g PETG)")
print(f"  薄压条 {2*BLK_X:g}×{2*BLK_Y:g}×{BAR_Z1-BAR_Z0:g} (asm {BAR_Z0:g}..{BAR_Z1:g}, 底=屏顶)")
print(f"  轴 Φ{AXIS_BORE:g} 通孔 + Φ{HEAD_D:g}×{HEAD_T:g} 底面头窝 (M6×20 平头, 先装后压屏); "
      f"{len(SCREW_XS)}×2 Φ{SCREW_D:g} @ (X{SCREW_XS}, Y±64), 盘头 M3×12~14; "
      f"配重 {len(CW_YS) if CW_ENABLE else 0}×Φ{CW_D:g} @ X{CW_X:g}; "
      f"对射管焊脚避空 {len(LEG_XY) if LEG_RELIEF else 0}×Φ{LEG_D:g} @ {LEG_XY}")
