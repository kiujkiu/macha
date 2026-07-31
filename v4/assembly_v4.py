"""
POV3D 装配 v4  (assembly_v4)  ——  200×200 网格底板配置 (2026-07-29)

v4 = v3 换底板。用户把洞洞板换成 200×200×13 网格板 (卖家规格: M6 螺纹孔
距边 12.5 / 节距 25; 4 个安装孔 Φ6.5 通 + Φ11×6 沉, 距边 25)。

**关键: 200 板的 4 个安装孔正好落在 (±75,±75) = 现有 4 根柱的位置**, 所以
POST_R 106.07 不变 → 顶轴承架 / 转子 / 罩子 / 屏幕支撑全部沿用 v3 原件。

唯一几何改动 = baseplate_collar: 新板是偶数孔网格 (±12.5/±37.5/±62.5/±87.5),
既无中心孔也无 ±50 轴向孔, 原 d100 的「对角100 + 装配转45°→脚落(±50,0)/(0,±50)」
落空 → 改走对角网格位 (±37.5,±37.5): 方形节距 75, 对角 106.07, **装配 ROT 45°→0°**。
新件 `v4/models/baseplate_collar_v4/`。

2026-07-29 追加 (用户"补成整圈"): 定子侧两处走线开口全部补实 —
  · baseplate_collar_v4: 凸台+套环 75..105° 走线缺口取消 (NOTCH_ENABLE=False)
  · flange_disc_v4 (新件): 0..5° 走线扇形槽 + 外圈凸台 40..45° 缺口都取消
    (SLOT_ENABLE / OUTER_CUTOUT_ENABLE = False); 外圈孔从 7 恢复为 8
  转子两件 (hub_disc / rim_ring) 早在 2026-07-21 就已补成整圈, 无需改动。
  ⚠⚠ 底座那个缺口原是**电机线唯一的出口** (C4110 坐凸台腔 ID55, 底盘 5 实心,
     上方是转子) —— 补实后必须另想走线方案, 或把 NOTCH_ENABLE 设回 True。

⚠ 底座质量 300×300×12 → 200×200×13 (钢约 8.5kg → 4.1kg)。底座质量是吸收转子
不平衡的主要手段, 对已知涡动问题 (f₁≈20–27 Hz) 是负面的; 建议用板上的 M6 螺纹孔
从下方把板锁到桌面/机架 (4 个 Φ6.5 安装孔已被柱占用)。
⚠ 安装孔的 Φ11×6 沉孔若在顶面, 柱子会陷进去 6mm → 柱顶 284, 光电叉顶 285.65 会
顶到架臂底 ✗。两种解法: (a) 把板翻面用 (M6 螺纹孔通攻, 两面都能用; 沉孔朝下正好
藏螺母) — 推荐; (b) 柱长 290→296。本装配按 (a) 建模, 柱底坐板顶面 Z=0。

--- 以下沿用 v3 ---
POV3D 装配 v3  (assembly_v3)  ——  双面屏配置 (2026-07-10)

2026-07-22 大改: 同步 v2.1 的转子重构 + 换 13.4 厚新屏 (边缘孔固定):
  · hub_disc 正放 + rim_ring 翻转当承载面 (42.2), mlkpai_carrier_disc 取消
  · pi2hub 组 +135°; wifi_shell 放平倒扣定稿位; 光电暂删 (等大改)
  · 柱 ±100 + frame_A/B_v2_1 (v2.1 短臂版)
  · 新屏 150×168.75×13.4 (LED 面=外侧, 边缘孔固定: 上下边各 3×M3 @64,
    距 LED 面 6.6, 同 screen_solder_jig 定位孔) —— LED 面 ±16.4
  · 屏幕组 (板/龙门/屏/顶帽) 整体转 V3_SCR_ROT=-45°: 4 脚落 22.5/67.5/
    202.5/247.5 环孔 (同 v2.1 用孔), 避开 wifi 壳 (不转则塔 A 扎进壳)
  ⚠ screen_plate_v3 / gantry_v3 / top_cap_v3 为旧 7.27 屏设计的占位件,
    待按边缘孔固定方案重做 (cap 腿孔与舌孔现差 3.5)。

与 assembly_v2 的区别 (原始 v3 设计, 仅屏幕组件 + 顶帽):
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
输出 assembly_v4.stl + 预览 PNG。 仅供装配核对, 不可打印。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

ROOT = Path(__file__).parent            # pov3d/v4
MODELS = ROOT.parent / "models"         # v1/v2 共享零件库
V3 = ROOT.parent / "v3"                 # v4 沿用的 v3 专属件 (转子/屏/顶部全套)
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

# v4: 底座不再转 45° —— 新板无 ±50 轴向孔, 4×M6 脚直接落对角网格位
# (±37.5,±37.5)。转子快照角度 ROTOR_ROT=0 (同 v3)。
ROT = 0.0
ROTOR_ROT = 0.0

parts = []

# ---- Z datum ----
MOTOR_D, MOTOR_H, MOTOR_Z0 = 50.0, 26.7, 5.0
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H            # 31.7

# 1) 网格底板 200×200×13, 顶面 Z=0 (按「翻面用」建模: 沉孔朝下, 顶面平)
#    M6 螺纹孔: 距边 12.5, 节距 25 → ±12.5/±37.5/±62.5/±87.5 (8×8 = 64 个)
#    4 安装孔: 距边 25 → (±75,±75), Φ6.5 通 + Φ11×6 沉 (朝下) —— **柱位**
BB_SIDE, BB_T = 200.0, 13.0
BB_GRID = [s0 * v for v in (12.5, 37.5, 62.5, 87.5) for s0 in (-1, 1)]
BB_MOUNT = 75.0
bb = m3d.Manifold.cube((BB_SIDE, BB_SIDE, BB_T), False).translate((-BB_SIDE/2, -BB_SIDE/2, -BB_T))
for bx in BB_GRID:
    for by in BB_GRID:
        h = m3d.Manifold.cylinder(BB_T + 2, 3.0, 3.0, 16, False).translate((bx, by, -BB_T - 1.0))
        bb = bb - h
for mx in (-BB_MOUNT, BB_MOUNT):
    for my in (-BB_MOUNT, BB_MOUNT):
        bb -= m3d.Manifold.cylinder(BB_T + 2, 3.25, 3.25, 24, False).translate((mx, my, -BB_T - 1.0))
        bb -= m3d.Manifold.cylinder(6.0 + 1.0, 5.5, 5.5, 32, False).translate((mx, my, -BB_T - 1.0))
parts.append(("grid plate 200x200x13", mesh_tris(bb)))

# 2) baseplate_collar_d100 居中转 45° (对脚菱形), 底面坐 Z=0
bpc = read_stl(ROOT / "models/baseplate_collar_v4/baseplate_collar_v4.stl")
bpc = rot_z(bpc, ROT)
parts.append(("baseplate_collar_v4", bpc))

# 3) flange_disc +18 直立 (随转 45°)
fd = read_stl(ROOT / "models/flange_disc_v4/flange_disc_v4.stl") + np.array([0.0, 0.0, 18.0])
fd = rot_z(fd, ROT)
parts.append(("flange_disc_v4", fd))

# 3) mounting_flange 翻转 180°(绕 X) 扣顶 (壁 18..25, 底 25..28), 随转 45°
mf = read_stl(ROOT / "models/mounting_flange_v4/mounting_flange_v4.stl")
mf[..., 1] = -mf[..., 1]
mf[..., 2] = 28.0 - mf[..., 2]
mf = mf[:, ::-1, :].copy()
mf = rot_z(mf, ROT)
parts.append(("mounting_flange_v4", mf))

# 3) 电机 C4110 Φ50×26.7, 立在底盘顶(5) 凸台孔内, 转子面 Z=31.7
motor = m3d.Manifold.cylinder(MOTOR_H, MOTOR_D/2, MOTOR_D/2, 64, False).translate((0, 0, MOTOR_Z0))
parts.append(("motor (placeholder)", mesh_tris(motor)))

# 4) 转子 (2026-07-21 重构, 同 v2.1): hub_disc 正放贴电机 (31.7..40.7, 塔 Φ50/
#    下凸台 Φ70), rim_ring 翻转扣上 (托盘面朝上当承载面, 顶 42.2; 内凸台环
#    OD80/ID70 落 hub 底板顶兼径向定心)。电机螺丝从 ring ID50 孔下去装。
hub = read_stl(MODELS / "hub_disc/hub_disc.stl") + np.array([0.0, 0.0, ROTOR_Z0])
hub = rot_z(hub, ROTOR_ROT)
parts.append(("hub_disc (rotor, 下)", hub))

RING_TOP = ROTOR_Z0 + 10.5                # 42.2 : 托盘顶 = 转子承载面
ring = read_stl(MODELS / "rim_ring/rim_ring.stl")
ring[..., 1] = -ring[..., 1]
ring[..., 2] = RING_TOP - ring[..., 2]
ring = rot_z(ring, ROTOR_ROT)
parts.append(("rim_ring (rotor, 上/承载盘)", ring))

# 5) mlkpai_carrier_disc 已取消 (2026-07-20) — 功能并入 rim_ring
DISC_TOP = RING_TOP                        # 42.2 : 承载面

# 6) pi2hub75e (下板): 7× M3 尼龙垫柱 ~5 高, 落座面 = 承载面+5 = 47.2 (同 v2.1)
PCB_ROT = 90.0
PCB_OFF = (-10.0, 0.0)
# 2026-07-21: 7 孔整组绕圆心逆时针 135° (俯视), 折进 PCB_ROT/PCB_OFF (同 v2.1)
PI_ROT_EXTRA = 135.0
_e = math.radians(PI_ROT_EXTRA)
PCB_OFF = (PCB_OFF[0]*math.cos(_e) - PCB_OFF[1]*math.sin(_e),
           PCB_OFF[0]*math.sin(_e) + PCB_OFF[1]*math.cos(_e))
PCB_ROT = PCB_ROT + PI_ROT_EXTRA
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
print(f"承载面(rim_ring 托盘顶) {DISC_TOP:.1f}; 垫柱顶 {BOSS_TOP:.1f}; pi2hub {BOSS_TOP:.1f}..{PI_TOP:.1f}; "
      f"尼龙柱 {PI_TOP:.1f}..{PCB_Z0:.1f}; 米联派底 {PCB_Z0:.1f}")

# 9) bottom_portal_v3 底部门形梁 (2026-07-22, 取代 gantry_v3×2 + screen_plate_v3;
#    中央板取消): 2 脚 (4 孔借盘环孔) + 2 腿 + 横梁 (顶 Z50 = 屏底, 6×M3×16 从
#    下往上拧进双屏底边孔)。整组 V3_SCR_ROT=-45°: 4 脚落 22.5/67.5/202.5/247.5
#    环孔 (同 v2.1 用孔, 避开 H1-H4 头沉), 腿避开 wifi 壳 (脚内缘与壳 NE 边平行
#    隙 ~2.2)。
# 2026-07-22 深夜终版 (用户分步定稿): 底部 = portal_tee_v3 ×2 (同件转 180°):
# T 型 (底条 67×10×5 装转子两螺丝 [Φ7 工艺井过筋], 竖梃 5×10 到 Z50) +
# 两端→梃顶大三角筋 (厚5) + 顶托内伸盖屏底 ±64 孔 (M3×12 经 Φ6.5 头窝井
# 向上锁屏, 托下 45° 小筋); 屏每侧只锁 1 颗, 中央孔空置, 模组自身为梁。
V3_SCR_ROT = -45.0
te = read_stl(V3 / "models/bottom_portal_v3/portal_tee_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
parts.append(("portal_tee A", rot_z(te.copy(), ROTOR_ROT + V3_SCR_ROT)))
parts.append(("portal_tee B", rot_z(te.copy(), ROTOR_ROT + V3_SCR_ROT + 180.0)))

# 10) 双面屏模组 (2026-07-22 深夜澄清: "两个屏幕一起" = 一体模组 13.4×150×
#     168.75, LED 面 ±6.7 两外侧; 底/顶面各 3×M3 居中单排 @64)。孪生已居中,
#     直接坐梁顶 (Z50 = 承载面+50), 随 V3_SCR_ROT。
SCREEN_T = 13.4
SCREEN_Z0 = DISC_TOP + 50.0                 # 92.2
sc = read_stl(MODELS / "screen_150x169_t13/screen_150x169_t13.stl") \
     + np.array([0.0, 0.0, SCREEN_Z0])
sc = rot_z(sc, ROTOR_ROT + V3_SCR_ROT)
parts.append(("dual_screen", sc))
MLK_TOP = PCB_Z0 + 1.6 + 1.2                # 64.6 米联派板顶+针尾

# 10b) 转子电路罩 rotor_shroud_v3 (2026-07-27, 用户: 把屏幕以下电路部分遮起来,
#      整体像个圆柱): Φ170 齐盘缘 / 壁 3 / 高 50 (承载面 42.2 → 屏底 92.2),
#      两半对开 + 3 厚封顶带屏缝; 每半 2× M3×55 经内立柱拧进 rim_ring 4 个
#      空闲外圈环孔 (装配 112.5/157.5/292.5/337.5°) 到 hub 底铜花螺母。
#      随屏组转 V3_SCR_ROT (立柱角 = 零件系 22.5/157.5/202.5/337.5°)。
SHROUD_DIR = V3 / "models/rotor_shroud_v3"
for _tag in ("A", "B"):
    _sh = read_stl(SHROUD_DIR / f"shroud_half_{_tag}_v3.stl") + np.array([0.0, 0.0, DISC_TOP])
    parts.append((f"shroud_half_{_tag}_v3", rot_z(_sh, ROTOR_ROT + V3_SCR_ROT)))
print(f"支架翼板底 {DISC_TOP+21.0:.1f} / 中央缺口顶(±60内) {DISC_TOP+50.0:.1f} (米联派顶 {MLK_TOP:.1f}); "
      f"双面屏模组 {SCREEN_Z0:.1f}..{SCREEN_Z0+168.75:.1f} (LED 面 X=±{SCREEN_T/2:.2f})")

# 11) 光电同步 v3 (2026-07-23 大改: 搬到顶部轴心区, 整体尺寸最小化):
#     sensor_module 平贴压条顶 (随转子): 模块局部 rotZ-90 后贴 (capX -3..20,
#     capY -55..-35), 模块绕孔中点 M(0,-45) 转 22.19°, 孔 (±2.64, -38.5/-51.5), 光轴过圆心, 刀片中心 r41.7;
#     2×M3 入压条 v5 的方螺母囚窝。静止挡光片 = vane_slider_v3 可调滑片
#     (2026-07-24 终版: 刀片印长 50 装机剪短补偿架高), 锁 frame_B 45° 臂筋侧,
#     刀尖调到 asm 280 (光轴 ~282.4, 叉顶 285.65 对筋底 290 留 4.35)。
sm = read_stl(MODELS / "photo_sensor/sensor_module.stl")
sm = sm[..., [1, 0, 2]] * np.array([1.0, -1.0, 1.0])   # rotZ-90: (x,y)->(y,-x)
sm = sm + np.array([-3.0, -45.0, 267.95])
# 六改: 绕孔线中点 M(0,-45) 转 22.196° → 光轴过圆心 (sin th = 17/45)
_th = np.arcsin(17.0 / 45.0)   # 22.196°
_R = np.array([[np.cos(_th), -np.sin(_th)], [np.sin(_th), np.cos(_th)]])
_M = np.array([0.0, -45.0])
sm[..., :2] = (sm[..., :2] - _M) @ _R.T + _M   # 2026-07-23: 孔挪条中线 (capX0), 梁线 capX+17
parts.append(("sensor_module", rot_z(sm, ROTOR_ROT + V3_SCR_ROT)))
# (2026-07-23 曾长死在 frame_B 筋底; 2026-07-24 改独立滑片, 见 frame 段后。)

# 12) WiFi (同 v2.1 定稿): wifi_shell 倒扣罩 (开口/沿朝下) + 放平模块孪生,
#     盒位 XC43 + 长边平移 -13, 随 135° 组转, 长边平行 pi2hub。
WIFI_ROT_EXTRA = 135.0
XC_WIFI, YC_WIFI = 43.0, -13.0
WS_H, WS_W = 18.1, 46.4
ws = read_stl(MODELS / "usb_wifi/wifi_shell.stl")
ws = ws[..., [2, 1, 0]] * np.array([1.0, 1.0, -1.0])   # rotY(+90), det=+1
ws[..., 0] += XC_WIFI - WS_W / 2
ws[..., 1] += YC_WIFI
ws[..., 2] += WS_H + DISC_TOP
parts.append(("wifi_shell", rot_z(ws, ROTOR_ROT + WIFI_ROT_EXTRA)))
wm = read_stl(MODELS / "usb_wifi/usb_wifi_module_flat.stl") + np.array([0.0, 0.0, DISC_TOP])
parts.append(("usb_wifi_module", rot_z(wm, ROTOR_ROT + WIFI_ROT_EXTRA)))

# 13) 顶部定心轴承: 柱 + frame_A/B_v2 沿用 v2; 转子侧 top_cap_v3_1 薄压条
#     (2026-07-22: 用户"只连左右两个 M3 孔, 做薄" → 31.75 厚压梁块改 7 厚
#     扁条 18×140, 底 260.95 = 屏顶, 顶 267.95)。
#     轴五金: M6×20 平头 (底面 Φ13×2.7 头窝, 先装后压屏) + Φ8×30 螺柱 + 双 688。
CAPTOP_V3 = 267.95
# 2026-07-22: 柱内移 1 格 ±125 → ±100 + frame_A/B_v2_1 短臂版 (同 v2.1)
# 2026-07-22: 帽变薄后五金按 1cm 分辨率重选最短 — 柱 300→280 (架臂底 280
# 对条顶 267.95 留 12.05 ≥ 5), 轴承降至 283..288/291..296; 螺柱 Φ8×30
# (267.95..297.95, 底坐条顶, 顶完整穿过上 688 顶 296), 螺丝 M6×20
# (头 260.95..263.65, 杆到 280.95, 旋入螺柱 13)。整机 322.7 → 297.95。
# 2026-07-23 光电大改配套: 柱 280→290 (+1cm, 光电叉顶 285.65 对臂底留 4.35),
# 螺柱 Φ8×30→Φ8×40; 同日柱再内移 1 格 ±100→±75 (POST_R 106.07, frame 换 v3 短臂,
# 转子 84.5 对柱内缘 102 留 17.6)。
# 2026-07-31 (用户圈图确认): 柱**就用网格板自带的 4 个安装孔**固定 —— POST_XY 与
#   BB_MOUNT 恒等 (都是 75), 柱轴心即安装孔轴心。紧固: M6×16 内六角圆柱头自板底穿
#   Φ6.5 (板顶起 7mm 那段) 拧进柱底轴向 M6 内丝, 咬合 9mm; 头 Φ10×6 沉平在 Φ11×6 里。
#   ⚠ 不能用螺母 —— M6 螺母对角 11.55 > 沉孔 Φ11, 塞不进。
POST_H, POST_XY = 290.0, 75.0
assert POST_XY == BB_MOUNT, "柱位必须与底板 4 安装孔重合"
for px in (-POST_XY, POST_XY):
    for py in (-POST_XY, POST_XY):
        post = m3d.Manifold.cylinder(POST_H, 4.0, 4.0, 24, False).translate((px, py, 0.0))
        parts.append((f"post @({px:+.0f},{py:+.0f})", mesh_tris(post)))
FRAME_DIR = V3 / "models/top_bearing_v3"
fa = read_stl(FRAME_DIR / "frame_A_v3.stl")
fa = rot_z(fa, 135.0)
fa[..., 2] += POST_H
parts.append(("frame_A_v3 (SW+NW)", fa))
fb = read_stl(FRAME_DIR / "frame_B_v3.stl")            # 打印翻转姿态
fb[..., 1] = -fb[..., 1]
fb[..., 2] = POST_H + 16.0 - fb[..., 2]
fb = fb[:, ::-1, :].copy()
fb = rot_z(fb, -45.0)
parts.append(("frame_B_v3 (NE+SE)", fb))
# 挡光滑片 vane_slider_v3 (静止; 终版: 两件都圆孔, 调节=刀片印长50装机剪短):
# 锁 frame_B ang=90 臂筋 (asm 45°) 侧面, M3×20+螺母 ×2 穿筋孔 (r45.2/51.4,
# 居中 z4 = asm 294); 板 8 高填满筋侧 (底平筋底 290, 顶抵臂底 298), 装配用已剪短孪生 (刀尖 280)
vs = read_stl(V3 / "models/photo_sensor_v3/vane_slider_v3_asm.stl")
vs = vs[..., [0, 2, 1]].copy()          # 打印姿态 (x,z,y-2) → 件系
vs[..., 1] += 2.0
vs = vs[:, ::-1, :]                     # 轴交换镜像 → 翻回绕向
vs = rot_z(vs, 45.0)
vs[..., 2] += 290.0
parts.append(("vane_slider_v3", vs))
# top_cap_v3_1 顶部薄压条 v3 (2026-07-22: 用户"做薄"):
# 扁条 18×140×7 (底 260.95 = 屏顶, 压住双屏; 顶 267.95 = CAPTOP),
# 2× 盘头 M3×12~14 经 Φ3.2 平面通孔拧进屏顶孔 (0,±64) (中央孔被轴占);
# M6×20 平头藏底面 Φ13×2.7 头窝 (⚠ 先装 M6 再压屏), 头 260.95..263.65。
cap = read_stl(V3 / "models/top_cap_v3_1/top_cap_v3_1.stl")  # 打印翻转姿态
cap[..., 1] = -cap[..., 1]
cap[..., 2] = CAPTOP_V3 - cap[..., 2]
cap = cap[:, ::-1, :].copy()
cap = rot_z(cap, ROTOR_ROT + V3_SCR_ROT)
parts.append(("top_cap_v3_1 (rotor)", cap))
scr = m3d.Manifold.cylinder(17.3, 3.0, 3.0, 32, False).translate((0, 0, 263.65))
parts.append(("M6x20 screw (rotor)", mesh_tris(scr)))
sto = m3d.Manifold.cylinder(40.0, 4.0, 4.0, 48, False).translate((0, 0, 267.95))
parts.append(("standoff Φ8×40 (rotor)", mesh_tris(sto)))
for bz, tag in ((POST_H + 3.0, "688 lower (frame_A)"), (POST_H + 11.0, "688 upper (frame_B)")):
    brg = (m3d.Manifold.cylinder(5.0, 8.0, 8.0, 64, False)
           - m3d.Manifold.cylinder(7.0, 4.0, 4.0, 64, False).translate((0, 0, -1.0)))
    parts.append((tag, mesh_tris(brg.translate((0.0, 0.0, bz)))))
print(f"顶轴承 (柱±{POST_XY:.0f}×{POST_H:.0f}, POST_R 106.07): 柱顶 {POST_H:.0f}; 薄压条 260.95..{CAPTOP_V3:.2f} "
      f"(底=屏顶 {SCREEN_Z0+168.75:.2f}); 架臂底-条顶隙 {POST_H-CAPTOP_V3:.2f}; "
      f"轴承 {POST_H+3:.0f}..{POST_H+8:.0f} / {POST_H+11:.0f}..{POST_H+16:.0f}; "
      f"螺柱 Φ8×30 @{CAPTOP_V3:.2f}..{CAPTOP_V3+30:.2f}, M6×20 杆到 280.95 (旋入 13)")

# 报告 d100 4 脚落点 (应为 (±50,0)/(0,±50))
_feet = [(-37.5, 37.5), (37.5, 37.5), (-37.5, -37.5), (37.5, -37.5)]
_rf = math.radians(ROT); _c, _s = math.cos(_rf), math.sin(_rf)
print("底座 4×M6 脚 (转%g° 后, 应落网格位 ±37.5):" % ROT,
      ["(%.1f,%.1f)" % (_c*fx - _s*fy, _s*fx + _c*fy) for (fx, fy) in _feet])

# ===== merge + export =====
all_tris = np.concatenate([t for (_, t) in parts], axis=0)
out = ROOT / "assembly_v4.stl"
_header = b"POV3D assembly_v4"
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
COLORS = {"grid plate 200x200x13": "#333333", "baseplate_collar_v4": "#777777",
          "flange_disc_v4": "#88aacc", "mounting_flange_v4": "#cccc77",
          "motor (placeholder)": "#444444", "hub_disc (rotor, 下)": "#ccaa55",
          "rim_ring (rotor, 上/承载盘)": "#9ccf9c",
          "pi2hub75e (下板)": "#2a7d2a", "nylon standoffs ×4": "#dddddd",
          "mlkpai_board (上)": "#e03020",
          "portal_tee A": "#aa6622", "portal_tee B": "#aa6622",
          "sensor_module": "#222266",
          "dual_screen": "#3355cc",
          "shroud_half_A_v3": "#b0b8c8", "shroud_half_B_v3": "#98a0b0",
          "wifi_shell": "#22aaaa",
          "usb_wifi_module": "#111111",
          "frame_A_v3 (SW+NW)": "#5577aa", "frame_B_v3 (NE+SE)": "#5577aa",
          "top_cap_v3_1 (rotor)": "#cc8888", "M6x20 screw (rotor)": "#888888",
          "standoff Φ8×30 (rotor)": "#888888",
          "vane_slider_v3": "#cc6644", "688 lower (frame_A)": "#999999", "688 upper (frame_B)": "#999999"}
for px in (-75, 75):
    for py in (-75, 75):
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
png = ROOT / "assembly_v4_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
