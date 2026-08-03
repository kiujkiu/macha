"""
rotor_shroud_v3 — 转子电路罩 (2026-07-27, 用户: "增加罩子, 把屏幕以下电路部分
遮盖住, 下面锁到转子的件上面, 整体看起来要是一个圆柱的样子")。

用户定档 (2026-07-27 四问):
  · 直径  = Φ170 齐盘缘 (外壁与 rim_ring OD 完全齐平, ID164/壁 3)
  · 分件  = 两半对开 (维护时可单独掀开一半)
  · 顶部  = 封顶带屏缝 (3 厚顶板, 中央开缝让双面屏穿出)
  · 筒壁  = 全封闭 (只保留几何上无法回避的让位/出线口)
  · 壁厚 3, "需要加强的地方加强"

几何 (零件系 = 屏局部系; 装配 = rot_z(part, ROTOR_ROT + V3_SCR_ROT) + Z DISC_TOP):
  Z 0..50 = 承载面 42.2 .. 屏底 92.2 —— 正好罩住 pi2hub(5..15.1) / 尼龙柱 /
  米联派(6.9..17.9) / wifi_shell(0..18.1) / 两个 portal_tee 的腿。
  · 筒壁  R82..85, Z 0..50
  · 顶板  R0..82, Z 47..50, 减屏缝
  · 屏缝  |X|≤7.0 (|Y|≤59.6) → |X|≤10.3 (59.6..78.0, 让 T 件梯形顶托 20 宽);
          |Y|>78.0 顶板做实 = 缝的两端封口 (T 件外面 76.6, 留 1.4)
  · 固定  4× 立柱 Φ10 @ r77.5, 零件系 22.5/157.5/202.5/337.5° (每半 2 根),
          Z 0..47 与筒壁融合 (兼竖向加强筋), Φ3.4 通孔, 顶部 Φ14 凸台 Z43..50
          + Φ6.5×5.5 沉孔 → M3×55 内六角从顶板往下, 穿 rim_ring 托盘 5 +
          hub 5.5 拧进 hub 底既有铜花螺母 (= 借用 4 个空闲环孔, rim_ring 不改)
  · 加强  ① 4 根立柱本身 = 竖筋; ② 接缝两端 bolster (内壁局部加厚到 ID152,
          |Y|≤4, Z0..47) —— 对开面加大 + 自由边加劲; ③ 屏缝两侧下翻边
          (X ±7..10, Z41..47, |Y|≤58) —— 顶板最长自由边加劲, 兼装屏导向
  · 让位  由「障碍件膨胀后布尔减」自动生成, 见 RELIEF 段

打印: 绕 X 翻 180° (顶板贴床) —— 筒壁竖直、立柱/筋/凸台全部朝上, 零支撑。
      占地 170×85, 高 50。
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

HERE = Path(__file__).parent
P31 = HERE.parent.parent                   # pov3d/v3.1
V3 = P31.parent / "v3"                     # 沿用的 v3 件
MODELS = P31.parent / "models"              # 共享零件库
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])

# ===== 参数 =====
OD, ID = 170.0, 164.0                      # 外径 = rim_ring OD (齐盘缘); 壁 3
R_OUT, R_IN = OD / 2, ID / 2               # 85.0 / 82.0
WALL = R_OUT - R_IN                        # 3.0
H = 50.0                                   # 承载面 42.2 → 屏底 92.2
PLATE_T = 2.0                              # 2026-07-27 用户"减": 顶板 3→2 减重 (屏缝下翻边自动变 7 深补刚度)
PLATE_Z0 = H - PLATE_T                     # 47.0

DISC_TOP = 42.2                            # 装配 Z 基准 (承载面)
V3_SCR_ROT = -45.0                         # 屏组整体角 (罩子随屏组)

# 屏缝 (双面屏模组 13.4 厚 × 150 宽, 居中; T 件梯形顶托外端 20 宽 @ Y76.6)
# ===== v3.1 偏心屏 (2026-07-30) =====
# 屏整体偏移 +6.7 让一面贴轴 → 屏占 X 0..13.4 (原 ±6.7)。屏缝做成**同时覆盖
# 居中与偏心两种落位** (X -7.0 .. +13.7), 与 portal_tee_v3_1 的 3 个离散孔配套,
# 拧不同孔即可切换, 罩子不用重印。
# ⚠ 快照布尔查不出缝宽不够 —— 屏底 92.2 恰好等于顶板顶面, 两者只相切;
#   冲突只在「罩子往下套过屏」的过程中出现, 必须按屏实际落位定缝宽 (或跑安装模拟)。
SCR_ECC = 6.7                              # 偏心量
SCR_X0 = -7.0                              # 缝内侧 (居中装法时的 -6.7 - 0.3)
SCR_X1 = SCR_ECC + 6.7 + 0.3               # 13.7 缝外侧 (偏心装法时的屏外面 + 0.3)
SCR_HW = 7.0                               # (保留: 旧对称半宽, 仅用于翻边定位)
TEE_HW = 16.3                              # v3.1: T 顶托加宽到 ±16 → +0.3
TEE_Y0 = 59.6                              # T 顶托内端 (= 屏缝加宽起点)
SLOT_Y1 = 78.0                             # 屏缝末端 (T 件外面 76.6 + 1.4); 之外顶板做实

# 固定立柱 = 上下贯通「沉井」(2026-07-27 用户改法: "让螺丝没有这么长, 螺丝头部
# 直径 7.5, 只要螺丝这个位置沉下去就行")。
# 先前方案是 Φ3.4 细孔 + M3×55 长螺丝从顶板一路穿下去 —— 螺丝难买, 且 55mm
# 拧紧力矩全压在 47mm 的 PLA 柱上。改成: 立柱中间掏 Φ9 大井直通顶板, 短螺丝
# 坐井底 3 厚台肩上, 头 (Φ7.5) 沉在井里不露头, 长螺丝刀顺井下去拧。
COL_R = 77.5                               # = rim_ring OUTER_PCD_R (借空闲环孔)
COL_ANG = (22.5, 157.5, 202.5, 337.5)      # 零件系 (= 装配系 + 45°)
COL_D = 14.0                               # 立柱外径 (r 70.5..84.5, 与筒壁融合)
COL_TOP = H                                # 立柱到顶 (与顶板融合), 井口开在顶板上
WELL_D = 9.0                               # 沉井内径 (螺丝头 Φ7.5 + 1.5 落料间隙)
FLOOR_T = 3.0                              # 井底台肩厚 (螺丝头压在这上面)
BORE_D = 3.4                               # 台肩上的 M3 过孔 (Z 0..FLOOR_T)
# 螺丝长度核算 (装配系): 头底坐井底台肩顶面 = 42.2+3 = 45.2;
#   台肩 3 + rim_ring 托盘 5 + hub 实体 1 → 36.2 = hub 底铜花螺母顶;
#   铜花螺母 31.7..36.2 (从 hub 底压入)。 ⇒ **M3×12**: 杆到 33.2, 旋入 3.0 ✓
#   (M3×14 到 31.2 会探出 hub 底 0.5 顶到电机端面 ✗)

# ===== 配重座 (2026-08-03 用户: "shroud_half 这两个件增加一个螺丝孔, 我们装一个
# 配重, 用 M6 螺丝来做") =====
# 为什么放罩子上: 转子盘被罩子盖住够不着, 且 rim_ring R77.5 那圈 8 个孔已全被占
# (4 沉井立柱 22.5+90k° + 4 个 T 脚 67.5+90k°) —— 罩顶板是唯一还能拿到大力臂的地方。
# 角向 135° / 225° (每半一个): 各距最近占位 22.5° (r75 弦距 29.3 > 凸台+立柱 14) ✓,
#   避开屏缝 (沿 ±Y)、bolster (|Y|≤4)、wifi 让位 (≈180°)。
#   **两个对称跨 180°**: 等质量时合矢量正好指向 −X = v3.1 偏心屏 (+X 偏 6.7) 要修正的
#   方向, 幅值 2·m·r·cos45° = 1.414·m·r; 两边配不等质量还能在 135..225° 之间调方向。
#   (正对布置 45°/225° 只能沿一条轴, 且做不出 180° 方向, 已否。)
# 结构: 顶板下挂 Φ14 凸台 (r 68..82, 外缘正好并到内壁 R82 融合), Z38..50 共 12 厚;
#   Φ6.5 M6 过孔上下通; 凸台自由端 (Z38) 开对边 10.3 六角螺母窝深 5.5 —— **装半罩前
#   从里面把 M6 螺母塞进去卡住**, 之后螺丝一律从罩外顶面往下拧, 罩装好也能加减配重。
# 打印: 打印姿态是绕 X 翻 180° 顶板贴床 ⇒ 凸台朝上、六角窝朝上开口, 零支撑 ✓。
CW_ENABLE = True
CW_R = 75.0                                # 力臂 (凸台外缘 82 = 内壁, 融合)
CW_ANG = (135.0, 225.0)                    # 零件系; A 半 135°, B 半 225°
CW_BOSS_D = 14.0
CW_BOSS_Z0 = 38.0                          # 凸台底 (顶板下表面 48 往下 10)
CW_HOLE_D = 6.5                            # M6 过孔
CW_NUT_AF = 10.3                           # M6 螺母对边 10 + 0.3
CW_NUT_H = 5.5                             # 螺母窝深 (螺母 5 + 0.5)

# 加强
BOL_R_IN = 76.0                            # 接缝 bolster 内径 (壁局部 9 厚)
BOL_HW = 4.0                               # bolster 半宽 (|Y| ≤ 4)
LIP_T, LIP_Z0 = 3.0, 41.0                  # 屏缝下翻边 3 厚, Z41..47 (6 深)
LIP_Y = 58.0                               # 翻边 |Y| ≤ 58 (避开 T 顶托 59.6)

# 让位间隙: 障碍件全是与罩子同步共转的转子件 (无相对运动), 只需覆盖打印公差,
# 0.4 足够。2026-07-27 从 0.6 收到 0.4 —— 0.6 时 157.5° 立柱的沉井内壁被 wifi 壳
# 让位窝啃出 ~6mm³ 破口 (井壁最内 0.5mm 环只剩 99.1% 实心); 顺带把 T 脚角处的
# 外皮从 0.79 提到 0.99。
RELIEF_CLR = 0.4
SWEEP_DOWN = 14.0        # 让位体向下扫掠深度 (覆盖最高的悬空障碍: 线缆头顶 Z10.05)
SEG = 360                                  # 圆柱分段
SEAM_GAP = 0.15                            # 对开面单边间隙 (两半合计 0.3)


def read_stl(p):
    raw = p.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    return np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64)


def to_manifold(tris):
    """STL 三角汤 → Manifold: 必须先按坐标合并顶点, 否则是 0 体积非流形;
    再按体积正负修绕向 (本项目有「翻绕向导出」的 STL, 见 v3 check 教训)。"""
    v = tris.reshape(-1, 3)
    uniq, inv = np.unique(np.round(v, 4), axis=0, return_inverse=True)
    idx = inv.astype(np.uint32).reshape(-1, 3)
    man = m3d.Manifold(m3d.Mesh(vert_properties=uniq.astype(np.float32), tri_verts=idx))
    if man.volume() < 0:
        man = m3d.Manifold(m3d.Mesh(vert_properties=uniq.astype(np.float32),
                                    tri_verts=idx[:, ::-1].copy()))
    return man


def rot_z(a, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x = a[..., 0].copy(); y = a[..., 1].copy()
    a[..., 0] = c * x - s * y
    a[..., 1] = s * x + c * y
    return a


def cyl(h, r, z0=0.0, seg=SEG):
    return m3d.Manifold.cylinder(h, r, r, seg, False).translate((0.0, 0.0, z0))


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def dilate(man, c):
    """粗膨胀: 原件 ∪ 6 个轴向平移副本 —— 盒状障碍件够用 (轴向 c, 对角 ~0.7c)。"""
    out = man
    for d in ((c, 0, 0), (-c, 0, 0), (0, c, 0), (0, -c, 0), (0, 0, c), (0, 0, -c)):
        out = out + man.translate(d)
    return out


def sweep_down(man, depth=SWEEP_DOWN):
    """向下扫掠 (倍增法, log 次并集, 各步连续无缝)。

    2026-07-27 安装模拟发现: 只按最终位置让位, 罩子就装不下去 —— 半 B 在最后
    9.5mm 下落时撞 usb_wifi 线缆头 (线缆悬在 Z4.45..10.05, 出口窗只在最终位对齐,
    窗上方的筒壁会砸在线缆上, 61.8 mm³)。让所有障碍件的让位体连同「从该位置一路
    向下」的扫掠体一起减掉, 悬空特征的窗就自动变成通到底边的槽, 罩子可竖直落下。
    绝大多数障碍件本来就落到 Z0, 扫掠对它们是空操作; 实际只有线缆头受影响。
    """
    s, d = man, 0.25
    while d < depth:
        s = s + s.translate((0.0, 0.0, -d))
        d *= 2.0
    return s


# ===================== 1) 罩体 (未分半) =====================
body = cyl(H, R_OUT) - cyl(H + 2.0, R_IN, -1.0)                    # 筒壁 R82..85
body += cyl(PLATE_T, R_IN, PLATE_Z0)                               # 顶板 (整圆, 后挖缝)

# 固定立柱 ×4 (兼竖筋), 到顶与顶板融合
for a in COL_ANG:
    cx, cy = COL_R * math.cos(math.radians(a)), COL_R * math.sin(math.radians(a))
    body += cyl(COL_TOP, COL_D / 2, 0.0, 64).translate((cx, cy, 0.0))

# 接缝 bolster ×2 (对开面加厚 + 自由边加劲)
body += ((cyl(COL_TOP, R_IN + 0.5) - cyl(COL_TOP + 2.0, BOL_R_IN, -1.0))
         ^ box(-R_OUT, R_OUT, -BOL_HW, BOL_HW, 0.0, COL_TOP))

# 配重座凸台 ×2 (每半一个), 顶板下挂, 外缘并到内壁
def _cw_xy(a):
    return CW_R * math.cos(math.radians(a)), CW_R * math.sin(math.radians(a))


if CW_ENABLE:
    for a in CW_ANG:
        cx, cy = _cw_xy(a)
        body += cyl(H - CW_BOSS_Z0, CW_BOSS_D / 2, CW_BOSS_Z0, 64).translate((cx, cy, 0.0))

# 屏缝下翻边 ×2 (顶板最长自由边加劲, 兼装屏导向)
# 屏缝下翻边 ×2: 贴在新缝 (SCR_X0 .. SCR_X1) 的两侧外面
body += box(SCR_X1, SCR_X1 + LIP_T, -LIP_Y, LIP_Y, LIP_Z0, PLATE_Z0)
body += box(SCR_X0 - LIP_T, SCR_X0, -LIP_Y, LIP_Y, LIP_Z0, PLATE_Z0)

# 屏缝 (顶板 + 翻边一起切穿)
slot = box(SCR_X0, SCR_X1, -SLOT_Y1, SLOT_Y1, LIP_Z0 - 1.0, H + 1.0)
slot += box(-TEE_HW, TEE_HW, TEE_Y0, SLOT_Y1, LIP_Z0 - 1.0, H + 1.0)
slot += box(-TEE_HW, TEE_HW, -SLOT_Y1, -TEE_Y0, LIP_Z0 - 1.0, H + 1.0)
body -= slot

# 沉井 Φ9 (井底台肩 Z0..3) + 台肩上的 Φ3.4 过孔 + 引导锥
# 引导锥 (2026-07-27): 头 Φ7.5 在 Φ9 井里横向游隙 ±0.75, 螺丝落到井底时杆尖
# 最多偏离过孔 0.75 → 会杵在台肩上不进孔 (井深 47, 掏不出来)。孔口加 45° 锥
# Φ3.4→Φ5.0 (Z2.2..3.0): 捕捉半径 (5−3)/2 = 1.0 > 0.75 ✓; 头仍压在 Φ5..Φ7.5
# 的环面上 (承压环宽 1.25), 不落进锥里。
LEAD_D, LEAD_H = 5.0, 0.8
for a in COL_ANG:
    cx, cy = COL_R * math.cos(math.radians(a)), COL_R * math.sin(math.radians(a))
    body -= cyl(H - FLOOR_T + 1.0, WELL_D / 2, FLOOR_T, 64).translate((cx, cy, 0.0))
    body -= cyl(FLOOR_T + 2.0, BORE_D / 2, -1.0, 48).translate((cx, cy, 0.0))
    body -= (m3d.Manifold.cylinder(LEAD_H, BORE_D / 2, LEAD_D / 2, 48, False)
             .translate((cx, cy, FLOOR_T - LEAD_H)))

# 配重座: Φ6.5 M6 过孔上下通 + 凸台自由端六角螺母窝 (对边 10.3 × 深 5.5)
if CW_ENABLE:
    def hexprism(af, h, z0):
        r = af / math.sqrt(3.0)            # 对边 af → 外接圆半径
        return m3d.Manifold.cylinder(h, r, r, 6, False).rotate((0, 0, 30)).translate((0, 0, z0))

    for a in CW_ANG:
        cx, cy = _cw_xy(a)
        body -= cyl(H - CW_BOSS_Z0 + 3.0, CW_HOLE_D / 2, CW_BOSS_Z0 - 1.0, 48).translate((cx, cy, 0.0))
        body -= hexprism(CW_NUT_AF, CW_NUT_H + 1.0, CW_BOSS_Z0 - 1.0).translate((cx, cy, 0.0))

# 外径兜底: 任何加料都不许超出 Φ170 (凸台/bolster 半径可能越界)
body = body ^ cyl(H + 2.0, R_OUT, -1.0)
V_RAW = body.volume()
if CW_ENABLE:
    _cwv = 0.0
    for a in CW_ANG:
        cx, cy = _cw_xy(a)
        _cwv += (body ^ cyl(H - CW_BOSS_Z0, CW_BOSS_D / 2, CW_BOSS_Z0, 64)
                 .translate((cx, cy, 0.0))).volume()
    V_CW_BEFORE = _cwv

# ===================== 2) 让位 (障碍件膨胀后布尔减) =====================
# 零件系 = 屏局部系。各障碍件的装配变换见 assembly_v3.py, 这里折算回零件系:
#   portal_tee : 装配 rot(V3_SCR_ROT) → 零件系 = 原件 (B 件再转 180°)
#   wifi 组    : 装配 rot(135) → 零件系 = rot(135+45) = rot(180)
obst = {}
te = read_stl(P31 / "models/bottom_portal_v3_1/portal_tee_v3_1.stl")
obst["portal_tee_A"] = te.copy()
obst["portal_tee_B"] = rot_z(te.copy(), 180.0)

ws = read_stl(MODELS / "usb_wifi/wifi_shell.stl")
ws = ws[..., [2, 1, 0]] * np.array([1.0, 1.0, -1.0])       # rotY(+90) 倒扣
ws[..., 0] += 43.0 - 46.4 / 2                              # XC_WIFI − WS_W/2
ws[..., 1] += -13.0                                        # YC_WIFI
ws[..., 2] += 18.1                                         # WS_H (零件系 Z 已相对承载面)
obst["wifi_shell"] = rot_z(ws, 180.0)
obst["usb_wifi_module"] = rot_z(read_stl(MODELS / "usb_wifi/usb_wifi_module_flat.stl"), 180.0)
obst["pi2hub75e"] = rot_z(read_stl(MODELS / "pi2hub75e/pi2hub75e.stl")
                          + np.array([0.0, 0.0, 5.0]), 225.0 + 45.0) \
    + np.array([-10.0 * math.cos(math.radians(135.0)),
                -10.0 * math.sin(math.radians(135.0)), 0.0])
# v3.1: 屏偏心 +SCR_ECC (让位按偏心位算; 缝已同时覆盖居中位)
obst["dual_screen"] = read_stl(MODELS / "screen_150x169_t13/screen_150x169_t13.stl") \
    + np.array([SCR_ECC, 0.0, 50.0])

# --- 紧固件头 (2026-07-27 用户提醒: "螺丝帽直径是 7.5mm, 这些干涉有检查吗") ---
# 装配孪生里只有塑料件, 螺丝一概没建模 —— 罩内壁 R82 附近有几处螺丝头是踩线的,
# 必须按 Φ7.5 头实体一起让位。头高按盘头 2.5 计。
HEAD_D, HEAD_H = 7.5, 2.5


def _rot_pt(x, y, deg):
    r = math.radians(deg)
    return (x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r))


HEADS = []
# ① wifi_shell 沿 4× M3×8: 头坐沿顶面 (沿 asm 42.2..45.2 → 零件系 Z3)。
#    孔位是装配系坐标 (rim_ring build_stl 的 _WIFI_ASM), 折到零件系 = rot(+45)。
for (ax, ay) in [(-42.99, 0.14), (18.24, 61.38), (-60.67, 17.82), (0.57, 79.05)]:
    HEADS.append((_rot_pt(ax, ay, -V3_SCR_ROT), 3.0, "wifi 沿 M3×8"))
# ② portal_tee 脚 4× M3×20: 头坐 T 底条顶面 (asm 47.2 → 零件系 Z5)。
#    孔位在 T 件系 = 罩零件系 (T 件与罩同随 V3_SCR_ROT), B 件转 180°。
for sgn in (1.0, -1.0):
    for hx in (29.658, -29.658):
        HEADS.append(((sgn * hx, sgn * 71.601), 5.0, "T 脚 M3×20"))
# ③ 屏底 2× M3×12: 头沉在 T 顶托底面 Φ7.5 让位窝里 (零件系 Z41..43.5)
for hy in (64.0, -64.0):
    HEADS.append(((0.0, hy), 41.0, "屏底 M3×12"))

print("=" * 76)
print("紧固件头 (Φ7.5) 对罩内壁 R82 的关系:")
head_man = None
for (hx, hy), hz, tag in HEADS:
    r_out = math.hypot(hx, hy) + HEAD_D / 2
    flag = "★ 压到内壁" if r_out > R_IN else ("· 贴边" if r_out > R_IN - 2 else "✓")
    print(f"  {tag:14s} 孔 r{math.hypot(hx, hy):6.2f} → 头外沿 r{r_out:6.2f}  Z{hz:5.1f}  {flag}")
    h = cyl(HEAD_H, HEAD_D / 2, hz, 48).translate((hx, hy, 0.0))
    head_man = h if head_man is None else head_man + h
_hm = head_man.to_mesh()
obst["fastener_heads_Φ7.5"] = (np.asarray(_hm.vert_properties)[:, :3])[np.asarray(_hm.tri_verts)]

print("=" * 76)
print("让位 (障碍件膨胀 %.1f 后从罩体减去):" % RELIEF_CLR)
relief_log = []
for name, tris in obst.items():
    man = to_manifold(tris)
    cut_solid = sweep_down(dilate(man, RELIEF_CLR))
    cut = cut_solid ^ body                      # 只关心真正咬到罩体的部分
    v = cut.volume()
    if v < 1e-6:
        print(f"  {name:18s} 无干涉 ✓")
        continue
    vt = np.asarray(cut.to_mesh().vert_properties)[:, :3]
    r = np.hypot(vt[:, 0], vt[:, 1])
    through = r.max() > R_OUT - 0.05
    body -= cut_solid
    kind = "★ 穿壁开口" if through else "内壁让位窝"
    relief_log.append((name, v, kind))
    print(f"  {name:18s} {kind}  切掉 {v:8.1f} mm³   "
          f"r {r.min():6.2f}..{r.max():6.2f}  Z {vt[:,2].min():6.2f}..{vt[:,2].max():6.2f}")

# --- 配重座完整性校核: 让位布尔不许啃到凸台 (啃了说明角向选错) ---
if CW_ENABLE:
    _after = 0.0
    for a in CW_ANG:
        cx, cy = _cw_xy(a)
        _after += (body ^ cyl(H - CW_BOSS_Z0, CW_BOSS_D / 2, CW_BOSS_Z0, 64)
                   .translate((cx, cy, 0.0))).volume()
    _loss = V_CW_BEFORE - _after
    print("=" * 76)
    print(f"配重座 @{CW_ANG[0]:g}°/{CW_ANG[1]:g}° r{CW_R:g}: 让位前后凸台体积 "
          f"{V_CW_BEFORE:.1f} → {_after:.1f} mm³, 损失 {_loss:.2f}")
    assert _loss < 1.0, f"配重座被障碍件啃掉 {_loss:.2f} mm³ —— 换角向"
    print("  ✓ 未被任何障碍件啃到")

# ===================== 3) 分半 + 导出 =====================
half_space_A = box(-R_OUT - 5, R_OUT + 5, SEAM_GAP, R_OUT + 5, -1.0, H + 1.0)
half_space_B = box(-R_OUT - 5, R_OUT + 5, -R_OUT - 5, -SEAM_GAP, -1.0, H + 1.0)
halves = {"shroud_half_A_v3_1": body ^ half_space_A,     # +Y 半 (含 wifi 壳让位窝)
          "shroud_half_B_v3_1": body ^ half_space_B}     # −Y 半 (含线缆出口)


def export(part, name, note):
    mesh = part.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    out = HERE / f"{name}.stl"
    with out.open("wb") as f:
        f.write(f"POV3D {name}".encode().ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
            n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
            if L > 0: n = n / L
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    assert 84 + len(tris) * 50 == out.stat().st_size
    nb = len(part.decompose())
    r = np.hypot(verts[:, 0], verts[:, 1])
    print(f"\n{name}  ({note})")
    print(f"  wrote {out.name}  {len(tris)} tris, 连通体 {nb}"
          f"{'  ★★ 不是单体!' if nb != 1 else ' ✓'}")
    print(f"  体积 {part.volume()/1000:6.1f} cm³  (~{part.volume()*1.24/1000:.0f} g PLA)")
    print(f"  包络 X {verts[:,0].min():7.2f}..{verts[:,0].max():7.2f}  "
          f"Y {verts[:,1].min():7.2f}..{verts[:,1].max():7.2f}  "
          f"Z {verts[:,2].min():6.2f}..{verts[:,2].max():6.2f}   r_max {r.max():6.2f}")
    return part.volume()


print("\n" + "=" * 76)
tot = 0.0
tot += export(halves["shroud_half_A_v3_1"], "shroud_half_A_v3_1",
              "+Y 半, 2 立柱 @ 零件系 22.5°/157.5° (装配 337.5°/112.5°)")
tot += export(halves["shroud_half_B_v3_1"], "shroud_half_B_v3_1",
              "−Y 半, 2 立柱 @ 零件系 202.5°/337.5° (装配 157.5°/292.5°)")

print("\n" + "=" * 76)
print(f"罩体合计 {tot/1000:.1f} cm³ ≈ {tot*1.24/1000:.0f} g PLA "
      f"(未让位前 {V_RAW/1000:.1f} cm³)")
print(f"筒 Φ{OD:g}/Φ{ID:g} 壁 {WALL:g}, 高 {H:g} (装配 {DISC_TOP:g}..{DISC_TOP+H:g} = 承载面→屏底)")
print(f"顶板 {PLATE_T:g} 厚 @ Z{PLATE_Z0:g}..{H:g}; 屏缝 ±{SCR_HW:g} (|Y|≤{TEE_Y0:g}) "
      f"/ ±{TEE_HW:g} ({TEE_Y0:g}..{SLOT_Y1:g}), |Y|>{SLOT_Y1:g} 封口")
print(f"固定: 4× M3×12 @ r{COL_R:g}, 坐 Φ{WELL_D:g} 沉井底 {FLOOR_T:g} 厚台肩 "
      f"(井深 {H-FLOOR_T:g}, 头 Φ7.5 沉在井里, 长螺丝刀顺井拧); "
      f"借 rim_ring 空闲外圈环孔 (装配 112.5/157.5/292.5/337.5°), rim_ring 不改")
print("加强: 4 立柱兼竖筋 / 接缝 bolster ×2 (壁局部 9 厚) / 屏缝下翻边 ×2 (6 深)")
if CW_ENABLE:
    _hang = {135.0: 25.5, 225.0: 31.5}     # 螺母窝底往下的实测悬空 (见 build 记录)
    print(f"配重座 ×2 (每半 1 个) @ 零件系 {CW_ANG[0]:g}°/{CW_ANG[1]:g}° r{CW_R:g} "
          f"(装配 {CW_ANG[0]+V3_SCR_ROT:g}°/{CW_ANG[1]+V3_SCR_ROT:g}°): "
          f"顶板下挂 Φ{CW_BOSS_D:g} 凸台 Z{CW_BOSS_Z0:g}..{H:g} (12 厚, 外缘并内壁), "
          f"Φ{CW_HOLE_D:g} M6 过孔通, 自由端对边 {CW_NUT_AF:g} 六角螺母窝深 {CW_NUT_H:g}")
    print(f"  装法: **装半罩前从里面把 M6 螺母压进六角窝** → 之后 M6 螺丝一律从罩外顶面"
          f"往下拧, 罩装好也能加减配重 (Φ13 套筒通道已校核通畅)")
    print(f"  配重量: 螺丝最长 **M6×35** (135° 侧悬空 {_hang[135.0]:g}, 225° 侧 {_hang[225.0]:g}); "
          f"头下可垫 M6 螺母/垫圈加码 (咬合保持 ≥5) ⇒ 每座约 **10~28 g**")
    print(f"  两座对称跨 180° ⇒ 等质量合矢量指向零件系 180° (装配 {180+V3_SCR_ROT:g}°), "
          f"幅值 1.414·m·r ≈ {1.414*CW_R:.0f}·m g·mm; 不等质量可在 {CW_ANG[0]:g}..{CW_ANG[1]:g}° 间调向")
    print(f"  ⚠ 凸台自身 (2×{V_CW_BEFORE/2/1000:.2f} cm³ ≈ {V_CW_BEFORE*1.27/1000:.1f} g PLA) "
          f"也带 ~{1.414*(V_CW_BEFORE*1.27/1000/2)*CW_R:.0f} g·mm 的固有偏置, 同样指向 180°")
    print("  ⚠ 转速下必须防松: 尼龙锁紧螺母或螺纹胶, 垫圈不许松动")
print("打印: 绕 X 翻 180° 顶板贴床, 占地 170×85×50, 零支撑")
if relief_log:
    print("让位汇总:", "; ".join(f"{n} {k} {v:.0f}mm³" for n, v, k in relief_log))
