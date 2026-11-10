"""
counterweight_fan_v4 —— V0.4 带屏动平衡扇形配重块 (2026-11-09, 用户: "用之前的 shroud,
修改那个配重块就行, 还是装到之前的 shroud")。**取代 counterweight_arm**, 罩子仍用
rotor_shroud_v3_1 (不重印)。

为什么扇形: 旧罩顶只有 −X 侧 4 个 M3 铜花螺母 (−50/−72, ±14) 能锁件, 配重只能装在
−X 半边。屏偏心装 (+X 偏 6.7) ⇒ 主修正必在 −X; 实测残余方向偏一点也落在本件覆盖的
扇区里。把原来只有 −X 两孔的配重臂扩成 100°~260° 扇形, 一圈 M6 + 一圈 M3 微调,
相邻孔组合即可合成该扇区内任意方向。若实测要 +X 修正 ⇒ 说明 −X 配多了, 减配重即可。

坐标 = 罩零件系 XY (0° = +X, 逆时针), Z0 = 罩顶面 (装配 92.2), 同 counterweight_arm。
装配 = rot_z(part, ROTOR_ROT + V3_SCR_ROT) + Z 92.2。

几何:
  · 扇形 r58..85, 零件角 100°..260° (两端离屏 ≥3: 居中屏占 X−6.7), 厚 6
    ∪ 原配重臂矩形 X−85..−44 |Y|≤26 (伸到内排 M3)。外缘 R85 = 罩 OD, 不超 Φ170。
  · 锁紧 4×Φ3.4 @ (−50, ±14) / (−72, ±14), M3×16 进罩顶铜花螺母 (同原臂, 跨缝连两半)。
  · M6 ×14: r78 一圈 13 个 (180° + 两侧各 6 个, 每 10.6°; 169°/191° 附近让锁紧孔)
            + 原臂内孔 (−64, 0)。Φ6.5 通 + **底面 Φ13×2.8 头窝**: M6 大扁头头朝下, 杆朝上叠螺母。
  · M3 微调 ×18: r64, 104°..168° 与 192°..256° 每 8°。Φ3.2 通 + 底面 Φ7×1.5 头窝, 螺纹朝上锁螺母。
⚠ 本件底面整个贴在罩顶, 板下无空间: 一切五金叠在板上面, 杆不许往下伸出。
⚠ 两翼悬臂 ~80° 只靠中间 4 颗 M3 锁, 在罩顶上平躺, 离心力是面内径向 (截面 27 深) 刚度够。
打印: 顶面贴床 (底面头窝朝上), 零支撑。输出 *_asm.stl (装配姿态) / .stl (打印姿态)。
"""
import math, struct
from pathlib import Path
import manifold3d as m3d
import numpy as np

HERE = Path(__file__).parent
R_OUT, R_IN, T = 85.0, 58.0, 6.0
A0, A1 = 100.0, 260.0
ARM = (-85.0, -44.0, 26.0)                 # 原配重臂矩形 X0, X1, 半宽
LOCK = [(x, s * 14.0) for x in (-50.0, -72.0) for s in (1, -1)]
LOCK_D = 3.4
M6_R, M6_D, CB_D, CB_DEEP = 78.0, 6.5, 13.0, 2.8
_side = [106.0 + 10.6 * k for k in range(6)]          # 106 .. 159
M6_ANGS = sorted(_side + [180.0] + [360.0 - a for a in _side])
M6 = [(M6_R * math.cos(math.radians(a)), M6_R * math.sin(math.radians(a))) for a in M6_ANGS] + [(-64.0, 0.0)]
TRIM_R, TRIM_D, TRIM_CB_D, TRIM_CB_DEEP = 64.0, 3.2, 7.0, 1.5
TRIM_ANGS = [104.0 + 8.0 * k for k in range(9)] + [256.0 - 8.0 * k for k in range(9)]
TRIM = [(TRIM_R * math.cos(math.radians(a)), TRIM_R * math.sin(math.radians(a))) for a in TRIM_ANGS]
RHO = 1.24


def cyl(d, x, y, z0, z1, seg=64):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg).translate((x, y, z0))


def build():
    a = np.radians(np.linspace(A0, A1, 161))
    pts = [(R_OUT * math.cos(t), R_OUT * math.sin(t)) for t in a] + \
          [(R_IN * math.cos(t), R_IN * math.sin(t)) for t in a[::-1]]
    p = m3d.CrossSection([pts]).extrude(T)
    x0, x1, hw = ARM
    p += (m3d.Manifold.cube((x1 - x0, 2 * hw, T)).translate((x0, -hw, 0)) ^ cyl(2 * R_OUT, 0, 0, -1, T + 1, 256))
    for x, y in LOCK:
        p -= cyl(LOCK_D, x, y, -1, T + 1)
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


def gap(P, Q, rp, rq, same=False):
    return min(math.dist(p, q) - rp - rq for i, p in enumerate(P) for j, q in enumerate(Q) if not (same and j <= i))


if __name__ == "__main__":
    p = build()
    assert len(p.decompose()) == 1
    v = write_stl(p, HERE / "counterweight_fan_v4_asm.stl", "POV3D counterweight_fan_v4 asm")
    write_stl(p.rotate((180, 0, 0)).translate((0, 0, T)), HERE / "counterweight_fan_v4.stl", "POV3D counterweight_fan_v4 print")
    r = np.hypot(v[:, 0], v[:, 1]).max(); assert r <= R_OUT + 1e-6
    mesh = p.to_mesh(); vp = np.asarray(mesh.vert_properties)[:, :3]; tri = vp[np.asarray(mesh.tri_verts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = np.einsum("ij,ij->i", a, np.cross(b, c)); cg = (d[:, None] * (a + b + c)).sum(0) / 24 / (d.sum() / 6)
    m = p.volume() / 1000 * RHO
    print(f"体积 {p.volume()/1000:.1f} cm³ ≈ {m:.0f} g PLA, 质心 ({cg[0]:.1f},{cg[1]:.1f}) ⇒ 自带 {m*math.hypot(*cg[:2]):.0f} g·mm @180°; r_max {r:.2f}")
    print(f"M6 ×{len(M6)} @ r78 角 {', '.join(f'{x:.1f}' for x in M6_ANGS)} + (−64,0)")
    print(f"M3 微调 ×{len(TRIM)} @ r64 角 {TRIM_ANGS[0]:g}..{TRIM_ANGS[8]:g} / {TRIM_ANGS[-1]:g}..{TRIM_ANGS[9]:g} 每 8°")
    chk = {
        "M6 窝-窝 (底面)": gap(M6, M6, CB_D / 2, CB_D / 2, True),
        "M6 窝-外缘": R_OUT - M6_R - CB_D / 2,
        "M6 窝-扇端": M6_R * math.sin(math.radians(M6_ANGS[0] - A0)) - CB_D / 2,
        "M6 孔/窝-锁孔": gap(M6, LOCK, CB_D / 2, LOCK_D / 2),
        "微调窝-窝": gap(TRIM, TRIM, TRIM_CB_D / 2, TRIM_CB_D / 2, True),
        "微调窝-M6 窝": gap(TRIM, M6, TRIM_CB_D / 2, CB_D / 2),
        "微调窝-锁孔": gap(TRIM, LOCK, TRIM_CB_D / 2, LOCK_D / 2),
        "微调窝-内缘": TRIM_R - TRIM_CB_D / 2 - R_IN,
        "微调窝-扇端": TRIM_R * math.sin(math.radians(TRIM_ANGS[0] - A0)) - TRIM_CB_D / 2,
        "微调螺母Φ6.6-锁紧头Φ7 (顶面)": gap(TRIM, LOCK, 3.3, 3.5),
        "M6 螺母Φ12.6-锁紧头Φ7 (顶面)": gap(M6, LOCK, 6.3, 3.5),
    }
    for k, val in chk.items():
        print(f"  {k:28s} {val:6.2f}")
        assert val > 0.4, k
    print(f"  M6 窝底 {T-CB_DEEP:.1f}; 扇端 X @r{R_IN:g}: {R_IN*math.cos(math.radians(A0)):.2f} (居中屏面 −6.7)")
