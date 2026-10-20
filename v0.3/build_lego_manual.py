"""
POV3D v3 乐高式拼装说明书 (2026-07-13) — 多页 A4 横向 PDF。
结构: 封面(说明) → 打印件清单(缩略图×数量) → 外购件+紧固件清单 → 步骤 1..12
      (每页: 本步完成后的 3D 视图, 新增件橙色 / 已装件灰色 + 右栏本步零件框)。
渲染复用 assembly_v3.py 的零件加载/摆位逻辑, 每个零件打上步骤标签。
输出: v3/print/assembly/assembly_v3_manual.pdf  (说明书, 非加工图, 不跑 verifier)
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from fpdf import FPDF

ROOT = Path(__file__).parent            # pov3d/v3
MODELS = ROOT.parent / "models"
TMP = Path("/tmp/claude-1000/-mnt-d-claude-workspace-macha/39a6f268-78bd-4307-8456-9cfbb727cdf4/scratchpad/manual")
TMP.mkdir(parents=True, exist_ok=True)
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])

def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    return np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64)

def mesh_tris(man):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    return v[np.asarray(m.tri_verts)]

def rot_z(a, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x = a[..., 0].copy(); y = a[..., 1].copy()
    a[..., 0] = c * x - s * y
    a[..., 1] = s * x + c * y
    return a

ROT, ROTOR_ROT = 45.0, 0.0
MOTOR_Z0, MOTOR_H = 5.0, 26.7
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H
RING_Z0 = ROTOR_Z0
DISC_Z0 = RING_Z0 + 9.0
DISC_TOP = DISC_Z0 + 5.0
BOSS_TOP = DISC_TOP + 5.0
PI_TOP = BOSS_TOP + 1.6
NYLON_H = 8.5
PCB_Z0 = PI_TOP + NYLON_H
SCREEN_Z0 = DISC_TOP + 50.0
CAPTOP = 292.7
POST_H, POST_XY = 350.0, 125.0
PCB_ROT, PCB_OFF = 90.0, (-10.0, 0.0)
PCB_OFF_W = np.array([PCB_OFF[0], PCB_OFF[1], 0.0])   # ROTOR_ROT=0

parts = []   # (step, name, tris)
def add(step, name, t): parts.append((step, name, t))

# --- step 2: 洞洞板 + d100 ---
bb = m3d.Manifold.cube((300.0, 300.0, 12.0), False).translate((-150, -150, -12))
GRID = [k * 25.0 for k in range(-5, 6)]
for bx in GRID:
    for by in GRID:
        bb = bb - m3d.Manifold.cylinder(14, 3, 3, 12, False).translate((bx, by, -13))
add(2, "洞洞板", mesh_tris(bb))
bpc = rot_z(read_stl(MODELS / "baseplate_collar_d100/baseplate_collar_d100.stl"), ROT)
add(2, "d100 底座", bpc)
# --- step 3: 电机 ---
add(3, "电机", mesh_tris(m3d.Manifold.cylinder(MOTOR_H, 25, 25, 48, False).translate((0, 0, MOTOR_Z0))))
# --- step 4: 法兰两件 + 8 长螺丝 ---
fd = read_stl(MODELS / "flange_disc/flange_disc.stl") + np.array([0.0, 0.0, 18.0])
add(4, "flange_disc", rot_z(fd, ROT))
mf = read_stl(MODELS / "mounting_flange/mounting_flange.stl")
mf[..., 1] = -mf[..., 1]; mf[..., 2] = 28.0 - mf[..., 2]
add(4, "mounting_flange", rot_z(mf[:, ::-1, :].copy(), ROT))
scr8 = None
for k in range(8):
    a = math.radians(22.5 + 45 * k + ROT)
    x, y = 36.25 * math.cos(a), 36.25 * math.sin(a)
    s = m3d.Manifold.cylinder(28, 1.5, 1.5, 12, False).translate((x, y, 0)) \
      + m3d.Manifold.cylinder(2.4, 3.2, 3.2, 12, False).translate((x, y, 28))
    scr8 = s if scr8 is None else scr8 + s
add(4, "M3×30 ×8", mesh_tris(scr8))
# --- step 5: hub + rim ---
hub = read_stl(MODELS / "hub_disc/hub_disc.stl")
hub[..., 1] = -hub[..., 1]; hub[..., 2] = ROTOR_Z0 + 9.0 - hub[..., 2]
add(5, "hub_disc", rot_z(hub[:, ::-1, :].copy(), ROTOR_ROT))
ring = read_stl(MODELS / "rim_ring/rim_ring.stl") + np.array([0.0, 0.0, RING_Z0])
add(5, "rim_ring", rot_z(ring, ROTOR_ROT))
# --- step 6: 承载盘 ---
disc = read_stl(MODELS / "mlkpai_carrier_disc/mlkpai_carrier_disc.stl") + np.array([0.0, 0.0, DISC_Z0])
add(6, "承载盘", rot_z(disc, ROTOR_ROT))
# --- step 7: 电子堆叠 ---
pi = read_stl(MODELS / "pi2hub75e/pi2hub75e.stl") + np.array([0.0, 0.0, BOSS_TOP])
add(7, "pi2hub75e", rot_z(pi, ROTOR_ROT + PCB_ROT) + PCB_OFF_W)
stand = None
for (sx, sy) in [(-39.5, 25), (39.5, 25), (-39.5, -25), (39.5, -25)]:
    p = m3d.Manifold.cylinder(NYLON_H, 2.75, 2.75, 6, False).translate((sx, sy, PI_TOP))
    stand = p if stand is None else stand + p
add(7, "尼龙柱", rot_z(mesh_tris(stand), ROTOR_ROT + PCB_ROT) + PCB_OFF_W)
board = read_stl(MODELS / "mlkpai_board/mlkpai_board.stl") + np.array([0.0, 0.0, PCB_Z0])
add(7, "米联派", rot_z(board, ROTOR_ROT + PCB_ROT) + PCB_OFF_W)
# --- step 8: wifi ---
for nm, f in [("wifi_box", "usb_wifi/wifi_box.stl"), ("wifi 模块", "usb_wifi/usb_wifi_module.stl")]:
    w = read_stl(MODELS / f) + np.array([0.0, 0.0, DISC_TOP])
    add(8, nm, rot_z(w, ROTOR_ROT))
# --- step 9: 光电 ---
add(9, "光电支架", rot_z(read_stl(MODELS / "photo_sensor/sensor_bracket_v2.stl"), ROTOR_ROT))
sm = read_stl(MODELS / "photo_sensor/sensor_module.stl")
sm[..., 1] = -sm[..., 1]; sm[..., 2] = -sm[..., 2]
sm = sm[:, ::-1, :].copy() + np.array([-98.0, 20.0, DISC_TOP])
add(9, "光电模块", rot_z(sm, ROTOR_ROT))
add(9, "挡光片", read_stl(MODELS / "photo_sensor/index_vane_v2.stl"))
# --- step 10: 支架 ---
gA = read_stl(ROOT / "models/l_bracket_v3/gantry_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
add(10, "gantry A", rot_z(gA, ROTOR_ROT))
gB = read_stl(ROOT / "models/l_bracket_v3/gantry_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
add(10, "gantry B", rot_z(gB, ROTOR_ROT + 180.0))
sp = read_stl(ROOT / "models/l_bracket_v3/screen_plate_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
add(10, "screen_plate_v3", rot_z(sp, ROTOR_ROT))
# --- step 11: 双屏 ---
sc_raw = read_stl(MODELS / "screen_150x169/screen_150x169.stl")
sc_b = sc_raw + np.array([10.27, 0.0, SCREEN_Z0])
add(11, "后屏", rot_z(sc_b, ROTOR_ROT))
sc_f = rot_z(sc_raw.copy(), 180.0) + np.array([-10.27, 0.0, SCREEN_Z0])
add(11, "前屏", rot_z(sc_f, ROTOR_ROT))
# --- step 12: 顶帽 + 轴承塔 ---
cap = read_stl(ROOT / "models/top_cap_v3/top_cap_v3.stl")
cap[..., 1] = -cap[..., 1]; cap[..., 2] = CAPTOP - cap[..., 2]
add(12, "top_cap_v3", rot_z(cap[:, ::-1, :].copy(), ROTOR_ROT))
add(12, "M6×40", mesh_tris(m3d.Manifold.cylinder(40, 3, 3, 16, False).translate((0, 0, 286.4))))
add(12, "Φ8×50 螺柱", mesh_tris(m3d.Manifold.cylinder(50, 4, 4, 16, False).translate((0, 0, 316.4))))
posts = None
for px in (-POST_XY, POST_XY):
    for py in (-POST_XY, POST_XY):
        p = m3d.Manifold.cylinder(POST_H, 4, 4, 16, False).translate((px, py, 0))
        posts = p if posts is None else posts + p
add(12, "Φ8×350 柱 ×4", mesh_tris(posts))
fa = read_stl(MODELS / "top_bearing/frame_A_v2.stl")
fa = rot_z(fa, 135.0); fa[..., 2] += POST_H
add(12, "frame_A_v2", fa)
fb = read_stl(MODELS / "top_bearing/frame_B_v2.stl")
fb[..., 1] = -fb[..., 1]; fb[..., 2] = POST_H + 16.0 - fb[..., 2]
add(12, "frame_B_v2", rot_z(fb[:, ::-1, :].copy(), -45.0))
brg = None
for bz in (353.0, 361.0):
    b = (m3d.Manifold.cylinder(5, 8, 8, 32, False) -
         m3d.Manifold.cylinder(7, 4, 4, 32, False).translate((0, 0, -1))).translate((0, 0, bz))
    brg = b if brg is None else brg + b
add(12, "688 ×2", mesh_tris(brg))

# ===== 渲染 =====
GRAY, NEW, DARK = "#c9c9c9", "#e8622a", "#8f8f8f"
STEP_COLORS = {2: "#888888", 3: "#444444", 4: "#88aacc", 5: "#ccaa55", 6: "#9ccf9c",
               7: "#c0392b", 8: "#22aaaa", 9: "#7744aa", 10: "#cc8833", 11: "#3355cc",
               12: "#5577aa"}
def render(fname, upto, elev, azim, xyl, z0, z1, title="", cover=False):
    fig = plt.figure(figsize=(7.2, 6.2))
    ax = fig.add_subplot(111, projection="3d")
    for (st, nm, t) in parts:
        if st > upto: continue
        if cover:
            col = "#3a3a3a" if nm == "洞洞板" else STEP_COLORS[st]
            alpha = 0.95
        else:
            col = NEW if st == upto else (DARK if nm == "洞洞板" else GRAY)
            alpha = 1.0 if st == upto else 0.55
        ax.add_collection3d(Poly3DCollection(t, facecolor=col, edgecolor="none",
                                             alpha=alpha))
    ax.set_xlim(-xyl, xyl); ax.set_ylim(-xyl, xyl); ax.set_zlim(z0, z1)
    ax.set_box_aspect((1, 1, (z1 - z0) / (2 * xyl)))
    ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    if title: ax.set_title(title)
    fig.tight_layout(pad=0.1)
    fig.savefig(TMP / fname, dpi=105)
    plt.close(fig)
    return TMP / fname

VIEWS = {  # step: (elev, azim, xyl, z0, z1)
    2:  (28, -60, 165, -20, 80),
    3:  (25, -60, 100, -15, 70),
    4:  (25, -60, 100, -15, 70),
    5:  (25, -60, 105, -15, 80),
    6:  (25, -60, 105, -15, 85),
    7:  (25, -60, 105, -10, 110),
    8:  (25, -30, 105, -10, 110),
    9:  (25, -150, 115, -12, 90),
    10: (18, -60, 140, -15, 300),
    11: (18, -60, 140, -15, 300),
    12: (16, -60, 175, -15, 380),
}
IMGS = {}
for stp, (el, az, xy, z0, z1) in VIEWS.items():
    IMGS[stp] = render(f"step{stp:02d}.png", stp, el, az, xy, z0, z1)
    print(f"step {stp} rendered")

# step 1: d100 + 盘 底面朝上并排
fig = plt.figure(figsize=(7.2, 4.4))
ax = fig.add_subplot(111, projection="3d")
d1 = read_stl(MODELS / "baseplate_collar_d100/baseplate_collar_d100.stl")
d1[..., 1] = -d1[..., 1]; d1[..., 2] = 28.0 - d1[..., 2]        # 底面朝上
ax.add_collection3d(Poly3DCollection(d1 + np.array([-75.0, 0, 0]), facecolor=NEW, edgecolor="none"))
d2 = read_stl(MODELS / "mlkpai_carrier_disc/mlkpai_carrier_disc.stl")
d2[..., 1] = -d2[..., 1]; d2[..., 2] = 5.0 - d2[..., 2]
ax.add_collection3d(Poly3DCollection(d2 + np.array([95.0, 0, 0]), facecolor=NEW, edgecolor="none"))
ax.set_xlim(-190, 190); ax.set_ylim(-190, 190); ax.set_zlim(-10, 40)
ax.set_box_aspect((1, 1, 50 / 380)); ax.view_init(elev=38, azim=-90); ax.set_axis_off()
fig.tight_layout(pad=0.1); fig.savefig(TMP / "step01.png", dpi=105); plt.close(fig)
IMGS[1] = TMP / "step01.png"
print("step 1 rendered")

# 封面全机 iso
IMGS[0] = render("cover.png", 12, 20, -55, 175, -15, 380, cover=True)
print("cover rendered")

# 打印件缩略图
THUMBS = [
    ("baseplate_collar_d100", "×1", MODELS / "baseplate_collar_d100/baseplate_collar_d100.stl"),
    ("flange_disc",           "×1", MODELS / "flange_disc/flange_disc.stl"),
    ("mounting_flange",       "×1", MODELS / "mounting_flange/mounting_flange.stl"),
    ("hub_disc",              "×1", MODELS / "hub_disc/hub_disc.stl"),
    ("rim_ring",              "×1", MODELS / "rim_ring/rim_ring.stl"),
    ("mlkpai_carrier_disc",   "×1", MODELS / "mlkpai_carrier_disc/mlkpai_carrier_disc.stl"),
    ("gantry_v3",             "×2", ROOT / "models/l_bracket_v3/gantry_v3.stl"),
    ("screen_plate_v3",       "×1", ROOT / "models/l_bracket_v3/screen_plate_v3.stl"),
    ("top_cap_v3",            "×1", ROOT / "models/top_cap_v3/top_cap_v3.stl"),
    ("sensor_bracket_v2",     "×1", MODELS / "photo_sensor/sensor_bracket_v2.stl"),
    ("index_vane_v2",         "×1", MODELS / "photo_sensor/index_vane_v2.stl"),
    ("wifi_box",              "×1", MODELS / "usb_wifi/wifi_box.stl"),
    ("frame_A_v2",            "×1", MODELS / "top_bearing/frame_A_v2.stl"),
    ("frame_B_v2",            "×1", MODELS / "top_bearing/frame_B_v2.stl"),
]
for i, (nm, q, p) in enumerate(THUMBS):
    t = read_stl(p)
    v = t.reshape(-1, 3)
    c = (v.min(0) + v.max(0)) / 2
    r = float(np.abs(v - c).max()) * 1.1
    fig = plt.figure(figsize=(2.1, 2.1))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(t - c, facecolor="#b9cbe0", edgecolor="none"))
    ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_zlim(-r, r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=30, azim=-60); ax.set_axis_off()
    fig.tight_layout(pad=0); fig.savefig(TMP / f"thumb{i:02d}.png", dpi=100); plt.close(fig)
print("thumbs rendered")

# ===== PDF =====
PW, PH = 297.0, 210.0
pdf = FPDF(orientation="L", unit="mm", format="A4")
pdf.set_auto_page_break(False)
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")
def T(x, y, s, size=5.5, anchor="start"):
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)
def frame():
    pdf.set_line_width(0.3); pdf.rect(5, 5, PW - 10, PH - 10, style="D")
def footer(pg):
    T(PW - 10, PH - 9, f"POV3D v3 拼装说明书  ·  第 {pg} 页", size=4.5, anchor="end")

# --- 封面 ---
pdf.add_page(); frame()
T(PW/2, 28, "POV 3D 旋转显示器 v3", size=17, anchor="middle")
T(PW/2, 37, "双面屏配置 · 拼装说明书", size=9, anchor="middle")
pdf.image(str(IMGS[0]), x=95, y=42, w=112)
for i, line in enumerate([
    "整机: 300×300 洞洞板底座 + C4110 无刷电机 + Φ170 旋转盘 + 双面 LED 屏 (背靠背, LED 面 X=±10.27)",
    "     + 顶部定心轴承塔 (4 柱 + 双 688)。打印件 15 件 (PETG/ABS, 4+圈壁, ≥40% 填充)。",
    "工具: 内六角/十字批, 烙铁 (压铜花螺母), M3/M6 扳手, 扎带钳。",
    "先读: 每步橙色 = 本步新增零件; 右框 = 本步所需零件与螺丝; 感叹号 ! = 顺序陷阱, 装错要拆返。",
]):
    T(20, 172 + i * 6, line, size=5.5)
footer(1)

# --- 打印件清单 ---
pdf.add_page(); frame()
T(PW/2, 16, "组件清单 (一) — 3D 打印件  15 件", size=10, anchor="middle")
for i, (nm, q, p) in enumerate(THUMBS):
    col, row = i % 5, i // 5
    x0, y0 = 16 + col * 55, 24 + row * 56
    pdf.set_line_width(0.2); pdf.rect(x0, y0, 50, 50, style="D")
    pdf.image(str(TMP / f"thumb{i:02d}.png"), x=x0 + 4, y=y0 + 2, w=42)
    T(x0 + 25, y0 + 46, nm, size=4.6, anchor="middle")
    T(x0 + 46, y0 + 7, q, size=7, anchor="end")
T(16, PH - 14, "打印姿态见 print/README.md (gantry_v3 侧躺 / screen_plate_v3 平躺, 其余原姿态); 图纸在各零件文件夹。", size=4.8)
footer(2)

# --- 外购件 + 紧固件 ---
pdf.add_page(); frame()
T(PW/2, 16, "组件清单 (二) — 外购件与紧固件", size=10, anchor="middle")
BUY = [
 ("电子/结构", [
  "1× 洞洞板 300×300×12 (M6 网格 25, 中心起)", "1× C4110 无刷电机 Φ50×26.7",
  "2× LED 屏 150×169×7.27 (自带 M3 螺母)", "1× pi2hub75e 板", "1× 米联派 MLKPAI-FS03",
  "1× LM393 对射光电模块", "1× AX1800 USB WiFi 网卡", "4× Φ8×350 M6 螺纹柱",
  "2× 688 轴承 (8×16×5)", "1× Φ8×50 单头螺柱 (M6 内丝)", "电源: 未定 (另行补充)"]),
 ("螺丝/螺母", [
  "15× M3×4×4.5 铜花螺母 (热压)", "10× M3×8", "8× M3×6/8 (双屏, 按屏螺母实高)",
  "13× M3×12", "4× M3×14", "2× M3×16", "4× M3×18", "6× M3×18/20", "8× M3×20",
  "8× M3×30 + 8× 2mm 垫圈", "4× 尼龙柱 M3×8.5 + 尼龙螺丝", "7× 尼龙垫柱 M3×5",
  "约30× M3 螺母 + 垫圈", "8× M6×16", "2× M6×30", "1× M6×40 平头 (帽Φ12.5)",
  "2+× M6 螺母", "M6 平头配重螺丝+螺母 按需", "1× 扎带"]),
]
for ci, (hd, items) in enumerate(BUY):
    x0 = 20 + ci * 140
    T(x0, 28, hd, size=7)
    pdf.set_line_width(0.2); pdf.line(x0, 30.5, x0 + 125, 30.5)
    for i, it in enumerate(items):
        T(x0, 36 + i * 6.6, it, size=5.4)
T(20, PH - 14, "长度存疑的先别拧死: M6×16 (入洞洞板) 与 M3×6/8 (双屏) 按实物确认; 8× M3×30 是定子锁紧关键件, 缺了整个定子锁不住。", size=4.8)
footer(3)

# --- 步骤页 ---
STEPS = [
 (1, "压铜花螺母", ["15× M3×4×4.5 铜花螺母", "工具: 烙铁"],
  ["d100 底座翻过来, 底面 8 个 Φ4.2 沉孔各压 1 颗;",
   "承载盘翻过来, 底面 7 个 Φ4.2 沉孔各压 1 颗。",
   "! d100 顶面的 8 个沉孔留空不压 (长螺丝方案)。",
   "! 压到与面齐平; 底下只剩 1mm 肩, 不要压穿。"]),
 (2, "d100 底座上板", ["1× d100 底座", "4× M6×16"],
  ["底座转 45° 摆成菱形对脚, 四脚对准洞洞板",
   "(±50,0)/(0,±50) 网格孔, 4× M6×16 锁紧。",
   "开口扇区 (75°-105°) 朝 +Y 方向。"]),
 (3, "装电机", ["1× C4110 电机", "4× M3×8"],
  ["电机从上放入凸台孔 (ID55), 底座十字对齐",
   "底盘 4× M3 孔 (对角25), 从底面沉孔向上锁 M3×8。",
   "! 电机线从 75°-105° 开口引出 (内外同高 8mm)。"]),
 (4, "定子锁紧", ["1× flange_disc", "1× mounting_flange", "8× M3×30 + 2mm 垫圈"],
  ["flange_disc 平放到套环顶 (对齐 PCD Φ72.5 孔);",
   "mounting_flange 翻扣盖上 (壁朝下);",
   "8× M3×30 (头下加 2mm 垫圈) 从顶面一插到底,",
   "拧进 d100 底面的铜花螺母。夹持 28mm。",
   "! 不加垫圈螺尖会凸出底面 2mm 顶在洞洞板上。"]),
 (5, "转子毂", ["1× hub_disc", "1× rim_ring", "4× M3×8"],
  ["hub_disc 翻扣 (凸台朝下), 中心菱形 4 孔",
   "M3×8 锁到电机转子面;",
   "rim_ring 与 hub 同层嵌套 (Φ60 凸台入 ID60 孔,",
   "缺口互锁), 两者共占 Z31.7..40.7。"]),
 (6, "承载盘", ["1× 承载盘 (已压 7 螺母)", "6× M3×12 + 螺母"],
  ["盘放上 rim_ring, 16 环孔对齐;",
   "只锁 R35 圈的 6 个空余孔: M3×12 从盘顶沉孔",
   "向下穿盘+环, 环底垫片+螺母。",
   "! R77.5 的 8 孔全部留空 — 后面步骤 8/9/10 借用。"]),
 (7, "盘上电子堆叠", ["1× pi2hub75e", "1× 米联派", "7× M3×12", "7× 尼龙垫柱5", "4× 尼龙柱8.5"],
  ["7 个尼龙垫柱摆到盘面孔位上, pi2hub 放上",
   "(PCB_ROT=90°, 偏 -10), 7× M3×12 穿板+垫柱",
   "拧进盘底铜花螺母;",
   "4× 尼龙柱立上 pi2hub 图案孔 (±39.5,±25),",
   "米联派排针朝下插进 pi2hub 排座。"]),
 (8, "WiFi 网卡盒", ["1× wifi_box", "1× 网卡模块", "4× M3×14 + 垫片螺母", "1× 扎带"],
  ["盒开口朝上, 模块侧立放入 (天线反折, 插头朝+Y);",
   "USB 母头从盒外穿 +Y 端窗对插;",
   "整体倒扣到盘 +X 位, 4 耳对 R35/R77.5 @±22.5° 孔,",
   "M3×14 穿耳+盘+环, 环底垫片螺母; 扎带锁母头。"]),
 (9, "光电同步", ["1× 光电支架", "1× 光电模块", "1× 挡光片", "2× M3×16 / 2× M3×8+螺母 / 2× M6×16"],
  ["支架板放盘顶 -X 位, 2× M3×16 借 R77.5 环孔锁紧;",
   "模块扣支架板底 (槽口朝下), 2× M3×8+螺母;",
   "挡光片立在洞洞板 (-100,±25) 孔, 2× M6×16。",
   "慢转一圈: 挡光片应从模块槽中间穿过不碰。"]),
 (10, "屏幕支架", ["2× gantry_v3", "1× screen_plate_v3", "4× M3×20 + 螺母", "6× M3×18/20 + 垫片螺母"],
  ["gantry ×2 对角放 (件2 转 180°: 塔分别在 ±X 侧),",
   "每件 2× M3×20 穿脚+盘+环锁紧 (共4);",
   "立板插进两塔之间 (顶舌朝上),",
   "6× M3×18/20 贯通 板+塔, 塔背垫片+螺母。"]),
 (11, "双面屏", ["2× LED 屏", "8× M3×6/8 (按屏螺母)"],
  ["! 先把两块屏的排线插好 — 接口要伸进立板中央",
   "  共用窗, 装好后手伸不进去。",
   "两屏分别贴立板两面 (LED 朝外), 4 对孔对齐,",
   "每孔两侧各 1 颗短 M3 对头拧进各自屏的螺母,",
   "螺杆入板各 ≤2.5mm (不相碰)。"]),
 (12, "顶帽与轴承塔", ["1× top_cap_v3", "M6×40+Φ8×50+M6螺母", "4× M3×18 + 垫片螺母",
                      "4× Φ8×350 柱", "frame_A/B + 2×688", "M6×16×2 / M6×30×2 / M3×20×4"],
  ["! M6×40 必须先装: 头朝下入帽底头窝, Φ8×50 螺柱",
   "  拧上 10mm — 之后凸舌挡住就装不进了;",
   "帽双腿骑上立板顶舌, 4× M3×18 贯通锁死;",
   "4 柱竖起拧进洞洞板四角 (±125,±125);",
   "688×2 入 frame_A/B 座, frame 架柱顶",
   "(A: M6×16×2 / B: M6×30×2, 毂间 4× M3×20),",
   "螺柱穿双 688, 柱顶 M6 螺母锁紧;",
   "慢转试机 → 配重螺丝按需入帽 ±X 孔阵调平。"]),
]
for pg, (n, title, needs, lines) in enumerate(STEPS, start=4):
    pdf.add_page(); frame()
    pdf.set_line_width(0.4); pdf.circle(20, 18, 6.5, style="D")
    T(20, 20.5, str(n), size=10, anchor="middle")
    T(31, 20.5, title, size=10)
    img_w = 170 if n not in (1,) else 175
    pdf.image(str(IMGS[n]), x=12, y=28, w=img_w)
    bx = 195
    pdf.set_line_width(0.25); pdf.rect(bx, 26, 92, 8 + len(needs) * 6.4, style="D")
    T(bx + 3, 32, "本步零件", size=6)
    for i, it in enumerate(needs):
        T(bx + 3, 38.5 + i * 6.4, it, size=5.2)
    ty = 46 + len(needs) * 6.4
    for i, ln in enumerate(lines):
        T(bx, ty + i * 6.2, ln, size=5.2)
    footer(pg)

out = ROOT / "print/assembly/assembly_v3_manual.pdf"
pdf.output(str(out))
print(f"wrote {out}  ({3 + len(STEPS)} pages)")
