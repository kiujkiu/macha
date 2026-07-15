"""
POV3D 装配 v3  (assembly_v3)  ——  双面屏配置 (2026-07-10)

与 assembly_v2 的区别 (仅屏幕组件 + 顶帽, 其余全部沿用 v2):
  1. **双面屏, 背靠背对称**: screen_plate_v3 居中在轴平面 (X -3..+3),
     两块 150×169×7.27 屏分别贴板两面 —— 前屏 X -10.27..-3 (LED 面 -10.27
     朝 -X), 后屏 X +3..+10.27 (LED 面 +10.27 朝 +X)。LED 面对称 ±10.27。
     · 4 屏幕孔两侧共用: 每孔两颗 M3 对头拧进各自屏螺母 (侵入板内各 ≤2.5)。
     · 接口窗两屏共用 —— 两接口 (各占位凸 6) 相向伸进 6 深窗, 若实测凸出 >3
       需两侧加垫柱 (数字孪生里目前互相穿透, 属占位待实测)。
  2. **gantry_v3 门形支架**: 塔柱移到屏幕宽度之外 (Y 76..88, 屏边 75 留 1),
     板加宽 ±88。A/B = 同一件 ×2 对角放 (件2 绕 Z 转 180°: 塔分别在 -X/+X 侧)
     → 180° 旋转对称, 动平衡; 脚仍借盘 R77.5 环孔, 盘不用改。
  3. **top_cap_v3 对称一字帽**: 板顶加中央凸舌 (±40, 伸到屏顶 264.7 之上到
     280.7), 帽双腿 (X ±(3..7), Z 267..292.7) 夹舌, 4×M3×18 贯通锁死;
     板 X -65..+65 对称, 配重孔阵 ±X 两端各 19。轴五金同 v2
     (M6×40 平头先装后夹舌 + Φ8×50 螺柱 + 双 688); 柱/frame_A/B_v2 原样沿用。
  4. SCREEN_FLIP 取消 (双面对称后无意义)。

沿用 v2: 洞洞板 / baseplate_collar_d100 对脚 45° / 法兰 / 电机 / hub+rim 同层 /
mlkpai_carrier_disc / pi2hub+尼龙柱+米联派堆叠 / 光电同步 / usb_wifi 盒 /
顶轴承柱+frame_v2。坐标系 = baseplate 底面 Z=0, Z 向上。
输出 assembly_v3.stl + 预览 PNG。 仅供装配核对, 不可打印。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

ROOT = Path(__file__).parent            # pov3d/v3
MODELS = ROOT.parent / "models"         # v1/v2 共享零件库
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

# d100 底座转 45° → 4×M6 脚落到坐标轴网格孔; 转子快照角度 ROTOR_ROT=0
# (θ=180 的光电模块正好套住静止挡光片, 方便目检干涉)。同 v2。
ROT = 45.0
ROTOR_ROT = 0.0

parts = []

# ---- Z datum ----
MOTOR_D, MOTOR_H, MOTOR_Z0 = 50.0, 26.7, 5.0
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H            # 31.7

# 1) 洞洞板 300×300×12, 顶面 Z=0, M6 网格从中心起 (25mm, 中心有孔)
BB_T = 12.0
bb = m3d.Manifold.cube((300.0, 300.0, BB_T), False).translate((-150.0, -150.0, -BB_T))
GRID = [k * 25.0 for k in range(-5, 6)]
for bx in GRID:
    for by in GRID:
        h = m3d.Manifold.cylinder(BB_T + 2, 3.0, 3.0, 16, False).translate((bx, by, -BB_T - 1.0))
        bb = bb - h
parts.append(("breadboard center-grid", mesh_tris(bb)))

# 2) baseplate_collar_d100 居中转 45° (对脚菱形), 底面坐 Z=0
bpc = read_stl(MODELS / "baseplate_collar_d100/baseplate_collar_d100.stl")
bpc = rot_z(bpc, ROT)
parts.append(("baseplate_collar_d100", bpc))

# 3) flange_disc +18 直立 (随转 45°)
fd = read_stl(MODELS / "flange_disc/flange_disc.stl") + np.array([0.0, 0.0, 18.0])
fd = rot_z(fd, ROT)
parts.append(("flange_disc", fd))

# 3) mounting_flange 翻转 180°(绕 X) 扣顶 (壁 18..25, 底 25..28), 随转 45°
mf = read_stl(MODELS / "mounting_flange/mounting_flange.stl")
mf[..., 1] = -mf[..., 1]
mf[..., 2] = 28.0 - mf[..., 2]
mf = mf[:, ::-1, :].copy()
mf = rot_z(mf, ROT)
parts.append(("mounting_flange", mf))

# 3) 电机 C4110 Φ50×26.7, 立在底盘顶(5) 凸台孔内, 转子面 Z=31.7
motor = m3d.Manifold.cylinder(MOTOR_H, MOTOR_D/2, MOTOR_D/2, 64, False).translate((0, 0, MOTOR_Z0))
parts.append(("motor (placeholder)", mesh_tris(motor)))

# 4) 转子: hub_disc 翻转嵌进 rim_ring, 两者同层 31.7..40.7 (组合高 9)
hub = read_stl(MODELS / "hub_disc/hub_disc.stl")
hub[..., 1] = -hub[..., 1]
hub[..., 2] = ROTOR_Z0 + 9.0 - hub[..., 2]
hub = hub[:, ::-1, :].copy()
hub = rot_z(hub, ROTOR_ROT)
parts.append(("hub_disc (rotor, 下)", hub))

RING_Z0 = ROTOR_Z0                        # 31.7 : 与 hub 同层嵌套
ring = read_stl(MODELS / "rim_ring/rim_ring.stl") + np.array([0.0, 0.0, RING_Z0])
ring = rot_z(ring, ROTOR_ROT)
parts.append(("rim_ring (rotor, 上)", ring))

# 5) 承载盘 mlkpai_carrier_disc: 坐在 rim_ring 顶 (40.7), Φ170×5
DISC_Z0 = RING_Z0 + 9.0                    # 40.7
DISC_TOP = DISC_Z0 + 5.0                   # 45.7 盘面
disc = read_stl(MODELS / "mlkpai_carrier_disc/mlkpai_carrier_disc.stl") + np.array([0.0, 0.0, DISC_Z0])
disc = rot_z(disc, ROTOR_ROT)
parts.append(("mlkpai_carrier_disc", disc))

# 6) pi2hub75e (下板): 7× M3 尼龙垫柱 ~5 高, 落座面 = 盘面+5 = 51.7 (同 v2)
PCB_ROT = 90.0
PCB_OFF = (-10.0, 0.0)
_r = math.radians(ROTOR_ROT)
PCB_OFF_W = np.array([PCB_OFF[0]*math.cos(_r) - PCB_OFF[1]*math.sin(_r),
                      PCB_OFF[0]*math.sin(_r) + PCB_OFF[1]*math.cos(_r), 0.0])
BOSS_TOP = DISC_TOP + 5.0                   # 51.7
pi = read_stl(MODELS / "pi2hub75e/pi2hub75e.stl") + np.array([0.0, 0.0, BOSS_TOP])
pi = rot_z(pi, ROTOR_ROT + PCB_ROT) + PCB_OFF_W
parts.append(("pi2hub75e (下板)", pi))
PI_TOP = BOSS_TOP + 1.6                     # 53.3

# 7) 4× M3 尼龙螺柱: 立在 pi2hub 顶的 4 图案孔 (±39.5,±25), 撑起米联派
NYLON_H = 8.5
CHX, CHY = 39.5, 25.0
stand = None
for (sx, sy) in [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]:
    p = m3d.Manifold.cylinder(NYLON_H, 5.5/2, 5.5/2, 6, False).translate((sx, sy, PI_TOP))
    stand = p if stand is None else stand + p
parts.append(("nylon standoffs ×4", rot_z(mesh_tris(stand), ROTOR_ROT + PCB_ROT) + PCB_OFF_W))

# 8) 米联派核心板 (上): 坐在尼龙柱顶, 排针朝下插进 pi2hub 排座
PCB_Z0 = PI_TOP + NYLON_H                   # 61.8
board = read_stl(MODELS / "mlkpai_board/mlkpai_board.stl") + np.array([0.0, 0.0, PCB_Z0])
board = rot_z(board, ROTOR_ROT + PCB_ROT) + PCB_OFF_W
parts.append(("mlkpai_board (上)", board))
print(f"disc {DISC_Z0:.1f}..{DISC_TOP:.1f}; 垫柱顶 {BOSS_TOP:.1f}; pi2hub {BOSS_TOP:.1f}..{PI_TOP:.1f}; "
      f"尼龙柱 {PI_TOP:.1f}..{PCB_Z0:.1f}; 米联派底 {PCB_Z0:.1f}")

# 9) l_bracket_v3 屏幕支架: gantry_v3 ×2 对角放 (件A 脚+Y 塔-X侧; 件B = 绕 Z
#    转 180°, 脚-Y 塔+X侧 → 180° 旋转对称) + screen_plate_v3 (176×214×6 居中
#    X -3..+3, 顶部凸舌到 280.7)。脚借盘 R77.5 环孔 (45° 阵列, 转 180° 仍对孔)。
gA = read_stl(ROOT / "models/l_bracket_v3/gantry_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
gA = rot_z(gA, ROTOR_ROT)
parts.append(("gantry_v3 A (+Y, 塔-X)", gA))
gB = read_stl(ROOT / "models/l_bracket_v3/gantry_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
gB = rot_z(gB, ROTOR_ROT + 180.0)
parts.append(("gantry_v3 B (-Y, 塔+X)", gB))
sp = read_stl(ROOT / "models/l_bracket_v3/screen_plate_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
sp = rot_z(sp, ROTOR_ROT)
parts.append(("screen_plate_v3", sp))

# 10) 双屏 150×169×7.27 背靠背: 屏模块局部系 LED 面 X=0 朝 +X, 体 -7.27..0。
#     后屏: 原样 +10.27 → 体 +3..+10.27, LED +10.27 朝 +X;
#     前屏: 绕 Z 转 180° 再 -10.27 → 体 -10.27..-3, LED -10.27 朝 -X。
#     下边沿 = 盘顶+50 (同 v2)。
SCREEN_T = 7.27
PLATE_HT = 3.0
SCREEN_Z0 = DISC_TOP + 50.0                 # 95.7
sc_raw = read_stl(MODELS / "screen_150x169/screen_150x169.stl")
sc_b = sc_raw + np.array([PLATE_HT + SCREEN_T, 0.0, SCREEN_Z0])       # +3..+10.27
sc_b = rot_z(sc_b, ROTOR_ROT)
parts.append(("screen back (+X)", sc_b))
sc_f = rot_z(sc_raw.copy(), 180.0) + np.array([-(PLATE_HT + SCREEN_T), 0.0, SCREEN_Z0])
sc_f = rot_z(sc_f, ROTOR_ROT)               # -10.27..-3
parts.append(("screen front (-X)", sc_f))
MLK_TOP = PCB_Z0 + 1.6 + 1.2                # 64.6 米联派板顶+针尾
print(f"支架翼板底 {DISC_TOP+21.0:.1f} / 中央缺口顶(±60内) {DISC_TOP+50.0:.1f} (米联派顶 {MLK_TOP:.1f}); "
      f"双屏 {SCREEN_Z0:.1f}..{SCREEN_Z0+169:.1f} (LED 面 X=±{PLATE_HT+SCREEN_T:.2f}); "
      f"板顶舌 {DISC_TOP+213.5:.1f}..{DISC_TOP+235.0:.1f}")

# 11) 光电同步 (同 v2): sensor_bracket_v2 + sensor_module 随转子; index_vane_v2 静止
sb = read_stl(MODELS / "photo_sensor/sensor_bracket_v2.stl")
sb = rot_z(sb, ROTOR_ROT)
parts.append(("sensor_bracket_v2", sb))
sm = read_stl(MODELS / "photo_sensor/sensor_module.stl")
sm[..., 1] = -sm[..., 1]; sm[..., 2] = -sm[..., 2]      # 绕 X 转180 = 槽口朝下
sm = sm[:, ::-1, :].copy()
sm = sm + np.array([-98.0, 20.0, DISC_TOP])
sm = rot_z(sm, ROTOR_ROT)
parts.append(("sensor_module", sm))
iv = read_stl(MODELS / "photo_sensor/index_vane_v2.stl")   # 静止, 不转
parts.append(("index_vane_v2", iv))

# 12) USB WiFi 网卡 + 倒扣盒 (同 v2): 随转子
for nm, f in [("wifi_box",        "usb_wifi/wifi_box.stl"),
              ("usb_wifi_module", "usb_wifi/usb_wifi_module.stl")]:
    w = read_stl(MODELS / f) + np.array([0.0, 0.0, DISC_TOP])
    parts.append((nm, rot_z(w, ROTOR_ROT)))

# 13) 顶部定心轴承: 柱 + frame_A/B_v2 沿用 v2; 转子侧换 top_cap_v3 ——
#     对称一字帽 (板 X -65..+65, 双腿 X ±(3..7) Z 267..292.7 夹板顶凸舌,
#     4×M3×18 @ (±22, Z{271,276.5}); 配重孔阵 ±X 两端各 19)。
#     轴五金同 v2: M6×40 平头 (先装后夹舌) + Φ8×50 螺柱 + 双 688。
CAPTOP_V3 = 292.7
POST_H, POST_XY = 350.0, 125.0
for px in (-POST_XY, POST_XY):
    for py in (-POST_XY, POST_XY):
        post = m3d.Manifold.cylinder(POST_H, 4.0, 4.0, 24, False).translate((px, py, 0.0))
        parts.append((f"post @({px:+.0f},{py:+.0f})", mesh_tris(post)))
fa = read_stl(MODELS / "top_bearing/frame_A_v2.stl")
fa = rot_z(fa, 135.0)
fa[..., 2] += POST_H
parts.append(("frame_A_v2 (SW+NW)", fa))
fb = read_stl(MODELS / "top_bearing/frame_B_v2.stl")     # 打印翻转姿态
fb[..., 1] = -fb[..., 1]
fb[..., 2] = POST_H + 16.0 - fb[..., 2]
fb = fb[:, ::-1, :].copy()
fb = rot_z(fb, -45.0)
parts.append(("frame_B_v2 (NE+SE)", fb))
cap = read_stl(ROOT / "models/top_cap_v3/top_cap_v3.stl")  # 打印翻转姿态
cap[..., 1] = -cap[..., 1]
cap[..., 2] = CAPTOP_V3 - cap[..., 2]
cap = cap[:, ::-1, :].copy()
cap = rot_z(cap, ROTOR_ROT)
parts.append(("top_cap_v3 (rotor)", cap))
scr = m3d.Manifold.cylinder(40.0, 3.0, 3.0, 32, False).translate((0, 0, 286.4))
parts.append(("M6x40 screw (rotor)", mesh_tris(scr)))
sto = m3d.Manifold.cylinder(50.0, 4.0, 4.0, 48, False).translate((0, 0, 316.4))
parts.append(("standoff Φ8×50 (rotor)", mesh_tris(sto)))
for bz, tag in ((353.0, "688 lower (frame_A)"), (361.0, "688 upper (frame_B)")):
    brg = (m3d.Manifold.cylinder(5.0, 8.0, 8.0, 64, False)
           - m3d.Manifold.cylinder(7.0, 4.0, 4.0, 64, False).translate((0, 0, -1.0)))
    parts.append((tag, mesh_tris(brg.translate((0.0, 0.0, bz)))))
print(f"顶轴承: 柱顶 {POST_H:.0f}; 帽板 {CAPTOP_V3-9:.1f}..{CAPTOP_V3:.1f} "
      f"(帽腿底 267.0 / 屏顶 {SCREEN_Z0+169:.1f} / 舌顶 {DISC_TOP+235.0:.1f}); "
      f"轴承 353..358 / 361..366; 螺柱 316.4..366.4")

# 报告 d100 4 脚落点 (应为 (±50,0)/(0,±50))
_feet = [(-35.355, 35.355), (35.355, 35.355), (-35.355, -35.355), (35.355, -35.355)]
_rf = math.radians(ROT); _c, _s = math.cos(_rf), math.sin(_rf)
print("d100 4×M6 脚 (转%g° 后):" % ROT,
      ["(%.1f,%.1f)" % (_c*fx - _s*fy, _s*fx + _c*fy) for (fx, fy) in _feet])

# ===== merge + export =====
all_tris = np.concatenate([t for (_, t) in parts], axis=0)
out = ROOT / "assembly_v3.stl"
_header = b"POV3D assembly_v3"
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
          "mlkpai_board (上)": "#e03020",
          "gantry_v3 A (+Y, 塔-X)": "#aa6622", "gantry_v3 B (-Y, 塔+X)": "#aa6622",
          "screen_plate_v3": "#cc8833",
          "screen front (-X)": "#3355cc", "screen back (+X)": "#5533cc",
          "sensor_bracket_v2": "#7744aa", "sensor_module": "#222266",
          "index_vane_v2": "#aa2288", "wifi_box": "#22aaaa",
          "usb_wifi_module": "#111111",
          "frame_A_v2 (SW+NW)": "#5577aa", "frame_B_v2 (NE+SE)": "#5577aa",
          "top_cap_v3 (rotor)": "#cc8888", "M6x40 screw (rotor)": "#888888",
          "standoff Φ8×50 (rotor)": "#888888",
          "688 lower (frame_A)": "#999999", "688 upper (frame_B)": "#999999"}
for px in (-125, 125):
    for py in (-125, 125):
        COLORS[f"post @({px:+.0f},{py:+.0f})"] = "#666666"
fig = plt.figure(figsize=(14, 7))
for i, (elev, azim, title) in enumerate([(22, -60, "iso"), (89, -90, "top")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    for name, t in parts:
        ax.add_collection3d(Poly3DCollection(t, facecolor=COLORS.get(name, "#222"), edgecolor="none", alpha=0.95))
    ax.set_xlim(-150, 150); ax.set_ylim(-150, 150); ax.set_zlim(-12, 372)
    ax.set_box_aspect((1, 1, 1.28)); ax.view_init(elev=elev, azim=azim)
    ax.set_title(title); ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
fig.tight_layout()
png = ROOT / "assembly_v3_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
