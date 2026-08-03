"""
counterweight_arm — 转子配重臂 (2026-08-03, 用户: "在 shroud_half A 和 B 上各增加
2 个 M3 通孔 ... 再做一个件可以锁在这两个通孔上面, 这个新增的件用来锁 M6 螺丝,
这个件我理解应该需要 shroud_half A 和 B 一起才能锁住, 旋转不要超出现在的旋转边缘,
应该是直径 17cm")。

**v3 / v3.1 两条线共用一件** —— 罩子 −X 侧的顶板几何两版完全一样 (差异只在 +X 侧的
屏缝), 所以放在共享 models/ 库里, 不分版本。

坐标系 = 罩子零件系 (= 屏局部系) 的 XY, **Z0 = 罩顶面 = 罩零件系 Z50 = 装配 Z92.2**。
装配 = rot_z(part, ROTOR_ROT + V3_SCR_ROT) + Z 92.2, 与罩子同步共转。

为什么在 −X: v3.1 偏心屏往 +X 偏 6.7 → 不平衡矢量在 +X, 修正配重必须在 **−X**;
而罩子对开缝正好是 Y=0 平面 (含 X 轴) ⇒ 骑在 −X 上天然跨缝, 4 颗 M3 里 2 颗进半 A、
2 颗进半 B ⇒ **本件顺带把两半在顶部连成一体** (接缝原来除各自 2 颗立柱螺丝外无连接件)。

几何:
  · 底板  6 厚 (Z0..6), X −85..−44, |Y|≤19, 外缘被 R85 圆弧裁掉 ⇒ **不超 Φ170**
  · M6 座 Φ16 凸台 @ (−75.5, 0), 加高到 Z10 (总 10 厚); 外缘 r83.5 对 R85 余 1.5
  · M6 孔  底面 对边 10.3 × 深 4.5 **六角窝** (卡 M6 六角头, 防转) + Φ6.5 通到顶面;
           头上方留 5.5 厚台肩承预紧
  · M3 孔  4× Φ3.4 @ (−50, ±14) / (−72, ±14), 对罩顶的 4 个铜花螺母

配重怎么加 (关键: 全部从机器外面操作, 不用拆罩):
  M6 六角头**朝下**卡在六角窝里 (窝底就压在罩顶面上, 转不动) → 杆朝上穿出 →
  从上面套垫圈/螺母, 拧紧即可。加减配重 = 加减垫圈, 螺栓换长的即可, **无上限**
  (罩顶往上到顶轴承架 290 全是空的)。
    · Φ18×1.6 大垫圈 2.84 g/片 = 1.78 g/mm 叠高 (比叠 M6 螺母 0.46 g/mm 划算 4 倍)
    · 力臂 r75.5 ⇒ 每 10 g 配重 = 755 g·mm
  ⚠ 必须防松: 最上面用尼龙锁紧螺母, 或螺纹胶。

打印: **底面贴床, 零支撑**。六角窝顶面是 10.3 的桥接 (常规参数即可, 该面是螺栓
承压台肩, 桥接质量差就把该层填充调高)。
BOM: M3×16 ×4 (进罩顶铜花螺母) + M6 六角头螺栓 ×1 (长度按配重量选) +
     M6 垫圈/螺母若干 + M6 尼龙锁紧螺母 ×1。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

# --- 与 rotor_shroud 对齐的参数 (改这里前先改罩子的 CWM_*) ---
R_OUT = 85.0                          # 罩外径 R = 旋转包络上限 (用户: 不超 Φ170)
M3_XS, M3_Y = (-50.0, -72.0), 14.0    # 罩顶 4 个铜花螺母位
M3_D = 3.4                            # M3 过孔

# --- 本件 ---
BASE_T = 6.0                          # 底板厚
X_IN = -44.0                          # 内端 (内排 M3 −50 往里留 6)
HW = 19.0                             # 半宽 (M3 在 ±14 → 边距 5)
M6_R = 75.5                           # M6 力臂
M6_BOSS_D, M6_BOSS_T = 16.0, 10.0     # M6 座凸台 (外缘 r83.5, 对 R85 余 1.5)
M6_D = 6.5                            # M6 过孔
M6_HEX_AF, M6_HEX_H = 10.3, 4.5       # 六角窝 (M6 六角头对边 10 + 0.3, 头高 4 + 0.5)

SEG = 128


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def cyl(h, d, z0=0.0, seg=SEG):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, seg, False).translate((0.0, 0.0, z0))


def hexprism(af, h, z0):
    r = af / math.sqrt(3.0)                       # 对边 af → 外接圆半径
    return m3d.Manifold.cylinder(h, r, r, 6, False).rotate((0, 0, 30)).translate((0, 0, z0))


# 底板: 矩形 ∩ R85 圆盘 (外缘随罩子外径, 保证不超 Φ170)
part = box(-R_OUT - 1, X_IN, -HW, HW, 0.0, BASE_T) ^ cyl(BASE_T, 2 * R_OUT)
# M6 座凸台
part += (cyl(M6_BOSS_T, M6_BOSS_D).translate((M6_R * -1.0, 0.0, 0.0)) ^ cyl(M6_BOSS_T, 2 * R_OUT))
# M6: 底面六角窝 + 通孔
part -= hexprism(M6_HEX_AF, M6_HEX_H + 1.0, -1.0).translate((-M6_R, 0.0, 0.0))
part -= cyl(M6_BOSS_T + 2.0, M6_D, -1.0, 48).translate((-M6_R, 0.0, 0.0))
# M3 ×4
for mx in M3_XS:
    for sy in (1.0, -1.0):
        part -= cyl(BASE_T + 2.0, M3_D, -1.0, 32).translate((mx, sy * M3_Y, 0.0))

assert len(part.decompose()) == 1, "配重臂不是单连通体"
_m = part.to_mesh()
_v = np.asarray(_m.vert_properties)[:, :3]
_r = np.hypot(_v[:, 0], _v[:, 1])
assert _r.max() <= R_OUT + 1e-6, f"超出 Φ{2*R_OUT:g}: r_max {_r.max():.3f}"

# 质心半径 (本件自身也是配重, 装上去就有固有偏置)
_mesh_v = _v[np.asarray(_m.tri_verts)]
_sv = np.einsum("ij,ij->i", _mesh_v[:, 0], np.cross(_mesh_v[:, 1], _mesh_v[:, 2])) / 6.0
_cen = ((_mesh_v.sum(1) / 4.0) * _sv[:, None]).sum(0) / _sv.sum()
VOL = abs(float(_sv.sum()))
MASS = VOL * 1.27 / 1000.0

out = Path(__file__).with_name("counterweight_arm.stl")
tris = np.asarray(_m.tri_verts)
with out.open("wb") as f:
    f.write(b"POV3D counterweight_arm (rotor, shared v3/v3.1)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = _v[t[0]], _v[t[1]], _v[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris) * 50 == out.stat().st_size

print("=" * 76)
print(f"wrote {out.name}  {len(tris)} tris, 连通体 {len(part.decompose())} ✓")
print(f"  底板 {BASE_T:g} 厚 × |Y|≤{HW:g} × X {-R_OUT:g}..{X_IN:g} (外缘 R{R_OUT:g} 弧裁) ; "
      f"M6 座 Φ{M6_BOSS_D:g} × {M6_BOSS_T:g} 高 @ r{M6_R:g}")
print(f"  包络 X {_v[:,0].min():7.2f}..{_v[:,0].max():7.2f}  Y {_v[:,1].min():7.2f}..{_v[:,1].max():7.2f}  "
      f"Z {_v[:,2].min():5.2f}..{_v[:,2].max():5.2f}   r_max {_r.max():.2f} (≤ {R_OUT:g} ✓ 不超 Φ{2*R_OUT:g})")
print(f"  体积 {VOL/1000:.2f} cm³ ≈ {MASS:.1f} g PLA, 质心 r{math.hypot(_cen[0], _cen[1]):.1f} "
      f"⇒ **本件自带 {MASS*math.hypot(_cen[0], _cen[1]):.0f} g·mm 固有配重** (方向零件系 180°)")
print(f"  孔: 4×Φ{M3_D:g} @ (X{M3_XS[0]:g}/{M3_XS[1]:g}, Y±{M3_Y:g}) → 罩顶铜花螺母, M3×16 ×4")
print(f"      1×Φ{M6_D:g} @ (−{M6_R:g}, 0) + 底面对边 {M6_HEX_AF:g}×{M6_HEX_H:g} 六角窝 (卡 M6 六角头防转), "
      f"台肩 {M6_BOSS_T-M6_HEX_H:g} 厚")

print("\n配重容量 (力臂 r%.1f; 头朝下卡窝, 杆朝上叠垫圈, 叠高无上限):" % M6_R)
RHO = 7.85e-3
W18 = math.pi * (9 ** 2 - 3 ** 2) * 1.6 * RHO
for L, t in ((30, 8), (45, 22), (60, 36), (80, 56)):
    n = round(t / 1.6)
    m = (471 + 26.0 * L) * RHO + n * W18
    print(f"  M6×{L:<3g}六角头 + {n:2d} 片 Φ18×1.6 大垫圈 (叠高 {t:g}) = {m:5.1f} g "
          f"→ {m*M6_R:6.0f} g·mm  (含本件自重共 {m*M6_R + MASS*math.hypot(_cen[0], _cen[1]):.0f})")
print("  对照 v3.1 偏心屏不平衡量 = m_屏 × 6.7:  300g→2010 / 500g→3350 / 800g→5360 g·mm")
print("  ⚠ 顶上用尼龙锁紧螺母或螺纹胶防松; 叠高 >40mm 不建议 (弯矩与摆动变差, 改用更密的材料)")
print("打印: 底面贴床, 零支撑; 六角窝顶面 10.3 桥接 (螺栓承压台肩, 该层填充调高)")
