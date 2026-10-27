"""
top_balance_bar_v4 — 顶部配重横梁 (2026-10-23 草案, 偏心装专用)。

为什么要它: V0.4 偏心装 (屏占 X 0..13.4) 的不平衡主方向在 ±X, 但压条
top_cap_v3_1_1 的 9 个 M6 配重孔排在 X=-11 沿 Y 排开 → X 向力臂只有 11,
上平面没法修 X 向。两平面动平衡的「上平面」就靠这根横梁补出 X 向 r54..78。

装配系 = 压条零件系 (装配里跟压条一起转 ROTOR_ROT + V3_SCR_ROT):
  · 平板 6 厚, 底面贴压条顶 267.95 → 顶 273.95。
  · 两臂沿 ±X, Y ±10, 端部按 R84 圆弧裁 (罩/盘 R85 包络内, 柱内缘 R91.2)。
  · 中段 hub: X -22..0 × Y ±21, 3×Φ6.5 对压条现有配重孔 (-11, 0/±14),
    M6×20 从压条底往上穿 (头在压条底 −X 悬空区, 偏心装时下面没屏), 螺母锁横梁顶。
    ⚠ 只适用于偏心装: 居中装时屏占 X ±6.7, 头会顶到屏顶。
  · 中心 Φ10 让开 Φ8 螺柱 (螺柱仍直接坐压条顶, 轴五金不动)。
  · 配重孔: 每臂 2×Φ6.5 @ r55/78。配重 = M6 大扁头 (头 Φ12.5×2.5, 用户 2026-10-23)
    + 螺母叠; 头 Φ12.5 ⇒ 节距须 ≥12.5, r55..78 区间只放得下 2 孔 (原 3 孔节距 12 会顶头)。
    头内缘 r48.75 避开挡光刀片扫带 r42.4..45.4 (刀尖 Z280); 头外缘 r84.25 < R85。
    横梁顶以上限高 14 (架臂底 Z290); 横梁下方 ±X 臂底下到罩顶全空, 往下叠不限。
    建议: 大扁头朝上 (头厚 2.5), 螺丝选长, 螺母从横梁底往下叠当配重。
    安装 3 颗同为 M6 大扁头 (头在压条底) + 螺母锁横梁顶, 长 ≥ 7+6+5 ⇒ M6×20。
打印: 底面贴床, 零支撑, 实心或 ≥5 墙。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

Z0, T = 267.95, 6.0                  # 底 = 压条顶 (CAPTOP_V3)
ARM_HW = 10.0                        # 臂半宽
R_TRIM = 84.0                        # 外缘裁切半径
HUB_X0, HUB_X1, HUB_HW = -22.0, 0.0, 21.0
MOUNT_D = 6.5
MOUNT_XY = ((-11.0, -14.0), (-11.0, 0.0), (-11.0, 14.0))   # = 压条 CW_X / CW_YS 子集
CENTER_D = 10.0                      # 让 Φ8 螺柱
CW_D = 6.5
CW_RS = (55.0, 78.0)
HEAD_D = 12.5                        # M6 大扁头 (用户 2026-10-23 图)
CW_XY = [(s * r, 0.0) for s in (-1.0, 1.0) for r in CW_RS]

# 压条参数对照 (防漂移): 安装孔必须落在压条的配重孔上
CAP_CW_X, CAP_CW_YS = -11.0, tuple(float(v) for v in range(-56, 57, 14))
assert all(abs(x - CAP_CW_X) < 1e-9 and y in CAP_CW_YS for x, y in MOUNT_XY), "安装孔不在压条孔上"
assert min(CW_RS) - HEAD_D / 2 > 45.41 + 2.0, "螺丝头压进刀片扫带"
assert max(CW_RS) + HEAD_D / 2 < 85.0, "螺丝头超出 R85"
assert min(b - a for a, b in zip(CW_RS, CW_RS[1:])) >= HEAD_D, "相邻配重孔螺丝头互顶"
assert min(abs(a[1] - b[1]) for a, b in zip(MOUNT_XY, MOUNT_XY[1:])) >= HEAD_D, "安装孔螺丝头互顶"


def cyl(d, x, y, z0, z1, seg=48):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg, False).translate((x, y, z0))


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def build():
    Z1 = Z0 + T
    part = box(-R_TRIM - 1, R_TRIM + 1, -ARM_HW, ARM_HW, Z0, Z1)
    part = part ^ cyl(2 * R_TRIM, 0, 0, Z0 - 1, Z1 + 1, 256)
    part += box(HUB_X0, HUB_X1, -HUB_HW, HUB_HW, Z0, Z1)
    part -= cyl(CENTER_D, 0, 0, Z0 - 1, Z1 + 1, 64)
    for (x, y) in MOUNT_XY:
        part -= cyl(MOUNT_D, x, y, Z0 - 1, Z1 + 1, 32)
    for (x, y) in CW_XY:
        part -= cyl(CW_D, x, y, Z0 - 1, Z1 + 1, 32)
    return part


def write_stl(man, out, header, flip_to_print=True):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].copy()
    if flip_to_print:
        v[:, 2] -= Z0                      # 打印姿态 = 装配姿态平移到 Z0=0 (底面贴床)
    tris = np.asarray(mesh.tri_verts)
    with out.open("wb") as f:
        f.write(header.ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            a, b, c = v[t[0]], v[t[1]], v[t[2]]
            n = np.cross(b - a, c - a); L = float(np.linalg.norm(n))
            if L > 0: n = n / L
            f.write(struct.pack("<3f", *n)); f.write(struct.pack("<3f", *a))
            f.write(struct.pack("<3f", *b)); f.write(struct.pack("<3f", *c))
            f.write(struct.pack("<H", 0))
    assert 84 + len(tris) * 50 == out.stat().st_size


if __name__ == "__main__":
    part = build()
    assert len(part.decompose()) == 1, "不连通"
    here = Path(__file__).parent
    write_stl(part, here / "top_balance_bar_v4.stl", b"POV3D top_balance_bar_v4 (print pose)")
    vol = part.volume()
    # 自身质心 (PLA 1.24): 用体素近似算 X 向偏心
    m = part.to_mesh(); vv = np.asarray(m.vert_properties)[:, :3]; tt = np.asarray(m.tri_verts)
    a, b, c = vv[tt[:, 0]], vv[tt[:, 1]], vv[tt[:, 2]]
    vol6 = np.einsum("ij,ij->i", a, np.cross(b, c))
    cen = ((a + b + c) / 4 * vol6[:, None]).sum(0) / vol6.sum()
    g = vol * 1.24 / 1000
    print(f"wrote top_balance_bar_v4.stl  vol {vol/1000:.2f} cm3 (~{g:.1f} g PLA)")
    print(f"  质心 X {cen[0]:+.2f} Y {cen[1]:+.2f} ⇒ 自带 {g*np.hypot(cen[0],cen[1]):.0f} g·mm 指向 -X")
    print(f"  配重孔 {[(round(x), round(y)) for x, y in CW_XY]}")
