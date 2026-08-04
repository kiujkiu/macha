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
  · 底板  6 厚 (Z0..6), X −85..−44, |Y|≤26, 外缘被 R85 圆弧裁掉 ⇒ **不超 Φ170**
  · M6 孔  **2× Φ6.5 光孔 @ (−77.7, ±6.5), 孔距 13.0** —— 二改 (2026-08-04 用户:
           "窄了, 做宽一点, 能放下 2 个 M6 螺丝, 只保留 M6 通孔就可以了, 不需要凸台,
           M6 螺丝间距要有 13mm")。**凸台与六角窝已全部取消**, 就是两个光孔。
           两孔同半径 r77.97 ⇒ 合矢量仍在 −X 轴上; 对 R85 外缘余 7.03
  · M3 孔  4× Φ3.4 @ (−50, ±14) / (−72, ±14), 对罩顶的 4 个铜花螺母

配重怎么加:
  2 个 Φ6.5 光孔, 五金自定。⚠ **本件底面整个贴在罩顶面上, 板下面没有任何空间** ——
  所以 M6 的头/螺母/垫圈只能全部放在**板上面**; 螺杆往下伸出的长度必须为 0
  (不然会顶在罩顶板上把件撑起来)。
    · 孔距 13 ⇒ **垫圈外径 ≤ 13**: 只能用 M6 标准平垫 Φ12×1.6 (1.07 g/片 = 0.67 g/mm 叠高)
      或 M6 螺母 (对角 11.55, 2.29 g/个 = 0.46 g/mm)。Φ18 大垫圈两片会打架, 用不了。
    · 力臂 r77.97, 两孔 ⇒ 每孔每 10 g = 780 g·mm, 两孔合计每 10 g/孔 = 1560 g·mm
  ⚠ 必须防松: 尼龙锁紧螺母或螺纹胶。
  (若确实需要板下藏螺母/螺栓头, 把 M6_CB_ENABLE 打开 = 底面 Φ11×4 沉孔, 不加凸台。)

打印: **底面贴床, 零支撑** (全件等厚 6, 无桥接特征)。
BOM: M3×16 ×4 (进罩顶铜花螺母) + M6 螺栓 ×2 (长度按配重量选, 杆不许往下伸出) +
     Φ12 平垫/M6 螺母若干 + M6 尼龙锁紧螺母 ×2。
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
BASE_T = 6.0                          # 底板厚 (全件等厚, 无凸台)
X_IN = -44.0                          # 内端 (内排 M3 −50 往里留 6)
HW = 26.0                             # 半宽 (2026-08-04 用户"做宽一点": 19 → 26)
M6_X, M6_Y = -77.7, 6.5               # 2× M6 光孔; 孔距 = 2×M6_Y = 13.0
M6_D = 6.5                            # M6 过孔 (光孔, 无沉孔无凸台)
M6_CB_ENABLE = False                  # 备选: 底面 Φ11×4 沉孔 (给板下藏螺母/头用)
M6_CB_D, M6_CB_H = 11.0, 4.0

SEG = 128


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def cyl(h, d, z0=0.0, seg=SEG):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, seg, False).translate((0.0, 0.0, z0))


# 底板: 矩形 ∩ R85 圆盘 (外缘随罩子外径, 保证不超 Φ170) —— 全件等厚, 无凸台
part = box(-R_OUT - 1, X_IN, -HW, HW, 0.0, BASE_T) ^ cyl(BASE_T, 2 * R_OUT)
# M6 ×2 光孔 (同半径, 孔距 13 ⇒ 合矢量在 −X 轴上)
for sy in (1.0, -1.0):
    part -= cyl(BASE_T + 2.0, M6_D, -1.0, 48).translate((M6_X, sy * M6_Y, 0.0))
    if M6_CB_ENABLE:
        part -= cyl(M6_CB_H + 1.0, M6_CB_D, -1.0, 48).translate((M6_X, sy * M6_Y, 0.0))
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
_m6r = math.hypot(M6_X, M6_Y)
print(f"  底板 {BASE_T:g} 厚 (等厚, 无凸台) × |Y|≤{HW:g} × X {-R_OUT:g}..{X_IN:g} (外缘 R{R_OUT:g} 弧裁)")
print(f"  包络 X {_v[:,0].min():7.2f}..{_v[:,0].max():7.2f}  Y {_v[:,1].min():7.2f}..{_v[:,1].max():7.2f}  "
      f"Z {_v[:,2].min():5.2f}..{_v[:,2].max():5.2f}   r_max {_r.max():.2f} (≤ {R_OUT:g} ✓ 不超 Φ{2*R_OUT:g})")
print(f"  体积 {VOL/1000:.2f} cm³ ≈ {MASS:.1f} g PLA, 质心 r{math.hypot(_cen[0], _cen[1]):.1f} "
      f"⇒ **本件自带 {MASS*math.hypot(_cen[0], _cen[1]):.0f} g·mm 固有配重** (方向零件系 180°)")
print(f"  孔: 4×Φ{M3_D:g} @ (X{M3_XS[0]:g}/{M3_XS[1]:g}, Y±{M3_Y:g}) → 罩顶铜花螺母, M3×16 ×4")
print(f"      **2×Φ{M6_D:g} 光孔 @ ({M6_X:g}, ±{M6_Y:g}), 孔距 {2*M6_Y:g}** — 同半径 r{_m6r:.2f}, "
      f"对 R{R_OUT:g} 外缘余 {R_OUT-_m6r:.2f}, 离最近 M3 孔 {math.hypot(M6_X-M3_XS[1], M6_Y-M3_Y):.2f}"
      + (f"; 底面 Φ{M6_CB_D:g}×{M6_CB_H:g} 沉孔 (已开)" if M6_CB_ENABLE else "; 无沉孔无凸台"))

RHO = 7.85e-3
W12 = math.pi * (6 ** 2 - 3 ** 2) * 1.6 * RHO      # M6 平垫 Φ12×1.6
NUT = (0.866 * 10 ** 2 * 5 - math.pi * 9 * 5) * RHO  # M6 螺母
_own = MASS * math.hypot(_cen[0], _cen[1])
print(f"\n配重容量 (力臂 r{_m6r:.2f} ×2 孔; ⚠ 孔距 {2*M6_Y:g} ⇒ 垫圈外径 ≤ {2*M6_Y:g}, "
      f"只能用 Φ12 平垫 {W12:.2f} g/片 或 M6 螺母 {NUT:.2f} g/个):")
for L, nw in ((30, 4), (45, 10), (60, 16), (80, 26)):
    m1 = (471 + 26.0 * L) * RHO + nw * W12          # 单孔: 螺栓 + nw 片 Φ12 平垫
    print(f"  每孔 M6×{L:<3g} + {nw:2d} 片 Φ12 平垫 = {m1:5.1f} g  ×2 孔 = {2*m1:5.1f} g "
          f"→ {2*m1*_m6r:6.0f} g·mm  (含本件自重共 {2*m1*_m6r + _own:.0f})")
print("  对照 v3.1 偏心屏不平衡量 = m_屏 × 6.7:  300g→2010 / 500g→3350 / 800g→5360 g·mm")
print("  ⚠ 本件底面全贴罩顶, **板下无空间** — 螺杆往下伸出量必须为 0, 五金全部放板上面")
print("  ⚠ 防松: 尼龙锁紧螺母或螺纹胶")
print("打印: 底面贴床, 零支撑 (全件等厚, 无桥接)")
