"""POV3D V1.2 定子线圈驱动小板 (XKT-801) 布局 + 合并: 散热片 (同电机控制板 40×20×6, 竖放) / 板 / MOS / 电解电容 + 底盘切口;
MOS 压块、电容卡件由独立生成器出, 本模块传参并入。

不 import build_v1_2 (避免循环): build_v1_2 在开底盘孔之前调用 make(sys.modules[__name__]), 结果挂在 B.CD。
需要 B 提供: cyl, cut, fuse, op, clean, DISC_T, DISC_D, M3_D, M3_CB_D, M3_CB_H, FL_Z0, CB_D, GRID, SH_M6, RING_M3, MOTOR_HOLES, OUT_SCREWS, FLANGE_SCREWS。

用户 11-12 夜 (最终):
- 「mos锁住就可以」: PCB 只靠 MOS 引脚挂着, 不罩不压; 无压盖 / 压边 / 支撑筋, 底盘顶面平; 背面电容低于 Z0 则底盘开让位坑 (+0.5)。
- 一字排布 (沿 Y): MOS 背板尖 (+Y) → MOS → 引脚 4 → 板 28 → 引线 → 电解电容 Φ10×20 平躺; 「从mos到电容长度是71mm」= MOS 尖 → 电容远端 71。
- 「mos偏心一点，电容是居中的」「mos这个卡件要做到以电路板中轴为对称」「散热片也是」: 散热片 / MOS 压块 / 电容卡件 都按板中心线 XPC 对称;
  MOS 中心线 XB = XPC + 2.95 (照片, 用户已确认)。
- MOS 按规格书 (TO-220 中值): E 10.1 / D 15.15 / A 4.45 / A1 1.3 / 引脚中心 Z2.7 ⇒ PCB Z2.3..3.1。
- 散热片竖放 (40 沿 Y, 20 沿 X), 从 MOS 下伸到板下 9 (再往 −Y 是背面电容坑)。
- MOS 压块: scripts/mos_clamp_v1_2.py make_mos_clamp(MC_PARAMS); 电容卡件: scripts/cap_clamp_v1_2.py make_cap_clamp(CC_PARAMS);
  返回 dict (clamp / disc_cuts = [其它…] + n×Φ3.2 + n×Φ7×2 / holes / nut_z0 / screw_len …); 文件不存在则跳过 (HAS_MC / HAS_CC = False)。
  参数快照写 out/coil_drv_params.json (生成器单跑用)。
- 两件各 2×M3 从底盘底面 Φ7×2 沉孔往上, 法兰螺母在件上; 可用高度 Z0..9.5 (定子盘底 B.FL_Z0), 件顶 / 螺母顶 / 螺尖 ≤ Z_LIMIT 9.0。
- 当前值 (XB 60 / P0 −26): XPC 57.05; MOS x55.0..65.05, y 塑封根 6 (MOS_Y_LEAD) → 背板尖 21.15 (MOS_Y_TIP); 板 y −26..2;
  散热片槽 x47.05..67.05 y−7..33; 电容 x52.05..62.05 y−49.85..−29.85, 轴 Z2.5, 槽深 2.5。
"""
import math, importlib, importlib.util
from pathlib import Path
from types import SimpleNamespace
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape
import coil_drv_pcb_v1_2 as PM

# ======================== 参数 (标 * 的为假设, 待用户实测) ========================
# --- 板 (XKT-801-49): 元件级模型见 coil_drv_pcb_v1_2.py ---
PCB_W, PCB_L, PCB_T = PM.PCB_W, PM.PCB_L, PM.PCB_T   # 16.5 × 28 × 0.8 (用户实测)
FRONT_H = PM.FRONT_MAX             # 正面最高件 1.7 (用户实测)
PCB_DX = -PM.MOS_DX                # ** 按照片估: 板中心相对 MOS 中心线 −2.95
COMP_CLR = 0.5                     # 背面电容坑 离元件 ≥0.5
# --- MOS TO-220 ---
# 用户 11-12 夜给的封装规格书 (TO-220, 取名义中值): A 4.45 / A1 1.3 / A2 2.45 / c 0.5 / E 10.1 / E1 8.35 (背面露铜宽) / D 15.15 /
#   D1 9.15 / H1 6.5 / ΦP 3.6 / Q 2.8 / b 0.8 / b1 1.45 / L1 3.05 / e 2.54。塑封体宽 = E (正视图), 塑封段长取 D − H1 = 8.65 (D1 含斜面)
MOS_W, MOS_L, MOS_T = 10.1, 15.15, 4.45   # E / D (含背板, 不含脚) / A
MOS_TAB_T = 1.3                    # A1 背板 (金属散热面) 厚
MOS_TAB_L = 6.5                    # H1 背板露出段长 (带 Φ3.6 孔那段)
MOS_HOLE_D, MOS_HOLE_Y = 3.6, 2.8  # ΦP / Q 孔心离背板尖端
MOS_LEAD_Z = 2.7                   # A2 2.45 + c/2 ⇒ 引脚中心线离背板底 2.7 ⇒ PCB 中面 = 此高度 (同平面直出)
LEAD_L = 4.0                       # 实物剪短后露出脚长 (MOS 本体 → PCB 边; 规格 L 13.2)
LEAD_W, LEAD_T, LEAD_P = 0.8, 0.5, 2.54   # b / c / e
LEAD_W1, LEAD_L1 = 1.45, 3.05      # b1 × L1 根部加宽段
# --- 电解电容 ---
CAP_D, CAP_L = 10.0, 20.0          # Φ10×20 (用户)
CHAIN_L = 71.0                     # 用户 11-12 夜「从mos到电容长度是71mm」: 理解为 MOS 尖 → 电容远端整串 (MOS 16 + 脚 4 + 板 28 + 引线 + 电容 20)
                                   #   ⇒ 用户确认: MOS → 板 → 电容 串成一线, 电容轴 = 板中心线 (x55.05), 平躺在底盘上, 弯脚; 引线 71 − 68 = 3
CAP_SINK_MIN0 = 0.0                # (原 CAP_SINK = 2.35 常数, 现于 make() 里按 FL_Z0 算) 底盘槽深 = 最小可行 (用户 11-12 夜): 电容顶 + 卡件间隙 0.15 + 顶厚 1.2 ≤ 9.0 ⇒ 10 − g + 1.35 ≤ 9 ⇒ g ≥ 2.35;
                                   #   以 cap_clamp_v1_2 算出的 groove 为准 (传 CAP_ZC=None, CAP_GROOVE=0); 底盘剩 3.65
CAP_TROUGH_CLR = 0.2               # 弧形槽半径余量 (槽圆心比电容轴低 0.2 ⇒ 电容底贴槽底)
# --- 散热片 (同 B.sink_shape: 40×20×6, 底座 2 + 7 鳍朝下; 本处转 90°, 40 沿 Y) ---
SINK_L, SINK_W, SINK_H, SINK_BASE, FIN_T, N_FIN = 40.0, 20.0, 6.0, 2.0, 1.4, 7
SINK_Y0_OFF = -13.0                # 散热片 (竖放: 20 沿 X, 40 沿 Y, x 按板中心居中) −Y 端相对 MOS 本体根: y −7..33 (伸到板下 9, 离背面电容坑 1.1; +Y 超出 MOS 尖 11.85)
# --- 位置 (用户 11-12 夜: 散热片 / MOS 压块 / 电容卡件 共用板中心线 x = XPC; MOS 偏 +2.95) ---
XB = 60.0                          # MOS 中心线 x ⇒ 板中心 XPC = 57.05。原 58 (XPC 55.05) 时, 按板中线对称的 MOS 压块 −X 端
                                   #   (孔 XPC−15 外再 4.1 井 + 1 壁) 到 x35.45, 碰线圈环方座 ±35.5 ⇒ 整串 +X 2 (压块端离线圈环 1.45)
P0 = -26.0                         # 板功率端 (−Y 短边) y。原 −28 时电容远端 y−51.85, 碰下罩四角三角块 (|x|,|y| > 51, Z0..5) ⇒ 整串 +Y 2
# --- MOS 压块 mos_clamp_v1_2: 独立生成器 scripts/mos_clamp_v1_2.py (make_mos_clamp(p), 另一 agent 写), 本模块只给参数 + 并入 ---
SCREW_L = 12.0                     # 本模块的预览螺丝 (压块 / 卡件都用 M3×12, 以生成器返回为准)
# --- 紧固件 (同 fasteners_v1_2: 超薄头 Φ7×1.5, 法兰螺母 Φ7.6/对边5.9/厚3.7) ---
HEAD_D, HEAD_H = 7.0, 1.5
NUT_FL_D, NUT_FL_H, NUT_AF, NUT_T = 7.6, 1.0, 5.9, 3.7
TOP_MARGIN = 0.5                   # 螺母顶 / 螺尖 须 ≤ 定子盘底 − 0.5
CC_TOP_MARGIN_MIN = 0.15           # 电容卡件顶离定子盘底最少 (用户 11-12 夜: 法兰盘底降到 Z8.5 后槽深挖到 3 仍顶 8.35 > 8.0 ⇒ 卡件单独放宽, 只留 0.15)
CAP_GROOVE_MAX = 3.0               # 底盘 6 剩 ≥3
# 要从底盘 M6 网格去掉的孔: (62.5,±12.5) / (62.5,37.5) 碰竖放散热片槽 (x47.05..67.05 y−7..33; M6 沉孔 Φ13); (62.5,−37.5) 碰电容弧形槽 (M6 通孔 Φ6.4)
GRID_REMOVE = [(62.5, 12.5), (62.5, -12.5), (62.5, 37.5), (62.5, -37.5)]
# 待实测 (README 列)
TBD = ['MOS_LEAD_Z 脚高 2.4 (定 PCB 高度)', 'MOS_TAB_L 背板露出段 6.3', 'MOS_HOLE_D/Y 背板孔 Φ3.6 / 离尖 2.8', 'LEAD_L 露出脚长 4',
       'CHAIN_L 71 的理解 (MOS 尖 → 电容远端, 电容与板串成一线)', 'coil_drv_pcb_v1_2.COMP 元件表 / MOS_DX (按照片估 ±0.5)']


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)), gp_Pnt(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()


def ycyl(x, z, d, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), d / 2, y1 - y0).Shape()


def comp(shapes):
    bb = BRep_Builder(); c = TopoDS_Compound(); bb.MakeCompound(c)
    for s in shapes: bb.Add(c, s)
    return c


def hexprism(x, y, af, z0, z1):
    rc = af / math.sqrt(3); pg = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.radians(30 + 60 * k); pg.Add(gp_Pnt(x + rc * math.cos(a), y + rc * math.sin(a), z0))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()


def make(B):
    cyl, cut, fuse, op, clean = B.cyl, B.cut, B.fuse, B.op, B.clean
    # ---------------- 推导 ----------------
    STATOR_Z0 = B.FL_Z0                       # 9.5 (用户 11-12 夜改: 法兰盘加厚 1 ⇒ 8.5)
    # 电容槽深 = 最小可行 (卡件顶 = 电容顶 + 0.15 + 1.2 ≤ 定子盘底 − 0.5), 上限 3; 到上限仍超 ⇒ 卡件 Z_LIMIT 放宽 (≥ 定子盘底 − 0.15)
    CAP_SINK = min(CAP_GROOVE_MAX, max(CAP_SINK_MIN0, round(CAP_D + 0.15 + 1.2 - (STATOR_Z0 - TOP_MARGIN), 6)))
    CC_Z_LIMIT = max(STATOR_Z0 - TOP_MARGIN, round(CAP_D - CAP_SINK + 0.15 + 1.2, 6))
    assert CC_Z_LIMIT <= STATOR_Z0 - CC_TOP_MARGIN_MIN + 1e-9, ('电容卡件顶离定子盘底 <0.15', CC_Z_LIMIT, STATOR_Z0)
    Y_PCB1 = P0 + PCB_L                       # 板 MOS 端 0
    Y_MOS0 = Y_PCB1 + LEAD_L                  # MOS 本体根 4
    Y_TIP = Y_MOS0 + MOS_L                    # MOS 尖 (背板端) 20
    SINK_LX, SINK_LY = SINK_W, SINK_L         # 转 90°: X 20, Y 40
    SINK_Y0 = Y_MOS0 + SINK_Y0_OFF; SINK_Y1 = SINK_Y0 + SINK_LY
    XPC = XB + PCB_DX                         # 板中心 x 57.05
    SINK_X0, SINK_X1 = XPC - SINK_LX / 2, XPC + SINK_LX / 2     # 用户: 散热片也按板中心线居中
    assert SINK_X0 <= XB - MOS_W / 2 and SINK_X1 >= XB + MOS_W / 2, 'MOS 背板没完整落在散热片上'
    PCB_Z0 = round(max(MOS_LEAD_Z - PCB_T / 2, PM.BACK_MAX + COMP_CLR), 6)   # 用户 11-13: 底盘不挖背面电容坑 ⇒ 板抬到背面电容 (2.5) 底离底盘 0.5 = Z3.0 (原 2.3 平 MOS 引脚, 现引脚往上弯 0.7)
    PCB_Z1 = PCB_Z0 + PCB_T                   # 2.8
    FRONT_Z = PCB_Z1 + FRONT_H                # 4.8
    BACK_Z0 = round(PCB_Z0 - PM.BACK_MAX, 6)  # 背面最低 (电容底) −0.5
    MOS_Y_LEAD, MOS_Y_TIP = Y_MOS0, Y_TIP     # MOS 塑封根 (引脚端, −Y) / 背板尖 (+Y); 背板 (散热面) 朝下 Z0, 背板端朝 +Y
    CAP_X = XPC                               # 用户 11-12 夜: 电容轴对准板中心线 (MOS 偏 +2.95)
    CAP_ZA = -CAP_SINK + CAP_D / 2            # 电容轴心 Z 2.5
    CAP_LEAD = CHAIN_L - (MOS_L + LEAD_L + PCB_L + CAP_L)   # 3
    CAP_Y1 = P0 - CAP_LEAD; CAP_Y0 = CAP_Y1 - CAP_L         # 电容 y −51..−31 (引线端 +Y)
    CAP_CX, CAP_ZC, CAP_GROOVE = CAP_X, CAP_ZA, CAP_SINK   # 给 cap_clamp_v1_2 的接口名
    assert CAP_ZA + CAP_D / 2 + 0.15 + 1.2 <= CC_Z_LIMIT + 1e-9, '电容顶 + 间隙 0.15 + 卡件顶厚 1.2 > 卡件 Z_LIMIT'
    assert CAP_SINK <= 3.0 + 1e-9 and B.DISC_T - CAP_SINK >= 3.0 - 1e-9, '电容槽太深'
    BEAR_Z = -B.DISC_T + B.M3_CB_H            # 螺丝头支承面 Z−4
    SCREW_TIP = BEAR_Z + SCREW_L              # 8
    Z_LIMIT = STATOR_Z0 - TOP_MARGIN          # 9.0
    assert SINK_Y0 <= Y_MOS0 and SINK_Y1 >= Y_TIP, '散热片没盖住 MOS'

    # ---------------- 零件 ----------------
    pcb = PM.make_pcb(XPC, Y_PCB1, PCB_Z0)   # 元件级 (板 + 两面元件 / 焊点盒)
    # 背面让位坑: 背面件底低于 Z0 + 0.5 的, 平面 +0.5, 坑底 = 件底 − 0.5; 相邻坑间壁 <1 合并
    pits = []
    for n, side, _, x0, x1, y0, y1, h, k in PM.COMP:
        if side == 'B' and PCB_Z0 - h < COMP_CLR:
            pits.append([XPC + x0 - COMP_CLR, Y_PCB1 + y0 - COMP_CLR, XPC + x1 + COMP_CLR, Y_PCB1 + y1 + COMP_CLR, PCB_Z0 - h - COMP_CLR])
    merged = True
    while merged:
        merged = False
        for i in range(len(pits)):
            for j in range(i + 1, len(pits)):
                a, b = pits[i], pits[j]
                if a[0] < b[2] + 1 and b[0] < a[2] + 1 and a[1] < b[3] + 1 and b[1] < a[3] + 1:
                    pits[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), min(a[4], b[4])]; del pits[j]; merged = True; break
            if merged: break
    BCAP_PITS = [tuple(round(v, 3) for v in p) for p in pits]
    mos = fuse(box(XB - MOS_W / 2, Y_MOS0, 0, XB + MOS_W / 2, Y_TIP - MOS_TAB_L, MOS_T),
               box(XB - MOS_W / 2, Y_TIP - MOS_TAB_L, 0, XB + MOS_W / 2, Y_TIP, MOS_TAB_T))
    mos = cut(mos, cyl(XB, Y_TIP - MOS_HOLE_Y, MOS_HOLE_D, -1, 2))
    mos = fuse(mos, *[box(XB + k * LEAD_P - LEAD_W / 2, Y_PCB1, MOS_LEAD_Z - LEAD_T / 2,
                          XB + k * LEAD_P + LEAD_W / 2, Y_MOS0, MOS_LEAD_Z + LEAD_T / 2) for k in (-1, 0, 1)],
               *[box(XB + k * LEAD_P - LEAD_W1 / 2, max(Y_PCB1, Y_MOS0 - LEAD_L1), MOS_LEAD_Z - LEAD_T / 2,
                     XB + k * LEAD_P + LEAD_W1 / 2, Y_MOS0, MOS_LEAD_Z + LEAD_T / 2) for k in (-1, 0, 1)])
    cap = ycyl(CAP_X, CAP_ZA, CAP_D, CAP_Y0, CAP_Y1)
    sink2 = box(SINK_X0, SINK_Y0, -SINK_BASE, SINK_X1, SINK_Y1, 0)    # 鳍沿 Y (转 90°)
    for i in range(N_FIN):
        x0 = SINK_X0 + i * (SINK_LX - FIN_T) / (N_FIN - 1)
        sink2 = fuse(sink2, box(x0, SINK_Y0, -SINK_H, x0 + FIN_T, SINK_Y1, -SINK_BASE))

    # 紧固件 (预览 / 校核用; fasteners_v1_2 另放)
    def screw_up(x, y): return fuse(cyl(x, y, HEAD_D, BEAR_Z - HEAD_H, BEAR_Z), cyl(x, y, 3.0, BEAR_Z, SCREW_TIP))
    def flange_nut(x, y, z0):
        return cut(fuse(cyl(x, y, NUT_FL_D, z0, z0 + NUT_FL_H), hexprism(x, y, NUT_AF, z0 + NUT_FL_H, z0 + NUT_T)), cyl(x, y, 3.0, z0 - 1, z0 + NUT_T + 1))
    screws, nuts, HOLES = [], [], []

    # 底盘切口: 散热片通槽 (零间隙) + 2×M3 (Φ3.2 通 + 底面 Φ7×2) + 电容弧形槽 + 背面电容坑
    _rt = CAP_D / 2 + CAP_TROUGH_CLR
    disc_cut_list = [box(SINK_X0, SINK_Y0, -B.DISC_T - 1, SINK_X1, SINK_Y1, 1)]
    disc_cut_list.append(op(BRepAlgoAPI_Common, ycyl(CAP_X, -CAP_SINK + _rt, 2 * _rt, CAP_Y0 - 0.5, CAP_Y1 + 0.5), box(0, -100, -10, 200, 100, 1)))
    CUT_LBL = ['散热片槽', '电容槽']
    for i, (x0, y0, x1, y1, zb) in enumerate(BCAP_PITS):      # 背面贴片电容让位坑
        disc_cut_list.append(box(x0, y0, zb, x1, y1, 1)); CUT_LBL.append(f'背面电容坑{i}')
    _hw = math.sqrt(_rt ** 2 - (_rt - CAP_SINK) ** 2)            # 顶面开口半宽
    CAP_TROUGH = (round(CAP_X - _hw, 2), round(CAP_X + _hw, 2), CAP_Y0 - 0.5, CAP_Y1 + 0.5, CAP_SINK)  # 顶面开口 x0,x1,y0,y1,深

    ns = SimpleNamespace(**{k: v for k, v in globals().items() if k.isupper()})
    ns.__dict__.update({k: v for k, v in locals().items() if k[0].isupper() or k in (
        'pcb', 'mos', 'cap', 'sink2', 'screws', 'nuts', 'disc_cut_list')})
    ns.B = B; ns.box = box; ns.ycyl = ycyl; ns.screw_up = screw_up; ns.flange_nut = flange_nut
    # ---- 两件独立生成器 (另两个 agent 写): mos_clamp_v1_2.make_mos_clamp / cap_clamp_v1_2.make_cap_clamp; 有则并入, 无则跳过 ----
    gr = [g for g in B.GRID if g not in GRID_REMOVE and math.hypot(*g) + B.CB_D / 2 <= B.DISC_D / 2
          and math.hypot(*g) >= B.COLLAR_D / 2 + B.M6_D / 2 + 1.0]          # 同 build 网格跳孔: 线圈环下的不开
    KEEPOUT = ([(x, y, B.CB_D / 2) for x, y in gr] + [(x, y, B.M3_CB_D / 2) for x, y in list(B.SH_M6) + list(B.RING_M3) + list(B.MOTOR_HOLES)]
               + [(x, y, 2.1) for x, y in list(B.OUT_SCREWS) + list(B.FLANGE_SCREWS)])          # 底盘已有孔/沉孔 (x, y, r)
    COMMON = dict(XPC=XPC, DISC_T=B.DISC_T, Z_LIMIT=Z_LIMIT, STATOR_Z0=STATOR_Z0, M3_D=B.M3_D, M3_CB_D=B.M3_CB_D, M3_CB_H=B.M3_CB_H,
                  HEAD_D=HEAD_D, HEAD_H=HEAD_H, NUT_FL_D=NUT_FL_D, NUT_FL_H=NUT_FL_H, NUT_AF=NUT_AF, NUT_T=NUT_T, KEEPOUT=KEEPOUT)
    MC_PARAMS = dict(COMMON, MOS_DX=round(XB - XPC, 6), MOS_X=XB, MOS_Y_LEAD=MOS_Y_LEAD, MOS_Y_TIP=MOS_Y_TIP, MOS_DIR=1, MOS_TIP_DIR='+Y', SINK_W=SINK_LX, SINK_Y0=SINK_Y0, SINK_Y1=SINK_Y1, MOS_A=MOS_T, MOS_A1=MOS_TAB_T, MOS_E=MOS_W, MOS_D=MOS_L, MOS_H1=MOS_TAB_L,
                     MOS_P=MOS_HOLE_D, MOS_Q=MOS_HOLE_Y, LEAD_Z=MOS_LEAD_Z, LEAD_L=LEAD_L,
                     MOS_W=MOS_W, MOS_L=MOS_L, MOS_T=MOS_T, MOS_TAB_T=MOS_TAB_T, MOS_TAB_L=MOS_TAB_L, MOS_HOLE_D=MOS_HOLE_D, MOS_HOLE_Y=MOS_HOLE_Y,
                     MOS_LEAD_Z=MOS_LEAD_Z, LEAD_W=LEAD_W, LEAD_T=LEAD_T, LEAD_P=LEAD_P, LEAD_W1=LEAD_W1, LEAD_L1=LEAD_L1,
                     SINK_RECT=(SINK_X0, SINK_Y0, SINK_X1, SINK_Y1), PCB_Y_MOS_END=Y_PCB1, PCB_RECT=(XPC - PCB_W / 2, P0, XPC + PCB_W / 2, Y_PCB1),
                     PCB_Z=(PCB_Z0, PCB_Z1), RING_HALF=getattr(B, 'COLLAR_FLAT', 35.5))
    CC_PARAMS = dict(COMMON, Z_LIMIT=CC_Z_LIMIT, CAP_CX=CAP_CX, CAP_Y0=CAP_Y0, CAP_Y1=CAP_Y1, CAP_ZC=None, CAP_GROOVE=0.0, CAP_D=CAP_D, CAP_L=CAP_L,
                     TROUGH_CLR=CAP_TROUGH_CLR)
    ns.KEEPOUT, ns.MC_PARAMS, ns.CC_PARAMS = KEEPOUT, MC_PARAMS, CC_PARAMS
    try:                                                  # 给生成器单跑用的参数快照
        import json
        _o = Path(__file__).resolve().parent.parent / 'out'; _o.mkdir(exist_ok=True)
        json.dump(dict(note='coil_drv_geom.make 写出 (装配系 mm; 底盘顶 Z0, 底 −DISC_T; MOS 背板朝下贴散热片顶 Z0, 背板尖朝 +Y, 引脚朝 −Y 接板)',
                       mos_clamp=MC_PARAMS, cap_clamp=CC_PARAMS), open(_o / 'coil_drv_params.json', 'w'), indent=1, ensure_ascii=False)
    except Exception as e:
        print('coil_drv_params.json 没写成:', e)

    MERGE_ERR = {}
    def merge(modname, fn, params, tag):
        if importlib.util.find_spec(modname) is None:
            return None
        try:
            mod = importlib.import_module(modname)
            res = getattr(mod, fn)(params)
        except Exception as e:                            # 生成器还在改 / 参数不合: 跳过, 不拖垮整机
            import traceback; traceback.print_exc()
            print(f'[coil_drv_geom] {modname}.{fn} 失败, 跳过: {e!r}'); MERGE_ERR[modname] = repr(e)
            return None
        get = (lambda k, d=None: res.get(k, d)) if isinstance(res, dict) else (lambda k, d=None: getattr(res, k, d))
        shp = res if isinstance(res, TopoDS_Shape) else get('clamp')
        holes = [tuple(h) for h in (get('holes') or [])]
        nz0 = get('nut_z0', get('ear_top'))
        cuts = list(get('disc_cuts') or [])
        n = len(holes); k = len(cuts) - 2 * n                # 约定: [其它切口 …] + n×Φ3.2 通 + n×Φ7 沉孔
        lbl = (list(get('disc_cut_labels') or [])[:k] + [f'{tag}切口{i}' for i in range(k)])[:k] if k > 0 else []
        lbl += [f'{tag}螺丝{i}Φ3.2' for i in range(n)] + [f'{tag}螺丝{i}沉孔Φ7' for i in range(n)]
        return dict(res=res, clamp=shp, holes=holes, nut_z0=nz0, cuts=cuts, lbl=lbl, screw_len=get('screw_len', SCREW_L))

    for key, modname, fn, params, tag in (('MC', 'mos_clamp_v1_2', 'make_mos_clamp', MC_PARAMS, '压块'),
                                          ('CC', 'cap_clamp_v1_2', 'make_cap_clamp', CC_PARAMS, '卡件')):
        m = merge(modname, fn, params, tag)
        setattr(ns, f'HAS_{key}', m is not None)
        setattr(ns, f'{key}_RES', m and m['res'])
        setattr(ns, f'{key}_HOLES', m['holes'] if m else [])
        setattr(ns, f'{key}_NUT_Z0', m and m['nut_z0'])
        setattr(ns, f'{key}_SCREW_L', m and m['screw_len'])
        setattr(ns, 'clamp' if key == 'MC' else 'cap_clamp', m and m['clamp'])
        if not m:
            print(f'[coil_drv_geom] {modname}.py 不存在, 跳过')
            continue
        if key == 'CC' and isinstance(m['res'], dict) and m['res'].get('groove') is not None:   # 槽深 / 电容轴以生成器算出的最小可行值为准
            r_ = m['res']
            if abs(r_['groove'] - CAP_GROOVE) > 1e-9 or abs(r_['cap_zc'] - CAP_ZC) > 1e-9:
                print(f'[coil_drv_geom] 电容槽深 {CAP_GROOVE} → {r_["groove"]} (cap_clamp 算), 轴 Z{CAP_ZC} → {r_["cap_zc"]}')
            for k_, v_ in (('CAP_GROOVE', r_['groove']), ('CAP_SINK', r_['groove']), ('CAP_ZC', r_['cap_zc']), ('CAP_ZA', r_['cap_zc'])):
                setattr(ns, k_, v_)
            ns.cap = cap = r_.get('cap') or ycyl(CAP_CX, r_['cap_zc'], CAP_D, CAP_Y0, CAP_Y1)
            _tr = r_.get('trough') or {}
            ns.CAP_TROUGH = (round(CAP_CX - _tr.get('top_halfwidth', 0), 2), round(CAP_CX + _tr.get('top_halfwidth', 0), 2), *(_tr.get('y') or (CAP_Y0 - 0.5, CAP_Y1 + 0.5)), r_['groove'])
        if key == 'CC' and m['lbl'] and not m['lbl'][0].startswith('卡件螺丝'):   # 生成器自带弧形槽 ⇒ 用它的, 去掉本模块的
            i_ = CUT_LBL.index('电容槽'); del disc_cut_list[i_]; del CUT_LBL[i_]
        disc_cut_list += m['cuts']; CUT_LBL += m['lbl']
        r_ = m['res'] if isinstance(m['res'], dict) else {}
        if r_.get('screws') and r_.get('nuts'):            # 生成器自带 (螺母倒放: 六角朝下坐井底, 法兰朝上)
            screws += list(r_['screws']); nuts += list(r_['nuts'])
        elif m['nut_z0'] is not None:
            screws += [fuse(cyl(x, y, HEAD_D, BEAR_Z - HEAD_H, BEAR_Z), cyl(x, y, 3.0, BEAR_Z, BEAR_Z + m['screw_len'])) for x, y in m['holes']]
            nuts += [flange_nut(x, y, m['nut_z0']) for x, y in m['holes']]
    ns.MERGE_ERR = MERGE_ERR
    ns.HOLES = ns.MC_HOLES; ns.CC_EAR_TOP = ns.CC_NUT_Z0; ns.EAR_TOP = ns.MC_NUT_Z0
    ns.ALL_HOLES = ns.MC_HOLES + ns.CC_HOLES
    ns.disc_cuts = comp(disc_cut_list)
    ns.PARTS = dict(pcb=pcb, mos=mos, cap=cap, sink2=sink2, **({'clamp': ns.clamp} if ns.HAS_MC else {}), **({'cap_clamp': ns.cap_clamp} if ns.HAS_CC else {}),
                    **{f'screw{i}': s for i, s in enumerate(screws)}, **{f'nut{i}': n for i, n in enumerate(nuts)})
    return ns
