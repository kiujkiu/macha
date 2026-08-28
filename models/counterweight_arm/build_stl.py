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
  · M6 孔  **2× Φ6.5 光孔 @ (−77, 0) / (−64, 0), 孔距 13.0** —— 三改 (2026-08-27 用户:
           "现在是上下两个, 改成左右, 上下居中, 间距还是 13, 左边的靠近左边缘 8mm")。
           两孔改排在 **X 轴上 (Y=0)**: 左孔离 R85 外缘 (Y=0 处即 X=−85) 8 ⇒ X=−77,
           右孔 X=−77+13=−64。两孔都在 −X 轴上 ⇒ 合矢量仍在 −X 轴上 (Y 分量恒 0)。
           ⚠ 力臂由原来的两孔同 r77.97 变成 r77 / r64 (平均 70.5, 配重效率 −9.6%)。
  · M6 沉孔 **底面 Φ12.5 × 深 3** (2026-08-27 用户: "在 M6 螺丝位置增加 M12.5 沉孔,
           深度 3mm")。开在 **底面** 而不是顶面 —— 因为板下无空间、螺杆不许下伸,
           唯一可行装法是 **M6 大扁头 (Φ12.5×3) 从下面插入沉进沉孔与底面齐平, 螺杆朝上**,
           垫圈/螺母全部叠在板上面。若要改成顶面沉孔, 把 M6_CB_FROM_BOTTOM 改 False。
           ⚠ 孔距 13 vs 沉孔 Φ12.5 ⇒ 两沉孔之间只剩 **0.5 肋**; 左沉孔外缘 r83.25,
           对 R85 外缘只剩 **1.75 边距**
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

打印: **翻面打印 —— 顶面贴床, 底面朝上** (2026-08-27 加了底面沉孔后改的): 这样 Φ12.5
      沉孔口朝上, 零支撑零桥接; 若按原来底面贴床, 沉孔顶会有 Φ12.5 的环形桥接。
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
M6_EDGE = 8.0                         # 左孔中心离左边缘 (Y=0 处外缘 = X −R_OUT)
M6_PITCH = 13.0                       # 两孔间距 (沿 X)
M6_XS = (-R_OUT + M6_EDGE, -R_OUT + M6_EDGE + M6_PITCH)   # = (−77, −64)
M6_Y = 0.0                            # 上下居中 (2026-08-27 三改: 上下 → 左右)
M6_D = 6.5                            # M6 过孔 (光孔)
M6_CB_ENABLE = True                   # 沉孔 (2026-08-27 用户新增)
M6_CB_D, M6_CB_H = 12.5, 3.0          # Φ12.5 × 深 3 = M6 大扁头沉平
M6_CB_FROM_BOTTOM = True              # True=开在底面 (头沉底, 螺杆朝上); False=顶面

SEG = 128


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def cyl(h, d, z0=0.0, seg=SEG):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, seg, False).translate((0.0, 0.0, z0))


# 底板: 矩形 ∩ R85 圆盘 (外缘随罩子外径, 保证不超 Φ170) —— 全件等厚, 无凸台
part = box(-R_OUT - 1, X_IN, -HW, HW, 0.0, BASE_T) ^ cyl(BASE_T, 2 * R_OUT)
# M6 ×2 光孔 (排在 X 轴上, Y=0, 孔距 13 ⇒ 合矢量在 −X 轴上)
for mx in M6_XS:
    part -= cyl(BASE_T + 2.0, M6_D, -1.0, 48).translate((mx, M6_Y, 0.0))
    if M6_CB_ENABLE:                       # 沉孔: 底面 = Z0..CB_H, 顶面 = (T−CB_H)..T
        _z0 = -1.0 if M6_CB_FROM_BOTTOM else BASE_T - M6_CB_H
        part -= cyl(M6_CB_H + 1.0, M6_CB_D, _z0, 48).translate((mx, M6_Y, 0.0))
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
_m6r = min(math.hypot(mx, M6_Y) for mx in M6_XS)      # 内侧孔 (力臂小的那个)
_m6r_out = max(math.hypot(mx, M6_Y) for mx in M6_XS)  # 外侧孔
_m6r_avg = 0.5 * (_m6r + _m6r_out)
print(f"  底板 {BASE_T:g} 厚 (无凸台) × |Y|≤{HW:g} × X {-R_OUT:g}..{X_IN:g} (外缘 R{R_OUT:g} 弧裁)")
print(f"  包络 X {_v[:,0].min():7.2f}..{_v[:,0].max():7.2f}  Y {_v[:,1].min():7.2f}..{_v[:,1].max():7.2f}  "
      f"Z {_v[:,2].min():5.2f}..{_v[:,2].max():5.2f}   r_max {_r.max():.2f} (≤ {R_OUT:g} ✓ 不超 Φ{2*R_OUT:g})")
print(f"  体积 {VOL/1000:.2f} cm³ ≈ {MASS:.1f} g PLA, 质心 r{math.hypot(_cen[0], _cen[1]):.1f} "
      f"⇒ **本件自带 {MASS*math.hypot(_cen[0], _cen[1]):.0f} g·mm 固有配重** (方向零件系 180°)")
print(f"  孔: 4×Φ{M3_D:g} @ (X{M3_XS[0]:g}/{M3_XS[1]:g}, Y±{M3_Y:g}) → 罩顶铜花螺母, M3×16 ×4")
print(f"      **2×Φ{M6_D:g} 光孔 @ X {M6_XS[0]:g}/{M6_XS[1]:g}, Y{M6_Y:g} (上下居中), 孔距 {M6_PITCH:g}** — "
      f"左孔离左边缘 {M6_EDGE:g}, 力臂 r{_m6r_out:.2f}/r{_m6r:.2f} (平均 {_m6r_avg:.2f}), "
      f"离最近 M3 孔 {min(math.hypot(mx-x3, M6_Y-M3_Y) for mx in M6_XS for x3 in M3_XS):.2f}")
if M6_CB_ENABLE:
    _cb_edge = R_OUT - (_m6r_out + M6_CB_D / 2)
    print(f"      沉孔 Φ{M6_CB_D:g} × 深 {M6_CB_H:g} 开在**{'底' if M6_CB_FROM_BOTTOM else '顶'}面** "
          f"(余厚 {BASE_T-M6_CB_H:g}) — 两沉孔间肋 {M6_PITCH-M6_CB_D:.2f}, 外沉孔对 R{R_OUT:g} 边距 {_cb_edge:.2f}")
    assert M6_CB_H < BASE_T, "沉孔比板还深"
    assert _cb_edge > 0, "沉孔切出 R85 外缘"
else:
    print("      无沉孔无凸台")

RHO = 7.85e-3
W12 = math.pi * (6 ** 2 - 3 ** 2) * 1.6 * RHO      # M6 平垫 Φ12×1.6
NUT = (0.866 * 10 ** 2 * 5 - math.pi * 9 * 5) * RHO  # M6 螺母
_own = MASS * math.hypot(_cen[0], _cen[1])
print(f"\n配重容量 (力臂 r{_m6r_out:.2f}+r{_m6r:.2f} ⇒ 等效 2×r{_m6r_avg:.2f}; ⚠ 孔距 {M6_PITCH:g} ⇒ 垫圈外径 ≤ {M6_PITCH:g}, "
      f"只能用 Φ12 平垫 {W12:.2f} g/片 或 M6 螺母 {NUT:.2f} g/个):")
for L, nw in ((30, 4), (45, 10), (60, 16), (80, 26)):
    m1 = (471 + 26.0 * L) * RHO + nw * W12          # 单孔: 螺栓 + nw 片 Φ12 平垫
    print(f"  每孔 M6×{L:<3g} + {nw:2d} 片 Φ12 平垫 = {m1:5.1f} g  ×2 孔 = {2*m1:5.1f} g "
          f"→ {2*m1*_m6r_avg:6.0f} g·mm  (含本件自重共 {2*m1*_m6r_avg + _own:.0f})")
print("  对照 v3.1 偏心屏不平衡量 = m_屏 × 6.7:  300g→2010 / 500g→3350 / 800g→5360 g·mm")
print("  ⚠ 本件底面全贴罩顶, **板下无空间** — 螺杆往下伸出量必须为 0, 五金全部放板上面")
print("  ⚠ 防松: 尼龙锁紧螺母或螺纹胶")
print("打印: **翻面 —— 顶面贴床, 底面(带沉孔)朝上** ⇒ 沉孔口朝上, 零支撑零桥接")
