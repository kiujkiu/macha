"""
portal_tee_v3 — v3 屏幕底部支撑, T 型件完整版 (2026-07-22 深夜, 用户分步:
T 型 [底条装转子两螺丝, 每面厚 5, 整件厚 10] + 两端→梃顶大三角加强筋 +
顶部内伸托屏小台 [屏只锁靠边 ±64 那颗螺丝], 左右对称; ×2 转 180° 对放)。

盘系 (Z0 = 承载面):
  · 底横条: X ±33.5 × 高 5 (Z 0..5) × 厚 10 (Y 66.6..76.6, 居中环孔线 71.601);
    2×Φ3.4 竖直孔 @ (±29.658, 71.601)
  · 中央竖梃: 宽 5 (X ±2.5) × 厚 10 × Z 5..50 (梃顶高度 = 屏幕安装高度)
  · 梯形加强壁 (2026-07-23 用户: 补全成梯形): X-Z 面完整梯形
    (±33.5,5)-(±10,45), 厚 5, **齐外侧面 (Y 71.6..76.6)** —— 正视轮廓 = 整梯形,
    斜边从底条两端直达顶托外缘; 壁在转子螺丝上方 → 2×Φ7 竖直工艺井
    (Z5..20) 供螺丝头+批头进出
  · 顶平板托 (2026-07-22 深夜用户: 顶部一个平面/梯形): Z 45..50 单块平板,
    俯视梯形 — 外边 (Y76.6) 宽 20 (X±10), 内边 (Y59.6) 宽 13.4 (X±6.7,
    = 屏厚同宽); 托面 Z50 = 屏底一整个平面; 1×Φ3.2 @ (0, 64), M3×12 锁屏,
    **Φ7 螺丝帽会咬竖梃内上角 0.9 → 托底开 Φ7.5×4 让位窝 (Z41..45), 帽沉入**
打印: **平躺, 外侧面 (Y=76.6) 贴床** — 所有特征自床面起, 零支撑。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

BAR_X, BAR_H = 33.5, 5.0
THK_Y0, THK_Y1 = 66.601, 76.601        # 厚 10, 居中 71.601
FOOT_HOLES = [(29.658, 71.601), (-29.658, 71.601)]
FOOT_HOLE_D = 3.4
STEM_HW, STEM_Z1 = 2.5, 50.0           # 托面 Z50 = 屏幕安装高度
GUS_T = 5.0                            # 三角筋厚 (齐外侧面)
WELL_D, WELL_Z1 = 7.0, 20.0            # 转子螺丝工艺井
PAD_T = 5.0                            # 顶平板托厚
PAD_Z0 = STEM_Z1 - PAD_T               # 45 (平板托 Z45..50; 梃/筋到 45)
PAD_Y0 = 59.601                        # 托内边 (内伸 7)
# ===== v3.1 偏心屏实验 (2026-07-30) =====
# 目标: 让双面屏的**其中一面正好落在旋转轴平面上** (现在两面在 X=±6.7, 各自
# 吃 6.7 的成像盲区 → 中心 Φ13.4 黑洞)。屏整体偏移 SCR_ECC 后, 贴轴那面盲区
# 归零, 另一面变 Φ26.8。
# ★ 结构死结与解法: 两个 T 件是**同件转 180°**放的。若把锁屏孔挪到 (+6.7,+64),
#   转 180° 后第二件的孔落在 (-6.7,-64), 两件会把屏往相反方向拉 → 装不上。
#   解法 = 顶托**对称加宽** + X 方向三个**离散孔** (-ECC / 0 / +ECC):
#   转 180° 后孔位仍是 (±ECC, -64) 与 (0,-64), 两件都有 +ECC 那个孔可用 ✓,
#   而且同一个件还支持居中装法 —— 拧不同的孔即可在「居中/偏心」间切换做对照,
#   不必重印。用离散孔而非长槽是为了实验位置可重复。
SCR_ECC = 6.7                          # 偏心量 = 屏半厚 (使一面贴轴)
SCR_T = 13.4                           # 屏厚
# 托要同时覆盖屏在 X 0..+13.4 (本件) 与 -13.4..0 (转 180° 的第二件) 两种落位
PAD_HW_MIN = SCR_T + 2.6               # 16.0 —— 半宽下限 (含 2.6 边料)
PAD_WI, PAD_WO = PAD_HW_MIN, PAD_HW_MIN   # v3.1: 托改**等宽矩形** (原梯形 6.7→10)
SCR_D, SCR_Y = 3.2, 64.0               # 屏底靠边螺丝孔
SCR_XS = (-SCR_ECC, 0.0, SCR_ECC)      # v3.1: 三个离散孔位 (X), 见上方说明

def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def tri_xz(pts, y0, t):
    a2 = sum(pts[i][0]*(pts[(i+1) % 3][1]-pts[(i-1) % 3][1]) for i in range(3))
    if a2 < 0:
        pts = list(reversed(pts))
    return m3d.CrossSection([pts]).extrude(t).rotate((90, 0, 0)).translate((0, y0 + t, 0))

def tri_yz(pts, x0, t):
    a2 = sum(pts[i][0]*(pts[(i+1) % 3][1]-pts[(i-1) % 3][1]) for i in range(3))
    if a2 < 0:
        pts = list(reversed(pts))
    return m3d.CrossSection([pts]).extrude(t).rotate((90, 0, -90)).translate((x0, 0, 0))

GY0 = THK_Y1 - GUS_T                   # 筋齐外侧面: Y 71.601..76.601
part = box(-BAR_X, BAR_X, THK_Y0, THK_Y1, 0.0, BAR_H)
part += box(-STEM_HW, STEM_HW, THK_Y0, THK_Y1, BAR_H, PAD_Z0)
# 梯形加强壁 (齐外侧面): (±33.5,5) → (±10,45)
wp = [(-BAR_X, BAR_H), (BAR_X, BAR_H), (PAD_WO, PAD_Z0), (-PAD_WO, PAD_Z0)]
wa = sum(wp[i][0]*(wp[(i+1) % 4][1]-wp[(i-1) % 4][1]) for i in range(4))
if wa < 0:
    wp.reverse()
wall = m3d.CrossSection([wp]).extrude(GUS_T).rotate((90, 0, 0)).translate((0, GY0 + GUS_T, 0))
part += wall
# 顶平板托: 俯视梯形 (外边 ±PAD_WO @Y76.6, 内边 ±PAD_WI @Y59.6), Z 45..50
tp = [(PAD_WO, THK_Y1), (-PAD_WO, THK_Y1), (-PAD_WI, PAD_Y0), (PAD_WI, PAD_Y0)]
a2 = sum(tp[i][0]*(tp[(i+1) % 4][1]-tp[(i-1) % 4][1]) for i in range(4))
if a2 < 0:
    tp.reverse()
part += m3d.CrossSection([tp]).extrude(PAD_T).translate((0.0, 0.0, PAD_Z0))
for (hx, hy) in FOOT_HOLES:
    part -= m3d.Manifold.cylinder(BAR_H + 2, FOOT_HOLE_D/2, FOOT_HOLE_D/2, 32, False)\
        .translate((hx, hy, -1.0))
    part -= m3d.Manifold.cylinder(WELL_Z1 - BAR_H, WELL_D/2, WELL_D/2, 32, False)\
        .translate((hx, hy, BAR_H))                                    # 工艺井 (筋上)
for _sx in SCR_XS:                                                     # v3.1: 3 个离散孔位
    part -= m3d.Manifold.cylinder(PAD_T + 2, SCR_D/2, SCR_D/2, 32, False)\
        .translate((_sx, SCR_Y, PAD_Z0 - 1.0))                         # 屏螺丝孔
    part -= m3d.Manifold.cylinder(4.0 + 0.1, 7.5/2, 7.5/2, 32, False)\
        .translate((_sx, SCR_Y, PAD_Z0 - 4.0))                         # Φ7.5×4 帽让位窝

mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("portal_tee_v3_1.stl")
with out.open("wb") as f:
    f.write(b"POV3D portal_tee_v3_1 (WIP)".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
r_max = float(np.hypot(verts[:, 0], verts[:, 1]).max())
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3  r_max {r_max:.2f}")
print(f"  底横条 {2*BAR_X:g}×10×{BAR_H:g} (2×Φ{FOOT_HOLE_D:g} @ ±29.658 + Φ{WELL_D:g} 工艺井); 竖梃 {2*STEM_HW:g}×10 到 Z{STEM_Z1:g}")
print(f"  梯形加强壁 (厚 {GUS_T:g}, 齐外侧面, ±{BAR_X:g}→±{PAD_WO:g}); 顶平板托梯形 外{2*PAD_WO:g}/内{2*PAD_WI:g}×深{THK_Y1-PAD_Y0:g}×{PAD_T:g} (托面 Z{STEM_Z1:g}=屏底), 屏孔 3×Φ{SCR_D:g}@X{SCR_XS}/Y{SCR_Y:g} + Φ7.5×4 帽让位窝")
print(f"  平躺打印 (外侧面 Y{THK_Y1:g} 贴床, 全特征落床零支撑); ×2 转 180° 对放; 屏每侧 1 颗 M3×12")
