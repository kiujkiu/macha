"""
POV3D 装配 V1.1  (assembly_v1_1)  ——  2026-10-21, 在 V1.0 上改两处 (用户):
  1. 底板 200×200×13 方网格板 → **Φ200×13 圆网格板** (图纸 2026-10-21): M6 网格节距 25 (±12.5 起, 同旧板),
     圆内 52 孔; 另 4-Φ6.5 沉孔 (±50, ±75) (节距 100×150, 落在网格孔中间), 沉孔尺寸图上没标, 按 M6 内六角
     Φ11×6.5 从顶面画 (仅示意)。定子 baseplate_collar_v4 的 4×M6 (±37.5,±37.5) 仍在网格位上。
  2. **拆掉四周 4 根立柱** ⇒ 挂在柱上的 frame_A/B、688×2、Φ8 螺柱、M6×20、挡光滑片一起拆。
     顶部固定方式待用户定; 顶盖 (含光电模块座) 和光电模块还在转子上, 静止挡光片没了。
其余 (转子盘 / 屏 / 底座 / WiFi / FPC) 与 V1.0 完全相同, 零件 STL 直接读 v1.0/models、v1.0/boards。
"""
import math
import struct
import sys
from pathlib import Path
import numpy as np
import manifold3d as m3d

ROOT = Path(__file__).parent                 # pov3d/v1.1
V10 = ROOT.parent / "v1.0"                   # 零件/板孪生全部沿用 V1.0
V04 = ROOT.parent / "v0.4"
MODELS = ROOT.parent / "models"
BOARDS = V10 / "boards"
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])


def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    tris = np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)
    return tris["verts"].astype(np.float64)


def mesh_tris(man):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    return v[np.asarray(m.tri_verts)]


def xform(t, R, T=(0.0, 0.0, 0.0)):
    """t[...,3] @ R^T + T; 行列式为负 (镜像) 时翻转三角形绕向。"""
    R = np.asarray(R, float)
    out = t @ R.T + np.asarray(T, float)
    if np.linalg.det(R) < 0:
        out = out[:, ::-1, :].copy()
    return out


def box(x0, x1, y0, y1, z0, z1):
    return mesh_tris(m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0)))


parts = []

# ===================== 1. 定子 + 转子盘: 原样沿用 V0.4 =====================
BB_D, BB_T = 200.0, 13.0
BB_GRID_ABS = (12.5, 37.5, 62.5, 87.5)
BB_GRID = [s * v for v in BB_GRID_ABS for s in (-1, 1)]
BB_HOLE_RMAX = 96.0                           # 图上 (87.5,37.5) r95.2 有, (87.5,62.5) r107 没有
BB_MOUNT = [(sx * 50.0, sy * 75.0) for sx in (-1, 1) for sy in (-1, 1)]
BB_MOUNT_D, BB_CB_D, BB_CB_H = 6.5, 11.0, 6.5  # 沉孔尺寸图上没标, 按 M6 内六角估
bb = m3d.Manifold.cylinder(BB_T, BB_D / 2, BB_D / 2, 256, False).translate((0, 0, -BB_T))
BB_NHOLE = 0
for bx in BB_GRID:
    for by in BB_GRID:
        if math.hypot(bx, by) < BB_HOLE_RMAX:
            bb -= m3d.Manifold.cylinder(BB_T + 2, 3.0, 3.0, 16, False).translate((bx, by, -BB_T - 1.0))
            BB_NHOLE += 1
for mx, my in BB_MOUNT:
    bb -= m3d.Manifold.cylinder(BB_T + 2, BB_MOUNT_D / 2, BB_MOUNT_D / 2, 24, False).translate((mx, my, -BB_T - 1.0))
    bb -= m3d.Manifold.cylinder(BB_CB_H + 1, BB_CB_D / 2, BB_CB_D / 2, 32, False).translate((mx, my, -BB_CB_H))
assert BB_NHOLE == 52, BB_NHOLE
parts.append(("grid plate D200x13", mesh_tris(bb)))

# 2026-10-21 用户: 透明罩 OD200 (玻璃 8 → 亚克力 5) 罩整机 (比全部件再高 100) + 底板上一块宽 40 的 PCB。
# 定位环 glass_seat_v1_1 (底座圈 + 内定位唇, M6 锁网格孔), PCB 尺寸在同一个文件里算。
sys.path.insert(0, str(ROOT / "models"))
import glass_seat_v1_1.build_stl as GS   # noqa: E402
parts.append(("glass_seat_v1_1", read_stl(ROOT / "models/glass_seat_v1_1/glass_seat_v1_1.stl")))
_pcb = m3d.Manifold.cube((GS.PCB_L, GS.PCB_W, GS.PCB_T), False).translate((-GS.PCB_L / 2, GS.PCB_Y0, GS.PCB_Z0))
parts.append((f"base PCB {GS.PCB_W:g}x{GS.PCB_L:g}", mesh_tris(_pcb)))
parts.append((f"base PCB component envelope (≤{GS.PCB_COMP_H:.1f})", mesh_tris(
    m3d.Manifold.cube((GS.PCB_L - 2, GS.PCB_W - 2, GS.PCB_COMP_H), False)
    .translate((-GS.PCB_L / 2 + 1, GS.PCB_Y0 + 1, GS.PCB_Z0 + GS.PCB_T)))))

BPC_COLLAR_TOP, BPC_BOSS_TOP = 15.5, 25.5
parts.append(("baseplate_collar_v4", read_stl(V04 / "models/baseplate_collar_v4/baseplate_collar_v4.stl")))
parts.append(("flange_disc_v4", read_stl(V04 / "models/flange_disc_v4/flange_disc_v4.stl")
              + np.array([0.0, 0.0, BPC_COLLAR_TOP])))
mf = read_stl(V04 / "models/mounting_flange_v4/mounting_flange_v4.stl")
parts.append(("mounting_flange_v4", xform(mf, np.diag([1, -1, -1]), (0, 0, BPC_BOSS_TOP))))

MOTOR_D, MOTOR_H, MOTOR_Z0 = 50.0, 26.7, 5.0
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H                 # 31.7
parts.append(("motor (placeholder)", mesh_tris(
    m3d.Manifold.cylinder(MOTOR_H, MOTOR_D/2, MOTOR_D/2, 64, False).translate((0, 0, MOTOR_Z0)))))
# 2026-10-20 用户: 转子盘 Φ170 → Φ180, 外圈 8 孔 R77.5 → 82.5 ⇒ hub_disc_v1_0 / rim_ring_v1_0
parts.append(("hub_disc_v1_0", read_stl(V10 / "models/hub_disc_v1_0/hub_disc_v1_0.stl") + np.array([0.0, 0.0, ROTOR_Z0])))
DISC_TOP = ROTOR_Z0 + 10.5                    # 42.2 承载面
# 2026-10-20: rim_ring → rim_ring_v1_0 (删 pi2hub 7 孔 + wifi 4 孔; 加 DR1M90 4 垫柱孔 + 屏幕底座 4 铜螺母孔)
parts.append(("rim_ring_v1_0", xform(read_stl(V10 / "models/rim_ring_v1_0/rim_ring_v1_0.stl"),
                                     np.diag([1, -1, -1]), (0, 0, DISC_TOP))))

# ===================== 2. DR1M90 底板 + FS03 =====================
# 底板 10-16 版: 板体 140×80×1.6 (板系原点 = 板中心, 顶面 Z1.59)。顶面 4 只 SMD 铜柱
# (±60,±30)/(±60,±20) 是本版新加的。暂按「5 高垫柱坐盘面」放 (同 V0.4 pi2hub)。
BASE_SPACER = 5.0
BASE_Z0 = DISC_TOP + BASE_SPACER              # 底板底面
# 底板朝向 = 让两个 FPC 座各自正对同侧桥板的 FPC2 (见 §4 校核), 候选 0/90/180/270 自动挑
BASE_FPC = [(34.76, 35.6), (-34.76, -35.6)]   # 连接器位置 csv: FPC1 / FPC2

# FS03 (旧 mlkpai_board 孪生 85×56, 板底 Z0, 排针体 -2.6..0 朝下): 公针体落在底板
# H1/H2 母座顶 (板系 Z10.09) 上 ⇒ FS03 板底 = 底板底 + 10.09 + 2.6。排针中线在底板
# (0.125, -0.56), 孪生排针 ±24.15 (底板 H1/H2 间距 48.20 vs 48.30, 差 0.1 忽略)。
FS03_DZ = 10.09 + 2.6
FS03_C = (0.125, -0.56)

# ===================== 3. 灯板 ×2 + 桥板 ×2 (+核心板占位) =====================
# 灯板板系 (Altium Gerber 原点 = LED 区中心): 板体 X ±81.98, Y -140.66..84.36,
# Z -1.84..0 (Z0 = Top = 2260/铜柱面 = 背面; Z-1.84 = Bottom = LED 面, CN1/CN2 也在此面)。
# 背面 6 只 M2.5 贴片铜柱 (±78.47, 79.35/-28.15/-135.65) 高出 Top 3.32 —— 2026-10-20 作废, 见下。
LED_T = 1.84
# 2026-10-20 用户定屏幕锁紧方式 (v1.0/concept/ 示意 3 版): 两板背靠背间距 **4.6 = M3 通孔六角铜螺母
# 对边**, 螺母**侧躺**在缝里 (轴线竖直), 每侧 3 组 × 2 颗上下叠 (上颗焊 A / 下颗焊 B, 拆螺丝两屏
# 即分开); 每侧 2 根 M3: 上螺丝从顶盖往下锁上组, 下螺丝从底座顶托往上穿下组锁进中组。
# 孪生里删掉 STEP 的 6 只立式铜柱 (其余背面件 ≤2.3, STEP 里没有 2260/220µF/LED 本体)。
BACK_GAP = 4.6
# ★ 偏心 (同 V0.4 --ecc 的做法): 双面屏整组沿厚度方向平移半个 LED 面间距, 让**面 B 的
#   LED 面正好落在旋转轴 X=0**, 面 A 在 X=2×SCR_ECC。V0.4 是 13.4 厚屏平移 +6.7;
#   这里 LED 面间距 = 2×(2.3+1.84) = 8.28 ⇒ SCR_ECC = 4.14 (按 PCB 的 LED 面算, LED 本体高未计)。
#   灯板/桥板/核心板一起平移。--center 退回居中。
SCR_ECC = 0.0 if "--center" in sys.argv else BACK_GAP / 2 + 1.84
LED_EDGE_BOT = -140.66                        # 板下沿 (板系 Y)
LED_AREA_BOT, LED_AREA_TOP = -84.375, 84.375
LED_EDGE_TOP = 84.36

# 桥板板系 (嘉立创, 原点在板外): 板中心 (65.91, 38.86); CN1/CN2 在底面 (Z<0) 朝灯板,
# 四角铜柱 (±60,±20 相对中心) 在底面高 3.33 ⇒ 桥板底面距灯板 LED 面 3.33
# (灯板 AXK 头 2.16 + 桥板 AXK 座 2.50 = 4.66, 插合重叠 1.33 ✓)。
BR_C = (65.91, 38.86)
BR_GAP = 3.33
BR_ON_LED_Y = -112.908                        # 灯板 CN1/CN2 / JP1-4 中心行
# ★ 桥板翻面方式 (待硬件确认, 即交接说明里「脚号方向 101-n」那条):
#   True  = 绕 Y 翻 (板系 X 镜像): 桥 CN1 落灯板 CN2 位; FPC2 落下沿 (-134.3) 且
#           X 正对底板同侧 FPC 座; VH 电源座/电解等高件全在下沿 —— 几何证据都指向这个
#   False = 绕 X 翻: 桥 CN1↔灯板 CN1 同名; 但 FPC2 与 VH 座跑到上沿贴着 LED 区
BRIDGE_MIRROR_X = "--bridge-xflip" not in sys.argv


def bridge_to_led(t):
    """桥板板系 → 灯板板系。"""
    t = t - np.array([BR_C[0], BR_C[1], 0.0])
    if BRIDGE_MIRROR_X:
        R = np.diag([-1.0, 1.0, -1.0])        # 绕 Y 转 180°
    else:
        R = np.diag([1.0, -1.0, -1.0])        # 绕 X 转 180°
    return xform(t, R, (0.0, BR_ON_LED_Y, -LED_T - BR_GAP))


# ACG525-CORE-V2 核心板模块 (2026-10-16 用户: 实物是 V2; 按官方封装当一个模块, 板厚 1.6)。
# 封装 = `发票内容/ACG525-CORE_LIB.zip` → ACG525-CORE.PcbLib「ACG525-CORE_NEW260310」
# (boards/pcblib_dump.py 解析), 封装系 mm:
#   两只 LB3524-G100P 插头沿 X: A 中心 (23.002, 2.169), B 中心 (22.791, 28.805)
#   ⇒ **中心距 26.636**, 沿长向错开 0.211; 排距 3.3
#   4×Ø2.7 孔 (0/46, 0/31) = 46×31; 板框 (TopOverlay 圆角框) X -2.286..48.260 Y -2.286..33.274
#   = **50.546×35.560 R1.27** (2026-10-16 修正: 之前把丝印包络 Y 到 36.195 当板框, 多算了
#   板外那个方向箭头 (X 37.97..42.67, Y 34.16..36.20), 宽了 2.92)
# 🔴 桥板 10-14 版 CN3/CN6 (同为 LB3524-G100P, 焊盘关于元件原点对称) 元件中心距
#    3304.2184-2280.6024 = 1023.616 mil = **26.000** ≠ 26.636 ⇒ **V2 核心板插不上, 桥板要改**。
#    本装配把核心板两插头中点对准 CN3/CN6 中点, 每边差 0.32 (只为看结构)。
#   (小梅哥 `06_硬件图纸/ACG525-CORE核心板封装.zip` 是旧版 V1/ACA420 封装, 中心距 26.00 —— 桥板数字跟它一样)
# 插合高度: LB3524 无 3D/规格书在手, 暂按灯板↔桥板那对 AXK 实测 3.33 (插头体高 2.16)。
CORE_FP_C = ((23.002 + 22.791) / 2, (2.169 + 28.805) / 2)   # 两插头中点 (封装系)
CORE_OUT = (-2.286, 48.260, -2.286, 33.274)  # 板框 50.546×35.560, 四角 R1.27
CORE_R = 1.27
CORE_HOLES = [(x, y) for x in (0.0, 46.0) for y in (0.0, 31.0)]
CORE_HDR = [(23.002, 2.169), (22.791, 28.805)]
CORE_T, CORE_MATE, HDR_H = 1.6, 3.33, 2.16
# 2026-10-16 桥板改版 (高云转接板1016.zip, 飞针文件): CN6 (2280.600,1530.330) 不动, CN3 移到
# (3329.220,1538.637) mil ⇒ 中心距 1048.620 mil = 26.635 / 错位 8.307 mil = 0.211 ✓ 对上 V2;
# 新增核心板 4 孔 PRENULL1-4 = 46×31 @ (71.232,39.079)。STEP 仍是 10-15 旧版 (只有 CN3 3D 位置旧)。
CORE_C = (71.245, 38.976)                    # 桥板 CN3/CN6 信号焊盘中点 (桥板系, 10-16 版)


def acg525_module():
    """封装系建模 (板底 Z0, 插头朝 -Z), 返回 manifold。"""
    x0, x1, y0, y1 = CORE_OUT
    r = CORE_R
    m = m3d.Manifold.hull(m3d.Manifold.compose([
        m3d.Manifold.cylinder(CORE_T, r, r, 24, False).translate((cx, cy, 0.0))
        for cx in (x0 + r, x1 - r) for cy in (y0 + r, y1 - r)]))
    for hx, hy in CORE_HOLES:
        m -= m3d.Manifold.cylinder(CORE_T + 2, 1.35, 1.35, 32, False).translate((hx, hy, -1.0))
    for hx, hy in CORE_HDR:
        m += m3d.Manifold.cube((28.2, 4.6, HDR_H), False).translate((hx - 14.1, hy - 2.3, -HDR_H))
    return m


# 封装系 → 桥板系: 插头在封装里沿 X, 桥板 CN3/CN6 沿桥板 Y ⇒ 转 90°; 板底在桥板顶 +3.33
_core = mesh_tris(acg525_module()) - np.array([CORE_FP_C[0], CORE_FP_C[1], 0.0])
core_br = xform(_core, [[0, -1, 0], [1, 0, 0], [0, 0, 1]], (CORE_C[0], CORE_C[1], 1.59 + CORE_MATE))

led = read_stl(BOARDS / "led_icn2260_v01_260921_lite.stl")
bridge = read_stl(BOARDS / "bridge_gw5a_2026-10-15_lite.stl")
_c = led.mean(axis=1)
_old_so = np.zeros(len(led), bool)
for _sx in (78.47, -78.47):
    for _sy in (79.35, -28.15, -135.65):
        _old_so |= (np.hypot(_c[:, 0] - _sx, _c[:, 1] - _sy) < 3.5) & (_c[:, 2] > 0.01)
module_led = led[~_old_so]                    # 灯板系, 去掉立式铜柱
assert module_led[..., 2].max() <= BACK_GAP / 2 + 1e-6, "灯板背面还有件高过 2.3, 会顶到对面板"
module_br = bridge_to_led(bridge)
module_core = bridge_to_led(core_br)


def led_to_world(t, face, z_area_bot):
    """face=+1: LED 面朝 +X 的那块 (A); face=-1: 绕 Z 转 180° 的 B。
    A: 板系 (x,y,z) → 世界 (BACK_GAP/2 - z, -x, y + dz)   (det +1)
    """
    dz = z_area_bot - LED_AREA_BOT
    R = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], float)
    w = xform(t, R, (BACK_GAP / 2, 0.0, dz))
    if face < 0:
        w = xform(w, np.diag([-1.0, -1.0, 1.0]))
    return w + np.array([SCR_ECC, 0.0, 0.0])


# ---- 先放底板/FS03, 再由它们的顶高定灯板模组高度 ----
def place_base(rot_deg):
    r = math.radians(rot_deg)
    Rz = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
    return Rz


def fpc_world_bridge(face, z_area_bot):
    """桥板 FPC2 座中心 (桥板系 31.15,17.47, 顶面) 的世界坐标。"""
    p = np.array([[[31.15, 17.47, 1.59]] * 3])
    return led_to_world(bridge_to_led(p), face, z_area_bot)[0, 0]


best = None
for rot in (0.0, 90.0, 180.0, 270.0):
    Rz = place_base(rot)
    err = 0.0
    for face in (+1, -1):
        fb = fpc_world_bridge(face, 0.0)
        # 桥 FPC 在 X 侧 sign(face); 底板两个 FPC 座里挑同侧那个比 Y
        cand = [Rz[:2, :2] @ np.array(c) for c in BASE_FPC]
        same = [c for c in cand if np.sign(c[0]) == face]
        err += min(abs(c[1] - fb[1]) for c in same) if same else 1e3
    if best is None or err < best[1]:
        best = (rot, err)
BASE_ROT = best[0]
Rb = place_base(BASE_ROT)
base = xform(read_stl(BOARDS / "base_dr1m90_2026-10-16_lite.stl"), Rb, (0, 0, BASE_Z0))
parts.append(("DR1M90 base (10-16)", base))
fs = read_stl(MODELS / "mlkpai_board/mlkpai_board.stl")
# FS03 实测 (2026-10-16 用户卡尺): **板底 → 最高件顶 = 15.4** —— RJ45 (P2) 与 USB-A (J6, 立式)
# 叠在板右侧长边 (手册外形 85×56×18.1 = 15.4 + 排针塑料座 2.6 ✓)。位置量自位号图 TOP
# (`03_参考设计_米联客FS03/MLKPAI-FS03_240909位号图.pdf`, 8.53 px/mm, 板中心原点 +Y=J11):
#   RJ45 X 21.4..43.3 Y -19.8..-3.6 / USB-A X 22.0..42.7 Y -2.5..3.6 ⇒ 合并包络 X 21.4..43.3 Y -19.8..3.6
# 其余器件 (BGA/DDR/电源) 按板面 +3 包络。⚠ FS03 插底板 H1/H2 的朝向 (J11 对 H1 还是 H2) 未核,
#   转 180° 时 RJ45 换到另一侧 —— 两根 FPC 走线都按「头顶有 RJ45」校核。
FS03_H = 15.4
FS03_T = 1.6
FS03_COMP = 3.0
FS03_TALL = (21.4, 43.3, -19.8, 3.6)
_tall = box(FS03_TALL[0], FS03_TALL[1], FS03_TALL[2], FS03_TALL[3], FS03_T, FS03_H)
_comp = box(-42.5, 42.5, -28.0, 28.0, FS03_T, FS03_T + FS03_COMP)
fs = np.concatenate([fs, _tall, _comp]) + np.array([FS03_C[0], FS03_C[1], 0.0])
fs = xform(fs, Rb, (0, 0, BASE_Z0 + FS03_DZ))
parts.append(("FS03 (mlkpai twin + RJ45/USB 15.4)", fs))
FS03_Z0 = BASE_Z0 + FS03_DZ
FS03_TOP = FS03_Z0 + FS03_H

# ---- WiFi: 平放在 FS03 正上方 (2026-10-16 用户: "放在板子正上方, 灯板与 soc 中间, 平放") ----
# 沿用 V0.4 的平放孪生 usb_wifi_module_flat (AX1800, 天线折平 14.5×40×70) + wifi_shell 倒扣罩
# (外 18.1 高 × 46.4 × 96.6 含两端螺丝沿), 居中、长边沿 Y、USB 头朝 +Y (同 FS03 J6 出口方向)。
# 托板 wifi_plate_v1_0 (2026-10-20 用户: 一块板 + 4 个 M3 孔, 尼龙螺柱固定; H 形给 USB 线留口):
#   4 根 M3 尼龙螺柱 (M-F, 25) 立在底板 10-16 版顶面 4 只贴片铜柱上 —— 位置 = 底板 4 个 Φ4.2 板孔
#   (params BASE_HOLES_BOARD)。⚠ 之前占位托架 4 柱里 (60,30) 那只是错的 (那里没铜柱, 应为 (60,-20))。
#   托板高 = 铜柱顶 + 尼龙柱长 (不再按 "RJ45 顶 + 1" 算; 现在余 1.82)。
# ⚠ wifi_shell 在 V0.4 位置做过 R83.5 盘缘裁切, 挪到这里后那一角只是沿上的小缺口; +Y 端螺丝沿落在 H 口上方, 罩待重做。
WIFI_DY = -6.0          # 整体往 -Y 挪, 让 +Y 的 USB 头 + AF 母头别顶到 +Y 屏幕底座
SHELF_CLR_MIN = 1.0     # 托板底离下方最高件 (RJ45) 至少
BASE_NUT_TOP = 4.91     # 铜柱顶 (板系 Z)
LED_GAP_WIFI = 3.0      # 灯板下沿离 wifi 罩顶
sys.path.insert(0, str(V10 / "models"))
import params_v1_0 as P1                      # noqa: E402
from wifi_plate_v1_0.build_stl import NYLON_L, PLATE_T, PLATE_X, PLATE_Y, HOLES as PLATE_HOLES  # noqa: E402


def _under(xlo, xhi, ylo, yhi, names=("DR1M90", "FS03")):
    """窗口内下方件最高 Z —— 按三角形外包盒与窗口相交判 (保守; 只看顶点会漏掉跨过窗口的大面)。"""
    z = 0.0
    for name, t in parts:
        if name.startswith(names):
            lo, hi = t.min(axis=1), t.max(axis=1)
            m = (hi[:, 0] >= xlo) & (lo[:, 0] <= xhi) & (hi[:, 1] >= ylo) & (lo[:, 1] <= yhi)
            if m.any():
                z = max(z, hi[m, 2].max())
    return z


for (_hx, _hy), (_bx, _by) in zip(PLATE_HOLES, P1.BASE_HOLES_BOARD):
    _w = Rb @ np.array([_bx, _by, 0.0])
    assert abs(_w[0] - _hx) < 1e-6 and abs(_w[1] - _hy) < 1e-6, "托板孔与底板铜柱不同心"
SHELF_Z0 = BASE_Z0 + BASE_NUT_TOP + NYLON_L
SHELF_CLR = SHELF_Z0 - _under(-PLATE_X, PLATE_X, -PLATE_Y, PLATE_Y)
assert SHELF_CLR >= SHELF_CLR_MIN, f"托板压到 FS03/RJ45 (余 {SHELF_CLR:.2f})"
SHELF_T = PLATE_T
SHELF_TOP = SHELF_Z0 + SHELF_T
parts.append(("wifi_plate_v1_0", read_stl(V10 / "models/wifi_plate_v1_0/wifi_plate_v1_0.stl")
              + np.array([0.0, 0.0, SHELF_Z0])))
_ny = [m3d.Manifold.cylinder(NYLON_L, 5.5 / math.sqrt(3), 5.5 / math.sqrt(3), 6, False)
       .translate((_hx, _hy, BASE_Z0 + BASE_NUT_TOP)) for _hx, _hy in PLATE_HOLES]
_ny += [m3d.Manifold.cylinder(3.0, 3.5, 3.5, 24, False).translate((_hx, _hy, SHELF_TOP)) for _hx, _hy in PLATE_HOLES]
parts.append((f"nylon standoff M3x{NYLON_L:g} ×4 + screw", mesh_tris(m3d.Manifold.batch_boolean(_ny, m3d.OpType.Add))))

WS_H, WS_W = 18.1, 46.4
ws = read_stl(MODELS / "usb_wifi/wifi_shell.stl")
ws = ws[..., [2, 1, 0]] * np.array([1.0, 1.0, -1.0])     # rotY(+90): 开口/沿朝下, 同 V0.4
ws = ws + np.array([-WS_W / 2, WIFI_DY, WS_H + SHELF_TOP])
parts.append(("wifi_shell", ws))
# 罩沿 ↔ 托板: 4× M3 从托板底往上 (Φ7×1.5 薄头在板底), 螺母在罩沿顶 (沿厚 3)
# (+12.5,37.3) 在 RJ45 正上方, 板底只余 1.82 —— 放不下螺母, 放得下 1.5 薄头 ⇒ 4 颗统一从下往上
from wifi_plate_v1_0.build_stl import SHELL_HOLES  # noqa: E402
_HD, _HH, _NH = P1.M3_HEAD_D, P1.M3_HEAD_H, 2.4
SHELL_SCREW_L = 10.0                                   # 板 3 + 沿 3 + 螺母 2.4 + 余 1.6
_ss = []
for _sx, _sy in SHELL_HOLES:
    _ss.append(m3d.Manifold.cylinder(_HH, _HD / 2, _HD / 2, 24, False).translate((_sx, _sy, SHELF_Z0 - _HH)))
    _ss.append(m3d.Manifold.cylinder(SHELL_SCREW_L, 1.5, 1.5, 16, False).translate((_sx, _sy, SHELF_Z0)))
    _ss.append(m3d.Manifold.cylinder(_NH, 5.5 / math.sqrt(3), 5.5 / math.sqrt(3), 6, False)
               .translate((_sx, _sy, SHELF_TOP + 3.0)))
parts.append((f"wifi shell screw M3x{SHELL_SCREW_L:g} (from below) + nut ×4",
              mesh_tris(m3d.Manifold.batch_boolean(_ss, m3d.OpType.Add))))
for _sx, _sy in SHELL_HOLES:
    _z = _under(_sx - _HD / 2, _sx + _HD / 2, _sy - _HD / 2, _sy + _HD / 2)
    _gap = SHELF_Z0 - _HH - _z
    print(f"  罩沿孔 ({_sx:+.1f},{_sy:+.1f}): 板底薄头 Φ{_HD:g}×{_HH:g} 下方最高 {_z:.2f} → 余 {_gap:.2f}")
    assert _gap > 0.2, "罩沿螺丝薄头碰到下方 FS03/RJ45"
wm = read_stl(MODELS / "usb_wifi/usb_wifi_module_flat.stl") + np.array([-43.0, 13.0 + WIFI_DY, SHELF_TOP])
# 2026-10-20 用户: 用扁平 USB 延长线 (AF 母 ↔ AMRI 弯头公)。孪生里的母头壳 (18.7×10.3×36.3) 当 AF 端占位,
# 去掉原 Φ4.8 圆线头; AF 尾出的扁线从 H 口往下折回, AMRI 弯头插 FS03 J6 (扁线本身未建模)。
_cbl = np.all(np.abs(wm[..., 0]) <= 2.41, axis=1) & np.all(wm[..., 1] >= wm[..., 1].max() - 20.0 - 1e-3, axis=1)
wm = wm[~_cbl]
WIFI_AF_END_Y = float(wm[..., 1].max())
parts.append(("wifi module (AX1800) + AF", wm))
WIFI_TOP = SHELF_TOP + WS_H
_wv = wm.reshape(-1, 3)
WIFI_RMAX = float(np.hypot(_wv[:, 0], _wv[:, 1]).max())

# 灯板模组高度 = wifi 罩顶 + 3 (之前用户调的 77.5 被 wifi 层取代)
LED_EDGE_BOT_Z = WIFI_TOP + LED_GAP_WIFI


def top_under(xlim, ylim=None):
    """在 |X|<=xlim (且 Y 在 ylim 内) 范围里, 底板 + FS03 的最高点。"""
    zmax = 0.0
    for name, t in parts:
        if not name.startswith(("DR1M90", "FS03", "wifi")):
            continue
        v = t.reshape(-1, 3)
        m = (np.abs(v[:, 0]) <= xlim) if np.isscalar(xlim) else (v[:, 0] >= xlim[0]) & (v[:, 0] <= xlim[1])
        if ylim is not None:
            m &= (v[:, 1] >= ylim[0]) & (v[:, 1] <= ylim[1])
        if m.any():
            zmax = max(zmax, v[m, 2].max())
    return zmax


# 模组 X 向包络 (A 面) —— 先用 dz=0 量
_tmp = np.concatenate([led_to_world(module_led, +1, 0.0), led_to_world(module_br, +1, 0.0),
                       led_to_world(module_core, +1, 0.0)]).reshape(-1, 3)
MOD_X = float(np.abs(_tmp[:, 0]).max())
STACK_TOP = max(top_under(MOD_X), WIFI_TOP)   # wifi 罩顶面是大平面, 顶点不落在模组带内, 单独算
CLEAR = LED_EDGE_BOT_Z - STACK_TOP
Z_AREA_BOT = LED_EDGE_BOT_Z + (LED_AREA_BOT - LED_EDGE_BOT)   # 板下沿 → LED 区下沿 = 56.3

for face, tag in ((+1, "A (+X)"), (-1, "B (-X)")):
    parts.append((f"LED board {tag}", led_to_world(module_led, face, Z_AREA_BOT)))
    parts.append((f"bridge {tag}", led_to_world(module_br, face, Z_AREA_BOT)))
    parts.append((f"ACG525 core {tag}", led_to_world(module_core, face, Z_AREA_BOT)))

LED_AREA_TOP_Z = Z_AREA_BOT + (LED_AREA_TOP - LED_AREA_BOT)
LED_EDGE_TOP_Z = Z_AREA_BOT + (LED_EDGE_TOP - LED_AREA_BOT)

# ===================== 3a. 屏幕组件锁紧 + 装到转子 (2026-10-20) =====================
# 零件参数在 v1.0/models/params_v1_0.py (底座/顶盖/rim_ring_v1_0 都从那取), 这里核对一致。
sys.path.insert(0, str(V10 / "models"))
import params_v1_0 as P1                      # noqa: E402
for _k, _v in (("LED_EDGE_BOT_Z", LED_EDGE_BOT_Z), ("LED_EDGE_TOP_Z", LED_EDGE_TOP_Z),
               ("DISC_TOP", DISC_TOP), ("BASE_ROT", BASE_ROT), ("BASE_SPACER", BASE_SPACER)):
    assert abs(getattr(P1, _k) - _v) < 0.01, f"params_v1_0.{_k}={getattr(P1, _k)} ≠ 装配 {_v:.3f}, 改参数后重跑零件"
assert SCR_ECC == P1.SCR_ECC and BACK_GAP == P1.BACK_GAP, "--center 下底座/顶盖螺丝孔对不上 (零件按偏心做)"


def _hex_z(af, h, x, y, z0):
    return m3d.Manifold.cylinder(h, af / math.sqrt(3), af / math.sqrt(3), 6, False).rotate((0, 0, 30)) \
        .translate((x, y, z0))


def _cyl_z(d, x, y, z0, z1, seg=32):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg, False).translate((x, y, z0))


_nA, _nB, _scr = [], [], []
GRP_H = 2 * P1.NUT_L
SCREW_HEAD_D, SCREW_HEAD_H = P1.M3_HEAD_D, P1.M3_HEAD_H   # 全部 M3 头 Φ7×3
TOP_CAP_T = 7.0
TRAY_BOT = LED_EDGE_BOT_Z - 5.0
for _sy in (1, -1):
    _y = _sy * P1.COL_Y
    for _gz in P1.GROUP_Z:
        _nA.append(_hex_z(P1.NUT_AF, P1.NUT_L, P1.COL_X, _y, _gz))             # 上颗焊 A
        _nB.append(_hex_z(P1.NUT_AF, P1.NUT_L, P1.COL_X, _y, _gz - P1.NUT_L))  # 下颗焊 B
    _tip = P1.GROUP_Z[0] - GRP_H / 2                                       # 上螺丝尖 = 上组底
    _scr.append(_cyl_z(3.0, P1.COL_X, _y, _tip, LED_EDGE_TOP_Z + TOP_CAP_T)
                + _cyl_z(SCREW_HEAD_D, P1.COL_X, _y, LED_EDGE_TOP_Z + TOP_CAP_T,
                         LED_EDGE_TOP_Z + TOP_CAP_T + SCREW_HEAD_H))
    _tip = P1.GROUP_Z[1] + GRP_H / 2 - 1.5                                 # 下螺丝尖 (中组顶下 1.5)
    _scr.append(_cyl_z(3.0, P1.COL_X, _y, TRAY_BOT, _tip)
                + _cyl_z(SCREW_HEAD_D, P1.COL_X, _y, TRAY_BOT - SCREW_HEAD_H, TRAY_BOT))
SCREW_TOP_L = LED_EDGE_TOP_Z + TOP_CAP_T - (P1.GROUP_Z[0] - GRP_H / 2)
SCREW_BOT_L = (P1.GROUP_Z[1] + GRP_H / 2 - 1.5) - TRAY_BOT
_u = lambda ms: mesh_tris(m3d.Manifold.batch_boolean(ms, m3d.OpType.Add))
parts.append(("hex nut M3 ×6 soldered A (上颗)", _u(_nA)))
parts.append(("hex nut M3 ×6 soldered B (下颗)", _u(_nB)))
parts.append((f"screen screw M3 ×4 (上 {SCREW_TOP_L:.0f} / 下 {SCREW_BOT_L:.0f})", _u(_scr)))
_foot = read_stl(V10 / "models/screen_foot_v1_0/screen_foot_v1_0_posY_asm.stl")
parts.append(("screen_foot_v1_0 +Y", _foot))
parts.append(("screen_foot_v1_0 -Y", read_stl(V10 / "models/screen_foot_v1_0/screen_foot_v1_0_negY_asm.stl")))
parts.append(("top_cap_v1_0", read_stl(V10 / "models/top_cap_v1_0/top_cap_v1_0_asm.stl")))
# DR1M90 固定 (2026-10-20 用户: 同旧 pi2hub): rim_ring 通孔 + 唇侧 Φ4.2 铜螺母, M3 尼龙垫柱 5 (M-F) 公头拧进
# 铜螺母撑住底板; 上面 wifi 托板的 25 尼龙柱公头穿底板贴片铜柱拧进这根垫柱的母头, 把底板夹住
_bs = []
for _bx, _by in P1.BASE_HOLES_BOARD:
    _wx, _wy = (Rb @ np.array([_bx, _by, 0.0]))[:2]
    _bs.append(m3d.Manifold.cylinder(BASE_SPACER, 5.5 / math.sqrt(3), 5.5 / math.sqrt(3), 6, False)
               .translate((_wx, _wy, DISC_TOP)))
parts.append((f"nylon standoff M3x{BASE_SPACER:g} ×4 (DR1M90)", _u(_bs)))
# 屏幕底座 → 转子: 4× M3 (Φ7 头) 从脚垫顶面穿 rim_ring 外圈环孔, 拧进 hub_disc 底面铜螺母 (Z 31.7..36.2)
FOOT_SCREW_L = 14.0
_fs = []
for _fx, _fy in __import__("screen_foot_v1_0.build_stl", fromlist=["x"]).FOOT_HOLES_WORLD:
    _pt = DISC_TOP + 5.0
    _fs.append(_cyl_z(3.0, _fx, _fy, _pt - FOOT_SCREW_L, _pt) + _cyl_z(SCREW_HEAD_D, _fx, _fy, _pt, _pt + SCREW_HEAD_H))
parts.append((f"foot screw M3x{FOOT_SCREW_L:g} ×4 (→ hub 铜螺母)", _u(_fs)))
FOOT_SCREW_ENGAGE = (DISC_TOP + 5.0 - FOOT_SCREW_L) - ROTOR_Z0
# 螺母 ↔ 两块灯板 贴面 (应为 0 干涉): 灯板背面平面在 X = SCR_ECC ± BACK_GAP/2
_nut_all = m3d.Manifold.batch_boolean(_nA + _nB, m3d.OpType.Add)
_bb = _nut_all.bounding_box()
assert abs(_bb[0] - (SCR_ECC - BACK_GAP / 2)) < 1e-6 and abs(_bb[3] - (SCR_ECC + BACK_GAP / 2)) < 1e-6

# ===================== 3b. FPC 排线 ×2 (桥板 FPC2 ↔ 底板 FPC1/FPC2) =====================
# 两头都是 XW0525512-702R-001 (0.5 mm 70+2P 翻盖下接)。插口朝向: 两块板上该座的 3D 模型同一
# 形状, 高 4.13 的那条边都朝向最近的板边 —— 判为**插口朝板边** (座子摆板边, 线往板外出):
#   桥板: 插口朝桥板下沿 → FPC 从桥板下沿竖直往下出
#   底板: 插口朝底板外边 → FPC 从底板外侧 (|X|>40) 反向插入
# 走线 (在 Y = 座中心的竖直面内, 都是 90° 弯): 桥板口 ↓ → 横向越过 FS03/RJ45 往外 → 底板外侧 ↓
#   → 反向水平插入底板座。另算「插口朝内」时的长度作对照。
FPC_W = 36.0          # 70+2P @0.5 估宽
FPC_T = 0.3           # 0.19 本体 (+两端补强 0.2), 只用于显示
FPC_R = 1.5           # 弯折中心线半径
FPC_SLOT = 0.9        # 插槽中心高出板面
FPC_IN = 1.0          # 线端离座子后壁
FPC_CLR = 1.0         # 线与下方器件最小间隙
FPC_SLACK = 10.0      # 余量 (装配先插一头 + 高度公差 + 弯折不压死)
FPC_ORDER = 115.0     # 2026-10-16 用户定: 两根统一下料 115 (面 B 103.3+余量决定)
BR_FPC = dict(x=31.15, y_front=13.84, y_rear=21.09)                 # 桥板系
BASE_FPC_LOC = {+1: dict(x=-34.76, y_front=-39.86, y_rear=-32.61),   # 底板系, 配面 A
                -1: dict(x=34.76, y_front=39.86, y_rear=32.61)}      # 配面 B


def _br_pt(face, y):
    p = np.array([[[BR_FPC["x"], y, 1.59 + FPC_SLOT]] * 3])
    return led_to_world(bridge_to_led(p), face, Z_AREA_BOT)[0, 0]


def _base_pt(face, y):
    c = BASE_FPC_LOC[face]
    return Rb @ np.array([c["x"], y, 1.59 + FPC_SLOT]) + np.array([0, 0, BASE_Z0])


def fillet_path(corners, r, step=0.25):
    """折线 (u,z) 各拐角倒圆 r → (采样点, 长度)。"""
    pts, L = [np.asarray(corners[0], float)], 0.0
    for i in range(1, len(corners) - 1):
        a, b, c = (np.asarray(corners[k], float) for k in (i - 1, i, i + 1))
        d1, d2 = (b - a) / np.linalg.norm(b - a), (c - b) / np.linalg.norm(c - b)
        t1, t2 = b - d1 * r, b + d2 * r
        L += np.linalg.norm(t1 - pts[-1]); pts.append(t1)
        ctr = t1 + r * (d2 - d1 * np.dot(d1, d2)) / np.linalg.norm(d2 - d1 * np.dot(d1, d2))
        a0, a1 = (math.atan2(*(q - ctr)[::-1]) for q in (t1, t2))
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(1, 9):
            ang = a0 + da * k / 8
            pts.append(ctr + r * np.array([math.cos(ang), math.sin(ang)]))
        L += abs(da) * r
    L += np.linalg.norm(np.asarray(corners[-1], float) - pts[-1]); pts.append(np.asarray(corners[-1], float))
    return np.array(pts), L


def strip_tris(pts_uz, sgn, yc, w, t):
    """中心线 (u,z) → 世界 X = sgn*u 的扁带三角形。"""
    tris = []
    n = len(pts_uz)
    tang = np.gradient(pts_uz, axis=0)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    rails = []
    for off_n, off_y in ((-t/2, -w/2), (t/2, -w/2), (t/2, w/2), (-t/2, w/2)):
        uz = pts_uz + nrm * off_n
        rails.append(np.stack([sgn * uz[:, 0], np.full(n, yc + off_y), uz[:, 1]], 1))
    for k in range(4):
        r0, r1 = rails[k], rails[(k + 1) % 4]
        for i in range(n - 1):
            tris += [[r0[i], r0[i + 1], r1[i + 1]], [r0[i], r1[i + 1], r1[i]]]
    return np.array(tris)


FPC_REPORT = []
for face, tag in ((+1, "A"), (-1, "B")):
    bf, brr = _br_pt(face, BR_FPC["y_front"]), _br_pt(face, BR_FPC["y_rear"])
    pf, prr = _base_pt(face, BASE_FPC_LOC[face]["y_front"]), _base_pt(face, BASE_FPC_LOC[face]["y_rear"])
    sgn = 1.0 if bf[0] > 0 else -1.0
    yc = float(bf[1])
    assert abs(yc - pf[1]) < 0.05, "桥板与底板 FPC 座不在同一 Y"
    u_b = sgn * bf[0]
    z_end_b = brr[2] - FPC_IN * np.sign(brr[2] - bf[2])          # 线端: 后壁往口内 1.0
    z_front_b = bf[2]
    u_base_front, u_base_rear = sgn * pf[0], sgn * prr[0]
    z_base = pf[2]
    base_edge_u = 40.0                                           # 底板半宽 (转 90° 后在 X)
    u_out = max(u_base_front, base_edge_u) + FPC_CLR + FPC_R
    u_end = u_base_rear + FPC_IN * np.sign(u_base_front - u_base_rear)
    xr = sorted((sgn * u_b, sgn * u_out))
    obst = top_under((xr[0], xr[1]), (yc - FPC_W / 2, yc + FPC_W / 2))
    z_lo = obst + FPC_CLR + FPC_T / 2
    z_hi = z_front_b - FPC_R
    z_h = (z_lo + z_hi) / 2 if z_lo <= z_hi else z_lo
    corners = [(u_b, z_end_b), (u_b, z_h), (u_out, z_h), (u_out, z_base), (u_end, z_base)]
    path, L = fillet_path(corners, FPC_R)
    # 对照: 底板插口朝内 (FPC 从 FS03 边与座子之间落下, 正向插入)
    u_end_in = u_base_front - FPC_IN * np.sign(u_base_front - u_base_rear)
    L_in = (z_end_b - z_base) + (u_end_in - u_b) - 3 * (2 - math.pi / 2) * FPC_R
    parts.append((f"FPC {tag}", strip_tris(path, sgn, yc, FPC_W, FPC_T)))
    FPC_REPORT.append((tag, L, L_in, obst, z_lo, z_hi, z_h, u_b, u_out, yc))

# ===================== 4. 顶部: 2026-10-21 拆立柱 (frame_A/B / 688 / Φ8 螺柱 / 挡光滑片一起拆) =====================
# 顶部固定方式待定。顶盖 (含光电模块座) 与光电模块随转子留着。
CAP_TOP = LED_EDGE_TOP_Z + TOP_CAP_T
from top_cap_v1_0.build_stl import SEN_M, SEN_TH  # noqa: E402
sm = read_stl(MODELS / "photo_sensor/sensor_module.stl")
sm = sm[..., [1, 0, 2]] * np.array([1.0, -1.0, 1.0])   # rotZ-90: (x,y)->(y,-x) (同 V0.4)
sm = sm + np.array([-3.0 + SEN_M[0], SEN_M[1], CAP_TOP])
_th = math.radians(SEN_TH)
_R2 = np.array([[math.cos(_th), -math.sin(_th)], [math.sin(_th), math.cos(_th)]])
sm[..., :2] = (sm[..., :2] - np.array(SEN_M)) @ _R2.T + np.array(SEN_M)
parts.append(("sensor_module", sm))
SEN_FORK_TOP = float(sm[..., 2].max())
TOP_Z = SEN_FORK_TOP                          # 整机最高点 (预览用)

GLASS_TOP = GS.GLASS_Z0 + GS.GLASS_H
assert GLASS_TOP - TOP_Z >= 100.0 - 1e-6, f"玻璃只比最高件高 {GLASS_TOP - TOP_Z:.2f}"
parts.append((f"glass tube OD{GS.GLASS_OD:g}x{GS.GLASS_T:g}x{GS.GLASS_H:g}", mesh_tris((
    m3d.Manifold.cylinder(GS.GLASS_H, GS.GLASS_OD / 2, GS.GLASS_OD / 2, 256, False)
    - m3d.Manifold.cylinder(GS.GLASS_H + 2, GS.GLASS_IR, GS.GLASS_IR, 256, False).translate((0, 0, -1)))
    .translate((0, 0, GS.GLASS_Z0)))))

# ===================== 5. 报告 =====================
ROTOR = [n for n, _ in parts if n.startswith(("LED", "bridge", "ACG525", "DR1M90", "FS03", "wifi", "FPC",
                                               "hex nut", "screen", "top_cap", "standoff"))]
print(f"★ 桥板翻面: {'绕 Y (X 镜像, 桥CN1→灯板CN2)' if BRIDGE_MIRROR_X else '绕 X (CN1↔CN1)'}")
print(f"底板: 转 {BASE_ROT:g}° (FPC 对位残差 {best[1]:.2f} mm), 底面 {BASE_Z0:.1f}, "
      f"FS03 板底 {FS03_Z0:.2f}, FS03 顶 (RJ45/USB 实测 15.4) {FS03_TOP:.2f}")
print(f"WiFi 托板: 尼龙柱 M3×{NYLON_L:g} ×4 @ {[(round(x, 1), round(y, 1)) for x, y in PLATE_HOLES]}, "
      f"板 {SHELF_Z0:.2f}..{SHELF_TOP:.2f} (离 RJ45 顶 {SHELF_CLR:.2f}); AF 母头末端 Y {WIFI_AF_END_Y:.2f}; "
      f"J6 顶 → AF 底 {SHELF_TOP + 7.25 - 10.3 / 2 - 75.29 - (BASE_Z0 - 47.2):.2f} 给 AMRI 弯头")
print(f"WiFi: 托板 {SHELF_Z0:.2f}..{SHELF_TOP:.2f} (下方最高 {SHELF_Z0-SHELF_CLR:.2f}), 罩顶 {WIFI_TOP:.2f}, "
      f"模块+线缆头最大半径 {WIFI_RMAX:.2f}")
print(f"模组 X 包络 ±{MOD_X:.2f}; 其下电路最高 {STACK_TOP:.2f} → 灯板下沿 {LED_EDGE_BOT_Z:.2f} "
      f"(余 {CLEAR:.2f})")
print(f"LED 区 {Z_AREA_BOT:.2f}..{LED_AREA_TOP_Z:.2f} (V0.4: 92.20..260.95, 抬高 {Z_AREA_BOT-92.2:+.2f}); "
      f"灯板上沿 {LED_EDGE_TOP_Z:.2f}")
print(f"LED 面 X = {SCR_ECC-BACK_GAP/2-LED_T:+.2f} (面B) / {SCR_ECC+BACK_GAP/2+LED_T:+.2f} (面A) "
      f"[{'偏心 SCR_ECC=%.2f' % SCR_ECC if SCR_ECC else '居中'}] (+LED 本体, STEP 无); 背靠背间距 {BACK_GAP:.2f} (= 六角铜螺母对边)")
print(f"底板: Φ{BB_D:g}×{BB_T:g} 圆网格板, M6 网格 {BB_NHOLE} 孔 + 4-Φ{BB_MOUNT_D:g} 沉孔 {BB_MOUNT}; 立柱已拆")
for tag, L, L_in, obst, z_lo, z_hi, z_h, u_b, u_out, yc in FPC_REPORT:
    order = math.ceil((L + FPC_SLACK) / 5.0) * 5.0
    print(f"FPC {tag} (Y={yc:+.1f}): 路径下方最高 {obst:.2f} → 横跨高度可用 {z_lo:.2f}..{z_hi:.2f} "
          f"({'✓' if z_lo <= z_hi else '✗ 不够'} 余 {z_hi-z_lo:.2f}), 取 {z_h:.2f}; 外折点 |X| {u_out:.1f}")
    print(f"   面{tag} 线端到线端 {L:.1f} mm (插口朝外, 默认) / 若底板插口朝内 {L_in:.1f}; "
          f"+余量 {FPC_SLACK:g} → 至少 {order:.0f}; 统一下料 {FPC_ORDER:.0f} ⇒ 实际余量 {FPC_ORDER-L:.1f}")
    assert FPC_ORDER >= order, f"FPC {tag} 统一长度 {FPC_ORDER} 不够"
# ---- 屏幕组件 / 底座 干涉粗查: 别的转子件顶点落进底座外包盒 (底座本身是缺口形, 只当提示) ----
print(f"屏幕锁紧: 螺母组中心 Z {', '.join(f'{z:.2f}' for z in P1.GROUP_Z)}; 上螺丝 M3 杆 {SCREW_TOP_L:.1f} "
      f"(顶盖 {TOP_CAP_T:g} + 上组) / 下螺丝 M3 杆 {SCREW_BOT_L:.1f} (顶托 5 + 下组 + 空段 + 中组)")
print(f"底座: M3×{FOOT_SCREW_L:g} 借外圈环孔, 尖在 hub 底面上 {FOOT_SCREW_ENGAGE:.1f} (铜螺母 4.5 深 ⇒ 吃进 "
      f"{4.5 - FOOT_SCREW_ENGAGE:.1f})")
print(f"透明罩 (亚克力/PC): OD{GS.GLASS_OD:g} ID{GS.GLASS_IR * 2:g} 高 {GS.GLASS_H:g}, Z {GS.GLASS_Z0:g}..{GLASS_TOP:g} "
      f"(比最高件 {TOP_Z:.2f} 高 {GLASS_TOP - TOP_Z:.2f}); 最小需要高 {TOP_Z + 100 - GS.GLASS_Z0:.1f}")
_rk = [(n, float(np.hypot(*t.reshape(-1, 3)[:, :2].T).max())) for n, t in parts
       if not n.startswith(("grid", "glass", "base PCB"))]
_rn, _rr = max(_rk, key=lambda x: x[1])
print(f"   罩内壁 R{GS.GLASS_IR:g} ↔ 最外件 {_rn} R{_rr:.2f}: 径向余 {GS.GLASS_IR - _rr:.2f}")
print(f"底板 PCB: {GS.PCB_W:g}×{GS.PCB_L:g}, Y {GS.PCB_Y0:.2f}..{GS.PCB_Y1:.2f}, 板 Z {GS.PCB_Z0:g}..{GS.PCB_Z0 + GS.PCB_T:g}, "
      f"元件限高 {GS.PCB_COMP_H:.1f} (上方定子法兰底 Z15.5)")
print(f"顶部: 顶盖 {LED_EDGE_TOP_Z:.2f}..{CAP_TOP:.2f}, 光电模块叉顶 {SEN_FORK_TOP:.2f} = 整机最高 (无立柱/轴承架)")
_fv = _foot.reshape(-1, 3)
_flo, _fhi = _fv.min(0), _fv.max(0)
for name, t in parts:
    if name.startswith(("screen_foot", "screen screw", "hex nut", "rim_ring", "LED board", "foot screw")):
        continue
    for sgn in (1, -1):
        lo = np.array([_flo[0], sgn * _flo[1] if sgn > 0 else -_fhi[1], _flo[2]]) + 0.01
        hi = np.array([_fhi[0], _fhi[1] if sgn > 0 else -_flo[1], _fhi[2]]) - 0.01
        v = t.reshape(-1, 3)
        k = np.all((v >= lo) & (v <= hi), axis=1)
        if k.any():
            print(f"  ⚠ {name} 有 {k.sum()} 个顶点在 {'+Y' if sgn > 0 else '-Y'} 底座外包盒内")
rmax = 0.0
for name, t in parts:
    if name in ROTOR:
        v = t.reshape(-1, 3)
        r = float(np.hypot(v[:, 0], v[:, 1]).max())
        rmax = max(rmax, r)
        print(f"  {name:32s} X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}"
              f"  Z {v[:,2].min():7.2f}..{v[:,2].max():7.2f}  r_max {r:6.2f}")
print(f"转子电路最大回转半径 {rmax:.2f} (盘缘 R90 / 底板 R{BB_D / 2:g})")
for face in (+1, -1):
    fb = fpc_world_bridge(face, Z_AREA_BOT)
    cand = [np.r_[Rb[:2, :2] @ np.array(c), BASE_Z0 + 4.13] for c in BASE_FPC]
    c = min(cand, key=lambda c: np.hypot(*(c[:2] - fb[:2])))
    print(f"  FPC 面{'A' if face > 0 else 'B'}: 桥 FPC2 ({fb[0]:.1f},{fb[1]:.1f},{fb[2]:.1f}) ↔ 底板 "
          f"({c[0]:.1f},{c[1]:.1f},{c[2]:.1f})  直线距 {np.linalg.norm(fb - c):.1f}")

# ===================== merge + export =====================
all_tris = np.concatenate([t for (_, t) in parts], axis=0).astype(np.float32)
out = ROOT / ("assembly_v1_1_xflip.stl" if not BRIDGE_MIRROR_X else "assembly_v1_1.stl")
rec = np.zeros(len(all_tris), dtype=STL_TRI)
rec["verts"] = all_tris
with out.open("wb") as f:
    f.write(b"POV3D assembly_v1_1".ljust(80, b" "))
    f.write(struct.pack("<I", len(all_tris)))
    f.write(rec.tobytes())
print(f"wrote {out}  ({len(all_tris)} triangles)")

# ===================== preview (大网格抽样) =====================
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
COL = {"grid": "#333333", "base": "#777777", "flange": "#88aacc", "mounting": "#cccc77", "motor": "#444444",
       "hub": "#ccaa55", "rim": "#9ccf9c", "DR1M90": "#2a7d2a", "FS03": "#e03020", "LED": "#3355cc",
       "bridge": "#1f9a6a", "ACG525": "#d9a400", "wifi_plate": "#bbbbbb", "nylon": "#f2f2e6", "wifi_shell": "#22aaaa", "wifi module": "#111111", "post": "#666666", "frame": "#5577aa", "FPC": "#e07b00",
       "hex nut": "#d4a017", "screen screw": "#202020", "screen_foot": "#ff7f2a", "top_cap": "#c05cd6",
       "M6": "#202020", "standoff": "#b0b0b0", "688": "#909090", "wifi shell screw": "#202020", "sensor": "#2060c0", "vane": "#e0e040", "foot screw": "#202020",
       "glass_seat": "#e8e8e8", "base PCB component": "#ffd0a0", "base PCB": "#2a7d2a", "glass tube": "#a0d8ef"}
MAXTRI = 60000
rng = np.random.default_rng(0)
fig = plt.figure(figsize=(16, 8))
views = [(18, -60, "iso"), (0, 0, "front (from +X)"), (0, -90, "side (from -Y)"), (89, -90, "top")]
for i, (elev, azim, title) in enumerate(views):
    ax = fig.add_subplot(1, 4, i + 1, projection="3d")
    for name, t in parts:
        if title == "top" and name.startswith("frame"):
            continue
        if len(t) > MAXTRI:   # 抽样: 优先保留大三角形
            ar = np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
            t = t[np.argsort(-ar)[:MAXTRI]]
        c = next((v for k, v in COL.items() if name.startswith(k)), "#222222")
        ax.add_collection3d(Poly3DCollection(t, facecolor=c, edgecolor="none",
                                             alpha=0.12 if name.startswith("glass tube") else 0.95))
    ax.set_xlim(-110, 110); ax.set_ylim(-110, 110); ax.set_zlim(-15, GLASS_TOP + 10)
    ax.set_box_aspect((1, 1, (GLASS_TOP + 25) / 220)); ax.view_init(elev=elev, azim=azim)
    ax.set_title(title); ax.set_xlabel("X"); ax.set_ylabel("Y")
fig.tight_layout()
png = out.with_name(out.stem + "_preview.png")
fig.savefig(png, dpi=100)
print(f"wrote {png}")

# ===================== 3MF (分零件 + 颜色, 给人看) =====================
import zipfile


def write_3mf(path, named_parts):
    def hexcol(name):
        c = next((v for k, v in COL.items() if name.startswith(k)), "#888888")
        return c.upper() + ("40" if name.startswith("glass tube") else "FF")   # 玻璃半透明
    names = [n for n, _ in named_parts]
    mats = "".join(f'<base name="{n}" displaycolor="{hexcol(n)}"/>' for n in names)
    objs, items = [], []
    for i, (name, t) in enumerate(named_parts):
        v, idx = np.unique(np.round(t.reshape(-1, 3), 4), axis=0, return_inverse=True)
        tri = idx.reshape(-1, 3)
        tri = tri[(tri[:, 0] != tri[:, 1]) & (tri[:, 1] != tri[:, 2]) & (tri[:, 0] != tri[:, 2])]
        vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in v)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tri)
        oid = i + 2
        objs.append(f'<object id="{oid}" name="{name}" type="model" pid="1" pindex="{i}">'
                    f'<mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{oid}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><basematerials id="1">{mats}</basematerials>{"".join(objs)}</resources>'
             f'<build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
                   'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.'
                   'org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)


p3 = out.with_suffix(".3mf")
write_3mf(p3, parts)
print(f"wrote {p3}  ({p3.stat().st_size/1e6:.1f} MB, {len(parts)} 个零件)")
# F3D 等查看器不认 3MF 的单件透明度 ⇒ 另出一份不带玻璃的, 看里面用
p3n = out.with_name(out.stem + "_noglass.3mf")
write_3mf(p3n, [(n, t) for n, t in parts if not n.startswith("glass tube")])
print(f"wrote {p3n}")
