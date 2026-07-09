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
  4. 转子端: hub_disc 翻转与电机相连, rim_ring 与 hub 同层嵌套 (同 v1):
     两者共占 31.7..40.7, 组合高 9 (Φ60 凸台入 ID60 孔, Φ165 底盘嵌墙内)。
     (2026-07-03 曾误画成堆叠 +9, 用户纠正后改回。)

已画到: 盘上电子堆叠 (pi2hub/尼龙柱/米联派) + l_bracket_v2 门形支架 + 新屏幕
150×169×7.27 (2026-07-02, 替代 2×HUB75) + usb_wifi 倒扣盒 + 顶部定心轴承 v2
(2026-07-09: 4×Φ8×350 M6螺纹柱 @(±125,±125) + frame_A/B_v2 + top_cap_v2 借屏顶
螺母孔, 五金沿用 v1: 688×2 / M6×40 / Φ8×50 螺柱; 电源仍未画)。
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
# 定子 (底座/法兰) 用 ROT=45; 转子自由旋转, 快照角度 ROTOR_ROT 单独设 —
# 2026-07-03 晚设为 0°, 让 θ=180 的光电模块正好套住静止挡光片, 方便目检干涉。
ROT = 45.0
ROTOR_ROT = 0.0

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

# 4) 转子: hub_disc 翻转嵌进 rim_ring, 两者同层 31.7..40.7 (组合高 9, 同 v1;
#    hub Φ60 凸台入 ring ID60 孔, 缺口互锁)
hub = read_stl(ROOT / "models/hub_disc/hub_disc.stl")
hub[..., 1] = -hub[..., 1]
hub[..., 2] = ROTOR_Z0 + 9.0 - hub[..., 2]
hub = hub[:, ::-1, :].copy()
hub = rot_z(hub, ROTOR_ROT)
parts.append(("hub_disc (rotor, 下)", hub))

RING_Z0 = ROTOR_Z0                        # 31.7 : 与 hub 同层嵌套
ring = read_stl(ROOT / "models/rim_ring/rim_ring.stl") + np.array([0.0, 0.0, RING_Z0])
ring = rot_z(ring, ROTOR_ROT)
parts.append(("rim_ring (rotor, 上)", ring))

# 5) 新承载盘 mlkpai_carrier_disc: 坐在 rim_ring 顶 (40.7), Φ170×5 (随转 45°)
DISC_Z0 = RING_Z0 + 9.0                    # 40.7 : rim_ring 顶
DISC_TOP = DISC_Z0 + 5.0                   # 45.7 盘面 (盘厚 6→5, 2026-07-06)
disc = read_stl(ROOT / "models/mlkpai_carrier_disc/mlkpai_carrier_disc.stl") + np.array([0.0, 0.0, DISC_Z0])
disc = rot_z(disc, ROTOR_ROT)
parts.append(("mlkpai_carrier_disc", disc))

# 6) pi2hub75e (下板, 100×75, 7 孔): 盘上凸台已取消 (2026-07-06), 板与盘之间
#    改用 7× M3 尼龙垫柱 ~5 高 (占位: 落座面仍 = 盘面+5=51.7; 盘上只剩
#    Φ3.2 通孔 + 盘底铜螺母沉孔)。 PCB 方向 PCB_ROT + 挪位 PCB_OFF 不变。
PCB_ROT = 90.0
PCB_OFF = (-10.0, 0.0)   # 盘系再 -X 挪 10 (2026-07-03 晚)
_r = math.radians(ROTOR_ROT)
PCB_OFF_W = np.array([PCB_OFF[0]*math.cos(_r) - PCB_OFF[1]*math.sin(_r),
                      PCB_OFF[0]*math.sin(_r) + PCB_OFF[1]*math.cos(_r), 0.0])
BOSS_TOP = DISC_TOP + 5.0                   # 51.7 : 垫柱顶 = pi2hub 落座面 (凸台已取消)
pi = read_stl(ROOT / "models/pi2hub75e/pi2hub75e.stl") + np.array([0.0, 0.0, BOSS_TOP])
pi = rot_z(pi, ROTOR_ROT + PCB_ROT) + PCB_OFF_W
parts.append(("pi2hub75e (下板)", pi))
PI_TOP = BOSS_TOP + 1.6                     # 53.3 : pi2hub 板顶

# 7) 4× M3 尼龙螺柱: 立在 pi2hub 顶的 4 图案孔 (±39.5,±25), 撑起米联派
NYLON_H = 8.5
CHX, CHY = 39.5, 25.0
stand = None
for (sx, sy) in [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]:
    p = m3d.Manifold.cylinder(NYLON_H, 5.5/2, 5.5/2, 6, False).translate((sx, sy, PI_TOP))
    stand = p if stand is None else stand + p
parts.append(("nylon standoffs ×4", rot_z(mesh_tris(stand), ROTOR_ROT + PCB_ROT) + PCB_OFF_W))

# 8) 米联派核心板 (上): 坐在尼龙柱顶, 排针朝下插进 pi2hub 排座 (随转 45°)
PCB_Z0 = PI_TOP + NYLON_H                   # 61.8 : 米联派 PCB 底面
board = read_stl(ROOT / "models/mlkpai_board/mlkpai_board.stl") + np.array([0.0, 0.0, PCB_Z0])
board = rot_z(board, ROTOR_ROT + PCB_ROT) + PCB_OFF_W
parts.append(("mlkpai_board (上)", board))
print(f"disc {DISC_Z0:.1f}..{DISC_TOP:.1f}; 垫柱顶 {BOSS_TOP:.1f}; pi2hub {BOSS_TOP:.1f}..{PI_TOP:.1f}; "
      f"尼龙柱 {PI_TOP:.1f}..{PCB_Z0:.1f}; 米联派底 {PCB_Z0:.1f}")

# 9) l_bracket_v2 屏幕支架三件: 门形底座 A/B (镜像左右手件, 双脚借盘 R77.5 环孔
#    @(±29.66,±71.6), 直背塔柱到 Z90 + 5厚满三角外侧筋墙) + 屏幕板 (156×182.5×6,
#    底边 Z21, 6×M3×18/20 贯通板+塔, 塔背垫片+螺母)。 随转 45°。
#    2026-07-09 深夜: 屏幕组件整体水平转 180° (SCREEN_FLIP) — plate 背面从
#    X=-13.27 转到 +13.27, LED 面仍在轴平面 X=0 但朝 -X; 帽腿因此落在平板
#    +X 末端, top_cap_v2 得以做成 L 型。盘 R77.5 环孔是 45° 阵列, 180° 转
#    后 4 只脚仍落在既有孔上, 盘不用改。
SCREEN_FLIP = 180.0
gb = np.concatenate([read_stl(ROOT / "models/l_bracket_v2/gantry_base_A.stl"),
                     read_stl(ROOT / "models/l_bracket_v2/gantry_base_B.stl")], axis=0) \
     + np.array([0.0, 0.0, DISC_TOP])
gb = rot_z(gb, ROTOR_ROT + SCREEN_FLIP)
parts.append(("gantry_base A+B", gb))
sp = read_stl(ROOT / "models/l_bracket_v2/screen_plate.stl") + np.array([0.0, 0.0, DISC_TOP])
sp = rot_z(sp, ROTOR_ROT + SCREEN_FLIP)
parts.append(("screen_plate", sp))

# 10) 新屏幕 150×169×7.27: 背贴立板, LED 面在轴平面 X=0 (SCREEN_FLIP 后朝 -X,
#     屏体 0..+7.27), 下边沿 = 盘顶+50 (随转 45°)
SCREEN_Z0 = DISC_TOP + 50.0                 # 95.7 (40→50, 2026-07-03 深夜: 中间12cm宽对盘面保5cm净空)
sc = read_stl(ROOT / "models/screen_150x169/screen_150x169.stl") + np.array([0.0, 0.0, SCREEN_Z0])
sc = rot_z(sc, ROTOR_ROT + SCREEN_FLIP)
parts.append(("screen_150x169", sc))
MLK_TOP = PCB_Z0 + 1.6 + 1.2                # 64.6 米联派板顶+针尾
print(f"支架翼板底 {DISC_TOP+21.0:.1f} / 中央缺口顶(±60内) {DISC_TOP+50.0:.1f} (米联派顶 {MLK_TOP:.1f}); "
      f"屏幕 {SCREEN_Z0:.1f}..{SCREEN_Z0+169:.1f} (盘面上 {SCREEN_Z0-DISC_TOP:.0f}); "
      f"支架顶 {DISC_TOP+213.5:.1f}")

# 11) 光电同步 (2026-07-03 晚: θ=180/-X, 与 PCB 同侧走线短): sensor_bracket_v2
#     盘顶板 (借盘 R77.5 环孔 (-71.6,±29.7), 悬出到 R113, 外角斜切) + sensor_module
#     (外购, 扣板底, 槽口朝下, 梁 (-98,0,37.7) 径向) — 两者随转子 (ROTOR_ROT);
#     index_vane_v2 静止 (脚 M6 @ 网格 (-100,±25) 切向对) — 不转。
#     ROTOR_ROT=0 时模块正好套住挡片 → 快照可直接目检干涉。
sb = read_stl(ROOT / "models/photo_sensor/sensor_bracket_v2.stl")
sb = rot_z(sb, ROTOR_ROT)
parts.append(("sensor_bracket_v2", sb))
sm = read_stl(ROOT / "models/photo_sensor/sensor_module.stl")
sm[..., 1] = -sm[..., 1]; sm[..., 2] = -sm[..., 2]      # 绕 X 转180 = 槽口朝下 (v1 同款)
sm = sm[:, ::-1, :].copy()                               # 翻面修正三角朝向
sm = sm + np.array([-98.0, 20.0, DISC_TOP])   # R_SLOT 112→98 (2026-07-07); 顶面平贴支架板底
sm = rot_z(sm, ROTOR_ROT)
parts.append(("sensor_module", sm))
iv = read_stl(ROOT / "models/photo_sensor/index_vane_v2.stl")   # 静止, 不转
parts.append(("index_vane_v2", iv))

# 12) USB WiFi 网卡 + 倒扣盒 (2026-07-09 第三版定稿): 模块侧立 (整块 14.5×40×70,
#     天线反折在内, 14.5×70 面坐盘, 40 竖直), 插头朝 +Y (同米联派 J6)。倒扣五面盒
#     壁 3, 借盘 4 环孔 (R35/R77.5 @ ±22.5°) 4× M3×14; +Y 端壁母头窗 + 扎带槽。随转子。
for nm, f in [("wifi_box",        "models/usb_wifi/wifi_box.stl"),
              ("usb_wifi_module", "models/usb_wifi/usb_wifi_module.stl")]:
    w = read_stl(ROOT / f) + np.array([0.0, 0.0, DISC_TOP])
    parts.append((nm, rot_z(w, ROTOR_ROT)))

# 13) 顶部定心轴承 v2 (2026-07-09, models/top_bearing/ *_v2): 结构同 v1 —
#     静止侧: 4×Φ8×350 M6螺纹柱 @(±125,±125) (R176.78, v2 网格最外角孔),
#     frame_A_v2 (hub 350..358, 688 下 @353..358) + frame_B_v2 (358..366,
#     688 上 @361..366) 架柱顶;
#     转子侧: top_cap_v2 —— L 型 (2026-07-09 深夜, 屏幕组件转 180° 后): 平板
#     283.7..292.7 (=屏顶 264.7+19) X -65..+17.27, 背板腿在 +X 末端
#     (+13.27..+17.27) 贴 plate 背面, 借屏幕上排螺母孔 (±49.975, Z253.2) 换
#     M3×16 锁死; 配重孔阵 19×M6 在 -X 悬伸 (轴和配重同侧, 故成 L) +
#     M6×40 平头 (头窝板底, 杆身 286.4..326.4) 拧进 Φ8×50 M6内丝螺柱
#     (316.4..366.4, 顶锁 M6 螺母) 穿双 688。柱顶 350 = 帽顶 292.7 + 57.3。
CAPTOP_V2 = 292.7
POST_H, POST_XY = 350.0, 125.0
for px in (-POST_XY, POST_XY):
    for py in (-POST_XY, POST_XY):
        post = m3d.Manifold.cylinder(POST_H, 4.0, 4.0, 24, False).translate((px, py, 0.0))
        parts.append((f"post @({px:+.0f},{py:+.0f})", mesh_tris(post)))
fa = read_stl(ROOT / "models/top_bearing/frame_A_v2.stl")
fa = rot_z(fa, 135.0)
fa[..., 2] += POST_H
parts.append(("frame_A_v2 (SW+NW)", fa))
fb = read_stl(ROOT / "models/top_bearing/frame_B_v2.stl")     # 打印翻转姿态
fb[..., 1] = -fb[..., 1]
fb[..., 2] = POST_H + 16.0 - fb[..., 2]
fb = fb[:, ::-1, :].copy()
fb = rot_z(fb, -45.0)
parts.append(("frame_B_v2 (NE+SE)", fb))
cap = read_stl(ROOT / "models/top_bearing/top_cap_v2.stl")    # 打印翻转姿态
cap[..., 1] = -cap[..., 1]
cap[..., 2] = CAPTOP_V2 - cap[..., 2]
cap = cap[:, ::-1, :].copy()
cap = rot_z(cap, ROTOR_ROT)
parts.append(("top_cap_v2 (rotor)", cap))
scr = m3d.Manifold.cylinder(40.0, 3.0, 3.0, 32, False).translate((0, 0, 286.4))
parts.append(("M6x40 screw (rotor)", mesh_tris(scr)))
sto = m3d.Manifold.cylinder(50.0, 4.0, 4.0, 48, False).translate((0, 0, 316.4))
parts.append(("standoff Φ8×50 (rotor)", mesh_tris(sto)))
for bz, tag in ((353.0, "688 lower (frame_A)"), (361.0, "688 upper (frame_B)")):
    brg = (m3d.Manifold.cylinder(5.0, 8.0, 8.0, 64, False)
           - m3d.Manifold.cylinder(7.0, 4.0, 4.0, 64, False).translate((0, 0, -1.0)))
    parts.append((tag, mesh_tris(brg.translate((0.0, 0.0, bz)))))
print(f"顶轴承 v2: 柱顶 {POST_H:.0f}; 帽板 {CAPTOP_V2-9:.1f}..{CAPTOP_V2:.1f} (屏顶 {SCREEN_Z0+169:.1f}+{CAPTOP_V2-9-SCREEN_Z0-169:.1f}); "
      f"轴承 353..358 / 361..366; 螺柱 316.4..366.4")

# 报告 d100 4 脚落点 (应为 (±50,0)/(0,±50))
_feet = [(-35.355, 35.355), (35.355, 35.355), (-35.355, -35.355), (35.355, -35.355)]
_rf = math.radians(ROT); _c, _s = math.cos(_rf), math.sin(_rf)
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
          "mlkpai_board (上)": "#e03020", "gantry_base A+B": "#aa6622",
          "screen_plate": "#cc8833", "screen_150x169": "#3355cc",
          "sensor_bracket_v2": "#7744aa", "sensor_module": "#222266",
          "index_vane_v2": "#aa2288", "wifi_box": "#22aaaa",
          "usb_wifi_module": "#111111",
          "frame_A_v2 (SW+NW)": "#5577aa", "frame_B_v2 (NE+SE)": "#5577aa",
          "top_cap_v2 (rotor)": "#cc8888", "M6x40 screw (rotor)": "#888888",
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
png = ROOT / "assembly_v2_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
