"""
balance_block_v4 —— V0.4 带屏动平衡移动配重块 (2026-11-09, 配 rotor_shroud_v4)。

沿用 V1.0 balance_block_v1_0 思路 (用户已验证): M6 大头 + M3 微调, 块本身可移位。
  · 扇形 r54..85 ±21° 厚 4.8, 平贴罩顶面 (装配 Z92.2), 外缘 = 罩 OD 170 不超包络。
  · 锁紧 2×M3 @ r67 ±7.5° → 罩顶相邻两个铜花螺母, **M3×10**; 顶面头沉 Φ7.5×2。
  · 4×M6 @ r78, ±5°/±15°: 底面 Φ13×2.8 头窝, M6 大扁头 (Φ12.5×2.5) 头朝下藏窝里,
    杆朝上叠螺母/垫圈。螺母 (对角 11.55) 外角 r83.8 < 85 ✓。
  · 5×M3 微调 @ r58, −16..+16 每 8°: 底面 Φ7×1.5 头窝, 头朝下、螺纹朝上锁螺母。
  · 可放位置 (零件系中心角) 见 balance_params_v4.BLK_CENTERS。
零件系: 块中心在 +X (0°), 原点 = 转轴, 底面 Z0 = 罩顶面。
输出: balance_block_v4.stl (打印姿态, 顶面贴床, 零支撑) / balance_block_v4_asm.stl (装配姿态)。
"""
import math, struct, sys
from pathlib import Path
import manifold3d as m3d
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import balance_params_v4 as BP  # noqa: E402

R_IN, R_OUT, T, HALF = BP.BLK_R_IN, BP.BLK_R_OUT, BP.BLK_T, BP.BLK_HALF
M3_D, M3_CB_D, M3_CB_DEEP = 3.2, 7.5, 2.0
M6_R, M6_D, M6_DEG = 78.0, 6.5, (-15.0, -5.0, 5.0, 15.0)
CB_D, CB_DEEP = 13.0, 2.8
TRIM_R, TRIM_D, TRIM_CB_D, TRIM_CB_DEEP = 58.0, 3.2, 7.0, 1.5
TRIM_DEG = (-16.0, -8.0, 0.0, 8.0, 16.0)
RHO = 1.24                                  # PLA g/cm³ (同罩子估重)

LOCK = [BP.pol(BP.LOCK_R, s * BP.LOCK_HALF) for s in (-1, 1)]
M6 = [BP.pol(M6_R, a) for a in M6_DEG]
TRIM = [BP.pol(TRIM_R, a) for a in TRIM_DEG]


def cyl(d, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, 64).translate((x, y, z0))


def build():
    a = np.radians(np.linspace(-HALF, HALF, 64))
    pts = [(R_OUT * math.cos(t), R_OUT * math.sin(t)) for t in a] + \
          [(R_IN * math.cos(t), R_IN * math.sin(t)) for t in a[::-1]]
    p = m3d.CrossSection([pts]).extrude(T)
    for x, y in LOCK:
        p -= cyl(M3_D, x, y, -1, T + 1); p -= cyl(M3_CB_D, x, y, T - M3_CB_DEEP, T + 1)
    for x, y in M6:
        p -= cyl(M6_D, x, y, -1, T + 1); p -= cyl(CB_D, x, y, -1, CB_DEEP)
    for x, y in TRIM:
        p -= cyl(TRIM_D, x, y, -1, T + 1); p -= cyl(TRIM_CB_D, x, y, -1, TRIM_CB_DEEP)
    return p


def write_stl(man, path, head):
    m = man.to_mesh(); v = np.asarray(m.vert_properties)[:, :3]; t = np.asarray(m.tri_verts)
    with open(path, "wb") as f:
        f.write(head.encode().ljust(80, b" ")[:80]); f.write(struct.pack("<I", len(t)))
        for tri in t:
            a, b, c = v[tri]; n = np.cross(b - a, c - a); L = np.linalg.norm(n)
            f.write(struct.pack("<12fH", *(n / L if L else n), *a, *b, *c, 0))
    return v


def wall(p, q, rp, rq):
    return math.dist(p, q) - rp - rq


if __name__ == "__main__":
    p = build()
    write_stl(p, HERE / "balance_block_v4_asm.stl", "POV3D balance_block_v4 asm")
    v = write_stl(p.rotate((180, 0, 0)).translate((0, 0, T)), HERE / "balance_block_v4.stl",
                  "POV3D balance_block_v4 print")
    m = p.volume() / 1000 * RHO
    mesh = p.to_mesh(); vp = np.asarray(mesh.vert_properties)[:, :3]; tri = vp[np.asarray(mesh.tri_verts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = np.einsum("ij,ij->i", a, np.cross(b, c)); cg = (d[:, None] * (a + b + c)).sum(0) / 24 / (d.sum() / 6)
    print(f"体积 {p.volume():.0f} mm³, 估重 {m:.1f} g (PLA), 质心 r{cg[0]:.1f}, 块自身 {m * cg[0]:.0f} g·mm; "
          f"genus {p.genus()}, 连通体 {len(p.decompose())}")
    # 壁厚校核 (同一面的窝 vs 窝, 贯通孔 vs 另一面的窝)
    chk = {
        "M6 窝-窝": min(wall(M6[i], M6[i + 1], CB_D / 2, CB_D / 2) for i in range(3)),
        "M6 窝-外缘": R_OUT - M6_R - CB_D / 2,
        "M6 窝-端面": min(M6_R * math.sin(math.radians(HALF - abs(x))) for x in M6_DEG) - CB_D / 2,
        "微调窝-窝": min(wall(TRIM[i], TRIM[i + 1], TRIM_CB_D / 2, TRIM_CB_D / 2) for i in range(4)),
        "微调窝-内缘": TRIM_R - TRIM_CB_D / 2 - R_IN,
        "微调窝-端面": TRIM_R * math.sin(math.radians(HALF - 16)) - TRIM_CB_D / 2,
        "微调窝-M6 窝(同底面)": min(wall(q, h, TRIM_CB_D / 2, CB_D / 2) for q in TRIM for h in M6),
        "锁孔-M6 窝": min(wall(q, h, M3_D / 2, CB_D / 2) for q in LOCK for h in M6),
        "锁孔-微调窝": min(wall(q, h, M3_D / 2, TRIM_CB_D / 2) for q in LOCK for h in TRIM),
        "锁头沉-微调孔": min(wall(q, h, M3_CB_D / 2, TRIM_D / 2) for q in LOCK for h in TRIM),
        "锁头沉-M6 孔": min(wall(q, h, M3_CB_D / 2, M6_D / 2) for q in LOCK for h in M6),
    }
    for k, val in chk.items():
        print(f"  {k:16s} {val:6.2f}")
        assert val > 0.4, k
    nut_r = M6_R + 11.55 / 2
    print(f"  M6 螺母外角 r{nut_r:.2f} (≤85 ✓)" if nut_r <= 85 else f"  ★ M6 螺母外角 r{nut_r:.2f} 超 85")
    print(f"  M6 窝底 {T - CB_DEEP:.1f}, 锁孔头下肉 {T - M3_CB_DEEP:.1f}; 打印姿态 Z {v[:,2].min():.2f}..{v[:,2].max():.2f}")
