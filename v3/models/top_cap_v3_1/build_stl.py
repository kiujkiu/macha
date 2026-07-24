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

BLK_X, BLK_Y = 9.0, 70.0             # 扁条半宽/半长 (Φ13 头窝外留 2.5 壁; ±64 孔外留 6)
BAR_Z0, BAR_Z1 = 260.95, 267.95      # 底面 = 屏顶, 条厚 7
AXIS_BORE = 6.2                      # M6 杆通孔
HEAD_D, HEAD_T = 13.0, 2.7           # M6 平头头窝 (开口朝下)
SCREW_YS, SCREW_D = (64.0, -64.0), 3.2   # 2× 屏顶 M3, Φ3.2 平面通孔
# 2026-07-23 v5: 光电模块直贴条顶 (梁线 r≈32, 模块中心 Y≈-30), 2×M3 @
# (-6,-23)/(-6,-37) + 底面方螺母囚窝 5.8²×2.2 (压条压上屏后螺母被囚, 无攻牙)
SEN_HOLES = [(0.0, -38.0), (0.0, -52.0)]   # 三改: 18 宽正中; 四改: 外移 (模块中心 capY−45, 旋转扫掠余量 2.1)
# 2026-07-23 二改 (用户: 按老 v2 支架的孔型) — Φ3.2 平通 + 底面 Φ6.5×2.5
# 头窝 (M3×12 压条上屏前从下插入, 同 M6 头窝逻辑), 模块平贴条顶, 螺母锁
# PCB 上面 (可从上拆装); 焊脚避空挖穿 (老方案 "3 避空槽挖穿"): 条上只有
# 排针尾 @ (X−1.2, −27.5..−32.5) → 穿透槽; 4 对管脚在条外悬空。
# 梁线 (capX+17, capY−45) → r_v≈48.1; 弦偏移使叉臂扫掠带加宽, 静刀片净通道
# r 44.7..51.9 — 刀片 3 宽 @ 46.8..49.8, 双侧扫掠余量 ~2.1 (frame_B 同步)。
SEN_CB_D, SEN_CB_T = 6.5, 2.5
SEN_LEAD_SLOT = (-3.5, 1.0, -49.0, -41.0)    # 排针尾避空槽 (穿透; 尾 @ X-1.2, 距两孔缘各 1.4)

def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, seg, False).translate((x, y, z0))

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

part = box(-BLK_X, BLK_X, -BLK_Y, BLK_Y, BAR_Z0, BAR_Z1)

part -= cyl(AXIS_BORE, 0, 0, BAR_Z0-1, BAR_Z1+1)             # 轴 Φ6.2 通孔
part -= cyl(HEAD_D, 0, 0, BAR_Z0-1, BAR_Z0+HEAD_T)           # Φ13×2.7 头窝 (朝下)
part -= m3d.Manifold.cube((SEN_LEAD_SLOT[1]-SEN_LEAD_SLOT[0],
                           SEN_LEAD_SLOT[3]-SEN_LEAD_SLOT[2],
                           BAR_Z1-BAR_Z0+2), False)\
    .translate((SEN_LEAD_SLOT[0], SEN_LEAD_SLOT[2], BAR_Z0-1))   # 排针尾避空槽 (穿透)
for (sx, sy) in SEN_HOLES:                                    # 光电模块 2×M3
    part -= cyl(3.2, sx, sy, BAR_Z0-1, BAR_Z1+1)
    part -= cyl(SEN_CB_D, sx, sy, BAR_Z0-1, BAR_Z0+SEN_CB_T)  # 底面头窝
for sy in SCREW_YS:                                          # 2× 屏顶 M3 通孔
    part -= cyl(SCREW_D, 0, sy, BAR_Z0-1, BAR_Z1+1, 32)

# ===== 导出为打印姿态 (条顶贴床): print = (x, -y, BAR_Z1 - z) =====
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3].copy()
verts[:, 1] = -verts[:, 1]
verts[:, 2] = BAR_Z1 - verts[:, 2]
tris = np.asarray(mesh.tri_verts)[:, ::-1]           # 与装配读取端翻绕向配套
out = Path(__file__).with_name("top_cap_v3_1.stl")
with out.open("wb") as f:
    f.write(b"POV3D top_cap_v3_1 (print pose)".ljust(80, b" "))
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
      f"2× Φ{SCREW_D:g} @ (0, ±64), 盘头 M3×12~14")
