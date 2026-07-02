"""
POV3D 装配 v2  (assembly_v2)  ——  新配置, 分步搭建 (2026-07-01)

与旧 assembly_stack.py 的区别:
  1. 洞洞板 300×300×12, M6(Φ6) 孔改为「从板中心起」的 25mm 网格
     (中心 0,0 有孔, 向外 0,±25..±125 → 11×11=121 孔)。
  2. 中间底座用 baseplate_collar_d100 (已合并底盘+套环) 居中, 且整体转 45°
     摆成菱形「对脚」安装: 角孔到中心 = 对角100/2 = 50, 转45° 后 4 脚落到
     坐标轴网格孔 (±50,0)/(0,±50), 正好锁在洞洞板上。
     —— 取代旧配置里分开的 baseplate + ring_collar。
  3. 上面: flange_disc + 翻转 mounting_flange + 电机 (同旧)。
  4. 转子端: hub_disc 与电机相连(在下 31.7..40.7), rim_ring 摞在 hub 顶上
     (40.7..49.7) —— 堆叠, 不再同层嵌套。

本次「先画到这里」= 只到 rim_ring 为止 (rim_top_disc/屏/电源/支架/顶轴承暂不画)。
坐标系 = baseplate 底面 Z=0, Z 向上。 输出 assembly_v2.stl + 预览 PNG。 仅供装配核对,不可打印。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

ROOT = Path(__file__).parent
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])

def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    tris = np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)
    return tris["verts"].astype(np.float64)

def mesh_tris(man):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    t = np.asarray(m.tri_verts)
    return v[t]

def rot_z(a, deg):
    """Rotate a tri array about Z (in place-ish); returns rotated copy view."""
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x = a[..., 0].copy(); y = a[..., 1].copy()
    a[..., 0] = c * x - s * y
    a[..., 1] = s * x + c * y
    return a

# d100 底座转 45° → 4×M6 脚 (角孔半径 50) 落到坐标轴网格孔 (±50,0)/(0,±50)。
# 上面的法兰/电机/转子整摞随同一角度旋转, 保持内部对齐 (凸台槽口/16孔/电机方阵)。
ROT = 45.0

parts = []

# ---- Z datum ----
MOTOR_D, MOTOR_H, MOTOR_Z0 = 50.0, 26.7, 5.0
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H            # 31.7

# 1) 洞洞板 300×300×12, 顶面 Z=0, M6 网格从中心起 (25mm, 中心有孔)
BB_T = 12.0
bb = m3d.Manifold.cube((300.0, 300.0, BB_T), False).translate((-150.0, -150.0, -BB_T))
GRID = [k * 25.0 for k in range(-5, 6)]  # 0, ±25 .. ±125  (|pos|<=125, 边距 25)
for bx in GRID:
    for by in GRID:
        h = m3d.Manifold.cylinder(BB_T + 2, 3.0, 3.0, 16, False).translate((bx, by, -BB_T - 1.0))
        bb = bb - h
parts.append(("breadboard center-grid", mesh_tris(bb)))

# 2) baseplate_collar_d100 居中转 45° (对脚菱形), 底面坐 Z=0
bpc = read_stl(ROOT / "models/baseplate_collar_d100/baseplate_collar_d100.stl")
bpc = rot_z(bpc, ROT)
parts.append(("baseplate_collar_d100", bpc))

# 3) flange_disc +18 直立 (随转 45°)
fd = read_stl(ROOT / "models/flange_disc/flange_disc.stl") + np.array([0.0, 0.0, 18.0])
fd = rot_z(fd, ROT)
parts.append(("flange_disc", fd))

# 3) mounting_flange 翻转 180°(绕 X) 扣顶 (壁 18..25, 底 25..28), 随转 45°
mf = read_stl(ROOT / "models/mounting_flange/mounting_flange.stl")
mf[..., 1] = -mf[..., 1]
mf[..., 2] = 28.0 - mf[..., 2]
mf = mf[:, ::-1, :].copy()
mf = rot_z(mf, ROT)
parts.append(("mounting_flange", mf))

# 3) 电机 C4110 Φ50×26.7, 立在底盘顶(5) 凸台孔内, 转子面 Z=31.7 (圆柱, 转不转都一样)
motor = m3d.Manifold.cylinder(MOTOR_H, MOTOR_D/2, MOTOR_D/2, 64, False).translate((0, 0, MOTOR_Z0))
parts.append(("motor (placeholder)", mesh_tris(motor)))

# 4) 转子: hub_disc 翻转与电机相连 (在下, 31.7..40.7),
#    rim_ring 摞在 hub 顶上 (40.7..49.7) —— 不再和 hub 同层嵌套 (随转 45°)
hub = read_stl(ROOT / "models/hub_disc/hub_disc.stl")
hub[..., 1] = -hub[..., 1]
hub[..., 2] = ROTOR_Z0 + 9.0 - hub[..., 2]
hub = hub[:, ::-1, :].copy()
hub = rot_z(hub, ROT)
parts.append(("hub_disc (rotor, 下)", hub))

RING_Z0 = ROTOR_Z0 + 9.0                  # 40.7 : hub 顶
ring = read_stl(ROOT / "models/rim_ring/rim_ring.stl") + np.array([0.0, 0.0, RING_Z0])
ring = rot_z(ring, ROT)
parts.append(("rim_ring (rotor, 上)", ring))

# 5) 新承载盘 mlkpai_carrier_disc: 坐在 rim_ring 顶 (49.7), Φ200×6 (随转 45°)
DISC_Z0 = RING_Z0 + 9.0                    # 49.7 : rim_ring 顶
DISC_TOP = DISC_Z0 + 6.0                   # 55.7 盘面
disc = read_stl(ROOT / "models/mlkpai_carrier_disc/mlkpai_carrier_disc.stl") + np.array([0.0, 0.0, DISC_Z0])
disc = rot_z(disc, ROT)
parts.append(("mlkpai_carrier_disc", disc))

# 6) pi2hub75e (下板): 坐在 6 个 Φ14 凸台顶 (盘面+2=57.7), 板底件在 2mm 凸台间隙避空 (随转 45°)
BOSS_TOP = DISC_TOP + 2.0                   # 57.7 : 凸台顶 = pi2hub 落座面
pi = read_stl(ROOT / "models/pi2hub75e/pi2hub75e.stl") + np.array([0.0, 0.0, BOSS_TOP])
pi = rot_z(pi, ROT)
parts.append(("pi2hub75e (下板)", pi))
PI_TOP = BOSS_TOP + 1.6                     # 59.3 : pi2hub 板顶

# 7) 4× M3 尼龙螺柱: 立在 pi2hub 顶的 4 图案孔 (±39.5,±25), 撑起米联派
NYLON_H = 8.5
CHX, CHY = 39.5, 25.0
stand = None
for (sx, sy) in [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]:
    p = m3d.Manifold.cylinder(NYLON_H, 5.5/2, 5.5/2, 6, False).translate((sx, sy, PI_TOP))
    stand = p if stand is None else stand + p
parts.append(("nylon standoffs ×4", rot_z(mesh_tris(stand), ROT)))

# 8) 米联派核心板 (上): 坐在尼龙柱顶, 排针朝下插进 pi2hub 排座 (随转 45°)
PCB_Z0 = PI_TOP + NYLON_H                   # 67.8 : 米联派 PCB 底面
board = read_stl(ROOT / "models/mlkpai_board/mlkpai_board.stl") + np.array([0.0, 0.0, PCB_Z0])
board = rot_z(board, ROT)
parts.append(("mlkpai_board (上)", board))
print(f"disc {DISC_Z0:.1f}..{DISC_TOP:.1f}; 凸台顶 {BOSS_TOP:.1f}; pi2hub {BOSS_TOP:.1f}..{PI_TOP:.1f} "
      f"(板底件到盘面 {BOSS_TOP-1.2-DISC_TOP:.1f}); 尼龙柱 {PI_TOP:.1f}..{PCB_Z0:.1f}; 米联派底 {PCB_Z0:.1f}")

# 报告 d100 4 脚落点 (应为 (±50,0)/(0,±50))
_feet = [(-35.355, 35.355), (35.355, 35.355), (-35.355, -35.355), (35.355, -35.355)]
_r = math.radians(ROT); _c, _s = math.cos(_r), math.sin(_r)
print("d100 4×M6 脚 (转%g° 后):" % ROT,
      ["(%.1f,%.1f)" % (_c*fx - _s*fy, _s*fx + _c*fy) for (fx, fy) in _feet])

# ===== merge + export =====
all_tris = np.concatenate([t for (_, t) in parts], axis=0)
out = ROOT / "assembly_v2.stl"
_header = b"POV3D assembly_v2"
with out.open("wb") as f:
    f.write(_header.ljust(80, b" "))
    f.write(struct.pack("<I", len(all_tris)))
    for t in all_tris:
        v0, v1, v2 = t
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(all_tris) * 50 == out.stat().st_size, "STL size mismatch"
print(f"wrote {out}  ({len(all_tris)} triangles)")
for name, t in parts:
    v = t.reshape(-1, 3)
    print(f"  {name:24s} X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  "
          f"Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}  Z {v[:,2].min():7.2f}..{v[:,2].max():7.2f}")

# ===== preview =====
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
COLORS = {"breadboard center-grid": "#333333", "baseplate_collar_d100": "#777777",
          "flange_disc": "#88aacc", "mounting_flange": "#cccc77",
          "motor (placeholder)": "#444444", "hub_disc (rotor, 下)": "#ccaa55",
          "rim_ring (rotor, 上)": "#9999bb", "mlkpai_carrier_disc": "#9ccf9c",
          "pi2hub75e (下板)": "#2a7d2a", "nylon standoffs ×4": "#dddddd",
          "mlkpai_board (上)": "#e03020"}
fig = plt.figure(figsize=(14, 7))
for i, (elev, azim, title) in enumerate([(22, -60, "iso"), (89, -90, "top")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    for name, t in parts:
        ax.add_collection3d(Poly3DCollection(t, facecolor=COLORS.get(name, "#222"), edgecolor="none", alpha=0.95))
    ax.set_xlim(-150, 150); ax.set_ylim(-150, 150); ax.set_zlim(-12, 90)
    ax.set_box_aspect((1, 1, 0.34)); ax.view_init(elev=elev, azim=azim)
    ax.set_title(title); ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
fig.tight_layout()
png = ROOT / "assembly_v2_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
